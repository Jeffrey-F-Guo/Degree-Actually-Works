from typing import List, Dict

def get_base_urls() -> Dict[str, str]:
    """
    Get base URLs for course catalog pages by department.
    """
    return {
        "CSCI": "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10593",
        "MATH": "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10724",
        "PSYCH": "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=10754",
        "BUS": "https://catalog.wwu.edu/preview_program.php?catoid=22&poid=11053",
    }

def get_llm_prompt() -> List[Dict[str, str]]:
    """
    Get the LLM prompt template for extracting course information from markdown.
    """
    return [
        {
            "role": "system",
            "content": """Your role is to extract information from a markdown file.
                    Given a markdown file, extract and return a list of courses. Each course should have the following fields:

                        course_name: str
                        course_description: str
                        course_prereqs: str
                        course_credits: int
            """
        },
        {
            "role": "user",
            "content": "{markdown}"
        }
    ]

def get_js_commands() -> List[str]:
    """
    Get JavaScript commands for expanding all course sections.
    """
    return [
        """
        async function expandAllCourses() {
            const links = document.querySelectorAll('li.acalog-course span a[onclick*="showCourse"]');
            for (let i = 0; i < links.length; i++) {
                links[i].click();
            }
        }

        expandAllCourses();
        """
    ]

def get_browser_config(debug_mode: bool = False) -> Dict:
    """
    Get browser configuration for the courses crawler.

    Args:
        debug_mode: If True, browser will run in non-headless mode for debugging
    """
    return {
        "headless": not debug_mode
    }

def get_crawler_config() -> Dict:
    """
    Get crawler run configuration for courses extraction.
    """
    return {
        "js_code": get_js_commands(),
        "delay_before_return_html": 15.0  # Wait for all expansions to complete
    }
