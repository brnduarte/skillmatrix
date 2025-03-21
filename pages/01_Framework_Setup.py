import streamlit as st
import pandas as pd
from data_manager import (
    load_data, save_data, add_competency, add_skill, 
    add_job_level, set_skill_expectation, set_competency_expectation, get_competency_skills,
    delete_competency, delete_skill, delete_job_level, delete_employee,
    delete_expectation, delete_competency_expectation, update_competency, update_skill, update_job_level,
    update_employee
)
from utils import check_permission
from modal_utils import create_modal, open_modal, close_modal, render_modal, display_as_table

# Page configuration
st.set_page_config(
    page_title="Framework Setup - Skill Matrix",
    page_icon="🛠️",
    layout="wide"
)

# Check if user is authenticated
if not hasattr(st.session_state, "authenticated") or not st.session_state.authenticated:
    st.warning("Please login from the Home page.")
    st.stop()

# Check permissions - only admin can access this page
if not check_permission("admin"):
    st.error("You don't have permission to access this page.")
    st.stop()

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
    
    # Main table showing all competencies
    competencies_df = load_data("competencies")
    skills_df = load_data("skills")
    
    # Add new competency button
    if st.button("➕ Add New Competency", type="primary", use_container_width=True):
        open_modal("add_competency")
        st.rerun()
    
    # Modal for adding a new competency
    def add_competency_modal():
        with st.form("add_competency_form"):
            comp_name = st.text_input("Competency Name")
            comp_desc = st.text_area("Description")
            
            submitted = st.form_submit_button("Add Competency")
            if submitted:
                if comp_name:
                    success, message, _ = add_competency(comp_name, comp_desc)
                    if success:
                        st.success(message)
                        close_modal("add_competency")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a competency name")
        
        if st.button("Cancel", type="secondary"):
            close_modal("add_competency")
            st.rerun()
    
    render_modal("Add New Competency", add_competency_modal, "add_competency")
    
    # Define edit and delete functions for competencies
    def edit_competency(competency_id):
        # Find the competency data
        comp_data = competencies_df[competencies_df["competency_id"] == competency_id].iloc[0]
        st.session_state["edit_comp_name"] = comp_data["name"]
        st.session_state["edit_comp_desc"] = comp_data["description"]
        st.session_state["edit_comp_id"] = competency_id
        open_modal("edit_competency")
        st.rerun()
    
    def delete_competency_action(competency_id):
        st.session_state["delete_comp_id"] = competency_id
        comp_data = competencies_df[competencies_df["competency_id"] == competency_id].iloc[0]
        st.session_state["delete_comp_name"] = comp_data["name"]
        open_modal("delete_competency")
        st.rerun()
    
    def view_skills(competency_id):
        st.session_state["view_skills_comp_id"] = competency_id
        comp_data = competencies_df[competencies_df["competency_id"] == competency_id].iloc[0]
        st.session_state["view_skills_comp_name"] = comp_data["name"]
        open_modal("view_skills")
        st.rerun()
    
    # Modal for editing a competency
    def edit_competency_modal():
        competency_id = st.session_state.get("edit_comp_id")
        with st.form("edit_competency_form"):
            comp_name = st.text_input("Competency Name", value=st.session_state.get("edit_comp_name", ""))
            comp_desc = st.text_area("Description", value=st.session_state.get("edit_comp_desc", ""))
            
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                if comp_name:
                    success, message = update_competency(competency_id, comp_name, comp_desc)
                    if success:
                        st.success(message)
                        close_modal("edit_competency")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a competency name")
        
        if st.button("Cancel", type="secondary"):
            close_modal("edit_competency")
            st.rerun()
    
    render_modal("Edit Competency", edit_competency_modal, "edit_competency")
    
    # Modal for deleting a competency
    def delete_competency_modal():
        competency_id = st.session_state.get("delete_comp_id")
        comp_name = st.session_state.get("delete_comp_name", "")
        
        st.warning(f"Are you sure you want to delete the competency '{comp_name}'? This will also delete all associated skills and expectations.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete", type="primary", use_container_width=True):
                success, message = delete_competency(competency_id)
                if success:
                    st.success(message)
                    close_modal("delete_competency")
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            if st.button("Cancel", type="secondary", use_container_width=True):
                close_modal("delete_competency")
                st.rerun()
    
    render_modal("Delete Competency", delete_competency_modal, "delete_competency")
    
    # Modal for viewing skills for a competency
    def view_skills_modal():
        competency_id = st.session_state.get("view_skills_comp_id")
        comp_name = st.session_state.get("view_skills_comp_name", "")
        
        st.subheader(f"Skills for {comp_name}")
        
        # Add new skill button
        if st.button("➕ Add New Skill", type="primary", use_container_width=True):
            st.session_state["add_skill_comp_id"] = competency_id
            st.session_state["add_skill_comp_name"] = comp_name
            open_modal("add_skill")
            close_modal("view_skills")
            st.rerun()
        
        # Get skills for this competency
        comp_skills = get_competency_skills(competency_id)
        
        if not comp_skills.empty:
            # Display skills in a table with edit/delete actions
            def edit_skill(skill_id):
                skill_data = comp_skills[comp_skills["skill_id"] == skill_id].iloc[0]
                st.session_state["edit_skill_id"] = skill_id
                st.session_state["edit_skill_name"] = skill_data["name"]
                st.session_state["edit_skill_desc"] = skill_data["description"]
                st.session_state["edit_skill_comp_id"] = competency_id
                st.session_state["edit_skill_comp_name"] = comp_name
                open_modal("edit_skill")
                close_modal("view_skills")
                st.rerun()
            
            def delete_skill_action(skill_id):
                skill_data = comp_skills[comp_skills["skill_id"] == skill_id].iloc[0]
                st.session_state["delete_skill_id"] = skill_id
                st.session_state["delete_skill_name"] = skill_data["name"]
                st.session_state["delete_skill_comp_name"] = comp_name
                open_modal("delete_skill")
                close_modal("view_skills")
                st.rerun()
            
            # Create the table
            st.dataframe(
                comp_skills[["name", "description"]],
                column_config={
                    "name": "Skill Name",
                    "description": "Description"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # For each skill, create edit and delete buttons
            for _, skill in comp_skills.iterrows():
                cols = st.columns([3, 1, 1])
                with cols[0]:
                    st.write(f"{skill['name']}: {skill['description']}")
                with cols[1]:
                    if st.button("✏️ Edit", key=f"edit_skill_{skill['skill_id']}", use_container_width=True):
                        edit_skill(skill["skill_id"])
                with cols[2]:
                    if st.button("🗑️ Delete", key=f"delete_skill_{skill['skill_id']}", use_container_width=True):
                        delete_skill_action(skill["skill_id"])
        else:
            st.info(f"No skills added yet for {comp_name}.")
        
        if st.button("Close", type="secondary", use_container_width=True):
            close_modal("view_skills")
            st.rerun()
    
    render_modal("View Skills", view_skills_modal, "view_skills", width=800)
    
    # Modal for adding a new skill
    def add_skill_modal():
        competency_id = st.session_state.get("add_skill_comp_id")
        comp_name = st.session_state.get("add_skill_comp_name", "")
        
        with st.form("add_skill_form"):
            st.subheader(f"Add New Skill to {comp_name}")
            skill_name = st.text_input("Skill Name")
            skill_desc = st.text_area("Description")
            
            submitted = st.form_submit_button("Add Skill")
            if submitted:
                if skill_name:
                    success, message, _ = add_skill(competency_id, skill_name, skill_desc)
                    if success:
                        st.success(message)
                        close_modal("add_skill")
                        open_modal("view_skills")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a skill name")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back to Skills", use_container_width=True):
                close_modal("add_skill")
                open_modal("view_skills")
                st.rerun()
        
        with col2:
            if st.button("Cancel", type="secondary", use_container_width=True):
                close_modal("add_skill")
                st.rerun()
    
    render_modal("Add New Skill", add_skill_modal, "add_skill")
    
    # Modal for editing a skill
    def edit_skill_modal():
        skill_id = st.session_state.get("edit_skill_id")
        skill_name = st.session_state.get("edit_skill_name", "")
        skill_desc = st.session_state.get("edit_skill_desc", "")
        comp_name = st.session_state.get("edit_skill_comp_name", "")
        comp_id = st.session_state.get("edit_skill_comp_id")
        
        with st.form("edit_skill_form"):
            st.subheader(f"Edit Skill for {comp_name}")
            new_skill_name = st.text_input("Skill Name", value=skill_name)
            new_skill_desc = st.text_area("Description", value=skill_desc)
            
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                if new_skill_name:
                    success, message = update_skill(skill_id, new_skill_name, new_skill_desc)
                    if success:
                        st.success(message)
                        close_modal("edit_skill")
                        open_modal("view_skills")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a skill name")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back to Skills", use_container_width=True):
                close_modal("edit_skill")
                open_modal("view_skills")
                st.rerun()
        
        with col2:
            if st.button("Cancel", type="secondary", use_container_width=True):
                close_modal("edit_skill")
                st.rerun()
    
    render_modal("Edit Skill", edit_skill_modal, "edit_skill")
    
    # Modal for deleting a skill
    def delete_skill_modal():
        skill_id = st.session_state.get("delete_skill_id")
        skill_name = st.session_state.get("delete_skill_name", "")
        comp_name = st.session_state.get("delete_skill_comp_name", "")
        
        st.warning(f"Are you sure you want to delete the skill '{skill_name}' from {comp_name}? This will also delete all associated expectations and assessments.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete", type="primary", use_container_width=True):
                success, message = delete_skill(skill_id)
                if success:
                    st.success(message)
                    close_modal("delete_skill")
                    open_modal("view_skills")
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            if st.button("Cancel", type="secondary", use_container_width=True):
                close_modal("delete_skill")
                open_modal("view_skills")
                st.rerun()
    
    render_modal("Delete Skill", delete_skill_modal, "delete_skill")
    
    # Display the competencies table with actions
    st.subheader("Competencies")
    
    if not competencies_df.empty:
        # Create a table to display competencies
        st.dataframe(
            competencies_df[["name", "description"]],
            column_config={
                "name": "Competency Name",
                "description": "Description"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # For each competency, create view, edit, and delete buttons
        for _, comp in competencies_df.iterrows():
            cols = st.columns([3, 1, 1, 1])
            with cols[0]:
                st.write(f"{comp['name']}: {comp['description'] or 'No description'}")
            with cols[1]:
                if st.button("👁️ Skills", key=f"view_skills_{comp['competency_id']}", use_container_width=True):
                    view_skills(comp["competency_id"])
            with cols[2]:
                if st.button("✏️ Edit", key=f"edit_comp_{comp['competency_id']}", use_container_width=True):
                    edit_competency(comp["competency_id"])
            with cols[3]:
                if st.button("🗑️ Delete", key=f"delete_comp_{comp['competency_id']}", use_container_width=True):
                    delete_competency_action(comp["competency_id"])
    else:
        st.info("No competencies added yet. Add your first competency to get started.")

# Job Levels Tab
with tab2:
    st.header("Job Levels")
    
    # Add new job level button
    if st.button("➕ Add New Job Level", type="primary", use_container_width=True):
        open_modal("add_job_level")
        st.rerun()
    
    # Modal for adding a new job level
    def add_job_level_modal():
        with st.form("add_job_level_form"):
            level_name = st.text_input("Level Name")
            level_desc = st.text_area("Description")
            
            submitted = st.form_submit_button("Add Job Level")
            if submitted:
                if level_name:
                    success, message, _ = add_job_level(level_name, level_desc)
                    if success:
                        st.success(message)
                        close_modal("add_job_level")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a job level name")
        
        if st.button("Cancel", type="secondary"):
            close_modal("add_job_level")
            st.rerun()
    
    render_modal("Add New Job Level", add_job_level_modal, "add_job_level")
    
    # Define edit and delete functions for job levels
    def edit_job_level(level_id):
        levels_df = load_data("levels")
        level_data = levels_df[levels_df["level_id"] == level_id].iloc[0]
        st.session_state["edit_level_id"] = level_id
        st.session_state["edit_level_name"] = level_data["name"]
        st.session_state["edit_level_desc"] = level_data["description"]
        open_modal("edit_job_level")
        st.rerun()
    
    def delete_job_level_action(level_id):
        levels_df = load_data("levels")
        level_data = levels_df[levels_df["level_id"] == level_id].iloc[0]
        st.session_state["delete_level_id"] = level_id
        st.session_state["delete_level_name"] = level_data["name"]
        open_modal("delete_job_level")
        st.rerun()
    
    # Modal for editing a job level
    def edit_job_level_modal():
        level_id = st.session_state.get("edit_level_id")
        
        with st.form("edit_job_level_form"):
            level_name = st.text_input("Level Name", value=st.session_state.get("edit_level_name", ""))
            level_desc = st.text_area("Description", value=st.session_state.get("edit_level_desc", ""))
            
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                if level_name:
                    success, message = update_job_level(level_id, level_name, level_desc)
                    if success:
                        st.success(message)
                        close_modal("edit_job_level")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a job level name")
        
        if st.button("Cancel", type="secondary"):
            close_modal("edit_job_level")
            st.rerun()
    
    render_modal("Edit Job Level", edit_job_level_modal, "edit_job_level")
    
    # Modal for deleting a job level
    def delete_job_level_modal():
        level_id = st.session_state.get("delete_level_id")
        level_name = st.session_state.get("delete_level_name", "")
        
        st.warning(f"Are you sure you want to delete the job level '{level_name}'? This will also delete all associated expectations.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete", type="primary", use_container_width=True):
                success, message = delete_job_level(level_id)
                if success:
                    st.success(message)
                    close_modal("delete_job_level")
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            if st.button("Cancel", type="secondary", use_container_width=True):
                close_modal("delete_job_level")
                st.rerun()
    
    render_modal("Delete Job Level", delete_job_level_modal, "delete_job_level")
    
    # Display the job levels table with actions
    st.subheader("Job Levels")
    
    levels_df = load_data("levels")
    if not levels_df.empty:
        # Create a table to display job levels
        st.dataframe(
            levels_df[["name", "description"]],
            column_config={
                "name": "Level Name",
                "description": "Description"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # For each job level, create edit and delete buttons
        for _, level in levels_df.iterrows():
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.write(f"{level['name']}: {level['description'] or 'No description'}")
            with cols[1]:
                if st.button("✏️ Edit", key=f"edit_level_{level['level_id']}", use_container_width=True):
                    edit_job_level(level["level_id"])
            with cols[2]:
                if st.button("🗑️ Delete", key=f"delete_level_{level['level_id']}", use_container_width=True):
                    delete_job_level_action(level["level_id"])
    else:
        st.info("No job levels added yet. Add your first job level to get started.")

# Skill Expectations Tab
with tab3:
    st.header("Skill Expectations")
    st.write("Set the expected skill scores for each job level.")
    
    levels_df = load_data("levels")
    competencies_df = load_data("competencies")
    skills_df = load_data("skills")
    expectations_df = load_data("expectations")
    
    if levels_df.empty or competencies_df.empty or skills_df.empty:
        st.warning("You need to set up job levels, competencies, and skills first.")
    else:
        # Add new expectation button
        if st.button("➕ Set New Expectation", type="primary", use_container_width=True):
            open_modal("add_expectation")
            st.rerun()
        
        # Modal for adding a new expectation
        def add_expectation_modal():
            with st.form("add_expectation_form"):
                # Select job level
                level_options = levels_df["name"].tolist()
                selected_level = st.selectbox("Select Job Level", level_options, key="expectation_level")
                
                # Select competency
                comp_options = competencies_df["name"].tolist()
                selected_comp = st.selectbox("Select Competency", comp_options, key="expectation_comp")
                
                # Get competency ID
                selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]
                
                # Get skills for selected competency
                comp_skills = get_competency_skills(selected_comp_id)
                
                if not comp_skills.empty:
                    # Select skill
                    skill_options = comp_skills["name"].tolist()
                    selected_skill = st.selectbox("Select Skill", skill_options, key="expectation_skill")
                    
                    # Set expected score
                    expected_score = st.slider(
                        "Expected Score", 
                        min_value=1.0, 
                        max_value=5.0, 
                        step=0.5, 
                        value=3.0
                    )
                    
                    submitted = st.form_submit_button("Set Expectation")
                    if submitted:
                        success, message = set_skill_expectation(
                            selected_level, 
                            selected_comp, 
                            selected_skill, 
                            expected_score
                        )
                        if success:
                            st.success(message)
                            close_modal("add_expectation")
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("No skills found for the selected competency.")
                    st.form_submit_button("Set Expectation", disabled=True)
        
            if st.button("Cancel", type="secondary"):
                close_modal("add_expectation")
                st.rerun()
        
        render_modal("Set New Expectation", add_expectation_modal, "add_expectation")
        
        # View existing expectations
        st.subheader("Existing Skill Expectations")
        
        if not expectations_df.empty:
            # Display expectations by job level
            level_names = expectations_df["job_level"].unique()
            
            for level in level_names:
                with st.expander(f"Level: {level}", expanded=True):
                    # Filter expectations for this level
                    level_exps = expectations_df[expectations_df["job_level"] == level]
                    
                    # Group by competency
                    for comp in level_exps["competency"].unique():
                        st.subheader(comp)
                        
                        # Get skills for this competency
                        comp_skills = level_exps[level_exps["competency"] == comp]
                        
                        # Create a formatted table
                        formatted_data = []
                        for _, row in comp_skills.iterrows():
                            formatted_data.append({
                                "Skill": row["skill"],
                                "Expected Score": row["expected_score"],
                                "expectation_id": row["expectation_id"]
                            })
                        
                        if formatted_data:
                            exp_df = pd.DataFrame(formatted_data)
                            
                            # Display as table
                            st.dataframe(
                                exp_df[["Skill", "Expected Score"]],
                                hide_index=True,
                                use_container_width=True
                            )
                            
                            # Add delete buttons for each expectation
                            for _, exp in exp_df.iterrows():
                                cols = st.columns([3, 1])
                                with cols[0]:
                                    st.write(f"{exp['Skill']}: {exp['Expected Score']}")
                                with cols[1]:
                                    if st.button("🗑️ Delete", key=f"del_exp_{exp['expectation_id']}", use_container_width=True):
                                        success, message = delete_expectation(level, comp, exp["Skill"])
                                        if success:
                                            st.success(message)
                                            st.rerun()
                                        else:
                                            st.error(message)
                        else:
                            st.info(f"No expectations set for {comp} in {level}.")
        else:
            st.info("No skill expectations set yet.")

# Competency Expectations Tab
with tab4:
    st.header("Competency Expectations")
    st.write("Set the expected overall competency scores for each job level.")
    
    levels_df = load_data("levels")
    competencies_df = load_data("competencies")
    comp_expectations_df = load_data("comp_expectations")
    
    if levels_df.empty or competencies_df.empty:
        st.warning("You need to set up job levels and competencies first.")
    else:
        # Add new competency expectation button
        if st.button("➕ Set New Competency Expectation", type="primary", use_container_width=True):
            open_modal("add_comp_expectation")
            st.rerun()
        
        # Modal for adding a new competency expectation
        def add_comp_expectation_modal():
            with st.form("add_comp_expectation_form"):
                # Select job level
                level_options = levels_df["name"].tolist()
                selected_level = st.selectbox("Select Job Level", level_options, key="comp_exp_level")
                
                # Select competency
                comp_options = competencies_df["name"].tolist()
                selected_comp = st.selectbox("Select Competency", comp_options, key="comp_exp_comp")
                
                # Set expected score
                expected_score = st.slider(
                    "Expected Score", 
                    min_value=1.0, 
                    max_value=5.0, 
                    step=0.5, 
                    value=3.0
                )
                
                submitted = st.form_submit_button("Set Expectation")
                if submitted:
                    success, message = set_competency_expectation(
                        selected_level, 
                        selected_comp, 
                        expected_score
                    )
                    if success:
                        st.success(message)
                        close_modal("add_comp_expectation")
                        st.rerun()
                    else:
                        st.error(message)
        
            if st.button("Cancel", type="secondary"):
                close_modal("add_comp_expectation")
                st.rerun()
        
        render_modal("Set New Competency Expectation", add_comp_expectation_modal, "add_comp_expectation")
        
        # View existing competency expectations
        st.subheader("Existing Competency Expectations")
        
        if not comp_expectations_df.empty:
            # Display expectations by job level
            level_names = comp_expectations_df["job_level"].unique()
            
            for level in level_names:
                with st.expander(f"Level: {level}", expanded=True):
                    # Filter expectations for this level
                    level_exps = comp_expectations_df[comp_expectations_df["job_level"] == level]
                    
                    # Create a formatted table
                    formatted_data = []
                    for _, row in level_exps.iterrows():
                        formatted_data.append({
                            "Competency": row["competency"],
                            "Expected Score": row["expected_score"],
                            "expectation_id": row["expectation_id"]
                        })
                    
                    if formatted_data:
                        exp_df = pd.DataFrame(formatted_data)
                        
                        # Display as table
                        st.dataframe(
                            exp_df[["Competency", "Expected Score"]],
                            hide_index=True,
                            use_container_width=True
                        )
                        
                        # Add delete buttons for each expectation
                        for _, exp in exp_df.iterrows():
                            cols = st.columns([3, 1])
                            with cols[0]:
                                st.write(f"{exp['Competency']}: {exp['Expected Score']}")
                            with cols[1]:
                                if st.button("🗑️ Delete", key=f"del_comp_exp_{exp['expectation_id']}", use_container_width=True):
                                    success, message = delete_competency_expectation(level, exp["Competency"])
                                    if success:
                                        st.success(message)
                                        st.rerun()
                                    else:
                                        st.error(message)
                    else:
                        st.info(f"No competency expectations set for {level}.")
        else:
            st.info("No competency expectations set yet.")

# Manage Employees Tab
with tab5:
    st.header("Manage Employees")
    
    employees_df = load_data("employees")
    job_levels_df = load_data("levels")
    
    # Add new employee button
    if st.button("➕ Add New Employee", type="primary", use_container_width=True):
        open_modal("add_employee")
        st.rerun()
    
    # View existing employees
    st.subheader("All Employees")
    
    if not employees_df.empty:
        # Display employees in a table
        st.dataframe(
            employees_df[["name", "email", "job_title", "job_level", "department", "manager_id"]],
            column_config={
                "name": "Name",
                "email": "Email",
                "job_title": "Job Title",
                "job_level": "Job Level",
                "department": "Department",
                "manager_id": "Manager ID"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Define edit and delete functions for employees
        def edit_employee(employee_id):
            employee_data = employees_df[employees_df["employee_id"] == employee_id].iloc[0]
            st.session_state["edit_employee_id"] = employee_id
            st.session_state["edit_employee_name"] = employee_data["name"]
            st.session_state["edit_employee_email"] = employee_data["email"]
            st.session_state["edit_employee_job_title"] = employee_data["job_title"]
            st.session_state["edit_employee_job_level"] = employee_data["job_level"]
            st.session_state["edit_employee_department"] = employee_data["department"]
            st.session_state["edit_employee_manager_id"] = employee_data["manager_id"]
            open_modal("edit_employee")
            st.rerun()
        
        def delete_employee_action(employee_id):
            employee_data = employees_df[employees_df["employee_id"] == employee_id].iloc[0]
            st.session_state["delete_employee_id"] = employee_id
            st.session_state["delete_employee_name"] = employee_data["name"]
            open_modal("delete_employee")
            st.rerun()
        
        # For each employee, create edit and delete buttons
        for _, employee in employees_df.iterrows():
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.write(f"{employee['name']}: {employee['job_title']} ({employee['job_level']})")
            with cols[1]:
                if st.button("✏️ Edit", key=f"edit_emp_{employee['employee_id']}", use_container_width=True):
                    edit_employee(employee["employee_id"])
            with cols[2]:
                if st.button("🗑️ Delete", key=f"delete_emp_{employee['employee_id']}", use_container_width=True):
                    delete_employee_action(employee["employee_id"])
    else:
        st.info("No employees added yet.")
    
    # Modal for adding a new employee
    def add_employee_modal():
        from data_manager import add_employee
        
        with st.form("add_employee_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            job_title = st.text_input("Job Title")
            
            # Job level selection
            if not job_levels_df.empty:
                job_level_options = job_levels_df["name"].tolist()
                job_level = st.selectbox("Job Level", job_level_options)
            else:
                job_level = st.text_input("Job Level")
                st.warning("No job levels found. Consider adding job levels first.")
            
            department = st.text_input("Department")
            
            # Manager selection
            if not employees_df.empty:
                manager_options = [("None", "None")] + [(row["employee_id"], row["name"]) for _, row in employees_df.iterrows()]
                manager_labels = [m[1] for m in manager_options]
                manager_ids = [m[0] for m in manager_options]
                
                selected_manager = st.selectbox("Manager", manager_labels)
                manager_idx = manager_labels.index(selected_manager)
                manager_id = manager_ids[manager_idx]
                
                if manager_id == "None":
                    manager_id = None
            else:
                manager_id = None
                st.info("No existing employees to select as manager.")
            
            hire_date = st.date_input("Hire Date")
            
            submitted = st.form_submit_button("Add Employee")
            if submitted:
                if name and email:
                    success, message, _ = add_employee(
                        name, 
                        email, 
                        job_title, 
                        job_level, 
                        department, 
                        manager_id, 
                        hire_date.strftime("%Y-%m-%d") if hire_date else None
                    )
                    if success:
                        st.success(message)
                        close_modal("add_employee")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a name and email")
        
        if st.button("Cancel", type="secondary"):
            close_modal("add_employee")
            st.rerun()
    
    render_modal("Add New Employee", add_employee_modal, "add_employee", width=800)
    
    # Modal for editing an employee
    def edit_employee_modal():
        employee_id = st.session_state.get("edit_employee_id")
        
        with st.form("edit_employee_form"):
            name = st.text_input("Name", value=st.session_state.get("edit_employee_name", ""))
            email = st.text_input("Email", value=st.session_state.get("edit_employee_email", ""))
            job_title = st.text_input("Job Title", value=st.session_state.get("edit_employee_job_title", ""))
            
            # Job level selection
            if not job_levels_df.empty:
                job_level_options = job_levels_df["name"].tolist()
                current_level = st.session_state.get("edit_employee_job_level", "")
                level_index = 0
                if current_level in job_level_options:
                    level_index = job_level_options.index(current_level)
                job_level = st.selectbox("Job Level", job_level_options, index=level_index)
            else:
                job_level = st.text_input("Job Level", value=st.session_state.get("edit_employee_job_level", ""))
            
            department = st.text_input("Department", value=st.session_state.get("edit_employee_department", ""))
            
            # Manager selection
            current_manager_id = st.session_state.get("edit_employee_manager_id")
            if not employees_df.empty:
                # Filter out the current employee from potential managers
                potential_managers = employees_df[employees_df["employee_id"] != employee_id]
                
                manager_options = [("None", "None")] + [(row["employee_id"], row["name"]) for _, row in potential_managers.iterrows()]
                manager_labels = [m[1] for m in manager_options]
                manager_ids = [m[0] for m in manager_options]
                
                # Find the index of the current manager
                manager_index = 0  # Default to "None"
                if current_manager_id in manager_ids:
                    manager_index = manager_ids.index(current_manager_id)
                
                selected_manager = st.selectbox("Manager", manager_labels, index=manager_index)
                manager_idx = manager_labels.index(selected_manager)
                manager_id = manager_ids[manager_idx]
                
                if manager_id == "None":
                    manager_id = None
            else:
                manager_id = None
                st.info("No existing employees to select as manager.")
            
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                if name and email:
                    success, message = update_employee(
                        employee_id,
                        name,
                        email,
                        job_title,
                        job_level,
                        department,
                        manager_id
                    )
                    if success:
                        st.success(message)
                        close_modal("edit_employee")
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a name and email")
        
        if st.button("Cancel", type="secondary"):
            close_modal("edit_employee")
            st.rerun()
    
    render_modal("Edit Employee", edit_employee_modal, "edit_employee", width=800)
    
    # Modal for deleting an employee
    def delete_employee_modal():
        employee_id = st.session_state.get("delete_employee_id")
        employee_name = st.session_state.get("delete_employee_name", "")
        
        st.warning(f"Are you sure you want to delete employee '{employee_name}'? This will also delete all associated assessments.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete", type="primary", use_container_width=True):
                success, message = delete_employee(employee_id)
                if success:
                    st.success(message)
                    close_modal("delete_employee")
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            if st.button("Cancel", type="secondary", use_container_width=True):
                close_modal("delete_employee")
                st.rerun()
    
    render_modal("Delete Employee", delete_employee_modal, "delete_employee")