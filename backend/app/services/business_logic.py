import cv2
import numpy as np
from app.services.market_spy import get_real_market_price 
from app.services.llm_service import generate_creative_listings, analyze_price_trends

# --- CONSTANTS ---
IGNORED_TAGS = ["text", "writing", "design", "indoor", "table", "floor", "close-up", "furniture", "houseplant", "wall", "ground", "surface"]

# Priority list: If these appear in the caption, trust them over tags
PRIORITY_OBJECTS = ["chair", "sofa", "table", "lamp", "shoe", "bag", "watch", "laptop", "pen", "bottle", "shawl", "scarf", "toy"]

# Materials to look for (needed for AI Pricing)
MATERIALS = ["leather", "wool", "cotton", "wood", "metal", "plastic", "mesh", "fabric", "gold", "silver", "canvas", "ceramic"]

def filter_main_object(raw_tags, caption):
    """
    Decides product name using both Tags and Caption.
    Priority: Caption Keyword > Tag > Default
    """
    caption_lower = caption.lower()
    
    # 1. Check Caption for specific objects (Most Accurate)
    for obj in PRIORITY_OBJECTS:
        if obj in caption_lower:
            # Catch specific adjectives if present
            if "ergonomic" in caption_lower: return "Ergonomic Chair"
            return obj.capitalize()

    # 2. Check Tags (Fallback)
    valid_tags = [t for t in raw_tags if t not in IGNORED_TAGS]
    
    # 3. Last Resort
    return valid_tags[0].capitalize() if valid_tags else "Product"

def apply_psychological_pricing(price):
    """
    Rounds price to end in 99 or 50 to maximize conversion.
    e.g., 1523 -> 1499
    """
    if price < 100: return price # Keep cheap items exact
    
    remainder = price % 100
    if remainder < 50:
        return price - remainder - 1 # Round down to 99 (e.g. 520 -> 499)
    else:
        return price - remainder + 99 # Round up to 99 (e.g. 560 -> 599)

def calculate_smart_price(main_object, material):
    """
    Combines Market Spy + AI Trend Analysis + Psychology.
    """
    # 1. BASE: Ask the Market Spy (DuckDuckGo)
    market_price = get_real_market_price(main_object)
    
    # 2. MULTIPLIER: Ask AI for Seasonality/Trend Logic
    trend_data = analyze_price_trends(main_object, material, market_price)
    multiplier = trend_data.get("multiplier", 1.1)
    reason = trend_data.get("reason", "Standard Artisan Markup")
    
    # 3. PROFIT CALCULATION
    optimal_price = int(market_price * multiplier)
    
    # 4. PSYCHOLOGY: The "99" Rule
    final_price = apply_psychological_pricing(optimal_price)
    
    # Calculate Profit (Assuming cost is roughly 40% of market price for artisans)
    estimated_cost = int(market_price * 0.4)
    profit = final_price - estimated_cost
    
    return {
        "price": f"₹ {final_price}", 
        "uplift": f"+ ₹{final_price - market_price} (vs Avg Market)",
        "explanation": reason
    }

def analyze_image_quality(image_bytes):
    """
    REAL LOGIC: Calculates brightness and sharpness using OpenCV.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None: return 0, 0 

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    return brightness, sharpness

def generate_advice(confidence, quality_stats, tags):
    """
    Generates advice based on REAL visual metrics.
    """
    brightness, sharpness = quality_stats
    advice = []

    # 1. Check Blur
    if sharpness < 100:
        advice.append("⚠️ Image is blurry. Hold the camera steady.")
    elif sharpness < 500:
        advice.append("ℹ️ Focus is okay, but could be sharper.")
    else:
        advice.append("✅ Excellent focus!")

    # 2. Check Brightness
    if brightness < 60:
        advice.append("⚠️ Too dark. Try moving near a window.")
    elif brightness > 200:
        advice.append("⚠️ Too bright/washed out. Avoid direct flash.")
    else:
        advice.append("✅ Lighting is balanced.")

    # 3. Check Clutter
    if "cluttered" in tags or "many" in tags:
        advice.append("⚠️ Background looks messy. Use a plain sheet.")

    return advice

def generate_listings(main_object, caption, tags, price):
    """Generates text using AI, falls back to template if needed."""
    
    # Identify material for the prompt
    material = next((t for t in tags if t in MATERIALS), "High-quality material")
    
    # 1. TRY AI FIRST (Llama 3 / GPT-4o)
    ai_content = generate_creative_listings(main_object, material, tags, price)
    
    if ai_content:
        return ai_content # ✅ Use the smart AI response

    # 2. FALLBACK TEMPLATE (If AI fails)
    return {
        "amazon": {
            "title": f"Premium {main_object.capitalize()} - {caption}",
            "features": [f"Made of {material}", "Handcrafted by Artisans", "Durable & Eco-friendly"]
        },
        "instagram": f"✨ New Arrival! {caption}. #Handmade #{main_object.capitalize()}",
        "whatsapp": f"Namaste! Selling this {main_object}. Price: {price}. Reply to buy."
    }