# -*- coding: utf-8 -*-
"""第 7 章示例：工具、运行时上下文注入与错误处理。

演示四件事：
  1. @tool 的 docstring 与类型注解如何变成模型看到的 schema
  2. ToolRuntime 注入：工具里怎么读到 state / context / store
  3. 工具返回 Command —— 直接修改图状态（v1 的新写法）
  4. 工具抛异常时，用 wrap_tool_call 把它变成模型能读懂的 ToolMessage

运行：python 04_tools.py
"""

import sys
from dataclasses import dataclass
from typing import Any, Callable, TypedDict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, show, tool_call
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langchain.tools.tool_node import ToolCallRequest
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command


# ---------------------------------------------------------------------------
# 1. 普通工具：docstring 就是工具描述，类型注解就是参数 schema
# ---------------------------------------------------------------------------
@tool
def search_orders(query: str, limit: int = 5) -> str:
    """按关键词搜索订单。

    Args:
        query: 搜索关键词
        limit: 最多返回多少条
    """
    return f"找到 {limit} 条与「{query}」相关的订单"


print("=" * 72)
print("① 工具的 schema 从哪来")
print("=" * 72)
print(f"  工具名（取自函数名）: {search_orders.name}")
print(f"  工具描述（取自 docstring）: {search_orders.description!r}")
print(f"  参数 schema: {search_orders.args_schema.model_json_schema()['properties'].keys()}")
print("  → 模型看到的就只有这三样东西；docstring 写得含糊，模型就会选错工具。")


# ---------------------------------------------------------------------------
# 2. ToolRuntime：工具里的「后门」
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("② ToolRuntime：工具里读取 state / context / store")
print("=" * 72)


class MyState(AgentState):
    """自定义状态：多一个 user_name 字段。"""

    user_name: str


@dataclass
class Ctx:
    tenant_id: str


@tool
def inspect_runtime(runtime: ToolRuntime[Ctx, MyState]) -> str:
    """读取运行时上下文并回报（runtime 参数对模型隐藏）。"""
    history = len(runtime.state["messages"])
    tenant = runtime.context.tenant_id
    runtime.store.put(("audit",), "last_call", {"tenant": tenant})
    hit = runtime.store.get(("audit",), "last_call")
    return f"历史 {history} 条 | tenant={tenant} | store 回读={hit.value}"


rt_agent = create_agent(
    model=ScriptedChatModel(
        script=[tool_call("inspect_runtime", {}, "c1"), reply("已读取运行时上下文。")]
    ),
    tools=[inspect_runtime],
    state_schema=MyState,
    context_schema=Ctx,
    store=InMemoryStore(),
)
out = rt_agent.invoke(
    {"messages": [{"role": "user", "content": "看看上下文"}]},
    context=Ctx(tenant_id="t-7"),
)
for msg in out["messages"]:
    if type(msg).__name__ == "ToolMessage":
        print(f"  工具返回值: {msg.content}")
print("  → runtime 参数对模型不可见：模型只看到工具名和描述，不会看到 user_id 之类的东西。")
print("  → 旧写法 InjectedState / InjectedStore / get_runtime() 在 v1 已由 runtime 统一取代。")


# ---------------------------------------------------------------------------
# 3. 工具返回 Command：直接改图状态
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("③ 工具返回 Command：直接修改状态")
print("=" * 72)


@tool
def set_user_name(new_name: str, runtime: ToolRuntime[None, MyState]) -> Command:
    """把用户名字写进会话状态。"""
    return Command(
        update={
            "user_name": new_name,
            # ⚠️ 返回 Command 时**必须**自己补一条 ToolMessage，
            #    否则 ToolNode 会因为找不到对应的 tool_call_id 而抛 ValueError。
            "messages": [
                ToolMessage(
                    content=f"名字已更新为 {new_name}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


cmd_agent = create_agent(
    model=ScriptedChatModel(
        script=[
            tool_call("set_user_name", {"new_name": "小明"}, "c1"),
            reply("记住了。"),
        ]
    ),
    tools=[set_user_name],
    state_schema=MyState,
)
out = cmd_agent.invoke({"messages": [{"role": "user", "content": "我叫小明"}]})
print(f"  最终 state['user_name'] = {out['user_name']!r}")
print("  → 工具不再只能返回字符串：返回 Command 就能顺手改状态，省掉一轮模型调用。")


# ---------------------------------------------------------------------------
# 4. 错误处理：v1 用中间件，不用 ToolException
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("④ 工具出错怎么办：wrap_tool_call 把异常变成 ToolMessage")
print("=" * 72)


@tool
def divide(a: int, b: int) -> str:
    """做整数除法。"""
    return str(a // b)


@wrap_tool_call
def handle_tool_errors(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage],
) -> Any:
    """把工具异常翻译成模型能读懂的失败消息。"""
    try:
        return handler(request)
    except ZeroDivisionError as exc:
        print(f"  [中间件] 捕获到异常：{type(exc).__name__}，转成 ToolMessage")
        return ToolMessage(
            content=f"工具执行失败：{exc}。请换一个参数再试。",
            tool_call_id=request.tool_call["id"],
        )


err_agent = create_agent(
    model=ScriptedChatModel(
        script=[
            tool_call("divide", {"a": 1, "b": 0}, "c1"),
            reply("除数不能为 0，我换个数再算。"),
        ]
    ),
    tools=[divide],
    middleware=[handle_tool_errors],
)
out = err_agent.invoke({"messages": [{"role": "user", "content": "1 除以 0"}]})
show(out["messages"])
print()
print("  对比一下两种做法的后果：")
print("  · 让异常直接抛出去 → 整个 agent 调用崩掉，用户看到 500；")
print("  · 转成 ToolMessage    → 模型读到「失败了，换个参数」，自己纠错继续。")
print()
print("  ⚠️ 注意：v1 已经**不再**使用 ToolException / handle_tool_error 这套旧 API。")
print("     要么像上面这样自己写 wrap_tool_call，要么直接用内置的 ToolErrorMiddleware。")
