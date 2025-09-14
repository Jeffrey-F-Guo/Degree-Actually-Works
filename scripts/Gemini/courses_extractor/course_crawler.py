import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import List, Dict
import logging
import json
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

BASE_URLS = {
    "CSCI": "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10593",
    "MATH": "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10724",
    "PSYCH": "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10754",
    "BUS": "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=11053",

}

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
    if department_code not in BASE_URLS:
        raise ValueError(f"{department_code} is not a valid department at WWU.")

    js_commands = [
        """
        async function expandAllCourses() {
            const links = document.querySelectorAll('li.acalog-course span a[onclick*="showCourse"]');
            for (let i = 0; i < links.length; i++) {
                links[i].click();
            }
        }

        expandAllCourses();
        """
    ]

    prompt_template = ChatPromptTemplate.from_messages([
        {
            "role": "system",
            "content": """Your role is to extract information from a markdown file.
                    Given a markdown file, extract and return a list of courses. Each course should have the following fields:

                        course_name: str
                        course_description: str
                        course_prereqs: str
                        course_credits: int
            """
        },
        {
            "role": "user",
            "content": "{markdown}"
        }
    ])
    config = CrawlerRunConfig(
        js_code=js_commands,
        delay_before_return_html=30.0  # Wait for all expansions to complete
    )

    base_url = BASE_URLS[department_code]
    b_config = BrowserConfig(headless=(not debug_mode))
    course_list = []
    async with AsyncWebCrawler(config=b_config) as crawler:
        # navigate once to the base URL
        results = await crawler.arun(url=base_url, config=config)
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

def write_to_csv(course_data: List[Dict], filename: str = "courses.csv"):
        """
        Writes extracted research information to a CSV file.

        Args:
            research_data: List of dictionaries containing professor info.
            filename: Name of the CSV file to write to.
        """
        if not course_data:
            logger.warning("No course data to write.")
            return

        # Determine the CSV headers from keys of the first dictionary
        headers = course_data[0].keys()
        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                for row in course_data:
                    writer.writerow(row)
            logger.info(f"Research data written to {filename}")
        except Exception as e:
            logger.error(f"Failed to write CSV: {e}")

async def extract_course(department_code: str, debug_mode: bool=False):
    course_info = await crawl_courses(department_code, debug_mode)
    if course_info:
        write_to_csv(course_info)


if __name__ == "__main__":
    asyncio.run(extract_course("CSCI", debug_mode=True))
