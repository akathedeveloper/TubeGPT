"""
TubeGPT - AI-Powered YouTube Video Assistant
A RAG-based chatbot for intelligent YouTube video content analysis.
"""

__title__ = "TubeGPT"
__version__ = "1.0.0"
__author__ = "Adhiraj Singh"
__description__ = "AI-Powered YouTube Video Assistant using RAG and Gemini AI"

from utils import YouTubeProcessor, GeminiHandler, VectorStoreManager
from config import Config

__all__ = [
    'YouTubeProcessor',
    'GeminiHandler',
    'VectorStoreManager',
    'Config'
]
