import asyncio
import os
import logging
import csv
import sys

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
            cur_page_len = len(results.markdown)
            # debugging check
            print("Page length:", cur_page_len)

            # TODO: replace with more consistent stop condition
            if cur_page_len == prev_page_len:
                break
            else:
                prev_page_len = cur_page_len

        results = await crawler.arun(url=base_url, config=crawler_config)

        try:
            prompt_template = ChatPromptTemplate.from_messages(config.get_llm_prompt())
            extraction_chain = llm_init(prompt_template, ExtractedEvents)
            # debugging check
            logger.info("invoke llm")
            output = extraction_chain.invoke({"html": results.html})
        except Exception as e:
            logger.error(f"Error extracting events: {e}")
            return []

        if not output:
            logger.warning("Did not find any events")
            return []

        events_list = []
        for event in output.events:
            events_list.append(event.model_dump())

        return events_list


async def extract_events(base_url: str, debug_mode: bool = False):
    events_list = await crawl_events(base_url, debug_mode)
    if events_list:
        csv_writer(events_list, "events.csv")
    return events_list

if __name__ == "__main__":
    asyncio.run(extract_events(config.get_base_url(), debug_mode=True))
