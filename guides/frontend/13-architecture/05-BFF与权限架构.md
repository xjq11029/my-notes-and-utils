> 模块：13-architecture（架构师进阶 第13周 前端架构设计）
> 难度：★★★ 架构核心
> 前置知识：HTTP 缓存、Vue Router 4 / React Router 6、JWT 与 Cookie 基础

---

# 05-BFF与权限架构

> **与 09-nodejs 模块的分工**：`09-nodejs/02-Web框架与BFF层.md` 已从 **Node 实现视角** 讲过 BFF —— Koa / Express 中间件、洋葱模型、Cookie 与 Session、JWT 签发与校验、BFF 聚合接口的代码写法、PM2 部署。本文件**不重复这些内容**，聚焦 **架构设计视角**：BFF 的职责边界与粒度划分、与 API Gateway 的分工、缓存与降级策略、反模式识别，以及前端权限体系（模型选型、四级权限、越权防护）。需要 Node 层代码细节时请回看 09 模块。

---

## 一、核心概念

### 1.1 BFF 的定义与解决的问题

**BFF（Backend For Frontend）** 由 Sam Newman 系统化提出，最早来自 SoundCloud 实践：**为每一种前端客户端提供专属的后端服务层**，位于客户端与后端微服务之间。它不是"多写一层代码"，而是为了解决客户端与微服务之间的**阻抗失配**。

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Web App  │  │  iOS App  │  │ 小程序    │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  BFF-Web  │  │ BFF-App  │  │ BFF-MP    │   ← 前端团队维护
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      └──────────────┼──────────────┘
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │用户服务 │  │订单服务 │  │商品服务 │   ← 后端团队维护
   └────────┘  └────────┘  └────────┘
```

| 问题 | 无 BFF 时的现象 | BFF 的做法 |
|---|---|---|
| **多端数据聚合** | 首页需要 5 个接口，弱网下 5 次 RTT 叠加，首屏 3 秒以上 | 一次请求完成聚合，1 次 RTT |
| **接口裁剪** | 后端返回 60 个字段、前端只用 8 个，流量浪费且暴露内部字段 | 按端裁剪，移动端只返回必要字段 |
| **协议转换** | 后端是 gRPC / Thrift / SOAP，浏览器无法直接消费 | 统一转换为 REST / GraphQL |
| **变更隔离** | 后端字段改名，三个端同时改代码同时上线 | 后端变更由 BFF 吸收，客户端按自己节奏发版 |

**架构定位的关键判断**：BFF 属于**客户端的一部分**，不属于后端。因此应由**前端团队负责开发和运维**，遵循客户端的发布节奏（可一天发多次），而不是跟随后端服务的发布窗口。这是 BFF 能否真正发挥价值的组织前提。

### 1.2 BFF 与 API Gateway 的职责边界

两者关注点完全不同，在大型系统中通常**同时存在**：`客户端 → CDN / 边缘 → API Gateway → BFF → 微服务`。

| 维度 | API Gateway | BFF |
|---|---|---|
| **服务对象** | 所有外部流量（含第三方、OpenAPI） | 特定客户端（Web / App / 小程序各一个） |
| **核心关注点** | 安全、流量治理、协议接入 | 业务数据编排、面向端的接口形态 |
| **典型能力** | 统一鉴权、限流熔断、灰度路由、TLS 终止、IP 黑白名单、API 计量 | 数据聚合、字段裁剪、协议转换、客户端专属缓存 |
| **是否懂业务** | **不懂业务**，只做通用横切 | **懂业务**，知道"首页需要哪几块数据" |
| **归属团队** | 基础设施 / 中台团队 | 前端团队 |
| **变更频率** | 低（改一次影响全站） | 高（跟随客户端迭代） |
| **技术选型** | Kong / APISIX / Envoy / Spring Cloud Gateway | Node.js（NestJS / Fastify / Koa）、Bun、Deno、Java |
| **故障影响面** | 全站不可用 | 单个端不可用 |

**一句话区分**：**API Gateway 关心"这个请求能不能进来"，BFF 关心"这个请求要返回什么数据"。**

**边界设计的三条原则**：
1. **鉴权两层都做，但语义不同**：Gateway 做**身份认证**（你是谁、Token 是否有效），BFF 做**数据权限收敛**（这个用户能看到哪些数据）。绝不能只在 BFF 做认证，因为 Gateway 是更靠前、更统一的可信边界。
2. **限流放在 Gateway**：BFF 实例数少、扩缩容慢，做全局限流成本高。BFF 只做**面向单用户的下游保护**（如对某个微服务的并发上限）。
3. **不要把 Gateway 的能力搬进 BFF**：一旦 BFF 开始维护 IP 黑白名单、证书、路由规则表，它就会退化成"第二个网关"，职责失控。

### 1.3 BFF 的部署形态与粒度

**按端拆分（纵向切分）** —— 最常见形态：`BFF-Web`（接口胖、字段全）、`BFF-App`（字段瘦）、`BFF-MP`（字段最瘦、包体积敏感）。优点是各端独立演进；缺点是服务数量随端数线性增长，登录、埋点等公共逻辑容易复制多份。适用**端之间数据形态差异大**的场景。

**按业务域拆分（横向切分）** —— 大型组织形态：`BFF-Trade` / `BFF-User` / `BFF-Content`，与后端微服务边界对齐（拆分逻辑与 01 微前端一致）。缺点是单页面跨域聚合时客户端仍需多次请求。适用**端间数据形态接近、但域多团队多**的场景。

**端 × 域二维矩阵** —— 大厂常见，能同时满足两种诉求，但服务数量 = 端数 × 域数，运维成本最高。实践中常用**一个 BFF 承载多个端**（通过请求头 `X-Client-Type` 区分响应形态）来降本，代价是服务内部维护多套响应适配逻辑。

| 团队规模 | 端数量 | 域数量 | 推荐粒度 |
|---|---|---|---|
| < 10 人前端 | 1-2 | 任意 | 单个 BFF，甚至不引入 BFF |
| 10-30 人前端 | 2-3 | 3-5 | 按端拆分 |
| 30-100 人前端 | 3+ | 5+ | 按端拆分为主 + 域内聚合 |
| 100+ 人前端 | 3+ | 10+ | 端 × 域矩阵，配 BFF 脚手架统一规范 |

### 1.4 前端网关与流量治理

"前端网关"是 BFF 再往前的**流量入口**，通常由 CDN + Nginx / 边缘运行时共同承担。

| 职责 | 说明 | 典型实现 |
|---|---|---|
| **路由分发** | 按路径 / 域名 / 请求头把流量导向不同集群 | Nginx `location`、`map` |
| **灰度发布** | 按用户 ID / 设备 ID / 比例分流 | Nginx `split_clients`、服务网格 VirtualService |
| **鉴权前置** | 在边缘校验 Token，拦截未登录流量，减少回源 | Edge Runtime、Nginx `auth_request` |
| **限流** | 令牌桶 / 漏桶，按 IP、UID、租户维度 | APISIX、Envoy |
| **静态资源加速** | HTML / JS / CSS / 图片就近分发 | CDN 边缘节点 |
| **A/B 实验** | 按实验分组注入不同 HTML 或配置 | 边缘运行时改写 HTML |

**边缘计算（Edge Runtime）在前端的四类应用**：

| 场景 | 传统做法 | 边缘做法 | 收益 |
|---|---|---|---|
| 多语言路由重写 | Nginx 维护 `map` 表 | 边缘函数按 `Accept-Language` 重写 | 配置即代码，可灰度 |
| 首屏个性化 | 客户端拉用户信息再渲染 | 边缘注入用户信息到 HTML | 减少 1 次 RTT，避免首屏闪变 |
| A/B 实验分流 | 客户端加载 SDK 后分流 | 边缘决定返回哪份 HTML | 无闪烁、无 SDK 体积 |
| 地理位置定价 | 后端按 IP 查库 | 边缘直接读取 `request.cf.country` | 免回源查询 |

```typescript
// 边缘函数示例（Cloudflare Workers 模块语法，Next.js Middleware 思路一致）
export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    // 1. 多语言路由重写：/product → /zh-CN/product
    if (!/^\/(zh-CN|en-US|ja-JP)\//.test(url.pathname)) {
      const locale = negotiateLocale(request.headers.get('Accept-Language'));
      url.pathname = `/${locale}${url.pathname}`;
      // 注意：rewrite 用 fetch 转发，redirect 会改变浏览器地址栏
      return fetch(new Request(url, request));
    }

    // 2. 灰度分流：按设备 ID 哈希取模，保证同一用户命中稳定
    const bucket = hash(request.headers.get('X-Device-Id') ?? '') % 100;
    url.searchParams.set('exp', bucket < 10 ? 'v2' : 'v1');

    return fetch(new Request(url, request));
  },
};
```

> **注意**：边缘运行时通常是 **V8 Isolate 而非完整 Node.js**，不支持 `fs`、原生 `net` 及大部分 npm 原生模块。可用能力以目标平台文档为准（Cloudflare Workers / Vercel Edge / Deno Deploy 限制各不相同）。

### 1.5 权限模型：RBAC / ABAC / ReBAC

**RBAC（Role-Based Access Control）**：`用户 → 角色 → 权限`，权限不直接授予用户，而是通过角色这一中间层。

| 层级 | 名称 | 能力 |
|---|---|---|
| RBAC0 | 核心 RBAC | 用户-角色、角色-权限两个多对多关系 |
| RBAC1 | 角色继承 | 角色有上下级，高级角色继承低级角色权限 |
| RBAC2 | 角色约束 | 互斥角色（不能同时是"制单人"和"审核人"）、角色基数限制 |
| RBAC3 | 统一模型 | RBAC1 + RBAC2 |

- 优点：模型简单、易理解易实现（两张关联表即可）
- 缺点：**角色爆炸** —— 当"华南区-家电类目-审核员"这类组合需求增多时，角色数量指数增长
- 适用：**绝大多数企业后台管理系统**，默认首选

**ABAC（Attribute-Based Access Control）**：通过**属性组合 + 策略表达式**判定 —— `主体属性 + 资源属性 + 操作 + 环境属性 → 允许/拒绝`。

```javascript
// 策略表达式的语义（以 Rego / Cedar 类策略语言为例，非直接可执行代码）
// 允许：主体部门与资源部门相同，且资源密级不高于主体密级，且在工作时间内
allow if {
  subject.department == resource.department
  resource.classification <= subject.clearance
  time.now().hour >= 9
  time.now().hour < 18
}
```

- 优点：表达能力强，可覆盖"同部门可编辑""只能在工作时间操作""密级不高于自身"；策略与代码解耦，可动态下发
- 缺点：策略编写与调试门槛高；判定通常需拿到资源属性，**成本高于 RBAC**；策略增多后难以反查"谁能访问 X"
- 适用：**合规要求高、规则维度多**的场景（金融、医疗、多租户 SaaS）
- 工程实现：OPA（Rego）、AWS Cedar、CASL（JS 生态 ABAC 库）

**ReBAC（Relationship-Based Access Control）**：权限来自**实体关系图**，用关系元组表达 `资源#关系@主体`。

```
document:report-2026#viewer@user:alice
document:report-2026#editor@group:finance#member
folder:reports#parent@document:report-2026
```

- 代表实现：Google Zanzibar 论文（2019）、OpenFGA（CNCF）、SpiceDB
- 优点：天然支持**共享、继承、嵌套**（"文件夹的查看者可查看文件夹内所有文档"），能反查"谁能访问这个资源"
- 缺点：需引入图存储与关系查询，架构复杂度显著上升；关系元组的一致性维护成本高
- 适用：**协作类产品**（在线文档、网盘、项目管理），即"用户把资源分享给他人"是核心功能的场景

| 场景特征 | 推荐模型 |
|---|---|
| 后台管理系统，权限由管理员配置 | RBAC |
| 权限维度少但要求灵活（时间、地域、密级） | RBAC + 少量 ABAC 策略 |
| 强合规、策略需审计和动态下发 | ABAC（策略引擎独立部署） |
| 资源可被用户互相分享、层级继承 | ReBAC |
| 混合场景 | RBAC 管"能不能进"，ABAC / ReBAC 管"能看哪些数据" |

### 1.6 前端权限的四个层次

前端的权限控制本质是**用户体验优化**，而不是安全边界。四个层次从粗到细：

| 层次 | 控制对象 | 实现方式 | 用户体验目标 |
|---|---|---|---|
| **路由级** | 页面能否进入 | 动态路由 + 全局前置守卫 | 无权限地址直接跳 403，不出现"能进去但报错" |
| **菜单级** | 导航项是否展示 | 路由表过滤后生成菜单 | 不展示点了就 403 的入口 |
| **按钮级** | 操作按钮是否可用 | 指令 / 组件 / Hook 判定 | 不展示点了就失败的操作 |
| **数据级** | 同页面内能看到哪些数据 | 字段级脱敏 + 后端按权限过滤 | 敏感字段不渲染，而非渲染后隐藏 |

> **命名补充**：路由级与菜单级通常成对出现（菜单由路由表派生），业界也常把二者合并称为"**页面级权限**"。

**关键认知**：四个层次**全部可以被绕过**（改内存、改 DOM、直接调接口），作用仅是**降低用户困惑和减少无效请求**。

### 1.7 前端权限不可信原则与越权防护

**核心原则**：**任何来自客户端的权限声明都不可信，越权防护必须由后端在每个数据接口上完成。**

| 绕过手段 | 具体操作 | 前端能防住吗 |
|---|---|---|
| 修改内存状态 | DevTools 修改 Pinia / Redux 中的 `permissions` 数组 | 不能 |
| 篡改 DOM | 删除按钮上的 `v-if`，或直接改 `display` | 不能 |
| 重放请求 | 从 Network 面板复制请求，用 curl 重放 | 不能 |
| 改 Token Payload | 修改 JWT Payload 中的 `role` 字段 | **能防住**（签名校验失败） |

| 越权类型 | 定义 | 例子 | 防护要点 |
|---|---|---|---|
| **水平越权**（横向） | 同角色用户访问**他人**数据 | 把 `/api/orders/1001` 改成 `/api/orders/1002` 看到他人订单 | 后端必须以 Token 中的 userId 作为查询条件，**不信任 URL 参数** |
| **垂直越权**（纵向） | 低权限用户执行**高权限**操作 | 普通用户直接调 `/api/admin/users/delete` | 每个接口做权限校验，不能只依赖前端隐藏入口 |

**IDOR（不安全的直接对象引用）** 是水平越权最常见的形态：接口直接使用客户端传入的资源 ID 查询，且未校验资源归属。

```javascript
// ❌ 水平越权漏洞：信任客户端传入的 userId
app.get('/api/orders', async (req, res) => {
  const { userId } = req.query; // 攻击者可传任意 userId
  res.json(await db.order.findMany({ where: { userId } }));
});

// ✅ 从可信来源（Token）获取 userId，忽略客户端传值
app.get('/api/orders', authMiddleware, async (req, res) => {
  const userId = req.auth.userId; // 来自已验签的 JWT / Session
  res.json(await db.order.findMany({ where: { userId } }));
});

// ✅ 单资源访问：查询条件同时包含资源 ID 和归属者 ID
app.get('/api/orders/:id', authMiddleware, async (req, res) => {
  const order = await db.order.findFirst({
    // 归属校验与查询合并，避免"先查后判"的竞态
    where: { id: req.params.id, userId: req.auth.userId },
  });
  if (!order) return res.status(404).json({ message: '订单不存在' });
  res.json(order);
});
```

> **安全建议**：资源不存在与无权访问统一返回 **404**，而不是 403。403 会泄露"该资源存在"这一信息，攻击者可据此枚举有效 ID 区间。

### 1.8 权限与多租户

SaaS 场景下，租户隔离是比用户权限更前置的一层约束。

| 隔离模式 | 数据层实现 | 隔离强度 | 成本 | 适用 |
|---|---|---|---|---|
| **独立数据库** | 每租户一个 DB 实例 | 最高 | 最高 | 金融、政企、强合规 |
| **共享库独立 Schema** | 每租户一个 Schema | 高 | 中 | 中大型 SaaS |
| **共享库共享表 + 租户字段** | 每行带 `tenant_id` | 中（依赖代码正确性） | 最低 | 中小型 SaaS、快速迭代 |

**链路传递**：`客户端 → 边缘（识别租户，注入 X-Tenant-Id）→ Gateway（校验租户合法性）→ BFF（透传）→ 微服务（写入查询条件）`

**三条必须遵守的规则**：
1. **租户 ID 必须由服务端推导，不能由客户端自由指定**。客户端只传"子域名 / 登录域名"这类**路由信息**，租户 ID 由边缘或网关按域名映射得出，防止 A 租户用户把 `X-Tenant-Id` 改成 B 租户。
2. **租户 ID 必须进入数据访问层，而不是靠开发者自觉**。推荐用 ORM 中间件 / 数据库行级安全（RLS）强制注入，避免某个查询漏写 `tenant_id` 造成跨租户泄露。
3. **缓存 Key 必须包含租户 ID**。`user:123:profile` 在多租户下会串数据，必须是 `tenant:{tid}:user:{uid}:profile`。

```typescript
// 用 ORM 中间件强制注入租户条件（以 Prisma 风格示例）
// 目标：业务代码里写 db.order.findMany() 时自动带上 tenantId，无法遗漏
const db = new PrismaClient().$extends({
  query: {
    $allModels: {
      async $allOperations({ args, query }) {
        const tenantId = tenantContext.getStore()?.tenantId;
        if (!tenantId) throw new Error('缺少租户上下文，拒绝执行查询');
        args.where = { ...(args.where ?? {}), tenantId }; // 强制合并，即使业务层没写
        return query(args);
      },
    },
  },
});
```

> `AsyncLocalStorage`（Node.js）是实现"请求级上下文自动透传"的标准手段，`tenantContext.getStore()` 读取当前请求的隔离存储，无需逐层传参。

---

## 二、底层原理

### 2.1 BFF 数据聚合的并行编排与部分失败

聚合 5 个下游接口、每个耗时 200ms：串行 1000ms，并行 200ms。

```typescript
// ❌ 串行：耗时线性累加（总计 600ms）
async function getHomeDataSerial(userId: string) {
  const user = await userService.get(userId);
  const orders = await orderService.list(userId);
  const coupons = await couponService.list(userId);
  return { user, orders, coupons };
}

// ✅ 并行：耗时取最大值（总计 200ms）
async function getHomeDataParallel(userId: string) {
  const [user, orders, coupons] = await Promise.all([
    userService.get(userId),
    orderService.list(userId),
    couponService.list(userId),
  ]);
  return { user, orders, coupons };
}
```

**部分失败的处理**：`Promise.all` 一旦有任一失败就整体 reject，首页会因为"优惠券服务抖动"而全白。BFF 必须按**数据重要程度**分级降级。

```typescript
async function getHomeData(userId: string) {
  // 关键数据：拿不到就没法渲染，失败直接抛错
  const user = await userService.get(userId);

  // 非关键数据：并行请求，各自兜底
  const [ordersResult, couponsResult, bannersResult] = await Promise.allSettled([
    orderService.list(userId),
    couponService.list(userId),
    contentService.banners(),
  ]);

  return {
    user,
    // 优惠券：失败降级为空数组 + 标记，前端据此区分"暂无"与"加载失败"
    coupons: couponsResult.status === 'fulfilled' ? couponsResult.value : [],
    couponsDegraded: couponsResult.status === 'rejected',
    orders: ordersResult.status === 'fulfilled' ? ordersResult.value : null,
    // 运营位：失败时用本地兜底图，不影响主流程
    banners: bannersResult.status === 'fulfilled' ? bannersResult.value : DEFAULT_BANNERS,
  };
}
```

**超时控制**：任何下游调用都必须有超时，否则慢下游会耗尽 BFF 的并发能力。

```typescript
// ⚠️ 用 Promise.race 实现的超时只是"放弃等待"，被放弃的请求仍在进行
async function withTimeout<T>(promise: Promise<T>, ms: number, fallback: T): Promise<T> {
  const timeout = new Promise<T>((resolve) => setTimeout(() => resolve(fallback), ms));
  return Promise.race([promise, timeout]);
}

// ✅ 推荐：用 AbortSignal.timeout 真正取消请求（Node 17.3+ / 现代浏览器）
async function fetchWithTimeout(url: string, ms: number) {
  return fetch(url, { signal: AbortSignal.timeout(ms) });
}
```

| 编排形态 | 实现 | 适用 |
|---|---|---|
| 固定聚合 | `Promise.all` 写死字段 | 首页、详情页这类结构固定的接口 |
| 声明式聚合 | 配置化描述"哪个字段来自哪个服务" | 接口数量多、希望前端自助新增字段 |
| 图查询聚合 | GraphQL / GraphQL Federation | 客户端需要自由组合字段 |

### 2.2 BFF 的缓存与降级策略

BFF 是缓存的**最佳落点**，因为它既了解客户端诉求，又贴近下游服务。

| 缓存层 | 位置 | 缓存内容 | 典型 TTL |
|---|---|---|---|
| CDN / 边缘 | 最外层 | 静态资源、公共接口响应 | 长（天级） |
| 前端网关 | 中间层 | 页面级 HTML、公开数据接口 | 分钟级 |
| **BFF** | **聚合层** | **聚合结果、下游单点结果** | **秒级 ~ 分钟级** |
| 下游微服务 | 最内层 | 领域数据 | 按业务 |

**两种缓存粒度**：**整体缓存**（缓存聚合结果）实现简单，但命中率受"最易变字段"拖累 —— 首页聚合里含"未读消息数"（秒级变化）会导致整体只能缓存 1 秒；**分片缓存**（缓存下游单点结果）命中率高但实现复杂 —— 把"用户资料"缓存 60s、"未读数"不缓存，各自独立。

```http
# 公共数据接口：允许 CDN 与浏览器共同缓存，过期后先返回旧值再后台刷新
Cache-Control: public, max-age=60, s-maxage=300, stale-while-revalidate=600, stale-if-error=86400

# 用户私有数据：只允许浏览器私有缓存，禁止 CDN 缓存（避免串用户）
Cache-Control: private, max-age=0, no-cache

# 敏感数据：完全不缓存
Cache-Control: no-store
```

| 指令 | 含义 | 前端架构价值 |
|---|---|---|
| `s-maxage` | 共享缓存（CDN）的 TTL，覆盖 `max-age` | 让 CDN 缓存更久、浏览器缓存更短 |
| `stale-while-revalidate` | 过期后在指定时间内**先返回旧值**，同时异步刷新 | 消除"缓存过期瞬间"的延迟尖峰 |
| `stale-if-error` | 下游报错时继续返回旧值 | 下游故障时页面仍可用 |
| `private` | 禁止共享缓存 | 防止 CDN 把 A 用户数据返回给 B 用户 |

> **易错点**：带用户身份的数据接口若未设 `private`，且 CDN 配置了"忽略 Cookie 缓存"，会导致**跨用户数据泄露**。这是 BFF 上线最常见的高危问题。

**四级降级矩阵**：

| 级别 | 触发条件 | 手段 | 用户感知 |
|---|---|---|---|
| L1 局部降级 | 单个非关键下游超时 | 该字段返回默认值 / 空数组 | 某个模块显示"暂无数据" |
| L2 缓存降级 | 下游整体不可用 | 返回过期缓存（`stale-if-error`） | 数据可能略旧，页面可用 |
| L3 静态降级 | 缓存也不可用 | 返回预生成的静态兜底 JSON | 页面可看不可交互 |
| L4 熔断 | 下游错误率超阈值 | 直接快速失败，不再请求下游 | 提示服务繁忙，避免雪崩 |

熔断器状态机：`CLOSED（正常放行）→ 失败率超阈值 → OPEN（快速失败）→ 冷却时间到 → HALF_OPEN（放行少量探测）→ 探测成功 → CLOSED`。

### 2.3 GraphQL 作为 BFF 的实践与取舍

GraphQL 的定位与 BFF 高度重合：**让客户端精确声明所需数据，服务端一次返回**。

| 维度 | REST BFF | GraphQL BFF |
|---|---|---|
| 字段裁剪 | BFF 预先定义多套响应，新增字段要改 BFF 代码 | 客户端自由选择字段，BFF 无需改动 |
| 多端适配 | 每端一个接口或一个 `clientType` 分支 | 同一 Schema，客户端各自声明 |
| 请求次数 | 页面需要多个资源时仍可能多次请求 | 单次请求拿到整棵数据树 |
| 类型契约 | 依赖 OpenAPI 手工维护 | Schema 即契约，可自动生成 TS 类型 |
| 缓存 | 天然基于 URL，HTTP 缓存直接可用 | 需持久化查询 + 服务端缓存，HTTP 缓存基本失效 |
| 学习成本 | 低 | 高（Schema 设计、Resolver、性能治理） |

**必须处理的四个工程问题**：

**① N+1 查询** —— 列表里每个元素都触发一次下游查询。

```typescript
// ❌ N+1：10 个订单触发 10 次用户查询
const bad = { Order: { user: (order) => userService.get(order.userId) } };

// ✅ DataLoader：同一事件循环内的请求合并为一次批量查询
import DataLoader from 'dataloader';

const userLoader = new DataLoader(async (userIds: readonly string[]) => {
  const users = await userService.getByIds([...userIds]);
  const map = new Map(users.map((u) => [u.id, u]));
  // 返回顺序必须与入参一一对应
  return userIds.map((id) => map.get(id) ?? null);
});

const good = { Order: { user: (order) => userLoader.load(order.userId) } };
```

> DataLoader 提供两个能力：**批量化**（同一 tick 内的多个 `load` 合并为一次调用）与**请求级缓存**。它必须**按请求创建**，不能做成全局单例，否则会串用户数据。

**② 查询复杂度攻击** —— 客户端可构造极深嵌套查询打垮服务端。

```typescript
// 防护：查询深度限制 + 复杂度评分 + 持久化查询白名单
import depthLimit from 'graphql-depth-limit';
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const validationRules = [
  depthLimit(7),                    // 最大嵌套深度 7 层
  createComplexityLimitRule(1000),  // 单次查询复杂度上限 1000
];
```

**③ HTTP 缓存失效** —— GraphQL 通常只有 `POST /graphql` 一个端点，CDN 无法按 URL 缓存。方案是 **APQ（Automatic Persisted Queries，自动持久化查询）**：客户端首次发送完整查询，服务端返回 hash；后续只发 hash，请求变为 `GET /graphql?extensions={"persistedQuery":{"sha256Hash":"..."}}`，**可被 CDN 缓存**。附带收益：只允许白名单查询，杜绝任意查询攻击。

**④ 错误语义** —— GraphQL 恒返回 HTTP 200，错误藏在 `errors` 数组里：

```json
{
  "data": { "user": null },
  "errors": [{ "message": "无权访问", "path": ["user"], "extensions": { "code": "FORBIDDEN" } }]
}
```

**前端必须显式检查 `errors`**，不能只看 HTTP 状态码；建议约定 `extensions.code` 与业务错误码体系对齐（`UNAUTHENTICATED` / `FORBIDDEN` / `NOT_FOUND`）。

**选型结论**：页面结构固定、接口可控 → REST BFF 更简单；多端字段差异大、频繁新增字段 → GraphQL 收益明显；需聚合多个后端团队的服务 → GraphQL Federation 有价值；**团队无 GraphQL 经验、无性能治理能力 → 不要用**。

### 2.4 动态路由与权限路由的实现原理

**本质**：把"路由表"从**静态常量**变为**运行时根据权限计算出的结果**。

```
登录 → 拉取用户权限 → 权限码集合 → 过滤静态路由表 → 得到可访问路由
     → router.addRoute() 动态注册 → 生成菜单 → 渲染页面
```

| 形态 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| **后端返回路由表** | 后端下发菜单/路由 JSON，前端动态注册 | 权限变更即时生效，前端无需发版 | 前端路由结构被后端耦合；组件路径需与前端约定 |
| **前端全量路由 + 权限码过滤** | 前端定义全部路由（含 `meta.permission`），按权限码过滤 | 前端掌控路由结构，组件映射简单 | 新增页面需前端发版 |
| **混合模式** | 路由结构前端定，可访问性由后端权限码决定 | 兼顾两者 | 需约定权限码规范 |

```typescript
// 静态路由（无需权限）
export const constantRoutes: RouteRecordRaw[] = [
  { path: '/login', component: () => import('@/views/Login.vue') },
  { path: '/403', component: () => import('@/views/Forbidden.vue') },
];

// 动态路由（需要权限），meta.permission 声明所需权限码
export const asyncRoutes: RouteRecordRaw[] = [
  {
    path: '/system',
    component: () => import('@/layout/index.vue'),
    meta: { title: '系统管理', permission: 'system' },
    children: [
      {
        path: 'user',
        component: () => import('@/views/system/User.vue'),
        meta: { title: '用户管理', permission: 'system:user:list' },
      },
    ],
  },
];

// 递归过滤：父路由无权限则整棵子树丢弃
function filterRoutes(routes: RouteRecordRaw[], codes: Set<string>): RouteRecordRaw[] {
  return routes
    .filter((route) => {
      const required = route.meta?.permission as string | undefined;
      return !required || codes.has(required);
    })
    .map((route) => ({
      ...route,
      children: route.children ? filterRoutes(route.children, codes) : undefined,
    }));
}
```

```typescript
// 全局前置守卫：在守卫里"首次"注册动态路由
router.beforeEach(async (to) => {
  const authStore = useAuthStore();

  if (!authStore.token) {
    return to.path === '/login' ? true : { path: '/login', query: { redirect: to.fullPath } };
  }

  if (!authStore.routesLoaded) {
    const codes = await authStore.fetchPermissions();
    filterRoutes(asyncRoutes, new Set(codes)).forEach((r) => router.addRoute(r));
    authStore.routesLoaded = true;
    // 关键：addRoute 后必须重新导航，让新路由参与匹配
    // 若直接 return true，本次导航仍按旧路由表解析，会命中 404
    return { ...to, replace: true };
  }

  return true;
});
```

**四个必须注意的点**：
1. **`addRoute` 之后必须重新导航**。`return { ...to, replace: true }` 让路由器用新路由表重新解析当前地址。
2. **登出时必须移除动态路由**。`router.removeRoute(name)` 或保存 `addRoute` 的返回函数逐个调用，否则切换账号后旧权限路由残留。
3. **刷新页面会丢失动态路由**（路由表在内存中），刷新后需重新走守卫流程；`routesLoaded` 不能简单持久化。
4. **404 通配路由必须最后注册**。`{ path: '/:pathMatch(.*)*' }` 若在动态路由之前注册，动态路由将永远无法匹配。

**React Router 6 的对应实现**：没有 `addRoute`，做法是**用状态驱动路由表** —— 权限拉取完成后 `setRoutes(filtered)`，`<Routes>` 重新渲染即完成"动态路由"。

```tsx
function AppRoutes() {
  const { routesLoaded, permissions } = useAuth();
  if (!routesLoaded) return <GlobalLoading />;

  const accessible = useMemo(() => filterRoutes(asyncRoutes, permissions), [permissions]);

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      {accessible.map((r) => (
        <Route key={r.path} path={r.path} element={r.element}>
          {r.children?.map((c) => (
            <Route key={c.path} path={c.path} element={c.element} />
          ))}
        </Route>
      ))}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
```

### 2.5 权限指令与权限组件的封装原理

按钮级权限有三种封装形态，本质都是"**读取权限码集合 → 判定 → 决定是否渲染 / 禁用**"。

| 形态 | 框架 | 特点 | 适用 |
|---|---|---|---|
| 指令 | Vue | 写法最简 `v-permission="'user:add'"`，但无法参与条件渲染表达式 | 按钮、操作项 |
| 组件 | Vue / React | `<Auth code="user:add">`，可组合、可传 fallback | 需要"无权限时展示替代内容" |
| Hook / Composable | Vue / React | `const canAdd = usePermission('user:add')`，可在逻辑中使用 | 需要参与计算、禁用态判断 |

```typescript
// Vue 3 指令实现
import type { App, Directive, DirectiveBinding } from 'vue';
import { useAuthStore } from '@/stores/auth';

function checkPermission(binding: DirectiveBinding<string | string[]>) {
  const authStore = useAuthStore();
  const required = Array.isArray(binding.value) ? binding.value : [binding.value];
  // 修饰符 .any 表示"满足任一权限码即可"，默认需要全部满足
  return binding.modifiers.any
    ? required.some((code) => authStore.permissions.has(code))
    : required.every((code) => authStore.permissions.has(code));
}

const permission: Directive<HTMLElement, string | string[]> = {
  // 用 mounted 而非 beforeMount：此时 el 已插入父节点，可安全操作 parentNode
  mounted(el, binding) {
    if (!checkPermission(binding)) {
      el.parentNode?.removeChild(el);
    }
  },
};

export function setupDirectives(app: App) {
  app.directive('permission', permission);
}
```

> **指令方案的已知缺陷**：`removeChild` 是**破坏性操作**，若后续权限发生变化，元素无法恢复（需重新渲染整个组件）。因此更适合"权限在会话内不变"的场景。若权限会动态变化，请改用组件或 `v-if`。

```vue
<!-- Vue 3 权限组件：无权限时可展示禁用按钮而非隐藏 -->
<template>
  <slot v-if="allowed" />
  <slot v-else name="fallback" />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

const props = withDefaults(
  defineProps<{ code: string | string[]; mode?: 'all' | 'any' }>(),
  { mode: 'all' }
);
const authStore = useAuthStore();

const allowed = computed(() => {
  const required = Array.isArray(props.code) ? props.code : [props.code];
  return props.mode === 'any'
    ? required.some((c) => authStore.permissions.has(c))
    : required.every((c) => authStore.permissions.has(c));
});
</script>
```

```tsx
// React 权限 Hook + 组件封装
import type { ReactNode } from 'react';

export function usePermission() {
  const permissions = useAuthStore((s) => s.permissions);
  return {
    has: (code: string | string[], mode: 'all' | 'any' = 'all') => {
      const required = Array.isArray(code) ? code : [code];
      return mode === 'any'
        ? required.some((c) => permissions.has(c))
        : required.every((c) => permissions.has(c));
    },
  };
}

export function Auth({ code, mode = 'all', fallback = null, children }: {
  code: string | string[];
  mode?: 'all' | 'any';
  fallback?: ReactNode;
  children: ReactNode;
}) {
  const { has } = usePermission();
  return <>{has(code, mode) ? children : fallback}</>;
}
```

**权限码设计规范**（比实现方式更容易出问题）：

```
推荐格式：{域}:{资源}:{操作}
  system:user:list / system:user:create / system:user:update / system:user:delete

约定：
1. 全部小写，冒号分隔，层级固定三段
2. 操作动词用统一词表：list / detail / create / update / delete / export / import / approve
3. 禁止出现 UI 概念（如 button:red:click），权限码描述业务能力而非界面元素
4. 前端不自行拼接权限码，全部从后端权限清单读取，避免命名漂移
```

**权限数据的获取与缓存**：

| 策略 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| **登录响应内联** | 登录接口直接返回 `permissions` 数组 | 少一次请求，首屏快 | 权限多时响应体大；权限变更需重新登录 |
| **独立权限接口** | `GET /api/me/permissions` | 职责清晰，可单独缓存 | 多一次 RTT |
| **Token 内嵌权限码** | 权限码放进 JWT Payload | 服务端无状态，零额外查询 | **Token 体积膨胀**，权限变更需等 Token 过期 |
| **Token 内嵌版本号** | Token 只放 `permVersion` | Token 小；权限可即时失效 | 需维护版本号与权限的映射缓存 |

**推荐组合**：Token 只放 `userId` + `tenantId` + `permVersion`；权限清单由 `GET /api/me/permissions` 返回并缓存在 Redis（key 含 `permVersion`，权限变更时递增版本号即可让缓存失效）。前端可缓存在内存（Pinia / Redux），但**不要**持久化到 localStorage 后长期不刷新，否则权限被回收后用户仍能看到入口。

### 2.6 BFF 的四种常见反模式

| 反模式 | 表现 | 根因 | 修正 |
|---|---|---|---|
| **变成新的巨石** | BFF 代码量超过前端主应用，改一处要全量回归，发布要排期 | 把业务逻辑（校验、计算、状态流转）写进 BFF，而非只做聚合编排 | BFF 只做聚合、裁剪、协议转换；业务逻辑归下游领域服务；Review 时检查 BFF 是否出现"业务规则" |
| **逻辑下沉混乱** | 同一段校验逻辑在前端、BFF、后端各写一遍，三处不一致导致脏数据 | 没有明确"校验归属"，开发者就近实现 | 约定：**格式校验**在前端（体验），**业务校验**在领域服务（唯一可信），BFF 只透传不校验 |
| **暴露内部接口** | 客户端能调到下游内部管理接口 | BFF 只做转发未做接口白名单 | 用显式路由表（白名单）而非通配转发；禁止 `app.use('*', proxy)` 式写法 |
| **职责越界** | BFF 开始维护 IP 黑白名单、证书、路由规则表 | 把 Gateway 的能力搬进 BFF | 明确边界：BFF 管"返回什么数据"，不管"能不能进来" |

---

## 三、实战应用

### 3.1 BFF 聚合接口完整实现（Fastify）

```typescript
// bff/src/routes/home.ts
import type { FastifyInstance } from 'fastify';

export async function homeRoutes(app: FastifyInstance, opts: { clients: DownstreamClients }) {
  const { userService, orderService, couponService, contentService } = opts.clients;

  app.get('/api/home', async (request, reply) => {
    // 用户身份只从已验签的 Token 中取，绝不从 query / body 取
    const userId = request.user.userId;

    // 关键数据：失败即整体失败（用户信息是页面渲染的前提）
    const user = await userService.get(userId);

    // 非关键数据：并行请求 + 各自兜底
    const [orders, coupons, banners] = await Promise.allSettled([
      orderService.list(userId),
      couponService.list(userId),
      contentService.banners(),
    ]);

    // 标记降级字段，让前端能区分"真的没有"和"加载失败"
    const degraded: string[] = [];
    if (orders.status === 'rejected') degraded.push('orders');
    if (coupons.status === 'rejected') degraded.push('coupons');
    if (banners.status === 'rejected') degraded.push('banners');

    // 用户私有数据禁止 CDN 缓存，允许浏览器短缓存
    reply.header('Cache-Control', 'private, max-age=30');

    return {
      // 只返回前端需要的字段，裁剪掉 phone / email 等敏感字段
      user: { id: user.id, nickname: user.nickname, avatar: user.avatar },
      orders: orders.status === 'fulfilled' ? orders.value.slice(0, 5) : [],
      coupons: coupons.status === 'fulfilled' ? coupons.value : [],
      banners: banners.status === 'fulfilled' ? banners.value : [],
      degraded,
    };
  });

  app.get('/healthz', async () => ({ status: 'ok' })); // 供网关探活
}
```

**BFF 接口设计的三条约定**：① 响应结构全站统一（`{ code, data, message }` 或直接返回业务对象，不要混用）；② **降级信息显式暴露**（如 `degraded: ['orders']`），否则前端无法区分"没有订单"与"订单服务挂了"；③ 不返回内部 ID 与内部字段（`dbId`、`internalStatus`、`operatorId`）。

**请求合并（DataLoader 思路）**：同一请求内多个模块都需要"用户信息"时，用 DataLoader 合并为一次下游调用。

```typescript
// 工厂函数：每个请求创建一套 loader，请求结束后随请求上下文一起回收
export function createLoaders(clients: DownstreamClients) {
  return {
    userLoader: new DataLoader<string, User | null>(async (ids) => {
      const users = await clients.userService.getByIds([...ids]);
      const map = new Map(users.map((u) => [u.id, u]));
      return ids.map((id) => map.get(id) ?? null);
    }),
  };
}

// 挂到请求上下文，请求结束自动丢弃
app.addHook('onRequest', async (request) => {
  request.loaders = createLoaders(clients);
});
```

> **反例警示**：把 DataLoader 做成模块级单例是严重错误。单例的请求级缓存会跨用户存活，导致 **A 用户拿到 B 用户的缓存数据**。

### 3.2 前端网关配置（Nginx 灰度与多租户路由）

```nginx
# 1. 按租户子域名映射后端集群（租户 ID 由服务端推导，不接受客户端传值）
map $host $tenant_backend {
    default              "https://bff-default.internal";
    "acme.example.com"   "https://bff-acme.internal";
    "globex.example.com" "https://bff-globex.internal";
}

# 2. 灰度分流：按设备 ID 哈希，保证同一用户稳定命中同一版本
split_clients "${http_x_device_id}${remote_addr}" $api_version {
    10%     "v2";
    *       "v1";
}

server {
    listen 443 ssl http2;
    server_name ~^(?<tenant>.+)\.example\.com$;

    location /api/ {
        proxy_pass $tenant_backend;
        # 覆盖客户端传入的同名头（Nginx 对同名 header 是覆盖语义）
        # 这是防止租户伪造的第一道防线
        proxy_set_header X-Tenant-Id $tenant;
        proxy_set_header X-Api-Version $api_version;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态资源：长期缓存 + 内容哈希文件名
    location ~* \.(js|css|woff2|png|jpg|svg)$ {
        root /var/www/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # HTML：不缓存，保证发版即时生效
    location / {
        root /var/www/html;
        add_header Cache-Control "no-cache";
        try_files $uri /index.html;
    }
}
```

> **关键安全点**：若使用 `proxy_pass_request_headers on` 且未显式覆盖 `X-Tenant-Id`，客户端可伪造该头实现跨租户访问。

### 3.3 Vue 3 完整权限体系实现

```typescript
// stores/auth.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { RouteRecordRaw } from 'vue-router';

export const useAuthStore = defineStore('auth', () => {
  const token = ref('');
  const permissions = ref<Set<string>>(new Set());
  const routesLoaded = ref(false);
  // 保存 addRoute 的返回值（移除函数），登出时逐个调用
  const removeHandlers = ref<Array<() => void>>([]);

  const hasPermission = computed(() => {
    return (code: string | string[], mode: 'all' | 'any' = 'all') => {
      const required = Array.isArray(code) ? code : [code];
      return mode === 'any'
        ? required.some((c) => permissions.value.has(c))
        : required.every((c) => permissions.value.has(c));
    };
  });

  async function fetchPermissions(): Promise<string[]> {
    const res = await http.get<{ permissions: string[] }>('/api/me/permissions');
    permissions.value = new Set(res.permissions);
    return res.permissions;
  }

  function registerRoutes(routes: RouteRecordRaw[], router: Router) {
    routes.forEach((route) => removeHandlers.value.push(router.addRoute(route)));
  }

  function reset() {
    // 关键：移除动态路由，防止切换账号后旧权限路由残留
    removeHandlers.value.forEach((remove) => remove());
    removeHandlers.value = [];
    token.value = '';
    permissions.value = new Set();
    routesLoaded.value = false;
  }

  return { token, permissions, routesLoaded, hasPermission, fetchPermissions, registerRoutes, reset };
});
```

```typescript
// 请求拦截器：401 统一登出并清理动态路由；403 触发权限自愈
http.interceptors.response.use(
  (res) => res.data,
  (error) => {
    const authStore = useAuthStore();
    const status = error.response?.status;
    if (status === 401) {
      authStore.reset();
      router.replace({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } });
    }
    // 403 表示后端判定无权 → 说明前端权限数据已过期，重新拉取
    if (status === 403) {
      authStore.routesLoaded = false;
    }
    return Promise.reject(error);
  }
);
```

> **设计要点**：把 **403 视为"前端权限数据过期"的信号**，触发权限重新拉取，而不是只弹错误提示。这是权限数据前后端不同步时最重要的自愈机制。

### 3.4 数据级权限：字段脱敏与行级过滤

```typescript
// 层次一：字段级 —— 无权限的字段直接不返回（而非返回后前端隐藏）
const FIELD_PERMISSION: Record<string, string> = {
  phone: 'user:field:phone',
  salary: 'user:field:salary',
  idCard: 'user:field:idCard',
};

function maskUser(user: User, permissions: Set<string>) {
  const result: Record<string, unknown> = { ...user };
  for (const [field, code] of Object.entries(FIELD_PERMISSION)) {
    // 直接删除，不返回空字符串（空字符串会泄露"该字段存在"）
    if (!permissions.has(code)) delete result[field];
  }
  return result;
}

// 层次二：行级 —— 数据范围权限（本人 / 本部门 / 本部门及下级 / 全部）
type DataScope = 'self' | 'dept' | 'dept_and_child' | 'all';

function buildScopeCondition(scope: DataScope, user: AuthUser) {
  switch (scope) {
    case 'self': return { ownerId: user.userId };
    case 'dept': return { deptId: user.deptId };
    // 部门树用 path 前缀匹配，避免递归查询
    case 'dept_and_child': return { deptPath: { startsWith: user.deptPath } };
    case 'all': return {}; // 仅限超管，且必须叠加租户条件
  }
}
```

**数据级权限必须由后端实现**。前端的脱敏（如 `138****8888`）只是展示层处理，**原始值绝不能出现在响应体中** —— 否则打开 Network 面板即可拿到完整手机号。

---

## 四、常见面试题

**Q1：BFF 和 API Gateway 有什么区别？为什么需要同时存在？**

**答案要点**：服务对象不同（Gateway 面向所有外部流量含第三方，BFF 面向特定客户端）；关注点不同（Gateway 管"能不能进来"—— 鉴权、限流、灰度、TLS 终止；BFF 管"返回什么数据"—— 聚合、裁剪、协议转换）；业务理解不同（Gateway 不懂业务只做通用横切，BFF 懂业务由前端团队维护）；归属与变更频率不同（Gateway 归基础设施团队、低频变更；BFF 归前端团队、跟随客户端高频迭代）。同时存在的价值：Gateway 提供统一可信的安全边界与流量治理，BFF 提供面向端的灵活数据编排，职责不重叠。

**Q2：BFF 的粒度应该如何划分？按端拆还是按业务域拆？**

**答案要点**：按端拆分适合端间数据形态差异大的场景，各端独立演进，缺点是服务数量随端数增长；按域拆分与后端微服务边界对齐，缺点是单页面跨域聚合仍需多次请求；端 × 域矩阵适合大型组织，运维成本最高，实践中常用 `X-Client-Type` 请求头让一个服务承载多端来降本。决策依据：团队规模、端数量、域数量、端间数据形态差异度。核心原则：BFF 属于客户端，应由前端团队维护并遵循客户端发布节奏。

**Q3：RBAC、ABAC、ReBAC 的区别和选型依据？**

**答案要点**：RBAC 是用户→角色→权限，模型简单易实现（含 RBAC0-3 四级），缺点是角色爆炸，适用绝大多数后台管理系统；ABAC 是主体/资源/操作/环境属性 + 策略表达式，表达能力强、策略可动态下发，缺点是判定成本高且难以反查"谁能访问 X"，适用强合规场景（OPA / Cedar / CASL）；ReBAC 是关系元组 `资源#关系@主体`，天然支持共享与继承，代表实现 Zanzibar / OpenFGA / SpiceDB，适用协作类产品。混合用法：RBAC 管"能不能进系统"，ABAC / ReBAC 管"能看哪些数据"。

**Q4：前端权限如何实现？为什么说前端权限不可信？**

**答案要点**：四个层次 —— 路由级（动态路由 + 守卫）、菜单级（路由表派生）、按钮级（指令/组件/Hook）、数据级（字段脱敏）。不可信的原因：内存状态可改、DOM 可改、请求可重放，前端只是"建议"而非"边界"；唯一可信的是后端签发并验签的 Token。越权防护必须由后端在每个数据接口上完成：水平越权靠"归属校验与查询合并"，垂直越权靠"每个接口的权限校验"。前端价值是减少无效请求、降低用户困惑。

**Q5：什么是水平越权和垂直越权？如何防护？**

**答案要点**：水平越权是同角色用户访问他人数据，典型形态是 IDOR；垂直越权是低权限用户执行高权限操作。水平越权防护：userId 只从 Token 取，绝不信任 query/body/URL；单资源查询把"归属条件"合并进 `where`，而不是"先查后判"。垂直越权防护：每个接口做权限校验（中间件 + 权限码注解），不能只依赖前端隐藏入口。资源不存在与无权访问统一返回 404，避免通过状态码枚举有效 ID。

**Q6：GraphQL 作为 BFF 有哪些坑？**

**答案要点**：N+1 查询（用 DataLoader 批量化 + 请求级缓存，且必须按请求创建，单例会串用户数据）；查询复杂度攻击（深度限制 + 复杂度评分 + 持久化查询白名单）；HTTP 缓存失效（单一 POST 端点无法按 URL 缓存，用 APQ 转成 GET 可缓存请求）；错误语义（GraphQL 恒返回 200，前端必须显式检查 `errors` 数组）。选型建议：团队无 GraphQL 经验、无性能治理能力时不要用，REST BFF 更稳。

**Q7：多租户系统在链路上如何保证租户隔离？**

**答案要点**：租户 ID 必须由服务端推导（从子域名/域名映射），客户端只传路由信息；边缘/网关必须覆盖客户端传入的 `X-Tenant-Id`（Nginx 同名 header 是覆盖语义）；租户条件必须进入数据访问层，用 ORM 中间件或数据库 RLS 强制注入；缓存 Key 必须包含租户 ID。三种隔离模式：独立库（最强最贵）、独立 Schema、共享表 + `tenant_id`（最省但最依赖代码正确性）。

---

## 五、避坑指南

| 坑点 | 现象 | 原因 | 解决方案 |
|---|---|---|---|
| BFF 演变成新的巨石 | BFF 代码量超过前端主应用，改一处要全量回归 | 团队把业务逻辑写进 BFF，而非只做聚合编排 | BFF 只做聚合、裁剪、协议转换；业务逻辑归下游领域服务 |
| 逻辑下沉混乱 | 同一段校验逻辑在前端、BFF、后端各写一遍，三处不一致导致脏数据 | 没有明确"校验归属" | 格式校验在前端（体验），业务校验在领域服务（唯一可信），BFF 只透传 |
| BFF 直接暴露内部接口 | 客户端能调到下游内部管理接口 | 只做转发未做接口白名单 | 用显式路由表（白名单）；禁止 `app.use('*', proxy)` 式通配转发 |
| 带用户身份的数据接口未设 `private` | CDN 把 A 用户数据返回给 B 用户 | 未设 `Cache-Control: private`，且 CDN 忽略 Cookie 缓存 | 用户私有接口强制 `private`；CDN 对 `/api/` 默认不缓存；上线前做缓存穿透测试 |
| 聚合接口用 `Promise.all` 导致整体失败 | 优惠券服务抖动，整个首页白屏 | 未区分关键与非关键数据 | 关键数据 `Promise.all`，非关键数据 `Promise.allSettled` + 兜底值，并返回 `degraded` 标记 |
| 下游调用无超时 | BFF 事件循环被慢下游占满，全部接口变慢 | 未设置请求超时 | 所有下游调用必须设超时（`AbortSignal.timeout`），并配合熔断器 |
| DataLoader 做成全局单例 | 用户看到他人数据（跨用户缓存泄露） | 单例的请求级缓存跨请求存活 | DataLoader 必须按请求创建，随请求上下文回收 |
| `router.addRoute` 后未重新导航 | 动态路由注册后页面空白或 404 | 当前导航已按旧路由表解析完成 | 守卫中返回 `{ ...to, replace: true }` 触发重新匹配 |
| 登出未移除动态路由 | 切换账号后低权限用户仍能通过地址访问旧权限页面 | `addRoute` 注册的路由在内存中未清理 | 保存 `addRoute` 返回的移除函数，登出时逐个调用 |
| 404 通配路由注册过早 | 动态路由永远匹配不到，全部跳 404 | `/:pathMatch(.*)*` 在动态路由之前注册 | 通配路由必须最后注册，或用 `hasRoute` 显式判断 |
| 权限码放进 JWT Payload | Token 超过 8KB 被网关拒绝；权限变更需等 Token 过期 | 权限码数量多且 Token 体积敏感 | Token 只放 `userId` + `tenantId` + `permVersion`；权限清单独立接口返回 |
| 用 403 泄露资源存在性 | 攻击者遍历 ID 枚举出有效资源区间 | 无权返回 403、不存在返回 404，状态码可区分 | 统一返回 404；日志中记录真实原因供排查 |
| 前端脱敏但响应体含原始值 | 打开 Network 面板即可看到完整手机号 | 只在前端做 `138****8888` 展示处理 | 敏感字段在后端删除或脱敏后再返回，前端拿不到原始值 |
| 多租户缓存 Key 未含租户 ID | 跨租户串数据，A 公司看到 B 公司数据 | 缓存 Key 设计遗漏租户维度 | 统一格式 `tenant:{tid}:...`；用工具函数生成 Key 避免手写 |
| 灰度分流未做用户粘性 | 同一用户在不同请求间命中不同版本，数据错乱 | 按随机数分流而非按稳定标识哈希 | 按用户 ID / 设备 ID 哈希取模，保证同一用户稳定命中 |

---

## 本章学习自检

- [ ] 能说清 BFF 解决的四个核心问题，并说明 BFF 与 API Gateway 的职责边界
- [ ] 能根据团队规模、端数量、域数量给出 BFF 粒度选型建议
- [ ] 能识别 BFF 的四种反模式（新巨石、逻辑下沉混乱、暴露内部接口、职责越界）
- [ ] 理解 BFF 缓存的分层设计与 `stale-while-revalidate` / `stale-if-error` 的适用场景
- [ ] 能设计"关键数据 `all` + 非关键数据 `allSettled`"的聚合降级方案与四级降级矩阵
- [ ] 能说明 GraphQL 作为 BFF 的四个工程问题及对应方案
- [ ] 能对比 RBAC / ABAC / ReBAC 的优缺点并给出选型依据
- [ ] 能实现 Vue 3 / React 的动态路由与权限路由（含 `addRoute` 后的重新导航）
- [ ] 能封装权限指令、权限组件、权限 Hook，并说明各自的适用场景与缺陷
- [ ] 能解释"前端权限不可信原则"，并区分水平越权与垂直越权
- [ ] 能识别 IDOR 漏洞并写出正确的归属校验查询
- [ ] 能说明多租户隔离的三种模式与三条必须遵守的规则
- [ ] 能设计数据级权限（字段级 + 行级）的后端实现方案

---

## 学习导航

- 上一章：[04-前端架构设计笔面试题集](./04-前端架构设计笔面试题集.md)
- 下一章：[06-国际化与多端同构](./06-国际化与多端同构.md)
- 导览文件：[05-BFF与权限架构-导览](./05-BFF与权限架构-导览.md)
- 相关模块（Node 实现视角）：[09-nodejs/02-Web框架与BFF层](../09-nodejs/02-Web框架与BFF层.md)
- 常见错误：[常见错误汇总](./常见错误汇总.md)
- 概念对比：[概念对比速查](./概念对比速查.md)
- 综合场景：[综合场景](./综合场景.md)
