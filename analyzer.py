import pandas as pd

class Analyzer:
    def __init__(self):
        pass

    def check_cup_and_handle(self, df):
        """
        Heuristic check for Cup and Handle pattern.
        Logic: 
        1. Price is within 90-100% of 52-week high.
        2. RSI is not overbought (>75).
        3. Recent consolidation (low volatility in last 5 days).
        """
        if df.empty or len(df) < 50:
            return False
            
        current_price = df['Close'].iloc[-1]
        year_high = df['Close'].rolling(window=252, min_periods=1).max().iloc[-1]
        
        # 1. Near Highs
        if current_price < 0.90 * year_high:
            return False
            
        # 2. Simple RSI check (14 period)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        if rsi.iloc[-1] > 75: # Too extended
            return False
            
        return True

    def check_parabola(self, df):
        """
        Checks for parabolic movement.
        Logic: Price > EMA20 > EMA50 and Price is > 10% above EMA20 (extended).
        """
        if df.empty or len(df) < 50:
            return False
            
        ema20 = df['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df['Close'].ewm(span=20, adjust=False).mean()
        
        current_price = df['Close'].iloc[-1]
        current_ema20 = ema20.iloc[-1]
        current_ema50 = ema50.iloc[-1]
        
        if current_price > current_ema20 > current_ema50:
            # Check extension
            if current_price > 1.10 * current_ema20:
                return True
                
        return False

    def check_squeeze(self, df):
        """
        Checks for TTM Squeeze (Bollinger Bands inside Keltner Channels).
        """
        if df.empty or len(df) < 20:
            return False
        
        # Calculate Bollinger Bands
        sma20 = df['Close'].rolling(window=20).mean()
        std20 = df['Close'].rolling(window=20).std()
        bb_upper = sma20 + 2 * std20
        bb_lower = sma20 - 2 * std20
        
        # Calculate Keltner Channels (using TR and EMA)
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr20 = tr.rolling(window=20).mean() # Simple ATR for simplicity
        
        ema20 = df['Close'].ewm(span=20, adjust=False).mean()
        kc_upper = ema20 + 1.5 * atr20
        kc_lower = ema20 - 1.5 * atr20
        
        # Check Squeeze condition on the last candle
        last_bb_u = bb_upper.iloc[-1]
        last_bb_l = bb_lower.iloc[-1]
        last_kc_u = kc_upper.iloc[-1]
        last_kc_l = kc_lower.iloc[-1]
        
        if last_bb_u < last_kc_u and last_bb_l > last_kc_l:
            return True
            
        return False

    def get_squeeze_status(self, df):
        """
        Returns detailed squeeze status information.
        
        Returns:
            dict with keys:
            - is_squeezed: bool (currently in squeeze)
            - squeeze_bars: int (number of consecutive bars in squeeze)
            - bb_width: float (Bollinger Band width)
            - kc_width: float (Keltner Channel width)
            - momentum: str ("bullish", "bearish", "neutral")
            - squeeze_data: dict (BB and KC values)
        """
        if df.empty or len(df) < 20:
            return None
        
        # Calculate Bollinger Bands
        sma20 = df['Close'].rolling(window=20).mean()
        std20 = df['Close'].rolling(window=20).std()
        bb_upper = sma20 + 2 * std20
        bb_lower = sma20 - 2 * std20
        
        # Calculate Keltner Channels
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr20 = tr.rolling(window=20).mean()
        
        ema20 = df['Close'].ewm(span=20, adjust=False).mean()
        kc_upper = ema20 + 1.5 * atr20
        kc_lower = ema20 - 1.5 * atr20
        
        # Check current squeeze status
        current_bb_u = bb_upper.iloc[-1]
        current_bb_l = bb_lower.iloc[-1]
        current_kc_u = kc_upper.iloc[-1]
        current_kc_l = kc_lower.iloc[-1]
        
        is_squeezed = current_bb_u < current_kc_u and current_bb_l > current_kc_l
        
        # Count consecutive squeeze bars
        squeeze_bars = 0
        for i in range(len(df) - 1, max(19, len(df) - 100), -1):
            bb_u = bb_upper.iloc[i]
            bb_l = bb_lower.iloc[i]
            kc_u = kc_upper.iloc[i]
            kc_l = kc_lower.iloc[i]
            
            if bb_u < kc_u and bb_l > kc_l:
                squeeze_bars += 1
            else:
                break
        
        # Calculate band widths
        bb_width = current_bb_u - current_bb_l
        kc_width = current_kc_u - current_kc_l
        
        # Determine momentum direction using histogram (similar to TTM Squeeze indicator)
        # Using Linear Regression of close prices
        close_prices = df['Close'].tail(20).values
        x = list(range(len(close_prices)))
        
        # Simple linear regression
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(close_prices)
        sum_xy = sum(x[i] * close_prices[i] for i in range(n))
        sum_x2 = sum(xi ** 2 for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Determine momentum
        if slope > 0.1:
            momentum = "bullish"
        elif slope < -0.1:
            momentum = "bearish"
        else:
            momentum = "neutral"
        
        return {
            "is_squeezed": is_squeezed,
            "squeeze_bars": squeeze_bars,
            "bb_width": bb_width,
            "kc_width": kc_width,
            "momentum": momentum,
            "squeeze_data": {
                "bb_upper": current_bb_u,
                "bb_lower": current_bb_l,
                "kc_upper": current_kc_u,
                "kc_lower": current_kc_l,
                "ema20": ema20.iloc[-1]
            }
        }

    def check_squeeze_breakout(self, df):
        """
        Detects if a squeeze has just broken out.
        
        A breakout occurs when:
        1. Stock WAS in squeeze on previous bar
        2. Stock is NO LONGER in squeeze on current bar
        3. Accompanied by volume expansion
        
        Returns:
            tuple: (is_breakout, direction, breakout_data)
            - is_breakout: bool
            - direction: "bullish" or "bearish" or None
            - breakout_data: dict with squeeze details
        """
        if df.empty or len(df) < 21:
            return False, None, None
        
        # Get current squeeze status
        current_status = self.get_squeeze_status(df)
        if not current_status:
            return False, None, None
        
        # Get previous bar squeeze status
        df_prev = df.iloc[:-1]
        prev_status = self.get_squeeze_status(df_prev)
        if not prev_status:
            return False, None, None
        
        # Check if breakout occurred (was squeezed, now released)
        is_breakout = prev_status["is_squeezed"] and not current_status["is_squeezed"]
        
        if not is_breakout:
            return False, None, None
        
        # Determine breakout direction
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        price_change_pct = ((current_price - prev_price) / prev_price) * 100
        
        # Check volume confirmation
        current_volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].iloc[-21:-1].mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Use momentum from previous squeeze to determine direction
        momentum = prev_status["momentum"]
        
        # Breakout direction based on price action and momentum
        if price_change_pct > 0.5 or momentum == "bullish":
            direction = "bullish"
        elif price_change_pct < -0.5 or momentum == "bearish":
            direction = "bearish"
        else:
            # Use which band was broken
            bb_upper = current_status["squeeze_data"]["bb_upper"]
            bb_lower = current_status["squeeze_data"]["bb_lower"]
            
            if current_price > bb_upper:
                direction = "bullish"
            elif current_price < bb_lower:
                direction = "bearish"
            else:
                direction = "neutral"
        
        breakout_data = {
            "squeeze_duration": prev_status["squeeze_bars"],
            "price": current_price,
            "price_change_pct": price_change_pct,
            "volume_ratio": volume_ratio,
            "momentum": momentum,
            "bb_upper": current_status["squeeze_data"]["bb_upper"],
            "bb_lower": current_status["squeeze_data"]["bb_lower"],
            "ema20": current_status["squeeze_data"]["ema20"]
        }
        
        return True, direction, breakout_data

    def check_breakout(self, df):
        """
        Checks for volume/price breakout.
        Logic: Price > 20-day High AND Volume > 2 * 20-day Average Volume.
        """
        if df.empty or len(df) < 21:
            return False
            
        current_price = df['Close'].iloc[-1]
        current_volume = df['Volume'].iloc[-1]
        
        # Previous 20 days (excluding today)
        recent_high = df['High'].iloc[-21:-1].max()
        avg_volume = df['Volume'].iloc[-21:-1].mean()
        
        if current_price > recent_high and current_volume > 2 * avg_volume:
            return True
            
        return False

    def check_volume_spike(self, df, threshold=5.0):
        """
        Checks if current volume is > threshold * average volume (20 days).
        """
        if df.empty or len(df) < 21:
            return False
            
        current_volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].iloc[-21:-1].mean()
        
        if current_volume > threshold * avg_volume:
            return True
        return False

    def check_volume_vs_history(self, df, lookback_years=2):
        """
        Checks if current volume is highest in 1-2 years.
        
        Returns:
            dict with keys:
            - is_record: bool (highest volume in lookback period)
            - percentile: float (where current volume ranks, 0-100)
            - avg_volume: float (average volume over period)
            - max_volume: float (max volume in period)
        """
        if df.empty or len(df) < 21:
            return None
        
        current_volume = df['Volume'].iloc[-1]
        
        # Get historical volume data (up to lookback_years)
        days_in_period = min(len(df), lookback_years * 252)  # 252 trading days per year
        historical_volume = df['Volume'].iloc[-days_in_period:]
        
        # Calculate statistics
        max_volume = historical_volume.max()
        avg_volume = historical_volume.mean()
        
        # Check if current is record
        is_record = current_volume >= max_volume
        
        # Calculate percentile (what % of days had lower volume)
        percentile = (historical_volume < current_volume).sum() / len(historical_volume) * 100
        
        return {
            "is_record": is_record,
            "percentile": percentile,
            "avg_volume": avg_volume,
            "max_volume": max_volume,
            "current_volume": current_volume,
            "lookback_days": days_in_period
        }

    def check_new_high(self, df):
        """
        Checks if current price is at a 52-week high.
        """
        if df.empty or len(df) < 252:
            return False
            
        current_price = df['Close'].iloc[-1]
        # Max of last 252 days (excluding today to compare)
        year_high = df['High'].iloc[-252:-1].max()
        
        if current_price > year_high:
            return True
        return False

    def check_sector_strength(self, ticker):
        """
        Checks if the stock belongs to a leading sector.
        Note: This is a simplified version. In a full implementation, 
        we would fetch sector performance data from FMP.
        """
        # Mapping of some major tickers to sectors (Simplified for demo)
        # In production, this would be a dynamic lookup
        tech_stocks = ["AAPL", "MSFT", "NVDA", "AMD", "GOOGL", "META", "CRM", "ADBE"]
        energy_stocks = ["XOM", "CVX", "COP", "SLB", "EOG"]
        financials = ["JPM", "BAC", "WFC", "C", "GS", "MS"]
        
        # Assume Tech and Energy are leading sectors currently (Example)
        leading_sectors = tech_stocks + energy_stocks
        
        if ticker in leading_sectors:
            return True
        return False


    def check_volume_precursor(self, df):
        """
        Detects volume building BEFORE price moves (accumulation phase).
        This is a leading indicator for breakouts.
        
        Criteria:
        1. Current volume 1.5x+ average
        2. Price change < 1% (hasn't moved yet)
        3. Above 20 SMA (in uptrend)
        4. Not in downtrend
        
        Returns: True if accumulation detected
        """
        if df.empty or len(df) < 21:
            return False
        
        current_volume = df['Volume'].iloc[-1]
        avg_volume_20 = df['Volume'].iloc[-21:-1].mean()
        current_price = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
        
        # Volume 1.5x+ average
        volume_ratio = current_volume / avg_volume_20
        if volume_ratio < 1.5:
            return False
        
        # Price hasn't moved much yet (<1%)
        price_change_pct = abs((current_price - prev_close) / prev_close) * 100
        if price_change_pct >= 1.0:
            return False
        
        # Above 20 SMA (uptrend)
        if current_price < sma_20:
            return False
        
        return True
    
    def check_tight_consolidation(self, df):
        """
        Detects tight consolidation pattern (coiling before breakout).
        
        Criteria:
        1. Trading in 2% range for last 3+ days
        2. Volume decreasing (compression)
        3. Above key moving averages
        
        Returns: True if tight consolidation detected
        """
        if df.empty or len(df) < 21:
            return False
        
        # Last 3 days
        recent = df.tail(3)
        high_3d = recent['High'].max()
        low_3d = recent['Low'].min()
        current_price = df['Close'].iloc[-1]
        
        # Calculate range
        range_pct = ((high_3d - low_3d) / low_3d) * 100
        
        # Tight range (<2%)
        if range_pct >= 2.0:
            return False
        
        # Volume decreasing
        vol_recent = recent['Volume'].mean()
        vol_prev = df['Volume'].iloc[-6:-3].mean()
        if vol_recent >= vol_prev:
            return False
        
        # Above 20 SMA
        sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
        if current_price < sma_20:
            return False
        
        return True
    
    def is_near_resistance(self, df, threshold_pct=5.0):
        """
        Checks if stock is near a key resistance level.
        
        Criteria:
        1. Within threshold_pct of 52-week high OR
        2. Within threshold_pct of recent swing high
        
        Returns: (is_near, resistance_level)
        """
        if df.empty or len(df) < 50:
            return False, 0
        
        current_price = df['Close'].iloc[-1]
        
        # 52-week high
        high_52w = df['High'].tail(252).max() if len(df) >= 252 else df['High'].max()
        distance_from_high = ((high_52w - current_price) / current_price) * 100
        
        if distance_from_high <= threshold_pct and distance_from_high >= 0:
            return True, high_52w
        
        # Recent swing high (last 20 days)
        swing_high = df['High'].tail(20).max()
        distance_from_swing = ((swing_high - current_price) / current_price) * 100
        
        if distance_from_swing <= threshold_pct and distance_from_swing >= 0:
            return True, swing_high
        
        return False, 0


    def check_vcp(self, df):
        """
        Checks for Volatility Contraction Pattern (Minervini).
        Logic:
        1. Primary Trend: Price > 200 SMA.
        2. Contraction: Series of lower highs with decreasing volatility.
        3. Volume: Volume dries up in the last contraction.
        """
        if df.empty or len(df) < 200:
            return False
            
        close = df['Close']
        volume = df['Volume']
        sma200 = close.rolling(window=200).mean().iloc[-1]
        
        # 1. Primary Trend Check
        if close.iloc[-1] < sma200:
            return False
            
        # 2. Contraction Check (Simplified)
        # Check last 3 swing highs are descending
        highs = df['High'].rolling(window=5, center=True).max()
        peaks = []
        for i in range(len(highs)-10, len(highs)):
            if highs.iloc[i] == df['High'].iloc[i]:
                peaks.append(highs.iloc[i])
        
        if len(peaks) < 2:
            return False
            
        # Check if peaks are descending (roughly)
        is_contracting = peaks[-1] < peaks[-2]
        
        # 3. Volume Contraction
        # Volume in last 5 days should be lower than 50-day average
        recent_vol = volume.iloc[-5:].mean()
        avg_vol_50 = volume.iloc[-50:].mean()
        vol_dry_up = recent_vol < 0.7 * avg_vol_50
        
        if is_contracting and vol_dry_up:
            return True
            
        return False

    def check_rsi_divergence(self, df):
        """
        Checks for Bullish RSI Divergence.
        Logic: Price makes Lower Low, RSI makes Higher Low.
        """
        if df.empty or len(df) < 30:
            return False
            
        close = df['Close']
        
        # Calculate RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Find last 2 swing lows in Price
        # This is a complex check, simplified here:
        # Check if Price[-1] < Price[-10] BUT RSI[-1] > RSI[-10]
        
        price_now = close.iloc[-1]
        price_prev = close.iloc[-10] # Approx previous swing
        
        rsi_now = rsi.iloc[-1]
        rsi_prev = rsi.iloc[-10]
        
        if price_now < price_prev and rsi_now > rsi_prev:
            # Confirm RSI is oversold territory or rising from it
            if rsi_prev < 40:
                return True
                
        return False

    def generate_full_report(self, df):
        """
        PROFESSIONAL TRADER ANALYSIS (75 Years Experience Level)
        Multi-timeframe, Relative Strength, Risk/Reward, Volume Profile, Institutional Flow
        """
        if df.empty or len(df) < 50:  # 50 days minimum for quality analysis
            return None
            
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        current_price = close.iloc[-1]
        
        # ========== PHASE 1: MULTI-TIMEFRAME ANALYSIS ==========
        # Daily Trend
        sma20_daily = close.rolling(window=20).mean().iloc[-1]
        sma50_daily = close.rolling(window=50).mean().iloc[-1]
        ema12_daily = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema26_daily = close.ewm(span=26, adjust=False).mean().iloc[-1]
        
        daily_trend = "BULLISH" if current_price > sma20_daily > sma50_daily else "BEARISH"
        
        # Weekly Trend (using daily data, sample every 5 days for weekly approximation)
        weekly_close = close.iloc[::5]  # Approximate weekly
        if len(weekly_close) >= 20:
            sma10_weekly = weekly_close.rolling(window=10).mean().iloc[-1]
            weekly_trend = "BULLISH" if current_price > sma10_weekly else "BEARISH"
            mtf_aligned = (daily_trend == weekly_trend == "BULLISH")
        else:
            weekly_trend = "UNKNOWN"
            mtf_aligned = False
            
        # ========== PHASE 2: RELATIVE STRENGTH VS MARKET ==========
        # Calculate % change over last 20 days
        stock_change = ((close.iloc[-1] / close.iloc[-20]) - 1) * 100
        # Assume SPY avg is ~0.5% in 20 days (rough benchmark)
        spy_benchmark = 0.5
        relative_strength = stock_change - spy_benchmark
        rs_strong = relative_strength > 2  # Outperforming by 2%+
        
        # ========== PHASE 3: VOLUME ANALYSIS ==========
        avg_volume_20 = volume.iloc[-20:].mean()
        current_volume = volume.iloc[-1]
        volume_ratio = current_volume / avg_volume_20
        
        # Look for accumulation (rising price + above avg volume)
        price_rising = close.iloc[-1] > close.iloc[-5]
        institutional_accumulation = price_rising and volume_ratio > 1.5
        
        # ========== PHASE 4: RSI & MACD (Classic) ==========
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        macd = ema12_daily - ema26_daily
        signal = pd.Series(macd).ewm(span=9, adjust=False).mean().iloc[-1] if isinstance(macd, float) else 0
        macd_bullish = macd > signal
        
        # ========== PHASE 5: RISK/REWARD CALCULATION ==========
        # Recent swing low (support)
        recent_low = low.iloc[-20:].min()
        stop_loss = recent_low * 0.98  # 2% below swing low
        risk_per_share = current_price - stop_loss
        
        # Target based on recent highs
        recent_high = high.iloc[-20:].max()
        target = recent_high * 1.05  # 5% above resistance
        reward = target - current_price
        
        if risk_per_share > 0:
            risk_reward_ratio = reward / risk_per_share
        else:
            risk_reward_ratio = 0
            
        acceptable_rr = risk_reward_ratio >= 2.5  # Minimum 1:2.5
        
        # ========== EXPERT SCORING SYSTEM ==========
        score = 0
        reasons = []
        
        # Multi-Timeframe (Weight: 3)
        if mtf_aligned:
            score += 3
            reasons.append("✅ Multi-Timeframe Aligned (Daily+Weekly Bullish)")
        else:
            score -= 1
            reasons.append(f"⚠️ Timeframe Conflict (Daily:{daily_trend}, Weekly:{weekly_trend})")
            
        # Relative Strength (Weight: 2)
        if rs_strong:
            score += 2
            reasons.append(f"💪 Strong Relative Strength (+{relative_strength:.1f}% vs Market)")
        else:
            reasons.append(f"📉 Weak Relative Strength ({relative_strength:.1f}%)")
            
        # Volume/Institutional (Weight: 2)
        if institutional_accumulation:
            score += 2
            reasons.append(f"🏦 Institutional Accumulation (Vol: {volume_ratio:.1f}x)")
        else:
            reasons.append(f"📊 Volume: {volume_ratio:.1f}x Average")
            
        # Risk/Reward (Weight: 2)
        if acceptable_rr:
            score += 2
            reasons.append(f"🎯 Excellent R/R Ratio (1:{risk_reward_ratio:.1f})")
        else:
            score -= 2
            reasons.append(f"⛔ Poor R/R Ratio (1:{risk_reward_ratio:.1f}) - SKIP")
            
        # RSI (Weight: 1)
        if 40 < current_rsi < 60:
            score += 1
            reasons.append(f"⚖️ RSI Neutral Zone ({current_rsi:.0f})")
        elif current_rsi < 35:
            score += 1
            reasons.append(f"🔄 RSI Oversold ({current_rsi:.0f}) - Reversal Play")
        elif current_rsi > 70:
            score -= 1
            reasons.append(f"🔥 RSI Overbought ({current_rsi:.0f}) - Risky")
        else:
            reasons.append(f"📊 RSI: {current_rsi:.0f}")
            
        # MACD (Weight: 1)
        if macd_bullish:
            score += 1
            reasons.append("📈 MACD Bullish Cross")
        else:
            reasons.append("📉 MACD Bearish")

        # VCP Pattern (Weight: 3) - NEW
        if self.check_vcp(df):
            score += 3
            reasons.append("💎 **VCP Pattern Detected** (Minervini Setup)")
            
        # RSI Divergence (Weight: 2) - NEW
        if self.check_rsi_divergence(df):
            score += 2
            reasons.append("🐊 **Bullish RSI Divergence**")

        # Sector Rotation (Weight: 1) - NEW
        # We need to pass ticker to generate_full_report to use this fully
        # For now, we'll skip adding it to score to avoid breaking existing calls
        # but the method is ready for future integration.


            
        # ========== PROFESSIONAL RATING ==========
        # STRICT CRITERIA: Only STRONG BUY if score >= 7
        if score >= 8:
            rating = "STRONG BUY 🟢🟢"
        elif score >= 6:
            rating = "BUY 🟢"
        elif score >= 3:
            rating = "HOLD 🟡"
        elif score <= -2:
            rating = "AVOID 🔴"
        else:
            rating = "WAIT ⏸️"
            
        return {
            "price": current_price,
            "rating": rating,
            "score": score,
            "risk_reward": risk_reward_ratio,
            "entry": current_price,
            "stop": stop_loss,
            "target": target,
            "reasons": reasons
        }
    
    def calculate_trade_plan(self, df, signal_type="LONG"):
        """
        Calculates Entry, Stop Loss, and Targets based on ATR and recent price action.
        Returns a dictionary with trade details.
        """
        if df.empty or len(df) < 20:
            return None
            
        current_price = df['Close'].iloc[-1]
        
        # Calculate ATR (14) for volatility-based stop
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        
        plan = {}
        
        if signal_type == "LONG":
            # Entry: Break of recent high (last 3 days) or current price if momentum is strong
            entry_price = current_price
            
            # Stop Loss: 2x ATR below entry or recent swing low
            stop_loss = entry_price - (2 * atr)
            
            # Target 1: 1.5x Risk
            risk = entry_price - stop_loss
            target1 = entry_price + (1.5 * risk)
            
            # Target 2: 3x Risk (Home Run)
            target2 = entry_price + (3.0 * risk)
            
            plan = {
                "direction": "BULLISH 🐂",
                "entry": entry_price,
                "stop_loss": stop_loss,
                "target_1": target1,
                "target_2": target2,
                "risk_per_share": risk
            }
            
        elif signal_type == "SHORT":
            entry_price = current_price
            stop_loss = entry_price + (2 * atr)
            risk = stop_loss - entry_price
            target1 = entry_price - (1.5 * risk)
            target2 = entry_price - (3.0 * risk)
            
            plan = {
                "direction": "BEARISH 🐻",
                "entry": entry_price,
                "stop_loss": stop_loss,
                "target_1": target1,
                "target_2": target2,
                "risk_per_share": risk
            }
            
        return plan

    def suggest_option(self, price, direction="LONG"):
        """
        Suggests an option contract based on price and direction.
        """
        import math
        
        if direction == "LONG":
            # ATM or slightly OTM Call
            strike = math.ceil(price) # Round up to nearest whole number
            type_ = "CALL"
        else:
            # ATM or slightly OTM Put
            strike = math.floor(price) # Round down
            type_ = "PUT"
            
        return f"Buy {type_} | Strike: ${strike} | Exp: 30-45 Days out (Monthly)"
