from bs4 import BeautifulSoup
import requests
import re
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

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


genai.configure(api_key = GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

response = model.generate_content(
    """Please find the hourly wage data, annual wage data, and projected growth level
        from the following HTML code.

        f{text_content}

        **IMPORTANT"" Return your answer in pure JSON format. Do not include anything other than hourly wage, annual wage, and projected growth level""")

print(response)
