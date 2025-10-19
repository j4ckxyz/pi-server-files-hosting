import os
import requests
from pydantic import BaseModel, Field



class Tools:
    class Valves(BaseModel):
        api_server_url: str = Field(
            default="http://localhost:8000",
            description="The URL of the file server.",
        )
        api_key: str = Field(
            default="",
            description="The API key for the file server.",
        )

    def __init__(self):
        self.valves = self.Valves()

    def list_files(self) -> str:
        """
        Lists the available files on the server.
        """
        if not self.valves.api_key:
            return "API key is not set in the tool's valves."

        try:
            response = requests.get(f"{self.valves.api_server_url}/files", headers={"X-API-Key": self.valves.api_key})
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
        if not self.valves.api_key:
            return "API key is not set in the tool's valves."

        try:
            response = requests.post(
                f"{self.valves.api_server_url}/search",
                headers={"X-API-Key": self.valves.api_key, "Content-Type": "application/json"},
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
        if not self.valves.api_key:
            return "API key is not set in the tool's valves."

        try:
            response = requests.get(f"{self.valves.api_server_url}/files/{filename}", headers={"X-API-Key": self.valves.api_key})
            response.raise_for_status()
            data = response.json()
            return f"Content of {filename}:\n\n{data['content']}"
        except requests.RequestException as e:
            return f"Error fetching file: {str(e)}"
