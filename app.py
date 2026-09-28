import streamlit as st
from github import Github
import gspread
from google.oauth2.service_account import Credentials
import os
import datetime

st.set_page_config(page_title="Task Request Portal", page_icon="📋", layout="centered")

st.title("📋 Submit a Task Request")
st.write("Fill out the details below to log a request directly into our task backlog.")

# Secrets Configuration
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", os.getenv("GITHUB_TOKEN"))
REPO_NAME = "aidata-creator/task-request-portal"

# Helper Function for Google Sheets Connection
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Fetch credentials from Streamlit secrets
    creds_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(credentials)

with st.form("task_form", clear_on_submit=True):
    title = st.text_input("Task Title *", placeholder="e.g., Design Social Media Banner / Process Lead List")
    email = st.text_input("Requester Email *", placeholder="name@company.com")
    
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ["Bug", "Feature Request", "Data Request", "Design", "Automations Request"])
    with col2:
        priority = st.select_slider("Priority", options=["Low", "Medium", "High", "Urgent"])
    
    today = datetime.date.today()
    deadline = st.date_input("Deadline / Target Date *", min_value=today, value=today + datetime.timedelta(days=3))

    description = st.text_area("Detailed Description *", help="Detail requirements, instructions, or scope.")
    
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
            # 1. CREATE GITHUB ISSUE
            gh = Github(GITHUB_TOKEN)
            repo = gh.get_repo(REPO_NAME)
            
            attachment_info = ""
            if file_url:
                attachment_info += f"\n* **Asset Link:** [{file_url}]({file_url})"
            if uploaded_file is not None:
                attachment_info += f"\n* **Attached File:** `{uploaded_file.name}` ({uploaded_file.size} bytes)"

            if not attachment_info:
                attachment_info = "\n* *None provided*"

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

            # 2. APPEND TO GOOGLE SHEET
            try:
                gc = get_gspread_client()
                # Replace with the exact title of your Google Sheet
                sh = gc.open("Task Requests Database").sheet1
                
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file_reference = file_url if file_url else (uploaded_file.name if uploaded_file else "None")
                
                row_data = [
                    timestamp,
                    f"#{issue.number}",
                    title,
                    email,
                    category,
                    priority,
                    deadline.strftime("%Y-%m-%d"),
                    description,
                    file_reference,
                    "",           # Assignee (Left blank for manual assignment in GS)
                    "Unassigned"  # Initial Status
                ]
                
                sh.append_row(row_data)
                gs_status = "and saved to Google Sheets "
            except Exception as gs_err:
                gs_status = f"(Note: Google Sheets save failed: {gs_err}) "

            st.success(f"✅ Task created {gs_status}successfully! Track ticket: [#{issue.number} on GitHub]({issue.html_url})")
            
        except Exception as e:
            st.error(f"Error submitting task: {e}")
