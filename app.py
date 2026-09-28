import streamlit as st
from github import Github
import os

st.set_page_config(page_title="Task Request Portal", page_icon="📋", layout="centered")

st.title("📋 Submit a Task Request")
st.write("Fill out the details below to log a request directly into our task backlog.")

# Access token securely from Streamlit Secrets or Environment Variables
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", os.getenv("GITHUB_TOKEN"))
REPO_NAME = "aidata-creator/task-request-portal" 

with st.form("task_form", clear_on_submit=True):
    title = st.text_input("Task Title *", placeholder="e.g., Update navigation bar link")
    email = st.text_input("Requester Email *", placeholder="name@company.com")
    
    category = st.selectbox("Category", ["Bug", "Feature Request", "Data Request", "Automations Request"])
    priority = st.select_slider("Priority", options=["Low", "Medium", "High", "Urgent"])
    
    description = st.text_area("Detailed Description *", help="Detail requirements, links, or context.")
    
    submitted = st.form_submit_button("Submit Request")

if submitted:
    if not title or not email or not description:
        st.error("Please fill in all required fields (*).")
    elif not GITHUB_TOKEN:
        st.error("GitHub Token configuration missing.")
    else:
        try:
            gh = Github(GITHUB_TOKEN)
            repo = gh.get_repo(REPO_NAME)
            
            body = f"""
### Task Overview
* **Requester:** {email}
* **Priority:** `{priority}`
* **Category:** `{category}`

---
### Description
{description}

---
*_Logged automatically via Streamlit Request Portal._*
"""
            labels = [f"priority:{priority.lower()}", f"type:{category.lower()}"]
            
            issue = repo.create_issue(
                title=f"[{category}] {title}",
                body=body,
                labels=labels
            )
            
            st.success(f"✅ Request logged successfully! Track issue [#{issue.number} on GitHub]({issue.html_url}).")
            
        except Exception as e:
            st.error(f"Error submitting task: {e}")
