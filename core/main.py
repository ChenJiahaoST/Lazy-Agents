import asyncio
from dotenv import load_dotenv

load_dotenv()

import lazyllm
from core.flow.deep_research import create_deep_research_pipeline


async def main():
    deep_research_ppl = create_deep_research_pipeline()
    question = input("Lazy Deep Research Demo...\nPlease enter your question：\n")
    if lazyllm.FileSystemQueue().size() > 0:
        lazyllm.FileSystemQueue().clear()
    lazyllm.globals._init_sid()
    all_process = ""
    with lazyllm.ThreadPoolExecutor(1) as executor:
        future = executor.submit(deep_research_ppl, question)
        while True:
            if value := lazyllm.FileSystemQueue().dequeue():
                print("".join(value))
                all_process += "".join(value)
            elif future.done():
                break
            else:
                await asyncio.sleep(0.3)
        log_filename = "all_process.log"
        with open(log_filename, "w", encoding="utf-8") as f:
            f.write(all_process)
        print(f"结果已保存至 {log_filename}")

if __name__ == "__main__":
    asyncio.run(main())