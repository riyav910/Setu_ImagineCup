import cv2
import numpy as np

# --- CONSTANTS ---
IGNORED_TAGS = ["text", "writing", "design", "indoor", "table", "floor", "close-up"]

# Expanded DB (We will replace this with Bing Search next)
PRICE_DB = {
    "pen": 50, "stationery": 100, "bottle": 500, "bag": 1200, 
    "shoe": 2000, "sneaker": 2500, "shawl": 4500, "watch": 3000, 
    "toy": 400, "chair": 1500, "lamp": 800
}

MATERIALS = ["leather", "wool", "cotton", "wood", "metal", "plastic", "gold", "silver"]

def filter_main_object(raw_tags):
    """Decides what the product actually is."""
    valid_tags = [t for t in raw_tags if t not in IGNORED_TAGS]
    return valid_tags[0] if valid_tags else "Product"

def analyze_image_quality(image_bytes):
    """
    REAL LOGIC: Calculates brightness and sharpness using OpenCV.
    """
    # Convert bytes to an image OpenCV can read
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return 0, 0 # Error reading image

    # Convert to Grayscale (needed for analysis)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Calculate Brightness (Average Pixel Intensity: 0-255)
    brightness = np.mean(gray)

    # 2. Calculate Sharpness (Variance of Laplacian)
    # < 100 is usually blurry
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    return brightness, sharpness

def generate_advice(confidence, quality_stats, tags):
    """
    Generates advice based on REAL visual metrics.
    """
    brightness, sharpness = quality_stats
    advice = []

    # 1. Check Blur (Real Logic)
    if sharpness < 100:
        advice.append("⚠️ Image is blurry. Hold the camera steady.")
    elif sharpness < 500:
        advice.append("ℹ️ Focus is okay, but could be sharper.")
    else:
        advice.append("✅ Excellent focus!")

    # 2. Check Brightness (Real Logic)
    if brightness < 60:
        advice.append("⚠️ Too dark. Try moving near a window.")
    elif brightness > 200:
        advice.append("⚠️ Too bright/washed out. Avoid direct flash.")
    else:
        advice.append("✅ Lighting is balanced.")

    # 3. Check Clutter (Tag Logic)
    if "cluttered" in tags or "many" in tags:
        advice.append("⚠️ Background looks messy. Use a plain sheet.")

    return advice

def calculate_price(main_object):
    """Calculates price based on object type (Still Mock DB for now)."""
    base_price = 100 
    for item, price in PRICE_DB.items():
        if item in main_object.lower():
            base_price = price
            break
            
    suggested = int(base_price * 1.5)
    return f"₹ {suggested}", f"+ ₹{suggested - base_price}"

def generate_listings(main_object, caption, tags, price):
    """Generates text (Still Template for now)."""
    material = next((t for t in tags if t in MATERIALS), "High-quality material")
    
    return {
        "amazon": {
            "title": f"Premium {main_object.capitalize()} - {caption}",
            "features": [f"Made of {material}", "Handcrafted by Artisans", "Durable & Eco-friendly"]
        },
        "instagram": f"✨ New Arrival! {caption}. #Handmade #{main_object.capitalize()}",
        "whatsapp": f"Namaste! Selling this {main_object}. Price: {price}. Reply to buy."
    }