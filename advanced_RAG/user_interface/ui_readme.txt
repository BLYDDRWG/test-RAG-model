# User Interface (UI) Module Documentation

## Overview

The `user_interface` module provides a Streamlit-based web interface for interacting with the Advanced RAG system. It allows users to upload documents, submit queries, visualize results, and evaluate system performance. The UI is designed to be user-friendly and supports real-time interaction with the backend services.

## Key Features

- **Document Upload**: Upload and process documents in various formats (PDF, TXT, Markdown).
- **Query Submission**: Submit queries and select retrieval strategies (naive, synthetic answers, synthetic queries).
- **Visualization**: View document embeddings and relationships using UMAP visualizations.
- **Evaluation Tools**: Compare RAG strategies and review performance metrics.

## File Structure

user_interface/ 
├── init.py # Module initializer 
├── ui.py # Main Streamlit UI implementation 
└── ui_readme.txt # Documentation for the UI module

## Functions in `ui.py`

### 1. `upload_documents()`
Handles document uploads and processes them into chunks for storage.

- **Input**: Uploaded file(s) via the Streamlit file uploader.
- **Output**: Confirmation message and processed document details.

### 2. `submit_query()`
Allows users to submit queries and select a retrieval strategy.

- **Input**:
  - `query`: User-entered query text.
  - `strategy`: Selected retrieval strategy (`naive`, `synthetic_answers`, `synthetic_queries`).
- **Output**: Retrieved documents and generated response.

### 3. `visualize_embeddings()`
Displays UMAP visualizations of document embeddings.

- **Input**: Processed document embeddings.
- **Output**: Interactive visualization in the Streamlit UI.

### 4. `evaluate_performance()`
Provides tools for evaluating RAG strategies and reviewing performance metrics.

- **Input**: Selected queries and evaluation metrics.
- **Output**: Precision, recall, and F1 score visualizations.

## Environment Variables

The following environment variables must be set for the UI module to function:

- `LLM_SERVICE_URL`: URL of the LLM service (default: `http://llm-service:8000`)
- `EVALUATION_SERVICE_URL`: URL of the evaluation service (default: `http://evaluation-service:8010`)

These should be configured in a `.env` file in the root directory:
```plaintext
LLM_SERVICE_URL=http://llm-service:8000
EVALUATION_SERVICE_URL=http://evaluation-service:8010

## Uploading Documents

- Navigate to the "Upload" tab in the sidebar.
- Drag and drop your document(s) or use the file uploader.
- The system will process the documents and store them in the database.

## Submitting a Query

- Navigate to the "Query" tab in the sidebar.
- Enter your query in the text box.
- Select a retrieval strategy (naive, synthetic answers, or synthetic queries).
- Click "Submit" to view the results and generated response.

## Visualizing Embeddings

- Navigate to the "Visualization" tab in the sidebar.
- Select a dataset or query to visualize.
- View the UMAP visualization of document embeddings.

## Evaluating Performance

- Navigate to the "Evaluation" tab in the sidebar.
- Select queries to evaluate or use the "Evaluate All" option.
- Review precision, recall, and F1 score visualizations.

## Notes

- Ensure the LLM_SERVICE_URL and EVALUATION_SERVICE_URL environment variables are correctly set before running the UI.
- The UI is optimized for real-time interaction and supports multiple concurrent users.
- For best performance, run the UI on a machine with sufficient resources to handle document processing and visualization.


