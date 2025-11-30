from data_manager import DataManager
from analyzer import Analyzer
import traceback

dm = DataManager()
analyzer = Analyzer()

df = dm.get_stock_history('AAPL')
print(f"DataFrame has {len(df)} rows")
print(f"Columns: {list(df.columns)}")

try:
    report = analyzer.generate_full_report(df)
    if report:
        print(f"\n✅ SUCCESS: {report['rating']}")
    else:
        print("\n❌ Report returned None")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()
