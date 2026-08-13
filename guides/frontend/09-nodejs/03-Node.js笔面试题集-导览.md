# 03-Node.js笔面试题集 导览

> 定位：五维框架浓缩提炼 03-Node.js笔面试题集.md 全部题目所考知识点，快速查阅与复习。
> 用法：每道题目提取所考知识点生成一张纵向表格，需要查看原题解析时跳转 [原文](./03-Node.js笔面试题集.md)。
> 前置知识：[01-Node运行时与核心API](./01-Node运行时与核心API-导览.md) | [02-Web框架与BFF层](./02-Web框架与BFF层-导览.md)

---

## 一、选择题（10 题，每题附解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 选择题覆盖 Node.js 单线程模型、事件循环阶段、nextTick/setImmediate 区别、Buffer 安全分配、CommonJS 特性、Stream 流类型、Koa 洋葱模型、cluster 模块、进程退出事件、模块查找顺序 |
| 能做什么 | 考查对 Node.js 运行时核心概念、事件循环机制、核心 API 的准确辨析能力 |
| 怎么用 | 先独立作答再对照解析，标注错题并回顾对应原理文件 |
| 原理和工作流程 | 题目按难度分布：基础题（1-3 题）考查单线程模型和事件循环基础，中档题（4-9 题）考查 Buffer/Stream/模块/Koa/cluster 等核心概念，拔高题（10 题）考查事件循环 poll 阶段的阻塞机制 |
| 缺点 | 选择题只能考查概念辨析，无法评估实际编码和调试能力 |

### 1. Node.js 的单线程模型说法正确的是

| 维度 | 内容 |
|------|------|
| 是什么 | JavaScript 代码在单线程中执行，但 I/O 操作通过 libuv 线程池在后台执行，不是所有操作都是单线程 |
| 能做什么 | 考查对 Node.js 单线程模型的准确理解，澄清"一切操作都是单线程"的常见误解 |
| 怎么用 | 回答要点：JS 代码单线程执行 + I/O 操作通过 libuv 线程池异步执行 + 事件循环协调 |
| 原理和工作流程 | 主线程：执行 JS 代码、处理事件回调。libuv 线程池：执行文件 I/O、DNS 查询、加密等阻塞操作。网络 I/O 使用操作系统原生异步 API（epoll/kqueue/IOCP），不占用线程池。Node.js 的"单线程"指 JS 代码执行层面，底层 I/O 实际上是多线程的 |
| 缺点 | 理解不准确可能在面试中回答错误 |

### 2. Node.js 事件循环中 check 阶段执行什么回调

| 维度 | 内容 |
|------|------|
| 是什么 | check 阶段执行 setImmediate 回调，它位于 poll 阶段之后、close callbacks 阶段之前 |
| 能做什么 | 考查对事件循环 6 个阶段及各自职责的准确记忆 |
| 怎么用 | `setImmediate(() => { console.log('check') })` 在 check 阶段执行 |
| 原理和工作流程 | 事件循环阶段顺序：timers（setTimeout/setInterval）→ pending callbacks → idle prepare → poll（核心，获取 I/O 事件）→ check（setImmediate）→ close callbacks。poll 阶段队列为空时，若有 setImmediate 则进入 check |
| 缺点 | 阶段多容易记混，setTimeout(fn,0) 和 setImmediate 的执行顺序易混淆 |

### 3. process.nextTick 和 setImmediate 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | nextTick 是微任务，在当前阶段结束后立即执行，优先级最高；setImmediate 是宏任务，在 check 阶段执行，位于 poll 之后 |
| 能做什么 | 考查对微任务和宏任务在 Node.js 中执行时机的准确理解 |
| 怎么用 | nextTick 用于需要立即在当前操作后执行的回调；setImmediate 用于将回调推迟到 poll 阶段之后 |
| 原理和工作流程 | nextTick 在事件循环每个阶段执行完毕后、下一个阶段开始前执行，优先级高于 Promise。setImmediate 在 poll 阶段之后的 check 阶段执行。在 I/O 回调中（poll 阶段），setImmediate 总是先于 setTimeout(fn, 0) 执行 |
| 缺点 | nextTick 递归调用会饿死事件循环；两者顺序在主模块和 I/O 回调中不同 |

### 4. Buffer.alloc 和 Buffer.allocUnsafe 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | Buffer.alloc 分配内存并全部初始化为 0（安全），Buffer.allocUnsafe 分配但不初始化（快但可能含旧数据） |
| 能做什么 | 考查对 Buffer 安全分配机制的理解 |
| 怎么用 | 敏感数据用 alloc；性能优先且立即覆盖的场景用 allocUnsafe |
| 原理和工作流程 | allocUnsafe 从操作系统预分配的内存池中获取，不初始化，可能包含之前使用过的内存数据（如密码、密钥等）。alloc 使用 fill(0) 确保全部清零，安全性高但速度较慢。allocUnsafe 后必须立即用 .fill() 或 .write() 覆盖全部数据 |
| 缺点 | 选错分配方式可能导致安全漏洞或性能浪费 |

### 5. 关于 CommonJS 模块的说法正确的是

| 维度 | 内容 |
|------|------|
| 是什么 | CommonJS 是同步加载，输出的是值的拷贝，获取到的是值的副本而非引用 |
| 能做什么 | 考查对 CommonJS 模块加载机制和输出特性的准确理解 |
| 怎么用 | `const math = require('./math')` 获取模块导出值的拷贝 |
| 原理和工作流程 | CommonJS 是同步加载（require 阻塞执行直到模块加载完成），首次加载后将结果缓存到 require.cache，后续 require 直接返回缓存。module.exports 输出的是值的拷贝，模块内部修改不会影响已导入的值。ES Module 是异步加载，输出的是值的引用（live binding） |
| 缺点 | 值拷贝特性在某些场景下可能不符合预期 |

### 6. Stream 流的类型不包括

| 维度 | 内容 |
|------|------|
| 是什么 | Node.js Stream 有四种类型：Readable（可读流）、Writable（可写流）、Duplex（双工流）、Transform（转换流），不存在 "BufferStream" 类型 |
| 能做什么 | 考查对 Stream 四种类型的准确记忆 |
| 怎么用 | Readable：fs.createReadStream；Writable：fs.createWriteStream；Duplex：TCP socket；Transform：zlib.createGzip |
| 原理和工作流程 | Readable 只能读取数据，Writable 只能写入数据，Duplex 可读可写（如 socket），Transform 是特殊的 Duplex 可在读写过程中转换数据（如压缩/加密）。所有流都继承自 EventEmitter |
| 缺点 | 四种类型的功能边界需要实际使用才能加深理解 |

### 7. Koa 中间件的洋葱模型是指

| 维度 | 内容 |
|------|------|
| 是什么 | 请求先进入最外层中间件，经过 await next() 进入内层，到达最内层后反向执行 next() 之后的代码 |
| 能做什么 | 考查对 Koa 洋葱模型执行顺序的理解，区分"进入"和"返回"代码的执行时机 |
| 怎么用 | `app.use(async (ctx, next) => { console.log('1-in'); await next(); console.log('1-out') })` |
| 原理和工作流程 | Koa 使用 compose 函数将中间件数组组合为一个大函数，通过递归 dispatch 实现。每个中间件 await next() 时暂停自身执行内层，内层全部完成后从最内层向外执行 next() 之后的代码。这种模型使得 Koa 比 Express 的 callback 风格更优雅 |
| 缺点 | 中间件嵌套过深时调试困难 |

### 8. cluster 模块的作用是

| 维度 | 内容 |
|------|------|
| 是什么 | cluster 模块通过 fork 多个子进程，利用多核 CPU 提高吞吐量，主进程负责分发请求到子进程 |
| 能做什么 | 解决 Node.js 单线程无法充分利用多核 CPU 的问题 |
| 怎么用 | `const cluster = require('cluster')`；`if (cluster.isPrimary) { for (let i = 0; i < cpus; i++) cluster.fork() } else { app.listen(3000) }` |
| 原理和工作流程 | 主进程 fork 多个子进程（数量等于 CPU 核心数），每个子进程独立运行应用实例。主进程通过内置的 round-robin 或操作系统调度将连接分发给子进程。子进程崩溃时主进程可自动重启。PM2 基于 cluster 提供生产级进程管理 |
| 缺点 | 内存不能共享，需要 Redis 等外部存储共享状态；子进程间通信通过 IPC 有开销 |

### 9. 以下哪个事件在 Node.js 进程退出前触发

| 维度 | 内容 |
|------|------|
| 是什么 | process.on('exit') 在进程退出前触发，但只能执行同步操作；process.on('beforeExit') 在事件循环空闲时触发，可执行异步操作 |
| 能做什么 | 考查对进程生命周期事件及各自限制的了解 |
| 怎么用 | `process.on('beforeExit', async () => { await cleanup() })` 用于异步清理；`process.on('exit', () => { ... })` 用于同步清理 |
| 原理和工作流程 | exit 事件在 Node.js 事件循环结束后触发，此时只能执行同步代码（异步操作的回调不会被调用）。beforeExit 在事件循环没有更多任务时触发，可执行异步操作，但异步操作完成后会重新进入事件循环。SIGTERM/SIGINT 信号处理用于优雅关闭 |
| 缺点 | 混淆 exit 和 beforeExit 的异步限制可能导致清理逻辑不完整 |

### 10. require 查找模块的顺序是

| 维度 | 内容 |
|------|------|
| 是什么 | require 查找顺序：核心模块 → 文件模块（含 .js/.json/.node）→ 目录模块（package.json main 字段或 index.js）→ node_modules（从当前目录逐级向上查找）→ 全局安装目录 |
| 能做什么 | 考查对 Node.js 模块解析算法的完整理解 |
| 怎么用 | 文件模块：`require('./math')` 依次尝试 math.js、math.json、math.node；目录模块：`require('./utils')` 查找 package.json main 字段或 index.js |
| 原理和工作流程 | 核心模块优先于文件模块，Node.js 内置模块（如 http、fs）优先级最高。文件模块按扩展名 .js、.json、.node 顺序尝试。目录模块先查 package.json 的 main 字段，没有则查 index.js。node_modules 从当前目录开始逐级向上查找，直到根目录。全局安装目录（NODE_PATH）最后查找 |
| 缺点 | 模块查找顺序的复杂性可能导致模块加载失败时难以排查 |

---

## 二、简答题（8 题，附要点）

| 维度 | 内容 |
|------|------|
| 是什么 | 简答题覆盖事件循环机制、nextTick vs setImmediate、CommonJS vs ES Module、Stream 类型、进程管理、Express vs Koa、Node.js 适用场景、BFF 层 |
| 能做什么 | 考查对 Node.js 核心机制的系统性理解和表达能力 |
| 怎么用 | 逐题口头回答后对照参考答案，补充遗漏要点 |
| 原理和工作流程 | 题目按难度分布：中档题（1-6 题）考查事件循环和核心 API，拔高题（7-8 题）考查适用场景和架构设计 |
| 缺点 | 简答题依赖记忆，实际能力需通过编码题验证 |

### 1. Node.js 事件循环机制

| 维度 | 内容 |
|------|------|
| 是什么 | 事件循环是 Node.js 的核心调度机制，分为 6 个阶段（timers/pending callbacks/idle prepare/poll/check/close callbacks），每阶段维护 FIFO 回调队列 |
| 能做什么 | 协调所有异步任务执行顺序，实现单线程高并发 |
| 怎么用 | 回答要点：6 阶段职责 + 微任务队列（nextTick 优先级最高）在各阶段之间执行 |
| 原理和工作流程 | timers 执行 setTimeout/setInterval 到期回调；poll（核心）获取新 I/O 事件并执行回调；check 执行 setImmediate 回调；close callbacks 执行关闭事件回调。微任务（nextTick > Promise）在每个阶段之间执行。Node 11+ 每个宏任务后清空微任务 |
| 缺点 | 阶段多，poll 阶段阻塞影响定时器精度 |

### 2. process.nextTick 和 setImmediate 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | nextTick 是微任务，当前阶段结束后立即执行；setImmediate 是宏任务，在 poll 阶段之后的 check 阶段执行 |
| 能做什么 | 根据执行时机需求选择：需要立即执行用 nextTick，需要推迟到 poll 之后用 setImmediate |
| 怎么用 | 回答要点：nextTick 微任务 vs setImmediate 宏任务 + 执行阶段 + 执行时机差异 + 递归风险 |
| 原理和工作流程 | nextTick 优先级最高，在当前事件循环阶段结束后、下一个阶段开始前执行。setImmediate 在 check 阶段执行。在 I/O 回调中 setImmediate 先于 setTimeout(fn,0)。nextTick 中递归调用 nextTick 会饿死事件循环 |
| 缺点 | 两者执行时机差异可能导致代码行为与预期不符 |

### 3. CommonJS 和 ES Module 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | CommonJS 同步加载、值拷贝、支持缓存；ES Module 异步加载、值引用（live binding）、支持 Tree Shaking |
| 能做什么 | 根据项目需求选择模块系统 |
| 怎么用 | CommonJS：`require`/`module.exports`；ES Module：`import`/`export`，需 package.json 中 `"type": "module"` 或 .mjs 扩展名 |
| 原理和工作流程 | CommonJS 同步加载（require 阻塞），输出的是值的拷贝，首次加载后缓存。ES Module 异步加载，编译时静态分析，输出的是值的引用（模块内部变化会反映到外部），支持顶层 await 和 Tree Shaking |
| 缺点 | 两种系统混用可能导致加载失败 |

### 4. Stream 的四种类型及应用场景

| 维度 | 内容 |
|------|------|
| 是什么 | Readable（可读）、Writable（可写）、Duplex（双工）、Transform（转换）四种流类型 |
| 能做什么 | 处理大文件读写、HTTP 请求响应、压缩解压等流式数据场景 |
| 怎么用 | Readable：fs.createReadStream；Writable：fs.createWriteStream；Duplex：TCP socket；Transform：zlib.createGzip |
| 原理和工作流程 | 所有流继承 EventEmitter 支持事件驱动。pipe() 自动处理背压：可写流消费速度跟不上时暂停可读流，drain 事件后恢复。手动处理背压需检查 write() 返回值 |
| 缺点 | 不处理流 error 事件会导致进程崩溃；流式调试不如一次性处理直观 |

### 5. Node.js 进程管理的方式

| 维度 | 内容 |
|------|------|
| 是什么 | cluster 模块、child_process 模块、PM2 进程管理工具三种方式 |
| 能做什么 | 利用多核 CPU、实现进程隔离、自动重启和管理 |
| 怎么用 | cluster：`cluster.fork()` fork 多进程；child_process：`spawn/exec/fork` 启动子进程；PM2：`pm2 start app.js -i max` 启动多实例 |
| 原理和工作流程 | cluster 通过主进程 fork 子进程，内置 round-robin 分发连接。child_process 提供四种方式：spawn（流式输出）、exec（缓冲输出）、fork（专用 Node 进程并建立 IPC 通道）、execFile（执行文件）。PM2 基于 cluster 提供负载均衡、自动重启、日志管理、零停机重启等生产级特性 |
| 缺点 | 进程间通信有开销；内存不能共享 |

### 6. Express 和 Koa 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | Express 是 callback 风格中间件（原生不支持 async/await），Koa 是 async/await 洋葱模型（内置 async/await + ctx） |
| 能做什么 | 根据项目需求选择合适的框架 |
| 怎么用 | Express：`app.use((req, res, next) => { ... next() })`；Koa：`app.use(async (ctx, next) => { await ...; await next() })` |
| 原理和工作流程 | Express 不内置任何中间件以外的功能，中间件通过 (req, res, next) 三元组操作，异步错误需显式 next(err)。Koa 使用 async/await 洋葱模型，ctx 上下文对象贯穿请求生命周期，错误处理更自然（try/catch），不内置任何中间件 |
| 缺点 | Express 异步错误处理不如 Koa 优雅；Koa 生态插件不如 Express 丰富 |

### 7. Node.js 适合什么场景不适合什么场景

| 维度 | 内容 |
|------|------|
| 是什么 | 适合 I/O 密集型（Web 服务、API 网关、BFF、实时通信），不适合 CPU 密集型（大量计算、图像处理、视频转码） |
| 能做什么 | 根据 Node.js 特性评估项目技术选型 |
| 怎么用 | 适合场景使用 Node.js 做 Web 服务；不适合场景用 Worker Threads 或拆分到其他语言服务 |
| 原理和工作流程 | I/O 密集型场景：Node.js 的非阻塞 I/O 和事件循环模型非常适合高并发网络请求。CPU 密集型场景：大计算量会阻塞事件循环，可通过 Worker Threads 将计算移到独立线程，或使用 C++ Addon 和 WASM 提升性能 |
| 缺点 | 误判场景可能导致性能瓶颈 |

### 8. BFF 层的概念和作用

| 维度 | 内容 |
|------|------|
| 是什么 | BFF（Backend For Frontend）是前端与后端微服务之间的中间层，为特定前端提供专属接口 |
| 能做什么 | 聚合多微服务数据、裁剪格式、统一认证、适配多端差异 |
| 怎么用 | 使用 Express/Nest.js 等框架搭建 BFF 服务，前端调用 BFF 单一接口 |
| 原理和工作流程 | BFF 层接收前端请求，并行调用多个后端微服务，聚合结果后按前端需要格式返回。BFF 统一处理认证、鉴权、日志、限流。为不同前端（Web/移动端/小程序）提供各自专属的 BFF |
| 缺点 | 增加架构复杂度；可能成为单点故障 |

---

## 三、场景设计题（5 题，附思路）

| 维度 | 内容 |
|------|------|
| 是什么 | 场景设计题覆盖高并发 API 服务设计、Node.js 中间层架构、实时通信系统、大文件上传服务、前端监控日志收集服务 |
| 能做什么 | 考查综合运用 Node.js 知识解决实际工程问题的能力 |
| 怎么用 | 先独立设计方案，再对照参考答案补充遗漏部分 |
| 原理和工作流程 | 题目按难度分布：中档题（1-2、4 题）考查服务设计和架构，拔高题（3、5 题）考查实时通信和监控系统 |
| 缺点 | 场景设计需要综合能力和架构思维 |

### 1. 设计一个高并发 REST API 服务

| 维度 | 内容 |
|------|------|
| 是什么 | 涵盖技术选型（Express/Koa）、中间件配置、数据库连接池、连接池优化、缓存策略（Redis）、错误处理、日志、进程管理（PM2）的完整设计 |
| 能做什么 | 提供高并发 Node.js 服务的最佳实践方案 |
| 怎么用 | 技术选型：Express + MySQL + Redis；中间件：body-parser、cors、helmet、rate-limit；连接池：poolSize 合理配置；缓存：Redis 缓存热点数据；进程管理：PM2 cluster 模式 |
| 原理和工作流程 | 连接池避免每次请求新建连接（提升响应速度）、PM2 多进程利用多核 CPU、Redis 缓存减少数据库压力、rate-limit 限制请求频率防止恶意攻击、结构化日志便于排查问题、统一错误处理中间件返回规范化错误响应 |
| 缺点 | 需要根据实际业务调整缓存策略和连接池配置 |

### 2. 设计一个 Node.js 中间层实现前后端分离

| 维度 | 内容 |
|------|------|
| 是什么 | 作为 BFF 中间层，聚合多个后端微服务数据，统一认证、鉴权、日志、限流，为前端提供专属接口 |
| 能做什么 | 解决前端多接口调用、数据格式不匹配、多端差异等问题 |
| 怎么用 | 使用 Express/Nest.js 搭建 BFF 服务，前端请求 BFF 接口，BFF 并行调用多个微服务，聚合结果返回 |
| 原理和工作流程 | 统一认证在 BFF 层处理，前端只需要传 token，BFF 将认证信息传递给后端服务。聚合层使用 Promise.all 并行调用多个微服务接口，组装结果。为不同前端（Web/移动端/小程序）提供各自专属的 BFF 服务 |
| 缺点 | 增加网络跳转，需处理局部失败和降级 |

### 3. 设计一个实时通信系统

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 Socket.IO 实现 WebSocket 实时通信，支持房间管理、消息持久化、认证鉴权、水平扩展（Redis Adapter） |
| 能做什么 | 支持聊天、实时协作、通知推送等场景 |
| 怎么用 | Socket.IO 搭建 WebSocket 服务；`socket.join('room1')` 房间管理；Redis Adapter 实现多进程消息广播 |
| 原理和工作流程 | 客户端连接 WebSocket 建立长连接，服务端管理连接池和房间。消息持久化存储到数据库（MongoDB/MySQL），离线消息上线后推送。多进程通过 Redis Adapter 实现跨进程消息广播（emit 到 Redis，所有进程监听 Redis 事件）。认证通过 Socket.IO 的 auth 中间件验证 token |
| 缺点 | 长连接占用服务器资源；水平扩展需 Redis 等外部存储 |

### 4. 设计一个大文件上传服务

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 multer 处理文件上传，支持分片上传、断点续传、秒传、并发控制 |
| 能做什么 | 解决大文件上传超时、失败后需重传整个文件的问题 |
| 怎么用 | 前端：Blob.slice 分片 + spark-md5 哈希；后端：multer 接收分片，上传完成后合并分片 |
| 原理和工作流程 | 前端切分文件为多个分片（如 5MB/片），计算文件哈希，并发上传分片。后端检查已上传分片列表（断点续传），根据文件哈希判断是否已存在（秒传）。所有分片上传完成后合并分片。并发控制限制同时上传的分片数量（3-5 个） |
| 缺点 | 需要前后端配合；合并分片需要额外磁盘 I/O |

### 5. 设计一个前端监控日志收集服务

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 POST 接口接收前端上报的错误日志和性能数据，写入日志文件（按天轮转），支持查询和统计 |
| 能做什么 | 收集前端错误日志和性能数据，为问题排查和性能优化提供数据支撑 |
| 怎么用 | 前端：错误捕获后 POST 到 `/api/logs`；后端：接收日志写入文件（winston 按天轮转），提供查询接口 |
| 原理和工作流程 | 数据接收：Express 服务接收 POST 日志，签名验证防伪造请求，写入日志队列。日志存储：winston 按天轮转日志文件，性能数据写入时序数据库（如 InfluxDB）。查询统计：按时间范围、错误类型、页面 URL 过滤查询，统计错误率和性能指标 |
| 缺点 | 高并发下日志写入可能成为瓶颈；需要处理日志存储空间和清理策略 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./03-Node.js笔面试题集.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)