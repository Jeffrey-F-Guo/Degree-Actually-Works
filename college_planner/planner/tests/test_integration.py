from planner.services.data_processor import DataProcessor
from planner.services.microservice_client import MicroserviceClient
data_processor = DataProcessor()

print(data_processor.test_connection())

microservice_client = MicroserviceClient()

print(microservice_client.get_research("CSCI"))