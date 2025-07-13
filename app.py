import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import re
import json
from typing import List, Dict, Tuple
import hashlib
import time
from datetime import datetime

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

# Modern Website CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Reset & Variables */
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
    
    /* Navigation Bar */
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
        text-decoration: none;
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
    }
    
    .nav-link:hover {
        color: var(--primary-color);
        background: rgba(99, 102, 241, 0.1);
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, var(--background-primary) 0%, var(--background-secondary) 100%);
        padding: 4rem 2rem;
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
        font-size: 4rem;
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
        font-size: 1.1rem;
        color: var(--text-muted);
        margin-bottom: 3rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .hero-cta {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
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
    
    /* Main Content */
    .main-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 3rem 2rem;
    }
    
    .content-grid {
        display: grid;
        grid-template-columns: 1fr 400px;
        gap: 3rem;
        margin-top: 2rem;
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
    
    /* Chat Interface */
    .chat-container {
        background: var(--background-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        height: 500px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .chat-header {
        background: var(--background-tertiary);
        padding: 1rem;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .message {
        max-width: 80%;
        padding: 1rem 1.5rem;
        border-radius: 1.5rem;
        position: relative;
        animation: slideIn 0.3s ease-out;
    }
    
    .message.user {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 0.5rem;
    }
    
    .message.bot {
        background: var(--background-tertiary);
        color: var(--text-primary);
        align-self: flex-start;
        border-bottom-left-radius: 0.5rem;
        border-left: 3px solid var(--primary-color);
    }
    
    .message-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .message-content {
        line-height: 1.5;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .chat-input {
        border-top: 1px solid var(--border-color);
        padding: 1rem;
        background: var(--background-tertiary);
    }
    
    .input-group {
        display: flex;
        gap: 0.75rem;
        align-items: flex-end;
    }
    
    .input-field {
        flex: 1;
        background: var(--background-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 0.75rem 1rem;
        color: var(--text-primary);
        font-size: 1rem;
        transition: var(--transition);
        resize: none;
        min-height: 44px;
        max-height: 120px;
    }
    
    .input-field:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    .send-button {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: var(--transition);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .send-button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .send-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
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
    
    /* Quick Actions */
    .quick-actions {
        display: grid;
        gap: 0.75rem;
    }
    
    .quick-action {
        background: var(--background-tertiary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        text-align: left;
        cursor: pointer;
        transition: var(--transition);
        color: var(--text-primary);
        font-weight: 500;
    }
    
    .quick-action:hover {
        background: var(--background-secondary);
        border-color: var(--primary-color);
        transform: translateX(4px);
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        text-align: center;
        box-shadow: var(--shadow-md);
        transition: var(--transition);
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        font-weight: 500;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Form Elements */
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: var(--text-primary);
    }
    
    .form-input {
        width: 100%;
        background: var(--background-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 0.75rem 1rem;
        color: var(--text-primary);
        font-size: 1rem;
        transition: var(--transition);
    }
    
    .form-input:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    .form-button {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: var(--transition);
        width: 100%;
        font-size: 1rem;
    }
    
    .form-button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .form-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }
    
    /* Features Grid */
    .features-grid {
        display: grid;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .feature-item {
        background: var(--background-tertiary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        transition: var(--transition);
        border-left: 4px solid var(--primary-color);
    }
    
    .feature-item:hover {
        transform: translateX(4px);
        background: var(--background-secondary);
    }
    
    /* Footer */
    .footer {
        background: var(--background-secondary);
        border-top: 1px solid var(--border-color);
        padding: 3rem 2rem 2rem;
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
    
    /* Loading States */
    .loading {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        padding: 2rem;
        color: var(--text-secondary);
    }
    
    .spinner {
        width: 20px;
        height: 20px;
        border: 2px solid var(--border-color);
        border-top: 2px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .content-grid {
            grid-template-columns: 1fr;
            gap: 2rem;
        }
        
        .navbar-content {
            padding: 0 1rem;
        }
        
        .navbar-nav {
            gap: 1rem;
        }
        
        .hero-section {
            padding: 2rem 1rem;
        }
        
        .main-content {
            padding: 2rem 1rem;
        }
        
        .message {
            max-width: 90%;
        }
        
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    /* Streamlit Specific Overrides */
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
    
    .stSelectbox > div > div > div {
        background: var(--background-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--border-radius) !important;
        color: var(--text-primary) !important;
    }
    
    .stExpander {
        background: var(--background-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--border-radius) !important;
    }
    
    .stSidebar {
        background: var(--background-secondary) !important;
    }
    
    .stSidebar .stButton > button {
        background: var(--background-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    .stSidebar .stButton > button:hover {
        background: var(--background-secondary) !important;
        border-color: var(--primary-color) !important;
    }
</style>
""", unsafe_allow_html=True)

class GeminiTubeGPT:
    def __init__(self):
        self.transcript = None
        self.video_id = None
        self.model = None
        self.chunks = []
        self.video_title = None
        
    def setup_gemini(self, api_key: str) -> bool:
        """Setup Gemini API"""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2000,
                }
            )
            return True
        except Exception as e:
            st.error(f"Error setting up Gemini: {str(e)}")
            return False
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        if len(url) == 11 and url.replace('-', '').replace('_', '').isalnum():
            return url
            
        return None
    
    def get_transcript(self, video_id: str) -> Tuple[str, bool]:
        """Get transcript from YouTube video"""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
            transcript = " ".join(chunk["text"] for chunk in transcript_list)
            return transcript, True
        except TranscriptsDisabled:
            return "No captions available for this video.", False
        except Exception as e:
            return f"Error fetching transcript: {str(e)}", False
    
    def chunk_transcript(self, transcript: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split transcript into chunks for better processing"""
        chunks = []
        start = 0
        
        while start < len(transcript):
            end = start + chunk_size
            
            if end < len(transcript):
                for i in range(end, max(start + chunk_size - 200, start), -1):
                    if transcript[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = transcript[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
        return chunks
    
    def find_relevant_chunks(self, question: str, chunks: List[str], max_chunks: int = 4) -> List[str]:
        """Find most relevant chunks using Gemini for semantic similarity"""
        if not chunks:
            return []
        
        try:
            relevance_prompt = f"""
            Given this question: "{question}"
            
            Rate the relevance of each text chunk below on a scale of 1-10, where 10 is most relevant.
            Return only a JSON array of scores, one for each chunk.
            
            Chunks:
            {json.dumps(chunks[:10])}
            """
            
            response = self.model.generate_content(relevance_prompt)
            
            try:
                scores = json.loads(response.text)
                if isinstance(scores, list) and len(scores) == len(chunks[:10]):
                    chunk_scores = list(zip(chunks[:10], scores))
                    chunk_scores.sort(key=lambda x: x[1], reverse=True)
                    return [chunk for chunk, score in chunk_scores[:max_chunks]]
            except:
                pass
            
            return chunks[:max_chunks]
            
        except Exception as e:
            st.error(f"Error finding relevant chunks: {str(e)}")
            return chunks[:max_chunks]
    
    def answer_question(self, question: str) -> str:
        """Answer question using Gemini with relevant transcript chunks"""
        if not self.transcript or not self.model:
            return "Please load a video first and ensure Gemini is configured."
        
        try:
            relevant_chunks = self.find_relevant_chunks(question, self.chunks)
            context = "\n\n".join(relevant_chunks)
            
            prompt = f"""
            You are TubeGPT, a helpful AI assistant that answers questions about YouTube videos.
            Answer ONLY from the provided transcript context below.
            If the context is insufficient to answer the question, say you don't know.
            Be conversational, helpful, and provide specific details from the transcript when possible.
            
            Context from video transcript:
            {context}
            
            Question: {question}
            
            Please provide a clear, helpful answer based only on the information in the transcript:
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def generate_summary(self) -> str:
        """Generate a comprehensive summary of the video"""
        if not self.transcript or not self.model:
            return "Please load a video first."
        
        try:
            summary_context = "\n\n".join(self.chunks[:6])
            
            prompt = f"""
            Create a comprehensive summary of this YouTube video based on the transcript below.
            Include:
            1. Main topic/theme
            2. Key points discussed
            3. Important people or entities mentioned
            4. Any conclusions or takeaways
            
            Transcript:
            {summary_context}
            
            Summary:
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"

def main():
    # Initialize session state
    if 'tube_gpt' not in st.session_state:
        st.session_state.tube_gpt = GeminiTubeGPT()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'video_loaded' not in st.session_state:
        st.session_state.video_loaded = False
    
    if 'api_configured' not in st.session_state:
        st.session_state.api_configured = False
    
    # Navigation Bar
    st.markdown("""
    <div class="navbar">
        <div class="navbar-content">
            <div class="navbar-brand">
                <span class="logo">🎥</span>
                <span>TubeGPT</span>
            </div>
            <div class="navbar-nav">
                <a href="#features" class="nav-link">Features</a>
                <a href="#about" class="nav-link">About</a>
                <a href="https://github.com/adhirajsingh/tubegpt" class="nav-link">GitHub</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">TubeGPT</h1>
            <p class="hero-subtitle">AI-Powered YouTube Video Q&A Assistant</p>
            <p class="hero-description">
                Transform any YouTube video into an interactive knowledge base. 
                Ask questions, get summaries, and explore video content with the power of AI.
            </p>
            <div class="hero-cta">
                <button class="cta-button" onclick="document.querySelector('.main-content').scrollIntoView()">
                    🚀 Get Started
                </button>
                <button class="cta-button secondary" onclick="document.querySelector('#features').scrollIntoView()">
                    ✨ Learn More
                </button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main Content
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Setup Section
    if not st.session_state.api_configured:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <span class="card-icon">🔑</span>
                <h2 class="card-title">Setup Your API Key</h2>
            </div>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                To get started, you'll need a Google Gemini API key. It's free and takes just a minute to set up.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("api_setup"):
            api_key = st.text_input(
                "🔑 Enter your Gemini API Key",
                type="password",
                placeholder="Enter your API key here...",
                help="Get your free API key from Google AI Studio"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("🚀 Setup API", use_container_width=True)
            with col2:
                if st.form_submit_button("ℹ️ Get API Key", use_container_width=True):
                    st.info("Visit: https://makersuite.google.com/app/apikey")
            
            if submitted and api_key:
                with st.spinner("Configuring Gemini..."):
                    if st.session_state.tube_gpt.setup_gemini(api_key):
                        st.session_state.api_configured = True
                        st.success("✅ API configured successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to configure API. Please check your key.")
    
    else:
        # Video Loading Section
        if not st.session_state.video_loaded:
            st.markdown("""
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">📹</span>
                    <h2 class="card-title">Load a YouTube Video</h2>
                </div>
                <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                    Enter any YouTube URL or video ID to start analyzing the video content.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("video_load"):
                video_input = st.text_input(
                    "📹 YouTube URL or Video ID",
                    placeholder="https://youtube.com/watch?v=... or video_id",
                    help="Paste a YouTube URL or just the video ID"
                )
                
                submitted = st.form_submit_button("📥 Load Video", use_container_width=True)
                
                if submitted and video_input:
                    video_id = st.session_state.tube_gpt.extract_video_id(video_input)
                    if video_id:
                        with st.spinner("🔄 Fetching transcript..."):
                            transcript, success = st.session_state.tube_gpt.get_transcript(video_id)
                            
                            if success:
                                st.session_state.tube_gpt.transcript = transcript
                                st.session_state.tube_gpt.video_id = video_id
                                
                                with st.spinner("🧠 Processing transcript..."):
                                    st.session_state.tube_gpt.chunks = st.session_state.tube_gpt.chunk_transcript(transcript)
                                    st.session_state.video_loaded = True
                                    st.session_state.chat_history = []
                                    st.success(f"✅ Video loaded! Created {len(st.session_state.tube_gpt.chunks)} chunks.")
                                    st.rerun()
                            else:
                                st.error(f"❌ {transcript}")
                    else:
                        st.error("❌ Invalid YouTube URL or Video ID")
        
        else:
            # Main Application Interface
            st.markdown(f"""
            <div class="status-card success">
                <span>🎬</span>
                <div>
                    <strong>Video Loaded: {st.session_state.tube_gpt.video_id}</strong><br>
                    <small>Ready for questions! Ask anything about the video content.</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Stats
            transcript_length = len(st.session_state.tube_gpt.transcript)
            chunk_count = len(st.session_state.tube_gpt.chunks)
            word_count = len(st.session_state.tube_gpt.transcript.split())
            
            st.markdown(f"""
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-number">{chunk_count}</span>
                    <span class="stat-label">Chunks</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{word_count:,}</span>
                    <span class="stat-label">Words</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{transcript_length//1000}K</span>
                    <span class="stat-label">Characters</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Content Grid
            st.markdown('<div class="content-grid">', unsafe_allow_html=True)
            
            # Chat Section
            st.markdown("""
            <div class="chat-container">
                <div class="chat-header">
                    <span style="font-size: 1.5rem;">💬</span>
                    <div>
                        <strong>Chat with Video</strong>
                        <div style="font-size: 0.9rem; color: var(--text-secondary);">Ask questions about the video content</div>
                    </div>
                </div>
                <div class="chat-messages" id="chat-messages">
            """, unsafe_allow_html=True)
            
            # Display chat history
            if st.session_state.chat_history:
                for question, answer in st.session_state.chat_history:
                    st.markdown(f"""
                    <div class="message user">
                        <div class="message-header">
                            <span>🙋</span>
                            <span>You</span>
                        </div>
                        <div class="message-content">{question}</div>
                    </div>
                    <div class="message bot">
                        <div class="message-header">
                            <span>🤖</span>
                            <span>TubeGPT</span>
                        </div>
                        <div class="message-content">{answer}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; color: var(--text-muted); padding: 2rem;">
                    <span style="font-size: 3rem;">💬</span>
                    <p>Start a conversation about the video!</p>
                    <p style="font-size: 0.9rem;">Ask questions, request summaries, or explore the content.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Chat Input
            with st.form("chat_form", clear_on_submit=True):
                st.markdown('<div class="chat-input">', unsafe_allow_html=True)
                question = st.text_input(
                    "💭 Ask a question about the video",
                    placeholder="What is this video about?",
                    label_visibility="collapsed"
                )
                submitted = st.form_submit_button("🚀 Send", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if submitted and question:
                    with st.spinner("🤔 Thinking..."):
                        answer = st.session_state.tube_gpt.answer_question(question)
                        st.session_state.chat_history.append((question, answer))
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sidebar Content
            st.markdown("""
            <div>
                <div class="card">
                    <div class="card-header">
                        <span class="card-icon">⚡</span>
                        <h3 class="card-title">Quick Actions</h3>
                    </div>
                    <div class="quick-actions">
            """, unsafe_allow_html=True)
            
            quick_questions = [
                "📝 Summarize this video",
                "🎯 What are the main topics?",
                "👥 Who are the speakers?",
                "💡 What are the key takeaways?",
                "📊 Any important statistics?",
                "🔍 What problems are discussed?",
                "💭 What solutions are proposed?",
                "⏰ Timeline or dates mentioned?",
                "🏢 Companies mentioned?",
                "🔗 Any recommendations?"
            ]
            
            for i, q in enumerate(quick_questions):
                if st.button(q, key=f"quick_{i}"):
                    with st.spinner("🤔 Processing..."):
                        answer = st.session_state.tube_gpt.answer_question(q[2:])
                        st.session_state.chat_history.append((q[2:], answer))
                        st.rerun()
            
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            # Controls
            st.markdown("""
            <div class="card" style="margin-top: 1rem;">
                <div class="card-header">
                    <span class="card-icon">🎛️</span>
                    <h3 class="card-title">Controls</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                if st.button("📋 Generate Summary", use_container_width=True):
                    with st.spinner("Generating summary..."):
                        summary = st.session_state.tube_gpt.generate_summary()
                        st.session_state.chat_history.append(("Generate a summary of this video", summary))
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close content-grid
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close main-content
    
    # Features Section
    st.markdown("""
    <div id="features" class="main-content">
        <div style="text-align: center; margin-bottom: 3rem;">
            <h2 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);">✨ Features</h2>
            <p style="font-size: 1.2rem; color: var(--text-secondary); max-width: 600px; margin: 0 auto;">
                Discover what makes TubeGPT the ultimate YouTube video analysis tool
            </p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">🎥</span>
                    <h3 class="card-title">YouTube Integration</h3>
                </div>
                <p style="color: var(--text-secondary);">
                    Load any YouTube video with captions instantly. Support for all major video formats and languages.
                </p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">🧠</span>
                    <h3 class="card-title">Google Gemini 2.0</h3>
                </div>
                <p style="color: var(--text-secondary);">
                    Powered by the latest Google Gemini 2.0 Flash model for intelligent, context-aware responses.
                </p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">🔍</span>
                    <h3 class="card-title">Smart Chunking</h3>
                </div>
                <p style="color: var(--text-secondary);">
                    Intelligent text processing that breaks down video content for better context understanding.
                </p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">💬</span>
                    <h3 class="card-title">Natural Chat</h3>
                </div>
                <p style="color: var(--text-secondary);">
                    Conversational interface that feels natural and intuitive for exploring video content.
                </p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">⚡</span>
                    <h3 class="card-title">Quick Questions</h3>
                </div>
                <p style="color: var(--text-secondary);">
                    Pre-built queries for common needs like summaries, key points, and speaker identification.
                </p>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">📊</span>
                    <h3 class="card-title">Video Analytics</h3>
                </div>
                <p style="color: var(--text-secondary);">
                    Detailed statistics about video content including word count, chunks, and processing metrics.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
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

if __name__ == "__main__":
    main()
