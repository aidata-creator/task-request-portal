import streamlit as st
from github import Github
import os
import datetime

st.set_page_config(page_title="Task Request Portal", page_icon="📋", layout="centered")

st.title("📋 Submit a Task Request")
st.write("Fill out the details below to log a request directly into our task backlog.")

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", os.getenv("GITHUB_TOKEN"))
REPO_NAME = "aidata-creator/task-request-portal"

with st.form("task_form", clear_on_submit=True):
    # Basic Information
    title = st.text_input("Task Title *", placeholder="e.g., Design Social Media Banner / Process Lead List")
    email = st.text_input("Requester Email *", placeholder="name@company.com")
    
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ["Bug", "Feature Request", "Data Request", "Design", "Automations Request"])
    with col2:
        priority = st.select_slider("Priority", options=["Low", "Medium", "High", "Urgent"])
    
    # 1. DEADLINE (Date Picker)
    today = datetime.date.today()
    deadline = st.date_input("Deadline / Target Date *", min_value=today, value=today + datetime.timedelta(days=3))

    # Detailed Description
    description = st.text_area("Detailed Description *", help="Detail requirements, instructions, or scope.")
    
    # 2. ATTACH FILE OR URL SECTION
    st.subheader("📁 Attachments & File Links")
    file_url = st.text_input("File Link / Asset URL (Optional)", placeholder="e.g., Canva link, Google Drive, Figma, Dropbox URL")
    uploaded_file = st.file_uploader("Upload File (Optional)", type=["png", "jpg", "jpeg", "pdf", "csv", "xlsx", "txt", "docx"])

    submitted = st.form_submit_button("Submit Request")

if submitted:
    if not title or not email or not description:
        st.error("Please fill in all required fields (*).")
    elif not GITHUB_TOKEN:
        st.error("GitHub Token configuration missing in Secrets.")
    else:
        try:
            gh = Github(GITHUB_TOKEN)
            repo = gh.get_repo(REPO_NAME)
            
            # Format File Attachment text
            attachment_info = ""
            if file_url:
                attachment_info += f"\n* **Asset Link:** [{file_url}]({file_url})"
            if uploaded_file is not None:
                attachment_info += f"\n* **Attached File:** `{uploaded_file.name}` ({uploaded_file.size} bytes)"

            if not attachment_info:
                attachment_info = "\n* *None provided*"

            # Construct GitHub Issue Markdown Body
            body = f"""
### 📋 Task Overview
* **Requester:** {email}
* **Priority:** `{priority}`
* **Category:** `{category}`
* **📅 Deadline:** `{deadline.strftime('%B %d, %Y')}`

---
### 📝 Description
{description}

---
### 📁 Attachments & Resources{attachment_info}

---
*_Logged automatically via Streamlit Request Portal._*
"""
            labels = [f"priority:{priority.lower()}", f"type:{category.lower()}"]
            
            issue = repo.create_issue(
                title=f"[{category}] {title}",
                body=body,
                labels=labels
            )
            
            st.success(f"✅ Task created successfully! Track ticket: [#{issue.number} on GitHub]({issue.html_url})")
            
        except Exception as e:
            st.error(f"Error submitting task: {e}")
