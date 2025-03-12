from dotenv import load_dotenv

load_dotenv()

from core.flow.deep_research import create_deep_research_pipeline


def main():
    deep_research_ppl = create_deep_research_pipeline()
    question = input("Lazy Deep Research Demo...\nPlease enter your question：\n")
    result = deep_research_ppl(question)
    
    print("结果：", result)

if __name__ == "__main__":
    main()