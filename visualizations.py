import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_manager import (
    load_data, 
    get_employee_assessments, 
    get_latest_assessment,
    get_latest_competency_assessment,
    calculate_employee_competency_means,
    calculate_employee_skill_means,
    get_team_competency_means
)

def create_radar_chart(data, categories, title="", scale=5):
    """Create a radar chart for skills visualization"""
    fig = go.Figure()
    
    # Add data to the chart
    fig.add_trace(go.Scatterpolar(
        r=data,
        theta=categories,
        fill='toself',
        name='Current Level'
    ))
    
    # Set layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, scale]
            )
        ),
        title=title,
        showlegend=True
    )
    
    return fig

def create_comparison_radar_chart(actual_data, expected_data, categories, title="", scale=5):
    """Create a radar chart comparing actual vs expected skills"""
    fig = go.Figure()
    
    # Add actual data
    fig.add_trace(go.Scatterpolar(
        r=actual_data,
        theta=categories,
        fill='toself',
        name='Current Level',
        line=dict(color='blue')
    ))
    
    # Add expected data
    fig.add_trace(go.Scatterpolar(
        r=expected_data,
        theta=categories,
        fill='toself',
        name='Expected Level',
        line=dict(color='red')
    ))
    
    # Set layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, scale]
            )
        ),
        title=title,
        showlegend=True
    )
    
    return fig

def employee_skill_radar(employee_id, assessment_type="self"):
    """Create a radar chart for an employee's skills"""
    # Get skill data
    skills_df = load_data("skills")
    competencies_df = load_data("competencies")
    
    if skills_df.empty or competencies_df.empty:
        return None, "No skills or competencies found."
    
    # Create lists for chart data
    labels = []
    values = []
    
    # Loop through all competencies and skills to get latest assessments
    for _, comp_row in competencies_df.iterrows():
        comp_skills = skills_df[skills_df["competency_id"] == comp_row["competency_id"]]
        
        for _, skill_row in comp_skills.iterrows():
            # Get latest assessment for this skill
            latest = get_latest_assessment(
                employee_id, 
                comp_row["name"], 
                skill_row["name"], 
                assessment_type
            )
            
            if latest is not None:
                labels.append(f"{comp_row['name']} - {skill_row['name']}")
                values.append(latest["score"])
    
    if not labels:
        return None, f"No {assessment_type} assessments found for this employee."
    
    # Create radar chart
    fig = create_radar_chart(
        data=values,
        categories=labels,
        title=f"Skill Assessment ({assessment_type.capitalize()})",
        scale=5
    )
    
    return fig, None

def comparison_radar_chart(employee_id, job_level, assessment_type="self"):
    """Create a radar chart comparing actual vs expected skills"""
    # Load necessary data
    skills_df = load_data("skills")
    competencies_df = load_data("competencies")
    expectations_df = load_data("expectations")
    
    if skills_df.empty or competencies_df.empty:
        return None, "No skills or competencies found."
    
    if expectations_df.empty:
        return None, "No skill expectations defined."
    
    # Filter expectations for the employee's job level
    level_expectations = expectations_df[expectations_df["job_level"] == job_level]
    
    if level_expectations.empty:
        return None, f"No skill expectations defined for job level {job_level}."
    
    # Create lists for chart data
    labels = []
    actual_values = []
    expected_values = []
    
    # Loop through all competencies and skills
    for _, comp_row in competencies_df.iterrows():
        comp_skills = skills_df[skills_df["competency_id"] == comp_row["competency_id"]]
        
        for _, skill_row in comp_skills.iterrows():
            # Get latest assessment for this skill
            latest = get_latest_assessment(
                employee_id, 
                comp_row["name"], 
                skill_row["name"], 
                assessment_type
            )
            
            # Find matching expectation
            expectation = level_expectations[
                (level_expectations["competency"] == comp_row["name"]) &
                (level_expectations["skill"] == skill_row["name"])
            ]
            
            # Only include if both assessment and expectation exist
            if latest is not None and not expectation.empty:
                labels.append(f"{comp_row['name']} - {skill_row['name']}")
                actual_values.append(latest["score"])
                expected_values.append(expectation.iloc[0]["expected_score"])
    
    if not labels:
        return None, "No matching skill expectations found for this employee's assessments."
    
    # Create radar chart
    fig = create_comparison_radar_chart(
        actual_data=actual_values,
        expected_data=expected_values,
        categories=labels,
        title=f"Skills vs. Expectations ({assessment_type.capitalize()})",
        scale=5
    )
    
    return fig, None

def team_skill_radar(team_assessments, assessment_type="self", title="Team Skills Assessment"):
    """Create a radar chart for a team's skills using latest assessments
    
    Args:
        team_assessments: DataFrame containing team assessment data
        assessment_type: Type of assessment to use (should be pre-filtered)
        title: Title for the chart
    """
    # Load necessary data
    skills_df = load_data("skills")
    competencies_df = load_data("competencies")
    
    # Check if dataframes are empty
    if skills_df.empty or competencies_df.empty or team_assessments.empty:
        return None, "No team members or skills/competencies found."
    
    # Get unique employee IDs from the assessments
    team_employee_ids = team_assessments["employee_id"].unique().tolist()
    if not team_employee_ids:
        return None, "No team members found in the assessments."
    
    # Dictionary to store cumulative skill scores and counts for averaging
    skill_data = {}  # {(competency, skill): [total_score, count]}
    
    # Process each employee's latest assessments
    for employee_id in team_employee_ids:
        # Loop through all competencies and skills
        for _, comp_row in competencies_df.iterrows():
            comp_skills = skills_df[skills_df["competency_id"] == comp_row["competency_id"]]
            
            for _, skill_row in comp_skills.iterrows():
                # Get latest assessment for this skill
                latest = get_latest_assessment(
                    employee_id, 
                    comp_row["name"], 
                    skill_row["name"], 
                    assessment_type
                )
                
                if latest is not None:
                    key = (comp_row["name"], skill_row["name"])
                    if key not in skill_data:
                        skill_data[key] = [latest["score"], 1]
                    else:
                        skill_data[key][0] += latest["score"]
                        skill_data[key][1] += 1
    
    if not skill_data:
        return None, f"No {assessment_type} assessments found for this team."
    
    # Calculate means and create chart data
    labels = []
    values = []
    
    for (comp, skill), (total, count) in skill_data.items():
        labels.append(f"{comp} - {skill}")
        values.append(total / count)  # Calculate mean
    
    # Create radar chart
    fig = create_radar_chart(
        data=values,
        categories=labels,
        title=title,
        scale=5
    )
    
    return fig, None

def team_competency_radar(team_assessments, assessment_type="self", title="Team Competency Assessment"):
    """Create a radar chart for a team's competencies using latest assessments"""
    # Load necessary data
    competencies_df = load_data("competencies")
    
    # Check if dataframes are empty
    if competencies_df.empty or team_assessments.empty:
        return None, "No team members or competencies found."
    
    # Get unique employee IDs from the assessments
    team_employee_ids = team_assessments["employee_id"].unique().tolist()
    if not team_employee_ids:
        return None, "No team members found in the assessments."
    
    # Dictionary to store cumulative competency scores and counts for averaging
    comp_data = {}  # {competency: [total_score, count]}
    
    # Process each employee's latest assessments
    for employee_id in team_employee_ids:
        # Loop through all competencies
        for _, comp_row in competencies_df.iterrows():
            # Get latest assessment for this competency
            latest = get_latest_competency_assessment(
                employee_id, 
                comp_row["name"], 
                assessment_type
            )
            
            if latest is not None:
                key = comp_row["name"]
                if key not in comp_data:
                    comp_data[key] = [latest["score"], 1]
                else:
                    comp_data[key][0] += latest["score"]
                    comp_data[key][1] += 1
    
    if not comp_data:
        return None, f"No {assessment_type} competency assessments found for this team."
    
    # Calculate means and create chart data
    labels = []
    values = []
    
    for comp, (total, count) in comp_data.items():
        labels.append(comp)
        values.append(total / count)  # Calculate mean
    
    # Create radar chart
    fig = create_radar_chart(
        data=values,
        categories=labels,
        title=title,
        scale=5
    )
    
    return fig, None

def employee_competency_radar(employee_id, assessment_type="self"):
    """Create a radar chart for an employee's competencies (not skills)"""
    # Get competency data
    competencies_df = load_data("competencies")
    
    if competencies_df.empty:
        return None, "No competencies found."
    
    # Create lists for chart data
    labels = []
    values = []
    
    # Loop through all competencies to get latest assessments
    for _, comp_row in competencies_df.iterrows():
        # Get latest competency assessment
        latest = get_latest_competency_assessment(
            employee_id, 
            comp_row["name"], 
            assessment_type
        )
        
        if latest is not None:
            labels.append(comp_row["name"])
            values.append(latest["score"])
    
    if not labels:
        return None, f"No {assessment_type} competency assessments found for this employee."
    
    # Create radar chart
    fig = create_radar_chart(
        data=values,
        categories=labels,
        title=f"Competency Assessment ({assessment_type.capitalize()})",
        scale=5
    )
    
    return fig, None

def competency_bar_chart(employee_id, job_level=None, assessment_type="self", title="Competency Assessment"):
    """Create a bar chart for competencies using latest assessments"""
    # Load necessary data
    competencies_df = load_data("competencies")
    comp_expectations_df = load_data("comp_expectations") if job_level else None
    
    if competencies_df.empty:
        return None, "No competencies found."
    
    if job_level and comp_expectations_df is not None:
        # Filter expectations for the employee's job level
        level_expectations = comp_expectations_df[comp_expectations_df["job_level"] == job_level]
        
        if level_expectations.empty:
            job_level = None  # Don't show expectations if none are defined for this level
    
    # Create lists for chart data
    labels = []
    actual_values = []
    expected_values = []
    
    # Loop through all competencies to get latest assessments
    for _, comp_row in competencies_df.iterrows():
        # Get latest competency assessment
        latest = get_latest_competency_assessment(
            employee_id, 
            comp_row["name"], 
            assessment_type
        )
        
        if latest is not None:
            labels.append(comp_row["name"])
            actual_values.append(latest["score"])
            
            # Get expectation if available
            if job_level and level_expectations is not None:
                expectation = level_expectations[level_expectations["competency"] == comp_row["name"]]
                if not expectation.empty:
                    expected_values.append(expectation.iloc[0]["expected_score"])
                else:
                    expected_values.append(None)  # No expectation for this competency
    
    if not labels:
        return None, f"No {assessment_type} competency assessments found."
    
    # Create bar chart
    fig = go.Figure()
    
    # Add actual data
    fig.add_trace(go.Bar(
        x=labels,
        y=actual_values,
        name="Actual Score"
    ))
    
    # Add expectation data if available
    if job_level and expected_values and any(v is not None for v in expected_values):
        # Replace None values with NaN for plotting
        expected_values = [v if v is not None else float('nan') for v in expected_values]
        
        fig.add_trace(go.Bar(
            x=labels,
            y=expected_values,
            name="Expected Score"
        ))
    
    # Set layout
    fig.update_layout(
        title=title,
        xaxis_title="Competency",
        yaxis_title="Score",
        yaxis=dict(range=[0, 5]),
        barmode="group"
    )
    
    return fig, None

def skill_improvement_chart(employee_id, competency, skill):
    """Create a line chart showing skill improvement over time"""
    assessments_df = load_data("assessments")
    
    if assessments_df.empty:
        return None, "No assessments found."
    
    # Filter for specific employee and skill
    skill_assessments = assessments_df[
        (assessments_df["employee_id"] == employee_id) &
        (assessments_df["competency"] == competency) &
        (assessments_df["skill"] == skill)
    ]
    
    if skill_assessments.empty:
        return None, f"No assessments found for {competency} - {skill}."
    
    # Convert dates
    skill_assessments["assessment_date"] = pd.to_datetime(skill_assessments["assessment_date"])
    
    # Group by date and assessment_type, keeping only the latest assessment for each day
    skill_assessments = skill_assessments.sort_values(["assessment_date", "assessment_id"], ascending=[True, False])
    
    # Create a date-only column for grouping by day
    skill_assessments["assessment_day"] = skill_assessments["assessment_date"].dt.date
    
    # Get the latest assessment for each day and assessment type
    latest_assessments = []
    for (day, assess_type), group in skill_assessments.groupby(["assessment_day", "assessment_type"]):
        latest_assessments.append(group.iloc[0])
    
    # Convert back to DataFrame and sort by date
    latest_assessments_df = pd.DataFrame(latest_assessments).sort_values("assessment_date")
    
    if latest_assessments_df.empty:
        return None, f"No assessments found for {competency} - {skill} after processing."
    
    # Create line chart
    fig = px.line(
        latest_assessments_df,
        x="assessment_date",
        y="score",
        color="assessment_type",
        title=f"Skill Progress: {competency} - {skill}",
        labels={"assessment_date": "Date", "score": "Score", "assessment_type": "Assessment Type"},
        markers=True
    )
    
    # Set y-axis range
    fig.update_layout(
        yaxis=dict(range=[0, 5])
    )
    
    return fig, None

def team_heatmap(team_assessments, assessment_type="self"):
    """Create a heatmap of team skills by competency using latest assessments"""
    # Load necessary data
    skills_df = load_data("skills")
    competencies_df = load_data("competencies")
    
    # Check if dataframes are empty
    if skills_df.empty or competencies_df.empty or team_assessments.empty:
        return None, "No team members or skills/competencies found."
    
    # Get unique employee IDs from the assessments
    team_employee_ids = team_assessments["employee_id"].unique().tolist()
    if not team_employee_ids:
        return None, "No team members found in the assessments."
    
    # Get all unique competencies and skills
    competencies = sorted(competencies_df["name"].unique())
    
    # Get all skills organized by competency
    skill_by_comp = {}
    all_skills = []
    
    for comp in competencies:
        comp_id = competencies_df[competencies_df["name"] == comp]["competency_id"].iloc[0]
        comp_skills = skills_df[skills_df["competency_id"] == comp_id]["name"].tolist()
        skill_by_comp[comp] = comp_skills
        all_skills.extend(comp_skills)
    
    all_skills = sorted(set(all_skills))  # Remove duplicates and sort
    
    if not all_skills:
        return None, "No skills found for this team."
    
    # Create 2D array for heatmap with default values of NaN (will display as blank in heatmap)
    heatmap_data = np.full((len(competencies), len(all_skills)), np.nan)
    
    # Dictionary to store cumulative skill scores and counts
    skill_data = {}  # {(competency, skill): [total_score, count]}
    
    # Process each employee's latest assessments
    for employee_id in team_employee_ids:
        # Loop through all competencies and skills
        for i, comp in enumerate(competencies):
            comp_id = competencies_df[competencies_df["name"] == comp]["competency_id"].iloc[0]
            comp_skills = skills_df[skills_df["competency_id"] == comp_id]
            
            for _, skill_row in comp_skills.iterrows():
                # Get latest assessment for this skill
                latest = get_latest_assessment(
                    employee_id, 
                    comp, 
                    skill_row["name"], 
                    assessment_type
                )
                
                if latest is not None:
                    key = (comp, skill_row["name"])
                    if key not in skill_data:
                        skill_data[key] = [latest["score"], 1]
                    else:
                        skill_data[key][0] += latest["score"]
                        skill_data[key][1] += 1
    
    if not skill_data:
        return None, f"No {assessment_type} assessments found for this team."
    
    # Fill in the heatmap data with calculated means
    for (comp, skill), (total, count) in skill_data.items():
        i = competencies.index(comp)
        j = all_skills.index(skill)
        heatmap_data[i, j] = total / count  # Calculate mean
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=all_skills,
        y=competencies,
        colorscale="Viridis",
        zmin=0,
        zmax=5
    ))
    
    # Set layout
    fig.update_layout(
        title=f"Team Skills Heatmap ({assessment_type.capitalize()})",
        xaxis_title="Skills",
        yaxis_title="Competencies"
    )
    
    return fig, None
