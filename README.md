# my-notes-and-utils

个人知识库与工具仓库：把**体系化学习指南**、**技术专题深度笔记**、**可复用工具函数**统一归档，便于检索与复用。

仓库以 Markdown 为主要载体（508 个文件，其中 477 篇 Markdown、约 25 万行），内容分两条主线：

- **知识线**：`guides/` 的笔面试学习资料库（后端 + 前端）与 `docs/` 的技术专题深度笔记；
- **工具线**：`src/` 的通用工具函数与 `examples/` 用法示例。

---

## 目录结构

```
my-notes-and-utils/
├── docs/                     技术专题深度笔记（自成体系的交付物）
│   ├── TOC.md                  全仓库文档目录
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
│   └── python/                  Python 工具
├── examples/                  src 工具函数的用法示例
├── scripts/                   本地初始化脚本
├── LICENSE                    MIT
└── README.md                  本文件
```

---

## 内容详解

### 一、`guides/` — 体系化学习指南

#### `guides/backend/` — Java 后端笔面试资料库（258 篇）

按 **4 大核心模块 + 1 个扩展模块** 组织，覆盖从 Java 基础到分布式微服务、Python AI Agent 的完整后端技术栈。

| 模块 | 子模块 | 文件数 | 目录 |
|------|--------|:------:|------|
| Java 基础 | java-core / jvm-juc / mysql-jdbc | 51 | [`01-java-basics/`](guides/backend/01-java-basics/) |
| JavaWeb 单体架构 | maven / javaweb-servlet / ssm / spring-boot / mybatis / linux / docker-k8s | 77 | [`02-javaweb-monolith/`](guides/backend/02-javaweb-monolith/) |
| 分布式微服务 | redis / mysql-advanced / nginx / spring-cloud / zookeeper / mq / elasticsearch / clickhouse / git | 95 | [`03-distributed-microservices/`](guides/backend/03-distributed-microservices/) |
| Python AI Agent | python-core / langchain-rag / llm-fine-tuning | 27 | [`04-python-aiagent/`](guides/backend/04-python-aiagent/) |
| 扩展：实战项目 | project（电商订单实时统计分析平台） | 5 | [`extensions/`](guides/backend/extensions/) |

- 总览与学习路线：[`guides/backend/README.md`](guides/backend/README.md)
- 知识地图：[`guides/backend/知识导览.md`](guides/backend/知识导览.md)
- 学习路线图：[`guides/backend/2026最新Java学习路线图.png`](guides/backend/2026最新Java学习路线图.png)
- 变更日志：[`guides/backend/_CHANGELOG.md`](guides/backend/_CHANGELOG.md)

> **文件结构约定**：每个子模块目录下含两类文件 —— **原理文件**（`NN-主题.md`，讲底层原理与实战）与**笔面试题集**（`*笔面试题集.md`，选择题 + 简答 + 编程/场景设计，全部附解析）；部分模块另配套 `常见错误汇总.md` / `概念对比速查.md` / `综合场景.md` 三个速查件。多数原理文件另有对应的 `-导览.md`（章节导读）。

#### `guides/frontend/` — 前端笔面试资料库（195 篇）

按 **15 个模块** 组织，与后端资料库互补，形成完整全栈知识体系。

| 模块 | 核心技术栈 | 目录 |
|------|-----------|------|
| 01 HTML/CSS | 语义化、盒模型、Flex/Grid、BFC、回流重绘、响应式 | [`01-html-css/`](guides/frontend/01-html-css/) |
| 02 JavaScript 核心 | 原型链、闭包、this、事件循环、Promise、ES6+、DOM、JSON、正则、BOM | [`02-javascript-core/`](guides/frontend/02-javascript-core/) |
| 03 TypeScript | 类型系统、泛型、高级类型、工具类型、装饰器 | [`03-typescript/`](guides/frontend/03-typescript/) |
| 04 浏览器原理 | 渲染流程、V8 引擎、事件循环、跨域、Web 安全、网络协议 | [`04-browser/`](guides/frontend/04-browser/) |
| 05 Vue 3 | Composition API、Proxy 响应式、diff 优化、Pinia | [`05-vue/`](guides/frontend/05-vue/) |
| 06 React 18 | Hooks、Fiber 架构、虚拟 DOM Diff、状态管理 | [`06-react/`](guides/frontend/06-react/) |
| 07 前端工程化 | Webpack、Vite、ESLint、CI/CD、Monorepo、质量门禁 | [`07-engineering/`](guides/frontend/07-engineering/) |
| 08 性能优化 | Core Web Vitals、INP、懒加载、缓存策略、图片与字体优化、SSR/SSG/RSC | [`08-performance/`](guides/frontend/08-performance/) |
| 09 Node.js | Event Loop、Koa/Express、中间件、BFF、数据库、ORM | [`09-nodejs/`](guides/frontend/09-nodejs/) |
| 10 实战项目 | 企业后台管理系统、电商平台、组件库/低代码/可视化大屏/IM | [`10-project/`](guides/frontend/10-project/) |
| 11 AI 辅助开发 | Cursor/Claude Code/Copilot、Prompt 工程、AI 代码审查、MCP 与 Agent 工作流 | [`11-ai-assisted/`](guides/frontend/11-ai-assisted/) |
| 12 跨端开发 | uniapp、渲染差异、PWA、Web Components、Electron/Tauri、RN/Flutter、鸿蒙 | [`12-cross-platform/`](guides/frontend/12-cross-platform/) |
| 13 前端架构设计 | 微前端、设计系统、分层架构、ADR、BFF 与权限、国际化与多端同构 | [`13-architecture/`](guides/frontend/13-architecture/) |
| 14 前端监控与运维 | Sentry、自建 SDK、埋点体系、灰度发布、Feature Flags、可观测性、A/B 实验 | [`14-monitoring/`](guides/frontend/14-monitoring/) |
| 15 前端测试策略 | Vitest、Testing Library、Playwright、E2E、视觉回归、性能测试、契约测试 | [`15-testing/`](guides/frontend/15-testing/) |

- 总览与学习路线：[`guides/frontend/README.md`](guides/frontend/README.md)
- 知识地图（五维速查表）：[`guides/frontend/知识导览.md`](guides/frontend/知识导览.md)
- 调试方法论：[`guides/frontend/万能通用Bug定位查找逻辑.md`](guides/frontend/万能通用Bug定位查找逻辑.md)
- 学习路线图：[`.md`](guides/frontend/前端学习路线图.md) / [`.html`](guides/frontend/前端学习路线图.html)
- 变更日志：[`guides/frontend/_CHANGELOG.md`](guides/frontend/_CHANGELOG.md)

#### `guides/code-review/` — 代码理解与审查指令体系（4 篇）

两份供 Agent 加载的指令规范，解决"代码是什么"（理解）与"改动能不能合入"（把关）两个问题，通过共享"项目画像"协作。

| 文件 | 版本 | 作用 |
|------|------|------|
| [`CODE_ANALYSIS_GUIDE.md`](guides/code-review/CODE_ANALYSIS_GUIDE.md) | v1.6.0 | 代码理解：逐文件生成调用图 + 功能说明文档（概览 / 标准 / 逐行三档模式） |
| [`CODE_REVIEW_GUIDE.md`](guides/code-review/CODE_REVIEW_GUIDE.md) | v1.1.0 | 代码审查：对变更集出具分级意见 + 合入结论（快速 / 标准 / 严格三档） |
| [`_GUIDE_CHANGELOG.md`](guides/code-review/_GUIDE_CHANGELOG.md) | — | 两份指南的合并版本变更记录 |
| [`README.md`](guides/code-review/README.md) | — | 体系使用说明、场景示例、产出物位置 |

#### `guides/learning/` — 学习方法论（2 篇）

- [`AI辅助源码阅读方法.md`](guides/learning/AI辅助源码阅读方法.md) —— 面向后端开发者的 AI 辅助开源项目源码阅读方法论（通用，不绑定具体项目）
- [`如何更好使用AI编程助手.md`](guides/learning/如何更好使用AI编程助手.md)

#### `guides/tools/` — 工具链速查（1 篇）

- [`vscode-extensions.md`](guides/tools/vscode-extensions.md) —— VS Code 扩展清单

---

### 二、`docs/` — 技术专题深度笔记

#### `docs/harness/` — Agent Harness 深度讲解（15 个文件）

从底层思想（冯·诺依曼架构同构）→ 第一性原理（长周期任务的五个必然问题）→ 结构解剖（12 个组件）→ 动手实现 → Codex 源码级实现（含 Prompt Cache 一等约束）→ 横向案例对比 → 架构决策 → 生产化纵深（评测 / 成本 / 安全 / 恢复 / 运维 / 合规 / RL 闭环）。

| 文件 | 说明 |
|------|------|
| [`agent-harness-deep-dive.html`](docs/harness/agent-harness-deep-dive.html) | 长文 · 精读版：单页自包含交互式深度讲解，11 章（0–10）+ 附录（约 3 万字，深色主题，离线可开） |
| [`harness-from-principle-to-codex.md`](docs/harness/harness-from-principle-to-codex.md) | 长文 · 纯文本版：同主题 Markdown 长文，11 节 + 附录（约 1430 行，含术语谱系、Inner/Outer Harness 视角、可操作结论） |
| [`code/minimal_harness.py`](docs/harness/code/minimal_harness.py) | 配套代码：可运行的最小 Harness 演示（约 720 行，仅依赖标准库） |
| [`images/`](docs/harness/images/) | 5 组原理图（PNG + SVG 双份） |
| [`README.md`](docs/harness/README.md) | 内容组织、使用方法、维护约定、内容自查记录 |
| [`AGENTS.md`](docs/harness/AGENTS.md) | 面向 Agent 的工程说明 |

```bash
cd docs/harness/code
python minimal_harness.py          # 运行六个对照实验，结束自动清理临时工作区
python minimal_harness.py --keep   # 保留临时工作区，便于检查中间状态
```

#### `docs/大模型与神经网络原理笔记/` — 大模型视频课程结构化笔记（20 个文件）

faster-whisper 语音转写 + 白板关键帧人工整理，共 10 章，按「概念 → 原理推导 → 白板演示 → 关键结论/公式 → 要点回顾」组织。

课程主线：**裸模型 → 模型服务 → AI 应用 → 机器学习 → 神经网络 → 梯度下降 + 反向传播 → 权重文件 + 配置文件**。

| 章 | 文件 | 主题 |
|:--:|------|------|
| 1 | [`ch01_raw_model.md`](docs/大模型与神经网络原理笔记/ch01_raw_model.md) | 裸模型 Raw Model：大模型的最底层真相 |
| 2 | [`ch02_model_service.md`](docs/大模型与神经网络原理笔记/ch02_model_service.md) | 模型服务：API、定价与采样参数 |
| 3 | [`ch03_ai_application.md`](docs/大模型与神经网络原理笔记/ch03_ai_application.md) | AI 应用层与概念分析方法论 |
| 4 | [`ch04_concepts_intelligence.md`](docs/大模型与神经网络原理笔记/ch04_concepts_intelligence.md) | 概念辨析与智能本质 |
| 5 | [`ch05_ml_overview.md`](docs/大模型与神经网络原理笔记/ch05_ml_overview.md) | AI 应用全景与机器学习 |
| 6 | [`ch06_neuron.md`](docs/大模型与神经网络原理笔记/ch06_neuron.md) | 神经元：从生物结构到数学模型 |
| 7 | [`ch07_network_structure.md`](docs/大模型与神经网络原理笔记/ch07_network_structure.md) | 神经网络结构：分层、全连接与前向传播 |
| 8 | [`ch08_loss_gradient.md`](docs/大模型与神经网络原理笔记/ch08_loss_gradient.md) | 损失与梯度下降 |
| 9 | [`ch09_backpropagation.md`](docs/大模型与神经网络原理笔记/ch09_backpropagation.md) | 反向传播 |
| 10 | [`ch10_training_mode.md`](docs/大模型与神经网络原理笔记/ch10_training_mode.md) | 训练模式：批量、张量与模型文件 |

另有 [`README.md`](docs/大模型与神经网络原理笔记/README.md)（术语表 + 核心结论速查）与 `assets/`（自绘示意图）。建议用 VSCode / Typora 打开以渲染 Mermaid 图。

> 完整文档目录见 [`docs/TOC.md`](docs/TOC.md)。

---

### 三、`src/` — 通用工具函数

从多个项目中抽取的、与具体业务解耦的通用工具，均为纯函数/类。

| 路径 | 内容 |
|------|------|
| [`src/python/utils.py`](src/python/utils.py) | `ensure_dir` / `timestamp_now` / `read_json` / `write_json` / `retry` 装饰器 |
| [`src/js/utils.js`](src/js/utils.js) | JS 常用工具：防抖 `debounce`、日期格式化 `formatDate`（无依赖） |
| [`src/js/errors.js`](src/js/errors.js) | 通用自定义错误类层次（ServiceError 基类 + 6 个子类），统一携带业务码 `code` |
| [`src/js/query-helper.js`](src/js/query-helper.js) | Sequelize 通用查询：分页 `paginate` + 条件构造 `buildWhere` |
| [`src/js/http-tool.js`](src/js/http-tool.js) | 统一响应、JWT 解析、可配置上传器、Markdown TOC 树生成 |
| [`src/js/README.md`](src/js/README.md) | JS 工具索引与依赖说明 |

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
2. 从 [`docs/TOC.md`](docs/TOC.md) 或本文件的「内容详解」定位目标文档
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
- **`AGENTS.md`**：工程根目录与 `docs/harness/` 各有一份 `AGENTS.md`，记录工程功能与关键目录结构，改动工程时同步更新。
- **数据来源分级**：`docs/harness/` 对关键数据做可信度分级（一手来源 / 源码分析 / 二手报道），修改时请维持该约定。
- **产物自包含**：`docs/harness/agent-harness-deep-dive.html` 必须保持单文件自包含（无 CDN / 无外部字体 / 无外部 JS），支持离线打开。

---

## 统计

| 项目 | 数值 |
|------|------|
| 文件总数 | 508（不含 `.git/` 与内部目录 `.workbuddy/`） |
| Markdown 文档 | 477 篇 / 约 25 万行 |
| `guides/backend/` | 259 个文件 / 258 篇 Markdown |
| `guides/frontend/` | 193 个文件 / 192 篇 Markdown |
| `docs/` | 36 个文件 |
| `src/` | 6 个文件 |

---

## License

[MIT](LICENSE) © 2026 xjq11029
