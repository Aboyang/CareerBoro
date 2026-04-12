from agent.tools import (
    browse_internet,
    read_webpage,
    match_job_resume,
    fetch_jobs,
    save_job
)
from agent.model import model
from agent.system_prompt import SYSTEM_PROMPT
from langchain.agents import create_agent


class Agent:
    def __init__(self):
        self.tools = [
            browse_internet,
            read_webpage,
            match_job_resume,
            fetch_jobs,
            save_job
        ]

        self.model = model
        self.system_prompt = SYSTEM_PROMPT

        # initialize agent once
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt
        )

    def invoke(self, content: str):
        result = self.agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": content}
                ]
            }
        )

        return result