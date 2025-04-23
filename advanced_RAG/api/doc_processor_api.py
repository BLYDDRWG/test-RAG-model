from fastapi import FastAPI, UploadFile, status, Depends, Request, Header, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
import os
import sys
from typing import Dict, Any, Optional
import requests
import json

# Add the parent directory to the path so we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.doc_processor import process_document
from api.validations import validate_document
from database.database_mgmt import store_document_chunks, store_document_chunks_batch

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

API_KEY = os.getenv("API_KEY")
API_URL = "http://doc-processor-api:8000/process-document"  # Replace with actual endpoint

@app.post("/process-document")
@limiter.limit("5/minute")
async def api_process_document(request: Request, file: UploadFile, x_api_key: Optional[str] = Header(None)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    # Create upload directory if it doesn't exist
    upload_dir = "/data/upload"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create a temporary file path
    temp_file_path = os.path.join(upload_dir, file.filename)
    
    try:
        # Save file to disk
        file_content = await file.read()
        with open(temp_file_path, "wb") as f:
            f.write(file_content)
        
        # Process the document - this returns chunks with embeddings
        processed_chunks = process_document(temp_file_path)
        
        # Store the chunks in the database
        num_stored = store_document_chunks(processed_chunks)
        
        # Return a simplified response for the client
        return {
            "filename": file.filename,
            "chunks": len(processed_chunks),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        # Return proper error information
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

def send_document_for_processing(file_path):
    headers = {"X-API-Key": API_KEY}
    files = {'file': open(file_path, 'rb')}
    try:
        response = requests.post(API_URL, headers=headers, files=files)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending document: {e}")
        return None

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration and monitoring"""
    try:
        # Verify we can access environment variables
        api_key = os.getenv("API_KEY")
        if not api_key:
            return {"status": "warning", "message": "API_KEY not configured"}
        
        # Basic system check passed
        return {"status": "ok", "service": "doc-processor-api"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/sample-documents")
async def sample_documents(request: dict):
    """Sample random documents from the database for visualization"""
    try:
        collection_name = request.get("collection_name", "test_data")
        sample_size = min(request.get("sample_size", 300), 500)  # Limit to 500 max
        
        from database.database_mgmt import get_collection
        collection = get_collection(collection_name)
        
        # Get random sample by using aggregate with $sample
        documents = []
        try:
            results = collection.aggregate([{"$sample": {"size": sample_size}}])
            documents = list(results)
            
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                if "_id" in doc and not isinstance(doc["_id"], str):
                    doc["_id"] = str(doc["_id"])
        except Exception as e:
            print(f"Error sampling documents: {e}")
        
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sampling documents: {str(e)}")