# 05-Node性能调优与内存排查 导览

> 定位：五维框架浓缩提炼 05-Node性能调优与内存排查.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./05-Node性能调优与内存排查.md)。
> 前置知识：[01-Node运行时与核心API](./01-Node运行时与核心API.md)、[02-Web框架与BFF层](./02-Web框架与BFF层.md)、[04-数据库与ORM](./04-数据库与ORM.md)

---

## 一、核心概念

| 维度 | 内容 |
|------|------|
| 是什么 | Node.js 性能调优与内存排查是围绕四类线上症状（响应变慢 / 内存持续上涨 / 进程不退出 / 偶发超时）建立的"测量 → 定位 → 修复 → 验证"体系 |
| 能做什么 | 判断问题属于 CPU 瓶颈、内存泄漏、句柄泄漏还是 GC 停顿，并选择正确的工具链完成定位 |
| 怎么用 | CPU 问题用 `--cpu-prof` / `0x` / `clinic flame`；内存问题用 `process.memoryUsage()` 采样 + Heap Snapshot 三快照法；进程不退出用 `why-is-node-running`；偶发卡顿用 `perf_hooks.monitorEventLoopDelay()`；容量评估用 autocannon / k6 |
| 原理和工作流程 | 四条核心原则：先测量再优化（没有 profiling 数据的优化都是猜测）；关注分位数而非平均值（P95 / P99 才是体验边界）；区分 CPU 密集与 I/O 密集（CPU 密集必须卸载到 `worker_threads`）；区分 V8 堆内存与外部内存（`heapUsed` 不含 Buffer） |
| 缺点 | 排查依赖真实流量与生产环境数据，本地难以复现；profiling 本身有性能开销，需权衡采样粒度；部分工具（clinic.js）已进入低维护状态 |

---

## 二、底层原理

### Node 性能分析工具链

| 维度 | 内容 |
|------|------|
| 是什么 | 一套从"最低成本采样"到"可视化火焰图"的工具体系：`--prof`、`--cpu-prof`、`--inspect`、`0x`、`clinic.js`，以及事件循环延迟监控 |
| 能做什么 | 采集 CPU 调用栈、生成火焰图、导出可交互的 `.cpuprofile`、实时监控事件循环阻塞程度 |
| 怎么用 | `node --prof app.js` + `node --prof-process isolate-*.log > processed.txt`；`node --cpu-prof --cpu-prof-dir=./profiles --cpu-prof-interval=500 app.js`；`node --inspect=0.0.0.0:9229 app.js` 后访问 `chrome://inspect`；`npx 0x app.js`；`npx clinic doctor -- node app.js`；`monitorEventLoopDelay({ resolution: 20 })` |
| 原理和工作流程 | `--prof` 让 V8 以固定频率采样调用栈，报告按 ticks 占比排序，`[Summary]` 中 GC 占比超 10% 说明内存压力大；`--cpu-prof` 直接产出 DevTools 可加载的 profile；`0x` 基于 V8 CPU profile 生成火焰图，横轴是采样占比、纵轴是调用栈深度，重点看"宽而平"的矩形（自身热点）；`clinic doctor` 会直接给出结论式建议；事件循环延迟是最核心的健康指标，P99 长期超 100ms 说明存在明显阻塞 |
| 缺点 | `--prof` 需要手工转换且报告可读性一般；火焰图采样期间必须有真实流量，否则只反映空转；`--inspect` 暴露任意代码执行能力，绝不能在生产开放到公网；clinic.js 已进入低维护状态，不宜作为唯一依赖 |

### CPU 瓶颈定位流程

| 维度 | 内容 |
|------|------|
| 是什么 | 从"CPU 高 / 响应变慢"现象出发，到确认瓶颈归属、采样、定位热点、分类处理、验证的标准化流程 |
| 能做什么 | 避免"盲优化"，快速判断瓶颈在 Node 进程内部还是下游服务，并把热点归入可处理的类别 |
| 怎么用 | ① `top -H -p <pid>` 看线程级 CPU；② `monitorEventLoopDelay()` 判断主线程是否被阻塞；③ 有真实流量时用 `--cpu-prof` / `0x` 采样；④ 按自耗时排序找热点函数；⑤ 分类处理（算法优化 / Worker 卸载 / 异步 API / 转内存排查）；⑥ 相同压测条件复测 |
| 原理和工作流程 | 事件循环延迟高 → 主线程被阻塞，问题在进程内部；延迟正常但响应慢 → 瓶颈在下游（数据库 / 外部 API / 磁盘）。热点分类：业务算法热点做算法优化或加缓存；无法优化的纯计算卸载到 `worker_threads`；`JSON.parse` / `JSON.stringify` 热点减少数据量与深拷贝；`crypto` / `zlib` 热点改用异步 API（走 libuv 线程池）；GC 热点转向内存排查 |
| 缺点 | 采样需要覆盖问题出现的时间窗口，短时采样可能错过偶发热点；火焰图只能反映采样期内的 CPU 分布，无法反映 I/O 等待 |

### V8 堆结构与内存管理

| 维度 | 内容 |
|------|------|
| 是什么 | V8 堆的空间划分（New Space / Old Space / Large Object Space / Code Space / Map Space）、回收算法（Scavenge 与 Mark-Sweep-Compact）、`process.memoryUsage()` 的五个字段，以及 Heap Snapshot 三快照法 |
| 能做什么 | 区分"GC 未触发导致的堆增长"与"真正的内存泄漏"；区分 V8 堆内存与外部内存（Buffer）；精确定位泄漏对象与其引用链 |
| 怎么用 | `process.memoryUsage()` 采样 `rss` / `heapTotal` / `heapUsed` / `external` / `arrayBuffers`；`v8.getHeapSpaceStatistics()` 看各空间用量；`v8.writeHeapSnapshot()` 或 `--heapsnapshot-signal=SIGUSR2` 导出快照；DevTools Memory 面板用 Comparison 视图做三快照对比 |
| 原理和工作流程 | New Space 分为 `from` / `to` 两个半空间（64 位系统默认约 16MB），Scavenge 用 Cheney 复制算法把存活对象复制到 `to-space`（复制即压缩），经两轮 Scavenge 仍存活的对象晋升到 Old Space；Old Space 用三色标记 + 增量标记 + 写屏障 + 并发清除 + 按碎片率触发的压缩。`heapUsed` 不包含 Buffer 内存（Buffer 计入 `external` 与 `arrayBuffers`），`rss` 才是容器 OOM Killer 的判断依据。三快照法：基线 → 执行操作 → 快照 2 → 再执行同一操作 → 快照 3，对比快照 2 与 3，`Delta` 线性增长且未被回收的对象即泄漏，再用 `Retainers` 展开从 GC Root 到该对象的引用链 |
| 缺点 | 单张 Heap Snapshot 无法区分正常缓存与泄漏；快照文件可达数百 MB，抓取时会造成明显停顿；`Retainers` 引用链在复杂框架下较长，定位到具体代码需要经验；`rss` 包含 C++ 对象与内存碎片，与"真实存活量"有偏差 |

### 内存泄漏常见成因

| 维度 | 内容 |
|------|------|
| 是什么 | 九类典型成因：意外的全局变量、全局容器累积、闭包持有大对象、事件监听未移除、定时器未清理、缓存无上限、Buffer / ArrayBuffer 未释放、未取消的异步任务、全局单例持有请求上下文 |
| 能做什么 | 在编码阶段规避绝大多数泄漏，并在排查时按成因清单逐项检查 |
| 怎么用 | 严格模式 + `let` / `const` 避免意外全局；缓存用 LRU + 最大条目数 + TTL；事件监听用 `once` 或在销毁时 `off`；定时器在生命周期结束时 `clearInterval`；大 Buffer 用 `Buffer.from(buf)` 复制独立内存；请求上下文改用 `AsyncLocalStorage`；用 `FinalizationRegistry` 辅助验证对象是否被回收 |
| 原理和工作流程 | 泄漏的本质是"本不该存在的引用链仍在"，导致对象始终可达、无法被标记清除。全局容器与缓存无上限属于"只增不减"；闭包与监听器属于"引用被长期持有"；Buffer 泄漏属于外部内存，`heapUsed` 看不到但 `rss` 持续上涨；`Buffer.slice` / `subarray` 会与底层内存共享，容易"意外持有"整块大内存 |
| 缺点 | 部分成因（如第三方库内部的缓存）无法从业务代码直接看出，需要用 Retainers 反查；`FinalizationRegistry` 的回调时机不确定，只能辅助判断；泄漏往往在长周期运行后才暴露，本地测试难以发现 |

### GC 调优参数

| 维度 | 内容 |
|------|------|
| 是什么 | `--max-old-space-size`（老生代上限）、`--max-semi-space-size`（新生代单个 semi-space 上限）、`--expose-gc`（暴露 `global.gc()`），以及观察 GC 行为的 `--trace-gc` / `--trace-gc-verbose` |
| 能做什么 | 在内存与停顿之间做权衡；避免容器内进程被 OOM Killer 静默杀掉；为 Worker 单独限制堆大小 |
| 怎么用 | `node --max-old-space-size=4096 app.js`；`node --max-semi-space-size=64 app.js`；`node --trace-gc app.js`；`Worker` 的 `resourceLimits: { maxOldGenerationSizeMb, maxYoungGenerationSizeMb, stackSizeMb }`；用 `PerformanceObserver` 监听 `entryTypes: ['gc']` 统计 GC 耗时占比 |
| 原理和工作流程 | `--max-old-space-size` 设为容器内存上限的 70%-80%，留出空间给 `external` 内存（Buffer）、C++ 对象、代码段与运行时；`--max-semi-space-size` 调大则 Scavenge 频率降低但单次停顿变长、内存占用上升，调小则相反。Node 12+ 在推导默认堆上限时会考虑 cgroup 限制，但不同版本与运行时规则不同，显式设置最稳妥 |
| 缺点 | 只设置容器 limit 而不设置堆上限最危险——V8 堆未达上限但 `rss` 超过 limit 时进程被直接杀掉，**不会产生 JS 层错误与堆栈**；GC 参数需要结合真实内存曲线反复试验，过度调大反而拉长单次停顿；`--expose-gc` 仅用于排查，不应在生产依赖 |

### 句柄泄漏与进程退出排查

| 维度 | 内容 |
|------|------|
| 是什么 | 事件循环中残留活跃 handle（定时器、socket、文件描述符）或 request（进行中的 I/O），导致进程收到 `SIGTERM` 后不退出或脚本执行完"卡住" |
| 能做什么 | 快速定位"谁在阻止进程退出"，并完善优雅关闭流程 |
| 怎么用 | `require('why-is-node-running')()` 打印活跃 handle 及创建位置的调用栈；`process._getActiveHandles()` / `process._getActiveRequests()` 查看活跃资源类型；后台定时器加 `.unref()`；优雅关闭流程为"停止接收新请求 → 依次关闭数据库 / Redis / Worker → 超时兜底 `process.exit(1)`" |
| 原理和工作流程 | 事件循环只有在没有活跃 handle 与 request 时才会清空并退出。常见来源：未清理的 `setInterval`（CPU 空转且阻止退出）、未关闭的数据库连接、未销毁的 keep-alive socket、未关闭的文件描述符（最终 `EMFILE`）、未移除的 `EventEmitter` 监听。`.unref()` 让定时器不参与"是否有活跃工作"的判断，适合"只需在进程存活期间运行"的后台任务 |
| 缺点 | `process._getActiveHandles()` / `_getActiveRequests()` 是内部 API（下划线开头），不保证跨版本稳定，仅用于排查；`why-is-node-running` 需要额外依赖；优雅关闭的超时时长需要结合业务请求耗时设置 |

### 压测与基准测试

| 维度 | 内容 |
|------|------|
| 是什么 | 用 autocannon / k6 做端到端压测，用 `node:perf_hooks` 做函数级微基准，评估吞吐、延迟分布与容量 |
| 能做什么 | 量化优化效果；评估容量上限；在 CI 中设置性能阈值防止回归 |
| 怎么用 | `npx autocannon -c 100 -d 30 -w 5 -p 10 http://localhost:3000/api/users`；k6 用 `export const options = { stages: [...], thresholds: { http_req_duration: ['p(95)<500'] } }` 定义阶段式负载与阈值；微基准用 `performance.now()` 包裹循环并做预热 |
| 原理和工作流程 | 五项原则：必须有预热（JIT 需要时间达到稳定优化状态）；压测机与被测服务分离；关注 P95 / P99 与错误率而非平均 QPS；区分吞吐测试与延迟测试；固定并记录环境变量。autocannon 结果中 Latency 的 p99 与 avg 差距超过 3 倍说明存在长尾，Non-2xx responses / Errors / Timeouts 必须为 0 |
| 缺点 | 微基准受 V8 的 JIT 优化（内联缓存、死代码消除）影响，结论严重偏离真实场景，只能做同环境相对比较；压测结果受机器配置、网络与数据库状态影响，跨环境不可直接对比 |

### Serverless 场景

| 维度 | 内容 |
|------|------|
| 是什么 | Serverless（FaaS）把"进程常驻"变成"按请求启动 / 复用实例"，优化重点从"常驻进程吞吐"转为"冷启动"与"无状态约束" |
| 能做什么 | 降低冷启动延迟；在无状态约束下正确设计会话与缓存；避免数据库连接数被弹性扩容打爆 |
| 怎么用 | 冷启动：减小包体积（只装生产依赖 + esbuild 打包单文件）、延迟初始化 + 动态 `import()`、减少模块顶层副作用、客户端初始化提到模块作用域、提高内存配置、预留并发；无状态：会话外置到 Redis / 数据库 / JWT，`/tmp` 只作临时缓存，handler 必须幂等；连接池：池大小设为 1，或用 PgBouncer / RDS Proxy，或改用 HTTP 协议访问数据库 |
| 原理和工作流程 | 冷启动分"初始化阶段"（下载代码、启动运行时、加载依赖、执行模块顶层代码）与"调用阶段"，优化目标是压缩初始化阶段。总连接数 = `实例数 × 单实例池大小`，弹性扩容时容易超过数据库 `max_connections`。Vercel 的 Serverless Functions 有完整 Node 运行时，Edge Functions 基于 Web 标准 API（无 Node 内置模块、无原生依赖、无长连接）；AWS Lambda 的内存与 CPU 成正比、执行环境会复用（模块作用域变量在热启动间保留）、`/tmp` 默认 512MB 且实例回收即丢失、超时上限 15 分钟但前面挂 API Gateway 时还要受其约 29 秒限制 |
| 缺点 | 预留并发可彻底消除冷启动但成本显著上升；外部连接池代理增加架构复杂度与一次网络跳转；Serverless 实例会被回收，无法依赖进程内后台定时任务；Node.js 运行时默认等待事件循环清空，keep-alive 连接会导致调用卡到超时（需 `context.callbackWaitsForEmptyEventLoop = false`） |

---

## 三、实战应用

### 一次内存泄漏的完整排查过程

| 维度 | 内容 |
|------|------|
| 是什么 | 从"`rss` 6 小时从 200MB 涨到 1.8GB 后被 OOM 杀掉"到定位并修复的完整案例 |
| 能做什么 | 演示"先区分泄漏与 GC 未触发 → 三快照定位对象 → Retainers 找引用链 → 修复并验证"的标准路径 |
| 怎么用 | ① 定时采样 `rss` / `heapUsed` / `external` / `arrayBuffers`；② 用 `--heapsnapshot-signal=SIGUSR2` 抓三张快照；③ DevTools Comparison 视图对比快照 2 与 3；④ `Retainers` 展开引用链；⑤ 修复后重新采样验证 |
| 原理和工作流程 | 采样发现 `heapUsed` 稳定但 `rss` 与 `external` 持续上涨 → 判断为**外部内存**问题而非 V8 堆问题；三快照对比发现 `ArrayBuffer` 类型新增两个约 50MB 实例且未回收；`Retainers` 引用链为 `(GC roots) → global → reportCache → Map → ArrayBuffer`，定位到"把生成的大 Buffer 缓存进无上限 Map"；修复方案是加容量上限 + TTL，并把大文件写入对象存储、缓存里只留 URL |
| 缺点 | 需要服务支持信号触发快照或提供导出接口，线上改造有成本；三张快照的抓取会引入明显停顿，需在低峰期进行 |

### 一次 CPU 飙高的定位过程

| 维度 | 内容 |
|------|------|
| 是什么 | 从"接口 P99 从 80ms 涨到 1.5s、CPU 95%、事件循环延迟 P99 超 800ms"到定位并修复的完整案例 |
| 能做什么 | 演示"事件循环延迟确认 → CPU profile 采样 → 火焰图定位 → 分类优化 → 复测"的标准路径 |
| 怎么用 | ① `monitorEventLoopDelay()` 确认主线程阻塞；② `node --cpu-prof --cpu-prof-dir=./profiles --cpu-prof-interval=500 app.js` 采样；③ 把 `.cpuprofile` 拖入 DevTools Performance 面板按自耗时排序；④ 优化：只记录审计必需字段，非关键路径改为异步批量；⑤ 复测 P99 与 CPU 使用率 |
| 原理和工作流程 | 火焰图显示 `JSON.stringify` 与 `structuredClone` 合计占 45% CPU，调用栈指向"每次请求都对完整订单对象做深拷贝用于审计日志"；优化后 P99 从 1.5s 回落到 90ms，CPU 从 95% 降到 35%。日志这类非关键路径用队列 + 定时批量刷盘，避免阻塞响应 |
| 缺点 | 采样间隔调小可提高精度但增加开销，需要权衡；火焰图无法反映下游 I/O 等待，需结合 APM 一起判断 |

### Serverless 冷启动优化实践

| 维度 | 内容 |
|------|------|
| 是什么 | 从"冷启动 P95 2.8s、热启动 P95 120ms"到优化到"冷启动 P95 700ms"的完整案例 |
| 能做什么 | 演示如何用打点定位冷启动瓶颈，并按收益排序选择优化手段 |
| 怎么用 | ① 在模块顶层与 handler 内打点，分段计时；② 把重型 SDK 换成基于 `undici` 的轻量封装；③ 只在特定路径用动态 `import()`；④ 用 esbuild 打包成单文件减少模块解析开销；⑤ 连接池改为 PgBouncer 外部代理，单实例连接数降为 1 |
| 原理和工作流程 | 打点显示依赖加载占 1400ms，是冷启动的主要瓶颈；换成轻量封装后降到 180ms。动态 `import()` 把重依赖的成本从"冷启动关键路径"移到"首次使用时"，代价是该路径首次调用变慢。连接池从每实例 10 个改为 1 个 + 外部代理后，200 实例峰值下数据库连接数从 2000 降到 200 |
| 缺点 | 延迟初始化把成本转移给首次调用，需要评估该路径的调用频率；动态 `import()` 增加代码复杂度；引入 PgBouncer 等外部连接池增加运维成本与一次网络跳转 |

---

## 四、常见面试题

### CPU 飙高的排查思路

| 维度 | 内容 |
|------|------|
| 是什么 | 考察从"确认瓶颈归属"到"验证修复效果"的完整排查链路，是 Node.js 进阶面试的高频题 |
| 能做什么 | 验证候选人是否具备"用数据说话"的排查习惯，而不是凭直觉改代码 |
| 怎么用 | 回答要点：`top -H -p <pid>` 看线程级 CPU → `monitorEventLoopDelay()` 判断主线程是否阻塞 → 有流量时用 `--cpu-prof` / `0x` 采样 → 按自耗时排序定位热点 → 分类处理（算法 / Worker 卸载 / 异步 API / 转内存排查）→ 相同压测条件复测 |
| 原理和工作流程 | 事件循环延迟高说明主线程被阻塞（问题在进程内）；延迟正常但响应慢说明瓶颈在下游。热点分类：业务算法做优化或加缓存；纯计算卸载到 `worker_threads`；`JSON` / `crypto` / `zlib` 热点改用异步 API 或减少数据量；GC 热点转向内存排查 |
| 缺点 | 生产环境采样需要权衡开销；偶发热点需要长时间采样才能捕获；火焰图不反映 I/O 等待 |

### `process.memoryUsage()` 字段含义与泄漏判断

| 维度 | 内容 |
|------|------|
| 是什么 | 考察 `rss` / `heapTotal` / `heapUsed` / `external` / `arrayBuffers` 五个字段的含义，以及"内存泄漏该看哪个" |
| 能做什么 | 区分"GC 未触发导致的堆增长"与"真正的内存泄漏"，并识别 Buffer 类外部内存泄漏 |
| 怎么用 | 回答要点：`rss` 是进程物理内存（OOM Killer 的判断依据）；`heapTotal` 是 V8 已申请的堆总量；`heapUsed` 是堆内对象占用（含未回收垃圾）；`external` 是绑定到 JS 对象的 C++ 侧内存（含 Buffer）；`arrayBuffers` 是 `ArrayBuffer` / `SharedArrayBuffer` 内存，是 `external` 的子集 |
| 原理和工作流程 | `heapUsed` 上涨不一定是泄漏，GC 未触发时会积累垃圾，必须看多次 GC 后的基线是否持续抬高。**Buffer 的内存不计入 `heapUsed`**，因此"`heapUsed` 稳定但 `rss` 持续上涨"是典型的 Buffer / ArrayBuffer 泄漏特征，此时要看 `external` 与 `arrayBuffers` |
| 缺点 | 只有 `--expose-gc` 才能主动触发 GC 获得"真实存活量"，生产环境不便使用；`rss` 包含 C++ 对象与内存碎片，与真实存活量有偏差 |

### Heap Snapshot 三快照法

| 维度 | 内容 |
|------|------|
| 是什么 | 通过"抓基线 → 执行操作 → 抓快照 2 → 再执行同一操作 → 抓快照 3"暴露增量，从而区分泄漏与正常缓存 |
| 能做什么 | 精确识别泄漏对象类型，并通过 `Retainers` 引用链定位到具体代码 |
| 怎么用 | 抓快照 1 → 执行一次可疑操作 → 抓快照 2 → 再执行一次 → 抓快照 3 → 选中快照 3，用 Comparison 视图对比快照 2，筛选 "Objects allocated between Snapshot 2 and Snapshot 3"；重点看 `# New` / `# Deleted` / `# Delta` 三列与 `Retainers` |
| 原理和工作流程 | 单张快照无法区分"应有的对象"与"泄漏的对象"，必须靠"重复同一操作"暴露增量。判读规则：某类对象的 `Delta` 随操作次数**线性增长**，且操作结束后仍存活（快照 2 中已存在又未回收），即为泄漏；正常缓存的特征是"数量有上限或能被 TTL 淘汰"。找到对象后展开 `Retainers`，沿 GC Root 到该对象的引用链找到持有者 |
| 缺点 | 快照文件可达数百 MB，抓取时停顿明显；`Retainers` 引用链在复杂框架下可能很长；需要能在目标环境触发快照（信号或接口），线上改造有成本 |

### 常见内存泄漏成因

| 维度 | 内容 |
|------|------|
| 是什么 | 考察九类典型成因及其修复方式 |
| 能做什么 | 在编码阶段规避绝大多数泄漏，并在排查时按清单逐项核对 |
| 怎么用 | 回答要点：意外的全局变量（严格模式 + `let` / `const`）；全局容器累积（LRU + TTL）；闭包持有大对象（只捕获必要字段）；事件监听未移除（`once` / `off`）；定时器未清理（`clearInterval`）；缓存无上限（LRU + 最大条目数）；`Buffer` / `ArrayBuffer` 未释放（`Buffer.from` 复制独立内存）；未取消的异步任务（`AbortController`）；全局单例持有请求上下文（改用 `AsyncLocalStorage`） |
| 原理和工作流程 | 泄漏的本质是"本不该存在的引用链仍在"，对象始终可达而无法被标记清除。全局容器与无上限缓存是"只增不减"；闭包与监听器是"引用被长期持有"；`Buffer.slice` / `subarray` 会与底层内存共享，容易意外持有整块大内存；Buffer 属于外部内存，`heapUsed` 看不到但 `rss` 持续上涨 |
| 缺点 | 第三方库内部的缓存无法从业务代码看出，需用 `Retainers` 反查；泄漏往往在长周期运行后才暴露，本地难以复现 |

### `--max-old-space-size` 的作用与容器配置

| 维度 | 内容 |
|------|------|
| 是什么 | 设置 V8 老生代堆上限（单位 MB），是最常用的 GC 调优参数 |
| 能做什么 | 在内存占用与 GC 停顿之间做权衡；避免容器内进程被 OOM Killer 静默杀掉 |
| 怎么用 | `node --max-old-space-size=4096 app.js`；容器中设为容器内存上限的 70%-80%；`Worker` 用 `resourceLimits: { maxOldGenerationSizeMb, maxYoungGenerationSizeMb, stackSizeMb }` 单独限制 |
| 原理和工作流程 | 设 70%-80% 是为了留出空间给 `external` 内存（Buffer）、C++ 对象、代码段与运行时本身。Node 12+ 在推导默认堆上限时会考虑 cgroup 限制，但不同版本与运行时规则不同，显式设置最稳妥。最危险的场景是"只设容器 limit 不设堆上限"：V8 堆未达上限但 `rss` 超过 limit 时进程被直接杀掉，**不会产生 JS 层错误与堆栈**，排查时毫无线索 |
| 缺点 | 参数需要结合真实内存曲线反复试验；调得过大导致单次 GC 停顿变长、OOM 风险上升；调得过小导致 GC 频繁、吞吐下降 |

### 进程不退出与句柄泄漏

| 维度 | 内容 |
|------|------|
| 是什么 | 事件循环中残留活跃 handle 或 request 导致进程收到 `SIGTERM` 后不退出 |
| 能做什么 | 快速定位"谁在阻止退出"，并完善优雅关闭流程 |
| 怎么用 | `require('why-is-node-running')()` 打印活跃 handle 及创建位置的调用栈；`process._getActiveHandles()` / `process._getActiveRequests()`（内部 API）查看资源类型；后台定时器加 `.unref()`；优雅关闭流程为"停止接收新请求 → 关闭数据库 / Redis / Worker → 超时兜底 `process.exit(1)`" |
| 原理和工作流程 | 事件循环只有在没有活跃 handle 与 request 时才清空退出。常见来源：未清理的 `setInterval`、未关闭的数据库连接、未销毁的 keep-alive socket、未关闭的文件描述符（最终 `EMFILE`）、未移除的 `EventEmitter` 监听。`.unref()` 让定时器不参与"是否有活跃工作"的判断 |
| 缺点 | `_getActiveHandles` / `_getActiveRequests` 是内部 API，不保证跨版本稳定；`why-is-node-running` 需额外依赖；优雅关闭超时时长需结合业务请求耗时设置 |

### autocannon 与 k6 的差异及压测要点

| 维度 | 内容 |
|------|------|
| 是什么 | autocannon 是零脚本的命令行压测工具；k6 是用 JavaScript 编写脚本、支持阶段式负载与阈值断言的压测平台 |
| 能做什么 | 快速测接口吞吐与延迟分布；构建可进 CI 的复杂压测场景 |
| 怎么用 | `npx autocannon -c 100 -d 30 -w 5 -p 10 <url>`；k6 用 `export const options = { stages: [{ duration: '30s', target: 50 }], thresholds: { http_req_duration: ['p(95)<500'], http_req_failed: ['rate<0.01'] } }` |
| 原理和工作流程 | autocannon 关注 Req/Sec、Latency 分位数（avg / p50 / p97.5 / p99 / max）、Throughput、Non-2xx / Errors / Timeouts；p99 与 avg 差距超 3 倍说明存在长尾。五项原则：必须有预热（JIT 需要时间稳定）；压测机与被测服务分离；关注分位数与错误率而非平均 QPS；区分吞吐与延迟目标；固定并记录环境变量（CPU 核数、Node 版本、堆上限、数据库状态） |
| 缺点 | 压测结果受机器、网络与数据库状态影响，跨环境不可直接对比；微基准受 V8 的 JIT 优化影响严重偏离真实场景，只能做同环境相对比较 |

### Serverless 数据库连接池的坑

| 维度 | 内容 |
|------|------|
| 是什么 | 每个 Serverless 实例都有独立连接池，总连接数 = `实例数 × 单实例池大小`，弹性扩容时容易打爆数据库 `max_connections` |
| 能做什么 | 在弹性扩缩场景下保护数据库连接数；避免偶发 `Connection terminated` |
| 怎么用 | 池大小设为 1；用外部连接池代理（PgBouncer / RDS Proxy）；用 HTTP 协议访问数据库的 serverless driver；配置连接超时与重试；不要在每个 handler 里 `$disconnect`；用全局单例避免热启动重复建连 |
| 原理和工作流程 | 实例数随并发弹性扩缩，单实例池越大，总连接数越容易超过数据库上限。实例被回收后长连接会失效，必须有超时与重试，否则出现偶发连接错误。`$disconnect` 会导致热启动反复建连，反而放大冷启动成本 |
| 缺点 | 外部连接池代理增加架构复杂度与一次网络跳转；HTTP 数据访问方案受数据库支持范围限制；池大小设为 1 时单实例内部无法并发查询 |

### Serverless 冷启动与无状态约束

| 维度 | 内容 |
|------|------|
| 是什么 | 冷启动由"初始化阶段"与"调用阶段"构成；无状态约束包括实例不固定、本地磁盘不共享、内存不共享、实例会被回收 |
| 能做什么 | 降低冷启动延迟；在无状态约束下正确设计会话、缓存与幂等 |
| 怎么用 | 冷启动：减小包体积（只装生产依赖 + esbuild 打包单文件）、延迟初始化 + 动态 `import()`、减少模块顶层副作用、客户端初始化提到模块作用域、提高内存配置、预留并发；无状态：会话外置到 Redis / 数据库 / JWT，`/tmp` 只作临时缓存，handler 必须幂等 |
| 原理和工作流程 | 优化目标是压缩初始化阶段（下载代码、启动运行时、加载依赖、执行模块顶层代码）。Vercel 的 Serverless Functions 有完整 Node 运行时，Edge Functions 基于 Web 标准 API（无 Node 内置模块、无原生依赖、无长连接）；AWS Lambda 的内存与 CPU 成正比、执行环境会复用（模块作用域变量在热启动间保留）、`/tmp` 默认 512MB 且实例回收即丢失、超时上限 15 分钟但前面挂 API Gateway 时还要受其约 29 秒限制、Node.js 运行时默认等待事件循环清空（需 `context.callbackWaitsForEmptyEventLoop = false`） |
| 缺点 | 预留并发成本显著上升；延迟初始化把成本转移给首次调用；外部连接池与离线包等方案增加运维复杂度；进程内后台定时任务不可依赖 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 性能调优与内存排查中的典型错误：无 profiling 就优化、只看 `heapUsed`、单张快照下结论、只设容器 limit 不设堆上限、生产开放 `--inspect`、压测不预热或同机压测、只看平均延迟、Serverless 池过大或 handler 内初始化、进程内变量存会话、定时器未 `unref()`、Lambda keep-alive 导致超时、微基准直接推断线上、把 CPU 密集写成 `async` 就以为不阻塞 |
| 能做什么 | 帮助开发者提前识别性能排查中的常见误区，避免"优化了但没效果"甚至"越优化越差" |
| 怎么用 | 对照排查：先用 `--cpu-prof` / `0x` 采样再动手；同时监控 `rss` / `heapUsed` / `external` / `arrayBuffers` 四个指标；用三快照法而非单张快照；`--max-old-space-size` 设为容器上限的 70%-80%；`--inspect` 只通过内网或 SSH 隧道访问；压测加预热参数并分离压测机；关注 P95 / P99 与错误率；Serverless 池大小设为 1 + 外部代理；会话外置；定时器加 `.unref()`；Lambda 设置 `callbackWaitsForEmptyEventLoop = false`；微基准只做同环境相对比较；CPU 密集任务用 `worker_threads` 卸载 |
| 原理和工作流程 | 常见错误根源：凭直觉猜测热点导致改的不是真瓶颈；`Buffer` 内存计入 `external` 不计入 `heapUsed` 导致漏判外部内存泄漏；单张快照无法区分正常缓存与泄漏；V8 堆未达上限但 `rss` 超容器 limit 时进程被 OOM Killer 静默杀掉且无 JS 堆栈；`--inspect` 暴露任意代码执行能力；JIT 未稳定导致压测前几秒数据失真；平均值掩盖长尾；Serverless 总连接数 = 实例数 × 单实例池大小；依赖加载与连接建立进入冷启动关键路径；活跃 handle 让事件循环无法清空；Node.js 运行时默认等待事件循环清空导致 Lambda 调用卡到超时；V8 的 JIT 优化让微基准偏离真实场景；`async` 不改变执行线程 |
| 缺点 | 部分问题（如内存泄漏、偶发卡顿）需要长周期监控与真实流量才能暴露；生产环境 profiling 有性能开销，需要在低峰期进行；Serverless 与容器环境的排查手段差异较大，经验难以直接迁移 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./05-Node性能调优与内存排查.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)
