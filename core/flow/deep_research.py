import json

import lazyllm
from lazyllm import OnlineChatModule, Color
from lazyllm.tools.agent.functionCall import StreamResponse

from core.prompt.planner_prompt import TOC_PLAN_INSTRUCTION
from core.prompt.write_prompt import REPORT_INSTRUCTION
from core.tools import web_search, visit_url, get_more_info_from_user
from core.tools.utils import table_of_content_parser
from core.agent.agent import CustomReactAgent
from core.agent.searcher_agent import create_search_agent_and_run


def create_deep_research_pipeline():
    with lazyllm.pipeline() as s_ppl:
        s_ppl.gen_query = lambda x: f"{x.get('desc')}\n{x.get('need_know')}"
        s_ppl.search_agent = create_search_agent_and_run
        s_ppl.gen_output = (lambda x, origin_dict: {**origin_dict, "search_info": x}) | lazyllm.bind(origin_dict=s_ppl.input)
    
    with lazyllm.pipeline() as dr_ppl:
        dr_ppl.planner_ins = StreamResponse(prefix="[Planner] Receive instruction:", prefix_color=Color.red, color=Color.magenta, stream=True)
        dr_ppl.planner = CustomReactAgent(
            llm=OnlineChatModule(source="qwen", model="qwen-plus", stream=False),
            tools=["get_more_info_from_user", "web_search", "visit_url"],
            custom_prompt=TOC_PLAN_INSTRUCTION,
            max_retries=10,
            return_trace=True,
            stream=True
        )
        dr_ppl.planner_out = StreamResponse(prefix="[Planner] ToC Completed:", prefix_color=Color.red, color=Color.magenta, stream=True)
        dr_ppl.toc_parser = table_of_content_parser
        dr_ppl.searcher = lazyllm.warp(lambda x: s_ppl(x)).aslist
        dr_ppl.search_parser = lambda x: json.dumps(
            [
                {"title": item.get("title"),
                 "desc": item.get("desc"),
                 "search_info": item.get("search_info")} for item in x
            ], ensure_ascii=False
            )
        dr_ppl.gen_report = OnlineChatModule(source="qwen", model="qwen-plus", stream=True).prompt(
            lazyllm.ChatPrompter(instruction=REPORT_INSTRUCTION)
        )
    return dr_ppl