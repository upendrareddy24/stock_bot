"""
Professional Market Index Analyzer
Analyzes major market indices with 75 years of experience methodology
Provides 0-10 rating scale for easy decision making
"""

from data_manager import DataManager

class IndexAnalyzer:
    """
    Professional Market Index Analysis
    Rating Scale: 0-10 (Easy to understand)
    - 9-10: EXTREME BULLISH 🟢🟢🟢 (Strong Buy Zone)
    - 7-8: BULLISH 🟢🟢 (Buy Zone)
    - 5-6: NEUTRAL 🟡 (Wait and Watch)
    - 3-4: BEARISH 🔴 (Caution)
    - 0-2: EXTREME BEARISH 🔴🔴 (Avoid/Cash)
    """
    
    INDICES = {
        # Major Market Indices
        'SPY': 'S&P 500',
        'QQQ': 'Nasdaq',
        'DIA': 'Dow Jones',
        'IWM': 'Russell 2000',
        
        # Commodities & Metals
        'GLD': 'Gold',
        'SLV': 'Silver',
        'USO': 'Oil',
        
        # Crypto
        'BTC-USD': 'Bitcoin',
        'ETH-USD': 'Ethereum',
        
        # Sector ETFs
        'XLK': 'Technology',
        'XLF': 'Financials',
        'XLE': 'Energy',
        'XLV': 'Healthcare',
        'XLI': 'Industrials',
        'XLP': 'Consumer Staples',
        'XLY': 'Consumer Discretionary',
        'XLU': 'Utilities',
        'SMH': 'Semiconductors',
        'VNQ': 'Real Estate'
    }
    
    def __init__(self):
        self.cache = {}
        self.dm = DataManager()
    
    def fetch_index_data(self, symbol, period='2y'):
        """Fetch historical data for index using DataManager (FMP -> Yahoo Fallback)"""
        try:
            # DataManager handles the fallback logic and API keys
            # We request 2y to ensure we have enough for 52-week high/low + Moving Averages
            df = self.dm.get_stock_history(symbol, period=period)
            return df
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()
    
    def analyze_index(self, symbol):
        """
        Professional Multi-Factor Index Analysis
        Based on 75 years of market wisdom
        """
        df = self.fetch_index_data(symbol)
        
        if df.empty or len(df) < 50:
            return None
        
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        current_price = close.iloc[-1]
        
        score = 0
        factors = []
        
        # ========== FACTOR 1: TREND ANALYSIS (3 points) ==========
        sma20 = close.rolling(window=20).mean().iloc[-1]
        sma50 = close.rolling(window=50).mean().iloc[-1]
        ema12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        
        # Strong uptrend: Price > EMA12 > EMA26 > SMA20 > SMA50
        if current_price > ema12 > ema26:
            score += 2
            factors.append("Strong Uptrend")
        elif current_price > sma20 > sma50:
            score += 1
            factors.append("Uptrend")
        elif current_price < sma50:
            score -= 1
            factors.append("Downtrend")
        else:
            factors.append("Sideways")
        
        # ========== FACTOR 2: MOMENTUM (2 points) ==========
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        if 50 < current_rsi < 70:
            score += 2
            factors.append(f"Bullish Momentum (RSI: {current_rsi:.0f})")
        elif current_rsi > 70:
            score += 1
            factors.append(f"Overbought (RSI: {current_rsi:.0f})")
        elif current_rsi < 30:
            score -= 1
            factors.append(f"Oversold (RSI: {current_rsi:.0f})")
        else:
            factors.append(f"Neutral (RSI: {current_rsi:.0f})")
        
        # ========== FACTOR 3: MACD (1 point) ==========
        macd_line = ema12 - ema26
        signal_line = close.ewm(span=9, adjust=False).mean().iloc[-1]
        
        if macd_line > 0:
            score += 1
            factors.append("MACD Bullish")
        else:
            factors.append("MACD Bearish")
        
        # ========== FACTOR 4: PRICE POSITION (2 points) ==========
        # Distance from 52-week high/low
        year_high = high.rolling(window=252, min_periods=1).max().iloc[-1]
        year_low = low.rolling(window=252, min_periods=1).min().iloc[-1]
        price_range = year_high - year_low
        position = (current_price - year_low) / price_range if price_range > 0 else 0.5
        
        if position > 0.75:
            score += 2
            factors.append(f"Near Highs ({position*100:.0f}% of range)")
        elif position > 0.50:
            score += 1
            factors.append(f"Mid Range ({position*100:.0f}%)")
        elif position < 0.25:
            score -= 1
            factors.append(f"Near Lows ({position*100:.0f}%)")
        else:
            factors.append(f"Lower Range ({position*100:.0f}%)")
        
        # ========== FACTOR 5: VOLATILITY & VOLUME (1 point) ==========
        avg_volume = volume.iloc[-20:].mean()
        recent_volume = volume.iloc[-5:].mean()
        volume_trend = recent_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_trend > 1.2:
            score += 1
            factors.append(f"High Volume ({volume_trend:.1f}x)")
        elif volume_trend < 0.8:
            factors.append(f"Low Volume ({volume_trend:.1f}x)")
        else:
            factors.append(f"Normal Volume")
        
        # ========== FACTOR 6: RECENT PERFORMANCE (1 point) ==========
        week_ago = close.iloc[-5]
        week_change = ((current_price - week_ago) / week_ago) * 100
        
        if week_change > 2:
            score += 1
            factors.append(f"Strong Week (+{week_change:.1f}%)")
        elif week_change < -2:
            score -= 1
            factors.append(f"Weak Week ({week_change:.1f}%)")
        else:
            factors.append(f"Week: {week_change:+.1f}%")
        
        # Normalize score to 0-10 scale
        raw_score = score
        normalized_score = max(0, min(10, 5 + score))  # Center at 5, range 0-10
        
        # Determine Rating
        if normalized_score >= 9:
            rating = "EXTREME BULLISH 🟢🟢🟢"
            action = "STRONG BUY ZONE - Deploy capital aggressively"
        elif normalized_score >= 7:
            rating = "BULLISH 🟢🟢"
            action = "BUY ZONE - Good risk/reward"
        elif normalized_score >= 5:
            rating = "NEUTRAL 🟡"
            action = "WAIT - No clear edge"
        elif normalized_score >= 3:
            rating = "BEARISH 🔴"
            action = "CAUTION - Reduce exposure"
        else:
            rating = "EXTREME BEARISH 🔴🔴"
            action = "AVOID - Move to cash/defensive"
        
        return {
            'symbol': symbol,
            'name': self.INDICES.get(symbol, symbol),
            'price': current_price,
            'score': normalized_score,
            'rating': rating,
            'action': action,
            'factors': factors,
            'trend': factors[0] if factors else 'Unknown',
            'week_change': week_change,
            'position_in_range': position * 100
        }
    
    def generate_market_report(self):
        """
        Generate comprehensive market report for all major indices
        Returns formatted report ready for Telegram
        """
        print("Generating Professional Market Analysis...")
        
        results = []
        for symbol in self.INDICES.keys():
            print(f"Analyzing {symbol}...")
            analysis = self.analyze_index(symbol)
            if analysis:
                results.append(analysis)
        
        if not results:
            return "❌ Unable to generate market report. Please try again later."
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Build report
        now = datetime.now()
        market_status = "AFTER CLOSE" if now.hour >= 16 else "BEFORE OPEN"
        
        report = f"📊 **PROFESSIONAL MARKET ANALYSIS** 📊\n"
        report += f"🕐 {now.strftime('%B %d, %Y at %I:%M %p ET')}\n"
        report += f"📍 Market Status: {market_status}\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Market Overview Summary
        avg_score = sum(r['score'] for r in results) / len(results)
        bullish_count = sum(1 for r in results if r['score'] >= 7)
        bearish_count = sum(1 for r in results if r['score'] < 5)
        
        if avg_score >= 7:
            market_bias = "🟢 BULLISH MARKET - Good environment for longs"
        elif avg_score >= 5:
            market_bias = "🟡 MIXED MARKET - Stock picking environment"
        else:
            market_bias = "🔴 BEARISH MARKET - Defensive positioning"
        
        report += f"**MARKET SENTIMENT**: {market_bias}\n"
        report += f"**Overall Score**: {avg_score:.1f}/10\n"
        report += f"**Bullish Sectors**: {bullish_count} | **Bearish**: {bearish_count}\n"
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Individual Index Analysis
        report += "**INDEX RATINGS** (0-10 Scale):\n\n"
        
        for r in results:
            emoji = "🟢" if r['score'] >= 7 else "🟡" if r['score'] >= 5 else "🔴"
            report += f"{emoji} **{r['symbol']}** ({r['name']})\n"
            report += f"   Score: **{r['score']:.1f}/10** | Price: ${r['price']:.2f}\n"
            report += f"   Rating: {r['rating']}\n"
            report += f"   Week: {r['week_change']:+.1f}% | Position: {r['position_in_range']:.0f}%\n"
            report += f"   _Action: {r['action']}_\n\n"
        
        # Top 3 Strongest Indices
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        report += "**🏆 STRONGEST INDICES TODAY**:\n"
        for i, r in enumerate(results[:3], 1):
            report += f"{i}. {r['symbol']} ({r['score']:.1f}/10) - {r['rating']}\n"
        
        # Professional Trading Advice
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        report += "**💡 PROFESSIONAL GUIDANCE**:\n\n"
        
        if avg_score >= 7:
            report += "• Market showing strength - favor setups in leading indices\n"
            report += "• Look for breakouts in high-scoring sectors\n"
            report += "• Manage stops aggressively to protect gains\n"
        elif avg_score >= 5:
            report += "• Mixed market - be selective with entries\n"
            report += "• Focus on relative strength plays\n"
            report += "• Tighter stops recommended\n"
        else:
            report += "• Defensive posture warranted\n"
            report += "• Preserve capital - cash is a position\n"
            report += "• Wait for better risk/reward setups\n"
        
        report += "\n_Analysis based on 75 years of market experience methodology_\n"
        report += "_Including: Trend, Momentum, Volume, Price Position, MACD_"
        
        return report


if __name__ == "__main__":
    analyzer = IndexAnalyzer()
    report = analyzer.generate_market_report()
    print("\n" + "="*60)
    print(report)
    print("="*60)
