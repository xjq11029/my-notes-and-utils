r"""B 段重做：拦截真正发往服务端的 HTTP 请求体，看 with_structured_output 的
method 参数在 provider 子类（ChatOpenAI）上到底改变了什么。

文档声明（code/README.md:104、ch04 ③）：
  「基类实现里 method 被直接丢掉，三条路径都走 bind_tools + tool_choice；
    method="json_schema" 的真实差别由 provider 子类实现（如 ChatOpenAI 会改用
    response_format 的 json_schema 模式）——需真实模型，本教程未实测」
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


PROMPT = "张三是一名 30 岁的软件工程师"


def make():
    return ChatOpenAI(
        model="glm-4.5-air",
        api_key=API_KEY.read_text(encoding="utf-8").strip(),
        base_url="https://open.bigmodel.cn/api/paas/v4",
        temperature=0.1,
        max_completion_tokens=512,
    )


print("=" * 78)
print("B. ChatOpenAI(provider 子类) 上四种 method 实际发出的 HTTP 参数")
print("=" * 78)

for method in (None, "function_calling", "json_schema", "json_mode"):
    kw = {} if method is None else {"method": method}
    label = str(method)
    try:
        chain = make().with_structured_output(Person, **kw)
        out = chain.invoke([HumanMessage(content=PROMPT)])
        has_tools = "tools" in captured
        has_rf = "response_format" in captured
        tc = captured.get("tool_choice")
        print(f"\n  method={label}")
        print(f"    返回 {type(out).__name__}: {out}")
        print(f"    带 tools 参数?         {has_tools}"
              + (f"  → 工具名={[t['function']['name'] for t in captured['tools']]}"
                 if has_tools else ""))
        print(f"    带 response_format?    {has_rf}"
              + (f"  → {captured['response_format']}" if has_rf else ""))
        if has_tools:
            print(f"    tool_choice = {tc if not isinstance(tc, dict) else tc.get('function', {}).get('name', tc)}")
    except Exception as e:  # noqa: BLE001
        print(f"\n  method={label}")
        print(f"    抛 {type(e).__name__}: {str(e)[:300]}")

print()
print("=" * 78)
print("B-附. include_raw=True 时坏数据怎么办（ch04 ④ 的机制，真实模型版）")
print("=" * 78)
chain = make().with_structured_output(Person, include_raw=True)
r = chain.invoke([HumanMessage(content="随便说点别的，不含任何人物信息。")])
print(f"  keys = {sorted(r.keys())}")
print(f"  parsed = {r['parsed']}")
print(f"  parsing_error = {type(r['parsing_error']).__name__ if r['parsing_error'] else None}")
print(f"  raw.content 前 80 字 = {str(r['raw'].content)[:80]!r}")
