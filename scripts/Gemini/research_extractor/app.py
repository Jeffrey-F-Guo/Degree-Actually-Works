import asyncio
from research_crawler import extract_research_by_department  # move your class into extractor.py

def lambda_handler(event, context):
    department = event.get("department_code", "CSCI")
    return asyncio.run(extract_research_by_department(department))
