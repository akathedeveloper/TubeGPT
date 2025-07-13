import streamlit as st
from utils.constants import QUICK_QUESTIONS

class ChatComponent:
    @staticmethod
    def render_chat_interface():
        """Render main chat interface using Streamlit components"""
        st.markdown("### 💬 Chat with Video")
        
        # Chat history container with better styling
        chat_container = st.container()
        
        with chat_container:
            if st.session_state.chat_history:
                # Create a scrollable chat area
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
        st.markdown("---")
        
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
        """Render improved quick action buttons"""
        if st.session_state.video_loaded and st.session_state.api_configured:
            st.markdown("### ⚡ Quick Actions")
            
            # Better organized quick actions in a grid
            questions_per_row = 2
            rows = [QUICK_QUESTIONS[i:i + questions_per_row] for i in range(0, len(QUICK_QUESTIONS), questions_per_row)]
            
            for row_idx, row in enumerate(rows):
                cols = st.columns(len(row))
                
                for col_idx, question in enumerate(row):
                    with cols[col_idx]:
                        # Clean button text (remove emoji for cleaner look)
                        clean_text = question[2:].strip()  # Remove emoji and extra spaces
                        button_key = f"quick_{row_idx}_{col_idx}"
                        
                        if st.button(
                            f"{question[:2]} {clean_text}", 
                            key=button_key, 
                            use_container_width=True,
                            help=f"Ask: {clean_text}"
                        ):
                            with st.spinner("🤔 Processing..."):
                                answer = st.session_state.tube_gpt.answer_question(clean_text)
                                st.session_state.chat_history.append((clean_text, answer))
                                st.rerun()
        else:
            st.info("💡 Configure API and load a video to see quick actions")
