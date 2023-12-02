import os
import sys
import streamlit as st
from st_pages import Page, show_pages
from dotenv import load_dotenv

# load_dotenv()
# sys.path.append(os.environ["PYTHONPATH"])

from functions.data_loading import load_data_concurrently
from functions.main_page import main_page

# os.chdir(os.environ["PYTHONPATH"])

st.set_page_config(layout="wide", page_title="Real Estate Market Analysis")


show_pages(
    [
        Page("main.py", "Project description", "💻"),
        Page("pages/page_houses.py", "Houses", "🏡"),
        Page("pages/page_lands.py", "Lands", "🌳"),
        Page("pages/page_apartments.py", "Apartments", "🏢")
    ])


if __name__ == "__main__":
    main_page()


if not hasattr(st.session_state, "data"):
    st.session_state.data = {}
    load_data_concurrently(True)

st.markdown("Data loaded")
