import os
from app.chat.models import ChatArgs
from langchain_openai.chat_models import ChatOpenAI


def build_llm(chat_args: ChatArgs, model_name: str):
    return ChatOpenAI(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        model_name=model_name,
        temperature=os.getenv('OPENAI_TEMPERATURE'),
        streaming=chat_args.streaming
    )