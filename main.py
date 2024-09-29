# import os
# from chat import CharacterChat
# from dotenv import load_dotenv

# def main():
#     load_dotenv()
#     openai_api_key = os.getenv('OPENAI_API_KEY')
#     model_id = os.getenv('MODEL_ID', 'gpt-3.5-turbo')

#     print("Welcome to the Personality-based Chatbot!")
#     print("Available characters: vambi")

#     character_name = input("Please select a character: ").lower()
#     chat = CharacterChat(character_name, openai_api_key, model_id)

#     print(f"You are now chatting with {character_name.capitalize()}. Type 'quit' to exit.")

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() == 'quit':
#             break
#         response = chat.chat(user_input)
#         print(f"{character_name.capitalize()}: {response}")

# if __name__ == "__main__":
#     main()
