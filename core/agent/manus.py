import os
import sys
from pathlib import Path

__dir__ = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
sys.path.extend([p.as_posix() for p in Path(__dir__).parents])

from typing import List

from lazyllm.tools.agent import PlanAndSolveAgent
from lazyllm.module import ModuleBase
from lazyllm import loop, pipeline, _0, package, bind, LOG, Color, ChatPrompter, OnlineChatModule

from core.tools import (
    json_list_parser,
    web_search,
    visit_url,
    python_executor,
    file_manager)
from core.agent.agent import CustomReactAgent
from core.prompt.planner_prompt import MANUS_PLAN_INSTRUCTION
from core.prompt.solver_prompt import MANUS_SOLVER_INPUT, MANUS_SOLVER_INSTRUCTION


class Manus(PlanAndSolveAgent):
    PLAN_PROMPT = MANUS_PLAN_INSTRUCTION
    SOLVE_SYSTEM_PROMPT = MANUS_SOLVER_INSTRUCTION
    SOLVE_INPUT_PROMPT = MANUS_SOLVER_INPUT
    memory = []

    def __init__(self, plan_llm, solve_llm, max_retries: int = 5, return_trace: bool = False, stream: bool = False):
        ModuleBase.__init__(self, return_trace=return_trace)
        self._max_retries = max_retries
        self._plan_llm = plan_llm.share(prompt=ChatPrompter(instruction=self.PLAN_PROMPT))
        self._solve_llm = solve_llm.share()
        self._tools = ["web_search", "visit_url", "file_manager", "python_executor"]
        self._return_trace = return_trace
        self._stream = stream
        self._build_agent_ppl()
        
    def _build_agent_ppl(self):
        with pipeline() as self._agent:
            self._agent.plan = self._plan_llm
            self._agent.parse = lambda text: package('', json_list_parser(text))
            with loop(stop_condition=lambda res, steps: len(steps) == 0) as self._agent.lp:
                self._agent.lp.pre_action = self._pre_action
                self._agent.lp.solve = self._give_task_to_solver
                self._agent.lp.post_action = self._post_action | bind(_0, self._agent.lp.input[0][1])

            self._agent.post_action = lambda res, steps: res

    def _pre_action(self, response: str, steps: list):
        query = f"步骤{steps[0]['id']}：{steps[0]['task']}\n具体要求：{steps[0]['desc']}\n"
        LOG.info(f"[Solver] begin\n{query}")
        history = "\n----------\n".join(self.memory[1:]) if len(self.memory) > 1 else "当前没有已完成的步骤"

        result = self.SOLVE_INPUT_PROMPT.format(objective=self.memory[0], previous_steps=history, current_step=query)
        return result

    def _post_action(self, response: str, steps: List[str]):
        last_step = f"步骤{steps[0]['id']}：{steps[0]['task']}\n完成情况：{response}\n"
        LOG.info(f"[Solver] response\n{last_step}")
        self.memory.append(last_step)
        steps.pop(0)
        return package(response, steps)
    
    def _give_task_to_solver(self, task: str):
        solver = CustomReactAgent(
            llm=self._solve_llm.share(),
            tools=self._tools,
            custom_prompt=self.SOLVE_SYSTEM_PROMPT,
            max_retries=self._max_retries,
            return_trace=self._return_trace,
            stream=self._stream
        )
        return solver(task)
    def forward(self, query: str):
        self.memory.append(query)
        return self._agent(query)

# plan_llm = OnlineChatModule(source="qwen", model="qwen-plus", stream=False)
# solve_llm = OnlineChatModule(source="qwen", model="qwen-plus", stream=False)
# tools = ["web_search", "visit_url", "file_manager", "python_executor"]
# manus = Manus(plan_llm, solve_llm, max_retries=10, stream=True)

# manus("调研一下如何用蒸馏技术训练LLM，并做一个ppt")