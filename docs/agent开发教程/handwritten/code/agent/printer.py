"""控制台打印监听器：把事件流翻译成人可读的终端输出。

不用颜色码，保证在任何终端 / 重定向到文件时可读。
"""
from agent.events import Event
from agent.listener import ModelListener


class ModelPrinterListener(ModelListener):
    """开发调试用：实时打印思考 / 正文 / 工具调用。

    show_reasoning=False 时不打印思考正文（只提示「思考中」），
    避免长思维链淹没输出。
    """

    def __init__(self, show_reasoning: bool = False) -> None:
        self.show_reasoning = show_reasoning
        self.listening = True  # 置为 False 可临时静音

    def _handler(self, event: str, **data) -> None:
        if not self.listening:
            return
        if event == Event.REASONING_START:
            if self.show_reasoning:
                print("思考：", end="", flush=True)
            else:
                print("（思考中…）", flush=True)
        elif event == Event.REASONING:
            if self.show_reasoning:
                print(data.get("text", ""), end="", flush=True)
        elif event == Event.REASONING_END:
            if self.show_reasoning:
                print()
        elif event == Event.CONTENT_START:
            print("内容：", end="", flush=True)
        elif event == Event.CONTENT:
            print(data.get("text", ""), end="", flush=True)
        elif event == Event.CONTENT_END:
            print()
        elif event == Event.TOOL_CALL_END:
            for name in data.get("names", []):
                print(f"调用工具: {name}")
