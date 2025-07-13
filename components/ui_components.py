import streamlit as st
from utils.constants import APP_CONFIG

class UIComponents:
    @staticmethod
    def load_saas_styles():
        """Load modern SaaS-style CSS"""
        st.markdown("""
        <style>
            /* Import Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
            
            /* CSS Variables */
            :root {
                --primary-color: #6366f1;
                --primary-dark: #4f46e5;
                --secondary-color: #8b5cf6;
                --accent-color: #06b6d4;
                --success-color: #10b981;
                --warning-color: #f59e0b;
                --error-color: #ef4444;
                --background-primary: #0f172a;
                --background-secondary: #1e293b;
                --background-tertiary: #334155;
                --text-primary: #f8fafc;
                --text-secondary: #cbd5e1;
                --text-muted: #64748b;
                --border-color: #334155;
                --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
                --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
                --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
                --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
                --border-radius: 12px;
                --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            /* Global Styles */
            .stApp {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: var(--background-primary);
                color: var(--text-primary);
                line-height: 1.6;
            }
            
            .main .block-container {
                padding: 0;
                max-width: 100%;
            }
            
            /* Hide Streamlit Elements */
            #MainMenu, footer, header, .stDeployButton {visibility: hidden;}
            .stApp > div:first-child {margin-top: -80px;}
            
            /* Navigation */
            .navbar {
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(20px);
                border-bottom: 1px solid var(--border-color);
                padding: 1rem 0;
                position: sticky;
                top: 0;
                z-index: 1000;
                box-shadow: var(--shadow-md);
            }
            
            .navbar-content {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 2rem;
            }
            
            .navbar-brand {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                font-size: 1.5rem;
                font-weight: 700;
                color: var(--text-primary);
            }
            
            .navbar-brand .logo {
                font-size: 2rem;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .navbar-nav {
                display: flex;
                gap: 2rem;
                align-items: center;
            }
            
            .nav-link {
                color: var(--text-secondary);
                text-decoration: none;
                font-weight: 500;
                transition: var(--transition);
                padding: 0.5rem 1rem;
                border-radius: var(--border-radius);
                cursor: pointer;
            }
            
            .nav-link:hover, .nav-link.active {
                color: var(--primary-color);
                background: rgba(99, 102, 241, 0.1);
            }
            
            /* Hero Section */
            .hero-section {
                background: linear-gradient(135deg, var(--background-primary) 0%, var(--background-secondary) 100%);
                padding: 6rem 2rem;
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            
            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(circle at 30% 20%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
                            radial-gradient(circle at 70% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
                pointer-events: none;
            }
            
            .hero-content {
                max-width: 800px;
                margin: 0 auto;
                position: relative;
                z-index: 1;
            }
            
            .hero-title {
                font-size: 4.5rem;
                font-weight: 800;
                margin-bottom: 1.5rem;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color), var(--accent-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                line-height: 1.1;
            }
            
            .hero-subtitle {
                font-size: 1.5rem;
                color: var(--text-secondary);
                margin-bottom: 2rem;
                font-weight: 400;
            }
            
            .hero-description {
                font-size: 1.2rem;
                color: var(--text-muted);
                margin-bottom: 3rem;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }
            
            .cta-button {
                background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
                color: white;
                padding: 1rem 2rem;
                border-radius: var(--border-radius);
                text-decoration: none;
                font-weight: 600;
                transition: var(--transition);
                box-shadow: var(--shadow-lg);
                border: none;
                cursor: pointer;
                font-size: 1rem;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-xl);
            }
            
            .cta-button.secondary {
                background: transparent;
                border: 2px solid var(--border-color);
                color: var(--text-primary);
            }
            
            .cta-button.secondary:hover {
                border-color: var(--primary-color);
                background: rgba(99, 102, 241, 0.1);
            }
            
            /* Cards */
            .card {
                background: var(--background-secondary);
                border: 1px solid var(--border-color);
                border-radius: var(--border-radius);
                padding: 2rem;
                box-shadow: var(--shadow-md);
                transition: var(--transition);
            }
            
            .card:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
                border-color: var(--primary-color);
            }
            
            .card-header {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 1.5rem;
            }
            
            .card-title {
                font-size: 1.25rem;
                font-weight: 600;
                color: var(--text-primary);
                margin: 0;
            }
            
            .card-icon {
                font-size: 1.5rem;
                color: var(--primary-color);
            }
            
            /* Status Cards */
            .status-card {
                padding: 1rem;
                border-radius: var(--border-radius);
                margin: 1rem 0;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                font-weight: 500;
            }
            
            .status-card.success {
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                color: var(--success-color);
            }
            
            .status-card.warning {
                background: rgba(245, 158, 11, 0.1);
                border: 1px solid rgba(245, 158, 11, 0.3);
                color: var(--warning-color);
            }
            
            .status-card.info {
                background: rgba(6, 182, 212, 0.1);
                border: 1px solid rgba(6, 182, 212, 0.3);
                color: var(--accent-color);
            }
            
            /* Features Grid */
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                margin: 4rem 0;
            }
            
            .feature-card {
                background: var(--background-secondary);
                border: 1px solid var(--border-color);
                border-radius: var(--border-radius);
                padding: 2rem;
                text-align: center;
                transition: var(--transition);
            }
            
            .feature-card:hover {
                transform: translateY(-4px);
                box-shadow: var(--shadow-lg);
                border-color: var(--primary-color);
            }
            
            .feature-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                color: var(--primary-color);
            }
            
            .feature-title {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1rem;
                color: var(--text-primary);
            }
            
            .feature-description {
                color: var(--text-secondary);
                line-height: 1.6;
            }
            
            /* How It Works */
            .how-it-works {
                padding: 4rem 2rem;
                background: var(--background-secondary);
                margin: 4rem 0;
                border-radius: var(--border-radius);
            }
            
            .steps-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 2rem;
                margin-top: 3rem;
            }
            
            .step-card {
                text-align: center;
                position: relative;
            }
            
            .step-number {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                font-weight: 700;
                margin: 0 auto 1rem;
            }
            
            .step-title {
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: var(--text-primary);
            }
            
            .step-description {
                color: var(--text-secondary);
            }
            
            /* Footer */
            .footer {
                background: var(--background-secondary);
                border-top: 1px solid var(--border-color);
                padding: 4rem 2rem 2rem;
                text-align: center;
                margin-top: 4rem;
            }
            
            .footer-content {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .footer-title {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 1rem;
                color: var(--text-primary);
            }
            
            .footer-text {
                color: var(--text-secondary);
                margin-bottom: 0.5rem;
            }
            
            .footer-links {
                display: flex;
                justify-content: center;
                gap: 2rem;
                margin: 2rem 0;
                flex-wrap: wrap;
            }
            
            .footer-link {
                color: var(--text-muted);
                text-decoration: none;
                transition: var(--transition);
            }
            
            .footer-link:hover {
                color: var(--primary-color);
            }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .hero-title {
                    font-size: 3rem;
                }
                
                .navbar-content {
                    padding: 0 1rem;
                }
                
                .hero-section {
                    padding: 4rem 1rem;
                }
                
                .features-grid {
                    grid-template-columns: 1fr;
                }
                
                .steps-grid {
                    grid-template-columns: 1fr;
                }
            }
            
            /* Streamlit Overrides */
            .stButton > button {
                background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)) !important;
                color: white !important;
                border: none !important;
                border-radius: var(--border-radius) !important;
                padding: 0.75rem 1.5rem !important;
                font-weight: 600 !important;
                transition: var(--transition) !important;
                width: 100% !important;
            }
            
            .stButton > button:hover {
                transform: translateY(-1px) !important;
                box-shadow: var(--shadow-md) !important;
            }
            
            .stTextInput > div > div > input {
                background: var(--background-secondary) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: var(--border-radius) !important;
                color: var(--text-primary) !important;
                padding: 0.75rem 1rem !important;
            }
            
            .stTextInput > div > div > input:focus {
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_navigation():
        """Render navigation bar"""
        st.markdown("""
        <div class="navbar">
            <div class="navbar-content">
                <div class="navbar-brand">
                    <span class="logo">🎥</span>
                    <span>TubeGPT</span>
                </div>
                <div class="navbar-nav">
                    <span class="nav-link" onclick="setPage('home')">Home</span>
                    <span class="nav-link" onclick="setPage('dashboard')">Dashboard</span>
                    <span class="nav-link" onclick="setPage('analytics')">Analytics</span>
                    <span class="nav-link" onclick="setPage('settings')">Settings</span>
                </div>
            </div>
        </div>
        
        <script>
            function setPage(page) {
                // This would be handled by Streamlit session state in practice
                console.log('Navigate to:', page);
            }
        </script>
        """, unsafe_allow_html=True)
        
        # Navigation buttons (Streamlit implementation)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.current_page = 'home'
                st.rerun()
        with col2:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
                st.rerun()
        with col3:
            if st.button("📈 Analytics", use_container_width=True):
                st.session_state.current_page = 'analytics'
                st.rerun()
        with col4:
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.current_page = 'settings'
                st.rerun()
    
    @staticmethod
    def render_hero_section():
        """Render hero section"""
        st.markdown("""
        <div class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">TubeGPT</h1>
                <p class="hero-subtitle">Transform YouTube Videos into Interactive Knowledge</p>
                <p class="hero-description">
                    Powered by Google Gemini AI, TubeGPT lets you chat with any YouTube video, 
                    get instant summaries, and explore content like never before.
                </p>
                <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                    <button class="cta-button" onclick="document.querySelector('.navbar-nav span:nth-child(2)').click()">
                        🚀 Get Started Free
                    </button>
                    <button class="cta-button secondary">
                        📹 Watch Demo
                    </button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_features_section():
        """Render features section"""
        st.markdown("""
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
            <div style="text-align: center; margin: 4rem 0 2rem;">
                <h2 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);">
                    ✨ Powerful Features
                </h2>
                <p style="font-size: 1.2rem; color: var(--text-secondary); max-width: 600px; margin: 0 auto;">
                    Everything you need to unlock the full potential of YouTube videos
                </p>
            </div>
            
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🎥</div>
                    <h3 class="feature-title">YouTube Integration</h3>
                    <p class="feature-description">
                        Load any YouTube video instantly. Support for all video formats with automatic transcript extraction.
                    </p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <h3 class="feature-title">AI-Powered Analysis</h3>
                    <p class="feature-description">
                        Powered by Google Gemini 2.0 for intelligent, context-aware responses and deep content understanding.
                    </p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">💬</div>
                    <h3 class="feature-title">Interactive Chat</h3>
                    <p class="feature-description">
                        Natural conversation interface that feels intuitive and responsive for exploring video content.
                    </p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3 class="feature-title">Smart Analytics</h3>
                    <p class="feature-description">
                        Detailed insights about video content including key metrics, topics, and engagement patterns.
                    </p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <h3 class="feature-title">Quick Actions</h3>
                    <p class="feature-description">
                        Pre-built queries for common needs like summaries, key points, and speaker identification.
                    </p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h3 class="feature-title">Smart Search</h3>
                    <p class="feature-description">
                        Advanced semantic search through video content with intelligent chunk retrieval.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_how_it_works():
        """Render how it works section"""
        st.markdown("""
        <div class="how-it-works">
            <div style="max-width: 1200px; margin: 0 auto;">
                <div style="text-align: center;">
                    <h2 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);">
                        🚀 How It Works
                    </h2>
                    <p style="font-size: 1.2rem; color: var(--text-secondary);">
                        Get started in just three simple steps
                    </p>
                </div>
                
                <div class="steps-grid">
                    <div class="step-card">
                        <div class="step-number">1</div>
                        <h3 class="step-title">Setup API Key</h3>
                        <p class="step-description">
                            Get your free Google Gemini API key and configure it in seconds
                        </p>
                    </div>
                    
                    <div class="step-card">
                        <div class="step-number">2</div>
                        <h3 class="step-title">Load Video</h3>
                        <p class="step-description">
                            Paste any YouTube URL and let our AI process the video transcript
                        </p>
                    </div>
                    
                    <div class="step-card">
                        <div class="step-number">3</div>
                        <h3 class="step-title">Start Chatting</h3>
                        <p class="step-description">
                            Ask questions, get summaries, and explore the video content interactively
                        </p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_footer():
        """Render footer"""
        st.markdown("""
        <div class="footer">
            <div class="footer-content">
                <h3 class="footer-title">🎥 TubeGPT</h3>
                <p class="footer-text">AI-Powered YouTube Video Q&A Assistant</p>
                <p class="footer-text">Built with ❤️ by <strong>Adhiraj Singh</strong></p>
                
                <div class="footer-links">
                    <a href="https://github.com/adhirajsingh/tubegpt" class="footer-link">GitHub</a>
                    <a href="#" class="footer-link">Documentation</a>
                    <a href="#" class="footer-link">Support</a>
                    <a href="#" class="footer-link">Privacy</a>
                    <a href="#" class="footer-link">Terms</a>
                </div>
                
                <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--border-color);">
                    <p style="color: var(--text-muted); font-size: 0.9rem;">
                        Powered by Google Gemini 2.0 Flash • Transform any YouTube video into an interactive knowledge base
                    </p>
                    <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 1rem;">
                        © 2025 TubeGPT. Made with Streamlit & Google Gemini.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_status_bar():
        """Render status bar"""
        if st.session_state.video_loaded:
            st.markdown(f"""
            <div class="status-card success">
                <span style="font-size: 1.5rem;">🎬</span>
                <div>
                    <strong>Video Loaded: {st.session_state.tube_gpt.video_id}</strong><br>
                    <small>Ready for questions! Ask anything about the video content.</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
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
