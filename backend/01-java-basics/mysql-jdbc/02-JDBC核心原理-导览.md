# JDBC 核心原理 导览

> 定位：五维框架浓缩提炼 02-JDBC核心原理.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-JDBC核心原理.md).
> 前置知识：MySQL 基础与 SQL 核心、Java 基础

---

## 一、核心概念

### 1.1 JDBC 架构

| 维度 | 内容 |
|------|------|
| 是什么 | Java 访问关系型数据库的标准 API，采用接口与驱动分离的设计，让 Java 代码与具体数据库解耦。 |
| 能做什么 | 统一数据库访问接口；通过 DriverManager 管理驱动；建立连接执行 SQL；管理事务；处理结果集。 |
| 怎么用 | `Connection conn = DriverManager.getConnection(url, user, pwd);` |
| 原理和工作流程 | JDBC API 位于 java.sql 包，定义 Connection、Statement、ResultSet 等接口。应用调用接口，DriverManager 根据 URL 匹配厂商驱动，驱动将调用翻译为数据库协议经 TCP 与数据库通信。分层为接口层、驱动管理器、数据库驱动、数据库，各厂商实现同一接口实现解耦。 |
| 缺点 | API 偏底层样板代码多；需手动管理资源关闭；异常为受检异常处理繁琐；直接拼接 SQL 有注入风险；结果集映射需手工编写。 |

### 1.2 JDBC 编程六步骤

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 JDBC 访问数据库的标准六步流程，涵盖加载驱动到释放资源全过程。 |
| 能做什么 | 加载数据库驱动；获取连接；创建 Statement；执行 SQL；处理结果集；释放资源。 |
| 怎么用 | `Class.forName(driver);` `conn=DriverManager.getConnection(...);` `ps=conn.prepareStatement(sql);` `ps.executeQuery();` `rs.close();` |
| 原理和工作流程 | 第一步通过反射加载驱动类并注册到 DriverManager，MySQL 8.0 后可由 SPI 自动加载；第二步 DriverManager 遍历已注册驱动匹配 URL 建立 TCP 连接；第三步 Connection 创建 Statement 对象；第四步 Statement 调用 execute 发送 SQL；第五步 ResultSet 游标逐行读取；第六步逆序关闭资源释放连接。建议用 try-with-resources 自动关闭。 |
| 缺点 | 步骤繁琐样板代码重复；资源忘记关闭导致泄漏；手动事务管理易遗漏；异常处理复杂；每步都可能出错需大量 try-catch。 |

---

## 二、底层原理

### 2.1 PreparedStatement vs Statement

| 维度 | 内容 |
|------|------|
| 是什么 | JDBC 中两种 SQL 执行器的对比，前者预编译防注入后者直接拼接执行。 |
| 能做什么 | Statement 执行静态 SQL；PreparedStatement 预编译并参数化；防御 SQL 注入；复用执行计划；提供类型安全设值。 |
| 怎么用 | `PreparedStatement ps = conn.prepareStatement("SELECT * FROM t_user WHERE username=?"); ps.setString(1, name);` |
| 原理和工作流程 | Statement 直接将拼接的 SQL 字符串发送执行，用户输入若含 SQL 语法会被解析导致注入。PreparedStatement 先将带问号占位的 SQL 模板发送数据库做词法语法分析生成执行计划并缓存，执行时通过 setXxx 传入的值被当作纯数据字面量不会被当作 SQL 关键字解析，从根本上杜绝注入，且可复用执行计划提升批量场景性能。 |
| 缺点 | Statement 有注入风险不推荐使用；PreparedStatement 占位符不能用于表名列名；预编译需额外往返；批量场景仍需手动 addBatch；首次预编译有开销。 |

### 2.2 连接池原理

| 维度 | 内容 |
|------|------|
| 是什么 | 预先创建并复用数据库连接的技术，避免每次请求新建和销毁连接的开销。 |
| 能做什么 | 复用 TCP 连接；限制最大连接数；减少建连认证开销；保护数据库；提供连接有效性检测。 |
| 怎么用 | 配置 minimumIdle、maximumPoolSize、connectionTimeout 等参数。 |
| 原理和工作流程 | 不用连接池时每次请求经历 TCP 三次握手、数据库认证、四次挥手耗时 50 到 200 毫秒且高并发连接数失控。连接池在启动时预创建一批连接放入池中，请求时从池中借用，用完归还复用，借还耗时小于 1 毫秒。池通过最小空闲、最大连接、超时、最大生命周期等参数控制连接数量与质量，空闲超时或达到生命周期则淘汰重建。 |
| 缺点 | 参数配置不当导致连接耗尽或浪费；maxLifetime 大于 wait_timeout 导致连接失效；连接泄漏难以排查；池本身增加内存开销；需额外的探活机制。 |

### 2.3 HikariCP 原理

| 维度 | 内容 |
|------|------|
| 是什么 | 目前性能最高的 JDBC 连接池，Spring Boot 2.x 默认集成，以极致性能为设计目标。 |
| 能做什么 | 提供高性能连接管理；无锁借还连接；字节码代理；精简设计；状态机管理连接。 |
| 怎么用 | `HikariConfig config = new HikariConfig(); config.setMaximumPoolSize(20);` |
| 原理和工作流程 | 高性能源于多项优化：FastList 替代 ArrayList 去掉越界检查减少 get 开销；ConcurrentBag 无锁并发队列基于 ThreadLocal 与 CopyOnWriteArrayList，借连接优先从当前线程 ThreadLocal 取无竞争，否则 CAS 借取；使用 Javassist 生成代理类避免反射；整体精简只保留核心功能；连接状态精准控制避免悬空。借取流程为 ThreadLocal 优先、共享队列 CAS、等待或新建。 |
| 缺点 | 监控能力较弱需结合 Actuator；无 SQL 解析与防火墙；参数相对少灵活性有限；对连接泄漏仅记录警告；不适合需要 SQL 审计的场景。 |

### 2.4 Druid 原理

| 维度 | 内容 |
|------|------|
| 是什么 | 阿里巴巴开源的数据库连接池，主打监控统计与 SQL 解析能力。 |
| 能做什么 | 监控 SQL 执行；解析 SQL 类型与表名；SQL 防火墙拦截危险语句；连接探活；输出完整 SQL 日志。 |
| 怎么用 | `ds.setFilters("stat,wall");` 开启统计与防火墙。 |
| 原理和工作流程 | 内置 StatFilter 拦截 SQL 执行统计次数、慢查询、执行时间；SQL Parser 解析 SQL 识别类型与表名字段支持 SQL 防火墙；WallFilter 拦截 DROP、TRUNCATE、OR 1=1 等危险 SQL；多种探活方式 testWhileIdle 与 validationQuery 检测连接有效性；LogFilter 输出完整 SQL 日志便于排查。相比 HikariCP 牺牲部分性能换取监控与安全能力。 |
| 缺点 | 性能略低于 HikariCP；配置参数多复杂度高；SQL 解析增加开销；监控页需密码保护；对部分新语法解析不全。 |

### 2.5 事务管理

| 维度 | 内容 |
|------|------|
| 是什么 | JDBC 通过 Connection 对象管理事务的机制，默认自动提交可手动控制提交与回滚。 |
| 能做什么 | 开启关闭事务；提交持久化；回滚撤销；设置保存点部分回滚；配置隔离级别。 |
| 怎么用 | `conn.setAutoCommit(false); conn.commit(); conn.rollback();` |
| 原理和工作流程 | JDBC 默认 autoCommit 为 true 每条 SQL 独立事务立即提交。手动事务需先 setAutoCommit(false) 开启事务，执行多条 SQL 后全部成功调用 commit 提交持久化，出现异常调用 rollback 回滚撤销所有操作。setTransactionIsolation 设置隔离级别控制脏读、不可重复读、幻读。事务期间持有连接和锁，需在 finally 恢复 autoCommit 并关闭连接。 |
| 缺点 | 手动管理易遗漏提交或回滚；异常时未回滚导致脏数据；长事务占用连接和锁；隔离级别越高并发越低；跨连接无法事务。 |

### 2.6 Savepoint

| 维度 | 内容 |
|------|------|
| 是什么 | 事务内的部分回滚点，可将事务回滚到指定保存点而非整体回滚。 |
| 能做什么 | 在事务中标记位置；部分回滚保留之前的操作；实现嵌套事务语义；精细化控制回滚范围。 |
| 怎么用 | `Savepoint sp = conn.setSavepoint("before_transfer"); conn.rollback(sp);` |
| 原理和工作流程 | 在事务执行过程中调用 setSavepoint 创建保存点，数据库记录当前事务状态位置。当后续操作失败时调用 rollback(savepoint) 仅回滚到该保存点之后的操作，保存点之前的操作仍保留在事务中，随后可继续提交。保存点在 undo 日志中标记，回滚时只撤销保存点后的修改。适用于一个事务中部分操作可容忍失败的场景。 |
| 缺点 | 增加事务复杂度；保存点过多消耗 undo 空间；部分数据库对保存点支持有限；回滚后需手动处理业务逻辑；嵌套层级深难维护。 |

---

## 三、实战应用

### 3.1 完整 JDBC CRUD 示例

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 JDBC 六步实现增删改查与事务转账的完整代码实践。 |
| 能做什么 | 新增并获取自增主键；查询单条与列表；更新与删除；实现事务转账；异常时回滚。 |
| 怎么用 | `PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);` |
| 原理和工作流程 | 新增用 prepareStatement 指定 RETURN_GENERATED_KEYS 执行后通过 getGeneratedKeys 获取自增主键。查询用 executeQuery 返回 ResultSet 游标逐行读取映射为对象。更新删除用 executeUpdate 返回影响行数。转账事务先 setAutoCommit(false)，扣款与加款分两条 SQL，余额不足抛异常触发 rollback，全部成功 commit，finally 恢复 autoCommit 并关闭连接。 |
| 缺点 | 样板代码冗长；结果集映射需手工编写；资源关闭繁琐；事务管理侵入业务代码；异常处理复杂；无法应对对象关系映射。 |

### 3.2 HikariCP 连接池配置

| 维度 | 内容 |
|------|------|
| 是什么 | 在 Java 与 Spring Boot 中配置 HikariCP 连接池参数的实践。 |
| 能做什么 | 设置连接池大小；配置超时与生命周期；指定连接检测；集成 Spring Boot 自动装配。 |
| 怎么用 | `config.setMaximumPoolSize(20); config.setMaxLifetime(1800000);` |
| 原理和工作流程 | 通过 HikariConfig 设置 jdbcUrl、用户名密码、驱动类，再配置 minimumIdle 最小空闲、maximumPoolSize 最大连接、connectionTimeout 获取超时、idleTimeout 空闲存活、maxLifetime 最大生命周期、connectionTestQuery 探活 SQL。HikariDataSource 据此初始化连接池。Spring Boot 下通过 application.yml 的 spring.datasource.hikari 前缀自动装配，连接池在启动时创建并管理连接。 |
| 缺点 | 参数调优依赖经验；maxLifetime 需小于数据库 wait_timeout；maximumPoolSize 过大拖垮数据库过小导致等待；探活 SQL 增加开销；配置不当引发连接耗尽。 |

### 3.3 Druid 配置

| 维度 | 内容 |
|------|------|
| 是什么 | 在 Java 与 Spring Boot 中配置 Druid 连接池及监控页的实践。 |
| 能做什么 | 配置连接池参数；开启统计与防火墙；配置连接探活；启用 Web 监控页。 |
| 怎么用 | `ds.setFilters("stat,wall");` 监控页 `url-pattern: /druid/*` |
| 原理和工作流程 | 通过 DruidDataSource 设置 url、initialSize 初始连接、minIdle、maxActive、maxWait 获取超时等参数。setFilters("stat,wall") 同时开启 StatFilter 统计与 WallFilter 防火墙。testWhileIdle 与 validationQuery 在借出连接时检测有效性。Spring Boot 下通过 stat-view-servlet 配置监控页路径与登录凭证，web-stat-filter 监控 Web 请求的 SQL 执行情况。 |
| 缺点 | 参数多配置复杂；监控页暴露需密码保护否则安全风险；防火墙可能误拦合法 SQL；stat 过滤器有性能开销；生产环境需谨慎开放监控页。 |

### 3.4 Spring JdbcTemplate

| 维度 | 内容 |
|------|------|
| 是什么 | Spring 对 JDBC 的薄封装，消除样板代码同时保留手写 SQL 灵活性。 |
| 能做什么 | 自动管理资源关闭；统一异常体系；支持自定义 RowMapper；支持命名参数；配合声明式事务。 |
| 怎么用 | `jdbcTemplate.queryForObject(sql, new BeanPropertyRowMapper<>(User.class), id);` |
| 原理和工作流程 | JdbcTemplate 内部封装了 Connection、Statement、ResultSet 的创建与关闭逻辑，通过模板方法模式在 execute 回调中执行用户提供的 SQL 与 RowMapper。将 SQLException 转换为 Spring 统一的 DataAccessException 运行时异常体系。query 方法用 RowMapper 将 ResultSet 每行映射为对象，BeanPropertyRowMapper 按属性名自动映射。配合 @Transactional 实现声明式事务无需手动管理边界。 |
| 缺点 | 仍需手写 SQL；结果映射需配置 RowMapper；不支持对象关系级联；复杂查询代码冗长；介于 JDBC 与 ORM 之间定位尴尬。 |

---

## 四、常见面试题（附答案）

### 1. Statement、PreparedStatement、CallableStatement 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | JDBC 三种 SQL 执行器的对比，呈继承关系逐层增强。 |
| 能做什么 | Statement 执行静态 SQL；PreparedStatement 预编译防注入；CallableStatement 调用存储过程。 |
| 怎么用 | `conn.createStatement()` 或 `conn.prepareStatement(sql)` 或 `conn.prepareCall(sql)` |
| 原理和工作流程 | Statement 用于执行静态 SQL 字符串，存在注入风险性能差。PreparedStatement 继承 Statement，预编译 SQL 用问号占位参数，防注入且可复用执行计划。CallableStatement 继承 PreparedStatement，用于调用存储过程，支持 OUT 与 INOUT 参数注册与获取。三者继承链为 Statement 到 PreparedStatement 到 CallableStatement，能力逐层增强。 |
| 缺点 | Statement 有注入风险不推荐；PreparedStatement 不支持表名列名占位；CallableStatement 依赖存储过程可移植性差；三者选择需按场景；误用导致安全或性能问题。 |

### 2. PreparedStatement 是如何防止 SQL 注入的？

| 维度 | 内容 |
|------|------|
| 是什么 | PreparedStatement 通过预编译与参数化防御 SQL 注入的底层机制。 |
| 能做什么 | 将 SQL 模板与参数分离；参数作字面量处理；复用执行计划；提供类型安全设值。 |
| 怎么用 | `ps.setString(1, "admin' OR '1'='1");` |
| 原理和工作流程 | 数据库先对带问号占位的 SQL 模板做词法语法分析生成执行计划并缓存，此阶段不涉及参数值。执行时通过 setXxx 传入的值被视为纯数据字面量，即使包含单引号或 OR 1=1 等字符也只被当作普通字符串值处理，不会被当作 SQL 关键字解析。但前提是必须用问号占位并调用 setXxx，若用字符串拼接 SQL 再交给 PreparedStatement 执行依然会注入。 |
| 缺点 | 仅在正确使用问号占位时有效；字符串拼接方式仍会注入；不能用于表名列名等结构；预编译需额外往返；部分数据库预编译缓存有限。 |

### 3. 为什么要使用数据库连接池？HikariCP 为什么快？

| 维度 | 内容 |
|------|------|
| 是什么 | 连接池复用连接的必要性及 HikariCP 高性能的原因分析。 |
| 能做什么 | 复用 TCP 连接减少建连开销；限制连接数保护数据库；HikariCP 无锁借还；字节码代理；精简设计。 |
| 怎么用 | 配置 HikariCP 的 maximumPoolSize、minimumIdle 等参数。 |
| 原理和工作流程 | 不用连接池每次请求经历 TCP 三次握手、数据库认证、四次挥手耗时 50 到 200 毫秒且连接数失控。连接池预创建复用连接借还小于 1 毫秒并限制最大连接数。HikariCP 快的原因：FastList 去掉越界检查；ConcurrentBag 无锁队列基于 ThreadLocal 优先借本线程连接减少锁竞争；Javassist 生成代理类避免反射；整体精简无冗余特性。 |
| 缺点 | 连接池参数调优复杂；连接泄漏难排查；HikariCP 监控弱；maxLifetime 配置不当致连接失效；池占用内存。 |

### 4. JDBC 事务管理的基本流程是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | JDBC 手动管理事务的标准流程，涵盖开启、提交、回滚与资源释放。 |
| 能做什么 | 关闭自动提交开启事务；执行多条 SQL；成功提交；异常回滚；恢复并关闭连接。 |
| 怎么用 | `conn.setAutoCommit(false); conn.commit(); conn.rollback();` |
| 原理和工作流程 | 默认 autoCommit 为 true 每条 SQL 独立提交。手动事务先 setAutoCommit(false) 开启事务，执行多条 SQL，全部成功调用 commit 提交持久化，异常调用 rollback 回滚撤销，finally 中恢复 autoCommit 为 true 并关闭连接。需部分回滚时用 setSavepoint 标记保存点再 rollback(savepoint) 仅回滚该点之后操作。事务期间持有连接与锁须及时结束。 |
| 缺点 | 流程繁琐易遗漏提交或回滚；异常未回滚致脏数据；长事务占连接和锁；finally 恢复易忘；跨连接无法事务。 |

### 5. HikariCP 和 Druid 该如何选择？

| 维度 | 内容 |
|------|------|
| 是什么 | 两大主流连接池的对比与选型原则。 |
| 能做什么 | HikariCP 追求极致性能；Druid 提供监控与 SQL 审计；按场景权衡选择。 |
| 怎么用 | 性能优先选 HikariCP；监控审计优先选 Druid。 |
| 原理和工作流程 | HikariCP 性能最高配置简单体积小，是 Spring Boot 默认连接池，通过无锁队列与字节码优化实现极致吞吐，但监控能力弱需结合 Actuator。Druid 性能略逊但内置 StatFilter 统计、SQL Parser 解析、WallFilter 防火墙，提供可视化 Web 监控页。互联网项目追求性能选 HikariCP，金融国企等需 SQL 审计与安全防护选 Druid。 |
| 缺点 | HikariCP 监控弱不适合审计场景；Druid 性能略低且配置复杂；两者不可兼得；Druid 监控页有安全风险；HikariCP 无 SQL 防火墙。 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 汇总 JDBC 常见误用与资源管理陷阱的实践清单。 |
| 能做什么 | 防止资源泄漏；避免 SQL 注入；正确管理事务；合理配置连接池；优化批量操作。 |
| 怎么用 | try-with-resources 自动关闭；PreparedStatement 防注入；maxLifetime 设为 wait_timeout 的 60% 到 80%。 |
| 原理和工作流程 | 资源未在 finally 关闭导致连接泄漏池耗尽，须按 rs 到 ps 到 conn 逆序关闭或用 try-with-resources。Statement 拼接 SQL 致注入须用 PreparedStatement 问号占位。事务异常未回滚致脏数据须 try-catch-finally 模式。maxLifetime 大于 wait_timeout 致连接失效须设为 60% 到 80%。批量逐条执行慢须用 addBatch 加 rewriteBatchedStatements。getDate 丢时分秒须用 getTimestamp。 |
| 缺点 | 规则多需记忆；try-with-resources 仅 Java 7 以上；连接池参数依赖经验；批量 SQL 过大超限制；资源泄漏难复现。 |

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./02-JDBC核心原理.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
