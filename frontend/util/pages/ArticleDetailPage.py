import streamlit as st

from knowledge_storm import CoStormRunner
from knowledge_storm.dataclass import KnowledgeNode

from util.file_io import Article, file_exists, read_json_file, read_txt_file, write_json_file, write_txt_file
from util.display import display_main_article, display_persona_conversations
from util.callback_handlers import WikiCallbackHandler, CoSTORMCallbackHandler
from util.runner import create_costorm_runner, create_costorm_runner_from_dict

def article_detail_page():
    article: Article = st.session_state["selected_article"]
    
    # Setup navigation sidebar
    with st.sidebar:
        if st.button("Back to Home"):
            # Reset necessary session states before navigating back
            if "write_article_state" in st.session_state:
                del st.session_state["write_article_state"]
            # Keep runner if exists to avoid recreation
            
            st.session_state["selected_page"] = "home"
            st.rerun()

    # Display article title
    st.header(article.name)
    

    # Tabs to switch between conversation and article
    conversation_tab, article_tab = st.tabs(["Conversation", "Article"])
    
    with conversation_tab:
        # Handle opening of an existing article
        if "write_article_state" not in st.session_state:
            if article.mode == "wiki":
                st.session_state["write_article_state"] = "completed"
            elif article.mode == "costorm":
                with st.status("Loading article...") as status:
                    st_callback_handler = CoSTORMCallbackHandler(status, article.id)
                    runner = create_costorm_runner_from_dict(
                        read_json_file(article.id, "runner.json"),
                        st_callback_handler,
                    )
                    status.update(state="complete")
                    st.session_state["runner"] = runner
                    st.session_state["write_article_state"] = "conversation"
            else:
                raise ValueError("Invalid article mode")
            st.rerun()
            
        if st.session_state["write_article_state"] == "not_started":
            if article.mode == "wiki":
                st.session_state["write_article_state"] = "pre_writing"
            elif article.mode == "costorm":
                st.session_state["write_article_state"] = "warm_start"
            else:
                raise ValueError("Invalid article mode")
            st.rerun()
        
        
        # States for writing wiki articles
        
        if st.session_state["write_article_state"] == "pre_writing":
            st.header(f"Researching: {st.session_state['topic']}")
            status = st.status("I am brain**STORM**ing now to research the topic. (This may take 2-3 minutes.)")
            st_callback_handler = WikiCallbackHandler(status, article.id)
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
                status.update(label="information synthesis complete!", state="completed_storm")

        elif st.session_state["write_article_state"] == "completed":
            st.success("STORM has finished writing the article.")
            display_persona_conversations(article.id)

        
        # States for writing costorm articles
        
        elif st.session_state["write_article_state"] == "warm_start":
            with st.status(
                "STATUS Conducting background information search in order to build shared conceptual space. (This may take a few minutes.)"
            ) as status:
                st_callback_handler = CoSTORMCallbackHandler(status, article.id)
                runner = create_costorm_runner(article.name, st_callback_handler)
                st.session_state["runner"] = runner
                st.info(
                    "INFO Conducting background information search in order to build shared conceptual space. (This may take a few minutes.)"
                )
                runner.warm_start()
                write_json_file(runner.to_dict(), article.id, "runner.json")
                
                st.session_state["write_article_state"] = "conversation"
                st.rerun()
        
        elif st.session_state["write_article_state"] in ["conversation", "taking_turn"]:
            runner: CoStormRunner = st.session_state["runner"]
            
            # Render past conversation
            for turn in runner.conversation_history:
                st.write(turn)
            
            def render_node(node: KnowledgeNode):
                # kb.write(f"{node.name}: {node.content}")
                st.sidebar.write(node)
                for child in node.children:
                    render_node(child)
            
            render_node(runner.knowledge_base.root)
        
            if st.session_state["write_article_state"] == "conversation":
                # Text box to send new chat message
                user_utterance = st.text_input("Take part in the conversation:", key="user_input")
                
                # Three buttons in a row to finish writing, ask expert, and send off
                col1, col2, col3 = st.columns(3)
                with col2:
                    if st.button("Expert Turn"):
                        st.session_state["utterance_input"] = ""
                        st.session_state["write_article_state"] = "taking_turn"
                        st.rerun()
                with col3:
                    if st.button("Take Part"):
                        st.session_state["utterance_input"] = user_utterance
                        st.session_state["write_article_state"] = "taking_turn"
                        st.rerun()
            
            elif st.session_state["write_article_state"] == "taking_turn":
                utterance = st.session_state["utterance_input"]
                with st.status(
                    "An expert is now taking his turn." if utterance == "" else "The user's turn is being processed.",
                    expanded=True,
                ) as status:
                    callback_handler: CoSTORMCallbackHandler = runner.callback_handler
                    callback_handler.status_container = status
                    runner.step(user_utterance=utterance)
                    status.info("Saving conversation...")
                    status.update(state="complete")
                    write_json_file(runner.to_dict(), article.id, "runner.json")
                    st.session_state["write_article_state"] = "conversation"
                    st.rerun()
            
            else:
                raise ValueError("Invalid write_article_state")
        

    # Handle article viewing mode
    with article_tab:
        if article.mode == "wiki":
            # Display the selected article
            display_main_article(article.id)
        elif article.mode == "costorm":
            exists = file_exists(article.id, "report.txt")
            
            if not exists:
                st.info("It is time to generate the article. Click the button below to start.")
            
            if st.button(
                "Regenerate Article" if exists else "Generate Article",
            ):
                with st.status("Generating article...", expanded=True) as status:
                    runner: CoStormRunner = st.session_state["runner"]
                    callback_handler: CoSTORMCallbackHandler = runner.callback_handler
                    callback_handler.status_container = status
                    report = runner.generate_report()
                    status.info("Saving article...")
                    write_txt_file(report, article.id, "report.txt")
                    status.update(state="complete")
                    st.rerun()
            
            if exists:
                report = read_txt_file(article.id, "report.txt")
                st.markdown(report)
