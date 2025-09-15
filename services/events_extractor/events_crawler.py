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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
base_url = "https://win.wwu.edu/events/?categories=9821&categories=17934&categories=21914&categories=9822&categories=11780&categories=23412&categories=9830"



prompt_template = ChatPromptTemplate.from_messages([
    {
        "role": "system",
        "content": """Your role is to extract information from a html file.
                Given a html file, extract and return a list of events. Each event should have the following fields:

                    event_name: str
                    date: str
                    page_url: str
        """
    },
    {
        "role": "user",
        "content": "{html}"
    }
])

class EventEntry(BaseModel):
    event_name: str
    date: str
    page_url: str

class ExtractedEvents(BaseModel):
    events: List[EventEntry] = Field(default_factory=list, description="A list of events with their details.")


async def crawl_events(base_url: str) -> List[EventEntry]:
    js_commands = [
        "window.scrollTo(0, document.body.scrollHeight);",
        "Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Load More'))?.click();"
    ]
    prev_page_len = 0
    cur_page_len = 0

    b_config = BrowserConfig(headless=False)
    async with AsyncWebCrawler(config=b_config) as crawler:
        # create a persistent session
        session_id = "base_event_page_session"
        config = CrawlerRunConfig(
            js_code=js_commands,
            js_only=True, # ensures browser window doesnt reload
            session_id=session_id  # ensures same tab
        )

        # navigate once to the base URL
        await crawler.arun(url=base_url, config=CrawlerRunConfig(session_id=session_id))


        while True:
            # execute JS without reloading the page
            results = await crawler.arun(url=base_url, config=config)
            await asyncio.sleep(2)

            cur_page_len = len(results.markdown)
            # debugging check
            print("Page length:", cur_page_len)

            # TODO: replace with more consistent stop condition
            if cur_page_len == prev_page_len:
                break
            else:
                prev_page_len = cur_page_len


        results = await crawler.arun(url=base_url, config=config)
        model = init_chat_model("gemini-2.5-flash", model_provider="google-genai")

        summary_llm = model.with_structured_output(ExtractedEvents)

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


async def extract_events(base_url: str):
    events_list = await crawl_events(base_url)
    if events_list:
        csv_writer(events_list, "events.csv")

if __name__ == "__main__":
    asyncio.run(extract_events(base_url))
