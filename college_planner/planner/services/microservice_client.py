from django.conf import settings
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MicroserviceClient:
    def __init__(self):
        self.base_url = settings.MICROSERVICE_URL
        self.timeout = 360

    def get_research(self, department_code: str):
        url = f"{self.base_url}/extract/research/{department_code}"
        response = httpx.get(url, timeout=self.timeout)
        # response.raise_for_status()
        return response.json()
    
    def get_course(self, department_code: str):
        url = f"{self.base_url}/extract/courses/{department_code}"
        try:
            response = httpx.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error occurred while getting course data: {e}")

    def get_events(self):
        url = f"{self.base_url}/extract/events"
        try:
            response = httpx.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error occured while getting events {e}")
    

    def test_connection(self):
        url = f"{self.base_url}/health"
        response = httpx.get(url)
        # response.raise_for_status()
        if response.status_code != 200:
            return False
        return True
