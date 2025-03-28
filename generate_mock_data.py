
import pandas as pd
import numpy as np
import random
from datetime import datetime
import data_manager

def generate_score_by_level(job_level, expected_score):
    """Generate a plausible score based on employee job level and expected score"""
    # Generate score with some variation around the expected score
    variation = random.uniform(-0.5, 0.3)  # Slightly biased towards lower scores
    score = expected_score + variation
    score = min(max(score, 1.0), 5.0)  # Ensure score stays within 1-5 range
    return round(score, 1)

def generate_assessments():
    employees_df = pd.read_csv('employees.csv')
    competencies_df = pd.read_csv('competencies.csv')
    skills_df = pd.read_csv('skills.csv')
    comp_expectations_df = pd.read_csv('competency_expectations.csv')
    skill_expectations_df = pd.read_csv('skill_expectations.csv')

    # Create empty DataFrames with correct columns
    skill_assessments_df = pd.DataFrame(columns=[
        "assessment_id", "employee_id", "competency", "skill", "score",
        "assessment_type", "assessment_date", "notes", "organization_id"
    ])
    comp_assessments_df = pd.DataFrame(columns=[
        "assessment_id", "employee_id", "competency", "score",
        "assessment_type", "assessment_date", "notes", "organization_id"
    ])
    
    # Save empty DataFrames to clear existing data
    data_manager.save_data("skill_assessments", skill_assessments_df)
    data_manager.save_data("comp_assessments", comp_assessments_df)

    assessment_date = datetime.now().strftime('%Y-%m-%d')
    skill_assessments = []
    comp_assessments = []
    skill_assessment_id = 1
    comp_assessment_id = 1

    for _, employee in employees_df.iterrows():
        job_level = employee['job_level']
        
        # Generate competency assessments
        for _, comp in competencies_df.iterrows():
            # Get expected score for this competency and job level
            expected_score_row = comp_expectations_df[
                (comp_expectations_df['job_level'] == job_level) & 
                (comp_expectations_df['competency'] == comp['name'])
            ]
            if not expected_score_row.empty:
                expected_score = expected_score_row.iloc[0]['expected_score']
                score = generate_score_by_level(job_level, expected_score)
                
                comp_assessments.append({
                    "assessment_id": comp_assessment_id,
                    "employee_id": employee['employee_id'],
                    "competency": comp['name'],
                    "score": score,
                    "assessment_type": "self",
                    "assessment_date": assessment_date,
                    "notes": f"Self assessment for {comp['name']}",
                    "organization_id": employee['organization_id']
                })
                comp_assessment_id += 1

                # Generate skill assessments for this competency
                comp_skills = skills_df[skills_df['competency_id'] == comp['competency_id']]
                for _, skill in comp_skills.iterrows():
                    # Get expected score for this skill and job level
                    expected_skill_score_row = skill_expectations_df[
                        (skill_expectations_df['job_level'] == job_level) & 
                        (skill_expectations_df['competency'] == comp['name']) &
                        (skill_expectations_df['skill'] == skill['name'])
                    ]
                    if not expected_skill_score_row.empty:
                        expected_skill_score = expected_skill_score_row.iloc[0]['expected_score']
                        skill_score = generate_score_by_level(job_level, expected_skill_score)
                        
                        skill_assessments.append({
                            "assessment_id": skill_assessment_id,
                            "employee_id": employee['employee_id'],
                            "competency": comp['name'],
                            "skill": skill['name'],
                            "score": skill_score,
                            "assessment_type": "self",
                            "assessment_date": assessment_date,
                            "notes": f"Self assessment for {skill['name']}",
                            "organization_id": employee['organization_id']
                        })
                        skill_assessment_id += 1

    # Save the generated assessments
    skill_assessments_df = pd.DataFrame(skill_assessments)
    comp_assessments_df = pd.DataFrame(comp_assessments)

    data_manager.save_data("skill_assessments", skill_assessments_df)
    data_manager.save_data("comp_assessments", comp_assessments_df)

    return len(skill_assessments), len(comp_assessments)

if __name__ == "__main__":
    num_skill_assessments, num_comp_assessments = generate_assessments()
    print(f"Generated {num_skill_assessments} skill assessments and {num_comp_assessments} competency assessments")
