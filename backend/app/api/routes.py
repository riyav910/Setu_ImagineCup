from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.azure_vision import get_image_analysis
from app.services.business_logic import (
    filter_main_object, 
    calculate_smart_price, 
    generate_advice, 
    generate_listings,
    analyze_image_quality,
    MATERIALS # <--- Importing this list to find material
)

router = APIRouter()

@router.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    try:
        # 1. READ DATA
        image_data = await file.read()
        
        # 2. CALL SERVICES (Get Raw Data First)
        # Call Azure Vision
        analysis = get_image_analysis(image_data)
        # Call OpenCV
        quality_stats = analyze_image_quality(image_data) 
        
        # 3. EXTRACT VARIABLES (Define raw_tags HERE)
        raw_tags = [tag.name.lower() for tag in analysis.tags]
        caption = analysis.description.captions[0].text.capitalize() if analysis.description.captions else "Handmade item"
        confidence = analysis.tags[0].confidence if analysis.tags else 0.5
        
        # 4. APPLY BUSINESS LOGIC (Now raw_tags exists!)
        main_object = filter_main_object(raw_tags, caption)
        
        # Identify Material (needed for Smart Pricing)
        # We look for a known material in the tags, otherwise default
        material = next((t for t in raw_tags if t in MATERIALS), "Standard Material")
        
        # Calculate Price (Using Market Spy + AI Trends)
        pricing_data = calculate_smart_price(main_object, material)
        
        # Generate Advice & Listings
        advice = generate_advice(confidence, quality_stats, raw_tags) 
        listings = generate_listings(main_object, caption, raw_tags, pricing_data["price"])
        
        # 5. RETURN RESPONSE
        return {
            "status": "success",
            "product_name": f"Handcrafted {main_object.capitalize()}",
            "suggested_price": pricing_data["price"],     
            "price_uplift": pricing_data["uplift"],       
            "pricing_reason": pricing_data["explanation"], 
            "photo_advice": advice,
            "listings": listings
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}