# Kafka 笔面试题集

> 模块：04-message-queue（第4周 消息队列）
> 覆盖：Kafka 核心原理、副本机制、可靠性保障、运维治理
> 题量：12 道选择题 + 8 道简答题 + 3 道场景设计题

> 📖 **参考链接**：
> - [Kafka Documentation](https://kafka.apache.org/documentation/) -- Kafka 官方文档总入口
> - [Kafka 设计原理](https://kafka.apache.org/documentation/#design) -- 高吞吐、持久化、副本等底层设计官方说明

---

## 一、选择题（12 题，每题附解析）

### 1. ★ Kafka 中 HW（High Watermark）的含义是（ ）

A. Leader 已写入的最大 offset
B. ISR 中所有副本都已同步到的 offset，消费者只能消费到该位置
C. 副本最后一条消息的大小
D. 消费者已提交的位移

**答案：B**

**解析：** HW（高水位）是 ISR 中所有副本都已同步完成的位置，消费者只能拉取到 HW 之前的消息。Leader 已写入的最大位置是 LEO（Log End Offset），消费者已提交的位置是 committed offset，三者含义不同。

---

### 2. ★ 关于 Kafka 的 LEO 与 HW，描述正确的是（ ）

A. HW 一定大于 LEO
B. LEO 是下一条待写入消息的 offset，HW = min(ISR 中所有副本的 LEO)
C. LEO 只存在于 Follower 副本
D. HW 由消费者提交位移后更新

**答案：B**

**解析：** LEO 指向副本下一条待写入消息的位置，Leader 和 Follower 都各自维护。Leader 的 HW 取 ISR 中所有副本 LEO 的最小值。由于 Follower 需要主动向 Leader 拉取数据，HW 通常落后于 Leader 的 LEO。HW 由 Leader 根据 ISR 同步进度更新，与消费者提交位移无关。

---

### 3. ★★ 生产者配置 acks=1 时，在什么情况下会丢消息？（ ）

A. Leader 写入成功但尚未同步到 Follower 时 Leader 宕机
B. 发生网络分区
C. ISR 中副本数超过 2
D. 消费者处理超时

**答案：A**

**解析：** acks=1 表示 Leader 写入本地日志即返回确认。若此时 Leader 宕机且消息尚未被 Follower 同步，则从 ISR 中选举出的新 Leader 不包含这条消息，消息丢失。acks=all 需要所有 ISR 副本确认，可避免该问题。B 是触发条件而非丢失根因，C、D 与 acks 语义无关。

> 📖 **参考链接**：[Kafka Producer 配置](https://kafka.apache.org/documentation/#producerconfigs) -- acks、retries、幂等等生产者配置官方说明

---

### 4. ★★ 当 acks=all 且 min.insync.replicas=2，但 ISR 中只剩 1 个副本时，生产者发送消息会（ ）

A. 发送成功
B. 抛出 NOT_ENOUGH_REPLICAS 异常，发送失败
C. 自动降级为 acks=1
D. 等待 ISR 恢复后自动发送

**答案：B**

**解析：** min.insync.replicas 规定写入成功所需的最小同步副本数。acks=all 时 Broker 会校验当前 ISR 大小是否满足 min.insync.replicas，不满足则拒绝写入并返回 NOT_ENOUGH_REPLICAS。这是"可靠性优先于可用性"的设计，避免在副本不足时写入而埋下丢失风险。

---

### 5. ★★ 消费者使用 enable.auto.commit=true（默认值）可能导致的问题是（ ）

A. 消息永远不会重复消费
B. 位移按时间间隔自动提交，可能在业务处理完成前提交，导致消息被跳过
C. 消费者无法加入 consumer group
D. 自动提交会导致 Broker 拒绝消息

**答案：B**

**解析：** enable.auto.commit=true 时消费者按 auto.commit.interval.ms（默认 5s）自动提交位移，提交时机与业务处理完成无关。若消息已拉取并自动提交位移，但业务尚未处理完时消费者宕机，重启后从已提交位移继续消费，未处理的消息就被跳过了，表现为消息丢失。生产环境建议 enable.auto.commit=false 配合手动提交。

---

### 6. ★★★ Kafka 消费者的位移提交后，位移数据存储在（ ）

A. ZooKeeper 的 /consumers 节点
B. 内部 Topic `__consumer_offsets`
C. 消费者本地磁盘
D. Broker 内存中

**答案：B**

**解析：** Kafka 0.9 之前位移存储在 ZooKeeper，0.9 之后改为存储在内部 Topic `__consumer_offsets`（默认 50 个分区）。该 Topic 使用 compact 清理策略，只保留每个 group+topic+partition 的最新位移。ZooKeeper 方案因写入过于频繁、不适合大批量提交而被废弃。

---

### 7. ★★ 以下哪种 Rebalance 分配策略可以做到"分阶段迁移、迁移期间不停止消费"？（ ）

A. Range
B. RoundRobin
C. Sticky
D. Cooperative Sticky

**答案：D**

**解析：** Cooperative Sticky（协作粘性，Kafka 2.4+）采用增量式（Incremental）再均衡协议，分两轮完成：第一轮消费者只撤销需要迁移的 Partition，第二轮完成再分配，期间其他 Partition 继续消费。Range、RoundRobin、Sticky 都属于 Eager 协议，Rebalance 期间所有消费者会先放弃全部 Partition，消费短暂停止。

---

### 8. ★★★ 以下关于 Kafka 日志清理策略的描述，错误的是（ ）

A. delete 策略按时间或大小删除过期日志段
B. compact 策略对相同 Key 只保留最新一条消息
C. 一个 Topic 可以同时配置 delete 和 compact
D. compact 策略会删除所有历史消息，只保留最后一条

**答案：D**

**解析：** compact（日志压缩）针对相同 Key 的消息只保留最新 Value，不同 Key 的消息全部保留，因此并非"只保留最后一条"。delete 按 retention.ms / retention.bytes 删除整个日志段；cleanup.policy 可配置为 "delete,compact" 同时生效。compact 适合变更日志、CDC、状态快照等场景。

---

### 9. ★★★ 关于 Kafka Topic 的分区数量，描述正确的是（ ）

A. 分区数可以增加也可以减少
B. 分区数只能增加，不能减少
C. 分区数修改后已有消息会重新分布到新分区
D. 分区数由 Broker 根据负载自动调整

**答案：B**

**解析：** Kafka 只支持增加分区数，不支持减少。减少分区会改变消息归属（同一 Key 可能哈希到不同分区），破坏分区内顺序性和消费位移连续性。此外，增加分区不会让已有消息重新分布——已有消息仍留在原分区，只有新消息才按新分区数路由。

---

### 10. ★★ Kafka 事务生产者实现 Exactly-Once 时，消费者需要配置的隔离级别是（ ）

A. read_uncommitted
B. read_committed
C. serializable
D. repeatable_read

**答案：B**

**解析：** 事务消息的消费者需设置 isolation.level=read_committed，只消费已提交事务的消息，未提交或已回滚事务的消息不可见。默认值为 read_uncommitted，会读到未提交事务的消息，破坏 Exactly-Once 语义。

> 📖 **参考链接**：[Kafka Exactly-Once 语义](https://kafka.apache.org/documentation/#semantics) -- 幂等生产者与事务机制官方说明

---

### 11. ★★ 关于 Kafka 副本数（replication.factor）的描述，正确的是（ ）

A. 副本数可以大于 Broker 数量
B. 副本数不能超过 Broker 数量，且副本数应大于等于 min.insync.replicas
C. 副本数为 1 时也能保证高可用
D. 副本数修改后已有消息不会补全新副本

**答案：B**

**解析：** 副本数不能超过集群 Broker 数量，否则分区无法完成分配。同时副本数需 ≥ min.insync.replicas，否则 acks=all 永远无法满足要求，生产者将无法写入。副本数为 1 时无冗余，Broker 宕机即不可用。副本数增加后 Kafka 会自动为已有分区创建新副本并同步数据（这一点与分区数不能减少不同）。

---

### 12. ★★ 以下关于 Kafka 消息顺序性的描述，正确的是（ ）

A. Kafka 保证全局消息有序
B. Kafka 只保证单个 Partition 内消息有序
C. 开启幂等且 max.in.flight.requests.per.connection ≤ 5 时，重试不会导致分区内乱序
D. B 和 C 都正确

**答案：D**

**解析：** Kafka 只保证单 Partition 内消息按写入顺序有序，不保证跨 Partition 的全局顺序。生产者开启幂等（enable.idempotence=true）且 max.in.flight.requests.per.connection ≤ 5 时，Broker 会按序列号拒绝乱序写入，重试也不会造成分区内乱序；未开幂等时若 max.in.flight > 1，重试可能导致乱序。

---

## 二、简答题（8 题，每题附完整解析）

### 1. 解释 Kafka 中 LEO 与 HW 的区别，以及 HW 如何保证副本一致性。

**答案：**

| 维度 | LEO（Log End Offset） | HW（High Watermark） |
|------|----------------------|---------------------|
| 定义 | 副本下一条待写入消息的 offset | ISR 中所有副本都已同步到的 offset |
| 维护者 | 每个副本各自维护（Leader 与 Follower） | Leader 维护并同步给 Follower |
| 可见性 | 不对消费者直接可见 | 消费者只能消费到 HW 之前的消息 |
| 关系 | Leader 的 LEO ≥ HW | HW = min(ISR 中所有副本的 LEO) |

**HW 更新流程：**

1. Follower 向 Leader 发送 Fetch 请求，请求中携带自己的 LEO
2. Leader 收到后更新该 Follower 的 LEO，取 ISR 中所有副本 LEO 的最小值更新 HW
3. Leader 在 Fetch 响应中把最新 HW 同步给 Follower
4. 消费者只能拉取 offset < HW 的消息

**为什么需要 HW：** 只有 HW 之前的消息才被 ISR 中所有副本持久化。即使 Leader 宕机，从 ISR 中选举出的新 Leader 也一定包含这些消息，从而保证"已提交消息"不丢失，同时避免消费者读到后续可能被截断的消息。

**HW 的缺陷：** HW 更新存在一轮 Fetch 的延迟；且 Leader 切换时可能发生日志截断（Truncation），导致短暂的数据不一致。Kafka 为此引入 Leader Epoch 机制，在截断时以 Epoch 为准判断日志一致性，修正了 HW 的截断缺陷。

> **生活化类比：LEO 与 HW = 排队买票的队尾与"已确认窗口"** —— LEO 是队伍已经排到的位置（下一个人要站的地方），HW 是售票员确认"这一截队伍的人都已核实身份、可以放行"的位置。排队的人（未同步的消息）还在，但只有 HW 之前的人才被正式承认。窗口跟着最慢的核实员走，所以 HW 永远不超过 LEO。

---

### 2. Kafka 如何通过 acks、min.insync.replicas、unclean.leader.election.enable 三者配合保证消息不丢失？

**答案：**

三个配置分别作用于"写入确认、最小同步副本、选举约束"，缺一不可：

| 配置 | 推荐取值 | 作用 |
|------|----------|------|
| acks | all（-1） | 生产者等待所有 ISR 副本写入成功才收到确认 |
| min.insync.replicas | 2 | 规定写入成功所需的最小同步副本数，ISR 不足时拒绝写入 |
| unclean.leader.election.enable | false（默认） | 禁止从非 ISR 副本选举 Leader，避免新 Leader 缺少已提交消息 |

**组合效果分析：**

- acks=all 但 min.insync.replicas=1：ISR 只剩 Leader 时仍能写入，Leader 宕机即丢消息
- min.insync.replicas=2 但 acks=1：Leader 写入即返回，Follower 未同步时宕机仍会丢消息
- 三者同时配置：ISR 至少 2 个副本、全部确认后才算提交、新 Leader 必来自 ISR，已提交消息不会丢失

**代价：** 可靠性提升带来可用性下降——ISR 副本不足时生产者写入失败（NOT_ENOUGH_REPLICAS），需等待 ISR 恢复。生产环境推荐 replication.factor=3、min.insync.replicas=2、acks=all 的"三副本两同步"配置，在可靠性和可用性之间取得平衡。

---

### 3. Kafka 消费者的位移提交方式有哪些？自动提交为什么会导致重复消费或消息丢失？

**答案：**

| 提交方式 | 配置/接口 | 特点 |
|----------|----------|------|
| 自动提交 | enable.auto.commit=true | 按 auto.commit.interval.ms 定时提交，提交时机与业务处理无关 |
| 手动同步提交 | commitSync() | 提交后阻塞等待结果，失败自动重试，可靠但吞吐较低 |
| 手动异步提交 | commitAsync() | 不阻塞，失败不重试，吞吐高但可能提交失败 |
| 手动指定位移 | commitSync(Map) | 精确控制提交位置，常用于批处理场景 |

**自动提交的两类问题：**

- **消息丢失**：消息已拉取、位移已自动提交，但业务尚未处理完消费者宕机，重启后从已提交位移继续消费，未处理的消息被跳过
- **重复消费**：消息处理完成后消费者宕机，而位移尚未到下一次自动提交周期，重启后从旧位移重新消费

**正确做法：**

1. 设置 enable.auto.commit=false
2. 业务处理成功后调用 commitSync() 提交位移；批处理场景处理完整批再提交
3. 消费端必须实现幂等（业务唯一 ID 去重），因为"至少一次"语义下重复不可避免
4. 合理设置 max.poll.records，避免单批处理时间超过 max.poll.interval.ms

> **生活化类比：位移提交 = 读书书签** —— 位移就是阅读书签。自动提交像"每 5 秒随手夹一次书签"，哪怕这一页还没读完；万一此时合上书（宕机），下次就从书签处继续，中间没读完的内容被跳过了（消息丢失）。手动提交则是"这一页确实读懂了再夹书签"，最坏情况是重复读一遍（重复消费），但不会漏读。所以书签要手动夹，同时给内容做去重标记。

---

### 4. Kafka 有哪些分区分配策略？如何避免 Rebalance 抖动？

**答案：**

**四种分配策略：**

| 策略 | 协议类型 | 原理 | 优缺点 |
|------|---------|------|--------|
| Range | Eager | 按 Topic 逐个分配，分区按序号范围切分 | 实现简单；多 Topic 时分配不均 |
| RoundRobin | Eager | 所有分区统一排序后轮询分配 | 分配均匀；Rebalance 时全量重分配 |
| Sticky | Eager | 尽量保留原分配，只移动最少分区 | 减少迁移量；首次分配不均 |
| Cooperative Sticky | Incremental | 分两轮增量迁移，不停止消费 | 平滑迁移；需 Kafka 2.4+ |

**Rebalance 触发条件：** 消费者成员变更、订阅 Topic 的分区数变更、心跳超时（session.timeout.ms 默认 45s）、处理超时（max.poll.interval.ms 默认 5min）。

**避免抖动的措施：**

1. 合理设置 session.timeout.ms（如 30s）与 heartbeat.interval.ms（如 3s），减少网络抖动导致的误判
2. 保证单批处理时间远小于 max.poll.interval.ms；耗时逻辑异步化或减小 max.poll.records
3. 使用 Cooperative Sticky 分配策略（partition.assignment.strategy=CooperativeStickyAssignor）
4. 使用静态成员（group.instance.id），消费者重启在 session.timeout.ms 内不触发 Rebalance
5. 避免频繁启停消费者，避免消费逻辑中出现长时间 GC 阻塞

---

### 5. Kafka 高吞吐原理中，顺序写、Page Cache、零拷贝分别解决了什么问题？

**答案：**

| 设计 | 解决的问题 | 原理 | 效果 |
|------|-----------|------|------|
| 顺序写磁盘 | 随机 I/O 性能差 | 消息只追加到日志段末尾，不做原地更新 | 顺序写 600MB/s vs 随机写 100KB/s |
| Page Cache | 避免频繁磁盘读写 | 读写都经过 OS 页缓存，写先落缓存由 OS 异步刷盘，读优先命中缓存 | 热数据读取几乎无磁盘 I/O |
| 零拷贝 sendfile | 内核态与用户态间多次拷贝 | 数据从 Page Cache 直接 DMA 到网卡，不经过用户态 | 4 次拷贝 + 4 次切换 → 2 次拷贝 + 2 次切换 |
| 批量发送 | 网络往返次数过多 | Producer 按 batch.size + linger.ms 凑批发送 | 单次网络请求承载多条消息 |
| 批量压缩 | 网络带宽成为瓶颈 | 整批压缩后传输，Broker 端保持压缩存储 | 压缩率 3-5 倍，节省带宽与磁盘 |
| 分区并行 | 单机处理能力有限 | 多 Partition 分布多 Broker 并行读写 | 水平扩展，吞吐随分区数增长 |

**为什么不用 JVM 堆内存存储：** Kafka 依赖 Page Cache 而非 JVM 堆内存，避免了 GC 停顿带来的长尾延迟；同时利用操作系统成熟的内存管理，Broker 重启后缓存仍由 OS 保留。这是 Kafka 相比纯内存消息队列更稳定的关键。

> 📖 **参考链接**：[Kafka 设计原理](https://kafka.apache.org/documentation/#design) -- 高吞吐六大设计官方说明

---

### 6. Kafka 的日志存储结构是怎样的？delete 和 compact 两种清理策略有何区别？

**答案：**

**存储结构：** 每个 Partition 对应一个目录（命名形如 `topic-partition`），目录内由多个日志段（Log Segment）组成：

- `.log`：消息数据文件，按 offset 顺序追加，写满 segment.bytes（默认 1GB）后滚动新建
- `.index`：偏移量索引文件，稀疏索引（每写入 log.index.interval.bytes 记录一条）
- `.timeindex`：时间戳索引文件，支持按时间查找消息
- 每个日志段以基准 offset 命名，如 `00000000000000000000.log`

**两种清理策略：**

| 维度 | delete | compact |
|------|--------|---------|
| 清理粒度 | 整个日志段 | 单条消息（按 Key 去重） |
| 触发条件 | retention.ms / retention.bytes 到期 | 满足 min.cleanable.dirty.ratio 后由 Log Cleaner 压缩 |
| 保留内容 | 未过期的全部消息 | 每个 Key 的最新 Value + 未过期的消息 |
| 消息顺序 | 保持 | 保持（压缩后 offset 出现空洞但顺序不变） |
| 适用场景 | 普通业务消息、日志 | 变更日志、状态快照、CDC、`__consumer_offsets` |

**配置方式：** `cleanup.policy=delete`（默认）/ `compact` / `delete,compact`。compact 保留的 offset 会出现空洞，消费者需按 offset 顺序读取，不能假设 offset 连续。

---

### 7. Kafka 的事务消息如何实现 Exactly-Once？与 RocketMQ 事务消息有何区别？

**答案：**

**Kafka 事务实现流程：**

1. 生产者调用 initTransactions() 向 Transaction Coordinator 注册并获取 PID
2. beginTransaction() 开启事务，后续 send() 的消息都带事务标记
3. sendOffsetsToTransaction() 把消费位移提交也纳入同一事务
4. commitTransaction() 原子提交，或 abortTransaction() 回滚
5. Broker 通过控制批次（control batch）标记事务边界，消费者设置 isolation.level=read_committed 只读已提交消息

**Exactly-Once 的完整链路：** 幂等生产者（单分区去重）+ 事务（跨分区原子写）+ 消费者 read_committed + 位移提交纳入事务。典型应用是 Kafka Streams 的 `processing.guarantee=exactly_once_v2`。

**与 RocketMQ 的区别：**

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 目标 | 实现流处理的端到端 Exactly-Once | 解决"本地事务 + 发消息"的分布式最终一致性 |
| 机制 | PID + 事务协调器 + 两阶段提交 | 半消息 + 本地事务 + 回查 |
| 回查 | 无回查，靠事务超时自动回滚 | Broker 定时回查，最多 15 次 |
| 位移提交 | 位移提交可纳入事务，与生产原子 | 位移提交独立于事务 |

**注意：** Kafka 事务只保证 Kafka 内部（消费-处理-生产）的原子性。若处理过程涉及外部数据库，仍需业务幂等或本地消息表兜底。

---

### 8. Kafka 与 ZooKeeper 的关系是什么？KRaft 模式解决了什么问题？

**答案：**

**ZooKeeper 的作用（旧架构）：**

- 存储集群元数据：Broker 列表、Topic/Partition 信息、副本分配、ISR、Controller 信息
- Controller 选举：第一个在 ZK 创建 /controller 节点的 Broker 成为 Controller
- 集群成员管理：Broker 上下线通过临时节点感知

**ZK 架构的问题：**

1. 需额外部署维护一套 ZK 集群，运维成本高
2. 元数据写入需经过 ZK，分区数多（数万）时元数据同步成为瓶颈
3. Controller 故障切换需从 ZK 全量加载元数据，分区多时恢复缓慢（分钟级）
4. 两套系统的一致性边界复杂，易出现元数据不一致

**KRaft 模式（Kafka 3.3+ 生产可用，4.0 起移除 ZK）：**

- 使用 Kafka 自身的 Raft 协议实现元数据仲裁，Controller 节点组成 Raft Quorum
- 元数据以日志形式存储在内部 Topic `__cluster_metadata`，由 Controller 维护并同步给 Broker
- 支持数百万分区，Controller 故障切换秒级完成
- 部署只需一套 Kafka，运维显著简化

**注意：** 迁移需按官方工具逐版本升级，不能直接从 ZK 模式切到 KRaft；KRaft 中 Controller 与 Broker 角色可合并（combined）或分离（isolated），生产推荐分离部署。

> 📖 **参考链接**：
> - [Kafka KRaft 模式](https://kafka.apache.org/documentation/#kraft) -- KRaft 元数据管理与 ZK 迁移官方说明
> - [Kafka 运维与监控](https://kafka.apache.org/documentation/#ops) -- Kafka 运维操作与监控官方指南

---

## 三、场景设计题（3 题，每题附完整解析）

### 1. 设计一个"Kafka 消息积压应急处理"方案

**场景描述：** 某电商大促期间，order-topic 消费 Lag 从 1 万暴涨到 800 万，消费者 CPU 打满，下游订单处理延迟超过 1 小时。Topic 当前 12 个分区、3 个消费者实例。

**设计方案：** 按「扩容分区 → 转存新 Topic 再消费 → 丢弃」三级处置策略逐级升级。

**第一级：扩容分区（提升消费并行度）**

```
现状分析：
- 12 分区仅 3 个消费者，存在 9 个空闲并行度
- 第一步先把消费者扩容到 12 个（不能超过分区数），Lag 增长速率立刻下降

若消费者已达分区数上限，再扩容分区：
kafka-topics.sh --bootstrap-server localhost:9092 \
  --alter --topic order-topic --partitions 48

注意事项：
- 分区数只能增加，不能减少
- 扩容分区需评估 Broker 磁盘、网络和文件句柄
- 已有消息不会重新分布，只有新消息按新分区数路由
- 建议单 Broker 分区总数不超过 2000-4000
```

**第二级：转存新 Topic 再消费（消费逻辑本身是瓶颈时）**

```
适用场景：消费者逻辑耗时（如调用外部接口、复杂计算），单条处理时间无法压缩

操作步骤：
1. 创建新 Topic order-topic-retry，分区数设为 48（远大于原分区数）
2. 部署临时转存消费者，只做"拉取-转发"，不执行业务逻辑
   （纯转发吞吐可达数十万 TPS），把原 Topic 快速消费并写入新 Topic
3. 原 Topic 的消费者组暂停业务消费，Lag 快速清零
4. 启动大批量业务消费者消费新 Topic，按分区并行处理
5. 处理完成后下线临时消费者，业务切回原 Topic
```

**第三级：丢弃（业务可容忍时）**

```
适用场景：消息已过期（如超过 24 小时的营销通知）、非核心数据、已有对账补偿机制

操作步骤：
1. 停止消费者，重置位移到最新
   kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
     --reset-offsets --to-latest --group order-group --topic order-topic --execute
2. 或直接删除重建 Topic 清空数据
```

**配套监控与预防：**

| 措施 | 说明 |
|------|------|
| Lag 监控告警 | Lag > 10 万或持续增长 5 分钟触发告警 |
| 消费者数上限 | 消费者数 ≤ 分区数，扩容前先确认 |
| 大促预案 | 提前扩容分区至日常峰值的 2-3 倍，预留消费者扩容余量 |
| 消费耗时监控 | 单批处理时间接近 max.poll.interval.ms 时告警 |
| 死信/重试 Topic | 异常消息不阻塞主流程，快速进入重试或死信通道 |

**三级策略对比：**

| 级别 | 适用场景 | 优点 | 风险 |
|------|----------|------|------|
| 扩容分区 | 消费并行度不足 | 操作简单、见效快 | 分区只增不减；过多分区增加元数据开销 |
| 转存新 Topic | 消费逻辑本身慢 | 可任意提高并行度 | 转存期间可能重复；需幂等；增加运维成本 |
| 丢弃 | 数据可容忍丢失 | 立即止血 | 不可逆，必须评估业务影响 |

---

### 2. 设计一个"端到端 Exactly-Once"的 Kafka 订单处理方案

**场景描述：** 订单服务消费上游支付消息，处理后写入订单库并向物流 Topic 发送发货消息，要求不重不漏。

**设计方案：**

**1. 上游生产者保障：**

```
- acks=all + enable.idempotence=true
- replication.factor=3、min.insync.replicas=2
- retries=Integer.MAX_VALUE（幂等开启后安全）
```

**2. 消费-处理-生产放入同一事务：**

```java
producer.initTransactions();
while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(500));
    if (records.isEmpty()) {
        continue;
    }
    producer.beginTransaction();
    try {
        for (ConsumerRecord<String, String> record : records) {
            // 业务处理：更新订单状态 + 发送下游发货消息
            orderService.markPaid(record.value());
            producer.send(new ProducerRecord<>("logistics-topic", record.key(), record.value()));
        }
        // 关键：把消费位移提交也纳入事务
        producer.sendOffsetsToTransaction(currentOffsets(records), consumer.groupMetadata());
        producer.commitTransaction();
    } catch (Exception e) {
        producer.abortTransaction();
        // 重置消费位置，重新处理本批
        seekToStartOfBatch(records);
    }
}
```

**3. 下游消费者配置：**

```
isolation.level=read_committed   // 只消费已提交事务的消息
enable.auto.commit=false         // 关闭自动提交，避免破坏事务边界
```

**4. 涉及外部数据库的兜底：** Kafka 事务无法覆盖外部数据库写入，需补充以下任一方案：

- 本地消息表：订单库写入与"待发送消息"记录在同一数据库事务中，再由独立任务投递
- 幂等写入：下游以业务唯一 ID（订单号）建唯一索引，重复写入直接忽略
- 对账补偿：定时对比订单库与物流库，发现缺失消息重新投递

**关键技术点：**

| 保障点 | 技术方案 | 说明 |
|--------|----------|------|
| 不丢 | acks=all + 三副本两同步 | 消息落盘到多副本后才算提交 |
| 不重 | 幂等生产者 PID + Sequence Number | 单分区内按序列号去重 |
| 原子 | 事务 API 包裹发送与位移提交 | 消费位移与下游消息同生共死 |
| 可见性 | read_committed 隔离级别 | 未提交事务消息对消费者不可见 |
| 兜底 | 本地消息表 / 幂等写入 / 对账 | 覆盖 Kafka 事务管不到的外部系统 |

**风险与应对：**

| 风险 | 应对措施 |
|------|----------|
| 事务超时（transaction.timeout.ms 默认 60s） | 减小单批数据量，保证事务在超时前提交 |
| 事务协调器故障 | 多副本部署 `__transaction_state`，监控未完成事务数 |
| 单批处理过慢触发 Rebalance | 减小 max.poll.records，配合静态成员 |

---

### 3. 设计一个"Kafka 集群容量规划与运维监控"方案

**场景描述：** 某公司要上线一套 Kafka 集群承载日均 20 亿条消息，需给出分区/副本规划、监控告警和常见故障处置方案。

**设计方案：**

**1. 容量规划：**

| 维度 | 规划方法 | 说明 |
|------|----------|------|
| Broker 数 | ≥ 6 | 3 副本下保证机架/可用区容灾 |
| Topic 分区数 | 峰值 TPS ÷ 单分区承载（约 1-5 万 TPS） | 预留 2-3 倍余量，分区只增不减 |
| 副本数 | 3 | replication.factor=3 + min.insync.replicas=2 |
| 磁盘容量 | 日均量 × 保留天数 × 副本数 × 1.3 | 预留 30% 余量应对峰值与副本同步 |
| 单 Broker 分区数 | ≤ 2000-4000 | 避免元数据开销过大和故障恢复缓慢 |

**2. 关键配置：**

```
unclean.leader.election.enable=false   # 禁止非 ISR 选举
min.insync.replicas=2                  # 最小同步副本
compression.type=lz4                   # 高吞吐低 CPU
log.segment.bytes=1073741824           # 日志段 1GB
num.io.threads / num.network.threads   # 按磁盘与网卡核数调整
```

**3. 监控指标与告警阈值：**

| 指标 | 含义 | 建议阈值 |
|------|------|----------|
| Consumer Lag | 消费积压量 | > 10 万或持续增长 5 分钟告警 |
| ISR 收缩 | 副本掉出 ISR | 任一 Topic 的 ISR < 副本数即告警 |
| UnderReplicatedPartitions | 副本不足的分区数 | > 0 告警 |
| ActiveControllerCount | 活跃 Controller 数 | 全集群必须等于 1，否则异常 |
| 磁盘使用率 | Broker 磁盘水位 | > 75% 告警，> 85% 严重 |
| Produce/Fetch P99 延迟 | 请求延迟 | > 100ms 告警 |
| 网络吞吐 | 出入带宽 | 接近网卡上限 80% 告警 |

**4. 常见故障处置：**

| 故障 | 现象 | 处置 |
|------|------|------|
| Broker 宕机 | 分区 Leader 切换 | 检查 ISR 是否满足 min.insync.replicas，必要时清理副本 |
| 副本不同步 | ISR 持续收缩 | 检查网络/磁盘，触发 Preferred Leader 选举或分区重分配 |
| Controller 频繁切换 | 元数据操作变慢 | 排查 ZK 会话超时（旧架构）或 Controller 负载 |
| 分区分布不均 | 部分 Broker 负载高 | 使用 kafka-reassign-partitions.sh 迁移分区 |
| 磁盘写满 | 消息写入被拒 | 缩短 retention、清理过期日志、扩容磁盘 |
| 消费者 Lag 突增 | 处理能力不足 | 按"扩容分区 → 转存 → 丢弃"三级策略处理 |

**5. 运维规范：**

```
- 变更窗口：分区扩容、副本重分配等操作在低峰期执行
- 分区扩容审批：评估下游消费者并行度与 Broker 承载能力
- 工具化：分区重分配、位移重置脚本化并留痕
- 定期演练：Broker 宕机、Controller 切换、磁盘故障演练
```

> 📖 **参考链接**：
> - [Kafka 运维与监控](https://kafka.apache.org/documentation/#ops) -- Kafka 运维操作与监控官方指南
> - [Kafka 配置参数](https://kafka.apache.org/documentation/#configuration) -- 核心 Broker/Topic 配置参数说明

---

> **学习导航**：
> - 返回 [学习路线总览](../../../README.md)
> - 本模块其他文件：[01-Kafka核心原理](./01-Kafka核心原理.md) | [01-Kafka核心原理导览](./01-Kafka核心原理-导览.md) | [03-消息队列笔面试题集](../03-消息队列笔面试题集.md)
