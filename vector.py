from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import uuid
from datasets import load_dataset
import pandas as pd
import os

# Load dataset and prepare data
dataset = load_dataset("QuyenAnhDE/Diseases_Symptoms")
df = pd.DataFrame(dataset['train'])
df = df.rename(columns={"Name": "disease", "Symptoms": "symptoms"})
df['symptoms'] = df['symptoms'].apply(lambda x: [s.strip().lower() for s in x.split(",")])

# Initialize SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")
url=os.environ.get("QDRANT_URL")
api_key=os.environ.get("QDRANT_API_KEY")
# Initialize Qdrant Cloud client
# Replace with your Qdrant Cloud URL and API key
qdrant_client = QdrantClient(
    url=url,  # Use environment variable
    api_key=api_key,  # Use environment variable
)

# Collection name
collection_name = "symptoms"

# Delete existing collection if it exists
try:
    qdrant_client.delete_collection(collection_name=collection_name)
except:
    pass

# Create a new collection
qdrant_client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=model.get_sentence_embedding_dimension(),  # Dimension of the embeddings
        distance=Distance.COSINE
    )
)

# Get all symptoms
all_symptoms = list({s for row in df['symptoms'] for s in row})
vectors = model.encode(all_symptoms)

# Prepare points for upsert
points = [
    PointStruct(
        id=str(uuid.uuid4()),
        vector=vector.tolist(),
        payload={"name": symptom}
    )
    for vector, symptom in zip(vectors, all_symptoms)
]

# Upsert embeddings to the collection
qdrant_client.upsert(
    collection_name=collection_name,
    points=points
)