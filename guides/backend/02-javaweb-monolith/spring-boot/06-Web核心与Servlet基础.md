# Web 核心与 Servlet 基础

> 学习路线对应：第2周 -- Spring Boot 框架
> 前置知识：Java 面向对象、网络编程基础
> 预计学习时间：1-2 天

## 一、核心概念

### 1.1 Web 发展历程

| 阶段 | 代表技术 | 特点 |
|------|---------|------|
| **静态 Web** | HTML、CGI | 页面内容固定，CGI 每次请求创建进程，开销大 |
| **动态 Web** | ASP、JSP、PHP | 服务端动态生成页面，与数据库交互 |
| **Java Web** | Servlet、JSP | 基于 Java 规范，跨平台，企业级应用 |
| **框架时代** | Spring MVC、Spring Boot | 约定优于配置，注解驱动，内嵌容器 |

### 1.2 HTTP 协议

HTTP 是无状态、基于请求-响应模型的应用层协议，默认端口 80（HTTPS 为 443）。

**请求结构：**

```
POST /api/user?debug=true HTTP/1.1        <-- 请求行：方法 URL 协议版本
Host: localhost:8080                       <-- 请求头
Content-Type: application/json
Content-Length: 35
Authorization: Bearer xxx-token

{"name":"张三","age":25}                   <-- 请求体（GET 请求通常无请求体）
```

**响应结构：**

```
HTTP/1.1 200 OK                            <-- 状态行：协议版本 状态码 状态描述
Content-Type: application/json             <-- 响应头
Content-Length: 28

{"code":0,"msg":"success"}                 <-- 响应体
```

**常用状态码：**

| 状态码 | 含义 | 场景 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 301 | Moved Permanently | 永久重定向，浏览器会缓存 |
| 302 | Found | 临时重定向 |
| 304 | Not Modified | 资源未修改，使用浏览器缓存 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证（需要登录） |
| 403 | Forbidden | 已认证但无权限访问 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 网关收到无效响应 |
| 503 | Service Unavailable | 服务不可用（过载或维护中） |

**GET vs POST：**

| 维度 | GET | POST |
|------|-----|------|
| 参数位置 | URL 查询字符串 | 请求体 |
| 长度限制 | 浏览器限制（约 2KB） | 理论上无限制 |
| 安全性 | 参数暴露在 URL | 相对安全（但明文传输仍不安全） |
| 幂等性 | 幂等（多次请求结果相同） | 非幂等 |
| 缓存 | 可被浏览器缓存 | 默认不缓存 |

> **生活化类比：HTTP 协议就像打电话** —— HTTP 的请求-响应模型就像打电话：你（客户端）拨通对方号码（发起请求），说"喂，帮我查一下订单状态"（请求行+请求头+请求体），对方（服务器）听完后回答"好的，你的订单已发货"（状态行+响应头+响应体），然后双方挂断（连接结束）。HTTP 是无状态的——每次打电话对方都不记得你上次说了什么（无状态协议），所以每次都要重新自我介绍（携带 Cookie/Token 认证信息）。GET 请求就像口头问问题（参数在 URL 查询字符串，对方听得见），POST 请求就像递一份书面材料（参数在请求体，更正式、内容更多）。301 重定向就像对方说"这事归另一个部门管，打这个电话"，302 是"临时转到另一个号码"，304 是"你问的事跟上次一样，答案没变，用上次的就行"。

> 📖 **参考链接**：
> - [MDN HTTP 文档](https://developer.mozilla.org/zh-CN/docs/Web/HTTP) -- MDN Web 文档（HTTP 协议、请求响应结构、状态码详解）
> - [Spring Framework Reference](https://docs.spring.io/spring-framework/reference/) -- Spring 框架参考文档（Web MVC、Servlet 容器集成）

### 1.3 Servlet

**什么是 Servlet：** Servlet 是 Java EE 规范中用于处理 Web 请求的服务器端组件，运行在 Servlet 容器（如 Tomcat）中。它本质是一个接口 `javax.servlet.Servlet`。

**Servlet 生命周期：**

| 阶段 | 方法 | 调用时机 | 调用次数 |
|------|------|---------|---------|
| 初始化 | `init(ServletConfig)` | Servlet 被加载时 | 1 次 |
| 处理请求 | `service(ServletRequest, ServletResponse)` | 每次请求 | 多次 |
| 销毁 | `destroy()` | 容器关闭或卸载时 | 1 次 |

> **生活化类比：Servlet 生命周期就像士兵服役** —— 一个 Servlet 的生命周期就像一名士兵的军旅生涯：① **init()——入伍训练**：士兵入伍时接受基础训练，配备装备（Servlet 被加载时初始化，读取配置参数），这一步只做一次；② **service()——执行任务**：士兵正式服役期间，每次接到命令（每次 HTTP 请求）都执行相应任务，根据任务类型分发到不同行动（service() 根据 HTTP 方法调用 doGet/doPost 等），这一步执行多次；③ **destroy()——退伍退役**：士兵退伍时交接装备、归还物资（容器关闭时 Servlet 销毁，释放资源），也只做一次。默认情况下 Servlet 是"招之即来"的——首次有请求时才入伍（懒加载），但可以通过 `load-on-startup` 设为"提前入伍"（容器启动时即初始化）。

> 📖 **参考链接**：
> - [Spring Framework Reference](https://docs.spring.io/spring-framework/reference/) -- Spring 框架参考文档（Servlet 集成、DispatcherServlet 与 Servlet 生命周期）

**Servlet 体系结构：**

```
Servlet（接口）
  └── GenericServlet（抽象类，与协议无关）
        └── HttpServlet（抽象类，处理 HTTP 协议）
              └── 自定义 Servlet（继承 HttpServlet）
```

- `GenericServlet`：实现了 `Servlet` 接口，提供了通用的 `init`/`destroy` 实现，留下 `service()` 抽象。
- `HttpServlet`：覆写了 `service()`，根据 HTTP 方法分发到 `doGet`/`doPost`/`doPut`/`doDelete` 等方法。

### 1.4 Tomcat

**Tomcat 架构：** Tomcat 由 Connector（连接器）和 Container（容器）两大核心组成。

```
Tomcat Server
  └── Service
        ├── Connector（连接器：处理网络 I/O、协议解析）
        │     ├── HTTP/1.1（端口 8080）
        │     └── AJP（端口 8009，与 Apache/Nginx 对接）
        └── Engine（容器：处理请求路由）
              └── Host（虚拟主机，如 localhost）
                    └── Context（Web 应用）
                          └── Wrapper（单个 Servlet）
```

**Tomcat 线程模型：**

| 模型 | 说明 | 适用场景 |
|------|------|---------|
| **BIO** | 阻塞 I/O，一个请求一个线程 | 并发量低（Tomcat 8.5 已移除） |
| **NIO** | 非阻塞 I/O，基于 Selector 多路复用 | 默认模型，高并发 |
| **APR** | 使用 native 库调用操作系统 I/O | 极致性能，需安装 native 库 |

**Tomcat 目录结构：**

| 目录 | 作用 |
|------|------|
| `bin/` | 启动/关闭脚本（startup.sh、shutdown.sh） |
| `conf/` | 配置文件（server.xml、web.xml） |
| `lib/` | Tomcat 运行所需 JAR 包 |
| `logs/` | 日志文件 |
| `webapps/` | Web 应用部署目录 |
| `work/` | JSP 编译后的 Servlet 文件 |

---

## 二、底层原理

### 2.1 Servlet 请求处理流程

一个 HTTP 请求在 Tomcat 中的完整流转路径：

```
1. 客户端发送 HTTP 请求
2. Connector 接收请求（NIO Endpoint 监听端口）
3. Connector 将请求封装为 CoyoteRequest/CoyoteResponse
4. CoyoteAdapter 将 Coyote 对象适配为 HttpServletRequest/Response
5. Mapper 根据 URL 匹配到对应的 Host -> Context -> Wrapper
6. Engine 的 Pipeline 执行 Valve 链
7. Host 的 Pipeline 执行 Valve 链
8. Context 的 Pipeline 执行 Valve 链
9. Wrapper 调用 FilterChain（执行所有匹配的 Filter）
10. 最终调用 Servlet 的 service() -> doGet()/doPost()
```

**核心要点：** Tomcat 使用 Pipeline-Valve 责任链模式实现容器组件间的请求传递，每个层级（Engine/Host/Context/Wrapper）都有自己的 Pipeline。

**HTTP 请求在 Tomcat 中的完整流转 Mermaid 图：**

```mermaid
%%{init: {'themeVariables': {'fontSize': '16px'}}}%%
flowchart TD
    A["客户端发送 HTTP 请求"] --> B["Connector（连接器）<br/>NIO Endpoint 监听端口"]
    B --> C["封装为 CoyoteRequest / CoyoteResponse"]
    C --> D["CoyoteAdapter 适配<br/>Coyote 对象 → HttpServletRequest/Response"]
    D --> E["Mapper 路由匹配<br/>根据 URL 匹配 Host → Context → Wrapper"]
    E --> F["Engine Pipeline<br/>执行 Engine 层 Valve 链"]
    F --> G["Host Pipeline<br/>执行 Host 层 Valve 链"]
    G --> H["Context Pipeline<br/>执行 Context 层 Valve 链"]
    H --> I["Wrapper 调用 FilterChain<br/>执行所有匹配的 Filter"]
    I --> J["Filter1 → Filter2 → Filter3"]
    J --> K["Servlet.service()<br/>根据 HTTP 方法分发"]
    K --> L["doGet() / doPost() / doPut() / doDelete()"]
    L --> M["业务逻辑处理<br/>生成响应内容"]
    M --> N["响应逆序返回<br/>Servlet → Filter3 → Filter2 → Filter1"]
    N --> O["通过 Connector 返回客户端"]

    style I["FilterChain（责任链模式）"]
    style K["Servlet 分发（模板方法模式）"]
```

> 📖 **参考链接**：
> - [MDN HTTP 文档](https://developer.mozilla.org/zh-CN/docs/Web/HTTP) -- MDN Web 文档（HTTP 请求响应生命周期）
> - [Spring Framework Reference](https://docs.spring.io/spring-framework/reference/) -- Spring 框架参考文档（Tomcat 内嵌容器请求处理机制）

### 2.2 HttpServletRequest / HttpServletResponse 核心 API

**HttpServletRequest：**

| 方法 | 作用 |
|------|------|
| `getParameter(String)` | 获取请求参数（表单/查询字符串） |
| `getHeader(String)` | 获取请求头 |
| `getMethod()` | 获取请求方法（GET/POST） |
| `getInputStream()` | 获取请求体输入流（用于读取 JSON） |
| `getCookies()` | 获取 Cookie 数组 |
| `getSession()` | 获取/创建 HttpSession |
| `setAttribute(String, Object)` | 请求作用域存储数据 |
| `getRequestDispatcher(String)` | 获取请求转发器 |

**HttpServletResponse：**

| 方法 | 作用 |
|------|------|
| `setStatus(int)` | 设置响应状态码 |
| `setHeader(String, String)` | 设置响应头 |
| `getOutputStream()` | 获取字节输出流（用于文件下载） |
| `getWriter()` | 获取字符输出流（用于文本响应） |
| `addCookie(Cookie)` | 添加 Cookie 到响应 |
| `sendRedirect(String)` | 重定向 |

### 2.3 Filter 过滤器

Filter 基于**责任链模式**实现，在请求到达 Servlet 之前和响应离开 Servlet 之后执行拦截。

**生命周期方法：**

| 方法 | 说明 |
|------|------|
| `init(FilterConfig)` | 初始化，容器启动时调用一次 |
| `doFilter(Request, Response, Chain)` | 核心方法，每次请求调用 |
| `destroy()` | 销毁，容器关闭时调用一次 |

**执行顺序：** 按 `web.xml` 中 `<filter-mapping>` 的声明顺序执行。在 Servlet 3.0+ 注解方式中，可通过 `@WebFilter` 的属性设置，但无法直接控制顺序，建议使用 `FilterRegistrationBean` 或 `@Order` 注解。

```
请求进来：Filter1 -> Filter2 -> Filter3 -> Servlet
响应出去：Servlet -> Filter3 -> Filter2 -> Filter1
```

### 2.4 Listener 监听器

Listener 基于**观察者模式**，监听 Web 应用中特定事件的发生。

| 监听器接口 | 触发时机 | 典型场景 |
|-----------|---------|---------|
| `ServletContextListener` | 应用启动/销毁 | 初始化全局资源、加载配置 |
| `HttpSessionListener` | Session 创建/销毁 | 统计在线人数 |
| `ServletRequestListener` | 请求创建/销毁 | 请求日志记录 |
| `ServletContextAttributeListener` | 应用作用域属性增删改 | 监听全局配置变化 |
| `HttpSessionAttributeListener` | Session 属性增删改 | 监听用户数据变化 |

### 2.5 JSP 到 Servlet 的编译过程

JSP 本质上会被编译成 Servlet，编译由 Tomcat 的 Jasper 引擎完成。

```
第一次访问 JSP 页面：
1. Tomcat 检测到 .jsp 文件被访问
2. Jasper 引擎解析 JSP 文件（HTML 标签 -> out.write()，JSP 脚本 -> Java 代码）
3. 生成 Java 源文件（work/Catalina/localhost/项目名/org/apache/jsp/xxx_jsp.java）
4. 编译为 .class 文件
5. 加载并实例化 Servlet，执行 _jspService() 方法
6. 后续访问直接调用已编译的 Servlet
```

**注意：** JSP 修改后，Tomcat 会自动重新编译（默认 `development=true`）。生产环境建议关闭以提升性能。

### 2.6 Session vs Cookie

| 维度 | Cookie | Session |
|------|--------|---------|
| 存储位置 | 客户端（浏览器） | 服务端 |
| 大小限制 | 约 4KB | 无限制（受内存影响） |
| 安全性 | 低（可被篡改） | 高 |
| 生命周期 | 可设置 maxAge | 默认 30 分钟超时 |
| 工作机制 | 服务器通过 Set-Cookie 下发 | 基于 Cookie 中的 JSESSIONID 关联 |

**Session 跟踪机制：**

```
1. 客户端首次请求，服务端创建 HttpSession，生成 JSESSIONID
2. 服务端通过 Set-Cookie 将 JSESSIONID 返回客户端
3. 客户端后续请求携带 JSESSIONID Cookie
4. 服务端根据 JSESSIONID 找到对应 Session
```

**Session 持久化：** Tomcat 关闭时可将 Session 序列化到磁盘（`SESSIONS.ser`），重启后恢复，避免用户登录状态丢失。

---

## 三、实战应用

### 3.1 手写 Servlet 完整示例

**方式一：web.xml 配置**

```xml
<!-- web.xml -->
<servlet>
    <servlet-name>userServlet</servlet-name>
    <servlet-class>com.example.web.UserServlet</servlet-class>
    <load-on-startup>1</load-on-startup>
</servlet>
<servlet-mapping>
    <servlet-name>userServlet</servlet-name>
    <url-pattern>/user</url-pattern>
</servlet-mapping>
```

**方式二：注解配置（Servlet 3.0+）**

```java
@WebServlet(name = "userServlet", urlPatterns = "/user", loadOnStartup = 1)
public class UserServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        resp.setContentType("application/json;charset=UTF-8");
        String name = req.getParameter("name");
        // 业务处理
        resp.getWriter().write("{\"name\":\"" + name + "\",\"msg\":\"success\"}");
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        // 处理 POST 请求
        BufferedReader reader = req.getReader();
        // 解析 JSON 请求体...
    }
}
```

### 3.2 Filter 实现统一编码过滤

```java
@WebFilter(urlPatterns = "/*")
public class EncodingFilter implements Filter {

    private String encoding = "UTF-8";

    @Override
    public void init(FilterConfig filterConfig) {
        String encoding = filterConfig.getInitParameter("encoding");
        if (encoding != null) {
            this.encoding = encoding;
        }
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {
        request.setCharacterEncoding(encoding);
        response.setCharacterEncoding(encoding);
        response.setContentType("application/json;charset=" + encoding);
        // 放行到下一个 Filter 或 Servlet
        chain.doFilter(request, response);
    }

    @Override
    public void destroy() {
        // 清理资源
    }
}
```

### 3.3 Listener 实现应用启动初始化

```java
@WebListener
public class AppContextListener implements ServletContextListener {

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        System.out.println("应用启动，开始初始化...");
        // 加载配置文件
        Properties props = new Properties();
        try {
            props.load(sce.getServletContext()
                    .getResourceAsStream("/WEB-INF/config.properties"));
            sce.getServletContext().setAttribute("config", props);
        } catch (IOException e) {
            throw new RuntimeException("配置加载失败", e);
        }
        // 初始化数据库连接池等全局资源
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        System.out.println("应用销毁，释放资源...");
        // 关闭连接池、清理资源
    }
}
```

### 3.4 Tomcat 在 Spring Boot 中的内嵌启动

Spring Boot 通过内嵌 Tomcat 实现 `main` 方法直接启动 Web 应用，无需部署 WAR 包。

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**内嵌 Tomcat 启动原理：**

```
1. SpringApplication.run() 启动
2. 创建 ApplicationContext（ServletWebServerApplicationContext）
3. 通过 ServletWebServerFactory 创建 Tomcat 实例（TomcatServletWebServerFactory）
4. 配置 Connector（端口、协议）
5. 注册 DispatcherServlet 为根 Servlet（映射 "/"）
6. Tomcat 启动，开始监听端口
```

**切换内嵌容器：**

```xml
<!-- 排除 Tomcat -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<!-- 使用 Undertow（并发性能更优） -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-undertow</artifactId>
</dependency>
```

---

## 四、常见面试题（附答案）

### 1. GET 和 POST 的区别？

GET 参数通过 URL 传递，有长度限制，可被缓存，幂等；POST 参数通过请求体传递，无长度限制，默认不缓存，非幂等。本质区别是语义不同：GET 用于获取资源，POST 用于提交数据。

### 2. Servlet 的生命周期？

Servlet 经历初始化（`init`）、处理请求（`service`）、销毁（`destroy`）三个阶段。`init` 在 Servlet 被加载时调用一次，`service` 在每次请求时调用，`destroy` 在容器关闭时调用一次。默认情况下 Servlet 是懒加载的（首次请求时初始化），可通过 `load-on-startup` 设置为启动时初始化。

### 3. Filter 和 Interceptor（拦截器）的区别？

| 维度 | Filter | Interceptor |
|------|--------|-------------|
| 规范 | Servlet 规范 | Spring 规范 |
| 依赖 | 不依赖 Spring 容器 | 依赖 Spring 容器 |
| 执行范围 | 可拦截所有请求（含静态资源） | 只拦截 Controller 请求 |
| 执行顺序 | Filter -> Interceptor -> Controller | Interceptor -> Controller |
| 获取 Bean | 需通过 ApplicationContext | 可直接注入 Bean |

### 4. Session 和 Cookie 的区别和联系？

Cookie 存储在客户端，Session 存储在服务端。Session 基于 Cookie 实现：服务端创建 Session 时生成 JSESSIONID，通过 Set-Cookie 下发到客户端，客户端后续请求携带此 ID，服务端据此找到对应 Session。Cookie 有大小限制（约 4KB）且安全性低，Session 安全性高但消耗服务端内存。

### 5. Tomcat 的 BIO、NIO、APR 三种线程模型有什么区别？

BIO 是阻塞 I/O，每个请求独占一个线程，并发量低（Tomcat 8.5 已移除）。NIO 是非阻塞 I/O，基于 Selector 多路复用，用少量线程处理大量连接，是 Spring Boot 默认模型。APR 使用 native 库直接调用操作系统 I/O，性能最高但需要安装 native 库，部署较复杂。

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| GET 请求中文乱码 | URL 参数中文显示乱码 | Tomcat URI 编码默认 ISO-8859-1 | 配置 `server.tomcat.uri-encoding=UTF-8`（Spring Boot 默认已为 UTF-8）；或使用 `URLEncoder.encode()` |
| POST 请求中文乱码 | 表单提交中文乱码 | 请求体未设置编码 | 在 `doPost` 第一行调用 `request.setCharacterEncoding("UTF-8")`，或使用 EncodingFilter |
| Filter 执行顺序不确定 | 多个 Filter 执行顺序与预期不符 | `@WebFilter` 注解无法控制顺序 | 使用 `FilterRegistrationBean` 注册并设置 `setOrder()` |
| Session 丢失 | 用户频繁重新登录 | Session 超时时间过短；负载均衡未做 Session 共享 | 调大 `server.servlet.session.timeout`；使用 Redis Session 共享 |
| 302 重定向丢失 POST 数据 | 重定向后请求变成 GET | 302 重定向标准要求使用 GET | 使用 307（保留请求方法）或 Forward 转发 |
| 内嵌 Tomcat 端口被占用 | 启动报 PortInUseException | 端口已被其他进程占用 | 修改 `server.port`；或终止占用端口的进程 |

---

## 本章学习自检

完成本章学习后，应该能够：
- [ ] 用自己的话解释 HTTP 协议结构、Servlet 生命周期、Tomcat 架构与请求处理流程
- [ ] 手写 Servlet（web.xml 和注解两种方式）、Filter 编码过滤器、Listener 初始化监听器
- [ ] 回答常见面试题（GET vs POST、Servlet 生命周期、Filter vs Interceptor、Session vs Cookie、Tomcat 线程模型）
- [ ] 理解 Spring Boot 内嵌 Tomcat 的启动原理及容器切换方式
- [ ] 识别并避免常见错误（中文乱码、Filter 顺序、Session 丢失、重定向丢数据等）

---

> **学习导航**：
> - 返回 [学习路线总览](../../README.md)
> - 本模块其他文件：[01-Spring-IoC与AOP深度](./01-Spring-IoC与AOP深度.md) | [03-SpringMVC与RESTful设计](./03-SpringMVC与RESTful设计.md) | [07-日志整合与监控](./07-日志整合与监控.md)
> - 实战应用：[电商订单实时统计分析平台](../../extensions/project/01-电商订单实时统计分析平台.md)