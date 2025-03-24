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
    """Creates a top navigation bar with expandable/collapsible sections"""
    # Only show if user is authenticated
    if not st.session_state.get("authenticated", False):
        return
        
    user_role = st.session_state.get("user_role", "")
    
    # Hide the default sidebar
    hide_sidebar()
    
    # Initialize session state for menu expansion if not exists
    if "nav_assessment_expanded" not in st.session_state:
        st.session_state.nav_assessment_expanded = False
    if "nav_manager_expanded" not in st.session_state:
        st.session_state.nav_manager_expanded = False
    if "nav_settings_expanded" not in st.session_state:
        st.session_state.nav_settings_expanded = False
    
    # Add CSS for navigation styling
    st.markdown("""
    <style>
    /* Fixed top navigation */
    div.fixed-topbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        background-color: #0f2b3d;
        color: white;
        padding: 10px 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Main content padding to accommodate fixed navbar */
    .main .block-container {
        padding-top: 110px !important;
    }
    
    /* Navigation menu item */
    .nav-item {
        display: inline-block;
        margin-right: 25px;
        position: relative;
    }
    
    /* Navigation menu header */
    .nav-header {
        color: white;
        font-weight: bold;
        cursor: pointer;
        padding: 8px 12px;
        border-radius: 4px;
        display: inline-block;
    }
    
    .nav-header:hover {
        background-color: rgba(255,255,255,0.1);
    }
    
    /* Dropdown content */
    .dropdown-content {
        display: none;
        position: absolute;
        background-color: white;
        min-width: 180px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        z-index: 1000;
        border-radius: 4px;
        padding: 8px 0;
        margin-top: 5px;
    }
    
    /* Show dropdown when parent is hovered */
    .nav-item:hover .dropdown-content {
        display: block;
    }
    
    /* Dropdown links */
    .dropdown-link {
        color: #333;
        padding: 8px 16px;
        text-decoration: none;
        display: block;
    }
    
    .dropdown-link:hover {
        background-color: #f5f5f5;
    }
    
    /* User info section */
    .user-section {
        float: right;
        text-align: right;
    }
    
    .user-info {
        display: inline-block;
        margin-right: 15px;
        color: white;
    }
    
    /* Logout button */
    .logout-btn {
        background-color: #d13c35;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 4px;
        cursor: pointer;
        text-decoration: none;
        font-size: 14px;
    }
    
    .logout-btn:hover {
        background-color: #b73229;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create top navigation bar with dropdowns using HTML
    html = """
    <div class="fixed-topbar">
        <div style="max-width: 1200px; margin: 0 auto;">
    """
    
    # Assessment dropdown (available to all users)
    html += """
            <div class="nav-item">
                <div class="nav-header">Assessment ▾</div>
                <div class="dropdown-content">
                    <a href="./" class="dropdown-link">Home</a>
                    <a href="./02_Employee_Assessment" class="dropdown-link">Self-Assessment</a>
                    <a href="./03_Individual_Performance" class="dropdown-link">My Performance</a>
                </div>
            </div>
    """
    
    # Manager dropdown (for managers and admins)
    if user_role in ["manager", "admin"]:
        html += """
            <div class="nav-item">
                <div class="nav-header">Manager ▾</div>
                <div class="dropdown-content">
                    <a href="./04_Team_Dashboard" class="dropdown-link">Team Dashboard</a>
                    <a href="./05_Export_Reports" class="dropdown-link">Export Reports</a>
                </div>
            </div>
        """
    
    # Settings dropdown (admin only)
    if user_role == "admin":
        html += """
            <div class="nav-item">
                <div class="nav-header">Settings ▾</div>
                <div class="dropdown-content">
                    <a href="./01_Framework_Setup" class="dropdown-link">Framework Setup</a>
                    <a href="./06_Organization_Management" class="dropdown-link">Organizations</a>
                    <a href="./07_User_Management" class="dropdown-link">User Management</a>
                </div>
            </div>
        """
    
    # User information and logout button
    html += f"""
            <div class="user-section">
                <span class="user-info"><strong>{st.session_state.username}</strong> ({st.session_state.user_role})</span>
                <a href="./?logout=true" class="logout-btn">Logout</a>
            </div>
        </div>
    </div>
    """
    
    # Render the navigation bar
    st.markdown(html, unsafe_allow_html=True)