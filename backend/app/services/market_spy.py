import re
import statistics
from urllib.parse import urlparse
from ddgs import DDGS

# ❌ BAD WORDS (Keep your existing list)
NEGATIVE_KEYWORDS = ["cover", "sheet", "pillow", "cushion", "protector", "toy", "miniature", "poster", "sticker"]

def extract_domain(url):
    """Extracts 'amazon' from 'https://www.amazon.in/...'"""
    try:
        domain = urlparse(url).netloc
        domain = domain.replace("www.", "").replace(".in", "").replace(".com", "")
        return domain.capitalize()
    except:
        return "Online Store"

def extract_prices(text):
    """(Keep your existing extraction logic here)"""
    matches = re.findall(r'(?:₹|Rs\.?|INR)\s?(\d{1,3}(?:,\d{3})*)', text, re.IGNORECASE)
    valid_prices = []
    for match in matches:
        try:
            price_val = int(match.replace(',', ''))
            if 100 < price_val < 500000:
                valid_prices.append(price_val)
        except:
            continue
    return valid_prices

def remove_outliers(prices):
    """(Keep your existing outlier logic here)"""
    count = len(prices)
    if count < 5: return prices
    prices.sort()
    if count <= 15: return prices[1:-1]
    cut_bottom = int(count * 0.15)
    cut_top = int(count * 0.10)
    if count - (cut_bottom + cut_top) < 3: return prices[1:-1]
    clean_prices = prices[cut_bottom : count - cut_top]
    return clean_prices if clean_prices else prices

def get_market_data(query, exclusions=[]):
    """
    Returns Stats AND the list of Source Websites.
    """
    # 1. Dynamic Negative Query
    negatives = " ".join([f"-{w}" for w in exclusions])
    search_term = f"{query} price buy online india {negatives}"
    
    print(f"🕵️ Deep Market Scan for: '{search_term}'...")
    
    try:
        results = DDGS().text(search_term, region='in-en', max_results=20)
        
        all_prices = []
        sources = set() # Use a set to store unique websites

        for result in results:
            title = result['title']
            body = result['body']
            url = result['href'] # DuckDuckGo gives us the link!
            
            # Skip noise
            if any(bad_word.lower() in title.lower() for bad_word in exclusions):
                continue

            found = extract_prices(title + " " + body)
            
            if found:
                all_prices.extend(found)
                # If we found a price, record the source
                site_name = extract_domain(url)
                if site_name not in ["Youtube", "Facebook", "Instagram"]: # Filter social media noise
                    sources.add(site_name)
            
        if not all_prices:
            return None 

        # Clean Data
        cleaned_prices = remove_outliers(all_prices)
        median_price = int(statistics.median(cleaned_prices))
        
        # Convert set back to list for JSON
        source_list = list(sources)[:5] # Keep top 5 sources

        return {
            "min": min(cleaned_prices),
            "max": max(cleaned_prices),
            "avg": median_price,
            "sources": source_list # <--- NEW FIELD
        }

    except Exception as e:
        print(f"❌ Market Spy Error: {e}")
        return None