# 04-数据库与 ORM

> 模块：09-nodejs（第9周 Node.js）
> 重点：SQL 核心概念、NoSQL 与 Redis、ORM 工具链
> 难度：★★★★★

---

## 一、核心概念

在 Node.js 后端开发中，数据库是持久化存储的核心组件。根据数据模型的不同，数据库可以分为三大类：

1. **关系型数据库（RDBMS）**：MySQL、PostgreSQL。数据以表（Table）为单位组织，表之间通过外键建立关联。使用 SQL（Structured Query Language）进行数据操作，强调数据一致性和完整性（ACID）。
2. **NoSQL 数据库**：MongoDB。数据以文档（Document）为单位组织，文档存储在集合（Collection）中。Schema 灵活，适合非结构化或半结构化数据的快速迭代场景。
3. **缓存数据库**：Redis。数据存储在内存中，读写速度极快（微秒级）。通常用作缓存层、消息队列或分布式锁，以减轻关系型数据库的压力。

ORM（Object-Relational Mapping）是连接 Node.js 应用与关系型数据库的桥梁，它将数据库表映射为 JavaScript 对象，让开发者可以用面向对象的方式操作数据库，而无需手写 SQL。

---

## 二、底层原理

### 2.1 关系型数据库基础

#### 2.1.1 表结构设计

关系型数据库的核心是"表"。表由行（Row）和列（Column）组成，每一行代表一条记录，每一列代表一个字段。表结构设计的关键在于**数据类型选择**、**约束定义**和**规范化**。

```sql
-- 用户表
CREATE TABLE users (
  id          INT AUTO_INCREMENT PRIMARY KEY,  -- 主键，自增
  username    VARCHAR(50)  NOT NULL UNIQUE,    -- 用户名，唯一
  email       VARCHAR(100) NOT NULL UNIQUE,    -- 邮箱，唯一
  password    VARCHAR(255) NOT NULL,           -- 密码哈希
  role        ENUM('user', 'admin') DEFAULT 'user',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 文章表（与用户表关联）
CREATE TABLE posts (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  title       VARCHAR(200) NOT NULL,
  content     TEXT,
  status      ENUM('draft', 'published') DEFAULT 'draft',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**常见数据类型对比**：

| 类型 | MySQL | PostgreSQL | 说明 |
|------|-------|-----------|------|
| 整数 | `INT` / `BIGINT` | `INTEGER` / `BIGINT` | 自增主键常用 |
| 字符串 | `VARCHAR(N)` / `TEXT` | `VARCHAR(N)` / `TEXT` | VARCHAR 有长度限制，TEXT 无 |
| 布尔 | `TINYINT(1)` / `BOOLEAN` | `BOOLEAN` | MySQL 的 BOOLEAN 是 TINYINT(1) 的别名 |
| 日期时间 | `DATETIME` / `TIMESTAMP` | `TIMESTAMP` / `TIMESTAMPTZ` | TIMESTAMP 带时区，DATETIME 不带 |
| 枚举 | `ENUM('a', 'b')` | 自定义枚举类型 | 限制字段只能取指定值 |
| JSON | `JSON` | `JSONB` / `JSON` | PostgreSQL 的 JSONB 支持索引 |
| 浮点数 | `DECIMAL(M, D)` | `NUMERIC(M, D)` | 金额等精确计算场景用 DECIMAL |

#### 2.1.2 SQL 增删改查（CRUD）

```sql
-- ====== 增（INSERT）======
-- 单条插入
INSERT INTO users (username, email, password)
VALUES ('zhangsan', 'zhangsan@example.com', 'hashed_password');

-- 批量插入
INSERT INTO users (username, email, password) VALUES
  ('lisi', 'lisi@example.com', 'hashed_pwd_1'),
  ('wangwu', 'wangwu@example.com', 'hashed_pwd_2');

-- ====== 删（DELETE）======
-- 条件删除
DELETE FROM users WHERE id = 3;

-- 软删除（推荐）：添加 deleted_at 字段，不物理删除
UPDATE users SET deleted_at = NOW() WHERE id = 3;

-- ====== 改（UPDATE）======
-- 更新单条记录
UPDATE users SET email = 'new_email@example.com' WHERE id = 1;

-- 批量更新
UPDATE users SET role = 'admin' WHERE id IN (1, 2, 3);

-- ====== 查（SELECT）======
-- 基础查询
SELECT * FROM users WHERE role = 'admin';

-- 指定字段
SELECT id, username, email FROM users;

-- 排序
SELECT * FROM posts ORDER BY created_at DESC;

-- 分页（LIMIT + OFFSET）
SELECT * FROM posts ORDER BY id DESC LIMIT 10 OFFSET 20;

-- 聚合查询
SELECT user_id, COUNT(*) AS post_count
FROM posts
GROUP BY user_id
HAVING post_count > 5;  -- HAVING 过滤聚合结果，WHERE 过滤原始行

-- 子查询
SELECT * FROM users
WHERE id IN (SELECT user_id FROM posts WHERE status = 'published');
```

#### 2.1.3 索引

索引是数据库表中一列或多列的值进行排序的一种数据结构，用于加速数据检索。如果把数据库比作一本字典，索引就是字典的目录。

```sql
-- 创建索引
CREATE INDEX idx_users_email ON users(email);           -- 普通索引
CREATE UNIQUE INDEX idx_users_username ON users(username); -- 唯一索引
CREATE INDEX idx_posts_user_status ON posts(user_id, status); -- 复合索引（多列）

-- 查看索引
SHOW INDEX FROM users;

-- 删除索引
DROP INDEX idx_users_email ON users;
```

**索引使用原则**：

| 原则 | 说明 |
|------|------|
| 最左前缀原则 | 复合索引中，查询条件必须从索引的最左列开始匹配，否则索引失效 |
| 避免在索引列上使用函数 | `WHERE YEAR(created_at) = 2024` 会导致索引失效 |
| 避免前导模糊查询 | `WHERE name LIKE '%keyword'` 无法使用索引，`LIKE 'keyword%'` 可以 |
| 高选择性列优先 | 值分布越分散的列（如邮箱），索引效果越好；性别等低选择性列不适合建索引 |
| 覆盖索引 | 查询的字段全部在索引中时，无需回表查询，性能最优 |

**EXPLAIN 分析查询**：

```sql
-- 使用 EXPLAIN 查看查询执行计划
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- 关注字段：
-- type: 连接类型（const > eq_ref > ref > range > index > ALL，越靠左越好）
-- possible_keys: 可能使用的索引
-- key: 实际使用的索引
-- rows: 扫描行数估算（越少越好）
-- Extra: 额外信息（Using index 表示覆盖索引，Using filesort 表示需要额外排序）
```

### 2.2 SQL 核心概念

#### 2.2.1 JOIN 类型

JOIN 用于将两个或多个表中相关联的行组合起来。理解 JOIN 的关键是使用**集合论**的视角：将每张表视为一个集合，JOIN 就是集合之间的运算。

```sql
-- 准备测试数据
-- users 表：id=1(张三), id=2(李四), id=3(王五), id=4(赵六，无文章)
-- posts 表：user_id=1(文章A), user_id=1(文章B), user_id=2(文章C), user_id=5(无用户)
```

**五种 JOIN 类型详解**：

```
INNER JOIN（内连接）
┌─────────────────────────┐
│ 返回两个表中匹配的行      │
│   ┌──────┐  ┌──────┐    │
│   │ A ∩ B│  │      │    │
│   └──────┘  └──────┘    │
└─────────────────────────┘

LEFT JOIN（左外连接）
┌──────────────────────────────┐
│ 返回左表所有行 + 右表匹配行    │
│   ┌──────────┐┌──────┐       │
│   │    A     ││  B   │       │
│   └──────────┘└──────┘       │
│ 右表无匹配时填充 NULL          │
└──────────────────────────────┘

RIGHT JOIN（右外连接）
┌──────────────────────────────┐
│ 返回右表所有行 + 左表匹配行    │
│   ┌──────┐┌──────────┐       │
│   │  A   ││    B     │       │
│   └──────┘└──────────┘       │
│ 左表无匹配时填充 NULL          │
└──────────────────────────────┘

FULL JOIN（全外连接）
┌──────────────────────────┐
│ 返回两表所有行             │
│   ┌──────────────┐       │
│   │   A  ∪  B    │       │
│   └──────────────┘       │
│ 无匹配时填充 NULL          │
└──────────────────────────┘
```

```sql
-- INNER JOIN：只返回两表都有匹配的行
SELECT u.username, p.title
FROM users u
INNER JOIN posts p ON u.id = p.user_id;
-- 结果：张三-文章A, 张三-文章B, 李四-文章C
-- 王五和赵六不出现在结果中

-- LEFT JOIN：返回左表所有行，右表无匹配时填充 NULL
SELECT u.username, p.title
FROM users u
LEFT JOIN posts p ON u.id = p.user_id;
-- 结果：张三-文章A, 张三-文章B, 李四-文章C, 王五-NULL, 赵六-NULL

-- RIGHT JOIN：返回右表所有行，左表无匹配时填充 NULL
SELECT u.username, p.title
FROM users u
RIGHT JOIN posts p ON u.id = p.user_id;
-- 结果：张三-文章A, 张三-文章B, 李四-文章C, NULL-文章D(user_id=5)

-- FULL JOIN：返回两表所有行（MySQL 不直接支持，用 UNION 模拟）
SELECT u.username, p.title
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
UNION
SELECT u.username, p.title
FROM users u
RIGHT JOIN posts p ON u.id = p.user_id;
-- 结果：所有用户和所有文章，无匹配处填充 NULL
```

**JOIN 类型对比**：

| JOIN 类型 | 返回结果 | 无匹配时 | 常见场景 |
|-----------|---------|---------|---------|
| INNER JOIN | 两表匹配的行 | 丢弃不匹配的行 | 查询"有文章的用户" |
| LEFT JOIN | 左表全部 + 右表匹配 | 右表填充 NULL | 查询"所有用户及其文章（含无文章的用户）" |
| RIGHT JOIN | 右表全部 + 左表匹配 | 左表填充 NULL | 查询"所有文章及其作者"（较少使用） |
| CROSS JOIN | 笛卡尔积（N x M 行） | 无过滤 | 生成所有组合（如规格 SKU 组合） |
| FULL JOIN | 两表全部行 | 无匹配处填充 NULL | 查询"所有用户和所有文章" |

#### 2.2.2 事务 ACID

事务是一组不可分割的数据库操作，要么全部成功，要么全部失败回滚。事务的四个特性（ACID）是关系型数据库保证数据一致性的基石：

| 特性 | 全称 | 含义 | 生活类比 |
|------|------|------|---------|
| **A** - 原子性 | Atomicity | 事务中的操作要么全部成功，要么全部失败 | 银行转账：扣款和到账必须同时成功，不能只扣款不到账 |
| **C** - 一致性 | Consistency | 事务前后数据必须满足所有约束（外键、唯一性等） | 转账后，两个账户的总金额必须与转账前相同 |
| **I** - 隔离性 | Isolation | 并发事务之间互不干扰，各自看到的数据一致 | 两个用户同时购买最后一件库存，只能有一个人成功 |
| **D** - 持久性 | Durability | 事务提交后，数据永久保存，即使系统崩溃也不丢失 | 转账成功后，即使银行系统崩溃，记录也不会丢失 |

```sql
-- 事务示例：转账操作
START TRANSACTION;

-- 步骤1：检查余额
SELECT balance FROM accounts WHERE id = 1;
-- 假设余额为 1000

-- 步骤2：扣款
UPDATE accounts SET balance = balance - 500 WHERE id = 1;

-- 步骤3：到账
UPDATE accounts SET balance = balance + 500 WHERE id = 2;

-- 步骤4：记录流水
INSERT INTO transactions (from_id, to_id, amount) VALUES (1, 2, 500);

-- 提交事务（全部成功）
COMMIT;

-- 如果任何步骤失败，回滚所有操作
-- ROLLBACK;
```

**事务隔离级别**：

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|---------|------|----------|------|------|
| READ UNCOMMITTED（读未提交） | 是 | 是 | 是 | 最高 |
| READ COMMITTED（读已提交） | 否 | 是 | 是 | 较高 |
| REPEATABLE READ（可重复读） | 否 | 否 | 是（MySQL 通过 MVCC 避免） | 中等 |
| SERIALIZABLE（串行化） | 否 | 否 | 否 | 最低 |

MySQL 默认隔离级别为 **REPEATABLE READ**，PostgreSQL 默认为 **READ COMMITTED**。

```sql
-- 查看当前隔离级别
SELECT @@transaction_isolation;          -- MySQL 5.7.20+ / 8.0+
SELECT @@tx_isolation;                   -- MySQL 5.7

-- 设置隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

**并发问题说明**：

- **脏读**：事务 A 读取了事务 B 未提交的修改，事务 B 回滚后，事务 A 读到的数据是"脏"的
- **不可重复读**：事务 A 内两次读取同一行数据，期间事务 B 修改了该行并提交，导致两次读取结果不一致
- **幻读**：事务 A 内两次查询同一范围的数据，期间事务 B 插入了新行并提交，导致第二次查询"多出"了行

#### 2.2.3 索引类型

不同数据库引擎和场景适用不同的索引类型：

| 索引类型 | 数据结构 | 适用场景 | 限制 |
|---------|---------|---------|------|
| B-Tree（默认） | 平衡多路搜索树 | 等值查询、范围查询、排序 | 前导模糊查询 `LIKE '%x'` 失效 |
| Hash 索引 | 哈希表 | 精确等值查询（`=`、`IN`） | 不支持范围查询和排序 |
| 全文索引（FULLTEXT） | 倒排索引 | 文本搜索（`MATCH...AGAINST`） | 仅 InnoDB 5.6+ 和 MyISAM 支持 |
| 空间索引（R-Tree） | R 树 | 地理位置查询（GIS） | 仅 MyISAM 支持 |
| 唯一索引（UNIQUE） | B-Tree | 强制列值唯一 | 允许 NULL（MySQL 允许多个 NULL） |

```sql
-- B-Tree 索引（默认类型）
CREATE INDEX idx_name ON users(username);

-- 全文索引
CREATE FULLTEXT INDEX idx_content ON posts(title, content);

-- 全文搜索
SELECT * FROM posts
WHERE MATCH(title, content) AGAINST('Node.js 数据库' IN NATURAL LANGUAGE MODE);

-- 唯一索引（同时也是约束）
CREATE UNIQUE INDEX idx_email ON users(email);
```

**B-Tree 与 B+Tree 的区别**：

| 特性 | B-Tree | B+Tree |
|------|--------|--------|
| 数据存储 | 所有节点都存储数据 | 只有叶子节点存储数据，非叶子节点只存索引 |
| 叶子节点连接 | 无连接 | 叶子节点通过指针连接成链表 |
| 范围查询 | 需要中序遍历 | 直接在叶子节点链表上遍历，效率更高 |
| 使用情况 | 早期数据库 | **MySQL InnoDB 等主流引擎使用 B+Tree** |

> 📖 **参考链接**：
> - [MySQL 官方文档](https://dev.mysql.com/doc/)
> - [MySQL 官方文档 - EXPLAIN 输出格式](https://dev.mysql.com/doc/refman/8.0/en/explain-output.html)

### 2.3 NoSQL 数据库基础（MongoDB）

MongoDB 是一个面向文档的 NoSQL 数据库，数据以 BSON（Binary JSON）格式存储。与传统关系型数据库不同，MongoDB 没有固定的表结构，同一集合中的文档可以有不同的字段。

#### 2.3.1 关系型 vs MongoDB 术语对照

| 关系型数据库 | MongoDB | 说明 |
|-------------|---------|------|
| Database | Database | 数据库 |
| Table | Collection | 集合（表） |
| Row | Document | 文档（行） |
| Column | Field | 字段（列） |
| Primary Key | `_id`（自动生成 ObjectId） | 主键 |
| JOIN | `$lookup`（聚合管道） | 关联查询 |
| Index | Index | 索引 |

```javascript
const { MongoClient } = require('mongodb');

const client = new MongoClient('mongodb://localhost:27017');
await client.connect();
const db = client.db('myapp');

// 获取集合
const users = db.collection('users');

// 插入文档
await users.insertOne({
  username: 'zhangsan',
  email: 'zhangsan@example.com',
  profile: {
    age: 28,
    city: '北京',
  },
  tags: ['nodejs', 'mongodb'],
  createdAt: new Date(),
});

// 查询文档
const user = await users.findOne({ username: 'zhangsan' });
const admins = await users.find({ role: 'admin' }).toArray();

// 更新文档
await users.updateOne(
  { username: 'zhangsan' },
  { $set: { 'profile.age': 29 }, $push: { tags: 'javascript' } }
);

// 删除文档
await users.deleteOne({ username: 'zhangsan' });
```

#### 2.3.2 聚合管道（Aggregation Pipeline）

聚合管道是 MongoDB 中最强大的数据处理工具，它将文档依次通过多个阶段（Stage），每个阶段对文档进行转换或过滤，最终输出处理结果。

```
输入文档 → $match → $group → $sort → $project → 输出结果
```

```javascript
// 聚合管道示例：统计每个用户的文章数量，并按数量降序排列
const result = await db.collection('posts').aggregate([
  // 阶段1：过滤已发布的文章
  { $match: { status: 'published' } },

  // 阶段2：按用户分组，统计文章数
  { $group: {
    _id: '$user_id',
    postCount: { $sum: 1 },
    avgViews: { $avg: '$views' },
  }},

  // 阶段3：排序
  { $sort: { postCount: -1 } },

  // 阶段4：关联用户信息
  { $lookup: {
    from: 'users',
    localField: '_id',
    foreignField: '_id',
    as: 'userInfo',
  }},

  // 阶段5：展开 userInfo 数组
  { $unwind: '$userInfo' },

  // 阶段6：选择输出字段
  { $project: {
    _id: 0,
    username: '$userInfo.username',
    postCount: 1,
    avgViews: 1,
  }},
]).toArray();
```

**常用聚合阶段**：

| 阶段 | 作用 | 类比 SQL |
|------|------|---------|
| `$match` | 过滤文档 | `WHERE` |
| `$group` | 分组聚合 | `GROUP BY` |
| `$sort` | 排序 | `ORDER BY` |
| `$project` | 选择/重命名字段 | `SELECT` |
| `$limit` / `$skip` | 分页 | `LIMIT` / `OFFSET` |
| `$lookup` | 关联查询（左外连接） | `LEFT JOIN` |
| `$unwind` | 展开数组字段 | 无直接对应 |
| `$addFields` | 添加新字段 | 计算列 |

#### 2.3.3 MongoDB 索引

```javascript
// 单字段索引
await users.createIndex({ email: 1 }); // 1 表示升序

// 复合索引
await users.createIndex({ role: 1, createdAt: -1 });

// 唯一索引
await users.createIndex({ username: 1 }, { unique: true });

// 文本索引
await posts.createIndex({ title: 'text', content: 'text' });

// 查看查询执行计划
await users.find({ email: 'test@example.com' }).explain('executionStats');
```

### 2.4 缓存数据库（Redis）

Redis（Remote Dictionary Server）是一个开源的**内存数据库**，所有数据存储在内存中，读写速度极快（微秒级）。它支持多种数据结构，不仅是简单的 key-value 存储。

#### 2.4.1 Redis 核心数据结构

| 数据结构 | 底层实现 | 典型应用场景 |
|---------|---------|-------------|
| **String（字符串）** | SDS（简单动态字符串） | 缓存 JSON 数据、计数器、分布式锁 |
| **Hash（哈希）** | 压缩列表 / 哈希表 | 存储对象（如用户信息）、购物车 |
| **List（列表）** | 双向链表 / 压缩列表 | 消息队列、最新动态列表、时间线 |
| **Set（集合）** | 整数集合 / 哈希表 | 标签系统、共同好友、去重 |
| **Sorted Set（有序集合）** | 压缩列表 / 跳表 | 排行榜、延迟队列、带权重的标签 |
| **Stream（流）** | Rax 树（基数树） | 消息队列（支持消费者组） |

```javascript
const Redis = require('ioredis');
const redis = new Redis({
  host: 'localhost',
  port: 6379,
});

// ====== String 操作 ======
await redis.set('user:1', JSON.stringify({ name: '张三', age: 28 }));
await redis.setex('token:abc123', 3600, 'valid'); // 带过期时间
const user = JSON.parse(await redis.get('user:1'));

// 计数器（原子操作）
await redis.incr('page:views');       // 浏览量 +1
await redis.incrby('user:score', 10); // 积分 +10

// ====== Hash 操作 ======
await redis.hset('user:profile:1', 'name', '张三');
await redis.hset('user:profile:1', 'age', '28');
await redis.hset('user:profile:2', {
  name: '李四',
  age: '30',
  city: '上海',
});
const profile = await redis.hgetall('user:profile:1');

// ====== List 操作 ======
await redis.lpush('news:latest', '新闻1', '新闻2', '新闻3'); // 左侧插入
await redis.rpush('task:queue', JSON.stringify({ type: 'email', to: 'user@ex.com' }));
const latest = await redis.lrange('news:latest', 0, 9); // 获取最近 10 条

// ====== Set 操作 ======
await redis.sadd('user:1:tags', 'nodejs', 'redis', 'mongodb');
await redis.sadd('user:2:tags', 'nodejs', 'python', 'docker');
// 取交集（共同标签）
const common = await redis.sinter('user:1:tags', 'user:2:tags');

// ====== Sorted Set 操作 ======
await redis.zadd('rank:score', 95, 'player:1');
await redis.zadd('rank:score', 88, 'player:2');
await redis.zadd('rank:score', 92, 'player:3');
// 获取排名前 10
const top10 = await redis.zrevrange('rank:score', 0, 9, 'WITHSCORES');
```

#### 2.4.2 Redis 过期策略

Redis 使用两种过期策略协同工作：

| 策略 | 机制 | 说明 |
|------|------|------|
| **惰性删除** | 访问 key 时检查是否过期，过期则删除 | 对 CPU 友好，但可能残留大量过期 key 占用内存 |
| **定期删除** | 每 100ms 随机抽取一批 key 检查并删除过期 key | 平衡 CPU 和内存，但可能漏删 |

**内存淘汰策略**（当内存达到 `maxmemory` 时）：

| 策略 | 行为 |
|------|------|
| `noeviction`（默认） | 不淘汰，写入操作返回错误 |
| `allkeys-lru` | 在所有 key 中淘汰最近最少使用的（LRU） |
| `allkeys-lfu` | 在所有 key 中淘汰最不频繁使用的（LFU） |
| `allkeys-random` | 在所有 key 中随机淘汰 |
| `volatile-lru` | 在设置了过期时间的 key 中淘汰 LRU |
| `volatile-lfu` | 在设置了过期时间的 key 中淘汰 LFU |
| `volatile-ttl` | 在设置了过期时间的 key 中淘汰 TTL 最短的 |

```bash
# redis.conf 配置
maxmemory 2gb
maxmemory-policy allkeys-lru
```

#### 2.4.3 缓存穿透、击穿、雪崩

这是 Redis 缓存使用中最常见的三个问题：

| 问题 | 现象 | 原因 | 解决方案 |
|------|------|------|---------|
| **缓存穿透** | 查询不存在的数据，请求直接打到数据库 | 缓存和数据库中都没有该数据 | 布隆过滤器、缓存空值（设置短过期时间）、参数校验 |
| **缓存击穿** | 热点 key 过期瞬间，大量请求直接打到数据库 | 热点 key 过期 + 高并发 | 互斥锁（只让一个请求去加载数据）、永不过期（逻辑过期 + 异步更新） |
| **缓存雪崩** | 大量 key 同时过期，数据库压力骤增 | 缓存集中过期 | 过期时间加随机值（打散）、多级缓存、限流降级 |

```javascript
// 缓存穿透解决方案：缓存空值
async function getUserById(id) {
  const cacheKey = `user:${id}`;
  const cached = await redis.get(cacheKey);

  if (cached !== null) {
    return cached === '__NULL__' ? null : JSON.parse(cached);
  }

  const user = await db.query('SELECT * FROM users WHERE id = ?', [id]);

  if (user) {
    await redis.setex(cacheKey, 3600, JSON.stringify(user));
  } else {
    // 缓存空值，防止缓存穿透，短过期时间
    await redis.setex(cacheKey, 60, '__NULL__');
  }

  return user;
}

// 缓存击穿解决方案：互斥锁
async function getHotData(key) {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const lockKey = `lock:${key}`;
  // 使用 SETNX 实现分布式锁
  const locked = await redis.set(lockKey, '1', 'EX', 10, 'NX');

  if (locked) {
    try {
      // 双重检查
      const recheck = await redis.get(key);
      if (recheck) return JSON.parse(recheck);

      const data = await db.query('SELECT * FROM hot_table WHERE ...');
      await redis.setex(key, 3600, JSON.stringify(data));
      return data;
    } finally {
      await redis.del(lockKey);
    }
  } else {
    // 未获取锁，等待后重试
    await new Promise(resolve => setTimeout(resolve, 100));
    return getHotData(key);
  }
}
```

> 📖 **参考链接**：
> - [Redis 官方文档](https://redis.io/docs/)
> - [Redis 官方命令参考](https://redis.io/commands/)

### 2.5 ORM 工具

ORM 将数据库表映射为 JavaScript 类/对象，让开发者可以面向对象地操作数据库。Node.js 生态中三大主流 ORM 分别是 Prisma、TypeORM 和 Sequelize。

#### 2.5.1 三大 ORM 对比

| 对比维度 | Prisma | TypeORM | Sequelize |
|---------|--------|---------|-----------|
| 发布时间 | 2020 | 2016 | 2011 |
| 类型安全 | 原生 TypeScript，自动生成类型 | TypeScript 优先，装饰器风格 | TypeScript 支持，但类型推断较弱 |
| Schema 定义 | 专用 `.prisma` 文件（DSL） | 装饰器（`@Entity`、`@Column`） | `sequelize.define()` 或 `Model.init()` |
| 迁移工具 | 内置 `prisma migrate` | 内置 `typeorm migration` | 内置 `sequelize-cli` |
| 查询构建 | Prisma Client（类型安全的查询 API） | QueryBuilder + Repository | Query 方法 + Sequelize 查询语法 |
| 关联查询 | `include` 语法简洁 | `relations` 配置灵活 | `include` 语法（需手动处理嵌套） |
| 学习曲线 | 低（DSL 直观，工具链完善） | 中（装饰器模式，概念较多） | 中（API 风格传统，文档丰富） |
| 性能 | Prisma Client 引擎（Rust） | 原生 JS 实现 | 原生 JS 实现 |
| 社区活跃度 | 快速增长（GitHub 50k+ stars） | 活跃（GitHub 35k+ stars） | 成熟但增速放缓（GitHub 30k+ stars） |

#### 2.5.2 Prisma 详解

Prisma 是新一代 Node.js ORM，由 Schema 文件、Prisma Client 和 Prisma Migrate 三部分组成。

**Schema 定义（`prisma/schema.prisma`）**：

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "mysql"      // 支持 mysql, postgresql, sqlite, sqlserver, mongodb
  url      = env("DATABASE_URL")
}

model User {
  id        Int       @id @default(autoincrement())
  email     String    @unique
  username  String    @unique
  password  String
  role      Role      @default(USER)
  profile   Profile?  // 一对一关联
  posts     Post[]    // 一对多关联
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt

  @@map("users")      // 映射到数据库表名
}

model Profile {
  id        Int      @id @default(autoincrement())
  bio       String?
  avatar    String?
  userId    Int      @unique
  user      User     @relation(fields: [userId], references: [id])
}

model Post {
  id        Int       @id @default(autoincrement())
  title     String
  content   String?   @db.Text
  published Boolean   @default(false)
  author    User      @relation(fields: [authorId], references: [id])
  authorId  Int
  tags      Tag[]
  createdAt DateTime  @default(now())
}

model Tag {
  id    Int    @id @default(autoincrement())
  name  String @unique
  posts Post[]
}

enum Role {
  USER
  ADMIN
}
```

**迁移命令**：

```bash
# 生成迁移文件（根据 Schema 变化自动生成 SQL）
pnpm prisma migrate dev --name init

# 将迁移应用到数据库（生产环境）
pnpm prisma migrate deploy

# 查看迁移状态
pnpm prisma migrate status

# 生成 Prisma Client（根据 Schema 重新生成类型安全的客户端）
pnpm prisma generate
```

**Prisma Client 查询操作**：

```javascript
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

// ====== 增（Create）======
const user = await prisma.user.create({
  data: {
    email: 'zhangsan@example.com',
    username: 'zhangsan',
    password: 'hashed_password',
    profile: {
      create: { bio: '全栈开发者' },  // 同时创建关联的 Profile
    },
  },
  include: { profile: true },  // 返回时包含关联数据
});

// 批量创建
await prisma.user.createMany({
  data: [
    { email: 'a@ex.com', username: 'a', password: 'xxx' },
    { email: 'b@ex.com', username: 'b', password: 'xxx' },
  ],
});

// ====== 查（Read）======
// 单条查询
const user = await prisma.user.findUnique({
  where: { id: 1 },
  include: {
    posts: {
      where: { published: true },
      orderBy: { createdAt: 'desc' },
    },
    profile: true,
  },
});

// 列表查询（分页、排序、过滤）
const users = await prisma.user.findMany({
  where: {
    role: 'USER',
    posts: { some: { published: true } }, // 至少有一篇已发布文章
  },
  orderBy: { createdAt: 'desc' },
  skip: 0,    // 偏移量
  take: 10,   // 每页数量
  select: {   // 只选择需要的字段
    id: true,
    username: true,
    _count: { select: { posts: true } },  // 聚合计数
  },
});

// 聚合查询
const stats = await prisma.post.aggregate({
  where: { authorId: 1 },
  _count: { id: true },
  _avg: { viewCount: true },
  _sum: { likeCount: true },
});

// ====== 改（Update）======
const updated = await prisma.user.update({
  where: { id: 1 },
  data: {
    role: 'ADMIN',
    profile: {
      update: { bio: '高级全栈开发者' },
    },
  },
});

// 批量更新
await prisma.post.updateMany({
  where: { authorId: 1 },
  data: { published: true },
});

// Upsert（存在则更新，不存在则创建）
await prisma.user.upsert({
  where: { email: 'zhangsan@example.com' },
  update: { username: 'zhangsan_v2' },
  create: { email: 'zhangsan@example.com', username: 'zhangsan_v2', password: 'xxx' },
});

// ====== 删（Delete）======
await prisma.user.delete({ where: { id: 1 } });
await prisma.post.deleteMany({ where: { authorId: 1 } });

// ====== 事务 ======
const [newUser, newPost] = await prisma.$transaction([
  prisma.user.create({ data: { ... } }),
  prisma.post.create({ data: { ... } }),
]);

// 交互式事务
await prisma.$transaction(async (tx) => {
  const user = await tx.user.create({ data: { ... } });
  await tx.profile.create({ data: { userId: user.id, ... } });
});
```

#### 2.5.3 TypeORM 详解

TypeORM 使用装饰器模式定义实体，支持 Active Record 和 Data Mapper 两种模式。

```typescript
import { Entity, Column, PrimaryGeneratedColumn, OneToMany, OneToOne, JoinColumn, ManyToMany, JoinTable } from 'typeorm';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  email: string;

  @Column({ unique: true })
  username: string;

  @Column()
  password: string;

  @Column({ type: 'enum', enum: ['user', 'admin'], default: 'user' })
  role: 'user' | 'admin';

  @OneToOne(() => Profile, (profile) => profile.user)
  profile: Profile;

  @OneToMany(() => Post, (post) => post.author)
  posts: Post[];

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}

@Entity('posts')
export class Post {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  title: string;

  @Column({ type: 'text', nullable: true })
  content: string;

  @Column({ default: false })
  published: boolean;

  @ManyToOne(() => User, (user) => user.posts)
  author: User;

  @ManyToMany(() => Tag)
  @JoinTable()
  tags: Tag[];
}

@Entity('tags')
export class Tag {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  name: string;

  @ManyToMany(() => Post, (post) => post.tags)
  posts: Post[];
}
```

**TypeORM 查询操作（Data Mapper 模式）**：

```typescript
import { AppDataSource } from './data-source';

const userRepo = AppDataSource.getRepository(User);
const postRepo = AppDataSource.getRepository(Post);

// 查询
const user = await userRepo.findOne({
  where: { id: 1 },
  relations: ['posts', 'profile'],
});

// 带条件的关联查询
const posts = await postRepo.find({
  where: { author: { id: 1 }, published: true },
  relations: ['tags'],
  order: { createdAt: 'DESC' },
  skip: 0,
  take: 10,
});

// QueryBuilder 复杂查询
const result = await userRepo
  .createQueryBuilder('user')
  .leftJoinAndSelect('user.posts', 'post')
  .leftJoinAndSelect('user.profile', 'profile')
  .where('user.role = :role', { role: 'admin' })
  .andWhere('post.published = :published', { published: true })
  .orderBy('user.createdAt', 'DESC')
  .getMany();

// 事务
await AppDataSource.transaction(async (manager) => {
  const user = await manager.save(User, { ... });
  await manager.save(Post, { author: user, ... });
});
```

#### 2.5.4 Sequelize 详解

Sequelize 是 Node.js 中最老牌的 ORM，API 风格传统，文档丰富。

```javascript
const { Sequelize, DataTypes, Model } = require('sequelize');

const sequelize = new Sequelize('database', 'username', 'password', {
  host: 'localhost',
  dialect: 'mysql', // 'mysql' | 'postgres' | 'sqlite' | 'mssql'
  logging: false,   // 关闭 SQL 日志
});

// 模型定义
class User extends Model {}
User.init({
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  email: { type: DataTypes.STRING, unique: true, allowNull: false },
  username: { type: DataTypes.STRING, unique: true, allowNull: false },
  password: { type: DataTypes.STRING, allowNull: false },
  role: { type: DataTypes.ENUM('user', 'admin'), defaultValue: 'user' },
}, {
  sequelize,
  modelName: 'User',
  tableName: 'users',
  timestamps: true,
});

class Post extends Model {}
Post.init({
  id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
  title: { type: DataTypes.STRING, allowNull: false },
  content: { type: DataTypes.TEXT },
  published: { type: DataTypes.BOOLEAN, defaultValue: false },
}, {
  sequelize,
  modelName: 'Post',
  tableName: 'posts',
});

// 关联定义
User.hasMany(Post, { foreignKey: 'authorId', as: 'posts' });
Post.belongsTo(User, { foreignKey: 'authorId', as: 'author' });

// 查询（带关联）
const userWithPosts = await User.findByPk(1, {
  include: [{
    model: Post,
    as: 'posts',
    where: { published: true },
    required: false, // LEFT JOIN（false），INNER JOIN（true）
  }],
});

// 分页查询
const { rows, count } = await User.findAndCountAll({
  where: { role: 'user' },
  order: [['createdAt', 'DESC']],
  offset: 0,
  limit: 10,
});

// 事务
const t = await sequelize.transaction();
try {
  const user = await User.create({ ... }, { transaction: t });
  await Post.create({ authorId: user.id, ... }, { transaction: t });
  await t.commit();
} catch (error) {
  await t.rollback();
  throw error;
}
```

#### 2.5.5 ORM 关联关系总结

| 关联类型 | 数据库实现 | Prisma | TypeORM | Sequelize |
|---------|-----------|--------|---------|-----------|
| 一对一 | 外键 + UNIQUE 约束 | `User Profile?` | `@OneToOne` | `hasOne` / `belongsTo` |
| 一对多 | 外键在"多"方 | `User Post[]` | `@OneToMany` / `@ManyToOne` | `hasMany` / `belongsTo` |
| 多对多 | 中间表 | 隐式或显式中间表 | `@ManyToMany` + `@JoinTable` | `belongsToMany` |
| 自关联 | 外键指向同一张表 | 同一模型内自引用 | 同一实体内自引用 | 同一模型内自引用 |

> 📖 **参考链接**：
> - [Prisma 官方文档](https://www.prisma.io/docs/getting-started)
> - [TypeORM 官方文档](https://typeorm.io/)

---

## 三、实战应用

### 3.1 数据库连接池配置

连接池是数据库连接管理的核心，合理配置连接池可以显著提升性能。

```javascript
// Prisma 连接池配置
// prisma/schema.prisma
datasource db {
  provider = "mysql"
  url      = env("DATABASE_URL")
  // Prisma 5.x/6.x 连接池配置：
  // 1. 服务端环境（如 Node.js）：使用 Prisma Client 内置连接池，通过 connection_limit 参数配置
  //    DATABASE_URL="mysql://user:pass@localhost:3306/db?connection_limit=10"
  // 2. Serverless 环境：推荐使用 @prisma/client/edge + Data Proxy 或 Accelerate
  // 3. 连接池大小建议：`(核心数 * 2) + 有效磁盘数`
}

// TypeORM 连接池配置
// data-source.ts
const AppDataSource = new DataSource({
  type: 'mysql',
  host: 'localhost',
  port: 3306,
  username: 'root',
  password: 'password',
  database: 'myapp',
  pool: {
    max: 10,        // 最大连接数
    min: 2,         // 最小连接数
    idleTimeout: 30000,  // 空闲连接超时（毫秒）
  },
});

// Sequelize 连接池配置
const sequelize = new Sequelize('database', 'user', 'pass', {
  host: 'localhost',
  dialect: 'mysql',
  pool: {
    max: 10,        // 最大连接数
    min: 2,         // 最小连接数
    acquire: 30000, // 获取连接超时（毫秒）
    idle: 10000,    // 空闲连接超时（毫秒）
  },
});
```

**连接池大小计算公式**（经验值）：

```
连接池大小 = (核心数 * 2) + 有效磁盘数
例如：4 核 CPU + 1 块 SSD → 连接池大小 ≈ 9
```

> 📖 **参考链接**：
> - [MySQL 官方文档 - 连接池](https://dev.mysql.com/doc/refman/8.0/en/)
> - [Prisma 官方文档 - 数据库连接管理](https://www.prisma.io/docs/guides/performance-and-optimization)

### 3.2 Redis 缓存完整示例

```javascript
const Redis = require('ioredis');
const redis = new Redis({
  host: 'localhost',
  port: 6379,
  retryStrategy: (times) => Math.min(times * 50, 2000), // 重试策略
  maxRetriesPerRequest: 3,
});

// 带缓存的 API 查询（Cache-Aside 模式）
async function getArticles(page = 1, pageSize = 10) {
  const cacheKey = `articles:page:${page}:size:${pageSize}`;

  // 1. 先查缓存
  const cached = await redis.get(cacheKey);
  if (cached) {
    return { data: JSON.parse(cached), fromCache: true };
  }

  // 2. 缓存未命中，查数据库
  const articles = await db.query(
    'SELECT * FROM articles ORDER BY created_at DESC LIMIT ? OFFSET ?',
    [pageSize, (page - 1) * pageSize]
  );

  // 3. 写入缓存（带随机过期时间防雪崩）
  const ttl = 300 + Math.floor(Math.random() * 60); // 5 分钟 + 随机 0-60 秒
  await redis.setex(cacheKey, ttl, JSON.stringify(articles));

  return { data: articles, fromCache: false };
}

// 数据更新时主动清除缓存（Cache Invalidation）
async function updateArticle(id, data) {
  await db.query('UPDATE articles SET ? WHERE id = ?', [data, id]);

  // 删除相关缓存（按模式批量删除）
  const keys = await redis.keys('articles:page:*');
  if (keys.length > 0) {
    await redis.del(...keys);
  }
  // 删除单条缓存
  await redis.del(`article:${id}`);
}
```

### 3.3 Prisma + Redis 完整项目结构

```
project/
├── prisma/
│   ├── schema.prisma       # 数据模型定义
│   └── migrations/         # 迁移文件
├── src/
│   ├── lib/
│   │   ├── prisma.ts       # Prisma Client 单例
│   │   └── redis.ts        # Redis Client 单例
│   ├── services/
│   │   ├── user.service.ts # 用户服务（含缓存逻辑）
│   │   └── post.service.ts # 文章服务
│   ├── routes/
│   │   ├── user.routes.ts
│   │   └── post.routes.ts
│   └── app.ts
├── .env
└── package.json
```

```typescript
// src/lib/prisma.ts - Prisma Client 单例
import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

export const prisma = globalForPrisma.prisma || new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

// src/lib/redis.ts - Redis Client 单例
import Redis from 'ioredis';

const globalForRedis = globalThis as unknown as { redis: Redis };

export const redis = globalForRedis.redis || new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: Number(process.env.REDIS_PORT) || 6379,
  maxRetriesPerRequest: 3,
});

if (process.env.NODE_ENV !== 'production') globalForRedis.redis = redis;

// src/services/user.service.ts - 用户服务
import { prisma } from '../lib/prisma';
import { redis } from '../lib/redis';

export class UserService {
  async getUserById(id: number) {
    const cacheKey = `user:${id}`;
    const cached = await redis.get(cacheKey);
    if (cached) return JSON.parse(cached);

    const user = await prisma.user.findUnique({
      where: { id },
      include: { profile: true, _count: { select: { posts: true } } },
    });

    if (user) {
      await redis.setex(cacheKey, 600, JSON.stringify(user));
    }
    return user;
  }

  async updateUser(id: number, data: any) {
    const user = await prisma.user.update({ where: { id }, data });
    await redis.del(`user:${id}`); // 清除缓存
    return user;
  }
}
```

---

## 四、常见面试题

**Q1：SQL JOIN 中 INNER JOIN、LEFT JOIN、RIGHT JOIN、FULL JOIN 的区别？**

四种 JOIN 的区别在于"如何处理不匹配的行"：

- **INNER JOIN**：只返回两表都有匹配的行，无匹配的行直接丢弃。最常用，性能通常最好。
- **LEFT JOIN**：返回左表的所有行，右表无匹配时填充 NULL。用于"查询所有用户及他们的文章（含无文章的用户）"这类场景。
- **RIGHT JOIN**：返回右表的所有行，左表无匹配时填充 NULL。功能上等价于交换两表位置的 LEFT JOIN，实际使用较少。
- **FULL JOIN**：返回两表的所有行，任何一方无匹配都填充 NULL。MySQL 不直接支持，需用 `LEFT JOIN UNION RIGHT JOIN` 模拟。

**Q2：事务的 ACID 特性分别指什么？**

ACID 是关系型数据库保证数据一致性的四个核心特性：

- **原子性（Atomicity）**：事务中的操作是一个整体，要么全部成功，要么全部失败回滚。通过 undo log 实现。
- **一致性（Consistency）**：事务执行前后，数据必须满足所有约束（外键、唯一性、CHECK 等）。由原子性、隔离性、持久性共同保证。
- **隔离性（Isolation）**：并发事务之间互不干扰。通过锁机制和 MVCC（多版本并发控制）实现，有四种隔离级别。
- **持久性（Durability）**：事务提交后，数据永久保存，即使系统崩溃也不丢失。通过 redo log 实现。

**Q3：MySQL 索引的底层数据结构是什么？为什么不用哈希表或二叉树？**

MySQL InnoDB 引擎的索引底层使用 **B+Tree**（B+ 树）。选择 B+Tree 而非其他数据结构的原因：

- **不用哈希表**：哈希表虽然等值查询 O(1)，但不支持范围查询（`BETWEEN`、`>`、`<`）和排序（`ORDER BY`），而数据库中范围查询是常见需求。
- **不用二叉搜索树**：数据量增大时树的高度会很高（如 100 万条数据，树高约 20），导致磁盘 I/O 次数多。B+Tree 每个节点可存储多个 key，树的高度极低（3~4 层即可存储千万级数据），磁盘 I/O 次数少。
- **B+Tree 相对 B-Tree 的优势**：B+Tree 只在叶子节点存储数据，非叶子节点只存索引，单个节点可存储更多 key，树更矮。叶子节点通过链表连接，范围查询效率极高。

**Q4：Redis 为什么这么快？**

Redis 单线程（指命令处理线程）却能达到 10 万+ QPS，原因如下：

1. **纯内存操作**：所有数据存储在内存中，读写速度是纳秒/微秒级。
2. **单线程模型**：避免了多线程的上下文切换和锁竞争开销，CPU 不是瓶颈（内存和网络带宽才是）。
3. **高效的数据结构**：底层使用 SDS（简单动态字符串）、跳表、压缩列表等高效数据结构。
4. **I/O 多路复用**：使用 epoll/kqueue 等机制，一个线程同时监听多个客户端连接。
5. **RESP 协议简洁**：Redis 序列化协议（RESP）设计简单，解析高效。

**Q5：Prisma 相比 TypeORM 和 Sequelize 有哪些优势？**

- **类型安全**：Prisma 从 Schema 文件自动生成完全类型安全的 Client，TypeScript 类型推断无死角。TypeORM 和 Sequelize 的类型推断较弱，查询结果常需要手动类型断言。
- **Schema 定义**：Prisma 使用专用 DSL（`.prisma` 文件），比装饰器（TypeORM）或 `define`（Sequelize）更直观、可读性更强。
- **迁移工具**：Prisma Migrate 自动对比 Schema 和数据库状态生成迁移 SQL，TypeORM 和 Sequelize 的迁移需要更多手动操作。
- **关联查询**：Prisma 的 `include` 和 `select` 语法简洁且类型安全，嵌套关联查询非常直观。
- **性能**：Prisma Client 的查询引擎用 Rust 编写，复杂查询性能优于纯 JS 实现的 TypeORM 和 Sequelize。

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 未使用连接池或连接池过小 | 请求频繁超时，数据库连接耗尽 | 每次请求创建新连接开销巨大，连接池过小无法应对并发 | 配置合理的连接池大小（`核心数*2+磁盘数`），并在应用启动时预热连接池 |
| 在循环中执行数据库查询（N+1 问题） | 接口响应极慢，数据库 CPU 飙升 | 循环中逐条查询导致 N+1 次数据库请求 | 使用 ORM 的 `include`/`relations` 预加载关联数据，或使用 `findMany` 批量查询后用代码组装 |
| SELECT * 查询所有字段 | 查询效率低，网络传输量大 | 返回不需要的字段浪费 I/O 和内存 | 使用 `select`（Prisma）、`select` 列（TypeORM）、`attributes`（Sequelize）只查询需要的字段 |
| 忘记为查询条件列建索引 | 全表扫描，查询从毫秒级变为秒级 | 没有索引时数据库必须扫描全表 | 使用 `EXPLAIN` 分析慢查询，为 WHERE/JOIN/ORDER BY 涉及的列创建索引 |
| MySQL 使用 `utf8` 字符集（非 `utf8mb4`） | Emoji 等 4 字节字符插入失败或乱码 | MySQL 的 `utf8` 是阉割版，最多支持 3 字节 | 始终使用 `utf8mb4` 字符集和 `utf8mb4_unicode_ci` 排序规则 |
| Redis 缓存与数据库数据不一致 | 缓存返回旧数据，与数据库不一致 | 更新数据库后未及时清除缓存，或缓存和数据库更新非原子 | 采用 Cache-Aside 模式（先更新数据库，再删除缓存），设置合理的过期时间兜底 |
| 事务未设置超时时间 | 数据库连接卡死，其他请求等待 | 事务长时间未提交导致锁持有，连接不释放 | 为事务设置超时时间；避免在事务中执行耗时操作（如外部 API 调用） |
| Prisma 生产环境使用 `prisma migrate dev` | 生产数据库被意外修改 | `migrate dev` 会触发开发环境特有的行为（如重置数据库） | 生产环境使用 `prisma migrate deploy`，CI/CD 中集成迁移检查 |
| MongoDB 未为聚合查询建索引 | 聚合管道执行极慢 | 聚合管道中的 `$match`、`$sort` 需要索引支持 | 为 `$match` 和 `$sort` 涉及的字段创建索引，使用 `explain` 分析聚合管道 |
| 大表直接 `ALTER TABLE` 添加字段 | 表被锁住，所有写入阻塞 | MySQL 5.6 前 `ALTER TABLE` 会锁表，大表执行时间可能长达数小时 | 使用 `pt-online-schema-change`（Percona Toolkit）在线修改表结构，或使用支持在线 DDL 的数据库版本 |

---

> **学习导航**：
> - 返回 [学习路线总览](../README.md)
> - 本模块其他文件：[01-Node运行时与核心API](./01-Node运行时与核心API.md) | [02-Web框架与BFF层](./02-Web框架与BFF层.md) | [03-Node.js笔面试题集](./03-Node.js笔面试题集.md)
> - 进阶学习：[企业后台管理系统](../10-project/01-企业后台管理系统实战.md)

---

## 本章学习自检

- [ ] 能够设计规范的表结构，理解主键、外键、索引的关系
- [ ] 掌握 SQL 增删改查（CRUD）的基本语法和聚合查询
- [ ] 能够区分 INNER JOIN、LEFT JOIN、RIGHT JOIN、FULL JOIN 的执行结果
- [ ] 理解事务 ACID 四个特性的含义和实现原理
- [ ] 能够说明四种事务隔离级别的区别和常见并发问题（脏读、不可重复读、幻读）
- [ ] 理解 B+Tree 索引的原理，能够解释为什么 MySQL 选择 B+Tree 而非二叉树或哈希表
- [ ] 掌握 MongoDB 的文档增删改查和聚合管道基本用法
- [ ] 掌握 Redis 五种核心数据结构（String、Hash、List、Set、Sorted Set）的使用场景
- [ ] 理解 Redis 的过期策略和内存淘汰机制
- [ ] 能够识别并解决缓存穿透、缓存击穿、缓存雪崩问题
- [ ] 能够对比 Prisma、TypeORM、Sequelize 三大 ORM 的核心差异
- [ ] 能够使用 ORM 定义模型、执行迁移、完成关联查询