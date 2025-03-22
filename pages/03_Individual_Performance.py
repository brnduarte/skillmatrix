import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Individual Performance - Skill Matrix",
    page_icon="📈",
    layout="wide"
)

import pandas as pd
import numpy as np
from datetime import datetime
from data_manager import (
    load_data, load_data_for_organization, get_employee_assessments, calculate_employee_skill_means,
    calculate_employee_competency_means, get_competency_skills, get_latest_assessment
)
from utils import check_permission, check_page_access, get_user_id, is_manager_of, get_employees_for_manager, get_current_organization_id
from ui_helpers import load_custom_css
from visualizations import (
    employee_skill_radar, employee_competency_radar, comparison_radar_chart, 
    skill_improvement_chart, combined_skill_radar, combined_competency_radar,
    combined_comparison_radar_chart
)

# Load custom CSS for consistent styling
load_custom_css()

# This page is accessible to all roles except email_user (all users with proper accounts)
if not check_page_access(["admin", "manager", "employee"]):
    st.stop()

# Check if user is authenticated
if not hasattr(st.session_state, "authenticated") or not st.session_state.authenticated:
    st.warning("Please login from the Home page.")
    st.stop()

st.title("Individual Performance")

# Select employee to view
employee_id = None
if st.session_state.user_role == "employee":
    # Employees can only view themselves
    employee_id = get_user_id(st.session_state.username)
    if employee_id is None:
        st.warning("Your user account is not linked to an employee record. Please contact an administrator.")
        st.stop()
else:
    # Managers and admins can view employees
    organization_id = get_current_organization_id()
    employees_df = load_data_for_organization("employees", organization_id)
    
    if employees_df.empty:
        st.warning("No employees found in the system.")
        st.stop()
    
    if st.session_state.user_role == "admin":
        # Admins can view anyone
        available_employees = employees_df
    else:
        # Managers can view their team members
        manager_id = get_user_id(st.session_state.username)
        available_employees = get_employees_for_manager(manager_id)
        if available_employees.empty:
            st.info("You don't have any team members to view.")
            # Managers can also view themselves
            employee_id = manager_id
    
    if employee_id is None and not available_employees.empty:
        employee_options = [(row["employee_id"], row["name"]) for _, row in available_employees.iterrows()]
        employee_names = [e[1] for e in employee_options]
        employee_ids = [e[0] for e in employee_options]
        
        selected_emp_name = st.selectbox("Select Employee", employee_names, key="individual_performance_emp_select")
        selected_emp_idx = employee_names.index(selected_emp_name)
        employee_id = employee_ids[selected_emp_idx]

# If we have a valid employee ID, show their performance
if employee_id:
    organization_id = get_current_organization_id()
    employees_df = load_data_for_organization("employees", organization_id)
    employee_info = employees_df[employees_df["employee_id"] == employee_id]
    
    if not employee_info.empty:
        # Show employee details
        employee_name = employee_info.iloc[0]["name"]
        employee_job = employee_info.iloc[0]["job_title"]
        employee_level = employee_info.iloc[0]["job_level"]
        employee_dept = employee_info.iloc[0]["department"]
        
        st.write(f"### {employee_name}")
        st.write(f"**Job Title:** {employee_job}")
        st.write(f"**Job Level:** {employee_level}")
        st.write(f"**Department:** {employee_dept}")
        
        # Get assessments for this employee
        self_assessments = get_employee_assessments(employee_id, "self")
        manager_assessments = get_employee_assessments(employee_id, "manager")
        
        if self_assessments.empty and manager_assessments.empty:
            st.info("No assessments found for this employee. Complete assessments to view performance.")
            st.stop()
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs([
            "Overall Performance", 
            "Skill Details", 
            "Development Progress"
        ])
        
        # Overall Performance Tab
        with tab1:
            st.header("Overall Performance")
            
            # Toggle between competency view and skill view
            view_type = st.radio(
                "View by:",
                ["Competencies", "Skills"],
                horizontal=True
            )
            
            if view_type == "Competencies":
                # Show competency-based radar charts
                st.subheader("Competency Overview")
                
                # Combined competency radar chart
                if not self_assessments.empty or not manager_assessments.empty:
                    fig, error = combined_competency_radar(employee_id)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(error or "No competency assessment data available.")
                else:
                    st.info("No assessments completed yet.")
            else:
                # Show skill-based radar charts
                st.subheader("Skills Overview")
                
                # Combined skill radar chart
                if not self_assessments.empty or not manager_assessments.empty:
                    fig, error = combined_skill_radar(employee_id)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(error or "No skill assessment data available.")
                else:
                    st.info("No assessments completed yet.")
            
            # Comparison to next level expectations
            st.markdown("---")
            st.subheader("Performance vs. Next Level Expectations")
            
            if not self_assessments.empty or not manager_assessments.empty:
                # Use the same view type (Skills/Competencies) as selected above
                comparison_view_type = "Skills" if view_type == "Skills" else "Competencies"
                
                # Display explanatory text
                st.markdown("""
                This chart compares:
                - **Current Performance**: Average score of self and manager assessments
                - **Next Level Expectations**: Required scores for the next job level
                """)
                
                # Use the combined comparison chart function that shows the mean of self and manager assessments
                # together with next level expected values
                fig, error = combined_comparison_radar_chart(employee_id, employee_level, comparison_view_type)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(error or f"Cannot create comparison chart. Check that expectations are defined for next level.")
            else:
                st.info("No assessments available to compare with expected levels.")
        
        # Skill Details Tab
        with tab2:
            st.header("Skill Details")
            
            # Load data
            organization_id = get_current_organization_id()
            competencies_df = load_data_for_organization("competencies", organization_id)
            skills_df = load_data_for_organization("skills", organization_id)
            
            if not competencies_df.empty:
                # Select competency to view
                comp_options = competencies_df["name"].tolist()
                selected_comp = st.selectbox("Select Competency", comp_options, key="individual_comp_select")
                
                # Get competency ID
                selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]
                
                # Get skills for this competency
                comp_skills = get_competency_skills(selected_comp_id)
                
                if not comp_skills.empty:
                    # Get expected scores
                    expectations_df = load_data_for_organization("expectations", organization_id)
                    
                    # Create a table with skill details and assessments
                    skill_data = []
                    
                    for _, skill_row in comp_skills.iterrows():
                        skill_name = skill_row["name"]
                        
                        # Get the latest assessments
                        self_assessment = get_latest_assessment(employee_id, selected_comp, skill_name, "self")
                        manager_assessment = get_latest_assessment(employee_id, selected_comp, skill_name, "manager")
                        
                        # Get expected score for this skill
                        expected_score = None
                        if not expectations_df.empty:
                            exp_row = expectations_df[
                                (expectations_df["job_level"] == employee_level) &
                                (expectations_df["competency"] == selected_comp) &
                                (expectations_df["skill"] == skill_name)
                            ]
                            if not exp_row.empty:
                                expected_score = exp_row.iloc[0]["expected_score"]
                        
                        skill_data.append({
                            "Skill": skill_name,
                            "Description": skill_row["description"],
                            "Self Score": float(self_assessment["score"]) if self_assessment is not None else None,
                            "Manager Score": float(manager_assessment["score"]) if manager_assessment is not None else None,
                            "Expected Score": expected_score,
                            "Gap to Expected (Self)": (float(self_assessment["score"]) - expected_score) if self_assessment is not None and expected_score is not None else None,
                            "Gap to Expected (Manager)": (float(manager_assessment["score"]) - expected_score) if manager_assessment is not None and expected_score is not None else None,
                        })
                    
                    # Convert to DataFrame for display
                    skills_table = pd.DataFrame(skill_data)
                    
                    # Style the table to highlight gaps
                    def highlight_gaps(val):
                        if isinstance(val, (int, float)) and "Gap" in skills_table.columns[skills_table.loc[skills_table.index[0]] == val].tolist():
                            if val < -1:
                                return 'background-color: #ffcccc' # red for significant gap
                            elif val < 0:
                                return 'background-color: #ffffcc' # yellow for small gap
                            elif val >= 0:
                                return 'background-color: #ccffcc' # green for meeting or exceeding
                        return ''
                    
                    # Show the table with styling
                    st.dataframe(skills_table.style.applymap(highlight_gaps))
                    
                    # Show select skill for detailed view
                    if skill_data:
                        st.subheader("Select Skill for Detailed View")
                        selected_skill = st.selectbox("Select Skill", [s["Skill"] for s in skill_data], key="individual_skill_detail_select")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Self assessment details
                            st.subheader("Self Assessment")
                            self_assessment = get_latest_assessment(employee_id, selected_comp, selected_skill, "self")
                            
                            if self_assessment is not None:
                                st.write(f"**Score:** {self_assessment['score']}")
                                st.write(f"**Date:** {pd.to_datetime(self_assessment['assessment_date']).strftime('%Y-%m-%d')}")
                                st.write(f"**Notes:** {self_assessment['notes']}")
                            else:
                                st.info("No self assessment available for this skill.")
                        
                        with col2:
                            # Manager assessment details
                            st.subheader("Manager Assessment")
                            manager_assessment = get_latest_assessment(employee_id, selected_comp, selected_skill, "manager")
                            
                            if manager_assessment is not None:
                                st.write(f"**Score:** {manager_assessment['score']}")
                                st.write(f"**Date:** {pd.to_datetime(manager_assessment['assessment_date']).strftime('%Y-%m-%d')}")
                                st.write(f"**Feedback:** {manager_assessment['notes']}")
                            else:
                                st.info("No manager assessment available for this skill.")
                    else:
                        st.info("No skill data available.")
                else:
                    st.info(f"No skills found for {selected_comp}.")
            else:
                st.warning("No competencies found in the system.")
        
        # Development Progress Tab
        with tab3:
            st.header("Development Progress")
            
            # Load competencies and skills
            organization_id = get_current_organization_id()
            competencies_df = load_data_for_organization("competencies", organization_id)
            skills_df = load_data_for_organization("skills", organization_id)
            
            if not competencies_df.empty and not skills_df.empty:
                # Select competency and skill
                col1, col2 = st.columns(2)
                
                with col1:
                    comp_options = competencies_df["name"].tolist()
                    selected_comp = st.selectbox("Select Competency", comp_options, key="prog_comp")
                
                # Get competency ID
                selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]
                
                # Get skills for this competency
                comp_skills = get_competency_skills(selected_comp_id)
                
                with col2:
                    if not comp_skills.empty:
                        skill_options = comp_skills["name"].tolist()
                        selected_skill = st.selectbox("Select Skill", skill_options, key="performance_skill")
                    else:
                        st.info(f"No skills found for {selected_comp}.")
                        selected_skill = None
                
                if selected_skill:
                    # Show progress chart
                    fig, error = skill_improvement_chart(employee_id, selected_comp, selected_skill)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(error or "No progress data available for this skill.")
                    
                    # Show assessment history
                    st.subheader("Assessment History")
                    assessments_df = load_data("assessments")
                    
                    if not assessments_df.empty:
                        skill_history = assessments_df[
                            (assessments_df["employee_id"] == employee_id) &
                            (assessments_df["competency"] == selected_comp) &
                            (assessments_df["skill"] == selected_skill)
                        ]
                        
                        if not skill_history.empty:
                            # Convert and sort by date
                            skill_history["assessment_date"] = pd.to_datetime(skill_history["assessment_date"])
                            skill_history = skill_history.sort_values("assessment_date", ascending=False)
                            
                            # Get only the latest assessment for each day and assessment type
                            skill_history["assessment_day"] = skill_history["assessment_date"].dt.date
                            
                            # Group by date and type, keeping the latest assessment for each
                            latest_day_assessments = []
                            for (day, assess_type), group in skill_history.groupby(["assessment_day", "assessment_type"]):
                                # Get the one with highest assessment_id within the group (most recent)
                                latest_day_assessments.append(group.iloc[0])
                            
                            # Convert to DataFrame and sort by date (most recent first)
                            latest_history_df = pd.DataFrame(latest_day_assessments).sort_values("assessment_date", ascending=False)
                            
                            if not latest_history_df.empty:
                                # Select and format columns for display
                                history_table = latest_history_df[["assessment_date", "assessment_type", "score", "notes"]]
                                history_table["assessment_date"] = history_table["assessment_date"].dt.strftime("%Y-%m-%d")
                                st.dataframe(history_table)
                            else:
                                st.info("No assessment history found after processing.")
                        else:
                            st.info("No assessment history found for this skill.")
                    else:
                        st.info("No assessment data available.")
            else:
                st.warning("Competency framework not fully set up.")
    else:
        st.warning("Employee record not found.")
else:
    st.info("Please select an employee to view their performance.")

# Add explanatory text at the bottom
st.markdown("---")
st.markdown("""
### Understanding Performance Data

- **Overall Performance:** Radar charts showing combined self and manager assessments across all skills or competencies
- **Performance vs. Next Level:** Comparison between current performance (mean of self and manager assessments) and the expected level for the next job level
- **Skill Details:** Detailed breakdown of individual skills with self and manager ratings, expected scores, and gaps
- **Development Progress:** Track progress over time for specific skills and view assessment history

Performance gaps highlighted in colors:
- 🟢 Green: Meeting or exceeding expectations
- 🟡 Yellow: Small gap (less than 1 point)
- 🔴 Red: Significant gap (1 point or more)

Use this data to identify strengths, areas for development, and track progress over time.
""")
