def combined_team_skill_radar(team_assessments, title="Team Skills Assessment"):
    """Create a combined radar chart for a team's skills showing both self and manager assessments
    
    Args:
        team_assessments: DataFrame containing team assessment data
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