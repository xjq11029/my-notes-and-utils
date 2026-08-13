# Redis 笔面试题集

> 题目来源：常见国企/互联网笔面试真题归纳
> 难度标注：★基础  ★★中档  ★★★拔高

---

## 一、选择题（20 题，每题附解析）

### 1. ★ Redis 的默认端口是？
A. 3306  B. 6379  C. 27017  D. 8080

**答案：B**

**解析**：6379 是 Redis 的默认端口。3306 是 MySQL 默认端口，27017 是 MongoDB 默认端口，8080 是常见 Web 服务器端口。Redis 端口号 6379 来源于手机键盘上 MERZ 对应的数字（MERZ 是意大利广告女郎的名字，Redis 作者 Antirez 和他的朋友常拿 MERZ 开玩笑）。

> 📖 **参考链接**：[Redis 官方文档 - Getting Started](https://redis.io/docs/getting-started/) -- Redis 默认端口 6379 的由来与基础配置说明

---

### 2. ★ Redis 的数据存储在？
A. 硬盘  B. 内存  C. 固态硬盘  D. 寄存器

**答案：B**

**解析**：Redis 是内存数据库，所有数据主要存储在内存中，这也是它读写速度极快（单机可达 10 万 QPS）的根本原因。虽然 Redis 提供了 RDB 和 AOF 持久化机制将数据写入磁盘，但数据读写始终在内存中进行。

> 📖 **参考链接**：[Redis 官方文档 - Introduction](https://redis.io/docs/about/) -- Redis 作为内存数据库的核心特性说明

---

### 3. ★★ Redis 的 String 类型底层数据结构是？
A. 数组  B. 链表  C. SDS（简单动态字符串）  D. 红黑树

**答案：C**

**解析**：Redis 使用 SDS（Simple Dynamic String）而非 C 语言原生字符串。SDS 的优势包括：O(1) 获取字符串长度、杜绝缓冲区溢出、二进制安全（可存储任意数据）、减少内存重分配次数（预分配和惰性空间释放）。String 类型在小数据量时使用 int 或 embstr 编码，长数据时使用 raw 编码。

> 📖 **参考链接**：[Redis 官方文档 - String](https://redis.io/docs/data-types/strings/) -- String 类型与 SDS 底层实现说明

---

### 4. ★★ Redis 哈希表扩容采用什么方式？
A. 一次性扩容  B. 渐进式 rehash  C. 不扩容  D. 手动扩容

**答案：B**

**解析**：Redis 使用渐进式 rehash 避免一次性扩容导致服务阻塞。维护 ht[0] 和 ht[1] 两个哈希表，rehashidx 标记当前迁移进度，每次对字典的增删改查操作时顺带迁移一个桶，同时定时任务也会在 1ms 内执行迁移，直到全部迁移完成。这样将扩容的计算量分摊到多次操作中，不会阻塞主线程。

> 📖 **参考链接**：[Redis 官方文档 - Hash](https://redis.io/docs/data-types/hashes/) -- Hash 渐进式 rehash 扩容机制说明

---

### 5. ★★ Redis 有序集合（ZSet）的底层实现是？
A. 红黑树  B. B+树  C. 跳跃表 + 字典  D. 数组

**答案：C**

**解析**：ZSet 使用跳跃表（skiplist）和字典（dict）两种数据结构组合实现。跳跃表负责按 score 排序，支持 O(logN) 的范围查询；字典负责 member 到 score 的映射，支持 O(1) 的单点查询。元素少时使用 ziplist 压缩列表编码。选择跳跃表而非红黑树的原因：跳跃表实现简单、支持范围查询、且 Redis 作者认为跳跃表更易理解和维护。

> 📖 **参考链接**：[Redis 官方文档 - Sorted Set](https://redis.io/docs/data-types/sorted-sets/) -- ZSet 跳跃表 + 字典底层实现说明

---

### 6. ★★ 以下哪个命令会阻塞 Redis 主线程？
A. GET  B. KEYS *  C. SCAN  D. EXISTS

**答案：B**

**解析**：`KEYS *` 会遍历所有 key，时间复杂度 O(N)。当 Redis 中有数百万个 key 时，执行 KEYS 会导致主线程长时间阻塞，无法处理其他请求。生产环境应使用 `SCAN` 命令，它采用游标方式渐进式遍历，每次只返回少量 key，不会阻塞主线程。

> 📖 **参考链接**：[Redis 官方文档 - SCAN](https://redis.io/commands/scan/) -- SCAN 渐进式游标遍历替代 KEYS 命令

---

**RDB 与 AOF 持久化流程对比示意图：**

**RDB 快照持久化：**

```mermaid
%%{init: {'themeVariables': {'fontSize': '16px'}}}%%
flowchart LR
    R1["触发条件<br/>（save / BGSAVE）"] --> R2["父进程 fork 子进程"]
    R2 --> R3["子进程写入<br/>临时 RDB 文件"]
    R3 --> R4["替换旧 RDB 文件"]
    R4 --> R5["完成快照"]
```

> RDB 通过 fork 子进程生成快照，文件小恢复快但可能丢失数据。

**AOF 追加日志持久化：**

```mermaid
%%{init: {'themeVariables': {'fontSize': '16px'}}}%%
flowchart LR
    A1["每条写命令"] --> A2["追加到<br/>AOF 缓冲区"]
    A2 --> A3["同步策略<br/>（always/everysec/no）"]
    A3 --> A4["写入 AOF 文件"]
    A4 --> A5["AOF 文件<br/>持续增长"]
    A5 --> A6["触发 AOF 重写<br/>（BGREWRITEAOF）"]
    A6 --> A7["压缩为<br/>最小命令集"]
```

> AOF 通过追加命令日志实现持久化，数据安全性更高但文件较大。

> 上图对比展示了 Redis 两种持久化机制的工作流程：RDB 通过 fork 子进程生成快照，文件小恢复快但可能丢失数据；AOF 通过追加命令日志实现持久化，数据安全性更高但文件较大。Redis 4.0 引入混合持久化，结合两者优势，兼顾恢复速度与数据安全。

### 7. ★★ Redis 的 AOF 默认写入策略是？
A. always  B. everysec  C. no  D. never

**答案：B**

**解析**：AOF 的默认写入策略是 everysec（每秒刷盘一次）。always 每次写命令都刷盘，安全性最高但性能最差；no 由操作系统决定刷盘，性能最好但不可控。everysec 是性能和数据安全之间的最佳平衡点，最多丢失 1 秒的数据。

> 📖 **参考链接**：[Redis 官方文档 - Persistence](https://redis.io/docs/management/persistence/) -- AOF 三种刷盘策略（always/everysec/no）说明

---

### 8. ★★ 哨兵模式下，判断主节点客观下线（ODOWN）的条件是？
A. 任意一个 Sentinel 认为下线  B. 超过 quorum 个 Sentinel 认为下线  C. 所有 Sentinel 认为下线  D. 主节点自己声明下线

**答案：B**

**解析**：单个 Sentinel 判断节点不可达是主观下线（SDOWN）。当超过 quorum 个 Sentinel 都认为主节点主观下线时，主节点被标记为客观下线（ODOWN），此时才会触发故障转移。quorum 是在 `sentinel monitor` 配置中指定的数量。

> 📖 **参考链接**：[Redis 官方文档 - Sentinel](https://redis.io/docs/management/sentinel/) -- 哨兵 quorum 配置与 SDOWN/ODOWN 判定机制

---

### 9. ★★ Redis Cluster 有多少个哈希槽？
A. 1024  B. 4096  C. 16384  D. 65536

**答案：C**

**解析**：Redis Cluster 有 16384 个哈希槽。选择这个数字的原因：心跳包大小约 2KB（16384/8/1024 = 2KB），如果使用 65536 个槽，心跳包会膨胀到 8KB，增加网络开销；同时 Redis 作者认为集群节点数不会超过 1000 个，16384 足够均匀分布。

> 📖 **参考链接**：[Redis 官方文档 - Cluster](https://redis.io/docs/management/scaling/) -- 16384 哈希槽数量设计原因说明

---

### 10. ★★ 缓存穿透的解决方案不包括？
A. 布隆过滤器  B. 缓存空值  C. 增加缓存过期时间  D. 参数校验

**答案：C**

**解析**：缓存穿透的核心问题是查询不存在的数据，每次请求都会穿透缓存直接打到数据库。增加缓存过期时间解决的是缓存雪崩问题（大量 key 同时过期），与缓存穿透无关。解决穿透需要：布隆过滤器（前置拦截不存在的数据）、缓存空值（设置短过期时间）、参数校验（过滤非法请求）。

> 📖 **参考链接**：[Redis 官方文档 - RedisBloom](https://redis.io/docs/data-types/probabilistic/bloom-filter/) -- 布隆过滤器模块（前置拦截缓存穿透）说明

---

### 11. ★★ Redis 的默认内存淘汰策略是？
A. allkeys-lru  B. volatile-lru  C. noeviction  D. allkeys-random

**答案：C**

**解析**：Redis 默认内存淘汰策略是 noeviction（不淘汰），当内存达到 maxmemory 限制时，写入操作会返回错误。生产环境通常建议配置为 allkeys-lru，从所有 key 中淘汰最近最少使用的，保证缓存服务的可用性。

> 📖 **参考链接**：[Redis 官方文档 - Eviction](https://redis.io/docs/reference/eviction/) -- 内存淘汰策略（noeviction/LRU/LFU）详解

---

### 12. ★★ 以下关于 Redis 分布式锁，说法错误的是？
A. 加锁用 SET NX EX  B. 解锁用 DEL 命令  C. 解锁应用 Lua 脚本保证原子性  D. 锁的 value 应设唯一标识

**答案：B**

**解析**：直接用 DEL 命令解锁是错误的，因为可能误删别人的锁。正确的做法是使用 Lua 脚本先 GET 判断 value 是否为自己设置的 UUID，再执行 DEL，保证原子性。如果锁已过期被其他线程获取，直接 DEL 会删除别人的锁，导致并发安全问题。

> 📖 **参考链接**：[Redis 官方文档 - Distributed Locks](https://redis.io/docs/manual/patterns/distributed-locks/) -- Redlock 分布式锁官方说明与 Lua 原子性释放

---

### 13. ★★ Redis 主从复制的全量复制使用什么机制？
A. 逐条命令同步  B. RDB 快照  C. AOF 文件  D. 日志文件

**答案：B**

**解析**：全量复制时，主节点执行 BGSAVE 生成 RDB 快照，将 RDB 文件发送给从节点。从节点加载 RDB 后，主节点再将复制积压缓冲区中的增量命令发送给从节点。RDB 作为全量数据的载体，可以高效地将初始数据同步到从节点。

> 📖 **参考链接**：[Redis 官方文档 - Replication](https://redis.io/docs/management/replication/) -- 全量复制 RDB 快照同步机制说明

---

### 14. ★★★ Redis 的 HyperLogLog 统计 UV 的误差率约为？
A. 0.01%  B. 0.81%  C. 5%  D. 10%

**答案：B**

**解析**：HyperLogLog 的标准误差率约为 0.81%。它使用概率算法，用极小的内存（12KB）即可统计 2^64 个元素的基数。对于亿级 UV 统计场景，0.81% 的误差通常是可以接受的，而其内存占用仅 12KB，优势巨大。

> 📖 **参考链接**：[Redis 官方文档 - HyperLogLog](https://redis.io/docs/data-types/hyperloglogs/) -- HyperLogLog 基数统计与 0.81% 误差率说明

---

### 15. ★★★ 以下关于 Redis Cluster，说法正确的是？
A. 使用一致性哈希  B. 使用哈希槽  C. 是中心化架构  D. 不支持在线扩容

**答案：B**

**解析**：Redis Cluster 使用哈希槽（Hash Slot）而非一致性哈希。一致性哈希在节点变化时只需迁移少量数据，而哈希槽在节点变化时迁移整个槽的数据。Redis Cluster 是去中心化架构（Gossip 协议），支持在线扩缩容（通过 reshard 迁移槽）。

> 📖 **参考链接**：[Redis 官方文档 - Cluster](https://redis.io/docs/management/scaling/) -- 哈希槽分片 vs 一致性哈希对比说明

---

### 16. ★★ Redis 的 Pipeline 的作用是？
A. 保证原子性  B. 减少 RTT（往返时间）  C. 事务回滚  D. 数据持久化

**答案：B**

**解析**：Pipeline（管道）将多个命令打包发送，服务端一次性返回所有结果，减少客户端与服务端之间的网络往返次数（RTT）。注意 Pipeline 不保证原子性（事务才保证），它只是减少网络开销的性能优化手段。

> 📖 **参考链接**：[Redis 官方文档 - Pipelining](https://redis.io/docs/manual/pipelining/) -- Pipeline 减少 RTT 网络往返原理说明

---

### 17. ★★ 以下哪个不是 Redis 的持久化方式？
A. RDB  B. AOF  C. 混合持久化  D. WAL（预写日志）

**答案：D**

**解析**：WAL（Write-Ahead Logging）是关系型数据库（如 PostgreSQL）和部分 NoSQL（如 RocksDB）使用的持久化机制，不是 Redis 的持久化方式。Redis 的持久化方式包括 RDB（快照）、AOF（追加日志）和混合持久化（RDB + AOF）。

> 📖 **参考链接**：[Redis 官方文档 - Persistence](https://redis.io/docs/management/persistence/) -- Redis 持久化方式（RDB/AOF/混合持久化）完整说明

---

### 18. ★★★ Redis 6.0 引入多线程主要用于？
A. 命令执行  B. 网络 IO 读写  C. 数据持久化  D. 主从同步

**答案：B**

**解析**：Redis 6.0 引入的多线程仅用于网络 IO 的读写（解析请求和写回响应），命令执行仍然是单线程的。这是因为 Redis 的性能瓶颈主要在网络 IO 而非 CPU 计算，单线程执行命令避免了锁竞争和上下文切换的开销。

> 📖 **参考链接**：[Redis 官方 FAQ - Multiple threads](https://redis.io/docs/get-started/faq/) -- Redis 6.0 多线程网络 IO 模型说明

---

### 19. ★★ Redis 的过期键删除策略是？
A. 定时删除  B. 惰性删除 + 定期删除  C. 立即删除  D. 手动删除

**答案：B**

**解析**：Redis 采用惰性删除 + 定期删除的组合策略。惰性删除：访问 key 时检查是否过期，过期则删除；定期删除：每隔一段时间（默认 100ms）随机抽取一批设置了过期时间的 key，检查并删除其中已过期的。这种组合在 CPU 开销和内存占用之间取得了平衡。

> 📖 **参考链接**：[Redis 官方文档 - Key eviction](https://redis.io/docs/reference/eviction/) -- 惰性删除 + 定期删除过期键策略说明

---

### 20. ★★★ 缓存雪崩的解决方案不包括？
A. 过期时间加随机值  B. Redis 集群高可用  C. 服务限流降级  D. 使用 String 代替 Hash

**答案：D**

**解析**：使用 String 代替 Hash 是数据结构选择问题，与缓存雪崩无关。缓存雪崩的解决方案包括：过期时间加随机值（避免大量 key 同时过期）、Redis 集群高可用（避免单点故障）、服务限流降级（保护数据库在缓存不可用时不被压垮）。

> 📖 **参考链接**：[Redis 官方文档 - Patterns](https://redis.io/docs/manual/patterns/) -- 缓存雪崩/击穿/穿透解决方案与最佳实践

---

## 二、简答题（10 题，附要点）

### 1. ★★ Redis 五种基本数据类型的底层实现？

**要点**：

| 数据类型 | 底层实现 | 编码切换条件 |
|---------|---------|------------|
| String | SDS（int/embstr/raw 编码） | 长度 <= 44 字节用 embstr，否则 raw |
| Hash | ziplist / hashtable | 元素 < 512 且所有 value < 64 字节用 ziplist |
| List | quicklist（3.2+） | 前身是 linkedlist + ziplist |
| Set | intset / hashtable | 元素全为整数且数量 < 512 用 intset |
| ZSet | ziplist / skiplist + dict | 元素 < 128 且所有 member < 64 字节用 ziplist |

Hash 的 hashtable 使用渐进式 rehash 进行扩容，避免一次性阻塞。

> 📖 **参考链接**：
> - [Redis 官方文档 - Data types](https://redis.io/docs/data-types/) -- 五种基本数据类型官方说明汇总
> - [Redis 官方文档 - Data type internals](https://redis.io/docs/reference/internals/) -- 各数据类型底层编码与切换条件

---

### 2. ★★ 持久化 RDB 和 AOF 的区别？

**要点**：

- **RDB**：定时快照持久化，生成二进制文件。优点是文件小、恢复快，缺点是可能丢失最后一次快照后的数据，大数据量时 `fork()` 耗时长。
- **AOF**：追加写命令日志，有三种写入策略（always/everysec/no）。优点是数据安全性更高，缺点是文件大、恢复慢。
- **混合持久化**（Redis 4.0+）：结合两者优势，AOF 文件前半部分为 RDB 格式，后半部分为 AOF 增量命令，兼顾恢复速度与数据安全。

> 📖 **参考链接**：[Redis 官方文档 - Persistence](https://redis.io/docs/management/persistence/) -- RDB / AOF / 混合持久化对比与配置说明

---

### 3. ★★ 哨兵模式的故障转移流程？

**要点**：

1. **SDOWN（主观下线）**：单个 Sentinel 在 `down-after-milliseconds` 时间内未收到主节点 PONG 回复，标记主观下线
2. **ODOWN（客观下线）**：超过 `quorum` 个 Sentinel 都认为主节点主观下线，标记客观下线
3. **Leader 选举**：Sentinel 之间通过 Raft 协议选举 Leader 来执行故障转移，先到先得，需半数以上同意
4. **选出新主节点**：从健康的从节点中选择优先级最高（`replica-priority` 最小）、复制偏移最大、run_id 最小的节点
5. **通知从节点**：新主节点执行 `REPLICAOF NO ONE` 升级，其他从节点执行 `REPLICAOF` 指向新主节点
6. **通知客户端**：通过 Pub/Sub 通道通知客户端更新主节点连接地址

> 📖 **参考链接**：[Redis 官方文档 - Sentinel](https://redis.io/docs/management/sentinel/) -- 哨兵 SDOWN/ODOWN/Raft 选举/故障转移完整流程

---

### 4. ★★ 缓存穿透 / 击穿 / 雪崩的解决方案？

**要点**：

| 问题 | 定义 | 核心解决方案 |
|------|------|-------------|
| 缓存穿透 | 查询不存在的数据，缓存和数据库都查不到 | 布隆过滤器（前置拦截） + 缓存空值（短过期时间） + 参数校验 |
| 缓存击穿 | 热点 key 过期瞬间，大量并发请求打到数据库 | 互斥锁（SETNX，第一个请求重建缓存） + 逻辑过期（返回旧值 + 异步更新） |
| 缓存雪崩 | 大量 key 同时过期或 Redis 集群宕机 | 过期时间加随机值（打散过期时间） + 集群高可用（主从+哨兵） + 限流降级 |

**完整代码示例：**

#### 一、手写布隆过滤器（两种实现）

**实现1：基于 Google Guava 的布隆过滤器：**

```java
import com.google.common.hash.BloomFilter;
import com.google.common.hash.Funnels;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.nio.charset.StandardCharsets;

/**
 * Guava 布隆过滤器实现
 * 用途：前置拦截缓存穿透 —— 判断请求的 key 是否可能存在于数据库中
 * 原理：使用多个哈希函数将元素映射到位数组中的多个位置
 * 
 * 注意：布隆过滤器不存在误判漏报（false negative），即：
 *  - 返回 false：元素一定不存在（100% 确定）
 *  - 返回 true：元素可能存在（有误判率，需查数据库确认）
 */
@Component
public class GuavaBloomFilter {

    // 预期插入数据量：100 万
    private static final int EXPECTED_INSERTIONS = 1_000_000;
    // 误判率：0.01（1%），越小越精确但占内存越多
    private static final double FPP = 0.01;

    private BloomFilter<String> bloomFilter;

    @PostConstruct
    public void init() {
        // 创建布隆过滤器，指定预期数据量和误判率
        bloomFilter = BloomFilter.create(
            Funnels.stringFunnel(StandardCharsets.UTF_8),
            EXPECTED_INSERTIONS,
            FPP
        );

        // 初始化：从数据库加载所有已有数据 ID 到布隆过滤器
        loadDataFromDB();
    }

    /**
     * 从数据库加载已有数据，预热布隆过滤器
     */
    private void loadDataFromDB() {
        // 实际项目中使用分页查询，避免一次性加载过多数据
        // List<String> allIds = mapper.selectAllIds();
        // allIds.forEach(bloomFilter::put);
        
        // 示例数据
        String[] sampleIds = {"user:001", "user:002", "product:1001", "product:1002"};
        for (String id : sampleIds) {
            bloomFilter.put(id);
        }
        System.out.println("布隆过滤器预热完成，已加载 " + sampleIds.length + " 条数据");
    }

    /**
     * 判断 key 是否可能存在
     * @return true=可能存在（需查数据库），false=一定不存在（直接拒绝）
     */
    public boolean mightContain(String key) {
        return bloomFilter.mightContain(key);
    }

    /**
     * 新增数据时同步更新布隆过滤器
     * 注意：布隆过滤器不支持删除，如需删除场景请使用 Counting Bloom Filter
     */
    public void add(String key) {
        bloomFilter.put(key);
    }
}
```

**实现2：基于 BitSet 手写简易布隆过滤器（不依赖 Guava）：**

```java
import java.util.BitSet;
import java.util.Objects;

/**
 * 手写布隆过滤器（基于 JDK BitSet）
 * 使用多个哈希函数降低误判率
 * 
 * 核心公式：
 *  - 位数组大小 m = -(n * ln(p)) / (ln(2)^2)
 *  - 哈希函数个数 k = (m / n) * ln(2)
 *  - 其中 n = 预期数据量，p = 目标误判率
 */
public class CustomBloomFilter {

    private final BitSet bitSet;
    private final int size;        // 位数组大小
    private final int hashCount;   // 哈希函数个数
    private int insertedCount;     // 已插入元素数量

    /**
     * @param expectedInsertions 预期插入数量
     * @param falsePositiveRate  期望误判率（如 0.01 代表 1%）
     */
    public CustomBloomFilter(int expectedInsertions, double falsePositiveRate) {
        // 计算最优位数组大小
        this.size = (int) (-expectedInsertions * Math.log(falsePositiveRate) / (Math.log(2) * Math.log(2)));
        // 计算最优哈希函数个数
        this.hashCount = Math.max(1, (int) (size / (double) expectedInsertions * Math.log(2)));
        this.bitSet = new BitSet(size);
        this.insertedCount = 0;
    }

    /**
     * 添加元素
     */
    public void add(String key) {
        int[] hashes = getHashes(key);
        for (int hash : hashes) {
            bitSet.set(Math.abs(hash % size));
        }
        insertedCount++;
    }

    /**
     * 判断元素是否可能存在
     */
    public boolean mightContain(String key) {
        int[] hashes = getHashes(key);
        for (int hash : hashes) {
            if (!bitSet.get(Math.abs(hash % size))) {
                return false; // 有一个位为 0，一定不存在
            }
        }
        return true; // 所有位都为 1，可能存在
    }

    /**
     * 生成多个哈希值（通过双重哈希模拟多个哈希函数）
     * 原理：hash_i = hash1 + i * hash2
     */
    private int[] getHashes(String key) {
        int[] hashes = new int[hashCount];
        int hash1 = Objects.hashCode(key);
        int hash2 = key.hashCode() ^ (key.hashCode() >>> 16); // 干扰函数
        for (int i = 0; i < hashCount; i++) {
            hashes[i] = hash1 + i * hash2;
        }
        return hashes;
    }

    public int getSize() {
        return size;
    }

    public int getInsertedCount() {
        return insertedCount;
    }

    // ====== 测试用例 ======
    public static void main(String[] args) {
        CustomBloomFilter filter = new CustomBloomFilter(100000, 0.01);
        
        // 添加元素
        filter.add("user:1001");
        filter.add("user:1002");
        filter.add("user:1003");
        
        // 测试
        System.out.println(filter.mightContain("user:1001")); // true（存在）
        System.out.println(filter.mightContain("user:9999")); // false（不存在）
        System.out.println("位数组大小: " + filter.getSize());
        System.out.println("哈希函数数量: " + filter.hashCount);
        System.out.println("已插入数量: " + filter.getInsertedCount());
    }
}
```

#### 二、缓存穿透 / 击穿 / 雪崩 —— 完整解决方案代码

```java
import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.Random;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 缓存服务 —— 集成穿透、击穿、雪崩三重防护
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CacheProtectionService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final GuavaBloomFilter bloomFilter;

    /** 空值缓存过期时间（秒） */
    private static final long NULL_VALUE_TTL = 60;
    /** 互斥锁过期时间（秒） */
    private static final long LOCK_TTL = 30;
    /** 基础过期时间（秒） */
    private static final long BASE_TTL = 3600;
    /** 随机过期时间范围（秒） */
    private static final long RANDOM_TTL_RANGE = 600;

    /**
     * 解决【缓存穿透】：
     * 1. 布隆过滤器前置拦截不存在的 key
     * 2. 缓存空值，设置短过期时间
     */
    private boolean isPenetrationDefense(String key) {
        // 第一层：布隆过滤器判断
        if (!bloomFilter.mightContain(key)) {
            log.warn("布隆过滤器拦截非法 key: {}", key);
            return false; // 直接返回不存在，不查数据库
        }
        return true; // 可能存在，继续往下查
    }

    /**
     * 解决【缓存击穿】：
     * 使用 SETNX 互斥锁，保证同一个 key 只有一个线程回源数据库
     */
    private Object hotKeyMutexLoad(String key, String cacheKey) {
        String lockKey = "lock:hot:" + key;
        Object cachedValue = redisTemplate.opsForValue().get(cacheKey);
        if (cachedValue != null) {
            return cachedValue; // 双重检查，已被其他线程重建
        }

        try {
            // SETNX 加锁，只允许一个线程执行重建
            Boolean locked = redisTemplate.opsForValue()
                .setIfAbsent(lockKey, "1", LOCK_TTL, TimeUnit.SECONDS);
            
            if (Boolean.TRUE.equals(locked)) {
                // 获得锁，回源数据库
                Object dbValue = queryFromDB(key);
                if (dbValue != null) {
                    redisTemplate.opsForValue().set(cacheKey, dbValue, BASE_TTL, TimeUnit.SECONDS);
                } else {
                    // 缓存空值防穿透
                    redisTemplate.opsForValue().set(cacheKey, "NULL", NULL_VALUE_TTL, TimeUnit.SECONDS);
                }
                return dbValue;
            } else {
                // 未获得锁，等待后重试
                Thread.sleep(100);
                return redisTemplate.opsForValue().get(cacheKey);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return null;
        } finally {
            // 释放锁（仅删除自己加的锁，生产环境建议用 Lua 脚本）
            redisTemplate.delete(lockKey);
        }
    }

    /**
     * 解决【缓存雪崩】：
     * 过期时间 = 基础过期时间 + 随机值（打散过期时间，避免大量 key 同时过期）
     */
    private long getExpireTimeWithRandom() {
        return BASE_TTL + new Random().nextInt((int) RANDOM_TTL_RANGE);
    }

    /**
     * 对外查询接口 —— 集成三重防护
     */
    public Object query(String key) {
        String cacheKey = "cache:data:" + key;

        // ===== 1. 查缓存 =====
        Object cachedValue = redisTemplate.opsForValue().get(cacheKey);
        if (cachedValue != null) {
            if ("NULL".equals(cachedValue)) {
                return null; // 空值缓存，直接返回
            }
            return cachedValue;
        }

        // ===== 2. 缓存穿透防护 =====
        if (!isPenetrationDefense(key)) {
            return null;
        }

        // ===== 3. 缓存击穿防护（互斥锁回源） =====
        Object dbValue = hotKeyMutexLoad(key, cacheKey);
        if (dbValue != null) {
            // ===== 4. 缓存雪崩防护（随机过期时间） =====
            redisTemplate.opsForValue().set(cacheKey, dbValue, getExpireTimeWithRandom(), TimeUnit.SECONDS);
            return dbValue;
        }

        return null;
    }

    /**
     * 模拟数据库查询
     */
    private Object queryFromDB(String key) {
        // 实际项目中调用 Mapper 查询
        return "DB_VALUE_FOR_" + key;
    }
}
```

> **生活化类比：缓存穿透/击穿/雪崩 = 银行网点三种异常** —— 把 Redis 缓存想象成银行大堂的自助查询机，数据库是柜台。缓存穿透：有人反复查一个根本不存在的账号（查无此人），查询机查不到只能去柜台确认，柜台也查不到——机器白忙活还堵了柜台；解决：门口保安拿黑名单本（布隆过滤器）先拦，或机器直接显示"查无此号"（缓存空值）。缓存击穿：某个热门 VIP 账号查询机突然宕机（热点 key 过期），所有人瞬间全涌去柜台；解决：柜台前只放一个人排队、其他人等结果（互斥锁），或机器挂个"稍后更新"的旧结果先应付（逻辑过期）。缓存雪崩：整排查询机同时断电（大量 key 同时过期 / 集群宕机），所有人挤爆柜台；解决：给各机器错峰断电（过期时间加随机值）、多备几排机器（集群高可用）、柜台设限流护栏（限流降级）。

> 📖 **参考链接**：
> - [Redis 官方文档 - Patterns](https://redis.io/docs/manual/patterns/) -- 缓存穿透/击穿/雪崩解决方案官方说明
> - [Redis 官方文档 - RedisBloom](https://redis.io/docs/data-types/probabilistic/bloom-filter/) -- 布隆过滤器防穿透模块

---

### 5. ★★ Redis 分布式锁的实现？

**要点**：

- **加锁**：`SET key UUID NX EX 30`，value 为 UUID 防止误删
- **解锁**：Lua 脚本先 GET 判断 value 再 DEL，保证原子性（不能直接 DEL）
- **锁续期**：Redisson Watchdog 看门狗，每 10 秒续期到 30 秒，防止业务超时锁提前释放
- **可重入**：基于 Redis Hash 结构，HINCRBY 递增，解锁时递减，计数归零删除 key
- **Redlock**：多节点分布式锁，半数以上节点加锁成功且总耗时 < 锁有效期，实践中单机 Redis + 哨兵已足够

**完整代码示例：**

#### 一、基于 SETNX + Lua 脚本手写分布式锁

```java
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * 手写 Redis 分布式锁（基于 SETNX + Lua 脚本）
 * 
 * 核心原则：
 * 1. 加锁必须设置过期时间（SET key value NX EX 30），防止死锁
 * 2. value 必须为唯一标识（UUID），防止误删别人的锁
 * 3. 解锁必须用 Lua 脚本保证原子性（先 GET 判断再 DEL）
 */
@Slf4j
@Component
public class RedisDistributedLock {

    private final RedisTemplate<String, String> redisTemplate;

    /** 锁的过期时间（秒） */
    private static final long LOCK_EXPIRE = 30L;
    /** 获取锁的最大等待时间（毫秒） */
    private static final long MAX_WAIT_MS = 5000L;
    /** 重试间隔（毫秒） */
    private static final long RETRY_INTERVAL_MS = 100L;

    public RedisDistributedLock(RedisTemplate<String, String> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    /**
     * 尝试获取锁
     * @param lockKey 锁的 key
     * @return 锁的唯一标识（用于解锁），null 表示获取失败
     */
    public String tryLock(String lockKey) {
        String lockValue = UUID.randomUUID().toString(); // 唯一标识
        long startTime = System.currentTimeMillis();

        while (System.currentTimeMillis() - startTime < MAX_WAIT_MS) {
            // SET key value NX EX 30（原子操作：仅在 key 不存在时设置，并设置过期时间）
            Boolean success = redisTemplate.opsForValue()
                .setIfAbsent(lockKey, lockValue, LOCK_EXPIRE, TimeUnit.SECONDS);

            if (Boolean.TRUE.equals(success)) {
                log.info("获取锁成功: key={}, value={}", lockKey, lockValue);
                return lockValue;
            }

            // 自旋等待
            try {
                Thread.sleep(RETRY_INTERVAL_MS);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return null;
            }
        }

        log.warn("获取锁超时: key={}", lockKey);
        return null;
    }

    /**
     * 释放锁（Lua 脚本保证原子性）
     * 先 GET 判断 value 是否为自己设置的 UUID，再 DEL
     * 防止误删其他线程的锁
     * 
     * @param lockKey   锁的 key
     * @param lockValue 锁的唯一标识（加锁时返回的 UUID）
     * @return true=释放成功，false=释放失败
     */
    public boolean unlock(String lockKey, String lockValue) {
        // Lua 脚本：原子性执行 GET + 判断 + DEL
        String luaScript =
            "if redis.call('GET', KEYS[1]) == ARGV[1] then " +
            "    return redis.call('DEL', KEYS[1]) " +
            "else " +
            "    return 0 " +
            "end";

        DefaultRedisScript<Long> script = new DefaultRedisScript<>();
        script.setScriptText(luaScript);
        script.setResultType(Long.class);

        Long result = redisTemplate.execute(
            script,
            Collections.singletonList(lockKey),
            lockValue
        );

        boolean success = result != null && result == 1L;
        if (success) {
            log.info("释放锁成功: key={}", lockKey);
        } else {
            log.warn("释放锁失败（锁可能已过期或被其他线程持有）: key={}", lockKey);
        }
        return success;
    }

    // ====== 使用示例 ======
    public void businessLogicWithLock(String lockKey) {
        String lockValue = tryLock(lockKey);
        if (lockValue == null) {
            throw new RuntimeException("获取锁失败，请稍后重试");
        }

        try {
            // 执行业务逻辑
            doBusiness();
        } finally {
            // 释放锁（必须放在 finally 中）
            unlock(lockKey, lockValue);
        }
    }

    private void doBusiness() {
        // 实际业务逻辑
    }
}
```

#### 二、基于 Redisson 的分布式锁（生产推荐）

```java
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RLock;
import org.redisson.api.RReadWriteLock;
import org.redisson.api.RedissonClient;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;

/**
 * Redisson 分布式锁 —— 生产环境推荐方案
 * 
 * 优势：
 * 1. Watchdog 看门狗自动续期：默认每 10 秒续期到 30 秒，防止业务超时锁提前释放
 * 2. 可重入锁：基于 Redis Hash 结构，HINCRBY 记录重入次数
 * 3. 读写锁：保证并发读，排他写
 * 4. 公平锁：按申请顺序获取锁
 * 5. 联锁/红锁：多节点分布式锁
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RedissonLockService {

    private final RedissonClient redissonClient;

    /**
     * 普通分布式锁（可重入 + Watchdog 自动续期）
     * 
     * 使用方式：
     * lock.lock()                  // 阻塞获取锁，Watchdog 自动续期
     * lock.lock(30, TimeUnit.SECONDS)  // 指定过期时间，不自动续期
     * lock.tryLock()               // 非阻塞尝试获取锁
     * lock.tryLock(10, 30, TimeUnit.SECONDS) // 最多等待 10 秒，锁有效期 30 秒
     */
    public void executeWithLock(String lockKey, Runnable task) {
        RLock lock = redissonClient.getLock(lockKey);
        
        try {
            // 尝试获取锁：最多等待 10 秒，锁有效期 30 秒
            boolean acquired = lock.tryLock(10, 30, TimeUnit.SECONDS);
            if (!acquired) {
                log.error("获取分布式锁失败: {}", lockKey);
                throw new RuntimeException("系统繁忙，请稍后重试");
            }

            // 执行业务逻辑
            log.info("获取锁成功，执行业务: {}", lockKey);
            task.run();

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("获取锁被中断", e);
        } finally {
            // 判断锁是否由当前线程持有，防止 IllegalMonitorStateException
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
                log.info("释放锁成功: {}", lockKey);
            }
        }
    }

    /**
     * 读写锁：读锁不互斥，写锁互斥
     * 场景：商品信息读取（并发读） vs 商品信息修改（排他写）
     */
    public Object executeWithReadWriteLock(String lockKey, Runnable writeTask) {
        RReadWriteLock rwLock = redissonClient.getReadWriteLock(lockKey);
        RLock writeLock = rwLock.writeLock();

        try {
            writeLock.lock(30, TimeUnit.SECONDS);
            writeTask.run();
            return "SUCCESS";
        } finally {
            if (writeLock.isHeldByCurrentThread()) {
                writeLock.unlock();
            }
        }
    }

    /**
     * 公平锁：按申请顺序获取锁，避免线程饥饿
     */
    public void executeWithFairLock(String lockKey, Runnable task) {
        RLock fairLock = redissonClient.getFairLock(lockKey);
        
        try {
            fairLock.lock(30, TimeUnit.SECONDS);
            task.run();
        } finally {
            if (fairLock.isHeldByCurrentThread()) {
                fairLock.unlock();
            }
        }
    }

    /**
     * 联锁（MultiLock）：多个独立的 Redis 节点同时加锁
     * 场景：高可靠性场景，如金融交易
     */
    public void executeWithMultiLock(String lockKey1, String lockKey2, String lockKey3, Runnable task) {
        RLock lock1 = redissonClient.getLock(lockKey1);
        RLock lock2 = redissonClient.getLock(lockKey2);
        RLock lock3 = redissonClient.getLock(lockKey3);
        RLock multiLock = redissonClient.getMultiLock(lock1, lock2, lock3);

        try {
            multiLock.lock(30, TimeUnit.SECONDS);
            task.run();
        } finally {
            multiLock.unlock();
        }
    }
}
```

**Redisson 配置类：**

```java
import org.redisson.Redisson;
import org.redisson.api.RedissonClient;
import org.redisson.config.Config;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Redisson 客户端配置
 */
@Configuration
public class RedissonConfig {

    @Bean(destroyMethod = "shutdown")
    public RedissonClient redissonClient() {
        Config config = new Config();
        
        // 单节点模式
        config.useSingleServer()
            .setAddress("redis://127.0.0.1:6379")
            .setPassword("your_password")            // 密码（无密码则注释掉）
            .setDatabase(0)                           // 数据库索引
            .setConnectionPoolSize(64)                 // 连接池大小
            .setConnectionMinimumIdleSize(10)          // 最小空闲连接
            .setIdleConnectionTimeout(10000)           // 空闲连接超时（毫秒）
            .setConnectTimeout(10000)                  // 连接超时（毫秒）
            .setTimeout(3000)                          // 命令超时（毫秒）
            .setRetryAttempts(3)                       // 命令重试次数
            .setRetryInterval(1500)                    // 重试间隔（毫秒）
            .setPingConnectionInterval(30000);         // Ping 间隔（毫秒）

        // 哨兵模式（高可用）
        // config.useSentinelServers()
        //     .setMasterName("mymaster")
        //     .addSentinelAddress("redis://127.0.0.1:26379")
        //     .addSentinelAddress("redis://127.0.0.1:26380");

        // 集群模式
        // config.useClusterServers()
        //     .addNodeAddress("redis://127.0.0.1:7000")
        //     .addNodeAddress("redis://127.0.0.1:7001")
        //     .addNodeAddress("redis://127.0.0.1:7002");

        return Redisson.create(config);
    }
}
```

**Maven 依赖：**

```xml
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <version>3.24.3</version>
</dependency>
```

> **生活化类比：分布式锁 = 公共洗手间的隔间门锁** —— 单机锁像自家厕所门锁，一个进程内自己锁自己就行；分布式锁像商场的公共洗手间隔间门锁——多个进程（顾客）抢同一个隔间（共享资源），锁必须放在所有人都能看到的"前台"（Redis）而不是各自家里。进门先看门牌是否被占（SET NX），占用时挂上写了自己名字的牌子（UUID value）防止走错门误开别人的锁（误删）；怕自己占太久门锁自动弹开（过期时间 EX），但又怕业务没办完锁先弹了，所以雇个保洁定时续门锁（Watchdog 看门狗续期）。开门时必须"看一眼牌子是不是自己的名字再开"（Lua 脚本判断 + DEL 原子操作），不能闭眼直接开门。

> 📖 **参考链接**：
> - [Redis 官方文档 - Distributed Locks](https://redis.io/docs/manual/patterns/distributed-locks/) -- Redlock 分布式锁官方说明
> - [Redis 官方文档 - EVAL](https://redis.io/commands/eval/) -- Lua 脚本保证解锁原子性

---

### 6. ★★ Redis 集群的哈希槽机制？

**要点**：

- 16384 个哈希槽，通过 `CRC16(key) % 16384` 定位槽
- 每个主节点负责一部分槽，集群启动时自动分配
- 去中心化 Gossip 协议交换节点状态，无需中心节点
- 客户端重定向：MOVED（永久迁移，更新缓存） vs ASK（临时迁移，仅本次转发）
- Hash Tag（`{...}`）确保相关 key 落在同一槽，支持批量操作

> 📖 **参考链接**：[Redis 官方文档 - Cluster](https://redis.io/docs/management/scaling/) -- 哈希槽 CRC16 分配与 MOVED/ASK 重定向机制

---

### 7. ★★ 渐进式 rehash 原理？

**要点**：

- Redis 字典维护两个哈希表：ht[0]（当前使用）和 ht[1]（扩容时的目标表）
- `rehashidx` 标记当前迁移进度，-1 表示未在 rehash
- 每次对字典的增删改查操作时，顺带将 rehashidx 对应的桶从 ht[0] 迁移到 ht[1]
- 定时任务（serverCron）每次执行时也会在 1ms 内迁移一部分桶
- 全部迁移完成后，ht[1] 成为新的 ht[0]，rehashidx 重置为 -1
- 查询时先查 ht[0]，再查 ht[1]；新增操作直接写入 ht[1]

> 📖 **参考链接**：[Redis 官方文档 - Hash](https://redis.io/docs/data-types/hashes/) -- Hash 渐进式 rehash 双哈希表迁移机制

---

### 8. ★★ 内存淘汰策略 LRU 和 LFU 的区别？

**要点**：

- **LRU（Least Recently Used）**：淘汰最近最少使用的 key，以「最后访问时间」为判断依据。Redis 使用近似 LRU（随机抽样 N 个 key，淘汰其中最久未使用的），默认抽样 5 个
- **LFU（Least Frequently Used，4.0+）**：淘汰访问频率最低的 key，以「访问频率」为判断依据。解决 LRU 的「偶发性访问」问题，如一个 key 昨天被访问 1000 次但今天未被访问，LRU 可能保留它，而 LFU 会淘汰它
- LFU 使用 24 位记录频率：高 16 位为上次访问时间，低 8 位为对数计数器（随时间衰减）

> 📖 **参考链接**：[Redis 官方文档 - Eviction](https://redis.io/docs/reference/eviction/) -- LRU 近似抽样与 LFU 频率衰减算法说明

---

### 9. ★★ Redis 为什么单线程还这么快？

**要点**：

1. **纯内存操作**：数据读写都在内存中完成，内存访问速度远快于磁盘
2. **IO 多路复用**：使用 epoll（Linux）/ kqueue（BSD）等机制，单线程即可处理大量并发连接
3. **单线程避免锁竞争**：无需考虑并发读写锁，不需要上下文切换
4. **高效数据结构**：SDS、quicklist、skiplist 等数据结构经过精心设计和优化
5. **Redis 6.0 引入多线程**：仅用于网络 IO 读写，命令执行仍为单线程

> 📖 **参考链接**：[Redis 官方 FAQ](https://redis.io/docs/get-started/faq/) -- Redis 单线程高性能与 6.0 多线程 IO 模型说明

---

### 10. ★★★ 如何保证数据库和缓存的双写一致性？

**要点**：

- **Cache Aside 模式**（最常用）：读 → 先查缓存，miss 则查数据库并写缓存；写 → 先更新数据库，再删除缓存（而非更新缓存）
- **为什么删除缓存而非更新**：并发写时更新缓存可能产生 ABA 问题，删除缓存后下次读请求自然加载最新数据
- **延迟双删**：删除缓存 → 更新数据库 → 延迟 N 毫秒 → 再次删除缓存，解决并发读写导致的脏数据
- **Canal 订阅 Binlog**：订阅 MySQL binlog → 解析变更事件 → 异步更新/删除缓存，实现最终一致性，业务代码无侵入
- **强一致性**：需要分布式事务（如 Seata），但会牺牲性能，实际项目中通常接受最终一致性

> 📖 **参考链接**：
> - [Redis 官方文档 - Patterns](https://redis.io/docs/manual/patterns/) -- Cache Aside 模式与延迟双删策略
> - [Redis 官方文档 - Keyspace notifications](https://redis.io/docs/manual/keyspace-notifications/) -- 键空间通知辅助缓存一致性

---

## 三、场景设计题（5 题，附思路）

### 1. ★★ 设计一个排行榜系统（如游戏积分排名）

**思路**：

- **数据结构**：使用 ZSet（有序集合），member 为玩家 ID，score 为积分
- **更新分数**：`ZADD rank <score> <playerId>`（若存在则更新）
- **获取 Top N**：`ZREVRANGE rank 0 <N-1> WITHSCORES`（按 score 降序）
- **查询玩家排名**：`ZREVRANK rank <playerId>`（升序排名，即第几名）
- **查询玩家分数**：`ZSCORE rank <playerId>`
- **百万级用户**：ZSet 底层使用 skiplist + dict，查询和更新复杂度 O(logN)，百万级可轻松应对
- **亿级用户**：需按区间分片，如按 score 范围分多个 ZSet（rank:0-1000、rank:1001-2000...），或按用户 ID 哈希分片

> 📖 **参考链接**：[Redis 官方文档 - Sorted Set](https://redis.io/docs/data-types/sorted-sets/) -- ZSet 排行榜场景命令（ZADD/ZREVRANGE/ZREVRANK）

---

### 2. ★★★ 设计一个分布式限流器（滑动窗口）

**思路**：

- **数据结构**：使用 ZSet，score 为请求时间戳，member 为唯一请求 ID（如 UUID）
- **核心流程**：
  1. 记录请求：`ZADD limiter:<api> <timestamp> <requestId>`
  2. 清理过期窗口：`ZREMRANGEBYSCORE limiter:<api> 0 <currentTime - windowSize>`
  3. 判断是否超限：`ZCARD limiter:<api>`，若 >= 限流阈值则拒绝请求
- **原子性保证**：以上三步需用 Lua 脚本封装，保证原子执行
- **Lua 脚本示例**：

```lua
local key = KEYS[1]
local window = tonumber(ARGV[1])  -- 窗口大小（毫秒）
local limit = tonumber(ARGV[2])   -- 限流阈值
local now = tonumber(ARGV[3])     -- 当前时间戳
local requestId = ARGV[4]         -- 请求 ID

-- 清理过期数据
redis.call("ZREMRANGEBYSCORE", key, 0, now - window)
-- 获取当前窗口内请求数
local count = redis.call("ZCARD", key)
if count < limit then
    redis.call("ZADD", key, now, requestId)
    return 1  -- 放行
else
    return 0  -- 限流
end
```

- 相比于固定窗口，滑动窗口的限流更加平滑，不会出现窗口边界流量突增的问题

> 📖 **参考链接**：[Redis 官方文档 - EVAL](https://redis.io/commands/eval/) -- Lua 脚本保证限流原子性执行

---

### 3. ★★ 设计一个延迟队列（如订单超时取消）

**思路**：

- **数据结构**：使用 ZSet，score 为执行时间戳（毫秒），member 为任务 JSON（包含订单 ID、任务类型等）
- **添加延迟任务**：`ZADD delay_queue <executeTimestamp> <taskJson>`
- **定时消费任务**：定时任务（如每秒执行一次）
  ```bash
  ZRANGEBYSCORE delay_queue 0 <currentTime> LIMIT 0 100
  ```
  获取当前时间之前的所有到期任务
- **处理任务**：遍历到期任务，执行对应业务逻辑（如取消订单），成功处理后 `ZREM delay_queue <taskJson>`
- **原子性消费**：使用 Lua 脚本将「获取到期任务 + 删除」合并为原子操作，避免多实例重复消费
- **可靠性保障**：处理失败的任务可保留在 ZSet 中，等待下次调度；或设置最大重试次数后移入死信队列

> 📖 **参考链接**：[Redis 官方文档 - Sorted Set](https://redis.io/docs/data-types/sorted-sets/) -- ZSet 延迟队列场景命令（ZRANGEBYSCORE/ZREM）

---

### 4. ★★★ 设计一个高并发秒杀系统

**思路**：

- **缓存预热**：秒杀开始前，将商品库存加载到 Redis（`SET stock:productId <totalStock>`）
- **原子扣减库存**：使用 Lua 脚本保证原子性
  ```lua
  local key = KEYS[1]
  local stock = tonumber(redis.call("GET", key))
  if stock and stock > 0 then
      redis.call("DECR", key)
      return 1  -- 扣减成功
  else
      return 0  -- 库存不足
  end
  ```
- **消息队列异步下单**：扣减库存成功后，将下单请求写入消息队列（Kafka/RabbitMQ），异步处理订单创建、支付等后续流程
- **限流防刷**：在网关层或业务层对用户请求进行限流（如单个用户 QPS 限制），防止脚本刷单
- **前端优化**：按钮防重复点击、验证码校验、静态资源 CDN 加速
- **兜底方案**：Redis 故障时降级为数据库扣减库存（性能差但能保证可用）

> 📖 **参考链接**：[Redis 官方文档 - EVAL](https://redis.io/commands/eval/) -- Lua 脚本保证秒杀库存原子扣减

---

### 5. ★★ 设计一个亿级 UV 统计系统

**思路**：

- **数据结构**：使用 HyperLogLog（PFADD 添加，PFCOUNT 统计），标准误差 0.81%，内存占用仅 12KB
- **按日期分组**：
  ```bash
  PFADD uv:20250101 userId1 userId2 userId3 ...
  PFCOUNT uv:20250101  # 获取当日 UV
  ```
- **多天合并**：
  ```bash
  PFMERGE uv:202501  uv:20250101 uv:20250102 ... uv:20250131
  PFCOUNT uv:202501  # 获取月 UV
  ```
- **去重存储**：每个用户 ID 只存储一次（HyperLogLog 内部自动去重），无需额外去重逻辑
- **亿级规模**：12KB 内存即可统计 2^64 个元素，亿级 UV 完全没问题
- **局限性**：无法获取具体的用户 ID 列表（只能统计基数），如需精确 UV 需用 Bitmap（内存占用大）或 Set（内存更大）

> 📖 **参考链接**：[Redis 官方文档 - HyperLogLog](https://redis.io/docs/data-types/hyperloglogs/) -- PFADD/PFCOUNT/PFMERGE 命令与 UV 统计场景

---

> 上一篇回顾：[02-Redis高级特性与实战](./02-Redis高级特性与实战.md) -- 全面覆盖持久化、主从复制、哨兵、集群、缓存策略、淘汰策略、分布式锁等核心知识点。
---

> **学习导航**：
> - 返回 [学习路线总览](../../README.md)
> - 本模块其他文件：[01-Redis核心数据结构与底层原理](./01-Redis核心数据结构与底层原理.md) | [02-Redis高级特性与实战](./02-Redis高级特性与实战.md)
> - 实战应用：[电商订单实时统计分析平台](../../extensions/project/01-电商订单实时统计分析平台.md)

