# Agent 开发教程 · LangChain / LangGraph / Deep Agents

一套自成体系的 **Agent 应用开发教程**，分两条线：**框架线**（本文件，ch01–ch19）讲「用现成框架怎么搭」，从「构建块 → 运行时 → 成品 harness」三层递进，讲清当下最主流的三个 Python / TypeScript Agent 框架，配 **Python 与 TypeScript 双语言实测示例**与自绘机制图；**手写线**（[`handwritten/`](handwritten/README.md)，S1–S11）讲「框架底下是什么」，不依赖框架从零手写会话、工具、ReAct、Agent、Skill、MCP 与子代理。

> **与 [`docs/harness/`](../harness/README.md) 的分工**：那篇回答「**为什么需要 harness**」（Agent = Model + Harness、五个必然问题、12 个组件），是原理篇；本篇回答「**用现成框架怎么搭**」，是工程篇；[手写线](handwritten/README.md)回答「**框架底下是什么**」，是实现篇。三条线可独立阅读，也可连着读。

---

## 怎么读这套教程

- **读者画像**：会 Python 或 TypeScript 基础（函数、类、装饰器、`async` / `await`），用过 HTTP API 即可；**不需要 agent 经验**。第一次见 Pydantic / `TypedDict` / zod 不用慌——第 4 章 2.1、第 11 章 2.1 都给了零基础说明。
- **代码块是节选**：正文里的代码块为了叙事做了删减，**完整可运行版本在 [`code/`](code/README.md)**。建议先按下面的命令跑通一个示例，再回来读正文；「正文片段跑不起来」多半只是缺了节选掉的导入。
- **动手建议**：每章的「要点回顾」可当检查清单；读完一章至少改一个参数（换 reducer、换 `stream_mode`、裁一个工具）并观察输出变化。手写线 S9 / S11 另有自测题。
- **双语言怎么读**：会一种语言即可；只有两语言行为不一致处才需要对照（正文都用对照表标出）。

---

## 交付物

| 文件 | 类型 | 说明 |
|---|---|---|
| `ch01`–`ch19*.md` | 教程正文（框架线） | 19 章，每章统一骨架：这一章要解决的问题 → 机制与原理 → 双语言代码 → 常见坑 → 关键结论 → 本章要点回顾 |
| [`handwritten/`](handwritten/README.md) | **手写线** | S1–S11 共 11 章 + Python 手写代码包 + 11 张配图：从模型接口契约到五大 Engineering，不依赖框架从零实现 Agent |
| `agent-frameworks-deep-dive.html` | 精读版长文 | 单文件自包含（无 CDN / 无外部字体 / 无外部 JS），深色主题，左侧目录滚动高亮，38 张内联 SVG，Python/TypeScript 代码切换。**由脚本生成，不手工改** |
| `_build_html.py` | 元文件 · 构建脚本 | 从 19 章正文 + `assets/` 生成上面那份 HTML。**幂等**；改章节或配图后必须重跑 |
| `code/python/` | 示例代码 | 17 个主示例 + `07_mcp_server.py`（MCP fixture）+ `19_deploy_agent.py` / `langgraph.json`（部署样例）；**全部实跑通过**，离线 Fake 模型无需 API Key（MCP 本地 stdio、`langgraph dev` 除外） |
| `code/typescript/` | 示例代码 | 17 个主示例与 Python 一一对应，**全部实跑通过**；MCP 客户端连接 Python fixture；部署为 Python-only 例外 |
| `assets/` | 配图 | 自绘 SVG 矢量源 + **2× PNG 导出**（Markdown 引用 PNG；SVG 与 HTML 精读版同一份源） |
| `_写作大纲与来源登记.md` | 元文件 | 逐章大纲 + 官方文档 URL + 版本 + **官方文档与本机实测的差异清单**（内部用） |
| [`_写法规范.md`](_写法规范.md) | 元文件 · 写法规范 | 从 `docs/harness/` 与大模型笔记提炼的**叙事改写 + 一致性修复**双轨规范（问题驱动 / 一句话主线 / 推导链 / 类比与最小例子 / 图文码互证 / 口径后置 + 存量例外），第八轮起框架线全章节适用；`ch02_models.md` 是参考实现 |

---

## 全书结构（基础层 + 三件套）

| 层 | 内容 | 定位 | 一句话 |
|---|---|---|---|
| **基础层** | 模型 / 消息 / 提示词 / 结构化输出 | 不碰循环，先把「原料」备齐 | 模型怎么造、话怎么说、结果怎么收 |
| **构建块** | LangChain v1 | 一个**高度可配置的 harness** | `create_agent` 给你循环 + 中间件插槽，自己组装 |
| **运行时** | LangGraph v1 | **图 + 状态 + 持久化**的底层基础设施 | 管状态、管检查点、管中断、管恢复 |
| **成品 harness** | Deep Agents | 在 `create_agent` 之上**预装**一整套能力 | 规划、虚拟文件系统、子代理、记忆开箱即用 |

> RAG（第 8 章）不在这四层里，它是**按需原料章**：放在工具章之后，因为那一章的最后一跳要把检索器包成工具接进 agent。不需要检索的读者可整章跳过。

> **官方口径与原理篇完全一致**：LangChain v1 文档把 Agent 定义为「模型在循环中调用工具直到任务完成」，把 **harness** 定义为「循环之外的一切——提示词、工具，以及任何塑造模型行为的 middleware」。

---

## 章节目录

| 章 | 文件 | 主题 |
|---|---|---|
| 1 | [ch01_landscape.md](ch01_landscape.md) | 三件套定位与心智模型：构建块 / 运行时 / 成品 harness |
| 2 | [ch02_models.md](ch02_models.md) | 模型的创建与调用：三个初始化角度与四种调用形态 |
| 3 | [ch03_messages_prompts.md](ch03_messages_prompts.md) | Message 与提示词模板：四种消息类型与模板渲染 |
| 4 | [ch04_structured_output.md](ch04_structured_output.md) | 结构化输出：四种 schema 模式与两种策略 |
| 5 | [ch05_create_agent.md](ch05_create_agent.md) | `create_agent` 与 Agent Loop：状态、两类作用域、结构化输出 |
| 6 | [ch06_middleware.md](ch06_middleware.md) | 中间件：钩子体系与治理件（HITL / PII / 限额 / 重试） |
| 7 | [ch07_tools_and_context.md](ch07_tools_and_context.md) | 工具与运行时上下文：`@tool`、注入与 MCP 客户端/服务端 |
| 8 | [ch08_rag.md](ch08_rag.md) | RAG 全链路：加载、切分、嵌入、入库与检索 |
| 9 | [ch09_context_engineering.md](ch09_context_engineering.md) | 上下文工程：摘要、裁剪、卸载与缓存前缀 |
| 10 | [ch10_observability.md](ch10_observability.md) | 可观测与评测：追踪、数据集与成本 |
| 11 | [ch11_langgraph_state.md](ch11_langgraph_state.md) | LangGraph 图与状态：Reducer、控制流与节点级容错 |
| 12 | [ch12_langgraph_persistence.md](ch12_langgraph_persistence.md) | 持久化：检查点、子图、durability、时间旅行 |
| 13 | [ch13_langgraph_control.md](ch13_langgraph_control.md) | 人在回路与流式：七档 `stream_mode` 与 `astream_events` |
| 14 | [ch14_deepagents_overview.md](ch14_deepagents_overview.md) | Deep Agents 全景：预装 harness 与 HarnessProfile |
| 15 | [ch15_deepagents_filesystem.md](ch15_deepagents_filesystem.md) | 虚拟文件系统与执行环境：文件工具、权限、后端 |
| 16 | [ch16_deepagents_delegation.md](ch16_deepagents_delegation.md) | 规划与委派：`write_todos` 与子代理 |
| 17 | [ch17_deepagents_context.md](ch17_deepagents_context.md) | 技能与记忆：Skills 渐进式披露与跨会话 Memory |
| 18 | [ch18_multiagent.md](ch18_multiagent.md) | 多智能体协作：三种拓扑与搭法 |
| 19 | [ch19_migration_and_deploy.md](ch19_migration_and_deploy.md) | 迁移与部署：映射表、`langgraph.json` 与本地 `dev` |

**推荐学习顺序**：按章顺序通读（1→19 为叙事线）；只关心某一层可跳读——第 2–4 章是基础层（模型、消息、结构化输出），第 5–9 章是 LangChain（含第 8 章 RAG 全链路），第 11–13 章是 LangGraph，第 14–17 章是 Deep Agents，第 18–19 章是多智能体与工程收尾。**可观测（第 10 章）只依赖第 5 章的 `create_agent`**，关心排查与成本的读者可在第 5 章后跳读它，再回到主线。想先搞懂「框架底下发生了什么」的读者，建议先读[手写线](handwritten/README.md)的 S1 → S3 → S4 → S5 → S6 → S7（契约 → 提示词与会话 → 工具 → 封装 → 循环 → 组装），再回框架线对照。

---

## 术语表（按首见章节排序）

> 「首见」指**首次正式定义或展开**该术语的章节；第 1 章等处的路线图式前向引用不计。

| 术语 | 中文注释 | 首见 |
|---|---|---|
| Harness | 围绕 Agent Loop 的一切：提示词、工具、中间件 | ch1 |
| `init_chat_model` | 按 `"provider:model"` 字符串创建模型的统一入口 | ch2 |
| `profile` | 模型的能力自述：上下文窗口、是否支持工具调用 / 结构化输出 | ch2 |
| `content_blocks` | 消息内容的结构化表示，多模态按块描述 | ch3 |
| `ChatPromptTemplate` | 提示词模板：变量注入后渲染成消息列表 | ch3 |
| `MessagesPlaceholder` | 模板里的消息列表占位符 | ch3 |
| `with_structured_output` | 把模型输出直接解析成 Pydantic 实例等结构化结果 | ch4 |
| `create_agent` | LangChain v1 创建 agent 的入口函数 | ch5 |
| Agent Loop | 调模型 → 执行工具 → 结果回灌 → 再调模型，直到不再请求工具 | ch5 |
| AgentState | agent 的状态容器，内置 `messages` 字段且**只追加** | ch5 |
| `thread_id` | **对话**作用域：决定消息历史与检查点归属 | ch5 |
| `context` | **单次运行**作用域：user_id、feature flag 等，不进检查点 | ch5 |
| Middleware | 挂在 Agent Loop 各阶段的扩展点 | ch6 |
| `wrap_model_call` / `wrap_tool_call` | 「包裹式」钩子：可改写请求、拦截响应、重试 | ch6 |
| `ToolRuntime` | 工具内访问 state / context / store 的注入参数 | ch7 |
| MCP | Model Context Protocol，标准化的工具供给协议 | ch7 |
| Document | RAG 的基本单位：`page_content` 加 `metadata` | ch8 |
| Text Splitter | 把长文档切成短块，`chunk_size` / `chunk_overlap` 可调 | ch8 |
| Embeddings | 把文本映射成定长向量；入库与检索各一个方法 | ch8 |
| Vector Store | 存向量与原文、支持相似度检索的库 | ch8 |
| Retriever | 「输入查询、输出相关 Document」的标准接缝 | ch8 |
| `Command` | 节点内同时「更新状态 + 跳转节点」的指令 | ch11 |
| `StateGraph` | LangGraph 的图构建器 | ch11 |
| Reducer | 决定「节点返回的更新如何合并进当前状态」的函数 | ch11 |
| `add_messages` | 内置 reducer：追加消息并按 ID 去重更新 | ch11 |
| `Send` | 从条件边动态派发并行的 map-reduce 原语 | ch11 |
| 超步（super-step） | 一轮里可以并行执行的节点集合 | ch11 |
| map-reduce | 派发一批并行任务、再把各自结果按 reducer 汇总的模式 | ch11 |
| Checkpointer | 把图状态按检查点落盘的组件 | ch12 |
| Checkpoint | 一次状态快照；同线程可回放与时间旅行 | ch12 |
| Store | 跨线程长期记忆的键值存储 | ch12 |
| Durable execution | 持久执行：崩溃或中断后从最近检查点续跑 | ch12 |
| `interrupt()` | 在图内暂停并等待人工输入的机制 | ch13 |
| `stream_mode` | 流式输出的投影方式（values / updates / messages / custom …） | ch13 |
| `create_deep_agent` | Deep Agents 的入口函数，预装一整套中间件 | ch14 |
| HarnessProfile | 声明式地裁剪 Deep Agents 内置能力 | ch14 |
| Virtual filesystem | 挂载在后端上的文件工具集（`ls`/`read_file`/`write_file`…） | ch15 |
| Backend | 文件与执行的落点（State / Store / Filesystem / Sandbox） | ch15 |
| `write_todos` | 任务规划工具，维护结构化待办列表 | ch16 |
| Subagent | 独立上下文的子代理，用 `task` 工具派发 | ch16 |
| Skills | 按需加载的领域知识包（`SKILL.md`），渐进式披露 | ch17 |
| Memory | 跨会话持久的指令与偏好（`AGENTS.md`） | ch17 |
| HITL | 人在回路：工具调用前暂停，等人 approve/edit/reject/respond | ch6 |
| PII | 个人可识别信息；`PIIMiddleware` 按类型做脱敏 | ch6 |
| MCP server | 以 stdio / HTTP 等传输提供工具的进程 | ch7 |
| `recursion_limit` | 单次图运行允许的最大 super-step 数（本机默认 10007） | ch11 |
| `durability` | 检查点落盘时机：`sync` / `async` / `exit` | ch12 |
| `astream_events` | 按回调事件（模型 token、工具开始/结束）流式输出 | ch13 |
| `langgraph.json` | Agent Server 的部署清单：依赖、图、环境变量、Python 版本 | ch19 |

---

## 示例代码

17 个主示例**一一对应**（Python / TypeScript），另有 MCP 辅助样例与 Python-only 部署样例。**全部离线可跑**——用一个脚本化的假模型替代真实 LLM，**跑示例本身不需要 API Key、不产生网络请求**，结果确定可复现（MCP 走本地 stdio 子进程）。

> **2026-10-16 更新**：原先标「未实测」的、只有真实模型才能验证的条目，已用智谱 OpenAI 兼容端点补测完毕；同时对本教程做了一次全量核验，逐条比对「正文声称的实测」与「示例真实输出」。结论与证据存档在 [`_实测输出核验/`](_实测输出核验/README.md)（含 34 份原始输出、6 张模型输出截图、真实模型抓包记录）。正文里凡标 **（源码核对）/（本机核对）** 的内容，都是这次核验中从「实测」降级出来的——**「实测」现在严格等于「示例输出里能看到」**。

> **双语言阅读说明**：每章第三节的 Python / TypeScript 两段是同一件事的两个语言版本，**会一种即可**；只有双语言行为不一致的地方才值得对照（教程中此类差异均以对照表或「常见坑」显式标出，不要求两边都细读）。

```bash
# Python
cd code/python
python -m venv .venv && . .venv/Scripts/activate   # Windows
pip install -r requirements.txt
python 02_models.py
python 07_tools.py            # 含本地 MCP stdio（会拉起 07_mcp_server.py）
python 19_deploy_agent.py     # 部署样例；配合 langgraph.json 使用

# TypeScript
cd code/typescript
pnpm install
pnpm run 02_models
pnpm run 07_tools             # MCP 段会调用 ../python/.venv
```

| 章节 | Python | TypeScript | 演示什么 |
|---|---|---|---|
| 2 | `02_models.py` | `02_models.ts` | 三种入参归一化、`AIMessage` 结构、stream / batch |
| 3 | `03_messages_prompts.py` | `03_messages_prompts.ts` | 四种消息、历史裁剪、模板的三种调用方式 |
| 4 | `04_structured_output.py` | `04_structured_output.ts` | 四种 schema 模式、校验失败、工具策略自动重试 |
| 5 | `05_create_agent.py` | `05_create_agent.ts` | Agent Loop、状态只追加、结构化输出 |
| 6 | `06_middleware.py` | `06_middleware.ts` | 六个钩子顺序、HITL 审批、PII 脱敏、限额/重试/回退 |
| 7 | `07_tools.py` | `07_tools.ts` | 工具定义、`ToolRuntime` 注入、工具内改状态、MCP stdio 客户端 |
| 8 | `08_rag.py` | `08_rag.ts` | 加载、切分、假嵌入、内存向量库、检索器接成工具 |
| 9 | `09_context.py` | `09_context.ts` | 摘要压缩触发、工具输出卸载 |
| 10 | `10_observability.py` | `10_observability.ts` | trace 结构（离线桩） |
| 11 | `11_state_graph.py` | `11_state_graph.ts` | Reducer、条件边、`Send`、顺序/扇入、循环上限、重试/缓存、Functional API |
| 12 | `12_persistence.py` | `12_persistence.ts` | 检查点、时间旅行、Store、子图 namespace、durability |
| 13 | `13_hitl_stream.py` | `13_hitl_stream.ts` | `interrupt`/`resume`、七档 `stream_mode`、list+subgraphs、`astream_events` |
| 14 | `14_deep_agent.py` | `14_deep_agent.ts` | 预装工具集、HarnessProfile |
| 15 | `15_filesystem.py` | `15_filesystem.ts` | 文件工具与权限判定 |
| 16 | `16_delegation.py` | `16_delegation.ts` | 规划与子代理派发 |
| 17 | `17_skills_memory.py` | `17_skills_memory.ts` | 技能加载与记忆注入 |
| 18 | `18_multiagent.py` | `18_multiagent.ts` | 多智能体拓扑与迁移映射（同时服务第 19 章） |
| 19 | `19_deploy_agent.py` + `langgraph.json` | — | 部署清单、`langgraph validate` / `dev` / `/ok`（Python-only） |

> 第 19 章的部署样例是 **Python-only**（`langgraph-cli` 由 Python 侧分发；TS 侧没有等价的本地 `dev` 样例），其余 17 个主示例双语言一一对应。
>
> 详细说明见 [`code/README.md`](code/README.md)。

---

## 配图

图统一为**自绘 SVG**（深色面板，自带满幅底色）+ **2× PNG 导出**——Markdown 引用 PNG，SVG 供二次编辑。重新渲染：

```bash
node scripts/svg-to-png.mjs "docs/agent开发教程/assets"
```

| 图 | 内容 | 用在 |
|---|---|---|
| 图 1 | 三件套分层：构建块 / 运行时 / 成品 harness | ch01 |
| 图 2 | 版本时间线 | ch01 |
| 图 3 | 模型初始化的三个角度 | ch02 |
| 图 4 | invoke 三种入参 → AIMessage 结构 | ch02 |
| 图 5 | 四种消息类型与字段 | ch03 |
| 图 6 | ChatPromptTemplate 渲染管线与三种产物 | ch03 |
| 图 7 | `with_structured_output` 的两种策略 | ch04 |
| 图 8 | Agent Loop 与中间件挂载点 | ch05、ch06 |
| 图 9 | 状态与两类作用域（thread_id / context） | ch05 |
| 图 10 | 六个钩子在一次工具调用中的真实触发顺序 | ch06 |
| 图 11 | 六大能力域 × 预置中间件 | ch06 |
| 图 12 | 治理中间件栈：HITL / PII / 限额 / 重试在模型与工具调用上的位置 | ch06 |
| 图 13 | 工具调用往返与 `ToolRuntime` 注入 | ch07 |
| 图 14 | MCP 接入与多服务器聚合 | ch07 |
| 图 15 | MCP client–server 的 stdio 管道与工具发现 | ch07 |
| 图 16 | RAG 检索链路 | ch08 |
| 图 17 | 文档切分与向量化 | ch08 |
| 图 18 | 上下文四种手段 | ch09 |
| 图 19 | 缓存前缀边界 | ch09 |
| 图 20 | trace 结构与可观测三层 | ch10 |
| 图 21 | 图的基本构件 | ch11 |
| 图 22 | Reducer 合并语义 | ch11 |
| 图 23 | 条件边与 `Send` 并行 | ch11 |
| 图 24 | 控制流原语与容错面 | ch11 |
| 图 25 | Store 跨线程分层 | ch12 |
| 图 26 | 检查点落盘与恢复 | ch12 |
| 图 27 | 时间旅行 | ch12 |
| 图 28 | 子图命名空间与 durability 时间线 | ch12 |
| 图 29 | interrupt / resume 时序 | ch13 |
| 图 30 | stream_mode 的七种投影 | ch13 |
| 图 31 | 七档投影与 astream_events 事件面 | ch13 |
| 图 32 | Deep Agents 预装中间件栈 | ch14 |
| 图 33 | 文件工具集与权限判定 | ch15 |
| 图 34 | 规划循环 | ch16 |
| 图 35 | 子代理的上下文防火墙 | ch16 |
| 图 36 | 技能渐进式披露与记忆时间尺度 | ch17 |
| 图 37 | 多智能体拓扑 | ch18 |
| 图 38 | `langgraph.json` → Agent Server → Studio / AgentChatUI 部署链路 | ch19 |

---

## 版本与来源

本教程的 API 描述**以实测为准**——所有代码在下列版本上真跑过，文档只用于补足概念与设计意图。

| 组件 | 实测版本 |
|---|---|
| `langchain` | 1.4.2 |
| `langgraph` | 1.2.12 |
| `deepagents` | 0.7.18 |
| `langchain-core` | 1.6.11（1.6.4 是 2026-09-24 首轮） |
| `langchain-openai` / `langchain-anthropic` | 1.7.2 / 1.7.6（1.6.5 / 1.7.4 是首轮） |
| `langchain`（JS） / `@langchain/core`（JS） | 1.5.11 / 1.2.12 |
| `@langchain/langgraph`（JS） / `deepagents`（JS） | 1.4.17 / 1.14.0 |

**来源分级**：

- **一手（官方文档 / 官方仓库）**：`docs.langchain.com` 的 OSS Python 与 JavaScript 文档、`reference.langchain.com` API 参考
- **实测（本仓库）**：本目录 `code/` 下示例的运行输出——**与文档冲突时以实测为准**，差异在正文中显式标注
- **版本锚点**：LangChain v1 与 LangGraph v1 于 **2025-10-22** 同步 GA；`deepagents` 独立演进，**两个语言的版本号不同步**（Python 0.7.x / JS 1.x）

逐章 URL、访问日期与实测记录见 [`_写作大纲与来源登记.md`](_写作大纲与来源登记.md)。

---

## 已知限制

- **真实模型只做了协议层探针，不是全部示例的端到端实测**：17 组主示例仍用脚本化假模型跑框架机制（MCP 与部署样例另计）；2026-10-16 另用智谱 OpenAI 兼容端点补测了流式分块、token / 缓存字段、结构化输出请求体与 `create_agent` 消息序列，证据在 `_实测输出核验/`。仍未实测的是**工具选择倾向、提示词遵从度、模型质量、跨供应商行为**——正文中逐处标注「需真实模型，未实测」。
- **LangSmith 上报未实测**：`LANGSMITH_TRACING` 相关的端到端上报需要账号，ch10 的 trace 结构用离线桩演示，字段名以官方文档为准。
- **TypeScript 类型检查未通过**：`pnpm run typecheck`（`tsc --noEmit`）当前是 `exit=1`、**73 个 `error TS`**（2026-10 增补轮后从 44 增至 73，新增集中在 11/12/13 的泛型标注与中间件工厂类型）；示例靠 `tsx` 运行，**「17/17 通过」只指运行时**。完整清单见 [`code/README.md`](code/README.md) 的「已知未通过项」。
- **MCP 第三方服务器未实测**：本地 stdio server（`07_mcp_server.py`）已端到端实测（Python `MCPAdapter` + TS `MultiServerMCPClient`）；第三方远程 server、鉴权与断连未实测。
- **部署只验证到本地 dev**：`langgraph validate` / `dev` / `/ok` 已实测；Studio / AgentChatUI 页面、Docker build、云端 deploy 未实测。
- **版本漂移**：三个框架迭代很快，且 `deepagents` 的 Python 包与 JS 包**版本号不同步**。**如与最新版本有出入，以官方文档与仓库实际代码为准。**
- **图示为机制示意**：图中的节点名、工具名来自实测，但布局与配色是为讲解服务的，不代表框架内部实现结构。

---

## 维护约定

- 章节骨架固定：`## 一、这一章要解决的问题` → `## 二、机制与原理` → `## 三、代码：Python 与 TypeScript` → `## 四、常见坑与边界条件` → `## 五、关键结论` → `## 本章要点回顾`（ch01 第三节为「安装与环境」；ch19 末尾另有 `## 全书回顾`）
- **结论与回顾分工去重**（2026-10 增补）：`## 五、关键结论` 只放**可迁移的判断 / 口径**（为什么、怎么判断、代价），压到 3–5 条（存量例外见 [`_写法规范.md`](_写法规范.md) §3 第 8 条）；`## 本章要点回顾` 只做**可勾选清单**（事实 + 图号 + 命名 + 互引）。**结论与回顾之间同一条信息只保留一处**（正文必要复述与导航句不计），纯事实不得在结论里罗列——改这两节时按此规则办
- **改动任何示例代码必须重跑**，并把输出同步到正文与 `code/README.md`
- **HTML 由脚本生成，不手工改**：改任何章节或配图后必须重跑，否则 HTML 与章节不一致
  ```bash
  python docs/agent开发教程/_build_html.py
  ```
- 配图：SVG 源与 PNG **必须成对**；改 SVG 后重跑
  ```bash
  node scripts/svg-to-png.mjs "docs/agent开发教程/assets"
  ```
  ⚠️ SVG 的 `width`/`height` 必须与 `viewBox` 相同，否则 `--scale 2` 会得到 4×
- 图号**严格按正文出现顺序全局连续**（1–38）；新增图插入后其后图号顺延；图注、README 配图索引、`_写作大纲与来源登记.md` 三处联动；改图后必须重渲染 PNG 并重跑 `_build_html.py`
- HTML 精读版保持**单文件自包含**；内联 SVG 的 marker `id` 必须加图号前缀去重（`_build_html.py` 已处理）
- 英文逐字引用必附中译
- 事实性数字必须标注来源与时间；查不到出处的性能数字不采用
- **本目录的结论以实测为准**：凡 API 名、参数名、默认值，与官方文档冲突时按实测写，并把差异登记进 `_写作大纲与来源登记.md`
- **叙事优先（第八轮起）**：章节**叙述层**按 [`_写法规范.md`](_写法规范.md) 执行——问题驱动开场、一句话主线、节首接缝句、表格先框定后出现、口径标签后置、重参考块入节末、最小例子先行、图文码互证。**叙述改写轮次事实层零改动**；若发现代码 / 参数 / 图 / 正文不一致，另开「一致性修复」轮次，按规范 §4.3 允许改事实并登记证据、重跑示例与构建。改章节前先读该规范与 `ch02_models.md`（参考实现）

---
## 内容自查记录

写作与核查过程中发现并修正的问题（2026-09-24）：

| 类型 | 问题 | 处理 |
|---|---|---|
| **实测推翻文档** | 官方文档把 Deep Agents 的工具列为一项，未区分「注册」与「绑定」 | 实测发现工具节点注册 **9 个**、**绑定给模型的只有 8 个**（`execute` 因默认后端不提供执行能力而不暴露）。全书统一为「注册 9 / 模型可见 8」，并点明「注册了 ≠ 模型看得见」 |
| **同名 API 不同行为** | 初稿把「工具抛异常会被 `ToolNode` 吞成 `ToolMessage`」写成 Python 的事实 | 实测发现**两语言行为相反**：Python 异常**原样抛出**（调用失败），JS 才吞成 error `ToolMessage`（内容带 `Please fix your mistakes.`）。ch04 改为对照表，并登记为双语言差异第 15 条 |
| **同名类不同实现** | 初稿未察觉 JS 侧有两个 `InMemoryStore` | 实测确认 `langchain` 导出的那个**没有** `put` / `get` / `batch`，传进 `createAgent({store})` 会报 `this.store.batch is not a function`；必须从 `@langchain/langgraph` 导入。登记为双语言差异第 16 条 |
| **语义理解错误** | 初稿认为 `invoke(None, cfg)` 会「从检查点续跑」 | 实测：`invoke(None)` 在已跑完的线程上是**空操作**；`invoke({})` 才是续跑。示例 06 与 ch06 按实测重写 |
| **图序与出现顺序不符** | ch07 的配图出现顺序是 17→15→16 | 按出现顺序重编号（15 = store 分层、16 = 检查点恢复、17 = 时间旅行），并同步三处索引与 HTML |
| **版本号自相矛盾** | ch01 正文说 deepagents「仍在 1.x 之前」，但同页表格里 JS 包是 1.14.0 | 改为「Python 包 0.7.x / JS 包 1.x，两边版本号不同步」 |
| **行尾不一致** | 两个早期用脚本改过的 SVG 变成 CRLF，与新目录其余 75 个 LF 文件不一致 | 归一化为 LF（教训：脚本改文件必须 `open(..., newline="")`，否则静默转换行尾） |
| **构建产物会漂移** | HTML 是生成物，但初稿没有把它与章节绑定 | 新增 `_build_html.py`（幂等，两次运行 md5 一致），并在维护约定里写死「改章节必须重跑」 |

### 第二轮复核（2026-09-28，只读审计后修正）

复核方法：读正文 + 跑示例 + **读本机已装包源码** + 查官方文档，四路交叉。示例实跑 **Python 13/13、TypeScript 13/13** 全部通过（**历史记录：该轮示例总数就是 13，非现在的 17**）。查出并修正下列问题——

| 类型 | 问题 | 处理 |
|---|---|---|
| **事实错误 · 子代理并行** | ch12 写「默认 `isolated` 的子代理是串行被派发的」 | 源码 `TASK_TOOL_DESCRIPTION` 明写「Launch multiple agents **concurrently** … using a single message with multiple tool calls」，官方 subagents 页同口径。改为「**可以**并发（一轮发多个 `task`），但发几个由模型决定，不保证」 |
| **事实错误 · 并行写同键** | ch06 写「并行分支写同一个无 reducer 字段，结果甚至可能不确定」 | 实测直接抛 `InvalidUpdateError: At key 'x': Can receive only one value per step.`——不是「不确定覆盖」，是**跑起来报错**。ch06 坑与结论同步改写 |
| **事实错误 · 迁移等价性** | ch15 三步顺序第 1 步写「`AgentExecutor` → `create_agent` 这一步**行为等价**」 | 官方 v1 迁移文档明确「不是行为等价」，且 ch15 自己的映射表就列着 5 处破坏性变更（`input`→`messages`、无 `output` 字段、hook→middleware、state 必须 `TypedDict`、流式节点名 `agent`→`model`）。改为「**接口迁移，非行为等价**」 |
| **结论写反 · 要点回顾** | ch04 要点回顾写「默认 `ToolNode` 本来就会把异常吞成 error `ToolMessage`」，与本章 2.6 节（Python 原样抛出、JS 才吞）**正相反** | 按 2.6 节实测结论改写为「两语言相反」，并补源码依据（`langchain/agents/middleware/types.py`：`Exceptions propagate unless handle_tool_errors is configured`） |
| **表述过强 · 「已废弃」** | ch04 / ch15 / `code/README.md` / 来源登记统一写 `ToolException` / `handle_tool_error`「已废弃 / 已不使用」 | 实测 **API 未删除**：`langchain.tools` 仍导出 `ToolException`，`StructuredTool` 仍有 `handle_tool_error` 字段，`langchain/mcp/tools.py` 自己就在用。全书统一改为「**不再推荐**（v1 agent 路线换了入口），但 API 仍在包里」 |
| **自相矛盾 · 分层口号** | ch01 写「LangChain 不知道什么叫检查点」，但 ch02 参数表里就有 `checkpointer` | 改为「**心智模型上的分工**，不是能力边界」，并点明 `create_agent` 编译出来就是 LangGraph 图、LangGraph 也自带 `ToolNode` |
| **表述过强 · 永久丢失** | ch05 写摘要后原文「永久丢失」、「时间旅行只能回到摘要后的状态」 | 实测（摘要中间件 + `InMemorySaver`，6 轮）：最终状态 8 条，而 `get_state_history` 的 **42 个快照**里仍能翻出第 1 轮的长工具输出原文。改为「**不配 checkpointer** 时不可恢复；配了则更早的快照仍保有原文」 |
| **缺限定 · 权限默认放行** | ch11 只写「没命中任何规则 → 走默认策略」，**没写明默认是 allow** | 补上「默认 **allow（放行）**」并给源码依据（`_check_fs_permission` 收尾 `return "allow"`），点明「只声明一条 deny 得不到白名单效果」 |
| **缺限定 · delete 不吃首匹配** | ch11 写「按声明顺序首次匹配即生效」是「唯一必须背下来的纪律」 | 源码对 `delete` 单独处理：目标可能有子孙时，任何能覆盖该子树（或其祖先）的 `deny write` 都会拦下删除，**不管排多后**（`regardless of rule order`）。补为「顺序纪律只对 `read` / `write` / `edit` 成立，**`delete` 是例外**」 |
| **缺限定 · 权限与执行后端互斥** | ch11 把 `FilesystemPermission` 与 `LocalShellBackend` 放在同一节讲，未提两者不能同时用 | 实测 `FilesystemMiddleware(backend=LocalShellBackend(), _permissions=[...])` 抛 `NotImplementedError: … does not yet support permissions with backends that provide command execution`。新增第 6 条坑，并附官方警告「`root_dir` / `virtual_mode=True` 都不是 shell 的安全边界」 |
| **表述过强 · 技能白搭** | ch13 写「技能与记忆都靠文件承载，所以都必须配持久化后端」，开篇提问更写成「不配持久化后端，技能与记忆都是白搭」 | 官方 skills 页明确 `StateBackend` 下 skills **可正常工作**（把文件作为输入状态传入即可；不是 `invoke(files=...)` 关键字调用），持久化后端只解决「跨线程存活」。拆成 Skills / Memory 两条分别表述；并补「**记忆不是自动积累**——agent 得主动 `edit_file`」 |
| **自相矛盾 · 流式前置条件** | ch08 开头与结论写「暂停、恢复、流式，都建立在检查点之上」，但 3.2 节的父图流式示例**没配 checkpointer** | 改为「**HITL 建立在检查点之上**；**流式不需要**，只有 `checkpoints` / `tasks` 两档 `stream_mode` 才要求」 |
| **自相矛盾 · node-style 能力** | ch03 表里写 node-style「**不能**改写请求」，本章坑 #2 又写「要干预模型看到的输入，得用 `before_model`（改状态里的消息）」 | 表与结论改为「**不能直接改 `request` 对象**，但返回状态更新**可以改变模型看到的输入**」 |
| **口径 · 出处与「文档没写」** | ch02 参数表 `name` 行的出处写成「大纲」；「文档正文未列出」容易被读成「文档里查不到」 | 出处改为「实测示例」；`interrupt_before` 等改述为「**正文没讲**，API 参考页的签名里有」 |
| **工程 · 依赖可复现性** | `code/python/requirements.txt` 用范围（`langchain>=1.4,<2`），正文却声称锁定 1.4.2 / 1.2.12 / 0.7.18 | 改为 `==` 精确锁定（正文所有结论都绑定这三个版本），并加注释说明原因 |
| **口径不一致 · 投影数量** | 图 19 与配图索引、来源登记都写 `stream_mode`「**六**种投影」，而 ch08 正文（与官方文档）是**七**种（`values` / `updates` / `messages` / `custom` / `checkpoints` / `tasks` / `debug`），且图内表格本来就列了 7 行 | 统一为「七种」：改 SVG 标题与两处说明、README 配图表、来源登记 |
| **工程 · 失败不可诊断** | `code/typescript/run_all.ts` 用 `spawnSync("pnpm", …, { stdio: "ignore", shell: true })`，失败只打印 FAIL 不打印原因；`pnpm` 自身被环境拦下时 13 个全挂 | 改为成功静默、**失败时透传 stdout / stderr 与 spawn error** |

**首版交付时的自检结果**（2026-09-24）：

- 章节 14 个，H1 唯一且格式正确；正文无裸 HTML、无占位内容、无 LaTeX
- 配图 **26 张**全部被引用；SVG / PNG **成对**，PNG 全部为 **2×**（1360px 宽）
- 双语言示例 **13 + 13 全部实跑通过**
- HTML：无外部资源、主要标签全配对、目录锚点全部有效、内联 SVG 的 marker 引用**全部在本图内定义**

### 第三轮：扩章（2026-09-29）

以尚硅谷《LangChain 从入门到实战 2026版》讲义为底本，补齐原教程缺失的**基础层**，从 14 章扩为 18 章。

| 项 | 变更 |
|---|---|
| **新增 4 章** | ch02 模型的创建与调用、ch03 Message 与提示词模板、ch04 结构化输出、ch08 RAG 全链路（前 3 章插在 ch01 之后，RAG 插在工具章之后） |
| **原有章节顺延** | 原 ch02–ch15 → 新 ch05–ch18（两段位移 +3 / +4）；正文 94 处「第 N 章」互引按查表改写，区间引用人工重排 |
| **ch07 摘除 RAG** | 原 ch04 的 2.8 节整体移出，标题改为「工具与运行时上下文：从 `@tool` 到 MCP」 |
| **配图 26 → 32 张** | 新增 6 张（图 3 / 4 / 5 / 6 / 7 / 15）；原图 9（RAG 链路）迁入 ch08 成为图 14；其余顺延 |
| **示例 13 → 17 对** | 新增 `02_models` / `03_messages_prompts` / `04_structured_output` / `08_rag` |
| **新增依赖** | Python：`langchain-text-splitters` / `langchain-community` / `pypdf`；TS：`@langchain/textsplitters` / `@langchain/classic` / `@langchain/community` / `d3-dsv` |

**扩章后自检结果**：

- 章节 18 个，H1 唯一且格式正确；「第 N 章」引用数字全部落在 1–18
- 配图 **32 张**全部被引用、路径全部存在；SVG / PNG 成对，PNG 为 **2×**
- 双语言示例 **17 + 17 全部实跑通过**
- HTML：`_build_html.py` 连跑两次 md5 一致（幂等）；32 张内联 SVG、18 个章级锚点

**本轮实测与讲义不一致处**（新章）：`temperature` 默认值（讲义 0.7 / 实测 `None`）、`model_provider` 支持列表（24 / 28）、`ChatPromptTemplate` 的「可调用」参数类型不成立（实测报错）、TS 的 `JSONLoader` 收 JSON Pointer 而非 jq、JS 基类 `withStructuredOutput` 只支持 function calling、`langchain-community` 已进入 sunset。

### 第四轮：结构重组与可读性修复（2026-10-14）

针对「学习顺序与可读性」问题做了一轮审查与修复（审查方法：三路子代理并行通读 + 关键指控逐条原文核验 + 结构连锁面实测）。

| 项 | 变更 |
|---|---|
| **ch17 前移** | 可观测与评测只依赖第 5 章，从末章前移为 **ch10**；原 ch10–ch16 顺延为 ch11–ch17 |
| **ch18 拆分** | 拆为 **ch18 多智能体** 与新建 **ch19 迁移与部署**（全书回顾移至 ch19）；末章追加不引起其他章改号，`18_multiagent` 示例两章共用 |
| **ch07 内部重排** | 「工具怎么定义」从最后一节（§2.8）前置为 **§2.2**，往返保留开篇；章首 roadmap 从六问扩为八问 |
| **手写线换序** | S9/S10 对调：**S9 子代理、S10 MCP**（MCP 是认知负荷峰值，标注可后置）；配图 h9/h10 随章序走 |
| **图号策略** | 框架线图号**绑定内容**、不随章序重排（图 31 先于图 18–30 出现为既定例外）；新增图仍按出现顺序递增 |
| **重编号残留清理** | 四章章首「前 N 章」计数（14→18 扩版残留）；ch06 表「第 10 / 12 章」→「第 15 / 17 章」；示例代码文件名引用与 Python 文件头「运行」名（扩章前旧名）；`_写作大纲与来源登记.md` 逐章大纲的配图编号；TS 文件头「pnpm run 0X_xxx」旧名 |
| **引用勘误** | 35 处「差异清单第 N 条」全部去编号、改述为内容（该清单实为两份：`code/README.md` 双语言差异 **18** 条、`_写作大纲` 文档 vs 实测 16 条，正文混引是错位根源）；ch11/ch12 的 `invoke(None)` 口径按「注入空输入 vs 不注入输入」三场景统一；手写线 5 处交叉引用指错章 |
| **跳读路径勘误** | 手写线捷径「S1→S4→S6→S7」改为「S1→S3→S4→S5→S6→S7」（S6/S7 代码直接依赖被跳过的 S3 与 S5） |
| **元信息清理** | 约 20 处「讲义 / 尚硅谷 / 内容底本」从学习者正文中移除（保留事实与「未实测」标签）；此类信息只留在 `_写作大纲与来源登记.md` 与本章自查记录 |
| **接缝补强** | ch05 补 `add_messages` / `checkpointer` 两句地基科普；ch11 加「AgentState = 最小图状态」回收句、super-step 释义、§2.8 checkpointer 前置说明；ch14 加「先看它干活」teaser 与 §2.1 导读；ch17 补「记忆」撞名区分；术语表补 `Command` / 超步 / map-reduce |
| **实测推翻旧口径** | TS 假模型探针证实：`responseFormat` 传裸 schema 默认走**工具策略**（源码 `ToolStrategy.fromSchema`，工具名取 schema 的 title），**脚本化假模型可以跑通**——「JS 默认走 provider 原生 JSON schema、假模型跑不通」是误读（只对 provider 子类成立）；ch05 / ch01 / code/README 三处口径按实测统一，TS 05 示例第 ④ 节从「未实测」升级为实测演示 |
| **依赖与归属** | RAG 统一为「按需原料章」（不占基础层）；ch01 安装节与 ch08 开头补 RAG 依赖安装指引 |
| **双语言命名勘误** | ch09 消息裁剪器：Python 是 `trim_messages`（函数）、JS 是 `trimMessages`（类）——原表把 JS 名当通用名；`create_agent` 实测签名 15 项（含 `debug`），ch05 参数表补全 |
| **结论/回顾分工去重** | 规则写入「维护约定」：结论只留可迁移判断（3–5 条）、回顾只做可勾选清单、同一事实只出现一次；本轮完成 ch02 / ch05 / ch10 / ch14 / ch17 五章 |
| **P2 打磨** | ch15 坑编号重复（两个 6.）；ch16 要点回顾 bullet 拆行；ch11 / ch12 代码片段补 `node_b` / `TypedDict` 导入；手写线 s09 自测题计数（三→四）；S1–S3 元信息头 `.svg`→`.png` |

**本轮自检结果**：

- 章节 19 个，H1 唯一且格式正确；「第 N 章」引用经占位符两轮替换 + 全量 grep 复核
- 配图 32 张全部被引用、路径全部存在；SVG / PNG 成对，PNG 为 **2×**；手写线 h1–h11 成对
- 两个 HTML 精读版均**连跑两次字节一致**（幂等）；框架线 19 个章级锚点、手写线 11 个
- 仓库统计经 Python 重算后同步（919 文件 / 579 篇 / 约 27.4 万行）
- 双语言示例：`05_create_agent.ts` 因口径修正重跑通过（结构化输出实测演示）；其余示例本轮未改逻辑，沿用第三轮实跑结论
- 章节正文中「讲义 / 尚硅谷 / 差异清单第 N 条」残留为 **0**

### 第五轮：ch02 接缝修复（2026-10-15）

用户反馈 ch02 的 2.2（`init_chat_model`）与 2.3（`invoke`）之间无衔接，看不出二者为何同属一章。修复如下——

| 项 | 变更 |
|---|---|
| **ch02 接缝补强** | 章首补「2.1–2.6 六节围同一个对象转」的章节地图（对齐 ch07 问题枚举 + 小节号范式），点明 `init_chat_model` 与 `invoke` 是同一对象的两端（前者造出来，后者是核心方法）；2.2 开头补「角度 2 展开 + `init_chat_model()` 返回模型对象」承接；2.3 开头补「不管哪个角度拿到的都是同一个模型对象，`invoke` 是它的核心方法」；2.5→2.6 补「自带 vs 临时传」过渡句 |

**本轮自检结果**：

- `_build_html.py` 连跑两次字节一致（幂等）；纯文字修改，无新增图、无新增事实，图号与配图索引不变
- 「五、关键结论」与「本章要点回顾」未动（衔接句是导航性陈述，遵守「同一事实只出现一次」）
- 「讲义 / 尚硅谷 / 差异清单第 N 条」残留为 **0**

### 第六轮：全量审查与讲解质量修复（2026-10-16）

两轮审查（结构核验 + 5 路子代理全文通读 + 讲解质量评审，全部指控逐条原文复核）后的集中修复，分五批：

| 批 | 变更 |
|---|---|
| **A · 事实错误** | ch05「第一轮后历史 1 条」→ **2 条**（与本章实测输出对齐）；手写线 S11「S9 的 MCP」→ **S10**（对调残留） |
| **B · 引用指错** | ch01「三处可选依赖」→ **两处**；ch02 `recursion_limit` 去掉落空的「第 11 章」引用；ch06 `HumanInTheLoopMiddleware` 详见列改为「第 13 章（LangGraph `interrupt` 路线；该中间件本书不展开）」；ch06 两处「双语言清单第 5/7 条」去编号（对齐第四轮声明）；README 已知限制「ch14 的 trace」→ **ch10**（前移残留）；ch12 `delete`「示例中未单独调用」与示例矛盾 → 改为如实描述；ch14「第 5–9 章……子代理要自己搭」→「第 5–13 章……多智能体协作到第 18 章才自己搭」；ch19 三步顺序补第 5 处破坏性变更（流式节点名 `agent`→`model`）并在映射表补对应行；手写线 S11「第 10 与 15 章」→ 第 **11 与 16** 章、S1 流式分片「在 S4 展开」→ **S6**、S9「下一章的五维」→ **S11**、S10 图注 h9 → **h10** |
| **C · 例子补强（改码并双语言实跑）** | ch08 新增 ③-0 手写二维玩具（猫/狗/汽车坐标，「语义相近=距离近」从口号变几何直觉）；ch12 新增快照序号示意 + ③-bis 三节点链（`bump→double→tag`，fork 后重走两步，「时间旅行」真正可演示）+ §2.4 补 git branch 同构类比；ch16 ③ 节升级为防火墙实证（子代理 2 轮含 3000 字工具资料，主代理只收 30 字符最终报告）；ch18 supervisor 加 db/mail→supervisor **回边**（「交出去还能收回来」有实证：决策序列 `['db','end']`） |
| **D · 类比台阶** | ch11 超步升格为 2.5 节完整段（游戏回合并列类比）；ch13 补「检查点只落在超步边界」的 interrupt 重跑机制解释（四条铁律从背规矩变推导）；ch06 补洋葱模型解释（快递包装类比）+ node-style 绕层 3 行最小示意 |
| **E · 单点小修** | ch02 `finish_reason` 补 `tool_calls` 取值（ch05 循环判据伏笔）；ch03 补三种错误的具体形态；ch09 `checkpointer` 首现补一句定位（第 12 章系统讲）；ch01 双 SDK 表前补「初读只需看命名规律」；ch04 TS 子类代码移出正文（登记为差异清单第 17 条）；ch10 token 表补第 9 章实测数字引用；ch17 TS 循环标注「引用回显，非机制验证」；ch14 `HarnessProfile` 声明式优势补两行对照（标注为写法示意） |

**本轮自检结果**：

- 双语言示例 **17 + 17 全部实跑通过**（本轮环境：Python 3.14.2 + 锁定版本 langchain 1.4.2 / langgraph 1.2.12 / deepagents 0.7.18；`langchain-core` 装到 1.6.11 为传递依赖，正文结论绑定的三个主包与第三轮实测一致；08 侧补装 `jq`——`requirements.txt` 未列，已顺手补上）
- 两个 HTML 精读版连跑两次 **md5 一致**（幂等）；无新增图，图号与配图索引不变
- 「差异清单第 N 条」正文残留为 **0**；手写线 S9/S10 对调残留清零
- C 批四处新输出均为**实跑转录**，非编造；正文代码片段与实跑代码一致（`get("trail", [])` 形式）
- **复核后追加修正**（子代理新鲜眼光复核发现）：ch19 流式节点名 TS 列「同左」→ `model_request`（与差异清单第 12 条对齐）；ch12 的 `delete` 改为**给代码补真实调用并实跑**（正文代码块原有该行但 `12_persistence.py`/`.ts` 实际未调用——原矛盾的本质是「文档代码 ≠ 实跑代码」，两语言补 `store.delete` 后输出 `['pref-food']`）；ch08 悬空引用「2.8 节」→「四、常见坑第 3 条」；ch09「第 5 章 2.3 节」→ 2.2 节参数表；ch16「3000 字」标注为示例设定值；`18_multiagent` 两处「见第 8 章示例」存量错引 → **第 13 章**（subgraphs 演示实际在 13_hitl_stream）

### 第七轮：ch02 §2.2 参数口径修复（2026-10-19）

用户对照 HTML 截图复核 ch02 §2.2 的 `init_chat_model` 签名与下文。签名逐字准确（`inspect.signature` 核对），但**下文有事实错误**。对本机 `langchain` 1.4.2 / `langchain-openai` 1.7.2 / `langchain-anthropic` 1.7.6 做**构造层核对**（只构造、不发请求、不需要 Key）后修复——

| 项 | 变更 |
|---|---|
| **「四个自己的参数」指代错位** | 原文「它自己的参数只有四个，`temperature` / `api_key` / `base_url` / `max_tokens` 全走 `**kwargs`」——逗号后那四个恰恰**不是**它自己的，读起来正好反了。改为点名签名里的 `model` / `model_provider` / `configurable_fields` / `config_prefix`，转发项另起一句 |
| **参数表缺两行** | 该表声明要回答「哪些是它自己的参数、哪些只是转发」，却只列了 4 个自有参数中的 2 个。补 `configurable_fields`（含「显式传 `model` 时默认 `None`，不传时默认 `("model", "model_provider")`」）与 `config_prefix`，并加**本机核对**列区分「示例实测 / 字段核对 / 示例未传」 |
| **核心口径反了** | 原文「写错了报错的是底层类」——实测**不报错**：给 `ChatOpenAI` 传 `api_base`、或把 `temperature` 拼成 `temperture`，构造照样成功，值静默进 `model_kwargs`、`openai_api_base` 仍是 `None`、请求照旧打到 `api.openai.com`，只有一条 `UserWarning`（基类 pydantic `extra='ignore'`）。坑 2 整条改写为「静默失效」并给出 `print(m.openai_api_base, m.temperature, m.model_kwargs)` 的排查法；§2.2「钥匙」句、关键结论 2、要点回顾同步 |
| **「参数名不归 LangChain 管」过度概括** | `api_key` / `base_url` 在 OpenAI 与 Anthropic 集成里都是 pydantic **别名**（本名 `openai_api_base` / `anthropic_api_url`；`max_tokens` 的别名是 `max_completion_tokens`），已明显收敛。改为「名字可能不同」与「写错不报错」两件事分开记；DeepSeek 的 `api_base` 保留但标注为官方 reference 核对、**未实测**（原文当既成事实陈述，与坑 2 自己的标注矛盾） |
| **坑 3 的通则不成立** | 「不传 `api_key` 会在构造时报错」只对 OpenAI 系成立（补 Python 侧证据，与 JS 是同一条 `OpenAIError`）；实测 `init_chat_model("anthropic:…")` 在无 key、无 `ANTHROPIC_API_KEY` 时**构造成功**，报错推迟到调用 → 改为「取决于集成」，并点明「构造通过 ≠ 凭据没问题」 |
| **正文代码片段 ≠ 实跑代码** | Python 片段 ① 里变量名 `direct` 绑的却是 `init_chat_model`（实跑代码中 `direct` 是 `ChatOpenAI`、`unified` 才是统一入口）→ 改名 `unified` 并与 TS 片段对齐；① 节头写「三个初始化角度」但只留了角度 2 → 标注「只留角度 2 的主干」；④ 节头写「四种调用形态」却少 `ainvoke`（实测输出块原有 `ainvoke → '异步返回。'`）→ 补一行并补 `import asyncio` |
| **要点回顾「四个坑」** | 第四节实有 8 条，原文只列 4 条却写「四个坑」→ 改为「坑共 8 条，最常踩的是这四条」 |
| **核验产物与登记** | 新增 `_实测输出核验/ch02_kwargs_构造层核对.py` / `.txt`（签名 / 静默失效 / 凭据时机 / 字段别名四组核对，`exit=0`、无 Key），并在该目录 README 登记；`_写作大纲与来源登记.md` 差异清单新增 **#23 #24**，ch02 大纲行同步 |

**本轮自检结果**：

- 新增核对脚本 `exit=0`，`.txt` 为 stdout 原样转录；正文本轮新增的每条「实测」都能在其中找到对应行
- **未改动** `code/python/02_models.py` 与 `code/typescript/02_models.ts`（本轮只把正文片段对齐到实跑代码，示例逻辑与实测输出块不变）
- `_build_html.py` 重跑通过、连跑两次字节一致（幂等）；无新增图，图号与配图索引不变
- ch02 全文行内粗体与反引号标记逐行配平校验通过；代码围栏成对
- 「差异清单第 N 条」在章节正文残留仍为 **0**（编号只出现在元文件）

### 第八轮：叙事优先改写（2026-10-19）

用户反馈：框架线写法与 `docs/harness/`、`docs/大模型与神经网络原理笔记/` 两篇范本比「不连贯、不易理解」。诊断结论——**事实层与实测纪律强于范本，叙述层是「参考手册式」**（节内表 + 坑 + 结论堆叠，缺问题导入与推导链）。本轮只改叙述层，事实层零改动。

| 项 | 变更 |
|---|---|
| **规范落地** | 新增内部元文件 `_写法规范.md`：范本五特征（问题驱动开场 / 一句话主线 / 推导链 / 类比台阶 / 从机制答为什么）+ 可做 / 不可做清单 + 每章自检清单 |
| **参考实现** | ch02 全文按规范重写：§2.2 症状导入（「设了 `temperature=0` 输出还飘」）+ 总机类比 + 28 个 provider 名单入节末参考块；2.3–2.6 补接缝句；坑节补导读 |
| **框架线全覆盖** | ch01、ch03–ch19 共 18 章分 6 批改写（子代理执行、逐章回读核对）：每章补一句话主线与节首接缝句、表格框定句补齐、7 处重参考块后置（内容一字不删）、49 处类比（均标注类比身份）、口径标签仅移位不删除 |
| **手写线** | 抽查 S1 / S6 已达问题驱动标准（症状导入 + 规模对照表），**不改动** |
| **纪律修复** | ch19 迁移表「见差异清单第 12 条」改为内容直引 + 指向 `code/README.md`（第四轮「正文只引内容不引编号」纪律的漏网残留） |
| **构建与核验** | `_build_html.py` 重跑；自写核验脚本全量通过 |

**本轮自检结果**：

- 叙述层统计：**一句话主线 12 处**、「下表回答的问题是」**38 处**、参考块 **7 处**、类比标注 **49 处**
- 各批子代理逐章回读确认：事实 / 数字 / 口径标签 / 图号 / 代码块 / 跨章与节号引用**零改动**（口径标签仅移位或加指向句，未删除未升级）
- `_build_html.py` 连跑两次 **md5 一致**（幂等）；无新增图，图号与配图索引不变
- 核验脚本：19 章 H1 唯一、代码围栏成对、**32 张配图引用全部存在**、跨章引用均在 1–19、图号均在 1–32、旧版错误文案与「讲义 / 尚硅谷 / 差异清单第 N 条」残留为 **0**
- **遗留备查**（2026-10-20 第九轮已修）：ch06 节号 3.1–3.4 → 2.1–2.4；ch08 节标题「四种切法」→「五种 Loader」；ch04 章首「结论见 2.4 节末」→ 2.3 节请求体表

### 第九轮：全量复审与事实修复（2026-10-20）

针对「内容是否易学且准确」做的一次全量复审：19 + 11 章逐章通读、17 + 17 框架示例与 S1–S10 全量实跑、安装包签名与源码抽查。修复分四类：

| 类别 | 修复（详见 `_实测输出核验/README.md` §6） |
|---|---|
| **API 误用** | ch14 `profile=` 改「按 provider 注册并补可运行演示」；ch15 后端导入与 `LangSmithSandbox` 路径纠正；ch19 三步顺序重排；ch11 JS 取 `.graph` 结论纠正 |
| **事实错误** | 手写 S9 剧本补齐 `api.md`（sub-dto 实测 3 轮 / 7 条）；S5 Schema 坑、S7 cwd 坑、S11 registry 与提示词映射纠正；S10 修复中文 Windows 编码问题 |
| **口径矛盾** | ch04 实测/未实测统一；ch05 默认策略改 `AutoStrategy`；ch13 `tasks` 前置条件；ch02 真实输出与 `initChatModel`；ch08–ch12 的切分器、假嵌入、`trimMessages`、run 数、Store 语义 |
| **过期声明** | 版本表同步、删除「本机无 API Key」、主 README 增 TypeScript typecheck 未通过说明；TS 文件头与示例章节引用修正 |

**本轮自检结果**：框架线 **17 + 17 全绿**、手写线 **10/10 全绿**（含中文 Windows 默认编码）；`_实测输出核验/` 全部更新；两份 HTML 精读版重跑且**连续两次 md5 一致**；章节节号、图号与跨章引用复核通过。

### 第十轮：规范补强与 ch02 图文码一致性修复（2026-10-21）

针对 2026-10-21 回溯的原问题（参考两篇范本、ch02 代码参数与下文、图片与下文语义、简单例子），本轮先补规范，再修 ch02 与同类重复：

| 项 | 变更 |
|---|---|
| **规范补强** | `_写法规范.md` 重写：用户反馈与核查诊断分栏；范本特征 5 → 7（新增最小例子、图文互证）；新增「叙述改写 / 一致性修复」两轨与裁决顺序；补口径子标注与别名映射、图 31 / ch01 §3 / ch19 全书回顾、结论数量存量例外（逐批收敛，批次 5 后全部章节 3–5 条，且每章至少 1 个最小例子）；新增图文码互证、最小例子、构建与登记要求；自检清单从 6 条扩到 14 条 |
| **ch02 参数表** | 「本机核对」列名改为「口径 / 依据」（列内同时有示例实测、源码核对、未实测，原列名与内容不同义） |
| **ch02 图 3** | 去掉「唯一会变的量」的单变量说法，改为「谁选类 + 模型在哪」；`ChatOllama` 只归角度 3；正文同步说明它为何不放进角度 1 |
| **ch02 图 4** | 输出框从固定的 `[SystemMessage, HumanMessage]` 改为「消息序列（条数随输入）」，并注明「字符串 1 条；列表 2 条」；正文与代码输出字符串同步纠正「三种写法完全一样」的说法 |
| **ch02 最小例子** | §2.2 签名后补 4 行 Python 最小例子（只构造、不发请求），演示新规范的最小例子要求 |
| **结论/回顾去重** | ch02、ch05、ch10 的关键结论删除与要点回顾重复的纯事实清单，只保留判断；事实清单留在回顾 |
| **构建与核验** | 02 示例 Python / TS 重跑 `exit=0`；`_实测输出核验/` 两份输出同步；两张 SVG 重渲染为 2× PNG（1360×920 / 1360×840）；`_build_html.py` 连跑两次 md5 一致（`b0df3d87…`） |

详细验证记录见 [`_实测输出核验/README.md`](_实测输出核验/README.md) §7。

**本轮自检结果**：

- 正文 / 图源 / 示例代码 / HTML 中 grep 旧错误文案 `三种写法归一化成同一件事` / `三种写法在模型这一侧看起来完全一样` / `唯一会变的量` / `三个类各管一家` 残留 **0**（本变更记录与核验报告中的历史引用不计）
- ch02 参数表头与列内容一致；图 3 / 图 4 的 PNG 与正文逐项对照通过
- 02 示例双语言重跑通过；输出归档已更新
- HTML 连跑两次 md5 一致；图 3 / 图 4 的内联 SVG 已随章节更新

**分批推进（2026-10-21）**：

| 批次 | 章节 | 变更 |
|---|---|---|
| 1 | ch01–ch04（ch02 已在第十轮开头完成） | ch01：补无 Key 版本验证最小例子；结论 6→5。ch03：补 `ChatPromptTemplate` 最小例子；结论 8→5，补口径注。ch04：补 Pydantic 最小例子；结论 8→5，补口径注。图 5 红字改两行，修复右侧裁切。 |
| 2 | ch05–ch08 | ch05：补 `create_agent` 最小例子；参数表补「维度」表头；补口径注。ch06：补 `before_model` 最小例子；参数表补「维度」表头；结论 6→5，六大能力域与图 11 对齐。ch07：补 `@tool` 最小例子；结论 7→5。ch08：补 `Document`+Splitter 最小例子；结论 6→5。图 8 改「四步判据」、图 11 重绘六大域、图 12 标注 Python 名、图 14 注明从切分开始。 |
| 3 | ch09–ch12 | ch09：补 `trim_messages` 最小例子；结论 7→5；图 16 修正 token 上升趋势、图 17 补第三条推论。ch10：补回调最小例子；补口径注；图 31 标注 Python 侧。ch11：补 `StateGraph` 最小例子；结论 7→5；图 18 改「三个构件 + 一次编译」、图 19 补 `None/null`、图 23 改 `update_state`。ch12：补三步检查点最小例子；表头补「维度」；结论 6→5。 |
| 4 | ch13–ch16 | ch13：修 `tasks` 不需要 checkpointer 的图文/正文冲突；补三步中断示例；结论 6→5。ch14：补 `create_deep_agent` 最小例子；补口径注。ch15：补三步 `StateBackend` 示例；结论 7→5；图 27 标注常用四种。ch16：补三步规划 + 委派示例；表头补「观测点」；结论 7→5。 |
| 5 | ch17–ch19 | ch17：补技能 / 记忆三步最小例子；表头补「维度」；补口径注。ch18：补 supervisor 三步最小例子；补口径注。ch19：补迁移三步最小例子；表头补「维度」；补口径注。 |

**全量收尾（批次 5 后）**：19 章全部满足关键结论 3–5 条、每章至少 1 个最小例子、无空表头；32 张 PNG 均为 SVG viewBox 的 2×；章节引用均在 1–19。

### 第十一轮：ch02 §2.2 可配置参数口径修复（2026-10-21）

用户复核指出：§2.2 把 `configurable_fields` / `config_prefix` 合并表述为「管运行时能不能改」，语义不完整；参数表里这两行的作用也指向不清。对照本机源码（Python `langchain` 1.4.2 的 `init_chat_model` / `_ConfigurableModel`；JS `langchain` 1.5.11 的 `chat_models/universal`）修复——

| 项 | 变更 |
|---|---|
| **合并表述拆开** | 「管运行时能不能改」→「管运行时改哪几个字段、用哪个键名改——前者是白名单，后者是键名前缀」，并补「传了 `model` 又不声明白名单 = 固定模型：运行时写什么都不生效，也不报错」 |
| **`configurable_fields` 行补全** | 原文只有「声明哪些参数能覆盖」+ 默认值。补三种取值（`None` / `"any"` / 字段列表）、`"any"` 连 `api_key` / `base_url` 一起放开的安全提示、名单外的键**静默丢弃**；默认值补原因「模型名本身得靠运行时给」 |
| **`config_prefix` 行重写** | 「给上面那些运行时键加前缀」指代不清。改为给键形（`a` → `a_model`；不传 → `model`）、`"a"` 与 `"a_"` 等价（内部补下划线），并明说它**不决定能不能改**：在传了 `model`、没传 `configurable_fields` 时单传它，只有一条 `UserWarning` + 一个固定模型；连 `model` 也没传则前缀照常生效 |
| **补返回类型副作用** | 新增一段：`configurable_fields` 非 `None` 时返回值从 `ChatXxx` 变 `_ConfigurableModel`，底层类延迟到每次调用才组装，`isinstance` 从声明起就失效（与 2.6 `with_config()` 坑同源）；并补两语言默认值不对称（JS 总是包装对象、默认放开 `model` / `modelProvider`；Python 传了 `model` 就全关） |
| **补键形示意** | 新增 `text` 块对比「有前缀 / 无前缀」两种键形，点明 `configurable_fields` 里写的是**裸字段名**（`"model"`，不是 `"a_model"`） |
| **连带同步** | 2.2 开头、2.3 开头的「Python 返回 `ChatXxx` 实例」各补「声明 `configurable_fields` 即包装对象」；2.6 `configurable` 行改为「只对声明过的字段生效，名单外静默忽略」；坑 8 的 2.2 依据由 `源码核对（docstring）` 细化为 `源码核对（docstring / _ConfigurableModel 实现）`（**口径等级不变**）；要点回顾同步白名单 / 键名前缀 |

**本轮自检结果**：

- 口径未升级：新增事实全部来自本机已装包源码，「运行时真发请求的覆盖」仍标未实测；未新增任何「实测」结论
- 示例代码与实测输出块未动；无新增图，图号与配图索引不变
- `_build_html.py` 连跑两次 md5 一致（`e31a87c3…`）
- 「讲义 / 尚硅谷 / 差异清单第 N 条」正文残留仍为 0

### 第十二轮：参数表述二轮精修（2026-10-21）

用户复核确认第十一轮方向正确，但指出条件仍有省略、表格语义仍不完整，并要求排查其它章节。本轮按同一口径修复——

| 项 | 变更 |
|---|---|
| **ch02 条件补全** | `configurable_fields` / `config_prefix` / 要点回顾统一补「传了 `model`」前提；`config_prefix` 补「连 `model` 也没传时，默认白名单生效、前缀照常生效」分支；键形示例补 `configurable_fields=["model", "temperature"]` 的初始化代码；正文「命名空间」统一为「键名前缀」 |
| **ch02 §2.6 纠偏** | `config` 由「记账方式、不改模型行为」改为「这一次调用的配置单」；关键结论 5 补 `max_concurrency` / `recursion_limit` / `configurable` 会改变执行，修正与同节表格的矛盾；前四项的可见范围由「只在追踪系统」改为「只在回调与追踪系统」 |
| **ch10 作用域** | 「不配 LangSmith 时无效果」改为「没有挂任何回调 / tracer 时无效果」，并说明自定义回调仍可读到（第 2 章 `TagProbe` 为证） |
| **ch16 SubAgent 表** | `tools` / `model` / `interrupt_on` / `permissions` 补省略时的继承语义，`middleware` 补「默认栈之后追加」，`skills` 补 `fork` 继承 |
| **ch05 JS 标注** | `interrupt_before` / `interrupt_after` / `debug` / `cache` / `transformers` 标为仅 Python；注明 JS `CreateAgentParams` 无这些字段、`streamTransformers` 不是同名替代 |
| **手写线 ch_s01** | `finish_reason` 补 `length` 等常见值、改为「本章只演示 `stop` / `tool_calls`」并指向坑 1；删掉错误的「2.4 节」引用 |
| **ch15** | `FilesystemMiddleware.tools` 默认值「全量」改为「全部内置文件工具」 |

**依据**：Python `langchain` 1.4.2 的 `init_chat_model` / `_ConfigurableModel` 源码，并用 `init_chat_model(config_prefix="a")` 与 `_model_params` 运行核对（前者返回 `_ConfigurableModel`、无 warning；后者确认白名单外的 `a_max_tokens` 被丢弃）；JS `langchain` 1.5.11 的 `chat_models/universal` 与 `agents/types.d.ts` 源码；`deepagents` 0.7.18 的 `SubAgent` docstring 与 `graph.py` 中 `raw_subagent_tools` / `model` / `permissions` 的默认逻辑。运行时覆盖仍未实测，口径不升级。

**本轮自检结果**：

- ch02 / ch10 / ch16 / ch05 / ch15 / 手写线 ch_s01 的旧表述 grep 残留 0（变更记录中的历史引用不计）
- 示例代码与实测输出块未动；无新增图，图号与配图索引不变
- `_build_html.py` 框架线连跑两次 md5 一致（`1ebe40ab…`），手写线连跑两次 md5 一致（`41a17627…`）


### 第十三轮：2026-10 增补轮（atguigu-note-main）

以 `atguigu-note-main` 课程包为**选题清单**（无 LICENSE；仅参考概念与 API 名称，未复制原文/图片/代码），就地扩写 6 章、新增 6 图，并补齐 guides。课程包锁定 `langchain 1.2.12 / langgraph 1.1.2`，低于本书基线；所有 API 以本机 `1.4.2 / 1.2.12` 实测为准。

| 项 | 变更 |
|---|---|
| **ch06** | 新增 §2.5–2.8：HITL、PII、限额、重试/回退；图 12 |
| **ch07** | 新增 §2.9–2.10：MCP 服务端（FastMCP + stdio）与接入边界；图 15；`07_mcp_server.py` |
| **ch11** | 新增 §2.9–2.13：`add_sequence`、静态扇入、循环/`recursion_limit`、`RetryPolicy`/async timeout/`CachePolicy`、Functional API；图 24 |
| **ch12** | 扩展 §2.3 durability；新增 §2.6–2.7 子图持久化与记忆类型学；图 28 |
| **ch13** | §2.4 改为七档全跑；新增 §2.6–2.8 list+subgraphs、`astream_events`、解析契约；图 31 |
| **ch19** | 新增 §2.5–2.7 `langgraph.json` / `langgraph dev` / 治理对接；图 38；`19_deploy_agent.py` + `langgraph.json`（Python-only） |
| **图号** | 32 → **38**；存量 8–32 全量重排（取消「图 31 例外」），图号严格按出现顺序连续 |
| **示例** | Python 主示例 17 个 + 部署 1 个 + MCP fixture 1 个；TS 17 个；`06/07/11/12/13` 双语言同步扩写 |
| **guides** | `python-core` 新增 4 篇 + 4 导览；`langchain-rag` 新增 LangGraph 面试篇 + 导览 |
| **来源** | `_写作大纲与来源登记.md` 新增 T1–T6（仅选题参考）与差异 #26–#36 |

**本轮实测与自检**：

- Python 主示例 **17/17 + 19 部署样例 exit=0**；TypeScript **17/17 通过**；`pnpm run typecheck` 仍 `exit=1`，错误数 **44 → 73**（新增集中在 11/12/13 的泛型与中间件工厂类型，运行时不受影响）。
- MCP 本地 stdio：Python `MCPAdapter(Path(...))` + TS `MultiServerMCPClient` 均发现 `add` / `echo` 并调用成功；Python 裸名、TS `demo__add` 前缀。
- 部署：`langgraph validate -c langgraph.json` 通过（1 graph）；`langgraph dev --config ...` 启动后 `/ok` 200；Studio / AgentChatUI / Docker / 云端未实测。
- 图：38 对 SVG/PNG；PNG 均 2×；章节 / README / 大纲三处图号审计无缺号、无重号、无悬空引用。
- HTML：`_build_html.py` 连跑两次 md5 一致（`ec630dde…`），38 个 `<figure>`，无外部资源。
- `atguigu-note-main/` 已加入 `.gitignore`；其 `.env` 移出仓库，notebook 内联密钥替换为占位符；未复制课程包图片与原文。
