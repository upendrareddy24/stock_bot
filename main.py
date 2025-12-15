# -*- coding: utf-8 -*-
import schedule
import datetime
import time
import threading
import random
import os
from bot import StockBot
from data_manager import DataManager
from analyzer import Analyzer
from index_analyzer import IndexAnalyzer

# Import configuration
from config import TELEGRAM_TOKEN, CHAT_ID, validate_config

# Database for persistence
from database import Database
db = Database()

def is_seen(item_id, item_type="news"):
    """Check if item has been seen in DB"""
    return db.is_item_seen(item_id)

def save_seen(item_id, item_type="news"):
    """Save item to DB"""
    db.add_seen_item(item_id, item_type)



def is_us_ticker(symbol):
    """
    Check if ticker is a US-listed stock (Robinhood compatible).
    Filter out: Foreign stocks, OTC, ADRs with dots/dashes
    """
    if not symbol:
        return False
    # Skip tickers with dots (foreign), excessive length, or known non-US patterns
    if '.' in symbol or '-' in symbol or len(symbol) > 5:
        return False
    # Skip known foreign/OTC patterns
    if symbol.endswith('F') or symbol.startswith('0'):
        return False
    return True


def scan_institutional_accumulation(bot_instance):
    """
    🚨 HIGHEST PRIORITY ALERT 🚨
    Scans for INSTITUTIONAL ACCUMULATION (5x+ volume spikes).
    
    This is the EARLIEST and STRONGEST signal of a major move.
    When institutions accumulate, retail follows - we want to be FIRST.
    
    Criteria:
    - Current volume 5x+ average (institutional-level buying)
    - Above 20 SMA (uptrend)
    - US-listed ticker
    
    Sends IMMEDIATE alert - no waiting, no batching.
    """
    print("🔍 SCANNING FOR INSTITUTIONAL ACCUMULATION (5x+ Volume)...")
    
    dm = DataManager()
    analyzer = Analyzer()
    
    # Get comprehensive stock universe
    tickers = dm.get_comprehensive_stock_universe()
    
    # Scan top 200 for speed (institutions usually in liquid stocks)
    tickers = tickers[:200]
    
    alerts_sent = 0
    
    for ticker in tickers:
        try:
            # Skip non-US tickers
            if not is_us_ticker(ticker):
                continue
            
            df = dm.get_stock_history(ticker)
            if df.empty or len(df) < 21:
                continue
            
            # Calculate volume metrics
            current_volume = df['Volume'].iloc[-1]
            avg_volume_20 = df['Volume'].iloc[-21:-1].mean()
            
            if avg_volume_20 == 0:
                continue
            
            volume_ratio = current_volume / avg_volume_20
            
            # 🚨 INSTITUTIONAL ACCUMULATION DETECTED 🚨
            if volume_ratio >= 5.0:
                current_price = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2]
                price_change_pct = ((current_price - prev_close) / prev_close) * 100
                sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
                
                # Quality filter: Must be in uptrend (above 20 SMA)
                if current_price < sma_20:
                    continue
                
                # Get expert analysis for context
                expert_report = None
                try:
                    expert_report = analyzer.generate_full_report(df)
                except:
                    pass
                
                # Build URGENT alert message
                msg = "🚨🚨🚨 **INSTITUTIONAL ACCUMULATION DETECTED** 🚨🚨🚨\n\n"
                msg += f"**{ticker}** - MASSIVE VOLUME SPIKE!\n\n"
                msg += f"📊 **Volume**: {volume_ratio:.1f}x Average (INSTITUTIONAL LEVEL)\n"
                msg += f"💰 **Price**: ${current_price:.2f} ({price_change_pct:+.2f}%)\n"
                msg += f"📈 **Trend**: Above 20 SMA (${sma_20:.2f})\n\n"
                
                if expert_report:
                    msg += f"⭐ **Expert Score**: {expert_report['score']}/12 - {expert_report['rating']}\n"
                    msg += f"🎯 **Entry**: ${expert_report['entry']:.2f}\n"
                    msg += f"🛑 **Stop**: ${expert_report['stop']:.2f}\n"
                    msg += f"🎯 **Target**: ${expert_report['target']:.2f}\n"
                    msg += f"💎 **R/R**: 1:{expert_report['risk_reward']:.1f}\n\n"
                
                msg += "⚡ **ACTION**: This is EARLY institutional accumulation!\n"
                msg += "🔥 **URGENCY**: HIGH - Institutions are loading up NOW\n"
                msg += "⚠️ **Confirm**: Watch for continued volume + price follow-through\n"
                
                # Create unique ID to prevent dupes
                alert_id = f"institutional:{ticker}:{int(current_price)}:{int(volume_ratio)}"
                
                if not db.is_item_seen(alert_id):
                    db.add_seen_item(alert_id, "institutional")
                    
                    print(f"🚨 INSTITUTIONAL ALERT: {ticker} - {volume_ratio:.1f}x volume!")
                    
                    # SEND IMMEDIATELY - Don't wait!
                    if CHAT_ID != "YOUR_CHAT_ID":
                        bot_instance.send_alert_sync(CHAT_ID, msg)
                        alerts_sent += 1
                        
        except Exception as e:
            print(f"Error scanning {ticker} for institutional: {e}")
            continue
    
    if alerts_sent > 0:
        print(f"✅ Sent {alerts_sent} institutional accumulation alerts")
    else:
        print("✅ No institutional accumulation detected (5x+ volume)")


def check_news(bot_instance):
    """
    Checks for breaking news every 5 minutes.
    If news is found, immediately scans that stock for technicals.
    """
    print(f"[{datetime.datetime.now().strftime('%H:%M')}] Checking for Breaking News...")
    dm = DataManager()
    analyzer = Analyzer()
    
    news_items = dm.get_major_news()
    if not news_items:
        return

    # ========== STRICT QUALITY FILTER ==========
    # Only send alerts for MAJOR CATALYSTS that move stocks
    
    # HIGH-IMPACT POSITIVE Keywords (Must have at least one)
    major_catalysts = [
        # Earnings & Financials
        "Beat", "Beats Estimates", "Crushes Estimates", "Blows Past", 
        "Record Revenue", "Record Earnings", "Record Profit",
        
        # Analyst Actions
        "Upgrade", "Upgraded to Buy", "Raised Price Target", "Initiates Coverage",
        
        # Corporate Actions
        "Acquisition", "Acquires", "Merger", "Buyback", "Stock Buyback",
        "Partnership", "Strategic Partnership", "Major Contract", "Wins Contract",
        
        # Regulatory & Product
        "FDA Approval", "Approval", "Patent", "Breakthrough",
        
        # Institutional
        "Insider Buying", "Institutional Buying"
    ]
    
    # NEGATIVE Keywords (Auto-reject if present)
    negative_keywords = [
        "Downgrade", "Lowered", "Misses", "Miss Estimates", "Disappoints",
        "Lawsuit", "Investigation", "Probe", "Recall", "Warning",
        "Layoff", "Bankruptcy", "Debt", "Loss", "Decline"
    ]

    for item in news_items:
        # Item: {'symbol': 'AAPL', 'title': '...', 'date': '...'}
        title = item['title']
        symbol = item['symbol']
        news_date = item.get('date', '')
        
        # Filter 1: Only TODAY's news (strict - skip if date is missing/invalid)
        try:
            if not news_date:
                continue  # Skip if no date
            news_datetime = datetime.datetime.fromisoformat(news_date.replace('Z', '+00:00'))
            today = datetime.datetime.now(datetime.timezone.utc).date()
            if news_datetime.date() != today:
                continue  # Skip old news
        except Exception as e:
            print(f"Skipping news with invalid date: {news_date}")
            continue  # If date parsing fails, skip this news item
        
        # Filter 2: REJECT if contains negative keywords
        if any(neg_keyword.lower() in title.lower() for neg_keyword in negative_keywords):
            print(f"Skipping negative news for {symbol}: {title}")
            continue
        
        # Filter 3: REQUIRE at least one major catalyst keyword
        if not any(catalyst.lower() in title.lower() for catalyst in major_catalysts):
            continue  # Skip non-impactful news
        
        # Unique ID for the news item to prevent dupes
        news_id = f"{symbol}:{title}"
        
        if not is_seen(news_id, "news"):
            # CRITICAL: Validate ticker is US-listed (Robinhood compatible)
            # Skip foreign stocks, OTC, non-US exchanges
            if not is_us_ticker(symbol):
                print(f"Skipping non-US ticker: {symbol}")
                continue
                
            save_seen(news_id, "news")  # Persist to DB
            print(f"✅ MAJOR CATALYST for {symbol}: {title}")

            
            # 1. Analyze the stock immediately for technical patterns
            tech_alert = ""
            df = None  # Initialize df
            try:
                df = dm.get_stock_history(symbol)
                if not df.empty:
                    if analyzer.check_squeeze(df):
                        tech_alert += " • 🌭 **Squeeze Detected!**\n"
                    if analyzer.check_breakout(df):
                        tech_alert += " • 💥 **Breakout Detected!**\n"
                    if analyzer.check_cup_and_handle(df):
                        tech_alert += " • ☕ **Cup & Handle!**\n"
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")

            # 2. Only send alert if we have data AND quality technical setup
            if df is not None and not df.empty:
                # 3. Run EXPERT ANALYSIS with HIGHER threshold (5+ for quality)
                try:
                    expert_report = analyzer.generate_full_report(df)
                    if expert_report and expert_report.get('score', 0) >= 5:  # RAISED from 3 to 5 for quality
                        # QUALITY SETUP: Score 5+ (Strong momentum + catalyst)
                        msg = f"🚨 **MAJOR CATALYST ALERT: {symbol}** 🚨\n\n"
                        msg += f"📰 **News**: {title}\n\n"
                        if tech_alert:
                            msg += f"**Technical Setup**:\n{tech_alert}\n"
                        msg += f"**EXPERT RATING**: {expert_report['rating']} (Score: {expert_report['score']}/12)\n\n"
                        msg += f"**Trade Plan**:\n"
                        msg += f"Entry: ${expert_report['entry']:.2f}\n"
                        msg += f"Stop: ${expert_report['stop']:.2f}\n"
                        msg += f"Target: ${expert_report['target']:.2f}\n"
                        msg += f"R/R: 1:{expert_report['risk_reward']:.1f}\n\n"
                        msg += "**Why This Setup**:\n"
                        for reason in expert_report['reasons'][:3]:
                            msg += f"{reason}\n"
                        
                        print(f"✅ Sending CATALYST ALERT for {symbol} (Score: {expert_report['score']})...")
                        if CHAT_ID != "YOUR_CHAT_ID":
                            bot_instance.send_alert_sync(CHAT_ID, msg)
                    else:
                        score = expert_report.get('score', 0) if expert_report else 0
                        print(f"Major news for {symbol} but expert score too low ({score}/12) - skipping.")
                except Exception as e:
                    print(f"Error running expert analysis on {symbol}: {e}")
            else:
                print(f"Major news for {symbol} but no data available - skipping alert.")



def scan_pre_breakouts(bot_instance):
    """
    Scans for PRE-BREAKOUT setups (EARLY WARNING SIGNALS).
    Catches stocks BEFORE they move - 5-15 minutes earlier than traditional alerts.
    
    Criteria (Need 2 of 3):
    1. Volume Precursor - Volume building but price flat
    2. Tight Consolidation - Coiling pattern
    3. Near Resistance - Within 5% of breakout level
    """
    print("🔍 Scanning for PRE-BREAKOUT setups...")
    
    dm = DataManager()
    analyzer = Analyzer()
    
    # Get comprehensive stock universe
    tickers = dm.get_comprehensive_stock_universe()
    
    # Limit to top 100 for faster scanning
    tickers = tickers[:100]
    
    for ticker in tickers:
        try:
            df = dm.get_stock_history(ticker)
            if df.empty or len(df) < 50:
                continue
            
            # Check early warning signals
            volume_precursor = analyzer.check_volume_precursor(df)
            tight_consolidation = analyzer.check_tight_consolidation(df)
            near_resistance, resistance_level = analyzer.is_near_resistance(df)
            
            # Count signals
            signals = sum([volume_precursor, tight_consolidation, near_resistance])
            
            # Need at least 2 signals for quality
            if signals >= 2:
                current_price = df['Close'].iloc[-1]
                sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
                
                # Additional quality filter: Must be above 20 SMA
                if current_price < sma_20:
                    continue
                
                # Build alert message
                setup_desc = []
                if volume_precursor:
                    setup_desc.append("Volume building")
                if tight_consolidation:
                    setup_desc.append("Tight consolidation")
                if near_resistance:
                    setup_desc.append(f"Near resistance ${resistance_level:.2f}")
                
                msg = f"🚨 **PRE-BREAKOUT ALERT: {ticker}** 🚨\n\n"
                msg += f"📊 Setup: {' + '.join(setup_desc)}\n"
                msg += f"💰 Current Price: ${current_price:.2f}\n"
                
                if near_resistance:
                    msg += f"🎯 Watch Breakout: ${resistance_level:.2f}\n"
                
                msg += f"\n⚠️ **Early Stage** - Confirm breakout before entry\n"
                msg += f"✅ Quality Signals: {signals}/3\n"
                
                print(f"✅ PRE-BREAKOUT: {ticker} ({signals} signals)")
                
                # Create unique ID to prevent dupes
                alert_id = f"prebreakout:{ticker}:{int(current_price)}"
                if not db.is_item_seen(alert_id):
                    db.add_seen_item(alert_id, "prebreakout")
                    bot_instance.send_alert_sync(CHAT_ID, msg)
                    
        except Exception as e:
            print(f"Error scanning {ticker} for pre-breakout: {e}")
            continue
    
    print("✅ Pre-breakout scan complete")


def scan_actives(bot_instance):
    """
    Scans 'Most Active' stocks every 15 minutes for extreme signals.
    NOW WITH EXPERT ANALYSIS: Picks top 2 movers and provides trade plans!
    - 5x Volume Spikes
    - 52-Week Highs
    - Expert Analysis with Entry/Exit/Target
    """
    print(f"[{datetime.datetime.now().strftime('%H:%M')}] Scanning Most Active Stocks...")
    dm = DataManager()
    analyzer = Analyzer()
    
    # Use comprehensive stock universe instead of just most active
    stock_universe = dm.get_comprehensive_stock_universe()
    print(f"Scanning {len(stock_universe)} stocks for movers...")
    
    # Track movers with their data for analysis
    movers_for_analysis = []
    simple_alerts = []
    
    for ticker in stock_universe:

        try:
            df = dm.get_stock_history(ticker)
            if df.empty:
                continue
            
            signals = []
            # 1. Check 5x Volume
            has_volume_spike = analyzer.check_volume_spike(df, threshold=5.0)
            if has_volume_spike:
                signals.append("🔊 5x Volume Spike")
                
            # 2. Check 52-Week High
            has_new_high = analyzer.check_new_high(df)
            if has_new_high:
                signals.append("🚀 New 52-Week High")
                
            if signals:
                line = f"**{ticker}**: {', '.join(signals)}"
                # Deduplicate
                if not is_seen(line, "technical"):
                    save_seen(line, "technical")
                    simple_alerts.append(line)

                    
                    # Save for expert analysis
                    movers_for_analysis.append({
                        'ticker': ticker,
                        'df': df,
                        'signals': signals
                    })
                    
        except Exception:
            continue
    
    if not simple_alerts:
        return
    
    # STEP 1: Send simple mover alert first
    msg = "🔥 **Market Movers Detected** 🔥\n\n" + "\n".join(simple_alerts)
    msg += "\n\n⏳ _Analyzing top movers for trade setups..._"
    print("Sending initial movers alert...")
    if CHAT_ID != "YOUR_CHAT_ID":
        bot_instance.send_alert_sync(CHAT_ID, msg)
    
    # STEP 2: Analyze movers and pick top 2
    if movers_for_analysis:
        print(f"Analyzing {len(movers_for_analysis)} movers for trade setups...")
        scored_movers = []
        
        for mover in movers_for_analysis:
            try:
                # Run expert analysis
                report = analyzer.generate_full_report(mover['df'])
                if report and report.get('score', 0) >= 6:  # Only quality setups
                    scored_movers.append({
                        'ticker': mover['ticker'],
                        'score': report['score'],
                        'report': report,
                        'signals': mover['signals']
                    })
            except:
                continue
        
        if scored_movers:
            # Sort by score and pick top 2
            scored_movers.sort(key=lambda x: x['score'], reverse=True)
            top_2 = scored_movers[:2]
            
            # STEP 3: Send detailed trade plans for top 2
            trade_msg = "🎯 **TOP 2 MOVER TRADE SETUPS** 🎯\n"
            trade_msg += "_Expert analysis on the strongest movers_\n\n"
            
            for i, mover in enumerate(top_2, 1):
                ticker = mover['ticker']
                r = mover['report']
                
                trade_msg += f"{'='*40}\n"
                trade_msg += f"**#{i}. {ticker}** (Score: {r['score']}/12)\n"
                trade_msg += f"Signals: {', '.join(mover['signals'])}\n\n"
                
                trade_msg += f"**RATING**: {r['rating']}\n\n"
                
                trade_msg += f"📈 **TRADE PLAN**:\n"
                trade_msg += f"• Entry: ${r['entry']:.2f}\n"
                trade_msg += f"• Stop Loss: ${r['stop']:.2f}\n"
                trade_msg += f"• Target: ${r['target']:.2f}\n"
                trade_msg += f"• Risk/Reward: 1:{r['risk_reward']:.1f}\n\n"
                
                trade_msg += f"**Why This Setup**:\n"
                for reason in r['reasons'][:3]:
                    trade_msg += f"{reason}\n"
                
                trade_msg += "\n"
            
            trade_msg += "⚠️ _Manage risk: Don't risk more than 2-5% per trade._"
            
            print(f"Sending trade plans for top 2 movers: {[m['ticker'] for m in top_2]}")
            if CHAT_ID != "YOUR_CHAT_ID":
                bot_instance.send_alert_sync(CHAT_ID, trade_msg)
        else:
            # No quality setups found
            no_setup_msg = "📊 Market movers detected but no high-quality trade setups found (score <6/12).\n\n"
            no_setup_msg += "_Staying patient for better risk/reward opportunities._"
            if CHAT_ID != "YOUR_CHAT_ID":
                bot_instance.send_alert_sync(CHAT_ID, no_setup_msg)


def generate_top_picks(bot_instance):
    """
    Scans S&P 100 (High Liquidity) to find the Top 2 highest potential trades for the day.
    Generates a detailed trade plan with Entry, Stop, Target, and Options.
    """
    print("Analyzing S&P 100 for Top Picks...")
    dm = DataManager()
    analyzer = Analyzer()
    
    # Use S&P 100 tickers (Hardcoded subset for speed/reliability if API fails, or fetch)
    # For now, let's fetch S&P 500 and take top 100 by market cap logic (or just first 100)
    full_list = dm.get_sp500_tickers()
    if not full_list:
        # Fallback list of liquid stocks
        scan_list = ["AAPL", "NVDA", "TSLA", "AMD", "MSFT", "AMZN", "GOOGL", "META", "NFLX", "BA", "JPM", "DIS", "SPY", "QQQ", "IWM", "COIN", "MARA", "PLTR", "SOFI", "DKNG"]
    else:
        scan_list = full_list[:100] # Approx top 100
        
    scored_stocks = []
    
    for ticker in scan_list:
        try:
            df = dm.get_stock_history(ticker)
            if df.empty:
                continue
                
            # Get Technical Score
            report = analyzer.generate_full_report(df)
            if not report:
                continue
                
            score = report.get('score', 0)
            
            # STRICT: Only picks with score >= 6 (BUY or better)
            if score >= 6:
                scored_stocks.append((score, ticker, df, report))
                
        except Exception:
            continue
            
    # Sort by score (Highest first)
    scored_stocks.sort(key=lambda x: x[0], reverse=True)
    
    # Pick Top 2
    top_picks = scored_stocks[:2]
    
    if not top_picks:
        return "No high-probability setups found today. Cash is a position! 🛡️"
        
    msg = "🏆 **CHALLENGE 25K to 1M: TOP PICKS** 🏆\n"
    msg += "Here are the 2 highest potential trades for today:\n\n"
    
    for score, ticker, df, report in top_picks:
        # Calculate Plan
        plan = analyzer.calculate_trade_plan(df, signal_type="LONG")
        option = analyzer.suggest_option(plan['entry'], direction="LONG")
        
        msg += f"🚀 **{ticker}** (Score: {score}/12)\n"
        msg += f"**Rating**: {report['rating']}\n"
        msg += f"**Entry**: ${report['entry']:.2f}\n"
        msg += f"**Stop Loss**: ${report['stop']:.2f}\n"
        msg += f"**Target**: ${report['target']:.2f}\n"
        msg += f"**Risk/Reward**: 1:{report['risk_reward']:.1f}\n"
        msg += f"**Option**: {option}\n\n"
        msg += "**Why This Setup:**\n"
        for reason in report['reasons'][:3]:  # Top 3 reasons
            msg += f"{reason}\n"
        msg += "-----------------------------\n"
        
    msg += "\n⚠️ _Strict Risk Management: Never risk more than 2-5% of account per trade._"
    
    return msg

def market_index_analysis_morning(bot_instance):
    """
    Sends BEFORE MARKET OPEN (9:00 AM) index analysis
    Helps decide market bias for the day
    """
    print("[9:00 AM] Generating Pre-Market Index Analysis...")
    
    try:
        index_analyzer = IndexAnalyzer()
        report = index_analyzer.generate_market_report()
        
        header = "🌅 **PRE-MARKET INDEX ANALYSIS** 🌅\n"
        header += "_Market opens in 30 minutes. Use this to plan your day._\n\n"
        
        full_report = header + report
        
        if CHAT_ID != "YOUR_CHAT_ID":
            bot_instance.send_alert_sync(CHAT_ID, full_report)
            print("✅ Pre-market index analysis sent!")
    except Exception as e:
        print(f"Error in morning index analysis: {e}")


def market_index_analysis_close(bot_instance):
    """
    Sends AFTER MARKET CLOSE (4:15 PM) index analysis
    Reviews the day's performance and sets up for tomorrow
    """
    print("[4:15 PM] Generating Post-Market Index Analysis...")
    
    try:
        index_analyzer = IndexAnalyzer()
        report = index_analyzer.generate_market_report()
        
        header = "🌆 **POST-MARKET INDEX ANALYSIS** 🌆\n"
        header += "_Market closed. Review today's action and plan tomorrow._\n\n"
        
        full_report = header + report
        
        if CHAT_ID != "YOUR_CHAT_ID":
            bot_instance.send_alert_sync(CHAT_ID, full_report)
            print("✅ Post-market index analysis sent!")
    except Exception as e:
        print(f"Error in closing index analysis: {e}")


def daily_briefing(bot_instance):
    """
    Sends the big daily report at 8:00 AM.
    """
    print("Generating Daily Briefing...")
    dm = DataManager()
    
    # 1. Top Picks (The "Meat" of the briefing)
    picks_msg = generate_top_picks(bot_instance)
    
    report = "🚀 **Daily Stock Briefing** 🚀\n\n"
    
    # Earnings
    earnings = dm.get_earnings_today()
    if earnings:
        report += f"📊 **Earnings**: {', '.join(earnings[:5])}\n\n"
        
    # Economic
    econ = dm.get_economic_data()
    if econ:
        report += "🌍 **Economic Events**:\n" + "\n".join(econ) + "\n\n"
        
    # Splits
    splits = dm.get_stock_splits()
    if splits:
        report += f"✂️ **Splits**: {', '.join(splits)}\n\n"

    # Mission Statement / Info
    report += "-----------------------------\n"
    report += "🤖 **Bot Info**: I am your AI Analyst, scanning the S&P 100 24/7 for high-probability setups.\n"
    report += "🎯 **The Goal**: Turn $25k to $1M in 1 Year.\n"
    report += "📉 **Strategy**: 1-2 High Quality Trades/Day. Strict Risk Management.\n"

    if CHAT_ID != "YOUR_CHAT_ID":
        # Send Picks FIRST (Priority)
        bot_instance.send_alert_sync(CHAT_ID, picks_msg)
        # Then the general briefing
        bot_instance.send_alert_sync(CHAT_ID, report)

def run_scheduler(bot_instance):
    # 0. INSTITUTIONAL ACCUMULATION (Every 5 minutes - HIGHEST PRIORITY)
    schedule.every(5).minutes.do(scan_institutional_accumulation, bot_instance)
    
    # 1. Intraday News (Every 5 minutes)
    schedule.every(5).minutes.do(check_news, bot_instance)
    
    # 2. Market Movers Scan (Every 15 minutes)
    schedule.every(15).minutes.do(scan_actives, bot_instance)
    
    # 3. Daily Briefing (8:00 AM)
    schedule.every().day.at("08:00").do(daily_briefing, bot_instance)
    
    # 4. PRE-MARKET Index Analysis (9:00 AM - Before market open)
    schedule.every().day.at("09:00").do(market_index_analysis_morning, bot_instance)
    
    # 5. POST-MARKET Index Analysis (4:15 PM - After market close)
    schedule.every().day.at("16:15").do(market_index_analysis_close, bot_instance)
    
    # Run immediate checks on startup
    print("Running startup checks...")
    scan_institutional_accumulation(bot_instance)  # Check for institutional activity first!
    check_news(bot_instance)
    scan_actives(bot_instance)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    import sys
    
    # Fix Windows console encoding for emojis
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    try:
        print("Running startup checks...")
        
        # Initialize bot
        bot = StockBot(TELEGRAM_TOKEN)
        dm = DataManager()
        analyzer = Analyzer()
        
        # Start scheduler in background
        scheduler_thread = threading.Thread(target=run_scheduler, args=(bot,), daemon=True)
        scheduler_thread.start()
        
        print(f"[{datetime.datetime.now().strftime('%H:%M')}] Checking for Breaking News...")
        check_news(bot)
        
        # Keep the bot alive
        bot.run()
    except KeyboardInterrupt:
        print("\n[OK] Bot stopped by user")
    except Exception as e:
        print(f"[ERROR] Bot crashed: {e}")
