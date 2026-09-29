# -*- coding: utf-8 -*-
"""第 15 章示例：规划与委派。

演示四件事：
  1. write_todos：任务列表长什么样、存在状态哪里
  2. subagents 参数：怎么定义子代理，SubAgent 有哪些字段
  3. task 工具：主代理如何把活派出去
  4. mode='isolated' 与 mode='fork' 的区别（子代理能看见什么）

运行：python 11_delegation.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, tool_call
from deepagents import SubAgent, create_deep_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.messages import HumanMessage


# ---------------------------------------------------------------------------
# 1. write_todos
# ---------------------------------------------------------------------------
print("=" * 78)
print("① write_todos：规划能力长什么样")
print("=" * 78)

TODOS = [
    {"content": "读需求文档", "status": "completed"},
    {"content": "设计数据模型", "status": "in_progress"},
    {"content": "写接口", "status": "pending"},
]
agent = create_deep_agent(
    model=ScriptedChatModel(script=[tool_call("write_todos", {"todos": TODOS}, "t1"), reply("计划已建。")]),
    middleware=[TodoListMiddleware()],
)
out = agent.invoke(
    {"messages": [HumanMessage("帮我规划一下")]},
    config={"configurable": {"thread_id": "todo-1"}},
)
print("  状态里的 todos：")
for item in out["todos"]:
    mark = {"completed": "✅", "in_progress": "🔄", "pending": "⬜"}[item["status"]]
    print(f"    {mark} {item['content']}  ({item['status']})")
print()
print("  write_todos 是**全量覆盖**语义：模型每次都要把整张表重新写一遍，")
print("  而不是「追加一条」。所以状态里的 todos 永远是最新的一张完整表。")
print("  ⚠️ 这也意味着：模型忘掉一条，那条就真的没了——规划列表不是 append-only。")


# ---------------------------------------------------------------------------
# 2 & 3. subagents 与 task 工具
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("② 定义子代理：SubAgent 的字段")
print("=" * 78)

researcher = SubAgent(
    name="researcher",
    description="负责查资料。当需要外部信息时派给它。",  # ← 主代理靠这句话决定要不要派活
    system_prompt="你是调研员，只负责查资料并给出结论，不要改任何文件。",
    tools=[],
)
print("  SubAgent 的实测字段：")
for field in (
    "name",
    "description",
    "system_prompt",
    "tools",
    "model",
    "middleware",
    "interrupt_on",
    "skills",
    "permissions",
    "response_format",
    "mode",
):
    print(f"    · {field}")
print()
print(f"  name        = {researcher['name']!r}")
print(f"  description = {researcher['description']!r}")
print("  ⚠️ description 是子代理能不能被用上的**唯一依据**——")
print("     主代理看到的只有 name + description，它靠这句话判断该不该派活。")
print("     官方文档列了 name/description/system_prompt/tools/model/middleware，")
print("     实测还有 interrupt_on / skills / permissions / response_format / mode，")
print("     共 11 个字段——按实测为准。")

print()
print("=" * 78)
print("③ task 工具：主代理把活派出去")
print("=" * 78)

m_boss = ScriptedChatModel(
    script=[
        tool_call("task", {"description": "查一下 LangGraph 的检查点机制", "subagent_type": "researcher"}, "c1"),
        reply("调研完成，结论如下……"),
    ]
)
boss = create_deep_agent(model=m_boss, subagents=[researcher])

out = boss.invoke(
    {"messages": [HumanMessage("帮我调研一下检查点机制")]},
    config={"configurable": {"thread_id": "delegate-1"}},
)
print(f"  主代理暴露的工具里有 task 吗：{'task' in m_boss.last_bound_tool_names()}")
for msg in out["messages"]:
    if type(msg).__name__ == "ToolMessage":
        print(f"  [task 返回] {str(msg.content)[:100]}")
print()
print("  task 的返回是**一份最终报告**，不是子代理的完整对话——")
print("  子代理的中间过程留在它自己的上下文里，主代理只拿到结论。")


# ---------------------------------------------------------------------------
# 4. mode
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("④ mode='isolated' 与 mode='fork'：子代理能看见什么")
print("=" * 78)

print("  isolated（默认）  子代理拿到**干净的上下文**：只有你派给它的那段任务描述。")
print("                    适合：任务自包含、只需要一句话就能说清。")
print()
print("  fork              子代理**继承主代理当前的对话历史**，再叠加任务描述。")
print("                    适合：任务需要主代理已经积累的上下文才能做对。")
print()
print("  取舍：")
print("    isolated 上下文干净、省 token，但你要把背景写全；")
print("    fork     不用重复背景，但子代理的上下文一开始就很长，")
print("             隔离带来的收益被削掉一部分。")
print()
print("  ⚠️ 子代理的价值是**上下文隔离**，不是「多几个模型并行跑」。")
print("     如果任务之间需要频繁来回对齐，拆子代理反而更慢——")
print("     路由开销 + 交接时的上下文损失，这两项经常被低估。")
