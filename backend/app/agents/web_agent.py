# backend/app/agents/web_agent.py
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import asyncio
import re
import os

class WebAgent:
    def __init__(self):
        self.extracted_results = []
        self.logs = []

    async def run_plan(self, plan: str, timeout=120):
        self.extracted_results = []
        self.logs = []

        steps = [line.strip() for line in plan.splitlines() if line.strip()]
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            for step in steps:
                try:
                    if step.startswith("open:"):
                        url = step[len("open:"):].strip()
                        self.logs.append(f"Opening URL: {url}")
                        await page.goto(url, timeout=timeout * 1000)

                    elif step.startswith("type:"):
                        match = re.match(r"type:\s*(.+?)->\"?(.*)\"?", step)
                        if match:
                            selector, text = match.groups()
                            self.logs.append(f"Typing '{text}' into {selector}")
                            await page.fill(selector.strip(), text.strip())

                    elif step.startswith("press:"):
                        key = step[len("press:"):].strip()
                        self.logs.append(f"Pressing key: {key}")
                        await page.keyboard.press(key)

                    elif step.startswith("click:"):
                        selector = step[len("click:"):].strip()
                        self.logs.append(f"Clicking on {selector}")
                        await page.click(selector, timeout=timeout * 1000)

                    elif step.startswith("extract_text:"):
                        match = re.match(r"extract_text:\s*(.+?)->(\d+)", step)
                        if match:
                            selector, count = match.groups()
                            count = int(count)
                            elements = await page.query_selector_all(selector.strip())
                            for el in elements[:count]:
                                text = await el.inner_text()
                                self.extracted_results.append(text.strip())
                            self.logs.append(f"Extracted {len(self.extracted_results)} items from {selector}")

                    elif step.startswith("screenshot:"):
                        filename = step[len("screenshot:"):].strip()
                        if not filename.endswith(".png"):
                            filename += ".png"
                        os.makedirs("screenshots", exist_ok=True)
                        path = os.path.join("screenshots", filename)
                        await page.screenshot(path=path)
                        self.logs.append(f"Screenshot saved to {path}")

                    else:
                        self.logs.append(f"Unknown action: {step}")

                except PlaywrightTimeout:
                    self.logs.append(f"Timeout on step: {step}")
                except Exception as e:
                    self.logs.append(f"Error on step '{step}': {e}")

            await browser.close()

        return {"logs": self.logs, "extracted": self.extracted_results}
