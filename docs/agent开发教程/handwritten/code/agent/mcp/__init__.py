"""agent.mcp：手写 MCP 客户端（纯标准库，无官方 SDK 依赖）。"""
from agent.mcp.client import MCPClient
from agent.mcp.jsonrpc import RpcError, StdioRpc

__all__ = ["MCPClient", "RpcError", "StdioRpc"]
