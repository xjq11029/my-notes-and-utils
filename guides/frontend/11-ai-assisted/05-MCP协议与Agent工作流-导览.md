# MCP 协议与 Agent 工作流 - 导览

> 对应原文：[05-MCP协议与Agent工作流.md](./05-MCP协议与Agent工作流.md)

---

## 核心概念

| 维度 | 内容 |
|------|------|
| 是什么 | MCP 协议与 Agent 工作流是"让 AI 接入工程体系"的两大支柱。MCP（Model Context Protocol）是 Anthropic 于 2024 年 11 月开源的开放协议，基于 JSON-RPC 2.0，标准化大模型应用连接外部工具与数据源的方式；Agent 工作流是让模型自主多步完成任务的工程方法体系 |
| 能做什么 | MCP 把"M 个应用 × N 个数据源"的集成爆炸问题变成 M + N；Agent 工作流通过 ReAct、Plan-and-Execute、多 Agent 协作把复杂任务拆解执行；配套的 AI 前端生成工具（v0 / Bolt / Lovable）与 RAG 解决"从零生成"与"私有知识"两类需求 |
| 怎么用 | 先理解 MCP 的三层架构与三大能力，再手写一个 MCP Server 接入组件库 / 设计稿 / 接口文档 / 浏览器自动化；Agent 侧按「探索 → 规划 → 人工确认 → 执行 → 自验证 → 交付」六阶段设计工作流；RAG 按「离线索引 + 在线检索生成」两段落地 |
| 原理和工作流程 | MCP 通过 Host / Client / Server 三层解耦能力提供方与消费方，Host 把 Server 暴露的 Tools 转换为模型的 Function Calling schema，模型输出调用意图后 Host 翻译为 MCP 请求；Agent 的核心是"推理-行动-观察"循环，上下文管理（压缩、外部记忆、子 Agent 隔离、按需检索）决定其可靠性 |
| 缺点 | MCP Server 以用户身份执行操作，权限过宽会导致误操作；多 Agent 的 Token 消耗是单 Agent 的 3-10 倍且调试困难；RAG 需要维护索引与检索质量；AI 生成工具不了解内部设计系统与业务约束，产物不能直接进生产 |

---

## MCP 三层架构与三大能力

| 维度 | 内容 |
|------|------|
| 是什么 | MCP 采用 Host / Client / Server 三层架构；Server 可暴露 Tools / Resources / Prompts 三类能力 |
| 能做什么 | 让任何 Host（IDE、CLI、桌面应用）接入任何 Server，无需为每个 Host 单独适配；一次实现工具，多处复用 |
| 怎么用 | Host 是宿主应用（Claude Desktop / Claude Code / IDE），Client 是协议连接器（与 Server 一对一），Server 是能力提供方；本地 Server 用 `command` + `args` 配置启动，远程 Server 用 Streamable HTTP 接入 |
| 原理和工作流程 | Host 运行模型、管理会话、决定何时调用工具；Client 负责能力协商与生命周期管理，与 Server 一对一（一个 Host 可创建多个 Client）；Server 执行业务逻辑并返回结果。三大能力的区分标准是"谁决定使用"：Tools 由模型决定（可执行动作、有副作用）、Resources 由应用决定（只读上下文）、Prompts 由用户决定（预置提示词模板）。Client 侧还有 Sampling / Roots / Elicitation 三类反向能力 |
| 缺点 | Server 以用户身份执行操作，接入数据库、生产接口、CI 触发类工具时必须限定只读权限或走审批；协议仍在快速演进，不同版本间存在传输方式等差异 |

---

## MCP 传输方式与 Function Calling 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | MCP 支持 stdio 与 Streamable HTTP 两种现行传输方式（HTTP+SSE 已被取代）；MCP 与 Function Calling 处于不同层次，不是替代关系 |
| 能做什么 | stdio 适合本地工具（文件系统、Git、本地数据库），Server 作为子进程启动；Streamable HTTP 适合远程 Server，单端点 + 可选 SSE 升级 + `Mcp-Session-Id` 会话管理 |
| 怎么用 | stdio 下 Host 用 `command` + `args` 启动子进程，通过 stdin / stdout 交换 JSON-RPC 消息；Streamable HTTP 下客户端 POST 到单端点，服务端可返回 JSON 或升级为 SSE 流，会话通过 `Mcp-Session-Id` 响应头维护 |
| 原理和工作流程 | stdio 传输下 stdout 是协议通道，**日志必须写 stderr**，否则会污染协议消息导致连接异常。MCP 与 Function Calling 的关系：Function Calling 是模型能力（模型输出结构化调用意图，写在每次 API 请求的 `tools` 参数里），MCP 是通信协议（工具由独立 Server 暴露，含工具 + 资源 + 提示词 + 生命周期 + 能力协商 + 传输 + 鉴权）。Host 把 MCP Tools 转换为 Function Calling schema，模型输出意图后 Host 翻译为 `tools/call` 请求 |
| 缺点 | 一句话总结：Function Calling 解决"模型怎么表达要调用什么"，MCP 解决"工具从哪里来、怎么统一接入"；面试中若把 MCP 说成 Function Calling 的替代品会直接失分 |

---

## Agent 工作流：ReAct 与 Plan-and-Execute

| 维度 | 内容 |
|------|------|
| 是什么 | ReAct 是"推理-行动循环"（Thought → Action → Observation），Plan-and-Execute 是"先规划再执行" |
| 能做什么 | ReAct 适合步骤不确定、需要探索的任务；Plan-and-Execute 适合步骤可预判、任务较长的场景；两者都通过工具调用与外部世界交互 |
| 怎么用 | ReAct 主循环：模型输出最终答案或工具调用意图 → 并行执行工具 → 把结果回填为 tool 消息 → 继续推理，循环受 `maxSteps`（8-15）限制；Plan-and-Execute 由 Planner 输出步骤列表、Executor 逐步执行、Replanner 按结果调整计划 |
| 原理和工作流程 | ReAct 每步都基于最新观察重新推理，Token 消耗较高（每步带完整历史）；Plan-and-Execute 执行阶段按计划走，Token 消耗较低。工程要点：必须有步数上限防止死循环；工具结果超长要截断（避免一次吃满上下文）；失败时把错误作为 Observation 回填让模型自我修正；无依赖的工具调用并行执行 |
| 缺点 | ReAct 容易在局部打转；Plan-and-Execute 的计划一旦错误会全错，必须靠 Replanner 兜底；直接抛错会让 Agent 无法自愈，单纯重复同一调用只会重复失败 |

---

## Agent 工作流：多 Agent 协作与工具设计

| 维度 | 内容 |
|------|------|
| 是什么 | 多 Agent 协作的主流模式是编排者-工作者（Orchestrator-Worker）；工具（Tool）设计是决定 Agent 可靠性的关键因素 |
| 能做什么 | 多 Agent 实现上下文隔离与子任务并行；好的工具设计让 Agent 准确选对工具、传对参数、正确解读结果 |
| 怎么用 | 编排者负责拆解任务、分派子任务、汇总结果，工作者只看到与自己子任务相关的上下文；工具定义需包含语义化命名、写清"何时用"的描述、Zod 等 schema 约束的参数、紧凑结构化的返回值、可行动的错误信息 |
| 原理和工作流程 | 多 Agent 的核心收益不是"更强"而是"上下文隔离"——避免单个 Agent 的上下文被无关信息撑爆。其他模式包括顺序流水线（生成 → 审查 → 修复）、层级式、对抗式（互相审查）。工具描述本身就是 Prompt：需说明使用时机、返回内容边界、与相似工具的区别；错误信息要引导模型换一种尝试方式（如"未找到 xxx，请先用 search_components 确认组件名"） |
| 缺点 | 多 Agent 的 Token 消耗通常是单 Agent 的 3-10 倍，调试难度显著上升（一个错误可能来自编排者、工作者或信息传递），端到端延迟增加；实践原则是"能用单 Agent 加好工具解决的任务，不要上多 Agent" |

---

## 上下文管理与 RAG 流程

| 维度 | 内容 |
|------|------|
| 是什么 | 上下文管理是 Agent 的稀缺资源调度问题；RAG（检索增强生成）解决"模型不知道你的私有知识" |
| 能做什么 | 上下文管理让长任务不因窗口超限而失效；RAG 把外部知识注入上下文，并支持返回引用来源 |
| 怎么用 | 上下文四类手段：压缩（接近阈值时总结历史并重建）、外部记忆（写入文件 / 数据库按需检索）、子 Agent 隔离（只回传结论）、按需检索 JIT（用工具按需拉取）；RAG 离线阶段做「文档加载 → 切分 → 向量化 → 存向量库」，在线阶段做「问题向量化 → 检索 top-k → rerank → 拼装 Prompt → 生成 → 流式返回」 |
| 原理和工作流程 | 压缩的两个风险：摘要丢失细节可能遗忘关键约束（需在摘要 Prompt 中明确要求保留已完成工作、关键决策与理由、待办事项、重要文件路径、禁忌），以及压缩本身消耗一次模型调用。RAG 的关键决策：切分按语义边界（300-800 token，重叠 10-20%）、混合检索（BM25 + 向量）对专有名词更好、先召回 top-50 再用 rerank 精选 top-5、Prompt 中要求"只依据给定片段回答"并标注来源。RAG 与微调的选择：知识类需求优先 RAG（更新成本低、可溯源），风格类需求才考虑微调 |
| 缺点 | 压缩过于频繁会显著增加成本；上下文不是越长越好，信息密度过高反而让模型抓不住重点；RAG 的检索质量依赖切分与 rerank 调优，纯向量检索对专有名词不擅长 |

---

## MCP Server 开发与前端落地场景

| 维度 | 内容 |
|------|------|
| 是什么 | 基于官方 TypeScript SDK（`@modelcontextprotocol/sdk`）手写 MCP Server，并接入前端开发链路中的设计稿、接口文档、数据库、组件库、浏览器自动化等对象 |
| 能做什么 | 让 AI 助手查询内部组件库列表与 API（避免编造组件名与 Props）、读取设计令牌与图层结构、按 OpenAPI 定义生成请求代码、读取数据库表结构生成类型、通过浏览器自动化形成"改代码 → 验证 → 再改"的闭环 |
| 怎么用 | 用 `new McpServer({ name, version })` 创建实例；`server.registerTool(name, { title, description, inputSchema }, handler)` 注册工具；`server.registerResource(...)` 注册只读资源；`server.registerPrompt(...)` 注册提示词模板；用 `StdioServerTransport` 连接本地进程，或用 `StreamableHTTPServerTransport` 部署远程；调试用 `@modelcontextprotocol/inspector` |
| 原理和工作流程 | 工具处理器返回 `{ content: [{ type: 'text', text }] }`；出错时返回 `{ isError: true, content: [...] }` 并给出可行动的下一步建议。本地 Server 的日志必须写 stderr（`console.error`），因为 stdout 是协议通道。远程部署时每个会话对应一个 transport 实例，用 `Mcp-Session-Id` 关联。前端开发中最有价值的接入是浏览器自动化——它让 Agent 从"能写代码"进化到"能验证代码" |
| 缺点 | Server 以用户身份执行操作，接入生产系统必须限定权限；工具返回内容过大会占用上下文；Server 的构建产物需要维护，且不同 Host 的配置格式存在差异（如 Claude Desktop 用 `claude_desktop_config.json`，Claude Code 用 `claude mcp add`） |

---

## Agent 工作流落地与 Human-in-the-loop

| 维度 | 内容 |
|------|------|
| 是什么 | 把"实现一个带筛选的列表页"这类中等规模任务交给 Agent 自主完成，并用 Human-in-the-loop 控制风险 |
| 能做什么 | 通过六阶段流程（探索 → 规划 → 人工确认 → 执行 → 自验证 → 交付）让 Agent 产出与项目风格一致的代码，并在不可逆操作前停下 |
| 怎么用 | 探索阶段先用工具读现有代码范式；规划阶段输出组件树 + 数据流 + 复用组件清单；人工确认后分步生成并逐步验证；自验证阶段跑 `typecheck` / `lint` / `test` 并用浏览器工具验证页面；危险操作（删除文件、写库、`git push`、发布）在工具执行前拦截并要求显式批准 |
| 原理和工作流程 | HITL 的三种介入点：方案审批（规划阶段暂停等待确认）、危险操作确认（工具调用前拦截）、异常升级（重试 N 次仍失败或涉及安全 / 支付 / 权限逻辑时停止并上报）。失败重试的边界：重试必须带上失败原因才有意义——把错误信息作为 Observation 回填，模型才能换一种方式尝试；超过上限应升级为 HITL 而非继续硬试 |
| 缺点 | 全自动执行到 PR 会让人只看结果不看过程，风险高；探索阶段若跳过"读现有代码"，产出风格会与项目完全不一致；自验证需要项目本身有 typecheck / lint / test 基础设施 |

---

## AI 前端生成工具（v0 / Bolt / Lovable）

| 维度 | 内容 |
|------|------|
| 是什么 | v0、Bolt、Lovable 是三类定位不同的 AI 前端生成产品：v0 专注 UI 组件与页面生成，Bolt 基于 WebContainers 在浏览器内跑 Node 做全栈脚手架，Lovable 是对话式全栈应用生成 |
| 能做什么 | v0 生成 React / Next.js + Tailwind + shadcn/ui 的高保真 UI（支持从截图生成）；Bolt 从零搭可运行的全栈 Demo（能 install / build / 预览）；Lovable 生成带登录与数据持久化的完整小应用 |
| 怎么用 | 需求评审时快速出可点原型、探索"这个交互怎么做"、生成标准 CRUD 页面的骨架、学习某个库的常见写法；产物必须经代码审查、替换为设计令牌、补齐边界态与测试后才能进生产 |
| 原理和工作流程 | 能力边界：擅长标准 UI 布局与常见交互，不擅长复杂业务状态机、性能敏感渲染（虚拟滚动、大数据量图表）、无障碍与边界态，也不了解公司内部组件库与私有工具。产物质量问题包括巨型单文件组件（600 行逻辑与视图混杂）、编造 API、样式硬编码、缺少 loading / error / empty 三种状态、无测试、无障碍缺失 |
| 缺点 | 核心原则是"把 AI 生成工具当作草稿生成器而不是代码交付方"——它可以帮你跳过"从空白文件开始"的阶段，但架构决策、设计系统对齐、边界态处理、安全审查仍必须由人完成 |

---

## 前端消费 RAG 结果与流式渲染

| 维度 | 内容 |
|------|------|
| 是什么 | 前端如何消费 RAG 的检索结果与流式输出，包括技术选型、SSE 解析、渲染节流与请求取消 |
| 能做什么 | 实现打字机效果的流式回答、展示引用来源、支持用户中途取消、避免逐 token 更新导致的卡顿 |
| 怎么用 | 推荐 `fetch` + `ReadableStream` 手动解析 SSE（支持 POST / 自定义头 / `AbortController`）；解析时用 buffer 缓存不完整分片，按 `\n\n` 切分后把最后一段留回 buffer；`TextDecoder` 必须用 `stream: true`；渲染层用 `requestAnimationFrame` 节流；组件卸载时 `abort()` |
| 原理和工作流程 | 三种技术选择对比：`EventSource` 是浏览器原生 SSE 客户端但只支持 GET、无法传复杂 Body 与自定义头；`fetch` + `ReadableStream` 最灵活（推荐）；WebSocket 适合需要双向交互（如中途打断并追问）但服务端与网关改造成本高。SSE 事件块可能被 TCP 分片切断，所以必须做 buffer；多字节字符可能被分片截断，所以必须用 `stream: true`。渲染层的三件事：节流渲染、卸载取消、增量 Markdown 渲染容错（未闭合的代码块需补全或流式期间先用纯文本） |
| 缺点 | 手动解析 SSE 需要处理分片边界，实现比 `EventSource` 复杂；增量 Markdown 渲染在流式过程中可能出现格式错乱，需要容错处理；语义缓存与 rerank 需要额外的服务端能力支撑 |

---

## 常见问题与避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | MCP 与 Agent 落地中的典型陷阱：MCP Server 日志污染协议通道、能力分类错位、工具描述含糊、Agent 无步数上限、失败后直接抛错、过度使用多 Agent、压缩后遗忘约束、流式渲染卡顿、SSE 解析不做 buffer、RAG 答案编造 |
| 能做什么 | 帮助开发者提前识别并避免 MCP / Agent / RAG 落地中的典型问题，减少调试成本与线上风险 |
| 怎么用 | 对照排查：日志全部写 stderr；用"谁决定使用"区分 Tools / Resources / Prompts；工具描述写明使用时机与返回边界；设 `maxSteps` 并在超限时升级 HITL；失败信息回填上下文并附失败原因；多 Agent 只在需要上下文隔离时使用；流式渲染用 `requestAnimationFrame` 节流；SSE 解析用 buffer；RAG 的 Prompt 要求"只依据给定片段回答" |
| 原理和工作流程 | 常见错误根源：stdio 传输下 stdout 是协议通道，日志写 stdout 会污染 JSON-RPC 消息导致连接异常断开；工具描述本身就是 Prompt，含糊描述会让模型频繁选错工具；工具返回值直接进上下文，超长输出会一次吃满 token 预算；缺少 `maxSteps` 会让 Agent 陷入"调用-失败-再调用"死循环；错误信息不回填会让 Agent 无法自我修正；把 MCP 说成 Function Calling 的替代品是混淆了协议层次与模型能力；token 到达频率远高于帧率，逐条更新视图必然卡顿；SSE 事件块可能被 TCP 分片切断，不做 buffer 会偶发 JSON 解析错误；`TextDecoder` 不用 `stream: true` 会让中文乱码；组件卸载不取消流式请求会写入已销毁组件；RAG 不约束"只依据片段回答"会让模型编造内容 |
| 缺点 | 这些坑需要实践积累才能识别；部分问题（如权限过宽导致的误操作）后果不可逆，必须在设计阶段就加审批门；多 Agent 的调试难度高，错误定位需要完整的可观测性支撑 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./05-MCP协议与Agent工作流.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)
