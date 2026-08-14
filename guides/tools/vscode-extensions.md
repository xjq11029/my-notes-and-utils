# VS Code 扩展列表

本文件记录了当前项目使用的 VS Code 扩展，方便在新环境中快速安装。

## 快速安装命令

```bash
# 一键安装所有扩展
code --install-extension aooiu.z-reader
code --install-extension aykutsarac.jsoncrack-vscode
code --install-extension dbaeumer.vscode-eslint
code --install-extension eamodio.gitlens
code --install-extension ecmel.vscode-html-css
code --install-extension editorconfig.editorconfig
code --install-extension equimper.react-native-react-redux
code --install-extension esbenp.prettier-vscode
code --install-extension formulahendry.auto-close-tag
code --install-extension glenn2223.live-sass
code --install-extension hollowtree.vue-snippets
code --install-extension ionutvmi.path-autocomplete
code --install-extension jacano.vscode-pnpm
code --install-extension marscode.marscode-extension
code --install-extension mikestead.dotenv
code --install-extension ms-ceintl.vscode-language-pack-zh-hans
code --install-extension ms-python.debugpy
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.vscode-python-envs
code --install-extension pucelle.vscode-css-navigation
code --install-extension rainbroadcast.shadow-reader
code --install-extension ritwickdey.liveserver
code --install-extension shd101wyy.markdown-preview-enhanced
code --install-extension streetsidesoftware.code-spell-checker
code --install-extension stylelint.vscode-stylelint
code --install-extension syler.sass-indented
code --install-extension usernamehw.errorlens
code --install-extension vscode-icons-team.vscode-icons
code --install-extension vue.volar
code --install-extension wejectchan.vue3-snippets-for-vscode
code --install-extension wscats.cors-browser
code --install-extension xabikos.javascriptsnippets
```

## 扩展详情

### AI 编程助手

| 扩展 ID | 名称 | 功能描述 |
|---------|------|----------|
| `marscode.marscode-extension` | 豆包 MarsCode | 字节跳动旗下的免费 AI 编程工具，提供代码补全、生成、编辑、解释、单测生成、问题修复、技术问答等功能 |

### 代码质量与格式化

| 扩展 ID | 名称 | 功能描述 |
|---------|------|----------|
| `dbaeumer.vscode-eslint` | ESLint | JavaScript/TypeScript 代码检查和格式化 |
| `esbenp.prettier-vscode` | Prettier | 代码格式化工具 |
| `stylelint.vscode-stylelint` | Stylelint | CSS/SCSS/Less 样式检查 |
| `editorconfig.editorconfig` | EditorConfig | 统一代码风格配置 |
| `usernamehw.errorlens` | Error Lens | 在代码行内直接显示错误和警告 |
| `streetsidesoftware.code-spell-checker` | Code Spell Checker | 代码拼写检查 |

### Vue 开发

| 扩展 ID | 名称 | 功能描述 |
|---------|------|----------|
| `vue.volar` | Vue - Official | Vue 3 官方语言支持（替代 Vetur） |
| `hollowtree.vue-snippets` | Vue Snippets | Vue 代码片段 |
| `wejectchan.vue3-snippets-for-vscode` | Vue3 Snippets | Vue 3 代码片段 |

### Python 开发

| 扩展 ID | 名称 | 功能描述 |
|---------|------|----------|
| `ms-python.python` | Python | Python 语言支持 |
| `ms-python.vscode-pylance` | Pylance | Python 语言服务器 |
| `ms-python.debugpy` | Python Debugger | Python 调试器 |
| `ms-python.vscode-python-envs` | Python Environments | Python 环境管理 |

### CSS/SCSS/Sass

| 扩展 ID | 名称 | 功能描述 |
|---------|------|----------|
| `glenn2223.live-sass` | Live Sass Compiler | 实时编译 Sass/SCSS |
| `syler.sass-indented` | Sass | Sass 语法支持 |
| `pucelle.vscode-css-navigation` | CSS Navigation | CSS 类名导航和补全 |
| `ecmel.vscode-html-css` | HTML CSS Support | HTML 中 CSS 类名补全 |

### HTML/JavaScript

| 扩展 ID | 名称 | 功能描述 |
|---------|------|----------|
| `formulahendry.auto-close-tag` | Auto Close Tag | 自动闭合 HTML 标签 |
| `xabikos.javascriptsnippets` | JavaScript Snippets | JavaScript 代码片段 |
| `equimper.react-native-react-redux` | React Native/React/Redux Snippets | React 相关代码片段 |

### 工具与效率

| 扩展 ID | 名称 | 功能描述 |
|---------|------|----------|
| `eamodio.gitlens` | GitLens | 增强 Git 功能，显示代码作者、历史等 |
| `ionutvmi.path-autocomplete` | Path Autocomplete | 文件路径自动补全 |
| `mikestead.dotenv` | DotENV | .env 文件语法高亮 |
| `jacano.vscode-pnpm` | pnpm | pnpm 包管理器支持 |
| `ritwickdey.liveserver` | Live Server | 本地开发服务器 |
| `wscats.cors-browser` | CORS Browser | CORS 跨域测试工具 |
| `vscode-icons-team.vscode-icons` | vscode-icons | 文件图标美化 |
| `ms-ceintl.vscode-language-pack-zh-hans` | Chinese (Simplified) | 简体中文语言包 |

### Markdown

| 扩展 ID | 名称 | 功能描述 |
|---------|------|----------|
| `shd101wyy.markdown-preview-enhanced` | Markdown Preview Enhanced | 增强型 Markdown 预览 |

### 阅读与休闲

| 扩展 ID | 名称 | 功能描述 |
|---------|------|----------|
| `aooiu.z-reader` | Z-Reader | 在 VS Code 中阅读小说 |
| `rainbroadcast.shadow-reader` | Shadow Reader | 阅读器扩展 |

### 数据可视化

| 扩展 ID | 名称 | 功能描述 |
|---------|------|----------|
| `aykutsarac.jsoncrack-vscode` | JSON Crack | 将 JSON 数据可视化为交互式图表，支持 JSON、YAML、XML、CSV 等格式 |

## 导出扩展列表命令

```bash
# 导出已安装的扩展列表
code --list-extensions > extensions.txt

# 生成安装命令（PowerShell）
code --list-extensions | ForEach-Object { "code --install-extension $_" }
```

## 安装说明

1. **方式一：命令行安装**
   复制上面的安装命令，在终端中执行即可。

2. **方式二：VS Code 界面安装**
   - 打开 VS Code
   - 按 `Ctrl+Shift+X` 打开扩展面板
   - 搜索扩展名称或 ID
   - 点击安装

3. **方式三：批量安装脚本**
   创建一个 `.sh` 或 `.ps1` 脚本文件，将安装命令写入后执行。
