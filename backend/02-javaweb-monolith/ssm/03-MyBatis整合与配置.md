# MyBatis 整合与配置

> 学习路线对应：SSM 单体架构 -- MyBatis 持久层整合
> 前置知识：MyBatis 基础使用、Spring IoC 容器、SpringMVC 基础
> 预计学习时间：1-2 天

## 一、核心概念

### 1.1 SSM 整合思路

SSM 整合是指将 Spring、SpringMVC、MyBatis 三个框架整合到一个项目中，形成完整的分层架构。

| 层次 | 框架 | 职责 |
|------|------|------|
| **表现层（Web）** | SpringMVC | 接收 HTTP 请求，参数校验，调用 Service，返回 JSON/View |
| **业务层（Service）** | Spring | 事务管理，业务逻辑编排，依赖注入 |
| **持久层（DAO）** | MyBatis | 与数据库交互，执行 SQL，返回实体对象 |

**整合核心思想：**
- Spring 作为"粘合剂"容器，统一管理所有 Bean
- SpringMVC 负责 Web 层，由 Spring 容器管理 Controller
- MyBatis 负责持久层，由 Spring 容器管理 Mapper 和 SqlSessionFactory
- 通过 Spring 事务管理统一控制事务

**分层优势：** 各层职责单一，降低耦合，便于测试和替换，DAO 层替换 MyBatis 为 JPA 不影响上层。

> **生活化类比：SSM 整合就像装修工程协作** —— SSM 整合中三个框架的分工与装修工程非常相似：Spring 是装修公司（统筹所有工人和材料，相当于容器管理 Bean）；SpringMVC 是前台接待和设计师（接待客户、出方案、对接客户需求，相当于 Web 层）；MyBatis 是泥瓦工和水电工（具体干活——和"水电煤"打交道即数据库），Spring 这个"装修公司"作为粘合剂统一调度。三层各司其职：前台不砌墙、泥瓦工不接客、装修公司不直接砌墙但负责调度。Spring 的"粘合剂"作用就体现在：把数据源、SqlSessionFactory、Mapper、Service、TransactionManager 这些"工人和材料"统一登记在册（IoC 容器），需要时按需调度。

> 📖 **参考链接**：
> - [MyBatis - 入门文档](https://mybatis.org/mybatis-3/zh_CN/getting-started.html) -- MyBatis 入门
> - [MyBatis - 配置 XML](https://mybatis.org/mybatis-3/zh_CN/configuration.html) -- MyBatis 全局配置
> - [MyBatis - Mapper XML 详解](https://mybatis.org/mybatis-3/zh_CN/sqlmap-xml.html) -- Mapper XML 文件
> - [MyBatis-Spring - 入门](https://mybatis.org/spring/zh_CN/getting-started.html) -- MyBatis-Spring 整合文档

---

### 1.2 Spring 整合 MyBatis

Spring 整合 MyBatis 的核心是将 MyBatis 的核心组件交给 Spring IoC 容器管理。

#### 核心组件

| 组件 | 作用 | 对应 Spring 整合类 |
|------|------|-------------------|
| **SqlSessionFactory** | 创建 SqlSession 的工厂 | `SqlSessionFactoryBean` |
| **SqlSession** | 执行 SQL 的会话 | 由 Spring 管理，注入到 DAO |
| **Mapper 接口** | MyBatis 映射接口 | `MapperScannerConfigurer` |
| **DataSource** | 数据库连接池 | `DataSource`（如 Druid、HikariCP） |

#### SqlSessionFactoryBean

`SqlSessionFactoryBean` 是 Spring 整合 MyBatis 的核心工厂类，用于创建 `SqlSessionFactory`。

```java
@Bean
public SqlSessionFactoryBean sqlSessionFactory(DataSource dataSource) {
    SqlSessionFactoryBean factoryBean = new SqlSessionFactoryBean();
    factoryBean.setDataSource(dataSource);
    // 配置 MyBatis 全局配置文件位置
    factoryBean.setConfigLocation(new ClassPathResource("mybatis-config.xml"));
    // 配置 Mapper XML 文件位置
    factoryBean.setMapperLocations(new PathMatchingResourcePatternResolver()
        .getResources("classpath:mapper/*.xml"));
    // 配置别名包
    factoryBean.setTypeAliasesPackage("com.example.entity");
    // 配置插件（如分页插件）
    factoryBean.setPlugins(new PageInterceptor());
    return factoryBean;
}
```

**关键属性：**
- `dataSource`：数据源，必须配置
- `configLocation`：MyBatis 全局配置文件路径
- `mapperLocations`：Mapper XML 文件路径，支持通配符
- `typeAliasesPackage`：实体类别名包扫描
- `plugins`：MyBatis 插件（如分页插件 PageHelper）

#### MapperScannerConfigurer

`MapperScannerConfigurer` 用于自动扫描指定包下的 Mapper 接口，生成代理对象并注册为 Spring Bean。

```java
@Bean
public MapperScannerConfigurer mapperScannerConfigurer() {
    MapperScannerConfigurer configurer = new MapperScannerConfigurer();
    // 指定 Mapper 接口所在包
    configurer.setBasePackage("com.example.mapper");
    // 指定 SqlSessionFactory Bean 名称（可选）
    // configurer.setSqlSessionFactoryBeanName("sqlSessionFactory");
    return configurer;
}
```

**或者使用 @MapperScan 注解简化：**
```java
@Configuration
@MapperScan("com.example.mapper")
public class MyBatisConfig {
    // 只需配置 SqlSessionFactory
}
```

---

### 1.3 Spring 整合 SpringMVC

Spring 整合 SpringMVC 的核心是让 SpringMVC 的 DispatcherServlet 使用自己的 WebApplicationContext，并与 Spring 根容器建立父子容器关系。

#### ContextLoaderListener

`ContextLoaderListener` 是 Servlet 规范提供的监听器，在 Web 应用启动时创建 Spring 根容器。

```xml
<!-- web.xml 配置 -->
<listener>
    <listener-class>org.springframework.web.context.ContextLoaderListener</listener-class>
</listener>

<!-- 指定 Spring 配置文件位置 -->
<context-param>
    <param-name>contextConfigLocation</param-name>
    <param-value>classpath:spring/applicationContext.xml</param-value>
</context-param>
```

`ContextLoaderListener` 创建的容器称为**根容器（Root WebApplicationContext）**，负责管理 Service、DAO、事务等非 Web 层的 Bean。

#### DispatcherServlet 配置

```xml
<!-- web.xml 配置 -->
<servlet>
    <servlet-name>dispatcher</servlet-name>
    <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
    <init-param>
        <param-name>contextConfigLocation</param-name>
        <param-value>classpath:spring/springmvc-servlet.xml</param-value>
    </init-param>
    <load-on-startup>1</load-on-startup>
</servlet>
<servlet-mapping>
    <servlet-name>dispatcher</servlet-name>
    <url-pattern>/</url-pattern>
</servlet-mapping>
```

DispatcherServlet 创建的容器称为**子容器（Servlet WebApplicationContext）**，负责管理 Controller、HandlerMapping、ViewResolver 等 Web 层 Bean。

---

### 1.4 父子容器关系

Spring 容器和 SpringMVC 容器形成了父子容器关系：

```
Root WebApplicationContext（父容器）
├── 管理：Service、DAO、事务管理器、数据源等
├── 创建者：ContextLoaderListener
└── 配置文件：applicationContext.xml 或 spring.xml

Servlet WebApplicationContext（子容器）
├── 管理：Controller、HandlerMapping、ViewResolver 等
├── 创建者：DispatcherServlet
├── 配置文件：springmvc-servlet.xml
└── 可以访问父容器中的 Bean
```

**核心规则：**
- 子容器可以访问父容器中的 Bean（Controller 可以注入 Service）
- 父容器不能访问子容器中的 Bean（Service 不能注入 Controller）
- 访问优先级：子容器优先查找自己的 Bean，找不到再到父容器找

**包扫描隔离：**
- 父容器扫描：Service、DAO、配置类，排除 Controller
- 子容器扫描：Controller，排除 Service 和 DAO

> **生活化类比：父子容器就像集团总部与子公司** —— 父容器相当于集团总部（管理 Service、DAO、事务等"公共职能"如财务、法务），子容器相当于子公司 SpringMVC（管理 Controller 等"业务部门"如市场部、销售部）。子公司的市场部（Controller）可以调用总部的财务部（Service），但总部的财务部不能反过来指挥子公司的市场部（父子访问是单向的）。包扫描隔离就是明确"谁归总部管、谁归子公司管"——避免市场部员工被总部错误地纳入编制（Controller 被父容器扫描），导致子公司这边没找到这个员工，所有"子公司专属福利"（AOP 事务代理）都没给到。

> 📖 **参考链接**：
> - [Spring Framework - Context Hierarchy](https://docs.spring.io/spring-framework/reference/core/beans/context-introduction.html#context-functionality-hierarchy) -- 父子容器层次
> - [MyBatis-Spring - SqlSessionFactoryBean](https://mybatis.org/spring/zh_CN/factorybean.html) -- SqlSessionFactoryBean 文档

```xml
<!-- 父容器：排除 Controller -->
<context:component-scan base-package="com.example">
    <context:exclude-filter type="annotation" 
        expression="org.springframework.stereotype.Controller"/>
</context:component-scan>

<!-- 子容器：只扫描 Controller -->
<context:component-scan base-package="com.example" use-default-filters="false">
    <context:include-filter type="annotation" 
        expression="org.springframework.stereotype.Controller"/>
</context:component-scan>
```

---

### 1.5 常见整合问题

SSM 整合过程中常见的问题及排查方法：

#### 问题一：事务不生效

| 现象 | 可能原因 | 解决方案 |
|------|---------|---------|
| @Transactional 注解不生效 | 没有配置事务管理器 | 配置 `DataSourceTransactionManager` |
| 事务不回滚 | 注解在 Controller 层 | @Transactional 应放在 Service 层 |
| 事务不回滚 | 因为父容器扫描了 Controller 导致事务代理失效 | 确保父子容器包扫描隔离 |

**排查步骤：**
1. 检查是否配置了 `DataSourceTransactionManager` Bean
2. 检查是否开启了 `@EnableTransactionManagement` 或 `<tx:annotation-driven/>`
3. 检查 `@Transactional` 注解是否在 Service 层而非 Controller 层
4. 检查包扫描是否正确隔离，避免 Controller 被父容器扫描

#### 问题二：DAO 注入失败

| 现象 | 可能原因 | 解决方案 |
|------|---------|---------|
| Mapper 接口无法注入 | 没有配置 MapperScannerConfigurer 或 @MapperScan | 配置 Mapper 扫描 |
| 注入时报 NoSuchBeanDefinitionException | Mapper 接口包路径扫描不正确 | 检查 basePackage 配置 |
| 注入时报类型不匹配 | Mapper 接口被父容器和子容器同时扫描 | 统一在父容器中扫描 Mapper |
| SqlSessionFactory 为 null | DataSource 配置缺失或错误 | 检查 DataSource 配置 |

**排查步骤：**
1. 确认 `@MapperScan` 注解配置在 Spring 配置类上
2. 确认 `basePackage` 路径正确，包含 Mapper 接口
3. 确认 DataSource 配置正确，数据库连接可用
4. 确认 Mapper XML 文件路径配置正确

#### 问题三：父子容器扫描冲突

**典型症状：** 事务不生效、AOP 不生效、Bean 被创建两次。

**根本原因：** 父容器和子容器都对同一个包进行了扫描，导致部分 Bean 被两个容器重复创建。当 Controller 被父容器扫描到时，由于不在子容器中，可能导致 AOP 事务失效。

**解决方案：**
1. 严格隔离包扫描：父容器扫 Service/DAO，子容器只扫 Controller
2. 使用 `@MapperScan` 明确指定 Mapper 包路径
3. 不要在父容器和子容器中重复扫描同一个包

---

## 二、底层原理

### 2.1 ContextLoaderListener 初始化流程

ContextLoaderListener 在 Web 容器启动时的初始化流程：

```
1. Web 容器启动
   Tomcat 等容器启动，加载 web.xml 或 WebApplicationInitializer

2. 触发 ContextLoaderListener.contextInitialized()
   创建 Root WebApplicationContext

3. 读取 contextConfigLocation 配置
   加载 Spring 配置文件（applicationContext.xml）

4. 初始化 Root WebApplicationContext
   扫描 Bean，创建 Service、DAO、事务管理器等

5. 将 Root WebApplicationContext 存入 ServletContext
   供 DispatcherServlet 后续获取父容器引用
```

---

### 2.2 DispatcherServlet 初始化流程

DispatcherServlet 作为 Servlet 被容器初始化：

```
1. DispatcherServlet.init()
   创建 Servlet WebApplicationContext 子容器

2. 从 ServletContext 获取 Root WebApplicationContext 作为父容器
   建立父子容器关系

3. 加载 DispatcherServlet 的配置文件
   通常为 springmvc-servlet.xml

4. 扫描 Controller 等 Web 层 Bean
   创建 HandlerMapping、HandlerAdapter 等

5. 初始化九大组件
   调用 initStrategies() 初始化 HandlerMapping、HandlerAdapter 等
```

---

### 2.3 MapperScannerConfigurer 原理

`MapperScannerConfigurer` 实现了 `BeanDefinitionRegistryPostProcessor` 接口，在 Spring 容器启动时执行：

```
1. 执行 postProcessBeanDefinitionRegistry()
   在 BeanDefinition 注册阶段执行

2. 扫描指定包下的 Mapper 接口
   使用 ClassPathMapperScanner 扫描包路径

3. 为每个 Mapper 接口创建 MapperFactoryBean 的 BeanDefinition
   MapperFactoryBean 是 FactoryBean，负责生成 Mapper 代理对象

4. 注册到 BeanDefinitionRegistry
   后续通过 getBean() 获取 Mapper 代理对象
```

**MapperFactoryBean 原理：** 实现了 `FactoryBean` 接口，其 `getObject()` 方法通过 `SqlSession.getMapper(Class)` 获取 MyBatis 生成的 Mapper 代理对象，并返回给 Spring 容器。

> 📖 **参考链接**：
> - [MyBatis-Spring - MapperScannerConfigurer](https://mybatis.org/spring/zh_CN/mappers.html) -- MapperScannerConfigurer 文档
> - [MyBatis-Spring - MapperFactoryBean](https://mybatis.org/spring/zh_CN/factorybean.html) -- MapperFactoryBean 工厂机制

---

## 三、实战应用

### 3.1 SSM 整合完整配置

#### Spring 配置（spring.xml）

```java
@Configuration
@ComponentScan(basePackages = "com.example",
    excludeFilters = @ComponentScan.Filter(
        type = FilterType.ANNOTATION,
        classes = {Controller.class, RestController.class}))
@EnableTransactionManagement
@MapperScan("com.example.mapper")
public class SpringConfig {

    @Bean
    public DataSource dataSource() {
        DruidDataSource dataSource = new DruidDataSource();
        dataSource.setUrl("jdbc:mysql://localhost:3306/test");
        dataSource.setUsername("root");
        dataSource.setPassword("root");
        dataSource.setDriverClassName("com.mysql.cj.jdbc.Driver");
        return dataSource;
    }

    @Bean
    public SqlSessionFactoryBean sqlSessionFactory(DataSource dataSource) throws Exception {
        SqlSessionFactoryBean factoryBean = new SqlSessionFactoryBean();
        factoryBean.setDataSource(dataSource);
        factoryBean.setMapperLocations(
            new PathMatchingResourcePatternResolver()
                .getResources("classpath:mapper/*.xml"));
        return factoryBean;
    }

    @Bean
    public PlatformTransactionManager transactionManager(DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

#### SpringMVC 配置（springmvc.xml）

```java
@Configuration
@EnableWebMvc
@ComponentScan(basePackages = "com.example.controller")
public class SpringMvcConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/static/**")
                .addResourceLocations("/static/");
    }

    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        // 配置 Jackson JSON 转换器
        MappingJackson2HttpMessageConverter converter = new MappingJackson2HttpMessageConverter();
        converter.setObjectMapper(new ObjectMapper());
        converters.add(converter);
    }
}
```

#### Web 初始化配置

```java
public class WebAppInitializer extends AbstractAnnotationConfigDispatcherServletInitializer {

    @Override
    protected Class<?>[] getRootConfigClasses() {
        return new Class<?>[]{SpringConfig.class}; // 父容器配置
    }

    @Override
    protected Class<?>[] getServletConfigClasses() {
        return new Class<?>[]{SpringMvcConfig.class}; // 子容器配置
    }

    @Override
    protected String[] getServletMappings() {
        return new String[]{"/"};
    }
}
```

### 3.2 分层代码示例

```java
// Controller 层
@RestController
@RequestMapping("/api/users")
public class UserController {
    @Autowired
    private UserService userService;

    @GetMapping("/{id}")
    public Result<UserVO> getUser(@PathVariable Long id) {
        return Result.success(userService.getUserById(id));
    }
}

// Service 层
@Service
@Transactional(rollbackFor = Exception.class)
public class UserService {
    @Autowired
    private UserMapper userMapper;

    public UserVO getUserById(Long id) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND);
        }
        return convertToVO(user);
    }
}

// Mapper 接口
public interface UserMapper {
    User selectById(Long id);
    int insert(User user);
    int update(User user);
    int deleteById(Long id);
}
```

### 3.3 整合问题排查清单

| 排查项 | 检查内容 | 命令/操作 |
|-------|---------|---------|
| 数据源配置 | 数据库连接 URL、用户名、密码 | 启动时可查看 DataSource 连接日志 |
| Mapper 扫描 | @MapperScan 包路径是否正确 | 检查 Mapper 接口是否在指定包下 |
| 事务配置 | @EnableTransactionManagement 是否开启 | 检查配置类上是否有该注解 |
| 包扫描隔离 | Controller 是否被父容器扫描 | 检查 excludeFilters 配置 |
| 事务注解位置 | @Transactional 是否在 Service 层 | 确认注解不在 Controller 层 |
| Mapper XML 路径 | mapperLocations 配置是否正确 | 检查 XML 文件路径是否匹配配置 |

---

## 四、常见面试题

### 1. SSM 整合的核心思路是什么？

SSM 整合核心思路：以 Spring 作为粘合剂容器，统一管理所有 Bean。SpringMVC 负责 Web 层（Controller），MyBatis 负责持久层（Mapper），Spring 负责业务层（Service）和事务管理。通过 ContextLoaderListener 创建父容器管理 Service/DAO/事务，通过 DispatcherServlet 创建子容器管理 Controller，形成父子容器关系。

### 2. SqlSessionFactoryBean 的作用是什么？

`SqlSessionFactoryBean` 是 Spring 整合 MyBatis 的核心工厂类，实现了 `FactoryBean` 接口。它负责创建 `SqlSessionFactory`，封装了 MyBatis 的配置逻辑：设置 DataSource、配置 Mapper XML 位置、配置实体类别名、注册插件等。最终通过 `getObject()` 方法返回 `SqlSessionFactory` 实例注册到 Spring 容器。

### 3. MapperScannerConfigurer 的作用是什么？

`MapperScannerConfigurer` 用于自动扫描指定包下的 Mapper 接口，将其注册为 Spring Bean。它实现了 `BeanDefinitionRegistryPostProcessor`，在 Bean 定义注册阶段执行，扫描包路径下的接口，为每个 Mapper 接口创建 `MapperFactoryBean` 的 BeanDefinition，最终通过 `SqlSession.getMapper()` 生成代理对象。

### 4. 父子容器的关系是什么？为什么要区分？

父容器（Root WebApplicationContext）由 ContextLoaderListener 创建，管理 Service、DAO、事务等。子容器（Servlet WebApplicationContext）由 DispatcherServlet 创建，管理 Controller、视图解析等。子容器可以访问父容器 Bean，父容器不能访问子容器 Bean。区分的原因：隔离 Web 层和非 Web 层，避免 Controller 被父容器扫描导致事务失效；子容器可以获取父容器的 Service 注入。

### 5. SSM 整合中事务不生效的常见原因？

① 忘记配置 `@EnableTransactionManagement` 或 `<tx:annotation-driven/>`；② `@Transactional` 注解放在了 Controller 层而非 Service 层；③ 父容器和子容器包扫描没有隔离，Controller 被父容器扫描，导致事务代理失效；④ 方法非 public 或不走代理（同类调用）；⑤ 异常被 catch 未抛出。

### 6. DAO 注入失败的排查思路？

① 检查 `@MapperScan` 注解是否配置且 basePackage 路径正确；② 检查 Mapper 接口是否在指定包路径下；③ 检查 DataSource 配置是否正确，数据库连接是否可用；④ 检查 Mapper XML 文件路径是否匹配配置；⑤ 检查 Mapper 接口是否被两个容器重复扫描。

### 7. ContextLoaderListener 和 DispatcherServlet 的区别？

`ContextLoaderListener` 是 Servlet 规范监听器，在 Web 应用启动时创建 Spring 根容器。`DispatcherServlet` 是 SpringMVC 前端控制器，初始化时创建自己的子容器。ContextLoaderListener 创建的容器先于 DispatcherServlet，作为父容器。ContextLoaderListener 管理非 Web 层 Bean，DispatcherServlet 管理 Web 层 Bean。

> 📖 **参考链接**：
> - [Spring Framework - ContextLoaderListener](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-servlet/context-hierarchy.html) -- ContextLoaderListener 文档
> - [MyBatis-Spring - Sample Application](https://mybatis.org/spring/zh_CN/sample.html) -- SSM 整合示例

---

## 五、避坑指南

| 常见问题 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 事务不生效 | 数据库操作未回滚 | 包扫描未隔离，Controller 被父容器扫描，事务代理失效 | 父容器排除 Controller 扫描，配置 `excludeFilters` |
| Mapper 注入失败 | NoSuchBeanDefinitionException | @MapperScan 未配置或 basePackage 路径错误 | 检查 @MapperScan 包路径，确保 Mapper 接口在指定包下 |
| Bean 重复创建 | 启动时有重复 Bean 警告 | 父容器和子容器都扫描了同一个包 | 隔离包扫描，如父容器扫 `com.example` 排除 Controller，子容器只扫 `com.example.controller` |
| DataSource 配置错误 | 启动失败，连接数据库报错 | 数据库 URL、用户名、密码配置错误 | 检查配置文件，确认数据库连接参数 |
| Mapper XML 找不到 | 报 Invalid bound statement | mapperLocations 路径配置错误 | 检查 `classpath:mapper/*.xml` 路径，确保 XML 在 resources/mapper 下 |
| 事务注解在 Controller 失效 | Service 层事务不生效 | @Transactional 放在 Controller 层，Controller 被父容器扫描时事务代理丢失 | @Transactional 必须放在 Service 层，且 Controller 不被父容器扫描 |

## 本章学习自检

完成本章学习后，你应该能够：
- [ ] 描述 SSM 整合的三层架构和整合思路
- [ ] 理解 SqlSessionFactoryBean、MapperScannerConfigurer 的作用
- [ ] 解释 ContextLoaderListener 和 DispatcherServlet 的父子容器关系
- [ ] 掌握包扫描隔离的配置方法
- [ ] 识别并解决事务不生效、DAO 注入失败等常见整合问题
- [ ] 手写 SSM 整合的完整配置类

---

> **学习导航**：
> - 返回 [02-javaweb-monolith 模块](../../README.md)
> - 上一篇：[02-SpringMVC执行流程](./02-SpringMVC执行流程.md)
> - 下一篇：[SSM整合笔面试题集](./SSM整合笔面试题集.md)