"""Test if bot analysis works via Telegram message handler"""
from bot import StockBot

print("Creating bot instance...")
bot = StockBot("7384198714:AAGNdXKZWY5rQP31f-a-Tw4LU3J7qFV288I")

print("\n✅ Bot created successfully!")
print("Handlers registered:")
for handler in bot.app.handlers[0]:
    print(f"  - {handler}")

print("\n📱 The bot should respond when you send it a ticker like 'AAPL' in Telegram.")
print("   If it doesn't, there's an issue with the message handler.")
