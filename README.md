# Skill Matrix & Competency Framework

A comprehensive Streamlit-based skill management platform designed to help organizations track, visualize, and optimize employee capabilities through interactive assessment and visualization tools.

## Features

- **Framework Setup**: Configure competencies, skills, job levels, and expectations
- **Employee Assessment**: Self and manager skill/competency evaluations
- **Individual Performance**: Visualize personal progress and skill gaps
- **Team Dashboard**: Monitor team-wide capabilities and trends
- **Export Reports**: Generate detailed performance reports

## Technical Stack

- Streamlit for dynamic web interface
- Pandas for advanced data processing
- Interactive data visualization with Plotly
- CSV-based data storage with automatic persistence
- Modal-based CRUD operations for framework management
- Responsive design with WCAG 2.2 color compliance

## Installation

1. Clone this repository:
```
git clone <your-repo-url>
```

2. Install required packages:
```
pip install -r requirements.txt
```

3. Run the application:
```
streamlit run app.py
```

## Default Login

- Username: admin
- Password: admin

## Project Structure

- `app.py`: Main application entry point
- `data_manager.py`: Data persistence and business logic
- `utils.py`: Utility functions for authentication and calculations
- `visualizations.py`: Chart generation and visualization utilities
- `ui_helpers.py`: CSS and UI styling utilities
- `pages/`: Multiple page modules for different sections of the app

## License

[Insert your chosen license here]

## Contact

[Your contact information]