import yfinance as yf
import pandas as pd
import datetime
import requests
from config import FMP_API_KEY

class DataManager:
    def __init__(self):
        pass

    def get_comprehensive_stock_universe(self):
        """
        Returns a comprehensive list of 500+ stocks for analysis.
        Includes: S&P 500, NASDAQ 100, popular growth/meme stocks, ETFs, all sectors.
        """
        stock_universe = []
        
        # 1. Get S&P 500 stocks
        sp500 = self.get_sp500_tickers()
        if sp500:
            stock_universe.extend(sp500[:300])  # Top 300 S&P 500
        
        # 2. Get most active stocks
        actives = self.get_most_active()
        if actives:
            stock_universe.extend(actives)
        
        # 3. Add popular growth/meme stocks and ETFs
        popular_stocks = [
            # Tech Giants
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AMD", "NFLX",
            # Growth/Meme Stocks
            "PLTR", "SOFI", "COIN", "MARA", "RIOT", "DKNG", "HOOD", "RBLX", "SNAP",
            "UBER", "LYFT", "ABNB", "SHOP", "SQ", "PYPL", "ROKU", "ZM", "DOCU",
            # Major ETFs
            "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "ARKK", "SOXL", "TQQQ", "SQQQ",
            # Energy/Commodities
            "XOM", "CVX", "COP", "SLB", "GLD", "SLV", "USO", "UNG",
            # Finance
            "JPM", "BAC", "WFC", "GS", "MS", "C", "V", "MA",
            # Healthcare/Biotech
            "JNJ", "PFE", "MRNA", "BNTX", "UNH", "ABBV",
            # Retail/Consumer
            "WMT", "TGT", "COST", "HD", "LOW", "NKE", "SBUX",
            # Semiconductors
            "INTC", "QCOM", "AVGO", "MU", "AMAT", "LRCX", "KLAC",
            # Chinese ADRs
            "BABA", "JD", "PDD", "NIO", "XPEV", "LI", "BIDU"
        ]
        stock_universe.extend(popular_stocks)
        
        # Remove duplicates and return
        return list(set(stock_universe))

    def get_earnings_today(self):
        """
        Fetches stocks with earnings today using FMP API.
        """
        print("Fetching earnings data from FMP...")
        earnings_list = []
        try:
            # FMP API Key
            api_key = FMP_API_KEY
            today = datetime.date.today().strftime("%Y-%m-%d")
            
            # FMP Earnings Calendar
            url = f"https://financialmodelingprep.com/api/v3/earning_calendar?from={today}&to={today}&apikey={api_key}"
            
            response = requests.get(url)
            data = response.json()
            
            if isinstance(data, list):
                for item in data:
                    # Filter for major stocks if possible, or just take the symbol
                    # FMP returns 'symbol', 'revenueEstimated', 'epsEstimated', etc.
                    earnings_list.append(item.get('symbol'))
            
            # Return top 10 to avoid spamming, or filter by importance if we had market cap data
            return earnings_list[:10]
            
        except Exception as e:
            print(f"Error fetching earnings: {e}")
            return []

    def get_economic_data(self):
        """
        Fetches key economic data (CPI, Fed Rates) using FMP API.
        Strictly filters for ONLY major market-moving events.
        """
        print("Fetching economic data from FMP...")
        econ_events = []
        # Very strict list
        important_keywords = ["CPI", "Fed Interest Rate", "Nonfarm Payrolls", "GDP Growth", "FOMC Minutes"]
        
        try:
            api_key = FMP_API_KEY
            today = datetime.date.today().strftime("%Y-%m-%d")
            
            url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={today}&to={today}&apikey={api_key}"
            
            response = requests.get(url)
            data = response.json()
            
            if isinstance(data, list):
                for item in data:
                    event = item.get('event', '')
                    # Check exact matches or strong containment
                    if any(keyword in event for keyword in important_keywords):
                        actual = item.get('actual')
                        estimate = item.get('estimate')
                        unit = item.get('unit', '')
                        
                        actual_str = f"{actual}{unit}" if actual is not None else "Wait"
                        est_str = f"{estimate}{unit}" if estimate is not None else "-"
                        
                        econ_events.append(f"• {event}: {actual_str} (Est: {est_str})")
                    
            return econ_events
        except Exception as e:
            print(f"Error fetching economic data: {e}")
            return []

    def get_stock_splits(self):
        """
        Fetches stock splits happening today.
        """
        print("Fetching stock splits...")
        splits = []
        try:
            api_key = FMP_API_KEY
            today = datetime.date.today().strftime("%Y-%m-%d")
            # FMP Split Calendar
            url = f"https://financialmodelingprep.com/api/v3/stock_split_calendar?from={today}&to={today}&apikey={api_key}"
            
            response = requests.get(url)
            data = response.json()
            
            if isinstance(data, list):
                for item in data:
                    symbol = item.get('symbol')
                    numerator = item.get('numerator')
                    denominator = item.get('denominator')
                    splits.append(f"{symbol} ({numerator}:{denominator})")
            
            return splits
        except Exception as e:
            print(f"Error fetching splits: {e}")
            return []

    def get_most_active(self):
        """
        Fetches the most active stocks (by volume) from FMP.
        """
        print("Fetching most active stocks...")
        tickers = []
        try:
            api_key = FMP_API_KEY
            url = f"https://financialmodelingprep.com/api/v3/stock_market/actives?apikey={api_key}"
            
            response = requests.get(url)
            data = response.json()
            
            if isinstance(data, list):
                for item in data:
                    tickers.append(item.get('symbol'))
            
            return tickers
        except Exception as e:
            print(f"Error fetching active stocks: {e}")
            return []

    def get_major_news(self):
        """
        Fetches general market news or specific stock news.
        Returns a list of dictionaries: [{'symbol': 'AAPL', 'title': 'News Title', 'date': '...'}]
        """
        print("Fetching market news...")
        news_items = []
        try:
            api_key = FMP_API_KEY
            # Stock News for a few major tickers (or we could use 'general_news' if we want broad market)
            # To get "instant" alerts on ANY stock, we should ideally use the 'stock_news' without tickers to get all latest?
            # FMP 'stock_news' usually requires tickers or returns latest for major.
            # Let's use 'general_news' for broad or 'stock_news?limit=10' which gives latest across market.
            
            url = f"https://financialmodelingprep.com/api/v3/stock_news?limit=10&apikey={api_key}"
            response = requests.get(url)
            data = response.json()
            
            if isinstance(data, list):
                for item in data:
                    news_items.append({
                        'symbol': item.get('symbol'),
                        'title': item.get('title'),
                        'date': item.get('publishedDate')
                    })
                    
            return news_items
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def get_stock_history(self, ticker, period="1y", interval="1d"):
        """
        Fetches historical data for a ticker using FMP API.
        """
        print(f"Fetching history for {ticker} from FMP...")
        try:
            api_key = FMP_API_KEY
            # FMP Historical Price Endpoint
            # period/interval mapping is a bit different in FMP. 
            # For daily, we use /historical-price-full/{ticker}
            
            url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey={api_key}"
            
            response = requests.get(url)
            data = response.json()
            
            if "historical" not in data:
                # Raise error to trigger fallback mechanisms
                raise ValueError(f"No historical data found for {ticker} in FMP response")
                
            # Convert to DataFrame
            df = pd.DataFrame(data["historical"])
            
            # FMP returns data in reverse order (newest first), we need oldest first for rolling calcs
            df = df.iloc[::-1].reset_index(drop=True)
            
            # Rename columns to match yfinance format (Capitalized)
            df = df.rename(columns={
                "date": "Date",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume"
            })
            
            # Set Date as index
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            # Filter by period if needed (approximate)
            if period == "1y":
                start_date = datetime.datetime.now() - datetime.timedelta(days=365)
                df = df[df.index >= start_date]
                
            return df
            
        except Exception as e:
            print(f"Error fetching data for {ticker} from FMP: {e}")

        # FALLBACK 1: Try Twelve Data (if key exists)
        from config import TWELVE_DATA_API_KEY
        if TWELVE_DATA_API_KEY:
            print(f"⚠️ FMP failed for {ticker}, falling back to Twelve Data...")
            try:
                # Twelve Data API
                # Mapping interval
                td_interval = "1day" if interval == "1d" else interval
                
                url = "https://api.twelvedata.com/time_series"
                params = {
                    "symbol": ticker,
                    "interval": td_interval,
                    "outputsize": 365 if period == "1y" else 5000, # Approx for coverage
                    "apikey": TWELVE_DATA_API_KEY,
                    "order": "ASC"
                }
                
                resp = requests.get(url, params=params, timeout=10)
                data = resp.json()
                
                if "values" in data:
                    df = pd.DataFrame(data["values"])
                    # Rename columns to Capitalized
                    df = df.rename(columns={
                        "datetime": "Date",
                        "open": "Open", 
                        "high": "High", 
                        "low": "Low", 
                        "close": "Close", 
                        "volume": "Volume"
                    })
                    
                    # Clean data
                    cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                    for col in cols:
                        df[col] = pd.to_numeric(df[col])
                        
                    df['Date'] = pd.to_datetime(df['Date'])
                    df.set_index('Date', inplace=True)
                    
                    print(f"✅ Successfully fetched {ticker} from Twelve Data (Fallback 1)")
                    return df
                else:
                    print(f"Twelve Data error: {data.get('message', 'Unknown error')}")
                    
            except Exception as e_td:
                 print(f"❌ Error fetching from Twelve Data: {e_td}")

        # FALLBACK 2: Try Yahoo Finance (Final Fallback)
        print(f"⚠️ FMP/TD failed for {ticker}, falling back to Yahoo Finance...")
        try:
            # yfinance fallback
            import yfinance as yf
            
            # Map period/interval if needed, yfinance is flexible
            # period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            # interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
            
            # Adjust interval for yfinance
            yf_interval = interval
            if interval == "1min": yf_interval = "1m"
            elif interval == "5min": yf_interval = "5m"
            elif interval == "15min": yf_interval = "15m"
            elif interval == "1hour": yf_interval = "1h"
            
            ticker_obj = yf.Ticker(ticker)
            df = ticker_obj.history(period=period, interval=yf_interval)
            
            if df.empty:
                print(f"No data found for {ticker} in Yahoo Finance.")
                return pd.DataFrame()
            
            # Standardize columns
            # Yahoo returns: Open, High, Low, Close, Volume, Dividends, Stock Splits
            # We need: Open, High, Low, Close, Volume (capitalized)
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            
            # Yahoo index is timezone aware datetime, make it tz-naive for compatibility
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
                
            df.index.name = 'Date'
            
            print(f"✅ Successfully fetched {ticker} from Yahoo Finance (Fallback)")
            return df
            
        except Exception as e_yahoo:
            print(f"❌ Error fetching from Yahoo Finance for {ticker}: {e_yahoo}")
            return pd.DataFrame()

    def get_sp500_tickers(self):
        """
        Fetches S&P 500 tickers using FMP API.
        """
        print("Fetching S&P 500 list from FMP...")
        tickers = []
        try:
            api_key = FMP_API_KEY
            url = f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={api_key}"
            
            response = requests.get(url)
            data = response.json()
            
            if isinstance(data, list):
                for item in data:
                    tickers.append(item.get('symbol'))
            
            return tickers
        except Exception as e:
            print(f"Error fetching S&P 500 list: {e}")
            # Fallback list if API fails
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "AMD", "INTC"]
