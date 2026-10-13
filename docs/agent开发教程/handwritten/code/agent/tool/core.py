"""工具封装：把普通 Python 函数变成模型可调用的 Tool。

三步封装：
1. create_params_model：inspect 函数签名 + Pydantic create_model，
   动态生成参数校验模型（类型来自注解，必填/可选来自默认值）；
2. Tool：包装函数。schema() 产出 OpenAI function calling 的 JSON Schema；
   __call__ 先校验再调用，异常不外抛——返回完整堆栈文本，
   让模型「看见」错误并尝试修正；
3. @tool 装饰器：参数描述写在装饰器里，与函数定义待在一起。
"""
import inspect
import sys
import traceback
from typing import Any, Callable

from pydantic import BaseModel, Field, create_model


def create_params_model(func: Callable, param_descriptions: dict | None = None) -> type[BaseModel]:
    """按函数签名动态创建 Pydantic 参数模型。

    这是整个封装里最「巧」的一步：模型写函数时只写普通 Python 函数，
    参数 Schema 完全由 inspect + create_model 自动生成。
    """
    param_descriptions = param_descriptions or {}
    fields: dict[str, tuple] = {}
    for name, param in inspect.signature(func).parameters.items():
        py_type = param.annotation if param.annotation is not inspect.Parameter.empty else Any
        desc = param_descriptions.get(name, "")
        if param.default is inspect.Parameter.empty:
            fields[name] = (py_type, Field(description=desc))  # 必填：不设默认值
        else:
            fields[name] = (py_type, Field(default=param.default, description=desc))
    return create_model(f"{func.__name__}_params", **fields)


class Tool:
    """一个可被模型调用的工具。

    - schema()：OpenAI function calling 格式的工具定义
    - __call__(**kwargs)：校验参数 → 执行函数 → 统一返回字符串
    - from_mcp()：从 MCP 服务器的工具描述构建（跳过 Pydantic，直接用
      服务器给定的 inputSchema）
    """

    def __init__(self, func: Callable, param_descriptions: dict | None = None,
                 name: str | None = None) -> None:
        self.func = func
        self.name = name or func.__name__
        self.description = inspect.getdoc(func) or ""
        self.param_model = create_params_model(func, param_descriptions)
        self._external_schema: dict | None = None

    # ---------- 构造方式二：来自 MCP ----------

    @classmethod
    def from_mcp(cls, server_name: str, info: dict, call_fn: Callable) -> "Tool":
        """把 MCP 服务器的工具描述包装成 Tool。

        工具名规范为 server__tool，避免不同服务器的同名工具冲突。
        参数 Schema 直接采用服务器返回的 inputSchema，本地不做二次建模。
        """
        tool = cls.__new__(cls)
        tool.func = call_fn
        tool.name = f"{server_name}__{info['name']}"
        tool.description = info.get("description", "")
        tool.param_model = None
        tool._external_schema = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": info.get("input_schema") or {"type": "object", "properties": {}},
            },
        }
        return tool

    # ---------- 行为 ----------

    def schema(self) -> dict:
        if self._external_schema is not None:
            return self._external_schema
        param_schema = self.param_model.model_json_schema()
        properties = {}
        for name, prop in param_schema.get("properties", {}).items():
            item = {"type": prop.get("type", "string"), "description": prop.get("description", "")}
            if "enum" in prop:
                item["enum"] = prop["enum"]
            properties[name] = item
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": param_schema.get("required", []),
                },
            },
        }

    def __call__(self, **kwargs) -> str:
        """执行工具。异常不外抛：返回完整堆栈文本，让模型自己看到错误。"""
        try:
            if self.param_model is not None:
                validated = self.param_model(**kwargs)  # 校验 + 类型转换
                kwargs = validated.model_dump()
            return str(self.func(**kwargs))
        except Exception:
            # 完整堆栈文本回给模型：错误信息越具体，模型越容易自行修正
            return "".join(traceback.format_exception(*sys.exc_info())).rstrip()
