# -*- coding: utf-8 -*-
"""第 5 章示例：上下文工程的四种手段。

本示例要回答一个很容易搞错的问题：
**「装了上下文中间件之后，图状态里的消息变少了吗？」**

答案是——**不一定**。所以本示例同时打印两个数字：

  · 状态里的消息数：`result["messages"]` 有多少条
  · 模型收到的消息数：从假模型那一侧记录的实际输入

两者在 `SummarizationMiddleware` 下会一起变小，在 `ContextEditingMiddleware`
下却会**分道扬镳**——这正是本示例最值得看的一处。

运行：python 05_context.py
"""

import sys
from langchain_core.messages import BaseMessage, HumanMessage

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, tool_call
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ClearToolUsesEdit,
    ContextEditingMiddleware,
    SummarizationMiddleware,
)
from langchain.tools import tool


@tool
def fetch_log(service: str) -> str:
    """拉取某个服务的日志（返回内容很长，正是上下文膨胀的元凶）。"""
    return f"[{service}] " + "ERROR connection reset; " * 40


def approx_tokens(messages: list[BaseMessage]) -> int:
    """复刻框架内置的近似计数：每 4 个字符算 1 token，每条消息再加 3。

    （`langchain_core.messages.utils.count_tokens_approximately` 的默认参数，
    这样打印出来的数字和中间件触发用的数字是同一把尺子。）
    """
    chars = sum(len(str(m.content)) for m in messages)
    return int(chars / 4) + 3 * len(messages)


def run_case(title: str, middleware: list, rounds: int = 6) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)
    print(f"  {'轮次':<4} {'状态消息数':>10} {'模型收到消息数':>14} {'模型收到 tokens':>15}")
    print("  " + "-" * 48)

    script = []
    for i in range(rounds):
        script.append(tool_call("fetch_log", {"service": f"svc-{i}"}, f"c{i}"))
        script.append(reply(f"第 {i} 轮排查完毕。"))

    model = ScriptedChatModel(script=script)
    agent = create_agent(model=model, tools=[fetch_log], middleware=middleware)

    messages: list[BaseMessage] = []
    for i in range(rounds):
        out = agent.invoke({"messages": [*messages, HumanMessage(f"排查 svc-{i}")]})
        messages = out["messages"]
        last_seen = model.seen[-1]
        print(
            f"  {i + 1:<4} {len(messages):>10} {len(last_seen):>14}"
            f" {approx_tokens(last_seen):>15}"
        )


# ---------------------------------------------------------------------------
# 基线：什么都不装
# ---------------------------------------------------------------------------
run_case("① 基线：不装任何中间件 —— 两个数字一起线性上涨", middleware=[])


# ---------------------------------------------------------------------------
# 手段一：摘要压缩
# ---------------------------------------------------------------------------
run_case(
    "② SummarizationMiddleware —— 状态本身被压缩（两个数字一起变小）",
    middleware=[
        SummarizationMiddleware(
            model=ScriptedChatModel(
                script=[reply("【摘要】前几轮排查了 svc-0 起的服务，均无新问题。")]
            ),
            trigger=("messages", 8),
            keep=("messages", 4),
        )
    ],
)


# ---------------------------------------------------------------------------
# 手段二：清掉旧工具输出
# ---------------------------------------------------------------------------
run_case(
    "③ ContextEditingMiddleware —— 状态继续涨，但模型收到的不涨",
    middleware=[
        ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=600,  # 模型输入超过 600（近似）token 就动手
                    keep=2,  # 最近 2 条工具结果必须保留
                    placeholder="[已清理：旧工具输出]",  # 清掉后的占位符
                )
            ]
        )
    ],
)

print()
print("=" * 78)
print("两种手段的机制差异（这是本示例的核心结论）")
print("=" * 78)
print()
print("  SummarizationMiddleware")
print("    实现方式：before_model 钩子，返回一条摘要消息，**写回图状态**")
print("    后果    ：状态与模型输入一起变小；原文从当前状态消失")
print("              ⚠️「永久丢失」要加前提：**不配 checkpointer** 才是；")
print("                 配了 checkpointer 时，摘要前那个检查点仍保有原文（第 7 章）")
print("    适用    ：对话很长、旧轮次的细节确实不再需要")
print()
print("  ContextEditingMiddleware")
print("    实现方式：wrap_model_call 钩子，deepcopy 一份消息、改完只传给模型，")
print("              **不回写状态**（源码里是 request.override(messages=edited)）")
print("    后果    ：状态里的历史一条不少（便于审计 / 时间旅行），")
print("              但模型看不到那些被清掉的工具输出")
print("    适用    ：工具输出又大又只用一次（日志、网页正文、检索片段）")
print()
print("  ⚠️ 两者都会造成**静默失败**：清理和压缩本身不报错，")
print("     只是关键信息悄悄没了，后面的回答开始变差——不报错的失败最难查。")
print()
print("  第四种手段「外部存储」不在本章演示：把长内容写进虚拟文件系统或 Store，")
print("  上下文里只留一句「已保存到 /xxx」——见第 10 章与第 12 章。")
