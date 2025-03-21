import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_manager import (
    load_data, 
    get_employee_assessments, 
    get_latest_assessment,
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
    assessments_df = get_employee_assessments(employee_id, assessment_type)
    
    if assessments_df.empty:
        return None, "No assessments found for this employee."
    
    # Group by competency and skill and get mean scores
    skill_means = assessments_df.groupby(["competency", "skill"])["score"].mean().reset_index()
    
    # Create labels and values for radar chart
    labels = [f"{row['competency']} - {row['skill']}" for _, row in skill_means.iterrows()]
    values = skill_means["score"].tolist()
    
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
    assessments_df = get_employee_assessments(employee_id, assessment_type)
    expectations_df = load_data("expectations")
    
    if assessments_df.empty:
        return None, "No assessments found for this employee."
    
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
    
    # Iterate through assessments and find matching expectations
    for _, assessment_row in assessments_df.iterrows():
        competency = assessment_row["competency"]
        skill = assessment_row["skill"]
        
        # Find matching expectation
        expectation = level_expectations[
            (level_expectations["competency"] == competency) &
            (level_expectations["skill"] == skill)
        ]
        
        if not expectation.empty:
            labels.append(f"{competency} - {skill}")
            actual_values.append(assessment_row["score"])
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

def team_skill_radar(team_assessments, title="Team Skills Assessment"):
    """Create a radar chart for a team's skills"""
    if team_assessments.empty:
        return None, "No assessments found for this team."
    
    # Group by competency and skill and get mean scores
    skill_means = team_assessments.groupby(["competency", "skill"])["score"].mean().reset_index()
    
    # Create labels and values for radar chart
    labels = [f"{row['competency']} - {row['skill']}" for _, row in skill_means.iterrows()]
    values = skill_means["score"].tolist()
    
    # Create radar chart
    fig = create_radar_chart(
        data=values,
        categories=labels,
        title=title,
        scale=5
    )
    
    return fig, None

def team_competency_radar(team_assessments, title="Team Competency Assessment"):
    """Create a radar chart for a team's competencies"""
    if team_assessments.empty:
        return None, "No assessments found for this team."
    
    # Group by competency and get mean scores
    competency_means = team_assessments.groupby(["competency"])["score"].mean().reset_index()
    
    # Create labels and values for radar chart
    labels = competency_means["competency"].tolist()
    values = competency_means["score"].tolist()
    
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
    # Get competency means directly using the new function
    comp_means = calculate_employee_competency_means(employee_id)
    
    if comp_means.empty:
        return None, "No assessments found for this employee."
    
    # Filter by assessment type
    filtered_means = comp_means[comp_means["assessment_type"] == assessment_type]
    
    if filtered_means.empty:
        return None, f"No {assessment_type} assessments found for this employee."
    
    # Create labels and values for radar chart
    labels = filtered_means["competency"].tolist()
    values = filtered_means["score"].tolist()
    
    # Create radar chart
    fig = create_radar_chart(
        data=values,
        categories=labels,
        title=f"Competency Assessment ({assessment_type.capitalize()})",
        scale=5
    )
    
    return fig, None

def competency_bar_chart(assessments_df, comparison_df=None, title="Competency Assessment"):
    """Create a bar chart for competencies"""
    if assessments_df.empty:
        return None, "No assessments found."
    
    # Group by competency and get mean scores
    competency_means = assessments_df.groupby(["competency"])["score"].mean().reset_index()
    
    # Create bar chart
    fig = go.Figure()
    
    # Add actual data
    fig.add_trace(go.Bar(
        x=competency_means["competency"],
        y=competency_means["score"],
        name="Actual Score"
    ))
    
    # Add comparison data if provided
    if comparison_df is not None and not comparison_df.empty:
        comparison_means = comparison_df.groupby(["competency"])["score"].mean().reset_index()
        
        # Make sure we're comparing the same competencies
        merged = competency_means.merge(
            comparison_means,
            on="competency",
            how="left",
            suffixes=("", "_expected")
        )
        
        fig.add_trace(go.Bar(
            x=merged["competency"],
            y=merged["score_expected"],
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
    
    # Convert dates and sort
    skill_assessments["assessment_date"] = pd.to_datetime(skill_assessments["assessment_date"])
    skill_assessments = skill_assessments.sort_values("assessment_date")
    
    # Create line chart
    fig = px.line(
        skill_assessments,
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

def team_heatmap(team_assessments):
    """Create a heatmap of team skills by competency"""
    if team_assessments.empty:
        return None, "No assessments found for this team."
    
    # Get all unique competencies and skills
    competencies = sorted(team_assessments["competency"].unique())
    skills = sorted(team_assessments["skill"].unique())
    
    # Create 2D array for heatmap
    heatmap_data = np.zeros((len(competencies), len(skills)))
    
    # Fill in data
    for i, comp in enumerate(competencies):
        for j, skill in enumerate(skills):
            filtered = team_assessments[
                (team_assessments["competency"] == comp) &
                (team_assessments["skill"] == skill)
            ]
            
            if not filtered.empty:
                heatmap_data[i, j] = filtered["score"].mean()
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=skills,
        y=competencies,
        colorscale="Viridis",
        zmin=0,
        zmax=5
    ))
    
    # Set layout
    fig.update_layout(
        title="Team Skills Heatmap",
        xaxis_title="Skills",
        yaxis_title="Competencies"
    )
    
    return fig, None
