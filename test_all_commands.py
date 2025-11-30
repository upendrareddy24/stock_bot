# test_all_commands.py
import asyncio
from bot import StockBot
from types import SimpleNamespace

# Dummy bot token (not used for actual Telegram API calls)
TOKEN = "TEST_TOKEN"

# Create the bot instance
bot = StockBot(TOKEN)

# Dummy context with a bot that prints messages
class DummyBot:
    async def send_message(self, chat_id, text, parse_mode=None):
        print(f"[send_message to {chat_id}] {text}\n")

class DummyContext:
    def __init__(self):
        self.bot = DummyBot()
        self.args = []

# Helper to create dummy Update objects
def make_update(command_text=None, chat_id=12345, username="testuser", first_name="Test"):
    # effective_user with username and first_name
    effective_user = SimpleNamespace(username=username, first_name=first_name)
    # effective_chat with id
    effective_chat = SimpleNamespace(id=chat_id)
    # message with reply_text method
    class DummyMessage:
        async def reply_text(self, text, parse_mode=None):
            print(f"[reply to {chat_id}] {text}\n")
    message = DummyMessage()
    # Update object with needed attributes
    update = SimpleNamespace(effective_user=effective_user,
                             effective_chat=effective_chat,
                             message=message)
    return update

async def run_tests():
    ctx = DummyContext()
    # Test /start (register user)
    print("--- Testing /start ---")
    await bot.start(make_update(), ctx)

    # Test /buy command
    print("--- Testing /buy AAPL 150 10 ---")
    ctx.args = ["AAPL", "150", "10"]
    await bot.cmd_buy(make_update(), ctx)

    # Test /portfolio command
    print("--- Testing /portfolio ---")
    await bot.cmd_portfolio(make_update(), ctx)

    # Test unknown command handling
    print("--- Testing unknown command ---")
    await bot.unknown_command(make_update(), ctx)

# Run the async test suite
asyncio.run(run_tests())
