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
    
    # Add fixed navigation style with better spacing and layout
    st.markdown("""
    <style>
    /* Add padding to main content to make space for fixed top navigation */
    .main .block-container {
        padding-top: 110px !important;
    }
    
    /* Fixed navigation container */
    .navbar-fixed {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: #0f2b3d;
        z-index: 9999;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        padding: 15px 20px;
    }
    
    /* Flexbox container for navigation */
    .navbar-container {
        display: flex;
        justify-content: space-between;
        color: white;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Menu groups container */
    .navbar-menu {
        display: flex;
        gap: 40px;
    }
    
    /* Individual menu group */
    .navbar-group {
        min-width: 140px;
    }
    
    /* Group headings */
    .navbar-heading {
        color: #f5f0d2;
        text-transform: uppercase;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 8px;
        padding-bottom: 4px;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Navigation links */
    .navbar-link {
        display: block;
        color: white;
        text-decoration: none;
        margin-bottom: 5px;
        font-size: 14px;
    }
    
    .navbar-link:hover {
        color: #f5f0d2;
        text-decoration: underline;
    }
    
    /* User information section */
    .navbar-user {
        text-align: right;
        min-width: 200px;
    }
    
    /* User detail text */
    .user-detail {
        margin-bottom: 8px;
        font-size: 14px;
    }
    
    /* Logout button */
    .logout-button {
        background-color: #d13c35;
        color: white;
        padding: 5px 15px;
        border-radius: 4px;
        text-decoration: none;
        font-size: 14px;
        display: inline-block;
        border: none;
    }
    
    .logout-button:hover {
        background-color: #b73229;
        text-decoration: none;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Build the navigation HTML
    html = """
    <div class="navbar-fixed">
        <div class="navbar-container">
            <div class="navbar-menu">
    """
    
    # Assessment section (available to all)
    html += """
                <div class="navbar-group">
                    <div class="navbar-heading">Assessment</div>
                    <a href="./" class="navbar-link">Home</a>
                    <a href="./02_Employee_Assessment" class="navbar-link">Self-Assessment</a>
                    <a href="./03_Individual_Performance" class="navbar-link">My Performance</a>
                </div>
    """
    
    # Manager section (conditional)
    if user_role in ["manager", "admin"]:
        html += """
                <div class="navbar-group">
                    <div class="navbar-heading">Manager</div>
                    <a href="./04_Team_Dashboard" class="navbar-link">Team Dashboard</a>
                    <a href="./05_Export_Reports" class="navbar-link">Export Reports</a>
                </div>
        """
    
    # Settings section (conditional)
    if user_role == "admin":
        html += """
                <div class="navbar-group">
                    <div class="navbar-heading">Settings</div>
                    <a href="./01_Framework_Setup" class="navbar-link">Framework Setup</a>
                    <a href="./06_Organization_Management" class="navbar-link">Organizations</a>
                    <a href="./07_User_Management" class="navbar-link">User Management</a>
                </div>
        """
    
    # Close the menu div and add user info
    html += """
            </div>
            <div class="navbar-user">
                <div class="user-detail"><strong>User:</strong> """ + st.session_state.username + """</div>
                <div class="user-detail"><strong>Role:</strong> """ + st.session_state.user_role + """</div>
                <a href="./?logout=true" class="logout-button">Logout</a>
            </div>
        </div>
    </div>
    """
    
    # Render the navigation
    st.markdown(html, unsafe_allow_html=True)