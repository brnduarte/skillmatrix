"""
Script to fix employee data by ensuring all existing employees have organization_id = 1.
"""
import pandas as pd
import numpy as np

# Load the employees data
df = pd.read_csv('employees.csv')

# Make sure organization_id is an integer
# First replace any non-numeric values with NaN
df['organization_id'] = pd.to_numeric(df['organization_id'], errors='coerce')

# Then replace NaN with 1
df['organization_id'] = df['organization_id'].fillna(1)

# Convert to integer
df['organization_id'] = df['organization_id'].astype(int)

# Make sure all organization_id values are 1
updated_count = (df['organization_id'] != 1).sum()
df['organization_id'] = 1

# Display the first few rows for verification
print("First few rows after update:")
print(df[['employee_id', 'name', 'organization_id']].head())

# Save the updated dataframe
df.to_csv('employees.csv', index=False)

print(f"Updated {updated_count} employee records to organization_id = 1")
print("Employee data fixed.")