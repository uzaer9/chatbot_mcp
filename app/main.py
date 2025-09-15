from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
import asyncio
import json
import time

from app.config import config
from app.mcp_client import SoccerMCPClient
from app.logger import get_logger

logger = get_logger("fastapi_app")

# Initialize FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    description="Soccer Analytics Chatbot API with SSE Streaming",
    version="1.0.0",
    debug=config.DEBUG_MODE
)

# Add CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global MCP client instance
mcp_client = SoccerMCPClient()

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    error: Optional[str] = None

class LeaguesResponse(BaseModel):
    leagues: List[str]

# SSE Event types
class SSEEvent:
    def __init__(self, event_type: str, data: dict):
        self.event_type = event_type
        self.data = data
    
    def format(self) -> str:
        """Format as SSE event"""
        return f"data: {json.dumps({'type': self.event_type, **self.data})}\n\n"

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info(f"Starting {config.APP_NAME} with SSE support")
    logger.info("FastAPI server is ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await mcp_client.cleanup()
    logger.info("FastAPI server shut down")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": config.APP_NAME,
        "debug_mode": config.DEBUG_MODE,
        "sse_enabled": True
    }

# Legacy non-streaming endpoint (for compatibility)
@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a soccer analytics query (non-streaming)"""
    try:
        logger.info(f"Received non-streaming query: {request.query}")
        
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Process the query
        response = await mcp_client.process_query(request.query)
        
        logger.info("Query processed successfully")
        return QueryResponse(response=response)
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        return QueryResponse(
            response="I'm sorry, I encountered an error processing your request.",
            error=str(e)
        )

# NEW: SSE Streaming endpoint
@app.get("/stream")
async def stream_query(query: str = Query(..., description="Soccer analytics query")):
    """Stream soccer analytics query processing with SSE"""
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate SSE stream for query processing"""
        try:
            logger.info(f"Starting SSE stream for query: {query}")
            
            if not query.strip():
                yield SSEEvent("error", {"message": "Query cannot be empty"}).format()
                return
            
            # Step 1: Connection status
            yield SSEEvent("status", {
                "status": "connecting",
                "message": "🔗 Connecting to soccer data server..."
            }).format()
            
            # Add small delay for visual effect
            await asyncio.sleep(0.1)
            
            # Process query with streaming updates
            async for update in mcp_client.process_query_stream(query):
                yield update
                # Small delay between chunks for better UX
                await asyncio.sleep(0.05)
            
            # Final completion event
            yield SSEEvent("complete", {
                "status": "complete", 
                "message": "✅ Analysis complete!"
            }).format()
            
            # Signal stream end
            yield SSEEvent("done", {}).format()
            
        except Exception as e:
            logger.error(f"SSE stream error: {e}")
            yield SSEEvent("error", {
                "message": f"Stream error: {str(e)}"
            }).format()
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Get available leagues
@app.get("/leagues", response_model=LeaguesResponse)
async def get_leagues():
    """Get available soccer leagues"""
    try:
        leagues = await mcp_client.get_available_leagues()
        return LeaguesResponse(leagues=leagues)
    except Exception as e:
        logger.error(f"Failed to get leagues: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve leagues")

# Reset conversation
@app.post("/reset")
async def reset_conversation():
    """Reset the conversation history"""
    try:
        mcp_client.messages = []
        logger.info("Conversation reset")
        return {"status": "success", "message": "Conversation reset"}
    except Exception as e:
        logger.error(f"Failed to reset conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset conversation")

# Get conversation history
@app.get("/history")
async def get_conversation_history():
    """Get current conversation history"""
    return {"messages": mcp_client.messages}

# NEW: Test SSE endpoint
@app.get("/test-stream")
async def test_stream():
    """Test SSE streaming functionality"""
    
    async def test_generate():
        """Generate test SSE events"""
        events = [
            ("status", {"message": "🧪 Testing SSE connection..."}),
            ("content", {"chunk": "This "}),
            ("content", {"chunk": "is "}),
            ("content", {"chunk": "a "}),
            ("content", {"chunk": "streaming "}),
            ("content", {"chunk": "test! "}),
            ("content", {"chunk": "⚽"}),
            ("complete", {"message": "✅ Test complete!"}),
            ("done", {})
        ]
        
        for event_type, data in events:
            yield SSEEvent(event_type, data).format()
            await asyncio.sleep(0.3)  # Simulate processing time
    
    return StreamingResponse(
        test_generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting SSE-enabled server on {config.FASTAPI_HOST}:{config.FASTAPI_PORT}")
    uvicorn.run(
        "app.main:app",
        host=config.FASTAPI_HOST,
        port=config.FASTAPI_PORT,
        reload=config.DEBUG_MODE,
        log_level=config.LOG_LEVEL.lower()
    )