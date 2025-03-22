import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="User Management",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import os
from utils import initialize_session_state, check_permission
from data_manager import load_data, save_data

# Load custom CSS
with open(os.path.join('.streamlit', 'style.css')) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state variables
initialize_session_state()

# Check if user is logged in
if not st.session_state.authenticated:
    st.warning("Please log in to access this page.")
    st.stop()

# Check if user has admin permissions
if not check_permission("admin"):
    st.error("You don't have permission to access this page. Admin access required.")
    st.stop()

st.title("User Management")
st.write("Manage users in the system. Add, update, or delete user accounts.")

# Main interface
tab1, tab2, tab3 = st.tabs(["View Users", "Add User", "Edit/Delete User"])

with tab1:
    st.header("All Users")
    
    # Load users data
    users_df = load_data("users")
    
    if users_df.empty:
        st.warning("No users found in the system.")
    else:
        # Display users in a table
        st.dataframe(users_df[["username", "role", "name", "email"]])
        
        # Show employee associations
        st.subheader("Employee Associations")
        
        try:
            employees_df = load_data("employees")
            
            if not employees_df.empty:
                # Join users with employees on email
                user_employee_df = pd.merge(
                    users_df[["username", "email", "role", "name"]],
                    employees_df[["employee_id", "email", "job_title", "job_level", "department", "organization_id"]],
                    on="email",
                    how="left"
                )
                
                # Display the associations
                st.dataframe(user_employee_df[[
                    "username", "name", "role", "email", "employee_id", 
                    "job_title", "job_level", "department", "organization_id"
                ]])
            else:
                st.info("No employees found in the system.")
        except Exception as e:
            st.error(f"Error retrieving employee associations: {str(e)}")

with tab2:
    st.header("Add New User")
    
    # User roles
    user_roles = ["admin", "manager", "employee"]
    
    # Form for adding new user
    with st.form(key="add_user_form"):
        st.subheader("Basic Information")
        username = st.text_input("Username", key="new_username")
        password = st.text_input("Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_new_password")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", key="new_name")
        with col2:
            email = st.text_input("Email", key="new_email")
        
        role = st.selectbox("User Role", options=user_roles, key="new_role")
        
        # Add employee record option
        create_employee = st.checkbox("Create Employee Record", value=True)
        
        if create_employee:
            st.subheader("Employee Information")
            
            job_title = st.text_input("Job Title", key="new_job_title")
            
            # Get job levels for dropdown
            job_levels_df = load_data("levels")
            job_level_options = [""] + job_levels_df["name"].tolist() if not job_levels_df.empty else [""]
            job_level = st.selectbox("Job Level", options=job_level_options, key="new_job_level")
            
            department = st.text_input("Department", key="new_department")
            
            # Get managers for dropdown
            employees_df = load_data("employees")
            managers = employees_df[["employee_id", "name"]].copy()
            manager_options = [("", "None")] + list(zip(managers["employee_id"].astype(str), managers["name"])) if not employees_df.empty else [("", "None")]
            manager_id = st.selectbox("Manager", options=manager_options, format_func=lambda x: x[1], key="new_manager_id")
            
            # Get organizations for dropdown
            from data_manager import get_organizations
            orgs_df = get_organizations()
            if not orgs_df.empty:
                # Ensure organization_id is properly formatted as a string
                orgs_df["organization_id"] = orgs_df["organization_id"].apply(lambda x: str(int(float(x))) if pd.notnull(x) else "")
                org_options = list(zip(orgs_df["organization_id"], orgs_df["name"]))
            else:
                org_options = []
            
            organization = st.selectbox("Organization", options=org_options, format_func=lambda x: x[1], key="new_org_id")
        
        submit_button = st.form_submit_button(label="Add User")
        
        if submit_button:
            # Validate form
            if not username or not password or not name or not email:
                st.error("Please fill in all required fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif "@" not in email or "." not in email:
                st.error("Please enter a valid email address.")
            else:
                # Check if username already exists
                existing_user = users_df[users_df["username"] == username]
                if not existing_user.empty:
                    st.error(f"Username '{username}' already exists.")
                else:
                    try:
                        from data_manager import add_user, add_employee
                        
                        # Add user
                        user_success, user_message = add_user(
                            username=username,
                            password=password,
                            role=role,
                            name=name,
                            email=email
                        )
                        
                        if user_success:
                            st.success(f"User '{username}' added successfully!")
                            
                            # Add employee record if selected
                            if create_employee:
                                # Extract manager_id (first element of the tuple)
                                manager_id_value = manager_id[0] if manager_id and manager_id[0] else None
                                
                                # Extract organization_id (first element of the tuple)
                                organization_id = None
                                if organization and organization[0]:
                                    # Handle potential float strings like '1.0'
                                    try:
                                        # First convert to float, then to int to handle '1.0' values
                                        organization_id = int(float(organization[0]))
                                    except (ValueError, TypeError):
                                        st.error(f"Invalid organization ID format: {organization[0]}")
                                        organization_id = None
                                
                                employee_success, employee_message, employee_id = add_employee(
                                    name=name,
                                    email=email,
                                    job_title=job_title,
                                    job_level=job_level,
                                    department=department,
                                    manager_id=manager_id_value,
                                    organization_id=organization_id
                                )
                                
                                if employee_success:
                                    st.success(f"Employee record created (ID: {employee_id}).")
                                else:
                                    st.error(f"Failed to create employee record: {employee_message}")
                        else:
                            st.error(f"Failed to add user: {user_message}")
                    except Exception as e:
                        st.error(f"Error adding user: {str(e)}")

with tab3:
    st.header("Edit or Delete User")
    
    # Select user to manage
    if users_df.empty:
        st.warning("No users to manage.")
    else:
        selected_username = st.selectbox(
            "Select a user to manage", 
            options=users_df["username"].tolist(),
            key="manage_user_select"
        )
        
        if selected_username:
            user = users_df[users_df["username"] == selected_username].iloc[0]
            
            st.subheader(f"Managing: {user['name']} ({selected_username})")
            
            # Management options
            option_tab1, option_tab2 = st.tabs(["Update User", "Delete User"])
            
            with option_tab1:
                # Form for updating user
                with st.form(key="update_user_form"):
                    st.subheader("Update Information")
                    
                    update_password = st.checkbox("Update Password")
                    
                    if update_password:
                        new_password = st.text_input("New Password", type="password", key="update_password")
                        confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_update_password")
                    
                    update_name = st.text_input("Full Name", value=user["name"], key="update_name")
                    update_email = st.text_input("Email", value=user["email"], key="update_email")
                    
                    update_role = st.selectbox(
                        "User Role", 
                        options=user_roles,
                        index=user_roles.index(user["role"]) if user["role"] in user_roles else 0,
                        key="update_role"
                    )
                    
                    update_button = st.form_submit_button(label="Update User")
                    
                    if update_button:
                        try:
                            # Validate form
                            if update_password and new_password != confirm_new_password:
                                st.error("New passwords do not match.")
                            elif not update_name or not update_email:
                                st.error("Name and email are required fields.")
                            elif "@" not in update_email or "." not in update_email:
                                st.error("Please enter a valid email address.")
                            else:
                                # Update user record
                                user_copy = users_df.copy()
                                user_idx = user_copy.index[user_copy["username"] == selected_username].tolist()[0]
                                
                                user_copy.at[user_idx, "name"] = update_name
                                user_copy.at[user_idx, "email"] = update_email
                                user_copy.at[user_idx, "role"] = update_role
                                
                                if update_password:
                                    user_copy.at[user_idx, "password"] = new_password
                                
                                save_data("users", user_copy)
                                st.success(f"User '{selected_username}' updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating user: {str(e)}")
            
            with option_tab2:
                st.warning("Deleting a user will permanently remove their account!")
                
                # Don't allow deleting the last admin
                is_last_admin = user["role"] == "admin" and len(users_df[users_df["role"] == "admin"]) <= 1
                
                if is_last_admin:
                    st.error("Cannot delete the last admin user. Create another admin user first.")
                else:
                    # Get confirmation for deletion
                    confirm_delete = st.text_input(
                        "Type the username to confirm deletion",
                        placeholder=f"Type '{selected_username}' to confirm"
                    )
                    
                    # Check if user has associated employee record
                    employees_df = load_data("employees")
                    has_employee = not employees_df.empty and any(employees_df["email"] == user["email"])
                    
                    delete_employee_too = st.checkbox("Also delete associated employee record", value=True) if has_employee else False
                    
                    if st.button("Delete User", key="delete_user_button"):
                        if confirm_delete != selected_username:
                            st.error("Username does not match. Deletion canceled.")
                        else:
                            try:
                                # Delete associated employee record if selected
                                if has_employee and delete_employee_too:
                                    from data_manager import delete_employee
                                    
                                    # Get employee ID
                                    employee = employees_df[employees_df["email"] == user["email"]].iloc[0]
                                    employee_id = employee["employee_id"]
                                    
                                    # Delete employee
                                    try:
                                        # Convert employee_id to appropriate type if needed
                                        if isinstance(employee_id, str) and '.' in employee_id:
                                            employee_id = int(float(employee_id))
                                        elif isinstance(employee_id, float):
                                            employee_id = int(employee_id)
                                            
                                        employee_success = delete_employee(employee_id)
                                    except (ValueError, TypeError) as e:
                                        st.error(f"Error converting employee ID: {str(e)}")
                                        employee_success = False
                                    
                                    if not employee_success:
                                        st.error("Failed to delete associated employee record.")
                                
                                # Delete user
                                user_copy = users_df.copy()
                                user_copy = user_copy[user_copy["username"] != selected_username]
                                save_data("users", user_copy)
                                
                                st.success(f"User '{selected_username}' deleted successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting user: {str(e)}")