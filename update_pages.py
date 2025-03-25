import os
import re

# Directory where page files are stored
pages_dir = "pages"

# Process all Python files in the pages directory
for filename in os.listdir(pages_dir):
    if not filename.endswith(".py"):
        continue
        
    filepath = os.path.join(pages_dir, filename)
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r') as file:
        content = file.read()
    
    # Add initialize_session_state import if needed
    if "initialize_session_state" not in content:
        content = re.sub(
            r'from utils import (.+?)(?=\n)',
            r'from utils import \1, initialize_session_state',
            content
        )
    
    # Replace the authentication check with the improved version
    # Pattern to match the authentication check code block
    auth_check_pattern = r'# Check if user is authenticated\s*if not hasattr\(st\.session_state, "authenticated"\) or not st\.session_state\.authenticated:\s*st\.warning\("Please login from the Home page\."\)\s*st\.stop\(\)'
    
    # New authentication check code block with improved session handling
    new_auth_check = """# Initialize session state and check if user is authenticated
state = initialize_session_state()
if not state["authenticated"]:
    st.warning("Please login from the Home page.")
    st.switch_page("app.py")
    st.stop()

# Check if user has selected an organization
if not state["organization_selected"]:
    st.warning("Please select an organization to continue.")
    st.switch_page("app.py")
    st.stop()"""
    
    # Replace authentication check
    content = re.sub(auth_check_pattern, new_auth_check, content)
    
    # Alternative pattern for pages that use a different pattern
    alt_auth_check_pattern = r'if not st\.session_state\.authenticated:\s*st\.warning\("Please login from the Home page\."\)\s*st\.stop\(\)'
    content = re.sub(alt_auth_check_pattern, new_auth_check, content)
    
    # Move check_page_access after auth checks
    access_check_pattern = r'# This page is accessible.+\n.*check_page_access\(\[.+?\]\)\).*\n.*st\.stop\(\)'
    
    # Find existing check_page_access calls
    access_check_match = re.search(r'if not check_page_access\(\[(.+?)\]\):\s*st\.stop\(\)', content)
    
    if access_check_match:
        # Extract the roles list
        roles = access_check_match.group(1)
        # Remove the old check_page_access call
        content = re.sub(r'if not check_page_access\(\[.+?\]\):\s*st\.stop\(\)', '', content)
        # Add the new check_page_access call after the auth checks
        new_access_check = f'# Check page access\nif not check_page_access([{roles}]):\n    st.stop()'
        content = content.replace(new_auth_check, f"{new_auth_check}\n\n{new_access_check}")
    
    # Write the updated content back to the file
    with open(filepath, 'w') as file:
        file.write(content)
    
    print(f"Updated {filepath}")
    
print("All pages updated!")
