import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
import os
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
import json
from dotenv import load_dotenv

from src.handlers.task_handlers import TaskHandler
from src.utils.security import validate_path
from src.utils.validators import is_valid_task
# Configuration
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

load_dotenv()

AI_PROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")
if not AI_PROXY_TOKEN:
    raise ValueError("AIPROXY_TOKEN environment variable is required")


# src/main.py

class LLMClient:
    """Client for interacting with the LLM service"""
    def __init__(self, token: str):
        self.token = token
        self.base_url = "YOUR_AI_PROXY_ENDPOINT"  # Replace with actual endpoint

    async def get_completion(self, prompt: str) -> str:
        """Get completion from LLM"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a task parsing assistant."},
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"LLM request failed: {response.text}")
                
            return response.json()["choices"][0]["message"]["content"]

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for texts"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",  # Replace with actual embedding model
                    "input": texts
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Embedding request failed: {response.text}")
                
            return response.json()["data"]

    async def process_image(self, image_data: bytes) -> str:
        """Process image with LLM"""
        import base64
        image_b64 = base64.b64encode(image_data).decode()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are an image processing assistant."},
                        {
                            "role": "user",
                            "content": [
                                {"type": "image", "data": image_b64},
                                {"type": "text", "text": "Extract text from this image."}
                            ]
                        }
                    ]
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Image processing failed: {response.text}")
                
            return response.json()["choices"][0]["message"]["content"]

app = FastAPI(title="LLM Automation Agent")



# Initialize LLM client and task handler
llm_client = LLMClient(AI_PROXY_TOKEN)
task_handler = TaskHandler(llm_client)

@app.post("/run")
async def run_task(task: str) -> Dict[str, Any]:
    """
    Execute a task described in natural language
    
    Args:
        task: String describing the task to be performed
        
    Returns:
        Dictionary containing task execution status and any relevant information
    """
    try:
        # Validate task
        if not task or not is_valid_task(task):
            raise HTTPException(
                status_code=400,
                detail="Invalid task description"
            )
        
        # Execute task
        result = await task_handler.handle_task(task)
        
        return {
            "status": "success",
            "result": result
        }
    
    except Exception as e:
        # Log the error (implement proper logging)
        print(f"Error executing task: {str(e)}")
        
        if isinstance(e, HTTPException):
            raise e
        
        # Determine if it's a task error (400) or system error (500)
        if "Invalid" in str(e) or "Failed to parse" in str(e):
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/read")
async def read_file(path: str) -> PlainTextResponse:
    """
    Read contents of a file
    
    Args:
        path: Path to the file to read
        
    Returns:
        PlainTextResponse containing the file contents
    """
    try:
        # Validate path is within /data directory
        if not validate_path(path):
            raise HTTPException(
                status_code=400,
                detail="Invalid path: Must be within /data directory"
            )
        
        file_path = Path(path)
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {path}"
            )
        
        # Read and return file contents
        content = file_path.read_text()
        return PlainTextResponse(content)
    
    except Exception as e:
        # Log the error (implement proper logging)
        print(f"Error reading file: {str(e)}")
        
        if isinstance(e, HTTPException):
            raise e
            
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint
    
    Returns:
        Dictionary containing service status
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)