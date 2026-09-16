# 大模型视频课程 · 结构化学习笔记

> **整理方式**：faster-whisper 语音转写 + 白板关键帧人工整理；口语已按书面语整理，忠实于原课内容
> **章节结构**：每章按「概念 → 原理推导 → 白板演示步骤 → 关键结论/公式 → 本节要点回顾」组织
> **使用说明**：各章截图引用 `../2026-09-07 12-15-43_doc/frames/` 目录，自绘示意图存放于本目录下 `assets/`（共 3 张：`vector_to_scalar.png`、`neuron_structure.png`、`forward_propagation.png`）。请用 VSCode / Typora 打开本文件夹阅读（Mermaid 图会自动渲染）

---

## 课程主线（一句话版）

**裸模型（token 进、概率分布出）→ 模型服务（API 三步封装）→ AI 应用（只能玩输入与输出）→ 要实现智能靠机器学习 → 机器学习靠神经网络 → 神经网络靠梯度下降 + 反向传播调参数 → 训练产物 = 权重文件 + 配置文件。**

## 章节目录

| 章 | 文件 | 主题 | 时间轴 |
|---|---|---|---|
| 1 | [ch01_raw_model.md](ch01_raw_model.md) | 裸模型 Raw Model：大模型的最底层真相 | 00:00–00:15 |
| 2 | [ch02_model_service.md](ch02_model_service.md) | 模型服务 Model Service：API、定价与采样参数 | 00:15–00:43 |
| 3 | [ch03_ai_application.md](ch03_ai_application.md) | AI 应用层与概念分析方法论（Skill 实战） | 00:44–01:12 |
| 4 | [ch04_concepts_intelligence.md](ch04_concepts_intelligence.md) | 概念辨析与智能本质：AI 的分类 | 01:12–01:30 |
| 5 | [ch05_ml_overview.md](ch05_ml_overview.md) | AI 应用全景与机器学习：问题域与学习范式 | 01:30–01:54 |
| 6 | [ch06_neuron.md](ch06_neuron.md) | 神经元：从生物结构到数学模型（MP 模型） | 01:54–02:18 |
| 7 | [ch07_network_structure.md](ch07_network_structure.md) | 神经网络结构：分层、全连接与前向传播 | 02:18–02:40 |
| 8 | [ch08_loss_gradient.md](ch08_loss_gradient.md) | 损失与梯度下降：网络如何自我调整 | 02:40–02:51 |
| 9 | [ch09_backpropagation.md](ch09_backpropagation.md) | 反向传播：梯度下降的实现手段 | 02:51–03:01 |
| 10 | [ch10_training_mode.md](ch10_training_mode.md) | 训练模式：批量、张量与模型文件 | 03:01–03:12 |

**推荐学习顺序**：按章节顺序通读（1→10 为原课叙事线）；复习时可只看各章「本节要点回顾」。

---

## 术语表（英文缩写 + 中文注释）

> 按"首见章节"排序；术语在各章正文首次出现处均有上下文解释。

### 基础层（第 1 章）

| 术语 | 中文注释 | 首见 |
|---|---|---|
| Raw Model | 裸模型 / 基础模型 / 原始模型——AI 体系最底层 | ch1 |
| Token | 词元——自然语言切分出的数字单元；中文 1 字 ≈ 1.5 token，英文 1 词 ≈ 1.3 token | ch1 |
| Tokenization | 分词——文字变 token 列表的过程 | ch1 |
| Probability Distribution | 概率分布——模型输出"下一个 token 的可能性" | ch1 |
| Context Window | 上下文窗口——token 列表的最大长度；能容纳 ≠ 能处理好 | ch1 |
| Weight Matrix | 权重矩阵——模型文件的核心；参数量 = 矩阵中数字的个数（7B = 70 亿） | ch1 |
| Training / Fine-tuning | 训练（从无到有生成矩阵）/ 微调（修改已有矩阵的部分参数） | ch1 |
| Corpus | 语料——训练与微调的原材料 | ch1 |
| Transformer | 变换器架构——当前主流神经网络架构，自 2017 年确立至今无本质变化 | ch1 |
| Pure Function | 纯函数——相同输入必得相同输出；GPU 浮点并行带来微小抖动 | ch1 |
| Multimodal | 多模态——对模型而言一切皆数字，模态差异只在于人如何解读 | ch1 |
| Subagent | 子代理——AI 编码工具为规避长上下文退化而采用的手段 | ch1 |

### 模型服务层（第 2 章）

| 术语 | 中文注释 | 首见 |
|---|---|---|
| Model Service | 模型服务——裸模型的二次封装，以 API 发布 | ch2 |
| API / SDK | 应用编程接口 / 软件开发工具包（封装网络请求） | ch2 |
| API Key / base_url | 鉴权密钥 / 请求基地址——换厂商三件套之一 | ch2 |
| System Prompt | 系统提示词——服务商注入的隐藏指令；提示词是服务商层概念，对模型都是 token | ch2 |
| Temperature | 温度（0–2）——控制采样随机性；代码 0–0.2 / 普通 0.7 / 创意 1+ | ch2 |
| top-K / top-P | 候选截断策略：取概率前 K 个 / 累计概率达 P 截断（核采样）；先截断、再随机 | ch2 |
| Auto-regression | 自回归——输出不断追加回输入的循环；输出 token 更贵的根源 | ch2 |
| Detokenization | 反分词——token 序列还原成自然语言 | ch2 |
| Forward / Backward 相关 | 前向传播 / 反向传播见下文神经网络部分 | — |

### 应用层与方法论（第 3–5 章）

| 术语 | 中文注释 | 首见 |
|---|---|---|
| AI Application | AI 应用——封装模型服务的第三层 | ch3 |
| Skill | 技能——本质是提示词 + 本地文件读取；概念会在层间流动（被服务商吸收） | ch3 |
| Tools / Function Calling | 工具调用——AI 应用通过请求体里的 tools 定义告知模型能力 | ch3 |
| MCP | Model Context Protocol，模型上下文协议 | ch3 |
| RAG | Retrieval-Augmented Generation，检索增强生成 | ch3 |
| LangChain / LangGraph | AI 应用开发框架 | ch3 |
| Proxy Server | 代理服务器——透视 AI 应用与模型服务之间消息传递的利器 | ch3 |
| SSE | Server-Sent Events，服务器单向流式传输 | ch3 |
| CLAUDE.md / system reminder | AI 编程工具每次请求自动携带的工程规范与系统提醒 | ch3 |
| Symbolism | 符号主义——智能 = 推理规则（哲学流派之一） | ch4 |
| Connectionism | 连接主义——模拟大脑神经元（当代主流流派） | ch4 |
| Behaviorism | 行为主义——智能来自与环境互动（哲学流派之一） | ch4 |
| NLP | Natural Language Processing，自然语言处理——研究语言本身特点，不关心实现手段 | ch4 |
| TTS / ASR | 文字转语音 / 自动语音识别 | ch4 |
| Machine Learning (ML) | 机器学习——任务 T 上的性能 P 随经验 E 增加而提升 | ch5 |
| Supervised Learning | 监督学习——人类给正确答案（数据标注） | ch5 |
| Self-supervised Learning | 自监督学习——自己找答案自己核对 | ch5 |
| Unsupervised Learning | 无监督学习——无答案做分类/相似度（工厂质检、鉴宝） | ch5 |
| Reinforcement Learning | 强化学习——只给结果数字反馈（下棋输赢） | ch5 |
| Semantic Segmentation | 语义分割——像素级归类（B 站防弹幕遮挡人物） | ch5 |
| OCR | Optical Character Recognition，光学字符识别（文字提取） | ch5 |

### 神经网络部分（第 6–10 章）

| 术语 | 中文注释 | 首见 |
|---|---|---|
| Neuron | 神经元——向量进、标量出的最小运算单元 | ch6 |
| Vector / Scalar | 向量（一列数字，真实场景可达上万维）/ 标量（单个数字）——神经元的输入与输出形态 | ch6 |
| Dendrite / Axon | 树突（多输入）/ 轴突（单输出）——生物神经元结构 | ch6 |
| MP Model | MP 模型（1943）——神经元的数学模型：`y = σ(Σ wᵢxᵢ + b)` | ch6 |
| Weight (w) | 权重——该维特征的重要程度（可调） | ch6 |
| Bias (b) | 偏置——激活门槛（可调） | ch6 |
| Parameter | 参数 = 权重 + 偏置 的统称——神经元唯一可调的东西 | ch6 |
| Activation Function | 激活函数——设计时定死不可调；老牌代表"与 0 取最大"（ReLU 思想） | ch6 |
| Activation Value | 激活值——神经元输出；0 = 未激活 | ch6 |
| ReLU | Rectified Linear Unit，修正线性单元——"与 0 取最大值"，负数砍成 0；简单且有效的**非线性**激活函数 | ch6 |
| Input / Hidden / Output Layer | 输入层（第 0 层，不转换）/ 隐藏层（数量看经验）/ 输出层（数量 = 类别数） | ch7 |
| Fully Connected | 全连接——下层每个神经元连接上层所有输出；权重数 = 上层输出数 | ch7 |
| Forward Propagation | 前向传播——信号从输入层逐层流向输出层；每层两步 `z = W·a + b` → `a = σ(z)` | ch7 |
| Batch / Mini-Batch | 批 / 小批量——一次并行处理多样本（矩阵按列堆叠），配合 GPU 批量并行 | ch7 |
| FLOPs | Floating Point Operations，浮点运算次数——一次前向约 `2 × 参数量` 次 | ch7 |
| Softmax | 归一化指数函数——把输出层得分压成"和为 1 的概率"，可读出置信度 | ch7 |
| Nonlinearity | 非线性——激活函数必须非线性，否则多层会塌缩成一层线性变换 | ch7 |
| CNN | Convolutional Neural Network，卷积神经网络——**局部连接 + 权重共享**（与全连接相对） | ch7 |
| Receptive Field | 感受野——CNN 中每个神经元只"看"输入的哪一小块 | ch7 |
| Attention | 注意力——不固定连谁，由输入动态决定"该看谁、看多重"；Transformer 的核心 | ch7 |
| Prediction / Label | 预测值（模型算的）/ 标签（人工标注的正确答案） | ch8 |
| Loss / Loss Function / Cost Function | 损失值 / 损失函数 / 代价函数（同义）——量化预测与标签的差距 | ch8 |
| Gradient Descent | 梯度下降——黑夜下山，沿最陡下坡方向小步走；是思想不是公式 | ch8 |
| Learning Rate | 学习率——梯度下降的步长；太大跨过谷底，太小收敛慢 | ch8 |
| Local / Global Optimum | 局部最优 / 全局最优——局部最优已足够好，全局可遇不可求 | ch8 |
| Backpropagation | 反向传播——梯度下降的实现手段；误差信号从输出层逐层回传 | ch9 |
| Partial Derivative / Chain Rule | 偏导数 / 链式法则——反向传播用到的微积分工具 | ch9 |
| SGD | Stochastic Gradient Descent，随机梯度下降——单样本更新，噪声大，基本弃用 | ch10 |
| Full Batch / Mini-Batch | 全批量（最稳最烧钱）/ 小批量（求平均更新，大模型主流）梯度下降 | ch10 |
| Tensor | 张量——多维数组；配合 GPU 批量并行 | ch10 |
| Catastrophic Forgetting | 灾难性遗忘——按类别顺序训练导致"训 1 忘 0"；数据要随机打乱 | ch10 |
| Overfitting / Underfitting | 过拟合（只认训练集）/ 欠拟合（训练集都学不会） | ch10 |
| Generalization | 泛化能力——能识别没见过的东西 | ch10 |
| Inference | 推理——只跑前向传播、**不更新参数**（区别于训练阶段的「前向 + 反向」） | ch10 |
| PyTorch | 当前主力训练框架（也用于推理）；老框架退守边缘计算 | ch10 |
| Edge Computing | 边缘计算——手机等设备上的小型训练/推理任务 | ch10 |
| Model File | 模型 = 权重文件（占体积）+ 配置文件（描述架构），缺一不可 | ch10 |

---

## 全课程核心结论速查

1. **裸模型** = `f(token 列表) → 下一个 token 的概率分布`，理论上是纯函数。
2. **模型服务** = 前处理（认证/注入提示词/分词）→ 自回归（逐 token 生成）→ 后处理（反分词/合规）。
3. **AI 应用**在裸模型之上只能玩两件事：**给模型输入什么 + 如何处理模型输出**——万能概念分析法。
4. 实现智能的主流 = **机器学习**（任务 T / 性能 P / 经验 E）；层级（**包含关系，非流程推进**）：**机器学习 ⊇ 神经网络 ⊇ 深度学习 ⊇ Transformer**。
5. 神经网络 = 分层连接的神经元；**参数（权重+偏置）唯一决定输出**（激活函数定死）。
6. 训练闭环：**前向传播 → 损失函数 → 梯度下降（方向）→ 反向传播（实现）→ 按学习率小步更新**，循环至损失收敛。
7. 训练产物 = **权重文件 + 配置文件**；使用模型 = 只跑前向传播（推理）。
8. 概念会过时（工具生命周期极短），**核心永远稳定**——抓核心、放细节。

---

*笔记整理：2026-09-08；转写底稿：faster-whisper small/medium；如有术语偏差以原视频为准。*
