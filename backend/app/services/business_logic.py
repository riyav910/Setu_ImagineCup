import cv2
import numpy as np
from app.services.market_spy import get_market_data 
# from app.services.azure_text import extract_selling_points
from app.services.llm_service import (
    generate_creative_listings, 
    analyze_complex_pricing, 
    analyze_product_details,
    generate_photo_critique,
    extract_selling_points
)
# --- CONSTANTS ---
# We keep IGNORED_TAGS because Azure sometimes gives garbage like "indoor" or "floor"
IGNORED_TAGS = ["text", "writing", "design", "indoor", "table", "floor", "close-up", "furniture", "houseplant", "wall", "ground", "surface", "ceiling"]
def get_product_info(raw_tags, caption, vision_prompt=""):
    """
    Returns Name, Material, AND Exclusions.
    """
    ai_data = analyze_product_details(
    raw_tags,
    f"{caption}\n\n{vision_prompt}"
    )
    
    if ai_data:
        # SAFETY FIX: Use .get() and 'or' to ensure we never return None
        # If AI returns null, we default to "Standard Material"
        name = ai_data.get("name") or "Handcrafted Item"
        material = ai_data.get("material") or "Standard Material"
        exclusions = ai_data.get("exclusions") or []

        print("🧠 FINAL LLM INPUT:\n", f"{caption}\n\n{vision_prompt}")
        
        return name, material, exclusions

    # Fallback (If AI Service is totally down)
    valid_tags = [t for t in raw_tags if t not in IGNORED_TAGS]
    fallback_name = valid_tags[0].capitalize() if valid_tags else "Item"
    
    return fallback_name, "Standard Material", []

def apply_psychological_pricing(price):
    if price < 100: return price
    remainder = price % 100
    if remainder < 50: return price - remainder - 1 
    else: return price - remainder + 99

def calculate_smart_price(main_object, material, exclusions, user_features="", user_expected_price=None):
    
    print(f"\n💎 MATERIAL: {material.upper()} | 🚫 AVOIDING: {exclusions}")
    
    # 1. MARKET SPY (Pass exclusions!)
    unique_keywords = []
    if user_features:
        unique_keywords = extract_selling_points(user_features)
    
    search_query = f"{material} {main_object} {' '.join(unique_keywords)}"
    
    # PASS THE EXCLUSIONS HERE
    market_stats = get_market_data(search_query, exclusions)

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
    pricing_strategy = analyze_complex_pricing(f"{main_object}", material, market_stats)
    optimal_price = pricing_strategy.get("recommended_price", market_stats['avg'])
    if unique_keywords: optimal_price = int(optimal_price * 1.15)
    final_price = apply_psychological_pricing(optimal_price)

    return {
        "price": f"₹ {final_price}", 
        "uplift": f"₹{market_stats['min']} - ₹{market_stats['max']}", 
        "explanation": pricing_strategy.get("strategy", "Optimized price."),
        "keywords_detected": unique_keywords,
        "market_stats": market_stats, 
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

def generate_advice(confidence, quality_stats, tags, product_name):
    """
    Generates dynamic photography advice.
    Primary: AI Photography Coach.
    Fallback: Logic-based checks.
    """
    
    # 1. 🚀 Try AI Coach First (Dynamic)
    ai_tips = generate_photo_critique(product_name, quality_stats, tags)
    
    if ai_tips:
        # Add emojis to make it friendly
        return [f"💡 {tip}" for tip in ai_tips]

    # 2. 🛡️ Fallback (Logic Based)
    # Only runs if AI fails. Kept simple.
    brightness, sharpness = quality_stats
    advice = []
    
    if sharpness < 100: 
        advice.append("⚠️ Image is blurry. Tap screen to focus.")
    elif sharpness > 500:
        advice.append("✅ Crystal clear focus!")
    
    if brightness < 60: 
        advice.append("⚠️ A bit dark. Try moving near a window.")
    elif brightness > 200: 
        advice.append("⚠️ Too bright. Reduces glare.")
    else:
        advice.append("✅ Perfect lighting.")
        
    return advice

def generate_listings(main_object, material, tags, price, caption):
    """
    Primary: 100% AI Generation (Vibe-aware).
    Backup: Safe, minimal text if AI fails.
    """
    
    # 1. AI GENERATION FIRST
    ai_content = generate_creative_listings(main_object, material, tags, price, caption)
    
    if ai_content:
        return ai_content 

    # 2. SAFETY NET (Only runs if AI crashes)
    # We keep this generic so it applies to literally anything (Laptop, Cake, Shoe).
    print("⚠️ AI generation failed. Using generic fallback.")
    
    return {
        "amazon": {
            "title": f"{main_object} ({material}) - {caption}",
            "features": [
                f"Made of {material}",
                "Verified Quality",
                "Available for immediate delivery",
                "Durable construction",
                f"Best price: {price}"
            ]
        },
        "instagram": f"Check out this {main_object}! ✨ {caption}. DM for details. #{main_object.replace(' ', '')}",
        "whatsapp": f"Hello! We have this {main_object} available.\nDetails: {caption}\nPrice: {price}"
    }