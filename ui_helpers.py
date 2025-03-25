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
    Creates a navigation sidebar using Streamlit native components.
    Manages page navigation while preserving session state.
    """
    # Only show if user is authenticated
    if not st.session_state.get("authenticated", False):
        return
        
    # Get user role from session state for access control
    user_role = st.session_state.get("user_role", "")
    
    # Get current page path from session state
    current_path = st.session_state.get("current_page", "")
    
    # Use Streamlit's sidebar
    with st.sidebar:
        # Add logo/title
        st.title("Skill Matrix")
        st.markdown("---")
        
        # Main navigation section
        st.markdown("### Main")
        if st.button("Home", key="nav_home", use_container_width=True, 
                    type="primary" if current_path == "./" else "secondary"):
            # Navigate to home page
            st.switch_page("app.py")
        
        # Assessment section
        st.markdown("---")
        st.markdown("### Assessment")
        
        if st.button("Self Assessment", key="nav_self_assess", use_container_width=True,
                    type="primary" if current_path == "./pages/02_Employee_Assessment" else "secondary"):
            st.switch_page("pages/02_Employee_Assessment.py")
            
        if st.button("My Performance", key="nav_my_perf", use_container_width=True,
                    type="primary" if current_path == "./pages/03_Individual_Performance" else "secondary"):
            st.switch_page("pages/03_Individual_Performance.py")
        
        # Management section (for managers and admins)
        if user_role in ["manager", "admin"]:
            st.markdown("---")
            st.markdown("### Management")
            
            if st.button("Team Dashboard", key="nav_team", use_container_width=True,
                        type="primary" if current_path == "./pages/04_Team_Dashboard" else "secondary"):
                st.switch_page("pages/04_Team_Dashboard.py")
                
            if st.button("Export Reports", key="nav_export", use_container_width=True,
                        type="primary" if current_path == "./pages/05_Export_Reports" else "secondary"):
                st.switch_page("pages/05_Export_Reports.py")
        
        # Admin section (for admins only)
        if user_role == "admin":
            st.markdown("---")
            st.markdown("### Administration")
            
            if st.button("Framework Setup", key="nav_framework", use_container_width=True,
                        type="primary" if current_path == "./pages/01_Framework_Setup" else "secondary"):
                st.switch_page("pages/01_Framework_Setup.py")
                
            if st.button("Organizations", key="nav_orgs", use_container_width=True,
                        type="primary" if current_path == "./pages/06_Organization_Management" else "secondary"):
                st.switch_page("pages/06_Organization_Management.py")
                
            if st.button("User Management", key="nav_users", use_container_width=True,
                        type="primary" if current_path == "./pages/07_User_Management" else "secondary"):
                st.switch_page("pages/07_User_Management.py")
        
        # User info and logout section
        st.markdown("---")
        st.markdown(f"**User:** {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.user_role}")
        
        if st.button("Logout", key="nav_logout", use_container_width=True, type="primary"):
            # Set logout in query params and navigate to home
            st.query_params["logout"] = "true"
            st.rerun()

def create_top_navigation():
    """
    Legacy top navigation function, kept for compatibility.
    Using the custom sidebar navigation instead.
    """
    # Delegate to the custom sidebar navigation
    create_custom_sidebar()