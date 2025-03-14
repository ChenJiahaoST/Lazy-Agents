import lazyllm
from lazyllm import OnlineChatModule, LOG, Color
from lazyllm.tools.agent.functionCall import StreamResponse

from core.prompt.search_prompt import WEB_SEARCH_INSTRUCTION
from core.tools.web_tools import web_search, visit_url
from core.agent.agent import CustomReactAgent


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