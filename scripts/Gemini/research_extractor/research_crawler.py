import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, JsonCssExtractionStrategy, BrowserConfig
import json
import os
from urllib.parse import urljoin, urlparse
from typing import List, Dict
import logging
import csv
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# base path for all professor pages by department
BASE_URLS = {
    "CSCI": "https://cs.wwu.edu",
    "BIO": "https://biology.wwu.edu/people",
}

# main faculty page for each department
FACULTY_URLS = {
    "CSCI": "https://cs.wwu.edu/faculty",
    "BIO": "https://biology.wwu.edu/directory/faculty",
}

async def extract_faculty_urls(department_code:str, debug_mode: bool=False) -> List[str]:
    """
    Extracts all professor profile URLS from a department's faculty page.

    Args:
        department_name: name of the department to extract professor information from.

    Return:
        List of absolute URLS to individual professor pages.
    """
    logger.info("Extracting faculty urls.")
    if department_code not in BASE_URLS or department_code not in FACULTY_URLS:
        raise ValueError(f"{department_code} is not a valid department at WWU.")

    # config crawler
    browser_config = BrowserConfig(headless=(not debug_mode))
    schema = _get_faculty_page_schema()
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
    )

    # Select url paths by department
    base_url = BASE_URLS[department_code]
    faculty_url = FACULTY_URLS[department_code]

    # Run crawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun(faculty_url, config=config)
        if not results.extracted_content:
            logger.warning(f"No content extracted from {faculty_url}.")
            return []

        all_pages = []
        pages = json.loads(results.extracted_content)
        for page in pages:
            # Crawled page provides relative urls like '/wolterp'. Join the base url to create an absolute url
            absolute_url = urljoin(base_url, page["professor_page_url"])
            all_pages.append(absolute_url)
        return all_pages

async def extract_professor_information(page_url: str) -> Dict:
    """
    Extracts all professor information on their profile page. Extracted information includes name, website, and research interests.

    Args:
        page_url: URL to professor's page. This is the page to extract information from.

    Return:
        Dictionary of extracted information.
    """
    logger.info("Extracting professor information.")
    schema = _get_professor_profile_schema()
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(page_url, config=config)
        if result.extracted_content:
            professor_data = json.loads(result.extracted_content)
            if professor_data:
                professor_data[0]["prof_url"] = page_url
                return professor_data[0]

        return None

async def extract_multiple_professor_information(url_list: List, debug_mode: bool=False):
    browser_config = BrowserConfig(headless= (not debug_mode))
    schema = _get_professor_profile_schema()
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
    config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
    )
    research_info = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        professor_info_list = await crawler.arun_many(url_list, config=config)
        for i, professor_info in enumerate(professor_info_list):
            if professor_info.extracted_content:
                professor_data = json.loads(professor_info.extracted_content)
                if professor_data:
                    professor_data[0]["src_url"] = url_list[i]
                    research_info.append(professor_data[0])
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

    research_info = await extract_multiple_professor_information(faculty_urls, debug_mode=debug_mode)
    return research_info

def write_research_to_csv(research_data: List[Dict], department_code: str):
    """
    Writes extracted research information to a CSV file.

    Args:
        research_data: List of dictionaries containing professor info.
        filename: Name of the CSV file to write to.
    """
    if not research_data:
        logger.warning("No research data to write.")
        return

    # Determine the CSV headers from keys of the first dictionary
    headers = research_data[0].keys()

    try:
        filename = f"{department_code}.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in research_data:
                writer.writerow(row)
        logger.info(f"Research data written to {filename}")
    except Exception as e:
        logger.error(f"Failed to write CSV: {e}")

# TODO: doesnt work universally for professor pages across all departments, only CSCI
def _get_professor_profile_schema() -> Dict:
    """
    CSS extraction schema for extracting professor information from professor profile pages.
    """
    return {
        "name": "Professor Page",
        "baseSelector" : "body",
        "fields": [
            {
                "name": "professor_name",
                "selector": "h1.field-content",
                "type": "text",
                "default": "None"
            },
            {
                "name": "website",
                "selector": "div.website a",
                "type": "attribute",
                "attribute": "href",
                "default": "None"
            },
            {
                "name": "research_interest",
                "selector": "h2.views-label-field-research-interests+p",
                "type": "text",
                "default": "None"
            },
        ]
    }

def _get_faculty_page_schema() -> Dict:
    """
    CSS extraction schema for extracting professor pages from the base faculty page.
    """
    return {
        "name": "Faculty Page",
        "baseSelector": "div.card",
        "fields": [
            {
                "name": "professor_page_url",
                "selector": "a",
                "type": "attribute",
                "attribute": "href"
            },
        ]
    }


# Usage functions
async def extract_research_by_department(department_code: str, debug_mode: bool=False, write_to_csv: bool = False) -> None:
    """
    Main function to extract research information for a specific department.

    Args:
        department_code: Department identifier (e.g., 'cs', 'math')

    Returns:
        List of professor research information
    """

    research_info = await extract_department_research(department_code, debug_mode)
    if research_info and write_to_csv:
        write_research_to_csv(research_info, department_code)
    return research_info

if __name__ == "__main__":
    asyncio.run(extract_research_by_department("BIO", debug_mode=True, write_to_csv=True))