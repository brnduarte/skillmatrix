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

def combined_skill_radar(employee_id):
    """Create a combined radar chart showing both self and manager assessments for an employee's skills"""
    # Get skill data
    skills_df = load_data("skills")
    competencies_df = load_data("competencies")
    
    if skills_df.empty or competencies_df.empty:
        return None, "No skills or competencies found."
    
    # Create lists for chart data
    labels = []
    self_values = []
    manager_values = []
    
    # Get unique skill identifier combinations
    skill_identifiers = []
    
    # First gather all possible competency-skill combinations for this employee
    for _, comp_row in competencies_df.iterrows():
        comp_skills = skills_df[skills_df["competency_id"] == comp_row["competency_id"]]
        
        for _, skill_row in comp_skills.iterrows():
            # Check if either self or manager assessment exists
            self_assessment = get_latest_assessment(
                employee_id, 
                comp_row["name"], 
                skill_row["name"], 
                "self"
            )
            
            manager_assessment = get_latest_assessment(
                employee_id, 
                comp_row["name"], 
                skill_row["name"], 
                "manager"
            )
            
            if self_assessment is not None or manager_assessment is not None:
                label = f"{comp_row['name']} - {skill_row['name']}"
                skill_identifiers.append((comp_row["name"], skill_row["name"], label))
    
    # Then populate the data arrays
    for comp_name, skill_name, label in skill_identifiers:
        labels.append(label)
        
        # Get latest self assessment
        self_assessment = get_latest_assessment(
            employee_id, 
            comp_name, 
            skill_name, 
            "self"
        )
        if self_assessment is not None:
            self_values.append(float(self_assessment["score"]))
        else:
            self_values.append(None)
        
        # Get latest manager assessment
        manager_assessment = get_latest_assessment(
            employee_id, 
            comp_name, 
            skill_name, 
            "manager"
        )
        if manager_assessment is not None:
            manager_values.append(float(manager_assessment["score"]))
        else:
            manager_values.append(None)
    
    if not labels:
        return None, "No assessments found for this employee."
    
    # Create combined radar chart
    fig = go.Figure()
    
    # Add self assessment data
    if any(v is not None for v in self_values):
        # Replace None with 0 for visualization purposes
        self_values_visual = [v if v is not None else 0 for v in self_values]
        
        fig.add_trace(go.Scatterpolar(
            r=self_values_visual,
            theta=labels,
            fill='toself',
            name='Self Assessment',
            line=dict(color='blue')
        ))
    
    # Add manager assessment data
    if any(v is not None for v in manager_values):
        # Replace None with 0 for visualization purposes
        manager_values_visual = [v if v is not None else 0 for v in manager_values]
        
        fig.add_trace(go.Scatterpolar(
            r=manager_values_visual,
            theta=labels,
            fill='toself',
            name='Manager Assessment',
            line=dict(color='green')
        ))
    
    # Set layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title="Combined Skills Assessment",
        showlegend=True
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

def combined_competency_radar(employee_id):
    """Create a combined radar chart showing both self and manager assessments for an employee's competencies"""
    # Get competency data
    competencies_df = load_data("competencies")
    
    if competencies_df.empty:
        return None, "No competencies found."
    
    # Create lists for chart data
    labels = []
    self_values = []
    manager_values = []
    
    # Get unique competency identifiers
    comp_identifiers = []
    
    # First gather all possible competencies for this employee
    for _, comp_row in competencies_df.iterrows():
        # Check if either self or manager assessment exists
        self_assessment = get_latest_competency_assessment(
            employee_id, 
            comp_row["name"], 
            "self"
        )
        
        manager_assessment = get_latest_competency_assessment(
            employee_id, 
            comp_row["name"], 
            "manager"
        )
        
        if self_assessment is not None or manager_assessment is not None:
            comp_identifiers.append(comp_row["name"])
    
    # Then populate the data arrays
    for comp_name in comp_identifiers:
        labels.append(comp_name)
        
        # Get latest self assessment
        self_assessment = get_latest_competency_assessment(
            employee_id, 
            comp_name, 
            "self"
        )
        if self_assessment is not None:
            self_values.append(float(self_assessment["score"]))
        else:
            self_values.append(None)
        
        # Get latest manager assessment
        manager_assessment = get_latest_competency_assessment(
            employee_id, 
            comp_name, 
            "manager"
        )
        if manager_assessment is not None:
            manager_values.append(float(manager_assessment["score"]))
        else:
            manager_values.append(None)
    
    if not labels:
        return None, "No competency assessments found for this employee."
    
    # Create combined radar chart
    fig = go.Figure()
    
    # Add self assessment data
    if any(v is not None for v in self_values):
        # Replace None with 0 for visualization purposes
        self_values_visual = [v if v is not None else 0 for v in self_values]
        
        fig.add_trace(go.Scatterpolar(
            r=self_values_visual,
            theta=labels,
            fill='toself',
            name='Self Assessment',
            line=dict(color='blue')
        ))
    
    # Add manager assessment data
    if any(v is not None for v in manager_values):
        # Replace None with 0 for visualization purposes
        manager_values_visual = [v if v is not None else 0 for v in manager_values]
        
        fig.add_trace(go.Scatterpolar(
            r=manager_values_visual,
            theta=labels,
            fill='toself',
            name='Manager Assessment',
            line=dict(color='green')
        ))
    
    # Set layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title="Combined Competency Assessment",
        showlegend=True
    )
    
    return fig, None

def competency_bar_chart(team_assessments, level_expectations=None, assessment_type="self", title="Competency Assessment"):
    """Create a bar chart for competencies using team assessment data
    
    Args:
        team_assessments: DataFrame containing assessment data
        level_expectations: DataFrame containing expectation data for job levels (optional)
        assessment_type: Type of assessment to use (should be pre-filtered)
        title: Title for the chart
    """
    # Load necessary data
    competencies_df = load_data("competencies")
    
    # Check if dataframes are empty
    if competencies_df.empty or team_assessments.empty:
        return None, "No competencies or assessments found."
    
    # Calculate the mean score for each competency from the filtered assessments
    comp_means = team_assessments.groupby('competency')['score'].mean().reset_index()
    
    if comp_means.empty:
        return None, f"No {assessment_type} competency assessments found."
    
    # Create lists for chart data
    labels = comp_means['competency'].tolist()
    actual_values = comp_means['score'].tolist()
    expected_values = []
    
    # Get expectation data if available
    if level_expectations is not None and not level_expectations.empty:
        # For each competency, find its expectation
        for comp in labels:
            expectation = level_expectations[level_expectations["competency"] == comp]
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
    if expected_values and any(v is not None for v in expected_values):
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
def combined_team_skill_radar(team_assessments, title="Team Skills Assessment"):
    """Create a combined radar chart for a team's skills showing both self and manager assessments
    
    Args:
        team_assessments: DataFrame containing team assessment data
        title: Title for the chart
    """
    import plotly.graph_objects as go
    from data_manager import load_data, get_latest_assessment
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
    
    # Dictionaries to store cumulative skill scores and counts for averaging
    self_skill_data = {}  # {(competency, skill): [total_score, count]}
    manager_skill_data = {}  # {(competency, skill): [total_score, count]}
    
    # Process each employee's latest assessments
    for employee_id in team_employee_ids:
        # Loop through all competencies and skills
        for _, comp_row in competencies_df.iterrows():
            comp_skills = skills_df[skills_df["competency_id"] == comp_row["competency_id"]]
            
            for _, skill_row in comp_skills.iterrows():
                # Get latest self assessment for this skill
                self_latest = get_latest_assessment(
                    employee_id, 
                    comp_row["name"], 
                    skill_row["name"], 
                    "self"
                )
                
                if self_latest is not None:
                    key = (comp_row["name"], skill_row["name"])
                    if key not in self_skill_data:
                        self_skill_data[key] = [self_latest["score"], 1]
                    else:
                        self_skill_data[key][0] += self_latest["score"]
                        self_skill_data[key][1] += 1
                
                # Get latest manager assessment for this skill
                manager_latest = get_latest_assessment(
                    employee_id, 
                    comp_row["name"], 
                    skill_row["name"], 
                    "manager"
                )
                
                if manager_latest is not None:
                    key = (comp_row["name"], skill_row["name"])
                    if key not in manager_skill_data:
                        manager_skill_data[key] = [manager_latest["score"], 1]
                    else:
                        manager_skill_data[key][0] += manager_latest["score"]
                        manager_skill_data[key][1] += 1
    
    # Get all unique keys (competency, skill pairs)
    all_keys = list(set(list(self_skill_data.keys()) + list(manager_skill_data.keys())))
    
    if not all_keys:
        return None, "No skill assessments found for this team."
    
    # Setup for radar chart
    labels = []
    self_values = []
    manager_values = []
    
    # Prepare data for the chart
    for key in sorted(all_keys):
        comp, skill = key
        labels.append(f"{comp} - {skill}")
        
        # Add self assessment data
        if key in self_skill_data:
            total, count = self_skill_data[key]
            self_values.append(total / count)
        else:
            self_values.append(None)
        
        # Add manager assessment data
        if key in manager_skill_data:
            total, count = manager_skill_data[key]
            manager_values.append(total / count)
        else:
            manager_values.append(None)
    
    # Create combined radar chart
    fig = go.Figure()
    
    # Add self assessment data
    if any(v is not None for v in self_values):
        # Replace None with 0 for visualization purposes
        self_values_visual = [v if v is not None else 0 for v in self_values]
        
        fig.add_trace(go.Scatterpolar(
            r=self_values_visual,
            theta=labels,
            fill='toself',
            name='Self Assessment',
            line=dict(color='blue')
        ))
    
    # Add manager assessment data
    if any(v is not None for v in manager_values):
        # Replace None with 0 for visualization purposes
        manager_values_visual = [v if v is not None else 0 for v in manager_values]
        
        fig.add_trace(go.Scatterpolar(
            r=manager_values_visual,
            theta=labels,
            fill='toself',
            name='Manager Assessment',
            line=dict(color='green')
        ))
    
    # Set layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title=title,
        showlegend=True
    )
    
    return fig, None

def combined_team_competency_radar(team_assessments, title="Team Competency Assessment"):
    """Create a combined radar chart for a team's competencies showing both self and manager assessments
    
    Args:
        team_assessments: DataFrame containing team assessment data
        title: Title for the chart
    """
    import plotly.graph_objects as go
    from data_manager import load_data, get_latest_competency_assessment
    
    # Load necessary data
    competencies_df = load_data("competencies")
    
    # Check if dataframes are empty
    if competencies_df.empty or team_assessments.empty:
        return None, "No team members or competencies found."
    
    # Get unique employee IDs from the assessments
    team_employee_ids = team_assessments["employee_id"].unique().tolist()
    if not team_employee_ids:
        return None, "No team members found in the assessments."
    
    # Dictionaries to store cumulative competency scores and counts for averaging
    self_comp_data = {}  # {competency: [total_score, count]}
    manager_comp_data = {}  # {competency: [total_score, count]}
    
    # Process each employee's latest assessments
    for employee_id in team_employee_ids:
        # Loop through all competencies
        for _, comp_row in competencies_df.iterrows():
            # Get latest self assessment for this competency
            self_latest = get_latest_competency_assessment(
                employee_id, 
                comp_row["name"], 
                "self"
            )
            
            if self_latest is not None:
                key = comp_row["name"]
                if key not in self_comp_data:
                    self_comp_data[key] = [self_latest["score"], 1]
                else:
                    self_comp_data[key][0] += self_latest["score"]
                    self_comp_data[key][1] += 1
            
            # Get latest manager assessment for this competency
            manager_latest = get_latest_competency_assessment(
                employee_id, 
                comp_row["name"], 
                "manager"
            )
            
            if manager_latest is not None:
                key = comp_row["name"]
                if key not in manager_comp_data:
                    manager_comp_data[key] = [manager_latest["score"], 1]
                else:
                    manager_comp_data[key][0] += manager_latest["score"]
                    manager_comp_data[key][1] += 1
    
    # Get all unique keys (competencies)
    all_keys = list(set(list(self_comp_data.keys()) + list(manager_comp_data.keys())))
    
    if not all_keys:
        return None, "No competency assessments found for this team."
    
    # Setup for radar chart
    labels = []
    self_values = []
    manager_values = []
    
    # Prepare data for the chart
    for key in sorted(all_keys):
        labels.append(key)
        
        # Add self assessment data
        if key in self_comp_data:
            total, count = self_comp_data[key]
            self_values.append(total / count)
        else:
            self_values.append(None)
        
        # Add manager assessment data
        if key in manager_comp_data:
            total, count = manager_comp_data[key]
            manager_values.append(total / count)
        else:
            manager_values.append(None)
    
    # Create combined radar chart
    fig = go.Figure()
    
    # Add self assessment data
    if any(v is not None for v in self_values):
        # Replace None with 0 for visualization purposes
        self_values_visual = [v if v is not None else 0 for v in self_values]
        
        fig.add_trace(go.Scatterpolar(
            r=self_values_visual,
            theta=labels,
            fill='toself',
            name='Self Assessment',
            line=dict(color='blue')
        ))
    
    # Add manager assessment data
    if any(v is not None for v in manager_values):
        # Replace None with 0 for visualization purposes
        manager_values_visual = [v if v is not None else 0 for v in manager_values]
        
        fig.add_trace(go.Scatterpolar(
            r=manager_values_visual,
            theta=labels,
            fill='toself',
            name='Manager Assessment',
            line=dict(color='green')
        ))
    
    # Set layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title=title,
        showlegend=True
    )
    
    return fig, None

def combined_comparison_radar_chart(employee_id, job_level, view_type="Skills"):
    """Create a radar chart comparing the mean of self and manager assessments vs expected levels for next job level
    
    Args:
        employee_id: ID of the employee to display
        job_level: Current job level of the employee (e.g., "IC1 - Associate")
        view_type: Whether to show "Skills" or "Competencies"
    """
    import plotly.graph_objects as go
    from data_manager import load_data, get_latest_assessment, get_latest_competency_assessment
    
    # Load necessary data
    skills_df = load_data("skills")
    competencies_df = load_data("competencies")
    expectations_df = load_data("expectations")
    comp_expectations_df = load_data("competency_expectations")
    job_levels_df = load_data("levels")
    
    if competencies_df.empty:
        return None, "No competencies found."
    
    if view_type == "Skills" and skills_df.empty:
        return None, "No skills found."
    
    if view_type == "Skills" and expectations_df.empty:
        return None, "No skill expectations defined."
    
    if view_type == "Competencies" and comp_expectations_df.empty:
        return None, "No competency expectations defined."
    
    # Get the numeric level_id for the current job level
    if job_levels_df.empty:
        return None, "No job levels defined in the system."
    
    # Map the text-based job level to its numeric ID
    level_id_row = job_levels_df[job_levels_df["name"] == job_level]
    if level_id_row.empty:
        return None, f"Job level '{job_level}' not found in the system."
    
    current_level_id = int(level_id_row.iloc[0]["level_id"])
    next_level_id = current_level_id + 1
    
    # Find the next level in the job_levels_df
    next_level_row = job_levels_df[job_levels_df["level_id"].astype(int) == next_level_id]
    if next_level_row.empty:
        return None, f"No next job level defined after {job_level}."
    
    next_level_name = next_level_row.iloc[0]["name"]
    
    # Filter expectations for the next job level using the numeric ID
    if view_type == "Skills":
        next_level_expectations = expectations_df[expectations_df["job_level"] == str(next_level_id)]
        if next_level_expectations.empty:
            return None, f"No skill expectations defined for next job level '{next_level_name}'."
    else:
        next_level_expectations = comp_expectations_df[comp_expectations_df["job_level"] == str(next_level_id)]
        if next_level_expectations.empty:
            return None, f"No competency expectations defined for next job level '{next_level_name}'."
    
    # Create lists for chart data
    labels = []
    combined_values = []
    next_level_expected_values = []
    
    if view_type == "Skills":
        # Loop through all competencies and skills
        for _, comp_row in competencies_df.iterrows():
            comp_skills = skills_df[skills_df["competency_id"] == comp_row["competency_id"]]
            
            for _, skill_row in comp_skills.iterrows():
                # Get latest self assessment for this skill
                self_latest = get_latest_assessment(
                    employee_id, 
                    comp_row["name"], 
                    skill_row["name"], 
                    "self"
                )
                
                # Get latest manager assessment for this skill
                manager_latest = get_latest_assessment(
                    employee_id, 
                    comp_row["name"], 
                    skill_row["name"], 
                    "manager"
                )
                
                # Find matching expectation for the next level
                next_expectation = next_level_expectations[
                    (next_level_expectations["competency"] == comp_row["name"]) &
                    (next_level_expectations["skill"] == skill_row["name"])
                ]
                
                # Only include if next level expectation exists and at least one assessment exists
                if not next_expectation.empty and (self_latest is not None or manager_latest is not None):
                    # Calculate the combined mean of self and manager assessments
                    sum_scores = 0
                    count_scores = 0
                    
                    if self_latest is not None:
                        sum_scores += float(self_latest["score"])
                        count_scores += 1
                        
                    if manager_latest is not None:
                        sum_scores += float(manager_latest["score"])
                        count_scores += 1
                    
                    # Only add if we have at least one assessment
                    if count_scores > 0:
                        labels.append(f"{comp_row['name']} - {skill_row['name']}")
                        combined_values.append(sum_scores / count_scores)
                        next_level_expected_values.append(next_expectation.iloc[0]["expected_score"])
    else:
        # Loop through all competencies
        for _, comp_row in competencies_df.iterrows():
            # Get latest self assessment for this competency
            self_latest = get_latest_competency_assessment(
                employee_id, 
                comp_row["name"], 
                "self"
            )
            
            # Get latest manager assessment for this competency
            manager_latest = get_latest_competency_assessment(
                employee_id, 
                comp_row["name"], 
                "manager"
            )
            
            # Find matching expectation for the next level
            next_expectation = next_level_expectations[
                (next_level_expectations["competency"] == comp_row["name"])
            ]
            
            # Only include if next level expectation exists and at least one assessment exists
            if not next_expectation.empty and (self_latest is not None or manager_latest is not None):
                # Calculate the combined mean of self and manager assessments
                sum_scores = 0
                count_scores = 0
                
                if self_latest is not None:
                    sum_scores += float(self_latest["score"])
                    count_scores += 1
                    
                if manager_latest is not None:
                    sum_scores += float(manager_latest["score"])
                    count_scores += 1
                
                # Only add if we have at least one assessment
                if count_scores > 0:
                    labels.append(comp_row["name"])
                    combined_values.append(sum_scores / count_scores)
                    next_level_expected_values.append(next_expectation.iloc[0]["expected_score"])
    
    if not labels:
        return None, f"No matching {'skill' if view_type == 'Skills' else 'competency'} expectations found for next level assessments."
    
    # Create radar chart
    fig = go.Figure()
    
    # Add combined assessment values trace
    fig.add_trace(go.Scatterpolar(
        r=combined_values,
        theta=labels,
        fill='toself',
        name='Current Performance (Mean)',
        line=dict(color='blue')
    ))
    
    # Add next level expected values trace
    fig.add_trace(go.Scatterpolar(
        r=next_level_expected_values,
        theta=labels,
        fill='toself',
        name=f'Expected ({next_level_name})',
        line=dict(color='red', dash='dash')
    ))
    
    # Set layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        title=f"Current Performance vs. Next Level ({view_type})",
        showlegend=True
    )
    
    return fig, None