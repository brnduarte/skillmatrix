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
    "assessments": "skill_assessments.csv"
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
            return pd.DataFrame(columns=["employee_id", "name", "email", "job_title", "job_level", "department", "manager_id", "hire_date"])
        elif data_type == "competencies":
            return pd.DataFrame(columns=["competency_id", "name", "description"])
        elif data_type == "skills":
            return pd.DataFrame(columns=["skill_id", "competency_id", "name", "description"])
        elif data_type == "levels":
            return pd.DataFrame(columns=["level_id", "name", "description"])
        elif data_type == "expectations":
            return pd.DataFrame(columns=["job_level", "competency", "skill", "expected_score"])
        elif data_type == "assessments":
            return pd.DataFrame(columns=["assessment_id", "employee_id", "competency", "skill", "score", "assessment_type", "assessment_date", "notes"])
        else:
            return pd.DataFrame()

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

def add_employee(name, email, job_title, job_level, department, manager_id, hire_date=None):
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
        "hire_date": [hire_date]
    })
    
    employees_df = pd.concat([employees_df, new_employee], ignore_index=True)
    save_data("employees", employees_df)
    return True, "Employee added successfully", new_id

def add_competency(name, description=""):
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
        "description": [description]
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

def add_job_level(name, description=""):
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
        "description": [description]
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

def add_assessment(employee_id, competency, skill, score, assessment_type, notes=""):
    """Add a new skill assessment"""
    assessments_df = load_data("assessments")
    
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
        "notes": [notes]
    })
    
    assessments_df = pd.concat([assessments_df, new_assessment], ignore_index=True)
    save_data("assessments", assessments_df)
    return True, "Assessment added successfully", new_id

def get_employee_assessments(employee_id, assessment_type=None):
    """Get all assessments for an employee"""
    assessments_df = load_data("assessments")
    
    if assessments_df.empty:
        return pd.DataFrame()
    
    if assessment_type:
        return assessments_df[
            (assessments_df["employee_id"] == employee_id) &
            (assessments_df["assessment_type"] == assessment_type)
        ]
    else:
        return assessments_df[assessments_df["employee_id"] == employee_id]

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

def get_latest_assessment(employee_id, competency, skill, assessment_type):
    """Get the latest assessment for a specific skill"""
    assessments_df = load_data("assessments")
    
    if assessments_df.empty:
        return None
    
    relevant = assessments_df[
        (assessments_df["employee_id"] == employee_id) &
        (assessments_df["competency"] == competency) &
        (assessments_df["skill"] == skill) &
        (assessments_df["assessment_type"] == assessment_type)
    ]
    
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

def get_team_skill_means(manager_id):
    """Calculate team skill means for a manager's team"""
    employees_df = load_data("employees")
    assessments_df = load_data("assessments")
    
    if employees_df.empty or assessments_df.empty:
        return pd.DataFrame()
    
    # Get all employees under this manager
    team_employees = employees_df[employees_df["manager_id"] == manager_id]["employee_id"].tolist()
    
    if not team_employees:
        return pd.DataFrame()
    
    # Get assessments for all team members
    team_assessments = assessments_df[assessments_df["employee_id"].isin(team_employees)]
    
    if team_assessments.empty:
        return pd.DataFrame()
    
    # Group by competency and skill and calculate mean
    means = team_assessments.groupby(["competency", "skill", "assessment_type"])["score"].mean().reset_index()
    
    return means
