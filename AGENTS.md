# AGENTS.md

## 工程定位与技术栈

`my-notes-and-utils` 是个人知识库与工具仓库：**体系化学习指南** + **技术专题深度笔记** + **可复用工具函数**，以 Markdown 为主要载体（559 个文件 / 501 篇 Markdown / 约 25.6 万行）。

技术栈：主体为 Markdown（无构建系统、无 CI）；`src/js/` 为 JavaScript / Node.js（按需 `require` 第三方依赖）；`src/python/` 仅标准库；`scripts/` 为本地脚本（Shell + Node ESM，依赖按需 `npm install`）。

## 目录结构

```
my-notes-and-utils/
├── docs/             # 技术专题深度笔记（harness / 大模型与神经网络原理笔记）
├── guides/           # 体系化学习指南（backend / frontend / code-review / learning / tools）
├── src/              # 通用工具函数（js / python）
├── examples/         # src 工具函数的用法示例
├── scripts/          # 本地脚本（环境初始化 + 配图 SVG → 2× PNG 渲染）
└── CONVENTIONS.md    # 工程约定（按需查阅，非常驻）
```

## 索引

**每个顶层目录均自带 `README.md`**，承载该目录的定位、规模与子目录 / 文件索引。要进入某个目录，**先读它的 `README.md`**，不要在本文件里找细节：

| 顶层目录 | 入口 |
|---|---|
| `docs/` | [`README`](docs/README.md) |
| `guides/` | [`README`](guides/README.md) |
| `src/` | [`README`](src/README.md) |
| `examples/` | [`README`](examples/README.md) |
| `scripts/` | [`README`](scripts/README.md) |

## 按需查阅（渐进式）

详细约定**不在此展开**——它们只在改动工程时才需要，常驻会白占每次请求的上下文。改工程前按需读：

| 当你要… | 读 |
|---|---|
| 新增 / 重命名文档、调整目录结构、写变更日志、修改任意 `README.md`、更新统计数字 | [`CONVENTIONS.md`](CONVENTIONS.md) |

**唯一常驻纪律**：不主动提交或推送代码 / 文件，需用户明确指令。
