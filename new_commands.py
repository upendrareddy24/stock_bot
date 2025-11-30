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
