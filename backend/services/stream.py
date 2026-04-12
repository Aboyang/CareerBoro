from openai import OpenAI
from services.agent import Agent
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

agent = Agent()

class Streamer:
    def __init__(self, model: str = "gpt-4.1"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    async def stream(self, prompt: str):

        # 1. Agent runs FIRST (tools happen inside here)
        result = agent.invoke(prompt)

        context = result["messages"][-1].content

        system_prompt = f"""
            Here is the answer to the user's prompt.
            Stream back everything as is:
            {context}
        """

        stream = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user", 
                    "content": prompt
                }, 
                {
                    "role": "system", 
                    "content": system_prompt
                }
            ],
            stream=True
        )

        for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta