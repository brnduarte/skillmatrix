import streamlit as st
import pandas as pd
from datetime import datetime
from data_manager import (
    load_data, add_assessment, get_employee_assessments,
    get_latest_assessment, get_competency_skills
)
from utils import check_permission, get_user_id, is_manager_of, get_employees_for_manager

# Page configuration
st.set_page_config(
    page_title="Employee Assessment - Skill Matrix",
    page_icon="📋",
    layout="wide"
)

# Check if user is authenticated
if not hasattr(st.session_state, "authenticated") or not st.session_state.authenticated:
    st.warning("Please login from the Home page.")
    st.stop()

st.title("Employee Skill Assessment")

# Get current employee ID (for self-assessment)
employee_id = get_user_id(st.session_state.username)

# Check if framework is set up
competencies_df = load_data("competencies")
skills_df = load_data("skills")

if competencies_df.empty or skills_df.empty:
    st.error("The competency framework has not been set up yet. Please ask an administrator to set it up.")
    st.stop()

# Email users only see self-assessment
if st.session_state.user_role == "email_user":
    # Self Assessment Section (no tabs)
    st.header("Self Assessment")
    
    if employee_id is None:
        st.warning("Your user account is not linked to an employee record. Please contact an administrator.")
    else:
        employees_df = load_data("employees")
        employee_info = employees_df[employees_df["employee_id"] == employee_id]
        
        if not employee_info.empty:
            st.write(f"Employee: **{employee_info.iloc[0]['name']}**")
            st.write(f"Job Title: {employee_info.iloc[0]['job_title']}")
            st.write(f"Job Level: {employee_info.iloc[0]['job_level']}")
            st.write(f"Department: {employee_info.iloc[0]['department']}")
            
            st.markdown("---")
            
            # Get existing assessments
            assessments = get_employee_assessments(employee_id, "self")
            
            # Select competency for assessment
            st.subheader("Rate Your Skills")
            
            comp_options = competencies_df["name"].tolist()
            selected_comp = st.selectbox("Select Competency", comp_options, key="self_comp")
            
            # Get competency ID
            selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]
            
            # Get skills for selected competency
            comp_skills = get_competency_skills(selected_comp_id)
            
            if not comp_skills.empty:
                st.write(f"Rate your proficiency in these skills from 1 to 5:")
                st.write("1: Novice, 2: Advanced Beginner, 3: Competent, 4: Proficient, 5: Expert")
                
                skill_scores = {}
                skill_notes = {}
                
                for _, skill_row in comp_skills.iterrows():
                    skill_name = skill_row["name"]
                    
                    # Check if there's an existing assessment for this skill
                    existing = get_latest_assessment(employee_id, selected_comp, skill_name, "self")
                    
                    # Set default value based on existing assessment if available
                    default_value = float(existing["score"]) if existing is not None else 3.0
                    default_notes = existing["notes"] if existing is not None else ""
                    
                    # Create expander for each skill
                    with st.expander(f"{skill_name} - {skill_row['description']}"):
                        skill_scores[skill_name] = st.slider(
                            f"Your rating for {skill_name}",
                            min_value=1.0,
                            max_value=5.0,
                            step=0.5,
                            value=default_value,
                            key=f"self_{skill_name}"
                        )
                        
                        skill_notes[skill_name] = st.text_area(
                            "Notes (examples, achievements, areas for improvement)",
                            value=default_notes,
                            key=f"self_notes_{skill_name}"
                        )
                
                # Submit button for all skills in this competency
                if st.button("Submit Self Assessment", key="submit_self"):
                    for skill_name, score in skill_scores.items():
                        success, message, _ = add_assessment(
                            employee_id,
                            selected_comp,
                            skill_name,
                            score,
                            "self",
                            skill_notes[skill_name]
                        )
                        
                        if success:
                            st.success(f"Assessment for {skill_name} submitted successfully.")
                        else:
                            st.error(f"Error submitting assessment for {skill_name}: {message}")
            else:
                st.info(f"No skills found for {selected_comp}. Please contact an administrator.")
        else:
            st.warning("Employee record not found. Please contact an administrator.")
            
else:
    # For regular users (admin, manager, employee), show tabs
    tab1, tab2 = st.tabs(["Self Assessment", "Manager Assessment"])
    
    # Self Assessment Tab
    with tab1:
        st.header("Self Assessment")
        
        if employee_id is None:
            st.warning("Your user account is not linked to an employee record. Please contact an administrator.")
        else:
            employees_df = load_data("employees")
            employee_info = employees_df[employees_df["employee_id"] == employee_id]
            
            if not employee_info.empty:
                st.write(f"Employee: **{employee_info.iloc[0]['name']}**")
                st.write(f"Job Title: {employee_info.iloc[0]['job_title']}")
                st.write(f"Job Level: {employee_info.iloc[0]['job_level']}")
                st.write(f"Department: {employee_info.iloc[0]['department']}")
                
                st.markdown("---")
                
                # Get existing assessments
                assessments = get_employee_assessments(employee_id, "self")
                
                # Select competency for assessment
                st.subheader("Rate Your Skills")
                
                comp_options = competencies_df["name"].tolist()
                selected_comp = st.selectbox("Select Competency", comp_options, key="self_comp")
                
                # Get competency ID
                selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]
                
                # Get skills for selected competency
                comp_skills = get_competency_skills(selected_comp_id)
                
                if not comp_skills.empty:
                    st.write(f"Rate your proficiency in these skills from 1 to 5:")
                    st.write("1: Novice, 2: Advanced Beginner, 3: Competent, 4: Proficient, 5: Expert")
                    
                    skill_scores = {}
                    skill_notes = {}
                    
                    for _, skill_row in comp_skills.iterrows():
                        skill_name = skill_row["name"]
                        
                        # Check if there's an existing assessment for this skill
                        existing = get_latest_assessment(employee_id, selected_comp, skill_name, "self")
                        
                        # Set default value based on existing assessment if available
                        default_value = float(existing["score"]) if existing is not None else 3.0
                        default_notes = existing["notes"] if existing is not None else ""
                        
                        # Create expander for each skill
                        with st.expander(f"{skill_name} - {skill_row['description']}"):
                            skill_scores[skill_name] = st.slider(
                                f"Your rating for {skill_name}",
                                min_value=1.0,
                                max_value=5.0,
                                step=0.5,
                                value=default_value,
                                key=f"self_{skill_name}"
                            )
                            
                            skill_notes[skill_name] = st.text_area(
                                "Notes (examples, achievements, areas for improvement)",
                                value=default_notes,
                                key=f"self_notes_{skill_name}"
                            )
                    
                    # Submit button for all skills in this competency
                    if st.button("Submit Self Assessment", key="submit_self"):
                        for skill_name, score in skill_scores.items():
                            success, message, _ = add_assessment(
                                employee_id,
                                selected_comp,
                                skill_name,
                                score,
                                "self",
                                skill_notes[skill_name]
                            )
                            
                            if success:
                                st.success(f"Assessment for {skill_name} submitted successfully.")
                            else:
                                st.error(f"Error submitting assessment for {skill_name}: {message}")
                else:
                    st.info(f"No skills found for {selected_comp}. Please contact an administrator.")
            else:
                st.warning("Employee record not found. Please contact an administrator.")
    
    # Manager Assessment Tab
    with tab2:
        st.header("Manager Assessment")
        
        # Check if user is a manager
        if st.session_state.user_role in ["admin", "manager"]:
            employees_df = load_data("employees")
            
            # Get employees that this user manages
            if st.session_state.user_role == "admin":
                # Admins can assess anyone
                managed_employees = employees_df
            else:
                # Get the manager's employee ID
                manager_id = get_user_id(st.session_state.username)
                if manager_id is None:
                    st.warning("Your user account is not linked to an employee record. Please contact an administrator.")
                    managed_employees = pd.DataFrame()
                else:
                    managed_employees = get_employees_for_manager(manager_id)
            
            if not managed_employees.empty:
                # Select employee to assess
                employee_options = [(row["employee_id"], row["name"]) for _, row in managed_employees.iterrows()]
                employee_names = [e[1] for e in employee_options]
                employee_ids = [e[0] for e in employee_options]
                
                selected_emp_name = st.selectbox("Select Employee to Assess", employee_names)
                selected_emp_idx = employee_names.index(selected_emp_name)
                selected_emp_id = employee_ids[selected_emp_idx]
                
                # Get employee details
                employee_info = employees_df[employees_df["employee_id"] == selected_emp_id]
                
                if not employee_info.empty:
                    st.write(f"Employee: **{employee_info.iloc[0]['name']}**")
                    st.write(f"Job Title: {employee_info.iloc[0]['job_title']}")
                    st.write(f"Job Level: {employee_info.iloc[0]['job_level']}")
                    st.write(f"Department: {employee_info.iloc[0]['department']}")
                    
                    st.markdown("---")
                    
                    # Get existing assessments
                    assessments = get_employee_assessments(selected_emp_id, "manager")
                    
                    # Select competency for assessment
                    st.subheader("Rate Employee Skills")
                    
                    comp_options = competencies_df["name"].tolist()
                    selected_comp = st.selectbox("Select Competency", comp_options, key="manager_comp")
                    
                    # Get competency ID
                    selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]
                    
                    # Get skills for selected competency
                    comp_skills = get_competency_skills(selected_comp_id)
                    
                    if not comp_skills.empty:
                        st.write(f"Rate the employee's proficiency in these skills from 1 to 5:")
                        st.write("1: Novice, 2: Advanced Beginner, 3: Competent, 4: Proficient, 5: Expert")
                        
                        skill_scores = {}
                        skill_notes = {}
                        
                        for _, skill_row in comp_skills.iterrows():
                            skill_name = skill_row["name"]
                            
                            # Check if there's an existing assessment for this skill
                            existing = get_latest_assessment(selected_emp_id, selected_comp, skill_name, "manager")
                            
                            # Set default value based on existing assessment if available
                            default_value = float(existing["score"]) if existing is not None else 3.0
                            default_notes = existing["notes"] if existing is not None else ""
                            
                            # Create expander for each skill
                            with st.expander(f"{skill_name} - {skill_row['description']}"):
                                # Show employee's self-assessment if available
                                self_assessment = get_latest_assessment(selected_emp_id, selected_comp, skill_name, "self")
                                if self_assessment is not None:
                                    st.info(f"Employee's self-assessment: **{self_assessment['score']}** ({pd.to_datetime(self_assessment['assessment_date']).strftime('%Y-%m-%d')})")
                                    if self_assessment["notes"]:
                                        st.info(f"Employee's notes: {self_assessment['notes']}")
                                
                                skill_scores[skill_name] = st.slider(
                                    f"Your rating for {skill_name}",
                                    min_value=1.0,
                                    max_value=5.0,
                                    step=0.5,
                                    value=default_value,
                                    key=f"manager_{skill_name}"
                                )
                                
                                skill_notes[skill_name] = st.text_area(
                                    "Feedback and notes",
                                    value=default_notes,
                                    key=f"manager_notes_{skill_name}"
                                )
                        
                        # Submit button for all skills in this competency
                        if st.button("Submit Manager Assessment", key="submit_manager"):
                            for skill_name, score in skill_scores.items():
                                success, message, _ = add_assessment(
                                    selected_emp_id,
                                    selected_comp,
                                    skill_name,
                                    score,
                                    "manager",
                                    skill_notes[skill_name]
                                )
                                
                                if success:
                                    st.success(f"Assessment for {skill_name} submitted successfully.")
                                else:
                                    st.error(f"Error submitting assessment for {skill_name}: {message}")
                    else:
                        st.info(f"No skills found for {selected_comp}. Please contact an administrator.")
                else:
                    st.warning("Employee record not found.")
            else:
                st.info("You don't have any team members to assess.")
        else:
            st.info("You need to be a manager or administrator to assess employees.")

# Add explanatory text at the bottom
st.markdown("---")
st.markdown("""
### Assessment Guidelines

- Be honest in your self-assessment to identify growth opportunities
- Rate skills based on demonstrated behaviors and outcomes, not potential
- Consider concrete examples when assigning scores
- Use the notes field to provide context and examples
- Assessments should reflect current capabilities, not past or future potential
- The rating scale represents:
  - **1 (Novice)**: Basic understanding, needs guidance
  - **2 (Advanced Beginner)**: Can perform with support
  - **3 (Competent)**: Works independently on standard tasks
  - **4 (Proficient)**: Deep knowledge, can handle complex situations
  - **5 (Expert)**: Recognized authority, develops new approaches
""")
