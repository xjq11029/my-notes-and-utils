# 第 14 章 Deep Agents 全景：预装 harness 与 HarnessProfile

## 一、这一章要解决的问题

第 5–13 章都在「自己拼」：循环要配、工具要写、上下文要管，多智能体协作也要到第 18 章才自己搭。拼着拼着你就会想：读文件、派下属、记笔记这些几乎每个项目都要用的能力，能不能别再从零拼一遍？**Deep Agents** 走的是另一条路——它在 `create_agent` 之上**预装**一整套常用能力：虚拟文件系统、子代理委派、技能与记忆、待办规划。

打个比方：`create_agent` 是毛坯房，水电格局都在，家具自己搬；`create_deep_agent` 是精装房，拎包即住（类比）。但精装房有个副作用——**你不想要的那部分，也已经在那了**；本章后半程讲的裁剪，拆的正是这个问题。

预装带来三个必须回答的问题：

1. 默认到底给了什么？（工具、中间件、图节点）
2. 哪些是「注册了」但**模型根本看不见**的？
3. 预装的东西我不想要，怎么裁？——这是 `HarnessProfile` 要解决的。

一句话主线：**本章回答「Deep Agents 预装了什么、模型看得见什么、不想要的怎么裁」**——先把全景建起来，再学声明式裁剪；四类能力各自的细节，交给后面三章。

想先看它干活？跳到 3.1：五段代码就能打印出「默认给了哪些工具、模型实际看得见几个」——本章最重要的结论（Python 侧注册 9 个、模型可见 8 个）就是这么探出来的，不需要 API Key。看过实测再回来读 2.1 的参数表，你会更清楚每一行的默认行为分别在后面哪节展开。

本章只讲**全景与裁剪**；文件系统与权限的细节在第 15 章，规划与委派在第 16 章，技能与记忆在第 17 章。

> 版本锚点：本章结论在 `deepagents` **0.7.18**（Python）/ **1.14.0**（JS）、`langchain` **1.4.2** 上实测；示例源码见 `code/python/14_deep_agent.py` 与 `code/typescript/14_deep_agent.ts`。

## 二、机制与原理

### 2.1 create_deep_agent 的完整参数

先给这一节定个位：**它是本章的地图，不是要背的册子**。后面 2.2–2.5 每一节，本质上都是在讲这张表里某几行的默认行为——默认工具集是 `middleware` 一行的展开，声明式裁剪是 `profile` 一行的展开。所以正确的读法是带着问题查行，而不是从头记到尾。

先看结论：**这张表不需要一次记完**。跑完 3.1 的探测脚本，你就知道默认给了什么；之后每次只查「我想改的那一行」——大多数项目真正用到的只有 `model` / `tools` / `system_prompt` / `subagents` 四行。

下面这张表回答「我能配什么」。参数按**实测签名**给全——官方文档正文只列了其中一部分。

| 参数（Python） | TypeScript | 作用 |
|---|---|---|
| `model` | `model` | 模型实例或 `provider:model` 字符串 |
| `tools` | `tools` | **追加**自定义工具（不会移除内置工具） |
| `system_prompt` | `systemPrompt` | 自定义系统提示 |
| `middleware` | `middleware` | **追加**中间件（如 `TodoListMiddleware()`） |
| `subagents` | `subagents` | 子代理清单，支撑 `task` 工具 |
| `skills` | `skills` | 技能源路径列表 |
| `memory` | `memory` | 记忆文件路径列表（`AGENTS.md`） |
| `permissions` | `permissions` | 文件系统权限规则 |
| `backend` | `backend` | 文件与执行的落点（默认 `StateBackend`） |
| `interrupt_on` | `interruptOn` | 哪些工具调用前要人工审批 |
| `response_format` | `responseFormat` | 结构化输出 |
| `state_schema` | `stateSchema` | 自定义状态字段 |
| `context_schema` | `contextSchema` | 单次运行的上下文（`context`） |
| `checkpointer` | `checkpointer` | 检查点保存器（第 12 章） |
| `store` | `store` | 跨线程存储（第 12 章） |
| `debug` | 参数表中无此字段 | 调试日志 |
| `name` | `name` | agent 名（当子图时有用） |
| `cache` | 参数表中无此字段 | 节点级缓存 |

表中两处「参数表中无此字段」的出处、以及 JS 侧多出的字段，见本节末参考块：

> **参考块｜参数表的两条来源说明**
> 两条来源说明：Python 列的 `debug` / `cache` 来自本机实测签名；JS 侧的 `CreateDeepAgentParams`（`deepagents` 1.14.0 类型定义）里确实**没有**这两个字段，但多一个 `streamTransformers`。

### 2.2 默认工具集：注册 9 个，模型只看得见 8 个（Python 单边）

2.1 的表里，`middleware` 一行摊开了预装能力；能力里最硬的是工具。这一节回答三个问题里的第二个——**默认到底给了哪些工具、模型看得见几个**，结论会落在一个反直觉的区分上。

先建立预期：**「注册了工具」不等于「模型看得见」**，必须分成两个口径看。打个比方：注册在工具节点，像通讯录里存了号码；绑定给模型，才像手机开通了呼叫权限——名单上有名却打不通，对 agent 的实际能力毫无意义（类比）。

下表回答的问题是：**默认工具集里，哪些注册在工具节点、哪些真的绑定给了模型？**

| 工具 | 用途 | 注册在工具节点 | 绑定给模型 |
|---|---|---|---|
| `ls` | 列目录 | ✅ | ✅ |
| `read_file` | 读文件 | ✅ | ✅ |
| `write_file` | 写文件 | ✅ | ✅ |
| `edit_file` | 改文件 | ✅ | ✅ |
| `delete` | 删文件 | ✅ | ✅ |
| `glob` | 按文件名模式找 | ✅ | ✅ |
| `grep` | 按内容搜 | ✅ | ✅ |
| `execute` | 执行命令 | ✅ | ❌ |
| `task` | 派子代理 | ✅ | ✅ |

**合计：工具节点里注册 9 个，绑定给模型的只有 8 个。** 差的正是 `execute`——默认后端是 `StateBackend`，它把文件存在图状态里，**不提供执行能力**，所以 `execute` 根本不向模型暴露。换句话说，想看 agent 到底能干什么，要看**模型被绑定了什么**，而不是看工具节点里挂了什么。

![图 26　Deep Agents 预装的中间件栈与工具集：注册 9 个、模型可见 8 个](assets/26_deep_agent_stack.png)

*图 26　Deep Agents 预装的中间件栈与工具集：注册 9 个、模型可见 8 个*

**`write_todos` 默认不开。** 它既不在这 9 个里，也不在那 8 个里——想用规划能力，必须显式加中间件：

- Python：`from langchain.agents.middleware import TodoListMiddleware`，然后 `create_deep_agent(model=..., middleware=[TodoListMiddleware()])`
- TypeScript：`import { todoListMiddleware } from "langchain"`，然后 `middleware: [todoListMiddleware()]`

加上之后 `write_todos` 才会被绑定给模型，并且**状态里会多出一个 `todos` 键**（实测）。规划能力的完整语义在第 16 章，这里只要记住一句：它默认不在。

> ⚠️ **与官方文档的差异**：概览页把 `write_todos` 描述为「可选能力，v0.7 起需主动开启」，但没有给出默认工具清单。实测（`deepagents` 0.7.18）确认默认**不绑定** `write_todos`，与文档口径一致；但「9 注册 / 8 可见」这个区分文档里没有，是 **Python 侧**本机实测补上的（JS 输出只验证了绑定侧的 8 个）。

### 2.3 四类内置能力

工具清单有了，还要知道每件工具背后是谁在供着。这一节把预装能力归成四类，给出能力域与中间件的对应关系——后面三章，就是把这四类逐一拆开。

这张表回答「预装的这些东西，各自属于哪一类能力」。中间件在 JS 侧是工厂函数（`createFilesystemMiddleware` 等），名字对应。

| 能力域 | 提供什么 | 靠哪个中间件 |
|---|---|---|
| **执行环境** | 虚拟文件系统的 7 个文件工具；命令执行（取决于后端） | `FilesystemMiddleware` + `backend` |
| **上下文管理** | 大工具输出卸载到文件系统、摘要压缩、修补不完整的工具调用 | `FilesystemMiddleware` / `SummarizationMiddleware` / `PatchToolCallsMiddleware` |
| **委派** | `task` 工具 + 独立上下文的子代理 | `SubAgentMiddleware` |
| **引导** | 系统提示、技能（Skills）、记忆（Memory）、待办（`write_todos`） | `SkillsMiddleware` / `MemoryMiddleware` / `TodoListMiddleware` |

四类里，执行环境决定 agent「能碰什么」，上下文管理决定它「忘不忘事」——前者是第 15 章的主题，后两类分别由第 16、17 章展开。

### 2.4 预装中间件栈与图节点名

四类能力各自挂在中间件上，中间件最终都落在编译后的图里。这一节回答一个排查时最常犯的错误：想知道 agent 装了哪些能力，该看哪里——以及为什么答案不是节点名。

打开编译后的图，能看到第 6 章的中间件各自插进来的钩子节点——**Deep Agents 没有发明新机制，它只是把一整套预置中间件替你装好**。为什么要知道节点名？因为排查「某个能力怎么没生效」时，节点清单是最快的定位入口。但**节点名是内部实现细节，跨语言会变（实测）**；「跨版本也会变」是合理推断，本机只跑过一个版本、**未实测**。下表回答的问题是：**同一个钩子，两个语言各挂在什么节点名上？**逐语言对照（示例实测）：

| 节点 | Python（`14_deep_agent.py`） | TypeScript（`14_deep_agent.ts`） |
|---|---|---|
| 模型节点 | `model` | `model_request` |
| 补丁钩子 | `PatchToolCallsMiddleware.before_agent`（**P 大写**） | `patchToolCallsMiddleware.before_agent`（**p 小写**） |
| 文件系统钩子 | **不出现** | `FilesystemMiddleware.before_agent` |
| 技能钩子 | `SkillsMiddleware.before_agent` | `SkillsMiddleware.`**`before_model`** |
| 记忆 / 审批 | `MemoryMiddleware.before_agent` / `HumanInTheLoopMiddleware.after_model` | 同名 |

这张表读起来平平无奇，但它藏着两处曾经标错又订正过的地方——正是「别硬编码节点名」最直接的证据，订正记录见本节末参考块：

> **参考块｜节点名的一处历史订正**
> ⚠️ 原先这里把 `FilesystemMiddleware.before_agent` 归给了 Python、「P 大写」也错标在它身上——**它只在 JS 侧出现**，「P 大写」指的是 `PatchToolCalls`。另外 JS 的 skills 节点挂在 **`before_model`** 而不是 `before_agent`。这正是「别硬编码节点名」的活教材。

**结论：要判断「这个 agent 到底装了哪些能力」，看工具列表或中间件清单，不要硬编码节点名**——这是全书特意标红的一条。

### 2.5 HarnessProfile：声明式裁剪，而不是自己拼中间件

三个问题问到最后一个：不想要的怎么裁。2.4 说过，Deep Agents 是「替你装好的一整套」——裁剪这件事有两种写法，这一节看推荐的那种，以及它和手拼的差别在哪。

预装能力的代价是「不想要的也塞进来了」。`HarnessProfile` 让你**声明式地**裁剪，而不是自己把中间件拆开重拼——好处是内置能力升级时，你的 profile 不用跟着改。打个比方：声明式裁剪像下馆子时说「不要香菜」，后厨怎么调整不用你管；自己拆中间件像自己进厨房重做一道菜，菜谱一改你就得重学（类比）。下面两段代码回答的问题是：**自己拆开重拼与声明式裁剪，差别在哪？**两句对照就能看出差别：

```python
# 自己拆开重拼：deepagents 升级、默认栈加了新中间件时，这段不会自动享受到
agent = create_agent(model, tools=[...],
                     middleware=[FilesystemMiddleware(...), TodoListMiddleware()])  # 逐个拼，漏一个就丢一项能力

# HarnessProfile 声明式裁剪：不是 create_deep_agent 的参数，
# 而是按 provider / provider:model 注册，创建对应模型时自动匹配
register_harness_profile("openai", HarnessProfile(excluded_tools=frozenset({"edit_file"})))
agent = create_deep_agent(model="openai:gpt-4o", tools=[...])
```

注意：`create_deep_agent` **没有 `profile=` 参数**；第二段是「注册」而不是「传参」。profile 会按模型自报的 provider（或 `provider:model`）自动匹配，3.2 节用假模型做一次可运行的演示。

官方文档只提到了 `excluded_tools` 与 `excluded_middleware` 两个字段，**本机核对签名一共 7 个**（示例里逐行 print 字段名）。下表回答的问题是：**一个 profile 能声明哪些裁剪？**

| 字段（Python） | TypeScript | 作用 |
|---|---|---|
| `base_system_prompt` | `baseSystemPrompt` | 替换基础系统提示 |
| `system_prompt_suffix` | `systemPromptSuffix` | 追加指令（如「一律用中文」） |
| `tool_description_overrides` | `toolDescriptionOverrides` | 改写某个工具的描述 |
| `excluded_tools` | `excludedTools` | 隐藏工具（Python `frozenset`，JS `Set`） |
| `excluded_middleware` | `excludedMiddleware` | 排除中间件 |
| `extra_middleware` | `extraMiddleware` | 追加中间件 |
| `general_purpose_subagent` | `generalPurposeSubagent` | 配置自动添加的通用子代理 |

两处边界要记住：

- **`excluded_middleware` 排不掉必需项**。`FilesystemMiddleware` 与 `SubAgentMiddleware` 被标为必需（前者撑起全部文件工具与权限，后者撑起 `task` 工具）；把它们写进 profile 时，**构造 profile 就会抛 `ValueError: required scaffolding cannot be excluded`**，不是静默无效。
- **JS 侧的工厂函数叫 `createHarnessProfile`**，字段是 camelCase，且 `excludedTools` / `excludedMiddleware` 在**实例上是 `Set`**——直接 `JSON.stringify` 会得到 `{}`，要用 `Array.from()`。

注册方式两边一致：`register_harness_profile(key, profile)` / `registerHarnessProfile(key, profile)`。key 必须是 **provider 或 `provider:model`**，由模型自动匹配；它不是「调用时按名字取用」的开关。

## 三、代码：Python 与 TypeScript

### 3.1 探测默认工具集：注册 9 个 vs 模型可见 8 个（Python 单边）

机制讲完了，现在把本章最重要的结论跑出来。这一节回答的问题是：**默认工具集的两个口径，怎么用一个假模型探到？**Python 侧从**模型那一侧**取工具名，再和工具节点里挂的做差集。注意 `bindTools` 是**每次模型调用时**才触发的，所以必须先 `invoke` 一次。

最小例子（离线创建并跑一次；在 `code/python/` 下运行）：

```python
from _fake_model import ScriptedChatModel, reply
from deepagents import create_deep_agent
from langchain_core.messages import HumanMessage

agent = create_deep_agent(model=ScriptedChatModel(script=[reply("你好，我是 Deep Agent。")]))
out = agent.invoke({"messages": [HumanMessage("你好")]},
                   config={"configurable": {"thread_id": "demo"}})
print(out["messages"][-1].content)   # 你好，我是 Deep Agent。
```

```python
from _fake_model import ScriptedChatModel, reply
from deepagents import create_deep_agent
from langchain_core.messages import HumanMessage

m0 = ScriptedChatModel(script=[reply("好的")])
agent0 = create_deep_agent(model=m0)
print(m0.last_bound_tool_names())            # [] —— bindTools 还没触发

agent0.invoke({"messages": [HumanMessage("你好")]},
              config={"configurable": {"thread_id": "probe"}})
names = m0.last_bound_tool_names()           # 模型这一侧看到的
print(len(names), names)                     # 8 个：不含 execute、不含 write_todos

node_tools = sorted(agent0.nodes["tools"].bound._tools_by_name.keys())
print(len(node_tools), sorted(set(node_tools) - set(names)))   # 9 个，差集 {'execute'}
# ⚠️ 上面这行读的是图内部的属性名，属于实现细节，换版本可能失效——
#    结论请以「模型被绑定了什么」为准。
```

TypeScript 侧只能从模型这一侧探测（包装对象的内部属性没有稳定路径），方法与 Python 完全一致。

```typescript
import { createDeepAgent } from "deepagents";
import { ScriptedChatModel, reply } from "./_fakeModel";

const m0 = new ScriptedChatModel({ script: [reply("好的")] });
const agent0 = createDeepAgent({ model: m0 as any });
console.log(m0.lastBoundToolNames());        // [] —— bindTools 还没触发

await agent0.invoke({ messages: [{ role: "user", content: "你好" }] },
                    { configurable: { thread_id: "probe" } });
const names = m0.lastBoundToolNames();
console.log(names.length, names);            // 8 个：ls / read_file / write_file / edit_file /
                                             // delete / glob / grep / task
```

> 为什么用假模型来探测：本教程的 `ScriptedChatModel` 会记录 `bindTools` 收到的工具名。这正是「注册 ≠ 可见」这条结论的证据来源。**真实模型下的工具选择倾向需要 API Key，未实测。**

### 3.2 显式开启规划，并注册一个 HarnessProfile

探测完默认值，这一节做两个主动操作：把 `write_todos` 开出来，再注册一个 profile 裁掉 `edit_file`——分别对应 2.2 与 2.5 两节的机制。Python 侧先加 `TodoListMiddleware` 让 `write_todos` 出现，再按模型 provider 注册 profile。

> 为什么裁 `edit_file` 而不是 `execute`：默认 `StateBackend` 下 `execute` 本来就不绑定给模型，拿它做裁剪演示看不到任何变化；`edit_file` 是默认可见工具，裁掉后能从绑定列表里直接验证。

```python
from deepagents import HarnessProfile, create_deep_agent, register_harness_profile
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.messages import HumanMessage
from _fake_model import ScriptedChatModel, reply   # 本教程的假模型

m1 = ScriptedChatModel(script=[reply("好")])       # 3.1 节探测用的同一类模型
planned = create_deep_agent(model=m1, middleware=[TodoListMiddleware()])
out = planned.invoke({"messages": [HumanMessage("帮我做个计划")]})
print("write_todos" in m1.last_bound_tool_names())     # True —— 加了中间件才出现
print(out.get("todos"))                                # 状态里多出 todos 键

profile = HarnessProfile(
    system_prompt_suffix="回答一律用中文。",
    excluded_tools=frozenset({"edit_file"}),            # 裁掉默认可见的工具
    tool_description_overrides={"grep": "在本项目源码里搜索。"},
)
# 假模型 _get_ls_params 报出的 provider 是 scriptedchatmodel；
# 真实项目换成 "openai" 或 "provider:model"
register_harness_profile("scriptedchatmodel", profile)

probe = ScriptedChatModel(script=[reply("好")])
probe_agent = create_deep_agent(model=probe)
probe_agent.invoke({"messages": [HumanMessage("试试")]})
print(probe.last_bound_tool_names())                   # edit_file 不在列表里
```

TypeScript 侧注意三处差异：工厂函数 `createHarnessProfile`、camelCase 字段、`excludedTools` 是 `Set`。

```typescript
import { createDeepAgent, createHarnessProfile, registerHarnessProfile } from "deepagents";
import { todoListMiddleware } from "langchain";

const planned = createDeepAgent({ model: m1 as any, middleware: [todoListMiddleware()] as any });
const out: any = await planned.invoke({ messages: [{ role: "user", content: "帮我做个计划" }] });
console.log(m1.lastBoundToolNames().includes("write_todos"));   // true
console.log(out.todos);                                        // 状态里多出 todos 键

const profile = createHarnessProfile({
  systemPromptSuffix: "回答一律用中文。",               // camelCase
  excludedTools: ["edit_file"],                        // 传数组，实例上是 Set
  toolDescriptionOverrides: { grep: "在本项目源码里搜索。" },
});
registerHarnessProfile("my-provider", profile);
console.log(Array.from(profile.excludedTools));        // ⚠️ 直接 JSON.stringify 会得到 {}
// 本示例的假模型不报告 provider，所以只验证注册 + 回读；
// 真实 ChatOpenAI / ChatAnthropic 会按 provider 自动匹配这个 profile。
```

> 完整可跑版本（含「挂 memory / skills / subagents / interrupt_on 后节点怎么变」的对比）：`code/python/14_deep_agent.py`、`code/typescript/14_deep_agent.ts`。

## 四、常见坑与边界条件

以下八条，前七条约定「怎么用」，最后一条划定本章的实测边界。

1. **「注册了」≠「模型看得见」**。Python 侧实测：默认 9 个注册、8 个可见，差的 `execute` 是因为 `StateBackend` 不提供执行能力；JS 输出只验证了绑定侧的 8 个。判断 agent 能力请看模型侧绑定结果。
2. **`write_todos` 默认不开**，必须显式加 `TodoListMiddleware` / `todoListMiddleware`（实测）。
3. **别硬编码图节点名**。Python 是 `model` / `PatchToolCallsMiddleware.before_agent`，JS 是 `model_request` / `patchToolCallsMiddleware.before_agent`——节点名是内部实现细节（实测）。
4. **包归属别搞错**：`FilesystemMiddleware` / `SubAgentMiddleware` 在 `deepagents` 里，**不在** `langchain.agents.middleware`；`SkillsMiddleware` 也不在 `deepagents` 顶层导出，要从 `deepagents.middleware` 导入（均为实测结论）。
5. **`tools=` 是追加不是替换**。想移除内置文件工具，得走 `HarnessProfile.excluded_tools` 或 `FilesystemMiddleware` 的白名单，不能靠 `tools=` 覆盖。
6. **`excluded_middleware` 不能排除必需项**（`FilesystemMiddleware` / `SubAgentMiddleware`）；写进去会在构造 profile 时抛 `ValueError`。
7. **JS 的 `excludedTools` 是 `Set`**，序列化前先 `Array.from()`；Python 侧是 `frozenset`，两边都不是普通列表。
8. **预装能力的效果需要真实模型才能评估**（子代理产出质量、技能是否被正确加载等）——**本轮未测**：2026-10-16 虽已接入智谱端点，但只测了协议层与框架机制（流式分块、结构化输出载荷、token 字段），没有跑「真实模型 + Deep Agents」的端到端质量评测；本章只验证「装了什么、暴露了什么」。

## 五、关键结论

1. **Deep Agents 没有发明新机制，它只是把一整套预置中间件替你装好**——`create_agent` + 预装中间件栈，文件系统、子代理、技能、记忆、规划开箱即得；第 6 章的钩子体系就是读懂它的钥匙。
2. **判断一个 Deep Agent 到底能干什么，看「模型被绑定了什么」，而不是看工具节点里挂了什么**——Python 侧注册 9 个、模型可见 8 个，差的那个 `execute` 就是因为默认后端不提供执行能力；`write_todos` 同理，默认不开。
3. **裁剪要用声明式，不要拆开重拼**：`HarnessProfile` 按 provider / `provider:model` 注册，创建模型时自动匹配；不是 `create_deep_agent` 的参数。**本机核对签名有 7 个字段**（文档只提 2 个）；`excluded_middleware` 排除必需项会在构造期报错。内置能力升级时你的 profile 不用跟着改，这是它比自己拼中间件强的根本原因。
   > ⚠️ 口径：**那 7 个字段名是 `14_deep_agent.py` 里逐行 print 的字面量**，不是从类上反射出来的；**JS 侧从未打印字段数**，只回读了 `excludedTools` 与 `systemPromptSuffix` 两个。所以「7 个字段」是 Python 单边，`baseSystemPrompt` / `excludedMiddleware` / `extraMiddleware` / `generalPurposeSubagent` 在 JS 输出里零出现。
4. **包归属与节点名都别看文档猜，以实测为准**：`FilesystemMiddleware` / `SubAgentMiddleware` 在 `deepagents` 而不在 `langchain.agents.middleware`；图节点名跨语言不同且随时可变（`model` vs `model_request`），硬编码它不如看工具清单。

> 口径：工具注册 / 绑定数、图节点名、HarnessProfile 字段数为本机核对 / 示例实测（`14_deep_agent.*`）；预装能力的实际效果需真实模型，未实测。

## 本章要点回顾

- **入口**：`create_deep_agent` / `createDeepAgent`，18 个参数按**本机核对签名**给全（读 `inspect.signature` / 类型定义，**不在示例输出里**；JS 侧无 `debug` / `cache`，多 `streamTransformers`）。
- **默认工具集两个口径（Python 单边）**：工具节点注册 **9** 个，模型可见 **8** 个——差的是 `execute`（默认 `StateBackend` 不给执行能力）；JS 只验证了绑定侧的 8 个。
- **规划要自己开**：`TodoListMiddleware()` / `todoListMiddleware()`，加上后状态多出 `todos` 键。
- **四类内置能力**：执行环境（`FilesystemMiddleware`）、上下文管理（卸载 / 摘要 / 修补）、委派（`SubAgentMiddleware` + `task`）、引导（技能 / 记忆 / 待办）。
- **节点名两边不同**：Python `model` / `PatchToolCallsMiddleware.before_agent`；JS `model_request` / `patchToolCallsMiddleware.before_agent`——**别硬编码**。
- **`HarnessProfile` 7 个字段**：`base_system_prompt` / `system_prompt_suffix` / `tool_description_overrides` / `excluded_tools` / `excluded_middleware` / `extra_middleware` / `general_purpose_subagent`。
- **JS 三处差异**：`createHarnessProfile`、camelCase 字段、`excludedTools` 是 `Set`（`JSON.stringify` 得 `{}`，Python 侧是 `frozenset`）。
- **必需中间件不能排除**：写进 `excluded_middleware` 会在构造 profile 时抛 `ValueError`。
- **包归属**：`FilesystemMiddleware` / `SubAgentMiddleware` 在 `deepagents`；`SkillsMiddleware` 要从 `deepagents.middleware` 导入（顶层不导出）。
- **预装能力的效果需真实模型，未实测**；本章验证的是「装了什么、暴露了什么」。
