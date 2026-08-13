# Request 与 Response & Filter 监听器 导览

> 定位：五维框架浓缩提炼 03-Request与Response&Filter监听器.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./03-Request与Response&Filter监听器.md)。
> 前置知识：无

---

## 一、核心概念

### 1.1 Filter 过滤器核心概念

| 维度 | 内容 |
|------|------|
| 是什么 | Filter 是 Servlet 规范中基于责任链模式的拦截组件，在请求到达 Servlet 之前和响应离开 Servlet 之后执行拦截处理 |
| 能做什么 | 统一编码处理；权限验证与登录检查；请求日志记录；敏感词过滤；响应压缩；跨域处理 |
| 怎么用 | 实现 `javax.servlet.Filter` 接口，覆写 init/doFilter/destroy 方法，通过 @WebFilter 注解或 web.xml 配置拦截路径 |
| 原理和工作流程 | Filter 在 Servlet 规范中定义，由 Servlet 容器管理生命周期。每个 Filter 实现 init(FilterConfig)、doFilter、destroy() 三个方法。多个 Filter 按配置顺序组成 FilterChain，请求依次经过各 Filter 的前置逻辑，最终到达 Servlet，响应沿逆序经过各 Filter 的后置逻辑。Filter 可拦截所有请求包括静态资源，执行顺序在 web.xml 中按 filter-mapping 声明顺序，注解方式可通过 FilterRegistrationBean 或 @Order 控制 |
| 缺点 | @WebFilter 注解无法直接控制执行顺序；不依赖 Spring 容器获取 Bean 需 ApplicationContext；只能拦截请求粒度无法细到方法级别；责任链过长影响性能 |

### 1.2 FilterChain 执行流程

| 维度 | 内容 |
|------|------|
| 是什么 | FilterChain 是 Filter 的有序集合，由 Servlet 容器构建，按顺序调用各 Filter 的 doFilter 方法，形成洋葱模型拦截链 |
| 能做什么 | 按配置顺序依次执行 Filter 前置逻辑；调用 chain.doFilter 放行到下一个 Filter 或 Servlet；在响应返回时逆序执行 Filter 后置逻辑 |
| 怎么用 | 在 doFilter 方法中调用 `chain.doFilter(request, response)` 放行，前置逻辑写在 doFilter 调用之前，后置逻辑写在之后 |
| 原理和工作流程 | FilterChain 由 Tomcat 的 ApplicationFilterChain 实现，内部维护 Filter 数组和当前位置指针。执行流程：1. 判断当前位置是否小于 Filter 数量，若是则取下一个 Filter 调用其 doFilter 方法。2. Filter 的 doFilter 中先执行前置逻辑，然后调用 chain.doFilter 将控制权交回 FilterChain。3. FilterChain 继续调用下一个 Filter。4. 所有 Filter 执行完毕后调用 Servlet 的 service 方法。5. Servlet 处理完成后调用栈逐层返回，各 Filter 执行后置逻辑。执行顺序：请求 Filter1 -> Filter2 -> Filter3 -> Servlet；响应 Servlet -> Filter3 -> Filter2 -> Filter1 |
| 缺点 | Filter 执行顺序依赖配置顺序易出错；chain.doFilter 忘记调用导致请求被拦截不继续；后置逻辑中 response 可能已被提交无法修改；FilterChain 构建依赖 URL 匹配规则 |

### 1.3 Listener 监听器核心概念

| 维度 | 内容 |
|------|------|
| 是什么 | Listener 是 Servlet 规范中基于观察者模式的监听组件，监听 Web 应用中特定事件（应用启动、Session 创建、属性变更等）的发生并执行回调 |
| 能做什么 | 应用启动时初始化全局资源；统计在线人数；记录请求日志；监听 Session 和属性变更；加载全局配置 |
| 怎么用 | 实现对应的 Listener 接口（如 ServletContextListener），标注 @WebListener 注解或在 web.xml 中配置，容器自动注册并在事件发生时回调 |
| 原理和工作流程 | Listener 基于观察者模式，Servlet 容器在特定事件发生时遍历已注册的监听器并调用对应回调方法。主要监听器类型：ServletContextListener（应用启动/销毁时触发）、HttpSessionListener（Session 创建/销毁时触发）、ServletRequestListener（请求创建/销毁时触发）、属性变更监听器（作用域属性增删改）、对象绑定监听器（HttpSessionBindingListener、HttpSessionActivationListener） |
| 缺点 | 监听器过多导致启动变慢；监听逻辑与容器生命周期耦合；无法精确控制事件传播；异步事件处理需额外机制 |

### 1.4 Session 钝化与活化

| 维度 | 内容 |
|------|------|
| 是什么 | Session 钝化是将 Session 对象从内存序列化到磁盘的过程，活化是将磁盘上的 Session 反序列化回内存的过程 |
| 能做什么 | 节省内存资源将不活跃的 Session 持久化到磁盘；服务器重启后恢复 Session 状态；实现 Session 跨服务器迁移 |
| 怎么用 | 实体类实现 Serializable 接口并实现 HttpSessionActivationListener；在 context.xml 中配置 Manager 的 maxIdleSwap 和 directory 参数 |
| 原理和工作流程 | Tomcat 的 PersistentManager 管理 Session 钝化与活化。当 Session 空闲时间超过 maxIdleSwap 时，Manager 将 Session 对象及其属性序列化到指定目录。Session 属性对象必须实现 Serializable 接口。实现 HttpSessionActivationListener 接口的类在钝化前收到 sessionWillPassivate 回调（释放不可序列化资源），活化后收到 sessionDidActivate 回调（重建资源）。钝化到磁盘的 Session 文件在 Session 过期后被删除 |
| 缺点 | 属性对象必须实现 Serializable 增加约束；钝化活化有 I/O 开销影响性能；不可序列化对象的释放和重建需自行处理；PersistentManager 配置复杂默认不启用 |

### 1.5 文件上传与下载

| 维度 | 内容 |
|------|------|
| 是什么 | 文件上传是客户端通过 multipart/form-data 编码将文件传输到服务端，文件下载是服务端将文件流写入响应输出流供客户端保存 |
| 能做什么 | 文件上传：接收客户端上传的文件保存到服务器或云存储；文件下载：将服务器文件以流方式返回客户端供下载 |
| 怎么用 | 上传：表单 `enctype="multipart/form-data"`，Servlet 3.0+ 使用 `@MultipartConfig` 和 `request.getPart("file")`；下载：设置 Content-Disposition 响应头，通过 `response.getOutputStream()` 写入文件流 |
| 原理和工作流程 | 文件上传：客户端表单设置 enctype="multipart/form-data"，浏览器将文件以二进制流编码在请求体中。Servlet 3.0+ 中标注 @MultipartConfig 注解，通过 request.getPart("file") 获取 Part 对象，调用 part.write(fileName) 保存文件。文件下载：设置 Content-Type 为 application/octet-stream，设置 Content-Disposition 为 `attachment; filename="xxx"` 触发浏览器下载对话框，通过 response.getOutputStream() 将文件字节流写入响应体 |
| 缺点 | 大文件上传占用内存和带宽需分片上传；文件类型和安全校验需自行实现；下载大文件需流式处理避免内存溢出；中文文件名需 URLEncoder 编码处理浏览器兼容性 |

### 1.6 中文乱码处理

| 维度 | 内容 |
|------|------|
| 是什么 | 中文乱码是由于字符编码不一致导致的显示问题，涉及请求参数编码、响应编码、页面编码、数据库编码等多个环节 |
| 能做什么 | 解决 GET 请求参数乱码；解决 POST 请求体乱码；统一响应编码；确保页面和数据库编码一致 |
| 怎么用 | GET 乱码：Tomcat 配置 `URIEncoding="UTF-8"`；POST 乱码：`request.setCharacterEncoding("UTF-8")`；响应：`response.setContentType("text/html;charset=UTF-8")` |
| 原理和工作流程 | 乱码根本原因：字符在不同环节使用不同编码方式导致解码错误。GET 请求参数乱码：Tomcat 默认使用 ISO-8859-1 解码 URL 参数。解决方案：在 server.xml 的 Connector 中配置 URIEncoding="UTF-8"。POST 请求体乱码：未设置请求体编码时默认使用 ISO-8859-1 解码。解决方案：在 doPost 第一行调用 request.setCharacterEncoding("UTF-8")。响应乱码：设置 response.setCharacterEncoding("UTF-8") 和 response.setContentType("text/html;charset=UTF-8")。数据库乱码：在 JDBC URL 中指定 characterEncoding=UTF-8 |
| 缺点 | 乱码问题场景多样需逐一排查编码环节；各服务器默认编码设置不一致；需要同时配置多个编码点；历史代码中编码处理不统一 |

---

## 二、底层原理

### 2.1 Filter 责任链底层实现

| 维度 | 内容 |
|------|------|
| 是什么 | Filter 责任链由 Tomcat 的 ApplicationFilterChain 类实现，内部维护 Filter 数组和索引指针，通过递归式调用实现链式拦截 |
| 能做什么 | 按配置顺序构建 Filter 执行链；通过索引指针控制 Filter 的执行顺序；在 Filter 前后分别执行前置和后置逻辑 |
| 怎么用 | ApplicationFilterChain 内部维护 `private Filter[] filters` 和 `private int pos`，通过 internalDoFilter 方法递归调用 |
| 原理和工作流程 | ApplicationFilterChain 核心实现：1. 构建阶段：StandardWrapperValve 在分配 Servlet 实例后，根据请求 URL 匹配所有适用的 Filter，按顺序创建 Filter 数组并设置目标 Servlet。2. 执行阶段：调用 ApplicationFilterChain.doFilter 方法，内部调用 internalDoFilter。internalDoFilter 判断 pos 是否小于 filters.length，若是则取 filters[pos++] 调用其 doFilter 方法。Filter 的 doFilter 中调用 chain.doFilter 时再次进入 internalDoFilter，取出下一个 Filter，形成递归调用。当 pos 等于 filters.length 时调用 servlet.service 方法。3. servlet.service 返回后调用栈逐层返回，各 Filter 执行后置逻辑 |
| 缺点 | 递归调用链过长可能导致栈溢出；Filter 执行顺序依赖数组构建顺序；后置逻辑中 response 可能已被提交；缺少异常处理机制需在 Filter 中捕获 |

### 2.2 Request 门面模式

| 维度 | 内容 |
|------|------|
| 是什么 | Tomcat 使用门面模式，通过 RequestFacade 和 ResponseFacade 包装内部 Request/Response 对象，限制应用程序只能访问 Servlet API 规范定义的方法 |
| 能做什么 | 防止应用程序直接访问 Tomcat 内部 API；确保 Servlet 规范的一致性；隐藏内部实现细节 |
| 怎么用 | 应用程序接收到的 HttpServletRequest 实际类型是 RequestFacade，内部持有 org.apache.catalina.connector.Request 引用 |
| 原理和工作流程 | Tomcat 内部使用 org.apache.catalina.connector.Request 处理请求，该对象包含大量 Tomcat 内部方法。如果直接暴露给应用程序，应用程序可能依赖 Tomcat 内部 API 导致无法移植。CoyoteAdapter 在适配请求时创建 RequestFacade 包装内部 Request 对象，RequestFacade 仅暴露 Servlet 规范定义的公共方法，对内部方法调用返回 UnsupportedOperationException 或 null。门面模式实现了容器与应用程序的解耦 |
| 缺点 | 限制了应用程序对底层能力的访问；门面包装增加了一次间接调用；调试时无法直接查看内部对象状态；需要反射才能绕过门面限制 |

### 2.3 Listener 的事件驱动模型

| 维度 | 内容 |
|------|------|
| 是什么 | Listener 基于观察者模式，Servlet 容器作为事件源在特定时机触发事件，已注册的监听器作为观察者接收事件并执行回调 |
| 能做什么 | 应用启动时触发 ServletContextEvent；Session 创建时触发 HttpSessionEvent；请求到达时触发 ServletRequestEvent；属性变更时触发对应事件 |
| 怎么用 | 实现对应监听器接口并标注 @WebListener，容器自动注册并在事件发生时回调 |
| 原理和工作流程 | Servlet 规范定义了 8 种监听器接口和对应的事件类型。生命周期监听器（ServletContextListener、HttpSessionListener、ServletRequestListener）监听创建/销毁事件。属性变更监听器（ServletContextAttributeListener、HttpSessionAttributeListener、ServletRequestAttributeListener）监听属性增删改事件。对象绑定监听器（HttpSessionBindingListener、HttpSessionActivationListener）由实体类实现，在对象绑定/解绑或钝化/活化时触发。容器在启动时扫描所有 @WebListener 注解的类并实例化注册。事件发生时容器遍历所有注册的监听器调用回调方法。监听器执行顺序不保证 |
| 缺点 | 监听器执行顺序不可控；监听器异常可能影响应用启动和请求处理；监听器数量多导致启动时间增加；事件类型有限无法自定义事件 |

---

## 三、实战应用

### 3.1 Filter 实现统一编码与权限校验

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 Filter 实现统一编码设置和登录权限校验的完整实战示例 |
| 能做什么 | 统一设置请求和响应编码；校验用户登录状态；放行白名单路径；未登录用户重定向到登录页 |
| 怎么用 | `@WebFilter(urlPatterns = "/*") public class AuthFilter implements Filter { doFilter 中判断路径和 Session 中用户信息决定放行或重定向 }` |
| 原理和工作流程 | 创建 AuthFilter 实现 Filter 接口，init 方法中初始化白名单路径列表。doFilter 方法中：1. 设置编码。2. 获取请求路径判断是否在白名单中，若是则直接放行。3. 从 Session 中获取登录用户信息，若不为空则放行。4. 若未登录且不在白名单，判断是否为 AJAX 请求（X-Requested-With 头），若是则返回 JSON 格式 401 错误，否则重定向到登录页。注意编码 Filter 应放在权限 Filter 之前 |
| 缺点 | 白名单路径硬编码维护不便；Session 校验依赖 Cookie 禁用后失效；静态资源拦截增加性能开销；AJAX 和页面请求的未登录处理需区分 |

### 3.2 Listener 实现应用启动初始化与在线人数统计

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 ServletContextListener 和 HttpSessionListener 实现应用启动时加载全局配置和统计在线人数 |
| 能做什么 | 应用启动时加载配置文件存入 ServletContext；Session 创建时在线人数加一；Session 销毁时在线人数减一 |
| 怎么用 | `@WebListener public class AppListener implements ServletContextListener, HttpSessionListener { contextInitialized 加载配置；sessionCreated 人数+1；sessionDestroyed 人数-1 }` |
| 原理和工作流程 | AppListener 同时实现 ServletContextListener 和 HttpSessionListener。contextInitialized 方法在应用启动时由容器回调，读取配置文件将 Properties 对象存入 ServletContext。同时初始化 AtomicInteger 在线计数器存入 ServletContext。sessionCreated 方法每次新 Session 创建时 AtomicInteger 加一。sessionDestroyed 方法 Session 过期或主动销毁时减一。注意 Session 销毁可能发生在超时后，统计在线人数只是近似值 |
| 缺点 | Session 超时销毁有延迟导致在线人数不精确；AtomicInteger 在分布式环境无法跨节点共享；监听器异常导致启动失败；配置文件路径硬编码不灵活 |

### 3.3 文件上传与下载完整实现

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 Servlet 3.0+ @MultipartConfig 实现文件上传和基于流式输出实现文件下载的完整实战 |
| 能做什么 | 接收客户端上传的文件保存到服务器；从服务器读取文件以流方式返回客户端下载；处理中文文件名和防止路径穿越 |
| 怎么用 | 上传：`@MultipartConfig(maxFileSize=10*1024*1024) @WebServlet("/upload") doPost 中 request.getPart("file").write(savePath + fileName)`；下载：`@WebServlet("/download") doGet 中设置 Content-Disposition 头，FileInputStream 写入 response.getOutputStream()` |
| 原理和工作流程 | 文件上传：在 Servlet 上标注 @MultipartConfig 配置大小限制。doPost 中通过 request.getPart("file") 获取 Part 对象，通过 getSubmittedFileName 获取文件名，使用 UUID 重命名防止冲突，通过 part.write(savePath) 保存到磁盘。文件下载：通过 request.getParameter 获取文件名，进行路径穿越校验，设置 Content-Type 为 application/octet-stream，设置 Content-Disposition 为 `attachment; filename*=UTF-8''urlEncodedFileName` 支持中文。使用 FileInputStream 循环读取文件字节写入 response.getOutputStream() |
| 缺点 | 大文件上传需分片上传和断点续传；文件类型校验需自行实现；下载大文件内存占用高需流式处理；中文文件名在不同浏览器编码处理不同 |

### 3.4 中文乱码统一解决方案

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 Tomcat 配置、EncodingFilter、页面编码设置、数据库连接编码四层统一解决中文乱码问题的完整方案 |
| 能做什么 | 解决 GET 请求 URL 参数乱码；解决 POST 请求体乱码；确保响应不乱码；确保数据库读写不乱码 |
| 怎么用 | Tomcat：`URIEncoding="UTF-8"`；Filter：`request.setCharacterEncoding("UTF-8")`；页面：`<%@ page contentType="text/html;charset=UTF-8" %>`；数据库：`jdbc:mysql://...?characterEncoding=utf-8` |
| 原理和工作流程 | 完整的乱码解决方案需覆盖四个环节：1. Tomcat 层面：配置 URIEncoding="UTF-8" 解决 GET 请求 URL 参数解码。2. Filter 层面：设置 request.setCharacterEncoding("UTF-8") 解决 POST 请求体解码，设置 response.setContentType 解决响应编码。3. 页面层面：JSP 设置 `<%@ page contentType="text/html;charset=UTF-8" %>`，HTML 设置 `<meta charset="UTF-8">`。4. 数据库层面：JDBC URL 添加 characterEncoding=utf-8 和 useUnicode=true，MySQL 数据库设置 utf8mb4 字符集 |
| 缺点 | 需要同时配置多个环节遗漏一处即乱码；各服务器默认编码设置不一致；历史代码编码处理不统一；UTF-8 与 GBK 混用增加排查难度 |

---

## 四、常见面试题

### 1. Filter 过滤器的工作原理和生命周期？

| 维度 | 内容 |
|------|------|
| 是什么 | Filter 基于责任链模式在请求到达 Servlet 前后执行拦截，生命周期包括 init/doFilter/destroy 三个阶段 |
| 能做什么 | 统一编码处理；权限验证；请求日志；敏感词过滤；响应压缩；跨域处理 |
| 怎么用 | 实现 Filter 接口，覆写 init/doFilter/destroy，通过 @WebFilter 注解或 web.xml 配置拦截路径 |
| 原理和工作流程 | Filter 生命周期：init 在容器启动时调用一次获取 FilterConfig 读取初始化参数。doFilter 在每次匹配的请求中调用，先执行前置逻辑，然后调用 chain.doFilter 放行，在 Servlet 处理完成后执行后置逻辑。destroy 在容器关闭时调用一次释放资源。多个 Filter 按配置顺序组成 FilterChain，请求按顺序经过各 Filter 前置逻辑，到达 Servlet 后逆序经过后置逻辑，形成洋葱模型 |
| 缺点 | 注解方式无法控制执行顺序需额外配置；不依赖 Spring 容器获取 Bean 困难；只能拦截请求粒度无法细到方法；责任链过长影响性能 |

### 2. Filter 和 Interceptor（拦截器）的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | Filter 是 Servlet 规范组件由 Servlet 容器管理，Interceptor 是 Spring 框架组件由 Spring 容器管理，二者在规范、依赖、执行范围、执行顺序上不同 |
| 能做什么 | Filter 拦截所有请求含静态资源；Interceptor 只拦截 Controller 请求可注入 Spring Bean |
| 怎么用 | Filter：`implements javax.servlet.Filter`；Interceptor：`implements HandlerInterceptor` 注册到 WebMvcConfigurer |
| 原理和工作流程 | Filter 是 Servlet 规范组件，由 Servlet 容器管理，作用于所有请求含静态资源，在请求进入 Servlet 前后执行，不依赖 Spring 容器。Interceptor 是 Spring 框架组件，由 Spring 容器管理，仅作用于 Spring MVC 处理的 Controller 请求，在 Controller 方法前后和视图渲染后执行（preHandle/postHandle/afterCompletion），可直接注入 Bean。执行顺序：Filter -> Interceptor -> Controller。Filter 基于函数回调，Interceptor 基于 AOP 和反射 |
| 缺点 | Filter 获取 Spring Bean 困难；Interceptor 无法拦截非 Controller 请求；二者执行顺序混合时排查复杂；Filter 与 Interceptor 职责重叠易混淆 |

### 3. Servlet 中 Listener 监听器有哪些？各有什么作用？

| 维度 | 内容 |
|------|------|
| 是什么 | Listener 是 Servlet 规范中基于观察者模式的监听组件，共 8 种接口，分为三类：生命周期监听、属性变更监听、对象绑定监听 |
| 能做什么 | 监听应用启动/销毁初始化全局资源；监听 Session 创建/销毁统计在线人数；监听请求创建/销毁记录日志；监听属性变更；监听对象绑定/钝化/活化 |
| 怎么用 | 实现对应接口并标注 @WebListener，容器自动注册并在事件发生时回调 |
| 原理和工作流程 | 三大类八种监听器：1. 生命周期监听器 -- ServletContextListener（应用启动/销毁）、HttpSessionListener（Session 创建/销毁）、ServletRequestListener（请求初始化/销毁）。2. 属性变更监听器 -- 三个作用域的 AttributeListener（属性增删改）。3. 对象绑定监听器 -- HttpSessionBindingListener（对象绑定到 Session/解绑，由实体类实现）、HttpSessionActivationListener（Session 钝化/活化，由实体类实现）。容器在特定事件发生时遍历已注册的监听器并调用回调方法 |
| 缺点 | 监听器执行顺序不可控；监听器异常可能影响应用启动；监听器数量多导致启动时间增加；事件类型有限无法自定义 |

### 4. 什么是 Session 钝化和活化？如何实现？

| 维度 | 内容 |
|------|------|
| 是什么 | Session 钝化是将不活跃的 Session 从内存序列化到磁盘，活化是将磁盘上的 Session 反序列化回内存，用于节省内存和实现 Session 迁移 |
| 能做什么 | 节省内存资源；服务器重启后恢复 Session；实现 Session 跨服务器迁移 |
| 怎么用 | 实体类实现 Serializable 和 HttpSessionActivationListener；在 context.xml 中配置 PersistentManager 的 maxIdleSwap 和 directory |
| 原理和工作流程 | Tomcat 的 PersistentManager 管理 Session 钝化与活化。当 Session 空闲时间超过 maxIdleSwap 时，Manager 将 Session 对象及其属性序列化到指定目录。Session 属性对象必须实现 Serializable。实现 HttpSessionActivationListener 接口的类在钝化前收到 sessionWillPassivate 回调（释放不可序列化资源），活化后收到 sessionDidActivate 回调（重建资源）。配置方式：在 context.xml 中配置 Manager 元素，如 `<Manager className="org.apache.catalina.session.PersistentManager" maxIdleSwap="60"><Store className="org.apache.catalina.session.FileStore" directory="sessions"/></Manager>` |
| 缺点 | 属性对象必须实现 Serializable 增加约束；钝化活化有 I/O 开销影响性能；不可序列化对象的释放和重建需自行处理；PersistentManager 默认不启用需手动配置 |

### 5. 文件上传时如何防止文件过大和类型安全问题？

| 维度 | 内容 |
|------|------|
| 是什么 | 文件上传安全防护包括限制文件大小、校验文件类型、防止路径穿越、重命名文件等综合措施 |
| 能做什么 | 限制单个文件和总请求大小；校验文件 MIME 类型和扩展名；防止路径穿越攻击；使用 UUID 重命名文件 |
| 怎么用 | @MultipartConfig 配置 maxFileSize 和 maxRequestSize；通过 part.getContentType() 获取 MIME 类型校验；通过 getSubmittedFileName 校验扩展名；使用 UUID.randomUUID() 重命名 |
| 原理和工作流程 | 大小限制：在 @MultipartConfig 中配置 maxFileSize 和 maxRequestSize，超出时抛出 SizeLimitExceededException。类型校验：通过 part.getContentType() 获取 MIME 类型与白名单对比，注意 MIME 类型可被伪造需结合文件头魔数校验。扩展名校验：通过 part.getSubmittedFileName() 获取原始文件名，提取扩展名与白名单对比。路径穿越防护：过滤文件名中的 ../ 和 ..\\ 等字符，仅保留纯文件名。重命名：使用 UUID.randomUUID() 生成唯一文件名，保留原始扩展名 |
| 缺点 | MIME 类型可被伪造需结合魔数校验；大文件上传需分片上传和断点续传；文件类型白名单维护成本高；文件存储路径规划需考虑磁盘空间和备份 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | Filter、Listener、文件上传下载、中文乱码相关的常见错误与陷阱汇总 |
| 能做什么 | 解决 Filter 执行顺序问题；避免 Listener 异常影响应用；处理文件上传路径穿越；统一解决中文乱码 |
| 怎么用 | Filter 顺序用 FilterRegistrationBean 控制；Listener 异常用 try-catch 包裹；文件名过滤路径穿越字符；四层编码方案统一解决乱码 |
| 原理和工作流程 | Filter 执行顺序：@WebFilter 注解无法控制顺序，需使用 FilterRegistrationBean 注册并设置 setOrder()。Listener 异常：contextInitialized 中异常会导致应用启动失败，需用 try-catch 包裹。文件上传路径穿越：攻击者可能上传 `../../etc/passwd` 文件名，需过滤 `../` 和 `..\\` 等字符。中文乱码：需同时覆盖 Tomcat URIEncoding、request.setCharacterEncoding、response.setContentType、页面 charset、数据库 characterEncoding 五个环节。文件下载中文文件名：使用 `filename*=UTF-8''urlEncodedFileName` 格式兼容各浏览器 |
| 缺点 | Filter 顺序控制增加配置复杂度；Listener 异常处理需逐个包裹；文件上传安全校验需覆盖多个维度；中文乱码需同时配置多个环节遗漏一处即乱码 |

---

> [返回原文](./03-Request与Response&Filter监听器.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)