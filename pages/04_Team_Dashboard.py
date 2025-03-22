import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Team Dashboard - Skill Matrix",
    page_icon="👥",
    layout="wide"
)

import pandas as pd
import numpy as np
from data_manager import (
    load_data, load_data_for_organization, get_employees_for_manager, get_employee_assessments,
    get_team_competency_means
)
from utils import check_permission, check_page_access, get_user_id, calculate_mean, get_current_organization_id
from ui_helpers import load_custom_css
from visualizations import (
    team_skill_radar, team_competency_radar, competency_bar_chart, team_heatmap,
    create_radar_chart, combined_team_skill_radar, combined_team_competency_radar
)

# Load custom CSS for consistent styling
load_custom_css()

# This page is accessible only to managers and admins
if not check_page_access(["admin", "manager"]):
    st.stop()

# Check if user is authenticated
if not hasattr(st.session_state, "authenticated") or not st.session_state.authenticated:
    st.warning("Please login from the Home page.")
    st.stop()

# Check permissions - only managers and admins can access this page
if not check_permission("manager"):
    st.error("You don't have permission to access this page.")
    st.stop()

st.title("Team Skills Dashboard")

# For managers, show their team
# For admins, allow selecting department or manager
department_filter = None
manager_id = None

if st.session_state.user_role == "admin":
    # Allow filtering by department or manager
    organization_id = get_current_organization_id()
    employees_df = load_data_for_organization("employees", organization_id)
    
    if not employees_df.empty:
        filter_type = st.radio("Filter by", ["Department", "Manager"], horizontal=True)
        
        if filter_type == "Department":
            departments = sorted(employees_df["department"].unique())
            department_filter = st.selectbox("Select Department", departments, key="team_dashboard_dept_filter")
        else:
            # Get all managers
            managers_df = employees_df[employees_df["employee_id"].isin(employees_df["manager_id"].dropna().unique())]
            
            if not managers_df.empty:
                manager_options = [(row["employee_id"], row["name"]) for _, row in managers_df.iterrows()]
                manager_names = [m[1] for m in manager_options]
                manager_ids = [m[0] for m in manager_options]
                
                selected_manager = st.selectbox("Select Manager", manager_names, key="team_dashboard_manager_select")
                selected_manager_idx = manager_names.index(selected_manager)
                manager_id = manager_ids[selected_manager_idx]
            else:
                st.warning("No managers found in the system.")
    else:
        st.warning("No employees found in the system.")
else:
    # For managers, get their employee ID
    manager_id = get_user_id(st.session_state.username)
    if manager_id is None:
        st.warning("Your user account is not linked to an employee record. Please contact an administrator.")
        st.stop()

# Get team members based on filters
organization_id = get_current_organization_id()
employees_df = load_data_for_organization("employees", organization_id)
team_members = pd.DataFrame()

if department_filter:
    team_members = employees_df[employees_df["department"] == department_filter]
elif manager_id:
    team_members = get_employees_for_manager(manager_id)
else:
    st.warning("Please select a department or manager.")
    st.stop()

if team_members.empty:
    st.info("No team members found with the current filters.")
    st.stop()

# Display team overview
st.header(f"Team Overview: {department_filter or team_members.iloc[0]['department']}")
st.write(f"Team size: {len(team_members)}")

# Get all assessments for team members
assessments_df = load_data_for_organization("assessments", organization_id)
team_assessments = pd.DataFrame()

if not assessments_df.empty:
    team_assessments = assessments_df[assessments_df["employee_id"].isin(team_members["employee_id"])]

if team_assessments.empty:
    st.warning("No assessment data available for this team.")
    st.stop()

# Create tabs for different views
tab1, tab2, tab3 = st.tabs([
    "Team Skills Overview", 
    "Competency Analysis", 
    "Individual Comparisons"
])

# Team Skills Overview Tab
with tab1:
    st.header("Team Skills Overview")
    
    # Filter by visualization type
    visual_type = st.radio(
        "Visualization Type", 
        ["Skills", "Competences"], 
        horizontal=True,
        key="team_overview_visual_type"
    )
    
    # Create team skills radar chart
    if visual_type == "Skills":
        st.subheader("Team Skills Radar")
        fig, error = combined_team_skill_radar(team_assessments)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(error or "Could not create team skills radar chart.")
    else:
        # Create team competencies radar chart
        st.subheader("Team Competencies")
        fig, error = combined_team_competency_radar(team_assessments)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(error or "Could not create team competencies radar chart.")
    
    # Team skills heatmap
    st.subheader("Skills by Job Level")
    # Display the heatmap for the selected assessment type (for now use "self")
    filtered_assessments = team_assessments[team_assessments["assessment_type"] == "self"]
    fig, error = team_heatmap(filtered_assessments)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(error or "Could not create skills heatmap.")

# Competency Analysis Tab
with tab2:
    st.header("Competency Analysis")
    
    # Load skill expectations
    expectations_df = load_data_for_organization("expectations", organization_id)
    
    # Select job level for expectations comparison
    levels_df = load_data_for_organization("levels", organization_id)
    if not levels_df.empty and not expectations_df.empty:
        level_options = sorted(expectations_df["job_level"].unique())
        selected_level = st.selectbox("Compare Against Job Level", level_options, key="team_dashboard_job_level_select")
        
        # Filter expectations for selected level
        level_expectations = expectations_df[expectations_df["job_level"] == selected_level]
    else:
        level_expectations = None
        selected_level = None
    
    # Competency breakdown
    st.subheader(f"Competency Breakdown")
    
    # Select assessment type
    assessment_type = st.radio(
        "Assessment Type", 
        ["self", "manager"], 
        horizontal=True,
        key="comp_assessment_type",
        format_func=lambda x: "Self Assessment" if x == "self" else "Manager Assessment"
    )
    
    # Filter assessments by type
    filtered_assessments = team_assessments[team_assessments["assessment_type"] == assessment_type]
    
    # Get unique competencies
    competencies = sorted(filtered_assessments["competency"].unique())
    
    # Create chart
    fig, error = competency_bar_chart(filtered_assessments, level_expectations)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(error or "Could not create competency bar chart.")
    
    # Table of mean scores by competency
    st.subheader("Mean Scores by Competency")
    
    if not filtered_assessments.empty:
        # Calculate mean scores
        competency_means = filtered_assessments.groupby(["competency"])["score"].mean().reset_index()
        competency_means["score"] = competency_means["score"].round(2)
        
        # Add expectations if available
        if level_expectations is not None:
            expected_means = level_expectations.groupby(["competency"])["expected_score"].mean().reset_index()
            
            # Merge with actual scores
            competency_means = competency_means.merge(
                expected_means,
                on="competency",
                how="left",
                suffixes=("", "_expected")
            )
            
            # Calculate gap
            competency_means["gap"] = competency_means["score"] - competency_means["expected_score"]
            competency_means["gap"] = competency_means["gap"].round(2)
            
            # Format for display
            competency_means = competency_means.rename(columns={
                "competency": "Competency",
                "score": f"Actual Score ({assessment_type})",
                "expected_score": f"Expected Score (Level {selected_level})",
                "gap": "Gap"
            })
        else:
            # Format for display
            competency_means = competency_means.rename(columns={
                "competency": "Competency",
                "score": f"Mean Score ({assessment_type})"
            })
        
        st.dataframe(competency_means)

# Individual Comparisons Tab
with tab3:
    st.header("Individual Member Comparison")
    
    # Create data for comparison
    comparison_data = []
    
    # Get all competencies
    competencies = sorted(team_assessments["competency"].unique()) if not team_assessments.empty else []
    
    # Select assessment type
    assessment_type = st.radio(
        "Assessment Type", 
        ["self", "manager"], 
        horizontal=True,
        key="indiv_assessment_type",
        format_func=lambda x: "Self Assessment" if x == "self" else "Manager Assessment"
    )
    
    # For each team member, calculate mean scores by competency
    for _, employee_row in team_members.iterrows():
        emp_id = employee_row["employee_id"]
        emp_name = employee_row["name"]
        
        employee_assessments = team_assessments[
            (team_assessments["employee_id"] == emp_id) &
            (team_assessments["assessment_type"] == assessment_type)
        ]
        
        if not employee_assessments.empty:
            # Calculate mean for each competency
            emp_data = {"Employee": emp_name}
            
            for comp in competencies:
                comp_assessments = employee_assessments[employee_assessments["competency"] == comp]
                if not comp_assessments.empty:
                    emp_data[comp] = round(comp_assessments["score"].mean(), 2)
                else:
                    emp_data[comp] = None
            
            # Calculate overall mean
            emp_data["Overall Mean"] = round(employee_assessments["score"].mean(), 2)
            
            comparison_data.append(emp_data)
    
    if comparison_data:
        # Create DataFrame for display
        comparison_df = pd.DataFrame(comparison_data)
        
        # Calculate team means for each competency
        team_means = {"Employee": "TEAM AVERAGE"}
        
        for comp in competencies:
            comp_assessments = team_assessments[
                (team_assessments["competency"] == comp) &
                (team_assessments["assessment_type"] == assessment_type)
            ]
            if not comp_assessments.empty:
                team_means[comp] = round(comp_assessments["score"].mean(), 2)
            else:
                team_means[comp] = None
        
        # Calculate overall team mean
        team_means["Overall Mean"] = round(team_assessments[team_assessments["assessment_type"] == assessment_type]["score"].mean(), 2)
        
        # Add team means to comparison data
        comparison_df = pd.concat([comparison_df, pd.DataFrame([team_means])], ignore_index=True)
        
        # Sort by overall mean
        comparison_df = comparison_df.sort_values("Overall Mean", ascending=False)
        
        # Display the comparison table
        st.dataframe(comparison_df)
        
        # Create visualization for selected employee comparison
        st.subheader("Compare Employees")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Select employees to compare
            employee_options = [row["Employee"] for _, row in comparison_df.iterrows() if row["Employee"] != "TEAM AVERAGE"]
            selected_employees = st.multiselect("Select Employees to Compare", employee_options)
        
        with col2:
            # Select competency to compare
            comp_options = ["Overall Mean"] + competencies
            selected_comp = st.selectbox("Select Competency", comp_options, key="team_dashboard_comp_select")
        
        # Create comparison chart
        if selected_employees and selected_comp:
            # Filter for selected employees and add team average
            filtered_df = comparison_df[
                comparison_df["Employee"].isin(selected_employees + ["TEAM AVERAGE"])
            ]
            
            # Create bar chart
            chart_data = pd.DataFrame({
                "Employee": filtered_df["Employee"],
                "Score": filtered_df[selected_comp]
            })
            
            st.bar_chart(
                chart_data.set_index("Employee"),
                use_container_width=True
            )
    else:
        st.info("No assessment data available for individual comparison.")

# Add explanatory text at the bottom
st.markdown("---")
st.markdown("""
### Dashboard Guide

- **Team Skills Overview:** View radar charts and heatmaps showing overall team capabilities
- **Competency Analysis:** Analyze strengths and gaps across competency areas compared to job level expectations
- **Individual Comparisons:** Compare performance metrics across team members and identify top performers

Use these visualizations to:
- Identify team-wide skill gaps
- Recognize training needs
- Highlight team strengths
- Identify key team members with specific skills
- Balance team composition for projects
""")
