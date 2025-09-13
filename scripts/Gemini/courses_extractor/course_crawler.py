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
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
# base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10593" # cs

base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=11053" # business

# base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10724" # math
# base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10754" # psych


async def crawl(base_url: str, debug_mode: bool) -> List:
    schema = {
        "name": "class list",
        "baseSelector": "li.acalog-course",
        "fields": [
            {
                "name": "course_name",
                "selector": "span a",
                "type": "text",
            }

        ]
    }
    extraction_strategy = JsonCssExtractionStrategy(schema=schema)
    config = CrawlerRunConfig(extraction_strategy=extraction_strategy)
    b_config = BrowserConfig(headless=(not debug_mode))
    course_list = []
    async with AsyncWebCrawler(config=b_config) as crawler:
        # navigate once to the base URL
        results = await crawler.arun(url=base_url, config=config)
        print(results.extracted_content)
        if not results.extracted_content:
            logger.warning("No courses found")
            return []
        courses = json.loads(results.extracted_content)
        for course in courses:
            if course:
                course_name = course["course_name"].replace("\xa0 - ", "")
                print(course_name)
                course_list.append(course_name)
    return course_list



if __name__ == "__main__":
    asyncio.run(crawl(base_url, debug_mode=True))
