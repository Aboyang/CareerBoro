from agent.tools import browse_internet, read_webpage, match_job_resume, fetch_jobs, save_job, send_email
from agent.model import model
from agent.system_prompt import SYSTEM_PROMPT
from langchain.agents import create_agent


class Agent:
    def __init__(self):
        self.tools = [browse_internet, read_webpage, match_job_resume, fetch_jobs, save_job, send_email]
        self.agent = create_agent(
            model=model,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT
        )

    def invoke(self, content: str):
        return self.agent.invoke({
            "messages": [{"role": "user", "content": content}]
        })

    async def astream(self, content: str):
        final_started = False
        async for event in self.agent.astream_events(
            {"messages": [{"role": "user", "content": content}]},
            version="v2"
        ):
            kind = event["event"]
            node = event["metadata"].get("langgraph_node")

            if kind == "on_tool_start" and node == "tools":
                yield f"⚙️ Calling {event['name']}...\n"

            elif kind == "on_tool_end" and node == "tools":
                yield f"✅ {event['name']} done\n"

            elif kind == "on_chat_model_stream" and node == "model":
                chunk = event["data"]["chunk"]
                if chunk.tool_call_chunks:
                    continue
                text = chunk.content
                if isinstance(text, str) and text:
                    if not final_started:
                        yield "---FINAL---"  # sentinel
                        final_started = True
                    yield text