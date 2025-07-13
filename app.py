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
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/adhirajsingh/tubegpt',
        'Report a bug': "https://github.com/adhirajsingh/tubegpt/issues",
        'About': "# TubeGPT\nAI-Powered YouTube Video Q&A Assistant by Adhiraj Singh"
    }
)

# Enhanced Professional CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Professional Header */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.1;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        margin-bottom: 0.5rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    .hero-author {
        font-size: 1rem;
        font-weight: 500;
        opacity: 0.8;
        position: relative;
        z-index: 1;
    }
    
    /* Modern Cards */
    .modern-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .modern-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* Chat Interface */
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-height: 600px;
        overflow-y: auto;
    }
    
    .message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        margin-left: 20%;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        position: relative;
        animation: slideInRight 0.3s ease;
    }
    
    .message-bot {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #333;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        position: relative;
        animation: slideInLeft 0.3s ease;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Status Cards */
    .status-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
    }
    
    .info-card {
        background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(23, 162, 184, 0.3);
    }
    
    /* Stats Dashboard */
    .stats-dashboard {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stat-label {
        font-size: 0.9rem;
        font-weight: 500;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Quick Action Buttons */
    .quick-action-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .quick-btn {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e9ecef;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        text-align: left;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        color: #495057;
    }
    
    .quick-btn:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.75rem;
        margin: 1rem 0;
    }
    
    .feature-item {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        transform: translateX(4px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
        border-left-color: #764ba2;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e9ecef;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }
    
    /* Footer */
    .professional-footer {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-top: 3rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Loading Animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
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
        
        .message-user, .message-bot {
            margin-left: 5%;
            margin-right: 5%;
        }
        
        .stats-dashboard {
            grid-template-columns: repeat(2, 1fr);
        }
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
    # Professional Hero Header
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">🎥 TubeGPT</div>
        <div class="hero-subtitle">AI-Powered YouTube Video Q&A Assistant</div>
        <div class="hero-author">Crafted with ❤️ by Adhiraj Singh</div>
        <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
            Powered by Google Gemini 2.0 Flash • Transform any YouTube video into an interactive knowledge base
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'tube_gpt' not in st.session_state:
        st.session_state.tube_gpt = GeminiTubeGPT()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'video_loaded' not in st.session_state:
        st.session_state.video_loaded = False
    
    if 'api_configured' not in st.session_state:
        st.session_state.api_configured = False
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Key Section
        with st.expander("🔑 Gemini API Setup", expanded=not st.session_state.api_configured):
            gemini_api_key = st.text_input(
                "Enter your Gemini API Key", 
                type="password",
                help="Get your API key from Google AI Studio",
                placeholder="Enter your API key here..."
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Setup", type="primary", use_container_width=True):
                    if gemini_api_key:
                        with st.spinner("Configuring Gemini..."):
                            if st.session_state.tube_gpt.setup_gemini(gemini_api_key):
                                st.session_state.api_configured = True
                                st.success("✅ Configured!")
                                st.rerun()
                            else:
                                st.error("❌ Configuration failed")
                    else:
                        st.error("Please provide your API key")
            
            with col2:
                if st.button("ℹ️ Get Key", use_container_width=True):
                    st.info("Visit: https://makersuite.google.com/app/apikey")
        
        st.divider()
        
        # Video Input Section
        with st.expander("📹 Load Video", expanded=st.session_state.api_configured and not st.session_state.video_loaded):
            video_input = st.text_input(
                "YouTube URL or Video ID",
                placeholder="https://youtube.com/watch?v=... or video_id",
                help="Enter a YouTube URL or just the video ID"
            )
            
            if st.button("📥 Load Video", type="primary", disabled=not st.session_state.api_configured, use_container_width=True):
                if not st.session_state.api_configured:
                    st.error("Please configure Gemini API first")
                elif video_input:
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
                    st.error("Please enter a YouTube URL or Video ID")
        
        # Video Stats
        if st.session_state.video_loaded:
            st.divider()
            st.markdown("### 📊 Video Analytics")
            
            transcript_length = len(st.session_state.tube_gpt.transcript)
            chunk_count = len(st.session_state.tube_gpt.chunks)
            word_count = len(st.session_state.tube_gpt.transcript.split())
            
            st.markdown(f"""
            <div class="stats-dashboard">
                <div class="stat-card">
                    <div class="stat-number">{chunk_count}</div>
                    <div class="stat-label">Chunks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{word_count:,}</div>
                    <div class="stat-label">Words</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{transcript_length//1000}K</div>
                    <div class="stat-label">Characters</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(f"🎬 **Video ID:** `{st.session_state.tube_gpt.video_id}`")
        
        # Controls
        if st.session_state.video_loaded:
            st.divider()
            st.markdown("### 🎛️ Controls")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                if st.button("📋 Summary", use_container_width=True):
                    with st.spinner("Generating summary..."):
                        summary = st.session_state.tube_gpt.generate_summary()
                        st.session_state.chat_history.append(("Generate a summary of this video", summary))
                        st.rerun()
    
    # Main Content Area
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        st.markdown("### 💬 Chat with Video")
        
        # Status Display
        if not st.session_state.api_configured:
            st.markdown("""
            <div class="warning-card">
                <strong>⚠️ Setup Required</strong><br>
                Please configure your Gemini API key in the sidebar to get started.
            </div>
            """, unsafe_allow_html=True)
        elif not st.session_state.video_loaded:
            st.markdown("""
            <div class="info-card">
                <strong>ℹ️ Ready to Load</strong><br>
                Load a YouTube video to start asking questions about its content.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-card">
                <strong>🎬 Video Loaded: {st.session_state.tube_gpt.video_id}</strong><br>
                Ready for questions! Ask anything about the video content.
            </div>
            """, unsafe_allow_html=True)
        
        # Chat Interface
        chat_container = st.container()
        
        with chat_container:
            if st.session_state.chat_history:
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                for i, (question, answer) in enumerate(st.session_state.chat_history):
                    st.markdown(f"""
                    <div class="message-user">
                        <strong>🙋 You:</strong> {question}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="message-bot">
                        <strong>🤖 TubeGPT:</strong> {answer}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Question Input
        if st.session_state.video_loaded and st.session_state.api_configured:
            st.markdown("---")
            with st.form("question_form", clear_on_submit=True):
                question = st.text_input(
                    "💭 Ask a question about the video:",
                    placeholder="What is this video about?",
                    help="Ask anything about the video content - main topics, speakers, key points, etc."
                )
                
                submitted = st.form_submit_button("🚀 Send Message", type="primary", use_container_width=True)
                
                if submitted and question:
                    with st.spinner("🤔 Thinking..."):
                        answer = st.session_state.tube_gpt.answer_question(question)
                        st.session_state.chat_history.append((question, answer))
                        st.rerun()
    
    with col2:
        st.markdown("### ⚡ Quick Actions")
        
        if st.session_state.video_loaded and st.session_state.api_configured:
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
            
            st.markdown('<div class="quick-action-grid">', unsafe_allow_html=True)
            for q in quick_questions:
                if st.button(q, key=f"quick_{hash(q)}", help=f"Ask: {q[2:]}"):
                    with st.spinner("🤔 Processing..."):
                        answer = st.session_state.tube_gpt.answer_question(q[2:])
                        st.session_state.chat_history.append((q[2:], answer))
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div class="modern-card">
                <p style="text-align: center; color: #666; margin: 0;">
                    Configure API and load a video to see quick actions
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Features Section
        st.markdown("### ✨ Features")
        features = [
            "🎥 **YouTube Integration**: Load any video with captions",
            "🧠 **Google Gemini 2.0**: Latest AI model for intelligent responses", 
            "🔍 **Smart Chunking**: Intelligent text processing for better context",
            "💬 **Natural Chat**: Conversational interface for easy interaction",
            "⚡ **Quick Questions**: Pre-built queries for common needs",
            "📊 **Video Analytics**: Statistics about loaded content",
            "🎯 **Contextual Answers**: Responses based only on video content"
        ]
        
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        for feature in features:
            st.markdown(f'<div class="feature-item">{feature}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Professional Footer
    st.markdown("""
    <div class="professional-footer">
        <h3 style="margin-bottom: 1rem;">🎥 TubeGPT</h3>
        <p style="margin-bottom: 0.5rem;">AI-Powered YouTube Video Q&A Assistant</p>
        <p style="margin-bottom: 0.5rem;">Built with ❤️ by <strong>Adhiraj Singh</strong></p>
        <p style="margin-bottom: 0; opacity: 0.8; font-size: 0.9rem;">
            Powered by Google Gemini 2.0 Flash • Transform any YouTube video into an interactive knowledge base
        </p>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            <small>© 2024 TubeGPT. Made with Streamlit & Google Gemini.</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
