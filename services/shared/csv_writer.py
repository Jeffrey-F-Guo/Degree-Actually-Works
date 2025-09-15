import csv
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

        # Determine the CSV headers from keys of the first dictionary
        headers = data[0].keys()
        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            logger.info(f"Data written to {filename}")
        except Exception as e:
            logger.error(f"Failed to write CSV: {e}")