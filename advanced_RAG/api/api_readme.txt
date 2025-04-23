# API Service Documentation

## Overview

The API module provides RESTful endpoints for interacting with the Advanced RAG system. It handles document processing, retrieval operations, and visualization data access with secure authentication and rate limiting protection.

## Authentication

All API endpoints are protected with API key authentication:

- API keys must be provided in the `X-API-Key` header
- Keys are configured through the `API_KEY` environment variable
- Unauthorized requests return a 401 error with appropriate headers

### Example Authenticated Request
```python
import requests

headers = {"X-API-Key": "your-api-key-here"}
response = requests.post("http://localhost:8000/process-document", 
                        headers=headers,
                        files={"file": open("document.pdf", "rb")})
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- Document processing: 5 requests per minute
- Error responses include Retry-After headers
- Exceeding limits returns 429 Too Many Requests

## Endpoints

### Document Processing

**POST /process-document**

Process and index a document into the RAG system.

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Body: file (PDF, TXT, or DOCX)

**Response:**

```json
{
  "filename": "example.pdf",
  "chunks": 15,
  "status": "success"
}
```

### Health Checks

**GET /health**

Check service health and configuration status.

**Response:**

```json
{
  "status": "ok",
  "service": "doc-processor-api"
}
```

### Data Sampling

**POST /sample-documents**

Retrieve random document samples from the database for visualization.

**Request:**

```json
{
  "collection_name": "test_data",
  "sample_size": 100
}
```

**Response:**

```json
{
  "documents": [...],
  "count": 100
}
```

## Error Handling

The API returns standardized error responses:

- 400: Bad Request - Invalid input format
- 401: Unauthorized - Missing or invalid API key
- 429: Too Many Requests - Rate limit exceeded
- 500: Internal Server Error - Processing errors

All error responses include a detail message explaining the issue.

## Code Structure

- `auth.py`: API key authentication handling
- `doc_processor_api.py`: Main API endpoints and request handlers
- `rate_limiting.py`: Request rate limiting setup
- `validations.py`: Input validation functions

## Environment Variables

- `API_KEY`: Authentication key for API access
- `API_URL`: Internal service URL for document processing

## Example Usage

### Processing a Document

```python
import requests

api_url = "http://localhost:8000/process-document"
headers = {"X-API-Key": "your-api-key-here"}

with open("document.pdf", "rb") as file:
    files = {"file": file}
    response = requests.post(api_url, headers=headers, files=files)

print(response.json())
```

### Health Check

```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())