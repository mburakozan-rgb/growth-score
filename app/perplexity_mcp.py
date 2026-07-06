# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import httpx
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env from the project root directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize FastMCP server
mcp = FastMCP("Perplexity Search Server")

@mcp.tool()
async def perplexity_search(query: str, depth: str = "sonar") -> str:
    """Performs a web search using Perplexity's real-time AI and search capabilities.
    
    Args:
        query: The search query.
        depth: The search depth or model (default is 'sonar').
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key or api_key == "your_perplexity_api_key_here":
        return "Error: PERPLEXITY_API_KEY is not set or has the placeholder value in the .env file."
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": depth,
        "messages": [
            {
                "role": "system",
                "content": "You are a research assistant. Return a concise summary of findings and provide clear citations/links where appropriate."
            },
            {
                "role": "user",
                "content": query
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            citations = data.get("citations", [])
            
            if citations:
                answer += "\n\nSources/Citations:\n" + "\n".join(f"- {c}" for c in citations)
                
            return answer
        except Exception as e:
            return f"Error executing Perplexity search: {str(e)}"

if __name__ == "__main__":
    mcp.run()
