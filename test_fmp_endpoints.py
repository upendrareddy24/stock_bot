import requests
import json

api_key = "Z0G45b7SaKOKIjdvJUdRjMqDWgyDTv5w"

def test_endpoint(name, url):
    print(f"Testing {name}...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"✅ {name} SUCCESS. Retrieved {len(data)} records.")
                print(f"Sample: {json.dumps(data[0], indent=2)}")
                return True
            else:
                print(f"⚠️ {name} returned empty list (Status 200).")
                return False
        else:
            print(f"❌ {name} FAILED. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {name} ERROR: {str(e)}")
        return False

# Test Insider Trading
# Note: FMP v4 endpoint for insider trading
insider_url = f"https://financialmodelingprep.com/api/v4/insider-trading?symbol=AAPL&limit=5&apikey={api_key}"
test_endpoint("Insider Trading (v4)", insider_url)

# Test Institutional Holders
institutional_url = f"https://financialmodelingprep.com/api/v3/institutional-holder/AAPL?apikey={api_key}"
test_endpoint("Institutional Holders (v3)", institutional_url)

# Test Insider Trading RSS Feed (General Market)
insider_rss_url = f"https://financialmodelingprep.com/api/v4/insider-trading-rss-feed?limit=5&apikey={api_key}"
test_endpoint("Insider Trading RSS (Market Wide)", insider_rss_url)
