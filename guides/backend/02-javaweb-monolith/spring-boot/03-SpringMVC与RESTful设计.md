# Spring MVC 与 RESTful 设计

> 学习路线对应：第2周 -- Spring Boot 框架
> 前置知识：Spring IoC、HTTP 协议基础
> 预计学习时间：1-2 天

## 一、核心概念

### 1.1 DispatcherServlet 核心流程

Spring MVC 的核心是 `DispatcherServlet`（前端控制器），它负责将请求分发到对应的处理器。

```
请求到达 -> DispatcherServlet
  -> 1. HandlerMapping：根据 URL 找到对应的 Handler（Controller 方法）
  -> 2. HandlerAdapter：调用 Handler 处理请求
  -> 3. Handler 执行（Controller 方法），返回 ModelAndView
  -> 4. ViewResolver：将逻辑视图名解析为具体视图
  -> 5. 视图渲染，返回响应
```

**核心组件：**

| 组件 | 接口 | 作用 |
|------|------|------|
| 前端控制器 | `DispatcherServlet` | 统一入口，协调各组件 |
| 处理器映射器 | `HandlerMapping` | 根据 URL 找到处理器 |
| 处理器适配器 | `HandlerAdapter` | 调用处理器方法 |
| 处理器 | `Handler`（Controller） | 业务逻辑处理 |
| 视图解析器 | `ViewResolver` | 解析视图名 |
| 视图 | `View` | 渲染响应 |

> **生活化类比：DispatcherServlet 就像公司前台接待** —— 想象一家大公司（Spring MVC 应用），所有来访者（HTTP 请求）都必须先到前台（DispatcherServlet）登记。前台不会自己处理业务，而是做三件事：① 查公司通讯录（HandlerMapping），根据来访者要找的部门（URL）找到对应的接待人（Handler/Controller 方法）；② 调派翻译（HandlerAdapter），因为不同部门接待人的沟通方式不同（有的说 JSON、有的说 XML），翻译负责适配调用方式；③ 接待人处理完事务后，前台将结果整理成标准格式（ViewResolver + View 渲染）返回给来访者。前台是唯一的统一入口，所有流转都在前台协调下完成，这就是"前端控制器"模式的核心思想。

> 📖 **参考链接**：
> - [Spring Framework Reference](https://docs.spring.io/spring-framework/reference/) -- Spring 框架参考文档（Spring MVC、DispatcherServlet、HandlerMapping、HandlerAdapter）

### 1.2 拦截器 vs 过滤器

| 维度 | 过滤器（Filter） | 拦截器（Interceptor） |
|------|-----------------|---------------------|
| **规范** | Servlet 规范 | Spring 框架 |
| **容器** | Servlet 容器管理 | Spring 容器管理 |
| **作用范围** | 所有请求（包括静态资源） | 仅 Spring MVC 处理的请求 |
| **粒度** | 粗粒度（只能在 doFilter 前后） | 细粒度（preHandle、postHandle、afterCompletion） |
| **能否获取 Spring Bean** | 不能直接获取 | 可以（由 Spring 管理） |
| **执行顺序** | Filter -> Interceptor -> Controller |

```java
// 过滤器
@Component
public class LogFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response,
                         FilterChain chain) throws IOException, ServletException {
        System.out.println("Filter: 请求前");
        chain.doFilter(request, response);
        System.out.println("Filter: 响应后");
    }
}

// 拦截器
@Component
public class LogInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response,
                             Object handler) {
        System.out.println("Interceptor: preHandle");
        return true; // 返回 true 继续执行，false 中断
    }

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response,
                           Object handler, ModelAndView modelAndView) {
        System.out.println("Interceptor: postHandle");
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) {
        System.out.println("Interceptor: afterCompletion");
    }
}
```

---

## 二、底层原理

### 2.1 DispatcherServlet 源码流程

```java
// 简化版 DispatcherServlet.doDispatch() 流程
protected void doDispatch(HttpServletRequest request, HttpServletResponse response) {
    // 1. 根据请求找到 Handler
    HandlerExecutionChain mappedHandler = getHandler(request);

    // 2. 根据 Handler 找到对应的 HandlerAdapter
    HandlerAdapter ha = getHandlerAdapter(mappedHandler.getHandler());

    // 3. 执行拦截器 preHandle
    if (!mappedHandler.applyPreHandle(request, response)) {
        return;
    }

    // 4. HandlerAdapter 调用 Handler 处理请求
    ModelAndView mv = ha.handle(request, response, mappedHandler.getHandler());

    // 5. 执行拦截器 postHandle
    mappedHandler.applyPostHandle(request, response, mv);

    // 6. 处理视图渲染
    processDispatchResult(request, response, mappedHandler, mv, dispatchException);
}
```

**DispatcherServlet 完整请求处理 Mermaid 流程图：**

```mermaid
%%{init: {'themeVariables': {'fontSize': '16px'}}}%%
flowchart TD
    A["HTTP 请求到达"] --> B["DispatcherServlet.doDispatch()"]
    B --> C["getHandler()<br/>HandlerMapping 根据 URL 匹配 Handler"]
    C --> D{"找到 Handler？"}
    D -->|"否"| E["返回 404"]
    D -->|"是"| F["getHandlerAdapter()<br/>根据 Handler 类型找到适配器"]
    F --> G["执行拦截器链 preHandle()"]
    G --> H{"preHandle 返回 true？"}
    H -->|"否"| I["请求被拦截，直接返回"]
    H -->|"是"| J["HandlerAdapter.handle()<br/>调用 Controller 方法"]
    J --> K["参数解析：HandlerMethodArgumentResolver<br/>@RequestParam / @PathVariable / @RequestBody"]
    K --> L["Controller 执行业务逻辑"]
    L --> M["返回值处理：HandlerMethodReturnValueHandler<br/>@ResponseBody → JSON 序列化"]
    M --> N["执行拦截器链 postHandle()"]
    N --> O["processDispatchResult()<br/>视图渲染 / 异常处理"]
    O --> P["执行拦截器链 afterCompletion()"]
    P --> Q["响应返回客户端"]

    style K["参数解析（核心扩展点）"]
    style M["返回值处理（核心扩展点）"]
```

**DispatcherServlet 流程关键扩展点详解：**

DispatcherServlet 的核心设计是"模板方法 + 策略模式"，它定义了请求处理的固定骨架，但每个步骤的具体实现都通过接口扩展：

| 步骤 | 扩展接口 | 默认实现 | 可自定义内容 |
|------|---------|---------|------------|
| Handler 查找 | `HandlerMapping` | `RequestMappingHandlerMapping` | 自定义 URL 到 Handler 的映射规则 |
| Handler 调用 | `HandlerAdapter` | `RequestMappingHandlerAdapter` | 支持不同类型的 Handler（如老式 Controller） |
| 参数解析 | `HandlerMethodArgumentResolver` | 30+ 内置解析器 | 自定义参数注解的解析逻辑 |
| 返回值处理 | `HandlerMethodReturnValueHandler` | 10+ 内置处理器 | 自定义返回值的序列化方式 |
| 异常处理 | `HandlerExceptionResolver` | `ExceptionHandlerExceptionResolver` | 全局异常处理策略 |
| 视图解析 | `ViewResolver` | `ContentNegotiatingViewResolver` | 自定义视图渲染逻辑 |

> 📖 **参考链接**：
> - [Spring Framework Reference](https://docs.spring.io/spring-framework/reference/) -- Spring 框架参考文档（DispatcherServlet 请求处理流程与核心组件扩展）

### 2.2 请求参数绑定原理

Spring MVC 通过 `HandlerMethodArgumentResolver` 接口实现参数绑定。常见的参数解析器：

| 参数解析器 | 支持的参数类型 |
|-----------|-------------|
| `RequestParamMethodArgumentResolver` | `@RequestParam` 注解的参数 |
| `PathVariableMethodArgumentResolver` | `@PathVariable` 注解的参数 |
| `RequestBodyMethodArgumentResolver` | `@RequestBody` 注解的参数 |
| `ModelAttributeMethodProcessor` | `@ModelAttribute` 注解的参数 |
| `ServletRequestMethodArgumentResolver` | `HttpServletRequest`、`HttpServletResponse` 等 |

```java
@RestController
public class UserController {
    // @PathVariable：URL 路径参数
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) { ... }

    // @RequestParam：查询参数
    @GetMapping("/users")
    public List<User> listUsers(@RequestParam(defaultValue = "1") int page) { ... }

    // @RequestBody：请求体 JSON -> Java 对象
    @PostMapping("/users")
    public User createUser(@Valid @RequestBody User user) { ... }

    // @ModelAttribute：表单数据绑定
    @PostMapping("/users/form")
    public User createFromForm(@ModelAttribute User user) { ... }
}
```

> **生活化类比：参数解析器就像快递分拣中心** —— 想象一个快递分拣中心（HandlerAdapter），每天收到各种格式的包裹（HTTP 请求参数）：有的地址写在包裹正面（`@RequestParam` 查询参数），有的写在背面标签上（`@PathVariable` URL 路径参数），有的装在密封箱子里需要拆开才能看到（`@RequestBody` JSON 请求体），有的地址信息分散在多个表单字段中（`@ModelAttribute` 表单绑定）。分拣中心有专门的工作人员（`HandlerMethodArgumentResolver`），每种包裹格式对应一个专门的分拣员，他们知道如何从对应位置取出地址信息并转交给快递员（Controller 方法）。当 Controller 方法声明了 `@PathVariable Long id` 参数时，`PathVariableMethodArgumentResolver` 就会从 URL 路径中提取 `{id}` 的值并转换为 Long 类型注入。

**参数解析器工作原理详解：**

每个 `HandlerMethodArgumentResolver` 包含两个核心方法：

| 方法 | 作用 | 调用时机 |
|------|------|---------|
| `supportsParameter()` | 判断当前解析器是否支持该参数类型 | 参数解析前，逐一询问所有解析器 |
| `resolveArgument()` | 从请求中提取并转换参数值 | 找到支持的解析器后执行实际解析 |

**Spring MVC 内置 30+ 参数解析器，按优先级排序的核心解析器：**

| 优先级 | 解析器 | 支持的参数 | 转换方式 |
|--------|--------|----------|---------|
| 1 | `RequestParamMethodArgumentResolver` | `@RequestParam` 标注的参数 | 查询字符串 → 类型转换 |
| 2 | `PathVariableMethodArgumentResolver` | `@PathVariable` 标注的参数 | URL 路径变量 → 类型转换 |
| 3 | `RequestBodyMethodArgumentResolver` | `@RequestBody` 标注的参数 | JSON/XML → HttpMessageConverter 反序列化 |
| 4 | `ModelAttributeMethodProcessor` | `@ModelAttribute` 标注的参数 | 表单字段 → 对象属性绑定 |
| 5 | `RequestHeaderMethodArgumentResolver` | `@RequestHeader` 标注的参数 | 请求头 → 类型转换 |
| 6 | `CookieValueMethodArgumentResolver` | `@CookieValue` 标注的参数 | Cookie 值 → 类型转换 |
| 7 | `ServletModelAttributeMethodProcessor` | `HttpServletRequest/Response` | 直接注入 Servlet API 对象 |

**自定义参数解析器示例：**

```java
// 1. 自定义注解：自动从请求头提取并解析当前登录用户
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
public @interface CurrentUser {
}

// 2. 自定义参数解析器
@Component
public class CurrentUserArgumentResolver implements HandlerMethodArgumentResolver {
    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return parameter.hasParameterAnnotation(CurrentUser.class)
            && parameter.getParameterType().equals(User.class);
    }

    @Override
    public Object resolveArgument(MethodParameter parameter, ModelAndViewContainer container,
                                  NativeWebRequest request, WebDataBinderFactory factory) {
        // 从请求头获取 Token，解析出当前用户
        String token = request.getHeader("Authorization");
        return userService.parseUserFromToken(token);
    }
}

// 3. 注册自定义解析器
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Autowired
    private CurrentUserArgumentResolver currentUserArgumentResolver;

    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        resolvers.add(currentUserArgumentResolver);
    }
}

// 4. 在 Controller 中使用
@RestController
public class OrderController {
    @GetMapping("/orders")
    public Result<List<Order>> myOrders(@CurrentUser User currentUser) {
        return Result.success(orderService.findByUserId(currentUser.getId()));
    }
}
```

> 📖 **参考链接**：
> - [Spring Framework Reference](https://docs.spring.io/spring-framework/reference/) -- Spring 框架参考文档（HandlerMethodArgumentResolver 参数解析机制与自定义扩展）

### 2.3 返回值处理原理

Spring MVC 通过 `HandlerMethodReturnValueHandler` 接口处理返回值：

| 返回值处理器 | 支持的返回值 |
|-------------|------------|
| `RequestResponseBodyMethodProcessor` | `@ResponseBody` 注解的方法返回值 |
| `ModelAndViewMethodReturnValueHandler` | `ModelAndView` 类型 |
| `ViewMethodReturnValueHandler` | `View` 类型 |
| `HttpEntityMethodProcessor` | `ResponseEntity` 类型 |

---

## 三、实战应用

### 3.1 统一异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 处理参数校验异常
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidationException(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining(", "));
        return Result.error(400, message);
    }

    // 处理业务异常
    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusinessException(BusinessException e) {
        return Result.error(e.getCode(), e.getMessage());
    }

    // 处理未知异常
    @ExceptionHandler(Exception.class)
    public Result<Void> handleException(Exception e) {
        log.error("系统异常", e);
        return Result.error(500, "服务器内部错误");
    }
}
```

### 3.2 RESTful API 设计规范

> **生活化类比：RESTful API 就像图书馆的图书管理** —— 在传统 API 设计中（动作导向），你想查一本书要访问 `/getBook?id=1`，想借书要访问 `/borrowBook?id=1`，每个操作一个 URL，就像在不同窗口排队办不同业务。而 RESTful API 是资源导向的——把所有书（资源）统一放在 `/books` 下，用 HTTP 方法表示操作意图：`GET /books/1`（查阅）、`POST /books`（入库新书）、`PUT /books/1`（更新书目信息）、`DELETE /books/1`（下架）。就像图书馆用一个统一的索书号系统管理所有书籍，通过不同行为（取阅、归还、录入、销毁）操作同一本书，而不是每种行为设一个独立窗口。URL 标识"是什么"（资源），HTTP 方法表达"做什么"（动作），二者分离使得接口语义清晰、统一、可预测。

| 规范 | 说明 | 示例 |
|------|------|------|
| **URL 命名** | 使用名词复数，小写，用连字符分隔 | `/api/v1/users`、`/api/v1/order-items` |
| **HTTP 方法** | GET（查询）、POST（新增）、PUT（全量更新）、PATCH（部分更新）、DELETE（删除） | `GET /users/1`、`POST /users` |
| **状态码** | 200（成功）、201（创建成功）、400（参数错误）、401（未认证）、403（无权限）、404（未找到）、500（服务器错误） | 创建成功返回 201 |
| **版本管理** | URL 路径版本（`/v1/`）或请求头版本 | `/api/v1/users` |
| **分页参数** | `?page=1&size=20&sort=createdAt,desc` | 统一分页格式 |
| **响应格式** | 统一返回结构（code、message、data） | `{"code":200,"message":"success","data":{...}}` |

**统一响应格式：**

```java
@Data
@AllArgsConstructor
public class Result<T> {
    private int code;
    private String message;
    private T data;

    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", data);
    }

    public static <T> Result<T> error(int code, String message) {
        return new Result<>(code, message, null);
    }
}
```

### 3.3 参数校验

```java
@Data
public class CreateUserRequest {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 20, message = "用户名长度必须在2-20之间")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 20, message = "密码长度必须在6-20之间")
    private String password;

    @Email(message = "邮箱格式不正确")
    private String email;

    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;

    @Min(value = 0, message = "年龄不能小于0")
    @Max(value = 150, message = "年龄不能大于150")
    private Integer age;
}

@RestController
@RequestMapping("/api/v1/users")
public class UserController {
    @PostMapping
    public Result<User> createUser(@Valid @RequestBody CreateUserRequest request) {
        // 参数校验失败时抛出 MethodArgumentNotValidException
        // 由 GlobalExceptionHandler 统一处理
        User user = userService.create(request);
        return Result.success(user);
    }
}
```

**常用校验注解：**

| 注解 | 说明 |
|------|------|
| `@NotNull` | 不能为 null |
| `@NotBlank` | 不能为 null 且不能为空字符串（trim 后） |
| `@NotEmpty` | 不能为 null 且不能为空（集合、字符串） |
| `@Size(min, max)` | 长度范围（字符串、集合） |
| `@Min` / `@Max` | 数值范围 |
| `@Email` | 邮箱格式 |
| `@Pattern` | 正则匹配 |
| `@Positive` / `@Negative` | 正数/负数 |

---

## 四、常见面试题（附答案）

### 1. Spring MVC 的执行流程？

1. 请求到达 `DispatcherServlet`
2. `DispatcherServlet` 通过 `HandlerMapping` 找到对应的 `Handler`
3. 通过 `HandlerAdapter` 调用 `Handler`（Controller 方法）
4. `Handler` 执行业务逻辑，返回 `ModelAndView`
5. `ViewResolver` 将逻辑视图名解析为具体 `View`
6. `View` 渲染，返回响应

### 2. 拦截器（Interceptor）和过滤器（Filter）的区别？

- Filter 是 Servlet 规范，由 Servlet 容器管理；Interceptor 是 Spring 框架的，由 Spring 容器管理
- Filter 作用于所有请求（包括静态资源），Interceptor 仅作用于 Spring MVC 处理的请求
- Filter 在请求进入 Servlet 之前和响应返回之后执行；Interceptor 可以在 Controller 方法前后和视图渲染后执行
- Filter 不能直接获取 Spring Bean，Interceptor 可以

### 3. @ControllerAdvice 和 @ExceptionHandler 的作用？

`@ControllerAdvice` 是全局的 Controller 增强器，配合 `@ExceptionHandler` 实现全局异常处理。当 Controller 抛出异常时，会被 `@ExceptionHandler` 注解的方法捕获处理，返回统一的错误响应格式。

### 4. RESTful API 和传统 API 的区别？

| 维度 | RESTful API | 传统 API |
|------|------------|----------|
| URL 设计 | 资源导向（`/users/1`） | 动作导向（`/getUser?id=1`） |
| HTTP 方法 | GET/POST/PUT/DELETE 语义明确 | 通常只用 GET/POST |
| 状态码 | 充分利用 HTTP 状态码 | 统一 200，错误信息在响应体中 |
| 无状态 | 每次请求独立，不依赖服务端 session | 可能依赖 session |
| 响应格式 | 通常 JSON/XML | 可能 JSON/XML/HTML |

### 5. Spring MVC 如何解决 POST 请求中文乱码？

```java
// 方式1：配置 CharacterEncodingFilter
@Bean
public FilterRegistrationBean<CharacterEncodingFilter> encodingFilter() {
    CharacterEncodingFilter filter = new CharacterEncodingFilter();
    filter.setEncoding("UTF-8");
    filter.setForceEncoding(true);
    FilterRegistrationBean<CharacterEncodingFilter> registration = new FilterRegistrationBean<>();
    registration.setFilter(filter);
    registration.addUrlPatterns("/*");
    return registration;
}

// 方式2：配置文件
// server.servlet.encoding.charset=UTF-8
// server.servlet.encoding.force=true
```

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| @PathVariable 与 URL 占位符不匹配 | 接口报错 | @PathVariable 必须在 URL 中有对应 {xxx} 占位符 | 检查 URL 映射是否包含对应占位符，如 @GetMapping("/users/{id}") |
| GET 请求使用 @RequestBody | 请求参数无法获取 | GET 请求没有请求体，大多数 HTTP 客户端不支持 GET 请求体 | GET 请求使用 @RequestParam 或 @ModelAttribute 接收参数 |
| 统一响应被拦截器重复包装 | 响应体变成 Result<Result<T>> 的嵌套结构 | @RestControllerAdvice 的 ResponseBodyAdvice 对所有返回值重复包装 | 在 supports() 方法中判断返回类型是否已经是 Result，避免重复包装 |

---

> **学习导航**：
> - 返回 [学习路线总览](../../README.md)
> - 本模块其他文件：[05-Spring-Boot笔面试题集](./05-Spring-Boot笔面试题集.md)
> - 实战应用：[电商订单实时统计分析平台](../../extensions/project/01-电商订单实时统计分析平台.md)

