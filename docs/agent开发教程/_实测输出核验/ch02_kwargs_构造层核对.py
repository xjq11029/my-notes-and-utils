# -*- coding: utf-8 -*-
"""ch02 §2.2 / 坑 2 / 坑 3 的构造层核对（2026-10-19）。

**不发任何请求、不需要 API Key**——只构造对象、读字段。核对三件事：
  A. init_chat_model 的真实签名（它自己的参数到底有几个）
  B. 未知 kwargs 会不会报错（结论：不报错，静默进 model_kwargs + 一条 UserWarning）
  C. 不传凭据是否在构造期失败（结论：因集成而异）

运行：python ch02_kwargs_构造层核对.py > ch02_kwargs_构造层核对.txt
"""

import inspect
import os
import sys
import warnings

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import langchain
from langchain.chat_models import init_chat_model

print("环境：langchain", langchain.__version__)
import langchain_openai
import langchain_anthropic

print("      langchain-openai", langchain_openai.__version__)
print("      langchain-anthropic", langchain_anthropic.__version__)
print("      ANTHROPIC_API_KEY 是否已设：", bool(os.environ.get("ANTHROPIC_API_KEY")))
print("      OPENAI_API_KEY 是否已设：", bool(os.environ.get("OPENAI_API_KEY")))

print("\n" + "=" * 72)
print("A. init_chat_model 的真实签名")
print("=" * 72)
print(" ", inspect.signature(init_chat_model))

print("\n" + "=" * 72)
print("B. 未知 kwargs：报错，还是静默失效？")
print("=" * 72)


def probe(label, **kw):
    print(f"\n  {label}")
    print(f"    传入：{kw}")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            m = init_chat_model(kw.pop("spec"), **kw)
        except Exception as exc:  # noqa: BLE001 - 报错本身就是要核对的结果
            print(f"    → 抛错 {type(exc).__name__}: {str(exc).splitlines()[0]}")
            return
        print(f"    → 构造成功：{type(m).__name__}（**没有报错**）")
        for name in ("openai_api_base", "anthropic_api_url", "temperature"):
            if hasattr(m, name):
                print(f"       {name} = {getattr(m, name)!r}")
        print(f"       model_kwargs = {getattr(m, 'model_kwargs', None)!r}")
        for w in caught:
            print("       [UserWarning]", " ".join(str(w.message).split())[:120])


probe("B1｜把 DeepSeek 的地址参数名给 ChatOpenAI",
      spec="openai:gpt-4o", api_key="sk-placeholder", api_base="https://api.deepseek.com/v1")
probe("B2｜参数名拼错（temperature → temperture）",
      spec="openai:gpt-4o", api_key="sk-placeholder", temperture=0)
probe("B3｜换一个集成，传一个不存在的参数名",
      spec="anthropic:claude-sonnet-4-5", api_key="sk-placeholder", totally_bogus_kwarg=123)
probe("B4｜对照组：参数名写对",
      spec="openai:gpt-4o", api_key="sk-placeholder", base_url="https://api.deepseek.com/v1",
      temperature=0, max_tokens=128)

print("\n" + "=" * 72)
print("C. 不传凭据：构造期就失败，还是推迟到调用？")
print("=" * 72)
for spec in ("openai:gpt-4o", "anthropic:claude-sonnet-4-5"):
    try:
        m = init_chat_model(spec)
        print(f"  {spec:32s} 无 key → 构造成功：{type(m).__name__}（报错会推迟到调用）")
    except Exception as exc:  # noqa: BLE001
        print(f"  {spec:32s} 无 key → {type(exc).__name__}: {str(exc).splitlines()[0][:100]}")

print("\n" + "=" * 72)
print("D. 字段本名 vs 别名（本机核对 model_fields）")
print("=" * 72)
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

for cls in (ChatOpenAI, ChatAnthropic):
    print(f"\n  {cls.__name__}")
    fields = cls.model_fields
    for name, label in (("openai_api_base", "地址"), ("openai_api_key", "密钥"),
                        ("anthropic_api_url", "地址"), ("anthropic_api_key", "密钥"),
                        ("max_tokens", "输出上限"), ("temperature", "温度")):
        if name in fields:
            f = fields[name]
            print(f"    {name:18s} ({label})  alias={f.alias!r}  default={f.default!r}")
    print(f"    populate_by_name = {cls.model_config.get('populate_by_name')}")

print("\n  BaseChatModel 的 pydantic extra 配置：", end=" ")
from langchain_core.language_models.chat_models import BaseChatModel

print(repr(BaseChatModel.model_config.get("extra")))
