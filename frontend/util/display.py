import streamlit as st
from stoc import stoc

from util.text_processing import DemoTextProcessingHelper
from util.file_io import read_json_file, assemble_article_data


def _display_main_article_text(article_text, citation_dict, table_content_sidebar):
    # Post-process the generated article for better display.
    if "Write the lead section:" in article_text:
        article_text = article_text[
            article_text.find("Write the lead section:")
            + len("Write the lead section:") :
        ]
    if article_text[0] == "#":
        article_text = "\n".join(article_text.split("\n")[1:])
    article_text = DemoTextProcessingHelper.add_inline_citation_link(
        article_text, citation_dict
    )
    # '$' needs to be changed to '\$' to avoid being interpreted as LaTeX in st.markdown()
    article_text = article_text.replace("$", "\\$")
    stoc.from_markdown(article_text, table_content_sidebar)


def _display_references(citation_dict):
    if citation_dict:
        reference_list = [f"reference [{i}]" for i in range(1, len(citation_dict) + 1)]
        selected_key = st.selectbox("Select a reference", reference_list)
        citation_val = citation_dict[reference_list.index(selected_key) + 1]
        citation_val["title"] = citation_val["title"].replace("$", "\\$")
        st.markdown(f"**Title:** {citation_val['title']}")
        st.markdown(f"**Url:** {citation_val['url']}")
        snippets = "\n\n".join(citation_val["snippets"]).replace("$", "\\$")
        st.markdown(f"**Highlights:**\n\n {snippets}")
    else:
        st.markdown("**No references available**")


def display_persona_conversations(article_id):
    """
    Display persona conversation in dialogue UI
    """
    # get personas list as (persona_name, persona_description, dialogue turns list) tuple
    parsed_conversation_history = DemoTextProcessingHelper.parse_conversation_history(
        read_json_file(article_id, "conversation_log.json")
    )
    # construct tabs for each persona conversation
    persona_tabs = st.tabs([name for (name, _, _) in parsed_conversation_history])
    for idx, persona_tab in enumerate(persona_tabs):
        with persona_tab:
            # show persona description
            st.info(parsed_conversation_history[idx][1])
            # show user / agent utterance in dialogue UI
            for message in parsed_conversation_history[idx][2]:
                message["content"] = message["content"].replace("$", "\\$")
                with st.chat_message(message["role"]):
                    if message["role"] == "user":
                        st.markdown(f"**{message['content']}**")
                    else:
                        st.markdown(message["content"])


def display_main_article(
    article_id, show_reference=True
):
    article_data = assemble_article_data(article_id)

    with st.container(height=1000, border=True):
        table_content_sidebar = st.sidebar.expander(
            "**Table of contents**", expanded=True
        )
        _display_main_article_text(
            article_text=article_data.get("article", ""),
            citation_dict=article_data.get("citations", {}),
            table_content_sidebar=table_content_sidebar,
        )

    # display reference panel
    if show_reference and "citations" in article_data:
        with st.sidebar.expander("**References**", expanded=True):
            with st.container(height=800, border=False):
                _display_references(citation_dict=article_data.get("citations", {}))
