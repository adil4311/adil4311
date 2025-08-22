import json
import os
from typing import Any

import requests
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="HyperAI Builder",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def theme_css(theme: str) -> str:
    if theme == "dark":
        return """
        <style>
        :root { --bg: #0b0f19; --panel: #111827; --text: #e5e7eb; --accent: #6366f1; }
        body { background: var(--bg); }
        .stApp { background: var(--bg); color: var(--text); }
        .css-1d391kg, .stSidebar { background: var(--panel); }
        </style>
        """
    return """
    <style>
    :root { --bg: #ffffff; --panel: #f8fafc; --text: #0f172a; --accent: #4f46e5; }
    body { background: var(--bg); }
    .stApp { background: var(--bg); color: var(--text); }
    .css-1d391kg, .stSidebar { background: var(--panel); }
    </style>
    """


st.markdown(theme_css(st.session_state.theme), unsafe_allow_html=True)

col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("HyperAI Builder")
    st.caption("Build production-grade AI apps from natural language.")
with col2:
    toggle = st.toggle("Dark Mode", value=(st.session_state.theme == "dark"))
    st.session_state.theme = "dark" if toggle else "light"

st.sidebar.header("Navigation")
st.sidebar.page_link("app.py", label="Project Wizard", icon="🧭")

# Auth
if "token" not in st.session_state:
    st.session_state.token = None

with st.sidebar:
    st.subheader("Auth")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    col_a, col_b = st.columns(2)
    if col_a.button("Register"):
        r = requests.post(f"{API_BASE}/auth/register", json={"email": email, "password": password})
        if r.ok:
            st.session_state.token = r.json()["access_token"]
            st.success("Registered and logged in.")
        else:
            st.error(r.text)
    if col_b.button("Login"):
        r = requests.post(f"{API_BASE}/auth/login", json={"email": email, "password": password})
        if r.ok:
            st.session_state.token = r.json()["access_token"]
            st.success("Logged in.")
        else:
            st.error(r.text)

headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

with st.sidebar:
    st.subheader("AI Providers")
    provider = st.selectbox("Provider", options=["openai", "anthropic", "gemini"], index=0)
    with st.expander("API Keys (encrypted)"):
        openai_key = st.text_input("OpenAI API Key", type="password")
        anthropic_key = st.text_input("Anthropic API Key", type="password")
        google_key = st.text_input("Google API Key", type="password")
        if st.button("Save Keys") and st.session_state.token:
            for p, k in [("openai", openai_key), ("anthropic", anthropic_key), ("gemini", google_key)]:
                if k:
                    rr = requests.post(
                        f"{API_BASE}/settings/api-keys",
                        json={"provider": p, "key": k},
                        headers=headers,
                    )
                    if not rr.ok:
                        st.error(f"Failed to save key for {p}: {rr.text}")
            st.success("Keys saved (securely)")

st.subheader("Project Creation Wizard")
with st.form("wizard"):
    name = st.text_input("Project Name")
    description = st.text_area("Describe your app in natural language", height=160)
    submitted = st.form_submit_button("Generate Blueprint")

if submitted and st.session_state.token:
    pr = requests.post(
        f"{API_BASE}/projects/",
        json={"name": name, "description": description},
        headers=headers,
    )
    if pr.ok:
        project = pr.json()
        st.session_state["current_project"] = project
        st.success("Project created.")
        br = requests.post(
            f"{API_BASE}/ai/blueprint",
            json={"description": description, "project_id": project["id"], "provider": provider},
            headers=headers,
        )
        if br.ok:
            blueprint_md = br.json()["blueprint_markdown"]
            st.session_state["current_project"]["blueprint_markdown"] = blueprint_md
        else:
            st.error(br.text)
    else:
        st.error(pr.text)

project = st.session_state.get("current_project")
if project:
    st.markdown("### Blueprint Preview")
    st.markdown(project.get("blueprint_markdown", "(awaiting generation)"))
    if st.button("Queue Code Generation"):
        gr = requests.post(
            f"{API_BASE}/ai/generate",
            json={"project_id": project["id"], "provider": provider},
            headers=headers,
        )
        if gr.ok:
            st.info("Code generation queued. Check status in the sidebar soon.")
        else:
            st.error(gr.text)

st.divider()
st.caption("Backend: FastAPI · Frontend: Streamlit · Queue: Celery · DB: SQLAlchemy")