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
    
    login_tab1, login_tab2, login_tab3 = st.tabs(["Account Login", "Email Self-Assessment", "Register"])
    
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
    
    with login_tab3:
        st.write("Create a new account to access the Skill Matrix")
        
        # Registration form
        with st.form(key="registration_form"):
            st.subheader("Personal Information")
            reg_name = st.text_input("Full Name", key="reg_name", placeholder="John Doe")
            reg_email = st.text_input("Email", key="reg_email", placeholder="john.doe@company.com")
            
            st.subheader("Account Information")
            reg_username = st.text_input("Username", key="reg_username", placeholder="johndoe")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
            
            st.subheader("Job Information")
            reg_job_title = st.text_input("Job Title", key="reg_job_title", placeholder="Software Engineer")
            
            # Get job levels for dropdown
            job_levels_df = load_data("levels")
            job_level_options = [""] + job_levels_df["name"].tolist() if not job_levels_df.empty else [""]
            reg_job_level = st.selectbox("Job Level", options=job_level_options, key="reg_job_level")
            
            reg_department = st.text_input("Department", key="reg_department", placeholder="Engineering")
            
            # Get managers for dropdown
            employees_df = load_data("employees")
            managers = employees_df[["employee_id", "name"]].copy()
            manager_options = [("", "None")] + list(zip(managers["employee_id"].astype(str), managers["name"])) if not employees_df.empty else [("", "None")]
            reg_manager_id = st.selectbox("Manager", options=manager_options, format_func=lambda x: x[1], key="reg_manager_id")
            
            # Submit button
            submit_button = st.form_submit_button(label="Register")
            
            if submit_button:
                # Validate form
                if not reg_name or not reg_email or not reg_username or not reg_password:
                    st.error("Please fill in all required fields")
                elif reg_password != reg_confirm_password:
                    st.error("Passwords do not match")
                elif "@" not in reg_email or "." not in reg_email:
                    st.error("Please enter a valid email address")
                else:
                    # Add user to database
                    from data_manager import add_user, add_employee
                    
                    # Extract manager ID (first element of the tuple)
                    manager_id = reg_manager_id[0] if reg_manager_id and reg_manager_id[0] else None
                    
                    # Create employee record first
                    success, message, employee_id = add_employee(
                        name=reg_name,
                        email=reg_email,
                        job_title=reg_job_title,
                        job_level=reg_job_level,
                        department=reg_department,
                        manager_id=manager_id
                    )
                    
                    if success:
                        # Create user account
                        user_success, user_message = add_user(
                            username=reg_username,
                            password=reg_password,
                            role="employee",  # Default role for new registrations
                            name=reg_name,
                            email=reg_email
                        )
                        
                        if user_success:
                            st.success("Registration successful! You can now log in with your username and password.")
                        else:
                            st.error(f"Failed to create user account: {user_message}")
                    else:
                        st.error(f"Failed to create employee record: {message}")

# Main application
def main_app():
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    st.sidebar.markdown(f"**Role**: {st.session_state.user_role}")
    
    # Display current organization
    if st.session_state.organization_name:
        st.sidebar.markdown(f"**Organization**: {st.session_state.organization_name}")
    
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

# Organization selection or creation
def display_organization_selector():
    st.title("Select or Create Organization")
    
    # Import data manager functions
    from data_manager import get_organizations, add_organization, get_user_organizations
    
    if st.session_state.user_role == "admin":
        # Admins can see all organizations or create new ones
        st.info("As an administrator, you can select an existing organization or create a new one.")
        
        tab1, tab2 = st.tabs(["Select Organization", "Create Organization"])
        
        with tab1:
            # Get all organizations
            orgs_df = get_organizations()
            
            if not orgs_df.empty:
                org_options = list(zip(orgs_df["organization_id"].astype(str), orgs_df["name"]))
                selected_org = st.selectbox(
                    "Select an organization", 
                    options=org_options,
                    format_func=lambda x: x[1]
                )
                
                if st.button("Continue with Selected Organization"):
                    # Store the organization ID in session state
                    st.session_state.organization_id = int(selected_org[0])
                    st.session_state.organization_name = selected_org[1]
                    st.session_state.organization_selected = True
                    st.rerun()
            else:
                st.warning("No organizations found. Please create a new organization.")
        
        with tab2:
            # Create new organization form
            org_name = st.text_input("Organization Name")
            
            if st.button("Create Organization") and org_name:
                # Add new organization
                success, message, org_id = add_organization(org_name, st.session_state.username)
                
                if success:
                    st.success(f"Organization '{org_name}' created successfully!")
                    # Store the organization ID in session state
                    st.session_state.organization_id = org_id
                    st.session_state.organization_name = org_name
                    st.session_state.organization_selected = True
                    st.rerun()
                else:
                    st.error(f"Failed to create organization: {message}")
    else:
        # Regular users can only see their organizations
        user_orgs = get_user_organizations(st.session_state.username)
        
        if not user_orgs.empty:
            org_options = list(zip(user_orgs["organization_id"].astype(str), user_orgs["name"]))
            selected_org = st.selectbox(
                "Select your organization", 
                options=org_options,
                format_func=lambda x: x[1]
            )
            
            if st.button("Continue"):
                # Store the organization ID in session state
                st.session_state.organization_id = int(selected_org[0])
                st.session_state.organization_name = selected_org[1]
                st.session_state.organization_selected = True
                st.rerun()
        else:
            st.warning("You don't have access to any organizations. Please contact an administrator.")
            
            if st.button("Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                initialize_session_state()
                st.rerun()

# Application flow
if not st.session_state.authenticated:
    display_login()
elif not st.session_state.get("organization_selected", False):
    display_organization_selector()
else:
    main_app()
