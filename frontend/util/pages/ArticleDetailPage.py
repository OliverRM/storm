import os
import time

import streamlit as st

from util.file_io import DemoFileIOHelper
from util.ui_components import DemoUIHelper
from util.display import display_article_page, _display_persona_conversations
from util.runner import get_demo_dir, clear_other_page_session_state, set_storm_runner
from util.callback_handlers import StreamlitCallbackHandler


def article_detail_page():
    # Setup navigation sidebar
    with st.sidebar:
        if st.button("Back to Home"):
            # Reset necessary session states before navigating back
            if "article_view_mode" in st.session_state:
                if st.session_state["article_view_mode"] == "generation":
                    if "write_article_state" in st.session_state:
                        del st.session_state["write_article_state"]
                    # Keep runner if exists to avoid recreation
            
            st.session_state["selected_page"] = "home"
            st.rerun()
    
    # Check view mode
    if "article_view_mode" not in st.session_state:
        st.error("No article selected")
        st.session_state["selected_page"] = "home"
        st.rerun()
    
    # Handle article viewing mode
    if st.session_state["article_view_mode"] == "view":
        if "selected_article" not in st.session_state or "selected_article_file_path_dict" not in st.session_state:
            st.error("Article information missing")
            st.session_state["selected_page"] = "home"
            st.rerun()
        
        # Display the selected article
        display_article_page(
            selected_article_name=st.session_state["selected_article"],
            selected_article_file_path_dict=st.session_state["selected_article_file_path_dict"],
            show_title=True,
            show_main_article=True,
        )
    
    # Handle article generation mode
    elif st.session_state["article_view_mode"] == "generation":
        if "write_article_state" not in st.session_state:
            st.session_state["write_article_state"] = "pre_writing"
        
        # Article generation process
        if st.session_state["write_article_state"] == "pre_writing":
            st.header(f"Researching: {st.session_state['topic']}")
            status = st.status("I am brain**STORM**ing now to research the topic. (This may take 2-3 minutes.)")
            st_callback_handler = StreamlitCallbackHandler(status)
            with status:
                # STORM main gen outline
                st.session_state["runner"].run(
                    topic=st.session_state["topic"],
                    do_research=True,
                    do_generate_outline=True,
                    do_generate_article=False,
                    do_polish_article=False,
                    callback_handler=st_callback_handler,
                )
                conversation_log_path = os.path.join(
                    st.session_state["current_working_dir"],
                    st.session_state["topic_name_truncated"],
                    "conversation_log.json",
                )
                _display_persona_conversations(
                    DemoFileIOHelper.read_json_file(conversation_log_path)
                )
                st.session_state["write_article_state"] = "final_writing"
                status.update(label="brain**STORM**ing complete!", state="complete")
                
        elif st.session_state["write_article_state"] == "final_writing":
            # Polish final article
            with st.status(
                "Now I will connect the information I found for your reference. (This may take 4-5 minutes.)"
            ) as status:
                st.info(
                    "Now I will connect the information I found for your reference. (This may take 4-5 minutes.)"
                )
                st.session_state["runner"].run(
                    topic=st.session_state["topic"],
                    do_research=False,
                    do_generate_outline=False,
                    do_generate_article=True,
                    do_polish_article=True,
                    remove_duplicate=False,
                )
                # Finish the session
                st.session_state["runner"].post_run()

                # Update status bar
                st.session_state["write_article_state"] = "prepare_to_show_result"
                status.update(label="information synthesis complete!", state="complete")
                
        elif st.session_state["write_article_state"] == "prepare_to_show_result":
            _, show_result_col, _ = st.columns([4, 3, 4])
            with show_result_col:
                if st.button("Show Final Article"):
                    st.session_state["write_article_state"] = "completed"
                    st.rerun()
                    
        elif st.session_state["write_article_state"] == "completed":
            # Display polished article
            current_working_dir_paths = DemoFileIOHelper.read_structure_to_dict(
                st.session_state["current_working_dir"]
            )
            current_article_file_path_dict = current_working_dir_paths[
                st.session_state["topic_name_truncated"]
            ]
            
            # Update selected article info for consistency with view mode
            st.session_state["selected_article"] = st.session_state["topic_name_cleaned"]
            st.session_state["selected_article_file_path_dict"] = current_article_file_path_dict
            
            display_article_page(
                selected_article_name=st.session_state["topic_name_cleaned"],
                selected_article_file_path_dict=current_article_file_path_dict,
                show_title=True,
                show_main_article=True,
            )
    else:
        st.error("Unknown article view mode")
        st.session_state["selected_page"] = "home"
        st.rerun()
