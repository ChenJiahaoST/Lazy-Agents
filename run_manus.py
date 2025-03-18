import asyncio
from dotenv import load_dotenv

load_dotenv()

import lazyllm
from lazyllm import OnlineChatModule

from core.agent import Manus


async def main():
    question = input("Lazy Manus Demo...\nPlease enter your task：\n")
    lazyllm.globals._init_sid()
    with lazyllm.ThreadPoolExecutor(1) as executor:
        agent = Manus(
            plan_llm=OnlineChatModule(source="qwen", model="qwen-plus", stream=False),
            solve_llm=OnlineChatModule(source="qwen", model="qwen-plus", stream=False),
            return_trace=True,
            stream=False,
            max_retries=10
        )
        future = executor.submit(agent, question)
        while True:
            if value := lazyllm.FileSystemQueue().dequeue():
                print("".join(value))
            elif future.done():
                break
            else:
                await asyncio.sleep(0.3)

if __name__ == "__main__":
    asyncio.run(main())