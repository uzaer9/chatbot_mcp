import streamlit as st
import requests
import json
import time
from typing import Optional, Dict, Any
from urllib.parse import quote
import os

# Import the visualization engine
from visualization import process_visualization_request

# Configure Streamlit page
st.set_page_config(
    page_title="Soccer Analytics Chatbot with Dynamic Visualizations",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
FASTAPI_URL = os.getenv("FASTAPI_URL","http://localhost:8000")

def initialize_session_state():
    """Initialize Streamlit session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "leagues" not in st.session_state:
        st.session_state.leagues = []
    if "streaming_response" not in st.session_state:
        st.session_state.streaming_response = ""
    if "is_streaming" not in st.session_state:
        st.session_state.is_streaming = False
    if "stream_status" not in st.session_state:
        st.session_state.stream_status = ""
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""

def call_api(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
    """Make API calls to FastAPI backend"""
    try:
        url = f"{FASTAPI_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            st.error("🚫 Cannot connect to the backend server. Please make sure FastAPI is running on port 8000.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None
    except json.JSONDecodeError:
        st.error("Invalid response format from server")
        return None

def process_sse_stream(query: str, status_placeholder, response_placeholder):
    """Process SSE stream from FastAPI"""
    try:
        url = f"{FASTAPI_URL}/stream?query={quote(query)}"
        
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()
        
        accumulated_response = ""
        
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                try:
                    data_str = line[6:]
                    data = json.loads(data_str)
                    event_type = data.get('type', '')
                    
                    if event_type == 'status':
                        status_msg = data.get('message', '')
                        st.session_state.stream_status = status_msg
                        status_placeholder.info(status_msg)
                        
                    elif event_type == 'content':
                        chunk = data.get('chunk', '')
                        accumulated_response += chunk
                        st.session_state.streaming_response = accumulated_response
                        response_placeholder.markdown(accumulated_response + "▋")
                        
                    elif event_type == 'complete':
                        complete_msg = data.get('message', 'Analysis complete!')
                        status_placeholder.success(complete_msg)
                        
                    elif event_type == 'done':
                        response_placeholder.markdown(accumulated_response)
                        st.session_state.is_streaming = False
                        break
                        
                    elif event_type == 'error':
                        error_msg = data.get('message', 'An error occurred')
                        status_placeholder.error(error_msg)
                        st.session_state.is_streaming = False
                        break
                        
                except json.JSONDecodeError as e:
                    st.warning(f"Failed to parse SSE data: {line}")
                    continue
        
        # Store final response
        if accumulated_response:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": accumulated_response
            })
            
    except requests.exceptions.RequestException as e:
        status_placeholder.error(f"Stream connection failed: {e}")
        st.session_state.is_streaming = False
    except Exception as e:
        status_placeholder.error(f"Streaming error: {e}")
        st.session_state.is_streaming = False

def load_leagues():
    """Load available leagues from API"""
    if not st.session_state.leagues:
        result = call_api("/leagues")
        if result:
            st.session_state.leagues = result.get("leagues", [])

def display_message(message: Dict[str, str]):
    """Display a chat message"""
    role = message["role"]
    content = message["content"]
    
    if role == "user":
        with st.chat_message("user"):
            st.write(content)
    else:
        with st.chat_message("assistant"):
            st.markdown(content)

def main():
    """Main Streamlit application with dynamic visualizations"""
    initialize_session_state()
    
    # Header
    st.title("⚽ Soccer Analytics Chatbot")
    st.markdown("**AI-Powered Analytics with Dynamic Visualizations!** Use keywords like 'visualize', 'chart', or 'compare' to generate charts.")
    
    # Layout with sidebar
    col1, col2 = st.columns([3, 1])
    
    with col2:
        # Control panel
        st.subheader("🎛️ Controls")
        
        # Health check
        health = call_api("/health")
        if health:
            sse_status = "✅ SSE Enabled" if health.get('sse_enabled') else "❌ SSE Disabled"
            st.success(f"✅ Server Connected")
            st.info(f"🌊 {sse_status}")
        else:
            st.error("❌ Server Offline")
        
        st.markdown("---")
        
        # Load leagues
        load_leagues()
        if st.session_state.leagues:
            st.subheader("Available Leagues:")
            for league in st.session_state.leagues[:6]:
                st.text(f"• {league}")
            if len(st.session_state.leagues) > 6:
                st.text(f"... and {len(st.session_state.leagues) - 6} more")
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Reset Chat"):
            result = call_api("/reset", "POST")
            if result and result.get("status") == "success":
                st.session_state.messages = []
                st.session_state.streaming_response = ""
                st.session_state.is_streaming = False
                st.session_state.last_query = ""
                st.success("Chat reset!")
                st.rerun()
        
        st.markdown("---")
        
        # Visualization help
        st.subheader("📊 Visualization Keywords")
        st.markdown("""
        **To create charts, use:**
        - "visualize"
        - "chart" / "graph"
        - "compare" 
        - "show chart"
        
        **Example queries:**
        - "Get Messi's stats and visualize"
        - "Compare Ronaldo vs Messi goals"
        - "Show Kroos stats with chart"
        """)
        
        st.markdown("---")
        
        # Sample queries
        st.subheader("🎯 Sample Queries")
        sample_queries = [
            "Get Modric stats for 2013-14 and visualize",
            "Compare Messi vs Ronaldo goals and assists",
            "Show Barcelona's 2011-12 season chart",
            "Visualize Kroos performance data"
        ]
        
        for query in sample_queries:
            if st.button(query, key=f"sample_{hash(query)}", 
                        disabled=st.session_state.is_streaming):
                if not st.session_state.is_streaming:
                    st.session_state.user_input = query
                    st.rerun()
    
    with col1:
        # Chat area
        st.subheader("💬 Chat Interface")
        
        # Display messages
        for message in st.session_state.messages:
            display_message(message)
        
        # Show streaming response
        if st.session_state.is_streaming:
            with st.chat_message("assistant"):
                status_placeholder = st.empty()
                response_placeholder = st.empty()
                
                if st.session_state.stream_status:
                    status_placeholder.info(st.session_state.stream_status)
                if st.session_state.streaming_response:
                    response_placeholder.markdown(st.session_state.streaming_response + "▋")
    
    # Chat input (full width)
    user_input = st.chat_input("Ask about soccer data. Use 'visualize' or 'chart' for graphics...", 
                               disabled=st.session_state.is_streaming)
    
    # Handle sample query selection
    if hasattr(st.session_state, 'user_input'):
        user_input = st.session_state.user_input
        del st.session_state.user_input
    
    # Process user input
    if user_input and not st.session_state.is_streaming:
        # Store the query for visualization
        st.session_state.last_query = user_input
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Start streaming
        st.session_state.is_streaming = True
        st.session_state.streaming_response = ""
        st.session_state.stream_status = "🔗 Connecting..."
        
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            response_placeholder = st.empty()
            
            # Process stream
            process_sse_stream(user_input, status_placeholder, response_placeholder)
        
        st.rerun()
    
    # Dynamic Visualization Section (only when visualization keywords are detected)
    if st.session_state.messages and st.session_state.last_query:
        last_message = st.session_state.messages[-1]
        
        if last_message["role"] == "assistant":
            query = st.session_state.last_query
            response = last_message["content"]
            
            # Check if visualization was requested and process
            process_visualization_request(query, response)

if __name__ == "__main__":
    main()