# processes a document to extract text and generate an embedding

import PyPDF2
from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # More efficient than string concatenation in a loop
            text_parts = [page.extract_text() for page in reader.pages]
            
            # Add potential header detection (heuristic)
            potential_headers = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                lines = page_text.split('\n')
                # Identify likely headers (short lines, ending without periods)
                for line in lines:
                    line = line.strip()
                    if 3 < len(line) < 100 and not line.endswith('.') and line.strip():
                        potential_headers.append((i, line))
            
            return "\n".join(text_parts), potential_headers
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    except PyPDF2.errors.PdfReadError:
        raise ValueError(f"Error reading PDF file: {file_path}")

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Text file not found: {file_path}")
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()

def extract_text_from_markdown(file_path):
    """Extract text with header structure and process Obsidian links"""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        content = file.read()
        
    # Parse headers and structure to enhance metadata
    headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
    
    # Extract Obsidian links
    wiki_links = re.findall(r'\[\[(.*?)(?:\|(.*?))?\]\]', content)
    
    # Process metadata including links
    metadata = {
        'headers': headers,
        'wiki_links': [link[0] for link in wiki_links]  # Extract link targets
    }
    
    return content, metadata

def extract_text_from_json(file_path):
    """Extract text from JSON file with structure preservation"""
    import json
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Format JSON data as readable text
        formatted_text = json.dumps(data, indent=2)
        return formatted_text
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {file_path}")

def get_embedding(text, retry_count=3):
    """
    Generate embeddings using OpenAI API with error handling and retry logic
    
    Args:
        text: The input text to embed
        retry_count: Number of retries on API errors
    
    Returns:
        List containing the embedding vector
    """
    # Basic text cleaning (optional)
    text = text.strip()
    
    # Check if text is empty
    if not text:
        raise ValueError("Cannot generate embedding for empty text")
        
    # Attempt to generate embedding with retries
    for attempt in range(retry_count):
        try:
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding
            
            # Validate embedding dimensions
            print(f"DEBUG - Raw embedding dimensions: {len(embedding)}")
            assert len(embedding) == 1536, f"Expected 1536 dimensions, got {len(embedding)}"
            
            return embedding
        except Exception as e:
            if attempt == retry_count - 1:
                raise Exception(f"Failed to generate embedding after {retry_count} attempts: {e}")
            print(f"Embedding generation failed (attempt {attempt+1}/{retry_count}): {e}")
            time.sleep(2)  # Wait before retry

def process_document(file_path, chunk_size=750, chunk_overlap=75):
    """
    Process a document by extracting text, chunking if necessary, and generating embeddings
    
    Args:
        file_path: Path to the document file
        chunk_size: Maximum size of text chunks (approx. 150 words)
        chunk_overlap: Overlap between consecutive chunks (approx. 10% or 15 words)
        
    Returns:
        List of dictionaries containing: 
        - text: Document text or chunk
        - embedding: Vector representation
        - metadata: Document information (filename, path, chunk_id if applicable)
    """
    # Extract file metadata
    filename = os.path.basename(file_path)
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Extract text based on file type
    if file_extension == '.pdf':
        text, headers = extract_text_from_pdf(file_path)
    elif file_extension == '.txt':
        text = extract_text_from_txt(file_path)  # No headers returned
    elif file_extension in ['.md', '.markdown']:
        text, headers = extract_text_from_markdown(file_path)
    elif file_extension == '.json':
        text = extract_text_from_json(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    # Split text into chunks if it's long
    chunks = split_text(text, chunk_size, chunk_overlap)
    
    # Process each chunk
    results = []
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        results.append({
            'text': chunk,
            'embedding': embedding,
            'metadata': {
                'filename': filename,
                'source_path': file_path,
                'chunk_id': i if len(chunks) > 1 else None,
                'total_chunks': len(chunks) if len(chunks) > 1 else None
            }
        })
    
    return results

def split_text(text, chunk_size=750, chunk_overlap=75):
    """
    Split text into chunks while preserving Obsidian link integrity
    """
    if len(text) <= chunk_size:
        return [text]
        
    chunks = []
    start = 0
    
    # Find all wiki link positions to avoid breaking them
    link_positions = [(m.start(), m.end()) for m in re.finditer(r'\[\[.*?\]\]', text)]
    
    while start < len(text):
        end = start + chunk_size
        
        # Don't break in the middle of a link
        for link_start, link_end in link_positions:
            if start < link_start < end < link_end:
                # Adjust end to before link start
                end = link_start
        
        # Try to find a good break point
        break_point = text.rfind('\n', start + chunk_size - chunk_overlap, end)
        if break_point == -1:
            break_point = text.rfind(' ', start + chunk_size - chunk_overlap, end)
        if break_point == -1:
            break_point = end
            
        chunks.append(text[start:break_point])
        start = break_point
        start = end - chunk_overlap
    
    return chunks