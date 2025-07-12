import streamlit as st
import os
from utils import YouTubeProcessor, GeminiHandler, VectorStoreManager
from config import Config
import time

# Page configuration
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout=Config.LAYOUT,
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # If CSS file doesn't exist, continue without custom styling
        pass

# Initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "video_processed" not in st.session_state:
        st.session_state.video_processed = False
    if "current_video_id" not in st.session_state:
        st.session_state.current_video_id = None

# Main header
def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>🎥 TubeGPT</h1>
        <p>Your AI-Powered YouTube Video Assistant</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🚀 How to Use TubeGPT")
        st.markdown("""
        1. **Enter YouTube URL** in the input field
        2. **Click Process Video** to analyze the transcript
        3. **Ask questions** about the video content
        4. **Get AI-powered answers** based on the transcript
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Video Statistics")
        if st.session_state.video_processed and hasattr(st.session_state, 'video_metadata'):
            metadata = st.session_state.video_metadata
            st.metric("Video ID", st.session_state.current_video_id)
            st.metric("Total Chunks", metadata.get('total_chunks', 'N/A'))
            st.metric("Transcript Length", f"{metadata.get('total_length', 0):,} chars")
            st.metric("Language", metadata.get('language', 'Unknown'))
            st.metric("Method", metadata.get('method', 'Unknown'))
        else:
            st.info("Process a video to see statistics")
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        temperature = st.slider("Response Creativity", 0.0, 1.0, 0.7, 0.1)
        max_results = st.slider("Search Results", 1, 10, 4)
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

# Video processing section
def render_video_processor():
    st.markdown("### 📹 Video Processing")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        video_url = st.text_input(
            "Enter YouTube Video URL:",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste any YouTube video URL here - the system will automatically find the best available transcript"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        process_button = st.button("🔄 Process Video", type="primary")
    
    if process_button and video_url:
        process_video(video_url)

def process_video(video_url):
    """Enhanced video processing with automatic fallbacks"""
    
    # Initialize processors
    youtube_processor = YouTubeProcessor(Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
    gemini_handler = GeminiHandler(Config.GOOGLE_API_KEY, Config.GEMINI_MODEL)
    
    # Extract video ID
    video_id = youtube_processor.extract_video_id(video_url)
    
    if not video_id:
        st.error("❌ Invalid YouTube URL. Please check the URL and try again.")
        return
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Analyze available transcripts
        status_text.text("🔍 Analyzing available transcripts...")
        progress_bar.progress(20)
        
        available_transcripts = youtube_processor.get_all_available_transcripts(video_id)
        
        if not available_transcripts:
            st.error("❌ No transcripts available for this video. The video may be private, restricted, or have no captions.")
            return
        
        # Display available transcript info
        st.info(f"📋 Found {len(available_transcripts)} transcript(s) available")
        
        # Step 2: Get best available transcript
        status_text.text("📥 Fetching optimal transcript...")
        progress_bar.progress(40)
        
        transcript, metadata = youtube_processor.get_transcript(video_id)
        
        if not transcript:
            st.error(f"❌ Failed to fetch transcript: {metadata.get('error', 'Unknown error')}")
            return
        
        # Display transcript info
        lang_info = f"{metadata.get('language', 'Unknown')} ({metadata.get('language_code', 'N/A')})"
        method_info = metadata.get('method', 'unknown')
        is_generated = metadata.get('is_generated', False)
        
        st.success(f"✅ Successfully fetched transcript in {lang_info}")
        st.info(f"📊 Method: {method_info} | Generated: {'Yes' if is_generated else 'No'} | Length: {len(transcript):,} chars")
        
        # Step 3: Process transcript
        status_text.text("✂️ Processing transcript into chunks...")
        progress_bar.progress(60)
        
        documents = youtube_processor.process_transcript(transcript, video_id)
        
        if not documents:
            st.error("❌ Failed to process transcript into chunks.")
            return
        
        # Step 4: Create vector store
        status_text.text("🔍 Creating searchable index...")
        progress_bar.progress(80)
        
        embeddings = gemini_handler.get_embeddings()
        vector_manager = VectorStoreManager(embeddings)
        
        if vector_manager.create_vector_store(documents):
            # Step 5: Complete
            status_text.text("✅ Video processed successfully!")
            progress_bar.progress(100)
            
            # Update session state
            st.session_state.vector_store = vector_manager
            st.session_state.gemini_handler = gemini_handler
            st.session_state.video_processed = True
            st.session_state.current_video_id = video_id
            st.session_state.video_metadata = metadata
            
            # Show success message with details
            st.success(f"🎉 Video processed successfully! Created {len(documents)} searchable chunks.")
            
            # Display processing details
            with st.expander("📊 Processing Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Language", metadata.get('language', 'Unknown'))
                    st.metric("Method", metadata.get('method', 'Unknown'))
                with col2:
                    st.metric("Chunks Created", len(documents))
                    st.metric("Generated", "Yes" if metadata.get('is_generated') else "No")
            
        else:
            st.error("❌ Failed to create searchable index. Please try again.")
            
    except Exception as e:
        st.error(f"❌ Error processing video: {str(e)}")
    
    finally:
        progress_bar.empty()
        status_text.empty()

# Chat interface
def render_chat_interface():
    st.markdown("### 💬 Chat with Your Video")
    
    if not st.session_state.video_processed:
        st.info("👆 Please process a YouTube video first to start chatting!")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about the video..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                response = generate_response(prompt)
                st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})

def generate_response(query):
    """Generate response using RAG pipeline"""
    try:
        # Retrieve relevant documents
        retrieved_docs = st.session_state.vector_store.similarity_search(query, k=4)
        
        if not retrieved_docs:
            return "I couldn't find relevant information in the video transcript to answer your question."
        
        # Prepare context
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Generate response
        response = st.session_state.gemini_handler.generate_response(query, context)
        
        return response
        
    except Exception as e:
        return f"Sorry, I encountered an error while processing your question: {str(e)}"

# Main application
def main():
    # Load CSS and initialize
    load_css()
    initialize_session_state()
    
    # Render components
    render_header()
    render_sidebar()
    render_video_processor()
    
    st.markdown("---")
    
    render_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 Built with ❤️ by Adhiraj Singh | 
        <a href="https://github.com/akathedeveloper/TubeGPT" target="_blank">View Source</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
