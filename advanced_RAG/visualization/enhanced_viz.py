import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict, Any, Optional, Tuple
import umap
from sklearn.metrics.pairwise import cosine_similarity
import os

class EnhancedRetrievalVisualization:
    def __init__(self):
        """Initialize the enhanced retrieval visualization tool"""
        self.embeddings_cache = {}
        self.dataset_embeddings = None
        self.dataset_umap = None
    
    def get_embedding(self, text):
        """Get embedding for a text, using cache if available"""
        from visualization.embedding import get_embedding
        
        if text not in self.embeddings_cache:
            self.embeddings_cache[text] = get_embedding(text)
        return self.embeddings_cache[text]
    
    def _project_embeddings(self, embeddings, umap_transform):
        """Project embeddings using an existing UMAP transform"""
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        return umap_transform.transform(embeddings)
    
    def initialize_dataset(self, sample_texts=None, collection_name="test_data", sample_size=300):
        """Initialize dataset embeddings for background visualization
        
        Args:
            sample_texts: List of texts to use as dataset (if None, retrieve from database)
            collection_name: Database collection for sampling if sample_texts not provided
            sample_size: Number of documents to sample if retrieving from database
        """
        import requests
        headers = {"X-API-Key": os.getenv("API_KEY")}
        
        # Get random sample of documents from database if sample_texts not provided
        if not sample_texts:
            try:
                # Make a request to get random samples from database 
                response = requests.post(
                    "http://doc-processor-api:8000/sample-documents",
                    json={"collection_name": collection_name, "sample_size": sample_size},
                    headers=headers
                )
                
                if response.status_code == 200:
                    samples = response.json().get("documents", [])
                    sample_texts = [doc.get("text", "") for doc in samples]
                else:
                    print(f"Error getting sample documents: {response.text}")
                    sample_texts = []
            except Exception as e:
                print(f"Error sampling documents: {str(e)}")
                sample_texts = []
        
        # Generate embeddings for all texts
        all_embeddings = [self.get_embedding(text) for text in sample_texts if text.strip()]
        
        if all_embeddings:
            self.dataset_embeddings = np.array(all_embeddings)
            # Create UMAP transform with better parameters
            self.dataset_umap = umap.UMAP(
                n_neighbors=15,
                min_dist=0.1,
                n_components=2,
                random_state=42,
                transform_seed=42
            ).fit(self.dataset_embeddings)
            return True
        return False

    def visualize_query_results(self, 
                                query: str, 
                                retrieved_docs: List[Dict[str, Any]],
                                synthetic_queries: List[str] = None) -> str:
        """
        Create an enhanced visualization of query results
        
        Args:
            query: Original query text
            retrieved_docs: Retrieved documents
            synthetic_queries: Optional list of synthetic/augmented queries
            
        Returns:
            base64 encoded image
        """
        # Initialize dataset if needed
        if self.dataset_embeddings is None:
            success = self.initialize_dataset()
            if not success:
                print("Warning: Could not initialize dataset embeddings")
                # Create smaller sample for demo
                dummy_texts = [f"Sample document {i}" for i in range(50)]
                dummy_embeddings = [self.get_embedding(text) for text in dummy_texts]
                self.dataset_embeddings = np.array(dummy_embeddings)
                self.dataset_umap = umap.UMAP(random_state=42, transform_seed=42).fit(self.dataset_embeddings)
        
        # Get embeddings
        original_query_embedding = np.array(self.get_embedding(query))
        
        # Get synthetic query embeddings if provided
        augmented_query_embeddings = []
        if synthetic_queries:
            augmented_query_embeddings = [self.get_embedding(q) for q in synthetic_queries]
            augmented_query_embeddings = np.array(augmented_query_embeddings)
        
        # Get retrieved document embeddings
        retrieved_embeddings = [self.get_embedding(doc["text"]) for doc in retrieved_docs]
        retrieved_embeddings = np.array(retrieved_embeddings) if retrieved_embeddings else np.array([])
        
        # Project all embeddings using dataset UMAP
        projected_dataset = self._project_embeddings(self.dataset_embeddings, self.dataset_umap)
        projected_query = self._project_embeddings(original_query_embedding, self.dataset_umap)
        
        projected_augmented = None
        if len(augmented_query_embeddings) > 0:
            projected_augmented = self._project_embeddings(augmented_query_embeddings, self.dataset_umap)
        
        projected_retrieved = None
        if len(retrieved_embeddings) > 0:
            projected_retrieved = self._project_embeddings(retrieved_embeddings, self.dataset_umap)
        
        # Create plot
        plt.figure(figsize=(12, 10))
        
        # Plot dataset embeddings as background
        plt.scatter(
            projected_dataset[:, 0],
            projected_dataset[:, 1],
            s=10,
            color="lightgray",
            alpha=0.5
        )
        
        # Plot original query
        plt.scatter(
            projected_query[:, 0],
            projected_query[:, 1],
            s=150,
            marker="X",
            color="red",
            label="Original Query"
        )
        
        # Plot synthetic queries if available
        if projected_augmented is not None and len(projected_augmented) > 0:
            plt.scatter(
                projected_augmented[:, 0],
                projected_augmented[:, 1],
                s=150,
                marker="X",
                color="orange",
                label="Synthetic Queries"
            )
        
        # Plot retrieved documents
        if projected_retrieved is not None and len(projected_retrieved) > 0:
            plt.scatter(
                projected_retrieved[:, 0],
                projected_retrieved[:, 1],
                s=100,
                facecolors="none",
                edgecolors="green",
                linewidth=2,
                label="Retrieved Documents"
            )
            
            # Draw connecting lines from query to retrieved docs
            for i in range(len(projected_retrieved)):
                plt.plot(
                    [projected_query[0, 0], projected_retrieved[i, 0]],
                    [projected_query[0, 1], projected_retrieved[i, 1]],
                    'k-', 
                    alpha=0.2
                )
        
        # Set plot style
        plt.gca().set_aspect('equal', 'datalim')
        plt.title(f"Query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        plt.axis('off')
        plt.legend(loc='upper right')
        
        # Convert plot to base64 encoded image
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        
        return img_str
        
    def compare_strategies(self,
                          query: str,
                          results_by_strategy: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Create a comparison visualization between different RAG strategies
        
        Args:
            query: The query text
            results_by_strategy: Dictionary mapping strategy names to their retrieved docs
            
        Returns:
            base64 encoded png image
        """
        # Initialize dataset if needed
        if self.dataset_embeddings is None:
            success = self.initialize_dataset()
            if not success:
                print("Warning: Could not initialize dataset embeddings")
                # Create smaller sample for demo
                dummy_texts = [f"Sample document {i}" for i in range(50)]
                dummy_embeddings = [self.get_embedding(text) for text in dummy_texts]
                self.dataset_embeddings = np.array(dummy_embeddings)
                self.dataset_umap = umap.UMAP(random_state=42, transform_seed=42).fit(self.dataset_embeddings)
        
        strategies = list(results_by_strategy.keys())
        
        # Get query embedding
        query_embedding = np.array(self.get_embedding(query))
        
        # Get embeddings for all retrieved documents
        all_doc_embeddings = {}
        for strategy, docs in results_by_strategy.items():
            all_doc_embeddings[strategy] = np.array([self.get_embedding(doc["text"]) for doc in docs])
        
        # Project all embeddings
        projected_dataset = self._project_embeddings(self.dataset_embeddings, self.dataset_umap)
        projected_query = self._project_embeddings(query_embedding, self.dataset_umap)
        projected_docs = {}
        for strategy, embeddings in all_doc_embeddings.items():
            if len(embeddings) > 0:
                projected_docs[strategy] = self._project_embeddings(embeddings, self.dataset_umap)
        
        # Create figure with subplots
        n_strategies = len(strategies)
        fig, axes = plt.subplots(1, n_strategies + 1, figsize=(5*(n_strategies+1), 6), constrained_layout=True)
        
        # Create a color map for strategies
        colors = ['blue', 'green', 'purple', 'orange', 'cyan']
        strategy_colors = {strategy: colors[i % len(colors)] for i, strategy in enumerate(strategies)}
        
        # Plot each strategy in its own subplot
        for i, strategy in enumerate(strategies):
            ax = axes[i]
            
            # Background dataset points
            ax.scatter(
                projected_dataset[:, 0],
                projected_dataset[:, 1],
                s=10,
                color="lightgray",
                alpha=0.3
            )
            
            # Query point
            ax.scatter(
                projected_query[:, 0],
                projected_query[:, 1],
                s=150,
                marker="X",
                color="red",
                label="Query"
            )
            
            # Retrieved documents for this strategy
            if strategy in projected_docs and len(projected_docs[strategy]) > 0:
                ax.scatter(
                    projected_docs[strategy][:, 0],
                    projected_docs[strategy][:, 1],
                    s=100,
                    facecolors="none",
                    edgecolors=strategy_colors[strategy],
                    linewidth=2,
                    label=f"Retrieved ({strategy})"
                )
                
                # Draw connecting lines from query to docs
                for j in range(len(projected_docs[strategy])):
                    ax.plot(
                        [projected_query[0, 0], projected_docs[strategy][j, 0]],
                        [projected_query[0, 1], projected_docs[strategy][j, 1]],
                        '-',
                        color=strategy_colors[strategy],
                        alpha=0.2
                    )
            
            ax.set_title(f"{strategy}")
            ax.legend(loc='upper right')
            ax.set_aspect('equal', 'datalim')
            ax.axis('off')
        
        # Combined view in the last subplot
        ax = axes[-1]
        
        # Background dataset points
        ax.scatter(
            projected_dataset[:, 0],
            projected_dataset[:, 1],
            s=10,
            color="lightgray",
            alpha=0.3
        )
        
        # Query point
        ax.scatter(
            projected_query[:, 0],
            projected_query[:, 1],
            s=150,
            marker="X",
            color="red", 
            label="Query"
        )
        
        # Plot documents for each strategy
        for strategy in strategies:
            if strategy in projected_docs and len(projected_docs[strategy]) > 0:
                ax.scatter(
                    projected_docs[strategy][:, 0],
                    projected_docs[strategy][:, 1],
                    s=100,
                    facecolors="none",
                    edgecolors=strategy_colors[strategy],
                    linewidth=2,
                    label=f"{strategy}"
                )
        
        ax.set_title("Combined View")
        ax.legend(loc='upper right')
        ax.set_aspect('equal', 'datalim')
        ax.axis('off')
        
        # Convert plot to base64 encoded image
        buf = io.BytesIO()
        fig.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        
        return img_str