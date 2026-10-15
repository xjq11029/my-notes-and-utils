"""从零手写的 Agent 包：最终形态。

模块演进对应各章：
    s01 模型接口契约 →（无代码，本包尚未出现）
    s02 系统提示词   → config / model / prompt(+prompt/system.j2)
    s03 会话         → session
    s04 tools        →（裸协议演示，不进包）
    s05 封装tools    → tool/core + tool/__init__(registry) + tool/builtin
    s06 ReAct        → events（事件系统，model 层此前已用上）
    s07 Agent        → agent + listener + printer
    s08 Skill        → skill
    s10 MCP          → mcp/jsonrpc + mcp/client
    s09 子代理       → subagent
"""
