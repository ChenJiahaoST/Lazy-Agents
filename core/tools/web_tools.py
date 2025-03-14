import os
import json

from lazyllm.tools import fc_register
from lazyllm.tools.tools.google_search import GoogleSearch
from lazyllm import LOG
from dotenv import load_dotenv
load_dotenv()

search_engine = GoogleSearch(os.getenv('GOOGLE_SEARCH_API_KEY'), os.getenv('GOOGLE_SEARCH_CX'))

@fc_register("tool")
def web_search(query: str) -> str:
    """
    使用google search搜索与query相关的网页，搜索结果包含每个搜索结果的标题、简介和链接。

    Args:
        query (str): The search query string.
    """
    LOG.info(f"[tool - Web Search] Searching the web for query '{query}'...")
    response = search_engine(query=query, date_restrict='m1')
    if response.get('status_code') != 200:
        return f"Error: Received status code {response.status_code}"
    search_res = json.loads(response.get('content'))
    res_str = ""
    cnt = 0
    for item in search_res.get('items'):
        if cnt >= 5:
            break
        link = item.get("link")
        title = item.get("title")
        snippet = item.get("snippet")
        res_str += f"Title: {title}\nSnippet: {snippet[:50]}...\nURL: {link}\n\n"
        cnt += 1
    return res_str


@fc_register("tool")
def visit_url(url: str, encoding: str = None) -> str:
    """
    使用这个工具来浏览一个网页的详细内容，并返回解析后的文本内容。

    Args:
        url (str): The URL of the webpage to visit.
        encoding (str, optional): The encoding of the webpage. If not specified, the encoding will be automatically detected.
    """
    import requests
    from bs4 import BeautifulSoup
    from readability import Document
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; my-bot/1.0)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        return f"Error: Failed to fetch URL. Exception: {e}"

    if response.status_code != 200:
        return f"Error: Received status code {response.status_code}"

    if encoding:
        response.encoding = encoding
    else:
        response.encoding = response.apparent_encoding or response.encoding

    doc = Document(response.text)
    main_content = doc.summary()
    main_text = BeautifulSoup(main_content, "html.parser").get_text(separator="\n", strip=True)

    return main_text if main_text else "Error: Failed to extract main content."