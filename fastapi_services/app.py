from fastapi import FastAPI, HTTPException
import asyncio
import logging
import os
from typing import List, Dict, Any

# Add the services directory to Python path to fix import issues

# Import all extractor functions
from research_extractor import extract_research_by_department
from events_extractor import extract_events
from courses_extractor import extract_course
from shared_utils import csv_writer
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI app instance
app = FastAPI(
    title="WWU Resource Extractor API",
    description="An API to scrape WWU resources from university websites.",
    version="1.0.0"
)


@app.get("/")
async def read_root():
    """
    Root endpoint with a welcome message.
    """
    return {"message": "Welcome to the Faculty Research Extractor API!"}

@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {"message": "WWU Resource Extractor API is running", "status": "healthy"}

@app.get("/logs")
async def logs():
    """
    logs check endpoint.
    """
    data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
    filename = "log_test.csv"
    csv_writer(data, filename)
    return {"message": "WWU Resource Extractor API is running", "status": "logged"}    

@app.get("/extract/research/{department_code}")
async def extract_research_endpoint(department_code: str):
    """
    Extracts all faculty research information for a given department.

    - **department_code**: The code for the department (e.g., 'CSCI').
    """
    logger.info(f"Received request to extract research for department: {department_code}")
    try:
        # Add timeout to prevent hanging
        research_data = await asyncio.wait_for(
            extract_research_by_department(department_code, debug_mode=False, write_to_csv=True),
            timeout=300  # 5 minutes timeout
        )

        if not research_data:
            logger.warning(f"No data found for department: {department_code}")
            # Raise an HTTPException, which FastAPI turns into a proper 404 response
            raise HTTPException(status_code=404, detail=f"No faculty research data found for department code: {department_code}")

        logger.info(f"Successfully extracted {len(research_data)} records for {department_code}.")
        return research_data

    except asyncio.TimeoutError:
        logger.error(f"Research extraction timed out for department: {department_code}")
        raise HTTPException(status_code=408, detail=f"Research extraction timed out for department: {department_code}")
    except ValueError as e:
        # Handle the invalid department error
        logger.error(f"Invalid department code provided: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch any other unexpected errors during scraping
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred during research scraping.")


@app.get("/extract/events")
async def extract_events_endpoint():
    """
    Extracts all events from the website.
    """
    logger.info("Received request to extract events")
    try:
        from events_extractor.config import get_base_url
        # events = await asyncio.wait_for(
        #     extract_events(get_base_url(), debug_mode=False),
        #     timeout=600  # 10 minutes timeout (events can take longer)
        # )
        events = await extract_events(get_base_url(), debug_mode=True)
        if not events:
            logger.warning("No events found")
            raise HTTPException(status_code=404, detail="No events found")
        logger.info({"message": "Events extracted successfully", "count": len(events) if events else 0})
        return events

    except asyncio.TimeoutError:
        logger.error("Events extraction timed out")
        raise HTTPException(status_code=408, detail="Events extraction timed out")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred during event scraping.")


@app.get("/extract/courses/{department_code}")
async def exract_courses_endpoint(department_code: str):
    """
    API endpoint to extract course information for a given department.
    """
    logger.info(f"Received request to extract courses for department: {department_code}")
    try:
        courses = await extract_course(department_code, debug_mode=False)
        print(type(courses[0]))
        if not courses:
            logger.warning("No courses found")
            raise HTTPException(status_code=404, detail="No courses found for the specified department")
        logger.info({"message": "Courses extracted successfully", "count": len(courses) if courses else 0})
        
        return courses
    except asyncio.TimeoutError:
        logger.error(f"Course extraction timed out for department: {department_code}")
        raise HTTPException(status_code=408, detail=f"Course extraction timed out for department: {department_code}")
    except ValueError as e:
        logger.error(f"Invalid department code provided: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred during course scraping.")


@app.get("/extract/all")
async def extract_all():
    """
    Extracts all data from all sources. This is the main endpoint for scheduled crawlers.

    This endpoint will:
    1. Extract research data for all departments (CSCI, BIO, MATH)
    2. Extract all events
    3. Extract course data for all departments (CSCI, MATH, PSYCH, BUS)

    Returns a summary of what was extracted.
    """
    logger.info("Received request to extract all data")

    results = {
        "research": {},
        "events": {"status": "pending", "count": 0},
        "courses": {},
        "summary": {
            "total_extractions": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
    }

    # Define departments for research and courses
    research_departments = ["CSCI", "MATH"]
    course_departments = ["CSCI", "MATH"]

    try:
        # Extract research data for all departments
        logger.info("Starting research data extraction...")
        for dept in research_departments:
            try:
                research_data = await extract_research_by_department(dept, debug_mode=False, write_to_csv=True)
                results["research"][dept] = {
                    "status": "success",
                    "count": len(research_data) if research_data else 0
                }
                results["summary"]["successful"] += 1
                logger.info(f"Successfully extracted research for {dept}: {len(research_data) if research_data else 0} records")
            except Exception as e:
                results["research"][dept] = {
                    "status": "failed",
                    "error": str(e),
                    "count": 0
                }
                results["summary"]["failed"] += 1
                results["summary"]["errors"].append(f"Research extraction failed for {dept}: {str(e)}")
                logger.error(f"Research extraction failed for {dept}: {e}")

        # Extract events
        logger.info("Starting events extraction...")
        try:
            from events_extractor.config import get_base_url
            events = await extract_events(get_base_url(), debug_mode=False)
            results["events"] = {
                "status": "success",
                "count": len(events) if events else 0
            }
            results["summary"]["successful"] += 1
            logger.info(f"Successfully extracted events: {len(events) if events else 0} records")
        except Exception as e:
            results["events"] = {
                "status": "failed",
                "error": str(e),
                "count": 0
            }
            results["summary"]["failed"] += 1
            results["summary"]["errors"].append(f"Events extraction failed: {str(e)}")
            logger.error(f"Events extraction failed: {e}")

        # Extract course data for all departments
        logger.info("Starting course data extraction...")
        for dept in course_departments:
            try:
                courses = await extract_course(dept, debug_mode=False)
                results["courses"][dept] = {
                    "status": "success",
                    "count": len(courses) if courses else 0
                }
                results["summary"]["successful"] += 1
                logger.info(f"Successfully extracted courses for {dept}: {len(courses) if courses else 0} records")
            except Exception as e:
                results["courses"][dept] = {
                    "status": "failed",
                    "error": str(e),
                    "count": 0
                }
                results["summary"]["failed"] += 1
                results["summary"]["errors"].append(f"Course extraction failed for {dept}: {str(e)}")
                logger.error(f"Course extraction failed for {dept}: {e}")

        # Calculate total extractions attempted
        results["summary"]["total_extractions"] = len(research_departments) + len(events) + len(course_departments)

        # Determine overall status
        if results["summary"]["failed"] == 0:
            results["summary"]["overall_status"] = "success"
        elif results["summary"]["successful"] > 0:
            results["summary"]["overall_status"] = "partial_success"
        else:
            results["summary"]["overall_status"] = "failed"

        logger.info(f"Extraction complete. Success: {results['summary']['successful']}, Failed: {results['summary']['failed']}")
        return results

    except Exception as e:
        logger.error(f"Critical error during extract_all: {e}", exc_info=True)
        results["summary"]["overall_status"] = "critical_failure"
        results["summary"]["errors"].append(f"Critical error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Critical error during extraction: {str(e)}")