import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
    AZURE_KEY = os.getenv("AZURE_KEY")
    
    # Validations
    if not AZURE_ENDPOINT or not AZURE_KEY:
        print("❌ CRITICAL: Azure Keys are missing in .env file!")

settings = Settings()