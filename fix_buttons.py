import re
import os

def fix_button_syntax(filename):
    with open(filename, 'r') as file:
        content = file.read()
    
    # Fix pattern: key= type="secondary", "button_key" or key= type="secondary", f"button_key_{id}"
    pattern = r'key=\s*type="secondary",\s*(f?"[^"]+")'
    replacement = r'key=\1, type="secondary"'
    
    fixed_content = re.sub(pattern, replacement, content)
    
    if fixed_content != content:
        with open(filename, 'w') as file:
            file.write(fixed_content)
        print(f"Fixed {filename}")
        return True
    return False

# Fix buttons in Framework_Setup.py
fix_button_syntax('pages/01_Framework_Setup.py')
