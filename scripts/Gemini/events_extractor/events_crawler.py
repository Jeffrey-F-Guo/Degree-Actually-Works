import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List
import logging
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
base_url = "https://win.wwu.edu/events/?categories=9821&categories=17934&categories=21914&categories=9822&categories=11780&categories=23412&categories=9830"

load_dotenv()


prompt_template = ChatPromptTemplate.from_messages([
    {
        "role": "system",
        "content": """Your role is to extract information from a markdown file.
                Given a markdown file, extract and return a list of events. Each event should have the following fields:

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
    events: List[EventEntry] = Field(..., description="A list of events with their details.")


async def crawl(base_url: str) -> List[EventEntry]:
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
            js_only=True,
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

            # TODO: replace with your real stop condition
            if cur_page_len == prev_page_len:
                break
            else:
                prev_page_len = cur_page_len


        results = await crawler.arun(url=base_url, config=config)
        model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

        summary_llm = model.with_structured_output(ExtractedEvents)

        extraction_chain = prompt_template | summary_llm
        output = extraction_chain.invoke({"html": results.html})

        print(output)
        print(f"output len is {len(output.events)}")

        write_research_to_csv(output.events)

    return []

def write_research_to_csv(event_data: List[EventEntry], filename: str = "events.csv"):
        """
        Writes extracted research information to a CSV file.

        Args:
            research_data: List of dictionaries containing professor info.
            filename: Name of the CSV file to write to.
        """
        if not event_data:
            logger.warning("No research data to write.")
            return

        # Determine the CSV headers from keys of the first dictionary
        headers = event_data[0].model_dump().keys()

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                for entry in event_data:
                    row = entry.model_dump()
                    writer.writerow(row)
            logger.info(f"Research data written to {filename}")
        except Exception as e:
            logger.error(f"Failed to write CSV: {e}")



def filter_events():
    """
    Filters out events that have already happened
    """
    pass
if __name__ == "__main__":
    asyncio.run(crawl(base_url))
