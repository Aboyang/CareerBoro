from langchain.chat_models import init_chat_model

import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


model = init_chat_model(
    model="gpt-5.1",
    temperature=0
)


# model = init_chat_model(
#     model="claude-sonnet-4-6",
#     model_provider="anthropic",
#     temperature=0
# )
