from .microservice_client import MicroserviceClient
from planner.models import Research

class DataProcessor:
    def __init__(self):
        self.microservice_client = MicroserviceClient()

    def process_research_data(self):
        department = "CSCI"
        research_data = self.microservice_client.get_research(department)
        if not research_data:
            return

        for item in research_data:
            Research.objects.create(
                professor_name=item["name"],
                department=department,
                website=item["website"],
                research_interest=item["research_interest"],
                src_url=item["src_url"])
    
    def test_connection(self):
        return self.microservice_client.test_connection()
