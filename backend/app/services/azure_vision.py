from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from app.core.config import settings
import io

# Initialize Client Once
try:
    client = ComputerVisionClient(settings.AZURE_ENDPOINT, CognitiveServicesCredentials(settings.AZURE_KEY))
except Exception as e:
    print(f"❌ Azure Connection Failed: {e}")
    client = None

def get_image_analysis(image_bytes):
    """
    Sends image to Azure and returns raw analysis (Tags + Caption).
    """
    if not client:
        raise Exception("Azure Client not initialized.")

    image_stream = io.BytesIO(image_bytes)
    
    # Call Azure
    analysis = client.analyze_image_in_stream(
        image_stream,
        visual_features=[
            VisualFeatureTypes.description, 
            VisualFeatureTypes.tags, 
            VisualFeatureTypes.color
        ]
    )
    
    return analysis