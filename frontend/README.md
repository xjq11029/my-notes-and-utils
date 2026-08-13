# 前端学习路线 — 笔面试资料库

> **定位**：面向 Java 后端转全栈、前端进阶学习者的系统性笔面试学习资料，覆盖原理深度、实战应用和面试题库三大维度。
> **配套**：与 [后端资料库](../backend/README.md) 互补，形成完整的全栈笔面试知识体系。

---

## 学习路线总览

| 周次 | 模块 | 核心技术栈 | 资料目录 |
|:----:|------|-----------|----------|
| 1 | HTML/CSS | 语义化、盒模型、Flex/Grid、BFC、回流重绘、响应式 | [01-html-css](./01-html-css/) |
| 2 | JavaScript 核心 | 原型链、闭包、this、事件循环、Promise、ES6+、DOM、JSON、正则、BOM | [02-javascript-core](./02-javascript-core/) |
| 3 | TypeScript | 类型系统、泛型、高级类型、工具类型、装饰器 | [03-typescript](./03-typescript/) |
| 4 | 浏览器原理 | 渲染流程、V8 引擎、事件循环、跨域、Web 安全、网络协议 | [04-browser](./04-browser/) |
| 5 | Vue 3 | Composition API、Proxy 响应式、diff 优化、Pinia | [05-vue](./05-vue/) |
| 6 | React 18 | Hooks、Fiber 架构、虚拟 DOM Diff、状态管理 | [06-react](./06-react/) |
| 7 | 前端工程化 | Webpack、Vite、ESLint、CI/CD、Monorepo | [07-engineering](./07-engineering/) |
| 8 | 性能优化 | Core Web Vitals、懒加载、缓存策略、SSR/SSG | [08-performance](./08-performance/) |
| 9 | Node.js | Event Loop、Koa/Express、中间件、BFF、数据库、ORM | [09-nodejs](./09-nodejs/) |
| 综合 | 实战项目 | 企业后台管理系统（Vue 3 + Vite + Pinia + Element Plus） | [10-project](./10-project/) |
| 11 | AI 辅助开发 | Cursor/Claude Code/Copilot、Prompt 工程、AI 代码审查、AST 拦截 | [11-ai-assisted](./11-ai-assisted/) |
| 12 | 跨端开发 | uniapp 架构、条件编译、H5/小程序渲染差异、跨端性能优化、PWA、Web Components | [12-cross-platform](./12-cross-platform/) |
| 13 | 前端架构设计 | 微前端、设计系统、分层架构、ADR、技术债管理 | [13-architecture](./13-architecture/) |
| 14 | 前端监控与运维 | Sentry、自建SDK、灰度发布、Feature Flags、可观测性 | [14-monitoring](./14-monitoring/) |
| 15 | 前端测试策略 | Vitest、Testing Library、Playwright、E2E、视觉回归 | [15-testing](./15-testing/) |

---

## 使用指南

### 按学习阶段使用

- **第 1-2 周（基础期）**：先通读 HTML/CSS 和 JavaScript 核心的原理文件，再刷对应的笔面试题集
- **第 3-4 周（进阶期）**：TypeScript→浏览器原理，按顺序推进，学完即刷题
- **第 5-6 周（框架期）**：Vue 3 和 React 18 可并行学习，选一个深入，另一个了解
- **第 7-8 周（工程化期）**：工程化→性能优化，结合实战项目串联知识点
- **第 9-10 周（拓展期）**：Node.js + 综合实战，打通前后端
- **进阶拓展**：AI 辅助开发（11-ai-assisted）和跨端开发（12-cross-platform）作为拓展模块，可在完成主线后按需学习
- **第 13-15 周（架构师期）**：前端架构设计（13-architecture）→ 前端监控与运维（14-monitoring）→ 前端测试策略（15-testing），构建架构师级别的系统思维
- **调试参考**：遇到未知 Bug 时查阅 [万能通用Bug定位查找逻辑](./万能通用Bug定位查找逻辑.md)，包含系统化调试方法论和常见场景排查手册
- **快速查阅**：使用 [知识导览](./知识导览.md) 五维表格快速回顾各知识点的"是什么/能做什么/怎么用/原理/缺点"

### 文件结构说明

每个模块目录包含两类文件：

- **原理文件**（`01-xxx.md`、`02-xxx.md`）：深入讲解核心概念、底层原理、实战应用，附常见面试题和避坑指南
- **笔面试题集**（`0X-xxx笔面试题集.md`）：选择题 + 简答题 + 编程/场景设计题，全部附完整解析，难度标注 ★/★★/★★★

### 相关知识库

本资料库与项目中的以下资料互补：

- [后端笔面试资料库](../backend/README.md) — Java 后端全栈学习资料（涵盖 Java 基础、JavaWeb 单体、分布式微服务三大阶段）
- [深度复习手册](../ljit-exam-deep-dive.md) — 计算机网络、操作系统等综合深度
- [计算机基础综合](../ljit-exam-foundation.md) — 计算机组成原理与信息安全

---

## 文件索引

### 01-html-css — HTML5 + CSS3（第 1 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-HTML核心与语义化.md](./01-html-css/01-HTML核心与语义化.md) | HTML5 新特性、语义化标签、SEO、meta 标签、元素分类 | 原理 |
| [02-CSS布局核心.md](./01-html-css/02-CSS布局核心.md) | 盒模型、BFC、Flex 布局、Grid 布局、居中方案 | 原理 |
| [03-CSS进阶与性能.md](./01-html-css/03-CSS进阶与性能.md) | CSS3 动画/变量、响应式设计、回流重绘、CSS 性能优化 | 原理 |
| [04-HTMLCSS笔面试题集.md](./01-html-css/04-HTMLCSS笔面试题集.md) | 选择题 15 + 简答 10 + 场景设计 5 | 题库 |

### 02-javascript-core — JavaScript 核心（第 2 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-语法基础与执行机制.md](./02-javascript-core/01-语法基础与执行机制.md) | 变量声明、作用域链、执行上下文、原型链、this 绑定 | 原理 |
| [02-异步编程与ES6+特性.md](./02-javascript-core/02-异步编程与ES6+特性.md) | 回调/Promise/async-await、事件循环、宏微任务、模块化 | 原理 |
| [03-常用API与手写原理.md](./02-javascript-core/03-常用API与手写原理.md) | 闭包、防抖节流、深浅拷贝、柯里化、继承、垃圾回收、EventEmitter、函数式编程 | 原理 |
| [04-JavaScript核心笔面试题集.md](./02-javascript-core/04-JavaScript核心笔面试题集.md) | 选择题 20 + 简答 15 + 编程题 10 | 题库 |
| [05-DOM操作与事件机制.md](./02-javascript-core/05-DOM操作与事件机制.md) | DOM 树、节点增删改查、事件流、事件委托、MutationObserver、IntersectionObserver | 原理 |
| [06-JSON与网络请求.md](./02-javascript-core/06-JSON与网络请求.md) | JSON.parse/stringify、AJAX、Fetch API、Axios 拦截器、请求取消 | 原理 |
| [07-正则表达式.md](./02-javascript-core/07-正则表达式.md) | 元字符、量词、标志、前瞻后顾、常用正则、性能优化 | 原理 |
| [08-BOM与浏览器扩展API.md](./02-javascript-core/08-BOM与浏览器扩展API.md) | window、location、history、navigator、Geolocation、Clipboard | 原理 |

### 03-typescript — TypeScript（第 3 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-TypeScript基础与类型系统.md](./03-typescript/01-TypeScript基础与类型系统.md) | 基础类型、联合交叉、接口 vs 类型别名、泛型基础 | 原理 |
| [02-高级类型与工程配置.md](./03-typescript/02-高级类型与工程配置.md) | 条件类型、映射类型、infer、工具类型、装饰器、tsconfig | 原理 |
| [03-TypeScript笔面试题集.md](./03-typescript/03-TypeScript笔面试题集.md) | 选择题 15 + 简答 8 + 类型体操 5 | 题库 |

### 04-browser — 浏览器原理（第 4 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-浏览器渲染与V8原理.md](./04-browser/01-浏览器渲染与V8原理.md) | 多进程架构、完整渲染流程、V8 垃圾回收 | 原理 |
| [02-事件循环与Web安全.md](./04-browser/02-事件循环与Web安全.md) | 事件循环、跨域方案、XSS/CSRF 防御、存储机制对比、WebSocket | 原理 |
| [03-浏览器笔面试题集.md](./04-browser/03-浏览器笔面试题集.md) | 选择题 15 + 简答 10 + 场景设计 3 | 题库 |
| [04-网络协议基础.md](./04-browser/04-网络协议基础.md) | OSI/TCP-IP 模型、DNS 解析、TCP 握手、HTTP/1.1 vs 2 vs 3、RESTful API | 原理 |
| [05-前端安全深度.md](./04-browser/05-前端安全深度.md) | CSP 策略设计、依赖安全扫描、安全头配置、Trusted Types、SRI | 原理 |

### 05-vue — Vue 3 生态（第 5 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Vue3核心语法.md](./05-vue/01-Vue3核心语法.md) | Composition API、ref/reactive、computed/watch、生命周期 | 原理 |
| [02-响应式与编译优化.md](./05-vue/02-响应式与编译优化.md) | Proxy vs defineProperty、虚拟 DOM、diff 算法优化 | 原理 |
| [03-路由与状态管理.md](./05-vue/03-路由与状态管理.md) | Vue Router 路由模式、路由守卫、Pinia vs Vuex | 原理 |
| [04-Vue3笔面试题集.md](./05-vue/04-Vue3笔面试题集.md) | 选择题 15 + 简答 10 + 场景设计 5 | 题库 |

### 06-react — React 18 生态（第 6 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-React核心与Hooks.md](./06-react/01-React核心与Hooks.md) | JSX、虚拟 DOM、Fiber 架构、Hooks 原理 | 原理 |
| [02-Diff算法与性能优化.md](./06-react/02-Diff算法与性能优化.md) | Diff 策略、同级比较、key 的作用、memo/useMemo/useCallback | 原理 |
| [03-路由与状态管理.md](./06-react/03-路由与状态管理.md) | React Router 原理、Redux vs Redux Toolkit vs Zustand | 原理 |
| [04-React笔面试题集.md](./06-react/04-React笔面试题集.md) | 选择题 15 + 简答 10 + 编程 3 + 场景设计 2 | 题库 |

### 07-engineering — 前端工程化（第 7 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-构建工具原理.md](./07-engineering/01-构建工具原理.md) | Webpack 原理、Vite 原理、打包流程、热更新 | 原理 |
| [02-工程规范与流程.md](./07-engineering/02-工程规范与流程.md) | ESLint/Prettier/Husky、Git 流程、CI/CD、Monorepo | 原理 |
| [03-前端工程化笔面试题集.md](./07-engineering/03-前端工程化笔面试题集.md) | 选择题 10 + 简答 8 + 场景设计 5 | 题库 |
| [04-测试集成与质量门禁.md](./07-engineering/04-测试集成与质量门禁.md) | 测试门禁体系、Husky+lintstaged、CI 流水线设计、覆盖率门禁、Bundle 体积监控 | 原理 |

### 08-performance — 前端性能优化（第 8 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-加载性能优化.md](./08-performance/01-加载性能优化.md) | Core Web Vitals、Tree Shaking、代码分割、懒加载、缓存策略、CDN | 原理 |
| [02-运行时优化.md](./08-performance/02-运行时优化.md) | 防抖节流、回流重绘优化、虚拟列表、内存泄漏、SSR/SSG/ISR | 原理 |
| [03-性能优化笔面试题集.md](./08-performance/03-性能优化笔面试题集.md) | 选择题 10 + 简答 8 + 场景分析 5 | 题库 |
| [04-渲染架构深度.md](./08-performance/04-渲染架构深度.md) | SSG/ISR/SSR/CSR 渲染策略、RSC、PPR、Streaming SSR、Edge Runtime | 原理 |

### 09-nodejs — Node.js（第 9 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Node运行时与核心API.md](./09-nodejs/01-Node运行时与核心API.md) | V8 + libuv 架构、Event Loop 阶段、模块机制、stream/Buffer | 原理 |
| [02-Web框架与BFF层.md](./09-nodejs/02-Web框架与BFF层.md) | Express vs Koa、洋葱模型、Session/Cookie、JWT、BFF 设计、API 文档、SSE | 原理 |
| [03-Node.js笔面试题集.md](./09-nodejs/03-Node.js笔面试题集.md) | 选择题 10 + 简答 8 + 编程题 3 | 题库 |
| [04-数据库与ORM.md](./09-nodejs/04-数据库与ORM.md) | MySQL/PostgreSQL、SQL JOIN/ACID、MongoDB、Redis、Prisma/TypeORM | 原理 |

### 10-project — 综合实战

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-企业后台管理系统实战.md](./10-project/01-企业后台管理系统实战.md) | 需求分析、技术选型、RBAC 权限、路由守卫、组件封装、打包部署 | 实战 |
| [02-电商平台实战.md](./10-project/02-电商平台实战.md) | 电商全栈项目：商品管理、订单系统、购物车、支付集成、Redis 缓存、Docker 部署 | 实战 |
| [03-项目实战笔面试题集.md](./10-project/03-项目实战笔面试题集.md) | 选择题 10 + 简答 8 + 场景设计 5 | 题库 |

### 11-ai-assisted — AI 辅助前端开发（拓展）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-AI编程工具与工作流.md](./11-ai-assisted/01-AI编程工具与工作流.md) | Cursor、Claude Code、GitHub Copilot 工具选型与工作流 | 原理 |
| [02-Prompt工程与代码生成.md](./11-ai-assisted/02-Prompt工程与代码生成.md) | Prompt 工程五要素、前端专用模板、复杂表单策略、防幻觉技巧 | 原理 |
| [03-AI代码审查与质量管控.md](./11-ai-assisted/03-AI代码审查与质量管控.md) | 三级审查模型、竞态检测、AST 拦截、防调试识别、CI/CD 集成 | 原理 |
| [04-AI辅助开发笔面试题集.md](./11-ai-assisted/04-AI辅助开发笔面试题集.md) | 选择题 10 + 简答 8 + 场景设计 5 | 题库 |

### 12-cross-platform — 跨端开发（拓展）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-uniapp跨端开发基础.md](./12-cross-platform/01-uniapp跨端开发基础.md) | uniapp 架构、条件编译、生命周期、组件与 API 体系 | 原理 |
| [02-uniapp渲染差异与性能优化.md](./12-cross-platform/02-uniapp渲染差异与性能优化.md) | H5/小程序渲染差异、排查路径、首屏优化、分包策略 | 原理 |
| [03-PWA与WebComponents.md](./12-cross-platform/03-PWA与WebComponents.md) | PWA 离线缓存、Service Worker 生命周期、Web Components 三件套、Lit 框架 | 原理 |
| [04-跨端开发笔面试题集.md](./12-cross-platform/04-跨端开发笔面试题集.md) | 选择题 10 + 简答 8 + 场景设计 5 | 题库 |

### 13-architecture — 前端架构设计（第 13 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-微前端架构.md](./13-architecture/01-微前端架构.md) | qiankun/Module Federation/wujie/micro-app 对比、沙箱隔离、应用通信、选型决策 | 原理 |
| [02-设计系统与组件库架构.md](./13-architecture/02-设计系统与组件库架构.md) | Design Tokens 三层体系、组件库架构、主题切换、零运行时 CSS 方案 | 原理 |
| [03-前端分层架构与技术管理.md](./13-architecture/03-前端分层架构与技术管理.md) | 分层架构模式、ADR 架构决策记录、技术债管理、技术选型框架 | 原理 |
| [04-前端架构设计笔面试题集.md](./13-architecture/04-前端架构设计笔面试题集.md) | 选择题 10 + 简答 8 + 场景设计 5 | 题库 |

### 14-monitoring — 前端监控与运维（第 14 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-前端监控体系.md](./14-monitoring/01-前端监控体系.md) | Sentry、自建 SDK、错误/性能/业务监控、Sourcemap 还原 | 原理 |
| [02-灰度发布与部署策略.md](./14-monitoring/02-灰度发布与部署策略.md) | Feature Flags 四类模型、灰度/金丝雀/蓝绿部署、容器化部署 | 原理 |
| [03-可观测性与故障排查.md](./14-monitoring/03-可观测性与故障排查.md) | Logs/Metrics/Traces 三支柱、链路追踪、告警策略、故障排查流程 | 原理 |
| [04-前端监控与运维笔面试题集.md](./14-monitoring/04-前端监控与运维笔面试题集.md) | 选择题 10 + 简答 8 + 场景设计 5 | 题库 |

### 15-testing — 前端测试策略（第 15 周）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-测试金字塔与单元测试.md](./15-testing/01-测试金字塔与单元测试.md) | 测试金字塔、Vitest 基础、Mock 策略、覆盖率 | 原理 |
| [02-组件测试与集成测试.md](./15-testing/02-组件测试与集成测试.md) | Testing Library、组件交互测试、集成测试、MSW | 原理 |
| [03-E2E测试与视觉回归.md](./15-testing/03-E2E测试与视觉回归.md) | Playwright/Cypress、E2E 场景设计、视觉回归测试 | 原理 |
| [04-前端测试笔面试题集.md](./15-testing/04-前端测试笔面试题集.md) | 选择题 10 + 简答 8 + 场景设计 5 | 题库 |

### 通用工具

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [万能通用Bug定位查找逻辑.md](./万能通用Bug定位查找逻辑.md) | 调试五步法、错误分类体系、六种调试方法、Chrome DevTools 指南、常见场景排查手册 | 工具 |

---

## 学习建议

> 如果你已经学习了 [后端资料库](../backend/README.md)，再学前端可以走"对比迁移"的快速路径。核心是 **复用已学知识，只学前端独有的东西**。

- **对比学习**：每学一个前端概念，问自己"这个在后端怎么实现？"（如事件循环在浏览器和 Node.js 中的区别）
- **项目驱动**：以"企业后台管理系统"为主线，学一个模块就集成一个模块
- **避坑指南**：不要一次性学完所有 CSS 属性、不要死记硬背所有 Hooks API、不要试图同时精通 Vue 和 React
- **交叉引用**：HTTP 协议、CORS 跨域、JWT 认证、CSRF/XSS 等主题已在后端资料中详细讲解，前端只补充前端视角，不重复