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
import courses_extractor.config as config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class courseInfo(BaseModel):
    course_name:str = Field(..., description="Name of the course")
    course_description: str = Field(..., description="Description of the course")
    prereqs: str = Field("", description="Prerequisites of the course")
    credits: int = Field(-1, description="Number of credits the course is worth")

class courseInfoList(BaseModel):
    info_list: List[courseInfo] = Field(..., description="List of course information")

async def prefilter_markdown(markdown: str) -> str:
    """
    Pre-filter the markdown to remove unnecessary content.
    """
    if not markdown:
        logger.error("No markdown found")
        return []
    courses = markdown.split("### Grade Requirements")
    # Remove initial major blurb
    if len(courses) < 2:
        logger.warning("Unexpected course page format")
        return [markdown]

    reqs = courses[1]
    pattern = r"(###.*?---)"
    matches = re.findall(pattern, reqs, flags=re.DOTALL)

    course_list = []
    for match in matches:
        course_list.append(match.strip())

    return course_list

async def crawl_courses(department_code: str, debug_mode: bool) -> List:
    base_urls = config.get_base_urls()
    if department_code not in base_urls:
        raise ValueError(f"{department_code} is not a valid department at WWU.")

    prompt_template = ChatPromptTemplate.from_messages(config.get_llm_prompt())

    crawler_config_dict = config.get_crawler_config()
    crawler_config = CrawlerRunConfig(**crawler_config_dict)

    base_url = base_urls[department_code]
    browser_config_dict = config.get_browser_config(debug_mode)
    b_config = BrowserConfig(**browser_config_dict)

    # List of courses to return
    course_list = []
    async with AsyncWebCrawler(config=b_config) as crawler:
        # navigate once to the base URL
        results = await crawler.arun(url=base_url, config=crawler_config)
        markdown_list = await prefilter_markdown(results.markdown)
        if not markdown_list:
            return []
        try:
            llm = llm_init(prompt_template, courseInfo)
            logger.info("invoking")
            for entry in markdown_list:
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
