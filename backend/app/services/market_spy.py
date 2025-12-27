import re
import statistics # <--- Added this (was missing)
from ddgs import DDGS # <--- Kept your correct import

def extract_prices(text):
    """
    Finds all valid rupee prices in a text string.
    """
    matches = re.findall(r'(?:₹|Rs\.?|INR)\s?(\d{1,3}(?:,\d{3})*)', text, re.IGNORECASE)
    
    valid_prices = []
    for match in matches:
        price_val = int(match.replace(',', ''))
        # Filter noise: Prices between ₹50 and ₹5,00,000
        if 50 < price_val < 500000:
            valid_prices.append(price_val)
    return valid_prices

def get_market_data(query):
    """
    Scrapes the web to find the High, Low, and Average market price.
    """
    print(f"🕵️ Deep Market Scan for: {query}...")
    search_term = f"{query} price in India amazon flipkart myntra"
    
    try:
        # Get more results (15) for better accuracy
        results = DDGS().text(search_term, region='in-en', max_results=15)
        
        all_prices = []
        for result in results:
            text_blob = result['title'] + " " + result['body']
            found = extract_prices(text_blob)
            all_prices.extend(found)
            
        if not all_prices:
            return None # No data found

        # Statistical Analysis
        median_price = int(statistics.median(all_prices))
        min_price = min(all_prices)
        max_price = max(all_prices)
        
        return {
            "min": min_price,
            "max": max_price,
            "avg": median_price,
            "sample_size": len(all_prices)
        }

    except Exception as e:
        print(f"❌ Market Spy Error: {e}")
        return None