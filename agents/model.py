from langchain.chat_models import init_chat_model

import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


model = init_chat_model(
    model="gpt-4.1-mini",
    temperature=0
)