from google import genai
from google.genai import types
from dotenv import load_dotenv 
from pathlib import Path
import json
import os

prompt_path = Path(__file__).resolve().parent.parent / 'res' / 'prompt'

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key is None:
    print("ERROR: Gemini api key not found.")

client = genai.Client(api_key=gemini_key)

def ai_response(prompt, data):

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=prompt),
        contents=str(data)
    )
    
    return response.text

def ai_classify(user_type, data):
    with open(prompt_path / 'classify.txt', 'r') as f:
        prompt = f.read()
    data_with_user_type = {
        "user_type": user_type,
        "data": data
    }
    
    response = ai_response(prompt, json.dumps(data_with_user_type, ensure_ascii=False))

    return response