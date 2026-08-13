# LangChain与AI智能体核心 导览

> 定位：五维框架浓缩提炼 02-LangChain与AI智能体核心.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-LangChain与AI智能体核心.md)。
> 前置知识：[Python核心语法速通](../python-core/01-Python核心语法速通-导览.md)、大语言模型基本概念

---

## 目录

本节为辅助内容，无五维表格

---

## 一、AI Agent基础概念

### 1.1 什么是AI智能体

| 维度 | 内容 |
|------|------|
| 是什么 | 以LLM为大脑、能感知环境做出决策并执行动作的自主系统。 |
| 能做什么 | 自主决策；感知环境变化；目标分解推进；调用工具与外部系统交互。 |
| 怎么用 | LLM + Tool + Memory 组合构建，如 LangChain AgentExecutor。 |
| 原理和工作流程 | 以LLM作为推理核心，结合记忆保存上下文、规划模块分解任务、工具调用与外界交互，形成感知-决策-执行的闭环，围绕目标逐步推进直至完成。 |
| 缺点 | 强依赖LLM能力与提示质量，决策可能出错；工具调用失败或幻觉会导致错误动作；token消耗大成本高。 |

---

### 1.2 感知-决策-执行循环

| 维度 | 内容 |
|------|------|
| 是什么 | AI Agent运行时不断重复感知、决策、执行三阶段的核心循环过程。 |
| 能做什么 | 接收输入读取状态；思考下一步动作；调用工具执行；更新状态继续循环。 |
| 怎么用 | 感知用Memory/Retriever；决策用LLM/Planning；执行用Tool/AgentExecutor。 |
| 原理和工作流程 | 感知阶段读取用户输入与记忆上下文，决策阶段LLM基于状态与目标推理下一步，执行阶段调用工具获得结果并写回状态，循环往复直到达成目标或达到步数上限。 |
| 缺点 | 循环无上限会死循环消耗token；每轮LLM调用增加延迟与成本；状态管理不当易丢上下文。 |

---

### 1.3 为什么需要AI Agent

| 维度 | 内容 |
|------|------|
| 是什么 | 阐述AI Agent相对纯LLM调用所解决的核心痛点。 |
| 能做什么 | 突破上下文限制；完成复杂任务；集成现有系统；人机协同处理不确定性。 |
| 怎么用 | 通过工具调用获取实时信息、访问知识库、操作数据库与API。 |
| 原理和工作流程 | 纯LLM受训练截止与上下文窗口限制，Agent通过工具调用动态获取外部信息、自动分解复杂任务分步执行、在关键节点寻求人类帮助，弥补LLM的固有限制。 |
| 缺点 | 架构复杂开发调试难度大；工具链与提示工程维护成本高；错误溯源与可解释性弱于直接调用。 |

---

## 二、LangChain生态全景

### 2.1 三大核心组件

| 维度 | 内容 |
|------|------|
| 是什么 | LangChain生态的LangChain、LangGraph、LangSmith三个核心项目。 |
| 能做什么 | 基础框架提供组件；高阶编排构建有状态工作流；开发平台调试评测监控。 |
| 怎么用 | `pip install langchain langgraph`；LangSmith接入可视化追踪。 |
| 原理和工作流程 | LangChain提供LLM调用、Prompt、Chain、Tool、Agent等基础抽象；LangGraph基于图构建有状态多节点可循环工作流；LangSmith通过追踪记录执行过程供调试评测。 |
| 缺点 | 三者边界有时模糊新手难选择；LangChain版本迭代快API易变动；LangSmith商用需付费。 |

---

### 2.2 LangChain核心设计思想

| 维度 | 内容 |
|------|------|
| 是什么 | LangChain模块化、可扩展、开箱即用的设计原则。 |
| 能做什么 | 功能独立成组件灵活组合；抽象接口支持自定义；内置大量整合即用。 |
| 怎么用 | Model I/O、Retrieval、Chains、Agents、Memory 五大模块组合。 |
| 原理和工作流程 | 将LLM交互、外部数据接入、组件编排、工具调用决策、状态管理各拆为独立模块，统一抽象接口，内置OpenAI等供应商整合，组件通过Chain或LCEL组合成应用。 |
| 缺点 | 抽象层多增加学习与调试成本；过度封装掩盖底层细节难定制；部分组件文档滞后于代码。 |

---

### 2.3 LangChain vs LangGraph 选择指南

| 维度 | 内容 |
|------|------|
| 是什么 | 根据场景在LangChain Chain与LangGraph间选择的决策指引。 |
| 能做什么 | 线性流程选Chain；条件分支选RouterChain；循环多轮与多智能体选LangGraph。 |
| 怎么用 | 简单顺序用SequentialChain；需循环人机协同用LangGraph。 |
| 原理和工作流程 | Chain面向无状态线性流水线，RouterChain支持条件分支但难循环；LangGraph以图为模型支持状态共享、节点循环、条件边与人机中断，适合复杂有状态编排。 |
| 缺点 | LangGraph概念与样板代码多于Chain，简单任务用它过度设计；Chain难以表达循环与中断，复杂任务力不从心。 |

---

## 三、核心组件：ModelI/O

### 3.1 Chat Model调用

| 维度 | 内容 |
|------|------|
| 是什么 | LangChain对不同模型供应商聊天模型的统一调用抽象。 |
| 能做什么 | 统一invoke/stream/batch接口；同步异步调用；切换供应商只改一行。 |
| 怎么用 | `llm = ChatOpenAI(model="gpt-4o")`；`llm.invoke("你好")`。 |
| 原理和工作流程 | 各供应商Chat模型实现BaseChatModel接口，统一返回BaseMessage（SystemMessage/HumanMessage/AIMessage），invoke同步等待、stream逐chunk返回、batch并发处理多输入。 |
| 缺点 | 不同供应商能力与参数差异被抽象掩盖，迁移仍有兼容问题；流式错误处理复杂；调用成本与延迟依赖供应商。 |

---

### 3.2 PromptTemplate

| 维度 | 内容 |
|------|------|
| 是什么 | LangChain动态生成提示词的模板组件。 |
| 能做什么 | 占位符填充；多角色消息模板；少样本提示；格式化为消息列表。 |
| 怎么用 | `ChatPromptTemplate.from_messages([("system","你是{role}专家"),("human","{question}")])`。 |
| 原理和工作流程 | 模板预定义占位符，format_messages时用传入变量替换占位生成最终消息列表；PromptTemplate为纯文本，ChatPromptTemplate支持多角色，FewShotPromptTemplate注入示例。 |
| 缺点 | 占位符与变量名不一致时报错难定位；复杂模板可读性差；缺乏模板校验易遗漏必填变量。 |

---

### 3.3 OutputParser

| 维度 | 内容 |
|------|------|
| 是什么 | LangChain将LLM输出解析为结构化格式的组件。 |
| 能做什么 | 解析为Pydantic模型；解析JSON；解析列表；解析失败自动重试。 |
| 怎么用 | `parser = PydanticOutputParser(Answer)`；`parser.parse(text)`。 |
| 原理和工作流程 | 解析器依据格式指令（如JSON Schema）从LLM文本提取结构化数据并校验，PydanticOutputParser借Pydantic模型校验字段，RetryOutputParser在解析失败时重发提示让LLM修正。 |
| 缺点 | 强依赖LLM遵守输出格式，格式不符解析失败；额外提示增加token消耗；复杂嵌套结构解析不稳定。 |

---

## 四、核心组件：Chain

### 4.1 LLMChain（基础链）

| 维度 | 内容 |
|------|------|
| 是什么 | LangChain最简单的组件组合：PromptTemplate加LLM加OutputParser。 |
| 能做什么 | 接收输入；格式化提示；调用LLM；解析输出为端到端流水线。 |
| 怎么用 | `chain = prompt | llm | parser`；`chain.invoke({"question":"..."})`。 |
| 原理和工作流程 | 传统LLMChain按顺序执行格式化、调用、解析三步；LCEL写法用管道符将组件串联，invoke时数据沿管道流转，每步输出作为下步输入。 |
| 缺点 | 仅支持单步线性流程无法分支循环；传统run方法已废弃易混淆；错误处理需额外配置。 |

---

### 4.2 SequentialChain（顺序链）

| 维度 | 内容 |
|------|------|
| 是什么 | 按顺序执行多个链、前链输出作为后链输入的编排方式。 |
| 能做什么 | 串联多步任务；传递中间变量；合并多链输出。 |
| 怎么用 | `SequentialChain(chains=[chain1,chain2], input_variables=["topic"], output_variables=["content"])`。 |
| 原理和工作流程 | 顺序执行chains列表，通过output_key与input_variables在链间传递变量，每链读取所需输入并写出指定输出键，最终聚合所有输出变量返回。 |
| 缺点 | 严格线性无法分支回退；变量管理繁琐易键名冲突；调试中间结果不直观。 |

---

### 4.3 RouterChain（路由链）

| 维度 | 内容 |
|------|------|
| 是什么 | 根据输入内容动态选择不同分支链处理的编排方式。 |
| 能做什么 | 输入分类；选择目标链；分发到不同逻辑；提供默认分支。 |
| 怎么用 | `MultiPromptChain(router_chain=..., destination_chains={...}, default_chain=...)`。 |
| 原理和工作流程 | LLMRouterChain让LLM根据输入与各destination描述选择最匹配分支，MultiPromptChain按路由结果调用对应destination_chain，无匹配时走default_chain。 |
| 缺点 | 路由依赖LLM判断可能误分类；分支描述需精心设计；不支持循环与多分支并行。 |

---

### 4.4 LCEL 现代写法

| 维度 | 内容 |
|------|------|
| 是什么 | LangChain Expression Language，用管道符组合组件的新一代语法。 |
| 能做什么 | 管道串联组件；支持并行分支；原生流式与异步；统一Runnable接口。 |
| 怎么用 | `chain = {"question": lambda x: x["question"]} | prompt | llm | parser`。 |
| 原理和工作流程 | 每个组件实现Runnable协议，管道符重载为组件拼接生成新Runnable，invoke/stream/batch统一流转数据，支持字典并行与lambda自定义变换。 |
| 缺点 | 调试管道中间步骤需借助调试工具；复杂lambda降低可读性；与旧Chain API并存增加学习负担。 |

---

## 五、核心组件：Tool与Agent

### 5.1 Tool工具集成

| 维度 | 内容 |
|------|------|
| 是什么 | LangChain为Agent提供可调用外部功能的工具机制，含内置与自定义工具。 |
| 能做什么 | 调用搜索/REPL/数据库等内置工具；用@tool装饰器定义自定义工具；类型注解描述参数。 |
| 怎么用 | `@tool\ndef get_weather(city:str)->str: """查询天气"""`。 |
| 原理和工作流程 | 内置工具封装第三方API为统一Tool接口；@tool装饰器从函数docstring与类型注解自动生成工具描述供LLM理解，LLM据此决定调用时机与参数。 |
| 缺点 | 工具描述质量直接影响调用准确率；危险工具（REPL/Bash）需严格权限控制；错误处理需自行实现。 |

---

### 5.2 Agent：ReAct模式

| 维度 | 内容 |
|------|------|
| 是什么 | Reasoning加Acting交替进行的最经典Agent提示模式。 |
| 能做什么 | 显式输出思考过程；决定调用工具；基于观察继续推理；最终给出答案。 |
| 怎么用 | `prompt = hub.pull("hwchase17/react")`；`create_react_agent(llm,tools,prompt)`。 |
| 原理和工作流程 | ReAct提示引导LLM按"思考-行动-观察"循环输出，思考当前所需信息，行动调用工具，观察工具返回，再思考直至得出答案，将推理与工具调用交织提升复杂任务表现。 |
| 缺点 | 每步显式思考消耗大量token；输出格式依赖LLM遵守易解析失败；步数多时延迟显著。 |

---

### 5.3 AgentExecutor

| 维度 | 内容 |
|------|------|
| 是什么 | ReAct Agent的执行器，负责循环调用Agent与工具直至完成。 |
| 能做什么 | 执行Agent循环；限制最大步数；处理解析错误；打印思考过程。 |
| 怎么用 | `AgentExecutor(agent=agent, tools=tools, max_iterations=10, handle_parsing_errors=True)`。 |
| 原理和工作流程 | 循环调用agent获取下一步动作，若为工具调用则执行工具将结果回填，直至LLM给出最终答案或达到max_iterations，handle_parsing_errors在输出格式错误时重试。 |
| 缺点 | 无max_iterations易死循环耗尽token；解析错误重试增加成本；中间状态黑盒调试依赖verbose。 |

---

## 六、核心组件：Memory

### 6.1 ConversationBufferMemory

| 维度 | 内容 |
|------|------|
| 是什么 | 最简单的Memory，完整保存所有对话历史。 |
| 能做什么 | 保存全部消息；按memory_key加载历史；返回消息对象列表。 |
| 怎么用 | `ConversationBufferMemory(memory_key="chat_history", return_messages=True)`。 |
| 原理和工作流程 | 内部维护消息列表，save_context将每轮输入输出追加为消息，load_memory_variables返回完整历史供Prompt拼接，return_messages决定返回消息对象还是拼接文本。 |
| 缺点 | token随对话线性增长，长对话超上下文窗口；无压缩无摘要成本高。 |

---

### 6.2 ConversationSummaryMemory

| 维度 | 内容 |
|------|------|
| 是什么 | 随对话增长自动对历史进行总结以节省token的Memory。 |
| 能做什么 | 调用LLM总结历史；保持token稳定；返回总结消息。 |
| 怎么用 | `ConversationSummaryMemory.from_llm(llm, memory_key="chat_history")`。 |
| 原理和工作流程 | 每新增一轮对话调用LLM对已有总结与新对话重新生成摘要，用不断更新的摘要替代完整历史，使token占用趋于稳定不随轮数无限增长。 |
| 缺点 | 总结丢失细节信息；每轮额外LLM调用增加延迟与成本；总结质量依赖LLM能力。 |

---

### 6.3 VectorStoreRetrieverMemory

| 维度 | 内容 |
|------|------|
| 是什么 | 将对话历史存入向量库、只检索相关片段的Memory。 |
| 能做什么 | 向量化存储历史；按当前问题检索相关上下文；支撑超长对话。 |
| 怎么用 | `VectorStoreRetrieverMemory(retriever=faiss.as_retriever())`。 |
| 原理和工作流程 | save_context将每轮对话嵌入并存入向量库，load_memory_variables时将当前问题嵌入检索top-k最相关历史片段注入Prompt，仅召回相关内容而非全部历史。 |
| 缺点 | 需要向量库与嵌入模型增加依赖；检索可能遗漏重要远期上下文；写入与检索均有延迟。 |

---

### 6.4 选择指南

| 维度 | 内容 |
|------|------|
| 是什么 | 根据对话长度与场景选择合适Memory类型的决策指引。 |
| 能做什么 | 短对话选Buffer；长对话选Summary；超长对话选VectorStore；最近上下文选BufferWindow。 |
| 怎么用 | 按token预算与细节需求在四类Memory间取舍。 |
| 原理和工作流程 | Buffer完整保留细节但token线性增长，Summary稳定token但丢细节，VectorStore只检索相关内容需嵌入存储，BufferWindow仅保留最近N轮折中，按对话长度与细节需求权衡。 |
| 缺点 | 无单一Memory适配所有场景；切换Memory需改造代码；参数调优依赖经验。 |

---

## 七、LangGraph高阶编排

### 7.1 核心概念

| 维度 | 内容 |
|------|------|
| 是什么 | LangGraph基于图编排的State、Node、Edge等核心概念集合。 |
| 能做什么 | 共享状态读写；定义执行节点；连接节点；条件选择下一节点；指定入口。 |
| 怎么用 | `StateGraph(State)`；`add_node`；`add_edge`；`add_conditional_edges`。 |
| 原理和工作流程 | State为所有节点共享的TypedDict，Node接收状态返回更新，Edge连接节点形成流转，Conditional Edge依状态动态选择下一节点，Entry Point指定起始节点，编译后图按边流转执行。 |
| 缺点 | 概念多上手门槛高；状态结构变更影响所有节点；图复杂时可视化与调试困难。 |

---

### 7.2 StateGraph 基础

| 维度 | 内容 |
|------|------|
| 是什么 | LangGraph以StateGraph构建有状态图工作流的基础用法。 |
| 能做什么 | 定义状态结构；添加节点函数；连接边；编译执行。 |
| 怎么用 | `workflow.add_node("plan",plan_node)`；`graph = workflow.compile()`；`graph.invoke({"input":"..."})`。 |
| 原理和工作流程 | StateGraph以TypedDict定义共享状态，add_node注册接收状态返回增量的节点函数，add_edge与set_entry_point定义流转，compile编译为可执行图，invoke按拓扑执行节点并合并状态。 |
| 缺点 | 节点返回需为状态增量否则覆盖出错；编译后图不可变修改需重建；状态合并策略默认覆盖需显式配置。 |

---

### 7.3 条件路由

| 维度 | 内容 |
|------|------|
| 是什么 | LangGraph根据状态动态决定下一节点的条件边机制。 |
| 能做什么 | 判断是否继续循环；按状态分支；实现Agent工具调用循环。 |
| 怎么用 | `workflow.add_conditional_edges("execute", should_continue, {"continue":"plan", END:END})`。 |
| 原理和工作流程 | 条件边绑定判断函数，执行完源节点后调用该函数读取状态返回路由键，按映射表选择下一目标节点，从而实现"继续循环或结束"等动态流转，是Agent循环的核心实现。 |
| 缺点 | 判断函数逻辑错误导致死循环或提前终止；路由键与映射不匹配报错；多条件分支状态管理复杂。 |

---

### 7.4 人机协同

| 维度 | 内容 |
|------|------|
| 是什么 | LangGraph支持中断执行等待人类输入后继续的机制。 |
| 能做什么 | 关键步骤人工审核；信息不足向用户提问；人工干预纠正错误。 |
| 怎么用 | `compile(checkpointer=MemorySaver(), interrupt_before=["review"])`；恢复 `graph.invoke(None, config)`。 |
| 原理和工作流程 | 编译时指定interrupt_before节点与checkpointer，执行到该节点前暂停并持久化状态，人工审核后用相同thread_id传入None或新输入恢复，从断点继续执行。 |
| 缺点 | 中断恢复依赖checkpointer状态持久化；并发会话管理复杂；人工等待阻塞流程需超时处理。 |

---

### 7.5 多智能体协作

| 维度 | 内容 |
|------|------|
| 是什么 | LangGraph实现多个Agent协作的编排能力。 |
| 能做什么 | Supervisor分工；顺序工作流串联；Agent间自由通信协作。 |
| 怎么用 | Supervisor节点路由到各工作Agent节点。 |
| 原理和工作流程 | 通过图编排多个Agent节点，Supervisor模式由主Agent根据任务分派给工作Agent并汇总结果，顺序工作流按固定顺序传递，自由协作通过共享状态或消息通道互相通信。 |
| 缺点 | 多Agent协调复杂易死锁或重复劳动；token与延迟成倍增加；责任归属与错误溯源困难。 |

---

### 7.4 LangGraph Streaming流式输出

| 维度 | 内容 |
|------|------|
| 是什么 | LangGraph支持的多种流式输出模式，用于实时展示Agent过程。 |
| 能做什么 | values输出完整状态；updates输出增量；messages输出token流；debug输出调试信息。 |
| 怎么用 | `graph.stream(input, stream_mode="messages")`；异步用 `astream_events`。 |
| 原理和工作流程 | stream按mode过滤事件输出，values每步输出完整状态快照，updates仅输出变化增量，messages透传LLM token流实现打字机效果，astream_events异步推送工具开始结束等细粒度事件。 |
| 缺点 | 不同mode语义易混淆；异步事件处理复杂；messages模式仅适用于含LLM调用的节点。 |

---

### 7.5 LangGraph Memory与状态持久化

| 维度 | 内容 |
|------|------|
| 是什么 | LangGraph的Checkpointer机制实现会话记忆与断点恢复。 |
| 能做什么 | 多轮对话状态保持；按thread_id隔离会话；中断恢复；持久化存储。 |
| 怎么用 | `compile(checkpointer=MemorySaver())`；config含 `thread_id`。 |
| 原理和工作流程 | Checkpointer在每个节点执行后持久化状态快照，thread_id标识会话实现隔离，再次invoke同thread_id时恢复历史状态延续记忆，interrupt暂停后传None从断点继续。 |
| 缺点 | MemorySaver进程结束丢失仅适合开发；生产需Postgres等持久化增加运维；状态序列化大对象影响性能。 |

---

## 学习导航

本节为辅助内容，无五维表格

---

## 自检清单

本节为辅助内容，无五维表格

---

> [返回原文](./02-LangChain与AI智能体核心.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
