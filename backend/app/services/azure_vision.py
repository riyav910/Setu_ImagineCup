from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from app.core.config import settings
import io

try:
    client = ComputerVisionClient(settings.AZURE_ENDPOINT, CognitiveServicesCredentials(settings.AZURE_KEY))
except Exception as e:
    print(f"❌ Azure Connection Failed: {e}")
    client = None

def get_image_analysis(image_bytes):
    """
    Sends image to Azure and returns raw analysis.
    We do NOT clean tags here anymore. The LLM will handle the noise.
    """
    if not client:
        raise Exception("Azure Client not initialized.")

    image_stream = io.BytesIO(image_bytes)
    
    analysis = client.analyze_image_in_stream(
        image_stream,
        visual_features=[
            VisualFeatureTypes.description, 
            VisualFeatureTypes.tags, 
            VisualFeatureTypes.color,
            VisualFeatureTypes.brands 
        ]
    )
    
    return analysis

# def extract_brands(analysis):
#     if not analysis.brands:
#         return []
#     return [brand.name for brand in analysis.brands]

def extract_rich_vision_context(analysis):
    """
    Converts Azure Vision output into structured, LLM-ready context.
    """
    context = {
        "objects": [],
        "descriptions": [],
        "colors": {},
        "brands": []
    }

    # 1️⃣ Object tags with confidence
    if analysis.tags:
        for tag in analysis.tags:
            if tag.confidence >= 0.6:
                context["objects"].append({
                    "name": tag.name.lower(),
                    "confidence": round(tag.confidence, 2)
                })

    # 2️⃣ Descriptions (ALL captions)
    if analysis.description and analysis.description.captions:
        for cap in analysis.description.captions:
            if cap.confidence >= 0.5:
                context["descriptions"].append({
                    "text": cap.text,
                    "confidence": round(cap.confidence, 2)
                })

    # 3️⃣ Colors
    if analysis.color:
        context["colors"] = {
            "dominant": analysis.color.dominant_colors or [],
            "accent": analysis.color.accent_color,
            "is_bw": analysis.color.is_bw_img
        }

    # 4️⃣ Brands
    if analysis.brands:
        for brand in analysis.brands:
            if brand.confidence >= 0.6:
                context["brands"].append({
                    "name": brand.name,
                    "confidence": round(brand.confidence, 2)
                })

    return context
