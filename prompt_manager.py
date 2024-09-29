import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from prompt import base_prompt

class PromptManager:
    def __init__(self, embeddings):
        self.characters = {}
        self.vectorstores = {}
        self.embeddings = embeddings

    def load_character(self, character_name):
        prompt_file = f"prompts/characters/{character_name}.py"
        data_file = f"data/characters/{character_name}.txt"

        # Load character prompt
        local_vars = {}
        with open(prompt_file, 'r', encoding='utf-8') as f:
            exec(f.read(), globals(), local_vars)

        prompt = local_vars.get('prompt', '')
        prompt1 = local_vars.get('info', '')
        prompt2 = local_vars.get('pavilion_content', '')

        prompt = prompt + prompt1 + prompt2
        # print(f"--------------------------{prompt}\n\n---------------------{prompt1}\n\n---------------------{prompt2}")

        
        # Load character info from text file
        with open(data_file, 'r', encoding='utf-8') as f:
            info = f.read()

        # Concatenate prompts
        full_prompt = f"{prompt}\n\n{info}"

        self.characters[character_name] = {
            'full_prompt': full_prompt
        }

        # Create vector store for character data
        loader = TextLoader(data_file, encoding='utf-8')
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        texts = text_splitter.split_documents(documents)

        self.vectorstores[character_name] = FAISS.from_documents(texts, self.embeddings)
        self.vectorstores[character_name].save_local(f"faiss_index_{character_name}")

    def get_full_prompt(self, character_name):
        return self.characters[character_name]['full_prompt']

    def get_relevant_context(self, character_name, query, k=3):
        # Load the FAISS vector store with dangerous deserialization enabled
        new_db = FAISS.load_local(
            f"faiss_index_{character_name}",
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True  # Add this parameter
        )
        if not new_db:
            print(f"[Error] No vector store found for character: {character_name}")
            return ""

        relevant_docs = new_db.similarity_search(query, k=k)
        if not relevant_docs:
            return "No relevant context found."

        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        return context

    def build_prompt(self, character_name, conversation_history, user_input, relevant_context):
        full_prompt = self.get_full_prompt(character_name)
        return base_prompt.format(
            full_prompt=full_prompt,
            relevant_context=relevant_context,
            conversation_history=conversation_history,
            user_input=user_input,
            character_name=character_name 
        )
