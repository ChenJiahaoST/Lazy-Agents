import os
import sys
import time
from pathlib import Path

__dir__ = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
sys.path.extend([p.as_posix() for p in Path(__dir__).parents])

import lazyllm
from lazyllm import OnlineChatModule, LOG, ThreadPoolExecutor, FileSystemQueue, Color
from lazyllm.tools.agent.functionCall import StreamResponse

from core.prompt.search_prompt import WEB_SEARCH_INSTRUCTION
from core.tools.web_tools import web_search, visit_url
from core.agent.agent import CustomReactAgent


def create_search_agent() -> CustomReactAgent:
    agent = CustomReactAgent(
        llm=OnlineChatModule(source="qwen", model="qwen-plus", stream=False),
        tools=["web_search", "visit_url"],
        custom_prompt=WEB_SEARCH_INSTRUCTION,
        max_retries=20,
        return_trace=True,
        stream=True
    )
    return agent


def create_search_agent_and_run(query: str) -> str:
    try:
        with lazyllm.pipeline() as ppl:
            ppl.receive = StreamResponse('[Searcher] Received query:', prefix_color=Color.red,
                                         color=Color.magenta, stream=True)
            ppl.run_search = CustomReactAgent(
                llm=OnlineChatModule(source="qwen", model="qwen-plus", stream=False),
                tools=["web_search", "visit_url"],
                custom_prompt=WEB_SEARCH_INSTRUCTION,
                max_retries=20,
                return_trace=True,
                stream=True
            )
            ppl.search_result = StreamResponse('[Searcher] Search result:', prefix_color=Color.red,
                                         color=Color.magenta, stream=True)
        return ppl(query)
    except Exception as e:
        LOG.error(f"[Search agent] Error occurred: {e}")
        return "搜索中断，未找到相关信息"
    
def test():
    search_agent = create_search_agent()
    with ThreadPoolExecutor(max_workers=1) as executor:
        f = executor.submit(search_agent, "## 文化影响与行业意义\n讨论游戏对国产3A游戏产业的推动作用，对中国传统文化IP的商业化探索，以及对全球玩家对中国游戏认知的改变。需结合行业研究报告、文化评论文章及开发者采访。")
        while True:
            if value := FileSystemQueue().dequeue():
                print("".join(value))
            elif f.done():
                break
            else:
                time.sleep(0.5)

# test()