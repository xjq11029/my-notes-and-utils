# Spring Data JPA 深度

> 学习路线对应：第3周 -- 数据访问与 ORM
> 前置知识：Spring Boot 基础、SQL 基础
> 预计学习时间：1-2 天

> 📖 **参考链接**：
> - [Spring Data JPA 官方文档](https://docs.spring.io/spring-data/jpa/reference/) -- Spring Data JPA 官方参考文档，涵盖 Repository、查询方法、JPQL、Specification、审计等全部特性
> - [Spring Data JPA 索引](https://docs.spring.io/spring-data/jpa/reference/index.html) -- 官方文档目录，按主题快速定位章节
> - [Spring Framework 参考文档](https://docs.spring.io/spring-framework/reference/) -- Spring 框架参考，含事务管理、AOP 等底层机制
> - [Jakarta Persistence API (JPA) 规范](https://jakarta.ee/specifications/persistence/) -- JPA 标准规范，理解注解语义的权威来源

## 一、核心概念

### 1.1 JPA 核心注解

> **生活化类比：JPA = "全自动同声传译"** —— 如果说 MyBatis 是"半自动翻译官"（SQL 你自己写，翻译它来做），那么 JPA/Hibernate 就是"全自动同声传译"——你只要定义好实体类（`@Entity` 标注的 Java 类），告诉它"User 类对应 t_user 表，username 字段对应 user_name 列"，之后 `save(user)` 它自己生成 `INSERT`、`findById(id)` 自己生成 `SELECT`、甚至复杂关联查询也能通过 JPQL 或方法名推导（`findByUsernameAndAge`）自动实现。开发者几乎不用碰 SQL，专注于对象和业务逻辑。代价是：SQL 对你"黑盒"，复杂报表、多表关联、极致性能优化时反而受束缚，需要用 `@Query` 写 JPQL 或原生 SQL 突破。所以国内复杂业务多用 MyBatis，标准 CRUD 为主的场景用 JPA 开发效率极高。

| 注解 | 作用 | 示例 |
|------|------|------|
| `@Entity` | 标识实体类，映射到数据库表 | `@Entity` |
| `@Table(name = "xxx")` | 指定映射的表名 | `@Table(name = "t_user")` |
| `@Id` | 标识主键字段 | `@Id` |
| `@GeneratedValue` | 主键生成策略 | `@GeneratedValue(strategy = GenerationType.IDENTITY)` |
| `@Column` | 指定列的映射细节 | `@Column(name = "user_name", length = 50, nullable = false)` |
| `@Transient` | 不映射到数据库 | `@Transient` |
| `@Enumerated` | 枚举类型映射 | `@Enumerated(EnumType.STRING)` |
| `@Lob` | 大对象类型（TEXT/BLOB） | `@Lob` |

**主键生成策略：**

| 策略 | 说明 | 适用数据库 |
|------|------|-----------|
| `IDENTITY` | 自增主键 | MySQL、SQL Server |
| `SEQUENCE` | 序列 | Oracle、PostgreSQL |
| `TABLE` | 使用单独的表模拟序列 | 通用 |
| `AUTO` | 由 JPA 自动选择 | 默认 |

### 1.2 关联关系映射

| 关系 | 注解 | 说明 |
|------|------|------|
| 一对一 | `@OneToOne` | 一个实体对应另一个实体 |
| 一对多 | `@OneToMany` | 一个实体对应多个实体 |
| 多对一 | `@ManyToOne` | 多个实体对应一个实体 |
| 多对多 | `@ManyToMany` | 多个实体对应多个实体 |

**fetch 策略：**

| 策略 | 说明 | 关联类型默认值 |
|------|------|-------------|
| **LAZY（懒加载）** | 访问关联属性时才查询 | `@OneToMany`、`@ManyToMany` 默认 |
| **EAGER（急加载）** | 查询主实体时立即查询关联实体 | `@OneToOne`、`@ManyToOne` 默认 |

```java
@Entity
@Table(name = "t_user")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "username", nullable = false, length = 50)
    private String username;

    // 一对多：一个用户有多个订单
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY,
               cascade = CascadeType.ALL)
    private List<Order> orders = new ArrayList<>();
}

@Entity
@Table(name = "t_order")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 多对一：多个订单属于一个用户
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;
}
```

**cascade（级联）类型：**

| 级联类型 | 说明 |
|---------|------|
| `CascadeType.PERSIST` | 级联保存 |
| `CascadeType.MERGE` | 级联更新 |
| `CascadeType.REMOVE` | 级联删除 |
| `CascadeType.REFRESH` | 级联刷新 |
| `CascadeType.ALL` | 包含以上所有 |

**1.2.1 完整 JPA 实体映射示例（含双向关联、复合主键、枚举、大对象）：**

```java
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

// ============ 主实体：订单（双向关联用户） ============
@Entity
@Table(name = "t_order")
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "order_no", nullable = false, unique = true, length = 32)
    private String orderNo;

    @Column(name = "amount", nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;

    // 多对一：多个订单属于一个用户（订单方维护外键）
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    // 一对多：一个订单有多个订单项
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();

    // 枚举映射
    @Enumerated(EnumType.STRING)
    @Column(name = "status", length = 20)
    private OrderStatus status;

    // 大对象（如备注，TEXT 类型）
    @Lob
    @Column(name = "remark")
    private String remark;

    // 不映射到数据库的字段
    @Transient
    private String transientFlag;

    // getter/setter 省略
}

// ============ 枚举定义 ============
public enum OrderStatus {
    PENDING,    // 待支付
    PAID,       // 已支付
    SHIPPED,    // 已发货
    COMPLETED,  // 已完成
    CANCELLED   // 已取消
}

// ============ 订单项实体（复合主键示例） ============
@Entity
@Table(name = "t_order_item")
@IdClass(OrderItemId.class)  // 复合主键类
public class OrderItem {

    @Id
    @Column(name = "order_id")
    private Long orderId;

    @Id
    @Column(name = "product_id")
    private Long productId;

    @Column(name = "quantity", nullable = false)
    private Integer quantity;

    @Column(name = "price", nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    // 多对一：订单项属于订单（订单项方维护外键，mappedBy 指向 Order 的 items 属性）
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", insertable = false, updatable = false)
    private Order order;

    // getter/setter 省略
}

// ============ 复合主键类（需实现 Serializable，重写 equals/hashCode） ============
import java.io.Serializable;
import java.util.Objects;

public class OrderItemId implements Serializable {
    private Long orderId;
    private Long productId;

    public OrderItemId() {}

    public OrderItemId(Long orderId, Long productId) {
        this.orderId = orderId;
        this.productId = productId;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof OrderItemId)) return false;
        OrderItemId that = (OrderItemId) o;
        return Objects.equals(orderId, that.orderId) &&
               Objects.equals(productId, that.productId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(orderId, productId);
    }
}
```

**实体映射最佳实践：**

| 实践 | 说明 | 原因 |
|------|------|------|
| 关联默认用 `LAZY` | `@ManyToOne`、`@OneToOne` 默认 EAGER，建议改为 LAZY | 避免不必要的关联查询，防止 N+1 |
| 双向关联由一方维护 | `@OneToMany` 用 `mappedBy` 放弃维护权 | 避免双方都维护外键导致冗余 UPDATE |
| 复合主键用 `@IdClass` 或 `@EmbeddedId` | 实现 Serializable，重写 equals/hashCode | JPA 规范要求，影响缓存和 detached 合并 |
| 实体重写 equals/hashCode | id 为 null 时用对象身份，否则用 id | 避免新实体放入 Set 时 hashCode 不一致 |
| 避免双向关联 JSON 递归 | 用 `@JsonIgnore` / `@JsonManagedReference` | 防止序列化时 StackOverflowError |

---

## 二、底层原理

### 2.1 N+1 问题及解决方案

**N+1 问题：** 查询主表时（1 次查询），遍历每个主实体访问关联属性时，每次都会单独查询关联表（N 次查询），导致总共 N+1 次查询。

> **生活化类比：N+1 问题 = "餐厅逐个上菜的笨服务员"** —— 你请 10 个朋友吃饭（查 10 个 User，1 次 SQL），服务员上菜时却犯傻：给第 1 个朋友端菜时跑去后厨问一次"这位的订单有哪些菜"（查 1 次 Orders），给第 2 个朋友又跑去后厨问一次……10 个朋友跑了 10 趟后厨（N 次 SQL），加上最初那 1 次点名，总共 N+1 = 11 次往返。聪明的服务员会怎么做？**一次性拿着所有朋友的名单去后厨**："这 10 位的菜全部给我"（JOIN FETCH，1 次 SQL 搞定）。这就是 `JOIN FETCH` 解决 N+1 的本质：把 N 次关联查询合并成 1 次 JOIN。`@EntityGraph` 是"声明式"地告诉 JPA 提前取哪些关联，`@BatchSize` 则是"分批取"（每次问后厨要 10 位的菜，减少往返次数）。生产中优先用 JOIN FETCH。

```java
// 问题代码
List<User> users = userRepository.findAll(); // 1 次查询
for (User user : users) {
    // 每次访问 user.getOrders() 都会触发一次查询 = N 次查询
    System.out.println(user.getOrders().size());
}
```

**解决方案：**

| 方案 | 实现方式 | 适用场景 |
|------|---------|---------|
| **JOIN FETCH** | `@Query("SELECT u FROM User u JOIN FETCH u.orders")` | 单次查询，灵活 |
| **@EntityGraph** | `@EntityGraph(attributePaths = "orders")` | 声明式，简洁 |
| **@BatchSize** | `@BatchSize(size = 10)` | 批量加载，减少查询次数 |

```java
// 方案1：JOIN FETCH
@Query("SELECT u FROM User u JOIN FETCH u.orders")
List<User> findAllWithOrders();

// 方案2：@EntityGraph
@EntityGraph(attributePaths = {"orders"})
@Query("SELECT u FROM User u")
List<User> findAllWithOrdersEntityGraph();

// 方案3：@BatchSize
@BatchSize(size = 10)
@OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
private List<Order> orders;
```

### 2.2 JPQL 查询

JPQL（Java Persistence Query Language）是面向对象的查询语言，操作的是实体对象而非数据库表。

> **生活化类比：Spring Data JPA 的方法名推导查询 = "自助点餐机"** —— 传统写 SQL 像跟人工服务员点菜：你要详细说"给我来一份用户表里用户名等于张三且年龄大于18岁的记录"。Spring Data JPA 的方法名推导查询就像商场里的自助点餐机——你只要按按钮（写方法名 `findByUsernameAndAgeGreaterThan`），机器自动理解你的需求并生成对应 SQL。`findBy` 是"我要查"，`Username` 是"按用户名"，`And` 是"并且"，`AgeGreaterThan` 是"年龄大于"。机器（Spring Data JPA）解析方法名，按规则拆解关键字，自动拼出 `SELECT ... WHERE username = ? AND age > ?`。简单查询完全不用写 SQL，复杂查询（聚合、多表、动态条件）再用 `@Query` 写 JPQL 或 Specification。注意：方法名推导虽方便，但方法名过长可读性差（如 `findByStatusAndCreatedAtBetweenAndDeletedFalse`），复杂场景还是推荐 `@Query`。

**方法名推导查询关键字速查表：**

| 关键字 | 示例 | 对应 SQL |
|--------|------|----------|
| `findBy` | `findByUsername` | `WHERE username = ?` |
| `And` / `Or` | `findByUsernameAndAge` | `WHERE username = ? AND age = ?` |
| `Between` | `findByAgeBetween` | `WHERE age BETWEEN ? AND ?` |
| `LessThan` / `GreaterThan` | `findByAgeGreaterThan` | `WHERE age > ?` |
| `LessThanEqual` / `GreaterThanEqual` | `findByAgeGreaterThanEqual` | `WHERE age >= ?` |
| `Like` / `NotLike` | `findByUsernameLike` | `WHERE username LIKE ?` |
| `StartingWith` / `EndingWith` | `findByUsernameStartingWith` | `WHERE username LIKE ?%` |
| `IsNull` / `IsNotNull` | `findByEmailIsNull` | `WHERE email IS NULL` |
| `In` / `NotIn` | `findByStatusIn` | `WHERE status IN (...)` |
| `OrderBy` | `findByAgeOrderByCreatedAtDesc` | `ORDER BY created_at DESC` |
| `Top` / `First` | `findTop10ByOrderByCreatedAtDesc` | `ORDER BY created_at DESC LIMIT 10` |
| `Distinct` | `findDistinctByUsername` | `SELECT DISTINCT ...` |

```java
// 基本查询
@Query("SELECT u FROM User u WHERE u.username = :username")
User findByUsername(@Param("username") String username);

// 聚合查询
@Query("SELECT COUNT(o) FROM Order o WHERE o.user.id = :userId")
Long countOrdersByUserId(@Param("userId") Long userId);

// 更新操作
@Modifying
@Transactional
@Query("UPDATE User u SET u.status = :status WHERE u.id = :id")
int updateStatus(@Param("id") Long id, @Param("status") String status);

// 原生 SQL
@Query(value = "SELECT * FROM t_user WHERE username = ?1", nativeQuery = true)
User findByUsernameNative(String username);
```

**JPQL 与 SQL 的核心区别：**

| 维度 | JPQL | SQL |
|------|------|-----|
| 操作对象 | 实体类（`User`）和属性（`u.username`） | 表（`t_user`）和列（`user_name`） |
| 大小写敏感 | 实体类名和属性名区分大小写 | 表名和列名通常不区分 |
| 关联查询 | `JOIN u.orders`（通过对象属性导航） | `JOIN t_order o ON o.user_id = u.id`（显式 ON） |
| 分页 | 通过 Spring Data 的 `Pageable` 参数 | 数据库方言（`LIMIT` / `ROWNUM`） |
| 可移植性 | 跨数据库无缝切换 | 方言相关，可能需改写 |

**JPQL 进阶用法：**

```java
// 1. 关联查询（通过对象属性导航，无需 ON）
@Query("SELECT u FROM User u JOIN u.orders o WHERE o.amount > :amount")
List<User> findUsersWithOrderAmountGreaterThan(@Param("amount") BigDecimal amount);

// 2. 投影查询（只取需要的字段，返回 Object[] 或 DTO）
@Query("SELECT u.id, u.username FROM User u WHERE u.status = :status")
List<Object[]> findIdAndUsernameByStatus(@Param("status") Integer status);

// 3. DTO 投影（通过构造函数表达式）
@Query("SELECT new com.example.dto.UserDTO(u.id, u.username, u.email) FROM User u WHERE u.id = :id")
UserDTO findDTOById(@Param("id") Long id);

// 4. 子查询
@Query("SELECT u FROM User u WHERE u.age > (SELECT AVG(u2.age) FROM User u2)")
List<User> findUsersOlderThanAverage();

// 5. 分页 + 排序（结合 Pageable 参数）
Page<User> findByStatus(Integer status, Pageable pageable);
// 调用：userRepository.findByStatus(1, PageRequest.of(0, 10, Sort.by("createdAt").descending()));

// 6. 命名参数与位置参数对比
@Query("SELECT u FROM User u WHERE u.username = ?1 AND u.email = ?2")  // 位置参数
@Query("SELECT u FROM User u WHERE u.username = :name AND u.email = :email")  // 命名参数（推荐）
```

> **JPQL 避坑**：JPQL 中不能使用数据库列名（如 `WHERE user_name = ?`），必须用实体属性名（`WHERE u.username = ?`）；`JOIN` 时不能写 `ON` 条件，关联条件由 `@OneToMany`/`@ManyToOne` 的映射关系自动提供；如必须用原生 SQL，加 `nativeQuery = true`，但失去跨数据库可移植性。

### 2.3 Specification 动态查询

```java
public interface UserRepository extends JpaRepository<User, Long>,
        JpaSpecificationExecutor<User> {
}

// 动态查询
public List<User> searchUsers(String username, String email, Integer minAge) {
    Specification<User> spec = (root, query, cb) -> {
        List<Predicate> predicates = new ArrayList<>();

        if (StringUtils.hasText(username)) {
            predicates.add(cb.like(root.get("username"), "%" + username + "%"));
        }
        if (StringUtils.hasText(email)) {
            predicates.add(cb.equal(root.get("email"), email));
        }
        if (minAge != null) {
            predicates.add(cb.greaterThanOrEqualTo(root.get("age"), minAge));
        }

        return cb.and(predicates.toArray(new Predicate[0]));
    };

    return userRepository.findAll(spec);
}
```

---

## 三、实战应用

### 3.1 事务管理

```java
@Service
public class OrderService {

    @Transactional(
        propagation = Propagation.REQUIRED,      // 传播行为
        isolation = Isolation.READ_COMMITTED,     // 隔离级别
        timeout = 30,                             // 超时时间（秒）
        readOnly = false,                         // 是否只读
        rollbackFor = Exception.class             // 回滚的异常类型
    )
    public void createOrder(OrderRequest request) {
        // 业务逻辑
    }
}
```

**传播行为：**

| 传播行为 | 说明 |
|---------|------|
| `REQUIRED`（默认） | 有事务则加入，无则新建 |
| `REQUIRES_NEW` | 总是新建事务，挂起当前事务 |
| `SUPPORTS` | 有事务则加入，无则非事务执行 |
| `NOT_SUPPORTED` | 非事务执行，挂起当前事务 |
| `MANDATORY` | 必须有事务，否则抛异常 |
| `NEVER` | 必须没有事务，否则抛异常 |
| `NESTED` | 嵌套事务（需要 Savepoint 支持） |

**隔离级别：**

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---------|------|----------|------|
| `READ_UNCOMMITTED` | 可能 | 可能 | 可能 |
| `READ_COMMITTED` | 不可能 | 可能 | 可能 |
| `REPEATABLE_READ`（MySQL 默认） | 不可能 | 不可能 | 可能 |
| `SERIALIZABLE` | 不可能 | 不可能 | 不可能 |

### 3.2 审计功能

JPA 审计功能通过监听器自动记录实体的创建时间、修改时间、创建人、修改人，无需在每个 Service 方法中手动 set 这些字段。

```java
@EntityListeners(AuditingEntityListener.class)
@MappedSuperclass
public abstract class BaseEntity {
    @CreatedDate
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @CreatedBy
    private String createdBy;

    @LastModifiedBy
    private String updatedBy;
}

// 启动类添加 @EnableJpaAuditing
@SpringBootApplication
@EnableJpaAuditing
public class Application { }
```

**审计功能完整配置（含 AuditorAware 获取当前用户）：**

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.domain.AuditorAware;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

import java.util.Optional;

@Configuration
@EnableJpaAuditing(auditorAwareRef = "auditorProvider")
public class JpaAuditingConfig {

    /**
     * 提供当前操作人信息（用于 @CreatedBy / @LastModifiedBy 自动填充）
     * 集成 Spring Security 时从 SecurityContext 获取当前登录用户
     */
    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> {
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            if (auth == null || !auth.isAuthenticated() || "anonymousUser".equals(auth.getPrincipal())) {
                return Optional.of("system");  // 系统自动任务（无登录用户）
            }
            return Optional.of(auth.getName());
        };
    }
}
```

**审计注解详解：**

| 注解 | 触发时机 | 字段类型 | 典型用途 |
|------|----------|----------|----------|
| `@CreatedDate` | INSERT 时 | `LocalDateTime` | 记录创建时间 |
| `@LastModifiedDate` | INSERT 和 UPDATE 时 | `LocalDateTime` | 记录最后修改时间 |
| `@CreatedBy` | INSERT 时 | `String` / `Long` | 记录创建人（需配 `AuditorAware`） |
| `@LastModifiedBy` | INSERT 和 UPDATE 时 | `String` / `Long` | 记录最后修改人 |
| `@EntityListeners` | 类级别 | 指定监听器类 | 绑定 `AuditingEntityListener` |
| `@MappedSuperclass` | 类级别 | 标注基类 | 让子类继承审计字段映射 |

**审计与其他生命周期回调对比：**

| 机制 | 触发时机 | 典型场景 |
|------|----------|----------|
| JPA 审计（`@CreatedDate` 等） | persist/update 自动触发 | 自动填充时间、操作人 |
| `@PrePersist` / `@PreUpdate` | 实体持久化前手动回调 | 自定义逻辑（如生成业务编号、数据校验） |
| `@PostPersist` / `@PostUpdate` | 实体持久化后回调 | 发送事件、清理缓存 |
| 数据库触发器 | 数据库层面 | 强一致性审计（绕过应用层也能记录） |

> **审计避坑**：`@CreatedBy` / `@LastModifiedBy` 必须配合 `AuditorAware` Bean 才能工作，否则字段为 null；审计字段通常放在 `@MappedSuperclass` 基类中，所有实体继承复用；如使用 Hibernate 的 `@CreationTimestamp` / `@UpdateTimestamp`，是 Hibernate 专属注解（非 JPA 标准），与 Spring Data 审计二选一，不要混用。

---

## 四、常见面试题（附答案）

### 1. JPA 中的 N+1 问题是什么？如何解决？

**N+1 问题：** 查询主表时执行 1 次查询，遍历结果访问关联属性时，每次触发 1 次查询，总共 N+1 次。**解决方案：** ① JOIN FETCH（`@Query` 中写 `JOIN FETCH`）② `@EntityGraph` ③ `@BatchSize` 批量加载。

### 2. fetch = LAZY 和 EAGER 的区别？

LAZY（懒加载）在访问关联属性时才查询，可以减少不必要的查询，但需要注意会话关闭后的 `LazyInitializationException`。EAGER（急加载）在查询主实体时立即查询关联实体，可能导致不必要的 JOIN，影响性能。一般推荐使用 LAZY，需要时通过 JOIN FETCH 显式加载。

### 3. @Transactional 的传播行为有哪些？

REQUIRED（默认，有则加入无则新建）、REQUIRES_NEW（总是新建）、SUPPORTS、NOT_SUPPORTED、MANDATORY、NEVER、NESTED（嵌套事务）。最常用的是 REQUIRED 和 REQUIRES_NEW。

### 4. JPA 和 MyBatis 的区别？

| 维度 | JPA | MyBatis |
|------|-----|---------|
| 定位 | 全自动 ORM | 半自动 ORM |
| SQL 控制 | 自动生成 SQL | 手动编写 SQL |
| 学习成本 | 较高（需理解实体关系映射） | 较低（会 SQL 即可上手） |
| 复杂查询 | JPQL/Criteria API | 原生 SQL（灵活） |
| 适用场景 | 标准 CRUD 为主的场景 | 复杂查询、报表、多表关联 |

### 5. 如何避免 LazyInitializationException？

1. 在事务内访问懒加载属性（`@Transactional` 方法内）
2. 使用 `JOIN FETCH` 或 `@EntityGraph` 在查询时预加载
3. 配置 `spring.jpa.open-in-view=true`（不推荐，会导致长事务）
4. 使用 DTO 投影，只查询需要的字段

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 生产环境开启 OSIV | 连接池耗尽 | OSIV 在请求处理期间保持数据库连接，高并发时连接无法释放 | 关闭 OSIV（`spring.jpa.open-in-view: false`），在 @Transactional 方法内访问懒加载属性 |
| JPA 实体 equals/hashCode 未正确重写 | Set 集合中出现重复元素，或关联查询异常 | 使用 @GeneratedValue 时 id 在 persist 前为 null，导致 hashCode 不一致 | id 为 null 时使用 Object.equals；hashCode 返回固定值（getClass().hashCode()） |
| 双向关联 JSON 序列化无限递归 | 接口返回 JSON 时报 StackOverflowError | User 有 orders，Order 有 user，JSON 序列化时互相引用形成循环 | 使用 @JsonIgnore 忽略一方；使用 @JsonManagedReference/@JsonBackReference；使用 DTO 避免循环引用 |
## 本章学习自检

完成本章学习后，应该能够：
- [ ] 用自己的话解释 JPA 核心注解、关联关系映射、N+1 问题及解决方案、事务传播行为与隔离级别
- [ ] 手写 JPA 实体映射（@OneToMany / @ManyToOne）、JOIN FETCH 查询、Specification 动态查询
- [ ] 回答常见面试题（N+1 问题、LAZY vs EAGER、传播行为、JPA vs MyBatis 区别等）
- [ ] 在实战项目中应用 JPA 进行数据访问层开发
- [ ] 识别并避免常见错误（LazyInitializationException、OSIV 配置陷阱、双向关联 JSON 序列化循环等）

---

> **学习导航**：
> - 返回 [学习路线总览](../../README.md)
> - 本模块其他文件：[03-MyBatis原生框架](./03-MyBatis原生框架.md) | [05-MyBatis-Plus实战](./05-MyBatis-Plus实战.md)
> - 关联模块：[01-MySQL基础与SQL核心](../../01-java-basics/mysql-jdbc/01-MySQL基础与SQL核心.md) | [02-JDBC核心原理](../../01-java-basics/mysql-jdbc/02-JDBC核心原理.md) | [06-MySQL深度优化](../../03-distributed-microservices/mysql-advanced/06-MySQL深度优化.md) | [07-数据库笔面试题集](../../03-distributed-microservices/mysql-advanced/07-数据库笔面试题集.md)
> - 实战应用：[电商订单实时统计分析平台](../../extensions/project/01-电商订单实时统计分析平台.md)

