# LangGraph核心机制与面试要点 导览

> 定位：五维框架浓缩提炼 05-LangGraph核心机制与面试要点.md 的机制结论与 30 道面试题，供面试前快速复盘。
> 用法：每个内容小节对应一张纵向表格；需要代码、完整答案与口径标记时跳转 [原文](./05-LangGraph核心机制与面试要点.md)。
> 前置知识：[LangChain与AI智能体核心](./02-LangChain与AI智能体核心-导览.md)、[Python核心语法速通](../python-core/01-Python核心语法速通-导览.md)

---

## 目录

本节为辅助内容，无五维表格

---

## 一、LangGraph 的定位与边界

### 1.1 三件套中的位置与边界

| 维度 | 内容 |
|------|------|
| 是什么 | LangChain 生态里的运行时：负责图、状态、持久化、中断与流式；上与 LangChain 构建块、Deep Agents 成品 harness 分层。 |
| 能做什么 | 画有状态图；做条件分支、循环、并行；挂检查点；中断恢复；把执行过程投影成流。 |
| 怎么用 | `StateGraph` 定义图并 `compile(checkpointer=...)`；`create_agent` 的产物本身就可当图或子图使用。 |
| 原理和工作流程 | 依赖单向：Deep Agents → `create_agent` → LangGraph 图；`create_agent` 编译出来的就是图，所以「用不用 LangGraph」不是选型问题。 |
| 缺点 | 概念与样板代码多；线性流程用它是过度设计；旧教程的 0.x API 与 v1 对不上。 |

### 1.2 Graph API、Functional API 与版本

| 维度 | 内容 |
|------|------|
| 是什么 | 同一运行时的两种写法，以及 v1 的导入路径约定。 |
| 能做什么 | Graph 画分支、循环、子图；Functional 用 `@entrypoint` / `@task` 写函数链；两者都能挂 checkpointer 与 store。 |
| 怎么用 | `StateGraph(State).add_node(...).compile()`；`@task` 配合 `.result()`；导入按 `langgraph.graph` / `langgraph.types` / `langgraph.checkpoint.memory` 等路径。 |
| 原理和工作流程 | 两种写法最终都落到同一套图运行时；Graph 显式建节点与边，Functional 把函数调用转成任务图；v1 把 agent 构建上移到 `langchain.agents.create_agent`。 |
| 缺点 | Graph 样板多；Functional 结构不可视、复杂控制流难表达；`MemorySaver`、`create_react_agent` 等旧路径容易误导。 |

---

## 二、StateGraph：状态、Reducer 与合并语义

### 2.1 State schema 与 reducer

| 维度 | 内容 |
|------|------|
| 是什么 | schema 定义图共享的字段；reducer 定义节点更新如何与旧值合并，默认是覆盖。 |
| 能做什么 | 用 TypedDict、dataclass、Pydantic 描述状态；用 `Annotated[type, reducer]` 做追加或自定义合并。 |
| 怎么用 | `class State(TypedDict)`；`log: Annotated[list, operator.add]`；节点返回增量 dict，由 `compile()` 后的图运行。 |
| 原理和工作流程 | 每个超步结束时对每个字段调 `reducer(old, update)`；无 reducer 取后写值；并行分支写同一无 reducer 字段会抛 `InvalidUpdateError`（源码核对）。 |
| 缺点 | 默认覆盖容易丢数据；schema 变更影响所有节点；并行写同键的报错要到运行期才暴露。 |

### 2.2 `add_messages` 与 `Overwrite`

| 维度 | 内容 |
|------|------|
| 是什么 | 消息专用 reducer 与「强制覆盖」指令。 |
| 能做什么 | 追加消息并按 `id` 替换（源码核对）；用 `Overwrite([])` 清空追加型字段。 |
| 怎么用 | `messages: Annotated[list, add_messages]`；清空写 `return {"log": Overwrite([])}`。 |
| 原理和工作流程 | `add_messages` 按消息 ID 去重更新；`Overwrite` 绕过 reducer 直接写入；普通空列表会被 `operator.add` 拼接，旧值仍在。 |
| 缺点 | 同 ID 替换行为未实测；`Overwrite` 只对合并型字段有意义；JS 普通 `concat` 不等价于 `messagesStateReducer`。 |

### 2.3 同一线程再次 `invoke`

| 维度 | 内容 |
|------|------|
| 是什么 | 带 checkpointer 时，同一 `thread_id` 的多次 `invoke` 如何把输入合进检查点状态。 |
| 能做什么 | 续跑、空操作、覆盖标量字段、追加列表字段；本机实测 `n` 走 1 → 1 → 2 → 101 → 102。 |
| 怎么用 | `invoke({}, cfg)` 续跑；`invoke(None, cfg)` 空操作；`invoke({"n": 100}, cfg)` 覆盖后再执行。 |
| 原理和工作流程 | 输入里出现的字段按各自 reducer 合并，没出现的保留检查点值；`None` 不注入输入，`{}` 注入空输入。 |
| 缺点 | 标量字段会被输入悄悄重置；`None` 与 `{}` 极易混；没有 checkpointer 时三条结论全部不成立。 |

---

## 三、控制流：节点、边与并行原语

### 3.1 节点、边、条件边与超步

| 维度 | 内容 |
|------|------|
| 是什么 | 图的基本执行单元（节点）、流转规则（边）与调度单位（超步）。 |
| 能做什么 | 顺序执行、条件分支、循环回边；一轮内所有就绪节点并行执行。 |
| 怎么用 | `add_node`、`add_edge`、`add_conditional_edges`；路由函数返回节点名或 `END`。 |
| 原理和工作流程 | 图按超步推进：所有就绪节点同轮执行，轮末统一用 reducer 结算，再进入下一轮；检查点也按超步落。 |
| 缺点 | 条件边写错会死循环或提前结束；不熟超步就解释不清并行与检查点粒度。 |

### 3.2 `Send`

| 维度 | 内容 |
|------|------|
| 是什么 | 运行期按数据长度派发 N 路并行的原语，适合 map-reduce。 |
| 能做什么 | 一个列表拆成多个任务同超步执行，再用字段 reducer 汇总结果。 |
| 怎么用 | 路由函数返回 `[Send("worker", {"item": it}) for it in state["items"]]`。 |
| 原理和工作流程 | 每个 `Send` 生成一个目标任务，payload 作为目标节点输入；并行写入靠目标字段的 reducer 汇总。 |
| 缺点 | payload 不是完整状态，容易读错键；汇总字段无 reducer 会覆盖或报错；动态并行难预估资源。 |

### 3.3 `Command`、子图、`add_sequence` 与循环

| 维度 | 内容 |
|------|------|
| 是什么 | 节点内更新加跳转、编译图当节点、固定顺序、循环上限四类控制流设施。 |
| 能做什么 | handoff、动态路由、复用子流程、线性链、给循环踩刹车。 |
| 怎么用 | `Command(goto=..., update=...)`；Python 直接 `add_node` 子图，JS 取 `.graph`；`add_sequence([a,b])`；`{"recursion_limit": N}`。 |
| 原理和工作流程 | `Command` 在节点内返回控制权；子图是父图的一次 task，有独立 `checkpoint_ns`；循环按超步计数，超限抛 `GraphRecursionError`，Python 可用 `RemainingSteps` 读剩余步数。 |
| 缺点 | `Command(goto)` 不能当输入；子图流式默认不透传；`add_sequence` 不接 `START`/`END`；默认 limit 随版本变（本机 10007）。 |

---

## 四、持久化：checkpointer、store 与时间旅行

### 4.1 checkpointer 与 store

| 维度 | 内容 |
|------|------|
| 是什么 | 两套互补的持久化系统：线程内的图状态快照，与跨线程的键值存储。 |
| 能做什么 | 多轮记忆、HITL、时间旅行、故障恢复；用户偏好、长期事实、共享知识。 |
| 怎么用 | `compile(checkpointer=...)` 配 `thread_id`；`compile(store=...)` 后在节点里用 `runtime.store`。 |
| 原理和工作流程 | checkpointer 逐超步存图快照；store 按命名空间、键、dict 值存数据；两者作用范围与隔离方式不同。 |
| 缺点 | 选错层会丢记忆或增加检索噪声；两套都要自己接后端；store 的值必须是 dict。 |

### 4.2 三级定位与三个方法

| 维度 | 内容 |
|------|------|
| 是什么 | `thread_id` / `checkpoint_ns` / `checkpoint_id` 三级定位，以及 `get_state` / `get_state_history` / `update_state`。 |
| 能做什么 | 定位线程、图、快照；看当前状态、翻历史、改写状态并开新分支。 |
| 怎么用 | `config={"configurable": {"thread_id": ...}}`；`snap.next` 判断是否跑完；`update_state` 返回新 config 后用 `invoke(None, forked)` 重放。 |
| 原理和工作流程 | 快照按超步落盘；`next` 是待执行节点；`update_state` 从历史快照的 config 新建分支，原线程历史不动。 |
| 缺点 | JS 的 `getStateHistory` 是异步迭代器；`next` 为空容易被误判为失败；时间旅行必须用新 config 才生效。 |

### 4.3 子图持久化、`durability` 与内置实现

| 维度 | 内容 |
|------|------|
| 是什么 | 子图的独立命名空间、三档落盘时机，以及 InMemory/Sqlite/Postgres 三种 saver。 |
| 能做什么 | 暂停态下钻子图；按 `sync`/`async`/`exit` 控制写入；开发、单机、生产各选一种后端。 |
| 怎么用 | `get_state(cfg, subgraphs=True)` 读 `tasks[].state`；`invoke(..., durability="sync")`；`PostgresSaver` 接生产。 |
| 原理和工作流程 | 子图 `checkpoint_ns` 为 `child:<uuid>`；`sync` 每步写、`async` 异步补写（默认）、`exit` 结束写一次，两节点图实测 4 / 4 / 1。 |
| 缺点 | 跑完后 `tasks` 为空；`get_state_history` 没有 `subgraphs` 参数；`exit` 崩溃丢整段；换 saver 搬不了历史。 |

---

## 五、interrupt 与 resume：人在回路

### 5.1 一次往返与三个前置条件

| 维度 | 内容 |
|------|------|
| 是什么 | 节点内暂停、外部恢复的人在回路原语。 |
| 能做什么 | 审批、补充信息、人工纠错；第一次 `invoke` 返回 `__interrupt__` 载荷。 |
| 怎么用 | 节点里 `interrupt(payload)`；用同一 `thread_id` 调 `invoke(Command(resume=值), cfg)`。 |
| 原理和工作流程 | `interrupt` 抛特殊挂起异常并落检查点；恢复时 `interrupt()` 直接返回 resume 值；前置为 checkpointer、`thread_id`、可序列化 payload。 |
| 缺点 | 缺任一前置就失效；payload 不能带对象或句柄；换线程恢复会被当成第一次执行。 |

### 5.2 重跑与四条铁律

| 维度 | 内容 |
|------|------|
| 是什么 | 恢复时整个节点从头执行的机制，以及由此产生的四条约束。 |
| 能做什么 | 解释副作用为何重复；指导把真副作用拆成独立节点。 |
| 怎么用 | 副作用放 `interrupt()` 之后；不包 `try/except`、不重排中断、不传复杂值、之前副作用幂等。 |
| 原理和工作流程 | 检查点只落在超步边界，存不住节点行号；恢复只能从上一个检查点重跑节点，跑到 `interrupt()` 时取回 resume 值。 |
| 缺点 | 重跑会重复日志与外部调用；违反铁律后表现为难查的玄学 bug；拆节点会增加图复杂度。 |

### 5.3 静态中断与工具级审批

| 维度 | 内容 |
|------|------|
| 是什么 | 编译期在节点边界暂停，以及中间件封装的工具调用审批。 |
| 能做什么 | 调试时观察中间状态；工具执行前做 approve / edit / reject / respond。 |
| 怎么用 | `compile(interrupt_before=[...])`；`HumanInTheLoopMiddleware(interrupt_on=...)`；`Command(resume={"decisions": [...]})`。 |
| 原理和工作流程 | 静态中断在节点边界停；中间件把 `interrupt` 包在工具调用前，`decisions` 与 `action_requests` 一一对应。 |
| 缺点 | 静态中断拿不到结构化人工输入，只适合调试；JS 无 `respond`；`decisions` 数量不匹配抛 `ValueError`。 |

---

## 六、流式：七档 `stream_mode` 与事件流

### 6.1 七档投影

| 维度 | 内容 |
|------|------|
| 是什么 | 同一次执行的七种观察方式：`values` / `updates` / `messages` / `custom` / `checkpoints` / `tasks` / `debug`。 |
| 能做什么 | 看完整状态、增量、token、业务进度、检查点、任务事件与排障信息。 |
| 怎么用 | `stream(..., stream_mode="messages")`；可传列表；`custom` 档用 `get_stream_writer()` 主动推。 |
| 原理和工作流程 | 每档从执行事件中投影不同字段；`checkpoints` 需要 checkpointer，`tasks` 不需要，`messages` 要求图里有模型节点。 |
| 缺点 | 档位语义易混；分块数随模型与版本变，不能拿来断言；`debug` 信息多而杂。 |

### 6.2 分块形状与子图透传

| 维度 | 内容 |
|------|------|
| 是什么 | 单档、list-mode、加 `subgraphs` 时的分块形状，以及子图消息的可见性。 |
| 能做什么 | 正确解包 `(mode, payload)` 与 `(namespace, mode, payload)`；用 `subgraphs=True` 恢复子图 token。 |
| 怎么用 | `for ns, mode, payload in app.stream(..., subgraphs=True)`；`ns[0].split(":")[0]` 判断来源。 |
| 原理和工作流程 | 子图内部输出默认不上传；加 `subgraphs` 后分块带命名空间路径，父图为空元组。 |
| 缺点 | 「namespace 包着二元组」的嵌套写法不成立；不加 `subgraphs` 前端没有打字机；工具消息仍可能不透出。 |

### 6.3 `astream_events`

| 维度 | 内容 |
|------|------|
| 是什么 | 按回调事件而非状态投影的流式接口。 |
| 能做什么 | 看模型 token、工具开始 / 结束、链的嵌套关系，按事件名分流。 |
| 怎么用 | Python `agent.astream_events(inp, version="v2")`；JS 逐 token 用 `agent.stream({streamMode: "messages"})`。 |
| 原理和工作流程 | 事件来自回调系统；`on_chat_model_stream` 要求模型走流式路径，假模型需实现 `_astream`；事件可能重复。 |
| 缺点 | JS agent 级 `streamEvents` 在 1.4.17 只出 start/end；模型未走流式时没有 token 事件；不能按事件条数断言。 |

---

## 七、节点级治理：重试、超时与缓存

### 7.1 `RetryPolicy`

| 维度 | 内容 |
|------|------|
| 是什么 | 挂在节点上的失败重试策略。 |
| 能做什么 | 指定最大尝试次数、触发重试的异常类型、退避间隔。 |
| 怎么用 | `add_node("flaky", flaky, retry_policy=RetryPolicy(max_attempts=3, retry_on=ValueError))`。 |
| 原理和工作流程 | 节点抛出指定异常时按策略重跑；Python 默认 3 次、初始间隔 0.5 秒，JS 间隔单位是毫秒。 |
| 缺点 | 非幂等操作重试会重复副作用；两语言单位差 1000 倍；重试耗尽后仍需兜底。 |

### 7.2 超时、缓存与兜底

| 维度 | 内容 |
|------|------|
| 是什么 | 节点级 `timeout`、`CachePolicy` 与 `error_handler`。 |
| 能做什么 | 限制 async 节点时长；纯节点同输入复用结果；重试耗尽后接管错误。 |
| 怎么用 | `timeout=0.05`（仅 async）；`cache_policy=CachePolicy(ttl=60)` 配 `compile(cache=InMemoryCache())`。 |
| 原理和工作流程 | 超时通过取消 async 任务实现；缓存以节点输入为键、TTL 按秒；`error_handler` 在重试耗尽后执行。 |
| 缺点 | 同步节点设 timeout 编译抛 `ValueError`；有副作用节点开缓存会跳过真实执行；`error_handler` 仅源码核对。 |

---

## 八、多智能体拓扑：supervisor、handoff 与 swarm

### 8.1 三种拓扑

| 维度 | 内容 |
|------|------|
| 是什么 | 按「控制权怎么流」划分的三种多智能体结构。 |
| 能做什么 | supervisor 中心调度并收回；handoff 一次交棒不回头；swarm 无中心互相转移。 |
| 怎么用 | supervisor 用条件边加回边；handoff 用 `Command(goto=...)`；swarm 需先设计终止条件与最大转移次数。 |
| 原理和工作流程 | 差别只在是否有中心、交出去能否收回；agent 当节点后就是子图，流式要 `subgraphs=True`。 |
| 缺点 | supervisor 有单点与瓶颈；handoff 交错了没人兜底；swarm 最易转圈；成本与排障难度成倍。 |

### 8.2 选型与工程细节

| 维度 | 内容 |
|------|------|
| 是什么 | 拓扑选择判据与落地注意事项。 |
| 能做什么 | 按协调轮次与分流方式选型；给每个 agent 命名；控制流式透传。 |
| 怎么用 | 多轮协调选 supervisor，一次分流选 handoff，边界模糊选 swarm 并加终止条件。 |
| 原理和工作流程 | 每多一层 agent 就多一轮模型调用与状态；trace 里靠 `name` 区分是哪一路在跑。 |
| 缺点 | 单 agent 够用时拆多智能体是负收益；swarm 没有可运行示例；真实模型调度质量未实测。 |

---

## 九、部署：`langgraph.json` 与本地 Agent Server

### 9.1 部署清单与命令

| 维度 | 内容 |
|------|------|
| 是什么 | `langgraph.json` 部署清单，以及 `langgraph validate` / `dev` 两个本地命令。 |
| 能做什么 | 声明依赖、图入口、环境变量、Python 版本；在本地起一个内存版 Agent Server。 |
| 怎么用 | `{"dependencies": ["."], "graphs": {"agent": "./x.py:graph"}}`；`validate -c`；`dev --config`；`curl /ok`。 |
| 原理和工作流程 | CLI 按清单导入编译好的图，起 `langgraph-runtime-inmem` 服务；`/ok` 返回 200 即就绪。 |
| 缺点 | `validate` 与 `dev` 选项名不通用；Windows 需装 `colorama`；`python_version` 只接受 3.11–3.13。 |

### 9.2 未实测边界与上线三查

| 维度 | 内容 |
|------|------|
| 是什么 | 本地验证覆盖到哪里，以及上线前必须确认的三件事。 |
| 能做什么 | 明确 Studio、AgentChatUI、Docker、云端未实测；检查持久化、调用上限、高风险 HITL。 |
| 怎么用 | 本地只验证 `/ok` 与图导入；生产换 `PostgresSaver`、设 `recursion_limit`、接审批流。 |
| 原理和工作流程 | 托管平台接管持久化与 UI，自托管要自己接后端；部署换的是接线，不是 agent 逻辑。 |
| 缺点 | 平台侧未验证；`InMemorySaver` 上生产会丢会话；中途换 saver 搬不了历史。 |

---

## 十、选型：什么时候用 LangGraph

### 10.1 选型决策

| 维度 | 内容 |
|------|------|
| 是什么 | 在 LCEL、`create_agent`、LangGraph、Deep Agents 之间选择的判据。 |
| 能做什么 | 线性流程用 LCEL；单 agent 用 `create_agent`；复杂控制流用 LangGraph；长周期用 Deep Agents。 |
| 怎么用 | 先看流程形状，再看状态与中断需求，最后看团队维护成本。 |
| 原理和工作流程 | 复杂度与表达能力匹配；`create_agent` 的循环形状固定，中间件只能挂钩子、改不了形状。 |
| 缺点 | 过度设计增加样板；选错层会重复造轮子；图只保证控制流，不保证答案质量。 |

### 10.2 迁移与反模式

| 维度 | 内容 |
|------|------|
| 是什么 | 从 `AgentExecutor` / LCEL 迁到 v1 的路径与常见反模式。 |
| 能做什么 | 三步迁移；识别「线性也画图」「所有状态塞一个 dict」「用图代替提示词优化」等问题。 |
| 怎么用 | 先换 `create_agent`，再改 `StateGraph`，最后把横切逻辑收进 middleware。 |
| 原理和工作流程 | 输入从 `input` 变 `messages`，输出取 `messages[-1]`，流式节点名变 `model`（Python）/ `model_request`（JS）。 |
| 缺点 | 第一步不是行为等价；一次全改难定位问题；旧 hook 与注入方式要重写。 |

---

## 十一、30 道高频面试题

### 11.1 题目分布与答法

| 维度 | 内容 |
|------|------|
| 是什么 | 30 道按概念、机制、排错、场景四组组织的面试题，配「定义 → 机制 → 边界 → 场景」四步答法。 |
| 能做什么 | 覆盖定位、状态、控制流、持久化、HITL、流式、治理、拓扑、部署、选型十块。 |
| 怎么用 | 先给一句话结论，再展开机制，主动补边界，最后落到一个具体场景。 |
| 原理和工作流程 | 题目按「会被追问的机制」组织；答案保留实测、源码核对、未实测的口径，避免把推断说成跑过。 |
| 缺点 | 速查表只给一句话，完整答案要看原文；真实面试的追问无法预设。 |

### 11.2 概念题速查（Q1–Q8）

| 题号 | 考点 | 一句话答案 |
|------|------|-----------|
| Q1 | LangGraph 定位 | LangChain 生态的运行时；依赖链是 Deep Agents → `create_agent` → 图。 |
| Q2 | 与 Chain / LCEL 的区别 | Chain 线性无状态，LangGraph 有状态可循环；LCEL 仍可写在节点内部。 |
| Q3 | Graph 与 Functional | 要可视化、中断、子图用 Graph；一条函数链用 Functional。 |
| Q4 | State / Node / Edge / 超步 | 超步是一轮就绪节点同执行、轮末统一结算的调度单位。 |
| Q5 | reducer | 默认覆盖；`Annotated` 才合并；并行写无 reducer 字段报 `InvalidUpdateError`。 |
| Q6 | `add_messages` | 追加 + 按 ID 替换（源码核对）；普通 list 没有 ID 语义。 |
| Q7 | `Overwrite` | 合并型字段的逃生舱；返回 `[]` 清不掉，要包 `Overwrite`。 |
| Q8 | checkpointer 与 store | 线程内图状态 vs 跨线程键值；前者管对话，后者管用户。 |

### 11.3 机制题速查（Q9–Q18）

| 题号 | 考点 | 一句话答案 |
|------|------|-----------|
| Q9 | 条件边与 `Send` | 选一条路 vs 同超步派发 N 路；payload 是目标节点输入，汇总靠 reducer。 |
| Q10 | `Command` 两形态 | `goto` 只能在节点内返回，`resume` 才能当输入；JS 要声明 `ends`。 |
| Q11 | 子图当节点 | Python 直接挂，JS 取 `.graph`；同名键共享通道，子图有独立 `checkpoint_ns`。 |
| Q12 | `recursion_limit` | 本机默认 10007 且随版本变；超限抛 `GraphRecursionError`；Python 用 `RemainingSteps`。 |
| Q13 | 检查点与 durability | 逐超步落盘；`sync` / `async`（默认）/ `exit`，实测快照数 4 / 4 / 1。 |
| Q14 | 三级定位 | `thread_id` 哪条线程、`checkpoint_ns` 哪张图、`checkpoint_id` 哪个快照。 |
| Q15 | 三个状态方法 | `get_state` 看当前、`get_state_history` 翻历史、`update_state` 开新分支。 |
| Q16 | interrupt 往返 | 第一次返回 `__interrupt__`，同一线程用 `Command(resume=值)` 恢复。 |
| Q17 | 恢复为何重跑 | 检查点只在超步边界；整个节点重跑，故有四条铁律。 |
| Q18 | 七档与分块形状 | 七档投影；list-mode 是二元组，加 `subgraphs` 是三元组。 |

### 11.4 排错与场景速查（Q19–Q30）

| 题号 | 考点 | 一句话答案 |
|------|------|-----------|
| Q19 | 多轮失忆 | 查 checkpointer、`thread_id`、是否用了 `InMemorySaver`、状态 schema 是否含消息。 |
| Q20 | `GraphRecursionError` | 先补循环出口，再显式设 limit；别靠调大默认值掩盖。 |
| Q21 | 同步节点 timeout | 只支持 async；改 async 或节点内自控超时。 |
| Q22 | 子图没有 token | 加 `subgraphs=True`；JS 确认挂的是 `.graph`。 |
| Q23 | `Send` 结果覆盖 | 汇总字段缺 reducer；补 `operator.add` 或自定义 reducer。 |
| Q24 | 扣款执行两次 | 副作用写在 `interrupt()` 之前；拆到独立节点并加幂等键。 |
| Q25 | validate / dev 报错 | `validate -c`、`dev --config`；Windows 装 `colorama`。 |
| Q26 | 退款审批设计 | classify → draft → approval(interrupt) → refund → notify；PostgresSaver + 幂等键。 |
| Q27 | 100 文档并行 | `Send` 派发 worker，`operator.add` 汇总，`join` 生成报告。 |
| Q28 | 拓扑选择 | 多轮协调 supervisor、一次分流 handoff、边界模糊 swarm 加终止条件。 |
| Q29 | 上线检查 | 持久化、调用上限、高风险 HITL；平台侧未实测。 |
| Q30 | 何时不用 | 线性流程、单 agent、长周期成品、团队无图经验，都不必上 LangGraph。 |

---

## 十二、避坑指南

### 12.1 症状、根因与正确做法

| 维度 | 内容 |
|------|------|
| 是什么 | 20 条按「症状 → 根因 → 正确做法」整理的高频坑。 |
| 能做什么 | 快速定位 reducer、持久化、中断、流式、部署五类问题。 |
| 怎么用 | 先按症状查表，再回原文看对应代码改法。 |
| 原理和工作流程 | 多数坑源于默认覆盖、检查点只在超步边界、子图默认不透传、CLI 选项不通用。 |
| 缺点 | 只列高频，不覆盖版本特例；同一症状可能多因，仍需日志与快照辅助。 |

---

## 十三、本章学习自检

### 13.1 自检清单怎么用

| 维度 | 内容 |
|------|------|
| 是什么 | 按定位、状态、控制流、持久化、HITL 与流式、治理与部署六组列出的自检项。 |
| 能做什么 | 定位薄弱环节；面试前用十分钟过一遍。 |
| 怎么用 | 能勾掉八成即可；勾不掉的项回到对应章节重读。 |
| 原理和工作流程 | 自检项与正文机制一一对应，覆盖概念、边界、代码三层，而不是只背名词。 |
| 缺点 | 自检不能替代真机调试；平台侧与真实模型行为不在清单覆盖范围内。 |

---

> [返回原文](./05-LangGraph核心机制与面试要点.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
