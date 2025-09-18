import asyncio
import os
import logging

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
    courses = markdown.split("### Grade Requirements")
    if len(courses) > 1:
        return courses[1]
        # course_reqs = courses[1].split("###  Electives")
        # if len(course_reqs) > 1:
        #     return (course_reqs[0], course_reqs[1])
        # else:
        #     logger.warning("No electives found in markdown")
        #     return markdown
    else:
        logger.warning("Unexpected course format")
        return markdown

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
    async with AsyncWebCrawler(config=b_config) as crawler:
        # navigate once to the base URL
        results = await crawler.arun(url=base_url, config=crawler_config)
        core_courses = await prefilter_markdown(results.markdown)
        try:
            llm = llm_init(prompt_template, courseInfoList)
            logger.info("invoking")
            courses = llm.invoke({"markdown": core_courses})
        except Exception as e:
            logger.error(f"LLM error extracting courses: {e}")
            return []

        if courses and courses.info_list:
            course_list = [course.model_dump() for course in courses.info_list]
        else:
            course_list = []

    return course_list

async def extract_course(department_code: str, debug_mode: bool=False):
    course_info = await crawl_courses(department_code, debug_mode)
    if course_info:
        csv_writer(course_info, f"{department_code}_courses.csv")
    return course_info


if __name__ == "__main__":
    asyncio.run(extract_course("CSCI", debug_mode=True))
