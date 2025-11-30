"""
Styling module for Professional Recruitment Tracker
Provides custom CSS and styling functions
"""

import streamlit as st


def apply_custom_css():
    """Apply custom CSS for professional appearance"""
    st.markdown("""
    <style>
    /* Main color scheme */
    :root {
        --primary-color: #2E86DE;
        --secondary-color: #54A0FF;
        --success-color: #10AC84;
        --warning-color: #F79F1F;
        --danger-color: #EE5A6F;
        --dark-bg: #1E272E;
        --light-bg: #F8F9FA;
        --text-primary: #2C3E50;
        --text-secondary: #7F8C8D;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid var(--primary-color);
    }
    
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* KPI Card styling */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: white;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-hired {
        background-color: var(--success-color);
        color: white;
    }
    
    .status-process {
        background-color: var(--warning-color);
        color: white;
    }
    
    .status-rejected {
        background-color: var(--danger-color);
        color: white;
    }
    
    .status-vacant {
        background-color: #FF6B6B;
        color: white;
    }
    
    .status-filled {
        background-color: #51CF66;
        color: white;
    }
    
    /* Table styling */
    .dataframe {
        font-size: 0.9rem;
    }
    
    .dataframe thead tr th {
        background-color: var(--primary-color) !important;
        color: white !important;
        font-weight: 600;
        padding: 12px !important;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    .dataframe tbody tr:hover {
        background-color: #e9ecef;
        cursor: pointer;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2E86DE 0%, #1E5BA8 100%);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2E86DE 0%, #1E5BA8 100%);
    }
    
    /* Metric card improvements */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Form styling */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 0.5rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(46, 134, 222, 0.1);
    }
    
    /* Card container */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #d4edda;
        border-left: 4px solid var(--success-color);
        padding: 1rem;
        border-radius: 4px;
    }
    
    .stError {
        background-color: #f8d7da;
        border-left: 4px solid var(--danger-color);
        padding: 1rem;
        border-radius: 4px;
    }
    
    .stWarning {
        background-color: #fff3cd;
        border-left: 4px solid var(--warning-color);
        padding: 1rem;
        border-radius: 4px;
    }
    
    /* Loading animation */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_kpi_card(label, value, icon="📊", color_gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"):
    """Render a professional KPI card"""
    st.markdown(f"""
    <div class="kpi-card" style="background: {color_gradient};">
        <div style="font-size: 2rem;">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status):
    """Render a status badge with appropriate styling"""
    status_upper = str(status).upper()
    
    if status_upper in ["HIRED", "FILLED"]:
        badge_class = "status-hired"
    elif status_upper in ["NOT HIRED", "REJECTED", "CANCELLED"]:
        badge_class = "status-rejected"
    elif status_upper == "VACANT":
        badge_class = "status-vacant"
    else:
        badge_class = "status-process"
    
    return f'<span class="status-badge {badge_class}">{status}</span>'


def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a styled metric card"""
    st.metric(label=title, value=value, delta=delta, delta_color=delta_color)


def render_section_header(title, icon=""):
    """Render a styled section header"""
    st.markdown(f"""
    <div class="sub-header">
        {icon} {title}
    </div>
    """, unsafe_allow_html=True)


def render_page_header(title, subtitle=""):
    """Render a styled page header"""
    st.markdown(f"""
    <div class="main-header">{title}</div>
    """, unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='color: var(--text-secondary); font-size: 1.1rem;'>{subtitle}</p>", unsafe_allow_html=True)


# Color gradients for different KPI cards
GRADIENT_BLUE = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
GRADIENT_GREEN = "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
GRADIENT_ORANGE = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
GRADIENT_PURPLE = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
GRADIENT_RED = "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
