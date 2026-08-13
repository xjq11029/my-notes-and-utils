# 02-事件循环与Web安全 导览

> 定位：五维框架浓缩提炼 02-事件循环与Web安全.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-事件循环与Web安全.md)。
> 前置知识：[浏览器渲染与V8原理](./01-浏览器渲染与V8原理-导览.md)、[异步编程与ES6+特性](../02-javascript-core/02-异步编程与ES6+特性-导览.md)

---

## 一、核心概念

本节为辅助内容，无五维表格。

---

## 二、底层原理

### 2.1 浏览器事件循环（Event Loop）

| 维度 | 内容 |
|------|------|
| 是什么 | JavaScript 单线程环境下通过宏任务队列和微任务队列实现异步任务调度的机制，核心规则是每个宏任务执行完后清空所有微任务再执行下一个宏任务。 |
| 能做什么 | 使 JavaScript 在单线程中能处理异步操作（定时器、Promise、事件监听、网络请求等），实现非阻塞 IO；通过理解执行顺序可编写正确的异步代码和预测输出顺序。 |
| 怎么用 | `console.log('1'); setTimeout(() => console.log('2'), 0); Promise.resolve().then(() => console.log('3')); console.log('4');` 输出顺序：1、4、3、2。 |
| 原理和工作流程 | 执行同步代码（script 整体是一个宏任务），执行完毕后清空微任务队列（包括执行过程中新产生的微任务），然后取出一个宏任务执行，再清空微任务队列，循环往复。宏任务包括：`setTimeout`、`setInterval`、`I/O`；微任务包括：`Promise.then/catch/finally`、`MutationObserver`、`queueMicrotask`。微任务队列必须完全清空后才能执行下一个宏任务；UI 渲染在宏任务之间可能执行，但不属于宏任务或微任务队列。 |
| 缺点 | 微任务无限递归产生新微任务会导致微任务队列永远清空不完，页面卡死；宏任务粒度较粗，无法精确控制异步执行时机。 |

### 2.2 requestAnimationFrame vs requestIdleCallback

| 维度 | 内容 |
|------|------|
| 是什么 | `requestAnimationFrame` 在浏览器下次重绘前执行回调，与屏幕刷新率同步；`requestIdleCallback` 在浏览器空闲时段执行回调，适合低优先级任务。 |
| 能做什么 | rAF 用于流畅动画和视觉更新，保证不掉帧且页面不可见时自动暂停节省资源；rIC 用于数据上报、日志记录、预加载等低优先级任务，不阻塞主线渲染。 |
| 怎么用 | `requestAnimationFrame(animate)` 递归调用实现动画循环；`requestIdleCallback((deadline) => { while (deadline.timeRemaining() > 0 && tasks.length) { task = tasks.shift(); task(); } })` 利用空闲时间执行任务。 |
| 原理和工作流程 | rAF 在浏览器每帧渲染前执行回调，帧率与屏幕刷新率同步（通常 60fps，即约 16.6ms 一帧）；页面不可见时自动暂停，恢复可见后继续执行；rIC 在每帧的空闲时间（16.6ms 减去渲染和 JS 执行时间后的剩余时间）执行回调，不保证一定会执行。 |
| 缺点 | rAF 不适合处理低优先级任务，会占用每帧的渲染预算；rIC 不保证执行时机，浏览器繁忙时可能长时间不触发回调。 |

### 2.3 跨域原理与解决方案

| 维度 | 内容 |
|------|------|
| 是什么 | 浏览器同源策略限制不同源（协议、域名、端口任一不同）之间的资源访问，CORS、JSONP、代理服务器、postMessage、WebSocket、document.domain 是六种常见跨域解决方案。 |
| 能做什么 | CORS 是最标准的方案，服务器设置响应头后浏览器自动处理跨域；JSONP 利用 `<script>` 标签不受同源限制实现 GET 跨域；代理服务器将跨域请求转为同源请求；postMessage 安全实现跨窗口通信。 |
| 怎么用 | CORS：`Access-Control-Allow-Origin: https://example.com`；JSONP：`<script src="https://api.com/data?callback=handleResponse">`；代理：`proxy: { '/api': { target: 'https://api.com', changeOrigin: true } }`；postMessage：`iframe.contentWindow.postMessage('hello', 'https://child.com')`。 |
| 原理和工作流程 | 同源策略是浏览器最基本的安全策略，限制跨域读取；CORS 简单请求（GET/HEAD/POST 且 Content-Type 为简单类型）直接发送，浏览器自动添加 Origin 头，服务器返回 Access-Control-Allow-Origin 决定是否允许；非简单请求先发送 OPTIONS 预检请求确认服务器是否允许，通过后再发送实际请求；携带 Cookie 需要服务器设置 `Access-Control-Allow-Credentials: true` 且客户端设置 `withCredentials: true`；JSONP 动态创建 `<script>` 标签，服务器返回回调函数调用，只支持 GET，安全性差；代理服务器转发请求绕过浏览器同源限制。 |
| 缺点 | CORS 预检请求增加一次额外网络往返；JSONP 只支持 GET、不安全、不支持自定义请求头；代理服务器增加运维成本；postMessage 需要双方配合验证来源。 |

### 2.4 Web 存储机制对比

| 维度 | 内容 |
|------|------|
| 是什么 | 浏览器端四种存储方案的对比：Cookie（约 4KB，每次 HTTP 请求自动携带）、localStorage（约 5MB，永久存储）、sessionStorage（约 5MB，关闭标签页清除）、IndexedDB（无上限，结构化数据，异步 API）。 |
| 能做什么 | Cookie 用于用户认证和会话管理；localStorage 用于长期缓存和用户偏好设置；sessionStorage 用于表单临时数据；IndexedDB 用于大量结构化数据和离线应用。 |
| 怎么用 | `document.cookie = 'token=abc; max-age=3600; path=/; secure; samesite=lax'`；`localStorage.setItem('theme', 'dark')`；`sessionStorage.setItem('formData', JSON.stringify({ name: 'test' }))`；`const request = indexedDB.open('myDB', 1)`。 |
| 原理和工作流程 | Cookie 在每次 HTTP 请求中自动附加在请求头中，增加请求体积，容量仅约 4KB，可设置过期时间、路径、Secure、HttpOnly、SameSite 等属性；localStorage 和 sessionStorage 为纯客户端存储，不随请求发送，API 简单，但只能存储字符串；IndexedDB 是浏览器端的 NoSQL 数据库，支持事务、索引、游标，异步 API 不阻塞主线程。 |
| 缺点 | Cookie 每次请求都携带，增加网络开销且容量小；localStorage 和 sessionStorage 只能存储字符串，存储对象需要 JSON 序列化；localStorage 为明文存储，XSS 攻击可读取；IndexedDB API 相对复杂，学习成本高。 |

### 2.5 XSS（跨站脚本攻击）原理与防御

| 维度 | 内容 |
|------|------|
| 是什么 | 攻击者将恶意脚本注入页面，在用户浏览器中执行的攻击方式，分为存储型、反射型和 DOM 型三种类型。 |
| 能做什么 | 防御策略包括：输入校验+输出编码转义特殊字符、使用 `textContent` 代替 `innerHTML`、配置 CSP 限制脚本来源、设置 HttpOnly Cookie 防止 Cookie 被盗、使用 DOMPurify 清理 HTML。 |
| 怎么用 | `element.textContent = userInput` 代替 `element.innerHTML = userInput`；`Content-Security-Policy: script-src 'self'`；`Set-Cookie: token=abc; HttpOnly; Secure; SameSite=Strict`。 |
| 原理和工作流程 | 存储型 XSS：恶意脚本存储在服务器端（评论、留言），用户访问时从服务器加载执行，危害最大；反射型 XSS：恶意脚本通过 URL 参数传递，服务器直接反射到页面，需诱导用户点击恶意链接；DOM 型 XSS：纯客户端发生，前端 JS 不当地将用户输入插入 DOM 中（如 `innerHTML = location.search` 的参数值）。 |
| 缺点 | 防御措施需要多层防护，单靠一层不够；CSP 配置不当可能导致正常功能被误拦截；对第三方富文本编辑器等场景，完全防御 XSS 难度较大。 |

### 2.6 CSRF（跨站请求伪造）原理与防御

| 维度 | 内容 |
|------|------|
| 是什么 | 攻击者利用用户已登录状态，在恶意网站中诱导用户向目标网站发起非预期请求，浏览器自动携带目标网站的 Cookie 导致请求被认证通过。 |
| 能做什么 | 防御措施：CSRF Token（服务器生成随机 Token 嵌入表单，提交时验证）、SameSite Cookie（Strict 完全禁止第三方请求携带 Cookie）、Referer/Origin 校验（检查请求来源域名）、双重 Cookie 验证。 |
| 怎么用 | `Set-Cookie: token=abc; SameSite=Strict`；`fetch('/api/data', { headers: { 'X-CSRF-Token': getCsrfToken() } })`；服务端校验 `Origin` 或 `Referer` 请求头。 |
| 原理和工作流程 | 用户登录 A 网站后浏览器保存 Cookie；用户访问恶意网站 B，B 向 A 发送请求（如 `<img src="https://A.com/transfer?to=attacker">`），浏览器自动携带 A 的 Cookie；A 服务端以为是用户自己发起的请求并执行操作；CSRF Token 防御原理是攻击者无法获取随机 Token 值，无法构造有效请求。 |
| 缺点 | CSRF Token 需要服务端配合，增加了开发复杂度；SameSite=Strict 过于严格，部分场景（如从邮件链接跳转）可能影响用户体验；Referer 校验可能被隐私设置或代理屏蔽。 |

### 2.7 点击劫持（Clickjacking）防御

| 维度 | 内容 |
|------|------|
| 是什么 | 攻击者通过透明 iframe 将目标页面覆盖在用户可见内容之上，用户以为点击的是可见按钮，实际点击的是透明 iframe 中的目标页面按钮。 |
| 能做什么 | 通过 `X-Frame-Options` 或 CSP `frame-ancestors` 指令禁止页面被嵌入到 iframe 中，从源头防御点击劫持。 |
| 怎么用 | `X-Frame-Options: DENY` 禁止任何页面嵌入；`X-Frame-Options: SAMEORIGIN` 允许同源嵌入；`Content-Security-Policy: frame-ancestors 'self'`。 |
| 原理和工作流程 | 攻击者在自己的页面中放置一个透明 iframe 加载目标页面，用户在视觉上看到的是攻击者页面内容，但点击事件穿透到透明 iframe 上；`X-Frame-Options` 是 HTTP 响应头，浏览器收到后拒绝在 iframe 中渲染该页面。 |
| 缺点 | 部分旧浏览器不支持 `X-Frame-Options`；CSP `frame-ancestors` 优先级更高，但需要浏览器支持 CSP。 |

### 2.8 内容安全策略（CSP）

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 HTTP 响应头或 `<meta>` 标签告诉浏览器哪些资源可以加载和执行，是防御 XSS 和数据注入攻击的强力手段。 |
| 能做什么 | 限制脚本来源（`script-src`）、样式来源（`style-src`）、图片来源（`img-src`）、连接来源（`connect-src`）等；禁止内联脚本和 `eval()`，从根本上阻止 XSS 攻击。 |
| 怎么用 | `Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.com; style-src 'self' 'unsafe-inline'; img-src *; connect-src 'self' https://api.example.com; object-src 'none'; frame-ancestors 'self'`。 |
| 原理和工作流程 | 浏览器解析 CSP 头后建立资源加载白名单；任何不符合白名单的资源（脚本、样式、图片、字体、连接等）被浏览器阻止加载并报告违规；`'nonce-xxx'` 和 `'strict-dynamic'` 提供更灵活的内联脚本控制；`report-uri` 或 `report-to` 指令可将违规报告发送到指定端点。 |
| 缺点 | CSP 配置复杂，需要仔细规划和测试；过于严格的策略会导致正常功能失效；部分老旧浏览器不支持 CSP。 |

---

## 三、实战应用

### 3.1 事件循环实战：异步任务调度

| 维度 | 内容 |
|------|------|
| 是什么 | 将耗时操作拆分为多个小任务，通过 `setTimeout` 将控制权交还给浏览器，避免长时间阻塞主线程的实践模式。 |
| 能做什么 | 处理大数组时按批次（chunk）执行，每批处理一定数量后将控制权交还浏览器渲染，保持页面响应。 |
| 怎么用 | `function processChunk() { const end = Math.min(index + chunkSize, items.length); for (; index < end; index++) { heavyProcess(items[index]); } if (index < items.length) { setTimeout(processChunk, 0); } }`。 |
| 原理和工作流程 | 每个 `setTimeout` 回调作为一个宏任务被放入任务队列；当前宏任务执行完毕后浏览器有机会执行 UI 渲染和事件处理，然后再取出下一个 `setTimeout` 回调；这样将长时间计算拆分为多个短任务，每个短任务之间可以插入 UI 渲染。 |
| 缺点 | `setTimeout` 最小延迟约 4ms（嵌套超过 5 层后），对于高精度分片不够精确；频繁的宏任务切换有一定开销。 |

### 3.2 安全编码实践

| 维度 | 内容 |
|------|------|
| 是什么 | 前端安全编码的三种核心实践：使用 `textContent` 防止 XSS、配置带 nonce 的 CSP 限制内联脚本、设置安全的 Cookie 属性和 CSRF Token。 |
| 能做什么 | 从源头阻止 XSS 注入和 CSRF 攻击；安全地渲染用户内容和处理跨域请求。 |
| 怎么用 | `const div = document.createElement('div'); div.textContent = userContent;` 安全渲染；`Set-Cookie: session=xxx; HttpOnly; Secure; SameSite=Lax; Path=/`；`fetch('/api/data', { headers: { 'X-CSRF-Token': getCsrfToken() } })`。 |
| 原理和工作流程 | `textContent` 将内容作为纯文本插入，不会解析 HTML 标签，从根本上阻止脚本注入；HttpOnly Cookie 禁止 JavaScript 访问，防止 XSS 窃取 Cookie；Secure 确保 Cookie 仅通过 HTTPS 传输；SameSite 限制第三方请求携带 Cookie；CSRF Token 在请求头中传递，攻击者无法读取 Cookie 中的 Token 值。 |
| 缺点 | 需要前后端配合实现 CSRF Token 和 Cookie 安全配置；`textContent` 不适用于需要渲染富文本的场景。 |

### 3.3 跨域开发实践

| 维度 | 内容 |
|------|------|
| 是什么 | 开发环境和生产环境中跨域解决方案的完整配置：开发环境使用 Vite/Webpack proxy 代理，生产环境使用 CORS 中间件或 Nginx 反向代理。 |
| 能做什么 | 开发环境通过代理转发避免跨域问题，无需后端配置 CORS；生产环境通过 CORS 中间件精确控制允许的来源、方法和请求头。 |
| 怎么用 | Vite: `server: { proxy: { '/api': { target: 'http://localhost:3000', changeOrigin: true } } }`；Express: `app.use(cors({ origin: 'https://your-frontend.com', credentials: true }))`。 |
| 原理和工作流程 | 开发代理将前端请求转发到目标服务器，对浏览器而言请求的是同源地址，不触发跨域限制；CORS 中间件根据配置自动设置 `Access-Control-Allow-Origin`、`Access-Control-Allow-Methods`、`Access-Control-Allow-Credentials` 等响应头。 |
| 缺点 | 开发代理配置仅适用于开发环境，生产环境需要独立的 CORS 方案；Nginx 反向代理需要运维配置。 |

---

## 四、常见面试题

### Q1：事件循环中，宏任务和微任务优先级是什么

| 维度 | 内容 |
|------|------|
| 是什么 | 微任务优先级高于宏任务，每次执行完一个宏任务后立即清空所有微任务，微任务队列未清空前不会执行下一个宏任务。 |
| 能做什么 | 预测异步代码的输出顺序，理解 `Promise.then` 回调为什么比 `setTimeout` 回调先执行。 |
| 怎么用 | `console.log('1'); setTimeout(() => console.log('2'), 0); Promise.resolve().then(() => console.log('3')); console.log('4');` 输出：1、4、3、2。 |
| 原理和工作流程 | 同步代码（script 宏任务）执行完后，检查微任务队列并全部清空（包括执行过程中新产生的微任务），然后取出下一个宏任务（setTimeout 回调）执行，再清空微任务队列，循环往复。 |
| 缺点 | 微任务中产生新微任务会导致当前轮次不断延长，可能延迟下一个宏任务和 UI 渲染的执行。 |

### Q2：requestAnimationFrame 和 setTimeout 做动画哪个更好

| 维度 | 内容 |
|------|------|
| 是什么 | `requestAnimationFrame` 与屏幕刷新率同步，在浏览器下次重绘前执行回调；`setTimeout` 受最小延迟和任务队列影响，执行时机不稳定。 |
| 能做什么 | rAF 保证动画不掉帧，自动适配不同刷新率设备；页面不可见时自动暂停节省 CPU 和电量；浏览器会将多个 rAF 回调合并到同一帧执行。 |
| 怎么用 | `function animate() { box.style.transform = 'translateX(' + x++ + 'px)'; requestAnimationFrame(animate); } requestAnimationFrame(animate);`。 |
| 原理和工作流程 | rAF 在每帧渲染前执行回调，频率与屏幕刷新率同步（通常 60fps）；即使主线程繁忙，rAF 也会在下一帧尽可能执行；页面切换到后台标签页时自动暂停；setTimeout 最小延迟约 4ms，且受任务队列中其他任务影响，执行间隔不稳定，可能导致动画掉帧。 |
| 缺点 | rAF 每帧只执行一次回调，不适合需要高频精确定时的场景（如游戏物理引擎）。 |

### Q3：CORS 预检请求是什么？什么情况下触发

| 维度 | 内容 |
|------|------|
| 是什么 | 浏览器在发送非简单跨域请求前，先发送 OPTIONS 请求询问服务器是否允许该跨域操作，这就是预检请求（Preflight）。 |
| 能做什么 | 让服务器在真正请求前确认跨域策略，避免复杂请求直接发送后被拒绝造成资源浪费。 |
| 怎么用 | 服务端需响应 OPTIONS 请求：`Access-Control-Allow-Methods: PUT, DELETE`、`Access-Control-Allow-Headers: X-Custom-Header`、`Access-Control-Max-Age: 86400` 缓存预检结果。 |
| 原理和工作流程 | 触发条件：请求方法不是 GET/HEAD/POST 之一，或 Content-Type 不在简单类型中（`text/plain`、`multipart/form-data`、`application/x-www-form-urlencoded`），或包含自定义请求头；浏览器自动发送 OPTIONS 请求，携带 `Access-Control-Request-Method` 和 `Access-Control-Request-Headers` 头；服务器返回允许的方法和头部后，浏览器才发送实际请求。 |
| 缺点 | 预检请求增加一次网络往返，增加请求延迟；`Access-Control-Max-Age` 可缓存预检结果减少重复预检，但缓存时间有限。 |

### Q4：Cookie 的 SameSite 属性有哪些值

| 维度 | 内容 |
|------|------|
| 是什么 | SameSite 是 Cookie 的安全属性，控制第三方请求是否携带 Cookie，有三个值：Strict（完全禁止第三方 Cookie）、Lax（允许安全的第三方请求）、None（所有请求都发送，需配合 Secure）。 |
| 能做什么 | Strict 提供最强 CSRF 防御；Lax 在安全性和用户体验间取得平衡，允许链接跳转和 GET 表单提交携带 Cookie；None 用于需要跨站共享 Cookie 的场景。 |
| 怎么用 | `Set-Cookie: token=abc; SameSite=Strict`；`Set-Cookie: token=abc; SameSite=Lax`；`Set-Cookie: token=abc; SameSite=None; Secure`。 |
| 原理和工作流程 | Strict：从第三方网站点击链接跳转到目标网站时也不携带 Cookie，用户需要重新登录；Lax：允许链接跳转、GET 表单提交等顶级导航携带 Cookie，但禁止 iframe、img、AJAX 等子资源请求携带；None：所有请求都携带 Cookie，必须配合 Secure 属性（仅 HTTPS 发送）。 |
| 缺点 | Strict 过于严格，从外部链接访问时用户需要重新登录；Chrome 默认 SameSite=Lax，可能影响依赖第三方 Cookie 的功能。 |

### Q5：XSS 和 CSRF 的区别是什么

| 维度 | 内容 |
|------|------|
| 是什么 | XSS 是攻击者将恶意脚本注入页面在用户浏览器中执行，目标是窃取用户信息；CSRF 是攻击者利用用户登录状态诱导用户执行非预期操作，目标是以用户身份发起请求。 |
| 能做什么 | 区分两种攻击可采取针对性防御：XSS 防御重在输入输出编码和 CSP；CSRF 防御重在 Token 验证和 SameSite Cookie。 |
| 怎么用 | XSS 防御：`element.textContent = userInput` + `Content-Security-Policy: script-src 'self'`；CSRF 防御：`Set-Cookie: token=abc; SameSite=Strict` + `fetch('/api', { headers: { 'X-CSRF-Token': token } })`。 |
| 原理和工作流程 | XSS 攻击发生在浏览器端，攻击者将 `<script>malicious()</script>` 注入到页面中，脚本在用户浏览器中执行，可读取 Cookie、localStorage、发送请求等；CSRF 攻击不需要注入脚本，只需诱导用户访问恶意页面，浏览器自动携带目标网站的 Cookie 发送请求，攻击者利用的是浏览器自动携带 Cookie 的机制。 |
| 缺点 | XSS 和 CSRF 可能同时存在，需要多层防御；防御措施需要前后端配合，单靠前端或后端都不够。 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 聚合了事件循环与 Web 安全开发中十个常见错误的综合参考：innerHTML 渲染用户输入、不理解 Promise 构造函数同步执行、微任务无限递归、Cookie 不设置 SameSite、跨域请求没带 Cookie、CORS 使用 `*` 且带 Cookie、CSRF Token 放在 Cookie 中、忘记移除事件监听、使用 document.domain 跨域、localStorage 存敏感数据。 |
| 能做什么 | 快速对照排查：使用 `textContent` 或 DOMPurify 代替 `innerHTML`；理解 `new Promise(fn)` 中 fn 是同步执行的；微任务中避免递归产生微任务；明确设置 SameSite 属性；服务器设置 `Access-Control-Allow-Credentials` 且客户端设置 `withCredentials`；带 Cookie 时 `Access-Control-Allow-Origin` 必须指定具体域名；Token 放在请求头或表单中；组件卸载时 `removeEventListener`；使用 `postMessage` 或 CORS 替代 `document.domain`；敏感数据存 HttpOnly Cookie 或加密存储。 |
| 原理和工作流程 | `innerHTML` 会解析执行 HTML 中的脚本标签，`textContent` 只设置纯文本；Promise 构造函数中的代码是同步执行的，只有 `.then` 回调是异步的；微任务中递归产生新微任务导致微任务队列不断增长，主线程永远无法执行下一个宏任务；Chrome 默认 SameSite=Lax，不设置时可能影响跨站请求；跨域请求默认不携带 Cookie，需要明确配置；`Access-Control-Allow-Origin: *` 与 `withCredentials: true` 互斥；Cookie 会被自动携带，攻击者页面也能利用，Token 应在请求头中传递。 |
| 缺点 | 需要开发者持续关注安全编码规范；部分错误（如微任务无限递归）在测试中不易发现。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./02-事件循环与Web安全.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)