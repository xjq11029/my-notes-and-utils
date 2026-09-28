# -*- coding: utf-8 -*-
"""第 6 章示例：LangGraph 的图与状态。

演示五件事：
  1. State schema 与 reducer —— 默认覆盖 vs Annotated 合并
  2. 同一线程再次 invoke 时，两种字段的不同命运
  3. 条件边：按状态决定下一步去哪
  4. Send：从一条边派发 N 个并行分支（map-reduce）
  5. Overwrite：绕过 reducer 强制覆盖

运行：python 06_state_graph.py
"""

import operator
import sys
from typing import Annotated, TypedDict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.types import Overwrite, Send


# ---------------------------------------------------------------------------
# 1. reducer：决定「节点返回的更新」如何合并进「当前状态」
# ---------------------------------------------------------------------------
print("=" * 78)
print("① reducer：默认是覆盖，Annotated 才合并")
print("=" * 78)


class State(TypedDict):
    # 没有 Annotated → 默认 reducer = 用新值**覆盖**旧值
    counter: int
    # 有 Annotated[list, operator.add] → 新值**追加**到旧值后面
    log: Annotated[list[str], operator.add]
    # 内置 reducer add_messages → 追加消息，并按消息 ID 去重更新
    messages: Annotated[list, add_messages]


def node_a(state: State) -> dict:
    return {"counter": 1, "log": ["a 跑过"], "messages": [AIMessage(content="a")]}


def node_b(state: State) -> dict:
    return {"counter": 2, "log": ["b 跑过"], "messages": [AIMessage(content="b")]}


g = (
    StateGraph(State)
    .add_node("a", node_a)
    .add_node("b", node_b)
    .add_edge(START, "a")
    .add_edge("a", "b")
    .add_edge("b", END)
    .compile()
)
out = g.invoke({"counter": 0, "log": [], "messages": [HumanMessage("起点")]})
print(f"  counter  = {out['counter']}   ← 两个节点都写过，留下的是**最后一个**")
print(f"  log      = {out['log']}   ← 两个节点的值被**合并**了")
print(f"  messages = {[m.content for m in out['messages']]}")
print("  → 同一个 State 里，不同字段可以有完全不同的合并规则，各管各的。")


# ---------------------------------------------------------------------------
# 2. 同一线程再次 invoke：输入值也走 reducer
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("② 同一线程再次 invoke：输入值按各字段自己的 reducer 合并")
print("=" * 78)

from langgraph.checkpoint.memory import InMemorySaver  # noqa: E402


class Acc(TypedDict):
    n: int  # 默认 reducer = 覆盖
    trail: Annotated[list[str], operator.add]  # 追加


def bump(state: Acc) -> dict:
    n = state["n"] + 1
    return {"n": n, "trail": [f"→{n}"]}


g2 = (
    StateGraph(Acc)
    .add_node("bump", bump)
    .add_edge(START, "bump")
    .add_edge("bump", END)
    .compile(checkpointer=InMemorySaver())
)
cfg = {"configurable": {"thread_id": "t-1"}}

rows = [
    ("第 1 次", {"n": 0, "trail": ["起点"]}),
    ("第 2 次", None),
    ("第 3 次", {}),
    ("第 4 次", {"n": 100}),
    ("第 5 次", {"trail": ["插一条"]}),
]
results = []
for label, inp in rows:
    r = g2.invoke(inp, cfg)
    results.append((label, inp, r))
    print(f"  {label}，输入 {str(inp):<26} → n={r['n']:<4} trail={r['trail']}")

print()
print("  逐行读：")
print("  · 第 1 次：给了 n=0 和 trail，节点 +1 得 n=1")
print("  · 第 2 次：输入是 None —— **空操作**！已跑完的线程没有待执行任务，")
print("            直接返回当前状态，什么都没发生（n 仍是 1）")
print("  · 第 3 次：输入是 {} —— 和 None **不一样**：图会从检查点状态重新执行，")
print("            节点读到检查点里的 n=1，+1 得 2")
print("  · 第 4 次：输入里给了 n=100，按默认 reducer（覆盖）冲掉检查点的 2，再 +1 得 101")
print("  · 第 5 次：输入里只有 trail，n 沿用检查点的 101，节点 +1 得 102；")
print("            trail 有 operator.add，输入值被**追加**而不是替换")
print()
print("  结论（实测口径）：")
print("  ① 输入字典里**出现**的字段 → 按该字段自己的 reducer 合并进检查点状态")
print("  ② 输入字典里**没出现**的字段 → 保留检查点里的值")
print("  ③ `invoke(None, cfg)` 是空操作；`invoke({}, cfg)` 才是「从检查点续跑」")
print("  ⚠️ 第 ①②条很容易踩：以为「同一线程会累积」，结果标量字段被输入悄悄重置。")


# ---------------------------------------------------------------------------
# 3. 条件边
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("③ 条件边：按状态决定下一步去哪")
print("=" * 78)


class Router(TypedDict):
    question: str
    route: str
    answer: str


def classify(state: Router) -> dict:
    q = state["question"]
    return {"route": "weather" if "天气" in q else "math"}


def weather_node(state: Router) -> dict:
    return {"answer": f"[天气分支] {state['question']} → 晴，22°C"}


def math_node(state: Router) -> dict:
    return {"answer": f"[数学分支] {state['question']} → 42"}


def pick(state: Router) -> str:
    return state["route"]


router_graph = (
    StateGraph(Router)
    .add_node("classify", classify)
    .add_node("weather", weather_node)
    .add_node("math", math_node)
    .add_edge(START, "classify")
    .add_conditional_edges("classify", pick, {"weather": "weather", "math": "math"})
    .add_edge("weather", END)
    .add_edge("math", END)
    .compile()
)
for q in ("今天天气怎么样", "1+1 等于几"):
    print(f"  输入 {q!r} → {router_graph.invoke({'question': q})['answer']}")


# ---------------------------------------------------------------------------
# 4. Send：一条边派发 N 个并行分支
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("④ Send：map-reduce 式的并行派发")
print("=" * 78)


class FanState(TypedDict):
    items: list[str]
    results: Annotated[list[str], operator.add]


def split(state: FanState) -> list[Send]:
    """这里返回的是 Send 列表，不是节点名——LangGraph 会为每一项起一个并行任务。"""
    return [Send("worker", {"item": it}) for it in state["items"]]


def worker(state: dict) -> dict:
    it = state["item"]
    return {"results": [f"{it} 处理完毕"]}


fan = (
    StateGraph(FanState)
    .add_node("worker", worker)
    .add_conditional_edges(START, split, ["worker"])
    .add_edge("worker", END)
    .compile()
)
out = fan.invoke({"items": ["a", "b", "c"], "results": []})
print(f"  items   = {out['items']}")
print(f"  results = {out['results']}")
print("  → 三个 worker 在**同一个 super-step** 里并行执行；")
print("    结果靠 results 字段的 operator.add reducer 汇总——这就是 map-reduce。")


# ---------------------------------------------------------------------------
# 5. Overwrite：合并型 reducer 的逃生舱
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("⑤ Overwrite：想清空合并型字段时怎么办")
print("=" * 78)


def reset_log(state: State) -> dict:
    # 直接返回 [] 是**没用的**——operator.add 会把 [] 拼上去，旧值还在
    return {"log": Overwrite([])}


g3 = (
    StateGraph(State)
    .add_node("reset", reset_log)
    .add_edge(START, "reset")
    .add_edge("reset", END)
    .compile()
)
print(f"  不包 Overwrite：log = ['旧值'] + [] = ['旧值']  ← 清不掉")
print(f"  包了 Overwrite：log = {g3.invoke({'counter': 0, 'log': ['旧值'], 'messages': []})['log']}")
print("  → Overwrite 是绕过 reducer 的显式指令，专门用来「我就是要覆盖」。")
