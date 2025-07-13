import streamlit as st
from utils.constants import QUICK_QUESTIONS

class ChatComponent:
    @staticmethod
    def render_chat_interface():
        """Render main chat interface using Streamlit components"""
        st.markdown("### 💬 Chat with Video")
        
        # Chat history container
        if st.session_state.chat_history:
            with st.container():
                for i, (question, answer) in enumerate(st.session_state.chat_history):
                    # User message
                    with st.chat_message("user"):
                        st.write(question)
                    
                    # Bot message
                    with st.chat_message("assistant"):
                        st.write(answer)
        else:
            st.info("💡 Start a conversation! Ask questions about the video content.")
        
        # Chat input
        if st.session_state.video_loaded and st.session_state.api_configured:
            ChatComponent._render_chat_input()
    
    @staticmethod
    def _render_chat_input():
        """Render chat input form"""
        with st.form("chat_form", clear_on_submit=True):
            question = st.text_input(
                "Ask a question about the video",
                placeholder="What is this video about?",
                help="Ask anything about the video content"
            )
            
            submitted = st.form_submit_button("🚀 Send Message", type="primary", use_container_width=True)
            
            if submitted and question:
                with st.spinner("🤔 Thinking..."):
                    answer = st.session_state.tube_gpt.answer_question(question)
                    st.session_state.chat_history.append((question, answer))
                    st.rerun()
    
    @staticmethod
    def render_quick_actions():
        """Render quick action buttons using Streamlit components"""
        if st.session_state.video_loaded and st.session_state.api_configured:
            st.markdown("### ⚡ Quick Actions")
            
            # Create two columns for better layout
            col1, col2 = st.columns(2)
            
            for i, q in enumerate(QUICK_QUESTIONS):
                col = col1 if i % 2 == 0 else col2
                
                with col:
                    if st.button(q, key=f"quick_{i}", use_container_width=True):
                        with st.spinner("🤔 Processing..."):
                            answer = st.session_state.tube_gpt.answer_question(q[2:])
                            st.session_state.chat_history.append((q[2:], answer))
                            st.rerun()
        else:
            st.info("💡 Configure API and load a video to see quick actions")
