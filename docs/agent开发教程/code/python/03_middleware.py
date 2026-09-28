# -*- coding: utf-8 -*-
"""第 3 章示例：中间件的钩子体系。

本示例做一件文档里没有、但写代码时最需要知道的事：
**把六个钩子在一次含工具调用的完整轮次里的真实触发顺序打出来。**

运行：python 03_middleware.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, tool_call
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    after_agent,
    after_model,
    before_agent,
    before_model,
    wrap_model_call,
    wrap_tool_call,
)
from langchain.tools import tool

TRACE: list[str] = []


@tool
def get_weather(city: str) -> str:
    """查询某个城市的天气。"""
    TRACE.append("        └─ 工具函数体真正执行")
    return f"{city}: 22°C，晴"


# ---------------------------------------------------------------------------
# 六个钩子
# ---------------------------------------------------------------------------
@before_agent
def hook_before_agent(state, runtime):
    TRACE.append("before_agent")


@before_model
def hook_before_model(state, runtime):
    TRACE.append("before_model")


@after_model
def hook_after_model(state, runtime):
    TRACE.append("after_model")


@after_agent
def hook_after_agent(state, runtime):
    TRACE.append("after_agent")


@wrap_model_call
def hook_wrap_model_call(request, handler):
    TRACE.append("wrap_model_call")
    return handler(request)


@wrap_tool_call
def hook_wrap_tool_call(request, handler):
    TRACE.append("wrap_tool_call")
    return handler(request)


print("=" * 72)
print("六个钩子的真实触发顺序")
print("=" * 72)

agent = create_agent(
    model=ScriptedChatModel(
        script=[
            tool_call("get_weather", {"city": "上海"}, "c1"),
            reply("上海 22°C，晴。"),
        ]
    ),
    tools=[get_weather],
    middleware=[
        hook_before_agent,
        hook_before_model,
        hook_after_model,
        hook_after_agent,
        hook_wrap_model_call,
        hook_wrap_tool_call,
    ],
)
agent.invoke({"messages": [{"role": "user", "content": "上海天气？"}]})

for i, line in enumerate(TRACE, 1):
    print(f"  {i:>2}. {line}")

print()
print("  读法：")
print("  · before_agent / after_agent 包住**整个** agent 调用，各只触发一次；")
print("  · before_model → wrap_model_call → after_model 是**每一次**模型调用都走一遍；")
print("  · 轮次里出现了两次 before_model，因为这一轮调了两次模型")
print("    （第一次决定调工具，第二次拿到工具结果后给最终答案）；")
print("  · wrap_tool_call 只在工具执行时出现一次，且夹在两次模型调用之间。")


# ---------------------------------------------------------------------------
# 用 wrap_model_call 拦截并改写模型请求
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("wrap_* 钩子能改写请求：动态切换模型")
print("=" * 72)

SWITCH_LOG: list[str] = []


class SwitchModelMiddleware(AgentMiddleware):
    """长上下文时换用「更强」的模型——真实项目里常见的成本/质量权衡。"""

    def __init__(self, cheap, strong, threshold=8):
        super().__init__()
        self.cheap = cheap
        self.strong = strong
        self.threshold = threshold

    def wrap_model_call(self, request, handler):
        n = len(request.state["messages"])
        if n > self.threshold:
            SWITCH_LOG.append(f"消息数 {n} > {self.threshold} → 换用强模型")
            return handler(request.override(model=self.strong))
        SWITCH_LOG.append(f"消息数 {n} ≤ {self.threshold} → 用便宜模型")
        return handler(request)


mw = SwitchModelMiddleware(
    cheap=ScriptedChatModel(script=[reply("便宜模型的回答")]),
    strong=ScriptedChatModel(script=[reply("强模型的回答")]),
    threshold=2,
)
sw_agent = create_agent(model=mw.cheap, tools=[], middleware=[mw])
out = sw_agent.invoke({"messages": [{"role": "user", "content": "问题一"}]})
print(f"  第一次调用：{SWITCH_LOG[-1]}")
print(f"  最终回复：{out['messages'][-1].content!r}")

out = sw_agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "问题一"},
            {"role": "assistant", "content": "答案一"},
            {"role": "user", "content": "问题二"},
        ]
    }
)
print(f"  第二次调用：{SWITCH_LOG[-1]}")
print(f"  最终回复：{out['messages'][-1].content!r}")
print("  → request.override(model=...) 是官方推荐的「换模型」写法；")
print("    直接改 request.model 也能跑，但 override 会保留链上其它中间件的语义。")
