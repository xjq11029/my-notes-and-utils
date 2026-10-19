r"""验证 ch09:182 的具体断言：

  「本机实测（6 轮、trigger=("messages", 8)）：最终状态 8 条，而
    get_state_history 的 **42 个快照**里仍能翻出第 1 轮的长工具输出原文。」

拆成两问：
  ① 快照到底几个？——纯结构量，与模型无关，用假模型 + checkpointer 就能数。
  ② 摘要前的检查点里是否仍保有第 1 轮的长工具输出原文？
  ③（真实模型档）把摘要器换成智谱真模型，状态消息数与保留性是否仍成立。

另外顺带核对：示例源码 09_context.py 的 ② 用的是 keep=("messages", 4)，
而 ch09:180 写的是 keep=2。
"""

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

CODE = pathlib.Path(__file__).resolve().parents[2] / "code" / "python"
sys.path.insert(0, str(CODE))

from _fake_model import ScriptedChatModel, reply, tool_call  # noqa: E402
from langchain.agents import create_agent  # noqa: E402
from langchain.agents.middleware import SummarizationMiddleware  # noqa: E402
from langchain_core.messages import BaseMessage, HumanMessage  # noqa: E402
from langchain.tools import tool  # noqa: E402
from langgraph.checkpoint.memory import InMemorySaver  # noqa: E402

ROUNDS = 6
TRIGGER = ("messages", 8)
KEEP = ("messages", 4)


@tool
def fetch_log(service: str) -> str:
    """拉取某个服务的日志（返回内容很长，正是上下文膨胀的元凶）。"""
    return f"[{service}] " + "ERROR connection reset; " * 40


def approx_tokens(messages: list[BaseMessage]) -> int:
    chars = sum(len(str(m.content)) for m in messages)
    return int(chars / 4) + 3 * len(messages)


def build(summarizer):
    script = []
    for i in range(ROUNDS):
        script.append(tool_call("fetch_log", {"service": f"svc-{i}"}, f"c{i}"))
        script.append(reply(f"第 {i} 轮排查完毕。"))
    return create_agent(
        model=ScriptedChatModel(script=script),
        tools=[fetch_log],
        middleware=[SummarizationMiddleware(model=summarizer, trigger=TRIGGER, keep=KEEP)],
        checkpointer=InMemorySaver(),
    )


def probe(tag, summarizer):
    print()
    print("=" * 78)
    print(f"{tag}")
    print("=" * 78)
    agent = build(summarizer)
    cfg = {"configurable": {"thread_id": "t-09"}}
    msgs = []
    for i in range(ROUNDS):
        out = agent.invoke({"messages": [*msgs, HumanMessage(f"排查 svc-{i}")]}, cfg)
        msgs = out["messages"]
        print(f"  第 {i + 1} 轮  状态消息数={len(msgs)}")
    print(f"  → 最终状态消息数 = {len(msgs)}   （正文 ch09:182 声称 8）")

    snaps = list(agent.get_state_history(cfg))
    print(f"  → get_state_history 快照总数 = {len(snaps)}   （正文声称 42）")

    # 第 1 轮的长工具输出原文特征串。
    # 注意：不能用 "ERROR connection reset;"——每轮日志都含它，会误判成「还在」。
    # 要用轮次专属的 [svc-0] 前缀 + 原文正文，才能证明「第 1 轮的原文」。
    needle = "[svc-0] ERROR connection reset; ERROR connection reset;"
    hit_now = any(needle in str(m.content) for m in msgs)
    print(f"  → 当前状态里还能找到第 1 轮长日志原文吗？ {hit_now}")
    found_at = [
        (i, s.values.get("messages") and len(s.values["messages"]))
        for i, s in enumerate(snaps)
        if any(needle in str(m.content) for m in s.values.get("messages", []))
    ]
    print(f"  → 含原文的快照个数 = {len(found_at)}，其下标(新→旧)与消息数 = {found_at[:8]}"
          f"{' ...' if len(found_at) > 8 else ''}")
    return len(snaps), len(msgs), len(found_at)


print("=" * 78)
print("前置事实核对：示例源码 09_context.py 的 keep 参数")
print("=" * 78)
src = (CODE / "09_context.py").read_text(encoding="utf-8")
for m in re.finditer(r"keep[=]\s*\(?.{0,24}", src):
    print(f"  源码出现：{m.group(0).strip()}")
print('  正文 ch09:180 写的是「keep=2」（且把它归给 SummarizationMiddleware）。')

# ① 假模型摘要器：纯结构计数，与真实模型无关
probe("① 假模型摘要器 + checkpointer（6 轮、trigger=('messages', 8)）",
      ScriptedChatModel(script=[reply("【摘要】前几轮排查了 svc-0 起的服务，均无新问题。")]))

# ③ 真实模型摘要器
from langchain_openai import ChatOpenAI  # noqa: E402

KEY = (pathlib.Path(__file__).resolve().parents[2] / "code" / ".secrets.log").read_text(
    encoding="utf-8"
).strip()
real = ChatOpenAI(
    model="glm-4.5-air",
    api_key=KEY,
    base_url="https://open.bigmodel.cn/api/paas/v4",
    temperature=0.1,
    max_completion_tokens=1024,
)
probe("③ 真实模型摘要器（智谱 glm-4.5-air）+ checkpointer", real)
