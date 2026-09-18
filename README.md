# my-notes-and-utils

个人知识库与工具仓库：把**体系化学习指南**、**技术专题深度笔记**、**可复用工具函数**统一归档，便于检索与复用。

仓库以 Markdown 为主要载体（510 个文件，其中 479 篇 Markdown、约 25 万行），内容分两条主线：

- **知识线**：`guides/` 的笔面试学习资料库（后端 + 前端）与 `docs/` 的技术专题深度笔记；
- **工具线**：`src/` 的通用工具函数与 `examples/` 用法示例。

> 本文件是**全局落地页**：给出各子工程的定位、规模与入口（`README.md` 链接）。每个子工程在自己的 `README.md` 中维护详细的总览、学习路线与逐文件索引，避免多处重复。

---

## 目录结构

```
my-notes-and-utils/
├── docs/                     技术专题深度笔记（自成体系的交付物）
│   ├── harness/                Agent Harness 深度讲解 + 可运行最小实现
│   └── 大模型与神经网络原理笔记/  大模型视频课程结构化笔记（10 章）
├── guides/                   体系化学习指南（笔面试资料库）
│   ├── backend/                Java 后端：4 大模块 + 扩展，258 篇
│   ├── frontend/               前端：15 个模块，195 篇
│   ├── code-review/            代码理解 / 代码审查 Agent 指令体系
│   ├── learning/               学习方法论
│   └── tools/                  工具链速查
├── src/                      通用工具函数
│   ├── js/                      JavaScript/Node.js 工具（含 README 索引）
│   └── python/                  Python 工具（含 README 索引）
├── examples/                  src 工具函数的用法示例
├── scripts/                   本地初始化脚本
├── LICENSE                    MIT
└── README.md                  本文件
```

---

## 各子工程索引与作用

### 一、`guides/` — 体系化学习指南

各子目录均自带 `README.md`（总览 / 学习路线 / 逐文件索引），下面仅列定位与规模。

#### `guides/backend/` — Java 后端笔面试资料库（258 篇）
Java 基础、JavaWeb 单体、分布式微服务、Python AI Agent 共 **4 大模块 + 1 扩展**。
总览、4+1 模块路线、逐文件索引、知识导览、学习路线图、变更日志见 [`guides/backend/README.md`](guides/backend/README.md)。

#### `guides/frontend/` — 前端笔面试资料库（195 篇）
HTML/CSS、JS、TS、浏览器、Vue、React、工程化、性能、Node.js、实战、AI 辅助、跨端、架构、监控、测试共 **15 个模块**。
总览、15 模块路线、逐文件索引、五维速查表、调试方法论见 [`guides/frontend/README.md`](guides/frontend/README.md)。

#### `guides/code-review/` — 代码理解与审查指令体系（4 篇）
供 Agent 加载的指令规范，解决"代码是什么"（理解）与"改动能不能合入"（把关），通过共享"项目画像"协作。
体系说明、场景示例、产出物位置见 [`guides/code-review/README.md`](guides/code-review/README.md)；核心两份指南：`CODE_ANALYSIS_GUIDE.md`（v1.6.0）、`CODE_REVIEW_GUIDE.md`（v1.1.0）。

#### `guides/learning/` — 学习方法论（2 篇）
AI 辅助源码阅读方法、如何更好使用 AI 编程助手。详见 [`guides/learning/README.md`](guides/learning/README.md)。

#### `guides/tools/` — 工具链速查（1 篇）
VS Code 扩展清单。详见 [`guides/tools/README.md`](guides/tools/README.md)。

---

### 二、`docs/` — 技术专题深度笔记

#### `docs/harness/` — Agent Harness 深度讲解（15 个文件）
从底层思想（冯·诺依曼同构）→ 第一性原理（长周期任务的五个必然问题）→ 结构解剖（12 个组件）→ 动手实现 → Codex 源码级实现（含 Prompt Cache 一等约束）→ 横向案例对比 → 架构决策 → 生产化纵深（评测 / 成本 / 安全 / 恢复 / 运维 / 合规 / RL 闭环）。
详细内容与运行方式见 [`docs/harness/README.md`](docs/harness/README.md)：含精读版 HTML 长文、纯文本版 MD 长文、可运行最小实现 `code/minimal_harness.py`、原理图 `images/`。

#### `docs/大模型与神经网络原理笔记/` — 大模型视频课程结构化笔记（20 个文件）
faster-whisper 语音转写 + 白板关键帧人工整理，共 10 章，按「概念 → 原理推导 → 白板演示 → 关键结论/公式 → 要点回顾」组织。
课程主线：**裸模型 → 模型服务 → AI 应用 → 机器学习 → 神经网络 → 梯度下降 + 反向传播 → 权重文件 + 配置文件**。
术语表与核心结论速查见 [`docs/大模型与神经网络原理笔记/README.md`](docs/大模型与神经网络原理笔记/README.md)；含 `assets/` 自绘示意图，建议用 VSCode / Typora 打开以渲染 Mermaid 图。

---

### 三、`src/` — 通用工具函数

从多个项目中抽取的、与具体业务解耦的通用工具，均为纯函数/类。各子目录自带 `README.md` 索引。

| 路径 | 内容 |
|------|------|
| [`src/python/utils.py`](src/python/utils.py) | `ensure_dir` / `timestamp_now` / `read_json` / `write_json` / `retry` 装饰器（仅标准库） |
| [`src/js/utils.js`](src/js/utils.js) | JS 常用工具：防抖 `debounce`、日期格式化 `formatDate`（无依赖） |
| [`src/js/errors.js`](src/js/errors.js) | 通用自定义错误类层次（ServiceError 基类 + 6 个子类），统一携带业务码 `code` |
| [`src/js/query-helper.js`](src/js/query-helper.js) | Sequelize 通用查询：分页 `paginate` + 条件构造 `buildWhere` |
| [`src/js/http-tool.js`](src/js/http-tool.js) | 统一响应、JWT 解析、可配置上传器、Markdown TOC 树生成 |
| [`src/js/README.md`](src/js/README.md) | JS 工具索引与依赖说明 |
| [`src/python/README.md`](src/python/README.md) | Python 工具索引与依赖说明 |

**使用约定**

- **密钥绝不硬编码**：JWT 密钥从 `process.env.JWT_SECRET` 读取；上传目录通过 `createUploader({ dest })` 或 `process.env.UPLOAD_DIR` 注入。
- **按需引入**：各 JS 模块在文件顶层 `require` 第三方依赖（`sequelize` / `jsonwebtoken` / `md5` / `multer` / `markdown-toc`），未安装则引入即报错；仅 `errors.js` 无依赖。
- 这是「可复用代码片段」集合，不是发布的 npm 包 —— 直接复制到目标工程的 `utils/` 目录即可。

### 四、`examples/` — 用法示例

- [`python-utils-demo.md`](examples/python-utils-demo.md) —— `src/python/utils.py` 的典型用法演示
- [`README.md`](examples/README.md) —— 示例索引

### 五、`scripts/` — 初始化脚本

- [`setup.sh`](scripts/setup.sh) —— Linux / macOS 本地环境初始化（创建并激活 Python venv）

---

## 如何使用

**作为知识库阅读**

1. 克隆仓库：`git clone https://github.com/xjq11029/my-notes-and-utils.git`
2. 从本文件「各子工程索引与作用」定位目标方向，再进入对应子工程的 `README.md` 按其学习路线推进
3. 后端 / 前端学习者建议先读对应 `README.md` 的学习路线，再按模块推进，学完即刷题集
4. 涉及 Mermaid 图与公式的笔记（如 `docs/大模型与神经网络原理笔记/`）建议用 VSCode / Typora 打开

**作为工具箱使用**

1. 从 `src/` 挑选需要的工具文件，复制到你的工程
2. 按 `src/js/README.md` 的依赖表安装对应 npm 包（`src/python/utils.py` 仅依赖标准库）
3. 参考 `examples/` 中的示例上手

**作为 Agent 指令集使用**

- 将 `guides/code-review/` 下的指南复制到目标项目根目录，然后对 Agent 下达指令；详细场景与产出物位置见 [`guides/code-review/README.md`](guides/code-review/README.md)

---

## 维护约定

- **文档与目录同步**：任何目录中的 `README.md` 必须真实反映该目录的实际情况，发现差异即时修正。
- **`AGENTS.md`**：工程根目录有一份 `AGENTS.md`，记录工程功能与关键目录结构，改动工程时同步更新。
- **数据来源分级**：`docs/harness/` 对关键数据做可信度分级（一手来源 / 源码分析 / 二手报道），修改时请维持该约定。
- **产物自包含**：`docs/harness/agent-harness-deep-dive.html` 必须保持单文件自包含（无 CDN / 无外部字体 / 无外部 JS），支持离线打开。
- **文件命名约定**（通用）：原理文件 `NN-主题.md` + 章节导读 `NN-主题-导览.md` + 题集 `*笔面试题集.md` + 速查件（`常见错误汇总.md` / `概念对比速查.md` / `综合场景.md`）；下划线前缀 `_*.md` 为内部 / 元文件（如变更日志）。

---

## 统计

| 项目 | 数值 |
|------|------|
| 文件总数 | 510（不含 `.git/` 与内部目录 `.workbuddy/`） |
| Markdown 文档 | 479 篇 / 约 25 万行 |
| `guides/backend/` | 259 个文件 / 258 篇 Markdown |
| `guides/frontend/` | 193 个文件 / 192 篇 Markdown |
| `docs/` | 35 个文件 |
| `src/` | 7 个文件 |

---

## License

[MIT](LICENSE) © 2026 xjq11029
