# -*- coding: utf-8 -*-
"""第 7 章配套：一个最小的 MCP stdio server。

它只做两件事：暴露 `add` 与 `echo` 两个工具，走 stdio 传输。
`07_tools.py` 的 Python 客户端与 `07_tools.ts` 的 TypeScript 客户端
都连接这个文件——MCP 是语言无关的协议，server 用什么写不重要。

运行（通常由客户端拉起，不需要手工启动）：
    python 07_mcp_server.py

注意：stdout 只能走 JSON-RPC；日志一律写 stderr，否则协议会被污染。
"""

from fastmcp import FastMCP

mcp = FastMCP("demo-tools")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


@mcp.tool()
def echo(text: str) -> str:
    """Return the text unchanged."""
    return text


if __name__ == "__main__":
    mcp.run(transport="stdio")
