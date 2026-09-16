# AGENTS.md

## 工程功能

本工程是一份关于 **Agent Harness（智能体脚手架 / 运行时控制层）** 的深度技术讲解交付物，包含两部分：

1. **单页 HTML 深度讲解**（约 2.8 万字）：从底层思想（冯·诺依曼架构同构）→ 第一性原理（长周期任务的五个必然问题）→ 结构解剖（12 个组件）→ 动手实现（最小 Harness）→ Codex 源码级实现（含 Prompt Cache 一等约束）→ 横向案例对比（含 LangChain 不换模型实验）→ 架构决策 → 模型与脚手架的协同设计 → 误区与未来。
2. **可运行的 Python 最小 Harness 演示**：用脚本化的 Mock LLM（无需 API Key、可离线运行）演示"同一个模型，六套 harness，六种结果"。

## 关键目录结构

```
2026-09-15-16-13-17/
├── AGENTS.md                      # 本文件，面向 Agent 的工程说明
├── README.md                      # 完整项目文档（内容组织、使用方法、维护约定）
├── agent-harness-deep-dive.html   # 主交付物：单页 HTML 深度讲解
│                                  #   深色主题，自包含（无 CDN / 无外部字体 / 无外部 JS）
│                                  #   9 张内联 SVG、22 张对比表、34 段代码
│                                  #   左侧目录滚动高亮、代码块一键复制、源码细节可折叠
└── code/
    └── minimal_harness.py         # 最小 Harness 演示（约 700 行，仅依赖标准库）
                                   #   运行：python minimal_harness.py
                                   #   六版递进：v0 裸调用 → v1 ReAct 循环 → v2 权限沙箱
                                   #            → v3 状态持久化 → v4 上下文压缩 → v5 验证门
```

> 详细说明、使用方法、维护约定与已知限制见 `README.md`。
