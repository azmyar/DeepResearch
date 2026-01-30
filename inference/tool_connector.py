import os
import json
import requests
from typing import Union
from qwen_agent.tools.base import BaseTool, register_tool

@register_tool("connector_search", allow_overwrite=True)
class ConnectorSearch(BaseTool):
    name = "connector_search"
    description = "Search through external connectors like GitHub, Drive, etc."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query."
            },
            "connector_id": {
                "type": "string",
                "description": "The connector ID to search (e.g., 'github'). Default is 'github'.",
                "default": "github"
            }
        },
        "required": ["query"]
    }

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            query = params
            connector_id = "github"
        else:
            query = params.get("query")
            connector_id = params.get("connector_id", "github")

        if not query:
            return "[ConnectorSearch] Query is required."

        bosa_token = os.environ.get("BOSA_TOKEN")
        user_token = os.environ.get("USER_TOKEN")
        
        if not bosa_token and not user_token:
            return "[ConnectorSearch] Error: Neither BOSA_TOKEN nor USER_TOKEN environment variable is set."

        url = f"https://stag-be-smart-search.obrol.id/v2/connector/{connector_id}/search"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        if bosa_token:
            headers["bosa-token"] = bosa_token
        
        if user_token:
            headers["Authorization"] = f"Bearer {user_token}"
        
        data = {
            "query": query
        }

        try:
            response = requests.post(url, headers=headers, data=data, timeout=3000)
            response.raise_for_status()
            result_json = response.json()
            
            items = result_json.get("data", [])
            if not items:
                return f"No results found for query: '{query}' on connector '{connector_id}'"

            formatted_results = []
            for item in items:
                content = item.get("content", "").strip()
                metadata = item.get("metadata", {})
                title = metadata.get("title", "No Title")
                source = metadata.get("source", "Unknown Source")
                formatted_results.append(f"Title: {title}\nSource: {source}\nContent: {content}")

            return f"Found {len(items)} results from {connector_id}:\n\n" + "\n\n---\n\n".join(formatted_results)

        except Exception as e:
            return f"[ConnectorSearch] Error: {str(e)}"
