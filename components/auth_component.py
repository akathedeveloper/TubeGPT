import streamlit as st

class AuthComponent:
    @staticmethod
    def render_api_setup():
        """Render API setup interface"""
        st.info("💡 To get started, you'll need a Google Gemini API key. It's free and takes just a minute to set up.")
        
        with st.form("api_setup_form", clear_on_submit=False):
            api_key = st.text_input(
                "Enter your Gemini API Key",
                type="password",
                placeholder="Enter your API key here...",
                help="Get your free API key from Google AI Studio"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("🚀 Setup API", type="primary", use_container_width=True)
            with col2:
                if st.form_submit_button("ℹ️ Get API Key", use_container_width=True):
                    st.info("Visit: https://makersuite.google.com/app/apikey")
            
            if submitted and api_key:
                with st.spinner("Configuring Gemini..."):
                    if st.session_state.tube_gpt.setup_gemini(api_key):
                        st.session_state.api_configured = True
                        st.success("✅ API configured successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to configure API. Please check your key.")
