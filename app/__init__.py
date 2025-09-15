# app/__init__.py
"""Soccer Analytics Chatbot - Main Application Package"""

__version__ = "1.0.0"
__author__ = "Soccer Analytics Team"
__description__ = "A chatbot for soccer data analysis using MCP and Gemini"

# utils/__init__.py
"""Utilities package for the soccer analytics chatbot"""

from .logger import get_logger

__all__ = ["get_logger"]

# mcp_server/__init__.py
"""MCP Server package for soccer data"""

__version__ = "1.0.0"