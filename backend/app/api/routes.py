from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.azure_vision import get_image_analysis
# Import the new function
from app.services.business_logic import (
    filter_main_object, 
    calculate_price, 
    generate_advice, 
    generate_listings,
    analyze_image_quality # <--- Add this
)

router = APIRouter()

@router.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    try:
        # 1. Read Data
        image_data = await file.read()
        
        # 2. Call Azure Service (For Tags/Caption)
        analysis = get_image_analysis(image_data)
        
        # 3. Analyze Quality (OpenCV) <--- NEW STEP
        quality_stats = analyze_image_quality(image_data) 
        
        # 4. Extract Raw Data
        raw_tags = [tag.name.lower() for tag in analysis.tags]
        caption = analysis.description.captions[0].text.capitalize() if analysis.description.captions else "Handmade item"
        confidence = analysis.tags[0].confidence if analysis.tags else 0.5
        
        # 5. Apply Business Logic
        main_object = filter_main_object(raw_tags)
        price, uplift = calculate_price(main_object)
        
        # Pass quality_stats to advice generator
        advice = generate_advice(confidence, quality_stats, raw_tags) 
        listings = generate_listings(main_object, caption, raw_tags, price)
        
        return {
            "status": "success",
            "product_name": f"Handcrafted {main_object.capitalize()}",
            "suggested_price": price,
            "price_uplift": uplift,
            "photo_advice": advice,
            "listings": listings
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}