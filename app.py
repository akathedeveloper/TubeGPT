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

# Page configuration with custom title
st.set_page_config(
    page_title="TubeGPT - AI Video Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed",  # Collapsed for full screen
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
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

def main():
    """Main application entry point"""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Apply light theme and full screen styling
        UIComponents.apply_light_theme()
        
        # Render navigation (this will handle page switching)
        UIComponents.render_navigation()
        
        # Render content based on current page
        if st.session_state.current_page == 'home':
            render_home_page()
        elif st.session_state.current_page == 'dashboard':
            render_dashboard()
        elif st.session_state.current_page == 'analytics':
            render_analytics_page()
        elif st.session_state.current_page == 'settings':
            render_settings_page()
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")

def render_home_page():
    """Render the home/landing page"""
    UIComponents.render_hero_streamlit()
    UIComponents.render_features_streamlit()
    UIComponents.render_footer_streamlit()

def render_dashboard():
    """Render the main dashboard"""
    if not st.session_state.api_configured:
        AuthComponent.render_api_setup()
    elif not st.session_state.video_loaded:
        VideoComponent.render_video_loader()
    else:
        render_main_interface()

def render_main_interface():
    """Render the main chat interface with full screen layout"""
    # Status indicator
    UIComponents.render_status_indicator()
    
    # Full screen main content layout
    col1, col2 = st.columns([3, 1], gap="large")  # Adjusted ratio for better space usage
    
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
    st.title("📊 Analytics Dashboard")
    
    if st.session_state.video_loaded:
        AnalyticsComponent.render_detailed_analytics()
    else:
        st.info("💡 Load a video to see detailed analytics")

def render_settings_page():
    """Render settings page"""
    st.title("⚙️ Settings")
    AuthComponent.render_settings()

if __name__ == "__main__":
    main()
