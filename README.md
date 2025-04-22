This is a retrieval augmented-generation model that was built for interacting with exercise and sports science information. As well as a way to evaluate different RAG components and see how they change the RAG model response.


## Overview

This advanced Retrieval-Augmented Generation (RAG) system implements a sophisticated document retrieval and generation pipeline leveraging hybrid search capabilities. The system features multiple retrieval strategies:

1. **Standard (Naive) RAG**: Direct document retrieval based on query relevance
2. **Synthetic Answers RAG**: Generates potential answers first, then retrieves supporting documents
3. **Synthetic Queries RAG**: Expands the original query into multiple related queries for broader retrieval

The system uses Astra DB's hybrid search capabilities, combining vector embeddings with lexical search and reranking, resulting in more contextually relevant and accurate responses.
