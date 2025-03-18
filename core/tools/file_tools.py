import os

from lazyllm.tools import fc_register


@fc_register("tool")
def file_manager(path: str, content: str="", action: str="w") -> str:
    """
    该工具用于对文件系统进行操作，支持文件的创建、读取、修改、删除等操作，
    且所有操作均限定在工程目录下的 output 文件夹内。

    Args:
        path (str): 文件相对于工程目录下 output 文件夹的路径，例如 "filename.txt" 或 "subdir/filename.txt"。
        content (str, optional): 要写入的内容（仅在写入或修改时使用）。
        action (str): 操作类型，支持：
            "w": 写入（覆盖）文件，
            "a": 追加内容到文件，
            "r": 读取文件内容，
            "d": 删除文件。
    """

    output_dir = './output'
    # 如果 output 目录不存在，则创建它
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = os.path.join(output_dir, path)

    if action == "r":
        if not os.path.exists(file_path):
            return f"读取失败：文件 {file_path} 不存在。"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"读取失败：{str(e)}"
    elif action in ["w", "a"]:
        mode = action  # "w"表示覆盖写入，"a"表示追加
        try:
            # 如果文件所在目录不存在，则自动创建目录结构
            file_dir = os.path.dirname(file_path)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            with open(file_path, mode, encoding="utf-8") as f:
                f.write(content)
            return f"操作成功：文件已{'覆盖' if action == 'w' else '追加'}。"
        except Exception as e:
            return f"写入失败：{str(e)}"
    elif action == "d":
        if not os.path.exists(file_path):
            return f"删除失败：文件 {file_path} 不存在。"
        try:
            os.remove(file_path)
            return "删除成功。"
        except Exception as e:
            return f"删除失败：{str(e)}"
    else:
        return "不支持的操作。"
    
    
    