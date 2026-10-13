"""模型层：封装 OpenAI Chat Completions 调用（非流式 + 流式）。

设计要点：
- client 可注入：默认按环境变量创建 OpenAI SDK client；离线示例注入
  _fake_llm.FakeClient，两者接口形状一致（duck-typing），上层代码零改动。
- Model 继承 EventEmitter：调用过程中的 reasoning / content / tool_calls
  三条通道以事件形式广播，展示逻辑（打印、日志）通过监听器接入。
- 流式响应用「装配器」逐 chunk 消费：三条通道各自累积、边解析边发事件，
  最终拼出与非流式 message 完全一致的归一化 dict。
"""
import json
from dataclasses import dataclass
from typing import Any, Iterable

from agent.config import settings
from agent.events import Event, EventEmitter


@dataclass
class InvokeResult:
    """一次调用的结果。

    message 是归一化后的 dict（role/content/[reasoning_content]/[tool_calls]），
    可直接进入会话历史；raw 是原始响应（流式调用时为 None）。
    """

    message: dict
    raw: Any = None

    def print_raw(self) -> str:
        text = json.dumps(self.raw, ensure_ascii=False, indent=2, default=str)
        print(text)
        return text


def make_default_client():
    """按环境变量创建真实的 OpenAI SDK client；未配置则给出清晰报错。"""
    if not settings.api_key:
        raise RuntimeError(
            "未设置 OPENAI_API_KEY。离线运行请显式注入假模型："
            "Model(client=FakeClient([...]))，见各示例脚本 s01~s10。"
        )
    from openai import OpenAI  # 懒加载：只有真跑才需要安装 openai

    return OpenAI(api_key=settings.api_key, base_url=settings.base_url or None)


class Model(EventEmitter):
    """模型调用器。session 提供 messages（必需）与 tools（可选）。"""

    def __init__(self, client: Any | None = None) -> None:
        super().__init__()
        self.client = client if client is not None else make_default_client()

    def invoke(self, session, stream: bool = False) -> InvokeResult:
        """调用模型。响应消息会自动追加进 session.messages。"""
        kwargs: dict[str, Any] = {
            "model": settings.model,
            "messages": list(session.messages),
        }
        if session.tools:
            kwargs["tools"] = session.tools
        if stream:
            return self._invoke_stream(session, **kwargs)
        return self._invoke(session, **kwargs)

    # ---------- 非流式 ----------

    def _invoke(self, session, **kwargs) -> InvokeResult:
        resp = self.client.chat.completions.create(**kwargs)
        message = _normalize_message(resp.choices[0].message)
        session.add_message(message)
        return InvokeResult(message=message, raw=_to_plain(resp))

    # ---------- 流式 ----------

    def _invoke_stream(self, session, **kwargs) -> InvokeResult:
        kwargs["stream"] = True
        chunks = self.client.chat.completions.create(**kwargs)
        message = _StreamAssembler(self).consume(chunks)
        session.add_message(message)
        return InvokeResult(message=message, raw=None)


# ---------- 消息归一化 ----------


def _normalize_message(msg) -> dict:
    """把 SDK 的 message 对象归一化成纯 dict。

    兼容两种思考字段命名：reasoning_content（DeepSeek 等）与 reasoning（部分厂商）。
    tool_calls 的 arguments 保留为 JSON 字符串（OpenAI 契约如此，分片拼接发生在流式层）。
    """
    reasoning = getattr(msg, "reasoning_content", None) or getattr(msg, "reasoning", None)
    message: dict = {"role": "assistant", "content": getattr(msg, "content", None)}
    if reasoning:
        message["reasoning_content"] = reasoning
    tool_calls = getattr(msg, "tool_calls", None)
    if tool_calls:
        message["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in tool_calls
        ]
    return message


def _to_plain(obj: Any) -> Any:
    """把响应对象递归转成可 JSON 化的纯结构（便于 print_raw 检视契约）。"""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_plain(x) for x in obj]
    if hasattr(obj, "model_dump"):
        try:
            return _to_plain(obj.model_dump())
        except Exception:
            pass
    if hasattr(obj, "__dict__"):
        return {k: _to_plain(v) for k, v in vars(obj).items()}
    return str(obj)


# ---------- 流式装配器 ----------


class _StreamAssembler:
    """逐 chunk 消费流式响应，拼装出完整 message，同时按通道发射事件。

    delta 的三个可选字段对应三条通道：
    - reasoning_content / reasoning → 思考内容（思考型模型才有）
    - content                       → 正文
    - tool_calls                    → 工具调用；arguments 是跨 chunk 的分片，
      必须按 index 累积拼接，流结束后才是完整 JSON——这是流式 tool calling
      最容易踩的坑。
    """

    def __init__(self, model: Model) -> None:
        self.model = model
        self.reasoning: list[str] = []
        self.content: list[str] = []
        self.tool_calls: dict[int, dict] = {}
        self._open = {"reasoning": False, "content": False, "tool": False}

    def _emit(self, event: str, **data) -> None:
        self.model.emit(event, **data)

    def consume(self, chunks: Iterable) -> dict:
        for chunk in chunks:
            self._feed(chunk.choices[0].delta)
        return self._finalize()

    def _feed(self, delta) -> None:
        # 1) 思考通道
        reasoning = getattr(delta, "reasoning_content", None) or getattr(delta, "reasoning", None)
        if reasoning:
            if not self._open["reasoning"]:
                self._open["reasoning"] = True
                self._emit(Event.REASONING_START)
            self.reasoning.append(reasoning)
            self._emit(Event.REASONING, text=reasoning)
        # 思考结束的判定：同一 chunk 出现 content/tool_calls（混合），
        # 或后续 chunk 出现 content/tool_calls（更常见）。
        has_later = bool(getattr(delta, "content", None)) or bool(getattr(delta, "tool_calls", None))
        if reasoning and has_later and self._open["reasoning"]:
            self._close_reasoning()
        # 2) 正文通道
        content = getattr(delta, "content", None)
        if content:
            if self._open["reasoning"]:
                self._close_reasoning()
            if not self._open["content"]:
                self._open["content"] = True
                self._emit(Event.CONTENT_START)
            self.content.append(content)
            self._emit(Event.CONTENT, text=content)
        # 3) 工具通道
        pieces = getattr(delta, "tool_calls", None) or []
        if pieces:
            if self._open["reasoning"]:
                self._close_reasoning()
            if not self._open["tool"]:
                self._open["tool"] = True
                self._emit(Event.TOOL_CALL_START)
        for piece in pieces:
            index = getattr(piece, "index", 0) or 0
            slot = self.tool_calls.setdefault(
                index, {"id": "", "type": "function", "function": {"name": "", "arguments": ""}}
            )
            if getattr(piece, "id", None):
                slot["id"] = piece.id
            fn = getattr(piece, "function", None)
            if fn is None:
                continue
            if getattr(fn, "name", None):
                slot["function"]["name"] = fn.name
                self._emit(Event.TOOL_CALL, name=fn.name)
            if getattr(fn, "arguments", ""):
                slot["function"]["arguments"] += fn.arguments

    def _close_reasoning(self) -> None:
        self._open["reasoning"] = False
        self._emit(Event.REASONING_END)

    def _finalize(self) -> dict:
        if self._open["reasoning"]:
            self._close_reasoning()
        if self._open["content"]:
            self._open["content"] = False
            self._emit(Event.CONTENT_END)
        if self._open["tool"]:
            self._open["tool"] = False
            names = [self.tool_calls[i]["function"]["name"] for i in sorted(self.tool_calls)]
            self._emit(Event.TOOL_CALL_END, names=names)
        message: dict = {"role": "assistant", "content": "".join(self.content) or None}
        if self.reasoning:
            message["reasoning_content"] = "".join(self.reasoning)
        if self.tool_calls:
            message["tool_calls"] = [self.tool_calls[i] for i in sorted(self.tool_calls)]
        self._emit(Event.COMPLETE, message=message)
        return message
