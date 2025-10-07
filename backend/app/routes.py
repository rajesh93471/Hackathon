from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.orchestrator import Orchestrator
import asyncio

router = APIRouter()
orchestrator = Orchestrator()  # initializes LLM + WebAgent

class CommandRequest(BaseModel):
    command: str

@router.post("/api/agents/execute")
async def execute_agent(req: CommandRequest):
    """Execute any natural language instruction via AI agent."""
    result = await orchestrator.execute_command(req.command)
    return {"status": "ok", "result": result}
