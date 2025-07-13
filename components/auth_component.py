import streamlit as st

class AuthComponent:
    @staticmethod
    def render_api_setup():
        """Render API setup interface"""
        st.markdown("""
        <div style="max-width: 600px; margin: 2rem auto; padding: 0 2rem;">
            <div class="card">
                <div class="card-header">
                    <span class="card-icon">🔑</span>
                    <h2 class="card-title">Setup Your API Key</h2>
                </div>
                <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                    To get started, you'll need a Google Gemini API key. It's free and takes just a minute to set up.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("api_setup", clear_on_submit=False):
            api_key = st.text_input(
                "🔑 Enter your Gemini API Key",
                type="password",
                placeholder="Enter your API key here...",
                help="Get your free API key from Google AI Studio"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("🚀 Setup API", use_container_width=True)
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
    
    @staticmethod
    def render_settings():
        """Render settings page"""
        st.markdown("## 🔑 API Configuration")
        
        if st.session_state.api_configured:
            st.success("✅ Gemini API is configured")
            if st.button("🔄 Reconfigure API"):
                st.session_state.api_configured = False
                st.rerun()
        else:
            AuthComponent.render_api_setup()
        
        st.markdown("---")
        st.markdown("## 🎛️ Application Settings")
        
        # Theme settings
        theme = st.selectbox("Theme", ["Dark", "Light"], index=0)
        
        # Language settings
        language = st.selectbox("Language", ["English", "Spanish", "French"], index=0)
        
        # Notification settings
        notifications = st.checkbox("Enable notifications", value=True)
        
        if st.button("💾 Save Settings"):
            st.success("Settings saved successfully!")
