import streamlit as st
from st_pages import Page, show_pages

from functions.data_loading import load_data_concurrently
from functions.main_page import main_page


st.set_page_config(layout="wide", page_title="Real Estate Market Analysis",
                   page_icon="🏘️")


if __name__ == "__main__":
    main_page()


if not hasattr(st.session_state, "data"):
    st.session_state.data = {}
    load_data_concurrently(True)
