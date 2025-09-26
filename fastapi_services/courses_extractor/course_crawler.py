import asyncio
import os
import logging
import re

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_utils.csv_writer import csv_writer
from shared_utils.llm_init import llm_init
from shared_utils.db_writer import write_to_db
from shared_utils.llm_batch_processor import llm_ainvoke_batch
import courses_extractor.config as config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class courseInfo(BaseModel):
    course_name:str = Field(..., description="Name of the course")
    course_description: str = Field(..., description="Description of the course")
    prereqs: str = Field("", description="Prerequisites of the course")
    credits: int = Field(-1, description="Number of credits the course is worth")


async def prefilter_markdown(markdown: str) -> list[str]:
    """
    Pre-filter the markdown to remove unnecessary content.
    """
    if not markdown:
        logger.error("No markdown found")
        return []
    try:
        courses = markdown.split("### Grade Requirements")
        # Remove initial major blurb
        if len(courses) < 2:
            logger.warning("Unexpected course page format")
            return [markdown]

        reqs = courses[1]

        # Match all patterns starting with ### and ending with ---
        # Pattern matching is non-greedy via '?'. Each individual record will be matched.
        pattern = r"(###.*?---)"
        matches = re.findall(pattern, reqs, flags=re.DOTALL)
        if not matches:
            return [markdown]
        course_list = []
        for match in matches:
            course_list.append(match.strip())

        return course_list
    except Exception as e:
        logger.error("Course markdown not in expected format. Returning entire markdown file")
        return [markdown]


async def crawl_courses(department_code: str, debug_mode: bool) -> List:
    # Retrieve url to scrape
    base_urls = config.get_base_urls()
    if department_code not in base_urls:
        raise ValueError(f"{department_code} is not a valid department at WWU.")
    base_url = base_urls[department_code]

    # Configs
    prompt_template = ChatPromptTemplate.from_messages(config.get_llm_prompt())
    crawler_config_dict = config.get_crawler_config()
    crawler_config = CrawlerRunConfig(**crawler_config_dict)
    browser_config_dict = config.get_browser_config(debug_mode)
    b_config = BrowserConfig(**browser_config_dict)

    # List of courses to return
    course_list = []

    # Start crawl
    async with AsyncWebCrawler(config=b_config) as crawler:
        results = await crawler.arun(url=base_url, config=crawler_config)
        markdown_list = await prefilter_markdown(results.markdown)
        if not markdown_list:
            return []
        try:
            llm = llm_init(prompt_template, courseInfo, "gemini-2.5-flash-lite", "google-genai")
            for entry in markdown_list:
                logger.info("invoking markdown extraction")
                course = llm.invoke({"markdown": entry})
                course_list.append(course.model_dump())

        except Exception as e:
            logger.error(f"LLM error extracting courses: {e}")
            return []

    return course_list

async def extract_course(department_code: str, debug_mode: bool=False):
    course_info = await crawl_courses(department_code, debug_mode)
    if course_info:
        csv_writer(course_info, f"{department_code}_courses.csv")
    return course_info


if __name__ == "__main__":
    asyncio.run(extract_course("CSCI", debug_mode=True))
