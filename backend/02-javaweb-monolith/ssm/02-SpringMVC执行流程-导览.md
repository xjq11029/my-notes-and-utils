# SpringMVC 执行流程 导览

> 定位：五维框架浓缩提炼 02-SpringMVC执行流程.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-SpringMVC执行流程.md)。
> 前置知识：[Spring核心与IoC原理](./01-Spring核心与IoC原理-导览.md)

---

## 一、核心概念

### 1.1 MVC 设计模式

| 维度 | 内容 |
|------|------|
| 是什么 | 将应用程序分为 Model（模型）、View（视图）、Controller（控制器）三层的架构设计模式 |
| 能做什么 | 分离数据、展示、控制逻辑；各层职责单一；降低耦合；便于维护和扩展 |
| 怎么用 | Model 对应 Service/DAO/Entity，View 对应 JSP/Thymeleaf/JSON，Controller 对应 @Controller 类 |
| 原理和工作流程 | 用户请求到达 Controller，Controller 调用 Model 层处理业务逻辑获取数据，Model 返回处理结果，Controller 选择 View 并传递模型数据，View 渲染展示给用户。核心思想是关注点分离，各层职责单一，修改 Model 不影响 View，修改 View 不影响 Model。SpringMVC 是 Spring 实现的 MVC 框架 |
| 缺点 | 简单应用分层过多增加复杂度；Controller 容易膨胀为业务逻辑容器；前后端分离场景下 View 层概念淡化 |

### 1.2 DispatcherServlet 九大组件

| 维度 | 内容 |
|------|------|
| 是什么 | DispatcherServlet 前端控制器依赖的九个核心组件，协同完成请求处理 |
| 能做什么 | HandlerMapping 查找处理器；HandlerAdapter 执行处理器；HandlerExceptionResolver 处理异常；ViewResolver 解析视图；View 渲染视图；MultipartResolver 处理文件上传；LocaleResolver 国际化；ThemeResolver 主题；FlashMapManager 重定向传参 |
| 怎么用 | 九个组件在 DispatcherServlet.initStrategies() 中按顺序初始化，容器启动时自动加载 |
| 原理和工作流程 | DispatcherServlet 继承 HttpServlet，作为前端控制器统一接收所有请求。请求到达后依次调用 HandlerMapping 查找 Handler 和拦截器链，HandlerAdapter 适配执行 Handler，异常时由 HandlerExceptionResolver 处理，返回 ModelAndView 后 ViewResolver 解析视图名，View 渲染视图返回响应。每个组件都是接口抽象，可替换默认实现。核心组件是 HandlerMapping、HandlerAdapter、ViewResolver 三个 |
| 缺点 | 九个组件职责划分细，理解完整链路需要时间；自定义组件替换默认实现需了解接口细节；组件缺失或未初始化会导致启动失败 |

### 1.3 请求处理完整流程

| 维度 | 内容 |
|------|------|
| 是什么 | 一个 HTTP 请求从客户端发送到 SpringMVC 返回响应的完整处理链路 |
| 能做什么 | 描述请求经过的各组件和处理顺序；定位请求处理各环节的职责 |
| 怎么用 | 请求 → DispatcherServlet → HandlerMapping → HandlerAdapter → Handler → ViewResolver → View → 响应 |
| 原理和工作流程 | 1. 客户端发送请求到达 DispatcherServlet。2. DispatcherServlet 调用 HandlerMapping 根据 URL 查找 Handler 和拦截器链返回 HandlerExecutionChain。3. 执行拦截器 preHandle，返回 false 则中断。4. 通过 HandlerAdapter 调用 Handler 执行业务逻辑返回 ModelAndView。5. ViewResolver 解析逻辑视图名为具体 View 对象。6. View 渲染模型数据到视图模板。7. 执行拦截器 afterCompletion 清理资源。前后端分离场景下 @ResponseBody 方法跳过 ViewResolver 和 View，直接通过 HttpMessageConverter 序列化返回 JSON |
| 缺点 | 流程环节多，单个环节出问题影响全局；前后端分离与传统流程有差异易混淆；调试需逐环节排查 |

### 1.4 常用注解

| 维度 | 内容 |
|------|------|
| 是什么 | SpringMVC 提供的核心注解，用于声明控制器、映射请求、绑定参数 |
| 能做什么 | @Controller/@RestController 声明控制器；@RequestMapping 及其衍生注解映射 URL；@RequestParam/@PathVariable/@RequestBody 绑定参数 |
| 怎么用 | `@RestController @RequestMapping("/api") public class Ctrl { @GetMapping("/{id}") public Result get(@PathVariable Long id) {} }` |
| 原理和工作流程 | @Controller 由 Spring 组件扫描注册为 Bean，@RequestMapping 解析为 RequestMappingInfo 映射 URL 到方法。请求到达时 DispatcherServlet 通过 HandlerMapping 逐条匹配 RequestMappingInfo，找到后通过 HandlerAdapter 调用方法。方法参数由 HandlerMethodArgumentResolver 根据注解解析：@RequestParam 从查询参数获取，@PathVariable 从 URL 路径获取，@RequestBody 从请求体读取并反序列化。@RestController = @Controller + @ResponseBody，方法返回值不走视图直接序列化返回 |
| 缺点 | 注解组合多，@RequestMapping 参数复杂容易写错；@RequestParam 和 @PathVariable 混用易混淆；@RequestBody 要求 Content-Type 为 application/json |

### 1.5 参数绑定原理

| 维度 | 内容 |
|------|------|
| 是什么 | SpringMVC 将 HTTP 请求中的参数自动映射到 Controller 方法参数的过程 |
| 能做什么 | 支持 URL 路径参数、查询参数、请求体、表单数据、请求头、Cookie 等多种参数来源 |
| 怎么用 | `@PathVariable` 绑路径参数；`@RequestParam` 绑查询参数；`@RequestBody` 绑 JSON 请求体 |
| 原理和工作流程 | HandlerAdapter 调用 Handler 时，遍历方法参数列表，调用 HandlerMethodArgumentResolver 解析器链。每个解析器有 supportsParameter 方法判断是否支持该参数类型和注解，若支持则调用 resolveArgument 解析参数值。Spring 内置 26+ 个解析器，包括 RequestParamMethodArgumentResolver（@RequestParam）、PathVariableMethodArgumentResolver（@PathVariable）、RequestResponseBodyMethodProcessor（@RequestBody）等。解析器通过 HttpMessageConverter 进行类型转换，如 String 转 Integer、JSON 转对象 |
| 缺点 | 自定义参数解析器开发成本高；解析器链顺序敏感；转换失败错误信息对用户不友好 |

### 1.6 类型转换

| 维度 | 内容 |
|------|------|
| 是什么 | SpringMVC 将字符串请求参数转换为目标 Java 类型的机制 |
| 能做什么 | 内置默认转换器支持常见类型；自定义 Converter 实现特殊转换；Formatter 支持国际化格式化；@DateTimeFormat/@NumberFormat 注解指定格式 |
| 怎么用 | `@DateTimeFormat(pattern = "yyyy-MM-dd") Date date` |
| 原理和工作流程 | SpringMVC 类型转换基于 Converter SPI 和 Formatter SPI。Converter 负责任意类型到任意类型的转换，Formatter 是 Converter 的特化支持国际化格式化。参数解析时 ConversionService 选择合适的 Converter 执行转换。自定义 Converter 实现 Converter<S, T> 接口并注册到 ConversionService。@DateTimeFormat 和 @NumberFormat 通过 Formatter 实现，注解指定格式后 Spring 自动选择对应 Formatter 转换 |
| 缺点 | 自定义转换器注册后全局生效可能影响其他模块；转换失败异常信息不直观；嵌套对象转换配置复杂 |

### 1.7 拦截器原理与 Filter 区别

| 维度 | 内容 |
|------|------|
| 是什么 | 拦截器是 SpringMVC 的请求拦截机制，在 Controller 方法前后执行；Filter 是 Servlet 规范的过滤器，在请求进入 Servlet 前后执行 |
| 能做什么 | 拦截器三个时机：preHandle 认证鉴权、postHandle 修改 ModelAndView、afterCompletion 清理资源；Filter 在所有请求进入前处理编码、安全等 |
| 怎么用 | 拦截器：`implements HandlerInterceptor` 注册到 WebMvcConfigurer；Filter：`implements Filter` 注册到 FilterRegistrationBean |
| 原理和工作流程 | Filter 是 Servlet 规范组件，由 Servlet 容器管理，不能直接注入 Spring Bean，作用范围是所有请求含静态资源，在请求进入 Servlet 前后执行。Interceptor 是 Spring 框架特有，由 Spring 容器管理，可直接注入 Bean，只作用于 Controller 请求，在 Controller 方法前后和视图渲染后执行。执行顺序：Filter 链 → DispatcherServlet → Interceptor preHandle → Controller → Interceptor postHandle → 视图渲染 → Interceptor afterCompletion。Filter 粒度粗拦截所有请求，Interceptor 粒度细可指定 URL 路径 |
| 缺点 | Filter 获取 Spring Bean 困难；Interceptor 无法拦截非 Controller 请求；二者执行顺序混合时排查复杂；职责重叠导致选择困难 |

### 1.8 @ControllerAdvice 全局异常处理

| 维度 | 内容 |
|------|------|
| 是什么 | SpringMVC 提供的全局异常处理机制，统一拦截所有 Controller 抛出的异常 |
| 能做什么 | 区分业务异常、参数校验异常、系统异常分别处理；统一错误响应格式；配合 @RestControllerAdvice 返回 JSON |
| 怎么用 | `@RestControllerAdvice public class GlobalExceptionHandler { @ExceptionHandler(BusinessException.class) public Result handle() {} }` |
| 原理和工作流程 | @ControllerAdvice 标注的类会被 Spring 扫描为 Bean，其 @ExceptionHandler 方法注册为异常处理器。当 Controller 方法抛出异常时，DispatcherServlet 的异常处理机制会查找匹配的异常处理器，按异常类型匹配（子类优先于父类），调用对应方法处理异常并返回错误响应。@RestControllerAdvice = @ControllerAdvice + @ResponseBody，返回值自动序列化为 JSON。一个应用中可以有多个 @ControllerAdvice 类，可通过 basePackages 指定作用范围 |
| 缺点 | 异常处理逻辑集中易臃肿；多个处理器时优先级不明确；Controller 内部 catch 异常不会触发全局处理器 |

---

## 二、底层原理

### 2.1 DispatcherServlet 初始化流程

| 维度 | 内容 |
|------|------|
| 是什么 | DispatcherServlet 继承 HttpServlet，在容器启动时的初始化过程 |
| 能做什么 | 创建 WebApplicationContext；调用 initStrategies() 初始化九大组件；注册为 Servlet 映射请求路径 |
| 怎么用 | Spring Boot 中通过 DispatcherServletAutoConfiguration 自动注册，映射 "/" |
| 原理和工作流程 | DispatcherServlet 继承 HttpServlet，其 init() 方法在 Servlet 容器启动时调用。初始化流程：1. 创建 WebApplicationContext 加载 Spring 配置；2. 调用 initStrategies() 按顺序初始化九大组件：initMultipartResolver、initLocaleResolver、initThemeResolver、initHandlerMappings、initHandlerAdapters、initHandlerExceptionResolvers、initViewResolvers、initFlashMapManager。每个组件通过 getDefaultStrategy() 获取默认实现或从 Spring 容器中查找自定义实现。初始化完成后注册到 Servlet 容器映射请求路径 |
| 缺点 | 初始化顺序固定，自定义组件必须按接口规范实现；Servlet 容器启动慢时 DispatcherServlet 初始化延迟 |

### 2.2 请求分发核心流程

| 维度 | 内容 |
|------|------|
| 是什么 | DispatcherServlet.doDispatch() 方法的核心逻辑，是请求处理的主流程 |
| 能做什么 | 查找 Handler；获取 HandlerAdapter；执行拦截器；调用 Handler；处理异常；渲染视图 |
| 怎么用 | 请求自动进入 doDispatch 方法，开发者无需手动调用 |
| 原理和工作流程 | doDispatch 核心流程：1. getHandler 通过 HandlerMapping 查找 HandlerExecutionChain（含 Handler 和拦截器）。2. getHandlerAdapter 根据 Handler 类型获取对应的 HandlerAdapter。3. applyPreHandle 执行所有拦截器的 preHandle，任一返回 false 则中断。4. ha.handle 通过 HandlerAdapter 执行 Handler 返回 ModelAndView。5. applyPostHandle 执行拦截器 postHandle。6. processDispatchResult 处理返回结果：有异常则走异常处理，正常则渲染视图。7. triggerAfterCompletion 执行拦截器 afterCompletion 清理资源 |
| 缺点 | doDispatch 方法体量大逻辑复杂；拦截器链多时调试困难；异常处理分散在多个位置 |

### 2.3 参数解析器链

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 HandlerMethodArgumentResolver 链解析 Controller 方法参数的机制 |
| 能做什么 | 按顺序匹配解析器；支持 26+ 内置解析器；可自定义解析器扩展 |
| 怎么用 | 内置解析器自动处理，自定义实现 HandlerMethodArgumentResolver 接口并注册 |
| 原理和工作流程 | HandlerMethodArgumentResolver 接口有两个方法：supportsParameter 判断是否支持该参数，resolveArgument 解析参数值。HandlerAdapter 调用 Handler 前，遍历方法参数调用解析器链，第一个 supportsParameter 返回 true 的解析器负责解析。内置解析器涵盖 @RequestParam、@PathVariable、@RequestBody、@ModelAttribute、@RequestHeader、@CookieValue 等。自定义解析器实现接口后通过 WebMvcConfigurer.addArgumentResolvers 注册 |
| 缺点 | 解析器链顺序影响结果，自定义解析器可能被内置解析器拦截；解析器开发需理解完整的请求上下文 |

---

## 三、实战应用

### 3.1 RESTful API 设计

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 @RestController 使用 RESTful 风格设计 CRUD 接口的最佳实践 |
| 能做什么 | GET 查询、POST 创建、PUT 更新、DELETE 删除；统一 URL 格式；分页查询 |
| 怎么用 | `@GetMapping` 查询；`@PostMapping` 创建；`@PutMapping` 更新；`@DeleteMapping` 删除；`@PathVariable` 获取资源 ID |
| 原理和工作流程 | RESTful API 遵循 HTTP 动词语义：GET 幂等查询，POST 创建资源，PUT 幂等更新，DELETE 删除资源。URL 路径使用名词复数表示资源集合，@PathVariable 获取资源 ID。@RequestBody 接收 JSON 请求体，@Valid 触发参数校验。返回值统一为 Result<T> 格式包含 code、message、data 字段。分页查询使用 @RequestParam 接收 page 和 size 参数 |
| 缺点 | RESTful 风格要求严格，团队规范不一致时混乱；GET 请求参数多时 URL 过长；DELETE 请求体不被一些代理支持 |

### 3.2 拦截器注册与配置

| 维度 | 内容 |
|------|------|
| 是什么 | 实现 WebMvcConfigurer 接口注册拦截器，指定拦截路径和排除路径 |
| 能做什么 | 注册多个拦截器；指定拦截路径和排除路径；设置执行顺序 |
| 怎么用 | `registry.addInterceptor(authInterceptor).addPathPatterns("/api/**").excludePathPatterns("/api/login").order(1)` |
| 原理和工作流程 | 拦截器注册到 InterceptorRegistry 后，Spring 在构建 HandlerMapping 时将拦截器与路径模式绑定。请求到达时，HandlerMapping 根据 URL 匹配路径模式，将匹配的拦截器加入 HandlerExecutionChain。执行顺序由 order 值决定，值越小越先执行。addPathPatterns 指定拦截路径，excludePathPatterns 指定排除路径，先匹配排除再匹配拦截 |
| 缺点 | 路径匹配规则为 Ant 风格，复杂路径容易写错；多个拦截器顺序依赖 order 值，调整不当导致执行顺序错误 |

### 3.3 全局异常处理 + 统一响应

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 @RestControllerAdvice 统一处理异常，返回统一格式 Result<T> 响应 |
| 能做什么 | 区分业务异常、参数校验异常、系统异常；统一错误码和错误信息；返回规范 JSON 格式 |
| 怎么用 | `@ExceptionHandler(BusinessException.class) public Result handle() { return Result.error(code, message); }` |
| 原理和工作流程 | GlobalExceptionHandler 标注 @RestControllerAdvice，@ExceptionHandler 指定处理的异常类型。Controller 抛出异常时，DispatcherServlet 调用异常处理器链，按异常类型精确匹配（BusinessException 优先于 Exception）。每个异常处理器返回统一格式 Result.error(code, message)。参数校验异常 MethodArgumentNotValidException 通过 getBindingResult 获取字段错误信息聚合展示。系统异常 Exception 兜底，记录日志并返回模糊提示避免泄露敏感信息 |
| 缺点 | 异常处理器集中管理，方法增多后类体量膨胀；@ExceptionHandler 方法参数与返回值限制严格；国际化需要额外配置 MessageSource |

---

## 四、常见面试题

### 1. 描述 SpringMVC 的完整执行流程？

| 维度 | 内容 |
|------|------|
| 是什么 | HTTP 请求进入 SpringMVC 到响应返回的完整处理链路 |
| 能做什么 | 描述 DispatcherServlet 和各组件协作流程；区分前后端分离场景 |
| 怎么用 | 请求 → DispatcherServlet → HandlerMapping → HandlerAdapter → Handler → ViewResolver → View → 响应 |
| 原理和工作流程 | 1. 请求到达 DispatcherServlet。2. HandlerMapping 根据 URL 查找 Handler 和拦截器链。3. 执行拦截器 preHandle。4. HandlerAdapter 适配执行 Handler 返回 ModelAndView。5. ViewResolver 解析逻辑视图名为具体 View。6. View 渲染模型数据。7. 执行拦截器 afterCompletion。前后端分离场景下 @ResponseBody 方法跳过视图解析，通过 HttpMessageConverter 直接返回 JSON |
| 缺点 | 流程环节多，面试回答容易遗漏步骤；前后端分离与传统流程需明确区分 |

### 2. Filter 和 Interceptor 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | Servlet 规范的 Filter 与 Spring 框架的 Interceptor 两种拦截机制对比 |
| 能做什么 | Filter 由 Servlet 容器管理拦截所有请求；Interceptor 由 Spring 容器管理只拦截 Controller；执行时机和注入能力不同 |
| 怎么用 | Filter：`implements Filter`；Interceptor：`implements HandlerInterceptor` |
| 原理和工作流程 | Filter 是 Servlet 规范，由 Servlet 容器管理，作用于所有请求含静态资源，在请求进入 Servlet 前后执行，不能直接注入 Spring Bean。Interceptor 是 Spring 框架特有，由 Spring 容器管理，只作用于 Controller 请求，在 Controller 方法前后和视图渲染后执行，可直接注入 Bean。执行顺序：Filter 链 → DispatcherServlet → Interceptor preHandle → Controller → Interceptor postHandle → 视图渲染 → Interceptor afterCompletion |
| 缺点 | 职责重叠时不易选择；Filter 获取 Bean 麻烦；Interceptor 无法拦截静态资源请求 |

### 3. @Controller 和 @RestController 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | @RestController = @Controller + @ResponseBody 组合注解 |
| 能做什么 | @Controller 方法返回值走视图解析；@RestController 方法返回值直接序列化为 JSON |
| 怎么用 | 前后端分离项目统一使用 @RestController |
| 原理和工作流程 | @Controller 标注类为控制器，方法返回 String 被 ViewResolver 解析为视图路径，返回 ModelAndView 包含视图和数据。@ResponseBody 标注后方法返回值通过 HttpMessageConverter 序列化为 JSON/XML 写入响应体跳过视图解析。@RestController 组合二者，所有方法自动应用 @ResponseBody，适合构建 RESTful API。前后端分离场景下后端只需返回 JSON 数据，因此统一使用 @RestController |
| 缺点 | 所有方法都返回 JSON 无法混合视图渲染；需要服务端渲染时不能用 @RestController |

### 4. @RequestParam 和 @RequestBody 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 两种不同的参数绑定方式：@RequestParam 绑查询参数和表单字段，@RequestBody 绑 JSON 请求体 |
| 能做什么 | @RequestParam 用于 GET 查询参数和表单提交；@RequestBody 用于 POST/PUT 的 JSON 请求体；支持默认值和必填校验 |
| 怎么用 | `@RequestParam(defaultValue = "1") int page`；`@RequestBody @Valid User user` |
| 原理和工作流程 | @RequestParam 由 RequestParamMethodArgumentResolver 解析，从 URL 查询字符串或表单 body 中按参数名提取值，支持 defaultValue 默认值、required 必填校验。@RequestBody 由 RequestResponseBodyMethodProcessor 解析，读取请求体 InputStream 并通过 HttpMessageConverter 反序列化，Content-Type 必须为 application/json。@RequestParam 一个方法可以有多个，@RequestBody 一个方法只能有一个因为请求体只能读取一次 |
| 缺点 | @RequestParam 多参数时方法签名冗长；@RequestBody 读取后请求体为空无法再次读取；Content-Type 不匹配导致反序列化失败 |

### 5. SpringMVC 如何处理参数绑定？

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 HandlerMethodArgumentResolver 解析器链将 HTTP 请求参数映射到方法参数 |
| 能做什么 | 支持 26+ 内置解析器覆盖各种参数类型；可自定义解析器扩展 |
| 怎么用 | 内置解析器自动处理，自定义：`implements HandlerMethodArgumentResolver` 并注册 |
| 原理和工作流程 | HandlerAdapter 调用 Handler 前遍历方法参数，调用解析器链。每个解析器 supportsParameter 判断是否支持该参数类型和注解，支持则 resolveArgument 解析参数值。常见解析器：RequestParamMethodArgumentResolver 处理 @RequestParam、PathVariableMethodArgumentResolver 处理 @PathVariable、RequestResponseBodyMethodProcessor 处理 @RequestBody。解析器通过 HttpMessageConverter 和 ConversionService 完成类型转换 |
| 缺点 | 自定义解析器开发成本高；解析器链顺序敏感；转换失败错误信息不直观 |

### 6. 拦截器的三个方法分别什么时候执行？

| 维度 | 内容 |
|------|------|
| 是什么 | preHandle、postHandle、afterCompletion 三个拦截器方法的执行时机 |
| 能做什么 | preHandle 认证鉴权；postHandle 修改 ModelAndView；afterCompletion 清理资源 |
| 怎么用 | `preHandle` 返回 true 放行 false 中断；`postHandle` 操作 ModelAndView；`afterCompletion` 清理 ThreadLocal |
| 原理和工作流程 | preHandle 在 Controller 方法执行前调用，返回 false 则中断请求后续拦截器和 Controller 不执行。postHandle 在 Controller 执行后视图渲染前调用，可修改 ModelAndView 添加公共数据。afterCompletion 在视图渲染后调用，无论是否异常都会执行，适合清理 ThreadLocal 等资源。执行顺序：Interceptor1.preHandle → Interceptor2.preHandle → Controller → Interceptor2.postHandle → Interceptor1.postHandle → 视图渲染 → Interceptor2.afterCompletion → Interceptor1.afterCompletion |
| 缺点 | preHandle 返回 false 后 postHandle 不执行容易误解；异步请求拦截器行为不同；afterCompletion 的异常参数可能为 null 需判空 |

### 7. 如何实现全局异常处理？

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 @RestControllerAdvice + @ExceptionHandler 实现全局统一的异常处理 |
| 能做什么 | 区分业务异常、参数校验异常、系统异常；统一错误响应格式；避免 Controller 层 try-catch |
| 怎么用 | `@RestControllerAdvice public class GlobalExceptionHandler { @ExceptionHandler(Exception.class) public Result handle() {} }` |
| 原理和工作流程 | @ControllerAdvice 标注的类被 Spring 扫描为全局异常处理器，其 @ExceptionHandler 方法注册到异常处理器链。Controller 抛出异常时，DispatcherServlet 查找匹配的异常处理器，按异常类型精确匹配子类优先级高于父类。每个处理器返回统一格式 Result.error 响应。@RestControllerAdvice 是 @ControllerAdvice + @ResponseBody 的组合，返回值自动序列化为 JSON。多个处理器类时可通过 basePackages 指定作用范围避免冲突 |
| 缺点 | 异常处理器集中导致类膨胀；@ExceptionHandler 方法参数限定严格；Controller 内部 catch 异常不触发全局处理器 |

### 8. SpringMVC 中如何处理跨域问题？

| 维度 | 内容 |
|------|------|
| 是什么 | 浏览器同源策略限制下，SpringMVC 三种处理跨域请求的方式 |
| 能做什么 | @CrossOrigin 注解精确控制；WebMvcConfigurer 全局配置；Filter 添加 CORS 响应头拦截所有请求 |
| 怎么用 | `@CrossOrigin(origins = "http://localhost:3000")`；`addCorsMappings()` 全局配置 |
| 原理和工作流程 | 跨域问题的本质是浏览器同源策略限制，跨域请求会先发送 OPTIONS 预检请求。方案一：@CrossOrigin 注解在 Controller 类或方法上，指定 allowOrigins、allowMethods、allowHeaders 等，Spring 在 HandlerMapping 阶段识别并添加 CORS 响应头。方案二：重写 WebMvcConfigurer.addCorsMappings 全局配置 CORS 映射规则。方案三：使用 Filter 在所有请求前添加 CORS 响应头，适用于拦截静态资源等非 Controller 请求 |
| 缺点 | 三种方式混合使用容易冲突；@CrossOrigin 粒度细但重复配置多；全局配置过于宽泛有安全风险 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | SpringMVC 开发中 @RequestBody 空、拦截器不生效、异常处理失效、404、静态资源拦截等常见问题汇总 |
| 能做什么 | 识别 Content-Type 不匹配导致的请求体为空；排查拦截器注册遗漏；确保异常处理器在扫描路径内；检查包扫描配置；配置静态资源处理器 |
| 怎么用 | 前端设置正确 Content-Type；实现 WebMvcConfigurer 注册拦截器；确保异常处理器在扫描路径；检查 @ComponentScan 配置；配置 default-servlet-handler |
| 原理和工作流程 | @RequestBody 为空通常因为 Content-Type 不是 application/json，前端须设置正确的请求头。拦截器不生效因为未注册到 WebMvcConfigurer.addInterceptors。@ExceptionHandler 不生效因为异常处理器不在 Spring 扫描范围内或异常被 Controller 内部 catch。请求 404 因为 @ComponentScan 不包含 Controller 所在包。静态资源被拦截因为 DispatcherServlet 映射 "/" 拦截了所有请求，需配置默认 Servlet 处理器转发静态资源请求 |
| 缺点 | 问题排查需要理解完整请求链路；配置遗漏导致功能静默失效；问题现象可能相似但原因不同 |

---

> [返回原文](./02-SpringMVC执行流程.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)