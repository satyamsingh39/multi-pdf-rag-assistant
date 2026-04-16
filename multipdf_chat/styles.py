from __future__ import annotations

import streamlit as st

APP_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #ffffff;
        --sidebar-bg: #f8fafc;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
        --border: #e2e8f0;
        --accent: #2563eb;
        --accent-hover: #1d4ed8;
        --card-bg: #ffffff;
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }

    html, body, [class*="css"] {
        font-family: "Inter", "Manrope", sans-serif;
    }

    .stApp {
        background-color: var(--bg) !important;
        color: var(--text-primary) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div {
        color: var(--text-secondary) !important;
    }

    /* File Uploader */
    [data-testid="stFileUploaderDropzone"] {
        background: white;
        border: 1px dashed var(--text-muted);
        border-radius: 12px;
        transition: border-color 0.2s ease;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--accent);
    }

    /* Inputs */
    .stTextInput > div > div {
        background: white;
        border: 1px solid var(--border);
        border-radius: 10px;
        transition: all 0.2s ease;
    }

    .stTextInput > div > div:focus-within {
        border-color: var(--accent);
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }

    .stTextInput input {
        color: var(--text-primary);
        min-height: 3rem;
        padding-left: 1rem !important;
    }

    .stTextInput input::placeholder {
        color: var(--text-muted);
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        background-color: var(--text-primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: var(--shadow);
    }

    .stButton > button:hover {
        background-color: #1e293b;
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Custom Cards */
    .hero-card,
    .info-card,
    .response-card,
    .sidebar-card,
    .result-shell {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        box-shadow: var(--shadow);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .hero-card {
        background: linear-gradient(to bottom right, #f8fafc, #ffffff);
        border: 1px solid #cbd5e1;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        background: #eff6ff;
        border: 1px solid #dbeafe;
        color: var(--accent);
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin: 0.75rem 0 0.5rem;
        color: var(--text-primary);
    }

    .hero-copy,
    .section-copy,
    .sidebar-copy {
        color: var(--text-secondary);
        line-height: 1.6;
        font-size: 0.95rem;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-top: 1.5rem;
    }

    .stat-chip {
        padding: 0.75rem;
        border-radius: 8px;
        background: #f1f5f9;
        border: 1px solid var(--border);
    }

    .stat-label {
        display: block;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin-bottom: 0.25rem;
    }

    .stat-value {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 0.9rem;
    }

    .section-title,
    .sidebar-title {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.125rem;
        margin-bottom: 0.5rem;
    }

    .question-helper {
        margin-top: 0.5rem;
        color: var(--text-muted);
        font-size: 0.825rem;
    }

    .response-label,
    .result-kicker {
        color: var(--accent);
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .result-question {
        color: var(--text-primary);
        font-size: 1.125rem;
        font-weight: 700;
        line-height: 1.5;
        margin: 0;
    }

    .result-meta {
        margin-top: 0.5rem;
        color: var(--text-muted);
        font-size: 0.875rem;
    }

    .sidebar-list {
        margin: 0;
        padding-left: 1.25rem;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    .sidebar-list li {
        margin-bottom: 0.5rem;
    }

    /* Streamlit specific tweaks */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .stDivider {
        margin: 1.5rem 0;
        border-bottom-color: var(--border);
    }

    @media (max-width: 900px) {
        .stats-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
"""


def inject_styles():
    st.markdown(APP_CSS, unsafe_allow_html=True)
