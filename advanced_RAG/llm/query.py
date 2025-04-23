import os
from typing import List, Dict, Any
from database.database_mgmt import get_collection
from openai import OpenAI
from .advanced_strategies import generate_synthetic_answers, generate_synthetic_queries

def query_documents(query, collection_name="test_data", top_k=3, n_results=None, 
                   strategy="naive", strategy_params=None):
    """
    Query the vector database for documents similar to the query text.
    
    Args:
        query: Text query to search for
        collection_name: Name of collection to search
        top_k: Number of results to return
        n_results: Alias for top_k (for backward compatibility)
        strategy: RAG strategy to use: "naive", "synthetic_answers", or "synthetic_queries"
        strategy_params: Additional parameters for the chosen strategy
    """
    # Use n_results if provided, otherwise use top_k
    limit = n_results if n_results is not None else top_k
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # Get the collection
        collection = get_collection(collection_name)
        found_docs = []
        
        # Add at the top of query_documents function for testing
        test_results = collection.find(
            filter={},
            sort={"$vector": [0.1] * 1024},  # Simple random vector
            limit=5
        )
        print("TEST FIND RESULTS:")
        for item in test_results:
            print(f"- Document: {item.keys()}")

        # Then do your normal query...
        
        if strategy == "naive":
            # Standard RAG approach (original implementation)
            response = client.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            )
            query_embedding = response.data[0].embedding
            
            # Debug logging
            print(f"Query embedding length: {len(query_embedding)}")
            
            # Truncate to match collection dimensions
            if len(query_embedding) > 1024:
                print(f"Truncating query vector from {len(query_embedding)} to 1024 dimensions")
                query_embedding = query_embedding[:1024]
            
            try:
                # True hybrid search with reranking
                results = collection.find_and_rerank(
                    filter={},  # Optional filter criteria
                    sort={"$hybrid": {"$vector": query_embedding, "$lexical": query}},
                    limit=limit,
                    rerank_query=query,
                    rerank_on="$lexical", # Rerank based on lexical match
                    include_scores=True  # Optional, to see ranking scores
                )
                
                found_docs = process_results(results)
                
            except Exception as e:
                print(f"Hybrid search failed: {e}")
                # Fallback to simple vector search
                results = collection.find(
                    filter={},
                    sort={"$vector": query_embedding},
                    limit=limit
                )
                found_docs = process_results(results)
                
        elif strategy == "synthetic_answers":
            # Generate synthetic answers strategy
            print(f"Generating synthetic answers for query: {query}")
            synthetic_answers = generate_synthetic_answers(query, num_answers=3)
            
            # Embed each synthetic answer and query for similar documents
            all_results = []
            for answer in synthetic_answers:
                print(f"Processing synthetic answer: {answer[:50]}...")
                response = client.embeddings.create(
                    input=answer,
                    model="text-embedding-3-small"
                )
                answer_embedding = response.data[0].embedding
                
                # Truncate to match collection dimensions
                if len(answer_embedding) > 1024:
                    print(f"Truncating answer vector from {len(answer_embedding)} to 1024 dimensions")
                    answer_embedding = answer_embedding[:1024]
                
                try:
                    # True hybrid search with reranking
                    results = collection.find_and_rerank(
                        filter={},
                        sort={"$hybrid": {"$vector": answer_embedding, "$lexical": answer}},
                        limit=limit,
                        rerank_query=answer,
                        rerank_on="$lexical", # Rerank based on lexical match
                        include_scores=True
                    )
                    all_results.extend(process_results(results))
                except Exception as e:
                    print(f"Error with synthetic answer: {e}")
            
            # Deduplicate results by text content
            seen_texts = set()
            found_docs = []
            for doc in all_results:
                if doc["text"] not in seen_texts:
                    seen_texts.add(doc["text"])
                    found_docs.append(doc)
                    if len(found_docs) >= limit:
                        break
            
        elif strategy == "synthetic_queries":
            # Generate synthetic queries strategy
            print(f"Generating synthetic queries for: {query}")
            synthetic_queries = generate_synthetic_queries(query, num_queries=3)
            synthetic_queries.insert(0, query)  # Include original query
            
            # Embed each query and find similar documents
            all_results = []
            for q in synthetic_queries:
                print(f"Processing query: {q[:50]}...")
                response = client.embeddings.create(
                    input=q,
                    model="text-embedding-3-small"
                )
                q_embedding = response.data[0].embedding
                
                # Truncate to match collection dimensions
                if len(q_embedding) > 1024:
                    print(f"Truncating synthetic query vector from {len(q_embedding)} to 1024 dimensions")
                    q_embedding = q_embedding[:1024]
                
                try:
                    results = collection.find_and_rerank(
                        filter={},
                        sort={"$hybrid": {"$vector": q_embedding, "$lexical": q}},
                        limit=limit // len(synthetic_queries) + 1,
                        rerank_query=q,
                        rerank_on="$lexical",
                        include_scores=True
                    )
                    
                    query_results = process_results(results)
                    print(f"Query '{q[:20]}...' found {len(query_results)} documents")
                    all_results.extend(query_results)
                except Exception as e:
                    print(f"Error with synthetic query: {e}")
            
            # Deduplicate results
            seen_texts = set()
            found_docs = []
            for doc in all_results:
                if doc["text"] not in seen_texts:
                    seen_texts.add(doc["text"])
                    found_docs.append(doc)
                    if len(found_docs) >= limit:
                        break
                    
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
            
        print(f"Processed {len(found_docs)} documents")
        return found_docs
            
    except Exception as e:
        print(f"Error in query_documents: {str(e)}")
        return [{"text": f"Error querying database: {str(e)}", "metadata": {}}]

def process_results(results):
    """Helper function to process query results"""
    found_docs = []
    
    try:
        # Process based on result type
        for item in results:
            try:
                # For RerankedResult objects from find_and_rerank
                if hasattr(item, 'document'):
                    doc = item.document
                    found_docs.append({
                        "text": doc.get("text", "No text available"),
                        "metadata": doc.get("metadata", {})
                    })
                # For dictionary results from regular find()
                elif isinstance(item, dict):
                    found_docs.append({
                        "text": item.get("text", "No text available"),
                        "metadata": item.get("metadata", {})
                    })
            except Exception as e:
                print(f"Error processing result item: {e}")
    except Exception as e:
        print(f"Error in process_results: {e}")
    
    print(f"Processed {len(found_docs)} documents")
    return found_docs