import os
import requests
from pydantic import BaseModel, Field

# Configuration
API_SERVER_URL = os.getenv("API_SERVER_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")

class Tools:
    def __init__(self):
        pass

    def list_files(self) -> str:
        """
        Lists the available files on the server.
        """
        if not API_KEY:
            return "API key is not set in the environment variable 'API_KEY'."

        try:
            response = requests.get(f"{API_SERVER_URL}/files", headers={"X-API-Key": API_KEY})
            response.raise_for_status()
            data = response.json()
            return f"Available files: {', '.join(data['files'])}"
        except requests.RequestException as e:
            return f"Error fetching files: {str(e)}"

    def search_files(
        self,
        query: str = Field(..., description="The content to search for in the files."),
    ) -> str:
        """
        Searches for content in the files.
        """
        if not API_KEY:
            return "API key is not set in the environment variable 'API_KEY'."

        try:
            response = requests.post(
                f"{API_SERVER_URL}/search",
                headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
                json={"query": query},
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            if not results:
                return f"No results found for '{query}'."

            formatted_results = []
            for result in results:
                formatted_results.append(
                    f"- File: {result['file']}, Line: {result['line']}, Content: {result['content']}"
                )
            return f"Search results for '{query}':\n" + "\n".join(formatted_results)
        except requests.RequestException as e:
            return f"Error searching files: {str(e)}"

    def get_file(
        self,
        filename: str = Field(..., description="The name of the file to retrieve."),
    ) -> str:
        """
        Retrieves the content of a specific file.
        """
        if not API_KEY:
            return "API key is not set in the environment variable 'API_KEY'."

        try:
            response = requests.get(f"{API_SERVER_URL}/files/{filename}", headers={"X-API-Key": API_KEY})
            response.raise_for_status()
            data = response.json()
            return f"Content of {filename}:\n\n{data['content']}"
        except requests.RequestException as e:
            return f"Error fetching file: {str(e)}"
