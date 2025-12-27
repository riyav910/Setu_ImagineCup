from ddgs import DDGS
import re

def extract_price(text):
    matches = re.findall(
        r'(?:₹|Rs\.?|INR)\s?(\d{1,3}(?:,\d{3})*)',
        text,
        re.IGNORECASE
    )
    prices = []
    for m in matches:
        val = int(m.replace(',', ''))
        if 50 < val < 200000:
            prices.append(val)
    return prices


def get_real_market_price(query):
    print(f"🕵️ Spying on the market for: {query}...")
    search_term = f"{query} price ₹ India site:amazon.in OR site:flipkart.com"

    try:
        results = DDGS().text(search_term, region='in-en', max_results=8)
        found_prices = []

        for r in results:
            text = r['title'] + " " + r['body']
            found_prices.extend(extract_price(text))

        if found_prices:
            avg = sum(found_prices) // len(found_prices)
            print(f"✅ Found Market Price: ₹{avg}")
            return avg

        print("⚠️ No specific price found, using fallback.")
        return 5000 if "furniture" in query.lower() else 800

    except Exception as e:
        print(f"❌ Market Spy Error: {e}")
        return 500
