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
    # JavaScript for the collapsible menu functionality
    collapsible_js = """
    <script>
    function toggleMenu(menuId) {
        const menuItems = document.getElementById(menuId);
        if (menuItems.style.display === "none" || menuItems.style.display === "") {
            menuItems.style.display = "block";
        } else {
            menuItems.style.display = "none";
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
    });
    </script>
    """
    st.sidebar.markdown(collapsible_js, unsafe_allow_html=True)
    
    # User role determines which menus are shown
    user_role = st.session_state.get("user_role", "")
    
    # Assessment section (available to all users)
    st.sidebar.markdown(
        """
        <div class="menu-header" onclick="toggleMenu('assessment-menu')">
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
            <div class="menu-header" onclick="toggleMenu('reports-menu')">
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
            <div class="menu-header" onclick="toggleMenu('admin-menu')">
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