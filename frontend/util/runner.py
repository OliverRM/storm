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
    RunnerArgument,
    CoStormRunner
)
from knowledge_storm.logging_wrapper import LoggingWrapper
from knowledge_storm.lm import LitellmModel


def get_demo_dir():
    return os.getcwd()


def set_storm_runner():
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


def set_costorm_runner():
    current_working_dir = os.path.join(get_demo_dir(), "output")
    if not os.path.exists(current_working_dir):
        os.makedirs(current_working_dir)
    
    # Configure Co-STORM runner
    lm_config = CollaborativeStormLMConfigs()
    
    openai_kwargs = {
        "api_key": st.secrets["OPENAI_API_KEY"],
        "api_provider": "openai",
        "temperature": 1.0,
        "top_p": 0.9,
    }
    
    # Use the same model for all LLM components for simplicity
    # In production, you might want different models for different tasks
    gpt_4o = LitellmModel(model="gpt-4o", max_tokens=1000, **openai_kwargs)
    
    lm_config.set_question_answering_lm(gpt_4o)
    lm_config.set_discourse_manage_lm(gpt_4o)
    lm_config.set_utterance_polishing_lm(gpt_4o)
    lm_config.set_warmstart_outline_gen_lm(gpt_4o)
    lm_config.set_question_asking_lm(gpt_4o)
    lm_config.set_knowledge_base_lm(gpt_4o)
    
    # Default arguments - can be overridden by user inputs
    runner_argument = RunnerArgument(
        topic="",  # Will be set by user input
        output_dir=current_working_dir,
        retrieve_top_k=3,
    )
    
    logging_wrapper = LoggingWrapper(lm_config)
    
    # Using SerperRM by default, but can be easily changed to other RMs
    rm = SerperRM(serper_search_api_key=st.secrets["SERPER_API_KEY"], k=runner_argument.retrieve_top_k)
    
    runner = CoStormRunner(
        lm_config=lm_config,
        runner_argument=runner_argument,
        logging_wrapper=logging_wrapper,
        rm=rm
    )
    
    st.session_state["costorm_runner"] = runner

def create_article(topic: str, mode: str):
    if mode == 'wiki':
        set_wiki_runner()
    elif mode == 'costorm':
        set_costorm_runner()
    else:
        raise ValueError("Invalid mode. Mode must be 'wiki' or 'costorm'.")
