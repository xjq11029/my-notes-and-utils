# 06-JSON与网络请求

> 模块：02-javascript-core（第2周 JavaScript 核心）
> 难度：★★★ 核心基础
> 前置知识：异步编程基础、Promise、ES6 语法

***

## 一、JSON 格式规范

### 1.1 核心概念

**JSON**（JavaScript Object Notation）是一种轻量级的**数据交换格式**，基于 JavaScript 对象字面量语法，但独立于任何编程语言。JSON 是前后端数据通信的事实标准。

JSON 格式的核心规则：

| 规则 | 说明 | 正确示例 | 错误示例 |
|------|------|----------|----------|
| 键名必须用双引号 | 键名必须使用双引号 `"` 包裹，单引号无效 | `"name": "Alice"` | `'name': 'Alice'` |
| 字符串必须用双引号 | 字符串值必须使用双引号，不能使用单引号 | `"hello"` | `'hello'` |
| 不支持注释 | JSON 中不能包含 `//` 或 `/* */` 注释 | — | `// 这是注释` |
| 不支持尾随逗号 | 最后一个元素后不能有逗号 | `[1, 2, 3]` | `[1, 2, 3,]` |
| 数据类型受限 | 只支持 6 种类型 | 见下文 | — |

### 1.2 JSON 支持的数据类型

JSON 只支持以下 6 种数据类型，与 JavaScript 类型存在差异：

| JSON 类型 | 说明 | 示例 | JavaScript 对应 |
|-----------|------|------|-----------------|
| `string` | 双引号包裹的字符串 | `"hello"` | `string` |
| `number` | 整数或浮点数，不支持 NaN/Infinity | `42`, `3.14` | `number` |
| `boolean` | 布尔值 | `true`, `false` | `boolean` |
| `null` | 空值 | `null` | `null` |
| `array` | 有序数组 | `[1, "a", true]` | `Array` |
| `object` | 无序键值对集合 | `{"key": "value"}` | `Object` |

```javascript
// 合法的 JSON 示例
{
  "name": "Alice",
  "age": 25,
  "isStudent": false,
  "hobbies": ["reading", "coding"],
  "address": {
    "city": "Beijing",
    "zip": null
  }
}
```

### 1.3 JSON 与 JavaScript 对象的区别

| 对比维度 | JSON | JavaScript 对象 |
|----------|------|-----------------|
| 键名引号 | 必须用双引号 | 可以不加引号、单引号或双引号 |
| 值类型 | 仅 6 种 | 支持所有 JS 类型 |
| 函数 | 不支持 | 支持方法 |
| undefined | 不支持 | 支持 |
| Date | 不支持（需转为字符串） | 支持 |
| 注释 | 不支持 | 支持（但 ES5 严格模式有限制） |
| 尾随逗号 | 不允许 | 允许（ES5+） |
| 用途 | 数据交换格式 | 编程语言数据结构 |

### 1.4 实战应用

```javascript
// 验证 JSON 字符串是否合法
function isValidJSON(str) {
  try {
    JSON.parse(str);
    return true;
  } catch (e) {
    return false;
  }
}

console.log(isValidJSON('{"name": "Alice"}'));  // true
console.log(isValidJSON("{'name': 'Alice'}"));  // false（单引号）
console.log(isValidJSON('{"name": undefined}')); // false（undefined 不是合法 JSON 值）
```

### 1.5 常见面试题

**Q：JSON 为什么不支持 `undefined` 和函数？**

JSON 的设计目标是跨语言数据交换，`undefined` 和函数是 JavaScript 特有的概念，其他语言（如 Java、Python）没有这些类型。为了保持格式的通用性和互操作性，JSON 只支持语言无关的基本数据类型。

### 1.6 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|----------|------|------|----------|
| 键名使用单引号 | `JSON.parse` 抛出 SyntaxError | JSON 规范要求双引号 | 始终使用双引号包裹键名 |
| 末尾多余逗号 | 解析失败 | JSON 不允许尾随逗号 | 检查并删除最后一个元素后的逗号 |
| 使用 `undefined` 作为值 | 序列化时该属性被丢弃 | `undefined` 不是合法 JSON 值 | 用 `null` 替代 `undefined` |
| 混淆 JSON 对象和 JS 对象 | 直接操作 JSON 字符串如对象 | JSON 是字符串，不是对象 | 先用 `JSON.parse()` 解析 |

> 📖 **参考链接**：
> - [MDN - JSON](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/JSON)
> - [MDN - JSON.stringify()](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify)
> - [MDN - JSON.parse()](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/JSON/parse)

***

## 二、JSON.parse() 与 JSON.stringify()

### 2.1 核心概念

`JSON.parse()` 和 `JSON.stringify()` 是 JavaScript 内置的 JSON 处理方法，负责 JSON 字符串与 JavaScript 对象之间的**双向转换**。

| 方法 | 方向 | 参数 | 返回值 |
|------|------|------|--------|
| `JSON.parse(text[, reviver])` | JSON 字符串 -> JS 对象 | `text`: JSON 字符串；`reviver`: 可选转换函数 | JavaScript 对象 |
| `JSON.stringify(value[, replacer[, space]])` | JS 对象 -> JSON 字符串 | `value`: JS 值；`replacer`: 可选过滤器；`space`: 缩进 | JSON 字符串 |

### 2.2 底层原理

#### JSON.parse() 的 reviver 参数

`reviver` 是一个函数，在解析过程中对每个键值对进行转换。它按**从内到外**的顺序遍历（先处理叶子节点，再处理父节点）。

```javascript
const jsonStr = '{"name":"Alice","birth":"1999-01-15","score":95}';

const result = JSON.parse(jsonStr, (key, value) => {
  // reviver 遍历顺序：从内到外
  console.log(`key: "${key}", value:`, value);

  // 将日期字符串转换为 Date 对象
  if (key === 'birth') {
    return new Date(value);
  }
  // 将分数转换为等级
  if (key === 'score') {
    return value >= 90 ? 'A' : 'B';
  }
  return value;
});

console.log(result.birth instanceof Date); // true
console.log(result.score);                  // "A"

// reviver 遍历输出顺序（从内到外）：
// key: "name", value: Alice
// key: "birth", value: 1999-01-15
// key: "score", value: 95
// key: "", value: {name: "Alice", birth: ..., score: "A"}  <- 最后处理根对象
```

#### JSON.stringify() 的 replacer 参数

`replacer` 可以是**数组**或**函数**：

- **数组**：指定哪些属性需要被序列化（白名单）
- **函数**：对每个属性进行自定义转换，返回值决定是否保留该属性（返回 `undefined` 则丢弃）

```javascript
const user = {
  name: 'Alice',
  age: 25,
  password: '123456',
  email: 'alice@example.com',
};

// replacer 为数组：白名单模式
const safe1 = JSON.stringify(user, ['name', 'email']);
console.log(safe1); // {"name":"Alice","email":"alice@example.com"}

// replacer 为函数：自定义过滤
const safe2 = JSON.stringify(user, (key, value) => {
  if (key === 'password') return undefined; // 过滤敏感字段
  return value;
});
console.log(safe2); // {"name":"Alice","age":25,"email":"alice@example.com"}
```

#### JSON.stringify() 的 space 参数

`space` 控制输出格式的缩进，可以是**数字**（缩进空格数）或**字符串**（自定义缩进符）。

```javascript
const data = { name: 'Alice', skills: ['JS', 'React'] };

// 不传 space：紧凑格式
console.log(JSON.stringify(data));
// {"name":"Alice","skills":["JS","React"]}

// space = 2：缩进 2 个空格
console.log(JSON.stringify(data, null, 2));
// {
//   "name": "Alice",
//   "skills": [
//     "JS",
//     "React"
//   ]
// }

// space = '-> '：自定义缩进符
console.log(JSON.stringify(data, null, '-> '));
// {
// -> "name": "Alice",
// -> "skills": [
// -> -> "JS",
// -> -> "React"
// -> ]
// }
```

### 2.3 实战应用

```javascript
// 1. 使用 reviver 自动转换日期字符串
const apiResponse = '{"createdAt":"2024-01-15T08:30:00Z","updatedAt":"2024-06-20T14:00:00Z"}';

const dateReviver = (key, value) => {
  // 匹配 ISO 8601 日期格式
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T/.test(value)) {
    return new Date(value);
  }
  return value;
};

const parsed = JSON.parse(apiResponse, dateReviver);
console.log(parsed.createdAt instanceof Date); // true

// 2. 使用 replacer 实现深拷贝（有限制）
const deepCopy = (obj) => JSON.parse(JSON.stringify(obj));

const original = { a: 1, b: { c: 2 } };
const copy = deepCopy(original);
copy.b.c = 999;
console.log(original.b.c); // 2（原对象不受影响）

// 3. 大对象 JSON 解析的性能优化
// 对于超大 JSON 字符串，可以分批处理或使用流式解析
const hugeJson = JSON.stringify({ data: new Array(10000).fill(0).map((_, i) => ({ id: i })) });
// 使用 reviver 可以边解析边处理，避免一次性创建所有对象
const ids = [];
JSON.parse(hugeJson, (key, value) => {
  if (key === 'id') ids.push(value);
  return value;
});
```

### 2.4 常见面试题

**Q1：`JSON.parse(JSON.stringify(obj))` 实现深拷贝有什么局限性？**

无法处理 `undefined`、函数、`Symbol`、`Date`（会转为字符串）、`RegExp`（会转为空对象）、`Map`/`Set`、循环引用、`BigInt` 等类型。适合处理纯数据的简单对象。

**Q2：`JSON.stringify` 的 `replacer` 函数中 `this` 指向什么？**

在 `replacer` 函数中，`this` 指向当前正在被序列化的属性所属的父对象。

### 2.5 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|----------|------|------|----------|
| 传入非法的 JSON 字符串给 `parse` | 抛出 SyntaxError | 字符串不符合 JSON 规范 | 用 `try-catch` 包裹，或先用 `isValidJSON` 校验 |
| `replacer` 函数返回 `undefined` 误删属性 | 属性值意外丢失 | 返回 `undefined` 会移除该属性 | 确认不需要移除时返回原值 |
| `space` 参数传入非数字/字符串 | 被静默忽略 | space 只能是数字或字符串 | 确保传入 0-10 的数字或 <=10 字符的字符串 |
| 忘记 `parse` 不会自动转 Date | 日期字段是字符串 | JSON 没有 Date 类型 | 使用 `reviver` 参数转换 |

***

## 三、序列化陷阱

### 3.1 核心概念

`JSON.stringify()` 在序列化 JavaScript 对象时，对某些特殊类型有**非直观的处理行为**，这些行为常常导致数据丢失或意外的结果。

### 3.2 底层原理

#### 序列化规则一览

| 数据类型 | `JSON.stringify()` 行为 | 示例 |
|----------|------------------------|------|
| `undefined` | 属性值被**丢弃**（对象中该属性消失）；数组中转为 `null`；独立值返回 `undefined` | `JSON.stringify({a: undefined})` -> `{}` |
| `Function` | 被**忽略** | `JSON.stringify({fn: function() {}})` -> `{}` |
| `Symbol` | 被**忽略**（包括 Symbol 键名的属性） | `JSON.stringify({[Symbol('id')]: 1})` -> `{}` |
| `Date` | 调用 `toISOString()` 转为 ISO 字符串 | `JSON.stringify({d: new Date()})` -> `{"d":"2024-..."}` |
| `NaN` / `Infinity` | 转为 `null` | `JSON.stringify({n: NaN})` -> `{"n":null}` |
| `RegExp` | 转为 `{}`（空对象） | `JSON.stringify({r: /test/})` -> `{"r":{}}` |
| `Map` / `Set` | 转为 `{}`（空对象） | `JSON.stringify({m: new Map()})` -> `{"m":{}}` |
| `BigInt` | 抛出 `TypeError` | `JSON.stringify({b: 1n})` -> TypeError |
| 循环引用 | 抛出 `TypeError` | `const a={}; a.self=a; JSON.stringify(a)` -> TypeError |
| 数组中的特殊值 | `undefined`/`Function`/`Symbol` 转为 `null` | `JSON.stringify([1, undefined, function(){}])` -> `[1,null,null]` |

#### toJSON() 方法

如果对象定义了 `toJSON()` 方法，`JSON.stringify()` 会调用该方法，用其返回值替代原对象进行序列化。

```javascript
const event = {
  title: 'Conference',
  date: new Date('2024-06-15'),
  // 自定义 toJSON 控制序列化行为
  toJSON() {
    return {
      title: this.title,
      date: this.date.toISOString().split('T')[0], // 只返回日期部分
    };
  },
};

console.log(JSON.stringify(event));
// {"title":"Conference","date":"2024-06-15"}
```

### 3.3 实战应用

```javascript
// 1. 处理循环引用：使用 WeakMap 缓存已序列化对象
function safeStringify(obj, space = 2) {
  const seen = new WeakSet();

  return JSON.stringify(obj, (key, value) => {
    if (typeof value === 'object' && value !== null) {
      if (seen.has(value)) {
        return '[Circular]'; // 循环引用标记
      }
      seen.add(value);
    }
    return value;
  }, space);
}

const a = { name: 'Alice' };
const b = { name: 'Bob', friend: a };
a.friend = b;

console.log(safeStringify(a));
// {"name":"Alice","friend":{"name":"Bob","friend":"[Circular]"}}

// 2. 处理 Date 序列化：保留时区信息
const data = {
  meeting: new Date('2024-06-15T10:00:00+08:00'),
};

// 默认序列化（转为 UTC ISO 字符串）
console.log(JSON.stringify(data));
// {"meeting":"2024-06-15T02:00:00.000Z"}

// 自定义序列化保留本地时间
const localStringify = JSON.stringify(data, (key, value) => {
  if (value instanceof Date) {
    return value.toLocaleString('zh-CN');
  }
  return value;
});
console.log(localStringify);
// {"meeting":"2024/6/15 10:00:00"}

// 3. 处理 Map 序列化
const mapData = new Map([['name', 'Alice'], ['age', 25]]);

// 转换为数组再序列化
const mapAsArray = JSON.stringify([...mapData]);
console.log(mapAsArray); // [["name","Alice"],["age",25]]

// 或转换为普通对象
const mapAsObject = JSON.stringify(Object.fromEntries(mapData));
console.log(mapAsObject); // {"name":"Alice","age":25}
```

### 3.4 常见面试题

**Q1：为什么 `JSON.stringify(undefined)` 返回 `undefined` 而不是 `"undefined"`？**

`JSON.stringify()` 接收 `undefined` 作为独立值时，返回 `undefined`（不是字符串）。这是因为 JSON 规范中 `undefined` 没有对应的表示，引擎选择返回 `undefined` 表示"无法序列化"。但在数组中，`undefined` 会被转为 `null` 以保持数组索引。

**Q2：`toJSON()` 和 `JSON.stringify()` 的 `replacer` 同时存在时，执行顺序是什么？**

`toJSON()` 先执行，返回的结果再传给 `replacer` 处理。即：`toJSON()` -> `replacer` -> 最终序列化。

### 3.5 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|----------|------|------|----------|
| 对象包含循环引用直接序列化 | TypeError | 引擎无法处理无限嵌套 | 使用 `safeStringify` 或第三方库 |
| `Date` 序列化后丢失原始类型 | 反序列化后是字符串，不是 Date 对象 | JSON 没有 Date 类型 | 反序列化时用 `reviver` 转换 |
| `Map`/`Set` 序列化后变为空对象 | 数据丢失 | `JSON.stringify` 不识别 ES6 集合类型 | 先转换为数组再序列化 |
| `BigInt` 序列化直接报错 | TypeError | JSON 不支持 BigInt | 转换为字符串或 Number 再序列化 |

***

## 四、AJAX 概念与 XMLHttpRequest

### 4.1 核心概念

**AJAX**（Asynchronous JavaScript And XML）是一种在**不刷新整个页面**的情况下，与服务器交换数据并更新部分网页的技术。尽管名字中包含 XML，但现代 AJAX 通常使用 JSON 作为数据格式。

AJAX 的核心价值：

| 特性 | 传统 Web 交互 | AJAX 交互 |
|------|-------------|-----------|
| 页面刷新 | 每次请求刷新整个页面 | 无需刷新，局部更新 |
| 用户体验 | 白屏等待，交互中断 | 流畅无感，异步进行 |
| 数据传输 | 整个 HTML 页面 | 仅传输必要数据（JSON） |
| 请求方式 | 同步阻塞 | 异步非阻塞 |
| 典型场景 | 传统表单提交 | 搜索建议、无限滚动、表单验证 |

### 4.2 底层原理：XMLHttpRequest

`XMLHttpRequest`（XHR）是 AJAX 的底层实现，浏览器通过它发起 HTTP 请求。

#### XHR 核心属性和方法

| 属性/方法 | 说明 | 类型 |
|-----------|------|------|
| `open(method, url, async)` | 初始化请求，不发送 | 方法 |
| `send(body)` | 发送请求 | 方法 |
| `readyState` | 请求状态（0-4） | 属性 |
| `onreadystatechange` | 状态变化回调 | 事件 |
| `status` | HTTP 状态码 | 属性 |
| `responseText` | 响应文本 | 属性 |
| `response` | 响应数据（根据 responseType） | 属性 |
| `setRequestHeader(key, value)` | 设置请求头 | 方法 |
| `abort()` | 取消请求 | 方法 |
| `timeout` | 超时时间（毫秒） | 属性 |

#### readyState 状态码

| readyState | 状态 | 说明 |
|------------|------|------|
| `0` | UNSENT | `open()` 尚未调用 |
| `1` | OPENED | `open()` 已调用 |
| `2` | HEADERS_RECEIVED | 已收到响应头 |
| `3` | LOADING | 正在接收响应体 |
| `4` | DONE | 请求完成 |

```javascript
// 原生 XHR 封装
function xhrRequest({ method = 'GET', url, data = null, headers = {}, timeout = 5000 }) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.open(method, url, true); // true 表示异步

    // 设置超时
    xhr.timeout = timeout;
    xhr.ontimeout = () => reject(new Error(`请求超时：${timeout}ms`));

    // 设置请求头
    Object.entries(headers).forEach(([key, value]) => {
      xhr.setRequestHeader(key, value);
    });

    // 监听状态变化
    xhr.onreadystatechange = () => {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (e) {
            resolve(xhr.responseText); // 非 JSON 返回原始文本
          }
        } else {
          reject(new Error(`请求失败：${xhr.status} ${xhr.statusText}`));
        }
      }
    };

    // 网络错误
    xhr.onerror = () => reject(new Error('网络错误'));

    // 发送请求
    if (data && method.toUpperCase() === 'POST') {
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify(data));
    } else {
      xhr.send(data);
    }
  });
}

// 使用示例
xhrRequest({ url: 'https://api.example.com/users' })
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

### 4.3 实战应用

```javascript
// 1. 上传进度监听
function uploadFile(url, file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);

    // 监听上传进度
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        onProgress(percent);
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`上传失败：${xhr.status}`));
      }
    };

    xhr.onerror = () => reject(new Error('网络错误'));
    xhr.open('POST', url);
    xhr.send(formData);
  });
}

// 2. 下载进度监听
function downloadFile(url, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.responseType = 'blob';

    xhr.onprogress = (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        onProgress(percent);
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        resolve(xhr.response);
      } else {
        reject(new Error(`下载失败：${xhr.status}`));
      }
    };

    xhr.open('GET', url);
    xhr.send();
  });
}
```

### 4.4 常见面试题

**Q1：`xhr.onreadystatechange` 和 `xhr.onload` 的区别是什么？**

`onreadystatechange` 在每次 `readyState` 变化时触发（0->1->2->3->4），共触发 4 次；`onload` 仅在请求成功完成（`readyState === 4` 且状态码为成功）时触发一次。`onload` 更简洁，但 `onreadystatechange` 可以监听中间状态。

**Q2：XHR 的 `responseType` 有哪些取值？**

`""`（默认，字符串）、`"text"`、`"json"`、`"blob"`、`"arraybuffer"`、`"document"`。设置 `responseType` 后，从 `xhr.response` 获取对应类型的响应数据。

### 4.5 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|----------|------|------|----------|
| 忘记设置 `async` 参数 | 浏览器卡死 | 同步 XHR 阻塞主线程 | `open` 第三个参数始终传 `true` |
| 跨域请求被拦截 | CORS 错误 | 浏览器同源策略限制 | 服务端设置 CORS 头或使用代理 |
| `readyState` 未检查就读取 `response` | 得到空值或旧值 | 请求未完成 | 确保 `readyState === 4` 再读取 |
| `onreadystatechange` 中 `this` 指向问题 | `this` 不是 XHR 对象 | 回调中 `this` 默认绑定 | 使用闭包中捕获的 `xhr` 变量 |

> 📖 **参考链接**：
> - [MDN - XMLHttpRequest](https://developer.mozilla.org/zh-CN/docs/Web/API/XMLHttpRequest)
> - [MDN - XMLHttpRequest.open()](https://developer.mozilla.org/zh-CN/docs/Web/API/XMLHttpRequest/open)

***

## 五、Fetch API

### 5.1 核心概念

**Fetch API** 是浏览器原生提供的、基于 Promise 的现代网络请求接口，旨在替代 `XMLHttpRequest`。它提供更简洁的语法和更强大的功能。

```javascript
// 基本用法对比
// XHR 方式
const xhr = new XMLHttpRequest();
xhr.open('GET', '/api/data');
xhr.onload = () => console.log(xhr.responseText);
xhr.send();

// Fetch 方式
fetch('/api/data')
  .then(response => response.json())
  .then(data => console.log(data));
```

### 5.2 底层原理

#### fetch() 核心参数

```javascript
fetch(url, {
  method: 'GET',          // 请求方法：GET/POST/PUT/DELETE 等
  headers: {},            // 请求头对象
  body: null,             // 请求体（GET 请求不能有 body）
  mode: 'cors',           // 请求模式：cors/no-cors/same-origin
  credentials: 'same-origin', // 凭证策略：omit/same-origin/include
  cache: 'default',       // 缓存策略
  redirect: 'follow',     // 重定向策略
  referrer: 'client',     // 引用来源
  signal: null,           // AbortSignal 用于取消请求
});
```

#### Response 对象

`fetch()` 返回的 Promise 会 resolve 为一个 `Response` 对象，即使 HTTP 状态码是 404 或 500，Promise 也不会 reject（只有网络错误才会 reject）。

| Response 属性/方法 | 说明 |
|-------------------|------|
| `response.ok` | 布尔值，状态码在 200-299 之间为 `true` |
| `response.status` | HTTP 状态码 |
| `response.statusText` | HTTP 状态文本 |
| `response.headers` | Headers 对象 |
| `response.json()` | 解析响应体为 JSON，返回 Promise |
| `response.text()` | 解析响应体为文本，返回 Promise |
| `response.blob()` | 解析响应体为 Blob，返回 Promise |
| `response.arrayBuffer()` | 解析响应体为 ArrayBuffer，返回 Promise |
| `response.formData()` | 解析响应体为 FormData，返回 Promise |
| `response.clone()` | 克隆 Response 对象（响应体只能读取一次） |

```javascript
// 检查响应状态
fetch('/api/data')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP 错误：${response.status}`);
    }
    return response.json();
  })
  .then(data => console.log(data))
  .catch(err => console.error('请求失败：', err));
```

#### Headers 对象

```javascript
const headers = new Headers({
  'Content-Type': 'application/json',
  'Authorization': 'Bearer token123',
});

// 常用方法
headers.append('X-Custom', 'value');   // 添加
headers.set('X-Custom', 'newValue');   // 覆盖
headers.get('Content-Type');           // 获取
headers.has('Authorization');          // 存在判断
headers.delete('X-Custom');            // 删除

// 遍历
for (const [key, value] of headers) {
  console.log(`${key}: ${value}`);
}
```

### 5.3 实战应用

```javascript
// 1. 通用 Fetch 封装（含错误处理）
async function request(url, options = {}) {
  const defaultOptions = {
    headers: { 'Content-Type': 'application/json' },
  };

  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: { ...defaultOptions.headers, ...options.headers },
  };

  const response = await fetch(url, mergedOptions);

  // 统一错误处理
  if (!response.ok) {
    const errorBody = await response.text().catch(() => '');
    throw new Error(`请求失败 [${response.status}]：${errorBody}`);
  }

  // 根据 Content-Type 自动选择解析方式
  const contentType = response.headers.get('Content-Type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }
  return response.text();
}

// 2. 流式读取（适用于大文件或实时数据）
async function streamFetch(url) {
  const response = await fetch(url);
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let result = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    result += decoder.decode(value, { stream: true });
  }

  return result;
}

// 3. 并发请求控制
async function fetchAll(urls) {
  const promises = urls.map(url => fetch(url).then(r => r.json()));
  const results = await Promise.all(promises);
  return results;
}

// 带重试的请求
async function fetchWithRetry(url, options = {}, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (err) {
      if (i === retries - 1) throw err;
      console.log(`第 ${i + 1} 次重试...`);
      await new Promise(r => setTimeout(r, 1000 * (i + 1))); // 递增延迟
    }
  }
}
```

### 5.4 常见面试题

**Q1：Fetch 和 XHR 的主要区别？**

| 对比维度 | XHR | Fetch |
|----------|-----|-------|
| API 风格 | 事件驱动（回调） | Promise 链式调用 |
| 语法简洁度 | 繁琐 | 简洁 |
| 请求/响应分离 | 在同一对象上 | Request / Response 分离 |
| 进度监听 | 支持（upload/download） | 不支持（需用 ReadableStream） |
| 请求取消 | `xhr.abort()` | AbortController |
| Cookie 默认携带 | 是 | 否（需设置 `credentials`） |
| 错误处理 | 网络错误回调 | 仅网络错误才 reject |
| 浏览器兼容 | 所有浏览器 | IE 不支持 |

**Q2：为什么 `fetch()` 不会在收到 404 时 reject？**

`fetch()` 的设计哲学是：只要网络请求成功完成（收到响应），Promise 就 resolve。HTTP 状态码（如 404、500）代表的是**应用层错误**，而非网络层错误。需要手动检查 `response.ok` 或 `response.status`。

### 5.5 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|----------|------|------|----------|
| 未检查 `response.ok` | 404 响应被当作成功处理 | Fetch 只 reject 网络错误 | 始终检查 `response.ok` 或 `response.status` |
| 响应体被多次读取 | TypeError: Already read | Response body 只能消费一次 | 使用 `response.clone()` 复制 |
| 跨域请求 Cookie 丢失 | 请求未携带 Cookie | 默认 `credentials: 'same-origin'` | 设置 `credentials: 'include'` |
| POST 请求 body 格式错误 | 服务端解析失败 | 未正确序列化 body | JSON 数据使用 `JSON.stringify()` |

> 📖 **参考链接**：
> - [MDN - Fetch API](https://developer.mozilla.org/zh-CN/docs/Web/API/Fetch_API)
> - [MDN - fetch()](https://developer.mozilla.org/zh-CN/docs/Web/API/fetch)

***

## 六、请求取消与超时处理

### 6.1 核心概念

在复杂的 Web 应用中，**请求取消**和**超时处理**是保证用户体验和资源管理的关键机制。常见场景包括：
- 用户快速切换页面，上一个页面的请求已无意义
- 搜索框输入防抖，取消上一次未完成的请求
- 文件上传被用户取消
- 请求超过预设时间返回超时错误

### 6.2 底层原理

#### AbortController 与 AbortSignal

`AbortController` 是浏览器原生提供的请求取消机制，通过 `AbortSignal` 向异步操作发送取消信号。

```javascript
// 创建 AbortController 实例
const controller = new AbortController();
const signal = controller.signal; // 获取对应的 signal

// 发起带 signal 的请求
fetch('/api/data', { signal })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(err => {
    if (err.name === 'AbortError') {
      console.log('请求已被取消');
    } else {
      console.error('其他错误：', err);
    }
  });

// 取消请求
controller.abort(); // 触发 AbortError
```

#### AbortSignal.timeout() 静态方法

`AbortSignal.timeout()` 是 DOM 标准提供的静态方法（Chrome 103+、Firefox 100+ 起支持），可以创建一个在指定时间后自动 abort 的 signal。

```javascript
// 内置超时取消（现代浏览器支持）
async function fetchWithTimeout(url, timeoutMs = 5000) {
  try {
    const response = await fetch(url, {
      signal: AbortSignal.timeout(timeoutMs),
    });
    return await response.json();
  } catch (err) {
    if (err.name === 'TimeoutError') {
      throw new Error(`请求超时：${timeoutMs}ms`);
    }
    throw err;
  }
}
```

#### Promise.race 手动超时

在 `AbortSignal.timeout()` 普及之前，可以使用 `Promise.race` 实现手动超时。

```javascript
// Promise.race 实现超时
function fetchWithRaceTimeout(url, timeoutMs = 5000) {
  return Promise.race([
    fetch(url).then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    }),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error(`请求超时：${timeoutMs}ms`)), timeoutMs)
    ),
  ]);
}
```

### 6.3 实战应用

```javascript
// 1. 搜索防抖 + 请求取消
function createSearchController() {
  let controller = null;

  return async function search(keyword) {
    // 取消上一次未完成的请求
    if (controller) {
      controller.abort();
    }

    controller = new AbortController();

    try {
      const response = await fetch(`/api/search?q=${keyword}`, {
        signal: controller.signal,
      });
      return await response.json();
    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('上次搜索已取消');
      } else {
        throw err;
      }
    }
  };
}

const search = createSearchController();

// 2. 同时支持 AbortController 和 timeout 的请求封装
async function enhancedFetch(url, options = {}) {
  const { timeout = 10000, ...fetchOptions } = options;
  let controller;

  // 如果外部没有传入 signal，创建新的
  if (!fetchOptions.signal) {
    controller = new AbortController();
    fetchOptions.signal = controller.signal;
  }

  // 超时自动取消
  const timeoutId = setTimeout(() => {
    controller?.abort();
  }, timeout);

  try {
    const response = await fetch(url, fetchOptions);
    clearTimeout(timeoutId);
    return response;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error(`请求超时或已被取消 (${timeout}ms)`);
    }
    throw err;
  }
}
```

### 6.4 常见面试题

**Q1：`AbortSignal.timeout()` 和 `Promise.race` 实现超时的区别？**

| 对比维度 | `AbortSignal.timeout()` | `Promise.race` |
|----------|------------------------|----------------|
| 实际请求 | 真正取消底层网络请求 | 请求仍在进行中 |
| 资源释放 | 立即释放网络资源 | 请求继续占用资源 |
| 浏览器支持 | 较新浏览器 | 全部浏览器 |
| 语义清晰度 | 语义明确 | 只是竞争胜出 |

**Q2：同一个 `AbortController` 可以取消多个请求吗？**

可以。将同一个 `signal` 传给多个 `fetch` 调用，调用一次 `controller.abort()` 即可同时取消所有关联的请求。

### 6.5 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|----------|------|------|----------|
| 忘记处理 AbortError | 取消请求后控制台报错 | AbortError 未被 catch | 在 catch 中检查 `err.name === 'AbortError'` |
| `Promise.race` 超时后请求仍在进行 | 内存/网络资源浪费 | race 只是忽略结果，不取消请求 | 使用 AbortController 真正取消 |
| `AbortController` 在 aborted 后复用 | 新的请求立即被取消 | signal 的 aborted 状态已变为 true | 每次创建新的 AbortController |
| 组件卸载后未取消请求 | 内存泄漏、状态更新错误 | React/Vue 组件已卸载但请求仍在进行 | 在 cleanup 函数中调用 `controller.abort()` |

***

## 七、Axios 核心特性

### 7.1 核心概念

**Axios** 是目前最流行的 HTTP 客户端库，基于 Promise，同时支持浏览器和 Node.js 环境。它在原生 API 基础上提供了更丰富的功能。

### 7.2 底层原理

#### 请求/响应拦截器

拦截器是 Axios 最强大的特性之一，允许在请求发送前或响应返回后统一处理。

```javascript
import axios from 'axios';

// 请求拦截器 —— 在请求发送前执行
axios.interceptors.request.use(
  (config) => {
    // 统一添加 Token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // 请求日志
    console.log(`[请求] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 —— 在响应返回后执行
axios.interceptors.response.use(
  (response) => {
    // 统一处理响应数据
    return response.data; // 直接返回 data，调用方无需再 .data
  },
  (error) => {
    // 统一错误处理
    if (error.response) {
      const { status } = error.response;
      switch (status) {
        case 401:
          // Token 过期，跳转登录
          window.location.href = '/login';
          break;
        case 403:
          console.error('没有权限');
          break;
        case 500:
          console.error('服务器错误');
          break;
      }
    }
    return Promise.reject(error);
  }
);
```

#### 实例创建与默认配置

```javascript
// 创建独立实例，避免全局污染
const apiClient = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  // 默认参数
  params: {
    version: 'v1',
  },
});

// 实例级别的拦截器
apiClient.interceptors.request.use((config) => {
  config.headers['X-Request-ID'] = generateUUID();
  return config;
});

// 使用实例
apiClient.get('/users').then(console.log);
apiClient.post('/users', { name: 'Alice' }).then(console.log);
```

#### 取消请求

Axios 支持通过 `AbortController`（现代方式）取消请求。

```javascript
// 现代方式：使用 AbortController
const controller = new AbortController();

axios.get('/api/data', { signal: controller.signal })
  .then(response => console.log(response.data))
  .catch(err => {
    if (axios.isCancel(err)) {
      console.log('请求被取消');
    }
  });

// 取消请求
controller.abort();
```

### 7.3 实战应用

```javascript
// 1. 完整的 Axios 封装方案
import axios from 'axios';

// 创建实例
const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器 —— 含 Token 刷新逻辑
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token);
  });
  failedQueue = [];
};

http.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config;

    // Token 过期，尝试刷新
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // 正在刷新，将请求加入队列
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return http(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { accessToken } = await http.post('/auth/refresh');
        localStorage.setItem('access_token', accessToken);
        processQueue(null, accessToken);
        originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        return http(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError);
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default http;

// 2. 并发请求
async function fetchDashboardData() {
  const [users, posts, stats] = await Promise.all([
    http.get('/users'),
    http.get('/posts'),
    http.get('/stats'),
  ]);
  return { users, posts, stats };
}

// 3. 请求重试拦截器
function createRetryInterceptor(retries = 3, delay = 1000) {
  return (error) => {
    const config = error.config;
    if (!config || !retries) return Promise.reject(error);

    config.__retryCount = config.__retryCount || 0;

    if (config.__retryCount >= retries) {
      return Promise.reject(error);
    }

    config.__retryCount += 1;

    return new Promise(resolve => {
      setTimeout(() => resolve(http(config)), delay * config.__retryCount);
    });
  };
}
```

### 7.4 Axios vs Fetch vs XHR 对比

| 对比维度 | XHR | Fetch | Axios |
|----------|-----|-------|-------|
| API 风格 | 事件回调 | Promise 链式 | Promise 链式 |
| 请求/响应拦截器 | 不支持 | 不支持 | 支持 |
| 自动 JSON 转换 | 手动 | 手动 `response.json()` | 自动 |
| 请求超时 | 原生支持 `xhr.timeout` | 需手动实现 | 原生支持 `timeout` 配置 |
| 请求取消 | `xhr.abort()` | AbortController | AbortController |
| 上传/下载进度 | 原生支持 | 不支持 | 支持 |
| 浏览器兼容性 | 全部 | 除 IE 外全部 | 全部（含 Node.js） |
| 实例创建 | 不支持 | 不支持 | `axios.create()` |
| 默认配置 | 不支持 | 不支持 | 支持 |
| 请求体自动序列化 | 手动 | 手动 | 自动 JSON.stringify |

### 7.5 常见面试题

**Q1：Axios 拦截器的执行顺序是怎样的？**

请求拦截器：**后添加的先执行**（栈结构），响应拦截器：**先添加的先执行**（队列结构）。

```
请求拦截器执行顺序（后进先出）：
  interceptor2.request -> interceptor1.request -> 发送请求

响应拦截器执行顺序（先进先出）：
  收到响应 -> interceptor1.response -> interceptor2.response
```

**Q2：Axios 实例和全局 Axios 的区别？**

全局 Axios 共享同一个配置，修改会影响所有调用。`axios.create()` 创建的实例拥有独立的配置和拦截器，适合多服务端（不同 baseURL、不同鉴权方式）的场景。

### 7.6 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|----------|------|------|----------|
| 拦截器中未 return config | 请求无法发送 | 请求拦截器必须返回 config | 确保 `return config` |
| 响应拦截器直接修改 `response` | 下游代码出错 | 修改了不可预期的数据结构 | 只修改明确的字段，或返回新对象 |
| 多个实例拦截器互相干扰 | 意外行为 | 全局拦截器影响所有实例 | 使用实例级别的拦截器 |
| 忘记处理取消请求的 AbortError | 取消后控制台报错 | 未区分取消和其他错误 | 在错误处理中检查 `axios.isCancel(err)` |

***

> **学习导航**：
>
> - 返回 [学习路线总览](../README.md)
> - 实战应用：[企业后台管理系统](../10-project/01-企业后台管理系统实战.md)

***

## 本章学习自检

- [ ] 能说出 JSON 格式的 5 条核心规则和支持的 6 种数据类型
- [ ] 理解 `JSON.parse()` 的 `reviver` 参数遍历顺序（从内到外）
- [ ] 理解 `JSON.stringify()` 的 `replacer` 参数（数组白名单 / 函数自定义）
- [ ] 能列举 `JSON.stringify()` 对特殊类型（undefined、Function、Symbol、Date、循环引用）的处理行为
- [ ] 理解 `toJSON()` 方法的作用和执行时机
- [ ] 能手写处理循环引用的 `safeStringify` 函数
- [ ] 理解 AJAX 的核心概念和 XHR 的 `readyState` 状态变化
- [ ] 能手写 XHR 的 Promise 封装
- [ ] 理解 Fetch API 与 XHR 的区别，知道 Fetch 不 reject 非 2xx 状态码
- [ ] 能使用 `AbortController` 取消请求
- [ ] 理解 `AbortSignal.timeout()` 和 `Promise.race` 超时的区别
- [ ] 能配置 Axios 的请求/响应拦截器
- [ ] 能使用 `axios.create()` 创建独立实例
- [ ] 能独立完成一个含 Token 刷新、重试、错误处理的 Axios 封装
