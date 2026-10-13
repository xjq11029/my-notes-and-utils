"""会话层：管理对话上下文（消息历史 + 工具清单），支持 JSON 持久化。

两条最佳实践，也是两条纪律：
1. 历史上下文一旦写入就不要修改——修改会破坏服务商端 prompt cache 的前缀命中；
2. 上下文里要保留思维链（reasoning_content）——丢了它，推理模型后续轮次的质量会下降。
"""
import json
import os
import tempfile
import uuid


class Session:
    """一次对话的完整上下文。

    - messages: OpenAI 契约形状的消息 dict 列表（system/user/assistant/tool）
    - tools:    绑定给模型的工具 Schema 列表
    - system_prompt 通过构造参数注入（通常来自 render_prompt 的渲染结果）
    """

    def __init__(self, system_prompt: str | None = None, tools: list | None = None) -> None:
        self.id = uuid.uuid4().hex
        self.messages: list[dict] = []
        self.tools: list[dict] = tools or []
        if system_prompt:
            self.add_message({"role": "system", "content": system_prompt})

    def add_message(self, message: dict) -> dict:
        """追加一条消息。只追加，不修改历史——保住 prompt cache 前缀。"""
        self.messages.append(message)
        return message

    # ---------- 持久化 ----------

    def save(self, directory: str | None = None) -> str:
        """保存为 JSON 文件，返回文件路径。默认存到系统临时目录，不污染工程。"""
        directory = directory or os.path.join(tempfile.gettempdir(), "agent-sessions")
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"{self.id}.json")
        with open(path, "w", encoding="utf-8", newline="") as f:
            json.dump(
                {"id": self.id, "tools": self.tools, "messages": self.messages},
                f, ensure_ascii=False, indent=2,
            )
        return path

    @classmethod
    def load(cls, path: str) -> "Session":
        """从 JSON 文件恢复会话。"""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        session = cls.__new__(cls)
        session.id = data["id"]
        session.tools = data.get("tools", [])
        session.messages = data.get("messages", [])
        return session

    # ---------- 调试输出 ----------

    def print_friendly(self) -> None:
        """人类可读的会话概览（截断长文本）。"""
        print(f"=== 会话 {self.id[:8]}…（{len(self.messages)} 条消息）===")
        for m in self.messages:
            role = m.get("role", "?")
            head = {"system": "[系统]", "user": "[用户]", "tool": "[工具]"}.get(role, "[助手]")
            if m.get("tool_calls"):
                calls = ", ".join(tc["function"]["name"] for tc in m["tool_calls"])
                print(f"{head} 请求调用工具: {calls}")
                continue
            text = m.get("content")
            if role == "tool":
                text = (text or "").replace("\n", " ")
                print(f"{head}({m.get('name', '')}) {text[:80]}{'…' if len(text) > 80 else ''}")
            elif text:
                text = str(text).replace("\n", " ")
                print(f"{head} {text[:80]}{'…' if len(text) > 80 else ''}")
            else:
                print(f"{head}（无文本内容）")
