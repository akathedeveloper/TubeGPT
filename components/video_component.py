import streamlit as st

class VideoComponent:
    @staticmethod
    def render_video_loader():
        """Render video loading interface using Streamlit components"""
        st.markdown("## 📹 Load a YouTube Video")
        
        with st.container():
            st.info("💡 Enter any YouTube URL or video ID to start analyzing the video content.")
            
            with st.form("video_load", clear_on_submit=False):
                video_input = st.text_input(
                    "YouTube URL or Video ID",
                    placeholder="https://youtube.com/watch?v=... or video_id",
                    help="Paste a YouTube URL or just the video ID"
                )
                
                submitted = st.form_submit_button("📥 Load Video", type="primary", use_container_width=True)
                
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
