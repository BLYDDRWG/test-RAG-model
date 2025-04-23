import os
from typing import List, Dict, Any
from openai import OpenAI

def generate_synthetic_answers(query: str, num_answers: int = 3) -> List[str]:
    """Generate potential synthetic answers to the query"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Generate several possible answers to this question, formatted as a list. These will be used for retrieval."},
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=300,
        n=1
    )
    
    # Extract answers from the response
    synthetic_answer_text = response.choices[0].message.content
    
    # Simple parsing of list items
    answers = []
    for line in synthetic_answer_text.split('\n'):
        # Look for numbered or bulleted items
        if line.strip() and (line.strip()[0].isdigit() or line.strip()[0] in '-*•'):
            answers.append(line.strip().split(' ', 1)[1].strip())
    
    # Ensure we have at least one answer
    if not answers:
        answers = [synthetic_answer_text]
    
    print(f"Generated {len(answers)} synthetic answers")
    return answers[:num_answers]  # Return at most num_answers

def generate_synthetic_queries(query: str, num_queries: int = 3) -> List[str]:
    """Generate related/adjacent queries"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Generate several related questions to the user's query, formatted as a list. These will expand the search scope."},
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=300,
        n=1
    )
    
    # Extract questions from the response
    synthetic_queries_text = response.choices[0].message.content
    
    # Simple parsing of list items
    queries = []
    for line in synthetic_queries_text.split('\n'):
        if line.strip() and (line.strip()[0].isdigit() or line.strip()[0] in '-*•'):
            queries.append(line.strip().split(' ', 1)[1].strip())
    
    # Ensure we have at least one query
    if not queries:
        queries = [query]  # Fallback to original query
    
    print(f"Generated {len(queries)} synthetic queries")
    return queries[:num_queries]  # Return at most num_queries