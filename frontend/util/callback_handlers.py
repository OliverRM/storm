from knowledge_storm.storm_wiki.modules.callback import BaseCallbackHandler


class StreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self, status_container):
        self.status_container = status_container

    def on_identify_perspective_start(self, **kwargs):
        self.status_container.info(
            "Start identifying different perspectives for researching the topic."
        )

    def on_identify_perspective_end(self, perspectives: list[str], **kwargs):
        perspective_list = "\n- ".join(perspectives)
        self.status_container.success(
            f"Finish identifying perspectives. Will now start gathering information"
            f" from the following perspectives:\n- {perspective_list}"
        )

    def on_information_gathering_start(self, **kwargs):
        self.status_container.info("Start browsing the Internet.")

    def on_dialogue_turn_end(self, dlg_turn, **kwargs):
        urls = list(set([r.url for r in dlg_turn.search_results]))
        for url in urls:
            self.status_container.markdown(
                f"""
                    <style>
                    .small-font {{
                        font-size: 14px;
                        margin: 0px;
                        padding: 0px;
                    }}
                    </style>
                    <div class="small-font">Finish browsing <a href="{url}" class="small-font" target="_blank">{url}</a>.</div>
                    """,
                unsafe_allow_html=True,
            )

    def on_information_gathering_end(self, **kwargs):
        self.status_container.success("Finish collecting information.")

    def on_information_organization_start(self, **kwargs):
        self.status_container.info(
            "Start organizing information into a hierarchical outline."
        )

    def on_direct_outline_generation_end(self, outline: str, **kwargs):
        self.status_container.success(
            f"Finish leveraging the internal knowledge of the large language model."
        )

    def on_outline_refinement_end(self, outline: str, **kwargs):
        self.status_container.success(f"Finish leveraging the collected information.")


class CoSTORMCallbackHandler:
    def __init__(self, status_container):
        self.status_container = status_container
    
    def on_warmstart_begin(self):
        self.status_container.info("Starting to analyze the topic and build initial knowledge structure...")
    
    def on_warmstart_complete(self, mind_map):
        self.status_container.success("Initial knowledge structure built successfully!")
    
    def on_step_begin(self, user_utterance=None):
        if user_utterance:
            self.status_container.info("Processing your input...")
        else:
            self.status_container.info("Generating next conversation turn...")
    
    def on_retrieval_complete(self, urls):
        if urls:
            self.status_container.info(f"Found relevant information from {len(urls)} sources")
            for url in urls:
                self.status_container.markdown(
                    f"""
                        <style>
                        .small-font {{
                            font-size: 14px;
                            margin: 0px;
                            padding: 0px;
                        }}
                        </style>
                        <div class="small-font">Retrieved information from <a href="{url}" class="small-font" target="_blank">{url}</a>.</div>
                        """,
                    unsafe_allow_html=True,
                )
    
    def on_step_complete(self, conversation_turn):
        self.status_container.success("Conversation turn complete!")
    
    def on_mind_map_update(self, mind_map):
        self.status_container.info("Knowledge structure has been updated.")
