# -*- coding: utf-8 -*-
"""第 13 章示例：Deep Agents 全景。

演示四件事：
  1. create_deep_agent 默认给你哪些工具（与官方文档的差异在这里显式指出）
  2. 规划能力默认**不开**，要显式加 TodoListMiddleware
  3. 预装中间件栈 —— 打印真实的图节点名
  4. HarnessProfile：声明式地裁掉不要的能力

运行：python 09_deep_agent.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, tool_call
from deepagents import HarnessProfile, create_deep_agent, register_harness_profile
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.messages import HumanMessage


def tool_names(model: ScriptedChatModel) -> list[str]:
    """把 agent 实际暴露给模型的工具名取出来。

    从**模型那一侧**取（`bindTools` 收到的名字），而不是翻图内部的工具表——
    图内部的属性名属于实现细节，换版本就可能变。

    ⚠️ 注意：`bindTools` 是**每次模型调用时**才触发的，不是构造 agent 时。
       所以必须先 invoke 一次，这个列表才非空。
    """
    return model.last_bound_tool_names()


def run_once(agent, thread: str = "probe") -> dict:
    """跑一轮最小对话，让模型至少被调用一次。"""
    return agent.invoke(
        {"messages": [HumanMessage("你好")]},
        config={"configurable": {"thread_id": thread}},
    )


# ---------------------------------------------------------------------------
# 1. 默认工具集
# ---------------------------------------------------------------------------
print("=" * 78)
print("① create_deep_agent 默认给你哪些工具")
print("=" * 78)

m0 = ScriptedChatModel(script=[reply("好的")])
agent0 = create_deep_agent(model=m0)
print(f"  构造完还没 invoke 时：{tool_names(m0)}   ← bindTools 还没触发")
run_once(agent0)
names = tool_names(m0)
print(f"  invoke 一次之后：共 {len(names)} 个")
print(f"  {names}")

node_tools = sorted(agent0.nodes["tools"].bound._tools_by_name.keys())
print()
print(f"  但工具节点里其实有 {len(node_tools)} 个：{node_tools}")
print(f"  差集：{sorted(set(node_tools) - set(names))}")
print()
print("  ⚠️ 这里有个容易搞错的点：**「注册了工具」不等于「模型看得见」**。")
print("     `execute` 挂在工具节点上，但默认后端是 StateBackend（不提供执行能力），")
print("     所以它**没有被绑定给模型**——模型根本不知道有这个工具。")
print("     换句话说：想看 agent 到底能干什么，要看模型被绑定了什么，")
print("     而不是看工具节点里挂了什么。")
print()
print("  模型实际看到的 8 个，按用途分：")
print("    文件读写  ls / read_file / write_file / edit_file / delete")
print("    文件检索  glob / grep")
print("    委派      task（创建子代理）")
print()
print("  ⚠️ 与官方文档的差异（本机实测 deepagents 0.7.18）：")
print("     文档把 write_todos 列为「可选能力，v0.7 起需主动开启」——")
print("     实测确认**默认绑定给模型的工具里确实没有 write_todos**。")
print("     想要规划能力，得自己加中间件（见 ②）。")


# ---------------------------------------------------------------------------
# 2. 显式开启规划
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("② 显式加 TodoListMiddleware，write_todos 才出现")
print("=" * 78)

m1 = ScriptedChatModel(
    script=[
        tool_call(
            "write_todos",
            {"todos": [{"content": "调研", "status": "in_progress"},
                       {"content": "写稿", "status": "pending"}]},
            "t1",
        ),
        reply("计划已建立。"),
    ]
)
planned = create_deep_agent(model=m1, middleware=[TodoListMiddleware()])
out = planned.invoke({"messages": [HumanMessage("帮我做个计划")]})
names2 = tool_names(m1)
print(f"  加中间件后共 {len(names2)} 个：{names2}")
print(f"  write_todos 出现了：{'write_todos' in names2}")
print(f"  运行后状态里多出的键：{[k for k in out if k != 'messages']}")
print(f"  todos = {out.get('todos')}")


# ---------------------------------------------------------------------------
# 3. 预装中间件栈：看真实的图节点名
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("③ 预装中间件栈 —— 图里到底挂了哪些节点")
print("=" * 78)

configs = [
    ("裸的（只给 model）", {}),
    ("+ 记忆 + 技能", {"memory": ["/memories/AGENTS.md"], "skills": ["/skills/"]}),
    ("+ 子代理", {"subagents": [{"name": "researcher", "description": "做调研", "system_prompt": "你负责调研"}]}),
    ("+ 人工审批", {"interrupt_on": {"execute": True}}),
]
for label, kw in configs:
    a = create_deep_agent(model=ScriptedChatModel(script=[reply("ok")]), **kw)
    nodes = [n for n in a.get_graph().nodes if not n.startswith("__")]
    print(f"  {label:<20} → 节点 {nodes}")

print()
print("  读法：")
print("    · 固定节点 model / tools 是所有 agent 共有的骨架；")
print("    · 形如 `XxxMiddleware.before_agent` 的节点，是**中间件自己插进来的钩子节点**；")
print("    · 挂了 memory 才有 MemoryMiddleware 节点，挂了 skills 才有 SkillsMiddleware 节点——")
print("      所以「看节点名」是反查「这个 agent 到底装了哪些能力」最快的方式。")


# ---------------------------------------------------------------------------
# 4. HarnessProfile
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("④ HarnessProfile：声明式裁剪内置能力")
print("=" * 78)

profile = HarnessProfile(
    system_prompt_suffix="回答一律用中文。",
    excluded_tools=frozenset({"execute"}),  # 不要执行能力
    tool_description_overrides={"grep": "在本项目源码里搜索。"},
)
print(f"  profile.excluded_tools = {profile.excluded_tools}")
print(f"  profile.system_prompt_suffix = {profile.system_prompt_suffix!r}")
print(f"  profile.tool_description_overrides = {profile.tool_description_overrides}")

register_harness_profile("my-openai-profile", profile)
print("  已注册 profile：'my-openai-profile'")

print()
print("  HarnessProfile 的全部字段（实测签名）：")
for f in (
    "base_system_prompt",
    "system_prompt_suffix",
    "tool_description_overrides",
    "excluded_tools",
    "excluded_middleware",
    "extra_middleware",
    "general_purpose_subagent",
):
    print(f"    · {f}")

print()
print("  ⚠️ 官方文档只提到了 excluded_tools 与 excluded_middleware 两个字段，")
print("     实测 HarnessProfile 一共 7 个——按实测为准。")
print("     用 profile 而不是「自己拼中间件」的好处：内置能力升级时你不用跟着改。")
