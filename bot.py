import logging
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from datetime import datetime, timedelta
from config import FMP_API_KEY

class StockBot:
    def __init__(self, token):
        self.token = token
        self.app = ApplicationBuilder().token(token).build()
        
        # Initialize User Manager
        from user_manager import UserManager
        self.user_manager = UserManager()
        
        self.setup_handlers()


    def setup_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.app.add_handler(start_handler)
        
        # Add /index command for on-demand market analysis
        index_handler = CommandHandler('index', self.cmd_index)
        self.app.add_handler(index_handler)
        
        # Add /picks command for on-demand stock picks
        picks_handler = CommandHandler('picks', self.cmd_picks)
        self.app.add_handler(picks_handler)
        
        # Add /options command for options chain
        options_handler = CommandHandler('options', self.cmd_options)
        self.app.add_handler(options_handler)

        # Add /whales command for insider/institutional tracking
        whales_handler = CommandHandler('whales', self.cmd_whales)
        self.app.add_handler(whales_handler)

        # Add /volume command for bullish/bearish volume analysis
        volume_handler = CommandHandler('volume', self.cmd_volume)
        self.app.add_handler(volume_handler)

        # Add /chart command for technical chart generation
        chart_handler = CommandHandler('chart', self.cmd_chart)
        self.app.add_handler(chart_handler)

        # Add timeframe-specific breakout commands
        intraday_handler = CommandHandler('intraday', self.cmd_intraday)
        self.app.add_handler(intraday_handler)
        
        weekly_handler = CommandHandler('weekly', self.cmd_weekly)
        self.app.add_handler(weekly_handler)
        
        monthly_handler = CommandHandler('monthly', self.cmd_monthly)
        self.app.add_handler(monthly_handler)
        
        # Add /squeeze command for squeeze breakout analysis
        squeeze_handler = CommandHandler('squeeze', self.cmd_squeeze)
        self.app.add_handler(squeeze_handler)
        
        # Add /fundamentals command for fundamental analysis
        fundamentals_handler = CommandHandler('fundamentals', self.cmd_fundamentals)
        self.app.add_handler(fundamentals_handler)
        
        # Add handler for text messages (stock tickers)
        msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
        self.app.add_handler(msg_handler)

        # Add handler for unknown commands (Must be last)
        unknown_handler = MessageHandler(filters.COMMAND, self.unknown_command)
        self.app.add_handler(unknown_handler)

        # Add /buy command
        buy_handler = CommandHandler('buy', self.cmd_buy)
        self.app.add_handler(buy_handler)

        # Add /portfolio command
        portfolio_handler = CommandHandler('portfolio', self.cmd_portfolio)
        self.app.add_handler(portfolio_handler)




    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = "🤖 **Stock Alert Bot Active!** 🤖\n\n"
        msg += "I'm your AI analyst tracking the market 24/7.\n\n"
        
        msg += "📊 **MARKET ANALYSIS**\n"
        msg += "/index - Market index analysis (S&P, Nasdaq, Dow)\n"
        msg += "/picks - Top 2 stock picks for the day\n"
        msg += "/volume - Top 5 bullish & bearish volume stocks\n\n"
        
        msg += "🔍 **BREAKOUT & PATTERNS**\n"
        msg += "/squeeze - TTM Squeeze breakouts (or /squeeze TICKER)\n"
        msg += "/intraday - Top 2 breakouts for day trading\n"
        msg += "/weekly - Top 2 breakouts for swing trading\n"
        msg += "/monthly - Top 2 breakouts for position trading\n\n"
        
        msg += "💰 **OPTIONS & WHALES**\n"
        msg += "/options - Top 5 options (or /options TICKER)\n"
        msg += "/whales - Insider/institutional activity (or /whales TICKER)\n\n"
        
        msg += "📈 **STOCK ANALYSIS**\n"
        msg += "/chart TICKER - Technical analysis chart\n"
        msg += "/fundamentals TICKER - Fundamental analysis (P/E, margins, growth)\n"
        msg += "Send TICKER - Instant expert analysis (e.g., AAPL, TSLA)\n\n"
        
        msg += "💼 **PAPER TRADING**\n"
        msg += "/portfolio - View your positions\n"
        msg += "/buy - Execute paper trades\n\n"
        
        msg += "/start - Show this message\n\n"

        msg += "**Automatic Alerts:**\n"
        msg += "• 9:00 AM - Pre-market index analysis\n"
        msg += "• 4:15 PM - Post-market index analysis\n"
        msg += "• 8:00 AM - Daily stock picks\n"
        msg += "• Real-time breaking news\n"
        msg += "• Every 15 min - Market movers with trade plans"
        
        # Register user
        self.user_manager.register_user(update)
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="Markdown")


    async def cmd_index(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /index command - On-demand market index analysis"""
        await update.message.reply_text("⏳ Analyzing all major market indices... (Takes ~10 seconds)")
        
        try:
            # Import here to avoid circular dependency
            from index_analyzer import IndexAnalyzer
            
            analyzer = IndexAnalyzer()
            report = analyzer.generate_market_report()
            
            header = "📊 **ON-DEMAND INDEX ANALYSIS** 📊\n"
            header += "_Real-time analysis requested by you_\n\n"
            
            full_report = header + report
            
            # Send the report
            self.send_alert_sync(update.effective_chat.id, full_report)
            
        except Exception as e:
            error_msg = f"❌ Error generating index analysis: {str(e)}\n"
            error_msg += "Please try again in a moment."
            await update.message.reply_text(error_msg)
    
    async def cmd_picks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /picks command - On-demand top stock picks"""
        await update.message.reply_text("🔍 Scanning 500+ stocks for top 2 picks... (Takes ~40-60 seconds)")
        
        try:
            from data_manager import DataManager
            from analyzer import Analyzer
            
            dm = DataManager()
            analyzer = Analyzer()
            
            # Use comprehensive stock universe
            scan_list = dm.get_comprehensive_stock_universe()
            print(f"Scanning {len(scan_list)} stocks for top picks...")
            
            scored_stocks = []
            
            for ticker in scan_list:
                try:
                    df = dm.get_stock_history(ticker)
                    if df.empty:
                        continue
                    
                    report = analyzer.generate_full_report(df)
                    if not report:
                        continue
                    
                    score = report.get('score', 0)
                    
                    if score >= 6:
                        scored_stocks.append((score, ticker, df, report))
                except:
                    continue
            
            # Sort by score
            scored_stocks.sort(key=lambda x: x[0], reverse=True)
            top_picks = scored_stocks[:2]
            
            if not top_picks:
                msg = "📊 **NO HIGH-PROBABILITY SETUPS FOUND**\n\n"
                msg += "Cash is a position! No trades meet our strict criteria (score ≥6/12) right now.\n\n"
                msg += "_Staying patient for better opportunities._"
                await update.message.reply_text(msg, parse_mode="Markdown")
                return
            
            msg = "🏆 **TOP 2 STOCK PICKS** 🏆\n"
            msg += "_On-demand analysis of highest potential trades_\n\n"
            
            for score, ticker, df, report in top_picks:
                msg += f"🚀 **{ticker}** (Score: {score}/12)\n"
                msg += f"**Rating**: {report['rating']}\n"
                msg += f"**Entry**: ${report['entry']:.2f}\n"
                msg += f"**Stop Loss**: ${report['stop']:.2f}\n"
                msg += f"**Target**: ${report['target']:.2f}\n"
                msg += f"**Risk/Reward**: 1:{report['risk_reward']:.1f}\n\n"
                msg += "**Why This Setup:**\n"
                for reason in report['reasons'][:3]:
                    msg += f"{reason}\n"
                msg += "-----------------------------\n"
            
            msg += "\n⚠️ _Manage risk: Never risk more than 2-5% per trade._"
            
            # Send the report
            self.send_alert_sync(update.effective_chat.id, msg)
            
        except Exception as e:
            error_msg = f"❌ Error generating stock picks: {str(e)}\n"
            error_msg += "Please try again in a moment."
            await update.message.reply_text(error_msg)
    
    async def cmd_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /options command - Get top 5 best options across market or for specific ticker"""
        
        # Check if ticker specified
        if context.args and len(context.args) > 0:
            # SPECIFIC TICKER ANALYSIS
            await self._analyze_single_ticker_options(update, context, context.args[0].upper())
        else:
            # SCAN ALL STOCKS FOR TOP 5 OPTIONS
            await self._scan_for_top_options(update, context)
    
    async def _scan_for_top_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Scan top stocks and find the 5 best options for next 3 months using yfinance"""
        await update.message.reply_text("🔍 Scanning S&P 100 for top 5 option plays... (Takes ~60-90 seconds)")
        
        try:
            import requests
            from data_manager import DataManager
            from analyzer import Analyzer
            from options_helper import get_options_for_ticker, score_option
            
            dm = DataManager()
            analyzer = Analyzer()
            api_key = FMP_API_KEY
            
            # Get top stocks to scan
            full_list = dm.get_sp500_tickers()
            if not full_list:
                scan_list = ["AAPL", "NVDA", "TSLA", "AMD", "MSFT", "AMZN", "GOOGL", "META", "NFLX", "SPY", "QQQ", "PLTR", "COIN", "SOFI", "BA", "JPM", "DIS"]
            else:
                scan_list = full_list[:30]  # Reduced to top 30 for speed with yfinance
            
            all_scored_options = []
            
            for ticker in scan_list:
                try:
                    # Get stock analysis
                    df = dm.get_stock_history(ticker)
                    if df.empty:
                        continue
                    
                    stock_analysis = analyzer.generate_full_report(df)
                    if not stock_analysis or stock_analysis['score'] < 5:  # Only analyze good setups
                        continue
                    
                    # Get current price
                    quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
                    quote_response = requests.get(quote_url, timeout=5)
                    quote_data = quote_response.json()
                    
                    if not quote_data or len(quote_data) == 0:
                        continue
                    
                    current_price = quote_data[0]['price']
                    
                    # Get options using yfinance helper
                    calls_df, puts_df = get_options_for_ticker(ticker)
                    
                    if calls_df is None and puts_df is None:
                        continue
                    
                    # Determine direction based on stock score
                    score = stock_analysis['score']
                    if score >= 7:
                        direction = "call"
                        options_to_check = calls_df
                    elif score <= 3:
                        direction = "put"
                        options_to_check = puts_df
                    else:
                        direction = "call"  # Default bullish
                        options_to_check = calls_df
                    
                    if options_to_check is None or options_to_check.empty:
                        continue

                    # Score options
                    for _, opt in options_to_check.iterrows():
                        scored = score_option(opt, current_price, score, direction)
                        if scored:
                            scored['ticker'] = ticker
                            scored['type'] = direction.upper()
                            scored['stock_rating'] = stock_analysis['rating']
                            scored['current_price'] = current_price
                            scored['target'] = stock_analysis['target']
                            scored['breakeven'] = scored['strike'] + scored['last_price'] if direction == "call" else scored['strike'] - scored['last_price']
                            all_scored_options.append(scored)
                    
                except Exception as e:
                    print(f"Error analyzing {ticker}: {e}")
                    continue
            
            if not all_scored_options:
                await update.message.reply_text("❌ No suitable options found across the market right now.")
                return
            
            # Sort by score and get top 5
            all_scored_options.sort(key=lambda x: x['score'], reverse=True)
            top_5 = all_scored_options[:5]
            
            # Build message
            msg = "🏆 **TOP 5 OPTION PLAYS** 🏆\n"
            msg += "_Best options across market (yfinance data)_\n\n"
            
            for i, opt in enumerate(top_5, 1):
                msg += f"**#{i}. {opt['ticker']} ${opt['strike']:.0f} {opt['type']}**\n"
                msg += f"Stock: ${opt['current_price']:.2f} | Rating: {opt['stock_rating']}\n"
                msg += f"Option: ${opt['last_price']:.2f} | Exp: {opt['expiration']} ({opt['dte']} DTE)\n"
                msg += f"Breakeven: ${opt['breakeven']:.2f} | Target: ${opt['target']:.2f}\n"
                msg += f"Delta: {opt['delta']:.2f} | IV: {opt['iv']:.1f}% | Vol: {opt['volume']:,}\n"
                msg += f"Score: {opt['score']}/25 ⭐\n"
                msg += f"{'='*40}\n\n"
            
            msg += "⚠️ _Options can expire worthless. Risk only what you can afford to lose._\n"
            msg += "📈 _75-year expert methodology_"
            
            self.send_alert_sync(update.effective_chat.id, msg)
            
        except Exception as e:
            error_msg = f"❌ Error scanning for options: {str(e)}\n"
            error_msg += "Please try again in a moment."
            await update.message.reply_text(error_msg)
    
    async def _analyze_single_ticker_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, ticker: str):
        """Analyze options for a specific ticker using yfinance"""
        await update.message.reply_text(f"🔍 Analyzing {ticker} options for next 3 months...")
        
        try:
            import requests
            from data_manager import DataManager
            from analyzer import Analyzer
            from options_helper import get_options_for_ticker, score_option
            
            # STEP 1: Get stock analysis
            dm = DataManager()
            analyzer = Analyzer()
            df = dm.get_stock_history(ticker)
            
            if df.empty:
                await update.message.reply_text(f"❌ Could not find data for {ticker}")
                return
            
            stock_analysis = analyzer.generate_full_report(df)
            if not stock_analysis:
                await update.message.reply_text(f"❌ Not enough data to analyze {ticker}")
                return
            
            # STEP 2: Get current stock price (still use FMP for price as it's fast)
            api_key = FMP_API_KEY
            quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={api_key}"
            quote_response = requests.get(quote_url)
            quote_data = quote_response.json()
            
            if not quote_data or len(quote_data) == 0:
                await update.message.reply_text(f"❌ Could not find ticker {ticker}")
                return
            
            current_price = quote_data[0]['price']
            
            # STEP 3: Get options using yfinance
            calls_df, puts_df = get_options_for_ticker(ticker)
            
            if calls_df is None and puts_df is None:
                await update.message.reply_text(f"❌ No options data available for {ticker}")
                return
            
            # STEP 4: Determine direction
            score = stock_analysis['score']
            rating = stock_analysis['rating']
            
            if score >= 7:
                direction = "call"
                sentiment = "BULLISH"
                options_to_check = calls_df
            elif score <= 3:
                direction = "put"
                sentiment = "BEARISH"
                options_to_check = puts_df
            else:
                direction = "call"
                sentiment = "NEUTRAL (Slight Bullish Bias)"
                options_to_check = calls_df
            
            if options_to_check is None or options_to_check.empty:
                 await update.message.reply_text(f"❌ No {direction}s available for {ticker}")
                 return

            # STEP 5: Score options
            scored_options = []
            for _, opt in options_to_check.iterrows():
                scored = score_option(opt, current_price, score, direction)
                if scored:
                    scored_options.append(scored)
            
            if not scored_options:
                await update.message.reply_text(f"❌ No suitable options found for {ticker}")
                return
            
            # Sort by score
            scored_options.sort(key=lambda x: x['score'], reverse=True)
            best_option = scored_options[0]
            
            # STEP 6: Build recommendation
            msg = f"📊 **{ticker} OPTIONS ANALYSIS** 📊\n\n"
            msg += f"**Stock Price**: ${current_price:.2f}\n"
            msg += f"**Stock Rating**: {rating} ({score}/12)\n"
            msg += f"**Direction**: {sentiment}\n"
            msg += f"{'='*40}\n\n"
            
            msg += f"🎯 **EXPERT RECOMMENDATION** 🎯\n\n"
            msg += f"**{direction.upper()}**: ${best_option['strike']:.0f} Strike\n"
            msg += f"**Expiration**: {best_option['expiration']} ({best_option['dte']} DTE)\n"
            msg += f"**Entry Price**: ${best_option['last_price']:.2f}\n"
            msg += f"**Delta**: {best_option['delta']:.2f}\n"
            msg += f"**IV**: {best_option['iv']:.1f}%\n"
            msg += f"**Volume**: {best_option['volume']:,}\n"
            msg += f"**Open Interest**: {best_option['oi']:,}\n"
            msg += f"**Confidence**: {best_option['score']}/13 ⭐\n\n"
            
            msg += f"**Why This Option:**\n"
            
            if direction == "call":
                target_price = stock_analysis['target']
                breakeven = best_option['strike'] + best_option['last_price']
                profit_potential = target_price - breakeven
                
                msg += f"✅ Stock showing {sentiment} momentum\n"
                msg += f"✅ {best_option['dte']} days gives time for move\n"
                msg += f"✅ Delta {best_option['delta']:.2f} = good leverage\n"
                msg += f"✅ Liquid (Vol: {best_option['volume']:,})\n"
                msg += f"✅ Breakeven: ${breakeven:.2f}\n"
                msg += f"✅ Target: ${target_price:.2f}\n"
                if profit_potential > 0:
                    msg += f"✅ Potential: ${profit_potential:.2f}/share if target hit\n"
            else:
                stop_price = stock_analysis['stop']
                breakeven = best_option['strike'] - best_option['last_price']
                profit_potential = breakeven - stop_price
                
                msg += f"✅ Stock showing {sentiment} weakness\n"
                msg += f"✅ {best_option['dte']} days for downside\n"
                msg += f"✅ Delta {best_option['delta']:.2f} = protection\n"
                msg += f"✅ Liquid (Vol: {best_option['volume']:,})\n"
                msg += f"✅ Breakeven: ${breakeven:.2f}\n"
                if profit_potential > 0:
                    msg += f"✅ Downside protection down to ${stop_price:.2f}\n"
            
            msg += f"\n{'='*40}\n\n"
            
            # Show top 3 alternatives
            msg += f"**Alternative Options (Top 3):**\n\n"
            for i, alt in enumerate(scored_options[1:4], 2):
                msg += f"#{i}. ${alt['strike']:.0f} {direction.upper()} - {alt['expiration']}\n"
                msg += f"   ${alt['last_price']:.2f} | {alt['dte']} DTE | Score: {alt['score']}/13\n\n"
            
            msg += f"⚠️ _Risk: Options can expire worthless. Only risk what you can afford to lose._\n"
            msg += f"📈 _Based on 75 years of options trading experience_"
            
            self.send_alert_sync(update.effective_chat.id, msg)
            
        except Exception as e:
            error_msg = f"❌ Error analyzing options: {str(e)}\n"
            error_msg += "Please check the ticker and try again."
            await update.message.reply_text(error_msg)

    async def cmd_whales(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /whales command - Track insider and institutional activity"""
        
        # Check if ticker specified
        if context.args and len(context.args) > 0:
            ticker = context.args[0].upper()
            await self._analyze_single_ticker_whales(update, context, ticker)
        else:
            await self._scan_market_whales(update, context)

    async def _scan_market_whales(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Scan for top insider purchases across the market"""
        await update.message.reply_text("🐋 Scanning for recent Whale activity (Insider Buys)...")
        
        try:
            api_key = FMP_API_KEY
            # Use RSS feed for latest transactions
            url = f"https://financialmodelingprep.com/api/v4/insider-trading-rss-feed?limit=100&apikey={api_key}"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if not data:
                await update.message.reply_text("❌ No recent insider data found.")
                return
            
            # Filter for Purchases
            buys = [d for d in data if 'Purchase' in d.get('transactionType', '')]
            
            # Calculate value if not present (sometimes it is, sometimes not)
            # FMP RSS feed usually has: symbol, filingDate, transactionDate, transactionType, securitiesTransacted, price, securitiesOwned
            
            significant_buys = []
            for trade in buys:
                try:
                    shares = float(trade.get('securitiesTransacted', 0))
                    price = float(trade.get('price', 0))
                    value = shares * price
                    
                    if value > 100000: # Filter > $100k
                        trade['total_value'] = value
                        significant_buys.append(trade)
                except:
                    continue
            
            # Sort by value
            significant_buys.sort(key=lambda x: x['total_value'], reverse=True)
            top_buys = significant_buys[:5]
            
            if not top_buys:
                await update.message.reply_text("❌ No significant insider buys (> $100k) found recently.")
                return
            
            msg = "🐋 **WHALE ALERT: TOP INSIDER BUYS** 🐋\n"
            msg += "_Significant recent insider purchases_\n\n"
            
            for i, trade in enumerate(top_buys, 1):
                symbol = trade.get('symbol', 'UNKNOWN')
                person = trade.get('reportingName', 'Unknown')
                title = trade.get('typeOfOwner', 'Insider')
                date = trade.get('transactionDate', 'N/A')
                value = trade.get('total_value', 0)
                price = trade.get('price', 0)
                
                msg += f"**#{i}. {symbol}** - ${value:,.0f}\n"
                msg += f"👤 {person} ({title})\n"
                msg += f"📅 {date} @ ${price:.2f}\n"
                msg += f"{'='*30}\n\n"
            
            msg += "💡 _Insider buys are often a strong bullish signal._"
            
            self.send_alert_sync(update.effective_chat.id, msg)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error scanning whales: {str(e)}")

    async def _analyze_single_ticker_whales(self, update: Update, context: ContextTypes.DEFAULT_TYPE, ticker: str):
        """Analyze insider and institutional activity for a specific ticker"""
        await update.message.reply_text(f"🐋 Tracking Whales for {ticker}...")
        
        try:
            api_key = FMP_API_KEY
            
            # 1. Get Insider Trading
            insider_url = f"https://financialmodelingprep.com/api/v4/insider-trading?symbol={ticker}&limit=20&apikey={api_key}"
            insider_resp = requests.get(insider_url, timeout=10)
            insider_data = insider_resp.json()
            
            # 2. Get Institutional Holders
            inst_url = f"https://financialmodelingprep.com/api/v3/institutional-holder/{ticker}?apikey={api_key}"
            inst_resp = requests.get(inst_url, timeout=10)
            inst_data = inst_resp.json()
            
            msg = f"🐋 **WHALE REPORT: {ticker}** 🐋\n\n"
            
            # --- Insider Section ---
            msg += "**Recent Insider Activity:**\n"
            if insider_data:
                # Filter for meaningful trades (ignore small grants/awards if possible, but FMP mixes them)
                # We'll show top 3 recent transactions
                count = 0
                for trade in insider_data:
                    if count >= 3: break
                    
                    t_type = trade.get('transactionType', 'Unknown')
                    if 'Purchase' in t_type:
                        emoji = "🟢 BUY"
                    elif 'Sale' in t_type:
                        emoji = "🔴 SELL"
                    else:
                        emoji = "⚪ " + t_type
                        
                    shares = float(trade.get('securitiesTransacted', 0))
                    price = float(trade.get('price', 0))
                    value = shares * price
                    date = trade.get('transactionDate', 'N/A')
                    name = trade.get('reportingName', 'Insider')
                    
                    if value > 0: # Only show non-zero value trades
                        msg += f"{emoji} **${value:,.0f}** ({date})\n"
                        msg += f"   {name} @ ${price:.2f}\n"
                        count += 1
                
                if count == 0:
                    msg += "No recent significant open market trades found.\n"
            else:
                msg += "No insider trading data available.\n"
            
            msg += "\n"
            
            # --- Institutional Section ---
            msg += "**Top Institutional Holders:**\n"
            if inst_data:
                # Sort by percentage held if available, or shares
                # FMP v3 institutional-holder usually returns list
                # Sample: {'holder': 'Vanguard Group Inc', 'shares': 123456, 'dateReported': '2024-09-30', 'change': 123}
                
                # Sort by shares descending just in case
                inst_data.sort(key=lambda x: x.get('shares', 0), reverse=True)
                
                for i, holder in enumerate(inst_data[:3], 1):
                    name = holder.get('holder', 'Unknown')
                    shares = holder.get('shares', 0)
                    date = holder.get('dateReported', 'N/A')
                    
                    msg += f"{i}. **{name}**\n"
                    msg += f"   Shares: {shares:,.0f} (Reported: {date})\n"
            else:
                msg += "No institutional data available.\n"
                
            msg += "\n⚠️ _Data derived from SEC 13F and Form 4 filings._"
            
            self.send_alert_sync(update.effective_chat.id, msg)
            
        except Exception as e:
             await update.message.reply_text(f"❌ Error analyzing whales for {ticker}: {str(e)}")

    async def cmd_volume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /volume command - Show top 5 bullish and bearish volume stocks"""
        await update.message.reply_text("🔍 Scanning 500+ stocks for high volume... (Takes ~30-40 seconds)")
        
        try:
            from data_manager import DataManager
            from analyzer import Analyzer
            
            dm = DataManager()
            analyzer = Analyzer()
            
            # Get comprehensive stock universe
            stock_universe = dm.get_comprehensive_stock_universe()
            print(f"Scanning {len(stock_universe)} stocks for volume analysis...")
            
            bullish_stocks = []
            bearish_stocks = []
            
            # Analyze each stock for volume + price action
            scanned = 0
            for ticker in stock_universe:
                try:
                    df = dm.get_stock_history(ticker)
                    if df.empty or len(df) < 21:
                        continue
                    
                    scanned += 1
                    current_price = df['Close'].iloc[-1]
                    prev_close = df['Close'].iloc[-2]
                    current_volume = df['Volume'].iloc[-1]
                    avg_volume_20 = df['Volume'].iloc[-21:-1].mean()
                    
                    # Calculate price change %
                    price_change_pct = ((current_price - prev_close) / prev_close) * 100
                    
                    # Calculate volume ratio
                    volume_ratio = current_volume / avg_volume_20
                    
                    # Filter: Only stocks with 2x+ volume
                    if volume_ratio >= 2.0:
                        stock_data = {
                            'ticker': ticker,
                            'price_change': price_change_pct,
                            'volume_ratio': volume_ratio,
                            'price': current_price
                        }
                        
                        # Bullish: Price up + high volume
                        if price_change_pct > 0:
                            bullish_stocks.append(stock_data)
                        # Bearish: Price down + high volume
                        elif price_change_pct < 0:
                            bearish_stocks.append(stock_data)
                            
                except Exception:
                    continue
            
            print(f"Scanned {scanned} stocks, found {len(bullish_stocks)} bullish and {len(bearish_stocks)} bearish")
            
            # Sort by volume ratio and take top 5
            bullish_stocks.sort(key=lambda x: x['volume_ratio'], reverse=True)
            bearish_stocks.sort(key=lambda x: x['volume_ratio'], reverse=True)
            
            top_bullish = bullish_stocks[:5]
            top_bearish = bearish_stocks[:5]
            
            # Build message
            msg = "📊 **HIGH VOLUME ANALYSIS** 📊\n\n"
            
            # Bullish Volume
            msg += "🟢 **TOP 5 BULLISH VOLUME** 🟢\n"
            msg += "_(Price UP + High Volume)_\n\n"
            
            if top_bullish:
                for i, stock in enumerate(top_bullish, 1):
                    msg += f"**{i}. {stock['ticker']}** ${stock['price']:.2f}\n"
                    msg += f"   📈 +{stock['price_change']:.2f}% | 🔊 {stock['volume_ratio']:.1f}x Volume\n"
            else:
                msg += "_No significant bullish volume detected_\n"
            
            msg += "\n" + "="*40 + "\n\n"
            
            # Bearish Volume
            msg += "🔴 **TOP 5 BEARISH VOLUME** 🔴\n"
            msg += "_(Price DOWN + High Volume)_\n\n"
            
            if top_bearish:
                for i, stock in enumerate(top_bearish, 1):
                    msg += f"**{i}. {stock['ticker']}** ${stock['price']:.2f}\n"
                    msg += f"   📉 {stock['price_change']:.2f}% | 🔊 {stock['volume_ratio']:.1f}x Volume\n"
            else:
                msg += "_No significant bearish volume detected_\n"
            
            msg += "\n⚠️ _High volume indicates strong conviction. Use with other indicators._"
            
            await update.message.reply_text(msg, parse_mode="Markdown")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error analyzing volume: {str(e)}")

    async def cmd_chart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chart command - Generate technical analysis chart"""
        if not context.args or len(context.args) == 0:
            await update.message.reply_text("Usage: /chart TICKER\nExample: /chart AAPL")
            return
        
        ticker = context.args[0].upper()
        await update.message.reply_text(f"📊 Generating technical chart for {ticker}...")
        
        try:
            from data_manager import DataManager
            from chart_generator import ChartGenerator
            from analyzer import Analyzer
            
            dm = DataManager()
            chart_gen = ChartGenerator()
            analyzer = Analyzer()
            
            # Get stock data
            df = dm.get_stock_history(ticker)
            if df.empty:
                await update.message.reply_text(f"❌ Could not fetch data for {ticker}")
                return
            
            # Detect patterns
            patterns = {
                'Cup & Handle': analyzer.check_cup_and_handle(df),
                'Squeeze': analyzer.check_squeeze(df),
                'Breakout': analyzer.check_breakout(df),
                'VCP': analyzer.check_vcp(df),
                'RSI Divergence': analyzer.check_rsi_divergence(df)
            }
            
            # Generate chart
            chart_path = chart_gen.generate_chart(ticker, df, patterns)
            
            if chart_path and os.path.exists(chart_path):
                # Send chart as photo
                with open(chart_path, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=f"📊 {ticker} Technical Analysis Chart\n"
                                f"Indicators: SMA (20,50,200), EMA (9,21), RSI, MACD, Volume"
                    )
                
                # Cleanup old charts
                chart_gen.cleanup_old_charts(max_age_hours=24)
            else:
                await update.message.reply_text(f"❌ Error generating chart for {ticker}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")



    async def cmd_intraday(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /intraday command - Top 2 breakouts for day trading"""
        await update.message.reply_text("🔍 Scanning for INTRADAY breakouts (5min-1hr holds)... (~30s)")
    
        try:
            from data_manager import DataManager
            from analyzer import Analyzer
        
            dm = DataManager()
            analyzer = Analyzer()
        
            actives = dm.get_most_active()
            if not actives:
                actives = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "AMD", "MSFT", "META", "AMZN"]
        
            breakouts = []
        
            for ticker in actives[:50]:  # Scan top 50 most active
                try:
                    df = dm.get_stock_history(ticker, period="5d", interval="1d")
                    if df.empty or len(df) < 5:
                        continue
                
                    current_price = df['Close'].iloc[-1]
                    current_volume = df['Volume'].iloc[-1]
                    avg_volume = df['Volume'].iloc[-5:-1].mean()
                    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                
                    if volume_ratio >= 3.0:
                        high_5d = df['High'].iloc[-5:].max()
                        distance_from_high = ((current_price - high_5d) / high_5d) * 100
                    
                        if distance_from_high >= -2.0:
                            report = analyzer.generate_full_report(df)
                            if report and report['score'] >= 6:
                                breakouts.append({
                                    'ticker': ticker,
                                    'price': current_price,
                                    'volume_ratio': volume_ratio,
                                    'score': report['score'],
                                    'entry': report['entry'],
                                    'stop': report['stop'],
                                    'target': report['target'],
                                    'rating': report['rating']
                                })
                except:
                    continue
        
            breakouts.sort(key=lambda x: (x['volume_ratio'], x['score']), reverse=True)
            top_2 = breakouts[:2]
        
            if not top_2:
                await update.message.reply_text("📊 No intraday breakouts found right now. Market may be consolidating.")
                return
        
            msg = "⚡ **INTRADAY BREAKOUTS** ⚡\n"
            msg += "_Top 2 for day trading (5min-1hr holds)_\n\n"
        
            for i, stock in enumerate(top_2, 1):
                msg += f"**#{i}. {stock['ticker']}** - ${stock['price']:.2f}\n"
                msg += f"🔊 Volume: {stock['volume_ratio']:.1f}x average\n"
                msg += f"⭐ Score: {stock['score']}/12 | {stock['rating']}\n"
                msg += f"📍 Entry: ${stock['entry']:.2f}\n"
                msg += f"🛑 Stop: ${stock['stop']:.2f}\n"
                msg += f"🎯 Target: ${stock['target']:.2f}\n"
                msg += "="*40 + "\n\n"
        
            msg += "⚠️ _Intraday: Use tight stops. Exit before market close._"
        
            await update.message.reply_text(msg, parse_mode="Markdown")
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_weekly(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /weekly command - Top 2 breakouts for swing trading"""
        await update.message.reply_text("🔍 Scanning for WEEKLY breakouts (1-5 day swings)... (~40s)")
    
        try:
            from data_manager import DataManager
            from analyzer import Analyzer
        
            dm = DataManager()
            analyzer = Analyzer()
        
            scan_list = dm.get_comprehensive_stock_universe()
        
            breakouts = []
        
            for ticker in scan_list[:200]:  # Scan 200 stocks
                try:
                    df = dm.get_stock_history(ticker, period="3mo", interval="1d")
                    if df.empty or len(df) < 50:
                        continue
                
                    current_price = df['Close'].iloc[-1]
                    current_volume = df['Volume'].iloc[-1]
                    avg_volume_20 = df['Volume'].iloc[-21:-1].mean()
                    volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0
                
                    if volume_ratio >= 2.0:
                        high_20d = df['High'].iloc[-21:-1].max()
                        if current_price >= high_20d * 0.98:  # Within 2% of breakout
                            report = analyzer.generate_full_report(df)
                            if report and report['score'] >= 7:
                                sma_20 = df['Close'].iloc[-20:].mean()
                                above_sma = current_price > sma_20
                            
                                if above_sma:
                                    breakouts.append({
                                        'ticker': ticker,
                                        'price': current_price,
                                        'volume_ratio': volume_ratio,
                                        'score': report['score'],
                                        'entry': report['entry'],
                                        'stop': report['stop'],
                                        'target': report['target'],
                                        'rating': report['rating'],
                                        'risk_reward': report['risk_reward']
                                    })
                except:
                    continue
        
            breakouts.sort(key=lambda x: (x['score'], x['volume_ratio']), reverse=True)
            top_2 = breakouts[:2]
        
            if not top_2:
                await update.message.reply_text("📊 No weekly breakouts found. Waiting for better setups.")
                return
        
            msg = "📈 **WEEKLY SWING TRADES** 📈\n"
            msg += "_Top 2 for 1-5 day holds_\n\n"
        
            for i, stock in enumerate(top_2, 1):
                msg += f"**#{i}. {stock['ticker']}** - ${stock['price']:.2f}\n"
                msg += f"🔊 Volume: {stock['volume_ratio']:.1f}x average\n"
                msg += f"⭐ Score: {stock['score']}/12 | {stock['rating']}\n"
                msg += f"📍 Entry: ${stock['entry']:.2f}\n"
                msg += f"🛑 Stop: ${stock['stop']:.2f}\n"
                msg += f"🎯 Target: ${stock['target']:.2f}\n"
                msg += f"💰 R/R: 1:{stock['risk_reward']:.1f}\n"
                msg += "="*40 + "\n\n"
        
            msg += "⚠️ _Weekly: Hold 1-5 days. Trail stops as it moves._"
        
            await update.message.reply_text(msg, parse_mode="Markdown")
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_monthly(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /monthly command - Top 2 breakouts for position trading"""
        await update.message.reply_text("🔍 Scanning for MONTHLY breakouts (weeks-months holds)... (~50s)")
    
        try:
            from data_manager import DataManager
            from analyzer import Analyzer
        
            dm = DataManager()
            analyzer = Analyzer()
        
            sp500 = dm.get_sp500_tickers()
            if not sp500:
                sp500 = dm.get_comprehensive_stock_universe()
        
            breakouts = []
        
            for ticker in sp500[:300]:  # Scan 300 stocks
                try:
                    df = dm.get_stock_history(ticker, period="1y", interval="1d")
                    if df.empty or len(df) < 200:
                        continue
                
                    current_price = df['Close'].iloc[-1]
                    current_volume = df['Volume'].iloc[-1]
                    avg_volume_50 = df['Volume'].iloc[-51:-1].mean()
                    volume_ratio = current_volume / avg_volume_50 if avg_volume_50 > 0 else 0
                
                    if volume_ratio >= 1.5:
                        high_50d = df['High'].iloc[-51:-1].max()
                        high_200d = df['High'].iloc[-201:-1].max()
                    
                        sma_200 = df['Close'].iloc[-200:].mean()
                    
                        if current_price >= high_50d * 0.97 and current_price > sma_200:
                            report = analyzer.generate_full_report(df)
                            if report and report['score'] >= 8:  # Higher threshold for monthly
                                sma_50 = df['Close'].iloc[-50:].mean()
                                uptrend = sma_50 > sma_200
                            
                                if uptrend:
                                    breakouts.append({
                                        'ticker': ticker,
                                        'price': current_price,
                                        'volume_ratio': volume_ratio,
                                        'score': report['score'],
                                        'entry': report['entry'],
                                        'stop': report['stop'],
                                        'target': report['target'],
                                        'rating': report['rating'],
                                        'risk_reward': report['risk_reward']
                                    })
                except:
                    continue
        
            breakouts.sort(key=lambda x: x['score'], reverse=True)
            top_2 = breakouts[:2]
        
            if not top_2:
                await update.message.reply_text("📊 No monthly breakouts found. These are rare, high-quality setups.")
                return
        
            msg = "🚀 **MONTHLY POSITION TRADES** 🚀\n"
            msg += "_Top 2 for weeks-months holds_\n\n"
        
            for i, stock in enumerate(top_2, 1):
                msg += f"**#{i}. {stock['ticker']}** - ${stock['price']:.2f}\n"
                msg += f"🔊 Volume: {stock['volume_ratio']:.1f}x average\n"
                msg += f"⭐ Score: {stock['score']}/12 | {stock['rating']}\n"
                msg += f"📍 Entry: ${stock['entry']:.2f}\n"
                msg += f"🛑 Stop: ${stock['stop']:.2f}\n"
                msg += f"🎯 Target: ${stock['target']:.2f}\n"
                msg += f"💰 R/R: 1:{stock['risk_reward']:.1f}\n"
                msg += "="*40 + "\n\n"
        
            msg += "⚠️ _Monthly: Position trades. Use wider stops, trail profits._"
        
            await update.message.reply_text(msg, parse_mode="Markdown")
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def cmd_squeeze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /squeeze command - Squeeze breakout analysis"""
        
        # Check if ticker specified
        if context.args and len(context.args) > 0:
            # SPECIFIC TICKER ANALYSIS
            ticker = context.args[0].upper()
            await self._analyze_single_ticker_squeeze(update, context, ticker)
        else:
            # SCAN MARKET FOR SQUEEZES
            await self._scan_market_squeeze(update, context)
    
    async def _scan_market_squeeze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Scan market for stocks in squeeze or recently broken out"""
        await update.message.reply_text("🔍 Scanning for TTM Squeeze setups... (~40-60 seconds)")
        
        try:
            from data_manager import DataManager
            from analyzer import Analyzer
            
            dm = DataManager()
            analyzer = Analyzer()
            
            # Get comprehensive stock universe
            scan_list = dm.get_comprehensive_stock_universe()
            print(f"Scanning {len(scan_list)} stocks for squeeze patterns...")
            
            in_squeeze = []
            breakouts = []
            
            for ticker in scan_list:
                try:
                    df = dm.get_stock_history(ticker)
                    if df.empty or len(df) < 21:
                        continue
                    
                    # Check for squeeze breakout
                    is_breakout, direction, breakout_data = analyzer.check_squeeze_breakout(df)
                    
                    if is_breakout and breakout_data:
                        # Calculate trade plan
                        trade_plan = analyzer.calculate_trade_plan(df, "LONG" if direction == "bullish" else "SHORT")
                        
                        breakouts.append({
                            'ticker': ticker,
                            'direction': direction,
                            'data': breakout_data,
                            'trade_plan': trade_plan
                        })
                    else:
                        # Check if currently in squeeze
                        squeeze_status = analyzer.get_squeeze_status(df)
                        if squeeze_status and squeeze_status['is_squeezed']:
                            in_squeeze.append({
                                'ticker': ticker,
                                'status': squeeze_status
                            })
                except:
                    continue
            
            # Sort breakouts by volume ratio (strongest first)
            breakouts.sort(key=lambda x: x['data']['volume_ratio'], reverse=True)
            
            # Sort in_squeeze by squeeze duration (longest first - more explosive)
            in_squeeze.sort(key=lambda x: x['status']['squeeze_bars'], reverse=True)
            
            # Build message
            msg = "🔥 **TTM SQUEEZE ANALYSIS** 🔥\n\n"
            
            # Show breakouts first (most actionable)
            if breakouts:
                msg += "⚡ **RECENT BREAKOUTS** ⚡\n"
                msg += "_Squeeze has released - Trade NOW_\n\n"
                
                for i, b in enumerate(breakouts[:3], 1):  # Top 3 breakouts
                    ticker = b['ticker']
                    direction = b['direction']
                    data = b['data']
                    trade = b['trade_plan']
                    
                    emoji = "🐂" if direction == "bullish" else "🐻"
                    
                    msg += f"**{i}. {ticker}** {emoji} {direction.upper()}\n"
                    msg += f"Price: ${data['price']:.2f} ({data['price_change_pct']:+.1f}%)\n"
                    msg += f"Squeeze Duration: {data['squeeze_duration']} bars\n"
                    msg += f"Volume: {data['volume_ratio']:.1f}x avg\n"
                    
                    if trade:
                        msg += f"\n📊 TRADE SETUP:\n"
                        msg += f"Entry: ${trade['entry']:.2f}\n"
                        msg += f"Stop: ${trade['stop_loss']:.2f}\n"
                        msg += f"Target 1: ${trade['target_1']:.2f}\n"
                        msg += f"Target 2: ${trade['target_2']:.2f}\n"
                    
                    msg += "="*40 + "\n\n"
            else:
                msg += "⚡ **NO RECENT BREAKOUTS**\n"
                msg += "_No squeezes have fired yet_\n\n"
            
            # Show stocks in squeeze (coiling for breakout)
            if in_squeeze:
                msg += "🎯 **STOCKS IN SQUEEZE** 🎯\n"
                msg += "_Coiling for breakout - Watch closely_\n\n"
                
                for i, s in enumerate(in_squeeze[:5], 1):  # Top 5 in squeeze
                    ticker = s['ticker']
                    status = s['status']
                    
                    momentum_emoji = "🟢" if status['momentum'] == "bullish" else "🔴" if status['momentum'] == "bearish" else "⚪"
                    
                    msg += f"**{i}. {ticker}** {momentum_emoji}\n"
                    msg += f"Duration: {status['squeeze_bars']} bars\n"
                    msg += f"Momentum: {status['momentum'].upper()}\n"
                    msg += f"Expected Direction: {status['momentum'].title()}\n"
                    msg += "-"*30 + "\n\n"
            else:
                msg += "🎯 **NO STOCKS IN SQUEEZE**\n"
                msg += "_Market is expanded - wait for next setup_\n\n"
            
            msg += "\n💡 _TTM Squeeze: Bollinger Bands inside Keltner Channels_\n"
            msg += "⚠️ _Breakouts signal explosive moves - act fast!_"
            
            await update.message.reply_text(msg, parse_mode="Markdown")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error scanning for squeezes: {str(e)}")
    
    async def _analyze_single_ticker_squeeze(self, update: Update, context: ContextTypes.DEFAULT_TYPE, ticker: str):
        """Analyze squeeze status for a specific ticker"""
        await update.message.reply_text(f"🔍 Analyzing {ticker} for TTM Squeeze...")
        
        try:
            from data_manager import DataManager
            from analyzer import Analyzer
            
            dm = DataManager()
            analyzer = Analyzer()
            
            df = dm.get_stock_history(ticker)
            if df.empty:
                await update.message.reply_text(f"❌ Could not find data for {ticker}")
                return
            
            # Check for breakout
            is_breakout, direction, breakout_data = analyzer.check_squeeze_breakout(df)
            
            # Get current squeeze status
            squeeze_status = analyzer.get_squeeze_status(df)
            
            if not squeeze_status:
                await update.message.reply_text(f"❌ Not enough data to analyze {ticker}")
                return
            
            current_price = df['Close'].iloc[-1]
            
            msg = f"🔥 **{ticker} SQUEEZE ANALYSIS** 🔥\n\n"
            msg += f"**Current Price**: ${current_price:.2f}\n\n"
            
            # Show breakout if it just happened
            if is_breakout:
                emoji = "🐂" if direction == "bullish" else "🐻"
                msg += f"⚡ **BREAKOUT DETECTED!** ⚡\n"
                msg += f"**Direction**: {emoji} {direction.upper()}\n"
                msg += f"**Price Change**: {breakout_data['price_change_pct']:+.1f}%\n"
                msg += f"**Volume**: {breakout_data['volume_ratio']:.1f}x average\n"
                msg += f"**Squeeze Duration**: {breakout_data['squeeze_duration']} bars\n"
                msg += f"**Momentum**: {breakout_data['momentum'].upper()}\n\n"
                
                # Get trade plan
                trade_plan = analyzer.calculate_trade_plan(df, "LONG" if direction == "bullish" else "SHORT")
                
                if trade_plan:
                    msg += f"📊 **TRADE SETUP**:\n"
                    msg += f"Entry: ${trade_plan['entry']:.2f}\n"
                    msg += f"Stop Loss: ${trade_plan['stop_loss']:.2f}\n"
                    msg += f"Target 1: ${trade_plan['target_1']:.2f} (1.5R)\n"
                    msg += f"Target 2: ${trade_plan['target_2']:.2f} (3R)\n"
                    msg += f"Risk/Share: ${trade_plan['risk_per_share']:.2f}\n\n"
                
                msg += "🚨 **ACTION**: Trade NOW - Breakout in progress!\n"
                
            elif squeeze_status['is_squeezed']:
                momentum_emoji = "🟢" if squeeze_status['momentum'] == "bullish" else "🔴" if squeeze_status['momentum'] == "bearish" else "⚪"
                
                msg += f"🎯 **IN SQUEEZE** 🎯\n"
                msg += f"**Status**: COILING {momentum_emoji}\n"
                msg += f"**Duration**: {squeeze_status['squeeze_bars']} bars\n"
                msg += f"**Momentum**: {squeeze_status['momentum'].upper()}\n"
                msg += f"**Expected Direction**: {squeeze_status['momentum'].title()}\n\n"
                
                msg += f"**Technical Levels**:\n"
                msg += f"BB Upper: ${squeeze_status['squeeze_data']['bb_upper']:.2f}\n"
                msg += f"BB Lower: ${squeeze_status['squeeze_data']['bb_lower']:.2f}\n"
                msg += f"EMA 20: ${squeeze_status['squeeze_data']['ema20']:.2f}\n\n"
                
                msg += "⏳ **ACTION**: WAIT for breakout - Set alerts!\n"
                msg += f"Watch for price to break above ${squeeze_status['squeeze_data']['bb_upper']:.2f} (bullish)\n"
                msg += f"or below ${squeeze_status['squeeze_data']['bb_lower']:.2f} (bearish)\n"
                
            else:
                msg += "❌ **NOT IN SQUEEZE**\n"
                msg += "Bollinger Bands are outside Keltner Channels\n\n"
                msg += "⏳ **ACTION**: Wait for next squeeze setup\n"
            
            msg += "\n💡 _TTM Squeeze: High compression = Explosive breakout_"
            
            await update.message.reply_text(msg, parse_mode="Markdown")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error analyzing {ticker}: {str(e)}")

    async def cmd_fundamentals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /fundamentals command - Comprehensive fundamental analysis"""
        if not context.args or len(context.args) == 0:
            await update.message.reply_text("Usage: /fundamentals TICKER\nExample: /fundamentals AAPL")
            return
        
        ticker = context.args[0].upper()
        await update.message.reply_text(f"📊 Analyzing {ticker} fundamentals...")
        
        try:
            import requests
            from data_manager import DataManager
            from analyzer import Analyzer
            
            api_key = FMP_API_KEY
            dm = DataManager()
            analyzer = Analyzer()
            
            # Get stock data for volume analysis
            df = dm.get_stock_history(ticker, period="2y")
            
            # Fetch fundamental data from FMP
            # 1. Company Profile
            profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}"
            profile_resp = requests.get(profile_url, timeout=10)
            profile = profile_resp.json()
            
            if not profile or len(profile) == 0:
                await update.message.reply_text(f"❌ Could not find fundamental data for {ticker}")
                return
            
            company = profile[0]
            
            # 2. Key Metrics (TTM)
            metrics_url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={api_key}"
            metrics_resp = requests.get(metrics_url, timeout=10)
            metrics = metrics_resp.json()
            
            # 3. Financial Ratios (TTM)
            ratios_url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={api_key}"
            ratios_resp = requests.get(ratios_url, timeout=10)
            ratios = ratios_resp.json()
            
            # 4. Income Statement (Annual - for growth rates)
            income_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=5&apikey={api_key}"
            income_resp = requests.get(income_url, timeout=10)
            income_statements = income_resp.json()
            
            # Build comprehensive report
            msg = f"📊 **{ticker} FUNDAMENTAL ANALYSIS** 📊\n\n"
            msg += f"**{company.get('companyName', ticker)}**\n"
            msg += f"Sector: {company.get('sector', 'N/A')} | Industry: {company.get('industry', 'N/A')}\n"
            msg += f"Market Cap: ${company.get('mktCap', 0) / 1e9:.2f}B\n\n"
            
            # === VALUATION ===
            msg += "💰 **VALUATION**\n"
            current_price = company.get('price', 0)
            pe_ratio = company.get('pe', 0)
            forward_pe = metrics[0].get('peRatioTTM', 0) if metrics else 0
            pb_ratio = ratios[0].get('priceToBookRatioTTM', 0) if ratios else 0
            ps_ratio = ratios[0].get('priceToSalesRatioTTM', 0) if ratios else 0
            
            msg += f"Price: ${current_price:.2f}\n"
            msg += f"P/E Ratio: {pe_ratio:.2f}" + (" (Expensive)" if pe_ratio > 25 else " (Reasonable)" if pe_ratio > 15 else " (Cheap)") + "\n"
            if pb_ratio:
                msg += f"P/B Ratio: {pb_ratio:.2f}\n"
            if ps_ratio:
                msg += f"P/S Ratio: {ps_ratio:.2f}\n"
            msg += "\n"
            
            # === PROFITABILITY ===
            msg += "📈 **PROFITABILITY**\n"
            gross_margin = ratios[0].get('grossProfitMarginTTM', 0) * 100 if ratios else 0
            operating_margin = ratios[0].get('operatingProfitMarginTTM', 0) * 100 if ratios else 0
            net_margin = ratios[0].get('netProfitMarginTTM', 0) * 100 if ratios else 0
            roe = ratios[0].get('returnOnEquityTTM', 0) * 100 if ratios else 0
            roa = ratios[0].get('returnOnAssetsTTM', 0) * 100 if ratios else 0
            
            msg += f"Gross Margin: {gross_margin:.1f}%\n"
            msg += f"Operating Margin: {operating_margin:.1f}%\n"
            msg += f"Net Margin: {net_margin:.1f}%\n"
            msg += f"ROE: {roe:.1f}%\n"
            msg += f"ROA: {roa:.1f}%\n"
            msg += "\n"
            
            # === GROWTH ===
            msg += "🚀 **GROWTH (YoY)**\n"
            if income_statements and len(income_statements) >= 2:
                latest = income_statements[0]
                previous = income_statements[1]
                
                revenue_growth = ((latest.get('revenue', 0) - previous.get('revenue', 1)) / previous.get('revenue', 1)) * 100
                earnings_growth = ((latest.get('netIncome', 0) - previous.get('netIncome', 1)) / abs(previous.get('netIncome', 1))) * 100
                
                msg += f"Revenue Growth: {revenue_growth:+.1f}%\n"
                msg += f"Earnings Growth: {earnings_growth:+.1f}%\n"
                msg += f"Latest Revenue: ${latest.get('revenue', 0) / 1e9:.2f}B\n"
                msg += f"Latest Earnings: ${latest.get('netIncome', 0) / 1e9:.2f}B\n"
            else:
                msg += "Growth data not available\n"
            msg += "\n"
            
            # === FINANCIAL HEALTH ===
            msg += "💪 **FINANCIAL HEALTH**\n"
            debt_to_equity = ratios[0].get('debtEquityRatioTTM', 0) if ratios else 0
            current_ratio = ratios[0].get('currentRatioTTM', 0) if ratios else 0
            quick_ratio = ratios[0].get('quickRatioTTM', 0) if ratios else 0
            
            msg += f"Debt/Equity: {debt_to_equity:.2f}" + (" (High Debt)" if debt_to_equity > 2 else " (Moderate)" if debt_to_equity > 0.5 else " (Low Debt)") + "\n"
            msg += f"Current Ratio: {current_ratio:.2f}" + (" (Healthy)" if current_ratio > 1.5 else " (Watch)" if current_ratio > 1 else " (Weak)") + "\n"
            if quick_ratio:
                msg += f"Quick Ratio: {quick_ratio:.2f}\n"
            msg += "\n"
            
            # === VOLUME ANALYSIS ===
            if not df.empty:
                volume_history = analyzer.check_volume_vs_history(df, lookback_years=2)
                if volume_history:
                    msg += "📊 **VOLUME ANALYSIS (2 Years)**\n"
                    msg += f"Current Volume: {volume_history['current_volume']:,.0f}\n"
                    msg += f"Average Volume: {volume_history['avg_volume']:,.0f}\n"
                    
                    if volume_history['is_record']:
                        msg += "🔥 **RECORD HIGH VOLUME** (Highest in 2 years!)\n"
                    else:
                        msg += f"Percentile: {volume_history['percentile']:.0f}th"
                        if volume_history['percentile'] >= 95:
                            msg += " (Top 5% - Very High!)\n"
                        elif volume_history['percentile'] >= 80:
                            msg += " (Top 20% - High)\n"
                        else:
                            msg += "\n"
                    msg += "\n"
            
            # === DIVIDENDS ===
            dividend_yield = company.get('lastDiv', 0)
            if dividend_yield and dividend_yield > 0:
                msg += "💵 **DIVIDENDS**\n"
                msg += f"Dividend Yield: {dividend_yield:.2f}%\n"
                msg += "\n"
            
            # === SUMMARY ===
            msg += "📋 **SUMMARY**\n"
            
            # Quality score
            quality_score = 0
            if net_margin > 15:
                quality_score += 1
            if roe > 15:
                quality_score += 1
            if revenue_growth > 10 if 'revenue_growth' in locals() else False:
                quality_score += 1
            if debt_to_equity < 1:
                quality_score += 1
            if current_ratio > 1.5:
                quality_score += 1
            
            if quality_score >= 4:
                msg += "✅ **Strong Fundamentals** (4-5/5)\n"
            elif quality_score >= 3:
                msg += "⚖️ **Decent Fundamentals** (3/5)\n"
            else:
                msg += "⚠️ **Weak Fundamentals** (0-2/5)\n"
            
            msg += f"\n💡 _Data from FMP API - Use with technical analysis for best results_"
            
            await update.message.reply_text(msg, parse_mode="Markdown")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching fundamentals: {str(e)}")


    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ticker = update.message.text.upper().strip()
        
        # Basic validation (Allow letters, numbers, dots, dashes)
        # e.g. AAPL, BRK.B, BTC-USD, 1234.HK
        import re
        if not re.match(r'^[A-Z0-9.-]+$', ticker) or len(ticker) > 10:
            await update.message.reply_text("Please send a valid ticker symbol (e.g., AAPL, BTC-USD).")
            return
            
        await update.message.reply_text(f"Analyzing {ticker}... 🔍")
        
        # Run analysis
        # Importing here to avoid circular imports at module level if any
        from data_manager import DataManager
        from analyzer import Analyzer
        
        dm = DataManager()
        analyzer = Analyzer()
        
        try:
            df = dm.get_stock_history(ticker)
            if df.empty:
                await update.message.reply_text(f"Could not find data for {ticker}. Check the symbol.")
                return
                
            report = analyzer.generate_full_report(df)
            if not report:
                print(f"Analysis failed for {ticker}. Rows: {len(df)}")
                await update.message.reply_text(f"Not enough data to analyze {ticker}. (Found {len(df)} days)")
                return
                
            # Format the response
            msg = f"📊 **{ticker} Analysis** (Expert Level)\n"
            msg += f"Price: ${report['price']:.2f}\n\n"
            msg += f"**RATING: {report['rating']}** (Score: {report['score']}/12)\n\n"
            msg += f"**Trade Plan:**\n"
            msg += f"Entry: ${report['entry']:.2f}\n"
            msg += f"Stop: ${report['stop']:.2f}\n"
            msg += f"Target: ${report['target']:.2f}\n"
            msg += f"R/R: 1:{report['risk_reward']:.1f}\n\n"
            msg += "**Key Signals:**\n"
            for reason in report['reasons'][:5]:  # Top 5 reasons
                msg += f"{reason}\n"
                
            msg += "\n_Expert multi-timeframe analysis. Not financial advice._"
            
            await update.message.reply_text(msg, parse_mode="Markdown")
            
        except Exception as e:
            await update.message.reply_text(f"Error analyzing {ticker}: {str(e)}")

    async def cmd_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command - View paper trading positions"""
        user_id = update.effective_chat.id
        portfolio = self.user_manager.get_user_portfolio(user_id)
        
        if not portfolio:
            msg = "📉 **Your Paper Portfolio is Empty**\n\n"
            msg += "Use `/buy TICKER PRICE QTY` to add a paper trade.\n"
            msg += "Example: `/buy AAPL 150.50 10`"
            await update.message.reply_text(msg, parse_mode="Markdown")
            return
            
        msg = "💼 **YOUR PAPER PORTFOLIO** 💼\n\n"
        total_value = 0
        
        for pos in portfolio:
            ticker = pos['ticker']
            entry = pos['entry_price']
            qty = pos['quantity']
            value = entry * qty
            total_value += value
            
            msg += f"**{ticker}**: {qty} shares @ ${entry:.2f}\n"
            msg += f"   Value: ${value:,.2f}\n"
            if pos['target_price']:
                msg += f"   Target: ${pos['target_price']:.2f} | Stop: ${pos['stop_loss']:.2f}\n"
            msg += "-------------------\n"
            
        msg += f"\n💰 **Total Invested**: ${total_value:,.2f}"
        
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def cmd_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /buy command for paper trading"""
        # Usage: /buy TICKER PRICE QTY [TARGET] [STOP]
        try:
            args = context.args
            if len(args) < 3:
                await update.message.reply_text("Usage: `/buy TICKER PRICE QTY`\nExample: `/buy AAPL 150.00 10`", parse_mode="Markdown")
                return
                
            ticker = args[0].upper()
            price = float(args[1])
            qty = float(args[2])
            
            target = float(args[3]) if len(args) > 3 else None
            stop = float(args[4]) if len(args) > 4 else None
            
            success = self.user_manager.add_paper_trade(update.effective_chat.id, ticker, price, qty, target, stop)
            
            if success:
                msg = f"✅ **Paper Trade Added!**\n\n"
                msg += f"Bought {qty} {ticker} @ ${price:.2f}\n"
                msg += f"Total: ${price * qty:,.2f}"
                await update.message.reply_text(msg, parse_mode="Markdown")
            else:
                await update.message.reply_text("❌ Failed to add trade. Please try again.")
                
        except ValueError:
            await update.message.reply_text("❌ Invalid format. Price and Qty must be numbers.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def send_alert(self, chat_id, message):
        await self.app.bot.send_message(chat_id=chat_id, text=message)

    def send_alert_sync(self, chat_id, message):
        """
        Broadcasts a message to ALL subscribed users.
        Ignores the 'chat_id' argument (kept for compatibility) and fetches active users from DB.
        """
        subscribers = self.user_manager.get_subscribers()
        
        if not subscribers:
            print("No subscribers found to broadcast message.")
            return

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
        # Split message into chunks
        chunk_size = 4000
        chunks = [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]
        
        print(f"Broadcasting to {len(subscribers)} users...")
        
        for user_id in subscribers:
            for chunk in chunks:
                data = {
                    "chat_id": user_id,
                    "text": chunk,
                    "parse_mode": "Markdown"
                }
                try:
                    response = requests.post(url, data=data)
                    if response.status_code != 200:
                        print(f"Failed to send to {user_id}: {response.text}")
                except Exception as e:
                    print(f"Error sending to {user_id}: {e}")

    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown commands by showing available commands"""
        msg = "❌ **Unknown Command**\n\n"
        msg += "Here are the commands I understand:\n"
        msg += "📉 **Trading**\n"
        msg += "/buy TICKER PRICE QTY - Paper trade\n"
        msg += "/portfolio - View positions\n\n"
        msg += "🧠 **Analysis**\n"
        msg += "/picks - Top 2 expert picks\n"
        msg += "/options TICKER - Best option contract\n"
        msg += "/whales - Insider buys >$100k\n"
        msg += "/volume - Bullish & bearish volume\n"
        msg += "/chart TICKER - Technical chart\n"
        msg += "/index - Market overview\n\n"
        msg += "Or just send me a ticker symbol (e.g. AAPL)!"
        
        await update.message.reply_text(msg, parse_mode="Markdown")


    def run(self):
        print("Bot is running...")
        print("Commands available: /start, /index, /picks, /options, /whales")
        print("Or send any ticker symbol for instant analysis!")

        self.app.run_polling()

    async def cmd_intraday(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /intraday command - Top 2 breakouts for day trading"""
        await update.message.reply_text(" Scanning for INTRADAY breakouts (5min-1hr holds)... (~30s)")
        
        try:
            from data_manager import DataManager
            from analyzer import Analyzer
            
            dm = DataManager()
            analyzer = Analyzer()
            
            # Scan most active stocks for intraday momentum
            actives = dm.get_most_active()
            if not actives:
                actives = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "AMD", "MSFT", "META", "AMZN"]
            
            breakouts = []
            
            for ticker in actives[:50]:  # Scan top 50 most active
                try:
                    df = dm.get_stock_history(ticker, period="5d", interval="1d")
                    if df.empty or len(df) < 5:
                        continue
                    
                    current_price = df['Close'].iloc[-1]
                    current_volume = df['Volume'].iloc[-1]
                    avg_volume = df['Volume'].iloc[-5:-1].mean()
                    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                    
                    # Intraday criteria: 3x+ volume + near highs
                    if volume_ratio >= 3.0:
                        high_5d = df['High'].iloc[-5:].max()
                        distance_from_high = ((current_price - high_5d) / high_5d) * 100
                        
                        # Must be within 2% of 5-day high
                        if distance_from_high >= -2.0:
                            report = analyzer.generate_full_report(df)
                            if report and report['score'] >= 6:
                                breakouts.append({
                                    'ticker': ticker,
                                    'price': current_price,
                                    'volume_ratio': volume_ratio,
                                    'score': report['score'],
                                    'entry': report['entry'],
                                    'stop': report['stop'],
                                    'target': report['target'],
                                    'rating': report['rating']
                                })
                except:
                    continue
            
            # Sort by volume ratio and score
            breakouts.sort(key=lambda x: (x['volume_ratio'], x['score']), reverse=True)
            top_2 = breakouts[:2]
            
            if not top_2:
                await update.message.reply_text(" No intraday breakouts found right now. Market may be consolidating.")
                return
            
            msg = " **INTRADAY BREAKOUTS** \n"
            msg += "_Top 2 for day trading (5min-1hr holds)_\n\n"
            
            for i, stock in enumerate(top_2, 1):
                msg += f"**#{i}. {stock['ticker']}** - ${stock['price']:.2f}\n"
                msg += f" Volume: {stock['volume_ratio']:.1f}x average\n"
                msg += f" Score: {stock['score']}/12 | {stock['rating']}\n"
                msg += f" Entry: ${stock['entry']:.2f}\n"
                msg += f" Stop: ${stock['stop']:.2f}\n"
                msg += f" Target: ${stock['target']:.2f}\n"
                msg += "="*40 + "\n\n"
            
            msg += " _Intraday: Use tight stops. Exit before market close._"
            
            await update.message.reply_text(msg, parse_mode="Markdown")
            
        except Exception as e:
            await update.message.reply_text(f" Error: {str(e)}")
# Add these three methods to the StockBot class in bot.py
# Insert them after the cmd_chart method (around line 773)

async def cmd_intraday(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /intraday command - Top 2 breakouts for day trading"""
    await update.message.reply_text("🔍 Scanning for INTRADAY breakouts (5min-1hr holds)... (~30s)")
    
    try:
        from data_manager import DataManager
        from analyzer import Analyzer
        
        dm = DataManager()
        analyzer = Analyzer()
        
        # Scan most active stocks for intraday momentum
        actives = dm.get_most_active()
        if not actives:
            actives = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "AMD", "MSFT", "META", "AMZN"]
        
        breakouts = []
        
        for ticker in actives[:50]:  # Scan top 50 most active
            try:
                df = dm.get_stock_history(ticker, period="5d", interval="1d")
                if df.empty or len(df) < 5:
                    continue
                
                current_price = df['Close'].iloc[-1]
                current_volume = df['Volume'].iloc[-1]
                avg_volume = df['Volume'].iloc[-5:-1].mean()
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                
                # Intraday criteria: 3x+ volume + near highs
                if volume_ratio >= 3.0:
                    high_5d = df['High'].iloc[-5:].max()
                    distance_from_high = ((current_price - high_5d) / high_5d) * 100
                    
                    # Must be within 2% of 5-day high
                    if distance_from_high >= -2.0:
                        report = analyzer.generate_full_report(df)
                        if report and report['score'] >= 6:
                            breakouts.append({
                                'ticker': ticker,
                                'price': current_price,
                                'volume_ratio': volume_ratio,
                                'score': report['score'],
                                'entry': report['entry'],
                                'stop': report['stop'],
                                'target': report['target'],
                                'rating': report['rating']
                            })
            except:
                continue
        
        # Sort by volume ratio and score
        breakouts.sort(key=lambda x: (x['volume_ratio'], x['score']), reverse=True)
        top_2 = breakouts[:2]
        
        if not top_2:
            await update.message.reply_text("📊 No intraday breakouts found right now. Market may be consolidating.")
            return
        
        msg = "⚡ **INTRADAY BREAKOUTS** ⚡\n"
        msg += "_Top 2 for day trading (5min-1hr holds)_\n\n"
        
        for i, stock in enumerate(top_2, 1):
            msg += f"**#{i}. {stock['ticker']}** - ${stock['price']:.2f}\n"
            msg += f"🔊 Volume: {stock['volume_ratio']:.1f}x average\n"
            msg += f"⭐ Score: {stock['score']}/12 | {stock['rating']}\n"
            msg += f"📍 Entry: ${stock['entry']:.2f}\n"
            msg += f"🛑 Stop: ${stock['stop']:.2f}\n"
            msg += f"🎯 Target: ${stock['target']:.2f}\n"
            msg += "="*40 + "\n\n"
        
        msg += "⚠️ _Intraday: Use tight stops. Exit before market close._"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def cmd_weekly(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /weekly command - Top 2 breakouts for swing trading"""
    await update.message.reply_text("🔍 Scanning for WEEKLY breakouts (1-5 day swings)... (~40s)")
    
    try:
        from data_manager import DataManager
        from analyzer import Analyzer
        
        dm = DataManager()
        analyzer = Analyzer()
        
        # Scan comprehensive universe for weekly setups
        scan_list = dm.get_comprehensive_stock_universe()
        
        breakouts = []
        
        for ticker in scan_list[:200]:  # Scan 200 stocks
            try:
                df = dm.get_stock_history(ticker, period="3mo", interval="1d")
                if df.empty or len(df) < 50:
                    continue
                
                current_price = df['Close'].iloc[-1]
                current_volume = df['Volume'].iloc[-1]
                avg_volume_20 = df['Volume'].iloc[-21:-1].mean()
                volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0
                
                # Weekly criteria: 2x+ volume + breakout from consolidation
                if volume_ratio >= 2.0:
                    # Check if breaking 20-day high
                    high_20d = df['High'].iloc[-21:-1].max()
                    if current_price >= high_20d * 0.98:  # Within 2% of breakout
                        report = analyzer.generate_full_report(df)
                        if report and report['score'] >= 7:
                            # Calculate 20-day SMA for trend confirmation
                            sma_20 = df['Close'].iloc[-20:].mean()
                            above_sma = current_price > sma_20
                            
                            if above_sma:
                                breakouts.append({
                                    'ticker': ticker,
                                    'price': current_price,
                                    'volume_ratio': volume_ratio,
                                    'score': report['score'],
                                    'entry': report['entry'],
                                    'stop': report['stop'],
                                    'target': report['target'],
                                    'rating': report['rating'],
                                    'risk_reward': report['risk_reward']
                                })
            except:
                continue
        
        # Sort by score and volume
        breakouts.sort(key=lambda x: (x['score'], x['volume_ratio']), reverse=True)
        top_2 = breakouts[:2]
        
        if not top_2:
            await update.message.reply_text("📊 No weekly breakouts found. Waiting for better setups.")
            return
        
        msg = "📈 **WEEKLY SWING TRADES** 📈\n"
        msg += "_Top 2 for 1-5 day holds_\n\n"
        
        for i, stock in enumerate(top_2, 1):
            msg += f"**#{i}. {stock['ticker']}** - ${stock['price']:.2f}\n"
            msg += f"🔊 Volume: {stock['volume_ratio']:.1f}x average\n"
            msg += f"⭐ Score: {stock['score']}/12 | {stock['rating']}\n"
            msg += f"📍 Entry: ${stock['entry']:.2f}\n"
            msg += f"🛑 Stop: ${stock['stop']:.2f}\n"
            msg += f"🎯 Target: ${stock['target']:.2f}\n"
            msg += f"💰 R/R: 1:{stock['risk_reward']:.1f}\n"
            msg += "="*40 + "\n\n"
        
        msg += "⚠️ _Weekly: Hold 1-5 days. Trail stops as it moves._"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def cmd_monthly(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /monthly command - Top 2 breakouts for position trading"""
    await update.message.reply_text("🔍 Scanning for MONTHLY breakouts (weeks-months holds)... (~50s)")
    
    try:
        from data_manager import DataManager
        from analyzer import Analyzer
        
        dm = DataManager()
        analyzer = Analyzer()
        
        # Scan S&P 500 for monthly position trades
        sp500 = dm.get_sp500_tickers()
        if not sp500:
            sp500 = dm.get_comprehensive_stock_universe()
        
        breakouts = []
        
        for ticker in sp500[:300]:  # Scan 300 stocks
            try:
                df = dm.get_stock_history(ticker, period="1y", interval="1d")
                if df.empty or len(df) < 200:
                    continue
                
                current_price = df['Close'].iloc[-1]
                current_volume = df['Volume'].iloc[-1]
                avg_volume_50 = df['Volume'].iloc[-51:-1].mean()
                volume_ratio = current_volume / avg_volume_50 if avg_volume_50 > 0 else 0
                
                # Monthly criteria: 1.5x+ volume + breaking 52-week consolidation
                if volume_ratio >= 1.5:
                    # Check if breaking 50-day high
                    high_50d = df['High'].iloc[-51:-1].max()
                    high_200d = df['High'].iloc[-201:-1].max()
                    
                    # Must be near 50-day high and above 200-day SMA
                    sma_200 = df['Close'].iloc[-200:].mean()
                    
                    if current_price >= high_50d * 0.97 and current_price > sma_200:
                        report = analyzer.generate_full_report(df)
                        if report and report['score'] >= 8:  # Higher threshold for monthly
                            # Check for strong uptrend (50 SMA > 200 SMA)
                            sma_50 = df['Close'].iloc[-50:].mean()
                            uptrend = sma_50 > sma_200
                            
                            if uptrend:
                                breakouts.append({
                                    'ticker': ticker,
                                    'price': current_price,
                                    'volume_ratio': volume_ratio,
                                    'score': report['score'],
                                    'entry': report['entry'],
                                    'stop': report['stop'],
                                    'target': report['target'],
                                    'rating': report['rating'],
                                    'risk_reward': report['risk_reward']
                                })
            except:
                continue
        
        # Sort by score (quality over volume for monthly)
        breakouts.sort(key=lambda x: x['score'], reverse=True)
        top_2 = breakouts[:2]
        
        if not top_2:
            await update.message.reply_text("📊 No monthly breakouts found. These are rare, high-quality setups.")
            return
        
        msg = "🚀 **MONTHLY POSITION TRADES** 🚀\n"
        msg += "_Top 2 for weeks-months holds_\n\n"
        
        for i, stock in enumerate(top_2, 1):
            msg += f"**#{i}. {stock['ticker']}** - ${stock['price']:.2f}\n"
            msg += f"🔊 Volume: {stock['volume_ratio']:.1f}x average\n"
            msg += f"⭐ Score: {stock['score']}/12 | {stock['rating']}\n"
            msg += f"📍 Entry: ${stock['entry']:.2f}\n"
            msg += f"🛑 Stop: ${stock['stop']:.2f}\n"
            msg += f"🎯 Target: ${stock['target']:.2f}\n"
            msg += f"💰 R/R: 1:{stock['risk_reward']:.1f}\n"
            msg += "="*40 + "\n\n"
        
        msg += "⚠️ _Monthly: Position trades. Use wider stops, trail profits._"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
