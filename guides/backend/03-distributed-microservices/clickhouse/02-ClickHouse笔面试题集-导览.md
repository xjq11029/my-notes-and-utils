# ClickHouse 笔面试题集 导览

> 定位：五维框架浓缩提炼 02-ClickHouse笔面试题集.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-ClickHouse笔面试题集.md)。
> 前置知识：[ClickHouse核心原理](./01-ClickHouse核心原理-导览.md)

---

## 一、选择题（10 题，每题 4 分，共 40 分）

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ClickHouse 基础概念与核心知识点的客观题型，每题 4 分共 40 分。 |
| 能做什么 | 覆盖存储方式、引擎家族、稀疏索引、分区、去重算法、适用场景、PREWHERE、SummingMergeTree、物化视图、数据类型等基础考点。 |
| 怎么用 | 四选一，选出正确或错误项。 |
| 原理和工作流程 | 通过单选形式快速检验对 ClickHouse 核心概念的记忆与辨析能力，题目含基础到中档难度，解析点明每个选项的对错依据。 |
| 缺点 | 仅能考查点状知识记忆，难以检验综合设计与实操能力；猜答概率 25%。 |

### 1. ClickHouse 的存储方式是？（★）

| 维度 | 内容 |
|------|------|
| 是什么 | ClickHouse 采用的面向列存储方式，同一列数据连续存放。 |
| 能做什么 | 查询只读所需列减少 IO；同列同类型高压缩；向量化执行。 |
| 怎么用 | 与 MySQL 行式存储对比辨识。 |
| 原理和工作流程 | 磁盘按列分块，每列数据连续存储；查询 AVG(age) 仅加载 age 列；列内类型一致压缩比 5-10 倍；与行式存储逐行存放形成对比，MySQL 等关系库为行式。 |
| 缺点 | 整行写入拆分开销大；全列查询无优势；不适合频繁单行更新。 |

### 2. 以下哪个引擎是 ClickHouse 最基础的 MergeTree 引擎？（★）

| 维度 | 内容 |
|------|------|
| 是什么 | MergeTree 是 ClickHouse 最核心基础的表引擎，所有高级引擎基于它构建。 |
| 能做什么 | 支持分区排序 TTL；作为 ReplacingMergeTree、SummingMergeTree 等的基座；Kafka、Distributed、Buffer 为非 MergeTree 系引擎。 |
| 怎么用 | `ENGINE = MergeTree()` |
| 原理和工作流程 | MergeTree 提供分区、排序键、稀疏索引、TTL 等核心能力；ReplacingMergeTree 等继承其机制并在合并时施加去重、汇总逻辑；Kafka 引擎消费消息、Distributed 是分布式表、Buffer 是内存缓冲，均非 MergeTree 系。 |
| 缺点 | 基础 MergeTree 不去重不汇总，需按场景选衍生引擎；引擎选型需理解各引擎合并逻辑。 |

### 3. ClickHouse 稀疏索引的默认粒度是？（★★）

| 维度 | 内容 |
|------|------|
| 是什么 | ClickHouse 稀疏索引默认每 8192 行生成一个标记的索引粒度配置。 |
| 能做什么 | 极小索引占用；快速定位数据区间；适合大批量扫描。 |
| 怎么用 | `SETTINGS index_granularity = 8192` |
| 原理和工作流程 | 与 MySQL B+Tree 稠密索引（每行一个索引项）不同，稀疏索引每 8192 行一个 Mark，记录区间排序键 min/max 与物理偏移；索引大小约为数据千分之一，查询先定位 Mark 区间再扫描。 |
| 缺点 | 只能定位区间不能精确定位单行；点查询需扫描整个 granule；粒度过大降低点查效率。 |

### 4. 以下关于 ClickHouse 分区的说法，错误的是？（★★）

| 维度 | 内容 |
|------|------|
| 是什么 | ClickHouse 分区的特性集合，其中分区键建表后不可随时修改。 |
| 能做什么 | 按时间分区；分区裁剪减少扫描；分区数建议不超 1000；分区键不可随时修改。 |
| 怎么用 | `PARTITION BY toYYYYMM(event_time)` |
| 原理和工作流程 | 分区键在建表时确定，数据按表达式值落入分区目录；分区裁剪查询只扫匹配分区；修改分区键需重建表，因已有数据按旧键分布无法迁移。 |
| 缺点 | 分区键不可变修改成本高；分区数过多影响元数据管理；粒度选择需权衡。 |

### 5. ClickHouse 中 uniq() 函数的底层算法是？（★★）

| 维度 | 内容 |
|------|------|
| 是什么 | uniq() 函数基于 HyperLogLog 算法实现的近似去重计数。 |
| 能做什么 | 高性能近似去重；默认误差约 2%；可通过 uniqCombined、uniqExact 调整精度。 |
| 怎么用 | `SELECT uniq(user_id) FROM t` |
| 原理和工作流程 | HyperLogLog 用哈希值的二进制前缀位数估计基数，固定内存下近似计数，性能远优于 COUNT(DISTINCT) 的精确去重；uniqCombined 结合多种算法平衡精度与性能。 |
| 缺点 | 近似结果有约 2% 误差；不适用于需精确去重的场景；高精度变体性能下降。 |

### 6. 以下哪种场景不适合使用 ClickHouse？（★★）

| 维度 | 内容 |
|------|------|
| 是什么 | ClickHouse 不支持事务且 UPDATE/DELETE 性能差的适用边界。 |
| 能做什么 | 实时 PV/UV 统计；漏斗分析；广告统计；不适合银行账户余额高频更新。 |
| 怎么用 | 事务与高频更新场景选 MySQL，分析场景选 ClickHouse。 |
| 原理和工作流程 | ClickHouse 的 UPDATE/DELETE 是异步 Mutation 会重写整个 Part，性能差且不支持事务；银行账户余额需事务保证和高频更新，违背列式存储批量写入设计前提；PV/UV、漏斗、广告统计为聚合分析契合其优势。 |
| 缺点 | 不适合任何需要事务或高频更新的业务；Mutation 操作代价高；不能作业务主库。 |

### 7. ClickHouse 中 PREWHERE 和 WHERE 的区别是？（★★）

| 维度 | 内容 |
|------|------|
| 是什么 | PREWHERE 是 ClickHouse 特有的列裁剪过滤优化，先过滤再读其他列。 |
| 能做什么 | 先对指定列过滤；只读满足条件行的其他列；减少 IO；MergeTree 自动将部分 WHERE 优化为 PREWHERE。 |
| 怎么用 | `SELECT ... FROM t PREWHERE event_type = 'click'` |
| 原理和工作流程 | WHERE 先读取所有列再过滤造成 IO 浪费；PREWHERE 先只读取过滤列的值，确定满足条件的行后，再读取这些行的其他列，从而减少无关列的读取量。 |
| 缺点 | 仅对高选择性过滤条件有效；过滤列仍需全量读取；手动使用不当可能无收益。 |

### 8. SummingMergeTree 引擎的作用是？（★）

| 维度 | 内容 |
|------|------|
| 是什么 | 合并 Part 时自动将相同排序键的数值列求和汇总的 MergeTree 衍生引擎。 |
| 能做什么 | 预聚合统计；按排序键汇总数值；适合 PV/UV 汇总场景。 |
| 怎么用 | `ENGINE = SummingMergeTree() ORDER BY (category, hour)` |
| 原理和工作流程 | 后台合并时，对相同排序键的行的数值列求和合并为一行，非数值列取任一值；查询时数据已被预聚合减少扫描量；与 ReplacingMergeTree（去重）、Distributed（分布式）、Kafka（消费）功能不同。 |
| 缺点 | 合并时机不确定查询时可能未汇总；非数值列汇总行为需注意；只汇总数值列不适用复杂聚合。 |

### 9. 以下关于 ClickHouse 物化视图的说法，正确的是？（★★）

| 维度 | 内容 |
|------|------|
| 是什么 | ClickHouse 物化视图是触发器，源表写入时自动增量计算并写入目标表。 |
| 能做什么 | 增量更新只算新数据；存储预计算结果；支持聚合与过滤；源表删除不同步删除。 |
| 怎么用 | `CREATE MATERIALIZED VIEW mv TO target AS SELECT ...` |
| 原理和工作流程 | 物化视图是物理视图存储数据，非逻辑视图；源表新数据写入触发 SELECT 聚合，结果 INSERT 到目标表；只处理新 Block 不重算历史；源表删除数据后物化视图不同步删除。 |
| 缺点 | 占用额外存储；源表删除不同步；逻辑修改需重建；不能替代源表。 |

### 10. 以下哪种数据类型在 ClickHouse 中不建议使用？（★★）

| 维度 | 内容 |
|------|------|
| 是什么 | Nullable(T) 类型因每行额外 Null 标记字节而不建议使用的类型。 |
| 能做什么 | 用默认值替代 Null；推荐 LowCardinality(String) 优化低基数列；UInt64 和 Decimal 为常用高效类型。 |
| 怎么用 | `amount Decimal(10,2) DEFAULT 0` 替代 Nullable。 |
| 原理和工作流程 | Nullable(T) 在每行额外存储一个 Null 标记字节，写入和查询都有额外开销，且影响压缩效果；LowCardinality(String) 对低基数字符串用字典编码高效；建议用默认值替代 Null 避免开销。 |
| 缺点 | Nullable 性能开销大；Enum 修改需 ALTER TABLE 不灵活；类型选大浪费存储。 |

---

## 二、简答题（5 题，每题 6 分，共 30 分）

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ClickHouse 原理理解与对比分析的问答题型，每题 6 分共 30 分。 |
| 能做什么 | 覆盖列式存储优势、PARTITION BY 与 ORDER BY 作用、稀疏索引与 B+Tree 区别、ClickHouse 与 MySQL 分区区别、数据去重方案。 |
| 怎么用 | 文字阐述原理，必要时配表格对比。 |
| 原理和工作流程 | 要求考生用结构化语言解释原理机制、对比异同、列举方案，检验对底层机制的深度理解而非死记结论。 |
| 缺点 | 主观评分可能有偏差；难以覆盖实操细节；答题耗时较长。 |

### 1. 简述 ClickHouse 列式存储的优势。

| 维度 | 内容 |
|------|------|
| 是什么 | 列式存储在 IO、压缩、向量化、存储成本上的四项优势。 |
| 能做什么 | 只读需要的列；高压缩比；向量化执行；减少存储成本。 |
| 怎么用 | `SELECT AVG(age) FROM users` 只读 age 列。 |
| 原理和工作流程 | 查询只读取所需列大幅减少 IO；同列数据类型相同值相似度高，LZ4/ZSTD 压缩比 5-10 倍；同一列内存连续 CPU 用 SIMD 批量处理；100GB 原始数据压缩后只需 10-20GB。 |
| 缺点 | 整行写入拆分开销大；全列查询无优势；不适合频繁单行更新。 |

### 2. MergeTree 引擎的 PARTITION BY 和 ORDER BY 分别有什么作用？

| 维度 | 内容 |
|------|------|
| 是什么 | PARTITION BY 按规则拆分数据到物理目录，ORDER BY 是排序键决定物理顺序并作主键。 |
| 能做什么 | 分区裁剪减少扫描；排序键加速范围查询；排序键生成稀疏索引；高基数列在前。 |
| 怎么用 | `PARTITION BY toYYYYMM(event_time) ORDER BY (event_type, event_time, user_id)` |
| 原理和工作流程 | PARTITION BY 将数据按表达式值拆分到不同物理目录，查询时分区裁剪只扫相关分区，建议按月分区不超 1000 个；ORDER BY 决定数据物理存储顺序，同时作为主键每 8192 行生成稀疏索引 Mark，应选查询最常用的过滤聚合字段高基数列在前。 |
| 缺点 | 分区键不可修改；排序键修改成本高；分区数过多影响元数据管理。 |

### 3. ClickHouse 的稀疏索引和 MySQL 的 B+Tree 索引有什么区别？

| 维度 | 内容 |
|------|------|
| 是什么 | ClickHouse 稀疏索引与 MySQL B+Tree 稠密索引在粒度、大小、查询方式上的差异。 |
| 能做什么 | 稀疏索引极小占用定位区间；B+Tree 精确定位单行；分别适配扫描与点查。 |
| 怎么用 | 稀疏索引 `index_granularity = 8192`；B+Tree 自动建索引。 |
| 原理和工作流程 | 稀疏索引每 8192 行一个 Mark，索引大小约数据千分之一，查询先定位区间再扫描，顺序写入性能高，适合大批量扫描聚合；B+Tree 每行一个索引项，索引大小约数据 10%-30%，直接定位到具体行，随机写入，适合精确查找点查询。 |
| 缺点 | 稀疏索引点查询需扫描整个 granule；B+Tree 索引占用大且写入慢；各有适用场景难以兼顾。 |

### 4. 简述 ClickHouse 的 Partition 和 MySQL 的 Partition 的区别。

| 维度 | 内容 |
|------|------|
| 是什么 | 两款数据库分区在目的、实现、查询优化、数量限制上的差异。 |
| 能做什么 | ClickHouse 分区用于查询裁剪；MySQL 分区用于管理维护；裁剪效果差异；数量限制不同。 |
| 怎么用 | ClickHouse `PARTITION BY toYYYYMM(event_time)`；MySQL 分区建表指定。 |
| 原理和工作流程 | ClickHouse 分区是独立物理目录存一组 Part，主要用于查询裁剪，列式存储加裁剪只读相关列相关分区，建议不超 1000 个；MySQL 分区是逻辑表拆分，主要用于管理维护如快速删除旧数据，裁剪后仍扫整行，单表最多 8192 个分区。 |
| 缺点 | ClickHouse 分区键不可改；MySQL 分区裁剪效果弱；两者分区数过多均影响性能。 |

### 5. ClickHouse 如何进行数据去重？有哪些方案？

| 维度 | 内容 |
|------|------|
| 是什么 | ClickHouse 四种数据去重方案及各自机制。 |
| 能做什么 | ReplacingMergeTree 合并去重；查询时 DISTINCT 或 argMax 取最新；写入前去重；FINAL 强制合并。 |
| 怎么用 | `SELECT * FROM table FINAL` 或 `argMax(value, version)` |
| 原理和工作流程 | ReplacingMergeTree 后台合并时按排序键删除重复行保留最新版本（ver 列），但合并时机不确定；查询时用 DISTINCT 或 GROUP BY 加 argMax 取最新版本；写入前在应用层或 Kafka 流处理去重；FINAL 强制合并但性能差。 |
| 缺点 | ReplacingMergeTree 查询时可能仍重复；FINAL 性能差不建议生产用；写入前去重增加链路复杂度；查询去重有额外开销。 |

---

## 三、场景设计题（3 题，每题 10 分，共 30 分）

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ClickHouse 实战架构设计能力的综合题型，每题 10 分共 30 分。 |
| 能做什么 | 覆盖实时 PV/UV 统计、用户行为漏斗分析、多维实时报表系统设计。 |
| 怎么用 | 给出场景需求，设计表结构、物化视图、查询与数据同步方案。 |
| 原理和工作流程 | 要求根据业务场景选择分区排序键、设计物化视图预聚合、规划数据同步链路（Canal 加 Kafka）、编写多维查询 SQL，检验端到端架构能力。 |
| 缺点 | 答案非唯一，评分标准难统一；耗时最长；对无实战经验者难度大。 |

### 1. 实时 PV/UV 统计系统设计

| 维度 | 内容 |
|------|------|
| 是什么 | 日均 1 亿条日志下按小时统计 PV/UV、延迟 5 分钟、保留 90 天的系统设计方案。 |
| 能做什么 | 按天分区 MergeTree 存原始日志；SummingMergeTree 目标表存预聚合；物化视图增量聚合；TTL 90 天自动过期。 |
| 怎么用 | `CREATE MATERIALIZED VIEW mv_pv_uv_hourly TO pv_uv_hourly AS SELECT toStartOfHour(event_time) AS hour, page_url, count() AS pv, uniq(user_id) AS uv FROM page_views GROUP BY hour, page_url` |
| 原理和工作流程 | 原始表按天分区（每天 1 亿条分区合理）、排序键按日期与 URL；物化视图源表写入触发按小时聚合，count() 算 PV、uniq() 算 UV，结果写入 SummingMergeTree 目标表；查询直接读预聚合表毫秒级返回；TTL 90 天自动清理。 |
| 缺点 | 物化视图占用额外存储；uniq() 近似去重有 2% 误差；源表删除不同步；高基数 URL 维度目标表膨胀。 |

### 2. 用户行为漏斗分析设计

| 维度 | 内容 |
|------|------|
| 是什么 | 电商平台浏览到支付四阶段转化漏斗的设计方案，支持按天按分类查询。 |
| 能做什么 | MergeTree 存用户事件；uniqIf 按事件类型分别去重；计算各阶段转化率；物化视图按天预聚合。 |
| 怎么用 | `SELECT event_date, uniqIf(user_id, event_type='view_product') AS view_users, uniqIf(user_id, event_type='add_cart') AS cart_users FROM user_events GROUP BY event_date` |
| 原理和工作流程 | 表按月分区、排序键按日期事件类型用户；漏斗查询用 uniqIf 对每个事件类型分别去重统计用户数，round 算各阶段转化率；可用物化视图按天预聚合各阶段用户数加速查询。 |
| 缺点 | 各阶段独立去重非严格有序漏斗，未保证用户实际经过前一阶段；uniqIf 近似有误差；多事件类型查询内存占用大。 |

### 3. 多维实时报表系统设计

| 维度 | 内容 |
|------|------|
| 是什么 | 按小时、分类、地区三维度统计销售额订单数客单价、延迟 1 分钟的报表系统设计方案。 |
| 能做什么 | Canal 监听 binlog 经 Kafka 同步；宽表写入时做 JOIN；物化视图按小时分类地区预聚合；多维查询毫秒级。 |
| 怎么用 | `CREATE MATERIALIZED VIEW mv_sales_hourly TO sales_hourly_agg AS SELECT toStartOfHour(event_time) AS hour, category, region, count() AS order_count, sum(amount) AS total_amount, uniq(user_id) AS user_count FROM order_wide GROUP BY hour, category, region` |
| 原理和工作流程 | Canal 监听 MySQL binlog 发送到 Kafka，ClickHouse 消费写入宽表（写入时 JOIN 避免查询时 JOIN）；物化视图按小时分类地区聚合到 SummingMergeTree 目标表；多维查询直接读预聚合表按维度 GROUP BY；同步延迟 Canal 加 Kafka 秒级，查询毫秒级。 |
| 缺点 | 宽表数据冗余；物化视图占用额外存储；Canal 加 Kafka 链路复杂需维护；维度组合多时目标表膨胀。 |

---

> [返回原文](./02-ClickHouse笔面试题集.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
