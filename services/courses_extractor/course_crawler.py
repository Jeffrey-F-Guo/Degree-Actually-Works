import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List, Dict
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.csv_writer import csv_writer
import config

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

def init_llm( prompt_template, model="gemini-2.5-flash", model_provider="google-genai"):
    llm = init_chat_model(model=model, model_provider=model_provider)
    structured_llm = llm.with_structured_output(courseInfoList)
    llm_chain = prompt_template | structured_llm

    return llm_chain

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
    course_list = []
    async with AsyncWebCrawler(config=b_config) as crawler:
        # navigate once to the base URL
        results = await crawler.arun(url=base_url, config=crawler_config)
        llm = init_llm(prompt_template)
        print("invoking")
        courses = llm.invoke({"markdown": results.markdown})
        if not courses:
            logger.warning("No courses found")
            return []
        for course in courses.info_list:
            course_info = course.model_dump()
            course_list.append(course_info)
    return course_list

async def extract_course(department_code: str, debug_mode: bool=False):
    course_info = await crawl_courses(department_code, debug_mode)
    if course_info:
        csv_writer(course_info, "courses.csv")


if __name__ == "__main__":
    asyncio.run(extract_course("CSCI", debug_mode=True))
