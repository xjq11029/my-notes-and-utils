# Gateway 网关与负载均衡 导览

> 定位：五维框架浓缩提炼 03-Gateway网关与负载均衡.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./03-Gateway网关与负载均衡.md)。
> 前置知识：[Nacos服务注册与配置中心](./02-Nacos服务注册与配置中心-导览.md)、[Nginx反向代理与负载均衡](../nginx/01-Nginx反向代理与负载均衡-导览.md)

---

## 一、Gateway 架构

### 1.1 核心定位

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 Spring WebFlux 构建的 API 网关，采用非阻塞 I/O 模型，是 Zuul 1.x 的替代方案 |
| 能做什么 | 路由转发；鉴权过滤；限流熔断；跨域处理；负载均衡集成 |
| 怎么用 | `Netty + Reactor 非阻塞 I/O` |
| 原理和工作流程 | 基于 Spring WebFlux（Spring 5）框架构建，底层使用 Netty 加 Reactor 实现非阻塞 I/O，少量 Event Loop 线程处理大量请求，天然支持长连接。相比 Zuul 1.x 基于 Servlet 的阻塞 I/O 一个请求一个线程模型，并发能力显著提升，支持万级并发 |
| 缺点 | 强依赖 WebFlux 与响应式编程模型，学习曲线陡峭；阻塞操作会拖垮 Event Loop 线程；与 spring-boot-starter-web 冲突不能共存 |

### 1.2 Gateway vs Zuul 1.x

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Cloud Gateway 与 Zuul 1.x 两个网关在底层框架、I/O 模型、并发能力上的对比 |
| 能做什么 | 对比底层框架；对比 I/O 与线程模型；对比并发能力与长连接支持；对比维护状态 |
| 怎么用 | `Gateway:WebFlux+非阻塞+活跃 | Zuul1.x:Servlet+阻塞+停更` |
| 原理和工作流程 | Gateway 底层为 Spring WebFlux（Spring 5），非阻塞 I/O（Netty + Reactor），少量线程处理大量请求，并发能力高支持万级并发，天然支持长连接，持续维护；Zuul 1.x 底层为 Servlet 2.5，阻塞 I/O，一个请求一个线程，并发受线程池大小限制，不支持长连接，已停止维护 |
| 缺点 | Gateway 响应式编程调试与排错难度高于同步模型；Zuul 1.x 已停更无安全更新；两者迁移需重写过滤器逻辑 |

### 1.3 请求处理流程

| 维度 | 内容 |
|------|------|
| 是什么 | Gateway 从接收请求到返回响应的完整处理链路 |
| 能做什么 | 路由匹配；断言判定；Pre 过滤；转发后端；Post 过滤；响应返回 |
| 怎么用 | `客户端 -> Netty Server -> RouteLocator -> Predicate -> Filter Chain -> 后端` |
| 原理和工作流程 | 客户端请求到达 Netty Server，经 Gateway Web Handler 交给 RouteLocator 路由匹配；Predicate 断言匹配路由条件，匹配成功进入 Filter Chain；Pre Filter 执行鉴权限流添加请求头，随后转发请求到后端服务；后端返回响应后 Post Filter 执行添加响应头记录日志，最终响应返回客户端 |
| 缺点 | 过滤器链过长增加请求延迟；路由匹配全量扫描效率随路由数增长下降；异步链路异常堆栈难以追踪 |

---

## 二、三大核心组件

### 2.1 Route（路由）

| 维度 | 内容 |
|------|------|
| 是什么 | 网关的基本构建块，由 id、uri、predicates、filters、order 五个属性组成 |
| 能做什么 | 唯一标识路由；指定目标服务地址；绑定断言与过滤器；控制路由优先级 |
| 怎么用 | `id + uri(lb://) + predicates + filters + order` |
| 原理和工作流程 | 路由包含 id（唯一标识）、uri（目标服务地址，支持 lb:// 负载均衡）、predicates（断言集合匹配请求条件）、filters（过滤器集合修改请求响应）、order（路由优先级，越小越优先）。RouteLocator 在启动时加载路由定义，运行时按 order 顺序匹配 |
| 缺点 | 路由配置分散在配置文件中难以集中管理；动态路由需额外实现；路由数量过多影响匹配性能 |

### 2.2 Predicate（断言）

| 维度 | 内容 |
|------|------|
| 是什么 | 用于匹配 HTTP 请求条件的谓词，决定请求是否匹配某条路由 |
| 能做什么 | 路径匹配；主机名匹配；请求方法匹配；请求头匹配；查询参数匹配；Cookie 匹配；时间匹配 |
| 怎么用 | `Path=/order/** | Host=**.example.com | Method=GET,POST` |
| 原理和工作流程 | 提供多种内置谓词：Path 路径匹配、Host 主机名匹配、Method 请求方法匹配、Header 请求头匹配、Query 查询参数匹配、Cookie 匹配、After/Before/Between 时间匹配。请求到达后按路由 order 顺序依次对 predicates 求值，全部命中则匹配该路由 |
| 缺点 | 断言组合复杂时可读性差；正则匹配性能开销大；不支持请求体内容匹配 |

### 2.3 Filter（过滤器）

| 维度 | 内容 |
|------|------|
| 是什么 | 在请求转发前后执行逻辑的组件，分为 GatewayFilter 与 GlobalFilter 两类 |
| 能做什么 | 修改请求响应；鉴权限流；添加请求头响应头；记录日志；统一异常处理 |
| 怎么用 | `GatewayFilter(特定路由) | GlobalFilter(全局生效)` |
| 原理和工作流程 | GatewayFilter 作用于特定路由由 filters 配置指定；GlobalFilter 作用于所有路由全局生效无需配置。过滤器执行顺序分 Pre 阶段（请求转发前）与 Post 阶段（响应返回后），GlobalFilter 通过 getOrder() 方法控制执行顺序，值越小优先级越高 |
| 缺点 | 过滤器执行顺序错误会导致鉴权在路由后执行；GlobalFilter 全局生效缺乏精细控制；过滤器间共享状态需通过 Exchange 属性传递 |

---

## 三、负载均衡

### 3.1 LoadBalancerClientFilter

| 维度 | 内容 |
|------|------|
| 是什么 | Gateway 内置的负载均衡过滤器，通过 lb:// 前缀自动实现服务实例选择 |
| 能做什么 | 解析 lb:// 前缀；从注册中心获取实例列表；选择实例替换地址；转发请求 |
| 怎么用 | `uri: lb://order-service` |
| 原理和工作流程 | 路由 uri 配置 lb:// 前缀表示启用负载均衡，LoadBalancerClientFilter 拦截该请求，从注册中心拉取目标服务的实例列表，使用负载均衡策略（默认轮询）选择一个实例，将服务名替换为真实 IP:Port 后转发请求 |
| 缺点 | 实例列表缓存存在短暂延迟，新实例上线或下线不能立即感知；实例列表为空时请求失败无自动重试；负载均衡策略扩展需自定义 Bean |

### 3.2 负载均衡策略

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Cloud LoadBalancer 提供的实例选择策略 |
| 能做什么 | 轮询分配；随机分配；自定义策略扩展 |
| 怎么用 | `RoundRobinLoadBalancer(默认) | RandomLoadBalancer` |
| 原理和工作流程 | Spring Cloud LoadBalancer 支持两种策略：RoundRobinLoadBalancer（默认）按顺序轮询分配请求，适用服务实例性能相近场景；RandomLoadBalancer 随机分配请求，适用简单随机分配场景。自定义策略通过实现 ReactorLoadBalancer 接口注册为 Bean |
| 缺点 | 内置策略少，缺乏加权轮询、一致性哈希等高级策略；轮询策略不考虑实例实际负载与健康度；策略切换需重启或自定义配置 |

---

## 四、实战应用

### 4.1 基础路由配置

| 维度 | 内容 |
|------|------|
| 是什么 | Gateway 通过 YAML 配置路由规则的基本用法 |
| 能做什么 | 定义多条路由；绑定路径断言；配置 StripPrefix 过滤器；指向负载均衡服务 |
| 怎么用 | `routes: id+uri(lb://)+predicates(Path)+filters(StripPrefix=1)` |
| 原理和工作流程 | 在 spring.cloud.gateway.routes 下定义路由列表，每条路由包含 id、uri（lb:// 启用负载均衡）、predicates（Path 路径匹配）、filters（StripPrefix=1 去除第一层路径前缀）。请求到达后按 predicates 匹配路由，匹配成功经 filters 处理后转发到 lb:// 对应服务 |
| 缺点 | 路由配置硬编码在配置文件，变更需重启；路由数量增长后配置文件臃肿；缺少路由级超时与重试配置 |

### 4.2 统一鉴权（JWT Token 校验）

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 GlobalFilter 在网关层统一校验 JWT Token 并透传用户信息的鉴权方案 |
| 能做什么 | 白名单放行；Token 提取与校验；用户信息透传下游；高优先级先执行 |
| 怎么用 | `GlobalFilter+Ordered(getOrder=-100) + JwtUtil.parseToken` |
| 原理和工作流程 | 实现 GlobalFilter 与 Ordered 接口，getOrder 返回 -100 保证最先执行。流程：判断路径是否在白名单（登录、公开接口），白名单直接放行；提取 Authorization Header 的 Bearer Token，缺失或格式错误返回 401；JwtUtil 解析 Token，校验失败返回 401；解析成功将 userId、userName 通过 mutate 写入请求头透传下游，chain.filter 放行 |
| 缺点 | 网关承担鉴权增加单点压力，Token 解析消耗 CPU；白名单硬编码需重启或依赖配置中心；Token 泄露后网关层无法识别需配合过期刷新机制 |

### 4.3 限流配置

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 RequestRateLimiter 过滤器基于 Redis 令牌桶实现请求限流 |
| 能做什么 | 控制每秒请求数；令牌桶容量配置；按 Key 维度限流；超出限流拒绝请求 |
| 怎么用 | `RequestRateLimiter + redis-rate-limiter.replenishRate + burstCapacity + key-resolver` |
| 原理和工作流程 | 在路由 filters 中配置 RequestRateLimiter，replenishRate 控制每秒填充令牌数，burstCapacity 控制令牌桶容量，key-resolver 指定限流 Key 解析器（如按 IP）。底层基于 Redis 令牌桶算法，请求获取令牌成功放行，令牌不足返回 429 Too Many Requests |
| 缺点 | 强依赖 Redis，Redis 故障导致限流失效或请求拒绝；令牌桶参数需根据实际流量调优；Key 解析器逻辑复杂时影响性能 |

### 4.4 跨域 CORS 配置

| 维度 | 内容 |
|------|------|
| 是什么 | Gateway 全局跨域资源共享配置，允许浏览器跨域访问 |
| 能做什么 | 配置允许的源；允许的方法与请求头；允许携带凭证；预检请求缓存时间 |
| 怎么用 | `globalcors.cors-configurations: allowedOriginPatterns + allowedMethods + maxAge` |
| 原理和工作流程 | 在 spring.cloud.gateway.globalcors.cors-configurations 下按路径模式配置 CORS 规则，allowedOriginPatterns 指定允许的源，allowedMethods 指定允许的方法，allowedHeaders 指定允许的请求头，allowCredentials 允许携带凭证，maxAge 设置预检请求缓存时间。网关在响应头添加 CORS 相关字段 |
| 缺点 | allowedOrigins 配置 * 与 allowCredentials true 不兼容需用 allowedOriginPatterns；CORS 仅防浏览器跨域无法防服务端调用；配置错误导致跨域失效 |

---

## 五、常见面试题

### 1. Gateway 和 Zuul 的核心区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Gateway 与 Zuul 1.x 在底层框架与 I/O 模型上的差异 |
| 能做什么 | 对比底层框架；对比 I/O 与线程模型；对比并发能力；对比维护状态 |
| 怎么用 | `Gateway:WebFlux非阻塞+活跃 | Zuul1.x:Servlet阻塞+停更` |
| 原理和工作流程 | Gateway 基于 WebFlux（Netty + Reactor），非阻塞 I/O，少量线程处理大量请求，并发能力强支持万级并发；Zuul 1.x 基于 Servlet，阻塞 I/O，一个请求一个线程，并发能力受线程池大小限制。Zuul 1.x 已停止维护，Gateway 是当前推荐方案 |
| 缺点 | Gateway 响应式编程学习成本高；Zuul 1.x 已停更无社区支持；迁移需重写过滤器 |

### 2. Gateway 的三大核心组件是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Route、Predicate、Filter 三个核心组件的定义与职责 |
| 能做什么 | 路由定义目标与标识；断言匹配请求条件；过滤器修改请求响应 |
| 怎么用 | `Route(id+uri) + Predicate(Path/Host) + Filter(Pre/Post)` |
| 原理和工作流程 | Route（路由）由 ID、URI、Predicate 集合、Filter 集合组成；Predicate（断言）匹配 HTTP 请求条件（Path、Header、Method 等）；Filter（过滤器）在请求转发前后执行逻辑（鉴权、限流、日志等）。三者协作：Predicate 匹配路由，Filter 处理请求，Route 定义转发目标 |
| 缺点 | 三组件概念易混淆；Predicate 与 Filter 职责边界模糊时配置混乱；组件组合复杂可读性差 |

### 3. Gateway 如何实现负载均衡？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Gateway 通过 lb:// 前缀集成负载均衡的机制 |
| 能做什么 | 解析 lb:// 前缀；获取实例列表；选择实例转发；默认轮询策略 |
| 怎么用 | `uri: lb://order-service -> LoadBalancerClientFilter` |
| 原理和工作流程 | 通过 lb:// 前缀声明路由目标，内置 LoadBalancerClientFilter 自动从注册中心获取服务实例列表，使用负载均衡策略（默认轮询）选择实例转发请求。配置 url 属性则直接调用该地址跳过负载均衡 |
| 缺点 | 实例列表缓存存在延迟；实例为空时请求失败无重试；策略扩展需自定义 Bean |

### 4. GlobalFilter 和 GatewayFilter 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查两类过滤器的作用范围与执行顺序控制 |
| 能做什么 | GatewayFilter 作用于特定路由；GlobalFilter 作用于所有路由；通过 getOrder 控制顺序 |
| 怎么用 | `GatewayFilter(filters配置) | GlobalFilter(全局生效,getOrder排序)` |
| 原理和工作流程 | GatewayFilter 作用于特定路由在 filters 中配置；GlobalFilter 作用于所有路由全局生效无需配置。GlobalFilter 通过实现 Ordered 接口的 getOrder() 方法控制执行顺序，值越小优先级越高。鉴权 Filter 通常设置高优先级（如 -100）保证最先执行 |
| 缺点 | GlobalFilter 全局生效缺乏路由级控制；执行顺序错误导致鉴权滞后；两类过滤器混用时顺序难以预测 |

---

## 六、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | Gateway 使用中常见错误的现象、原因与解决方案汇总 |
| 能做什么 | 避免网关做复杂业务；正确控制 Filter 顺序；避免依赖冲突；配置 Redis 支撑限流；集成熔断降级 |
| 怎么用 | `网关专注横切 | getOrder控制顺序 | 不引入web | 限流配Redis | 集成Sentinel` |
| 原理和工作流程 | 网关做复杂业务逻辑会导致性能下降成瓶颈，应专注横切关注点；Filter 执行顺序错误导致鉴权在路由后执行，应通过 getOrder() 控制优先级；引入 spring-boot-starter-web 与 WebFlux 冲突导致启动失败，应使用 webflux；限流未配 Redis 导致 RequestRateLimiter 不生效；生产环境未配熔断降级会被后端故障拖垮，应集成 Sentinel 或 Resilience4j |
| 缺点 | 避坑要点需经验积累；部分方案引入额外依赖增加复杂度；Filter 顺序与依赖冲突排查难度高 |

---

> [返回原文](./03-Gateway网关与负载均衡.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
