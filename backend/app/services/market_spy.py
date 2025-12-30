import re
import time
import statistics
from urllib.parse import urlparse
from ddgs import DDGS

# ❌ BAD WORDS (Noise to ignore)
# NEGATIVE_KEYWORDS = ["cover", "sheet", "pillow", "cushion", "protector", "toy", "miniature", "poster", "sticker"]

TRUSTED_SITES = [
    "amazon.in", 
    "flipkart.com", 
    "myntra.com", 
    "ajio.com", 
    "nykaa.com", 
    "tatacliq.com", 
    "reliancedigital.in",
    "croma.com"
]

def extract_domain(url):
    """
    Extracts a clean site name from the URL.
    """
    try:
        domain = urlparse(url).netloc
        domain = domain.replace("www.", "").replace("m.", "")
        if "." in domain:
            domain = domain.split(".")[0]
        return domain.capitalize()
    except:
        return "Online Store"

def extract_prices(text):
    """Finds valid INR prices in text."""
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
    """Smart outlier removal."""
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
    Attempts to fetch prices from EACH trusted site individually
    using DuckDuckGo search snippets.
    """
    all_prices = []
    sources = set()

    negatives = " ".join([f"-{w}" for w in exclusions])

    for site in TRUSTED_SITES:
        search_term = f"{query} price {negatives} site:{site}"
        print(f"🕵️ Scanning {site} → '{search_term}'")

        max_retries = 3
        results = []

        for attempt in range(max_retries):
            try:
                time.sleep(1)
                results = list(DDGS().text(
                    search_term,
                    region="in-en",
                    max_results=5
                ))
                break
            except Exception as e:
                print(f"⚠️ {site} attempt {attempt+1}/{max_retries} failed: {e}")
                time.sleep(2)

        if not results:
            print(f"⚠️ No results from {site}")
            continue

        for result in results:
            title = result.get("title", "")
            body = result.get("body", "")
            url = result.get("href", "")

            if any(bad.lower() in title.lower() for bad in exclusions):
                continue

            found = extract_prices(title + " " + body)

            if found:
                all_prices.extend(found)
                sources.add(extract_domain(url))
                print(f"   ✅ {site}: {found}")

    if not all_prices:
        print("⚠️ No prices found across all sites.")
        return None

    cleaned_prices = remove_outliers(all_prices)
    if not cleaned_prices:
        return None

    median_price = int(statistics.median(cleaned_prices))

    return {
        "min": min(cleaned_prices),
        "max": max(cleaned_prices),
        "avg": median_price,
        "sources": list(sources)
    }
