from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Qdrant Cloud client
url=os.environ.get("QDRANT_URL")
api_key=os.environ.get("QDRANT_API_KEY")
qdrant_client = QdrantClient(
        url=url,  # Use environment variable
        api_key=api_key,  # Use environment variable
    timeout=30.0
)

# Initialize SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Collection name (must match the one used during upsert)
collection_name = "symptoms"

def get_similar_symptoms(symptom):
    # Encode the input symptom
    vector = model.encode(symptom)
    
    # Perform similarity search
    results = qdrant_client.search(
        collection_name=collection_name,
        query_vector=vector.tolist(),
        limit=5,  # Return top 5 similar symptoms
        with_payload=True  # Include payload (e.g., symptom name)
    )
    
    # Extract symptom names from results
    similar_symptoms = [result.payload["name"] for result in results]
    return similar_symptoms
