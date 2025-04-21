import os
import streamlit as st

from knowledge_storm import (
    STORMWikiRunnerArguments,
    STORMWikiRunner,
    STORMWikiLMConfigs,
)
from knowledge_storm.lm import OpenAIModel
from knowledge_storm.rm import SerperRM
from knowledge_storm.collaborative_storm.engine import (
    CollaborativeStormLMConfigs, 
    RunnerArgument as CoStormRunnerArgument,
    CoStormRunner
)
from knowledge_storm.collaborative_storm.modules.callback import BaseCallbackHandler as CoStormBaseCallbackHandler
from knowledge_storm.logging_wrapper import LoggingWrapper
from knowledge_storm.lm import LitellmModel

from knowledge_storm.collaborative_storm import (
    Encoder as CoStormEncoder,
    KnowledgeBase as CoStormKnowledgeBase,
    ConversationTurn as CoStormConversationTurn,
)


def get_demo_dir():
    return os.getcwd()


def create_wiki_runner():
    current_working_dir = os.path.join(get_demo_dir(), "output")
    if not os.path.exists(current_working_dir):
        os.makedirs(current_working_dir)

    # configure STORM runner
    llm_configs = STORMWikiLMConfigs()
    llm_configs.init_openai_model(
        openai_api_key=st.secrets["OPENAI_API_KEY"],
        azure_api_key="",
        openai_type="openai",
    )
    llm_configs.set_question_asker_lm(
        OpenAIModel(
            model="gpt-4o",
            api_key=st.secrets["OPENAI_API_KEY"],
            api_provider="openai",
            max_tokens=500,
            temperature=1.0,
            top_p=0.9,
        )
    )
    engine_args = STORMWikiRunnerArguments(
        output_dir=current_working_dir,
        max_conv_turn=3,
        max_perspective=3,
        search_top_k=3,
        retrieve_top_k=5,
    )

    rm = SerperRM(serper_search_api_key=st.secrets["SERPER_API_KEY"], k=engine_args.search_top_k)

    runner = STORMWikiRunner(engine_args, llm_configs, rm)
    st.session_state["runner"] = runner


def create_costorm_runner(topic: str, callback_handler: CoStormBaseCallbackHandler) -> CoStormRunner:
    # Configure Co-STORM runner
    lm_config = CollaborativeStormLMConfigs()
    lm_config.init(lm_type=os.getenv("OPENAI_API_TYPE"))
    
    # Default arguments - can be overridden by user inputs
    runner_argument = CoStormRunnerArgument(
        topic = topic,
    )
    
    logging_wrapper = LoggingWrapper(lm_config)
    
    # Using SerperRM by default, but can be easily changed to other RMs
    rm = SerperRM(serper_search_api_key=st.secrets["SERPER_API_KEY"], k=runner_argument.retrieve_top_k)
    
    runner = CoStormRunner(
        lm_config=lm_config,
        runner_argument=runner_argument,
        logging_wrapper=logging_wrapper,
        rm=rm,
        callback_handler=callback_handler,
    )
    
    return runner

def create_costorm_runner_from_dict(data, callback_handler: CoStormBaseCallbackHandler) -> CoStormRunner:
    # CoStormRunner has a method from_dict but that skips loading some
    # required configuration. For example, it always sets the retrieval
    # model to Bing. Therefor, we do not use it and instead reimplement
    # it here.
    
    lm_config = CollaborativeStormLMConfigs()
    lm_config.init(lm_type=os.getenv("OPENAI_API_TYPE"))
    
    runner_argument = CoStormRunnerArgument.from_dict(data["runner_argument"])
    
    logging_wrapper = LoggingWrapper(lm_config)
    
    # Using SerperRM by default, but can be easily changed to other RMs
    rm = SerperRM(serper_search_api_key=st.secrets["SERPER_API_KEY"], k=runner_argument.retrieve_top_k)
    
    runner = CoStormRunner(
        lm_config=lm_config,
        runner_argument=runner_argument,
        logging_wrapper=logging_wrapper,
        rm=rm,
        callback_handler=callback_handler,
    )
    runner.encoder = CoStormEncoder()
    runner.conversation_history = [
        CoStormConversationTurn.from_dict(turn) for turn in data["conversation_history"]
    ]
    runner.warmstart_conv_archive = [
        CoStormConversationTurn.from_dict(turn)
        for turn in data.get("warmstart_conv_archive", [])
    ]
    runner.discourse_manager.deserialize_experts(data["experts"])
    runner.knowledge_base = CoStormKnowledgeBase.from_dict(
        data=data["knowledge_base"],
        knowledge_base_lm=runner.lm_config.knowledge_base_lm,
        node_expansion_trigger_count=runner.runner_argument.node_expansion_trigger_count,
        encoder=runner.encoder,
    )
    return runner
