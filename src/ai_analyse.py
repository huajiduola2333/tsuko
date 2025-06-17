from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyCiN1ZTyuzQ2Gh2lMzIJg4xiTzoBqriaGo")

def ai_response(prompt, data):

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=prompt),
        contents=str(data)
    )
    
    return response


