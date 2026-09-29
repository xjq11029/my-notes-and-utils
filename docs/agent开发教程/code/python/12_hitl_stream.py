# -*- coding: utf-8 -*-
"""第 12 章示例：人在回路与流式输出。

演示四件事：
  1. interrupt() / Command(resume=...) 的完整往返
  2. **恢复时整个节点从头重跑** —— 这是理解一切人在回路坑的钥匙
  3. stream_mode 各档投影分别给你什么
  4. agent 作为子图时，不加 subgraphs=True 就拿不到 token

运行：python 08_hitl_stream.py
"""

import sys
from typing import TypedDict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, tool_call
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


# ---------------------------------------------------------------------------
# 1 & 2. interrupt / resume
# ---------------------------------------------------------------------------
print("=" * 78)
print("① interrupt / resume 的完整往返")
print("=" * 78)

SIDE_EFFECTS: list[str] = []


class Order(TypedDict):
    amount: int
    status: str


def charge(state: Order) -> dict:
    """真实场景里这里会扣款——所以必须人工审批后才能过。"""
    SIDE_EFFECTS.append(f"调用扣款接口：{state['amount']} 元")
    return {"status": "已扣款"}


def approval(state: Order) -> Command:
    # ⚠️ 注意这一行：恢复时它会被**再执行一次**
    SIDE_EFFECTS.append(f"节点开始，读到 amount={state['amount']}")
    decision = interrupt(
        {
            "question": f"确认扣款 {state['amount']} 元？",
            "amount": state["amount"],
        }
    )
    if decision:
        return Command(goto="charge")
    return Command(goto="cancelled")


def cancelled(state: Order) -> dict:
    return {"status": "已取消"}


hitl = (
    StateGraph(Order)
    .add_node("approval", approval)
    .add_node("charge", charge)
    .add_node("cancelled", cancelled)
    .add_edge(START, "approval")
    .add_edge("charge", END)
    .add_edge("cancelled", END)
    .compile(checkpointer=InMemorySaver())
)
cfg = {"configurable": {"thread_id": "order-1"}}

print("  第一次 invoke（会停在 interrupt）：")
r1 = hitl.invoke({"amount": 199, "status": "待审批"}, cfg)
for itr in r1["__interrupt__"]:
    print(f"    __interrupt__ = {itr.value}")
print(f"    此时状态：{hitl.get_state(cfg).values}")
print(f"    待执行节点 next = {hitl.get_state(cfg).next}")

print()
print("  第二次 invoke（用 Command(resume=True) 恢复）：")
r2 = hitl.invoke(Command(resume=True), cfg)
print(f"    最终状态：{r2}")

print()
print("  副作用日志（看清「节点从头重跑」这件事）：")
for i, line in enumerate(SIDE_EFFECTS, 1):
    print(f"    {i}. {line}")
print()
print("  ⚠️ 看到没——「节点开始，读到 amount=199」出现了**两次**：")
print("     恢复不是从中断那一行继续，而是把整个节点**从头再执行一遍**。")
print("     所以 interrupt() 之前的代码必须是幂等的；")
print("     真正的副作用（扣款）要放到 interrupt() **之后**的节点里——")
print("     就像本示例把 charge 单独拆成一个节点那样。")


# ---------------------------------------------------------------------------
# 3. stream_mode
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("② stream_mode：同一张图，七种投影")
print("=" * 78)


class Talk(TypedDict):
    n: int
    note: str


def step(state: Talk) -> dict:
    writer = get_stream_writer()
    writer(f"进度：正在处理第 {state['n'] + 1} 步")  # 自定义事件
    return {"n": state["n"] + 1, "note": f"第 {state['n'] + 1} 步完成"}


talk = (
    StateGraph(Talk)
    .add_node("step", step)
    .add_edge(START, "step")
    .add_edge("step", END)
    .compile(checkpointer=InMemorySaver())
)
s_cfg = {"configurable": {"thread_id": "stream-1"}}

for mode in ("values", "updates", "custom", "debug"):
    chunks = list(talk.stream({"n": 0, "note": ""}, s_cfg, stream_mode=mode))
    if mode == "debug":
        shown = [c.get("type") for c in chunks]
    elif mode == "custom":
        shown = chunks
    else:
        shown = chunks
    print(f"  stream_mode={mode!r:<10} → {shown}")

print()
print("  各档给你的东西：")
print("    values  每步之后的**完整状态**（体积最大，但最省心）")
print("    updates 每步节点返回的**增量**（带节点名，适合做进度条）")
print("    custom  节点里用 get_stream_writer() 主动推的事件（适合推「第 3/10 步」）")
print("    debug   checkpoints + tasks 的合并，信息最多")
print("  另有：messages（LLM 逐 token，最常用于打字机效果）、")
print("        checkpoints / tasks（需要 checkpointer）")


# ---------------------------------------------------------------------------
# 4. agent 作为子图时的流式坑
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("③ 坑：agent 放进父图当子图后，stream_mode='messages' 就收不到 token 了")
print("=" * 78)


@tool
def lookup(q: str) -> str:
    """查一下。"""
    return f"{q} 的结果"


sub_agent = create_agent(
    model=ScriptedChatModel(script=[tool_call("lookup", {"q": "x"}, "c1"), reply("查完了。")]),
    tools=[lookup],
)
parent = (
    StateGraph(dict)
    .add_node("agent", sub_agent)
    .add_edge(START, "agent")
    .add_edge("agent", END)
    .compile()
)


def describe(chunks: list, tagged: bool) -> list[str]:
    """把流出来的分块翻译成人能读的行。"""
    lines = []
    for chunk in chunks:
        if tagged:
            ns, (msg, meta) = chunk
            where = f"ns={ns[0].split(':')[0] if ns else '()'}"
        else:
            msg, meta = chunk
            where = "ns=()"
        lines.append(f"{where} node={meta.get('langgraph_node')} [{type(msg).__name__}] {str(msg.content)[:20]!r}")
    return lines


direct = list(
    sub_agent.stream({"messages": [{"role": "user", "content": "查 x"}]}, stream_mode="messages")
)
wrapped = list(
    parent.stream({"messages": [{"role": "user", "content": "查 x"}]}, stream_mode="messages")
)
tagged = list(
    parent.stream(
        {"messages": [{"role": "user", "content": "查 x"}]},
        stream_mode="messages",
        subgraphs=True,
    )
)

print(f"  A. 直接 stream 子 agent —— {len(direct)} 个分块，内部消息一览无余：")
for line in describe(direct, tagged=False):
    print(f"       {line}")

print()
print(f"  B. 父图 stream，**不加** subgraphs=True —— {len(wrapped)} 个分块：")
for line in describe(wrapped, tagged=False):
    print(f"       {line}")
print("       ↑ 只剩「输入」和「最终答案」两条，模型内部的 token 全没了")

print()
print(f"  C. 父图 stream，**加** subgraphs=True —— {len(tagged)} 个分块：")
for line in describe(tagged, tagged=True):
    print(f"       {line}")
print("       ↑ 分块带上了 namespace，能区分「这是哪个子图吐出来的」")

print()
print("  ⚠️ 因为 create_agent 返回的是**已编译的图**，把它当节点加进父图，它就变成了子图。")
print("     子图的内部输出默认不透传——这就是「图能跑、结果也对，")
print("     但打字机效果莫名其妙没了」的原因。要透传就显式加 subgraphs=True。")
print()
print("  ⚠️ 别把这里的「分块个数」当结论：本示例用的是假模型，")
print("     它一次吐一条完整消息，不是逐 token 吐——所以个数不可比。")
print("     真正要看的是**哪几条消息能看见**：A 能看到子图内部全部消息，")
print("     B 只剩进出两条，C 恢复了内部消息并额外标出它来自哪个子图。")
