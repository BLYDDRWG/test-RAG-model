# Database Module Documentation

## Overview

The `database` module is responsible for managing the connection to Astra DB and handling all database operations for the Advanced RAG system. It supports storing, retrieving, and managing document chunks with hybrid search capabilities.

## Key Features

- **Astra DB Integration**: Connects to Astra DB using the DataStax API
- **Hybrid Search Support**: Enables vector, lexical, and reranking search capabilities
- **Document Storage**: Stores document chunks with embeddings and metadata
- **Batch Operations**: Optimized for storing large document sets in batches

## File Structure

database/ 
    ├── init.py # Module initializer 
    ├── database_mgmt.py # Core database management logic 
    ├── database_service.py # Service layer for database operations 
    └── database_readme.txt # Documentation for the database module


## Functions in `database_mgmt.py`

### 1. `initialize_collection(collection_name=DEFAULT_COLLECTION)`
Initializes a collection in Astra DB with hybrid search capabilities.

- **Input**: `collection_name` (string, optional)
- **Output**: A reference to the initialized collection
- **Error Handling**: Prints and raises exceptions for connection or initialization errors

### 2. `get_collection(collection_name=DEFAULT_COLLECTION)`
Retrieves a reference to an existing collection in Astra DB.

- **Input**: `collection_name` (string, optional)
- **Output**: A reference to the collection

### 3. `store_document_chunks(chunks, collection_name=DEFAULT_COLLECTION)`
Stores document chunks with their embeddings in the database.

- **Input**:
  - `chunks`: List of dictionaries containing `text`, `embedding`, and `metadata`
  - `collection_name`: Name of the collection to store the chunks
- **Output**: None
- **Error Handling**: Truncates embeddings to 1024 dimensions if necessary

### 4. `store_document_chunks_batch(chunks, batch_size=100, collection_name=DEFAULT_COLLECTION)`
Stores document chunks in batches for better performance with large datasets.

- **Input**:
  - `chunks`: List of dictionaries containing `text`, `embedding`, and `metadata`
  - `batch_size`: Number of chunks to store in each batch
  - `collection_name`: Name of the collection to store the chunks
- **Output**: None

## Environment Variables

The following environment variables must be set for the database module to function:

- `DB_TOKEN`: Astra DB authentication token
- `ASTRA_DB_ENDPOINT`: Astra DB API endpoint

These should be configured in a `.env` file in the root directory.

## Example Usage

### Initializing a Collection
```python
from database.database_mgmt import initialize_collection

collection = initialize_collection("test_data")

Storing Document Chunks

from database.database_mgmt import store_document_chunks

chunks = [
    {
        "text": "Example chunk text",
        "embedding": [0.1, 0.2, 0.3, ...],  # 1024-dimensional vector
        "metadata": {"source": "example.pdf", "chunk_index": 1}
    }
]

store_document_chunks(chunks, collection_name="test_data")

Batch Storing Document Chunks

from database.database_mgmt import store_document_chunks_batch

chunks = [
    {
        "text": "Example chunk text",
        "embedding": [0.1, 0.2, 0.3, ...],  # 1024-dimensional vector
        "metadata": {"source": "example.pdf", "chunk_index": 1}
    },
    # Add more chunks here
]

store_document_chunks_batch(chunks, batch_size=50, collection_name="test_data")

## Notes

Ensure that the DB_TOKEN and ASTRA_DB_ENDPOINT environment variables are correctly set before running any database operations.
The default collection name is test_data, but this can be customized as needed.
Embeddings are truncated to 1024 dimensions to match the collection's vector dimension.

## Error Handling

Connection Errors: Prints and raises exceptions if the database connection fails.
Chunk Validation: Ensures that embeddings are truncated to the correct dimensions before storage.
Batch Operations: Handles partial failures gracefully by retrying failed batches.

## Supported Features

Vector Search: Finds documents based on semantic similarity.
Lexical Search: Finds documents based on keyword matching.
Reranking: Combines vector and lexical search results for improved relevance.