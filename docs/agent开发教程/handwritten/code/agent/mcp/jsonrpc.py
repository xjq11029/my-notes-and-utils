"""手写 MCP 传输层：JSON-RPC 2.0 over stdio（换行分隔）。

MCP 的 stdio 传输没有魔法：
- 一条消息 = 一行 JSON（禁止内嵌换行）；
- 客户端把请求写成一行写进子进程 stdin；
- 服务端把响应写成一行写回 stdout（日志必须走 stderr，否则污染协议通道）；
- 双方靠 id 字段匹配请求与响应；无 id 的是通知，不期待响应。

这是教学实现：readline 是阻塞读，没有超时——生产实现必须加超时与
并发读（官方 SDK 用 asyncio 解决）。
"""
import json
import os
import subprocess
import uuid


class RpcError(Exception):
    """JSON-RPC 错误响应，或传输层异常。"""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


class StdioRpc:
    """启动一个子进程，并与之进行同步 JSON-RPC 通信。"""

    def __init__(self, command: str, args: list[str] | None = None) -> None:
        self.proc = subprocess.Popen(
            [command, *(args or [])],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # 服务器日志走 stderr；示例中丢弃以保持输出干净
            text=True,
            encoding="utf-8",
            bufsize=1,  # 行缓冲：写一行立刻可被对方读到
        )
        self._closed = False

    # ---------- 发送 ----------

    def notify(self, method: str, params: dict | None = None) -> None:
        """发送通知（无 id，不期待响应）。"""
        self._send({"jsonrpc": "2.0", "method": method,
                    **({"params": params} if params is not None else {})})

    def request(self, method: str, params: dict | None = None) -> dict:
        """发送请求并等待同 id 的响应；途中遇到的其他行一律忽略。"""
        req_id = uuid.uuid4().hex[:8]
        self._send({"jsonrpc": "2.0", "id": req_id, "method": method,
                    **({"params": params} if params is not None else {})})
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RpcError(-32000, "服务器提前退出（stdout 已关闭）")
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue  # 不是 JSON 的行（脏输出）忽略
            if msg.get("id") == req_id:
                if "error" in msg:
                    err = msg["error"]
                    raise RpcError(err.get("code", -32603), err.get("message", "unknown error"))
                return msg.get("result", {})
            # 其他消息（服务器主动通知等）忽略

    def _send(self, payload: dict) -> None:
        if self._closed:
            raise RpcError(-32000, "连接已关闭")
        self.proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

    # ---------- 生命周期 ----------

    def close(self) -> None:
        """关闭 stdin，等待子进程退出（服务器以 stdin EOF 为退出信号）。"""
        if self._closed:
            return
        self._closed = True
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
