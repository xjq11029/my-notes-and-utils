# 通用工具函数（src）

从多个项目中抽取的、与具体业务解耦的通用工具，均为纯函数 / 类，可直接复制到目标工程使用。

## 子目录索引

| 子目录 | 定位 | 规模 | 第三方依赖 | 入口 |
|--------|------|------|-----------|------|
| [`js/`](js/) | JavaScript / Node.js 通用工具：错误类层次、Sequelize 分页查询、统一响应 / JWT / 上传器 / Markdown TOC | 5 个文件 | 按需 `require`：`sequelize` / `jsonwebtoken` / `md5` / `multer` / `markdown-toc` | [README](js/README.md) |
| [`python/`](python/) | Python 通用工具：目录创建、时间戳、JSON 读写、重试装饰器 | 2 个文件 | 无（仅标准库） | [README](python/README.md) |

## 使用约定

- **按需引入**：JS 各模块在文件顶层 `require` 其依赖，未安装对应 npm 包则引入即报错。无依赖、可放心直接引入的是 `js/utils.js`、`js/errors.js` 与 `python/utils.py`。
- **密钥绝不硬编码**：JWT 密钥从 `process.env.JWT_SECRET` 读取；上传目录通过 `createUploader({ dest })` 或 `process.env.UPLOAD_DIR` 注入。
- 这是「可复用代码片段」集合，**不是**发布到 npm / PyPI 的包 —— 直接复制到目标工程的工具目录即可。
- 用法示例见 [`examples/`](../examples/README.md)。

> 各子目录的 `README.md` 必须真实反映该目录实际情况；本目录随文件增减同步更新。
