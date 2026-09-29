# -*- coding: utf-8 -*-
"""第 2 章示例：模型的创建与调用 —— 三个初始化角度与四种调用形态。

演示五件事：
  1. 模型初始化的三个角度：提供商库 / init_chat_model / 本地 Ollama
  2. invoke 的三种入参形态，以及它们被归一化成什么（用假模型的 .seen 观测）
  3. 返回值 AIMessage 的字段结构
  4. 四种调用形态：invoke / stream / batch / ainvoke
  5. profile 属性与 config 参数（tags / metadata / callbacks）

运行：python 02_models.py

⚠️ 未实测范围（本机没有模型 API Key，也没有本地 Ollama）：
   - 「初始化」一节只走到**构造出对象**这一步，不发任何请求，因此可离线实测；
   - 真实 provider 的 invoke、stream 的真实分块、token 计费**未实测**，逐处标注；
   - 本示例真正跑通的调用链路全部走假模型 ScriptedChatModel（见 _fake_model.py）。
"""

import asyncio
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, tool_call
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage


# ---------------------------------------------------------------------------
# ① 模型初始化的三个角度
# ---------------------------------------------------------------------------
print("=" * 72)
print("① 模型初始化的三个角度：提供商库 / init_chat_model / 本地 Ollama")
print("=" * 72)
print("  ⚠️ 本节只走到「构造出对象」，不发请求——真实调用需 API Key，未实测。")
print()

# 角度 1：模型提供商库 —— 直接实例化对应的 ChatXxx 类
print("  角度 1｜提供商库：直接 new 一个 ChatXxx 类")
try:
    from langchain_openai import ChatOpenAI

    direct = ChatOpenAI(model="gpt-4o", api_key="sk-placeholder")
    print(f"    ChatOpenAI(model='gpt-4o') → {type(direct).__name__}，model_name={direct.model_name!r}")
except ImportError as exc:
    print(f"    （未安装 langchain-openai，跳过：{exc}）")
print("    → 一个提供商一个类、一套参数名；换一家就得改 import 和参数名。")
print()

# 角度 2：统一入口 init_chat_model()
print("  角度 2｜统一入口：init_chat_model(\"provider:model\")")
try:
    unified = init_chat_model("openai:gpt-4o", api_key="sk-placeholder")
    print(f"    init_chat_model('openai:gpt-4o') → {type(unified).__name__}"
          "（前缀 openai 自动选中了 ChatOpenAI）")
except Exception as exc:  # noqa: BLE001 - 没装 provider 包时这里会抛 ImportError
    print(f"    init_chat_model('openai:gpt-4o') → {type(exc).__name__}: {str(exc).splitlines()[0]}")

# 兼容用法：任何 OpenAI 兼容平台，都可以让 openai 这个前缀去接
compat = init_chat_model(
    model="deepseek-chat",
    model_provider="openai",
    api_key="sk-placeholder",
    base_url="https://api.deepseek.com/v1",
)
print(f"    init_chat_model(model='deepseek-chat', model_provider='openai', base_url=...)"
      f" → {type(compat).__name__}")
print(f"    底层实际用的 base_url = {compat.openai_api_base}")
print("    → provider 前缀指的是「用哪套协议 / 哪个类」，不是「哪家厂商」；")
print("      平台没有专用集成时，把它套进 openai 前缀即可。")
print()

print("    两个「前缀没写 / 写错」的实测报错：")
for model_id in ("deepseek:deepseek-chat", "qwen-plus"):
    try:
        init_chat_model(model_id, api_key="sk-placeholder")
        print(f"      init_chat_model({model_id!r}) → 构造成功（本机装了对应 provider 包）")
    except Exception as exc:  # noqa: BLE001
        print(f"      init_chat_model({model_id!r}) → {type(exc).__name__}: {str(exc).splitlines()[0]}")
print("      ↑ 前者说明「前缀 → 需要哪个包」；后者说明「不写前缀时框架得猜得出提供商」。")
print()

# 角度 3：本地模型
print("  角度 3｜本地模型：ChatOllama（需本机先起 Ollama 服务）")
try:
    from langchain_ollama import ChatOllama

    local = ChatOllama(model="deepseek-r1:1.5b", base_url="http://localhost:11434")
    print(f"    ChatOllama(model='deepseek-r1:1.5b') → {type(local).__name__}")
except ImportError as exc:
    print(f"    （未安装 langchain-ollama，跳过：{exc}）")
print("    → 也可以走统一入口：init_chat_model('deepseek-r1:1.5b', model_provider='ollama')。")
print("    ⚠️ Ollama 必须先在本机跑起来（默认 http://localhost:11434）。")
print("       服务没起、模型没 pull，构造能过，一 invoke 就连接失败——本机无 Ollama，未实测。")


# ---------------------------------------------------------------------------
# ② invoke 的三种入参形态与归一化
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("② invoke 的三种入参形态，与模型实际收到的消息（.seen 观测）")
print("=" * 72)

probe = ScriptedChatModel(script=[reply("收到。"), reply("收到。"), reply("收到。")])
cases = [
    ("字符串", "翻译成英文：你好世界"),
    (
        "dict 列表",
        [
            {"role": "system", "content": "你是翻译助手。"},
            {"role": "user", "content": "翻译成英文：你好世界"},
        ],
    ),
    ("消息对象列表", [SystemMessage("你是翻译助手。"), HumanMessage("翻译成英文：你好世界")]),
]
for label, payload in cases:
    probe.invoke(payload)
    received = probe.seen[-1]
    kinds = [type(m).__name__ for m in received]
    print(f"  [{label}] 模型收到 {len(received)} 条：{kinds}")
    print(f"      {[(type(m).__name__, m.content) for m in received]}")

print()
print("  → 三种写法归一化成同一件事：一条 system + 一条 human。")
print("    模型侧永远只认消息对象：字符串被包成一条 HumanMessage，dict 被逐条转换。")
print()

# 反例：单独一条 dict 不合法
try:
    probe.invoke({"role": "user", "content": "hi"})
    print("  单条 dict → 竟然通过了")
except Exception as exc:  # noqa: BLE001
    print(f"  单条 dict → {type(exc).__name__}: {exc}")
print("  → 「dict 形态」指的是 dict 的**列表**；传单条 dict 会被当成非法输入直接拒绝。")


# ---------------------------------------------------------------------------
# ③ 返回值 AIMessage 的字段结构
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("③ 返回值 AIMessage 的字段结构")
print("=" * 72)

text_reply = ScriptedChatModel(script=[reply("2 + 3 * 2 = 8")]).invoke("2 + 3 * 2 = ？")
print("  一条「正常回答」的 AIMessage：")
print(f"    content            = {text_reply.content!r}   ← 最终文本，最常读的就是它")
print(f"    tool_calls         = {text_reply.tool_calls}   ← 模型请求调用的工具（这里没有）")
print(f"    invalid_tool_calls = {text_reply.invalid_tool_calls}   ← 格式错误的调用尝试")
print(f"    response_metadata  = {text_reply.response_metadata}   ← 假模型是空字典")
print(f"    usage_metadata     = {text_reply.usage_metadata}   ← 假模型是 None")
print(f"    additional_kwargs  = {text_reply.additional_kwargs}")
# 运行 ID 每次都不一样，只打印前缀，保证输出可复现
print(f"    id                 = {text_reply.id.split('--')[0] + '--…' if text_reply.id else None}"
      "   ← 框架自动生成的运行 ID（后半段每次不同）")

print()
print("  一条「请求调用工具」的 AIMessage：")
with_call = ScriptedChatModel(
    script=[tool_call("get_weather", {"city": "上海"}, "call_1")]
).invoke("上海天气")
print(f"    content    = {with_call.content!r}   ← 要调工具时，文本通常为空")
print(f"    tool_calls = {with_call.tool_calls}")
print()
print("  → content / tool_calls 说的是「模型说了什么」；")
print("    response_metadata / usage_metadata 说的是「这次调用花了什么代价」——")
print("    模型版本、结束原因、token 数，都由真实 provider 填。")
print("    假模型不产生这两项，所以这里是空的，不是 bug。")


# ---------------------------------------------------------------------------
# ④ 四种调用形态
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("④ 四种调用形态：invoke / stream / batch / ainvoke")
print("=" * 72)

one = ScriptedChatModel(script=[reply("一次性返回。")]).invoke("你好")
print(f"  invoke  → {one.content!r}")
print("            阻塞：等模型全部生成完，再一次性返回一个 AIMessage。")

chunks = list(ScriptedChatModel(script=[reply("流式输出。")]).stream("你好"))
print(f"  stream  → {len(chunks)} 个 chunk：{[c.content for c in chunks]}")
print("            ⚠️ 假模型只吐 1 个 chunk（一次给整条消息）；")
print("               真实模型逐 token 分多个 chunk，靠 for 循环边收边显示。")

outs = ScriptedChatModel(
    script=[reply("第一"), reply("第二"), reply("第三")]
).batch(["q1", "q2", "q3"])
print(f"  batch   → {[o.content for o in outs]}")
print("            一批输入，按原顺序返回 list；真实场景下框架会并发发请求。")


async def _ainvoke_demo():
    """异步调用：await 期间事件循环可以去干别的事。"""
    model = ScriptedChatModel(script=[reply("异步返回。")])
    return await model.ainvoke("你好")


async_result = asyncio.run(_ainvoke_demo())
print(f"  ainvoke → {async_result.content!r}")
print("            同步版的异步孪生：ainvoke / astream / abatch 三件套。")


# ---------------------------------------------------------------------------
# ⑤ profile 属性与 config 参数
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("⑤ profile 属性与 config 参数（tags / metadata / callbacks）")
print("=" * 72)

print("  profile：LangChain 给模型做的「能力画像」，声明过才有——")
fake_profile = ScriptedChatModel(script=[reply("x")]).profile
print(f"    假模型 profile = {fake_profile!r}（基类不带画像）")
try:
    real_model = init_chat_model("openai:gpt-4o", api_key="sk-placeholder")
    prof = real_model.profile or {}
    picked = {
        k: prof.get(k)
        for k in ("max_input_tokens", "max_output_tokens", "tool_calling", "structured_output")
    }
    print(f"    init_chat_model('openai:gpt-4o').profile（节选）= {picked}")
except Exception as exc:  # noqa: BLE001
    print(f"    （构造失败：{type(exc).__name__}）")
print("    ⚠️ 画像来自「构造」，不代表真实调用行为；本机无 Key，未实测调用。")
print("    → 用途：运行时判断这个模型支不支持工具调用、上下文窗口有多大。")
print()


class TagProbe(BaseCallbackHandler):
    """观测 config 里的 tags / metadata —— 它们不进消息，只能从回调这一侧看见。"""

    def on_chat_model_start(
        self,
        serialized,
        messages,
        *,
        run_id=None,
        parent_run_id=None,
        tags=None,
        metadata=None,
        **kwargs,
    ):
        print(f"    [回调] tags     = {tags}")
        print(f"    [回调] metadata = {metadata}")


print("  config：不改模型，只改「这一次调用」的记账方式")
model = ScriptedChatModel(script=[reply("收到。")])
model.invoke(
    "你好",
    config={
        "tags": ["ch02", "demo"],
        "metadata": {"user_id": "u-42"},
        "callbacks": [TagProbe()],
        "run_name": "my_run",
    },
)
print("    → tags / metadata / run_name 都不进消息、不改模型行为，")
print("      它们是给追踪系统（如 LangSmith）用的记账信息。")
print("      metadata 里多出的 ls_provider / ls_model_type / lc_versions 是框架自动补的。")
print()

pinned = ScriptedChatModel(script=[reply("收到。")]).with_config(
    tags=["pinned"], metadata={"src": "with_config"}
)
print("  with_config：把 tags / metadata 钉在模型对象上")
print(f"    返回对象类型 = {type(pinned).__name__}（不再是 ScriptedChatModel，这是个容易踩的点）")
pinned.invoke("你好", config={"callbacks": [TagProbe()]})
print("    → 返回的是包装后的 Runnable，照样能 invoke，但 isinstance 判断会失败；")
print("      要取回原对象用 .bound。")
