import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7
    TOP_K_RESULTS = 4
    
    # Streamlit page config
    PAGE_TITLE = "TubeGPT - AI YouTube Assistant"
    PAGE_ICON = "🎥"
    LAYOUT = "wide"
    
    # Model configuration
    GEMINI_MODEL = "gemini-2.0-flash-exp"
    EMBEDDING_MODEL = "models/text-embedding-004"
