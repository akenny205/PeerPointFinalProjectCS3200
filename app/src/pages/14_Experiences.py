import logging
logger = logging.getLogger(__name__)
import streamlit as st
import pandas as pd
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks


st.title('Experience Viewer')

SideBarLinks()

# View Experience

if st.button("View Students' Experiences"):
    st.switch_page('/appcode/pages/15_View_Experiences.py')

# Create Experience
if st.button("Create Experience"):
    result = 2 # add route