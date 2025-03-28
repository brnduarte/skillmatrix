import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        
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
    
    # Return whether authenticated and organization are selected
    return {
        "authenticated": st.session_state.authenticated,
        "organization_selected": st.session_state.organization_selected
    }

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

def track_page_load():
    """
    Tracks the current page being loaded and updates session state.
    This allows the custom navigation to highlight the active page.
    This function should be called at the top of each page.
    
    Returns:
        The current page path
    """
    # Get the script path that's currently running
    try:
        current_script = sys.argv[0]
        # Get the page name from the script path
        if current_script.endswith(".py"):
            if '/pages/' in current_script:
                # For pages, use the page path
                page_path = './pages/' + os.path.basename(current_script)
            else:
                # For main app, use root path
                page_path = './'
            
            # Store the current page in session state
            st.session_state["current_page"] = page_path
            return page_path
    except:
        # Default to root if we can't determine the page
        st.session_state["current_page"] = './'
        return './'

def check_page_access(allowed_roles):
    """Check if the current user has access to the page
    
    Args:
        allowed_roles: List of roles that have access to the page
        
    Returns:
        bool: True if the user has access, False otherwise
    """
    # Initialize session state if needed
    initialize_session_state()
    
    # Track what page is being loaded
    track_page_load()
    
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
