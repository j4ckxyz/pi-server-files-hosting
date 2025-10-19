
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import glob

load_dotenv()

API_KEY = os.getenv("API_KEY")
DATA_LOCATION = os.getenv("DATA_LOCATION")

api_key_header = APIKeyHeader(name="X-API-Key")

app = FastAPI(
    title="File Server API",
    description="An API to search and retrieve files from a local directory.",
    version="1.0.0",
)

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.get("/files", summary="List available files")
def list_files(api_key: str = Security(get_api_key)):
    files = []
    for ext in ("*.pdf", "*.md", "*.txt"):
        files.extend(glob.glob(os.path.join(DATA_LOCATION, ext)))
    return {"files": [os.path.basename(f) for f in files]}

class SearchRequest(BaseModel):
    query: str

@app.post("/search", summary="Search for content in files")
def search_files(request: SearchRequest, api_key: str = Security(get_api_key)):
    results = []
    for ext in ("*.pdf", "*.md", "*.txt"):
        for filepath in glob.glob(os.path.join(DATA_LOCATION, ext)):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f):
                    if request.query in line:
                        results.append({"file": os.path.basename(filepath), "line": i + 1, "content": line.strip()})
    return {"results": results}

@app.get("/files/{filename}", summary="Get the content of a specific file")
def get_file(filename: str, api_key: str = Security(get_api_key)):
    filepath = os.path.join(DATA_LOCATION, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return {"content": f.read()}
