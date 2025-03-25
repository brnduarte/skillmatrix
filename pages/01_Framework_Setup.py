import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Framework Setup - Skill Matrix",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
from data_manager import (
    load_data, load_data_for_organization, save_data, add_competency, add_skill, 
    add_job_level, set_skill_expectation, set_competency_expectation, get_competency_skills,
    delete_competency, delete_skill, delete_job_level, delete_employee,
    delete_expectation, delete_competency_expectation, update_competency, update_skill, update_job_level,
    update_employee
)
from utils import get_current_organization_id, check_page_access, initialize_session_state, check_permission, track_page_load
from ui_helpers import load_custom_css, create_custom_sidebar

# Load custom CSS for consistent styling
load_custom_css()

# Track current page for navigation highlighting
current_page = track_page_load()

# Initialize session state and check if user is authenticated
state = initialize_session_state()

# Check if user has selected an organization
if not state["organization_selected"]:
    st.warning("Please select an organization to continue.")
    st.switch_page("app.py")
    st.stop()

# Check page access
if not check_page_access(["admin"]):
    st.stop()

# Check if user has access to this page (admin only)


st.title("Competency Framework Setup")
st.write("Configure competencies, skills, job levels, and expected scores for your organization.")

# Create tabs for different setup sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Competencies & Skills", 
    "Job Levels", 
    "Skill Expectations",
    "Competency Expectations",
    "Manage Employees"
])

# Competencies & Skills Tab
with tab1:
    st.header("Competencies & Skills")
    
    # Action buttons row
    col1, col2 = st.columns([1, 1])
    
    with col1:
        show_add_competency = st.button("➕ Add New Competency", type="primary", key="show_add_comp_btn")
    
    with col2:
        show_add_skill = st.button("➕ Add New Skill", type="primary", key="show_add_skill_btn")
    
    # Create session state variables if they don't exist
    if "show_add_competency_form" not in st.session_state:
        st.session_state.show_add_competency_form = False
    
    if "show_add_skill_form" not in st.session_state:
        st.session_state.show_add_skill_form = False
    
    # Toggle form visibility when buttons are clicked
    if show_add_competency:
        st.session_state.show_add_competency_form = not st.session_state.show_add_competency_form
        # Close the other form when this one is opened
        if st.session_state.show_add_competency_form:
            st.session_state.show_add_skill_form = False
    
    if show_add_skill:
        st.session_state.show_add_skill_form = not st.session_state.show_add_skill_form
        # Close the other form when this one is opened
        if st.session_state.show_add_skill_form:
            st.session_state.show_add_competency_form = False
    
    # Display add competency form as a modal if active
    if st.session_state.show_add_competency_form:
        # Create a modal using Streamlit's container with border
        with st.container(border=True):
            st.subheader("Add New Competency")
            comp_name = st.text_input("Competency Name", key="comp_name_input")
            comp_desc = st.text_area("Description", key="comp_desc_input")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_comp = st.button("Save", type="primary", key="submit_comp_btn")
            with col2:
                cancel_comp = st.button("Cancel", key="cancel_comp_btn")
            
            if submit_comp:
                if comp_name:
                    success, message, _ = add_competency(comp_name, comp_desc)
                    if success:
                        st.success(message)
                        st.session_state.show_add_competency_form = False
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a competency name")
            
            if cancel_comp:
                st.session_state.show_add_competency_form = False
                st.rerun()
    
    # Display add skill form as a modal if active
    if st.session_state.show_add_skill_form:
        organization_id = get_current_organization_id()
        competencies_df = load_data_for_organization("competencies", organization_id)
        
        if competencies_df.empty:
            st.warning("You need to add competencies first.")
            st.session_state.show_add_skill_form = False
        else:
            # Create a modal using Streamlit's container with border
            with st.container(border=True):
                st.subheader("Add New Skill")
                
                comp_options = competencies_df["name"].tolist()
                selected_comp = st.selectbox("Select Competency", comp_options, key="add_skill_comp_select")
                
                # Get the competency ID
                selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]
                
                skill_name = st.text_input("Skill Name", key="skill_name_input")
                skill_desc = st.text_area("Skill Description", key="skill_desc_input")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    submit_skill = st.button("Save", type="primary", key="submit_skill_btn")
                with col2:
                    cancel_skill = st.button("Cancel", key="cancel_skill_btn")
                
                if submit_skill:
                    if skill_name:
                        success, message, _ = add_skill(selected_comp_id, skill_name, skill_desc)
                        if success:
                            st.success(message)
                            st.session_state.show_add_skill_form = False
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter a skill name")
                
                if cancel_skill:
                    st.session_state.show_add_skill_form = False
                    st.rerun()
    
    # View existing competencies with edit/delete options
    st.subheader("Existing Competencies")
    organization_id = get_current_organization_id()
    competencies_df = load_data_for_organization("competencies", organization_id)
    skills_df = load_data_for_organization("skills", organization_id)
    
    # Add filter options
    filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])
    with filter_col1:
        filter_type = st.selectbox("Filter By", ["All Competencies", "Search by Name"], key="competency_filter_type")
    
    with filter_col2:
        if filter_type == "Search by Name":
            search_term = st.text_input("Enter competency name", key="competency_search")
            if search_term:
                filtered_comp_df = competencies_df[competencies_df["name"].str.contains(search_term, case=False)]
            else:
                filtered_comp_df = competencies_df
        else:
            filtered_comp_df = competencies_df
    
    # Display management instructions
    st.info("Use the table below to manage competencies and skills.")
    
    if not competencies_df.empty:
        # Display competencies in a table format
        
        # Display headers
        header_cols = st.columns([3, 5, 1, 1])
        with header_cols[0]:
            st.markdown("**Name**")
        with header_cols[1]:
            st.markdown("**Description**")
        with header_cols[2]:
            st.markdown("**Edit**")
        with header_cols[3]:
            st.markdown("**Delete**")
        
        st.markdown("---")
        
        # Display each competency row (filtered)
        for _, comp_row in filtered_comp_df.iterrows():
            comp_id = comp_row["competency_id"]
            comp_cols = st.columns([3, 5, 1, 1])
            
            with comp_cols[0]:
                st.write(f"{comp_row['name']} (ID: {comp_id})")
            
            with comp_cols[1]:
                st.write(f"{comp_row['description']}")
            
            with comp_cols[2]:
                # Edit competency button
                if st.button("✏️", key=f"edit_comp_{comp_id}"):
                    # Set session state to store the competency being edited
                    st.session_state[f"edit_comp_id_{comp_id}"] = True
            
            with comp_cols[3]:
                # Delete competency button
                if st.button("🗑️", key=f"del_comp_{comp_id}"):
                    success, message = delete_competency(comp_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            # Display edit form as a modal if the edit button was clicked
            if st.session_state.get(f"edit_comp_id_{comp_id}", False):
                # Create a modal using Streamlit's container with border
                with st.container(border=True):
                    st.markdown("### Edit Competency")
                    new_name = st.text_input("Name", value=comp_row["name"], key=f"comp_name_{comp_id}")
                    new_desc = st.text_area("Description", value=comp_row["description"], key=f"comp_desc_{comp_id}")
                    
                    edit_col1, edit_col2 = st.columns([1, 1])
                    with edit_col1:
                        if st.button("Save", type="primary", key=f"save_comp_{comp_id}"):
                            success, message = update_competency(comp_id, new_name, new_desc)
                            if success:
                                st.success(message)
                                # Clear the editing state
                                st.session_state.pop(f"edit_comp_id_{comp_id}", None)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with edit_col2:
                        if st.button("Cancel", key=f"cancel_comp_{comp_id}"):
                            # Clear the editing state
                            st.session_state.pop(f"edit_comp_id_{comp_id}", None)
                            st.rerun()
        
        # Skills section
        st.subheader("Skills")

        # Display add skill form as a modal if active
        if st.session_state.show_add_skill_form:
            organization_id = get_current_organization_id()
            competencies_df = load_data_for_organization("competencies", organization_id)

            if competencies_df.empty:
                st.warning("You need to add competencies first.")
                st.session_state.show_add_skill_form = False
            else:
                # Create a modal using Streamlit's container with border
                with st.container(border=True):
                    st.subheader("Add New Skill")

                    comp_options = competencies_df["name"].tolist()
                    selected_comp = st.selectbox("Select Competency", comp_options, key="add_skill_comp_select")

        
        # Filter options
        filter_col1, filter_col2 = st.columns(2)
        
        # Get all skills for the dropdown
        all_skills_df = skills_df.copy()
        
        with filter_col1:
            if not all_skills_df.empty:
                # Create a "Select Skill" filter dropdown with "All Skills" option
                skill_options = ["All Skills"] + all_skills_df["name"].tolist()
                selected_skill_name = st.selectbox(
                    "Select Skill",
                    skill_options,
                    key="skill_filter"
                )
                
                # Filter based on selected skill
                if selected_skill_name == "All Skills":
                    st.markdown("#### All Skills")
                    filtered_skills = skills_df
                else:
                    st.markdown(f"#### Skill: {selected_skill_name}")
                    filtered_skills = skills_df[skills_df["name"] == selected_skill_name]
            else:
                st.info("No skills have been added yet.")
                filtered_skills = pd.DataFrame()
        
        # Add text search filter
        with filter_col2:
            if not filtered_skills.empty:
                search_skill = st.text_input("Search skills by name", key="skill_search")
                if search_skill:
                    filtered_skills = filtered_skills[filtered_skills["name"].str.contains(search_skill, case=False)]
        
        if not filtered_skills.empty:
            # Display skills in a table format
            
            # Display headers
            skill_header_cols = st.columns([2, 2, 3, 1, 1])
            with skill_header_cols[0]:
                st.markdown("**Skill Name**")
            with skill_header_cols[1]:
                st.markdown("**Competency**")
            with skill_header_cols[2]:
                st.markdown("**Description**")
            with skill_header_cols[3]:
                st.markdown("**Edit**")
            with skill_header_cols[4]:
                st.markdown("**Delete**")
            
            st.markdown("---")
            
            # Display each skill row (filtered)
            for _, skill_row in filtered_skills.iterrows():
                skill_id = skill_row["skill_id"]
                # Get competency name for this skill
                comp_id = skill_row['competency_id']
                comp_name = competencies_df[competencies_df['competency_id'] == comp_id]['name'].iloc[0] if comp_id in competencies_df['competency_id'].values else "Unknown"
                
                skill_cols = st.columns([2, 2, 3, 1, 1])
                
                with skill_cols[0]:
                    st.write(f"{skill_row['name']}")
                    
                with skill_cols[1]:
                    st.write(f"{comp_name}")
                
                with skill_cols[2]:
                    st.write(f"{skill_row['description']}")
                
                with skill_cols[3]:
                    # Edit skill button
                    if st.button("✏️", key=f"edit_skill_{skill_id}"):
                        # Set session state to store the skill being edited
                        st.session_state[f"edit_skill_id_{skill_id}"] = True
                
                with skill_cols[4]:
                    # Delete skill button
                    if st.button("🗑️", key=f"del_skill_{skill_id}"):
                        success, message = delete_skill(skill_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                # Display edit form as a modal if the edit button was clicked
                if st.session_state.get(f"edit_skill_id_{skill_id}", False):
                    # Create a modal using Streamlit's container with border
                    with st.container(border=True):
                        st.markdown("### Edit Skill")
                        new_skill_name = st.text_input("Name", value=skill_row["name"], key=f"skill_name_{skill_id}")
                        new_skill_desc = st.text_area("Description", value=skill_row["description"], key=f"skill_desc_{skill_id}")
                        
                        skill_edit_col1, skill_edit_col2 = st.columns([1, 1])
                        with skill_edit_col1:
                            if st.button("Save", type="primary", key=f"save_skill_{skill_id}"):
                                success, message = update_skill(skill_id, new_skill_name, new_skill_desc)
                                if success:
                                    st.success(message)
                                    # Clear the editing state
                                    st.session_state.pop(f"edit_skill_id_{skill_id}", None)
                                    st.rerun()
                                else:
                                    st.error(message)
                        
                        with skill_edit_col2:
                            if st.button("Cancel", key=f"cancel_skill_{skill_id}"):
                                # Clear the editing state
                                st.session_state.pop(f"edit_skill_id_{skill_id}", None)
                                st.rerun()
        else:
            st.info("No skills match your filter criteria.")
    else:
        st.info("No competencies added yet.")

# Job Levels Tab
with tab2:
    st.header("Job Levels")
    
    # Add button for new job level
    show_add_level = st.button("➕ Add New Job Level", type="primary", key="show_add_level_btn")
    
    # Create session state variable if it doesn't exist
    if "show_add_level_form" not in st.session_state:
        st.session_state.show_add_level_form = False
    
    # Toggle form visibility when button is clicked
    if show_add_level:
        st.session_state.show_add_level_form = not st.session_state.show_add_level_form
    
    # Display add job level form as a modal if active
    if st.session_state.show_add_level_form:
        # Create a modal using Streamlit's container with border
        with st.container(border=True):
            st.subheader("Add New Job Level")
            level_name = st.text_input("Level Name", key="level_name_input")
            level_desc = st.text_area("Level Description", key="level_desc_input")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_level = st.button("Save", type="primary", key="submit_level_btn")
            with col2:
                cancel_level = st.button("Cancel", key="cancel_level_btn")
            
            if submit_level:
                if level_name:
                    success, message, _ = add_job_level(level_name, level_desc)
                    if success:
                        st.success(message)
                        st.session_state.show_add_level_form = False
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a job level name")
            
            if cancel_level:
                st.session_state.show_add_level_form = False
                st.rerun()
    
    # Display existing job levels section
    st.markdown("---")
    st.subheader("Existing Job Levels")
    organization_id = get_current_organization_id()
    levels_df = load_data_for_organization("levels", organization_id)
    
    if not levels_df.empty:
        # Add filter options
        filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])
        with filter_col1:
            filter_type = st.selectbox("Filter By", ["All Levels", "Search by Name", "Filter by Skill"], key="level_filter_type")
        
        # Load skills data and expectations data for filtering
        skills_df = load_data_for_organization("skills", organization_id)
        competencies_df = load_data_for_organization("competencies", organization_id)
        expectations_df = load_data_for_organization("expectations", organization_id)
        
        # Define selected_skill with a default value
        selected_skill = "All Skills"
        
        with filter_col2:
            if filter_type == "Search by Name":
                search_term = st.text_input("Enter level name", key="level_search")
                if search_term:
                    filtered_levels_df = levels_df[levels_df["name"].str.contains(search_term, case=False)]
                else:
                    filtered_levels_df = levels_df
            elif filter_type == "Filter by Skill":
                # If we have skills data, create a dropdown for skills
                if not skills_df.empty:
                    skill_options = ["All Skills"] + skills_df["name"].tolist()
                    selected_skill = st.selectbox("Select Skill", skill_options, key="level_skill_filter")
                    
                    if selected_skill != "All Skills" and not expectations_df.empty:
                        # Get all job levels that have expectations for this skill
                        job_levels_with_skill = expectations_df[expectations_df["skill"] == selected_skill]["job_level"].unique()
                        filtered_levels_df = levels_df[levels_df["name"].isin(job_levels_with_skill)]
                    else:
                        filtered_levels_df = levels_df
                else:
                    st.info("No skills have been added yet.")
                    filtered_levels_df = levels_df
            else:
                filtered_levels_df = levels_df
        
        # Display management instructions
        if filter_type == "Filter by Skill" and selected_skill != "All Skills" and not filtered_levels_df.empty:
            st.info(f"Showing job levels that have expectations for the skill: **{selected_skill}**")
        else:
            st.info("Use the table below to manage job levels.")
        
        # Display headers
        header_cols = st.columns([3, 5, 1, 1])
        with header_cols[0]:
            st.markdown("**Name**")
        with header_cols[1]:
            st.markdown("**Description**")
        with header_cols[2]:
            st.markdown("**Edit**")
        with header_cols[3]:
            st.markdown("**Delete**")
        
        st.markdown("---")
        
        # Display each level row (filtered)
        for _, level_row in filtered_levels_df.iterrows():
            level_id = level_row["level_id"]
            level_cols = st.columns([3, 5, 1, 1])
            
            with level_cols[0]:
                st.write(f"{level_row['name']} (ID: {level_id})")
            
            with level_cols[1]:
                st.write(f"{level_row['description']}")
            
            with level_cols[2]:
                # Edit level button
                if st.button("✏️", key=f"edit_level_{level_id}"):
                    # Set session state to store the level being edited
                    st.session_state[f"edit_level_id_{level_id}"] = True
            
            with level_cols[3]:
                # Delete level button
                if st.button("🗑️", key=f"del_level_{level_id}"):
                    success, message = delete_job_level(level_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            # Display edit form as a modal if the edit button was clicked
            if st.session_state.get(f"edit_level_id_{level_id}", False):
                # Create a modal using Streamlit's container with border
                with st.container(border=True):
                    st.markdown("### Edit Job Level")
                    new_name = st.text_input("Name", value=level_row["name"], key=f"level_name_{level_id}")
                    new_desc = st.text_area("Description", value=level_row["description"], key=f"level_desc_{level_id}")
                    
                    edit_col1, edit_col2 = st.columns([1, 1])
                    with edit_col1:
                        if st.button("Save", type="primary", key=f"save_level_{level_id}"):
                            success, message = update_job_level(level_id, new_name, new_desc)
                            if success:
                                st.success(message)
                                # Clear the editing state
                                st.session_state.pop(f"edit_level_id_{level_id}", None)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with edit_col2:
                        if st.button("Cancel", key=f"cancel_level_{level_id}"):
                            # Clear the editing state
                            st.session_state.pop(f"edit_level_id_{level_id}", None)
                            st.rerun()
    else:
        st.info("No job levels added yet.")

# Skill Expectations Tab
with tab3:
    st.header("Skill Expectations")
    st.write("Set the expected skill scores for each job level.")
    
    organization_id = get_current_organization_id()
    levels_df = load_data_for_organization("levels", organization_id)
    competencies_df = load_data_for_organization("competencies", organization_id)
    skills_df = load_data_for_organization("skills", organization_id)
    
    if levels_df.empty or competencies_df.empty or skills_df.empty:
        st.warning("You need to set up job levels, competencies, and skills first.")
    else:
        # Add button for new skill expectation
        show_add_expectation = st.button("➕ Add New Expected Score", type="primary", key="show_add_expectation_btn")
        
        # Create session state variable if it doesn't exist
        if "show_add_expectation_form" not in st.session_state:
            st.session_state.show_add_expectation_form = False
        
        # Toggle form visibility when button is clicked
        if show_add_expectation:
            st.session_state.show_add_expectation_form = not st.session_state.show_add_expectation_form
        
        # Display add form if active
        if st.session_state.show_add_expectation_form:
            with st.container(border=True):
                st.subheader("Add New Expected Score")
                
                # Select job level
                level_options = levels_df["name"].tolist()
                selected_level = st.selectbox("Select Job Level", level_options, key="expectations_level")
                
                # Select competency
                comp_options = competencies_df["name"].tolist()
                selected_comp = st.selectbox("Select Competency", comp_options, key="expectations_comp")
                
                # Get competency ID
                selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]
                
                # Get skills for selected competency
                comp_skills = get_competency_skills(selected_comp_id)
                
                if not comp_skills.empty:
                    # Select skill
                    skill_options = comp_skills["name"].tolist()
                    selected_skill = st.selectbox("Select Skill", skill_options, key="expectations_skill")
                    
                    # Set expected score
                    expected_score = st.slider(
                        "Expected Score", 
                        min_value=1.0, 
                        max_value=5.0, 
                        step=0.5, 
                        value=3.0
                    )
                    
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        submit_expectation = st.button("Save", type="primary", key="submit_expectation_btn")
                    with col2:
                        cancel_expectation = st.button("Cancel", key="cancel_expectation_btn")
                    
                    if submit_expectation:
                        success, message = set_skill_expectation(
                            selected_level, 
                            selected_comp, 
                            selected_skill, 
                            expected_score
                        )
                        if success:
                            st.success(message)
                            st.session_state.show_add_expectation_form = False
                            st.rerun()
                        else:
                            st.error(message)
                    
                    if cancel_expectation:
                        st.session_state.show_add_expectation_form = False
                        st.rerun()
                else:
                    st.warning("No skills found for the selected competency.")
        
        st.markdown("---")
        
        # Display Current Expectations section
        st.subheader("Current Expectations")
        organization_id = get_current_organization_id()
        expectations_df = load_data_for_organization("expectations", organization_id)
        
        if not expectations_df.empty:
            # Show filter options
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
                level_options = ["All Levels"] + levels_df["name"].tolist()
                filter_level = st.selectbox("Filter by Job Level", level_options, key="filter_expectations_level")
                
            with filter_col2:
                comp_options = ["All Competencies"] + competencies_df["name"].tolist()
                filter_comp = st.selectbox("Filter by Competency", comp_options, key="filter_skill_expectations_comp")
            
            # Apply filters
            filtered_exp = expectations_df.copy()
            
            if filter_level != "All Levels":
                # Filter by selected level
                filtered_exp = filtered_exp[filtered_exp["job_level"] == filter_level]
                
            if filter_comp != "All Competencies":
                # Filter by selected competency
                filtered_exp = filtered_exp[filtered_exp["competency"] == filter_comp]
                
            if (filter_level != "All Levels" or filter_comp != "All Competencies"):
                if not filtered_exp.empty:
                    # Display expectations in a table format
                    st.info("Use the table below to manage skill expectations.")
                    
                    # Display headers
                    header_cols = st.columns([2, 2, 1, 1, 1])
                    with header_cols[0]:
                        st.markdown("**Competency**")
                    with header_cols[1]:
                        st.markdown("**Skill**")
                    with header_cols[2]:
                        st.markdown("**Expected Score**")
                    with header_cols[3]:
                        st.markdown("**Edit**")
                    with header_cols[4]:
                        st.markdown("**Delete**")
                    
                    st.markdown("---")
                    
                    # Display each expectation row
                    for i, row in filtered_exp.iterrows():
                        # Create session state for edit if doesn't exist
                        if f"edit_exp_{i}" not in st.session_state:
                            st.session_state[f"edit_exp_{i}"] = False
                        
                        # Display row content
                        exp_cols = st.columns([2, 2, 1, 1, 1])
                        with exp_cols[0]:
                            st.write(f"{row['competency']}")
                        with exp_cols[1]:
                            st.write(f"{row['skill']}")
                        with exp_cols[2]:
                            st.write(f"{row['expected_score']}")
                        with exp_cols[3]:
                            if st.button("✏️", key=f"edit_btn_exp_{i}"):
                                st.session_state[f"edit_exp_{i}"] = True
                        with exp_cols[4]:
                            if st.button("🗑️", key=f"del_exp_{i}"):
                                success, message = delete_expectation(
                                    row["job_level"], 
                                    row["competency"], 
                                    row["skill"]
                                )
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        
                        # Display edit form if edit button was clicked
                        if st.session_state[f"edit_exp_{i}"]:
                            with st.container(border=True):
                                st.markdown("### Edit Skill Expectation")
                                new_score = st.slider(
                                    "Expected Score", 
                                    min_value=1.0, 
                                    max_value=5.0, 
                                    step=0.5, 
                                    value=float(row['expected_score']),
                                    key=f"edit_score_exp_{i}"
                                )
                                
                                edit_col1, edit_col2 = st.columns([1, 5])
                                with edit_col1:
                                    if st.button("Save", type="primary", key=f"save_exp_{i}"):
                                        success, message = set_skill_expectation(
                                            row["job_level"],
                                            row["competency"],
                                            row["skill"],
                                            new_score
                                        )
                                        if success:
                                            st.success(message)
                                            st.session_state[f"edit_exp_{i}"] = False
                                            st.rerun()
                                        else:
                                            st.error(message)
                                
                                with edit_col2:
                                    if st.button("Cancel", key=f"cancel_exp_{i}"):
                                        st.session_state[f"edit_exp_{i}"] = False
                                        st.rerun()
                else:
                    # Show appropriate info message based on what was filtered
                    if filter_level != "All Levels" and filter_comp != "All Competencies":
                        st.info(f"No skill expectations set for {filter_level} and {filter_comp}.")
                    elif filter_level != "All Levels":
                        st.info(f"No skill expectations set for {filter_level}.")
                    else:
                        st.info(f"No skill expectations set for {filter_comp}.")
            else:
                # Show all expectations in a table format
                st.info("Showing all skill expectations. Use filters above to narrow down the results.")
                
                # Display headers
                header_cols = st.columns([2, 2, 2, 1, 1, 1])
                with header_cols[0]:
                    st.markdown("**Job Level**")
                with header_cols[1]:
                    st.markdown("**Competency**")
                with header_cols[2]:
                    st.markdown("**Skill**")
                with header_cols[3]:
                    st.markdown("**Expected Score**")
                with header_cols[4]:
                    st.markdown("**Edit**")
                with header_cols[5]:
                    st.markdown("**Delete**")
                
                st.markdown("---")
                
                # Display each expectation row
                for i, row in expectations_df.iterrows():
                    # Create session state for edit if doesn't exist
                    if f"edit_exp_all_{i}" not in st.session_state:
                        st.session_state[f"edit_exp_all_{i}"] = False
                    
                    exp_cols = st.columns([2, 2, 2, 1, 1, 1])
                    with exp_cols[0]:
                        st.write(f"{row['job_level']}")
                    with exp_cols[1]:
                        st.write(f"{row['competency']}")
                    with exp_cols[2]:
                        st.write(f"{row['skill']}")
                    with exp_cols[3]:
                        st.write(f"{row['expected_score']}")
                    with exp_cols[4]:
                        if st.button("✏️", key=f"edit_btn_exp_all_{i}"):
                            st.session_state[f"edit_exp_all_{i}"] = True
                    with exp_cols[5]:
                        if st.button("🗑️", key=f"del_exp_all_{i}"):
                            success, message = delete_expectation(
                                row["job_level"], 
                                row["competency"], 
                                row["skill"]
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    # Display edit form if edit button was clicked
                    if st.session_state[f"edit_exp_all_{i}"]:
                        with st.container(border=True):
                            st.markdown("### Edit Skill Expectation")
                            new_score = st.slider(
                                "Expected Score", 
                                min_value=1.0, 
                                max_value=5.0, 
                                step=0.5, 
                                value=float(row['expected_score']),
                                key=f"edit_score_exp_all_{i}"
                            )
                            
                            edit_col1, edit_col2 = st.columns([1, 5])
                            with edit_col1:
                                if st.button("Save", type="primary", key=f"save_exp_all_{i}"):
                                    success, message = set_skill_expectation(
                                        row["job_level"],
                                        row["competency"],
                                        row["skill"],
                                        new_score
                                    )
                                    if success:
                                        st.success(message)
                                        st.session_state[f"edit_exp_all_{i}"] = False
                                        st.rerun()
                                    else:
                                        st.error(message)
                            
                            with edit_col2:
                                if st.button("Cancel", key=f"cancel_exp_all_{i}"):
                                    st.session_state[f"edit_exp_all_{i}"] = False
                                    st.rerun()
        else:
            st.info("No skill expectations set yet.")

# Competency Expectations Tab
with tab4:
    st.header("Competency Expectations")
    st.write("Set the expected competency scores for each job level (separate from skills).")
    
    organization_id = get_current_organization_id()
    levels_df = load_data_for_organization("levels", organization_id)
    competencies_df = load_data_for_organization("competencies", organization_id)
    
    if levels_df.empty or competencies_df.empty:
        st.warning("You need to set up job levels and competencies first.")
    else:
        # Add button for new competency expectation
        show_add_comp_expectation = st.button("➕ Add New Competency Expected Score", type="primary", key="show_add_comp_expectation_btn")
        
        # Create session state variable if it doesn't exist
        if "show_add_comp_expectation_form" not in st.session_state:
            st.session_state.show_add_comp_expectation_form = False
        
        # Toggle form visibility when button is clicked
        if show_add_comp_expectation:
            st.session_state.show_add_comp_expectation_form = not st.session_state.show_add_comp_expectation_form
        
        # Display add form if active
        if st.session_state.show_add_comp_expectation_form:
            with st.container(border=True):
                st.subheader("Add New Competency Expected Score")
                
                # Select job level
                level_options = levels_df["name"].tolist()
                selected_level = st.selectbox("Select Job Level", level_options, key="comp_expectations_level")
                
                # Select competency
                comp_options = competencies_df["name"].tolist()
                selected_comp = st.selectbox("Select Competency", comp_options, key="comp_expectations_comp")
                
                # Set expected score
                expected_score = st.slider(
                    "Expected Score", 
                    min_value=1.0, 
                    max_value=5.0, 
                    step=0.5, 
                    value=3.0,
                    key="comp_expected_score"
                )
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    submit_comp_expectation = st.button("Save", type="primary", key="submit_comp_expectation_btn")
                with col2:
                    cancel_comp_expectation = st.button("Cancel", key="cancel_comp_expectation_btn")
                
                if submit_comp_expectation:
                    success, message = set_competency_expectation(
                        selected_level, 
                        selected_comp, 
                        expected_score
                    )
                    if success:
                        st.success(message)
                        st.session_state.show_add_comp_expectation_form = False
                        st.rerun()
                    else:
                        st.error(message)
                
                if cancel_comp_expectation:
                    st.session_state.show_add_comp_expectation_form = False
                    st.rerun()
        
        st.markdown("---")
        
        # Display Current Competency Expectations section
        st.subheader("Current Competency Expectations")
        organization_id = get_current_organization_id()
        comp_expectations_df = load_data_for_organization("comp_expectations", organization_id)
        
        if not comp_expectations_df.empty:
            # Show filter options
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
                level_options = ["All Levels"] + levels_df["name"].tolist()
                filter_level = st.selectbox("Filter by Job Level", level_options, key="filter_comp_expectations_level")
                
            with filter_col2:
                comp_options = ["All Competencies"] + competencies_df["name"].tolist()
                filter_comp = st.selectbox("Filter by Competency", comp_options, key="filter_comp_expectations_comp")
            
            # Apply filters
            filtered_exp = comp_expectations_df.copy()
            
            if filter_level != "All Levels":
                # Filter by selected level
                filtered_exp = filtered_exp[filtered_exp["job_level"] == filter_level]
                
            if filter_comp != "All Competencies":
                # Filter by selected competency
                filtered_exp = filtered_exp[filtered_exp["competency"] == filter_comp]
                
            if (filter_level != "All Levels" or filter_comp != "All Competencies"):
                if not filtered_exp.empty:
                    # Display expectations in a table format
                    st.info("Use the table below to manage competency expectations.")
                    
                    # Display headers
                    header_cols = st.columns([3, 1, 1, 1])
                    with header_cols[0]:
                        st.markdown("**Competency**")
                    with header_cols[1]:
                        st.markdown("**Expected Score**")
                    with header_cols[2]:
                        st.markdown("**Edit**")
                    with header_cols[3]:
                        st.markdown("**Delete**")
                    
                    st.markdown("---")
                    
                    # Display each expectation row
                    for i, row in filtered_exp.iterrows():
                        # Create session state for edit if doesn't exist
                        if f"edit_comp_exp_{i}" not in st.session_state:
                            st.session_state[f"edit_comp_exp_{i}"] = False
                        
                        exp_cols = st.columns([3, 1, 1, 1])
                        with exp_cols[0]:
                            st.write(f"{row['competency']}")
                        with exp_cols[1]:
                            st.write(f"{row['expected_score']}")
                        with exp_cols[2]:
                            if st.button("✏️", key=f"edit_btn_comp_exp_{i}"):
                                st.session_state[f"edit_comp_exp_{i}"] = True
                        with exp_cols[3]:
                            if st.button("🗑️", key=f"del_comp_exp_{i}"):
                                success, message = delete_competency_expectation(
                                    row["job_level"],
                                    row["competency"]
                                )
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        
                        # Display edit form if edit button was clicked
                        if st.session_state[f"edit_comp_exp_{i}"]:
                            with st.container(border=True):
                                st.markdown("### Edit Competency Expectation")
                                new_score = st.slider(
                                    "Expected Score", 
                                    min_value=1.0, 
                                    max_value=5.0, 
                                    step=0.5, 
                                    value=float(row['expected_score']),
                                    key=f"edit_score_comp_exp_{i}"
                                )
                                
                                edit_col1, edit_col2 = st.columns([1, 5])
                                with edit_col1:
                                    if st.button("Save", type="primary", key=f"save_comp_exp_{i}"):
                                        success, message = set_competency_expectation(
                                            row["job_level"],
                                            row["competency"],
                                            new_score
                                        )
                                        if success:
                                            st.success(message)
                                            st.session_state[f"edit_comp_exp_{i}"] = False
                                            st.rerun()
                                        else:
                                            st.error(message)
                                
                                with edit_col2:
                                    if st.button("Cancel", key=f"cancel_comp_exp_{i}"):
                                        st.session_state[f"edit_comp_exp_{i}"] = False
                                        st.rerun()
                else:
                    # Show appropriate info message based on what was filtered
                    if filter_level != "All Levels" and filter_comp != "All Competencies":
                        st.info(f"No competency expectations set for {filter_level} and {filter_comp}.")
                    elif filter_level != "All Levels":
                        st.info(f"No competency expectations set for {filter_level}.")
                    else:
                        st.info(f"No competency expectations set for {filter_comp}.")
            else:
                # Show all expectations in a table format
                st.info("Showing all competency expectations. Use filters above to narrow down the results.")
                
                # Display headers
                header_cols = st.columns([2, 3, 1, 1, 1])
                with header_cols[0]:
                    st.markdown("**Job Level**")
                with header_cols[1]:
                    st.markdown("**Competency**")
                with header_cols[2]:
                    st.markdown("**Expected Score**")
                with header_cols[3]:
                    st.markdown("**Edit**")
                with header_cols[4]:
                    st.markdown("**Delete**")
                
                st.markdown("---")
                
                # Display each expectation row
                for i, row in comp_expectations_df.iterrows():
                    # Create session state for edit if doesn't exist
                    if f"edit_comp_exp_all_{i}" not in st.session_state:
                        st.session_state[f"edit_comp_exp_all_{i}"] = False
                    
                    exp_cols = st.columns([2, 3, 1, 1, 1])
                    with exp_cols[0]:
                        st.write(f"{row['job_level']}")
                    with exp_cols[1]:
                        st.write(f"{row['competency']}")
                    with exp_cols[2]:
                        st.write(f"{row['expected_score']}")
                    with exp_cols[3]:
                        if st.button("✏️", key=f"edit_btn_comp_exp_all_{i}"):
                            st.session_state[f"edit_comp_exp_all_{i}"] = True
                    with exp_cols[4]:
                        if st.button("🗑️", key=f"del_comp_exp_all_{i}"):
                            success, message = delete_competency_expectation(
                                row["job_level"],
                                row["competency"]
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    # Display edit form if edit button was clicked
                    if st.session_state[f"edit_comp_exp_all_{i}"]:
                        with st.container(border=True):
                            st.markdown("### Edit Competency Expectation")
                            new_score = st.slider(
                                "Expected Score", 
                                min_value=1.0, 
                                max_value=5.0, 
                                step=0.5, 
                                value=float(row['expected_score']),
                                key=f"edit_score_comp_exp_all_{i}"
                            )
                            
                            edit_col1, edit_col2 = st.columns([1, 5])
                            with edit_col1:
                                if st.button("Save", type="primary", key=f"save_comp_exp_all_{i}"):
                                    success, message = set_competency_expectation(
                                        row["job_level"],
                                        row["competency"],
                                        new_score
                                    )
                                    if success:
                                        st.success(message)
                                        st.session_state[f"edit_comp_exp_all_{i}"] = False
                                        st.rerun()
                                    else:
                                        st.error(message)
                            
                            with edit_col2:
                                if st.button("Cancel", key=f"cancel_comp_exp_all_{i}"):
                                    st.session_state[f"edit_comp_exp_all_{i}"] = False
                                    st.rerun()
        else:
            st.info("No competency expectations set yet.")

# Manage Employees Tab
with tab5:
    st.header("Manage Employees")
    
    # Add button for new employee
    show_add_employee = st.button("➕ Add New Employee", type="primary", key="show_add_employee_btn")
    
    # Create session state variable if it doesn't exist
    if "show_add_employee_form" not in st.session_state:
        st.session_state.show_add_employee_form = False
    
    # Toggle form visibility when button is clicked
    if show_add_employee:
        st.session_state.show_add_employee_form = not st.session_state.show_add_employee_form
    
    # Display add employee form if active
    if st.session_state.show_add_employee_form:
        with st.container(border=True):
            st.subheader("Add New Employee")
            
            # Get job levels for dropdown
            organization_id = get_current_organization_id()
            levels_df = load_data_for_organization("levels", organization_id)
            level_options = [""] + levels_df["name"].tolist() if not levels_df.empty else [""]
            
            # Get managers for dropdown
            employees_df = load_data_for_organization("employees", organization_id)
            manager_options = [("", "None")] + [
                (str(row["employee_id"]), row["name"]) 
                for _, row in employees_df.iterrows()
            ] if not employees_df.empty else [("", "None")]
            
            manager_names = [m[1] for m in manager_options]
            manager_ids = [m[0] for m in manager_options]
            
            # Create two columns for compacter layout
            field_col1, field_col2 = st.columns(2)
            
            # Form for adding new employee
            with field_col1:
                emp_name = st.text_input("Employee Name", key="emp_name_input")
                emp_email = st.text_input("Email", key="emp_email_input")
                emp_title = st.text_input("Job Title", key="emp_title_input")
            
            with field_col2:
                emp_level = st.selectbox("Job Level", level_options, key="emp_level_input")
                emp_dept = st.text_input("Department", key="emp_dept_input")
                selected_manager = st.selectbox("Manager", manager_names, key="emp_manager_input")
                emp_date = st.date_input("Hire Date", key="emp_date_input")
            
            # Get manager ID from selection
            selected_manager_idx = manager_names.index(selected_manager)
            selected_manager_id = manager_ids[selected_manager_idx]
            
            # Action buttons
            button_col1, button_col2 = st.columns([1, 5])
            with button_col1:
                submit_employee = st.button("Save", type="primary", key="submit_employee_btn")
            with button_col2:
                cancel_employee = st.button("Cancel", key="cancel_employee_btn")
            
            # Submit handler
            if submit_employee:
                if emp_name and emp_email and emp_title and emp_level and emp_dept:
                    from data_manager import add_employee
                    
                    # Convert manager ID to integer if it's not empty
                    manager_id = int(selected_manager_id) if selected_manager_id else None
                    
                    success, message, _ = add_employee(
                        emp_name, 
                        emp_email, 
                        emp_title, 
                        emp_level, 
                        emp_dept, 
                        manager_id, 
                        emp_date.strftime("%Y-%m-%d")
                    )
                    if success:
                        st.success(message)
                        st.session_state.show_add_employee_form = False
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill in all required fields.")
            
            # Cancel handler
            if cancel_employee:
                st.session_state.show_add_employee_form = False
                st.rerun()
    
    st.markdown("---")
    
    # Manage Existing Employees section
    st.subheader("Manage Existing Employees")
    organization_id = get_current_organization_id()
    employees_df = load_data_for_organization("employees", organization_id)
    
    if not employees_df.empty:
        # Create a mapping of employee IDs to names for manager display
        emp_id_to_name = dict(zip(employees_df["employee_id"], employees_df["name"]))
        
        # Create filter options
        # Handle case where department contains both string and NaN values
        departments = employees_df["department"].dropna().unique().tolist()
        departments = sorted([str(d) for d in departments])
        
        # Handle job_levels the same way
        job_levels = employees_df["job_level"].dropna().unique().tolist()
        job_levels = sorted([str(j) for j in job_levels])
        
        # Show filter controls
        filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])
        
        with filter_col1:
            filter_type = st.selectbox("Filter By", ["All Employees", "Department", "Job Level"], key="employee_filter_type")
        
        with filter_col2:
            if filter_type == "Department":
                filter_value = st.selectbox("Select Department", departments, key="employee_filter_dept")
                filtered_df = employees_df[employees_df["department"] == filter_value]
            elif filter_type == "Job Level":
                filter_value = st.selectbox("Select Job Level", job_levels, key="employee_filter_level")
                filtered_df = employees_df[employees_df["job_level"] == filter_value]
            else:
                filtered_df = employees_df
        
        # Display a table of all employees with edit and delete buttons
        st.info("Use the table below to manage employees.")
        
        # Display headers
        header_cols = st.columns([2, 2, 2, 1, 1, 1])
        with header_cols[0]:
            st.markdown("**Name**")
        with header_cols[1]:
            st.markdown("**Job Title**")
        with header_cols[2]:
            st.markdown("**Department**")
        with header_cols[3]:
            st.markdown("**Level**")
        with header_cols[4]:
            st.markdown("**Edit**")
        with header_cols[5]:
            st.markdown("**Delete**")
        
        st.markdown("---")
        
        # Display each employee in a row (filtered)
        for i, row in filtered_df.iterrows():
            emp_id = row["employee_id"]
            
            # Create session state for edit if doesn't exist
            if f"edit_emp_{emp_id}" not in st.session_state:
                st.session_state[f"edit_emp_{emp_id}"] = False
            
            emp_cols = st.columns([2, 2, 2, 1, 1, 1])
            with emp_cols[0]:
                st.write(f"{row['name']}")
            with emp_cols[1]:
                st.write(f"{row['job_title']}")
            with emp_cols[2]:
                st.write(f"{row['department']}")
            with emp_cols[3]:
                st.write(f"{row['job_level']}")
            with emp_cols[4]:
                if st.button("✏️", key=f"edit_btn_emp_{emp_id}"):
                    st.session_state[f"edit_emp_{emp_id}"] = True
            with emp_cols[5]:
                if st.button("🗑️", key=f"del_emp_btn_{emp_id}"):
                    success, message = delete_employee(emp_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            # Display edit form if edit button was clicked
            if st.session_state[f"edit_emp_{emp_id}"]:
                with st.container(border=True):
                    st.markdown("### Edit Employee")
                    
                    # Get job levels for dropdown
                    levels_df = load_data("levels")
                    level_options = levels_df["name"].tolist() if not levels_df.empty else []
                    
                    # Get managers for dropdown (exclude the current employee)
                    manager_options = [("", "None")] + [
                        (str(row2["employee_id"]), row2["name"]) 
                        for _, row2 in employees_df.iterrows() 
                        if row2["employee_id"] != emp_id
                    ]
                    
                    manager_names = [m[1] for m in manager_options]
                    manager_ids = [m[0] for m in manager_options]
                    
                    # Find the current manager in the options
                    current_manager_id = row["manager_id"] if pd.notna(row["manager_id"]) else ""
                    current_manager_idx = 0  # Default to "None"
                    for j, m_id in enumerate(manager_ids):
                        if str(current_manager_id) == str(m_id):
                            current_manager_idx = j
                            break
                    
                    # Create two columns for compacter layout
                    edit_field_col1, edit_field_col2 = st.columns(2)
                    
                    # Input fields in first column
                    with edit_field_col1:
                        new_name = st.text_input("Name", value=row["name"], key=f"emp_name_{emp_id}")
                        new_email = st.text_input("Email", value=row["email"], key=f"emp_email_{emp_id}")
                        new_title = st.text_input("Job Title", value=row["job_title"], key=f"emp_title_{emp_id}")
                        
                    # Input fields in second column
                    with edit_field_col2:
                        # Job level dropdown
                        level_idx = level_options.index(row["job_level"]) if row["job_level"] in level_options else 0
                        new_level = st.selectbox("Job Level", level_options, index=level_idx, key=f"emp_level_{emp_id}")
                        
                        new_dept = st.text_input("Department", value=row["department"], key=f"emp_dept_{emp_id}")
                        
                        # Manager dropdown
                        new_manager_name = st.selectbox("Manager", manager_names, index=current_manager_idx, key=f"emp_manager_{emp_id}")
                    
                    # Get manager ID from selection
                    manager_idx = manager_names.index(new_manager_name)
                    new_manager_id = manager_ids[manager_idx]
                    
                    # Convert manager ID to integer if it's not empty
                    new_manager_id = int(new_manager_id) if new_manager_id else None
                    
                    # Action buttons
                    action_col1, action_col2 = st.columns([1, 5])
                    with action_col1:
                        if st.button("Save", type="primary", key=f"save_emp_{emp_id}"):
                            success, message = update_employee(
                                emp_id,
                                new_name,
                                new_email,
                                new_title,
                                new_level,
                                new_dept,
                                new_manager_id
                            )
                            if success:
                                st.success(message)
                                # Clear the editing state
                                st.session_state[f"edit_emp_{emp_id}"] = False
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with action_col2:
                        if st.button("Cancel", key=f"cancel_emp_{emp_id}"):
                            # Clear the editing state
                            st.session_state[f"edit_emp_{emp_id}"] = False
                            st.rerun()
    else:
        st.info("No employees added yet.")

# Add explanatory text at the bottom
st.markdown("---")
st.markdown("""
### How to Use This Page

1. First, create competencies that represent broad skill categories in your organization.
2. Add specific skills under each competency.
3. Define job levels or roles in your organization.
4. Set expected scores for each skill at each job level.
5. Set expected scores for each competency at each job level (separate from skills).
6. Add employees and assign them to appropriate job levels and managers.

This framework will be used as the basis for skill and competency assessments and visualizations throughout the application.
The system allows you to evaluate both individual skills and overall competency areas separately.
""")
