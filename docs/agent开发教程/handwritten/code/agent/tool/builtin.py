"""内置工具：读文件 / 写文件 / 执行命令。

只定义不注册——由示例脚本或 Agent 显式 registry.register()，
让「注册」这个动作始终可见。
"""
import subprocess

from agent.tool import tool


@tool(filepath="文件的绝对路径，或相对于当前工作目录的路径")
def read_file(filepath: str) -> str:
    """读取文件内容并以字符串形式返回"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


@tool(filepath="文件的绝对路径，或相对于当前工作目录的路径",
      content="要写入的完整内容，会覆盖文件原有内容")
def write_file(filepath: str, content: str) -> str:
    """把内容写入文件（覆盖写）"""
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    return f"已写入 {filepath}（{len(content)} 字符）"


@tool(command="要执行的 shell 命令")
def bash_command(command: str) -> str:
    """执行一条 shell 命令并返回输出（30 秒超时）"""
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=30,
    )
    output = ((result.stdout or "") + (result.stderr or "")).strip()
    return output or f"（命令执行完成，退出码 {result.returncode}）"
