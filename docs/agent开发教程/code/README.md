# 示例代码（code）

本目录是 `docs/agent开发教程/` 的配套示例，**Python 与 TypeScript 一一对应**。

**全部示例都已在本机实跑通过**（见下方「实测记录」）。示例用**脚本化的假模型**替代真实 LLM，因此**跑这些示例本身不需要 API Key、不产生网络请求**，结果确定可复现。

凡只有真实模型才能暴露的行为，已另用智谱 OpenAI 兼容端点补测完毕（2026-10-16），结论见「真实模型实测」一节；原始输出与核验脚本存档在 `../_实测输出核验/`。

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
python 02_models.py
```

### TypeScript

```bash
cd code/typescript
pnpm install
pnpm run 02_models        # 单个
pnpm run all                    # 全部（按顺序）
pnpm run typecheck              # 类型检查
```

---

## 示例索引

| 章 | Python | TypeScript | 演示什么 | 关键结论（实测） |
|---|---|---|---|---|
| 2 | `02_models.py` | `02_models.ts` | 三种入参归一化（字符串 1 条；两种列表 2 条）、`AIMessage` 结构、stream / batch | 假模型 `stream` 只吐 1 个 chunk；真实模型实测吐 **194 个 chunk**（见「真实模型实测」A） |
| 3 | `03_messages_prompts.py` | `03_messages_prompts.ts` | 四种消息、历史裁剪、模板的三种调用方式 | `format()` 返回带标签的 str、`format_messages()` 返回消息列表 |
| 4 | `04_structured_output.py` | `04_structured_output.ts` | 四种 schema 模式、校验失败、工具策略自动重试 | Python 侧只有 Pydantic 会抛 `ValidationError`；JS 基类不校验。**基类两语言都把 `method` 丢掉**，只有 provider 子类才真正分叉（已实测，见 B） |
| 5 | `05_create_agent.py` | `05_create_agent.ts` | Agent Loop、状态只追加、两类作用域、结构化输出 | 消息序列 Human → AI(tool_call) → ToolMessage → AI(final)；第 2 轮历史 4 条而非 2 条 |
| 6 | `06_middleware.py` | `06_middleware.ts` | 六个钩子的真实触发顺序、`wrap_*` 改写请求 | 顺序：`before_agent → before_model → wrap_model_call → after_model → wrap_tool_call → before_model → wrap_model_call → after_model → after_agent` |
| 7 | `07_tools.py` | `07_tools.ts` | 工具 schema、`ToolRuntime` 注入、返回 `Command`、异常处理 | 返回 `Command` 必须自带匹配 `tool_call_id` 的 `ToolMessage`；v1 的 agent 路线不再推荐 `ToolException`（API 仍在包里） |
| 8 | `08_rag.py` | `08_rag.ts` | Loader / Splitter / 假嵌入（含手写二维玩具 ③-0）/ 内存向量库 / 检索器接成工具 | 假嵌入只验链路不验语义；TS 的 `JSONLoader` 收 JSON Pointer 而非 jq |
| 9 | `09_context.py` | `09_context.ts` | 摘要压缩 vs 工具输出卸载 | **两者机制不同**：摘要写回状态（4→24 被压到 8），卸载不回写状态（状态 4→24 但模型收到的 token 稳定在 253→588） |
| 10 | `10_observability.py` | `10_observability.ts` | trace 树、离线评测骨架 | **Python 侧**一次 agent 调用产生 7 个 run（1 chain → 2 model→llm + 1 tools→tool）；**TS 侧是 10 个 run、chain 一律无名**。单边结论，别当双语言一致 |
| 11 | `11_state_graph.py` | `11_state_graph.ts` | Reducer、条件边、`Send`、`Overwrite` | 输入里出现的字段按各自 reducer 合并，没出现的保留检查点值；`invoke(None)` 不注入新输入（已完成的线程上为空操作）、`invoke({})` 才是续跑 |
| 12 | `12_persistence.py` | `12_persistence.ts` | 检查点、时间旅行（快照序号示意 + 三节点链重放两步）、Store 跨线程 | `updateState` 新建分支不改原线程；三节点链 fork 后只重走 `double→tag` 两步；`store.search(('alice',))` 是**前缀**匹配，命中 3 条 |
| 13 | `13_hitl_stream.py` | `13_hitl_stream.ts` | `interrupt`/`resume`、`stream_mode`、子图流式 | 恢复时**整个节点从头重跑**（副作用日志出现两次）；agent 当子图时不加 `subgraphs` 就收不到内部消息 |
| 14 | `14_deep_agent.py` | `14_deep_agent.ts` | 默认工具集、`HarnessProfile`、中间件栈 | **模型只被绑定 8 个**两侧一致；「工具节点注册 9 个、差集 `execute`」**只有 Python 测得**（TS 输出自己写明「Python 侧实测」）。`write_todos` 默认不开。Python 侧另演示 `HarnessProfile` 按 provider 注册后自动匹配（裁掉 `edit_file` 后绑定列表里消失） |
| 15 | `15_filesystem.py` | `15_filesystem.ts` | 文件工具、权限、后端谱系 | `StateBackend` 把文件存在**图状态**里（`state.files`）；权限默认 **allow**，按声明顺序**首次匹配即生效** |
| 16 | `16_delegation.py` | `16_delegation.ts` | `write_todos`、子代理、`task`、上下文防火墙实证 | `write_todos` 是**全量覆盖**语义；`SubAgent` 实测 11 个字段；子代理 2 轮（含 3000 字工具资料），主代理只收 30 字符最终报告 |
| 17 | `17_skills_memory.py` | `17_skills_memory.ts` | Skills 渐进式披露、Memory 的信任与验证条款 | 技能只把 name + description 常驻系统提示；记忆提示里明写「把记忆当参考资料，不当隐藏指令」 |
| 18 | `18_multiagent.py` | `18_multiagent.ts` | supervisor / handoff 拓扑、迁移对照 | agent 可直接当节点；supervisor 带 db/mail→supervisor **回边**（决策序列 `['db','end']`：派出去→收回来→结束）；handoff 交棒后不回来 |

> 第 1 章是纯定位章，无示例，因此编号从 02 开始。`18_multiagent` 同时服务第 18 章（多智能体拓扑）与第 19 章（迁移映射与部署），无单独的 19 号示例。

---

## 实测记录

**环境**：2026-09-24 首轮为 Windows + Python 3.13.14 + Node 22.22.2。**2026-10-16 第六轮全量重跑**：Python 3.14.2（隔离 venv）+ Node 24.11.0，17 + 17 全部通过（08/12/16/18 四个示例有改动，其余沿用原逻辑；`langchain-core` 为传递依赖装到 1.6.11，正文结论绑定的 `langchain` / `langgraph` / `deepagents` 三个主包与锁定版本一致）。

**2026-10-16 第七轮复核**：同环境重跑，Python 17/17、TypeScript 17/17 仍全部 `exit=0`；34 份原始 stdout 存档在 `../_实测输出核验/`。本轮同时首次接入真实模型补测原先的「未实测」项。

| 组件 | 实测版本 |
|---|---|
| `langchain` | 1.4.2 |
| `langchain-core` | 1.6.11（1.6.4 是 2026-09-24 那轮，正文多处锚点未同步） |
| `langgraph` | 1.2.12 |
| `deepagents` | 0.7.18 |
| `langchain-openai` / `langchain-anthropic` | 1.7.2 / 1.7.6（1.6.5 / 1.7.4 是 2026-09-24 那轮） |
| `langchain`（JS） | 1.5.11 |
| `@langchain/core`（JS） | 1.2.12 |
| `@langchain/langgraph`（JS） | 1.4.17 |
| `deepagents`（JS） | 1.14.0 |

**结果**：Python 17/17 通过，TypeScript 17/17 通过。

> 上一段与本行曾互相矛盾（这里写 13/13、上面写 17+17）——13 是只有 13 个示例那轮的旧文案，已订正。

## 真实模型实测（2026-10-16 补测）

原先标「未实测」的条目，已用**智谱 OpenAI 兼容端点**（`glm-4.5-air` / `glm-4-plus`，经
`langchain_openai.ChatOpenAI` 与 `@langchain/openai` 的 `ChatOpenAI`）实测。
抓包方式：Python 侧挂 httpx event hook，JS 侧架本地反代——**看的是真正上线的 JSON 请求体**，
不是 `bind_tools` 的入参。证据文件见 `../_实测输出核验/真实模型/`。

| 编号 | 结论 | 证据 |
|---|---|---|
| A | 真实模型 `stream` 吐 **194 个 chunk**（假模型 1 个）；`usage_metadata` 只出现在**倒数第二个** chunk 上，不要每个 chunk 都读 | `01_verify_untested_claims.txt` |
| B | **provider 子类上 `method` 才真正生效**：`json_schema` 发 `response_format={type:json_schema, strict:true}` 且**不带 `tools`**；`function_calling` 发 `tools + tool_choice` 且不带 `response_format`。Python / JS 双侧一致 | `04_wire_capture.txt`、`05_js_provider_subclass.txt` |
| B′ | **基类确实把 `method` 丢掉**：假模型上 `None` / `function_calling` / `json_schema` 三档的 `bind_tools` 额外参数完全相同，均无 `response_format`——原「三条路径都走 bind_tools」的说法成立 | `04_wire_capture.txt` 对照组 |
| C | `usage_metadata` 与 `response_metadata.token_usage` 字段齐全（`input_tokens` / `output_tokens` / `cache_read` / `cached_tokens`），第 10 章的 token 与成本指标**不再需要「以官方文档为准」** | `01_verify_untested_claims.txt` |
| D | 缓存命中率可实测：同一长前缀连发 3 次，`cached_tokens` = **4 → 780 → 780**（input 恒 793） | 同上 |
| E | 换成真实模型后，`create_agent` 的**消息序列结构不变**（仍 Human → AI(tool_call) → ToolMessage → AI(final) 4 条），变的是 content 文本——真实模型会先说一句「我来帮您查询」再调工具 | 同上 |

### 真实模型新暴露的三条坑（原文档未覆盖）

1. **provider 子类的「缺省 `method`」就是 `json_schema`，不是工具策略。**
   `ChatOpenAI().with_structured_output(Person)` 不传 `method` 时，实际发的是
   `response_format: json_schema strict:true`、**不带 `tools`**。差异清单 #13 原先写
   「默认策略 = 工具策略」只对**假模型基类**成立；照抄到真实 provider 上会直接踩坑。

2. **第三方 OpenAI 兼容端点会无视 `strict` JSON schema。**
   `glm-4-plus` 收到 `json_schema strict:true` 后照样返回散文（`"好的，从"张三是一名…"`），
   客户端侧抛 `ValidationError` / `SyntaxError`；`json_mode` 下模型还把字段名
   `occupation` 自作主张改成了 `profession`。**`strict` 是请求，不是保证。**

3. **`include_raw=True` 兜不住 provider 层的解析失败。**
   走 `response_format` 路径时，失败发生在 OpenAI SDK 的 `raw_response.parse()` 里，
   **早于** LangChain 的解析步骤，`include_raw=True` 照样抛异常。只有 `function_calling`
   路径能被它兜住——而兜住的返回值是 `{parsed: None, parsing_error: None, raw: …}`，
   **`parsing_error` 也是 `None`**，等于把错误彻底吞了。批量抽取时这比抛错更危险。

另：`function_calling` 在 `glm-4-plus` 上出现过**静默返回 `None`**（模型没发 tool_call，
解析器不报错）——正是第 4 章「不报错、不告警，只是 None」在真实模型上的复现。

## 仍未实测的部分（不伪造结果）

- **工具选择倾向、提示词遵从度、摘要质量**：本轮只测了机制与协议层字段，没做质量评测；
  单一供应商（智谱）的结论不能外推到 OpenAI / Anthropic 原生端点。
- **LangSmith 上报**：需要账号。第 10 章用离线回调演示 trace 结构，字段名以官方文档为准。
- **MCP 真实服务器**：`MCPAdapter` 需要额外安装 `langchain[mcp]`，**本机未安装**
  （venv 无 `mcp` / `fastmcp`，`import langchain.mcp` 抛 `ModuleNotFoundError`；
  `requirements.txt` 里该行是注释状态），也没连过真实 MCP 服务器。
- **`04_structured_output.ts` 第 ② 节**：JS **基类**的 `withStructuredOutput` 只支持
  function calling（源码写死：传 `method: "jsonMode"` 直接抛错），默认工具名 `extract`，
  `jsonSchema` 与 `functionCalling` 行为一致——这条**限定在基类**，仍然成立。
  provider 子类的分叉见上表 B。agent 侧 `responseFormat` 传裸 schema 时默认走工具策略
  （源码 `ToolStrategy.fromSchema`，工具名取 schema 的 title），假模型可跑通，见
  `05_create_agent.ts` 第 ④ 节。

## 已知未通过项

`pnpm run typecheck`（即 `tsc --noEmit`）**不通过**：`exit=1`，44 个 `error TS`，
分布在 `11_state_graph`(15) / `12_persistence`(11) / `13_hitl_stream`(11) /
`14_deep_agent`(1) / `15_filesystem`(1) / `16_delegation`(2) / `18_multiagent`(3)；
错误码为 TS2345×18、TS2769×13、TS2322×13。完整清单见 `../_实测输出核验/typescript/_typecheck.txt`。

**示例能跑是因为 `tsx` 不做类型检查**——「17/17 通过」指退出码，不蕴含类型干净。
2026-10-20 修复 `07_tools.ts` 的 `InMemoryStore` 导入（差异清单 #16）后，错误数从 45 降到 44。
这些报错**不影响运行时结论**，但别把 `typecheck` 当成已通过。

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
| 8 | 返回 `Command` 的节点 | 靠类型注解 `Command[Literal[...]]` 声明去向 | 建议显式 `addNode(name, fn, { ends: [...] })`。「不写就编译报 `UnreachableNodeError`」是**读源码所得**，本机 `tsc` 的 44 条报错里**没有一条**是该错误名 |
| 9 | 把 agent 当节点 | 直接 `add_node("x", agent)` | 要取 `agent.graph`（`ReactAgent` 包装对象本身不是 Runnable） |
| 10 | 检查点历史遍历 | `list(graph.get_state_history(cfg))` | `for await (const s of await graph.getStateHistory(cfg))` |
| 11 | `HarnessProfile` | `HarnessProfile(system_prompt_suffix=...)`，`frozenset` | `createHarnessProfile({ systemPromptSuffix })`，`Set` |
| 12 | 图节点名 | `model` / `PatchToolCallsMiddleware.before_agent`（P 大写）；`SkillsMiddleware.before_agent` | `model_request` / `patchToolCallsMiddleware.before_agent`（p 小写）；`SkillsMiddleware.before_model`；另有 Python 侧不出现的 `FilesystemMiddleware.before_agent` |
| 13 | 结构化输出默认策略 | **假模型基类**：工具策略，三档 `method` 被丢弃（已实测）；**provider 子类**：缺省即 `response_format: json_schema`，**不走 tools**（已实测） | 与 Python 同构：基类走工具调用，`ChatOpenAI` 缺省即 `jsonSchema`（已实测） |
| 14 | 结构化输出工具名 | schema 名 | 默认 `"extract"`（可用 `schema.name` 覆盖） |
| 15 | **工具抛异常** | `07_tools` 两侧**都挂了捕获中间件**，实测行为一致（都转 error `ToolMessage` 并继续）。「Python 默认原样抛出」是**源码核对 / 官方文档**口径，本机**未做无中间件对照实验** | 同左。「`ToolNode` 默认吞成 error `ToolMessage`（带 `Please fix your mistakes.`）」亦为源码核对，非本轮实测产物 |
| 16 | **`InMemoryStore` 的导入源** | `langgraph.store.memory` | 必须从 `@langchain/langgraph` 导入；`langchain` 也导出了一个**同名**类，但它**没有** `put` / `get` / `batch`，传进 `createAgent({store})` 后会在 `runtime.store.put` 报 `this.store.batch is not a function`。示例已改为正确导入并实测回读成功 |
| 17 | withStructuredOutput 对假模型的要求 | 直接可用 | 解析器要求 `AIMessageChunk`，公共假模型返回 `AIMessage`——`04_structured_output.ts` 里本地派生 `ChunkScriptedChatModel` 子类（只改返回类型一处；正文 ch04 已改为一句话引用，完整定义在本文件） |
| 18 | trace 的 run 数 | 一次 agent 调用 **7 个 run**，根节点名由 `run_name` 决定 | 同样调用产生 **10 个 run**，且 chain 节点**一律无名**（`runName` 未透传）。第 10 章的「7 个 run」是 Python 单边 |

> ⚠️ 第 12 条尤其要记住：**节点名是内部实现细节**，**跨语言会变（已实测）**；「跨版本也会变」是合理推断，本机只跑过 `langgraph` 1.2.12 / `@langchain/langgraph` 1.4.17 一个版本，**未实测**。要判断「装了哪些能力」，用工具列表或中间件清单，不要硬编码节点名。
>
> ⚠️ 第 16 条是**实测踩出来的**（`T07` 里那句 `this.store.batch is not a function` 就是它）：同名类不同实现，双语言项目里最常见。
>
> 第 15 条要分开看：**中间件生效后的行为**是实测的（两侧一致），但**默认行为的差异**只是源码核对——别拿它当「跑出来的结论」。

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

装上对应的 provider 包并设置好 API Key 即可。兼容 OpenAI 接口的第三方（实测过的智谱）：

```python
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="glm-4.5-air",
                   base_url="https://open.bigmodel.cn/api/paas/v4")
```

```typescript
import { ChatOpenAI } from "@langchain/openai";
const model = new ChatOpenAI({
  model: "glm-4-plus",
  apiKey: process.env.ZHIPU_API_KEY,
  configuration: { baseURL: "https://open.bigmodel.cn/api/paas/v4" },
});
```

> ⚠️ JS 侧两个字段名极易写错（实测）：`apiKey` 是**顶层**字段，`openAIApiKey` 在
> `@langchain/openai` 1.6.2 上已不被读取；base URL 要走 `configuration.baseURL`
> （**大写 L**），写成 `baseUrl` 会被静默忽略、退回 `api.openai.com`。

**换成真实模型后，示例里的断言式输出会变**——本目录的输出是脚本模型产生的，不要当成真实模型的行为基线。但要说清「变」的边界（实测，见上表 E）：**消息序列、钩子顺序、状态与检查点结构这些框架机制不变**，变的是模型吐出来的文本、以及是否真的发 tool_call。

---

## 维护约定

- **改动任何示例必须重跑**（`pnpm run all` / 逐个跑 Python），并把输出同步到本章正文与上方「示例索引」表
- 假模型的两个记录字段（`seen` / `bound_tool_names`）是很多结论的证据来源，不要删
- 新增示例时**两个语言都要加**，编号保持一致
- 示例里的 `⚠️` 注释都是实测踩到的坑，不要当成冗余删掉
