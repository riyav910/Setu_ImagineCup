from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.azure_vision import get_image_analysis
from app.services.business_logic import (
    get_product_info,
    calculate_smart_price, 
    generate_advice, 
    generate_listings,
    analyze_image_quality,
)

router = APIRouter()

@router.post("/analyze")
async def analyze_endpoint(
    file: UploadFile = File(...),
    user_features: str = Form(""),
    user_price: str = Form("0")
):
    try:
        # Parse price safely
        try:
            expected_price = int(user_price)
        except:
            expected_price = 0

        # 1. READ IMAGE
        image_data = await file.read()
        
        # 2. AZURE VISION & OPENCV
        analysis = get_image_analysis(image_data)
        quality_stats = analyze_image_quality(image_data)
        
        # 3. EXTRACT DATA
        raw_tags = [tag.name.lower() for tag in analysis.tags]
        caption = analysis.description.captions[0].text.capitalize() if analysis.description.captions else "Handmade item"
        confidence = analysis.tags[0].confidence if analysis.tags else 0.5
        
        # 4. BUSINESS LOGIC
        main_object, material = get_product_info(raw_tags, caption)
        
        # FIX IS HERE: Pass 'expected_price' to the function!
        pricing_data = calculate_smart_price(main_object, material, user_features, expected_price)
        
        advice = generate_advice(confidence, quality_stats, raw_tags) 
        listings = generate_listings(main_object, material, raw_tags, pricing_data["price"], caption)
        
        return {
            "status": "success",
            "product_name": main_object,
            "suggested_price": pricing_data["price"],     
            "price_uplift": pricing_data["uplift"],       
            "pricing_reason": pricing_data["explanation"],
            "unique_tags": pricing_data["keywords_detected"],
            "market_stats": pricing_data["market_stats"], 
            "raw_price": pricing_data["raw_price"],
            "photo_advice": advice,
            "listings": listings
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}