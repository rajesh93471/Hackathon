# This file describes your Python functions to the LLM.
TOOLS = [
    {
        "name": "search_duckduckgo",
        "description": "Searches the web to find relevant links for a user's query. Use this as the first step for any general search question.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query, e.g., 'latest news on AI'."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "fetch_page_content_and_screenshot",
        "description": "Visits a specific URL to get its text content and a screenshot. Use this only when you already have a URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL of the webpage to visit."
                }
            },
            "required": ["url"]
        }
    }
]