import asyncio
import os
import logging
import csv
import re
from bs4 import BeautifulSoup

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict
from urllib.parse import urljoin, urlparse


from shared_utils import csv_writer
from shared_utils import llm_init
from events_extractor import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class EventEntry(BaseModel):
    event_name: str = Field(..., description="Name of the event")
    date: str = Field(..., description="Date the event is planned for")
    page_url: str = Field(..., description="url of the event page")

def prefilter_html(html: str) -> list[str]:
    """
    Extract only event-related content from the HTML to reduce size for LLM processing.
    This significantly reduces the HTML size by keeping only event cards and essential structure.
    """
    if not html:
        return []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        event_list = (soup.select('a:has(div.MuiCard-root)'))
        if event_list:
            return event_list
        
        # Fallback: look for the  event list container
        logger.warning("html prefilter did not find event cards. Defaulting to event list container.")
        event_container = list(soup.find('div', id='event-discovery-list'))
        return event_container if event_container else [html]

    except Exception as e:
        logger.error(f"Error pre-filtering HTML: {e}")
        return [html]

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
            await asyncio.sleep(5)
            cur_page_len = len(results.html)
            # debugging check
            print("Page length:", cur_page_len)

            if cur_page_len == prev_page_len:
                break
            else:
                prev_page_len = cur_page_len

        results = await crawler.arun(url=base_url, config=crawler_config)
        filtered_html_list = prefilter_html(results.html)
        
        events_list = []
        try:
            prompt_template = ChatPromptTemplate.from_messages(config.get_llm_prompt())
            extraction_chain = llm_init(prompt_template, EventEntry, "gemini-2.5-flash-lite", "google-genai")
            for html in filtered_html_list:
                # debugging check
                logger.info("Extracting event information")
                output = extraction_chain.invoke({"html": html})
                event = output.model_dump()
                event["page_url"] = urljoin(config.get_base_url(), event["page_url"])
                events_list.append(event)

        except Exception as e:
            logger.error(f"Error extracting events: {e}")
            return []

        if not events_list:
            logger.warning("Did not find any events")
            return []

        return events_list


async def extract_events(base_url: str, debug_mode: bool = False):
    events_list = await crawl_events(base_url, debug_mode)
    if events_list:
        csv_writer(events_list, "events.csv")
    return events_list


if __name__ == "__main__":
    asyncio.run(extract_events(config.get_base_url(), debug_mode=True))
