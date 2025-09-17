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
    page_title="Soccer Analytics AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Modern container styling */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Status indicators */
    .status-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1rem 0;
    }
    
    .status-item {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 500;
        text-align: center;
        min-width: 120px;
    }
    
    .status-online {
        background: #10b981;
        color: white;
    }
    
    .status-offline {
        background: #ef4444;
        color: white;
    }
    
    /* Chat interface styling */
    .chat-container {
        background: #f8fafc;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        min-height: 400px;
        border: 1px solid #e2e8f0;
    }
    
    /* Quick actions */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .action-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e2e8f0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .action-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .action-title {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1e293b;
    }
    
    .action-desc {
        font-size: 0.9rem;
        color: #64748b;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "streaming_response" not in st.session_state:
        st.session_state.streaming_response = ""
    if "is_streaming" not in st.session_state:
        st.session_state.is_streaming = False
    if "stream_status" not in st.session_state:
        st.session_state.stream_status = ""
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
    if "server_status" not in st.session_state:
        st.session_state.server_status = "checking"

def check_server_health():
    """Check server health status"""
    try:
        url = f"{FASTAPI_URL}/health"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            st.session_state.server_status = "online"
            return True
    except:
        pass
    st.session_state.server_status = "offline"
    return False

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
                    continue
        
        # Store final response
        if accumulated_response:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": accumulated_response
            })
            
    except requests.exceptions.RequestException as e:
        status_placeholder.error(f"Connection failed: {str(e)}")
        st.session_state.is_streaming = False
    except Exception as e:
        status_placeholder.error(f"Error: {str(e)}")
        st.session_state.is_streaming = False

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
    """Main Streamlit application with modern interactive UI"""
    initialize_session_state()
    
    # Check server status
    server_online = check_server_health()
    
    # Header section
    st.markdown("""
    <div class="header-container">
        <div class="header-title">⚽ Soccer Analytics AI</div>
        <div class="header-subtitle">Intelligent football data analysis with dynamic visualizations</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Status indicators
    status_class = "status-online" if server_online else "status-offline"
    status_text = "🟢 Server Online" if server_online else "🔴 Server Offline"
    
    st.markdown(f"""
    <div class="status-container">
        <div class="status-item {status_class}">{status_text}</div>
        <div class="status-item status-online">🤖 AI Ready</div>
        <div class="status-item status-online">📊 Visualizations Active</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not server_online:
        st.error("⚠️ Backend server is not responding. Please ensure the FastAPI server is running on port 8000.")
        st.stop()
    
    # Quick action cards
    st.markdown("### Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏆 Player Comparison", use_container_width=True):
            st.session_state.selected_query = "Compare Messi vs Ronaldo stats for 2012-13 season and create spider chart"
    
    with col2:
        if st.button("📈 Team Analysis", use_container_width=True):
            st.session_state.selected_query = "Show Barcelona 2010-11 season performance with charts"
    
    with col3:
        if st.button("🕷️ Spider Charts", use_container_width=True):
            st.session_state.selected_query = "Create spider chart for Messi 2011-12 Barcelona performance"
    
    with col4:
        if st.button("🔄 Reset Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.streaming_response = ""
            st.session_state.is_streaming = False
            st.session_state.last_query = ""
            st.rerun()
    
    # Main chat interface
    st.markdown("### Chat Interface")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
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
    
    # Chat input with modern styling
    user_input = st.chat_input(
        "Ask about player stats, team performance, or request visualizations...", 
        disabled=st.session_state.is_streaming
    )
    
    # Handle quick action selection
    if hasattr(st.session_state, 'selected_query'):
        user_input = st.session_state.selected_query
        del st.session_state.selected_query
    
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
        st.session_state.stream_status = "Connecting to AI..."
        
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            response_placeholder = st.empty()
            
            # Process stream
            process_sse_stream(user_input, status_placeholder, response_placeholder)
        
        st.rerun()
    
    # Show help section in expandable area
    with st.expander("💡 How to Use"):
        st.markdown("""
        **Visualization Keywords:**
        - Use "visualize", "chart", "graph", or "spider chart" to generate visualizations
        - Add "compare" for multi-player/team comparisons
        - Request specific chart types: "pie chart", "bar chart", "spider chart"
        
        **Example Queries:**
        - "Show Messi 2012-13 stats with spider chart"
        - "Compare Ronaldo vs Neymar and visualize"
        - "Barcelona 2011 season performance chart"
        - "Create pie chart for Real Madrid goals distribution"
        
        **Supported Data:**
        - Player statistics (goals, assists, matches, cards)
        - Team performance (points, wins, draws, losses)
        - Multiple seasons and leagues
        - Interactive charts and tables
        """)
    
    # Dynamic Visualization Section
    if st.session_state.messages and st.session_state.last_query:
        last_message = st.session_state.messages[-1]
        
        if last_message["role"] == "assistant":
            query = st.session_state.last_query
            response = last_message["content"]
            
            # Check if visualization was requested and process
            process_visualization_request(query, response)

if __name__ == "__main__":
    main()