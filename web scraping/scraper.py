from bs4 import BeautifulSoup
import requests
import re
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ollama_client import OllamaClient

# manual web scraper gets all data
# llm extracts info of interest

scrape_url = 'https://www.onetonline.org/link/summary/15-1252.00'
page = requests.get(scrape_url).text

html_content = BeautifulSoup(page, "html.parser")
text_content = str(html_content.prettify)

wage_info = html_content.find_all(string=re.compile(r"\$.*"))
growth = html_content.find_all(string=re.compile("Projected growth"))

with open("file.txt", 'w') as f:
    f.write(text_content)


for text in wage_info:
    print(text.strip())


# Initialize Ollama client
ollama_client = OllamaClient(model="llama3.2")

# Create a system prompt for wage data extraction
system_prompt = """You are an expert at extracting wage and employment data from HTML content.
Extract and return ONLY valid JSON with the following structure:
{
  "hourly_wage": "extracted hourly wage data",
  "annual_wage": "extracted annual wage data", 
  "projected_growth": "extracted projected growth level"
}

IMPORTANT: Return ONLY valid JSON. No explanations or additional text."""

user_prompt = f"""Please find the hourly wage data, annual wage data, and projected growth level
from the following HTML code.

{text_content}

Return your answer in pure JSON format. Do not include anything other than hourly wage, annual wage, and projected growth level."""

response = ollama_client.generate_content(user_prompt, system_prompt)
print(response)
