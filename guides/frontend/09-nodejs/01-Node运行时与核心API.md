# 01-Node 运行时与核心 API

> 模块：09-nodejs（第9周 Node.js）
> 重点：事件循环、模块机制、Stream、Buffer
> 难度：★★★★☆

---

## 一、核心概念

Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行时环境，它让 JavaScript 能够在服务端运行。Node.js 的核心特征可以概括为四个关键词：

1. **单线程 + 事件驱动**：JavaScript 代码在单个主线程中执行，但通过事件循环（Event Loop）和回调机制实现高并发。
2. **非阻塞 I/O**：所有 I/O 操作（文件读写、网络请求、数据库查询）都是异步的，不会阻塞主线程。
3. **事件循环**：Node.js 的核心调度机制，负责协调异步任务的执行顺序。
4. **跨平台**：通过 libuv 屏蔽不同操作系统的底层差异，实现统一的异步 I/O API。

Node.js 的典型应用场景包括：Web 服务端开发、BFF 中间层、CLI 工具、实时通信（WebSocket）、微服务架构等。

---

## 二、底层原理

### 2.1 Node.js 架构层次

Node.js 的整体架构分为四层，自上而下分别是：

```text
┌──────────────────────────────────────────────┐
│          Node.js 标准库（JavaScript）          │
│   http / fs / path / stream / buffer / ...   │
├──────────────────────────────────────────────┤
│          C++ 绑定层（Node.js Bindings）        │
│   将 JavaScript 调用桥接到 C++ 底层实现         │
├──────────────────────────────────────────────┤
│          底层支撑库                           │
│  ┌──────────┐  ┌──────────────────────────┐  │
│  │  V8 引擎  │  │  libuv（事件驱动 + 异步I/O）│  │
│  │ JS→机器码 │  │  epoll/kqueue/IOCP/线程池  │  │
│  └──────────┘  └──────────────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ OpenSSL  │  │  zlib    │  │ http-parser│  │
│  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────────────────────────────┘
```

- **V8 引擎**：Google 开源的高性能 JavaScript 引擎，负责将 JavaScript 代码编译为机器码执行。Node.js 内置了 V8，因此可以直接运行 JavaScript。
- **libuv**：Node.js 的核心异步 I/O 库，用 C 语言编写，提供跨平台的异步 I/O 能力。它是 Node.js 实现非阻塞 I/O 和事件循环的关键。
- **C++ 绑定层**：将 JavaScript 对核心模块的调用（如 `fs.readFile`）通过 C++ 桥接层转发到底层 C/C++ 库。
- **标准库**：开发者直接使用的 Node.js API，如 `http`、`fs`、`path`、`stream` 等，全部由 JavaScript 编写。

### 2.2 libuv 跨平台异步 I/O 库

libuv 是 Node.js 异步能力的核心。它针对不同类型的 I/O 操作采用不同的处理策略：

| I/O 类型 | 处理方式 | 底层机制 |
|---------|---------|---------|
| 网络 I/O（TCP/UDP） | 操作系统原生异步 API | Linux: epoll / macOS: kqueue / Windows: IOCP |
| 文件 I/O | 线程池（默认 4 线程） | 阻塞 I/O 放入线程池执行，完成后回调 |
| DNS 查询 | 线程池 | `getaddrinfo` 是阻塞调用，放入线程池 |
| 定时器 | 事件循环的 timers 阶段 | 基于 libuv 的定时器堆 |
| 信号处理 | 管道 + 事件循环 | 信号通过管道写入，事件循环读取 |

**为什么文件 I/O 要用线程池？**

操作系统提供的原生异步 I/O API（epoll/kqueue/IOCP）主要适用于网络 I/O（socket）。对于文件 I/O，大多数操作系统并没有真正的异步非阻塞 API（Linux 的 AIO 有诸多限制）。因此 Node.js 采用了线程池方案：将文件 I/O 操作丢到线程池中执行，主线程继续处理其他事件，线程池完成后将回调注册到事件循环中。

可以通过 `UV_THREADPOOL_SIZE` 环境变量调整线程池大小（默认 4）：

```bash
UV_THREADPOOL_SIZE=8 node app.js
```

> **生活化类比：奶茶店前台接单** —— 把 Node.js 想象成一家奶茶店的**前台**：
> - **店员（主线程）**：只有一人，负责接单。对于扫码点单的顾客（网络请求），店员只需在手机上确认（epoll 通知），不需要亲自制作——系统自动处理。
> - **后厨切水果（线程池）**：只有需要手动切水果（文件 I/O）时，才交给后厨（线程池，默认 4 人），店员继续接单。
> - **关键区分**：绝大多数高并发场景（网络请求）用的是系统原生异步 API，不经过线程池。只有文件 I/O 和少数 CPU 密集操作（如加密）才走线程池。这正是 Node.js 能高并发处理网络请求的核心原因。

### 2.3 Node.js 事件循环（Event Loop）详解

事件循环是 Node.js 的"心脏"，它负责调度所有异步任务的执行。Node.js 的事件循环分为 **6 个阶段**，每个阶段维护一个 FIFO 回调队列：

```
   ┌───────────────────────────┐
┌─>│           timers          │  执行 setTimeout/setInterval 回调
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │     pending callbacks     │  执行延迟到下一轮循环的 I/O 回调
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │       idle, prepare       │  内部使用，开发者不直接接触
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │           poll            │  ★ 核心阶段：获取新的 I/O 事件
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │           check           │  执行 setImmediate() 回调
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │      close callbacks      │  执行关闭事件回调（如 socket.on('close')）
│  └─────────────┬─────────────┘
│                 │
└─────────────────┘
```

**各阶段详解**：

1. **timers（定时器阶段）**：执行 `setTimeout()` 和 `setInterval()` 中到期的回调。注意：定时器指定的时间是最小延迟，实际执行时间可能因系统调度而延后。

2. **pending callbacks（待处理回调阶段）**：执行某些系统操作（如 TCP 错误类型）的回调，这些回调被延迟到下一轮循环执行。

3. **idle / prepare**：仅内部使用，开发者无需关心。

4. **poll（轮询阶段）**：**最重要的阶段**。有两个核心职责：
   - 计算应该阻塞和轮询 I/O 的时间
   - 处理 poll 队列中的事件
   
   当 poll 队列为空时：
   - 如果有 `setImmediate()` 回调，则结束 poll 阶段，进入 check 阶段
   - 如果没有 `setImmediate()`，则等待回调被添加到队列中（阻塞等待），然后立即执行

5. **check（检查阶段）**：执行 `setImmediate()` 的回调。`setImmediate()` 是一个特殊的定时器，它在 poll 阶段完成后立即执行。

6. **close callbacks（关闭回调阶段）**：执行关闭事件的回调，如 `socket.on('close', ...)`。

**微任务（Microtask）的执行时机**：

`process.nextTick()` 和 `Promise` 回调属于微任务，它们在**每个事件循环阶段之间**执行，而不是在某个特定阶段内执行。具体来说：

- 每个阶段执行完毕后，会先清空 `process.nextTick` 队列，再清空 `Promise` 微任务队列
- `process.nextTick` 的优先级**高于** `Promise`
- 在微任务执行过程中新产生的微任务，也会在当前轮次被处理

```javascript
// 验证 nextTick 和 Promise 的执行顺序
console.log('start');

process.nextTick(() => {
  console.log('nextTick 1');
  process.nextTick(() => console.log('nextTick 2'));
});

Promise.resolve().then(() => {
  console.log('Promise 1');
  Promise.resolve().then(() => console.log('Promise 2'));
});

console.log('end');

// 输出顺序：
// start
// end
// nextTick 1
// nextTick 2
// Promise 1
// Promise 2
```

**事件循环六个阶段顺序总览**：

```
Node.js 事件循环六个阶段执行顺序（纵向流程）：

         ┌──────────────────────────────────────┐
         │         启动 Node.js 进程              │
         │     初始化 V8、libuv、加载模块          │
         └────────────────┬─────────────────────┘
                          │
         ┌────────────────▼─────────────────────┐
  ┌──────┤      ① timers 定时器阶段              │
  │      │  执行 setTimeout / setInterval 回调    │
  │      │  检查定时器堆，执行到期回调             │
  │      └────────────────┬─────────────────────┘
  │                       │
  │      ┌────────────────▼─────────────────────┐
  │      │  ② pending callbacks 待处理回调阶段    │
  │      │  执行延迟到本轮循环的 I/O 回调          │
  │      │  （如 TCP 错误回调）                    │
  │      └────────────────┬─────────────────────┘
  │                       │
  │      ┌────────────────▼─────────────────────┐
  │      │   ③ idle, prepare 空闲/预备阶段       │
  │      │  Node.js 内部使用，开发者不直接接触     │
  │      │  用于准备 poll 阶段的资源              │
  │      └────────────────┬─────────────────────┘
  │                       │
  │      ┌────────────────▼─────────────────────┐
  │      │      ④ poll 轮询阶段 ★核心★           │
  │      │  ├─ 获取新的 I/O 事件，执行回调         │
  │      │  ├─ 队列不为空：依次执行回调            │
  │      │  ├─ 队列为空且有 setImmediate：        │
  │      │  │    结束 poll，进入 check 阶段        │
  │      │  └─ 队列为空且无 setImmediate：        │
  │      │       阻塞等待新事件到来               │
  │      └────────────────┬─────────────────────┘
  │                       │
  │      ┌────────────────▼─────────────────────┐
  │      │     ⑤ check 检查阶段                  │
  │      │  执行 setImmediate() 回调              │
  │      │  setImmediate 专门在此阶段执行          │
  │      └────────────────┬─────────────────────┘
  │                       │
  │      ┌────────────────▼─────────────────────┐
  │      │  ⑥ close callbacks 关闭回调阶段       │
  │      │  执行 socket.on('close', ...) 等回调   │
  │      │  清理资源、关闭连接                     │
  │      └────────────────┬─────────────────────┘
  │                       │
  └───────────────────────┘
         循环回到 ①（除非队列全空，进程退出）

  微任务执行插入点：每个阶段切换之间
  ├─ ① 清空 process.nextTick 队列（优先级最高）
  └─ ② 清空 Promise 微任务队列
```

**Node.js 事件循环六个阶段状态图**：

```mermaid
%%{init: {'themeVariables': {'fontSize': '16px'}}}%%
stateDiagram-v2
    [*] --> timers
    timers --> pending_callbacks : 执行完到期定时器回调
    pending_callbacks --> idle_prepare : 执行完延迟的 I/O 回调
    idle_prepare --> poll : 内部准备工作完成
    poll --> check : 有 setImmediate 回调时
    poll --> timers : 有到期定时器时
    poll --> poll : 等待新 I/O 事件
    check --> timers : 执行完 setImmediate 回调
    close_callbacks --> timers : 执行完关闭回调

    state timers {
        [*] --> "执行 setTimeout/setInterval 回调"
    }
    state pending_callbacks {
        [*] --> "执行延迟到下一轮的 I/O 回调"
    }
    state idle_prepare {
        [*] --> "libuv 内部准备（仅内部使用）"
    }
    state poll {
        [*] --> "获取新 I/O 事件<br/>执行 I/O 回调"
    }
    state check {
        [*] --> "执行 setImmediate 回调"
    }
    state close_callbacks {
        [*] --> "执行 close 事件回调<br/>（如 socket.on('close')）"
    }
```

> Node.js 事件循环按 **timers -> pending callbacks -> idle/prepare -> poll -> check -> close callbacks** 六个阶段循环执行。poll 阶段是核心，负责监听新 I/O 事件；微任务（nextTick/Promise）在每个阶段切换间隙执行，且 nextTick 优先级高于 Promise。理解事件循环是编写高性能 Node.js 应用的基础。

> 📖 **参考链接**：
> - [Node.js 官方文档 - 事件循环、定时器与 process.nextTick](https://nodejs.org/en/docs/guides/event-loop-timers-and-nexttick)
> - [Node.js 官方文档 - The Node.js Event Loop（英文）](https://nodejs.org/en/docs/guides/event-loop-timers-and-nexttick)

### 2.4 Node.js 事件循环 vs 浏览器事件循环

| 对比维度 | Node.js 事件循环 | 浏览器事件循环 |
|---------|-----------------|---------------|
| 宏任务阶段 | 6 个阶段（timers/poll/check 等），每个阶段有独立队列 | 只有一个宏任务队列，每次取一个执行 |
| 微任务队列 | `process.nextTick` 队列 + `Promise` 队列，nextTick 优先级更高 | 只有 `Promise` 微任务队列（含 MutationObserver） |
| setImmediate | 有，在 check 阶段执行 | 无此 API |
| 执行模型 | 每个阶段执行完所有回调后，再执行微任务 | 每个宏任务执行完后，清空所有微任务 |
| I/O 操作 | 由 libuv 线程池/系统异步 API 处理 | 由浏览器提供的 Web API 处理 |
| Node 11+ 变化 | 与浏览器行为统一：每个宏任务后清空微任务 | 无变化 |

**重要变化**：Node.js 11 之前，微任务在每个阶段之间执行；Node.js 11+ 改为与浏览器一致：每个宏任务执行完后立刻清空微任务队列。这使得 `setTimeout` 和 `setImmediate` 的执行顺序在 Node 11+ 中与浏览器行为更加一致。

```javascript
// Node 11+ 行为与浏览器统一
setTimeout(() => {
  console.log('timeout');
  Promise.resolve().then(() => console.log('promise in timeout'));
}, 0);

setImmediate(() => {
  console.log('immediate');
  Promise.resolve().then(() => console.log('promise in immediate'));
});

// Node 11+ 输出（setTimeout 先触发的情况）：
// timeout
// promise in timeout
// immediate
// promise in immediate
//
// 注意：在主模块中，setTimeout 和 setImmediate 的执行顺序不确定，
// 取决于事件循环启动时的耗时。但无论谁先执行，微任务（Promise）
// 总是在当前宏任务结束后立即执行，这是 Node 11+ 与浏览器统一的行为。
// （在 I/O 回调中，setImmediate 总是先于 setTimeout 执行）
```

### 2.5 模块加载机制

Node.js 支持两种模块系统：**CommonJS**（require）和 **ES Module**（import/export）。

#### CommonJS（require）

CommonJS 是 Node.js 默认的模块系统，特点如下：

- **同步加载**：`require()` 是同步操作，加载完成后才执行后续代码
- **缓存机制**：模块首次加载后会被缓存到 `require.cache`，后续 `require` 直接返回缓存对象
- **值拷贝**：导出的是值的拷贝，模块内部变化不会影响外部已导入的值

```javascript
// math.js - CommonJS 导出
const add = (a, b) => a + b;
const PI = 3.14159;

module.exports = { add, PI };
// 或
exports.add = add;
exports.PI = PI;

// app.js - CommonJS 导入
const math = require('./math');
console.log(math.add(1, 2)); // 3
```

#### ES Module（import/export）

ES Module 是 ECMAScript 官方标准，Node.js 12+ 开始稳定支持：

- **异步加载**：`import` 是异步操作
- **静态分析**：编译时确定模块依赖关系，支持 Tree Shaking
- **值引用**：导出的是值的引用（live binding），模块内部变化会反映到外部
- **使用条件**：需要在 `package.json` 中设置 `"type": "module"`，或使用 `.mjs` 扩展名

```javascript
// math.mjs - ES Module 导出
export const add = (a, b) => a + b;
export const PI = 3.14159;
export default function multiply(a, b) { return a * b; }

// app.mjs - ES Module 导入
import multiply, { add, PI } from './math.mjs';
console.log(add(1, 2)); // 3
```

#### CommonJS vs ES Module 对比

| 对比维度 | CommonJS | ES Module |
|---------|----------|-----------|
| 语法 | `require()` / `module.exports` | `import` / `export` |
| 加载方式 | 同步加载 | 异步加载 |
| 执行时机 | 运行时加载 | 编译时静态分析 |
| 导出方式 | 值拷贝 | 值引用（live binding） |
| Tree Shaking | 不支持 | 支持 |
| 顶层 await | 不支持 | 支持 |
| this 指向 | 指向当前模块 | `undefined` |
| 文件扩展名 | `.js` / `.cjs` | `.mjs` 或 `package.json` 中 `"type": "module"` |
| 动态导入 | `require()` 本身是动态的 | `import()` 函数返回 Promise |

#### require 查找策略

当执行 `require('moduleName')` 时，Node.js 按以下顺序查找：

```
1. 核心模块（如 http、fs、path）
   └─ 找到 → 直接返回核心模块
   └─ 未找到 → 继续

2. 文件模块（路径以 ./ ../ / 开头）
   ├─ 精确匹配文件名
   ├─ 添加 .js 扩展名
   ├─ 添加 .json 扩展名
   ├─ 添加 .node 扩展名
   └─ 未找到 → 当作目录

3. 目录模块
   ├─ 查找 package.json 的 main 字段
   ├─ 查找 index.js
   └─ 查找 index.node

4. node_modules 逐级向上查找
   ├─ 当前目录的 node_modules
   ├─ 父目录的 node_modules
   ├─ ...
   └─ 根目录的 node_modules

5. 全局安装目录
   └─ 仍未找到 → 抛出 MODULE_NOT_FOUND 错误
```

```javascript
// 查看模块缓存
console.log(require.cache);

// 手动清除模块缓存（用于热更新）
delete require.cache[require.resolve('./module')];
```

### 2.6 Stream 流

Stream（流）是 Node.js 中处理流式数据的抽象接口。流的核心优势是**分块处理数据**，避免一次性将大量数据加载到内存中。

#### 四种流类型

| 类型 | 说明 | 典型场景 |
|------|------|---------|
| Readable（可读流） | 从数据源读取数据 | `fs.createReadStream()`、HTTP 请求的 `req` |
| Writable（可写流） | 向目标写入数据 | `fs.createWriteStream()`、HTTP 响应的 `res` |
| Duplex（双工流） | 既可读又可写 | TCP socket、WebSocket |
| Transform（转换流） | 读写过程中对数据进行转换 | `zlib.createGzip()`、`crypto.createCipher()` |

#### 背压机制（Backpressure）

背压是指当**可写流的消费速度跟不上可读流的产出速度**时，数据会在内存中积压，可能导致内存溢出。Node.js 的 `pipe()` 方法自动处理背压：

```javascript
const fs = require('fs');
const zlib = require('zlib');

// pipe 自动处理背压：当可写流繁忙时，自动暂停可读流
fs.createReadStream('input.txt')
  .pipe(zlib.createGzip())       // 压缩
  .pipe(fs.createWriteStream('output.txt.gz'));
```

手动处理背压：

```javascript
const readable = fs.createReadStream('large-file.txt');
const writable = fs.createWriteStream('copy.txt');

readable.on('data', (chunk) => {
  // write() 返回 false 表示内部缓冲区已满，需要暂停读取
  const canContinue = writable.write(chunk);
  if (!canContinue) {
    readable.pause();
    // 等待可写流排空
    writable.once('drain', () => readable.resume());
  }
});

readable.on('end', () => writable.end());
```

#### 流的事件

```javascript
const readable = fs.createReadStream('file.txt');

readable.on('data', (chunk) => {
  // 每次读取到数据块时触发
  console.log(`读取了 ${chunk.length} 字节`);
});

readable.on('end', () => {
  // 数据读取完毕
  console.log('读取完成');
});

readable.on('error', (err) => {
  // 读取过程发生错误
  console.error('读取错误:', err);
});
```

> 📖 **参考链接**：
> - [Node.js 官方文档 - Stream API](https://nodejs.org/api/stream.html)
> - [Node.js 官方文档 - File System API](https://nodejs.org/api/fs.html)
> - [Node.js 官方文档 - Cluster（多进程）](https://nodejs.org/api/cluster.html)

### 2.7 Buffer 缓冲区

Buffer 是 Node.js 中用于处理二进制数据的类，它是 `Uint8Array` 的子类。JavaScript 原生擅长处理字符串，但对二进制数据的处理能力较弱，Buffer 弥补了这一不足。

```javascript
// 创建 Buffer 的三种方式
const buf1 = Buffer.alloc(10);              // 分配 10 字节，初始化为 0（安全）
const buf2 = Buffer.allocUnsafe(10);        // 分配 10 字节，不初始化（快但可能含旧数据）
const buf3 = Buffer.from('Hello Node.js');  // 从字符串创建
const buf4 = Buffer.from([0x48, 0x65, 0x6c, 0x6c, 0x6f]); // 从数组创建

// 编码转换
console.log(buf3.toString('utf8'));     // 'Hello Node.js'
console.log(buf3.toString('base64'));   // 'SGVsbG8gTm9kZS5qcw=='
console.log(buf3.toString('hex'));      // '48656c6c6f204e6f64652e6a73'

// Buffer 操作
const buf = Buffer.alloc(4);
buf.writeUInt32BE(0x12345678, 0);       // 大端序写入
console.log(buf.readUInt32BE(0));        // 0x12345678
console.log(buf.readUInt32LE(0));        // 0x78563412（小端序读取）

// Buffer 合并
const part1 = Buffer.from('Hello ');
const part2 = Buffer.from('World');
const combined = Buffer.concat([part1, part2]);
console.log(combined.toString()); // 'Hello World'
```

> 📖 **参考链接**：
> - [Node.js 官方文档 - Buffer API](https://nodejs.org/api/buffer.html)
> - [Node.js 官方文档 - String Decoder API](https://nodejs.org/api/string_decoder.html)

---

## 三、实战应用

### 3.1 大文件流式处理

```javascript
const fs = require('fs');
const { Transform } = require('stream');

// 创建一个转换流：将每行转大写
const upperCaseTransform = new Transform({
  transform(chunk, encoding, callback) {
    this.push(chunk.toString().toUpperCase());
    callback();
  }
});

// 逐行读取大文件并处理
const readline = require('readline');
async function processLargeFile(filePath) {
  const rl = readline.createInterface({
    input: fs.createReadStream(filePath, { encoding: 'utf8' }),
    crlfDelay: Infinity,
  });

  let lineCount = 0;
  for await (const line of rl) {
    lineCount++;
    // 处理每一行，不需要一次性加载整个文件
    if (lineCount % 10000 === 0) {
      console.log(`已处理 ${lineCount} 行`);
    }
  }
  console.log(`总计 ${lineCount} 行`);
}
```

### 3.2 自定义 Event Loop 调度

```javascript
// 利用 setImmediate 将 CPU 密集型任务拆分为多个小块
function heavyComputation(items, batchSize = 100) {
  return new Promise((resolve) => {
    let index = 0;
    const results = [];

    function processBatch() {
      const end = Math.min(index + batchSize, items.length);
      for (let i = index; i < end; i++) {
        results.push(items[i] * items[i]); // 模拟计算
      }
      index = end;

      if (index < items.length) {
        // 将控制权交还给事件循环，避免阻塞
        setImmediate(processBatch);
      } else {
        resolve(results);
      }
    }

    setImmediate(processBatch);
  });
}
```

### 3.3 模块热更新

```javascript
// 简单的模块热更新实现
const fs = require('fs');
const path = require('path');

function hotRequire(modulePath) {
  // 清除模块缓存
  const resolvedPath = require.resolve(modulePath);
  delete require.cache[resolvedPath];

  // 重新加载模块
  return require(modulePath);
}

// 监听文件变化，实现热更新
fs.watch(path.join(__dirname, 'config.js'), () => {
  const newConfig = hotRequire('./config.js');
  console.log('配置已更新:', newConfig);
});
```

---

## 四、常见面试题

**Q1：Node.js 是单线程的，为什么还能处理高并发？**

Node.js 的 JavaScript 代码确实运行在单线程中，但 I/O 操作（文件读写、网络请求）通过 libuv 的线程池和操作系统异步 API 在后台执行，不会阻塞主线程。当 I/O 完成后，回调被推入事件循环队列，由主线程逐一执行。这种"单线程事件循环 + 非阻塞 I/O"的模型，使得 Node.js 擅长处理 I/O 密集型的高并发场景。

**Q2：`process.nextTick()` 和 `setImmediate()` 的区别？**

- `process.nextTick()`：在当前阶段执行完毕后、下一个阶段开始前执行（微任务），优先级最高。
- `setImmediate()`：在 check 阶段执行（宏任务），在 poll 阶段之后。
- 调用时机：`nextTick` 在当前操作完成后立即执行；`setImmediate` 在事件循环的下一个 check 阶段执行。

**Q3：`setTimeout(fn, 0)` 和 `setImmediate(fn)` 哪个先执行？**

答案取决于调用上下文。在主模块中调用时，受进程性能影响，顺序不确定。但在 I/O 回调中调用时，`setImmediate` 总是先执行（因为 I/O 回调在 poll 阶段，之后直接进入 check 阶段）。

**Q4：Buffer.alloc 和 Buffer.allocUnsafe 的区别？**

- `Buffer.alloc(size)`：分配指定大小的内存并**全部初始化为 0**，安全但较慢。
- `Buffer.allocUnsafe(size)`：分配内存但**不初始化**，可能包含旧数据（敏感信息泄露风险），但速度更快。适合立即覆盖全部内容的场景。

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 在 for 循环中使用 `require` | 模块被重复加载，但实际返回的是缓存 | `require` 有缓存机制，首次加载后缓存 | 将 `require` 放在文件顶部，不要放在循环或函数内 |
| 混淆 `process.nextTick` 和 `setImmediate` | 回调执行顺序不符合预期 | 两者执行阶段不同：nextTick 在本阶段结束时执行，setImmediate 在 check 阶段执行 | 记住：nextTick 更早、优先级更高；setImmediate 在 poll 阶段之后 |
| 大文件使用 `fs.readFile` 而不是流 | 内存溢出或程序崩溃 | `readFile` 一次性将文件全部读入内存 | 使用 `fs.createReadStream` 配合 pipe 流式处理大文件 |
| `Buffer.allocUnsafe` 未覆盖数据 | 可能泄露旧内存中的敏感数据 | `allocUnsafe` 不初始化内存，原内存可能包含密码、密钥等 | 优先使用 `Buffer.alloc`；若用 `allocUnsafe`，确保立即覆盖全部数据 |
| 在 `package.json` 混用 CommonJS 和 ESM | 模块加载失败，报 `ERR_REQUIRE_ESM` 错误 | `"type": "module"` 下 `.js` 文件被当作 ESM，不支持 `require` | 明确使用 `.mjs`（ESM）和 `.cjs`（CommonJS）扩展名 |
| 未处理流错误导致进程崩溃 | 进程因未捕获的 `error` 事件而退出 | 流默认会在 `error` 事件无监听器时抛出异常 | 始终为流绑定 `error` 事件监听器 |
| 在 poll 阶段递归调用 `process.nextTick` | 事件循环被"饿死"，无法进入下一阶段 | nextTick 在当前阶段结束时执行，递归调用会无限循环 | 避免在 nextTick 中递归调用 nextTick；改用 `setImmediate` |
| 线程池被 CPU 密集型任务占满 | 所有异步 I/O 响应变慢 | 线程池默认只有 4 个线程，CPU 密集型任务会阻塞线程池 | 将 CPU 密集型任务交由 Worker Threads 处理，或增大 `UV_THREADPOOL_SIZE` |

---

## 六、Node.js 现代特性

### 6.1 Node.js 内置 `fetch()` API（Node 18+，Node 24 LTS 中完全稳定）

Node.js 18 开始内置了 `fetch()` API，它基于 `undici`（一个高性能 HTTP 客户端库）实现，与浏览器 `fetch()` API 保持高度兼容。

#### 与浏览器 fetch 对比

| 对比维度 | Node.js fetch | 浏览器 fetch |
|---------|--------------|-------------|
| 底层实现 | 基于 undici（HTTP/1.1 + HTTP/2） | 基于浏览器网络栈 |
| CORS 限制 | 无 CORS 限制 | 受同源策略和 CORS 限制 |
| Cookie 管理 | 需手动管理 Cookie 头 | 浏览器自动管理 |
| 缓存 | 无内置缓存 | 支持 HTTP 缓存 |
| 文件上传 | 支持 `file:` 协议读取本地文件 | 不支持本地文件协议 |
| 自定义 Agent | 通过 `dispatcher` 选项自定义 | 无（受浏览器沙箱限制） |
| 代理支持 | 支持 HTTP/HTTPS 代理 | 使用系统代理设置 |
| 超时控制 | 通过 `AbortSignal.timeout()` | 通过 `AbortSignal.timeout()` |

#### 完整代码示例

```javascript
// ========== 基础 GET 请求 ==========
async function basicFetch() {
  try {
    const response = await fetch('https://jsonplaceholder.typicode.com/posts/1');
    if (!response.ok) {
      throw new Error(`HTTP 错误: ${response.status}`);
    }
    const data = await response.json();
    console.log('响应数据:', data);
  } catch (err) {
    console.error('请求失败:', err.message);
  }
}

// ========== POST 请求（发送 JSON） ==========
async function postJson() {
  const response = await fetch('https://jsonplaceholder.typicode.com/posts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer your-token-here',
    },
    body: JSON.stringify({
      title: 'Node.js fetch 示例',
      body: '这是一篇关于 fetch 的文章',
      userId: 1,
    }),
  });
  const data = await response.json();
  console.log('创建成功:', data);
}

// ========== 超时与中断 ==========
async function fetchWithTimeout() {
  const controller = new AbortController();
  // 5 秒后自动中断
  const timeoutId = setTimeout(() => controller.abort(), 5000);

  try {
    const response = await fetch('https://httpbin.org/delay/10', {
      signal: controller.signal,
    });
    console.log('响应:', await response.json());
  } catch (err) {
    if (err.name === 'AbortError') {
      console.error('请求超时，已取消');
    } else {
      console.error('请求失败:', err.message);
    }
  } finally {
    clearTimeout(timeoutId);
  }
}

// Node 20+ 的更简洁写法：使用 AbortSignal.timeout()
async function fetchWithTimeoutV2() {
  try {
    const response = await fetch('https://httpbin.org/delay/10', {
      signal: AbortSignal.timeout(5000), // 5 秒超时，Node 20+
    });
    console.log('响应:', await response.json());
  } catch (err) {
    if (err.name === 'TimeoutError') {
      console.error('请求超时');
    }
  }
}

// ========== 流式读取大文件 ==========
async function streamFetch() {
  const response = await fetch('https://jsonplaceholder.typicode.com/photos');

  // 逐块读取响应体，避免一次性加载全部数据到内存
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let result = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    result += decoder.decode(value, { stream: true });
    console.log(`已读取 ${result.length} 字符`);
  }
  console.log('流式读取完成');
}

// ========== 自定义 Dispatcher（高级用法） ==========
// 需要安装 undici: pnpm add undici
// const { Agent } = require('undici');
// const agent = new Agent({
//   keepAliveTimeout: 10000,
//   keepAliveMaxTimeout: 30000,
//   connections: 128, // 最大并发连接数
// });
// const response = await fetch('https://api.example.com/data', {
//   dispatcher: agent,
// });
```

> **迁移建议**：如果你之前使用 `node-fetch` 或 `axios`，可以逐步迁移到内置 `fetch()`。`fetch()` 在 Node 18+ 中已稳定可用，无需额外安装依赖。对于需要拦截器、请求重试等高级功能的场景，`axios` 仍然是更好的选择。

### 6.2 Web Streams API

Node.js 从 16.5.0 开始实验性支持 Web Streams API，Node 18+ 中已稳定支持。Web Streams API 提供了一套与浏览器一致的标准流处理接口，包括 `ReadableStream`、`WritableStream`、`TransformStream`。

#### 核心概念

```
ReadableStream（可读流） → TransformStream（转换流） → WritableStream（可写流）
     数据源                   中间处理/转换              数据目标
```

#### ReadableStream 完整示例

```javascript
// ========== 创建自定义 ReadableStream ==========
function createIntervalStream(intervalMs = 1000, maxCount = 5) {
  return new ReadableStream({
    start(controller) {
      this.count = 0;
      this.timer = setInterval(() => {
        this.count++;
        if (this.count > maxCount) {
          controller.close(); // 数据发送完毕
          clearInterval(this.timer);
          return;
        }
        const chunk = `数据块 #${this.count} - ${new Date().toISOString()}\n`;
        controller.enqueue(new TextEncoder().encode(chunk));
      }, intervalMs);
    },

    cancel(reason) {
      clearInterval(this.timer);
      console.log('流被取消:', reason);
    },
  });
}

// 消费 ReadableStream
async function consumeReadable() {
  const stream = createIntervalStream(500, 5);
  const reader = stream.getReader();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('流读取完毕');
        break;
      }
      console.log('收到:', new TextDecoder().decode(value));
    }
  } finally {
    reader.releaseLock();
  }
}

// ========== 将 Node.js Readable 转为 Web ReadableStream ==========
// Node 18+ 内置支持
// const fs = require('fs');
// const readable = fs.createReadStream('large-file.txt');
// const webStream = ReadableStream.from(readable);
```

#### WritableStream 完整示例

```javascript
// ========== 创建自定义 WritableStream ==========
function createLoggingWritableStream() {
  return new WritableStream({
    start() {
      this.totalBytes = 0;
      this.chunkCount = 0;
      console.log('可写流已启动');
    },

    write(chunk, controller) {
      this.totalBytes += chunk.byteLength;
      this.chunkCount++;
      console.log(`写入第 ${this.chunkCount} 块，${chunk.byteLength} 字节，累计 ${this.totalBytes} 字节`);
      // 模拟异步写入（如写数据库）
      // return new Promise(resolve => setTimeout(resolve, 100));
    },

    close() {
      console.log(`可写流已关闭，总计写入 ${this.totalBytes} 字节`);
    },

    abort(reason) {
      console.error('可写流异常终止:', reason);
    },
  });
}

// 使用 WritableStream
async function writeToStream() {
  const writable = createLoggingWritableStream();
  const writer = writable.getWriter();

  try {
    await writer.write(new TextEncoder().encode('Hello '));
    await writer.write(new TextEncoder().encode('Web '));
    await writer.write(new TextEncoder().encode('Streams!'));
    await writer.close();
  } catch (err) {
    console.error('写入失败:', err);
  }
}
```

#### TransformStream 完整示例

```javascript
// ========== 创建自定义 TransformStream（数据转换） ==========

// 示例 1：文本转大写转换流
const upperCaseTransform = new TransformStream({
  transform(chunk, controller) {
    const text = new TextDecoder().decode(chunk);
    const upperText = text.toUpperCase();
    controller.enqueue(new TextEncoder().encode(upperText));
  },
});

// 示例 2：JSON 行解析转换流（处理 NDJSON 格式）
const jsonLineParser = new TransformStream({
  transform(chunk, controller) {
    const text = new TextDecoder().decode(chunk);
    const lines = text.split('\n').filter(Boolean);
    for (const line of lines) {
      try {
        const parsed = JSON.parse(line);
        controller.enqueue(new TextEncoder().encode(JSON.stringify(parsed, null, 2) + '\n'));
      } catch {
        // 跳过非 JSON 行
      }
    }
  },
});

// 示例 3：数据压缩/加密转换流（结合 Node.js 原生模块）
// const { Transform } = require('stream');
// const zlib = require('zlib');
// 可以将 Node.js Transform 流桥接到 Web TransformStream

// ========== 管道式组合：Readable → Transform → Writable ==========
async function pipeStreams() {
  // 创建源流
  const source = new ReadableStream({
    start(controller) {
      const data = ['{"name":"Alice"}\n', '{"name":"Bob"}\n', 'not json\n', '{"name":"Charlie"}\n'];
      for (const chunk of data) {
        controller.enqueue(new TextEncoder().encode(chunk));
      }
      controller.close();
    },
  });

  // 创建目标流
  const destination = new WritableStream({
    write(chunk) {
      console.log('输出:', new TextDecoder().decode(chunk));
    },
  });

  // 使用 pipeThrough 链式处理
  await source
    .pipeThrough(jsonLineParser)   // 先解析 JSON
    .pipeThrough(upperCaseTransform) // 再转大写
    .pipeTo(destination);           // 最后输出
}

// 执行
// pipeStreams();
// 输出:
// 输出: {
// 输出:   "NAME": "ALICE"
// 输出: }
// 输出: {
// 输出:   "NAME": "BOB"
// 输出: }
// 输出: {
// 输出:   "NAME": "CHARLIE"
// 输出: }
```

#### Web Streams 与 Node.js Stream 对比

| 对比维度 | Web Streams API | Node.js Stream |
|---------|----------------|----------------|
| 标准来源 | WHATWG 标准（浏览器 + Node.js 通用） | Node.js 专属 API |
| 主要类 | `ReadableStream` / `WritableStream` / `TransformStream` | `Readable` / `Writable` / `Duplex` / `Transform` |
| 消费方式 | `getReader()` / `getWriter()` / `pipeTo()` / `pipeThrough()` | `pipe()` / `on('data')` / `for await...of` |
| 背压机制 | 内置，通过 `controller.desiredSize` 控制 | 内置，通过 `write()` 返回值 + `drain` 事件 |
| 浏览器兼容 | 原生支持 | 不支持（需 polyfill） |
| Node.js 支持 | Node 18+ 稳定 | 所有版本 |
| 互转 | 可通过 `ReadableStream.from()` 从 Node Stream 转换 | 可通过 `stream.Readable.fromWeb()` 从 Web Stream 转换 |

### 6.3 Node.js 20+/24 LTS 新特性速览

> **版本说明**：截至 2026 年 7 月，Node.js 最新 LTS 为 24.x。以下特性从 Node 20 开始引入，在 Node 24 LTS 中已非常成熟。

#### node:test 测试运行器

Node.js 20 内置了 `node:test` 模块，无需安装 Jest、Mocha 等第三方测试框架即可编写和运行测试。

```javascript
// ========== CommonJS 写法 ==========
// test/basic.test.js
const { test } = require('node:test');
const assert = require('node:assert/strict');

// 基础测试
test('同步测试 - 加法', (t) => {
  const result = 1 + 2;
  assert.strictEqual(result, 3);
});

// 异步测试
test('异步测试 - Promise', async (t) => {
  const fetchData = () => Promise.resolve('data');
  const result = await fetchData();
  assert.strictEqual(result, 'data');
});

// 子测试（subtests）
test('用户模块', async (t) => {
  await t.test('创建用户', async (t) => {
    const user = { id: 1, name: 'Alice' };
    assert.strictEqual(user.name, 'Alice');
  });

  await t.test('删除用户', async (t) => {
    const users = ['Alice', 'Bob'];
    const filtered = users.filter(u => u !== 'Alice');
    assert.deepStrictEqual(filtered, ['Bob']);
  });
});

// describe/it 风格（更接近 Jest/Mocha）
const { describe, it } = require('node:test');

describe('用户 API', () => {
  it('应该返回用户列表', () => {
    const users = [{ id: 1 }, { id: 2 }];
    assert.strictEqual(users.length, 2);
  });

  it('应该处理空列表', () => {
    const users = [];
    assert.strictEqual(users.length, 0);
  });
});

// 跳过测试
test('跳过的测试', { skip: true }, (t) => {
  // 不会执行
});

// 仅运行某些测试
test('仅运行的测试', { only: true }, (t) => {
  // 使用 node --test-only 运行
});

// ========== ESM 写法（推荐） ==========
// test/basic.test.mjs 或 package.json 中设置 "type": "module"
// import { test } from 'node:test';
// import assert from 'node:assert/strict';
//
// test('同步测试 - 加法', (t) => {
//   const result = 1 + 2;
//   assert.strictEqual(result, 3);
// });
//
// test('异步测试 - Promise', async (t) => {
//   const fetchData = () => Promise.resolve('data');
//   const result = await fetchData();
//   assert.strictEqual(result, 'data');
// });
//
// // describe/it 风格（ESM）
// // import { describe, it } from 'node:test';
// // describe('用户 API', () => {
// //   it('应该返回用户列表', () => { ... });
// // });

// ========== 运行测试 ==========
// node --test                    # 运行所有测试文件
// node --test test/basic.test.js # 运行指定文件
// node --test --watch            # 监听模式（Node 22+）
// node --test --test-only        # 仅运行 { only: true } 的测试
// node --test --test-reporter spec  # 使用 spec 格式输出
```

#### --watch 模式

Node.js 18 引入了实验性的 `--watch` 模式，Node.js 22 中已稳定，文件变化时自动重启进程：

```bash
# 监听文件变化自动重启
node --watch app.js

# 结合 --watch-path 指定监听目录（Node 22+）
node --watch-path=./src --watch-path=./config app.js

# 监听测试文件
node --test --watch

# 与 nodemon 对比
# nodemon: 需要额外安装，功能更丰富（可配置忽略文件等）
# --watch: 内置，零依赖，Node 22+ 稳定可用
```

#### .env 内置支持

Node.js 20.6.0+ 开始实验性支持 `.env` 文件（Node 22+ 稳定），无需 `dotenv` 包：

```bash
# .env 文件
DATABASE_URL=postgres://localhost:5432/mydb
API_KEY=sk-1234567890
PORT=3000
NODE_ENV=development
```

```javascript
// 方式一：命令行参数
// node --env-file=.env app.js
// 自动加载 .env 文件内容到 process.env

// 方式二：指定多个 .env 文件
// node --env-file=.env --env-file=.env.local app.js

// app.js - 直接使用
console.log(process.env.DATABASE_URL); // postgres://localhost:5432/mydb
console.log(process.env.PORT);         // 3000

// 与 dotenv 对比
// dotenv: 功能更丰富（支持变量展开、模板语法等）
// --env-file: 内置、零依赖、零配置，适合简单场景
```

#### 权限模型（Permission Model）

Node.js 20 引入（实验性，使用 `--experimental-permission` 标志），Node.js 24 LTS 中正式稳定，标志改为 `--permission`。权限模型可以限制进程对文件系统、网络、子进程等资源的访问：

```bash
# 只允许读取 ./data 目录，禁止写入和网络访问
node --permission \
     --allow-fs-read=./data \
     --allow-fs-read=/tmp \
     app.js

# 允许特定网络访问
node --permission \
     --allow-fs-read=./data \
     --allow-net=api.example.com:443 \
     app.js

# 允许子进程
node --permission \
     --allow-child-process \
     app.js

# 允许 Worker Threads
node --permission \
     --allow-worker \
     app.js
```

```javascript
// 在代码中查询权限状态
const permission = process.permission;

// 检查是否有文件读取权限
if (permission.has('fs.read', '/etc/passwd')) {
  // 有权限
} else {
  console.error('无权限读取 /etc/passwd');
}

// 检查是否有网络权限
if (permission.has('net', 'api.example.com')) {
  // 有权限
} else {
  console.error('无权限访问 api.example.com');
}
```

> **安全意义**：权限模型可以在生产环境中限制 Node.js 进程的能力范围，即使应用代码存在漏洞（如路径遍历），攻击者也无法访问超出权限范围的资源。这是 Node.js 在安全领域的重大进步。

> 📖 **参考链接**：
> - [Node.js 官方文档 - Permission Model](https://nodejs.org/api/permissions.html)
> - [Node.js 官方文档 - Process permission API](https://nodejs.org/api/process.html#process_process_permission)

#### node:sqlite — 原生 SQLite 支持（Node.js 24 LTS）

Node.js 24 LTS 引入了原生 `node:sqlite` 模块，无需安装第三方库即可在 Node.js 中操作 SQLite 数据库。

```javascript
import { DatabaseSync } from 'node:sqlite';

// 创建/打开数据库（同步 API）
const db = new DatabaseSync(':memory:');

// 创建表
db.exec(`
  CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
  )
`);

// 插入数据
const insert = db.prepare('INSERT INTO users (name, email) VALUES (?, ?)');
insert.run('张三', 'zhangsan@example.com');
insert.run('李四', 'lisi@example.com');

// 查询数据
const query = db.prepare('SELECT * FROM users WHERE id > ?');
const users = query.all(0);
console.log(users); // [{ id: 1, name: '张三', email: '...' }, ...]

// 关闭连接
db.close();
```

**关键特性**：
- 同步 API（`DatabaseSync`），无需 async/await
- 支持预编译语句（`prepare()`），防止 SQL 注入
- 内存数据库（`:memory:`）和文件数据库均支持
- 内置 WAL 模式支持，读写性能优异

#### TypeScript 原生支持（Node.js 22.6+ / 24 LTS 成熟可用）

Node.js 22.6+ 引入 `--experimental-strip-types` 标志，可直接运行 TypeScript 文件（类型注解在运行时被忽略）。Node.js 23.6+ 默认启用原生 TypeScript 支持。

```bash
# Node.js 22.6+：使用 --experimental-strip-types 标志
node --experimental-strip-types app.ts

# Node.js 23.6+：直接运行 TypeScript 文件（默认启用）
node app.ts
```

```typescript
// app.ts — 可以直接用 Node.js 运行
interface User {
  name: string;
  age: number;
}

function greet(user: User): string {
  return `Hello, ${user.name}!`;
}

console.log(greet({ name: 'World', age: 42 }));
```

**限制与注意事项**：
- 仅剥离类型注解（type stripping），不进行类型检查
- 不支持 TypeScript 特有语法（如 enum、namespace、参数属性等）
- 不支持 `.tsx` 文件
- 建议：开发时仍使用 `tsc --noEmit` 进行类型检查，运行时使用 Node.js 原生支持

#### SEA（Single Executable Application）— Node.js 21+

Node.js 21+ 支持将 Node.js 应用打包为单个可执行文件（SEA），无需安装 Node.js 运行时即可在目标系统上运行。

```bash
# 创建 SEA 配置
echo '{ "main": "app.js", "output": "sea-prep.blob" }' > sea-config.json

# 生成 blob 文件
node --experimental-sea-config sea-config.json

# 复制 Node.js 可执行文件
node -e "require('fs').copyFileSync(process.execPath, 'my-app.exe')"

# 将 blob 注入到可执行文件中（需使用 postject 工具）
pnpm dlx postject my-app.exe NODE_SEA_BLOB sea-prep.blob --sentinel-fuse NODE_SEA_FUSE_fce680ab2cc467b6e072b8b5df1996b2

# 运行
./my-app.exe
```

**适用场景**：CLI 工具分发、内部工具部署、无需 Node.js 环境的场景。

---

> **学习导航**：
> - 返回 [学习路线总览](../README.md)
> - 本模块其他文件：[02-Web框架与BFF层](./02-Web框架与BFF层.md) | [03-Node.js笔面试题集](./03-Node.js笔面试题集.md) | [04-数据库与ORM](./04-数据库与ORM.md)
> - 进阶学习：[企业后台管理系统](../10-project/01-企业后台管理系统实战.md)

---

## 本章学习自检

- [ ] 能够画出 Node.js 的四层架构图并说明每层的作用
- [ ] 理解 libuv 针对不同 I/O 类型的处理策略（网络 I/O 用系统异步 API，文件 I/O 用线程池）
- [ ] 能够完整描述 Node.js 事件循环的 6 个阶段及其职责
- [ ] 理解 `process.nextTick` 和 `Promise` 微任务的执行时机和优先级
- [ ] 能够对比 Node.js 事件循环和浏览器事件循环的差异
- [ ] 理解 CommonJS 和 ES Module 的核心区别（同步/异步、值拷贝/值引用、Tree Shaking）
- [ ] 能够描述 `require` 的完整查找策略
- [ ] 理解 Stream 四种类型和背压机制的原理
- [ ] 掌握 Buffer 的创建方式和编码转换
- [ ] 能够解释 Node.js 单线程如何实现高并发
- [ ] 掌握 Node.js 内置 `fetch()` API 的基本用法（GET/POST/超时/流式读取），理解与浏览器 fetch 的差异
- [ ] 理解 Web Streams API（ReadableStream / WritableStream / TransformStream）的创建和管道组合
- [ ] 了解 Node.js 20+ 核心新特性：`node:test` 测试运行器、`--watch` 模式、`.env` 内置支持、权限模型
- [ ] 了解 Node.js 24 LTS 原生 `node:sqlite` 模块的基本用法（同步 API、预编译语句、WAL 模式）
- [ ] 了解 Node.js 原生 TypeScript 支持（`--experimental-strip-types`、适用场景与限制）
- [ ] 了解 SEA（单可执行文件）的打包流程和适用场景


## 补充：日志与配置管理

### 1. 日志库（winston / pino）

- 日志的重要性：问题排查、性能监控、审计追溯
- 日志级别：error（严重错误需立即处理）、warn（警告信息）、info（关键业务流程）、debug（调试信息）、verbose/trace（详细追踪）
- winston 日志库：创建 logger、定义 transports（Console/File/Http）、日志格式（JSON/文本/自定义）、日志级别过滤
- pino 日志库：极高性能（异步写入）、pino-pretty 美化输出、与 winston 性能对比
- 代码示例：winston 完整配置示例（多 transport、按级别分文件）、pino 基本用法

### 2. 环境变量与配置管理（dotenv）

dotenv 是一个零依赖的 npm 包，用于从 `.env` 文件加载环境变量到 `process.env`。它是 Node.js 项目中最常用的配置管理方案。

#### 基本用法

```bash
# 安装 dotenv
pnpm add dotenv
```

```env
# .env 文件（不要提交到 Git）
DATABASE_URL=mysql://user:pass@localhost:3306/mydb
API_KEY=sk-1234567890
PORT=3000
NODE_ENV=development

# 支持注释
# 引号是可选的，但包含特殊字符时建议使用
SECRET_KEY="my-secret-key-with-special-chars"
```

```javascript
// app.js - 在入口文件最顶部加载 dotenv
require('dotenv').config();
// 或使用 ES Module：
// import 'dotenv/config';

console.log(process.env.DATABASE_URL); // mysql://user:pass@localhost:3306/mydb
console.log(process.env.PORT);          // 3000

// 如果 .env 文件不在默认位置，可以指定路径
require('dotenv').config({ path: '.env.production' });
```

#### 多环境配置策略

```bash
# 项目中的环境文件组织
├── .env                  # 默认环境变量（所有环境共用）
├── .env.development      # 开发环境
├── .env.staging          # 预发布环境
├── .env.production       # 生产环境
├── .env.local            # 本地覆盖（不提交到 Git）
└── .env.example          # 模板文件（提交到 Git，不含敏感信息）
```

```javascript
// config/index.js - 根据 NODE_ENV 加载对应环境文件
const path = require('path');
const dotenv = require('dotenv');

// 先加载默认配置
dotenv.config();

// 再加载环境特定配置（会覆盖默认值）
const envFile = `.env.${process.env.NODE_ENV || 'development'}`;
dotenv.config({ path: path.resolve(__dirname, '..', envFile), override: true });

// 最后加载本地覆盖（.env.local 优先级最高）
dotenv.config({ path: path.resolve(__dirname, '..', '.env.local'), override: true });

module.exports = {
  port: process.env.PORT || 3000,
  databaseUrl: process.env.DATABASE_URL,
  apiKey: process.env.API_KEY,
  nodeEnv: process.env.NODE_ENV || 'development',
};
```

#### 配置验证（使用 zod）

```javascript
// config/validate.js - 使用 zod 验证环境变量
const { z } = require('zod');

const envSchema = z.object({
  PORT: z.coerce.number().int().positive().default(3000),
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
  NODE_ENV: z.enum(['development', 'staging', 'production']).default('development'),
  REDIS_URL: z.string().url().optional(),
  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'debug']).default('info'),
});

// 验证并导出类型安全的配置对象
const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error('环境变量配置错误：');
  console.error(parsed.error.flatten().fieldErrors);
  process.exit(1);
}

module.exports = parsed.data;
```

```bash
# 启动时指定环境
NODE_ENV=production node app.js

# 或使用 cross-env 跨平台兼容
pnpm add -D cross-env
# cross-env NODE_ENV=production node app.js
```

> **敏感信息管理要点**：永远不要将 `.env` 文件提交到 Git（在 `.gitignore` 中添加 `.env` 和 `.env.local`）。生产环境建议通过 Docker/K8s 的环境变量注入或密钥管理服务（如 Vault、AWS Secrets Manager）来管理敏感配置，而非依赖 `.env` 文件。

### 3. 全局错误处理中间件

- Express 全局错误处理中间件：四个参数 (err, req, res, next)
- 未捕获异常处理：process.on('uncaughtException')、process.on('unhandledRejection')
- 优雅关闭：捕获 SIGTERM/SIGINT 信号、关闭数据库连接、停止接收新请求
- 代码示例：完整的错误处理中间件 + 优雅关闭实现

---

## 补充：worker_threads 多线程

### 1. Node.js 单线程模型的真实含义

"Node.js 是单线程的"是一个简化说法。准确表述是：**JavaScript 代码的执行是单线程的，但 Node.js 进程本身不是单线程的。**

| 组成 | 是否单线程 | 说明 |
|------|-----------|------|
| JavaScript 执行 | 单线程 | 所有 JS 代码（含回调）都在主线程的 V8 Isolate 中执行，同一时刻只有一段 JS 在跑 |
| libuv 事件循环 | 单线程 | 事件循环本身运行在主线程 |
| libuv 线程池 | 多线程 | 默认 4 个线程，处理文件 I/O、DNS 查询（`getaddrinfo`）、`zlib` 压缩、部分 `crypto` 运算 |
| 网络 I/O | 不需要线程 | 使用操作系统原生异步 API（epoll / kqueue / IOCP） |
| V8 后台线程 | 多线程 | 垃圾回收、JIT 编译的并行与并发标记等 |
| Worker Threads | 多线程 | 显式创建的独立 V8 Isolate，各自有独立的 JS 执行环境 |

所以"单线程"的真正含义是：**JS 主线程只有一个，任何 CPU 密集的 JS 计算都会阻塞它**，导致事件循环无法推进，所有 I/O 回调与定时器都被推迟。这正是需要 `worker_threads` 的根本原因。

```javascript
// 反例：CPU 密集计算阻塞事件循环
const http = require('node:http')

http
  .createServer((req, res) => {
    if (req.url === '/heavy') {
      // 同步计算数秒：这段时间内事件循环完全停摆
      let sum = 0
      for (let i = 0; i < 5e9; i++) sum += i
      res.end(String(sum))
    } else {
      res.end('ok')
    }
  })
  .listen(3000)

// 现象：/heavy 执行期间，访问 / 也会一起卡住
```

```bash
# 用 libuv 线程池处理文件 I/O、压缩与部分加密运算，不占用 JS 主线程
UV_THREADPOOL_SIZE=8 node app.js
```

### 2. `worker_threads` / `cluster` / `child_process` 的区别与选型

| 维度 | `worker_threads` | `cluster` | `child_process` |
|------|-----------------|-----------|-----------------|
| 隔离级别 | 同一进程内的多个 V8 Isolate | 多进程（fork 主进程副本） | 多进程（可执行任意命令） |
| 内存开销 | 低（可共享内存） | 高（每个进程独立堆） | 高（每个进程独立堆） |
| 启动速度 | 快（几十毫秒量级） | 较慢（进程 fork + 重新初始化） | 最慢（可启动任意程序） |
| 通信方式 | `postMessage` / `MessageChannel` / `SharedArrayBuffer` | 进程间 IPC（基于句柄传递的 `send`） | stdin / stdout / stderr 或 IPC channel |
| 共享内存 | 支持（`SharedArrayBuffer`、Transferable） | 不支持 | 不支持 |
| 崩溃影响 | 默认会拖垮整个进程（可通过监听 `error` 缓解） | 单进程崩溃不影响其他进程 | 完全隔离 |
| 端口共享 | 不支持（需自行传递 handle） | 原生支持（多个进程监听同一端口） | 不支持 |
| 适用场景 | CPU 密集计算（压缩、加密、图像处理、大 JSON 解析） | 提升 HTTP 服务吞吐（利用多核 + 端口复用） | 调用外部程序、完全隔离的沙箱任务 |

**选型口诀**：

- 要利用多核**提升 HTTP 服务吞吐** → `cluster`（或直接用 PM2 / K8s 多实例）。
- 要卸载**CPU 密集计算**且希望低开销、能共享内存 → `worker_threads`。
- 要执行**外部命令**或需要**强隔离**（不可信代码） → `child_process`。

### 3. `Worker` 用法与 `parentPort` 通信

主线程创建 `Worker`，Worker 通过 `parentPort` 与主线程双向通信。通信基于结构化克隆（structured clone），数据是**拷贝**而非引用。

```javascript
// main.js —— 主线程
const { Worker } = require('node:worker_threads')
const path = require('node:path')

function runWorker(payload) {
  return new Promise((resolve, reject) => {
    // workerData 是创建时传入的初始数据（同样是拷贝）
    const worker = new Worker(path.resolve(__dirname, 'worker.js'), {
      workerData: payload
    })

    // message 事件接收 Worker 通过 parentPort.postMessage 发来的消息
    worker.on('message', resolve)

    // error 事件捕获 Worker 内未捕获的异常
    worker.on('error', reject)

    // exit 事件在线程结束时触发，code 为 0 表示正常退出
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker 异常退出，code=${code}`))
    })
  })
}

runWorker({ n: 45 }).then((result) => {
  console.log('计算结果：', result) // 主线程全程未被阻塞
})
```

```javascript
// worker.js —— Worker 线程
const { parentPort, workerData, isMainThread, threadId } = require('node:worker_threads')

// isMainThread 可用于编写"同一文件既是入口又是 Worker"的模块
if (!isMainThread) {
  console.log(`运行在 Worker 线程，threadId=${threadId}`)

  function fib(n) {
    return n < 2 ? n : fib(n - 1) + fib(n - 2)
  }

  // 从 workerData 读取初始数据，把结果回传主线程
  parentPort.postMessage(fib(workerData.n))

  // 长期通信用 on，只处理一条消息用 once
  parentPort.once('shutdown', () => process.exit(0))
}
```

`postMessage` 使用结构化克隆算法，因此**不能传递函数、`Symbol`、DOM 节点等不可克隆的对象**，否则会抛 `DataCloneError`。

```javascript
// 结构化克隆的限制：函数无法传递
worker.postMessage({ fn: () => {} }) // 抛 DataCloneError

// 正确做法：传数据，不传行为；行为在 Worker 内部定义
worker.postMessage({ type: 'compress', payload: buffer })
```

### 4. `MessageChannel` 与 `SharedArrayBuffer` 的零拷贝共享

默认的 `postMessage` 会**拷贝**数据：传一个 100MB 的 `Buffer` 意味着内存里同时存在两份，拷贝本身也要耗时。

**方案一：`MessageChannel` + Transferable（转移所有权，零拷贝）**

`ArrayBuffer` 是 Transferable 对象。把它放进 `postMessage` 的第二个参数（transferList）后，所有权被**转移**：发送方不再持有，接收方拿到同一块内存，不发生拷贝。

```javascript
// main.js —— 用 MessageChannel 转移 ArrayBuffer 所有权
const { Worker, MessageChannel } = require('node:worker_threads')

const worker = new Worker('./worker.js')

// 创建一对互相连通的端口，一个留给主线程，一个交给 Worker
const { port1, port2 } = new MessageChannel()

// 把 port2 转移给 Worker（port2 本身也是 Transferable）
worker.postMessage({ type: 'init', port: port2 }, [port2])

const buffer = new ArrayBuffer(1024 * 1024 * 100) // 100MB

// 关键：第二个参数是 transferList，转移所有权而不是拷贝
port1.postMessage({ type: 'process', buffer }, [buffer])

console.log(buffer.byteLength) // 0：所有权已转移，主线程不再持有这块内存

port1.on('message', (msg) => {
  console.log('处理完成', msg)
})
```

```javascript
// worker.js —— 接收转移过来的端口与 ArrayBuffer
const { parentPort } = require('node:worker_threads')

parentPort.on('message', (msg) => {
  if (msg.type !== 'init') return

  const { port } = msg

  port.on('message', (data) => {
    // 直接使用同一块内存，无拷贝
    const view = new Uint8Array(data.buffer)
    port.postMessage({ done: true, length: view.length })
  })
})
```

**方案二：`SharedArrayBuffer`（真正的共享内存）**

多个线程同时读写同一块内存。因为不涉及所有权转移，主线程与 Worker 可以同时持有。

```javascript
// main.js —— 共享内存
const { Worker } = require('node:worker_threads')

const sab = new SharedArrayBuffer(4 * 1024) // 4KB 共享内存
const view = new Int32Array(sab)

const worker = new Worker('./counter.js', { workerData: { sab } })

worker.on('message', () => {
  console.log(view[0]) // Worker 已把结果写入共享内存，主线程直接可见
})
```

```javascript
// counter.js —— 在共享内存上累加
const { workerData, parentPort } = require('node:worker_threads')

const view = new Int32Array(workerData.sab)

for (let i = 0; i < 1e6; i++) {
  // 注意：普通读写不是原子的，多线程并发写同一位置会丢更新
  view[0] += 1
}

parentPort.postMessage('done')
```

**并发安全**：`SharedArrayBuffer` 上的普通读写不是原子的，多线程同时写同一位置会产生竞态，需要用 `Atomics` 提供原子操作与等待 / 通知机制。

```javascript
// worker.js —— 用 Atomics 做原子操作与线程同步
const { workerData, parentPort } = require('node:worker_threads')

const view = new Int32Array(workerData.sab)

// 原子加：等价于 view[0] += 1，但不会被其他线程的写入打断
Atomics.add(view, 0, 1)

// 原子读
const current = Atomics.load(view, 0)

// 线程同步：index 0 上的值仍为 0 时挂起等待，被唤醒后继续
Atomics.wait(view, 0, 0)

parentPort.postMessage(current)
```

```javascript
// main.js —— 唤醒等待中的 Worker
Atomics.store(view, 0, 1) // 先改值
Atomics.notify(view, 0, 1) // 再唤醒 1 个在 index 0 上等待的线程
```

> **安全提示**：`SharedArrayBuffer` 在浏览器中需要跨源隔离（COOP / COEP）才能使用，也是 Spectre 类侧信道攻击的敏感对象。Node.js 中不受此限制，但同样要谨慎处理不可信数据。

### 5. 线程池 `UV_THREADPOOL_SIZE` 与 Worker 的区别

两者经常被混淆，但解决的问题不同：

| 维度 | libuv 线程池（`UV_THREADPOOL_SIZE`） | `worker_threads` |
|------|-----------------------------------|-----------------|
| 谁在用 | Node.js 内部 API：`fs`、`dns.lookup`、`zlib`、`crypto`（部分） | 开发者显式创建的 Worker |
| 能否执行 JS | **不能**，只执行 C++ 侧的阻塞调用 | 能，每个 Worker 有独立的 V8 Isolate |
| 默认大小 | 4 | 无固定上限（受内存与 CPU 限制） |
| 调整方式 | 环境变量 `UV_THREADPOOL_SIZE`，必须在进程启动前设置 | `new Worker()` 按需创建 |
| 适用 | 加速文件 I/O、DNS、压缩、加密等已有异步 API | 卸载自定义的 CPU 密集 JS 计算 |

```bash
# 必须在启动 Node.js 之前设置，运行时修改无效
UV_THREADPOOL_SIZE=8 node app.js
```

```javascript
// 线程池大小受"同时执行的阻塞任务数"影响
const fs = require('node:fs/promises')

async function readMany(paths) {
  // 并发发起 20 个文件读取，但线程池只有 4 个线程时会排队
  return Promise.all(paths.map((p) => fs.readFile(p)))
}
```

> **常见误区**：把 CPU 密集的 JS 计算写成 `async` 函数，就以为它不阻塞。`async` 只改变写法，不改变执行线程——`await` 之前的同步计算仍然占用主线程。要真正卸载，必须使用 `worker_threads`。

### 6. CPU 密集任务的卸载实践

**场景一：压缩（`zlib`）**

`zlib` 的异步 API 已经使用 libuv 线程池，多数场景下直接用异步版本即可，不必自己开 Worker。

```javascript
// 优先方案：使用异步 API，自动走 libuv 线程池
const zlib = require('node:zlib')
const { promisify } = require('node:util')

const gzip = promisify(zlib.gzip)

async function compress(buffer) {
  // 不阻塞 JS 主线程
  return gzip(buffer, { level: 6 })
}
```

**场景二：加密 / 哈希（`crypto`）**

`crypto` 的异步 API（`pbkdf2`、`scrypt`、`randomFill` 等）同样走线程池；但**同步版本会阻塞主线程**，在登录接口中做高迭代次数的密码哈希时尤其危险。

```javascript
const crypto = require('node:crypto')
const { promisify } = require('node:util')

const pbkdf2 = promisify(crypto.pbkdf2)

async function hashPassword(password, salt) {
  // 走 libuv 线程池，不阻塞事件循环
  // 迭代次数越高越安全，但越吃 CPU
  const derived = await pbkdf2(password, salt, 600000, 32, 'sha256')
  return derived.toString('hex')
}
```

**场景三：图像处理（`sharp`）**

`sharp` 底层是 libvips（C++），其异步 API 会把工作放到自己的线程池，不占用 JS 主线程，通常不需要额外的 Worker。

```javascript
const sharp = require('sharp')

async function makeThumbnail(inputPath, outputPath) {
  // libvips 在 C++ 侧多线程处理，JS 主线程只负责调度
  await sharp(inputPath).resize(320).webp({ quality: 80 }).toFile(outputPath)
}
```

**场景四：纯 JS 计算（必须自己开 Worker）**

```javascript
// worker-pool.js —— 可复用的 Worker 池，避免每次计算都重新创建线程
const { Worker } = require('node:worker_threads')
const os = require('node:os')

class WorkerPool {
  constructor(workerPath, size = Math.max(1, os.cpus().length - 1)) {
    this.workerPath = workerPath
    this.size = size
    this.idle = [] // 空闲 Worker
    this.queue = [] // 等待分配的任务
    this.tasks = new Map() // 记录每个 Worker 当前正在处理的任务

    for (let i = 0; i < size; i++) {
      this.idle.push(this.createWorker())
    }
  }

  createWorker() {
    const worker = new Worker(this.workerPath)

    // 一个 Worker 完成一项任务后，把结果回传并归还到空闲队列
    worker.on('message', ({ result, error }) => {
      const task = this.tasks.get(worker)
      this.tasks.delete(worker)
      this.idle.push(worker)

      if (task) {
        error ? task.reject(new Error(error)) : task.resolve(result)
      }

      this.dispatch() // 立刻尝试领取下一个任务
    })

    // Worker 崩溃时补一个新线程，避免池容量永久下降
    worker.on('error', () => {
      const task = this.tasks.get(worker)
      this.tasks.delete(worker)
      if (task) task.reject(new Error('Worker 执行失败'))

      this.idle = this.idle.filter((w) => w !== worker)
      this.idle.push(this.createWorker())
      this.dispatch()
    })

    return worker
  }

  run(payload) {
    return new Promise((resolve, reject) => {
      this.queue.push({ payload, resolve, reject })
      this.dispatch()
    })
  }

  dispatch() {
    while (this.idle.length > 0 && this.queue.length > 0) {
      const worker = this.idle.pop()
      const task = this.queue.shift()
      this.tasks.set(worker, task)
      // 复用同一个 Worker，只需 postMessage，不必重新创建线程
      worker.postMessage(task.payload)
    }
  }

  async destroy() {
    await Promise.all(this.idle.map((w) => w.terminate()))
    this.idle = []
  }
}

module.exports = { WorkerPool }
```

```javascript
// 使用 Worker 池
const { WorkerPool } = require('./worker-pool')

// 池大小默认取 CPU 核数 - 1，给主线程留出 CPU 时间
const pool = new WorkerPool(require.resolve('./cpu-worker.js'))

async function handleRequest(payload) {
  // 并发提交多个任务，池会自动排队并复用线程
  return pool.run(payload)
}
```

```javascript
// cpu-worker.js —— 只负责计算，不关心调度
const { parentPort } = require('node:worker_threads')

parentPort.on('message', (payload) => {
  try {
    const result = heavyCompute(payload)
    parentPort.postMessage({ result })
  } catch (err) {
    // 把错误回传主线程，而不是让异常冒泡导致线程退出
    parentPort.postMessage({ error: err.message })
  }
})

function heavyCompute(payload) {
  // 这里放真正 CPU 密集的纯 JS 逻辑
  return payload.items.reduce((acc, n) => acc + Math.sqrt(n), 0)
}
```

### 7. Worker 的开销与复用策略

**创建成本**：一个 `Worker` 需要初始化新的 V8 Isolate（堆、内置对象、JIT 状态），创建耗时在几十毫秒量级，内存开销从几 MB 起。因此**不要为每个请求创建一个 Worker**。

| 策略 | 说明 | 适用 |
|------|------|------|
| 一次性 Worker | 每次任务新建、结束即 `terminate()` | 低频、长时间的重任务（如一次性报表生成） |
| Worker 池 | 预创建固定数量（通常为 CPU 核数 - 1），复用线程 | 高频、短任务（如接口中的计算卸载） |
| 常驻 Worker | 启动时创建，进程生命周期内不销毁 | 需要维护内部状态（如缓存的索引结构） |

**其他要点**：

- **消息传递成本**：`postMessage` 的结构化克隆对大对象开销显著，能用 Transferable / `SharedArrayBuffer` 就用。
- **错误处理**：Worker 内未捕获的异常会触发 `error` 事件，若不处理会拖垮主进程；Worker 内也应使用 `try/catch` 并回传错误信息。
- **优雅退出**：用 `worker.terminate()` 强制结束（会中断正在执行的 JS），或先 `postMessage` 通知 Worker 自行清理后再退出。
- **不要在 Worker 里做 I/O 密集任务**：I/O 已由事件循环与 libuv 处理，放进 Worker 只会增加通信开销。
- **内存成倍增长**：每个 Worker 有独立的堆，创建过多会导致内存成倍增长，池大小必须受控。

```javascript
// 优雅关闭：先通知，超时后强制终止
async function shutdownWorker(worker, timeoutMs = 1000) {
  const exited = new Promise((resolve) => worker.once('exit', resolve))

  // 通知 Worker 自行清理资源
  worker.postMessage({ type: 'shutdown' })

  // 竞速：正常退出优先，超时则强制终止
  const result = await Promise.race([
    exited,
    new Promise((resolve) => setTimeout(() => resolve('timeout'), timeoutMs))
  ])

  if (result === 'timeout') {
    await worker.terminate()
  }
}
```

### 8. 面试常见问法

**Q1：Node.js 是单线程的吗？**
回答要点：不完全是。JavaScript 代码的执行是单线程的（只有一个主线程的 V8 Isolate），但 Node.js 进程本身是多线程的——libuv 有默认 4 个线程的线程池处理文件 I/O、DNS、`zlib` 与部分 `crypto` 运算，网络 I/O 使用操作系统原生异步 API，V8 自身也有 GC 与 JIT 的后台线程。因此"单线程"的真正含义是"JS 主线程只有一个，CPU 密集的 JS 会阻塞事件循环"。

**Q2：`worker_threads`、`cluster`、`child_process` 怎么选？**
回答要点：要利用多核提升 HTTP 服务吞吐用 `cluster`（多进程 + 端口复用）；要卸载 CPU 密集计算且希望低开销、能共享内存用 `worker_threads`；要执行外部命令或需要强隔离用 `child_process`。三者的隔离级别与通信成本依次递增，内存开销也依次递增。

**Q3：`postMessage` 会拷贝数据吗？怎么避免？**
回答要点：会，默认使用结构化克隆算法做深拷贝。避免方式是用 Transferable 对象（如 `ArrayBuffer`）配合 transferList 转移所有权实现零拷贝，或用 `SharedArrayBuffer` 真正共享内存（需配合 `Atomics` 保证并发安全）。注意结构化克隆无法传递函数、`Symbol` 等不可克隆对象。

**Q4：`UV_THREADPOOL_SIZE` 和 `worker_threads` 有什么区别？**
回答要点：libuv 线程池由 Node.js 内部 API 使用，**不能执行 JS**，只处理 C++ 侧的阻塞调用，默认 4 个线程，通过启动前的环境变量调整；`worker_threads` 是开发者显式创建、每个都有独立 V8 Isolate 的线程，能执行 JS，用于卸载自定义的 CPU 密集计算。两者解决的问题不同。

**Q5：Worker 创建有开销吗？应该怎么用？**
回答要点：有。每个 Worker 要初始化新的 V8 Isolate，创建耗时在几十毫秒量级、内存开销从几 MB 起，因此不能为每个请求创建。高频短任务应该用 Worker 池（预创建 CPU 核数 - 1 个并复用），低频长任务可以一次性创建，需要维护内部状态的用常驻 Worker。

### 9. 易错点

| 易错点 | 现象 | 原因 | 解决方案 |
|--------|------|------|----------|
| 把 CPU 密集计算写成 `async` 就以为不阻塞 | 接口依然超时 | `async` 只改变写法，不改变执行线程，`await` 之前的同步计算仍占用主线程 | 用 `worker_threads` 真正卸载 |
| 为每个请求创建 Worker | 响应变慢、内存暴涨 | 每个 Worker 都要初始化新的 V8 Isolate | 使用 Worker 池并复用线程 |
| `postMessage` 传大对象 | 主线程卡顿、内存翻倍 | 结构化克隆做深拷贝 | 用 Transferable 转移所有权或 `SharedArrayBuffer` |
| 在 `SharedArrayBuffer` 上做普通读写 | 计数结果偏小、数据错乱 | 普通读写不是原子的，存在竞态 | 用 `Atomics.add` / `Atomics.load` 等原子操作 |
| Worker 内异常未处理 | 整个进程退出 | Worker 的未捕获异常触发 `error` 事件，未监听会拖垮进程 | Worker 内 `try/catch` 并回传错误，同时监听 `error` 事件 |
| 把 I/O 任务放进 Worker | 性能反而变差 | I/O 已由事件循环与 libuv 处理，放进 Worker 只增加通信开销 | I/O 用异步 API，Worker 只放 CPU 密集的纯 JS 计算 |
| 运行时修改 `UV_THREADPOOL_SIZE` | 配置不生效 | 该环境变量在进程启动时读取 | 在启动命令前设置，如 `UV_THREADPOOL_SIZE=8 node app.js` |
| Worker 池容量按 CPU 核数满配 | 主线程被挤占，响应变慢 | 主线程也需要 CPU 时间 | 池大小设为 CPU 核数 - 1 或更小 |