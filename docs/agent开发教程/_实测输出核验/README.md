# 实测输出核验报告

> 核验日期：2026-10-16 · 环境：Windows / Python 3.14.2（`code/python/.venv`）/ Node v24.11.0 / pnpm 10.20.0
> 本目录是**一次性核验产物**，不是教程正文。所有 `.txt` 是脚本 stdout 的原样重定向，未编辑。

---

## 0. 本目录里有什么

| 路径 | 内容 |
|---|---|
| `python/*.txt` | 17 个 Python 示例（02–18）的原始 stdout+stderr，逐个 `exit=0` |
| `typescript/*.txt` | 17 个 TypeScript 示例（02–18）的原始 stdout+stderr，逐个 `exit=0` |
| `typescript/_typecheck.txt` | `npx tsc --noEmit` 的完整报错（**exit=1，45 个 error TS**） |
| `真实模型/00_connectivity.*` | 智谱 key 的连通性与可用模型探测 |
| `真实模型/01_verify_untested_claims.*` | 文档标注「未实测」的 5 项声明（A–E）真实模型验证 |
| `真实模型/02`、`03` | `with_structured_output` 的 `method` 行为（前两版，含踩坑记录） |
| `真实模型/04_wire_capture.*` | httpx 层抓取**真正上线的 JSON 请求体**（Python ChatOpenAI） |
| `真实模型/05_js_provider_subclass.txt` | 同上，JS 侧（本地反代抓包） |
| `真实模型/06_ch09_snapshot_count.*` | 复现 ch09:182 的「42 个快照」断言 |
| `真实模型/js/` | 独立小包（`@langchain/openai` 1.6.2），**未改动教程的 `package.json` / lockfile** |
| `截图/*.png` | 6 张模型输出截图（2× 清晰度）：`00-示例运行清单`、`01-智谱key连通性与可用模型`、`02-真实模型验证未实测声明`、`03-Python上线请求体`、`04-JS上线请求体`、`05-ch09快照数复现` |
| `截图页面/*.html` + `_build_screenshot_page.py` + `_render_screenshots.py` | 截图的生成物与脚本（读 `.txt` 渲染，无手写内容），可重跑 |

### ⚠️ API Key 的存放与处置

Key 明文**只**存在于 `../code/.secrets.log`，该路径被 `.gitignore:13`（`*.log`）忽略，已用
`git status --ignored` 与全目录 grep 双重确认：**没有任何 `.txt` / `.md` / `.py` / `.html` 含 key 明文**。
核验脚本一律从该文件读取，命令行参数与输出里都不出现。

**这个文件现在还留在磁盘上。如不再需要重跑真实模型验证，请删掉它**：

```bash
rm "docs/agent开发教程/code/.secrets.log"
```

---

## 1. 运行结论

**34 / 34 示例全部跑通，退出码 0。** 与 `code/README.md:85`「17 + 17 全部通过」一致。

但有一处 README 没说、也跑不出来：**`pnpm run typecheck` 失败**。

```
npx tsc --noEmit   →  exit=1，45 个 error TS
  07_tools.ts        1     14_deep_agent.ts    1
  11_state_graph.ts 15     15_filesystem.ts    1
  12_persistence.ts 11     16_delegation.ts    2
  13_hitl_stream.ts 11     18_multiagent.ts    3
错误码分布：TS2345×18、TS2769×14、TS2322×13
```

示例能跑是因为 `tsx` 不做类型检查。全仓**没有任何地方声称 typecheck 通过**（`typecheck` 只出现在 `code/README.md:52` 的命令清单里），所以这不算「文档说谎」；但 `code/README.md:121`（差异清单 #8）与 `ch18:49` 把「JS 必须显式 `ends: [...]`，否则编译报 `UnreachableNodeError`」写成**已验证机制**——`_typecheck.txt` 里 45 条错误**没有一条**是 `UnreachableNodeError`，11/12/13/18 的报错恰恰是「没写 `ends` 之外」的类型不匹配。这条属于**读源码得出的、被标成实测**。

---

## 2. 真实模型验证：文档标「未实测」的部分，现在测了

智谱 key 可用模型实测：`glm-4.5-air` / `glm-4.6v` / `glm-4-plus` / `glm-4.5` / `glm-4.6` 全部返回 200 且带 `usage`。

### 2.1 逐条判定

| 文档声明 | 出处 | 实测结果 | 判定 |
|---|---|---|---|
| 「假模型 `stream` 只吐 1 个 chunk；真实模型分多块（未实测）」 | `code/README.md:61`、ch02 | `glm-4.5-air` 一次请求吐 **194 个 chunk**；`usage_metadata` 只出现在倒数第 2 个 chunk（下标 192） | ✅ **成立** |
| 「token 与成本字段需要真实模型返回的 usage 元数据，本机无 API Key，未实测」 | `code/README.md:103`、ch10:59 | `usage_metadata = {input_tokens:18, output_tokens:128, total_tokens:146, input_token_details:{cache_read:4}}`；`response_metadata.token_usage` 含 `cached_tokens` | ✅ **成立，且字段齐全** |
| 「缓存命中率与真实计费需要真实模型与 API Key，本机没有账号」 | ch09:95 | 同一长前缀连发 3 次：`cached_tokens` = **4 → 780 → 780**（input 恒 793） | ✅ **成立，命中率可直接观测** |
| 「`method="json_schema"` 的真实差别由 provider 子类实现（如 ChatOpenAI 会改用 `response_format` 的 json_schema 模式）——需真实模型，未实测」 | `code/README.md:104`、ch04 ③ | 抓真实请求体：Python `ChatOpenAI` 与 JS `ChatOpenAI` **都**发 `response_format={type:json_schema, strict:true}` 且**不带** `tools`；而 `function_calling` 发 `tools=[Person] + tool_choice` 且不带 `response_format` | ✅ **成立（双侧、抓包级证据）** |
| 「基类实现里 `method` 被直接丢掉，三条路径都走 `bind_tools + tool_choice`」 | ch04 ③ | 用子类覆盖 `bind_tools` 复测假模型基类：`None` / `function_calling` / `json_schema` 三档的额外参数**完全相同**（`['ls_structured_output_format','tool_choice']`），均无 `response_format` | ✅ **成立** |
| 「换成真实模型后，示例里的断言式输出会变」 | `code/README.md:158` | `create_agent` + `glm-4.5-air`：消息序列仍是 Human → AI(tool_call) → ToolMessage → AI(final) 4 条，**结构没变**；变的是 content 文本（模型会先说一句「我来帮您查询」再调工具） | ⚠️ **部分成立**：结构稳定，别把「会变」理解成「序列会变」 |
| ch09:182「本机实测（6 轮、`trigger=("messages", 8)`）：最终状态 8 条，而 `get_state_history` 的 **42 个快照**里仍能翻出第 1 轮的长工具输出原文」 | ch09 | 配 `InMemorySaver` 重建该场景：最终状态 **8 条** ✅、快照总数 **42** ✅、含第 1 轮 `[svc-0]` 原文的快照 **12 个** ✅、当前状态已无原文 ✅。假模型与真实摘要模型两组数字**完全一致**（快照数是结构量，与模型无关） | ✅ **精确成立** |

**净结论：教程诚实度很高。** 凡是明确标了「未实测」的，用真实模型验证下来**全部成立**，没有一条被推翻；连最细的「42 个快照」这种数字都精确复现。

### 2.2 真实模型暴露出文档没写的两件事（建议补进正文）

1. **provider 子类上「缺省 method」就是 `json_schema`，不是工具策略。**
   `ChatOpenAI().with_structured_output(Person)`（不传 `method`）实际发的是 `response_format: json_schema strict:true`，**不带 tools**。
   而差异清单 #13（`code/README.md:126`）写「结构化输出默认策略 | Python 侧：工具策略（脚本模型可跑通）」——那句只对**假模型基类**成立。读者极易把它当成通用结论抄到真实 provider 上，一抄就踩坑。

2. **第三方 OpenAI 兼容端点会无视 `strict` JSON schema。**
   `glm-4-plus` 收到 `response_format: json_schema strict:true` 后照样返回散文（`"好的，从"张三是一名…"`），langchain 侧直接 `ValidationError` / `SyntaxError`；`json_mode` 下模型还把字段名 `occupation` 自己改成了 `profession`。
   更危险的是 `function_calling` 在 `glm-4-plus` 上**静默返回 `None`**（模型没发 tool_call，解析器不报错）——正是 ch04 ④ 说的「不报错、不告警，只是 None」，在真实模型上以另一种方式复现了。

3. **`include_raw=True` 兜不住 provider 层的解析失败。**
   ch04 ④ 称「`include_raw` 把抛错变成返回值，不会一条坏数据打断整批」。真实 `ChatOpenAI` + `response_format` 路径下，失败发生在 SDK 的 `raw_response.parse()` 里，**早于** langchain 的解析步骤，`include_raw=True` 照样抛 `ValidationError`。只有 `function_calling` 路径能被 `include_raw` 兜住（返回 `{parsed:None, parsing_error:None, raw:...}`——注意 `parsing_error` 也是 `None`，等于把错误彻底吞了）。

---

## 3. 文档与实测不一致清单（这是主要问题）

问题**不在假模型跑不出结果**（34/34 全绿），而在**正文把单边语言的输出写成了双语言共同实测**，以及**版本号/免责声明过期**。按严重度分三档。

### 3.1 高：结论性错误或自相矛盾

| # | 位置 | 正文说 | 实测是 |
|---|---|---|---|
| 1 | `code/README.md:99` | 「Python 13/13 通过，TypeScript 13/13 通过」 | 同文件 `:85` 已写「17 + 17 全部通过」。**README 内部自相矛盾**，`:99` 是只有 13 例那轮的旧文案 |
| 2 | `code/README.md:103`、`README.md:228`、`docs/README.md:27` | 「本机无 API Key」「不需要 API Key」 | 现在本机**有**可用 key，且本报告 §2 已用它实测。大量「未实测」免责以此为前提，需重新界定范围 |
| 3 | `code/README.md:106` | 「`MCPAdapter` 需要额外安装 `langchain[mcp]`（本机已装、可 import，会打印 beta 警告）」 | venv 里**没有** `mcp` / `fastmcp`，`import langchain.mcp` 抛 `ModuleNotFoundError`；`requirements.txt:27` 该行是注释状态 |
| 4 | `code/README.md:128`（差异清单 #15） | 「工具抛异常的默认行为：Python 异常**原样抛出**，整个调用失败 / TS `ToolNode` 吞成 error `ToolMessage`」 | 当前 `07_tools.py` 与 `07_tools.ts` **两侧都挂了捕获中间件**，`P07:25-29` / `T07:27-33` 行为完全一致（都转 ToolMessage 并继续）。Python「原样抛出」那半边**在输出里没有证据**，只是脚本自己打印的假设性解说 |
| 5 | `ch07:315/339`、`code/README.md:129`（#16） | 「改从 `@langchain/langgraph` 导入即恢复正常（**已实测回读成功**）」 | 实跑源码 `code/typescript/07_tools.ts:14` 仍从 `"langchain"` 导入；`T07:15` 只有 `TypeError: this.store.batch is not a function`，**TS 侧从未有回读成功记录**；`_typecheck.txt:1-3` 还记着 `InMemoryStore` 不满足 `BaseStore`。正文展示的 import 不是产出该输出的代码 |
| 6 | `code/README.md:69`、`ch10:33/47/315` | 「一次 agent 调用产生 **7 个 run**」 | Python 是 7（`P10:12`）；**TypeScript 是 10 个 run**（`T10:15`），树形 10 节点、chain 一律无名、多 2 个 chain 子节点。正文按单侧写且未标差异 |
| 7 | `code/README.md:73`、`ch14:94` | 「工具节点注册 9 个但模型只绑定 8 个」 | 「8 个」两侧一致；**「9 个 / 差集 `execute`」只有 Python 测得**，`T14:14` 自己写明「Python 侧实测」。README 与 ch14 未披露此差异 |
| 8 | `ch15:179` | 「TypeScript 侧语义**完全一致**」 | 被 `T15:8-11` 直接推翻：JS 四条返回**各不相同**，`read_file` 返回 `[object Object]`、**无分页头**、grep 用 `1 occurrence(s)` 而非 `1 instance(s)`。`ch15:33-40` 标「实测返回值的原样」实为 Python 单边且被截短 |
| 9 | `ch14:94` | 「文件系统钩子叫 `FilesystemMiddleware.before_agent`（Python，P 大写）」 | `P14:38-41` 四组节点里**没有** `FilesystemMiddleware`，它只出现在 JS（`T14:32-35`）；「P 大写」实指 `PatchToolCalls`。同句把 skills 节点写成 `SkillsMiddleware.before_agent`，JS 实为 **`before_model`** |
| 10 | `ch02:298`、`ch03:332/415`、`ch04:18`、`code/README.md:90` | `langchain-core` `1.6.4` | `P02:89` 实为 **`1.6.11`**（`code/README.md:85` 自己也写了 1.6.11，与 `:90` 的版本表冲突） |
| 11 | `code/README.md:93`、`README.md:213-214` | `langchain-openai` / `langchain-anthropic` = `1.6.5` / `1.7.4` | 实装 **1.7.2 / 1.7.6** |
| 12 | `ch09:180` | 「Python 是位置参数 `trigger=("messages", 8)`、**`keep=2`**」 | `SummarizationMiddleware` 的 `keep` 实为 `("messages", 4)`（`09_context.py:94`）；`keep=2` 属于 `ClearToolUsesEdit`（`:110`）。参数张冠李戴 |
| 13 | `ch13:72/248/260` | 「同一张图，**七种投影** / 七档」 | Python 实跑 4 档（`P13:26-29`），TS 实跑 3 档且**无 debug**；`checkpoints` / `tasks` 两边都没跑过 |
| 14 | `README.md:338` | 差异清单「16 条」 | `code/README.md:114-130` 实为 **17 条**（`:381` 已登记第 17 条） |
| 15 | `docs/README.md:27` | 「框架线为 18 章」 | 同文件 `:10` 与实际目录都是 **19 章** |
| 16 | 顶层 `README.md:5/88` vs `AGENTS.md` | 「919 文件 / 579 篇」 vs 「916 / 576」 | 互斥；实际（排除 `node_modules` / `.venv`）**972 文件 / 582 篇 md** |

### 3.2 中：引用输出后被改写，或把源码阅读写成实测

- **ch06:21-31**「实测触发顺序」块是 9 步，真实是 **10 步**——`P06:4-13` / `T06:4-13` 第 6 项 `└─ 工具函数体真正执行` 被删，7~10 被重编号为 6~9。
- **ch04:371-425** 自称「两个示例的真实运行输出」，实为折叠改写：`:400` 把 `tool_calls=[('Person', {'name':…,'age':'三十',…})]` 缩成 `tool_calls=[('Person', age='三十')]`；`:419` 把三行并写并替换真实值；`:422` 用「同 Python」替代真实六行消息序列。
- **ch04:109 / :415** 引用的报错全文（`…'description' in undefined` / `as a member`）在输出里被源码的 `.slice(0, 60)` / `.slice(0, 80)` **截断**（`T04:22` 止于 `in unde`，`T04:30` 止于 `as a me`）。补全后的文本不是实测文本。
- **ch08:216-219** 把 TS 输出套上 Python 函数名并凭空改维度：写 `embed_query('退换货') → 维度 16`，Python 实测是 `embed_query('键盘到哪了')` **维度 8**，TS 是 `embedQuery` **维度 4**。Python 真实 score（`0.5845` / `0.4035`）正文从未出现。
- **ch08:149-153** 样例工具名写 `search_docs`（TS 名），Python 实测是 `search_knowledge`。
- **ch08:173/57** CSVLoader「3 个 Document」——TS 侧是 **2 个**（语料不同），与 `ch08:162`「两套示例一一对应」矛盾。
- **ch08:191-211**「两种实现的真实差别」——TS 用另一段文本、`chunkSize` 40、separator `\n`，两种切分器输出完全相同的 3 块、无 WARNING；「38>30」「保证不超」只在 Python 成立。
- **ch10:38-44** 复述树写 `[llm] ChatModel`，实测 `[llm] ScriptedChatModel`；`:53` 说「model chain 输出里能看到 `{"sku":"A-1"}`」，但 `TraceRecorder` 只存 name/type/parent/children/t0/t1，两份输出**无任何 input/output**。
- **ch10:154**「`run_name`/`tags`/`metadata` 不配 LangSmith 不产生任何效果」——`P10:4` 根节点名正是 `run_name` 给的，`P02:88-89` 也证明 tags/metadata 进了回调。且 TS 侧 10 号树根名为 `chain`（`runName` **未生效**）这一差异正文没写。
- **ch11:56/62**「`add_messages` 追加 + **按 ID 去重**」——只证明了追加，去重从未被测。
- **ch11:248 / code/README.md:132**「节点名跨语言、**跨版本**都会变（实测）」——跨语言证据在 13 不在 11；「跨版本」无任何证据，只跑过 1.2.12 / 1.4.17 一个版本。
- **ch11:66/241/255**「返回空列表清不掉」那行是 `11_state_graph.py:234` **硬印的字面量**，不包 `Overwrite` 的分支从未执行；TS 侧连这行都没有。
- **ch13:50/61/246** 副作用日志——Python 3 行（含「3. 调用扣款接口：199 元」），**TS 只有 2 行**，`13_hitl_stream.ts:56` 的 charge 节点根本没写日志。故「真副作用拆独立节点、只执行一次」只有 Python 证据。
- **ch13:103/227** B 组「只剩进出两条」——Python 确为 2 条，**TS 只有 1 条且 `node=model_request`（子图内部节点名）**，按 ch13:238 自己给的判据，JS 侧会被判成「内部消息透传了」，与正文结论相反。
- **ch16:66/259/270**「SubAgent 实测 11 个字段（实测签名）」——11 项是 `16_delegation.py:70-83` **硬编码 print**，不是从库里探测出来的；`T16:16` 自己写明「Python 侧实测 11 个，JS 侧为同名 camelCase」。ch14 的「HarnessProfile 7 字段」同理（`14_deep_agent.py:158-167` 硬编码，TS 侧从未打印字段数）。
- **ch15:233**「LangSmithSandbox 导入路径验证」——两语言源码**都没 import** 它，只是表内文字。
- **ch05:217-230**「实测输出」整块非逐字（格式被重写、P05:17-20 与 P05:36 的关键证据被省略）；日期「2026-09-24」在本轮基线里不存在。
- **ch07:190** docstring 与 `P07:5` 实际打印的（含 `Args:` 段）不同，却被用来支撑 Args 解析结论。

### 3.3 低：挂「实测」名义但输出里无证据（需逐条改口径或补测）

这些**不一定是错的**，很多是真读源码读出来的——问题在于被冠以「实测」名义。抽样：

- ch02：`model_fields["temperature"].default is None`、provider 列表 28 个、`gpt-4o` profile 25 键、假模型 chunk 类型是 `AIMessage` 而非 `AIMessageChunk`、不传 `api_key` → `OpenAIError`（源码恒传 `sk-placeholder`）。
- ch03：`KeyError: missing variables {'q'}`、双花括号转义、`content_blocks` 是 property 且不缓存。
- ch04：TS `No tool call found with name extract.`（**T04 全文没有工具名不匹配的测试行**）、`extract-1` 自增、JS 枚举非法值原样通过、`Input is not an AIMessageChunk`。
- ch05/06：`interrupt_before/after`、`debug`、`cache`、`transformers` 的「实测签名」；「64 个导出」；「换模型不影响钩子顺序」（第二次运行没挂 trace 中间件，无任何顺序打印）。
- ch11/12/13：`InvalidUpdateError: Can receive only one value per step.`、`UnreachableNodeError`、`ReactAgent` 不是 Runnable、`SqliteSaver` import 失败、节点里用 `runtime.store`（**全 `code/` 目录 grep 零命中**，没有任何示例把 store 挂到图上）、传 list-mode 时 `(mode,payload)` vs `[mode,payload]`、JS `StreamMode` 多 `"tools"`（实为读 `dist/pregel/types.d.ts`）。
- ch14/15/16：`create_deep_agent` 18 参数「按实测签名给全」、`excluded_middleware` 排不掉、`SkillsMiddleware` 要从 `deepagents.middleware` 导入、`FilesystemMiddleware` 六参数与 `20000/50000/3600/1000`（import 后从未使用）、`permissions × LocalShellBackend` 抛 `NotImplementedError`、**权限「首次匹配即生效 / 未命中默认 allow」**（`P15:33-42` / `T15:35-44` 全是 print 出的结论文字，示例从未 invoke 带 permissions 的 agent，无任何拦截/放行观测）。
- ch17/18/19：JS 必须取 `.graph`（`T18:9` 反说「可以直接当节点用」）、`ToolException` 仍在包里、顶层不导出 `SkillsMiddleware`、`MemoryMiddleware` 四参数含 `add_cache_control`、Skills 在默认后端 `invoke(files=...)` 也能用。
- `ch08:262`「本机实测 0.4.2 import 打印 DeprecationWarning」——两份 08 输出首行即 ① 标题，**无该警告**。

### 3.4 版本锚点

`code/README.md:89-97` 版本表里 **6 行正确、2 行过期**（#10、#11）。另：`ch02:257` 的 `langchain-openai 1.6.5 / Python 3.13.14`、`ch04:18` 的 `pydantic 2.13.5` 与本轮环境（1.7.2 / 3.14.2 / 2.14.1）不符——那是 2026-09-24 那轮的环境，`:85` 已声明本轮重跑，正文锚点未同步。

**注意本报告 §2 的 JS 实测用的是 `@langchain/openai` 1.6.2 + `langchain` 1.5.18 + `@langchain/core` 1.2.18**（独立小包，与教程锁定的 1.5.11 / 1.2.12 不同版本）。所以 §2.1 第 4 行的 JS 结论算「同生态实测补充」，不能直接替换教程正文的版本锚点。

---

## 4. 一句话总结

**代码没问题，文档有系统性的口径问题。**

34 个示例全绿；凡明确标「未实测」的，真实模型验证下来**一条没被推翻**，连「42 个快照」都精确复现——这套教程的免责纪律是认真的。

真正的毛病是另一类：**把 Python 单边跑出来的输出写成「双语言实测」**（§3.1 的 #6/#7/#8、§3.2 约 15 处），**把读源码得到的结论冠以「实测」**（§3.3 约 40 处，含差异清单 #8/#15/#16 三条），以及**过期未同步的版本号与「本机无 API Key」声明**。这三类都不会让读者跑不起来，但会让读者把「一边如此」当成「两边如此」、把「读来的」当成「跑出来的」——恰好是该教程自己反复警告的那件事。

---

## 5. 修复状态（2026-10-16 同日）

**上文列出的问题已全部落地修复。** 本节保留原样，作为「改了什么、为什么改」的底账。

| 类别 | 处理 |
|---|---|
| §2 的 7 条「未实测」 | 全部升级为**已实测**并填入真实数据（194 chunk / `cached_tokens` 4→780→780 / `usage_metadata` 结构 / provider 子类抓包 / 42 快照复现），另补 3 条真实模型新暴露的坑 |
| §3.1 的 16 条高危 | 逐条订正：版本表（1.6.4→1.6.11、1.6.5/1.7.4→1.7.2/1.7.6）、`13/13`→`17/17`、`langchain[mcp]` 改「未安装」、「本机无 API Key」按 **LangSmith 账号 vs 模型 Key** 重新界定、ch09 `keep` 张冠李戴、ch19 映射表 10→11 行、差异清单条数 16→18 |
| §3.1 的单边结论 | 全部标注归属：ch10「7 个 run」并列 JS 的 10 个、ch14「注册 9 个」标 Python 单边、ch15 删「TS 语义完全一致」改为逐条列 JS 实际返回、ch14 节点名改为**逐语言对照表**（含 `FilesystemMiddleware` 实属 JS、skills 挂 `before_model`）、ch13「七种投影」改为实跑档数 |
| §3.3 的约 40 条 | 引入**四级口径**并逐条改写：**示例实测 / 本机核对 / 源码核对 / 未实测**——「实测」现在严格等于「示例输出里能看到」。差异清单 #8/#15、ch11/ch18 的 `UnreachableNodeError`、ch11 的 `InvalidUpdateError`、ch12 的 `runtime.store`、ch15 的权限默认值、ch16 的 SubAgent 字段来源等均下调为源码核对 |
| 新增 | `code/README.md` 增「真实模型实测」「已知未通过项（tsc 45 errors）」两节与差异清单第 18 条；`_写作大纲与来源登记.md` 增第 18–22 条；`CONVENTIONS.md` 统计口径补 `.venv/` 排除 |

**同步产物**：`agent-frameworks-deep-dive.html` 已重跑，幂等已验证（连续两次构建 md5 一致）。

**没有做的事**：没有为了让 §3.3 的条目「名副其实」去补写实验（`InvalidUpdateError`、`UnreachableNodeError`、权限拦截、`tool_choice` 真实语义等）——它们仍标着「源码核对 / 未实测」。**这是诚实的标注，不是遗漏**：读者若需要这些结论，得自己补那一脚。

**改动面**：**27 个 Markdown**（含全部 19 章正文 + `code/README.md` + 教程 `README.md` + `docs/README.md` + 根 `README.md` + `AGENTS.md` + `CONVENTIONS.md` + `_写作大纲与来源登记.md` + 本报告）与 **1 个 HTML**（`agent-frameworks-deep-dive.html`）。示例代码（`.py` / `.ts`）**一行未动**，34 个示例仍全部 `exit=0`。
