r"""B 段 v2：无论成功失败，都打印实际发往服务端的 HTTP 参数。

目的：精确回答「provider 子类（ChatOpenAI）上 method 到底改了什么」。
"""

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")

import openai.resources.chat.completions as comp
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

API_KEY = pathlib.Path(__file__).resolve().parents[2] / "code" / ".secrets.log"

captured = {}
_orig = comp.Completions.create


def spy(self, *a, **k):
    captured.clear()
    captured.update(k)
    return _orig(self, *a, **k)


comp.Completions.create = spy


class Person(BaseModel):
    """人物信息"""

    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")


PROMPT = "张三是一名 30 岁的软件工程师。请抽取人物信息。"


def make(model):
    return ChatOpenAI(
        model=model,
        api_key=API_KEY.read_text(encoding="utf-8").strip(),
        base_url="https://open.bigmodel.cn/api/paas/v4",
        temperature=0.1,
        max_completion_tokens=1024,
    )


def probe(model, method, include_raw=False):
    captured.clear()
    kw = {} if method is None else {"method": method}
    if include_raw:
        kw["include_raw"] = True
    label = f"model={model} method={method} include_raw={include_raw}"
    print(f"\n  ── {label}")
    try:
        chain = make(model).with_structured_output(Person, **kw)
        out = chain.invoke([HumanMessage(content=PROMPT)])
        if include_raw:
            print(f"     返回 dict keys = {sorted(out.keys())}")
            print(f"       parsed={out['parsed']}  parsing_error="
                  f"{type(out['parsing_error']).__name__ if out['parsing_error'] else None}")
        else:
            print(f"     返回 {type(out).__name__}: {out}")
    except Exception as e:  # noqa: BLE001
        print(f"     抛 {type(e).__name__}: {str(e).splitlines()[0][:120]}")
    tools = captured.get("tools")
    rf = captured.get("response_format")
    print(f"     HTTP.tools            = {[t['function']['name'] for t in tools] if tools else None}")
    if tools:
        tc = captured.get("tool_choice")
        print(f"     HTTP.tool_choice      = {tc.get('function', {}).get('name') if isinstance(tc, dict) else tc}")
    print(f"     HTTP.response_format  = {rf}")


print("=" * 78)
print("B-1. 假模型基类 vs 真实 provider 子类：method 是否真的被「丢掉」")
print("     文档 code/README.md:63 / ch04 ③ 称：基类三条路径都走 bind_tools + tool_choice")
print("=" * 78)
for meth in (None, "function_calling", "json_schema", "json_mode"):
    probe("glm-4-plus", meth)

print()
print("=" * 78)
print("B-2. 同一组实验换推理模型 glm-4.5-air（资源包对它另有额度）")
print("=" * 78)
for meth in (None, "function_calling", "json_schema"):
    probe("glm-4.5-air", meth)

print()
print("=" * 78)
print("B-3. include_raw=True 能否兜住真实模型给的坏数据？")
print("     文档 ch04 ④：「include_raw 把抛错变成返回值，不会一条坏数据打断整批」")
print("=" * 78)
probe("glm-4-plus", None, include_raw=True)
probe("glm-4-plus", "json_schema", include_raw=True)
probe("glm-4-plus", "function_calling", include_raw=True)
