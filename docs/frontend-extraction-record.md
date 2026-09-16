# Front-end 抽取封装记录

- **扫描来源**：`D:\Front-end`（含 Geeker-Admin、cesium-*、electron-desktop-tool、employment-platform-mis、example-mini、icegl-three-vue-tres、platform-mis、robot-dog-mis、scheduling-mini、serial-mis、sse、tools、vue-cesium-airline、web_robot-master 等 16 个项目目录）
- **扫描时间**：2026-08-13
- **操作范围**：仅抽取 / 封装，**未提交、未推送**
- **脱敏原则**：排除一切项目特定业务逻辑、硬编码接口地址、路径、凭据、协议/串口代码与含项目背景的文档；仅保留与业务无关的通用能力。

---

## 一、抽取的文档资料（已复制到仓库）

| 源文件 | 目标位置 | 判定理由 |
| --- | --- | --- |
| `tools/如何更好使用AI编程助手.md` | `guides/learning/如何更好使用AI编程助手.md` | 通用方法论，无项目敏感信息 |
| `tools/vscode-extensions.md` | `guides/tools/vscode-extensions.md` | 仅 VS Code 扩展安装清单，通用开发环境参考 |

### 已排除的文档（含项目背景，不抽取）
- `tools/AI对话示例.md`：基于 `serial-mis` 串口项目的对话示例，含项目技术栈与具体提问上下文，属项目资料。
- `tools/README.md` / `README.en.md`：Gitee 仓库模板占位说明，无实质内容。
- `tools/extensions.txt`：为 `vscode-extensions.md` 的子集，冗余。
- 各业务项目内的 `产品说明文档.md`、`接口文件*.md`、`*.docx`、`*.xlsx`、串口/协议文档等：均为项目专属，排除。

---

## 二、抽取封装的工具方法代码（已封装到 `src/utils/`）

所有源码源自各项目高度重复的 `src/utils/`，为同一套 Admin 模板派生，已统一清洗：

| 目标文件 | 源文件（代表性） | 封装/脱敏处理 |
| --- | --- | --- |
| `src/utils/is.ts` | Geeker-Admin `src/utils/is/index.ts` | 纯函数，原样复用，零依赖 |
| `src/utils/color.ts` | Geeker-Admin `src/utils/color.ts` | 去除 `element-plus` 的 `ElMessage` 依赖，非法输入改为抛 `Error` |
| `src/utils/validate.ts` | Geeker-Admin `eleValidate.ts` + web_robot `form-validation.js` | 由 Element 的 `(rule,value,callback)` 回调改写为返回 `boolean` 的纯函数；合并手机/邮箱/金额/QQ/统一社会信用代码/网址/身份证校验 |
| `src/utils/datetime.ts` | example-mini `tools.ts` + robot-dog-mis `help.ts` | 合并去重 `formatDate`/`formatDateTime`/`getWeek`/相对日期/随机整数，零依赖 |
| `src/utils/download.ts` | robot-dog-mis `help.ts` | 去除业务 `apiFunction` 与 UI 耦合，改为接收 `Blob`/`Response` 的通用下载 |
| `src/utils/eventBus.ts` | 各项目 `mittBus.ts` | 用零依赖实现替代 `mitt` 一行封装，API 保持一致 |
| `src/utils/docx-export.js` | robot-dog-mis `docxtemplater/exportDocx.js` | **删除** `uploadFile`（含 `http://localhost:8080` 硬编码后端地址）；`ElMessage` 改为 `console.error`；注明三方依赖 |

### 已排除的代码（项目特定，不抽取）
- `cesium-test` / `cesium-vue3-vite` / `vue-cesium-airline` 的 `cesium*` 三维地图控制代码：与 Cesium 强绑定。
- `serial-mis` 的 `serial.ts`、`parseSerialData.ts`、`protocol/*`、`chart/Buffer.ts`：串口协议/硬件解析，项目专属。
- `web_robot-master` 的 `services.js`、`cache.js`（硬编码 `token` 键）、`i18n.ts`：业务接口/存储/国际化。
- `robot-dog-mis` 的 `help.ts` 中 `getParam` / `isValidTeachingSchedule` / `getKeyFromKeys`（Proxy 随机 AK）：业务/密钥相关。
- `electron-desktop-tool` 的 `tool.ts`：依赖 Electron `ipcRenderer` 桌面录屏，环境特定。
- `dict.ts`（`genderType`/`userStatus` 等枚举）：虽通用但属 UI 字典，价值有限，未单独抽取。

---

## 三、仓库变更清单（待用户确认后再提交）

新增文件：
```
guides/learning/如何更好使用AI编程助手.md
guides/tools/vscode-extensions.md
src/utils/is.ts
src/utils/color.ts
src/utils/validate.ts
src/utils/datetime.ts
src/utils/download.ts
src/utils/eventBus.ts
src/utils/docx-export.js
src/utils/README.md
docs/frontend-extraction-record.md
```

> 当前均未纳入版本控制（未 `git add` / `commit` / `push`），请审阅后再决定是否提交。
