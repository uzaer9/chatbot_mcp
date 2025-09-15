import os
from dotenv import load_dotenv
from typing import List # Import List

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Server Configuration
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "localhost")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # MCP Server Configuration
    MCP_SERVER_PATH: str = os.getenv("MCP_SERVER_PATH", "./mcp_server/soccer_server.py")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "Soccer Analytics Chatbot")
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"
    
    # Data Configuration
    MAX_RESULTS_PER_QUERY: int = int(os.getenv("MAX_RESULTS_PER_QUERY", "50"))

    # --- ADD THIS SECTION BACK ---
    # Static League Data
    AVAILABLE_LEAGUES: List[str] = [
        "Big 5 European Leagues Combined",
        "ENG-Premier League",
        "ESP-La Liga",
        "FRA-Ligue 1",
        "GER-Bundesliga",
        "INT-European Championship",
        "INT-Women's World Cup",
        "INT-World Cup",
        "ITA-Serie A"
    ]
    # ---------------------------
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        return True

# Global config instance
config = Config()

# Validate configuration on import
try:
    config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please check your .env file")