import streamlit as st

class VideoComponent:
    @staticmethod
    def render_video_loader():
        """Render video loading interface"""
        st.markdown("""
        <div style="max-width: 600px; margin: 2rem auto; padding: 0 2rem;">
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">📹</span>
                    <h2 class="card-title">Load a YouTube Video</h2>
                </div>
                <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                    Enter any YouTube URL or video ID to start analyzing the video content.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("video_load", clear_on_submit=False):
            video_input = st.text_input(
                "📹 YouTube URL or Video ID",
                placeholder="https://youtube.com/watch?v=... or video_id",
                help="Paste a YouTube URL or just the video ID"
            )
            
            submitted = st.form_submit_button("📥 Load Video", use_container_width=True)
            
            if submitted and video_input:
                VideoComponent._process_video(video_input)
    
    @staticmethod
    def _process_video(video_input):
        """Process video input"""
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
    
    @staticmethod
    def render_video_info():
        """Render video information"""
        if st.session_state.video_loaded:
            st.markdown(f"""
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">🎬</span>
                    <h3 class="card-title">Video Information</h3>
                </div>
                <p><strong>Video ID:</strong> {st.session_state.tube_gpt.video_id}</p>
                <p><strong>Status:</strong> <span style="color: var(--success-color);">✅ Loaded</span></p>
            </div>
            """, unsafe_allow_html=True)
