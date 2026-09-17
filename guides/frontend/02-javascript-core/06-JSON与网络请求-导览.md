# 06-JSON与网络请求 导览

> 定位：五维框架浓缩提炼 06-JSON与网络请求.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./06-JSON与网络请求.md)。
> 前置知识：异步编程基础、Promise、ES6 语法

---

## 一、JSON 格式规范

### 1.1 JSON 基础规则

| 维度 | 内容 |
|------|------|
| 是什么 | JSON（JavaScript Object Notation）是一种轻量级的、语言无关的数据交换格式，是前后端数据通信的事实标准。它是 JavaScript 对象字面量语法的**严格子集**。 |
| 能做什么 | 前后端数据交换、配置文件存储、API 响应格式、跨语言数据序列化。支持 6 种数据类型：`string`、`number`、`boolean`、`null`、`object`、`array`。 |
| 怎么用 | 键名必须用双引号包裹；字符串值必须用双引号；不支持注释；不支持尾随逗号；不支持 `undefined`、`Function`、`Symbol`、`NaN`、`Infinity`。验证合法性：`try { JSON.parse(str); } catch { return false; }` |
| 原理和工作流程 | JSON 解析分为词法分析（逐字符扫描识别 token）、语法分析（构建 AST）、验证（检查键引号、值类型、结构完整性）三个阶段。任何阶段失败均抛出 `SyntaxError`。 |
| 缺点 | 不支持注释导致配置文件可读性差；不支持 `undefined` 和函数，需要手动转换；不支持 Date 原生类型，反序列化后是字符串；不支持尾随逗号，手动拼接 JSON 时容易出错。 |

### 1.2 JSON 与 JavaScript 对象对比

| 维度 | 内容 |
|------|------|
| 是什么 | JSON 是数据交换格式（字符串），JavaScript 对象是编程语言中的数据结构（内存中的对象）。两者语法相似但规范不同。 |
| 能做什么 | JSON 用于跨语言/跨平台数据交换；JavaScript 对象用于程序内部数据组织和逻辑处理。 |
| 怎么用 | 键名：JSON 必须双引号，JS 对象可省略引号；值类型：JSON 仅 6 种，JS 对象支持所有类型；JSON 不支持函数、undefined、Date、注释、尾随逗号。 |
| 原理和工作流程 | JSON 字符串需通过 `JSON.parse()` 解析为 JS 对象才能操作；JS 对象需通过 `JSON.stringify()` 序列化为 JSON 字符串才能传输。两者通过这两个方法实现双向转换。 |
| 缺点 | 混淆 JSON 字符串和 JS 对象是常见错误——直接对 JSON 字符串使用点语法访问属性会得到 `undefined`。 |

---

## 二、JSON.parse() 与 JSON.stringify()

### 2.1 JSON.parse() 核心用法

| 维度 | 内容 |
|------|------|
| 是什么 | `JSON.parse(text[, reviver])` 将合法的 JSON 字符串解析为 JavaScript 对象。`reviver` 是可选转换函数，在解析过程中对每个键值对进行转换。 |
| 能做什么 | 将 API 返回的 JSON 字符串转为可操作的 JS 对象；通过 `reviver` 参数在解析时自动转换日期字符串、过滤敏感字段、进行数据格式化。 |
| 怎么用 | `JSON.parse('{"name":"Alice"}')` -> `{name: "Alice"}`；`JSON.parse(str, (key, value) => key === 'date' ? new Date(value) : value)` |
| 原理和工作流程 | `reviver` 按**从内到外**的顺序遍历解析树：先处理叶子节点（如 `"name"` -> `"Alice"`），最后处理根对象（`""` -> 整个对象）。如果 `reviver` 返回 `undefined`，该属性会被删除。 |
| 缺点 | 传入非法 JSON 字符串会抛出 `SyntaxError`，必须用 `try-catch` 包裹；`reviver` 遍历顺序（从内到外）与直觉相反，容易导致逻辑错误。 |

### 2.2 JSON.stringify() 核心用法

| 维度 | 内容 |
|------|------|
| 是什么 | `JSON.stringify(value[, replacer[, space]])` 将 JavaScript 值序列化为 JSON 字符串。`replacer` 可以是数组（白名单）或函数（自定义过滤），`space` 控制输出缩进。 |
| 能做什么 | 将 JS 对象转为 JSON 字符串用于网络传输；通过 `replacer` 数组实现字段白名单；通过 `replacer` 函数过滤敏感字段（如密码）；通过 `space` 参数美化输出。 |
| 怎么用 | 基础：`JSON.stringify({a:1})` -> `'{"a":1}'`；白名单：`JSON.stringify(obj, ['name','email'])`；过滤：`JSON.stringify(obj, (k,v) => k==='pwd' ? undefined : v)`；美化：`JSON.stringify(obj, null, 2)` |
| 原理和工作流程 | 序列化时遍历对象属性，对每个属性调用 `replacer`（如果提供）。`replacer` 为函数时，`this` 指向当前属性的父对象。返回 `undefined` 的属性会被丢弃。`space` 为数字时表示缩进空格数（0-10），为字符串时取前 10 个字符作为缩进符。 |
| 缺点 | 对 `undefined`、函数、`Symbol`、循环引用、`BigInt`、`Map`/`Set` 等特殊类型处理不直观（静默丢弃或报错）；`replacer` 函数容易误删属性；`parse`/`stringify` 实现的深拷贝局限性大。 |

---

## 三、序列化陷阱

### 3.1 特殊类型序列化行为

| 维度 | 内容 |
|------|------|
| 是什么 | `JSON.stringify()` 对 JavaScript 中的特殊类型（`undefined`、`Function`、`Symbol`、`Date`、`NaN`、`Infinity`、`RegExp`、`Map`、`Set`、`BigInt`、循环引用）有非直观的处理行为。 |
| 能做什么 | 理解这些行为可以避免数据丢失、运行时错误和调试困难；知道如何正确处理这些特殊类型（如 Date 转 ISO 字符串后需 reviver 还原）。 |
| 怎么用 | 对象属性中的 `undefined`/`Function`/`Symbol` 被丢弃；数组中转为 `null`；`Date` 调用 `toISOString()`；`NaN`/`Infinity` 转为 `null`；`RegExp`/`Map`/`Set` 转为 `{}`；`BigInt` 抛出 TypeError；循环引用抛出 TypeError。 |
| 原理和工作流程 | 序列化时引擎按 ECMAScript 规范对每种类型执行特定转换：基本类型直接转换，对象类型递归遍历属性。遇到不支持的类型时，根据规范执行丢弃或报错。`toJSON()` 方法优先于 `replacer` 执行。 |
| 缺点 | 行为不统一：对象中丢弃、数组中转 null、独立值返回 undefined，容易造成困惑；`Map`/`Set` 转为空对象导致数据静默丢失，难以排查；`BigInt` 直接报错而非降级处理。 |

### 3.2 toJSON() 方法

| 维度 | 内容 |
|------|------|
| 是什么 | 如果对象定义了 `toJSON()` 方法，`JSON.stringify()` 会调用该方法，用其返回值替代原对象进行序列化。 |
| 能做什么 | 自定义对象的序列化行为：控制输出哪些字段（如 Date 只输出日期部分）、格式化字段值、隐藏内部属性。 |
| 怎么用 | `class Event { toJSON() { return { title: this.title, date: this.date.toISOString().split('T')[0] }; } }` |
| 原理和工作流程 | 执行顺序：`toJSON()` -> `replacer` -> 最终序列化。`toJSON()` 返回的对象会替代原对象，然后该返回值再经过 `replacer` 处理。 |
| 缺点 | 如果 `toJSON()` 返回的不是对象而是原始值，则该原始值会被直接序列化；可能与 `replacer` 的逻辑产生冲突。 |

### 3.3 循环引用处理

| 维度 | 内容 |
|------|------|
| 是什么 | 当对象之间存在相互引用（A 引用 B，B 引用 A）时，`JSON.stringify()` 会抛出 `TypeError`，因为无法处理无限嵌套。 |
| 能做什么 | 通过自定义 `safeStringify` 函数，使用 `WeakSet` 追踪已序列化的对象，遇到循环引用时返回标记字符串（如 `"[Circular]"`）。 |
| 怎么用 | `function safeStringify(obj) { const seen = new WeakSet(); return JSON.stringify(obj, (k, v) => { if (typeof v === 'object' && v !== null) { if (seen.has(v)) return '[Circular]'; seen.add(v); } return v; }); }` |
| 原理和工作流程 | 在 `replacer` 函数中维护一个 `WeakSet`（或 `WeakMap`），每次遇到对象类型时检查是否已存在：存在则返回标记字符串，不存在则加入集合并继续。使用 `WeakSet` 而非 `Set` 避免内存泄漏。 |
| 缺点 | 循环引用被标记后无法还原，反序列化时丢失原始引用关系；`WeakSet` 只能标记"是否见过"，无法记录引用路径。 |

---

## 四、AJAX 与 XMLHttpRequest

### 4.1 AJAX 概念

| 维度 | 内容 |
|------|------|
| 是什么 | AJAX（Asynchronous JavaScript And XML）是一种在不刷新整个页面的情况下，与服务器异步交换数据并局部更新网页的技术。现代 AJAX 通常使用 JSON 而非 XML。 |
| 能做什么 | 实现无刷新页面更新（搜索建议、无限滚动、表单异步提交、实时数据加载）；提升用户体验，避免白屏等待；减少数据传输量（仅传数据而非整个 HTML）。 |
| 怎么用 | 通过 `XMLHttpRequest` 对象或 `fetch()` API 发起异步 HTTP 请求，在回调/Promise 中处理响应数据，使用 DOM 操作更新页面局部内容。 |
| 原理和工作流程 | 浏览器通过 JavaScript 引擎发起异步网络请求（不阻塞主线程），请求完成后触发回调。底层依赖浏览器的网络线程池处理 HTTP 通信，主线程只负责发起请求和处理响应。 |
| 缺点 | 纯 AJAX 页面不利于 SEO（搜索引擎爬虫难以抓取动态内容）；浏览器后退按钮行为异常（需手动管理 History API）；跨域请求受同源策略限制。 |

### 4.2 XMLHttpRequest

| 维度 | 内容 |
|------|------|
| 是什么 | `XMLHttpRequest`（XHR）是浏览器提供的 AJAX 底层实现对象，通过事件驱动的方式发起 HTTP 请求并处理响应。 |
| 能做什么 | 发起 GET/POST/PUT/DELETE 等 HTTP 请求；设置自定义请求头；监听上传/下载进度；设置请求超时；获取响应状态码和响应体。 |
| 怎么用 | `xhr.open(method, url, async)` 初始化；`xhr.setRequestHeader()` 设置请求头；`xhr.send(body)` 发送；`xhr.onreadystatechange` 监听状态变化；`readyState === 4` 时读取 `status` 和 `responseText`。 |
| 原理和工作流程 | `readyState` 经历 5 个状态：0(UNSENT) -> 1(OPENED) -> 2(HEADERS_RECEIVED) -> 3(LOADING) -> 4(DONE)。每次状态变化触发 `onreadystatechange`。`onload` 是 `readyState === 4` 且状态码成功的简写。 |
| 缺点 | 回调地狱（多层嵌套回调）；API 设计繁琐（需要手动检查状态码、解析 JSON）；不支持 Promise 风格；`onreadystatechange` 触发多次增加调试复杂度。 |

### 4.3 XHR 上传/下载进度

| 维度 | 内容 |
|------|------|
| 是什么 | XHR 提供 `xhr.upload.onprogress` 和 `xhr.onprogress` 事件，分别用于监听上传和下载的进度。 |
| 能做什么 | 实现文件上传进度条、下载进度指示器；通过 `e.loaded` 和 `e.total` 计算百分比。 |
| 怎么用 | 上传：`xhr.upload.onprogress = (e) => { const pct = Math.round(e.loaded / e.total * 100); }`；下载：`xhr.onprogress` 同理。需设置 `responseType = 'blob'` 用于下载。 |
| 原理和工作流程 | 浏览器在传输数据时，周期性地触发 progress 事件，携带已传输字节数（`loaded`）和总字节数（`total`）。`lengthComputable` 为 `true` 时 `total` 有效。 |
| 缺点 | 仅在 XHR 中原生支持，Fetch API 不直接支持进度监听（需通过 `ReadableStream` 实现）；`total` 在某些情况下可能为 0。 |

---

## 五、Fetch API

### 5.1 Fetch 基础用法

| 维度 | 内容 |
|------|------|
| 是什么 | Fetch API 是浏览器原生提供的、基于 Promise 的现代网络请求接口，旨在替代 `XMLHttpRequest`。 |
| 能做什么 | 发起 HTTP 请求并获取响应；支持多种响应体解析方式（`json()`、`text()`、`blob()`、`arrayBuffer()`、`formData()`）；通过 `Request`/`Response`/`Headers` 对象实现请求和响应的分离管理。 |
| 怎么用 | `fetch(url, { method, headers, body, signal })` 返回 Promise；`.then(response => response.json())` 解析 JSON；`.then(data => console.log(data))` 处理数据；`.catch(err => console.error(err))` 处理错误。 |
| 原理和工作流程 | `fetch()` 返回的 Promise 只在**网络错误**时 reject（如断网、DNS 解析失败）。HTTP 错误状态码（404、500）不会导致 reject，Promise 仍会 resolve，需手动检查 `response.ok` 或 `response.status`。 |
| 缺点 | 不默认携带 Cookie（需设置 `credentials: 'include'`）；不原生支持超时（需配合 AbortController 或 Promise.race）；不原生支持进度监听；响应体只能消费一次。 |

### 5.2 Response 与 Headers 对象

| 维度 | 内容 |
|------|------|
| 是什么 | `Response` 对象是 `fetch()` 返回的响应封装，包含状态码、响应头、响应体等信息。`Headers` 对象用于管理 HTTP 请求/响应头。 |
| 能做什么 | 通过 `response.ok` 快速判断请求是否成功（200-299）；通过 `response.status` 获取 HTTP 状态码；通过 `response.headers` 获取响应头；通过 `response.clone()` 复制响应体以便多次读取。 |
| 怎么用 | `if (!response.ok) throw new Error('请求失败');`；`response.headers.get('Content-Type')`；`const clone = response.clone();`。Headers 方法：`append()`、`set()`、`get()`、`has()`、`delete()`。 |
| 原理和工作流程 | 响应体是 `ReadableStream`，只能被消费一次。消费后再次读取会抛出 `TypeError: Already read`。`clone()` 通过 tee 操作复制底层流，但会消耗双倍内存。 |
| 缺点 | 响应体一次性的限制容易导致调试困难；`clone()` 的内存开销较大；`json()` 等方法如果响应体不是对应格式会抛出错误。 |

### 5.3 Fetch 与 XHR 对比

| 维度 | 内容 |
|------|------|
| 是什么 | Fetch 和 XHR 都是浏览器端的网络请求方案，Fetch 是现代化替代方案，XHR 是传统方案。 |
| 能做什么 | 两者都能完成 HTTP 请求。Fetch 优势：Promise 风格、Request/Response 分离、更简洁的语法。XHR 优势：原生进度监听、原生超时设置、全浏览器兼容。 |
| 怎么用 | 选择依据：需要进度监听 -> XHR；需要简洁语法和 Promise -> Fetch；需要拦截器 -> Axios；（已过时）需要兼容 IE -> XHR（历史兼容场景，2026 年新项目按现代浏览器基线）。 |
| 原理和工作流程 | Fetch 基于 Promise 和 Stream API；XHR 基于事件驱动模型。Fetch 的 `credentials` 默认 `same-origin`，XHR 默认携带同源 Cookie。 |
| 缺点 | Fetch 在 404/500 时不 reject 是常见陷阱；Fetch 不原生支持超时和进度监听；XHR 的回调风格导致代码嵌套。 |

---

## 六、请求取消与超时处理

### 6.1 AbortController

| 维度 | 内容 |
|------|------|
| 是什么 | `AbortController` 是浏览器原生提供的请求取消机制，通过 `AbortSignal` 向异步操作（如 `fetch`）发送取消信号。 |
| 能做什么 | 取消进行中的 fetch 请求；同时取消多个关联请求；实现搜索防抖中的请求取消；在 React/Vue 组件卸载时取消未完成的请求。 |
| 怎么用 | `const controller = new AbortController(); fetch(url, { signal: controller.signal }); controller.abort();`。取消后 fetch 抛出 `AbortError`，需在 catch 中检查 `err.name === 'AbortError'`。 |
| 原理和工作流程 | `AbortController` 内部维护一个 `AbortSignal` 对象。当 `abort()` 被调用时，`signal.aborted` 变为 `true`，并触发 `signal` 上的 `abort` 事件。绑定该 `signal` 的 fetch 请求会立即终止底层网络连接。 |
| 缺点 | 同一 `signal` abort 后无法复用，需要创建新的 `AbortController`；忘记处理 `AbortError` 会导致控制台报错；不适用于所有异步操作（仅支持实现了 signal 接口的 API）。 |

### 6.2 超时处理方案对比

| 维度 | 内容 |
|------|------|
| 是什么 | 超时处理是防止请求无限等待的机制。三种方式：`AbortSignal.timeout()`（ES2024）、`Promise.race` 手动超时、XHR 的 `timeout` 属性。 |
| 能做什么 | 为请求设置最大等待时间；超时后自动取消请求并返回超时错误；防止用户长时间等待。 |
| 怎么用 | ES2024：`fetch(url, { signal: AbortSignal.timeout(5000) })`；Promise.race：`Promise.race([fetch(url), timeoutPromise])`；XHR：`xhr.timeout = 5000; xhr.ontimeout = () => reject()` |
| 原理和工作流程 | `AbortSignal.timeout()` 内部使用定时器，到期后自动 abort，真正取消底层网络请求。`Promise.race` 只是竞争胜出，**不取消**实际请求——超时后请求仍在进行中，浪费资源。 |
| 缺点 | `AbortSignal.timeout()` 浏览器兼容性有限；`Promise.race` 不真正取消请求导致资源浪费；XHR 的 timeout 仅在 XHR 中可用。 |

### 6.3 实战：搜索防抖 + 请求取消

| 维度 | 内容 |
|------|------|
| 是什么 | 将防抖（debounce）与请求取消（AbortController）结合，确保快速输入时只保留最新请求，取消中间未完成的请求。 |
| 能做什么 | 搜索框输入时避免发起大量无效请求；节省带宽和服务器资源；确保展示的搜索结果与最新输入一致。 |
| 怎么用 | 维护一个 `controller` 引用，每次发起新请求前调用 `controller.abort()` 取消上一次请求，然后创建新的 `AbortController`。在组件卸载时也调用 `abort()`。 |
| 原理和工作流程 | 每次输入触发搜索时，先取消上一个未完成的请求，再发起新请求。即使旧请求已发出，`abort()` 会终止其网络连接，响应不会到达。 |
| 缺点 | 需要在 catch 中区分 `AbortError`（正常取消）和其他错误；如果组件卸载时忘记取消请求，可能导致内存泄漏和状态更新错误。 |

---

## 七、Axios 核心特性

### 7.1 Axios 概述

| 维度 | 内容 |
|------|------|
| 是什么 | Axios 是目前最流行的、基于 Promise 的 HTTP 客户端库，同时支持浏览器和 Node.js 环境。在原生 API 基础上提供了拦截器、实例创建、自动 JSON 转换等增强功能。 |
| 能做什么 | 发起 HTTP 请求并自动处理 JSON 转换；通过请求/响应拦截器实现统一的 Token 注入、错误处理、日志记录；通过 `axios.create()` 创建多服务端实例；支持请求取消、超时、进度监听。 |
| 怎么用 | `axios.get(url, config)` / `axios.post(url, data, config)`；`axios.create({ baseURL, timeout })` 创建实例；`axios.interceptors.request.use(successFn, errorFn)` 注册拦截器。 |
| 原理和工作流程 | 请求拦截器按**后进先出**（栈）顺序执行：后添加的先执行。响应拦截器按**先进先出**（队列）顺序执行：先添加的先执行。`axios.create()` 创建的实例拥有独立的拦截器链，不会与全局拦截器互相干扰。 |
| 缺点 | 相比原生 Fetch 体积较大（约 13KB gzipped）；学习成本比 Fetch 高；拦截器执行顺序（请求 LIFO、响应 FIFO）容易混淆。 |

### 7.2 请求/响应拦截器

| 维度 | 内容 |
|------|------|
| 是什么 | 拦截器是 Axios 的核心特性，允许在请求发送前（request interceptor）和响应返回后（response interceptor）统一处理。 |
| 能做什么 | 请求拦截器：统一添加 Token、设置请求头、请求日志、参数转换；响应拦截器：统一数据提取（`response.data`）、错误处理（401 跳登录、403 提示）、Token 刷新。 |
| 怎么用 | `axios.interceptors.request.use(onFulfilled, onRejected)`；`axios.interceptors.response.use(onFulfilled, onRejected)`。请求拦截器必须 `return config`，响应拦截器可以 `return response.data` 简化调用方代码。 |
| 原理和工作流程 | 拦截器形成链式调用：`requestInterceptor2 -> requestInterceptor1 -> dispatchRequest -> responseInterceptor1 -> responseInterceptor2`。请求拦截器后添加的先执行（栈），响应拦截器先添加的先执行（队列）。 |
| 缺点 | 请求拦截器中忘记 `return config` 导致请求无法发送；响应拦截器中过度修改 `response` 导致下游代码不可预期；拦截器链过长影响性能。 |

### 7.3 实例创建与默认配置

| 维度 | 内容 |
|------|------|
| 是什么 | `axios.create(config)` 创建独立的 Axios 实例，拥有独立的配置（baseURL、timeout、headers）和拦截器链。 |
| 能做什么 | 多服务端场景：不同 API 使用不同的 baseURL 和鉴权方式；避免全局配置污染；微前端/多模块项目中的请求隔离。 |
| 怎么用 | `const api = axios.create({ baseURL: 'https://api.example.com', timeout: 10000 });`；`api.get('/users')` 使用实例发起请求；实例级别的拦截器：`api.interceptors.request.use(...)`。 |
| 原理和工作流程 | `axios.create()` 内部创建新的 Axios 实例，复制默认配置并合并用户配置。每个实例维护独立的拦截器栈/队列，实例之间互不影响。全局 `axios` 本质也是一个默认实例。 |
| 缺点 | 过多实例会增加内存开销；实例间配置不共享，需要手动管理公共配置；当需要实例间共享拦截器逻辑时，需要抽取公共函数。 |

### 7.4 Axios 取消请求

| 维度 | 内容 |
|------|------|
| 是什么 | Axios 支持通过 `AbortController`（现代方式）取消请求，与 Fetch API 使用相同的取消机制。 |
| 能做什么 | 取消进行中的请求；在搜索防抖、页面切换、组件卸载等场景中避免无效请求；使用 `axios.isCancel(err)` 判断是否为取消错误。 |
| 怎么用 | `const controller = new AbortController(); axios.get(url, { signal: controller.signal }); controller.abort();`；错误处理中：`if (axios.isCancel(err)) { ... }` |
| 原理和工作流程 | 与 Fetch 的 AbortController 机制相同。Axios 内部将 `signal` 传递给底层适配器（浏览器用 XHR/fetch，Node.js 用 http），由适配器处理取消逻辑。 |
| 缺点 | 与 Fetch 相同的 AbortController 限制：一个 signal 只能使用一次；需要手动处理 `AbortError`。 |

### 7.5 Axios vs Fetch vs XHR 综合对比

| 维度 | 内容 |
|------|------|
| 是什么 | 三种浏览器端 HTTP 请求方案：XHR 是传统回调方案，Fetch 是原生 Promise 方案，Axios 是第三方增强库。 |
| 能做什么 | XHR：基础请求 + 进度监听 + 超时；Fetch：Promise 风格 + 流式读取；Axios：拦截器 + 实例 + 自动转换 + 全平台兼容。 |
| 怎么用 | 选择依据：简单请求用 Fetch，需要拦截器/实例用 Axios，需要进度监听用 XHR，（已过时）需要兼容 IE 用 XHR 或 Axios（历史兼容场景，2026 年新项目按现代浏览器基线）。 |
| 原理和工作流程 | XHR 基于事件驱动，Fetch 基于 Promise + Stream，Axios 基于适配器模式（封装 XHR 和 Node.js http 模块）。Axios 在浏览器端底层仍使用 XHR。 |
| 缺点 | XHR 回调地狱；Fetch 不 reject 非 2xx、不原生支持超时和进度；Axios 体积较大、学习成本较高。 |

---

## 八、常见面试题

### 1. JSON.stringify 的序列化陷阱

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 `JSON.stringify()` 对 `undefined`、`Function`、`Symbol`、`Date`、`NaN`、`Infinity`、`RegExp`、`Map`、`Set`、`BigInt`、循环引用等特殊类型的处理行为。 |
| 能做什么 | 检验对 JSON 序列化底层规则的理解深度，以及对数据丢失风险的防范意识。 |
| 怎么用 | 对象属性中的 `undefined`/`Function`/`Symbol` 被丢弃；数组中转为 `null`；`Date` -> ISO 字符串；`NaN`/`Infinity` -> `null`；`BigInt` -> TypeError；循环引用 -> TypeError。 |
| 原理和工作流程 | 引擎按 ECMAScript 规范对每种类型执行特定转换。不支持的类型根据规范执行丢弃或报错。`toJSON()` 优先于 `replacer` 执行。 |
| 缺点 | 回答时容易遗漏数组与对象中行为不一致的细节，以及 `toJSON()` 与 `replacer` 的执行顺序。 |

### 2. Fetch 与 XHR 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查浏览器端两种网络请求方案在 API 风格、错误处理、功能支持等维度的差异。 |
| 能做什么 | 检验对现代 Web API 演进的了解，以及在实际项目中如何选择合适的请求方案。 |
| 怎么用 | Fetch：Promise 风格、简洁语法、不默认携带 Cookie、不 reject 非 2xx；XHR：事件回调风格、原生进度监听、原生超时、全浏览器兼容。 |
| 原理和工作流程 | Fetch 基于 Promise 和 Stream API，Response body 只能消费一次；XHR 基于事件驱动，`readyState` 经历 5 个状态变化。 |
| 缺点 | 容易忽略 Fetch 的 404 不 reject 陷阱和 Cookie 默认不携带的问题。 |

### 3. Axios 拦截器执行顺序

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Axios 请求拦截器和响应拦截器的执行顺序：请求拦截器后进先出（栈），响应拦截器先进先出（队列）。 |
| 能做什么 | 检验对 Axios 拦截器链式调用机制的深入理解。 |
| 怎么用 | 请求拦截器：`interceptor2 -> interceptor1 -> dispatchRequest`；响应拦截器：`dispatchRequest -> interceptor1 -> interceptor2`。 |
| 原理和工作流程 | Axios 内部维护拦截器数组，请求拦截器使用 `unshift` 插入（栈），响应拦截器使用 `push` 插入（队列）。最终形成链式 Promise 调用。 |
| 缺点 | 容易混淆请求和响应拦截器的执行顺序，错误的拦截器顺序可能导致 Token 注入失败或数据处理异常。 |

---

## 九、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 汇总 JSON 处理与网络请求中 10 个高频错误：JSON 格式错误、序列化数据丢失、反序列化类型丢失、Fetch 不 reject 404、响应体重复读取、Cookie 丢失、请求未取消、超时未真正取消、拦截器 config 未返回、AbortError 未处理。 |
| 能做什么 | 帮助开发者提前规避常见陷阱，写出更健壮的网络请求代码。 |
| 怎么用 | JSON 解析用 try-catch 包裹；序列化前检查特殊类型；Fetch 始终检查 `response.ok`；响应体只读取一次或 clone；设置 `credentials: 'include'`；组件卸载时 `controller.abort()`；使用 AbortSignal.timeout 而非 Promise.race；拦截器必须 `return config`。 |
| 原理和工作流程 | 每个错误对应一个底层机制的误解：JSON 是 JS 对象的严格子集；Fetch 设计哲学区分网络层和应用层错误；Response body 是 ReadableStream；拦截器形成链式调用。 |
| 缺点 | 部分避坑方案需要理解底层机制才能正确应用，初学者容易机械套用。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./06-JSON与网络请求.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)
