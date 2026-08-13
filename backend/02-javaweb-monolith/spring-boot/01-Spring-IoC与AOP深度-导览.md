# Spring IoC 与 AOP 深度 导览

> 定位：五维框架浓缩提炼 01-Spring-IoC与AOP深度.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./01-Spring-IoC与AOP深度.md)。
> 前置知识：[面向对象基础](../../01-java-basics/java-core/05-面向对象基础-导览.md)、[反射机制](../../01-java-basics/java-core/12-反射机制-导览.md)

---

## 一、核心概念

### 1.1 IoC 控制反转 vs DI 依赖注入

| 维度 | 内容 |
|------|------|
| 是什么 | 将对象创建与依赖管理的控制权从代码转移到容器的设计思想，DI 是其落地实现方式 |
| 能做什么 | 解耦组件依赖；统一管理对象生命周期；支持构造器、Setter、字段三种注入方式；便于单元测试 |
| 怎么用 | `@Component public class OrderService { private final UserRepository userRepository; public OrderService(UserRepository userRepository) { this.userRepository = userRepository; } }` |
| 原理和工作流程 | 容器启动时读取配置元数据（XML、注解、Java Config），生成 BeanDefinition 并注册到 BeanDefinitionRegistry（底层为 ConcurrentHashMap）。实例化阶段通过反射调用构造器创建对象，再根据 @Autowired 等注解完成属性填充。构造器注入在 Spring 4.3+ 可省略 @Autowired，且能保证依赖不可变、强制提供，是推荐方式；字段注入通过反射直接写入字段，隐藏依赖且不利于测试 |
| 缺点 | 字段注入隐藏依赖关系、难以独立测试；过度依赖容器导致代码脱离容器无法运行；构造器注入参数过多时暗示类职责过重 |

### 1.2 Bean 作用域

| 维度 | 内容 |
|------|------|
| 是什么 | 定义容器中 Bean 实例的创建策略和可见范围，决定单例还是多例等生命周期形态 |
| 能做什么 | singleton 全局唯一；prototype 每次新建；request 绑定 HTTP 请求；session 绑定会话；application 绑定 ServletContext |
| 怎么用 | `@Component @Scope("prototype") public class PrototypeBean { }` |
| 原理和工作流程 | singleton 作用域下容器在启动时（或首次请求时）创建唯一实例并缓存于 singletonObjects 一级缓存，后续 getBean 返回同一对象。prototype 作用域下每次 getBean 都调用 createBean 新建实例，容器不缓存其引用，销毁回调也不由容器触发。Web 作用域通过 request 或 context 维度的 Map 存储，并配合 ScopedProxyFactoryBean 生成代理解决单例 Bean 注入 Web 作用域 Bean 的问题 |
| 缺点 | prototype 注入到 singleton 时只创建一次，需 @Lookup 或 ObjectFactory 解决；Web 作用域依赖 Web 环境，非 Web 容器下无法使用；singleton Bean 持有状态会引发线程安全问题 |

---

## 二、底层原理

### 2.1 Bean 容器启动流程

| 维度 | 内容 |
|------|------|
| 是什么 | 容器从配置加载到 Bean 就绪的初始化过程，包含资源定位、定义加载、注册、实例化四个阶段 |
| 能做什么 | 解析 XML、注解、Java Config；构建 BeanDefinition 元数据；注册到 Registry；按需实例化并完成依赖注入 |
| 怎么用 | `AnnotationConfigApplicationContext ctx = new AnnotationConfigApplicationContext(AppConfig.class); UserService service = ctx.getBean(UserService.class);` |
| 原理和工作流程 | 1. Resource 定位找到配置文件；2. BeanDefinitionReader 解析配置生成 BeanDefinition，包含类名、作用域、依赖、初始化方法等元数据；3. 注册到 BeanDefinitionRegistry（底层 ConcurrentHashMap）；4. 对非懒加载的 singleton 调用 createBean 反射实例化，填充属性完成依赖注入，再执行初始化回调和 BeanPostProcessor。BeanFactory 是容器根接口，ApplicationContext 在其基础上扩展事件、国际化、资源加载等企业功能 |
| 缺点 | 启动时全量扫描和实例化导致启动慢；BeanDefinition 元数据占用内存；循环依赖需三级缓存兜底，构造器注入循环依赖无法解决 |

### 2.2 Bean 生命周期

| 维度 | 内容 |
|------|------|
| 是什么 | Bean 从实例化到销毁经历的完整过程，包含实例化、属性赋值、初始化、使用、销毁五个阶段 |
| 能做什么 | 在各阶段插入回调；通过 @PostConstruct 做初始化；通过 @PreDestroy 释放资源；通过 BeanPostProcessor 做增强 |
| 怎么用 | `@PostConstruct public void init() { } @PreDestroy public void destroy() { }` |
| 原理和工作流程 | 1. 反射调用构造器实例化；2. 处理 @Autowired、@Value 完成属性注入；3. Aware 接口回调注入 BeanName、BeanFactory、ApplicationContext；4. BeanPostProcessor.postProcessBeforeInitialization；5. 初始化依次执行 @PostConstruct、InitializingBean.afterPropertiesSet、init-method；6. BeanPostProcessor.postProcessAfterInitialization，AOP 代理在此阶段由 AbstractAutoProxyCreator 生成；7. Bean 就绪；8. 销毁依次执行 @PreDestroy、DisposableBean.destroy、destroy-method |
| 缺点 | 回调接口多、顺序复杂易出错；Aware 注入造成对 Spring API 的耦合；BeanPostProcessor 全局拦截会增加初始化开销 |

### 2.3 循环依赖问题

| 维度 | 内容 |
|------|------|
| 是什么 | 两个或多个 Bean 互相持有对方引用，导致实例化时无法完成依赖注入的循环等待局面 |
| 能做什么 | 通过三级缓存解决 setter、字段注入的 singleton 循环依赖；暴露早期引用让被依赖方先行使用半成品对象 |
| 怎么用 | `@Autowired public void setB(B b) { this.b = b; }` |
| 原理和工作流程 | 一级缓存 singletonObjects 存完全初始化的 Bean，二级缓存 earlySingletonObjects 存早期暴露的半成品，三级缓存 singletonFactories 存 ObjectFactory。以 A 依赖 B、B 依赖 A 为例：创建 A 时先将其 ObjectFactory 放入三级缓存；填充 A 属性时发现需要 B，转而创建 B 并将其 ObjectFactory 放入三级缓存；填充 B 属性时需要 A，从三级缓存获取 A 的 ObjectFactory 生成早期引用并提升到二级缓存；B 完成初始化进入一级缓存；A 随后拿到 B 完成初始化进入一级缓存。三级缓存的存在是为了处理 AOP 代理，确保早期暴露的是代理对象 |
| 缺点 | 构造器注入循环依赖无法解决，抛 BeanCurrentlyInCreationException；仅对 singleton 生效；三级缓存机制复杂，debug 困难；循环依赖本身是设计缺陷，应重构消除 |

### 2.4 AOP 代理原理

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 通过动态代理在运行时为目标 Bean 创建代理对象，将切面逻辑织入方法调用的机制 |
| 能做什么 | 基于接口用 JDK 动态代理；基于继承用 CGLIB 生成子类；按规则自动选择代理方式；在 postProcessAfterInitialization 阶段生成代理 |
| 怎么用 | `spring.aop.proxy-target-class=true` |
| 原理和工作流程 | JDK 动态代理通过 Proxy.newProxyInstance 基于 interfaces 生成代理类，调用时由 InvocationHandler.invoke 反射转发，要求目标类实现接口。CGLIB 通过 ASM 字节码框架生成目标类的子类，覆写非 final 方法，方法调用走 MethodInterceptor.intercept，不能代理 final 类和方法，Spring Boot 2.x 默认使用 CGLIB。代理创建发生在 Bean 生命周期的 postProcessAfterInitialization 阶段，由 AbstractAutoProxyCreator 判断 Bean 是否匹配切点，匹配则包装为代理对象返回容器。Spring AOP 借用 AspectJ 注解语法但实现独立 |
| 缺点 | JDK 代理要求接口；CGLIB 不能代理 final 类和方法且生成子类有内存开销；同类方法内部调用 this 不走代理导致切面失效；代理调用有反射或字节码跳转开销 |

---

## 三、实战应用

### 3.1 自定义 AOP 切面

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 @Aspect 声明切面，结合切入点表达式和通知注解，将横切逻辑织入目标方法的编程实践 |
| 能做什么 | 记录方法调用日志；统计执行耗时；捕获异常并上报；通过 @Around 控制是否执行目标方法 |
| 怎么用 | `@Aspect @Component public class LogAspect { @Around("execution(* com.example.service.*.*(..))") public Object log(ProceedingJoinPoint pjp) throws Throwable { return pjp.proceed(); } }` |
| 原理和工作流程 | Spring 启动时解析 @Aspect 注解的 Bean，将其 advice 与 pointcut 注册到 BeanFactoryAspectJAdvisorsBuilder。在 Bean 后置处理阶段，AnnotationAwareAspectJAutoProxyCreator 扫描所有 Bean，对匹配 pointcut 的 Bean 创建代理。代理方法被调用时，按 @Around、@Before、目标方法、@AfterReturning 或 @AfterThrowing、@After 的顺序织入通知链，@Around 通过 ProceedingJoinPoint.proceed() 控制目标方法执行时机 |
| 缺点 | 切入点表达式书写错误难以排查；环绕通知忘记 proceed 会导致目标方法不执行；切面过多影响性能；非 public 方法和同类调用无法被代理 |

### 3.2 事务管理 AOP 原理

| 维度 | 内容 |
|------|------|
| 是什么 | @Transactional 注解通过 AOP 代理在目标方法前后织入事务开启、提交、回滚逻辑的机制 |
| 能做什么 | 自动管理事务边界；按异常类型回滚；支持传播行为和隔离级别配置；声明式事务免样板代码 |
| 怎么用 | `@Transactional(rollbackFor = Exception.class) public void createOrder(Order order) { }` |
| 原理和工作流程 | Spring 为带 @Transactional 的 Bean 创建代理，调用时由 TransactionInterceptor 拦截。拦截器先通过 PlatformTransactionManager 获取或创建事务，再执行目标方法；正常返回则提交，抛出异常则按 rollbackFor 规则判断是否回滚。事务通过 ThreadLocal 绑定到当前线程的 Connection，保证同一事务内多个 DAO 共用同一连接。默认仅回滚 RuntimeException 和 Error，checked 异常需指定 rollbackFor |
| 缺点 | 方法非 public 不生效；同类方法内部调用不走代理导致失效；异常被 catch 未抛出则不回滚；多线程不共享事务；数据库引擎不支持事务则失效 |

---

## 四、常见面试题（附答案）

### 1. IoC 和 DI 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | IoC 是将对象创建与依赖管理控制权转移给容器的设计思想，DI 是其具体实现方式 |
| 能做什么 | IoC 反转控制方向；DI 通过构造器、Setter、字段注入落地；二者构成 Spring 容器的核心理念 |
| 怎么用 | `@Autowired public void setDao(Dao dao) { this.dao = dao; }` |
| 原理和工作流程 | IoC 强调谁控制对象创建——由容器而非代码控制；DI 强调依赖如何进入对象——由容器主动注入。容器通过 BeanDefinition 描述依赖关系，实例化时按依赖图自动装配。没有 IoC 思想 DI 无从谈起，没有 DI 实现 IoC 只是空谈，Spring 将二者结合，容器既负责创建也负责注入 |
| 缺点 | 概念易混淆，初学者常把二者等同；过度容器化导致对象脱离容器难以独立构造 |

### 2. Spring Bean 的生命周期？

| 维度 | 内容 |
|------|------|
| 是什么 | Bean 从实例化到销毁经历的完整阶段序列，是理解 Spring 容器运作的核心 |
| 能做什么 | 描述各阶段回调顺序；定位 @PostConstruct、AOP 代理、@PreDestroy 的执行时机；排查初始化失败 |
| 怎么用 | `实例化 -> 属性赋值 -> Aware -> BPP前置 -> @PostConstruct -> BPP后置(AOP代理) -> 使用 -> @PreDestroy` |
| 原理和工作流程 | 反射实例化后填充属性，再回调 Aware 接口注入容器引用。BeanPostProcessor 的 before 钩子执行后进入初始化阶段，依次调用 @PostConstruct、InitializingBean.afterPropertiesSet、init-method。after 钩子阶段是 AOP 代理生成点，AbstractAutoProxyCreator 在此包装 Bean。容器关闭时执行销毁链：@PreDestroy、DisposableBean.destroy、destroy-method |
| 缺点 | 阶段多、回调分散，排查问题需理解完整链路；BeanPostProcessor 全局生效可能意外影响其他 Bean |

### 3. Spring AOP 和 AspectJ 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 两种 AOP 实现方案的对比，前者运行时动态代理，后者编译时或加载时字节码织入 |
| 能做什么 | Spring AOP 仅拦截方法执行；AspectJ 可拦截构造器、字段访问、方法调用等更多连接点 |
| 怎么用 | Spring AOP 用 `@Aspect` 注解配置；AspectJ 用 ajc 编译器或加载期 javaagent 织入 |
| 原理和工作流程 | Spring AOP 在运行时通过 JDK 动态代理或 CGLIB 创建代理对象，调用时反射或字节码跳转织入切面，性能略低但使用简单。AspectJ 在编译时通过 ajc 编译器直接修改字节码，或类加载时通过 javaagent 织入，切面逻辑与目标代码融为一体，调用时无代理开销，性能更高但需要额外编译器或织入器配置。Spring AOP 借用了 AspectJ 的注解语法但实现独立 |
| 缺点 | Spring AOP 只支持方法级连接点、性能有代理开销；AspectJ 配置复杂、学习曲线陡、需集成编译器插件 |

### 4. 如何解决 Spring Bean 的循环依赖？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 通过三级缓存机制解决 setter、字段注入的 singleton Bean 循环依赖的方案 |
| 能做什么 | 暴露早期半成品引用；处理 AOP 代理对象的提前暴露；判断哪些循环依赖可解、哪些不可解 |
| 怎么用 | setter 注入循环依赖自动解决；构造器注入循环依赖需重构或改用 setter |
| 原理和工作流程 | singletonObjects（一级）存成品、earlySingletonObjects（二级）存半成品、singletonFactories（三级）存 ObjectFactory。创建 A 时将其 ObjectFactory 入三级缓存，填充属性遇 B 则创建 B；B 填充属性遇 A，从三级缓存调用 ObjectFactory 生成 A 的早期引用（若需代理则生成代理）并提升到二级缓存，B 完成后入一级缓存；A 取得 B 完成初始化入一级缓存。三级缓存的存在是为在需要时才生成代理，避免不必要的提前代理 |
| 缺点 | 构造器注入循环依赖无法解决，抛 BeanCurrentlyInCreationException；仅对 singleton 且 setter、字段注入生效；机制复杂，循环依赖本身应通过重构消除 |

### 5. Spring 中使用了哪些设计模式？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 框架在源码中落地的经典 GoF 设计模式集合，是框架设计的典型范例 |
| 能做什么 | 单例（Bean 默认 scope）；工厂（BeanFactory）；代理（AOP）；模板方法（JdbcTemplate）；观察者（事件机制）；策略（Resource）；适配器（HandlerAdapter） |
| 怎么用 | `jdbcTemplate.query(sql, rowMapper);` `ctx.publishEvent(new OrderCreatedEvent(order));` |
| 原理和工作流程 | Bean 默认 singleton 作用域，容器缓存唯一实例体现单例模式。BeanFactory 作为根接口隔离使用与创建体现工厂模式。AOP 通过 JDK 或 CGLIB 代理实现代理模式。JdbcTemplate 定义算法骨架、子类覆写回调体现模板方法。ApplicationEventPublisher 发布事件、ApplicationListener 监听体现观察者模式。Resource 接口不同实现（ClassPathResource、FileSystemResource）体现策略模式。HandlerAdapter 适配不同类型 Handler 体现适配器模式 |
| 缺点 | 模式密集增加源码阅读门槛；单例 Bean 的状态管理易引发线程安全问题；工厂和代理层层包装导致调试栈深 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 开发中 AOP 失效、事务不回滚、Prototype 注入 Singleton 等高频误用的汇总与对策 |
| 能做什么 | 识别 @Transactional 失效场景；处理 AOP 同类调用失效；解决 Prototype Bean 注入 Singleton 陷阱 |
| 怎么用 | `@Autowired @Lazy private OrderService self;` |
| 原理和工作流程 | AOP 同类调用失效是因为 this 指向目标对象而非代理对象，切面拦截不到，需通过 AopContext.currentProxy() 或注入自身代理解决。@Transactional 失效根源在于代理只拦截 public 方法、同类调用不走代理、异常被吞不传播、引擎不支持事务、多线程事务绑定 ThreadLocal 不共享。Prototype Bean 注入 Singleton 时只创建一次，因为 Singleton 只初始化一次，需 @Lookup 或 ObjectFactory 每次获取新实例 |
| 缺点 | 陷阱隐蔽，新手难以察觉；解决方案多样需按场景选择；注入自身代理有循环依赖风险需配合 @Lazy |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./01-Spring-IoC与AOP深度.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
