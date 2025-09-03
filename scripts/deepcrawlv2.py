import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.deep_crawling.filters import FilterChain, DomainFilter
from pydantic import BaseModel, Field
from typing import List
import os
from dotenv import load_dotenv
import json

load_dotenv()
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')

class EventEntry(BaseModel):
    name: str
    date: str
    location: str
    source_url: str = Field(default="", description="URL where the event was found")

class ExtractedEvents(BaseModel):
    events: List[EventEntry] = Field(..., description="A list of events with their details.")

async def main():
    # Configure extraction strategy
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="gemini/gemini-2.5-flash",
            api_token=GEMINI_API_KEY,
        ),
        extraction_type="schema",
        input_format="markdown",
        schema=ExtractedEvents.model_json_schema(),  # Updated method name
        instruction="""Your role is to extract event information from markdown content.
                    Given markdown content from a webpage, extract and return a list of events.
                    Each event should have the following fields:

                    - name: The name/title of the event
                    - date: The date and time of the event (keep original format)
                    - location: Where the event is taking place
                    - source_url: The URL where this event information was found

                    If no events are found, return an empty list.
                    Be thorough and look for any event-related information including:
                    - Scheduled events, meetings, workshops
                    - Performances, lectures, seminars
                    - Social activities, sports events
                    - Academic events, deadlines
                    """
    )
    # link_filter = FilterChain([DomainFilter(allowed_domains=['win.wwu.edu'])])
    # Configure a 1-level deep crawl (depth=1 means one level deep)
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=1,
            include_external=False,
            max_pages=10,
            # filter_chain = link_filter,
            # link_filter_patterns=[
            #     r".*event.*",  # Include URLs containing 'event'
            #     r".*calendar.*",  # Include URLs containing 'calendar'
            #     r".*activity.*",  # Include URLs containing 'activity'
            # ]
        ),
        extraction_strategy=llm_strategy,
        verbose=True
    )

    async with AsyncWebCrawler() as crawler:
        try:
            results = await crawler.arun("https://win.wwu.edu/events", config=config)

            print(f"Crawled {len(results)} pages in total")
            print("\n" + "="*60)

            all_events = []

            # Process each result -- go through the events for each page
            for i, result in enumerate(results):
                print(f"\nPage {i+1}:")
                print(f"URL: {result.url}")
                print(f"Depth: {result.metadata.get('depth', 0)}")
                print(f"Success: {result.success}")

                content = json.loads(result.extracted_content)
                print("content", content)
                events_list = content[0]["events"]
                if events_list:
                    extracted_events = ExtractedEvents(events=events_list)
                    all_events.extend(extracted_events.events)
                    # for event in events_list:
                    #     print("PROGRESSS")
                    #     print(event)
                    #     extracted_event = EventEntry(**event)
                    #     all_events.append(extracted_event)

                else:
                    print("Did not find events on page")
            



            # Summary and detailed results
            print("\n" + "="*60)
            print(f"SUMMARY: Found {len(all_events)} total events across all pages")
            print("="*60)

            print(all_events)
            # Display all events
            if all_events:
                for i, event in enumerate(all_events):
                    print(f"\nEvent {i}:")
                    print(f"  Name: {event.name}")
                    print(f"  Date: {event.date}")
                    print(f"  Location: {event.location}")
                    print(f"  Source: {event.source_url}")
            else:
                print("No events were extracted from any page.")

            return all_events

        except Exception as e:
            print(f"Error during crawling: {e}")
            return []

if __name__ == "__main__":
    asyncio.run(main())