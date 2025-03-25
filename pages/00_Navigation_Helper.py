import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Navigation Helper - Skill Matrix",
    page_icon="🧭",
    layout="wide"
)

from utils import initialize_session_state, check_page_access
from ui_helpers import load_custom_css

# Load custom CSS for consistent styling
load_custom_css()

# Initialize session state and check if user is authenticated
state = initialize_session_state()
if not state["authenticated"]:
    st.warning("Please login from the Home page.")
    st.switch_page("app.py")
    st.stop()

# No need to check organization here since this is just a helper page

st.title("Navigation Helper")

st.info("""
This is a helper page that shows the correct URL formats for direct navigation.
Streamlit uses the filenames of pages for URL routing.
""")

st.header("Available Pages")

# Create a table of the pages and their URLs
st.markdown("""
| Page Name | Direct URL to Use |
|-----------|------------------|
| Home/Login | `/` |
| Framework Setup | `/01_Framework_Setup` |
| Employee Assessment | `/02_Employee_Assessment` |
| Individual Performance | `/03_Individual_Performance` |
| Team Dashboard | `/04_Team_Dashboard` |
| Export Reports | `/05_Export_Reports` |
| Organization Management | `/06_Organization_Management` |
| User Management | `/07_User_Management` |
""")

st.caption("Note: Make sure you're logged in before using these direct links.")

# Show user role and available pages
if st.session_state.authenticated:
    st.header("Your Access")
    st.write(f"Your role: **{st.session_state.user_role}**")
    
    # Determine available pages based on role
    available_pages = []
    
    # Everyone has access to Employee Assessment and Individual Performance
    available_pages.extend([
        "02_Employee_Assessment",
        "03_Individual_Performance"
    ])
    
    # Managers and admins have access to Team Dashboard and Export Reports
    if st.session_state.user_role in ["admin", "manager"]:
        available_pages.extend([
            "04_Team_Dashboard",
            "05_Export_Reports"
        ])
    
    # Only admins have access to Framework Setup, Organization Management, and User Management
    if st.session_state.user_role == "admin":
        available_pages.extend([
            "01_Framework_Setup",
            "06_Organization_Management",
            "07_User_Management"
        ])
    
    st.subheader("Pages You Can Access")
    
    # Create buttons to navigate to each page
    for page in sorted(available_pages):
        # Extract page name from filename by removing the number prefix and replacing underscores with spaces
        page_name = page[3:].replace("_", " ")
        
        if st.button(f"Go to {page_name}", key=f"btn_{page}"):
            st.switch_page(f"pages/{page}.py")