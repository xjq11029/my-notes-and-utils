"""MCP 客户端：把「某个 MCP 服务器上的工具」变成 Agent 可调用的工具。

协议交互只有三步——这就是 MCP 的全部：
1. initialize   —— 握手：交换协议版本与能力声明；
2. tools/list   —— 拉取工具清单（name / description / inputSchema）；
3. tools/call   —— 调用某个工具，取回 content 文本。

与官方 SDK（asyncio + ClientSession）不同，本实现是同步纯标准库，
代码就是协议本身，没有任何隐藏。
"""
from agent.mcp.jsonrpc import RpcError, StdioRpc
from agent.tool.core import Tool


class MCPClient:
    """管理多个 stdio MCP 服务器。

    配置形如::

        {"servers": {
            "time": {"type": "stdio", "command": "python",
                     "args": ["mcp_servers/time_server.py"]},
        }}
    """

    def __init__(self, config: dict) -> None:
        self._config = config.get("servers", {})

    # ---------- 协议三步 ----------

    def _connect(self, server_name: str) -> StdioRpc:
        """启动子进程并完成握手（initialize + initialized 通知）。"""
        cfg = self._config[server_name]
        if cfg.get("type", "stdio") != "stdio":
            raise RpcError(-32601, f"手写客户端只实现了 stdio 传输，"
                                   f"无法连接 {server_name}（type={cfg.get('type')}）")
        rpc = StdioRpc(cfg["command"], cfg.get("args", []))
        rpc.request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "handwritten-agent", "version": "0.1.0"},
        })
        rpc.notify("notifications/initialized")
        return rpc

    def list_tools(self) -> dict[str, list[dict]]:
        """所有服务器的工具清单：{server_name: [{name, description, input_schema}]}。"""
        all_tools: dict[str, list[dict]] = {}
        for name in self._config:
            rpc = self._connect(name)
            try:
                result = rpc.request("tools/list")
            finally:
                rpc.close()
            all_tools[name] = [
                {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "input_schema": t.get("inputSchema", {}),
                }
                for t in result.get("tools", [])
            ]
        return all_tools

    def call_tool(self, server_name: str, tool_name: str,
                  arguments: dict | None = None) -> str:
        """调用工具，返回 content 里的全部文本。"""
        rpc = self._connect(server_name)
        try:
            result = rpc.request("tools/call", {"name": tool_name,
                                                "arguments": arguments or {}})
        finally:
            rpc.close()
        if result.get("isError"):
            text = "\n".join(p.get("text", "") for p in result.get("content", [])
                             if p.get("type") == "text")
            raise RpcError(-32000, f"工具执行出错：{text}")
        return "\n".join(p.get("text", "") for p in result.get("content", [])
                         if p.get("type") == "text")

    # ---------- 与工具注册表对接 ----------

    def register_tools(self, registry) -> list[Tool]:
        """把每个 MCP 工具包装成 Tool 注册进 registry，返回注册的工具列表。

        注册之后，Agent 侧对「本进程工具」与「MCP 远程工具」完全无感知——
        这正是 MCP 作为协议的价值：工具的来源被协议抹平了。
        """
        tools: list[Tool] = []
        for server_name, infos in self.list_tools().items():
            for info in infos:
                call_fn = self._make_call_fn(server_name, info["name"])
                tools.append(registry.register(
                    Tool.from_mcp(server_name, info, call_fn)))
        return tools

    def _make_call_fn(self, server_name: str, tool_name: str):
        """为单个 MCP 工具生成调用函数（闭包绑定服务器与工具名）。"""

        def call_fn(**arguments):
            return self.call_tool(server_name, tool_name, arguments)

        return call_fn
