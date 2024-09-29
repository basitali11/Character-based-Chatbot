import os
import datetime
import json
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from prompt_manager import PromptManager
from langchain_openai import OpenAIEmbeddings

class CharacterChat:
    def __init__(self, character_name, openai_api_key, model_id):
        self.character_name = character_name
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.prompt_manager = PromptManager(self.embeddings)
        self.prompt_manager.load_character(character_name)
        self.llm = ChatOpenAI(
            temperature=0.7, 
            model_name=model_id, 
            openai_api_key=openai_api_key
        )
        self.histories = {}  # Store conversation histories per user_id
        self.history_folder = "History"
        os.makedirs(self.history_folder, exist_ok=True)

    def chat(self, user_id, user_input):
        # Initialize memory for the user if not exists
        if user_id not in self.histories:
            self.histories[user_id] = ConversationBufferWindowMemory(k=10, return_messages=True)
        
        relevant_context = self.prompt_manager.get_relevant_context(self.character_name, user_input)

        conversation_history = self.get_conversation_history(user_id)
        prompt = self.prompt_manager.build_prompt(
            character_name=self.character_name,
            conversation_history=conversation_history,
            user_input=user_input,
            relevant_context=relevant_context
        )

        # Send the prompt to the LLM using invoke()
        response = self.llm.invoke([HumanMessage(content=prompt)])

        # Save the conversation
        self.histories[user_id].save_context(
            {"input": user_input},
            {"output": response.content}
        )

        # Save chat history to file
        self.save_chat_history(user_id)

        return response.content

    def get_conversation_history(self, user_id):
        conversation_history = ""
        if user_id in self.histories:
            for message in self.histories[user_id].load_memory_variables({})["history"]:
                if isinstance(message, HumanMessage):
                    conversation_history += f"ユーザー: {message.content}\n"
                elif isinstance(message, AIMessage):
                    conversation_history += f"{self.character_name}: {message.content}\n"
        return conversation_history.strip()

    def save_chat_history(self, user_id):
        # Prepare chat entry
        conversation = []
        history = self.histories[user_id].load_memory_variables({})["history"]
        for i in range(0, len(history), 2):
            user_msg = history[i].content if i < len(history) else ""
            ai_msg = history[i+1].content if i+1 < len(history) else ""
            conversation.append({
                "user_input": user_msg,
                "ai_response": ai_msg
            })
        
        # Load existing data
        filename = os.path.join(self.history_folder, f"user_{user_id}.json")
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        # Update data
        if self.character_name not in data:
            data[self.character_name] = []
        data[self.character_name] = conversation  # Overwrite with the latest conversation

        # Save updated data
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            