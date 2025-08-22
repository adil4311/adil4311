import os
import uuid

import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="HyperAI Builder",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "step" not in st.session_state:
    st.session_state.step = 1

st.sidebar.title("HyperAI Builder")
mode = st.sidebar.radio("Theme", ["Dark", "Light"], index=0)
if mode == "Light":
    st.markdown(
        """
        <style>
        .stApp { background-color: #ffffff; color: #141414; }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.title("HyperAI Builder")
st.caption("Create professional AI applications from natural language.")

with st.container():
    cols = st.columns(3)
    with cols[0]:
        name = st.text_input("Project Name", placeholder="Customer Support Chatbot")
    with cols[1]:
        model = st.selectbox("AI Model", ["openai", "anthropic", "gemini"], index=0)
    with cols[2]:
        st.write(" ")
        st.write(" ")
        next_clicked = st.button("Generate Blueprint →", use_container_width=True)

    description = st.text_area(
        "Describe your application",
        height=180,
        placeholder=(
            "Build a hyper-realistic AI image editor with error detection and "
            "professional UI"
        ),
    )

if next_clicked and name and description:
    st.session_state.step = 2

if st.session_state.step >= 2:
    st.subheader("Blueprint")
    st.markdown(
        """
        ```mermaid
        flowchart TD
            A[User] -->|Prompt| B[HyperAI Builder]
            B --> C[Blueprint]
            C --> D[Code Generation]
            D --> E[Project Artifacts]
        ```
        """
    )
    if st.button("Create Project", key="create"):
        resp = requests.post(
            f"{API_BASE}/api/projects/",
            json={"name": name, "description": description},
            timeout=20,
        )
        if resp.ok:
            data = resp.json()
            st.session_state.project_id = data["id"]
            st.success("Project created")

if st.session_state.get("project_id"):
    st.subheader("Generate Code")
    prompt = st.text_area("Prompt to generator", value=description, height=150)
    if st.button("Generate", key="gen"):
        pid = st.session_state.project_id
        requests.post(
            f"{API_BASE}/api/projects/{pid}/generate",
            json={"prompt": prompt, "model": model},
            timeout=60,
        )
        st.info("Generation queued. Check status below.")

    st.subheader("Preview")
    with st.spinner("Fetching latest generated code..."):
        pid = st.session_state.project_id
        r = requests.get(f"{API_BASE}/api/projects/{pid}", timeout=20)
        if r.ok:
            proj = r.json()
            st.code(proj.get("generated_code") or "# No code yet", language="python")