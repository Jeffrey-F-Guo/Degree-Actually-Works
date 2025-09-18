from typing import Dict, List

def get_base_urls() -> Dict[str, str]:
    """
    Get base URLs for all professor pages by department.
    """
    return {
        "CSCI": "https://cs.wwu.edu",
        "BIO": "https://biology.wwu.edu/people",
        "MATH": "https://mathematics.wwu.edu/people"
    }

def get_faculty_urls() -> Dict[str, str]:
    """
    Get main faculty page URLs for each department.
    """
    return {
        "CSCI": "https://cs.wwu.edu/faculty",
        "BIO": "https://biology.wwu.edu/directory/faculty",
        "MATH": "https://mathematics.wwu.edu/directory",
    }

def get_llm_prompt() -> List[Dict[str, str]]:
    """
    Get the LLM prompt template for extracting professor information.
    """
    return [
        {
            "role": "system",
            "content": """Your role is to extract information from a markdown file.
                    Given a markdown file, extract and return a list. Each event represents a prefoessor's web page
                    and should have the following fields:

                        name: str
                        website: str (optional). Only include URLS that are under the website section. If there is no website section, leave the field empty.
                        research_interest: list (optional) *important note: this must be academic interest. Only record research interests if they are under the research interests section. If there is no research section, leave the list empty*

            """
        },
        {
            "role": "user",
            "content": "{markdown}"
        }
    ]

def get_faculty_page_schema() -> Dict:
    """
    CSS extraction schema for extracting professor pages from the base faculty page.
    """
    return {
        "name": "Faculty Page",
        "baseSelector": "div.card",
        "fields": [
            {
                "name": "professor_page_url",
                "selector": "a",
                "type": "attribute",
                "attribute": "href"
            },
        ]
    }

def get_professor_profile_schema() -> Dict:
    """
    CSS extraction schema for extracting professor information from professor profile pages.
    Note: Currently works for CSCI department pages, may need adjustment for other departments.
    """
    return {
        "name": "Professor Page",
        "baseSelector" : "body",
        "fields": [
            {
                "name": "professor_name",
                "selector": "h1.field-content",
                "type": "text",
                "default": "None"
            },
            {
                "name": "website",
                "selector": "div.website a",
                "type": "attribute",
                "attribute": "href",
                "default": "None"
            },
            {
                "name": "research_interest",
                "selector": "h2.views-label-field-research-interests+p",
                "type": "text",
                "default": "None"
            },
        ]
    }