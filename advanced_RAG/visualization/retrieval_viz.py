import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict, Any, Optional, Tuple
import umap
from sklearn.metrics.pairwise import cosine_similarity
import os
import json
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from visualization.embedding import get_embedding

class RetrievalVisualizer:
    def __init__(self):
        """Initialize the retrieval visualization tool"""
        self.embeddings_cache = {}
        
    def get_embedding(self, text):
        """Get embedding for a text, using cache if available"""
        if text not in self.embeddings_cache:
            self.embeddings_cache[text] = get_embedding(text)
        return self.embeddings_cache[text]
    
    def visualize_query_results(self, 
                               query: str, 
                               retrieved_docs: List[Dict[str, Any]],
                               n_neighbors: int = 15, 
                               min_dist: float = 0.1) -> Tuple[str, np.ndarray]:
        """
        Visualize query results using UMAP projection

        Args:
            query: The query text
            retrieved_docs: List of retrieved document chunks with text and metadata
            n_neighbors: UMAP parameter for local neighborhood size
            min_dist: UMAP parameter for minimum distance

        Returns:
            base64 encoded png image, reduced embeddings
        """
        # Extract texts from docs
        texts = [query] + [doc["text"] for doc in retrieved_docs]
        labels = ["Query"] + [f"Doc {i+1}" for i in range(len(retrieved_docs))]
        
        # Get embeddings
        embeddings = [self.get_embedding(text) for text in texts]
        embeddings_array = np.array(embeddings)
        
        # Apply UMAP for dimensionality reduction
        reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, random_state=42)
        embedding_2d = reducer.fit_transform(embeddings_array)
        
        # Calculate distances from query to each document
        query_embedding = embeddings[0]
        similarities = [
            cosine_similarity([query_embedding], [doc_embedding])[0][0] 
            for doc_embedding in embeddings[1:]
        ]
        
        # Create plot
        plt.figure(figsize=(10, 8))
        
        # Plot documents with similarity-based color gradient
        sc = plt.scatter(
            embedding_2d[1:, 0],
            embedding_2d[1:, 1],
            c=similarities,
            cmap='viridis',
            s=100,
            alpha=0.7
        )
        cbar = plt.colorbar(sc)
        cbar.set_label('Similarity to Query')
        
        # Plot query point
        plt.scatter(
            embedding_2d[0, 0],
            embedding_2d[0, 1],
            c='red',
            marker='*',
            s=300,
            label="Query"
        )
        
        # Add labels
        for i, (x, y, label) in enumerate(zip(embedding_2d[:, 0], embedding_2d[:, 1], labels)):
            plt.annotate(
                label,
                (x, y),
                fontsize=9,
                alpha=0.8,
                xytext=(5, 5),
                textcoords='offset points'
            )
        
        # Add connections between query and docs
        query_x, query_y = embedding_2d[0]
        for i in range(1, len(embedding_2d)):
            doc_x, doc_y = embedding_2d[i]
            plt.plot([query_x, doc_x], [query_y, doc_y], 'k-', alpha=0.2)
        
        plt.title(f"Query Retrieval Visualization")
        plt.tight_layout()
        
        # Convert plot to base64 encoded image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        
        return img_str, embedding_2d
    
    def compare_strategies(self,
                          query: str,
                          results_by_strategy: Dict[str, List[Dict[str, Any]]],
                          n_neighbors: int = 15,
                          min_dist: float = 0.1) -> str:
        """
        Create a comparison visualization between different RAG strategies
        
        Args:
            query: The query text
            results_by_strategy: Dictionary mapping strategy names to their retrieved docs
            
        Returns:
            base64 encoded png image
        """
        strategies = list(results_by_strategy.keys())
        
        # Create subplots - one for each strategy plus combined view
        n_plots = len(strategies) + 1
        fig, axes = plt.subplots(1, n_plots, figsize=(5*n_plots, 6))
        
        # Get all unique documents across strategies
        all_docs = []
        for strategy, docs in results_by_strategy.items():
            for doc in docs:
                doc_text = doc["text"]
                if not any(d["text"] == doc_text for d in all_docs):
                    all_docs.append(doc)
        
        # Get all embeddings
        all_texts = [query] + [doc["text"] for doc in all_docs]
        embeddings = [self.get_embedding(text) for text in all_texts]
        embeddings_array = np.array(embeddings)
        
        # Apply UMAP for dimensionality reduction
        reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, random_state=42)
        embedding_2d = reducer.fit_transform(embeddings_array)
        
        # Query point coordinates
        query_x, query_y = embedding_2d[0]
        
        # For tracking document indices across strategies
        doc_indices = {}
        for i, doc in enumerate(all_docs):
            doc_indices[doc["text"]] = i + 1  # +1 because query is at index 0
            
        # Plot each strategy separately
        for i, strategy in enumerate(strategies):
            ax = axes[i]
            strategy_docs = results_by_strategy[strategy]
            
            # Plot query point
            ax.scatter(query_x, query_y, c='red', marker='*', s=200, label="Query")
            
            # Plot all documents (gray)
            ax.scatter(
                embedding_2d[1:, 0],
                embedding_2d[1:, 1],
                c='lightgray',
                s=50,
                alpha=0.3
            )
            
            # Highlight retrieved documents for this strategy
            for doc in strategy_docs:
                idx = doc_indices[doc["text"]]
                ax.scatter(
                    embedding_2d[idx, 0],
                    embedding_2d[idx, 1],
                    c='blue',
                    s=100,
                    alpha=0.7
                )
                
                # Connect to query
                ax.plot(
                    [query_x, embedding_2d[idx, 0]],
                    [query_y, embedding_2d[idx, 1]],
                    'b-',
                    alpha=0.4
                )
            
            ax.set_title(f"{strategy}")
            ax.set_xticks([])
            ax.set_yticks([])
            
        # Combined view in last plot
        ax = axes[-1]
        
        # Plot query
        ax.scatter(query_x, query_y, c='red', marker='*', s=200, label="Query")
        
        # Plot documents with color by strategy
        colors = ['blue', 'green', 'purple', 'orange', 'cyan']
        for i, strategy in enumerate(strategies):
            strategy_docs = results_by_strategy[strategy]
            color = colors[i % len(colors)]
            
            for doc in strategy_docs:
                idx = doc_indices[doc["text"]]
                ax.scatter(
                    embedding_2d[idx, 0],
                    embedding_2d[idx, 1],
                    c=color,
                    s=80,
                    alpha=0.7,
                    label=f"{strategy}" if doc == strategy_docs[0] else ""
                )
                
                # Connect to query
                ax.plot(
                    [query_x, embedding_2d[idx, 0]],
                    [query_y, embedding_2d[idx, 1]],
                    color=color,
                    alpha=0.3
                )
        
        ax.set_title("Combined Comparison")
        ax.legend(loc='upper right')
        ax.set_xticks([])
        ax.set_yticks([])
        
        plt.tight_layout()
        
        # Convert plot to base64 encoded image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        
        return img_str