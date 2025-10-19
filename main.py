
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import glob
import re
from typing import List, Set
try:
    from PyPDF2 import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

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

def generate_search_variations(query: str) -> Set[str]:
    variations = set()
    variations.add(query.lower())
    
    no_spaces = query.replace(" ", "").lower()
    variations.add(no_spaces)
    
    words = query.split()
    if len(words) > 1:
        acronym = "".join(word[0] for word in words).lower()
        variations.add(acronym)
        
        variations.add("-".join(words).lower())
        variations.add("_".join(words).lower())
    
    variations.add(query.replace("-", " ").lower())
    variations.add(query.replace("_", " ").lower())
    
    return variations

def extract_text_from_pdf(filepath: str) -> str:
    if not PDF_SUPPORT:
        return ""
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"[Error reading PDF: {str(e)}]"

def read_file_content(filepath: str) -> str:
    if filepath.endswith('.pdf'):
        return extract_text_from_pdf(filepath)
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

@app.post("/search", summary="Search for content in files")
def search_files(request: SearchRequest, api_key: str = Security(get_api_key)):
    results = []
    search_variations = generate_search_variations(request.query)
    
    for ext in ("*.pdf", "*.md", "*.txt"):
        for filepath in glob.glob(os.path.join(DATA_LOCATION, ext)):
            content = read_file_content(filepath)
            content_lower = content.lower()
            
            matched_variation = None
            for variation in search_variations:
                if variation in content_lower:
                    matched_variation = variation
                    break
            
            if matched_variation:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if matched_variation in line.lower():
                        results.append({
                            "file": os.path.basename(filepath),
                            "line": i + 1,
                            "content": line.strip(),
                            "matched_term": matched_variation
                        })
    
    return {"results": results, "searched_variations": list(search_variations)}

@app.get("/files/{filename}", summary="Get the content of a specific file")
def get_file(filename: str, api_key: str = Security(get_api_key)):
    filepath = os.path.join(DATA_LOCATION, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    content = read_file_content(filepath)
    return {"content": content}
