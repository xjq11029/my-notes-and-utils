# 文档目录（TOC）

> 全仓库文档索引。各目录的 `README.md` 提供该目录的详细说明，本文件提供**全局导航**。
> 统计口径：文件数为目录内文件总数（含图片、脚本等非 Markdown 文件），括号内注明 Markdown 篇数。

---

## 一、`guides/` — 体系化学习指南（467 文件 / 465 篇 Markdown）

### 1.1 `guides/backend/` — Java 后端笔面试资料库（259 文件 / 258 篇 Markdown）

| 索引文件 | 说明 |
|------|------|
| [README.md](../guides/backend/README.md) | 后端学习总览、4+1 模块路线与逐文件索引 |
| [知识导览.md](../guides/backend/知识导览.md) | 知识地图 |
| [_CHANGELOG.md](../guides/backend/_CHANGELOG.md) | 资料库版本演进记录（版本 / 日期 / 变更摘要 / 来源项目） |
| [2026最新Java学习路线图.png](../guides/backend/2026最新Java学习路线图.png) | 学习路线图 |

| 模块 | 文件数 | 子模块 |
|------|:------:|--------|
| [01-java-basics](../guides/backend/01-java-basics/) | 51 | java-core（29）/ jvm-juc（15）/ mysql-jdbc（7） |
| [02-javaweb-monolith](../guides/backend/02-javaweb-monolith/) | 77 | maven（9）/ javaweb-servlet（11）/ ssm（11）/ spring-boot（19）/ mybatis（9）/ linux（9）/ docker-k8s（9） |
| [03-distributed-microservices](../guides/backend/03-distributed-microservices/) | 95 | redis（9）/ mysql-advanced（7）/ nginx（9）/ spring-cloud（17）/ zookeeper（9）/ mq（19）/ elasticsearch（9）/ clickhouse（7）/ git（9） |
| [04-python-aiagent](../guides/backend/04-python-aiagent/) | 27 | python-core（7）/ langchain-rag（9）/ llm-fine-tuning（11） |
| [extensions](../guides/backend/extensions/) | 5 | project（5，电商订单实时统计分析平台） |

> **模块内文件约定**：原理文件 `NN-主题.md` + 章节导读 `NN-主题-导览.md` + 题集 `*笔面试题集.md` + 速查件（`常见错误汇总.md` / `概念对比速查.md` / `综合场景.md`）。

### 1.2 `guides/frontend/` — 前端笔面试资料库（201 文件 / 200 篇 Markdown）

| 索引文件 | 说明 |
|------|------|
| [README.md](../guides/frontend/README.md) | 前端学习总览、15 模块路线与逐文件索引 |
| [知识导览.md](../guides/frontend/知识导览.md) | 五维速查表（是什么 / 能做什么 / 怎么用 / 原理 / 缺点） |
| [前端学习路线图.md](../guides/frontend/前端学习路线图.md) · [.html](../guides/frontend/前端学习路线图.html) | 学习路线图 |
| [万能通用Bug定位查找逻辑.md](../guides/frontend/万能通用Bug定位查找逻辑.md) | 调试五步法、错误分类、Chrome DevTools 指南、场景排查手册 |
| [_CHANGELOG.md](../guides/frontend/_CHANGELOG.md) | 资料库版本演进记录（版本 / 日期 / 变更摘要 / 来源项目） |

| 模块 | 文件数 | 主题 |
|------|:------:|------|
| [01-html-css](../guides/frontend/01-html-css/) | 11 | HTML5 语义化、盒模型、Flex/Grid、BFC、回流重绘、响应式 |
| [02-javascript-core](../guides/frontend/02-javascript-core/) | 21 | 原型链、闭包、this、事件循环、Promise、ES6+、DOM、JSON、正则、BOM |
| [03-typescript](../guides/frontend/03-typescript/) | 9 | 类型系统、泛型、高级类型、工具类型、装饰器 |
| [04-browser](../guides/frontend/04-browser/) | 13 | 渲染流程、V8 引擎、事件循环、跨域、Web 安全、网络协议 |
| [05-vue](../guides/frontend/05-vue/) | 13 | Composition API、Proxy 响应式、diff 优化、Pinia、SSR/Nuxt |
| [06-react](../guides/frontend/06-react/) | 13 | Hooks、Fiber 架构、虚拟 DOM Diff、状态管理、数据请求层 |
| [07-engineering](../guides/frontend/07-engineering/) | 11 | Webpack、Vite、ESLint、CI/CD、Monorepo、质量门禁 |
| [08-performance](../guides/frontend/08-performance/) | 11 | Core Web Vitals、INP、懒加载、缓存策略、SSR/SSG/RSC |
| [09-nodejs](../guides/frontend/09-nodejs/) | 13 | Event Loop、Koa/Express、中间件、BFF、数据库、ORM、性能排查 |
| [10-project](../guides/frontend/10-project/) | 11 | 企业后台管理、电商平台、组件库/低代码/大屏/IM |
| [11-ai-assisted](../guides/frontend/11-ai-assisted/) | 13 | Cursor/Claude Code/Copilot、Prompt 工程、AI 代码审查、MCP/Agent |
| [12-cross-platform](../guides/frontend/12-cross-platform/) | 17 | uniapp、渲染差异、PWA、Web Components、桌面端、RN/Flutter、鸿蒙 |
| [13-architecture](../guides/frontend/13-architecture/) | 15 | 微前端、设计系统、分层架构、ADR、BFF 与权限、国际化与同构 |
| [14-monitoring](../guides/frontend/14-monitoring/) | 13 | Sentry、自建 SDK、埋点、灰度发布、Feature Flags、可观测性、A/B 实验 |
| [15-testing](../guides/frontend/15-testing/) | 11 | Vitest、Testing Library、Playwright、E2E、视觉回归、性能与契约测试 |

### 1.3 `guides/code-review/` — 代码理解与审查指令体系（4 篇）

| 文件 | 版本 | 作用 |
|------|------|------|
| [README.md](../guides/code-review/README.md) | — | 体系使用说明、场景示例、产出物位置 |
| [CODE_ANALYSIS_GUIDE.md](../guides/code-review/CODE_ANALYSIS_GUIDE.md) | v1.6.0 | 代码理解：逐文件生成调用图 + 功能说明文档（概览 / 标准 / 逐行） |
| [CODE_REVIEW_GUIDE.md](../guides/code-review/CODE_REVIEW_GUIDE.md) | v1.1.0 | 代码审查：对变更集出具分级意见 + 合入结论（快速 / 标准 / 严格） |
| [_GUIDE_CHANGELOG.md](../guides/code-review/_GUIDE_CHANGELOG.md) | — | 两份指南的合并版本变更记录 |

### 1.4 `guides/learning/` — 学习方法论（2 篇）

- [AI辅助源码阅读方法.md](../guides/learning/AI辅助源码阅读方法.md) —— 面向后端开发者的 AI 辅助开源项目源码阅读方法论
- [如何更好使用AI编程助手.md](../guides/learning/如何更好使用AI编程助手.md)

### 1.5 `guides/tools/` — 工具链速查（1 篇）

- [vscode-extensions.md](../guides/tools/vscode-extensions.md) —— VS Code 扩展清单

---

## 二、`docs/` — 技术专题深度笔记（36 文件）

### 2.1 `docs/harness/` — Agent Harness 深度讲解（15 文件）

| 文件 | 说明 |
|------|------|
| [README.md](harness/README.md) | 内容组织、使用方法、维护约定、内容自查记录 |
| [AGENTS.md](harness/AGENTS.md) | 面向 Agent 的工程说明 |
| [agent-harness-deep-dive.html](harness/agent-harness-deep-dive.html) | 长文 · 精读版：单页自包含交互式深度讲解，11 章（0–10）+ 附录（约 3 万字，深色主题，离线可开） |
| [code/minimal_harness.py](harness/code/minimal_harness.py) | 配套代码：可运行的最小 Harness 演示（约 720 行，仅依赖标准库） |
| [harness-from-principle-to-codex.md](harness/harness-from-principle-to-codex.md) | 长文 · 纯文本版：同主题 Markdown 长文，11 节 + 附录（约 1430 行，含术语谱系、Inner/Outer Harness 视角、可操作结论六步） |
| [images/](harness/images/) | 5 组原理图（PNG + SVG 各一份） |

### 2.2 `docs/大模型与神经网络原理笔记/` — 大模型视频课程结构化笔记（20 文件）

| 文件 | 说明 |
|------|------|
| [README.md](大模型与神经网络原理笔记/README.md) | 术语表（按首见章节排序）+ 全课程核心结论速查 |
| [ch01_raw_model.md](大模型与神经网络原理笔记/ch01_raw_model.md) | 裸模型 Raw Model：大模型的最底层真相 |
| [ch02_model_service.md](大模型与神经网络原理笔记/ch02_model_service.md) | 模型服务：API、定价与采样参数 |
| [ch03_ai_application.md](大模型与神经网络原理笔记/ch03_ai_application.md) | AI 应用层与概念分析方法论（Skill 实战） |
| [ch04_concepts_intelligence.md](大模型与神经网络原理笔记/ch04_concepts_intelligence.md) | 概念辨析与智能本质：AI 的分类 |
| [ch05_ml_overview.md](大模型与神经网络原理笔记/ch05_ml_overview.md) | AI 应用全景与机器学习：问题域与学习范式 |
| [ch06_neuron.md](大模型与神经网络原理笔记/ch06_neuron.md) | 神经元：从生物结构到数学模型（MP 模型） |
| [ch07_network_structure.md](大模型与神经网络原理笔记/ch07_network_structure.md) | 神经网络结构：分层、全连接与前向传播 |
| [ch08_loss_gradient.md](大模型与神经网络原理笔记/ch08_loss_gradient.md) | 损失与梯度下降：网络如何自我调整 |
| [ch09_backpropagation.md](大模型与神经网络原理笔记/ch09_backpropagation.md) | 反向传播：梯度下降的实现手段 |
| [ch10_training_mode.md](大模型与神经网络原理笔记/ch10_training_mode.md) | 训练模式：批量、张量与模型文件 |
| [assets/](大模型与神经网络原理笔记/assets/) | 自绘示意图（含 Mermaid 图，建议用 VSCode / Typora 打开） |

---

## 三、`src/` — 通用工具函数（6 文件）

| 文件 | 说明 |
|------|------|
| [python/utils.py](../src/python/utils.py) | `ensure_dir` / `timestamp_now` / `read_json` / `write_json` / `retry` |
| [js/README.md](../src/js/README.md) | JS/Node.js 通用工具索引（含依赖说明） |
| [js/utils.js](../src/js/utils.js) | 防抖 `debounce`、日期格式化 `formatDate`（无依赖） |
| [js/errors.js](../src/js/errors.js) | 通用自定义错误类层次（ServiceError 基类 + 6 个子类） |
| [js/query-helper.js](../src/js/query-helper.js) | Sequelize 通用分页 / 筛选查询 |
| [js/http-tool.js](../src/js/http-tool.js) | 统一响应 / JWT 解析 / 可配置上传 / Markdown TOC |

## 四、`examples/` — 用法示例（2 文件）

- [README.md](../examples/README.md) —— 示例索引
- [python-utils-demo.md](../examples/python-utils-demo.md) —— Python 工具函数用法演示

## 五、`scripts/` — 初始化脚本（1 文件）

- [setup.sh](../scripts/setup.sh) —— Linux / macOS 本地环境初始化

---

## 附：文件命名约定

| 后缀 / 前缀 | 含义 |
|------|------|
| `NN-主题.md` | 原理文件（正文） |
| `NN-主题-导览.md` | 章节导读（速览版，与原理文件一一对应） |
| `*笔面试题集.md` | 题库（选择题 + 简答 + 编程/场景设计，附解析） |
| `常见错误汇总.md` | 速查件：易错点汇总 |
| `概念对比速查.md` | 速查件：相近概念对照 |
| `综合场景.md` | 速查件：综合场景题 |
| `_*.md`（下划线前缀） | 内部 / 元文件（如变更日志） |
