# ClickHouse 笔面试题集

> 学习路线对应：第8周 — ClickHouse 列式数据库
> 题目来源：大厂面试真题 + 高频考点
> 难度标注：★基础  ★★中档  ★★★拔高

> 📖 **参考链接**：
> - [ClickHouse Documentation](https://clickhouse.com/docs/) -- ClickHouse 官方文档总入口
> - [ClickHouse Introduction](https://clickhouse.com/docs/en/intro/) -- ClickHouse 简介与核心特性

---

## 一、选择题（10 题，每题 4 分，共 40 分）

### 1. ClickHouse 的存储方式是？（★）

A. 行式存储
B. 列式存储
C. 键值存储
D. 文档存储

**答案：B**

**解析**：ClickHouse 是面向列的 OLAP 数据库，采用列式存储。同一列数据连续存储，查询时只读取需要的列，大幅减少 IO。MySQL 等传统关系型数据库采用行式存储。

---

### 2. 以下哪个引擎是 ClickHouse 最基础的 MergeTree 引擎？（★）

A. Kafka
B. Distributed
C. MergeTree
D. Buffer

**答案：C**

**解析**：MergeTree 是 ClickHouse 最核心、最基础的表引擎，所有高级引擎（ReplacingMergeTree、SummingMergeTree、AggregatingMergeTree 等）都基于它。Kafka 引擎用于消费 Kafka 消息，Distributed 是分布式表引擎，Buffer 是内存缓冲引擎。

---

### 3. ClickHouse 稀疏索引的默认粒度是？（★★）

A. 每 1 行一个标记
B. 每 100 行一个标记
C. 每 8192 行一个标记
D. 每 65536 行一个标记

**答案：C**

**解析**：ClickHouse 的稀疏索引默认每 8192 行（`index_granularity`）生成一个标记（Mark）。与 MySQL B+Tree 的稠密索引（每行一个索引项）不同，稀疏索引占用空间极小，适合大批量扫描场景。

> 📖 **参考链接**：[ClickHouse 稀疏索引](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/) -- index_granularity 与稀疏索引官方说明

---

### 4. 以下关于 ClickHouse 分区的说法，**错误**的是？（★★）

A. 分区可以按时间字段进行（如 toYYYYMM）
B. 分区数量建议不超过 1000 个
C. 分区裁剪可以减少查询扫描的数据量
D. 分区键可以随时修改

**答案：D**

**解析**：分区键在创建表时确定，**不能随时修改**。如果需要修改分区键，必须重建表。A、B、C 都是正确的说法。

---

### 5. ClickHouse 中 `uniq()` 函数的底层算法是？（★★）

A. BitMap
B. HyperLogLog
C. Bloom Filter
D. Count-Min Sketch

**答案：B**

**解析**：`uniq()` 基于 **HyperLogLog** 算法实现近似去重计数，性能远优于 `COUNT(DISTINCT)`。默认误差率约 2%，可通过 `uniqCombined()`、`uniqExact()` 等变体调整精度。

---

### 6. 以下哪种场景**不适合**使用 ClickHouse？（★★）

A. 实时统计每小时 PV/UV
B. 用户行为漏斗分析
C. 银行账户余额高频更新
D. 广告曝光点击率统计

**答案：C**

**解析**：ClickHouse 不支持事务，UPDATE/DELETE 是异步 Mutation 操作，性能差。银行账户余额需要事务支持和高频更新，不适合 ClickHouse。A、B、D 都是 ClickHouse 的典型应用场景。

---

### 7. ClickHouse 中 `PREWHERE` 和 `WHERE` 的区别是？（★★）

A. PREWHERE 比 WHERE 慢
B. PREWHERE 先过滤再读取其他列，WHERE 先读取所有列再过滤
C. PREWHERE 只能用于字符串字段
D. 两者没有区别

**答案：B**

**解析**：`PREWHERE` 是 ClickHouse 特有的优化——先对指定列进行过滤（列裁剪），只读取满足条件的行的其他列，从而减少 IO。`WHERE` 是先读取所有列，再进行过滤。实际上 ClickHouse 会自动将部分 WHERE 条件优化为 PREWHERE。

---

### 8. SummingMergeTree 引擎的作用是？（★）

A. 自动删除重复数据
B. 合并时自动汇总数值列
C. 支持分布式查询
D. 从 Kafka 消费数据

**答案：B**

**解析**：SummingMergeTree 在后台合并 Part 时，自动将相同排序键的行的数值列进行求和汇总。适合预聚合统计场景。A 是 ReplacingMergeTree 的功能，C 是 Distributed 引擎的功能，D 是 Kafka 引擎的功能。

---

### 9. 以下关于 ClickHouse 物化视图的说法，**正确**的是？（★★）

A. 物化视图是逻辑视图，不存储数据
B. 物化视图是增量更新的，只计算新写入的数据
C. 物化视图只能聚合，不能过滤
D. 物化视图的源表删除数据后，物化视图也会同步删除

**答案：B**

**解析**：ClickHouse 的物化视图是一个**触发器**，源表有新数据写入时，自动增量计算并将结果写入目标表。A 错误（物化视图存储数据），C 错误（可以过滤），D 错误（物化视图数据不会自动同步删除）。

---

### 10. 以下哪种数据类型在 ClickHouse 中**不建议**使用？（★★）

A. UInt64
B. LowCardinality(String)
C. Nullable(String)
D. Decimal(10, 2)

**答案：C**

**解析**：`Nullable(T)` 类型在每行都有一个额外的 Null 标记字节，导致写入和查询都有额外开销。建议用默认值替代 Null。`LowCardinality(String)` 是推荐的低基数字符串优化，`UInt64` 和 `Decimal` 都是常用的高效类型。

---

## 二、简答题（5 题，每题 6 分，共 30 分）

### 1. 简述 ClickHouse 列式存储的优势。

**答**：
1. **只读需要的列**：查询 `SELECT AVG(age) FROM users` 只读取 `age` 列，大幅减少 IO
2. **高压缩比**：同一列数据类型相同、值相似度高，压缩比可达 5-10 倍（LZ4/ZSTD）
3. **向量化执行**：同一列数据在内存中连续存放，CPU 可利用 SIMD 指令批量处理
4. **减少存储成本**：100GB 原始数据压缩后只需 10-20GB 存储

> **生活化类比：列式存储 = 竖着读表格** —— 想象一张成绩单：行式存储横着读（每个学生所有科目一行），统计"全班平均分"得读完整张表；列式存储竖着读（只看成绩列），直接读完算平均。竖着读不仅读得少，同一列数据类型相同还特别适合压缩（5-10 倍压缩比），CPU 还能批量处理（向量化执行）。

> 📖 **参考链接**：[ClickHouse 列式存储](https://clickhouse.com/docs/en/intro/) -- 列式存储核心优势官方说明

---

### 2. MergeTree 引擎的 PARTITION BY 和 ORDER BY 分别有什么作用？

**答**：
- **PARTITION BY**：将数据按指定规则拆分到不同物理目录。查询时 ClickHouse 只扫描相关分区，大幅减少数据扫描量。建议按月分区（`toYYYYMM`），分区数量不宜超过 1000 个。
- **ORDER BY**：排序键，数据按此字段顺序物理存储。也是主键（稀疏索引），ClickHouse 基于排序键每 8192 行生成一个标记。应选择查询中最常用的过滤和聚合字段，高基数列在前。

---

### 3. ClickHouse 的稀疏索引和 MySQL 的 B+Tree 索引有什么区别？

**答**：

| 维度 | 稀疏索引（ClickHouse） | B+Tree 索引（MySQL） |
|------|----------------------|---------------------|
| 索引粒度 | 8192 行一个标记 | 每行一个索引项 |
| 索引大小 | 极小（千分之一） | 较大（10%-30%） |
| 查询方式 | 定位区间 → 扫描区间内数据 | 直接定位到具体行 |
| 写入性能 | 高（顺序写入） | 一般（随机写入） |
| 适用场景 | 大批量扫描 + 聚合 | 精确查找 + 点查询 |

> **生活化类比：稀疏索引 = 路标，B+Tree = 门牌号** —— 稀疏索引就像高速公路上的路标，每隔 8 公里（8192 行）立一个，告诉你"这一段的大致范围"，快速定位到哪个区间再细看。B+Tree 就像每家每户的门牌号，精确到具体哪一行。路标（稀疏索引）虽不够精确，但占用空间极小（千分之一），适合"快速扫一大片"；门牌号（B+Tree）精确但体积大，适合"精确定位一家"。

> 📖 **参考链接**：[ClickHouse 索引机制](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/) -- 稀疏索引与主键官方说明

---

### 4. 简述 ClickHouse 的 Partition 和 MySQL 的 Partition 的区别。

**答**：
- **目的不同**：ClickHouse 分区主要用于查询裁剪（减少扫描数据量），MySQL 分区主要用于管理维护（如快速删除旧数据）。
- **实现不同**：ClickHouse 分区每个分区是独立的物理目录，存储一组 Part 文件；MySQL 分区是逻辑上的表拆分。
- **查询优化**：ClickHouse 的分区裁剪效果更显著，因为列式存储 + 分区裁剪，只读取相关分区的相关列；MySQL 分区裁剪后仍需扫描整行。
- **数量限制**：ClickHouse 建议分区数不超过 1000 个，MySQL 单个表最多 8192 个分区。

---

### 5. ClickHouse 如何进行数据去重？有哪些方案？

**答**：
1. **ReplacingMergeTree**：后台合并时删除相同排序键的重复行，保留最新版本（通过 `ver` 版本列）。注意：合并时机不确定，查询时可能仍有重复。
2. **查询时去重**：使用 `SELECT DISTINCT` 或 `GROUP BY + argMax()` 取最新版本。
3. **写入前去重**：在应用层或使用 Kafka + 流处理去重后再写入 ClickHouse。
4. **使用 `FINAL` 关键字**：强制合并数据（`SELECT * FROM table FINAL`），但性能较差，不建议在生产环境频繁使用。

---

## 三、场景设计题（3 题，每题 10 分，共 30 分）

### 1. 实时 PV/UV 统计系统设计

**场景**：某网站每天产生约 1 亿条页面访问日志，需要实时统计每小时的 PV（页面浏览量）和 UV（独立访客数），延迟不超过 5 分钟，数据保留 90 天。

**参考答案**：

**表设计**：
```sql
CREATE TABLE page_views (
    event_time  DateTime,
    event_date  Date DEFAULT toDate(event_time),
    page_url    String,
    user_id     UInt64,
    session_id  String,
    device      LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)    -- 按天分区（每天 1 亿条，分区合理）
ORDER BY (event_date, page_url, event_time)
TTL event_time + INTERVAL 90 DAY
SETTINGS index_granularity = 8192;
```

**物化视图预聚合**：
```sql
-- 目标表
CREATE TABLE pv_uv_hourly (
    hour        DateTime,
    page_url    String,
    pv          UInt64,
    uv          UInt64
)
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (page_url, hour);

-- 物化视图
CREATE MATERIALIZED VIEW mv_pv_uv_hourly TO pv_uv_hourly AS
SELECT
    toStartOfHour(event_time) AS hour,
    page_url,
    count() AS pv,
    -- 注意：uniq() 基于 HyperLogLog 近似算法，聚合写入 SummingMergeTree 时精度会进一步降低
    -- 如需更高精度，可改用 uniqState() 存储中间状态，查询时用 uniqMerge() 合并
    uniq(user_id) AS uv
FROM page_views
GROUP BY hour, page_url;
```

**查询方式**：直接查询 `pv_uv_hourly` 表，数据已被预聚合，查询延迟毫秒级。

---

### 2. 用户行为漏斗分析设计

**场景**：电商平台需要分析用户从"浏览商品 → 加入购物车 → 下单 → 支付"的转化漏斗，要求支持按天、按商品分类查询。

**参考答案**：

**表设计**：
```sql
CREATE TABLE user_events (
    event_time  DateTime,
    event_date  Date DEFAULT toDate(event_time),
    user_id     UInt64,
    event_type  LowCardinality(String),  -- view_product, add_cart, place_order, pay
    product_id  UInt64,
    category    LowCardinality(String),
    amount      Decimal(10, 2)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_date, event_type, user_id);
```

**漏斗分析查询**：
```sql
-- 按天统计各阶段用户数
SELECT
    event_date,
    uniqIf(user_id, event_type = 'view_product') AS view_users,
    uniqIf(user_id, event_type = 'add_cart') AS cart_users,
    uniqIf(user_id, event_type = 'place_order') AS order_users,
    uniqIf(user_id, event_type = 'pay') AS pay_users,
    round(cart_users / view_users, 4) AS view_to_cart_rate,
    round(order_users / cart_users, 4) AS cart_to_order_rate,
    round(pay_users / order_users, 4) AS order_to_pay_rate
FROM user_events
WHERE event_date BETWEEN '2026-06-22' AND '2026-06-28'
GROUP BY event_date
ORDER BY event_date;
```

**优化**：使用物化视图按天预聚合各阶段用户数，查询时直接读预计算结果。

---

### 3. 多维实时报表系统设计

**场景**：某运营团队需要实时查看以下维度的销售数据：按小时、按商品分类、按地区三个维度的销售额、订单数、客单价。数据来源为 MySQL 订单表（每天新增约 500 万条），要求延迟不超过 1 分钟。

**参考答案**：

**数据同步**：使用 Canal 监听 MySQL binlog → Kafka → ClickHouse 消费者。

**宽表设计**（写入时做 JOIN，避免查询时 JOIN）：
```sql
CREATE TABLE order_wide (
    order_id        UInt64,
    event_time      DateTime,
    event_date      Date DEFAULT toDate(event_time),
    user_id         UInt64,
    product_id      UInt64,
    category        LowCardinality(String),
    region          LowCardinality(String),
    amount          Decimal(10, 2),
    quantity        UInt16,
    status          LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_date, category, region, event_time);
```

**物化视图预聚合（按小时 + 分类 + 地区）**：
```sql
CREATE TABLE sales_hourly_agg (
    hour        DateTime,
    category    LowCardinality(String),
    region      LowCardinality(String),
    order_count UInt64,
    total_amount Decimal(20, 2),
    user_count  UInt64
)
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (category, region, hour);

CREATE MATERIALIZED VIEW mv_sales_hourly TO sales_hourly_agg AS
SELECT
    toStartOfHour(event_time) AS hour,
    category,
    region,
    count() AS order_count,
    sum(amount) AS total_amount,
    uniq(user_id) AS user_count
FROM order_wide
GROUP BY hour, category, region;
```

**多维查询**：
```sql
-- 按分类 + 地区统计
SELECT category, region, sum(order_count), sum(total_amount)
FROM sales_hourly_agg
WHERE hour >= '2026-06-29 00:00:00'
GROUP BY category, region;

-- 按小时趋势
SELECT hour, sum(order_count), sum(total_amount)
FROM sales_hourly_agg
WHERE hour >= '2026-06-29 00:00:00'
GROUP BY hour ORDER BY hour;
```

**性能保证**：预聚合后查询延迟毫秒级，数据同步延迟 Canal + Kafka 保证在秒级。宽表设计避免查询时 JOIN，物化视图避免实时扫描原始数据。

> 📖 **参考链接**：
> - [ClickHouse 物化视图](https://clickhouse.com/docs/en/sql-reference/statements/create/view/) -- 物化视图与增量预聚合官方说明
> - [ClickHouse 最佳实践](https://clickhouse.com/docs/en/guides/developer/best-practices/) -- 建表、写入、查询最佳实践官方指南

---

> **学习导航**：
> - 返回 [学习路线总览](../../README.md)
> - 本模块其他文件：[01-ClickHouse核心原理](./01-ClickHouse核心原理.md)
> - 实战应用：[电商订单实时统计分析平台](../../extensions/project/01-电商订单实时统计分析平台.md)

