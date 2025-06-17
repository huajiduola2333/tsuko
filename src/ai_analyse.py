from google import genai
from google.genai import types
from dotenv import load_dotenv 
from pathlib import Path
import json
import os

prompt_path = Path(__file__).resolve().parent.parent / 'res' / 'prompt'

CONFIG_FILE_NAME = 'config.env'
def get_config_path():
    return os.path.join(os.path.dirname(__file__), f'../{CONFIG_FILE_NAME}')
load_dotenv(dotenv_path=get_config_path())

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
    with open(prompt_path / 'nyaa.txt', 'r') as f:
        prompt = f.read()
    with open(prompt_path / 'classify.txt', 'r') as f:
        prompt += f.read()
    data_with_user_type = {
        "user_type": user_type,
        "data": data
    }
    
    response = ai_response(prompt, json.dumps(data_with_user_type, ensure_ascii=False))

    return response

def ai_details_summary(data):
    with open(prompt_path / 'nyaa.txt', 'r') as f:
        prompt = f.read()
    with open(prompt_path / 'details_summary.txt', 'r') as f:
        prompt += f.read()

        response = ai_response(prompt, data)

    return response

def talk_with_mashiro():
    from main import gwt_details, gwt_classify
    # print(gemini_key)
    with open(prompt_path / 'nyaa.txt', 'r') as f:
        prompt = f.read()
    with open(prompt_path / 'mashiro.txt', 'r') as f:
        prompt += f.read()

    config = types.GenerateContentConfig(
    tools=[gwt_details, gwt_classify]
)

    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=config
        )
    user_input = prompt
    while True:
        response = chat.send_message_stream(user_input)
        for chunk in response:
            print(chunk.text, end="")
        print()
        user_input = input(">>  ")