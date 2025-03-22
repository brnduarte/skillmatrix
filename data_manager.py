import pandas as pd
import os
import json
from datetime import datetime

# Define the data files
DATA_FILES = {
    "users": "users.csv",
    "employees": "employees.csv",
    "competencies": "competencies.csv",
    "skills": "skills.csv",
    "levels": "job_levels.csv",
    "expectations": "skill_expectations.csv",
    "comp_expectations": "competency_expectations.csv",
    "assessments": "skill_assessments.csv",
    "comp_assessments": "competency_assessments.csv",
    "organizations": "organizations.csv"
}

# Define the ID columns for each data type
ID_COLUMNS = {
    "users": "username",
    "employees": "employee_id",
    "competencies": "competency_id",
    "skills": "skill_id",
    "levels": "level_id",
    "expectations": None,  # Composite key
    "comp_expectations": None,  # Composite key
    "assessments": "assessment_id",
    "comp_assessments": "assessment_id",
    "organizations": "organization_id"
}

def load_data(data_type):
    """Load data from a CSV file"""
    if data_type not in DATA_FILES:
        raise ValueError(f"Unknown data type: {data_type}")
    
    file_path = DATA_FILES[data_type]
    
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        # Return empty DataFrame with the correct structure
        if data_type == "users":
            return pd.DataFrame(columns=["username", "password", "role", "name", "email"])
        elif data_type == "employees":
            return pd.DataFrame(columns=["employee_id", "name", "email", "job_title", "job_level", "department", "manager_id", "organization_id", "hire_date"])
        elif data_type == "competencies":
            return pd.DataFrame(columns=["competency_id", "name", "description", "organization_id"])
        elif data_type == "skills":
            return pd.DataFrame(columns=["skill_id", "competency_id", "name", "description"])
        elif data_type == "levels":
            return pd.DataFrame(columns=["level_id", "name", "description", "organization_id"])
        elif data_type == "expectations":
            return pd.DataFrame(columns=["job_level", "competency", "skill", "expected_score"])
        elif data_type == "comp_expectations":
            return pd.DataFrame(columns=["job_level", "competency", "expected_score"])
        elif data_type == "assessments":
            return pd.DataFrame(columns=["assessment_id", "employee_id", "competency", "skill", "score", "assessment_type", "assessment_date", "notes"])
        elif data_type == "comp_assessments":
            return pd.DataFrame(columns=["assessment_id", "employee_id", "competency", "score", "assessment_type", "assessment_date", "notes"])
        elif data_type == "organizations":
            return pd.DataFrame(columns=["organization_id", "name", "created_by", "created_at"])
        else:
            return pd.DataFrame()

def load_data_for_organization(data_type, organization_id):
    """Load data from a CSV file filtered by organization_id
    
    Args:
        data_type: Type of data to load (employees, competencies, levels, skills, assessments, etc.)
        organization_id: ID of the organization to filter by
        
    Returns:
        DataFrame containing only records for the specified organization
    """
    df = load_data(data_type)
    
    # Skip filtering for users and organizations
    if data_type in ["users", "organizations"]:
        return df
    
    # Check if empty dataframe
    if df.empty:
        return df
    
    # Handle special case for skills - they need to be filtered by their competency's organization
    if data_type == "skills" and "organization_id" not in df.columns:
        # Ensure organization_id is in the competencies table
        competencies_df = load_data("competencies")
        if "organization_id" not in competencies_df.columns:
            update_csv_structure("competencies", {"organization_id": None})
            competencies_df = load_data("competencies")
        
        # Filter competencies by organization
        if not competencies_df.empty and "organization_id" in competencies_df.columns:
            org_competencies = competencies_df[
                (competencies_df["organization_id"] == organization_id) | 
                (competencies_df["organization_id"].isna())
            ]
            
            # Then filter skills by those competencies
            if not org_competencies.empty:
                return df[df["competency_id"].isin(org_competencies["competency_id"])]
    
    # For all other data types, ensure organization_id column exists
    if "organization_id" not in df.columns:
        # Update the schema to include organization_id
        update_csv_structure(data_type, {"organization_id": None})
        df = load_data(data_type)
        if "organization_id" not in df.columns:
            return pd.DataFrame()  # Return empty dataframe if we can't add the column
    
    # Ensure organization_id in dataframe is numeric and compare with numeric organization_id parameter
    # Handle different potential data types in the CSV file
    if not df.empty and "organization_id" in df.columns:
        try:
            # Convert to numeric, but keep NaN values where conversion fails
            df["organization_id"] = pd.to_numeric(df["organization_id"], errors='coerce')
            
            # Convert organization_id parameter to int for comparison
            org_id_int = int(organization_id)
            
            # Filter by organization ID, including records where organization_id is NULL/None when needed
            return df[(df["organization_id"] == org_id_int) | 
                    (df["organization_id"].isna() & (data_type in ["expectations", "comp_expectations"]))]
        except (ValueError, TypeError):
            # If conversion fails, fall back to string comparison
            print(f"Warning: Data type conversion issue in organization filtering for {data_type}")
            return df[(df["organization_id"].astype(str) == str(organization_id)) | 
                    (df["organization_id"].isna() & (data_type in ["expectations", "comp_expectations"]))]
    return df

def save_data(data_type, df):
    """Save data to a CSV file"""
    if data_type not in DATA_FILES:
        raise ValueError(f"Unknown data type: {data_type}")
    
    file_path = DATA_FILES[data_type]
    df.to_csv(file_path, index=False)
    return True

def add_user(username, password, role, name, email):
    """Add a new user"""
    users_df = load_data("users")
    
    # Check if username already exists
    if not users_df.empty and username in users_df["username"].values:
        return False, "Username already exists"
    
    # Add new user
    new_user = pd.DataFrame({
        "username": [username],
        "password": [password],
        "role": [role],
        "name": [name],
        "email": [email]
    })
    
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    save_data("users", users_df)
    return True, "User added successfully"

def add_employee(name, email, job_title, job_level, department, manager_id, organization_id=None, hire_date=None):
    """Add a new employee"""
    employees_df = load_data("employees")
    
    # Generate new employee ID
    if employees_df.empty:
        new_id = 1
    else:
        new_id = employees_df["employee_id"].max() + 1
    
    # Add new employee
    if hire_date is None:
        hire_date = datetime.now().strftime("%Y-%m-%d")
    
    new_employee = pd.DataFrame({
        "employee_id": [new_id],
        "name": [name],
        "email": [email],
        "job_title": [job_title],
        "job_level": [job_level],
        "department": [department],
        "manager_id": [manager_id],
        "organization_id": [organization_id],
        "hire_date": [hire_date]
    })
    
    employees_df = pd.concat([employees_df, new_employee], ignore_index=True)
    save_data("employees", employees_df)
    return True, "Employee added successfully", new_id

def add_competency(name, description="", organization_id=None):
    """Add a new competency"""
    competencies_df = load_data("competencies")
    
    # Generate new competency ID
    if competencies_df.empty:
        new_id = 1
    else:
        new_id = competencies_df["competency_id"].max() + 1
    
    # Add new competency
    new_competency = pd.DataFrame({
        "competency_id": [new_id],
        "name": [name],
        "description": [description],
        "organization_id": [organization_id]
    })
    
    competencies_df = pd.concat([competencies_df, new_competency], ignore_index=True)
    save_data("competencies", competencies_df)
    return True, "Competency added successfully", new_id

def add_skill(competency_id, name, description=""):
    """Add a new skill to a competency"""
    skills_df = load_data("skills")
    competencies_df = load_data("competencies")
    
    # Check if competency exists
    if competencies_df.empty or competency_id not in competencies_df["competency_id"].values:
        return False, "Competency does not exist", None
    
    # Generate new skill ID
    if skills_df.empty:
        new_id = 1
    else:
        new_id = skills_df["skill_id"].max() + 1
    
    # Add new skill
    new_skill = pd.DataFrame({
        "skill_id": [new_id],
        "competency_id": [competency_id],
        "name": [name],
        "description": [description]
    })
    
    skills_df = pd.concat([skills_df, new_skill], ignore_index=True)
    save_data("skills", skills_df)
    return True, "Skill added successfully", new_id

def add_job_level(name, description="", organization_id=None):
    """Add a new job level"""
    levels_df = load_data("levels")
    
    # Generate new level ID
    if levels_df.empty:
        new_id = 1
    else:
        new_id = levels_df["level_id"].max() + 1
    
    # Add new level
    new_level = pd.DataFrame({
        "level_id": [new_id],
        "name": [name],
        "description": [description],
        "organization_id": [organization_id]
    })
    
    levels_df = pd.concat([levels_df, new_level], ignore_index=True)
    save_data("levels", levels_df)
    return True, "Job level added successfully", new_id

def set_skill_expectation(job_level, competency, skill, expected_score):
    """Set the expected score for a skill at a specific job level"""
    expectations_df = load_data("expectations")
    
    # Check if expectation already exists
    existing = expectations_df[
        (expectations_df["job_level"] == job_level) & 
        (expectations_df["competency"] == competency) & 
        (expectations_df["skill"] == skill)
    ]
    
    if not existing.empty:
        # Update existing expectation
        expectations_df.loc[existing.index, "expected_score"] = expected_score
    else:
        # Add new expectation
        new_expectation = pd.DataFrame({
            "job_level": [job_level],
            "competency": [competency],
            "skill": [skill],
            "expected_score": [expected_score]
        })
        expectations_df = pd.concat([expectations_df, new_expectation], ignore_index=True)
    
    save_data("expectations", expectations_df)
    return True, "Skill expectation set successfully"

def set_competency_expectation(job_level, competency, expected_score):
    """Set the expected score for a competency at a specific job level"""
    # Use a separate file for competency expectations
    comp_expectations_df = load_data("comp_expectations")
    
    # Check if expectation already exists
    existing = comp_expectations_df[
        (comp_expectations_df["job_level"] == job_level) & 
        (comp_expectations_df["competency"] == competency)
    ]
    
    if not existing.empty:
        # Update existing expectation
        comp_expectations_df.loc[existing.index, "expected_score"] = expected_score
    else:
        # Add new expectation
        new_expectation = pd.DataFrame({
            "job_level": [job_level],
            "competency": [competency],
            "expected_score": [expected_score]
        })
        comp_expectations_df = pd.concat([comp_expectations_df, new_expectation], ignore_index=True)
    
    save_data("comp_expectations", comp_expectations_df)
    return True, "Competency expectation set successfully"

def add_assessment(employee_id, competency, skill, score, assessment_type, notes="", organization_id=None):
    """Add a new skill assessment"""
    assessments_df = load_data("assessments")
    
    # Get employee's organization if not provided
    if organization_id is None and employee_id is not None:
        employees_df = load_data("employees")
        if not employees_df.empty:
            employee = employees_df[employees_df["employee_id"] == employee_id]
            if not employee.empty and "organization_id" in employee.columns:
                organization_id = employee.iloc[0].get("organization_id")
    
    # Generate new assessment ID
    if assessments_df.empty:
        new_id = 1
    else:
        new_id = assessments_df["assessment_id"].max() + 1
    
    # Add new assessment
    new_assessment = pd.DataFrame({
        "assessment_id": [new_id],
        "employee_id": [employee_id],
        "competency": [competency],
        "skill": [skill],
        "score": [score],
        "assessment_type": [assessment_type],
        "assessment_date": [datetime.now().strftime("%Y-%m-%d")],
        "notes": [notes],
        "organization_id": [organization_id]
    })
    
    assessments_df = pd.concat([assessments_df, new_assessment], ignore_index=True)
    save_data("assessments", assessments_df)
    return True, "Assessment added successfully", new_id

def get_employee_assessments(employee_id, assessment_type=None, organization_id=None):
    """Get all assessments for an employee
    
    Args:
        employee_id: ID of the employee
        assessment_type: Optional filter for assessment type (self/manager)
        organization_id: Optional organization ID to filter assessments
        
    Returns:
        DataFrame of assessments
    """
    assessments_df = load_data("assessments")
    
    if assessments_df.empty:
        return pd.DataFrame()
    
    # If no organization_id provided, get it from the employee record
    if organization_id is None and employee_id is not None:
        employees_df = load_data("employees")
        if not employees_df.empty:
            employee = employees_df[employees_df["employee_id"] == employee_id]
            if not employee.empty and "organization_id" in employee.columns:
                organization_id = employee.iloc[0].get("organization_id")
    
    # Base filter is always by employee ID
    filtered = assessments_df[assessments_df["employee_id"] == employee_id]
    
    # Add assessment type filter if provided
    if assessment_type:
        filtered = filtered[filtered["assessment_type"] == assessment_type]
    
    # Add organization filter if organization_id column exists
    if organization_id is not None and "organization_id" in filtered.columns:
        filtered = filtered[
            (filtered["organization_id"] == organization_id) | 
            (filtered["organization_id"].isna())
        ]
    
    return filtered

def get_skill_assessments(employee_id, competency, skill):
    """Get all assessments for a specific skill"""
    assessments_df = load_data("assessments")
    
    if assessments_df.empty:
        return pd.DataFrame()
    
    return assessments_df[
        (assessments_df["employee_id"] == employee_id) &
        (assessments_df["competency"] == competency) &
        (assessments_df["skill"] == skill)
    ]

def get_latest_assessment(employee_id, competency, skill, assessment_type, organization_id=None):
    """Get the latest assessment for a specific skill
    
    Args:
        employee_id: ID of the employee
        competency: Name of the competency
        skill: Name of the skill
        assessment_type: Type of assessment (self/manager)
        organization_id: Optional organization ID to filter assessments
        
    Returns:
        Latest assessment record or None if not found
    """
    assessments_df = load_data("assessments")
    
    if assessments_df.empty:
        return None
    
    # If no organization_id provided, get it from the employee record
    if organization_id is None and employee_id is not None:
        employees_df = load_data("employees")
        if not employees_df.empty:
            employee = employees_df[employees_df["employee_id"] == employee_id]
            if not employee.empty and "organization_id" in employee.columns:
                organization_id = employee.iloc[0].get("organization_id")
    
    # Base filter conditions
    conditions = [
        (assessments_df["employee_id"] == employee_id),
        (assessments_df["competency"] == competency),
        (assessments_df["skill"] == skill),
        (assessments_df["assessment_type"] == assessment_type)
    ]
    
    # Add organization filter if needed
    if organization_id is not None and "organization_id" in assessments_df.columns:
        conditions.append(
            (assessments_df["organization_id"] == organization_id) | 
            (assessments_df["organization_id"].isna())
        )
    
    # Apply all filters
    relevant = assessments_df[pd.Series(True, index=assessments_df.index)]
    for condition in conditions:
        relevant = relevant[condition]
    
    if relevant.empty:
        return None
    
    # Sort by date and get most recent
    relevant["assessment_date"] = pd.to_datetime(relevant["assessment_date"])
    latest = relevant.sort_values("assessment_date", ascending=False).iloc[0]
    return latest

def get_competency_skills(competency_id):
    """Get all skills for a competency"""
    skills_df = load_data("skills")
    
    if skills_df.empty:
        return pd.DataFrame()
    
    return skills_df[skills_df["competency_id"] == competency_id]

def calculate_employee_skill_means(employee_id):
    """Calculate the mean scores for all skills for an employee"""
    assessments_df = load_data("assessments")
    
    if assessments_df.empty:
        return pd.DataFrame()
    
    employee_assessments = assessments_df[assessments_df["employee_id"] == employee_id]
    
    if employee_assessments.empty:
        return pd.DataFrame()
    
    # Group by competency, skill, and assessment_type and calculate mean
    means = employee_assessments.groupby(["competency", "skill", "assessment_type"])["score"].mean().reset_index()
    
    return means

def calculate_employee_competency_means(employee_id):
    """Calculate the mean scores for competencies (separately from skills)"""
    assessments_df = load_data("assessments")
    
    if assessments_df.empty:
        return pd.DataFrame()
    
    employee_assessments = assessments_df[assessments_df["employee_id"] == employee_id]
    
    if employee_assessments.empty:
        return pd.DataFrame()
    
    # Group by competency and assessment_type and calculate mean
    means = employee_assessments.groupby(["competency", "assessment_type"])["score"].mean().reset_index()
    
    return means

def get_employees_for_manager(manager_id, organization_id=None):
    """Get all employees reporting to a manager
    
    Args:
        manager_id: ID of the manager
        organization_id: Optional organization ID to filter employees
        
    Returns:
        DataFrame of employees reporting to this manager
    """
    try:
        employees_df = load_data("employees")
        
        if employees_df.empty:
            return pd.DataFrame()
        
        # If no organization_id provided, get it from the manager's record
        if organization_id is None and manager_id is not None:
            manager = employees_df[employees_df["employee_id"] == manager_id]
            if not manager.empty and "organization_id" in manager.columns:
                organization_id = manager.iloc[0].get("organization_id")
        
        # Always filter by manager_id
        filtered = employees_df[employees_df["manager_id"] == manager_id]
        
        # Add organization filter if needed
        if organization_id is not None and "organization_id" in filtered.columns:
            filtered = filtered[filtered["organization_id"] == organization_id]
        
        return filtered
        
    except Exception as e:
        print(f"Error getting employees for manager: {str(e)}")
        return pd.DataFrame()

def get_team_skill_means(manager_id, organization_id=None):
    """Calculate team skill means for a manager's team
    
    Args:
        manager_id: ID of the manager
        organization_id: Optional organization ID to filter data
        
    Returns:
        DataFrame with mean scores by competency, skill, and assessment type
    """
    # Get employees from the same organization as the manager
    team_members = get_employees_for_manager(manager_id, organization_id)
    assessments_df = load_data("assessments")
    
    if team_members.empty or assessments_df.empty:
        return pd.DataFrame()
    
    # Extract employee IDs
    team_employee_ids = team_members["employee_id"].tolist()
    
    if not team_employee_ids:
        return pd.DataFrame()
    
    # If no organization_id provided, get it from the manager's record
    if organization_id is None and manager_id is not None:
        employees_df = load_data("employees")
        if not employees_df.empty:
            manager = employees_df[employees_df["employee_id"] == manager_id]
            if not manager.empty and "organization_id" in manager.columns:
                organization_id = manager.iloc[0].get("organization_id")
    
    # Get assessments for all team members
    team_assessments = assessments_df[assessments_df["employee_id"].isin(team_employee_ids)]
    
    # Add organization filter if needed
    if organization_id is not None and "organization_id" in team_assessments.columns:
        team_assessments = team_assessments[
            (team_assessments["organization_id"] == organization_id) | 
            (team_assessments["organization_id"].isna())
        ]
    
    if team_assessments.empty:
        return pd.DataFrame()
    
    # Group by competency, skill and assessment_type and calculate mean
    means = team_assessments.groupby(["competency", "skill", "assessment_type"])["score"].mean().reset_index()
    
    return means

def get_team_competency_means(manager_id, organization_id=None):
    """Calculate team competency means for a manager's team (separate from skills)
    
    Args:
        manager_id: ID of the manager
        organization_id: Optional organization ID to filter data
        
    Returns:
        DataFrame with mean scores by competency and assessment type
    """
    # Get employees from the same organization as the manager
    team_members = get_employees_for_manager(manager_id, organization_id)
    assessments_df = load_data("assessments")
    
    if team_members.empty or assessments_df.empty:
        return pd.DataFrame()
    
    # Extract employee IDs
    team_employee_ids = team_members["employee_id"].tolist()
    
    if not team_employee_ids:
        return pd.DataFrame()
    
    # If no organization_id provided, get it from the manager's record
    if organization_id is None and manager_id is not None:
        employees_df = load_data("employees")
        if not employees_df.empty:
            manager = employees_df[employees_df["employee_id"] == manager_id]
            if not manager.empty and "organization_id" in manager.columns:
                organization_id = manager.iloc[0].get("organization_id")
    
    # Get assessments for all team members
    team_assessments = assessments_df[assessments_df["employee_id"].isin(team_employee_ids)]
    
    # Add organization filter if needed
    if organization_id is not None and "organization_id" in team_assessments.columns:
        team_assessments = team_assessments[
            (team_assessments["organization_id"] == organization_id) | 
            (team_assessments["organization_id"].isna())
        ]
    
    if team_assessments.empty:
        return pd.DataFrame()
    
    # Group by competency only and assessment_type and calculate mean
    means = team_assessments.groupby(["competency", "assessment_type"])["score"].mean().reset_index()
    
    return means

# Delete functions for each data type
def delete_record(data_type, record_id):
    """Delete a record from the specified data type by ID"""
    if data_type not in DATA_FILES:
        return False, f"Unknown data type: {data_type}"
    
    df = load_data(data_type)
    
    if df.empty:
        return False, f"No {data_type} data found"
    
    # Get the ID column name
    id_column = ID_COLUMNS.get(data_type)
    if id_column is None:
        return False, f"Cannot delete from {data_type} using a simple ID"
    
    # Check if the record exists
    if record_id not in df[id_column].values:
        return False, f"{data_type} record with ID {record_id} not found"
    
    # Delete the record
    df = df[df[id_column] != record_id]
    save_data(data_type, df)
    
    return True, f"{data_type} record deleted successfully"

def delete_competency(competency_id):
    """Delete a competency and all associated skills and expectations"""
    # First check if there are any skills using this competency
    skills_df = load_data("skills")
    has_skills = not skills_df.empty and any(skills_df["competency_id"] == competency_id)
    
    # Also check if there are expectations using this competency's name
    expectations_df = load_data("expectations")
    comp_expectations_df = load_data("comp_expectations")
    competency_name = ""
    
    competencies_df = load_data("competencies")
    if not competencies_df.empty:
        competency = competencies_df[competencies_df["competency_id"] == competency_id]
        if not competency.empty:
            competency_name = competency.iloc[0]["name"]
    
    has_expectations = not expectations_df.empty and any(expectations_df["competency"] == competency_name)
    has_comp_expectations = not comp_expectations_df.empty and any(comp_expectations_df["competency"] == competency_name)
    
    # Also check if there are assessments using this competency's name
    assessments_df = load_data("assessments")
    has_assessments = not assessments_df.empty and any(assessments_df["competency"] == competency_name)
    
    # First delete associated skills
    if has_skills:
        skills_to_delete = skills_df[skills_df["competency_id"] == competency_id]
        for _, skill in skills_to_delete.iterrows():
            delete_skill(skill["skill_id"])
    
    # Then delete skill expectations
    if has_expectations:
        expectations_df = expectations_df[expectations_df["competency"] != competency_name]
        save_data("expectations", expectations_df)
    
    # Delete competency expectations
    if has_comp_expectations:
        comp_expectations_df = comp_expectations_df[comp_expectations_df["competency"] != competency_name]
        save_data("comp_expectations", comp_expectations_df)
    
    # Handle assessments
    if has_assessments:
        assessments_df = assessments_df[assessments_df["competency"] != competency_name]
        save_data("assessments", assessments_df)
    
    # Finally delete the competency
    competencies_df = competencies_df[competencies_df["competency_id"] != competency_id]
    save_data("competencies", competencies_df)
    
    return True, "Competency and related data deleted successfully"

def delete_skill(skill_id):
    """Delete a skill and all associated expectations and assessments"""
    skills_df = load_data("skills")
    if skills_df.empty:
        return False, "No skills data found"
    
    # Get the skill name and competency
    skill = skills_df[skills_df["skill_id"] == skill_id]
    if skill.empty:
        return False, f"Skill with ID {skill_id} not found"
    
    skill_name = skill.iloc[0]["name"]
    
    # Check for expectations and assessments using this skill's name
    expectations_df = load_data("expectations")
    has_expectations = not expectations_df.empty and any(expectations_df["skill"] == skill_name)
    
    assessments_df = load_data("assessments")
    has_assessments = not assessments_df.empty and any(assessments_df["skill"] == skill_name)
    
    # Delete expectations
    if has_expectations:
        expectations_df = expectations_df[expectations_df["skill"] != skill_name]
        save_data("expectations", expectations_df)
    
    # Delete assessments
    if has_assessments:
        assessments_df = assessments_df[assessments_df["skill"] != skill_name]
        save_data("assessments", assessments_df)
    
    # Delete the skill
    skills_df = skills_df[skills_df["skill_id"] != skill_id]
    save_data("skills", skills_df)
    
    return True, "Skill and related data deleted successfully"

def delete_job_level(level_id):
    """Delete a job level and all associated expectations"""
    levels_df = load_data("levels")
    if levels_df.empty:
        return False, "No job levels data found"
    
    # Get the level name
    level = levels_df[levels_df["level_id"] == level_id]
    if level.empty:
        return False, f"Job level with ID {level_id} not found"
    
    level_name = level.iloc[0]["name"]
    
    # Check for expectations using this level's name
    expectations_df = load_data("expectations")
    comp_expectations_df = load_data("comp_expectations")
    has_expectations = not expectations_df.empty and any(expectations_df["job_level"] == level_name)
    has_comp_expectations = not comp_expectations_df.empty and any(comp_expectations_df["job_level"] == level_name)
    
    # Also check for employees with this job level
    employees_df = load_data("employees")
    has_employees = not employees_df.empty and any(employees_df["job_level"] == level_name)
    
    # Warn if there are employees using this level
    if has_employees:
        return False, f"Cannot delete job level '{level_name}' because it is assigned to employees"
    
    # Delete skill expectations
    if has_expectations:
        expectations_df = expectations_df[expectations_df["job_level"] != level_name]
        save_data("expectations", expectations_df)
    
    # Delete competency expectations
    if has_comp_expectations:
        comp_expectations_df = comp_expectations_df[comp_expectations_df["job_level"] != level_name]
        save_data("comp_expectations", comp_expectations_df)
    
    # Delete the level
    levels_df = levels_df[levels_df["level_id"] != level_id]
    save_data("levels", levels_df)
    
    return True, "Job level and related data deleted successfully"

def delete_employee(employee_id):
    """Delete an employee and all associated assessments"""
    employees_df = load_data("employees")
    if employees_df.empty:
        return False, "No employees data found"
    
    # Check if employee exists
    employee = employees_df[employees_df["employee_id"] == employee_id]
    if employee.empty:
        return False, f"Employee with ID {employee_id} not found"
    
    # Check if there are other employees with this as manager
    has_subordinates = not employees_df.empty and any(employees_df["manager_id"] == employee_id)
    if has_subordinates:
        return False, f"Cannot delete employee because they are assigned as a manager"
    
    # Delete assessments
    assessments_df = load_data("assessments")
    if not assessments_df.empty:
        assessments_df = assessments_df[assessments_df["employee_id"] != employee_id]
        save_data("assessments", assessments_df)
    
    # Delete the employee
    employees_df = employees_df[employees_df["employee_id"] != employee_id]
    save_data("employees", employees_df)
    
    return True, "Employee and related data deleted successfully"

def delete_expectation(job_level, competency, skill):
    """Delete a specific skill expectation"""
    expectations_df = load_data("expectations")
    if expectations_df.empty:
        return False, "No expectations data found"
    
    # Find the specific expectation
    filtered = expectations_df[
        (expectations_df["job_level"] == job_level) & 
        (expectations_df["competency"] == competency) & 
        (expectations_df["skill"] == skill)
    ]
    
    if filtered.empty:
        return False, "Expectation not found"
    
    # Delete the expectation
    expectations_df = expectations_df.drop(filtered.index)
    save_data("expectations", expectations_df)
    
    return True, "Expectation deleted successfully"

def delete_competency_expectation(job_level, competency):
    """Delete a specific competency expectation"""
    comp_expectations_df = load_data("comp_expectations")
    if comp_expectations_df.empty:
        return False, "No competency expectations data found"
    
    # Find the specific expectation
    filtered = comp_expectations_df[
        (comp_expectations_df["job_level"] == job_level) & 
        (comp_expectations_df["competency"] == competency)
    ]
    
    if filtered.empty:
        return False, "Competency expectation not found"
    
    # Delete the expectation
    comp_expectations_df = comp_expectations_df.drop(filtered.index)
    save_data("comp_expectations", comp_expectations_df)
    
    return True, "Competency expectation deleted successfully"

def delete_assessment(assessment_id):
    """Delete a specific assessment"""
    assessments_df = load_data("assessments")
    if assessments_df.empty:
        return False, "No assessments data found"
    
    # Check if assessment exists
    assessment = assessments_df[assessments_df["assessment_id"] == assessment_id]
    if assessment.empty:
        return False, f"Assessment with ID {assessment_id} not found"
    
    # Delete the assessment
    assessments_df = assessments_df[assessments_df["assessment_id"] != assessment_id]
    save_data("assessments", assessments_df)
    
    return True, "Assessment deleted successfully"

def update_competency(competency_id, name=None, description=None):
    """Update a competency's details"""
    competencies_df = load_data("competencies")
    if competencies_df.empty:
        return False, "No competencies data found"
    
    # Check if competency exists
    competency = competencies_df[competencies_df["competency_id"] == competency_id]
    if competency.empty:
        return False, f"Competency with ID {competency_id} not found"
    
    # Get the current name for reference
    old_name = competency.iloc[0]["name"]
    
    # Update the competency
    if name is not None:
        competencies_df.loc[competency.index, "name"] = name
    
    if description is not None:
        competencies_df.loc[competency.index, "description"] = description
    
    save_data("competencies", competencies_df)
    
    # If name changed, update related records
    if name is not None and name != old_name:
        # Update skill expectations
        expectations_df = load_data("expectations")
        if not expectations_df.empty:
            expectations_df.loc[expectations_df["competency"] == old_name, "competency"] = name
            save_data("expectations", expectations_df)
        
        # Update competency expectations
        comp_expectations_df = load_data("comp_expectations")
        if not comp_expectations_df.empty:
            comp_expectations_df.loc[comp_expectations_df["competency"] == old_name, "competency"] = name
            save_data("comp_expectations", comp_expectations_df)
        
        # Update assessments
        assessments_df = load_data("assessments")
        if not assessments_df.empty:
            assessments_df.loc[assessments_df["competency"] == old_name, "competency"] = name
            save_data("assessments", assessments_df)
    
    return True, "Competency updated successfully"

def update_skill(skill_id, name=None, description=None):
    """Update a skill's details"""
    skills_df = load_data("skills")
    if skills_df.empty:
        return False, "No skills data found"
    
    # Check if skill exists
    skill = skills_df[skills_df["skill_id"] == skill_id]
    if skill.empty:
        return False, f"Skill with ID {skill_id} not found"
    
    # Get the current name for reference
    old_name = skill.iloc[0]["name"]
    
    # Update the skill
    if name is not None:
        skills_df.loc[skill.index, "name"] = name
    
    if description is not None:
        skills_df.loc[skill.index, "description"] = description
    
    save_data("skills", skills_df)
    
    # If name changed, update related records
    if name is not None and name != old_name:
        # Update expectations
        expectations_df = load_data("expectations")
        if not expectations_df.empty:
            expectations_df.loc[expectations_df["skill"] == old_name, "skill"] = name
            save_data("expectations", expectations_df)
        
        # Update assessments
        assessments_df = load_data("assessments")
        if not assessments_df.empty:
            assessments_df.loc[assessments_df["skill"] == old_name, "skill"] = name
            save_data("assessments", assessments_df)
    
    return True, "Skill updated successfully"

def update_job_level(level_id, name=None, description=None):
    """Update a job level's details"""
    levels_df = load_data("levels")
    if levels_df.empty:
        return False, "No job levels data found"
    
    # Check if level exists
    level = levels_df[levels_df["level_id"] == level_id]
    if level.empty:
        return False, f"Job level with ID {level_id} not found"
    
    # Get the current name for reference
    old_name = level.iloc[0]["name"]
    
    # Update the level
    if name is not None:
        levels_df.loc[level.index, "name"] = name
    
    if description is not None:
        levels_df.loc[level.index, "description"] = description
    
    save_data("levels", levels_df)
    
    # If name changed, update related records
    if name is not None and name != old_name:
        # Update skill expectations
        expectations_df = load_data("expectations")
        if not expectations_df.empty:
            expectations_df.loc[expectations_df["job_level"] == old_name, "job_level"] = name
            save_data("expectations", expectations_df)
        
        # Update competency expectations
        comp_expectations_df = load_data("comp_expectations")
        if not comp_expectations_df.empty:
            comp_expectations_df.loc[comp_expectations_df["job_level"] == old_name, "job_level"] = name
            save_data("comp_expectations", comp_expectations_df)
        
        # Update employees
        employees_df = load_data("employees")
        if not employees_df.empty:
            employees_df.loc[employees_df["job_level"] == old_name, "job_level"] = name
            save_data("employees", employees_df)
    
    return True, "Job level updated successfully"

def update_employee(employee_id, name=None, email=None, job_title=None, job_level=None, department=None, manager_id=None):
    """Update an employee's details"""
    employees_df = load_data("employees")
    if employees_df.empty:
        return False, "No employees data found"
    
    # Check if employee exists
    employee = employees_df[employees_df["employee_id"] == employee_id]
    if employee.empty:
        return False, f"Employee with ID {employee_id} not found"
    
    # Update the employee fields that are provided
    if name is not None:
        employees_df.loc[employee.index, "name"] = name
    
    if email is not None:
        employees_df.loc[employee.index, "email"] = email
    
    if job_title is not None:
        employees_df.loc[employee.index, "job_title"] = job_title
    
    if job_level is not None:
        employees_df.loc[employee.index, "job_level"] = job_level
    
    if department is not None:
        employees_df.loc[employee.index, "department"] = department
    
    if manager_id is not None:
        # Check that we're not creating a circular management relationship
        if manager_id == employee_id:
            return False, "An employee cannot be their own manager"
        employees_df.loc[employee.index, "manager_id"] = manager_id
    
    save_data("employees", employees_df)
    return True, "Employee updated successfully"

# Competency Assessment functions
def add_competency_assessment(employee_id, competency, score, assessment_type, notes="", organization_id=None):
    """Add a new competency assessment"""
    comp_assessments_df = load_data("comp_assessments")
    
    # Get employee's organization if not provided
    if organization_id is None and employee_id is not None:
        employees_df = load_data("employees")
        if not employees_df.empty:
            employee = employees_df[employees_df["employee_id"] == employee_id]
            if not employee.empty and "organization_id" in employee.columns:
                organization_id = employee.iloc[0].get("organization_id")
    
    # Generate new assessment ID
    if comp_assessments_df.empty:
        new_id = 1
    else:
        new_id = comp_assessments_df["assessment_id"].max() + 1
    
    # Add new assessment
    new_assessment = pd.DataFrame({
        "assessment_id": [new_id],
        "employee_id": [employee_id],
        "competency": [competency],
        "score": [score],
        "assessment_type": [assessment_type],
        "assessment_date": [datetime.now().strftime("%Y-%m-%d")],
        "notes": [notes],
        "organization_id": [organization_id]
    })
    
    comp_assessments_df = pd.concat([comp_assessments_df, new_assessment], ignore_index=True)
    save_data("comp_assessments", comp_assessments_df)
    return True, "Competency assessment added successfully", new_id

def get_employee_competency_assessments(employee_id, assessment_type=None, organization_id=None):
    """Get all competency assessments for an employee
    
    Args:
        employee_id: ID of the employee
        assessment_type: Optional filter for assessment type (self/manager)
        organization_id: Optional organization ID to filter assessments
        
    Returns:
        DataFrame of competency assessments
    """
    comp_assessments_df = load_data("comp_assessments")
    
    if comp_assessments_df.empty:
        return pd.DataFrame()
    
    # If no organization_id provided, get it from the employee record
    if organization_id is None and employee_id is not None:
        employees_df = load_data("employees")
        if not employees_df.empty:
            employee = employees_df[employees_df["employee_id"] == employee_id]
            if not employee.empty and "organization_id" in employee.columns:
                organization_id = employee.iloc[0].get("organization_id")
    
    # Base filter is always by employee ID
    filtered = comp_assessments_df[comp_assessments_df["employee_id"] == employee_id]
    
    # Add assessment type filter if provided
    if assessment_type:
        filtered = filtered[filtered["assessment_type"] == assessment_type]
    
    # Add organization filter if organization_id column exists
    if organization_id is not None and "organization_id" in filtered.columns:
        filtered = filtered[
            (filtered["organization_id"] == organization_id) | 
            (filtered["organization_id"].isna())
        ]
    
    return filtered

def get_latest_competency_assessment(employee_id, competency, assessment_type, organization_id=None):
    """Get the latest assessment for a specific competency
    
    Args:
        employee_id: ID of the employee
        competency: Name of the competency
        assessment_type: Type of assessment (self/manager)
        organization_id: Optional organization ID to filter assessments
        
    Returns:
        Latest assessment record or None if not found
    """
    comp_assessments_df = load_data("comp_assessments")
    
    if comp_assessments_df.empty:
        return None
    
    # If no organization_id provided, get it from the employee record
    if organization_id is None and employee_id is not None:
        employees_df = load_data("employees")
        if not employees_df.empty:
            employee = employees_df[employees_df["employee_id"] == employee_id]
            if not employee.empty and "organization_id" in employee.columns:
                organization_id = employee.iloc[0].get("organization_id")
    
    # Base filter conditions
    conditions = [
        (comp_assessments_df["employee_id"] == employee_id),
        (comp_assessments_df["competency"] == competency),
        (comp_assessments_df["assessment_type"] == assessment_type)
    ]
    
    # Add organization filter if needed
    if organization_id is not None and "organization_id" in comp_assessments_df.columns:
        conditions.append(
            (comp_assessments_df["organization_id"] == organization_id) | 
            (comp_assessments_df["organization_id"].isna())
        )
    
    # Apply all filters
    relevant = comp_assessments_df[pd.Series(True, index=comp_assessments_df.index)]
    for condition in conditions:
        relevant = relevant[condition]
    
    if relevant.empty:
        return None
    
    # Sort by date and get most recent
    relevant["assessment_date"] = pd.to_datetime(relevant["assessment_date"])
    latest = relevant.sort_values("assessment_date", ascending=False).iloc[0]
    return latest

def calculate_employee_comp_assessment_means(employee_id):
    """Calculate the mean scores for competency assessments"""
    comp_assessments_df = load_data("comp_assessments")
    
    if comp_assessments_df.empty:
        return pd.DataFrame()
    
    employee_assessments = comp_assessments_df[comp_assessments_df["employee_id"] == employee_id]
    
    if employee_assessments.empty:
        return pd.DataFrame()
    
    # Group by competency and assessment_type and calculate mean
    means = employee_assessments.groupby(["competency", "assessment_type"])["score"].mean().reset_index()
    
    return means

def get_team_comp_assessment_means(manager_id):
    """Calculate team competency assessment means for a manager's team"""
    employees_df = load_data("employees")
    comp_assessments_df = load_data("comp_assessments")
    
    if employees_df.empty or comp_assessments_df.empty:
        return pd.DataFrame()
    
    # Get all employees under this manager
    team_employees = employees_df[employees_df["manager_id"] == manager_id]["employee_id"].tolist()
    
    if not team_employees:
        return pd.DataFrame()
    
    # Get assessments for all team members
    team_assessments = comp_assessments_df[comp_assessments_df["employee_id"].isin(team_employees)]
    
    if team_assessments.empty:
        return pd.DataFrame()
    
    # Group by competency and assessment_type and calculate mean
    means = team_assessments.groupby(["competency", "assessment_type"])["score"].mean().reset_index()
    
    return means

def delete_competency_assessment(assessment_id):
    """Delete a specific competency assessment"""
    comp_assessments_df = load_data("comp_assessments")
    
    if comp_assessments_df.empty:
        return False, "No competency assessment found"
    
    if assessment_id not in comp_assessments_df["assessment_id"].values:
        return False, f"Competency assessment with ID {assessment_id} not found"
    
    comp_assessments_df = comp_assessments_df[comp_assessments_df["assessment_id"] != assessment_id]
    save_data("comp_assessments", comp_assessments_df)
    
    return True, "Competency assessment deleted successfully"


# Organization functions
def add_organization(name, created_by):
    """Add a new organization"""
    organizations_df = load_data("organizations")
    
    # Generate new organization ID
    if organizations_df.empty:
        new_id = 1
    else:
        new_id = organizations_df["organization_id"].max() + 1
    
    # Add new organization
    new_organization = pd.DataFrame({
        "organization_id": [new_id],
        "name": [name],
        "created_by": [created_by],
        "created_at": [datetime.now().strftime("%Y-%m-%d")]
    })
    
    organizations_df = pd.concat([organizations_df, new_organization], ignore_index=True)
    save_data("organizations", organizations_df)
    return True, "Organization added successfully", new_id

def get_organization(organization_id):
    """Get an organization by ID"""
    organizations_df = load_data("organizations")
    
    if organizations_df.empty:
        return None
    
    org = organizations_df[organizations_df["organization_id"] == organization_id]
    
    if org.empty:
        return None
    
    return org.iloc[0]

def get_organizations():
    """Get all organizations"""
    return load_data("organizations")

def get_user_organizations(username):
    """Get all organizations created by a user"""
    organizations_df = load_data("organizations")
    
    if organizations_df.empty:
        return pd.DataFrame()
    
    return organizations_df[organizations_df["created_by"] == username]

def update_organization(organization_id, name=None):
    """Update an organization's details"""
    organizations_df = load_data("organizations")
    
    if organizations_df.empty:
        return False, "No organizations found"
    
    # Check if organization exists
    organization_mask = organizations_df["organization_id"] == organization_id
    if not any(organization_mask):
        return False, f"Organization with ID {organization_id} not found"
    
    # Update fields if provided
    if name is not None:
        organizations_df.loc[organization_mask, "name"] = name
    
    save_data("organizations", organizations_df)
    return True, "Organization updated successfully"

def delete_organization(organization_id, force_delete=False):
    """Delete an organization
    
    Args:
        organization_id: ID of the organization to delete
        force_delete: If True, also delete all associated records
        
    Returns:
        Tuple of (success, message)
    """
    # Check if this organization has associated records
    employees_df = load_data("employees")
    competencies_df = load_data("competencies")
    skills_df = load_data("skills")
    job_levels_df = load_data("levels")
    assessments_df = load_data("assessments")
    competency_assessments_df = load_data("comp_assessments")
    expectations_df = load_data("expectations")
    competency_expectations_df = load_data("comp_expectations")
    
    # Convert organization_id to int for consistent comparison
    organization_id = int(organization_id)
    
    # Check if organization has associated records
    has_employees = not employees_df.empty and "organization_id" in employees_df.columns and any(employees_df["organization_id"].astype(str).astype(int) == organization_id)
    has_competencies = not competencies_df.empty and "organization_id" in competencies_df.columns and any(competencies_df["organization_id"].astype(str).astype(int) == organization_id)
    has_skills = not skills_df.empty and "organization_id" in skills_df.columns and any(skills_df["organization_id"].astype(str).astype(int) == organization_id)
    has_job_levels = not job_levels_df.empty and "organization_id" in job_levels_df.columns and any(job_levels_df["organization_id"].astype(str).astype(int) == organization_id)
    has_assessments = not assessments_df.empty and "organization_id" in assessments_df.columns and any(assessments_df["organization_id"].astype(str).astype(int) == organization_id)
    has_comp_assessments = not competency_assessments_df.empty and "organization_id" in competency_assessments_df.columns and any(competency_assessments_df["organization_id"].astype(str).astype(int) == organization_id)
    
    # If there are associated records and force_delete is False, prevent deletion
    if (has_employees or has_competencies or has_skills or has_job_levels or has_assessments or has_comp_assessments) and not force_delete:
        return False, "Cannot delete organization because it has associated records. Use force_delete to remove all associated data."
    
    # If force_delete is True, delete all associated records
    if force_delete:
        # Delete employees and their assessments
        if has_employees:
            # Get all employee IDs in this organization
            org_employees = employees_df[employees_df["organization_id"].astype(str).astype(int) == organization_id]
            for _, employee in org_employees.iterrows():
                delete_employee(employee["employee_id"])
        
        # Delete competencies and their skills
        if has_competencies:
            org_competencies = competencies_df[competencies_df["organization_id"].astype(str).astype(int) == organization_id]
            for _, competency in org_competencies.iterrows():
                delete_competency(competency["competency_id"])
        
        # Delete job levels
        if has_job_levels:
            org_levels = job_levels_df[job_levels_df["organization_id"].astype(str).astype(int) == organization_id]
            for _, level in org_levels.iterrows():
                delete_job_level(level["level_id"])
        
        # Delete any remaining assessments
        if has_assessments:
            assessments_df = assessments_df[assessments_df["organization_id"].astype(str).astype(int) != organization_id]
            save_data("assessments", assessments_df)
        
        # Delete any remaining competency assessments
        if has_comp_assessments:
            competency_assessments_df = competency_assessments_df[competency_assessments_df["organization_id"].astype(str).astype(int) != organization_id]
            save_data("comp_assessments", competency_assessments_df)
    
    # Now delete the organization record
    return delete_record("organizations", organization_id)

def update_csv_structure(data_type, add_columns):
    """Add new columns to a CSV file structure
    
    Args:
        data_type: Type of data (employees, competencies, etc.)
        add_columns: Dictionary of column names and default values to add
    
    Returns:
        Success status and message
    """
    try:
        df = load_data(data_type)
        
        # Check if columns already exist
        existing_columns = set(df.columns)
        new_columns = set(add_columns.keys())
        columns_to_add = new_columns - existing_columns
        
        if not columns_to_add:
            return True, f"No new columns to add to {data_type}"
        
        # Add the new columns with default values
        for col in columns_to_add:
            df[col] = add_columns[col]
        
        # Save the updated dataframe
        save_data(data_type, df)
        return True, f"Added columns {', '.join(columns_to_add)} to {data_type}"
    
    except Exception as e:
        return False, f"Error updating {data_type} structure: {str(e)}"

def update_schema_for_organizations():
    """Update the schema of all relevant data types to include organization_id field
    
    This ensures all data structures can be properly associated with an organization.
    """
    results = []
    
    # Primary entity schemas
    success, message = update_csv_structure("employees", {"organization_id": None})
    results.append(f"Employees: {message}")
    
    success, message = update_csv_structure("competencies", {"organization_id": None})
    results.append(f"Competencies: {message}")
    
    success, message = update_csv_structure("levels", {"organization_id": None})
    results.append(f"Job Levels: {message}")
    
    # Assessment schemas
    success, message = update_csv_structure("assessments", {"organization_id": None})
    results.append(f"Skill Assessments: {message}")
    
    success, message = update_csv_structure("comp_assessments", {"organization_id": None})
    results.append(f"Competency Assessments: {message}")
    
    # Expectation schemas
    success, message = update_csv_structure("expectations", {"organization_id": None})
    results.append(f"Skill Expectations: {message}")
    
    success, message = update_csv_structure("comp_expectations", {"organization_id": None})
    results.append(f"Competency Expectations: {message}")
    
    # Skills schema (linked through competencies)
    success, message = update_csv_structure("skills", {"organization_id": None})
    results.append(f"Skills: {message}")
    
    return results
