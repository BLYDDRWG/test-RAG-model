import json
import os
import requests
import time
from flask import Flask, request, jsonify
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class RAGEvaluator:
    def __init__(self, llm_service_url="http://llm-service:8000"):
        self.llm_service_url = llm_service_url
        self.ground_truth_path = "/app/EXRXdata/rag_eval_ground_truth.json"
        self.load_ground_truth()
        
    def load_ground_truth(self):
        logger.info(f"Loading ground truth from {self.ground_truth_path}")
        with open(self.ground_truth_path, 'r') as f:
            self.ground_truth_data = json.load(f)
    
    def evaluate_query(self, query_id=None, query_text=None):
        # Find the query in ground truth
        if query_id:
            query_data = next((item for item in self.ground_truth_data["evaluations"] 
                              if item["id"] == query_id), None)
        elif query_text:
            query_data = next((item for item in self.ground_truth_data["evaluations"] 
                              if item["query"] == query_text), None)
        else:
            return {"error": "Must provide either query_id or query_text"}
            
        if not query_data:
            return {"error": f"Query not found in ground truth"}
            
        # Send query to RAG system
        logger.info(f"Sending query to LLM service: {query_data['query'][:50]}...")
        response = requests.post(
            f"{self.llm_service_url}/query",
            json={"query": query_data["query"]},
            timeout=60
        )
        
        rag_response = response.json()
        
        # Extract answer text from RAG response
        answer_text = rag_response.get("response", "")
        
        # Simplified comparison - text overlap instead of embeddings
        similarity_scores = self.simple_compare_response(answer_text, query_data["ground_truth"])
        
        # Simple novel insight detection
        novel_insight = self.simple_detect_novel_insight(answer_text, query_data["ground_truth"])
        
        result = {
            "query_id": query_data["id"],
            "query": query_data["query"],
            "ground_truth": query_data["ground_truth"],
            "rag_response": answer_text,
            "similarity_scores": similarity_scores,
            "novel_insight_detected": novel_insight is not None,
            "novel_insight": novel_insight
        }
        
        # Add retrieved documents if available in response
        if "documents" in rag_response:
            result["retrieved_documents"] = rag_response["documents"]
            
        return result
    
    def simple_compare_response(self, rag_response: str, ground_truth: dict) -> dict:
        """Simple text-based comparison without embeddings"""
        scores = {}
        
        for key, expected_value in ground_truth.items():
            if isinstance(expected_value, str):
                # Use simple text overlap for similarity
                expected_words = set(expected_value.lower().split())
                response_words = set(rag_response.lower().split())
                
                if len(expected_words) > 0:
                    # Jaccard similarity: intersection over union
                    intersection = len(expected_words.intersection(response_words))
                    union = len(expected_words.union(response_words))
                    similarity = intersection / union if union > 0 else 0
                    scores[key] = similarity
                else:
                    scores[key] = 0.0
            
            elif isinstance(expected_value, dict):
                scores[key] = {}
                for sub_key, sub_value in expected_value.items():
                    if isinstance(sub_value, str):
                        expected_words = set(sub_value.lower().split())
                        response_words = set(rag_response.lower().split())
                        
                        if len(expected_words) > 0:
                            intersection = len(expected_words.intersection(response_words))
                            union = len(expected_words.union(response_words))
                            similarity = intersection / union if union > 0 else 0
                            scores[key][sub_key] = similarity
                        else:
                            scores[key][sub_key] = 0.0
        
        return scores
    
    def simple_detect_novel_insight(self, rag_response: str, ground_truth: dict) -> dict:
        """Simple novel insight detection without embeddings"""
        # Extract key intervention terms from ground truth
        ground_truth_terms = set()
        for key, value in ground_truth.items():
            if isinstance(value, str):
                terms = re.findall(r'\b[A-Za-z]{3,}\b', value)
                ground_truth_terms.update([t.lower() for t in terms])
            elif isinstance(value, dict):
                for sub_value in value.values():
                    if isinstance(sub_value, str):
                        terms = re.findall(r'\b[A-Za-z]{3,}\b', sub_value)
                        ground_truth_terms.update([t.lower() for t in terms])
        
        # Find sentences in RAG response that might contain novel approaches
        sentences = re.split(r'(?<=[.!?])\s+', rag_response)
        
        novel_sentences = []
        for sentence in sentences:
            sentence_terms = set([t.lower() for t in re.findall(r'\b[A-Za-z]{3,}\b', sentence)])
            
            novel_terms = sentence_terms - ground_truth_terms
            
            intervention_indicators = ['exercise', 'protocol', 'program', 'technique', 'approach', 'method']
            
            if (len(novel_terms) >= 3 and 
                any(indicator in sentence.lower() for indicator in intervention_indicators)):
                novel_sentences.append(sentence)
        
        if novel_sentences:
            return {
                "novel_sentences": novel_sentences,
                "explanation": "These sentences contain approaches not explicitly mentioned in the ground truth."
            }
        
        return None
    
    def evaluate_all_queries(self):
        """Evaluate all queries in the ground truth file"""
        results = []
        for evaluation in self.ground_truth_data["evaluations"]:
            query_id = evaluation["id"]
            logger.info(f"Evaluating query {query_id}...")
            
            try:
                result = self.evaluate_query(query_id=query_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Error evaluating query {query_id}: {str(e)}")
                results.append({
                    "query_id": query_id,
                    "error": str(e)
                })
        
        return results
        
    def update_novel_insights(self, query_id: str, novel_insight: str, expert_rating: int):
        """Update the ground truth with expert-validated novel insights"""
        query_data = next((item for item in self.ground_truth_data["evaluations"] 
                          if item["id"] == query_id), None)
        
        if not query_data:
            return {"error": f"Query ID {query_id} not found"}
            
        # Update novel insights in memory
        query_data["novel_insights"] = {
            "captured": True,
            "value": novel_insight,
            "expert_rating": expert_rating
        }
        
        # Save updated ground truth to file
        with open(self.ground_truth_path, 'w') as f:
            json.dump(self.ground_truth_data, f, indent=2)
            
        return {"status": "success", "message": "Novel insight saved"}


# Initialize evaluator
evaluator = RAGEvaluator()

# API routes
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/evaluate', methods=['POST'])
def evaluate_query():
    data = request.json
    query_id = data.get('query_id')
    query_text = data.get('query_text')
    
    result = evaluator.evaluate_query(query_id=query_id, query_text=query_text)
    return jsonify(result)

@app.route('/evaluate-all', methods=['GET'])
def evaluate_all():
    results = evaluator.evaluate_all_queries()
    return jsonify({"results": results})

@app.route('/update-novel-insight', methods=['POST'])
def update_novel_insight():
    data = request.json
    query_id = data.get('query_id')
    novel_insight = data.get('novel_insight')
    expert_rating = data.get('expert_rating')
    
    if not query_id or not novel_insight or expert_rating is None:
        return jsonify({"error": "Missing required parameters"}), 400
        
    result = evaluator.update_novel_insights(query_id, novel_insight, expert_rating)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)