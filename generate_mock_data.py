import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import data_manager

# Load existing data
employees_df = pd.read_csv('employees.csv')
competencies_df = pd.read_csv('competencies.csv')
skills_df = pd.read_csv('skills.csv')
job_levels_df = pd.read_csv('job_levels.csv')

# Generate mock data based on job level
def generate_score_by_level(job_level):
    """Generate a plausible score based on employee job level"""
    level_base_scores = {
        "Associate": 2.0,
        "Mid Level": 3.0,
        "Senior": 4.0,
        "Staff": 4.5,
        "Principal": 4.8,
        "Manager": 4.0
    }
    
    base_score = level_base_scores.get(job_level, 3.0)
    # Add some randomness but keep within 0-5 range
    score = base_score + random.uniform(-1.0, 1.0)
    score = min(max(score, 1.0), 5.0)  # Keep score between 1 and 5
    return round(score, 1)  # Round to 1 decimal place

# Generate assessments for all employees
def generate_assessments():
    """Generate mock assessment data for all employees"""
    # Clear existing assessment data
    data_manager.save_data("assessments", pd.DataFrame({
        "assessment_id": [],
        "employee_id": [],
        "competency": [],
        "skill": [],
        "score": [],
        "assessment_type": [],
        "assessment_date": [],
        "notes": []
    }))
    
    data_manager.save_data("comp_assessments", pd.DataFrame({
        "assessment_id": [],
        "employee_id": [],
        "competency": [],
        "score": [],
        "assessment_type": [],
        "assessment_date": [],
        "notes": []
    }))
    
    # Settings
    assessment_date = datetime.now().strftime('%Y-%m-%d')
    assessment_types = ["self", "manager"]
    
    # Skill assessments
    skill_assessment_id = 1
    skill_assessments = []
    
    # Competency assessments
    comp_assessment_id = 1
    comp_assessments = []
    
    for _, employee in employees_df.iterrows():
        for assessment_type in assessment_types:
            # Skip manager assessments for some employees to create variation
            if assessment_type == "manager" and random.random() < 0.3:
                continue
                
            # Generate assessments for each competency and skill based on job level
            for _, comp in competencies_df.iterrows():
                # Competency assessment
                score = generate_score_by_level(employee['job_level'])
                
                # Add some variation for different assessment types
                if assessment_type == "manager":
                    # Manager might rate slightly lower or higher
                    score = score + random.uniform(-0.5, 0.5)
                    score = min(max(score, 1.0), 5.0)
                    score = round(score, 1)
                
                comp_assessments.append({
                    "assessment_id": comp_assessment_id,
                    "employee_id": employee['employee_id'],
                    "competency": comp['name'],
                    "score": score,
                    "assessment_type": assessment_type,
                    "assessment_date": assessment_date,
                    "notes": f"{assessment_type.capitalize()} assessment for {comp['name']}"
                })
                comp_assessment_id += 1
                
                # For each competency, find skills and create skill assessments
                comp_skills = skills_df[skills_df['competency_id'] == comp['competency_id']]
                
                for _, skill in comp_skills.iterrows():
                    # Skill assessment score - slightly varies from competency score
                    skill_score = score + random.uniform(-0.8, 0.8)
                    skill_score = min(max(skill_score, 1.0), 5.0)
                    skill_score = round(skill_score, 1)
                    
                    skill_assessments.append({
                        "assessment_id": skill_assessment_id,
                        "employee_id": employee['employee_id'],
                        "competency": comp['name'],
                        "skill": skill['name'],
                        "score": skill_score,
                        "assessment_type": assessment_type,
                        "assessment_date": assessment_date,
                        "notes": f"{assessment_type.capitalize()} assessment for {skill['name']}"
                    })
                    skill_assessment_id += 1
    
    # Create DataFrames and save
    skill_assessments_df = pd.DataFrame(skill_assessments)
    comp_assessments_df = pd.DataFrame(comp_assessments)
    
    data_manager.save_data("assessments", skill_assessments_df)
    data_manager.save_data("comp_assessments", comp_assessments_df)
    
    return len(skill_assessments), len(comp_assessments)

if __name__ == "__main__":
    num_skill_assessments, num_comp_assessments = generate_assessments()
    print(f"Generated {num_skill_assessments} skill assessments and {num_comp_assessments} competency assessments")