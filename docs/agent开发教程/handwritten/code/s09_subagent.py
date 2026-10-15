"""s09 子代理：上下文防火墙——大任务拆给独立上下文的子代理。

运行：python s09_subagent.py

对比视角：
- 不拆：主上下文里堆满两个主题的全部调研细节（几十条消息）；
- 拆：主代理一次 create_agent 调用，两个子代理各自在自己的上下文里
  消化细节，只把结论带回主上下文。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _fake_llm import FakeClient

from agent.agent import Agent
from agent.subagent import make_create_agent_tool
from agent.tool import registry


def user_text(msgs):
    return " ".join(m.get("content") or "" for m in msgs if m.get("role") == "user")


def tool_text(msgs):
    return " ".join(m.get("content") or "" for m in msgs if m.get("role") == "tool")


# ------------------------------------------------------------------
# 剧本。匹配是共享的（主/子代理用同一个 FakeClient），所以每条规则
# 的 match 都写成函数，只命中自己那条故事线：
#   主代理：最后 user 含「两个主题」；收到含【sub-orm】的工具结果后汇总
#   子代理1：query 含「ORM 数据层怎么搭」，随后按工具结果推进
#   子代理2：query 含「DTO 与接口怎么设计」
# ------------------------------------------------------------------
client = FakeClient([
    {   # 主代理：规划并派发
        "match": lambda m: "两个主题" in user_text(m),
        "resp": {"tool_calls": [{"name": "create_agent", "arguments": {"agents": [
            {"name": "sub-orm", "query": "调研任务：ORM 数据层怎么搭？先读 docs/orm.md，再读 docs/migration.md，最后给结论。"},
            {"name": "sub-dto", "query": "调研任务：DTO 与接口怎么设计？先读 docs/dto.md，再读 docs/api.md，最后给结论。"},
        ]}}]},
    },
    {   # 主代理：拿到两个子代理的报告后汇总
        "match": lambda m: "【sub-orm】" in tool_text(m),
        "resp": {"content": "两个子代理已完成调研：数据层用 SQLAlchemy 2.0 + Alembic；DTO/接口用 Pydantic 分层 + FastAPI。"},
    },
    {   # 子代理 1：第一步，读 orm.md
        "match": lambda m: "ORM 数据层怎么搭" in user_text(m),
        "resp": {"tool_calls": [{"name": "read_file", "arguments": {"filepath": "docs/orm.md"}}]},
    },
    {   # 子代理 1：第二步，读 migration.md
        "match": lambda m: "SQLAlchemy" in tool_text(m),
        "resp": {"tool_calls": [{"name": "read_file", "arguments": {"filepath": "docs/migration.md"}}]},
    },
    {   # 子代理 1：结论
        "match": lambda m: "Alembic" in tool_text(m),
        "resp": {"content": "结论：用 SQLAlchemy 2.0 声明式模型 + Alembic 迁移，一个 migrations 目录按版本号递增。"},
    },
    {   # 子代理 2：第一步，读 dto.md
        "match": lambda m: "DTO 与接口怎么设计" in user_text(m),
        "resp": {"tool_calls": [{"name": "read_file", "arguments": {"filepath": "docs/dto.md"}}]},
    },
    {   # 子代理 2：结论
        "match": lambda m: "Pydantic" in tool_text(m) and "In/Out" in tool_text(m),
        "resp": {"content": "结论：Pydantic DTO 分层（In/Out），FastAPI 依赖注入校验，接口按资源分组。"},
    },
])

# 演示文件（系统临时目录）
import tempfile
demo_dir = tempfile.mkdtemp(prefix="agent-s09-")
for name, text in {
    "docs/orm.md": "ORM：推荐 SQLAlchemy 2.0 声明式模型……",
    "docs/migration.md": "迁移：Alembic，版本号递增……",
    "docs/dto.md": "DTO：Pydantic In/Out 分层……",
    "docs/api.md": "接口：FastAPI 按资源分组……",
}.items():
    path = os.path.join(demo_dir, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
os.chdir(demo_dir)  # 子代理用相对路径读文件

# ------------------------------------------------------------------
# 组装：create_agent 工具的 agent_factory 每次产出全新 Agent
# ------------------------------------------------------------------
registry.register(make_create_agent_tool(
    agent_factory=lambda: Agent(client=client, auto_builtin=True)))

agent = Agent(client=client)
print("== 1. 主代理派发两个子代理 ==")
agent.invoke("调研数据层与 DTO/接口两个主题，汇总成结论给我。")

print("\n== 2. 主代理的完整轨迹（注意：主上下文只有 1 次工具调用）==")
agent.session.print_friendly()
print(f"主上下文消息数：{len(agent.session.messages)}")

print("\n== 3. 上下文防火墙效果 ==")
print("两个子代理各自的调研往返（读文件、比对、汇总）全部发生在独立会话里，")
print("主上下文只收到一段汇总文本——这就是子代理的价值。")
