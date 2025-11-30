# Stock Bot - Cloud Deployment Guide

## Quick Start (Docker)

### 1. Prerequisites
- Docker and Docker Compose installed
- Telegram Bot Token (from @BotFather)
- FMP API Key (from financialmodelingprep.com)

### 2. Setup Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

### 3. Deploy with Docker Compose
```bash
# Build and start the bot
docker-compose up -d

# View logs
docker-compose logs -f stock-bot

# Stop the bot
docker-compose down
```

## Manual Deployment (VPS/Cloud Server)

### 1. Install Python 3.10+
```bash
sudo apt update
sudo apt install python3.10 python3-pip
```

### 2. Clone and Setup
```bash
cd /opt
git clone <your-repo-url> stock_bot
cd stock_bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Create .env file
cp .env.example .env
nano .env
```

### 4. Run with systemd (Recommended)
Create `/etc/systemd/system/stock-bot.service`:
```ini
[Unit]
Description=Stock Alert Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/stock_bot
Environment="PATH=/opt/stock_bot/venv/bin"
ExecStart=/opt/stock_bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-bot
sudo systemctl start stock-bot
sudo systemctl status stock-bot
```

## Cloud Platform Specific

### AWS EC2
1. Launch t2.micro or t3.small instance (Ubuntu 22.04)
2. Configure security group (no inbound ports needed)
3. Follow manual deployment steps above

### Google Cloud Run
```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/stock-bot

# Deploy
gcloud run deploy stock-bot \
  --image gcr.io/PROJECT_ID/stock-bot \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_TOKEN=xxx,FMP_API_KEY=xxx
```

### Heroku
```bash
# Login and create app
heroku login
heroku create stock-bot-app

# Set environment variables
heroku config:set TELEGRAM_TOKEN=xxx
heroku config:set FMP_API_KEY=xxx

# Deploy
git push heroku main
```

### DigitalOcean App Platform
1. Connect your GitHub repo
2. Select Dockerfile deployment
3. Add environment variables in dashboard
4. Deploy

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_TOKEN` | Bot token from @BotFather | Yes |
| `CHAT_ID` | Your Telegram chat ID | No* |
| `FMP_API_KEY` | Financial Modeling Prep API key | Yes |
| `DATABASE_URL` | Database connection string | No** |
| `LOG_LEVEL` | Logging level (INFO/DEBUG) | No |

*CHAT_ID is optional - bot now supports multi-user registration
**DATABASE_URL defaults to SQLite, use PostgreSQL for production

## Monitoring

### View Logs
```bash
# Docker
docker-compose logs -f stock-bot

# Systemd
sudo journalctl -u stock-bot -f

# Manual
tail -f bot_output.log
```

### Health Check
Send `/start` to your bot to verify it's running

## Troubleshooting

### Bot not responding
1. Check logs for errors
2. Verify TELEGRAM_TOKEN is correct
3. Ensure no firewall blocking outbound HTTPS

### API errors
1. Verify FMP_API_KEY is valid
2. Check API rate limits
3. Review error logs

### Database issues
1. Ensure write permissions to data directory
2. For PostgreSQL, verify DATABASE_URL format
3. Check disk space

## Scaling to Production

### Use PostgreSQL
```bash
# Update .env
DATABASE_URL=postgresql://user:pass@host:5432/stock_bot

# Uncomment postgres service in docker-compose.yml
```

### Add Redis for Caching (Optional)
- Cache stock data to reduce API calls
- Implement rate limiting

### Load Balancing
- Not needed - single bot instance handles all users
- Telegram API prevents multiple instances

## Security Best Practices

1. **Never commit .env file** - Use .env.example as template
2. **Rotate API keys** regularly
3. **Use secrets management** in production (AWS Secrets Manager, etc.)
4. **Enable firewall** - Only allow outbound HTTPS
5. **Regular updates** - Keep dependencies updated

## Backup Strategy

### Database Backup
```bash
# SQLite
cp data/stock_bot.db backups/stock_bot_$(date +%Y%m%d).db

# PostgreSQL
pg_dump $DATABASE_URL > backup.sql
```

### Automated Backups
Add to crontab:
```bash
0 2 * * * /opt/stock_bot/backup.sh
```

## Cost Estimates

| Platform | Instance Type | Monthly Cost |
|----------|--------------|--------------|
| AWS EC2 | t2.micro | $8-10 |
| DigitalOcean | Basic Droplet | $6 |
| Google Cloud | e2-micro | $7-9 |
| Heroku | Hobby Dyno | $7 |

## Support

For issues, check:
1. Logs first
2. Environment variables
3. API quotas
4. Network connectivity
