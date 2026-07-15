import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv('C:/Users/USER/Desktop/ARISK V002/.env')

api_key = os.environ.get('GEMINI_API_KEY')
print(f"API Key: {api_key[:10] if api_key else 'None'}")

genai.configure(api_key=api_key)
try:
    for m in genai.list_models():
        print(m.name)
except Exception as e:
    print(f"Error: {e}")
