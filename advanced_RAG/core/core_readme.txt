# Core Module Documentation

## Overview

The `core` module is responsible for document processing, including text extraction, chunking, and embedding generation. It serves as the backbone of the Advanced RAG system, preparing documents for storage and retrieval.

## Key Features

- **Text Extraction**: Supports multiple file formats (PDF, TXT, Markdown, JSON)
- **Chunking**: Splits long documents into manageable chunks for efficient processing
- **Embedding Generation**: Creates vector embeddings for each chunk using OpenAI's API
- **Metadata Handling**: Adds metadata to each chunk for better traceability and searchability

## File Structure

core/ 
    ├── init.py # Module initializer 
    ├── core_readme.txt # Documentation for the core module 
    └── doc_processor.py # Main document processing logic


## Functions in `doc_processor.py`

### 1. `extract_text_from_pdf(file_path)`
Extracts text from PDF files and identifies potential headers.

- **Input**: Path to the PDF file
- **Output**: Extracted text and potential headers
- **Error Handling**: Raises `FileNotFoundError` or `ValueError` for unreadable files

### 2. `extract_text_from_txt(file_path)`
Reads text files with UTF-8 encoding and falls back to Latin-1 if needed.

- **Input**: Path to the text file
- **Output**: Extracted text
- **Error Handling**: Handles missing or corrupted files

### 3. `extract_text_from_markdown(file_path)`
Processes Markdown files, extracting headers and Obsidian-style links.

- **Input**: Path to the Markdown file
- **Output**: Extracted text and metadata (headers, links)

### 4. `extract_text_from_json(file_path)`
Extracts and formats text from JSON files while preserving structure.

- **Input**: Path to the JSON file
- **Output**: Formatted text
- **Error Handling**: Raises `ValueError` for invalid JSON

### 5. `split_text(text, chunk_size=750, chunk_overlap=75)`
Splits long text into smaller chunks while maintaining overlap for context continuity.

- **Input**: Text to split, chunk size, and overlap size
- **Output**: List of text chunks

### 6. `get_embedding(text, retry_count=3)`
Generates vector embeddings for text using OpenAI's API with retry logic.

- **Input**: Text to embed and retry count
- **Output**: Vector embedding
- **Error Handling**: Raises `ValueError` for empty text or API failures

### 7. `process_document(file_path, chunk_size=750, chunk_overlap=75)`
Processes a document by extracting text, splitting it into chunks, and generating embeddings.

- **Input**: Path to the document, chunk size, and overlap size
- **Output**: List of dictionaries containing:
  - `text`: Chunk text
  - `embedding`: Vector representation
  - `metadata`: Document metadata (filename, chunk ID, etc.)
- **Error Handling**: Handles unsupported file types and extraction errors

## Supported File Formats

- **PDF**: Extracts text and identifies headers
- **TXT**: Reads plain text files
- **Markdown**: Processes headers and Obsidian-style links
- **JSON**: Formats structured data into readable text

## Environment Variables

- `OPENAI_API_KEY`: API key for OpenAI embedding generation

## Example Usage

### Processing a Document
```python
from core.doc_processor import process_document

file_path = "example.pdf"
results = process_document(file_path, chunk_size=750, chunk_overlap=75)

for chunk in results:
    print(f"Chunk Text: {chunk['text']}")
    print(f"Embedding Length: {len(chunk['embedding'])}")
    print(f"Metadata: {chunk['metadata']}")

from core.doc_processor import extract_text_from_markdown

file_path = "example.md"

text, metadata = extract_text_from_markdown(file_path)

print("Extracted Text:", text)
print("Headers:", metadata['headers'])
print("Wiki Links:", metadata['wiki_links'])

## Notes
Ensure that the OPENAI_API_KEY environment variable is set before running any embedding-related functions.
The chunking logic is optimized for text documents with approximately 150 words per chunk.
Metadata is critical for traceability and searchability in the RAG system.