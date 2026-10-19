r"""用智谱真实模型验证教程文档里标注「未实测」的结论。

对应文档声明：
  A. code/README.md:61 + ch02 —— 「假模型 stream 只吐 1 个 chunk；真实模型分多块（未实测）」
  B. code/README.md:104 + ch04 ③ —— 「method="json_schema" 的真实差别由 provider 子类
     实现（如 ChatOpenAI 会改用 response_format 的 json_schema 模式）——需真实模型，未实测」
  C. code/README.md:103 + ch10:59 —— 「token 与成本字段需要真实模型返回的 usage 元数据，
     本机无 API Key，未实测」
  D. ch09:95 —— 「缓存命中率与真实计费需要真实模型与 API Key，本机没有账号」
  E. code/README.md:158 —— 「换成真实模型后，示例里的断言式输出会变」

key 从 gitignore 的 code/.secrets.log 读取，不硬编码、不落盘到输出。
"""

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

API_KEY = (
    pathlib.Path(__file__).resolve().parents[2] / "code" / ".secrets.log"
)
MODEL = "glm-4.5-air"


def make(**kw):
    return ChatOpenAI(
        model=MODEL,
        api_key=API_KEY.read_text(encoding="utf-8").strip(),
        base_url="https://open.bigmodel.cn/api/paas/v4",
        temperature=0.1,
        **kw,
    )


RULE = "=" * 78


# ---------------------------------------------------------------- A
print(RULE)
print("A. 真实模型 stream 到底吐几个 chunk？（文档：假模型 1 个，真实模型分多块·未实测）")
print(RULE)
m = make(max_completion_tokens=200)
chunks = list(m.stream([HumanMessage(content="用一句话介绍长城。")]))
text = "".join(c.content for c in chunks)
print(f"  chunk 总数        = {len(chunks)}")
print(f"  前 5 个 chunk 的 content 长度 = {[len(c.content) for c in chunks[:5]]}")
print(f"  累计文本（前 60 字）= {text[:60]!r}")
print(f"  → 结论：真实模型吐 {len(chunks)} 个 chunk，"
      f"{'明显多于 1 个，文档说法成立' if len(chunks) > 1 else '仍只有 1 个，文档说法需修正'}")
print("  → 顺带验证 ch02 的另一个说法：流式最后一个 chunk 才带完整 usage_metadata")
last_usage = [c.usage_metadata for c in chunks if c.usage_metadata]
print(f"     带 usage_metadata 的 chunk 数 = {len(last_usage)}，"
      f"位置 = {[i for i, c in enumerate(chunks) if c.usage_metadata]}")

# ---------------------------------------------------------------- C
print()
print(RULE)
print("C. usage_metadata / token 计费字段（文档：本机无 Key，未实测）")
print(RULE)
r = m.invoke([HumanMessage(content="1+1 等于几？只回答数字。")])
print(f"  type(r.usage_metadata) = {type(r.usage_metadata).__name__}")
print(f"  r.usage_metadata = {r.usage_metadata}")
print(f"  r.response_metadata 里的模型/身份字段：")
for k in ("model_name", "model", "id", "token_usage", "finish_reason"):
    if k in r.response_metadata:
        v = r.response_metadata[k]
        print(f"    · {k} = {v}")

# ---------------------------------------------------------------- D
print()
print(RULE)
print("D. 缓存命中率（ch09:95 声称未实测）——连发同样的长前缀，看 cached_tokens")
print(RULE)
long_prefix = ("下面是背景资料，请仔细阅读但不要回答：\n" + "智谱 GLM 系列模型的上下文缓存"
               "会对重复前缀计费打折。" * 40)
for i in range(3):
    rr = make(max_completion_tokens=16).invoke(
        [SystemMessage(content=long_prefix),
         HumanMessage(content=f"第 {i + 1} 次请求：只回答数字 7。")]
    )
    um = rr.usage_metadata or {}
    det = rr.response_metadata.get("token_usage", {})
    print(f"  第 {i + 1} 次: input={um.get('input_tokens')} "
          f"cached={um.get('input_token_details', {}).get('cache_read')} "
          f"| raw={det}")

# ---------------------------------------------------------------- B
print()
print(RULE)
print("B. with_structured_output 的 method 在 provider 子类上到底有何差别")
print("   （文档：基类三条路径都走 bind_tools；json_schema 的真实差别由 provider 子类实现·未实测）")
print(RULE)


class Person(BaseModel):
    """人物信息"""

    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")


PROMPT = "张三是一名 30 岁的软件工程师"

for method in (None, "function_calling", "json_schema", "json_mode"):
    mm = make(max_completion_tokens=512)
    kw = {} if method is None else {"method": method}
    try:
        bound = mm.with_structured_output(Person, **kw)
        # 抓住真正发给服务的请求体，看它走的是 tools 还是 response_format
        captured = {}
        orig = bound.bound.bound_client.chat.completions.create

        def spy(*a, _o=orig, **k):
            captured.update(k)
            return _o(*a, **k)

        bound.bound.bound_client.chat.completions.create = spy
        out = bound.invoke([HumanMessage(content=PROMPT)])
        keys = sorted(captured.keys())
        sig = []
        if "tools" in captured:
            sig.append(f"tools={[[t['function']['name'] for t in captured['tools']]]}")
        if "response_format" in captured:
            sig.append(f"response_format={captured['response_format']}")
        print(f"  method={str(method):<17} → 返回 {type(out).__name__}: {out}")
        print(f"  {'':<17}   实际 HTTP 参数: {' '.join(sig) or '(无 tools / 无 response_format)'}")
    except Exception as e:  # noqa: BLE001
        print(f"  method={str(method):<17} → 抛 {type(e).__name__}: {str(e)[:160]}")

# ---------------------------------------------------------------- E
print()
print(RULE)
print("E. 换成真实模型后，create_agent 的消息序列还符合 ch05 的断言吗")
print(RULE)
from langchain_core.tools import tool
from langchain.agents import create_agent


@tool
def get_weather(city: str) -> str:
    """查城市天气。"""
    return f"{city}: 22°C，晴"


agent = create_agent(model=make(max_completion_tokens=512), tools=[get_weather])
res = agent.invoke({"messages": [HumanMessage(content="上海天气怎么样？")]})
msgs = res["messages"]
print(f"  消息条数 = {len(msgs)}")
for i, msg in enumerate(msgs, 1):
    tc = getattr(msg, "tool_calls", [])
    print(f"  {i}. [{type(msg).__name__}] {str(msg.content)[:40]!r}"
          f"  tool_calls={[(t['name'], t['args']) for t in tc] if tc else ''}")
print("  文档 ch05 断言的序列是 Human → AI(tool_call) → ToolMessage → AI(final)")
print("  → 看上面实际序列是否一致（真实模型可能直接回答、或调多次工具）")
