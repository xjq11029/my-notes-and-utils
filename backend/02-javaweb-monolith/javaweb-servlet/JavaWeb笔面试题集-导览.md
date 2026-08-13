# JavaWeb 笔面试题集 导览

> 定位：五维框架浓缩提炼 JavaWeb笔面试题集.md 全部内容小节，快速查阅与复习。
> 用法：每道题目提取所考知识点生成纵向表格，需要查看原题与解析时跳转 [原文](./JavaWeb笔面试题集.md)。
> 前置知识：无

---

## 第一部分：选择题（共 20 题）

| 维度 | 内容 |
|------|------|
| 是什么 | 覆盖 HTTP 协议、Servlet、Tomcat 核心概念的 20 道单选题题型分类 |
| 能做什么 | 考查状态码、请求报文结构、请求方法、doGet 默认行为、Tomcat 端口、Cookie/Session 辨析、Servlet 生命周期、load-on-startup、Forward/Redirect、Filter 顺序、HTTPS 证书验证、Connector/Container 职责、ServletContext 功能、HTTP 报文分隔、GET/POST 缓存、持久连接、线程安全、Mapper 组件、FilterChain 特性、HTTPS 握手等知识点 |
| 怎么用 | 单选作答后对照解析，定位薄弱点回查导览 |
| 原理和工作流程 | 以四选一形式聚焦单一知识点辨析，解析给出正确项并解释错误项错因，覆盖基础至拔高难度梯度 |
| 缺点 | 单选无法考查综合应用；仅考辨析不考实操；题量有限覆盖不全 |

### 1. ★ HTTP 协议中，以下哪个状态码表示"请求成功"？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HTTP 状态码 200 OK 的含义 |
| 能做什么 | 200 表示请求成功；301 永久重定向；404 资源不存在；500 服务器内部错误 |
| 怎么用 | `resp.setStatus(200)`，客户端根据状态码决定后续处理逻辑 |
| 原理和工作流程 | 200 属于 2xx 成功类，表示服务端已成功处理请求并返回响应体。301 属于 3xx 重定向类浏览器缓存新地址。404 属于 4xx 客户端错误类。500 属于 5xx 服务端错误类 |
| 缺点 | 状态码语义有限无法精确表达业务级别成功或失败细节 |

### 2. ★ 以下哪项不是 HTTP 请求报文的一部分？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HTTP 请求报文与响应报文结构区别，状态码属于响应报文 |
| 能做什么 | 请求报文由请求行+请求头+空行+请求体组成；状态码属于响应状态行 |
| 怎么用 | 客户端构造请求报文的四个部分，服务端解析后返回含状态码的响应报文 |
| 原理和工作流程 | 请求报文结构：请求行（方法+URL+协议版本）+ 请求头 + 空行 + 请求体。响应报文结构：状态行（协议版本+状态码+描述）+ 响应头 + 空行 + 响应体。状态码仅出现在响应报文中 |
| 缺点 | GET 请求通常无请求体；部分代理和防火墙会修改请求头 |

### 3. ★ 用户在浏览器地址栏输入 URL 并回车，浏览器默认发送的 HTTP 请求方法是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查浏览器地址栏访问、超链接点击、表单 method="get" 时的默认请求方法 |
| 能做什么 | GET 用于获取资源，是浏览器默认的 HTTP 方法 |
| 怎么用 | 地址栏输入 URL 回车即发送 GET 请求，参数可通过 URL 查询字符串传递 |
| 原理和工作流程 | 浏览器解析 URL 构造 GET 请求报文，通过 DNS 解析域名获取 IP，建立 TCP 连接后发送。GET 请求参数通过 URL 查询字符串传递，可被浏览器缓存和历史记录保存。POST 需要表单提交或 AJAX 指定 |
| 缺点 | GET 请求参数暴露在 URL 不安全且长度受限；浏览器历史记录会保存 URL 含敏感参数 |

### 4. ★ Servlet 规范中，HttpServlet 的 doGet 和 doPost 方法默认行为是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HttpServlet 中 doGet/doPost 默认返回 405 Method Not Allowed |
| 能做什么 | 默认返回 405 提示客户端该 HTTP 方法不被支持，开发者需显式覆写 |
| 怎么用 | 继承 HttpServlet 后必须覆写 doGet 或 doPost，否则收到 405 错误 |
| 原理和工作流程 | HttpServlet 的 service 方法根据 request.getMethod() 分发到 doGet/doPost 等。这些 doXxx 方法的默认实现是调用 sendMethodNotAllowed 设置 405 状态码并返回错误信息 |
| 缺点 | 默认返回 405 不友好；新手容易忘记覆写导致接口不可用 |

### 5. ★ Tomcat 默认的 HTTP 监听端口是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Tomcat 默认 HTTP 端口 8080，HTTPS 端口 8443 |
| 能做什么 | 8080 是 Tomcat 默认 HTTP 端口，可通过 server.xml 或 server.port 修改 |
| 怎么用 | 在 server.xml 的 Connector 元素中配置 port 属性，默认 8080 |
| 原理和工作流程 | 使用非标准端口 8080 是因为 80 端口在 Linux 下需要 root 权限。开发环境通常使用 8080，生产环境通过 Nginx 反向代理到 80/443 |
| 缺点 | 8080 非标准端口需在 URL 中显式指定；与其它服务可能冲突 |

### 6. ★★ 以下关于 Cookie 和 Session 的说法，正确的是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Cookie 和 Session 的存储位置、大小限制、关联机制、超时时间等核心概念辨析 |
| 能做什么 | Cookie 存储在客户端约 4KB；Session 存储在服务端通过 JSESSIONID 关联；默认超时 30 分钟 |
| 怎么用 | 服务端创建 Session 生成 JSESSIONID 通过 Set-Cookie 下发，客户端后续请求自动携带 |
| 原理和工作流程 | Cookie 存储客户端（浏览器）约 4KB。Session 存储服务端通过 Cookie 中 JSESSIONID 关联。Session 默认超时 30 分钟。Session 依赖 Cookie 传递 JSESSIONID |
| 缺点 | Cookie 大小受限且不安全；Session 依赖 Cookie 禁用 Cookie 需 URL 重写 |

### 7. ★★ Servlet 生命周期中，init 方法被调用的次数是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Servlet 生命周期中 init 仅调用一次 |
| 能做什么 | init 实例化后调用一次完成初始化；service 每次请求调用多次；destroy 销毁时调用一次 |
| 怎么用 | 覆写 init(ServletConfig) 或 init()，在方法中执行初始化逻辑 |
| 原理和工作流程 | init 仅调用一次，容器加载 Servlet 类并实例化后调用 init(ServletConfig)。GenericServlet 的 init(ServletConfig) 调用无参 init()。service 每次请求调用，destroy 容器关闭时调用一次。一个 Servlet 类型通常只有一个实例（单例） |
| 缺点 | init 仅调用一次，初始化失败导致 Servlet 不可用；单例模式下实例变量需保证线程安全 |

### 8. ★★ 在 web.xml 中配置 `<load-on-startup>1</load-on-startup>` 的作用是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 load-on-startup 控制 Servlet 在容器启动时加载，值越小优先级越高 |
| 能做什么 | 值为 0 或正数时启动时加载；负数或不配置时首次请求懒加载 |
| 怎么用 | web.xml：`<load-on-startup>1</load-on-startup>`；注解：`@WebServlet(loadOnStartup=1)` |
| 原理和工作流程 | 默认首次请求时初始化（懒加载），首次请求需等待 init 执行导致响应慢。配置 load-on-startup 后启动时初始化，值越小越先加载。适用于需要提前初始化的 Servlet |
| 缺点 | 启动时加载过多 Servlet 导致容器启动变慢；值冲突时加载顺序不确定 |

### 9. ★★ 请求转发（Forward）和重定向（Redirect）的区别，以下说法错误的是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Forward 和 Redirect 在地址栏、请求次数、跳转范围、数据传递方面的区别 |
| 能做什么 | Forward 服务端内部跳转只能跳转应用内；Redirect 客户端跳转可跳转任意 URL |
| 怎么用 | Forward：`req.getRequestDispatcher("/target").forward(req, resp)`；Redirect：`resp.sendRedirect("/target")` |
| 原理和工作流程 | Forward 地址栏不变一次请求只能跳转应用内。Redirect 地址栏变为新 URL 两次请求可跳转任意 URL。Forward 可共享请求属性，Redirect 丢失请求数据。错误说法 C：Forward 不能跳转到外部 URL |
| 缺点 | Forward 只能跳转应用内；Redirect 丢失请求数据；Forward 地址栏不变用户困惑 |

### 10. ★★ 以下关于 Filter 执行顺序的说法，正确的是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Filter 按 web.xml 中 filter-mapping 声明顺序执行 |
| 能做什么 | web.xml 中按 filter-mapping 声明顺序；注解方式无法直接控制顺序；FilterRegistrationBean 可 setOrder |
| 怎么用 | web.xml 中按期望顺序声明 filter-mapping；Spring Boot 中 FilterRegistrationBean.setOrder() |
| 原理和工作流程 | web.xml 中 Filter 按 filter-mapping 声明顺序组成 FilterChain。注解 @WebFilter 无法控制顺序。FilterRegistrationBean 通过 setOrder 控制顺序。顺序错误导致功能异常 |
| 缺点 | 注解方式无法控制顺序需额外配置；注解和 web.xml 混合时顺序不确定 |

### 11. ★★ 客户端通过 HTTPS 访问网站时，浏览器首先验证的是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HTTPS 握手中浏览器验证服务器 SSL 证书的过程 |
| 能做什么 | 浏览器验证证书链、域名匹配、有效期、吊销状态，确认服务器身份 |
| 怎么用 | 服务端配置 CA 签发的 SSL 证书，浏览器自动验证 |
| 原理和工作流程 | 服务端在 ServerHello 后发送证书。浏览器验证：证书链追溯到根 CA、域名匹配、有效期、CRL/OCSP 吊销状态。验证通过后使用证书公钥加密预主密钥 |
| 缺点 | 自签名证书浏览器不信任；证书过期需及时续期；证书链不完整导致验证失败 |

### 12. ★★ Tomcat 中 Connector 和 Container 的关系，以下描述正确的是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Connector（网络通信+协议解析）和 Container（请求路由+业务处理）的职责分工 |
| 能做什么 | Connector 处理网络 I/O 和 HTTP 协议解析；Container 按层级路由请求到具体 Servlet |
| 怎么用 | 在 server.xml 中配置 Connector（端口、协议）和 Engine/Host/Context（路由规则） |
| 原理和工作流程 | Connector 包含 Endpoint+Processor+Adapter，负责网络通信和协议解析。Container 包含 Engine->Host->Context->Wrapper 四层，负责请求路由。一个 Service 可包含多个 Connector。Connector 接收请求后通过 CoyoteAdapter 适配为 Servlet API 调用 Container |
| 缺点 | 二者职责分离增加理解成本；协作依赖内部 API |

### 13. ★★ 以下哪个不是 ServletContext 的功能？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ServletContext（应用级）和 ServletConfig（Servlet 级）功能区分 |
| 能做什么 | ServletContext 提供应用级初始化参数、资源路径、请求转发器；ServletConfig 管理 Servlet 级初始化参数 |
| 怎么用 | ServletContext：`getServletContext().getInitParameter("key")`；ServletConfig：`getServletConfig().getInitParameter("key")` |
| 原理和工作流程 | ServletContext 功能：获取应用级初始化参数、getRealPath、getResource、getRequestDispatcher、全局属性共享。ServletConfig 功能：管理单个 Servlet 的 init-param 初始化参数。C 选项"管理 Servlet 的初始化参数"是 ServletConfig 功能 |
| 缺点 | 两个接口功能有重叠容易混淆；应用级属性全局共享需注意并发安全 |

### 14. ★★ HTTP 请求报文中，用于区分头部和请求体的标志是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HTTP 协议中空行（\r\n\r\n）作为头部和体部的分隔符 |
| 能做什么 | 空行（两个连续 CRLF）是 HTTP 协议中区分头部和体部的标准分隔符 |
| 怎么用 | 解析 HTTP 请求时按行读取直到遇到空行，空行后为请求体 |
| 原理和工作流程 | HTTP 协议规定请求行和请求头每行以 CRLF 结尾。所有头部结束后发送一个空行（\r\n\r\n）表示头部结束。空行后内容为请求体。Content-Type 描述体类型，Content-Length 描述体长度，都不是分隔符 |
| 缺点 | 仅靠空行分隔需要按行解析；部分代理可能修改 CRLF |

### 15. ★★ 以下关于 GET 和 POST 的说法，正确的是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 GET 可被缓存、POST 默认不缓存的核心区别 |
| 能做什么 | GET 可被浏览器和 CDN 缓存；POST 默认不缓存 |
| 怎么用 | GET 用于获取资源（查询操作），POST 用于提交数据（创建/修改操作） |
| 原理和工作流程 | GET 请求规范允许请求体但不推荐。POST 参数在请求体中。GET 可被浏览器和 CDN 缓存，POST 默认不缓存。GET 是幂等的，POST 是非幂等的 |
| 缺点 | 语义常被误用；幂等性是语义约定非协议强制 |

### 16. ★★★ 以下关于 HTTP/1.1 持久连接的说法，正确的是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HTTP/1.1 默认启用持久连接（Connection: keep-alive），一个 TCP 连接复用多个请求 |
| 能做什么 | HTTP/1.1 默认持久连接减少 TCP 握手开销；HTTP/1.0 默认每次新建连接 |
| 怎么用 | HTTP/1.1 默认 Connection: keep-alive 无需显式配置；可通过 Connection: close 关闭 |
| 原理和工作流程 | HTTP/1.0 默认每次请求新建连接。HTTP/1.1 默认持久连接，一个 TCP 连接可复用发送多个请求。持久连接在空闲超时后仍需关闭。减少 TCP 三次握手和四次挥手开销，但存在队头阻塞问题 |
| 缺点 | 队头阻塞导致一个慢请求阻塞后续请求；连接占用时间长导致服务端资源消耗 |

### 17. ★★★ Servlet 中，以下关于线程安全的说法，正确的是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Servlet 默认单例多线程，实例变量被所有线程共享存在线程安全问题 |
| 能做什么 | 不使用实例变量或用 ThreadLocal/synchronized；SingleThreadModel 已废弃 |
| 怎么用 | 不使用实例变量，将状态存储在线程安全容器，或使用 ThreadLocal，或使用 synchronized |
| 原理和工作流程 | Servlet 默认单例，一个实例服务所有请求。service 方法被多线程并发调用，实例变量被所有线程共享存在线程安全问题。方法内局部变量是线程安全的。SingleThreadModel 已废弃（Servlet 2.4），性能极差且不能真正保证线程安全 |
| 缺点 | 线程安全问题需开发者自行处理；ThreadLocal 使用不当导致内存泄漏；synchronized 影响并发性能 |

### 18. ★★★ Tomcat 中，以下哪个组件负责将 URL 映射到具体的 Servlet？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Tomcat 内部 Mapper 组件负责 URL 路由匹配 |
| 能做什么 | Mapper 根据请求 URL 匹配 Host -> Context -> Wrapper，是路由核心组件 |
| 怎么用 | Mapper 在 Tomcat 内部自动工作，根据 web.xml 和注解配置的 URL 映射规则匹配 |
| 原理和工作流程 | CoyoteAdapter 调用 Mapper.map()。Mapper 内部维护路由表，根据 Host 头匹配 Host，根据 URL 路径逐段匹配 Context 和 Wrapper。匹配规则：精确匹配 > 前缀匹配 > 扩展名匹配 > 默认匹配 |
| 缺点 | Mapper 路由规则复杂调试困难；URL 匹配规则多种优先级需理解；路由表更新有延迟 |

### 19. ★★★ 以下关于 FilterChain 的说法，错误的是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 FilterChain 由容器构建、按配置顺序执行、chain.doFilter 放行、顺序不可动态改变 |
| 能做什么 | FilterChain 在请求到达时由容器构建，按配置顺序执行，顺序在启动时确定不可动态改变 |
| 怎么用 | 在 doFilter 中调用 chain.doFilter(request, response) 放行 |
| 原理和工作流程 | FilterChain 由 StandardWrapperValve 在请求到达时构建。按 web.xml 中 filter-mapping 声明顺序或 FilterRegistrationBean 顺序执行。不调用 chain.doFilter 请求被拦截。FilterChain 顺序在应用启动时确定，无法在运行时动态改变 |
| 缺点 | 顺序无法动态改变限制运行时灵活性；忘记调用 chain.doFilter 导致请求被拦截 |

### 20. ★★★ 以下关于 HTTPS 握手过程的描述，正确的是？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HTTPS 握手中客户端用服务端公钥加密预主密钥发送给服务端 |
| 能做什么 | 客户端验证证书后用服务端公钥加密预主密钥，双方用随机数+预主密钥生成会话密钥 |
| 怎么用 | 服务端配置 SSL 证书，浏览器自动完成 TLS 握手 |
| 原理和工作流程 | 客户端不能直接使用对称密钥（尚未协商）。客户端用证书中公钥加密预主密钥发送给服务端，服务端用私钥解密。证书中包含服务端公钥。双方用客户端随机数+服务端随机数+预主密钥生成会话密钥，后续使用对称加密 |
| 缺点 | TLS 握手增加 1-2 个 RTT 延迟；旧版本 TLS 存在安全漏洞 |

---

## 第二部分：简答题（共 15 题）

| 维度 | 内容 |
|------|------|
| 是什么 | 覆盖 HTTP 协议、Servlet、Tomcat、Filter、Session/Cookie 核心原理的 15 道简答题题型分类 |
| 能做什么 | 考查 HTTP 协议特点、响应报文结构、Servlet 生命周期、GET/POST 区别、Cookie/Session 区别、Filter 原理、Forward/Redirect 区别、Tomcat 架构、ServletContext/Config 区别、301/302 区别、类加载机制、NIO 线程模型、HTTP/HTTPS 区别、表单重复提交方案、编码问题解决方案等综合表述能力 |
| 怎么用 | 简答作答后对照解析查漏补缺 |
| 原理和工作流程 | 以开放问答形式考查对机制的完整表述与流程梳理，解析给出核心要点和关键细节，覆盖基础至拔高难度 |
| 缺点 | 主观评分标准不一；仅考表述不考实操；题量有限 |

### 1. ★ 简述 HTTP 协议的主要特点

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HTTP 协议无状态、请求-响应模型、应用层协议、基于 TCP 等核心特性 |
| 能做什么 | 定义数据交换格式；通过 URL 定位资源；通过方法操作资源；通过状态码标识结果 |
| 怎么用 | 客户端发送请求报文，服务端返回响应报文 |
| 原理和工作流程 | 无状态 -- 协议本身不保存客户端状态。基于请求-响应模型 -- 客户端主动发起服务端被动响应。应用层协议 -- 建立在 TCP 之上端口 80。灵活 -- 可传输任意类型数据。简单快速 -- 请求方法简洁。支持 B/S 和 C/S 架构 |
| 缺点 | 无状态需额外机制维持会话；明文传输不安全；队头阻塞 |

### 2. ★ 简述 HTTP 响应报文的结构

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HTTP 响应报文状态行、响应头、空行、响应体四部分结构 |
| 能做什么 | 状态行返回协议版本、状态码和描述；响应头传递元信息；响应体承载实际内容 |
| 怎么用 | 服务端构造 `HTTP/1.1 200 OK` + 响应头 + 空行 + 响应体 |
| 原理和工作流程 | 状态行：协议版本+三位状态码+状态描述。响应头：Content-Type、Content-Length、Set-Cookie、Cache-Control、Location 等。空行：\r\n\r\n 分隔。响应体：HTML/JSON/XML/二进制等 |
| 缺点 | 状态码语义有限；大响应体需分块传输 |

### 3. ★ 简述 Servlet 的生命周期

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Servlet 从实例化到销毁的 init -> service -> destroy 三个阶段 |
| 能做什么 | init 初始化一次；service 处理每次请求；destroy 销毁一次 |
| 怎么用 | 覆写 init/doGet/doPost/destroy，通过 load-on-startup 控制加载时机 |
| 原理和工作流程 | 初始化：容器加载类并实例化，调用 init(ServletConfig) 一次。请求处理：每次请求调用 service，HttpServlet 分发到 doGet/doPost。销毁：容器关闭时调用 destroy() 一次。单例多线程需保证线程安全 |
| 缺点 | 单例多线程需自行处理并发安全；懒加载导致首次请求慢 |

### 4. ★★ 简述 GET 和 POST 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 GET 和 POST 在参数位置、长度限制、安全性、幂等性、缓存、语义方面的区别 |
| 能做什么 | GET 获取资源参数在 URL 可缓存幂等；POST 提交数据参数在请求体不缓存非幂等 |
| 怎么用 | GET：`/api/user?id=1`；POST：`/api/user` + JSON 请求体 |
| 原理和工作流程 | 参数位置：GET URL 查询字符串，POST 请求体。长度：GET 约 2KB，POST 无限制。安全性：GET 暴露 URL，POST 相对安全。幂等性：GET 幂等，POST 非幂等。缓存：GET 可缓存，POST 不缓存。语义：GET 获取资源，POST 提交数据 |
| 缺点 | GET 长度限制不统一；POST 明文传输仍不安全；语义常被误用 |

### 5. ★★ 简述 Cookie 和 Session 的区别与联系

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Cookie 客户端存储与 Session 服务端会话两种机制的对比及 Session 基于 Cookie 的关联 |
| 能做什么 | Cookie 客户端存小量数据约 4KB；Session 服务端存用户状态无限制；Session 通过 JSESSIONID 关联 Cookie |
| 怎么用 | Cookie：`resp.addCookie()`；Session：`req.getSession().setAttribute()` |
| 原理和工作流程 | 区别：存储位置、大小限制、安全性、生命周期、性能。联系：Session 依赖 Cookie 传递 JSESSIONID，服务端创建 Session 生成 JSESSIONID 通过 Set-Cookie 下发，客户端携带 Cookie 回传。浏览器禁用 Cookie 需 URL 重写 |
| 缺点 | Cookie 大小受限且不安全；Session 服务端内存消耗大；分布式需 Session 共享 |

### 6. ★★ 简述 Servlet 中 Filter 的工作原理

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Filter 基于责任链模式的拦截机制，在请求到达 Servlet 前后执行拦截处理 |
| 能做什么 | 统一编码、权限验证、日志记录、敏感词过滤、响应压缩、跨域处理 |
| 怎么用 | 实现 Filter 接口，覆写 init/doFilter/destroy，通过 @WebFilter 或 web.xml 配置 |
| 原理和工作流程 | 生命周期：init 容器启动时一次，doFilter 每次请求，destroy 关闭时一次。多个 Filter 按配置顺序组成 FilterChain，请求前置->Servlet->逆序后置，洋葱模型。执行顺序按 web.xml 中 filter-mapping 声明顺序或 FilterRegistrationBean.setOrder |
| 缺点 | 注解方式无法控制执行顺序；不依赖 Spring 容器获取 Bean 困难 |

### 7. ★★ 简述 Forward 和 Redirect 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Forward 服务端内部转发与 Redirect 客户端重定向在请求次数、地址栏、参数传递、跳转范围方面的区别 |
| 能做什么 | Forward 服务端内部转发共享请求属性；Redirect 实现外部跳转和防止表单重复提交 |
| 怎么用 | Forward：`req.getRequestDispatcher().forward()`；Redirect：`resp.sendRedirect()` |
| 原理和工作流程 | 请求次数：Forward 一次，Redirect 两次。地址栏：Forward 不变，Redirect 变为新 URL。参数传递：Forward setAttribute 共享，Redirect URL 参数或 Session。跳转范围：Forward 仅应用内，Redirect 任意 URL。效率：Forward 高。场景：Forward 内部跳转，Redirect PRG 模式 |
| 缺点 | Forward 地址栏不变用户困惑；Redirect 丢失请求数据；路径写法不同易混淆 |

### 8. ★★ 简述 Tomcat 的整体架构

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Tomcat Server -> Service ->（Connector + Engine）-> Host -> Context -> Wrapper 分层架构 |
| 能做什么 | Connector 处理网络通信和协议解析；Container 按层级路由请求到 Servlet |
| 怎么用 | 在 server.xml 中配置 Connector、Engine、Host、Context |
| 原理和工作流程 | Server 管理所有 Service。Service 组合 Connector 和 Engine。Connector 负责网络通信（Endpoint+Processor+Adapter）。Engine 顶级容器路由到 Host -> Context -> Wrapper。每层有 Pipeline-Valve 责任链。请求：Connector -> CoyoteAdapter -> Engine Pipeline -> Host Pipeline -> Context Pipeline -> Wrapper -> FilterChain -> Servlet |
| 缺点 | 架构层次多新手上手难；默认配置不适合高并发需调优 |

### 9. ★★ 简述 ServletContext 和 ServletConfig 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ServletContext（应用级上下文）和 ServletConfig（Servlet 级配置）的作用域和功能区别 |
| 能做什么 | ServletContext 应用级初始化参数、全局属性共享、资源路径；ServletConfig Servlet 级初始化参数 |
| 怎么用 | ServletContext：`getServletContext().getInitParameter()`；ServletConfig：`getServletConfig().getInitParameter()` |
| 原理和工作流程 | 作用域：ServletContext 应用级一个应用一个，生命周期等于应用。ServletConfig 每个 Servlet 一个，初始化时创建。功能：ServletContext 提供 context-param 初始化参数、getRealPath、getResource、setAttribute/getAttribute、getRequestDispatcher。ServletConfig 提供 init-param 初始化参数、getServletName、getServletContext |
| 缺点 | 两个接口功能有重叠容易混淆；ServletContext 属性全局共享需注意并发安全 |

### 10. ★★ 简述 HTTP 状态码 301 和 302 的区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 301 永久重定向浏览器缓存新地址与 302 临时重定向每次仍请求原地址的区别 |
| 能做什么 | 301 永久重定向缓存新地址后续直接访问；302 临时重定向每次重新请求原地址 |
| 怎么用 | 301：`resp.setStatus(301); resp.setHeader("Location", newUrl)`；302：`resp.sendRedirect(newUrl)` |
| 原理和工作流程 | 301 浏览器缓存重定向，后续访问原地址直接跳转新地址，搜索引擎转移权重。302 浏览器每次请求原地址，搜索引擎保留原地址权重。301 适用于域名更换、HTTP 迁移 HTTPS。302 适用于临时维护、PRG 模式 |
| 缺点 | 301 缓存期过长难以清除；302 被搜索引擎误用可能导致 URL 劫持 |

### 11. ★★★ 简述 Tomcat 的类加载机制

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Tomcat 自定义类加载器体系打破双亲委派，实现 Web 应用间类隔离 |
| 能做什么 | Web 应用间类隔离互不影响；共享公共类库；支持热加载和热部署 |
| 怎么用 | 公共类放 CATALINA_HOME/lib，应用私有类放 WEB-INF/lib |
| 原理和工作流程 | 类加载器层级：Bootstrap -> System -> Common（CATALINA_HOME/lib）-> Catalina（Tomcat 专用）-> Webapp（每个应用独立）。Webapp ClassLoader 打破双亲委派：先自己加载（WEB-INF），找不到再委托父类。默认不从父类缓存查找，确保不同应用同名类版本独立。热加载：WEB-INF 变化时废弃旧 WebappClassLoader 创建新的 |
| 缺点 | 层级多调试困难；打破双亲委派可能引起类找不到；类加载器泄漏导致 PermGen/Metaspace 溢出 |

### 12. ★★★ 简述 Tomcat 的 NIO 线程模型

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Tomcat NIO 模型基于 Selector 多路复用的三类线程（Acceptor/Poller/Worker）协作机制 |
| 能做什么 | Acceptor 接收连接；Poller 监听 I/O 事件；Worker 线程池处理业务；实现高并发低延迟 |
| 怎么用 | server.xml 配置 Connector protocol="HTTP/1.1"，调整 maxThreads、acceptCount |
| 原理和工作流程 | 三类线程：Acceptor（默认 1 个）循环 accept() 注册到 Poller Selector。Poller（每 CPU 1-2 个）循环 select() 监听就绪事件提交到 Worker。Worker 线程池（maxThreads 默认 200）读取 Socket 解析 HTTP 调用 Container 写回响应。关键参数：maxConnections=10000、acceptCount=100、maxThreads=200 |
| 缺点 | 参数调优需根据业务场景定制；线程数设置不当导致资源浪费或瓶颈 |

### 13. ★★★ 简述 HTTP 和 HTTPS 的主要区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HTTP 明文传输与 HTTPS 加密传输在安全性、端口、证书、连接、性能方面的区别 |
| 能做什么 | HTTP 明文传输端口 80；HTTPS 基于 TLS 加密端口 443 需 CA 证书 |
| 怎么用 | HTTP：`http://domain.com`；HTTPS：`https://domain.com` 需配置 SSL 证书 |
| 原理和工作流程 | 安全性：HTTP 明文可窃听篡改，HTTPS TLS 加密防窃听篡改。端口：HTTP 80，HTTPS 443。证书：HTTP 不需要，HTTPS 需要 CA 签发证书。连接：HTTP 直接 TCP，HTTPS 增加 TLS 握手。性能：HTTP 无加密开销，HTTPS 有握手延迟和加解密开销。HTTP/2 仅支持 HTTPS。SEO：HTTPS 有排名加权 |
| 缺点 | HTTPS 证书有费用和有效期；TLS 握手增加延迟；旧设备可能不支持现代 TLS |

### 14. ★★★ 简述如何防止表单重复提交

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Post-Redirect-Get 模式、Token 机制、前端防抖三种表单重复提交防护方案 |
| 能做什么 | 防止刷新重复提交；防止多次点击；防止浏览器后退重新提交 |
| 怎么用 | PRG：POST 处理后 Redirect 到结果页；Token：表单隐藏 Token 服务端校验一次性 |
| 原理和工作流程 | PRG 模式：POST 处理完成后 Redirect 到 GET 结果页，用户刷新时刷新 GET 而非 POST。Token 机制：服务端生成唯一 Token 存入 Session 和表单隐藏域，提交时校验后删除 Token，重复提交时 Token 不存在被拒绝。前端控制：提交后禁用按钮或防抖节流。推荐组合使用 PRG + Token |
| 缺点 | PRG 增加一次请求；Token 增加服务端存储和校验开销；前端控制可被绕过 |

### 15. ★★★ 简述 Web 应用中常见的编码问题及解决方案

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Web 应用中文乱码的成因和四层解决方案（Tomcat + Filter + 页面 + 数据库） |
| 能做什么 | 解决 GET/POST 乱码；确保响应不乱码；确保数据库读写不乱码 |
| 怎么用 | Tomcat：URIEncoding="UTF-8"；Filter：request.setCharacterEncoding；页面：charset=UTF-8；数据库：characterEncoding=utf-8 |
| 原理和工作流程 | 乱码根因：字符在不同环节使用不同编码导致解码错误。四层方案：1. Tomcat 层 URIEncoding="UTF-8" 解决 GET 乱码。2. Filter 层 setCharacterEncoding 解决 POST 乱码和响应编码。3. 页面层 JSP pageEncoding 和 HTML meta charset。4. 数据库层 JDBC URL characterEncoding=utf-8 和 MySQL utf8mb4 |
| 缺点 | 需同时配置多个环节遗漏一处即乱码；各服务器默认编码不一致；历史代码编码处理不统一 |

---

## 第三部分：场景设计题（共 3 题）

| 维度 | 内容 |
|------|------|
| 是什么 | 考查登录认证方案、文件上传服务、API 限流方案三道综合场景设计题 |
| 能做什么 | 设计 Filter + Session + Cookie 的登录认证；设计 @MultipartConfig 文件上传；设计滑动窗口 API 限流 |
| 怎么用 | 场景一：AuthFilter 白名单+Session 校验+记住我 Cookie+AJAX 区分。场景二：@MultipartConfig 大小限制+类型校验+UUID 重命名+路径穿越防护。场景三：RateLimitFilter 滑动窗口+Redis 计数+429 响应+可配置规则 |
| 原理和工作流程 | 场景题以实际业务场景为背景，考查综合运用 Filter、Servlet、Session、Cookie、文件上传、限流算法等知识解决实际问题的能力。每道题需给出完整方案，包括组件设计、配置方式、核心流程、安全考虑和集群扩展 |
| 缺点 | 主观评分标准不一；部分方案（如上传进度）需第三方库支持；集群方案增加系统复杂度 |

### 场景题 1：设计一个统一的登录认证方案

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 AuthFilter + Session + Cookie 实现统一登录认证，含白名单、重定向回跳、记住我、AJAX 区分 |
| 能做什么 | 未登录拦截跳转登录页；登录后跳转回原页面；记住我 7 天免登录；AJAX 返回 JSON 格式错误 |
| 怎么用 | AuthFilter 拦截所有请求，白名单放行，Session 校验登录状态，Cookie 实现记住我 |
| 原理和工作流程 | AuthFilter 拦截所有请求（urlPatterns="/*"），init 初始化白名单。doFilter 中获取 Session 中 user 属性判断登录状态。若未登录检查 Cookie 中 remember_token 自动登录。均无效时判断 AJAX 请求返回 JSON 401，页面请求重定向到登录页。登录成功从 Session 取出 redirect_url 跳转。记住我：登录成功生成 UUID token 存入 Cookie（Max-Age=7天）和数据库 |
| 缺点 | 白名单路径硬编码；记住我 token 存数据库增加查询开销；AJAX 和页面请求处理逻辑需区分 |

### 场景题 2：设计一个文件上传服务

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 @MultipartConfig 实现文件上传服务，含大小限制、类型校验、UUID 重命名、路径穿越防护、进度反馈 |
| 能做什么 | 限制 50MB 单文件；校验图片和文档类型；UUID 重命名防冲突；防止路径穿越；返回访问 URL |
| 怎么用 | @MultipartConfig 配置大小限制，Part API 获取文件信息，白名单校验类型，UUID 重命名保存 |
| 原理和工作流程 | Servlet 配置 @MultipartConfig(maxFileSize=50MB, maxRequestSize=55MB)。类型校验：白名单 MIME 类型和扩展名双重校验。安全防护：过滤 ../ 和 ..\\ 路径穿越字符，使用 FilenameUtils.getName() 仅保留文件名。保存：UUID + 原始扩展名，按日期分子目录。返回 URL：拼接访问 URL 返回客户端。进度反馈：标准 Servlet 不支持，需 Apache Commons FileUpload 或前端分片上传 |
| 缺点 | 标准 Servlet 不支持上传进度；MIME 类型可被伪造需结合魔数校验；大文件需分片和断点续传 |

### 场景题 3：设计一个 API 限流方案

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 RateLimitFilter 实现 API 限流，含滑动窗口算法、配置化规则、429 响应、Redis 集中式限流 |
| 能做什么 | 每个 IP 每分钟限流 100 次；超过限制返回 429；规则可配置化；支持集群环境 |
| 怎么用 | RateLimitFilter 拦截 API 请求，根据 IP 和 URL 查询限流计数，判断是否超限 |
| 原理和工作流程 | 算法：滑动窗口使用 Redis ZSET 存储请求时间戳，每次请求清理过期记录并计数。Filter 实现：从 request.getRemoteAddr() 获取 IP，结合请求路径匹配限流规则。规则配置：properties 文件配置 `/api/order=50`、`default=100`。超限处理：返回 429 状态码 + Retry-After 响应头 + JSON 错误信息。集群方案：单机 ConcurrentHashMap，集群 Redis 集中存储计数 + Lua 脚本保证原子性（INCR + EXPIRE） |
| 缺点 | Redis 方案增加网络开销和依赖；单机内存方案重启丢失计数；IP 可能被代理和 NAT 共享导致误限 |

---

> [返回原文](./JavaWeb笔面试题集.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)