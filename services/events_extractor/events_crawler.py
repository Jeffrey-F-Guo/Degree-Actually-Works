import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List, Dict
import logging
import csv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.csv_writer import csv_writer
import config

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
        model = init_chat_model("gemini-2.5-flash", model_provider="google-genai")

        summary_llm = model.with_structured_output(ExtractedEvents)
        prompt_template = ChatPromptTemplate.from_messages(config.get_llm_prompt())
        extraction_chain = prompt_template | summary_llm
        logger.info("invoke llm")
        output = extraction_chain.invoke({"html": results.html})
        if not output:
            logger.warning("Did not extract any events")
            return []

        events_list = []
        for event in output.events:
            events_list.append(event.model_dump())

        return events_list


async def extract_events(base_url: str, debug_mode: bool = False):
    events_list = await crawl_events(base_url, debug_mode)
    if events_list:
        csv_writer(events_list, "events.csv")

if __name__ == "__main__":
    asyncio.run(extract_events(config.get_base_url(), debug_mode=True))
