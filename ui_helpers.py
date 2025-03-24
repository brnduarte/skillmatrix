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
    """Creates a simple navigation menu directly in the main container"""
    # Only show if user is authenticated
    if not st.session_state.get("authenticated", False):
        return
        
    user_role = st.session_state.get("user_role", "")
    
    # Hide the default sidebar
    hide_sidebar()
    
    # Create a custom CSS for the navigation
    st.markdown("""
    <style>
    /* Navigation container */
    .navigation-container {
        background-color: #0f2b3d;
        color: white;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 0;
        display: flex;
        justify-content: space-between;
    }
    
    /* Navigation menu section */
    .nav-menu {
        display: flex;
        gap: 40px;
    }
    
    /* Group container */
    .nav-group {
        display: flex;
        flex-direction: column;
    }
    
    /* Group titles */
    .group-title {
        color: #f5f0d2;
        font-size: 16px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        padding-bottom: 5px;
    }
    
    /* Links */
    .nav-link {
        color: white;
        text-decoration: none;
        margin-bottom: 5px;
        display: block;
    }
    
    .nav-link:hover {
        color: #f5f0d2;
        text-decoration: underline;
    }
    
    /* User info */
    .user-info {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        justify-content: center;
        min-width: 200px;
    }
    
    .user-text {
        color: white;
        margin-bottom: 5px;
    }
    
    .logout-button {
        background-color: #d13c35;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
    }
    
    .logout-button:hover {
        background-color: #b73229;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create HTML for the navigation
    html = """
    <div class="navigation-container">
        <div class="nav-menu">
    """
    
    # Assessment group (available to all)
    html += """
            <div class="nav-group">
                <div class="group-title">Assessment</div>
                <a href="./" class="nav-link">Home</a>
                <a href="./02_Employee_Assessment" class="nav-link">Self-Assessment</a>
                <a href="./03_Individual_Performance" class="nav-link">My Performance</a>
            </div>
    """
    
    # Manager group (conditional)
    if user_role in ["manager", "admin"]:
        html += """
            <div class="nav-group">
                <div class="group-title">Manager</div>
                <a href="./04_Team_Dashboard" class="nav-link">Team Dashboard</a>
                <a href="./05_Export_Reports" class="nav-link">Export Reports</a>
            </div>
        """
    
    # Settings group (conditional)
    if user_role == "admin":
        html += """
            <div class="nav-group">
                <div class="group-title">Settings</div>
                <a href="./01_Framework_Setup" class="nav-link">Framework Setup</a>
                <a href="./06_Organization_Management" class="nav-link">Organizations</a>
                <a href="./07_User_Management" class="nav-link">User Management</a>
            </div>
        """
    
    # Close nav-menu div and add user info
    html += """
        </div>
        <div class="user-info">
            <div class="user-text"><strong>User:</strong> """ + st.session_state.username + """</div>
            <div class="user-text"><strong>Role:</strong> """ + st.session_state.user_role + """</div>
            <a href="./?logout=true" class="logout-button">Logout</a>
        </div>
    </div>
    """
    
    # Render the navigation
    st.markdown(html, unsafe_allow_html=True)
    
    # Add margin below navigation
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)