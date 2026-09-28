# -*- coding: utf-8 -*-
"""第 13 章示例：可观测与评测。

本示例用**离线回调**搭出一棵 trace 树，把「一次 agent 调用产生了哪些 span」
这件事讲清楚——因为 LangSmith 上报需要账号，本机无法实测。

演示三件事：
  1. 一次 agent 调用会产生哪些嵌套的 run（这就是 trace 的结构）
  2. 每个 run 上能拿到什么元数据（类型、耗时、输入输出）
  3. 离线评测的最小骨架：跑用例 → 判定 → 汇总

运行：python 13_observability.py
"""

import sys
import time
import uuid

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, tool_call
from langchain.agents import create_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langchain.tools import tool


# ---------------------------------------------------------------------------
# 1 & 2. trace 树
# ---------------------------------------------------------------------------
class TraceRecorder(BaseCallbackHandler):
    """把 run 的开始 / 结束记下来，还原成一棵树。

    LangSmith 做的事和这里本质相同：给每个 run 记 start / end / 父子关系 / 元数据，
    只是它把数据送到服务端，并且跨进程、跨服务也能串起来。
    """

    def __init__(self) -> None:
        self.runs: dict[str, dict] = {}
        self.roots: list[str] = []

    def _start(self, run_id, parent_run_id, name, run_type) -> None:
        self.runs[run_id] = {
            "name": name,
            "type": run_type,
            "parent": parent_run_id,
            "children": [],
            "t0": time.perf_counter(),
            "t1": None,
        }
        if parent_run_id is None:
            self.roots.append(run_id)
        elif parent_run_id in self.runs:
            self.runs[parent_run_id]["children"].append(run_id)

    def _end(self, run_id) -> None:
        if run_id in self.runs:
            self.runs[run_id]["t1"] = time.perf_counter()

    def on_chain_start(self, serialized, inputs, **kw):
        # 链节点的名字优先看 serialized（LangGraph 会写 'LangGraph' 之类），
        # 再看 run_name，最后兜底
        name = (serialized or {}).get("name") or kw.get("name") or "chain"
        self._start(kw.get("run_id"), kw.get("parent_run_id"), name, "chain")

    def on_chain_end(self, outputs, **kw):
        self._end(kw.get("run_id"))

    def on_chat_model_start(self, serialized, messages, **kw):
        name = (serialized or {}).get("name") or "ChatModel"
        self._start(kw.get("run_id"), kw.get("parent_run_id"), name, "llm")

    def on_llm_end(self, response, **kw):
        self._end(kw.get("run_id"))

    def on_tool_start(self, serialized, input_str, **kw):
        # ⚠️ 工具名在 serialized['name'] 里，不在 kw 里——这里踩过一次
        name = (serialized or {}).get("name") or kw.get("name") or "tool"
        self._start(kw.get("run_id"), kw.get("parent_run_id"), name, "tool")

    def on_tool_end(self, output, **kw):
        self._end(kw.get("run_id"))

    def tree(self) -> str:
        lines: list[str] = []

        def walk(run_id: str, depth: int) -> None:
            r = self.runs[run_id]
            ms = (r["t1"] - r["t0"]) * 1000 if r["t1"] else 0.0
            lines.append(f"{'  ' * depth}├─ [{r['type']:<5}] {r['name']}  ({ms:.1f} ms)")
            for child in r["children"]:
                walk(child, depth + 1)

        for root in self.roots:
            walk(root, 0)
        return "\n".join(lines)


@tool
def get_price(sku: str) -> str:
    """查商品价格。"""
    return f"{sku}: 199 元"


print("=" * 78)
print("① 一次 agent 调用产生的 trace 树")
print("=" * 78)

recorder = TraceRecorder()
agent = create_agent(
    model=ScriptedChatModel(
        script=[tool_call("get_price", {"sku": "A-1"}, "c1"), reply("A-1 卖 199 元。")]
    ),
    tools=[get_price],
)
agent.invoke(
    {"messages": [HumanMessage("A-1 多少钱？")]},
    config={"callbacks": [recorder], "run_name": "price_lookup"},
)

print(recorder.tree())
print()
print(f"  共 {len(recorder.runs)} 个 run，根节点 {len(recorder.roots)} 个")
print()
print("  结构读法：")
print("    chain  ── 整次 agent 调用（对应 LangSmith 里的一个 trace）")
print("      └ chain ── 图里的 model 节点")
print("          └ llm ── 真正那次模型请求")
print("      └ chain ── 图里的 tools 节点")
print("          └ tool ── 真正那次工具执行")
print()
print("  ⚠️ 每个 run 都有自己的 input / output，所以「第几次模型调用说了什么」")
print("     是可以逐层下钻看到的——这就是能查清「agent 为什么走了这一步」的原因。")
print("     没有 trace 的话，你只能看到最终答案，中间过程是个黑盒。")


# ---------------------------------------------------------------------------
# 3. 离线评测骨架
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("② 离线评测的最小骨架")
print("=" * 78)

CASES = [
    {"input": "A-1 多少钱？", "expect_tool": "get_price", "expect_in_reply": "199"},
    {"input": "B-2 多少钱？", "expect_tool": "get_price", "expect_in_reply": "199"},
    {"input": "你好", "expect_tool": None, "expect_in_reply": "你好"},
]


def build_agent(case: dict):
    """按用例预期构造一个「正确」的脚本模型（真实评测里这里换成真模型）。"""
    script = []
    if case["expect_tool"]:
        script.append(tool_call(case["expect_tool"], {"sku": "X"}, "c1"))
    script.append(reply(case["expect_in_reply"] if case["expect_tool"] else "你好，有什么可以帮你？"))
    return create_agent(model=ScriptedChatModel(script=script), tools=[get_price])


passed = 0
print(f"  {'#':<3} {'用例':<14} {'调用的工具':<14} {'判定'}")
print("  " + "-" * 52)
for i, case in enumerate(CASES, 1):
    rec = TraceRecorder()
    a = build_agent(case)
    out = a.invoke(
        {"messages": [HumanMessage(case["input"])]},
        config={"callbacks": [rec], "configurable": {"thread_id": f"eval-{i}"}},
    )
    called = sorted({r["name"] for r in rec.runs.values() if r["type"] == "tool"})
    actual_tool = called[0] if called else None
    final = str(out["messages"][-1].content)
    ok = actual_tool == case["expect_tool"] and case["expect_in_reply"] in final
    passed += ok
    print(
        f"  {i:<3} {case['input']:<14} {str(actual_tool):<14} {'✅ 通过' if ok else '❌ 失败'}"
    )

print()
print(f"  结果：{passed}/{len(CASES)} 通过")
print()
print("  评测的两个层次（别只做第一层）：")
print("    ① 结果对不对 —— 最终答案是否满足预期（本例做的就是这层）")
print("    ② 过程对不对 —— 工具选得对不对、调了几次、有没有绕路")
print("       第二层才是 agent 评测和普通 LLM 评测的分水岭：")
print("       答案碰对了但过程全错，换个输入就会崩。")
print()
print("  ⚠️ 本示例的「判定」是字符串匹配，只是骨架。真实项目里判定器本身也要评测——")
print("     用 LLM 当裁判会引入位置偏差、冗长偏差、自我偏好、风格偏差四类系统性问题。")


# ---------------------------------------------------------------------------
# 成本与延迟
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("③ 该盯哪几个数")
print("=" * 78)
print("  ┌────────────────┬──────────────────────────────────────────────┐")
print("  │ 指标           │ 为什么盯它                                    │")
print("  ├────────────────┼──────────────────────────────────────────────┤")
print("  │ 模型调用次数   │ agent 的成本基本正比于它；失控循环也看这个    │")
print("  │ 输入 token     │ 每轮都要重发完整历史，涨得比你想的快          │")
print("  │ 缓存命中率     │ 命中与否，单价可能差一个数量级                │")
print("  │ 工具调用次数   │ 工具选错 / 反复重试，看这里最直观             │")
print("  │ 端到端 P95     │ 平均延迟掩盖长尾，而用户体验由长尾决定        │")
print("  └────────────────┴──────────────────────────────────────────────┘")
print()
print("  ⚠️ 本示例的 trace 是离线回调，只记了耗时；token 与成本字段需要真实模型")
print("     返回的 usage 元数据，本机无 API Key，未实测——以官方文档为准。")
