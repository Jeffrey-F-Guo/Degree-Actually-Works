from langchain.chat_models import init_chat_model
from pydantic import BaseModel

def llm_init( prompt_template, pydantic_model, model="gemini-2.5-flash-lite", model_provider="google-genai"):
    llm = init_chat_model(model=model, model_provider=model_provider)
    structured_llm = llm.with_structured_output(pydantic_model)
    llm_chain = prompt_template | structured_llm
    return llm_chain

