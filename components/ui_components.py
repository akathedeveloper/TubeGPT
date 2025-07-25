import streamlit as st

class UIComponents:
    @staticmethod
    def apply_light_theme():
        """Apply light theme styling"""
        st.markdown("""
        <style>
            /* Hide Streamlit branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display: none;}
             /* Full width layout - REMOVE LEFT/RIGHT MARGINS */
        .main .block-container {
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            padding-top: 1rem !important;
            max-width: 100% !important;
            width: 100% !important;
        }
        
        .css-18e3th9, .css-1d391kg {
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
            
            /* Light theme styling */
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
                height: 3rem;
            }
            
            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
            
            /* Full width container */
            .main .block-container {
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
                max-width: 100%;
            }
            
            /* Tab styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 2rem;
                background-color: #f8fafc;
                padding: 0.5rem;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 3rem;
                padding: 0.5rem 1.5rem;
                background-color: transparent;
                border-radius: 8px;
                color: #6b7280;
                font-weight: 600;
            }
            
            .stTabs [aria-selected="true"] {
                background: linear-gradient(90deg, #3b82f6, #1d4ed8);
                color: white;
            }
            
            /* Input styling */
            .stTextInput > div > div > input {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                height: 3rem;
            }
            
            .stTextInput > div > div > input:focus {
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_app_header():
        """Render custom app header"""
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #1f2937; margin-bottom: 0.5rem; background: linear-gradient(90deg, #3b82f6, #1d4ed8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                🎥 TubeGPT
            </h1>
            <p style="color: #6b7280; font-style: italic;">AI-Powered YouTube Video Q&A Assistant by Adhiraj Singh</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_hero_streamlit():
        """Render hero section"""
        st.markdown("## 🚀 Transform YouTube Videos into Interactive Knowledge")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            **TubeGPT** uses Google Gemini AI to help you chat with any YouTube video, 
            get instant summaries, and explore content like never before.
            """)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.button("🚀 Get Started", type="primary", use_container_width=True, key="hero_start")
            
            with col_b:
                if st.button("📹 Learn More", use_container_width=True, key="hero_learn"):
                    st.info("TubeGPT helps you understand video content through AI-powered conversations!")
        
        st.divider()
    
    @staticmethod
    def render_features_streamlit():
        """Render features section"""
        st.markdown("## ✨ Powerful Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎥 YouTube Integration")
            st.write("Load any YouTube video instantly with automatic transcript extraction.")
            
            st.markdown("### 💬 Interactive Chat")
            st.write("Natural conversation interface for exploring video content.")
        
        with col2:
            st.markdown("### 🧠 AI-Powered Analysis")
            st.write("Powered by Google Gemini 2.0 for intelligent responses.")
            
            st.markdown("### ⚡ Quick Actions")
            st.write("Pre-built queries for summaries and key insights.")
        
        with col3:
            st.markdown("### 📊 Smart Analytics")
            st.write("Detailed insights about video content and metrics.")
            
            st.markdown("### 🔍 Smart Search")
            st.write("Advanced semantic search through video content.")
    
    @staticmethod
    def render_footer_streamlit():
        """Render footer"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎥 TubeGPT")
            st.write("AI-Powered Video Assistant")
        
        with col2:
            st.markdown("### 🔗 Links")
            st.write("• [GitHub](https://github.com/akathedeveloper/tubegpt)")
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
                if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                if st.button("🔄 New Video", use_container_width=True, key="new_video"):
                    st.session_state.video_loaded = False
                    st.session_state.chat_history = []
                    st.rerun()
