# AGENTS.md

## 工程功能

`my-notes-and-utils` 是个人知识库与工具仓库，把**体系化学习指南**、**技术专题深度笔记**、**可复用工具函数**统一归档，便于检索与复用。以 Markdown 为主要载体（518 个文件，其中 487 篇 Markdown、约 25 万行；统计不含 `.git/` 与内部目录 `.workbuddy/`、`.workbuddy-ai/`）。

内容分两条主线：

1. **知识线**
   - `guides/backend/` —— Java 后端笔面试资料库：Java 基础、JavaWeb 单体架构、分布式微服务、Python AI Agent，共 4 大模块 + 1 个扩展模块。
   - `guides/frontend/` —— 前端笔面试资料库：HTML/CSS、JS 核心、TypeScript、浏览器原理、Vue、React、工程化、性能、Node.js、实战项目、AI 辅助、跨端、架构、监控、测试，共 15 个模块。
   - `guides/code-review/` —— 供 Agent 加载的代码理解 / 代码审查指令规范（分析指南 + 审查指南 + 合并变更日志）。
   - `guides/learning/`、`guides/tools/` —— 学习方法论与工具链速查。
   - `docs/harness/` —— Agent Harness 深度讲解（精读版 HTML 长文 + 纯文本版 Markdown 长文，含"生产化纵深"章）+ 可运行的最小 Harness 演示。
   - `docs/大模型与神经网络原理笔记/` —— 大模型视频课程结构化笔记（10 章）。
2. **工具线**
   - `src/` —— 与业务解耦的通用工具函数（JavaScript/Node.js 与 Python）。
   - `examples/` —— `src/` 工具函数的用法示例。
   - `scripts/` —— 本地环境初始化脚本。

## 关键目录结构

```
my-notes-and-utils/
├── README.md                   # 工程总览（定位、目录结构、内容详解、使用方式、维护约定）
├── AGENTS.md                   # 本文件，面向 Agent 的工程说明
├── LICENSE                     # MIT
├── docs/                       # 技术专题深度笔记
│   ├── harness/                #   Agent Harness 深度讲解（精读版 HTML + 纯文本版 MD + minimal_harness.py + images + 自身 README.md）
│   └── 大模型与神经网络原理笔记/  #   大模型课程笔记 ch01–ch10 + assets/ + README.md
├── guides/                     # 体系化学习指南
│   ├── backend/                #   README.md、_CHANGELOG.md、知识导览.md、路线图 PNG
│   │   ├── 01-java-basics/                 # java-core / jvm-juc / mysql-jdbc
│   │   ├── 02-javaweb-monolith/            # maven / javaweb-servlet / ssm / spring-boot / mybatis / linux / docker-k8s
│   │   ├── 03-distributed-microservices/   # redis / mysql-advanced / nginx / spring-cloud / zookeeper / mq（kafka / rabbitmq / rocketmq） / elasticsearch / clickhouse / git
│   │   ├── 04-python-aiagent/              # python-core / langchain-rag / llm-fine-tuning
│   │   └── extensions/project/             # 实战项目
│   ├── frontend/               #   README.md、知识导览.md、前端学习路线图(.md/.html)、万能通用Bug定位查找逻辑.md
│   │   └── 01-html-css/ … 15-testing/      #   15 个模块目录
│   ├── code-review/            #   CODE_ANALYSIS_GUIDE.md / CODE_REVIEW_GUIDE.md / _GUIDE_CHANGELOG.md / README.md
│   ├── learning/               #   AI辅助源码阅读方法.md、如何更好使用AI编程助手.md
│   └── tools/                  #   vscode-extensions.md
├── src/                        # 通用工具函数
│   ├── js/                     #   utils.js / errors.js / query-helper.js / http-tool.js + README.md（依赖索引）
│   └── python/                 #   utils.py
├── examples/                   # 用法示例（python-utils-demo.md + README.md）
└── scripts/                    # setup.sh（Linux/macOS 环境初始化）
```

## 目录内文件结构约定

- **指南类模块目录**（`guides/backend/**`、`guides/frontend/**`）通常包含：
  - 原理文件 `NN-主题.md` 与对应的 `NN-主题-导览.md`（章节导读）；
  - 笔面试题集 `*笔面试题集.md`（选择题 + 简答 + 编程/场景设计，附解析）；
  - 速查件 `常见错误汇总.md` / `概念对比速查.md` / `综合场景.md`。
  - 特例：`guides/frontend/02-javascript-core/` 另含 2 个专属可视化文件（`01-语法基础与执行机制-原型链流程图.md`、`01-语法基础与执行机制-双链协同图.md`）。
- **变更日志**：`guides/code-review/_GUIDE_CHANGELOG.md`、`guides/backend/_CHANGELOG.md` 记录对应指南体系的版本演进（版本 / 日期 / 变更摘要 / 来源项目）。
- **每个目录的 `README.md` 必须真实反映该目录实际情况**，发现差异即时修正。
- **数据来源分级**：`docs/harness/` 对关键数据做可信度分级（一手来源 / 源码分析 / 二手报道），修改时维持该约定。
- **`docs/harness/agent-harness-deep-dive.html` 必须保持单文件自包含**（无 CDN / 无外部字体 / 无外部 JS），支持离线打开。

## 维护纪律

- 改动工程后同步更新本文件（工程功能 + 关键目录结构）与根 `README.md`。
- 不主动提交或推送代码 / 文件，需用户明确指令。
