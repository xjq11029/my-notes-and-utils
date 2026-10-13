"""s05 封装 tools：@tool 装饰器 + Pydantic 动态参数模型 + 注册表。

运行：python s05_tool_package.py

封装目标：定义工具 = 写一个带 docstring 的普通函数 + 装饰器注明参数含义。
Schema 生成、参数校验、异常兜底、注册查找全部自动化。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _fake_llm import FakeClient

from agent.model import Model
from agent.session import Session
from agent.tool import registry, tool
from agent.tool.core import Tool, create_params_model

# ------------------------------------------------------------------
# 1) 动态参数模型：inspect 签名 → Pydantic create_model
# ------------------------------------------------------------------


def write_file(filepath: str, content: str, encoding: str = "utf-8") -> None:
    """将内容写入文件"""
    with open(filepath, "w", encoding=encoding, newline="") as f:
        f.write(content)


param_model = create_params_model(write_file, param_descriptions={
    "filepath": "文件的绝对路径或相对于cwd的路径",
    "content": "待写入的文件内容",
    "encoding": "文件编码",
})
print("== 1. create_params_model 生成的 JSON Schema ==")
import json
print(json.dumps(param_model.model_json_schema(), ensure_ascii=False, indent=2))

# ------------------------------------------------------------------
# 2) Tool 类：schema() 与校验
# ------------------------------------------------------------------
tool_obj = Tool(write_file, param_descriptions={
    "filepath": "文件的绝对路径或相对于cwd的路径",
    "content": "待写入的文件内容",
    "encoding": "文件编码",
})
print("\n== 2. Tool.schema()（OpenAI function calling 格式）==")
print(json.dumps(tool_obj.schema(), ensure_ascii=False, indent=2))

print("\n== 3. 参数校验：类型错误会得到可读的堆栈文本（而不是炸掉程序）==")
err = tool_obj(filepath=12345, content="hi")  # filepath 声明为 str
print(err.splitlines()[-1])

# ------------------------------------------------------------------
# 3) @tool 装饰器 + 注册表
# ------------------------------------------------------------------


@tool(filepath="文件的绝对路径，或相对于当前工作目录的路径")
def read_file(filepath: str) -> str:
    """读取文件内容并以字符串形式返回"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


registry.register(read_file)
registry.register(tool_obj)

print("\n== 4. 注册表：schemas() 交给 session.tools，invoke() 替你执行 ==")
session = Session()
session.tools = registry.schemas()
print("已注册工具:", [s["function"]["name"] for s in session.tools])

client = FakeClient([
    {"match": "帮我读取",
     "resp": {"tool_calls": [{"name": "read_file",
                              "arguments": {"filepath": os.path.join("agent", "prompt", "system.j2")}}]}},
    {"match": "system.j2", "resp": {"content": "system.j2 的开头是角色设定：「你是运行在用户终端里的编码助手」。"}},
])
model = Model(client=client)

session.add_message({"role": "user", "content": "帮我读取 agent/prompt/system.j2 的开头"})
model.invoke(session, stream=True)

results = registry.invoke(session.messages[-1])  # 没有 tool_calls 时返回 None
print("registry.invoke 返回:", json.dumps(results, ensure_ascii=False, indent=2))
session.messages.extend(results)

resp = model.invoke(session, stream=True)
print("\n最终回答:", resp.message["content"])

print("\n== 5. 完整消息序列（注意 role=tool 的消息格式）==")
session.print_friendly()
