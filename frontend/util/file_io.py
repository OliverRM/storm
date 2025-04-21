from dataclasses import dataclass
import datetime
import json
import os
from typing import Dict
import random
import string


@dataclass
class Article:
    id: str
    name: str
    mode: str
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
                mode=article["mode"],
                date=datetime.datetime.fromisoformat(article["date"])
            ) for article in json.load(f)
        }

def add_article(name: str, mode: str) -> Article:
    """
    Adds a new article to the articles data file.
    Args:
        name (str): The name of the new article.
    Returns:
        Article: The newly created Article object.
    """
    articles = get_all_articles()
    article_id = ''.join(random.choices(string.ascii_lowercase, k=8))
    article = Article(
        id=article_id,
        name=name,
        mode=mode,
        date=datetime.datetime.now()
    )
    articles[article_id] = article
    with open(os.path.join(os.getcwd(), "output", "articles.json"), "w") as f:
        json.dump(
            [
                {
                    "id": article.id,
                    "name": article.name,
                    "mode": article.mode,
                    "date": article.date.isoformat()
                } 
                for article in articles.values()
            ], 
            f, 
            indent=4
        )
    
    print(f"Article {article_id} added with name: {name} and mode: {mode}")
    
    # Create the directory for the article
    os.makedirs(os.path.join(os.getcwd(), "output", article_id))
    
    return article

def file_exists(article_id, file_name):
    """
    Checks if a file with the given name exists in the directory of the given article.
    Args:
        article_id (str): The ID of the article for which the file is being checked.
        file_name (str): The name of the file to be checked.
    Returns:
        bool: True if the file exists, False otherwise.
    """
    file_path = os.path.join(os.getcwd(), "output", article_id, file_name)
    return os.path.exists(file_path)

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

def write_txt_file(data, article_id, file_name):
    """
    Writes a string to a text file.
    Args:
        data (str): The data to be written to the file.
        article_id (str): The ID of the article for which the file is being written.
        file_name (str): The name of the text file to be written.
    """
    file_path = os.path.join(os.getcwd(), "output", article_id, file_name)
    with open(file_path, "w") as f:
        f.write(data)
    
def write_json_file(data, article_id, file_name):
    """
    Writes a Python dictionary or list to a JSON file.
    Args:
        data (dict or list): The data to be written to the JSON file.
        article_id (str): The ID of the article for which the file is being written.
        file_name (str): The name of the JSON file to be written.
    """
    file_path = os.path.join(os.getcwd(), "output", article_id, file_name)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

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
