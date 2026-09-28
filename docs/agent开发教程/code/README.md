# 示例代码（code）

本目录是 `docs/agent开发教程/` 的配套示例，**Python 与 TypeScript 一一对应**。

**全部示例都已在本机实跑通过**（见下方「实测记录」）。示例用**脚本化的假模型**替代真实 LLM，因此**不需要 API Key、不产生网络请求**，结果确定可复现。

---

## 为什么用假模型

本教程要验证的是**框架的机制**（循环、钩子、状态、检查点、中断、流式、工具派发），不是模型有多聪明。用真实 LLM 会引入三个干扰：

1. 需要 API Key 和网络，读者跑不起来；
2. 同样的输入未必给同样的输出，结论无法复现；
3. 分不清某个行为是框架做的还是模型做的。

所以两个语言各有一个「按脚本逐条吐消息」的假模型：

| 语言 | 文件 | 说明 |
|---|---|---|
| Python | `python/_fake_model.py` | `ScriptedChatModel`，实现 `bind_tools`（必须，否则 `create_agent` 报 `NotImplementedError`） |
| TypeScript | `typescript/_fakeModel.ts` | 同语义的 TS 版 |

两者都记录两样东西，这是本教程反复用到的观测手段：

- `seen` —— **模型每一次实际收到的消息**（中间件可以在消息到达模型前改写它，图状态里看到的可能仍是未改写的样子）
- `bound_tool_names` / `boundToolNames` —— **模型被绑定了哪些工具**（「注册了工具」≠「模型看得见」）

> 注：JS 侧自带 `FakeToolCallingModel`，但它的回复内容是从输入消息**回显**拼出来的、不受控，所以没有采用。

---

## 运行

### Python

```bash
cd code/python
python -m venv .venv
. .venv/Scripts/activate        # Windows；macOS / Linux 用 source .venv/bin/activate
pip install -r requirements.txt
python 02_create_agent.py
```

### TypeScript

```bash
cd code/typescript
pnpm install
pnpm run 02_create_agent        # 单个
pnpm run all                    # 全部（按顺序）
pnpm run typecheck              # 类型检查
```

---

## 示例索引

| 章 | Python | TypeScript | 演示什么 | 关键结论（实测） |
|---|---|---|---|---|
| 2 | `02_create_agent.py` | `02_create_agent.ts` | Agent Loop、状态只追加、两类作用域、结构化输出 | 消息序列 Human → AI(tool_call) → ToolMessage → AI(final)；第 2 轮历史 4 条而非 2 条 |
| 3 | `03_middleware.py` | `03_middleware.ts` | 六个钩子的真实触发顺序、`wrap_*` 改写请求 | 顺序：`before_agent → before_model → wrap_model_call → after_model → wrap_tool_call → before_model → wrap_model_call → after_model → after_agent` |
| 4 | `04_tools.py` | `04_tools.ts` | 工具 schema、`ToolRuntime` 注入、返回 `Command`、异常处理 | 返回 `Command` 必须自带匹配 `tool_call_id` 的 `ToolMessage`；v1 的 agent 路线不再推荐 `ToolException`（API 仍在包里） |
| 5 | `05_context.py` | `05_context.ts` | 摘要压缩 vs 工具输出卸载 | **两者机制不同**：摘要写回状态（4→24 被压到 8），卸载不回写状态（状态 4→24 但模型收到的 token 稳定在 253→588） |
| 6 | `06_state_graph.py` | `06_state_graph.ts` | Reducer、条件边、`Send`、`Overwrite` | 输入里出现的字段按各自 reducer 合并，没出现的保留检查点值；`invoke(None)` 是空操作、`invoke({})` 才是续跑 |
| 7 | `07_persistence.py` | `07_persistence.ts` | 检查点、时间旅行、Store 跨线程 | `updateState` 新建分支不改原线程；`store.search(('alice',))` 是**前缀**匹配，命中 3 条 |
| 8 | `08_hitl_stream.py` | `08_hitl_stream.ts` | `interrupt`/`resume`、`stream_mode`、子图流式 | 恢复时**整个节点从头重跑**（副作用日志出现两次）；agent 当子图时不加 `subgraphs` 就收不到内部消息 |
| 9 | `09_deep_agent.py` | `09_deep_agent.ts` | 默认工具集、`HarnessProfile`、中间件栈 | 工具节点注册 9 个但**模型只被绑定 8 个**（`execute` 因默认 `StateBackend` 不提供执行能力而未暴露）；`write_todos` 默认不开 |
| 10 | `10_filesystem.py` | `10_filesystem.ts` | 文件工具、权限、后端谱系 | `StateBackend` 把文件存在**图状态**里（`state.files`）；权限按声明顺序**首次匹配即生效** |
| 11 | `11_delegation.py` | `11_delegation.ts` | `write_todos`、子代理、`task` | `write_todos` 是**全量覆盖**语义；`SubAgent` 实测 11 个字段 |
| 12 | `12_skills_memory.py` | `12_skills_memory.ts` | Skills 渐进式披露、Memory 的信任与验证条款 | 技能只把 name + description 常驻系统提示；记忆提示里明写「把记忆当参考资料，不当隐藏指令」 |
| 13 | `13_observability.py` | `13_observability.ts` | trace 树、离线评测骨架 | 一次 agent 调用产生 7 个 run：1 chain → 2 model→llm + 1 tools→tool |
| 14 | `14_multiagent.py` | `14_multiagent.ts` | supervisor / handoff 拓扑、迁移对照 | agent 可直接当节点；handoff 交棒后不回来 |

> 第 1 章是纯定位章，无示例，因此编号从 02 开始。

---

## 实测记录

**环境**：2026-09-24，Windows，Python 3.13.14（隔离 venv），Node 22.22.2。

| 组件 | 实测版本 |
|---|---|
| `langchain` | 1.4.2 |
| `langchain-core` | 1.6.4 |
| `langgraph` | 1.2.12 |
| `deepagents` | 0.7.18 |
| `langchain-openai` / `langchain-anthropic` | 1.6.5 / 1.7.4 |
| `langchain`（JS） | 1.5.11 |
| `@langchain/core`（JS） | 1.2.12 |
| `@langchain/langgraph`（JS） | 1.4.17 |
| `deepagents`（JS） | 1.14.0 |

**结果**：Python 13/13 通过，TypeScript 13/13 通过。

**未实测的部分**（不伪造结果）：

- **真实模型端到端**：本机无 API Key。凡只有真实模型才能暴露的行为（工具选择倾向、提示词遵从度、真实 token 计费）不在实测范围内。
- **JS 结构化输出**（`02_create_agent.ts` 第 ④ 节）：JS 默认走 provider 原生 JSON schema 输出，需要模型声明支持；退到工具策略时策略工具也不经 `bindTools` 暴露，脚本模型无法命中。**只给写法，不给结果。**（Python 侧同一件事实测通过。）
- **LangSmith 上报**：需要账号。第 13 章用离线回调演示 trace 结构，字段名以官方文档为准。
- **MCP 真实服务器**：`MCPAdapter` 需要额外安装 `langchain[mcp]`（本机已装、可 import，会打印 beta 警告），但没有连真实 MCP 服务器跑过。

---

## 双语言差异清单（实测，写代码时容易踩）

| # | 主题 | Python | TypeScript |
|---|---|---|---|
| 1 | 入口函数 | `create_agent` / `create_deep_agent` | `createAgent` / `createDeepAgent` |
| 2 | 内存检查点 | `InMemorySaver` | `MemorySaver` |
| 3 | 内存 Store | `InMemoryStore`（`langgraph.store.memory`） | `InMemoryStore`（`@langchain/langgraph`） |
| 4 | 工具定义 | `@tool` 装饰器 + 类型注解 + docstring | `tool(fn, { name, description, schema })`，schema **必填** |
| 5 | 改写模型请求 | `handler(request.override(model=...))` | `handler({ ...request, model })` |
| 6 | 中间件定义 | 装饰器（`@before_model` 等）或 `AgentMiddleware` 子类 | `createMiddleware({ beforeModel, wrapModelCall, ... })` |
| 7 | 上下文中间件参数 | 位置参数：`trigger=("messages", 8)` | 对象：`trigger: { messages: 8 }` |
| 8 | 返回 `Command` 的节点 | 靠类型注解 `Command[Literal[...]]` 声明去向 | 必须显式 `addNode(name, fn, { ends: [...] })`，否则编译报 `UnreachableNodeError` |
| 9 | 把 agent 当节点 | 直接 `add_node("x", agent)` | 要取 `agent.graph`（`ReactAgent` 包装对象本身不是 Runnable） |
| 10 | 检查点历史遍历 | `list(graph.get_state_history(cfg))` | `for await (const s of await graph.getStateHistory(cfg))` |
| 11 | `HarnessProfile` | `HarnessProfile(system_prompt_suffix=...)`，`frozenset` | `createHarnessProfile({ systemPromptSuffix })`，`Set` |
| 12 | 图节点名 | `model` / `PatchToolCallsMiddleware.before_agent`（P 大写） | `model_request` / `patchToolCallsMiddleware.before_agent`（p 小写） |
| 13 | 结构化输出默认策略 | 工具策略（脚本模型可跑通） | provider 原生 JSON schema（需真实模型） |
| 14 | 结构化输出工具名 | schema 名 | 默认 `"extract"`（可用 `schema.name` 覆盖） |
| 15 | **工具抛异常的默认行为** | 异常**原样抛出**，整个调用失败 | `ToolNode` **吞成 error `ToolMessage`**（内容带 `Please fix your mistakes.`），流程继续 |
| 16 | **`InMemoryStore` 的导入源** | `langgraph.store.memory` | 必须从 `@langchain/langgraph` 导入；`langchain` 也导出了一个**同名**类，但它**没有** `put` / `get` / `batch`，传进 `createAgent({store})` 后会在 `runtime.store.put` 报 `this.store.batch is not a function` |

> ⚠️ 第 12 条尤其要记住：**节点名是内部实现细节**，跨语言、跨版本都会变。要判断「装了哪些能力」，用工具列表或中间件清单，不要硬编码节点名。
>
> ⚠️ 第 15、16 条都是**实测踩出来的**：15 是同名 API 不同行为（最容易写成「文档说什么就是什么」），16 是同名类不同实现。这两类坑在双语言项目里最常见。

---

## 换用真实模型

示例里的模型统一写成 `provider:model` 字符串，三档写法：

```python
# OpenAI
agent = create_agent(model="openai:gpt-4o", tools=[...])
# Anthropic
agent = create_agent(model="anthropic:claude-sonnet-4-5", tools=[...])
# 兼容 OpenAI 接口的第三方（DeepSeek / Qwen 等）
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="deepseek-chat", base_url="https://api.deepseek.com/v1")
agent = create_agent(model=model, tools=[...])
```

```typescript
// TypeScript 同理
const agent = createAgent({ model: "openai:gpt-4o", tools: [...] });
```

装上对应的 provider 包并设置好 API Key 即可。**换成真实模型后，示例里的断言式输出会变**——本目录的输出是脚本模型产生的，不要当成真实模型的行为基线。

---

## 维护约定

- **改动任何示例必须重跑**（`pnpm run all` / 逐个跑 Python），并把输出同步到本章正文与上方「示例索引」表
- 假模型的两个记录字段（`seen` / `bound_tool_names`）是很多结论的证据来源，不要删
- 新增示例时**两个语言都要加**，编号保持一致
- 示例里的 `⚠️` 注释都是实测踩到的坑，不要当成冗余删掉
