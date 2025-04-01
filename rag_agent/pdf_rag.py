import os
import time
import uuid
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
from dotenv import load_dotenv
from openai import OpenAI


from pinecone import Pinecone, ServerlessSpec

# Load environment variables from .env file
load_dotenv()

# Download NLTK resources if necessary
nltk.download("punkt")
nltk.download("punkt_tab")  # Ensure punkt_tab is available

# Load API keys and configuration from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

print("DEBUG: OPENAI_API_KEY =", OPENAI_API_KEY)
print("DEBUG: PINECONE_API_KEY =", PINECONE_API_KEY)
print("DEBUG: PINECONE_REGION =", PINECONE_REGION)

if not OPENAI_API_KEY or not PINECONE_API_KEY:
    raise Exception("Missing API keys in environment variables.")

# # Configure OpenAI API key and type
# openai.api_key = OPENAI_API_KEY
# openai.api_type = "openai"  # explicitly set API type

client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Pinecone instance and create index if needed
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "rasa-text-embedding-3-small-test"
dimension = 1536

print(f"DEBUG: Checking if index '{index_name}' exists.")
if not pc.has_index(index_name):
    print(f"DEBUG: Index '{index_name}' not found. Creating index...")
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_REGION)
    )
else:
    print(f"DEBUG: Index '{index_name}' exists.")

index = pc.Index(index_name)
print("DEBUG: Connected to Pinecone index.")

# FastAPI app instance
app = FastAPI()

# Settings
BATCH_SIZE = 250
MAX_CHUNK_LENGTH = 200  # Maximum characters per chunk

def embed(docs: List[str]) -> List[List[float]]:
    print("DEBUG: Embedding documents:", docs)
    response = client.embeddings.create(
        input=docs,
        model="text-embedding-3-small"
    )
    embeddings = [r.embedding for r in response.data]
    print("DEBUG: Received embeddings of length:", len(embeddings))
    return embeddings

def split_into_sentence_chunks(text: str, max_chunk_length: int) -> List[str]:
    print("DEBUG: Splitting text into chunks...")
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chunk_length:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk = f"{current_chunk} {sentence}" if current_chunk else sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    print("DEBUG: Created", len(chunks), "chunks.")
    return chunks

def read_pdf(pdf_path: str) -> str:
    print("DEBUG: Reading PDF from:", pdf_path)
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    print(f"DEBUG: Extracted text from page {i+1}.")
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")

# Pydantic models for requests
class IngestPDFRequest(BaseModel):
    pdf_path: str

class QueryRequest(BaseModel):
    query: str

@app.post("/ingest")
def ingest_document(req: IngestPDFRequest):
    print("DEBUG: Ingest endpoint called with:", req.pdf_path)
    try:
        file_contents = read_pdf(req.pdf_path)
        print("DEBUG: Read PDF content. Length:", len(file_contents))
    except Exception as e:
        print("DEBUG: Error reading PDF:", e)
        raise HTTPException(status_code=400, detail=str(e))
    
    # Split document text into sentence chunks
    chunks = split_into_sentence_chunks(file_contents, MAX_CHUNK_LENGTH)
    # Filter out very short chunks
    chunks = [chunk for chunk in chunks if len(chunk) >= 10]
    print("DEBUG: Number of valid chunks to ingest:", len(chunks))

    # Process and upsert chunks into Pinecone in batches
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        print(f"DEBUG: Processing batch {i//BATCH_SIZE + 1} with {len(batch)} chunks.")
        embeddings = embed(batch)
        vectors = []
        for chunk, emb in zip(batch, embeddings):
            vectors.append({
                "id": str(uuid.uuid4()),
                "values": emb,
                "metadata": {"text": chunk},
            })
        print("DEBUG: Upserting", len(vectors), "vectors into Pinecone.")
        index.upsert(vectors=vectors, namespace="ns1")
        time.sleep(1)  # Small delay to handle rate limits

    return {"status": "success", "chunks_ingested": len(chunks)}

@app.post("/query")
def query_document(req: QueryRequest):
    print("DEBUG: Query endpoint called with query:", req.query)
    query_embedding = embed([req.query])[0]
    print("DEBUG: Query embedding computed.")
    results = index.query(
        namespace="ns1",
        vector=query_embedding,
        top_k=3,
        include_values=False,
        include_metadata=True,
    )
    print("DEBUG: Query returned results from Pinecone.")
    print("DEBUG: Results:", results)
    
    # Extract context from results matches if available
    context = ""
    if hasattr(results, "matches") and results.matches:
        context = " ".join([match.metadata.get("text", "") for match in results.matches])
    else:
        context = ""
    
    # If no context is found, return a predefined reply.
    if not context.strip():
        predefined_reply = "I'm sorry, I couldn't find any relevant information regarding your query."
        print("DEBUG: No context found. Returning predefined reply.")
        return {"query": req.query, "answer": predefined_reply}
    
    # Otherwise, build a prompt with the extracted context.
    prompt = f"Using the following context, answer the user's question in 1 small paragraph only and if you are not sure just say contact HR for more details.\nContext: {context}\nUser question: {req.query}"
    print("DEBUG: Prompt for LLM:", prompt)
    
    # Call the OpenAI ChatCompletion API to generate a reply.
    completion = client.chat.completions.create(
         model="gpt-4o-mini",
         messages=[{"role": "user", "content": prompt}]
    )
    answer = completion.choices[0].message.content
    print("DEBUG: LLM answer:", answer)
    
    return {"query": req.query, "answer": answer}

@app.get("/")
def read_root():
    print("DEBUG: Root endpoint called.")
    return {"message": "Welcome to the PDF QA API."}

if __name__ == "__main__":
    import uvicorn
    print("DEBUG: Starting server...")
    uvicorn.run("pdf_rag:app", host="0.0.0.0", port=8000, reload=True)
