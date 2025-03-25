import streamlit as st
import os
import base64

def load_custom_css():
    """Load custom CSS to apply Lato font and color scheme across all pages"""
    streamlit_dir = '.streamlit'
    css_path = os.path.join(streamlit_dir, 'style.css')
    
    if not os.path.exists(streamlit_dir):
        os.makedirs(streamlit_dir)
        
    if not os.path.exists(css_path):
        with open(css_path, 'w') as f:
            f.write('/* Default Streamlit styles */\n')
            
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
def hide_sidebar():
    """Hide the sidebar completely using CSS - use this only for login page"""
    st.markdown("""
    <style>
    /* Hide sidebar completely */
    section[data-testid="stSidebar"] {
        display: none !important;
        width: 0px !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
        visibility: hidden !important;
    }
    
    /* Expand main content area */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 40px !important;
        padding-right: 40px !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

def create_card_container(content, key=None):
    """Creates a styled card container with the given content"""
    st.markdown(
        f"""
        <div class="card-container" id="card-{key}">
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )
    
def create_custom_sidebar():
    """
    Creates a sidebar with user information but without navigation buttons.
    """
    # Only show if user is authenticated
    if not st.session_state.get("authenticated", False):
        return
        
    # Get user role from session state for access control
    user_role = st.session_state.get("user_role", "")
    
    # Use Streamlit's sidebar
    with st.sidebar:
        # Add logo/title
        st.title("Skill Matrix")
        st.markdown("---")
        
        # User information section
        st.markdown("### User Information")
        
        # Get organization name if available
        org_name = st.session_state.get("organization_name", "Not selected")
        
        # Display user information
        st.markdown(f"**Username:** {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.user_role}")
        st.markdown(f"**Organization:** {org_name}")
        
        # Logout button
        st.markdown("---")
        if st.button("Logout", key="nav_logout", use_container_width=True, type="primary"):
            # Set logout in query params and navigate to home
            st.query_params["logout"] = "true"
            st.rerun()

def create_top_navigation():
    """
    Legacy top navigation function, kept for compatibility.
    This function is now empty as we've removed navigation from the UI.
    """
    # No longer doing anything
    pass