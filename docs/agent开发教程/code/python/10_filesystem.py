# -*- coding: utf-8 -*-
"""第 10 章示例：虚拟文件系统与执行环境。

演示四件事：
  1. 默认后端 StateBackend：文件存在图状态里，随线程走
  2. 8 个文件工具的实际行为（ls / write_file / read_file / edit_file / glob / grep / delete）
  3. FilesystemPermission 的声明式权限：首次匹配即生效
  4. 换后端：StoreBackend（跨线程持久）与 CompositeBackend（按路径分流）

运行：python 10_filesystem.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, tool_call
from deepagents import FilesystemMiddleware, create_deep_agent
from langchain_core.messages import HumanMessage


# ---------------------------------------------------------------------------
# 1 & 2. 文件工具的实际行为
# ---------------------------------------------------------------------------
print("=" * 78)
print("① 文件工具跑起来是什么样（StateBackend，文件存在图状态里）")
print("=" * 78)

script = [
    tool_call("write_file", {"file_path": "/notes/todo.md", "content": "# 待办\n- 写文档\n- 跑测试"}, "c1"),
    tool_call("read_file", {"file_path": "/notes/todo.md"}, "c2"),
    tool_call("edit_file", {"file_path": "/notes/todo.md", "old_string": "- 跑测试", "new_string": "- 跑测试 ✅"}, "c3"),
    tool_call("ls", {"path": "/notes"}, "c4"),
    reply("做完了。"),
]
model = ScriptedChatModel(script=script)
agent = create_deep_agent(model=model)

out = agent.invoke(
    {"messages": [HumanMessage("先写个待办，再读出来改一改")]},
    config={"configurable": {"thread_id": "fs-1"}},
)
print(f"  默认暴露给模型的工具（invoke 之后才取得到）：{model.last_bound_tool_names()}")

print("  逐条工具调用的返回值：")
for msg in out["messages"]:
    if type(msg).__name__ == "ToolMessage":
        text = str(msg.content).replace("\n", "\\n")
        print(f"    [{msg.name}] {text[:88]}")

print()
print(f"  状态里的键：{sorted(k for k in out if not k.startswith('_'))}")
print(f"  state['files'] 的内容：{out.get('files')}")
print()
print("  ⚠️ 关键点：StateBackend 把「文件」存在**图状态**里。")
print("     好处：跟着线程走，天然享受检查点（可回放、可时间旅行）；")
print("     代价：跨线程就没了——新 thread_id 打开是一张白纸。")
print("     要跨线程，得换 StoreBackend（见 ④）。")


# ---------------------------------------------------------------------------
# 3. 权限
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("② FilesystemPermission：声明式权限")
print("=" * 78)

from deepagents import FilesystemPermission  # noqa: E402

perm = FilesystemPermission(
    operations=["read", "write"],
    paths=["/workspace/**"],
    mode="allow",
)
print(f"  实测签名：FilesystemPermission(operations, paths, mode='allow')")
print(f"  构造出的实例：{perm!r}")
print()
print("  三个字段：")
print("    operations  ['read', 'write'] 的列表")
print("    paths       路径 glob，如 '/workspace/**'")
print("    mode        'allow' | 'deny' | 'interrupt'")
print()
print("  ⚠️ mode='interrupt' 这一档容易被忽略：它不是「拒绝」，")
print("     而是**暂停下来问人**——权限系统与人在回路是打通的。")
print()
print("  规则按**声明顺序首次匹配即生效**（first match wins）：")
print("    1. 先声明「/secrets/** 禁止读写」")
print("    2. 再声明「/workspace/** 允许读写」")
print("    3. 没被任何规则命中的路径 → **默认 allow（放行）**")
print()
print("  ⚠️ 顺序写反了（先 allow /workspace/**，再 deny /workspace/secrets/**）")
print("     后一条永远不会生效——因为第一条已经命中了。")
print("     这条规则和防火墙的 ACL 是同一个思路：**具体规则放前面，宽泛规则放后面**。")
print("     ⚠️ 两个例外：① 未命中任何规则时**默认放行**（只写一条 deny 得不到白名单）；")
print("                 ② 递归 delete 的 deny **不受顺序约束**，更靠后的 deny 照样拦得住。")


# ---------------------------------------------------------------------------
# 4. 后端谱系
# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("③ 后端谱系：文件到底存在哪")
print("=" * 78)

import deepagents.backends as B  # noqa: E402
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend  # noqa: E402

rows = [
    ("StateBackend", "图状态（默认）", "跟线程走、可回放；跨线程丢失"),
    ("StoreBackend", "LangGraph Store", "跨线程持久；适合 /memories/ 这类长期记忆"),
    ("FilesystemBackend", "真实磁盘", "直接读写本机文件；要小心权限"),
    ("LocalShellBackend", "本机 shell", "提供 execute 能力；生产环境慎用"),
    ("LangSmithSandbox", "托管沙箱", "隔离执行；适合不信任的代码"),
    ("CompositeBackend", "按路径分流", "如 /memories/** 走 Store，其余走 State"),
]
print(f"  {'后端':<20} {'落点':<16} 特点")
print("  " + "-" * 70)
for name, where, note in rows:
    print(f"  {name:<20} {where:<16} {note}")

print()
print("  实测签名：")
print("    StateBackend()")
print("    StoreBackend(*, namespace, store=None)      ← namespace 是个函数，从 Runtime 算出来")
print("    FilesystemBackend(root_dir=None, virtual_mode=True, max_file_size_mb=10)")
print("    LocalShellBackend(root_dir=None, *, virtual_mode=True, timeout=120, ...)")
print("    CompositeBackend(default, routes, *, artifacts_root='/')")
print()
print("  注意 LangSmithSandbox 不在 deepagents.backends 的顶层导出里，")
print("  要从 deepagents.backends.langsmith 导入——按实测为准。")

print()
print("  CompositeBackend 的典型用法（把长期记忆单独分流）：")
print("    backend = CompositeBackend(")
print("        default=StateBackend(),")
print("        routes={'/memories/': StoreBackend(namespace=lambda rt: ('memories',))},")
print("    )")
print("  → agent 写 /memories/xxx 就跨线程持久，写别处仍走状态，各取所需。")
print()
print("  ⚠️ 默认后端是 StateBackend（实测 create_deep_agent 源码：")
print("     `backend = backend if backend is not None else StateBackend()`）。")
print("     官方文档提到「默认写入图状态中的本地文件系统」，与实测一致。")
