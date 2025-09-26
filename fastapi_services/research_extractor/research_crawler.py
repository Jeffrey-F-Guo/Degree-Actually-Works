import asyncio
import json
import os
import logging

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, JsonCssExtractionStrategy, BrowserConfig
from urllib.parse import urljoin, urlparse
from typing import List, Dict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_utils.csv_writer import csv_writer
from shared_utils.llm_init import llm_init
from shared_utils.llm_batch_processor import llm_ainvoke_batch
import research_extractor.config as config
from shared_utils.db_writer import write_to_db


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProfessorPage(BaseModel):
    name: str = Field(..., description="Professor's name")
    website: str = Field("N/A", description="Professor's personal website")
    research_interest: List[str] = Field(default_factory=list, description="List of professor's research interests")
    src_url: str = Field(..., description="Source URL of the professor's page")

async def extract_faculty_urls(department_code:str, debug_mode: bool=False) -> List[str]:
    """
    Extracts all professor profile URLS from a department's faculty page.

    Args:
        department_name: name of the department to extract professor information from.

    Return:
        List of absolute URLS to individual professor pages.
    """
    logger.info("Extracting faculty urls.")
    base_urls = config.get_base_urls()
    faculty_urls = config.get_faculty_urls()

    if department_code not in base_urls or department_code not in faculty_urls:
        raise ValueError(f"{department_code} is not a valid department at WWU.")

    # config crawler
    browser_config = BrowserConfig(headless=(not debug_mode))
    schema = config.get_faculty_page_schema()
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    crawler_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
    )

    # Select url paths by department
    base_url = base_urls[department_code]
    faculty_url = faculty_urls[department_code]

    # Run crawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun(faculty_url, config=crawler_config)
        if not results.extracted_content:
            logger.warning(f"No content extracted from {faculty_url}.")
            return []

        all_pages = set()
        pages = json.loads(results.extracted_content)
        for page in pages:
            # Crawled page provides relative urls like '/wolterp'. Join the base url to create an absolute url
            absolute_url = urljoin(base_url, page["professor_page_url"])
            all_pages.add(absolute_url)
        return list(all_pages)


async def extract_professor_information(url_list: List, debug_mode: bool=False) -> List[dict]:
    """
    Extract professor information from a list of URLs using async processing.
    
    Args:
        url_list: List of professor page URLs to process
        debug_mode: Whether to run in debug mode (non-headless browser)
        
    Returns:
        List of processed professor information dictionaries
    """
    logger.info(f"Starting extraction for {len(url_list)} professor URLs")
    
    prompt_template = ChatPromptTemplate.from_messages(config.get_llm_prompt())
    llm_chain = llm_init(prompt_template, ProfessorPage, model="gemini-2.5-flash-lite", model_provider="google-genai")
    browser_config = BrowserConfig(headless= (not debug_mode))

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            # returns a list of crawlerrun objects
            logger.info("Starting concurrent web crawling...")
            professor_info_list = await crawler.arun_many(url_list)
            logger.info(f"Completed crawling {len(professor_info_list)} pages")

            
            # Process all LLM calls concurrently
            if professor_info_list:
                research_info = await llm_ainvoke_batch(
                    llm_chain, 
                    professor_info_list, 
                    max_concurrent=5 
                )
                logger.info(f"Successfully processed {len(research_info)} professor profiles")
            else:
                logger.warning("No markdown content found for LLM processing")
                research_info = []
                
    except Exception as e:
        logger.error(f"Error during professor information extraction: {e}")
        research_info = []
            
    return research_info

async def extract_department_research(department_code, debug_mode=False) -> List[dict]:
    """
    Extracts research information and more from all professors in a department.

    Args:
        department_code: Department identifier to extracti info from.

    Return:
        List dictionaries containing all professors' research information.
    """

    faculty_urls = await extract_faculty_urls(department_code, debug_mode=debug_mode)
    if not faculty_urls:
        logger.warning(f"No faculty URLs found for department: {department_code}")
        return []

    research_info = await extract_professor_information(faculty_urls, debug_mode=debug_mode)
    return research_info


# 'public' wrapper. Other files import this function
async def extract_research_by_department(department_code: str, debug_mode: bool=False, write_to_csv: bool = False) -> None:
    """
    Main function to extract research information for a specific department.

    Args:
        department_code: Department identifier (e.g., 'cs', 'math')

    Returns:
        List of professor research information
    """

    research_info = await extract_department_research(department_code, debug_mode)
    write_to_db(research_info)
    if research_info and write_to_csv:
        csv_writer(research_info, f"research_{department_code}.csv")
    return research_info

if __name__ == "__main__":
    asyncio.run(extract_research_by_department("CSCI", debug_mode=False, write_to_csv=True))
