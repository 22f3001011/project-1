import os

AI_PROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")
if not AI_PROXY_TOKEN:
    raise ValueError("AIPROXY_TOKEN environment variable is required")

print(AI_PROXY_TOKEN)
