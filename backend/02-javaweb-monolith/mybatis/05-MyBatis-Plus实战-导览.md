# MyBatis-Plus 实战 导览

> 定位：五维框架浓缩提炼 05-MyBatis-Plus实战.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./05-MyBatis-Plus实战.md)。
> 前置知识：[MyBatis原生框架](./03-MyBatis原生框架-导览.md)、SQL基础

---

## 一、核心概念

### 1.1 MyBatis vs MyBatis-Plus

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis 的增强工具，在 MyBatis 基础上只做增强不做改变，提供内置 CRUD 与高级功能。 |
| 能做什么 | 内置 CRUD 免手写；条件构造器；分页插件；逻辑删除；乐观锁；自动填充；代码生成器。 |
| 怎么用 | 引入 mybatis-plus-boot-starter 依赖，Mapper 继承 BaseMapper 即可使用。 |
| 原理和工作流程 | MyBatis-Plus 基于 MyBatis，注入通用 CRUD 实现原理是在启动时扫描继承 BaseMapper 的接口，通过 SqlInjector 注入通用方法对应的 SQL 到 MyBatis Configuration 中，每个通用方法注入为一条 MappedStatement，调用时直接执行。MyBatis-Plus 不修改 MyBatis 源码，作为 MyBatis 的插件增强，原生 MyBatis 功能完全兼容。条件构造器、分页插件等通过 MyBatis 拦截器机制实现。 |
| 缺点 | 通用方法无法满足复杂业务需手写；高级功能需理解拦截器原理；版本升级可能有兼容问题；复杂 SQL 仍需 XML；过度依赖通用方法忽略 SQL 优化。 |

### 1.2 核心注解

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 用于实体与表映射的核心注解集合，扩展自 MyBatis。 |
| 能做什么 | 指定表名；标识主键与策略；映射列名；排除字段；逻辑删除字段；乐观锁字段；自动填充字段。 |
| 怎么用 | `@TableName("t_user") @TableId(type=IdType.AUTO) @TableField("user_name")` |
| 原理和工作流程 | @TableName 指定实体对应表名解决命名不一致，@TableId 标识主键并指定生成策略如 AUTO 数据库自增、ASSIGN_ID 雪花 ID、UUID、INPUT 手动输入。@TableField 指定列名与是否参与插入更新等属性，exist 为 false 表示非数据库字段。@TableLogic 标记逻辑删除字段，删除时更新该字段而非物理删除。@Version 标记乐观锁版本号字段。@TableField 的 fill 属性配合 MetaObjectHandler 实现自动填充。注解在启动时解析生成 TableInfo 缓存供通用 CRUD 使用。 |
| 缺点 | 注解配置分散；命名策略默认可能不符合预期；@TableField 属性多易混淆；雪花 ID 时钟回拨问题；注解与全局配置混用易冲突。 |

---

## 二、底层原理

### 2.1 BaseMapper 常用方法

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 为 Mapper 接口提供的通用 CRUD 方法集，继承即用免手写。 |
| 能做什么 | 增删改查；批量操作；条件查询；主键查询；统计计数。 |
| 怎么用 | `userMapper.selectById(1L);` `userMapper.insert(user);` `userMapper.selectList(new QueryWrapper<User>().eq("status",1));` |
| 原理和工作流程 | BaseMapper 定义了 insert、deleteById、deleteBatchIds、updateById、selectById、selectBatchIds、selectList、selectCount、selectPage 等通用方法。MyBatis-Plus 在启动时通过 SqlInjector 将这些方法对应的 SQL 模板注入为 MappedStatement 存入 Configuration。调用时根据实体 TableInfo 解析表名与列名，拼接 SQL 交由 MyBatis 执行。条件构造器参数动态生成 WHERE 子句。无需编写 XML 即可完成单表 CRUD。 |
| 缺点 | 仅支持单表操作多表需手写；批量 insert 默认非真正批量需 rewriteBatchedStatements；复杂条件不如 XML 灵活；selectList 全表查需注意性能；方法名固定无法自定义语义。 |

### 2.2 条件构造器

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 提供的链式条件拼接 API，用于构建 WHERE 子句替代手写 SQL。 |
| 能做什么 | 等值范围模糊；排序分组；条件链式拼接；Lambda 类型安全；SQL 片段拼接。 |
| 怎么用 | `new LambdaQueryWrapper<User>().eq(User::getStatus, 1).like(User::getName, "张").ge(User::getAge, 18).orderByDesc(User::getId);` |
| 原理和工作流程 | QueryWrapper 与 LambdaQueryWrapper 提供链式 API，eq、ne、gt、ge、lt、le、like、in、between、isNull 等方法将条件封装为 MergeSegments。LambdaQueryWrapper 通过方法引用 User::getStatus 获取字段名避免硬编码字符串拼写错误。condition 参数控制条件是否生效实现动态查询。最终通过 AbstractWrapper 的 getCustomSqlSegment 生成 WHERE 子句拼接到通用 SQL 中，orderByDesc 等生成 ORDER BY 子句。条件构造器在执行时解析为 SQL 片段。 |
| 缺点 | 复杂条件拼接可读性下降；Lambda 编译稍慢；链式调用层级深；部分 SQL 函数难表达；与 XML 混用需注意优先级。 |

### 2.3 分页插件配置

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 内置的分页插件，通过拦截器自动拼接 LIMIT 与 COUNT 语句实现物理分页。 |
| 能做什么 | 自动物理分页；自动 COUNT 查询；支持多数据库；支持排序；Page 对象封装结果。 |
| 怎么用 | 配置 MybatisPlusInterceptor 添加 PaginationInnerInterceptor，调用 `userMapper.selectPage(new Page<>(1,10), wrapper);` |
| 原理和工作流程 | 配置 MybatisPlusInterceptor 注册 PaginationInnerInterceptor 并指定数据库类型。执行 selectPage 时传入 Page 对象封装页码页大小。分页插件作为 MyBatis 拦截器拦截 SQL 执行，先执行 COUNT 查询获取总数，再对原 SQL 拼接 LIMIT offset size 生成物理分页 SQL，执行后将结果封装到 Page 的 records 与 total。插件支持 MySQL、Oracle、PostgreSQL 等多种数据库方言自动适配分页语法。可通过 optimizeJoin 优化左连接。 |
| 缺点 | 深分页 COUNT 与 LIMIT 性能仍差；多表关联分页 COUNT 不准；需正确配置数据库类型；插件拦截有轻微开销；复杂 SQL 分页可能异常。 |

### 2.4 代码生成器（AutoGenerator）

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 提供的代码生成器，根据数据库表自动生成实体、Mapper、Service、Controller 全套代码。 |
| 能做什么 | 生成实体类；生成 Mapper 接口与 XML；生成 Service 与实现；生成 Controller；自定义模板。 |
| 怎么用 | 配置 AutoGenerator 指定数据源与包名后执行 `generator.execute();` |
| 原理和工作流程 | 通过 AutoGenerator 配置 GlobalConfig 全局策略、DataSourceConfig 数据源、PackageConfig 包路径、StrategyConfig 生成策略、TemplateConfig 模板。AutoGenerator 读取数据库元数据获取表结构，根据策略与 Velocity 模板生成实体类、Mapper 接口、Mapper XML、Service 接口、ServiceImpl 实现类、Controller。3.5.x 版本采用 builder 模式配置更简洁。生成的 Service 继承 IService 拥有更多业务方法，ServiceImpl 继承 ServiceImpl 拥有批量保存等增强方法。 |
| 缺点 | 重新生成覆盖手写代码；模板需自定义适配项目规范；生成代码量大需筛选；配置项多；复杂业务逻辑仍需手写。 |

---

## 三、实战应用

### 3.1 逻辑删除

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 通过标记字段实现软删除的机制，删除时更新标记而非物理删除。 |
| 能做什么 | 软删除不丢数据；查询自动过滤已删除；可恢复误删；统一逻辑删除字段。 |
| 怎么用 | `@TableLogic` 注解字段，配置 `logic-delete-field`、`logic-delete-value`、`logic-not-delete-value`。 |
| 原理和工作流程 | 实体字段标注 @TableLogic 标记逻辑删除字段，配置未删除值与已删除值。执行 deleteById 时 MyBatis-Plus 拦截改为 UPDATE 语句将逻辑删除字段更新为已删除值而非物理 DELETE。执行查询时自动拼接 WHERE 条件过滤已删除记录。selectList、selectById、update 等方法均自动加入逻辑删除条件。物理删除可通过特殊方法绕过。逻辑删除让数据可恢复同时对外不可见，适合需要审计追溯的场景。 |
| 缺点 | 唯一索引需包含逻辑删除字段否则冲突；查询性能因额外条件下降；逻辑删除字段占用空间；业务代码需感知软删除；物理删除需特殊处理。 |

### 3.2 乐观锁

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 通过版本号字段实现乐观锁的机制，防止并发更新丢失。 |
| 能做什么 | 并发更新检测；版本号自动递增；更新失败重试；CAS 语义。 |
| 怎么用 | `@Version` 注解字段，配置 OptimisticLockerInnerInterceptor 拦截器。 |
| 原理和工作流程 | 实体字段标注 @Version 标记乐观锁版本号。配置 MybatisPlusInterceptor 添加 OptimisticLockerInnerInterceptor。执行 updateById 时拦截器自动在 WHERE 条件中加入 version 等于当前版本，并 SET version 加 1。若数据库中版本号与实体版本号不一致说明已被其他事务修改，UPDATE 影响行数为 0 即更新失败。应用层检测影响行数为 0 后可重试或报错。乐观锁适合读多写少场景，相比悲观锁不阻塞提升并发。 |
| 缺点 | 写冲突频繁时重试开销大；需应用层处理更新失败；版本号字段占用空间；不支持复杂并发控制；高竞争场景性能不如悲观锁。 |

### 3.3 自动填充

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 通过 MetaObjectHandler 在插入更新时自动填充字段值的机制。 |
| 能做什么 | 自动填充创建时间；自动填充更新时间；自动填充操作人；统一审计字段。 |
| 怎么用 | 字段标注 `@TableField(fill=FieldFill.INSERT)`，实现 MetaObjectHandler 重写 insertFill 与 updateFill。 |
| 原理和工作流程 | 实体字段标注 @TableField 的 fill 属性指定 INSERT、UPDATE 或 INSERT_UPDATE 填充时机。实现 MetaObjectHandler 接口重写 insertFill 与 updateFill 方法，在方法中通过 setFieldValByName 或 strictInsertFill 设置字段值如创建时间、更新时间、操作人。MyBatis-Plus 在执行 insert 或 update 时调用 MetaObjectHandler 的对应方法，通过反射将值填充到实体对象中再生成 SQL。这样审计字段无需在每个业务方法中手动设置。 |
| 缺点 | 反射填充有轻微性能开销；需注册 MetaObjectHandler Bean；复杂填充逻辑需手写；填充时机固定不够灵活；与审计功能重叠需选择。 |

---

## 四、常见面试题（附答案）

### 1. MyBatis-Plus 的 BaseMapper 提供了哪些方法？

| 维度 | 内容 |
|------|------|
| 是什么 | BaseMapper 为 Mapper 接口提供的通用 CRUD 方法集，继承即用。 |
| 能做什么 | insert 新增；deleteById 删除；updateById 更新；selectById 查询；selectList 列表；selectPage 分页；selectCount 统计。 |
| 怎么用 | `userMapper.insert(user);` `userMapper.selectPage(new Page<>(1,10), wrapper);` |
| 原理和工作流程 | BaseMapper 定义 insert、deleteById、deleteBatchIds、updateById、selectById、selectBatchIds、selectList、selectCount、selectPage 等方法。MyBatis-Plus 启动时通过 SqlInjector 将这些方法对应 SQL 模板注入为 MappedStatement。调用时根据实体 TableInfo 解析表名列名拼接 SQL 交由 MyBatis 执行。条件构造器参数动态生成 WHERE。无需编写 XML 即完成单表 CRUD。 |
| 缺点 | 仅支持单表操作；批量 insert 默认非真正批量；复杂条件不如 XML 灵活；selectList 全表查需注意性能；方法名固定无法自定义语义。 |

### 2. MyBatis-Plus 如何实现分页？底层原理是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 内置分页插件通过拦截器自动拼接 LIMIT 与 COUNT 实现物理分页。 |
| 能做什么 | 自动物理分页；自动 COUNT 查询；多数据库支持；排序；Page 对象封装。 |
| 怎么用 | 配置 PaginationInnerInterceptor，调用 `selectPage(new Page<>(1,10), wrapper)` |
| 原理和工作流程 | 配置 MybatisPlusInterceptor 注册 PaginationInnerInterceptor 指定数据库类型。执行 selectPage 传入 Page 对象封装页码页大小。分页插件作为 MyBatis 拦截器拦截 SQL 执行，先执行 COUNT 查询获取总数，再对原 SQL 拼接 LIMIT offset size 生成物理分页 SQL，执行后将结果封装到 Page 的 records 与 total。支持 MySQL Oracle PostgreSQL 等多种方言自动适配分页语法。 |
| 缺点 | 深分页 COUNT 与 LIMIT 性能仍差；多表关联分页 COUNT 不准；需正确配置数据库类型；插件拦截有轻微开销；复杂 SQL 分页可能异常。 |

### 3. 条件构造器 QueryWrapper 和 LambdaQueryWrapper 有什么区别？

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 两种条件构造器的对比，字符串字段名与 Lambda 方法引用之别。 |
| 能做什么 | QueryWrapper 字符串指定字段；LambdaQueryWrapper 方法引用类型安全；链式拼接条件；动态条件。 |
| 怎么用 | `new QueryWrapper<User>().eq("status",1)` 或 `new LambdaQueryWrapper<User>().eq(User::getStatus,1)` |
| 原理和工作流程 | QueryWrapper 通过字符串指定字段名如 eq("status",1)，简单直观但字段名拼写错误在运行时才暴露。LambdaQueryWrapper 通过方法引用 User::getStatus 获取字段名，编译期检查字段存在性重构友好，底层通过 SerializedLambda 解析方法引用对应的属性名再映射到列名。两者 API 一致仅字段指定方式不同，最终都生成 WHERE 子句拼接到 SQL。Lambda 版本在性能上有微弱的序列化开销但可忽略。 |
| 缺点 | QueryWrapper 字段名硬编码易拼写错误；LambdaQueryWrapper 序列化有微弱开销；Lambda 不支持复杂表达式；两者混用易混乱；链式层级深可读性下降。 |

### 4. 逻辑删除的原理是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 通过标记字段实现软删除的机制，删除时更新标记而非物理删除。 |
| 能做什么 | 软删除保留数据；查询自动过滤；可恢复误删；统一删除字段。 |
| 怎么用 | `@TableLogic` 注解字段，配置删除值与未删除值。 |
| 原理和工作流程 | 实体字段标注 @TableLogic 标记逻辑删除字段，配置未删除值与已删除值。执行 deleteById 时 MyBatis-Plus 拦截改为 UPDATE 将逻辑删除字段更新为已删除值而非物理 DELETE。执行查询时自动拼接 WHERE 条件过滤已删除记录。selectList、selectById、update 等方法均自动加入逻辑删除条件。物理删除可通过特殊方法绕过。逻辑删除让数据可恢复同时对外不可见。 |
| 缺点 | 唯一索引需包含逻辑删除字段否则冲突；查询性能因额外条件下降；逻辑删除字段占用空间；业务代码需感知软删除；物理删除需特殊处理。 |

### 5. MyBatis-Plus 的乐观锁是如何实现的？

| 维度 | 内容 |
|------|------|
| 是什么 | MyBatis-Plus 通过版本号字段与拦截器实现乐观锁的机制。 |
| 能做什么 | 并发更新检测；版本号自动递增；更新失败检测；CAS 语义。 |
| 怎么用 | `@Version` 注解字段，配置 OptimisticLockerInnerInterceptor。 |
| 原理和工作流程 | 实体字段标注 @Version 标记乐观锁版本号。配置 MybatisPlusInterceptor 添加 OptimisticLockerInnerInterceptor。执行 updateById 时拦截器自动在 WHERE 加入 version 等于当前版本，并 SET version 加 1。若数据库版本号与实体版本号不一致说明已被其他事务修改，UPDATE 影响行数为 0 即更新失败。应用层检测影响行数为 0 后重试或报错。乐观锁适合读多写少场景不阻塞提升并发。 |
| 缺点 | 写冲突频繁时重试开销大；需应用层处理更新失败；版本号字段占用空间；不支持复杂并发控制；高竞争场景性能不如悲观锁。 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 汇总 MyBatis-Plus 常见配置与使用陷阱的实践清单。 |
| 能做什么 | 解决主键策略冲突；处理逻辑删除唯一索引；避免乐观锁失效；批量插入优化；多数据源配置。 |
| 怎么用 | 主键用 ASSIGN_ID；逻辑删除字段纳入唯一索引；乐观锁字段需查询带出。 |
| 原理和工作流程 | 主键策略默认 ASSIGN_ID 雪花 ID，与数据库 AUTO 冲突需 @TableId 指定一致。逻辑删除字段纳入唯一索引避免软删除后唯一约束冲突。乐观锁 @Version 字段更新前需先查询带出版本号否则 WHERE 条件无版本致锁失效。批量 saveBatch 默认逐条插入需开启 rewriteBatchedStatements 实现真正批量。多数据源用 dynamic-datasource 或 @DS 注解切换。@TableLogic 与 @TableField fill 同时使用需注意填充时机。 |
| 缺点 | 主键策略配置不当致冲突；逻辑删除唯一索引设计复杂；乐观锁易因未查询版本号失效；批量优化依赖驱动参数；多数据源事务管理复杂。 |

---

> [返回原文](./05-MyBatis-Plus实战.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
