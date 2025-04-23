from astrapy import DataAPIClient
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

DEFAULT_COLLECTION = "test_data"

def initialize_collection(collection_name=DEFAULT_COLLECTION):
    try:
        client = DataAPIClient(os.getenv("DB_TOKEN"))
        db = client.get_database_by_api_endpoint(os.getenv("ASTRA_DB_ENDPOINT"))
        
        print(f"Connected to Astra DB: {db.list_collection_names()}")
        
        # Check if collection exists
        all_collections = db.list_collection_names()
        if collection_name in all_collections:
            print(f"Using existing collection: {collection_name}")
            return db.get_collection(collection_name)
        
        # Create new collection with hybrid search enabled
        print(f"Creating new collection with hybrid search: {collection_name}")
        return db.create_collection(
            collection_name=collection_name,
            vector_dimension=1024,  # Based on your current dimension truncation
            options={
                "vector": {"enabled": True},
                "lexical": {"enabled": True},  # Enable lexical search
                "rerank": {"enabled": True}    # Enable reranking
            }
        )
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise

def get_collection(collection_name=DEFAULT_COLLECTION):
    """Get a reference to the vector collection for querying"""
    return initialize_collection(collection_name)

def store_document_chunks(chunks, collection_name=DEFAULT_COLLECTION):
    """Store document chunks with their embeddings in the database"""
    collection = initialize_collection(collection_name)
    
    # Process and store each chunk
    for chunk in chunks:
        # Ensure vectors match collection dimensions
        if len(chunk["embedding"]) != 1024:
            print(f"WARNING: Truncating vector from {len(chunk['embedding'])} to 1024 dimensions")
            chunk["embedding"] = chunk["embedding"][:1024]
        
        print(f"DEBUG - Embedding dimensions: {len(chunk['embedding'])}")
        # Create document with the correct structure for hybrid search
        document = {
            "_id": str(uuid.uuid4()),
            "text": chunk["text"],
            "$vector": chunk["embedding"],
            "$lexical": chunk["text"],  # Add lexical field for hybrid search
            "metadata": chunk["metadata"]
        }
        
        try:
            collection.insert_one(document)
        except Exception as e:
            print(f"Error inserting document: {str(e)}")
    
    return len(chunks)

# For better performance with large document sets
def store_document_chunks_batch(chunks, batch_size=100, collection_name=DEFAULT_COLLECTION):
    collection = initialize_collection(collection_name)
    successful_inserts = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        documents = {}
        for chunk in batch:
            print(f"DEBUG - Embedding dimensions: {len(chunk['embedding'])}")
            doc_id = str(uuid.uuid4())
            documents[doc_id] = {
                "text": chunk["text"],
                "$vector": chunk["embedding"],
                "$lexical": chunk["text"],  # Add lexical field for hybrid search
                "metadata": chunk["metadata"]
            }
        
        try:
            collection.insert_many(documents=documents)
            successful_inserts += len(batch)
            print(f"Progress: {successful_inserts}/{len(chunks)} chunks processed")
        except Exception as e:
            print(f"Error inserting batch {i//batch_size + 1}: {e}")
    
    return successful_inserts