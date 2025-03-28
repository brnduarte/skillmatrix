
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

    # List of diverse names for demo data
    manager_names = [
        ("Sarah Chen", "f"), 
        ("Miguel Rodriguez", "m"),
        ("Priya Patel", "f")
    ]
    
    employee_names = [
        ("James Wilson", "m"), ("Maria Garcia", "f"), ("Wei Zhang", "m"),
        ("Aisha Ahmed", "f"), ("Carlos Santos", "m"), ("Emma Thompson", "f"),
        ("Raj Kumar", "m"), ("Sofia Kowalski", "f"), ("Juan Martinez", "m"),
        ("Yuki Tanaka", "f"), ("David Kim", "m"), ("Fatima Al-Said", "f"),
        ("Andre Silva", "m"), ("Lisa Wang", "f"), ("Omar Hassan", "m"),
        ("Nina Petrova", "f"), ("Marcus Johnson", "m"), ("Leila Patel", "f"),
        ("Thomas Anderson", "m"), ("Zara Khan", "f"), ("Gabriel Costa", "m"),
        ("Maya Singh", "f"), ("Alexander Lee", "m"), ("Isabella Romano", "f"),
        ("Mohammed Ahmed", "m"), ("Ana Santos", "f"), ("Daniel Chen", "m"),
        ("Elena Popov", "f"), ("Lucas Mueller", "m"), ("Sophia Wong", "f"),
        ("Sanjay Gupta", "m"), ("Carmen Rodriguez", "f"), ("Benjamin Cohen", "m"),
        ("Amara Okafor", "f"), ("Henrik Nielsen", "m"), ("Mei Lin", "f"),
        ("Ali Kazemi", "m"), ("Victoria Smith", "f"), ("Ravi Sharma", "m"),
        ("Emilia Santos", "f"), ("Kenzo Yamamoto", "m"), ("Olivia Brown", "f"),
        ("Ricardo Torres", "m"), ("Anika Das", "f"), ("Jean-Pierre Dubois", "m"),
        ("Nadia Hassan", "f"), ("Lars Anderson", "m")
    ]

    departments = ["Engineering", "Product", "Design"]
    job_levels = ["Associate", "Mid Level", "Senior", "Staff", "Principal"]
    
    # Create 3 managers
    managers = []
    for i in range(3):
        dept = departments[i % len(departments)]
        name, gender = manager_names[i]
        username = name.lower().replace(" ", "")
        email = f"{username}@demoorg.com"
        
        manager_success, manager_message = add_user(
            username=username,
            password="password123",  # For demo purposes
            role="manager",
            name=name,
            email=email
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
        name, gender = employee_names[i]
        username = name.lower().replace(" ", "")
        email = f"{username}@demoorg.com"
        
        user_success, user_message = add_user(
            username=username,
            password="password123",  # For demo purposes
            role="employee",
            name=name,
            email=email
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
