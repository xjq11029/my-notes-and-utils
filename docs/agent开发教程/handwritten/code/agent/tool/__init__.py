"""工具注册表：全局唯一的工具调度中心。

职责只有两个：
- schemas()：把所有已注册工具的 Schema 交给 session.tools；
- invoke(message)：模型返回 tool_calls 后，查表、执行、回填成 tool 消息。
"""
import json

from agent.tool.core import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> Tool:
        self._tools[tool.name] = tool
        return tool

    def schemas(self) -> list[dict]:
        """所有工具的 Schema 列表，可直接赋给 session.tools。"""
        return [t.schema() for t in self._tools.values()]

    def invoke(self, message: dict) -> list[dict] | None:
        """从 assistant 消息中提取 tool_calls 并逐个执行。

        没有工具调用时返回 None——这正是 ReAct 循环的终止信号。
        每个 tool_call 对应一条 role=tool 的消息（带 tool_call_id）。
        """
        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            return None
        results = []
        for tc in tool_calls:
            name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"] or "{}")
            except json.JSONDecodeError:
                args = None
            tool = self._tools.get(name)
            if args is None:
                result = f"错误：arguments 不是合法 JSON：{tc['function']['arguments']!r}"
            elif tool is None:
                result = f"错误：没有名为 {name} 的工具，请检查工具名拼写"
            else:
                result = tool(**args)
            results.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "name": name,
                "content": result,
            })
        return results


def tool(**param_descriptions):
    """装饰器：把函数包装成 Tool，参数描述与函数定义写在一起。

    用法::

        @tool(filepath="文件的绝对路径")
        def read_file(filepath: str) -> str:
            \"\"\"读取文件内容并以字符串形式返回\"\"\"
            ...
    """

    def decorator(func):
        return Tool(func, param_descriptions)

    return decorator


# 全局单例：整个进程共享一个工具注册表
registry = ToolRegistry()
