import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, JsonCssExtractionStrategy
import json
import os
from urllib.parse import urljoin, urlparse
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacultyResearchExtractor:
    def __init__(self):
        self.BASE_URLS = {
            "CSCI": "https://cs.wwu.edu"
        }

        self.FACULTY_URLS = {
            "CSCI": "https://cs.wwu.edu/faculty"
        }

    async def extract_faculty_urls(self, department_code:str) -> List[str]:
        """
        Extracts all professor profile URLS from a department's faculty page.

        Args:
            department_name: name of the department to extract professor information from.

        Return:
            List of absolute URLS to individual professor pages.
        """
        if department_code not in self.BASE_URLS or department_code not in self.FACULTY_URLS:
            raise ValueError(f"{department_code} is not a valid department at WWU.")

        schema = self._get_faculty_page_schema()
        extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)
        config = CrawlerRunConfig(
            extraction_strategy=extraction_strategy,
        )

        base_url = self.BASE_URLS["CSCI"]
        faculty_url = self.FACULTY_URLS["CSCI"]

        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(faculty_url, config=config)
            if not results.extracted_content:
                logger.warning(f"No content extracted from {faculty_url}.")
                return []

            all_pages = []
            pages = json.loads(results.extracted_content)
            for page in pages:
                absolute_url = urljoin(base_url, page["professor_page_url"])
                all_pages.append(absolute_url)
            return all_pages

    async def extract_professor_information(self, page_url) -> Dict:
        """
        Extracts all professor information on their profile page. Extracted information includes name, website, and research interests.

        Args:
            page_url: URL to professor's page. This is the page to extract information from.

        Return:
            Dictionary of extracted information.
        """

        schema = self._get_professor_profile_schema()
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

    async def extract_department_research(self, department_code) -> List[dict]:
        """
        Extracts research information and more from all professors in a department.

        Args:
            department_code: Department identifier to extracti info from.

        Return:
            List dictionaries containing all professors' research information.
        """

        faculty_urls = await self.extract_faculty_urls(department_code)
        if not faculty_urls:
            logger.warning(f"No faculty URLs found for department: {department_code}")
            return []

        research_info = []
        for url in faculty_urls:
            professor_info = await self.extract_professor_information(url)
            if professor_info:
                research_info.append(professor_info)
            else:
                logger.warning(f"Could not extract information at: {url}")

        return research_info

    def _get_professor_profile_schema(self) -> Dict:
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
                },
                {
                    "name": "website",
                    "selector": "div.website a",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "research_interest",
                    "selector": "h2.views-label-field-research-interests+p",
                    "type": "text",
                },
            ]
        }

    def _get_faculty_page_schema(self) -> Dict:
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
async def extract_research_by_department(department_code: str) -> None:
    """
    Main function to extract research information for a specific department.

    Args:
        department_code: Department identifier (e.g., 'cs', 'math')

    Returns:
        List of professor research information
    """
    extractor = FacultyResearchExtractor()
    research_data = await extractor.extract_department_research(department_code)
    print(research_data)
    return

if __name__ == "__main__":
    asyncio.run(extract_research_by_department("CSCI"))