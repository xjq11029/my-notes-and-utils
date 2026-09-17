# AGENTS.md

## 工程功能

本目录是关于 **Agent Harness（智能体脚手架 / 运行时控制层）** 的深度技术讲解交付物，含两篇互补长文 + 一套可运行演示：

1. **精读版**（`agent-harness-deep-dive.html`，约 3 万字）：单页自包含交互式 HTML。主线为底层思想 → 第一性原理（长周期任务的五个必然问题）→ 结构解剖（12 个组件）→ 动手实现（最小 Harness）→ Codex 源码级实现 → 横向案例对比 → 七个架构决策 → 模型与脚手架协同设计 → 误区与未来 → **生产化纵深**（评测 / 成本 / 安全 / 恢复 / 运维 / 合规 / RL 闭环）。
2. **纯文本版**（`harness-from-principle-to-codex.md`，约 1430 行）：同一主题的 Markdown 长文，含精读版未覆盖的术语谱系与演进史、Inner/Outer Harness 视角、可操作结论六步、来源可信度分级；另有与精读版共有的第 10 章「生产化纵深」；配图走 `images/`。
3. **可运行演示**（`code/minimal_harness.py`）：脚本化 Mock LLM（无需 API Key、可离线运行），演示"同一个模型，六套 harness，六种结果"。

## 两篇长文的分工

- **精读版（HTML）**：完整通读、交互式阅读；所有图示内联，**不依赖** `images/`。
- **纯文本版（MD）**：检索、摘录、diff、迁移到其他笔记系统；引用 `images/` 下的 5 张图。

两者可独立阅读，主题重叠但各有独特章节（详见 `README.md` 的分工对照表），非重复冗余。

## 关键目录结构

```
harness/
├── AGENTS.md                           # 本文件，面向 Agent 的工程说明
├── README.md                           # 完整项目文档（交付物分工、使用方法、维护约定、已知限制）
├── agent-harness-deep-dive.html         # 长文 · 精读版
│                                        #   单页自包含（无 CDN / 无外部字体 / 无外部 JS），深色主题
│                                        #   9 张内联 SVG、31 张对比表、41 段代码
│                                        #   左侧目录滚动高亮、代码一键复制、源码细节可折叠
├── harness-from-principle-to-codex.md   # 长文 · 纯文本版（11 节 + 附录，含图 1–5 原始 SVG 源码）
├── code/
│   └── minimal_harness.py               # 最小 Harness 演示（约 720 行，仅依赖标准库）
│                                        #   运行：python minimal_harness.py
│                                        #   六版递进：v0 裸调用 → v1 ReAct 循环 → v2 权限沙箱
│                                        #            → v3 状态持久化 → v4 上下文压缩 → v5 验证门
└── images/
    └── fig1–fig5.{png,svg}              # 纯文本版引用的 5 张图（PNG 2× 供 Markdown，SVG 矢量供编辑）
```

> 详细说明、使用方法、维护约定与已知限制见 `README.md`。
