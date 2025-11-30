import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import data_manager
import analytics
import styles

# --- Page Config ---
st.set_page_config(
    page_title="Professional Recruitment Tracker", 
    page_icon="👥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
styles.apply_custom_css()

# --- Load Data ---
# Load data on first run (no cache to ensure fresh data from Google Sheets)
success, msg = data_manager.load_data()

if not success:
    st.error(f"⚠️ {msg}")
    st.stop()

# Get data from manager
df_candidates = data_manager.get_candidates()
df_jobs = data_manager.get_jobs()
preferences = data_manager.get_preferences()

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("# 👥 Recruitment Tracker")
    st.markdown("### Professional HR Management")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "💼 Job Openings", "👤 Candidates", "📊 Analytics", 
         "➕ Add Candidate", "➕ Add Job Opening", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick Stats in Sidebar
    st.markdown("### Quick Stats")
    total_candidates = len(df_candidates)
    open_positions = len(df_jobs[df_jobs["STATUS"].astype(str).str.upper() == "VACANT"]) if not df_jobs.empty else 0
    st.metric("Total Candidates", total_candidates)
    st.metric("Open Positions", open_positions)
    
    st.markdown("---")
    
    st.caption("v2.0 - Professional Edition")

# =============================================================================
# DASHBOARD PAGE
# =============================================================================
if page == "🏠 Dashboard":
    styles.render_page_header("Dashboard", "Overview of recruitment activities and key metrics")
    
    if df_candidates.empty and df_jobs.empty:
        st.warning("No data available. Start by adding job openings and candidates.")
    else:
        # --- Top KPI Cards ---
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_candidates = len(df_candidates)
            styles.render_kpi_card("Total Candidates", total_candidates, "👥", styles.GRADIENT_BLUE)
        
        with col2:
            open_positions = len(df_jobs[df_jobs["STATUS"].astype(str).str.upper() == "VACANT"]) if not df_jobs.empty else 0
            styles.render_kpi_card("Open Positions", open_positions, "💼", styles.GRADIENT_GREEN)
        
        with col3:
            hired_count = len(df_candidates[df_candidates["STATUS"].astype(str).str.upper() == "HIRED"])
            styles.render_kpi_card("Hired", hired_count, "✅", styles.GRADIENT_PURPLE)
        
        with col4:
            time_to_hire_data = analytics.calculate_time_to_hire(df_candidates)
            avg_days = time_to_hire_data["average_days"]
            styles.render_kpi_card("Avg Time-to-Hire", f"{avg_days} days", "⏱️", styles.GRADIENT_ORANGE)
        
        with col5:
            cost_data = analytics.calculate_cost_per_hire(df_jobs, df_candidates)
            avg_cost = cost_data["average_cost"]
            styles.render_kpi_card("Avg Cost/Hire", f"${avg_cost:,.0f}", "💰", styles.GRADIENT_RED)
        
        st.markdown("---")
        
        # --- Job Openings Overview ---
        if not df_jobs.empty:
            styles.render_section_header("Job Openings Overview", "💼")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Job openings table with key info
                display_jobs = df_jobs[["JOB ID", "JOB TITLE", "DEPARTMENT", "RECRUITER", "STATUS", "OPENING DATE"]].copy()
                display_jobs = display_jobs.sort_values("OPENING DATE", ascending=False).head(10)
                st.dataframe(display_jobs, width="stretch", hide_index=True)
            
            with col2:
                # Job status distribution
                if "STATUS" in df_jobs.columns:
                    status_counts = df_jobs["STATUS"].value_counts()
                    fig_job_status = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Job Status Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_job_status.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_job_status, width="stretch")
        
        st.markdown("---")
        
        # --- Recruitment Funnel ---
        styles.render_section_header("Recruitment Funnel", "📊")
        
        funnel_data = analytics.get_funnel_data(df_candidates)
        if not funnel_data.empty:
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_data["Stage"],
                x=funnel_data["Count"],
                textinfo="value+percent initial",
                marker={"color": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#11998e", "#38ef7d"]}
            ))
            fig_funnel.update_layout(title="Candidate Pipeline Funnel", height=400)
            st.plotly_chart(fig_funnel, width="stretch")
        
        st.markdown("---")
        
        # --- Charts Row 1 ---
        col1, col2 = st.columns(2)
        
        with col1:
            styles.render_section_header("Candidates by Status", "📈")
            if "STATUS" in df_candidates.columns and not df_candidates.empty:
                status_counts = df_candidates["STATUS"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]
                fig_status = px.bar(
                    status_counts, 
                    x="Status", 
                    y="Count", 
                    color="Status",
                    title="Distribution by Status",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_status.update_layout(showlegend=False)
                st.plotly_chart(fig_status, width="stretch")
        
        with col2:
            styles.render_section_header("Candidates by Department", "🏢")
            if "DEPARTMENT" in df_candidates.columns and not df_candidates.empty:
                dept_counts = df_candidates["DEPARTMENT"].value_counts().reset_index()
                dept_counts.columns = ["Department", "Count"]
                fig_dept = px.pie(
                    dept_counts,
                    values="Count",
                    names="Department",
                    title="Distribution by Department",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_dept, width="stretch")
        
        st.markdown("---")
        
        # --- Charts Row 2 ---
        col1, col2 = st.columns(2)
        
        with col1:
            styles.render_section_header("Hiring Trend", "📅")
            trends = analytics.calculate_trends(df_candidates, period='M')
            if not trends.empty:
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=trends["Period"], 
                    y=trends["Applications"],
                    mode='lines+markers',
                    name='Applications',
                    line=dict(color='#667eea', width=3)
                ))
                fig_trend.add_trace(go.Scatter(
                    x=trends["Period"], 
                    y=trends["Hired"],
                    mode='lines+markers',
                    name='Hired',
                    line=dict(color='#38ef7d', width=3)
                ))
                fig_trend.update_layout(
                    title="Applications & Hires Over Time",
                    xaxis_title="Period",
                    yaxis_title="Count",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_trend, width="stretch")
        
        with col2:
            styles.render_section_header("Recruiter Performance", "👨‍💼")
            recruiter_metrics = analytics.get_recruiter_metrics(df_candidates, df_jobs)
            if not recruiter_metrics.empty:
                fig_rec = px.bar(
                    recruiter_metrics,
                    x="Recruiter",
                    y=["Total Candidates", "Hired", "In Process"],
                    title="Recruiter Workload & Performance",
                    barmode='group',
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig_rec, width="stretch")
        
        st.markdown("---")
        
        # --- Source Effectiveness ---
        styles.render_section_header("Source Effectiveness", "🎯")
        source_metrics = analytics.get_source_metrics(df_candidates)
        if not source_metrics.empty:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.dataframe(source_metrics, width="stretch", hide_index=True)
            with col2:
                fig_source = px.bar(
                    source_metrics,
                    x="Source",
                    y="Hire Rate %",
                    title="Hire Rate by Source",
                    color="Hire Rate %",
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig_source, width="stretch")

# =============================================================================
# JOB OPENINGS PAGE
# =============================================================================
elif page == "💼 Job Openings":
    styles.render_page_header("Job Openings", "Manage all open and closed positions")
    
    if df_jobs.empty:
        st.info("No job openings found. Add your first position below!")
    else:
        # Summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        vacant = len(df_jobs[df_jobs["STATUS"].astype(str).str.upper() == "VACANT"])
        filled = len(df_jobs[df_jobs["STATUS"].astype(str).str.upper() == "FILLED"])
        suspended = len(df_jobs[df_jobs["STATUS"].astype(str).str.upper() == "SUSPENDED"])
        cancelled = len(df_jobs[df_jobs["STATUS"].astype(str).str.upper() == "CANCELLED"])
        
        with col1:
            st.metric("Vacant", vacant, delta=None)
        with col2:
            st.metric("Filled", filled, delta=None)
        with col3:
            st.metric("Suspended", suspended, delta=None)
        with col4:
            st.metric("Cancelled", cancelled, delta=None)
        
        st.markdown("---")
        
        # Filters
        with st.expander("🔍 Filters", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                dept_filter = st.multiselect("Department", options=preferences.get("Departments", []))
            with col2:
                recruiter_filter = st.multiselect("Recruiter", options=preferences.get("Recruiters", []))
            with col3:
                status_filter = st.multiselect("Status", options=preferences.get("Job Statuses", []))
        
        # Apply filters
        df_filtered = df_jobs.copy()
        if dept_filter:
            df_filtered = df_filtered[df_filtered["DEPARTMENT"].isin(dept_filter)]
        if recruiter_filter:
            df_filtered = df_filtered[df_filtered["RECRUITER"].isin(recruiter_filter)]
        if status_filter:
            df_filtered = df_filtered[df_filtered["STATUS"].isin(status_filter)]
        
        # Display table
        st.dataframe(df_filtered, width="stretch", hide_index=True)
        
        # Cost summary
        if "HIRING COST" in df_filtered.columns:
            total_cost = df_filtered["HIRING COST"].sum()
            st.markdown(f"**Total Hiring Cost:** ${total_cost:,.2f}")

# =============================================================================
# CANDIDATES PAGE
# =============================================================================
elif page == "👤 Candidates":
    styles.render_page_header("Candidates Database", "View and manage all candidates")
    
    if df_candidates.empty:
        st.warning("No candidates found.")
    else:
        # Advanced Filters
        with st.expander("🔍 Advanced Filters", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                status_filter = st.multiselect("Status", options=preferences.get("Status", []))
            with col2:
                recruiter_filter = st.multiselect("Recruiter", options=preferences.get("Recruiters", []))
            with col3:
                dept_filter = st.multiselect("Department", options=preferences.get("Departments", []))
            with col4:
                source_filter = st.multiselect("Source", options=preferences.get("Sources", []))
            
            # Search
            search_term = st.text_input("🔎 Search (Name, Email, Phone)", "")
        
        # Apply filters
        df_filtered = df_candidates.copy()
        if status_filter:
            df_filtered = df_filtered[df_filtered["STATUS"].isin(status_filter)]
        if recruiter_filter:
            df_filtered = df_filtered[df_filtered["RECRUITER"].isin(recruiter_filter)]
        if dept_filter and "DEPARTMENT" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["DEPARTMENT"].isin(dept_filter)]
        if source_filter:
            df_filtered = df_filtered[df_filtered["SOURCE"].isin(source_filter)]
        
        # Search filter
        if search_term:
            search_term = search_term.lower()
            df_filtered = df_filtered[
                df_filtered["CANDIDATE NAME"].astype(str).str.lower().str.contains(search_term) |
                df_filtered["EMAIL"].astype(str).str.lower().str.contains(search_term) |
                df_filtered["PHONE"].astype(str).str.lower().str.contains(search_term)
            ]
        
        st.markdown(f"**Showing {len(df_filtered)} of {len(df_candidates)} candidates**")
        
        # Display table
        st.dataframe(df_filtered, width="stretch", hide_index=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"candidates_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# =============================================================================
# ANALYTICS PAGE
# =============================================================================
elif page == "📊 Analytics":
    styles.render_page_header("Analytics & Insights", "Deep dive into recruitment metrics")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    st.markdown("---")
    
    # Time-to-Hire Analysis
    styles.render_section_header("Time-to-Hire Analysis", "⏱️")
    time_to_hire = analytics.calculate_time_to_hire(df_candidates)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Time-to-Hire", f"{time_to_hire['average_days']} days")
    
    if time_to_hire["by_position"]:
        st.markdown("**By Position:**")
        for pos, days in time_to_hire["by_position"].items():
            st.write(f"- {pos}: {days} days")
    
    st.markdown("---")
    
    # Cost Analysis
    styles.render_section_header("Cost Analysis", "💰")
    cost_data = analytics.calculate_cost_per_hire(df_jobs, df_candidates)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Hiring Cost", f"${cost_data['total_cost']:,.2f}")
    with col2:
        st.metric("Total Hires", cost_data['total_hires'])
    with col3:
        st.metric("Average Cost per Hire", f"${cost_data['average_cost']:,.2f}")
    
    st.markdown("---")
    
    # Conversion Funnel
    styles.render_section_header("Conversion Funnel", "📊")
    conversions = analytics.get_conversion_rates(df_candidates)
    if conversions:
        st.write("**Conversion Rates:**")
        for stage, rate in conversions.items():
            st.write(f"- {stage}: {rate}%")
    
    st.markdown("---")
    
    # Department Metrics
    if not df_jobs.empty:
        styles.render_section_header("Department Metrics", "🏢")
        dept_metrics = analytics.get_department_metrics(df_candidates, df_jobs)
        if not dept_metrics.empty:
            st.dataframe(dept_metrics, width="stretch", hide_index=True)

# =============================================================================
# ADD CANDIDATE PAGE
# =============================================================================
elif page == "➕ Add Candidate":
    styles.render_page_header("Add New Candidate", "Enter candidate information")
    
    with st.form("new_candidate_form"):
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Candidate Name *", key="cand_name")
            email = st.text_input("Email", key="cand_email")
            phone = st.text_input("Phone", key="cand_phone")
        
        with col2:
            date = st.date_input("Application Date", key="cand_date")
            source = st.selectbox("Source", options=preferences.get("Sources", []), key="cand_source")
        
        st.markdown("### Position & Assignment")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Job selection
            job_options = df_jobs["JOB TITLE"].tolist() if not df_jobs.empty else []
            position = st.selectbox("Position", options=job_options, key="cand_position")
            
            # Auto-populate job ID and department based on position
            if position and not df_jobs.empty:
                selected_job = df_jobs[df_jobs["JOB TITLE"] == position].iloc[0]
                job_id = selected_job["JOB ID"]
                department = selected_job["DEPARTMENT"]
            else:
                job_id = None
                department = None
        
        with col2:
            recruiter = st.selectbox("Recruiter", options=preferences.get("Recruiters", []), key="cand_recruiter")
        
        with col3:
            status = st.selectbox("Status", options=preferences.get("Status", []), key="cand_status")
        
        st.markdown("### Decision & Feedback")
        col1, col2 = st.columns(2)
        
        with col1:
            final_decision = st.selectbox(
                "Final Decision", 
                options=["", "Hired", "Not Hired", "Candidate in Process", "Candidate Refusal"],
                key="cand_decision"
            )
        
        with col2:
            pass  # Placeholder for balance
        
        # Multi-stakeholder views
        st.markdown("### Stakeholder Views")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            hr_view = st.text_area("HR View", key="cand_hr_view")
        with col2:
            manager_view = st.text_area("Hiring Manager View", key="cand_manager_view")
        with col3:
            decision_maker_view = st.text_area("Decision Maker View", key="cand_dm_view")
        
        st.markdown("### Comments & Notes")
        received_app_comments = st.text_area("Received Application Comments", key="cand_rec_comments")
        notes = st.text_area("General Notes / Comments", key="cand_notes")
        
        submitted = st.form_submit_button("💾 Save Candidate", width="stretch")
        
        if submitted:
            if not name:
                st.error("Candidate name is required.")
            else:
                new_data = {
                    "CANDIDATE NAME": name,
                    "EMAIL": email,
                    "PHONE": phone,
                    "APPLICATION DATE": date,
                    "POSITION": position,
                    "JOB ID": job_id,
                    "DEPARTMENT": department,
                    "RECRUITER": recruiter,
                    "SOURCE": source,
                    "STATUS": status,
                    "FINAL DECISION": final_decision,
                    "HR VIEW": hr_view,
                    "HIRING MANAGER VIEW": manager_view,
                    "DECISION MAKER VIEW": decision_maker_view,
                    "RECEIVED APPLICATION COMMENTS": received_app_comments,
                    "NOTES": notes
                }
                
                success, msg = data_manager.save_candidate(new_data)
                if success:
                    st.success(msg)
                    st.cache_data.clear()
                    st.balloons()
                else:
                    st.error(msg)

# =============================================================================
# ADD JOB OPENING PAGE
# =============================================================================
elif page == "➕ Add Job Opening":
    styles.render_page_header("Add New Job Opening", "Create a new position")
    
    with st.form("new_job_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate next job ID
            if not df_jobs.empty:
                max_id = df_jobs["JOB ID"].max()
                next_id = int(float(max_id)) + 1 if pd.notna(max_id) else 1
            else:
                next_id = 1
            
            job_id = st.number_input("Job ID", value=next_id, min_value=1, key="job_id")
            job_title = st.text_input("Job Title *", key="job_title")
            department = st.selectbox("Department", options=preferences.get("Departments", []) + ["+ Add New"], key="job_dept")
            
            if department == "+ Add New":
                department = st.text_input("New Department Name", key="job_new_dept")
        
        with col2:
            recruiter = st.selectbox("Assigned Recruiter", options=preferences.get("Recruiters", []), key="job_recruiter")
            opening_date = st.date_input("Opening Date", key="job_opening_date")
            status = st.selectbox("Status", options=preferences.get("Job Statuses", []), key="job_status")
        
        col1, col2 = st.columns(2)
        with col1:
            target_start_date = st.date_input("Target Start Date (Optional)", value=None, key="job_start_date")
        with col2:
            hiring_cost = st.number_input("Hiring Cost Budget ($)", min_value=0.0, value=0.0, key="job_cost")
        
        submitted = st.form_submit_button("💾 Save Job Opening", width="stretch")
        
        if submitted:
            if not job_title:
                st.error("Job title is required.")
            else:
                new_job = {
                    "JOB ID": job_id,
                    "JOB TITLE": job_title,
                    "DEPARTMENT": department,
                    "RECRUITER": recruiter,
                    "OPENING DATE": opening_date,
                    "STATUS": status,
                    "NEW HIRE START DATE": target_start_date if target_start_date else None,
                    "HIRING COST": hiring_cost
                }
                
                success, msg = data_manager.save_job_opening(new_job)
                if success:
                    st.success(msg)
                    st.cache_data.clear()
                    st.balloons()
                else:
                    st.error(msg)

# =============================================================================
# SETTINGS PAGE
# =============================================================================
elif page == "⚙️ Settings":
    data_source = "Google Sheets" if data_manager.manager.use_google_sheets else "Excel (Local)"
    styles.render_page_header("Settings", "Manage preferences, data, and system configuration")
    
    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Recruiters", 
        "🏢 Departments", 
        "📍 Sources", 
        "📊 Pipeline Status",
        "🔧 System"
    ])
    
    # =========================================================================
    # TAB 1: RECRUITERS
    # =========================================================================
    with tab1:
        st.markdown("### Manage Recruiters")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Current Recruiters")
            recruiters = preferences.get("Recruiters", [])
            
            if recruiters:
                # Display as a nice table with stats
                recruiter_stats = []
                for rec in recruiters:
                    # Count candidates per recruiter
                    rec_candidates = len(df_candidates[df_candidates["RECRUITER"] == rec]) if not df_candidates.empty else 0
                    rec_jobs = len(df_jobs[df_jobs["RECRUITER"] == rec]) if not df_jobs.empty else 0
                    recruiter_stats.append({
                        "Recruiter": rec,
                        "Candidates": rec_candidates,
                        "Job Openings": rec_jobs
                    })
                
                df_rec_stats = pd.DataFrame(recruiter_stats)
                st.dataframe(df_rec_stats, width="stretch", hide_index=True)
            else:
                st.info("No recruiters found in preferences.")
        
        with col2:
            st.markdown("#### Quick Stats")
            st.metric("Total Recruiters", len(recruiters))
            if not df_candidates.empty:
                avg_candidates = len(df_candidates) / len(recruiters) if len(recruiters) > 0 else 0
                st.metric("Avg Candidates/Recruiter", f"{avg_candidates:.1f}")
        
        st.markdown("---")
        st.info(f"💡 **How to modify:** Edit the 'Preferences' sheet in the {data_source}, column C (starting row 8), then reload data.")
    
    # =========================================================================
    # TAB 2: DEPARTMENTS
    # =========================================================================
    with tab2:
        st.markdown("### Manage Departments")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Current Departments")
            departments = preferences.get("Departments", [])
            
            if departments:
                # Display with stats
                dept_stats = []
                for dept in departments:
                    dept_jobs = len(df_jobs[df_jobs["DEPARTMENT"] == dept]) if not df_jobs.empty else 0
                    dept_candidates = len(df_candidates[df_candidates["DEPARTMENT"] == dept]) if not df_candidates.empty else 0
                    open_positions = len(df_jobs[(df_jobs["DEPARTMENT"] == dept) & (df_jobs["STATUS"] == "Vacant")]) if not df_jobs.empty else 0
                    
                    dept_stats.append({
                        "Department": dept,
                        "Open Positions": open_positions,
                        "Total Jobs": dept_jobs,
                        "Candidates": dept_candidates
                    })
                
                df_dept_stats = pd.DataFrame(dept_stats)
                st.dataframe(df_dept_stats, width="stretch", hide_index=True)
            else:
                st.info("No departments found. Departments are auto-extracted from Job Openings.")
        
        with col2:
            st.markdown("#### Quick Stats")
            st.metric("Total Departments", len(departments))
            if not df_jobs.empty:
                vacant_positions = len(df_jobs[df_jobs["STATUS"] == "Vacant"])
                st.metric("Total Open Positions", vacant_positions)
        
        st.markdown("---")
        st.info("💡 **How to add:** Departments are automatically extracted from the 'JobOpenings' sheet. Add a new job opening with a new department name.")
    
    # =========================================================================
    # TAB 3: SOURCES
    # =========================================================================
    with tab3:
        st.markdown("### Manage Recruitment Sources")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Current Sources")
            sources = preferences.get("Sources", [])
            source_metrics = pd.DataFrame()  # Initialize empty
            
            if sources:
                # Display with effectiveness metrics
                source_metrics = analytics.get_source_metrics(df_candidates)
                if not source_metrics.empty:
                    st.dataframe(source_metrics, width="stretch", hide_index=True)
                else:
                    for source in sources:
                        st.write(f"- {source}")
            else:
                st.info("No sources found.")
        
        with col2:
            st.markdown("#### Quick Stats")
            st.metric("Total Sources", len(sources))
            if not source_metrics.empty:
                best_source = source_metrics.iloc[0]["Source"]
                st.metric("Best Source", best_source)
        
        st.markdown("---")
        st.info("💡 **How to add:** Sources are auto-extracted from candidate data. Add a candidate with a new source to include it.")
    
    # =========================================================================
    # TAB 4: PIPELINE STATUS
    # =========================================================================
    with tab4:
        st.markdown("### Manage Pipeline Statuses")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Current Pipeline Stages")
            statuses = preferences.get("Status", [])
            
            if statuses:
                # Display with candidate counts
                status_stats = []
                for status in statuses:
                    count = len(df_candidates[df_candidates["STATUS"] == status]) if not df_candidates.empty else 0
                    status_stats.append({
                        "Stage": status,
                        "Candidates": count,
                        "Percentage": f"{(count / len(df_candidates) * 100):.1f}%" if not df_candidates.empty and len(df_candidates) > 0 else "0%"
                    })
                
                df_status_stats = pd.DataFrame(status_stats)
                st.dataframe(df_status_stats, width="stretch", hide_index=True)
                
                # Visualize pipeline
                st.markdown("#### Pipeline Visualization")
                if not df_candidates.empty:
                    fig_pipeline = px.funnel(
                        df_status_stats,
                        x="Candidates",
                        y="Stage",
                        title="Recruitment Pipeline"
                    )
                    st.plotly_chart(fig_pipeline, width="stretch")
            else:
                st.info("No pipeline statuses found.")
        
        with col2:
            st.markdown("#### Quick Stats")
            st.metric("Total Stages", len(statuses))
            if not df_candidates.empty:
                conversion_rate = (len(df_candidates[df_candidates["STATUS"] == "Hired"]) / len(df_candidates) * 100) if len(df_candidates) > 0 else 0
                st.metric("Conversion to Hire", f"{conversion_rate:.1f}%")
        
        st.markdown("---")
        st.info("💡 **How to modify:** Edit the 'Preferences' sheet in the Excel file, column L (starting row 8), then reload data.")
    
    # =========================================================================
    # TAB 5: SYSTEM SETTINGS
    # =========================================================================
    with tab5:
        st.markdown("### System Settings & Data Management")
        
        # Data Management Section
        st.markdown("#### 📁 Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Reload Data**")
            if st.button(f"🔄 Reload from {data_source}", width="stretch"):
                st.cache_data.clear()
                success, msg = data_manager.load_data()
                if success:
                    st.success("Data reloaded successfully!")
                    st.rerun()
                else:
                    st.error(msg)
        
        with col2:
            st.markdown("**Export Data**")
            if st.button("📥 Export All Data", width="stretch"):
                # Create export with all data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Export candidates
                if not df_candidates.empty:
                    csv_candidates = df_candidates.to_csv(index=False)
                    st.download_button(
                        label="Download Candidates CSV",
                        data=csv_candidates,
                        file_name=f"candidates_{timestamp}.csv",
                        mime="text/csv"
                    )
                
                # Export jobs
                if not df_jobs.empty:
                    csv_jobs = df_jobs.to_csv(index=False)
                    st.download_button(
                        label="Download Jobs CSV",
                        data=csv_jobs,
                        file_name=f"jobs_{timestamp}.csv",
                        mime="text/csv"
                    )
        
        with col3:
            st.markdown("**Generate Mock Data**")
            if st.button("🎲 Add Mock Data", width="stretch"):
                st.info("Run `python generate_mock_data.py` from terminal to add sample data.")
        
        st.markdown("---")
        
        # System Information
        st.markdown("#### ℹ️ System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Database Statistics**")
            st.write(f"- Total Candidates: {len(df_candidates)}")
            st.write(f"- Total Job Openings: {len(df_jobs)}")
            st.write(f"- Total Recruiters: {len(preferences.get('Recruiters', []))}")
            st.write(f"- Total Departments: {len(preferences.get('Departments', []))}")
            st.write(f"- Total Sources: {len(preferences.get('Sources', []))}")
        
        with col2:
            st.markdown("**Application Info**")
            st.write("- Version: 2.0 Professional")
            st.write("- Framework: Streamlit")
            data_source = "Google Sheets" if data_manager.manager.use_google_sheets else "Excel (Local)"
            st.write(f"- Data Source: {data_source}")
            st.write(f"- Last Load: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.markdown("---")
        
        # Advanced Settings
        with st.expander("🔧 Advanced Settings"):
            st.markdown("**Cache Management**")
            if st.button("Clear All Cache"):
                st.cache_data.clear()
                st.success("Cache cleared!")
            
            st.markdown("**Debug Information**")
            if st.checkbox("Show Debug Info"):
                st.json({
                    "candidates_columns": df_candidates.columns.tolist() if not df_candidates.empty else [],
                    "jobs_columns": df_jobs.columns.tolist() if not df_jobs.empty else [],
                    "preferences_keys": list(preferences.keys())
                })
        
        st.markdown("---")
        st.success("✅ All systems operational")
