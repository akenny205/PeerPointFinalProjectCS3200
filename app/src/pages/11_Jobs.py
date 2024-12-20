import logging
import pandas as pd
import streamlit as st
from modules.nav import SideBarLinks
import requests

    
logger = logging.getLogger(__name__)

if st.session_state['role'] == 'admin':
    st.set_page_config(layout='wide')


    SideBarLinks()

    st.title('Admin Job Editor')

    # Create a 2-column layout
    col1, col2 = st.columns(2)

    # Column 1: Add and delete jobs
    with col1:
        # Add Job Form
        st.subheader("Add a New Job")
        title = st.text_input('Input Job Title:')
        empid = st.text_input('Input Employer ID:')
        description = st.text_input('Input Job Description:')
    # Add Jobs
        if st.button('Add Job', use_container_width=True):
            if title and empid and description:

                job_data = {
                    'Title': title,
                    'EmpID': empid,
                    'Description': description
                }

                response = requests.post(f"http://api:4000/j/create_job/{empid}/{title}/{description}", json=job_data)

                if response.status_code == 200:
                    st.success("Job added successfully!")
                else:
                    st.error("Failed to add job.")
            else:
                st.warning("Please fill in all fields.")
        st.subheader("Delete a Job")
        JobID = st.text_input('Input Job ID:')

    # Delete Jobs
        if st.button('Delete Job', use_container_width=True):
            if JobID:
                response = requests.delete(f"http://api:4000/j/deletejob/{JobID}")
                if response.status_code == 200:
                    st.success("Job deleted successfully!")
                else:
                    st.error("Failed to delete job.")
            else:
                st.warning("Please fill in all fields.")

    # Displays all jobIDs and Titles
    with col2:
        st.subheader("Current Jobs")
        response = requests.get('http://api:4000/j/viewjobs')
        if response.status_code == 200:
            jobs = response.json()
            if jobs:
                st.dataframe(jobs)
            else:
                st.write("No jobs available.")
else:
    # Init Back Button:
    if st.session_state['role'] == 'coop_career_advisor':
        page = 'pages/20_Advisor_Home.py'
    elif st.session_state['role'] == 'peer_mentor':
        page = 'pages/10_Exp_Student_Home.py'
    elif st.session_state['role'] == 'inexperienced_student':
        page = 'pages/00_Inexp_Student_Home.py'
    
    st.set_page_config(layout='wide')

    SideBarLinks()

    st.title('Jobs Browser')
    
    st.subheader("Current Jobs")
    response = requests.get('http://api:4000/j/viewjobs')
    if response.status_code == 200:
        jobs = response.json()
        if jobs:
            st.dataframe(jobs)
        else:
            st.write("No jobs to display.")