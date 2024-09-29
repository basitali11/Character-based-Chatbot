import os
import uvicorn
from fastapi import FastAPI, Form, HTTPException
from chat import CharacterChat
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
model_id = os.getenv('MODEL_ID')

# Initialize the FastAPI app
app = FastAPI(title="Character-based Chatbot API")

# Initialize a dictionary to hold CharacterChat instances per character
chatbots = {}

# Available characters
available_characters = ["vambi", "kuriemi", "ryoff_karma", "yuji_mizoguchi", "yuta_misaki", "yuya_tegoshi", "sugizo"]   # Extend this list as you add more characters

@app.post("/chat")
async def chat_endpoint(
    character_name: str = Form(...),
    user_id: str = Form(...),
    user_input: str = Form(...)
):
    character_name = character_name.lower()

    # Validate character
    if character_name not in available_characters:
        raise HTTPException(status_code=400, detail=f"Character '{character_name}' is not available.")

    # Initialize CharacterChat instance if not exists
    if character_name not in chatbots:
        chatbots[character_name] = CharacterChat(character_name, openai_api_key, model_id)

    chatbot = chatbots[character_name]

    # Get response from the chatbot
    try:
        response = chatbot.chat(user_id, user_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "user_id": user_id,
        "character_name": character_name,
        "user_input": user_input,
        "response": response
    }


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8023)