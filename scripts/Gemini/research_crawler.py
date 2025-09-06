import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
import json
from crawl4ai import JsonCssExtractionStrategy
import os
from urllib.parse import urljoin, urlparse



async def get_professor_research(url):
    schema = {
        "name": "Professor Page",
        "baseSelector" : "body",
        "fields": [
            {
                "name": "research_interest",
                "selector": "h2.views-label-field-research-interests+p",
                "type": "text",
            },

        ]
    }

    # 2. Create the extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

    # 3. Set up your crawler config (if needed)
    config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, config=config)

        print(f"extracted content: {result.extracted_content}")


async def get_all_professors():
    schema = {
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

    # 2. Create the extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

    # 3. Set up your crawler config (if needed)
    config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://cs.wwu.edu/faculty", config=config)
        BASE_URL = "https://cs.wwu.edu"
        all_pages = []
        pages = json.loads(results.extracted_content)
        for page in pages:
            absolute_url = urljoin(BASE_URL, page["professor_page_url"])
            all_pages.append(absolute_url)
        return all_pages

async def extract_research():
    all_pages = await get_all_professors()
    print(all_pages)
    for page in all_pages:
        await get_professor_research(page)


if __name__ == "__main__":
    asyncio.run(extract_research())