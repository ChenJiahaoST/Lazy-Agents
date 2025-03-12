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
    使用google search搜索与query最相关的网页，搜索结果将返回一个json格式的列表，包含每个搜索结果的标题、简介和链接。

    Args:
        query (str): The search query string.
    """
    LOG.info(f"[tool - Web Search] Searching the web for query '{query}'...")
    # search_engine = GoogleSearch(GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_CX)
    response = search_engine(query=query, date_restrict='m1')
    if response.get('status_code') != 200:
        return f"Error: Received status code {response.status_code}"
    search_res = json.loads(response.get('content'))
    results = []
    for item in search_res.get('items'):
        link = item.get("link")
        title = item.get("title")
        snippet = item.get("snippet")
        results.append({"title": title, "snippet":snippet, "url": link})
    return json.dumps(results, ensure_ascii=False)


@fc_register("tool")
def visit_url(url: str) -> str:
    """
    使用这个工具来浏览一个网页的详细内容。记住，当你搜索到一些相关网站时，不要只满足于网站的简介，一定要使用这个工具浏览相关网站的详细内容。

    Args:
        url (str): The URL of the webpage to visit.
    """
    import requests
    from bs4 import BeautifulSoup
    LOG.info(f"[tool - Visit URL] Visiting URL '{url}'...")
    try:
        response = requests.get(url, timeout=10)
    except Exception as e:
        return f"Error: Failed to fetch URL. Exception: {e}"

    if response.status_code != 200:
        return f"Error: Received status code {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")

    main_tag = soup.find("main")
    if main_tag:
        text = main_tag.get_text(separator="\n", strip=True)
        if text:
            return text

    article_tag = soup.find("article")
    if article_tag:
        text = article_tag.get_text(separator="\n", strip=True)
        if text:
            return text

    body = soup.find("body")
    if body:
        for element in body(["script", "style"]):
            element.decompose()
        text = body.get_text(separator="\n", strip=True)
        if text:
            return text

    text = soup.get_text(separator="\n", strip=True)
    return text