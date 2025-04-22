import streamlit as st
from knowledge_storm.collaborative_storm.engine import CoStormRunner
from stoc import stoc

from util.text_processing import DemoTextProcessingHelper
from util.file_io import construct_citation_dict_from_knowledge_base, read_json_file, assemble_article_data, read_txt_file


def display_references(article_id):
    article_data = assemble_article_data(article_id)
    citation_dict = article_data.get("citations", {})

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


def display_toc(article_id):
    article_data = assemble_article_data(article_id)
    article_text = article_data.get("article", "")
    toc = stoc.from_markdown(article_text)
    toc.toc()


def _display_article(article_text: str, citation_dict: dict):
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
    
    # customize markdown font size
    custom_css = """
    <style>
        /* Adjust the font size for headings */
        h1 { font-size: 28px; }
        h2 { font-size: 24px; }
        h3 { font-size: 22px; }
        h4 { font-size: 20px; }
        h5 { font-size: 18px; }
        /* Adjust the font size for normal text */
        p { font-size: 18px; }
    </style>
    """
    st.html(custom_css)
    st.markdown(article_text)


def display_wiki_article(article_id):
    article_data = assemble_article_data(article_id)

    article_text=article_data.get("article", "")
    citation_dict=article_data.get("citations", {})

    _display_article(article_text, citation_dict)


def display_costorm_article(
    article_id, runner: CoStormRunner, show_reference=True
) -> bool:
    article_text = read_txt_file(article_id, "article.txt")
    article_text = DemoTextProcessingHelper.parse(article_text)
    
    citation_dict = construct_citation_dict_from_knowledge_base(runner.knowledge_base)
    
    _display_article(article_text, citation_dict)
