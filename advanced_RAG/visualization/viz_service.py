import os
import requests
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from typing import List, Dict, Any
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(title="RAG Visualization Service")

# Import your visualization module
from visualization.enhanced_viz import EnhancedRetrievalVisualization

# Initialize visualizer
visualizer = EnhancedRetrievalVisualization()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key authentication
API_KEY = os.getenv("API_KEY")
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if not API_KEY or api_key == API_KEY:
        return True
    raise HTTPException(status_code=401, detail="Unauthorized")

class QueryRequest(BaseModel):
    query: str
    strategy: str = "naive"
    top_k: int = 3
    collection_name: str = "test_data"

class CompareStrategiesRequest(BaseModel):
    query: str
    strategies: List[str] = ["naive", "synthetic_answers", "synthetic_queries"]
    top_k: int = 3
    collection_name: str = "test_data"

# Simple function to query documents via the API instead of direct imports
def query_documents(query, collection_name="test_data", top_k=3, strategy="naive"):
    """Query documents via LLM service API instead of importing modules"""
    try:
        # Call the LLM service API
        headers = {"X-API-Key": API_KEY}
        response = requests.post(
            "http://llm-service:8000/query",
            json={
                "query": query,
                "collection_name": collection_name,
                "top_k": top_k,
                "strategy": strategy
            },
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json().get("documents", [])
        else:
            print(f"Error from LLM service: {response.text}")
            return []
    except Exception as e:
        print(f"Error querying documents: {str(e)}")
        return []

@app.post("/visualize-query", dependencies=[Depends(verify_api_key)])
async def visualize_query(request: QueryRequest):
    """Generate visualization for a query and its retrieved documents"""
    try:
        # Get documents based on the query and strategy
        retrieved_docs = query_documents(
            query=request.query,
            collection_name=request.collection_name,
            top_k=request.top_k,
            strategy=request.strategy
        )
        
        # Get synthetic queries if using that strategy
        synthetic_queries = None
        if request.strategy == "synthetic_queries":
            try:
                headers = {"X-API-Key": API_KEY}
                gen_response = requests.post(
                    "http://llm-service:8000/generate-synthetic-queries",
                    json={"query": request.query, "num_queries": 3},
                    headers=headers
                )
                if gen_response.status_code == 200:
                    synthetic_queries = gen_response.json().get("queries", [])
            except Exception as e:
                print(f"Could not get synthetic queries: {e}")
        
        # Generate enhanced visualization
        image_base64 = visualizer.visualize_query_results(
            query=request.query,
            retrieved_docs=retrieved_docs,
            synthetic_queries=synthetic_queries
        )
        
        return {
            "image_base64": image_base64,
            "num_docs": len(retrieved_docs),
            "strategy": request.strategy
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating visualization: {str(e)}")

@app.post("/compare-strategies", dependencies=[Depends(verify_api_key)])
async def compare_strategies(request: CompareStrategiesRequest):
    """Generate comparison visualization for different RAG strategies"""
    try:
        results_by_strategy = {}
        
        # Get results for each strategy
        for strategy in request.strategies:
            docs = query_documents(
                query=request.query,
                collection_name=request.collection_name,
                top_k=request.top_k,
                strategy=strategy
            )
            results_by_strategy[strategy] = docs
        
        # Generate enhanced comparison visualization
        image_base64 = visualizer.compare_strategies(
            query=request.query,
            results_by_strategy=results_by_strategy
        )
        
        return {
            "image_base64": image_base64,
            "strategies": request.strategies
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating comparison: {str(e)}")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}