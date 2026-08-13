# Redis 核心数据结构与底层原理 导览

> 定位：五维框架浓缩提炼 01-Redis核心数据结构与底层原理.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./01-Redis核心数据结构与底层原理.md)。
> 前置知识：无

---

## 一、核心概念

### 1.1 Redis 是什么

| 维度 | 内容 |
|------|------|
| 是什么 | 基于内存的高性能键值数据库，ANSI C 编写，采用单线程事件驱动模型。 |
| 能做什么 | 存储丰富数据结构；提供持久化与主从复制；支撑缓存、锁、排行榜、消息队列等场景。 |
| 怎么用 | `redis-server` 启动；`redis-cli` 连接；`SET k v` / `GET k` 读写。 |
| 原理和工作流程 | 数据常驻内存，通过 epoll 多路复用单线程处理命令，避免锁竞争与上下文切换；底层用 SDS、跳跃表、压缩列表等结构支撑高效读写，单机 QPS 可达 10 万级。6.0 后网络读写由多线程处理，命令执行仍单线程以保证原子性。 |
| 缺点 | 全内存导致容量受物理内存限制；持久化与 fork 在大数据量下有阻塞风险；单线程难以利用多核 CPU。 |

### 1.2 与 Memcached 对比

| 维度 | 内容 |
|------|------|
| 是什么 | 将二者在数据结构、持久化、集群等维度的特性对照。 |
| 能做什么 | 区分二者适用边界；为缓存选型提供依据；明确功能扩展点。 |
| 怎么用 | 纯缓存选 Memcached；需丰富结构、持久化、发布订阅选 Redis。 |
| 原理和工作流程 | Redis 支持 String/Hash/List/Set/ZSet/Bitmap/HyperLogLog/GEO/Stream，原生集群 16384 槽，RDB+AOF 持久化；Memcached 仅二进制 String，无持久化，需客户端一致性哈希，多线程模型。现代项目多选 Redis。 |
| 缺点 | Memcached 功能单一无法满足复杂场景；Redis 功能丰富但内存占用与复杂度更高，纯缓存场景不如 Memcached 轻量。 |

### 1.3 单线程为什么快

| 维度 | 内容 |
|------|------|
| 是什么 | 对单线程模型仍能保持高性能的原因解析。 |
| 能做什么 | 解释单线程高性能来源；说明 6.0 多线程引入动机；指导性能调优方向。 |
| 怎么用 | 保持命令简短；避免 `KEYS` 等阻塞命令；6.0 开启 `io-threads 4`。 |
| 原理和工作流程 | 纯内存操作使内存带宽而非 CPU 成瓶颈；epoll 多路复用单线程监听多连接；单线程无锁竞争与上下文切换；SDS、跳跃表等结构针对高性能设计。6.0 因网络 I/O 成瓶颈引入多线程处理读写与协议解析，命令执行仍单线程保原子性。 |
| 缺点 | 单线程无法利用多核计算；大 Key 与全量命令仍会阻塞主线程；6.0 多线程仅缓解网络 I/O，CPU 密集命令无改善。 |

### 1.4 全局命令速查

| 维度 | 内容 |
|------|------|
| 是什么 | 跨数据类型通用的 key 管理命令集合。 |
| 能做什么 | 查询、判断、删除 key；设置与查看过期时间；渐进式遍历键空间。 |
| 怎么用 | `SCAN 0 MATCH user:* COUNT 100`；`EXPIRE k 60`；`TTL k`；`TYPE k`。 |
| 原理和工作流程 | EXISTS/TYPE/DEL 直接操作键空间元数据；EXPIRE 将 key 加入过期字典；TTL 查询过期字典剩余秒数。KEYS 一次性遍历全部 key 为 O(N) 阻塞主线程，SCAN 基于游标分批返回，通过 rehashidx 兼容 rehash 期间遍历。 |
| 缺点 | `KEYS` 在生产阻塞主线程；SCAN 结果可能重复且不保证完整；DEL 大 Key 同步阻塞需用 UNLINK。 |

---

## 二、底层原理

### 2.1 字符串（SDS — Simple Dynamic String）

| 维度 | 内容 |
|------|------|
| 是什么 | 自定义的简单动态字符串结构，替代 C 语言 char[] 作为 String 底层。 |
| 能做什么 | O(1) 取长度；杜绝缓冲区溢出；二进制安全存储；预分配与惰性释放减少 malloc。 |
| 怎么用 | `SET k v`；`INCR k`；`APPEND k suffix`；`STRLEN k`。 |
| 原理和工作流程 | 结构含 len、free、buf[] 三字段，len 记录已用字节使取长 O(1)，free 记录预留空间。扩容时 len<1MB 空间加倍、>=1MB 追加 1MB，缩短时惰性释放保留 free。三种编码：int 存整数、embstr 连续分配（<=44 字节，因 jemalloc 64 字节块减去 16 字节对象头与 4 字节开销）、raw 分两次 malloc。 |
| 缺点 | 预分配带来额外内存占用；embstr 修改会转 raw；大字符串仍占连续内存。 |

### 2.2 哈希（Hash）

| 维度 | 内容 |
|------|------|
| 是什么 | 字段-值映射结构，底层用 ziplist/listpack 或 hashtable 编码。Redis 7.0 已将 ziplist 替换为 listpack。 |
| 能做什么 | 存储对象字段；原子递增字段值；批量读写字段；渐进式遍历大 Hash。 |
| 怎么用 | `HSET k f v`；`HGET k f`；`HINCRBY k f 1`；`HSCAN k 0`。 |
| 原理和工作流程 | 字段数<=512 且单值<=64 字节用 ziplist 连续存储省内存，超阈值转 hashtable 字典 O(1) 查询。ziplist 由 zlbytes/zltail/zllen/entry/zlend 组成，连续内存无指针开销。扩缩容采用渐进式 rehash：维护 ht[0]、ht[1]，每次操作顺带迁移一桶，serverCron 每 1ms 迁移 100 桶，期间查找先 ht[0] 后 ht[1]，新增直接入 ht[1]。负载因子>=1 扩容，<0.1 缩容。 |
| 缺点 | ziplist 插入删除可能连锁更新；rehash 期间双表内存占用翻倍；HGETALL 大 Hash 阻塞主线程。 |

### 2.3 列表（List）

| 维度 | 内容 |
|------|------|
| 是什么 | 有序字符串列表结构，3.2 起统一用 quicklist 实现。 |
| 能做什么 | 头尾 O(1) 增删；阻塞消费实现消息队列；LRANGE 范围获取；LTRIM 保留最近 N 条。 |
| 怎么用 | `LPUSH k v`；`RPOP k`；`BRPOP k 5`；`LRANGE k 0 -1`。 |
| 原理和工作流程 | quicklist 是双向链表与 ziplist 的混合：外层双向链表，每个节点内部是一个 ziplist 压缩存储多个元素。相比纯链表减少指针开销，相比纯 ziplist 限制单节点大小避免连锁更新；中间节点支持 LZF 压缩进一步省内存。前身 3.2 前小数据用 ziplist、大数据用 linkedlist。 |
| 缺点 | 中间随机访问 O(N)；大 List 全量 LRANGE 阻塞；链表节点指针仍有额外开销。 |

### 2.4 集合（Set）

| 维度 | 内容 |
|------|------|
| 是什么 | 不重复元素集合结构，底层用 intset 或 hashtable 编码。 |
| 能做什么 | 元素去重；交集并集差集运算；随机抽奖；标签系统与共同好友计算。 |
| 怎么用 | `SADD k m`；`SINTER k1 k2`；`SRANDMEMBER k 3`；`SCARD k`。 |
| 原理和工作流程 | 全整数且数量<=512 用 intset 有序数组二分查找 O(logN)，超出范围或含非整数转 hashtable。intset 按元素大小选 int16/int32/int64 编码，插入超出当前编码的元素触发整体升级，升级不可逆不支持降级。hashtable 编码 value 为 NULL，仅用键存储。 |
| 缺点 | intset 升级不可逆浪费空间；SMEMBERS 大集合阻塞；集合运算大集合耗内存与 CPU。 |

### 2.5 有序集合（ZSet）

| 维度 | 内容 |
|------|------|
| 是什么 | 按 score 排序且元素唯一的结构，底层用 ziplist 或 skiplist+dict 编码。 |
| 能做什么 | 排行榜 Top N；延迟队列按时间戳轮询；带优先级的消息队列；范围排名查询。 |
| 怎么用 | `ZADD k 100 m`；`ZREVRANGE k 0 9`；`ZRANGEBYSCORE k 0 100`；`ZINCRBY k 5 m`。 |
| 原理和工作流程 | 元素<=128 且成员<=64 字节用 ziplist 按 score 升序紧凑存储，超阈值转 skiplist+dict。skiplist 多层索引链表按 score 排序支持 O(logN) 范围与排名查询，dict 提供 member→score 的 O(1) 查找，二者指针共享 member 与 score 不翻倍。节点随机层高 p=0.25，最高 32 层，期望约 1.33 层。选 skiplist 而非红黑树因其实现简单、范围查询友好、并发锁粒度细。 |
| 缺点 | skiplist 内存额外指针开销；ziplist 大集合连锁更新；全量 ZRANGE 阻塞主线程。 |

### 2.6 高级数据结构

#### 2.6.1 Bitmap（位图）

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 String 的位操作扩展，最大支持 2^32 位（约 512MB）。 |
| 能做什么 | 按位设置与读取；统计置位数量；位运算合并；实现签到、在线状态、布隆过滤器。 |
| 怎么用 | `SETBIT k 5 1`；`GETBIT k 5`；`BITCOUNT k`；`BITOP AND d k1 k2`。 |
| 原理和工作流程 | 以 String 为底层，每个字节 8 位，通过 offset 定位具体位。SETBIT 计算字节与位偏移自动扩展 String，GETBIT 读取对应位。BITCOUNT 按 Popcount 算法统计 1 的个数，BITOP 对多个 Bitmap 按位运算写入目标。签到场景以日期映射 offset，统计即 BITCOUNT。 |
| 缺点 | 稀疏位图浪费内存；offset 过大触发 String 扩容阻塞；不支持直接获取置位元素列表。 |

#### 2.6.2 HyperLogLog

| 维度 | 内容 |
|------|------|
| 是什么 | 概率性基数估算结构，每个 key 仅占 12KB，标准误差 0.81%。 |
| 能做什么 | 统计不重复元素个数；合并多个基数；亿级 UV 去重计数。 |
| 怎么用 | `PFADD k uid`；`PFCOUNT k`；`PFMERGE d s1 s2`。 |
| 原理和工作流程 | 基于伯努利试验，对元素哈希值记录连续前导零的最大长度 k，估算基数约为 2^k。N 个随机比特串中出现 k 个连续前导零的概率约 1/2^k，通过分桶与调和平均降低方差，固定 12KB 内存即可估算 2^64 基数。 |
| 缺点 | 存在约 0.81% 误差不精确；无法取出具体元素；少量元素时估算偏差较大。 |

#### 2.6.3 GEO（地理位置）

| 维度 | 内容 |
|------|------|
| 是什么 | Redis 3.2 引入的地理位置结构，底层基于 ZSet 与 GeoHash 编码。 |
| 能做什么 | 存储经纬度；计算两点距离；按半径查询附近成员；获取 GeoHash 编码。 |
| 怎么用 | `GEOADD k lng lat m`；`GEODIST k m1 m2 km`；`GEORADIUS k lng lat 1 km`。 |
| 原理和工作流程 | 经纬度经 GeoHash 二分逼近编码为 52 位整数存入 ZSet 的 score，member 为成员名。利用 ZSet 的范围查询实现地理位置搜索，相邻区域 GeoHash 编码相近可批量检索。GEODIST 通过 Haversine 公式计算球面距离。 |
| 缺点 | GeoHash 边界处存在误差；无法高效支持多边形范围查询；高精度编码导致 ZSet 范围查询开销增大。 |

---

## 三、实战应用

### 3.1 Spring Boot 集成 Redis

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 通过 starter-data-redis 与连接池集成 Redis 的标准方式。 |
| 能做什么 | 引入依赖与连接池；配置 Lettuce 连接参数；为上层提供 RedisTemplate 基础设施。 |
| 怎么用 | 引入 `spring-boot-starter-data-redis` 与 `commons-pool2`；yml 配置 host/port/lettuce 池参数。 |
| 原理和工作流程 | starter 自动装配 RedisConnectionFactory，默认使用 Lettuce 客户端基于 Netty 的异步非阻塞连接。lettuce.pool 配置 max-active/max-idle/min-idle/max-wait 控制连接复用，连接池减少握手开销。RedisTemplate 在此工厂上执行命令。 |
| 缺点 | 默认连接池较小高并发易耗尽；Lettuce 共享连接在阻塞命令下可能相互影响；配置不当导致超时或泄漏。 |

### 3.2 RedisTemplate 与序列化

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Data Redis 提供的统一 Redis 操作模板及键值序列化器选型机制。 |
| 能做什么 | 任意类型读写；自定义 Key/Value 序列化；提供 StringRedisTemplate 纯字符串操作。 |
| 怎么用 | Key 用 `StringRedisSerializer`，Value 用 `Jackson2JsonRedisSerializer`，`afterPropertiesSet` 生效。 |
| 原理和工作流程 | RedisTemplate 通过 setKeySerializer/setValueSerializer 指定序列化策略，命令执行前将对象序列化为字节写入连接。默认 JdkSerializationRedisSerializer 产生不可读且体积大的字节流；Jackson2JsonRedisSerializer 输出可读 JSON 配合 activateDefaultTyping 保留类型信息；StringRedisTemplate 固定 String 序列化适合纯字符串。 |
| 缺点 | 默认 JDK 序列化乱码且跨语言不兼容；JSON 序列化带 @class 元数据增大体积；序列化异常导致存取失败。 |

### 3.3 缓存注解

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Cache 提供的声明式缓存注解，与 Redis 结合实现方法级缓存。 |
| 能做什么 | 命中缓存直接返回；方法后更新或删除缓存；组合多注解处理复杂场景。 |
| 怎么用 | `@Cacheable(value="user",key="#id")`；`@CacheEvict(key="#id")`；`@CachePut(key="#user.id")`。 |
| 原理和工作流程 | @Cacheable 通过 AOP 拦截方法，先按 key 查缓存命中则返回，未命中执行方法并将结果写入缓存；@CacheEvict 在方法执行后删除指定缓存或清空整组；@CachePut 每次执行方法并更新缓存；@Caching 组合多个 evict/put 操作。unless 与 SpEL 控制条件写入。 |
| 缺点 | 注解基于 AOP 同类调用失效；缓存粒度粗易脏数据；大结果缓存占内存需配合过期与淘汰。 |

### 3.4 分布式 Session

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 Spring Session 将 HttpSession 存入 Redis 实现多实例共享的会话机制。 |
| 能做什么 | 跨节点共享登录态；自动续期与过期；支持命名空间隔离。 |
| 怎么用 | `@EnableRedisHttpSession(maxInactiveIntervalInSeconds=1800)`；yml 配置 `store-type: redis`。 |
| 原理和工作流程 | @EnableRedisHttpSession 通过 Filter 将 HttpSession 替换为 SessionRepositoryFilter 包装的 Session，每次请求按 sessionId 从 Redis 读取会话属性，on_save 模式在响应提交时刷新写回。namespace 作为 key 前缀隔离不同应用，maxInactiveIntervalInSeconds 控制 TTL。 |
| 缺点 | 每次请求访问 Redis 增加延迟；Session 序列化与反序列化有开销；Redis 故障导致登录态丢失。 |

### 3.5 Pipeline 批量操作

| 维度 | 内容 |
|------|------|
| 是什么 | 将多个命令打包一次性发送以减少网络往返的批量执行机制。 |
| 能做什么 | 批量读写降低 RTT；提升高延迟网络下的吞吐；客户端异步发送。 |
| 怎么用 | `redisTemplate.executePipelined(RedisCallback)`，循环内 conn.set 多条命令。 |
| 原理和工作流程 | 客户端将多条命令按顺序写入发送缓冲区一次性发出，服务端依次执行并按序返回结果，省去每条命令的往返等待。命令间无需等待响应，网络往返由 N 次降为 1 次。Lettuce 原生支持异步非阻塞 Pipeline。 |
| 缺点 | 不保证原子性，中间命令失败不影响其他；命令过多占内存与网络；需 Lua 或事务保证原子性。 |

---

## 四、常见面试题

### 面试题 1：Redis 的 String 底层用什么实现？SDS 和 C 字符串有什么区别？

| 维度 | 内容 |
|------|------|
| 是什么 | String 底层使用 SDS（Simple Dynamic String）而非 C 语言 char[]。 |
| 能做什么 | O(1) 取长度；杜绝缓冲区溢出；二进制安全；预分配与惰性释放减少 malloc。 |
| 怎么用 | 三种编码 `int`/`embstr`(<=44 字节)/`raw` 按内容自动切换。 |
| 原理和工作流程 | SDS 含 len、free、buf[]，len 使取长 O(1)；修改前检查 free 自动扩容避免溢出；以 len 判断结束可存含 \0 的二进制数据；扩容 len<1MB 加倍、>=1MB 加 1MB，缩短惰性释放。buf 末尾保留 \0 兼容部分 C 函数。整数用 int 直接存不分配 SDS。 |
| 缺点 | 预分配占额外内存；embstr 修改转 raw；大字符串占连续内存。 |

### 面试题 2：Redis 的 ZSet 底层为什么用跳跃表而不用红黑树？

| 维度 | 内容 |
|------|------|
| 是什么 | ZSet 底层用 skiplist+dict 组合而非红黑树的选型决策。 |
| 能做什么 | 按 score 排序；O(logN) 范围与排名查询；O(1) 单点 score 查询。 |
| 怎么用 | `ZADD`/`ZRANGE`/`ZRANGEBYSCORE` 操作跳跃表与字典共享数据。 |
| 原理和工作流程 | skiplist 多层索引链表，节点随机层高 p=0.25 期望 1.33 层，最高 32 层，查找从高层逐层下降 O(logN)。选 skiplist 因实现简单代码少、范围查询在 level 0 顺序遍历高效、并发锁粒度细易实现无锁结构；红黑树旋转涉及多节点锁粒度粗、中序遍历需父指针回溯。 |
| 缺点 | skiplist 平均每节点约 1.33 额外指针略增内存；非精确平衡最坏退化；内存占用与红黑树差距不大但仍偏高。 |

### 面试题 3：Redis 的哈希表扩容是一次性完成的吗？渐进式 rehash 怎么做的？

| 维度 | 内容 |
|------|------|
| 是什么 | 字典扩容采用渐进式 rehash 分摊迁移而非一次性完成。 |
| 能做什么 | 避免一次性扩容阻塞主线程；扩缩容平滑过渡；期间保持读写可用。 |
| 怎么用 | 负载因子>=1 扩容；<0.1 缩容；serverCron 每 1ms 迁移 100 桶。 |
| 原理和工作流程 | 字典维护 ht[0]、ht[1]，触发扩容时为 ht[1] 分配空间并置 rehashidx=0。每次增删改查顺带迁移 rehashidx 对应桶到 ht[1] 并自增，后台 serverCron 每 1ms 迁移 100 桶。期间查找先 ht[0] 后 ht[1]，新增直接入 ht[1]。rehashidx==ht[0].size 时完成，释放 ht[0] 并替换。 |
| 缺点 | rehash 期间双表内存占用翻倍；查找需访问两表增加开销；BGSAVE 期间提高扩容阈值仍可能内存压力。 |

### 面试题 4：Redis 为什么单线程还这么快？Redis 6.0 为什么引入多线程？

| 维度 | 内容 |
|------|------|
| 是什么 | 单线程高性能原因及 6.0 多线程 I/O 引入动机的解析。 |
| 能做什么 | 解释单线程性能来源；说明多线程仅处理网络 I/O；指导线程配置。 |
| 怎么用 | `io-threads 4` 开启多线程 I/O；命令执行保持单线程。 |
| 原理和工作流程 | 纯内存操作使内存带宽成瓶颈而非 CPU；epoll 多路复用单线程监听多连接；单线程无锁竞争与上下文切换；SDS、跳跃表等结构高效。6.0 因网络硬件发展网络 I/O 成瓶颈，引入多线程处理读写与协议解析，命令执行仍单线程保原子性，默认关闭需配置开启。 |
| 缺点 | 单线程无法利用多核；大 Key 仍阻塞；多线程仅缓解网络 I/O，CPU 密集命令无改善。 |

### 面试题 5：大 Key 有什么危害？如何发现和解决？

| 维度 | 内容 |
|------|------|
| 是什么 | 单个 key 的 value 过大（String>10KB 或集合>10000 元素）引发问题的现象与治理。 |
| 能做什么 | 阻塞主线程与网卡；中断主从同步；阻碍集群迁移；导致内存倾斜。 |
| 怎么用 | `redis-cli --bigkeys` 发现；`UNLINK` 异步删除；`SCAN` 分批删除元素。 |
| 原理和工作流程 | 大 Key 的 GET/SET、HGETALL/SMEMBERS/DEL 在单线程执行耗时长阻塞其他请求；同步时复制缓冲区溢出致主从断连；集群槽迁移大 Key 耗时长致槽不可用。发现用 --bigkeys 扫描、MEMORY USAGE 估算、SCAN 自研工具。解决靠拆分大 Hash、UNLINK 异步删、压缩 value、对象存储替代。 |
| 缺点 | 拆分增加业务复杂度；UNLINK 延迟释放内存；压缩引入 CPU 开销；治理需改造现有数据模型。 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | 生产实践中高频踩坑点及对应解决方案的汇总。 |
| 能做什么 | 识别 KEYS、大 Key、序列化、全量操作、热 Key、同时过期、淘汰策略、连接池等常见错误。 |
| 怎么用 | `SCAN` 替代 `KEYS`；`UNLINK` 异步删；配置 Jackson 序列化与 maxmemory。 |
| 原理和工作流程 | KEYS 为 O(N) 遍历阻塞主线程故用 SCAN 渐进式；大 Key 全量操作阻塞故拆分与异步删；默认 JDK 序列化乱码故换 JSON；全量 HGETALL 等阻塞故用 HSCAN；热 Key 单点过载故本地缓存加分摊；同时过期致集中删除故过期时间加随机偏移；未配淘汰策略致 OOM 故设 maxmemory 与 allkeys-lru；连接池耗尽故调大 max-active；多命令非原子故用 Lua 或事务。 |
| 缺点 | 各方案均有取舍：SCAN 结果可能重复；拆分增加复杂度；JSON 带元数据增大体积；本地缓存有一致性延迟；随机过期降低命中率；Lua 脚本调试困难。 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./01-Redis核心数据结构与底层原理.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
