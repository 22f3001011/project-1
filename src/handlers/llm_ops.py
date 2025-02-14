import httpx

async def process_with_llm(task: str, token: str) -> dict:
    """
    Process the task with GPT-4o-Mini to:
    1. Understand the intent
    2. Extract key parameters
    3. Identify required operations
    """
    async with httpx.AsyncClient() as client:
        # Configure your AI Proxy endpoint
        response = await client.post(
            "YOUR_AI_PROXY_ENDPOINT",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a task parsing assistant."},
                    {"role": "user", "content": task}
                ]
            }
        )
        
        if response.status_code != 200:
            raise Exception("Failed to process task with LLM")
            
        return response.json()
