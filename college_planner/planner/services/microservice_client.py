from django.conf import settings
import httpx


class MicroserviceClient:
    def __init__(self):
        self.base_url = settings.MICROSERVICE_URL
        self.timeout = 360

    def get_research(self, department_code: str):
        url = f"{self.base_url}/extract/research/{department_code}"
        response = httpx.get(url, timeout=self.timeout)
        # response.raise_for_status()
        return response.json()

    def test_connection(self):
        url = f"{self.base_url}/health"
        response = httpx.get(url)
        # response.raise_for_status()
        if response.status_code != 200:
            return False
        return True
