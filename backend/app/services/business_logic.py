import cv2
import numpy as np
from app.services.market_spy import get_market_data 
from app.services.azure_text import extract_selling_points
from app.services.llm_service import (
    generate_creative_listings, 
    analyze_complex_pricing, 
    analyze_product_details
)
# --- CONSTANTS ---
# We keep IGNORED_TAGS because Azure sometimes gives garbage like "indoor" or "floor"
IGNORED_TAGS = ["text", "writing", "design", "indoor", "table", "floor", "close-up", "furniture", "houseplant", "wall", "ground", "surface", "ceiling"]

def get_product_info(raw_tags, caption):
    """The new 'Master Function' that gets Name and Material from AI."""
    ai_data = analyze_product_details(raw_tags, caption)
    if ai_data:
        return ai_data["name"], ai_data["material"]

    valid_tags = [t for t in raw_tags if t not in IGNORED_TAGS]
    fallback_name = valid_tags[0].capitalize() if valid_tags else "Handcrafted Item"
    fallback_material = "Sustainable Material"
    return fallback_name, fallback_material

def apply_psychological_pricing(price):
    if price < 100: return price
    remainder = price % 100
    if remainder < 50: return price - remainder - 1 
    else: return price - remainder + 99

def calculate_smart_price(main_object, material, user_features="", user_expected_price=None):
    """
    Price Engine v3: Spy -> User Fallback -> AI Optimize.
    """
    # 1. MARKET SPY (Try to find real data first)
    unique_keywords = []
    if user_features:
        unique_keywords = extract_selling_points(user_features)
    
    search_query = f"{main_object} {' '.join(unique_keywords)}"
    market_stats = get_market_data(search_query)
    
    # Retry with generic name if specific search failed
    if not market_stats:
        market_stats = get_market_data(main_object)

    # 2. FALLBACK: USE USER'S PRICE (If Spy Failed)
    if not market_stats:
        if user_expected_price and user_expected_price > 0:
            # Create synthetic market data around the user's price
            print(f"⚠️ Market Spy failed. Using User Price: {user_expected_price}")
            market_stats = {
                "min": int(user_expected_price * 0.8), # -20%
                "max": int(user_expected_price * 1.4), # +40%
                "avg": int(user_expected_price)
            }
        else:
            # Last resort safety net (if user didn't give a price either)
            market_stats = {"min": 500, "max": 2000, "avg": 1000}

    # 3. AI STRATEGY (Apply Seasonality, Trends, & Uniqueness)
    # The AI will now modify the User's Price based on factors!
    pricing_strategy = analyze_complex_pricing(f"{main_object} ({user_features})", material, market_stats)
    
    optimal_price = pricing_strategy.get("recommended_price", market_stats['avg'])
    
    # 4. UNIQUENESS MARKUP
    if unique_keywords:
        optimal_price = int(optimal_price * 1.15)
        
    reason = pricing_strategy.get("strategy", "Optimized based on market factors.")
    final_price = apply_psychological_pricing(optimal_price)
    
    return {
        "price": f"₹ {final_price}", 
        "uplift": f"₹{market_stats['min']} - ₹{market_stats['max']}", 
        "explanation": reason,
        "keywords_detected": unique_keywords,
        "market_stats": market_stats, # Return for Graph
        "raw_price": final_price
    }

def analyze_image_quality(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None: return 0, 0 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    return brightness, sharpness

def generate_advice(confidence, quality_stats, tags):
    brightness, sharpness = quality_stats
    advice = []
    if sharpness < 100: advice.append("⚠️ Image is blurry. Hold steady.")
    elif sharpness < 500: advice.append("ℹ️ Focus is okay, but could be sharper.")
    else: advice.append("✅ Great focus!")
    
    if brightness < 60: advice.append("⚠️ Too dark. Find better light.")
    elif brightness > 200: advice.append("⚠️ Too bright. Avoid flash.")
    else: advice.append("✅ Lighting is balanced.")
    return advice

def generate_listings(main_object, material, tags, price, caption):
    """
    Generates dynamic content. 
    If AI works -> Returns curated AI text.
    If AI fails -> Constructs valid text from tags/caption (No hardcoding).
    """
    
    # 1. Try AI Generation (Now passing 'caption')
    ai_content = generate_creative_listings(main_object, material, tags, price, caption)
    
    if ai_content:
        return ai_content 

    # 2. Smart Fallback (If AI is down)
    # We build the text dynamically based on what we actually know
    
    # Create dynamic features from top tags
    feature_1 = f"Premium quality {material}" if material else "High-quality build"
    feature_2 = f"Designed for {tags[0]}" if tags else "Modern design"
    feature_3 = f"{caption}" # Use the visual description as a feature
    
    return {
        "amazon": {
            "title": f"{main_object} - {caption}",
            "features": [
                feature_1.capitalize(),
                feature_2.capitalize(),
                "Durable and long-lasting",
                "Available for immediate shipping",
                f"Best value at {price}"
            ]
        },
        "instagram": f"Check out this {main_object}! 📸 {caption}. Get yours now for {price}. #{main_object.replace(' ', '')} #NewArrival",
        "whatsapp": f"Hello! We have a new {main_object} available. \n\nDetails: {caption}\nPrice: {price}.\n\nReply to order!"
    }