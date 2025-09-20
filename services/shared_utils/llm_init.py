import os
from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from dotenv import load_dotenv

def llm_init(prompt_template, pydantic_model, model="gemini-2.5-flash-lite", model_provider="google-genai"):
    # Get API key from environment variable
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required. Make sure it's set in your .env file.")
    
    llm = init_chat_model(
        model=model, 
        model_provider=model_provider,
        api_key=api_key
    )
    structured_llm = llm.with_structured_output(pydantic_model)
    llm_chain = prompt_template | structured_llm
    return llm_chain

