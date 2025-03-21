import streamlit as st
import pandas as pd
import numpy as np
from utils import authenticate_user, get_user_role, initialize_session_state
from data_manager import load_data, save_data

# Page configuration
st.set_page_config(
    page_title="Skill Matrix & Competency Framework",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
initialize_session_state()

# User authentication
def display_login():
    st.title("Skill Matrix & Competency Framework")
    st.subheader("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = get_user_role(username)
            st.rerun()
        else:
            st.error("Invalid username or password")

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
