#!/usr/bin/env python
"""
LLM Query Service Entry Point
"""
import sys
import os
import requests
from .query import query_documents, generate_synthetic_queries  # Fix this import
from .response import generate_response  # Fix this import
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

API_KEY = os.getenv("API_KEY")
API_URL = "http://doc-processor-api:8000/process-document"  # Replace with actual endpoint

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    strategy: str = "naive"  # "naive", "synthetic_answers", "synthetic_queries"
    strategy_params: Optional[Dict[str, Any]] = None

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    try:
        # Get relevant documents using the specified strategy
        results = query_documents(
            query=request.query,
            top_k=request.top_k,
            strategy=request.strategy,
            strategy_params=request.strategy_params
        )
        
        # Generate response from the retrieved documents
        response_data = generate_response(request.query, results)
        
        # The response now returns a dict with text and sources
        response_text = response_data["text"]
        detailed_sources = response_data["sources"]
        
        return {
            "query": request.query,
            "strategy": request.strategy,
            "response": response_text,
            "sources": detailed_sources,
            "documents": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add this endpoint

class SyntheticQueryRequest(BaseModel):
    query: str
    num_queries: int = 3

@app.post("/generate-synthetic-queries")
async def generate_synthetic_queries_endpoint(request: SyntheticQueryRequest):
    try:
        queries = generate_synthetic_queries(
            request.query, 
            num_queries=request.num_queries
        )
        return {"queries": queries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating synthetic queries: {str(e)}")

def get_processed_document(file_path):
    headers = {"X-API-Key": API_KEY}
    files = {'file': open(file_path, 'rb')}
    try:
        response = requests.post(API_URL, headers=headers, files=files)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting document: {e}")
        return None

def print_help():
    print("LLM Query Service")
    print("Usage:")
    print("  query <text>   - Query the database with the given text")
    print("  help           - Show this help message")

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "help":
        print_help()
        return
    
    if sys.argv[1] == "query" and len(sys.argv) > 2:
        query_text = " ".join(sys.argv[2:])
        print(f"Querying with: {query_text}")
        results = query_documents(query_text)
        response = generate_response(query_text, results)
        print(f"\nResponse: {response}")
    else:
        print("Invalid command")
        print_help()

if __name__ == "__main__":
    import sys
    import time
    
    # Check for serve mode
    if len(sys.argv) > 1 and sys.argv[1] == 'serve':
        print("Starting LLM Query Service in server mode...")
        while True:
            time.sleep(60)  # Sleep for 1 minute
            print("LLM Query Service is running...")
    else:
        # Original behavior
        main()