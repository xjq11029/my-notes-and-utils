"""一个手写的 MCP 服务器：纯标准库，约 130 行。

把 stdin 的每一行当一条 JSON-RPC 消息，处理后把响应写成一行输出到
stdout；日志一律走 stderr（stdout 是协议通道，不能被污染）。

协议只要求实现三种消息：initialize / tools/list / tools/call。
提供两个工具：
- get_current_time：动态结果（时间随运行而变）
- add：确定性结果（a+b，便于验证协议与复现输出）
"""
import json
import sys
from datetime import datetime

SERVER_INFO = {"name": "handwritten-time", "version": "0.1.0"}
PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {
        "name": "get_current_time",
        "description": "获取指定时区的当前时间",
        "inputSchema": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "IANA 时区名，如 Asia/Shanghai"},
            },
        },
    },
    {
        "name": "add",
        "description": "计算两个整数的和（确定性工具，用于验证协议）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "第一个整数"},
                "b": {"type": "integer", "description": "第二个整数"},
            },
            "required": ["a", "b"],
        },
    },
]


def get_current_time(timezone: str = "Asia/Shanghai") -> str:
    from zoneinfo import ZoneInfo  # 标准库（Python 3.9+）
    try:
        now = datetime.now(ZoneInfo(timezone))
    except Exception:
        return f"错误：无法识别时区 {timezone}"
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


def add(a: int, b: int) -> str:
    return str(a + b)


def _result(req_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def handle(request: dict) -> dict | None:
    """处理一条 JSON-RPC 消息；通知返回 None（不回应）。"""
    method = request.get("method")
    req_id = request.get("id")

    if method == "initialize":
        return _result(req_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        })
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return _result(req_id, {"tools": TOOLS})
    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        try:
            if name == "get_current_time":
                text = get_current_time(**args)
            elif name == "add":
                text = add(**args)
            else:
                return _result(req_id, {
                    "content": [{"type": "text", "text": f"未知工具 {name}"}],
                    "isError": True,
                })
            return _result(req_id, {"content": [{"type": "text", "text": text}]})
        except TypeError as e:
            return _result(req_id, {
                "content": [{"type": "text", "text": f"参数错误：{e}"}],
                "isError": True,
            })
    if req_id is not None:
        return {"jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32601, "message": f"未知方法 {method}"}}
    return None


def main() -> None:
    print(f"[{SERVER_INFO['name']}] 已启动，等待请求", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            print(f"[{SERVER_INFO['name']}] 非法 JSON 行已忽略", file=sys.stderr)
            continue
        response = handle(request)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    print(f"[{SERVER_INFO['name']}] stdin 已关闭，退出", file=sys.stderr)


if __name__ == "__main__":
    main()
