# -*- coding: utf-8 -*-
"""第 11 章示例：LangGraph 的图与状态。

演示九件事：
  1. State schema 与 reducer —— 默认覆盖 vs Annotated 合并
  2. 同一线程再次 invoke 时，两种字段的不同命运
  3. 条件边：按状态决定下一步去哪
  4. Send：从一条边派发 N 个并行分支（map-reduce）
  5. Overwrite：绕过 reducer 强制覆盖
  6. add_sequence 与静态扇入：多起点边会等所有起点完成
  7. 循环与 recursion_limit：默认上限、GraphRecursionError、RemainingSteps
  8. 节点级容错：RetryPolicy、async timeout、CachePolicy
  9. Functional API：用 @entrypoint / @task 写同一类工作流

运行：python 11_state_graph.py
"""

import asyncio
import operator
import sys
from typing import Annotated, TypedDict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.cache.memory import InMemoryCache
from langgraph.errors import GraphRecursionError, NodeTimeoutError
from langgraph.func import entrypoint, task
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.managed import RemainingSteps
from langgraph.types import CachePolicy, Overwrite, RetryPolicy, Send


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


# ---------------------------------------------------------------------------
# 6. 顺序与静态扇入
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("⑥ add_sequence 与静态扇入：顺序、并行汇合")
print("=" * 78)


class Flow(TypedDict):
    trail: Annotated[list[str], operator.add]


def seq_a(state: Flow) -> dict:
    return {"trail": ["a"]}


def seq_b(state: Flow) -> dict:
    return {"trail": ["b"]}


sequence = (
    StateGraph(Flow)
    .add_sequence([seq_a, seq_b])
    .add_edge(START, "seq_a")
    .add_edge("seq_b", END)
    .compile()
)
print(f"  add_sequence([a, b]) → {sequence.invoke({'trail': []})['trail']}")


def left(state: Flow) -> dict:
    return {"trail": ["left"]}


def right(state: Flow) -> dict:
    return {"trail": ["right"]}


def join(state: Flow) -> dict:
    return {"trail": [f"join<-{','.join(sorted(state['trail']))}"]}


fan_in = (
    StateGraph(Flow)
    .add_node("left", left)
    .add_node("right", right)
    .add_node("join", join)
    .add_edge(START, "left")
    .add_edge(START, "right")
    .add_edge(["left", "right"], "join")
    .add_edge("join", END)
    .compile()
)
print(f"  静态扇入 START→left/right→join → {fan_in.invoke({'trail': []})['trail']}")
print("  → add_edge([a, b], 'join') 的含义是「等 a、b 都完成后再跑 join」；")
print("    Python 侧一次传 list 即可，TS 侧同样是 addEdge(['left','right'], 'join')。")


# ---------------------------------------------------------------------------
# 7. 循环与递归上限
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("⑦ 循环与 recursion_limit：本机默认 10007")
print("=" * 78)


class Loop(TypedDict):
    n: int


def inc(state: Loop) -> dict:
    return {"n": state["n"] + 1}


def keep_going(state: Loop) -> str:
    return "inc" if state["n"] < 3 else END


loop = (
    StateGraph(Loop)
    .add_node("inc", inc)
    .add_edge(START, "inc")
    .add_conditional_edges("inc", keep_going, {"inc": "inc", END: END})
    .compile()
)
print(f"  循环到 n>=3 自动退出 → {loop.invoke({'n': 0})}")

try:
    loop.invoke({"n": 0}, {"recursion_limit": 3})
except GraphRecursionError as exc:
    print(f"  recursion_limit=3 → {type(exc).__name__}: {str(exc).splitlines()[0]}")

print("  → 本机 langgraph 1.2.12 的默认上限是 10007（源码核对）；")
print("    讲义/旧文档里的 25、1000、10000 都随版本变化，生产代码请显式传值。")


class StepState(TypedDict):
    n: int
    remaining_steps: RemainingSteps


def report_steps(state: StepState) -> dict:
    print(f"  节点看到的 remaining_steps = {state['remaining_steps']}")
    return {"n": state["n"] + 1}


step_graph = (
    StateGraph(StepState)
    .add_node("report", report_steps)
    .add_edge(START, "report")
    .add_edge("report", END)
    .compile()
)
print(f"  recursion_limit=5 时 → {step_graph.invoke({'n': 0}, {'recursion_limit': 5})}")
print("  → RemainingSteps 是 LangGraph 注入的 managed 值：进入节点时还剩几步；")
print("    Python 侧从 langgraph.managed 导入；JS 1.4.17 没有同名导出（差异已登记）。")


# ---------------------------------------------------------------------------
# 8. 节点级容错与缓存
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("⑧ RetryPolicy / async timeout / CachePolicy")
print("=" * 78)

attempts = {"n": 0}


def flaky(state: Loop) -> dict:
    attempts["n"] += 1
    if attempts["n"] < 3:
        raise ValueError("boom")
    return {"n": 1}


retry_graph = (
    StateGraph(Loop)
    .add_node(
        "flaky",
        flaky,
        retry_policy=RetryPolicy(max_attempts=3, initial_interval=0.01, jitter=False, retry_on=ValueError),
    )
    .add_edge(START, "flaky")
    .add_edge("flaky", END)
    .compile()
)
print(f"  RetryPolicy(max_attempts=3) → {retry_graph.invoke({'n': 0})}，实际尝试 {attempts['n']} 次")


async def slow(state: Loop) -> dict:
    await asyncio.sleep(0.2)
    return {"n": 1}


timeout_graph = (
    StateGraph(Loop)
    .add_node("slow", slow, timeout=0.05)
    .add_edge(START, "slow")
    .add_edge("slow", END)
    .compile()
)
try:
    asyncio.run(timeout_graph.ainvoke({"n": 0}))
except NodeTimeoutError as exc:
    print(f"  async 节点 timeout=0.05s → {type(exc).__name__}: {str(exc).split(' (elapsed')[0]}")

print("  ⚠️ 同步节点不能设 timeout：compile() 会直接抛 ValueError（Python 无法安全取消同步执行），")
print("     所以示例用 async 节点；这条不是配置问题，是运行时限制。")

runs = {"n": 0}


def pure(state: Loop) -> dict:
    runs["n"] += 1
    return {"n": state["n"] + 1}


cache_graph = (
    StateGraph(Loop)
    .add_node("pure", pure, cache_policy=CachePolicy(ttl=60))
    .add_edge(START, "pure")
    .add_edge("pure", END)
    .compile(cache=InMemoryCache())
)
cache_graph.invoke({"n": 1})
cache_graph.invoke({"n": 1})
print(f"  同一输入调用两次 CachePolicy(ttl=60) → 节点实际执行 {runs['n']} 次")
print("  → 只缓存「纯节点」；有副作用（写库、发消息、扣款）的节点不要开缓存。")


# ---------------------------------------------------------------------------
# 9. Functional API
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("⑨ Functional API：@entrypoint / @task")
print("=" * 78)


@task
def add_one(x: int) -> int:
    return x + 1


@task
def triple(x: int) -> int:
    return x * 3


@entrypoint()
def pipeline(x: int) -> int:
    a = add_one(x).result()
    b = triple(a).result()
    return b


print(f"  @entrypoint 串行：3 → add_one → triple = {pipeline.invoke(3)}")


@entrypoint()
def fan_tasks(x: int) -> int:
    f1 = add_one(x)
    f2 = triple(x)
    return f1.result() + f2.result()


print(f"  两个 @task 并行后汇总：(3+1) + (3×3) = {fan_tasks.invoke(3)}")
print("  → Graph API 用节点/边描述形状；Functional API 用普通函数调用描述同一件事。")
print("    需要可视化、中断、子图时优先 Graph API；逻辑本身就是一条函数链时 Functional 更直接。")
