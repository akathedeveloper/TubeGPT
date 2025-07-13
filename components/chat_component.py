import streamlit as st
from utils.constants import QUICK_QUESTIONS

class ChatComponent:
    @staticmethod
    def render_chat_interface():
        """Render main chat interface"""
        st.markdown("### 💬 Chat with Video")
        
        # Chat history
        if st.session_state.chat_history:
            ChatComponent._render_chat_history()
        else:
            ChatComponent._render_empty_chat()
        
        # Chat input
        if st.session_state.video_loaded and st.session_state.api_configured:
            ChatComponent._render_chat_input()
    
    @staticmethod
    def _render_chat_history():
        """Render chat history"""
        st.markdown("""
        <div style="
            background: var(--background-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin: 1rem 0;
            max-height: 500px;
            overflow-y: auto;
        ">
        """, unsafe_allow_html=True)
        
        for question, answer in st.session_state.chat_history:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 20px 20px 5px 20px;
                margin: 0.5rem 0 0.5rem 20%;
                box-shadow: var(--shadow-md);
                animation: slideInRight 0.3s ease;
            ">
                <strong>🙋 You:</strong> {question}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="
                background: var(--background-tertiary);
                color: var(--text-primary);
                padding: 1rem 1.5rem;
                border-radius: 20px 20px 20px 5px;
                margin: 0.5rem 20% 0.5rem 0;
                border-left: 4px solid var(--primary-color);
                box-shadow: var(--shadow-md);
                animation: slideInLeft 0.3s ease;
            ">
                <strong>🤖 TubeGPT:</strong> {answer}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _render_empty_chat():
        """Render empty chat state"""
        st.markdown("""
        <div style="
            background: var(--background-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 3rem;
            margin: 1rem 0;
            text-align: center;
            color: var(--text-muted);
        ">
            <div style="font-size: 4rem; margin-bottom: 1rem;">💬</div>
            <h3 style="color: var(--text-primary); margin-bottom: 0.5rem;">Start a conversation!</h3>
            <p>Ask questions, request summaries, or explore the video content.</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_chat_input():
        """Render chat input form"""
        st.markdown("---")
        with st.form("chat_form", clear_on_submit=True):
            question = st.text_input(
                "💭 Ask a question about the video",
                placeholder="What is this video about?",
                help="Ask anything about the video content"
            )
            
            submitted = st.form_submit_button("🚀 Send Message", use_container_width=True)
            
            if submitted and question:
                with st.spinner("🤔 Thinking..."):
                    answer = st.session_state.tube_gpt.answer_question(question)
                    st.session_state.chat_history.append((question, answer))
                    st.rerun()
    
    @staticmethod
    def render_quick_actions():
        """Render quick action buttons"""
        if st.session_state.video_loaded and st.session_state.api_configured:
            st.markdown("### ⚡ Quick Actions")
            
            for q in QUICK_QUESTIONS:
                if st.button(q, key=f"quick_{hash(q)}", help=f"Ask: {q[2:]}"):
                    with st.spinner("🤔 Processing..."):
                        answer = st.session_state.tube_gpt.answer_question(q[2:])
                        st.session_state.chat_history.append((q[2:], answer))
                        st.rerun()
        else:
            st.markdown("""
            <div class="card">
                <p style="text-align: center; color: var(--text-muted); margin: 0;">
                    Configure API and load a video to see quick actions
                </p>
            </div>
            """, unsafe_allow_html=True)
