# my-notes-and-utils

个人知识库与工具仓库：把**体系化学习指南**、**技术专题深度笔记**、**可复用工具函数**统一归档，便于检索与复用。

仓库以 Markdown 为主要载体（568 个文件，其中 502 篇 Markdown、约 25.6 万行），内容分两条主线：

- **知识线**：`guides/` 的笔面试学习资料库（后端 + 前端）与 `docs/` 的技术专题深度笔记；
- **工具线**：`src/` 的通用工具函数与 `examples/` 用法示例。

> 本文件是**全局落地页**：只给各子工程的定位与入口。每个子工程在自己的 `README.md` 中维护详细的总览、学习路线与逐文件索引——**要看细节就读它的 `README.md`**，避免多处重复。

---

## 目录结构

```
my-notes-and-utils/
├── docs/                     技术专题深度笔记（自成体系的交付物）
│   ├── harness/                Agent Harness 深度讲解 + 可运行最小实现
│   └── 大模型与神经网络原理笔记/  两门视频课程笔记：大模型原理（10 章）+ coding-agent/ 子课程（8 章）
├── guides/                   体系化学习指南（笔面试资料库）
│   ├── backend/                Java 后端：4 大模块 + 扩展
│   ├── frontend/               前端：15 个模块
│   ├── code-review/            代码理解 / 代码审查 Agent 指令体系
│   ├── learning/               学习方法论
│   └── tools/                  工具链速查
├── src/                      通用工具函数（js / python）
├── examples/                 src 工具函数的用法示例
├── scripts/                  本地脚本（环境初始化 + 配图 SVG → 2× PNG 渲染）
├── CONVENTIONS.md            工程约定（按需查阅，非常驻）
├── LICENSE                   MIT
└── README.md                 本文件
```

---

## 子工程索引

| 子工程 | 定位 | 入口 |
|--------|------|------|
| `guides/` | **体系化学习指南**：后端 / 前端笔面试资料库、代码理解与审查指令体系、学习方法论、工具链速查 | [`README`](guides/README.md) |
| `docs/` | **技术专题深度笔记**：Agent Harness 深度讲解、两门视频课程的结构化笔记 | [`README`](docs/README.md) |
| `src/` | **通用工具函数**：JavaScript / Node.js 与 Python，与业务解耦、可直接复制复用 | [`README`](src/README.md) |
| `examples/` | `src/` 工具函数的用法示例 | [`README`](examples/README.md) |
| `scripts/` | 本地脚本：环境初始化（`setup.sh`）与配图渲染（`svg-to-png.mjs`） | [`README`](scripts/README.md) |

---

## 如何使用

**作为知识库阅读**

1. 克隆仓库：`git clone https://github.com/xjq11029/my-notes-and-utils.git`
2. 从上方「子工程索引」定位方向，进入对应子工程的 `README.md`，按其学习路线或目录索引推进
3. 后端 / 前端学习者建议先读对应 `README.md` 的学习路线，再按模块推进，学完即刷题集
4. 涉及 Mermaid 图与公式的笔记（如 `docs/大模型与神经网络原理笔记/`）建议用 VSCode / Typora 打开

**作为工具箱使用**

1. 从 `src/` 挑选需要的工具文件，复制到你的工程
2. 依赖说明与使用约定见 [`src/README.md`](src/README.md)；用法示例见 [`examples/`](examples/README.md)

**作为 Agent 指令集使用**

- 将 `guides/code-review/` 下的指南复制到目标项目根目录，然后对 Agent 下达指令；详细场景与产出物位置见 [`guides/code-review/README.md`](guides/code-review/README.md)

---

## 维护约定

改工程前请先读 [`CONVENTIONS.md`](CONVENTIONS.md)——目录结构约定、变更日志机制、维护纪律与统计口径都在那里（**按需加载，不常驻提示词**）。

**唯一常驻纪律**：不主动提交或推送，需用户明确指令。

---

## 统计

| 项目 | 数值 |
|------|------|
| 文件总数 | 568（不含 `.git/`、内部目录 `.workbuddy/`、`.workbuddy-ai/` 与依赖目录 `node_modules/`） |
| Markdown 文档 | 502 篇 / 约 25.6 万行 |
| `guides/backend/` | 259 个文件 / 258 篇 Markdown |
| `guides/frontend/` | 201 个文件 / 200 篇 Markdown |
| `docs/` | 78 个文件 |
| `src/` | 8 个文件 |

---

## License

[MIT](LICENSE) © 2026 xjq11029
