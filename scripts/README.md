# 本地脚本（scripts）

仓库的**本地环境初始化与素材处理**脚本。本仓库主体为 Markdown 文档，无构建系统、无 CI、无部署流程——脚本只在需要时手动跑。

## 文件清单

| 文件 | 用途 | 适用平台 |
|------|------|----------|
| [`setup.sh`](setup.sh) | 在仓库根目录创建并激活 Python 虚拟环境 `.venv`，并升级 pip | Linux / macOS |
| [`svg-to-png.mjs`](svg-to-png.mjs) | 把课程笔记的配图 SVG 矢量源批量渲染为 2× PNG（Markdown 引用的是 PNG） | 跨平台（Node ≥ 18） |
| [`package.json`](package.json) | `svg-to-png.mjs` 的依赖声明（`@resvg/resvg-js`） | — |

## 使用

### setup.sh

```bash
bash scripts/setup.sh
```

脚本会在**仓库根目录**生成 `.venv/`。

> 说明：本仓库的日常阅读与检索**无需**运行任何脚本。`setup.sh` 仅在需要用 Python 跑示例（如 [`docs/harness/code/minimal_harness.py`](../docs/harness/code/minimal_harness.py)）时按需执行；由于该示例仅依赖标准库，实际上不建虚拟环境也能直接运行。

### svg-to-png.mjs

课程笔记的配图约定为「**SVG 矢量源 + 2× PNG 导出**」：`.svg` 供二次编辑，`.png` 供 Markdown 引用。改完 SVG 后跑一次即可重新生成全部 PNG。

```bash
# 首次使用：先装依赖（装在 scripts/node_modules，已被 .gitignore 排除）
cd scripts && npm install --registry=https://registry.npmmirror.com && cd ..

# 渲染整个 assets 目录（自动跳过已是最新的 PNG）
node scripts/svg-to-png.mjs "docs/大模型与神经网络原理笔记/coding-agent/assets"

# 强制全部重渲染 / 指定单张 SVG / 改缩放倍率
node scripts/svg-to-png.mjs "docs/大模型与神经网络原理笔记/coding-agent/assets" --force
node scripts/svg-to-png.mjs assets/06_mcp_flow.svg --scale 2
```

行为要点：

- 递归查找目录下的 `*.svg`，在**同目录**生成同名 `.png`；文件名以 `_` 开头的 SVG 一律跳过（元文件 / 内部素材）
- 默认跳过「PNG 比 SVG 新」的文件，只重渲染改动过的图
- 已显式指定中文字体（微软雅黑 / 黑体等），避免中文渲染成方块

> 兜底方案：若 `@resvg/resvg-js` 装不上或字体加载异常，可改用浏览器 / Chromium 截图渲染；SVG 本身也可直接被 VSCode、Typora、GitHub 渲染，必要时可只交付 `.svg`。
