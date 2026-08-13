# 08-BOM与浏览器扩展API 导览

> 定位：五维框架浓缩提炼 08-BOM与浏览器扩展API.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./08-BOM与浏览器扩展API.md)。
> 前置知识：JavaScript 基础语法、DOM 操作

---

## 一、window 对象

### 1.1 window 全局作用域与定时器

| 维度 | 内容 |
|------|------|
| 是什么 | `window` 是 BOM 的核心对象，代表浏览器窗口，同时也是 JavaScript 全局对象。所有全局变量和函数都挂载在 `window` 上。 |
| 能做什么 | 提供全局作用域；通过 `setTimeout` 延迟执行代码、`setInterval` 周期执行代码；通过 `clearTimeout`/`clearInterval` 取消定时器；通过 `alert`/`confirm`/`prompt` 弹出系统对话框。 |
| 怎么用 | `var a = 1` 等价于 `window.a = 1`（`let`/`const` 不会挂载到 `window`）；`const id = setTimeout(fn, 1000)` 延迟执行，`clearTimeout(id)` 取消；`setInterval(fn, 1000)` 周期执行，`clearInterval(id)` 停止。 |
| 原理和工作流程 | `var` 声明的全局变量存储在全局环境记录的 `[[VarRecord]]` 中，绑定到 `window` 对象；`let`/`const` 存储在 `[[DeclarativeRecord]]` 中，不绑定 `window`。定时器回调进入宏任务队列，等待事件循环调度。嵌套超过 5 层的定时器最小延迟强制为 4ms，后台标签页最小延迟 1000ms。 |
| 缺点 | `var` 全局变量污染 `window`；`setInterval` 不考虑回调耗时，可能导致回调堆积；`alert`/`confirm`/`prompt` 是同步阻塞的，会冻结页面；定时器中的 `this` 默认指向 `window`。 |

### 1.2 窗口控制与滚动

| 维度 | 内容 |
|------|------|
| 是什么 | `window.open()` 打开新窗口，`window.close()` 关闭窗口（仅限通过 `open` 打开的窗口）。`window.scrollTo()` 滚动到指定位置，`window.scrollBy()` 相对当前滚动。 |
| 能做什么 | 弹窗打开第三方页面；实现页面平滑滚动到指定区域；通过 `behavior: 'smooth'` 实现 CSS 级别的平滑滚动动画。 |
| 怎么用 | `window.open(url, '_blank', 'width=800,height=600')` 打开居中弹窗；`window.scrollTo({ top: 0, behavior: 'smooth' })` 平滑滚动到顶部；`window.scrollBy({ top: 500, behavior: 'smooth' })` 向下滚动 500px。 |
| 原理和工作流程 | `open()` 返回新窗口的 `window` 引用，可跨窗口通信（同源）。现代浏览器通常拦截非用户手势触发的 `open()`。`scrollTo`/`scrollBy` 操作的是 `window.scrollX`/`scrollY`。 |
| 缺点 | 弹窗常被浏览器拦截；`close()` 只能关闭脚本打开的窗口；`scrollTo` 在 `overflow: hidden` 的容器中无效。 |

---

## 二、location 对象

### 2.1 location 核心属性

| 维度 | 内容 |
|------|------|
| 是什么 | `location` 对象提供当前文档的 URL 完整信息，包含协议、主机、端口、路径、查询参数、哈希等组成部分。 |
| 能做什么 | 读取和解析 URL 各部分信息；通过修改 `location.href` 实现页面跳转；通过 `search`、`hash` 获取查询参数和锚点。 |
| 怎么用 | `location.href` 获取完整 URL；`location.pathname` 获取路径；`location.search` 获取 `?key=value` 查询字符串；`location.hash` 获取 `#section` 哈希值；`location.origin` 获取协议+主机+端口。 |
| 原理和工作流程 | 修改 `location` 的任何属性（除 `hash` 外）都会触发页面导航。修改 `hash` 仅触发 `hashchange` 事件，不刷新页面。修改 `href` 等价于调用 `assign()`。 |
| 缺点 | 修改 `location` 属性后代码不会立即停止执行，可能导致后续代码意外运行；`search` 返回的是原始字符串，需手动解析；中文参数被 URL 编码。 |

### 2.2 location 导航方法

| 维度 | 内容 |
|------|------|
| 是什么 | `location.assign()`、`location.replace()`、`location.reload()` 是三种页面导航方式，区别在于历史记录的处理方式。 |
| 能做什么 | `assign(url)` 导航到新 URL 并保留历史记录（可后退）；`replace(url)` 替换当前 URL，不保留历史记录（不可后退）；`reload()` 重新加载页面，可选参数 `true` 强制绕过缓存。 |
| 怎么用 | 常规跳转：`location.assign('/page')`；登录后跳转：`location.replace('/dashboard')`（防止回退到登录页）；刷新：`location.reload()` 或 `location.reload(true)` 强制刷新。 |
| 原理和工作流程 | `assign()` 和 `replace()` 的区别在于是否在浏览器历史栈中创建新条目。`replace()` 替换当前条目，`assign()` 添加新条目。`reload()` 默认从缓存加载，参数 `true` 强制从服务器加载。 |
| 缺点 | `replace()` 会破坏用户的后退预期，需谨慎使用；`reload()` 的参数在不同浏览器中行为可能不一致。 |

---

## 三、history 对象

### 3.1 历史记录操作

| 维度 | 内容 |
|------|------|
| 是什么 | `history` 对象提供对浏览器会话历史的访问，`back()`/`forward()`/`go()` 实现页面导航，`pushState()`/`replaceState()` 在不刷新页面的情况下修改 URL 和历史记录。 |
| 能做什么 | 实现 SPA 路由系统的核心；支持前进/后退导航；通过 `pushState` 添加历史记录；通过 `replaceState` 替换当前历史记录；通过 `state` 属性存储页面状态数据。 |
| 怎么用 | `history.back()` 后退，`history.forward()` 前进，`history.go(-1)` 后退一页；`history.pushState({ page: 1 }, '', '/page1')` 添加记录；`history.replaceState({ page: 2 }, '', '/page2')` 替换记录。 |
| 原理和工作流程 | `pushState` 在历史栈中推入新条目，`replaceState` 替换当前条目。两者都**不触发** `popstate` 事件。用户点击前进/后退按钮或调用 `back()`/`forward()`/`go()` 时才会触发 `popstate`。`popstate` 事件的 `event.state` 携带 `pushState`/`replaceState` 传入的状态对象。 |
| 缺点 | `pushState` 后 URL 是真实路径，刷新页面需要服务端配置 fallback 否则 404；`state` 数据不宜过大（需序列化存储在浏览器中）；`popstate` 在页面首次加载时不触发。 |

### 3.2 SPA 路由原理

| 维度 | 内容 |
|------|------|
| 是什么 | SPA（单页应用）路由通过 `pushState`/`replaceState` 修改 URL，监听 `popstate` 事件匹配路由，渲染对应组件，全程不刷新页面。 |
| 能做什么 | 实现前端路由（Vue Router、React Router 的 History 模式）；支持前进后退导航；保持页面状态；实现路由守卫。 |
| 怎么用 | 定义路由表 → 监听 `popstate` 事件 → 匹配当前路径 → 渲染对应组件。手动导航时调用 `pushState` 并手动触发路由匹配。 |
| 原理和工作流程 | `popstate` 仅在浏览器前进/后退时触发，`pushState`/`replaceState` 不触发。因此需要在导航方法中手动调用路由处理函数。路由匹配基于 `location.pathname`，支持动态路由参数（如 `/user/:id`）。 |
| 缺点 | 需要服务端配置 fallback（所有路径指向 `index.html`）；`state` 在 `popstate` 中可能为 `null`（直接访问页面时）；hash 路由（`#`）兼容性更好但 URL 不美观、SEO 不友好。 |

---

## 四、navigator 对象

### 4.1 浏览器信息检测

| 维度 | 内容 |
|------|------|
| 是什么 | `navigator` 对象包含浏览器的运行环境信息，如用户代理、操作系统、语言偏好、网络状态等。 |
| 能做什么 | 通过 `userAgent` 获取浏览器和操作系统信息；通过 `language` 实现国际化语言适配；通过 `onLine` 检测网络状态；通过 `cookieEnabled` 检测 Cookie 是否启用；通过 `hardwareConcurrency` 获取 CPU 核心数。 |
| 怎么用 | `navigator.userAgent` 获取 UA 字符串；`navigator.language` 获取首选语言；`navigator.onLine` 判断是否联网；`navigator.cookieEnabled` 判断 Cookie 是否可用；监听 `online`/`offline` 事件获取网络状态变化。 |
| 原理和工作流程 | `userAgent` 字符串由浏览器在发起 HTTP 请求时自动附带，可被用户或扩展修改。`onLine` 通过检测浏览器是否连接到网络接口判断，但无法保证该网络能访问外网。推荐使用**特性检测**（`'feature' in obj`）替代 UA 检测。 |
| 缺点 | `userAgent` 不可靠，各浏览器互相伪装，维护正则成本高；`onLine` 仅表示连接了网络接口，不代表能访问外网；`language` 在不同浏览器中返回格式可能不同。 |

---

## 五、screen 对象

### 5.1 屏幕信息

| 维度 | 内容 |
|------|------|
| 是什么 | `screen` 对象提供客户端显示屏幕的物理尺寸信息，包括总宽度/高度和可用宽度/高度。 |
| 能做什么 | 获取屏幕尺寸用于弹窗居中定位；获取可用尺寸（排除任务栏）用于窗口尺寸计算；结合 `devicePixelRatio` 处理高 DPI 屏幕。 |
| 怎么用 | `screen.width` / `screen.height` 获取屏幕总尺寸；`screen.availWidth` / `screen.availHeight` 获取可用尺寸；结合 `(screen.availWidth - w) / 2` 计算居中位置。 |
| 原理和工作流程 | `screen` 返回的是物理像素值，与 CSS 像素不同。在高 DPI 屏幕（如 Retina）上，`screen.width` 可能与 `window.innerWidth` 差距很大，因为 `devicePixelRatio` 不为 1。 |
| 缺点 | 响应式布局不应使用 `screen.width`，应使用 `window.innerWidth` 或 CSS 媒体查询；高 DPI 屏幕下物理像素和 CSS 像素不一致；`availHeight` 在不同操作系统上行为不同。 |

---

## 六、URL 与 URLSearchParams

### 6.1 URL 构造函数

| 维度 | 内容 |
|------|------|
| 是什么 | `URL` 构造函数用于解析和构造 URL，返回一个包含 `protocol`、`hostname`、`pathname`、`search`、`hash` 等属性的 URL 对象。 |
| 能做什么 | 安全地解析 URL 各组成部分；构造带查询参数的 URL；通过 `searchParams` 属性获取 `URLSearchParams` 实例；支持相对 URL 解析（传入 base 参数）。 |
| 怎么用 | `const url = new URL('https://example.com/path?key=value')` 解析；`url.searchParams.get('key')` 获取参数；`url.toString()` 或 `url.href` 获取完整 URL；`new URL('/api', 'https://example.com')` 解析相对 URL。 |
| 原理和工作流程 | `URL` 构造函数内部按 RFC 3986 规范解析 URL 字符串，各部分存入对应属性。`searchParams` 返回的 `URLSearchParams` 对象与 URL 实例保持同步，修改 `searchParams` 会自动更新 `search` 属性。 |
| 缺点 | 在 Node.js 中需 v10+ 才可用；相对 URL 解析时 base 参数需以 `/` 结尾，否则可能解析错误。 |

### 6.2 URLSearchParams

| 维度 | 内容 |
|------|------|
| 是什么 | `URLSearchParams` 是专门用于操作 URL 查询参数的原生 API，支持增删改查和迭代遍历。 |
| 能做什么 | 通过 `get()` 获取单个参数值；通过 `getAll()` 获取同名参数的多个值；通过 `set()` 设置/覆盖参数；通过 `append()` 追加参数；通过 `delete()` 删除参数；通过 `forEach()` 或 `for...of` 遍历参数。 |
| 怎么用 | `const params = new URLSearchParams('a=1&b=2')`；`params.get('a')` -> `'1'`；`params.set('a', '3')` 覆盖；`params.append('b', '4')` 追加；`params.delete('b')` 删除；`params.toString()` -> `'a=3'`。 |
| 原理和工作流程 | `URLSearchParams` 实现了迭代器协议，可用 `for...of` 遍历。`toString()` 自动对参数进行 URL 编码。`Object.fromEntries(params)` 可转为普通对象，但同名参数会丢失（后面的覆盖前面的）。 |
| 缺点 | `Object.fromEntries` 转换会丢失同名参数（需用 `getAll` 处理）；所有值都是字符串类型，需要手动转换数字和布尔值。 |

---

## 七、浏览器扩展 Web APIs

### 7.1 Geolocation API（地理定位）

| 维度 | 内容 |
|------|------|
| 是什么 | `navigator.geolocation` 提供设备地理位置访问能力，基于 GPS、Wi-Fi、IP 地址等定位方式。 |
| 能做什么 | 一次性获取当前位置（`getCurrentPosition`）；持续监听位置变化（`watchPosition`）；根据精度、超时、缓存等配置优化定位策略。 |
| 怎么用 | `navigator.geolocation.getCurrentPosition(success, error, { enableHighAccuracy: true, timeout: 10000 })`；`watchPosition` 返回 `watchId`，用 `clearWatch(id)` 停止监听。 |
| 原理和工作流程 | 浏览器根据 `enableHighAccuracy` 选择合适的定位源（GPS 高精度但耗电，Wi-Fi/IP 低精度但快速）。`error.code` 区分三种错误：`PERMISSION_DENIED`（用户拒绝）、`POSITION_UNAVAILABLE`（不可用）、`TIMEOUT`（超时）。 |
| 缺点 | 要求 HTTPS 安全上下文；`enableHighAccuracy: true` 在高精度模式下耗电快；用户可能拒绝授权；室内定位精度差。 |

### 7.2 Notification API（浏览器通知）

| 维度 | 内容 |
|------|------|
| 是什么 | `Notification` API 允许网页向用户发送系统级桌面通知，即使页面不在前台。 |
| 能做什么 | 发送带标题、正文、图标的通知；通过 `tag` 属性替换重复通知；通过 `requireInteraction` 阻止自动关闭；监听通知点击事件跳转页面。 |
| 怎么用 | 先检查 `Notification.permission`，若为 `default` 则调用 `Notification.requestPermission()` 请求授权；`new Notification('标题', { body: '内容', icon: '/icon.png' })` 发送通知。 |
| 原理和工作流程 | 权限分为三种状态：`default`（未决定）、`granted`（已授权）、`denied`（已拒绝）。`requestPermission()` 返回 Promise。通知点击后可通过 `onclick` 回调聚焦窗口或跳转页面。 |
| 缺点 | 必须先获取用户授权；移动端兼容性有限；`denied` 后无法再次请求（需用户手动在浏览器设置中修改）；通知样式无法自定义。 |

### 7.3 Clipboard API（剪贴板）

| 维度 | 内容 |
|------|------|
| 是什么 | `navigator.clipboard` 提供异步读写系统剪贴板的现代 API，替代传统的 `document.execCommand('copy')`。 |
| 能做什么 | 异步写入文本到剪贴板（`writeText`）；异步读取剪贴板文本（`readText`）；写入任意数据（如图片）到剪贴板（`write` + `ClipboardItem`）；读取任意数据（`read`）。 |
| 怎么用 | `await navigator.clipboard.writeText('hello')` 复制文本；`await navigator.clipboard.readText()` 读取文本；`await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])` 复制图片。 |
| 原理和工作流程 | 基于 Promise 的异步操作，写入/读取剪贴板不阻塞主线程。`readText()` 和 `read()` 在浏览器中可能触发权限提示（Paste 权限）。 |
| 缺点 | 要求 HTTPS 安全上下文或 localhost；`readText()` 需要用户授权（部分浏览器）；旧浏览器不支持，需提供 `execCommand` 降级方案；`write()` 和 `read()` 的兼容性有限。 |

### 7.4 Fullscreen API（全屏）

| 维度 | 内容 |
|------|------|
| 是什么 | Fullscreen API 允许将网页中的任意元素以全屏模式显示，常用于视频播放器、图片查看器、演示文稿等。 |
| 能做什么 | 将指定元素全屏显示（`requestFullscreen`）；退出全屏（`exitFullscreen`）；检测当前全屏状态（`fullscreenElement`）；监听全屏变化（`fullscreenchange` 事件）。 |
| 怎么用 | `element.requestFullscreen()` 进入全屏；`document.exitFullscreen()` 退出全屏；`document.fullscreenElement` 判断是否全屏；`document.addEventListener('fullscreenchange', fn)` 监听变化。 |
| 原理和工作流程 | 全屏 API 需要用户手势触发（如点击事件）。全屏时元素会占据整个屏幕，其余内容不可见。退出全屏可通过 ESC 键或程序调用 `exitFullscreen()`。使用 `:fullscreen` CSS 伪类可适配全屏样式。 |
| 缺点 | 必须由用户手势触发，不能自动全屏；iOS Safari 不支持 `requestFullscreen`（仅支持视频元素的 `webkitEnterFullscreen`）；全屏后 ESC 退出时的键盘事件处理需特别注意。 |

### 7.5 Page Visibility API（页面可见性）

| 维度 | 内容 |
|------|------|
| 是什么 | Page Visibility API 提供检测页面是否可见（用户是否正在查看当前标签页）的能力，用于优化性能和用户体验。 |
| 能做什么 | 通过 `visibilityState` 判断页面是否可见（`visible` / `hidden`）；监听 `visibilitychange` 事件响应状态变化；在隐藏时暂停视频、停止轮询；在可见时恢复操作、刷新数据。 |
| 怎么用 | `document.visibilityState` 获取当前状态；`document.addEventListener('visibilitychange', fn)` 监听变化；隐藏时 `clearInterval` 停止轮询，可见时重新启动并刷新数据。 |
| 原理和工作流程 | 当用户切换标签页、最小化窗口、锁屏时，`visibilityState` 变为 `hidden`。回来时变为 `visible`。浏览器会降低隐藏标签页的定时器频率和资源分配。 |
| 缺点 | `document.hidden` 已废弃，应使用 `visibilityState`；移动端切后台行为在不同浏览器中可能不一致；隐藏时数据不会自动更新，需要手动刷新。 |

---

## 八、综合面试题

### 1. pushState 和 hash 路由的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 SPA 路由的两种实现方式：History API 的 `pushState` 模式和 hash 模式，在 URL 外观、兼容性、服务端配置、SEO 等维度的差异。 |
| 能做什么 | 检验对前端路由底层原理的理解，以及在实际项目中如何选择路由模式。 |
| 怎么用 | pushState：干净 URL（`/page`），需服务端 fallback，SEO 友好，`popstate` 事件；hash：带 `#` URL（`/#/page`），无需服务端配置，全兼容，`hashchange` 事件。 |
| 原理和工作流程 | pushState 修改真实路径，刷新时浏览器会请求该路径（需服务端重定向到 index.html）；hash 修改的是 URL 的 fragment 部分，不会发送到服务器。 |
| 缺点 | 回答时容易忽略 pushState 需要服务端 fallback 配置和 hash 的 SEO 不友好问题。 |

### 2. setTimeout 和 setInterval 的执行机制

| 维度 | 内容 |
|------|------|
| 是什么 | 考查定时器的宏任务机制、最小延迟规则、嵌套限制、以及 `setInterval` 的回调堆积问题。 |
| 能做什么 | 检验对事件循环和定时器底层机制的深入理解。 |
| 怎么用 | `setTimeout` 延迟执行一次，`setInterval` 周期执行。嵌套 5 层以上最小延迟 4ms，后台标签页最小延迟 1000ms。`setInterval` 不考虑回调耗时，可能导致堆积。 |
| 原理和工作流程 | 定时器回调进入宏任务队列，等待当前执行栈和微任务队列清空后才执行。`setInterval` 按固定间隔将回调加入队列，若前一个回调未执行完，会堆积。 |
| 缺点 | 容易忽略 `setInterval` 的回调堆积问题，以及嵌套定时器的最小延迟限制。 |

### 3. 浏览器扩展 Web APIs 的安全上下文要求

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Geolocation、Clipboard、Notification、Fullscreen 等 API 的 HTTPS 要求和权限模型。 |
| 能做什么 | 检验对浏览器安全策略的理解，以及在生产环境中正确配置 HTTPS 的意识。 |
| 怎么用 | Geolocation、Clipboard 要求 HTTPS 或 localhost；Notification 需要用户授权；Fullscreen 需要用户手势触发；Clipboard `readText` 需要额外的粘贴权限。 |
| 原理和工作流程 | 浏览器将功能分为不同安全等级：功能检测（所有环境）、权限请求（需要用户授权）、安全上下文限制（必须 HTTPS）、用户手势限制（必须在事件处理中调用）。 |
| 缺点 | 容易忘记在开发环境（localhost）和生产环境（HTTPS）中 API 可用性的差异；不同浏览器对权限模型的支持程度不同。 |

---

## 九、综合避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 汇总 BOM 与浏览器扩展 API 中 10 个高频错误：定时器未清除、`pushState` 后刷新 404、通知权限未检查、全屏非用户手势触发、地理定位在 HTTP 下不可用、剪贴板 API 未处理异步错误、`visibilitychange` 中未停止轮询、`navigator.onLine` 误判、`setInterval` 回调堆积、`location` 修改后代码继续执行。 |
| 能做什么 | 帮助开发者提前规避常见陷阱，写出更健壮的浏览器交互代码。 |
| 怎么用 | 组件卸载时清除定时器；配置服务端 SPA fallback；先检查 `Notification.permission` 再发送通知；在用户事件中调用全屏；使用 HTTPS；剪贴板操作使用 try-catch；`visibilitychange` 隐藏时停止轮询；结合请求结果判断网络状态；用 `setTimeout` 递归替代 `setInterval`；`location` 跳转后加 `return`。 |
| 原理和工作流程 | 每个错误对应一个底层机制的误解：定时器与事件循环的关系、History API 与服务端路由的关系、浏览器安全策略的分层模型、网络状态检测的局限性。 |
| 缺点 | 部分避坑方案需要理解底层机制才能正确应用，初学者容易机械套用。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./08-BOM与浏览器扩展API.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)