# Test Expert Analysis
from data_manager import DataManager
from analyzer import Analyzer

dm = DataManager()
a = Analyzer()

print("Testing expert analysis on AAPL...")
df = dm.get_stock_history('AAPL')
print(f"Data rows: {len(df)}")

report = a.generate_full_report(df)

if report and 'score' in report:
    print("\n✅ NEW EXPERT ANALYSIS CONFIRMED!")
    print(f"Rating: {report['rating']}")
    print(f"Score: {report['score']}/12")
    print(f"Entry: ${report['entry']:.2f}")
    print(f"Stop: ${report['stop']:.2f}")
    print(f"Target: ${report['target']:.2f}")
    print(f"R/R: 1:{report['risk_reward']:.1f}")
    print(f"\nTop 3 Reasons:")
    for r in report['reasons'][:3]:
        print(f"  {r}")
else:
    print("\n❌ OLD ANALYSIS - score field missing!")
    if report:
        print(f"Fields: {list(report.keys())}")
