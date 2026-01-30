import os
import json
import requests
from typing import Union
from qwen_agent.tools.base import BaseTool, register_tool

@register_tool("internal_retrieval", allow_overwrite=True)
class Retrieval(BaseTool):
    name = "internal_retrieval"
    description = "Retrieves knowledge from internal knowledge base."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search for in the internal knowledge base."
            }
        },
        "required": ["query"]
    }

    def call(self, params: Union[str, dict], **kwargs) -> str:
        query = params.get("query") if isinstance(params, dict) else params
        if not query:
            return "[Retrieval] Query is required."

        api_key = os.environ.get("RETRIEVAL_KEY")
        url = "https://stag-gbe-gdplabs-gen-ai-starter.obrol.id/components/testing_enhancement_cache:retrieval-pipeline/run"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        
        data = {
            "inputs": {
                "standalone_query": query
            },
            "config": {}
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result_json = response.json()
            
            chunks = result_json.get("chunks", [])
            if not chunks:
                return f"No results found for query: '{query}'"

            formatted_results = []
            for chunk in chunks:
                content = chunk.get("content", "").strip()
                metadata = chunk.get("metadata", {})
                source = metadata.get("source", "Unknown Source")
                formatted_results.append(f"Source: {source}\nContent:\n{content}")

            return f"Found {len(chunks)} results:\n\n" + "\n\n---\n\n".join(formatted_results)

        except Exception as e:
            return f"[Retrieval] Error: {str(e)}"
