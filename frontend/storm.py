import os

script_dir = os.path.dirname(os.path.abspath(__file__))
wiki_root_dir = os.path.dirname(os.path.dirname(script_dir))

from util.file_io import get_all_articles
from util.pages.HomePage import home_page
from util.pages.ArticleDetailPage import article_detail_page
from streamlit_float import *
import streamlit as st

def main():
    global database
    st.set_page_config(layout="wide", page_title="STORM Research Assistant", page_icon="🧠")

    if "first_run" not in st.session_state:
        # set api keys from secrets
        for key, value in st.secrets.items():
            if type(value) == str:
                os.environ[key] = value
                
        # Load articles
        st.session_state["articles"] = get_all_articles()

        st.session_state["first_run"] = False

    # Initialize page selection
    if "selected_page" not in st.session_state:
        st.session_state["selected_page"] = "home"
    
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
