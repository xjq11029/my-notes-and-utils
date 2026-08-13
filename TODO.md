# 待处理问题清单（Known Issues）

> 来源：2026-08-13 对 `my-notes-and-utils` 的目录健康检查。
> 状态：待处理。处理完成后请从本清单移除对应条目或标记为已完成。

## 概览

| # | 严重度 | 问题 | 位置 | 状态 |
|---|--------|------|------|------|
| 1 | 高 | `src/js/utils.js` 语法错误 | `src/js/utils.js:1` | ✅ 已修复 |
| 2 | 中 | 遗留 secret 占位符（GitHub 已告警） | `guides/frontend/12-cross-platform/01-uniapp跨端开发基础.md:431` | ✅ 已修复 |
| 3 | 低 | `backend` 模块编号冲突 | `guides/backend/` | ✅ 已修复（实为 16 个空占位目录，已删除） |

---

## 1. `src/js/utils.js` 存在真实语法错误【高】

**现象**：文件首行使用 `# 常用 JS 工具示例`（Python 注释风格）。JavaScript 不识别 `#` 作为注释符，`node --check` 报 `SyntaxError: Invalid or unexpected token`。

**影响**：该文件无法被 `require` / `import`，任何引用都会直接抛语法错误。

**位置**：`src/js/utils.js` 第 1 行。

**修复方案**：将首行 `#` 改为 `//`。

**状态**：✅ 已修复（2026-08-13，commit `ba6326f`）。`node --check` 通过，首行现为 `// 常用 JS 工具示例`。

---

## 2. 遗留 secret 占位符未处理（GitHub secret scanning 已告警）【中】

**现象**：`guides/frontend/12-cross-platform/01-uniapp跨端开发基础.md:431` 包含 `appid: "wx1234567890abcdef"`，符合微信小程序 AppID 格式（`wx` + 16 位十六进制），被 GitHub secret scanning 识别为 "Tencent WeChat API App ID" 并触发邮件告警（关联 commit `9c188ab`）。

**风险评估**：低。`1234567890abcdef` 为连续十六进制，明显是示例/占位值，非真实密钥，无被利用风险。但 GitHub secret scanning 只做格式匹配、不区分真实与示例，会持续告警直至关闭。

**处理方案**：
1. 将 `wx1234567890abcdef` 替换为明显占位符，如 `wxYOUR_APPID_HERE`（含大写与下划线，不匹配 AppID 格式，不再触发扫描）。
2. 提交并推送。
3. 在 GitHub 关闭告警：仓库 → Security → Secret scanning → 找到该条 "Tencent WeChat API App ID" → Close as → "False positive"。

**状态**：✅ 已修复（2026-08-13，commit `ba6326f`）。占位值已替换为 `wxYOUR_APPID_HERE`，全仓库扫描确认无残留 AppID；并通过 GitHub API 将该告警（alert #1）标记为 `resolved / false_positive`，告警已消除。

---

## 3. `backend` 模块编号冲突【低】

**现象**：`guides/backend/` 下 20 个主题模块中，`01/02/03/04` 编号各重复 2 次：
- `01-java-basics` 与 `01-java-core`
- `02-javaweb-monolith` 与 `02-spring-boot`
- `03-data-access` 与 `03-distributed-microservices`
- `04-message-queue` 与 `04-python-aiagent`

而 `guides/frontend/` 为 `01-15` 严格连续编号，两套编号风格不一致。

**说明**：`backend` 的重复编号可能是「同主题大类共享编号」的有意设计（如 `01` 均为 Java 语言），并非错误；是否重编号取决于想采用的约定。另外发现 `04-python-aiagent` 与 `14-python-ai-agent` 疑似主题重叠，可一并梳理。

**可选方案**：
- A. 保持现状：`backend` 用「大类编号」、`frontend` 用「唯一编号」，在 `README.md` 中注明约定。
- B. 统一唯一编号：`backend` 20 个模块重新连续编号为 `01-20`，并同步更新 `docs/TOC.md`（改动较大，会调整目录名）。
- C. 最小改动：仅给重复的 4 组重新分配后缀字母或新编号。

**状态**：✅ 已修复（2026-08-13）。经核查，所谓「20 个模块编号冲突」实为误判——真正有内容且被 git 跟踪的模块仅 4 个（`01-java-basics`、`02-javaweb-monolith`、`03-distributed-microservices`、`04-python-aiagent` + `extensions`），编号 01–04 本就唯一、无冲突；而 `01-java-core`、`02-spring-boot`、`03-data-access`、`04-message-queue`、`05-microservices`…`16-maven` 共 **16 个空目录**且未被 git 跟踪（git 不跟踪空目录），是「编号重复」的表象来源。已删除这 16 个空占位目录，`guides/backend/` 顶层现仅余 4 个真实模块 + `extensions` + 文档文件；同步更新 `docs/TOC.md` 模块清单为真实 4 模块。空目录未入库，无需提交删除动作本身。

---

## 处理记录

- **2026-08-13** · 问题 1（`src/js/utils.js` 语法错误）→ 已修复，commit `ba6326f`。
- **2026-08-13** · 问题 2（secret 占位符）→ 已修复并推送（`ba6326f`），GitHub 告警 #1 已通过 API 关闭为 false positive。
- **2026-08-13** · 问题 3（`backend` 编号冲突）→ 已修复：删除 16 个未跟踪的空占位目录，真实模块 01–04 唯一；同步更新 `docs/TOC.md`。
