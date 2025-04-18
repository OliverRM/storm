import streamlit as st

from util.file_io import Article
from util.display import display_main_article, display_persona_conversations
from util.callback_handlers import StreamlitCallbackHandler


def article_detail_page():
    article: Article = st.session_state["articles"][st.session_state["selected_article"]]
    
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

    # Display article title
    st.header(article.name)
    

    # Tabs to switch between conversation and article
    conversation_tab, article_tab = st.tabs(["Conversation", "Article"])
    
    # Handle article generation mode
    with conversation_tab:
        if "write_article_state" not in st.session_state:
            st.session_state["write_article_state"] = "reviewing"
        
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
                st.session_state["write_article_state"] = "completed"
                status.update(label="information synthesis complete!", state="complete")
                
        elif st.session_state["write_article_state"] == "completed":
            st.success("STORM has finished writing the article.")
        
        display_persona_conversations(article.id)

    # Handle article viewing mode
    with article_tab:
        # Display the selected article
        display_main_article(article.id)
