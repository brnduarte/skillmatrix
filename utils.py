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
    """Get the employee ID associated with a username"""
    try:
        users_df = pd.read_csv("users.csv")
        employees_df = pd.read_csv("employees.csv")
        
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
