import os
import time

import streamlit as st
from streamlit_card import card

from util.file_io import DemoFileIOHelper
from util.text_processing import DemoTextProcessingHelper
from util.ui_components import DemoUIHelper
from util.display import display_article_page
from util.runner import get_demo_dir, clear_other_page_session_state, set_storm_runner
from util.callback_handlers import StreamlitCallbackHandler
from knowledge_storm.utils import truncate_filename


def home_page():
    # Show create new article form
    st.header("Create New Article")
    
    # Clear other page session states if needed
    if "home_page_init" not in st.session_state:
        clear_other_page_session_state(page_index=1)
        st.session_state["home_page_init"] = True
    
    # Initialize write article state
    if "write_article_state" not in st.session_state:
        st.session_state["write_article_state"] = "not started"
    
    # Create article form
    _, search_form_column, _ = st.columns([2, 5, 2])
    with search_form_column:
        with st.form(key="search_form"):
            # Text input for the search topic
            DemoUIHelper.st_markdown_adjust_size(
                content="Enter the topic you want to learn in depth:", font_size=18
            )
            st.session_state["topic"] = st.text_input(
                label="topic", label_visibility="collapsed"
            )

            control_col, button_col = st.columns([3, 1])
            # Mode selection for STORM or Co-STORM
            with control_col:
                if "mode" not in st.session_state:
                    st.session_state["mode"] = "STORM"  # Default to STORM
                st.session_state["mode"] = st.segmented_control(
                    "Mode",
                    options=["STORM", "Co-STORM"],
                    default="STORM",
                    label_visibility="collapsed",
                )
            # Submit button to start the search
            with button_col:
                submit_button = st.form_submit_button(label="Research")

            # Will be set to false if the topic is empty
            pass_appropriateness_check = True

            if submit_button:
                if not st.session_state["topic"].strip():
                    pass_appropriateness_check = False
                    st.session_state["warning_message"] = "Topic could not be empty"

                st.session_state["topic_name_cleaned"] = (
                    st.session_state["topic"].replace(" ", "_").replace("/", "_")
                )
                st.session_state["topic_name_truncated"] = truncate_filename(
                    st.session_state["topic_name_cleaned"]
                )
                
                if not pass_appropriateness_check:
                    alert = st.warning(
                        st.session_state["warning_message"], icon="⚠️"
                    )
                    time.sleep(5)
                    alert.empty()
                else:
                    st.session_state["write_article_state"] = "initiated"
                    # Set up working directory
                    current_working_dir = os.path.join(get_demo_dir(), "output")
                    if not os.path.exists(current_working_dir):
                        os.makedirs(current_working_dir)

                    if "runner" not in st.session_state:
                        set_storm_runner()
                    st.session_state["current_working_dir"] = current_working_dir
                    
                    # Navigate to article detail page for generation
                    st.session_state["selected_page"] = "article_detail"
                    st.session_state["article_view_mode"] = "generation"
                    st.rerun()
    
    # Divider between create form and article list
    st.divider()
    
    # Show My Articles
    st.header("My Articles")
    
    # Load articles
    local_dir = os.path.join(get_demo_dir(), "output")
    os.makedirs(local_dir, exist_ok=True)
    user_articles_file_path_dict = DemoFileIOHelper.read_structure_to_dict(local_dir)
    
    # Display article cards
    my_article_columns = st.columns(3)
    if len(user_articles_file_path_dict) > 0:
        # Get article names
        article_names = sorted(list(user_articles_file_path_dict.keys()))
        
        # Configure pagination
        pagination = st.container()
        bottom_menu = st.columns((1, 4, 1, 1, 1))[1:-1]
        with bottom_menu[2]:
            batch_size = st.selectbox("Page Size", options=[24, 48, 72])
        with bottom_menu[1]:
            total_pages = (
                int(len(article_names) / batch_size)
                if int(len(article_names) / batch_size) > 0
                else 1
            )
            current_page = st.number_input(
                "Page", min_value=1, max_value=total_pages, step=1
            )
        with bottom_menu[0]:
            st.markdown(f"Page **{current_page}** of **{total_pages}** ")
        
        # Show article cards
        with pagination:
            my_article_count = 0
            start_index = (current_page - 1) * batch_size
            end_index = min(current_page * batch_size, len(article_names))
            for article_name in article_names[start_index:end_index]:
                column_to_add = my_article_columns[my_article_count % 3]
                my_article_count += 1
                
                with column_to_add:
                    cleaned_article_title = article_name.replace("_", " ")
                    hasClicked = card(
                        title="My Article",
                        text=cleaned_article_title,
                        image=DemoFileIOHelper.read_image_as_base64(
                            os.path.join(get_demo_dir(), "assets", "void.jpg")
                        ),
                        styles=DemoUIHelper.get_article_card_UI_style(boarder_color="#9AD8E1"),
                    )
                    if hasClicked:
                        st.session_state["selected_article"] = article_name
                        st.session_state["selected_article_file_path_dict"] = user_articles_file_path_dict[article_name]
                        st.session_state["selected_page"] = "article_detail"
                        st.session_state["article_view_mode"] = "view"
                        st.rerun()
    else:
        st.info("You haven't created any articles yet. Use the form above to start researching a topic.")
