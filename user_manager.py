from database import Database

class UserManager:
    def __init__(self):
        self.db = Database()

    def register_user(self, update):
        """Register a user from a Telegram update"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        username = user.username
        first_name = user.first_name
        
        success = self.db.add_user(chat_id, username, first_name)
        if success:
            print(f"User registered: {username} ({chat_id})")
        return success

    def get_subscribers(self):
        """Get list of chat_ids for broadcasting"""
        return self.db.get_active_users()

    def add_paper_trade(self, chat_id, ticker, price, quantity, target=None, stop=None):
        """Add a trade to user's paper portfolio"""
        return self.db.add_position(chat_id, ticker, price, quantity, target, stop)

    def get_user_portfolio(self, chat_id):
        """Get user's portfolio"""
        return self.db.get_portfolio(chat_id)
