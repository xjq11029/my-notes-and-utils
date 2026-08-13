# Spring MVC 与 RESTful 设计 导览

> 定位：五维框架浓缩提炼 03-SpringMVC与RESTful设计.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./03-SpringMVC与RESTful设计.md)。
> 前置知识：[Spring-IoC与AOP深度](./01-Spring-IoC与AOP深度-导览.md)、HTTP协议基础

---

## 一、核心概念

### 1.1 DispatcherServlet 核心流程

| 维度 | 内容 |
|------|------|
| 是什么 | Spring MVC 的前端控制器，统一接收所有请求并协调各组件完成请求处理的调度中心 |
| 能做什么 | 通过 HandlerMapping 查找处理器；通过 HandlerAdapter 调用处理器；通过 ViewResolver 解析视图 |
| 怎么用 | DispatcherServlet 继承自 FrameworkServlet，自动注册为根 Servlet 映射 "/" |
| 原理和工作流程 | 请求到达 DispatcherServlet 后 doDispatch 方法被调用。首先通过 HandlerMapping 根据 URL 找到 HandlerExecutionChain（含 Handler 和拦截器）。然后获取匹配的 HandlerAdapter，执行拦截器 preHandle，再由 HandlerAdapter 调用 Controller 方法处理请求返回 ModelAndView。接着执行拦截器 postHandle，最后 ViewResolver 将逻辑视图名解析为具体 View，渲染后返回响应。前后端分离场景下 @ResponseBody 直接序列化为 JSON，跳过视图渲染 |
| 缺点 | 单点入口，DispatcherServlet 故障则全站不可用；组件链路长，排查问题需理解完整流程；非 REST 场景下视图解析增加开销 |

### 1.2 拦截器 vs 过滤器

| 维度 | 内容 |
|------|------|
| 是什么 | Spring MVC 拦截器（Interceptor）与 Servlet 过滤器（Filter）两种请求拦截机制的对比 |
| 能做什么 | Filter 拦截所有请求含静态资源；Interceptor 仅拦截 Spring MVC 处理的请求；Interceptor 可注入 Spring Bean |
| 怎么用 | Filter 实现 Filter 接口加 `@Component`；Interceptor 实现 HandlerInterceptor 并注册到 WebMvcConfigurer |
| 原理和工作流程 | Filter 是 Servlet 规范的一部分，由 Servlet 容器管理，在请求进入 Servlet 前后通过 doFilter 链式调用，作用范围覆盖所有请求包括静态资源，无法直接获取 Spring Bean。Interceptor 是 Spring 框架的，由 Spring 容器管理，在 HandlerMapping 找到 Handler 后、HandlerAdapter 调用前后执行，提供 preHandle、postHandle、afterCompletion 三个细粒度回调，可直接注入 Bean。执行顺序为 Filter -> Interceptor -> Controller -> Interceptor -> Filter |
| 缺点 | Filter 无法获取 Spring Bean 需额外处理；Interceptor 不拦截非 Spring MVC 请求；两者执行顺序混用易混淆 |

---

## 二、底层原理

### 2.1 DispatcherServlet 源码流程

| 维度 | 内容 |
|------|------|
| 是什么 | DispatcherServlet.doDispatch 方法的源码级请求处理流程，揭示各组件协作细节 |
| 能做什么 | 定位 Handler 查找；执行拦截器链；调用 HandlerAdapter；处理视图渲染和异常 |
| 怎么用 | `protected void doDispatch(HttpServletRequest request, HttpServletResponse response) { ... }` |
| 原理和工作流程 | doDispatch 首先调用 getHandler 遍历所有 HandlerMapping，根据 URL 匹配返回 HandlerExecutionChain（含 Handler 和拦截器链）。然后调用 getHandlerAdapter 根据 Handler 类型找到支持的 HandlerAdapter。接着 applyPreHandle 执行拦截器 preHandle，任一返回 false 则中断。HandlerAdapter.handle 调用 Controller 方法返回 ModelAndView。applyPostHandle 执行拦截器 postHandle。最后 processDispatchResult 处理视图渲染，若过程中抛异常则交由 HandlerExceptionResolver 处理，触发 afterCompletion 回调 |
| 缺点 | 源码链路深，调试栈长；异常处理分散在多个阶段；ModelAndView 在 REST 场景下部分逻辑冗余 |

### 2.2 请求参数绑定原理

| 维度 | 内容 |
|------|------|
| 是什么 | Spring MVC 通过 HandlerMethodArgumentResolver 将请求数据绑定到 Controller 方法参数的机制 |
| 能做什么 | 绑定 @RequestParam 查询参数；绑定 @PathVariable 路径变量；绑定 @RequestBody JSON 请求体；绑定 @ModelAttribute 表单 |
| 怎么用 | `@GetMapping("/users/{id}") public User get(@PathVariable Long id) { }` |
| 原理和工作流程 | HandlerAdapter 调用 Controller 方法前，遍历所有 HandlerMethodArgumentResolver，对每个参数找到 supports 返回 true 的解析器。RequestParamMethodArgumentResolver 处理 @RequestParam，从 request.getParameter 取值并类型转换；PathVariableMethodArgumentResolver 从 URI 模板变量取值；RequestResponseBodyMethodProcessor 处理 @RequestBody，通过 HttpMessageConverter（如 MappingJackson2HttpMessageConverter）将 JSON 反序列化为 Java 对象，并配合 @Valid 触发校验；ModelAttributeMethodProcessor 将表单字段绑定到对象属性 |
| 缺点 | 类型转换失败抛异常需统一处理；@RequestBody 只能读取一次请求体，过滤器提前读取会导致后续绑定失败；自定义参数解析器需理解 SPI |

### 2.3 返回值处理原理

| 维度 | 内容 |
|------|------|
| 是什么 | Spring MVC 通过 HandlerMethodReturnValueHandler 处理 Controller 方法返回值的机制 |
| 能做什么 | @ResponseBody 序列化为 JSON；ModelAndView 解析视图；ResponseEntity 设置状态码和响应体 |
| 怎么用 | `@RestController` 等价于 `@Controller` 加 `@ResponseBody` |
| 原理和工作流程 | HandlerAdapter 调用 Controller 方法获得返回值后，遍历所有 HandlerMethodReturnValueHandler，找到 supportsReturnType 返回 true 的处理器。RequestResponseBodyMethodProcessor 处理 @ResponseBody 标注的返回值，通过内容协商选择 HttpMessageConverter（通常 MappingJackson2HttpMessageConverter），将返回对象序列化为 JSON 写入响应体。ModelAndViewMethodReturnValueHandler 处理 ModelAndView 类型，交由 ViewResolver 解析视图。HttpEntityMethodProcessor 处理 ResponseEntity，设置状态码、响应头后再处理响应体 |
| 缺点 | 返回值处理器优先级冲突时可能选错处理器；内容协商失败抛异常；自定义返回值处理需理解 SPI 机制 |

---

## 三、实战应用

### 3.1 统一异常处理

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 @RestControllerAdvice 配合 @ExceptionHandler 全局捕获 Controller 异常并返回统一错误响应的实践 |
| 能做什么 | 区分业务异常、参数校验异常、系统异常；返回统一格式错误响应；避免异常堆栈泄露 |
| 怎么用 | `@RestControllerAdvice public class GlobalExceptionHandler { @ExceptionHandler(BusinessException.class) public Result<Void> handle(BusinessException e) { return Result.error(e.getCode(), e.getMessage()); } }` |
| 原理和工作流程 | @RestControllerAdvice 是 @ControllerAdvice 加 @ResponseBody 的组合，被 HandlerExceptionResolver 的子类 ExceptionHandlerExceptionResolver 识别。Controller 方法抛出异常后，DispatcherServlet 的 processDispatchResult 将异常交由 HandlerExceptionResolver 链处理。ExceptionHandlerExceptionResolver 遍历所有 @ControllerAdvice 类，查找匹配异常类型的 @ExceptionHandler 方法，找到后反射调用，返回值经 ReturnValueHandler 处理（如序列化为 JSON）。匹配规则按异常类型最近匹配优先 |
| 缺点 | @ExceptionHandler 匹配规则基于异常类型，父子异常可能误匹配；全局捕获可能掩盖业务逻辑错误；无法捕获 Filter 抛出的异常 |

### 3.2 RESTful API 设计规范

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 HTTP 语义和资源导向设计 API 接口的一组约定，涵盖 URL 命名、HTTP 方法、状态码、响应格式 |
| 能做什么 | 用名词复数命名 URL；用 HTTP 方法表达操作语义；用状态码反映结果；统一响应格式 |
| 怎么用 | `GET /api/v1/users/1`、`POST /api/v1/users`、`PUT /api/v1/users/1`、`DELETE /api/v1/users/1` |
| 原理和工作流程 | REST 风格将一切抽象为资源，URL 用名词复数定位资源（如 /users），HTTP 方法表达操作（GET 查询、POST 新增、PUT 全量更新、PATCH 部分更新、DELETE 删除）。状态码 200 表示成功、201 创建成功、400 参数错误、401 未认证、403 无权限、404 未找到、500 服务器错误。版本管理通过 URL 路径（/v1/）或请求头实现。响应格式统一为 code、message、data 三段结构，分页参数统一为 page、size、sort。无状态原则要求每次请求独立、不依赖服务端 session |
| 缺点 | 纯 REST 对复杂操作（如登录、批量操作）表达力不足；HTTP 方法语义与实际业务可能不完全对应；版本迁移成本高 |

### 3.3 参数校验

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 JSR-303（Bean Validation）注解对请求参数进行声明式校验的机制 |
| 能做什么 | 非空校验；长度范围校验；格式校验（邮箱、手机号）；数值范围校验；正则匹配 |
| 怎么用 | `@NotBlank @Size(min=2, max=20) private String username;` 配合 `@Valid @RequestBody User user` |
| 原理和工作流程 | 在 DTO 字段上标注 @NotBlank、@Size、@Email、@Pattern 等校验注解，Controller 方法参数标注 @Valid 触发校验。RequestResponseBodyMethodProcessor 在反序列化请求体后调用 Validator.validate，遍历字段上的约束注解执行校验逻辑。校验失败时收集所有 ConstraintViolation，封装为 MethodArgumentNotValidException 抛出。该异常可被 @ExceptionHandler 统一捕获，提取 FieldError 的 defaultMessage 拼接为错误信息返回。Hibernate Validator 是默认实现 |
| 缺点 | 注解校验无法覆盖跨字段联合校验（需自定义 ConstraintValidator）；校验失败异常处理需统一配置；复杂业务规则校验仍需在 Service 层补充 |

---

## 四、常见面试题（附答案）

### 1. Spring MVC 的执行流程？

| 维度 | 内容 |
|------|------|
| 是什么 | 一个 HTTP 请求从到达 DispatcherServlet 到返回响应的完整组件协作流程 |
| 能做什么 | 定位 Handler；调用 HandlerAdapter；执行拦截器链；解析视图；渲染响应 |
| 怎么用 | `请求 -> DispatcherServlet -> HandlerMapping -> HandlerAdapter -> Controller -> ViewResolver -> View -> 响应` |
| 原理和工作流程 | 请求到达 DispatcherServlet 后 doDispatch 方法被调用。HandlerMapping 根据 URL 找到 HandlerExecutionChain，HandlerAdapter 根据 Handler 类型调用具体方法。Controller 执行业务逻辑返回 ModelAndView，拦截器 postHandle 在视图渲染前执行。ViewResolver 将逻辑视图名解析为具体 View，View 渲染后写入响应。前后端分离场景下 @ResponseBody 经 HttpMessageConverter 直接序列化为 JSON，跳过 ViewResolver 和 View |
| 缺点 | 组件链路长，单点故障影响全局；流程理解门槛高；非 REST 场景视图解析开销大 |

### 2. 拦截器（Interceptor）和过滤器（Filter）的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 拦截器与 Servlet 过滤器两种请求拦截机制的对比区分 |
| 能做什么 | Filter 拦截所有请求含静态资源；Interceptor 仅拦截 MVC 请求且可注入 Bean；执行顺序 Filter 先于 Interceptor |
| 怎么用 | Filter 实现 Filter 接口；Interceptor 实现 HandlerInterceptor 接口并注册 |
| 原理和工作流程 | Filter 是 Servlet 规范组件，由 Servlet 容器管理，在请求进入 DispatcherServlet 前后通过 FilterChain.doFilter 链式调用，作用于所有请求包括静态资源，不能直接获取 Spring Bean。Interceptor 是 Spring 框架组件，由 Spring 容器管理，在 HandlerMapping 找到 Handler 后通过 HandlerExecutionChain 执行，提供 preHandle、postHandle、afterCompletion 三个回调，可注入 Bean。执行顺序为 Filter -> Interceptor -> Controller -> Interceptor -> Filter |
| 缺点 | Filter 无法直接获取 Bean 需 ApplicationContext 辅助；Interceptor 作用范围窄不拦截静态资源；两者混用时顺序理解易出错 |

### 3. @ControllerAdvice 和 @ExceptionHandler 的作用？

| 维度 | 内容 |
|------|------|
| 是什么 | @ControllerAdvice 是全局 Controller 增强器，@ExceptionHandler 是异常处理方法注解，二者配合实现全局异常处理 |
| 能做什么 | 全局捕获 Controller 异常；按异常类型分发处理；返回统一错误响应格式；避免堆栈泄露 |
| 怎么用 | `@RestControllerAdvice public class GlobalExceptionHandler { @ExceptionHandler(Exception.class) public Result<Void> handle(Exception e) { return Result.error(500, "服务器错误"); } }` |
| 原理和工作流程 | @ControllerAdvice 被 ExceptionHandlerExceptionResolver 识别为全局异常处理器。Controller 方法抛出异常后，DispatcherServlet 将异常交由 HandlerExceptionResolver 链处理。ExceptionHandlerExceptionResolver 遍历所有 @ControllerAdvice 类，查找 @ExceptionHandler 标注且异常类型匹配的方法，按类型最近匹配优先。找到后反射调用，返回值经 ReturnValueHandler 处理（如序列化为 JSON）。@RestControllerAdvice 额外加 @ResponseBody 使返回值直接写入响应体 |
| 缺点 | 匹配基于异常类型，父子异常可能误匹配；全局捕获可能掩盖业务错误；Filter 层异常无法被捕获 |

### 4. RESTful API 和传统 API 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 资源导向的 RESTful 风格与动作导向的传统 API 风格的对比 |
| 能做什么 | URL 资源化；HTTP 方法语义化；状态码充分利用；无状态无 session 依赖 |
| 怎么用 | RESTful 用 `GET /users/1`；传统用 `GET /getUser?id=1` |
| 原理和工作流程 | RESTful API 以资源为核心，URL 用名词复数定位资源（/users、/order-items），HTTP 方法表达操作语义（GET 查询、POST 新增、PUT 更新、DELETE 删除），充分利用 HTTP 状态码（200、201、400、404、500）反映结果，每次请求无状态独立。传统 API 以动作为核心，URL 含动词（/getUser、/deleteOrder），通常只用 GET 和 POST，状态码统一 200、错误信息放响应体，可能依赖服务端 session。RESTful 响应格式通常 JSON，传统可能 JSON、XML、HTML 混用 |
| 缺点 | 纯 REST 对登录、批量操作等复杂场景表达力不足；HTTP 方法语义与业务不完全对应；学习成本高于传统风格 |

### 5. Spring MVC 如何解决 POST 请求中文乱码？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring MVC 中通过配置字符编码过滤器解决 POST 请求体中文乱码的方案 |
| 能做什么 | 统一设置请求和响应编码为 UTF-8；强制编码覆盖容器默认；通过配置文件或 Filter Bean 配置 |
| 怎么用 | `server.servlet.encoding.charset=UTF-8` 配合 `server.servlet.encoding.force=true` |
| 原理和工作流程 | POST 请求体中文乱码的根因是 Tomcat 默认使用 ISO-8859-1 解码请求体，与 UTF-8 编码不匹配。解决方案一是注册 CharacterEncodingFilter，在 doFilter 中调用 request.setCharacterEncoding("UTF-8") 和 response.setCharacterEncoding("UTF-8")，setForceEncoding(true) 强制覆盖。该 Filter 必须在请求体被读取前执行，因此需排在 Filter 链最前。方案二通过 application.properties 配置 server.servlet.encoding.charset 和 force，Spring Boot 自动注册 CharacterEncodingFilter 并设置参数。GET 请求乱码需配置 Tomcat URI 编码 |
| 缺点 | Filter 顺序不当则编码设置无效；强制编码可能覆盖客户端指定的编码；GET 请求乱码需单独配置 URI 编码 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | Spring MVC 开发中 @PathVariable 不匹配、GET 误用 @RequestBody、响应重复包装等高频问题汇总 |
| 能做什么 | 检查 URL 占位符与 @PathVariable 对应；GET 请求避免 @RequestBody；ResponseBodyAdvice 避免重复包装 |
| 怎么用 | `@GetMapping("/users/{id}")` 配合 `@PathVariable Long id` |
| 原理和工作流程 | @PathVariable 与 URL 占位符不匹配是因为 @PathVariable 必须在 URL 中有对应 {xxx} 占位符，缺失则启动期或运行期报错，需检查 @GetMapping 路径是否包含对应占位符。GET 请求使用 @RequestBody 失败是因为 GET 请求没有请求体，大多数 HTTP 客户端不支持 GET 请求体，应改用 @RequestParam 或 @ModelAttribute。统一响应被拦截器重复包装是因为 ResponseBodyAdvice 对所有返回值重复包装，需在 supports 方法中判断返回类型是否已是 Result，避免嵌套包装 |
| 缺点 | 占位符错误在启动期才暴露；GET 请求体限制因客户端而异；ResponseBodyAdvice 判断逻辑易遗漏边界情况 |

---

> [返回原文](./03-SpringMVC与RESTful设计.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
