import asyncio
from crawl4ai import AsyncWebCrawler
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List
from datetime import date

load_dotenv()


async def crawl():
    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url="https://win.wwu.edu/events")

        # Print the extracted content
        with open("events.html", "w") as f:
            f.write(result.html)
    return result

# Run the async main function
result = asyncio.run(crawl())


class EventEntry(BaseModel):
    event_name: str
    date: str
    page_url: str

class ExtractedEvents(BaseModel):
    events: List[EventEntry] = Field(..., description="A list of events with their details.")


model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

summary_llm = model.with_structured_output(ExtractedEvents)
output = summary_llm.invoke([
    {
        "role": "system",
        "content": """Your role is to extract information from a markdown file.
                Given a markdown file, extract and return a list of events. Each event should have the following fields:

                    event_name: str
                    page_url: str
        """
    },
    {
        "role": "user",
        "content": result.html
    }
])

# print(result.markdown)

print(output)
print(f"output len is {len(output.events)}")
