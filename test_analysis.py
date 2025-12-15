"""Test the stock analysis feature standalone"""
from data_manager import DataManager
from analyzer import Analyzer

print("Testing Stock Analysis Feature...")
dm = DataManager()
analyzer = Analyzer()

# Test with AAPL
ticker = "AAPL"
print(f"\nFetching data for {ticker}...")
df = dm.get_stock_history(ticker)
print(f"Got {len(df)} rows of data")

if len(df) >= 20:
    print("Generating report...")
    report = analyzer.generate_full_report(df)
    
    if report:
        print("\n✅ SUCCESS! Report generated:")
        print(f"Price: ${report['price']:.2f}")
        print(f"Rating: {report['rating']}")
        print("Reasons:")
        for reason in report['reasons']:
            print(f"  • {reason}")
    else:
        print("\n❌ FAILED: Report is None")
else:
    print(f"\n❌ FAILED: Not enough data ({len(df)} rows)")
