from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from app.services.azure_vision import get_image_analysis, extract_rich_vision_context

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
        try:
            expected_price = int(user_price)
        except:
            expected_price = 0

        # Data Containers
        all_tags = set()
        all_captions = []
        collected_brands = set() # <--- NEW: Store brands here
        best_quality = (0, 0)
        final_confidence = 0.0

        print(f"📸 Processing {len(files)} images...")
        vision_contexts = []

        
        for file in files:
            image_data = await file.read()
            
            # 1. Analyze
            analysis = get_image_analysis(image_data)
            quality_stats = analyze_image_quality(image_data)
            rich_context = extract_rich_vision_context(analysis)
            vision_contexts.append(rich_context)

            
            # 2. Collect Tags
            if analysis.tags:
                for tag in analysis.tags:
                    all_tags.add(tag.name.lower())                 
                if analysis.tags[0].confidence > final_confidence:
                    final_confidence = analysis.tags[0].confidence

            # 3. Collect Captions
            if analysis.description.captions:
                all_captions.append(analysis.description.captions[0].text.capitalize())

            # 4. Collect Brands (NEW)
            # detected_brands = extract_brands(analysis)
            # if detected_brands:
            #     for brand in detected_brands:
            #         collected_brands.add(brand) # Add to brand set
            #         all_tags.add(brand.lower()) # Add to tags for AI context
            #     print(f"🏷️ Brand Detected: {detected_brands}")

            # 5. Quality Check
            if quality_stats[1] > best_quality[1]:
                best_quality = quality_stats

        # --- MERGE ---

        merged_vision = merge_vision_contexts(vision_contexts)
        vision_prompt = format_vision_context(merged_vision, user_features)

        if all_captions:
            master_caption = "\n".join([f"[Image {i+1}]: {cap}" for i, cap in enumerate(all_captions)])
        else:
            master_caption = "Handmade item"
            
        master_tags = list(all_tags)
        
        print(f"🧠 Merged Context:\n{master_caption}")
        # Format Brand String (e.g. "Nike" or "Nike, Adidas")
        brand_str = ", ".join(list(collected_brands)) if collected_brands else "Unknown Brand"

        # --- LOGIC ---
        main_object, material, exclusions = get_product_info(master_tags,master_caption,vision_prompt)

        pricing_data = calculate_smart_price(main_object, material, exclusions, user_features, expected_price)
        advice = generate_advice(final_confidence, best_quality, master_tags, main_object) 
        listings = generate_listings(main_object, material, master_tags, pricing_data["price"], master_caption)
        
        return {
            "status": "success",
            "product_name": main_object,
            "brand": brand_str, # <--- NEW FIELD RETURNED
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
    

def merge_vision_contexts(contexts):
    merged = {
        "objects": {},
        "descriptions": [],
        "colors": set(),
        "brands": {}
    }

    for ctx in contexts:
        for obj in ctx.get("objects", []):
            merged["objects"][obj["name"]] = max(
                merged["objects"].get(obj["name"], 0),
                obj["confidence"]
            )

        merged["descriptions"].extend(ctx.get("descriptions", []))

        for color in ctx.get("colors", {}).get("dominant", []):
            merged["colors"].add(color)

        for brand in ctx.get("brands", []):
            merged["brands"][brand["name"]] = max(
                merged["brands"].get(brand["name"], 0),
                brand["confidence"]
            )

    return {
        "objects": merged["objects"],
        "descriptions": merged["descriptions"],
        "colors": list(merged["colors"]),
        "brands": merged["brands"]
    }

def format_vision_context(vision, user_notes=""):
    lines = ["VISION CONTEXT:"]

    if vision["objects"]:
        lines.append("Objects:")
        for k, v in vision["objects"].items():
            lines.append(f"- {k} ({v})")

    if vision["descriptions"]:
        lines.append("\nDescriptions:")
        for d in vision["descriptions"][:3]:
            lines.append(f"- {d['text']} ({d['confidence']})")

    if vision["colors"]:
        lines.append("\nColors:")
        lines.append("- " + ", ".join(vision["colors"]))

    if vision["brands"]:
        lines.append("\nBrands:")
        for b, c in vision["brands"].items():
            lines.append(f"- {b} ({c})")
    else:
        lines.append("\nBrands:")
        lines.append("- None")

    if user_notes:
        lines.append("\nUser notes:")
        lines.append(f"- {user_notes}")

    return "\n".join(lines)

