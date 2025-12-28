from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from app.services.azure_vision import get_image_analysis
from app.services.voice_service import transcribe_audio 
from app.services.business_logic import (
    get_product_info,
    calculate_smart_price, 
    generate_advice, 
    generate_listings,
    analyze_image_quality,
)

router = APIRouter()

@router.post("/analyze-voice")
async def analyze_voice_endpoint(file: UploadFile = File(...)):
    try:
        # 1. READ AUDIO
        audio_data = await file.read()
        
        # 2. TRANSCRIBE & TRANSLATE (The Magic Step)
        english_text = transcribe_audio(audio_data)
        
        if not english_text:
            return {"status": "error", "message": "Could not understand audio."}

        # 3. NOW ACT AS IF THE USER TYPED THIS
        # We just return the text to the frontend so the user can verify it,
        # OR we can immediately trigger the analysis logic here.
        # For better UX, let's return it so the user sees what was heard.
        return {
            "status": "success",
            "detected_text": english_text, # "I have a red banarasi saree..."
            "original_language_hint": "Processed via Whisper-Large"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/analyze")
async def analyze_endpoint(
   files: List[UploadFile] = File(...),
    user_features: str = Form(""),
    user_price: str = Form("0")
):
    try:
        # Parse price safely
        try:
            expected_price = int(user_price)
        except:
            expected_price = 0

        all_tags = set()
        all_captions = []
        best_quality = (0, 0) # Store best brightness/sharpness found
        final_confidence = 0.0

        print(f"📸 Processing {len(files)} images...")
        
        # --- LOOP THROUGH EACH IMAGE ---
        for file in files:
            image_data = await file.read()
            
            # 1. Analyze this specific image
            analysis = get_image_analysis(image_data)
            quality_stats = analyze_image_quality(image_data)
            
            # 2. Collect Data
            if analysis.tags:
                for tag in analysis.tags:
                    all_tags.add(tag.name.lower()) # Add unique tags
                
                # Keep the highest confidence score we find
                if analysis.tags[0].confidence > final_confidence:
                    final_confidence = analysis.tags[0].confidence

            if analysis.description.captions:
                all_captions.append(analysis.description.captions[0].text.capitalize())

            # Keep the quality stats of the sharpest image
            if quality_stats[1] > best_quality[1]:
                best_quality = quality_stats

        # --- MERGE DATA ---
        # Combine captions into one big story: "Front view shows bag. Back view shows leather tag."
        master_caption = " ".join(all_captions) if all_captions else "Handmade item"
        master_tags = list(all_tags)
        
        print(f"🧠 Merged Context: {master_caption}")

        # 2. AZURE VISION & OPENCV
        analysis = get_image_analysis(image_data)
        quality_stats = analyze_image_quality(image_data)
        
        # 3. EXTRACT DATA
        raw_tags = [tag.name.lower() for tag in analysis.tags]
        caption = analysis.description.captions[0].text.capitalize() if analysis.description.captions else "Handmade item"
        confidence = analysis.tags[0].confidence if analysis.tags else 0.5
        
        # 4. BUSINESS LOGIC
        main_object, material, exclusions = get_product_info(master_tags, master_caption)
        
        pricing_data = calculate_smart_price(main_object, material, exclusions, user_features, expected_price)
        
        advice = generate_advice(final_confidence, best_quality, master_tags) 
        listings = generate_listings(main_object, material, master_tags, pricing_data["price"], master_caption)
        
        return {
            "status": "success",
            "product_name": main_object,
            "material": material,
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