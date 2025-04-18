import time
import pytz

import streamlit as st
from streamlit_card import card

from util.ui_components import DemoUIHelper
from util.runner import create_article


def home_page():
    # Show create new article form
    st.header("Create New Article")
        
    # Create article form
    _, search_form_column, _ = st.columns([2, 5, 2])
    with search_form_column:
        with st.form(key="search_form"):
            # Text input for the search topic
            DemoUIHelper.st_markdown_adjust_size(
                content="Enter the topic you want to learn in depth:", font_size=18
            )
            st.session_state["new_article_topic"] = st.text_input(
                label="topic", label_visibility="collapsed"
            )

            control_col, button_col = st.columns([3, 1])
            # Mode selection for STORM or Co-STORM
            with control_col:
                if "new_article_mode" not in st.session_state:
                    st.session_state["new_article_mode"] = "wiki"  # Default to Storm Wiki
                st.session_state["new_article_mode"] = st.segmented_control(
                    "Mode",
                    options=["wiki", "costorm"],
                    default="wiki",
                    format_func=lambda mode: "STORM" if mode == "wiki" else "Co-STORM",
                    label_visibility="collapsed",
                )
            # Submit button to start the search
            with button_col:
                submit_button = st.form_submit_button(label="Research")

            if submit_button:
                st.session_state["new_article_topic"] = st.session_state["new_article_topic"].strip()

                if not st.session_state["new_article_topic"]:
                    alert = st.warning(
                        "Topic could not be empty", icon="⚠️"
                    )
                    time.sleep(5)
                    alert.empty()
                else:
                    article_id = create_article(st.session_state["new_article_topic"], st.session_state["new_article_mode"])
                    
                    st.session_state["selected_article"] = article_id
                    st.rerun()
    
    # Divider between create form and article list
    st.divider()
    
    # Show My Articles
    st.header("My Articles")
    
    # Load articles
    articles = list(st.session_state["articles"].values())
    
    if len(articles) > 0:
        # Show article cards
        for article in articles:
            # Convert UTC date to local timezone and format it
            local_tz = pytz.timezone(time.tzname[0])
            local_date = article.date.astimezone(local_tz)
            formatted_date = local_date.strftime("%c")

            hasClicked = card(
                title=formatted_date,
                text=article.name,
                styles=DemoUIHelper.get_article_card_UI_style(border_color="#9AD8E1"),
            )
            if hasClicked:
                st.session_state["selected_article"] = article.id
                st.session_state["selected_page"] = "article_detail"
                st.rerun()
    else:
        st.info("You haven't created any articles yet. Use the form above to start researching a topic.")
    
    # For debugging purposes, show all session state
    st.divider()

    st.subheader("Session State")
    st.write(st.session_state)

    # Refresh button, reloads the state
    if st.button("Refresh"):
        st.experimental_rerun()
