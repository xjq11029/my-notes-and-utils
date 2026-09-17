# 05-SSR与Nuxt实战 导览

> 定位：五维框架浓缩提炼 05-SSR与Nuxt实战.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./05-SSR与Nuxt实战.md)。
> 前置知识：[Vue3核心语法](./01-Vue3核心语法-导览.md)、[响应式与编译优化](./02-响应式与编译优化-导览.md)、[路由与状态管理](./03-路由与状态管理-导览.md)

---

## 一、核心概念

### 为什么需要服务端渲染

| 维度 | 内容 |
|------|------|
| 是什么 | 服务端渲染（SSR）也称通用渲染（Universal Rendering）或同构渲染（Isomorphic Rendering）：服务端执行一遍组件代码，直接产出带内容的 HTML，客户端再执行一遍同样的代码把静态 HTML 激活为可交互应用，这一步称为水合（Hydration）。 |
| 能做什么 | 解决纯 CSR 的三个问题：首屏白屏时间长、SEO 不友好、弱网与低端设备体验差；同时让数据获取在服务端完成（可能更靠近数据库）。 |
| 怎么用 | 服务端用 `createSSRApp()` + `renderToString()` 产出 HTML；客户端用同一份 `createApp()` 逻辑 `mount()`，自动走水合分支。 |
| 原理和工作流程 | 服务端先渲染出 HTML 并响应给浏览器，浏览器立即显示内容；随后加载客户端 JS，客户端创建与服务端完全相同的应用实例，把 VNode 树与已有 DOM 逐一比对并挂上事件监听器，完成交互接管。 |
| 缺点 | 开发受限（浏览器 API 只能在特定生命周期使用、部分第三方库需特殊处理）、部署需要 Node 环境、服务端渲染耗 CPU（高流量必须配缓存）、同一份代码要在两个环境正确运行并处理状态隔离。 |

### 四种渲染模式对比与选型

| 维度 | 内容 |
|------|------|
| 是什么 | CSR（客户端渲染）、SSR（服务端渲染）、SSG（构建时静态生成）、ISR（增量静态再生，本质是按路由的缓存与再生策略，语义为 `stale-while-revalidate`）。 |
| 能做什么 | CSR 适合无需 SEO 的强交互应用（后台、编辑器、游戏）；SSR 适合内容型页面与需要 SEO 的电商营销页；SSG 适合数据构建期已知且不变的博客、文档站；ISR 适合需要低成本 + 数据有 TTL 延迟的商品/博客列表。 |
| 怎么用 | 选型路径：是否需要 SEO → 内容是否对每个用户相同 → 数据是否构建期已知 → 能否接受 TTL 延迟；落地时用 Nuxt 的 `ssr: false`（CSR）、默认 SSR、`routeRules` 的 `prerender`（SSG）/ `swr`（ISR/SWR）配置。 |
| 原理和工作流程 | CSR 首屏由浏览器渲染；SSR 每请求渲染；SSG 构建时渲染一次并由静态托管/CDN 分发；ISR 首次请求按需生成并缓存，未过期直接返回，过期后先返回旧内容、同时后台重新生成并更新缓存。生产常态是**混合渲染**：同一应用不同路由用不同策略。 |
| 缺点 | SSG **要求渲染数据对每个用户都相同**，含个性化内容（如当前登录用户）的页面不适用；ISR 有 TTL 延迟且 CDN 缓存能力依赖部署平台；SSR 服务端成本最高。 |

---

## 二、底层原理

### Hydration（水合）原理

| 维度 | 内容 |
|------|------|
| 是什么 | 客户端接管服务端静态 HTML 的过程：Vue 创建一个与服务端完全相同的应用实例，把 VNode 树与已有真实 DOM 逐一对应，为元素挂上事件监听器与应用动态属性。 |
| 能做什么 | 让服务端产出的静态 HTML 变为可交互应用；复用服务端 DOM 而不重建节点，避免首屏闪烁与重复渲染成本。 |
| 怎么用 | 服务端与客户端共享 `createSSRApp()` 的应用创建逻辑；客户端执行 `createApp().mount('#app')`，`createSSRApp` 标记的应用会走水合分支而非新建 DOM。 |
| 原理和工作流程 | 流程为：定位容器取得真实 DOM → 逐层遍历 VNode 与真实 DOM 比对类型与结构 → 匹配成功则复用节点只补充事件监听器与动态属性 → 匹配失败则丢弃并重建节点同时输出警告 → 完成后进入正常响应式更新。**两个关键结论**：水合阶段会执行两遍组件代码（服务端一遍、客户端一遍），任何「每次执行结果不同」的代码都会导致不匹配；水合期间服务端响应性默认被禁用（无用户交互与 DOM 更新）。 |
| 缺点 | 需要处理水合不匹配；服务端与客户端两遍执行意味着组件代码必须「通用」，不能依赖平台特有 API 与不可重复的副作用。 |

### 水合不匹配的原因与排查

| 维度 | 内容 |
|------|------|
| 是什么 | 水合不匹配（hydration mismatch）：预渲染的 HTML 的 DOM 结构不符合客户端应用的期望，Vue 比对失败。 |
| 能做什么 | 通过识别常见原因与排查手段，在开发阶段消除不匹配，避免「丢弃节点并重建」带来的渲染性能损失与首屏闪烁。 |
| 怎么用 | 排查四步：开发环境看控制台警告（`Hydration completed but contains mismatches`，含节点与组件栈）→ 生产用编译期特性标志 `__VUE_PROD_HYDRATION_MISMATCH_DETAILS__` 输出详情 → 二分法用 `<ClientOnly>` 包裹可疑组件 → 校验服务端 HTML 合法性。不可避免时用 `data-allow-mismatch`（Vue 3.5+），可选值 `text` / `children` / `class` / `style` / `attribute`。 |
| 原理和工作流程 | 常见原因：不合规范的 HTML 嵌套（如 `<div>` 放在 `<p>` 里被浏览器解析纠正）、渲染随机值（`Math.random()` / `Date.now()`）、服务端与客户端时区或语言环境不一致、渲染期读取浏览器 API（`window` / `localStorage`）、`v-if` 依赖客户端状态、第三方库或浏览器扩展在水合前修改了 DOM、自定义指令只实现了 `mounted` 而被 SSR 忽略、`Teleport` 目标设为 `body`。 |
| 缺点 | `data-allow-mismatch` 只是「承认这里对不上」的逃生舱，只消除警告，节点仍会被客户端重建，性能损失依然存在；依赖 `<ClientOnly>` 会让该部分内容失去 SEO 与首屏优势。 |

### Vue 3 原生 SSR API

| 维度 | 内容 |
|------|------|
| 是什么 | Vue 的服务端渲染 API 位于 `vue/server-renderer`：`renderToString`、流式渲染系列 API；应用侧用 `createSSRApp()` 创建支持水合的应用实例，用 `useSSRContext()` 访问渲染上下文。 |
| 能做什么 | 在 Node.js 中把 Vue 应用渲染为 HTML 字符串或流；通过 SSR 上下文对象在渲染过程中收集数据（典型是收集要写进 `<head>` 的元数据）。 |
| 怎么用 | `const app = createSSRApp(RootComponent); const html = await renderToString(app, ctx)`；组件内 `if (import.meta.env.SSR) { const ctx = useSSRContext(); ctx.title = '用户详情' }`。 |
| 原理和工作流程 | `createSSRApp(rootComponent)` 与 `createApp` 的区别仅在于客户端 `mount()` 时走水合分支；`renderToString(input, context?)` 接收应用实例或 VNode，返回 `Promise<string>`，第二个参数是可选上下文，可用 `useSSRContext()` 在组件内访问（**只能在 setup 或 `<script setup>` 中调用，且必须确保只在服务端调用**，客户端返回 `undefined`）。 |
| 缺点 | `renderToString` 必须等整棵树渲染完才返回，TTFB 被最慢的数据请求拖住；`useSSRContext` 依赖 SSR 上下文，客户端调用无效，使用时机受限。 |

### 流式渲染 API

| 维度 | 内容 |
|------|------|
| 是什么 | 一组把渲染结果以流的形式输出的 API：`renderToWebStream`、`pipeToWebWritable`、`renderToNodeStream`、`pipeToNodeWritable`、`renderToSimpleStream`。 |
| 能做什么 | 渲染出一块就发一块，尽早输出首字节，配合 `<Suspense>` 可把已就绪的部分先推给浏览器，显著降低 TTFB。 |
| 怎么用 | `return new Response(renderToWebStream(app))`；Node 环境写 `pipeToNodeWritable(app, {}, res)`；Web 环境未全局暴露 `ReadableStream` 时用 `pipeToWebWritable` 配 `TransformStream`。 |
| 原理和工作流程 | `renderToWebStream` 返回 `ReadableStream`（推荐）；`pipeToWebWritable` / `pipeToNodeWritable` 把结果写入对应的 Writable；`renderToSimpleStream` 通过自定义 `push` / `destroy` 回调暴露最底层接口。`renderToNodeStream` 在 `vue/server-renderer` 的 ESM 构建下不可用，应改用 `pipeToNodeWritable`。 |
| 缺点 | 需要配合 Suspense 才能体现价值，普通组件树仍是「整棵渲染完才能确定内容」；流式输出一旦开始就无法再改变响应状态码与响应头，错误处理更复杂。 |

### 跨请求状态污染

| 维度 | 内容 |
|------|------|
| 是什么 | 在 SSR 下把状态放在模块级单例，导致同一个状态对象被多个请求复用，用户数据互相泄漏的现象。 |
| 能做什么 | 识别并规避 SSR 下最典型的安全隐患；指导共享状态的正确组织方式（每请求实例化 + `app.provide()`）。 |
| 怎么用 | ❌ `export const userInfo = ref(null)`；✅ 在 `createApp()` 内创建实例并 `app.provide('userInfo', userInfo)` 后返回 `{ app, userInfo }`。 |
| 原理和工作流程 | 浏览器中每次页面访问都会重新初始化模块，模块级状态天然「每页面一份」；服务端**只在启动时初始化一次模块**，同一个单例被所有请求复用，A 用户写入的数据会被 B 用户读到。解决方案是每个请求创建全新的应用实例（含 router 与 store），通过应用级 `app.provide()` 提供共享状态，而不是在组件里直接 `import` 单例。 |
| 缺点 | 每请求创建实例会带来额外初始化开销；`app.provide()` 方式要求所有使用方都通过 `inject` 获取，无法再直接 `import` 使用，代码组织成本更高。 |

### Nuxt 3 目录约定

| 维度 | 内容 |
|------|------|
| 是什么 | Nuxt 通过「约定优于配置」内置 SSR 全流程的目录规范：`pages/`、`components/`、`composables/`、`layouts/`、`middleware/`、`plugins/`、`server/`、`public/`、`app.vue`、`nuxt.config.ts`。 |
| 能做什么 | `pages/` 提供基于文件系统的路由（`pages/user/[id].vue` → `/user/:id`）；`components/` 与 `composables/` 自动导入；`server/` 承载 Nitro 服务端代码；`public/` 直接映射到站点根路径。 |
| 怎么用 | `app.vue` 中写 `<NuxtLayout><NuxtPage /></NuxtLayout>`；布局由 `definePageMeta({ layout: 'admin' })` 指定；中间件文件名即中间件名。 |
| 原理和工作流程 | 构建时 Nuxt 扫描约定目录生成路由表与自动导入清单，把上一章手写的「双份构建 + 服务端入口 + 客户端入口 + 资源注入」流程全部内置；服务端由 Nitro 承载，负责 API 路由与渲染响应。 |
| 缺点 | 约定即隐式依赖，目录与命名规则需要团队统一认知；自动导入让「变量从哪来」不直观，排查时需要熟悉约定。 |

### 数据获取：useAsyncData 与 useFetch

| 维度 | 内容 |
|------|------|
| 是什么 | Nuxt 的两个 SSR 友好数据获取 API：`useAsyncData` 是通用异步数据封装（key 手动指定），`useFetch` 是 `useAsyncData` + `$fetch` 的语法糖（key 由 URL 与选项自动生成）。 |
| 能做什么 | 服务端执行数据获取、结果序列化进 payload，客户端水合时直接复用而不重复请求；支持依赖变化自动重新获取、结果加工、字段裁剪与自定义缓存读取。 |
| 怎么用 | `await useAsyncData('user-detail', () => $fetch(url), { server, lazy, watch, default, transform, getCachedData })`；`await useFetch('/api/articles', { query, pick, lazy })`；返回值含 `data` / `pending` / `error` / `refresh` / `execute` / `status` / `clear`。 |
| 原理和工作流程 | 服务端渲染时执行 handler 并把结果写入 payload 随 HTML 下发；客户端水合时按 key 命中同一份 payload，跳过重复请求。`lazy: false`（默认）会阻塞导航直到数据就绪，`lazy: true` 则不阻塞但服务端不会等数据；`watch` 中的响应式依赖变化会触发重新获取。 |
| 缺点 | **`data` 默认是 `null`**，模板必须判空或用 `default` 兜底，否则首屏报错；**key 必须唯一且稳定**，冲突会让两个组件共用同一份数据；`lazy: true` 会牺牲 SEO 首屏内容。 |

### 状态共享：useState

| 维度 | 内容 |
|------|------|
| 是什么 | Nuxt 提供的 SSR 友好共享状态，等价于「跨组件共享的 ref + 自动序列化进 payload」，签名形如 `useState(key, init)`。 |
| 能做什么 | 在多个组件间共享同一份状态，同时保证每个请求有独立副本，从根本上避免跨请求状态污染。 |
| 怎么用 | `const count = useState('counter', () => 0)`；封装成 composable：`export const useCounter = () => { const count = useState('counter', () => 0); return { count, increment: () => count.value++ } }`。 |
| 原理和工作流程 | 状态挂在**当前请求的 Nuxt 应用实例**上，而不是模块作用域，因此每个请求拿到独立副本；渲染结束后随 payload 序列化下发，客户端水合时恢复，保证两端一致。 |
| 缺点 | 只适合轻量共享状态，缺少 getter / action 的组织能力；key 需要全局唯一，命名冲突会静默共用同一份状态。需要复杂逻辑编排时应改用 Pinia。 |

### 页面元信息：definePageMeta

| 维度 | 内容 |
|------|------|
| 是什么 | 定义页面级路由元信息的编译宏，**只能写在 `pages/` 目录下页面组件的 `<script setup>` 顶层**。 |
| 能做什么 | 配置 `name`、`layout`、`middleware`、`keepalive`、`alias`、`pageTransition`，以及用 `validate` 做参数校验（返回 `false` 则 404）。 |
| 怎么用 | `definePageMeta({ name: 'user-detail', layout: 'admin', middleware: ['auth'], keepalive: true, validate: (route) => /^\d+$/.test(String(route.params.id)) })`。 |
| 原理和工作流程 | 它是编译期处理的宏，Nuxt 在构建时静态分析并把它转换为路由配置，因此**不能动态构造**（如 `const meta = {...}; definePageMeta(meta)` 无法被静态分析，配置不生效）。需要动态值时从路由参数或 `useState` 中读取。 |
| 缺点 | 编译宏的使用位置与写法限制严格，动态构造会静默失效；写在非 `pages/` 组件中不生效；配置项与 Vue Router 的 `meta` 语义不完全一致，迁移时需要重新对应。 |

### 服务端路由：server/api

| 维度 | 内容 |
|------|------|
| 是什么 | Nuxt 基于 Nitro 的文件系统服务端路由：`server/api/` 下的文件自动映射为 `/api/*` 接口，`server/routes/` 则不带 `/api` 前缀；文件名后缀（`.get` / `.post`）可限定请求方法。 |
| 能做什么 | 在同一项目内编写后端接口（BFF 层），直接读数据库或调用上游服务；抛出标准 HTTP 错误供前端 `useFetch` 消费；通过 `runtimeConfig` 安全管理密钥。 |
| 怎么用 | `export default defineEventHandler(async (event) => { const { page } = getQuery(event); return { list } })`；读路径参数 `getRouterParam(event, 'id')`；读请求体 `await readBody(event)`；抛错 `throw createError({ statusCode: 404, statusMessage: '用户不存在' })`。 |
| 原理和工作流程 | Nitro 在构建时扫描 `server/` 目录生成路由表，`defineEventHandler` 定义处理器；处理器直接 `return` 对象时 Nitro 自动序列化为 JSON；`createError` 抛出的错误会带状态码返回，客户端 `useFetch` 的 `error` 能拿到。`runtimeConfig` 中**未加 `public` 前缀的字段只在服务端可用**，适合放密钥。 |
| 缺点 | 服务端代码与前端共享同一仓库，部署形态受 Nitro 预设约束（不同平台行为有差异）；接口层与业务逻辑混在一起时容易膨胀，需要自行分层。 |

### SEO：useSeoMeta

| 维度 | 内容 |
|------|------|
| 是什么 | Nuxt 提供的 SSR 友好元信息设置方式，接收扁平对象并自动映射为对应的 `<meta>` 标签；更细粒度的控制用 `useHead`。 |
| 能做什么 | 设置 `title`、`description`、`ogTitle` / `ogImage`、`twitterCard`、`robots` 等，服务端即写入 HTML，爬虫无需执行 JS 即可读到；`useHead` 可设置 `htmlAttrs`、`link`（canonical）、`script`（JSON-LD）。 |
| 怎么用 | `useSeoMeta({ title: '...', description: '...', ogImage: '...' })`；`useHead({ htmlAttrs: { lang: 'zh-CN' }, link: [{ rel: 'canonical', href: '...' }] })`。 |
| 原理和工作流程 | 内部基于 Unhead，在 SSR 期间把标签收集并渲染进服务端输出的 HTML，客户端水合后接管更新。若改用 `onMounted` 里手写 `document.title`，SSR 首屏的 HTML 中没有这些标签，SEO 收益为零。 |
| 缺点 | 标签内容依赖渲染时已有的数据，数据获取较晚（如 `lazy: true`）会导致元信息缺失或延迟；`useSeoMeta` 是扁平字段约定，特殊标签仍需退回 `useHead`。 |

### 混合渲染：routeRules

| 维度 | 内容 |
|------|------|
| 是什么 | `nuxt.config.ts` 中按路由配置渲染与缓存策略的能力，支持 `prerender`、`swr`、`isr`、`ssr`、`cors`、`redirect` 等字段。 |
| 能做什么 | 在同一应用内混用 SSG / SWR / ISR / CSR：首页预渲染、列表页缓存、详情页增量再生、后台路由关闭 SSR；还可做服务端重定向与 CORS 头注入。 |
| 怎么用 | `routeRules: { '/': { prerender: true }, '/products/**': { swr: 3600 }, '/blog/**': { isr: true }, '/admin/**': { ssr: false }, '/old-page': { redirect: '/new-page' } }`。 |
| 原理和工作流程 | **`isr` 与 `swr` 行为基本相同**，区别在于 `isr` 会把响应加入**支持该能力的平台 CDN 缓存**（目前主要是 Netlify 与 Vercel），因此 ISR 高度依赖部署平台，`swr` 更多依赖 Nitro 自身缓存；`swr: true` 只添加 `stale-while-revalidate` 头不含 MaxAge，控制 TTL 要传具体秒数；使用 `isr` / `swr` 的路由会额外生成 `_payload.json`，客户端导航时加载缓存 payload 而非重新请求；`ssr: false` 的路由页面组件会在构建时被排除出服务端 bundle。 |
| 缺点 | `nuxt generate` **不支持混合渲染**；ISR 依赖平台能力，换平台可能静默退化为普通 SSR；缓存策略配置错误会造成内容长期不更新，排查成本高。 |

### SSR 场景下的状态管理（Pinia）

| 维度 | 内容 |
|------|------|
| 是什么 | Pinia 在 SSR 下的使用约定：每个请求必须创建独立的 Pinia 实例，`state` 必须是返回对象的函数。 |
| 能做什么 | 在 SSR 下安全地组织复杂状态（state / getters / actions），同时保证请求之间状态隔离与客户端水合时状态接续。 |
| 怎么用 | 安装 `@pinia/nuxt` 模块（自动完成按请求创建实例、state 序列化到 payload、客户端恢复）；store 写 `state: () => ({ token: '', profile: null })`；服务端请求透传 cookie：`const headers = import.meta.server ? useRequestHeaders(['cookie']) : undefined`。 |
| 原理和工作流程 | 服务端渲染期间创建的 store，其 state 需要随 HTML 序列化给客户端，否则客户端水合时会用初始 state 渲染导致内容不一致；`@pinia/nuxt` 把这份 state 放进 payload，客户端据此初始化 pinia 完成状态接续。若 `state` 写成对象，会在模块加载时创建，成为被所有请求共享的单例，造成跨请求状态污染。 |
| 缺点 | 三条铁律必须遵守（`state` 必须是函数、服务端请求手动透传 Cookie、敏感数据不进会被序列化的 state）；payload 会随 HTML 下发，state 体积过大或含敏感字段都会带来问题。 |

### 数据预取时机

| 维度 | 内容 |
|------|------|
| 是什么 | 在 SSR 中决定「何时、在哪个环境获取数据」的三种方式：`useAsyncData` / `useFetch` 默认（阻塞）、同上加 `lazy: true`（不阻塞）、纯 Vue SSR 的 `onServerPrefetch`。 |
| 能做什么 | 让服务端在渲染前把数据准备好，从而产出带内容的 HTML（SEO 友好）；对非首屏关键数据则可延后到客户端加载，加快导航。 |
| 怎么用 | 页面级数据：`await useAsyncData(...)`（默认 `lazy: false`）；非关键数据：`useFetch(url, { lazy: true })`；纯 Vue SSR：`onServerPrefetch(async () => { articles.value = await fetchArticles() })`。 |
| 原理和工作流程 | SSR 期间只执行 `beforeCreate`、`created` 与 setup 根作用域，`onMounted` **不会执行**，因此把数据获取写在 `onMounted` 里，服务端渲染出的 HTML 就是空数据，首屏 SEO 完全失效。`onServerPrefetch` 只在服务端执行，客户端水合时不再执行，数据由序列化状态提供。 |
| 缺点 | `lazy: true` 会让服务端不等数据，牺牲 SEO 首屏内容；`onServerPrefetch` 与客户端数据获取逻辑分离，容易出现两端不一致，且仅适用于纯 Vue SSR 场景。 |

---

## 三、实战应用

### 列表页：数据获取 + 缓存 + 分页

| 维度 | 内容 |
|------|------|
| 是什么 | 一个完整的 SSR 列表页示例：用 `useAsyncData` 取列表数据、按 query 页码分页、用 `default` 兜底、用 `useSeoMeta` 设置元信息。 |
| 能做什么 | 页码变化自动重新获取；首屏由服务端渲染出真实列表内容；`NuxtLink` 自动为内部链接做预取。 |
| 怎么用 | `await useAsyncData('blog-list', () => $fetch('/api/blog', { query: { page: route.query.page ?? 1 } }), { watch: [() => route.query.page], default: () => ({ list: [], total: 0 }) })`；模板中用 `v-if="pending"` / `v-else-if="error"` / `v-else` 三态渲染。 |
| 原理和工作流程 | `watch` 中声明响应式依赖，依赖变化时自动重新获取；服务端渲染时数据写入 payload，客户端水合复用；`data` 默认可能为 `null`，因此用 `default` 提供初始结构，避免模板报「读取 null 的属性」。 |
| 缺点 | key 不唯一会导致两个组件共用数据；`data` 忘记兜底会在首屏报错；分页依赖 query 变化，若用 `lazy: true` 则首屏 HTML 中列表为空。 |

### 详情页：错误处理与 404

| 维度 | 内容 |
|------|------|
| 是什么 | 详情页示例：用 `useFetch` 取详情，数据缺失或接口报错时用 `createError` 抛出带状态码的错误。 |
| 能做什么 | 让页面在数据不存在时返回真正的 404 状态码，而不是 200 的空页面；`fatal: true` 终止渲染并展示错误页。 |
| 怎么用 | `const { data: article, error } = await useFetch(...)`；`if (!article.value \|\| error.value) throw createError({ statusCode: 404, statusMessage: '文章不存在', fatal: true })`。 |
| 原理和工作流程 | `createError` 在服务端抛出后会作为 HTTP 状态码返回给浏览器，同时触发 Nuxt 的错误页渲染；`fatal: true` 表示终止当前渲染。这样对 SEO 与状态码语义都正确，避免「软 404」。 |
| 缺点 | 错误页需要自行设计（或依赖 `error.vue`）；对 `lazy: true` 的数据获取，服务端阶段拿不到 `error`，404 判断会失效。 |

### SSR 性能优化

| 维度 | 内容 |
|------|------|
| 是什么 | 一组按收益排序的 SSR 优化手段：按路由降级渲染、静态化与缓存、接口层缓存、减小 payload、流式渲染、避免重复请求、减少首屏水合量、减少 SSR 中的重计算。 |
| 能做什么 | 把「每请求渲染」变成「命中缓存」，把服务端成本下降一个数量级；降低 TTFB、减小 HTML 体积、减少首屏需要水合的节点数量。 |
| 怎么用 | `routeRules: { '/admin/**': { ssr: false } }`；`prerender: true` / `swr: 3600` / `isr: true`；`defineCachedEventHandler(handler, { maxAge: 60, swr: true, getKey: () => 'hot-articles' })`；`useFetch` 的 `pick` / `transform`；`lazy: true` 与 `<ClientOnly>`。 |
| 原理和工作流程 | 收益呈层级递减：越靠前的层级减少的是「需要参与渲染的请求量」（缓存与降级），越靠后减少的是「单次渲染的常数开销」（payload 体积、水合节点数、计算量）。因此先做路由降级与缓存，再做流式与 payload 优化。Nuxt 默认用 `renderToString` 一次性返回，需要流式时要在 Nitro 层自定义渲染处理函数。 |
| 缺点 | 缓存会带来内容更新延迟，必须权衡 TTL；`ssr: false` 的路由失去 SEO 与首屏优势；流式渲染的实现与错误处理复杂度更高。 |

---

## 四、常见面试题

### 1. SSR 和 CSR 有什么区别？为什么 SSR 首屏更快

| 维度 | 内容 |
|------|------|
| 是什么 | CSR 由浏览器渲染，服务端只返回空壳 HTML；SSR 由服务端每请求渲染出完整 HTML，客户端再水合接管。 |
| 能做什么 | SSR 让首屏内容立即可见、SEO 友好、数据获取更靠近数据库；CSR 部署最简单、服务端零渲染压力、页面切换最流畅。 |
| 怎么用 | CSR：`ssr: false`；SSR：Nuxt 默认模式，服务端 `createSSRApp()` + `renderToString()`。 |
| 原理和工作流程 | CSR 需等 JS 下载、执行、发请求、拿到数据后才渲染，首屏存在白屏；SSR 服务端先执行一遍组件代码直接返回带内容 HTML，浏览器拿到即可显示。 |
| 缺点 | SSR 开发受限（浏览器 API 只能在特定生命周期用）、需要 Node 环境、服务端渲染耗 CPU、必须处理水合与跨请求状态隔离。 |

### 2. 什么是水合？水合不匹配的常见原因

| 维度 | 内容 |
|------|------|
| 是什么 | 水合是客户端创建与服务端完全相同的应用实例、把 VNode 树与已有 DOM 逐一比对并复用节点、挂上事件监听器与动态属性的过程。 |
| 能做什么 | 让服务端静态 HTML 变为可交互应用，同时复用已有 DOM 避免重复渲染。 |
| 怎么用 | 用 `createSSRApp()` 创建应用，客户端 `mount()` 自动走水合分支；不匹配时用 `data-allow-mismatch`（Vue 3.5+）消除不可避免的警告。 |
| 原理和工作流程 | 匹配成功则复用节点；失败则丢弃重建并告警。常见原因：非法 HTML 嵌套、随机值（`Math.random()` / `Date.now()`）、时区或语言环境不一致、渲染期读取浏览器 API、`v-if` 依赖客户端状态、第三方库或浏览器扩展改了 DOM、指令只实现 `mounted` 而被 SSR 忽略、`Teleport` 目标为 `body`。 |
| 缺点 | 不匹配会造成节点重建的性能损失与首屏闪烁；`data-allow-mismatch` 只消除警告，不解决根本问题。 |

### 3. Vue 3 原生 SSR 提供了哪些 API

| 维度 | 内容 |
|------|------|
| 是什么 | `vue/server-renderer` 提供的服务端渲染 API：`renderToString`、`renderToWebStream`、`pipeToWebWritable`、`pipeToNodeWritable`、`renderToSimpleStream`；应用侧 `createSSRApp` 与 `useSSRContext`。 |
| 能做什么 | 把 Vue 应用渲染为 HTML 字符串或流；通过 SSR 上下文收集要写进 `<head>` 的元数据等附加信息。 |
| 怎么用 | `const html = await renderToString(app, ctx)`；组件内 `if (import.meta.env.SSR) { const ctx = useSSRContext(); ctx.title = '用户详情' }`。 |
| 原理和工作流程 | `createSSRApp` 与 `createApp` 的区别仅在于客户端 `mount()` 走水合分支；`renderToString` 返回 `Promise<string>`，第二参数为可选上下文；`useSSRContext()` 是运行时 API，只能在 setup 中调用且必须确保只在服务端调用。`renderToNodeStream` 在 ESM 构建下不可用，应改用 `pipeToNodeWritable`。 |
| 缺点 | `renderToString` 必须等整棵树渲染完，TTFB 受最慢请求拖累；`useSSRContext` 客户端调用返回 `undefined`，使用时机受限。 |

### 4. 为什么 SSR 下不能把状态放在模块级单例

| 维度 | 内容 |
|------|------|
| 是什么 | 跨请求状态污染：模块级单例在服务端被多个请求复用，导致用户数据互相泄漏。 |
| 能做什么 | 明确 SSR 下共享状态的正确组织方式，规避最典型的数据泄漏风险。 |
| 怎么用 | 每个请求在 `createApp()` 内创建实例并用 `app.provide()` 注入；Pinia 的 `state` 写成函数；Nuxt 中用 `useState`。 |
| 原理和工作流程 | 浏览器中每次页面访问都会重新初始化模块，模块级状态天然「每页面一份」；服务端模块只在启动时初始化一次，单例被所有请求复用，A 用户写入的数据会被 B 用户读到。 |
| 缺点 | 每请求实例化有初始化开销；`provide` / `inject` 方式要求使用方统一改造，无法直接 `import` 单例。 |

### 5. `useAsyncData` 和 `useFetch` 有什么区别

| 维度 | 内容 |
|------|------|
| 是什么 | `useAsyncData` 是通用异步数据封装（key 手动指定）；`useFetch` 是 `useAsyncData` + `$fetch` 的封装（key 由 URL 与选项自动生成）。 |
| 能做什么 | 两者都是 SSR 友好的：服务端执行、结果序列化进 payload，客户端水合时直接复用不重复请求。 |
| 怎么用 | `useAsyncData('key', () => $fetch(url), { watch, default, transform })`；`useFetch('/api/articles', { query, pick, lazy })`。 |
| 原理和工作流程 | 服务端渲染时执行 handler 并把结果写入 payload 随 HTML 下发，客户端按 key 命中同一份 payload 跳过请求。返回值含 `data` / `pending` / `error` / `refresh` / `execute` / `status` / `clear`。`useAsyncData` 适合多请求组合、自定义逻辑、非 HTTP 数据源；`useFetch` 适合单个 HTTP 请求。 |
| 缺点 | `data` 默认是 `null`，模板必须判空或提供 `default`；key 必须唯一稳定，冲突会让两个组件共用数据；`lazy: true` 会牺牲 SEO 首屏内容。 |

### 6. SSR 下 `window is not defined` 怎么解决

| 维度 | 内容 |
|------|------|
| 是什么 | 通用代码在 Node.js 中执行时访问了浏览器全局对象（`window` / `document` / `localStorage`）而报错。 |
| 能做什么 | 通过环境判断、惰性访问、组件隔离三类手段让同一份代码在两个环境正确运行。 |
| 怎么用 | `if (import.meta.client) { ... }`；把访问逻辑放到 `onMounted` 中；Nuxt 中用 `<ClientOnly>` 组件或 `*.client.vue` 后缀隔离整个组件；第三方库改为动态 `import()`。 |
| 原理和工作流程 | SSR 期间只执行 `beforeCreate`、`created` 与 setup 根作用域，`onMounted` 只在客户端运行，因此把浏览器 API 访问惰性化到 `onMounted` 即可避开服务端；`<ClientOnly>` 则在服务端不渲染该子树。 |
| 缺点 | `<ClientOnly>` 会让该部分内容失去 SEO 与首屏优势；在模块顶层就访问 `window` 的第三方库只能改为动态加载，增加加载延迟与代码复杂度。 |

### 7. SSR 期间生命周期钩子有什么差异

| 维度 | 内容 |
|------|------|
| 是什么 | SSR 期间只有 `beforeCreate`、`created` 与 setup 根作用域会执行，`mounted` / `updated` / `beforeUnmount` / `unmounted` 等只在客户端运行。 |
| 能做什么 | 据此决定「哪些逻辑能写在服务端」「数据获取应该放在哪里」，避免首屏空数据与资源泄漏。 |
| 怎么用 | 数据获取用 `useAsyncData` / `useFetch` 或纯 Vue SSR 的 `onServerPrefetch`；副作用（如 `setInterval`）放到 `onMounted` 并在 `onUnmounted` 中清理。 |
| 原理和工作流程 | 服务端没有用户交互与 DOM 更新，因此挂载与更新类钩子无意义、不会执行；同时 `unmounted` 不执行意味着在 setup 根作用域或 `created` 中创建的定时器永远不会被清理。 |
| 缺点 | 数据获取不能写在 `onMounted`，否则服务端 HTML 是空数据、SEO 收益为零；副作用清理逻辑必须依赖客户端钩子，容易遗漏造成泄漏。 |

### 8. Nuxt 3 的渲染模式与 `routeRules` 怎么配合

| 维度 | 内容 |
|------|------|
| 是什么 | Nuxt 默认 Universal Rendering（SSR + 水合），可通过 `ssr: false` 全局退化为 CSR；混合渲染通过 `routeRules` 按路由配置。 |
| 能做什么 | 同一应用内混用 SSG（`prerender`）、SWR（`swr`）、ISR（`isr`）、CSR（`ssr: false`），并做服务端重定向与 CORS 头注入。 |
| 怎么用 | `routeRules: { '/': { prerender: true }, '/products/**': { swr: 3600 }, '/blog/**': { isr: true }, '/admin/**': { ssr: false } }`。 |
| 原理和工作流程 | `isr` 与 `swr` 行为基本相同，区别在于 `isr` 会把响应加入支持该能力的平台 CDN 缓存（主要是 Netlify 与 Vercel），因此高度依赖部署平台；使用 `isr` / `swr` 的路由会额外生成 `_payload.json`，客户端导航时加载缓存 payload 而非重新请求。 |
| 缺点 | `nuxt generate` 不支持混合渲染；ISR 换平台可能静默退化为普通 SSR；缓存配置错误会造成内容长期不更新。 |

### 9. SSR 应用的性能优化有哪些手段

| 维度 | 内容 |
|------|------|
| 是什么 | 按收益排序的优化手段集合：按路由降级与缓存、接口层缓存、流式渲染、减小 payload、减少首屏水合量、避免重复请求、把客户端重计算移出 SSR。 |
| 能做什么 | 把「每请求渲染」变成「命中缓存」，服务端成本下降一个数量级；同时降低 TTFB、减小 HTML 体积、减少水合节点数。 |
| 怎么用 | `'/admin/**': { ssr: false }`；`prerender: true` / `swr: 3600` / `isr: true`；`defineCachedEventHandler` / `defineCachedFunction`；`useFetch` 的 `pick` / `transform`；`lazy: true` 与 `<ClientOnly>`。 |
| 原理和工作流程 | 收益呈层级递减：先减少「需要参与渲染的请求量」（缓存与降级），再减少「单次渲染的常数开销」（payload 体积、水合节点数、计算量）。Nuxt 默认用 `renderToString` 一次性返回，需要流式时要在 Nitro 层自定义渲染处理函数。 |
| 缺点 | 缓存带来内容更新延迟，需权衡 TTL；`ssr: false` 的路由失去 SEO 与首屏优势；流式渲染实现与错误处理复杂度更高。 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 聚合了 SSR 开发中的十九个常见错误：首屏数据写在 `onMounted`、setup 根作用域写 `setInterval`、渲染期访问浏览器 API、引入在顶层访问 `window` 的第三方库、模块级单例作为共享状态、Pinia 的 `state` 写成对象、服务端 `$fetch` 未透传 Cookie、敏感数据进入会被序列化的 state、`useAsyncData` 的 key 不唯一、模板直接用 `data.xxx`、用 `typeof window !== 'undefined'` 渲染差异内容、非法 HTML 嵌套、渲染期使用随机值与本地时间格式化、`Teleport` 目标设为 `body`、误以为 `data-allow-mismatch` 能修复问题、在 `definePageMeta` 中传入变量、用 SSR 渲染强个性化页面、用 `isr` 却部署在不支持的平台上、手写生产级 SSR 流程。 |
| 能做什么 | 快速对照排查：首屏数据改用 `useAsyncData` / `useFetch` 或 `onServerPrefetch`；副作用放 `onMounted` 并在 `onUnmounted` 清理；浏览器 API 用 `import.meta.client` 判断、`<ClientOnly>` 或 `*.client.vue` 隔离；共享状态用 `useState` 或每请求实例 + `app.provide()`；Pinia 的 `state` 写成 `() => ({ ... })`；服务端请求用 `useRequestHeaders(['cookie'])` 透传；敏感数据留在服务端；key 保证全局唯一；模板判空或用 `default`；差异内容用 `<ClientOnly>` 或 `data-allow-mismatch`；`definePageMeta` 只写对象字面量；个性化页面降级为 CSR；ISR 前先确认平台支持。 |
| 怎么用 | `state: () => ({ token: '' })`；`const headers = import.meta.server ? useRequestHeaders(['cookie']) : undefined`；`useAsyncData('blog-list', () => $fetch('/api/blog'), { default: () => ({ list: [] }) })`；`defineCachedEventHandler(handler, { maxAge: 60, swr: true })`。 |
| 原理和工作流程 | 根因只有三类：**环境差异**（服务端没有浏览器 API）、**生命周期差异**（`onMounted` / `onUnmounted` 在 SSR 期间不执行）、**实例复用**（服务端模块只初始化一次，单例被所有请求共享）。水合类问题的根因是「服务端与客户端渲染结果不同」，缓存类问题的根因是「路由规则与部署平台能力不匹配」。 |
| 缺点 | 这些问题大多在开发环境不报错、只在特定请求或生产环境暴露（如跨请求污染、缓存不生效），排查成本高；部分修复手段（`<ClientOnly>`、`ssr: false`）会牺牲 SEO 或首屏优势，需要权衡。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./05-SSR与Nuxt实战.md) | [返回模块目录](../README.md) | [返回知识导览](../知识导览.md)
