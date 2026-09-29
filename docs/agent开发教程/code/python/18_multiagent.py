# -*- coding: utf-8 -*-
"""第 18 章示例：多智能体协作与从旧版迁移。

演示三件事：
  1. supervisor 拓扑：把 create_agent 建好的 agent 当节点塞进父图
  2. handoff 拓扑：用 Command 把控制权交给另一个 agent
  3. 从 LCEL / AgentExecutor 迁移到 v1 的写法对照

运行：python 14_multiagent.py
"""

import sys
from typing import Annotated, TypedDict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, tool_call
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.types import Command


# ---------------------------------------------------------------------------
# 1. supervisor 拓扑
# ---------------------------------------------------------------------------
print("=" * 78)
print("① supervisor 拓扑：agent 当节点")
print("=" * 78)


@tool
def query_db(sql: str) -> str:
    """查数据库。"""
    return f"[{sql}] → 3 行结果"


@tool
def send_email(to: str) -> str:
    """发邮件。"""
    return f"已发送给 {to}"


db_agent = create_agent(
    model=ScriptedChatModel(script=[tool_call("query_db", {"sql": "select 1"}, "c1"), reply("查到 3 行。")]),
    tools=[query_db],
    name="db_agent",
)
mail_agent = create_agent(
    model=ScriptedChatModel(script=[reply("邮件已发。")]),
    tools=[send_email],
    name="mail_agent",
)


class TopState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str


def supervisor(state: TopState) -> dict:
    """极简路由：真实项目里这里通常是另一个模型调用。"""
    last = str(state["messages"][-1].content)
    return {"route": "mail" if "邮件" in last else "db"}


def pick(state: TopState) -> str:
    return state["route"]


top = (
    StateGraph(TopState)
    .add_node("supervisor", supervisor)
    .add_node("db", db_agent)  # ← 直接把编译好的 agent 当节点
    .add_node("mail", mail_agent)
    .add_edge(START, "supervisor")
    .add_conditional_edges("supervisor", pick, {"db": "db", "mail": "mail"})
    .add_edge("db", END)
    .add_edge("mail", END)
    .compile()
)

for text in ("帮我查一下数据库", "帮我发个邮件"):
    out = top.invoke({"messages": [{"role": "user", "content": text}]})
    print(f"  输入 {text!r:<16} → route={out['route']:<5} 最终回复={out['messages'][-1].content!r}")

print()
print("  ⚠️ create_agent 返回的就是**已编译的图**，所以可以直接 add_node。")
print("     副作用：它变成了子图，流式输出需要 subgraphs=True（见第 8 章示例）。")
print("     记得给每个 agent 起 name=，否则 trace 里分不清是谁在跑。")


# ---------------------------------------------------------------------------
# 2. handoff
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("② handoff 拓扑：用 Command 交棒")
print("=" * 78)


class HandState(TypedDict):
    messages: Annotated[list, add_messages]
    owner: str


def triage(state: HandState) -> Command:
    """接待员：判断该谁处理，然后用 Command(goto=...) 交棒。"""
    text = str(state["messages"][-1].content)
    target = "billing" if "账单" in text else "tech"
    return Command(goto=target, update={"owner": target})


def billing(state: HandState) -> dict:
    return {"messages": [{"role": "assistant", "content": "[账单组] 已处理"}]}


def tech(state: HandState) -> dict:
    return {"messages": [{"role": "assistant", "content": "[技术组] 已处理"}]}


hand = (
    StateGraph(HandState)
    .add_node("triage", triage)
    .add_node("billing", billing)
    .add_node("tech", tech)
    .add_edge(START, "triage")
    .add_edge("billing", END)
    .add_edge("tech", END)
    .compile()
)

for text in ("我要问账单", "系统报错了"):
    out = hand.invoke({"messages": [{"role": "user", "content": text}]})
    print(f"  输入 {text!r:<14} → owner={out['owner']:<8} 回复={out['messages'][-1].content!r}")

print()
print("  supervisor vs handoff 的区别：")
print("    supervisor  有一个「调度者」节点反复决定下一步交给谁，交完还能收回来；")
print("    handoff     交棒后**不回来**，接手的 agent 负责到底——更像「转人工」。")
print("    前者适合需要多轮协调的任务，后者适合一次分流就结束的场景。")


# ---------------------------------------------------------------------------
# 3. 迁移对照
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("③ 从旧版迁移到 v1")
print("=" * 78)

rows = [
    ("建 agent", "AgentExecutor(agent=..., tools=...)", "create_agent(model, tools)"),
    ("调用", "executor.invoke({'input': '...'})", "agent.invoke({'messages': [...]})"),
    ("输入形态", "字符串 input", "消息列表 messages"),
    ("输出形态", "{'output': '...'}", "{'messages': [...]}，取 messages[-1]"),
    ("提示词", "prompt 模板字符串", "system_prompt= + middleware"),
    ("记忆", "memory=ConversationBufferMemory()", "checkpointer + thread_id"),
    ("工具错误", "handle_tool_error / ToolException", "@wrap_tool_call 或 ToolErrorMiddleware"),
    ("运行时注入", "InjectedState / InjectedStore", "runtime: ToolRuntime"),
    ("链式拼装", "LCEL 的 `|` 管道", "StateGraph 的 add_node / add_edge"),
    ("扩展点", "自定义 Agent / 继承", "middleware 的六个钩子"),
]
print(f"  {'能力':<12} {'旧版写法':<38} {'v1 写法'}")
print("  " + "-" * 92)
for cap, old, new in rows:
    print(f"  {cap:<12} {old:<38} {new}")

print()
print("  迁移的心智转变（比记 API 更重要）：")
print("    · 旧版：agent 是一个**组件**，你用 LCEL 把它串进链里；")
print("    · v1 ：agent 是一张**图**，你用节点和边定义控制流，用中间件扩展行为。")
print("    所以「迁移」不是换函数名，而是把控制流从链式表达改成图表达。")
print()
print("  建议顺序：① 先把 AgentExecutor 换成 create_agent（接口迁移，非行为等价）；")
print("            ② 再把 LCEL 的编排改成 StateGraph（这一步才真正动结构）；")
print("            ③ 最后把自定义逻辑收进 middleware。")
print("            一次全改，出了问题分不清是哪一步引入的。")


# ---------------------------------------------------------------------------
# 4. 部署形态
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("④ 部署形态")
print("=" * 78)
print("  托管（Agent Server）")
print("    · 持久化（checkpointer / store）由服务端自动提供，不用自己配")
print("    · 自带 trace、评测、人工审批的 UI")
print("    · 代价：绑定平台，本地调试与线上环境的差异要自己盯")
print()
print("  自托管")
print("    · 自己接 Postgres 做检查点与 Store，自己接观测后端")
print("    · 自由度最高，但「持久化」这件事必须一开始就做对——")
print("      中途从 InMemorySaver 换到 PostgresSaver，历史数据是搬不过去的")
print()
print("  ⚠️ 无论哪种形态，上线前都该确认三件事：")
print("     ① 检查点有没有持久化（进程重启会不会丢会话）")
print("     ② 有没有调用次数上限（模型调用 / 工具调用都要限）")
print("     ③ 高风险操作有没有人在回路（扣款、发邮件、删文件）")
