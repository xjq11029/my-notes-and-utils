# DeepInfer 推理框架源码笔记

> **对象**：[`deepseek-ai/DeepInfer`](https://github.com/deepseek-ai/DeepInfer) —— DeepSeek 官方开源的大模型推理框架（Apache-2.0，仓库创建于 2026-10-16）。本笔记基于**本地源码快照**（`D:\资文件\大模型部署\DeepInfer`，HEAD `9bd9cf2`，2026-10-21 核对）逐文件整理，当前版本 `0.1.0`。
> **整理方式**：**源码阅读为主**，官方 [`README.md`](https://github.com/deepseek-ai/DeepInfer/blob/main/README.md) 与 [`doc/inference_deployment_qa.md`](https://github.com/deepseek-ai/DeepInfer/blob/main/doc/inference_deployment_qa.md) 交叉核对；**未在真机运行**（本机不满足最低硬件要求：Linux + NVIDIA SM100 / 昇腾 950），凡涉及运行结果的表述均为「源码推演」或「官方数据」，不当成实测。
> **章节结构**：每章按「这一章要解决的问题 → 机制与原理 → 源码走读 → 常见坑与边界条件 → 关键结论 → 本章要点回顾」组织；本目录是**源码分析**，采用「源码笔记目录」骨架（见 [`CONVENTIONS.md`](../../CONVENTIONS.md)）。
> **配图说明**：本目录不设 `assets/`，机制图统一用 **Mermaid `graph TD` 竖排**（VSCode / Typora 可直接渲染），时间线用 ```text 框线块；这样图与正文同源、可随代码修订，不产生位图维护负担。
> **数据来源分级**：正文关键事实以行内标注注明出处，取值 **官方**（仓库 README / 官方 Q&A / 发布说明）、**一手**（源码、测试、构建脚本）、**三方**（外部报道与社区讨论）。完整底账见 [`_来源与数据分级.md`](_来源与数据分级.md)。
> **路径约定**：正文中的源码路径均相对 DeepInfer 仓库根目录；行号以本地快照 `9bd9cf2` 为准，上游更新后可能漂移。

---

## 一句话版

**DeepInfer 是 DeepSeek V4.1-Flash 的「后厨运营系统」：C++ 调度器决定每步做谁的活，KV/State cache 决定半成品放在哪，V4 注意力与 MoE 决定每步怎么算，零开销异步调度让 CPU 排班与 GPU 计算重叠；开源版给的是核心引擎与离线推理，生产环境里的 KV 存储集群、P/D 编排与服务层四类负载均衡器并未随仓库发布（引擎内的 EPLB 除外）。**

---

## 章节目录

| 章 | 文件 | 主题 |
|---|---|---|
| 1 | [ch01_positioning.md](ch01_positioning.md) | 定位与全景：它解决什么问题、生产架构长什么样、开源边界在哪 |
| 2 | [ch02_startup_path.md](ch02_startup_path.md) | 代码地图与启动链路：从 `LLM.generate()` 到一次 GPU step |
| 3 | [ch03_scheduler.md](ch03_scheduler.md) | 调度器：连续批处理、chunked prefill、抢占与 DP 步型投票 |
| 4 | [ch04_kv_cache.md](ch04_kv_cache.md) | KV cache 与状态缓存：分页块、StateBlock、SWA 环与落盘布局 |
| 5 | [ch05_attention.md](ch05_attention.md) | 注意力栈：MLA、压缩 KV、稀疏索引（DSA）、SWA 与 YoCo |
| 6 | [ch06_moe_eplb.md](ch06_moe_eplb.md) | MoE、专家并行与 EPLB：逻辑专家、物理槽位与热专家复制 |
| 7 | [ch07_speculative_decoding.md](ch07_speculative_decoding.md) | 投机解码：DFlash、置信度头与变长验证 |
| 8 | [ch08_zos_batch_invariant.md](ch08_zos_batch_invariant.md) | 零开销异步调度与批不变性：气泡消除与可复现输出 |
| 9 | [ch09_sampling_structured_output.md](ch09_sampling_structured_output.md) | 采样与结构化输出：从 logits 到合法 JSON |
| 10 | [ch10_multimodal_parallel.md](ch10_multimodal_parallel.md) | 多模态与并行组：图片如何变 token，DP/CP/EP 怎么切 |
| 11 | [ch11_production_eval.md](ch11_production_eval.md) | 生产部署与评测：KV 存储、负载均衡、基准与正确性回归 |

**推荐阅读顺序**：先读 1、2、11 建立「它是什么、代码怎么跑、离生产还差什么」的全景；再按 3→9 沿一次请求的数据流推进；第 10 章可按需插入（做多模态或并行时再读）。

---

## 全系列主线

```text
LLM.generate()
  → EngineArgs / 四类 Config（第 2 章）
  → C++ Scheduler 选批、分配 KV block（第 3 章）
  → Worker 准备 InputMetadata（位置、slot、block table、SWA/压缩索引）
  → 主模型 forward：MLA + 稀疏索引 + SWA + MoE（第 5、6 章）
  → Sampler：验证上一轮草稿、采样本轮 token、生成下一轮草稿（第 7、9 章）
  → 结构化输出 mask 在采样前约束合法 token（第 9 章）
  → ZOS：本轮 GPU 计算与上轮后处理 / 下轮调度重叠（第 8 章）
  → 输出 RequestOutput，block/state 按引用计数回收（第 3、4 章）
```

贯穿全系列的三条暗线：

1. **省显存**：MLA 压缩 KV、state cache 环形复用、SWA 只存窗口、YoCo 丢弃 consumer 段 —— 第 4、5 章。
2. **省通信**：Wide-EP 把专家摊到更多卡上、EPLB 复制热专家、Mega MoE 把通信与计算融合 —— 第 6 章。
3. **省气泡**：投机解码提高每步产出、变长验证按边际收益分配算力、ZOS 把 CPU 工作塞进 GPU 计算期间 —— 第 7、8 章。

---

## 开源版给了什么、没给什么

| 能力 | 开源仓库 | 说明 |
|---|---|---|
| 核心推理引擎（调度 / cache / 模型执行 / 采样） | ✅ | `deepinfer/` + `csrc/` |
| 离线批量推理 | ✅ | `LLM.generate()`；`examples/offline_inference.py` |
| 多模态（VE 与 LLM 同引擎） | ✅ | `ve/`、`examples/offline_inference.py` 的 VL 样例 |
| 投机解码与变长验证 | ✅ | DFlash / MTPVarlen，默认 `nextn=5` |
| 结构化输出 | ✅ | xgrammar，JSON Schema / regex / EBNF |
| 基准与评测脚本 | ✅ | `examples/benchmark.py`、`eval/` |
| 在线服务 API（HTTP / gRPC / 流式） | ❌ | `LLMEngine` 文档明确「本版本不含在线服务封装」 |
| KV cache 存储集群（3FS / 跨机共享） | ❌ | 仅提供 state 落盘布局与 P/E 搬运所需的接口 |
| P/D 分离的完整编排 | ⚠️ | `EngineType.PROMPT / COMPLETION` 与虚函数钩子在，但无部署编排 |
| 四类负载均衡器（P / D / VE / 服务层专家调度） | ❌ | 官方 Q&A 明确与内部基础设施耦合，未开源；引擎内的 EPLB 除外 |
| 多厂商 API 协议转换 | ❌ | 独立仓库 [`deepseek-recipe`](https://github.com/deepseek-ai/deepseek-recipe) |

> 一句话：**引擎级开源，不是平台级开源**。把它当「可部署的 vLLM 替代品」会失望；把它当「DeepSeek 线上推理系统的核心部件与设计样本」则信息量极大。

---

## 术语表

> 按「主要展开章节」排序；部分术语会在第 1 章的全景表中先出现，详细解释在对应章节。

### 全景与运行链路（第 1–2 章）

| 术语 | 中文注释 | 展开 |
|---|---|---|
| E/P/D | Encoder（视觉编码）/ Prefill（读题）/ Decode（逐字写）三阶段分离部署 | ch1 |
| Wide-EP | 大专家并行：Decode 侧把专家摊到 64–128 张卡，降低单步访存量 | ch1 |
| TTFT / TBT | 首 token 延迟 / 相邻 token 间隔；P 与 D 分离后可分别优化 | ch1 |
| Driver worker | 引擎进程内持有模型与调度的主 worker；CP 的其余 rank 为 slave worker | ch2 |
| CUDA Graph | 把一整段 decode 计算录成图后重放，省去逐 kernel 的 CPU 发射开销 | ch2 |
| `EngineType` | `NORMAL`（P+D）/ `PROMPT`（只做 prefill）/ `COMPLETION`（只做 decode） | ch2 |

### 调度与缓存（第 3–4 章）

| 术语 | 中文注释 | 展开 |
|---|---|---|
| Continuous batching | 每步重新组批，完成的请求立刻退出、新请求立刻补位 | ch3 |
| Chunked prefill | 超长 prompt 切成多个 chunk 分步预填充，避免独占一步 | ch3 |
| Preemption | 显存块不足时抢占请求：重算（回 waiting）或直接终止 | ch3 |
| `block_size` | KV 页大小，V4.1 固定 128 token（`resolved_tokens_per_block = 128`） | ch4 |
| State cache | 每序列一个固定槽位，存 SWA 环、压缩状态等非分页状态 | ch4 |
| SWA | Sliding Window Attention，只保留最近窗口的 KV | ch4 |
| `KVSTORE_GRAIN` | 落盘粒度 128 token：只在 128 的整数倍位置写盘 | ch4 |
| Stored / dropped region | StateBlock 中「需要落盘」与「仅运行时保留」的两段布局 | ch4 |

### 注意力与 MoE（第 5–6 章）

| 术语 | 中文注释 | 展开 |
|---|---|---|
| MLA | Multi-head Latent Attention，把 KV 压成低秩潜向量，显著缩小 KV cache | ch5 |
| 压缩 KV（compress ratio） | 每 N 个 token 压成一个压缩 key，注意力在其上计算 | ch5 |
| Indexer / DSA | 稀疏注意力的索引器：给压缩 KV 打分并选 TopK，DeepSeek Sparse Attention | ch5 |
| Packed KV | 把多个 head 的 KV 打包存放，减少独立张量与访存 | ch5 |
| YoCo | You Only Cache Once：前若干层为 producer，后续 consumer 层复用/重算 | ch5 |
| MoE | Mixture of Experts，路由网络为每个 token 选少数专家 | ch6 |
| EP / EPLB | 专家并行 / 专家并行负载均衡；后者把热专家复制到空闲卡 | ch6 |
| 逻辑专家 / 物理槽位 | 模型定义的第 i 个专家 / GPU 上实际存放的副本槽位 | ch6 |
| Mega MoE | 把 dispatch、GEMM、combine 融合成更少的 kernel，减少中间访存 | ch6 |

### 投机、异步与输出（第 7–9 章）

| 术语 | 中文注释 | 展开 |
|---|---|---|
| MTP / NextN | Multi-Token Prediction，一次预测后续多个 token | ch7 |
| DFlash | DeepInfer 的投机头实现，含 draft 层、Markov 头与置信度头 | ch7 |
| Draft / Verify | 先用便宜路径猜若干 token，再用主模型批量验证 | ch7 |
| Confidence Head | 预测每个草稿 token 的接受概率，用于变长验证的预算分配 | ch7 |
| ZOS | Zero-Overhead Scheduling，零开销调度：CPU 排班与 GPU 计算重叠 | ch8 |
| Batch-invariant | 同一请求无论与谁拼批、批多大，输出都一致 | ch8 |
| `seq_seed` | 每序列的 uint64 采样种子；固定后可复现采样结果 | ch9 |
| Structured Output（SO） | 用语法自动机约束输出必须符合 JSON Schema / regex / EBNF | ch9 |

### 多模态、并行与生产（第 10–11 章）

| 术语 | 中文注释 | 展开 |
|---|---|---|
| VE | Vision Encoder，视觉编码器；把图片编码成 LLM 可消费的 embedding | ch10 |
| DP / CP / EP / ENP | 数据并行 / 上下文并行 / 专家并行 / Engram 并行 | ch10 |
| CP mirror | Prefill 时把 token 按 CP rank 重排，使每卡算力均衡 | ch10 |
| `userbuffer` | 预先分配的通信缓冲区，避免每步临时分配 | ch10 |
| KV Store | 跨机 KV cache 存储（生产用 3FS），开源版未提供 | ch11 |
| Prefix cache | 命中历史 KV，跳过重复 prefill；开源版无自动前缀匹配服务 | ch11 |
| Pass@1 | 单次采样正确率；`eval/` 的主指标 | ch11 |

---

## 源码规模与目录

> 以下数字于 2026-10-21 对本地快照实测，不含 `vendor/` 子模块与 `.git/`。

| 项 | 数量 |
|---|---|
| `deepinfer/` Python 文件 | 218 个 / 46,353 行 |
| `csrc/`（C++ / CUDA / 头文件） | 33 个文件 |
| `deep_cluster/` | 8 个 Python 文件（硬件探测、NUMA 绑定、拓扑） |
| `vendor/` 子模块 | DeepEP、DeepEP-Ascend、DeepGEMM、DeepGEMM-Ascend、DeepSelect、FlashMLA |
| 测试 | `tests/` 覆盖 offline PPL、batch invariant、EPLB policy、sampler、VE、state cache、userbuffer、CUDA 同步守卫 |

```text
DeepInfer/
├── deepinfer/
│   ├── entrypoints/llm.py          # 离线入口 LLM.generate()
│   ├── engine/llm_engine.py        # 引擎主循环、worker 管理、输出组装
│   ├── engine/arg_utils.py         # EngineArgs → 四类 Config
│   ├── worker/                     # Worker、ModelRunner、CacheEngine、CUDA Graph
│   ├── model_executor/             # 模型、层、TileLang 算子、EPLB、并行组
│   │   ├── models/v4_modules/      # V4 注意力、MoE、YoCo、Engram、HC
│   │   ├── models/mtp/dflash.py    # DFlash 投机头
│   │   ├── layers/                 # Sampler、Linear、RoPE、TileLang 算子
│   │   └── eplb/                   # 专家负载均衡
│   ├── structure_output/           # xgrammar 编译 / matcher / bitmask
│   ├── ve/                         # 多模态预处理
│   ├── distributed/                # 共享内存广播
│   └── environ.py                  # 全部 DEEPINFER_* 环境变量
├── csrc/engine/                    # C++ 调度器、BlockManager、Sequence、ZOS
├── deep_cluster/                   # GPU/NPU 探测、NUMA、拓扑
├── examples/                       # 离线推理、benchmark、sweep、YoCo 验证
├── eval/                           # AIME / GPQA / HLE 评测
├── tests/                          # pytest 回归
└── doc/inference_deployment_qa.md  # 生产部署 Q&A（本笔记的重要官方来源）
```

---

## 与参考目录的关系

- **结构**：均为「根级 `chNN_*.md` 章节 + `README.md` 索引」的多章专题；章节文件名、H1 格式、Mermaid 竖排、禁用 LaTeX、章间引用用纯文本「第 N 章」等约定一致。
- **骨架**：参考目录是视频课程整理，第三节是「演示步骤」；本目录是源码分析，第三节改为「源码走读」，其余五节不变（问题 → 机制 → 源码 → 坑 → 结论 → 回顾）。
- **配图**：参考目录以自绘位图为主；本目录以 Mermaid 为主，优势是图与代码同源、可审阅、无二进制资产；另提供由 `_build_html.py` 生成的单文件 HTML 精读版（见下）。
- **来源**：参考目录以课程转写为准；本目录以源码与官方文档为准，并新增 [`_来源与数据分级.md`](_来源与数据分级.md) 记录每条关键数据的出处。

---

## HTML 精读版

- 文件：[`deepinfer-inference-framework-deep-dive.html`](deepinfer-inference-framework-deep-dive.html) —— 与 11 章同源的单文件自包含深色长文（无 CDN / 无外部字体 / 无外部 JS），含侧栏目录与 14 张静态内联 SVG 机制图。
- 构建：`python docs/DeepInfer推理框架笔记/_build_html.py`（仅 Python 标准库，幂等）。改章节正文或 Mermaid 图后必须重跑，否则 HTML 与 Markdown 不一致。
- 图是 `graph TD` 子集的静态简化渲染（布局与官方 Mermaid 不完全一致），以离线可读为目标；源图请以 Markdown 里的 Mermaid 为准。

---

## 版本与时效

- 本笔记对应 DeepInfer `0.1.0`，本地快照 HEAD `9bd9cf2`（2026-10-21）。
- 仓库极新（创建于 2026-10-16），上游仍在快速迭代；**配置项默认值、算子实现、支持模型都可能变化**。引用具体数值前，先对照你本地源码的 `deepinfer/environ.py`、`deepinfer/config.py` 与 `README.md`。
- 官方生产数据（如 155 万亿 token/天、$38/GPU-hour、AIME 99.9%）来自官方 Q&A / 仓库，**不是开源版复现结果**，本笔记会明确标注。

---

## 复核记录

- **2026-10-21 源码复核**：对照本地快照逐章核查默认值、代码语义与官方数字；修正了计数不一致（四类/五类工作、三种/五类缓存、四种切分/五套进程组、三件事/四件事）、block 数「取平均 vs 取最小值」、`KEEP_TOKENS` 的实际校验强度、Mega MoE 的平台条件、EPLB 在 benchmark 的开关、DSpark 的命名边界、+4–7% 的适用区间等问题。11 章均保留六节骨架，本地链接已校验；另生成单文件 HTML 精读版（11 章 / 14 图）。
