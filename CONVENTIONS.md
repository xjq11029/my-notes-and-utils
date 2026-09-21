# 工程约定（按需加载）

> 本文件**不在 `AGENTS.md` 中展开**——它属于低频内容（只在改动工程时才需要），
> 常驻提示词会白白占用每次请求的上下文。按渐进式原则，这里只按需读取。
>
> **触发场景**：新增 / 重命名文档、调整目录结构、更新工程统计、写变更日志、修改任意 `README.md`。

---

## 一、目录内文件结构约定

### 指南类模块目录（`guides/backend/**`、`guides/frontend/**`）

每个子模块目录通常包含：

- **原理文件** `NN-主题.md` 与对应的 `NN-主题-导览.md`（章节导读，五维纵向表格：是什么 / 能做什么 / 怎么用 / 原理和工作流程 / 缺点）
- **笔面试题集** `*笔面试题集.md`（选择 + 简答 + 编程/场景，全附解析）
- **速查件**：`常见错误汇总.md` / `概念对比速查.md` / `综合场景.md`

> **强约束**：导览文件与源文件必须 **1:1 对应**。新增原理文件或题集时，必须同批创建配套 `-导览.md`。
>
> 特例：`guides/frontend/02-javascript-core/` 另含 2 个专属可视化文件。

### 课程笔记目录（`docs/**`）

- 章节文件命名 `chNN_英文小写下划线.md`（两位补零）
- 配图统一放该课程的 `assets/`，命名 `英文小写下划线.png|jpg|svg`
  - **矢量源 + 位图导出**：`.svg` 为矢量源（供二次编辑），`.png` 为 2× 导出——**Markdown 引用 PNG**，不直接引 SVG
    - 例外：**对外发布稿**（`docs/harness/articles/images/`）用 **4×**（2720px 宽）。这些图要上传到掘金 / CSDN，会被读者放大查看、经平台二次缩放，位图需更高像素密度（长文里同图是内联 SVG，放大不糊）。理由见 [`docs/harness/articles/README.md`](docs/harness/articles/README.md)
  - 渲染脚本：`node scripts/svg-to-png.mjs <assets 目录>`（依赖见 `scripts/package.json`）
  - 历史遗留的手机拍屏照片等原始素材，移入 `assets/_原始拍照/` 存档，正文不再引用
- 每章 H1 为 `# 第 N 章 中文主标题：中文副标题`
- 章节骨架固定：`## 一、概念` → `## 二、原理推导` → `## 三、演示步骤（按讲解顺序还原）` → `## 四、关键结论` → `## 本节要点回顾`
  - 第三节的标题按**实际内容**命名：有真机演示的用「白板演示步骤」或「演示步骤」（均带「按讲解顺序还原」）；仅有口头说明、无实操的用「使用要点（本章无现场演示）」，并在节首一句说明原因——**标题必须与内容相符**，不要给纯理论归纳挂「演示」的名
- **禁用 LaTeX**：公式一律用行内反引号 / blockquote 加粗 / ```text 框线块
- Mermaid 一律 **`graph TD` 竖排**，图前引导句「用 Mermaid 还原 …（竖向）：」
- 章间引用用**纯文本「第 N 章」**，不用 Markdown 链接；仅 README 的章节目录表用链接
- 逐字稿等转写中间产物**不纳入仓库**（整理时临时生成、完成后删除）；课件原文等需长期留存的元文件用 `_` 前缀

### 单文件自包含（`docs/harness/*.html`）

`docs/harness/agent-harness-deep-dive.html` 必须保持**单文件自包含**（无 CDN / 无外部字体 / 无外部 JS），支持离线打开。

### 数据来源分级（`docs/harness/`）

对关键数据做可信度分级（一手来源 / 源码分析 / 二手报道），修改时维持该约定。

### 元文件约定

下划线前缀 `_*.md` 为内部 / 元文件（如变更日志、课件原文存档）。

---

## 二、变更日志机制

仓库现有三份变更日志：

- `guides/code-review/_GUIDE_CHANGELOG.md`
- `guides/backend/_CHANGELOG.md`
- `guides/frontend/_CHANGELOG.md`

**格式**：标题 + 3 行 blockquote 引言 + 表格，4 列 `| 版本 | 日期 | 变更摘要 | 来源项目 |`；
**升序排列**（最旧在上）；语义化 `vX.Y.Z`；日期 `YYYY-MM-DD`；摘要为长句，类别（新增 / 扩充 / 修复 / 修订）以正文动词内联表达，不单设分类列。

**版本规则**：

| 改动 | 版本变化 |
|---|---|
| 新增模块 / 新增原理文件或题集 / 新增章节 | 次版本号 +1 |
| 扩充条目、修订措辞、修正错误 | 修订号 +1 |

**登记位置**：对应目录的 `README.md` + 根 `README.md` + 根 `AGENTS.md`。

> ⚠️ 曾登记过的 `docs/TOC.md` 经 2026-09-18 核查**不存在**（仓库内无任何 TOC 类文件），已从清单移除。

---

## 三、维护纪律

1. **README 真实性**：任何目录中的 `README.md` 必须真实反映该目录实际情况，发现差异**即时修正**。
2. **同步上层**：改动工程后，同步更新 `AGENTS.md`（工程功能 + 关键目录结构）与根 `README.md`（含「统计」表）。
3. **不主动提交或推送**：改动完成后报告，等用户明确指令。
4. **同一文件禁止在同一条消息里并发发起多个 Edit** —— 会静默丢失改动（工具仍报成功）。批量修改请用带 `count == 1` 校验的脚本一次性完成。
5. **删除未跟踪目录前必须先核对**：`git status` 显示为 `??` 的目录删掉后无法从历史恢复，务必「先搬移 → 核对文件数 → 再删除」。

---

## 四、统计口径

**排除**：`.git/`、`.workbuddy/`、`.workbuddy-ai/`、`node_modules/`。

```bash
# 总文件数
find . -type f ! -path './.git/*' ! -path './.workbuddy/*' ! -path './.workbuddy-ai/*' ! -path '*/node_modules/*' | wc -l

# Markdown 篇数
find . -type f -name '*.md' ! -path './.git/*' ! -path './.workbuddy/*' ! -path './.workbuddy-ai/*' ! -path '*/node_modules/*' | wc -l

# Markdown 总行数（必须用 -exec cat {} +；用 xargs wc -l 会分批截断）
find . -type f -name '*.md' ! -path './.git/*' ! -path './.workbuddy/*' ! -path './.workbuddy-ai/*' ! -path '*/node_modules/*' -exec cat {} + | wc -l

# 单目录文件数
find docs -type f | wc -l
```

> 注意：`find` 的 `-path` 参数**必须加引号**，否则 `!` 会被 shell 展开导致报错。
> `node_modules/` 是 `scripts/` 下按需安装的依赖（已被 `.gitignore` 排除），统计时必须一并排除，否则数字会被依赖包内的文件污染。
