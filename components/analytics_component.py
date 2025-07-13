import streamlit as st

class AnalyticsComponent:
    @staticmethod
    def render_video_stats():
        """Render video statistics"""
        if st.session_state.video_loaded:
            st.markdown("### 📊 Video Analytics")
            
            transcript_length = len(st.session_state.tube_gpt.transcript)
            chunk_count = len(st.session_state.tube_gpt.chunks)
            word_count = len(st.session_state.tube_gpt.transcript.split())
            
            # Stats grid
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Chunks", chunk_count)
            
            with col2:
                st.metric("Words", f"{word_count:,}")
            
            with col3:
                st.metric("Characters", f"{transcript_length//1000}K")
    
    @staticmethod
    def render_detailed_analytics():
        """Render detailed analytics page"""
        if not st.session_state.video_loaded:
            st.info("Load a video to see detailed analytics")
            return
        
        transcript_length = len(st.session_state.tube_gpt.transcript)
        chunk_count = len(st.session_state.tube_gpt.chunks)
        word_count = len(st.session_state.tube_gpt.transcript.split())
        chat_count = len(st.session_state.chat_history)
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Words", f"{word_count:,}")
        
        with col2:
            st.metric("Text Chunks", chunk_count)
        
        with col3:
            st.metric("Characters", f"{transcript_length:,}")
        
        with col4:
            st.metric("Chat Messages", chat_count)
        
        st.markdown("---")
        
        # Detailed breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Content Analysis")
            st.info(f"**Video ID:** {st.session_state.tube_gpt.video_id}")
            st.info(f"**Average words per chunk:** {word_count // chunk_count if chunk_count > 0 else 0}")
            st.info(f"**Processing time:** Instant")
        
        with col2:
            st.markdown("### 💬 Chat Statistics")
            if chat_count > 0:
                avg_response_length = sum(len(answer) for _, answer in st.session_state.chat_history) // chat_count
                st.info(f"**Total conversations:** {chat_count}")
                st.info(f"**Average response length:** {avg_response_length} characters")
            else:
                st.info("No chat history yet")
