"""s04 tools：不封装直接用——手动拼 Schema、手动执行、手动回填。

运行：python s04_tools.py

看清 tool calling 的完整裸流程之后，下一章的封装才不是魔法：
1. 把工具的 JSON Schema 放进请求的 tools 字段；
2. 模型不执行工具，它只「点菜」：返回 tool_calls（名字 + JSON 参数）；
3. 执行与否、怎么执行，完全是客户端自己的事；
4. 执行结果以 role=tool 消息回填，tool_call_id 对得上即可。
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _fake_llm import FakeClient

from agent.model import Model
from agent.session import Session

# 演示用目录（系统临时目录，不污染工程）
demo_dir = tempfile.mkdtemp(prefix="agent-s04-")
uv_md = os.path.join(demo_dir, "uv.md")

# ------------------------------------------------------------------
# 1) 定义两个普通函数——模型看不见它们，只能看见 Schema
# ------------------------------------------------------------------


def read_file(filepath: str) -> str:
    """读取文件内容并以字符串形式返回"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filepath: str, content: str) -> None:
    """将内容写入文件"""
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        f.write(content)


# ------------------------------------------------------------------
# 2) 手动拼 JSON Schema（下一章把这个苦力活自动化）
# ------------------------------------------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string",
                                 "description": "文件的绝对路径，或相对于cwd的路径"},
                },
                "required": ["filepath"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string",
                                 "description": "文件的绝对路径，或相对于cwd的路径"},
                    "content": {"type": "string",
                                "description": "要写入的内容，该内容会完全覆盖文件原本内容"},
                },
                "required": ["filepath", "content"],
            },
        },
    },
]

client = FakeClient([
    {
        "match": "新建一个 uv.md",
        "resp": {
            "tool_calls": [{"name": "write_file",
                            "arguments": {"filepath": uv_md,
                                          "content": "# UV 安装教程\n\nUV 是一个用 Rust 编写的极速 Python 包管理器。"}}],
        },
    },
    {"match": "uv.md", "resp": {"content": "已创建 uv.md，内容是 UV 安装教程的一句话简介。"}},
])
model = Model(client=client)

session = Session()
session.tools = tools  # 绑定工具：放进请求的 tools 字段
session.add_message({"role": "user", "content": "请在临时目录新建一个 uv.md 文件，写入 UV 的安装教程。直接新建就好"})

# ------------------------------------------------------------------
# 3) 第一次调用：模型「点菜」（请求工具，但不执行）
# ------------------------------------------------------------------
resp = model.invoke(session)
print("== 1. 模型返回的原始响应（注意 tool_calls 与 finish_reason）==")
print(json.dumps({
    "finish_reason": resp.raw["choices"][0]["finish_reason"],
    "message": resp.message,
}, ensure_ascii=False, indent=2))

# ------------------------------------------------------------------
# 4) 手动执行：从 tool_calls 里抠出名字和参数，自己想办法找到函数
# ------------------------------------------------------------------
msg = session.messages[-1]
tc = msg["tool_calls"][0]
print("\n== 2. 手动执行（演示原始做法）==")
print("tool id :", tc["id"])
print("tool name:", tc["function"]["name"])
print("arguments:", tc["function"]["arguments"])

func = globals().get(tc["function"]["name"])  # agent-core 课件里的原始做法
if callable(func):
    arguments = json.loads(tc["function"]["arguments"])
    func(**arguments)
    print(f"-> 已执行 {func.__name__}，文件已生成")
# 这个做法的问题：函数必须定义在本模块 globals 里；名字对不上就静默失败；
# 参数没有校验；异常直接炸。下一章逐一解决。

# ------------------------------------------------------------------
# 5) 回填：role=tool 的消息，tool_call_id 必须对应
# ------------------------------------------------------------------
session.messages.append({
    "role": "tool",
    "tool_call_id": tc["id"],
    "name": tc["function"]["name"],
    "content": "已写入文件",
})

# ------------------------------------------------------------------
# 6) 第二次调用：模型看到工具结果，给出最终回答
# ------------------------------------------------------------------
resp2 = model.invoke(session)
print("\n== 3. 回填后的最终回答 ==")
print(resp2.message["content"])

print("\n== 4. 完整消息序列 ==")
session.print_friendly()
