"""
Test script to verify all bot commands work correctly
"""
import requests
import time

TELEGRAM_TOKEN = "7384198714:AAGNdXKZWY5rQP31f-a-Tw4LU3J7qFV288I"
CHAT_ID = "5662042103"

def send_command(command):
    """Send a command to the bot via Telegram API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": command
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"✅ Sent: {command}")
            return True
        else:
            print(f"❌ Failed to send {command}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending {command}: {e}")
        return False

# List of all commands to test
commands = [
    "/start",
    "/index",
    "/picks",
    "/options AAPL",
    "/whales",
    "/portfolio",
    "/buy AAPL 150 10",
    "TSLA",  # Test ticker analysis
]

print("🧪 Testing all bot commands...\n")

for cmd in commands:
    print(f"\n📤 Testing: {cmd}")
    send_command(cmd)
    time.sleep(3)  # Wait 3 seconds between commands to avoid rate limiting

print("\n✅ All commands sent! Check your Telegram for responses.")
print("Note: Some commands like /picks and /index may take 20-30 seconds to respond.")
