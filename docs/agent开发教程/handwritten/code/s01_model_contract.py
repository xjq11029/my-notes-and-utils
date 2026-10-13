"""s01 模型接口契约：Chat Completions 的请求 / 响应 / 流式三种形态。

运行：python s01_model_contract.py
（离线：注入 FakeClient；真模型：设置 OPENAI_API_KEY 后用 Model() 默认 client）

本章回答一个问题：LangChain 这类框架在帮你调模型时，网络上实际跑的是
什么？答案就是 OpenAI Chat Completions 这一份 JSON 契约。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _fake_llm import FakeClient

from agent.model import Model
from agent.session import Session

client = FakeClient([
    {
        "match": "你是谁",
        "resp": {
            "reasoning": "用户在问我是谁，直接自我介绍即可。",
            "content": "我是手写教程里的假模型，替你演示模型接口契约。",
        },
    },
    {
        "match": "从 1 数到 5",
        "resp": {"content": "1、2、3、4、5。"},
    },
])
model = Model(client=client)

# ------------------------------------------------------------------
# 1) 非流式：一次请求，一次拿回完整响应
# ------------------------------------------------------------------
session = Session()
session.add_message({"role": "user", "content": "你是谁"})
resp = model.invoke(session)

print("== 1. 非流式：归一化后的 message（可直接进入会话历史）==")
print(json.dumps(resp.message, ensure_ascii=False, indent=2))

print("\n== 2. 响应的原始形状（顶层结构即契约）==")
raw = resp.raw
print("顶层字段     :", sorted(raw.keys()))
print("choices[0]   :", sorted(raw["choices"][0].keys()))
print("message 字段 :", sorted(raw["choices"][0]["message"].keys()))
print("usage        :", raw["usage"])
print("finish_reason:", raw["choices"][0]["finish_reason"])

# ------------------------------------------------------------------
# 2) 流式：响应被切成一串 chunk，正文藏在每个 chunk 的 delta 里
# ------------------------------------------------------------------
print("\n== 3. 流式：逐 chunk 的 delta（手动迭代原始 chunk）==")
chunks = client.chat.completions.create(
    model="fake", messages=[{"role": "user", "content": "从 1 数到 5"}], stream=True)
for i, chunk in enumerate(chunks):
    delta = chunk.choices[0].delta
    print(f"chunk {i}: delta.content={getattr(delta, 'content', None)!r} "
          f"finish={chunk.choices[0].finish_reason!r}")

model2 = Model(client=client)
session2 = Session()
session2.add_message({"role": "user", "content": "从 1 数到 5"})
resp2 = model2.invoke(session2, stream=True)  # Model 层负责把上面这些 chunk 拼回去

print("\n== 4. 拼装后的 message（与非流式形状完全一致）==")
print(json.dumps(resp2.message, ensure_ascii=False, indent=2))

# ------------------------------------------------------------------
# 3) 检视请求侧：模型实际收到了什么
# ------------------------------------------------------------------
print("\n== 5. 请求侧：发给模型服务的 JSON（第 1 次调用）==")
print(json.dumps(client.calls[0], ensure_ascii=False, indent=2))
