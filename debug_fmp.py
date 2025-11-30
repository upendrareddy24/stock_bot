from data_manager import DataManager
import pandas as pd

dm = DataManager()
print("Fetching AAPL...")
df = dm.get_stock_history("AAPL")
print(f"DataFrame Shape: {df.shape}")
print(f"Columns: {df.columns}")
print(f"Head:\n{df.head()}")
print(f"Tail:\n{df.tail()}")

if len(df) < 50:
    print("ERROR: Less than 50 rows!")
else:
    print("SUCCESS: More than 50 rows.")
