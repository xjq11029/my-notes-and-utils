r"""流式装配器的健壮性探针：真实 OpenAI 在 stream_options={"include_usage": True}
下会在流末尾发一个 **choices 为空数组** 的 usage-only chunk。

model.py:155 是 `self._feed(chunk.choices[0].delta)`，没有对空 choices 做防护。
本脚本构造这种尾块，看装配器会不会崩。

这不是挑刺：S1 教的正是「流式契约」，而 include_usage 是拿 token 账的唯一途径——
装配器扛不住它，S1 的「计费」这条就补不上。
"""
import pathlib
import sys
from types import SimpleNamespace

sys.stdout.reconfigure(encoding="utf-8")
HERE = pathlib.Path(__file__).resolve().parents[2] / "handwritten" / "code"
sys.path.insert(0, str(HERE))

from agent.model import _StreamAssembler, Model  # noqa: E402


def d(**kw):
    return SimpleNamespace(**kw)


def c(delta=None, finish=None, choices_empty=False):
    if choices_empty:
        return d(id="x", object="chat.completion.chunk", model="m", choices=[])
    return d(id="x", object="chat.completion.chunk", model="m",
             choices=[d(index=0, delta=delta, finish_reason=finish)])


RULE = "=" * 74

print(RULE)
print("A. 普通流（不含 usage-only 尾块）——基线")
print(RULE)
chunks = [c(delta=d(role="assistant", content="")), c(delta=d(content="你好")),
          c(delta=d(content="，世界")), c(delta=d(), finish="stop")]
try:
    msg = _StreamAssembler(Model(client=object())).consume(chunks)
    print(f"  ✅ 正常装配: {msg}")
except Exception as e:
    print(f"  ❌ {type(e).__name__}: {e}")

print()
print(RULE)
print("B. 带 usage-only 空 choices 尾块（OpenAI include_usage 的真实形状）")
print(RULE)
chunks = [c(delta=d(content="你好")), c(delta=d(), finish="stop"),
          c(choices_empty=True)]
try:
    msg = _StreamAssembler(Model(client=object())).consume(chunks)
    print(f"  ✅ 扛住了: {msg}")
except Exception as e:
    print(f"  ❌ 崩溃: {type(e).__name__}: {e}")
    print("     → model.py:155 `chunk.choices[0].delta` 对空 choices 无防护。")
    print("       而 include_usage 是流式下唯一能拿到 token 账的途径，")
    print("       所以「流式 + 计费」这条路当前是走不通的。")

print()
print(RULE)
print("C. 对照：真实 SDK 是否真的会发空 choices？（查 SDK 类型定义）")
print(RULE)
import openai.types.chat.chat_completion_chunk as ccc  # noqa: E402
f = ccc.ChatCompletionChunk.model_fields
print(f"  choices 字段: required={f['choices'].is_required()} "
      f"default={f['choices'].default!r}")
print(f"  usage 字段  : required={f['usage'].is_required()} "
      f"default={f['usage'].default!r}")
print("  → choices 可为空数组（SDK 允许），故 B 的输入是合法协议形状。")
