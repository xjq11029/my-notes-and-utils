"""s03 会话：模型无状态，会话靠客户端自己拼消息历史。

运行：python s03_session.py

要点：
- 模型服务不记得上一轮——每次调用都要把完整历史重传一遍；
- 无会话 = 每次只发一条消息 = 模型「失忆」；
- Session 的两条纪律：历史只追加不修改（保 prompt cache）、保留思维链。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _fake_llm import FakeClient

from agent.model import Model
from agent.session import Session


def make_client():
    """同一套剧本造一个新 client。

    match 用函数检查「全部消息历史」：上下文里出现过 uv 且有追问 → 续答；
    只有孤立的「如何安装」→ 说明失忆了。
    """
    return FakeClient([
        {
            "match": lambda msgs: any("uv 是什么" in (m.get("content") or "") for m in msgs)
                                  and not any(m.get("role") == "assistant" for m in msgs),
            "resp": {"content": "uv 是 Astral 用 Rust 写的 Python 包管理器，极快。"},
        },
        {
            "match": lambda msgs: any(m.get("role") == "assistant" and "uv" in (m.get("content") or "")
                                      for m in msgs),
            "resp": {"content": "接着上面的：Windows 用 powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\" 安装。"},
        },
        {
            "match": "如何安装",
            "resp": {"content": "抱歉，你说的「如何安装」是指什么？我们之前没有聊过别的话题。"},
        },
    ])


# ------------------------------------------------------------------
# 1) 对照实验：两个独立 Session（无会话语境）→ 第二次「失忆」
# ------------------------------------------------------------------
print("== 1. 两个独立 Session：第二次调用「失忆」==")
model = Model(client=make_client())
a = Session()
a.add_message({"role": "user", "content": "uv 是什么？"})
model.invoke(a, stream=True)

b = Session()  # 全新的会话：没有 a 的任何历史
b.add_message({"role": "user", "content": "如何安装？"})
model.invoke(b, stream=True)

# ------------------------------------------------------------------
# 2) 有会话：同一 Session 里的追问能接上上文
# ------------------------------------------------------------------
print("\n== 2. 同一 Session 里的追问 ==")
model2 = Model(client=make_client())
s = Session()
s.add_message({"role": "user", "content": "uv 是什么？"})
model2.invoke(s, stream=True)
s.add_message({"role": "user", "content": "如何安装？"})
model2.invoke(s, stream=True)

print("\n== 3. 会话全文（print_friendly）==")
s.print_friendly()

# ------------------------------------------------------------------
# 3) 持久化与恢复
# ------------------------------------------------------------------
path = s.save()
print(f"\n== 4. 已保存到 {path} ==")
restored = Session.load(path)
print(f"恢复后会话 {restored.id[:8]}… 共 {len(restored.messages)} 条消息：")
restored.print_friendly()

# ------------------------------------------------------------------
# 4) 检视：每次调用都重传了完整历史
# ------------------------------------------------------------------
print("\n== 5. 每次请求的 messages 长度（历史是客户端自己重传的）==")
for i, call in enumerate(model2.client.calls):
    roles = [m["role"] for m in call["messages"]]
    print(f"第 {i + 1} 次调用：{len(call['messages'])} 条消息 {roles}")
