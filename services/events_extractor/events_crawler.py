import asyncio
import os
import logging
import csv
import sys
import re
from bs4 import BeautifulSoup

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_utils.csv_writer import csv_writer
from shared_utils.llm_init import llm_init
import events_extractor.config as config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class EventEntry(BaseModel):
    event_name: str
    date: str
    page_url: str

class ExtractedEvents(BaseModel):
    events: List[EventEntry] = Field(default_factory=list, description="A list of events with their details.")

def prefilter_html(html: str) -> str:
    """
    Extract only event-related content from the HTML to reduce size for LLM processing.
    This significantly reduces the HTML size by keeping only event cards and essential structure.
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Find the event discovery list container
        event_list = soup.find('div', id='event-discovery-list')
        if not event_list:
            # Fallback: look for MuiCard-root elements
            event_cards = soup.find_all('div', class_=re.compile(r'MuiCard-root'))
            if event_cards:
                # Create a minimal container with just the event cards
                filtered_html = f"""
                <div id="event-discovery-list">
                    <div style="display: flex; flex-wrap: wrap; margin: -10px">
                        {''.join(str(card) for card in event_cards)}
                    </div>
                </div>
                """
                return filtered_html
            else:
                logger.warning("No event cards found in HTML")
                return html

        logger.info(f"HTML pre-filtered: {len(html)} -> {len(filtered_html)} characters ({len(filtered_html)/len(html)*100:.1f}% reduction)")
        return str(event_list)

    except Exception as e:
        logger.error(f"Error pre-filtering HTML: {e}")
        return html

async def save_html(html: str, filename: str):
    with open(filename, "w") as f:
        f.write(html)

async def crawl_events(base_url: str, debug_mode: bool = False) -> List[EventEntry]:
    prev_page_len = 0
    cur_page_len = 0

    browser_config_dict = config.get_browser_config(debug_mode)
    b_config = BrowserConfig(**browser_config_dict)

    async with AsyncWebCrawler(config=b_config) as crawler:
        # create a persistent session
        crawler_config_dict = config.get_crawler_config()
        crawler_config = CrawlerRunConfig(**crawler_config_dict)

        # navigate once to the base URL
        await crawler.arun(url=base_url, config=CrawlerRunConfig(session_id=crawler_config_dict["session_id"]))

        while True:
            # execute JS without reloading the page
            results = await crawler.arun(url=base_url, config=crawler_config)
            await asyncio.sleep(2)
            await save_html(results.html, "events.html")
            await save_html(results.markdown, "events.markdown")
            cur_page_len = len(results.html)
            # debugging check
            print("Page length:", cur_page_len)

            if cur_page_len == prev_page_len:
                break
            else:
                prev_page_len = cur_page_len

        results = await crawler.arun(url=base_url, config=crawler_config)

        try:
            prompt_template = ChatPromptTemplate.from_messages(config.get_llm_prompt())
            extraction_chain = llm_init(prompt_template, ExtractedEvents, model="gemini-2.5-flash")
            # debugging check
            logger.info("invoke llm")
            output = extraction_chain.invoke({"html": results.html})
            if output and output.events:
                events_list = [event.model_dump() for event in output.events]
            else:
                events_list = []
        except Exception as e:
            logger.error(f"Error extracting events: {e}")
            return []

        if not events_list:
            logger.warning("Did not find any events")
            return []

        return events_list


async def extract_events(base_url: str, debug_mode: bool = False):
    events_list = await crawl_events(base_url, debug_mode)
    # events_list = await dummy_test()
    if events_list:
        csv_writer(events_list, "events.csv")
    return events_list


if __name__ == "__main__":
    asyncio.run(extract_events(config.get_base_url(), debug_mode=True))
