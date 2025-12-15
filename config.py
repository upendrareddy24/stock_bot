"""
Configuration module for Stock Bot
Loads environment variables and provides centralized config access
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7384198714:AAGNdXKZWY5rQP31f-a-Tw4LU3J7qFV288I')
CHAT_ID = os.getenv('CHAT_ID', '5662042103')

# Financial Modeling Prep API (Primary)
FMP_API_KEY = os.getenv('FMP_API_KEY', 'jpqEaEcySzNXNAuzjY8XWSQjsU4kgrUt')

# Twelve Data API (Secondary Fallback)
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY', '')

# Alpha Vantage API (Tertiary Fallback)
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'LFFBABGTSL3S1295')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///stock_bot.db')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set"""
    required_vars = {
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'FMP_API_KEY': FMP_API_KEY
    }
    
    missing = []
    for var_name, var_value in required_vars.items():
        if not var_value or var_value.startswith('your_'):
            missing.append(var_name)
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return True
