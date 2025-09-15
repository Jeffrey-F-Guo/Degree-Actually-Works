"""
LLM Service API
Provides a FastAPI service for LLM interactions
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LLM Service",
    description="A service for LLM interactions and text processing",
    version="1.0.0"
)

class TextRequest(BaseModel):
    text: str
    model: Optional[str] = "gemini-pro"
    max_tokens: Optional[int] = 1000

class TextResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: Optional[int] = None

@app.get("/")
async def root():
    return {"message": "LLM Service is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm-service"}

@app.post("/generate", response_model=TextResponse)
async def generate_text(request: TextRequest):
    """
    Generate text using the specified LLM model
    """
    try:
        # This is a placeholder - you'll need to implement actual LLM integration
        # based on your specific needs (Ollama, OpenAI, Google Gemini, etc.)

        # Example response structure
        response = TextResponse(
            response=f"Generated response for: {request.text[:50]}...",
            model_used=request.model,
            tokens_used=len(request.text.split())
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")

@app.post("/summarize", response_model=TextResponse)
async def summarize_text(request: TextRequest):
    """
    Summarize the provided text
    """
    try:
        # Placeholder for summarization logic
        summary = f"Summary of: {request.text[:100]}..."

        response = TextResponse(
            response=summary,
            model_used=request.model,
            tokens_used=len(request.text.split())
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing text: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
