import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, JsonCssExtractionStrategy
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
base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10593" # cs

#base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=11053" # business

# base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10724" # math
# base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10754" # psych


async def crawl(base_url: str, debug_mode: bool) -> List:
    schema = {
        "name": "class list",
        "baseSelector": "body",
        "fields": [
            {
                "name": "course_name",
                "selector": "li.acalog-course span a",
                "type": "text",
            }

        ]
    }
    extraction_strategy = JsonCssExtractionStrategy(schema=schema)
    config = CrawlerRunConfig(extraction_strategy=extraction_strategy)
    b_config = BrowserConfig(headless=(not debug_mode))
    async with AsyncWebCrawler(config=b_config) as crawler:
        # navigate once to the base URL
        results = await crawler.arun(url=base_url, config=config)
        await asyncio.sleep(2)
        print(results.extracted_content)
        if not results.extracted_content:
            logger.warning("No courses found")
            return []
        # for result in results.extracted_content:
        #     print(result)
        with open("psych_courses.html", "w") as f:
            f.write(results.html)

    return []


if __name__ == "__main__":
    asyncio.run(crawl(base_url, debug_mode=True))
