# Web 核心与 Servlet 基础 导览

> 定位：五维框架浓缩提炼 06-Web核心与Servlet基础.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./06-Web核心与Servlet基础.md)。
> 前置知识：[面向对象基础](../../01-java-basics/java-core/05-面向对象基础-导览.md)、[网络编程](../../01-java-basics/java-core/11-网络编程-导览.md)

---

## 一、核心概念

### 1.1 Web 发展历程

| 维度 | 内容 |
|------|------|
| 是什么 | Web 技术从静态页面到动态框架的四个演进阶段（静态 Web、动态 Web、Java Web、框架时代） |
| 能做什么 | 静态 Web 用 CGI 处理固定内容；动态 Web 服务端生成页面；Java Web 基于规范跨平台；框架时代注解驱动内嵌容器 |
| 怎么用 | 静态：HTML+CGI；动态：JSP/PHP；Java Web：Servlet/JSP；框架：Spring MVC/Spring Boot |
| 原理和工作流程 | 静态 Web 阶段页面内容固定，CGI 每次请求创建进程开销大。动态 Web 阶段服务端根据请求动态生成页面并与数据库交互。Java Web 阶段基于 Servlet 规范实现跨平台企业级应用。框架时代以 Spring MVC 和 Spring Boot 为代表，采用约定优于配置、注解驱动、内嵌容器的方式，大幅降低开发与部署成本。每个阶段都在前阶段基础上提升开发效率与运行性能 |
| 缺点 | CGI 进程模型开销大无法高并发；JSP 脚本与 HTML 混杂难维护；Servlet API 偏底层 boilerplate 多；框架抽象层多对新手不透明 |

### 1.2 HTTP 协议

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 一种无状态、基于请求-响应模型的应用层协议，默认端口 80（HTTPS 为 443） |
| 能做什么 | 定义请求行/头/体结构；定义状态行/头/体结构；通过状态码标识处理结果；支持 GET/POST 等方法 |
| 怎么用 | 请求：`POST /api/user HTTP/1.1` + 头 + 体；响应：`HTTP/1.1 200 OK` + 头 + 体 |
| 原理和工作流程 | HTTP 请求由请求行（方法 URL 协议版本）、请求头（Host、Content-Type 等）、请求体（GET 通常无）组成。响应由状态行（协议版本 状态码 描述）、响应头、响应体组成。状态码分五类：2xx 成功、3xx 重定向（301 永久/302 临时/304 缓存）、4xx 客户端错误（400 参数错/401 未认证/403 无权限/404 不存在）、5xx 服务端错误（500/502/503）。GET 参数在 URL 有长度限制可缓存幂等，POST 参数在请求体无长度限制不缓存非幂等。协议本身无状态，需 Cookie/Session 或 Token 维持用户状态 |
| 缺点 | 无状态导致需额外机制维持会话；明文传输不安全需 HTTPS；GET 参数暴露在 URL；状态码语义有限难以表达复杂业务错误 |

### 1.3 Servlet

| 维度 | 内容 |
|------|------|
| 是什么 | Servlet Java EE 规范中处理 Web 请求的服务器端组件，本质是 javax.servlet.Servlet 接口，运行在 Servlet 容器中 |
| 能做什么 | 接收 HTTP 请求并生成响应；通过生命周期方法管理实例；按 HTTP 方法分发到 doGet/doPost 等 |
| 怎么用 | `public class UserServlet extends HttpServlet { protected void doGet(req, resp) { ... } }` |
| 原理和工作流程 | Servlet 生命周期含三阶段：init(ServletConfig) 在加载时调用一次完成初始化，service(ServletRequest,ServletResponse) 在每次请求时调用处理请求，destroy() 在容器关闭时调用一次释放资源。体系结构为 Servlet 接口 -> GenericServlet 抽象类（与协议无关，提供通用 init/destroy）-> HttpServlet 抽象类（覆写 service 按 HTTP 方法分发到 doGet/doPost/doPut/doDelete）-> 自定义 Servlet。默认懒加载，首次请求时初始化，可通过 load-on-startup 设为启动时初始化 |
| 缺点 | API 偏底层 boilerplate 多；一个 Servlet 通常只处理一类请求导致类爆炸；配置繁琐需 web.xml 或注解；并发安全需自行处理实例变量 |

### 1.4 Tomcat

| 维度 | 内容 |
|------|------|
| 是什么 | Tomcat 由 Connector（连接器）和 Container（容器）两大核心组成的开源 Servlet 容器实现 |
| 能做什么 | 处理网络 I/O 与协议解析；按层级路由请求；管理 Web 应用生命周期；支持 BIO/NIO/APR 线程模型 |
| 怎么用 | `bin/startup.sh` 启动；`conf/server.xml` 配置；`webapps/` 部署应用 |
| 原理和工作流程 | Tomcat 架构为 Server -> Service ->（Connector + Engine）。Connector 处理网络 I/O 和协议解析（HTTP/1.1 端口 8080、AJP 端口 8009）。Engine 是容器负责请求路由，层级为 Engine -> Host（虚拟主机）-> Context（Web 应用）-> Wrapper（单个 Servlet）。线程模型有三种：BIO 阻塞 I/O 一请求一线程并发低（8.5 已移除），NIO 基于 Selector 多路复用少量线程处理大量连接是默认模型，APR 调用 native 库直接操作系统 I/O 性能最高但需安装 native 库。目录结构含 bin（脚本）、conf（配置）、lib（JAR）、logs（日志）、webapps（部署）、work（JSP 编译产物） |
| 缺点 | BIO 并发低已淘汰；APR 部署复杂需 native 库；默认配置不适合高并发需调优；单机部署无集群能力需额外方案 |

---

## 二、底层原理

### 2.1 Servlet 请求处理流程

| 维度 | 内容 |
|------|------|
| 是什么 | 一个 HTTP 请求在 Tomcat 中从 Connector 接收到 Servlet 执行的完整流转路径 |
| 能做什么 | 网络接收与协议解析；Coyote 与 Servlet API 适配；按 URL 匹配容器层级；执行 FilterChain 责任链 |
| 怎么用 | 请求 -> Connector -> CoyoteAdapter -> Mapper -> Pipeline-Valve -> FilterChain -> Servlet |
| 原理和工作流程 | 1. 客户端发送 HTTP 请求。2. Connector 的 NIO Endpoint 监听端口接收请求，封装为 CoyoteRequest/CoyoteResponse。3. CoyoteAdapter 将 Coyote 对象适配为 HttpServletRequest/Response。4. Mapper 根据 URL 匹配到 Host -> Context -> Wrapper。5. Engine 的 Pipeline 执行 Valve 链。6. Host 的 Pipeline 执行 Valve 链。7. Context 的 Pipeline 执行 Valve 链。8. Wrapper 调用 FilterChain 执行所有匹配的 Filter。9. 最终调用 Servlet 的 service() 分发到 doGet()/doPost()。核心是 Tomcat 使用 Pipeline-Valve 责任链模式实现容器组件间请求传递，每个层级都有自己的 Pipeline |
| 缺点 | 流转链路长排查问题需逐层定位；Pipeline-Valve 责任链增加理解成本；FilterChain 顺序依赖配置易出错；大量内部对象转换有性能开销 |

### 2.2 HttpServletRequest / HttpServletResponse 核心 API

| 维度 | 内容 |
|------|------|
| 是什么 | Servlet 规范定义的用于读取请求数据和写入响应数据的两个核心接口及其方法集合 |
| 能做什么 | 读取请求参数/头/方法/体/Cookie/Session；设置响应状态码/头/输出流；请求转发与重定向 |
| 怎么用 | 请求：`req.getParameter("name")`、`req.getHeader("Host")`；响应：`resp.setStatus(200)`、`resp.getWriter().write("ok")` |
| 原理和工作流程 | HttpServletRequest 提供获取请求信息的方法：getParameter 获取表单/查询参数，getHeader 获取请求头，getMethod 获取请求方法，getInputStream 获取请求体输入流（读 JSON），getCookies 获取 Cookie，getSession 获取或创建 HttpSession，setAttribute 在请求作用域存数据，getRequestDispatcher 获取请求转发器。HttpServletResponse 提供设置响应的方法：setStatus 设置状态码，setHeader 设置响应头，getOutputStream 获取字节输出流（文件下载），getWriter 获取字符输出流（文本响应），addCookie 添加 Cookie，sendRedirect 重定向。两个对象由容器在请求到达时创建并传入 Servlet |
| 缺点 | API 基于 IO 流读取一次后无法重复读；请求参数需手动类型转换；响应写出后无法修改；异步处理需额外 API |

### 2.3 Filter 过滤器

| 维度 | 内容 |
|------|------|
| 是什么 | Filter 基于**责任链模式**实现的 Servlet 规范组件，在请求到达 Servlet 前和响应离开后执行拦截 |
| 能做什么 | 请求前置处理（编码、鉴权、日志）；响应后置处理；按声明顺序组成责任链；拦截所有请求含静态资源 |
| 怎么用 | `@WebFilter("/*") public class EncodingFilter implements Filter { public void doFilter(req, resp, chain) { chain.doFilter(req, resp); } }` |
| 原理和工作流程 | Filter 生命周期含 init(FilterConfig) 容器启动时调用一次、doFilter(Request,Response,Chain) 每次请求调用、destroy() 容器关闭时调用一次。执行顺序按 web.xml 中 filter-mapping 声明顺序，注解方式 @WebFilter 无法直接控制顺序，建议用 FilterRegistrationBean 或 @Order。请求进来按 Filter1 -> Filter2 -> Filter3 -> Servlet 顺序，响应出去按 Servlet -> Filter3 -> Filter2 -> Filter1 逆序，形成洋葱模型。每个 Filter 调用 chain.doFilter 放行到下一环节 |
| 缺点 | @WebFilter 注解无法控制执行顺序；与 Spring 容器解耦获取 Bean 需 ApplicationContext；只能拦截请求粒度无法细到方法；责任链过长影响性能 |

### 2.4 Listener 监听器

| 维度 | 内容 |
|------|------|
| 是什么 | Listener 基于**观察者模式**的 Servlet 规范组件，监听 Web 应用中特定事件的发生 |
| 能做什么 | 监听应用启动销毁初始化全局资源；监听 Session 创建销毁统计在线人数；监听请求创建记录日志；监听作用域属性增删改 |
| 怎么用 | `@WebListener public class AppContextListener implements ServletContextListener { public void contextInitialized(sce) { ... } }` |
| 原理和工作流程 | Listener 基于观察者模式，容器在特定事件发生时回调注册的监听器。ServletContextListener 在应用启动/销毁时触发，用于初始化全局资源、加载配置。HttpSessionListener 在 Session 创建/销毁时触发，用于统计在线人数。ServletRequestListener 在请求创建/销毁时触发，用于请求日志记录。ServletContextAttributeListener 监听应用作用域属性增删改。HttpSessionAttributeListener 监听 Session 属性增删改。监听器在容器启动时实例化并注册，事件发生时由容器回调对应方法 |
| 缺点 | 监听器过多导致启动变慢；监听逻辑与容器耦合；无法精确控制事件传播；异步事件处理需额外机制 |

### 2.5 JSP 到 Servlet 的编译过程

| 维度 | 内容 |
|------|------|
| 是什么 | JSP 由 Tomcat 的 Jasper 引擎编译为 Servlet 再执行的转换过程 |
| 能做什么 | 首次访问时解析 JSP；HTML 标签转 out.write()；JSP 脚本转 Java 代码；编译为 class 加载执行 |
| 怎么用 | 首次访问 .jsp 触发编译，产物存于 work/Catalina/localhost/项目名/org/apache/jsp/xxx_jsp.java |
| 原理和工作流程 | 第一次访问 JSP 页面时：1. Tomcat 检测到 .jsp 文件被访问。2. Jasper 引擎解析 JSP 文件，HTML 标签转为 out.write() 调用，JSP 脚本转为 Java 代码。3. 生成 Java 源文件存于 work 目录。4. 编译为 .class 文件。5. 加载并实例化 Servlet，执行 _jspService() 方法。6. 后续访问直接调用已编译的 Servlet，无需重新编译。JSP 修改后 Tomcat 默认自动重新编译（development=true），生产环境建议关闭以提升性能 |
| 缺点 | 首次访问编译耗时导致响应慢；编译产物占用磁盘；development=true 在生产环境有性能损耗；JSP 脚本与 HTML 混杂难维护已逐渐被前后端分离取代 |

### 2.6 Session vs Cookie

| 维度 | 内容 |
|------|------|
| 是什么 | Cookie 客户端存储机制与 Session 服务端会话机制两种状态保持方案的对比与协作 |
| 能做什么 | Cookie 客户端存键值对约 4KB；Session 服务端存用户状态无大小限制；Session 基于 Cookie 中 JSESSIONID 关联 |
| 怎么用 | Cookie：`resp.addCookie(new Cookie("k","v"))`；Session：`HttpSession s = req.getSession(); s.setAttribute("user", user);` |
| 原理和工作流程 | Cookie 存储在客户端浏览器，大小限制约 4KB，安全性低可被篡改，生命周期可通过 maxAge 设置。Session 存储在服务端，无大小限制受内存影响，安全性高，默认 30 分钟超时。Session 跟踪机制：1. 客户端首次请求，服务端创建 HttpSession 生成 JSESSIONID。2. 服务端通过 Set-Cookie 将 JSESSIONID 返回客户端。3. 客户端后续请求携带 JSESSIONID Cookie。4. 服务端根据 JSESSIONID 找到对应 Session。Tomcat 关闭时可将 Session 序列化到磁盘（SESSIONS.ser）重启后恢复 |
| 缺点 | Cookie 大小受限且不安全；Session 占用服务端内存；分布式环境需 Session 共享；Session 依赖 Cookie 禁用 Cookie 需 URL 重写 |

---

## 三、实战应用

### 3.1 手写 Servlet 完整示例

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 web.xml 配置和 Servlet 3.0+ 注解两种方式手写 Servlet 的完整开发示例 |
| 能做什么 | web.xml 方式声明 servlet 与 mapping；注解方式 @WebServlet 零配置；覆写 doGet/doPost 处理请求 |
| 怎么用 | 注解：`@WebServlet(urlPatterns="/user") public class UserServlet extends HttpServlet { ... }` |
| 原理和工作流程 | 方式一 web.xml 配置，通过 servlet 标签声明 servlet-name 和 servlet-class，通过 servlet-mapping 标签将 url-pattern 映射到 servlet-name，load-on-startup 控制启动时加载。方式二注解配置（Servlet 3.0+），在类上标注 @WebServlet 指定 name、urlPatterns、loadOnStartup，容器扫描注解自动注册。doGet 中通过 req.getParameter 获取参数，resp.setContentType 设置响应类型，resp.getWriter().write 输出 JSON。doPost 中通过 req.getReader 读取请求体解析 JSON。注解方式免除了 web.xml 配置，是现代开发推荐方式 |
| 缺点 | web.xml 配置繁琐易出错；手动拼接 JSON 字符串易产生注入和格式错误；一个 Servlet 对应一个 URL 导致类爆炸；缺乏参数绑定和类型转换需手动处理 |

### 3.2 Filter 实现统一编码过滤

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 Filter 在请求到达 Servlet 前统一设置请求和响应字符编码的实战示例 |
| 能做什么 | 统一设置请求编码；统一设置响应编码；设置 Content-Type；支持通过初始化参数配置编码 |
| 怎么用 | `request.setCharacterEncoding("UTF-8"); response.setContentType("application/json;charset=UTF-8"); chain.doFilter(request, response);` |
| 原理和工作流程 | EncodingFilter 实现 Filter 接口，init 方法从 FilterConfig 读取 encoding 初始化参数（默认 UTF-8）保存为成员变量。doFilter 方法中调用 request.setCharacterEncoding 设置请求体编码，response.setCharacterEncoding 设置响应编码，response.setContentType 设置 Content-Type 头，然后 chain.doFilter 放行到下一个 Filter 或 Servlet。配置 urlPatterns 为 /* 拦截所有请求，确保所有请求和响应都使用统一编码，避免中文乱码。destroy 方法用于清理资源 |
| 缺点 | 拦截所有请求含静态资源有性能开销；编码设置在请求体已读取后无效需前置；Filter 顺序需正确否则可能被覆盖；仅解决字符编码不解决其他乱码场景 |

### 3.3 Listener 实现应用启动初始化

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 ServletContextListener 在 Web 应用启动时初始化全局资源的实战示例 |
| 能做什么 | 应用启动时加载配置文件；初始化数据库连接池；将全局资源存入 ServletContext；应用销毁时释放资源 |
| 怎么用 | `@WebListener public class AppContextListener implements ServletContextListener { public void contextInitialized(sce) { sce.getServletContext().setAttribute("config", props); } }` |
| 原理和工作流程 | AppContextListener 实现 ServletContextListener 接口，标注 @WebListener 由容器自动注册。contextInitialized 在应用启动时由容器回调，读取 /WEB-INF/config.properties 配置文件加载为 Properties 对象，通过 sce.getServletContext().setAttribute 将配置存入应用作用域供全局访问，并初始化数据库连接池等全局资源。contextDestroyed 在应用销毁时回调，用于关闭连接池、清理资源。监听器在所有 Servlet 和 Filter 之前执行，确保资源在请求处理前就绪 |
| 缺点 | 启动初始化失败会导致应用无法启动；加载逻辑与容器生命周期耦合；异常处理不当会阻塞启动；全局资源存 ServletContext 缺乏类型安全 |

### 3.4 Tomcat 在 Spring Boot 中的内嵌启动

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 通过内嵌 Tomcat 实现 main 方法直接启动 Web 应用无需部署 WAR 包的机制 |
| 能做什么 | main 方法启动 Web 应用；自动创建并配置 Tomcat 实例；注册 DispatcherServlet；支持切换 Undertow/Jetty |
| 怎么用 | `@SpringBootApplication public class Application { public static void main(String[] args) { SpringApplication.run(Application.class, args); } }` |
| 原理和工作流程 | 1. SpringApplication.run() 启动。2. 创建 ServletWebServerApplicationContext。3. 通过 ServletWebServerFactory（TomcatServletWebServerFactory）创建 Tomcat 实例。4. 配置 Connector（端口、协议）。5. 注册 DispatcherServlet 为根 Servlet 映射 "/"。6. Tomcat 启动开始监听端口。切换内嵌容器时，在 spring-boot-starter-web 中排除 spring-boot-starter-tomcat，引入 spring-boot-starter-undertow 或 spring-boot-starter-jetty，Spring Boot 自动适配新容器无需修改业务代码 |
| 缺点 | 单进程单端口部署水平扩展需额外管理；内嵌容器调优参数不如独立 Tomcat 丰富；切换容器后部分 Tomcat 特有配置失效； fat jar 启动内存占用较高 |

---

## 四、常见面试题

### 1. GET 和 POST 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 两种最常用请求方法在参数位置、长度限制、安全性、幂等性、缓存等维度的对比 |
| 能做什么 | GET 获取资源参数在 URL 幂等可缓存；POST 提交数据参数在请求体非幂等不缓存 |
| 怎么用 | GET：`GET /api/user?name=zhangsan`；POST：`POST /api/user` + 请求体 |
| 原理和工作流程 | GET 参数通过 URL 查询字符串传递，有浏览器长度限制（约 2KB），可被浏览器缓存，幂等（多次请求结果相同）。POST 参数通过请求体传递，理论上无长度限制，默认不缓存，非幂等。本质区别是语义不同：GET 用于获取资源，POST 用于提交数据。GET 参数暴露在 URL 不安全，POST 相对安全但明文传输仍不安全需 HTTPS。GET 可被浏览器和 CDN 缓存提升性能，POST 默认不缓存 |
| 缺点 | GET 长度限制受浏览器约束不一致；POST 明文传输仍不安全；二者语义常被误用（用 GET 提交数据）；幂等性是语义约定非协议强制 |

### 2. Servlet 的生命周期？

| 维度 | 内容 |
|------|------|
| 是什么 | Servlet 从实例化到销毁经历的初始化、处理请求、销毁三个阶段及对应方法调用机制 |
| 能做什么 | init 初始化加载资源；service 处理每次请求；destroy 释放资源；支持懒加载与启动时加载 |
| 怎么用 | `init(ServletConfig)` 加载时一次；`service(req,resp)` 每次请求；`destroy()` 关闭时一次 |
| 原理和工作流程 | Servlet 经历初始化（init）、处理请求（service）、销毁（destroy）三个阶段。init 在 Servlet 被加载时调用一次完成初始化，可通过 ServletConfig 获取初始化参数。service 在每次请求时调用，HttpServlet 中根据 HTTP 方法分发到 doGet/doPost 等。destroy 在容器关闭或卸载时调用一次释放资源。默认懒加载，首次请求时初始化，可通过 load-on-startup 设为启动时初始化。整个容器中一个 Servlet 类型通常只有一个实例（单例），service 方法被多线程并发调用 |
| 缺点 | 单例多线程需自行处理并发安全；init 失败导致 Servlet 不可用；懒加载导致首次请求慢；destroy 时长影响容器关闭速度 |

### 3. Filter 和 Interceptor（拦截器）的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | Filter（Servlet 规范）与 Interceptor（Spring 规范）两种拦截机制在规范、依赖、执行范围、执行顺序上的对比 |
| 能做什么 | Filter 拦截所有请求含静态资源不依赖 Spring；Interceptor 只拦 Controller 请求可注入 Bean |
| 怎么用 | Filter：`implements Filter`；Interceptor：`implements HandlerInterceptor` 注册到 WebMvcConfigurer |
| 原理和工作流程 | Filter 是 Servlet 规范组件由 Servlet 容器管理，作用于所有请求含静态资源，在请求进入 Servlet 前后执行，不依赖 Spring 容器获取 Bean 需 ApplicationContext。Interceptor 是 Spring 框架组件由 Spring 容器管理，仅作用于 Spring MVC 处理的请求（Controller），在 Controller 方法前后和视图渲染后执行（preHandle/postHandle/afterCompletion），可直接注入 Bean。执行顺序为 Filter -> Interceptor -> Controller。Filter 粒度粗拦截所有请求，Interceptor 粒度细只拦 Controller |
| 缺点 | Filter 获取 Spring Bean 困难；Interceptor 无法拦截非 Controller 请求；二者执行顺序混合时排查复杂；Filter 与 Interceptor 职责重叠易混淆 |

### 4. Session 和 Cookie 的区别和联系？

| 维度 | 内容 |
|------|------|
| 是什么 | Cookie 客户端存储与 Session 服务端会话两种机制的区别及 Session 基于 Cookie 实现的关联 |
| 能做什么 | Cookie 客户端存小量数据约 4KB；Session 服务端存用户状态无限制；Session 通过 JSESSIONID 关联 Cookie |
| 怎么用 | Cookie：`resp.addCookie(new Cookie("k","v"))`；Session：`req.getSession().setAttribute("user",user)` |
| 原理和工作流程 | Cookie 存储在客户端浏览器，大小限制约 4KB，安全性低可被篡改。Session 存储在服务端，无大小限制受内存影响，安全性高。Session 基于 Cookie 实现：服务端创建 Session 时生成 JSESSIONID，通过 Set-Cookie 下发到客户端，客户端后续请求携带此 ID，服务端据此找到对应 Session。Cookie 有大小限制且安全性低，Session 安全性高但消耗服务端内存。二者协作完成无状态 HTTP 上的用户状态保持 |
| 缺点 | Cookie 大小受限且不安全；Session 占用服务端内存；分布式需 Session 共享；浏览器禁用 Cookie 需 URL 重写 |

### 5. Tomcat 的 BIO、NIO、APR 三种线程模型有什么区别？

| 维度 | 内容 |
|------|------|
| 是什么 | Tomcat 三种网络 I/O 线程模型在 I/O 方式、并发能力、性能、部署复杂度上的对比 |
| 能做什么 | BIO 阻塞 I/O 一请求一线程；NIO 多路复用少量线程处理大量连接；APR native 库直接操作系统 I/O |
| 怎么用 | NIO 默认无需配置；APR 需安装 native 库；BIO 已在 8.5 移除 |
| 原理和工作流程 | BIO 是阻塞 I/O，每个请求独占一个线程，请求处理期间线程阻塞，并发量低，Tomcat 8.5 已移除。NIO 是非阻塞 I/O，基于 Selector 多路复用，用少量线程处理大量连接，线程在 I/O 等待时可处理其他请求，是 Spring Boot 默认模型，适合高并发。APR 使用 native 库直接调用操作系统 I/O，性能最高，但需要安装 native 库部署较复杂，适合极致性能场景。三者性能从低到高：BIO < NIO < APR，NIO 在性能与易用性间平衡是主流选择 |
| 缺点 | BIO 并发低已淘汰；APR 部署复杂需 native 库跨平台性差；NIO 编程复杂度高（由 Tomcat 封装）；模型选择需权衡性能与运维成本 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | Web 与 Servlet 开发中中文乱码、Filter 顺序、Session 丢失、重定向丢数据等高频问题汇总 |
| 能做什么 | 解决 GET/POST 中文乱码；控制 Filter 执行顺序；防止 Session 丢失；避免重定向丢 POST 数据；处理端口占用 |
| 怎么用 | `server.tomcat.uri-encoding=UTF-8`；`FilterRegistrationBean.setOrder()`；`server.servlet.session.timeout` |
| 原理和工作流程 | GET 请求中文乱码因 Tomcat URI 编码默认 ISO-8859-1，需配置 uri-encoding=UTF-8 或 URLEncoder.encode。POST 请求中文乱码因请求体未设置编码，需在 doPost 首行 request.setCharacterEncoding("UTF-8") 或用 EncodingFilter。Filter 执行顺序不确定因 @WebFilter 无法控制顺序，需用 FilterRegistrationBean 注册并 setOrder。Session 丢失因超时时间过短或负载均衡未做共享，需调大 timeout 或用 Redis Session 共享。302 重定向丢 POST 数据因标准要求重定向用 GET，需用 307 保留方法或 Forward 转发。内嵌 Tomcat 端口被占用需修改 server.port 或终止占用进程 |
| 缺点 | 乱码问题场景多样需逐一排查；Filter 顺序控制增加配置复杂度；Redis Session 共享依赖 Redis 可用性；307 兼容性需验证；端口冲突需运维介入 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./06-Web核心与Servlet基础.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)