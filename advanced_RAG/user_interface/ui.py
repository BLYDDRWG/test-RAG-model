import streamlit as st
import sys
import os
import time
import requests
import json
import pandas as pd
from typing import List, Dict, Any
import plotly.express as px

# Set page configuration first - before any other st commands
st.set_page_config(page_title="Bad Wolf", layout="wide")

API_KEY = os.getenv("API_KEY")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import RAG components (adjust paths if needed)
from llm.query import query_documents
from llm.response import generate_response

# Define grayscale color sequence with darker shades for better contrast
grayscale_colors = ["#bdbdbd", "#969696", "#737373", "#525252", "#252525", "#000000"]

# Page configuration
st.title("Database Knowledge Assistant")

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I can answer questions using your database. What would you like to know?"}]

# Sidebar with app mode selection
with st.sidebar:
    st.header("Application Mode")
    app_mode = st.radio(
        "Select Mode",
        options=["Chat", "Document Upload", "Evaluation"],
        index=0,
        help="Chat with database, upload documents, or evaluate RAG system"
    )
    
    # Conditional UI elements based on selected mode
    if app_mode == "Chat":
        st.header("RAG Strategy")
        rag_strategy = st.radio(
            "Select RAG Strategy",
            options=["Standard RAG", "Advanced RAG (Synthetic Answers)", "Advanced RAG (Synthetic Queries)"],
            index=0,
            help="Standard RAG uses the query directly. Synthetic Answers creates potential answers first. Synthetic Queries generates related questions."
        )
        
        # Add visualization toggle
        st.header("Visualization Options")
        enable_viz = st.toggle("Enable Visualizations", value=False, help="Show UMAP visualizations of retrieval results")
        
        if enable_viz:
            viz_comparison = st.checkbox("Compare All Strategies", value=False, 
                                      help="When enabled, shows a comparison of all three retrieval strategies")
        
        # Convert the UI selection to API parameter
        strategy_mapping = {
            "Standard RAG": "naive",
            "Advanced RAG (Synthetic Answers)": "synthetic_answers",
            "Advanced RAG (Synthetic Queries)": "synthetic_queries"
        }
    
    elif app_mode == "Document Upload":
        st.header("Document Upload")
        uploaded_file = st.file_uploader("Add new document to knowledge base", 
                                       type=["pdf", "txt", "md"])
        
        if uploaded_file and st.button("Process Document"):
            with st.spinner("Processing document..."):
                # Save uploaded file to temp location
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                try:
                    # Example in your UI code (using requests library)
                    headers = {"X-API-Key": API_KEY}  # Set the API key in the header
                    files = {'file': open(temp_path, 'rb')}
                    response = requests.post("http://doc-processor-api:8000/process-document", headers=headers, files=files)
                    
                    if response.status_code == 200:
                        st.success(f"Document processed successfully! Added {response.json()['chunks']} chunks to knowledge base.")
                    else:
                        st.error(f"Error processing database: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    # Clean up
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    elif app_mode == "Evaluation":
        st.header("RAG Evaluation")
        eval_mode = st.radio(
            "Evaluation Mode",
            options=["Single Query", "All Queries", "Novel Insights"],
            index=0,
            help="Evaluate a single query, all queries, or review novel insights"
        )

# Main content area
if app_mode == "Chat":
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Ask a question about your database"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                with st.spinner("Searching database..."):
                    # Map selected strategy to API parameter
                    selected_strategy = strategy_mapping[rag_strategy]
                    
                    # Get relevant document chunks with the selected strategy
                    relevant_chunks = query_documents(
                        query=prompt, 
                        n_results=3,
                        strategy=selected_strategy
                    )
                    
                    # Add visualization logic
                    if enable_viz:
                        try:
                            with st.spinner("Generating visualizations..."):
                                # Selected strategy visualization
                                if not viz_comparison:
                                    headers = {"X-API-Key": API_KEY}
                                    viz_request = {
                                        "query": prompt,
                                        "strategy": selected_strategy,
                                        "top_k": 3
                                    }
                                    viz_response = requests.post("http://viz-service:8000/visualize-query", 
                                                               headers=headers, json=viz_request)
                                    
                                    if viz_response.status_code == 200:
                                        viz_data = viz_response.json()
                                        st.image(f"data:image/png;base64,{viz_data['image_base64']}", 
                                               caption=f"Retrieval Visualization for {rag_strategy}")
                                        
                                # Strategy comparison visualization
                                else:
                                    headers = {"X-API-Key": API_KEY}
                                    viz_request = {
                                        "query": prompt,
                                        "strategies": ["naive", "synthetic_answers", "synthetic_queries"],
                                        "top_k": 3
                                    }
                                    viz_response = requests.post("http://viz-service:8000/compare-strategies", 
                                                               headers=headers, json=viz_request)
                                    
                                    if viz_response.status_code == 200:
                                        viz_data = viz_response.json()
                                        st.image(f"data:image/png;base64,{viz_data['image_base64']}", 
                                               caption="RAG Strategy Comparison")
                        except Exception as e:
                            st.warning(f"Visualization could not be generated: {str(e)}")
                    
                    if not relevant_chunks:
                        response_text = "I couldn't find any relevant information in the database."
                        message_placeholder.markdown(response_text)
                        full_response = response_text
                    else:
                        # Generate response from chunks
                        response_data = generate_response(prompt, relevant_chunks)
                        main_response = response_data["text"]
                        
                        # Create a more structured display for the response
                        message_placeholder.empty()  # Clear the placeholder
                        
                        # Create tabs for different parts of the response
                        tab1, tab2 = st.tabs(["Response", "Sources"])
                        
                        with tab1:
                            # Display the response with some styling
                            st.markdown(f"""
                            <div style="max-height: 400px; overflow-y: auto; padding: 10px; border-radius: 5px;">
                            {main_response}
                            </div>
                            <p><em>RAG Strategy: {rag_strategy}</em></p>
                            """, unsafe_allow_html=True)
                        
                        with tab2:
                            if len(response_data["sources"]) > 0:
                                for i, source in enumerate(response_data["sources"]):
                                    with st.expander(f"Source {i+1}: {source.get('title', f'Document {i+1}')}"):
                                        # Add metadata if available
                                        if source.get('category'):
                                            st.markdown(f"*Category:* {source['category']}")
                                        if source.get('source'):
                                            st.markdown(f"*From:* {source['source']}")
                                        if source.get('page'):
                                            st.markdown(f"*Page:* {source['page']}")
                                        
                                        # Add source text preview
                                        if 'text' in source:
                                            st.markdown("**Preview:**")
                                            st.markdown(f"<div style='background-color:#f0f0f0; padding:10px; border-radius:5px; max-height:200px; overflow-y:auto;'>{source['text']}</div>", unsafe_allow_html=True)
                            else:
                                st.info("No source information available.")
                        
                        # Format for chat history
                        full_response = f"{main_response}\n\n*RAG Strategy: {rag_strategy}*"

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                error_message = f"Error: {str(e)}"
                message_placeholder.markdown(error_message)
                full_response = error_message
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

elif app_mode == "Document Upload":
    # Main content area for document upload
    st.header("Document Processing")
    st.write("Use the sidebar to upload and process documents for the knowledge base.")
    
    # Display document stats or previously uploaded files
    st.subheader("Database Statistics")
    # (Add code to display database stats)

elif app_mode == "Evaluation":
    st.header("RAG System Evaluation")
    
    if eval_mode == "Single Query":
        # Load ground truth data
        try:
            with open("EXRXdata/rag_eval_ground_truth.json", "r") as f:
                ground_truth_data = json.load(f)
                
            # Create dropdown of available queries
            query_options = [(item["id"], item["query"]) for item in ground_truth_data["evaluations"]]
            selected_query_id = st.selectbox(
                "Select query to evaluate:",
                options=[q[0] for q in query_options],
                format_func=lambda x: next(q[1] for q in query_options if q[0] == x)
            )
            
            if st.button("Run Evaluation"):
                with st.spinner("Evaluating query against RAG system..."):
                    # Call evaluation service
                    response = requests.post(
                        "http://rag-eval-service:8000/evaluate",
                        headers={"Content-Type": "application/json"},
                        json={"query_id": selected_query_id}
                    )
                    
                    if response.status_code == 200:
                        eval_results = response.json()
                        
                        # Display results in tabs
                        tab1, tab2, tab3 = st.tabs(["RAG Response", "Ground Truth", "Similarity"])
                        
                        with tab1:
                            st.subheader("RAG System Response")
                            st.write(eval_results["rag_response"])
                            
                            if "retrieved_documents" in eval_results:
                                st.subheader("Retrieved Documents")
                                for i, doc in enumerate(eval_results["retrieved_documents"]):
                                    with st.expander(f"Document {i+1}"):
                                        st.text(doc.get("text", "No text available"))
                        
                        with tab2:
                            st.subheader("Expected Answer (Ground Truth)")
                            st.json(eval_results["ground_truth"])
                        
                        with tab3:
                            st.subheader("Similarity Scores")
                            similarity_data = eval_results["similarity_scores"]
                            
                            # Visualize similarity scores
                            df = pd.DataFrame({
                                "Component": list(similarity_data.keys()),
                                "Similarity": list(similarity_data.values())
                            })
                            
                            fig = px.bar(df, x="Component", y="Similarity", 
                                       title="Similarity to Ground Truth",
                                       color="Similarity",
                                       color_continuous_scale=["#737373", "#525252", "#252525"],  # Darker grays
                                       range_color=[0, 1],
                                       template="plotly_white")

                            # Enhanced text contrast
                            fig.update_layout(
                                title_font_color="black",
                                font_color="black", 
                                plot_bgcolor="white",
                                paper_bgcolor="white",
                                xaxis=dict(title_font=dict(color="black", size=14), tickfont=dict(color="black", size=12)),
                                yaxis=dict(title_font=dict(color="black", size=14), tickfont=dict(color="black", size=12)),
                                coloraxis_colorbar=dict(title_font=dict(color="black"), tickfont=dict(color="black"))
                            )

                            st.plotly_chart(fig)
                        
                        # Novel insights capture
                        if eval_results["novel_insight_detected"]:
                            st.subheader("Novel Insights Detected")
                            st.info("The RAG system provided approaches not explicitly mentioned in the ground truth:")
                            
                            for i, sentence in enumerate(eval_results["novel_insight"]["novel_sentences"]):
                                st.markdown(f"**Novel Insight {i+1}**: {sentence}")
                            
                            with st.form("novel_insight_form"):
                                selected_insight = st.selectbox(
                                    "Select most valuable insight:", 
                                    options=eval_results["novel_insight"]["novel_sentences"]
                                )
                                rating = st.slider("Expert Rating (1-5)", 1, 5, 3)
                                submit = st.form_submit_button("Save Rating")
                                
                                if submit:
                                    # Save the expert rating
                                    feedback_response = requests.post(
                                        "http://rag-eval-service:8000/update-novel-insight",
                                        json={
                                            "query_id": selected_query_id,
                                            "novel_insight": selected_insight,
                                            "expert_rating": rating
                                        }
                                    )
                                    
                                    if feedback_response.status_code == 200:
                                        st.success("Expert rating saved successfully!")
                                    else:
                                        st.error(f"Error saving rating: {feedback_response.text}")
                    else:
                        st.error(f"Evaluation failed: {response.text}")
                        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    elif eval_mode == "All Queries":
        if st.button("Evaluate All Queries"):
            with st.spinner("Running evaluation on all queries..."):
                response = requests.get("http://rag-eval-service:8000/evaluate-all")
                
                if response.status_code == 200:
                    all_results = response.json()["results"]
                    
                    # Convert to DataFrame for analysis
                    results_df = pd.DataFrame([
                        {
                            "query_id": r["query_id"],
                            "query": r.get("query", "")[:50] + "...",  # Truncate for display
                            "avg_similarity": sum(r["similarity_scores"].values())/len(r["similarity_scores"]) if "similarity_scores" in r else 0,
                            "has_novel_insight": r.get("novel_insight_detected", False),
                            "category": r["query_id"].split("-")[0] if "query_id" in r else ""
                        }
                        for r in all_results if "error" not in r
                    ])
                    
                    # Display summary metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Average Similarity", f"{results_df['avg_similarity'].mean():.2f}")
                    col2.metric("Queries With Novel Insights", f"{results_df['has_novel_insight'].sum()}")
                    col3.metric("Total Queries Evaluated", len(results_df))
                    
                    # Show charts
                    fig = px.bar(results_df, x="query_id", y="avg_similarity", 
                              color="category",
                              color_discrete_sequence=grayscale_colors,  # Using updated darker colors
                              title="Similarity by Query",
                              template="plotly_white")

                    # Enhanced text contrast
                    fig.update_layout(
                        title_font=dict(size=18, color="black"),
                        font_color="black",
                        legend_title_font_color="black",
                        legend_font_color="black",
                        xaxis=dict(title_font=dict(color="black", size=14), tickfont=dict(color="black", size=12)),
                        yaxis=dict(title_font=dict(color="black", size=14), tickfont=dict(color="black", size=12)),
                        plot_bgcolor="white",  # Add this line to force white plot background
                        paper_bgcolor="white" 
                    )

                    st.plotly_chart(fig)
                    
                    # Category performance
                    category_df = results_df.groupby("category").agg(
                        avg_similarity=("avg_similarity", "mean"),
                        count=("query_id", "count"),
                        novel_insights=("has_novel_insight", "sum")
                    ).reset_index()
                    
                    fig2 = px.bar(category_df, x="category", y="avg_similarity", 
                                color="category", 
                                color_discrete_sequence=grayscale_colors,  # Using updated darker colors
                                title="Performance by Category",
                                text="count",
                                template="plotly_white")

                    # Enhanced text contrast
                    fig2.update_layout(
                        title_font=dict(size=18, color="black"),
                        font_color="black", 
                        legend_title_font_color="black",
                        legend_font_color="black",
                        xaxis=dict(title_font=dict(color="black", size=14), tickfont=dict(color="black", size=12)),
                        yaxis=dict(title_font=dict(color="black", size=14), tickfont=dict(color="black", size=12)),
                        plot_bgcolor="white",  # Add this line to force white plot background
                        paper_bgcolor="white"
                    )

                    st.plotly_chart(fig2)
                    
                    # Detailed results table
                    st.subheader("Detailed Results")
                    st.dataframe(results_df)
                    
                    # Allow downloading results as CSV
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download results as CSV",
                        data=csv,
                        file_name="rag_evaluation_results.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"Failed to retrieve evaluation results: {response.text}")
    
    elif eval_mode == "Novel Insights":
        # Load ground truth with existing novel insights
        try:
            with open("EXRXdata/rag_eval_ground_truth.json", "r") as f:
                ground_truth_data = json.load(f)
                
            # Filter to items with captured novel insights
            insights = [
                item for item in ground_truth_data["evaluations"]
                if item["novel_insights"].get("captured", False)
            ]
            
            if not insights:
                st.info("No novel insights have been captured yet. Run evaluations to discover novel approaches.")
            else:
                st.subheader("Captured Novel Insights")
                
                for insight in insights:
                    with st.expander(f"{insight['id']}: {insight['query'][:50]}..."):
                        st.markdown(f"**Novel Insight:**\n{insight['novel_insights']['value']}")
                        st.markdown(f"**Expert Rating:** {insight['novel_insights']['expert_rating']}/5")
                        st.markdown("---")
                        st.markdown("**Ground Truth:**")
                        st.json(insight["ground_truth"])
                
                # Statistics on novel insights
                st.subheader("Novel Insights Statistics")
                
                ratings_df = pd.DataFrame([
                    {
                        "query_id": item["id"],
                        "category": item["id"].split("-")[0],
                        "rating": item["novel_insights"]["expert_rating"]
                    }
                    for item in insights
                ])
                
                if not ratings_df.empty:
                    fig = px.box(ratings_df, x="category", y="rating", 
                               title="Expert Ratings by Category",
                               color="category",
                               color_discrete_sequence=grayscale_colors,  # Using updated darker colors
                               template="plotly_white")

                    # Enhanced text contrast
                    fig.update_layout(
                        title_font=dict(size=18, color="black"),
                        font_color="black",
                        legend_title_font_color="black", 
                        legend_font_color="black",
                        xaxis=dict(title_font=dict(color="black", size=14), tickfont=dict(color="black", size=12)),
                        yaxis=dict(title_font=dict(color="black", size=14), tickfont=dict(color="black", size=12))
                    )

                    st.plotly_chart(fig)
        
        except Exception as e:
            st.error(f"Error loading novel insights: {str(e)}")
