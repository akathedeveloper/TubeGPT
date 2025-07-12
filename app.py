import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import re
import json
from typing import List, Dict, Tuple
import hashlib
import time

# Page configuration
st.set_page_config(
    page_title="TubeGPT by Adhiraj Singh",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        border-left: 4px solid #9c27b0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .video-info {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #4caf50;
    }
    
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666;
        border-top: 1px solid #eee;
        margin-top: 3rem;
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        border-radius: 10px;
    }
    
    .quick-question-btn {
        width: 100%;
        margin: 0.25rem 0;
        padding: 0.5rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quick-question-btn:hover {
        background: #f0f0f0;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

class GeminiTubeGPT:
    def __init__(self):
        self.transcript = None
        self.video_id = None
        self.model = None
        self.chunks = []
        
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
        
        # If it's already just an ID
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
            
            # Try to break at sentence boundaries
            if end < len(transcript):
                # Look for sentence endings near the chunk boundary
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
            # Use Gemini to find relevant chunks
            relevance_prompt = f"""
            Given this question: "{question}"
            
            Rate the relevance of each text chunk below on a scale of 1-10, where 10 is most relevant.
            Return only a JSON array of scores, one for each chunk.
            
            Chunks:
            {json.dumps(chunks[:10])}  # Limit to first 10 chunks to avoid token limits
            """
            
            response = self.model.generate_content(relevance_prompt)
            
            try:
                scores = json.loads(response.text)
                if isinstance(scores, list) and len(scores) == len(chunks[:10]):
                    # Pair chunks with scores and sort by relevance
                    chunk_scores = list(zip(chunks[:10], scores))
                    chunk_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    # Return top chunks
                    return [chunk for chunk, score in chunk_scores[:max_chunks]]
            except:
                pass
            
            # Fallback: return first few chunks
            return chunks[:max_chunks]
            
        except Exception as e:
            st.error(f"Error finding relevant chunks: {str(e)}")
            return chunks[:max_chunks]
    
    def answer_question(self, question: str) -> str:
        """Answer question using Gemini with relevant transcript chunks"""
        if not self.transcript or not self.model:
            return "Please load a video first and ensure Gemini is configured."
        
        try:
            # Find relevant chunks
            relevant_chunks = self.find_relevant_chunks(question, self.chunks)
            context = "\n\n".join(relevant_chunks)
            
            # Generate answer using Gemini
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
            # Use first few chunks for summary
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
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎥 TubeGPT</h1>
        <p>AI-Powered YouTube Video Q&A Assistant</p>
        <p><em>by Adhiraj Singh with ❤️</em></p>
        <p><small>Powered by Google Gemini 2.0 Flash</small></p>
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
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key
        st.subheader("🔑 Gemini API Key")
        gemini_api_key = st.text_input(
            "Enter your Gemini API Key", 
            type="password",
            help="Get your API key from Google AI Studio: https://makersuite.google.com/app/apikey"
        )
        
        if st.button("🚀 Setup Gemini", type="primary"):
            if gemini_api_key:
                with st.spinner("Configuring Gemini..."):
                    if st.session_state.tube_gpt.setup_gemini(gemini_api_key):
                        st.session_state.api_configured = True
                        st.success("✅ Gemini configured successfully!")
                    else:
                        st.error("❌ Failed to configure Gemini")
            else:
                st.error("Please provide your Gemini API key")
        
        st.divider()
        
        # Video Input
        st.subheader("📹 Load Video")
        video_input = st.text_input(
            "YouTube URL or Video ID",
            placeholder="https://youtube.com/watch?v=... or video_id",
            help="Enter a YouTube URL or just the video ID"
        )
        
        if st.button("📥 Load Video", type="primary", disabled=not st.session_state.api_configured):
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
                                st.session_state.chat_history = []  # Clear chat history
                                st.success(f"✅ Video loaded! Created {len(st.session_state.tube_gpt.chunks)} chunks.")
                        else:
                            st.error(f"❌ {transcript}")
                else:
                    st.error("❌ Invalid YouTube URL or Video ID")
            else:
                st.error("Please enter a YouTube URL or Video ID")
        
        # Video Stats
        if st.session_state.video_loaded:
            st.divider()
            st.subheader("📊 Video Stats")
            
            transcript_length = len(st.session_state.tube_gpt.transcript)
            chunk_count = len(st.session_state.tube_gpt.chunks)
            word_count = len(st.session_state.tube_gpt.transcript.split())
            
            st.markdown(f"""
            <div class="stats-container">
                <div class="stat-item">
                    <div class="stat-number">{chunk_count}</div>
                    <div class="stat-label">Chunks</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{word_count:,}</div>
                    <div class="stat-label">Words</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{transcript_length:,}</div>
                    <div class="stat-label">Characters</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(f"🎬 **Video ID:** `{st.session_state.tube_gpt.video_id}`")
        
        # Controls
        if st.session_state.video_loaded:
            st.divider()
            st.subheader("🎛️ Controls")
            
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
            
            if st.button("📋 Generate Summary"):
                with st.spinner("Generating summary..."):
                    summary = st.session_state.tube_gpt.generate_summary()
                    st.session_state.chat_history.append(("Generate a summary of this video", summary))
                    st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with Video")
        
        # Status indicators
        if not st.session_state.api_configured:
            st.warning("⚠️ Please configure your Gemini API key in the sidebar to get started.")
        elif not st.session_state.video_loaded:
            st.info("ℹ️ Load a YouTube video to start asking questions about its content.")
        else:
            st.markdown(f"""
            <div class="video-info">
                <strong>🎬 Video Loaded:</strong> {st.session_state.tube_gpt.video_id}<br>
                <strong>📝 Ready for questions!</strong> Ask anything about the video content.
            </div>
            """, unsafe_allow_html=True)
        
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for i, (question, answer) in enumerate(st.session_state.chat_history):
                st.markdown(f"""
                <div class="user-message">
                    <strong>🙋 You:</strong> {question}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="bot-message">
                    <strong>🤖 TubeGPT:</strong> {answer}
                </div>
                """, unsafe_allow_html=True)
        
        # Question input
        if st.session_state.video_loaded and st.session_state.api_configured:
            with st.form("question_form", clear_on_submit=True):
                question = st.text_input(
                    "Ask a question about the video:",
                    placeholder="What is this video about?",
                    help="Ask anything about the video content - main topics, speakers, key points, etc."
                )
                
                submitted = st.form_submit_button("🚀 Send", type="primary")
                
                if submitted and question:
                    with st.spinner("🤔 Thinking..."):
                        answer = st.session_state.tube_gpt.answer_question(question)
                        st.session_state.chat_history.append((question, answer))
                        st.rerun()
    
    with col2:
        st.header("⚡ Quick Actions")
        
        if st.session_state.video_loaded and st.session_state.api_configured:
            quick_questions = [
                "📝 Summarize this video",
                "🎯 What are the main topics discussed?",
                "👥 Who are the speakers or people mentioned?",
                "💡 What are the key takeaways?",
                "📊 Are there any important statistics or numbers?",
                "🔍 What problems are discussed?",
                "💭 What solutions are proposed?",
                "⏰ What timeline or dates are mentioned?",
                "🏢 What companies or organizations are mentioned?",
                "🔗 Are there any recommendations made?"
            ]
            
            st.subheader("💡 Quick Questions")
            for q in quick_questions:
                if st.button(q, key=f"quick_{hash(q)}", help=f"Ask: {q[2:]}"):
                    with st.spinner("🤔 Processing..."):
                        answer = st.session_state.tube_gpt.answer_question(q[2:])  # Remove emoji
                        st.session_state.chat_history.append((q[2:], answer))
                        st.rerun()
        
        else:
            st.info("Configure API and load a video to see quick actions")
        
        # Features
        st.subheader("✨ Features")
        features = [
            "🎥 **YouTube Integration**: Load any video with captions",
            "🧠 **Google Gemini 2.0**: Latest AI model for intelligent responses", 
            "🔍 **Smart Chunking**: Intelligent text processing for better context",
            "💬 **Natural Chat**: Conversational interface for easy interaction",
            "⚡ **Quick Questions**: Pre-built queries for common needs",
            "📊 **Video Analytics**: Statistics about loaded content",
            "🎯 **Contextual Answers**: Responses based only on video content"
        ]
        
        for feature in features:
            st.markdown(f"""
            <div class="feature-card">
                {feature}
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>🎥 <strong>TubeGPT</strong> - AI-Powered YouTube Video Q&A Assistant</p>
        <p>Built with ❤️ by <strong>Adhiraj Singh</strong> using Streamlit & Google Gemini</p>
        <p><em>Transform any YouTube video into an interactive knowledge base!</em></p>
        <p><small>Powered by Google Gemini 2.0 Flash • No OpenAI dependencies</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
