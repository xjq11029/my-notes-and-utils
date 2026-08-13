# JavaWeb 核心与 HTTP 协议 导览

> 定位：五维框架浓缩提炼 01-JavaWeb核心与HTTP协议.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./01-JavaWeb核心与HTTP协议.md)。
> 前置知识：无

---

## 一、核心概念

### 1.1 Web 开发概念

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 HTTP 协议构建客户端与服务端交互的应用程序，涵盖前端页面、后端逻辑、数据存储三层架构 |
| 能做什么 | 构建动态网站、RESTful API、企业级 Web 应用；支持用户注册登录、数据增删改查、实时通信等场景 |
| 怎么用 | 前端 HTML/CSS/JavaScript 构建页面，后端 Java/Python/Node.js 处理业务逻辑，数据库 MySQL/Redis 存储数据，通过 HTTP 协议通信 |
| 原理和工作流程 | 客户端（浏览器）发送 HTTP 请求到 Web 服务器，服务器解析请求后调用后端程序处理业务逻辑，查询或更新数据库，将结果封装为 HTTP 响应返回客户端，浏览器渲染响应内容展示给用户。整个过程遵循请求-响应模型，每次交互独立无状态 |
| 缺点 | HTTP 无状态导致需要额外机制维持会话；前后端分离增加部署复杂度；跨域安全限制需额外配置；网络延迟影响用户体验需优化 |

### 1.2 HTTP 协议概述

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 是一种无状态、基于请求-响应模型的应用层协议，运行在 TCP 之上，默认端口 80 |
| 能做什么 | 定义客户端与服务端的数据交换格式；支持 GET/POST/PUT/DELETE 等方法操作资源；通过状态码标识处理结果；通过头部字段传递元信息 |
| 怎么用 | 客户端构造请求行+请求头+请求体发送到服务端，服务端返回状态行+响应头+响应体给客户端 |
| 原理和工作流程 | HTTP 建立在 TCP 协议之上，经历三次握手建立连接后发送请求报文，服务端处理完毕后返回响应报文，可通过 Connection: keep-alive 复用连接。各版本演进：HTTP/1.0 每次请求新建连接，HTTP/1.1 支持持久连接和管道化，HTTP/2 支持多路复用和头部压缩，HTTP/3 基于 QUIC 使用 UDP 进一步提升性能 |
| 缺点 | 明文传输不安全需 HTTPS；无状态特性需 Cookie/Session 或 Token 补充；HTTP/1.1 队头阻塞问题；GET 请求参数暴露在 URL |

### 1.3 HTTP 请求报文

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 请求报文由请求行、请求头、空行、请求体四部分组成，是客户端向服务端发送的数据格式 |
| 能做什么 | 请求行指定 HTTP 方法、URL 和协议版本；请求头携带 Host、Content-Type、Authorization 等元信息；请求体传输表单数据、JSON、文件等 |
| 怎么用 | `POST /api/user?debug=true HTTP/1.1` + 请求头键值对 + 空行 + 请求体内容 |
| 原理和工作流程 | 请求行包含请求方法（GET/POST/PUT/DELETE 等）、请求 URI（含查询参数）和 HTTP 协议版本。请求头以 Key: Value 格式传递元信息，常用头包括 Host、Content-Type、Content-Length、Authorization、Cookie、User-Agent。空行区分头部与体部。请求体在 GET 请求中通常为空，POST/PUT 请求中承载数据 |
| 缺点 | 请求体一次读取后无法重复消费；请求头大小无硬性限制但服务器可能拒绝过大头部；GET 请求参数在 URL 中暴露；URL 长度受浏览器和服务器限制 |

### 1.4 HTTP 响应报文

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 响应报文由状态行、响应头、空行、响应体四部分组成，是服务端向客户端返回的数据格式 |
| 能做什么 | 状态行返回协议版本、状态码和状态描述；响应头携带 Content-Type、Content-Length、Set-Cookie 等元信息；响应体返回 HTML、JSON、图片等实际内容 |
| 怎么用 | `HTTP/1.1 200 OK` + 响应头键值对 + 空行 + 响应体内容 |
| 原理和工作流程 | 状态行包含协议版本、三位状态码和状态描述短语。响应头以 Key: Value 格式传递元信息，常用头包括 Content-Type、Content-Length、Set-Cookie、Cache-Control、Location。空行后为响应体，承载实际返回内容，可为 HTML 页面、JSON 数据、二进制文件等。服务端处理完成后将响应写入 Socket 输出流发送给客户端 |
| 缺点 | 响应体一次性写入后不可修改；状态码语义有限难以表达复杂业务错误；大响应体需分块传输增加实现复杂度；响应头过多增加网络开销 |

### 1.5 状态码详解

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 状态码是三位数字，表示服务端对请求的处理结果，分为五类：1xx 信息、2xx 成功、3xx 重定向、4xx 客户端错误、5xx 服务端错误 |
| 能做什么 | 200 表示请求成功；301/302 控制页面跳转；304 利用浏览器缓存；400/401/403/404 反馈客户端问题；500/502/503 反馈服务端问题 |
| 怎么用 | 服务端通过 `resp.setStatus(200)` 设置状态码；客户端根据状态码决定后续行为（如 401 跳转登录、302 跟随重定向） |
| 原理和工作流程 | 1xx 信息类（100 Continue、101 Switching Protocols）。2xx 成功类（200 OK、201 Created、204 No Content）。3xx 重定向类（301 永久重定向浏览器缓存新地址、302 临时重定向每次重新请求、304 资源未修改使用缓存）。4xx 客户端错误类（400 Bad Request、401 未认证、403 无权限、404 不存在、405 方法不允许）。5xx 服务端错误类（500 内部错误、502 网关无效响应、503 服务不可用、504 网关超时） |
| 缺点 | 状态码语义有限无法精确表达业务错误；部分浏览器对某些状态码有特殊处理；401 和 403 常被混淆；自定义业务错误码需额外约定 |

### 1.6 HTTPS 核心原理

| 维度 | 内容 |
|------|------|
| 是什么 | HTTPS 是 HTTP over TLS/SSL，在 HTTP 与 TCP 之间加入 TLS 加密层，通过非对称加密协商对称密钥后使用对称加密传输数据，默认端口 443 |
| 能做什么 | 加密传输数据防窃听；验证服务器身份防冒充；保证数据完整性防篡改；支持双向认证 |
| 怎么用 | 服务端配置 SSL 证书（含公钥和域名信息），客户端通过 HTTPS URL 访问，浏览器自动完成 TLS 握手 |
| 原理和工作流程 | TLS 握手流程：1. 客户端发送 ClientHello（支持的加密套件列表、随机数）。2. 服务端返回 ServerHello + 证书（含公钥）+ ServerHelloDone。3. 客户端验证证书有效性，生成预主密钥用服务端公钥加密后发送。4. 双方用客户端随机数+服务端随机数+预主密钥生成会话密钥。5. 双方确认切换加密模式，后续通信使用对称加密。证书由 CA 签发，操作系统和浏览器内置 CA 根证书信任链 |
| 缺点 | TLS 握手增加 1-2 个 RTT 延迟；证书有有效期需定期续费；非对称加密计算开销大（仅握手阶段）；旧版本 TLS/SSL 存在安全漏洞需升级 |

### 1.7 Cookie 机制

| 维度 | 内容 |
|------|------|
| 是什么 | Cookie 是服务端通过 Set-Cookie 响应头下发给浏览器的客户端存储机制，浏览器在后续请求中通过 Cookie 请求头自动回传 |
| 能做什么 | 维持用户登录状态；记录用户偏好（语言、主题）；跟踪用户行为；实现购物车功能 |
| 怎么用 | 服务端：`resp.addCookie(new Cookie("key", "value"))`；客户端：浏览器自动管理存储和回传 |
| 原理和工作流程 | 服务端通过 Set-Cookie 响应头设置 Cookie，格式为 `Set-Cookie: name=value; Domain=xxx; Path=/; Max-Age=3600; HttpOnly; Secure; SameSite=Lax`。Domain 指定生效域名范围，Path 指定生效路径，Max-Age 设置有效期，HttpOnly 禁止 JavaScript 读取防 XSS，Secure 要求仅 HTTPS 传输，SameSite 控制跨站请求时是否发送。浏览器存储 Cookie 后在匹配域名的请求中自动通过 Cookie 请求头回传，单个 Cookie 大小限制约 4KB，每个域名总 Cookie 数约 20-50 个 |
| 缺点 | 大小限制约 4KB 无法存储大量数据；客户端存储可被篡改；每次请求自动携带增加网络开销；跨域共享复杂；隐私法规要求 Cookie 同意提示 |

### 1.8 Session 机制

| 维度 | 内容 |
|------|------|
| 是什么 | Session 是服务端维护的用户会话对象，通过 Cookie 中的 JSESSIONID 与客户端关联，存储在服务端内存或外部存储中 |
| 能做什么 | 存储用户登录状态；保存购物车数据；记录用户操作上下文；实现权限控制 |
| 怎么用 | `HttpSession session = req.getSession(); session.setAttribute("user", user); session.getAttribute("user"); session.invalidate();` |
| 原理和工作流程 | 客户端首次请求时服务端调用 req.getSession() 创建 HttpSession 对象并生成唯一 JSESSIONID，通过 Set-Cookie 将 JSESSIONID 返回客户端。客户端后续请求自动携带 JSESSIONID Cookie，服务端根据此 ID 查找对应 Session 对象。Session 默认超时时间为 30 分钟（Tomcat），生命周期：创建（首次请求）-> 活跃（每次请求重置超时计时器）-> 过期（超时或主动 invalidate）-> 销毁。Tomcat 关闭时可将 Session 序列化到磁盘，重启后反序列化恢复 |
| 缺点 | 占用服务端内存大量用户时压力大；分布式环境需 Session 共享（Redis）；依赖 Cookie 若浏览器禁用需 URL 重写；Session 固定攻击风险需登录后重新生成 |

### 1.9 Cookie 与 Session 对比

| 维度 | 内容 |
|------|------|
| 是什么 | Cookie 客户端存储机制与 Session 服务端会话机制两种状态保持方案的全面对比 |
| 能做什么 | Cookie 存轻量键值对约 4KB 在客户端；Session 存任意对象在服务端通过 JSESSIONID 关联 |
| 怎么用 | Cookie：`resp.addCookie(new Cookie("k","v"))`；Session：`req.getSession().setAttribute("k",v)` |
| 原理和工作流程 | 存储位置：Cookie 在浏览器，Session 在服务端。大小限制：Cookie 约 4KB，Session 无限制受内存影响。安全性：Cookie 可被篡改，Session 较安全。生命周期：Cookie 可设 Max-Age 持久化或浏览器关闭即失效，Session 默认 30 分钟超时。性能：Cookie 每次请求携带增加带宽，Session 占用服务端内存。协作关系：Session 依赖 Cookie 传递 JSESSIONID，二者共同解决 HTTP 无状态问题 |
| 缺点 | Cookie 大小受限且不安全；Session 服务端内存消耗大；分布式需额外 Session 共享方案；二者均需防范 CSRF 攻击 |

---

## 二、底层原理

### 2.1 HTTP 请求在 Tomcat 中的完整流转

| 维度 | 内容 |
|------|------|
| 是什么 | 一个 HTTP 请求从客户端发出到 Tomcat 内部处理完毕的全链路流转过程 |
| 能做什么 | 理解请求在各组件间的流转路径；掌握 Connector 与 Container 的协作机制；定位请求处理瓶颈 |
| 怎么用 | 请求 -> Connector(NIO Endpoint) -> CoyoteAdapter -> Mapper -> Pipeline-Valve -> FilterChain -> Servlet |
| 原理和工作流程 | 1. 客户端 TCP 三次握手后发送 HTTP 请求报文。2. Connector 的 NIO Endpoint 通过 Poller 线程监听 Socket 事件，将就绪连接交给 Worker 线程池。3. Worker 线程解析 HTTP 协议封装为 CoyoteRequest/CoyoteResponse。4. CoyoteAdapter 适配为 HttpServletRequest/Response。5. Mapper 根据 URL 匹配 Host -> Context -> Wrapper。6. 依次经过 Engine -> Host -> Context -> Wrapper 的 Pipeline-Valve 责任链。7. Wrapper 构建 FilterChain 依次执行 Filter。8. 最终调用 Servlet 的 service()。9. 响应沿原路返回 |
| 缺点 | 流转链路长排查问题需逐层定位；Coyote 到 Servlet API 的适配有性能开销；Pipeline-Valve 责任链增加理解成本；FilterChain 执行顺序依赖配置易出错 |

### 2.2 Cookie 与 Session 的底层实现

| 维度 | 内容 |
|------|------|
| 是什么 | Cookie 通过 HTTP 响应头 Set-Cookie 下发和请求头 Cookie 回传实现，Session 通过 Tomcat 的 Manager 组件管理会话生命周期 |
| 能做什么 | Cookie 在 HTTP 层面实现客户端状态存储；Session 在 Tomcat 容器层面通过 Manager 实现服务端会话管理 |
| 怎么用 | Set-Cookie 响应头下发；Cookie 请求头回传；Manager 管理 Session 生命周期 |
| 原理和工作流程 | Cookie 实现：response.addCookie() 时 Tomcat 将 Cookie 序列化为 `Set-Cookie: name=value; Domain=xxx; Path=/` 写入响应头。浏览器解析 Set-Cookie 头按 Domain/Path 规则存储，后续自动通过 Cookie 请求头回传。Session 实现：Tomcat 内置 StandardManager 管理 Session，Session 存储在 ConcurrentHashMap 中（key 为 JSESSIONID），后台线程定期扫描过期 Session 清理。StandardManager 支持 Session 持久化，关闭时序列化到 SESSIONS.ser，启动时反序列化恢复。分布式可用 PersistentManager 配合 JDBCStore 或 Redis |
| 缺点 | Cookie 每次请求自动携带增加带宽消耗；Session 单机存储在容器重启时丢失；StandardManager 持久化不适用于高并发；分布式 Session 共享增加系统复杂度 |

### 2.3 HTTPS 加密套件协商过程

| 维度 | 内容 |
|------|------|
| 是什么 | TLS 握手中客户端与服务端协商选择双方都支持的加密套件（密钥交换算法 + 对称加密算法 + 消息认证码算法）的过程 |
| 能做什么 | 协商密钥交换算法（RSA/DH/ECDHE）；协商对称加密算法（AES-GCM/ChaCha20）；协商哈希算法（SHA256/SHA384）；保证前向安全性 |
| 怎么用 | 客户端在 ClientHello 中发送支持的加密套件列表，服务端在 ServerHello 中选择其一 |
| 原理和工作流程 | 加密套件格式如 `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`，含义：ECDHE 为密钥交换算法（支持前向安全），RSA 为身份认证算法，AES_128_GCM 为对称加密算法，SHA256 为消息认证码算法。协商过程：客户端在 ClientHello 中按优先级发送支持的加密套件列表。服务端根据自身配置和安全策略选择优先级最高的共同套件在 ServerHello 中返回。推荐优先 ECDHE 密钥交换，优先 AES-GCM 或 ChaCha20-Poly1305，禁用 RC4、3DES、MD5 |
| 缺点 | 低版本客户端可能不支持现代加密套件；配置不当可能降级到不安全套件；加密套件组合复杂需专业知识；TLS 1.3 简化了套件但部分旧系统不兼容 |

---

## 三、实战应用

### 3.1 手写 HTTP 请求解析器

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 Java Socket 编程手动解析 HTTP 请求报文，提取请求行、请求头和请求体的实战示例 |
| 能做什么 | 解析请求方法、URL、协议版本；解析请求头键值对；解析请求体内容；理解 HTTP 协议底层结构 |
| 怎么用 | 创建 ServerSocket 监听端口，accept 获取 Socket，从 InputStream 读取字节流按 HTTP 格式解析 |
| 原理和工作流程 | 通过 ServerSocket 监听指定端口，accept() 阻塞等待客户端连接。获取 Socket 后从 getInputStream() 读取字节流。首先按行读取请求行，按空格分割出方法、URI、协议版本。然后循环按行读取请求头，每行以 `Key: Value` 格式解析，直到遇到空行。根据 Content-Length 头读取对应长度的请求体字节。解析完成后可构造响应返回客户端 |
| 缺点 | 手动解析繁琐易出错需处理各种边界情况；性能不如 NIO 模型；阻塞 I/O 不适合高并发；需自行处理长连接和分块传输 |

### 3.2 Cookie 实现记住登录状态

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 Cookie 实现用户登录后记住用户名和自动登录功能的实战示例 |
| 能做什么 | 登录成功后写入 Cookie 记录用户名；下次访问时读取 Cookie 自动填充；设置 Max-Age 控制记住时长 |
| 怎么用 | 登录成功：`Cookie c = new Cookie("username", URLEncoder.encode(name, "UTF-8")); c.setMaxAge(7*24*3600); resp.addCookie(c);` 读取：`for (Cookie c : req.getCookies()) { if ("username".equals(c.getName())) { ... } }` |
| 原理和工作流程 | 用户登录成功后，服务端创建 Cookie 存储用户名（需 URLEncoder 编码避免中文乱码），设置 Max-Age 为 7 天，通过 response.addCookie 写入响应。浏览器收到 Set-Cookie 后存储到本地。下次访问时浏览器自动通过 Cookie 请求头回传，服务端通过 request.getCookies() 遍历获取。安全注意事项：敏感信息不应存 Cookie；Cookie 值需加密或签名防篡改；设置 HttpOnly 和 Secure 属性；使用 SameSite 属性防 CSRF |
| 缺点 | Cookie 存储明文用户名有隐私风险；客户端可篡改 Cookie 值；Cookie 大小限制约 4KB 无法存复杂数据；跨浏览器不共享 |

### 3.3 Session 实现用户登录状态管理

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 HttpSession 实现用户登录认证和状态保持的完整实战示例 |
| 能做什么 | 登录成功后将用户信息存入 Session；通过 Session 判断登录状态；实现登出功能清除 Session；设置 Session 超时时间 |
| 怎么用 | 登录：`req.getSession().setAttribute("user", user);` 校验：`session.getAttribute("user") != null` 登出：`session.invalidate();` |
| 原理和工作流程 | 用户登录时验证用户名密码，成功后调用 req.getSession() 获取或创建 Session，将用户对象存入 Session 的 user 属性。后续请求通过 session.getAttribute("user") 判断是否已登录。登录成功后可调用 session.setMaxInactiveInterval(1800) 设置超时。登出时调用 session.invalidate() 销毁 Session。安全要点：登录成功后调用 session.invalidate() 销毁旧 Session 再创建新 Session 防止 Session 固定攻击；Session 中仅存用户标识而非完整敏感信息 |
| 缺点 | 服务端内存消耗大高并发时需扩容；分布式需 Session 共享增加复杂度；Session 超时后用户需重新登录；Session 依赖 Cookie 浏览器禁用需 URL 重写 |

---

## 四、常见面试题

### 1. HTTP 协议中 GET 和 POST 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 两种最常用请求方法在参数位置、长度限制、安全性、幂等性、缓存、语义等维度的全面对比 |
| 能做什么 | GET 获取资源参数在 URL 可缓存幂等；POST 提交数据参数在请求体不缓存非幂等 |
| 怎么用 | GET：`/api/user?id=1`；POST：`/api/user` + JSON 请求体 |
| 原理和工作流程 | GET 参数通过 URL 查询字符串传递，浏览器限制 URL 长度约 2KB，可被浏览器和 CDN 缓存，幂等（多次请求结果相同），参数暴露在 URL 不安全。POST 参数通过请求体传递，理论上无长度限制，默认不缓存，非幂等，参数不在 URL 中相对安全。本质区别是语义：GET 用于获取资源，POST 用于提交数据。GET 请求可被浏览器收藏、可在地址栏直接访问，POST 不能 |
| 缺点 | GET 长度限制受浏览器和服务器约束不一致；POST 明文传输仍不安全；语义常被误用（GET 提交数据）；幂等性是语义约定非协议强制 |

### 2. HTTP 和 HTTPS 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 明文传输与 HTTPS 加密传输在安全性、端口、证书、性能、部署等维度的对比 |
| 能做什么 | HTTP 明文传输端口 80；HTTPS 基于 TLS 加密端口 443 需 CA 证书 |
| 怎么用 | HTTP：`http://domain.com`；HTTPS：`https://domain.com` 需配置 SSL 证书 |
| 原理和工作流程 | HTTP 数据明文传输，中间人可窃听、篡改。HTTPS 在 HTTP 与 TCP 间加入 TLS 加密层，通过非对称加密协商对称密钥后使用对称加密传输数据，防止窃听和篡改。HTTPS 需要 CA 签发证书验证服务器身份。TLS 握手增加 1-2 个 RTT 延迟，但 HTTP/2 仅支持 HTTPS 可实现多路复用提升性能。搜索引擎对 HTTPS 站点有排名加权 |
| 缺点 | HTTPS 证书有费用和有效期；TLS 握手增加延迟；旧设备可能不支持现代 TLS 版本；部署和运维复杂度高于 HTTP |

### 3. Cookie 和 Session 的区别和联系？

| 维度 | 内容 |
|------|------|
| 是什么 | Cookie 客户端存储与 Session 服务端会话两种机制的对比及 Session 基于 Cookie 中 JSESSIONID 关联的协作关系 |
| 能做什么 | Cookie 客户端存小量数据约 4KB；Session 服务端存用户状态无限制；Session 通过 JSESSIONID 关联 Cookie |
| 怎么用 | Cookie：`resp.addCookie(new Cookie("k","v"))`；Session：`req.getSession().setAttribute("k",v)` |
| 原理和工作流程 | 存储位置：Cookie 在浏览器，Session 在服务端。大小限制：Cookie 约 4KB，Session 无限制受内存影响。安全性：Cookie 可被篡改，Session 较安全。生命周期：Cookie 可设 Max-Age 持久化或浏览器关闭即失效，Session 默认 30 分钟超时。性能：Cookie 每次请求携带增加带宽，Session 占用服务端内存。协作关系：Session 依赖 Cookie 传递 JSESSIONID，二者共同解决 HTTP 无状态问题。若浏览器禁用 Cookie，Session 可通过 URL 重写实现跟踪 |
| 缺点 | Cookie 大小受限且不安全；Session 服务端内存消耗大；分布式需 Session 共享；浏览器禁用 Cookie 需 URL 重写增加复杂度 |

### 4. 什么是 HTTP 的无状态？如何解决？

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 协议本身不保存客户端的状态信息，每次请求都是独立的，服务端无法识别两次请求是否来自同一用户 |
| 能做什么 | 理解无状态的含义；掌握 Cookie/Session 和 Token 两种状态保持方案 |
| 怎么用 | Cookie/Session 方案：服务端创建 Session 通过 Cookie 传递 JSESSIONID；Token 方案：服务端签发 JWT 等令牌客户端存储并在请求头中携带 |
| 原理和工作流程 | HTTP 无状态意味着协议层面每个请求都是独立事务，服务端处理完请求后不保留任何客户端信息。Cookie/Session 方案：服务端创建 Session 存储用户状态，生成 JSESSIONID 通过 Set-Cookie 下发，客户端后续请求自动携带 Cookie，服务端根据 JSESSIONID 还原 Session。Token 方案：用户登录后服务端签发 Token，客户端存储并在后续请求的 Authorization 头中携带，服务端验证 Token 有效性并从中提取用户信息。Token 方案天然支持分布式，不依赖服务端存储 |
| 缺点 | Cookie/Session 方案服务端内存消耗大且分布式需共享；Token 方案令牌体积大增加带宽；Token 无法主动失效需设置短有效期；两种方案均需防范 CSRF 和 XSS 攻击 |

### 5. 常见的 HTTP 状态码有哪些？各代表什么含义？

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 状态码分为五类，是服务端对请求处理结果的标准化标识 |
| 能做什么 | 2xx 表示成功；3xx 表示重定向；4xx 表示客户端错误；5xx 表示服务端错误 |
| 怎么用 | 服务端通过 `resp.setStatus(200)` 设置，客户端根据状态码决定后续行为 |
| 原理和工作流程 | 200 OK 请求成功。301 永久重定向浏览器缓存新地址，302 临时重定向每次重新请求，304 资源未修改使用缓存。400 请求参数错误，401 未认证需登录，403 已认证无权限，404 资源不存在，405 方法不允许。500 服务器内部错误，502 网关收到无效响应，503 服务不可用过载或维护中，504 网关超时。3xx 重定向时浏览器自动跟随 Location 头跳转；4xx 和 5xx 需要前端做错误处理和用户提示 |
| 缺点 | 状态码语义有限无法精确表达业务错误；部分浏览器对 301 缓存期过长难以清除；401 和 403 常被混淆；502 和 504 排查困难需定位上游服务 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | JavaWeb 开发中 HTTP 协议、Cookie/Session、HTTPS 相关的高频错误与陷阱汇总 |
| 能做什么 | 解决 Cookie 中文乱码；防范 Session 固定攻击；处理 HTTPS 证书问题；避免 Cookie 跨域问题 |
| 怎么用 | Cookie 中文用 URLEncoder 编码；登录后重新生成 Session；生产环境强制 HTTPS 并设置 Secure Cookie |
| 原理和工作流程 | Cookie 中文乱码：Cookie 值不支持非 ASCII 字符，需 URLEncoder.encode 编码存储，读取时 URLDecoder.decode 解码。Session 固定攻击：攻击者先获取一个 JSESSIONID 诱导用户使用该 ID 登录，登录成功后攻击者可用同一 ID 冒充用户。防范措施：登录成功后调用 session.invalidate() 销毁旧 Session 再创建新 Session。Cookie 跨域问题：Domain 属性默认限制在当前域名，设置 Domain 为父域名可共享给子域名但无法跨顶级域名。HTTPS 证书问题：自签名证书浏览器不信任；证书过期需及时续期；证书链不完整需配置中间证书；混合内容浏览器会警告或阻止 |
| 缺点 | 乱码问题场景多样需逐一排查编码环节；Session 安全加固增加开发成本；Cookie 跨域限制导致集群架构设计复杂；HTTPS 证书管理增加运维成本 |

---

> [返回原文](./01-JavaWeb核心与HTTP协议.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)