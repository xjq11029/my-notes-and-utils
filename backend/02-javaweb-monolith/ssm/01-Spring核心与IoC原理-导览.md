# Spring 核心与 IoC 原理 导览

> 定位：五维框架浓缩提炼 01-Spring核心与IoC原理.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./01-Spring核心与IoC原理.md)。
> 前置知识：无

---

## 一、核心概念

### 1.1 Spring 框架概述

| 维度 | 内容 |
|------|------|
| 是什么 | 开源 Java 企业级开发框架，核心是 IoC 控制反转和 AOP 面向切面编程 |
| 能做什么 | 通过 IoC/DI 解耦组件依赖；通过 AOP 统一处理横切关注点；提供事务抽象统一事务管理；集成 ORM 框架；自带 SpringMVC Web 框架 |
| 怎么用 | `@Component` 声明 Bean；`@Autowired` 注入依赖；`@Aspect` 定义切面；`@Transactional` 声明事务 |
| 原理和工作流程 | Spring 容器读取配置（XML/注解/Java Config）解析生成 BeanDefinition，注册到 BeanDefinitionRegistry，然后实例化 Bean 完成依赖注入，通过 BeanPostProcessor 对 Bean 进行增强如生成 AOP 代理。设计理念是约定优于配置，简化企业级开发，避免过度模板化和工厂工厂等样板代码 |
| 缺点 | 容器启动有开销；魔法注解多新手难理解底层原理；配置错误排查难；过度依赖容器导致脱离容器难以独立运行 |

### 1.2 IoC 容器

| 维度 | 内容 |
|------|------|
| 是什么 | 将对象创建和依赖管理控制权反转给容器的核心机制，BeanFactory 是根接口，ApplicationContext 是功能扩展实现 |
| 能做什么 | 由容器负责对象实例化、配置、生命周期管理；对比 BeanFactory 和 ApplicationContext 在功能、初始化时机、扩展特性上的差异 |
| 怎么用 | `ClassPathXmlApplicationContext` 加载 XML；`AnnotationConfigApplicationContext` 加载 Java Config |
| 原理和工作流程 | BeanFactory 只提供基础容器功能，采用懒加载，用到才实例化 Bean。ApplicationContext 继承 BeanFactory，添加国际化、事件机制、资源加载、注解支持等企业级功能，启动时饿加载所有非懒加载 singleton Bean。BeanFactory 适合轻量场景，ApplicationContext 功能更全是开发常用选择 |
| 缺点 | BeanFactory 功能太弱不支持注解和企业特性；ApplicationContext 饿加载导致启动慢；二者继承关系容易混淆懒加载饿加载区别 |

### 1.3 依赖注入三种方式

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 支持构造器注入、Setter 注入、字段注入三种依赖注入方式，推荐构造器注入 |
| 能做什么 | 构造器注入用于强制依赖保证不可变；Setter 注入用于可选依赖；字段注入写法简洁但不推荐 |
| 怎么用 | `@Component public class Service { private final Dep dep; public Service(Dep dep) { this.dep = dep; } }` |
| 原理和工作流程 | 构造器注入通过构造方法参数注入依赖，Spring 4.3+ 单构造器可省略 @Autowired，保证依赖不可变、强制提供，便于单元测试，循环依赖能提前暴露。Setter 注入通过 setter 方法注入，适用于可选依赖可设置默认值。字段注入通过 @Autowired 标注字段由反射直接赋值，隐藏依赖关系不便于测试，循环依赖问题延后暴露容易运行时出错 |
| 缺点 | 字段注入隐藏依赖不便于测试；构造器参数过多暗示类职责过重；Setter 注入允许中途修改依赖；循环依赖下构造器注入直接失败能提醒重构 |

### 1.4 Bean 生命周期

| 维度 | 内容 |
|------|------|
| 是什么 | Bean 从实例化到销毁经历的完整流程，包含多个回调扩展点 |
| 能做什么 | 在各阶段插入自定义逻辑；@PostConstruct 做初始化；@PreDestroy 释放资源；BeanPostProcessor 做全局增强 |
| 怎么用 | `@PostConstruct public void init() {} @PreDestroy public void destroy() {}` |
| 原理和工作流程 | 完整流程：1. 反射实例化；2. 属性注入 @Autowired @Value；3. Aware 接口回调注入 BeanName、BeanFactory、ApplicationContext；4. BeanPostProcessor.postProcessBeforeInitialization；5. 初始化依次执行 @PostConstruct、InitializingBean.afterPropertiesSet、init-method；6. BeanPostProcessor.postProcessAfterInitialization，AOP 代理在此阶段生成；7. Bean 就绪；8. 销毁依次执行 @PreDestroy、DisposableBean.destroy、destroy-method |
| 缺点 | 生命周期环节多回调分散，排查问题需要完整理解链路；BeanPostProcessor 全局生效可能意外影响其他 Bean；顺序敏感理解复杂 |

### 1.5 AOP 代理

| 维度 | 内容 |
|------|------|
| 是什么 | Spring AOP 支持 JDK 动态代理和 CGLIB 代理两种方式，用于生成代理对象织入横切逻辑 |
| 能做什么 | JDK 动态代理基于接口；CGLIB 基于继承生成子类；按规则自动选择代理方式 |
| 怎么用 | `proxy-target-class="true"` 强制使用 CGLIB |
| 原理和工作流程 | JDK 动态代理基于接口，使用 java.lang.reflect.Proxy + InvocationHandler 在运行时生成实现目标接口的代理类，要求目标类必须实现接口，方法调用经反射转发，依赖 JDK 原生无需额外 jar。CGLIB 基于继承，通过 ASM 字节码框架生成目标类的子类覆写方法，不需要接口，不能代理 final 类和 final 方法，调用直接走子类方法性能更好。Spring 默认规则：目标实现接口用 JDK，否则用 CGLIB，Spring Boot 2.x+ 默认 proxyTargetClass=true 即强制 CGLIB |
| 缺点 | JDK 代理要求必须有接口；CGLIB 不能代理 final 类和方法；生成子类有内存开销；同类内部调用 this 不走代理导致切面失效 |

### 1.6 Spring 事务管理

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 提供声明式事务和编程式事务两种管理方式，@Transactional 注解声明式事务是推荐用法 |
| 能做什么 | 支持 7 种传播行为、4 种隔离级别；自动处理事务开启提交回滚；失效场景需识别避免 |
| 怎么用 | `@Transactional(rollbackFor = Exception.class) public void createOrder() { }` |
| 原理和工作流程 | 声明式事务本质是 AOP 增强，@Around 环绕通知在目标方法前后织入逻辑：1. 获取或创建事务；2. 执行目标方法；3. 正常返回提交；4. 异常判断是否回滚，需要则回滚。事务连接通过 ThreadLocal 绑定到当前线程，保证同一事务多个 DAO 共用一个连接。传播行为定义多个方法间事务如何传播，隔离级别定义事务间隔离程度 |
| 缺点 | 代理机制导致多种失效场景；传播行为组合复杂容易理解错；隔离级别配置需数据库配合；多线程不共享事务 |

---

## 二、底层原理

### 2.1 Spring IoC 容器启动流程

| 维度 | 内容 |
|------|------|
| 是什么 | IoC 容器从配置加载到 Bean 就绪的完整启动过程，分为资源定位、定义解析、注册、实例化四阶段 |
| 能做什么 | 解析 XML/注解/Java Config；构建 BeanDefinition 元数据；注册到注册表；实例化非懒加载 Bean |
| 怎么用 | `new AnnotationConfigApplicationContext(AppConfig.class)` 启动容器 |
| 原理和工作流程 | 1. Resource 定位找到配置资源；2. BeanDefinitionReader 解析配置生成 BeanDefinition，包含类名、作用域、依赖、初始化方法等元数据；3. 注册到 BeanDefinitionRegistry，底层是 ConcurrentHashMap<String, BeanDefinition>；4. 遍历非懒加载 singleton Bean，依次调用 createBean 完成实例化、属性注入、初始化。BeanFactory 是根接口定义 getBean 等基础方法，ApplicationContext 在其基础上扩展企业功能 |
| 缺点 | 启动时全量扫描实例化导致启动慢；BeanDefinition 元数据占用内存；循环依赖需三级缓存兜底 |

### 2.2 Bean 生命周期详细流程

| 维度 | 内容 |
|------|------|
| 是什么 | Bean 生命周期各环节扩展点汇总，BeanFactoryPostProcessor、BeanPostProcessor、Aware 等 |
| 能做什么 | BeanFactoryPostProcessor 在实例化前修改 BeanDefinition；BeanPostProcessor 在初始化前后增强 Bean；Aware 注入容器信息 |
| 怎么用 | `BeanFactoryPostProcessor`、`BeanPostProcessor` 实现接口注册为 Bean |
| 原理和工作流程 | BeanFactoryPostProcessor 执行时机是 BeanDefinition 注册完成后，Bean 实例化之前，可修改 BeanDefinition 元数据。BeanPostProcessor 在 Bean 初始化前后执行，每个 Bean 初始化都会经过该处理器，AOP 代理就是在 postProcessAfterInitialization 生成。Aware 接口回调让 Bean 获取容器引用如 BeanName、BeanFactory、ApplicationContext，会耦合 Spring API |
| 缺点 | 扩展点多顺序容易记混；BeanFactoryPostProcessor 全局修改风险大；Aware 接口耦合 Spring API |

### 2.3 AOP 代理生成时机

| 维度 | 内容 |
|------|------|
| 是什么 | AOP 代理在 Bean 生命周期的具体生成位置，由 AbstractAutoProxyCreator 处理 |
| 能做什么 | 在 Bean 初始化后包装生成代理；判断 Bean 是否匹配切点；匹配则返回代理对象 |
| 怎么用 | 匹配切点的 Bean 自动被代理，无需手动处理 |
| 原理和工作流程 | AOP 代理生成发生在 BeanPostProcessor.postProcessAfterInitialization 阶段，Bean 已经完成实例化、属性注入、初始化，AbstractAutoProxyCreator 判断该 Bean 是否匹配切入点表达式，匹配则通过 JDK 或 CGLIB 创建代理对象返回容器，后续注入依赖使用的是代理对象 |
| 缺点 | 代理创建发生在初始化后，若 Bean 初始化阶段就需要切面增强则无法生效；代理对象创建有性能开销 |

### 2.4 事务代理机制

| 维度 | 内容 |
|------|------|
| 是什么 | @Transactional 注解事务基于 AOP 代理实现的核心原理 |
| 能做什么 | 在方法调用前后织入事务开启提交回滚逻辑；绑定连接到 ThreadLocal；按异常类型判断回滚 |
| 怎么用 | `@EnableTransactionManagement` 开启注解驱动，`@Transactional` 标注方法或类 |
| 原理和工作流程 | @Transactional 注解通过 AOP 织入，TransactionInterceptor 作为切面拦截方法调用。拦截器先通过 PlatformTransactionManager 从 DataSource 获取连接，按照传播行为判断是新建还是加入现有事务，然后绑定到 ThreadLocal；执行目标方法；正常返回则提交事务；抛出异常判断是否匹配 rollbackFor 规则，需要回滚则回滚。ThreadLocal 绑定保证同一线程同一事务多个 DAO 共用同一个连接 |
| 缺点 | 依赖 AOP 代理所以存在多种失效场景；默认只回滚 RuntimeException 需配置 rollbackFor；事务绑定 ThreadLocal 跨线程不共享 |

---

## 三、实战应用

### 3.1 构造器注入最佳实践

| 维度 | 内容 |
|------|------|
| 是什么 | 构造器注入配合 final 字段是 Spring 官方推荐的依赖注入写法 |
| 能做什么 | 保证依赖不可变；强制依赖不能为空；便于单元测试；提前暴露循环依赖 |
| 怎么用 | `@Service public class Service { private final Dep dep; public Service(Dep dep) { this.dep = dep; } }` |
| 原理和工作流程 | final 字段保证不可变，构造器注入保证依赖在对象创建时就完成注入，Spring 4.3+ 如果类只有一个构造器可以省略 @Autowired 注解简化写法。若有多个构造器需要给一个加 @Autowired 告诉 Spring 使用哪个 |
| 缺点 | 参数过多时构造器臃肿暗示类职责过重需要拆分；循环依赖下直接启动失败必须重构 |

### 3.2 自定义 AOP 切面日志

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 @Aspect 注解定义切面，@Around 环绕通知记录方法调用日志、参数、耗时、异常 |
| 能做什么 | 统一记录 Service 层方法调用日志；统计执行耗时；异常时记录错误日志 |
| 怎么用 | `@Aspect @Component public class LogAspect { @Around("execution(* com.example.service..*.*(..))") public Object log(ProceedingJoinPoint pjp) throws Throwable { return pjp.proceed(); } }` |
| 原理和工作流程 | @Aspect 标记该类是切面，@Pointcut 定义切入点表达式匹配需要拦截的方法，@Around 环绕通知可以控制目标方法执行时机。ProceedingJoinPoint 可以获取方法签名、参数，调用 proceed() 执行目标方法。记录开始时间，执行完计算耗时，正常记录完成，异常记录错误并重新抛出不吞异常 |
| 缺点 | 切入点表达式写错不拦截；忘记 proceed() 目标方法不执行；高并发下大量日志影响性能；同类调用不走代理 |

### 3.3 声明式事务配置

| 维度 | 内容 |
|------|------|
| 是什么 | 开启注解事务并在 Service 层使用 @Transactional 声明事务的完整配置 |
| 能做什么 | 支持 @Transactional 注解；配置 PlatformTransactionManager；rollbackFor 配置正确回滚规则 |
| 怎么用 | `@Configuration @EnableTransactionManagement public class TxConfig { @Bean public PlatformTransactionManager txManager(DataSource ds) { return new DataSourceTransactionManager(ds); } }` |
| 原理和工作流程 | @EnableTransactionManagement 开启注解事务支持，注册 AnnotationTransactionAttributeSource 解析 @Transactional 注解，注册 InfrastructureAdvisorAutoProxyCreator 创建代理。DataSourceTransactionManager 管理 DataSource 连接，根据 @Transactional 属性配置传播行为、隔离级别、超时等。推荐配置 rollbackFor = Exception.class 让所有异常包括 checked exception 都回滚避免数据不一致 |
| 缺点 | 忘记 @EnableTransactionManagement 注解不生效；rollbackFor 未配置导致 checked 异常不回滚；多个数据源需要配置多个事务管理器 |

---

## 四、常见面试题

### 1. IoC 和 DI 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | IoC 是控制反转设计思想，DI 依赖注入是 IoC 的具体实现方式 |
| 能做什么 | IoC 反转对象创建控制权；DI 实现依赖注入到对象中；二者思想与实现的关系 |
| 怎么用 | IoC 由容器管理 Bean，DI 通过构造器/Setter/字段注入依赖 |
| 原理和工作流程 | IoC（Inversion of Control）是一种设计思想，主张将对象创建和依赖管理的控制权从应用代码转移到容器，由容器负责实例化和生命周期管理，应用代码只需声明依赖不需要自己 new。DI（Dependency Injection）是 IoC 的具体实现方式，容器在运行时根据依赖关系将依赖对象注入到目标对象中。IoC 是思想层面，DI 是实现层面，没有 DI 实现 IoC 只是空谈 |
| 缺点 | 概念容易混淆，初学者常将二者等同；过度依赖容器导致对象脱离容器难以实例化 |

### 2. BeanFactory 和 ApplicationContext 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 两个核心容器接口，BeanFactory 是根接口，ApplicationContext 继承扩展 |
| 能做什么 | BeanFactory 只提供基础容器功能懒加载；ApplicationContext 添加企业功能饿加载 |
| 怎么用 | 开发一般用 ApplicationContext，轻量场景用 BeanFactory |
| 原理和工作流程 | BeanFactory 是 IoC 容器根接口，只定义基础方法如 getBean，默认懒加载即用到才实例化 Bean，不支持国际化、事件、资源加载等扩展。ApplicationContext 继承 BeanFactory，添加国际化支持、事件发布机制、资源加载、注解支持、BeanFactoryPostProcessor 自动执行等，默认饿加载启动时实例化所有非懒加载 Bean。ApplicationContext 功能更全是开发默认选择 |
| 缺点 | ApplicationContext 饿加载启动慢；BeanFactory 功能太弱不支持注解 |

### 3. 依赖注入三种方式对比，推荐哪种？

| 维度 | 内容 |
|------|------|
| 是什么 | 构造器注入、Setter 注入、字段注入三种注入方式对比，推荐构造器注入 |
| 能做什么 | 构造器强制依赖不可变；Setter 可选依赖；字段注入简洁但有缺点 |
| 怎么用 | 强制依赖用构造器，可选依赖用 Setter，尽量不用字段注入 |
| 原理和工作流程 | 构造器注入：依赖在构造时确定不可变，强制提供不能为空，便于单元测试，循环依赖提前暴露无法启动，Spring 官方推荐。Setter 注入：用于可选依赖，可后续修改，循环依赖能注入成功但运行可能出问题。字段注入：@Autowired 直接标注字段，写法简洁，但是依赖隐藏，不便于测试，循环依赖问题延后暴露，Spring 不推荐。构造器注入保证依赖不可变，符合不可变对象设计原则 |
| 缺点 | 构造器参数过多暗示职责过重；Setter 允许中途修改依赖；字段注入隐藏依赖不利于测试 |

### 4. 说出 Spring Bean 的完整生命周期？

| 维度 | 内容 |
|------|------|
| 是什么 | 从实例化到销毁完整顺序，各阶段回调 |
| 能做什么 | 定位扩展点执行顺序；记住 AOP 代理生成时机；初始化销毁回调顺序 |
| 怎么用 | 实例化 → 属性注入 → Aware → BPP 前置 → 初始化 → BPP 后置 → 使用 → 销毁 |
| 原理和工作流程 | 完整顺序：1. 反射实例化；2. 依赖注入填充属性；3. Aware 接口回调注入容器信息；4. BeanPostProcessor.postProcessBeforeInitialization；5. 初始化：@PostConstruct → InitializingBean.afterPropertiesSet() → init-method；6. BeanPostProcessor.postProcessAfterInitialization，AOP 代理在此生成；7. Bean 就绪可用；8. 容器关闭时销毁：@PreDestroy → DisposableBean.destroy() → destroy-method |
| 缺点 | 环节多容易记混顺序；多个回调扩展点理解成本高 |

### 5. JDK 动态代理和 CGLIB 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring AOP 两种代理实现方式对比 |
| 能做什么 | JDK 基于接口，CGLIB 基于继承；默认选择规则不同 |
| 怎么用 | Spring 默认实现接口用 JDK，否则 CGLIB；Spring Boot 2.x 默认 CGLIB |
| 原理和工作流程 | JDK 动态代理：基于接口，使用 Proxy.newProxyInstance 生成代理类实现目标接口，InvocationHandler 处理方法调用，反射转发，要求目标类必须实现接口，JDK 原生无依赖，调用有反射开销。CGLIB：基于继承，ASM 字节码生成子类覆写方法，不需要接口，不能代理 final 类和 final 方法，调用直接走子类性能更好，需要额外 ASM 依赖。Spring Boot 2.x 默认 spring.aop.proxy-target-class=true 即不管是否实现接口都用 CGLIB |
| 缺点 | JDK 要求必须有接口；CGLIB 不能代理 final；二者都无法代理 private 方法；同类调用不走代理 |

### 6. @Transactional 失效场景有哪些？

| 维度 | 内容 |
|------|------|
| 是什么 | @Transactional 注解不生效事务不回滚的常见原因汇总 |
| 能做什么 | 识别失效场景；排查事务不回滚问题 |
| 怎么用 | 避免非 public 方法；避免同类调用；异常必须抛出到代理层；用 InnoDB 引擎 |
| 原理和工作流程 | 常见失效场景：① 方法非 public，Spring AOP 只拦截 public 方法，private/protected 不生成代理；② 同类方法内部调用，this.method() 直接调用目标对象不走代理，切面不生效；③ 异常被 catch 吃掉没有重新抛出，代理层检测不到异常不回滚；④ 数据库引擎不支持事务如 MyISAM；⑤ 多线程场景，事务绑定 ThreadLocal 新线程不共享；⑥ 注解在接口上，CGLIB 代理读不到接口注解；⑦ propagation 设置为 NOT_SUPPORTED 挂起事务。默认只回滚 RuntimeException，checked 异常不回滚需 rollbackFor = Exception.class |
| 缺点 | 失效场景隐蔽排查困难；多种原因可能同时存在；代理机制本身限制无法完全避免 |

### 7. Spring 事务传播行为有哪几种？默认是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | 多个事务方法互相调用时，事务如何传播的七种定义 |
| 能做什么 | REQUIRED 默认加入或新建；REQUIRES_NEW 总是新建挂起当前；NESTED 嵌套事务 |
| 怎么用 | 默认 REQUIRED，需要独立事务用 REQUIRES_NEW |
| 原理和工作流程 | 七种传播行为：REQUIRED（默认）：有事务就加入，没有就新建，适用于绝大多数场景。REQUIRES_NEW：总是新建事务，挂起当前事务，适用于需要独立事务不影响外层的场景。NESTED：如果有事务就在嵌套事务中执行，外层回滚嵌套也回滚，嵌套回滚外层可捕获不回滚，没有就新建。SUPPORTS：有事务加入，没有就不使用。NOT_SUPPORTED：不使用事务，挂起当前事务。MANDATORY：必须在事务中执行否则抛异常。NEVER：必须不使用事务否则抛异常 |
| 缺点 | 传播行为组合复杂容易理解错；嵌套事务需要数据库支持；REQUIRES_NEW 会挂起当前事务新建连接有性能开销 |

### 8. Spring 事务隔离级别有哪几种？MySQL 默认是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | 定义多个事务并发执行时的隔离程度，四种隔离级别 |
| 能做什么 | 解决脏读、不可重复读、幻读问题；隔离越高性能越差 |
| 怎么用 | MySQL InnoDB 默认 REPEATABLE_READ |
| 原理和工作流程 | 四种隔离级别：READ_UNCOMMITTED（读未提交）允许脏读不可重复读幻读，几乎不用。READ_COMMITTED（读已提交）解决脏读，允许不可重复读幻读，多数数据库默认。REPEATABLE_READ（可重复读）解决脏读不可重复读，允许幻读，MySQL InnoDB 默认通过 MVCC 解决了幻读。SERIALIZABLE（串行化）解决所有问题完全隔离，性能差几乎不用。脏读：一个事务读到另一个事务未提交的数据。不可重复读：同一个事务两次读取同一行数据结果不同。幻读：同一个事务两次范围查询行数不同 |
| 缺点 | 隔离越高并发性能越低；READ_UNCOMMITTED 几乎不用；SERIALIZABLE 性能太差 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | Spring IoC/AOP/事务开发中常见坑点汇总及解决方案 |
| 能做什么 | 识别 AOP 同类调用失效；事务不回滚；循环依赖；CGLIB 代理 final 类；多线程事务 |
| 怎么用 | 使用自身注入代理解决同类调用；添加 rollbackFor 配置；构造器注入提前暴露循环依赖 |
| 原理和工作流程 | AOP 同类调用失效原因是 this 指向目标对象而非代理，切面拦截不到，解决方案：拆分为两个 Service；AopContext.currentProxy() 获取代理；自身注入自身 @Autowired @Lazy 注入代理调用。@Transactional 不回滚因为默认只回滚 RuntimeException，需 rollbackFor = Exception.class。字段注入循环依赖能启动但是运行可能 NPE，构造器注入启动就失败提前暴露。CGLIB 不能代理 final 类因为要继承，所以不能有 final。多线程事务不共享因为绑定 ThreadLocal，跨线程不传递 |
| 缺点 | 坑点隐蔽新手难以发现；多种解决方案各有适用场景；自身注入有循环依赖风险需 @Lazy |

---

> [返回原文](./01-Spring核心与IoC原理.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
