r"""B 段 v3：在 httpx 传输层抓**真正上线的 JSON 请求体**。

v2 的教训：langchain-openai 通过 `client.chat.completions.with_raw_response.create`
调用，该包装器在 client 构造时就把原函数绑成了实例属性，事后 monkeypatch
`Completions.create` 抓不到。event hook 在 httpx 层，任何 SDK 包装都绕不过去。
"""

import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")

import httpx
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

API_KEY = pathlib.Path(__file__).resolve().parents[2] / "code" / ".secrets.log"
KEY = API_KEY.read_text(encoding="utf-8").strip()

captured = {}


def _hook(request):
    try:
        captured.clear()
        captured.update(json.loads(request.content.decode("utf-8")))
    except Exception:  # noqa: BLE001
        captured.clear()


def make(model):
    return ChatOpenAI(
        model=model,
        api_key=KEY,
        base_url="https://open.bigmodel.cn/api/paas/v4",
        temperature=0.1,
        max_completion_tokens=1024,
        http_client=httpx.Client(event_hooks={"request": [_hook]}),
    )


class Person(BaseModel):
    """人物信息"""

    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")


PROMPT = "张三是一名 30 岁的软件工程师。请抽取人物信息。"


def probe(model, method):
    captured.clear()
    kw = {} if method is None else {"method": method}
    print(f"\n  ── model={model}  method={method}")
    try:
        out = make(model).with_structured_output(Person, **kw).invoke(
            [HumanMessage(content=PROMPT)]
        )
        print(f"     返回 {type(out).__name__}: {out}")
    except Exception as e:  # noqa: BLE001
        print(f"     抛 {type(e).__name__}: {str(e).splitlines()[0][:130]}")
    tools = captured.get("tools")
    rf = captured.get("response_format")
    tc = captured.get("tool_choice")
    print(f"     上线 tools           = {[t['function']['name'] for t in tools] if tools else None}")
    if tools:
        print(f"     上线 tool_choice     = "
              f"{tc.get('function', {}).get('name') if isinstance(tc, dict) else tc}")
        print(f"     上线 tool 的 strict  = {tools[0]['function'].get('strict', '(字段缺失)')}")
    print(f"     上线 response_format = {rf}")


print("=" * 78)
print("真实请求体抓取：with_structured_output 的 method 在 provider 子类上改了什么")
print("=" * 78)
for meth in (None, "function_calling", "json_schema", "json_mode"):
    probe("glm-4-plus", meth)

print()
print("=" * 78)
print("对照组：同一个 method 参数在**假模型基类**上是否被丢掉")
print("（ch04 ③ / 差异清单 #13 的实测口径。用子类覆盖 bind_tools 来记录入参，")
print("  因为 ScriptedChatModel 是 pydantic 模型，不能在实例上直接赋值。）")
print("=" * 78)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "code" / "python"))
from _fake_model import ScriptedChatModel  # noqa: E402

CALLS = []


class SpyModel(ScriptedChatModel):
    def bind_tools(self, tools, **kwargs):
        CALLS.append(([getattr(t, "name", t) for t in tools], kwargs))
        return super().bind_tools(tools, **kwargs)


for meth in (None, "function_calling", "json_schema"):
    CALLS.clear()
    m = SpyModel(script=[])
    try:
        m.with_structured_output(Person, **({} if meth is None else {"method": meth}))
        names, extra = CALLS[0] if CALLS else ([], {})
        print(f"  method={str(meth):<17} → bind_tools 工具名={names} "
              f"额外参数={sorted(extra)}")
    except Exception as e:  # noqa: BLE001
        print(f"  method={str(meth):<17} → 抛 {type(e).__name__}: {str(e)[:100]}")
print("  → 若三行的「额外参数」都不含 response_format，且三者一致，")
print("    说明基类确实把 method 丢掉了（与 ch04 ③ 的说法吻合）。")
