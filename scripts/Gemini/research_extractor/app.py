from fastapi import FastAPI, HTTPException
from research_crawler import FacultyResearchExtractor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI app instance
app = FastAPI(
    title="Faculty Research Extractor API",
    description="An API to scrape faculty research interests from university websites.",
    version="1.0.0"
)

# Create a single, reusable instance of your extractor
extractor = FacultyResearchExtractor()

@app.get("/")
async def read_root():
    """
    Root endpoint with a welcome message.
    """
    return {"message": "Welcome to the Faculty Research Extractor API!"}


@app.get("/extract/{department_code}")
async def extract_research(department_code: str):
    """
    Extracts all faculty research information for a given department.

    - **department_code**: The code for the department (e.g., 'CSCI').
    """
    logger.info(f"Received request to extract research for department: {department_code}")
    try:
        # Use the existing async method from your class
        research_data = await extractor.extract_department_research(department_code)

        if not research_data:
            logger.warning(f"No data found for department: {department_code}")
            # Raise an HTTPException, which FastAPI turns into a proper 404 response
            raise HTTPException(status_code=404, detail=f"No faculty research data found for department code: {department_code}")

        logger.info(f"Successfully extracted {len(research_data)} records for {department_code}.")
        return research_data

    except ValueError as e:
        # Handle the invalid department error from your class
        logger.error(f"Invalid department code provided: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch any other unexpected errors during scraping
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred during scraping.")
