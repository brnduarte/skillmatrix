import streamlit as st
import os

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
    """Hide the sidebar completely using CSS"""
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
    
def create_top_navigation():
    """Creates a pure Streamlit-based navigation menu"""
    # Only show if user is authenticated
    if not st.session_state.get("authenticated", False):
        return
        
    user_role = st.session_state.get("user_role", "")
    
    # Hide the default sidebar
    hide_sidebar()
    
    # Add some CSS for basic styling
    st.markdown("""
    <style>
    /* Navigation bar styling */
    div[data-testid="stHorizontalBlock"] > div:first-child div.stMarkdown h3 {
        color: #0f2b3d;
        border-bottom: 2px solid #0f2b3d;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }
    
    /* Main content padding */
    .main .block-container {
        padding-top: 10px;
    }
    
    /* Style for the navigation container */
    .nav-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a container for the navigation
    with st.container():
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        
        # Create columns for navigation sections
        cols = st.columns([3, 1]) 
        
        with cols[0]:
            # Create sub-columns for navigation groups
            if user_role == "admin":
                nav_cols = st.columns(3)
            elif user_role == "manager":
                nav_cols = st.columns(2)
            else:
                nav_cols = st.columns(1)
            
            # Assessment section (for everyone)
            with nav_cols[0]:
                st.markdown("### Assessment")
                st.markdown("• [Home](./) ")
                st.markdown("• [Self-Assessment](./02_Employee_Assessment)")
                st.markdown("• [My Performance](./03_Individual_Performance)")
            
            # Manager section (for managers and admins)
            if user_role in ["manager", "admin"]:
                with nav_cols[1]:
                    st.markdown("### Manager")
                    st.markdown("• [Team Dashboard](./04_Team_Dashboard)")
                    st.markdown("• [Export Reports](./05_Export_Reports)")
            
            # Settings section (admin only)
            if user_role == "admin":
                with nav_cols[2]:
                    st.markdown("### Settings")
                    st.markdown("• [Framework Setup](./01_Framework_Setup)")
                    st.markdown("• [Organizations](./06_Organization_Management)")
                    st.markdown("• [User Management](./07_User_Management)")
        
        # User info and logout
        with cols[1]:
            st.write(f"**User:** {st.session_state.username}")
            st.write(f"**Role:** {st.session_state.user_role}")
            
            if st.button("Logout", type="primary"):
                # Clear session state and reinitialize
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                from utils import initialize_session_state
                initialize_session_state()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)