import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import re
import json
from typing import List, Dict, Tuple
import hashlib
import time
from datetime import datetime

# Component imports with error handling
try:
    from components import (
        UIComponents,
        AuthComponent, 
        VideoComponent,
        ChatComponent,
        AnalyticsComponent
    )
    from core import GeminiTubeGPT
    from utils import APP_CONFIG, QUICK_QUESTIONS
except ImportError as e:
    st.error(f"Missing component: {str(e)}")
    st.info("Please ensure all component files are properly installed.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="TubeGPT - AI Video Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/adhirajsingh/tubegpt',
        'Report a bug': "https://github.com/adhirajsingh/tubegpt/issues",
        'About': "# TubeGPT\nAI-Powered YouTube Video Q&A Assistant by Adhiraj Singh"
    }
)

def initialize_session_state():
    """Initialize all session state variables"""
    if 'tube_gpt' not in st.session_state:
        st.session_state.tube_gpt = GeminiTubeGPT()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'video_loaded' not in st.session_state:
        st.session_state.video_loaded = False
    
    if 'api_configured' not in st.session_state:
        st.session_state.api_configured = False
    
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0

def main():
    """Main application entry point"""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Apply light theme
        UIComponents.apply_light_theme()
        
        # Render app header
        UIComponents.render_app_header()
        
        # Navigation tabs (removed Settings)
        tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Dashboard", "📈 Analytics"])
        
        with tab1:
            render_home_page()
        
        with tab2:
            render_dashboard()
        
        with tab3:
            render_analytics_page()
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        if st.checkbox("Show debug info"):
            st.exception(e)

def render_home_page():
    """Render the home/landing page"""
    UIComponents.render_hero_streamlit()
    UIComponents.render_features_streamlit()
    UIComponents.render_footer_streamlit()

def render_dashboard():
    """Render the main dashboard"""
    if not st.session_state.api_configured:
        st.markdown("## 🔑 Setup Required")
        AuthComponent.render_api_setup()
    elif not st.session_state.video_loaded:
        st.markdown("## 📹 Load Video")
        VideoComponent.render_video_loader()
    else:
        render_main_interface()

def render_main_interface():
    """Render the main chat interface"""
    # Status indicator
    UIComponents.render_status_indicator()
    
    # Main content layout
    col1, col2 = st.columns([3, 1], gap="large")
    
    with col1:
        ChatComponent.render_chat_interface()
    
    with col2:
        render_sidebar_content()

def render_sidebar_content():
    """Render sidebar content"""
    ChatComponent.render_quick_actions()
    
    if st.session_state.video_loaded:
        AnalyticsComponent.render_video_stats()
    
    UIComponents.render_controls()

def render_analytics_page():
    """Render analytics page"""
    st.markdown("## 📊 Analytics Dashboard")
    
    if st.session_state.video_loaded:
        AnalyticsComponent.render_detailed_analytics()
    else:
        st.info("💡 Load a video to see detailed analytics")

if __name__ == "__main__":
    main()
