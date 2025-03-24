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

def create_collapsible_menu():
    """Creates a collapsible menu in the sidebar that organizes pages into categories
    
    This function creates expandable/collapsible sections in the sidebar with categories
    like 'Assessment', 'Reports', 'Administration'.
    """
    # Add CSS for menu styling
    menu_css = """
    <style>
    /* Menu styling */
    .menu-header {
        cursor: pointer;
        padding: 10px;
        background-color: #0a1f2d;
        color: #f5f0d2;
        border-radius: 5px;
        margin-bottom: 10px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .menu-header::after {
        content: "▾";
        font-size: 16px;
    }
    
    .menu-header.active::after {
        content: "▴";
    }
    
    .menu-items {
        margin-bottom: 20px;
        background-color: #f5f5f5;
        border-radius: 5px;
        overflow: hidden;
    }
    
    .menu-items ul {
        margin: 0;
        padding: 10px;
    }
    
    .menu-items li {
        margin-bottom: 8px;
    }
    
    .menu-items a {
        color: #0a1f2d;
        text-decoration: none;
        display: block;
        padding: 5px 10px;
        transition: all 0.2s ease;
        border-radius: 3px;
    }
    
    .menu-items a:hover {
        background-color: #d0e8f2;
        padding-left: 15px;
    }
    
    /* Hide default sidebar nav elements to avoid duplication */
    section[data-testid="stSidebar"] .element-container:has(div.stPages) {
        display: none !important;
    }
    </style>
    """
    st.sidebar.markdown(menu_css, unsafe_allow_html=True)
    
    # JavaScript for the collapsible menu functionality
    collapsible_js = """
    <script>
    function toggleMenu(menuId) {
        const menuItems = document.getElementById(menuId);
        const menuHeader = document.querySelector(`[data-menu="${menuId}"]`);
        
        if (menuItems.style.display === "none" || menuItems.style.display === "") {
            menuItems.style.display = "block";
            if (menuHeader) menuHeader.classList.add("active");
        } else {
            menuItems.style.display = "none";
            if (menuHeader) menuHeader.classList.remove("active");
        }
    }
    
    // Initialize menus as collapsed
    document.addEventListener('DOMContentLoaded', function() {
        const menuIds = ['assessment-menu', 'reports-menu', 'admin-menu'];
        menuIds.forEach(id => {
            const menu = document.getElementById(id);
            if (menu) {
                menu.style.display = "none";
            }
        });
        
        // Auto-expand the section for the current page
        const currentPath = window.location.pathname;
        if (currentPath.includes('01_Framework_Setup') || 
            currentPath.includes('06_Organization_Management') || 
            currentPath.includes('07_User_Management')) {
            toggleMenu('admin-menu');
        } else if (currentPath.includes('04_Team_Dashboard') || 
                  currentPath.includes('05_Export_Reports')) {
            toggleMenu('reports-menu');
        } else if (currentPath.includes('02_Employee_Assessment') || 
                  currentPath.includes('03_Individual_Performance')) {
            toggleMenu('assessment-menu');
        }
    });
    </script>
    """
    st.sidebar.markdown(collapsible_js, unsafe_allow_html=True)
    
    # Title for navigation section
    st.sidebar.markdown("<h3>Navigation</h3>", unsafe_allow_html=True)
    
    # User role determines which menus are shown
    user_role = st.session_state.get("user_role", "")
    
    # Assessment section (available to all users)
    st.sidebar.markdown(
        """
        <div class="menu-header" data-menu="assessment-menu" onclick="toggleMenu('assessment-menu')">
            📊 Assessment
        </div>
        <div id="assessment-menu" class="menu-items">
            <ul style="list-style-type: none; padding-left: 0;">
                <li><a href="./02_Employee_Assessment" target="_self">Self-Assessment</a></li>
                <li><a href="./03_Individual_Performance" target="_self">My Performance</a></li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Reports section (for managers and admins)
    if user_role in ["manager", "admin"]:
        st.sidebar.markdown(
            """
            <div class="menu-header" data-menu="reports-menu" onclick="toggleMenu('reports-menu')">
                📈 Reports
            </div>
            <div id="reports-menu" class="menu-items">
                <ul style="list-style-type: none; padding-left: 0;">
                    <li><a href="./04_Team_Dashboard" target="_self">Team Dashboard</a></li>
                    <li><a href="./05_Export_Reports" target="_self">Export Reports</a></li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Admin section (for admins only)
    if user_role == "admin":
        st.sidebar.markdown(
            """
            <div class="menu-header" data-menu="admin-menu" onclick="toggleMenu('admin-menu')">
                ⚙️ Administration
            </div>
            <div id="admin-menu" class="menu-items">
                <ul style="list-style-type: none; padding-left: 0;">
                    <li><a href="./01_Framework_Setup" target="_self">Framework Setup</a></li>
                    <li><a href="./06_Organization_Management" target="_self">Organization Management</a></li>
                    <li><a href="./07_User_Management" target="_self">User Management</a></li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

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