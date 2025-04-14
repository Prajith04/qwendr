from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from utils.vector_search import get_similar_symptoms
from utils.sql_queries import get_diseases_by_symptoms, get_related_symptoms
import sqlite3
import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Groq API key from environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Helper function to check if a symptom exists in the database
def is_valid_symptom(symptom):
    conn = sqlite3.connect("disease.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM symptom WHERE name = ?", (symptom,))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0

@app.get("/search")
def search(symptom: str, selected: list[str] = Query([])):
    # Get similar symptoms from vector search
    similar = get_similar_symptoms(symptom)
    
    # Check if the exact symptom exists in our database
    if is_valid_symptom(symptom):
        # Use the exact symptom if it exists
        search_symptoms = [symptom] + selected
    else:
        # Otherwise, try to use the first similar symptom that exists in our database
        valid_symptom_found = False
        for sim in similar:
            if is_valid_symptom(sim):
                search_symptoms = [sim] + selected
                valid_symptom_found = True
                break
        
        # If no valid symptom found, just use all similar symptoms
        if not valid_symptom_found:
            search_symptoms = similar + selected
    
    # Get diseases that have ALL the selected search symptoms
    diseases = get_diseases_by_symptoms(search_symptoms)
    
    # Get related symptoms from the matching diseases, excluding already selected symptoms
    suggestions = get_related_symptoms(diseases, exclude=search_symptoms)

    return {
        "matching_diseases": diseases,
        "related_symptoms": suggestions,
        "semantic_matches": similar
    }

@app.get("/disease-info")
async def disease_info(name: str):
    """
    Get detailed information about a disease using Groq's LLM API
    """
    if not GROQ_API_KEY:
        return {"info": "<p>Error: Groq API key not found in environment variables.</p>"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-70b-8192",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful medical assistant. Provide accurate, well-structured information about diseases. Format your response in HTML paragraphs with appropriate headings using <h4> tags. Include symptoms, causes, treatments, and prevention when possible. Keep responses concise but informative."
                        },
                        {
                            "role": "user",
                            "content": f"Provide detailed information about {name}, including symptoms, causes, diagnosis, treatments, and prevention methods when applicable."
                        }
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"info": content}
            else:
                return {"info": f"<p>Error: Failed to fetch information. Status code: {response.status_code}</p>"}
                
    except Exception as e:
        return {"info": f"<p>Error: {str(e)}</p>"}
