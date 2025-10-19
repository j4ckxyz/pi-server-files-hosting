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
            files = data.get('files', [])
            if not files:
                return "No files found on the server. Check DATA_LOCATION configuration."
            return f"Available files ({len(files)}):\n" + "\n".join(f"- {f}" for f in files)
        except requests.RequestException as e:
            return f"Error fetching files: {str(e)}"

    def search_files(
        self,
        query: str = Field(..., description="The content to search for in the files."),
    ) -> str:
        """
        Searches for content in the files. Uses automatic variations (case-insensitive, acronyms, spacing variants).
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
            variations = data.get("searched_variations", [])
            files_searched = data.get("files_searched", 0)
            
            if not results:
                return f"No results found for '{query}'.\nSearched {files_searched} files.\nVariations tried: {', '.join(variations) if variations else 'none'}"

            formatted_results = []
            for result in results:
                matched = result.get('matched_term', query)
                formatted_results.append(
                    f"- File: {result['file']}, Line: {result['line']}, Matched: '{matched}', Content: {result['content']}"
                )
            return f"Search results for '{query}' ({len(results)} matches in {files_searched} files searched):\nVariations: {', '.join(variations)}\n\n" + "\n".join(formatted_results)
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

    def debug_server(self) -> str:
        """
        Shows server debug information including file count and configuration.
        """
        if not self.valves.api_key:
            return "API key is not set in the tool's valves."

        try:
            response = requests.get(f"{self.valves.api_server_url}/debug", headers={"X-API-Key": self.valves.api_key})
            response.raise_for_status()
            data = response.json()
            return f"""Server Debug Info:
- Data Location: {data.get('data_location', 'Not set')}
- Location Exists: {data.get('data_location_exists', False)}
- Total Files Found: {data.get('total_files', 0)}
- PDF Support: {data.get('pdf_support', False)}
- Sample Files: {', '.join(data.get('sample_files', [])) if data.get('sample_files') else 'None'}"""
        except requests.RequestException as e:
            return f"Error fetching debug info: {str(e)}"
