import streamlit as st
import pandas as pd
from data_manager import (
    load_data, save_data, add_competency, add_skill, 
    add_job_level, set_skill_expectation, get_competency_skills
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
tab1, tab2, tab3, tab4 = st.tabs([
    "Competencies & Skills", 
    "Job Levels", 
    "Skill Expectations", 
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
            selected_comp = st.selectbox("Select Competency", comp_options)
            
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
    
    # View existing competencies and skills
    st.subheader("Existing Competencies & Skills")
    competencies_df = load_data("competencies")
    skills_df = load_data("skills")
    
    if not competencies_df.empty:
        for _, comp_row in competencies_df.iterrows():
            with st.expander(f"{comp_row['name']}"):
                st.write(f"**Description:** {comp_row['description']}")
                st.write("**Skills:**")
                
                comp_skills = get_competency_skills(comp_row["competency_id"])
                if not comp_skills.empty:
                    for _, skill_row in comp_skills.iterrows():
                        st.write(f"- {skill_row['name']}: {skill_row['description']}")
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
            st.dataframe(levels_df[["name", "description"]])
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
            selected_level = st.selectbox("Select Job Level", level_options)
            
            # Select competency
            comp_options = competencies_df["name"].tolist()
            selected_comp = st.selectbox("Select Competency", comp_options)
            
            # Get competency ID
            selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]
            
            # Get skills for selected competency
            comp_skills = get_competency_skills(selected_comp_id)
            
            if not comp_skills.empty:
                # Select skill
                skill_options = comp_skills["name"].tolist()
                selected_skill = st.selectbox("Select Skill", skill_options)
                
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
                        st.dataframe(filtered_exp)
                    else:
                        st.info(f"No expectations set for {selected_level} yet.")
                else:
                    st.dataframe(expectations_df)
            else:
                st.info("No skill expectations set yet.")

# Manage Employees Tab
with tab4:
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
        emp_level = st.selectbox("Job Level", level_options)
        emp_dept = st.text_input("Department")
        selected_manager = st.selectbox("Manager", manager_names)
        
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
        st.subheader("Existing Employees")
        employees_df = load_data("employees")
        
        if not employees_df.empty:
            display_df = employees_df.copy()
            
            # Join with manager names
            if "manager_id" in display_df.columns:
                # Create a mapping of employee IDs to names
                emp_id_to_name = dict(zip(employees_df["employee_id"], employees_df["name"]))
                
                # Map manager IDs to names
                display_df["manager"] = display_df["manager_id"].map(
                    lambda x: emp_id_to_name.get(x, "None") if pd.notna(x) else "None"
                )
            
            st.dataframe(display_df[["name", "email", "job_title", "job_level", "department", "manager", "hire_date"]])
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
5. Add employees and assign them to appropriate job levels and managers.

This framework will be used as the basis for skill assessments and visualizations throughout the application.
""")
