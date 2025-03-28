
import pandas as pd
from datetime import datetime
import random
from data_manager import add_organization, add_user, add_employee

def generate_demo_data():
    # Create Demo Org
    org_success, org_message, org_id = add_organization("Demo Org", "admin")
    if not org_success:
        print(f"Failed to create organization: {org_message}")
        return

    departments = ["Engineering", "Product", "Design"]
    job_levels = ["Associate", "Mid Level", "Senior", "Staff", "Principal"]
    
    # Create 3 managers
    managers = []
    for i in range(3):
        dept = departments[i % len(departments)]
        username = f"manager{i+1}"
        manager_success, manager_message = add_user(
            username=username,
            password="password123",  # For demo purposes
            role="manager",
            name=f"Manager {i+1}",
            email=f"manager{i+1}@demoorg.com"
        )
        
        if manager_success:
            emp_success, emp_message, emp_id = add_employee(
                name=f"Manager {i+1}",
                email=f"manager{i+1}@demoorg.com",
                job_title=f"{dept} Manager",
                job_level="Manager",
                department=dept,
                manager_id=None,
                organization_id=org_id
            )
            if emp_success:
                managers.append((emp_id, dept))
    
    # Create 47 employees
    for i in range(47):
        manager_id, dept = random.choice(managers)
        level = random.choice(job_levels)
        username = f"employee{i+1}"
        
        user_success, user_message = add_user(
            username=username,
            password="password123",  # For demo purposes
            role="employee",
            name=f"Employee {i+1}",
            email=f"employee{i+1}@demoorg.com"
        )
        
        if user_success:
            emp_success, emp_message, emp_id = add_employee(
                name=f"Employee {i+1}",
                email=f"employee{i+1}@demoorg.com",
                job_title=f"{dept} {level}",
                job_level=level,
                department=dept,
                manager_id=manager_id,
                organization_id=org_id
            )

if __name__ == "__main__":
    generate_demo_data()
