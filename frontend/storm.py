import os

script_dir = os.path.dirname(os.path.abspath(__file__))
wiki_root_dir = os.path.dirname(os.path.dirname(script_dir))

from util.runner import clear_other_page_session_state
from util.pages.HomePage import home_page
from util.pages.ArticleDetailPage import article_detail_page
from streamlit_float import *
import streamlit as st

def main():
    global database
    st.set_page_config(layout="wide", page_title="STORM Research Assistant", page_icon="🧠")

    if "first_run" not in st.session_state:
        st.session_state["first_run"] = True

    # set api keys from secrets
    if st.session_state["first_run"]:
        for key, value in st.secrets.items():
            if type(value) == str:
                os.environ[key] = value

    # Initialize page selection
    if "selected_page" not in st.session_state:
        st.session_state["selected_page"] = "home"
    
    if st.session_state.get("rerun_requested", False):
        st.session_state["rerun_requested"] = False
        st.rerun()

    st.write(
        "<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True
    )
    
    # Display selected page
    if st.session_state["selected_page"] == "home":
        home_page()
    elif st.session_state["selected_page"] == "article_detail":
        article_detail_page()


if __name__ == "__main__":
    main()
