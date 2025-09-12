import asyncio
from crawl4ai import AsyncWebCrawler
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List
from datetime import date

load_dotenv()


async def crawl():
    # Create an instance of AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        # Run the crawler on a URL
        result = await crawler.arun(url="https://mathematics.wwu.edu/people/bergeta")

        # Print the extracted content
        with open("math_prof.html", "w") as f:
            f.write(result.html)
    return result

# Run the async main function
result = asyncio.run(crawl())

