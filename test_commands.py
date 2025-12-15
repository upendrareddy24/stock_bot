# test_commands.py
import pandas as pd
from analyzer import Analyzer
from user_manager import UserManager
from database import Database

# Create dummy price data for 250 days
dates = pd.date_range(end=pd.Timestamp.today(), periods=250)
price = pd.Series([100 + i * 0.1 for i in range(250)], index=dates)
high = price * 1.01
low = price * 0.99
volume = pd.Series([1_000_000 + i * 1000 for i in range(250)], index=dates)

df = pd.DataFrame({
    "Close": price,
    "High": high,
    "Low": low,
    "Volume": volume,
})

# ---------- Analyzer test ----------
analyzer = Analyzer()
report = analyzer.generate_full_report(df)
print("[Analyzer] Report generated:")
print(report)

# ---------- Database seen items test ----------
db = Database()
item_id = "test_news_1"
print("[Database] Is seen before add?", db.is_item_seen(item_id))
db.add_seen_item(item_id, "news")
print("[Database] Is seen after add?", db.is_item_seen(item_id))

# ---------- UserManager test ----------
class DummyUpdate:
    def __init__(self, chat_id):
        self.effective_chat = type("Chat", (), {"id": chat_id})

um = UserManager()
dummy_update = DummyUpdate(chat_id=12345)
um.register_user(dummy_update)
print("[UserManager] Active user IDs:", um.get_active_user_ids())

# Add a paper trade
added = um.add_paper_trade(12345, "AAPL", 150.0, 10, target=160.0, stop=145.0)
print("[UserManager] Paper trade added?", added)
print("[UserManager] Portfolio for user 12345:", um.get_user_portfolio(12345))
