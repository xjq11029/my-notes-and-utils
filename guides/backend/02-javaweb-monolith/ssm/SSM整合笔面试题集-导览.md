# SSM 整合笔面试题集 导览

> 定位：五维框架浓缩提炼 SSM整合笔面试题集.md 全部内容小节，快速查阅与复习。
> 用法：每个题型对应一张概要表格，每道题目提取所考知识点生成五维表格，需要深入理解时跳转 [原文](./SSM整合笔面试题集.md)。
> 前置知识：[Spring核心与IoC原理](./01-Spring核心与IoC原理-导览.md)、[SpringMVC执行流程](./02-SpringMVC执行流程-导览.md)、[MyBatis整合与配置](./03-MyBatis整合与配置-导览.md)

---

## 一、选择题（15 题，附解析）

| 维度 | 内容 |
|------|------|
| 是什么 | SSM 整合笔面试选择题题型，覆盖 Spring 核心特性、父子容器、事务配置、整合组件、注解辨析等核心知识点 |
| 能做什么 | 考查基础概念辨析；考查整合配置细节；考查注解用法理解；通过选项干扰检验掌握程度 |
| 怎么用 | 单选四选一，附答案与解析，难度分基础中档拔高三级 |
| 原理和工作流程 | 选择题侧重考查 SSM 整合核心知识点的精确记忆和辨析，涵盖 Spring 核心特性识别、父子容器 Bean 管理范围、容器访问规则、@Transactional 注解位置、SqlSessionFactoryBean 作用、@MapperScan 注解、DispatcherServlet 九大组件、Filter 与 Interceptor 顺序、@RestController 等效关系、事务失效原因、@RequestParam 与 @PathVariable 区别、Mapper 接口特点、preHandle 返回 false 行为、@RequestBody 反序列化、Controller 被父容器扫描后果等 15 个知识点。每题附解析说明正确选项依据和错误选项辨析 |
| 缺点 | 选择题难以考查综合应用能力；选项暗示性强可能猜对；侧重记忆而非理解；无法反映代码实践能力 |

### 1. ★ Spring 框架核心特性

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 核心特性包括 IoC 控制反转和 AOP 面向切面编程，ORM 是外部框架特性 |
| 能做什么 | 区分 Spring 原生特性与集成特性；IoC/DI 解耦依赖；AOP 处理横切关注点 |
| 怎么用 | IoC 通过 @Component 管理 Bean；AOP 通过 @Aspect 定义切面；ORM 通过集成 MyBatis/Hibernate 实现 |
| 原理和工作流程 | Spring 核心特性是 IoC（控制反转）和 DI（依赖注入），以及 AOP（面向切面编程）。ORM（对象关系映射）是 Hibernate、MyBatis 等框架的特性，Spring 通过 spring-orm 模块提供集成支持，但 ORM 本身不是 Spring 框架的核心特性。Spring 的设计理念是简化开发，IoC 负责对象管理，AOP 负责横切逻辑 |
| 缺点 | 新手容易混淆 Spring 原生特性和集成特性；Spring 生态庞大各模块边界模糊 |

### 2. ★★ ContextLoaderListener 容器管理范围

| 维度 | 内容 |
|------|------|
| 是什么 | ContextLoaderListener 创建根容器，管理 Service、DAO、事务管理器等非 Web 层 Bean |
| 能做什么 | 管理 Service 业务层、DAO 持久层、事务管理器、数据源；不管理 Controller |
| 怎么用 | ContextLoaderListener 加载 applicationContext.xml 创建父容器，排除 Controller 扫描 |
| 原理和工作流程 | ContextLoaderListener 实现 ServletContextListener，在 Web 容器启动时创建 Root WebApplicationContext。它的职责是管理非 Web 层 Bean：Service、DAO、事务管理器、数据源等。Controller 由 DispatcherServlet 创建的子容器管理。父子容器通过 ServletContext 传递引用，子容器可访问父容器 Bean |
| 缺点 | 容器职责划分需理解父子容器关系；配置错误导致 Bean 归属错误 |

### 3. ★★ 父子容器访问规则

| 维度 | 内容 |
|------|------|
| 是什么 | 子容器可以访问父容器 Bean，父容器不能访问子容器 Bean |
| 能做什么 | Controller 可以注入 Service；Service 不能注入 Controller；子容器优先查找自身 Bean |
| 怎么用 | `@Autowired UserService userService` 在 Controller 中正常注入父容器 Service |
| 原理和工作流程 | 子容器（Servlet WebApplicationContext）创建时，将父容器（Root WebApplicationContext）设置为 parent。获取 Bean 时子容器先在自身 BeanFactory 查找，找不到则委托父容器 BeanFactory 查找。因此 Controller 可以注入 Service。但父容器查找 Bean 时不会委托子容器，所以 Service 不能注入 Controller。父子容器不是相互隔离互不可访问，也不是共享同一个 Bean，而是单向委托关系 |
| 缺点 | 单向访问规则容易误解；Service 误注入 Controller 会导致启动失败 |

### 4. ★★ @Transactional 注解位置

| 维度 | 内容 |
|------|------|
| 是什么 | @Transactional 应当放在 Service 层，放在 Controller 层可能导致事务失效 |
| 能做什么 | 事务注解在 Service 层确保事务代理正常生效；避免 Controller 层事务失效 |
| 怎么用 | `@Service @Transactional(rollbackFor = Exception.class) public class OrderService { }` |
| 原理和工作流程 | SSM 整合中事务代理在父容器中由 @EnableTransactionManagement 和 TransactionInterceptor 生效。Controller 由子容器管理，事务代理在子容器中可能不生效。且 Controller 不应承载业务逻辑和事务边界，职责是接收请求调用 Service。@Transactional 放在 DAO 层粒度太细无法保证多个 DAO 操作在同一事务中。放在 Service 层是最佳实践，一个 Service 方法作为一个事务边界 |
| 缺点 | 放在 Controller 层事务静默失效难以排查；新手不了解分层原则容易放错位置 |

### 5. ★ SqlSessionFactoryBean 作用

| 维度 | 内容 |
|------|------|
| 是什么 | SqlSessionFactoryBean 是 Spring 整合 MyBatis 的核心 FactoryBean，用于创建 SqlSessionFactory |
| 能做什么 | 封装 MyBatis 配置（DataSource、Mapper XML、别名、插件）；产出 SqlSessionFactory 实例 |
| 怎么用 | `@Bean public SqlSessionFactoryBean sqlSessionFactory(DataSource ds) { factoryBean.setDataSource(ds); ... }` |
| 原理和工作流程 | SqlSessionFactoryBean 实现 FactoryBean 接口，getObject() 调用 SqlSessionFactoryBuilder.build() 创建 SqlSessionFactory。配置 DataSource、mapperLocations（Mapper XML 路径）、typeAliasesPackage（实体类别名）、configLocation（MyBatis 全局配置）、plugins（插件）。SqlSessionFactoryBuilder 是 MyBatis 原生 API 不是 Spring 整合类，SqlSessionTemplate 是 SqlSession 的线程安全封装 |
| 缺点 | 配置项多容易遗漏；xml 方式和 Java Config 方式配置差异大 |

### 6. ★★ @MapperScan 注解

| 维度 | 内容 |
|------|------|
| 是什么 | @MapperScan 注解用于自动扫描指定包下 MyBatis Mapper 接口并注册为 Spring Bean |
| 能做什么 | 指定 Mapper 接口包路径；内部通过 MapperScannerConfigurer 实现扫描；替代 @ComponentScan 单独扫描 Mapper |
| 怎么用 | `@Configuration @MapperScan("com.example.mapper") public class SpringConfig { }` |
| 原理和工作流程 | @MapperScan 通过 @Import(MapperScannerRegistrar.class) 导入注册器，注册器在 BeanDefinition 注册阶段创建 ClassPathMapperScanner 扫描 basePackage 下接口，为每个接口创建 MapperFactoryBean 的 BeanDefinition。@ComponentScan 不会自动扫描 Mapper 接口注册为 Bean，@ServiceScan 和 @RepositoryScan 不是 Spring 标准注解。@MapperScan 是 mybatis-spring 提供的专用注解 |
| 缺点 | 扫描包路径写错 Mapper 不注册；和 @ComponentScan 混用容易混淆；多数据源时需配置多个 |

### 7. ★★ DispatcherServlet 九大组件

| 维度 | 内容 |
|------|------|
| 是什么 | DispatcherServlet 依赖的九个核心组件，TransactionManager 不属于其中 |
| 能做什么 | HandlerMapping 查找处理器；HandlerAdapter 执行处理器；ViewResolver 解析视图；View 渲染视图；其他辅助组件 |
| 怎么用 | 九大组件在 initStrategies() 中按顺序初始化，容器启动时自动加载 |
| 原理和工作流程 | DispatcherServlet 九大组件：HandlerMapping（查找 Handler 和拦截器）、HandlerAdapter（适配执行 Handler）、HandlerExceptionResolver（处理异常）、ViewResolver（解析视图）、View（渲染视图）、MultipartResolver（文件上传）、LocaleResolver（国际化）、ThemeResolver（主题）、FlashMapManager（重定向传参）。TransactionManager 是 Spring 事务管理组件，不属于 DispatcherServlet |
| 缺点 | 组件多职责细，理解完整链路需要时间；自定义替换默认实现需了解接口细节 |

### 8. ★★ Filter 与 Interceptor 执行顺序

| 维度 | 内容 |
|------|------|
| 是什么 | Filter 在请求进入 Servlet 前执行，先于 Interceptor，而不是同时或随机 |
| 能做什么 | Filter 处理所有请求含静态资源；Interceptor 处理 Controller 请求；执行顺序固定 |
| 怎么用 | Filter 配置在 FilterRegistrationBean；Interceptor 注册到 WebMvcConfigurer |
| 原理和工作流程 | Filter 是 Servlet 规范组件，由 Servlet 容器管理，在请求进入 Servlet 前执行 doFilter。Interceptor 是 SpringMVC 组件，在 DispatcherServlet 内部 Controller 方法前后执行。执行顺序：Filter 链 → DispatcherServlet → Interceptor preHandle → Controller → Interceptor postHandle → 视图渲染 → Interceptor afterCompletion。Filter 先于 Interceptor 是固定的，不是同时或随机 |
| 缺点 | 顺序固定但理解易混淆；多个 Filter 和 Interceptor 混合时顺序复杂 |

### 9. ★ @RestController 等价关系

| 维度 | 内容 |
|------|------|
| 是什么 | @RestController = @Controller + @ResponseBody 组合注解 |
| 能做什么 | 标识 Controller 类；所有方法返回值序列化为 JSON/XML 写入响应体；不经过视图解析 |
| 怎么用 | `@RestController @RequestMapping("/api") public class Ctrl { }` |
| 原理和工作流程 | @Controller 将类标记为控制器由 Spring 扫描注册，方法返回值默认走视图解析。@ResponseBody 标注后方法返回值通过 HttpMessageConverter 序列化直接写入响应体。@RestController 组合两者，所有方法自动应用 @ResponseBody，适合 RESTful API。不是等价于 @Service + @Controller 或 @Component |
| 缺点 | 所有方法都返回 JSON 无法混合视图渲染；不适用服务端渲染场景 |

### 10. ★★ 事务失效原因排除

| 维度 | 内容 |
|------|------|
| 是什么 | SSM 整合中事务失效的常见原因不包括 DataSource 配置连接池，连接池是正常配置 |
| 能做什么 | 识别真正的失效原因：未开启事务、注解位置错误、包扫描冲突、方法非 public、异常被吞 |
| 怎么用 | 检查 @EnableTransactionManagement、@Transactional 位置、包扫描隔离、方法可见性、异常处理 |
| 原理和工作流程 | 事务失效原因：① 未配置 @EnableTransactionManagement 开启事务代理；② @Transactional 放在 Controller 层；③ 父子容器包扫描未隔离；④ 方法非 public；⑤ 异常被 catch 未抛出。DataSource 配置连接池（如 Druid、HikariCP）是正常配置，不会导致事务失效。连接池管理的是连接复用，事务管理的是连接上的事务状态 |
| 缺点 | 失效原因多需逐一排查；DataSource 配置错误会导致连接失败但不是事务失效 |

### 11. ★★ @RequestParam 与 @PathVariable 区别

| 维度 | 内容 |
|------|------|
| 是什么 | @RequestParam 获取 URL 查询参数（?key=value），@PathVariable 获取 URL 路径变量（/path/{var}） |
| 能做什么 | @RequestParam 绑查询参数和表单字段；@PathVariable 绑 RESTful URL 路径变量 |
| 怎么用 | `@RequestParam(defaultValue = "1") int page`；`@PathVariable Long id` |
| 原理和工作流程 | @RequestParam 由 RequestParamMethodArgumentResolver 解析，从 URL 查询字符串或表单 body 提取参数值，支持 defaultValue 和 required。@PathVariable 由 PathVariableMethodArgumentResolver 解析，从 URL 路径模板匹配变量提取值。两者功能不同，不可互换。@RequestParam 不获取请求体，@PathVariable 不获取查询参数 |
| 缺点 | 功能相似容易混淆；GET 请求参数多时 URL 过长；RESTful 路径变量命名需规范 |

### 12. ★★ MyBatis Mapper 接口特点

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis Mapper 接口不需要实现类，方法名与 XML id 一致，支持注解配置，不强制继承 BaseMapper |
| 能做什么 | 接口由 MyBatis 动态代理生成实现；方法名对应 XML 中 SQL 语句 ID；@Select 注解可替代 XML |
| 怎么用 | `public interface UserMapper { User selectById(Long id); }` |
| 原理和工作流程 | MyBatis Mapper 接口不需要编写实现类，MyBatis 通过 JDK 动态代理生成代理对象执行 SQL。方法名必须与 XML 中 statement id 一致。接口方法也可使用 @Select、@Insert 等注解代替 XML 配置。继承 BaseMapper 是 MyBatis-Plus 的特性，不是 MyBatis 原生的要求。MyBatis 原生 Mapper 不需要继承任何类 |
| 缺点 | 方法名与 XML id 不一致时报错不直观；纯注解方式复杂 SQL 可读性差 |

### 13. ★★ preHandle 返回 false 行为

| 维度 | 内容 |
|------|------|
| 是什么 | preHandle 返回 false 会中断请求，后续拦截器和 Controller 都不执行 |
| 能做什么 | 认证失败时中断请求；权限不足时拒绝访问；提前返回错误响应 |
| 怎么用 | `if (token == null) { response.setStatus(401); return false; }` |
| 原理和工作流程 | 拦截器 preHandle 返回 false 时，DispatcherServlet 中断请求处理链。后续拦截器的 preHandle 不会执行，Controller 方法不会执行，所有拦截器的 postHandle 都不会执行。但已执行过的拦截器的 afterCompletion 仍会执行以清理资源。返回 false 不会自动抛出异常，而是由开发者在 preHandle 中自行处理响应 |
| 缺点 | 返回 false 后 postHandle 不执行容易误解；需手动设置响应状态码和内容 |

### 14. ★★ @RequestBody 反序列化

| 维度 | 内容 |
|------|------|
| 是什么 | @RequestBody 通过 HttpMessageConverter 将请求体反序列化为 Java 对象 |
| 能做什么 | 接收 JSON/XML 请求体；一个方法只能有一个；不支持默认值；Content-Type 必须为 application/json |
| 怎么用 | `public Result create(@RequestBody @Valid User user) { }` |
| 原理和工作流程 | @RequestBody 由 RequestResponseBodyMethodProcessor 解析，读取请求体 InputStream 所有字节，通过 HttpMessageConverter（如 MappingJackson2HttpMessageConverter）反序列化为目标类型。因为请求体 InputStream 只能读取一次，所以一个方法只能有一个 @RequestBody 参数。不支持设置默认值，因为请求体内容要么有要么没有。用于接收 JSON 请求体，不是 URL 查询参数 |
| 缺点 | 请求体只能读取一次无法重复读；Content-Type 不匹配反序列化失败；大请求体有性能开销 |

### 15. ★★★ Controller 被父容器扫描后果

| 维度 | 内容 |
|------|------|
| 是什么 | Controller 被父容器扫描到会导致事务代理失效，而非应用启动失败或 Mapper 注入失败 |
| 能做什么 | 识别包扫描冲突的后果；理解事务代理在父子容器中的差异 |
| 怎么用 | 父容器 @ComponentScan 配置 excludeFilters 排除 Controller 注解 |
| 原理和工作流程 | 如果 Controller 被父容器扫描到，Controller 实例在父容器中创建。同时子容器也扫描 Controller 创建实例，两个容器中存在两个 Controller Bean。父容器中 Service 有事务代理，但 Controller 的 @Transactional 在父容器中本就可能不生效（因为 Controller 不应承载事务）。更重要的是，当子容器中 Controller 也存在时，事务代理链可能不完整。应用通常能启动不报错，但事务功能静默失效，这是最隐蔽的问题 |
| 缺点 | 问题隐蔽不报错但功能异常；排查需要理解父子容器和事务代理机制 |

---

## 二、简答题（10 题，附要点）

| 维度 | 内容 |
|------|------|
| 是什么 | SSM 整合笔面试简答题题型，要求用要点形式阐述核心原理和整合配置 |
| 能做什么 | 考查父子容器关系理解；考查整合组件配置；考查事务失效排查；考查组件对比辨析 |
| 怎么用 | 简答题附要点答案，难度中档为主 |
| 原理和工作流程 | 简答题侧重考查 SSM 整合的理解深度，涵盖父子容器关系、SqlSessionFactoryBean 配置、Mapper 扫描配置、事务失效原因、九大组件、Filter 与 Interceptor 区别、全局异常处理、参数绑定区别、DAO 注入失败排查、包扫描隔离配置等 10 个知识点。每题附要点答案列出核心要点供评分参考 |
| 缺点 | 评分主观性强；要点遗漏难以全面覆盖；侧重记忆要点而非实际应用 |

### 1. ★★ SSM 整合中父子容器关系

| 维度 | 内容 |
|------|------|
| 是什么 | 父子容器关系：父容器管理非 Web 层 Bean，子容器管理 Web 层 Bean，子容器可访问父容器 |
| 能做什么 | 隔离 Web 层和非 Web 层；子容器注入父容器 Service；避免 Controller 被父容器扫描 |
| 怎么用 | 父容器由 ContextLoaderListener 创建；子容器由 DispatcherServlet 创建；包扫描隔离 |
| 原理和工作流程 | 父容器（Root WebApplicationContext）由 ContextLoaderListener 创建，管理 Service、DAO、事务、数据源等。子容器（Servlet WebApplicationContext）由 DispatcherServlet 创建，管理 Controller、视图解析等。子容器可访问父容器 Bean（Controller 注入 Service），父容器不能访问子容器 Bean。分开的原因：隔离不同层 Bean，避免 Controller 被父容器扫描导致事务失效，子容器专注 Web 层处理 |
| 缺点 | 父子关系抽象难理解；配置不当导致事务失效；两个容器配置分离增加维护成本 |

### 2. ★★ SqlSessionFactoryBean 作用和配置

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 整合 MyBatis 的 FactoryBean，封装 MyBatis 配置创建 SqlSessionFactory |
| 能做什么 | 设置 DataSource、Mapper XML 路径、实体类别名、全局配置、插件 |
| 怎么用 | `@Bean public SqlSessionFactoryBean sf(DataSource ds) { sf.setDataSource(ds); sf.setMapperLocations(...); }` |
| 原理和工作流程 | SqlSessionFactoryBean 实现 FactoryBean 接口，getObject() 调用 SqlSessionFactoryBuilder.build() 创建 SqlSessionFactory。必配 dataSource 指定数据源；mapperLocations 指定 Mapper XML 文件路径支持通配符；typeAliasesPackage 指定实体类别名扫描包；configLocation 指定 MyBatis 全局配置文件；plugins 注册插件如 PageHelper。Spring 容器启动时调用 getObject() 获取实例注册为 Bean |
| 缺点 | 配置项多容易遗漏；Mapper XML 路径通配符写错导致映射失败；多数据源需多个 SqlSessionFactory |

### 3. ★★ Mapper 接口自动扫描配置

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 @MapperScan 注解或 MapperScannerConfigurer 自动扫描 Mapper 接口注册为 Bean |
| 能做什么 | 指定包路径扫描 Mapper 接口；为每个接口创建 MapperFactoryBean；通过 SqlSession.getMapper 生成代理 |
| 怎么用 | `@MapperScan("com.example.mapper")` 或 `new MapperScannerConfigurer().setBasePackage("com.example.mapper")` |
| 原理和工作流程 | @MapperScan 内部通过 @Import(MapperScannerRegistrar.class) 在 BeanDefinition 注册阶段创建 ClassPathMapperScanner 扫描指定包下接口，为每个接口创建 MapperFactoryBean 的 BeanDefinition。MapperFactoryBean 是 FactoryBean，getObject() 调用 sqlSession.getMapper(mapperInterface) 获取 MyBatis 生成的代理对象。MapperScannerConfigurer 实现 BeanDefinitionRegistryPostProcessor 在更早的阶段执行相同的逻辑 |
| 缺点 | 扫描包路径写错 Mapper 不注册；与 @ComponentScan 混用易混淆；多个数据源需配置多个扫描器 |

### 4. ★★ SSM 整合事务失效原因

| 维度 | 内容 |
|------|------|
| 是什么 | SSM 整合中 @Transactional 不生效的六种常见原因汇总 |
| 能做什么 | 识别配置遗漏、注解位置错误、包扫描冲突、方法可见性、异常处理、代理调用问题 |
| 怎么用 | 检查 @EnableTransactionManagement、@Transactional 位置、包扫描隔离、方法 public、异常抛出 |
| 原理和工作流程 | 六种常见原因：① 忘记配置 @EnableTransactionManagement 或 <tx:annotation-driven/>，事务代理未开启。② @Transactional 放在 Controller 层，Controller 可能被父容器扫描导致事务代理失效。③ 父子容器包扫描未隔离，Controller 被父容器扫描，事务代理链不完整。④ 方法非 public，Spring AOP 只代理 public 方法。⑤ 异常被 catch 未抛出，代理层检测不到异常。⑥ 同类方法内部调用 this.method() 不走代理对象 |
| 缺点 | 多种原因可能同时存在；包扫描冲突问题隐蔽不报错；排查需理解完整链路 |

### 5. ★★ DispatcherServlet 九大组件

| 维度 | 内容 |
|------|------|
| 是什么 | DispatcherServlet 依赖的九个核心组件，核心是 HandlerMapping、HandlerAdapter、ViewResolver |
| 能做什么 | HandlerMapping 查找处理器；HandlerAdapter 执行处理器；ViewResolver 解析视图；其余辅助 |
| 怎么用 | 九大组件在 initStrategies() 按顺序初始化，Spring Boot 自动配置 |
| 原理和工作流程 | 九大组件：HandlerMapping（根据 URL 查找 Handler 和拦截器）、HandlerAdapter（适配执行不同类型的 Handler）、HandlerExceptionResolver（处理 Handler 执行异常）、ViewResolver（解析逻辑视图名为具体 View）、View（渲染视图）、MultipartResolver（处理文件上传）、LocaleResolver（国际化）、ThemeResolver（主题）、FlashMapManager（重定向传参）。核心三个是 HandlerMapping、HandlerAdapter、ViewResolver，覆盖请求处理主流程 |
| 缺点 | 组件多理解成本高；自定义替换默认实现需了解接口；组件缺失启动失败 |

### 6. ★★ Filter 与 Interceptor 区别

| 维度 | 内容 |
|------|------|
| 是什么 | Filter 是 Servlet 规范组件，Interceptor 是 Spring 框架组件，执行顺序 Filter 先于 Interceptor |
| 能做什么 | Filter 拦截所有请求含静态资源；Interceptor 只拦截 Controller 请求；注入能力不同 |
| 怎么用 | Filter 实现 Filter 接口注册；Interceptor 实现 HandlerInterceptor 接口注册到 WebMvcConfigurer |
| 原理和工作流程 | Filter 是 Servlet 规范由 Servlet 容器管理，作用于所有请求，在请求进入 Servlet 前后执行，不能直接注入 Spring Bean。Interceptor 是 Spring 框架特有由 Spring 容器管理，只作用于 Controller 请求，在 Controller 方法前后和视图渲染后执行，可直接注入 Bean。执行顺序：Filter → DispatcherServlet → Interceptor preHandle → Controller → Interceptor postHandle → 视图渲染 → Interceptor afterCompletion |
| 缺点 | 职责重叠时不易选择；Filter 获取 Bean 麻烦；Interceptor 无法拦截静态资源请求 |

### 7. ★★ 全局异常处理实现

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 @RestControllerAdvice + @ExceptionHandler 实现全局统一的异常处理 |
| 能做什么 | 区分业务异常、参数校验异常、系统异常；统一错误码和错误信息；返回规范 JSON 格式 |
| 怎么用 | `@RestControllerAdvice public class GlobalExceptionHandler { @ExceptionHandler(BusinessException.class) public Result handle() {} }` |
| 原理和工作流程 | @ControllerAdvice 标注的类被 Spring 扫描为全局异常处理器。@ExceptionHandler 方法注册到异常处理器链，Controller 抛出异常时 DispatcherServlet 查找匹配的异常处理器，按异常类型精确匹配。每个处理器返回统一格式 Result.error 响应。@RestControllerAdvice = @ControllerAdvice + @ResponseBody，返回值自动序列化为 JSON |
| 缺点 | 异常处理器集中导致类膨胀；Controller 内部 catch 异常不触发全局处理器；多个处理器优先级不明确 |

### 8. ★★ @RequestParam 与 @RequestBody 区别

| 维度 | 内容 |
|------|------|
| 是什么 | @RequestParam 获取查询参数和表单字段，@RequestBody 获取 JSON 请求体 |
| 能做什么 | @RequestParam 支持默认值必填校验，一个方法多个；@RequestBody 反序列化 JSON，一个方法一个 |
| 怎么用 | `@RequestParam(defaultValue = "1") int page`；`@RequestBody @Valid User user` |
| 原理和工作流程 | @RequestParam 由 RequestParamMethodArgumentResolver 解析，从 URL 查询字符串或表单 body 提取参数，支持 defaultValue 和 required。@RequestBody 由 RequestResponseBodyMethodProcessor 解析，读取请求体 InputStream 通过 HttpMessageConverter 反序列化，因为请求体只能读取一次所以一个方法只能有一个，不支持默认值。Content-Type 必须为 application/json |
| 缺点 | 功能相似容易混淆；@RequestBody 不支持默认值；请求体只能读取一次 |

### 9. ★★ DAO 注入失败排查

| 维度 | 内容 |
|------|------|
| 是什么 | Mapper 接口注入失败时 NoSuchBeanDefinitionException 的系统化排查方法 |
| 能做什么 | 检查 @MapperScan 配置、DataSource 连接、Mapper XML 路径、扫描范围 |
| 怎么用 | 逐项排查：@MapperScan 配置 → basePackage 路径 → DataSource 连接 → Mapper XML 路径 |
| 原理和工作流程 | 排查顺序：1. 检查 @MapperScan 注解是否配置且 basePackage 路径正确。2. 确认 Mapper 接口在 basePackage 路径下。3. 检查 DataSource 配置是否正确，数据库连接是否可用。4. 检查 Mapper XML 文件路径是否匹配 mapperLocations 配置。5. 检查 Mapper 接口是否被父子容器重复扫描。6. 查看启动日志是否有 Mapper 注册相关信息 |
| 缺点 | 排查步骤多需逐一检查；问题可能由多个原因叠加；日志信息不一定直观 |

### 10. ★★ 包扫描隔离配置

| 维度 | 内容 |
|------|------|
| 是什么 | 父子容器各自扫描不同包，避免 Controller 被父容器扫描导致事务失效和 Bean 重复创建 |
| 能做什么 | 父容器扫 Service/DAO 排除 Controller；子容器只扫 Controller；两个容器扫描范围不重叠 |
| 怎么用 | 父容器：`excludeFilters = @Filter(Controller.class)`；子容器：`@ComponentScan("com.example.controller")` |
| 原理和工作流程 | 父容器用 @ComponentScan 排除 Controller 注解，管理 Service、DAO、配置类等。子容器用 @ComponentScan 只扫描 Controller 包，管理 Web 层 Bean。也可用 XML 配置：父容器 <context:exclude-filter> 排除 Controller，子容器 use-default-filters="false" 只含 Controller。隔离的原因：避免 Controller 被父容器扫描导致事务代理失效，避免 Bean 被两个容器重复创建导致注入混乱 |
| 缺点 | 配置不当导致功能静默失效；两个容器扫描范围需要仔细规划；新增 Controller 包时需要更新配置 |

---

## 三、场景设计题（3 题）

| 维度 | 内容 |
|------|------|
| 是什么 | SSM 整合笔面试场景设计题题型，要求设计完整排查方案解决综合性问题 |
| 能做什么 | 考查问题排查能力；考查配置诊断能力；考查方案设计能力 |
| 怎么用 | 场景设计题附原因分析和参考方案，难度拔高 |
| 原理和工作流程 | 场景设计题侧重考查综合排查和方案设计能力，涵盖事务失效排查场景（分析原因+排查步骤+解决方案）、整合配置问题排查场景（分析原因+完整排查方案）、父子容器冲突排查场景（分析原因+正确配置方案）等 3 个综合场景。每题附原因分析和参考方案供对照 |
| 缺点 | 方案不唯一难以标准化评分；考查范围广深度难统一；时间限制下方案完整性难保证 |

### 1. ★★★ 事务失效排查场景

| 维度 | 内容 |
|------|------|
| 是什么 | 订单创建接口 @Transactional 标注但事务不回滚的完整排查场景 |
| 能做什么 | 分析配置原因、注解位置、异常类型、代理调用、方法可见性、异常处理等六种可能原因 |
| 怎么用 | 逐项排查：@EnableTransactionManagement → @Transactional 位置 → 包扫描隔离 → 方法 public → 异常抛出 → rollbackFor |
| 原理和工作流程 | 可能原因：1. 未开启 @EnableTransactionManagement。2. @Transactional 放在 Controller 层。3. Controller 被父容器扫描。4. 方法非 public。5. 异常被 catch 未抛出。6. rollbackFor 未配置默认只回滚 RuntimeException。排查步骤：检查配置类注解、检查注解位置、检查包扫描 excludeFilters、检查方法可见性、检查异常处理、开启事务日志。解决方案：确保事务注解在 Service 层、配置 rollbackFor = Exception.class、父容器排除 Controller 扫描 |
| 缺点 | 多种原因可能叠加；包扫描冲突问题隐蔽；排查需要理解完整链路 |

### 2. ★★★ 整合配置问题排查场景

| 维度 | 内容 |
|------|------|
| 是什么 | Mapper 接口注入失败报 NoSuchBeanDefinitionException 的完整排查方案 |
| 能做什么 | 分析 @MapperScan 未配置、basePackage 错误、DataSource 缺失、Mapper XML 路径错误、依赖缺失、父子容器冲突等原因 |
| 怎么用 | 按步骤排查：依赖 → @MapperScan → DataSource → Mapper XML → 包路径 → 启动日志 |
| 原理和工作流程 | 排查方案：1. 检查 pom.xml 确认引入 mybatis-spring、mybatis、mysql-connector-java、spring-jdbc。2. 检查 @MapperScan 注解是否配置且 basePackage 路径正确。3. 检查 DataSource 和 SqlSessionFactoryBean 配置是否正确。4. 检查 Mapper XML 的 mapperLocations 路径是否匹配实际文件位置。5. 检查 Mapper 接口是否在 basePackage 路径下。6. 查看启动日志搜索 MapperScannerConfigurer 或 MapperFactoryBean 相关日志 |
| 缺点 | 排查步骤多需逐一验证；问题可能由多个原因叠加；缺少日志时难以定位 |

### 3. ★★★ 父子容器冲突排查场景

| 维度 | 内容 |
|------|------|
| 是什么 | 父子容器同时对同一包全量扫描导致事务失效的根因分析和正确配置方案 |
| 能做什么 | 分析 Controller 被父容器扫描导致事务代理失效的机制；给出正确的包扫描隔离配置 |
| 怎么用 | 父容器排除 Controller 扫描；子容器只扫描 Controller；两个容器扫描范围不重叠 |
| 原理和工作流程 | 问题根因：父子容器都对 com.example 包全量扫描，Controller 被父容器创建，同时子容器也创建 Controller。父容器中事务代理链可能不完整，子容器中 Controller 事务代理可能缺失。Service 和 DAO 也被两个容器重复创建导致注入混乱。正确方案：父容器 @ComponentScan 配置 excludeFilters 排除 Controller 和 RestController，只管理 Service、DAO、事务。子容器 @ComponentScan 只扫描 com.example.controller 包，只管理 Controller。Web 初始化通过 AbstractAnnotationConfigDispatcherServletInitializer 分别指定根配置类和 Servlet 配置类 |
| 缺点 | 问题隐蔽不报错但功能异常；排查需要理解父子容器和事务代理机制；配置隔离需要仔细规划包结构 |

---

> [返回原文](./SSM整合笔面试题集.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)