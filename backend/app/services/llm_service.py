import os
import json
from groq import Groq
from dotenv import load_dotenv
import datetime

load_dotenv()

# Initialize Groq Client
client = None
api_key = os.getenv("GROQ_API_KEY")

if api_key:
    client = Groq(api_key=api_key)
else:
    print("⚠️ WARNING: Groq API Key missing. Listings will be templates.")

# ---------------------------------------------------------
# 1. THE PRODUCT DETECTIVE (Name, Material, Exclusions)
# ---------------------------------------------------------
def analyze_product_details(tags, caption):
    """
    Identifies Name, Material, AND Search Exclusions (Noise).
    Smarter at ignoring props (like shoes/models) in multi-photo uploads.
    """
    if not client:
        return {"name": "Handcrafted Item", "material": "Standard", "exclusions": []}

    prompt = f"""
    You are an Expert Visual Merchandiser. Analyze the following GALLERY of images for a SINGLE product listing.
    
    DETECTED TAGS: {', '.join(tags)}

    ⚠️ WARNING: Computer Vision tags are often visually similar but contextually wrong.
    - Example: It might tag a "Pen" as an "Arrow" or "Weapon" because they are both thin and straight.
    - Example: It might tag a "Hose" as a "Snake".
    
    IMAGE DESCRIPTIONS (Sequential):
    {caption}
    
    ---
    🛑 CRITICAL RULES FOR IDENTIFICATION:
    1. **The "Majority Rule":** Count the images. What is the subject in the *majority* of them?
       - If 4 images show a "Man in a Tracksuit/Co-ord Set" and 1 image shows "Sneakers", the product is the **TRACKSUIT**.
       - The single sneaker photo is just a "styling detail" or prop. IGNORE IT.
    
    2. **"Whole vs. Part" Bias:**
       - Always prefer the "Whole Outfit" (Set, Tracksuit, Suit, Kurta Set) over a "Part" (Shoes, Watch, Bag) unless *every* image focuses *only* on the part.
       - If you see "Top", "Pants", and "Shoes" tags -> The product is likely a **Co-ord Set** or **Tracksuit**.

    3. **Ignore Models:**
       - The model is wearing shoes to complete the look. Do not list the shoes unless the listing is *clearly* for footwear only.
    ---

    YOUR JOB:
    1. Look for the **Semantic Cluster**. (e.g., If you see "Office, Desk, Pen, Arrow", the cluster is "Office Supplies", so "Arrow" is wrong).
    2. Identify the SINGLE main product based on the strongest cluster of tags.
    3. Ignore isolated tags that conflict with the majority context.

    Task:
    1. Identify the Main Product Name (e.g. "Men's Black Co-ord Set", "Cotton Tracksuit").
    2. Identify the Material (e.g. "Cotton Blend", "Polyester").
    3. Identify "Noise Keywords" (Things visible but NOT for sale).
       - *Crucial:* If selling a Co-ord Set, add "shoes", "sneakers", "footwear" to exclusions.

    Return JSON ONLY:
    {{
        "name": "...",
        "material": "...",
        "exclusions": ["word1", "word2"]
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, # Low temp for strict logic
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"🕵️ AI Detective Error: {e}")
        return None

# ---------------------------------------------------------
# 2. THE PRICING STRATEGIST (Price & Reason)
# ---------------------------------------------------------
def analyze_complex_pricing(product_name, material, market_data):
    """
    Inputs: Market Min/Max/Avg.
    Output: Optimal Price + Strategic Explanation.
    """
    if not client:
        return {"recommended_price": int(market_data['avg'] * 1.1), "strategy": "Standard Markup"}

    current_month = datetime.datetime.now().strftime("%B")
    
    prompt = f"""
    Act as a Senior Pricing Strategist.
    
    Product: {product_name} | Material: {material} | Month: {current_month}
    
    Market Data:
    - Low: ₹{market_data['min']} | Avg: ₹{market_data['avg']} | High: ₹{market_data['max']}
    
    Task: Determine Optimal Selling Price.
    Analyze: Seasonality ({material} in {current_month}?), Trends, and Artisan Premium.
    
    Output JSON ONLY:
    {{
        "recommended_price": <integer_value>,
        "strategy": "Max 15 words explanation."
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Pricing AI Error: {e}")
        return {"recommended_price": int(market_data['avg'] * 1.1), "strategy": "Safe average markup."}

# ---------------------------------------------------------
# 3. THE COPYWRITER (Listings)
# ---------------------------------------------------------
def generate_creative_listings(product_name, material, tags, price, caption):
    """
    Generates 100% AI-written listings adapting tone to the product.
    """
    if not client:
        return None

    prompt = f"""
    Act as an expert E-Commerce Copywriter.
    
    Product: {product_name} ({material})
    Context: {caption}
    Price: {price}

    Task:
    1. Identify Product Category (Tech, Fashion, Home).
    2. Write 3 distinct listings:
       - **Amazon:** Title + 5 Bullet points (Tailored to category).
       - **Instagram:** Trendy caption with emojis/hashtags.
       - **WhatsApp:** Polite, direct sales message.

    Output JSON ONLY:
    {{
        "amazon": {{ "title": "...", "features": ["..."] }},
        "instagram": "...",
        "whatsapp": "..."
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Content Gen Error: {e}")
        return None

# ---------------------------------------------------------
# 4. THE PHOTOGRAPHY COACH (Advice)
# ---------------------------------------------------------
def generate_photo_critique(product_name, quality_stats, tags):
    """
    Acts as a professional photographer giving specific advice.
    """
    if not client:
        return None

    brightness, sharpness = quality_stats
    
    prompt = f"""
    Act as a Photo Mentor.
    Product: {product_name}
    Stats: Brightness {int(brightness)} (0-255), Sharpness {int(sharpness)} (0-1000).

    Task: Provide 2 short, specific tips to improve the photo for THIS item.
    
    Output JSON ONLY:
    {{ "tips": ["Tip 1", "Tip 2"] }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        data = json.loads(completion.choices[0].message.content)
        return data.get("tips", [])
    except Exception as e:
        print(f"📸 Photo Coach Error: {e}")
        return None
    
def extract_selling_points(text):
    """
    Extracts high-value keywords from user input to force into the search.
    Replaces azure_text.py.
    """
    if not client or not text:
        return []

    prompt = f"""
    Extract 3-5 specific, high-value e-commerce search keywords from this user description.
    Focus on materials, styles, or unique features.
    
    User Input: "{text}"
    
    Output JSON ONLY:
    {{
        "keywords": ["keyword1", "keyword2"]
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1, # Low temp = strict extraction
            response_format={"type": "json_object"}
        )
        data = json.loads(completion.choices[0].message.content)
        return data.get("keywords", [])
    except Exception as e:
        print(f"🔑 Keyword Extraction Error: {e}")
        # Fallback: Simple split if AI fails
        return [w.strip() for w in text.split() if len(w) > 3]