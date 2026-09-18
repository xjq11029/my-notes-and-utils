# 体系化学习指南（guides）

按技术域划分的体系化学习资料与 Agent 指令体系，便于按方向检索与推进。

## 子工程索引

| 子工程 | 定位 | 规模 | 入口 |
|--------|------|------|------|
| [`backend/`](backend/) | Java 后端笔面试资料库：Java 基础、JavaWeb 单体、分布式微服务、Python AI Agent（4 大模块 + 1 扩展） | 258 篇 | [README](backend/README.md) |
| [`frontend/`](frontend/) | 前端笔面试资料库：HTML/CSS、JS、TS、浏览器、Vue、React、工程化、性能、Node.js、实战、AI 辅助、跨端、架构、监控、测试（15 个模块） | 200 篇 | [README](frontend/README.md) |
| [`code-review/`](code-review/) | 供 Agent 加载的代码理解 / 代码审查指令规范（分析指南 + 审查指南 + 合并变更日志） | 4 篇 | [README](code-review/README.md) |
| [`learning/`](learning/) | 学习方法论：AI 辅助源码阅读、如何更好使用 AI 编程助手 | 3 篇 | [README](learning/README.md) |
| [`tools/`](tools/) | 工具链速查：VS Code 扩展清单 | 2 篇 | [README](tools/README.md) |

## 文件结构说明

- 指南类模块目录（`backend/**`、`frontend/**`）通常包含：原理文件 `NN-主题.md` 与对应导览 `NN-主题-导览.md`、笔面试题集 `*笔面试题集.md`、速查件（`常见错误汇总.md` / `概念对比速查.md` / `综合场景.md`）。
- 下划线前缀 `_*.md` 为内部 / 元文件（如变更日志）。

> 工程级维护纪律（README 真实性、统计口径、变更日志格式等）见仓库根 [`CONVENTIONS.md`](../CONVENTIONS.md)。
