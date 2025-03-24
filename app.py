import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(page_title="Skill Matrix & Competency Framework",
                   page_icon="📊",
                   layout="wide",
                   initial_sidebar_state="expanded")

import pandas as pd
import numpy as np
import os
from utils import authenticate_user, get_user_role, initialize_session_state
from data_manager import load_data, save_data
from email_manager import verify_invitation, mark_invitation_accepted

# Ensure .streamlit directory exists and create default CSS if needed
streamlit_dir = '.streamlit'
css_path = os.path.join(streamlit_dir, 'style.css')

if not os.path.exists(streamlit_dir):
    os.makedirs(streamlit_dir)

if not os.path.exists(css_path):
    with open(css_path, 'w') as f:
        f.write('/* Default Streamlit styles */\n')

# Initialize session state variables
initialize_session_state()

# Load custom CSS
with open(css_path) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
# Add CSS to hide sidebar contents until authenticated
if not st.session_state.get("authenticated", False):
    # CSS to hide the default sidebar navigation
    st.markdown("""
    <style>
    /* Hide the sidebar collapse control */
    [data-testid="collapsedControl"] {
        display: none;
    }
    
    /* Hide all pages in the sidebar navigation */
    section[data-testid="stSidebar"] .element-container:has(div.stPages) {
        display: none !important;
    }
    
    /* Hide the sidebar navigation links */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] div:has(ul) {
        display: none !important;
    }
    
    /* But keep the main sidebar container visible for login form */
    [data-testid="stSidebar"] {
        display: flex;
    }
    </style>
    """, unsafe_allow_html=True)


# Check for invitation token in query parameters
def handle_invitation():
    """Handle invitation token from URL query parameters"""
    # Use the non-experimental API
    if "token" in st.query_params:
        token = st.query_params["token"]

        # Verify the token
        is_valid, invitation = verify_invitation(token)

        if is_valid and invitation:
            st.success(f"Welcome! Your invitation is valid.")

            # Pre-fill registration form with invitation data
            st.session_state.invitation_token = token
            st.session_state.invitation_username = invitation.get(
                "username", "")
            st.session_state.invitation_email = invitation.get("email", "")
            st.session_state.invitation_role = invitation.get(
                "role", "employee")
            st.session_state.invitation_organization_id = invitation.get(
                "organization_id")

            # Show invitation acceptance form
            with st.form(key="accept_invitation_form"):
                st.subheader("Accept Invitation")
                st.write(
                    f"You've been invited to join the Skill Matrix platform with the username: **{invitation.get('username')}**"
                )

                # Personal information
                name = st.text_input("Full Name", key="inv_accept_name")

                # Email is pre-filled and not editable
                st.text_input("Email",
                              value=invitation.get("email", ""),
                              disabled=True)

                # Account setup
                username = st.text_input("Username",
                                         value=invitation.get("username", ""),
                                         key="inv_accept_username")
                password = st.text_input("Set Password",
                                         type="password",
                                         key="inv_accept_password")
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    key="inv_accept_confirm_password")

                # Job information
                job_title = st.text_input("Job Title",
                                          key="inv_accept_job_title",
                                          placeholder="Software Engineer")

                # Get job levels for dropdown
                job_levels_df = load_data("levels")
                job_level_options = [""] + job_levels_df["name"].tolist(
                ) if not job_levels_df.empty else [""]
                job_level = st.selectbox("Job Level",
                                         options=job_level_options,
                                         key="inv_accept_job_level")

                department = st.text_input("Department",
                                           key="inv_accept_department",
                                           placeholder="Engineering")

                # Get managers for dropdown
                employees_df = load_data("employees")
                managers = employees_df[["employee_id", "name"]].copy()
                manager_options = [("", "None")] + list(
                    zip(managers["employee_id"].astype(str),
                        managers["name"])) if not employees_df.empty else [
                            ("", "None")
                        ]
                manager_id = st.selectbox("Manager",
                                          options=manager_options,
                                          format_func=lambda x: x[1],
                                          key="inv_accept_manager_id")

                submit_button = st.form_submit_button(
                    label="Accept Invitation")

                if submit_button:
                    # Validate form
                    if not name or not username or not password:
                        st.error("Please fill in all required fields")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        # Add user to database
                        from data_manager import add_user, add_employee

                        # Extract manager ID (first element of the tuple)
                        manager_id_value = manager_id[
                            0] if manager_id and manager_id[0] else None

                        # Get organization ID from invitation
                        organization_id = None
                        if invitation.get("organization_id") and pd.notnull(
                                invitation["organization_id"]):
                            # Convert to int for consistency
                            try:
                                organization_id = int(
                                    float(invitation["organization_id"]))
                            except (ValueError, TypeError):
                                st.error(
                                    f"Invalid organization ID in invitation data"
                                )

                        # Create user account first
                        user_success, user_message = add_user(
                            username=username,
                            password=password,
                            role=invitation.get("role", "employee"),
                            name=name,
                            email=invitation.get("email", ""))

                        if user_success:
                            # Create employee record with organization
                            employee_success, employee_message, employee_id = add_employee(
                                name=name,
                                email=invitation.get("email", ""),
                                job_title=job_title,
                                job_level=job_level,
                                department=department,
                                manager_id=manager_id_value,
                                organization_id=organization_id)

                            if employee_success:
                                # Mark invitation as accepted
                                mark_invitation_accepted(token)

                                # Automatically log in the new user
                                st.session_state.authenticated = True
                                st.session_state.username = username
                                st.session_state.user_role = invitation.get(
                                    "role", "employee")
                                st.session_state.employee_id = employee_id

                                # Set the organization properly
                                if organization_id:
                                    # Get the organization name
                                    from data_manager import get_organization
                                    org_data = get_organization(
                                        organization_id)
                                    if org_data is not None:
                                        # Set both organization ID and name
                                        st.session_state.organization_id = int(
                                            organization_id)
                                        st.session_state.organization_name = org_data.get(
                                            "name", "")
                                        st.session_state.organization_selected = True

                                st.success(
                                    "Invitation accepted! You've been automatically logged in."
                                )

                                # Clear invitation data and params
                                for key in list(st.session_state.keys()):
                                    if key.startswith("invitation_"):
                                        del st.session_state[key]

                                # Clear query params and redirect to app
                                st.query_params.clear()
                                st.rerun()
                            else:
                                st.error(
                                    f"Failed to create employee record: {employee_message}"
                                )
                        else:
                            st.error(
                                f"Failed to create user account: {user_message}"
                            )

            # Stop further execution
            st.stop()
        else:
            st.error("This invitation link is invalid or has expired.")
            # Clear query params
            st.query_params.clear()


# User authentication
def display_login():
    # Application logo/header
    st.markdown(
        """
        <div class="login-header">
            <h1>Skill Matrix & Competency Framework</h1>
            <p>Manage and develop your team's skills effectively</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Create a two-column layout for login
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown(
            """
            <div class="card-container">
                <h2>Welcome to the Skill Management Platform</h2>
                <p>This platform helps organizations track, visualize, and optimize employee capabilities through interactive assessment and visualization tools.</p>
                <br>
                <h3>Key Features:</h3>
                <ul>
                    <li>Comprehensive skill assessment framework</li>
                    <li>Self and manager evaluations</li>
                    <li>Individual performance tracking</li>
                    <li>Team dashboards with visualization</li>
                    <li>Export reports for review sessions</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        # Login card with tabs
        st.markdown(
            """
            <div class="card-container">
                <h2>Access Your Account</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        login_tab1, login_tab2, login_tab3 = st.tabs(
            ["Account Login", "Email Self-Assessment", "Register"])

        with login_tab1:
            username = st.text_input("Username", key="username_login", placeholder="Enter your username")
            password = st.text_input("Password",
                                    type="password",
                                    key="password_login",
                                    placeholder="Enter your password")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Login", key="login_button", use_container_width=True):
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_role = get_user_role(username)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                        
            with col2:
                st.markdown("""<div style="text-align: right; padding-top: 8px;"><a href="#forgot-password">Forgot password?</a></div>""", unsafe_allow_html=True)

        with login_tab2:
            st.markdown("<p>Access your self-assessment using your email address</p>", unsafe_allow_html=True)
            email = st.text_input("Your Email",
                                key="email_login",
                                placeholder="name@company.com")

            if st.button("Access Self-Assessment", key="email_login_button", use_container_width=True):
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
                    st.error(
                        "Email not found. Please contact your manager or administrator."
                    )

        with login_tab3:
            st.markdown("<p>Create a new account to access the Skill Matrix</p>", unsafe_allow_html=True)

            # Registration form
            with st.form(key="registration_form"):
                st.subheader("Personal Information")
                reg_name = st.text_input("Full Name",
                                        key="reg_name",
                                        placeholder="John Doe")
                reg_email = st.text_input("Email",
                                        key="reg_email",
                                        placeholder="john.doe@company.com")

                st.subheader("Account Information")
                reg_username = st.text_input("Username",
                                            key="reg_username",
                                            placeholder="johndoe")
                reg_password = st.text_input("Password",
                                            type="password",
                                            key="reg_password")
                reg_confirm_password = st.text_input("Confirm Password",
                                                    type="password",
                                                    key="reg_confirm_password")

                st.subheader("Job Information")
                reg_job_title = st.text_input("Job Title",
                                            key="reg_job_title",
                                            placeholder="Software Engineer")

                # Get job levels for dropdown
                job_levels_df = load_data("levels")
                job_level_options = [""] + job_levels_df["name"].tolist(
                ) if not job_levels_df.empty else [""]
                reg_job_level = st.selectbox("Job Level",
                                            options=job_level_options,
                                            key="reg_job_level")

                reg_department = st.text_input("Department",
                                            key="reg_department",
                                            placeholder="Engineering")

                # Get managers for dropdown
                employees_df = load_data("employees")
                managers = employees_df[["employee_id", "name"]].copy()
                manager_options = [("", "None")] + list(
                    zip(managers["employee_id"].astype(str),
                        managers["name"])) if not employees_df.empty else [
                            ("", "None")
                        ]
                reg_manager_id = st.selectbox("Manager",
                                            options=manager_options,
                                            format_func=lambda x: x[1],
                                            key="reg_manager_id")
                                            
                # Submit button inside the form
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
                    manager_id = reg_manager_id[
                        0] if reg_manager_id and reg_manager_id[0] else None

                    # Add organization selection
                    st.subheader("Organization Information")

                    from data_manager import get_organizations, add_organization
                    orgs_df = get_organizations()

                    org_tab1, org_tab2 = st.tabs([
                        "Select Existing Organization",
                        "Create New Organization"
                    ])
                    organization_id = None

                    with org_tab1:
                        if not orgs_df.empty:
                            org_options = list(
                                zip(orgs_df["organization_id"].astype(str),
                                    orgs_df["name"]))
                            selected_org = st.selectbox(
                                "Select an organization",
                                options=org_options,
                                format_func=lambda x: x[1],
                                key="org_select")
                            if selected_org:
                                organization_id = int(selected_org[0])
                        else:
                            st.warning(
                                "No organizations found. Please create a new organization."
                            )

                    with org_tab2:
                        org_name = st.text_input("Organization Name",
                                                 key="new_org_name")
                        create_org = st.button("Create New Organization",
                                               key="create_org")

                        if create_org and org_name:
                            # Add new organization
                            org_success, org_message, org_id = add_organization(
                                org_name, reg_username)

                            if org_success:
                                st.success(
                                    f"Organization '{org_name}' created successfully!"
                                )
                                organization_id = org_id
                            else:
                                st.error(
                                    f"Failed to create organization: {org_message}"
                                )

                    # Create user account first
                    user_success, user_message = add_user(
                        username=reg_username,
                        password=reg_password,
                        role="employee",  # Default role for new registrations
                        name=reg_name,
                        email=reg_email)

                    if user_success:
                        # Create employee record with organization
                        employee_success, employee_message, employee_id = add_employee(
                            name=reg_name,
                            email=reg_email,
                            job_title=reg_job_title,
                            job_level=reg_job_level,
                            department=reg_department,
                            manager_id=manager_id,
                            organization_id=
                            organization_id  # Link to organization
                        )

                        if employee_success:
                            # Automatically log in the new user
                            st.session_state.authenticated = True
                            st.session_state.username = reg_username
                            st.session_state.user_role = "employee"
                            st.session_state.employee_id = employee_id

                            # Set the organization properly
                            if organization_id:
                                # Get the organization name
                                from data_manager import get_organization
                                org_data = get_organization(organization_id)
                                if org_data is not None:
                                    # Set both organization ID and name
                                    st.session_state.organization_id = int(
                                        organization_id)
                                    st.session_state.organization_name = org_data.get(
                                        "name", "")
                                    st.session_state.organization_selected = True

                            st.success(
                                "Registration successful! You've been automatically logged in."
                            )
                            st.rerun()
                        else:
                            st.error(
                                f"Failed to create employee record: {employee_message}"
                            )
                    else:
                        st.error(
                            f"Failed to create user account: {user_message}")


# Function to hide pages based on user role
def hide_pages_by_role():
    """Hide specific pages in the sidebar based on user role"""
    import streamlit as st

    # Define page access by role
    role_based_access = {
        "admin": [
            "01_Framework_Setup.py", "02_Employee_Assessment.py",
            "03_Individual_Performance.py", "04_Team_Dashboard.py",
            "05_Export_Reports.py", "06_Organization_Management.py",
            "07_User_Management.py"
        ],
        "manager": [
            "02_Employee_Assessment.py", "03_Individual_Performance.py",
            "04_Team_Dashboard.py", "05_Export_Reports.py"
        ],
        "employee":
        ["02_Employee_Assessment.py", "03_Individual_Performance.py"],
        "email_user": ["02_Employee_Assessment.py"]
    }

    # Get current role
    current_role = st.session_state.user_role
    allowed_pages = role_based_access.get(current_role, [])

    # Create JavaScript to hide the pages
    hide_pages_script = """
    <script>
    function wait_for_pages() {
        const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        const navLinks = sidebar ? sidebar.querySelectorAll('a[href*="pages"]') : [];
        
        if (navLinks.length > 0) {
            // We have page links, check which ones need to be hidden
            const allowedPages = %s;
            navLinks.forEach(link => {
                const href = link.getAttribute('href');
                const pageName = href.split('/').pop();
                
                if (!allowedPages.includes(pageName)) {
                    // Hide this page
                    const listItem = link.closest('li');
                    if (listItem) {
                        listItem.style.display = 'none';
                    } else {
                        link.style.display = 'none';
                    }
                }
            });
        } else {
            // Page links not loaded yet, try again in 100ms
            setTimeout(wait_for_pages, 100);
        }
    }
    
    // Initial call when script loads
    wait_for_pages();
    
    // Also set an interval to catch any navigation changes
    setInterval(wait_for_pages, 1000);
    </script>
    """ % str(allowed_pages)

    # Use components.html to inject the JavaScript
    from streamlit.components.v1 import html
    html(hide_pages_script, height=0, width=0)


# Main application
def main_app():
    # Import our custom UI helpers
    from ui_helpers import create_collapsible_menu
    
    # Set up user info section at the top of sidebar
    st.sidebar.markdown(
        f"""
        <div style="background-color: #0a1f2d; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <h3 style="color: #f5f0d2; margin: 0;">Welcome, {st.session_state.username}</h3>
            <p style="color: #f5f0d2; margin: 5px 0 0 0;"><b>Role:</b> {st.session_state.user_role}</p>
            {f'<p style="color: #f5f0d2; margin: 5px 0 0 0;"><b>Organization:</b> {st.session_state.organization_name}</p>' if st.session_state.organization_name else ''}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create the collapsible menu in sidebar
    create_collapsible_menu()
    
    # Hide standard pages based on user role (this is a fallback)
    hide_pages_by_role()
    
    # Add logout button at the bottom
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    if st.sidebar.button("Logout", use_container_width=True):
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

    # Load summary data filtered by organization
    try:
        from utils import get_current_organization_id
        from data_manager import load_data_for_organization

        organization_id = get_current_organization_id()

        employees_df = load_data_for_organization("employees", organization_id)
        competencies_df = load_data_for_organization("competencies",
                                                     organization_id)
        skills_df = load_data_for_organization("skills", organization_id)
        assessments_df = load_data_for_organization("assessments",
                                                    organization_id)

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
                by="assessment_date", ascending=False).head(5)

            # Join with employee names
            if not employees_df.empty:
                recent_assessments = recent_assessments.merge(
                    employees_df[["employee_id", "name"]], on="employee_id")

                for _, row in recent_assessments.iterrows():
                    st.markdown(
                        f"**{row['name']}** - {row['competency']} / {row['skill']} - "
                        f"Score: {row['score']} ({row['assessment_type']}) - "
                        f"{pd.to_datetime(row['assessment_date']).strftime('%Y-%m-%d')}"
                    )

    except Exception as e:
        st.warning(
            f"Could not load overview data. You may need to set up the framework first."
        )
        if st.session_state.user_role == "admin":
            st.info("Go to the Framework Setup page to get started.")


# Organization selection or creation
def display_organization_selector():
    st.title("Select or Create Organization")

    # Import data manager functions
    from data_manager import get_organizations, add_organization, get_user_organizations

    if st.session_state.user_role == "admin":
        # Admins can see all organizations or create new ones
        st.info(
            "As an administrator, you can select an existing organization or create a new one."
        )

        tab1, tab2 = st.tabs(["Select Organization", "Create Organization"])

        with tab1:
            # Get all organizations
            orgs_df = get_organizations()

            if not orgs_df.empty:
                org_options = list(
                    zip(orgs_df["organization_id"].astype(str),
                        orgs_df["name"]))
                selected_org = st.selectbox("Select an organization",
                                            options=org_options,
                                            format_func=lambda x: x[1])

                if st.button("Continue with Selected Organization"):
                    # Store the organization ID in session state
                    st.session_state.organization_id = int(selected_org[0])
                    st.session_state.organization_name = selected_org[1]
                    st.session_state.organization_selected = True
                    st.rerun()
            else:
                st.warning(
                    "No organizations found. Please create a new organization."
                )

        with tab2:
            # Create new organization form
            org_name = st.text_input("Organization Name")

            if st.button("Create Organization") and org_name:
                # Add new organization
                success, message, org_id = add_organization(
                    org_name, st.session_state.username)

                if success:
                    st.success(
                        f"Organization '{org_name}' created successfully!")
                    # Update schemas to include organization_id fields
                    from data_manager import update_schema_for_organizations
                    update_results = update_schema_for_organizations()

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
            org_options = list(
                zip(user_orgs["organization_id"].astype(str),
                    user_orgs["name"]))
            selected_org = st.selectbox("Select your organization",
                                        options=org_options,
                                        format_func=lambda x: x[1])

            if st.button("Continue"):
                # Store the organization ID in session state
                st.session_state.organization_id = int(selected_org[0])
                st.session_state.organization_name = selected_org[1]
                st.session_state.organization_selected = True
                st.rerun()
        else:
            st.warning(
                "You don't have access to any organizations. Please contact an administrator."
            )

            if st.button("Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                initialize_session_state()
                st.rerun()


# Application flow
# First, check for invitation tokens
handle_invitation()

# Regular application flow
if not st.session_state.authenticated:
    display_login()
elif not st.session_state.get("organization_selected", False):
    display_organization_selector()
else:
    main_app()
