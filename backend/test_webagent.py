import asyncio
from app.agents.web_agent import WebAgent

# Example plan
plan = """
1. open: https://www.flipkart.com/laptops-store
2. wait_for: input[name='q']
3. type: input[name='q']->laptops under 50000
4. press: Enter
5. wait_for: .s1Q9rs
6. extract_text: .s1Q9rs->5
7. extract_text: .fPjUP->5
8. screenshot: laptops.png
"""


async def main():
    web = WebAgent()  # headless=True for invisible browser, False to see it
    result = await web.run_plan(plan)
    print("Execution result:")
    print(result)

# Run the test
asyncio.run(main())
