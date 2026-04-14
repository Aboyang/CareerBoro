from agent.agent import Agent


class Streamer:
    def __init__(self):
        self.agent = Agent()

    async def stream(self, prompt: str):
        async for chunk in self.agent.astream(prompt):
            yield chunk