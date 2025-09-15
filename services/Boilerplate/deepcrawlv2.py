import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, MatchMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, DFSDeepCrawlStrategy
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.deep_crawling.filters import FilterChain, DomainFilter, URLPatternFilter
from pydantic import BaseModel, Field
from typing import List
import os
from dotenv import load_dotenv
import json
from prettytable import PrettyTable
import traceback

load_dotenv()
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
LOG_PATH = "logs"
class EventEntry(BaseModel):
    name: str
    date: str
    location: str
    source_url: str = Field(default="", description="URL where the event was found")

class ExtractedEvents(BaseModel):
    events: List[EventEntry] = Field(..., description="A list of events with their details.")

llm_prompt = """
    Your role is to extract event information from markdown content.
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

async def main():
    # Configure extraction strategy
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="gemini/gemini-2.5-flash",
            api_token=GEMINI_API_KEY,
        ),
        extraction_type="schema",
        input_format="markdown",
        schema=ExtractedEvents.model_json_schema(),
        instruction=llm_prompt
    )
    link_filter = FilterChain(
        filters = [
            DomainFilter(
                allowed_domains=['win.wwu.edu']
            ),
            URLPatternFilter(
                patterns=[r".*/events$", r".*/event/\d+$"],
            )
        ],
    )
    # Configure a 1-level deep crawl (depth=1 means one level deep)
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=1,
            include_external=False,
            max_pages=50,
            filter_chain = link_filter,
        ),
        extraction_strategy=llm_strategy,
        verbose=True
    )

    async with AsyncWebCrawler() as crawler:
        try:
            results = await crawler.arun("https://win.wwu.edu/events", config=config)

            print(f"Crawled {len(results)} pages in total")

            all_events = [] # currently can have duplicate events. Will need to update after migrating to DB

            # Process the events for each page explored
            for i, result in enumerate(results):
                # debugging
                print(f"\nPage {i+1}:")
                print(f"URL: {result.url}")
                print(f"Depth: {result.metadata.get('depth', 0)}")
                print(f"Success: {result.success}")
                print(f"Contet: {result.extracted_content}")

                if bool(result.success) and result.extracted_content:
                    # format events using pydantic model
                    content = json.loads(result.extracted_content)
                    events_list = content[0]["events"]
                    if events_list:
                        extracted_events = ExtractedEvents(events=events_list)
                        all_events.extend(extracted_events.events)

                    else:
                        print("Did not find events on page")
                else:
                    print("Did not find events on page")

                # Add a small delay to be respectful to the llm
                await asyncio.sleep(1)

            write_to_db(all_events)

            return all_events

        except Exception as e:
            print(f"Error during crawling: {e}")
            traceback.print_exc()
            return []

def write_to_db(all_data):
    # Placeholder for future DB solution
    print("\n" + "="*60)
    print(f"SUMMARY: Found {len(all_data)} total events across all pages")
    print("="*60)

    # Display all events
    if all_data:
        output_table = PrettyTable(["Event Name", "Event Date", "Event Location", "Source URL"])
        for event in all_data:
            output_table.add_row([event.name, event.date, event.location, event.source_url])
        with open(os.path.join("..", LOG_PATH, "events.txt"), "w") as f:
            f.write(output_table.get_string())

        # display names in separate file -- only for testing
        with open(os.path.join("..", LOG_PATH, "names.txt"), "w") as f:
            for event in all_data:
                f.write(f"{event.name}\n")
    else:
        print("No events were extracted from any page.")


if __name__ == "__main__":
    asyncio.run(main())