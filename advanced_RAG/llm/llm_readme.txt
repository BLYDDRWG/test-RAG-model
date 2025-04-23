# LLM Module Documentation

## Overview

The `llm` module is responsible for implementing the core Retrieval-Augmented Generation (RAG) strategies. It handles query processing, document retrieval, and response generation using OpenAI's language models. This module supports multiple RAG strategies, including naive retrieval, synthetic answers, and synthetic queries.

## Key Features

- **Query Processing**: Handles user queries and selects the appropriate RAG strategy.
- **Hybrid Search**: Combines vector and lexical search for improved relevance.
- **Synthetic Strategies**: Generates synthetic answers and queries to enhance retrieval.
- **Response Generation**: Formats and generates responses with source attribution.

## File Structure

llm/ 
├── init.py # Module initializer 
├── query.py # RAG query implementations and strategies 
├── advanced_strategies.py # Synthetic queries and answers generators 
├── response.py # LLM response generation with formatting and source attribution 
└── llm_readme.txt # Documentation for the LLM module


## Functions in `query.py`

### 1. `query_documents(query, collection_name="test_data", strategy="naive", ...)`
Processes a query and retrieves relevant documents using the specified strategy.

- **Input**:
  - `query`: The user query
  - `collection_name`: Name of the database collection
  - `strategy`: Retrieval strategy (`naive`, `synthetic_answers`, `synthetic_queries`)
- **Output**: A list of retrieved documents with metadata and scores.

### 2. `process_results(results)`
Processes the results from the database and formats them for response generation.

- **Input**: Results from the database query
- **Output**: A list of formatted documents.

## Functions in `advanced_strategies.py`

### 1. `generate_synthetic_answers(query, num_answers=3)`
Generates synthetic answers for a query using OpenAI's language model.

- **Input**:
  - `query`: The user query
  - `num_answers`: Number of synthetic answers to generate
- **Output**: A list of synthetic answers.

### 2. `generate_synthetic_queries(query, num_queries=3)`
Expands the original query into multiple related queries for broader retrieval.

- **Input**:
  - `query`: The user query
  - `num_queries`: Number of synthetic queries to generate
- **Output**: A list of synthetic queries.

## Functions in `response.py`

### 1. `generate_response(documents, query)`
Generates a response using the retrieved documents and the user query.

- **Input**:
  - `documents`: List of retrieved documents
  - `query`: The user query
- **Output**: A formatted response with source attribution.

### 2. `format_response(response, sources)`
Formats the response for display, including source attribution.

- **Input**:
  - `response`: The generated response
  - `sources`: List of source documents
- **Output**: A formatted string with the response and sources.

## Environment Variables

- `OPENAI_API_KEY`: API key for OpenAI embedding and completion services.

These variables should be set in a `.env` file in the root directory:
```plaintext
OPENAI_API_KEY=your_openai_api_key
```

## Example Usage

```python
from llm.query import query_documents

query = "Describe the Wendler 5/3/1 program."
results = query_documents(query, strategy="synthetic_answers")

for doc in results:
    print(f"Document Text: {doc['text']}")
    print(f"Metadata: {doc['metadata']}")
```

```python
from llm.advanced_strategies import generate_synthetic_queries

query = "What is progressive overload?"
synthetic_queries = generate_synthetic_queries(query, num_queries=3)

print("Synthetic Queries:")
for sq in synthetic_queries:
    print(sq)
```

```python
from llm.response import generate_response

documents = [
    {"text": "Progressive overload is a training principle...", "metadata": {"source": "example.pdf"}},
    {"text": "It involves gradually increasing the stress...", "metadata": {"source": "example2.pdf"}}
]
query = "What is progressive overload?"
response = generate_response(documents, query)

print("Generated Response:")
print(response)
```
## Notes

- Ensure the OPENAI_API_KEY environment variable is set before running any LLM-related functions.
- The synthetic strategies are designed to enhance retrieval for complex or ambiguous queries.
- The response generation includes source attribution for transparency and traceability.
