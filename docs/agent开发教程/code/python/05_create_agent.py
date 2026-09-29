# -*- coding: utf-8 -*-
"""第 5 章示例：create_agent 与 Agent Loop。

演示四件事：
  1. 一次工具调用的完整往返（Human → AI(tool_call) → ToolMessage → AI(final)）
  2. AgentState 的 messages 只追加
  3. thread_id（对话作用域）与 context（单次运行作用域）的区别
  4. 结构化输出 response_format

运行：python 02_create_agent.py
"""

import sys
from dataclasses import dataclass
from typing import TypedDict

from pydantic import BaseModel, Field

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, show, tool_call
from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langgraph.checkpoint.memory import InMemorySaver


# ---------------------------------------------------------------------------
# 一个普通工具：模型只能看到 city 参数
# ---------------------------------------------------------------------------
@tool
def get_weather(city: str) -> str:
    """查询某个城市的天气。"""
    return f"{city}: 22°C，晴"


print("=" * 72)
print("① 一次工具调用的完整往返")
print("=" * 72)

agent = create_agent(
    model=ScriptedChatModel(
        script=[
            tool_call("get_weather", {"city": "上海"}, "call_1"),
            reply("上海 22°C，晴。"),
        ]
    ),
    tools=[get_weather],
)
result = agent.invoke({"messages": [{"role": "user", "content": "上海天气怎么样？"}]})
show(result["messages"])
print("\n  模型从没执行过工具——它只输出「请调用 get_weather」；")
print("  真正执行并把结果写回上下文的是框架的 tools 节点。")


# ---------------------------------------------------------------------------
# 状态只追加：同一个 thread_id 再问一次，历史是累加的
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("② AgentState.messages 只追加（append-only）")
print("=" * 72)

chat = create_agent(
    model=ScriptedChatModel(script=[reply("你好，我是脚本模型。"), reply("你刚才说你叫小明。")]),
    tools=[],
    checkpointer=InMemorySaver(),
)
cfg = {"configurable": {"thread_id": "chat-1"}}

first = chat.invoke({"messages": [{"role": "user", "content": "你好，我叫小明。"}]}, cfg)
print(f"  第 1 轮后，历史里有 {len(first['messages'])} 条消息")

second = chat.invoke({"messages": [{"role": "user", "content": "我叫什么？"}]}, cfg)
print(f"  第 2 轮后，历史里有 {len(second['messages'])} 条消息（不是 2 条）")
show(second["messages"])
print("\n  注意：第二次 invoke 传进去的那条消息是被**追加**进去的，")
print("  而不是替换掉旧历史——这就是 messages 字段的 add_messages reducer 在起作用。")


# ---------------------------------------------------------------------------
# thread_id vs context
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("③ thread_id（对话作用域）与 context（单次运行作用域）")
print("=" * 72)


class UserContext(TypedDict):
    user_id: str


@tool
def whoami(runtime: ToolRuntime[UserContext]) -> str:
    """返回当前调用的用户 ID（参数对模型隐藏）。"""
    return f"user_id={runtime.context['user_id']}"


ctx_agent = create_agent(
    model=ScriptedChatModel(script=[tool_call("whoami", {}, "c1"), reply("已确认身份。")]),
    tools=[whoami],
    context_schema=UserContext,
    checkpointer=InMemorySaver(),
)
out = ctx_agent.invoke(
    {"messages": [{"role": "user", "content": "我是谁？"}]},
    config={"configurable": {"thread_id": "ctx-1"}},
    context={"user_id": "u-42"},
)
for msg in out["messages"]:
    if type(msg).__name__ == "ToolMessage":
        print(f"  工具看到的 context：{msg.content}")
print("  → thread_id 决定「这段历史属于哪次对话」，会被写进检查点；")
print("  → context 是「这一次运行」的随身数据，不写进检查点，也不进消息历史。")


# ---------------------------------------------------------------------------
# 结构化输出
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("④ 结构化输出：response_format")
print("=" * 72)


class Weather(BaseModel):
    """天气查询结果。"""

    city: str = Field(description="城市名")
    temp_c: int = Field(description="摄氏度温度")


struct_agent = create_agent(
    model=ScriptedChatModel(script=[tool_call("Weather", {"city": "上海", "temp_c": 22}, "s1")]),
    tools=[],
    response_format=Weather,
)
out = struct_agent.invoke({"messages": [{"role": "user", "content": "上海天气？"}]})
print(f"  type(result['structured_response']) = {type(out['structured_response']).__name__}")
print(f"  result['structured_response'] = {out['structured_response']!r}")
print("  → 拿到的是**已校验的 Pydantic 实例**，不是字符串，不用自己解析 JSON。")
