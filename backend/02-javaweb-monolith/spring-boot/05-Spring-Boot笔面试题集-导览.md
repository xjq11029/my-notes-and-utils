# Spring Boot 笔面试题集 导览

> 定位：五维框架浓缩提炼 05-Spring-Boot笔面试题集.md 全部内容小节，快速查阅与复习。
> 用法：每个题型对应一张概要表格，每道题目提取所考知识点生成五维表格，需要深入理解时跳转 [原文](./05-Spring-Boot笔面试题集.md)。
> 前置知识：[Spring-IoC与AOP深度](./01-Spring-IoC与AOP深度-导览.md)、[Spring-Boot自动配置原理](./02-Spring-Boot自动配置原理-导览.md)、[SpringMVC与RESTful设计](./03-SpringMVC与RESTful设计-导览.md)、[登录认证与安全](./04-登录认证与安全-导览.md)

---

## 一、选择题（15 题，附解析）

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 笔面试选择题题型，覆盖注解组成、Bean 作用域、AOP 代理、事务回滚等核心知识点 |
| 能做什么 | 考查基础概念辨析；考查注解细节记忆；考查原理机制理解；通过选项干扰检验掌握程度 |
| 怎么用 | 单选四选一，附答案与解析，难度分基础中档拔高三级 |
| 原理和工作流程 | 选择题侧重考查对 Spring Boot 核心知识点的精确记忆和辨析能力，涵盖 @SpringBootApplication 注解组成、Bean 作用域默认值、AOP 代理限制、@Transactional 回滚规则、DispatcherServlet 作用、自动配置核心注解、条件注解、参数绑定注解、Starter 机制、Bean 生命周期、循环依赖三级缓存、依赖注入方式、拦截器执行时机、@RestController 等效关系、自动配置注册文件演进等 15 个知识点。每题附解析说明正确选项的依据和错误选项的辨析 |
| 缺点 | 选择题难以考查综合应用能力；选项暗示性强可能猜对；侧重记忆而非理解；无法反映代码实践能力 |

### 1. ★ @SpringBootApplication 注解不包含以下哪个功能？

| 维度 | 内容 |
|------|------|
| 是什么 | @SpringBootApplication 组合注解的三个组成部分及其不包含的功能 |
| 能做什么 | 包含 @SpringBootConfiguration 等效 @Configuration；包含 @EnableAutoConfiguration 开启自动配置；包含 @ComponentScan 组件扫描；不包含 @Transactional 事务 |
| 怎么用 | `@SpringBootApplication` 等效于 `@SpringBootConfiguration + @EnableAutoConfiguration + @ComponentScan` |
| 原理和工作流程 | @SpringBootApplication 是 Spring Boot 启动类的核心组合注解，由三个注解合成：@SpringBootConfiguration（标记主类为配置类等效 @Configuration）、@EnableAutoConfiguration（开启自动配置机制）、@ComponentScan（扫描当前包及子包组件）。@Transactional 是事务注解需单独标注在方法或类上，不属于启动注解的组合部分。三者协同完成配置声明、自动装配、组件扫描三大职责 |
| 缺点 | 组合注解内部机制对新手不透明；三个注解耦合在启动类灵活性受限；易误以为包含其他常用注解 |

### 2. ★★ Spring Bean 作用域默认值

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Bean 的默认作用域为 singleton（单例）及其含义 |
| 能做什么 | singleton 全容器一个实例；prototype 每次获取新实例；request/session/Web 作用域；默认 singleton |
| 怎么用 | 默认 singleton；指定 prototype：`@Scope("prototype")` |
| 原理和工作流程 | Spring Bean 默认作用域是 singleton（单例），整个 IoC 容器中只有一个实例，所有获取该 Bean 的请求返回同一对象。singleton 在容器启动时（或首次懒加载时）创建一个实例缓存于一级缓存 singletonObjects。其他作用域包括 prototype（每次获取创建新实例）、request（每个 HTTP 请求一个实例）、session（每个 Session 一个实例）。@Transactional 等需注意单例 Bean 中注入 prototype Bean 的代理问题 |
| 缺点 | 单例 Bean 共享状态需注意线程安全；单例中注入 prototype Bean 仍为同一实例需代理；有状态 Bean 用 singleton 有并发风险 |

### 3. ★★ Spring AOP 不能代理的方法

| 维度 | 内容 |
|------|------|
| 是什么 | Spring AOP 基于 JDK 动态代理或 CGLIB 代理无法代理 private 方法的限制 |
| 能做什么 | 代理 public 方法；代理接口方法（JDK）；代理非 final 类方法（CGLIB）；不能代理 private 方法 |
| 怎么用 | JDK 代理：基于接口；CGLIB 代理：基于继承生成子类 |
| 原理和工作流程 | Spring AOP 使用 JDK 动态代理或 CGLIB 代理实现横切逻辑。JDK 动态代理基于接口，通过 Proxy 加 InvocationHandler 生成代理对象，只能代理接口中声明的方法。CGLIB 基于继承，通过 ASM 生成目标类的子类覆写方法，无法代理 final 类和 final 方法，且子类无法访问父类的 private 方法。因此两种代理方式都无法代理 private 方法。同类方法内部调用（this.method）也不走代理因不经过代理对象。Spring Boot 2.x 默认使用 CGLIB（proxyTargetClass=true） |
| 缺点 | private 方法无法被增强；同类内部调用不走代理导致 AOP 失效；final 方法无法被 CGLIB 增强；代理有轻微性能开销 |

### 4. ★★ @Transactional 默认回滚的异常类型

| 维度 | 内容 |
|------|------|
| 是什么 | @Transactional 默认只回滚 RuntimeException 和 Error（未检查异常），不回滚 checked exception |
| 能做什么 | 默认回滚 RuntimeException 和 Error；不回滚 checked exception；可通过 rollbackFor 指定回滚异常；noRollbackFor 排除异常 |
| 怎么用 | 默认行为；指定回滚：`@Transactional(rollbackFor = Exception.class)` |
| 原理和工作流程 | @Transactional 默认只回滚 RuntimeException 和 Error（未检查异常）。对于 checked exception（如 IOException）默认不回滚需提交，因为 Spring 认为 checked exception 是业务可预期的。若需对 checked exception 回滚需指定 rollbackFor = Exception.class。回滚判断逻辑在 TransactionAspectSupport 的 completeTransactionAfterThrowing 中，通过 rollbackOn 方法判断异常类型是否匹配回滚规则。此默认设计遵循 Java 异常体系约定，未检查异常表示程序错误应回滚，checked exception 表示业务预期可不回滚 |
| 缺点 | 默认不回滚 checked exception 易导致数据不一致；rollbackFor 配置遗漏导致回滚异常；异常被 catch 未抛出导致不回滚 |

### 5. ★ DispatcherServlet 的作用

| 维度 | 内容 |
|------|------|
| 是什么 | DispatcherServlet 是 Spring MVC 的前端控制器，负责统一接收请求并分发给对应 Handler |
| 能做什么 | 统一接收所有请求；通过 HandlerMapping 查找 Handler；通过 HandlerAdapter 调用 Handler；解析视图并渲染 |
| 怎么用 | Spring Boot 自动注册 DispatcherServlet 映射 "/" |
| 原理和工作流程 | DispatcherServlet 是 Spring MVC 的前端控制器（Front Controller 模式），作为所有请求的统一入口。请求到达后 DispatcherServlet 调用 HandlerMapping 根据 URL 查找对应的 Handler（Controller 方法）和拦截器链，再通过 HandlerAdapter 适配调用 Handler 执行业务逻辑，Handler 返回 ModelAndView，ViewResolver 解析视图并渲染响应。DispatcherServlet 解耦了请求分发与业务处理，统一管理请求处理流程。Spring Boot 中通过 DispatcherServletAutoConfiguration 自动注册 |
| 缺点 | 单一前端控制器可能成为性能瓶颈；请求处理链路长排查需逐环节；配置复杂出错难定位；与异步 Servlet 集成有细节 |

### 6. ★★ Spring Boot 自动配置的核心注解

| 维度 | 内容 |
|------|------|
| 是什么 | @EnableAutoConfiguration 是 Spring Boot 自动配置的核心注解，通过导入选择器加载自动配置类 |
| 能做什么 | 通过 @Import 导入 AutoConfigurationImportSelector；读取自动配置类列表；按条件注解过滤；导入符合条件的配置类 |
| 怎么用 | `@EnableAutoConfiguration` 或经 `@SpringBootApplication` 间接启用 |
| 原理和工作流程 | @EnableAutoConfiguration 是自动配置的核心注解，通过 @Import(AutoConfigurationImportSelector.class) 导入自动配置选择器。选择器调用 selectImports 方法从 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports（2.7 前为 spring.factories）读取所有自动配置类全限定名，通过条件注解（@ConditionalOnClass、@ConditionalOnMissingBean 等）过滤，将符合条件的配置类导入容器。@SpringBootApplication 内含 @EnableAutoConfiguration 故启动类间接启用自动配置 |
| 缺点 | 自动配置类数量多导致启动开销；条件过滤逻辑复杂调试困难；@ConditionalOnBean 评估顺序可能导致误判 |

### 7. ★★ @ConditionalOnMissingBean 条件注解

| 维度 | 内容 |
|------|------|
| 是什么 | @ConditionalOnMissingBean 在容器中不存在指定 Bean 时生效的条件注解，是自动配置让用户自定义优先的核心机制 |
| 能做什么 | 容器无指定 Bean 时创建默认 Bean；用户自定义 Bean 优先于默认；按类型或名称判断；支持覆盖默认配置 |
| 怎么用 | `@Bean @ConditionalOnMissingBean public LogAspect logAspect() { return new LogAspect(); }` |
| 原理和工作流程 | @ConditionalOnMissingBean 在容器中不存在指定 Bean 时配置生效。这是自动配置的核心机制：自动配置类提供默认 Bean，但若用户自定义了同类型 Bean，则条件不满足跳过默认 Bean，使用用户的自定义 Bean，实现用户配置优先。判断逻辑在 Condition 接口的 matches 方法中，通过 BeanFactory 查找指定类型或名称的 Bean 是否已存在。评估时机在 Bean 注册阶段，此时部分 Bean 可能还未创建导致顺序敏感。@ConditionalOnBean 是相反逻辑，存在指定 Bean 时才生效 |
| 缺点 | 评估依赖 Bean 注册顺序顺序不当误判；仅按类型判断同类型多 Bean 行为复杂；顺序敏感问题难排查 |

### 8. ★★ @RequestBody 接收 JSON 请求体

| 维度 | 内容 |
|------|------|
| 是什么 | @RequestBody 用于接收 JSON/XML 格式请求体并绑定到方法参数的 Spring MVC 注解 |
| 能做什么 | 接收 JSON/XML 请求体；自动反序列化为对象；配合 @Valid 校验；与 @RequestParam @PathVariable 区分 |
| 怎么用 | `public Result create(@RequestBody User user) { ... }` |
| 原理和工作流程 | @RequestBody 用于接收 JSON/XML 格式的请求体，Spring MVC 通过 HttpMessageConverter（如 MappingJackson2HttpMessageConverter）将请求体反序列化为方法参数对象。@RequestParam 用于接收查询参数和表单字段，@PathVariable 用于接收 URL 路径中的变量（如 /user/{id} 中的 id），@ModelAttribute 用于绑定表单数据到对象。@RequestBody 只能用于请求体且一个方法只能有一个 @RequestBody 参数，因其请求体只能读取一次。Content-Type 需为 application/json |
| 缺点 | 请求体只能读取一次无法重复读；大请求体反序列化有性能开销；Content-Type 不匹配报错；一个方法仅一个 @RequestBody |

### 9. ★ Spring Boot Starter 机制

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot Starter 是一组依赖描述符的集合，引入即可获得相关功能的自动化配置 |
| 能做什么 | 聚合相关依赖；提供自动配置；官方命名 spring-boot-starter-*；第三方命名 *-spring-boot-starter；适用各种场景 |
| 怎么用 | 引入 `spring-boot-starter-data-jpa` 即获数据访问能力 |
| 原理和工作流程 | Starter 是一组依赖描述符的集合，引入一个 Starter 即可获得该功能所需的全部依赖和自动配置。官方 Starter 命名格式为 spring-boot-starter-*（如 spring-boot-starter-web、spring-boot-starter-data-jpa、spring-boot-starter-test），第三方 Starter 命名格式通常为 *-spring-boot-starter。Starter 不仅聚合依赖，还通过 spring-boot-autoconfigure 提供对应的自动配置类，根据条件注解自动创建默认 Bean。Starter 可用于各种场景不限于 Web 开发，如数据访问、测试、安全等 |
| 缺点 | 引入 Starter 可能带入不需要的依赖；版本冲突需手动排除；自动配置黑盒化排查困难； Starter 过多导致依赖膨胀 |

### 10. ★★ Spring Bean 的生命周期

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Bean 从实例化到销毁的完整生命周期，编译不属于其中 |
| 能做什么 | 实例化；属性赋值（依赖注入）；Aware 回调；BeanPostProcessor 前后置处理；初始化；使用；销毁 |
| 怎么用 | 实例化 -> 属性赋值 -> 初始化 -> 使用 -> 销毁 |
| 原理和工作流程 | Bean 生命周期包括：实例化（构造器创建对象）-> 属性赋值（依赖注入）-> Aware 接口回调（如 BeanNameAware 注入 Bean 名）-> BeanPostProcessor 前置处理（postProcessBeforeInitialization）-> 初始化（@PostConstruct、InitializingBean、init-method）-> BeanPostProcessor 后置处理（postProcessAfterInitialization，AOP 代理在此生成）-> 使用 -> 销毁（@PreDestroy、DisposableBean、destroy-method）。编译是 Java 代码到字节码的过程发生在运行之前，不属于 Bean 生命周期 |
| 缺点 | 生命周期环节多易遗漏；BeanPostProcessor 顺序影响代理生成；循环依赖在实例化和属性赋值间发生；销毁顺序复杂 |

### 11. ★★ Spring 三级缓存解决循环依赖

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 通过三级缓存机制解决单例 Bean 的循环依赖问题 |
| 能做什么 | 一级缓存存完全初始化的 Bean；二级缓存存早期暴露的 Bean；三级缓存存 Bean 工厂；支持循环引用完成注入 |
| 怎么用 | singletonObjects(一级) / earlySingletonObjects(二级) / singletonFactories(三级) |
| 原理和工作流程 | Spring 通过三级缓存解决单例 Bean 的循环依赖：一级缓存 singletonObjects 存完全初始化好的 Bean，二级缓存 earlySingletonObjects 存早期暴露的半成品 Bean（已实例化未完成属性注入），三级缓存 singletonFactories 存 ObjectFactory Bean 工厂。当 A 依赖 B 且 B 依赖 A 形成循环时，A 实例化后将 ObjectFactory 放入三级缓存，注入 B 时 B 又需注入 A，B 从三级缓存获取 A 的 ObjectFactory 调用 getObject 得到早期 A 引用（若需代理则生成早期代理），放入二级缓存，B 完成初始化后 A 继续完成注入。三级缓存的存在是为了处理 AOP 代理，确保循环依赖时也能正确生成代理对象 |
| 缺点 | 仅支持单例作用域的循环依赖；构造器注入无法解决循环依赖；三级缓存机制复杂难理解；代理场景行为微妙 |

### 12. ★★ Spring 依赖注入方式

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 支持构造器注入、Setter 注入、字段注入三种依赖注入方式，反射注入不是其中之一 |
| 能做什么 | 构造器注入（推荐）；Setter 注入（可选依赖）；字段注入（@Autowired 标字段）；不支持反射注入 |
| 怎么用 | 构造器：`public Service(Dep dep) { this.dep = dep; }`；字段：`@Autowired private Dep dep;` |
| 原理和工作流程 | Spring 支持三种注入方式：构造器注入通过构造方法参数注入依赖，可保证依赖不可变和强制依赖（推荐），Spring 4.3 单构造器可省略 @Autowired。Setter 注入通过 setter 方法注入，适用于可选依赖可设默认值。字段注入通过 @Autowired 标注在字段上由反射直接赋值，写法简洁但无法在构造时保证依赖不为 null 且不利于测试。反射注入不是 Spring 定义的注入方式。推荐使用构造器注入保证依赖不可变和便于单元测试 |
| 缺点 | 字段注入无法在构造时保证非 null；构造器注入参数过多时构造器臃肿；Setter 注入可能被中途修改；循环依赖时构造器注入失败 |

### 13. ★★ 拦截器（Interceptor）的执行时机

| 维度 | 内容 |
|------|------|
| 是什么 | Interceptor 的三个执行时机 preHandle、postHandle、afterCompletion，请求到达服务器前不属于其中 |
| 能做什么 | preHandle Controller 方法执行前；postHandle Controller 后视图渲染前；afterCompletion 视图渲染后 |
| 怎么用 | `preHandle` 返回 boolean 决定是否放行；`postHandle` 操作 ModelAndView；`afterCompletion` 清理资源 |
| 原理和工作流程 | 拦截器执行时机有三个：preHandle 在 Controller 方法执行前调用，返回 false 则中断请求后续拦截器和 Controller 不执行；postHandle 在 Controller 方法执行后视图渲染前调用，可操作 ModelAndView；afterCompletion 在视图渲染后调用，用于资源清理。请求到达服务器前是 Filter 的执行时机而非 Interceptor，因 Filter 属于 Servlet 规范在请求进入 Servlet 前执行，Interceptor 属于 Spring MVC 在 DispatcherServlet 内部 Controller 前后执行。执行顺序为 Filter -> Interceptor.preHandle -> Controller -> Interceptor.postHandle -> 视图渲染 -> Interceptor.afterCompletion |
| 缺点 | preHandle 返回 false 后 postHandle 不执行易误解；异步请求拦截器行为不同；拦截器顺序影响执行；与 Filter 时机易混淆 |

### 14. ★★ @RestController 注解

| 维度 | 内容 |
|------|------|
| 是什么 | @RestController 等价于 @Controller + @ResponseBody 的组合注解 |
| 能做什么 | 标识 Controller；方法返回值序列化为 JSON/XML 写入响应体；无需视图解析；构建 RESTful API |
| 怎么用 | `@RestController @RequestMapping("/api") public class UserController { ... }` |
| 原理和工作流程 | @RestController 等价于 @Controller + @ResponseBody。@Controller 标识该类为控制器组件由 Spring 扫描注册，@ResponseBody 标注后方法返回值不经过视图解析器，而是通过 HttpMessageConverter 序列化为 JSON/XML 直接写入响应体。@RestController 将两者组合，意味着 Controller 中所有方法返回值都会被序列化为 JSON/XML 直接写入响应体，适用于构建 RESTful API。前后端分离场景下普遍使用 @RestController 替代 @Controller |
| 缺点 | 所有方法都返回 JSON 无法混合视图渲染；异常处理需 @RestControllerAdvice；返回值序列化依赖 Jackson 配置；不适用服务端渲染场景 |

### 15. ★★★ Spring Boot 2.7 自动配置注册文件演进

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 2.7 将自动配置注册文件从 spring.factories 改为 AutoConfiguration.imports |
| 能做什么 | 简化注册格式为每行一个类名；提升加载效率；隔离自动配置与其他扩展注册；回退兼容旧文件 |
| 怎么用 | `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 每行一个类全限定名 |
| 原理和工作流程 | Spring Boot 2.7+ 使用 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports 文件注册自动配置类，替代了之前的 spring.factories。spring.factories 采用 key-value 格式，EnableAutoConfiguration 的值通过续行符列出多个配置类，该文件还承担 Listener、Initializer 等扩展点注册。2.7 之后自动配置类单独注册到 .imports 文件，每行一个类全限定名无需 key。AutoConfigurationImportSelector 优先读取 .imports 文件，回退读取 spring.factories 保证兼容。分离后加载解析更高效，为未来移除 spring.factories 的自动配置 key 做铺垫 |
| 缺点 | 过渡期两套机制并存增加理解成本；旧项目升级需迁移注册文件；第三方 Starter 需同时适配两版本；新文件路径较长易写错 |

---

## 二、简答题（10 题，附要点）

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 笔面试简答题题型，要求用要点形式阐述核心原理和对比 |
| 能做什么 | 考查原理理解深度；考查概念对比辨析；考查流程描述能力；通过要点评分检验表达 |
| 怎么用 | 简答题附要点答案，难度中档为主 |
| 原理和工作流程 | 简答题侧重考查对 Spring 核心原理的理解和表达能力，涵盖 IoC 与 DI 区别、Bean 生命周期、自动配置原理、JDK 与 CGLIB 代理区别、Spring MVC 执行流程、@Transactional 失效场景、Filter 与 Interceptor 区别、@Component 与 @Bean 区别、配置文件加载优先级、Spring 设计模式应用等 10 个知识点。每题附要点答案列出核心要点供评分参考 |
| 缺点 | 评分主观性强；要点遗漏难以全面覆盖；侧重记忆要点而非实际应用；无法反映代码能力 |

### 1. ★★ Spring IoC 和 DI 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | IoC（控制反转）是设计思想，DI（依赖注入）是 IoC 的具体实现方式 |
| 能做什么 | IoC 将对象创建管理控制权转移给容器；DI 通过构造器/Setter/字段注入依赖；解耦组件间依赖 |
| 怎么用 | IoC：容器管理 Bean；DI：`@Autowired`、构造器、setter 注入依赖 |
| 原理和工作流程 | IoC（Inversion of Control）是一种设计思想，将对象创建和管理的控制权从代码转移到容器，由容器负责对象的实例化、配置和生命周期管理。DI（Dependency Injection）是 IoC 的具体实现方式，容器在运行时将依赖注入到对象中。Spring 通过三种方式实现 DI：构造器注入（通过构造方法参数注入，推荐）、Setter 注入（通过 setter 方法注入可选依赖）、字段注入（@Autowired 标注字段由反射赋值）。IoC 是思想层面的控制权反转，DI 是实现层面的依赖传递机制，二者是思想与实现的关系 |
| 缺点 | IoC 概念抽象易与 DI 混淆；过度依赖容器导致对象脱离容器难以测试；循环依赖问题；容器启动变慢 |

### 2. ★★ Spring Bean 的生命周期？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Bean 从实例化到销毁经历的完整生命周期及各阶段回调 |
| 能做什么 | 实例化构造对象；属性赋值注入依赖；Aware 回调注入容器信息；BeanPostProcessor 前后置处理；初始化与销毁回调 |
| 怎么用 | 实例化 -> 属性赋值 -> Aware 回调 -> BeanPostProcessor 前置 -> @PostConstruct -> BeanPostProcessor 后置 -> 使用 -> @PreDestroy |
| 原理和工作流程 | Bean 生命周期完整流程：实例化（构造器创建对象）-> 属性赋值（依赖注入）-> Aware 接口回调（BeanNameAware、BeanFactoryAware 等注入容器信息）-> BeanPostProcessor 前置处理（postProcessBeforeInitialization）-> 初始化（@PostConstruct、InitializingBean 的 afterPropertiesSet、init-method）-> BeanPostProcessor 后置处理（postProcessAfterInitialization，AOP 代理在此阶段生成）-> 使用 -> 销毁（@PreDestroy、DisposableBean 的 destroy、destroy-method）。BeanPostProcessor 是生命周期扩展的核心，AOP 代理、@Configuration 的 CGLIB 增强都在后置处理中完成 |
| 缺点 | 生命周期环节多易遗漏回调；BeanPostProcessor 顺序影响代理生成；销毁顺序与依赖关系相反；循环依赖打乱正常流程 |

### 3. ★★ Spring Boot 自动配置原理？

| 维度 | 内容 |
|------|------|
| 是什么 | @EnableAutoConfiguration 通过导入选择器加载并按条件过滤自动配置类的机制 |
| 能做什么 | 读取自动配置类列表；按条件注解过滤；导入符合条件配置类；用户自定义 Bean 优先 |
| 怎么用 | `@EnableAutoConfiguration` 或 `@SpringBootApplication` 启用 |
| 原理和工作流程 | @EnableAutoConfiguration 通过 @Import(AutoConfigurationImportSelector.class) 导入自动配置选择器。选择器从 META-INF/spring/*.AutoConfiguration.imports（2.7 前为 spring.factories）读取所有自动配置类全限定名。然后通过条件注解过滤：@ConditionalOnClass 判断类路径是否存在指定类，@ConditionalOnMissingBean 判断容器是否缺少指定 Bean，@ConditionalOnProperty 判断配置属性是否满足。符合条件的配置类导入容器，其 @Bean 方法创建默认实例，用户自定义 Bean 优先于默认 Bean。整个机制实现引入 Starter 即自动配置、用户可覆盖的约定优于配置理念 |
| 缺点 | 自动配置类数量多启动开销大；条件过滤逻辑复杂调试困难；@ConditionalOnBean 顺序敏感；黑盒化出问题难排查 |

### 4. ★★ Spring AOP 中 JDK 动态代理和 CGLIB 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring AOP 两种代理方式 JDK 动态代理（基于接口）与 CGLIB（基于继承）的对比 |
| 能做什么 | JDK 代理基于接口用 Proxy+InvocationHandler；CGLIB 基于继承用 ASM 生成子类；Spring Boot 2.x 默认 CGLIB |
| 怎么用 | JDK：目标类实现接口；CGLIB：`proxyTargetClass=true`（Spring Boot 默认） |
| 原理和工作流程 | JDK 动态代理基于接口，使用 java.lang.reflect.Proxy 加 InvocationHandler 在运行时生成实现目标接口的代理类，要求目标类必须实现接口，只能代理接口中声明的方法。CGLIB 基于继承，通过 ASM 字节码框架生成目标类的子类覆写方法实现代理，不能代理 final 类和 final 方法，无需接口。Spring Boot 2.x 默认使用 CGLIB（spring.aop.proxy-target-class=true），即使用户类实现了接口也用 CGLIB 代理。JDK 代理创建快但调用经反射有开销，CGLIB 生成子类创建稍慢但调用经 FastClass 机制性能更好 |
| 缺点 | JDK 代理要求目标类实现接口；CGLIB 不能代理 final 类和方法；CGLIB 生成子类有内存开销；代理对象不等于目标对象类型转换需注意 |

### 5. ★★ Spring MVC 的执行流程？

| 维度 | 内容 |
|------|------|
| 是什么 | 一个 HTTP 请求在 Spring MVC 中从 DispatcherServlet 接收到响应返回的完整执行流程 |
| 能做什么 | DispatcherServlet 统一入口；HandlerMapping 查找 Handler；HandlerAdapter 调用；ViewResolver 解析视图渲染 |
| 怎么用 | 请求 -> DispatcherServlet -> HandlerMapping -> HandlerAdapter -> Handler -> ModelAndView -> ViewResolver -> 渲染 -> 响应 |
| 原理和工作流程 | Spring MVC 执行流程：1. 请求到达 DispatcherServlet（前端控制器）。2. DispatcherServlet 调用 HandlerMapping 根据 URL 查找对应的 Handler（Controller 方法）和拦截器链。3. DispatcherServlet 调用 HandlerAdapter 适配并执行 Handler。4. Handler 执行业务逻辑返回 ModelAndView（数据模型和视图名）。5. ViewResolver 解析视图名为具体 View 对象。6. View 渲染（将模型数据填充到视图）。7. 返回响应。前后端分离场景下 Handler 返回对象经 @ResponseBody 由 HttpMessageConverter 序列化为 JSON 直接响应，跳过 ViewResolver 和视图渲染 |
| 缺点 | 流程环节多排查需逐环节定位；HandlerMapping 匹配规则复杂；异步请求流程不同；前后端分离与传统流程有差异 |

### 6. ★★ @Transactional 失效的常见场景？

| 维度 | 内容 |
|------|------|
| 是什么 | @Transactional 注解在特定场景下事务失效不回滚的常见原因 |
| 能做什么 | 识别方法非 public 失效；识别同类调用失效；识别异常被 catch 失效；识别引擎不支持事务；识别多线程失效 |
| 怎么用 | 失效场景：非 public 方法；this.method() 同类调用；异常被 catch 未抛出；MyISAM 引擎；多线程 |
| 原理和工作流程 | @Transactional 失效的常见场景：① 方法非 public，Spring AOP 通过代理只增强 public 方法，protected/private 方法不经过代理事务失效。② 同类方法调用，this.method() 直接调用目标对象方法不经过代理对象，事务增强不生效，需通过 AopContext.currentProxy() 或注入自身代理调用。③ 异常被 catch 未抛出，方法内 catch 异常未重新抛出，代理层检测不到异常不触发回滚。④ 数据库引擎不支持事务，如 MySQL MyISAM 不支持事务需用 InnoDB。⑤ 多线程场景，事务绑定在当前线程的 ThreadLocal 上，新线程不共享事务上下文 |
| 缺点 | 失效场景隐蔽不易发现；同类调用需改代码用代理；异常处理需谨慎抛出；多线程事务需编程式事务；排查需理解代理机制 |

### 7. ★★ Filter 和 Interceptor 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | Filter（Servlet 规范）与 Interceptor（Spring 规范）两种拦截机制的对比 |
| 能做什么 | Filter 由 Servlet 容器管理拦截所有请求；Interceptor 由 Spring 管理只拦 Controller；执行时机和范围不同 |
| 怎么用 | Filter：`implements Filter`；Interceptor：`implements HandlerInterceptor` |
| 原理和工作流程 | Filter 是 Servlet 规范组件由 Servlet 容器管理，作用于所有请求含静态资源，在请求进入 Servlet 前后执行，不依赖 Spring 容器获取 Bean 需 ApplicationContext。Interceptor 是 Spring 框架组件由 Spring 容器管理，仅作用于 Spring MVC 处理的请求（Controller），在 Controller 方法前后和视图渲染后执行（preHandle/postHandle/afterCompletion），可直接注入 Bean。Filter 在请求进入 Servlet 前执行，Interceptor 在 Controller 前后执行。执行顺序为 Filter -> Interceptor -> Controller。Filter 粒度粗拦截所有请求，Interceptor 粒度细只拦 Controller |
| 缺点 | Filter 获取 Spring Bean 困难；Interceptor 无法拦截非 Controller 请求；二者执行顺序混合时排查复杂；职责重叠易混淆 |

### 8. ★★ @Component 和 @Bean 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | @Component（作用于类）与 @Bean（作用于方法）两种 Bean 注册方式的对比 |
| 能做什么 | @Component 类路径扫描自动注册；@Bean 在 @Configuration 类中手动声明；适用场景不同 |
| 怎么用 | @Component：`@Component public class MyService {}`；@Bean：`@Bean public DataSource dataSource() { ... }` |
| 原理和工作流程 | @Component 作用于类，通过类路径扫描（@ComponentScan）自动发现并注册为 Bean，适用于自己编写的类。@Bean 作用于方法，在 @Configuration 类中手动声明 Bean，方法返回值即为 Bean 实例，适用于第三方类（无法修改源码加 @Component）或需要复杂初始化逻辑的 Bean。@Configuration 类中 @Bean 方法之间的调用会被 CGLIB 增强确保返回同一单例（Full 模式），@Component 类中 @Bean 方法调用不增强每次返回新实例（Lite 模式）。@Bean 可配合 @Conditional、@Primary 等精细控制 |
| 缺点 | @Component 无法注册第三方类；@Bean 需手动编写配置类；@Configuration 与 @Component 的 @Bean 行为不同易混淆；过度用 @Bean 配置类臃肿 |

### 9. ★★ Spring Boot 配置文件加载优先级？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 多来源配置属性按固定优先级从高到低覆盖的规则 |
| 能做什么 | 命令行参数最高；环境变量次之；jar 包外高于包内；profile 配置高于默认；@PropertySource 最低 |
| 怎么用 | `java -jar app.jar --server.port=9090` 命令行参数最高优先级 |
| 原理和工作流程 | 配置文件加载优先级从高到低：命令行参数 > 环境变量 > 系统属性 > jar 包外部 application-{profile}.yml > jar 包内部 application-{profile}.yml > jar 包外部 application.yml > jar 包内部 application.yml > @PropertySource。高优先级覆盖低优先级，同名属性前者覆盖后者。Spring Boot 通过 Environment 抽象管理配置属性，按优先级构造 PropertySource 链，获取属性时从高到低遍历首个命中即返回。jar 包外配置覆盖 jar 包内配置便于不改包修改配置，profile 配置覆盖默认配置实现环境隔离 |
| 缺点 | 优先级层级多容易混淆；同名属性跨来源覆盖排查困难；环境变量命名需转换（点号转下划线大写）；外部配置位置不当不生效 |

### 10. ★★ Spring 中使用了哪些设计模式？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 框架中应用的设计模式及其在框架中的具体体现 |
| 能做什么 | 单例模式 Bean 作用域；工厂模式 BeanFactory；代理模式 AOP；模板方法 JdbcTemplate；观察者事件机制；策略 Resource；适配器 HandlerAdapter；装饰器 BeanWrapper |
| 怎么用 | 单例：Bean 默认 singleton；工厂：`BeanFactory factory = context;`；代理：`@Aspect` AOP |
| 原理和工作流程 | Spring 框架广泛应用设计模式：单例模式体现在 Bean 默认作用域为 singleton 全容器一个实例。工厂模式体现在 BeanFactory 和 ApplicationContext 作为工厂创建管理 Bean。代理模式体现在 AOP 通过 JDK 动态代理或 CGLIB 生成代理对象实现横切逻辑。模板方法模式体现在 JdbcTemplate、RestTemplate 等定义算法骨架子类实现具体步骤。观察者模式体现在 ApplicationEvent 事件机制，发布者发布事件监听者响应。策略模式体现在 Resource 接口对不同资源类型的策略选择。适配器模式体现在 HandlerAdapter 适配不同类型的 Handler。装饰器模式体现在 BeanWrapper 增强 Bean 功能 |
| 缺点 | 设计模式应用隐蔽新手不易察觉；模式组合增加理解难度；过度设计可能引入不必要复杂度；模式名称与实现对应关系需经验积累 |

---

## 三、编程题（3 题，每题 15 分，共 45 分）

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 笔面试编程题题型，要求手写完整代码实现特定功能 |
| 能做什么 | 考查代码实现能力；考查注解与 AOP 综合应用；考查自动配置机制；通过评分要点检验规范性 |
| 怎么用 | 编程题附评分要点和参考实现，难度中档至拔高 |
| 原理和工作流程 | 编程题侧重考查代码实现能力和 Spring Boot 核心机制的综合应用，涵盖自定义 Starter 开发（注解+AOP+自动配置+spring.factories）、AOP 日志切面（切点表达式+环绕通知+异常处理+耗时统计）、自定义注解+防重复提交（参数校验切面+Redis SET NX EX+请求唯一标识）等 3 个综合场景。每题附评分要点和参考实现供对照 |
| 缺点 | 评分受代码风格影响；参考实现不唯一难以标准化评分；考查范围有限无法全面评估；时间限制下代码质量难保证 |

### 1. ★★ 实现一个自定义 Spring Boot Starter

| 维度 | 内容 |
|------|------|
| 是什么 | 实现 my-log-spring-boot-starter，引入后自动对 @MyLog 注解方法进行日志记录的自定义 Starter 开发 |
| 能做什么 | 创建 @MyLog 注解；创建 AOP 切面 @Around 环绕通知；创建自动配置类 @ConditionalOnClass；注册 spring.factories；支持 IDE 提示 |
| 怎么用 | `@MyLog public void method() {}` 自动记录方法名参数执行时间 |
| 原理和工作流程 | 自定义 Starter 开发步骤：1. 创建 @MyLog 注解（@Target METHOD、@Retention RUNTIME）含 value 属性。2. 创建 AOP 切面 LogAspect 标注 @Aspect @Component，@Around("@annotation(myLog)") 环绕通知中获取方法名 joinPoint.getSignature().getName()、参数 joinPoint.getArgs()、记录开始时间，proceed 执行目标方法后计算耗时，log.info 输出日志，异常时 log.error 记录并重新抛出。3. 创建自动配置类 MyLogAutoConfiguration 标注 @Configuration @ConditionalOnClass(LogAspect.class) @EnableConfigurationProperties，@Bean @ConditionalOnMissingBean 注册 LogAspect。4. 创建 META-INF/spring.factories 文件注册 EnableAutoConfiguration=MyLogAutoConfiguration。5. 创建 spring-configuration-metadata.json 支持 IDE 配置提示 |
| 缺点 | Starter 开发步骤多易遗漏；spring.factories 路径写错不生效；@ConditionalOnClass 顺序敏感；IDE 提示元数据维护成本高 |

### 2. ★★ 实现一个 AOP 日志切面，记录 Controller 层的请求和响应

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 Spring AOP 实现切面拦截所有 Controller 方法记录请求 URL 参数响应结果耗时的日志切面 |
| 能做什么 | 切点表达式拦截 Controller 包；@Around 环绕通知；获取请求信息（URL 方法 参数）；记录响应和耗时；异常处理记录 |
| 怎么用 | `@Pointcut("execution(* com.example.controller..*.*(..))")` + `@Around` |
| 原理和工作流程 | AOP 日志切面实现：ControllerLogAspect 标注 @Aspect @Component @Slf4j。@Pointcut 定义切点表达式 execution(* com.example.controller..*.*(..)) 拦截 controller 包下所有方法。@Around 环绕通知中通过 RequestContextHolder.getRequestAttributes() 获取 ServletRequestAttributes，再获取 HttpServletRequest，提取 URL（getRequestURL）、Method（getMethod）、类名方法名（joinPoint.getSignature()）、参数（joinPoint.getArgs()）。log.info 记录请求开始，记录开始时间，proceed 执行目标方法获取结果，计算耗时，log.info 记录请求结束含响应结果和耗时。catch 异常时 log.error 记录异常并重新抛出确保异常不吞没 |
| 缺点 | 切点表达式过宽可能拦截非预期方法；JSON 序列化大对象有性能开销；异常日志需注意堆栈完整；高并发下日志量大 |

### 3. ★★★ 实现一个方法级别的参数校验和防重复提交注解

| 维度 | 内容 |
|------|------|
| 是什么 | 实现 @ValidateParam 参数校验注解和 @PreventDuplicate 基于 Redis 防重复提交注解的综合方案 |
| 能做什么 | @ValidateParam 非空和长度校验；@PreventDuplicate Redis SET NX EX 防重；生成唯一请求标识（用户ID+方法名+参数MD5）；统一异常处理 |
| 怎么用 | `@ValidateParam(notNull={"name"}) @PreventDuplicate(expire=5) public void method() {}` |
| 原理和工作流程 | 注解定义：@ValidateParam 含 notNull 属性指定需非空校验的参数字段名，@PreventDuplicate 含 expire 属性默认 5 秒防重时间窗口。防重复提交切面 PreventDuplicateAspect 标注 @Aspect @Component，@Around("@annotation(preventDuplicate)") 环绕通知中：获取当前用户 ID（从请求上下文），生成请求唯一标识 key = "duplicate:" + userId + ":" + 方法名 + ":" + 参数 MD5（DigestUtils.md5Hex(JSON.toJSONString(args))）。使用 Redis SET NX EX 判断是否重复：redisTemplate.opsForValue().setIfAbsent(key, "1", expire, TimeUnit.SECONDS)，返回 false 表示重复提交抛出 RuntimeException。返回 true 则 proceed 执行业务逻辑。参数校验切面对 notNull 指定字段校验非空和长度 |
| 缺点 | Redis 不可用导致防重失效；MD5 计算有性能开销；用户 ID 获取依赖上下文；防重窗口内合法重复请求被拒 |

---

## 四、场景设计题（2 题，每题 20 分，共 40 分）

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 笔面试场景设计题题型，要求设计完整方案解决综合性问题 |
| 能做什么 | 考查架构设计能力；考查方案选型权衡；考查综合技术应用；通过参考答案检验设计完整性 |
| 怎么用 | 场景设计题附架构设计和参考代码，难度拔高 |
| 原理和工作流程 | 场景设计题侧重考查架构设计能力和综合方案权衡，涵盖统一异常处理方案（自定义业务异常+@RestControllerAdvice 全局捕获+错误码枚举+统一响应格式+国际化）和 API 接口幂等性方案（Token 机制+唯一索引+状态机三种方案对比）等 2 个综合场景。每题附架构设计和参考代码供对照 |
| 缺点 | 设计方案不唯一难以标准化评分；考查范围广深度难统一；时间限制下方案完整性难保证；无法验证方案实际可行性 |

### 1. ★★★ 设计一个统一异常处理方案

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 项目中基于 @RestControllerAdvice 的完整统一异常处理架构方案 |
| 能做什么 | 自定义业务异常含错误码；全局捕获异常；区分业务/参数/系统异常；统一错误响应格式；支持国际化 |
| 怎么用 | `@RestControllerAdvice public class GlobalExceptionHandler { @ExceptionHandler(BusinessException.class) public Result handle() { ... } }` |
| 原理和工作流程 | 架构设计：请求 -> Controller -> Service 抛出业务异常 -> @RestControllerAdvice 全局捕获 -> 统一异常处理器 -> 统一错误响应。核心组件：1. 统一响应格式 Result<T> 含 code、message、data，提供 success 和 error 静态工厂方法。2. 自定义业务异常 BusinessException 继承 RuntimeException 含 code 字段，可由 ErrorCode 枚举构造。3. 错误码枚举 ErrorCode 定义标准错误码（200 成功、400 参数错误、401 未认证、403 无权限、404 不存在、4001 重复提交、500 系统异常）。4. 全局异常处理器 GlobalExceptionHandler 标注 @RestControllerAdvice，@ExceptionHandler 分别处理 BusinessException（业务异常返回具体错误码）、MethodArgumentNotValidException（参数校验异常聚合字段错误信息）、Exception（系统异常返回 500 系统繁忙）。5. 国际化用 MessageSource + LocaleResolver 根据 Accept-Language 头返回对应语言错误信息 |
| 缺点 | 异常处理逻辑集中易臃肿；错误码枚举维护成本高；国际化资源文件管理繁琐；系统异常信息脱敏与排查矛盾 |

### 2. ★★★ 设计一个 API 接口幂等性方案

| 维度 | 内容 |
|------|------|
| 是什么 | 分布式系统中确保同一请求多次调用结果一致的 API 幂等性方案，含 Token、唯一索引、状态机三种 |
| 能做什么 | Token 机制适用创建操作；唯一索引适用数据库层；状态机适用有状态业务；防止重复扣款重复创建 |
| 怎么用 | Token：GET /token 获取 -> 请求携带 -> Lua 脚本校验删除；唯一索引：`ALTER TABLE ADD UNIQUE INDEX`；状态机：检查当前状态允许的变更 |
| 原理和工作流程 | 方案一 Token 机制适用于创建操作：1. 客户端先请求 GET /api/idempotent/token 获取 token。2. 服务端生成 token 存入 Redis SET token:xxx "1" EX 300。3. 客户端请求时携带 Header: Idempotent-Token: xxx。4. 服务端用 Lua 脚本校验 token 是否存在，存在则删除 token 执行业务，不存在返回请勿重复提交。Lua 脚本保证 EXISTS 和 DEL 的原子性。方案二唯一索引适用于数据库层面：对 order_no 等业务唯一键添加唯一索引，重复插入触发唯一约束异常捕获后返回重复提交。方案三状态机适用于有状态业务：订单状态待支付->已支付->已发货->已完成，每次变更前检查当前状态只允许特定变更。三者对比：Token 通用性强无侵入但需额外请求；唯一索引简单可靠但仅适用有唯一键场景；状态机业务语义清晰但实现复杂 |
| 缺点 | Token 机制需额外请求获取 token；唯一索引仅适用有唯一键场景；状态机实现复杂需维护状态；Redis 不可用 Token 方案失效 |

---

> [返回原文](./05-Spring-Boot笔面试题集.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
