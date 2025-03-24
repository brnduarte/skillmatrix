import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "current_employee_id" not in st.session_state:
        st.session_state.current_employee_id = None
    if "employee_email" not in st.session_state:
        st.session_state.employee_email = None
    if "organization_selected" not in st.session_state:
        st.session_state.organization_selected = False
    if "organization_id" not in st.session_state:
        st.session_state.organization_id = None
    if "organization_name" not in st.session_state:
        st.session_state.organization_name = None

def authenticate_user(username, password):
    """
    Authenticate a user based on username and password
    In a real application, this would use secure authentication methods
    """
    # For demo purposes, using simple authentication
    # In a production environment, use secure password hashing and verification
    try:
        users_df = pd.read_csv("users.csv")
        user = users_df[(users_df["username"] == username) & (users_df["password"] == password)]
        return not user.empty
    except FileNotFoundError:
        # If no users file exists, create default admin account
        if username == "admin" and password == "admin":
            create_default_admin()
            return True
        return False

def get_user_role(username):
    """Get the role of the authenticated user"""
    try:
        users_df = pd.read_csv("users.csv")
        user = users_df[users_df["username"] == username]
        if not user.empty:
            return user.iloc[0]["role"]
        return None
    except FileNotFoundError:
        # If this is the first run with default admin
        if username == "admin":
            return "admin"
        return None

def create_default_admin():
    """Create a default admin user if no users exist"""
    users_df = pd.DataFrame({
        "username": ["admin"],
        "password": ["admin"],
        "role": ["admin"],
        "name": ["Administrator"],
        "email": ["admin@example.com"]
    })
    users_df.to_csv("users.csv", index=False)

def get_user_id(username):
    """Get the employee ID associated with a username or email login"""
    try:
        employees_df = pd.read_csv("employees.csv")
        
        # Check if this is an email login
        if username.startswith("email_"):
            email = username.replace("email_", "")
            employee = employees_df[employees_df["email"] == email]
            if not employee.empty:
                return employee.iloc[0]["employee_id"]
        else:
            # Regular user login
            users_df = pd.read_csv("users.csv")
            user = users_df[users_df["username"] == username]
            if not user.empty:
                user_email = user.iloc[0]["email"]
                employee = employees_df[employees_df["email"] == user_email]
                if not employee.empty:
                    return employee.iloc[0]["employee_id"]
    except Exception as e:
        pass
    return None

def check_permission(required_role):
    """Check if the current user has the required role"""
    if not st.session_state.authenticated:
        return False
    
    if required_role == "any":
        return True
    
    user_role = st.session_state.user_role
    
    # Admin has access to everything
    if user_role == "admin":
        return True
    
    # Manager has access to manager and employee areas
    if user_role == "manager" and required_role in ["manager", "employee"]:
        return True
    
    # Employee only has access to employee areas
    if user_role == "employee" and required_role == "employee":
        return True
    
    # Email users have access to self-assessment only
    if user_role == "email_user" and required_role == "employee":
        return True
    
    return False

def format_date(date_str):
    """Format a date string for display"""
    try:
        return pd.to_datetime(date_str).strftime("%Y-%m-%d")
    except:
        return date_str

def calculate_mean(values):
    """Calculate the mean of numeric values, ignoring NaN"""
    if not values or len(values) == 0:
        return 0
    return np.nanmean([float(v) for v in values if v and not pd.isna(v)])

def get_level_expectation(job_level, competency, skill, expectations_df):
    """Get the expected skill level for a job level"""
    if expectations_df is None or expectations_df.empty:
        return None
    
    filtered = expectations_df[
        (expectations_df["job_level"] == job_level) & 
        (expectations_df["competency"] == competency) & 
        (expectations_df["skill"] == skill)
    ]
    
    if not filtered.empty:
        return filtered.iloc[0]["expected_score"]
    return None

def get_employee_manager_id(employee_id):
    """Get the manager ID for a given employee"""
    try:
        employees_df = pd.read_csv("employees.csv")
        employee = employees_df[employees_df["employee_id"] == employee_id]
        if not employee.empty:
            return employee.iloc[0]["manager_id"]
    except Exception:
        pass
    return None

def get_employees_for_manager(manager_id):
    """Get all employees reporting to a manager"""
    try:
        employees_df = pd.read_csv("employees.csv")
        return employees_df[employees_df["manager_id"] == manager_id]
    except Exception:
        return pd.DataFrame()

def is_manager_of(manager_id, employee_id):
    """Check if a user is the manager of an employee"""
    try:
        employees_df = pd.read_csv("employees.csv")
        employee = employees_df[employees_df["employee_id"] == employee_id]
        if not employee.empty:
            return employee.iloc[0]["manager_id"] == manager_id
    except Exception:
        pass
    return False

def get_current_organization_id():
    """Get the current organization ID from session state
    
    Returns:
        int or None: The organization ID or None if not selected
    """
    if hasattr(st.session_state, "organization_id") and st.session_state.organization_id is not None:
        return st.session_state.organization_id
    return None

def check_page_access(allowed_roles):
    """Check if the current user has access to the page
    
    Args:
        allowed_roles: List of roles that have access to the page
        
    Returns:
        bool: True if the user has access, False otherwise
    """
    # Initialize session state if needed
    initialize_session_state()
    
    # Check if user is authenticated
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in to access this page.")
        st.stop()
        return False
        
    # Check if user has selected an organization
    if not st.session_state.get("organization_selected", False):
        st.warning("Please select an organization to continue.")
        st.stop()
        return False
        
    # Check if user role is allowed
    current_role = st.session_state.get("user_role", "")
    if current_role not in allowed_roles:
        st.error("You don't have permission to access this page.")
        st.stop()
        return False
        
    return True

def create_organized_sidebar():
    """Create an organized sidebar with nested sections based on user role
    
    This function creates a consistent sidebar structure across all pages.
    """
    if "user_role" not in st.session_state:
        return
    
    current_role = st.session_state.user_role
    
    # Add sidebar header with user info
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    st.sidebar.markdown(f"**Role**: {st.session_state.user_role}")

    # Display current organization
    if st.session_state.organization_name:
        st.sidebar.markdown(f"**Organization**: {st.session_state.organization_name}")
        
    # Add Home link
    st.sidebar.markdown('<a href="/" target="_self">🏠 Home</a>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Define sections with their pages
    sidebar_sections = {
        "Assessments": {
            "roles": ["admin", "manager", "employee", "email_user"],
            "pages": ["02_Employee_Assessment.py", "03_Individual_Performance.py"],
            "icons": ["📝", "📊"]
        },
        "Manager": {
            "roles": ["admin", "manager"],
            "pages": ["04_Team_Dashboard.py", "05_Export_Reports.py"],
            "icons": ["👥", "📄"]
        },
        "Settings": {
            "roles": ["admin"],
            "pages": ["01_Framework_Setup.py", "06_Organization_Management.py", "07_User_Management.py"],
            "icons": ["⚙️", "🏢", "👤"]
        }
    }
    
    # Create links for each section if user has access
    for section_name, section_data in sidebar_sections.items():
        # Check if user has access to any page in this section
        if current_role in section_data["roles"]:
            # Create an expander for the section
            with st.sidebar.expander(f"**{section_name}**", expanded=True):
                # Add links to each page in this section
                for i, page in enumerate(section_data["pages"]):
                    # Get the page name without extension and numbering
                    page_name = page.split("_", 1)[1].replace(".py", "").replace("_", " ")
                    icon = section_data["icons"][i] if i < len(section_data["icons"]) else "📄"
                    
                    # Create a link to the page using HTML to ensure it opens in the same tab
                    st.markdown(f'<a href="/{page}" target="_self">{icon} {page_name}</a>', unsafe_allow_html=True)
    
    # Add logout button
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_session_state()
        st.rerun()
