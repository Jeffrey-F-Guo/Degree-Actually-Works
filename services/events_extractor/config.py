from typing import List, Dict

def get_base_url() -> str:
    """
    Get the base URL for WWU events page with all categories.
    """
    return "https://win.wwu.edu/events/?categories=9821&categories=17934&categories=21914&categories=9822&categories=11780&categories=23412&categories=9830"

def get_llm_prompt() -> List[Dict[str, str]]:
    """
    Get the LLM prompt template for extracting event information from HTML.
    """
    return [
        {
            "role": "system",
            "content": """Your role is to extract information from a html file.
                    Given a html file, extract and return a list of events. Each event should have the following fields:

                        event_name: str
                        date: str
                        page_url: str
            """
        },
        {
            "role": "user",
            "content": "{html}"
        }
    ]

def get_js_commands() -> List[str]:
    """
    Get JavaScript commands for scrolling and loading more events.
    """
    return [
        "window.scrollTo(0, document.body.scrollHeight);",
        "Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('Load More'))?.click();"
    ]

def get_browser_config(debug_mode: bool = False) -> Dict:
    """
    Get browser configuration for the events crawler.

    Args:
        debug_mode: If True, browser will run in non-headless mode for debugging
    """
    return {
        "headless": not debug_mode
    }

def get_crawler_config() -> Dict:
    """
    Get crawler run configuration for events extraction.
    """
    return {
        "js_code": get_js_commands(),
        "js_only": True,  # ensures browser window doesn't reload
        "session_id": "base_event_page_session"  # ensures same tab
    }
