# my-notes-and-utils

一个集中管理 **常用模板、学习指南与工具函数** 的仓库。目标是把零散的 Markdown 模板、体系化的技术学习指南，以及可复用的工具代码，统一归档、便于检索与复用。

## 目录结构

- `docs/`        —— 常用 Markdown 模板与零散笔记（会议记录、速查表等，见 `docs/templates/`）
- `guides/`      —— 体系化学习指南，按技术域拆分：
  - `guides/backend/`     后端技术学习指南（Java / Spring / 分布式 / Python AI 等）
  - `guides/frontend/`    前端技术学习指南（HTML / CSS / JS / TS / Vue / React 等）
  - `guides/code-review/` 代码理解与审查指南及变更日志
- `src/`         —— 常用工具函数（按语言分类：Python / JavaScript）
- `examples/`    —— `src` 工具函数的用法示例
- `scripts/`     —— 本地初始化脚本

## 文档索引

完整的文档目录见 [`docs/TOC.md`](docs/TOC.md)。

## 如何使用

1. 克隆仓库：`git clone https://github.com/xjq11029/my-notes-and-utils.git`
2. 按需将 `docs/templates/` 下的模板复制到你的项目
3. 参考 `guides/` 下的技术指南进行学习
4. 使用 `src/` 下的工具函数，并查看 `examples/` 中的用法示例
