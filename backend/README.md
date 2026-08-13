# Java 后端学习路线 -- 笔面试资料库

> **来源**：基于 [DeepSeek 分享](https://chat.deepseek.com/share/e1m9lmjj7qlfnntjmh) 的 8 周 Java 后端速成学习路线，面向有前端/Python/Node.js 基础的学习者。
> **定位**：深入详细的笔面试学习资料，覆盖原理深度、实战应用和面试题库三大维度。

---

## 学习路线总览

资料库按 **4 大核心模块 + 1 个扩展模块** 组织，共 5 个一级目录，覆盖从 Java 基础到分布式微服务、Python AI Agent 的完整后端技术栈。

| 序号 | 模块 | 包含子模块 | 文件数 | 资料目录 |
|:----:|------|-----------|:------:|----------|
| 1 | Java 基础 | java-core / jvm-juc / mysql-jdbc | 20 | [01-java-basics](./01-java-basics/) |
| 2 | JavaWeb 单体架构 | maven / javaweb-servlet / ssm / spring-boot / mybatis / linux / docker-k8s | 28 | [02-javaweb-monolith](./02-javaweb-monolith/) |
| 3 | 分布式微服务 | redis / mysql-advanced / nginx / spring-cloud / zookeeper / mq / elasticsearch / clickhouse / git | 32 | [03-distributed-microservices](./03-distributed-microservices/) |
| 4 | Python AI Agent | python-core / langchain-rag / llm-fine-tuning | 8 | [04-python-aiagent](./04-python-aiagent/) |
| 扩展 | 实战项目 | project | 1 | [extensions](./extensions/) |

---

## 使用指南

### 按学习阶段使用

- **阶段一：Java 基础** -- 先通读 `01-java-basics` 中的 java-core 和 jvm-juc 原理文件，再刷笔面试题集；随后学习 mysql-jdbc 建立数据库基础。
- **阶段二：JavaWeb 单体架构** -- 按 maven -> javaweb-servlet -> ssm -> spring-boot -> mybatis -> linux -> docker-k8s 顺序推进，从项目管理到部署上线，构建完整的单体应用能力。
- **阶段三：分布式微服务** -- 从 redis 缓存和 mysql-advanced 深入优化开始，逐步扩展到 nginx 反向代理、spring-cloud 微服务全家桶、zookeeper 协调服务、mq 消息队列、elasticsearch 搜索引擎、clickhouse 列式数据库和 git 版本控制。
- **阶段四：Python AI Agent** -- python-core 速通后，深入 langchain-rag 智能体开发和 llm-fine-tuning 大模型微调。
- **考前冲刺** -- 重点刷各模块的笔面试题集，结合 `extensions/project` 中的实战项目理解综合场景。

### 文件结构说明

每个子模块目录包含两类文件：

- **原理文件**（`01-xxx.md`、`02-xxx.md`）：深入讲解核心概念、底层原理、实战应用，附常见面试题
- **笔面试题集**（`xxx笔面试题集.md`）：选择题 + 简答题 + 编程/场景设计题，全部附完整解析

### 相关知识库

本资料库与项目中的以下深度资料互补：

- [ljit-exam-deep-dive.md](../ljit-exam-deep-dive.md) — 完整版深度复习手册（20156 行）
- [ljit-exam-newtech.md](../ljit-exam-newtech.md) — 计算机新型技术考点
- [ljit-exam-foundation.md](../ljit-exam-foundation.md) — 计算机基础综合（含信息安全管理）

---

## 文件索引

### 01-java-basics — Java 基础（20 文件）

#### java-core（13 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Java语言概述.md](./01-java-basics/java-core/01-Java语言概述.md) | Java发展历史、JDK安装配置、HelloWorld、JVM简介 | 原理 |
| [02-变量与运算符.md](./01-java-basics/java-core/02-变量与运算符.md) | 关键字标识符、8种基本类型、类型转换、运算符 | 原理 |
| [03-流程控制语句.md](./01-java-basics/java-core/03-流程控制语句.md) | if-else、switch-case、循环结构、break/continue、Scanner | 原理 |
| [04-数组.md](./01-java-basics/java-core/04-数组.md) | 一维二维数组、内存解析、排序查找算法、Arrays工具类 | 原理 |
| [05-面向对象基础.md](./01-java-basics/java-core/05-面向对象基础.md) | 类与对象、封装继承多态、接口、内部类、枚举注解包装类 | 原理 |
| [06-异常处理.md](./01-java-basics/java-core/06-异常处理.md) | 异常体系、try-catch-finally、throws/throw、自定义异常 | 原理 |
| [07-常用类与基础API.md](./01-java-basics/java-core/07-常用类与基础API.md) | String、StringBuilder、日期时间API、BigDecimal、Comparator | 原理 |
| [08-面向对象与集合框架.md](./01-java-basics/java-core/08-面向对象与集合框架.md) | HashMap/ConcurrentHashMap源码、ArrayList/LinkedList、集合框架 | 原理 |
| [09-泛型.md](./01-java-basics/java-core/09-泛型.md) | 泛型类/方法、通配符、PECS原则、类型擦除 | 原理 |
| [10-IO流.md](./01-java-basics/java-core/10-IO流.md) | File类、字节流/字符流、缓冲流、对象流、序列化、NIO | 原理 |
| [11-网络编程.md](./01-java-basics/java-core/11-网络编程.md) | TCP/UDP、Socket编程、URL编程、三次握手四次挥手 | 原理 |
| [12-反射机制.md](./01-java-basics/java-core/12-反射机制.md) | Class类、Constructor/Method/Field、动态代理、类加载器 | 原理 |
| [18-正则表达式.md](./01-java-basics/java-core/18-正则表达式.md) | Pattern/Matcher、正则语法、零宽断言、常见模式、回溯与ReDoS | 原理 |

#### jvm-juc（5 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [13-多线程与并发编程.md](./01-java-basics/jvm-juc/13-多线程与并发编程.md) | 线程池、synchronized/AQS、volatile、CAS、ThreadLocal | 原理 |
| [14-JVM原理与调优.md](./01-java-basics/jvm-juc/14-JVM原理与调优.md) | 内存模型、GC算法、类加载、JVM参数调优、OOM排查 | 原理 |
| [15-JDK8-17新特性.md](./01-java-basics/jvm-juc/15-JDK8-17新特性.md) | Lambda、Stream API、Optional、var、记录类、密封类 | 原理 |
| [16-设计模式.md](./01-java-basics/jvm-juc/16-设计模式.md) | 单例/工厂/策略/代理/模板方法、Spring设计模式应用 | 原理 |
| [17-Java核心笔面试题集.md](./01-java-basics/jvm-juc/17-Java核心笔面试题集.md) | 选择题 30 + 简答 15 + 编程 8 | 题库 |

#### mysql-jdbc（2 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-MySQL基础与SQL核心.md](./01-java-basics/mysql-jdbc/01-MySQL基础与SQL核心.md) | MySQL安装配置、数据类型、DDL/DML/DQL/DCL、多表JOIN、子查询、视图 | 原理 |
| [02-JDBC核心原理.md](./01-java-basics/mysql-jdbc/02-JDBC核心原理.md) | DriverManager/Connection/PreparedStatement、连接池(HikariCP/Druid)、事务管理 | 原理 |

---

### 02-javaweb-monolith — JavaWeb 单体架构（28 文件）

#### maven（3 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Maven核心原理与依赖管理.md](./02-javaweb-monolith/maven/01-Maven核心原理与依赖管理.md) | POM结构、坐标体系、依赖管理、传递依赖、生命周期、聚合与继承 | 原理 |
| [02-Maven私服与实战配置.md](./02-javaweb-monolith/maven/02-Maven私服与实战配置.md) | settings.xml配置、镜像源、Nexus私服搭建、发布配置、多环境Profile | 原理 |
| [03-Maven笔面试题集.md](./02-javaweb-monolith/maven/03-Maven笔面试题集.md) | 选择题 10 + 简答 5 | 题库 |

#### javaweb-servlet（4 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-JavaWeb核心与HTTP协议.md](./02-javaweb-monolith/javaweb-servlet/01-JavaWeb核心与HTTP协议.md) | Web开发概念、HTTP协议细节、请求响应模型、Cookie/Session机制 | 原理 |
| [02-Servlet与Tomcat底层.md](./02-javaweb-monolith/javaweb-servlet/02-Servlet与Tomcat底层.md) | Servlet接口体系、生命周期、Tomcat架构、连接器与容器 | 原理 |
| [03-Request与Response&Filter监听器.md](./02-javaweb-monolith/javaweb-servlet/03-Request与Response&Filter监听器.md) | Filter过滤器链、Listener监听器、请求封装与响应处理 | 原理 |
| [JavaWeb笔面试题集.md](./02-javaweb-monolith/javaweb-servlet/JavaWeb笔面试题集.md) | 选择题 + 简答 + 场景题 | 题库 |

#### ssm（4 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Spring核心与IoC原理.md](./02-javaweb-monolith/ssm/01-Spring核心与IoC原理.md) | Spring框架概述、IoC容器、Bean生命周期、依赖注入方式 | 原理 |
| [02-SpringMVC执行流程.md](./02-javaweb-monolith/ssm/02-SpringMVC执行流程.md) | MVC设计模式、DispatcherServlet、HandlerMapping、视图解析 | 原理 |
| [03-MyBatis整合与配置.md](./02-javaweb-monolith/ssm/03-MyBatis整合与配置.md) | SqlSessionFactory、Mapper代理、Spring整合MyBatis、事务管理 | 原理 |
| [SSM整合笔面试题集.md](./02-javaweb-monolith/ssm/SSM整合笔面试题集.md) | 选择题 + 简答 + 场景题 | 题库 |

#### spring-boot（8 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Spring-IoC与AOP深度.md](./02-javaweb-monolith/spring-boot/01-Spring-IoC与AOP深度.md) | IoC 容器、Bean 生命周期、依赖注入、AOP 代理原理 | 原理 |
| [02-Spring-Boot自动配置原理.md](./02-javaweb-monolith/spring-boot/02-Spring-Boot自动配置原理.md) | @SpringBootApplication、Starter 机制、条件注解 | 原理 |
| [03-SpringMVC与RESTful设计.md](./02-javaweb-monolith/spring-boot/03-SpringMVC与RESTful设计.md) | DispatcherServlet、拦截器、统一异常处理、RESTful 规范 | 原理 |
| [04-登录认证与安全.md](./02-javaweb-monolith/spring-boot/04-登录认证与安全.md) | Session/JWT 认证、Spring Security、OAuth2、CSRF/XSS/SQL 注入防御 | 原理 |
| [05-Spring-Boot笔面试题集.md](./02-javaweb-monolith/spring-boot/05-Spring-Boot笔面试题集.md) | 选择题 15 + 简答 10 + 编程 3 + 场景设计 2 | 题库 |
| [06-Web核心与Servlet基础.md](./02-javaweb-monolith/spring-boot/06-Web核心与Servlet基础.md) | HTTP协议、Servlet生命周期、Tomcat架构、Filter/Listener | 原理 |
| [07-日志整合与监控.md](./02-javaweb-monolith/spring-boot/07-日志整合与监控.md) | Logback配置、日志级别、Actuator端点、Prometheus集成 | 原理 |
| [08-SpringBoot部署与运维.md](./02-javaweb-monolith/spring-boot/08-SpringBoot部署与运维.md) | jar打包、Docker部署、外部化配置、Profile隔离、热部署 | 原理 |

#### mybatis（3 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [03-MyBatis原生框架.md](./02-javaweb-monolith/mybatis/03-MyBatis原生框架.md) | SqlSession核心API、动态SQL、一二级缓存、注解开发、逆向工程 | 原理 |
| [04-Spring-Data-JPA深度.md](./02-javaweb-monolith/mybatis/04-Spring-Data-JPA深度.md) | Entity 映射、JPQL、N+1 问题、事务管理 | 原理 |
| [05-MyBatis-Plus实战.md](./02-javaweb-monolith/mybatis/05-MyBatis-Plus实战.md) | BaseMapper、分页插件、条件构造器、代码生成器 | 原理 |

#### linux（3 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Linux核心命令与Shell脚本.md](./02-javaweb-monolith/linux/01-Linux核心命令与Shell脚本.md) | 发行版选择、FHS文件结构、文件操作、管道重定向、文本三剑客、Shell脚本 | 原理 |
| [02-Linux系统管理与服务部署.md](./02-javaweb-monolith/linux/02-Linux系统管理与服务部署.md) | 用户权限、进程管理、网络管理、JDK/MySQL/Redis服务部署、系统监控 | 原理 |
| [03-Linux笔面试题集.md](./02-javaweb-monolith/linux/03-Linux笔面试题集.md) | 选择题 15 + 简答 8 + 场景题 2 | 题库 |

#### docker-k8s（3 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Docker核心原理.md](./02-javaweb-monolith/docker-k8s/01-Docker核心原理.md) | 镜像/容器/仓库、Dockerfile 最佳实践、docker-compose | 原理 |
| [02-Kubernetes核心概念.md](./02-javaweb-monolith/docker-k8s/02-Kubernetes核心概念.md) | Pod/Deployment/Service/Ingress/ConfigMap、调度策略 | 原理 |
| [03-容器与K8s笔面试题集.md](./02-javaweb-monolith/docker-k8s/03-容器与K8s笔面试题集.md) | 选择题 15 + 简答 8 | 题库 |

---

### 03-distributed-microservices — 分布式微服务（32 文件）

#### redis（3 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Redis核心数据结构与底层原理.md](./03-distributed-microservices/redis/01-Redis核心数据结构与底层原理.md) | SDS、Hash、List、ZSet/Skiplist、Bitmap/HyperLogLog/GEO | 原理 |
| [02-Redis高级特性与实战.md](./03-distributed-microservices/redis/02-Redis高级特性与实战.md) | 持久化、主从/哨兵/集群、缓存策略、内存淘汰、分布式锁 | 原理 |
| [03-Redis笔面试题集.md](./03-distributed-microservices/redis/03-Redis笔面试题集.md) | 选择题 20 + 简答 10 + 场景设计 5 | 题库 |

#### mysql-advanced（2 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [06-MySQL深度优化.md](./03-distributed-microservices/mysql-advanced/06-MySQL深度优化.md) | InnoDB 引擎、B+ 树索引、SQL 优化、分库分表 | 原理 |
| [07-数据库笔面试题集.md](./03-distributed-microservices/mysql-advanced/07-数据库笔面试题集.md) | 选择题 20 + 简答 10 + SQL 题 10 | 题库 |

#### nginx（3 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Nginx反向代理与负载均衡.md](./03-distributed-microservices/nginx/01-Nginx反向代理与负载均衡.md) | Master-Worker架构、配置结构、location匹配、反向代理、六种负载均衡算法 | 原理 |
| [02-Nginx性能优化与安全配置.md](./03-distributed-microservices/nginx/02-Nginx性能优化与安全配置.md) | 动静分离、sendfile零拷贝、gzip压缩、HTTPS配置、限流、CORS | 原理 |
| [03-Nginx笔面试题集.md](./03-distributed-microservices/nginx/03-Nginx笔面试题集.md) | 选择题 15 + 简答 8 + 场景题 2 | 题库 |

#### spring-cloud（7 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Spring-Cloud-Alibaba深度.md](./03-distributed-microservices/spring-cloud/01-Spring-Cloud-Alibaba深度.md) | 微服务架构演进、Spring Cloud 组件全景 | 原理 |
| [02-Nacos服务注册与配置中心.md](./03-distributed-microservices/spring-cloud/02-Nacos服务注册与配置中心.md) | AP/CP 模式、注册中心原理、配置中心动态刷新 | 原理 |
| [03-Gateway网关与负载均衡.md](./03-distributed-microservices/spring-cloud/03-Gateway网关与负载均衡.md) | 路由断言工厂、过滤器链、限流、Sentinel 熔断降级 | 原理 |
| [04-分布式事务与Seata.md](./03-distributed-microservices/spring-cloud/04-分布式事务与Seata.md) | AT/TCC/Saga 模式、Seata TC/TM/RM 架构、undo_log | 原理 |
| [05-微服务笔面试题集.md](./03-distributed-microservices/spring-cloud/05-微服务笔面试题集.md) | 选择题 20 + 简答 10 + 场景设计 5 | 题库 |
| [06-OpenFeign声明式调用.md](./03-distributed-microservices/spring-cloud/06-OpenFeign声明式调用.md) | 动态代理机制、超时重试、日志级别、拦截器、fallback降级 | 原理 |
| [07-链路追踪与可观测性.md](./03-distributed-microservices/spring-cloud/07-链路追踪与可观测性.md) | Trace/Span模型、SkyWalking/Zipkin原理、采样策略、日志关联 | 原理 |

#### zookeeper（3 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Zookeeper核心原理.md](./03-distributed-microservices/zookeeper/01-Zookeeper核心原理.md) | 数据模型ZNode、Watcher机制、ZAB协议、Leader选举、会话管理 | 原理 |
| [02-Zookeeper集群与应用场景.md](./03-distributed-microservices/zookeeper/02-Zookeeper集群与应用场景.md) | 集群部署配置、分布式锁、服务注册发现、配置中心、选举 | 原理 |
| [Zookeeper笔面试题集.md](./03-distributed-microservices/zookeeper/Zookeeper笔面试题集.md) | 选择题 + 简答 + 场景题 | 题库 |

#### mq（6 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [kafka/01-Kafka核心原理.md](./03-distributed-microservices/mq/kafka/01-Kafka核心原理.md) | Topic/Partition、ISR 机制、高吞吐原理、Exactly Once | 原理 |
| [rabbitmq/02-RabbitMQ核心原理.md](./03-distributed-microservices/mq/rabbitmq/02-RabbitMQ核心原理.md) | Exchange/Queue/Binding、死信队列、延迟队列、消息确认 | 原理 |
| [rocketmq/01-RocketMQ核心原理.md](./03-distributed-microservices/mq/rocketmq/01-RocketMQ核心原理.md) | NameServer/Broker架构、存储模型、消息类型、高可用设计 | 原理 |
| [rocketmq/02-RocketMQ高级特性.md](./03-distributed-microservices/mq/rocketmq/02-RocketMQ高级特性.md) | 顺序消息、事务消息、延迟消息、消息过滤、消息轨迹 | 原理 |
| [rocketmq/RocketMQ笔面试题集.md](./03-distributed-microservices/mq/rocketmq/RocketMQ笔面试题集.md) | 选择题 + 简答 + 场景题 | 题库 |
| [03-消息队列笔面试题集.md](./03-distributed-microservices/mq/03-消息队列笔面试题集.md) | 选择题 15 + 简答 8 + 场景设计 3（综合对比） | 题库 |

#### elasticsearch（3 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-ES核心原理.md](./03-distributed-microservices/elasticsearch/01-ES核心原理.md) | 倒排索引、分词器、映射、集群分片、写入流程 | 原理 |
| [02-ES查询与聚合分析.md](./03-distributed-microservices/elasticsearch/02-ES查询与聚合分析.md) | DSL 查询、bool/must/should、聚合、高亮、Spring Data ES | 原理 |
| [03-ES笔面试题集.md](./03-distributed-microservices/elasticsearch/03-ES笔面试题集.md) | 选择题 15 + 简答 8 + 场景设计 3 | 题库 |

#### clickhouse（2 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-ClickHouse核心原理.md](./03-distributed-microservices/clickhouse/01-ClickHouse核心原理.md) | MergeTree 引擎、列式存储、分区策略、物化视图 | 原理 |
| [02-ClickHouse笔面试题集.md](./03-distributed-microservices/clickhouse/02-ClickHouse笔面试题集.md) | 选择题 10 + 简答 5 + 场景设计 3 | 题库 |

#### git（3 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Git核心概念与常用命令.md](./03-distributed-microservices/git/01-Git核心概念与常用命令.md) | 分布式版本控制、四层模型、reset三种模式、远程协作、标签与版本 | 原理 |
| [02-Git分支策略与协作工作流.md](./03-distributed-microservices/git/02-Git分支策略与协作工作流.md) | 分支管理、rebase黄金法则、冲突解决、GitFlow/GitHubFlow/Trunk-Based | 原理 |
| [03-Git笔面试题集.md](./03-distributed-microservices/git/03-Git笔面试题集.md) | 选择题 15 + 简答 6 + 场景题 2 | 题库 |

---

### 04-python-aiagent — Python AI Agent（8 文件）

#### python-core（1 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-Python核心语法速通.md](./04-python-aiagent/python-core/01-Python核心语法速通.md) | Java对比Python速通、数据类型、函数、面向对象、装饰器、常用标准库 | 原理 |

#### langchain-rag（3 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [02-LangChain与AI智能体核心.md](./04-python-aiagent/langchain-rag/02-LangChain与AI智能体核心.md) | AI Agent循环、Model I/O、Chain、Tool、Agent、Memory、LangGraph编排 | 原理 |
| [03-RAG检索增强生成实战.md](./04-python-aiagent/langchain-rag/03-RAG检索增强生成实战.md) | RAG架构、文档切分、向量化、检索策略、知识库问答系统、RAG评估 | 原理 |
| [04-Python与AI智能体笔面试题集.md](./04-python-aiagent/langchain-rag/04-Python与AI智能体笔面试题集.md) | 选择题 15 + 简答 10 + 场景题 3 | 题库 |

#### llm-fine-tuning（4 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-大模型基础与Transformer架构.md](./04-python-aiagent/llm-fine-tuning/01-大模型基础与Transformer架构.md) | LLM发展脉络、Transformer架构、Self-Attention、GPT/LLaMA/Qwen系列、分词技术 | 原理 |
| [02-微调技术与LoRA原理.md](./04-python-aiagent/llm-fine-tuning/02-微调技术与LoRA原理.md) | 全量微调vs PEFT、LoRA数学推导、QLoRA量化、DeepSpeed分布式训练、评估方法 | 原理 |
| [03-强化学习与RLHF对齐技术.md](./04-python-aiagent/llm-fine-tuning/03-强化学习与RLHF对齐技术.md) | RL基础理论、策略梯度、RLHF三阶段、SFT、PPO、GRPO、DPO微调实战 | 原理 |
| [04-大模型微调笔面试题集.md](./04-python-aiagent/llm-fine-tuning/04-大模型微调笔面试题集.md) | 选择题 15 + 简答 10 + 场景题 3 | 题库 |

---

### extensions — 扩展模块（1 文件）

#### project（1 文件）

| 文件 | 内容 | 类型 |
|------|------|:--:|
| [01-电商订单实时统计分析平台.md](./extensions/project/01-电商订单实时统计分析平台.md) | 架构设计、技术选型、详细实现、部署方案 | 实战 |

---

## 学习建议

> 你已经有前端、Python 和 Node.js 的扎实基础，再学 Java 后端及配套技术栈，完全可以走"以熟带生、对比迁移"的快速路径。核心是 **复用已有知识，只学 Java 独有的东西**，并围绕实战项目串联整个技术栈。

- **对比学习**：每学一个 Java 概念，问自己"这个在 Node.js/Python 里怎么实现？"
- **项目驱动**：以"电商订单实时统计分析平台"为主线，学一个组件就集成一个组件
- **避坑指南**：不要啃《Java 编程思想》、不要手写 JDBC/Servlet、不要一次性学完所有 Spring Cloud 组件