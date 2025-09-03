import asyncio
from crawl4ai import AsyncWebCrawler
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List, Set
import re
from urllib.parse import urljoin, urlparse
import logging
from prettytable import PrettyTable
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class EventEntry(BaseModel):
    event_name: str
    event_date: str
    location: str
    source_url: str = Field(default="", description="URL where the event was found")


class ExtractedEvents(BaseModel):
    events: List[EventEntry] = Field(..., description="A list of events with their details.")


def extract_links(markdown_content: str, base_url: str) -> Set[str]:
    """Extract links from markdown content and convert them to absolute URLs."""
    links = set()

    # Pattern to match markdown links: [text](url)
    markdown_link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(markdown_link_pattern, markdown_content)

    for text, url in matches:
        # Convert relative URLs to absolute URLs
        absolute_url = urljoin(base_url, url)

        # Only include links from the same domain (to avoid external links)
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(absolute_url).netloc

        if base_domain == link_domain:
            links.add(absolute_url)

    return links


async def crawl_deep(base_url: str, max_links: int = 10) -> List[tuple]:
    """
    Crawl the base URL and then crawl linked pages one level deep.

    Args:
        base_url: The starting URL to crawl
        max_links: Maximum number of links to follow (to avoid overwhelming the server)

    Returns:
        List of tuples containing (url, markdown_content)
    """
    crawled_content = []

    async with AsyncWebCrawler(verbose=True) as crawler:
        logger.info(f"Crawling base URL: {base_url}")

        # First, crawl the main page
        try:
            result = await crawler.arun(url=base_url)
            crawled_content.append((base_url, result.markdown))
            logger.info(f"Successfully crawled base URL")

            # Extract links from the main page
            links = extract_links(result.markdown, base_url)
            logger.info(f"Found {len(links)} links on base page")

            # Limit the number of links to crawl
            links_to_crawl = list(event_links)[:max_links]

            # Crawl each linked page
            for i, link in enumerate(links_to_crawl, 1):
                try:
                    logger.info(f"Crawling link {i}/{len(links_to_crawl)}: {link}")
                    link_result = await crawler.arun(url=link)
                    crawled_content.append((link, link_result.markdown))
                    logger.info(f"Successfully crawled: {link}")

                    # Add a small delay to be respectful to the server
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"Failed to crawl {link}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Failed to crawl base URL {base_url}: {str(e)}")
            return crawled_content

    return crawled_content


async def extract_events_from_content(crawled_content: List[tuple]) -> ExtractedEvents:
    """Extract events from all crawled content using LLM."""

    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
    summary_llm = model.with_structured_output(ExtractedEvents)

    all_events = []

    for url, markdown_content in crawled_content:
        logger.info(f"Extracting events from: {url}")

        try:
            # Add URL context to the content
            content_with_source = f"Source URL: {url}\n\n{markdown_content}"

            output = summary_llm.invoke([
                {
                    "role": "system",
                    "content": """Your role is to extract event information from markdown content.
                    Given markdown content from a webpage, extract and return a list of events.
                    Each event should have the following fields:

                    - event_name: The name/title of the event
                    - event_date: The date and time of the event (keep original format)
                    - location: Where the event is taking place
                    - source_url: The URL where this event information was found

                    If no events are found, return an empty list.
                    Be thorough and look for any event-related information including:
                    - Scheduled events, meetings, workshops
                    - Performances, lectures, seminars
                    - Social activities, sports events
                    - Academic events, deadlines
                    """
                },
                {
                    "role": "user",
                    "content": content_with_source
                }
            ])

            # Add source URL to each event if not already present
            for event in output.events:
                if not event.source_url:
                    event.source_url = url

            all_events.extend(output.events)
            logger.info(f"Found {len(output.events)} events from {url}")

        except Exception as e:
            logger.error(f"Failed to extract events from {url}: {str(e)}")
            continue

    return ExtractedEvents(events=all_events)


async def main():
    """Main function to run the deep crawling and event extraction."""
    base_url = "https://win.wwu.edu/events"

    logger.info("Starting deep crawl...")

    # Perform deep crawling
    crawled_content = await crawl_deep(base_url, max_links=10)
    logger.info(f"Crawled {len(crawled_content)} pages total")

    if not crawled_content:
        logger.error("No content was crawled successfully")
        return

    # Extract events from all crawled content
    logger.info("Extracting events from all crawled content...")
    all_events = await extract_events_from_content(crawled_content)

    # Print results
    print(f"\n=== CRAWLING SUMMARY ===")
    print(f"Pages crawled: {len(crawled_content)}")
    print(f"Total events found: {len(all_events.events)}")

    table = PrettyTable(["event_number", "name", "date", "location", "source_url"])

    for i, event in enumerate(all_events.events):
        table.add_row(i, event.event_name, event.event_date, event.location, event.source_url)

    with open("events.txt", "w") as f:
        f.write(table.get_string())

    return all_events


if __name__ == "__main__":
    # Run the async main function
    result = asyncio.run(main())