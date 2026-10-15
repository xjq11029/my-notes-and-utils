# 手写线：不依赖框架，从零实现一个 Agent

手写线回答的问题是：**LangChain 这些框架在你点 `invoke` 的那一下，底下到底发生了什么？** 本线不引入任何 Agent 框架，只用 OpenAI 兼容的模型接口 + 两个基础库（`pydantic` / `jinja2`），从一份 JSON 契约开始，逐章手写出会话、工具系统、ReAct 循环、完整 Agent、Skill 渐进式披露、MCP 客户端与服务器、子代理——最后收束为五大 Engineering 方法论。

> **三条线的分工**：`docs/harness/` 回答「**为什么需要 harness**」（原理篇）；框架线 `ch01–ch19` 回答「**用现成框架怎么搭**」（工程篇）；本线回答「**框架底下是什么**」（实现篇）。手写线的每一章都能在框架线找到对应物，正文逐处标注对照关系。三条线可独立阅读，也可按 原理 → 手写 → 框架 的顺序连读。

---

## 交付物

| 文件 | 类型 | 说明 |
|---|---|---|
| `ch_s01`–`ch_s11*.md` | 教程正文 | 11 章，沿用框架线统一骨架：这一章要解决的问题 → 机制与原理 → 代码 → 常见坑与边界条件 → 关键结论 → 本章要点回顾 |
| `code/` | 示例代码 | Python 单语言，**10 个脚本全部离线实跑通过**（脚本化假模型，无需 API Key）；含最终形态的 `agent/` 包与手写 MCP 服务器 |
| `assets/` | 配图 | 自绘 SVG（深色面板）+ 2× PNG 导出（Markdown 引用 PNG） |
| `code/README.md` | 元文件 | 代码结构、章节映射、实测环境、与参考课件的实现差异清单 |

---

## 章节目录

| 章 | 文件 | 主题 | 框架线对应 |
|---|---|---|---|
| S1 | [ch_s01_model_contract.md](ch_s01_model_contract.md) | 模型接口契约：Chat Completions 的请求 / 响应 / 流式 | 第 2 章 |
| S2 | [ch_s02_system_prompt.md](ch_s02_system_prompt.md) | 系统提示词：五原则与 Jinja2 环境注入 | 第 3 章 |
| S3 | [ch_s03_session.md](ch_s03_session.md) | 会话：模型无状态，记忆靠客户端；两条历史纪律 | 第 3 / 11 章 |
| S4 | [ch_s04_tools.md](ch_s04_tools.md) | tools 裸流程：手动拼 Schema、手动执行、手动回填 | 第 7 章 |
| S5 | [ch_s05_tool_package.md](ch_s05_tool_package.md) | 封装 tools：`@tool` 装饰器、动态参数模型、注册表 | 第 7 章 |
| S6 | [ch_s06_react.md](ch_s06_react.md) | ReAct：事件系统 + 手写循环（Agent 的心脏） | 第 5 章 |
| S7 | [ch_s07_agent.md](ch_s07_agent.md) | Agent：分层编排、监听器、max_turns 安全阀 | 第 5 / 6 章 |
| S8 | [ch_s08_skill.md](ch_s08_skill.md) | Skill：SKILL.md 与渐进式披露 | 第 17 章 |
| S9 | [ch_s09_subagent.md](ch_s09_subagent.md) | 子代理：上下文防火墙 | 第 16 章 |
| S10 | [ch_s10_mcp.md](ch_s10_mcp.md) | MCP：手写客户端与服务器、Skill vs MCP 对照 | 第 7 章 |
| S11 | [ch_s11_engineering.md](ch_s11_engineering.md) | 五大 Engineering：Prompt / Context / Harness / Loop / Graph | 第 9 章等 |

**推荐学习顺序**：按章顺序通读（S1→S11 是一条「从契约到方法论」的递进线）。赶时间的最小闭环是 S1 → S3 → S4 → S5 → S6 → S7（契约 → 提示词与会话 → 工具 → 封装 → 循环 → 组装），大约等于一个 Agent 的全部主干——S6 / S7 的代码直接用到 S3 的 `Session` 与 S5 的 `registry`，这两章不建议跳。**S10（MCP）是全线认知负荷峰值的一章**，赶时间可先读 S9 再回读 S10。

---

## 术语表（按首见章节排序）

| 术语 | 中文注释 | 首见 |
|---|---|---|
| Chat Completions | OpenAI 的对话补全接口，事实上的行业标准契约 | S1 |
| `finish_reason` | 本轮结束原因：`stop`（正常答完）/ `tool_calls`（请求调工具） | S1 |
| delta | 流式 chunk 里「增量」字段的名字，正文/思考/工具调用都从这里出 | S1 |
| 系统提示词 | 消息列表最前面的 `system` 消息，模型行为设定的载体 | S2 |
| 渐进式披露 | 先给清单（几十 token），命中再给全文——Skill 的核心机制 | S2 / S8 |
| prompt cache | 服务商按请求前缀缓存 KV 的机制——历史只追加就是为了命中它 | S3 |
| tool calling | 模型在响应中「点菜」（请求调用工具），执行永远是客户端的事 | S4 |
| JSON Schema | 工具参数的声明式描述，模型选工具与填参数的唯一依据 | S4 |
| 注册表（registry） | 工具的调度中心：`schemas()` 供清单、`invoke()` 管执行 | S5 |
| ReAct | Reasoning + Acting：思考 → 行动 → 观察 的循环模式 | S6 |
| 事件通道 | 流式响应的三条并行数据流：思考 / 正文 / 工具调用 | S6 |
| 上下文防火墙 | 子代理用独立会话消化细节，只把结论带回主上下文 | S9 |
| JSON-RPC 2.0 | MCP 的消息格式：请求/响应靠 `id` 配对，通知无 `id` | S10 |
| Harness | 围绕模型循环的一切工程——挽具；五大 Engineering 之一 | S11 |

---

## 与参考课件的关系

本线以《Agents底层逻辑》课程（袁进，[`gitee.com/dev-edu/agent-core`](https://gitee.com/dev-edu/agent-core)，本机课件位于 `D:\资文件\agent-core`）的工程篇（15–29 章）与方法论篇（30–34 章）为参考脉络重写。**不是逐字搬运**：实现做了三处有意调整（单一最终形态的 agent 包、手写 MCP 替代官方 SDK、`os.getenv` 替代 pydantic-settings），差异清单见 [`code/README.md`](code/README.md)；原理篇（02–14 章）未搬入——相关内容已由 [`大模型与神经网络原理笔记/`](../大模型与神经网络原理笔记/README.md) 覆盖。

逐章来源与实测差异登记在 [`../_写作大纲与来源登记.md`](../_写作大纲与来源登记.md)（内部元文件）。

---

## 维护约定

- 章节骨架与框架线一致（六段式）；改示例代码必须重跑对应脚本，并把输出同步进正文
- 配图：SVG 源与 PNG **必须成对**；SVG 的 `width`/`height` 必须与 `viewBox` 相同；改 SVG 后重跑

```bash
node scripts/svg-to-png.mjs "docs/agent开发教程/handwritten/assets"
```

- 图号 `h1`–`h11` **手写线内部连续**（与框架线的图 1–32 相互独立）；marker `id` 带图号前缀（`ar1h`…），供 HTML 精读版内联去重
- 事实纪律同框架线：**实测优先**、英文引用附中译、不臆造数字

---

## 已知限制

- **真实模型端到端未实测**：本机无模型 API Key，示例用脚本化假模型验证**结构**（循环、协议、注册表、事件流）。凡只有真实模型才能暴露的行为（工具选择倾向、提示词遵从度、真实 token 计费、思考字段的厂商差异细节）不在实测范围内，正文逐处标注「需 API Key，未实测」。
- **MCP 只实现 stdio 传输**：HTTP（streamable）传输在 `agent/mcp/client.py` 显式报错留作练习——协议三步消息两种传输完全一致。
- **参考课件的说法按本机实测校准**：课件基于特定模型与 SDK 版本（如 openai 1.74、mcp 1.28），本线只对「协议结构」负责，不绑定具体模型行为。
