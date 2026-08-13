# src/js — JavaScript/Node.js 通用工具

从多个后端项目中抽取的、与具体业务解耦的通用工具模块。均为纯函数/类，不依赖任何项目级配置或数据。

| 模块 | 用途 | 第三方依赖（按需安装） |
|------|------|------------------------|
| `errors.js` | 通用自定义错误类层次（ServiceError 基类 + Upload/Unauthorized/Forbidden/Validation/NotFound/Unknown 子类），统一携带业务码 `code` | 无 |
| `query-helper.js` | Sequelize 通用查询工具：分页 `paginate` + 条件构造 `buildWhere`（支持模糊搜索、时间范围） | `sequelize` |
| `http-tool.js` | HTTP 通用工具：统一响应 `formatResponse/success`、JWT 解析 `analysisToken`、可配置上传器 `createUploader`、Markdown TOC 树生成 `handleTOC` | `jsonwebtoken`、`md5`、`multer`、`markdown-toc` |

## 使用约定

- **密钥绝不硬编码**：`analysisToken` 的 JWT 密钥从 `process.env.JWT_SECRET` 读取；上传目录通过 `createUploader({ dest })` 或 `process.env.UPLOAD_DIR` 注入。
- **按需引入**：各模块在文件顶层 `require` 其依赖，若未安装对应 npm 包则该模块 `require` 时报错——请按上表提前安装所需依赖，或仅引入无依赖的 `errors.js`。
- 这些模块是「可复用代码片段」集合，非一个打包发布的 npm 包；直接复制到你的工程 `utils/` 目录即可使用。
