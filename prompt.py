from langchain.prompts import PromptTemplate

base_prompt = PromptTemplate(
    input_variables=["full_prompt", "relevant_context", "conversation_history", "user_input", "character_name"],
    template="""
{full_prompt}

関連するコンテキスト:
{relevant_context}

これまでの会話:
{conversation_history}

ユーザー: {user_input}

{character_name}として、以下のように**簡潔に答えてください（100文字以内）**:
"""
)

