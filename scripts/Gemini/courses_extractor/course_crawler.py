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
# base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10593" # cs

#base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=11053" # business

base_url = "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10724" # math

async def crawl(base_url: str) -> List:
    b_config = BrowserConfig(headless=False)
    async with AsyncWebCrawler(config=b_config) as crawler:
        # navigate once to the base URL
        results = await crawler.arun(url=base_url)
        with open("math_courses.html", "w") as f:
            f.write(results.html)

        print(results.markdown)

    return []


if __name__ == "__main__":
    asyncio.run(crawl(base_url))
