from lazyllm import OnlineChatModule

from core.prompt.planner_prompt import TOC_PLAN_INSTRUCTION
from core.tools.web_tools import web_search, visit_url
from core.tools.plan_tools import get_more_info_from_user
from core.agent.agent import CustomReactAgent


def create_plan_agent() -> CustomReactAgent:
    agent = CustomReactAgent(
        llm=OnlineChatModule(source="qwen", model="qwen-plus", stream=False),
        tools=["get_more_info_from_user", "web_search", "visit_url"],
        custom_prompt=TOC_PLAN_INSTRUCTION,
        max_retries=10,
        return_trace=True,
        stream=True
    )
    return agent
