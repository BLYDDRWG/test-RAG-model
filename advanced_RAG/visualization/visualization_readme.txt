# Visualization Module Documentation

## Overview

The `visualization` module provides tools for creating visual representations of document embeddings and retrieval strategies. It supports UMAP-based dimensionality reduction, strategy comparison, and query result visualization. These visualizations help users understand the relationships between documents and the effectiveness of different RAG strategies.

## Key Features

- **UMAP Dimensionality Reduction**: Projects high-dimensional embeddings into 2D space for visualization.
- **Query Result Visualization**: Displays retrieved documents and their relationships to the query.
- **Strategy Comparison**: Compares the performance of different RAG strategies visually.
- **Interactive Visualizations**: Generates visualizations that can be embedded in the UI or exported.

## File Structure

visualization/ 
├── init.py # Module initializer 
├── embedding.py # Embedding generation for visualization 
├── enhanced_viz.py # Enhanced visualization tools for RAG strategies 
├── retrieval_viz.py # Retrieval visualization tools 
├── viz_service.py # FastAPI service for visualization endpoints 
├── requirements_viz.txt # Visualization-specific dependencies 
└── visualization_readme.txt # Documentation for the visualization module


## Functions in `enhanced_viz.py`

### 1. `initialize_dataset(sample_texts=None, collection_name="test_data", sample_size=300)`
Initializes dataset embeddings for background visualization.

- **Input**:
  - `sample_texts`: List of texts to use as the dataset (optional).
  - `collection_name`: Database collection to sample from if `sample_texts` is not provided.
  - `sample_size`: Number of documents to sample.
- **Output**: Initializes UMAP embeddings for the dataset.

### 2. `visualize_query_results(query, retrieved_docs, synthetic_queries=None)`
Creates a visualization of query results and their relationships.

- **Input**:
  - `query`: Original query text.
  - `retrieved_docs`: List of retrieved documents.
  - `synthetic_queries`: Optional list of synthetic queries.
- **Output**: Base64-encoded PNG image of the visualization.

### 3. `compare_strategies(query, results_by_strategy)`
Generates a comparison visualization for different RAG strategies.

- **Input**:
  - `query`: The query text.
  - `results_by_strategy`: Dictionary mapping strategy names to their retrieved documents.
- **Output**: Base64-encoded PNG image comparing strategies.

## Functions in `retrieval_viz.py`

### 1. `visualize_query_results(query, retrieved_docs, n_neighbors=15, min_dist=0.1)`
Visualizes query results using UMAP projection.

- **Input**:
  - `query`: The query text.
  - `retrieved_docs`: List of retrieved document chunks.
  - `n_neighbors`: UMAP parameter for local neighborhood size.
  - `min_dist`: UMAP parameter for minimum distance.
- **Output**: Base64-encoded PNG image and reduced embeddings.

### 2. `compare_strategies(query, results_by_strategy, n_neighbors=15, min_dist=0.1)`
Creates a comparison visualization for different RAG strategies.

- **Input**:
  - `query`: The query text.
  - `results_by_strategy`: Dictionary mapping strategy names to their retrieved documents.
  - `n_neighbors`: UMAP parameter for local neighborhood size.
  - `min_dist`: UMAP parameter for minimum distance.
- **Output**: Base64-encoded PNG image.

## API Endpoints in `viz_service.py`

### `POST /visualize-query`
Generates a visualization for a query and its retrieved documents.

**Request:**
```json
{
  "query": "example query",
  "collection_name": "test_data",
  "top_k": 5,
  "strategy": "naive"
}
```

**Response:**
```json
{
  "image_base64": "base64-encoded-image",
  "num_docs": 5,
  "strategy": "naive"
}
```

### `POST /compare-strategies
Generates a comparison visualization for different RAG strategies.

**Request:**
```json
{
  "query": "example query",
  "collection_name": "test_data",
  "top_k": 5,
  "strategies": ["naive", "synthetic_answers", "synthetic_queries"]
}

**Response**
```json
{
  "image_base64": "base64-encoded-image",
  "strategies": ["naive", "synthetic_answers", "synthetic_queries"]
}

## `GET /health
Checks the health of the visualization service.

**Response:**
```json
{
  "status": "healthy"
}

## Environment Variables
The following environment variables must be set for the visualization module to function:

API_KEY=your_api_key
LLM_SERVICE_URL=http://llm-service:8000
DATABASE_SERVICE_URL=http://doc-processor-api:8000

## Example Usage

```python
from visualization.enhanced_viz import EnhancedRetrievalVisualization

visualizer = EnhancedRetrievalVisualization()
query = "What is progressive overload?"
retrieved_docs = [
    {"text": "Progressive overload is a training principle...", "metadata": {"source": "example.pdf"}},
    {"text": "It involves gradually increasing the stress...", "metadata": {"source": "example2.pdf"}}
]
image_base64 = visualizer.visualize_query_results(query, retrieved_docs)
print("Visualization Image (Base64):", image_base64)

query = "Describe the Wendler 5/3/1 program."
results_by_strategy = {
    "naive": [{"text": "Wendler 5/3/1 is a strength training program...", "metadata": {"source": "doc1.pdf"}}],
    "synthetic_answers": [{"text": "The program focuses on progressive overload...", "metadata": {"source": "doc2.pdf"}}]
}
image_base64 = visualizer.compare_strategies(query, results_by_strategy)
print("Comparison Visualization (Base64):", image_base64)
```
## Notes

- Ensure the API_KEY, LLM_SERVICE_URL, and DATABASE_SERVICE_URL environment variables are correctly set before running the visualization module.
- UMAP parameters (n_neighbors and min_dist) can be adjusted for different datasets to improve visualization quality.
- Visualizations are returned as Base64-encoded PNG images, which can be embedded in the UI or saved locally.




