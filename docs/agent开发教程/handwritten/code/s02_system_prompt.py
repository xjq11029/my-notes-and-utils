"""s02 系统提示词：让模型「带着设定」工作，并用模板注入运行环境。

运行：python s02_system_prompt.py

要点：
- 系统提示词放在所有消息最前面，训练时被重点对待；
- 编写五原则：精简 / 自洽 / 全局约束 / 保持静态 / 结构化；
- 动态环境信息（cwd、os、is_git）用 Jinja2 模板在启动时渲染一次。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _fake_llm import FakeClient

from agent.model import Model
from agent.prompt import render_prompt
from agent.session import Session

# ------------------------------------------------------------------
# 1) 渲染系统提示词：模板 + 环境变量
# ------------------------------------------------------------------
system_prompt = render_prompt()
print("== 1. 渲染后的系统提示词 ==")
print(system_prompt)

# ------------------------------------------------------------------
# 2) 带着系统提示词对话
# ------------------------------------------------------------------
client = FakeClient([
    {
        "match": "目前在哪个目录",
        "resp": {"content": "当前工作目录是 D:\\ProjectCode\\my-notes-and-utils\\docs\\agent开发教程\\handwritten\\code。"},
    },
    {
        "match": "你好",
        "resp": {"content": "你好"},
    },
])
model = Model(client=client)

session = Session(system_prompt=system_prompt)
session.add_message({"role": "user", "content": "目前在哪个目录？"})
resp = model.invoke(session, stream=True)
session.add_message({"role": "user", "content": "你好"})
resp = model.invoke(session, stream=True)

print("\n== 2. 系统提示词的「精简」反例 vs 正例（同一意图）==")
bad = ("你现在要充当一名专业代码顾问，接下来我会向你提出各种各样和编程相关的问题。"
       "希望你认真仔细地阅读我每一次发送过来的内容，充分理解我的诉求之后，再进行回答。"
       "回答的时候尽量清晰易懂，方便我进行理解。如果遇到不清楚的内容，千万不要随意编造答案。")
good = "你是代码顾问。精准解答编程问题，不懂直接说明，禁止编造信息。"
print(f"反例（{len(bad)} 字）: {bad[:40]}…")
print(f"正例（{len(good)} 字）: {good}")

print("\n== 3. 检视：系统提示词在 messages 里的位置 ==")
print(json.dumps(model.client.calls[0]["messages"][0], ensure_ascii=False)[:120] + "…")
