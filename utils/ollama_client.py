import requests
import json
import re
import logging
from typing import Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class OllamaClient:
    """
    Client for interacting with Ollama API to replace Google Gemini API calls.
    Provides structured output functionality similar to LangChain's with_structured_output.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1"):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
        
    def _clean_json_response(self, response_text: str) -> str:
        """
        Clean JSON response from Ollama which may be wrapped in markdown code blocks.
        """
        # Remove markdown code block wrappers
        response_text = re.sub(r'^```json\s*', '', response_text, flags=re.MULTILINE)
        response_text = re.sub(r'^```\s*$', '', response_text, flags=re.MULTILINE)
        response_text = re.sub(r'```.*$', '', response_text, flags=re.MULTILINE)
        
        # Remove any leading/trailing whitespace
        response_text = response_text.strip()
        
        # Try to find JSON object in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return response_text
    
    def _make_request(self, prompt: str, system_prompt: str = "") -> str:
        """
        Make a request to the Ollama API and return the response text.
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for more consistent structured output
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            response = self.session.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Ollama request: {e}")
            raise
    
    def extract_events(self, content: str, source_url: str = "") -> Dict[str, Any]:
        """
        Extract events from markdown content using Ollama.
        Returns a dictionary that can be used to create ExtractedEvents Pydantic model.
        """
        system_prompt = """You are an expert at extracting event information from web content.
Given markdown content, extract and return ONLY valid JSON in this exact format:
{
  "events": [
    {
      "event_name": "Example Event",
      "event_date": "2024-01-01", 
      "location": "Example Location",
      "source_url": "https://example.com"
    }
  ]
}

Be thorough and look for:
- Scheduled events, meetings, workshops
- Performances, lectures, seminars  
- Sports events, social activities
- Academic events, deadlines

If no events found, return: {"events": []}

IMPORTANT: Return ONLY valid JSON. No explanations or additional text."""

        user_prompt = f"Source URL: {source_url}\n\n{content}"
        
        try:
            response = self._make_request(user_prompt, system_prompt)
            cleaned_response = self._clean_json_response(response)
            
            # Parse JSON
            parsed_data = json.loads(cleaned_response)
            
            # Ensure the response has the expected structure
            if "events" not in parsed_data:
                logger.warning("Response missing 'events' key, returning empty list")
                return {"events": []}
            
            # Add source_url to each event if not present
            for event in parsed_data["events"]:
                if not event.get("source_url") and source_url:
                    event["source_url"] = source_url
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response}")
            return {"events": []}
        except Exception as e:
            logger.error(f"Error extracting events: {e}")
            return {"events": []}
    
    def extract_structured(self, content: str, schema: Type[T], system_prompt: str = "") -> T:
        """
        Extract structured data using a Pydantic schema.
        Similar to LangChain's with_structured_output functionality.
        """
        if not system_prompt:
            system_prompt = f"""You are an expert at extracting structured information from content.
Extract and return ONLY valid JSON that matches this schema:
{json.dumps(schema.model_json_schema(), indent=2)}

IMPORTANT: Return ONLY valid JSON. No explanations or additional text."""

        try:
            response = self._make_request(content, system_prompt)
            cleaned_response = self._clean_json_response(response)
            
            # Parse JSON
            parsed_data = json.loads(cleaned_response)
            
            # Validate against Pydantic schema
            return schema(**parsed_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response}")
            # Return empty instance of the schema
            return schema()
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            logger.error(f"Parsed data: {parsed_data}")
            return schema()
        except Exception as e:
            logger.error(f"Error in structured extraction: {e}")
            return schema()
    
    def generate_content(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate content using Ollama (similar to Google GenerativeAI).
        """
        try:
            return self._make_request(prompt, system_prompt)
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return ""
    
    def health_check(self) -> bool:
        """
        Check if Ollama service is running and accessible.
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
