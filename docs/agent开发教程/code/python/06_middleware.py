# -*- coding: utf-8 -*-
"""第 6 章示例：中间件的钩子体系与治理件。

本示例做两件事：
  1. 把六个钩子在一次含工具调用的完整轮次里的真实触发顺序打出来；
  2. 演示四类治理件：HITL 审批、PII 脱敏、调用限额、重试与回退。

运行：python 06_middleware.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, tool_call
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    HumanInTheLoopMiddleware,
    ModelCallLimitMiddleware,
    ModelFallbackMiddleware,
    ModelRetryMiddleware,
    PIIMiddleware,
    ToolCallLimitMiddleware,
    ToolRetryMiddleware,
    after_agent,
    after_model,
    before_agent,
    before_model,
    wrap_model_call,
    wrap_tool_call,
)
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

TRACE: list[str] = []


@tool
def get_weather(city: str) -> str:
    """查询某个城市的天气。"""
    TRACE.append("        └─ 工具函数体真正执行")
    return f"{city}: 22°C，晴"


# ---------------------------------------------------------------------------
# 六个钩子
# ---------------------------------------------------------------------------
@before_agent
def hook_before_agent(state, runtime):
    TRACE.append("before_agent")


@before_model
def hook_before_model(state, runtime):
    TRACE.append("before_model")


@after_model
def hook_after_model(state, runtime):
    TRACE.append("after_model")


@after_agent
def hook_after_agent(state, runtime):
    TRACE.append("after_agent")


@wrap_model_call
def hook_wrap_model_call(request, handler):
    TRACE.append("wrap_model_call")
    return handler(request)


@wrap_tool_call
def hook_wrap_tool_call(request, handler):
    TRACE.append("wrap_tool_call")
    return handler(request)


print("=" * 72)
print("六个钩子的真实触发顺序")
print("=" * 72)

agent = create_agent(
    model=ScriptedChatModel(
        script=[
            tool_call("get_weather", {"city": "上海"}, "c1"),
            reply("上海 22°C，晴。"),
        ]
    ),
    tools=[get_weather],
    middleware=[
        hook_before_agent,
        hook_before_model,
        hook_after_model,
        hook_after_agent,
        hook_wrap_model_call,
        hook_wrap_tool_call,
    ],
)
agent.invoke({"messages": [{"role": "user", "content": "上海天气？"}]})

for i, line in enumerate(TRACE, 1):
    print(f"  {i:>2}. {line}")

print()
print("  读法：")
print("  · before_agent / after_agent 包住**整个** agent 调用，各只触发一次；")
print("  · before_model → wrap_model_call → after_model 是**每一次**模型调用都走一遍；")
print("  · 轮次里出现了两次 before_model，因为这一轮调了两次模型")
print("    （第一次决定调工具，第二次拿到工具结果后给最终答案）；")
print("  · wrap_tool_call 只在工具执行时出现一次，且夹在两次模型调用之间。")


# ---------------------------------------------------------------------------
# 用 wrap_model_call 拦截并改写模型请求
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("wrap_* 钩子能改写请求：动态切换模型")
print("=" * 72)

SWITCH_LOG: list[str] = []


class SwitchModelMiddleware(AgentMiddleware):
    """长上下文时换用「更强」的模型——真实项目里常见的成本/质量权衡。"""

    def __init__(self, cheap, strong, threshold=8):
        super().__init__()
        self.cheap = cheap
        self.strong = strong
        self.threshold = threshold

    def wrap_model_call(self, request, handler):
        n = len(request.state["messages"])
        if n > self.threshold:
            SWITCH_LOG.append(f"消息数 {n} > {self.threshold} → 换用强模型")
            return handler(request.override(model=self.strong))
        SWITCH_LOG.append(f"消息数 {n} ≤ {self.threshold} → 用便宜模型")
        return handler(request)


mw = SwitchModelMiddleware(
    cheap=ScriptedChatModel(script=[reply("便宜模型的回答")]),
    strong=ScriptedChatModel(script=[reply("强模型的回答")]),
    threshold=2,
)
sw_agent = create_agent(model=mw.cheap, tools=[], middleware=[mw])
out = sw_agent.invoke({"messages": [{"role": "user", "content": "问题一"}]})
print(f"  第一次调用：{SWITCH_LOG[-1]}")
print(f"  最终回复：{out['messages'][-1].content!r}")

out = sw_agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "问题一"},
            {"role": "assistant", "content": "答案一"},
            {"role": "user", "content": "问题二"},
        ]
    }
)
print(f"  第二次调用：{SWITCH_LOG[-1]}")
print(f"  最终回复：{out['messages'][-1].content!r}")
print("  → request.override(model=...) 是官方推荐的「换模型」写法；")
print("    直接改 request.model 也能跑，但 override 会保留链上其它中间件的语义。")


# ---------------------------------------------------------------------------
# 3. HITL
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("③ HumanInTheLoopMiddleware：工具调用前停下来等人")
print("=" * 72)

REFUNDS: list[str] = []


@tool
def refund(order_id: str) -> str:
    """给订单退款。"""
    REFUNDS.append(order_id)
    return f"{order_id} 已退款"


def make_refund_agent():
    return create_agent(
        model=ScriptedChatModel(
            script=[tool_call("refund", {"order_id": "A-1"}, "c1"), reply("已处理。")]
        ),
        tools=[refund],
        middleware=[HumanInTheLoopMiddleware(interrupt_on={"refund": True})],
        checkpointer=InMemorySaver(),
    )


approve_agent = make_refund_agent()
approve_cfg = {"configurable": {"thread_id": "refund-approve"}}
first = approve_agent.invoke(
    {"messages": [{"role": "user", "content": "把 A-1 退款"}]}, approve_cfg
)
request = first["__interrupt__"][0].value
print(f"  待审批工具 = {request['action_requests'][0]['name']}")
print(f"  允许决策   = {request['review_configs'][0]['allowed_decisions']}")
print(f"  审批前退款次数 = {len(REFUNDS)}")
second = approve_agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), approve_cfg)
print(f"  approve 后退款次数 = {len(REFUNDS)}，最终回复 = {second['messages'][-1].content!r}")

reject_agent = make_refund_agent()
reject_cfg = {"configurable": {"thread_id": "refund-reject"}}
reject_agent.invoke({"messages": [{"role": "user", "content": "把 A-1 退款"}]}, reject_cfg)
rejected = reject_agent.invoke(
    Command(resume={"decisions": [{"type": "reject", "message": "金额不对"}]}), reject_cfg
)
print(f"  reject 后退款次数 = {len(REFUNDS)}（未增加），最终回复 = {rejected['messages'][-1].content!r}")
print("  → 审批载荷里带 action_requests 与 review_configs；恢复用 Command(resume={'decisions': [...]})。")
print("    HumanInTheLoopMiddleware 只是把第 13 章的 interrupt 封装成工具级审批，底层仍是中断 + 检查点。")


# ---------------------------------------------------------------------------
# 4. PII
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("④ PIIMiddleware：模型侧只看到脱敏文本")
print("=" * 72)

pii_model = ScriptedChatModel(script=[reply("收到。")])
pii_agent = create_agent(
    model=pii_model,
    tools=[],
    middleware=[
        PIIMiddleware("email", strategy="redact"),
        PIIMiddleware("credit_card", strategy="mask"),
    ],
)
pii_agent.invoke(
    {"messages": [{"role": "user", "content": "联系 alice@example.com，卡号 4111 1111 1111 1111"}]}
)
print(f"  模型实际收到：{[str(m.content) for m in pii_model.seen[-1]]}")
print("  → 脱敏发生在消息到达模型之前；图状态里可能仍是原文，只有模型侧看到脱敏结果。")
print("    默认 apply_to_input=True、apply_to_output=False、apply_to_tool_results=False（源码核对）。")


# ---------------------------------------------------------------------------
# 5. 限额
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("⑤ 限额：模型调用与工具调用的上限")
print("=" * 72)

limit_model = ScriptedChatModel(script=[tool_call("get_weather", {"city": "上海"}, "c1")])
limit_agent = create_agent(
    model=limit_model,
    tools=[get_weather],
    middleware=[ModelCallLimitMiddleware(run_limit=1, exit_behavior="end")],
)
limit_out = limit_agent.invoke({"messages": [{"role": "user", "content": "上海天气？"}]})
print(f"  ModelCallLimit(run_limit=1) → 最后一条：{limit_out['messages'][-1].content!r}")

tool_limit_model = ScriptedChatModel(
    script=[
        tool_call("get_weather", {"city": "上海"}, "c1"),
        tool_call("get_weather", {"city": "北京"}, "c2"),
        reply("只查了一个。"),
    ]
)
tool_limit_agent = create_agent(
    model=tool_limit_model,
    tools=[get_weather],
    middleware=[
        ToolCallLimitMiddleware(tool_name="get_weather", run_limit=1, exit_behavior="continue")
    ],
)
tool_limit_out = tool_limit_agent.invoke(
    {"messages": [{"role": "user", "content": "两个城市天气"}]}
)
for msg in tool_limit_out["messages"]:
    if type(msg).__name__ == "ToolMessage":
        print(f"  ToolMessage: {str(msg.content)[:60]!r}")


# ---------------------------------------------------------------------------
# 6. 重试与回退
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("⑥ 重试与回退：ToolRetry / ModelRetry / ModelFallback")
print("=" * 72)

FLAKY_CALLS = {"n": 0}


@tool
def flaky_weather(city: str) -> str:
    """一个前两次会失败、第三次成功的天气工具。"""
    FLAKY_CALLS["n"] += 1
    if FLAKY_CALLS["n"] < 3:
        raise ValueError("上游超时")
    return f"{city}: 22°C"


retry_agent = create_agent(
    model=ScriptedChatModel(
        script=[tool_call("flaky_weather", {"city": "上海"}, "c1"), reply("查到了。")]
    ),
    tools=[flaky_weather],
    middleware=[ToolRetryMiddleware(max_retries=2, initial_delay=0.01, jitter=False)],
)
retry_out = retry_agent.invoke({"messages": [{"role": "user", "content": "上海天气？"}]})
print(
    f"  ToolRetry(max_retries=2) → 工具实际调用 {FLAKY_CALLS['n']} 次，"
    f"最后回复 = {retry_out['messages'][-1].content!r}"
)


class FlakyModel(ScriptedChatModel):
    fails: int = 1

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if self.fails > 0:
            self.fails -= 1
            raise RuntimeError("模型偶发失败")
        return super()._generate(messages, stop, run_manager, **kwargs)


flaky_model = FlakyModel(script=[reply("重试成功")])
model_retry_agent = create_agent(
    model=flaky_model,
    tools=[],
    middleware=[ModelRetryMiddleware(max_retries=2, initial_delay=0.01, jitter=False)],
)
model_retry_out = model_retry_agent.invoke(
    {"messages": [{"role": "user", "content": "你好"}]}
)
print(f"  ModelRetry → {model_retry_out['messages'][-1].content!r}（fails 余量 {flaky_model.fails}）")


class AlwaysFailModel(ScriptedChatModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        raise RuntimeError("主模型不可用")


fallback_model = ScriptedChatModel(script=[reply("备用模型的回答")])
fallback_agent = create_agent(
    model=AlwaysFailModel(script=[reply("never")]),
    tools=[],
    middleware=[ModelFallbackMiddleware(fallback_model)],
)
fallback_out = fallback_agent.invoke({"messages": [{"role": "user", "content": "你好"}]})
print(f"  ModelFallback → {fallback_out['messages'][-1].content!r}")
print("  → 重试解决「偶发失败」，回退解决「主模型整体不可用」；两者可以叠加，但顺序决定语义。")
