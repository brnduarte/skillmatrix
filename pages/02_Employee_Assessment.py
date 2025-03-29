import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Employee Assessment - Skill Matrix",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
from datetime import datetime
from data_manager import (
    load_data, load_data_for_organization, add_assessment, get_employee_assessments,
    get_latest_assessment, get_competency_skills,
    add_competency_assessment, get_employee_competency_assessments,
    get_latest_competency_assessment, add_note, get_employee_notes
)
from utils import check_permission, check_page_access, get_user_id, is_manager_of, get_employees_for_manager
from utils import get_current_organization_id, initialize_session_state, track_page_load
from ui_helpers import load_custom_css, create_custom_sidebar

# Load custom CSS for consistent styling
load_custom_css()

# Track current page for navigation highlighting
current_page = track_page_load()

# Initialize session state and check if user is authenticated
state = initialize_session_state()

# Check if user has selected an organization
if not state["organization_selected"]:
    st.warning("Please select an organization to continue.")
    st.switch_page("app.py")
    st.stop()

# Check page access
if not check_page_access(["admin", "manager", "employee", "email_user"]):
    st.stop()

# This page is accessible to all roles: admin, manager, employee, email_user


st.title("Employee Skill & Competency Assessment")

# Get current employee ID (for self-assessment)
employee_id = get_user_id(st.session_state.username)

# Check if framework is set up
organization_id = get_current_organization_id()
competencies_df = load_data_for_organization("competencies", organization_id)
skills_df = load_data_for_organization("skills", organization_id)

if competencies_df.empty or skills_df.empty:
    st.error("The competency framework has not been set up yet. Please ask an administrator to set it up.")
    st.stop()

# Email users only see self-assessment
if st.session_state.user_role == "email_user":
    # Self Assessment Section (no tabs)
    st.header("Self Assessment")

    if employee_id is None:
        st.warning("Your user account is not linked to an employee record. Please contact an administrator.")
    else:
        organization_id = get_current_organization_id()
        employees_df = load_data_for_organization("employees", organization_id)
        employee_info = employees_df[employees_df["employee_id"] == employee_id]

        if not employee_info.empty:
            st.write(f"Employee: **{employee_info.iloc[0]['name']}**")
            st.write(f"Job Title: {employee_info.iloc[0]['job_title']}")
            st.write(f"Job Level: {employee_info.iloc[0]['job_level']}")
            st.write(f"Department: {employee_info.iloc[0]['department']}")

            st.markdown("---")

            # Create tabs for skill vs competency assessment
            skill_tab, comp_tab = st.tabs(["Skill Assessment", "Competency Assessment"])

            # Skills Assessment Tab
            with skill_tab:
                # Get existing assessments
                assessments = get_employee_assessments(employee_id, "self")

                # Select competency for assessment
                st.subheader("Rate Your Skills")

                comp_options = competencies_df["name"].tolist()
                selected_comp = st.selectbox("Select Competency", comp_options, key="self_comp_skill")

                # Get competency ID
                selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]

                # Get skills for selected competency
                comp_skills = get_competency_skills(selected_comp_id)

                if not comp_skills.empty:
                    st.write(f"Rate your proficiency in these skills from 1 to 5:")
                    st.write("1: Novice, 2: Advanced Beginner, 3: Competent, 4: Proficient, 5: Expert")

                    skill_scores = {}
                    skill_notes = {}

                    for _, skill_row in comp_skills.iterrows():
                        skill_name = skill_row["name"]

                        # Check if there's an existing assessment for this skill
                        existing = get_latest_assessment(employee_id, selected_comp, skill_name, "self")

                        # Set default value based on existing assessment if available
                        default_value = float(existing["score"]) if existing is not None else 3.0
                        default_notes = existing["notes"] if existing is not None else ""

                        # Create expander for each skill
                        with st.expander(f"{skill_name} - {skill_row['description']}"):
                            skill_scores[skill_name] = st.slider(
                                f"Your rating for {skill_name}",
                                min_value=1.0,
                                max_value=5.0,
                                step=0.5,
                                value=default_value,
                                key=f"self_{skill_name}"
                            )

                            skill_notes[skill_name] = st.text_area(
                                "Notes (examples, achievements, areas for improvement)",
                                value=default_notes,
                                key=f"self_notes_{skill_name}"
                            )

                    # Submit button for all skills in this competency
                    if st.button("Submit Skill Assessments", key="submit_self_skills"):
                        for skill_name, score in skill_scores.items():
                            success, message, _ = add_assessment(
                                employee_id,
                                selected_comp,
                                skill_name,
                                score,
                                "self",
                                skill_notes[skill_name]
                            )

                            if success:
                                st.success(f"Assessment for {skill_name} submitted successfully.")
                            else:
                                st.error(f"Error submitting assessment for {skill_name}: {message}")
                else:
                    st.info(f"No skills found for {selected_comp}. Please contact an administrator.")

            # Competency Assessment Tab
            with comp_tab:
                st.subheader("Rate Your Competencies")

                # Select competency for assessment
                comp_options = competencies_df["name"].tolist()

                st.write(f"Rate your overall proficiency in these competency areas from 1 to 5:")
                st.write("1: Novice, 2: Advanced Beginner, 3: Competent, 4: Proficient, 5: Expert")

                comp_scores = {}
                comp_notes = {}

                for _, comp_row in competencies_df.iterrows():
                    comp_name = comp_row["name"]

                    # Check if there's an existing assessment for this competency
                    existing = get_latest_competency_assessment(employee_id, comp_name, "self")

                    # Set default value based on existing assessment if available
                    default_value = float(existing["score"]) if existing is not None else 3.0
                    default_notes = existing["notes"] if existing is not None else ""

                    # Create expander for each competency
                    with st.expander(f"{comp_name} - {comp_row['description']}"):
                        comp_scores[comp_name] = st.slider(
                            f"Your overall rating for {comp_name} competency",
                            min_value=1.0,
                            max_value=5.0,
                            step=0.5,
                            value=default_value,
                            key=f"self_comp_{comp_name}"
                        )

                        comp_notes[comp_name] = st.text_area(
                            "Notes (examples, achievements, areas for improvement)",
                            value=default_notes,
                            key=f"self_comp_notes_{comp_name}"
                        )

                # Submit button for all competency assessments
                if st.button("Submit Competency Assessments", key="submit_self_comps"):
                    for comp_name, score in comp_scores.items():
                        success, message, _ = add_competency_assessment(
                            employee_id,
                            comp_name,
                            score,
                            "self",
                            comp_notes[comp_name]
                        )

                        if success:
                            st.success(f"Assessment for {comp_name} competency submitted successfully.")
                        else:
                            st.error(f"Error submitting competency assessment for {comp_name}: {message}")
        else:
            st.warning("Employee record not found. Please contact an administrator.")

else:
    # For regular users (admin, manager, employee), show tabs
    tab1, tab2 = st.tabs(["Self Assessment", "Manager Assessment"])

    # Self Assessment Tab
    with tab1:
        st.header("Self Assessment")

        if employee_id is None:
            st.warning("Your user account is not linked to an employee record. Please contact an administrator.")
        else:
            organization_id = get_current_organization_id()
            employees_df = load_data_for_organization("employees", organization_id)
            employee_info = employees_df[employees_df["employee_id"] == employee_id]

            if not employee_info.empty:
                st.write(f"Employee: **{employee_info.iloc[0]['name']}**")
                st.write(f"Job Title: {employee_info.iloc[0]['job_title']}")
                st.write(f"Job Level: {employee_info.iloc[0]['job_level']}")
                st.write(f"Department: {employee_info.iloc[0]['department']}")

                st.markdown("---")

                # Create tabs for skill vs competency assessment
                skill_tab, comp_tab = st.tabs(["Skill Assessment", "Competency Assessment"])

                # Skills Assessment Tab
                with skill_tab:
                    # Get existing assessments
                    assessments = get_employee_assessments(employee_id, "self")

                    # Select competency for assessment
                    st.subheader("Rate Your Skills")

                    # Add descriptive information in an info box
                    st.info("Rate your skills for each competency. Each skill is rated on a scale of 1-5.")

                    # Create a container with border for the selection and rating form
                    with st.container(border=True):
                        comp_options = competencies_df["name"].tolist()
                        selected_comp = st.selectbox("Select Competency", comp_options, key="self_comp")

                        # Get competency ID
                        selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]

                        # Get skills for selected competency
                        comp_skills = get_competency_skills(selected_comp_id)

                        if not comp_skills.empty:
                            # Create a better rating legend with columns
                            st.write("### Rating Scale")
                            legend_cols = st.columns(5)
                            with legend_cols[0]:
                                st.markdown("**1: Novice**")
                            with legend_cols[1]:
                                st.markdown("**2: Advanced Beginner**")
                            with legend_cols[2]:
                                st.markdown("**3: Competent**") 
                            with legend_cols[3]:
                                st.markdown("**4: Proficient**")
                            with legend_cols[4]:
                                st.markdown("**5: Expert**")

                            st.divider()
                            st.subheader("Skills Assessment")

                            skill_scores = {}
                            skill_notes = {}

                            # Display skills in a more organized way
                            for _, skill_row in comp_skills.iterrows():
                                skill_name = skill_row["name"]
                                skill_desc = skill_row["description"]

                                # Check if there's an existing assessment for this skill
                                existing = get_latest_assessment(employee_id, selected_comp, skill_name, "self")

                                # Set default value based on existing assessment if available
                                default_value = float(existing["score"]) if existing is not None else 3.0
                                default_notes = existing["notes"] if existing is not None else ""

                                # Create a bordered container for each skill
                                with st.container(border=True):
                                    st.markdown(f"**{skill_name}**")
                                    st.caption(f"{skill_desc}")

                                    skill_scores[skill_name] = st.slider(
                                        f"Your rating for {skill_name}",
                                        min_value=1.0,
                                        max_value=5.0,
                                        step=0.5,
                                        value=default_value,
                                        key=f"self_{skill_name}"
                                    )

                                    skill_notes[skill_name] = st.text_area(
                                        "Notes (examples, achievements, areas for improvement)",
                                        value=default_notes,
                                        key=f"self_notes_{skill_name}",
                                        height=100
                                    )

                            # Submit button with better styling
                            st.divider()
                            submit_col1, submit_col2 = st.columns([1, 5])
                            with submit_col1:
                                if st.button("Submit Assessment", type="primary", key="submit_self"):
                                    for skill_name, score in skill_scores.items():
                                        success, message, _ = add_assessment(
                                            employee_id,
                                            selected_comp,
                                            skill_name,
                                            score,
                                            "self",
                                            skill_notes[skill_name]
                                        )

                                        if success:
                                            st.success(f"Assessment for {skill_name} submitted successfully.")
                                        else:
                                            st.error(f"Error submitting assessment for {skill_name}: {message}")
                        else:
                            st.warning(f"No skills found for {selected_comp}. Please contact an administrator.")

                # Competency Assessment Tab
                with comp_tab:
                    st.subheader("Rate Your Competencies")

                    # Add descriptive information in an info box
                    st.info("Rate your overall proficiency in each competency area. Each competency is rated on a scale of 1-5.")

                    # Create a container with border for the rating form
                    with st.container(border=True):
                        # Create a better rating legend with columns
                        st.write("### Rating Scale")
                        legend_cols = st.columns(5)
                        with legend_cols[0]:
                            st.markdown("**1: Novice**")
                        with legend_cols[1]:
                            st.markdown("**2: Advanced Beginner**")
                        with legend_cols[2]:
                            st.markdown("**3: Competent**") 
                        with legend_cols[3]:
                            st.markdown("**4: Proficient**")
                        with legend_cols[4]:
                            st.markdown("**5: Expert**")

                        st.divider()
                        st.subheader("Competency Assessment")

                        comp_scores = {}
                        comp_notes = {}

                        # Display competencies in a more organized way
                        for _, comp_row in competencies_df.iterrows():
                            comp_name = comp_row["name"]
                            comp_desc = comp_row["description"]

                            # Check if there's an existing assessment for this competency
                            existing = get_latest_competency_assessment(employee_id, comp_name, "self")

                            # Set default value based on existing assessment if available
                            default_value = float(existing["score"]) if existing is not None else 3.0
                            default_notes = existing["notes"] if existing is not None else ""

                            # Create a bordered container for each competency
                            with st.container(border=True):
                                st.markdown(f"**{comp_name}**")
                                st.caption(f"{comp_desc}")

                                comp_scores[comp_name] = st.slider(
                                    f"Your overall rating for {comp_name} competency",
                                    min_value=1.0,
                                    max_value=5.0,
                                    step=0.5,
                                    value=default_value,
                                    key=f"self_comp_{comp_name}"
                                )

                                comp_notes[comp_name] = st.text_area(
                                    "Notes (examples, achievements, areas for improvement)",
                                    value=default_notes,
                                    key=f"self_comp_notes_{comp_name}",
                                    height=100
                                )

                        # Submit button with better styling
                        st.divider()
                        submit_col1, submit_col2 = st.columns([1, 5])
                        with submit_col1:
                            if st.button("Submit Assessment", type="primary", key="submit_self_comp"):
                                for comp_name, score in comp_scores.items():
                                    success, message, _ = add_competency_assessment(
                                        employee_id,
                                        comp_name,
                                        score,
                                        "self",
                                        comp_notes[comp_name]
                                    )

                                    if success:
                                        st.success(f"Assessment for {comp_name} competency submitted successfully.")
                                    else:
                                        st.error(f"Error submitting competency assessment for {comp_name}: {message}")
            else:
                st.warning("Employee record not found. Please contact an administrator.")

    # Manager Assessment Tab
    with tab2:
        st.header("Manager Assessment")

        # Check if user is a manager
        if st.session_state.user_role in ["admin", "manager"]:
            organization_id = get_current_organization_id()
            employees_df = load_data_for_organization("employees", organization_id)

            # Get employees that this user manages
            if st.session_state.user_role == "admin":
                # Admins can assess anyone
                managed_employees = employees_df
            else:
                # Get the manager's employee ID
                manager_id = get_user_id(st.session_state.username)
                if manager_id is None:
                    st.warning("Your user account is not linked to an employee record. Please contact an administrator.")
                    managed_employees = pd.DataFrame()
                else:
                    managed_employees = get_employees_for_manager(manager_id)

            if not managed_employees.empty:
                # Select employee to assess
                employee_options = [(row["employee_id"], row["name"]) for _, row in managed_employees.iterrows()]
                employee_names = [e[1] for e in employee_options]
                employee_ids = [e[0] for e in employee_options]

                selected_emp_name = st.selectbox("Select Employee to Assess", employee_names, key="emp_assessment_select")
                selected_emp_idx = employee_names.index(selected_emp_name)
                selected_emp_id = employee_ids[selected_emp_idx]

                # Get employee details
                employee_info = employees_df[employees_df["employee_id"] == selected_emp_id]

                if not employee_info.empty:
                    st.write(f"Employee: **{employee_info.iloc[0]['name']}**")
                    st.write(f"Job Title: {employee_info.iloc[0]['job_title']}")
                    st.write(f"Job Level: {employee_info.iloc[0]['job_level']}")
                    st.write(f"Department: {employee_info.iloc[0]['department']}")

                    st.markdown("---")

                    # Create tabs for skill vs competency assessment
                    mgr_skill_tab, mgr_comp_tab = st.tabs(["Skill Assessment", "Competency Assessment"])

                    # Skills Assessment Tab
                    with mgr_skill_tab:
                        # Get existing assessments
                        assessments = get_employee_assessments(selected_emp_id, "manager")

                        # Select competency for assessment
                        st.subheader("Rate Employee Skills")

                        # Add descriptive information in an info box
                        st.info("Rate the employee's skills for each competency. Each skill is rated on a scale of 1-5.")

                        # Create a container with border for the selection and rating form
                        with st.container(border=True):
                            comp_options = competencies_df["name"].tolist()
                            selected_comp = st.selectbox("Select Competency", comp_options, key="manager_comp")

                            # Get competency ID
                            selected_comp_id = competencies_df[competencies_df["name"] == selected_comp]["competency_id"].iloc[0]

                            # Get skills for selected competency
                            comp_skills = get_competency_skills(selected_comp_id)

                            if not comp_skills.empty:
                                # Create a better rating legend with columns
                                st.write("### Rating Scale")
                                legend_cols = st.columns(5)
                                with legend_cols[0]:
                                    st.markdown("**1: Novice**")
                                with legend_cols[1]:
                                    st.markdown("**2: Advanced Beginner**")
                                with legend_cols[2]:
                                    st.markdown("**3: Competent**") 
                                with legend_cols[3]:
                                    st.markdown("**4: Proficient**")
                                with legend_cols[4]:
                                    st.markdown("**5: Expert**")

                                st.divider()
                                st.subheader("Skills Assessment")

                                skill_scores = {}
                                skill_notes = {}

                                # Display skills in a more organized way
                                for _, skill_row in comp_skills.iterrows():
                                    skill_name = skill_row["name"]
                                    skill_desc = skill_row["description"]

                                    # Check if there's an existing assessment for this skill
                                    existing = get_latest_assessment(selected_emp_id, selected_comp, skill_name, "manager")

                                    # Set default value based on existing assessment if available
                                    default_value = float(existing["score"]) if existing is not None else 3.0
                                    default_notes = existing["notes"] if existing is not None else ""

                                    # Create a bordered container for each skill
                                    with st.container(border=True):
                                        st.markdown(f"**{skill_name}**")
                                        st.caption(f"{skill_desc}")

                                        # Show employee's self-assessment if available
                                        self_assessment = get_latest_assessment(selected_emp_id, selected_comp, skill_name, "self")
                                        if self_assessment is not None:
                                            with st.container(border=True):
                                                st.markdown("**Employee's self-assessment**")
                                                st.markdown(f"**Score:** {self_assessment['score']} ({pd.to_datetime(self_assessment['assessment_date']).strftime('%Y-%m-%d')})")
                                                if self_assessment["notes"]:
                                                    st.markdown(f"**Notes:** {self_assessment['notes']}")

                                        skill_scores[skill_name] = st.slider(
                                            f"Your rating for {skill_name}",
                                            min_value=1.0,
                                            max_value=5.0,
                                            step=0.5,
                                            value=default_value,
                                            key=f"manager_{skill_name}"
                                        )

                                        skill_notes[skill_name] = st.text_area(
                                            "Feedback and notes",
                                            value=default_notes,
                                            key=f"manager_notes_{skill_name}",
                                            height=100
                                        )

                                # Submit button with better styling
                                st.divider()
                                submit_col1, submit_col2 = st.columns([1, 5])
                                with submit_col1:
                                    if st.button("Submit Assessment", type="primary", key="submit_manager"):
                                        for skill_name, score in skill_scores.items():
                                            success, message, _ = add_assessment(
                                                selected_emp_id,
                                                selected_comp,
                                                skill_name,
                                                score,
                                                "manager",
                                                skill_notes[skill_name]
                                            )

                                            if success:
                                                st.success(f"Assessment for {skill_name} submitted successfully.")
                                            else:
                                                st.error(f"Error submitting assessment for {skill_name}: {message}")
                            else:
                                st.warning(f"No skills found for {selected_comp}. Please contact an administrator.")

                    # Competency Assessment Tab
                    with mgr_comp_tab:
                        st.subheader("Rate Employee Competencies")

                        # Add descriptive information in an info box
                        st.info("Rate the employee's overall proficiency in each competency area. Each competency is rated on a scale of 1-5.")

                        # Create a container with border for the rating form
                        with st.container(border=True):
                            # Create a better rating legend with columns
                            st.write("### Rating Scale")
                            legend_cols = st.columns(5)
                            with legend_cols[0]:
                                st.markdown("**1: Novice**")
                            with legend_cols[1]:
                                st.markdown("**2: Advanced Beginner**")
                            with legend_cols[2]:
                                st.markdown("**3: Competent**") 
                            with legend_cols[3]:
                                st.markdown("**4: Proficient**")
                            with legend_cols[4]:
                                st.markdown("**5: Expert**")

                            st.divider()
                            st.subheader("Competency Assessment")

                            comp_scores = {}
                            comp_notes = {}

                            # Display competencies in a more organized way
                            for _, comp_row in competencies_df.iterrows():
                                comp_name = comp_row["name"]
                                comp_desc = comp_row["description"]

                                # Check if there's an existing assessment for this competency
                                existing = get_latest_competency_assessment(selected_emp_id, comp_name, "manager")

                                # Set default value based on existing assessment if available
                                default_value = float(existing["score"]) if existing is not None else 3.0
                                default_notes = existing["notes"] if existing is not None else ""

                                # Create a bordered container for each competency
                                with st.container(border=True):
                                    st.markdown(f"**{comp_name}**")
                                    st.caption(f"{comp_desc}")

                                    # Show employee's self-assessment if available
                                    self_comp_assessment = get_latest_competency_assessment(selected_emp_id, comp_name, "self")
                                    if self_comp_assessment is not None:
                                        with st.container(border=True):
                                            st.markdown("**Employee's self-assessment**")
                                            st.markdown(f"**Score:** {self_comp_assessment['score']} ({pd.to_datetime(self_comp_assessment['assessment_date']).strftime('%Y-%m-%d')})")
                                            if self_comp_assessment["notes"]:
                                                st.markdown(f"**Notes:** {self_comp_assessment['notes']}")

                                    comp_scores[comp_name] = st.slider(
                                        f"Your overall rating for {comp_name} competency",
                                        min_value=1.0,
                                        max_value=5.0,
                                        step=0.5,
                                        value=default_value,
                                        key=f"manager_comp_{comp_name}"
                                    )

                                    comp_notes[comp_name] = st.text_area(
                                        "Feedback and notes",
                                        value=default_notes,
                                        key=f"manager_comp_notes_{comp_name}",
                                        height=100
                                    )

                            # Submit button with better styling
                            st.divider()
                            submit_col1, submit_col2 = st.columns([1, 5])
                            with submit_col1:
                                if st.button("Submit Assessment", type="primary", key="submit_manager_comp"):
                                    for comp_name, score in comp_scores.items():
                                        success, message, _ = add_competency_assessment(
                                            selected_emp_id,
                                            comp_name,
                                            score,
                                            "manager",
                                            comp_notes[comp_name]
                                        )

                                        if success:
                                            st.success(f"Assessment for {comp_name} competency submitted successfully.")
                                        else:
                                            st.error(f"Error submitting competency assessment for {comp_name}: {message}")
                else:
                    st.warning("Employee record not found.")
            else:
                st.info("You don't have any team members to assess.")
        else:
            st.info("You need to be a manager or administrator to assess employees.")

        # Notes section
        st.subheader("Assessment Notes")

        # Get existing notes
        notes = get_employee_notes(selected_emp_id, get_user_id(st.session_state.username), "manager")

        # Display existing notes
        if not notes.empty:
                        for _, note in notes.iterrows():
                            with st.expander(f"Note from {note['author_type']} - {note['date']}", expanded=False):
                                st.write(note["content"])
                                if note["related_competencies"]:
                                    st.write("**Related Competencies:** " + note["related_competencies"])
                                if note["related_skills"]:
                                    st.write("**Related Skills:** " + note["related_skills"])
                                st.write("**Visibility:** " + ("Shared" if note["is_shared"] else "Private"))

                    # Add new note
                    with st.expander("Add New Note", expanded=False):
                        note_content = st.text_area("Note Content", key="new_note_content", height=150)
                        is_shared = st.checkbox("Share with Employee", key="note_is_shared")

                        # Multi-select for related items
                        related_comps = st.multiselect("Related Competencies", competencies_df["name"].tolist())
                        related_skills = st.multiselect("Related Skills", skills_df["name"].tolist())

                        if st.button("Add Note"):
                            if note_content.strip():
                                success, msg, _ = add_note(
                                    selected_emp_id,
                                    get_user_id(st.session_state.username),
                                    "manager",
                                    note_content,
                                    is_shared,
                                    get_current_organization_id(),
                                    related_skills,
                                    related_comps
                                )
                                if success:
                                    st.success("Note added successfully")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to add note: {msg}")
                            else:
                                st.warning("Please enter note content")


# Add explanatory text at the bottom
st.markdown("---")
st.markdown("""
### Assessment Guidelines

- Be honest in your self-assessment to identify growth opportunities
- Rate skills based on demonstrated behaviors and outcomes, not potential
- Consider concrete examples when assigning scores
- Use the notes field to provide context and examples
- Assessments should reflect current capabilities, not past or future potential
- The rating scale represents:
  - **1 (Novice)**: Basic understanding, needs guidance
  - **2 (Advanced Beginner)**: Can perform with support
  - **3 (Competent)**: Works independently on standard tasks
  - **4 (Proficient)**: Deep knowledge, can handle complex situations
  - **5 (Expert)**: Recognized authority, develops new approaches
""")