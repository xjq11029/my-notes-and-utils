# 第 2 章 模型的创建与调用：三个初始化角度与四种调用形态

## 一、这一章要解决的问题

第 1 章把三件套的边界画完了，但一行代码都没写。从这一章开始动手，而所有 Agent 代码的第一行都长一个样：**先造一个模型对象，再把它交给别的东西。**

「造模型」看起来是全书最简单的一步——无非 `ChatOpenAI(...)`。但它同时替后面钉死了三件很难再改的事：

1. **用谁家的接口**——换个平台，类名、参数名、环境变量名、甚至「支不支持工具调用」全都跟着变；
2. **你传进去的东西，模型到底收到了什么**——这是排查一切「模型为什么不按我说的做」的起点；
3. **一次调用回来的对象里有什么**——只读 `content`，会把 token 账、结束原因、工具调用意图全丢掉。

这三件事对应的三个典型症状是：「明明设了 `temperature=0`，输出还是飘」、「我就传了个字典，怎么就报错了」、「钱花哪儿了不知道」。

本章只讲**单个模型对象**的创建与调用，2.1–2.6 六节围着同一个对象转：**创建**两站——2.1 模型初始化的三个角度，2.2 最常用的统一入口 `init_chat_model` 的参数展开；**调用**四站——2.3 `invoke` 的三种入参形态，2.4 返回的 `AIMessage` 结构，2.5 同步 / 异步 / 流式 / 批量四种调用形态，2.6 模型的 `profile` 属性与单次调用的 `config`。`init_chat_model` 与 `invoke` 同属一章，因为它们是同一个对象的两端：**前者把它造出来，后者是它身上最核心的方法**——先造出来，再调用它，就是本章的主线。它**不涉及**：Agent 循环（第 5 章 `create_agent` 与 Agent Loop）、消息类型与提示词模板的细节（第 3 章 Message 与提示词模板）、结构化输出（第 4 章 结构化输出）、工具与运行时上下文（第 7 章 工具与运行时上下文）。本章是它们共同的前置。

## 二、机制与原理

### 2.1 三个初始化角度

「初始化一个模型」这件事里，先看两个问题：**谁替你决定用哪个类**、**模型部署在哪**。日常入口可以归成三个角度——

- **角度 1｜模型提供商库**：你自己选类（`langchain-openai` 的 `ChatOpenAI`、`langchain-deepseek` 的 `ChatDeepSeek`）。控制最细，但参数名跟着厂商走。
- **角度 2｜统一入口 `init_chat_model()`**：你写 `"provider:model"` 字符串，框架按前缀去注册表里查该用哪个类。换模型只改字符串。
- **角度 3｜本地 Ollama（`ChatOllama`）**：模型不在云端，就在本机。前两个角度问的是「用哪家的 API」，这一个问的是「模型部署在哪」。（`ChatOllama` 同样是你自己选类，但本节按部署位置把它单列为角度 3；图 3 只把它放在角度 3。）

为什么这么分？因为这三种写法的**失效方式完全不同**：角度 1 换平台要改代码；角度 2 拼错前缀会在构造时就报错（见 2.2）；角度 3 服务没起、模型没 `pull`，构造能过但一调用就连接失败。分清楚你用的是哪一条路，就知道出错时该查什么。

![图 3　模型初始化的三个角度](assets/03_model_init_angles.png)
*图 3　模型初始化的三个角度*

### 2.2 `init_chat_model` 的常用参数

2.1 的三个角度里，角度 2（统一入口）是日常默认路径，本节把它展开。先明确一件事：**`init_chat_model()` 返回的是一个模型对象**——但**两语言返回的具体类型不同（示例实测）**：Python 侧是 `ChatOpenAI` 实例（例外：声明了 `configurable_fields`、或干脆没传 `model`，返回的是 `_ConfigurableModel`，见本节表后那段），**JS 侧是 `ConfigurableModel`**（`initChatModel` 的通用包装，内部才持有真正的 provider 类）。而且 JS 侧返回的是 **`Promise`**，少一个 `await` 拿到的是 Promise 而不是模型。2.3 起要讲的 `invoke` 等方法，都是这个对象上的方法。造它正是为了调它。

「明明设了 `temperature=0`，输出还是飘」——这类「设了却不生效」的困惑，排查起点就在造模型的那一行。用 `init_chat_model` 只需要搞清楚一件事：**你写进去的参数，哪些归它自己管，哪些它原样转手给了别人？** 这条界线一清楚，后面所有坑都有了着落。

实测签名（`langchain` 1.4.2）：

```python
init_chat_model(model=None, *, model_provider=None,
                configurable_fields=None, config_prefix=None, **kwargs)
```

先跑一个最小例子（Python，只构造、不发请求）：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-4o", api_key="sk-placeholder")
print(type(model).__name__)   # ChatOpenAI
```

对着签名数：**它自己的参数只有四个**——就是上面签名里那四个：`model` / `model_provider` 管「造哪个类的哪个模型」，`configurable_fields` / `config_prefix` 管「运行时改哪几个字段、用哪个键名改」——**前者是白名单，后者是键名前缀**。**传了 `model` 又不声明 `configurable_fields` 时**，模型就是固定的：运行时在 `config` 里写什么都不生效，也不报错（没传 `model` 是另一条分支，见下表）。除此之外你写的一切（`temperature` / `api_key` / `base_url` / `max_tokens` 是最常用的几个）都落进 `**kwargs`，**原样转发**给底层那个 `ChatXxx` 类的构造函数。

打个比方：`init_chat_model` 像总机，只认四个转接规则；你说的其他任何话，它都原封不动传给分机那边的专人——而每个分机（每家集成）听懂的词并不一样。这就是下一段「钥匙」的由来。

这一点是理解后面所有坑的钥匙：**转发意味着 `init_chat_model` 这一层不校验参数名**。参数名由每个集成自己的字段定义决定，于是有两件事要分开记：

- **名字可能不同**：`ChatOpenAI` 与 `ChatAnthropic` 的地址参数都收 `base_url`（本机核对二者 pydantic 字段的 alias），但 `ChatDeepSeek` 收的是 `api_base`（官方 reference 核对，本机未装 `langchain-deepseek`、**未实测**）。
- **写错了不报错**：这才是真正咬人的地方。实测给 `ChatOpenAI` 传 `api_base`，构造**照样成功**，请求照旧打到 `api.openai.com`，只留一条 `UserWarning`——完整实测见第四节坑 2。

下表回答的问题是：**这个函数到底能配哪些东西，哪些是它自己的参数、哪些只是转发？**

| 参数 | 作用 | 谁在管 | 口径 / 依据 |
|---|---|---|---|
| `model` | 模型名，或 `"provider:model"` 形式 | `init_chat_model`（用来自动选类） | 示例实测 |
| `model_provider` | 提供商名，等价于 `model` 里的前缀 | `init_chat_model`（用来自动选类） | 示例实测 |
| `configurable_fields` | 运行时覆盖的**白名单**。**传了 `model` 时**：不传（`None`，默认）= 固定模型，运行时写什么都不生效；`"any"` = 全部字段可改（含 `api_key` / `base_url`，等于能把请求改道，**别对不可信配置开**）；列出字段名 = 只有这些能改，**名单外的键静默丢弃**。**没传 `model` 时**：默认 `("model", "model_provider")`——模型名本身得靠运行时给 | `init_chat_model` | 源码核对（docstring / `_ConfigurableModel` 实现），运行时覆盖未实测 |
| `config_prefix` | 只给白名单里的字段**改运行时键名**：设 `"a"` 就用 `config["configurable"]["a_model"]` 覆盖，不设就用 `config["configurable"]["model"]`；`"a"` 与 `"a_"` 等价（缺下划线内部会补）。它**不决定能不能改**——**传了 `model` 但没传 `configurable_fields`** 时，单传它只会拿到一条 `UserWarning` 和一个固定模型；连 `model` 也没传时，框架会默认放开 `model` / `model_provider`，前缀照常生效 | `init_chat_model` | 同上 |
| `temperature` | 采样温度，越高越随机 | 转发给底层类 | 默认值已核对（见下），示例未传 |
| `api_key` | 密钥；不传则从环境变量读 | 转发给底层类 | 示例实测 |
| `base_url` | 请求地址 | 转发给底层类（**参数名随集成变**） | 示例实测 |
| `max_tokens` | 输出 token 上限 | 转发给底层类 | 字段存在已核对，示例未传 |

`configurable_fields` 还有一个比它自己更容易漏的副作用：**只要它非空（`"any"` 或一串字段名），`init_chat_model` 返回的就不再是 `ChatXxx`**，而是 `_ConfigurableModel` 包装对象——真正的模型类延迟到**每次调用**才按「构造时的默认值 + 这次 `config` 的覆盖」现场组装（源码核对：`_model()` / `_model_params()`）。这带来两个连带结果：一是 `isinstance(m, ChatOpenAI)` 从声明那一刻起就是 `False`——后面凡按类做判断、按类取属性的写法都会在这里断；二是两语言的默认值并不对称——JS 的 `initChatModel` **总是**返回 `ConfigurableModel`，不显式传 `configurableFields` 时默认放开 `model` / `modelProvider`（源码核对，JS `langchain` 1.5.11），Python 侧传了 `model` 就默认全关。**同样是 `openai:gpt-4o`，JS 那边运行时能换模型，Python 这边不能。**

两个参数的配合只有一种形状——**先声明白名单，再决定键名**。例如初始化时：

```python
m = init_chat_model("openai:gpt-4o", configurable_fields=["model", "temperature"],
                    config_prefix="a")
```

运行时：

```text
config_prefix="a"   →  config={"configurable": {"a_model": "openai:gpt-4o-mini", "a_temperature": 0.2}}
不传 config_prefix   →  config={"configurable": {"model": "openai:gpt-4o-mini", "temperature": 0.2}}
```

`configurable_fields` 里写的是**不带前缀的裸字段名**（写 `"model"`，不写 `"a_model"`）；键名对不上前缀的，等同于没传。上例若把 `temperature` 从白名单里去掉，`a_temperature` 就会被静默丢弃。

一个容易忽略的转发细节：`api_key` / `base_url` 在 `ChatOpenAI` 上是**别名**，字段本名分别是 `openai_api_key` / `openai_api_base`（示例 ① 打印的就是 `compat.openai_api_base`），`max_tokens` 的别名则是 `max_completion_tokens`（本机核对 `langchain-openai` 1.7.2 的 `model_fields`）。两种写法构造出的是同一个对象，但读源码、看请求体时看到的是本名。

还有两处**本机核对（不在示例输出里）与官方文档参数表不一致**，按本教程口径**以本机核对为准**：

- **`temperature` 的默认值**：官方文档参数表写 `0.7`；本机核对 `ChatOpenAI.model_fields["temperature"].default` 是 `None`（不传就不传，由服务端决定），`ChatOpenAI.model_fields["model_name"].default` 才是 `"gpt-3.5-turbo"`。所以「不设温度」和「设成 0.7」不是一回事。
- **支持的 provider 列表**：官方文档列了 **24 个**（且有两处拼写粘连：`bedrockbedrock_converse`、`google_vertexaigrog`）；本机核对报错信息里给出的完整列表是 **28 个**（`langchain` 1.4.2），比文档多出 `baseten`、`langsmith`、`litellm`、`meta`。完整名单见本节末尾的参考块——这份列表会随版本变，别背，拼错时框架会把当前版本的全表打给你。

> **参考块｜`init_chat_model` 的 28 个 provider（本机核对，`langchain` 1.4.2）**
> `anthropic, anthropic_bedrock, azure_ai, azure_openai, baseten, bedrock, bedrock_converse, cohere, deepseek, fireworks, google_anthropic_vertex, google_genai, google_vertexai, groq, huggingface, ibm, langsmith, litellm, meta, mistralai, nvidia, ollama, openai, openrouter, perplexity, together, upstage, xai`

### 2.3 `invoke` 的三种入参形态

不管 2.1 走哪个角度、2.2 配了哪些参数，拿到的都是**同一个模型对象**：Python 的 `init_chat_model()` 返回 2.1 角度 1 里直接选类的那个 `ChatXxx` 实例（声明了 `configurable_fields` 时是包装对象，见 2.2）；JS 的 `initChatModel()` 返回 `ConfigurableModel` 包装对象（它把真实模型类延迟到调用时组装）。从这里开始讲「用」——**`invoke` 是这个模型对象的核心方法**：给它输入，还你一个 `AIMessage`（字段结构见 2.4）。

`invoke` 接受三种写法。下表回答的问题是：**这三种写法真的等价吗，为什么要有三种？**

| 你传的 | 模型实际收到 | 适用场景 |
|---|---|---|
| 一个字符串 | `[HumanMessage(...)]` | 快速测试、单轮问答 |
| `list[dict]`（`{"role": ..., "content": ...}`） | 逐条转成对应消息对象 | 报文、数据库里取出来的数据 |
| `list[Message]`（`SystemMessage` / `HumanMessage` / …） | 原样 | 代码里拼逻辑（本教程统一用这种） |

![图 4　invoke 三种入参 → AIMessage 结构](assets/04_invoke_to_aimessage.png)
*图 4　invoke 三种入参 → AIMessage 结构*

实测结论：三种写法的归一化结果**逐条一致**（见本章第三节的运行输出）。差异只在你这一侧——`dict` 适合序列化和网络传输，消息对象有类型、能挂 `tool_calls`。消息类型本身的细节（四种角色、`content_blocks`、提示词模板）是第 3 章 Message 与提示词模板的主题。

一条**边界条件**值得单独记住：**`dict` 形态指的是 dict 的列表**。传单条 dict（`model.invoke({"role": "user", "content": "hi"})`）会被直接拒绝——Python 抛 `ValueError: Invalid input type <class 'dict'>`，JS 抛 `TypeError`。这不是「静默忽略」，是硬报错。

### 2.4 返回的 `AIMessage` 结构

三种入口看过，再看 `invoke` 吐出来的东西：它返回的不是字符串，是一个 `AIMessage`。下表回答的问题是：**这个对象里除了文本，还有什么值得读？**

| 字段 | 含义 | 谁填的 |
|---|---|---|
| `content` | 最终文本 | 模型 |
| `tool_calls` | 模型请求调用的工具列表（`name` / `args` / `id`） | 模型 |
| `invalid_tool_calls` | 格式错误、无法解析的调用尝试 | 模型（异常情况） |
| `response_metadata` | 原始响应元数据：模型版本、`finish_reason` 等 | **provider 驱动** |
| `usage_metadata` | 标准化后的 token 账：`input_tokens` / `output_tokens` / `total_tokens` | **provider 驱动** |
| `additional_kwargs` | 厂商特有字段（如 DeepSeek 的 `reasoning_content`） | provider 驱动 |
| `id` | LangChain 内部给这次运行分配的 ID | 框架（**仅 Python 假模型填**，形如 `lc_run--…`；**JS 假模型不填**，是 `undefined`） |

前三个字段是「模型说了什么」，后四个是「这次调用花了什么代价」。**`response_metadata` 和 `usage_metadata` 由 provider 驱动填**——本教程的假模型不产生它们（示例实测：Python `response_metadata = {}`、`usage_metadata = None`；JS 同为空对象 / `undefined`），真实 provider 才会填。真实 provider 下的完整长相（**2026-10-16 已用智谱端点实测**）：

```text
content='（回答正文，随提示词变化）'
response_metadata={'model_name': 'glm-4.5-air',
                   'finish_reason': 'stop', ...}
usage_metadata={'input_tokens': 18, 'output_tokens': 128, 'total_tokens': 146,
                'input_token_details': {'cache_read': 4}, ...}
```

`finish_reason` 有两个常见取值：`stop`（正常结束）与 `length`（撞到 `max_tokens` 被截断）。看到「回答说到一半没了」，先查这个字段，再看 `max_tokens`。agent 语境下还有第三个关键取值 `tool_calls`（模型决定调工具、把话筒交给框架）——LangChain 会把它转成 `AIMessage` 的 `tool_calls` 字段，正是第 5 章 Agent Loop「继续转还是停」的判据。

### 2.5 四种调用形态

一次 `invoke` 的来龙去脉清楚了，接下来看同一个模型的另外几种调法。下表回答的问题是：**同一个模型，我该用哪个方法调它？**

| 方法（Python） | 对应 JS | 行为 | 典型场景 |
|---|---|---|---|
| `invoke` | `invoke` | 阻塞，一次返回一个 `AIMessage` | 批处理、无需实时反馈 |
| `stream` | `stream` | 返回 chunk 迭代器，边生成边拿 | 聊天机器人、长文本 |
| `batch` | `batch` | 一批输入，按**原顺序**返回 list | 文档摘要、批量分类 |
| `ainvoke` | **没有** | `invoke` 的异步孪生 | 高并发 Web 服务 |

这四个方法不是四套实现，而是两个维度的组合：**要不要等**（同步 / 异步）× **怎么收**（整条 / 流式 / 一批）。Python 把两个维度都做成了独立方法，所以有 6 个（`invoke` / `stream` / `batch` 与各自的 `a` 版本）；JS 只保留了「怎么收」那一维——因为 JS 的这三个方法本来就返回 `Promise`，`await` 一下就是异步版，不需要第二套名字。这是双语言最容易记混的一处。

`stream` 的 chunk 语义必须说清楚：**chunk 是「增量」，不是「片段」**。真实模型逐 token 产出，一条几百字的回答会分成多个 chunk（**2026-10-16 已用 `glm-4.5-air` 实测 194 个 chunk**；具体个数仍取决于模型与供应商），要靠循环拼接。本教程的假模型**只吐 1 个 chunk**（一次给整条消息），而且类型是 `AIMessage` 而不是真实模型会用的 `AIMessageChunk`（后者为源码核对，示例只打印数量与内容）——这两点都是为了让输出可复现，不是真实行为。所以「假模型 stream 只有 1 个 chunk」只能用来验证「框架的流式管道通了」，不能用来验证「分块粒度」；写 `isinstance(chunk, AIMessageChunk)` 这类判断时更要小心。

`batch` 也有两条纪律：**返回顺序与输入顺序一致**（实测 `["第一", "第二", "第三"]`），以及它的价值在真实网络下才体现——框架并发发出请求，比 `for` + `invoke` 少很多往返等待。想限制并发数，在 `config` 里传 `max_concurrency`（见 2.6）。

### 2.6 `profile` 属性与 `config` 参数

调用方法看完，还有两样东西挂在同一个对象上：一样是它**自带**的（`profile`，造出来时就定了），一样是每次调用时**临时传**的（`config`）。

**`profile` 是模型的「能力画像」**：上下文窗口多大、支不支持工具调用、支不支持结构化输出。本机核对（`langchain-openai` 1.7.2，**构造层核对，未联网**）：

```text
init_chat_model('openai:gpt-4o').profile（节选）
= {'max_input_tokens': 128000, 'max_output_tokens': 16384,
   'tool_calling': True, 'structured_output': True}
```

两条边界：**① 画像存在与否取决于 LangChain 有没有为这个模型声明过**——声明过就是一个 dict（`gpt-4o` 本机核对有 25 个键；示例只打印了其中 4 个键的节选），没声明就是 `None`（本机核对 `openai:zzz-unknown-model`）；假模型继承基类，Python 侧是 `None`、JS 侧是 `{}`。**② 画像描述的是「构造出来的那个对象」，不是「服务端真的这么干」**，它适合做运行时判断，不适合当契约。

**`config` 是「这一次调用的配置单」**——它不只记账，也能改变执行（见下表后三项）。下表回答的问题是：**config 里能放什么，各自影响什么？**

| 配置项 | 作用 | 本教程实测 |
|---|---|---|
| `run_name` | 给这次运行起个可读名字 | 透传到回调 |
| `tags` | 标签，用于分类过滤 | 透传到回调 |
| `metadata` | 任意键值对（`user_id`、`session_id`…） | 透传到回调 |
| `callbacks` | 回调处理器 | 触发 `on_chat_model_start` |
| `max_concurrency` | `batch` 的最大并发数 | 未实测 |
| `recursion_limit` | 图执行的递归深度上限 | 未实测（LangGraph 执行期生效：agent 编译成图后循环轮数超限会拦截执行，不绑定某一章） |
| `configurable` | 运行时覆盖模型参数——**只对初始化时的 `configurable_fields` 白名单生效**（没传 `model` 时默认 `model` / `model_provider`，见 2.2），名单外的键静默忽略 | 未实测（声明方式为源码核对） |

前四项的用途集中在**可观测**上：它们不进消息、不影响模型输出，只在回调与追踪系统（如 LangSmith）里可见。第 10 章 可观测与评测会接着用它们。实测还发现框架会往 `metadata` 里**自动补**几个键：`ls_provider`、`ls_model_type`、`ls_integration`、`lc_versions`（JS 侧叫 `versions`）——这些不是你写的，是给追踪用的。

后三项属于另一类：**它们真的会影响执行**——`max_concurrency` 改并发度，`recursion_limit` 改递归上限，`configurable` 改这次调用实际用的模型参数。所以这张表按「只记账 / 真影响执行」分两半，读的时候要分清。

最后一条容易踩的点：**把 config 钉在模型对象上要用 `with_config()`，而它返回的不是原来的模型类**。实测 Python 返回 `RunnableBinding`、JS 也返回 `RunnableBinding`；照样能 `invoke`，但 `isinstance` / `instanceof` 判断会失败。要取回原对象用 `.bound`。

## 三、代码：Python 与 TypeScript

下面两段是同一件事的两个语言版本，只留主干；完整版（含五节完整输出）见 `code/python/02_models.py` 与 `code/typescript/02_models.ts`。

Python 侧：

```python
import asyncio

from _fake_model import ScriptedChatModel, reply, tool_call
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage

# ① 三个初始化角度（只构造，不发请求；此处只留角度 2 的主干）
unified = init_chat_model("openai:gpt-4o", api_key="sk-placeholder")  # 前缀 openai → ChatOpenAI
compat = init_chat_model(model="deepseek-chat", model_provider="openai",  # 兼容用法：任何
                         api_key="sk-placeholder",                        # OpenAI 兼容平台
                         base_url="https://api.deepseek.com/v1")          # 都走 openai 前缀
init_chat_model("deepseek:deepseek-chat")   # ImportError：缺 langchain-deepseek
init_chat_model("qwen-plus")                # ValueError：推断不出 provider

# ② 三种入参形态 → 归一化（用 .seen 看模型实际收到什么）
probe = ScriptedChatModel(script=[reply("收到。")] * 3)
probe.invoke("翻译成英文：你好世界")                       # → [HumanMessage]
probe.invoke([{"role": "system", "content": "你是翻译助手。"},
              {"role": "user", "content": "翻译成英文：你好世界"}])   # → [System, Human]
probe.invoke([SystemMessage("你是翻译助手。"),
              HumanMessage("翻译成英文：你好世界")])                  # → [System, Human]
print(probe.seen[-1])        # 模型侧只认消息对象

# ③ AIMessage 结构
msg = ScriptedChatModel(script=[reply("2 + 3 * 2 = 8")]).invoke("2 + 3 * 2 = ？")
print(msg.content, msg.tool_calls, msg.response_metadata, msg.usage_metadata)
# 假模型：'2 + 3 * 2 = 8' [] {} None —— 后两项要真实 provider 才填

# ④ 四种调用形态
ScriptedChatModel(script=[reply("一次性返回。")]).invoke("你好")
list(ScriptedChatModel(script=[reply("流式输出。")]).stream("你好"))    # 假模型：1 个 chunk
ScriptedChatModel(script=[reply("第一"), reply("第二"), reply("第三")]).batch(["q1", "q2", "q3"])
asyncio.run(ScriptedChatModel(script=[reply("异步返回。")]).ainvoke("你好"))  # 异步孪生

# ⑤ profile 与 config
print(ScriptedChatModel(script=[reply("x")]).profile)      # 假模型：None
class TagProbe(BaseCallbackHandler):
    def on_chat_model_start(self, serialized, messages, *, tags=None, metadata=None, **kw):
        print(tags, metadata)                              # tags/metadata 只能从回调看见
ScriptedChatModel(script=[reply("收到。")]).invoke(
    "你好", config={"tags": ["ch02"], "metadata": {"user_id": "u-42"}, "callbacks": [TagProbe()]})
```

TypeScript 侧：

```typescript
import { initChatModel } from "langchain";
import { BaseCallbackHandler } from "@langchain/core/callbacks/base";
import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import { ScriptedChatModel, reply } from "./_fakeModel";

// ① 三个初始化角度（只构造，不发请求）
// ⚠️ JS 的 initChatModel 是**异步**的，必须 await
const unified = await initChatModel("openai:gpt-4o", { apiKey: "sk-placeholder" });
// 本机未装 @langchain/openai：构造不会失败，返回 ConfigurableModel；
// 真正 invoke 时才会报缺包（实测输出见 code/typescript/02_models.ts 的 ①）
await initChatModel("qwen-plus");   // 抛 Unable to infer model provider（中译：推断不出模型提供商）

// ② 三种入参形态 → 归一化（用 seen 看模型实际收到什么）
const probe = new ScriptedChatModel({ script: [reply("收到。"), reply("收到。"), reply("收到。")] });
await probe.invoke("翻译成英文：你好世界");                        // → [HumanMessage]
await probe.invoke([{ role: "system", content: "你是翻译助手。" },
                    { role: "user", content: "翻译成英文：你好世界" }]);   // → [System, Human]
await probe.invoke([new SystemMessage("你是翻译助手。"),
                    new HumanMessage("翻译成英文：你好世界")]);            // → [System, Human]
console.log(probe.seen.at(-1));     // 模型侧只认消息对象

// ③ AIMessage 结构
const msg: any = await new ScriptedChatModel({ script: [reply("2 + 3 * 2 = 8")] })
  .invoke("2 + 3 * 2 = ？");
console.log(msg.content, msg.tool_calls, msg.response_metadata, msg.usage_metadata);
// 假模型："2 + 3 * 2 = 8" [] {} undefined

// ④ 三种调用形态（JS 没有 ainvoke，invoke/stream/batch 本身就返回 Promise）
const one: any = await new ScriptedChatModel({ script: [reply("一次性返回。")] }).invoke("你好");
const chunks: any[] = [];
for await (const c of await new ScriptedChatModel({ script: [reply("流式输出。")] }).stream("你好")) {
  chunks.push(c);                                    // 假模型：1 个 chunk
}
await new ScriptedChatModel({ script: [reply("第一"), reply("第二"), reply("第三")] })
  .batch(["q1", "q2", "q3"]);

// ⑤ profile 与 config
console.log(new ScriptedChatModel({ script: [reply("x")] }).profile);   // 假模型：{}
class TagProbe extends BaseCallbackHandler {
  name = "TagProbe";
  async handleChatModelStart(_llm: any, _m: any, _rid: string, _pid?: string,
                             _extra?: any, tags?: string[], metadata?: any, runName?: string) {
    console.log(tags, metadata, runName);   // tags/metadata 只能从回调看见
  }
}
await new ScriptedChatModel({ script: [reply("收到。")] }).invoke("你好", {
  tags: ["ch02"], metadata: { user_id: "u-42" }, callbacks: [new TagProbe()], runName: "my_run",
});
```

实测输出（Python，2026-10-16 复核轮，`langchain` 1.4.2 / `langchain-openai` 1.7.2 / Python 3.14.2；**节选**，超长行做了折行、内容未改）：

```text
① 模型初始化的三个角度：提供商库 / init_chat_model / 本地 Ollama
    ChatOpenAI(model='gpt-4o') → ChatOpenAI，model_name='gpt-4o'
    init_chat_model('openai:gpt-4o') → ChatOpenAI（前缀 openai 自动选中了 ChatOpenAI）
    底层实际用的 base_url = https://api.deepseek.com/v1
      init_chat_model('deepseek:deepseek-chat') → ImportError: Initializing ChatDeepSeek
        requires the langchain-deepseek package. Please install it with `pip install langchain-deepseek`
      init_chat_model('qwen-plus') → ValueError: Unable to infer model provider for
        model='qwen-plus'. Please specify 'model_provider' directly.

② invoke 的三种入参形态，与模型实际收到的消息（.seen 观测）
  [字符串] 模型收到 1 条：['HumanMessage']
  [dict 列表] 模型收到 2 条：['SystemMessage', 'HumanMessage']
  [消息对象列表] 模型收到 2 条：['SystemMessage', 'HumanMessage']
  单条 dict → ValueError: Invalid input type <class 'dict'>.
               Must be a PromptValue, str, or list of BaseMessages.

③ 返回值 AIMessage 的字段结构
    content            = '2 + 3 * 2 = 8'
    tool_calls         = []
    response_metadata  = {}
    usage_metadata     = None
    id                 = lc_run--…   ← 框架自动生成的运行 ID（后半段每次不同）
    tool_calls = [{'name': 'get_weather', 'args': {'city': '上海'}, 'id': 'call_1', 'type': 'tool_call'}]

④ 四种调用形态：invoke / stream / batch / ainvoke
  invoke  → '一次性返回。'
  stream  → 1 个 chunk：['流式输出。']
  batch   → ['第一', '第二', '第三']
  ainvoke → '异步返回。'

⑤ profile 属性与 config 参数（tags / metadata / callbacks）
    假模型 profile = None（基类不带画像）
    init_chat_model('openai:gpt-4o').profile（节选）
      = {'max_input_tokens': 128000, 'max_output_tokens': 16384,
         'tool_calling': True, 'structured_output': True}
    [回调] tags     = ['ch02', 'demo']
    [回调] metadata = {'user_id': 'u-42', 'ls_provider': 'scriptedchatmodel',
                       'ls_model_type': 'chat', 'ls_integration': 'langchain_chat_model',
                       'lc_versions': {'langchain-core': '1.6.11', 'langchain': '1.4.2'}}
    返回对象类型 = RunnableBinding（不再是 ScriptedChatModel）
```

第 ② 节的三行「模型收到 N 条」就是本章最核心的证据：**两种列表写法在模型这一侧完全一样；字符串写法只产生一条 `HumanMessage`**——三种写法的差别只在客户端封装，模型侧最终都只看到消息对象。第 ③ 节里 `response_metadata = {}`、`usage_metadata = None` 是假模型的产物，不是框架漏填。

## 四、常见坑与边界条件

以下八条坑全部来自本机实测或源码核对，每条都附了复现方式与排查方法；越靠前的踩得越快。

**1. provider 前缀拼错，报错信息指向的是「包」而不是「前缀」。** 实测 JS 侧 `initChatModel("deepseek:deepseek-chat")` 抛的是 `Unable to import @langchain/deepseek`（中译：无法导入 `@langchain/deepseek`）——**前缀名与包名不是简单拼接**：实测 `openai` → `@langchain/openai`、`anthropic` → `@langchain/anthropic`、`ollama` → `@langchain/ollama`；读本机已装包源码（`langchain` 1.5.11 的 `chat_models/universal`）还能看到 `azure_openai` 也指向 `@langchain/openai`、`bedrock` 指向 `@langchain/aws`。Python 侧同一件事抛 `ImportError: Initializing ChatDeepSeek requires the langchain-deepseek package`（中译：初始化 `ChatDeepSeek` 需要 `langchain-deepseek` 包）。看到这类错，先去装包，别改前缀。

**2. 参数名写错不会报错，只会静默失效——本章最容易白耗一天的就是这条。** 2.2 说过 `init_chat_model` 不校验 `**kwargs`，实测确认了后果（构造层，`langchain` 1.4.2 / `langchain-openai` 1.7.2 / `langchain-anthropic` 1.7.6，本机可复现）：

| 你写的 | 实测结果 |
|---|---|
| `init_chat_model('openai:gpt-4o', api_key=…, api_base='https://api.deepseek.com/v1')` | **构造成功**。`api_base` 被挪进 `model_kwargs`，`openai_api_base` 仍是 `None`，请求照旧打到 `https://api.openai.com/v1`；只有一条 `UserWarning: api_base is not default parameter` |
| `init_chat_model('openai:gpt-4o', api_key=…, temperture=0)`（拼错） | 同上：静默进 `model_kwargs`，`temperature` 保持 `None` |
| `init_chat_model('anthropic:…', api_key=…, totally_bogus_kwarg=123)` | 同上：只有 warning，不抛错 |

机制：`BaseChatModel` 的 pydantic 配置是 `extra='ignore'`，未知字段本身不报错；集成构造时把挑剩的 kwargs 整包塞进 `model_kwargs`，顺手打一条 warning（`langchain_core/utils/utils.py`）。而 `UserWarning` 默认只往 stderr 印一次、不中断执行，日志里极易被划过去。**所以「设了却不生效」优先怀疑参数名**，验证方法是把字段打出来看：`print(m.openai_api_base, m.temperature, m.model_kwargs)`——写对了字段有值、`model_kwargs` 是空的；写错了正好反过来。上面三行都是**构造层核对**（不发请求、不需要 Key），脚本与原始输出在 `_实测输出核验/ch02_kwargs_构造层核对.py` / `.txt`。

另一件事仍然成立：**参数名随集成变**。绝大多数平台兼容 OpenAI 接口规范，没有专用集成时把模型名和地址塞进 `openai` 前缀即可（示例实测：`model="deepseek-chat", model_provider="openai", base_url="https://api.deepseek.com/v1"` → 底层是 `ChatOpenAI`，`openai_api_base` 就是传进去的地址）。但 `ChatDeepSeek` 的地址参数叫 `api_base`（官方 reference 核对，本机未装 `langchain-deepseek`、**未实测**）——把它原样传给 `ChatOpenAI`，落到的就是上面那张表的第一行。

**3. 环境变量名每个 provider 一套；而「不传 `api_key` 会不会在构造时就报错」取决于集成。** OpenAI 系会：Python 侧 `init_chat_model("openai:gpt-4o")` 直接抛 `OpenAIError: Missing credentials. Please pass an api_key, workload_identity, admin_api_key, or set the OPENAI_API_KEY ...`（中译：缺少凭据，请传入 `api_key`，或设置 `OPENAI_API_KEY` 环境变量），JS 侧 `new ChatOpenAI({...})` 抛同一条——都不是等到调用才失败。**但 Anthropic 不会**：本机实测 `init_chat_model("anthropic:claude-sonnet-4-5")` 在无 `api_key`、环境里也没有 `ANTHROPIC_API_KEY` 的情况下**构造成功**，报错推迟到第一次调用。所以「构造通过」不等于「凭据没问题」，别拿 OpenAI 的行为当跨集成的通则。**注意字段名**：`@langchain/openai` 1.6.2 上认的是**顶层 `apiKey`**，写 `openAIApiKey` 会被当成没传而报同一个错。命名规律是 `{PROVIDER}_API_KEY`，但**别猜**：`langchain-deepseek` 读 `DEEPSEEK_API_KEY`，`ChatTongyi` 读 `DASHSCOPE_API_KEY`，名字和 provider 名并不总是对得上。

**4. Ollama 必须先起服务，且要先 `pull` 模型。** `ChatOllama(model="deepseek-r1:1.5b")` 的构造不需要服务在线，所以「构造成功」不代表能用。默认地址 `http://localhost:11434`；服务没起是连接失败，模型没 `pull` 是模型不存在，两种报错要分清楚。本机无 Ollama，**未实测**。

**5. `stream` 的 chunk 是增量，不是片段。** 真实模型逐 token 产出多个 chunk——**2026-10-16 已实测**：智谱 `glm-4.5-air` 一次请求吐 **194 个 chunk**，且 `usage_metadata` **只出现在倒数第二个 chunk**（下标 192）上，别每个 chunk 都读 token 数。本教程假模型只吐 1 个、且类型是 `AIMessage` 而非 `AIMessageChunk`（chunk 数为示例实测；**类型一项为源码核对，示例只打印了数量与内容**）。所以：**别用假模型的 chunk 数去推断真实分块粒度**，也别写死 `AIMessageChunk` 类型判断；另外别忘了把 chunk 拼起来才是完整回答。注意 `chunk.content` 与 `chunk.text` 都能读文本，但多模态场景下 `content` 可能是 list——第 3 章 Message 与提示词模板讲了 `content_blocks` 这个统一口径。

**6. `dict` 形态必须传列表。** 传单条 dict 是硬报错，且**两语言报错形态不同**：Python 是 `ValueError: Invalid input type <class 'dict'>. Must be a PromptValue, str, or list of BaseMessages.`（中译：输入类型非法，必须是 `PromptValue`、`str` 或 `BaseMessage` 的列表），JS 是 `TypeError: promptValue.toChatMessages is not a function`（中译：`promptValue.toChatMessages` 不是一个函数）——JS 那条信息完全看不出问题在哪，排查时要有心理准备。

**7. `with_config()` 之后对象类型就变了。** 实测 Python 与 JS 都返回 `RunnableBinding`，`isinstance(obj, ChatOpenAI)` / `obj instanceof ChatOpenAI` 都会是 `False`。它照样能 `invoke`，但如果你后面写了类型判断或按类取属性，就会在这一步断掉；要拿回原对象用 `.bound`。

**8. 本章的未实测范围。** 真实 provider 的 `invoke` / `stream` 真实分块 / token 计费**已于 2026-10-16 用智谱 OpenAI 兼容端点补测**（194 个 chunk、`usage_metadata` 与 `cached_tokens` 齐全，见 2.5 节与第四节坑 5，以及 `code/README.md`「真实模型实测」）。**仍未实测**的是：`langchain-deepseek`、`langchain-ollama` 的参数细节（本机未装、无本地 Ollama）——所以坑 2 里「`ChatDeepSeek` 的地址参数叫 `api_base`」只有官方 reference 背书；`configurable_fields` / `config_prefix` 的运行时覆盖行为（2.2 表里那两行是**源码核对（docstring / `_ConfigurableModel` 实现）**，真正发请求的覆盖未跑）；以及**模型质量类**表现（回答准确性、指令遵从度）——本轮只测了协议层与框架机制，没做质量评测。本章的「实测」结论分三类：**构造层实测**（不发请求，如 `init_chat_model` 的类映射、`profile` 内容、坑 2 与坑 3 的参数名和凭据行为——跨集成对照用的是本机已装的 `langchain-openai` 1.7.2 与 `langchain-anthropic` 1.7.6）、**字段核对**（`model_fields` 的默认值与 alias）、**假模型实测**（调用链路）。

## 五、关键结论

1. **三个初始化角度不是按「厂商」切，而是按「谁选类 / 模型在哪」切**——三种写法的失效方式完全不同，分清楚走的是哪条路，出错时才知道该查什么。
2. **`init_chat_model` 的参数分两类：自己的四个 vs 原样转发的 `**kwargs`**——**转发意味着这一层不校验参数名**，而写错名字**不报错、只静默失效**（实测见坑 2）。这才是「明明设了却不生效」类问题的根源，比「报错」更难查。
3. **`AIMessage` 要读两层**：「模型说了什么」是 `content` / `tool_calls`；「花了什么代价」是 `response_metadata` / `usage_metadata`（由 provider 驱动填，假模型为空）——只读 `content`，会把 token 账和工具调用意图全丢掉。
4. **`stream` 的 chunk 是「增量」不是「片段」**：要靠循环拼接，别用假模型的 chunk 数推断真实分块粒度。
5. **`profile` 与 `config` 分工**：前者是模型的能力画像（声明过才有，未知模型是 `None`）；后者是单次调用的配置入口——`tags` / `metadata` / `run_name` / `callbacks` 只记账，`max_concurrency` / `recursion_limit` / `configurable` 分别改并发、递归上限与实际模型参数。

## 本章要点回顾

- **三个初始化角度**见**图 3**：提供商库 / `init_chat_model` / 本地 Ollama。
- **`init_chat_model` 只有四个自己的参数**——`model` / `model_provider` 选类，`configurable_fields` / `config_prefix` 是运行时覆盖的**白名单**与**键名前缀**（传了 `model` 又不声明就是固定模型）；`temperature` / `api_key` / `base_url` / `max_tokens` 都是转发的 `**kwargs`。实测 `ChatOpenAI` 的 `temperature` 默认是 `None`（**与官方文档参数表的 0.7 不一致，以实测为准**）。
- **转发不校验参数名**：给 `ChatOpenAI` 传 `api_base`、或把 `temperature` 拼错，**构造全部成功**，值静默落进 `model_kwargs`，只有一条 `UserWarning`（基类 pydantic 是 `extra='ignore'`）——「设了不生效」先 `print(m.openai_api_base, m.temperature, m.model_kwargs)` 对照。`api_key` / `base_url` 在 OpenAI 与 Anthropic 集成里都是别名（本名 `openai_api_base` / `anthropic_api_url`），DeepSeek 的地址参数则是 `api_base`（官方 reference，未实测）。
- **实测 provider 列表 28 个**（官方文档列的是旧集合），且会随版本变——拼错时框架会把全表打给你。
- **`invoke` 三种入参归一化一致**见**图 4**：字符串 → 1 条 `HumanMessage`，`dict` 列表 / 消息对象列表 → 2 条（System + Human）；**单条 dict 直接报错**。
- **`AIMessage` 七字段**：`content` / `tool_calls` / `invalid_tool_calls` / `response_metadata` / `usage_metadata` / `additional_kwargs` / `id`；假模型下 `response_metadata` 为空、`usage_metadata` 为 `None`（JS 为 `undefined`）。**`id` 分语言**：Python 假模型由框架填 `lc_run--…`，**JS 假模型不填（`undefined`）**——别按「假模型只填前三个」一刀切。
- **四种调用形态**：`invoke` / `stream` / `batch` / `ainvoke`；**JS 没有 `ainvoke` 这一套**（三个方法本来就返回 `Promise`）；假模型 `stream` 只吐 1 个 chunk，真实模型实测 194 个。
- **`profile`**：实测 `openai:gpt-4o` → `{'max_input_tokens': 128000, 'tool_calling': True, 'structured_output': True, ...}`；未知模型 → `None`；假模型 Python `None` / JS `{}`。
- **`config`**：`tags` / `metadata` / `run_name` / `callbacks` 只影响记账，实测透传到 `on_chat_model_start`；框架自动补 `ls_provider` / `ls_model_type` / `ls_integration` / `lc_versions`。
- **`with_config()` 返回 `RunnableBinding`**，不再是原来的模型类，`isinstance` / `instanceof` 判断会失败；取回原对象用 `.bound`。
- **坑共 8 条**（第四节），最常踩的是这四条：provider 前缀报错指向**包名**而不是前缀；**参数名写错不报错、只静默失效**；不传 `api_key` 是否在**构造期**失败**取决于集成**（OpenAI 系会、Anthropic 不会）；`dict` 形态必须传列表（JS 报错信息看不出问题）。
- **已补测（2026-10-16，智谱端点）**：真实 provider 的 `invoke`、真实 `stream` 分块（194 chunk）、token 计费与缓存字段（`usage_metadata` / `cached_tokens`）。详见 `code/README.md` 的「真实模型实测」。
- **仍未实测**：DeepSeek 与 Ollama 的参数细节（本机无 Ollama、未装 `langchain-deepseek`）；`configurable_fields` / `config_prefix` 的运行时覆盖（只有源码核对）；模型质量类指标（工具选择倾向、提示词遵从度）。
- **示例全部离线可跑**（假模型）。补测与核对的脚本、原始输出都在 `_实测输出核验/`：真实模型补测在其 `真实模型/` 子目录，本章的参数名与凭据核对是根目录的 `ch02_kwargs_构造层核对.py` / `.txt`（只构造、不需要 Key）。
