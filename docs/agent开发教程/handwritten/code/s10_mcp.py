"""s10 MCP：手写客户端、手写服务器、Agent 接入——全程离线。

运行：python s10_mcp.py

MCP 的本质是「工具来源的标准化」：
- 传输：stdio（一行一条 JSON-RPC 消息的子进程）；
- 三步协议：initialize 握手 → tools/list 发现 → tools/call 调用；
- 注册进工具注册表后，Agent 对「本进程工具」与「MCP 远程工具」零感知。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _fake_llm import FakeClient

from agent.agent import Agent
from agent.mcp import MCPClient
from agent.mcp.jsonrpc import StdioRpc

here = os.path.dirname(os.path.abspath(__file__))
server_script = os.path.join(here, "mcp_servers", "time_server.py")
server_config = {
    "servers": {
        "time": {"type": "stdio", "command": sys.executable, "args": [server_script]},
    }
}

# ------------------------------------------------------------------
# 1) 裸协议：手动走一遍三步交互（看最原始的 JSON）
# ------------------------------------------------------------------
print("== 1. 裸协议：initialize → tools/list → tools/call ==")
rpc = StdioRpc(server_config["servers"]["time"]["command"],
               server_config["servers"]["time"]["args"])
result = rpc.request("initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "handwritten-agent", "version": "0.1.0"},
})
print("initialize →", json.dumps(result, ensure_ascii=False))
rpc.notify("notifications/initialized")

result = rpc.request("tools/list")
print("tools/list  →", json.dumps(result, ensure_ascii=False)[:160], "…")

result = rpc.request("tools/call", {"name": "add", "arguments": {"a": 123, "b": 456}})
print("tools/call  →", json.dumps(result, ensure_ascii=False))
rpc.close()

# ------------------------------------------------------------------
# 2) MCPClient 封装：发现与调用
# ------------------------------------------------------------------
print("\n== 2. MCPClient：list_tools / call_tool ==")
mcp = MCPClient(server_config)
for server, tools in mcp.list_tools().items():
    for t in tools:
        print(f"[{server}] {t['name']}：{t['description']}")

print("call_tool(add) →", mcp.call_tool("time", "add", {"a": 123, "b": 456}))
print("call_tool(get_current_time) →", mcp.call_tool("time", "get_current_time",
                                                      {"timezone": "Asia/Shanghai"}),
      "（时间值随运行时刻变化）")

# ------------------------------------------------------------------
# 3) Agent 接入：MCP 工具注册进注册表后，Agent 零感知
# ------------------------------------------------------------------
print("\n== 3. Agent 接入 MCP ==")
from agent.tool import registry
mcp.register_tools(registry)
print("注册表现有工具:", [s["function"]["name"] for s in registry.schemas()])

def tool_text(msgs):
    return " ".join(m.get("content") or "" for m in msgs if m.get("role") == "tool")


client = FakeClient([
    {"match": "几点",
     "resp": {"tool_calls": [{"name": "time__get_current_time",
                              "arguments": {"timezone": "Asia/Shanghai"}}]}},
    {"match": lambda msgs: "CST" in tool_text(msgs) or "2026" in tool_text(msgs),
     "resp": {"tool_calls": [{"name": "time__add", "arguments": {"a": 123, "b": 456}}]}},
    {"match": lambda msgs: "579" in tool_text(msgs),
     "resp": {"content": "现在是上海时间（见工具返回）；另外 123 + 456 = 579。"}},
])

agent = Agent(client=client, auto_builtin=False)
agent.invoke("现在几点了？顺便算一下 123 + 456")
agent.session.print_friendly()
