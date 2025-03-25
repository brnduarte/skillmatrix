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
    
def create_custom_sidebar():
    """
    Creates a custom sidebar navigation that works with Streamlit but doesn't use
    the built-in sidebar. Manages page navigation while preserving session state.
    """
    # Only show if user is authenticated
    if not st.session_state.get("authenticated", False):
        return
        
    user_role = st.session_state.get("user_role", "")
    
    # CSS for the custom sidebar
    st.markdown("""
    <style>
    /* Custom sidebar styles */
    .custom-sidebar {
        position: fixed;
        top: 0;
        left: 0;
        bottom: 0;
        width: 230px;
        background-color: #0f2b3d;
        color: white;
        z-index: 1000;
        padding: 20px 10px;
        overflow-y: auto;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }
    
    /* Adjust main content area to make room for the sidebar */
    .main .block-container {
        margin-left: 230px !important;
        max-width: calc(100% - 230px) !important;
        padding-left: 40px !important;
        padding-right: 40px !important;
        width: calc(100% - 230px) !important;
    }
    
    /* Logo area */
    .sidebar-logo {
        text-align: center;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Navigation section */
    .nav-section {
        margin-bottom: 20px;
    }
    
    .nav-section-header {
        font-weight: bold;
        color: rgba(255,255,255,0.7);
        text-transform: uppercase;
        font-size: 12px;
        margin-bottom: 10px;
        padding-left: 10px;
    }
    
    /* Navigation items */
    .nav-item {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        cursor: pointer;
        text-decoration: none;
        color: white;
        display: block;
        transition: background-color 0.2s;
    }
    
    .nav-item:hover {
        background-color: rgba(255,255,255,0.1);
    }
    
    .nav-item.active {
        background-color: rgba(255,255,255,0.2);
        font-weight: bold;
    }
    
    /* User info section */
    .user-section {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 15px;
        background-color: rgba(0,0,0,0.2);
        font-size: 14px;
    }
    
    .user-info {
        margin-bottom: 10px;
    }
    
    /* Logout button */
    .sidebar-logout-btn {
        background-color: #d13c35;
        color: white;
        border: none;
        padding: 8px 10px;
        border-radius: 4px;
        cursor: pointer;
        width: 100%;
        text-align: center;
        display: inline-block;
        text-decoration: none;
    }
    
    .sidebar-logout-btn:hover {
        background-color: #b73229;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get current page path - using only the session state to track it
    current_path = st.session_state.get("current_page", "")
    
    # Functions to navigate to pages
    def nav_to(page_path):
        """Set the page to navigate to"""
        # Save navigation in session state
        st.session_state["nav_target"] = page_path
        
        # Use JavaScript to navigate without losing session state
        nav_script = f"""
        <script>
            window.location.href = "{page_path}";
        </script>
        """
        st.markdown(nav_script, unsafe_allow_html=True)
        
    # Create the HTML for the sidebar
    sidebar_html = """
    <div class="custom-sidebar">
        <div class="sidebar-logo">
            <h2>Skill Matrix</h2>
        </div>
    """
    
    # Create dictionary of navigation items with proper paths
    nav_items = {
        "Home": "./",
        "Dashboard": "./"
    }
    
    # Employee/self assessment pages (for all users)
    emp_items = {
        "Self Assessment": "./pages/02_Employee_Assessment",
        "My Performance": "./pages/03_Individual_Performance"
    }
    
    # Manager pages
    manager_items = {}
    if user_role in ["manager", "admin"]:
        manager_items = {
            "Team Dashboard": "./pages/04_Team_Dashboard",
            "Export Reports": "./pages/05_Export_Reports"
        }
    
    # Admin pages
    admin_items = {}
    if user_role == "admin":
        admin_items = {
            "Framework Setup": "./pages/01_Framework_Setup",
            "Organizations": "./pages/06_Organization_Management",
            "User Management": "./pages/07_User_Management"
        }
    
    # Add main navigation items
    sidebar_html += """
        <div class="nav-section">
            <div class="nav-section-header">Main</div>
    """
    
    for label, path in nav_items.items():
        active_class = "active" if current_path == path else ""
        sidebar_html += f"""
            <a href="{path}" class="nav-item {active_class}">{label}</a>
        """
    
    sidebar_html += """
        </div>
    """
    
    # Add employee assessment section
    sidebar_html += """
        <div class="nav-section">
            <div class="nav-section-header">Assessment</div>
    """
    
    for label, path in emp_items.items():
        active_class = "active" if current_path == path else ""
        sidebar_html += f"""
            <a href="{path}" class="nav-item {active_class}">{label}</a>
        """
    
    sidebar_html += """
        </div>
    """
    
    # Add manager section if applicable
    if manager_items:
        sidebar_html += """
            <div class="nav-section">
                <div class="nav-section-header">Management</div>
        """
        
        for label, path in manager_items.items():
            active_class = "active" if current_path == path else ""
            sidebar_html += f"""
                <a href="{path}" class="nav-item {active_class}">{label}</a>
            """
        
        sidebar_html += """
            </div>
        """
    
    # Add admin section if applicable
    if admin_items:
        sidebar_html += """
            <div class="nav-section">
                <div class="nav-section-header">Administration</div>
        """
        
        for label, path in admin_items.items():
            active_class = "active" if current_path == path else ""
            sidebar_html += f"""
                <a href="{path}" class="nav-item {active_class}">{label}</a>
            """
        
        sidebar_html += """
            </div>
        """
    
    # Add user info and logout
    sidebar_html += f"""
        <div class="user-section">
            <div class="user-info">
                <strong>{st.session_state.username}</strong><br>
                {st.session_state.user_role}
            </div>
            <a href="./?logout=true" class="sidebar-logout-btn">Logout</a>
        </div>
    """
    
    sidebar_html += """
    </div>
    """
    
    # Render the sidebar
    st.markdown(sidebar_html, unsafe_allow_html=True)

def create_top_navigation():
    """
    Legacy top navigation function, kept for compatibility.
    Using the custom sidebar navigation instead.
    """
    # Delegate to the custom sidebar navigation
    create_custom_sidebar()