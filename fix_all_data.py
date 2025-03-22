"""
Script to ensure all data tables have organization_id = 1 for existing data.
This script makes sure organization IDs are consistent across all tables and 
converts them to the proper integer format for consistent comparison.
"""
import pandas as pd
import os
import numpy as np

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
            # Convert organization_id to numeric format, coerce errors to NaN
            df['organization_id'] = pd.to_numeric(df['organization_id'], errors='coerce')
            
            # Count how many non-1 values we have
            mask = (df['organization_id'] != 1) | df['organization_id'].isna()
            non_1_count = mask.sum()
            
            # Replace NaN and non-1 values with 1
            df['organization_id'] = df['organization_id'].fillna(1)
            df.loc[df['organization_id'] != 1, 'organization_id'] = 1
            
            # Convert to integer (no decimals)
            df['organization_id'] = df['organization_id'].astype(int)
            
            # Save the updated file
            df.to_csv(filename, index=False)
            
            print(f"Updated {non_1_count} rows in {filename}")
            if non_1_count > 0:
                print(f"First 5 rows of {filename} after update:")
                print(df.head())
        else:
            print(f"File {filename} does not have an organization_id column")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

print("All data tables updated to use organization_id = 1 consistently.")