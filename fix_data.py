"""
Script to assign organization_id = 1 to all existing data without an organization_id.
This will link all previously created data to the first organization.
"""
import pandas as pd
import os

# List of CSV files to process
files_to_update = [
    'employees.csv',
    'competencies.csv',
    'skills.csv',
    'job_levels.csv',
    'skill_assessments.csv',
    'competency_assessments.csv',
    'skill_expectations.csv',
    'competency_expectations.csv'
]

# Organization ID to assign
org_id = 1

# Process each file
for filename in files_to_update:
    if not os.path.exists(filename):
        print(f"File {filename} does not exist, skipping.")
        continue
    
    try:
        # Read the CSV file
        df = pd.read_csv(filename)
        
        # Check if the file has an organization_id column
        if 'organization_id' in df.columns:
            # Update only rows where organization_id is null or empty
            null_org_mask = df['organization_id'].isna() | (df['organization_id'] == '')
            if null_org_mask.any():
                df.loc[null_org_mask, 'organization_id'] = org_id
                print(f"Updated {null_org_mask.sum()} rows in {filename}")
                
                # Save the updated file
                df.to_csv(filename, index=False)
            else:
                print(f"No rows to update in {filename}")
        else:
            print(f"File {filename} does not have an organization_id column")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

print("Data update complete.")