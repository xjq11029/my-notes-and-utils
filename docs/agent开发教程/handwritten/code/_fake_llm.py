"""离线假模型：模拟 OpenAI Chat Completions 的响应形状（非流式 + 流式）。

教学重点：它返回的数据形状与真实 OpenAI SDK 一致（duck-typing），
所以 Model 层代码不需要任何改动就能在真假模型之间切换——
这本身就是「模型接口契约」稳定性的最好证明。

脚本驱动：每个示例脚本按剧情注册若干条响应规格，
FakeClient 按「最后一条用户消息」匹配合适的响应。
"""
import itertools
import json
from types import SimpleNamespace

_counter = itertools.count(1)


def _resp_id() -> str:
    return f"chatcmpl-fake-{next(_counter)}"


class FakeClient:
    """脚本驱动的假模型，替代 OpenAI SDK 的 client。

    script 每项形如::

        {
            "match": "天气",                 # 或 callable(messages) -> bool
            "resp": {
                "content": "最终回复文本",     # 可选
                "reasoning": "思考过程文本",   # 可选（思考型模型才有）
                "tool_calls": [              # 可选；有则模拟请求工具
                    {"name": "read_file", "arguments": {"filepath": "a.txt"}}
                ],
            },
            "once": True,                    # 默认 True：匹配后消费一次
        }

    - match 为字符串时，与「最后一条 user 消息」做子串匹配；
      需要检查全部上下文时传函数（见 s03 会话章的用法）。
    - 所有未被匹配的请求返回 default_content。
    """

    def __init__(self, script: list[dict] | None = None,
                 default_content: str = "（假模型：没有匹配到脚本）") -> None:
        self.script = [dict(item, consumed=False) for item in (script or [])]
        self.default_content = default_content
        completions = SimpleNamespace(create=self._create)
        self.chat = SimpleNamespace(completions=completions)
        self.calls: list[dict] = []  # 记录每次请求，供检视「模型实际收到了什么」

    # ---------- OpenAI SDK 形状的入口 ----------

    def _create(self, *, model=None, messages=None, tools=None, stream=False, **kwargs):
        record = {"model": model, "messages": list(messages or [])}
        if tools is not None:
            record["tools"] = tools
        self.calls.append(record)
        spec = self._pick(messages or [])
        if stream:
            return self._stream(spec)
        return self._complete(spec)

    # ---------- 脚本匹配 ----------

    def _pick(self, messages: list[dict]) -> dict:
        last_user = next((m for m in reversed(messages) if m.get("role") == "user"), {})
        text = last_user.get("content") or ""
        for item in self.script:
            if item["consumed"]:
                continue
            matcher = item.get("match")
            ok = matcher(messages) if callable(matcher) else (matcher in text)
            if ok:
                if item.get("once", True):
                    item["consumed"] = True
                return item["resp"]
        return {"content": self.default_content}

    # ---------- 非流式 ----------

    def _complete(self, spec: dict) -> SimpleNamespace:
        message = self._build_message(spec)
        finish = "tool_calls" if message.tool_calls else "stop"
        return SimpleNamespace(
            id=_resp_id(), object="chat.completion", created=0, model="fake",
            choices=[SimpleNamespace(index=0, message=message, finish_reason=finish)],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )

    def _build_message(self, spec: dict) -> SimpleNamespace:
        tool_calls = None
        if spec.get("tool_calls"):
            tool_calls = [
                SimpleNamespace(
                    id=f"call_{i + 1}", type="function",
                    function=SimpleNamespace(
                        name=tc["name"],
                        arguments=json.dumps(tc.get("arguments", {}), ensure_ascii=False),
                    ),
                )
                for i, tc in enumerate(spec["tool_calls"])
            ]
        return SimpleNamespace(
            role="assistant",
            content=spec.get("content"),
            reasoning_content=spec.get("reasoning"),
            tool_calls=tool_calls,
        )

    # ---------- 流式 ----------

    def _stream(self, spec: dict):
        """把一个响应规格切成 chunk 序列。

        - reasoning / content 按小片逐个发出（模拟逐 token）；
        - tool_calls 故意拆成「id+name → arguments 前半 → arguments 后半」三片，
          演示流式下 arguments 跨 chunk 拼接这一关键细节。
        """

        def chunk(delta, finish=None):
            return SimpleNamespace(
                id=_resp_id(), object="chat.completion.chunk", model="fake",
                choices=[SimpleNamespace(index=0, delta=delta, finish_reason=finish)],
            )

        chunks = []
        reasoning = spec.get("reasoning")
        if reasoning:
            mid = max(1, len(reasoning) // 2)
            chunks.append(chunk(SimpleNamespace(reasoning_content=reasoning[:mid])))
            chunks.append(chunk(SimpleNamespace(reasoning_content=reasoning[mid:])))
        content = spec.get("content")
        if content:
            size = max(1, len(content) // 3)
            for i in range(0, len(content), size):
                chunks.append(chunk(SimpleNamespace(content=content[i:i + size])))
        for i, tc in enumerate(spec.get("tool_calls", [])):
            args = json.dumps(tc.get("arguments", {}), ensure_ascii=False)
            chunks.append(chunk(SimpleNamespace(tool_calls=[SimpleNamespace(
                index=i, id=f"call_{i + 1}", type="function",
                function=SimpleNamespace(name=tc["name"], arguments=""))])))
            half = max(1, len(args) // 2)
            chunks.append(chunk(SimpleNamespace(tool_calls=[SimpleNamespace(
                index=i, function=SimpleNamespace(arguments=args[:half]))])))
            chunks.append(chunk(SimpleNamespace(tool_calls=[SimpleNamespace(
                index=i, function=SimpleNamespace(arguments=args[half:]))])))
        finish = "tool_calls" if spec.get("tool_calls") else "stop"
        chunks.append(chunk(SimpleNamespace(), finish=finish))
        return iter(chunks)
