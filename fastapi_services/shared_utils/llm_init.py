import os
import asyncio
import logging
from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

#TODO: make this configurable
LLM_URL = "http://localhost:11435"

def llm_init(prompt_template, pydantic_model, model, model_provider):
    if model_provider == "ollama":
        llm = init_chat_model(
            model=model, 
            model_provider=model_provider,
            base_url=LLM_URL
        )
    elif model_provider == "google-genai":
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required. Make sure it's set in your .env file.")
        llm = init_chat_model(
            model=model, 
            model_provider=model_provider,
            api_key=api_key
        )
    
    # chain the llm with the structured output
    structured_llm = llm.with_structured_output(pydantic_model)
    llm_chain = prompt_template | structured_llm
    return llm_chain
