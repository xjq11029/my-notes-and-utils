# 第 19 章 迁移与部署：一张映射表与上线前检查

## 一、这一章要解决的问题

前面 18 章讲的都是「怎么把一个 agent 搭出来、组织好」。这一章处理两个收尾问题：

1. **老代码怎么迁过来**——很多团队手上是 LCEL / `AgentExecutor` 写的 agent。v1 不是换个函数名，而是换了一套控制流的表达方式。
2. **上线前要确认什么**——本地跑通不等于能上生产，有三件事必须在上线前定死。

> **给从没用过 v0.x 的读者**：LCEL 是旧版用 `|` 管道把组件串成一条链的编排方式；`AgentExecutor` 是旧版创建 agent 的类；`ConversationBufferMemory` 是旧版管理对话历史的记忆组件。v1 用 `create_agent` + 图 + middleware 替换了它们——这一章讲的迁移，就是把这三样旧东西换成新表达。

> 版本锚点：本章结论在 `langchain` **1.4.2** / `langgraph` **1.2.12**（Python）与 `langchain` **1.5.11** / `@langchain/langgraph` **1.4.17**（JS）上实测；迁移映射表的打印见 `code/python/18_multiagent.py` 与 `code/typescript/18_multiagent.ts`（与第 18 章共用同一示例，无单独的 19 号示例）。

## 二、机制与原理

### 2.1 从 LCEL / AgentExecutor 迁移到 v1：一张映射表

很多团队手上是旧版代码。下面这张表回答「我以前那样写，现在该怎么写」。旧版指 LCEL 编排 + `AgentExecutor`（Python）/ 旧版 JS 写法。

| 能力 | 旧版写法 | v1（Python） | v1（TypeScript） |
|---|---|---|---|
| 建 agent | `AgentExecutor(agent=..., tools=...)` | `create_agent(model, tools)` | `createAgent({ model, tools })` |
| 调用 | `executor.invoke({"input": "..."})` | `agent.invoke({"messages": [...]})` | `agent.invoke({ messages })` |
| 输入形态 | 字符串 `input` | 消息列表 `messages` | 消息列表 `messages` |
| 输出形态 | `{"output": "..."}` | `{"messages": [...]}`，取 `messages[-1]` | 同左，取 `messages.at(-1)` |
| 提示词 | prompt 模板字符串 | `system_prompt=` + middleware | `prompt` / `systemPrompt` + middleware |
| 记忆 | `memory=ConversationBufferMemory()` | checkpointer + `thread_id` | checkpointer + `thread_id` |
| 工具错误 | `handle_tool_error` / `ToolException` | `@wrap_tool_call` 或 `ToolErrorMiddleware` | `wrapToolCall` 或 `toolErrorMiddleware` |
| 运行时注入 | `InjectedState` / `InjectedStore` | `runtime: ToolRuntime` | `runtime` 参数 |
| 链式拼装 | LCEL 的 `|` 管道 | `StateGraph` 的 `add_node` / `add_edge` | `StateGraph` 的 `addNode` / `addEdge` |
| 扩展点 | 自定义 Agent / 继承 | middleware 的六个钩子 | middleware 的六个钩子 |
| 流式节点名 | 编译图里 agent 节点叫 `agent` | 改叫 `model`（按节点名过滤流式事件时受影响） | 改叫 `model_request`（节点名两语言本就不同，见差异清单第 12 条） |

这张表里有两行是**机制替换**，不是「换了个名字」：**工具错误**（v1 的 agent 路线**不再推荐** `ToolException` / `handle_tool_error`——注意这两个 API **仍在包里**，只是入口换成了中间件，实测结论）与**运行时注入**（`InjectedState` / `InjectedStore` 统一收口到 `runtime: ToolRuntime`，实测结论）。这两处照抄旧代码在 v1 上都不成立，得改写法。

> ⚠️ **「旧版写法」一列未在本机重跑**：本机只装了 v1（`langchain` 1.4.2 / `langgraph` 1.2.12），旧版 LCEL / `AgentExecutor` 环境没有安装，这一列来自官方迁移文档与示例中的对照表，**不是实测结论**；v1 侧那一列是实测。

### 2.2 迁移的心智转变与三步顺序

比记 API 更重要的是**心智模型换了**：

- **旧版：agent 是一个「组件」**。你有一个 executor，用 LCEL 的 `|` 把它串进一条链里，链的形状是**线性的**。
- **v1：agent 是一张「图」**。你用节点和边定义控制流，用 middleware 扩展行为，图可以**有分支、有循环、有并行**。

所以「迁移」不是换函数名，而是**把控制流从「链式表达」改成「图表达」**。这也是为什么迁移完代码结构往往要变——旧版表达不了的东西（条件分支、循环、人工审批），新版才表达得了。

**三步建议顺序**（一次全改，出了问题分不清是哪一步引入的）：

1. **先换 `AgentExecutor` → `create_agent`**。这一步**只动构造与调用形态，不动流程结构**——但**不是「行为等价」**：对照 2.1 的映射表，输入从 `input` 变成 `messages`、输出不再有 `output` 字段、hook 要搬进 middleware、state 必须改成 `TypedDict`、流式节点名从 `agent` 变成 `model`（Python）/ `model_request`（JS）。把它当成一次**接口迁移**来做，改完先确认功能没变，再往下走。
2. **再改 LCEL → `StateGraph`**。这一步才真正动结构，是风险最大的一步。
3. **最后把自定义逻辑收进 middleware**。前两步稳定之后，再把横切逻辑（日志、限流、错误处理）从业务代码里抽出来。

### 2.3 两种部署形态

agent 最终要跑到某个地方。这张表回答「托管还是自托管」。

| | 托管（Agent Server） | 自托管 |
|---|---|---|
| 持久化 | 服务端自动提供（checkpointer / store 不用自己配） | 自己接 Postgres 等 |
| 可观测 | 自带 trace、评测、人工审批 UI | 自己接观测后端 |
| 自由度 | 受平台约束 | 最高 |
| 代价 | 绑定平台，本地与线上差异要自己盯 | 持久化必须**一开始就做对** |

自托管里最要命的是最后那句。**中途从 `InMemorySaver`（JS `MemorySaver`）换成 `PostgresSaver`，历史数据是搬不过去的**——两种 saver 的存储结构不同，已经产生的会话找不回来。这不是「换个类」就完事，而是**上线前就要定死**的事。

### 2.4 上线前必查三件事

不管选哪种形态，这三条必须在上线前确认。这张表回答「上线前还有哪些坑没堵」。

| # | 检查项 | 不做的后果 |
|---|---|---|
| 1 | **检查点有没有持久化** | 进程一重启，所有会话丢失；多副本部署时同一用户请求落到不同副本，上下文对不上 |
| 2 | **有没有调用次数上限** | agent 可能陷入循环，模型调用和工具调用都要设上限，否则账单和延迟同时失控 |
| 3 | **高风险操作有没有人在回路** | 扣款、发邮件、删文件这类不可逆操作，必须有 `interrupt()` 审批（第 13 章） |

## 三、代码：Python 与 TypeScript

本章无新增示例：迁移映射表的打印、部署形态说明都在第 18 章的示例里（`code/python/18_multiagent.py` / `code/typescript/18_multiagent.ts`），两个语言均已实跑通过。

## 四、常见坑与边界条件

1. **`ToolException` / `handle_tool_error` / `InjectedState` / `InjectedStore` 在 v1 都不是推荐写法**（实测结论）——前两者的 API 仍在包里、只是 agent 路线换了入口；后两者被 `runtime: ToolRuntime` 取代。迁移时这两处是机制替换，不是改名。
2. **别一次全改**。三步顺序（executor → 图 → 中间件）是为了让每一步都可单独验证；跳过第一步直接改结构，出问题会同时面对两套变量的干扰。
3. **`InMemorySaver` → `PostgresSaver` 搬不了历史数据**，持久化方案必须在上线前定死。

## 五、关键结论

1. **迁移的 10 行映射表**里，有两处是机制替换而非改名：工具错误（走中间件）与运行时注入（统一 `ToolRuntime`）。
2. **迁移的心智转变**：旧版 agent 是一个组件、用 LCEL 串进链；v1 agent 是一张图、用节点和边定义控制流。
3. **三步顺序**：先 `AgentExecutor` → `create_agent`（**接口迁移，非行为等价**），再 LCEL → `StateGraph`（动结构），最后收进 middleware。
4. **部署两形态**：托管省持久化与 UI，代价是绑定平台；自托管自由但持久化必须一开始就做对。
5. **上线前必查三件事**：检查点持久化、调用次数上限、高风险操作的人在回路。

## 本章要点回顾

- **迁移 10 行映射**：建 agent / 调用 / 输入 / 输出 / 提示词 / 记忆 / 工具错误 / 运行时注入 / 链式拼装 / 扩展点。
- **两处机制替换**：工具错误走中间件；运行时注入统一 `ToolRuntime`。
- **心智转变**：组件 + LCEL → 图 + 节点 / 边 + middleware。
- **三步顺序**：`AgentExecutor` → `create_agent`；LCEL → `StateGraph`；逻辑收进 middleware。
- **部署**：托管（自动持久化 + UI，绑定平台）vs 自托管（自由，但 `InMemorySaver` → `PostgresSaver` 搬不了历史数据）。
- **上线三查**：检查点持久化 / 调用次数上限 / 高风险操作的人在回路。

## 全书回顾

到这里 19 章走完，主线其实只有一条：**把「模型 + 循环」做成一个可控、可观测、能上生产的系统**。按章顺序串起来是：

- **第 1 章**先立坐标：**基础层**（模型、消息、提示词、结构化输出）是三件套的共同地基；其上 LangChain 是构建块、LangGraph 是运行时、Deep Agents 是成品 harness——分层决定了后面每一章在讲哪一层。
- **第 2–4 章**是地基：模型怎么造（第 2 章）、话怎么说（第 3 章）、结果怎么收（第 4 章）——它们不碰循环，但决定了循环里每句话的形态。
- **第 5–9 章**在 LangChain 层：先用 `create_agent` 拿到 **agent loop**（第 5 章），再用 **middleware** 把循环各阶段打开成插槽（第 6 章），接着把**工具与上下文注入**接上（第 7 章），用 **RAG 全链路**把外部知识接进来（第 8 章），最后系统化地做**上下文工程**（第 9 章）。
- **第 10 章**是可观测：trace / 数据集 / 成本——它只依赖第 5 章，却是排查后面一切「模型不听话」的眼镜。
- **第 11–13 章**下沉到 LangGraph：**图与状态**定义控制流（第 11 章），**持久化**让状态存得下来、能续跑（第 12 章），**人在回路与流式**建立在检查点之上（第 13 章）。
- **第 14–17 章**升到 Deep Agents：**全景**看预装了哪些能力（第 14 章），再逐块展开**虚拟文件系统与执行环境**（第 15 章）、**规划与委派**（第 16 章）、**技能与记忆**（第 17 章）。
- **第 18–19 章**是工程收尾：**多智能体**回答「多个怎么组织」（第 18 章），**迁移与部署**回答「老的怎么过来、上线的边界在哪」（第 19 章）。

一句话概括：**第 5–9 章教你把一个 agent 搭出来，第 10 章让你看得见它，第 11–13 章教你把它的状态与中断管住，第 14–17 章给你一套开箱的成品，第 18–19 章把它送进生产。**

- **全书主线**：搭出来（5–9）→ 看得见（10）→ 管住状态（11–13）→ 开箱成品（14–17）→ 送进生产（18–19）。
