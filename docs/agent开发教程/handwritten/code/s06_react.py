"""s06 ReAct：事件系统 + 手写 ReAct 循环（Agent 的心脏）。

运行：python s06_react.py

ReAct = Reasoning + Acting：模型在循环里交替「思考 → 调工具 → 看结果」，
直到它不再请求工具。本脚本先看事件流（模型调用的内部视角），
再手写一个最小 ReAct 循环，最后看一次多步任务跑完的完整轨迹。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _fake_llm import FakeClient

from agent.events import Event
from agent.model import Model
from agent.session import Session
from agent.tool import registry
from agent.tool import builtin as builtin_tools

# 准备一个待读写的演示文件（系统临时目录）
import tempfile
demo_dir = tempfile.mkdtemp(prefix="agent-s06-")
notes = os.path.join(demo_dir, "notes.txt")
summary = os.path.join(demo_dir, "summary.txt")
with open(notes, "w", encoding="utf-8", newline="") as f:
    f.write("会话要只追加不修改；上下文要保留思维链；工具异常要回给模型。")

for t in (builtin_tools.read_file, builtin_tools.write_file):
    registry.register(t)

# ------------------------------------------------------------------
# 1) 事件流：一次流式调用的内部视角
# ------------------------------------------------------------------
print("== 1. 一次调用的完整事件序列 ==")
client = FakeClient([
    {"match": "读取 notes.txt",
     "resp": {"reasoning": "用户要我读文件，先调用 read_file。",
              "tool_calls": [{"name": "read_file", "arguments": {"filepath": notes}}]}},
    {"match": "notes.txt", "resp": {"content": "notes.txt 的内容已读取，共 3 条要点。"}},
])
model = Model(client=client)
events_seen: list[str] = []


def recorder(event: str, **data) -> None:
    events_seen.append(event)


for e in (Event.REASONING_START, Event.REASONING, Event.REASONING_END,
          Event.CONTENT_START, Event.CONTENT, Event.CONTENT_END,
          Event.TOOL_CALL_START, Event.TOOL_CALL, Event.TOOL_CALL_END):
    model.on(e, recorder)

s = Session()
s.add_message({"role": "user", "content": "读取 notes.txt"})
model.invoke(s, stream=True)
print(" -> ".join(events_seen))

# ------------------------------------------------------------------
# 2) 最小 ReAct 循环：Agent 的全部秘密就这么几行
# ------------------------------------------------------------------
print("\n== 2. 手写 ReAct 循环：读文件 → 写摘要 → 汇报 ==")


def tool_text(msgs):
    return " ".join(m.get("content") or "" for m in msgs if m.get("role") == "tool")


client2 = FakeClient([
    {   # 第 1 轮：读文件
        "match": "并总结",
        "resp": {"tool_calls": [{"name": "read_file", "arguments": {"filepath": notes}}]}},
    {   # 第 2 轮：拿到文件内容后写摘要
        "match": lambda msgs: "会话要只追加不修改" in tool_text(msgs),
        "resp": {"tool_calls": [{"name": "write_file",
                                 "arguments": {"filepath": summary,
                                               "content": "核心：历史只追加、保留思维链、异常回给模型。"}}]}},
    {   # 第 3 轮：写入成功后汇报
        "match": lambda msgs: "已写入" in tool_text(msgs),
        "resp": {"content": "已把 3 条要点写进 summary.txt：历史只追加、保留思维链、异常回给模型。"}},
])
model2 = Model(client2)
session = Session()
session.tools = registry.schemas()

session.add_message({"role": "user", "content": f"读取 {notes} 并总结，把摘要写到 {summary}"})

rounds = 0
while True:
    rounds += 1
    model2.invoke(session, stream=True)
    call_msg = registry.invoke(session.messages[-1])
    if call_msg is None:
        break  # 模型不再请求工具：任务完成
    session.messages.extend(call_msg)
    print(f"第 {rounds} 轮：执行 {', '.join(m['name'] for m in call_msg)}")

print(f"循环共 {rounds} 轮结束")

# ------------------------------------------------------------------
# 3) 轨迹回放：print_friendly 就是 Agent 的「行车记录仪」
# ------------------------------------------------------------------
print("\n== 3. 完整轨迹 ==")
session.print_friendly()
print(f"\nsummary.txt 内容: {open(summary, encoding='utf-8').read()}")
