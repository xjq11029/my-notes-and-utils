# 08-BOM与浏览器扩展API

> 模块：02-javascript-core（第2周 JavaScript 核心）
> 难度：★★★ 核心基础
> 前置知识：JavaScript 基础语法、DOM 操作

***

## 一、window 对象

### 1.1 核心概念

`window` 对象是 BOM（Browser Object Model，浏览器对象模型）的核心，代表浏览器窗口。在浏览器中，`window` 既是全局对象，也是所有全局变量和全局函数的宿主。**所有在全局作用域中声明的变量和函数，都会成为 `window` 对象的属性和方法**。

> **生活化类比**：window 就是浏览器这张"桌子"——桌面上摆放的所有东西（全局变量、全局函数）都属于这张桌子，你可以通过 `window.xxx` 来取用。

| 分类 | 核心属性/方法 | 说明 |
|------|-------------|------|
| 全局作用域 | `window.xxx` / 直接 `xxx` | 全局变量和函数自动成为 window 的属性 |
| 定时器 | `setTimeout()` / `setInterval()` | 延迟执行和周期执行 |
| 对话框 | `alert()` / `confirm()` / `prompt()` | 弹出系统对话框 |
| 窗口控制 | `open()` / `close()` | 打开/关闭浏览器窗口 |
| 滚动控制 | `scrollTo()` / `scrollBy()` | 控制页面滚动 |
| 尺寸信息 | `innerWidth` / `innerHeight` | 视口尺寸 |

### 1.2 底层原理

#### 全局作用域与 window 的关系

在浏览器环境中，全局作用域本质上是 `window` 对象。使用 `var` 声明的全局变量会成为 `window` 的属性，而 `let` 和 `const` 声明的变量虽然也在全局作用域中，但不会挂载到 `window` 上。

```javascript
var a = 1;
let b = 2;
const c = 3;

console.log(window.a); // 1 —— var 声明会挂载到 window
console.log(window.b); // undefined —— let 声明不会挂载到 window
console.log(window.c); // undefined —— const 声明不会挂载到 window
```

#### setTimeout / setInterval 的底层机制

`setTimeout` 和 `setInterval` 是浏览器提供的定时器 API，它们将回调函数放入**宏任务队列**（MacroTask Queue），等待事件循环在合适的时机执行。

```javascript
// 定时器的执行时机
console.log('1 - 同步');

setTimeout(() => {
  console.log('2 - setTimeout 0ms'); // 宏任务
}, 0);

Promise.resolve().then(() => {
  console.log('3 - Promise.then'); // 微任务
});

console.log('4 - 同步');

// 输出顺序：1 → 4 → 3 → 2
// setTimeout 虽然延迟为 0，但仍是宏任务，在微任务之后执行
```

#### 定时器的最小延迟

根据 HTML 规范，`setTimeout` 和 `setInterval` 的嵌套层级超过 5 层时，最小延迟会被强制设为 4ms。对于未激活的标签页，浏览器会进一步降低定时器频率（通常最小 1000ms）。

```javascript
// 嵌套定时器延迟展示
let start = Date.now();
let count = 0;

function nestedTimeout() {
  count++;
  const elapsed = Date.now() - start;
  console.log(`第 ${count} 次，间隔 ${elapsed}ms`);
  start = Date.now();
  if (count < 10) {
    setTimeout(nestedTimeout, 0);
  }
}

setTimeout(nestedTimeout, 0);
// 前 5 次：约 0-1ms
// 第 6 次起：至少 4ms 间隔
```

#### 定时器 ID 与清除

`setTimeout` 返回一个数字 ID（定时器句柄），`clearTimeout(id)` 通过该 ID 取消定时器。同理 `setInterval` 返回的 ID 可用 `clearInterval(id)` 取消。

```javascript
const timerId = setTimeout(() => {
  console.log('这个不会执行');
}, 1000);

clearTimeout(timerId); // 立即取消

// setInterval 示例
let count = 0;
const intervalId = setInterval(() => {
  count++;
  console.log(count);
  if (count >= 5) {
    clearInterval(intervalId); // 执行 5 次后停止
  }
}, 500);
```

### 1.3 实战应用

```javascript
// 1. 使用 setTimeout 模拟 setInterval（避免回调堆积）
function safeInterval(fn, delay) {
  let timerId;
  function loop() {
    fn();
    timerId = setTimeout(loop, delay);
  }
  timerId = setTimeout(loop, delay);
  return () => clearTimeout(timerId); // 返回取消函数
}

const cancel = safeInterval(() => {
  console.log('执行中...', new Date().toLocaleTimeString());
}, 1000);

// 5 秒后取消
setTimeout(cancel, 5000);

// 2. 页面滚动到指定位置（平滑滚动）
// 滚动到页面顶部
window.scrollTo({ top: 0, behavior: 'smooth' });

// 向下滚动 500px
window.scrollBy({ top: 500, behavior: 'smooth' });

// 3. 窗口控制（注意：现代浏览器通常拦截自动弹窗）
// 打开新窗口
const newWindow = window.open(
  'https://example.com',
  '_blank',
  'width=800,height=600'
);
// 关闭窗口（仅限通过 open 打开的窗口）
// newWindow.close();

// 4. 对话框的使用场景
// alert：提示信息
// window.alert('操作成功！');

// confirm：确认操作
// const isConfirmed = window.confirm('确定要删除吗？');
// if (isConfirmed) { /* 执行删除 */ }

// prompt：获取用户输入
// const userName = window.prompt('请输入你的名字：', '匿名用户');
// console.log('用户输入了：', userName);
```

### 1.4 常见面试题

**Q1：`setTimeout(fn, 0)` 中的 0 毫秒真的是立即执行吗？**

不是。`setTimeout(fn, 0)` 的含义是"尽快执行"，但回调函数需要等待当前执行栈清空、微任务队列清空后才能执行。即使延迟为 0，回调也是异步的，至少需要等待 4ms（嵌套 5 层以上时）。

**Q2：`let` 声明的全局变量为什么不是 `window` 的属性？**

这是 ES6 规范的设计。`var` 声明的全局变量存储在全局环境记录的 `[[VarRecord]]` 中，该记录与 `window` 对象绑定。而 `let`/`const` 存储在 `[[DeclarativeRecord]]` 中，该记录不绑定到 `window`，实现了更严格的全局作用域隔离。

**Q3：`setInterval` 有什么缺陷？**

`setInterval` 不考虑回调的执行时间，如果回调执行时间大于间隔时间，会导致回调函数堆积（多个回调排队等待执行）。使用 `setTimeout` 递归调用可以确保前一次执行完毕后才开始下一次计时。

### 1.5 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| `setInterval` 回调堆积 | 回调执行次数异常增多 | 回调耗时 > 间隔时间 | 改用 `setTimeout` 递归 |
| 忘记清除定时器 | 组件卸载后定时器仍在运行 | 未在适当时机调用 `clearTimeout` | 在 cleanup 函数中清除 |
| 使用 `var` 声明全局变量 | 全局变量污染 `window` | `var` 自动挂载到 `window` | 使用 `let`/`const` 声明 |
| `alert` 阻塞页面 | 页面卡住无法操作 | `alert` 是同步阻塞操作 | 使用自定义弹窗组件替代 |
| 定时器中 `this` 指向 | `this` 指向 `window` 而非组件 | 定时器回调中的 `this` 默认指向 `window` | 使用箭头函数或 `bind` |

> 📖 **参考链接**：
> - [MDN - Window](https://developer.mozilla.org/zh-CN/docs/Web/API/Window)
> - [MDN - Window.setTimeout()](https://developer.mozilla.org/zh-CN/docs/Web/API/Window/setTimeout)

***

## 二、location 对象

### 2.1 核心概念

`location` 对象提供了当前文档的 URL 信息，并允许通过编程方式导航到新的 URL。它既是 `window` 的属性，也是 `document` 的属性。

| 属性 | 说明 | 示例（URL: `https://example.com:8080/path/page?name=alice#section1`） |
|------|------|------|
| `href` | 完整 URL | `https://example.com:8080/path/page?name=alice#section1` |
| `protocol` | 协议 | `https:` |
| `host` | 主机名 + 端口 | `example.com:8080` |
| `hostname` | 主机名 | `example.com` |
| `port` | 端口号 | `8080` |
| `pathname` | 路径 | `/path/page` |
| `search` | 查询字符串（含 `?`） | `?name=alice` |
| `hash` | 哈希值（含 `#`） | `#section1` |
| `origin` | 协议 + 主机 + 端口 | `https://example.com:8080` |

| 方法 | 说明 |
|------|------|
| `assign(url)` | 导航到新 URL，保留浏览历史 |
| `replace(url)` | 替换当前 URL，不保留历史记录 |
| `reload()` | 重新加载当前页面 |

### 2.2 底层原理

#### location 的导航机制

`location.assign()` 和 `location.replace()` 的区别在于浏览器历史记录的处理：

- `assign()`：创建一个新的历史记录条目，用户可以通过"后退"按钮返回
- `replace()`：替换当前历史记录条目，用户无法通过"后退"按钮返回

直接修改 `location.href` 等同于调用 `assign()`。

```javascript
// 三种导航方式对比
// 方式1：直接修改 href（等同于 assign）
location.href = 'https://example.com';

// 方式2：使用 assign（保留历史记录）
location.assign('https://example.com');

// 方式3：使用 replace（替换历史记录，无法后退）
location.replace('https://example.com');
```

#### reload() 的缓存机制

`location.reload()` 有一个布尔参数：`false`（默认）表示优先从浏览器缓存加载，`true` 表示强制从服务器重新加载（绕过缓存）。

```javascript
// 从缓存加载（默认行为）
location.reload();

// 强制从服务器加载（Ctrl+F5 效果）
// 注意：location.reload(true) 的强制刷新参数为非标准特性，仅 Firefox 支持，不推荐在生产环境使用
location.reload(true);
```

### 2.3 实战应用

```javascript
// 1. 解析 URL 参数（不使用 URLSearchParams 的传统方式）
function getQueryParams() {
  const params = {};
  const search = location.search.substring(1); // 去掉 '?'
  if (!search) return params;

  search.split('&').forEach(pair => {
    const [key, value] = pair.split('=');
    params[decodeURIComponent(key)] = decodeURIComponent(value || '');
  });
  return params;
}

console.log(getQueryParams()); // { name: 'alice', age: '25' }

// 2. 监听 hash 变化（传统方式）
window.addEventListener('hashchange', (e) => {
  console.log('旧 hash:', e.oldURL);
  console.log('新 hash:', e.newURL);
  console.log('当前 hash:', location.hash);
});

// 3. 页面跳转常见场景
// 登录成功后跳转到首页
function loginSuccess() {
  location.replace('/dashboard'); // 用 replace 防止用户回退到登录页
}

// 带参跳转
function goToDetail(id) {
  location.assign(`/detail?id=${id}`);
}

// 4. 刷新当前页面
function refreshPage() {
  location.reload();
}
```

### 2.4 常见面试题

**Q1：`location.href` 和 `location.replace()` 的区别？**

`location.href` 和 `location.assign()` 效果相同，都会在浏览器历史中创建新记录，用户可以点击"后退"返回。`location.replace()` 替换当前历史记录，用户无法后退到前一个页面。登录后跳转到首页建议使用 `replace()`。

**Q2：如何获取 URL 中的查询参数？**

现代方式使用 `URLSearchParams`：`new URLSearchParams(location.search).get('name')`。传统方式需要手动解析 `location.search` 字符串。

### 2.5 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 修改 `location` 属性后代码继续执行 | 跳转后仍有代码执行 | 修改 `location` 不会立即中断脚本 | 跳转后加 `return` 或放在条件分支末尾 |
| 混淆 `host` 和 `hostname` | 端口号处理不一致 | `host` 包含端口号，`hostname` 不包含 | 根据场景选择正确的属性 |
| `reload()` 参数记忆错误 | 缓存策略不符合预期 | 容易忘记默认参数是 `false` | 明确传入 `true` 或 `false` |
| 忘记 `decodeURIComponent` | 中文参数乱码 | URL 查询参数是编码的 | 解析时使用 `decodeURIComponent` |

> 📖 **参考链接**：
> - [MDN - Location](https://developer.mozilla.org/zh-CN/docs/Web/API/Location)
> - [MDN - HTMLAnchorElement](https://developer.mozilla.org/zh-CN/docs/Web/API/HTMLAnchorElement)

***

## 三、history 对象

### 3.1 核心概念

`history` 对象提供了对浏览器会话历史的访问，是 SPA（单页应用）路由系统的核心基础。它允许在用户浏览历史中前进和后退，并支持通过 `pushState` 和 `replaceState` 修改历史记录而不引起页面刷新。

| 属性/方法 | 说明 |
|----------|------|
| `length` | 当前会话的历史记录数量 |
| `state` | 当前历史记录条目的状态对象 |
| `back()` | 后退一页 |
| `forward()` | 前进一页 |
| `go(n)` | 前进/后退 n 页（正数为前进，负数为后退） |
| `pushState(state, title, url)` | 添加一条历史记录（不触发页面刷新） |
| `replaceState(state, title, url)` | 替换当前历史记录（不触发页面刷新） |

### 3.2 底层原理

#### pushState / replaceState 的工作机制

`pushState` 和 `replaceState` 是 HTML5 History API 的核心方法，它们可以在不刷新页面的情况下修改浏览器地址栏 URL 和历史记录。

```javascript
// pushState：添加新历史记录
history.pushState({ page: 1 }, '', '/page1');
// 地址栏变为 /page1，但页面不刷新

// replaceState：替换当前历史记录
history.replaceState({ page: 2 }, '', '/page2');
// 地址栏变为 /page2，但页面不刷新
```

#### popstate 事件

当用户点击浏览器的"前进"或"后退"按钮时（或者调用 `history.back()` / `history.forward()` / `history.go()`），会触发 `popstate` 事件。**注意：`pushState` 和 `replaceState` 不会触发 `popstate` 事件。**

```javascript
window.addEventListener('popstate', (event) => {
  console.log('历史记录变化了！');
  console.log('state 数据：', event.state);
  // 根据 event.state 渲染对应页面内容
});

// pushState 不会触发 popstate
history.pushState({ page: 1 }, '', '/page1');

// 用户点击后退按钮 → 触发 popstate
// history.back() → 触发 popstate
```

#### SPA 路由原理

SPA 路由的核心思路是：监听 URL 变化，根据 URL 匹配对应的组件，渲染到页面中，全程不刷新页面。

```javascript
// 简易 SPA 路由实现
class Router {
  constructor() {
    this.routes = {};
    // 监听 popstate 事件（浏览器前进/后退）
    window.addEventListener('popstate', () => {
      this.handleRoute();
    });
  }

  // 注册路由
  addRoute(path, callback) {
    this.routes[path] = callback;
  }

  // 导航到指定路径
  navigate(path) {
    history.pushState({}, '', path);
    this.handleRoute();
  }

  // 处理当前路由
  handleRoute() {
    const path = location.pathname;
    const callback = this.routes[path] || this.routes['/404'];
    if (callback) callback();
  }
}

// 使用示例
const router = new Router();
router.addRoute('/', () => console.log('首页'));
router.addRoute('/about', () => console.log('关于页'));
router.addRoute('/404', () => console.log('404 页面'));

// 导航
router.navigate('/about'); // 地址栏变为 /about，输出"关于页"
```

### 3.3 实战应用

```javascript
// 1. 监听页面返回事件（常见于移动端 H5）
window.addEventListener('popstate', () => {
  // 用户点击了返回按钮
  console.log('用户返回了上一页');
  // 可以在这里进行页面状态恢复
});

// 2. 阻止用户返回（需谨慎使用）
// 先 push 一个状态，再监听 popstate 阻止
history.pushState(null, '', location.href);
window.addEventListener('popstate', () => {
  history.pushState(null, '', location.href);
  console.log('当前页面不允许返回');
});

// 3. 使用 history.state 实现页面状态保持
// 进入页面时保存状态
const pageState = { scrollTop: 0, filter: 'all' };
history.replaceState(pageState, '');

// 滚动时更新状态
window.addEventListener('scroll', () => {
  history.replaceState(
    { ...history.state, scrollTop: window.scrollY },
    ''
  );
});

// 返回时恢复状态
window.addEventListener('popstate', (e) => {
  if (e.state && e.state.scrollTop) {
    window.scrollTo(0, e.state.scrollTop);
  }
});

// 4. history.go() 的使用
history.go(-1);  // 后退一页，等同于 history.back()
history.go(1);   // 前进一页，等同于 history.forward()
history.go(-2);  // 后退两页
history.go(0);   // 刷新当前页面
```

### 3.4 常见面试题

**Q1：`pushState` 和 `hash` 路由的区别？**

| 对比维度 | pushState（History 模式） | hash 模式 |
|---------|--------------------------|-----------|
| URL 形式 | `/page1`（干净） | `/#/page1`（带 #） |
| 兼容性 | HTML5，IE10+（历史兼容场景，2026 年新项目按现代浏览器基线） | 全兼容 |
| 服务器配置 | 需要服务端配置 fallback | 不需要 |
| 触发事件 | `popstate` | `hashchange` |
| SEO | 友好 | 不友好（# 后内容不被爬虫抓取） |

**Q2：为什么 `pushState` 后服务端需要配置 fallback？**

因为 `pushState` 修改的 URL 是真实路径（如 `/page1`），用户直接访问或刷新该 URL 时，浏览器会向服务器请求 `/page1`，而服务器上可能不存在该物理文件。因此需要配置 fallback，将所有请求都重定向到 `index.html`，由前端路由处理。

### 3.5 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 认为 `pushState` 会触发 `popstate` | 事件监听不生效 | `pushState`/`replaceState` 不触发 `popstate` | 在 `pushState` 后手动调用路由处理函数 |
| 忘记处理 `popstate` 的 `state` 为 `null` | 页面状态丢失 | 直接访问页面时 `event.state` 为 `null` | 始终检查 `event.state` 是否为 `null` |
| History 模式未配置服务端 fallback | 刷新后 404 | 服务端找不到对应路径 | 配置 Nginx/Apache 将所有请求指向 `index.html` |
| `history.state` 数据过大致性能问题 | 页面卡顿 | `state` 数据会被序列化存储 | 仅在 `state` 中存储必要标识，数据从缓存/API 获取 |

> 📖 **参考链接**：
> - [MDN - History API](https://developer.mozilla.org/zh-CN/docs/Web/API/History_API)
> - [MDN - History](https://developer.mozilla.org/zh-CN/docs/Web/API/History)

***

## 四、navigator 对象

### 4.1 核心概念

`navigator` 对象包含了浏览器的相关信息，如浏览器名称、版本、操作系统、语言偏好、网络状态等。它是进行**浏览器特性检测**和**环境判断**的核心工具。

| 属性 | 说明 | 示例值 |
|------|------|--------|
| `userAgent` | 用户代理字符串 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64)...` |
| `platform` | 操作系统平台 | `Win32` |
| `language` | 浏览器首选语言 | `zh-CN` |
| `languages` | 浏览器语言偏好列表 | `['zh-CN', 'zh', 'en']` |
| `onLine` | 是否联网 | `true` / `false` |
| `cookieEnabled` | 是否启用 Cookie | `true` / `false` |
| `hardwareConcurrency` | CPU 核心数 | `8` |
| `maxTouchPoints` | 最大触摸点数 | `0`（桌面）/ `5`（移动端） |

### 4.2 底层原理

#### userAgent 的解析与局限性

`userAgent` 是一个历史悠久的特性，最初用于标识浏览器，但由于历史原因（各浏览器互相伪装），`userAgent` 字符串非常复杂且不可靠。现代开发中推荐使用**特性检测**而非 UA 检测。

```javascript
// userAgent 示例
console.log(navigator.userAgent);
// Chrome: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."

// 常见的 UA 解析
function parseUA() {
  const ua = navigator.userAgent;
  return {
    isMobile: /Mobile|Android|iPhone|iPad/i.test(ua),
    isWeChat: /MicroMessenger/i.test(ua),
    isiOS: /iPhone|iPad|iPod/i.test(ua),
    isAndroid: /Android/i.test(ua),
  };
}

// 特性检测优于 UA 检测
// 差：通过 UA 判断是否支持某个功能
// 好：直接检测功能是否存在
if ('geolocation' in navigator) {
  console.log('支持地理定位');
}
```

#### onLine 的检测机制

`navigator.onLine` 表示浏览器是否连接到网络，但它**并不保证**一定能访问互联网——它仅表示浏览器是否连接到局域网或 Wi-Fi，但该网络可能无法访问外网。

```javascript
// 监听网络状态变化
window.addEventListener('online', () => {
  console.log('网络已连接');
});

window.addEventListener('offline', () => {
  console.log('网络已断开');
});

// 注意：navigator.onLine 的局限性
console.log(navigator.onLine); // true 不一定代表能访问外网
```

### 4.3 实战应用

```javascript
// 1. 浏览器语言国际化
function getBrowserLanguage() {
  // 优先使用 navigator.languages 获取偏好列表
  const lang = navigator.language || navigator.userLanguage || 'en';
  return lang.startsWith('zh') ? 'zh-CN' : 'en';
}

console.log('当前语言：', getBrowserLanguage());

// 2. 检测是否为移动端
function isMobileDevice() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i
    .test(navigator.userAgent);
}

// 3. 检测是否支持 Cookie
if (!navigator.cookieEnabled) {
  console.warn('请启用 Cookie 以获得最佳体验');
}

// 4. 网络状态监听 + 离线提示
function setupNetworkListener() {
  const updateOnlineStatus = () => {
    const status = navigator.onLine ? '在线' : '离线';
    console.log(`网络状态：${status}`);
    // 可以在这里更新 UI 提示
  };

  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
}

// 5. 获取设备信息（用于性能优化）
function getDeviceInfo() {
  return {
    cores: navigator.hardwareConcurrency || 4, // CPU 核心数，用于 Web Worker 数量决策
    memory: navigator.deviceMemory || 4,       // 设备内存（GB），Chrome 支持
    touchSupported: navigator.maxTouchPoints > 0,
    platform: navigator.platform,
  };
}
```

### 4.4 常见面试题

**Q1：为什么不应该依赖 `userAgent` 做浏览器检测？**

1. `userAgent` 字符串可以被用户或浏览器扩展任意修改
2. 各浏览器历史上互相伪装，UA 字符串不可靠
3. 新浏览器和设备不断出现，维护 UA 正则成本高

推荐使用**特性检测**（Feature Detection）来判断浏览器是否支持某个功能。

**Q2：`navigator.onLine` 的局限性是什么？**

`navigator.onLine` 只能检测浏览器是否连接到网络（如 Wi-Fi 已连接），但无法确定该网络是否能访问互联网。例如，连接到路由器但路由器未接入外网时，`onLine` 仍为 `true`。

### 4.5 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 依赖 UA 判断浏览器功能 | 在部分浏览器中功能异常 | UA 字符串不可靠 | 使用特性检测（`'feature' in obj`） |
| 仅用 `navigator.onLine` 判断网络 | 离线逻辑不触发 | 局域网连接但无外网时 `onLine` 为 `true` | 结合实际请求结果判断网络状态 |
| `navigator.language` 格式不一致 | 国际化匹配失败 | 不同浏览器返回格式不同 | 统一转为小写后匹配 |
| 忘记 `cookieEnabled` 检测 | 依赖 Cookie 的功能报错 | 用户禁用了 Cookie | 使用前检查 `navigator.cookieEnabled` |

***

## 五、screen 对象

### 5.1 核心概念

`screen` 对象包含客户端显示屏幕的信息，主要用于获取屏幕的尺寸和可用空间，用于响应式布局、弹窗定位等场景。

| 属性 | 说明 |
|------|------|
| `width` | 屏幕总宽度（像素） |
| `height` | 屏幕总高度（像素） |
| `availWidth` | 屏幕可用宽度（排除任务栏） |
| `availHeight` | 屏幕可用高度（排除任务栏） |
| `colorDepth` | 屏幕颜色深度 |
| `pixelDepth` | 屏幕像素深度（通常等于 colorDepth） |

### 5.2 底层原理

```javascript
// screen 对象属性示例
console.log('屏幕总宽度：', screen.width);        // 如 1920
console.log('屏幕总高度：', screen.height);       // 如 1080
console.log('可用宽度：', screen.availWidth);    // 如 1920（有任务栏时可能更小）
console.log('可用高度：', screen.availHeight);   // 如 1040（排除任务栏）
console.log('颜色深度：', screen.colorDepth);    // 如 24
```

#### 与 window 尺寸的区别

| 对比维度 | `screen` | `window.inner*` | `document.documentElement.client*` |
|---------|----------|-----------------|-----------------------------------|
| 含义 | 物理屏幕尺寸 | 浏览器视口（含滚动条） | 文档可视区域（不含滚动条） |
| 用途 | 弹窗定位、屏幕适配 | 响应式布局 | 内容区域计算 |
| 示例 | `screen.width` | `window.innerWidth` | `document.documentElement.clientWidth` |

### 5.3 实战应用

```javascript
// 1. 弹窗居中显示
function openCenteredWindow(url, width, height) {
  const left = (screen.availWidth - width) / 2;
  const top = (screen.availHeight - height) / 2;
  const features = `width=${width},height=${height},left=${left},top=${top}`;
  return window.open(url, '_blank', features);
}

// 打开一个 800x600 的居中弹窗
// openCenteredWindow('https://example.com', 800, 600);

// 2. 检测屏幕方向
function getScreenOrientation() {
  if (screen.width > screen.height) {
    return '横屏（landscape）';
  }
  return '竖屏（portrait）';
}

// 3. 根据屏幕尺寸调整布局
function adaptLayout() {
  const screenWidth = screen.width;
  if (screenWidth < 768) {
    console.log('小屏幕模式');
  } else if (screenWidth < 1024) {
    console.log('中等屏幕模式');
  } else {
    console.log('大屏幕模式');
  }
}
```

### 5.4 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 用 `screen.width` 做响应式布局 | 在 Retina 屏幕显示异常 | 设备像素比（DPR）导致实际渲染像素不同 | 使用 `window.innerWidth` 或 CSS 媒体查询 |
| 混淆 `availHeight` 和 `height` | 弹窗位置偏下 | 未考虑任务栏高度 | 弹窗定位使用 `availWidth`/`availHeight` |
| 高 DPI 屏幕下 `screen.width` 不准确 | 尺寸计算错误 | 高分屏的实际 CSS 像素与物理像素不同 | 结合 `window.devicePixelRatio` 计算 |

***

## 六、URL 与 URLSearchParams

### 6.1 核心概念

`URL` 和 `URLSearchParams` 是 ES6 引入的浏览器原生 API，用于解析、构造和操作 URL 及其查询参数，替代传统的手动字符串拼接方式。

| API | 说明 |
|-----|------|
| `new URL(url, base)` | 解析 URL 字符串，返回 URL 对象 |
| `new URLSearchParams(query)` | 解析查询字符串，提供迭代器操作 |
| URL 实例属性 | `href`、`protocol`、`hostname`、`pathname`、`search`、`hash` 等 |
| URLSearchParams 实例方法 | `get()`、`set()`、`append()`、`delete()`、`has()`、`toString()`、`forEach()` |

### 6.2 底层原理

#### URL 构造函数

`URL` 构造函数可以接受一个绝对 URL 或相对 URL（配合 base 参数），解析后返回一个包含各部分的 URL 对象。

```javascript
// 解析绝对 URL
const url = new URL('https://example.com:8080/path/page?name=alice&age=25#section1');

console.log(url.protocol);  // 'https:'
console.log(url.hostname);  // 'example.com'
console.log(url.port);      // '8080'
console.log(url.pathname);  // '/path/page'
console.log(url.search);    // '?name=alice&age=25'
console.log(url.hash);      // '#section1'
console.log(url.origin);    // 'https://example.com:8080'

// 解析相对 URL
const baseUrl = 'https://example.com/api/';
const relativeUrl = new URL('users/123', baseUrl);
console.log(relativeUrl.href); // 'https://example.com/api/users/123'
```

#### URLSearchParams 的迭代器特性

`URLSearchParams` 实现了迭代器协议，可以直接用 `for...of` 遍历。

```javascript
const params = new URLSearchParams('name=alice&age=25&hobby=reading&hobby=coding');

// 核心方法
console.log(params.get('name'));       // 'alice'
console.log(params.has('age'));        // true
console.log(params.getAll('hobby'));   // ['reading', 'coding']

params.set('name', 'bob');             // 设置/覆盖
params.append('hobby', 'gaming');      // 追加（同名参数保留）
params.delete('age');                  // 删除
console.log(params.toString());        // 'name=bob&hobby=reading&hobby=coding&hobby=gaming'

// 迭代遍历
for (const [key, value] of params) {
  console.log(`${key}: ${value}`);
}

// 转成普通对象
const paramsObj = Object.fromEntries(params);
console.log(paramsObj); // { name: 'bob', hobby: 'gaming' }
// 注意：同名参数后面的会覆盖前面的
```

### 6.3 实战应用

```javascript
// 1. 构建带查询参数的 URL
function buildUrl(baseUrl, params) {
  const url = new URL(baseUrl);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, value);
    }
  });
  return url.toString();
}

const apiUrl = buildUrl('https://api.example.com/users', {
  page: 1,
  limit: 20,
  status: 'active',
  keyword: null, // 会被过滤掉
});
console.log(apiUrl);
// 'https://api.example.com/users?page=1&limit=20&status=active'

// 2. 提取当前页面的查询参数
function getCurrentQueryParams() {
  return new URLSearchParams(location.search);
}

const searchParams = getCurrentQueryParams();
console.log(searchParams.get('id'));

// 3. 更新 URL 查询参数（不刷新页面）
function updateQueryParam(key, value) {
  const url = new URL(location.href);
  if (value === null || value === undefined) {
    url.searchParams.delete(key);
  } else {
    url.searchParams.set(key, value);
  }
  history.replaceState({}, '', url.toString());
}

// 更新页码
updateQueryParam('page', '3');
// 地址栏变为 ...?page=3

// 4. 解析 URL 中的 hash 参数
function parseHashParams() {
  const hash = location.hash.substring(1); // 去掉 '#'
  return new URLSearchParams(hash);
}

// 5. 数组参数的处理
const params = new URLSearchParams();
params.append('ids', '1');
params.append('ids', '2');
params.append('ids', '3');
console.log(params.toString()); // 'ids=1&ids=2&ids=3'
console.log(params.getAll('ids')); // ['1', '2', '3']
```

### 6.4 常见面试题

**Q1：`URLSearchParams` 和手动解析 URL 查询字符串相比，有什么优势？**

1. 原生 API，无需引入第三方库
2. 自动处理 URL 编码/解码（`encodeURIComponent` / `decodeURIComponent`）
3. 支持同名参数（`getAll`）
4. 支持迭代器遍历
5. 代码更简洁，不易出错

**Q2：如何安全地构建 URL？**

使用 `URL` 构造函数，避免手动拼接字符串。手动拼接容易出现编码错误、参数注入等问题。

### 6.5 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 手动拼接 URL 参数 | 特殊字符编码错误 | 忘记 `encodeURIComponent` | 使用 `URL` 和 `URLSearchParams` |
| `Object.fromEntries` 丢失同名参数 | 同名参数只剩最后一个 | `fromEntries` 会覆盖同名键 | 使用 `getAll()` 处理同名参数 |
| 混淆 `URL` 和 `location` 对象 | 属性访问方式不同 | `URL` 是构造函数，`location` 是对象 | `URL` 适用于解析，`location` 适用于当前页面 |
| 忽略 base URL 参数 | 相对 URL 解析错误 | `new URL('../path', base)` 的 base 需以 `/` 结尾 | 确保 base URL 拼写正确 |

***

## 七、浏览器扩展 Web APIs

### 7.1 Geolocation API（地理定位）

#### 核心概念

`navigator.geolocation` 提供了访问设备地理位置的能力，可以通过 GPS、Wi-Fi、IP 地址等方式获取位置信息。

| 方法 | 说明 |
|------|------|
| `getCurrentPosition(success, error, options)` | 获取当前位置（一次性） |
| `watchPosition(success, error, options)` | 持续监听位置变化，返回 watchId |
| `clearWatch(watchId)` | 停止监听位置变化 |

#### 底层原理

```javascript
// 获取当前位置
navigator.geolocation.getCurrentPosition(
  (position) => {
    console.log('纬度：', position.coords.latitude);
    console.log('经度：', position.coords.longitude);
    console.log('精度：', position.coords.accuracy, '米');
    console.log('海拔：', position.coords.altitude);
    console.log('速度：', position.coords.speed);
    console.log('时间戳：', position.timestamp);
  },
  (error) => {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        console.error('用户拒绝了定位请求');
        break;
      case error.POSITION_UNAVAILABLE:
        console.error('位置信息不可用');
        break;
      case error.TIMEOUT:
        console.error('定位请求超时');
        break;
    }
  },
  {
    enableHighAccuracy: true,  // 高精度模式
    timeout: 10000,             // 超时时间（毫秒）
    maximumAge: 0,              // 缓存时间（0 表示不使用缓存）
  }
);

// 持续监听位置变化
const watchId = navigator.geolocation.watchPosition(
  (position) => {
    console.log('位置更新：', position.coords.latitude, position.coords.longitude);
  },
  (error) => console.error('定位错误：', error),
  { enableHighAccuracy: true, timeout: 5000 }
);

// 停止监听
// navigator.geolocation.clearWatch(watchId);
```

#### 实战应用

```javascript
// 计算两点之间的距离（Haversine 公式）
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // 地球半径（公里）
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return (R * c).toFixed(2); // 返回距离（公里）
}
```

#### 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 未处理用户拒绝定位 | 页面无响应 | 用户拒绝后无错误处理 | 始终提供 `error` 回调 |
| HTTPS 环境检测遗漏 | 定位 API 不工作 | Chrome 等要求 HTTPS | 确保生产环境使用 HTTPS |
| 高精度模式耗电 | 设备电量快速消耗 | GPS 持续工作 | 按需使用 `enableHighAccuracy` |

### 7.2 Notification API（浏览器通知）

#### 核心概念

`Notification` API 允许网页向用户发送系统级桌面通知，即使页面不在前台也能显示。

| 属性/方法 | 说明 |
|----------|------|
| `Notification.permission` | 当前通知权限状态：`granted` / `denied` / `default` |
| `Notification.requestPermission()` | 请求通知权限（返回 Promise） |
| `new Notification(title, options)` | 创建并显示通知 |

#### 底层原理

```javascript
// 请求权限并发送通知
async function sendNotification(title, options = {}) {
  // 检查浏览器是否支持
  if (!('Notification' in window)) {
    console.warn('当前浏览器不支持 Notification API');
    return;
  }

  // 检查权限状态
  if (Notification.permission === 'granted') {
    // 已授权，直接发送
    new Notification(title, {
      body: options.body || '',
      icon: options.icon || '/favicon.ico',
      tag: options.tag || '',       // 相同 tag 的通知会替换
      requireInteraction: options.requireInteraction || false, // 是否不自动关闭
    });
  } else if (Notification.permission !== 'denied') {
    // 未决定，请求权限
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      new Notification(title, options);
    }
  }
}

// 使用示例
sendNotification('新消息', {
  body: '你有一条新的评论',
  icon: '/icon.png',
  tag: 'new-message',
});

// 通知点击事件
const notification = new Notification('提醒', { body: '点击查看详情' });
notification.onclick = () => {
  window.focus();
  // 跳转到对应页面
  // location.href = '/detail';
};
```

#### 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 未请求权限直接创建通知 | 通知不显示 | 必须先获取用户授权 | 使用 `requestPermission()` 获取权限 |
| Service Worker 中未注册事件 | 通知点击无响应 | 需在 SW 中监听 `notificationclick` | 在 SW 中注册 `notificationclick` 事件 |
| 移动端兼容性 | 通知不显示 | 部分移动浏览器不支持 | 检查兼容性，提供降级方案 |

### 7.3 Clipboard API（剪贴板）

#### 核心概念

Clipboard API 提供了异步读写系统剪贴板的能力，替代传统的 `document.execCommand('copy')` 方式。

| 方法 | 说明 |
|------|------|
| `navigator.clipboard.writeText(text)` | 将文本写入剪贴板（返回 Promise） |
| `navigator.clipboard.readText()` | 从剪贴板读取文本（返回 Promise） |
| `navigator.clipboard.write(data)` | 写入任意数据（如图片） |
| `navigator.clipboard.read()` | 读取任意数据 |

#### 底层原理

```javascript
// 复制文本到剪贴板
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    console.log('已复制到剪贴板：', text);
  } catch (err) {
    console.error('复制失败：', err);
    // 降级方案：使用传统方式
    fallbackCopy(text);
  }
}

// 传统降级方案
function fallbackCopy(text) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.select();
  try {
    document.execCommand('copy');
    console.log('已复制（降级方案）');
  } catch (err) {
    console.error('复制失败');
  }
  document.body.removeChild(textarea);
}

// 从剪贴板读取文本
async function readClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    console.log('剪贴板内容：', text);
    return text;
  } catch (err) {
    console.error('读取剪贴板失败：', err);
    return null;
  }
}

// 复制图片到剪贴板
async function copyImage(imageUrl) {
  try {
    const response = await fetch(imageUrl);
    const blob = await response.blob();
    await navigator.clipboard.write([
      new ClipboardItem({
        [blob.type]: blob,
      }),
    ]);
    console.log('图片已复制到剪贴板');
  } catch (err) {
    console.error('复制图片失败：', err);
  }
}
```

#### 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 非 HTTPS 环境调用失败 | 剪贴板 API 不可用 | Clipboard API 要求安全上下文 | 确保使用 HTTPS 或 localhost |
| 未处理权限拒绝 | 写入/读取失败 | 用户拒绝了剪贴板权限 | 使用 try-catch 并提供降级方案 |
| 忘记降级处理 | 旧浏览器无法使用 | Clipboard API 兼容性有限 | 为旧浏览器提供 `execCommand` 降级 |

### 7.4 Fullscreen API（全屏）

#### 核心概念

Fullscreen API 允许将网页中的某个元素以全屏方式显示，常用于视频播放器、图片查看器、演示文稿等场景。

| 方法 | 说明 |
|------|------|
| `element.requestFullscreen()` | 将指定元素全屏显示 |
| `document.exitFullscreen()` | 退出全屏模式 |
| `document.fullscreenElement` | 当前全屏的元素（null 表示非全屏） |
| `document.fullscreenEnabled` | 是否支持全屏 |

#### 实战应用

```javascript
// 全屏切换
async function toggleFullscreen(element = document.documentElement) {
  try {
    if (document.fullscreenElement) {
      // 当前处于全屏模式，退出
      await document.exitFullscreen();
      console.log('已退出全屏');
    } else {
      // 进入全屏
      await element.requestFullscreen();
      console.log('已进入全屏');
    }
  } catch (err) {
    console.error('全屏操作失败：', err);
  }
}

// 监听全屏变化
document.addEventListener('fullscreenchange', () => {
  if (document.fullscreenElement) {
    console.log('进入了全屏模式');
  } else {
    console.log('退出了全屏模式');
  }
});

// 全屏错误处理
document.addEventListener('fullscreenerror', (e) => {
  console.error('全屏请求失败：', e);
});

// 视频全屏播放
const video = document.querySelector('video');
// video.requestFullscreen();

// 指定容器全屏（如代码编辑器）
const editor = document.querySelector('.code-editor');
// editor.requestFullscreen();
```

#### 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 忘记用户手势触发 | 全屏请求被拒绝 | 全屏 API 需要用户手势触发 | 在点击事件等用户交互中调用 |
| 移动端兼容性 | iOS Safari 不支持 | `requestFullscreen` 在 iOS 上不支持 | 使用 `webkitEnterFullscreen`（视频元素） |
| 全屏样式未适配 | 全屏后布局异常 | 全屏后元素尺寸变化 | 使用 `:fullscreen` CSS 伪类适配 |

### 7.5 Page Visibility API（页面可见性）

#### 核心概念

Page Visibility API 提供了检测页面是否可见（即用户是否正在查看当前标签页）的能力，用于优化性能和用户体验。

| 属性/事件 | 说明 |
|----------|------|
| `document.visibilityState` | 当前可见性状态：`visible` / `hidden` |
| `document.hidden` | 是否隐藏（已废弃，推荐用 `visibilityState`） |
| `visibilitychange` 事件 | 可见性状态变化时触发 |

#### 底层原理

```javascript
// 监听页面可见性变化
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    console.log('页面可见 - 用户回来了');
    // 恢复操作：继续播放视频、重新请求数据等
    resumeVideo();
    refreshData();
  } else {
    console.log('页面隐藏 - 用户离开了');
    // 暂停操作：暂停视频、停止轮询等
    pauseVideo();
    stopPolling();
  }
});

// 获取当前状态
console.log('当前状态：', document.visibilityState); // 'visible' 或 'hidden'
```

#### 实战应用

```javascript
// 1. 页面隐藏时暂停视频
const video = document.querySelector('video');
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    video.pause();
  } else {
    video.play();
  }
});

// 2. 页面隐藏时停止轮询，可见时恢复
let pollTimer = null;

function startPolling() {
  pollTimer = setInterval(() => {
    fetch('/api/status').then(res => res.json()).then(data => {
      updateUI(data);
    });
  }, 5000);
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    startPolling();
    // 恢复时立即刷新一次数据
    fetch('/api/status').then(res => res.json()).then(updateUI);
  } else {
    stopPolling();
  }
});

// 3. 页面隐藏时更新标题（如未读消息数）
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    // 用户回来了，清除标题提示
    document.title = '我的应用';
  }
});

// 有新消息时
function onNewMessage(count) {
  if (document.visibilityState === 'hidden') {
    document.title = `【${count}条新消息】我的应用`;
  }
}
```

#### 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 使用 `document.hidden` | 类型检查不准确 | `document.hidden` 已废弃 | 使用 `document.visibilityState` |
| 忘记在恢复时刷新数据 | 页面显示过期数据 | 隐藏期间数据未更新 | 在 `visibilitychange` 可见时重新请求 |
| 未停止定时器 | 后台持续消耗资源 | 隐藏时定时器仍在运行 | 隐藏时清除定时器，可见时恢复 |
| 移动端切后台处理 | 移动端行为不一致 | 不同浏览器对后台标签页处理不同 | 测试主流移动浏览器 |

***

## 八、综合面试题

### Q1：如何实现一个 SPA 路由？

**实现思路**：监听 URL 变化，匹配路由表，渲染对应组件。

```javascript
class SPARouter {
  constructor(routes) {
    this.routes = routes;
    this.currentComponent = null;
    this.init();
  }

  init() {
    // 监听浏览器前进/后退
    window.addEventListener('popstate', () => this.handleRoute());
    // 初始路由
    this.handleRoute();
  }

  handleRoute() {
    const path = location.pathname;
    const route = this.routes.find(r => r.path === path);
    const component = route ? route.component : this.routes.find(r => r.path === '*').component;
    this.render(component);
  }

  navigate(path) {
    history.pushState({}, '', path);
    this.handleRoute();
  }

  render(component) {
    const app = document.getElementById('app');
    app.innerHTML = '';
    app.appendChild(component());
  }
}

// 使用
const router = new SPARouter([
  { path: '/', component: () => { const div = document.createElement('div'); div.textContent = '首页'; return div; } },
  { path: '/about', component: () => { const div = document.createElement('div'); div.textContent = '关于'; return div; } },
  { path: '*', component: () => { const div = document.createElement('div'); div.textContent = '404'; return div; } },
]);
```

### Q2：`hash` 路由和 `history` 路由的优缺点对比？

| 对比维度 | hash 路由 | history 路由 |
|---------|-----------|-------------|
| URL 美观度 | `/#/page` 不美观 | `/page` 干净美观 |
| 兼容性 | 全浏览器兼容 | HTML5，IE10+（历史兼容场景，2026 年新项目按现代浏览器基线） |
| 服务端配置 | 不需要 | 需要 fallback 配置 |
| SEO | 不友好（# 后内容不被抓取） | 友好 |
| 实现方式 | 监听 `hashchange` 事件 | 使用 `pushState` + `popstate` |
| 锚点功能 | 冲突（# 被路由占用） | 正常使用 |

### Q3：如何实现一个带超时和重试的请求函数？

```javascript
async function fetchWithTimeout(url, options = {}, timeout = 5000, retries = 2) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error('请求超时');
    }
    if (retries > 0) {
      console.log(`请求失败，剩余重试次数：${retries}`);
      return fetchWithTimeout(url, options, timeout, retries - 1);
    }
    throw err;
  }
}
```

### Q4：如何实现一个"复制到剪贴板"的功能？

```javascript
async function copyToClipboard(text) {
  // 优先使用 Clipboard API
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return { success: true, message: '已复制到剪贴板' };
    } catch (err) {
      // 降级
    }
  }

  // 降级方案：使用 execCommand
  return new Promise((resolve) => {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    textarea.style.top = '-9999px';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();

    try {
      document.execCommand('copy');
      resolve({ success: true, message: '已复制到剪贴板' });
    } catch (err) {
      resolve({ success: false, message: '复制失败，请手动复制' });
    } finally {
      document.body.removeChild(textarea);
    }
  });
}
```

***

## 九、综合避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 定时器未清除 | 组件卸载后仍执行，导致内存泄漏 | 忘记在 `cleanup` 中清除定时器 | 使用 `useEffect` 返回清除函数或 `beforeUnmount` 钩子 |
| `pushState` 后刷新页面 404 | 直接访问子路由页面 404 | 服务端未配置 SPA fallback | 配置 Nginx/Apache 将所有请求指向 `index.html` |
| 通知 API 未检查权限 | 通知不显示且无报错 | 用户拒绝了通知权限 | 先检查 `Notification.permission` |
| 全屏 API 在非用户手势下调用 | 全屏请求被拒绝 | 浏览器安全策略要求用户手势 | 在 `click` 等用户事件中调用全屏 |
| 地理定位在 HTTP 下不可用 | 定位失败 | Chrome 要求 HTTPS | 使用 HTTPS 或 localhost 开发 |
| 剪贴板 API 未处理异步错误 | 复制失败静默 | Promise 被拒绝但未 catch | 使用 try-catch 并在失败时降级 |
| `visibilitychange` 中未停止轮询 | 后台持续消耗带宽和 CPU | 隐藏时未停止定时器/轮询 | 在 `hidden` 时清除定时器，`visible` 时恢复 |

***

> **学习导航**：
>
> - 返回 [学习路线总览](../README.md)
> - 本模块上一章：[07-正则表达式](./07-正则表达式.md)
> - 实战应用：[企业后台管理系统](../10-project/01-企业后台管理系统实战.md)

***

## 本章学习自检

- [ ] 能说明 `window` 作为全局对象，`var` 和 `let`/`const` 全局声明的差异
- [ ] 理解 `setTimeout` 和 `setInterval` 的执行机制，知道定时器的最小延迟规则
- [ ] 能区分 `location.assign()`、`location.replace()` 和直接修改 `location.href` 的区别
- [ ] 理解 `pushState` / `replaceState` 与 `popstate` 的关系，能实现简易 SPA 路由
- [ ] 能解释 `hash` 路由和 `history` 路由的区别及各自适用场景
- [ ] 知道 `navigator.onLine` 的局限性，能正确监听网络状态变化
- [ ] 能使用 `URL` 和 `URLSearchParams` 安全地解析和构建 URL
- [ ] 能使用 `URLSearchParams` 的 `getAll()` 处理同名参数
- [ ] 能使用 Geolocation API 获取地理位置并处理权限拒绝
- [ ] 能使用 Notification API 发送通知并处理权限
- [ ] 能使用 Clipboard API 实现复制功能并提供降级方案
- [ ] 能使用 Fullscreen API 实现全屏切换
- [ ] 能使用 Page Visibility API 优化页面性能和用户体验
- [ ] 理解各 Web API 的安全上下文（HTTPS）要求