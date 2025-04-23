# Advanced RAG System Documentation

## Overview

This advanced Retrieval-Augmented Generation (RAG) system implements a sophisticated document retrieval and generation pipeline leveraging hybrid search capabilities. The system features multiple retrieval strategies:

1. **Standard (Naive) RAG**: Direct document retrieval based on query relevance
2. **Synthetic Answers RAG**: Generates potential answers first, then retrieves supporting documents
3. **Synthetic Queries RAG**: Expands the original query into multiple related queries for broader retrieval

The system uses Astra DB's hybrid search capabilities, combining vector embeddings with lexical search and reranking, resulting in more contextually relevant and accurate responses.

## Project Structure
advanced_RAG/
├── api/
│   ├── auth.py            # API authentication and key validation
│   └── endpoints.py       # FastAPI endpoint definitions
│
├── core/
│   └── doc_processor.py   # Document processing, chunking, and embedding generation
│
├── database/
│   └── database_mgmt.py   # Astra DB connection and collection management
│
├── llm/
│   ├── query.py           # RAG query implementations and strategies
│   ├── advanced_strategies.py  # Synthetic queries and answers generators
│   └── response.py        # LLM response generation with formatting and source attribution
│
├── user_interface/
│   └── ui.py              # Streamlit UI implementation
│
├── visualization/
│   ├── viz_service.py     # Visualization service endpoints
│   └── enhanced_viz.py    # UMAP visualization implementations
│
├── evaluation/
│   ├── eval_service.py    # Evaluation service for RAG performance
│   └── metrics.py         # Evaluation metrics and scoring functions
│
├── EXRXdata/              # Exercise science training data
│   ├── assessments/       # Assessment protocols and rubrics
│   ├── exercises/         # Exercise descriptions and categories
│   ├── general_movement/  # Movement principles and patterns
│   ├── grounded_truth.txt # Ground truth for evaluation
│   └── rag_eval_queries.txt # Evaluation queries
│
├── data/                  # Data directory
│   ├── input/             # Files for processing
│   ├── output/            # Processed outputs
│   └── upload/            # Temporary upload storage
│
└── docker/                # Docker configuration
    ├── Dockerfile.llm     # LLM service container definition
    ├── Dockerfile.ui      # UI service container definition
    └── Dockerfile.eval    # Evaluation service container definition

## Service Architecture

The system is fully containerized using Docker Compose with the following services:

### 1. UI Service (Port 8501)
- Streamlit-based user interface
- Document upload capabilities
- Query interface with strategy selection
- Visualization options

### 2. LLM Service (Port 8000)
- Handles document queries with different strategies
- Manages communication with OpenAI's embedding and completion APIs
- Implements advanced RAG strategies

### 3. Evaluation Service (Port 8010)
- Provides query evaluation against ground truth
- Calculates similarity scores and detection of novel insights
- Tools for comprehensive RAG performance analysis

### 4. Visualization Service (Port 8020)
- Creates UMAP visualizations of document embeddings
- Compares different RAG strategies visually

## Database Configuration

The system uses Astra DB (DataStax) as the vector database with hybrid search capabilities:

- Vector storage for semantic similarity
- Lexical search for keyword matching
- Reranking for optimized result relevance

## Running the System

```bash
# Start all services
docker-compose up -d

# Access the UI
# Open http://localhost:8501 in your browser

# Stop all services
docker-compose down
```

## Evaluation Tools

The system includes a comprehensive evaluation framework built directly into the Streamlit UI, accessible via the "Evaluation" tab in the sidebar navigation. Key features include:

### Evaluation Capabilities
- **Strategy Comparison**: Compare performance across all three RAG strategies
- **Metric Visualization**: Visual charts for precision, recall, and F1 scores
- **Query-by-Query Analysis**: Detailed breakdown of performance for individual queries
- **Ground Truth Comparison**: Side-by-side comparison with ground truth answers

### Using the Evaluation UI
1. Navigate to http://localhost:8501 and select the "Evaluation" tab
2. Choose evaluation metrics (relevance, factuality, completeness)
3. Select queries to evaluate or use the "Evaluate All" option
4. Review performance metrics and visualizations
5. Export results in CSV format for further analysis

### Available Metrics
- **Retrieval Precision**: How relevant the retrieved documents are
- **Answer Accuracy**: Factual correctness compared to ground truth
- **Retrieval Diversity**: Breadth of information coverage
- **Response Time**: Performance benchmarking across strategies

The evaluation framework helps identify which RAG strategy works best for different query types and knowledge domains within your corpus.

## Environment Variables

The system requires the following environment variables:

OPENAI_API_KEY: OpenAI API key for embeddings and completions
ASTRA_DB_ENDPOINT: Astra DB API endpoint
DB_TOKEN: Astra DB authentication token

## Prerequisites

Before running the system, you need to have the following installed:
- OPENAI_API_KEY=your_key
- ASTRA_DB_ENDPOINT=your_endpoint
- DB_TOKEN=your_token

## Setup

1. Clone the repository
2. Create a `.env` file in the project root with:
3. Run `docker-compose up -d` to start all services

## Document Upload

Documents can be uploaded directly through the Streamlit UI:
1. Navigate to http://localhost:8501
2. Select the "Upload" tab from the sidebar
3. Upload text, PDF, or markdown files
4. The system automatically processes documents into chunks, generates embeddings, and stores them in the database

## API Reference

### Main Endpoints

- `POST /query` - Submit a query to the RAG system
  - Parameters: `query` (text), `strategy` (naive, synthetic_answers, synthetic_queries), `top_k` (number of results)
  
- `POST /upload` - Upload and process a document
  - Parameters: `file` (multipart), `chunk_size` (optional), `chunk_overlap` (optional)
  
- `GET /health` - Check service health

### Environment Configuration

The following optional configurations can be set in your `.env` file:

- `CHUNK_SIZE=500` - Default chunk size for document processing (characters)
- `CHUNK_OVERLAP=50` - Default chunk overlap for document processing (characters)
- `MAX_TOKENS=1000` - Maximum tokens for LLM response generation
- `MODEL_NAME=gpt-4o` - Default LLM model to use for responses

## Database Schema

Documents are stored in Astra DB with the following structure:

- `_id`: UUID for document identification
- `text`: Original text content of the chunk
- `$vector`: Vector embedding representation (1024 dimensions)
- `$lexical`: Text field for lexical search (identical to text)
- `metadata`: Additional document information including:
  - `source`: Source filename
  - `chunk_index`: Position of chunk in original document
  - `timestamp`: When the document was processed
  - `category`: Document type/category (if available)

## Evaluation Metrics

The evaluation framework calculates the following metrics:

- **Retrieval Precision**: Proportion of relevant documents among retrieved documents
- **Retrieval Recall**: Proportion of relevant documents that are successfully retrieved
- **Answer Relevance**: How well the generated answer addresses the query
- **Factual Accuracy**: Correctness of information when compared to ground truth
- **Context Utilization**: How effectively the system uses the retrieved context

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style conventions and includes appropriate tests.

## Roadmap

Future development plans include:

- **Client Profiles**: Save and manage client-specific data to ensure personalized responses
- **Microservice Integration**: Push client programming to training platforms