# 本地脚本（scripts）

仓库的**本地环境初始化与素材处理**脚本。本仓库主体为 Markdown 文档，无构建系统、无 CI、无部署流程——脚本只在需要时手动跑。

## 文件清单

| 文件 | 用途 | 适用平台 |
|------|------|----------|
| [`setup.sh`](setup.sh) | 在仓库根目录创建并激活 Python 虚拟环境 `.venv`，并升级 pip | Linux / macOS |
| [`svg-to-png.mjs`](svg-to-png.mjs) | 把配图 SVG 矢量源批量渲染为 PNG（**默认 2×**，`--scale` 可改；Markdown 引用的是 PNG） | 跨平台（Node ≥ 18） |
| [`extract-svg-from-html.py`](extract-svg-from-html.py) | 把 HTML 里的内联 `<svg>` 抽成独立 `.svg` 文件，可选注入满幅底色与底部居中的「图 N」（深色主题长文 → 浅色发布平台的关键一步） | 跨平台（Python ≥ 3.10） |
| [`package.json`](package.json) | `svg-to-png.mjs` 的依赖声明（`@resvg/resvg-js`） | — |

## 使用

### setup.sh

```bash
bash scripts/setup.sh
```

脚本会在**仓库根目录**生成 `.venv/`。

> 说明：本仓库的日常阅读与检索**无需**运行任何脚本。`setup.sh` 仅在需要用 Python 跑示例（如 [`docs/harness/code/minimal_harness.py`](../docs/harness/code/minimal_harness.py)）时按需执行；由于该示例仅依赖标准库，实际上不建虚拟环境也能直接运行。

### extract-svg-from-html.py

长文 HTML（如 [`docs/harness/agent-harness-deep-dive.html`](../docs/harness/agent-harness-deep-dive.html)）的图示是**内联 SVG**——内嵌在单文件里、不依赖外部图片。要往 Markdown 平台（掘金 / CSDN）发文章时，得先把它们变成独立图片。本脚本负责第一步：抽成 `.svg`；第二步交给 `svg-to-png.mjs`。

```bash
# 抽取 §0–§3 区间的 13 张图 → 注入深色底 → 注入底部居中的「图 N」→ 修正图内失效引用
python scripts/extract-svg-from-html.py \
    docs/harness/agent-harness-deep-dive.html \
    articles/agent-harness/agent-harness-from-analogy-to-12-components/images \
    --from-anchor s0 --to-anchor s4 --bg '#111721' --expect 13 --label \
    --replace '方块里的数字与 3.1 的组件表一致=方块里的数字与组件表的编号一致' \
    --names three-layers,von-neumann,concentric-rings,five-problems,controlled-loop,\
problem-component-map,agent-loop,memory-scales,silent-failure,prompt-layers,\
state-management,subagent-firewall,component-placement

# 先干跑看清单，不写盘
python scripts/extract-svg-from-html.py <html> <输出目录> --dry-run
```

参数：

| 参数 | 说明 |
|------|------|
| `--from-anchor ID` / `--to-anchor ID` | 按 `<h2 id="ID">` 切区间（起含、止不含）；省略则取整个文件 |
| `--bg COLOR` | 给每张图注入一个满幅底矩形，宽高取自该图自己的 `viewBox`；不给则保持透明 |
| `--label` | 在每张图底部注入一行居中的「图 N」，viewBox 高度 +34。⚠️ 底栏在**原 viewBox 之外**——各图底部留白从 6px 到 38px 不等，塞进留白会让留白小的图压到内容 |
| `--replace OLD=NEW` | 对抽出的 SVG 做字面替换，可重复。规则是**全局**的（一条规则可能只命中其中一张图），**某条规则全程 0 命中才报错** |
| `--prefix` / `--names` | 文件名前缀（默认 `fig`）与逐张短名（`fig01-<短名>.svg`） |
| `--expect N` | 断言图数；不符直接报错退出，防区间写错 |
| `--dry-run` | 只打印清单，不写盘 |

行为要点：

- 只在区间内找 `<figure>`，逐张抽其中的 `<svg>`——**区间切分才是定位手段**，不要拿 `viewBox` 去认图（同尺寸的图会认错）
- 处理顺序固定：**抽 SVG → `--replace` → `--bg` → `--label`**
- 输出统一 LF 行尾；已存在同名文件直接覆盖

> ⚠️ **为什么 `--bg` 往往是必需的**：`svg-to-png.mjs` 硬编码 `background: '#FFFFFF'`，而深色主题长文的图示文字**全是浅色**。不注入底色直接渲染，得到的是「浅字白底」——在掘金 / CSDN 这类浅色平台上**完全不可读**。注入与文档 `--bg-soft` 同色的底矩形，等于把深色图面板原样搬过去。

> ⚠️ **图内烧死的引用：用 `--replace` 修，不要手改文件**。有些图的 SVG 里印着章节号（如「与 3.1 的组件表一致」）——这类文字**改不了，只能改 SVG 源**。但要注意：**它在长文里可能本来就是对的**（§3.1 确实存在），只是发布稿重编号后失效。所以正确做法是把它作为 `--replace` 规则写进再生成命令，而不是手工改抽出的文件——**手改产物、不改源，重跑抽取就会复活死引用**（实测踩过：13 张里只有图 6 与现有文件不一致）。

### svg-to-png.mjs

配图约定为「**SVG 矢量源 + PNG 导出**」：`.svg` 供二次编辑，`.png` 供 Markdown 引用。改完 SVG 后跑一次即可重新生成全部 PNG。

倍率默认 **2×**（课程笔记够用）；**对外发布稿**（`articles/<类别>/<文章>/images`）用 **4×**

```bash
# 首次使用：先装依赖（装在 scripts/node_modules，已被 .gitignore 排除）
cd scripts && npm install --registry=https://registry.npmmirror.com && cd ..

# 渲染整个 assets 目录（自动跳过已是最新的 PNG）
node scripts/svg-to-png.mjs "docs/大模型与神经网络原理笔记/coding-agent/assets"

# 强制全部重渲染 / 指定单张 SVG / 改缩放倍率
node scripts/svg-to-png.mjs "docs/大模型与神经网络原理笔记/coding-agent/assets" --force
node scripts/svg-to-png.mjs assets/06_mcp_flow.svg --scale 2

# 对外发布稿：4×（2720px 宽）
node scripts/svg-to-png.mjs articles/agent-harness/agent-harness-from-analogy-to-12-components/images --scale 4 --force
```

行为要点：

- 递归查找目录下的 `*.svg`，在**同目录**生成同名 `.png`；文件名以 `_` 开头的 SVG 一律跳过（元文件 / 内部素材）
- 默认跳过「PNG 比 SVG 新」的文件，只重渲染改动过的图
- 已显式指定中文字体（微软雅黑 / 黑体等），避免中文渲染成方块

> 兜底方案：若 `@resvg/resvg-js` 装不上或字体加载异常，可改用浏览器 / Chromium 截图渲染；SVG 本身也可直接被 VSCode、Typora、GitHub 渲染，必要时可只交付 `.svg`。
