# Vue 3 SSR 与 Nuxt 实战

> 模块：05-vue（第5周 Vue 3 生态）
> 定位：服务端渲染与 Nuxt 框架原理篇

---

## 核心概念

前三章讲的是「浏览器里跑一个 Vue 应用」，本章讲的是「同一份 Vue 代码如何在服务端先跑一遍」。这个能力叫**服务端渲染（Server-Side Rendering，SSR）**，也叫**通用渲染（Universal Rendering）**或**同构渲染（Isomorphic Rendering）**——应用的大部分代码会同时运行在服务端和客户端。

### 为什么需要服务端渲染

纯客户端渲染（CSR）的 SPA 首屏有一个绕不开的问题：浏览器拿到的是几乎空的 HTML 外壳，必须等 JS 下载、解析、执行、发请求、拿到数据之后才能渲染出内容。后果有三：**首屏白屏时间长**（用户先看到 loading）、**SEO 不友好**（Google / Bing 能索引「同步执行 JS」的应用，但以 loading 开局、内容靠 Ajax 异步获取的页面爬虫通常不会等）、**弱网与低端设备体验差**。

SSR 的做法是：**服务端执行一遍组件代码，直接产出带内容的 HTML**，浏览器拿到即可显示；随后客户端再执行一遍同样的代码，把静态 HTML「激活」为可交互应用，这一步就是**水合（Hydration）**。

**SSR 的代价**（面试常被追问，必须能说清）：

| 代价 | 说明 |
|------|------|
| 开发限制 | 浏览器特有 API 只能在特定生命周期使用；部分第三方库需要特殊处理 |
| 部署复杂 | 需要能跑 Node.js 的环境，不能像纯静态 SPA 一样丢到任意静态服务器 |
| 服务端负载高 | 渲染整棵组件树比托管静态文件更耗 CPU，高流量下必须配缓存 |
| 心智负担 | 同一份代码要在两个环境正确运行，还要处理状态隔离 |

> **判断标准**：先问「首屏速度对业务重要吗」。内部管理后台的几百毫秒延迟无所谓，不需要 SSR；内容站、电商、营销页这类「内容展示速度直接关联转化」的场景才有价值。

### 四种渲染模式对比与选型

| 模式 | HTML 生成时机 | 做法 | 优点 | 缺点 | 适用 |
|------|--------------|------|------|------|------|
| **CSR** | 浏览器运行时 | 服务端只返回空壳 HTML（`<div id="app"></div>` + 入口脚本） | 部署最简单、服务端零渲染压力、切换最流畅 | 首屏白屏、SEO 差 | SaaS 后台、编辑器、游戏 |
| **SSR** | 每次请求 | 每个请求在服务端渲染出完整 HTML | 首屏内容立即可见、SEO 友好、数据获取更靠近数据库 | 需 Node 环境、服务端负载高、要处理水合与状态隔离 | 内容型页面、需要 SEO 的电商与营销页 |
| **SSG** | 构建时 | 构建时渲染成静态 HTML，由静态服务器或 CDN 托管 | 保留 SSR 的首屏与 SEO 优势，成本更低、抗流量最强 | **只适合数据在构建期已知且多次请求之间不变的页面** | 博客、文档站、营销页 |
| **ISR** | 首次请求时生成，之后按 TTL 再生 | 按需生成并缓存，过期后先返回旧内容、同时后台再生 | 兼顾静态化的低成本与数据新鲜度 | 有 TTL 延迟；CDN 缓存能力依赖部署平台 | 商品列表、博客列表 |

**两个关键前提**：

1. **SSG 要求渲染所需数据对每个用户都相同**。页面一旦出现「当前登录用户」这类个性化内容，就不适合整页 SSG。
2. **ISR 严格说不是独立渲染模式**，而是按路由的缓存与再生策略，语义就是 `stale-while-revalidate`。

```
页面需要 SEO、或首屏内容对转化重要吗？
  ├─ 不需要 → CSR（ssr: false），部署最省事
  └─ 需要
       ├─ 内容对每个用户都相同吗？
       │    ├─ 是 → 数据在构建期已知吗？
       │    │         ├─ 是 → SSG（prerender: true）
       │    │         └─ 否 → 能接受 TTL 延迟吗？
       │    │                   ├─ 能 → ISR / SWR（swr: TTL）
       │    │                   └─ 不能 → SSR
       │    └─ 否（含个性化内容）→ SSR
       └─ 同一应用内既有静态页又有动态页 → 混合渲染（routeRules 按路由配置）
```

> **混合渲染**才是生产常态：首页 `prerender`，商品列表 `swr`，商品详情 `isr`，`/admin/**` 直接 `ssr: false` 退化成 CSR。

---

## 底层原理

### Hydration（水合）原理

**概念定义**：水合是客户端接管服务端静态 HTML 的过程——Vue 创建一个与服务端**完全相同**的应用实例，把 VNode 树与已有真实 DOM 逐一对应，为元素挂上事件监听器、应用动态属性，让页面可交互。

```javascript
// app.js（服务端与客户端共享的通用代码）
import { createSSRApp } from 'vue'

export function createApp() {
  // createSSRApp 而不是 createApp：标记该应用需要以「水合」方式挂载
  return createSSRApp({
    data: () => ({ count: 1 }),
    template: `<button @click="count++">{{ count }}</button>`
  })
}

// client.js：mount 会走水合分支，复用服务端 DOM 而不是创建新节点
// createApp().mount('#app')
```

**执行流程**：

```
1. 定位容器（#app），取得服务端渲染出的真实 DOM
2. 逐层遍历 VNode 树与真实 DOM，比对节点类型与结构
3. 匹配成功 → 复用该 DOM，只补充事件监听器与动态属性（不重建节点）
4. 匹配失败 → 丢弃该节点并重新创建，同时输出水合不匹配警告
5. 遍历完成后，应用进入正常的响应式更新流程
```

**两个关键结论**：

1. 水合阶段会执行两遍组件代码（服务端一遍、客户端一遍），任何「每次执行结果不同」的代码都会导致不匹配。
2. 水合期间响应式在服务端是被禁用的——服务端没有用户交互与 DOM 更新，Vue 默认关闭服务端响应性以提升性能。

**水合不匹配（hydration mismatch）的常见原因**：

| 原因 | 例子 | 现象 |
|------|------|------|
| 不规范的 HTML 嵌套 | `<p><div>hi</div></p>` | 浏览器解析时自动补全/截断标签，DOM 与 VNode 结构不一致 |
| 渲染了随机值 | `Math.random()`、`Date.now()` | 服务端与客户端生成的值不同 |
| 时区 / 语言环境不一致 | `new Date().toLocaleString()` | 服务端时区与用户时区不同 |
| 渲染期读取浏览器 API | 模板中访问 `window.innerWidth`、`localStorage` | 服务端取不到值，两次渲染分支不同 |
| 依赖客户端状态的 `v-if` | `v-if="isMobile"`，而 `isMobile` 由 `window` 判断 | 首屏分支不同 |
| 第三方库在水合前改了 DOM | 广告脚本、地图/图表库、浏览器扩展 | DOM 被外部改动，Vue 比对失败 |
| 指令被 SSR 忽略 | 只实现了 `mounted` 的自定义指令 | 客户端多出或缺少属性 |
| `Teleport` 目标为 `body` | `<Teleport to="body">` | `body` 中已有其他 SSR 内容，无法确定水合起始位置 |

**排查手段**：

1. 开发环境看控制台：Vue 会输出 `Hydration completed but contains mismatches`，并给出具体节点与组件栈（Vue 3.4+ 的报错信息比早期版本详细得多）。
2. 生产环境开启详细报错：Vue 3.4+ 提供编译期特性标志 `__VUE_PROD_HYDRATION_MISMATCH_DETAILS__`，排查完再关掉。
3. 二分法定位：把可疑组件用 `<ClientOnly>` 包起来，若不匹配消失，问题就在该组件内。
4. 检查 HTML 合法性：把服务端产出的 HTML 贴进校验器，确认没有非法嵌套。

**消除不可避免的不匹配**：Vue 3.5+ 提供 `data-allow-mismatch`，可选值为 `text`、`children`、`class`、`style`、`attribute`，不写值表示允许所有类型：

```html
<div data-allow-mismatch="text">{{ data.toLocaleString() }}</div>
```

> **易错点**：它是「承认这里对不上」的逃生舱，不是修复手段。警告消失但节点仍会被客户端重建，性能损失依然存在。

### Vue 3 原生 SSR API

服务端渲染 API 位于 `vue/server-renderer` 子路径下。

#### createSSRApp 与 renderToString

```javascript
// server.js —— 运行在 Node.js 服务端
import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'

const app = createSSRApp({
  data: () => ({ count: 1 }),
  template: `<button @click="count++">{{ count }}</button>`
})

const html = await renderToString(app) // 输出：<button>1</button>
```

- `createSSRApp(rootComponent)`：创建「支持水合」的应用实例，与 `createApp` 的区别仅在于客户端 `mount()` 时走水合分支。
- `renderToString(app, context?)`：接收应用实例或 VNode，返回 `Promise<string>`；第二个参数是**可选的 SSR 上下文对象**，用于在渲染过程中收集额外数据。

#### useSSRContext

`useSSRContext()` 用于在组件内部拿到 `renderToString` 传入的上下文对象，典型用途是收集要写进 HTML `<head>` 的元数据：

```vue
<script setup>
import { useSSRContext } from 'vue'

// 必须确保只在服务端调用：客户端调用返回 undefined
if (import.meta.env.SSR) {
  const ctx = useSSRContext()
  ctx.title = '用户详情' // 渲染完成后由服务器写入 <head>
}
</script>
```

> 它是运行时 API，只能在组件 setup 或 `<script setup>` 中调用。Nuxt 中一般不需要直接用它，`useHead` / `useSeoMeta` 已封装这套逻辑。

#### 流式渲染 API

`renderToString` 必须等整棵树渲染完才返回，首字节时间（TTFB）被最慢的数据请求拖住；流式渲染**渲染出一块就发一块**：

| API | 输出形式 | 说明 |
|-----|---------|------|
| `renderToWebStream(input, context?)` | `ReadableStream` | 推荐使用，可直接 `new Response(renderToWebStream(app))` |
| `pipeToWebWritable(input, context, writable)` | 写入 Web `WritableStream` | 环境未全局暴露 `ReadableStream` 构造函数时使用 |
| `renderToNodeStream(input, context?)` | Node `Readable` | `vue/server-renderer` 的 ESM 构建不支持，应改用 `pipeToNodeWritable` |
| `pipeToNodeWritable(input, context, writable)` | 写入 Node `Writable` | Node.js 环境下的流式输出 |
| `renderToSimpleStream(input, context, options)` | 自定义 `push` / `destroy` 回调 | 最底层接口，供自定义流实现使用 |

```javascript
// 流式渲染：把渲染结果直接作为 HTTP 响应体返回
import { createSSRApp } from 'vue'
import { renderToWebStream } from 'vue/server-renderer'

export default defineEventHandler(() => {
  const app = createSSRApp(App)
  // 边渲染边传输，配合 Suspense 可把已就绪的部分先推给浏览器
  return new Response(renderToWebStream(app), {
    headers: { 'content-type': 'text/html; charset=utf-8' }
  })
})
```

#### 跨请求状态污染

```javascript
// ❌ 错误：模块级单例，会被所有请求共享
import { ref } from 'vue'
export const userInfo = ref(null) // 服务器启动时创建一次，所有请求复用

// ✅ 正确：每个请求创建独立实例，通过 app.provide 注入
export function createApp() {
  const app = createSSRApp(App)
  const userInfo = ref(null)
  app.provide('userInfo', userInfo)
  return { app, userInfo }
}
```

**原因**：浏览器中每次页面访问都会重新初始化模块，模块级单例天然「每页面一份」；服务端**只在启动时初始化一次模块**，同一个单例被所有请求复用，A 用户的数据可能泄露给 B 用户。

**解决方案**：每个请求创建全新的应用实例（含 router 与 store），通过应用级 `app.provide()` 提供共享状态，而不是在组件里直接 `import` 单例。

> **生产环境不要手写整套 SSR 流程**：完整 SSR 还需要同一应用构建两次（客户端 + 服务端）、服务端产物中模板编译成字符串拼接而非 render 函数、HTML 中注入正确的资源预加载提示、路由与数据获取的通用化管理。官方明确建议直接使用上层框架（Nuxt）。

### Nuxt 3 核心

#### 目录约定

| 目录 / 文件 | 作用 |
|------------|------|
| `pages/` | 基于文件系统的路由；`pages/user/[id].vue` → `/user/:id` |
| `components/` / `composables/` | 组件与组合式函数自动导入，无需手写 `import` |
| `layouts/` | 布局，页面用 `definePageMeta({ layout: 'admin' })` 指定 |
| `middleware/` | 路由中间件，文件名即中间件名 |
| `plugins/` | 应用启动时执行的插件 |
| `server/` | Nitro 服务端代码（API 路由、中间件、工具函数） |
| `public/` | 静态资源，直接映射到站点根路径 |
| `app.vue` / `nuxt.config.ts` | 应用根组件与配置文件 |

```vue
<!-- app.vue：应用根组件 -->
<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
```

#### 数据获取：useAsyncData 与 useFetch

两者都是 **SSR 友好**的：服务端执行、结果序列化进 payload，客户端水合时直接复用，不会重复请求。

```typescript
// useAsyncData：自定义异步逻辑，key 必须手动指定
const { data, pending, error, refresh, status } = await useAsyncData(
  'user-detail',                    // 唯一 key，用于 payload 复用与去重
  () => $fetch(`/api/user/${route.params.id}`),
  {
    server: true,                   // 是否在服务端执行（默认 true）
    lazy: false,                    // false：阻塞导航直到数据就绪
    watch: [() => route.params.id], // 依赖变化时自动重新获取
    default: () => ({ name: '' }),  // data 的初始值
    transform: (res) => res.data,   // 对返回值做加工
    getCachedData: (key, nuxtApp) => nuxtApp.payload.data[key]
  }
)

// useFetch：useAsyncData + $fetch 的语法糖，key 由 URL 与选项自动生成
const { data: articles } = await useFetch('/api/articles', {
  query: { page: 1, size: 10 }, // 自动序列化为 query string
  pick: ['list', 'total'],      // 只取需要的字段，减小 payload 体积
  lazy: true                    // 不阻塞导航，进入页面后再加载
})
```

| 维度 | `useAsyncData` | `useFetch` |
|------|---------------|-----------|
| 本质 | 通用异步数据封装 | `useAsyncData` + `$fetch` 的封装 |
| key | 必须手动指定 | 由 URL 与选项自动生成 |
| 适用 | 多请求组合、自定义逻辑、非 HTTP 数据源 | 单个 HTTP 请求 |
| 返回值 | `data` / `pending` / `error` / `refresh` / `execute` / `status` / `clear` | 同上 |

**三个必须记住的点**：

1. **`data` 默认是 `null`**，模板中要用 `v-if="data"` 或提供 `default`，否则首屏会报「读取 null 的属性」。
2. **`lazy: true` 不阻塞导航**，但服务端不会等数据就绪，SEO 场景应保持默认的 `lazy: false`。
3. **`key` 必须唯一且稳定**，key 冲突会让两个组件共用同一份 payload 数据。

#### 状态共享：useState

`useState` 是 Nuxt 提供的 SSR 友好共享状态，等价于「跨组件共享的 ref + 自动序列化进 payload」：

```typescript
// composables/useCounter.ts
export const useCounter = () => {
  // 每个请求都有独立的状态副本，不会跨请求污染
  const count = useState('counter', () => 0)
  return { count, increment: () => count.value++ }
}
```

**为什么不用模块级 `ref`？** 服务端模块只初始化一次，模块级 `ref` 会变成跨请求共享的单例，造成状态污染。`useState` 把状态挂到当前请求的 Nuxt 应用实例上，从根上避免了这个问题。需要 SSR 安全的跨组件共享状态时优先用 `useState`；逻辑复杂、需要 action / getter 组织时用 Pinia。

#### 页面元信息：definePageMeta

`definePageMeta` 是编译宏，**只能写在 `pages/` 目录下页面组件的 `<script setup>` 顶层**：

```vue
<script setup lang="ts">
definePageMeta({
  name: 'user-detail',
  layout: 'admin',                 // 使用的布局
  middleware: ['auth'],            // 路由中间件（文件位于 middleware/）
  keepalive: true,                 // 是否被 <KeepAlive> 缓存
  alias: ['/u/:id'],               // 路由别名
  pageTransition: { name: 'fade', mode: 'out-in' },
  validate: (route) => /^\d+$/.test(String(route.params.id)) // 返回 false 则 404
})
</script>
```

> **易错点**：它是编译期处理的宏，**不能动态构造**（如 `const meta = {...}; definePageMeta(meta)`），否则无法被静态分析。需要动态值时从路由参数或 `useState` 中读取。

#### 服务端路由：server/api

`server/api/` 下的文件自动映射为 `/api/*` 接口（`server/routes/` 则不带 `/api` 前缀），无需额外配置：

```typescript
// server/api/articles.get.ts  →  GET /api/articles（.get / .post 等后缀可限定方法）
export default defineEventHandler(async (event) => {
  const { page = 1, size = 10 } = getQuery(event) // 读 query
  // const body = await readBody(event)           // 读请求体（POST / PUT）

  const list = await db.article.findMany({
    skip: (Number(page) - 1) * Number(size),
    take: Number(size)
  })

  return { list, total: list.length } // 直接 return 对象，Nitro 自动序列化为 JSON
})
```

```typescript
// server/api/user/[id].ts  →  GET /api/user/:id
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const user = await db.user.findUnique({ where: { id } })

  if (!user) {
    // 抛出 HTTP 错误，客户端 useFetch 的 error 会拿到它
    throw createError({ statusCode: 404, statusMessage: '用户不存在' })
  }

  return user
})
```

配套工具：`defineEventHandler`（定义处理器）、`getQuery` / `readBody` / `getRouterParam`（读参数）、`createError`（抛 HTTP 错误）、`useRuntimeConfig`（读运行时配置——`runtimeConfig` 中未加 `public` 前缀的字段只在服务端可用，适合放密钥）。

#### SEO：useSeoMeta

```vue
<script setup lang="ts">
useSeoMeta({
  title: 'Vue 3 SSR 与 Nuxt 实战',
  description: '从渲染模式选型到水合原理，系统掌握 Vue 3 的服务端渲染',
  ogTitle: 'Vue 3 SSR 与 Nuxt 实战',
  ogImage: 'https://example.com/cover.png',
  twitterCard: 'summary_large_image',
  robots: 'index, follow'
})

// 需要更细粒度控制（如插入 JSON-LD）时使用 useHead
useHead({
  htmlAttrs: { lang: 'zh-CN' },
  link: [{ rel: 'canonical', href: 'https://example.com/ssr' }]
})
</script>
```

> 它的价值在于**服务端就把标签写进 HTML**，爬虫无需执行 JS 即可读到；如果在 `onMounted` 里手写 `document.title`，SSR 首屏的 HTML 里没有这些标签，SEO 收益为零。

#### 混合渲染：routeRules

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    '/': { prerender: true },              // SSG：构建时预渲染
    '/products/**': { swr: 3600 },         // SWR：缓存 1 小时，过期后先返回旧内容再后台再生
    '/blog/**': { isr: true },             // ISR：内容持续到下次部署（需平台支持 CDN 缓存）
    '/admin/**': { ssr: false },           // CSR：后台不需要 SEO，且被排除出服务端 bundle
    '/old-page': { redirect: '/new-page' } // 服务端重定向
  }
})
```

**四个必须知道的事实**：

1. **`isr` 与 `swr` 行为基本相同**，区别在于 `isr` 会把响应加入**支持该能力的平台 CDN 缓存**（目前主要是 Netlify 与 Vercel），因此 ISR 高度依赖部署平台；`swr` 更多依赖 Nitro 自身缓存。
2. `swr: true` 只添加 `stale-while-revalidate` 响应头而不含 MaxAge；要控制 TTL 应传具体秒数。
3. **使用 `isr` / `swr` 的路由会额外生成 `_payload.json`**，客户端导航时加载缓存的 payload 而不是重新请求数据。
4. `nuxt generate` **不支持混合渲染**，它是整站静态生成的模式。

### SSR 场景下的状态管理与数据预取

#### Pinia 在 SSR 下必须按请求隔离

核心规则只有一条：**每个请求都要有独立的 Pinia 实例**。Nuxt 中安装 `@pinia/nuxt` 模块即可，它会自动完成「按请求创建实例 + state 序列化到 payload + 客户端恢复」：

```typescript
// nuxt.config.ts
export default defineNuxtConfig({ modules: ['@pinia/nuxt'] })
```

```javascript
// stores/user.js
export const useUserStore = defineStore('user', {
  // ✅ 函数形式：每个请求调用一次，返回全新对象
  state: () => ({ token: '', profile: null }),
  // ❌ 对象形式：模块级单例，会在所有请求间共享，造成跨请求状态污染

  actions: {
    async fetchProfile() {
      // SSR 期间服务端请求不会自动带 cookie，需要手动透传
      const headers = import.meta.server ? useRequestHeaders(['cookie']) : undefined
      this.profile = await $fetch('/api/profile', { headers })
    }
  }
})
```

**三条 SSR 状态管理铁律**：

1. **`state` 必须是函数**，绝不在模块顶层创建响应式状态。
2. **服务端请求要手动透传 Cookie**：服务端发起请求时没有浏览器的同源 cookie 自动附带。
3. **敏感数据不要放进会被序列化的 state**：payload 会随 HTML 下发到浏览器。

#### 数据预取时机

| 方式 | 适用场景 | 说明 |
|------|---------|------|
| `useAsyncData` / `useFetch`（默认） | 页面级数据 | 在 setup 顶层 `await`，服务端等数据就绪后再渲染，SEO 友好 |
| 同上 + `lazy: true` | 非首屏关键数据 | 不阻塞导航，进入页面后加载，需自行处理 `pending` |
| `onServerPrefetch` | 纯 Vue SSR（无 Nuxt） | 只在服务端执行的钩子，用于渲染前把异步数据准备好 |

```vue
<script setup>
import { onServerPrefetch, ref } from 'vue'

const articles = ref([])

// 仅在服务端执行；客户端水合时不会再次执行，数据由序列化状态提供
onServerPrefetch(async () => {
  articles.value = await fetchArticles()
})
</script>
```

> **关键点**：`onMounted` 在 SSR 期间**不会执行**，把数据获取写在 `onMounted` 里，服务端渲染出的 HTML 就是空数据，首屏 SEO 完全失效。

---

## 实战应用

### 1. 列表页：数据获取 + 缓存 + 分页

```vue
<!-- pages/blog/index.vue -->
<script setup lang="ts">
const route = useRoute()

const { data, pending, error, refresh } = await useAsyncData(
  'blog-list',                        // key 必须唯一且稳定
  () => $fetch('/api/blog', { query: { page: route.query.page ?? 1 } }),
  {
    watch: [() => route.query.page],  // 页码变化时自动重新获取
    default: () => ({ list: [], total: 0 })
  }
)

useSeoMeta({ title: '博客列表', description: 'Vue 3 生态学习笔记' })
</script>

<template>
  <div>
    <!-- data 可能为 null，务必判空或用 default 兜底 -->
    <p v-if="pending">加载中…</p>
    <p v-else-if="error">加载失败：{{ error.message }}</p>

    <ul v-else>
      <li v-for="item in data.list" :key="item.id">
        <!-- NuxtLink 会为内部链接自动做预取 -->
        <NuxtLink :to="`/blog/${item.id}`">{{ item.title }}</NuxtLink>
      </li>
    </ul>

    <button @click="refresh()">刷新</button>
  </div>
</template>
```

### 2. 详情页：错误处理与 404

```vue
<!-- pages/blog/[id].vue -->
<script setup lang="ts">
const route = useRoute()
const { data: article, error } = await useFetch(`/api/blog/${route.params.id}`)

// 接口返回 404 时，让页面也返回 404 状态码，而不是 200 的空页面
if (!article.value || error.value) {
  throw createError({ statusCode: 404, statusMessage: '文章不存在', fatal: true })
}

useSeoMeta({ title: article.value.title, description: article.value.summary })
</script>
```

### 3. 混合渲染配置

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],
  ssr: true, // 默认值，显式写出来便于团队理解
  routeRules: {
    '/': { prerender: true },
    '/blog/**': { swr: 3600 },
    '/admin/**': { ssr: false }
  },
  // 未加 public 的字段只在服务端可见，适合放密钥
  runtimeConfig: {
    apiSecret: '',
    public: { apiBase: 'https://api.example.com' }
  }
})
```

### 4. SSR 性能优化

| 手段 | 做法 | 收益 |
|------|------|------|
| 按路由降级渲染 | `routeRules: { '/admin/**': { ssr: false } }` | 后台页面不再占用服务端渲染资源，且被排除出服务端 bundle |
| 静态化 / 缓存 | `prerender: true`、`swr: 3600`、`isr: true` | 把「每请求渲染」变成「命中缓存」，服务端成本下降一个数量级 |
| 接口层缓存 | Nitro 的 `defineCachedEventHandler` / `defineCachedFunction` | 重查询接口做服务端缓存，避免每次渲染都打数据库 |
| 减小 payload | `useFetch` 的 `pick` / `transform` 只保留必要字段 | HTML 体积更小，水合更快 |
| 流式渲染 | `renderToWebStream` / `pipeToWebStream` 配合 `<Suspense>` 先推送已就绪部分 | TTFB 显著降低（Nuxt 默认用 `renderToString` 一次性返回，需要流式时要在 Nitro 层自定义渲染处理函数） |
| 避免重复请求 | 保持 `useAsyncData` 的 key 稳定，利用 payload 复用 | 客户端水合后不再重复请求同一份数据 |
| 减少首屏水合量 | `lazy: true`、`<ClientOnly>`、`defineAsyncComponent` | 减少首屏需要水合的节点数量 |
| 减少 SSR 中的重计算 | 把只在客户端需要的计算移到 `onMounted` | 直接降低单次渲染耗时 |

```typescript
// server/api/hot-articles.ts —— 接口层缓存
export default defineCachedEventHandler(
  async () => db.article.findHot(), // TTL 内这段逻辑只执行一次
  { maxAge: 60, swr: true, getKey: () => 'hot-articles' }
)
```

---

## 常见面试题

### 1. SSR 和 CSR 有什么区别？为什么 SSR 首屏更快？

CSR 下服务端只返回空壳 HTML，浏览器需要等 JS 下载、执行、发请求、拿到数据后才渲染，首屏存在白屏；SSR 下服务端先执行一遍组件代码，直接返回带内容的 HTML，浏览器拿到即可显示，因此首屏更快，爬虫也无需执行 JS 即可索引内容。SSR 的代价是开发受限（浏览器 API 只能在特定生命周期用）、需要 Node 环境部署、服务端渲染有 CPU 开销，以及必须处理水合与跨请求状态隔离。

### 2. 什么是水合？水合不匹配的常见原因有哪些？

水合是客户端接管服务端静态 HTML 的过程：客户端创建与服务端完全相同的应用实例，把 VNode 树与已有 DOM 逐一比对，复用节点并挂上事件监听器与动态属性，使页面可交互。不匹配的常见原因：模板中存在不合规范的 HTML 嵌套（如 `<div>` 放在 `<p>` 里，被浏览器解析纠正）、渲染了随机值（`Math.random()` / `Date.now()`）、服务端与客户端时区或语言环境不一致、渲染期读取浏览器 API、`v-if` 依赖客户端状态、第三方库或浏览器扩展在水合前修改了 DOM、自定义指令只实现了 `mounted` 而被 SSR 忽略、`Teleport` 目标设为 `body`。Vue 遇到不匹配会尝试自动恢复（丢弃不匹配节点并重建），但会有性能损失。

### 3. Vue 3 原生 SSR 提供了哪些 API？

服务端 API 位于 `vue/server-renderer`：`renderToString(app, context?)` 返回 `Promise<string>`；流式渲染有 `renderToWebStream`、`pipeToWebWritable`、`pipeToNodeWritable`、`renderToSimpleStream`（`renderToNodeStream` 在 ESM 构建下不可用，应改用 `pipeToNodeWritable`）。应用侧用 `createSSRApp()` 创建支持水合的应用实例，客户端 `mount()` 时会走水合分支而非新建 DOM。`useSSRContext()` 用于在组件内拿到 `renderToString` 传入的上下文对象，典型用途是收集要写进 `<head>` 的元数据，且必须确保只在服务端调用。

### 4. 为什么 SSR 下不能把状态放在模块级单例？怎么解决？

浏览器中每次页面访问都会重新初始化模块，模块级状态天然是「每页面一份」；但服务端模块只在启动时初始化一次，同一个单例会被所有请求复用，一旦写入某个用户的数据就可能泄露给其他请求，这就是跨请求状态污染。解决方案是每个请求创建全新的应用实例（含 router 与 store），通过应用级 `app.provide()` 提供共享状态，而不是在组件里直接 `import` 单例。Pinia 在 SSR 下要求 `state` 必须是返回对象的函数，Nuxt 的 `useState` 把状态挂到当前请求的应用实例上，都是同一个思路。

### 5. `useAsyncData` 和 `useFetch` 有什么区别？

`useFetch` 是 `useAsyncData` 与 `$fetch` 的封装，key 由 URL 和选项自动生成，适合单个 HTTP 请求；`useAsyncData` 更底层，key 必须手动指定，可以执行任意异步逻辑，适合多个请求组合、需要对结果做复杂加工、或数据源不是 HTTP 的场景。两者返回值一致（`data` / `pending` / `error` / `refresh` / `execute` / `status` / `clear`），且都是 SSR 友好的：服务端执行、结果序列化进 payload，客户端水合时直接复用不会重复请求。使用时要注意 `data` 默认是 `null`，且 `key` 必须唯一稳定。

### 6. SSR 下 `window is not defined` 怎么解决？

根因是通用代码在 Node.js 中执行时访问了浏览器全局对象。处理方式分三类：一是用 `import.meta.client` / `import.meta.server` 做环境判断；二是把浏览器相关的访问惰性化，放到只在客户端执行的 `onMounted` 中；三是把整个组件隔离到客户端渲染，Nuxt 中可用 `<ClientOnly>` 组件或 `*.client.vue` 后缀。对在模块顶层就访问 `window` 的第三方库，应改为动态 `import()` 或仅在客户端加载。

### 7. SSR 期间生命周期钩子有什么差异？

SSR 期间只有 `beforeCreate`、`created` 和 setup 根作用域会执行，`mounted` / `updated` / `beforeUnmount` / `unmounted` 等**都只在客户端运行**。因此有两点必须注意：一是数据获取不能写在 `onMounted` 里，否则服务端渲染出的 HTML 是空数据，SEO 收益为零，应使用 `useAsyncData` / `useFetch` 或 `onServerPrefetch`；二是会产生副作用且需要清理的代码（如 `setInterval`）不能放在 setup 根作用域或 `created` 中，因为清理钩子不会在服务端执行，会造成资源泄漏。

### 8. Nuxt 3 的渲染模式与 `routeRules` 是怎么配合的？

Nuxt 默认是 Universal Rendering（SSR + 水合），可通过 `ssr: false` 全局退化为 CSR。混合渲染通过 `routeRules` 按路由配置：`prerender: true` 构建时预渲染（SSG），`swr: 秒数` 缓存并在过期后先返回旧内容、后台再生，`isr` 与 `swr` 行为相同但会把响应加入支持该能力的平台 CDN 缓存（主要是 Netlify 与 Vercel，因此高度依赖部署平台），`ssr: false` 让该路由只在浏览器渲染。使用 `isr` / `swr` 的路由会额外生成 `_payload.json`，客户端导航时加载缓存 payload 而非重新请求。需要注意 `nuxt generate` 不支持混合渲染。

### 9. SSR 应用的性能优化有哪些手段？

按收益排序：一是**按路由降级与缓存**——后台路由 `ssr: false`，静态页 `prerender`，列表页 `swr` / `isr`，把「每请求渲染」变成「命中缓存」；二是**接口层缓存**，用 Nitro 的 `defineCachedEventHandler` / `defineCachedFunction` 避免每次渲染都打数据库；三是**流式渲染**，用 `renderToWebStream` 尽早输出首字节；四是**减小 payload**，用 `pick` / `transform` 只传必要字段；五是**减少首屏水合量**，非关键组件 `lazy: true`、用 `<ClientOnly>` 隔离客户端专属组件；六是**避免重复请求**，保持 `useAsyncData` 的 key 稳定以复用 payload；七是**把只属于客户端的重计算移到 `onMounted`**。

---

## 避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 在 `onMounted` 中获取首屏数据 | 服务端 HTML 里没有内容，SEO 失效 | `onMounted` 在 SSR 期间不执行 | 改用 `useAsyncData` / `useFetch`，纯 Vue SSR 用 `onServerPrefetch` |
| 在 setup 根作用域写 `setInterval` | 服务端定时器永不清理，内存持续增长 | 清理钩子在 SSR 期间不执行 | 副作用放到 `onMounted`，并在 `onUnmounted` 中清理 |
| 在渲染期访问 `window` / `document` / `localStorage` | `window is not defined`，进程报错 | 服务端没有浏览器全局对象 | 用 `import.meta.client` 判断；放到 `onMounted`；用 `<ClientOnly>` 或 `*.client.vue` 隔离 |
| 引入在模块顶层访问 `window` 的第三方库 | 引入即报错 | 该库没有做通用化处理 | 改为动态 `import()` 或仅在客户端加载 |
| 模块级 `ref` / `reactive` 作为共享状态 | 用户之间串数据 | 服务端模块只初始化一次，单例被所有请求复用 | 用 `useState`，或每请求创建实例并 `app.provide()` |
| Pinia 的 `state` 写成对象而非函数 | SSR 下跨请求状态污染 | 对象形式在模块加载时创建，成为单例 | `state: () => ({ ... })` |
| 服务端 `$fetch` 未透传 Cookie | 首屏显示未登录，水合后才变登录态 | 服务端请求没有浏览器的 cookie 自动附带 | 用 `useRequestHeaders(['cookie'])` 取出后传入 `headers` |
| 把敏感数据放进会被序列化的 state | 浏览器 payload 中能直接看到 | state 会随 HTML 下发到客户端 | 敏感数据只留在服务端，不进 `useState` / Pinia |
| `useAsyncData` 的 key 不唯一 | 两个组件显示同一份数据，刷新逻辑互相干扰 | key 冲突导致 payload 复用错位 | key 用业务语义命名并保证全局唯一 |
| 模板中直接使用 `data.xxx` | 报「读取 null 的属性」 | `useAsyncData` / `useFetch` 的 `data` 默认是 `null` | 提供 `default` 或用 `v-if="data"` 兜底 |
| 用 `typeof window !== 'undefined'` 渲染差异内容 | 水合不匹配警告 | 服务端与客户端渲染分支不同 | 用 `<ClientOnly>`，或 `data-allow-mismatch`（Vue 3.5+），或延后到 `onMounted` |
| 在模板里写 `<p><div>hi</div></p>` | 水合不匹配 | 浏览器会纠正非法嵌套，DOM 与 VNode 结构不一致 | 使用合法的 HTML 嵌套结构 |
| 在渲染期使用 `Math.random()` / 本地时间格式化 | 水合不匹配、首屏闪烁 | 两次执行结果不同（随机值、时区差异） | 用 `v-if` + `onMounted` 延后到客户端，或统一随机种子 / 时区 |
| 把 `Teleport` 目标设为 `body` | 水合时无法确定起始位置 | `<body>` 中已有其他 SSR 渲染出的内容 | 使用独立容器，如 `<div id="teleported"></div>` |
| 认为 `data-allow-mismatch` 能修复问题 | 警告消失但仍闪烁、性能仍差 | 它只消除警告，节点依然会被客户端重建 | 优先定位并消除不匹配的真实原因，把它当最后手段 |
| 在 `definePageMeta` 中传入变量 | 配置不生效 | 它是编译宏，无法静态分析动态对象 | 直接写对象字面量，动态值从路由参数或 `useState` 读取 |
| 用 SSR 渲染强个性化页面 | 服务端 CPU 飙高、缓存命中率为零 | 每个用户内容都不同，无法缓存 | 个性化部分改成客户端渲染，或整页降级为 CSR |
| 用 `isr` 却部署在不支持的平台上 | 缓存不生效，行为退化成普通 SSR | ISR 依赖平台 CDN 缓存能力（Netlify / Vercel） | 确认部署平台支持，或改用 `swr` / Nitro 缓存 |
| 手写生产级 SSR 流程 | 构建配置复杂、资源提示缺失、问题频发 | 生产 SSR 需要双份构建、资源注入、路由与状态通用化 | 直接使用 Nuxt 等上层框架 |

---

> **学习导航**：
> - 返回 [学习路线总览](../README.md)
> - 本模块其他原理文件：[01-Vue3核心语法](./01-Vue3核心语法.md) | [02-响应式与编译优化](./02-响应式与编译优化.md) | [03-路由与状态管理](./03-路由与状态管理.md) | [04-Vue3笔面试题集](./04-Vue3笔面试题集.md)
> - 实战应用：[企业后台管理系统](../10-project/01-企业后台管理系统实战.md)

## 本章学习自检

- [ ] 我能说清 CSR、SSR、SSG、ISR 四种渲染模式的区别与各自适用场景
- [ ] 我能根据「是否需要 SEO / 内容是否个性化 / 数据是否构建期已知」做出选型判断
- [ ] 我理解水合（Hydration）的执行流程，以及为什么服务端与客户端要执行两遍代码
- [ ] 我能列举至少 5 种水合不匹配的常见原因并给出排查思路
- [ ] 我知道 `data-allow-mismatch` 的作用与它的定位（消除警告而非修复问题）
- [ ] 我能说出 `createSSRApp` 与 `createApp` 的区别
- [ ] 我理解 `renderToString` 与 `useSSRContext` 的用法，知道 `useSSRContext` 只能在服务端调用
- [ ] 我能列举 Vue 的流式渲染 API，并说明流式渲染的收益
- [ ] 我理解跨请求状态污染的成因，以及 `app.provide()` 和每请求实例化的解决思路
- [ ] 我能说出 SSR 期间哪些生命周期钩子会执行、哪些不会
- [ ] 我能说出 `useAsyncData` 与 `useFetch` 的区别，知道 `data` 默认是 `null`
- [ ] 我理解 `useState` 为什么比模块级 `ref` 更适合 SSR
- [ ] 我知道 `definePageMeta` 是编译宏以及它的使用限制
- [ ] 我能用 `server/api` 编写服务端接口，并用 `createError` 返回正确的 HTTP 状态码
- [ ] 我能用 `useSeoMeta` 设置页面元信息，并说明它相比 `document.title` 的优势
- [ ] 我能用 `routeRules` 配置混合渲染，并说明 ISR 对平台的依赖
- [ ] 我理解 Pinia 在 SSR 下为什么要求 `state` 必须是函数
- [ ] 我能说出至少 6 种 SSR 性能优化手段及其收益层级
- [ ] 我能说出 `window is not defined` 的三类解决方案
- [ ] 我知道服务端请求为什么要手动透传 Cookie
