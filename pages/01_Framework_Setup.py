import streamlit as st
import pandas as pd
from data_manager import (
    load_data, save_data, add_competency, add_skill, 
    add_job_level, set_skill_expectation, set_competency_expectation, get_competency_skills,
    delete_competency, delete_skill, delete_job_level, delete_employee,
    delete_expectation, update_competency, update_skill, update_job_level,
    update_employee
)
from utils import check_permission

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
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add New Competency")
        comp_name = st.text_input("Competency Name")
        comp_desc = st.text_area("Description")
        
        if st.button("Add Competency"):
            if comp_name:
                success, message, _ = add_competency(comp_name, comp_desc)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Please enter a competency name")
    
    with col2:
        st.subheader("Add New Skill")
        competencies_df = load_data("competencies")
        
        if competencies_df.empty:
            st.warning("You need to add competencies first.")
        else:
            comp_options = competencies_df["name"].tolist()
            selected_comp = st.selectbox("Select Competency", comp_options, key="add_skill_comp")
            
            # Get the competency ID
            selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]
            
            skill_name = st.text_input("Skill Name")
            skill_desc = st.text_area("Skill Description")
            
            if st.button("Add Skill"):
                if skill_name:
                    success, message, _ = add_skill(selected_comp_id, skill_name, skill_desc)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a skill name")
    
    # View existing competencies and skills with edit/delete options
    st.subheader("Existing Competencies & Skills")
    competencies_df = load_data("competencies")
    skills_df = load_data("skills")
    
    # Display management instructions
    st.info("Expand a competency to view, edit, or delete its details and associated skills.")
    
    if not competencies_df.empty:
        for _, comp_row in competencies_df.iterrows():
            comp_id = comp_row["competency_id"]
            with st.expander(f"{comp_row['name']} (ID: {comp_id})"):
                # Create columns for competency actions
                comp_col1, comp_col2, comp_col3 = st.columns([2, 1, 1])
                
                with comp_col1:
                    st.write(f"**Description:** {comp_row['description']}")
                
                with comp_col2:
                    # Edit competency button
                    if st.button(f"Edit Competency #{comp_id}", key=f"edit_comp_{comp_id}"):
                        # Set session state to store the competency being edited
                        st.session_state[f"edit_comp_id_{comp_id}"] = True
                
                with comp_col3:
                    # Delete competency button
                    if st.button(f"Delete Competency #{comp_id}", key=f"del_comp_{comp_id}"):
                        success, message = delete_competency(comp_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                # Display edit form if the edit button was clicked
                if st.session_state.get(f"edit_comp_id_{comp_id}", False):
                    st.markdown("### Edit Competency")
                    new_name = st.text_input("Name", value=comp_row["name"], key=f"comp_name_{comp_id}")
                    new_desc = st.text_area("Description", value=comp_row["description"], key=f"comp_desc_{comp_id}")
                    
                    edit_col1, edit_col2 = st.columns([1, 1])
                    with edit_col1:
                        if st.button("Save Changes", key=f"save_comp_{comp_id}"):
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
                
                st.markdown("---")
                st.write("**Skills:**")
                
                comp_skills = get_competency_skills(comp_id)
                if not comp_skills.empty:
                    # Create a table-like display for skills with actions
                    for _, skill_row in comp_skills.iterrows():
                        skill_id = skill_row["skill_id"]
                        skill_col1, skill_col2, skill_col3 = st.columns([3, 1, 1])
                        
                        with skill_col1:
                            st.write(f"**{skill_row['name']}**: {skill_row['description']}")
                        
                        with skill_col2:
                            # Edit skill button
                            if st.button(f"Edit", key=f"edit_skill_{skill_id}"):
                                st.session_state[f"edit_skill_id_{skill_id}"] = True
                        
                        with skill_col3:
                            # Delete skill button
                            if st.button(f"Delete", key=f"del_skill_{skill_id}"):
                                success, message = delete_skill(skill_id)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        
                        # Display edit form if the edit button was clicked
                        if st.session_state.get(f"edit_skill_id_{skill_id}", False):
                            st.markdown("### Edit Skill")
                            new_skill_name = st.text_input("Name", value=skill_row["name"], key=f"skill_name_{skill_id}")
                            new_skill_desc = st.text_area("Description", value=skill_row["description"], key=f"skill_desc_{skill_id}")
                            
                            skill_edit_col1, skill_edit_col2 = st.columns([1, 1])
                            with skill_edit_col1:
                                if st.button("Save Changes", key=f"save_skill_{skill_id}"):
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
                        
                        st.markdown("---")
                else:
                    st.write("No skills added yet.")
    else:
        st.info("No competencies added yet.")

# Job Levels Tab
with tab2:
    st.header("Job Levels")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add New Job Level")
        level_name = st.text_input("Level Name")
        level_desc = st.text_area("Level Description")
        
        if st.button("Add Job Level"):
            if level_name:
                success, message, _ = add_job_level(level_name, level_desc)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Please enter a job level name")
    
    with col2:
        st.subheader("Existing Job Levels")
        levels_df = load_data("levels")
        
        if not levels_df.empty:
            # Display management instructions
            st.info("Select a job level to edit or delete")
            
            # Create a selection box for job levels
            level_options = [(row["level_id"], f"{row['name']} (ID: {row['level_id']})") for _, row in levels_df.iterrows()]
            level_labels = [l[1] for l in level_options]
            level_ids = [l[0] for l in level_options]
            
            if level_labels:
                selected_level_label = st.selectbox("Select Job Level", level_labels, key="select_level_to_manage")
                selected_idx = level_labels.index(selected_level_label)
                selected_level_id = level_ids[selected_idx]
                
                # Get the selected level details
                selected_level = levels_df[levels_df["level_id"] == selected_level_id].iloc[0]
                
                # Display the level details
                st.write(f"**Name:** {selected_level['name']}")
                st.write(f"**Description:** {selected_level['description']}")
                
                # Create action buttons
                action_col1, action_col2 = st.columns([1, 1])
                
                with action_col1:
                    if st.button("Edit Job Level", key=f"edit_level_{selected_level_id}"):
                        st.session_state[f"edit_level_id_{selected_level_id}"] = True
                
                with action_col2:
                    if st.button("Delete Job Level", key=f"del_level_{selected_level_id}"):
                        success, message = delete_job_level(selected_level_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                # Edit form
                if st.session_state.get(f"edit_level_id_{selected_level_id}", False):
                    st.markdown("### Edit Job Level")
                    new_name = st.text_input("Name", value=selected_level["name"], key=f"level_name_{selected_level_id}")
                    new_desc = st.text_area("Description", value=selected_level["description"], key=f"level_desc_{selected_level_id}")
                    
                    edit_col1, edit_col2 = st.columns([1, 1])
                    with edit_col1:
                        if st.button("Save Changes", key=f"save_level_{selected_level_id}"):
                            success, message = update_job_level(selected_level_id, new_name, new_desc)
                            if success:
                                st.success(message)
                                # Clear the editing state
                                st.session_state.pop(f"edit_level_id_{selected_level_id}", None)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with edit_col2:
                        if st.button("Cancel", key=f"cancel_level_{selected_level_id}"):
                            # Clear the editing state
                            st.session_state.pop(f"edit_level_id_{selected_level_id}", None)
                            st.rerun()
            
            # Also show a table of all levels for reference
            st.markdown("### All Job Levels")
            st.dataframe(levels_df[["level_id", "name", "description"]])
        else:
            st.info("No job levels added yet.")

# Skill Expectations Tab
with tab3:
    st.header("Skill Expectations")
    st.write("Set the expected skill scores for each job level.")
    
    levels_df = load_data("levels")
    competencies_df = load_data("competencies")
    skills_df = load_data("skills")
    
    if levels_df.empty or competencies_df.empty or skills_df.empty:
        st.warning("You need to set up job levels, competencies, and skills first.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Set Expected Scores")
            
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
                
                if st.button("Set Expectation"):
                    success, message = set_skill_expectation(
                        selected_level, 
                        selected_comp, 
                        selected_skill, 
                        expected_score
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            else:
                st.warning("No skills found for the selected competency.")
        
        with col2:
            st.subheader("Current Expectations")
            expectations_df = load_data("expectations")
            
            if not expectations_df.empty:
                # Filter for selected level if one is chosen
                if selected_level:
                    filtered_exp = expectations_df[expectations_df["job_level"] == selected_level]
                    if not filtered_exp.empty:
                        # Display a table with delete buttons
                        st.info("Click Delete to remove an expectation")
                        
                        for i, row in filtered_exp.iterrows():
                            exp_cols = st.columns([3, 1])
                            with exp_cols[0]:
                                st.write(f"**{row['competency']} - {row['skill']}**: Expected score {row['expected_score']}")
                            
                            with exp_cols[1]:
                                if st.button("Delete", key=f"del_exp_{i}"):
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
                                        
                        # Also show a table for reference
                        st.markdown("### All Expectations for this Level")
                        st.dataframe(filtered_exp)
                    else:
                        st.info(f"No expectations set for {selected_level} yet.")
                else:
                    # Show all expectations with a select box to choose which one to delete
                    st.info("Select an expectation to delete")
                    
                    # Create a selection box for expectations
                    exp_options = [
                        (i, f"{row['job_level']} - {row['competency']} - {row['skill']}: {row['expected_score']}") 
                        for i, row in expectations_df.iterrows()
                    ]
                    exp_labels = [e[1] for e in exp_options]
                    exp_indices = [e[0] for e in exp_options]
                    
                    if exp_labels:
                        selected_exp_label = st.selectbox("Select Expectation", exp_labels, key="select_expectation_to_manage")
                        selected_idx = exp_labels.index(selected_exp_label)
                        selected_exp_idx = exp_indices[selected_idx]
                        
                        # Get the selected expectation
                        selected_exp = expectations_df.iloc[selected_exp_idx]
                        
                        # Create action button
                        if st.button("Delete Selected Expectation"):
                            success, message = delete_expectation(
                                selected_exp["job_level"],
                                selected_exp["competency"],
                                selected_exp["skill"]
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    # Also show all expectations in a table
                    st.markdown("### All Expectations")
                    st.dataframe(expectations_df)
            else:
                st.info("No skill expectations set yet.")

# Competency Expectations Tab
with tab4:
    st.header("Competency Expectations")
    st.write("Set the expected competency scores for each job level (separate from skills).")
    
    levels_df = load_data("levels")
    competencies_df = load_data("competencies")
    
    if levels_df.empty or competencies_df.empty:
        st.warning("You need to set up job levels and competencies first.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Set Competency Expected Scores")
            
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
            
            if st.button("Set Competency Expectation"):
                success, message = set_competency_expectation(
                    selected_level, 
                    selected_comp, 
                    expected_score
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        with col2:
            st.subheader("Current Competency Expectations")
            comp_expectations_df = load_data("comp_expectations")
            
            if not comp_expectations_df.empty:
                # Filter for selected level if one is chosen
                if selected_level:
                    filtered_exp = comp_expectations_df[comp_expectations_df["job_level"] == selected_level]
                    if not filtered_exp.empty:
                        # Display a table with delete buttons
                        st.info("Click Delete to remove a competency expectation")
                        
                        for i, row in filtered_exp.iterrows():
                            exp_cols = st.columns([3, 1])
                            with exp_cols[0]:
                                st.write(f"**{row['competency']}**: Expected score {row['expected_score']}")
                            
                            with exp_cols[1]:
                                if st.button("Delete", key=f"del_comp_exp_{i}"):
                                    # Create delete_competency_expectation function implementation
                                    # For now we'll handle it directly
                                    comp_expectations_df = comp_expectations_df.drop(i)
                                    save_data("comp_expectations", comp_expectations_df)
                                    st.success("Competency expectation deleted successfully")
                                    st.rerun()
                                        
                        # Also show a table for reference
                        st.markdown("### All Competency Expectations for this Level")
                        st.dataframe(filtered_exp)
                    else:
                        st.info(f"No competency expectations set for {selected_level} yet.")
                else:
                    # Show all expectations with a select box to choose which one to delete
                    st.info("Select a competency expectation to delete")
                    
                    # Create a selection box for expectations
                    exp_options = [
                        (i, f"{row['job_level']} - {row['competency']}: {row['expected_score']}") 
                        for i, row in comp_expectations_df.iterrows()
                    ]
                    exp_labels = [e[1] for e in exp_options]
                    exp_indices = [e[0] for e in exp_options]
                    
                    if exp_labels:
                        selected_exp_label = st.selectbox("Select Expectation", exp_labels, key="select_comp_expectation_to_manage")
                        selected_idx = exp_labels.index(selected_exp_label)
                        selected_exp_idx = exp_indices[selected_idx]
                        
                        # Get the selected expectation
                        selected_exp = comp_expectations_df.iloc[selected_exp_idx]
                        
                        # Create action button
                        if st.button("Delete Selected Competency Expectation"):
                            # Handle deletion directly
                            comp_expectations_df = comp_expectations_df.drop(selected_exp_idx)
                            save_data("comp_expectations", comp_expectations_df)
                            st.success("Competency expectation deleted successfully")
                            st.rerun()
                    
                    # Also show all expectations in a table
                    st.markdown("### All Competency Expectations")
                    st.dataframe(comp_expectations_df)
            else:
                st.info("No competency expectations set yet.")

# Manage Employees Tab
with tab5:
    st.header("Manage Employees")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add New Employee")
        
        # Get job levels for dropdown
        levels_df = load_data("levels")
        level_options = [""] + levels_df["name"].tolist() if not levels_df.empty else [""]
        
        # Get managers for dropdown
        employees_df = load_data("employees")
        manager_options = [("", "None")] + [
            (str(row["employee_id"]), row["name"]) 
            for _, row in employees_df.iterrows()
        ] if not employees_df.empty else [("", "None")]
        
        manager_names = [m[1] for m in manager_options]
        manager_ids = [m[0] for m in manager_options]
        
        # Form for adding new employee
        emp_name = st.text_input("Employee Name")
        emp_email = st.text_input("Email")
        emp_title = st.text_input("Job Title")
        emp_level = st.selectbox("Job Level", level_options, key="emp_level")
        emp_dept = st.text_input("Department")
        selected_manager = st.selectbox("Manager", manager_names, key="emp_manager")
        
        # Get manager ID from selection
        selected_manager_idx = manager_names.index(selected_manager)
        selected_manager_id = manager_ids[selected_manager_idx]
        
        emp_date = st.date_input("Hire Date")
        
        if st.button("Add Employee"):
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
                else:
                    st.error(message)
            else:
                st.warning("Please fill in all required fields.")
    
    with col2:
        st.subheader("Manage Existing Employees")
        employees_df = load_data("employees")
        
        if not employees_df.empty:
            # Display management instructions
            st.info("Select an employee to edit or delete")
            
            # Create a selection box for employees
            employee_options = [
                (row["employee_id"], f"{row['name']} (ID: {row['employee_id']})") 
                for _, row in employees_df.iterrows()
            ]
            employee_labels = [e[1] for e in employee_options]
            employee_ids = [e[0] for e in employee_options]
            
            if employee_labels:
                selected_emp_label = st.selectbox("Select Employee", employee_labels, key="select_employee_to_manage")
                selected_idx = employee_labels.index(selected_emp_label)
                selected_emp_id = employee_ids[selected_idx]
                
                # Get the selected employee details
                selected_emp = employees_df[employees_df["employee_id"] == selected_emp_id].iloc[0]
                
                # Create a mapping of employee IDs to names for manager display
                emp_id_to_name = dict(zip(employees_df["employee_id"], employees_df["name"]))
                manager_name = emp_id_to_name.get(selected_emp["manager_id"], "None") if pd.notna(selected_emp["manager_id"]) else "None"
                
                # Display the employee details
                st.write(f"**Name:** {selected_emp['name']}")
                st.write(f"**Email:** {selected_emp['email']}")
                st.write(f"**Job Title:** {selected_emp['job_title']}")
                st.write(f"**Job Level:** {selected_emp['job_level']}")
                st.write(f"**Department:** {selected_emp['department']}")
                st.write(f"**Manager:** {manager_name}")
                st.write(f"**Hire Date:** {selected_emp['hire_date']}")
                
                # Create action buttons
                action_col1, action_col2 = st.columns([1, 1])
                
                with action_col1:
                    if st.button("Edit Employee", key=f"edit_emp_{selected_emp_id}"):
                        st.session_state[f"edit_emp_id_{selected_emp_id}"] = True
                
                with action_col2:
                    if st.button("Delete Employee", key=f"del_emp_{selected_emp_id}"):
                        success, message = delete_employee(selected_emp_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                # Edit form
                if st.session_state.get(f"edit_emp_id_{selected_emp_id}", False):
                    st.markdown("### Edit Employee")
                    
                    # Get job levels for dropdown
                    levels_df = load_data("levels")
                    level_options = levels_df["name"].tolist() if not levels_df.empty else []
                    
                    # Get managers for dropdown (exclude the current employee)
                    manager_options = [("", "None")] + [
                        (str(row["employee_id"]), row["name"]) 
                        for _, row in employees_df.iterrows() 
                        if row["employee_id"] != selected_emp_id
                    ]
                    
                    manager_names = [m[1] for m in manager_options]
                    manager_ids = [m[0] for m in manager_options]
                    
                    # Find the current manager in the options
                    current_manager_id = selected_emp["manager_id"] if pd.notna(selected_emp["manager_id"]) else ""
                    current_manager_idx = 0  # Default to "None"
                    for i, m_id in enumerate(manager_ids):
                        if str(current_manager_id) == str(m_id):
                            current_manager_idx = i
                            break
                    
                    # Input fields
                    new_name = st.text_input("Name", value=selected_emp["name"], key=f"emp_name_{selected_emp_id}")
                    new_email = st.text_input("Email", value=selected_emp["email"], key=f"emp_email_{selected_emp_id}")
                    new_title = st.text_input("Job Title", value=selected_emp["job_title"], key=f"emp_title_{selected_emp_id}")
                    
                    # Job level dropdown
                    level_idx = level_options.index(selected_emp["job_level"]) if selected_emp["job_level"] in level_options else 0
                    new_level = st.selectbox("Job Level", level_options, index=level_idx, key=f"emp_level_{selected_emp_id}")
                    
                    new_dept = st.text_input("Department", value=selected_emp["department"], key=f"emp_dept_{selected_emp_id}")
                    
                    # Manager dropdown
                    new_manager_name = st.selectbox("Manager", manager_names, index=current_manager_idx, key=f"emp_manager_{selected_emp_id}")
                    manager_idx = manager_names.index(new_manager_name)
                    new_manager_id = manager_ids[manager_idx]
                    
                    # Convert manager ID to integer if it's not empty
                    new_manager_id = int(new_manager_id) if new_manager_id else None
                    
                    edit_col1, edit_col2 = st.columns([1, 1])
                    with edit_col1:
                        if st.button("Save Changes", key=f"save_emp_{selected_emp_id}"):
                            success, message = update_employee(
                                selected_emp_id,
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
                                st.session_state.pop(f"edit_emp_id_{selected_emp_id}", None)
                                st.rerun()
                            else:
                                st.error(message)
                    
                    with edit_col2:
                        if st.button("Cancel", key=f"cancel_emp_{selected_emp_id}"):
                            # Clear the editing state
                            st.session_state.pop(f"edit_emp_id_{selected_emp_id}", None)
                            st.rerun()
            
            # Also show a table of all employees for reference
            st.markdown("### All Employees")
            display_df = employees_df.copy()
            
            # Join with manager names
            if "manager_id" in display_df.columns:
                # Map manager IDs to names
                display_df["manager"] = display_df["manager_id"].map(
                    lambda x: emp_id_to_name.get(x, "None") if pd.notna(x) else "None"
                )
            
            st.dataframe(display_df[["employee_id", "name", "email", "job_title", "job_level", "department", "manager", "hire_date"]])
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
