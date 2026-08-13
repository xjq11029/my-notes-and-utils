> 本文档为 `03-PWA与WebComponents.md` 的导览文件，提供快速索引和全局概览。
> 前置知识：Service Worker 概念、HTML/CSS/JS 基础

---

# 03-PWA与WebComponents - 导览

---

## 1.1 PWA 核心能力（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | PWA（Progressive Web App）的目标是"把网站变成 App"，通过 Service Worker、Web App Manifest、Push API 等 Web 标准技术，让普通网页获得离线访问、安装到桌面、推送通知、后台同步等原生应用体验 |
| 能做什么 | 离线访问（Service Worker + Cache API）、安装到桌面（Web App Manifest）、推送通知（Push API + Notification API）、后台同步（Background Sync API）、全屏体验（display: standalone） |
| 怎么用 | 提供 `manifest.json` 配置应用信息 → 注册 Service Worker 实现离线缓存 → 通过 HTTPS 提供服务 → 响应式设计适配移动端 → Lighthouse PWA 审计评分 > 90 |
| 原理和工作流程 | 用户首次访问 → 浏览器下载并安装 Service Worker → SW 预缓存关键资源 → 后续访问 SW 拦截请求并返回缓存 → 离线时仍可访问 → 浏览器检测到 manifest.json 后提示"添加到主屏幕" |
| 缺点 | iOS Safari 支持不完整（存储限制、后台同步不可用、推送通知需原生 App）；Service Worker 调试困难；缓存策略不当可能导致用户看到旧内容 |

---

## 1.2 Web Components 三件套（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | Web Components 是一套浏览器原生支持的组件化技术标准，由 Custom Elements（自定义 HTML 标签）、Shadow DOM（封装内部 DOM 和样式）、HTML Templates（声明式定义可复用 DOM 片段）三部分组成 |
| 能做什么 | 创建框架无关的可复用 UI 组件，在任何 HTML 页面、React、Vue、Angular 中使用，不需要任何运行时依赖 |
| 怎么用 | 定义模板：`<template id="tpl"><style>...</style><div>...</div></template>` → 定义类：`class MyElement extends HTMLElement { constructor() { this.attachShadow({ mode: 'open' }) } }` → 注册：`customElements.define('my-element', MyElement)` → 使用：`<my-element></my-element>` |
| 原理和工作流程 | 浏览器解析 HTML 遇到自定义标签 → 查找对应的 Custom Element 类 → 调用 constructor 创建 Shadow DOM → 将模板内容克隆到 Shadow DOM → 触发生命周期回调（connectedCallback、attributeChangedCallback）→ 组件渲染完成 |
| 缺点 | 相比 React/Vue 缺少响应式系统、路由、状态管理等基础设施；SEO 支持有限（Declarative Shadow DOM 正在改善）；浏览器兼容性仍有差距（Safari 对部分特性支持滞后） |

---

## 1.3 PWA 与跨端开发的关系（核心概念）

| 维度 | 内容 |
|---|---|
| 是什么 | PWA 提供跨平台能力（一套代码运行在 Web、Android、iOS、桌面），同时提供原生体验（离线、安装、推送），是跨端开发的一种低成本方案 |
| 能做什么 | 无需应用商店审核即可分发，降低用户获取成本；一套代码覆盖所有支持浏览器的平台；渐进式增强，不支持的浏览器降级为普通网站 |
| 怎么用 | 与 React Native、Flutter、uniapp 等方案根据项目需求选择：PWA 适合内容型应用、轻量工具；RN/Flutter 适合需要深度原生能力的应用 |
| 原理和工作流程 | PWA 基于 Web 标准，通过浏览器提供原生能力 → RN 通过 JS Bridge 调用原生组件 → Flutter 通过 Skia 引擎自绘 UI → 选择依据：开发成本、原生能力需求、分发渠道、团队技术栈 |
| 缺点 | 原生能力不如 RN/Flutter（蓝牙、NFC、文件系统等）；iOS 生态限制较多；无法上架应用商店（可通过 Trusted Web Activity 在 Google Play 发布） |

---

## 2.1 Service Worker 生命周期（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | Service Worker 的生命周期分为四个阶段：install（下载并预缓存关键资源）→ waiting（等待旧 SW 释放控制权）→ activate（激活并清理旧缓存）→ fetch（拦截并处理网络请求） |
| 能做什么 | 在 install 阶段预缓存应用外壳（App Shell）；在 activate 阶段清理旧版本缓存；在 fetch 阶段实现各种缓存策略 |
| 怎么用 | `self.addEventListener('install', event => event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(urls))))`；`self.addEventListener('activate', event => event.waitUntil(cleanOldCaches()))`；`self.addEventListener('fetch', event => event.respondWith(handleFetch(event.request)))` |
| 原理和工作流程 | 页面注册 SW → 浏览器下载 sw.js → 触发 install 事件 → 安装完成后进入 waiting 状态 → 旧 SW 控制的页面全部关闭后 → 触发 activate 事件 → SW 进入激活状态 → 开始拦截 fetch 事件 |
| 缺点 | 首次安装后才能生效，首次访问无离线能力；更新需要等旧 SW 释放；调试需要 Chrome DevTools Application 面板 |

---

## 2.2 缓存策略（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | 五种缓存策略：Cache First（先查缓存，未命中才请求网络）、Network First（先请求网络，失败后回退缓存）、Stale-While-Revalidate（立即返回缓存，同时后台更新）、Network Only（只请求网络）、Cache Only（只使用缓存） |
| 能做什么 | 根据资源类型和数据新鲜度要求选择最合适的缓存策略，平衡离线可用性和数据新鲜度 |
| 怎么用 | 静态资源（CSS/JS/图片）→ Cache First；API 数据 → Network First 或 Stale-While-Revalidate；实时交易 → Network Only；预缓存资源 → Cache Only |
| 原理和工作流程 | Cache First：`caches.match(request)` → 命中返回缓存，未命中 fetch → 缓存响应 → 返回；Network First：`fetch(request)` → 成功则缓存并返回，失败则 `caches.match(request)` → 返回缓存或离线页面 |
| 缺点 | Cache First 可能导致用户看到过期内容；Network First 在弱网下等待时间长；策略选择错误会导致用户体验差 |

---

## 2.3 Shadow DOM 隔离原理（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | Shadow DOM 提供样式隔离（内部 CSS 不会泄漏到外部，外部 CSS 不影响内部）和 DOM 隔离（内部节点不在主文档树中，`document.querySelector` 无法选中），通过 `attachShadow({ mode: 'open' | 'closed' })` 创建 |
| 能做什么 | 创建真正封装的组件，避免样式冲突和 DOM 污染；`mode: 'open'` 允许外部通过 `element.shadowRoot` 访问；`mode: 'closed'` 禁止外部访问 |
| 怎么用 | `this.attachShadow({ mode: 'open' })` 创建 Shadow Root → `shadowRoot.innerHTML = '<style>...</style><div>...</div>'` 填充内容 → 使用 `:host`/`::slotted()` 选择器控制样式 |
| 原理和工作流程 | 浏览器为自定义元素创建独立的 Shadow DOM 树 → 样式规则只作用于 Shadow DOM 内部 → 外部 CSS 选择器无法穿透 Shadow Boundary → 继承属性（color、font-size）仍会穿透 → 事件 target 被重定向为宿主元素 |
| 缺点 | SSR 需要 Declarative Shadow DOM 支持；Safari 对部分 Shadow DOM 特性支持滞后；事件重定向可能导致调试困难 |

---

## 2.4 Declarative Shadow DOM（底层原理）

| 维度 | 内容 |
|---|---|
| 是什么 | Declarative Shadow DOM 是 Shadow DOM 的声明式创建方式，在 HTML 中通过 `<template shadowrootmode="open">` 直接定义，不需要 JavaScript，浏览器解析后自动创建 Shadow DOM |
| 能做什么 | 让 Shadow DOM 支持 SSR（服务端渲染），服务端可以直接生成包含 Shadow DOM 的 HTML；对 SEO 和首屏渲染友好，不需要等待 JavaScript 加载 |
| 怎么用 | 在 HTML 中写：`<my-element><template shadowrootmode="open"><style>...</style><div>...</div></template></my-element>`；服务端直接渲染此 HTML |
| 原理和工作流程 | 服务端渲染 HTML 时包含 `<template shadowrootmode="open">` → 浏览器解析 HTML → 遇到 shadowrootmode 属性 → 自动创建 Shadow DOM 并附加到父元素 → 不需要 JavaScript 的 `attachShadow()` |
| 缺点 | 浏览器兼容性有限（Chrome/Edge 支持，Firefox/Safari 需要 polyfill）；不适用于需要动态更新 Shadow DOM 内容的场景 |

---

## 3.1 PWA 从零到一（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | 完整的 PWA 实现：manifest.json 配置（应用名称、图标、主题色、显示模式）+ Service Worker 注册和缓存策略 + 离线回退页面 + 安装提示处理 |
| 能做什么 | 让一个普通网站获得完整的 PWA 体验：离线访问、添加到主屏幕、自定义图标和启动画面 |
| 怎么用 | 创建 `manifest.json` 配置应用信息 → 创建 `sw.js` 实现 install/activate/fetch 生命周期 → 在 HTML 中 `<link rel="manifest">` 和注册 SW → 添加 `beforeinstallprompt` 事件处理 |
| 原理和工作流程 | 用户首次访问 → 浏览器下载 manifest.json 和 SW → SW 预缓存关键资源 → 浏览器检测到 PWA 条件满足 → 显示安装提示 → 用户点击安装 → 桌面生成图标 → 后续访问从桌面图标打开，使用 standalone 模式 |
| 缺点 | 需要在 HTTPS 下运行（localhost 除外）；manifest.json 和 SW 文件需要正确配置 MIME 类型；iOS 引导安装体验不如 Android |

---

## 3.2 使用 Workbox 简化 Service Worker 开发（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | Workbox 是 Google 提供的 Service Worker 工具库，封装了预缓存、运行时缓存、后台同步等常见模式，通过 Vite/Webpack 插件或手动配置使用 |
| 能做什么 | 简化 SW 开发：自动生成预缓存清单、声明式配置缓存策略、内置过期控制和条目限制、支持后台同步 |
| 怎么用 | Vite：`vite-plugin-pwa` 插件配置 `workbox.runtimeCaching`；Webpack：`workbox-webpack-plugin`；手动：`import { registerRoute } from 'workbox-routing'` |
| 原理和工作流程 | 构建时 Workbox 扫描构建产物生成预缓存清单 → 生成 SW 代码包含缓存策略 → 运行时 SW 根据配置的 urlPattern 和 handler 处理请求 → 自动管理缓存过期和条目限制 |
| 缺点 | 配置文件较复杂，学习曲线存在；版本更新时需要注意 SW 兼容性；某些高级场景仍需要手动编写 SW 代码 |

---

## 3.3 Web Components 实战（使用 Lit 3.0）（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | Lit 是 Google 开发的轻量级 Web Components 框架（~5KB），提供了响应式状态管理（@state/@property）、声明式模板（html 标签模板）、高效的 DOM 更新（仅更新变化部分） |
| 能做什么 | 快速创建具备响应式数据绑定、属性监听、事件派发、样式隔离的 Web Components，开发体验接近 React/Vue |
| 怎么用 | `pnpm add lit` → 定义类 `@customElement('my-button') class MyButton extends LitElement` → 声明属性 `@property()` → 渲染 `render() { return html\`...\` }` → 使用 `<my-button></my-button>` |
| 原理和工作流程 | LitElement 基于 Custom Elements + Shadow DOM → @property 属性变化触发重新渲染 → html 标签模板生成 DOM → Lit 的 diff 算法仅更新变化部分 → 自定义事件通过 dispatchEvent 派发 |
| 缺点 | 需要额外的构建步骤（装饰器转换）；相比 React/Vue 生态较小；模板语法与 JSX 差异较大 |

---

## 3.4 Web Components 在 React/Vue 中使用（实战应用）

| 维度 | 内容 |
|---|---|
| 是什么 | Web Components 是框架无关的，可以在 React 和 Vue 中直接使用，但需要注意属性传递和事件通信的差异 |
| 能做什么 | 在现有 React/Vue 项目中引入 Web Components，实现跨框架组件复用 |
| 怎么用 | React 18-：通过 ref + DOM API 设置属性，通过 addEventListener 监听事件；React 19：原生支持自定义元素属性；Vue：天然支持，属性绑定和事件监听与普通组件一致，需配置 `isCustomElement` |
| 原理和工作流程 | React 通过 JSX 渲染 `<custom-element>` → React 18 只能传递字符串属性 → 复杂数据通过 ref + setAttribute 设置 → 自定义事件通过 addEventListener 监听 → Vue 通过模板语法渲染 → 属性自动绑定 → 事件通过 @event-name 语法监听 |
| 缺点 | React 18 之前对 Web Components 支持不完善；复杂数据传递需要序列化/反序列化；事件命名约定不同（React 用 camelCase，Web Components 用 kebab-case） |

---

> [返回原文](./03-PWA与WebComponents.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)