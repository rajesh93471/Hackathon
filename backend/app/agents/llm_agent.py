# backend/app/agents/llm_agent.py
import requests

PLANNER_PROMPT = """
You are a browser automation assistant. Break the user's instruction into numbered browser actions:

1. open: <url>
2. type: <CSS selector>-><text>
3. press: <key>
4. click: <CSS selector>
5. extract_text: <CSS selector>-><count>
6. screenshot: <filename>

Instruction:
{instruction}

Output ONLY the numbered list.
"""

class LLMAgent:
    def __init__(self, ollama_url="http://localhost:11434/api/generate", model="llama3"):
        self.ollama_url = ollama_url
        self.model = model

    def plan(self, instruction: str) -> str:
        prompt = PLANNER_PROMPT.format(instruction=instruction)
        response = requests.post(
            self.ollama_url,
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response") or data.get("message") or ""
