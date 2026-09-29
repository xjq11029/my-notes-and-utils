# Agent 开发教程 · LangChain / LangGraph / Deep Agents

一套自成体系的 **Agent 应用开发教程**：从「构建块 → 运行时 → 成品 harness」三层递进，讲清当下最主流的三个 Python / TypeScript Agent 框架，配 **Python 与 TypeScript 双语言实测示例**与自绘机制图。

> **与 [`docs/harness/`](../harness/README.md) 的分工**：那篇回答「**为什么需要 harness**」（Agent = Model + Harness、五个必然问题、12 个组件），是原理篇；本篇回答「**用现成框架怎么搭**」，是工程篇。两篇可独立阅读，也可连着读。

---

## 交付物

| 文件 | 类型 | 说明 |
|---|---|---|
| `ch01`–`ch18*.md` | 教程正文 | 18 章，每章统一骨架：这一章要解决的问题 → 机制与原理 → 双语言代码 → 常见坑 → 关键结论 → 本章要点回顾 |
| `agent-frameworks-deep-dive.html` | 精读版长文 | 单文件自包含（无 CDN / 无外部字体 / 无外部 JS），深色主题，左侧目录滚动高亮，32 张内联 SVG，Python/TypeScript 代码切换。**由脚本生成，不手工改** |
| `_build_html.py` | 元文件 · 构建脚本 | 从 18 章正文 + `assets/` 生成上面那份 HTML。**幂等**；改章节或配图后必须重跑 |
| `code/python/` | 示例代码 | Python 示例，**全部实跑通过**；离线 Fake 模型，无需 API Key |
| `code/typescript/` | 示例代码 | TypeScript 示例，与 Python 一一对应，**全部实跑通过** |
| `assets/` | 配图 | 自绘 SVG 矢量源 + **2× PNG 导出**（Markdown 引用 PNG；SVG 与 HTML 精读版同一份源） |
| `_写作大纲与来源登记.md` | 元文件 | 逐章大纲 + 官方文档 URL + 版本 + **官方文档与本机实测的差异清单**（内部用） |

---

## 全书结构（基础层 + 三件套）

| 层 | 内容 | 定位 | 一句话 |
|---|---|---|---|
| **基础层** | 模型 / 消息 / 提示词 / 结构化输出 / RAG | 不碰循环，先把「原料」备齐 | 模型怎么造、话怎么说、结果怎么收、知识从哪来 |
| **构建块** | LangChain v1 | 一个**高度可配置的 harness** | `create_agent` 给你循环 + 中间件插槽，自己组装 |
| **运行时** | LangGraph v1 | **图 + 状态 + 持久化**的底层基础设施 | 管状态、管检查点、管中断、管恢复 |
| **成品 harness** | Deep Agents | 在 `create_agent` 之上**预装**一整套能力 | 规划、虚拟文件系统、子代理、记忆开箱即用 |

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
| 6 | [ch06_middleware.md](ch06_middleware.md) | 中间件：harness 的可插拔扩展点与钩子体系 |
| 7 | [ch07_tools_and_context.md](ch07_tools_and_context.md) | 工具与运行时上下文：`@tool`、注入与 MCP 接入 |
| 8 | [ch08_rag.md](ch08_rag.md) | RAG 全链路：加载、切分、嵌入、入库与检索 |
| 9 | [ch09_context_engineering.md](ch09_context_engineering.md) | 上下文工程：摘要、裁剪、卸载与缓存前缀 |
| 10 | [ch10_langgraph_state.md](ch10_langgraph_state.md) | LangGraph 图与状态：State / Reducer / Node / Edge / Send |
| 11 | [ch11_langgraph_persistence.md](ch11_langgraph_persistence.md) | 持久化与持久执行：检查点、线程、时间旅行、长期记忆 |
| 12 | [ch12_langgraph_control.md](ch12_langgraph_control.md) | 人在回路与流式：interrupt / resume / stream_mode |
| 13 | [ch13_deepagents_overview.md](ch13_deepagents_overview.md) | Deep Agents 全景：预装 harness 与 HarnessProfile |
| 14 | [ch14_deepagents_filesystem.md](ch14_deepagents_filesystem.md) | 虚拟文件系统与执行环境：文件工具、权限、后端 |
| 15 | [ch15_deepagents_delegation.md](ch15_deepagents_delegation.md) | 规划与委派：`write_todos` 与子代理 |
| 16 | [ch16_deepagents_context.md](ch16_deepagents_context.md) | 技能与记忆：Skills 渐进式披露与跨会话 Memory |
| 17 | [ch17_observability.md](ch17_observability.md) | 可观测与评测：追踪、数据集与成本 |
| 18 | [ch18_multiagent_and_migration.md](ch18_multiagent_and_migration.md) | 多智能体协作、从旧版迁移与生产部署 |

**推荐学习顺序**：按章顺序通读（1→18 为叙事线）；只关心某一层可跳读——第 2–4 章是基础层（模型、消息、结构化输出），第 5–9 章是 LangChain（含第 8 章 RAG 全链路），第 10–12 章是 LangGraph，第 13–16 章是 Deep Agents，第 17–18 章是公共工程话题。

---

## 术语表（按首见章节排序）

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
| `StateGraph` | LangGraph 的图构建器 | ch10 |
| Reducer | 决定「节点返回的更新如何合并进当前状态」的函数 | ch10 |
| `add_messages` | 内置 reducer：追加消息并按 ID 去重更新 | ch10 |
| `Send` | 从条件边动态派发并行的 map-reduce 原语 | ch10 |
| Checkpointer | 把图状态按检查点落盘的组件 | ch11 |
| Checkpoint | 一次状态快照；同线程可回放与时间旅行 | ch11 |
| Store | 跨线程长期记忆的键值存储 | ch11 |
| Durable execution | 持久执行：崩溃或中断后从最近检查点续跑 | ch11 |
| `interrupt()` | 在图内暂停并等待人工输入的机制 | ch12 |
| `stream_mode` | 流式输出的投影方式（values / updates / messages / custom …） | ch12 |
| `create_deep_agent` | Deep Agents 的入口函数，预装一整套中间件 | ch13 |
| HarnessProfile | 声明式地裁剪 Deep Agents 内置能力 | ch13 |
| Virtual filesystem | 挂载在后端上的文件工具集（`ls`/`read_file`/`write_file`…） | ch14 |
| Backend | 文件与执行的落点（State / Store / Filesystem / Sandbox） | ch14 |
| `write_todos` | 任务规划工具，维护结构化待办列表 | ch15 |
| Subagent | 独立上下文的子代理，用 `task` 工具派发 | ch15 |
| Skills | 按需加载的领域知识包（`SKILL.md`），渐进式披露 | ch16 |
| Memory | 跨会话持久的指令与偏好（`AGENTS.md`） | ch16 |

---

## 示例代码

两套示例**一一对应**，覆盖同样的 17 个主题。**全部离线可跑**——用一个脚本化的假模型替代真实 LLM，不需要 API Key、不产生网络请求，结果确定可复现。

```bash
# Python
cd code/python
python -m venv .venv && . .venv/Scripts/activate   # Windows
pip install -r requirements.txt
python 02_models.py

# TypeScript
cd code/typescript
pnpm install
pnpm run 02_models
```

| 章节 | Python | TypeScript | 演示什么 |
|---|---|---|---|
| 2 | `02_models.py` | `02_models.ts` | 三种入参归一化、`AIMessage` 结构、stream / batch |
| 3 | `03_messages_prompts.py` | `03_messages_prompts.ts` | 四种消息、历史裁剪、模板的三种调用方式 |
| 4 | `04_structured_output.py` | `04_structured_output.ts` | 四种 schema 模式、校验失败、工具策略自动重试 |
| 5 | `05_create_agent.py` | `05_create_agent.ts` | Agent Loop、状态只追加、结构化输出 |
| 6 | `06_middleware.py` | `06_middleware.ts` | 六个钩子的真实触发顺序 |
| 7 | `07_tools.py` | `07_tools.ts` | 工具定义、`ToolRuntime` 注入、工具内改状态 |
| 8 | `08_rag.py` | `08_rag.ts` | 加载、切分、假嵌入、内存向量库、检索器接成工具 |
| 9 | `09_context.py` | `09_context.ts` | 摘要压缩触发、工具输出卸载 |
| 10 | `10_state_graph.py` | `10_state_graph.ts` | Reducer 语义、条件边、`Send` 并行 |
| 11 | `11_persistence.py` | `11_persistence.ts` | 检查点、时间旅行、Store 跨线程 |
| 12 | `12_hitl_stream.py` | `12_hitl_stream.ts` | `interrupt`/`resume`、`stream_mode` |
| 13 | `13_deep_agent.py` | `13_deep_agent.ts` | 预装工具集、HarnessProfile |
| 14 | `14_filesystem.py` | `14_filesystem.ts` | 文件工具与权限判定 |
| 15 | `15_delegation.py` | `15_delegation.ts` | 规划与子代理派发 |
| 16 | `16_skills_memory.py` | `16_skills_memory.ts` | 技能加载与记忆注入 |
| 17 | `17_observability.py` | `17_observability.ts` | trace 结构（离线桩） |
| 18 | `18_multiagent.py` | `18_multiagent.ts` | 多智能体拓扑与迁移映射 |

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
| 图 12 | 工具调用往返与 `ToolRuntime` 注入 | ch07 |
| 图 13 | MCP 接入与多服务器聚合 | ch07 |
| 图 14 | RAG 检索链路 | ch08 |
| 图 15 | 文档切分与向量化 | ch08 |
| 图 16 | 上下文四种手段 | ch09 |
| 图 17 | 缓存前缀边界 | ch09 |
| 图 18 | 图的基本构件 | ch10 |
| 图 19 | Reducer 合并语义 | ch10 |
| 图 20 | 条件边与 `Send` 并行 | ch10 |
| 图 21 | Store 跨线程分层 | ch11 |
| 图 22 | 检查点落盘与恢复 | ch11 |
| 图 23 | 时间旅行 | ch11 |
| 图 24 | interrupt / resume 时序 | ch12 |
| 图 25 | stream_mode 的七种投影 | ch12 |
| 图 26 | Deep Agents 预装中间件栈 | ch13 |
| 图 27 | 文件工具集与权限判定 | ch14 |
| 图 28 | 规划循环 | ch15 |
| 图 29 | 子代理的上下文防火墙 | ch15 |
| 图 30 | 技能渐进式披露与记忆时间尺度 | ch16 |
| 图 31 | trace 结构与可观测三层 | ch17 |
| 图 32 | 多智能体拓扑 | ch18 |

---

## 版本与来源

本教程的 API 描述**以实测为准**——所有代码在下列版本上真跑过，文档只用于补足概念与设计意图。

| 组件 | 实测版本 |
|---|---|
| `langchain` | 1.4.2 |
| `langgraph` | 1.2.12 |
| `deepagents` | 0.7.18 |
| `langchain-core` | 1.6.4 |
| `langchain-openai` / `langchain-anthropic` | 1.6.5 / 1.7.4 |

**来源分级**：

- **一手（官方文档 / 官方仓库）**：`docs.langchain.com` 的 OSS Python 与 JavaScript 文档、`reference.langchain.com` API 参考
- **实测（本仓库）**：本目录 `code/` 下示例的运行输出——**与文档冲突时以实测为准**，差异在正文中显式标注
- **版本锚点**：LangChain v1 与 LangGraph v1 于 **2025-10-22** 同步 GA；`deepagents` 独立演进，**两个语言的版本号不同步**（Python 0.7.x / JS 1.x）

逐章 URL、访问日期与实测记录见 [`_写作大纲与来源登记.md`](_写作大纲与来源登记.md)。

---

## 已知限制

- **真实模型端到端未实测**：本机无模型 API Key，示例用脚本化假模型验证**框架的机制**（循环、钩子、状态、检查点、中断、流式、工具派发）。凡是**只有真实模型才能暴露**的行为（如模型的工具选择倾向、提示词遵从度、真实 token 计费）**不在实测范围内**，正文中逐处标注「需 API Key，未实测」。
- **LangSmith 上报未实测**：`LANGSMITH_TRACING` 相关的端到端上报需要账号，ch13 的 trace 结构用离线桩演示，字段名以官方文档为准。
- **MCP 真实服务器未实测**：MCP 接入的代码路径以官方文档为准，正文标注。
- **版本漂移**：三个框架迭代很快，且 `deepagents` 的 Python 包与 JS 包**版本号不同步**。**如与最新版本有出入，以官方文档与仓库实际代码为准。**
- **图示为机制示意**：图中的节点名、工具名来自实测，但布局与配色是为讲解服务的，不代表框架内部实现结构。

---

## 维护约定

- 章节骨架固定：`## 一、这一章要解决的问题` → `## 二、机制与原理` → `## 三、代码：Python 与 TypeScript` → `## 四、常见坑与边界条件` → `## 五、关键结论` → `## 本章要点回顾`
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
- 图号**全局连续且按出现顺序递增**；新增图插在中间时，其后图号顺延，并同步更新本章图注、本 README 配图索引、`_写作大纲与来源登记.md` 配图清单，**并重跑 `_build_html.py`**
- HTML 精读版保持**单文件自包含**；内联 SVG 的 marker `id` 必须加图号前缀去重（`_build_html.py` 已处理）
- 英文逐字引用必附中译
- 事实性数字必须标注来源与时间；查不到出处的性能数字不采用
- **本目录的结论以实测为准**：凡 API 名、参数名、默认值，与官方文档冲突时按实测写，并把差异登记进 `_写作大纲与来源登记.md`

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

复核方法：读正文 + 跑示例 + **读本机已装包源码** + 查官方文档，四路交叉。示例实跑 **Python 13/13、TypeScript 13/13** 全部通过。查出并修正下列问题——

| 类型 | 问题 | 处理 |
|---|---|---|
| **事实错误 · 子代理并行** | ch11 写「默认 `isolated` 的子代理是串行被派发的」 | 源码 `TASK_TOOL_DESCRIPTION` 明写「Launch multiple agents **concurrently** … using a single message with multiple tool calls」，官方 subagents 页同口径。改为「**可以**并发（一轮发多个 `task`），但发几个由模型决定，不保证」 |
| **事实错误 · 并行写同键** | ch06 写「并行分支写同一个无 reducer 字段，结果甚至可能不确定」 | 实测直接抛 `InvalidUpdateError: At key 'x': Can receive only one value per step.`——不是「不确定覆盖」，是**跑起来报错**。ch06 坑与结论同步改写 |
| **事实错误 · 迁移等价性** | ch14 三步顺序第 1 步写「`AgentExecutor` → `create_agent` 这一步**行为等价**」 | 官方 v1 迁移文档明确「不是行为等价」，且 ch14 自己的映射表就列着 5 处破坏性变更（`input`→`messages`、无 `output` 字段、hook→middleware、state 必须 `TypedDict`、流式节点名 `agent`→`model`）。改为「**接口迁移，非行为等价**」 |
| **结论写反 · 要点回顾** | ch04 要点回顾写「默认 `ToolNode` 本来就会把异常吞成 error `ToolMessage`」，与本章 2.6 节（Python 原样抛出、JS 才吞）**正相反** | 按 2.6 节实测结论改写为「两语言相反」，并补源码依据（`langchain/agents/middleware/types.py`：`Exceptions propagate unless handle_tool_errors is configured`） |
| **表述过强 · 「已废弃」** | ch04 / ch14 / `code/README.md` / 来源登记统一写 `ToolException` / `handle_tool_error`「已废弃 / 已不使用」 | 实测 **API 未删除**：`langchain.tools` 仍导出 `ToolException`，`StructuredTool` 仍有 `handle_tool_error` 字段，`langchain/mcp/tools.py` 自己就在用。全书统一改为「**不再推荐**（v1 agent 路线换了入口），但 API 仍在包里」 |
| **自相矛盾 · 分层口号** | ch01 写「LangChain 不知道什么叫检查点」，但 ch02 参数表里就有 `checkpointer` | 改为「**心智模型上的分工**，不是能力边界」，并点明 `create_agent` 编译出来就是 LangGraph 图、LangGraph 也自带 `ToolNode` |
| **表述过强 · 永久丢失** | ch05 写摘要后原文「永久丢失」、「时间旅行只能回到摘要后的状态」 | 实测（摘要中间件 + `InMemorySaver`，6 轮）：最终状态 8 条，而 `get_state_history` 的 **42 个快照**里仍能翻出第 1 轮的长工具输出原文。改为「**不配 checkpointer** 时不可恢复；配了则更早的快照仍保有原文」 |
| **缺限定 · 权限默认放行** | ch10 只写「没命中任何规则 → 走默认策略」，**没写明默认是 allow** | 补上「默认 **allow（放行）**」并给源码依据（`_check_fs_permission` 收尾 `return "allow"`），点明「只声明一条 deny 得不到白名单效果」 |
| **缺限定 · delete 不吃首匹配** | ch10 写「按声明顺序首次匹配即生效」是「唯一必须背下来的纪律」 | 源码对 `delete` 单独处理：目标可能有子孙时，任何能覆盖该子树（或其祖先）的 `deny write` 都会拦下删除，**不管排多后**（`regardless of rule order`）。补为「顺序纪律只对 `read` / `write` / `edit` 成立，**`delete` 是例外**」 |
| **缺限定 · 权限与执行后端互斥** | ch10 把 `FilesystemPermission` 与 `LocalShellBackend` 放在同一节讲，未提两者不能同时用 | 实测 `FilesystemMiddleware(backend=LocalShellBackend(), _permissions=[...])` 抛 `NotImplementedError: … does not yet support permissions with backends that provide command execution`。新增第 6 条坑，并附官方警告「`root_dir` / `virtual_mode=True` 都不是 shell 的安全边界」 |
| **表述过强 · 技能白搭** | ch12 写「技能与记忆都靠文件承载，所以都必须配持久化后端」，开篇提问更写成「不配持久化后端，技能与记忆都是白搭」 | 官方 skills 页明确 `StateBackend` 下 skills **可正常工作**（`invoke(files=...)` 传入即可），持久化后端只解决「跨线程存活」。拆成 Skills / Memory 两条分别表述；并补「**记忆不是自动积累**——agent 得主动 `edit_file`」 |
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
| **原有章节顺延** | 原 ch02–ch14 → 新 ch05–ch18（两段位移 +3 / +4）；正文 94 处「第 N 章」互引按查表改写，区间引用人工重排 |
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
