"""
Helper module for options analysis using yfinance
"""
import yfinance as yf
from datetime import datetime, timedelta


def get_options_for_ticker(ticker):
    """Get options chain for a ticker using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        
        # Get all expiration dates
        expirations = stock.options
        
        if not expirations or len(expirations) == 0:
            return None, None
        
        # Filter for next 3 months
        today = datetime.now()
        three_months = today + timedelta(days=90)
        
        valid_expirations = []
        for exp_str in expirations:
            exp_date = datetime.strptime(exp_str, '%Y-%m-%d')
            if today < exp_date <= three_months:
                valid_expirations.append(exp_str)
        
        if not valid_expirations:
            return None, None
        
        # Get options chains for all valid expirations
        all_calls = []
        all_puts = []
        
        for exp in valid_expirations:
            try:
                opt_chain = stock.option_chain(exp)
                
                # Add expiration date to each option
                calls = opt_chain.calls.copy()
                calls['expiration'] = exp
                
                puts = opt_chain.puts.copy()
                puts['expiration'] = exp
                
                all_calls.append(calls)
                all_puts.append(puts)
            except:
                continue
        
        if not all_calls and not all_puts:
            return None, None
        
        # Combine all expirations
        import pandas as pd
        calls_df = pd.concat(all_calls, ignore_index=True) if all_calls else pd.DataFrame()
        puts_df = pd.concat(all_puts, ignore_index=True) if all_puts else pd.DataFrame()
        
        return calls_df, puts_df
        
    except Exception as e:
        print(f"Error getting options for {ticker}: {e}")
        return None, None


def score_option(opt_row, current_price, stock_score, direction='call'):
    """Score an option based on professional criteria"""
    try:
        strike = opt_row['strike']
        exp_date = datetime.strptime(opt_row['expiration'], '%Y-%m-%d')
        dte = (exp_date - datetime.now()).days
        last_price = opt_row['lastPrice']
        volume = opt_row.get('volume', 0)
        oi = opt_row.get('openInterest', 0)
        iv = opt_row.get('impliedVolatility', 0) * 100
        
        # Use inTheMoney or calculate delta proxy
        if 'delta' in opt_row and opt_row['delta'] is not None:
            delta = abs(opt_row['delta'])
        else:
            # Approximate delta based on moneyness
            if direction == 'call':
                delta = max(0, min(1, (current_price - strike) / current_price + 0.5))
            else:
                delta = max(0, min(1, (strike - current_price) / current_price + 0.5))
        
        # Skip if no price or volume
        if last_price <= 0 or volume < 10:
            return None
        
        option_score = 0
        
        # Stock quality (most important) - adjusted for 5+ baseline
        option_score += (stock_score - 5) * 2
        
        # Time value (30-60 DTE sweet spot)
        if 30 <= dte <= 60:
            option_score += 3
        elif 20 <= dte <= 75:
            option_score += 2
        else:
            option_score += 1
        
        # Delta
        if 0.40 <= delta <= 0.60:
            option_score += 3
        elif 0.30 <= delta <= 0.70:
            option_score += 2
        else:
            option_score += 1
        
        # Liquidity
        liquidity = volume + oi
        if liquidity > 1000:
            option_score += 3
        elif liquidity > 500:
            option_score += 2
        elif liquidity > 100:
            option_score += 1
        
        # IV
        if iv < 25:
            option_score += 2
        elif iv < 35:
            option_score += 1
        
        # Strike positioning
        if direction == 'call':
            if 1.05 <= strike/current_price <= 1.10:
                option_score += 2
            elif 1.00 <= strike/current_price <= 1.15:
                option_score += 1
        else:
            if 0.90 <= strike/current_price <= 0.95:
                option_score += 2
            elif 0.85 <= strike/current_price <= 1.00:
                option_score += 1
        
        return {
            'score': option_score,
            'strike': strike,
            'expiration': opt_row['expiration'],
            'dte': dte,
            'last_price': last_price,
            'volume': int(volume) if volume else 0,
            'oi': int(oi) if oi else 0,
            'iv': iv,
            'delta': delta
        }
        
    except Exception as e:
        print(f"Error scoring option: {e}")
        return None
