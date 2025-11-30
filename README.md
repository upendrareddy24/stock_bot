# Stock Alert Bot Pro

An advanced Telegram bot for stock market analysis, alerts, and paper trading. Powered by expert technical analysis and real-time market data.

## Features

### 📊 Expert Analysis
- **Multi-timeframe analysis** - Daily, weekly, monthly trends
- **Advanced patterns** - VCP, RSI Divergence, Cup & Handle, Squeeze
- **Smart scoring system** - 12-point expert rating (STRONG BUY to AVOID)
- **Risk/reward calculations** - Entry, stop loss, and target prices

### 🔔 Real-Time Alerts
- **Breaking news** - Filtered for positive, high-impact news
- **Market movers** - 5x volume spikes, 52-week highs
- **Insider trading** - Whale activity tracking
- **Scheduled reports** - Pre-market, post-market, daily picks

### 💼 Paper Trading
- `/buy TICKER PRICE QTY` - Add paper trades
- `/portfolio` - View positions and P&L
- Track performance without risking capital

### 📈 On-Demand Commands
- `/picks` - Top 2 stock picks (scans 500+ stocks)
- `/volume` - Top 5 bullish & bearish volume
- `/index` - Market index analysis (SPY, QQQ, DIA)
- `/options TICKER` - Best option contracts
- `/whales` - Recent insider buying
- `TICKER` - Instant stock analysis with rating

## Quick Start

### Local Development
```bash
# Clone repository
git clone <your-repo-url>
cd stock_bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run bot
python main.py
```

### Docker Deployment
```bash
# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f stock-bot
```

## Configuration

Required environment variables:
- `TELEGRAM_TOKEN` - Get from @BotFather on Telegram
- `FMP_API_KEY` - Get from financialmodelingprep.com

Optional:
- `CHAT_ID` - Your Telegram chat ID (for legacy single-user mode)
- `DATABASE_URL` - Database connection (defaults to SQLite)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed cloud deployment instructions.

## Architecture

```
stock_bot/
├── main.py              # Entry point, scheduler
├── bot.py               # Telegram bot handlers
├── analyzer.py          # Technical analysis engine
├── data_manager.py      # Market data fetching
├── database.py          # SQLite/PostgreSQL persistence
├── user_manager.py      # Multi-user management
├── config.py            # Environment configuration
└── index_analyzer.py    # Market index analysis
```

## Tech Stack

- **Python 3.10+**
- **python-telegram-bot** - Telegram API
- **yfinance** - Stock data
- **pandas** - Data analysis
- **SQLite/PostgreSQL** - Database
- **Docker** - Containerization

## Deployment Platforms

Tested and ready for:
- ✅ AWS EC2
- ✅ Google Cloud Run
- ✅ DigitalOcean
- ✅ Heroku
- ✅ Any VPS with Docker

See [DEPLOYMENT.md](DEPLOYMENT.md) for platform-specific guides.

## Stock Universe

Scans **500+ stocks** including:
- Top 300 S&P 500 stocks
- NASDAQ 100 leaders
- Popular growth/meme stocks (PLTR, SOFI, COIN, etc.)
- Major ETFs (SPY, QQQ, ARKK, SOXL, etc.)
- All sectors: Tech, Energy, Finance, Healthcare, Retail, Semiconductors

## Automated Alerts

- **Every 5 min** - Breaking news scan
- **Every 15 min** - Market movers with trade plans
- **8:00 AM** - Daily top picks
- **9:00 AM** - Pre-market index analysis
- **4:15 PM** - Post-market index analysis

## Security

- ✅ No hardcoded credentials
- ✅ Environment variable configuration
- ✅ .gitignore for sensitive files
- ✅ Docker secrets support
- ✅ Multi-user authentication

## License

MIT License - See LICENSE file for details

## Support

For deployment help, see [DEPLOYMENT.md](DEPLOYMENT.md)

For issues, check logs first:
```bash
# Docker
docker-compose logs -f stock-bot

# Manual
tail -f bot_output.log
```

## Credits

Built with expert technical analysis methodologies and real-time market data integration.
