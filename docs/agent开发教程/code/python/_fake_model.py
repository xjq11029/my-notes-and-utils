# -*- coding: utf-8 -*-
"""离线可用的可脚本化假模型 —— 本目录所有示例共用。

为什么需要它
------------
本教程的示例要验证的是**框架的机制**（循环、钩子、状态、检查点、中断、流式、
工具派发），不是模型有多聪明。用真实 LLM 会引入三个干扰：

1. 需要 API Key 和网络，读者跑不起来；
2. 同样的输入未必给同样的输出，结论无法复现；
3. 分不清某个行为是框架做的还是模型做的。

所以这里用一个**按脚本逐条吐消息**的假模型：你告诉它「先请求调用哪个工具、
再说什么话」，它就照做。框架该做的事一件都不会少。

关键点：`bind_tools` 必须实现
----------------------------
`langchain_core.language_models.GenericFakeChatModel` 不能直接用于 agent——
`create_agent` 在调模型前会执行 `model.bind_tools(...)`，而基类默认抛
`NotImplementedError`。所以这里自己实现一个，让 `bind_tools` 原样返回自身。

（这一点在本机实测中确认：直接用 `GenericFakeChatModel` 建 agent，
运行时会报 `NotImplementedError`。）
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class ScriptedChatModel(BaseChatModel):
    """按脚本逐条回复的假模型。

    参数
    ----
    script:
        依次返回的 `AIMessage` 列表。脚本用完后重复最后一条。

    行为
    ----
    - `bind_tools` 返回自身（真实模型在这一步把工具的 JSON Schema 写进请求）
    - **记录每一次实际收到的消息列表**（`seen`）——这是本教程反复用到的观测手段：
      中间件可以在消息到达模型之前改写它，而图状态里看到的可能仍是未改写的样子，
      只有从模型这一侧看，才知道模型究竟收到了什么。
    - 无网络、无随机数，结果确定可复现
    """

    script: list[AIMessage] = []
    seen: list[list[BaseMessage]] = []
    bound_tool_names: list[list[str]] = []
    _cursor: int = 0

    model_config = {"arbitrary_types_allowed": True}

    @property
    def _llm_type(self) -> str:
        return "scripted-fake-chat-model"

    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> "ScriptedChatModel":
        """真实模型在这里把工具 schema 绑进请求；假模型只记下名字，然后原样返回。

        「模型被给了哪些工具」只能从这一侧看见——图内部的工具表属于实现细节。
        """
        names = [getattr(t, "name", None) or (t.get("name") if isinstance(t, dict) else None) for t in tools]
        self.bound_tool_names.append([n for n in names if n])
        return self

    def last_bound_tool_names(self) -> list[str]:
        """最近一次绑定的工具名（升序）。"""
        return sorted(self.bound_tool_names[-1]) if self.bound_tool_names else []

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        # 记下「模型实际收到什么」——中间件的效果只能从这里看见
        self.seen.append(list(messages))
        idx = min(self._cursor, len(self.script) - 1)
        msg = self.script[idx]
        self._cursor += 1
        return ChatResult(generations=[ChatGeneration(message=msg)])


def tool_call(name: str, args: dict[str, Any], call_id: str) -> AIMessage:
    """构造一条「请求调用工具」的 AI 消息。"""
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


def reply(text: str) -> AIMessage:
    """构造一条「给出最终答案」的 AI 消息。"""
    return AIMessage(content=text)


def show(messages: list[BaseMessage]) -> None:
    """把一条消息序列打印成人能读的形式（示例统一用这个函数输出）。"""
    for i, msg in enumerate(messages, 1):
        kind = type(msg).__name__
        content = str(msg.content)
        if len(content) > 60:
            content = content[:57] + "..."
        calls = getattr(msg, "tool_calls", None) or []
        suffix = ""
        if calls:
            suffix = "  tool_calls=" + str([(c["name"], c["args"]) for c in calls])
        print(f"  {i}. [{kind}] {content!r}{suffix}")
