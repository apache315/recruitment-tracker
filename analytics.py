"""
Analytics module for Recruitment Tracker
Provides calculation functions for KPIs and metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_time_to_hire(df_candidates):
    """
    Calculate average time from application to hire
    Returns: dict with average days and breakdown by position/department
    """
    if df_candidates.empty:
        return {"average_days": 0, "by_position": {}, "by_department": {}}
    
    # Filter only hired candidates
    hired = df_candidates[df_candidates["STATUS"].astype(str).str.upper() == "HIRED"].copy()
    
    if hired.empty:
        return {"average_days": 0, "by_position": {}, "by_department": {}}
    
    # Ensure APPLICATION DATE is datetime
    hired["APPLICATION DATE"] = pd.to_datetime(hired["APPLICATION DATE"], errors='coerce')
    hired = hired.dropna(subset=["APPLICATION DATE"])
    
    # Calculate days from application to today (or hire date if available)
    # For now, we'll use today as the hire date approximation
    today = pd.Timestamp.now()
    hired["days_to_hire"] = (today - hired["APPLICATION DATE"]).dt.days
    
    # Calculate average
    avg_days = hired["days_to_hire"].mean()
    
    # Breakdown by position
    by_position = {}
    if "POSITION" in hired.columns:
        by_position = hired.groupby("POSITION")["days_to_hire"].mean().to_dict()
    
    # Breakdown by department
    by_department = {}
    if "DEPARTMENT" in hired.columns:
        by_department = hired.groupby("DEPARTMENT")["days_to_hire"].mean().to_dict()
    
    return {
        "average_days": round(avg_days, 1) if not pd.isna(avg_days) else 0,
        "by_position": {k: round(v, 1) for k, v in by_position.items()},
        "by_department": {k: round(v, 1) for k, v in by_department.items()}
    }


def calculate_cost_per_hire(df_jobs, df_candidates):
    """
    Calculate average cost per successful hire
    Returns: dict with total cost, total hires, and average
    """
    if df_jobs.empty:
        return {"total_cost": 0, "total_hires": 0, "average_cost": 0}
    
    # Get jobs with hiring cost
    jobs_with_cost = df_jobs[df_jobs["HIRING COST"].notna()].copy()
    
    if jobs_with_cost.empty:
        return {"total_cost": 0, "total_hires": 0, "average_cost": 0}
    
    total_cost = jobs_with_cost["HIRING COST"].sum()
    
    # Count hires (jobs with status "Filled")
    total_hires = len(df_jobs[df_jobs["STATUS"].astype(str).str.upper() == "FILLED"])
    
    avg_cost = total_cost / total_hires if total_hires > 0 else 0
    
    return {
        "total_cost": round(total_cost, 2),
        "total_hires": total_hires,
        "average_cost": round(avg_cost, 2)
    }


def get_conversion_rates(df_candidates):
    """
    Calculate conversion rates between pipeline stages
    Returns: dict with conversion percentages
    """
    if df_candidates.empty:
        return {}
    
    # Define pipeline order
    pipeline_stages = [
        "RECEIVED APPLICATION",
        "SENT TO MANAGER", 
        "INTERVIEWS",
        "TESTS",
        "JOB OFFER",
        "HIRED"
    ]
    
    # Count candidates at each stage
    stage_counts = {}
    for stage in pipeline_stages:
        count = len(df_candidates[df_candidates["STATUS"].astype(str).str.upper() == stage.upper()])
        stage_counts[stage] = count
    
    # Calculate conversion rates
    conversions = {}
    total_candidates = len(df_candidates)
    
    if total_candidates > 0:
        for stage, count in stage_counts.items():
            conversions[stage] = round((count / total_candidates) * 100, 1)
    
    return conversions


def get_funnel_data(df_candidates):
    """
    Get data formatted for funnel visualization
    Returns: DataFrame with stages and counts
    """
    if df_candidates.empty:
        return pd.DataFrame(columns=["Stage", "Count", "Percentage"])
    
    pipeline_stages = [
        "Received Application",
        "Sent to Manager", 
        "Interviews",
        "Tests",
        "Job Offer",
        "Hired"
    ]
    
    stage_data = []
    total = len(df_candidates)
    
    for stage in pipeline_stages:
        count = len(df_candidates[df_candidates["STATUS"].astype(str).str.upper() == stage.upper()])
        percentage = (count / total * 100) if total > 0 else 0
        stage_data.append({
            "Stage": stage,
            "Count": count,
            "Percentage": round(percentage, 1)
        })
    
    return pd.DataFrame(stage_data)


def get_source_metrics(df_candidates):
    """
    Calculate effectiveness metrics by source
    Returns: DataFrame with source metrics
    """
    if df_candidates.empty or "SOURCE" not in df_candidates.columns:
        return pd.DataFrame(columns=["Source", "Total Candidates", "Hired", "Hire Rate %"])
    
    source_data = []
    
    for source in df_candidates["SOURCE"].dropna().unique():
        source_candidates = df_candidates[df_candidates["SOURCE"] == source]
        total = len(source_candidates)
        hired = len(source_candidates[source_candidates["STATUS"].astype(str).str.upper() == "HIRED"])
        hire_rate = (hired / total * 100) if total > 0 else 0
        
        source_data.append({
            "Source": source,
            "Total Candidates": total,
            "Hired": hired,
            "Hire Rate %": round(hire_rate, 1)
        })
    
    df_sources = pd.DataFrame(source_data)
    return df_sources.sort_values("Hired", ascending=False)


def get_recruiter_metrics(df_candidates, df_jobs=None):
    """
    Calculate performance metrics by recruiter
    Returns: DataFrame with recruiter metrics
    """
    if df_candidates.empty or "RECRUITER" not in df_candidates.columns:
        return pd.DataFrame(columns=["Recruiter", "Total Candidates", "Hired", "In Process", "Hire Rate %"])
    
    recruiter_data = []
    
    for recruiter in df_candidates["RECRUITER"].dropna().unique():
        recruiter_candidates = df_candidates[df_candidates["RECRUITER"] == recruiter]
        total = len(recruiter_candidates)
        hired = len(recruiter_candidates[recruiter_candidates["STATUS"].astype(str).str.upper() == "HIRED"])
        in_process = len(recruiter_candidates[~recruiter_candidates["STATUS"].astype(str).str.upper().isin(["HIRED", "NOT HIRED", "CANDIDATE REFUSAL"])])
        hire_rate = (hired / total * 100) if total > 0 else 0
        
        recruiter_data.append({
            "Recruiter": recruiter,
            "Total Candidates": total,
            "Hired": hired,
            "In Process": in_process,
            "Hire Rate %": round(hire_rate, 1)
        })
    
    df_recruiters = pd.DataFrame(recruiter_data)
    return df_recruiters.sort_values("Total Candidates", ascending=False)


def get_department_metrics(df_candidates, df_jobs):
    """
    Calculate metrics by department
    Returns: DataFrame with department metrics
    """
    if df_jobs.empty or "DEPARTMENT" not in df_jobs.columns:
        return pd.DataFrame(columns=["Department", "Open Positions", "Total Candidates", "Hired"])
    
    dept_data = []
    
    for dept in df_jobs["DEPARTMENT"].dropna().unique():
        dept_jobs = df_jobs[df_jobs["DEPARTMENT"] == dept]
        open_positions = len(dept_jobs[dept_jobs["STATUS"].astype(str).str.upper() == "VACANT"])
        
        # Get candidates for this department's jobs
        dept_job_ids = dept_jobs["JOB ID"].tolist()
        dept_candidates = df_candidates[df_candidates["JOB ID"].isin(dept_job_ids)] if "JOB ID" in df_candidates.columns else pd.DataFrame()
        
        total_candidates = len(dept_candidates)
        hired = len(dept_candidates[dept_candidates["STATUS"].astype(str).str.upper() == "HIRED"]) if not dept_candidates.empty else 0
        
        dept_data.append({
            "Department": dept,
            "Open Positions": open_positions,
            "Total Candidates": total_candidates,
            "Hired": hired
        })
    
    df_depts = pd.DataFrame(dept_data)
    return df_depts.sort_values("Open Positions", ascending=False)


def calculate_trends(df_candidates, period='M'):
    """
    Calculate time-series trends for candidates
    period: 'D' (daily), 'W' (weekly), 'M' (monthly), 'Y' (yearly)
    Returns: DataFrame with time periods and counts
    """
    if df_candidates.empty or "APPLICATION DATE" not in df_candidates.columns:
        return pd.DataFrame(columns=["Period", "Applications", "Hired"])
    
    df = df_candidates.copy()
    df["APPLICATION DATE"] = pd.to_datetime(df["APPLICATION DATE"], errors='coerce')
    df = df.dropna(subset=["APPLICATION DATE"])
    
    if df.empty:
        return pd.DataFrame(columns=["Period", "Applications", "Hired"])
    
    # Group by period
    df["Period"] = df["APPLICATION DATE"].dt.to_period(period)
    
    # Count applications and hires per period
    applications = df.groupby("Period").size()
    hired = df[df["STATUS"].astype(str).str.upper() == "HIRED"].groupby("Period").size()
    
    # Combine into DataFrame
    trends = pd.DataFrame({
        "Applications": applications,
        "Hired": hired
    }).fillna(0)
    
    trends.index = trends.index.astype(str)
    trends = trends.reset_index()
    trends.columns = ["Period", "Applications", "Hired"]
    
    return trends


def get_pipeline_distribution(df_candidates):
    """
    Get distribution of candidates across pipeline stages
    Returns: DataFrame with stage counts and percentages
    """
    if df_candidates.empty or "STATUS" not in df_candidates.columns:
        return pd.DataFrame(columns=["Status", "Count", "Percentage"])
    
    total = len(df_candidates)
    status_counts = df_candidates["STATUS"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    status_counts["Percentage"] = round((status_counts["Count"] / total * 100), 1)
    
    return status_counts
