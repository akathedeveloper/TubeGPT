import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default API key if available
if os.getenv("GEMINI_API_KEY"):
    st.session_state.default_api_key = os.getenv("GEMINI_API_KEY")

# Run the main app
if __name__ == "__main__":
    import app
    app.main()
