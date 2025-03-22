import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import base64
from datetime import datetime
from data_manager import (
    load_data, get_employee_assessments, calculate_employee_skill_means,
    get_competency_skills, get_latest_assessment
)
from utils import check_permission, get_user_id, is_manager_of, get_employees_for_manager
from visualizations import (
    employee_skill_radar, comparison_radar_chart, team_skill_radar, team_competency_radar
)

# Page configuration
st.set_page_config(
    page_title="Export Reports - Skill Matrix",
    page_icon="📊",
    layout="wide"
)

# Check if user is authenticated
if not hasattr(st.session_state, "authenticated") or not st.session_state.authenticated:
    st.warning("Please login from the Home page.")
    st.stop()

# Check permissions - only managers and admins can export reports
if not check_permission("manager"):
    st.error("You don't have permission to access this page.")
    st.stop()

st.title("Export Reports")
st.write("Generate and export reports for individuals or teams")

# Helper function to convert dataframe to CSV download link
def get_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
    return href

# Helper function to convert dataframe to Excel download link
def get_excel_download_link(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download Excel</a>'
    return href

# Create tabs for different report types
tab1, tab2, tab3 = st.tabs([
    "Individual Reports", 
    "Team Reports",
    "Framework Reports"
])

# Individual Reports Tab
with tab1:
    st.header("Individual Performance Reports")
    
    # Get list of employees the user can access
    employees_df = load_data("employees")
    
    if employees_df.empty:
        st.warning("No employees found in the system.")
    else:
        # Filter employees based on user role
        if st.session_state.user_role == "admin":
            # Admins can see all employees
            available_employees = employees_df
        else:
            # Managers can see their team members
            manager_id = get_user_id(st.session_state.username)
            if manager_id is None:
                st.warning("Your user account is not linked to an employee record.")
                available_employees = pd.DataFrame()
            else:
                available_employees = get_employees_for_manager(manager_id)
        
        if not available_employees.empty:
            # Allow selecting employee
            employee_options = [(row["employee_id"], row["name"]) for _, row in available_employees.iterrows()]
            employee_names = [e[1] for e in employee_options]
            employee_ids = [e[0] for e in employee_options]
            
            selected_emp_name = st.selectbox("Select Employee", employee_names, key="export_employee_select")
            selected_emp_idx = employee_names.index(selected_emp_name)
            selected_emp_id = employee_ids[selected_emp_idx]
            
            # Allow selecting report type
            report_type = st.selectbox(
                "Report Type",
                ["Full Assessment Report", "Competency Breakdown", "Skills Gap Analysis"],
                key="individual_report_type"
            )
            
            # Get assessment data
            self_assessments = get_employee_assessments(selected_emp_id, "self")
            manager_assessments = get_employee_assessments(selected_emp_id, "manager")
            
            if self_assessments.empty and manager_assessments.empty:
                st.warning("No assessment data available for this employee.")
            else:
                # Get employee details
                employee_info = employees_df[employees_df["employee_id"] == selected_emp_id].iloc[0]
                
                if report_type == "Full Assessment Report":
                    # Create full assessment report
                    st.subheader(f"Full Assessment Report: {employee_info['name']}")
                    
                    # Prepare data
                    report_data = []
                    
                    competencies_df = load_data("competencies")
                    skills_df = load_data("skills")
                    expectations_df = load_data("expectations")
                    
                    # Get all assessments and organize by competency and skill
                    all_assessments = pd.concat([self_assessments, manager_assessments])
                    if not all_assessments.empty:
                        for _, assessment in all_assessments.iterrows():
                            competency = assessment["competency"]
                            skill = assessment["skill"]
                            assessment_type = assessment["assessment_type"]
                            score = assessment["score"]
                            date = pd.to_datetime(assessment["assessment_date"]).strftime("%Y-%m-%d")
                            notes = assessment["notes"]
                            
                            # Get expected score if available
                            expected_score = None
                            if not expectations_df.empty:
                                exp_row = expectations_df[
                                    (expectations_df["job_level"] == employee_info["job_level"]) &
                                    (expectations_df["competency"] == competency) &
                                    (expectations_df["skill"] == skill)
                                ]
                                if not exp_row.empty:
                                    expected_score = exp_row.iloc[0]["expected_score"]
                            
                            # Calculate gap
                            gap = None
                            if expected_score is not None:
                                gap = float(score) - float(expected_score)
                            
                            report_data.append({
                                "Competency": competency,
                                "Skill": skill,
                                "Assessment Type": assessment_type.capitalize(),
                                "Score": score,
                                "Expected Score": expected_score,
                                "Gap": gap,
                                "Assessment Date": date,
                                "Notes": notes
                            })
                    
                    if report_data:
                        # Convert to DataFrame
                        report_df = pd.DataFrame(report_data)
                        
                        # Display preview
                        st.dataframe(report_df)
                        
                        # Create download links
                        st.markdown("### Download Report")
                        filename = f"Employee_Assessment_{employee_info['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
                        
                        st.markdown(get_csv_download_link(report_df, f"{filename}.csv"), unsafe_allow_html=True)
                        st.markdown(get_excel_download_link(report_df, f"{filename}.xlsx"), unsafe_allow_html=True)
                        
                        # Show visualizations
                        st.subheader("Visualizations")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Radar chart for self assessment
                            if not self_assessments.empty:
                                fig, _ = employee_skill_radar(selected_emp_id, "self")
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Radar chart for manager assessment
                            if not manager_assessments.empty:
                                fig, _ = employee_skill_radar(selected_emp_id, "manager")
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                        
                        # Comparison radar chart
                        fig, _ = comparison_radar_chart(selected_emp_id, employee_info["job_level"], "manager" if not manager_assessments.empty else "self")
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No assessment data available for reporting.")
                
                elif report_type == "Competency Breakdown":
                    # Create competency breakdown report
                    st.subheader(f"Competency Breakdown: {employee_info['name']}")
                    
                    # Prepare data
                    all_assessments = pd.concat([self_assessments, manager_assessments])
                    
                    if not all_assessments.empty:
                        # Group by competency and assessment type
                        competency_data = []
                        
                        for comp in all_assessments["competency"].unique():
                            comp_assessments = all_assessments[all_assessments["competency"] == comp]
                            
                            for assessment_type in ["self", "manager"]:
                                type_assessments = comp_assessments[comp_assessments["assessment_type"] == assessment_type]
                                
                                if not type_assessments.empty:
                                    mean_score = type_assessments["score"].mean()
                                    
                                    competency_data.append({
                                        "Competency": comp,
                                        "Assessment Type": assessment_type.capitalize(),
                                        "Mean Score": round(mean_score, 2),
                                        "Number of Skills": len(type_assessments["skill"].unique()),
                                        "Latest Assessment": pd.to_datetime(type_assessments["assessment_date"]).max().strftime("%Y-%m-%d")
                                    })
                        
                        if competency_data:
                            # Convert to DataFrame
                            competency_df = pd.DataFrame(competency_data)
                            
                            # Display preview
                            st.dataframe(competency_df)
                            
                            # Create download links
                            st.markdown("### Download Report")
                            filename = f"Competency_Breakdown_{employee_info['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
                            
                            st.markdown(get_csv_download_link(competency_df, f"{filename}.csv"), unsafe_allow_html=True)
                            st.markdown(get_excel_download_link(competency_df, f"{filename}.xlsx"), unsafe_allow_html=True)
                            
                            # Show visualization
                            st.subheader("Visualization")
                            
                            # Create bar chart of competency scores
                            fig = px.bar(
                                competency_df,
                                x="Competency",
                                y="Mean Score",
                                color="Assessment Type",
                                barmode="group",
                                title="Competency Mean Scores",
                                labels={"Competency": "Competency", "Mean Score": "Mean Score", "Assessment Type": "Assessment Type"}
                            )
                            fig.update_layout(yaxis_range=[0, 5])
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No competency data available for reporting.")
                    else:
                        st.info("No assessment data available for reporting.")
                
                elif report_type == "Skills Gap Analysis":
                    # Create skills gap analysis report
                    st.subheader(f"Skills Gap Analysis: {employee_info['name']}")
                    
                    # Get expected scores
                    expectations_df = load_data("expectations")
                    
                    if expectations_df.empty:
                        st.warning("No skill expectations defined in the system.")
                    else:
                        # Filter expectations for this employee's job level
                        level_expectations = expectations_df[expectations_df["job_level"] == employee_info["job_level"]]
                        
                        if level_expectations.empty:
                            st.warning(f"No skill expectations defined for job level: {employee_info['job_level']}")
                        else:
                            # Prepare gap analysis data
                            gap_data = []
                            
                            # Prefer manager assessments if available, otherwise use self
                            assessment_type = "manager" if not manager_assessments.empty else "self"
                            assessments = manager_assessments if assessment_type == "manager" else self_assessments
                            
                            if not assessments.empty:
                                for _, assessment in assessments.iterrows():
                                    competency = assessment["competency"]
                                    skill = assessment["skill"]
                                    score = float(assessment["score"])
                                    
                                    # Find matching expectation
                                    expected_row = level_expectations[
                                        (level_expectations["competency"] == competency) &
                                        (level_expectations["skill"] == skill)
                                    ]
                                    
                                    if not expected_row.empty:
                                        expected_score = float(expected_row.iloc[0]["expected_score"])
                                        gap = score - expected_score
                                        
                                        gap_data.append({
                                            "Competency": competency,
                                            "Skill": skill,
                                            "Current Score": score,
                                            "Expected Score": expected_score,
                                            "Gap": round(gap, 2),
                                            "Assessment Type": assessment_type.capitalize(),
                                            "Assessment Date": pd.to_datetime(assessment["assessment_date"]).strftime("%Y-%m-%d")
                                        })
                                
                                if gap_data:
                                    # Convert to DataFrame
                                    gap_df = pd.DataFrame(gap_data)
                                    
                                    # Sort by gap (ascending to show biggest gaps first)
                                    gap_df = gap_df.sort_values("Gap")
                                    
                                    # Display preview
                                    st.dataframe(gap_df)
                                    
                                    # Create download links
                                    st.markdown("### Download Report")
                                    filename = f"Skills_Gap_Analysis_{employee_info['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
                                    
                                    st.markdown(get_csv_download_link(gap_df, f"{filename}.csv"), unsafe_allow_html=True)
                                    st.markdown(get_excel_download_link(gap_df, f"{filename}.xlsx"), unsafe_allow_html=True)
                                    
                                    # Show visualization
                                    st.subheader("Visualization")
                                    
                                    # Create bar chart of skill gaps
                                    fig = px.bar(
                                        gap_df,
                                        x="Skill",
                                        y="Gap",
                                        color="Competency",
                                        hover_data=["Current Score", "Expected Score"],
                                        title="Skill Gaps Analysis",
                                        labels={"Skill": "Skill", "Gap": "Gap (Current - Expected)", "Competency": "Competency"}
                                    )
                                    
                                    # Add zero line
                                    fig.add_shape(
                                        type="line",
                                        x0=-0.5,
                                        x1=len(gap_df)-0.5,
                                        y0=0,
                                        y1=0,
                                        line=dict(color="black", width=1, dash="dash")
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.info("No matching skill expectations found for this employee's assessments.")
                            else:
                                st.info("No assessment data available for gap analysis.")
        else:
            st.info("You don't have access to any employee records.")

# Team Reports Tab
with tab2:
    st.header("Team Performance Reports")
    
    # Get department or team data
    employees_df = load_data("employees")
    assessments_df = load_data("assessments")
    
    if employees_df.empty or assessments_df.empty:
        st.warning("Employee or assessment data not available.")
    else:
        # Filter based on user role
        if st.session_state.user_role == "admin":
            # Admins can select department or manager
            filter_type = st.radio("Filter by", ["Department", "Manager"], horizontal=True)
            
            if filter_type == "Department":
                departments = sorted(employees_df["department"].unique())
                selected_filter = st.selectbox("Select Department", departments, key="team_report_dept_select")
                
                # Filter employees by department
                team_members = employees_df[employees_df["department"] == selected_filter]
                team_name = f"Department: {selected_filter}"
            else:
                # Get all managers
                managers_df = employees_df[employees_df["employee_id"].isin(employees_df["manager_id"].dropna().unique())]
                
                if not managers_df.empty:
                    manager_options = [(row["employee_id"], row["name"]) for _, row in managers_df.iterrows()]
                    manager_names = [m[1] for m in manager_options]
                    manager_ids = [m[0] for m in manager_options]
                    
                    selected_manager = st.selectbox("Select Manager", manager_names, key="team_report_manager_select")
                    selected_manager_idx = manager_names.index(selected_manager)
                    selected_manager_id = manager_ids[selected_manager_idx]
                    
                    # Filter employees by manager
                    team_members = employees_df[employees_df["manager_id"] == selected_manager_id]
                    team_name = f"Team: {selected_manager}"
                else:
                    st.warning("No managers found in the system.")
                    team_members = pd.DataFrame()
                    team_name = ""
        else:
            # Managers see their own team
            manager_id = get_user_id(st.session_state.username)
            if manager_id is None:
                st.warning("Your user account is not linked to an employee record.")
                team_members = pd.DataFrame()
                team_name = ""
            else:
                # Get manager name
                manager_name = employees_df[employees_df["employee_id"] == manager_id]["name"].iloc[0]
                
                # Get team members
                team_members = employees_df[employees_df["manager_id"] == manager_id]
                team_name = f"Team: {manager_name}"
        
        if not team_members.empty:
            # Get team member IDs
            team_ids = team_members["employee_id"].tolist()
            
            # Get team assessments
            team_assessments = assessments_df[assessments_df["employee_id"].isin(team_ids)]
            
            if team_assessments.empty:
                st.warning("No assessment data available for this team.")
            else:
                # Allow selecting report type
                report_type = st.selectbox(
                    "Report Type",
                    ["Team Competency Summary", "Skill Distribution", "Individual Comparison"],
                    key="team_report_type"
                )
                
                # Filter by assessment type
                assessment_type = st.radio(
                    "Assessment Type",
                    ["self", "manager", "both"],
                    horizontal=True,
                    format_func=lambda x: "Self Assessment" if x == "self" else "Manager Assessment" if x == "manager" else "Combined"
                )
                
                if assessment_type != "both":
                    filtered_assessments = team_assessments[team_assessments["assessment_type"] == assessment_type]
                else:
                    filtered_assessments = team_assessments
                
                if report_type == "Team Competency Summary":
                    # Create team competency summary report
                    st.subheader(f"Team Competency Summary: {team_name}")
                    
                    if not filtered_assessments.empty:
                        # Group by competency
                        competency_data = []
                        
                        for comp in filtered_assessments["competency"].unique():
                            comp_assessments = filtered_assessments[filtered_assessments["competency"] == comp]
                            
                            mean_score = comp_assessments["score"].mean()
                            min_score = comp_assessments["score"].min()
                            max_score = comp_assessments["score"].max()
                            
                            competency_data.append({
                                "Competency": comp,
                                "Mean Score": round(mean_score, 2),
                                "Min Score": min_score,
                                "Max Score": max_score,
                                "Range": round(max_score - min_score, 2),
                                "Number of Assessments": len(comp_assessments),
                                "Number of Skills": len(comp_assessments["skill"].unique()),
                                "Number of Employees": len(comp_assessments["employee_id"].unique())
                            })
                        
                        if competency_data:
                            # Convert to DataFrame
                            comp_df = pd.DataFrame(competency_data)
                            
                            # Display preview
                            st.dataframe(comp_df)
                            
                            # Create download links
                            st.markdown("### Download Report")
                            filename = f"Team_Competency_Summary_{datetime.now().strftime('%Y%m%d')}"
                            
                            st.markdown(get_csv_download_link(comp_df, f"{filename}.csv"), unsafe_allow_html=True)
                            st.markdown(get_excel_download_link(comp_df, f"{filename}.xlsx"), unsafe_allow_html=True)
                            
                            # Show visualization
                            st.subheader("Visualization")
                            
                            # Team radar chart
                            fig, _ = team_competency_radar(filtered_assessments, f"Team Competency Summary ({assessment_type.capitalize()})")
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                                
                            # Bar chart with error bars
                            fig = go.Figure()
                            
                            fig.add_trace(go.Bar(
                                x=comp_df["Competency"],
                                y=comp_df["Mean Score"],
                                error_y=dict(
                                    type='data',
                                    array=[(max - mean) for max, mean in zip(comp_df["Max Score"], comp_df["Mean Score"])],
                                    arrayminus=[(mean - min) for min, mean in zip(comp_df["Min Score"], comp_df["Mean Score"])],
                                    visible=True
                                ),
                                name='Mean Score'
                            ))
                            
                            fig.update_layout(
                                title="Team Competency Scores with Range",
                                xaxis_title="Competency",
                                yaxis_title="Score",
                                yaxis=dict(range=[0, 5])
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No competency data available for reporting.")
                    else:
                        st.info("No assessment data available after filtering.")
                
                elif report_type == "Skill Distribution":
                    # Create skill distribution report
                    st.subheader(f"Skill Distribution: {team_name}")
                    
                    if not filtered_assessments.empty:
                        # Allow selecting competency
                        competencies = sorted(filtered_assessments["competency"].unique())
                        selected_comp = st.selectbox("Select Competency", competencies, key="export_comp_select")
                        
                        # Filter by competency
                        comp_assessments = filtered_assessments[filtered_assessments["competency"] == selected_comp]
                        
                        if not comp_assessments.empty:
                            # Group by skill
                            skill_data = []
                            
                            for skill in comp_assessments["skill"].unique():
                                skill_assessments = comp_assessments[comp_assessments["skill"] == skill]
                                
                                # Calculate distribution of scores
                                scores = skill_assessments["score"].tolist()
                                
                                # Count scores in each band
                                score_counts = {
                                    "1.0-1.5": len([s for s in scores if 1.0 <= float(s) <= 1.5]),
                                    "2.0-2.5": len([s for s in scores if 2.0 <= float(s) <= 2.5]),
                                    "3.0-3.5": len([s for s in scores if 3.0 <= float(s) <= 3.5]),
                                    "4.0-4.5": len([s for s in scores if 4.0 <= float(s) <= 4.5]),
                                    "5.0": len([s for s in scores if float(s) == 5.0])
                                }
                                
                                skill_data.append({
                                    "Skill": skill,
                                    "Mean Score": round(skill_assessments["score"].mean(), 2),
                                    "Number of Employees": len(skill_assessments["employee_id"].unique()),
                                    "Score 1.0-1.5": score_counts["1.0-1.5"],
                                    "Score 2.0-2.5": score_counts["2.0-2.5"],
                                    "Score 3.0-3.5": score_counts["3.0-3.5"],
                                    "Score 4.0-4.5": score_counts["4.0-4.5"],
                                    "Score 5.0": score_counts["5.0"]
                                })
                            
                            if skill_data:
                                # Convert to DataFrame
                                skill_df = pd.DataFrame(skill_data)
                                
                                # Display preview
                                st.dataframe(skill_df)
                                
                                # Create download links
                                st.markdown("### Download Report")
                                filename = f"Skill_Distribution_{selected_comp.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
                                
                                st.markdown(get_csv_download_link(skill_df, f"{filename}.csv"), unsafe_allow_html=True)
                                st.markdown(get_excel_download_link(skill_df, f"{filename}.xlsx"), unsafe_allow_html=True)
                                
                                # Show visualization
                                st.subheader("Visualization")
                                
                                # Stacked bar chart of skill distribution
                                fig = go.Figure()
                                
                                # Add traces for each score band
                                bands = ["Score 1.0-1.5", "Score 2.0-2.5", "Score 3.0-3.5", "Score 4.0-4.5", "Score 5.0"]
                                colors = ["#ff9999", "#ffcc99", "#ffff99", "#99ff99", "#99ccff"]
                                
                                for i, band in enumerate(bands):
                                    fig.add_trace(go.Bar(
                                        x=skill_df["Skill"],
                                        y=skill_df[band],
                                        name=band.replace("Score ", ""),
                                        marker_color=colors[i],
                                    ))
                                
                                # Set layout
                                fig.update_layout(
                                    title=f"Skill Score Distribution for {selected_comp}",
                                    xaxis_title="Skill",
                                    yaxis_title="Number of Employees",
                                    barmode='stack'
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No skill data available for reporting.")
                        else:
                            st.info(f"No assessment data available for {selected_comp}.")
                    else:
                        st.info("No assessment data available after filtering.")
                
                elif report_type == "Individual Comparison":
                    # Create individual comparison report
                    st.subheader(f"Individual Comparison: {team_name}")
                    
                    if not filtered_assessments.empty:
                        # Calculate means for each employee and competency
                        comparison_data = []
                        
                        for emp_id in team_ids:
                            emp_name = team_members[team_members["employee_id"] == emp_id]["name"].iloc[0]
                            emp_assessments = filtered_assessments[filtered_assessments["employee_id"] == emp_id]
                            
                            if not emp_assessments.empty:
                                # Calculate overall mean
                                overall_mean = emp_assessments["score"].mean()
                                
                                # Calculate means by competency
                                comp_means = {}
                                for comp in emp_assessments["competency"].unique():
                                    comp_assessments = emp_assessments[emp_assessments["competency"] == comp]
                                    comp_means[comp] = comp_assessments["score"].mean()
                                
                                # Create record
                                record = {
                                    "Employee Name": emp_name,
                                    "Employee ID": emp_id,
                                    "Overall Mean": round(overall_mean, 2)
                                }
                                
                                # Add competency means
                                for comp in filtered_assessments["competency"].unique():
                                    record[f"{comp} Mean"] = round(comp_means.get(comp, 0), 2)
                                
                                comparison_data.append(record)
                        
                        if comparison_data:
                            # Convert to DataFrame
                            comparison_df = pd.DataFrame(comparison_data)
                            
                            # Calculate team averages
                            team_avgs = {"Employee Name": "TEAM AVERAGE", "Employee ID": None, "Overall Mean": round(filtered_assessments["score"].mean(), 2)}
                            
                            for comp in filtered_assessments["competency"].unique():
                                comp_assessments = filtered_assessments[filtered_assessments["competency"] == comp]
                                team_avgs[f"{comp} Mean"] = round(comp_assessments["score"].mean(), 2)
                            
                            # Add team averages to DataFrame
                            comparison_df = pd.concat([comparison_df, pd.DataFrame([team_avgs])], ignore_index=True)
                            
                            # Sort by overall mean
                            comparison_df = comparison_df.sort_values("Overall Mean", ascending=False)
                            
                            # Display preview
                            st.dataframe(comparison_df)
                            
                            # Create download links
                            st.markdown("### Download Report")
                            filename = f"Team_Individual_Comparison_{datetime.now().strftime('%Y%m%d')}"
                            
                            st.markdown(get_csv_download_link(comparison_df, f"{filename}.csv"), unsafe_allow_html=True)
                            st.markdown(get_excel_download_link(comparison_df, f"{filename}.xlsx"), unsafe_allow_html=True)
                            
                            # Show visualization
                            st.subheader("Visualization")
                            
                            # Allow selecting which employees to visualize
                            employee_options = [e for e in comparison_df["Employee Name"].tolist() if e != "TEAM AVERAGE"]
                            selected_employees = st.multiselect("Select Employees to Compare", employee_options, default=employee_options[:5] if len(employee_options) > 5 else employee_options)
                            
                            # Get competency names
                            comp_cols = [c for c in comparison_df.columns if c.endswith(" Mean") and c != "Overall Mean"]
                            comp_names = [c.replace(" Mean", "") for c in comp_cols]
                            
                            if selected_employees:
                                # Filter data for selected employees and add team average
                                viz_data = comparison_df[comparison_df["Employee Name"].isin(selected_employees + ["TEAM AVERAGE"])]
                                
                                # Create bar chart for overall means
                                fig = px.bar(
                                    viz_data,
                                    x="Employee Name",
                                    y="Overall Mean",
                                    title="Overall Skill Mean by Employee",
                                    labels={"Employee Name": "Employee", "Overall Mean": "Overall Mean Score"},
                                    color="Employee Name"
                                )
                                
                                # Set y-axis range
                                fig.update_layout(yaxis=dict(range=[0, 5]))
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Create radar chart comparing employees
                                fig = go.Figure()
                                
                                for _, row in viz_data.iterrows():
                                    employee = row["Employee Name"]
                                    values = [row[f"{comp} Mean"] for comp in comp_names]
                                    
                                    fig.add_trace(go.Scatterpolar(
                                        r=values,
                                        theta=comp_names,
                                        fill='toself',
                                        name=employee
                                    ))
                                
                                fig.update_layout(
                                    polar=dict(
                                        radialaxis=dict(
                                            visible=True,
                                            range=[0, 5]
                                        )
                                    ),
                                    title="Competency Comparison by Employee"
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Please select at least one employee to visualize.")
                        else:
                            st.info("No comparison data available for reporting.")
                    else:
                        st.info("No assessment data available after filtering.")
        else:
            st.info("No team members found with the current filter.")

# Framework Reports Tab
with tab3:
    st.header("Framework Reports")
    
    # Only admins can access framework reports
    if st.session_state.user_role != "admin":
        st.info("Only administrators can access framework reports.")
    else:
        # Load framework data
        competencies_df = load_data("competencies")
        skills_df = load_data("skills")
        expectations_df = load_data("expectations")
        
        if competencies_df.empty or skills_df.empty:
            st.warning("Competency framework not fully set up.")
        else:
            # Select report type
            report_type = st.selectbox(
                "Report Type",
                ["Competency Framework Overview", "Skill Expectations by Level"]
            )
            
            if report_type == "Competency Framework Overview":
                # Create framework overview report
                st.subheader("Competency Framework Overview")
                
                # Prepare data
                framework_data = []
                
                for _, comp_row in competencies_df.iterrows():
                    comp_id = comp_row["competency_id"]
                    comp_name = comp_row["name"]
                    comp_desc = comp_row["description"]
                    
                    # Count skills for this competency
                    comp_skills = skills_df[skills_df["competency_id"] == comp_id]
                    skill_count = len(comp_skills)
                    
                    # Create record
                    framework_data.append({
                        "Competency ID": comp_id,
                        "Competency Name": comp_name,
                        "Description": comp_desc,
                        "Number of Skills": skill_count,
                        "Skills": ", ".join(comp_skills["name"].tolist()) if not comp_skills.empty else ""
                    })
                
                if framework_data:
                    # Convert to DataFrame
                    framework_df = pd.DataFrame(framework_data)
                    
                    # Display preview
                    st.dataframe(framework_df)
                    
                    # Create download links
                    st.markdown("### Download Report")
                    filename = f"Competency_Framework_Overview_{datetime.now().strftime('%Y%m%d')}"
                    
                    st.markdown(get_csv_download_link(framework_df, f"{filename}.csv"), unsafe_allow_html=True)
                    st.markdown(get_excel_download_link(framework_df, f"{filename}.xlsx"), unsafe_allow_html=True)
                    
                    # Show visualization
                    st.subheader("Visualization")
                    
                    # Bar chart of skills per competency
                    fig = px.bar(
                        framework_df,
                        x="Competency Name",
                        y="Number of Skills",
                        title="Number of Skills per Competency",
                        labels={"Competency Name": "Competency", "Number of Skills": "Number of Skills"}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No framework data available for reporting.")
            
            elif report_type == "Skill Expectations by Level":
                # Create skill expectations report
                st.subheader("Skill Expectations by Level")
                
                if expectations_df.empty:
                    st.warning("No skill expectations defined in the system.")
                else:
                    # Get available job levels
                    job_levels = sorted(expectations_df["job_level"].unique())
                    
                    # Allow selecting job level
                    selected_level = st.selectbox("Select Job Level", job_levels)
                    
                    # Filter expectations by level
                    level_expectations = expectations_df[expectations_df["job_level"] == selected_level]
                    
                    if not level_expectations.empty:
                        # Prepare data in a more usable format
                        expectations_data = []
                        
                        for _, exp_row in level_expectations.iterrows():
                            competency = exp_row["competency"]
                            skill = exp_row["skill"]
                            expected_score = exp_row["expected_score"]
                            
                            # Find skill ID
                            skill_info = skills_df[skills_df["name"] == skill]
                            skill_id = skill_info["skill_id"].iloc[0] if not skill_info.empty else None
                            
                            # Find competency ID
                            comp_info = competencies_df[competencies_df["name"] == competency]
                            comp_id = comp_info["competency_id"].iloc[0] if not comp_info.empty else None
                            
                            expectations_data.append({
                                "Competency ID": comp_id,
                                "Competency": competency,
                                "Skill ID": skill_id,
                                "Skill": skill,
                                "Expected Score": expected_score
                            })
                        
                        if expectations_data:
                            # Convert to DataFrame
                            expectations_df_report = pd.DataFrame(expectations_data)
                            
                            # Display preview
                            st.dataframe(expectations_df_report)
                            
                            # Create download links
                            st.markdown("### Download Report")
                            filename = f"Skill_Expectations_{selected_level.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
                            
                            st.markdown(get_csv_download_link(expectations_df_report, f"{filename}.csv"), unsafe_allow_html=True)
                            st.markdown(get_excel_download_link(expectations_df_report, f"{filename}.xlsx"), unsafe_allow_html=True)
                            
                            # Show visualization
                            st.subheader("Visualization")
                            
                            # Group by competency for visualization
                            comp_avg = expectations_df_report.groupby("Competency")["Expected Score"].mean().reset_index()
                            
                            # Bar chart of average expected scores by competency
                            fig = px.bar(
                                comp_avg,
                                x="Competency",
                                y="Expected Score",
                                title=f"Average Expected Scores by Competency for {selected_level}",
                                labels={"Competency": "Competency", "Expected Score": "Average Expected Score"}
                            )
                            
                            # Set y-axis range
                            fig.update_layout(yaxis=dict(range=[0, 5]))
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Heatmap of expected scores
                            # Pivot data for heatmap
                            pivot_df = expectations_df_report.pivot_table(
                                index="Competency",
                                columns="Skill",
                                values="Expected Score"
                            )
                            
                            # Create heatmap
                            fig = px.imshow(
                                pivot_df,
                                labels=dict(x="Skill", y="Competency", color="Expected Score"),
                                x=pivot_df.columns,
                                y=pivot_df.index,
                                color_continuous_scale="Viridis",
                                title=f"Expected Skill Scores for {selected_level}"
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No expectations data available for reporting.")
                    else:
                        st.info(f"No expectations defined for level {selected_level}.")

# Add explanatory text at the bottom
st.markdown("---")
st.markdown("""
### Report Export Guide

These reports allow you to analyze and export various aspects of the skill matrix:

**Individual Reports:**
- Full Assessment Report: Complete assessment details for an individual
- Competency Breakdown: Summary of competency scores with means
- Skills Gap Analysis: Compare current skills against expected levels

**Team Reports:**
- Team Competency Summary: Overview of competency scores across the team
- Skill Distribution: Analyze the distribution of skill scores within the team
- Individual Comparison: Compare team members side by side

**Framework Reports:**
- Competency Framework Overview: Summary of the competency framework structure
- Skill Expectations by Level: Expected skill scores for different job levels

Reports can be downloaded in CSV or Excel format for further analysis or sharing.
""")
