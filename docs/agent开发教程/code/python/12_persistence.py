# -*- coding: utf-8 -*-
"""第 12 章示例：持久化与持久执行。

演示五件事：
  1. checkpointer 让「同一线程」的第二次调用接着上次的状态跑
  2. get_state / get_state_history —— 看清检查点长什么样
  3. update_state —— 时间旅行：改历史再重放
  4. Store —— 跨线程的长期记忆（与 checkpointer 的分工）
  5. Store 的命名空间与前缀搜索语义

运行：python 12_persistence.py
"""

import sys
from typing import TypedDict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.store.memory import InMemoryStore


class Counter(TypedDict):
    n: int
    trail: list[str]


def step(state: Counter) -> dict:
    n = state["n"] + 1
    return {"n": n, "trail": [*state.get("trail", []), f"step→{n}"]}


builder = StateGraph(Counter).add_node("step", step).add_edge(START, "step").add_edge("step", END)


# ---------------------------------------------------------------------------
# 1 & 2. 检查点
# ---------------------------------------------------------------------------
print("=" * 78)
print("① checkpointer：同一线程接着上次跑")
print("=" * 78)

graph = builder.compile(checkpointer=InMemorySaver())
cfg = {"configurable": {"thread_id": "order-2026"}}

r1 = graph.invoke({"n": 0, "trail": []}, cfg)
print(f"  第 1 次，输入 {{n:0, trail:[]}}      → n={r1['n']}, trail={r1['trail']}")

r2 = graph.invoke({}, cfg)
print(f"  第 2 次，输入 {{}}（从检查点续跑）  → n={r2['n']}, trail={r2['trail']}")

r3 = graph.invoke(None, cfg)
print(f"  第 3 次，输入 None（空操作）        → n={r3['n']}, trail={r3['trail']}")

r4 = graph.invoke({"n": 100}, cfg)
print(f"  第 4 次，输入 {{n:100}}（覆盖 n）    → n={r4['n']}, trail={r4['trail']}")
print()
print("  读法（这里是本示例最容易搞错的一处，实测确认）：")
print("  · `invoke({}, cfg)` —— 空字典：图从检查点状态**重新执行**，n 从 1 变 2；")
print("  · `invoke(None, cfg)` —— None：**空操作**。已跑完的线程没有待执行任务，")
print("    直接返回当前状态，图一步都没跑（n 仍是 2）；")
print("  · 第 4 次输入里给了 n=100，按默认 reducer 覆盖掉检查点里的 2，再 +1 得 101；")
print("  · trail 一直在长，因为输入里从没给过 trail，它一直沿用检查点里的值。")

print()
print("  状态快照（get_state）：")
snap = graph.get_state(cfg)
print(f"    values = {snap.values}")
print(f"    next   = {snap.next}    ← 空元组表示已跑完，没有待执行节点")
print(f"    config = {snap.config['configurable']}")

print()
print("  检查点历史（get_state_history）：")
history = list(graph.get_state_history(cfg))
print(f"    共 {len(history)} 个检查点：")
for i, s in enumerate(reversed(history)):
    print(f"      [{i}] step={s.metadata.get('step'):>2}  n={s.values.get('n')}  next={s.next}")


# ---------------------------------------------------------------------------
# 3. 时间旅行
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("③ update_state：改写历史再重放（时间旅行）")
print("=" * 78)

snapshots = list(graph.get_state_history(cfg))
print("  快照序号示意（get_state_history 返回顺序：新 → 旧，取下标要用负数）：")
for i, s in enumerate(snapshots):
    print(f"      snapshots[{i:>2}]（倒数第 {len(snapshots) - i}）  step={s.metadata.get('step'):>2}  n={s.values.get('n')}")
# 挑一个中间检查点（从最早往回数第 2 个）
target = snapshots[-2]
print(f"  选中的历史检查点：snapshots[-2] → step={target.metadata.get('step')}, n={target.values.get('n')}")
forked = graph.update_state(target.config, {"n": 100, "trail": ["人工改写：从 100 开始"]})
print(f"  改写后的新分支 config：{forked['configurable']['checkpoint_id'][:20]}...")
replayed = graph.invoke(None, forked)
print(f"  重放结果：n = {replayed['n']}, trail = {replayed['trail']}")
print("  → update_state 会**新建一个分支**，原线程的历史不受影响。")
print("    这是调试 agent 的利器：把某一步的状态改一改，看后面会怎么走。")

print()
print("  ③-bis 三节点链（bump → double → tag）：回到中间某步、重走后面**两步**")
print("  （单节点图重放只有一步，看不出来「时间旅行」——多节点才能看出「跳回中间」）")


def bump(state: Counter) -> dict:
    n = state["n"] + 1
    return {"n": n, "trail": [*state.get("trail", []), f"bump→{n}"]}


def double(state: Counter) -> dict:
    n = state["n"] * 2
    return {"n": n, "trail": [*state.get("trail", []), f"double→{n}"]}


def tag(state: Counter) -> dict:
    return {"trail": [*state.get("trail", []), "tag✓"]}


chain = (StateGraph(Counter).add_node("bump", bump).add_node("double", double).add_node("tag", tag)
         .add_edge(START, "bump").add_edge("bump", "double").add_edge("double", "tag").add_edge("tag", END)
         .compile(checkpointer=InMemorySaver()))
cfg2 = {"configurable": {"thread_id": "chain-demo"}}
base = chain.invoke({"n": 1, "trail": []}, cfg2)
print(f"    原始执行：n = {base['n']}, trail = {base['trail']}")

chain_snaps = list(chain.get_state_history(cfg2))
mid = next(s for s in chain_snaps if s.next == ("double",))   # bump 之后、double 之前的快照
print(f"    选中中间快照（next={mid.next}，即 bump 刚跑完）：n = {mid.values.get('n')}")
forked2 = chain.update_state(mid.config, {"n": 10, "trail": ["人工改写：n=10"]})
re2 = chain.invoke(None, forked2)
print(f"    从该点重放（重走 double、tag 两步）：n = {re2['n']}, trail = {re2['trail']}")
print("    → 只重走了 double→tag 两步，bump 没有重跑；原线程 chain-demo 的历史不受影响。")


# ---------------------------------------------------------------------------
# 4 & 5. Store：跨线程长期记忆
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("④ Store：跨线程的长期记忆（与 checkpointer 的分工）")
print("=" * 78)

store = InMemoryStore()
USER = ("alice", "memories")

store.put(USER, "pref-food", {"text": "喜欢川菜"})
store.put(USER, "pref-city", {"text": "住在杭州"})
store.put(("alice", "notes"), "note-1", {"text": "上周开会提到 Q3 目标"})

print(f"  store.get(('alice','memories'), 'pref-food') → {store.get(USER, 'pref-food').value}")

print()
print("  前缀搜索的坑（search 的 namespace_prefix 是**前缀**匹配，不是精确匹配）：")
hits = store.search(("alice",))
print(f"    store.search(('alice',)) 命中 {len(hits)} 条：")
for item in hits:
    print(f"      namespace={item.namespace}  key={item.key}  value={item.value}")

print()
print(f"  只想要 memories 这一层：store.search(('alice','memories')) → "
      f"{[i.key for i in store.search(USER)]}")
print(f"  列出命名空间：store.list_namespaces(prefix=('alice',)) → {store.list_namespaces(prefix=('alice',))}")
print("  → 一旦数据多了，把命名空间写细（('alice','memories') 而不是 ('alice',)）能省掉不少误命中。")

print()
store.delete(USER, "pref-city")                      # 删除单个键
print(f"  store.delete(USER, 'pref-city') 后再 search → "
      f"{[i.key for i in store.search(USER)]}   ← pref-city 没了")

print()
print("=" * 78)
print("checkpointer 与 store 的分工")
print("=" * 78)
print("  ┌──────────────┬────────────────────────┬──────────────────────────┐")
print("  │              │ Checkpointer           │ Store                    │")
print("  ├──────────────┼────────────────────────┼──────────────────────────┤")
print("  │ 作用范围     │ 单个线程（thread）     │ 跨线程                   │")
print("  │ 存什么       │ 图状态的完整快照       │ 应用自定义的键值数据     │")
print("  │ 怎么取       │ 传 thread_id           │ 节点里用 runtime.store   │")
print("  │ 典型用途     │ 对话延续 / 人在回路 /  │ 用户偏好 / 长期事实 /    │")
print("  │              │ 时间旅行 / 故障恢复    │ 共享知识                 │")
print("  └──────────────┴────────────────────────┴──────────────────────────┘")
print()
print("  ⚠️ 生产环境别用 InMemorySaver / InMemoryStore —— 进程一重启就全没了。")
print("     持久化检查点需另装：pip install langgraph-checkpoint-sqlite（本地）")
print("     或 langgraph-checkpoint-postgres（生产）。")
