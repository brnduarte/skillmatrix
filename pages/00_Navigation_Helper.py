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

st.error("""
## Important URL Information

The navigation bar has been completely removed as requested. To navigate between pages, you need to use the **correct URL format**.

Streamlit requires a specific URL format that includes the `/pages/` prefix followed by the exact filename:

```
https://your-domain.com/pages/01_Framework_Setup
```

Not using the proper format will result in a "page not found" error.
""")

st.header("Available Pages")

# Create a colored box to draw attention to the URL format
st.markdown("""
<div style='padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 20px;'>
<h3 style='margin-top: 0;'>Correct URL Patterns</h3>
<p>Always include <code>/pages/</code> before the page name:</p>
</div>
""", unsafe_allow_html=True)

# Create a more visually appealing table of the pages and their URLs
st.markdown("""
| Page Name | Correct URL to Use | Description |
|-----------|------------------|-------------|
| Home/Login | `/` | Main dashboard and login page |
| Navigation Helper | `/pages/00_Navigation_Helper` | This page - navigation assistance |
| Framework Setup | `/pages/01_Framework_Setup` | Define competencies, skills, and job levels |
| Employee Assessment | `/pages/02_Employee_Assessment` | Self and manager assessments |
| Individual Performance | `/pages/03_Individual_Performance` | Individual performance metrics |
| Team Dashboard | `/pages/04_Team_Dashboard` | Team performance and analysis |
| Export Reports | `/pages/05_Export_Reports` | Generate PDF/Excel reports |
| Organization Management | `/pages/06_Organization_Management` | Manage organizations |
| User Management | `/pages/07_User_Management` | Manage users and invitations |
""")

st.warning("**Note**: Make sure you're logged in before using these direct links. If your session expires, you'll be redirected to the login page.")

# Show user role and available pages
if st.session_state.authenticated:
    st.header("Your Access")
    st.write(f"Your role: **{st.session_state.user_role}**")
    
    # Also display organization info if selected
    if st.session_state.get("organization_selected", False):
        st.write(f"Current organization: **{st.session_state.get('organization_name', 'None')}**")
    
    # Determine available pages based on role
    available_pages = []
    
    # Everyone has access to Employee Assessment and Individual Performance
    available_pages.extend([
        "00_Navigation_Helper",
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
    
    # If email user, limit access
    if st.session_state.user_role == "email_user":
        available_pages = ["00_Navigation_Helper", "02_Employee_Assessment"]
    
    st.subheader("Pages You Can Access")
    
    # Create a more visually appealing grid of navigation buttons
    # Organize in rows of 3 buttons
    cols_per_row = 3
    
    # Sort pages to ensure they're in order
    sorted_pages = sorted(available_pages) 
    
    # Group pages into rows
    for i in range(0, len(sorted_pages), cols_per_row):
        # Create a row of columns
        row = st.columns(cols_per_row)
        
        # Add buttons to each column in this row
        for col_idx in range(cols_per_row):
            page_idx = i + col_idx
            
            # Check if we still have pages to display
            if page_idx < len(sorted_pages):
                page = sorted_pages[page_idx]
                
                # Extract page name for display
                if page.startswith("0"):
                    page_num = page[:2]
                    page_name = page[3:].replace("_", " ")
                else:
                    page_num = ""
                    page_name = page.replace("_", " ")
                
                # Add emoji based on page type
                emoji = "📋"
                if "Framework" in page_name:
                    emoji = "🧩"
                elif "Employee" in page_name:
                    emoji = "📊"
                elif "Individual" in page_name:
                    emoji = "👤"
                elif "Team" in page_name:
                    emoji = "👥"
                elif "Export" in page_name:
                    emoji = "📄"
                elif "Organization" in page_name:
                    emoji = "🏢"
                elif "User" in page_name:
                    emoji = "👥"
                elif "Navigation" in page_name:
                    emoji = "🧭"
                
                # Create button in the appropriate column with the page number as a badge
                with row[col_idx]:
                    if st.button(f"{emoji} {page_name}", key=f"btn_{page}", use_container_width=True):
                        st.switch_page(f"pages/{page}.py")
    
    st.markdown("---")
    
    # Add a "Return to Dashboard" button at the bottom
    if st.button("🏠 Return to Dashboard", use_container_width=True):
        st.switch_page("app.py")
        
    # Add a logout button
    if st.button("🚪 Logout", use_container_width=True):
        # Clear all session state and redirect to home
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("app.py")