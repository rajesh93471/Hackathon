# backend/app/agents/orchestrator.py
import asyncio
from app.agents.llm_agent import LLMAgent
from app.agents.web_agent import WebAgent

class Orchestrator:
    def __init__(self):
        self.llm = LLMAgent()  # synchronous
        self.web = WebAgent()  # async

    async def execute_command(self, command: str, timeout: int = 120):
        # 1. Generate plan from LLM
        plan = self.llm.plan(command)

        # 2. Execute plan using WebAgent (async)
        result = await asyncio.wait_for(self.web.run_plan(plan, timeout=timeout), timeout=timeout)

        # 3. Return structured output
        return {"plan": plan, "execution": result}
