import streamlit as st

# Server configuration
import os
os.environ['STREAMLIT_SERVER_PORT'] = '5000'
os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'

# Page configuration must be the first Streamlit command
st.set_page_config(page_title="Dashboard - Skill Matrix & Competency Framework",
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
    
# Import UI helper functions
from ui_helpers import create_custom_sidebar

# Add track_page_load to monitor current page
from utils import track_page_load


# Check for invitation token in query parameters
def handle_invitation():
    """Handle invitation token from URL query parameters"""
    # Use the non-experimental API
    if "token" in st.query_params:
        token_raw = st.query_params["token"]
        
        # Clean the token and ensure it's a string
        token = str(token_raw).strip()
        
        # More subtle processing notification
        with st.spinner("Processing your invitation..."):
            # Process invitation token silently (log to console only)
            print(f"Processing invitation token: {token}")
            print(f"Raw token from URL: {token_raw}")
            print(f"Cleaned token: {token}")
            print(f"Token type: {type(token).__name__}")
            
            # Verify the token without showing all the debug info to user
            token_to_verify = str(token).strip()
            is_valid, invitation = verify_invitation(token_to_verify)
            
            print(f"Verification result: Valid={is_valid}, Data exists={invitation is not None}")
            
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

                    # Job information section removed for streamlined user experience
                    # All users coming from email invitations don't need to specify job details
                    job_title = "Admin"  # Default job title for invited users
                    job_level = ""  # Empty job level
                    department = ""  # Empty department
                    manager_id = ("", "None")  # Default - no manager

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
                            if invitation.get("organization_id"):
                                try:
                                    # Handle various formats (int, float, string)
                                    org_id_raw = invitation["organization_id"]
                                    if isinstance(org_id_raw, (int, float)):
                                        organization_id = int(org_id_raw)
                                    elif isinstance(org_id_raw, str) and org_id_raw.strip():
                                        organization_id = int(float(org_id_raw))
                                except (ValueError, TypeError):
                                    print(f"Invalid organization ID in invitation: {invitation.get('organization_id')}")

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
                                    # Mark invitation as accepted - use the cleaned token_to_verify
                                    print(f"Marking token {token_to_verify} as accepted...")
                                    acceptance_result = mark_invitation_accepted(token_to_verify)
                                    print(f"Acceptance update result: {acceptance_result}")

                                    # Automatically log in the new user
                                    st.session_state.authenticated = True
                                    st.session_state.username = username
                                    
                                    # Initialize success message
                                    success_msg = ""
                                    
                                    # Set user role and handle organization assignment
                                    if invitation:
                                        # Use role from invitation
                                        role = invitation.get("role", "employee")
                                        st.session_state.user_role = role
                                        st.session_state.employee_id = employee_id
                                        
                                        # Handle organization assignment
                                        if invitation.get("organization_id"):
                                            org_id = int(float(invitation["organization_id"]))
                                            org_data = get_organization(org_id)
                                            if org_data is not None:
                                                st.session_state.organization_id = org_id
                                                st.session_state.organization_name = org_data.get("name", "")
                                                st.session_state.organization_selected = True
                                                success_msg = f"Invitation accepted! You've been added to the organization as a {role}."
                                            else:
                                                st.error("Error retrieving organization information.")
                                                st.stop()
                                        elif role == "admin":
                                            # Only admins without organization should create one
                                            st.session_state.organization_id = None
                                            st.session_state.organization_name = None
                                            st.session_state.organization_selected = False
                                            st.session_state.redirect_to_org_management = True
                                            success_msg = "Registration successful! Please create your organization to get started."
                                        elif role in ["employee", "manager"]:
                                            st.error("Invalid invitation: Organization required for employee/manager roles.")
                                            st.stop()
                                        else:
                                            st.error("Invalid role specified.")
                                            st.stop()
                                    else:
                                        # Self-registered users are always admins
                                        st.session_state.user_role = "admin"
                                        st.session_state.employee_id = employee_id
                                        st.session_state.organization_id = None
                                        st.session_state.organization_name = None
                                        st.session_state.organization_selected = False
                                        st.session_state.redirect_to_org_management = True
                                        success_msg = "Registration successful! You've been automatically logged in as an admin. Please create your organization to get started."

                                    st.success(success_msg)
                                    # Set redirect flag for admin users
                                    st.session_state.redirect_to_org_management = (invitation.get("role") == "admin")

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
                # More user-friendly error message
                st.error("This invitation link appears to be invalid or has expired.")
                # Provide help without exposing technical details
                st.info("Need help? Here are some options:")
                st.markdown("""
                1. Check if you're using the complete invitation link from your email
                2. The invitation might have expired (they're valid for 7 days)
                3. Contact the person who sent you the invitation for a new link
                """)
                
                # Log technical details to console for debugging
                print(f"Token verification failed for: {token}")
                
                # Check if the token exists in invitations.csv but don't display to user
                from email_manager import ensure_invitations_file
                invitations_df = ensure_invitations_file()
                invitations_df["token"] = invitations_df["token"].astype(str)
                token_str = str(token).strip()
                
                if token_str in invitations_df["token"].values:
                    invitation_row = invitations_df[invitations_df["token"] == token_str].iloc[0]
                    print(f"Found invitation in DB: Status = {invitation_row['status']}, Expires at = {invitation_row['expires_at']}")
                    
                    # Check expiration for console logs
                    import datetime
                    now = datetime.datetime.now()
                    expires_at = datetime.datetime.strptime(invitation_row["expires_at"], "%Y-%m-%d %H:%M:%S")
                    is_expired = now > expires_at
                    print(f"Current time: {now}, Expiration time: {expires_at}, Is expired: {is_expired}")
                    
                    # Add a button to request a new invitation
                    if st.button("Request a new invitation"):
                        st.session_state.show_request_form = True
                        st.rerun()
                else:
                    print(f"Token {token_str} not found in invitation database.")
                
                # Clear query params to avoid repeated processing
                st.query_params.clear()


# User authentication
def display_login():
    # Hide the sidebar on login page
    from ui_helpers import hide_sidebar
    hide_sidebar()
    
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
        
        login_tab1, login_tab2 = st.tabs(
            ["Account Login", "Sign in"])

        with login_tab1:
            username = st.text_input("Username", key="username_login", placeholder="Enter your username")
            password = st.text_input("Password",
                                    type="password",
                                    key="password_login",
                                    placeholder="Enter your password")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Login", type="primary", key="login_button", use_container_width=True):
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

                # Note: Job information section has been removed
                # All users registering through this form will be assigned as Admins
                                            
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

                    # No manager ID needed as all users from registration are admins
                    manager_id = None

                    # Skip organization selection during initial registration
                    # Organization setup will happen after email verification
                    # We'll set organization_id to None for now
                    organization_id = None

                    # First, create an invitation token and send verification email
                    from email_manager import create_invitation, send_invitation_email
                    
                    # Create invitation with admin role
                    success, message, token = create_invitation(
                        username=reg_username,
                        email=reg_email,
                        role="admin",  # All users from registration form are admins
                        organization_id=organization_id,
                        expiry_days=7
                    )
                    
                    if success:
                        # Send verification email
                        email_sent, email_message = send_invitation_email(
                            email=reg_email,
                            token=token,
                            name=reg_name,
                            organization_name=None  # Organization will be set after email confirmation
                        )
                        
                        if email_sent:
                            st.success(f"Verification email sent to {reg_email}. Please check your inbox to complete registration.")
                            
                            # Also display the invitation link as fallback
                            base_url = 'https://skilltracker.replit.app'
                            invite_url = f"{base_url}/?token={token}"
                            st.markdown(f"If you don't receive the email, you can use this link: [Accept Invitation]({invite_url})")
                            
                            # Skip automatic login since verification is required
                            st.stop()
                        else:
                            # If email fails, proceed with direct registration but show the error
                            st.warning(f"Failed to send verification email: {email_message}")
                            st.warning("You can continue with direct registration.")
                            
                            # Create user account with admin role
                            user_success, user_message = add_user(
                                username=reg_username,
                                password=reg_password,
                                role="admin",  # Admin role for direct registrations
                                name=reg_name,
                                email=reg_email)
                            
                            if user_success:
                                # Create employee record with organization (minimal info)
                                employee_success, employee_message, employee_id = add_employee(
                                    name=reg_name,
                                    email=reg_email,
                                    job_title="Admin",  # Default job title
                                    job_level="",
                                    department="",
                                    manager_id=None,
                                    organization_id=organization_id  # Link to organization
                                )
                                
                                if employee_success:
                                    # Automatically log in the new user
                                    st.session_state.authenticated = True
                                    st.session_state.username = reg_username
                                    st.session_state.user_role = "admin"
                                    st.session_state.employee_id = employee_id
                                    
                                    # Set the organization properly
                                    if organization_id:
                                        # Get the organization name
                                        from data_manager import get_organization
                                        org_data = get_organization(organization_id)
                                        if org_data is not None:
                                            # Set both organization ID and name
                                            st.session_state.organization_id = int(organization_id)
                                            st.session_state.organization_name = org_data.get("name", "")
                                            st.session_state.organization_selected = True
                                    
                                    st.success(
                                        "Registration successful! You've been automatically logged in. "
                                        "You will be redirected to Organization Management."
                                    )
                                    # Set the flag for redirection to Organization Management
                                    st.session_state.redirect_to_org_management = True
                                    st.rerun()
                                else:
                                    st.error("Failed to create employee record")
                            else:
                                st.error("Failed to create user account")
                    else:
                        st.error(f"Failed to create invitation: {message}")
                        # Fallback to direct registration
                        user_success, user_message = add_user(
                            username=reg_username,
                            password=reg_password,
                            role="admin",  # Admin role for direct registrations
                            name=reg_name,
                            email=reg_email)
                        
                        if user_success:
                            # Create employee record with organization (minimal info)
                            employee_success, employee_message, employee_id = add_employee(
                                name=reg_name,
                                email=reg_email,
                                job_title="Admin",  # Default job title
                                job_level="",
                                department="",
                                manager_id=None,
                                organization_id=organization_id  # Link to organization
                            )
                            
                            if employee_success:
                                # Automatically log in the new user
                                st.session_state.authenticated = True
                                st.session_state.username = reg_username
                                st.session_state.user_role = "admin"
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
                                    "Registration successful! You've been automatically logged in. "
                                    "You will be redirected to Organization Management."
                                )
                                # Set the flag for redirection to Organization Management
                                st.session_state.redirect_to_org_management = True
                                st.rerun()
                            else:
                                st.error("Failed to create employee record")
                        else:
                            st.error("Failed to create user account")


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
    """Displays the main dashboard page"""
    # Initialize session state for page tracking
    current_page = track_page_load()
    
    # Add the custom sidebar navigation
    create_custom_sidebar()
    
    # Home Page Content
    st.title("Dashboard")

    # Display overview based on role with direct page links
    if st.session_state.user_role == "admin":
        st.subheader("Admin Dashboard")
        
        st.info("""
        As an administrator, you can:
        - Set up and manage the competency framework
        - Create and modify skills within competencies
        - Define expected skill levels for each role/position
        - Add and manage users
        - View team and individual performance
        """)

    elif st.session_state.user_role == "manager":
        st.subheader("Manager Dashboard")
        
        st.info("""
        As a manager, you can:
        - Evaluate team members' skills
        - View individual and team performance metrics
        - Compare performance against expected levels
        - Generate and export reports
        """)

    elif st.session_state.user_role == "employee":
        st.subheader("Employee Dashboard")
        
        st.info("""
        As an employee, you can:
        - Complete self-assessments of your skills
        - View your performance metrics and manager feedback
        - Compare your current skills with expected levels
        - Track your progress over time
        """)

    elif st.session_state.user_role == "email_user":
        # Display email user dashboard
        employee_email = st.session_state.employee_email
        employees_df = load_data("employees")
        employee = employees_df[employees_df["email"] == employee_email]

        if not employee.empty:
            employee_name = employee.iloc[0]["name"]
            st.subheader(f"Self-Assessment Portal for {employee_name}")
            
            st.info(f"""
            Welcome to your self-assessment portal. Here you can:
            - Complete skill self-assessments
            - View your current skills and ratings
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
    # Initialize session state for page tracking
    current_page = track_page_load()
    
    # Add the custom sidebar navigation if the user is authenticated
    if st.session_state.authenticated:
        create_custom_sidebar()
        
    st.title("Organization Selection")

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
        # Get the organization of the admin who created this user
        from data_manager import load_data
        users_df = load_data("users")
        if not users_df.empty:
            user = users_df[users_df["username"] == st.session_state.username]
            if not user.empty:
                user_email = user.iloc[0]["email"]
                # Find the user in employees table to get their organization
                employees_df = load_data("employees")
                if not employees_df.empty:
                    employee = employees_df[employees_df["email"] == user_email]
                    if not employee.empty and pd.notnull(employee.iloc[0]["organization_id"]):
                        org_id = int(employee.iloc[0]["organization_id"])
                        orgs_df = get_organizations()
                        if not orgs_df.empty:
                            org = orgs_df[orgs_df["organization_id"] == org_id]
                            if not org.empty:
                                st.session_state.organization_id = org_id
                                st.session_state.organization_name = org.iloc[0]["name"]
                                st.session_state.organization_selected = True
                                st.rerun()

        st.warning(
            "You don't have access to any organizations. Please contact an administrator."
        )

        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            initialize_session_state()
            st.rerun()


# Top navigation is already imported at the top of the file

# Delete LearnUpon organization data
from data_manager import delete_organization
success, message = delete_organization(1, force_delete=True)

# Check for logout in query parameters
if "logout" in st.query_params and st.query_params["logout"] == "true":
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()
    # Clear query parameters
    st.query_params.clear()
    st.rerun()

# Application flow
# First, check for invitation tokens
handle_invitation()

# Regular application flow
if not st.session_state.authenticated:
    display_login()
elif not st.session_state.get("organization_selected", False):
    # No navigation - removed as requested
    display_organization_selector()
else:
    # Check if we need to redirect to Organization Management
    if st.session_state.get("redirect_to_org_management", False) and st.session_state.user_role == "admin":
        # Clear the flag
        st.session_state.redirect_to_org_management = False
        # Redirect to Organization Management page
        st.switch_page("pages/06_Organization_Management.py")
    else:
        # No navigation - removed as requested
        main_app()
