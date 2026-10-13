"""事件系统：发布-订阅模式的事件总线。

Model 在调用过程中向外广播事件（思考 / 正文 / 工具调用三条通道），
任何关心调用过程的组件（打印器、日志、UI、计费统计）都以监听器身份接入，
模型层不依赖任何具体的展示逻辑——这是 Agent 可观测性的地基。
"""
from collections import defaultdict
from typing import Callable


class Event:
    """事件类型常量。三组 START / 正文 / END 事件对应流式响应的三条通道。"""

    REASONING_START = "reasoning_start"
    REASONING = "reasoning"
    REASONING_END = "reasoning_end"

    CONTENT_START = "content_start"
    CONTENT = "content"
    CONTENT_END = "content_end"

    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL = "tool_call"
    TOOL_CALL_END = "tool_call_end"

    COMPLETE = "complete"


ALL_EVENTS = [
    Event.REASONING_START, Event.REASONING, Event.REASONING_END,
    Event.CONTENT_START, Event.CONTENT, Event.CONTENT_END,
    Event.TOOL_CALL_START, Event.TOOL_CALL, Event.TOOL_CALL_END,
    Event.COMPLETE,
]


class EventEmitter:
    """极简发布-订阅：一个事件可绑定多个回调。

    回调统一签名：callback(event: str, **data)。
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def on(self, event: str, callback: Callable) -> None:
        """注册监听器。"""
        self._handlers[event].append(callback)

    def emit(self, event: str, **data) -> None:
        """触发事件，依次调用所有监听器。"""
        for callback in list(self._handlers[event]):
            callback(event, **data)
