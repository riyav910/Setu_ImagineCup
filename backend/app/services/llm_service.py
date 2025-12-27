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

def generate_creative_listings(product_name, material, tags, price, caption):
    """
    Generates e-commerce listings for ANY product (Tech, Fashion, Home, etc.).
    """
    if not client:
        return None

    # send the Caption for context
    prompt = f"""
    Act as an expert E-Commerce Copywriter.
    
    Product: {product_name}
    Material/Type: {material}
    Key Features (Tags): {', '.join(tags[:6])}
    Visual Description: {caption}
    Price: {price}

    Task: Write 3 distinct listings in JSON format.
    1. **Amazon**: A generic, SEO-friendly title + 5 feature bullet points (focus on utility, durability, and style based on the tags).
    2. **Instagram**: A catchy caption suitable for the product type (use emojis).
    3. **WhatsApp**: A professional, direct sales message.

    **Tone**: Adapt the tone to the product. (e.g., Professional for office gear, Trendy for fashion, Warm for handmade).
    
    Output format MUST be valid JSON:
    {{
        "amazon": {{ "title": "...", "features": ["...", "...", "..."] }},
        "instagram": "...",
        "whatsapp": "..."
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Content Gen Error: {e}")
        return None
    
def analyze_product_details(tags, caption):
    """
    Simultaneously identifies the Specific Name AND Material.
    Replaces hardcoded lists.
    """
    if not client:
        # Fallback if AI is down
        return {"name": "Handcrafted Product", "material": "Standard Material"}

    prompt = f"""
    Analyze these image tags and caption to extract the Product Name and Material.
    
    Tags: {', '.join(tags)}
    Caption: {caption}
    
    Task:
    1. Identify the specific Product Name (e.g. "Wingback Chair", "Silk Saree", "Running Shoe").
    2. Identify the primary Material (e.g. "Velvet", "Leather", "Teak Wood"). If unknown, infer from context or use "Mixed Materials".
    
    Return JSON ONLY:
    {{
        "name": "...",
        "material": "..."
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"🕵️ AI Detective Error: {e}")
        # Intelligent fallback using raw tags if AI fails
        return None
    
def identify_exact_product(tags, caption):
    """
    Uses Llama 3 to figure out the EXACT product name from vague tags.
    e.g. Input: ["furniture", "seat", "wheels"], Caption: "Grey object"
         Output: "Ergonomic Office Chair"
    """
    if not client:
        return "Product" # Fallback

    # We give the AI the raw data and ask for a 2-3 word specific name
    prompt = f"""
    Analyze these image tags and caption to identify the specific product.
    
    Tags: {', '.join(tags)}
    Caption: {caption}
    
    Rules:
    1. Be specific (e.g., instead of "Shoe", say "Running Sneaker").
    2. Instead of "Furniture", say "Wingback Chair" or "Office Desk".
    3. Return ONLY the name (max 3 words). No punctuation.
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, # Low temp = more factual
            max_tokens=20
        )
        # Clean up the response (remove quotes or extra spaces)
        product_name = completion.choices[0].message.content.strip().replace('"', '').replace(".", "")
        return product_name
    except Exception as e:
        print(f"🕵️ Product Detective Error: {e}")
        return None
    
def analyze_complex_pricing(product_name, material, market_data):
    """
    The Advanced Pricing Engine.
    Inputs: Market Min/Max/Avg, Seasonality, Trends.
    Output: Optimal Price + Strategic Explanation.
    """
    if not client:
        return {"multiplier": 1.1, "strategy": "Standard Markup (AI Offline)"}

    current_month = datetime.datetime.now().strftime("%B")
    
    # Construct a detailed economic scenario for the AI
    prompt = f"""
    Act as a Senior Pricing Strategist for a premium handmade marketplace.
    
    Product: {product_name}
    Material: {material}
    Current Month: {current_month}
    
    Market Data (Competitors):
    - Lowest Price: ₹{market_data['min']} (Mass produced/Cheap)
    - Average Price: ₹{market_data['avg']} (Standard)
    - Highest Price: ₹{market_data['max']} (Luxury/Branded)
    
    Task: Determine the Optimal Selling Price to maximize profit without losing customers (churn).
    
    Analyze these factors:
    1. **Seasonality:** Is {material} in high demand in {current_month}? (e.g. Wool in Dec = High, Cotton in May = High).
    2. **Trend:** Is {product_name} currently fashionable?
    3. **Artisan Premium:** Handmade items should cost more than the "Lowest" but be competitive with "Highest".
    4. **Psychology:** Avoid pricing too high above the 'Average' unless the material is premium.
    
    Output JSON ONLY:
    {{
        "recommended_price": <integer_value>,
        "strategy": "Explanation of why this price was chosen (max 15 words). e.g., 'Premium pricing due to high winter demand for wool.'"
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4, # Balanced creativity/logic
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Pricing AI Error: {e}")
        # Fallback: Just use average + 10%
        return {"recommended_price": int(market_data['avg'] * 1.1), "strategy": "Safe average markup."}
    
def analyze_price_trends(product_name, material, current_price):
    """
    Asks Llama 3 to act as a Pricing Analyst.
    Returns a multiplier (e.g., 1.2 for high demand, 0.9 for off-season).
    """
    if not client:
        return {"multiplier": 1.1, "reason": "Standard markup (AI unavailable)."}

    current_month = datetime.datetime.now().strftime("%B")

    prompt = f"""
    Act as a Pricing Algo.
    Product: {product_name}
    Material: {material}
    Current Month: {current_month}
    Base Market Price: ₹{current_price}

    Analyze 3 factors:
    1. Seasonality: Is this material good for {current_month}?
    2. Trend: Is {product_name} trending?
    3. Quality: Is {material} considered premium?

    Based on this, suggest a Price Multiplier (0.8 to 1.5).
    - < 1.0: Off-season/Low demand to reduce churn.
    - 1.0 - 1.2: Standard competitive.
    - > 1.3: High seasonal demand/Premium profit.

    Output JSON ONLY:
    {{
        "multiplier": 1.2,
        "reason": "High demand in winter for wool."
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5, # Lower temperature for logical math
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Pricing AI Error: {e}")
        return {"multiplier": 1.1, "reason": "Standard safe markup."}