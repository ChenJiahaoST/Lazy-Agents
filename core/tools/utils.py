import datetime
import json

from lazyllm import LOG

# 获取今天的日期
def get_today_date():
    """
    获取今天的日期

    Returns:
        str: 当前日期，格式为"YYYY-MM-DD"
    """
    today = datetime.date.today()
    return today.strftime("%Y-%m-%d")


def table_of_content_parser(text: str) -> list:
    try:
        # 找到第一个 '[' 和最后一个 ']' 的索引
        start_index = text.find('[')
        end_index = text.rfind(']')
        if start_index == -1 or end_index == -1:
            # 没有找到有效的 JSON 结构，返回空列表
            return []
        json_str = text[start_index:end_index+1]
        # 尝试解析 JSON
        data = json.loads(json_str)
        LOG.info(f"报告写作大纲生成成功：\n{data}")
        return data
    except Exception as e:
        # 如果解析出错，输出错误信息并返回空列表
        print("解析 JSON 出错:", e)
        raise e

    

