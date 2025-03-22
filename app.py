import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Skill Matrix & Competency Framework",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import numpy as np
import os
from utils import authenticate_user, get_user_role, initialize_session_state
from data_manager import load_data, save_data

# Load custom CSS
with open(os.path.join('.streamlit', 'style.css')) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state variables
initialize_session_state()

# User authentication
def display_login():
    st.title("Skill Matrix & Competency Framework")
    st.subheader("Login")
    
    login_tab1, login_tab2 = st.tabs(["Account Login", "Email Self-Assessment"])
    
    with login_tab1:
        username = st.text_input("Username", key="username_login")
        password = st.text_input("Password", type="password", key="password_login")
        
        if st.button("Login", key="login_button"):
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_role = get_user_role(username)
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with login_tab2:
        st.write("Access your self-assessment using your email address")
        email = st.text_input("Your Email", key="email_login", placeholder="name@company.com") 
        
        if st.button("Access Self-Assessment", key="email_login_button"):
            # Check if email exists in the employees database
            employees_df = load_data("employees")
            employee = employees_df[employees_df["email"] == email]
            
            if not employee.empty:
                # Create a temporary user session for self-assessment only
                st.session_state.authenticated = True
                st.session_state.username = f"email_{email}"  # Special format to identify email login
                st.session_state.user_role = "email_user"  # Special role with limited access
                st.session_state.employee_email = email
                st.rerun()
            else:
                st.error("Email not found. Please contact your manager or administrator.")

# Main application
def main_app():
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    st.sidebar.markdown(f"**Role**: {st.session_state.user_role}")
    
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_session_state()
        st.rerun()
    
    # Home Page Content
    st.title("Skill Matrix & Competency Framework")
    
    # Display overview based on role
    if st.session_state.user_role == "admin":
        st.info("""
        ### Admin Dashboard
        
        As an administrator, you can:
        - Set up and manage the competency framework
        - Create and modify skills within competencies
        - Define expected skill levels for each role/position
        - Add and manage users
        - View team and individual performance
        
        Navigate using the pages in the sidebar.
        """)
        
    elif st.session_state.user_role == "manager":
        st.info("""
        ### Manager Dashboard
        
        As a manager, you can:
        - Evaluate team members' skills
        - View individual and team performance metrics
        - Compare performance against expected levels
        - Generate and export reports
        
        Navigate using the pages in the sidebar.
        """)
        
    elif st.session_state.user_role == "employee":
        st.info("""
        ### Employee Dashboard
        
        As an employee, you can:
        - Complete self-assessments of your skills
        - View your performance metrics and manager feedback
        - Compare your current skills with expected levels
        - Track your progress over time
        
        Navigate using the pages in the sidebar.
        """)
    
    elif st.session_state.user_role == "email_user":
        # Display email user dashboard
        employee_email = st.session_state.employee_email
        employees_df = load_data("employees")
        employee = employees_df[employees_df["email"] == employee_email]
        
        if not employee.empty:
            employee_name = employee.iloc[0]["name"]
            st.info(f"""
            ### Self-Assessment Portal for {employee_name}
            
            Welcome to your self-assessment portal. Here you can:
            - Complete skill self-assessments
            - View your current skills and ratings
            
            Please go to the Employee Assessment page in the sidebar to complete your assessment.
            """)
    
    # Key metrics overview
    st.header("Overview")
    
    # Load summary data
    try:
        employees_df = load_data("employees")
        competencies_df = load_data("competencies")
        skills_df = load_data("skills")
        assessments_df = load_data("assessments")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Employees", len(employees_df))
            
        with col2:
            st.metric("Competencies", len(competencies_df))
            
        with col3:
            st.metric("Skills", len(skills_df))
        
        # Show recent updates
        if not assessments_df.empty:
            st.subheader("Recent Assessments")
            recent_assessments = assessments_df.sort_values(
                by="assessment_date", ascending=False
            ).head(5)
            
            # Join with employee names
            if not employees_df.empty:
                recent_assessments = recent_assessments.merge(
                    employees_df[["employee_id", "name"]],
                    on="employee_id"
                )
                
                for _, row in recent_assessments.iterrows():
                    st.markdown(
                        f"**{row['name']}** - {row['competency']} / {row['skill']} - "
                        f"Score: {row['score']} ({row['assessment_type']}) - "
                        f"{pd.to_datetime(row['assessment_date']).strftime('%Y-%m-%d')}"
                    )
        
    except Exception as e:
        st.warning(f"Could not load overview data. You may need to set up the framework first.")
        if st.session_state.user_role == "admin":
            st.info("Go to the Framework Setup page to get started.")

# Application flow
if not st.session_state.authenticated:
    display_login()
else:
    main_app()
