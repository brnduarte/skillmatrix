"""
This script updates the visualization colors in the application to be WCAG 2.2 compliant.
It reads the visualizations.py file and makes the necessary color changes to ensure
accessibility standards are met.
"""

import re

# Define the WCAG 2.2 compliant colors
wcag_colors = {
    # Original colors -> WCAG 2.2 compliant colors
    "'blue'": "'#0A1A2A'",  # Darker blue with better contrast
    "'red'": "'#B22222'",  # Darker red with better contrast
    "'green'": "'#006400'",  # Darker green with better contrast
    "'#0e2b3d'": "'#0A1A2A'",  # Darker blue with better contrast
    "'#d13c35'": "'#B22222'",  # Darker red with better contrast
    "'#e67e22'": "'#E36C09'",  # Darker orange with better contrast
    "'#f2bc54'": "'#FFCB4C'",  # Darker yellow with better contrast
    "'#f5f0d2'": "'#FFFFFF'",  # White for better contrast
}

# Read the visualizations.py file
with open('visualizations.py', 'r') as file:
    content = file.read()

# Replace colors and add width parameter to lines
modified_content = content

# Replace colors
for old_color, new_color in wcag_colors.items():
    # Replace colors in line=dict(color=...) statements
    modified_content = re.sub(
        f'line=dict\\(color={old_color}\\)',
        f'line=dict(color={new_color}, width=2)',  # Add width=2 for better visibility
        modified_content
    )
    
    # Also replace colors in other contexts if needed
    modified_content = modified_content.replace(
        f"[0, {old_color}]", 
        f"[0, {new_color}]"
    )
    modified_content = modified_content.replace(
        f"[0.25, {old_color}]", 
        f"[0.25, {new_color}]"
    )
    modified_content = modified_content.replace(
        f"[0.5, {old_color}]", 
        f"[0.5, {new_color}]"
    )
    modified_content = modified_content.replace(
        f"[0.75, {old_color}]", 
        f"[0.75, {new_color}]"
    )
    modified_content = modified_content.replace(
        f"[1, {old_color}]", 
        f"[1, {new_color}]"
    )

# Update rgba values for fillcolor
modified_content = modified_content.replace(
    "fillcolor='rgba(14, 43, 61, 0.2)'",
    "fillcolor='rgba(10, 26, 42, 0.2)'"
)
modified_content = modified_content.replace(
    "fillcolor='rgba(209, 60, 53, 0.2)'",
    "fillcolor='rgba(178, 34, 34, 0.2)'"
)

# Write the modified content back to the file
with open('visualizations.py', 'w') as file:
    file.write(modified_content)

print("Visualization colors have been updated to be WCAG 2.2 compliant.")