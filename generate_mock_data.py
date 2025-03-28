import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import data_manager

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
    score = base_score + random.uniform(-0.8, 0.8)
    score = min(max(score, 1.0), 5.0)
    return round(score, 1)

def generate_assessments():
    employees_df = pd.read_csv('employees.csv')
    competencies_df = pd.read_csv('competencies.csv')
    skills_df = pd.read_csv('skills.csv')

    # Clear existing assessment data
    data_manager.save_data("skill_assessments", pd.DataFrame())
    data_manager.save_data("competency_assessments", pd.DataFrame())

    assessment_date = datetime.now().strftime('%Y-%m-%d')
    assessment_types = ["self", "manager"]

    skill_assessments = []
    comp_assessments = []
    skill_assessment_id = 1
    comp_assessment_id = 1

    for _, employee in employees_df.iterrows():
        for assessment_type in assessment_types:
            # Generate competency assessments
            for _, comp in competencies_df.iterrows():
                base_score = generate_score_by_level(employee['job_level'])

                # Add variation for manager assessments
                if assessment_type == "manager":
                    base_score = base_score + random.uniform(-0.3, 0.3)
                    base_score = min(max(base_score, 1.0), 5.0)
                    base_score = round(base_score, 1)

                comp_assessments.append({
                    "assessment_id": comp_assessment_id,
                    "employee_id": employee['employee_id'],
                    "competency": comp['name'],
                    "score": base_score,
                    "assessment_type": assessment_type,
                    "assessment_date": assessment_date,
                    "notes": f"{assessment_type.capitalize()} assessment for {comp['name']}",
                    "organization_id": employee['organization_id']
                })
                comp_assessment_id += 1

                # Generate skill assessments
                comp_skills = skills_df[skills_df['competency_id'] == comp['competency_id']]
                for _, skill in comp_skills.iterrows():
                    skill_score = base_score + random.uniform(-0.5, 0.5)
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
                        "notes": f"{assessment_type.capitalize()} assessment for {skill['name']}",
                        "organization_id": employee['organization_id']
                    })
                    skill_assessment_id += 1

    # Save the generated assessments
    skill_assessments_df = pd.DataFrame(skill_assessments)
    comp_assessments_df = pd.DataFrame(comp_assessments)

    data_manager.save_data("skill_assessments", skill_assessments_df)
    data_manager.save_data("competency_assessments", comp_assessments_df)

    return len(skill_assessments), len(comp_assessments)

if __name__ == "__main__":
    num_skill_assessments, num_comp_assessments = generate_assessments()
    print(f"Generated {num_skill_assessments} skill assessments and {num_comp_assessments} competency assessments")