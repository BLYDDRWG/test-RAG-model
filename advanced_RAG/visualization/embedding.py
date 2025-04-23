#Provides embedding generation specifically for visualization components
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text, retry_count=3):
    """Generate embeddings using OpenAI API with error handling and retry logic"""
    # Basic text cleaning
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
            
            # Truncate to match collection dimensions
            if len(embedding) > 1024:
                print(f"Truncating embedding from {len(embedding)} to 1024 dimensions")
                embedding = embedding[:1024]
                
            return embedding
            
        except Exception as e:
            if attempt == retry_count - 1:
                raise Exception(f"Failed to generate embedding after {retry_count} attempts: {e}")
            print(f"Embedding generation failed (attempt {attempt+1}/{retry_count}): {e}")
            import time
            time.sleep(2)  # Wait before retry