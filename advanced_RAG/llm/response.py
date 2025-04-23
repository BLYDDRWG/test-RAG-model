import os
from openai import OpenAI
from typing import List, Dict, Any

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(query: str, documents: List[Dict], model: str = "gpt-4o") -> dict:
    """Generate a response using retrieved documents with improved formatting"""
    
    if not documents:
        return {
            "text": "I couldn't find relevant information to answer your question.",
            "sources": []
        }
    
    # Extract document texts
    doc_texts = [doc.get("text", "") for doc in documents if doc.get("text")]
    
    # Prepare source information for attribution
    sources = []
    for i, doc in enumerate(documents):
        metadata = doc.get("metadata", {})
        source_info = {
            "id": i,
            "text": doc.get("text", "")[:100] + "...", # Preview of content
            "title": metadata.get("title", f"Source {i+1}"),
            "source": metadata.get("source", "Unknown source"),
            "page": metadata.get("page", None),
            "category": metadata.get("category", "Uncategorized")
        }
        sources.append(source_info)
    
    # Create a prompt that encourages good formatting
    system_prompt = """You are a knowledgeable fitness and health assistant that provides well-formatted, readable responses.
Follow these formatting rules:
- Use proper Markdown formatting
- Create clear bullet points or numbered lists where appropriate
- Use headings for different sections (##, ###)
- Add line breaks between paragraphs
- Never use references like "{from Document X}" in your answer
- Present information in a clear, organized manner
- If listing exercises, format them consistently with proper spacing
- You can still mention source categories in natural language (e.g., "according to exercise science guidelines")"""
    
    # Create content for each document
    doc_content = "\n\n".join([f"Document {i+1}: {text}" for i, text in enumerate(doc_texts)])

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
                {"role": "system", "content": f"Here are some relevant documents to help answer the query:\n\n{doc_content}"}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        result = {
            "text": response.choices[0].message.content.strip(),
            "sources": sources  # Include detailed source information
        }
        return result
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return {
            "text": "I'm sorry, I encountered an error while generating a response.",
            "sources": []
        }