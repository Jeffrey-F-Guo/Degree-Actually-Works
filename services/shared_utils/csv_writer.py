import csv
from typing import List, Dict
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOGS_PATH = "/app/logs"

def csv_writer(data: List[Dict], filename: str):
        """
        Writes extracted information to a CSV file.

        Args:
            data: List of dictionaries containing information.
            filename: Name of the CSV file to write to.
        """
        if not data:
            logger.warning("No data to write.")
            return
        if not os.path.exists(LOGS_PATH):
            os.makedirs(LOGS_PATH)
        # Determine the CSV headers from keys of the first dictionary
        headers = data[0].keys()
        filepath = os.path.join(LOGS_PATH, filename)
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            logger.info(f"Data written to {filename}")
        except Exception as e:
            logger.error(f"Failed to write CSV: {e}")