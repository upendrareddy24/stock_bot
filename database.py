import sqlite3
import json
from datetime import datetime
import os

DB_NAME = "stock_bot.db"

class Database:
    def __init__(self):
        self.conn = None
        self.init_db()

    def get_connection(self):
        """Create a database connection"""
        try:
            conn = sqlite3.connect(DB_NAME, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Access columns by name
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                chat_id TEXT UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                subscription_level TEXT DEFAULT 'free'
            )
        ''')
        
        # Signals Table (History of alerts sent)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                strategy TEXT NOT NULL,
                score INTEGER,
                price REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Portfolio Table (Paper Trading)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ticker TEXT NOT NULL,
                entry_price REAL NOT NULL,
                quantity REAL NOT NULL,
                entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'OPEN',
                target_price REAL,
                stop_loss REAL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Watchlist Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ticker TEXT NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, ticker)
            )
        ''')

        # Seen Items Table (for News/Technicals deduplication)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seen_items (
                item_id TEXT PRIMARY KEY,
                item_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        
        conn.commit()
        conn.close()
        print("Database initialized successfully.")

    def add_user(self, chat_id, username=None, first_name=None):
        """Add a new user or update existing"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (chat_id, username, first_name)
                VALUES (?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                is_active=1
            ''', (str(chat_id), username, first_name))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            conn.close()

    def get_active_users(self):
        """Get all active users for broadcasting"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM users WHERE is_active=1")
            return [row['chat_id'] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
        finally:
            conn.close()

    def log_signal(self, ticker, strategy, score, price, metadata=None):
        """Log a trading signal"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            meta_json = json.dumps(metadata) if metadata else "{}"
            cursor.execute('''
                INSERT INTO signals (ticker, strategy, score, price, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (ticker, strategy, score, price, meta_json))
            conn.commit()
        except Exception as e:
            print(f"Error logging signal: {e}")
        finally:
            conn.close()

    # --- Portfolio Methods ---
    
    def add_position(self, user_chat_id, ticker, price, quantity, target=None, stop=None):
        """Add a paper trading position"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # Get user_id
            cursor.execute("SELECT user_id FROM users WHERE chat_id=?", (str(user_chat_id),))
            user = cursor.fetchone()
            if not user:
                return False
            
            user_id = user['user_id']
            
            cursor.execute('''
                INSERT INTO portfolio (user_id, ticker, entry_price, quantity, target_price, stop_loss)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, ticker.upper(), price, quantity, target, stop))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding position: {e}")
            return False
        finally:
            conn.close()

    def get_portfolio(self, user_chat_id):
        """Get open positions for a user"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.* FROM portfolio p
                JOIN users u ON p.user_id = u.user_id
                WHERE u.chat_id = ? AND p.status = 'OPEN'
            ''', (str(user_chat_id),))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching portfolio: {e}")
            return []
        finally:
            conn.close()

    # --- Seen Items Methods ---
    def is_item_seen(self, item_id):
        """Check if item exists in seen_items"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM seen_items WHERE item_id=?", (item_id,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking seen item: {e}")
            return False
        finally:
            conn.close()

    def add_seen_item(self, item_id, item_type="news"):
        """Add item to seen_items"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO seen_items (item_id, item_type) VALUES (?, ?)", (item_id, item_type))
            conn.commit()
        except Exception as e:
            print(f"Error adding seen item: {e}")
        finally:
            conn.close()

