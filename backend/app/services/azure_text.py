import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

# Initialize Azure Language Client
endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
key = os.getenv("AZURE_LANGUAGE_KEY")

client = None
if endpoint and key:
    client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

def extract_selling_points(user_input):
    """
    Uses Azure AI Language to extract key phrases from user input.
    e.g. Input: "It has gold zari work and is made of pure silk"
         Output: ["gold zari work", "pure silk"]
    """
    if not client or not user_input:
        return []

    try:
        documents = [user_input]
        response = client.extract_key_phrases(documents=documents)[0]
        
        if not response.is_error:
            return response.key_phrases
        else:
            print(f"Azure NLP Error: {response.error}")
            return []
    except Exception as e:
        print(f"Azure Text Client Error: {e}")
        return []