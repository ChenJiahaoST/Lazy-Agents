from lazyllm import OnlineChatModule, LOG

from core.prompt.search_prompt import WEB_SEARCH_INSTRUCTION
from core.tools.web_tools import web_search, visit_url
from core.agent.agent import CustomReactAgent


def create_search_agent() -> CustomReactAgent:
    agent = CustomReactAgent(
        llm=OnlineChatModule(source="qwen", model="qwen-plus", stream=False),
        tools=["web_search", "visit_url"],
        custom_prompt=WEB_SEARCH_INSTRUCTION,
        max_retries=20,
        return_trace=True
    )
    return agent


def create_agent_and_run(query: str) -> str:
    try:
        result = create_search_agent()(query)
        return result
    except Exception as e:
        LOG.error(f"[Search agent] Error occurred: {e}")
        return "搜索中断，未找到相关信息"
    
def test():
    search_agent = create_search_agent()
    print(search_agent("## 文化影响与行业意义\n讨论游戏对国产3A游戏产业的推动作用，对中国传统文化IP的商业化探索，以及对全球玩家对中国游戏认知的改变。需结合行业研究报告、文化评论文章及开发者采访。"))
