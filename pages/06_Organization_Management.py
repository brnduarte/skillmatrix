import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Organization Management",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import os
from utils import initialize_session_state, check_permission, check_page_access, get_current_organization_id
from data_manager import get_organizations, add_organization, update_organization, delete_organization, get_user_organizations

# Load custom CSS
with open(os.path.join('.streamlit', 'style.css')) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state variables
initialize_session_state()

# This page is accessible only to admins


# Check if user is logged in
if not st.session_state.authenticated:
    st.warning("Please log in to access this page.")
    st.stop()

# Check if user has admin permissions
if not check_permission("admin"):
    st.error("You don't have permission to access this page. Admin access required.")
    st.stop()

st.title("Organization Management")
st.write("Add, update, or delete organizations in the system.")

# Main interface
tab1, tab2, tab3 = st.tabs(["View Organizations", "Add Organization", "Manage Organizations"])

with tab1:
    st.header("All Organizations")
    
    # Get all organizations
    orgs_df = get_organizations()
    
    if orgs_df.empty:
        st.warning("No organizations found in the system.")
    else:
        # Display organizations in a table
        st.dataframe(orgs_df[["organization_id", "name", "created_by", "created_at"]])
        
        # Show counts of items in each organization
        st.subheader("Organization Statistics")
        
        try:
            from data_manager import load_data_for_organization
            
            for _, org in orgs_df.iterrows():
                org_id = org["organization_id"]
                org_name = org["name"]
                
                employees = load_data_for_organization("employees", org_id)
                competencies = load_data_for_organization("competencies", org_id)
                skills = load_data_for_organization("skills", org_id)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(f"{org_name} - Employees", len(employees))
                    
                with col2:
                    st.metric(f"{org_name} - Competencies", len(competencies))
                    
                with col3:
                    st.metric(f"{org_name} - Skills", len(skills))
                
                st.divider()
        except Exception as e:
            st.error(f"Error retrieving organization statistics: {str(e)}")

with tab2:
    st.header("Add New Organization")
    
    # Form for adding new organization
    with st.form(key="add_organization_form"):
        org_name = st.text_input("Organization Name", placeholder="Enter organization name")
        
        submit_button = st.form_submit_button(label="Create Organization")
        
        if submit_button:
            if not org_name:
                st.error("Please enter an organization name.")
            else:
                success, message, org_id = add_organization(org_name, st.session_state.username)
                
                if success:
                    st.success(f"Organization '{org_name}' created successfully!")
                else:
                    st.error(f"Failed to create organization: {message}")

with tab3:
    st.header("Manage Organizations")
    
    # Get all organizations for management
    orgs_df = get_organizations()
    
    if orgs_df.empty:
        st.warning("No organizations to manage.")
    else:
        # Select organization to manage
        org_options = list(zip(orgs_df["organization_id"].astype(str), orgs_df["name"]))
        selected_org = st.selectbox(
            "Select organization to manage", 
            options=org_options,
            format_func=lambda x: x[1],
            key="manage_org_select"
        )
        
        if selected_org:
            org_id = int(selected_org[0])
            org_name = selected_org[1]
            
            st.subheader(f"Managing: {org_name}")
            
            # Management options
            option_tab1, option_tab2 = st.tabs(["Update Organization", "Delete Organization"])
            
            with option_tab1:
                # Form for updating organization
                with st.form(key="update_organization_form"):
                    new_name = st.text_input("New Organization Name", value=org_name)
                    
                    update_button = st.form_submit_button(label="Update Organization")
                    
                    if update_button:
                        if not new_name:
                            st.error("Please enter an organization name.")
                        elif new_name == org_name:
                            st.info("No changes made to organization name.")
                        else:
                            success, message = update_organization(org_id, new_name)
                            
                            if success:
                                st.success(f"Organization updated to '{new_name}' successfully!")
                            else:
                                st.error(f"Failed to update organization: {message}")
            
            with option_tab2:
                st.warning("Deleting an organization will permanently remove it and all its data!")
                
                # Get confirmation for deletion
                confirm_delete = st.text_input(
                    "Type the organization name to confirm deletion",
                    placeholder=f"Type '{org_name}' to confirm"
                )
                
                # Option to force delete all associated data
                force_delete = st.checkbox(
                    "Force delete all associated data (employees, competencies, skills, assessments, etc.)",
                    help="Warning: This will delete all data associated with this organization. This action cannot be undone."
                )
                
                if st.button("Delete Organization", key="delete_org_button"):
                    if confirm_delete != org_name:
                        st.error("Organization name does not match. Deletion canceled.")
                    else:
                        success, message = delete_organization(org_id, force_delete)
                        
                        if success:
                            st.success(f"Organization '{org_name}' deleted successfully!")
                            # Reset the current organization if it was the one deleted
                            if st.session_state.organization_id == org_id:
                                st.session_state.organization_id = None
                                st.session_state.organization_name = None
                                st.session_state.organization_selected = False
                        else:
                            st.error(f"Failed to delete organization: {message}")
                            
                        # If force delete was not selected but needed, show helpful message
                        if not success and not force_delete and "Use force_delete" in message:
                            st.info("This organization has associated data. Check the 'Force delete' option above to delete the organization and all its data.")