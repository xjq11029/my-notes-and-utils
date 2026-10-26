# LangGraph核心机制与面试要点

> 定位：把 LangGraph 从「照着例子能跑」推进到「讲得清机制、扛得住追问」，面向 AI Agent 岗位的面试复盘与自测。
> 读法：第一至十章按机制展开，每节先给结论表、再给最小代码；第十一章是 30 道题，时间紧可直接刷题，答不顺再回前文。
> 版本锚点：Python `langgraph` 1.2.12 / `langchain` 1.4.2；JS `@langchain/langgraph` 1.4.17 / `langchain` 1.5.11。LangChain v1 与 LangGraph v1 于 2025-10-22 同步 GA，0.x 时代的教程与本文的 API 对不上。
> 口径：本文是面试导向的机制手册，不追求覆盖全部 API；只保留会被追问、工程上会踩坑的部分。

全文沿用四种口径标记，读到结论时先看它属于哪一类：

| 标记 | 含义 | 怎么对待 |
|---|---|---|
| 实测 | 本机脚本跑过，有 stdout | 可以当事实背 |
| 源码核对 | 读签名 / 常量 / 导出表得出，未构造运行用例 | 结论成立，但别声称「跑过」 |
| 未实测 | 需要浏览器 / 云服务 / 真实嵌入模型 | 只记写法与边界，不当已验证 |
| 架构判断 | 分层与选型建议 | 面试可讲取舍，不宜说成唯一答案 |

---

## 目录

- [一、LangGraph 的定位与边界](#一langgraph-的定位与边界)
- [二、StateGraph：状态、Reducer 与合并语义](#二stategraph状态reducer-与合并语义)
- [三、控制流：节点、边与并行原语](#三控制流节点边与并行原语)
- [四、持久化：checkpointer、store 与时间旅行](#四持久化checkpointerstore-与时间旅行)
- [五、interrupt 与 resume：人在回路](#五interrupt-与-resume人在回路)
- [六、流式：七档 stream_mode 与事件流](#六流式七档-stream_mode-与事件流)
- [七、节点级治理：重试、超时与缓存](#七节点级治理重试超时与缓存)
- [八、多智能体拓扑：supervisor、handoff 与 swarm](#八多智能体拓扑supervisorhandoff-与-swarm)
- [九、部署：langgraph.json 与本地 Agent Server](#九部署langgraphjson-与本地-agent-server)
- [十、选型：什么时候用 LangGraph](#十选型什么时候用-langgraph)
- [十一、30 道高频面试题](#十一30-道高频面试题)
- [十二、避坑指南](#十二避坑指南)
- [十三、本章学习自检](#十三本章学习自检)

---

## 一、LangGraph 的定位与边界

面试最常见的开场是「LangGraph 是什么」。一句话答案：**它是 LangChain 生态里的运行时（runtime）——把「图 + 状态 + 持久化」做成可执行的基础设施**。既不是「更高级的 Chain」，也不只是「多智能体框架」。

### 1.1 三件套里的位置

| 层 | 框架 | 你该来这里找什么 | 代表 API |
|---|---|---|---|
| 构建块 | LangChain v1 | agent 循环、提示词、工具、中间件插槽 | `create_agent`、`@tool`、middleware |
| 运行时 | LangGraph v1 | 图、状态合并、检查点、中断、流式 | `StateGraph`、checkpointer、`interrupt` |
| 成品 harness | Deep Agents | 预装文件系统、子代理、技能、规划 | `create_deep_agent`、`HarnessProfile` |

依赖方向是单向的：**Deep Agents 依赖 `create_agent`，`create_agent` 编译出来的就是一张 LangGraph 图**。所以「用了 LangChain 还需不需要 LangGraph」这个问法本身不成立——你已经在用了，只是没有直接画图。

边界判断落到具体现场：

| 现场问题 | 先去哪一层 | 原因 |
|---|---|---|
| 多轮对话记不住上文 | LangGraph | checkpointer + `thread_id` |
| 工具报错想统一兜底 | LangChain | `wrap_tool_call` 等中间件钩子 |
| 要一个能读写的文件系统 | Deep Agents | 预装 filesystem 中间件 |
| 扣款前要人工审批 | LangGraph | `interrupt` + 检查点 |
| 结构化输出不稳定 | LangChain | `with_structured_output` |
| 想限制模型调用次数 | LangChain + LangGraph | 中间件管模型调用，`recursion_limit` 管超步 |

> 这张表是**心智模型上的分工，不是能力边界**：LangGraph 也带 `ToolNode` 这类预置件，`create_agent` 的签名里也有 `checkpointer`。它回答的是「该去哪一层找答案」。

### 1.2 Graph API 与 Functional API

同一套运行时有两种写法。面试问「为什么不直接写函数」时，答这一节。

| 维度 | Graph API | Functional API |
|---|---|---|
| 形状表达 | 节点 + 边，可编译成图、可视化 | 普通函数调用链 |
| 状态 | 显式 schema + reducer | 函数参数 / 返回值；`@entrypoint` 仍可挂 checkpointer / store |
| 并行 | `Send`、静态扇入 | `@task` 返回 future，可并发后汇总 |
| 中断 / 子图 | 原生支持，暂停点清晰 | 能中断，但复杂控制流要自己拆 |
| 适合 | 多分支、循环、HITL、多智能体 | 单条流水线、批处理、脚本式编排 |
| 代价 | 样板代码多、概念多 | 结构不可视，复杂图表达力弱 |

Graph API 的最小骨架只有四个构件：State、Node、Edge、`compile()`。

```python
from typing import TypedDict
from langgraph.graph import START, END, StateGraph

class State(TypedDict):
    n: int

graph = (StateGraph(State)
         .add_node("inc", lambda s: {"n": s["n"] + 1})
         .add_edge(START, "inc")
         .add_edge("inc", END)
         .compile())

graph.invoke({"n": 1})     # {'n': 2}
```

Functional API 表达同一件事：

```python
from langgraph.func import entrypoint, task

@task
def add_one(x: int) -> int:
    return x + 1

@entrypoint()
def pipeline(x: int) -> int:
    return add_one(x).result()

pipeline.invoke(3)   # 4
```

两条纪律：`@task` 只能在 `@entrypoint` 或图里调用；Python 忘记 `.result()`、JS 忘记 `await`，拿到的是任务对象而不是值（实测）。选型口径：**需要可视化、中断、子图时用 Graph API；逻辑本身就是一条函数链时 Functional 更直接**。

### 1.3 版本差异与导入路径

旧教程最容易把人带沟里的四处：

| 旧写法（0.x / 二手教程） | v1 写法 | 说明 |
|---|---|---|
| `from langgraph.prebuilt import create_react_agent` | `from langchain.agents import create_agent` | agent 构建上移一层，产物仍是图 |
| Python 侧 `MemorySaver` | `InMemorySaver` | JS 侧仍叫 `MemorySaver` |
| `stream_mode` 只有四档 | 七档 | 见第六节 |
| `interrupt_before` 做审批流 | 节点内 `interrupt()` | 静态中断只适合调试 |

导入路径按这张表记，写代码和答笔试都不容易错：

| 要什么 | Python 导入 |
|---|---|
| `StateGraph` / `START` / `END` / `add_messages` | `langgraph.graph` |
| `Command` / `interrupt` / `Send` / `Overwrite` / `RetryPolicy` / `CachePolicy` | `langgraph.types` |
| `InMemorySaver` | `langgraph.checkpoint.memory` |
| `InMemoryStore` | `langgraph.store.memory` |
| `InMemoryCache` | `langgraph.cache.memory` |
| `RemainingSteps` | `langgraph.managed` |
| `entrypoint` / `task` | `langgraph.func` |
| `get_stream_writer` | `langgraph.config` |
| `Runtime` | `langgraph.runtime` |

---

## 二、StateGraph：状态、Reducer 与合并语义

这一节回答三个问题：状态长什么样、多个节点的写入怎么合、同一线程再次 `invoke` 时输入怎么进状态。前两个是「节点之间」的语义，第三个是「两次运行之间」的语义，面试经常混着问。

### 2.1 State schema：三种形态

| 形态 | Python | JS | 说明 |
|---|---|---|---|
| 字典式 | `TypedDict` | `Annotation.Root({...})` | 最常用，字段即状态键 |
| 类式 | `dataclass` | 无等价写法 | 字段默认值方便 |
| 校验式 | Pydantic `BaseModel` | zod schema | 作为**整个 state** 传入，不能塞进 `Annotation.Root` 的字段 |

不管哪种形态，核心事实只有一条：**schema 只描述字段，不描述合并规则；同一张图里每个字段可以有自己的合并规则**。`counter` 走覆盖、`log` 走追加、`messages` 走消息语义，三者互不影响。

```python
from typing import TypedDict

class State(TypedDict):
    n: int
    note: str
```

`StateGraph(State)` 只是「画图纸」，必须 `compile()` 才能运行。结构错误（比如边指向不存在的节点）在编译期就会暴露，`checkpointer` / `store` / `cache` 这些运行时依赖也在这一步传入。

### 2.2 Reducer：默认覆盖，`Annotated` 才合并

reducer 的语义是一个二元函数：

```text
new_value = reducer(left = 当前状态值, right = 节点返回的更新)
```

字段没有显式声明 reducer 时，LangGraph 用**覆盖**：后写的值把旧值冲掉。面试最常考的就是「两个节点都写同一个字段，最后剩什么」。

| 字段写法 | reducer | 两个节点分别返回 | 最终值 |
|---|---|---|---|
| `counter: int` | 覆盖 | `1`、`2` | `2`（前一个被冲掉） |
| `log: Annotated[list, operator.add]` | 追加 | `["a"]`、`["b"]` | `["a", "b"]` |
| `messages: Annotated[list, add_messages]` | 消息专用 | 两条 AI 消息 | 起点 + a + b |

```python
import operator
from typing import Annotated, TypedDict
from langgraph.graph import START, END, StateGraph, add_messages

class State(TypedDict):
    counter: int                                  # 无 Annotated → 覆盖
    log: Annotated[list[str], operator.add]       # 追加
    messages: Annotated[list, add_messages]       # 消息专用

def a(state: State) -> dict:
    return {"counter": 1, "log": ["a"], "messages": [{"role": "ai", "content": "a"}]}

def b(state: State) -> dict:
    return {"counter": 2, "log": ["b"], "messages": [{"role": "ai", "content": "b"}]}

graph = (StateGraph(State).add_node("a", a).add_node("b", b)
         .add_edge(START, "a").add_edge("a", "b").add_edge("b", END).compile())
# counter=2；log=['a','b']；messages 依次为 a、b
```

两个边界必须记住：

- **并行分支写同一个无 reducer 字段会抛 `InvalidUpdateError`**，不是「不确定地覆盖」——编译能过，跑起来才炸（源码核对：`Can receive only one value per step`）。
- **顺序执行时才是「后写的赢」**。所以「默认覆盖」这句话要补一句：并行写同键，直接报错。

### 2.3 `add_messages` 与 `Overwrite`

`add_messages` 是消息专用 reducer，解决普通列表解决不了的三件事：

| 能力 | 说明 | 口径 |
|---|---|---|
| 追加 | 新消息接到列表尾部 | 实测 |
| 按 `id` 去重 / 替换 | 同一个 `id` 再次出现是替换而不是重复追加 | 源码核对（示例没构造同 ID 用例） |
| 类型宽松 | 接受 `BaseMessage`、dict、`(role, content)` 元组 | 源码核对 |

JS 侧对应 `messagesStateReducer`，预置 schema 是 `MessagesAnnotation`。**不要用普通 `concat` 代替**：对话里工具消息回写、消息修正都依赖 ID 语义，普通 concat 只会越堆越长。

合并型 reducer 带来一个反直觉问题：**想清空一个追加型字段，返回空列表没用**。`operator.add` 会把 `[]` 拼上去，旧值仍在。要用 `Overwrite` 显式绕过 reducer：

```python
from langgraph.types import Overwrite

def reset(state: State) -> dict:
    # return {"log": []} 清不掉；下面这样才行
    return {"log": Overwrite([])}
```

> 口径：包了 `Overwrite` 能清空是实测；「不包就清不掉」是按 reducer 语义成立，但示例里那一支只打印了字面量、没有真正执行。`Overwrite` 只对合并型字段有意义，无 reducer 的字段本来就是覆盖。

### 2.4 同一线程再次 `invoke`：输入也走 reducer

前提是 `compile(checkpointer=...)`。同一 `thread_id` 的第二次 `invoke`，输入字典不是「替换整个状态」，而是**逐字段合并**。本机五连实测（`n` 覆盖、`trail` 追加）：

| 次 | 输入 | 结果 `n` | 结果 `trail` | 语义 |
|---|---|---|---|---|
| 1 | `{"n": 0, "trail": ["起点"]}` | `1` | `["起点","→1"]` | 首次执行 |
| 2 | `None` | `1` | 不变 | **空操作**：已跑完，无待执行任务 |
| 3 | `{}` | `2` | `+["→2"]` | **从检查点续跑** |
| 4 | `{"n": 100}` | `101` | `+["→101"]` | 输入按覆盖语义冲掉检查点值 |
| 5 | `{"trail": ["插一条"]}` | `102` | `+"插一条","→102"` | 没出现的 `n` 沿用检查点 |

```python
cfg = {"configurable": {"thread_id": "t-1"}}
graph.invoke({"n": 0, "trail": ["起点"]}, cfg)   # n=1
graph.invoke(None, cfg)                          # n=1，空操作
graph.invoke({}, cfg)                            # n=2，续跑
graph.invoke({"n": 100}, cfg)                    # n=101，输入覆盖
graph.invoke({"trail": ["插一条"]}, cfg)          # n=102，n 沿用检查点
```

三条结论，面试可以直接背：

1. 输入里**出现**的字段，按该字段自己的 reducer 合并进检查点状态；
2. 输入里**没出现**的字段，保留检查点里的值；
3. `invoke(None, cfg)` 是空操作，`invoke({}, cfg)` 才是续跑——这两个极容易混。

---

## 三、控制流：节点、边与并行原语

控制流原语一共七件，面试常把它们混成一锅。先用一张表分开：

| 原语 | 形状 | 何时用 | 关键限制 |
|---|---|---|---|
| `add_edge` | 固定一条 | 顺序执行 | 无 |
| `add_conditional_edges` | 运行时选一条（也可返回多条目标） | 分支、循环回边 | 路由函数返回节点名或 `Send` 列表 |
| `Send` | 运行时派发 N 路并行 | map-reduce | payload 是目标节点输入；汇总靠 reducer |
| `Command` | 节点内更新状态 + 跳转 | handoff、动态路由 | 只有 `Command(resume=...)` 能当输入 |
| 子图 | 编译好的图当节点 | 复用、多 agent | 流式要 `subgraphs=True`，有独立 `checkpoint_ns` |
| `add_sequence` | 固定顺序 | 线性链 | 不接 `START` / `END` |
| `add_edge([a, b], "join")` | 静态扇入 | 固定几路汇合 | 编译期写死 |

### 3.1 节点、边、条件边与超步

节点就是一个函数：读 state、返回**增量字典**（不是完整状态）。异步函数也可以。边分两种：普通边无条件走，条件边由路由函数决定。

```python
def route(state: State) -> str:
    return "math" if "等于" in state["q"] else "weather"

builder.add_conditional_edges(
    "classify", route,
    {"math": "math", "weather": "weather"},
)
```

图不是「逐个函数调用」那样执行，而是按**超步（super-step）**推进：**一轮里所有就绪节点同时执行，轮末统一用 reducer 结算，再进入下一轮**。这句话解释了两件事：`Send` 派发的多个分支跑在同一个超步；检查点也是逐超步落的（第四节）。

### 3.2 `Send`：运行期动态并行

条件边是「选一条路」，`Send` 是「同时走多条路」。路由函数返回一个 `Send` 列表，LangGraph 为每一项起一个并行任务。

```python
import operator
from typing import Annotated, TypedDict
from langgraph.types import Send

class Fan(TypedDict):
    items: list[str]
    results: Annotated[list[str], operator.add]

def fan_out(state: Fan) -> list[Send]:
    return [Send("worker", {"item": it}) for it in state["items"]]

def worker(state: dict) -> dict:
    return {"results": [f"{state['item']} 完成"]}
```

三个易错点：

- **payload 是目标节点的输入**，不是完整状态。worker 读 `state["item"]`（当前一项），不是 `state["items"]`。
- **汇总字段必须有 reducer**，否则并行分支互相覆盖；同一超步写无 reducer 字段会抛 `InvalidUpdateError`。
- **`Send` 与静态扇入不是一回事**：前者按数据长度动态派发，后者是编译期固定的几路汇合。

### 3.3 `Command` 与子图

`Command` 让节点自己决定去哪，同时还能更新状态：

```python
from langgraph.types import Command

def triage(state: State) -> Command:
    target = "refund" if state["intent"] == "refund" else "faq"
    return Command(goto=target, update={"route": target})
```

两条硬约束：

- **`Command(goto=...)` 只能在节点内部返回，不能当 `invoke` 的输入**；能从外面喂进去的只有 `Command(resume=...)`。
- JS 侧返回 `Command` 的节点要在 `addNode` 第三个参数里用 `ends` 声明去向（源码核对；本机 `tsc` 报的是类型不匹配，**没有复现** `UnreachableNodeError` 这个具体错误名）。Python 靠类型注解 `Command[Literal[...]]` 表达同一件事。

子图就是「把编译好的图直接当节点」。Python 的 `create_agent` 返回 `CompiledStateGraph`，可以直接 `add_node("db", db_agent)`；JS 的 `createAgent` 返回包装对象，必须先取 `agent.graph`（实测）。

```python
child = (StateGraph(ChildState)
         .add_node("step", step)
         .add_edge(START, "step").add_edge("step", END)
         .compile())

parent.add_node("child", child)   # 子图内部状态落在自己的 checkpoint_ns
```

父子状态怎么共享：**schema 里同名的键共享同一通道**；字段对不上时，要在父图节点里做一层映射函数，而不是硬塞。子图的内部消息默认不透传，流式要显式 `subgraphs=True`（第六节）。

### 3.4 `add_sequence` 与静态扇入

`add_sequence` 只补中间的顺序边，入口和出口仍要自己接：

```python
sequence = (StateGraph(Flow)
            .add_sequence([seq_a, seq_b])
            .add_edge(START, "seq_a")
            .add_edge("seq_b", END)
            .compile())
```

静态扇入表示「等所有起点都完成再跑 join」：

```python
fan_in = (StateGraph(Flow)
          .add_node("left", left).add_node("right", right).add_node("join", join)
          .add_edge(START, "left").add_edge(START, "right")
          .add_edge(["left", "right"], "join")
          .add_edge("join", END)
          .compile())
# trail = ['left', 'right', 'join<-left,right']（实测）
```

`add_edge([a, b], "join")` 是**静态**的：几路汇合在编译期写死。`Send` 是**动态**的：跑起来才知道有几路。两者都能并行，但回答「为什么不用 Send」时要说清这个区别。

### 3.5 循环与 `recursion_limit`

条件边绕回自己就形成循环，比如 agent 的「模型 → 工具 → 模型」。循环必须有人踩刹车：`recursion_limit` 限制单次运行最多走多少个超步。

```python
def keep_going(state: Loop) -> str:
    return "inc" if state["n"] < 3 else END

loop = (StateGraph(Loop).add_node("inc", inc).add_edge(START, "inc")
        .add_conditional_edges("inc", keep_going, {"inc": "inc", END: END})
        .compile())
loop.invoke({"n": 0}, {"recursion_limit": 5})   # {'n': 3}
```

三个事实（`langgraph` 1.2.12，Python）：

1. **本机默认上限是 10007**（`DEFAULT_RECURSION_LIMIT`，源码核对）。这个值随版本变：旧文档写 1000、课程包在 1.1.2 上量到 10000、讲义里出现过 25。**生产代码永远显式传**。
2. 超过上限抛 `GraphRecursionError`，报错文本里带当前 limit（实测）。
3. `RemainingSteps` 是注入的 managed 值：状态里声明 `remaining_steps: RemainingSteps`，节点里就能读到「进入本节点时还剩几步」（`recursion_limit=5` 时看到 4，实测）。Python 从 `langgraph.managed` 导入；**JS 1.4.17 没有同名导出**（本机核对）。JS 的配置键是驼峰 `recursionLimit`。

---

## 四、持久化：checkpointer、store 与时间旅行

持久化在面试里经常被简化成「加个 `InMemorySaver`」，真正的考点是**两套系统、三级定位、三个方法、三档落盘**。

### 4.1 checkpointer 与 store：两套互不替代的系统

| 维度 | Checkpointer | Store |
|---|---|---|
| 作用范围 | 单个线程（thread） | 跨线程 |
| 存什么 | 图状态的完整快照 | 应用自定义的键值数据 |
| 怎么取 | 运行时传 `thread_id` | 节点里用 `runtime.store` |
| 典型用途 | 对话延续、HITL、时间旅行、故障恢复 | 用户偏好、长期事实、共享知识 |
| 隔离方式 | 线程之间互相看不到 | 按命名空间自行隔离 |

判断口径只有一句：**「这次对话内记得」→ checkpointer；「换个人、换次会话还记得」→ store**。把用户偏好写进 checkpointer，换个 `thread_id` 就丢；把整段对话塞进 store，检索噪声和成本都会上去。

### 4.2 三级定位：`thread_id` / `checkpoint_ns` / `checkpoint_id`

图在**每个超步边界**落一份检查点。运行配置里的 `configurable` 决定「读 / 写哪一份」：

| 键 | 示例 | 定位什么 |
|---|---|---|
| `thread_id` | `"order-2026"` | 哪条线程（对话的身份证，必填） |
| `checkpoint_ns` | `""` | 线程里的哪张图；顶层为空串，子图有自己的命名空间 |
| `checkpoint_id` | `"1ef4..."` | 哪一个快照；不传就取最新 |

`thread_id` 不只是「会话 ID」：没有它，HITL 恢复时定位不到线程，多轮记忆也无处挂。`checkpoint_ns` 是子图持久化的关键（4.4）。`checkpoint_id` 之所以重要，是因为 `update_state` 接收的正是**某个历史快照自带的 config**。

### 4.3 读与改：`get_state` / `get_state_history` / `update_state`

| 方法 | 返回 | 用途 | 注意 |
|---|---|---|---|
| `get_state(cfg)` | `StateSnapshot` | 当前快照：`values` / `next` / `config` / `metadata` / `tasks` | `next` 为空表示已跑完 |
| `get_state_history(cfg)` | 迭代器，新 → 旧 | 翻历史快照 | JS 是异步迭代器，必须 `for await` |
| `update_state(cfg, values)` | 新分支的 config | 改写状态、时间旅行 | **不改原线程历史** |

```python
snap = graph.get_state(cfg)
print(snap.values, snap.next)            # 跑完 → next 为空

for s in graph.get_state_history(cfg):   # 新 → 旧
    print(s.metadata["step"], s.values["n"], s.next)

target = list(graph.get_state_history(cfg))[-2]
forked = graph.update_state(target.config, {"n": 100, "trail": ["人工改写"]})
graph.invoke(None, forked)               # 从新分支重放
```

**时间旅行不是改历史，而是开分支**——语义和 git 的 branch 同构：历史只读，你只是在某个旧 commit 上开了条新分支。这也是调试 agent 最有力的一招：把走错的那一步改回正确状态，看它接下来会不会又走错。

### 4.4 子图持久化：`checkpoint_ns` 与两层历史

- 子图不单独传 checkpointer 时，继承父图的 saver，检查点落在父图命名空间下的子命名空间（`checkpoint_ns = "child:<uuid>"`）。
- 子图自带 saver 时，它仍然是父图的一次 task，只是有自己的一层历史。
- 暂停态下用 `get_state(cfg, subgraphs=True)` 下钻：返回的 `StateSnapshot.tasks[]` 里，每个 task 的 `.state` 是子图快照。
- **`get_state_history` 没有 `subgraphs` 参数**（源码核对签名里只有 `filter` / `before` / `limit`），子图历史要拿它自己的 `checkpoint_ns` 单独查。
- 图跑完后 `tasks` 为空，事后再想看子图历史，只能靠子图自己的 saver 或命名空间。

### 4.5 `durability`：三档落盘时机

`durability` 只在已经配了 checkpointer 时才有意义。同一张两节点图、同一输入，本机实测的历史快照数：

| 档位 | 落盘时机 | 快照数 | 适用 |
|---|---|---|---|
| `sync` | 每个超步同步落盘 | 4 | 崩溃后最多丢当前一步，关键流程 |
| `async` | 异步落盘，`invoke` 返回前补写 | 4 | **本机默认值**，吞吐优先 |
| `exit` | 只在图结束时写一次 | 1 | 可整段重跑、追求最少写入 |

两个坑：**默认是 `async`**（源码核对），关键流程不要依赖默认；**`exit` 不是「更省的持久执行」**，中途崩溃会丢掉整段运行，故障恢复至少用 `async`。

### 4.6 内置实现与 Store API

| 实现 | 导入 | 落在哪 | 适用 |
|---|---|---|---|
| `InMemorySaver`（JS `MemorySaver`） | `langgraph.checkpoint.memory` | 进程内存 | 开发与测试 |
| `SqliteSaver` | `langgraph.checkpoint.sqlite` | 单个 SQLite 文件 | 本地单机 |
| `PostgresSaver` | `langgraph.checkpoint.postgres` | PostgreSQL | 生产 |

注意：`langgraph` 1.2.12 默认安装**不含** `langgraph.checkpoint.sqlite`，要先 `pip install langgraph-checkpoint-sqlite`（本机核对）。**中途从 `InMemorySaver` 换成 `PostgresSaver`，历史数据搬不过去**——存储结构不同，已产生的会话找不回来，持久化方案要在项目早期定死。

Store 的模型是「命名空间元组 + 键 + dict 值」：

| 方法 | 语义 | 注意 |
|---|---|---|
| `put(ns, key, value)` | 写入 | 值必须是 dict，传字符串/列表会抛 `ValueError` |
| `get(ns, key)` | 读取 | 返回 `Item` 或 `None`，数据在 `.value` |
| `search(ns_prefix, ...)` | 搜索 | **前缀匹配**，不是精确匹配 |
| `delete(ns, key)` | 删除 | |
| `list_namespaces(...)` | 列命名空间 | 返回路径列表 |

`search(("alice",))` 会把 `("alice","memories")` 和 `("alice","notes")` 全捞出来（实测 3 条）。语义检索要在构造 Store 时配 `index`（Python `embed` / JS `embeddings`，加 `dims`、`fields`），需要真实嵌入模型，**未实测**。

按作用域可以把记忆分四层，面试问「记忆怎么设计」时按这个答：

| 记忆类型 | 载体 | 作用域 | 典型内容 |
|---|---|---|---|
| 短期对话 | checkpointer | 线程内 | 消息、工具结果、待审批状态 |
| 长期事实 | Store | 跨线程 | 用户偏好、租户配置 |
| 语义记忆 | Store `index` | 跨线程、按相似度 | 领域知识、历史工单 |
| 程序性记忆 | Skills / `AGENTS.md` | 文件、按需加载 | 操作步骤、团队规范 |

---

## 五、interrupt 与 resume：人在回路

HITL 是 LangGraph 面试的高频压轴题。机制本身不复杂，难的是**恢复时节点会从头重跑**这一条，以及由它推出的四条铁律。

### 5.1 一次完整往返与三个前置条件

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command, interrupt

def approval(state: Order) -> Command:
    decision = interrupt({"question": f"确认扣款 {state['amount']} 元？"})
    return Command(goto="charge") if decision else Command(goto="cancelled")

def charge(state: Order) -> dict:
    return {"status": "已扣款"}      # 真副作用放这里，只执行一次

app = (StateGraph(Order).add_node("approval", approval).add_node("charge", charge)
       .add_node("cancelled", lambda s: {"status": "已取消"})
       .add_edge(START, "approval")
       .add_edge("charge", END).add_edge("cancelled", END)
       .compile(checkpointer=InMemorySaver()))
cfg = {"configurable": {"thread_id": "order-1"}}

r1 = app.invoke({"amount": 199}, cfg)
print(r1["__interrupt__"][0].value)   # payload
print(app.get_state(cfg).next)        # ('approval',) —— 停在半路

r2 = app.invoke(Command(resume=True), cfg)   # 同一个 thread_id
print(r2["status"])                   # 已扣款
```

三个前置条件缺一不可：

| # | 条件 | 缺了会怎样 |
|---|---|---|
| 1 | 图带 checkpointer | 中断状态无处落盘，图停不住 |
| 2 | 调用带 `thread_id` | 恢复时定位不到线程 |
| 3 | payload 与 resume 值可序列化 | 写不进检查点，直接报错 |

`Command(resume=...)` 是**唯一**能当 `invoke` / `stream` 输入的 `Command` 形态；`Command(goto=...)` 只能在节点内部返回。

### 5.2 恢复 = 整个节点从头重跑

这是本章最该记死的一条：**恢复不是从 `interrupt()` 那一行继续，而是把整个节点从头再执行一遍**。

原因不在 `interrupt()`，在检查点的粒度：检查点只落在超步边界，它存得住「这一轮开始前的状态」，存不住「节点内部执行到了哪一行」。恢复时只能从上一个检查点把节点重跑一遍，跑到 `interrupt()` 那一行时发现「这里断过、且带了 resume 值」，再把值交还给你。**重跑就是它定位断点的手段，不是缺陷**。

实测证据：在 `interrupt()` 之前往列表里 append 一行日志，跑完一轮后这行出现两次（两语言都复现）。

由此推出四条铁律：

| # | 铁律 | 为什么 |
|---|---|---|
| 1 | 不要把 `interrupt()` 包进 `try/except` | 它靠抛异常挂起，吞掉异常等于取消暂停 |
| 2 | 不要重排节点内的 `interrupt()` | 多个中断按调用顺序对应 resume 值，顺序一变就配错 |
| 3 | 不要传复杂值 | 对象、函数、数据库连接都进不了检查点 |
| 4 | `interrupt()` 之前的副作用必须幂等 | 那段代码注定执行两次 |

第 4 条的正确解法不是「让副作用幂等」，而是**把真副作用挪出去**：扣款、发邮件、删文件拆成独立节点，放在 `interrupt()` 之后。这样重跑的是审批节点，副作用节点只执行一次。

### 5.3 静态中断：`interrupt_before` / `interrupt_after`

不动节点、编译时声明暂停点：

```python
app = builder.compile(checkpointer=InMemorySaver(), interrupt_before=["charge"])
app.invoke({"amount": 199}, cfg)   # 执行到 charge 节点前停下
app.invoke(None, cfg)              # 人工处理完后从节点边界继续
```

它只能在**节点边界**停，停不到节点中间，也拿不到结构化的人工输入（人工决定得另外写进状态）。**适合调试时观察中间状态，不推荐做审批流**。JS 侧是 `interruptBefore` / `interruptAfter`。

### 5.4 工具级审批：中间件封装的 HITL

`HumanInTheLoopMiddleware` 把 `interrupt()` 封装成「工具调用前审批」：命中 `interrupt_on` 的工具会被拦下，图停在检查点，恢复时用 `Command(resume={"decisions": [...]})`。

```python
agent = create_agent(
    model=model, tools=[refund],
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"refund": True})],
    checkpointer=InMemorySaver(),
)
agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), cfg)
```

| 决策 | Python | JS | 含义 |
|---|---|---|---|
| 同意 | `{"type": "approve"}` | 同左 | 原样执行 |
| 编辑 | `{"type": "edit", "edited_action": {...}}` | `editedAction` | 改参数/工具后执行 |
| 拒绝 | `{"type": "reject", "message": "..."}` | 同左 | 不执行，理由回给模型 |
| 代答 | `{"type": "respond", "message": "..."}` | **无** | 不执行工具，人工答复当工具结果 |

Python 默认允许四种决策，**JS 只支持前三种**（类型定义核对）。一次中断里有多个工具调用时，`decisions` 的数量必须与 `action_requests` 一一对应，否则抛 `ValueError`。approve / reject 两条路径实测，edit / respond 只做了类型与源码核对。

---

## 六、流式：七档 `stream_mode` 与事件流

流式有三个控制面：`stream_mode` 选投影、`subgraphs` 决定透不透传、`astream_events` 看回调事件。面试常问「打字机效果为什么没了」，答案通常在第二个控制面。

### 6.1 七档投影

| 取值 | 给你什么 | 前置条件 / 用途 |
|---|---|---|
| `values` | 每步之后的完整状态 | 最省心，体积最大 |
| `updates` | 每步节点返回的增量（带节点名） | 进度条、步骤高亮 |
| `messages` | `(token, metadata)` 二元组 | 打字机效果；图里必须真有模型节点 |
| `custom` | 节点里主动推的事件 | 「第 3/10 步」这类业务进度 |
| `checkpoints` | 检查点事件 | **需要 checkpointer** |
| `tasks` | 任务开始 / 结束（含结果与错误） | **不需要 checkpointer**（实测） |
| `debug` | checkpoints + tasks 及额外元数据 | 排障；信息最多也最杂 |

`custom` 档要在节点里主动推：Python `get_stream_writer()`，JS `getWriter()`。`debug` 的实际事件序列是 `checkpoint → checkpoint → task → task_result → checkpoint`，里面有 `task_result`，不是「两个词」能概括的。

> 别把分块数当语义：本机 `values/updates/messages/custom/checkpoints/tasks/debug` 的首轮分块数是 2/1/1/1/3/2/5，但那是假模型 + 这张图的产物。要断言就断言首块类型、字段、事件名。

### 6.2 list-mode 与 `subgraphs` 的分块形状

这是最容易写错解析代码的一处：

| 配置 | Python | JS | 解析要点 |
|---|---|---|---|
| 单档 | `payload` | `payload` | 直接读 |
| list-mode | `(mode, payload)` | `[mode, payload]` | 先看 `mode`，再解 payload |
| list + subgraphs | `(namespace, mode, payload)` | `[namespace, mode, payload]` | **三元组**，`namespace` 是元组/数组 |
| 事件流 | `{"event", "name", "data", ...}` | 同左 | 按 `event` 名分流 |

**不是** `(namespace, (mode, payload))` 这种「namespace 包着二元组」的嵌套形状（实测否定）。解包要写：

```python
for ns, mode, payload in app.stream(
        inp, cfg, stream_mode=["updates", "custom"], subgraphs=True):
    origin = ns[0].split(":")[0] if ns else "parent"
    print(origin, mode, payload)
```

`namespace` 不是子图名字符串，而是一条路径：`("child:<uuid>",)`。取 `ns[0].split(":")[0]` 得到 `child`；父图自己产生的事件是空元组。

### 6.3 子图透传：A / B / C 三组对比

把 `create_agent` 的产物直接挂进父图，它就变成了子图，而**子图的内部输出默认不往上传**。

| 组 | 怎么流 | 能看见什么 |
|---|---|---|
| A | 直接 `stream` 子 agent | 内部消息一览无余（模型调用、工具消息全在） |
| B | 父图 `stream`，不加 `subgraphs` | 只剩跨边界的少数几条，token 全没了 |
| C | 父图 `stream`，加 `subgraphs=True` | 恢复子图最终模型输出；分块带 namespace，能区分来源 |

「后端日志正常、前端打字机不动」的根因就是 B。修复不是改模型，而是显式加 `subgraphs=True`。注意 C 也只恢复子图的最终模型输出，工具消息仍未透出——这是实测边界，不是配置没写对。

### 6.4 `astream_events`：按回调事件流

`stream_mode` 是按状态投影，`astream_events` 是按回调事件流，能看到模型 token、工具开始 / 结束、链的嵌套关系。

```python
async for event in agent.astream_events(inp, version="v2"):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")
```

Python 侧事件名有 `on_chat_model_stream` / `on_tool_start` / `on_tool_end` / `on_chain_start`；`version` 支持 v1/v2/v3，默认 v2（源码核对）。`on_chat_model_stream` 要求模型真正走流式路径，假模型必须实现 `_astream`。

JS 有一处实测差异：**`model.streamEvents` 会出 `on_chat_model_stream`，但 `agent.streamEvents` 在 1.4.17 只出 start/end**。要逐 token，用 `agent.stream({streamMode:"messages"})`；要看模型级事件，直接对 model 调 `streamEvents`。

---

## 七、节点级治理：重试、超时与缓存

治理件都挂在 `add_node` 上，是**节点级**而非全局。面试问「节点失败怎么办」，按「重试 → 超时 → 缓存 → 兜底」四层答。

### 7.1 `RetryPolicy`：失败重试

```python
from langgraph.types import RetryPolicy

graph.add_node("flaky", flaky,
               retry_policy=RetryPolicy(max_attempts=3, retry_on=ValueError))
```

| 参数 | Python | JS | 注意 |
|---|---|---|---|
| 最大尝试次数 | `max_attempts`（默认 3） | `maxAttempts` | 含首次执行 |
| 重试间隔 | `initial_interval`（秒，默认 0.5） | `initialInterval`（**毫秒**） | 照抄数字会差 1000 倍 |
| 触发异常 | `retry_on` | `retryOn` | 不写则按默认策略 |

实测：前两次抛 `ValueError`、第三次成功时，节点总共执行 3 次。重试只适合**幂等**操作；扣款类节点要么不重试，要么带幂等键。

### 7.2 `timeout`：只支持 async 节点

```python
async def slow(state: Loop) -> dict:
    await asyncio.sleep(0.2)
    return {"n": 1}

graph.add_node("slow", slow, timeout=0.05)   # 仅 async 节点
```

给**同步节点**设 `timeout`，`compile()` 直接抛 `ValueError`（实测：`Node timeouts are only supported for async nodes`）。这不是配置问题——Python 无法安全取消同步执行。要么把节点改成 `async`，要么在节点内部自己做超时。JS 侧 `timeout` 单位是毫秒。

### 7.3 `CachePolicy` 与 `error_handler`

```python
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

graph.add_node("pure", pure, cache_policy=CachePolicy(ttl=60))
graph = graph.compile(cache=InMemoryCache())
```

- 缓存键默认由**节点输入**生成，`ttl` 单位是秒；同一输入第二次调用直接复用结果（实测节点只执行 1 次）。
- **只给纯节点开缓存**：写库、发消息、扣款这类有副作用的节点开了缓存，会跳过真实副作用。
- JS 的 `InMemoryCache` 不在 `@langchain/langgraph` 顶层，要从 `@langchain/langgraph-checkpoint` 导入（本机核对）。
- `error_handler` 在重试耗尽后接管，与重试策略分开配置。签名与继承规则只做了**源码核对**，示例未构造「重试耗尽后交给 error_handler」的用例。

---

## 八、多智能体拓扑：supervisor、handoff 与 swarm

多智能体不是「上几个 agent 就更强」，而是**控制权怎么流**。三种拓扑只差一个变量：交出去的控制权还能不能收回来。

### 8.1 三种拓扑

| 拓扑 | 控制权怎么流 | 适合 | 风险 |
|---|---|---|---|
| **supervisor** | 有中心调度者，反复决定下一步交给谁，**交出去还能收回来** | 需要多轮协调的任务 | 调度者成为瓶颈 / 单点；逻辑不好会踢皮球 |
| **handoff** | 交棒后**不回来**，接手的 agent 负责到底 | 一次分流就结束（像「转人工」） | 交错了没人兜底；链路长难追 |
| **swarm** | **没有中心**，agent 之间互相转移 | 任务边界模糊、需要接力 | 最容易失控：循环转圈、没人收尾 |

三者的关系：**handoff 是 supervisor 去掉「收回来」，swarm 是 handoff 去掉「中心」**。去掉得越多越省事，也越难管。

### 8.2 supervisor：把 agent 当节点

父图里放一个 supervisor 节点做路由，若干 agent 节点做具体工作，**每个 agent 完成后把边指回 supervisor**——这条回边就是 supervisor 的定义性特征。

```python
def supervisor(state: TopState) -> dict:
    return {"route": decide_next(state)}      # "db" / "mail" / END

parent = (StateGraph(TopState)
          .add_node("supervisor", supervisor)
          .add_node("db", db_agent)           # Python 可直接挂编译好的图
          .add_node("mail", mail_agent)
          .add_edge(START, "supervisor")
          .add_conditional_edges("supervisor", lambda s: s["route"],
                                 {"db": "db", "mail": "mail", END: END})
          .add_edge("db", "supervisor")       # 回边：交出去还能收回来
          .add_edge("mail", "supervisor")
          .compile())
```

两个工程细节：agent 当节点后就是子图，流式要 `subgraphs=True`；**给每个 agent 起 `name=`**，否则 trace 里全叫默认名，分不清哪一路在跑。

### 8.3 handoff：用 `Command` 交棒

没有调度者，节点内部直接决定去向，且不回来：

```python
from langgraph.types import Command

def triage(state: State) -> Command:
    target = "billing" if state["intent"] == "refund" else "tech"
    return Command(goto=target, update={"owner": target})
```

`Command(goto=...)` 只能在节点内部返回，不能当 `invoke` 输入；JS 侧同样要在 `addNode` 里用 `ends` 声明去向。

### 8.4 swarm 与选型

swarm 没有中心，agent 之间互相转移。它最灵活也最容易失控，落地前必须把两件事设计死：**终止条件**（什么状态算完成）和**最大转移次数**（防止转圈）。本教程的示例只实现了 supervisor 与 handoff，**swarm 只讲机制与风险，没有可运行代码**，面试时别把它说成「已经跑通」。

| 场景 | 选 | 理由 |
|---|---|---|
| 多轮协调、需要汇总 | supervisor | 有中心，能收回控制权 |
| 一次分流、各管各的 | handoff | 少一层调度，链路短 |
| 边界模糊、互相接力 | swarm | 无中心，但必须加终止条件 |
| 单 agent 工具就够 | 不用多智能体 | 多一层就多一份 token、延迟和排障成本 |

---

## 九、部署：`langgraph.json` 与本地 Agent Server

部署题的答法分两层：**清单怎么写**、**本地怎么验证**。平台侧（托管、云端）没有实测，不要展开成「我上线过」。

### 9.1 `langgraph.json`：部署清单

| 字段 | 作用 | 注意 |
|---|---|---|
| `dependencies` | 依赖来源，`"."` 表示本地包 / 同目录 `requirements.txt` | 本机示例用 `["."]` |
| `graphs` | 图 ID → `模块路径:变量名` | `{"agent": "./19_deploy_agent.py:graph"}` |
| `env` | 环境变量文件或键值映射 | 生产用 `.env` 或平台 Secret，**别写明文密钥** |
| `python_version` | 构建镜像用的 Python 版本 | CLI 只接受 `3.11` / `3.12` / `3.13` |
| `dockerfile_lines` | 追加到 Dockerfile 的构建行 | 本机未实测 |
| `http` / `auth` | HTTP 服务与鉴权 | 托管平台使用，本机未实测 |

```json
{
  "dependencies": ["."],
  "graphs": { "agent": "./19_deploy_agent.py:graph" }
}
```

`graphs` 指向的变量必须是**编译好的图**；路径相对于 `langgraph.json` 所在目录。

### 9.2 `validate` 与 `dev`：本地验证

```bash
pip install -U "langgraph-cli[inmem]"
langgraph validate -c langgraph.json
langgraph dev --config langgraph.json --no-browser --no-reload --port 2025
curl http://127.0.0.1:2025/ok
```

| 命令 | 作用 | 坑 |
|---|---|---|
| `validate -c` | 只校验清单 | **用 `-c`**，不是 `--config` |
| `dev --config` | 起内存版 Agent Server（`langgraph-runtime-inmem`），带热重载 | **用 `--config`**，两个子命令选项名不通用（实测） |
| `/ok` | 就绪探针 | 返回 `{"ok":true,"services":{}}` |

Windows 上还要 `pip install colorama`，否则 `structlog` 的彩色 ConsoleRenderer 会在日志配置阶段直接崩，表现为「服务还没起就退出」（本机实测）。`python_version` 只影响 `build` 的镜像，`dev` 用当前解释器；本机 3.14.2 能跑 `dev`，不代表镜像能构建。

### 9.3 Studio、AgentChatUI、Docker 与云端：未实测边界

`dev` 启动日志会给出 `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2025` 这类地址。本机**只验证了服务端 `/ok` 与图导入**：

| 对象 | 状态 | 说明 |
|---|---|---|
| Studio 页面 | **未实测** | 需要浏览器与账号，没打开过 |
| AgentChatUI | **未实测** | 同上 |
| Docker 构建 / 容器 | **未实测** | `build` / `up` 未跑 |
| 云端托管部署 | **未实测** | 平台配置与账号流程未验证 |

面试里正确的说法是「本地用 `langgraph dev` 起过内存版服务、验证过 `/ok`；Studio 和云端没有实际部署经验」——比含糊说「部署过」安全得多。

### 9.4 上线前三查与治理件落点

| # | 检查项 | 不做的后果 |
|---|---|---|
| 1 | 检查点有没有持久化 | 进程一重启会话全丢；多副本时上下文对不上 |
| 2 | 有没有调用次数上限 | 循环一旦失控，账单和延迟同时爆 |
| 3 | 高风险操作有没有人在回路 | 扣款、发邮件、删文件没有审批就执行 |

| 本地能力 | 本地写法 | 上线落点 |
|---|---|---|
| 持久化 | `compile(checkpointer=InMemorySaver())` | 托管：平台自动接；自托管：`PostgresSaver` + 连接串 |
| durability | `invoke(..., durability="sync")` | 写进运行配置；关键流程别依赖默认 `async` |
| 调用限额 | `recursion_limit` + `ModelCallLimitMiddleware` | agent 代码里保留，平台侧再配预算告警 |
| 人审 | `interrupt()` / `HumanInTheLoopMiddleware` | 平台审批 UI 只是前端，后端仍是检查点 + resume |
| 密钥 | `.env` / 环境变量 | 平台 Secret；不要进镜像或仓库 |

一句话：**部署不是把本地代码原样上传**——持久化后端、密钥来源、审批 UI 都会换，换的是接线，不是 agent 逻辑。

---

## 十、选型：什么时候用 LangGraph

选型题考的不是「哪个强」，而是「你能不能为复杂度说出理由」。答题顺序：先看流程形状，再看状态与中断需求，最后看团队维护成本。

### 10.1 决策表

| 场景 | 首选 | 理由 |
|---|---|---|
| 线性、无状态、步骤固定 | LCEL / 普通函数 | 引入图是过度设计 |
| 单 agent + 工具循环 | `create_agent` | 循环已经内置，配中间件即可 |
| 多阶段、条件分支、循环 | LangGraph Graph API | 控制流要自己画 |
| 人工审批、断点恢复 | LangGraph | `interrupt` + checkpointer |
| 固定并行汇合 / 动态 map-reduce | LangGraph | 静态扇入 / `Send` |
| 多 agent 协作 | LangGraph | supervisor / handoff |
| 长周期、文件系统、子代理、技能 | Deep Agents | 成品 harness，别从零拼 |
| 逻辑就是一条函数链 | Functional API | 比画图直接 |

一个常见反问是「`create_agent` 不够吗」。答案：`create_agent` 的循环形状是固定的「模型 → 工具 → 模型」，中间件只能挂钩子、改不了形状；一旦要分类分流、并行、审批、多阶段流水线，就得自己画图。

### 10.2 迁移与反模式

从 `AgentExecutor` / LCEL 迁到 v1，三步顺序（一次全改会分不清哪步引入的问题）：

| 步 | 动作 | 风险 |
|---|---|---|
| 1 | `AgentExecutor` → `create_agent` | 接口迁移，**不是行为等价**：输入从 `input` 变 `messages`，输出取 `messages[-1]` |
| 2 | LCEL → `StateGraph` | 真正动结构，风险最大 |
| 3 | hook / 自定义逻辑收进 middleware | 前两步稳定后再做 |

两个迁移期的硬变化：流式节点名从 `agent` 变成 `model`（Python）/ `model_request`（JS），按节点名过滤的代码会失效；`InjectedState` / `InjectedStore` 统一收口到 `runtime: ToolRuntime`，`ToolException` / `handle_tool_error` 不再是 agent 路线的推荐入口。

三个反模式，面试里说出来很加分：

| 反模式 | 症状 | 更好的做法 |
|---|---|---|
| 为三个节点的线性流程画图 | 样板代码比业务多 | 普通函数或 LCEL |
| 所有状态塞一个 `dict` | 无 reducer、并行就炸 | 显式 schema + 按字段定 reducer |
| 用图来「保证 agent 聪明」 | 图跑通了，答案还是错 | 图只保证控制流，模型与提示词才是上限 |

---

## 十一、30 道高频面试题

答题模板统一四步：**定义 → 机制 → 边界 → 场景**。先给一句话结论，再展开机制，最后主动补一句「什么时候不适用」，比背长答案更像做过的。

### 11.1 概念辨析（Q1–Q8）

**Q1（★）LangGraph 是什么？它与 LangChain、Deep Agents 是什么关系？**

**答：** LangGraph 是 LangChain 生态的**运行时**，负责图、状态、持久化、中断与流式。LangChain v1 是构建块（`create_agent`、工具、中间件），Deep Agents 是建在 `create_agent` 之上的成品 harness。依赖是单向的：Deep Agents → `create_agent` → LangGraph 图。所以「用不用 LangGraph」不是选型问题，`create_agent` 编译出来本来就是图。

**Q2（★★）LangGraph 和 LCEL / Chain 的本质区别是什么？**

**答：** Chain 是**线性、无状态**的流水线，执行路径在定义时就定了；LangGraph 是**有状态、可循环**的图，支持条件分支、并行、中断恢复。区别不在「谁更高级」，而在控制流表达能力：Chain 表达不了「回到上一步」「等人审批」「按列表长度并行」。LCEL 在 v1 里仍然有用——它适合写在节点内部，负责一次模型调用或一次数据变换。

**Q3（★★）Graph API 和 Functional API 怎么选？**

**答：** 需要可视化、中断、子图、多 agent 时用 Graph API；逻辑本身就是一条函数链、或批处理脚本时用 Functional API。两者跑在同一套运行时上：`@entrypoint` 包入口、`@task` 包可并行/可重试的任务，`@entrypoint` 同样能挂 checkpointer 和 store。Functional 的代价是结构不可视，复杂分支会被写成嵌套函数。

**Q4（★）State、Node、Edge、超步分别是什么？**

**答：** State 是图共享的数据 schema；Node 是读 state、返回增量字典的函数；Edge 决定下一步去哪；超步（super-step）是「一轮里所有就绪节点同时执行、轮末统一结算」的调度单位。超步这个概念解释了两件事：`Send` 的多个分支在同一超步并行；检查点逐超步落盘。

**Q5（★★）什么是 reducer？默认行为是什么？**

**答：** reducer 决定「节点返回的更新怎么和旧值合并」，形式是 `new = reducer(old, update)`。字段不写 reducer 时默认**覆盖**；写 `Annotated[type, reducer]` 才是合并。最容易错的两点：顺序执行时「后写的赢」，但**同一超步的并行分支写无 reducer 字段会抛 `InvalidUpdateError`**（源码核对），不是随机覆盖。凡可能被并发写的字段，必须给 reducer。

**Q6（★★）`add_messages` 和普通 list 追加有什么区别？**

**答：** `add_messages` 是消息专用 reducer：除了追加，还会按消息 `id` 去重——同一个 `id` 再次出现是替换而不是重复追加（源码核对；示例只实测了追加）。它还接受 `BaseMessage`、dict、`(role, content)` 元组。普通 `operator.add` 没有 ID 语义，工具消息回写、消息修正时会越堆越多。JS 对应 `messagesStateReducer` / `MessagesAnnotation`。

**Q7（★★）`Overwrite` 解决什么问题？**

**答：** 它是合并型 reducer 的逃生舱。字段有 `operator.add` 时，返回 `[]` 清不掉——空列表会被拼上去，旧值还在；要写成 `{"log": Overwrite([])}` 才能强制覆盖（包了能清空是实测）。它只对合并型字段有意义，无 reducer 的字段本来就是覆盖。

**Q8（★★）checkpointer 和 store 有什么区别？**

**答：** checkpointer 按线程存**图状态快照**，用 `thread_id` 取，服务对话延续、HITL、时间旅行；store 跨线程存**应用键值数据**，节点里用 `runtime.store` 取，服务用户偏好、长期事实。判断口径：这次对话内记得 → checkpointer；换人换会话还记得 → store。两者不可互替。

### 11.2 机制原理（Q9–Q18）

**Q9（★★）条件边和 `Send` 有什么区别？**

**答：** 条件边是「选一条路」，路由函数返回节点名；`Send` 是「同时走多条路」，路由函数返回 `Send` 列表，LangGraph 为每一项起一个并行任务。`Send` 的 payload 是**目标节点的输入**，不是完整状态，所以 worker 读 `state["item"]` 而不是 `state["items"]`；并行结果必须靠目标字段的 reducer 汇总。静态扇入 `add_edge([a,b], "join")` 是编译期固定几路，`Send` 是运行期按数据长度动态派发，三者别混。

**Q10（★★）`Command` 有哪两种形态？为什么 `Command(goto=...)` 不能当输入？**

**答：** 一是节点内返回的 `Command(goto=..., update=...)`，同时更新状态和跳转；二是 `Command(resume=...)`，用来恢复 `interrupt()`。`goto` 依赖「当前节点刚执行完、控制权在谁手里」这个上下文，从外部 `invoke` 喂进去没有这个上下文；所以只有 `resume` 形态能当输入。JS 侧返回 `Command` 的节点要用 `ends` 声明去向（源码核对）。

**Q11（★★）子图怎么当节点？父子状态怎么共享？**

**答：** 编译好的图可以直接 `add_node`：Python 的 `create_agent` 返回 `CompiledStateGraph`，直接挂；JS 的 `createAgent` 返回包装对象，要取 `.graph`（实测）。父子 schema 里**同名的键共享通道**，字段对不上时要在父图节点里做映射。子图有独立的 `checkpoint_ns`，暂停态用 `get_state(cfg, subgraphs=True)` 下钻；流式要 `subgraphs=True` 才能看到内部 token。

**Q12（★★）`recursion_limit` 默认多少？超了报什么？怎么在节点里知道还剩几步？**

**答：** 本机 `langgraph` 1.2.12 的默认值是 **10007**（源码核对），但这个值随版本变，旧文档写过 1000、课程包在 1.1.2 量到 10000。超限抛 `GraphRecursionError`，报错里带当前 limit。生产代码永远显式传 `{"recursion_limit": N}`；JS 键名是 `recursionLimit`。Python 可以在状态里声明 `remaining_steps: RemainingSteps`（从 `langgraph.managed` 导入），节点里读到进入时剩余步数；JS 1.4.17 没有同名导出。

**Q13（★★）检查点什么时候落盘？`durability` 三档差在哪？**

**答：** 每个超步边界落一份完整状态快照。`durability` 决定「何时写」：`sync` 每步同步写、`async` 异步写（`invoke` 返回前补写）、`exit` 只在结束时写一次。本机默认 `async`；同一张两节点图实测历史快照数是 **4 / 4 / 1**。`exit` 中途崩溃会丢整段运行，故障恢复至少用 `async`；不配 checkpointer 时 `durability` 没有地方可写。

**Q14（★★）`thread_id`、`checkpoint_ns`、`checkpoint_id` 各定位什么？**

**答：** 三级定位：`thread_id` 定位哪条线程（对话身份证，必填）；`checkpoint_ns` 定位线程里的哪张图（顶层为空串，子图是 `child:<uuid>`）；`checkpoint_id` 定位哪一个快照（不传取最新）。`update_state` 能改写历史，正是因为它接收某个历史快照自带的 config。

**Q15（★★）`get_state`、`get_state_history`、`update_state` 分别做什么？时间旅行会改历史吗？**

**答：** `get_state` 看当前快照（`values` / `next` / `config` / `metadata` / `tasks`）；`get_state_history` 从新到旧翻历史（JS 是异步迭代器）；`update_state` 改写状态并返回**新分支**的 config。时间旅行**不改历史**，语义和 git 开分支一样：原线程一条不动，要接着新分支跑就用返回的 config 配 `invoke(None, forked)`。`next` 为空是判断「图是否停在半路」最可靠的信号。

**Q16（★★★）`interrupt` / `resume` 的完整流程与前置条件是什么？**

**答：** 节点里调 `interrupt(payload)`，LangGraph 抛特殊挂起异常、存检查点，第一次 `invoke` 的结果里多出 `__interrupt__`；人审完后用**同一个 `thread_id`** 调 `invoke(Command(resume=值), cfg)`，`interrupt()` 这次直接返回 resume 值。三个前置条件：图带 checkpointer、调用带 `thread_id`、payload 与 resume 值可序列化。`Command(resume=...)` 是唯一能当 `invoke` 输入的 `Command` 形态。

**Q17（★★★）为什么恢复时节点会从头重跑？由此推出哪些铁律？**

**答：** 检查点只落在超步边界，存得住「这一轮开始前的状态」，存不住「节点执行到第几行」。恢复时只能从上一个检查点把整个节点重跑，跑到 `interrupt()` 时发现断过、带回 resume 值，再继续。实测副作用日志会出现两次。四条铁律：不包 `try/except`、不重排节点内多个 `interrupt()`、不传复杂值、`interrupt()` 之前的副作用必须幂等。正解是把真副作用拆成独立节点放在 `interrupt()` 之后，而不是只靠幂等。

**Q18（★★★）`stream_mode` 七档分别是什么？list-mode 加 `subgraphs` 后分块长什么样？**

**答：** 七档是 `values` / `updates` / `messages` / `custom` / `checkpoints` / `tasks` / `debug`。`checkpoints` 需要 checkpointer，`tasks` 不需要（实测），`messages` 要求图里真有模型节点。list-mode 的分块是 Python `(mode, payload)`、JS `[mode, payload]`；再加 `subgraphs=True` 是 **`(namespace, mode, payload)` 三元组**（JS 三元素数组），**不是**「namespace 包着二元组」的嵌套形状（实测否定）。`namespace` 是 `("child:<uuid>",)` 这样的路径，父图为空元组。

### 11.3 排错与边界（Q19–Q25）

**Q19（★★）多轮对话记不住上文，怎么排查？**

**答：** 按顺序查四件事：① `compile` 有没有传 checkpointer；② 每次 `invoke` 有没有带同一个 `thread_id`；③ 换会话是不是换了 `thread_id`（换了就是白纸）；④ 用的是不是 `InMemorySaver`——进程重启就丢，生产要换 `PostgresSaver`。另外默认 `AgentState` 只有 `messages`，自定义字段要用 `state_schema` 扩展并想清 reducer，否则下一轮会被覆盖。

**Q20（★★）图跑起来报 `GraphRecursionError`，怎么办？**

**答：** 先分清是「循环没出口」还是「上限太小」。检查条件边是否在某个状态能返回 `END`，再显式传 `{"recursion_limit": N}`（JS `recursionLimit`）。不要靠调大默认值掩盖问题——默认值随版本变，本机是 10007。需要在节点内提前降级时，用 `RemainingSteps` 读剩余步数，剩得少就转人工或返回兜底答案。

**Q21（★★）给同步节点设 `timeout`，为什么 `compile()` 就报 `ValueError`？**

**答：** 因为 Python 无法安全取消同步执行，LangGraph 只对 **async 节点**支持超时。报错是 `Node timeouts are only supported for async nodes`（实测）。解法两条：把节点改成 `async`，或在节点内部自己做超时（例如给外部调用设超时）。`TimeoutPolicy` 也一样只适用于 async；JS 的 `timeout` 单位是毫秒。

**Q22（★★）父图流式看不到子 agent 的 token，为什么？**

**答：** agent 当节点后就是子图，而子图的内部输出默认不透传。父图 `stream` 要显式加 `subgraphs=True`，分块会变成三元组并带 namespace；不加时只剩跨边界的少数几条消息，表现就是「后端日志正常、前端打字机不动」。JS 侧还要确认挂的是 `agent.graph` 而不是包装对象。

**Q23（★★）`Send` 并行后结果互相覆盖，甚至抛 `InvalidUpdateError`，怎么修？**

**答：** 汇总字段没有 reducer。并行分支在同一个超步写同一个无 reducer 字段，会直接报 `Can receive only one value per step`（源码核对）。给字段加 `Annotated[list, operator.add]` 或自定义 reducer；同时确认 `Send` 的 payload 形状对——worker 读的是当次那一项，不是完整列表。

**Q24（★★★）审批通过后扣款扣了两次，怎么定位？**

**答：** 大概率是扣款写在 `interrupt()` 之前的同一个节点里：恢复时整个节点从头重跑，扣款代码执行了两次。修复不是加 `try/except`，而是把扣款拆成 `interrupt()` 之后的独立节点，让重跑只发生在审批节点；再给扣款接口带幂等键兜底。顺带检查有没有把 `interrupt()` 包进 `try/except`，那会让暂停直接失效。

**Q25（★★）`langgraph validate` 和 `langgraph dev` 为什么一个报「No such option」？**

**答：** 两个子命令的选项名不通用：`validate` 用 `-c`，`dev` 用 `--config`（本机实测踩过）。另外 Windows 上要先装 `colorama`，否则 `structlog` 的彩色渲染会在日志配置阶段崩；`python_version` 只接受 3.11/3.12/3.13，本地 `dev` 用当前解释器，不代表镜像能构建。

### 11.4 场景设计（Q26–Q30）

**Q26（★★★）设计一个带人工审批的退款 agent，你怎么落图？**

**答：** 节点拆成 `classify → draft → approval → refund → notify`，`approval` 里调 `interrupt()` 返回审批载荷，`refund` 放 `interrupt()` 之后，保证只执行一次。编译时挂 `PostgresSaver`，`thread_id` 用订单号；审批若走 `HumanInTheLoopMiddleware`，恢复用 `Command(resume={"decisions":[{"type":"approve"}]})`，自写 `interrupt()` 则 resume 自己约定的结构。再补三件事：退款接口带幂等键、外部调用配 `RetryPolicy`、整图显式 `recursion_limit` 并记录审批审计日志。

**Q27（★★★）100 个文档并行摘要再汇总，怎么画？**

**答：** 用 map-reduce：入口节点读文档列表，条件边返回 `[Send("worker", {"doc": d}) for d in docs]`，`worker` 每个文档一个任务、同一超步并行；汇总字段 `Annotated[list, operator.add]`，最后 `join` 节点统一生成报告。IO 密集时把 worker 写成 `async`，配 `RetryPolicy` 处理单篇失败。注意检查点会存下每一步状态，输入别塞整篇原文；量大时按批拆分，避免单个超步压力过大。

**Q28（★★）多智能体该选 supervisor、handoff 还是 swarm？**

**答：** 看控制权：需要多轮协调、干完要汇总 → supervisor（有中心、能收回）；一次分流、各管各的 → handoff（交棒不回头）；边界模糊、需要互相接力 → swarm，但必须先设计终止条件和最大转移次数。能用单 agent 解决就别拆：每多一层就多一份 token、延迟和排障成本，trace 也会更难读。

**Q29（★★★）上线前你会检查什么？**

**答：** 三查：检查点是否持久化（生产用 `PostgresSaver`，别用 `InMemorySaver`；中途换 saver 历史搬不过去）、有没有调用次数上限（`recursion_limit` + `ModelCallLimitMiddleware`）、高风险操作有没有 HITL。再补：关键流程 `durability="sync"`、密钥走平台 Secret、观测接 trace、`langgraph.json` 的 `graphs` 指向编译好的图。最后明确边界：Studio、AgentChatUI、Docker、云端部署本机都未实测。

**Q30（★★）什么时候不该用 LangGraph？**

**答：** 四种情况：线性无状态流程（普通函数或 LCEL 就够）、单 agent 工具循环（`create_agent` 已内置）、长周期文件/子代理/技能场景（Deep Agents 更省事）、团队还没有图的心智模型（先用小图，别一上来多智能体）。图只保证控制流可控，不保证答案正确；模型、提示词、检索质量仍是上限。

---

## 十二、避坑指南

下面这些坑按「症状 → 根因 → 正确做法」记，比背 API 有用。

### 12.1 二十条高频坑

| # | 症状 | 根因 | 正确做法 |
|---|---|---|---|
| 1 | 两个节点写同一字段，前一个值没了 | 默认 reducer 是覆盖 | 要合并就写 `Annotated[type, reducer]` |
| 2 | 并行分支跑起来抛 `InvalidUpdateError` | 同一超步写无 reducer 字段 | 给字段加 reducer，或改成串行 |
| 3 | 追加型字段清空失败 | `[]` 被 reducer 拼上去 | `Overwrite([])` |
| 4 | `invoke(None)` 没反应 | 已跑完的线程无待执行任务 | 续跑用 `invoke({})`，重放用新分支 config |
| 5 | 同一线程第二轮标量被重置 | 输入里的字段按 reducer 覆盖了检查点 | 不想动状态就传 `{}` |
| 6 | 循环跑飞、账单暴涨 | 没有出口或 `recursion_limit` 太大 | 条件边保 `END`，显式传 limit |
| 7 | 同步节点设 timeout 编译失败 | 超时只支持 async 节点 | 改 async 或节点内自控超时 |
| 8 | 生产环境会话随机丢失 | 用了 `InMemorySaver` | 换 `PostgresSaver`，项目早期定方案 |
| 9 | 崩溃后整段重跑 | `durability="exit"` | 关键流程用 `sync`，至少 `async` |
| 10 | 审批后副作用执行两次 | 恢复时整个节点从头重跑 | 副作用拆到 `interrupt()` 之后的独立节点 |
| 11 | 中断完全没生效 | `interrupt()` 被 `try/except` 吞了 | 不包，或原样重抛 |
| 12 | 恢复后拿到错误的 resume 值 | 节点内多个 `interrupt()` 顺序被改 | 保持调用顺序稳定 |
| 13 | 父图流式没有 token | 子图内部输出默认不透传 | `subgraphs=True`；JS 挂 `.graph` |
| 14 | 解析流式分块时报错 | 按嵌套二元组解包 | list+subgraphs 是三元组 |
| 15 | JS 端等不到逐 token | `agent.streamEvents` 只出 start/end | 用 `agent.stream({streamMode:"messages"})` |
| 16 | JS 返回 `Command` 编译报错 | 没声明可能去向 | `addNode(name, fn, { ends: [...] })` |
| 17 | `validate` 报 `No such option: -c` | 和 `dev` 的选项混用 | `validate -c`、`dev --config` |
| 18 | Store 搜出一堆无关数据 | `search` 是前缀匹配 | 命名空间写细，别当精确查询 |
| 19 | 换 saver 后历史全没了 | 存储结构不同，搬不过去 | 上线前定死持久化后端 |
| 20 | 按节点名过滤流式事件失效 | v1 节点名变了 | Python `model`、JS `model_request`，别硬编码 |

三条最值得写成代码的改法：

```python
# ① 清空合并型字段
return {"log": Overwrite([])}

# ② 并行汇总字段必须有 reducer
class Fan(TypedDict):
    items: list[str]
    results: Annotated[list[str], operator.add]

# ③ list + subgraphs 按三元组解包
for ns, mode, payload in app.stream(inp, cfg, stream_mode=["updates"], subgraphs=True):
    print(ns, mode, payload)
```

---

## 十三、本章学习自检

能勾掉下面八成，LangGraph 的面试基本不会翻车。

### 13.1 定位与选型

- [ ] 能一句话说清 LangGraph 是「运行时」，并画出 LangChain / LangGraph / Deep Agents 的依赖方向
- [ ] 能说出 `create_agent` 编译产物就是 LangGraph 图
- [ ] 能对比 Graph API 与 Functional API，并各举一个适用场景
- [ ] 能说出三种「不该用 LangGraph」的情况

### 13.2 状态与 reducer

- [ ] 能解释默认 reducer 是覆盖，`Annotated` 才是合并
- [ ] 能说出并行写无 reducer 字段会抛 `InvalidUpdateError`
- [ ] 能解释 `add_messages` 的追加与按 ID 替换，以及为什么不用普通 list
- [ ] 能用 `Overwrite` 清空合并型字段
- [ ] 能背出同线程 `invoke` 的 `None` / `{}` 区别与三条合并结论

### 13.3 控制流

- [ ] 能区分条件边、`Send`、静态扇入、`add_sequence`、`Command`
- [ ] 能解释超步与「轮末统一结算」
- [ ] 知道 `Send` 的 payload 是目标节点输入，汇总靠 reducer
- [ ] 知道 `Command(goto)` 只能在节点内返回，`Command(resume)` 才能当输入
- [ ] 能说出本机 `recursion_limit` 默认 10007 且随版本变，JS 键名是 `recursionLimit`

### 13.4 持久化

- [ ] 能对比 checkpointer 与 store，并各举两个用途
- [ ] 能解释 `thread_id` / `checkpoint_ns` / `checkpoint_id` 三级定位
- [ ] 能说出 `get_state` / `get_state_history` / `update_state` 的返回与用途
- [ ] 能解释时间旅行是开分支、不改历史
- [ ] 能说出 `durability` 三档与 4 / 4 / 1，默认是 `async`
- [ ] 知道子图有独立 `checkpoint_ns`，`get_state_history` 没有 `subgraphs` 参数

### 13.5 HITL 与流式

- [ ] 能完整走一遍 `interrupt` → `__interrupt__` → `Command(resume=...)`
- [ ] 能说出三个前置条件与四条铁律
- [ ] 能解释「恢复时整个节点从头重跑」的原因
- [ ] 知道静态中断只适合调试
- [ ] 能说出七档 `stream_mode` 与各自前置条件
- [ ] 能写出 list + subgraphs 的三元组解包
- [ ] 知道 JS agent 级 `streamEvents` 只出 start/end

### 13.6 治理、多智能体与部署

- [ ] 能说出 `RetryPolicy` / `timeout` / `CachePolicy` 各自边界（尤其 timeout 仅 async）
- [ ] 能对比 supervisor / handoff / swarm 的控制权流动
- [ ] 知道 swarm 只讲机制、没有可运行示例
- [ ] 能写出 `langgraph.json` 的最小清单与 `validate -c` / `dev --config`
- [ ] 能明确说出 Studio / AgentChatUI / Docker / 云端**未实测**
- [ ] 能背出上线三查：持久化、调用上限、高风险 HITL

最后用三句话收束本章：

1. **LangGraph 的核心不是「图」这个画法，而是「状态怎么合、控制权怎么流、状态存在哪」。**
2. **所有 HITL 的坑都源于一件事：检查点只落在超步边界，所以恢复时节点从头重跑。**
3. **图只保证控制流可控；答案对不对，仍取决于模型、提示词与检索质量。**
