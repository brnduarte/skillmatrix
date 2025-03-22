"""
Script to ensure all data tables have organization_id = 1 for existing data.
This script makes sure organization IDs are consistent across all tables.
"""
import pandas as pd
import os

# List of CSV files to process
files_to_update = [
    'competencies.csv',
    'skills.csv',
    'job_levels.csv',
    'skill_assessments.csv',
    'competency_assessments.csv',
    'skill_expectations.csv',
    'competency_expectations.csv'
]

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
            # Convert to string for consistent comparison
            df['organization_id'] = df['organization_id'].astype(str)
            
            # Find rows where organization_id is not 1
            mask = (df['organization_id'] != '1') & (df['organization_id'] != '1.0')
            if mask.any():
                # Update organization_id to 1
                df.loc[mask, 'organization_id'] = '1'
                print(f"Updated {mask.sum()} rows in {filename}")
                
                # Save the updated file
                df.to_csv(filename, index=False)
            else:
                print(f"No rows to update in {filename}")
        else:
            print(f"File {filename} does not have an organization_id column")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

print("All data tables updated to use organization_id = 1 consistently.")