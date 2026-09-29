# 技术专题深度笔记（docs）

自成体系的技术专题交付物：每一份都是**独立成文的长文或课程笔记**，不依附于某条学习路线，可按需单独阅读。

## 子工程索引

| 子工程 | 定位 | 规模 | 入口 |
|--------|------|------|------|
| [`harness/`](harness/) | Agent Harness（智能体脚手架 / 运行时控制层）深度讲解：精读版 HTML 长文 + 纯文本版 MD 长文 + 可运行最小实现 | 14 个文件 / 2 篇 | [README](harness/README.md) |
| [`agent开发教程/`](agent开发教程/) | **Agent 应用开发教程**：LangChain v1 / LangGraph v1 / Deep Agents 四层递进（基础层 + 三件套），18 章 MD 教程 + HTML 精读版 + Python / TypeScript 双语言实测示例 + 32 张自绘机制图 | 128 个文件 / 21 篇 | [README](agent开发教程/README.md) |
| [`大模型与神经网络原理笔记/`](大模型与神经网络原理笔记/) | 两门视频课程的结构化笔记：**大模型与神经网络原理**（10 章）+ **Coding Agent 原理与工具链**（8 章，子目录 [`coding-agent/`](大模型与神经网络原理笔记/coding-agent/README.md)） | 57 个文件 / 21 篇 | [README](大模型与神经网络原理笔记/README.md) · [coding-agent](大模型与神经网络原理笔记/coding-agent/README.md) |
| [`Jev/`](Jev/) | **决策式模型 Jev 主题笔记**（非课程整理）：TypeSafe AI 的「System One 模型」，6 章覆盖定位与由来 / 三个原语与 API 契约 / RLCD 校准原理 / 与 LLM 的分工 / 工程实践 / 基准与争议 | 22 个文件 / 8 篇 | [README](Jev/README.md) |

## 与 `guides/` 的分工

| | `guides/` | `docs/` |
|---|---|---|
| 组织方式 | 按技术域的**体系化学习路线**（后端 / 前端笔面试资料库） | 按主题的**单点深度交付物**（一份长文讲透一个主题） |
| 文件结构 | 模块化四类文件：原理 + 导览 + 题集 + 速查件 | 长文 / 课程章节，自成体系 |
| 服务目的 | 系统学习与应试，按路线推进 | 深入理解，可独立阅读、不依赖前后文 |

## 文件结构说明

- **课程笔记目录**（`大模型与神经网络原理笔记/**`）：章节文件命名 `chNN_英文小写下划线.md`（两位补零）；配图统一放该课程的 `assets/`，约定为**矢量源 SVG + 2× PNG 导出**（Markdown 引用 PNG），重新渲染用 [`scripts/svg-to-png.mjs`](../scripts/svg-to-png.mjs)；原始拍屏照片等素材存 `assets/_原始拍照/`，正文不引用。
- **主题笔记目录**（`Jev/**`）：内容**不是课程整理**，而是围绕单一主题自成体系的笔记；文件、配图与章节骨架约定见 [`CONVENTIONS.md`](../CONVENTIONS.md) 的「主题笔记目录」条目；其 `_来源与数据分级.md` 为来源底账元文件。
- **长文交付物**（`harness/**`）：`agent-harness-deep-dive.html` 必须保持**单文件自包含**（无 CDN / 无外部字体 / 无外部 JS），支持离线打开。
- **教程交付物**（`agent开发教程/**`）：双档交付——18 章 MD 教程 + 单文件 HTML 精读版。**配图为深色面板 SVG**（自带满幅底色 `#111721`，与 HTML 精读版同一份源），仍走 **2× PNG** 导出；HTML 由 [`_build_html.py`](agent开发教程/_build_html.py) 从章节 + `assets/` 生成（**幂等**，改章节后须重跑）。示例代码为 **Python / TypeScript 双语言一一对应**，用脚本化假模型离线运行，**不需要 API Key**。
- **对外发布稿**（仓库根 `articles/**`）：见 [`articles/README.md`](../articles/README.md)——从长文 / 笔记切出、面向技术社区（掘金 / CSDN 等）的独立文章，**按类别分目录、一篇文章一个独立目录**，编号与引用**重新组织、不指向源文件后文**。该目录有自己的 README 说明统一约定（图号烧进图片、4× 导出、引用框类型标签），每篇文章目录另有 README 记对应关系与再生成命令。
- 下划线前缀 `_*.md` / `_*.py` 为内部 / 元文件（如课件原文存档、HTML 构建脚本）。
- 含 Mermaid 图的笔记建议用 **VSCode / Typora** 打开（图会自动渲染）。

> 工程级维护纪律（README 真实性、统计口径、变更日志格式等）见仓库根 [`CONVENTIONS.md`](../CONVENTIONS.md)。
