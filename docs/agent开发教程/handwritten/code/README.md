# 手写线代码：不依赖框架，从零实现一个 Agent

本目录是手写线（S1–S10）的配套代码。**Python 单语言**，核心依赖只有
`pydantic`（参数校验与动态 Schema）与 `jinja2`（提示词模板）两件套；
事件系统、会话、工具注册表、ReAct 循环、MCP 传输层全部用标准库手写。

**全部示例离线可跑**——模型层注入脚本化的假模型（`_fake_llm.py`），
它返回与 OpenAI SDK 完全一致的数据形状，用于验证「结构」（循环、协议、
注册表、事件流），不验证模型智能。设置 `OPENAI_API_KEY` /
`OPENAI_BASE_URL` / `OPENAI_MODEL` 后把 `FakeClient` 换成 `Model()` 的
默认 client 即可切到真模型（正文逐处标注哪些行为只有真模型才能暴露）。

## 运行

```bash
cd code
python -m venv .venv && . .venv/Scripts/activate   # Windows
pip install -r requirements.txt
python s01_model_contract.py
```

| 脚本 | 演示什么 | 产出 |
|---|---|---|
| `s01_model_contract.py` | Chat Completions 请求/响应/流式三种形态 | 契约结构打印 |
| `s02_system_prompt.py` | Jinja2 渲染系统提示词 + 注入环境变量 | 渲染后的提示词 |
| `s03_session.py` | 无会话失忆 vs 有会话续答、持久化恢复 | 会话 JSON |
| `s04_tools.py` | 裸流程：手动拼 Schema、手动执行、手动回填 | 临时目录 uv.md |
| `s05_tool_package.py` | `@tool` 装饰器、动态参数模型、注册表 | Schema 与校验输出 |
| `s06_react.py` | 事件流 + 手写 ReAct 循环（读→写→答三轮） | summary.txt |
| `s07_agent.py` | Agent 组装、行车记录仪、max_turns 安全阀 | 完整轨迹 |
| `s08_skill.py` | SKILL.md 扫描、清单注入、load_skill 全文加载 | 三次工具往返 |
| `s09_mcp.py` | 手写 MCP 服务器 + 手写客户端 + Agent 接入 | 协议交互 JSON |
| `s10_subagent.py` | 子代理派发与上下文防火墙 | 主/子上下文对比 |

`s11`（五大 Engineering）是方法论章，无代码。

## agent 包结构（最终形态）与章节映射

| 模块 | 职责 | 引入于 |
|---|---|---|
| `agent/config.py` | 环境变量配置（OPENAI_API_KEY 等） | S2 |
| `agent/model.py` | 模型调用（流式装配器 + 事件广播） | S1 讲契约，S2 落码 |
| `agent/prompt.py` + `agent/prompt/system.j2` | 提示词模板渲染 | S2 |
| `agent/session.py` | 会话：消息历史、工具清单、JSON 持久化 | S3 |
| `agent/tool/core.py` | `Tool` 类、`create_params_model` 动态参数模型 | S5 |
| `agent/tool/__init__.py` | 注册表（`registry`）与 `@tool` 装饰器 | S5 |
| `agent/tool/builtin.py` | 内置工具：read_file / write_file / bash_command | S5 |
| `agent/events.py` | 事件总线（发布-订阅） | S6 |
| `agent/listener.py` / `agent/printer.py` | 监听器抽象与控制台打印实现 | S7 |
| `agent/agent.py` | Agent：ReAct 循环编排 + max_turns 安全阀 | S7 |
| `agent/skill.py` | SKILL.md 扫描、清单注入、load_skill 工具 | S8 |
| `agent/mcp/jsonrpc.py` | 手写 JSON-RPC over stdio 传输 | S9 |
| `agent/mcp/client.py` | MCPClient：initialize / tools/list / tools/call | S9 |
| `agent/subagent.py` | create_agent 工具：子代理派发 | S10 |

配套资产：

- `_fake_llm.py`——脚本驱动的假模型（OpenAI SDK 形状，支持流式分片）
- `mcp_servers/time_server.py`——手写 MCP 服务器（纯标准库，约 130 行）
- `skills/weather-report/SKILL.md`、`skills/text-summary/SKILL.md`——示例技能

## 实测环境

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 |
| Python | 3.13.12（隔离 venv） |
| pydantic | 2.14.1 |
| jinja2 | 3.1.6 |
| tzdata | 2025.2（Windows 上 `zoneinfo` 必需） |
| 模型 | 脚本化假模型（`FakeClient`），无 API Key |

## 与参考课件（agent-core）的实现差异

手写线以《Agents底层逻辑》课程（袁进）工程篇为参考脉络，实现做了三处
有意调整，正文已逐处标注：

| # | 参考课件做法 | 本目录做法 | 原因 |
|---|---|---|---|
| 1 | MCP Client/Server 用官方 `mcp` SDK（asyncio） | **手写** stdio JSON-RPC（同步、纯标准库） | 协议只有三步消息，手写后代码就是协议本身；官方 SDK 的 asyncio + 线程同步技巧对初学者是噪音 |
| 2 | 每章一份递进的 `agent/` 包（10 份副本） | **单一最终形态**的包，示例脚本按章取用 | 避免 10 份重复代码；每章 README 标注模块引入关系 |
| 3 | 配置用 pydantic-settings | 三个 `os.getenv` | 「从零」基调；正文注明生产可用 pydantic-settings |

## 已知限制

- **真实模型端到端未实测**：无 API Key，凡只有真模型才能暴露的行为
  （工具选择倾向、提示词遵从度、真实 token 计费、思考型模型的
  reasoning 字段差异）不在实测范围内，正文标注。
- **MCP 只实现 stdio 传输**：HTTP（streamable）传输在 `client.py` 里
  显式报错并提示，留作练习；协议三步消息两种传输完全一致。
- **假模型不验证智能**：工具选择、多轮规划都是脚本写死的；
  假模型验证的是「我们的结构能正确处理这些消息」。
