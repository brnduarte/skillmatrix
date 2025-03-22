"""
Script to fix employee data by ensuring all existing employees have organization_id = 1.
"""
import pandas as pd

# Load the employees data
df = pd.read_csv('employees.csv')

# Convert organization_id to a string for cleaner display
df['organization_id'] = df['organization_id'].astype(str)

# Replace any organization_id that is not 1 with 1
# This includes empty strings, NaN values, and values like '2025-03-22' that might have been mistakenly added
mask = (df['organization_id'] != '1.0') & (df['organization_id'] != '1')
updated_count = mask.sum()

# Update the organization_id to 1 for all employees
df.loc[mask, 'organization_id'] = '1'

# Save the updated dataframe
df.to_csv('employees.csv', index=False)

print(f"Updated {updated_count} employee records to organization_id = 1")
print("Employee data fixed.")