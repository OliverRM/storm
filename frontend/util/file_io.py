from dataclasses import dataclass
import datetime
import json
import os
from typing import Dict


@dataclass
class Article:
    id: str
    name: str
    date: datetime.datetime

def get_all_articles() -> Dict[str, Article]:
    """
    Reads the articles data file and constructs a dictionary of articles.
    Returns a dictionary where the keys are article IDs, and the values are Article objects.

    Returns:
        dict[str, Article]: A dictionary where each key is an article ID, 
            and each value is an Article object.
    """
    articles_data_file = os.path.join(os.getcwd(), "output", "articles.json")
    if not os.path.exists(articles_data_file):
        return {}
    with open(articles_data_file) as f:
        return {
            article["id"]: Article(
                id=article["id"],
                name=article["name"],
                date=datetime.datetime.fromisoformat(article["date"])
            ) for article in json.load(f)
        }
    
def read_txt_file(article_id, file_name):
    """
    Reads the contents of a text file and returns it as a string.

    Args:
        article_id (str): The ID of the article for which the file is being read.
        file_name (str): The name of the text file to be read.

    Returns:
        str: The content of the file as a single string.
    """
    file_path = os.path.join(os.getcwd(), "output", article_id, file_name)
    with open(file_path) as f:
        return f.read()

def read_json_file(article_id, file_name):
    """
    Reads a JSON file and returns its content as a Python dictionary or list,
    depending on the JSON structure.

    Args:
        article_id (str): The ID of the article for which the file is being read.
        file_name (str): The name of the JSON file to be read.

    Returns:
        dict or list: The content of the JSON file. The type depends on the
                    structure of the JSON file (object or array at the root).
    """
    file_path = os.path.join(os.getcwd(), "output", article_id, file_name)
    with open(file_path) as f:
        return json.load(f)

def assemble_article_data(article_id):
    """
    Constructs a dictionary containing the content and metadata of an article
    based on the available files in the article's directory. This includes the
    main article text, citations from a JSON file, and a conversation log if
    available. The function prioritizes a polished version of the article if
    both a raw and polished version exist.

    Args:
        article_id (str): The ID of the article for which data is being assembled.

    Returns:
        dict or None: A dictionary containing the parsed content of the article,
                    citations, and conversation log if available. Returns None
                    if neither the raw nor polished article text exists in the
                    provided file paths.
    """
    # Import here to avoid circular imports
    from util.text_processing import DemoTextProcessingHelper
    
    # List all files in article dir
    article_files = os.listdir(
        os.path.join(os.getcwd(), "output", article_id)
    )
    
    if (
        "storm_gen_article.txt" in article_files
        or "storm_gen_article_polished.txt" in article_files
    ):
        full_article_file = (
            "storm_gen_article_polished.txt"
            if "storm_gen_article_polished.txt" in article_files
            else "storm_gen_article.txt"
        )
        article_data = {
            "article": DemoTextProcessingHelper.parse(
                read_txt_file(article_id, full_article_file)
            )
        }
        if "url_to_info.json" in article_files:
            article_data["citations"] = _construct_citation_dict_from_search_result(
                read_json_file(article_id, "url_to_info.json")
            )
        if "conversation_log.json" in article_files:
            article_data["conversation_log"] = read_json_file(article_id, "conversation_log.json")
        return article_data
    return None

def _construct_citation_dict_from_search_result(search_results):
    if search_results is None:
        return None
    citation_dict = {}
    for url, index in search_results["url_to_unified_index"].items():
        citation_dict[index] = {
            "url": url,
            "title": search_results["url_to_info"][url]["title"],
            "snippets": search_results["url_to_info"][url]["snippets"],
        }
    return citation_dict
