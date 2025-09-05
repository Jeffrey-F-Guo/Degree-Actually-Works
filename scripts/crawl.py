import asyncio
from crawl4ai import AsyncWebCrawler
import os
import sys
from pydantic import BaseModel, Field
from typing import List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ollama_client import OllamaClient


async def crawl():
    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url="https://win.wwu.edu/events")

        # Print the extracted content
        # print(result.markdown)
    return result

# Run the async main function
result = asyncio.run(crawl())


class EventEntry(BaseModel):
    event_name: str
    event_date: str
    location: str

class ExtractedEvents(BaseModel):
    events: List[EventEntry] = Field(..., description="A list of events with their details.")


# Extract events using Ollama
ollama_client = OllamaClient(model="llama3.2")
events_data = ollama_client.extract_events(result.markdown)

# Convert to ExtractedEvents object
events = []
for event_data in events_data.get("events", []):
    event = EventEntry(
        event_name=event_data.get("event_name", ""),
        event_date=event_data.get("event_date", ""),
        location=event_data.get("location", "")
    )
    events.append(event)

output = ExtractedEvents(events=events)

# print(result.markdown)
print(output)