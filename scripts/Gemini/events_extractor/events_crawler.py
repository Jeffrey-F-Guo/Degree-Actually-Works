import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, JsonCssExtractionStrategy
import os
from dotenv import load_dotenv
from typing import List, Dict
import json

load_dotenv()
base_url = "https://win.wwu.edu/events/?categories=9821&categories=17934&categories=21914&categories=9822&categories=11780&categories=23412&categories=9830"

"""
schema = {
    name: str,
    date: :datetime,
    location: str,
    url: str,
    description: str,

}
"""
"""
Pseudocode:

schema = {js navigation, fields, ...}

while

crawl
check dates
save url
click load
repeat

** how to crawl from where we left offr?

"""
event_preview_schema = {
    "name": "events_list",
    "baseSelector": "a",
    "fields": [
        {
            "name": "event_name",
            "selector": "h3",
            "type": "text",
        },
        {
            "name": "event_url",
            "selector": "a",
            "type": "attribute",
            "attribute_name": "href"
        },
        {
            "name": "event_date",
            # This is the corrected, highly specific selector for ONLY the date div.
            "selector": "div:has(> svg > path[d^='M9 11'])",
            "type": "text"
        },
        {
            "name": "event_location",
            # This is the specific selector for ONLY the location div.
            "selector": "div:has(> svg > path[d^='M12 2C'])",
            "type": "text"
        }
    ]
}
async def extract_event_urls(base_url) -> Dict:
    event_urls = {}
    extraction_strategy = JsonCssExtractionStrategy(event_preview_schema, verbose=True)
    config = CrawlerRunConfig(extraction_strategy=extraction_strategy)
    async with AsyncWebCrawler() as crawler:
        # while True:
        results = await crawler.arun(base_url, config=config)
        events = json.loads(results.extracted_content)
        print(len(events))
        print(events)
    return event_urls

if __name__ == "__main__":
    asyncio.run(extract_event_urls(base_url))