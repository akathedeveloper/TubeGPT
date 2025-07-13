import streamlit as st
from utils.constants import APP_CONFIG

class UIComponents:
    @staticmethod
    def apply_light_theme():
        """Apply light theme styling using Streamlit's theming"""
        st.markdown("""
        <style>
            /* Light theme overrides */
            .stApp {
                background-color: #ffffff;
                color: #1f2937;
            }
            
            .stButton > button {
                background: linear-gradient(90deg, #3b82f6, #1d4ed8);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
            
            .stSelectbox > div > div {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
            }
            
            .stTextInput > div > div > input {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            
            .stTextInput > div > div > input:focus {
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            /* Hide default Streamlit elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_streamlit_navigation():
        """Render navigation using Streamlit components"""
        # App header
        st.markdown("# 🎥 TubeGPT")
        st.markdown("*AI-Powered YouTube Video Q&A Assistant*")
        
        # Navigation tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📊 Dashboard", "📈 Analytics", "⚙️ Settings"])
        
        with tab1:
            if st.button("Go to Home", key="nav_home", use_container_width=True):
                st.session_state.current_page = 'home'
                st.rerun()
        
        with tab2:
            if st.button("Go to Dashboard", key="nav_dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
                st.rerun()
        
        with tab3:
            if st.button("Go to Analytics", key="nav_analytics", use_container_width=True):
                st.session_state.current_page = 'analytics'
                st.rerun()
        
        with tab4:
            if st.button("Go to Settings", key="nav_settings", use_container_width=True):
                st.session_state.current_page = 'settings'
                st.rerun()
        
        st.divider()
    
    @staticmethod
    def render_hero_streamlit():
        """Render hero section using Streamlit components"""
        # Hero section
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("## 🚀 Transform YouTube Videos into Interactive Knowledge")
            st.markdown("""
            **TubeGPT** uses Google Gemini AI to help you chat with any YouTube video, 
            get instant summaries, and explore content like never before.
            """)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🚀 Get Started", type="primary", use_container_width=True):
                    st.session_state.current_page = 'dashboard'
                    st.rerun()
            
            with col_b:
                if st.button("📹 Learn More", use_container_width=True):
                    st.info("TubeGPT helps you understand video content through AI-powered conversations!")
        
        st.divider()
    
    @staticmethod
    def render_features_streamlit():
        """Render features section using Streamlit components"""
        st.markdown("## ✨ Powerful Features")
        
        # Features grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container():
                st.markdown("### 🎥 YouTube Integration")
                st.write("Load any YouTube video instantly with automatic transcript extraction.")
                
                st.markdown("### 💬 Interactive Chat")
                st.write("Natural conversation interface for exploring video content.")
        
        with col2:
            with st.container():
                st.markdown("### 🧠 AI-Powered Analysis")
                st.write("Powered by Google Gemini 2.0 for intelligent responses.")
                
                st.markdown("### ⚡ Quick Actions")
                st.write("Pre-built queries for summaries and key insights.")
        
        with col3:
            with st.container():
                st.markdown("### 📊 Smart Analytics")
                st.write("Detailed insights about video content and metrics.")
                
                st.markdown("### 🔍 Smart Search")
                st.write("Advanced semantic search through video content.")
        
        st.divider()
    
    @staticmethod
    def render_footer_streamlit():
        """Render footer using Streamlit components"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎥 TubeGPT")
            st.write("AI-Powered Video Assistant")
        
        with col2:
            st.markdown("### 🔗 Links")
            st.write("• [GitHub](https://github.com/adhirajsingh/tubegpt)")
            st.write("• [Documentation](#)")
            st.write("• [Support](#)")
        
        with col3:
            st.markdown("### 👨‍💻 Developer")
            st.write("Built with ❤️ by **Adhiraj Singh**")
            st.write("Powered by Google Gemini")
        
        st.markdown("---")
        st.markdown("*© 2025 TubeGPT. Made with Streamlit & Google Gemini.*")
    
    @staticmethod
    def render_status_indicator():
        """Render status indicator"""
        if st.session_state.video_loaded:
            st.success(f"🎬 **Video Loaded:** {st.session_state.tube_gpt.video_id} - Ready for questions!")
    
    @staticmethod
    def render_controls():
        """Render control buttons"""
        if st.session_state.video_loaded:
            st.markdown("### 🎛️ Controls")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                if st.button("🔄 New Video", use_container_width=True):
                    st.session_state.video_loaded = False
                    st.session_state.chat_history = []
                    st.rerun()
