# 01-Node运行时与核心API 导览

> 定位：五维框架浓缩提炼 01-Node运行时与核心API.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./01-Node运行时与核心API.md)。
> 前置知识：[语法基础与执行机制](../02-javascript-core/01-语法基础与执行机制-导览.md)、[TypeScript基础与类型系统](../03-typescript/01-TypeScript基础与类型系统-导览.md)

---

## 一、核心概念

| 维度 | 内容 |
|------|------|
| 是什么 | Node.js 是基于 Chrome V8 引擎的 JavaScript 运行时环境，核心特征为单线程+事件驱动、非阻塞 I/O、事件循环调度、跨平台（通过 libuv） |
| 能做什么 | 用于 Web 服务端开发、BFF 中间层、CLI 工具、实时通信（WebSocket）、微服务架构等 I/O 密集型场景 |
| 怎么用 | `const http = require('http')` 创建 HTTP 服务；`const fs = require('fs')` 文件操作 |
| 原理和工作流程 | 四个核心特征：单线程+事件驱动（JS 代码单线程执行，但通过事件循环和回调实现高并发）、非阻塞 I/O（所有 I/O 操作异步不阻塞主线程）、事件循环（libuv 提供的 6 阶段调度机制协调异步任务执行顺序）、跨平台（libuv 屏蔽不同操作系统底层差异） |
| 缺点 | 单线程不适合 CPU 密集型计算（需用 Worker Threads）；回调嵌套可能导致回调地狱（已通过 async/await 缓解） |

---

## 二、底层原理

### Node.js 架构层次

| 维度 | 内容 |
|------|------|
| 是什么 | Node.js 整体架构分为四层：标准库（JavaScript 层）、C++ 绑定层、底层支撑库（V8 + libuv + OpenSSL + zlib）、操作系统 |
| 能做什么 | 理解 Node.js 的组成结构有助于定位问题层级和性能瓶颈 |
| 怎么用 | 标准库：直接使用 `require('http')`、`require('fs')` 等 API |
| 原理和工作流程 | V8 引擎负责将 JS 编译为机器码执行。libuv 是核心异步 I/O 库（C 语言编写），提供跨平台事件驱动和异步 I/O 能力。C++ 绑定层将 JS 对核心模块的调用（如 fs.readFile）桥接到底层 C/C++ 库。标准库全部由 JavaScript 编写，是开发者直接使用的 API |
| 缺点 | 架构分层多，调试底层问题需要 C/C++ 知识 |

### libuv 跨平台异步 I/O 库

| 维度 | 内容 |
|------|------|
| 是什么 | libuv 是 Node.js 异步能力的核心，针对不同 I/O 类型采用不同处理策略：网络 I/O 用系统原生异步 API，文件 I/O 和 DNS 查询用线程池（默认 4 线程） |
| 能做什么 | 实现跨平台统一的异步 I/O API，在 Linux（epoll）、macOS（kqueue）、Windows（IOCP）上均能高效运行 |
| 怎么用 | 通过 `UV_THREADPOOL_SIZE=8 node app.js` 调整线程池大小 |
| 原理和工作流程 | 网络 I/O（TCP/UDP）使用操作系统原生异步 API（epoll/kqueue/IOCP），不占用线程池。文件 I/O 和 DNS 查询（getaddrinfo 是阻塞调用）放入线程池执行，完成后回调注册到事件循环。定时器基于 libuv 定时器堆管理。信号处理通过管道写入事件循环读取。文件 I/O 用线程池而非原生异步 API 的原因是大多数操作系统没有真正的异步文件 I/O |
| 缺点 | 线程池默认只有 4 线程，CPU 密集型任务会阻塞线程池导致所有异步 I/O 变慢 |

### Node.js 事件循环详解

| 维度 | 内容 |
|------|------|
| 是什么 | 事件循环是 Node.js 的核心调度机制，分为 6 个阶段（timers/pending callbacks/idle prepare/poll/check/close callbacks），每个阶段维护一个 FIFO 回调队列 |
| 能做什么 | 协调所有异步任务的执行顺序，实现单线程下的高并发处理 |
| 怎么用 | `setTimeout(fn, 0)` 在 timers 阶段执行；`setImmediate(fn)` 在 check 阶段执行；`process.nextTick(fn)` 在各阶段之间执行 |
| 原理和工作流程 | timers 阶段执行 setTimeout/setInterval 到期回调。pending callbacks 执行延迟到下一轮循环的 I/O 回调。poll 阶段（核心）获取新 I/O 事件并执行回调，队列为空时若有 setImmediate 则进入 check，否则阻塞等待。check 阶段执行 setImmediate 回调。close callbacks 执行关闭事件回调。微任务（process.nextTick 和 Promise）在每个阶段之间执行，nextTick 优先级高于 Promise。Node 11+ 改为每个宏任务后清空微任务，与浏览器行为统一 |
| 缺点 | 事件循环阶段多，执行顺序理解容易出错；poll 阶段阻塞可能影响定时器精度 |

### Node.js 事件循环 vs 浏览器事件循环

| 维度 | 内容 |
|------|------|
| 是什么 | Node.js 有 6 个宏任务阶段（每个阶段独立队列），浏览器只有一个宏任务队列；Node.js 有 nextTick + Promise 双微任务队列，浏览器只有 Promise 微任务队列 |
| 能做什么 | 理解两者差异有助于在 Node.js 和浏览器环境中正确编写异步代码 |
| 怎么用 | Node.js 特有 API：`process.nextTick`、`setImmediate`；浏览器特有 API：`requestAnimationFrame`、`MutationObserver` |
| 原理和工作流程 | 宏任务阶段：Node.js 6 个阶段各有独立队列，每个阶段执行完所有回调后才进入下一阶段；浏览器只有一个宏任务队列，每次取一个执行。微任务队列：Node.js 有 process.nextTick 队列（优先级最高）+ Promise 队列；浏览器只有 Promise 微任务队列（含 MutationObserver）。Node 11+ 行为与浏览器统一：每个宏任务后清空微任务队列 |
| 缺点 | Node 版本差异导致行为不一致，需注意版本兼容性 |

### 模块加载机制

| 维度 | 内容 |
|------|------|
| 是什么 | CommonJS（require/module.exports）同步加载、值拷贝、支持缓存；ES Module（import/export）异步加载、值引用（live binding）、支持 Tree Shaking |
| 能做什么 | 根据项目需求选择模块系统：CommonJS 适合 Node.js 传统项目，ES Module 适合现代项目且支持 Tree Shaking |
| 怎么用 | CommonJS：`const math = require('./math')`；ES Module：`import { add } from './math.mjs'`，需在 package.json 设置 `"type": "module"` 或使用 .mjs 扩展名 |
| 原理和工作流程 | CommonJS 同步加载，首次加载后缓存到 require.cache，后续直接返回缓存对象，导出的是值的拷贝。ES Module 异步加载，编译时静态分析，导出的是值的引用（模块内部变化会反映到外部），支持顶层 await。require 查找策略：核心模块 → 文件模块（含 .js/.json/.node 扩展名）→ 目录模块（package.json main 字段或 index.js）→ node_modules 逐级向上查找 → 全局安装目录 |
| 缺点 | 两种模块系统混用可能导致加载失败；package.json 中 "type": "module" 下 .js 文件不支持 require |

### Stream 流

| 维度 | 内容 |
|------|------|
| 是什么 | Stream 是 Node.js 中处理流式数据的抽象接口，核心优势是分块处理数据，避免一次性将大量数据加载到内存中 |
| 能做什么 | 用于大文件读写、HTTP 请求响应、压缩解压、加密解密等需要流式处理的场景 |
| 怎么用 | `fs.createReadStream('input.txt').pipe(zlib.createGzip()).pipe(fs.createWriteStream('output.txt.gz'))` |
| 原理和工作流程 | 四种流类型：Readable（可读流，如 fs.createReadStream）、Writable（可写流，如 fs.createWriteStream）、Duplex（双工流，如 TCP socket）、Transform（转换流，如 zlib.createGzip）。背压机制：当可写流消费速度跟不上可读流产出的速度时，pipe() 自动暂停可读流，待可写流排空（drain 事件）后恢复。手动处理背压需检查 write() 返回值并在 false 时暂停可读流 |
| 缺点 | 未处理流 error 事件会导致进程崩溃；流式处理调试不如一次性处理直观 |

### Buffer 缓冲区

| 维度 | 内容 |
|------|------|
| 是什么 | Buffer 是 Node.js 中用于处理二进制数据的类，是 Uint8Array 的子类，弥补 JavaScript 原生二进制处理能力的不足 |
| 能做什么 | 处理文件读写、网络协议、加密解密、编码转换等二进制数据场景 |
| 怎么用 | `Buffer.alloc(10)` 安全分配初始化；`Buffer.from('Hello')` 从字符串创建；`buf.toString('base64')` 编码转换；`Buffer.concat([buf1, buf2])` 合并 |
| 原理和工作流程 | Buffer.alloc 分配并初始化为 0（安全但慢），Buffer.allocUnsafe 分配但不初始化（快但可能含旧数据有安全风险），Buffer.from 从字符串/数组创建。支持多种编码转换（utf8/base64/hex）。大端序（BE）和小端序（LE）读写多字节数值。Buffer 一旦创建大小固定不可变 |
| 缺点 | allocUnsafe 可能泄露旧内存中的敏感数据（密码、密钥等）；Buffer 大小固定不可动态扩展 |

---

## 三、实战应用

### 大文件流式处理

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 readline + createReadStream 逐行处理大文件，避免一次性加载整个文件到内存 |
| 能做什么 | 处理 GB 级别的大文件（日志分析、数据导入），内存占用恒定 |
| 怎么用 | `const rl = readline.createInterface({ input: fs.createReadStream(filePath) })`；`for await (const line of rl) { ... }` |
| 原理和工作流程 | createReadStream 以流方式读取文件，每次读取一个 chunk（默认 64KB），readline 将 chunk 按行分割。for await...of 异步迭代逐行处理，内存中只保留当前行数据。可配合 Transform 流在读取过程中进行数据转换（如转大写、过滤） |
| 缺点 | 逐行处理比一次性读取慢；某些操作（如排序）需要完整数据，不适合流式处理 |

### 自定义 Event Loop 调度

| 维度 | 内容 |
|------|------|
| 是什么 | 利用 setImmediate 将 CPU 密集型任务拆分为多个小批次，每批次处理后将控制权交还给事件循环 |
| 能做什么 | 避免长时间阻塞主线程，保持服务器对其他请求的响应能力 |
| 怎么用 | 在批处理函数中：`setImmediate(processBatch)` 将下一批调度到 check 阶段执行 |
| 原理和工作流程 | 将大数组按 batchSize 拆分，每批处理 batchSize 个元素后调用 setImmediate 将控制权交还给事件循环，允许处理其他 I/O 事件。处理完成后 Promise resolve 返回结果。这种方式比直接循环处理慢，但不会阻塞事件循环 |
| 缺点 | 比同步处理慢；不适合对实时性要求极高的计算任务（应使用 Worker Threads） |

### 模块热更新

| 维度 | 内容 |
|------|------|
| 是什么 | 通过删除 require.cache 中的缓存条目并重新 require，实现配置/模块的运行时热更新 |
| 能做什么 | 在不重启进程的情况下更新配置或模块，适用于开发调试和配置热加载 |
| 怎么用 | `delete require.cache[require.resolve('./config')]`；`const newConfig = require('./config')` |
| 原理和工作流程 | require 首次加载模块后将结果缓存到 require.cache 对象中，后续 require 直接返回缓存。删除缓存条目后再次 require 会重新执行模块代码并获取最新值。通过 fs.watch 监听文件变化自动触发重新加载 |
| 缺点 | 只删除缓存可能导致旧引用未被更新；复杂模块（有状态或有副作用）热更新可能产生不一致 |

---

## 四、常见面试题

### Node.js 是单线程的为什么还能处理高并发

| 维度 | 内容 |
|------|------|
| 是什么 | JS 代码在单线程中执行，但 I/O 操作通过 libuv 的线程池和操作系统异步 API 在后台执行，不阻塞主线程 |
| 能做什么 | 验证候选人是否理解 Node.js 的"单线程事件循环 + 非阻塞 I/O"模型 |
| 怎么用 | 回答要点：单线程 JS + 非阻塞 I/O + 事件循环调度 + 线程池处理文件 I/O 和加密等阻塞操作 |
| 原理和工作流程 | 主线程执行 JS 代码和处理事件回调，I/O 操作（网络请求、文件读写）交给 libuv 后台处理（线程池或系统异步 API），完成后回调推入事件循环队列由主线程执行。这种模型使 Node.js 擅长处理 I/O 密集型高并发场景（如 Web 服务、API 网关），但不适合 CPU 密集型计算 |
| 缺点 | 纯 CPU 计算会阻塞事件循环，需用 Worker Threads 或拆分任务 |

### process.nextTick 和 setImmediate 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | process.nextTick 是微任务，在当前阶段结束后立即执行，优先级最高；setImmediate 是宏任务，在 check 阶段执行 |
| 能做什么 | 根据执行时机需求选择正确的 API：需立即执行用 nextTick，需在 poll 之后执行用 setImmediate |
| 怎么用 | `process.nextTick(() => { ... })` 在当前操作完成后立即执行；`setImmediate(() => { ... })` 在下一轮 check 阶段执行 |
| 原理和工作流程 | nextTick 在当前事件循环阶段执行完毕后、下一个阶段开始前执行，优先级高于 Promise。setImmediate 在 poll 阶段之后的 check 阶段执行。在 I/O 回调中（poll 阶段），setImmediate 总是先于 setTimeout(fn, 0) 执行（因为 poll 后直接进入 check，而 timers 需要等到下一轮） |
| 缺点 | 在 nextTick 中递归调用 nextTick 会"饿死"事件循环，导致无法进入下一阶段 |

### setTimeout(fn, 0) 和 setImmediate(fn) 哪个先执行

| 维度 | 内容 |
|------|------|
| 是什么 | 答案取决于调用上下文：主模块中顺序不确定（受进程性能影响），I/O 回调中 setImmediate 总是先执行 |
| 能做什么 | 验证候选人对事件循环阶段的深入理解 |
| 怎么用 | 在主模块中测试：顺序不确定；在 I/O 回调中测试：setImmediate 先执行 |
| 原理和工作流程 | 主模块调用时，setTimeout(fn, 0) 的最小延迟实际为 1ms（Node 中），与 setImmediate 的执行时机取决于进程启动时间，顺序不确定。I/O 回调在 poll 阶段执行，poll 阶段结束后直接进入 check 阶段（setImmediate），而 timers 阶段需要等到下一轮循环，因此 setImmediate 先执行 |
| 缺点 | 行为依赖进程性能，不应依赖主模块中的执行顺序 |

### Buffer.alloc 和 Buffer.allocUnsafe 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | Buffer.alloc(size) 分配内存并全部初始化为 0（安全但慢），Buffer.allocUnsafe(size) 分配内存但不初始化（快但可能含旧数据，有安全风险） |
| 能做什么 | 根据场景选择：敏感数据场景用 alloc，性能优先且立即覆盖全部内容的场景用 allocUnsafe |
| 怎么用 | `Buffer.alloc(1024)` 安全分配；`Buffer.allocUnsafe(1024)` 快速分配但需立即覆盖 |
| 原理和工作流程 | allocUnsafe 直接从操作系统预分配的内存池中获取，不进行初始化，因此可能包含之前使用过的内存数据（如密码、密钥等敏感信息）。alloc 使用 fill(0) 确保全部清零，但速度较慢。allocUnsafe 后必须立即用 .fill() 或 .write() 覆盖全部数据 |
| 缺点 | allocUnsafe 使用不当可能导致敏感信息泄露；alloc 比 allocUnsafe 慢 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | Node.js 开发中常见错误：循环中 require、混淆 nextTick 和 setImmediate、大文件用 readFile 而非流、Buffer allocUnsafe 未覆盖、混用 CommonJS 和 ESM、未处理流错误、nextTick 递归饿死事件循环、线程池被 CPU 任务占满 |
| 能做什么 | 帮助开发者提前识别并避免 Node.js 中的典型陷阱 |
| 怎么用 | 对照排查：大文件用 createReadStream + pipe；始终为流绑定 error 事件监听器；避免在 nextTick 中递归调用 nextTick 改用 setImmediate；CPU 密集任务用 Worker Threads 或增大 UV_THREADPOOL_SIZE |
| 原理和工作流程 | 常见错误根源：require 有缓存机制，循环中 require 不会重复加载但影响可读性；nextTick 和 setImmediate 执行阶段不同导致顺序混乱；readFile 一次性加载大文件到内存可能 OOM；allocUnsafe 不初始化可能泄露旧内存数据；package.json "type": "module" 下混用 require 和 import 报错；流默认无 error 监听器时抛出异常导致进程崩溃；nextTick 递归导致事件循环无法进入下一阶段；默认 4 线程池被 CPU 任务占满导致所有异步 I/O 变慢 |
| 缺点 | 部分问题（如线程池饥饿）需要性能监控才能发现 |

---

## 六、Node.js 现代特性

### 6.1 Node.js 内置 fetch() API

| 维度 | 内容 |
|------|------|
| 是什么 | Node.js 18+ 内置的 `fetch()` API，基于 `undici` 实现，与浏览器 `fetch()` 保持高度兼容，支持 HTTP/1.1 和 HTTP/2 |
| 能做什么 | 替代 `node-fetch`、`axios` 等第三方 HTTP 客户端库，实现零依赖的 HTTP 请求；支持 GET/POST、超时中断、流式读取、自定义 Dispatcher 等 |
| 怎么用 | `const response = await fetch('https://api.example.com/data', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })`；使用 `AbortSignal.timeout(5000)` 设置超时 |
| 原理和工作流程 | 底层基于 undici HTTP 客户端（C++ 编写），通过 libuv 的事件循环调度网络 I/O。与浏览器 fetch 的主要差异：无 CORS 限制、无自动 Cookie 管理、无内置缓存、支持自定义 Agent 和代理 |
| 缺点 | 无内置请求拦截器、重试机制（需自行封装）；错误处理需手动检查 `response.ok`（与 axios 不同）；不支持请求取消的进度回调 |

### 6.2 Web Streams API

| 维度 | 内容 |
|------|------|
| 是什么 | Node.js 18+ 稳定支持的 WHATWG 标准流接口，包括 `ReadableStream`（可读流）、`WritableStream`（可写流）、`TransformStream`（转换流），与浏览器 Web Streams API 完全一致 |
| 能做什么 | 实现跨平台（浏览器 + Node.js）统一的流式数据处理；通过 `pipeThrough()` 链式组合多个转换流；通过 `pipeTo()` 将数据管道输出到目标 |
| 怎么用 | 创建流：`new ReadableStream({ start(controller) { controller.enqueue(data); } })`；消费：`reader.read()` 逐块读取；管道：`source.pipeThrough(transform).pipeTo(destination)` |
| 原理和工作流程 | Web Streams 内置背压机制，通过 `controller.desiredSize` 自动控制数据流速。与 Node.js Stream 可互转：`ReadableStream.from(nodeStream)` 和 `stream.Readable.fromWeb(webStream)`。`pipeThrough` 是 Web Streams 独有的链式转换能力 |
| 缺点 | 与 Node.js 原生 Stream 生态（如 `fs.createReadStream`）的互操作需要额外转换；`pipeThrough` 的链式写法不如 Node.js 的 `.pipe()` 直观 |

### 6.3 Node.js 20+ 新特性速览

| 维度 | 内容 |
|------|------|
| 是什么 | Node.js 20+ 引入的四个重要新特性：`node:test` 内置测试运行器（替代 Jest/Mocha）、`--watch` 模式（替代 nodemon）、`.env` 内置支持（替代 dotenv）、权限模型（限制进程对文件系统/网络/子进程的访问） |
| 能做什么 | **node:test**：零依赖编写和运行测试，支持子测试、describe/it 风格、skip/only 控制；**--watch**：文件变化自动重启进程，替代 nodemon；**--env-file**：加载 .env 到 process.env，替代 dotenv；**权限模型**：限制进程能力范围，防止安全漏洞被利用 |
| 怎么用 | `node --test` 运行测试；`node --watch app.js` 监听模式；`node --env-file=.env app.js` 加载环境变量；`node --permission --allow-fs-read=./data --allow-net=api.example.com app.js` 权限控制 |
| 原理和工作流程 | node:test 基于 Node.js 内置的 Test Runner API，使用 TAP（Test Anything Protocol）输出格式；--watch 基于文件系统事件监听（fs.watch）；--env-file 在启动时解析 .env 文件注入 process.env；权限模型通过操作系统级别的权限检查拦截文件/网络/子进程操作 |
| 缺点 | node:test 生态不如 Jest 成熟（缺少快照测试、覆盖率报告需额外工具）；`--watch` 在 Node 22 中已稳定；权限模型在 Node 20 中为实验性，Node 22 中仍为实验性；--env-file 不支持 dotenv 的变量展开和模板语法 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./01-Node运行时与核心API.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)