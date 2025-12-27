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

def generate_creative_listings(product_name, material, tags, price):
    """
    Uses Llama 3 (via Groq) to write unique, creative listings.
    """
    if not client:
        return None

    prompt = f"""
    You are an expert social media manager for rural artisans.
    
    Product: {product_name}
    Material: {material}
    Vibe Keywords: {', '.join(tags[:5])}
    Price: {price}

    Task: Write 3 listings in JSON format.
    1. Amazon: Professional title + 3 feature bullet points.
    2. Instagram: Catchy caption with emojis and hashtags.
    3. WhatsApp: Short, polite, direct sales message.

    Output format MUST be valid JSON:
    {{
        "amazon": {{ "title": "...", "features": ["...", "...", "..."] }},
        "instagram": "...",
        "whatsapp": "..."
    }}
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192", # Free, fast, and smart
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq/Llama Error: {e}")
        return None
    
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