# MyBatis 原生框架 导览

> 定位：五维框架浓缩提炼 03-MyBatis原生框架.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./03-MyBatis原生框架.md)。
> 前置知识：[JDBC核心原理](../../01-java-basics/mysql-jdbc/02-JDBC核心原理-导览.md)、SQL基础

---

## 一、核心概念

### 1.1 MyBatis 架构

| 维度 | 内容 |
|------|------|
| 是什么 | 一款半自动 ORM 框架，封装 JDBC 重复操作同时保留对 SQL 的完全控制力。 |
| 能做什么 | 封装连接与资源管理；SQL 与对象映射；动态 SQL；一二级缓存；事务管理；接口代理。 |
| 怎么用 | `SqlSession session = factory.openSession();` `User u = session.getMapper(UserMapper.class).findById(1L);` |
| 原理和工作流程 | 分三层：接口层 SqlSession 对外暴露 API；核心处理层 Executor 调度 StatementHandler、ParameterHandler、ResultSetHandler 完成 SQL 执行与结果映射；基础支撑层提供配置解析、日志、反射、类型转换、数据源。执行流程为调用 Mapper 方法到 SqlSession 到 Executor 查缓存到 StatementHandler 创建 PreparedStatement 到 ParameterHandler 设参到执行 SQL 到 ResultSetHandler 映射结果。 |
| 缺点 | 半自动需手写 SQL；学习曲线涉及 XML 配置；二级缓存分布式场景有脏读风险；复杂动态 SQL 难维护；结果映射配置繁琐。 |

### 1.2 核心配置文件 mybatis-config.xml

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 的全局配置文件，定义属性、设置、类型别名、环境、映射器等核心配置。 |
| 能做什么 | 引入外部属性；配置全局行为开关；定义类型别名；配置数据源与事务；注册 Mapper。 |
| 怎么用 | `<settings><setting name="mapUnderscoreToCamelCase" value="true"/></settings>` |
| 原理和工作流程 | 配置文件按 properties、settings、typeAliases、typeHandlers、environments、mappers 顺序解析。properties 引入外部文件支持占位符引用；settings 控制驼峰映射、缓存开关、日志实现、执行器类型等全局行为；typeAliases 简化全限定类名；environments 配置数据源类型与事务管理器；mappers 注册 Mapper 接口或 XML 映射文件位置。解析结果存入 Configuration 对象全局共享。 |
| 缺点 | XML 配置繁琐；配置项多易遗漏；环境切换需修改配置；与 Spring 整合后部分配置转移；类型处理器自定义复杂。 |

### 1.3 Mapper 映射器

| 维度 | 内容 |
|------|------|
| 是什么 | 由接口与 XML 两部分组成的 SQL 映射组件，MyBatis 通过动态代理生成实现类。 |
| 能做什么 | 定义方法签名；编写 SQL 与映射；动态拼接 SQL；获取自增主键；实现批量操作。 |
| 怎么用 | `interface UserMapper { User findById(Long id); }` 对应 `<select id="findById" resultType="User">SELECT ...</select>` |
| 原理和工作流程 | Mapper 由接口与 XML 组成，接口全限定名须等于 XML 的 namespace，方法名须等于 SQL 标签 id。MyBatis 启动时解析 XML 将每条 SQL 封装为 MappedStatement 存入 Configuration。调用 getMapper 时通过 MapperProxyFactory 用 JDK 动态代理生成实现类，MapperProxy.invoke 根据方法签名找到对应 MappedStatement 委托 SqlSession 执行，因此开发者只需定义接口与 XML 无需手写实现类。 |
| 缺点 | namespace 与接口路径须严格一致否则绑定异常；接口与 XML 分离增加维护成本；纯注解不利于复杂 SQL；方法名与 id 拼写错误难排查；多参数需 @Param。 |

---

## 二、底层原理

### 2.1 SqlSession 核心 API

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 的核心会话对象，封装 SQL 执行、事务管理、Mapper 获取等 API。 |
| 能做什么 | 执行增删改查；获取 Mapper 代理；管理事务提交回滚；清空缓存；关闭会话。 |
| 怎么用 | `sqlSession.selectList("UserMapper.findList", query);` `sqlSession.getMapper(UserMapper.class);` |
| 原理和工作流程 | SqlSession 是非线程安全的请求级对象，每次请求创建一个。selectOne、selectList、insert、update、delete 等方法接收 statementId 与参数，委托 Executor 执行。Executor 先查二级缓存与一级缓存未命中再执行 SQL。getMapper 返回接口的动态代理对象。SqlSessionFactory 是应用级单例由 Builder 创建，SqlSessionFactoryBuilder 用完即弃。事务需手动 commit 或 rollback。 |
| 缺点 | 非线程安全须每次请求新建；手动事务易遗漏；statementId 字符串易写错无编译检查；忘记 close 致连接泄漏；生命周期管理需谨慎。 |

### 2.2 动态 SQL

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 通过 XML 标签在运行时根据参数动态拼接 SQL 的能力，是相比 JDBC 的核心优势。 |
| 能做什么 | 条件判断拼接；智能 WHERE 与 SET 生成；多选一；遍历集合批量操作；修剪前后缀；绑定变量。 |
| 怎么用 | `<where><if test="username!=null">AND username LIKE ...</if></where>` `<foreach collection="list" item="u" separator=",">` |
| 原理和工作流程 | MyBatis 提供一组 XML 标签在运行时根据 OGNL 表达式求值动态拼接 SQL。if 标签满足条件拼接该段；where 自动生成 WHERE 并去掉首个 AND 或 OR；set 用于 UPDATE 去掉末尾逗号；choose/when/otherwise 实现多选一；foreach 遍历集合生成 IN 列表或批量 VALUES；trim 自定义前后缀修剪；bind 用 OGNL 预定义变量。拼接结果作为最终 SQL 交由 PreparedStatement 执行。 |
| 缺点 | OGNL 表达式语法特殊易错；XML 中小于号需转义；复杂动态 SQL 可读性差；拼接结果难调试；foreach 超大集合超 SQL 长度限制。 |

### 2.3 一二级缓存机制

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 的两级查询缓存机制，一级为 SqlSession 级默认开启，二级为 Mapper 级需手动开启。 |
| 能做什么 | 一级缓存同会话复用；二级缓存跨会话共享；配置淘汰策略；集成第三方缓存；减少数据库访问。 |
| 怎么用 | 全局 `<setting name="cacheEnabled" value="true"/>` Mapper 内 `<cache eviction="LRU"/>` |
| 原理和工作流程 | 一级缓存存储在 SqlSession 内部的 HashMap，key 为 statementId 加参数加分页信息，同一会话相同查询直接命中，执行增删改或关闭会话时失效。二级缓存为 namespace 级别跨 SqlSession 共享，需全局 cacheEnabled 加 Mapper 内 cache 标签开启，事务提交后才写入，默认 PerpetualCache 基于 HashMap 可集成 Ehcache 或 Redis。查询顺序为二级缓存到一级缓存到数据库。淘汰策略有 LRU、FIFO、SOFT、WEAK。 |
| 缺点 | 一级缓存仅同会话作用有限；二级缓存 namespace 级多表关联易脏读；缓存对象需 Serializable；分布式环境需外部缓存；事务未提交不写入二级缓存。 |

### 2.4 #{} vs ${} 区别

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 中两种参数占位方式的对比，前者预编译安全后者字符串拼接有风险。 |
| 能做什么 | #{} 预编译防注入；${} 动态拼接表名列名；自动类型处理；自动加引号。 |
| 怎么用 | `WHERE id = #{id}` 安全；`ORDER BY ${columnName}` 用于结构。 |
| 原理和工作流程 | #{} 底层使用 PreparedStatement 的问号占位，参数被当作字面量值处理，自动加引号与类型转换，防御 SQL 注入，适用于参数值。${} 是字符串直接拼接到 SQL 中，不做类型处理不加引号，存在 SQL 注入风险，适用于表名、列名、ORDER BY 字段等无法预编译的 SQL 结构。生产中优先用 #{}，必须用 ${} 时做白名单校验防止注入。 |
| 缺点 | #{} 不能用于表名列名等结构；${} 有注入风险须白名单校验；两者混用易出错；${} 不做类型转换；新手易误用 ${} 传参数值。 |

### 2.5 注解开发

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 支持的纯注解开发方式，用注解替代 XML 定义 SQL 与映射。 |
| 能做什么 | 注解定义增删改查；结果映射；关联查询；附加选项；参数命名。 |
| 怎么用 | `@Select("SELECT * FROM t_user WHERE id=#{id}") User findById(Long id);` |
| 原理和工作流程 | MyBatis 支持 @Select、@Insert、@Update、@Delete 注解直接在接口方法上定义 SQL。@Results 与 @Result 替代 resultMap 完成结果映射。@One 与 @Many 实现一对一与一对多关联查询。@Options 附加如 useGeneratedKeys 等选项。@Param 为多参数命名以便 SQL 中引用。注解方式适合简单 SQL，启动时 MyBatis 解析注解生成 MappedStatement，复杂 SQL 仍推荐 XML。 |
| 缺点 | 复杂 SQL 注解可读性差；动态 SQL 需 @SelectProvider 等较繁琐；注解与 XML 混用易混乱；无法使用 resultMap 高级映射；长 SQL 拼接字符串难维护。 |

### 2.6 逆向工程（MyBatis Generator）

| 维度 | 内容 |
|------|------|
| 是什么 | 根据数据库表自动生成实体类、Mapper 接口、Mapper XML 的代码生成工具。 |
| 能做什么 | 自动生成实体类；生成 Mapper 接口；生成 XML 映射；生成动态条件构造器；减少重复劳动。 |
| 怎么用 | 配置 generatorConfig.xml 后执行 `mvn mybatis-generator:generate` |
| 原理和工作流程 | 通过 generatorConfig.xml 配置数据库连接、生成目标包与路径、指定表名与实体名。MBG 读取数据库元数据获取表结构与列信息，按模板生成实体类、Mapper 接口含基础 CRUD、XML 映射文件、可选的 Example 动态条件构造器。可通过 Maven 插件或 Java API 执行。建议采用生成加继承扩展模式，MBG 生成基础类，自定义 Mapper 继承扩展功能避免重新生成覆盖手写代码。 |
| 缺点 | 生成的代码量大需筛选；重新生成会覆盖手写修改；Example 条件构造器不够灵活；配置文件维护成本；复杂业务仍需手写 SQL。 |

---

## 三、实战应用

### 3.1 完整项目搭建

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 MyBatis 原生框架搭建完整数据访问项目的实战，含配置、实体、Mapper、工具类与测试。 |
| 能做什么 | 配置数据源与事务；定义实体与查询对象；编写完整 Mapper XML；封装工具类；编写测试验证。 |
| 怎么用 | `SqlSessionFactory factory = new SqlSessionFactoryBuilder().build(Resources.getResourceAsStream("mybatis-config.xml"));` |
| 原理和工作流程 | 项目由 db.properties 配置数据库连接信息，mybatis-config.xml 引入属性并配置环境与映射器。实体类与查询对象封装数据。UserMapper.xml 定义 resultMap 结果映射、sql 通用列、select 查询含动态 where、insert 返回自增主键、batchInsert 批量插入、updateSelective 选择性更新、batchDelete 批量删除。MyBatisUtil 封装单例 SqlSessionFactory 与 openSession。测试类用 try-with-resources 管理 SqlSession 并手动提交事务。 |
| 缺点 | 原生配置繁琐；工具类需自行封装；事务手动管理易遗漏；无 Spring 集成需手写资源管理；项目结构需规范。 |

### 3.2 动态 SQL 实战

| 维度 | 内容 |
|------|------|
| 是什么 | 结合 if、where、foreach 等标签实现多条件查询与批量更新的实战技巧。 |
| 能做什么 | 任意组合条件查询；IN 列表动态生成；批量更新 case when；批量删除；选择性更新。 |
| 怎么用 | `<foreach collection="statusList" item="s" open="(" separator="," close=")">#{s}</foreach>` |
| 原理和工作流程 | 多条件查询用 where 包裹多个 if，条件为空时不生成 WHERE，满足时自动去首个 AND。IN 查询用 foreach 遍历集合生成括号包裹逗号分隔的值列表。批量更新用 foreach 配合 CASE WHEN 语句一次性更新多行不同值，避免逐条发送 SQL。foreach 的 collection 指定集合，item 指定元素变量，open 与 close 指定首尾符号，separator 指定分隔符。拼接结果交由 PreparedStatement 执行。 |
| 缺点 | foreach 超大集合 SQL 过长超限制需分批；CASE WHEN 批量更新 SQL 复杂难调试；OGNL 表达式易写错；XML 转义易遗漏；动态 SQL 拼接结果不可预测。 |

### 3.3 缓存配置实战

| 维度 | 内容 |
|------|------|
| 是什么 | 验证与配置 MyBatis 一级缓存与二级缓存的实际行为与生效条件。 |
| 能做什么 | 验证一级缓存命中与失效；验证二级缓存跨会话共享；配置淘汰策略与刷新间隔；设置只读与读写模式。 |
| 怎么用 | 一级：同 session 两次查询命中；二级：`<cache eviction="LRU" flushInterval="60000" size="512" readOnly="false"/>` |
| 原理和工作流程 | 一级缓存验证：同一 SqlSession 内连续两次相同查询，第二次命中一级缓存不发 SQL，执行更新或 commit 后缓存清空重新查询。二级缓存验证：跨两个 SqlSession，第一个会话查询并 commit 后数据写入二级缓存，第二个会话相同查询命中二级缓存不发 SQL。注意二级缓存在 SqlSession commit 或 close 后才写入，未提交不会命中。cache 标签配置 eviction 淘汰策略、flushInterval 刷新间隔、size 最大对象数、readOnly 是否只读。 |
| 缺点 | 二级缓存 commit 才写入易踩坑；readOnly 为 false 返回拷贝有序列化开销；多表关联易脏读；分布式环境失效；缓存命中率难预估。 |

### 3.4 逆向工程使用

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 MyBatis Generator 自动生成代码并集成到项目的方法。 |
| 能做什么 | 生成实体类；生成 Mapper 接口与 XML；生成 Example 条件构造器；Maven 插件执行；避免手写重复代码。 |
| 怎么用 | 配置 generatorConfig.xml 指定表名后执行 `mvn mybatis-generator:generate` |
| 原理和工作流程 | generatorConfig.xml 配置数据库连接、commentGenerator 控制注释、javaModelGenerator 指定实体生成位置、sqlMapGenerator 指定 XML 位置、javaClientGenerator 指定接口位置、table 指定表名与实体名并关闭 Example 等选项。执行 Maven 插件后 MBG 读取表结构生成 User 实体、UserMapper 接口含基础 CRUD、UserMapper XML、可选 UserExample 条件构造器。生成代码建议不手动修改，扩展功能通过继承或新建 Mapper 实现。 |
| 缺点 | 重新生成覆盖手写代码；Example 条件构造器不够灵活；配置文件维护成本；生成代码可能不符合项目规范；复杂业务仍需手写。 |

---

## 四、常见面试题（附答案）

### 1. MyBatis 的一级缓存和二级缓存有什么区别？

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 两级查询缓存的对比，作用域与开启方式不同。 |
| 能做什么 | 一级缓存同会话复用；二级缓存跨会话共享；配置淘汰策略；集成外部缓存。 |
| 怎么用 | 一级默认开启；二级需 `cacheEnabled=true` 加 `<cache/>` |
| 原理和工作流程 | 一级缓存是 SqlSession 级别默认开启，存储在 SqlSession 内部 HashMap，key 为 statementId 加参数，同会话相同查询直接命中，执行增删改或关闭会话时失效。二级缓存是 Mapper 的 namespace 级别需手动开启，跨 SqlSession 共享，事务提交后才写入，执行增删改时失效。查询顺序为二级缓存到一级缓存到数据库。二级缓存默认 LRU 淘汰，缓存对象需实现 Serializable，分布式环境需集成 Redis。 |
| 缺点 | 一级缓存仅同会话作用有限；二级缓存多表关联易脏读；分布式环境需外部缓存;事务未提交不写入；缓存一致性问题。 |

### 2. #{} 和 ${} 的区别是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 两种参数占位方式的对比，预编译与字符串拼接之别。 |
| 能做什么 | #{} 预编译防注入；${} 动态拼接结构；自动类型处理；自动加引号。 |
| 怎么用 | `WHERE id = #{id}` 安全；`ORDER BY ${columnName}` 用于结构。 |
| 原理和工作流程 | #{} 底层使用 PreparedStatement 问号占位，参数被当作字面量值自动加引号与类型转换防御 SQL 注入，适用于参数值。${} 是字符串直接拼接到 SQL 不做类型处理不加引号，存在注入风险，适用于表名列名 ORDER BY 字段等无法预编译的 SQL 结构。生产优先用 #{}，必须用 ${} 时做白名单校验。 |
| 缺点 | #{} 不能用于表名列名；${} 有注入风险须校验；两者混用易出错；${} 不做类型转换；新手易误用。 |

### 3. MyBatis 中如何处理动态 SQL？

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 通过 XML 标签运行时动态拼接 SQL 的机制。 |
| 能做什么 | 条件判断；智能 WHERE 与 SET；多选一；遍历集合；修剪前后缀；绑定变量。 |
| 怎么用 | `<if test="...">` `<where>` `<foreach collection="list" item="u">` |
| 原理和工作流程 | MyBatis 提供一组 XML 标签在运行时根据 OGNL 表达式求值动态拼接 SQL。if 满足条件拼接该段；where 自动生成 WHERE 去首个 AND 或 OR；set 用于 UPDATE 去末尾逗号；choose/when/otherwise 多选一；foreach 遍历集合用于 IN 查询或批量插入；trim 自定义前后缀修剪；bind 用 OGNL 预定义变量。拼接结果作为最终 SQL 交由 PreparedStatement 执行。这是 MyBatis 相比 JDBC 的核心优势。 |
| 缺点 | OGNL 语法特殊易错；XML 小于号需转义；复杂动态 SQL 可读性差；拼接结果难调试；foreach 超大集合超限制。 |

### 4. MyBatis 的执行流程是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | 从调用 Mapper 方法到返回结果的完整执行链路。 |
| 能做什么 | 接口代理调用；缓存查询；SQL 执行；参数设置；结果映射。 |
| 怎么用 | `mapper.findById(1L)` 触发完整流程。 |
| 原理和工作流程 | 应用调用 Mapper 接口方法，MyBatis 通过动态代理生成接口实现将方法映射到 MappedStatement。SqlSession 接收调用委托 Executor 执行器，Executor 先查二级缓存和一级缓存，未命中则调用 StatementHandler 创建 PreparedStatement。ParameterHandler 将 Java 参数设置到问号占位符，StatementHandler 执行 SQL，最后 ResultSetHandler 将结果集按 resultMap 或 resultType 映射为 Java 对象返回。配置解析、缓存、事务、类型转换由基础支撑层提供。 |
| 缺点 | 流程涉及多个组件调试困难；缓存与执行器交互复杂；代理层增加调用开销；结果映射配置繁琐；异常链路长难定位。 |

### 5. MyBatis 接口为什么不需要实现类就能执行 SQL？

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 通过动态代理为 Mapper 接口生成实现类的机制。 |
| 能做什么 | 接口定义方法；XML 定义 SQL；动态代理生成实现；方法映射 SQL；无需手写实现类。 |
| 怎么用 | `sqlSession.getMapper(UserMapper.class)` 获取代理对象。 |
| 原理和工作流程 | MyBatis 使用 JDK 动态代理为 Mapper 接口生成代理对象。启动时解析配置与 Mapper XML，将接口全限定名加方法名与对应 MappedStatement 建立映射存入 Configuration。调用 getMapper 时通过 MapperProxyFactory 用 JDK 动态代理生成实现类，MapperProxy.invoke 被调用时根据方法签名找到对应 MappedStatement，委托 SqlSession 执行 SQL 并返回结果。因此开发者只需定义接口和 XML 无需手写实现类。 |
| 缺点 | 动态代理仅支持接口不支持类；方法名与 id 须严格匹配；代理调用有反射开销；调试时栈帧深；新手难理解代理机制。 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 汇总 MyBatis 常见配置与使用陷阱的实践清单。 |
| 能做什么 | 避免 namespace 不匹配；防止连接泄漏；规避 SQL 注入；处理缓存脏读；解决 XML 转义。 |
| 怎么用 | namespace 等于接口全限定名；${} 做白名单校验；小于号用 `&lt;` 转义。 |
| 原理和工作流程 | namespace 与接口全限定名不一致致绑定异常须严格匹配。SqlSession 未关闭致连接泄漏须 try-with-resources。${} 致 SQL 注入须参数值用 #{} 结构用白名单。二级缓存多表关联致脏读须共用 namespace 或禁用。foreach 超大集合超 max_allowed_packet 须分批。动态 SQL 小于号被当标签起始须转义或 CDATA。单参数未加 @Param 取不到值须加注解。属性与列名不匹配须开驼峰映射或 resultMap。 |
| 缺点 | 规则多需记忆；namespace 拼写错误难排查；CDATA 增加代码冗余；二级缓存脏读隐蔽；@Param 易遗漏。 |

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./03-MyBatis原生框架.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
