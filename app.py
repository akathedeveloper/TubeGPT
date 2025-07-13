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
    """Initialize all session state variables with validation"""
    # Core application state
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
    
    # Additional state variables
    if 'app_version' not in st.session_state:
        st.session_state.app_version = APP_CONFIG.get('version', '2.0.0')
    
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'theme': 'dark',
            'language': 'en',
            'notifications': True
        }

def main():
    """Main application entry point"""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Validate current page
        valid_pages = ['home', 'dashboard', 'analytics', 'settings']
        if st.session_state.current_page not in valid_pages:
            st.session_state.current_page = 'home'
        
        # Load CSS
        UIComponents.load_saas_styles()
        
        # Navigation
        UIComponents.render_navigation()
        
        # Page routing
        page_functions = {
            'home': render_home_page,
            'dashboard': render_dashboard,
            'analytics': render_analytics_page,
            'settings': render_settings_page
        }
        
        # Render the current page
        page_functions[st.session_state.current_page]()
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")
        
        # Debug information (only in development)
        if st.checkbox("Show debug info"):
            st.exception(e)

def render_home_page():
    """Render the home/landing page"""
    try:
        UIComponents.render_hero_section()
        UIComponents.render_features_section()
        UIComponents.render_how_it_works()
        UIComponents.render_footer()
    except Exception as e:
        st.error("Error loading home page components")
        st.exception(e)

def render_dashboard():
    """Render the main dashboard"""
    try:
        if not st.session_state.api_configured:
            AuthComponent.render_api_setup()
        elif not st.session_state.video_loaded:
            VideoComponent.render_video_loader()
        else:
            render_main_interface()
    except Exception as e:
        st.error("Error loading dashboard")
        st.exception(e)

def render_main_interface():
    """Render the main chat interface"""
    try:
        # Status bar
        UIComponents.render_status_bar()
        
        # Main content grid
        col1, col2 = st.columns([2.5, 1])
        
        with col1:
            ChatComponent.render_chat_interface()
        
        with col2:
            render_sidebar_content()
    except Exception as e:
        st.error("Error loading main interface")
        st.exception(e)

def render_sidebar_content():
    """Render sidebar content"""
    try:
        # Quick actions
        ChatComponent.render_quick_actions()
        
        # Video analytics
        if st.session_state.video_loaded:
            AnalyticsComponent.render_video_stats()
        
        # Controls
        UIComponents.render_controls()
    except Exception as e:
        st.error("Error loading sidebar content")
        st.exception(e)

def render_analytics_page():
    """Render analytics page"""
    try:
        st.markdown("# 📊 Analytics Dashboard")
        
        if st.session_state.video_loaded:
            AnalyticsComponent.render_detailed_analytics()
        else:
            st.info("Load a video to see analytics")
    except Exception as e:
        st.error("Error loading analytics page")
        st.exception(e)

def render_settings_page():
    """Render settings page"""
    try:
        st.markdown("# ⚙️ Settings")
        AuthComponent.render_settings()
    except Exception as e:
        st.error("Error loading settings page")
        st.exception(e)

if __name__ == "__main__":
    main()
