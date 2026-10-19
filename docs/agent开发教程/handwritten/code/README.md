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
| `s09_subagent.py` | 子代理派发与上下文防火墙 | 主/子上下文对比 |
| `s10_mcp.py` | 手写 MCP 服务器 + 手写客户端 + Agent 接入 | 协议交互 JSON |

`s11`（五大 Engineering）是方法论章，无代码。

## agent 包结构（最终形态）与章节映射

| 模块 | 职责 | 引入于 |
|---|---|---|
| `agent/config.py` | 环境变量配置（OPENAI_API_KEY 等） | S2 |
| `agent/model.py` | 模型调用（流式装配器 + 事件广播） | **S1 即已使用**（`s01_model_contract.py:17` 就 `import Model` 并在 `:33`/`:64` 调用）；S1 讲契约、S1 起就用这个类，S2 只是加上了模板渲染 |
| `agent/prompt.py` + `agent/prompt/system.j2` | 提示词模板渲染 | S2 |
| `agent/session.py` | 会话：消息历史、工具清单、JSON 持久化 | S3 |
| `agent/tool/core.py` | `Tool` 类、`create_params_model` 动态参数模型 | S5 |
| `agent/tool/__init__.py` | 注册表（`registry`）与 `@tool` 装饰器 | S5 |
| `agent/tool/builtin.py` | 内置工具：read_file / write_file / bash_command | S5 |
| `agent/events.py` | 事件总线（发布-订阅） | S6 |
| `agent/listener.py` / `agent/printer.py` | 监听器抽象与控制台打印实现 | S7 |
| `agent/agent.py` | Agent：ReAct 循环编排 + max_turns 安全阀 | S7 |
| `agent/skill.py` | SKILL.md 扫描、清单注入、load_skill 工具 | S8 |
| `agent/mcp/jsonrpc.py` | 手写 JSON-RPC over stdio 传输 | S10 |
| `agent/mcp/client.py` | MCPClient：initialize / tools/list / tools/call | S10 |
| `agent/subagent.py` | create_agent 工具：子代理派发 | S9 |

配套资产：

- `_fake_llm.py`——脚本驱动的假模型（OpenAI SDK 形状，支持流式分片）
- `mcp_servers/time_server.py`——手写 MCP 服务器（纯标准库，约 130 行）
- `skills/weather-report/SKILL.md`、`skills/text-summary/SKILL.md`——示例技能

## 实测环境

| 项 | 值 |
|---|---|
| 日期 | 2026-10-12 首轮；**2026-10-19 复核轮 + 真实模型补测轮** |
| Python | 3.13.12（首轮）→ **3.14.2**（复核轮；`code/` 下未建独立 venv，与框架线共用，`__pycache__` 全为 `cpython-314.pyc`） |
| pydantic | 2.14.1 |
| jinja2 | 3.1.6 |
| tzdata | 2025.2（Windows 上 `zoneinfo` 必需） |
| 模型（示例） | 脚本化假模型（`FakeClient`），**跑示例不需 API Key** |
| 模型（补测） | **智谱 OpenAI 兼容端点** `glm-4-plus` / `glm-4.5-air`，经 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` 注入，走 `Model()` 的默认 client |

**复核轮结果**：`s01`–`s10` **10/10 `exit=0`**，无落盘污染（产物全在临时目录）。原始 stdout 与真实模型实测记录存档在 `../../_实测输出核验/手写线/`。

> **读正文引文前必知**：示例输出里有三类值**每次运行都不同**——会话 id（`uuid4().hex`，`session.py:22`）、临时目录名（`tempfile.mkdtemp`，形如 `agent-s04-xxxxxxxx`）、时间戳。正文引用的这些值**不会**与你的输出逐字相同，这不是 bug 也不是版本差异。S3 / S4 / S7 已在引文旁注明；其余章节按此理解。
>
> 另有三类字段随运行变化：`finish_reason` 之外的模型 `content` 文本（真实模型每次措辞不同）、流式分片数量（假模型固定、真实模型可达数百）、以及 `s07` 的 stderr 警告（被脚本捕获后丢弃，不在 stdout 里）。

## 与参考课件（agent-core）的实现差异

手写线以《Agents底层逻辑》课程（袁进）工程篇为参考脉络，实现做了三处
有意调整，正文已逐处标注：

| # | 参考课件做法 | 本目录做法 | 原因 |
|---|---|---|---|
| 1 | MCP Client/Server 用官方 `mcp` SDK（asyncio） | **手写** stdio JSON-RPC（同步、纯标准库） | 协议只有三步消息，手写后代码就是协议本身；官方 SDK 的 asyncio + 线程同步技巧对初学者是噪音 |
| 2 | 每章一份递进的 `agent/` 包（10 份副本） | **单一最终形态**的包，示例脚本按章取用 | 避免 10 份重复代码；每章 README 标注模块引入关系 |
| 3 | 配置用 pydantic-settings | 三个 `os.getenv` | 「从零」基调；正文注明生产可用 pydantic-settings |

## 真实模型实测（2026-10-19 补测）

把 `FakeClient` 换成 `Model()` 的默认 client（只需设 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL`），
用智谱 OpenAI 兼容端点跑端到端。**「换一下就行」这句话本身已实测成立**——上层代码零改动。

| 验证项 | 结果 |
|---|---|
| 流式装配器 vs 非流式归一化的**字段集合** | 两个模型都一致（含思考型的 `reasoning_content`） |
| 思考通道切分 | `glm-4.5-air`：**535 个 reasoning 分片 + 6 个 content 分片**，边界事件顺序 `reasoning_end → content_start` 正确；`glm-4-plus`：reasoning 分片数 0 |
| 真实模型自选工具 | 正确选中 `get_weather`，ReAct 2 轮 |
| **`tool_calls.arguments` 跨 chunk 拼接** | 拼出 `{"query":"上海"}`，`json.loads` 通过——流式 tool calling 最容易踩的坑，手写装配器扛住了 |
| 手写 MCP + 真实模型 | 端到端跑通，模型选中 `time__get_current_time` |

**结论：这套手写代码在真实模型下没有暴露任何逻辑错误。** 但补测也确认了两个真实缺陷：

### 缺陷 1：模型层拿不到 token 账

`_normalize_message`（`model.py:88-108`）与 `_StreamAssembler` **都不读 `usage` 字段**，
且流式路径把 `InvokeResult.raw` 显式置为 `None`（`model.py:82`）。实测确认：
`message` dict 里没有 `usage` 键；非流式的 `raw.usage` 有值（`{'prompt_tokens':18,'completion_tokens':128,...}`）但没有任何代码消费它。

**影响**：S6 §2.1 与 S7 §2.4 提到的「计费监听器」当前**实现不了**——`complete` 事件只携带 `message`（`model.py:225`），拿不到 token。
**修法**：在 `_invoke` / `_invoke_stream` 里把 `resp.usage` 归一化进 `message["usage"]`，并让流式也保留 `raw`。

### 缺陷 2：流式装配器扛不住 `stream_options={"include_usage": true}`

`model.py:155` 是 `self._feed(chunk.choices[0].delta)`，**对空 `choices` 无防护**。
实测构造 OpenAI 在该模式下的 usage-only 尾块（`choices: []`）→ `IndexError: list index out of range`
（见 `../../_实测输出核验/手写线/stream_robustness_probe.txt`）。

**这条与缺陷 1 是同一个洞的两面**：`include_usage` 正是流式下拿 token 账的唯一途径，
而装配器一遇它的尾块就崩——所以「流式 + 计费」这条路当前完全走不通。
**修法**：`consume` 里加一行守卫 `if not chunk.choices: continue`。

> 注：`choices` 在 OpenAI SDK 类型里是 required 的 list，空数组是合法取值；
> 「`include_usage` 下会发空 `choices` 尾块」是官方文档行为，**本机未对真 OpenAI 验证**（智谱不发该尾块，故示例与上述实测均未触发）。

## 仍未实测

- **提示词遵从度**：本轮只测了协议层与框架机制（自选工具、流式装配、思考通道），没做「模型是否稳定遵守系统提示词」的设计实验。
- **HTTP（streamable）MCP 传输**：`agent/mcp/client.py:34-35` 对非 stdio 显式抛 `RpcError(-32601)`，留作练习；协议三步消息两种传输完全一致。
- **假模型不验证智能**：工具选择、多轮规划在示例里都是脚本写死的；假模型验证的是「我们的结构能正确处理这些消息」，**不是「模型会这样做」**——正文引用假模型输出时请按此理解。
