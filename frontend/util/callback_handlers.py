from knowledge_storm.storm_wiki.modules.callback import BaseCallbackHandler as WikiBaseCallbackHandler
from knowledge_storm.collaborative_storm.modules.callback import BaseCallbackHandler as CoStormBaseCallbackHandler
from typing import List
import os
import json
import datetime


def ensure_log_directory(article_id):
    """Create the log directory if it doesn't exist."""
    log_dir = f"./output/{article_id}"
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def log_callback(article_id, callback_name, args=None, kwargs=None):
    """Log a callback to the article's log file."""
    timestamp = datetime.datetime.now().isoformat()
    args_str = json.dumps(args) if args is not None else "null"
    kwargs_str = json.dumps({k: str(v) for k, v in kwargs.items()}) if kwargs else "{}"
    
    log_dir = ensure_log_directory(article_id)
    log_path = f"{log_dir}/log.txt"
    
    with open(log_path, "a") as f:
        f.write(f"{timestamp}\t{callback_name}\t{args_str}\t{kwargs_str}\n")


class WikiCallbackHandler(WikiBaseCallbackHandler):
    def __init__(self, status_container, article_id):
        self.status_container = status_container
        self.article_id = article_id
        log_callback(self.article_id, "init", None, {"status_container": "status_container", "article_id": article_id})

    def on_identify_perspective_start(self, **kwargs):
        log_callback(self.article_id, "on_identify_perspective_start", None, kwargs)
        self.status_container.info(
            "Start identifying different perspectives for researching the topic."
        )

    def on_identify_perspective_end(self, perspectives: list[str], **kwargs):
        log_callback(self.article_id, "on_identify_perspective_end", {"perspectives": perspectives}, kwargs)
        perspective_list = "\n- ".join(perspectives)
        self.status_container.success(
            f"Finish identifying perspectives. Will now start gathering information"
            f" from the following perspectives:\n- {perspective_list}"
        )

    def on_information_gathering_start(self, **kwargs):
        log_callback(self.article_id, "on_information_gathering_start", None, kwargs)
        self.status_container.info("Start browsing the Internet.")

    def on_dialogue_turn_end(self, dlg_turn, **kwargs):
        log_callback(self.article_id, "on_dialogue_turn_end", {"dlg_turn": str(dlg_turn)}, kwargs)
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
        log_callback(self.article_id, "on_information_gathering_end", None, kwargs)
        self.status_container.success("Finish collecting information.")

    def on_information_organization_start(self, **kwargs):
        log_callback(self.article_id, "on_information_organization_start", None, kwargs)
        self.status_container.info(
            "Start organizing information into a hierarchical outline."
        )

    def on_direct_outline_generation_end(self, outline: str, **kwargs):
        log_callback(self.article_id, "on_direct_outline_generation_end", {"outline": outline}, kwargs)
        self.status_container.success(
            f"Finish leveraging the internal knowledge of the large language model."
        )

    def on_outline_refinement_end(self, outline: str, **kwargs):
        log_callback(self.article_id, "on_outline_refinement_end", {"outline": outline}, kwargs)
        self.status_container.success(f"Finish leveraging the collected information.")


class CoSTORMCallbackHandler(CoStormBaseCallbackHandler):
    """Base callback handler to manage callbacks from the Co-STORM pipeline."""
    
    def __init__(self, status_container, article_id):
        self.status_container = status_container
        self.article_id = article_id
        log_callback(self.article_id, "init", None, {"status_container": "status_container", "article_id": article_id})

    def on_turn_policy_planning_start(self, **kwargs):
        """Run when the turn policy planning begins, before deciding the direction or goal for the next conversation turn."""
        log_callback(self.article_id, "on_turn_policy_planning_start", None, kwargs)
        self.status_container.info("Start planning next expert actions and inspecting the mind map.")

    def on_expert_action_planning_start(self, **kwargs):
        """Run when the expert action planning begins, preparing to determine the actions that each expert should take."""
        log_callback(self.article_id, "on_expert_action_planning_start", None, kwargs)
        self.status_container.info("Reviewing discourse history and deciding utterance intent.")

    def on_expert_action_planning_end(self, **kwargs):
        """Run when the expert action planning ends, after deciding the actions that each expert should take."""
        log_callback(self.article_id, "on_expert_action_planning_end", None, kwargs)
        self.status_container.success("Finished planning expert actions.")

    def on_expert_information_collection_start(self, **kwargs):
        """Run when the expert information collection starts, start gathering all necessary data from selected sources."""
        log_callback(self.article_id, "on_expert_information_collection_start", None, kwargs)
        self.status_container.info("Start searching with the search engine and browsing collected information.")

    def on_expert_information_collection_end(self, info: List["Information"], **kwargs):
        """Run when the expert information collection ends, after gathering all necessary data from selected sources."""
        log_callback(self.article_id, "on_expert_information_collection_end", {"info": str(info)}, kwargs)
        if info:
            urls = list(set([i.url for i in info if hasattr(i, 'url')]))
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
        self.status_container.success("Finished collecting information.")

    def on_expert_utterance_generation_end(self, **kwargs):
        """Run when the expert utterance generation ends, before creating responses or statements from each expert."""
        log_callback(self.article_id, "on_expert_utterance_generation_end", None, kwargs)
        self.status_container.success("Finished generating expert utterance from collected information.")

    def on_expert_utterance_polishing_start(self, **kwargs):
        """Run when the expert utterance polishing begins, to refine and improve the clarity and coherence of generated content."""
        log_callback(self.article_id, "on_expert_utterance_polishing_start", None, kwargs)
        self.status_container.info("Start polishing expert utterance for clarity and coherence.")

    def on_mindmap_insert_start(self, **kwargs):
        """Run when the process of inserting new information into the mindmap starts."""
        log_callback(self.article_id, "on_mindmap_insert_start", None, kwargs)
        self.status_container.info("Start inserting information into mind map.")

    def on_mindmap_insert_end(self, **kwargs):
        """Run when the process of inserting new information into the mindmap ends."""
        log_callback(self.article_id, "on_mindmap_insert_end", None, kwargs)
        self.status_container.success("Finished inserting information into mind map.")

    def on_mindmap_reorg_start(self, **kwargs):
        """Run when the reorganization of the mindmap begins, to restructure and optimize the flow of information."""
        log_callback(self.article_id, "on_mindmap_reorg_start", None, kwargs)
        self.status_container.info("Start reorganizing mind map for better information flow.")

    def on_expert_list_update_start(self, **kwargs):
        """Run when the expert list update starts, to modify or refresh the list of active experts."""
        log_callback(self.article_id, "on_expert_list_update_start", None, kwargs)
        self.status_container.info("Start updating expert candidates.")

    def on_article_generation_start(self, **kwargs):
        """Run when the article generation process begins, to compile and format the final article content."""
        log_callback(self.article_id, "on_article_generation_start", None, kwargs)
        self.status_container.info("Start generating final article from collected information.")

    def on_warmstart_update(self, message, **kwargs):
        """Run when the warm start process has update."""
        log_callback(self.article_id, "on_warmstart_update", {"message": message}, kwargs)
        self.status_container.info(f"Warm start update: {message}")
