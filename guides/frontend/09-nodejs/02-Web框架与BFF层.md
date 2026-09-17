# 02-Web 框架与 BFF 层

> 模块：09-nodejs（第9周 Node.js）
> 重点：Express/Koa、洋葱模型、JWT、BFF
> 难度：★★★★☆

---

## 一、核心概念

在 Node.js 生态中，Web 框架是构建服务端应用的基础设施。Express 和 Koa 是 Node.js 社区最主流的两大 Web 框架，它们分别代表了不同的设计哲学：

- **Express**：功能完备、开箱即用，内置路由、静态文件、模板引擎等，适合快速开发。
- **Express 5.x**：已于 2024 年 9 月正式发布（自 2014 年以来首个大版本），关键变化包括：路径路由匹配语法变更（Breaking Change）、Promise rejection 自动转发到中间件、要求 Node.js 18+。以下示例基于 Express 4.x，5.x 迁移时需注意正则路由语法变更。
- **Koa**：极简内核、洋葱模型，不绑定任何中间件，所有功能通过插件扩展，适合需要精细控制的场景。

BFF（Backend For Frontend）是一种架构模式，在微服务架构中为前端提供专属的后端服务层，负责数据聚合、格式转换和接口适配。

---

## 二、底层原理

### 2.1 Express 框架

Express 是 Node.js 最老牌、最流行的 Web 框架，基于中间件（Middleware）机制构建。

#### 核心概念

```javascript
const express = require('express');
const app = express();

// 中间件：处理请求和响应的函数
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next(); // 调用 next() 将控制权交给下一个中间件
});

// 路由定义
app.get('/api/users', (req, res) => {
  res.json({ users: [] });
});

// 错误处理中间件（必须有 4 个参数）
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: '服务器内部错误' });
});

// 静态文件服务
app.use(express.static('public'));

app.listen(3000, () => console.log('Server running on port 3000'));
```

#### 中间件机制

Express 的中间件是一个个函数，按照注册顺序依次执行。中间件可以：
- 执行任意代码
- 修改 `req` 和 `res` 对象
- 结束请求-响应周期（如 `res.send()`）
- 调用 `next()` 将控制权交给下一个中间件

**关键点**：如果中间件既不调用 `next()` 也不结束响应，请求会一直挂起，直到超时。

**Express 中间件链式调用时序图**：

```mermaid
%%{init: {'themeVariables': {'fontSize': '16px'}}}%%
sequenceDiagram
    participant C as "客户端"
    participant M1 as "中间件1（日志）"
    participant M2 as "中间件2（鉴权）"
    participant M3 as "中间件3（业务处理）"
    participant S as "响应"

    C->>M1: app.use(logger)
    Note over M1: 记录请求日志
    M1->>M2: next()
    Note over M2: 验证 Token
    M2->>M3: next()
    Note over M3: 处理业务逻辑<br/>查询数据库
    M3-->>M2: 返回处理结果
    M2-->>M1: 返回
    Note over M1: 记录响应日志
    M1-->>C: res.send() 响应返回
```

> Express 中间件通过 `next()` 函数实现**链式调用**，每个中间件在处理完自己的逻辑后，调用 `next()` 将控制权传递给下一个中间件。如果中间件既不调用 `next()` 也不结束响应，请求将一直挂起。这种设计使得日志、鉴权、业务处理等横切关注点可以独立封装，按需组合。

#### 请求对象（req）和响应对象（res）

| 对象 | 常用属性/方法 | 说明 |
|------|-------------|------|
| `req` | `req.params` | 路由参数（如 `/users/:id`） |
| `req` | `req.query` | URL 查询字符串 |
| `req` | `req.body` | 请求体（需 body-parser 中间件） |
| `req` | `req.headers` | 请求头 |
| `req` | `req.cookies` | Cookie（需 cookie-parser） |
| `res` | `res.send()` | 发送任意类型响应 |
| `res` | `res.json()` | 发送 JSON 响应 |
| `res` | `res.status()` | 设置 HTTP 状态码 |
| `res` | `res.redirect()` | 重定向 |
| `res` | `res.sendFile()` | 发送文件 |

```javascript
// 路由参数示例
app.get('/users/:id', (req, res) => {
  const userId = req.params.id;
  const filter = req.query.status; // /users/123?status=active
  res.json({ id: userId, status: filter });
});

// 请求体解析（Express 4.16+ 内置）
app.use(express.json());       // 解析 application/json
app.use(express.urlencoded({ extended: true })); // 解析 application/x-www-form-urlencoded
```

> 📖 **参考链接**：
> - [Express 5 迁移指南](https://expressjs.com/en/guide/migrating-5.html)
> - [Express 官方网站](https://expressjs.com/)

### 2.2 Koa 框架

Koa 是由 Express 原班人马打造的"下一代" Web 框架。与 Express 相比，Koa 更加轻量、现代化。

#### Koa vs Express 对比

| 对比维度 | Express | Koa |
|---------|---------|-----|
| 内核大小 | 较大，内置路由、静态文件等 | 极小，核心只有约 2000 行代码 |
| 中间件模型 | 线性执行，通过 `next()` 串联 | 洋葱模型（onion model），基于 `async/await` |
| 错误处理 | 需要专门的错误处理中间件（4 参数） | 使用 `try/catch` 统一捕获 |
| 请求/响应 | 独立的 `req` 和 `res` 对象 | 统一的 `ctx` 上下文对象 |
| 响应方式 | `res.send()` / `res.json()` | `ctx.body = ...` 直接赋值 |
| 异步支持 | 基于回调，需手动处理 Promise | 原生支持 `async/await` |
| 中间件扩展 | 内置 `express.static` 等 | 全部通过第三方插件实现 |
| 适用场景 | 快速开发、传统项目 | 需要精细控制、现代项目 |

#### Koa 基础用法

```javascript
const Koa = require('koa');
const app = new Koa();

// 中间件基于 async/await
app.use(async (ctx, next) => {
  const start = Date.now();
  await next(); // 等待下游中间件执行完毕
  const ms = Date.now() - start;
  console.log(`${ctx.method} ${ctx.url} - ${ms}ms`);
});

// ctx 上下文对象统一 req/res
app.use(async (ctx) => {
  ctx.body = { message: 'Hello Koa' };
  ctx.status = 200;
  ctx.set('X-Custom-Header', 'Koa');
});

app.listen(3000);
```

> 📖 **参考链接**：
> - [Koa 官方网站](https://koajs.com/)
> - [Express 官方文档 - 使用中间件](https://expressjs.com/en/guide/using-middleware.html)

### 2.3 Fastify 框架

Fastify 是 Node.js 生态中性能最高的 Web 框架之一，由 Matteo Collina 和 Tomas Della Vedova 创建，专注于**低开销、高性能**的请求处理。

#### 核心特点

| 特点 | 说明 |
|---|---|
| **极致性能** | 基准测试中每秒可处理数万请求，性能约为 Express 的 2-3 倍、Koa 的 1.5-2 倍 |
| **Schema 驱动** | 基于 JSON Schema 的请求/响应验证，自动生成序列化代码，减少运行时开销 |
| **插件系统** | 封装性强的插件架构，每个插件有独立的作用域，支持异步加载和依赖管理 |
| **原生 TypeScript** | 完全使用 TypeScript 编写，提供一流的类型推导和泛型支持 |
| **Pino 日志** | 默认集成 Pino 高性能日志库，JSON 格式输出，适合生产环境日志采集 |
| **生命周期钩子** | 丰富的钩子（onRequest、preHandler、onSend、onResponse 等），精细控制请求处理流程 |

#### 基础用法

```typescript
// 安装：pnpm add fastify
import Fastify from 'fastify';

// 创建 Fastify 实例
const fastify = Fastify({
  logger: true, // 内置 Pino 日志，生产环境建议开启
});

// 定义 JSON Schema 验证规则
const userSchema = {
  body: {
    type: 'object',
    required: ['name', 'email'],
    properties: {
      name: { type: 'string', minLength: 2 },
      email: { type: 'string', format: 'email' },
    },
  },
  response: {
    200: {
      type: 'object',
      properties: {
        id: { type: 'number' },
        name: { type: 'string' },
        email: { type: 'string' },
        createdAt: { type: 'string' },
      },
    },
  },
};

// 路由定义（带 Schema 验证，自动序列化）
fastify.post('/api/users', { schema: userSchema }, async (request, reply) => {
  const { name, email } = request.body;
  // 业务逻辑...
  const user = { id: 1, name, email, createdAt: new Date().toISOString() };
  // Fastify 根据 schema 自动序列化响应，无需手动 JSON.stringify
  return user;
});

// 路由参数 + 查询参数
fastify.get('/api/users/:id', async (request, reply) => {
  const { id } = request.params;      // 类型安全的参数提取
  const { fields } = request.query;    // 查询参数
  return { id, fields };
});

// 生命周期钩子
fastify.addHook('onRequest', async (request, reply) => {
  // 请求到达时执行（如鉴权）
  request.log.info({ url: request.url }, 'incoming request');
});

fastify.addHook('preHandler', async (request, reply) => {
  // 路由匹配后、handler 执行前（如权限校验）
});

fastify.addHook('onSend', async (request, reply, payload) => {
  // 响应发送前（如添加响应头、包装响应体）
  return payload;
});

// 插件注册
fastify.register(import('@fastify/cors'), {
  origin: 'https://example.com',
});

// 错误处理
fastify.setErrorHandler((error, request, reply) => {
  request.log.error(error);
  reply.status(error.statusCode || 500).send({
    error: error.message,
    statusCode: error.statusCode || 500,
  });
});

// 启动服务
fastify.listen({ port: 3000 }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  console.log(`Server running at ${address}`);
});
```

#### Express / Koa / Fastify 三者核心差异对比

| 对比维度 | Express | Koa | Fastify |
|---|---|---|---|
| **设计哲学** | 功能完备、开箱即用 | 极简内核、按需扩展 | Schema 驱动、性能优先 |
| **核心体积** | 约 20KB（含路由、静态文件等） | 约 2KB（仅核心） | 约 30KB（含 Schema 验证、序列化等） |
| **中间件模型** | 回调函数串联（`(req, res, next) => {}`） | async/await 洋葱模型（`async (ctx, next) => {}`） | async/await + 生命周期钩子链 |
| **请求/响应对象** | 独立的 `req` / `res`（Node.js 原生增强） | 统一的 `ctx` 上下文对象 | 分离的 `request` / `reply`（封装层） |
| **错误处理** | 需四参数中间件 `(err, req, res, next)` | `try/catch` 或 `ctx.onerror` | 集中式 `setErrorHandler` |
| **Schema 验证** | 需第三方库（如 Joi、Zod） | 需第三方库 | 内置 JSON Schema 验证 |
| **序列化性能** | `JSON.stringify`（通用，无优化） | `JSON.stringify`（通用，无优化） | Schema 驱动的快速序列化（`fast-json-stringify`） |
| **TypeScript 支持** | 需额外安装 `@types/express` | 需额外安装 `@types/koa` | 原生 TypeScript，类型推导完善 |
| **生态成熟度** | 最成熟，中间件数量最多（10,000+） | 成熟，中间件丰富（2,000+） | 快速成长，插件生态完善（500+） |
| **学习曲线** | 低（入门简单，概念直观） | 中（需理解洋葱模型和 async/await） | 中（需理解 Schema 和插件系统） |
| **基准性能（req/s）** | ~15,000 | ~25,000 | ~45,000+ |
| **适用场景** | 快速原型、小型项目、传统 REST API | 需要精细控制中间件执行顺序的项目 | 高并发 API 网关、微服务、性能敏感型应用 |

**性能基准说明**：以上数据为近似参考值，实际性能受硬件、网络、业务逻辑复杂度等因素影响。Fastify 的性能优势主要来源于：
1. **Schema 驱动的快速序列化**：`fast-json-stringify` 根据 JSON Schema 预编译序列化函数，比通用 `JSON.stringify` 快 2-3 倍
2. **优化的路由匹配**：使用 `find-my-way` 路由库，基于 Radix Tree 实现高效路由查找
3. **最小化对象分配**：减少请求处理过程中的对象创建和 GC 压力

#### 适用场景推荐

| 场景 | 推荐框架 | 理由 |
|---|---|---|
| 快速原型验证、小型内部工具 | Express | 学习成本最低，开箱即用 |
| 中大型项目，需要精细控制中间件流程 | Koa | 洋葱模型灵活，中间件组合能力强 |
| 高并发 API 服务、微服务网关 | Fastify | 性能最优，Schema 验证天然适合 API 场景 |
| 团队以 TypeScript 为主 | Fastify | 原生 TS 支持，类型安全 |
| 需要大量社区中间件支持 | Express | 生态最成熟，中间件选择最多 |
| 需要请求/响应自动校验 | Fastify | 内置 JSON Schema，无需额外依赖 |
| 需要自定义框架（如企业级框架封装） | Koa | 极简内核，可按需扩展 |

> 📖 **参考链接**：
> - [Fastify 官方网站](https://fastify.dev/)
> - [Express 官方文档 - 使用中间件](https://expressjs.com/en/guide/using-middleware.html)

### 2.4 洋葱模型（Onion Model）

洋葱模型是 Koa 中间件的核心执行模型，也是 Koa 区别于 Express 的最大特点。

#### 执行流程

```
请求进入
    │
    ▼
┌──────────────────────────────┐
│    中间件 1（前半部分）         │
│  ┌────────────────────────┐  │
│  │  中间件 2（前半部分）     │  │
│  │ ┌──────────────────┐   │  │
│  │ │    中间件 3       │   │  │
│  │ │  （核心业务逻辑）   │   │  │
│  │ └──────────────────┘   │  │
│  │  中间件 2（后半部分）     │  │
│  └────────────────────────┘  │
│    中间件 1（后半部分）         │
└──────────────────────────────┘
    │
    ▼
  响应返回
```

具体执行顺序：**请求进入 → 中间件1 前半 → 中间件2 前半 → 中间件3（核心业务）→ 中间件2 后半 → 中间件1 后半 → 响应返回**

#### compose 函数实现原理

Koa 的洋葱模型核心是 `koa-compose` 函数，它将多个中间件组合成一个：

```javascript
function compose(middlewares) {
  return function (ctx) {
    let index = -1;

    function dispatch(i) {
      if (i <= index) {
        // 防止 next() 被多次调用
        return Promise.reject(new Error('next() called multiple times'));
      }
      index = i;

      const fn = middlewares[i];
      if (!fn) return Promise.resolve(); // 所有中间件执行完毕

      try {
        // 执行当前中间件，传入 ctx 和下一个 dispatch
        return Promise.resolve(fn(ctx, () => dispatch(i + 1)));
      } catch (err) {
        return Promise.reject(err);
      }
    }

    return dispatch(0);
  };
}
```

**关键点**：`dispatch(i + 1)` 作为 `next` 参数传入中间件，中间件调用 `await next()` 时，会触发下一个中间件的执行。当后面的中间件全部执行完毕后，执行权回溯到当前中间件，继续执行 `next()` 之后的代码。

#### 洋葱模型的应用场景

```javascript
// 1. 请求计时中间件
app.use(async (ctx, next) => {
  const start = Date.now();
  await next(); // 等待所有下游中间件执行完毕
  ctx.set('X-Response-Time', `${Date.now() - start}ms`);
});

// 2. 响应体包装中间件
app.use(async (ctx, next) => {
  await next();
  // 在响应返回前统一包装数据格式
  if (ctx.body && ctx.status === 200) {
    ctx.body = {
      code: 0,
      data: ctx.body,
      message: 'success',
    };
  }
});

// 3. 错误统一捕获中间件
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = { code: -1, message: err.message };
    // 触发 error 事件，可由 app.on('error') 监听
    ctx.app.emit('error', err, ctx);
  }
});
```

> 📖 **参考链接**：
> - [Express 官方文档 - 使用中间件](https://expressjs.com/en/guide/using-middleware.html)
> - [Koa 官方文档 - Middleware](https://koajs.com/#middleware)

### 2.5 常用中间件

Koa 本身不绑定任何中间件，需要通过第三方插件扩展功能：

| 中间件 | 功能 | 安装 |
|--------|------|------|
| `koa-router` | 路由定义 | `pnpm add koa-router` |
| `koa-body` | 请求体解析（支持文件上传） | `pnpm add koa-body` |
| `koa-static` | 静态文件服务 | `pnpm add koa-static` |
| `@koa/cors` | 跨域资源共享 | `pnpm add @koa/cors` |
| `koa-jwt` | JWT 认证 | `pnpm add koa-jwt` |
| `koa-helmet` | 安全 HTTP 头 | `pnpm add koa-helmet` |
| `koa-logger` | 请求日志 | `pnpm add koa-logger` |

```javascript
const Koa = require('koa');
const Router = require('koa-router');
const koaBody = require('koa-body');
const cors = require('@koa/cors');
const jwt = require('koa-jwt');
const helmet = require('koa-helmet');
const serve = require('koa-static');

const app = new Koa();
const router = new Router();

// 安全头
app.use(helmet());

// 跨域
app.use(cors({ origin: 'https://example.com', credentials: true }));

// 请求体解析
app.use(koaBody({ multipart: true }));

// 静态文件
app.use(serve('./public'));

// 公开路由（无需认证）
router.get('/public', (ctx) => { ctx.body = 'public data'; });

// JWT 认证中间件（保护后续路由）
app.use(jwt({ secret: 'your-secret-key' }).unless({ path: [/^\/public/] }));

// 受保护路由
router.get('/protected', (ctx) => {
  ctx.body = { user: ctx.state.user };
});

app.use(router.routes());
app.use(router.allowedMethods());
```

### 2.6 Session 与 Cookie

#### Cookie 基础

Cookie 是服务端通过 `Set-Cookie` 响应头在客户端存储的小型数据（最大 4KB）：

```javascript
// Express 设置 Cookie
res.cookie('username', 'john', {
  maxAge: 900000,           // 过期时间（毫秒）
  httpOnly: true,           // 禁止 JavaScript 访问（防 XSS）
  secure: true,             // 仅 HTTPS 传输
  sameSite: 'strict',       // 防 CSRF：strict / lax / none
  domain: '.example.com',   // 作用域
  path: '/',                // 路径
});
```

#### Cookie 属性详解

| 属性 | 说明 | 安全建议 |
|------|------|---------|
| `HttpOnly` | 禁止 JavaScript 通过 `document.cookie` 访问 | 始终设置为 `true`（防 XSS） |
| `Secure` | 仅在 HTTPS 连接中传输 | 生产环境始终设置为 `true` |
| `SameSite` | 控制跨站请求是否携带 Cookie | `Strict`（最安全）或 `Lax`（常用） |
| `Domain` | 指定 Cookie 生效的域名 | 尽量不使用，默认仅当前域名 |
| `Path` | 指定 Cookie 生效的路径 | 默认 `/`，按需限制 |
| `Max-Age` | Cookie 有效期（秒） | 区分会话 Cookie 和持久 Cookie |

#### Session 鉴权流程

Session 是服务端存储的用户会话数据，客户端只保存一个 Session ID（通常通过 Cookie 传递）：

```
1. 用户登录 → 服务端验证凭证
2. 服务端创建 Session，存储用户信息（内存 / Redis）
3. 服务端将 Session ID 通过 Set-Cookie 返回客户端
4. 客户端后续请求自动携带 Cookie（含 Session ID）
5. 服务端根据 Session ID 查找用户信息
6. 用户登出 → 服务端销毁 Session
```

```javascript
// Express + express-session 实现 Session
const session = require('express-session');
const RedisStore = require('connect-redis').default;

app.use(session({
  store: new RedisStore({ client: redisClient }), // 生产环境用 Redis 存储
  secret: 'your-secret',
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 24 * 60 * 60 * 1000, // 24 小时
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  },
}));

// 登录
app.post('/login', (req, res) => {
  // 验证用户名密码...
  req.session.user = { id: 1, username: 'john' };
  res.json({ message: '登录成功' });
});

// 获取当前用户
app.get('/me', (req, res) => {
  if (!req.session.user) return res.status(401).json({ error: '未登录' });
  res.json({ user: req.session.user });
});

// 登出
app.post('/logout', (req, res) => {
  req.session.destroy();
  res.json({ message: '已登出' });
});
```

### 2.7 JWT 认证

JWT（JSON Web Token）是一种无状态的认证方案，服务端不需要存储 Session 数据。

#### JWT 结构

```
header.payload.signature
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjF9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

- **Header**：包含算法类型（如 HS256）和 token 类型
- **Payload**：包含声明数据（用户 ID、过期时间等）
- **Signature**：对前两部分的签名，用于验证 token 未被篡改

#### Token 生成与验证

```javascript
const jwt = require('jsonwebtoken');

const SECRET = 'your-secret-key';

// 生成 Token
function generateToken(user) {
  return jwt.sign(
    { userId: user.id, role: user.role },
    SECRET,
    { expiresIn: '15m' } // 短期有效
  );
}

// 生成 Refresh Token
function generateRefreshToken(user) {
  return jwt.sign(
    { userId: user.id, type: 'refresh' },
    SECRET,
    { expiresIn: '7d' } // 长期有效
  );
}

// 验证 Token
function verifyToken(token) {
  return jwt.verify(token, SECRET);
}

// 使用示例
app.post('/login', async (req, res) => {
  const user = await validateUser(req.body.username, req.body.password);
  if (!user) return res.status(401).json({ error: '用户名或密码错误' });

  const accessToken = generateToken(user);
  const refreshToken = generateRefreshToken(user);

  res.json({ accessToken, refreshToken });
});

app.get('/profile', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  try {
    const decoded = verifyToken(token);
    res.json({ userId: decoded.userId });
  } catch (err) {
    res.status(401).json({ error: 'Token 无效或已过期' });
  }
});
```

#### 双 Token 刷新机制

Access Token 短期有效（15 分钟），Refresh Token 长期有效（7 天）。当 Access Token 过期时，客户端使用 Refresh Token 换取新的 Access Token：

```javascript
// Token 刷新端点
app.post('/refresh', (req, res) => {
  const { refreshToken } = req.body;

  try {
    const decoded = jwt.verify(refreshToken, SECRET);
    if (decoded.type !== 'refresh') {
      return res.status(401).json({ error: '无效的 Refresh Token' });
    }

    // 生成新的 Access Token
    const newAccessToken = jwt.sign(
      { userId: decoded.userId, role: decoded.role },
      SECRET,
      { expiresIn: '15m' }
    );

    res.json({ accessToken: newAccessToken });
  } catch (err) {
    res.status(401).json({ error: 'Refresh Token 已过期，请重新登录' });
  }
});
```

### 2.8 BFF（Backend For Frontend）设计模式

#### 什么是 BFF

BFF 是为前端定制的后端服务层，位于前端应用和后端微服务之间。它是前端团队自主开发和维护的 Node.js 服务，负责：

- **数据聚合**：将多个微服务接口的数据合并为前端需要的数据结构
- **数据裁剪**：去除前端不需要的字段，减少传输量
- **接口适配**：为不同客户端（Web、Mobile、Desktop）提供定制化的 API
- **协议转换**：将 gRPC、SOAP 等协议转换为 REST 或 GraphQL

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Web App  │  │  iOS App  │  │ Android  │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  BFF-Web  │  │ BFF-iOS  │  │BFF-Android│
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │
      └──────────────┼──────────────┘
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ 用户服务  │  │ 订单服务  │  │ 商品服务  │
└──────────┘  └──────────┘  └──────────┘
```

#### BFF 解决的问题

| 问题 | 传统方案 | BFF 方案 |
|------|---------|---------|
| 数据聚合 | 前端发起多个请求，自行拼装数据 | BFF 层一次请求完成聚合，减少网络开销 |
| 数据冗余 | 微服务返回完整数据，前端自行过滤 | BFF 层裁剪数据，只返回前端需要的字段 |
| 接口差异 | 不同客户端使用同一套 API，字段冗余 | 为每个客户端定制专属 BFF |
| 版本管理 | API 版本升级影响所有客户端 | BFF 层隔离变化，后端升级不影响前端 |
| 协议适配 | 前端直接对接不同协议的服务 | BFF 层统一转换为 RESTful API |

#### BFF 实现示例

```javascript
// BFF 层聚合用户信息和订单列表
const Koa = require('koa');
const Router = require('koa-router');
const axios = require('axios');

const app = new Koa();
const router = new Router();

// 用户服务 API 地址
const USER_SERVICE = 'http://user-service:3001';
// 订单服务 API 地址
const ORDER_SERVICE = 'http://order-service:3002';

router.get('/api/dashboard', async (ctx) => {
  const userId = ctx.state.user.id;

  // 并行请求两个微服务
  const [userRes, ordersRes] = await Promise.all([
    axios.get(`${USER_SERVICE}/users/${userId}`),
    axios.get(`${ORDER_SERVICE}/orders?userId=${userId}`),
  ]);

  // 聚合 + 裁剪数据
  ctx.body = {
    user: {
      name: userRes.data.name,
      avatar: userRes.data.avatar,
      level: userRes.data.level,
      // 不返回敏感字段如 phone、email
    },
    orders: ordersRes.data.items.map(order => ({
      id: order.id,
      total: order.total,
      status: order.status,
      createdAt: order.createdAt,
      // 只返回前端需要的字段
    })),
    summary: {
      totalOrders: ordersRes.data.total,
      totalSpent: ordersRes.data.items.reduce((sum, o) => sum + o.total, 0),
    },
  };
});

app.use(router.routes());
```

#### GraphQL 作为 BFF 的替代方案

GraphQL 天然适合作为 BFF 层，它允许前端精确描述所需数据，服务端一次返回：

```javascript
// GraphQL Schema 定义
const typeDefs = `
  type User {
    id: ID!
    name: String!
    orders: [Order!]!
  }

  type Order {
    id: ID!
    total: Float!
    status: String!
  }

  type Query {
    dashboard: User!
  }
`;

// Resolver：聚合多个数据源
const resolvers = {
  Query: {
    dashboard: async (_, __, { userId }) => {
      const user = await userService.getUser(userId);
      return user;
    },
  },
  User: {
    orders: async (user) => {
      const orders = await orderService.getOrdersByUser(user.id);
      return orders;
    },
  },
};
```

> 📖 **参考链接**：
> - [Sam Newman - BFF 模式](https://samnewman.io/patterns/architectural/bff/)
> - [ThoughtWorks - BFF @ SoundCloud](https://www.thoughtworks.com/insights/blog/bff-soundcloud)

### 2.9 进程管理

#### PM2 进程守护

PM2 是 Node.js 生产环境最常用的进程管理工具：

```bash
# 安装
pnpm add -g pm2

# 启动应用（cluster 模式，充分利用多核 CPU）
pm2 start app.js -i max

# 查看状态
pm2 list

# 查看日志
pm2 logs

# 监控
pm2 monit

# 保存进程列表（开机自启）
pm2 save
pm2 startup

# 零停机重载
pm2 reload app
```

#### PM2 配置文件

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'my-app',
    script: './app.js',
    instances: 'max',          // 使用所有 CPU 核心
    exec_mode: 'cluster',
    watch: false,              // 生产环境关闭文件监听
    max_memory_restart: '1G',  // 内存超过 1G 自动重启
    env: {
      NODE_ENV: 'production',
      PORT: 3000,
    },
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    error_file: './logs/err.log',
    out_file: './logs/out.log',
  }],
};
```

#### Node.js cluster 模块

```javascript
const cluster = require('cluster');
const http = require('http');
const numCPUs = require('os').cpus().length;

if (cluster.isPrimary) {
  console.log(`主进程 ${process.pid} 正在运行`);

  // Fork 工作进程
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  // 监听工作进程退出，自动重启
  cluster.on('exit', (worker, code, signal) => {
    console.log(`工作进程 ${worker.process.pid} 已退出`);
    cluster.fork(); // 自动重启
  });
} else {
  // 工作进程共享 TCP 连接
  http.createServer((req, res) => {
    res.writeHead(200);
    res.end(`Hello from worker ${process.pid}\n`);
  }).listen(8000);

  console.log(`工作进程 ${process.pid} 已启动`);
}
```

---

## 三、实战应用

### 3.1 完整的 Koa 项目结构

```
project/
├── app.js              # 入口文件
├── middleware/
│   ├── error.js        # 错误处理
│   ├── logger.js       # 日志
│   └── auth.js         # 认证
├── router/
│   ├── index.js        # 路由聚合
│   ├── user.js         # 用户路由
│   └── order.js        # 订单路由
├── controller/
│   ├── user.js         # 用户控制器
│   └── order.js        # 订单控制器
├── service/
│   ├── user.js         # 用户服务层
│   └── order.js        # 订单服务层
└── config/
    └── index.js        # 配置文件
```

### 3.2 统一错误处理中间件

```javascript
// middleware/error.js
module.exports = async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    // 区分已知错误和未知错误
    const status = err.status || 500;
    const message = status === 500 ? '服务器内部错误' : err.message;

    ctx.status = status;
    ctx.body = {
      code: status,
      message,
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
    };

    // 记录错误日志
    console.error(`[${new Date().toISOString()}] ${ctx.method} ${ctx.url} - ${err.message}`);
  }
};
```

---

## 四、常见面试题

**Q1：Express 和 Koa 的核心区别是什么？**

Express 是功能完备的框架，内置路由、静态文件等，中间件基于回调串联。Koa 是极简内核，核心只有约 2000 行代码，中间件基于 async/await 洋葱模型，使用统一的 ctx 上下文对象，错误处理更简洁。选择 Express 适合快速开发，选择 Koa 适合需要精细控制的现代项目。

**Q2：什么是洋葱模型？**

洋葱模型是 Koa 中间件的执行模型。请求像"剥洋葱"一样逐层进入中间件，到达核心业务逻辑后，再逐层"穿出"。每个中间件在 `await next()` 之前执行的代码是"进入"，之后执行的代码是"穿出"。这使得中间件可以在请求处理前后都执行逻辑，非常适合日志记录、响应包装、错误处理等场景。

**Q3：Session 和 JWT 的区别？**

- Session：服务端存储，客户端只存 Session ID。优势是服务端可主动失效、敏感信息不暴露；劣势是服务端需要存储、分布式需要共享存储。
- JWT：无状态，客户端存储完整 Token。优势是服务端无需存储、天然支持分布式；劣势是 Token 无法主动失效（除非使用黑名单）、Payload 仅 Base64 编码（非加密）。

**Q4：为什么需要双 Token 模式？**

Access Token 短期有效（如 15 分钟），即使被窃取，影响时间有限。Refresh Token 长期有效（如 7 天），仅用于刷新 Access Token，不频繁传输。两者配合既保证了安全性，又避免了用户频繁登录。

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 中间件不调用 `next()` 也不结束响应 | 请求挂起直到超时 | 中间件链条中断，响应永远不会被发送 | 检查每个中间件是否正确调用 `next()` 或 `res.send()` |
| 在 Koa 中混用回调风格的中间件 | 洋葱模型断裂，执行顺序不可预期 | Koa 中间件必须返回 Promise，回调风格无法被 `await` | 将回调风格中间件包装为 Promise，或使用 `util.promisify` |
| 生产环境使用内存存储 Session | 服务重启后所有用户重新登录 | 内存存储不持久化，且多进程间不共享 | 使用 `connect-redis` 等持久化存储 |
| JWT Secret 硬编码在代码中 | 密钥泄露导致 Token 可被伪造 | 密钥暴露在代码仓库中 | 使用环境变量或配置中心管理密钥 |
| 忘记设置 Cookie 的 `httpOnly` | XSS 攻击可窃取 Cookie | JavaScript 可通过 `document.cookie` 读取 Cookie | 始终设置 `httpOnly: true` |
| BFF 层串行请求多个微服务 | 接口响应慢，用户体验差 | 串行请求延长了总体响应时间 | 使用 `Promise.all` 并行请求，无依赖关系的接口必须并行 |
| `ctx.body` 在 `await next()` 之后赋值导致不生效 | 响应已发送，后续修改无效 | 响应一旦发送，HTTP 连接就可能关闭 | 响应体数据在 `await next()` 之前准备好，或在 `next()` 之后利用流式响应 |
| 未设置 `SameSite` 属性 | 可能遭受 CSRF 攻击 | 跨站请求默认携带 Cookie | 设置 `sameSite: 'strict'` 或 `sameSite: 'lax'` |

---

> **学习导航**：
> - 返回 [学习路线总览](../README.md)
> - 本模块其他文件：[01-Node运行时与核心API](./01-Node运行时与核心API.md) | [03-Node.js笔面试题集](./03-Node.js笔面试题集.md) | [04-数据库与ORM](./04-数据库与ORM.md)
> - 进阶学习：[企业后台管理系统](../10-project/01-企业后台管理系统实战.md)

---

## 本章学习自检

- [ ] 能够对比 Express 和 Koa 的核心差异（中间件模型、错误处理、上下文对象）
- [ ] 理解洋葱模型的执行流程，能够画出中间件执行顺序图
- [ ] 能够实现 `compose` 函数的核心逻辑
- [ ] 掌握常用 Koa 中间件的用途和配置方式
- [ ] 理解 Cookie 各属性的安全含义（HttpOnly、Secure、SameSite）
- [ ] 能够实现 Session 鉴权和 JWT 鉴权两种方案
- [ ] 理解双 Token 刷新机制的设计原理
- [ ] 能够阐述 BFF 设计模式解决的核心问题
- [ ] 能够使用 PM2 或 cluster 模块实现多进程部署
- [ ] 能够设计一个聚合多个微服务的 BFF 接口

---

## 补充：API 文档与 SSE

### 1. API 文档（Swagger / OpenAPI）

#### 1.1 OpenAPI 规范概述

Swagger 是目前最流行的 API 文档工具链，其核心规范已捐赠给 Linux 基金会并更名为 **OpenAPI** 规范（当前主流版本为 OpenAPI 3.0/3.1）。OpenAPI 规范使用 JSON 或 YAML 格式描述 RESTful API 的全部信息，包括端点、参数、请求/响应结构、认证方式等。

**规范核心结构**：

```yaml
openapi: "3.0.0"
info:
  title: 用户管理 API
  version: 1.0.0
  description: 用户增删改查接口文档

servers:
  - url: http://localhost:3000/api
    description: 本地开发环境

# 组件定义：可复用的数据模型
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
      required:
        - name
        - email
    Error:
      type: object
      properties:
        code:
          type: integer
        message:
          type: string

  # 安全方案定义
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

# 路径定义：所有 API 端点
paths:
  /users:
    get:
      summary: 获取用户列表
      tags:
        - 用户管理
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
    post:
      summary: 创建用户
      tags:
        - 用户管理
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      responses:
        '201':
          description: 创建成功
        '400':
          description: 参数错误
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /users/{id}:
    get:
      summary: 获取单个用户
      tags:
        - 用户管理
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: 用户不存在
```

**关键概念说明**：

| 概念 | 说明 |
|------|------|
| `openapi` | 声明使用的 OpenAPI 规范版本 |
| `info` | API 基本元信息（标题、版本、描述） |
| `servers` | API 服务器地址列表（支持多环境） |
| `components/schemas` | 可复用的数据模型定义，通过 `$ref` 引用 |
| `paths` | 所有 API 端点定义，每个端点包含 HTTP 方法、参数、请求体、响应 |
| `securitySchemes` | 认证方案定义（Bearer Token、API Key、OAuth2 等） |
| `tags` | API 分组标签，用于文档界面中的分类展示 |

#### 1.2 自动化文档生成（swagger-jsdoc + swagger-ui-express）

在 Express 项目中，可以通过 **swagger-jsdoc**（从 JSDoc 注释生成 OpenAPI 规范）和 **swagger-ui-express**（提供可视化文档界面）实现自动化 API 文档。

**安装依赖**：

```bash
pnpm add swagger-jsdoc swagger-ui-express
```

**完整配置示例**：

```javascript
// app.js
const express = require('express');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const app = express();
app.use(express.json());

// ========== Swagger 配置 ==========

const swaggerDefinition = {
  openapi: '3.0.0',
  info: {
    title: '用户管理 API 文档',
    version: '1.0.0',
    description: '基于 Express 的用户增删改查接口，支持 JWT 认证',
  },
  servers: [
    {
      url: 'http://localhost:3000',
      description: '本地开发环境',
    },
  ],
  components: {
    securitySchemes: {
      bearerAuth: {
        type: 'http',
        scheme: 'bearer',
        bearerFormat: 'JWT',
        description: '请输入 JWT Token，格式：Bearer <token>',
      },
    },
  },
};

const options = {
  swaggerDefinition,
  // 扫描指定目录下的所有 JS 文件，提取 JSDoc 注释中的 OpenAPI 定义
  apis: ['./routes/*.js'],
};

const swaggerSpec = swaggerJsdoc(options);

// 挂载 Swagger UI 文档页面（访问 /api-docs 查看）
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
  customCss: '.swagger-ui .topbar { display: none }',
}));

// 可选：提供原始 JSON 规范文件
app.get('/api-docs.json', (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.send(swaggerSpec);
});

// ========== 路由定义（带 JSDoc 注释） ==========

/**
 * @swagger
 * /users:
 *   get:
 *     summary: 获取用户列表
 *     tags: [用户管理]
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: 页码
 *       - in: query
 *         name: pageSize
 *         schema:
 *           type: integer
 *           default: 10
 *         description: 每页数量
 *     responses:
 *       200:
 *         description: 成功返回用户列表
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 code:
 *                   type: integer
 *                   example: 0
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/User'
 *                 total:
 *                   type: integer
 */
app.get('/users', (req, res) => {
  const { page = 1, pageSize = 10 } = req.query;
  // 业务逻辑...
  res.json({ code: 0, data: [{ id: 1, name: '张三', email: 'zhangsan@example.com' }], total: 1 });
});

/**
 * @swagger
 * components:
 *   schemas:
 *     User:
 *       type: object
 *       required:
 *         - name
 *         - email
 *       properties:
 *         id:
 *           type: integer
 *           description: 用户 ID
 *         name:
 *           type: string
 *           description: 用户名
 *         email:
 *           type: string
 *           format: email
 *           description: 邮箱地址
 */

/**
 * @swagger
 * /users:
 *   post:
 *     summary: 创建用户
 *     tags: [用户管理]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/User'
 *     responses:
 *       201:
 *         description: 创建成功
 *       400:
 *         description: 参数校验失败
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 code:
 *                   type: integer
 *                   example: 400
 *                 message:
 *                   type: string
 *                   example: "用户名不能为空"
 *       401:
 *         description: 未授权（Token 无效或缺失）
 */
app.post('/users', (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) {
    return res.status(400).json({ code: 400, message: '用户名和邮箱不能为空' });
  }
  // 创建用户逻辑...
  res.status(201).json({ code: 0, data: { id: Date.now(), name, email } });
});

/**
 * @swagger
 * /users/{id}:
 *   get:
 *     summary: 获取单个用户
 *     tags: [用户管理]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *         description: 用户 ID
 *     responses:
 *       200:
 *         description: 成功
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/User'
 *       404:
 *         description: 用户不存在
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 code:
 *                   type: integer
 *                   example: 404
 *                 message:
 *                   type: string
 *                   example: "用户不存在"
 */
app.get('/users/:id', (req, res) => {
  const { id } = req.params;
  // 查询用户逻辑...
  res.json({ id: Number(id), name: '张三', email: 'zhangsan@example.com' });
});

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
  console.log('API 文档: http://localhost:3000/api-docs');
});
```

#### 1.3 API 文档最佳实践

| 最佳实践 | 说明 |
|---------|------|
| **请求/响应示例** | 每个接口都应提供 `example` 字段，展示真实的请求和响应数据格式 |
| **错误码说明** | 明确列出所有可能的 HTTP 状态码（200/201/400/401/403/404/500）及其含义 |
| **认证方式标注** | 使用 `security` 字段标注接口是否需要认证，并在 `components/securitySchemes` 中定义认证方案 |
| **数据模型复用** | 将通用的数据模型定义在 `components/schemas` 中，通过 `$ref` 引用，避免重复定义 |
| **分组标签** | 使用 `tags` 对接口进行逻辑分组（如"用户管理"、"订单管理"），提升文档可读性 |
| **参数校验说明** | 在参数描述中说明必填/可选、默认值、格式要求、取值范围 |
| **版本管理** | 在 `info.version` 中标注 API 版本，路径中也可包含版本号（如 `/api/v1/users`） |

### 2. SSE（Server-Sent Events）

#### 2.1 SSE 概念

SSE（Server-Sent Events）是一种基于 HTTP 协议的**服务端向客户端单向推送数据**的技术。与 WebSocket 不同，SSE 只支持服务端到客户端的数据流，但实现更简单，且天然支持 HTTP/2 多路复用和自动重连。

**核心特点**：
- 基于标准 HTTP 协议，无需额外握手
- 单向数据流（服务端 → 客户端）
- 客户端通过浏览器内置的 `EventSource` API 接收
- 支持自动重连机制
- 文本格式传输（UTF-8）

#### 2.2 服务端实现

服务端需要设置 `Content-Type: text/event-stream` 响应头，并按照 SSE 消息格式发送数据。

**SSE 消息字段**：

| 字段 | 说明 | 必填 |
|------|------|------|
| `data` | 消息数据体，可以多行，以 `\n\n` 结束一条消息 | 是 |
| `event` | 自定义事件类型，客户端可通过 `addEventListener` 监听 | 否 |
| `id` | 消息 ID，用于断线重连时的 `Last-Event-ID` | 否 |
| `retry` | 重连间隔时间（毫秒），客户端断线后按此时间重试 | 否 |
| `:`（冒号开头） | 注释行，用于心跳保活 | 否 |

**Express SSE 服务端推送完整示例**：

```javascript
const express = require('express');
const app = express();

// 存储所有 SSE 客户端连接
const sseClients = new Set();

// SSE 端点
app.get('/sse/events', (req, res) => {
  // 设置 SSE 必需的响应头
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',           // 禁用缓存
    'Connection': 'keep-alive',            // 保持长连接
    'Access-Control-Allow-Origin': '*',    // 跨域支持
  });

  // 发送连接成功注释（用于确认连接建立）
  res.write(': connected\n\n');

  // 发送初始消息
  res.write(`data: ${JSON.stringify({ type: 'connected', message: 'SSE 连接已建立' })}\n\n`);

  // 将当前连接的 res 对象加入客户端集合
  sseClients.add(res);

  // 定时发送心跳，保持连接活跃
  const heartbeatInterval = setInterval(() => {
    res.write(': heartbeat\n\n'); // 冒号开头为注释，客户端忽略
  }, 30000); // 每 30 秒发送一次心跳

  // 客户端断开连接时清理
  req.on('close', () => {
    clearInterval(heartbeatInterval);
    sseClients.delete(res);
    console.log('客户端已断开连接');
  });
});

// 广播消息给所有 SSE 客户端
function broadcast(event, data) {
  const message = [
    `event: ${event}`,        // 自定义事件类型
    `id: ${Date.now()}`,       // 消息 ID
    `data: ${JSON.stringify(data)}`,
    '\n',                      // 空行表示消息结束
  ].join('\n');

  for (const client of sseClients) {
    client.write(message);
  }
}

// 模拟业务场景：每 5 秒推送一条通知
setInterval(() => {
  const notifications = [
    { type: 'info', title: '系统通知', content: '服务器运行正常', time: new Date().toISOString() },
    { type: 'warning', title: '告警', content: 'CPU 使用率超过 80%', time: new Date().toISOString() },
    { type: 'success', title: '任务完成', content: '数据备份已完成', time: new Date().toISOString() },
  ];
  const notification = notifications[Math.floor(Math.random() * notifications.length)];
  broadcast('notification', notification);
}, 5000);

app.listen(3000, () => console.log('SSE 服务运行在 http://localhost:3000'));
```

#### 2.3 客户端 EventSource API

客户端使用浏览器内置的 `EventSource` 对象连接 SSE 服务，自动处理重连。

```html
<!-- 客户端 HTML 示例 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>SSE 客户端示例</title>
</head>
<body>
  <h1>SSE 消息推送</h1>
  <div id="messages"></div>

  <script>
    const messagesEl = document.getElementById('messages');

    // 创建 EventSource 连接
    const eventSource = new EventSource('http://localhost:3000/sse/events');

    // 连接打开事件
    eventSource.onopen = () => {
      console.log('SSE 连接已建立');
      appendMessage('系统', 'SSE 连接已建立');
    };

    // 监听默认 message 事件（服务端未指定 event 字段时触发）
    eventSource.onmessage = (event) => {
      console.log('收到默认消息:', event.data);
      const data = JSON.parse(event.data);
      appendMessage('默认消息', data.message || event.data);
      console.log('消息 ID:', event.lastEventId); // 获取消息 ID
    };

    // 监听自定义 notification 事件
    eventSource.addEventListener('notification', (event) => {
      const data = JSON.parse(event.data);
      console.log('收到通知:', data);
      appendMessage(data.title, `${data.content} (${data.type})`);
    });

    // 连接错误事件（自动重连时也会触发）
    eventSource.onerror = (event) => {
      console.error('SSE 连接错误:', event);
      // readyState 状态说明：
      // 0 = CONNECTING（正在连接）
      // 1 = OPEN（已连接）
      // 2 = CLOSED（已关闭）
      if (eventSource.readyState === EventSource.CLOSED) {
        appendMessage('系统', '连接已关闭');
      } else {
        appendMessage('系统', '连接错误，正在重连...');
      }
    };

    // 手动关闭连接
    // eventSource.close();

    function appendMessage(title, content) {
      const div = document.createElement('div');
      div.innerHTML = `<strong>[${title}]</strong> ${content} <small>${new Date().toLocaleTimeString()}</small>`;
      messagesEl.appendChild(div);
    }
  </script>
</body>
</html>
```

**EventSource 自动重连机制**：当连接断开时，浏览器会自动尝试重新连接。服务端可通过 `retry` 字段指定重连间隔（默认约 3 秒），客户端可通过 `Last-Event-ID` 请求头告知服务端最后收到的消息 ID，实现断点续传。

#### 2.4 SSE 与 WebSocket 对比

| 对比维度 | SSE | WebSocket |
|---------|-----|-----------|
| **通信方向** | 单向（服务端 → 客户端） | 双向（全双工） |
| **协议** | HTTP/HTTPS（标准 HTTP 协议） | ws:// / wss://（独立协议，需升级握手） |
| **自动重连** | 浏览器内置自动重连，支持 `Last-Event-ID` 断点续传 | 需手动实现重连逻辑 |
| **二进制支持** | 仅支持文本（UTF-8），二进制数据需 Base64 编码 | 原生支持文本和二进制帧 |
| **浏览器支持** | 所有现代浏览器均支持（IE 除外） | 所有现代浏览器均支持 |
| **HTTP/2 多路复用** | 天然支持，可在一个 HTTP/2 连接上建立多个 SSE 流 | 独立连接，每个 WebSocket 占用一个连接 |
| **防火墙/代理兼容性** | 极好（基于标准 HTTP，无额外端口） | 部分代理/防火墙可能拦截 WebSocket 升级请求 |
| **服务端实现复杂度** | 低（只需设置响应头 + 按格式发送数据） | 中（需要处理握手、帧解析、心跳保活） |
| **适用场景** | 实时通知、股票行情、日志推送、进度更新、社交媒体动态流 | 即时通讯、在线协作编辑、实时游戏、双向 RPC 调用 |

**选型建议**：

- **选择 SSE**：数据推送场景（如通知、仪表盘实时更新、日志流），客户端只需接收数据，无需频繁发送。
- **选择 WebSocket**：需要双向实时通信（如聊天应用、在线游戏、协同编辑），延迟敏感，需要收发二进制数据。

---

## 大模型流式输出前端渲染优化

> AI 大模型（如 ChatGPT、Claude）采用 SSE 流式输出逐字生成内容，前端需要处理增量渲染、性能优化、中断重试和交互体验等复杂场景。

### 2.5 逐字输出的 DOM 增量更新策略

大模型流式输出的核心挑战是：**每收到一个 token 就触发一次 DOM 更新**，如果直接使用 `innerHTML` 或 `textContent` 全量替换，会导致严重的性能问题。

#### 策略一：DOM 片段缓存（推荐）

维护一个文本缓冲区，通过 `requestAnimationFrame` 批量更新 DOM，避免高频重排：

```javascript
// SSE 流式接收 + DOM 片段缓存策略
class StreamingRenderer {
  constructor(container) {
    this.container = container;
    this.buffer = '';          // 文本缓冲区
    this.pending = false;      // 是否有待渲染的更新
    this.rafId = null;         // requestAnimationFrame ID
  }

  // SSE 每收到一块数据就调用
  append(chunk) {
    this.buffer += chunk;
    if (!this.pending) {
      this.pending = true;
      this.rafId = requestAnimationFrame(() => this.flush());
    }
  }

  // 批量刷新到 DOM
  flush() {
    this.container.textContent = this.buffer;
    this.pending = false;
    this.rafId = null;
  }

  destroy() {
    if (this.rafId) cancelAnimationFrame(this.rafId);
  }
}

// 使用示例
const renderer = new StreamingRenderer(document.getElementById('output'));

const eventSource = new EventSource('/api/chat/stream');
eventSource.onmessage = (event) => {
  if (event.data === '[DONE]') {
    renderer.flush(); // 最后刷新一次，确保所有内容渲染
    eventSource.close();
    return;
  }
  const { content } = JSON.parse(event.data);
  renderer.append(content);
};
```

#### 策略二：虚拟滚动（超长文本）

当流式输出内容超过数千行时，全量 DOM 节点会卡顿。使用虚拟滚动只渲染可视区域：

```javascript
// 结合虚拟滚动的流式渲染（简化示意）
// 实际项目中推荐使用 vue-virtual-scroller 或 react-window
class VirtualStreamRenderer {
  constructor(options) {
    this.lineHeight = options.lineHeight || 24;
    this.visibleCount = Math.ceil(options.containerHeight / this.lineHeight) + 2;
    this.bufferLines = []; // 所有行数据
    this.startIndex = 0;
  }

  appendChunk(chunk) {
    // 将 chunk 按换行符拆分为行
    const newLines = chunk.split('\n');
    if (this.bufferLines.length > 0) {
      // 将新数据的第一行拼接到上一行的末尾
      this.bufferLines[this.bufferLines.length - 1] += newLines.shift();
    }
    this.bufferLines.push(...newLines);
    this.renderVisible();
  }

  renderVisible() {
    const visibleLines = this.bufferLines.slice(
      this.startIndex,
      this.startIndex + this.visibleCount
    );
    // 只渲染可见行，容器总高度用 padding 撑开
    this.container.style.paddingTop = `${this.startIndex * this.lineHeight}px`;
    this.container.style.paddingBottom =
      `${(this.bufferLines.length - this.startIndex - this.visibleCount) * this.lineHeight}px`;
    // 渲染 visibleLines...
  }
}
```

### 2.6 流式渲染中的防抖与批量更新

| 优化策略 | 原理 | 适用场景 |
|---------|------|---------|
| `requestAnimationFrame` 批量更新 | 将多次 DOM 更新合并到下一帧渲染前执行 | 高频 token 推送（>30 tokens/s） |
| 标记脏数据 + 异步更新 | 类似 Vue/React 的异步更新队列，合并状态变更 | 框架内的流式渲染 |
| CSS `content-visibility: auto` | 浏览器跳过不可见区域的渲染 | 长文本输出，用户可能只看底部 |
| `will-change: contents` | 提前告知浏览器该元素内容会频繁变化 | 高性能要求的流式场景 |

**React 流式渲染示例**：

```jsx
import { useState, useRef, useCallback, useEffect } from 'react';

function StreamingChat() {
  const [text, setText] = useState('');
  const bufferRef = useRef('');
  const rafRef = useRef(null);

  // 使用 rAF 批量更新 React 状态
  const appendChunk = useCallback((chunk) => {
    bufferRef.current += chunk;
    if (!rafRef.current) {
      rafRef.current = requestAnimationFrame(() => {
        setText(bufferRef.current);
        rafRef.current = null;
      });
    }
  }, []);

  useEffect(() => {
    const es = new EventSource('/api/chat/stream');
    es.onmessage = (e) => {
      if (e.data === '[DONE]') {
        setText(bufferRef.current); // 最终刷新
        es.close();
        return;
      }
      appendChunk(JSON.parse(e.data).content);
    };
    return () => {
      es.close();
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [appendChunk]);

  return <div className="streaming-output">{text}</div>;
}
```

### 2.7 流式输出中断、超时与错误重试

```javascript
class RobustStreamingClient {
  constructor(url, options = {}) {
    this.url = url;
    this.options = {
      timeout: 60000,        // 60 秒超时
      maxRetries: 3,         // 最大重试次数
      retryDelay: 1000,      // 重试延迟（毫秒）
      ...options,
    };
    this.retryCount = 0;
    this.abortController = null;
  }

  async connect(onChunk, onDone, onError) {
    this.abortController = new AbortController();

    // 超时定时器
    const timeoutId = setTimeout(() => {
      this.abortController.abort();
      onError(new Error('请求超时'));
    }, this.options.timeout);

    try {
      const response = await fetch(this.url, {
        headers: { 'Accept': 'text/event-stream' },
        signal: this.abortController.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          onDone();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // 保留不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              onDone();
              return;
            }
            onChunk(JSON.parse(data));
          }
        }
      }
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        // 用户主动取消，不重试
        return;
      }
      // 自动重试
      if (this.retryCount < this.options.maxRetries) {
        this.retryCount++;
        console.warn(`流式输出中断，${this.retryDelay}ms 后重试（${this.retryCount}/${this.options.maxRetries}）`);
        await new Promise(resolve => setTimeout(resolve, this.options.retryDelay * this.retryCount));
        return this.connect(onChunk, onDone, onError);
      }
      onError(err);
    }
  }

  // 主动取消（用户点击停止按钮）
  abort() {
    if (this.abortController) {
      this.abortController.abort();
    }
  }
}
```

**UI 交互状态管理**：

```javascript
// 流式输出 UI 状态机
const StreamingState = {
  IDLE: 'idle',           // 空闲
  CONNECTING: 'connecting', // 正在连接
  STREAMING: 'streaming',   // 正在输出
  PAUSED: 'paused',        // 用户手动暂停（滚动查看历史内容）
  ERROR: 'error',           // 出错
  DONE: 'done',             // 完成
};

// 在组件中根据状态渲染不同 UI：
// - IDLE：显示输入框
// - CONNECTING：显示 loading 动画
// - STREAMING：显示流式文本 + 停止按钮 + 光标闪烁动画
// - PAUSED：显示"正在输出中，点击继续"提示
// - ERROR：显示错误信息 + 重试按钮
// - DONE：显示完整文本 + 复制/重新生成按钮
```

### 2.8 Markdown 流式渲染

大模型输出通常为 Markdown 格式，需要实时渲染为 HTML：

```javascript
import { marked } from 'marked';

class MarkdownStreamRenderer {
  constructor(container) {
    this.container = container;
    this.rawText = '';
    this.lastRenderLength = 0;
  }

  append(chunk) {
    this.rawText += chunk;

    // 增量渲染：只渲染新增部分，避免全量刷新
    // 方案：找到最近一个完整的 Markdown 块边界（如段落结束的空行）
    const renderBoundary = this.findSafeBoundary(this.rawText);

    if (renderBoundary > this.lastRenderLength) {
      const html = marked.parse(this.rawText.slice(0, renderBoundary));
      this.container.innerHTML = html;
      this.lastRenderLength = renderBoundary;
    }
  }

  // 找到安全的渲染边界（段落结束、代码块结束等）
  findSafeBoundary(text) {
    // 查找最后一个完整的双换行（段落结束标记）
    const lastDoubleNewline = text.lastIndexOf('\n\n');
    // 查找最后一个完整的代码块结束标记
    const lastCodeBlockEnd = text.lastIndexOf('\n```\n');

    return Math.max(lastDoubleNewline + 2, lastCodeBlockEnd + 5, 0);
  }

  // 代码高亮延迟加载：流式输出时不立即高亮，等输出完成后再执行
  finalize() {
    const html = marked.parse(this.rawText);
    this.container.innerHTML = html;
    // 流式输出完成后，统一执行代码高亮
    this.container.querySelectorAll('pre code').forEach((block) => {
      hljs.highlightElement(block);
    });
  }
}
```

### 2.9 自动滚动与用户交互

```javascript
class AutoScrollManager {
  constructor(container) {
    this.container = container;
    this.isUserScrolling = false; // 用户是否手动滚动
    this.scrollThreshold = 80;    // 距离底部多少像素内视为"在底部"
  }

  // 判断是否在底部
  isAtBottom() {
    const { scrollTop, scrollHeight, clientHeight } = this.container;
    return scrollHeight - scrollTop - clientHeight < this.scrollThreshold;
  }

  // 滚动到底部（仅在用户未手动滚动时）
  scrollToBottom() {
    if (!this.isUserScrolling) {
      this.container.scrollTop = this.container.scrollHeight;
    }
  }

  // 监听用户滚动事件
  setup() {
    this.container.addEventListener('scroll', () => {
      // 用户手动向上滚动 → 暂停自动滚动
      this.isUserScrolling = !this.isAtBottom();
    });

    // 用户滚动到底部 → 恢复自动滚动
    // 或提供"回到底部"浮动按钮
  }

  // 新内容到达时调用
  onNewContent() {
    this.scrollToBottom();
  }
}

// 使用示例
const scrollManager = new AutoScrollManager(document.getElementById('chat-container'));
scrollManager.setup();

// 在流式渲染回调中调用
renderer.onChunk = (chunk) => {
  appendToDOM(chunk);
  scrollManager.onNewContent();
};
```

**用户体验要点总结**：

| 交互场景 | 策略 |
|---------|------|
| 流式输出中 | 自动滚动到底部，光标闪烁动画 |
| 用户向上滚动查看历史 | 暂停自动滚动，显示"正在输出中"提示 |
| 用户滚动回底部 | 恢复自动滚动 |
| 用户点击停止按钮 | 调用 `abort()`，保留已输出内容 |
| 网络中断 | 自动重试（指数退避），显示"重新连接中..." |
| 输出完成 | 移除光标动画，显示复制/重新生成按钮 |

---

### 3. multer 文件上传（概要）

#### 3.1 multer 中间件用途

multer 是 Express 生态中最常用的文件上传中间件，专门用于解析 `multipart/form-data` 格式的请求体（即包含文件的表单数据）。它基于 `busboy` 实现，支持：

- 单文件 / 多文件上传
- 文件大小限制
- 文件类型（MIME）校验
- 自定义存储引擎（磁盘 / 内存 / 云存储）

#### 3.2 单文件与多文件上传配置

```javascript
const express = require('express');
const multer = require('multer');
const path = require('path');

const app = express();

// 配置磁盘存储
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, './uploads/'); // 文件保存目录
  },
  filename: (req, file, cb) => {
    // 生成唯一文件名：时间戳 + 原始扩展名
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  },
});

// 文件过滤器：仅允许图片类型
const fileFilter = (req, file, cb) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  if (allowedTypes.includes(file.mimetype)) {
    cb(null, true); // 接受文件
  } else {
    cb(new Error('仅支持 JPG、PNG、GIF、WebP 格式的图片'), false);
  }
};

// 创建 multer 实例
const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 5 * 1024 * 1024, // 单个文件最大 5MB
    files: 10,                   // 最多上传 10 个文件
  },
});

// 单文件上传（字段名为 avatar）
app.post('/upload/avatar', upload.single('avatar'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ code: 400, message: '请选择文件' });
  }
  res.json({
    code: 0,
    message: '上传成功',
    data: {
      filename: req.file.filename,
      originalname: req.file.originalname,
      size: req.file.size,
      path: req.file.path,
    },
  });
});

// 多文件上传（字段名为 photos，最多 5 个）
app.post('/upload/photos', upload.array('photos', 5), (req, res) => {
  if (!req.files || req.files.length === 0) {
    return res.status(400).json({ code: 400, message: '请选择文件' });
  }
  res.json({
    code: 0,
    message: '上传成功',
    data: req.files.map(f => ({
      filename: f.filename,
      originalname: f.originalname,
      size: f.size,
    })),
  });
});

// 多字段混合上传
app.post('/upload/mixed', upload.fields([
  { name: 'avatar', maxCount: 1 },
  { name: 'photos', maxCount: 5 },
]), (req, res) => {
  res.json({
    code: 0,
    avatar: req.files['avatar']?.[0]?.filename,
    photos: req.files['photos']?.map(f => f.filename),
  });
});

// multer 错误处理中间件
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    // multer 自身错误（如文件过大）
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ code: 400, message: '文件大小超过限制（最大 5MB）' });
    }
    return res.status(400).json({ code: 400, message: err.message });
  }
  if (err) {
    // 自定义错误（如文件类型不匹配）
    return res.status(400).json({ code: 400, message: err.message });
  }
  next();
});

app.listen(3000);
```

#### 3.3 文件大小限制与类型校验

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `limits.fileSize` | 单个文件最大字节数 | `5 * 1024 * 1024`（5MB） |
| `limits.files` | 最大文件数量 | `10` |
| `limits.fieldSize` | 字段值最大字节数 | `1024 * 1024`（1MB） |
| `limits.fields` | 最大非文件字段数量 | `20` |
| `fileFilter` | 自定义文件过滤函数，可校验 MIME 类型 | 仅允许 `image/*` |

> **详细实现参见**：同目录下的 [03-Node.js笔面试题集](./03-Node.js笔面试题集.md) 和 [综合场景](./综合场景.md) 文件中的完整文件上传示例。

---

## 六、速率限制与安全防护

### 6.1 express-rate-limit 基本配置

`express-rate-limit` 是 Express 生态中最常用的速率限制中间件，用于防止 API 被滥用、暴力破解、DDoS 攻击等。它基于内存或外部存储记录每个 IP 的请求次数，超出阈值后返回 429 Too Many Requests。

```bash
pnpm add express-rate-limit
```

**基础配置**：

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 时间窗口：15 分钟
  max: 100,                   // 每个 IP 在窗口内最多 100 次请求
  message: '请求过于频繁，请稍后再试',
  standardHeaders: true,      // 返回 RateLimit-* 头（draft-6 标准）
  legacyHeaders: false,       // 禁用 X-RateLimit-* 头（旧标准）
});

// 应用到所有 /api/ 路由
app.use('/api/', limiter);
```

**响应头信息**（启用 `standardHeaders: true` 后）：

| 响应头 | 说明 |
|--------|------|
| `RateLimit-Limit` | 窗口内允许的最大请求数 |
| `RateLimit-Remaining` | 当前窗口剩余请求数 |
| `RateLimit-Reset` | 窗口重置的时间戳（Unix 秒） |
| `Retry-After` | 达到限制后，建议等待的秒数 |

### 6.2 差异化限流策略

不同接口的安全需求不同，应对不同路由应用不同的限流策略：

```javascript
const rateLimit = require('express-rate-limit');

// 登录接口：严格限制，防止暴力破解
const loginLimiter = rateLimit({
  windowMs: 1 * 60 * 1000,  // 1 分钟
  max: 5,                     // 最多 5 次尝试
  message: { code: 429, message: '登录尝试过于频繁，请 1 分钟后再试' },
  skipSuccessfulRequests: false, // 包括成功请求也计数
});

// 普通 API：宽松限制
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100,
});

// 静态资源：不限制
app.use('/static', express.static('public'));

// 应用限流
app.use('/api/login', loginLimiter);
app.use('/api/', apiLimiter);
```

**限流策略建议**：

| 接口类型 | 窗口 | 限制次数 | 原因 |
|---------|------|---------|------|
| 登录/注册 | 1 分钟 | 5-10 次 | 防止暴力破解和恶意注册 |
| 验证码发送 | 1 分钟 | 1 次 | 防止短信轰炸 |
| 普通 CRUD API | 15 分钟 | 100-200 次 | 正常使用保护 |
| 文件上传 | 1 小时 | 10-20 次 | 防止存储滥用 |
| 搜索接口 | 1 分钟 | 30 次 | 防止爬虫和恶意搜索 |

### 6.3 跳过与白名单配置

使用 `skip` 函数可以跳过特定请求的限流检查：

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  // 跳过内网 IP 和本地开发环境
  skip: (req) => {
    // 内网 IP 白名单
    const whitelist = ['127.0.0.1', '::1', '::ffff:127.0.0.1'];
    if (whitelist.includes(req.ip)) return true;

    // 内网 IP 段
    if (req.ip.startsWith('192.168.') || req.ip.startsWith('10.')) return true;

    return false;
  },
});

// 基于用户角色的跳过
const userAwareLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  skip: (req) => {
    // VIP 用户不限流
    return req.user?.role === 'vip' || req.user?.role === 'admin';
  },
  keyGenerator: (req) => {
    // 已登录用户按用户 ID 限流，未登录按 IP 限流
    return req.user?.id || req.ip;
  },
});
```

### 6.4 分布式限流（Redis）

在多进程/多实例部署中，内存限流无法跨实例共享计数，需要使用 Redis 作为共享存储：

```bash
pnpm add rate-limit-redis ioredis
```

```javascript
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const Redis = require('ioredis');

const redisClient = new Redis({
  host: 'localhost',
  port: 6379,
  enableOfflineQueue: false,
});

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  // 使用 Redis 存储计数器
  store: new RedisStore({
    sendCommand: (...args) => redisClient.call(...args),
    prefix: 'rl:', // Redis key 前缀
  }),
});
```

**分布式限流注意事项**：
- Redis 连接失败时的降级策略：可以选择放行（安全优先）或拒绝（功能优先）
- Redis 的 `prefix` 用于区分不同应用的限流计数器
- 在高并发场景下，Redis 的原子操作保证了计数的准确性

### 6.5 自定义错误响应

限制达到后返回的响应可以自定义：

```javascript
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  handler: (req, res, next, options) => {
    res.status(options.statusCode).json({
      code: 429,
      message: '请求过于频繁，请稍后再试',
      retryAfter: Math.ceil(options.windowMs / 1000), // 秒
      limit: options.max,
      remaining: 0,
    });
  },
});

// 也可以针对不同环境返回不同内容
const envAwareLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  handler: (req, res) => {
    if (req.accepts('html')) {
      // 浏览器请求返回 HTML 页面
      res.status(429).send('<h1>请求过于频繁</h1><p>请稍后再试</p>');
    } else if (req.accepts('json')) {
      // API 请求返回 JSON
      res.status(429).json({ code: 429, message: '请求过于频繁' });
    } else {
      // 其他请求返回纯文本
      res.status(429).type('txt').send('请求过于频繁');
    }
  },
});
```

### 6.6 与 helmet 配合的安全最佳实践

速率限制应与安全头中间件配合使用，构建多层防护：

```javascript
const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();

// 第一层：安全头
app.use(helmet());

// 第二层：全局速率限制
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
}));

// 第三层：严格限制敏感接口
app.use('/api/auth', rateLimit({
  windowMs: 1 * 60 * 1000,
  max: 10,
  message: '认证请求过于频繁',
}));
```

| 防护层 | 组件 | 作用 |
|--------|------|------|
| 安全头 | helmet | 设置 CSP、X-Frame-Options、HSTS 等安全头 |
| 全局限流 | express-rate-limit | 防止 DDoS 和 API 滥用 |
| 敏感接口限流 | express-rate-limit（严格策略） | 防止暴力破解和撞库 |
| 请求体大小限制 | express.json({ limit }) | 防止大 payload 攻击 |
| 参数校验 | express-validator / joi | 防止注入和参数篡改 |