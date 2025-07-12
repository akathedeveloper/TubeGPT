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
    if "video_metadata" not in st.session_state:
        st.session_state.video_metadata = {}

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
        1. **Enter YouTube Video ID** (11 characters)
        2. **Click Process Video** to analyze the transcript
        3. **Ask questions** about the video content
        4. **Get AI-powered answers** based on the transcript
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Current Video")
        if st.session_state.video_processed and st.session_state.video_metadata:
            metadata = st.session_state.video_metadata
            video_id = st.session_state.current_video_id
            
            # Display video info
            st.metric("Video ID", video_id)
            st.metric("Transcript Length", f"{metadata.get('total_length', 0):,} chars")
            st.metric("Total Segments", metadata.get('total_segments', 'N/A'))
            st.metric("Duration", f"{metadata.get('duration', 0):.1f}s")
            
            # YouTube link
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            st.markdown(f"[🔗 Watch on YouTube]({youtube_url})")
            
            # Copy video ID
            st.code(video_id, language=None)
        else:
            st.info("No video processed yet")
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        chunk_type = st.selectbox(
            "Chunking Method",
            ["Text-based", "Time-based"],
            help="Choose how to split the transcript"
        )
        
        if chunk_type == "Time-based":
            chunk_duration = st.slider("Chunk Duration (seconds)", 30, 180, 60)
        
        temperature = st.slider("Response Creativity", 0.0, 1.0, 0.7, 0.1)
        max_results = st.slider("Search Results", 1, 10, 4)
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 Sample Video IDs")
        st.markdown("""
        - `bMt47wvK6u0` (Your working example)
        - `dQw4w9WgXcQ` (Rick Roll)
        - `9bZkp7q19f0` (Gangnam Style)
        """)
        
        if st.button("🚀 Test with Sample"):
            process_video_input("bMt47wvK6u0")

# Video processing section
def render_video_processor():
    st.markdown("### 📹 Video Processing")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        video_input = st.text_input(
            "Enter YouTube Video ID:",
            placeholder="bMt47wvK6u0",
            help="Enter the 11-character YouTube video ID (e.g., bMt47wvK6u0)"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        process_button = st.button("🔄 Process Video", type="primary")
    
    # Processing options
    with st.expander("⚙️ Processing Options"):
        col1, col2 = st.columns(2)
        with col1:
            chunk_method = st.radio(
                "Chunking Method:",
                ["Text-based chunks", "Time-based chunks"],
                help="Choose how to split the transcript for processing"
            )
        with col2:
            if chunk_method == "Time-based chunks":
                time_chunk_duration = st.slider("Time chunk duration (seconds)", 30, 180, 60)
            else:
                time_chunk_duration = 60
    
    if process_button and video_input:
        chunk_type = "time" if chunk_method == "Time-based chunks" else "text"
        process_video_input(video_input, chunk_type, time_chunk_duration)
    
    # Examples section
    st.markdown("### 💡 How to Find Video ID")
    st.info("""
    **From YouTube URL:** `https://www.youtube.com/watch?v=bMt47wvK6u0`
    
    The Video ID is: `bMt47wvK6u0` (the part after `v=`)
    """)

def process_video_input(video_input, chunk_type="text", chunk_duration=60):
    """Process video input and create vector store"""
    
    # Initialize processors
    youtube_processor = YouTubeProcessor(Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
    gemini_handler = GeminiHandler(Config.GOOGLE_API_KEY, Config.GEMINI_MODEL)
    
    # Extract or validate video ID
    video_id = youtube_processor.extract_video_id(video_input)
    
    if not video_id:
        st.error("❌ Invalid input. Please enter a valid 11-character YouTube video ID.")
        st.info("Example: `bMt47wvK6u0`")
        return
    
    # Show the video ID being processed
    st.markdown(f"""
    <div class="video-id-display">
        🎯 Processing Video ID: <strong>{video_id}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Get transcript
        status_text.text("📥 Fetching video transcript...")
        progress_bar.progress(20)
        
        if chunk_type == "time":
            # Get timestamped data for time-based chunking
            transcript_data, metadata = youtube_processor.get_transcript_with_timestamps(video_id)
            if not transcript_data:
                st.error(f"❌ {metadata.get('error', 'Failed to fetch timestamped transcript')}")
                return
            
            # Also get text for display
            transcript_text = youtube_processor.process_transcript_data(transcript_data)
        else:
            # Get regular transcript
            transcript_text, metadata = youtube_processor.get_transcript(video_id)
            if not transcript_text:
                st.error(f"❌ {metadata.get('error', 'Failed to fetch transcript')}")
                return
            transcript_data = None
        
        # Step 2: Process transcript
        status_text.text("✂️ Processing transcript into chunks...")
        progress_bar.progress(50)
        
        if chunk_type == "time" and transcript_data:
            documents = youtube_processor.create_timestamped_chunks(transcript_data, video_id, chunk_duration)
        else:
            documents = youtube_processor.process_transcript(transcript_text, video_id)
        
        if not documents:
            st.error("❌ Failed to process transcript into chunks.")
            return
        
        # Step 3: Create vector store
        status_text.text("🔍 Creating searchable index...")
        progress_bar.progress(75)
        
        embeddings = gemini_handler.get_embeddings()
        vector_manager = VectorStoreManager(embeddings)
        
        if vector_manager.create_vector_store(documents):
            # Step 4: Complete
            status_text.text("✅ Video processed successfully!")
            progress_bar.progress(100)
            
            # Update session state
            st.session_state.vector_store = vector_manager
            st.session_state.gemini_handler = gemini_handler
            st.session_state.video_processed = True
            st.session_state.current_video_id = video_id
            st.session_state.video_metadata = metadata
            
            # Show success message
            st.success(f"🎉 Video processed successfully! Created {len(documents)} searchable chunks using {chunk_type}-based chunking.")
            
            # Display processing details
            with st.expander("📊 Processing Details", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Video ID", video_id)
                    st.metric("Method", metadata.get('method', 'Unknown'))
                with col2:
                    st.metric("Transcript Length", f"{metadata.get('total_length', 0):,} chars")
                    st.metric("Chunks Created", len(documents))
                with col3:
                    st.metric("Total Segments", metadata.get('total_segments', 'N/A'))
                    if metadata.get('duration'):
                        st.metric("Duration", f"{metadata.get('duration', 0):.1f}s")
                
                # Show YouTube link
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                st.markdown(f"**YouTube Link:** [Watch Video]({youtube_url})")
                
                # Show sample transcript
                if transcript_text:
                    st.markdown("**Sample Transcript:**")
                    st.text(transcript_text[:500] + "..." if len(transcript_text) > 500 else transcript_text)
            
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
    
    # Display current video info
    if st.session_state.current_video_id:
        st.markdown(f"**Currently chatting about:** `{st.session_state.current_video_id}`")
    
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
