"""
Chart Generator Module
Creates technical analysis charts with indicators for stock analysis
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate technical analysis charts with indicators"""
    
    def __init__(self, output_dir='charts'):
        """Initialize chart generator
        
        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created charts directory: {output_dir}")
    
    def calculate_indicators(self, df):
        """Calculate technical indicators for the chart
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        df = df.copy()
        
        # Calculate SMAs
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Calculate EMAs
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        return df
    
    def generate_chart(self, ticker, df, patterns=None, timeframe='6mo'):
        """Generate comprehensive technical analysis chart
        
        Args:
            ticker: Stock ticker symbol
            df: DataFrame with OHLCV data
            patterns: Dict of detected patterns (optional)
            timeframe: Timeframe string for title
            
        Returns:
            Path to generated chart image, or None if error
        """
        try:
            # Ensure we have enough data
            if len(df) < 200:
                logger.warning(f"Insufficient data for {ticker}: {len(df)} bars")
                # Still generate chart but with available indicators
            
            # Calculate indicators
            df = self.calculate_indicators(df)
            
            # Prepare data for mplfinance
            df.index = pd.to_datetime(df.index)
            
            # Create additional plots for indicators
            apds = []
            
            # Add moving averages to main chart
            apds.append(mpf.make_addplot(df['SMA_20'], color='orange', width=1.5, label='SMA 20'))
            apds.append(mpf.make_addplot(df['SMA_50'], color='blue', width=1.5, label='SMA 50'))
            if len(df) >= 200:
                apds.append(mpf.make_addplot(df['SMA_200'], color='red', width=2, label='SMA 200'))
            
            apds.append(mpf.make_addplot(df['EMA_9'], color='cyan', width=1, linestyle='--', label='EMA 9'))
            apds.append(mpf.make_addplot(df['EMA_21'], color='magenta', width=1, linestyle='--', label='EMA 21'))
            
            # Add RSI subplot (panel 2, since volume is panel 1)
            apds.append(mpf.make_addplot(df['RSI'], panel=2, color='purple', ylabel='RSI', 
                                         secondary_y=False))
            
            # Add MACD subplot (panel 3)
            apds.append(mpf.make_addplot(df['MACD'], panel=3, color='blue', ylabel='MACD',
                                         secondary_y=False))
            apds.append(mpf.make_addplot(df['MACD_Signal'], panel=3, color='red',
                                         secondary_y=False))
            apds.append(mpf.make_addplot(df['MACD_Hist'], panel=3, type='bar', color='gray',
                                         alpha=0.5, secondary_y=False))
            
            # Create style
            mc = mpf.make_marketcolors(up='g', down='r', edge='inherit',
                                       wick={'up':'g','down':'r'},
                                       volume='in')
            s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=False)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{ticker}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create title with patterns if provided
            title = f"{ticker} - Technical Analysis"
            if patterns:
                pattern_str = ", ".join([p for p in patterns if patterns[p]])
                if pattern_str:
                    title += f"\n🎯 Patterns: {pattern_str}"
            
            # Plot the chart
            fig, axes = mpf.plot(
                df,
                type='candle',
                style=s,
                title=title,
                ylabel='Price ($)',
                volume=True,
                addplot=apds,
                figsize=(14, 10),
                panel_ratios=(3, 1, 1, 1),  # Main, Volume, RSI, MACD
                returnfig=True,
                warn_too_much_data=500
            )
            
            # Add horizontal lines for RSI overbought/oversold
            # axes[0] = main price, axes[1] = volume, axes[2] = RSI, axes[3] = MACD
            axes[2].axhline(y=70, color='r', linestyle='--', alpha=0.5, linewidth=1)
            axes[2].axhline(y=30, color='g', linestyle='--', alpha=0.5, linewidth=1)
            axes[2].set_ylim([0, 100])
            
            # Add zero line for MACD
            axes[3].axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
            
            # Save the figure
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Generated chart for {ticker}: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating chart for {ticker}: {str(e)}")
            return None
    
    def cleanup_old_charts(self, max_age_hours=24):
        """Remove charts older than specified hours
        
        Args:
            max_age_hours: Maximum age in hours before deletion
        """
        try:
            now = datetime.now()
            count = 0
            
            for filename in os.listdir(self.output_dir):
                if not filename.endswith('.png'):
                    continue
                
                filepath = os.path.join(self.output_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                age_hours = (now - file_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    os.remove(filepath)
                    count += 1
            
            if count > 0:
                logger.info(f"Cleaned up {count} old charts")
                
        except Exception as e:
            logger.error(f"Error cleaning up charts: {str(e)}")
