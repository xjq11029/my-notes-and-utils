# MyBatis 整合与配置 导览

> 定位：五维框架浓缩提炼 03-MyBatis整合与配置.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./03-MyBatis整合与配置.md)。
> 前置知识：[Spring核心与IoC原理](./01-Spring核心与IoC原理-导览.md)、[SpringMVC执行流程](./02-SpringMVC执行流程-导览.md)

---

## 一、核心概念

### 1.1 SSM 整合思路

| 维度 | 内容 |
|------|------|
| 是什么 | 将 Spring、SpringMVC、MyBatis 三个框架整合为三层架构，Spring 作为粘合剂容器统一管理所有 Bean |
| 能做什么 | 表现层 SpringMVC 处理 HTTP 请求；业务层 Spring 管理事务和依赖注入；持久层 MyBatis 执行 SQL |
| 怎么用 | Spring 配置管理 Service、DAO、事务；SpringMVC 配置管理 Controller、视图解析；MyBatis 通过 SqlSessionFactoryBean 和 MapperScannerConfigurer 整合 |
| 原理和工作流程 | Spring 作为核心容器通过 IoC 管理所有组件。SpringMVC 的 DispatcherServlet 创建子容器管理 Controller，ContextLoaderListener 创建父容器管理 Service 和 DAO，形成父子容器关系。MyBatis 的 SqlSessionFactory 和 Mapper 接口由 Spring 容器管理，通过 FactoryBean 和扫描器注册为 Bean。分层优势：各层职责单一，降低耦合，DAO 层替换不影响上层 |
| 缺点 | 三个框架整合配置复杂，初学者容易遗漏；父子容器关系抽象难理解；配置错误排查困难 |

### 1.2 Spring 整合 MyBatis

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 SqlSessionFactoryBean 创建 SqlSessionFactory，通过 MapperScannerConfigurer 扫描 Mapper 接口注册为 Bean |
| 能做什么 | SqlSessionFactoryBean 封装 MyBatis 配置（DataSource、Mapper XML、别名、插件）；MapperScannerConfigurer 自动扫描 Mapper 接口生成代理对象 |
| 怎么用 | `@Bean SqlSessionFactoryBean` 配置 DataSource 和 mapperLocations；`@MapperScan("com.example.mapper")` 扫描 Mapper 接口 |
| 原理和工作流程 | SqlSessionFactoryBean 实现 FactoryBean 接口，getObject() 通过 SqlSessionFactoryBuilder.build() 创建 SqlSessionFactory，封装 DataSource、Mapper XML 路径、别名包、插件等配置。MapperScannerConfigurer 实现 BeanDefinitionRegistryPostProcessor，在 BeanDefinition 注册阶段扫描指定包下 Mapper 接口，为每个接口创建 MapperFactoryBean 的 BeanDefinition（MapperFactoryBean 也是 FactoryBean，getObject() 调用 SqlSession.getMapper() 生成代理对象）。@MapperScan 是 MapperScannerConfigurer 的注解简化版 |
| 缺点 | 配置项多容易遗漏；Mapper XML 路径通配符写错导致映射失败；多数据源配置复杂 |

### 1.3 Spring 整合 SpringMVC

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 ContextLoaderListener 创建 Spring 根容器，通过 DispatcherServlet 创建子容器，形成父子容器关系 |
| 能做什么 | ContextLoaderListener 在 Web 容器启动时初始化根容器管理 Service、DAO、事务；DispatcherServlet 初始化子容器管理 Controller、视图解析 |
| 怎么用 | 配置 ContextLoaderListener 和 contextConfigLocation；配置 DispatcherServlet 和 springmvc-servlet.xml |
| 原理和工作流程 | ContextLoaderListener 实现 ServletContextListener，在 Web 容器启动时触发 contextInitialized 方法，创建 Root WebApplicationContext 加载 applicationContext.xml，管理 Service、DAO、事务等 Bean，存入 ServletContext。DispatcherServlet 继承 HttpServlet，init 方法中创建 Servlet WebApplicationContext 子容器，从 ServletContext 获取根容器设置为父容器，加载 springmvc-servlet.xml 管理 Controller、HandlerMapping、ViewResolver 等 |
| 缺点 | 两个容器独立配置增加维护成本；配置文件拆分不当导致 Bean 找不到；ContextLoaderListener 在 Servlet 3.0+ 可用代码配置替代 XML |

### 1.4 父子容器关系

| 维度 | 内容 |
|------|------|
| 是什么 | 父容器（Root WebApplicationContext）管理非 Web 层 Bean，子容器（Servlet WebApplicationContext）管理 Web 层 Bean，子容器可访问父容器 Bean |
| 能做什么 | 隔离 Web 层和非 Web 层；子容器注入父容器 Service；父容器不受子容器影响；避免 Controller 被父容器扫描导致事务失效 |
| 怎么用 | 父容器：`<context:component-scan>` 排除 Controller；子容器：只扫描 Controller |
| 原理和工作流程 | 父容器由 ContextLoaderListener 创建，管理 Service、DAO、事务管理器、数据源等，配置文件为 applicationContext.xml。子容器由 DispatcherServlet 创建，管理 Controller、HandlerMapping、ViewResolver 等，配置文件为 springmvc-servlet.xml。子容器可以访问父容器 Bean（Controller 可以注入 Service），父容器不能访问子容器 Bean（Service 不能注入 Controller）。访问优先级：子容器先查自己的 Bean，找不到再到父容器查找。包扫描必须隔离，父容器排除 Controller 注解，子容器只含 Controller 注解 |
| 缺点 | 父子容器关系抽象难理解；包扫描隔离配置不当导致事务失效；两个容器启动顺序有依赖 |

### 1.5 常见整合问题

| 维度 | 内容 |
|------|------|
| 是什么 | SSM 整合中事务不生效、DAO 注入失败、父子容器扫描冲突等高频问题汇总 |
| 能做什么 | 识别事务不生效的排查步骤；定位 DAO 注入失败的配置原因；解决父子容器扫描冲突 |
| 怎么用 | 检查 @EnableTransactionManagement、@MapperScan、包扫描隔离配置、@Transactional 注解位置 |
| 原理和工作流程 | 事务不生效排查：1. 检查是否配置 DataSourceTransactionManager 和 @EnableTransactionManagement；2. 检查 @Transactional 是否在 Service 层而非 Controller；3. 检查包扫描是否隔离，Controller 被父容器扫描会导致事务代理失效。DAO 注入失败排查：1. 检查 @MapperScan 或 MapperScannerConfigurer 是否配置且 basePackage 正确；2. 检查 DataSource 连接是否可用；3. 检查 Mapper XML 文件路径是否匹配。父子容器扫描冲突：父容器和子容器同时扫描同一包导致 Bean 重复创建，Controller 在父容器中无事务代理，解决方法是严格隔离包扫描 |
| 缺点 | 问题排查需要理解完整整合链路；配置错误导致功能静默失效；多个问题可能同时存在 |

---

## 二、底层原理

### 2.1 ContextLoaderListener 初始化流程

| 维度 | 内容 |
|------|------|
| 是什么 | ContextLoaderListener 在 Web 容器启动时创建 Root WebApplicationContext 的初始化流程 |
| 能做什么 | 创建根容器；加载 Spring 配置文件；初始化 Service、DAO、事务等 Bean；存入 ServletContext |
| 怎么用 | 配置在 web.xml 中或通过 WebApplicationInitializer 代码替代 |
| 原理和工作流程 | 1. Web 容器启动触发 ContextLoaderListener.contextInitialized 方法。2. 读取 contextConfigLocation 配置参数获取 Spring 配置文件路径。3. 创建 XmlWebApplicationContext 或 AnnotationConfigWebApplicationContext。4. 调用 refresh() 方法初始化容器，扫描 Bean 创建 Service、DAO、事务管理器等。5. 将 Root WebApplicationContext 存入 ServletContext 属性中，供 DispatcherServlet 后续获取父容器引用 |
| 缺点 | 启动失败时 Web 应用无法部署；XML 配置方式较繁琐；Servlet 3.0+ 推荐用代码配置替代 |

### 2.2 DispatcherServlet 初始化流程

| 维度 | 内容 |
|------|------|
| 是什么 | DispatcherServlet 作为 Servlet 初始化时创建子容器并建立父子关系的流程 |
| 能做什么 | 创建 Servlet WebApplicationContext；获取根容器设为父容器；扫描 Controller；初始化九大组件 |
| 怎么用 | 配置在 web.xml 中或通过 WebApplicationInitializer 代码配置 |
| 原理和工作流程 | 1. DispatcherServlet.init() 方法被 Servlet 容器调用。2. 创建 Servlet WebApplicationContext（XmlWebApplicationContext 或 AnnotationConfigWebApplicationContext）。3. 从 ServletContext 获取 Root WebApplicationContext 设置为父容器。4. 加载 DispatcherServlet 专属配置文件（springmvc-servlet.xml）。5. 扫描 Controller 等 Web 层 Bean。6. 调用 initStrategies() 初始化 HandlerMapping、HandlerAdapter、ViewResolver 等九大组件 |
| 缺点 | 初始化顺序依赖根容器，根容器未初始化完成时 DispatcherServlet 初始化失败；配置加载路径错误导致启动失败 |

### 2.3 MapperScannerConfigurer 原理

| 维度 | 内容 |
|------|------|
| 是什么 | 实现 BeanDefinitionRegistryPostProcessor 接口，在 Bean 定义注册阶段扫描 Mapper 接口并注册为 BeanDefinition |
| 能做什么 | 扫描指定包下 Mapper 接口；为每个接口创建 MapperFactoryBean 的 BeanDefinition；最终通过 SqlSession.getMapper 生成代理 |
| 怎么用 | `@MapperScan("com.example.mapper")` 或 `new MapperScannerConfigurer().setBasePackage("com.example.mapper")` |
| 原理和工作流程 | MapperScannerConfigurer 实现 BeanDefinitionRegistryPostProcessor，其 postProcessBeanDefinitionRegistry 方法在 Bean 定义注册阶段执行。使用 ClassPathMapperScanner 扫描 basePackage 下的接口，对每个接口创建 MapperFactoryBean 的 BeanDefinition 并注册到 BeanDefinitionRegistry。MapperFactoryBean 是 FactoryBean，其 getObject 方法调用 sqlSession.getMapper(mapperInterface) 获取 MyBatis 生成的 Mapper 代理对象。@MapperScan 注解内部通过 @Import(MapperScannerRegistrar.class) 实现相同的逻辑 |
| 缺点 | 扫描时机在 BeanDefinition 注册阶段，此时 DataSource 可能尚未创建；扫描包路径写错导致 Mapper 不注册；多个 MapperScannerConfigurer 可能冲突 |

---

## 三、实战应用

### 3.1 SSM 整合完整配置

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 Java Config 方式的 SSM 整合完整配置，包含 Spring 配置、SpringMVC 配置、Web 初始化 |
| 能做什么 | Spring 配置管理 Service、DAO、事务、数据源、MyBatis；SpringMVC 配置管理 Controller、视图解析、静态资源；Web 初始化配置父子容器 |
| 怎么用 | SpringConfig 排除 Controller 扫描；SpringMvcConfig 只扫描 Controller；WebAppInitializer 继承 AbstractAnnotationConfigDispatcherServletInitializer |
| 原理和工作流程 | SpringConfig 通过 @ComponentScan 排除 Controller 注解，@EnableTransactionManagement 开启事务，@MapperScan 扫描 Mapper 接口，配 DataSource 和 SqlSessionFactoryBean。SpringMvcConfig 用 @EnableWebMvc 和 @ComponentScan 只扫描 Controller 包，配置资源处理器和消息转换器。WebAppInitializer 继承 AbstractAnnotationConfigDispatcherServletInitializer，重写 getRootConfigClasses 返回 SpringConfig 作为父容器配置，getServletConfigClasses 返回 SpringMvcConfig 作为子容器配置，getServletMappings 返回 "/" 映射 DispatcherServlet |
| 缺点 | Java Config 方式配置类多，类间依赖关系需理解；@Bean 方法间调用顺序敏感；多环境配置切换需额外处理 |

### 3.2 分层代码示例

| 维度 | 内容 |
|------|------|
| 是什么 | SSM 分层架构下 Controller、Service、Mapper 三层代码的典型写法 |
| 能做什么 | Controller 处理 HTTP 请求调用 Service；Service 管理事务编排业务逻辑；Mapper 定义数据库操作 |
| 怎么用 | Controller 用 @RestController + @Autowired 注入 Service；Service 用 @Service + @Transactional + @Autowired 注入 Mapper；Mapper 用接口定义 SQL 映射方法 |
| 原理和工作流程 | Controller 层只负责接收请求参数校验和调用 Service，不包含业务逻辑。Service 层是业务核心，@Transactional 声明事务边界，调用多个 Mapper 完成数据库操作，处理异常抛出业务异常。Mapper 层只定义接口，方法名对应 Mapper XML 中的 SQL 语句 ID，通过 MyBatis 生成代理对象执行 SQL。分层清晰后各层职责单一，测试时可按层 Mock |
| 缺点 | 简单 CRUD 场景分层过重增加代码量；Service 过薄退化为代理转发；DTO/VO 对象转换增加复杂度 |

### 3.3 整合问题排查清单

| 维度 | 内容 |
|------|------|
| 是什么 | SSM 整合出现问题时的系统化排查清单，覆盖数据源、Mapper 扫描、事务、包扫描隔离等 |
| 能做什么 | 按清单逐项排查数据源连接、Mapper 扫描配置、事务注解位置、包扫描隔离、Mapper XML 路径 |
| 怎么用 | 逐项检查：DataSource 配置 → @MapperScan 包路径 → @EnableTransactionManagement → 包扫描隔离 → @Transactional 位置 → Mapper XML 路径 |
| 原理和工作流程 | 排查顺序：1. 检查 DataSource 连接是否成功（URL、用户名、密码、驱动）。2. 检查 @MapperScan 扫描的包路径是否正确，Mapper 接口是否在包下。3. 检查 @EnableTransactionManagement 是否开启。4. 检查包扫描是否隔离：父容器排除 Controller，子容器只扫 Controller。5. 检查 @Transactional 是否在 Service 层方法上。6. 检查 Mapper XML 的 mapperLocations 路径是否匹配实际文件位置 |
| 缺点 | 排查项多需逐项对号入座；问题可能由多个原因叠加；清单未覆盖所有整合场景 |

---

## 四、常见面试题

### 1. SSM 整合的核心思路是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | 以 Spring 为粘合剂容器统一管理 Bean，SpringMVC 负责 Web 层，MyBatis 负责持久层，通过父子容器隔离 |
| 能做什么 | 表现层 SpringMVC 处理 HTTP 请求；业务层 Spring 管理事务和依赖注入；持久层 MyBatis 执行 SQL |
| 怎么用 | ContextLoaderListener 创建父容器管理 Service/DAO/事务；DispatcherServlet 创建子容器管理 Controller |
| 原理和工作流程 | Spring 作为核心容器通过 IoC 管理所有组件。SpringMVC 的 DispatcherServlet 创建子容器，ContextLoaderListener 创建父容器，形成父子容器关系。子容器可以访问父容器 Bean（Controller 注入 Service），父容器不能访问子容器。MyBatis 通过 SqlSessionFactoryBean 和 MapperScannerConfigurer 整合到 Spring 容器中，事务由 Spring 统一管理 |
| 缺点 | 整合配置复杂容易遗漏；父子容器关系抽象；配置错误排查困难 |

### 2. SqlSessionFactoryBean 的作用是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 整合 MyBatis 的核心工厂类，实现 FactoryBean 接口，用于创建 SqlSessionFactory |
| 能做什么 | 封装 MyBatis 配置：设置 DataSource、Mapper XML 位置、实体类别名、插件；产出 SqlSessionFactory 实例 |
| 怎么用 | `@Bean public SqlSessionFactoryBean sqlSessionFactory(DataSource ds) { factoryBean.setDataSource(ds); ... }` |
| 原理和工作流程 | SqlSessionFactoryBean 实现 FactoryBean 接口，其 getObject() 方法通过 SqlSessionFactoryBuilder.build() 创建 SqlSessionFactory。配置时设置 dataSource（必填）、mapperLocations（Mapper XML 路径）、configLocation（MyBatis 全局配置）、typeAliasesPackage（别名包）、plugins（如 PageHelper）。Spring 容器启动时调用 getObject() 获取 SqlSessionFactory 实例注册为 Bean |
| 缺点 | 配置项多容易遗漏；Mapper XML 路径通配符写错导致映射失败；多数据源配置复杂 |

### 3. MapperScannerConfigurer 的作用是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | 自动扫描指定包下 Mapper 接口，为每个接口创建 MapperFactoryBean 并注册为 Spring Bean |
| 能做什么 | 扫描包路径下接口；为每个 Mapper 接口生成代理对象；通过 SqlSession.getMapper() 获取代理 |
| 怎么用 | `@MapperScan("com.example.mapper")` |
| 原理和工作流程 | MapperScannerConfigurer 实现 BeanDefinitionRegistryPostProcessor，在 BeanDefinition 注册阶段扫描 basePackage 下接口，为每个接口创建 MapperFactoryBean 的 BeanDefinition。MapperFactoryBean 是 FactoryBean，getObject() 方法调用 sqlSession.getMapper(mapperInterface) 获取 MyBatis 生成的 Mapper 代理对象。@MapperScan 注解内部通过 @Import(MapperScannerRegistrar.class) 实现相同逻辑 |
| 缺点 | 扫描时机在 BeanDefinition 注册阶段，此时 DataSource 可能未创建；扫描包路径错误导致 Mapper 不注册 |

### 4. 父子容器的关系是什么？为什么要区分？

| 维度 | 内容 |
|------|------|
| 是什么 | 父容器管理非 Web 层 Bean，子容器管理 Web 层 Bean，子容器可访问父容器，父容器不能访问子容器 |
| 能做什么 | 隔离 Web 层和非 Web 层；子容器注入父容器 Service；避免 Controller 被父容器扫描导致事务失效 |
| 怎么用 | 父容器扫 Service/DAO 排除 Controller；子容器只扫 Controller |
| 原理和工作流程 | 父容器由 ContextLoaderListener 创建，管理 Service、DAO、事务管理器、数据源等。子容器由 DispatcherServlet 创建，管理 Controller、HandlerMapping、ViewResolver 等。子容器可以访问父容器 Bean（Controller 注入 Service），父容器不能访问子容器 Bean。访问优先级：子容器先查自身，找不到再到父容器查找。区分的原因：隔离 Web 层和非 Web 层，避免 Controller 被父容器扫描导致事务代理失效，同时子容器可以获取父容器 Service 注入 |
| 缺点 | 父子关系抽象难理解；包扫描隔离配置不当导致事务失效；两个容器配置分离增加维护成本 |

### 5. SSM 整合中事务不生效的常见原因？

| 维度 | 内容 |
|------|------|
| 是什么 | SSM 整合中 @Transactional 注解无效或事务不回滚的常见原因汇总 |
| 能做什么 | 识别配置遗漏、注解位置错误、包扫描冲突导致的事务失效|
| 怎么用 | 检查 @EnableTransactionManagement、@Transactional 位置、包扫描隔离、方法可见性 |
| 原理和工作流程 | 常见原因：① 忘记配置 @EnableTransactionManagement 或 <tx:annotation-driven/>，事务代理未开启。② @Transactional 放在 Controller 层，事务代理在 Service 层生效。③ 父容器和子容器包扫描未隔离，Controller 被父容器扫描导致事务代理失效。④ 方法非 public，Spring AOP 只代理 public 方法。⑤ 异常被 catch 未抛出，代理层检测不到异常。⑥ 同类方法内部调用不走代理 |
| 缺点 | 多个原因可能同时存在，排查需逐一验证；包扫描冲突问题隐蔽，启动不报错但功能异常 |

### 6. DAO 注入失败的排查思路？

| 维度 | 内容 |
|------|------|
| 是什么 | Mapper 接口无法注入 Spring 容器时 NoSuchBeanDefinitionException 的系统化排查方法 |
| 能做什么 | 检查 @MapperScan 配置、DataSource 连接、Mapper XML 路径、扫描范围 |
| 怎么用 | 逐项排查：@MapperScan → basePackage → DataSource → Mapper XML 路径 |
| 原理和工作流程 | 排查顺序：1. 检查 @MapperScan 注解是否配置在 Spring 配置类上，basePackage 路径是否正确。2. 检查 Mapper 接口是否在 basePackage 路径下。3. 检查 DataSource 配置是否正确，数据库连接是否可用。4. 检查 Mapper XML 文件路径是否匹配 mapperLocations 配置。5. 检查 Mapper 接口是否被父子容器重复扫描。6. 查看启动日志是否有 Mapper 注册相关的信息 |
| 缺点 | 排查步骤多需逐一检查；问题可能由多个原因叠加；日志信息不一定直观 |

### 7. ContextLoaderListener 和 DispatcherServlet 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 两种创建 Spring 容器的 Web 组件对比：ContextLoaderListener 是 Servlet 监听器，DispatcherServlet 是 Servlet |
| 能做什么 | ContextLoaderListener 创建父容器管理非 Web 层 Bean；DispatcherServlet 创建子容器管理 Web 层 Bean |
| 怎么用 | ContextLoaderListener 配置在 web.xml 监听器中；DispatcherServlet 配置在 servlet 中 |
| 原理和工作流程 | ContextLoaderListener 实现 ServletContextListener，在 Web 容器启动时创建 Root WebApplicationContext，加载 applicationContext.xml 管理 Service、DAO、事务等，存入 ServletContext。DispatcherServlet 继承 HttpServlet，init 方法中创建 Servlet WebApplicationContext，从 ServletContext 获取根容器为父容器，加载 springmvc-servlet.xml 管理 Controller、视图解析等。ContextLoaderListener 创建的容器先于 DispatcherServlet，作为父容器 |
| 缺点 | 两个组件分开配置增加维护成本；配置顺序错误导致启动失败；Servlet 3.0+ 可用代码配置替代 XML |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | SSM 整合中事务不生效、Mapper 注入失败、Bean 重复创建、DataSource 错误、Mapper XML 找不到、事务注解位置错误等高频问题汇总 |
| 能做什么 | 识别包扫描未隔离导致的事务失效；排查 Mapper 扫描配置错误；解决 Bean 重复创建；检查 DataSource 连接；确认 Mapper XML 路径；确保 @Transactional 在 Service 层 |
| 怎么用 | 父容器排除 Controller 扫描配置 excludeFilters；检查 @MapperScan 包路径；隔离包扫描范围；检查数据库连接参数；确认 mapperLocations 路径 |
| 原理和工作流程 | 事务不生效的核心原因是包扫描未隔离，Controller 被父容器扫描后事务代理链丢失。解决方法是父容器 @ComponentScan 配置 excludeFilters 排除 Controller 注解。Mapper 注入失败是因为 @MapperScan 未配置或 basePackage 路径错误。Bean 重复创建是因为两个容器扫描了同一包，需隔离扫描范围。DataSource 配置错误需检查 URL、用户名、密码、驱动。Mapper XML 找不到是因为 mapperLocations 路径与实际文件位置不匹配。@Transactional 在 Controller 层失效是因为 Controller 被父容器扫描时事务代理丢失，注解必须放在 Service 层 |
| 缺点 | 问题隐蔽不易发现；配置错误导致功能静默失效；排查需要理解完整整合链路；多个问题可能同时存在 |

---

> [返回原文](./03-MyBatis整合与配置.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)