# Kafka 笔面试题集 导览

> 定位：五维框架浓缩提炼 Kafka笔面试题集.md 全部内容小节，快速查阅与复习。
> 用法：每个题型分类对应一张概要表格，每道题目提取所考知识点对应一张纵向表格，需要深入理解时跳转 [原文](./Kafka笔面试题集.md)。
> 前置知识：[Kafka核心原理](./01-Kafka核心原理-导览.md)

---

## 一、选择题（12 题，每题附解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 从给定选项中选择正确答案的客观题型，本题集共 12 道，覆盖 Kafka 副本机制、可靠性配置、位移提交、日志清理、运维约束 |
| 能做什么 | 考查 HW 与 LEO、acks 与 min.insync.replicas、自动提交风险、`__consumer_offsets`、Cooperative Sticky、delete/compact、分区数不可减少、read_committed、副本数约束、顺序性保证等点状知识 |
| 怎么用 | 阅读题干排除干扰项，结合解析巩固易混淆概念 |
| 原理和工作流程 | 每题聚焦单一知识点，通过选项对比强化辨析。星号标注难度，一星为基础、二星为进阶、三星为深入。覆盖 Kafka 副本同步、可靠性三配置、消费者位移、Rebalance 策略、日志存储、事务隔离、顺序保证等核心考点 |
| 缺点 | 单题覆盖面窄；选项存在猜测成分；难以考查综合设计与运维能力 |

### 1. ★ Kafka 中 HW（High Watermark）的含义是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | HW 高水位是 ISR 中所有副本都已同步到的 offset，是消费者可见的消息边界 |
| 能做什么 | 界定消费者可见范围；标识"已提交"消息；配合 ISR 保证副本一致 |
| 怎么用 | Leader 自动维护并通过 Fetch 响应同步给 Follower，无需手工配置 |
| 原理和工作流程 | HW = min(ISR 中所有副本的 LEO)。Follower 拉取时上报 LEO，Leader 据此推进 HW，消费者只能消费 offset < HW 的消息。Leader 已写入的最大位置是 LEO，消费者已提交的位置是 committed offset |
| 缺点 | 更新有一轮 Fetch 延迟；Leader 切换时可能日志截断；需 Leader Epoch 修正 |

### 2. ★ 关于 Kafka 的 LEO 与 HW，描述正确的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | LEO 是副本下一条待写入消息的 offset，HW 取 ISR 中所有副本 LEO 的最小值 |
| 能做什么 | LEO 标识各副本写入进度；HW 标识全局已同步位置；两者共同保证一致性 |
| 怎么用 | 通过 kafka-log-dirs、JMX 指标或 kafka-dump-log 观察 LEO 与 HW |
| 原理和工作流程 | Leader 与 Follower 各自维护 LEO。Leader 根据 Follower 上报的 LEO 更新 HW，通常 HW 落后于 Leader 的 LEO。HW 由 Leader 根据 ISR 同步进度更新，与消费者提交位移无关，LEO 也不只存在于 Follower |
| 缺点 | LEO 与 HW 概念易混淆；HW 滞后导致消费延迟；截断场景需额外机制 |

### 3. ★★ 生产者配置 acks=1 时，在什么情况下会丢消息？（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | acks=1 仅 Leader 写入即确认，Leader 宕机且未同步时消息丢失 |
| 能做什么 | 识别 acks=1 的丢消息窗口；对比 acks=0/1/all 的可靠性差异 |
| 怎么用 | `acks=1` 兼顾吞吐与部分可靠；金融场景改用 `acks=all` |
| 原理和工作流程 | acks=1 时 Leader 写入本地日志立即返回确认。若 Leader 此时宕机且 Follower 尚未同步，从 ISR 选举的新 Leader 不含该消息，消息丢失。网络分区是触发条件而非根因，ISR 副本数与消费者超时与 acks 语义无关 |
| 缺点 | 存在丢消息窗口；对 Leader 故障敏感；高可靠场景不适用 |

### 4. ★★ 当 acks=all 且 min.insync.replicas=2，但 ISR 中只剩 1 个副本时，生产者发送消息会（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | ISR 不足 min.insync.replicas 时 Broker 拒绝写入并返回 NOT_ENOUGH_REPLICAS |
| 能做什么 | 强制保证写入副本数；在副本不足时优先保护数据而非可用性 |
| 怎么用 | `acks=all` + `min.insync.replicas=2` 组合配置 |
| 原理和工作流程 | acks=all 时 Broker 校验当前 ISR 大小是否满足 min.insync.replicas，不满足则拒绝写入返回 NOT_ENOUGH_REPLICAS，不会自动降级为 acks=1，也不会等待 ISR 恢复后自动补发 |
| 缺点 | 副本不足时服务不可写；需监控 ISR 并及时恢复副本；配置不当影响可用性 |

### 5. ★★ 消费者使用 enable.auto.commit=true（默认值）可能导致的问题是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 自动提交按时间间隔提交位移，提交时机与业务处理完成无关 |
| 能做什么 | 简化位移管理；但也可能造成消息被跳过或重复消费 |
| 怎么用 | `enable.auto.commit=false` 配合 `commitSync()` 手动提交 |
| 原理和工作流程 | 自动提交按 auto.commit.interval.ms 默认 5s 定时提交。消息已拉取且位移已提交但业务未处理完时宕机，重启后从未处理消息之后继续，表现为消息丢失。与 Broker 是否拒收消息、能否加入消费者组无关 |
| 缺点 | 提交时机不可控；丢消息风险；生产环境不推荐 |

### 6. ★★★ Kafka 消费者的位移提交后，位移数据存储在（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Kafka 0.9 后消费者位移存储在内部 Topic `__consumer_offsets` |
| 能做什么 | 持久化各组消费进度；支持消费者重启后从上次位置继续；compact 只保留最新位移 |
| 怎么用 | `kafka-consumer-groups.sh --describe --group order-group` 查看 |
| 原理和工作流程 | 位移以 group+topic+partition 为 Key 写入 `__consumer_offsets`（默认 50 分区），使用 compact 清理策略只保留最新值。0.9 之前存于 ZooKeeper /consumers，因写入频繁被废弃 |
| 缺点 | 内部 Topic 需合理设置分区与副本；位移提交频繁增加 Broker 压力；查询依赖命令行工具 |

### 7. ★★ 以下哪种 Rebalance 分配策略可以做到"分阶段迁移、迁移期间不停止消费"？（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Cooperative Sticky 采用增量式再均衡协议，分两轮迁移且不停止消费 |
| 能做什么 | 只撤销需迁移的 Partition；其余 Partition 持续消费；减少迁移抖动 |
| 怎么用 | `partition.assignment.strategy=CooperativeStickyAssignor`（Kafka 2.4+） |
| 原理和工作流程 | Cooperative Sticky 第一轮消费者仅撤销需迁移的 Partition，第二轮完成再分配，期间其他 Partition 继续消费。Range、RoundRobin、Sticky 均为 Eager 协议，Rebalance 期间先放弃全部 Partition 再重新分配，消费短暂停止 |
| 缺点 | 需 Kafka 2.4+；与旧协议混用需谨慎；分配过程稍复杂，排查成本高 |

### 8. ★★★ 以下关于 Kafka 日志清理策略的描述，错误的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | delete 按时间/大小删除日志段，compact 按 Key 保留最新 Value，两者可同时配置 |
| 能做什么 | delete 控制存储成本；compact 保留每个 Key 最新状态；组合策略兼顾两者 |
| 怎么用 | `cleanup.policy=delete` / `compact` / `delete,compact` |
| 原理和工作流程 | compact 针对相同 Key 只保留最新 Value，不同 Key 全部保留，并非"只保留最后一条"。delete 按 retention.ms / retention.bytes 删除整个日志段。同一 Topic 可配置 "delete,compact" 同时生效，compact 适合变更日志与状态快照 |
| 缺点 | compact 后 offset 出现空洞；压缩消耗磁盘与 CPU；delete 会整段删除可能丢数据 |

### 9. ★★★ 关于 Kafka Topic 的分区数量，描述正确的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Kafka 分区数只能增加不能减少，且已有消息不会重新分布 |
| 能做什么 | 增加分区提升并行度；扩容消费能力；限制单 Broker 分区总量 |
| 怎么用 | `kafka-topics.sh --alter --topic order --partitions 48` |
| 原理和工作流程 | 减少分区会改变消息归属，破坏分区内顺序与位移连续性，因此 Kafka 不支持减少。增加分区后已有消息仍留在原分区，只有新消息按新分区数路由。分区数也不会由 Broker 自动调整 |
| 缺点 | 只能单向扩容；分区过多增加元数据开销与恢复时间；已有数据无法重分布 |

### 10. ★★ Kafka 事务生产者实现 Exactly-Once 时，消费者需要配置的隔离级别是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 消费者需设置 isolation.level=read_committed 只消费已提交事务消息 |
| 能做什么 | 过滤未提交与已回滚事务消息；保障 Exactly-Once 语义；控制消息可见性 |
| 怎么用 | `isolation.level=read_committed` |
| 原理和工作流程 | 事务消息由控制批次标记事务边界，read_committed 时 Broker 只返回已提交事务的消息，未提交或已回滚消息不可见。默认 read_uncommitted 会读到未提交事务消息，破坏 Exactly-Once 语义 |
| 缺点 | read_committed 增加 Broker 过滤开销；事务未提交期间消费延迟；默认值易踩坑 |

### 11. ★★ 关于 Kafka 副本数（replication.factor）的描述，正确的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 副本数不能超过 Broker 数，且应 ≥ min.insync.replicas |
| 能做什么 | 提供数据冗余与故障容错；副本数增加时自动为已有分区补全新副本 |
| 怎么用 | `replication.factor=3` + `min.insync.replicas=2` |
| 原理和工作流程 | 副本数超过 Broker 数会导致分区无法分配。副本数需 ≥ min.insync.replicas，否则 acks=all 永远无法满足，生产者无法写入。副本数为 1 时无冗余，Broker 宕机即不可用。副本数增加后 Kafka 会自动创建新副本并同步数据 |
| 缺点 | 副本多增加存储与网络开销；副本不足时写入受限；跨机架分配需规划 |

### 12. ★★ 以下关于 Kafka 消息顺序性的描述，正确的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Kafka 仅保证单 Partition 内有序；幂等 + max.in.flight ≤ 5 时重试不破坏分区内顺序 |
| 能做什么 | 分区内严格有序；幂等配合限制在途请求防止重试乱序；跨分区顺序需业务处理 |
| 怎么用 | `enable.idempotence=true`；`max.in.flight.requests.per.connection=5` |
| 原理和工作流程 | Kafka 只保证单 Partition 内按写入顺序有序，不保证跨分区全局有序。开启幂等且 max.in.flight ≤ 5 时，Broker 按序列号拒绝乱序写入，重试也不会造成分区内乱序；未开幂等且 max.in.flight > 1 时重试可能乱序 |
| 缺点 | 无全局顺序；依赖分区数权衡顺序与吞吐；跨分区乱序需业务幂等或版本号处理 |

---

## 二、简答题（8 题，每题附完整解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 需要文字阐述原理的题型，本题集共 8 道，覆盖副本同步、可靠性配置、位移提交、Rebalance、高吞吐、日志清理、事务与 EOS、ZK 与 KRaft |
| 能做什么 | 考查 LEO 与 HW 区别、三配置防丢消息组合、位移提交方式与风险、分配策略与抖动治理、高吞吐六设计、delete/compact 差异、Kafka 与 RocketMQ 事务对比、KRaft 解决的问题 |
| 怎么用 | 分点阐述原理，结合配置项和流程图说明 |
| 原理和工作流程 | 简答题要求系统阐述机制原理与流程，覆盖 HW 更新流程、可靠性三配置组合效果、四种位移提交方式、四种分配策略与五类抖动治理措施、顺序写/Page Cache/零拷贝各自解决的问题、日志段三文件与两种清理策略、事务协调器与两阶段提交、KRaft Raft Quorum。每题附完整解析 |
| 缺点 | 主观评分；答案需全面否则失分；难以机器批改 |

### 1. 解释 Kafka 中 LEO 与 HW 的区别，以及 HW 如何保证副本一致性

| 维度 | 内容 |
|------|------|
| 是什么 | LEO 是下一条待写入 offset，HW 是 ISR 中所有副本都已同步到的 offset，HW = min(ISR 的 LEO) |
| 能做什么 | 界定消费者可见范围；标识已提交消息；Leader 切换后保证新 Leader 含已提交消息 |
| 怎么用 | Leader 自动维护，Follower 通过 Fetch 上报 LEO 并接收 HW |
| 原理和工作流程 | Follower 发 Fetch 请求携带自身 LEO，Leader 更新其 LEO 后取 ISR 最小值推进 HW，并在响应中同步 HW。消费者只能消费 offset < HW 的消息。只有 HW 之前的消息被 ISR 全部持久化，新 Leader 必然包含，从而不丢失。HW 更新有一轮延迟，Leader 切换可能截断，需 Leader Epoch 修正 |
| 缺点 | HW 滞后导致消费延迟；截断导致短暂不一致；概念理解成本高 |

### 2. Kafka 如何通过 acks、min.insync.replicas、unclean.leader.election.enable 三者配合保证消息不丢失

| 维度 | 内容 |
|------|------|
| 是什么 | 写入确认、最小同步副本、选举约束三个配置协同，缺一不可的防丢消息机制 |
| 能做什么 | acks=all 等所有 ISR 确认；min.insync.replicas=2 限制最小副本；禁止非 ISR 选举 |
| 怎么用 | `acks=all`；`min.insync.replicas=2`；`unclean.leader.election.enable=false` |
| 原理和工作流程 | acks=all 但 min.insync.replicas=1 时 ISR 仅 Leader 仍可写入，宕机丢消息；min.insync.replicas=2 但 acks=1 时 Leader 写入即返回仍会丢。三者同配后 ISR 至少 2 副本、全部确认才算提交、新 Leader 必来自 ISR，已提交消息不丢。代价是 ISR 不足时写入失败，可用性下降 |
| 缺点 | 可靠性与可用性取舍；ISR 恢复前不可写；需监控 ISR 与 UnderReplicatedPartitions |

### 3. Kafka 消费者的位移提交方式有哪些 自动提交为什么会导致重复消费或消息丢失

| 维度 | 内容 |
|------|------|
| 是什么 | 自动提交、手动同步提交、手动异步提交、手动指定位移四类提交方式 |
| 能做什么 | 自动提交简化管理；commitSync 可靠；commitAsync 高吞吐；指定位移支持批处理精确控制 |
| 怎么用 | `enable.auto.commit=false`；`commitSync()`；`commitAsync()`；`commitSync(Map)` |
| 原理和工作流程 | 自动提交按 auto.commit.interval.ms 定时提交，与业务处理无关：已提交位移但业务未完成时宕机导致消息被跳过（丢失），业务已完成但未到提交周期时宕机导致重复消费。正确做法为关闭自动提交、处理成功后 commitSync、消费端实现业务唯一 ID 幂等、合理设置 max.poll.records |
| 缺点 | 手动提交增加复杂度；异步提交失败不重试；至少一次语义下重复不可避免 |

### 4. Kafka 有哪些分区分配策略 如何避免 Rebalance 抖动

| 维度 | 内容 |
|------|------|
| 是什么 | Range、RoundRobin、Sticky、Cooperative Sticky 四种分配策略及 Rebalance 抖动治理 |
| 能做什么 | Range 简单；RoundRobin 均匀；Sticky 少迁移；Cooperative Sticky 增量迁移不停消费 |
| 怎么用 | `partition.assignment.strategy=CooperativeStickyAssignor`；静态成员 `group.instance.id` |
| 原理和工作流程 | Range 按 Topic 分区序号范围切分易不均，RoundRobin 全分区轮询均匀但全量重分配，Sticky 尽量保留原分配，Cooperative Sticky 分两轮增量迁移。抖动治理：调大 session.timeout.ms 至 30s、heartbeat.interval.ms 至 3s 减少误判；处理时间远小于 max.poll.interval.ms；耗时逻辑异步化；用静态成员；避免频繁启停与长 GC |
| 缺点 | Eager 协议 Rebalance 期间停止消费；静态成员超时仍会触发；分区数变更无法完全避免 |

### 5. Kafka 高吞吐原理中 顺序写 Page Cache 零拷贝分别解决了什么问题

| 维度 | 内容 |
|------|------|
| 是什么 | 顺序写解决随机 I/O，Page Cache 避免频繁磁盘读写，零拷贝消除用户态拷贝 |
| 能做什么 | 顺序写达 600MB/s；Page Cache 使热数据读取几乎无磁盘 I/O；零拷贝将 4 次拷贝降至 2 次 |
| 怎么用 | 追加写入日志段；依赖 OS 页缓存；Broker 自动调用 sendfile |
| 原理和工作流程 | 消息只追加到日志段末尾避免随机 I/O；读写经 OS 页缓存，写先落缓存由 OS 异步刷盘，读优先命中缓存；sendfile 让数据从 Page Cache 直接 DMA 到网卡，不经过用户态。配合批量发送、批量压缩、分区并行进一步提升吞吐。依赖 Page Cache 而非 JVM 堆内存，避免 GC 停顿 |
| 缺点 | 依赖 OS 缓存机制，内存不足时性能下降；零拷贝无法在用户态加工数据；批量发送增加延迟 |

### 6. Kafka 的日志存储结构是怎样的 delete 和 compact 两种清理策略有何区别

| 维度 | 内容 |
|------|------|
| 是什么 | 每个 Partition 一个目录，内含 .log/.index/.timeindex 三类日志段文件；delete 与 compact 两种清理策略 |
| 能做什么 | 顺序追加存储消息；稀疏索引加速定位；按时间查找；控制存储成本与保留最新状态 |
| 怎么用 | `segment.bytes`；`cleanup.policy=delete` / `compact` / `delete,compact`；`retention.ms` |
| 原理和工作流程 | 日志段以基准 offset 命名，写满 segment.bytes 默认 1GB 后滚动新建。delete 按 retention.ms/bytes 删除整个日志段；compact 在满足 min.cleanable.dirty.ratio 后由 Log Cleaner 按 Key 压缩，只保留每个 Key 最新 Value，offset 出现空洞但顺序不变，适合变更日志、CDC、`__consumer_offsets` |
| 缺点 | compact 消耗磁盘与 CPU；offset 空洞需消费者按序读取；delete 整段删除可能丢数据 |

### 7. Kafka 的事务消息如何实现 Exactly-Once 与 RocketMQ 事务消息有何区别

| 维度 | 内容 |
|------|------|
| 是什么 | Kafka 通过 PID + 事务协调器 + 两阶段提交实现消费-处理-生产原子性；RocketMQ 通过半消息 + 本地事务 + 回查保证最终一致 |
| 能做什么 | Kafka 实现端到端 EOS 与跨分区原子写；RocketMQ 解决本地事务与发消息的一致性 |
| 怎么用 | `initTransactions()` → `beginTransaction()` → `sendOffsetsToTransaction()` → `commitTransaction()`；`isolation.level=read_committed` |
| 原理和工作流程 | Kafka 生产者向 Transaction Coordinator 注册获取 PID，开启事务后发送的消息带事务标记，位移提交纳入同一事务，提交或回滚原子生效，Broker 用控制批次标记边界，消费者 read_committed 只读已提交。RocketMQ 先发半消息，执行本地事务后 Commit/Rollback，未确认时 Broker 回查最多 15 次。Kafka 无回查，靠事务超时回滚 |
| 缺点 | Kafka 事务只覆盖 Kafka 内部，外部数据库仍需幂等或本地消息表；事务增加延迟；transaction.timeout.ms 需调优 |

### 8. Kafka 与 ZooKeeper 的关系是什么 KRaft 模式解决了什么问题

| 维度 | 内容 |
|------|------|
| 是什么 | 旧架构 ZK 存储元数据并选举 Controller；KRaft 用 Kafka 自身 Raft 协议管理元数据 |
| 能做什么 | ZK 存元数据、选 Controller、感知 Broker 上下线；KRaft 支持百万分区、秒级切换、单套部署 |
| 怎么用 | 旧架构 `zookeeper.connect`；KRaft 用 `process.roles`、`controller.quorum.voters` |
| 原理和工作流程 | ZK 存 Broker 列表、Topic/Partition、副本分配、ISR、Controller 信息，Broker 通过临时节点感知上下线。ZK 架构存在额外运维成本、元数据同步瓶颈、Controller 切换全量加载慢、双系统一致性边界复杂等问题。KRaft 让 Controller 组成 Raft Quorum，元数据存于 `__cluster_metadata` 并同步给 Broker，切换秒级完成 |
| 缺点 | 迁移不能直接从 ZK 切到 KRaft；需按版本升级；Controller 与 Broker 分离部署增加节点 |

---

## 三、场景设计题（3 题，每题附完整解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 给定业务场景设计 Kafka 方案的综合题型，本题集共 3 道 |
| 能做什么 | 考查消息积压应急处理、端到端 Exactly-Once 订单处理、集群容量规划与运维监控 |
| 怎么用 | 分析场景需求，按三级积压策略处置、用事务 API 保证原子性、按容量公式规划分区与副本 |
| 原理和工作流程 | 场景设计题要求结合业务需求选择 Kafka 特性，设计架构、可靠性保障、幂等、监控告警与故障处置。覆盖扩容分区、转存新 Topic、位移重置、事务 API 与本地消息表、分区与副本容量规划、监控阈值与运维规范。每题附完整设计方案和关键配置 |
| 缺点 | 答案开放主观评分；需综合多知识点；难以机器批改 |

### 1. 设计一个"Kafka 消息积压应急处理"方案

| 维度 | 内容 |
|------|------|
| 是什么 | 针对大促 Lag 从 1 万暴涨到 800 万的场景，按扩容分区、转存新 Topic、丢弃三级处置 |
| 能做什么 | 第一级扩容消费者至分区数上限或扩容分区；第二级转存新 Topic 提升并行度；第三级重置位移丢弃 |
| 怎么用 | `--alter --topic order-topic --partitions 48`；临时消费者纯转发；`--reset-offsets --to-latest --execute` |
| 原理和工作流程 | 先分析 12 分区仅 3 消费者的空闲并行度，优先扩容消费者至 12 个；不足则扩容分区至 48，注意分区只增不减且已有消息不重分布。消费逻辑本身慢时，建 48 分区新 Topic，用纯转发消费者快速转存，再并行消费，需幂等防重复。数据可容忍丢失时重置位移到最新或删除重建。配套 Lag 告警、消费者数上限、大促预案、消费耗时监控、死信通道 |
| 缺点 | 扩容分区增加元数据开销；转存期间可能重复且需额外运维；丢弃不可逆需评估影响 |

### 2. 设计一个"端到端 Exactly-Once"的 Kafka 订单处理方案

| 维度 | 内容 |
|------|------|
| 是什么 | 上游 acks=all 加幂等，订单服务用事务 API 将消费位移提交与下游发货消息放入同一事务，下游 read_committed |
| 能做什么 | 不丢靠三副本两同步；不重靠 PID 与序列号；原子靠事务；可见性靠 read_committed；外部系统靠本地消息表兜底 |
| 怎么用 | `initTransactions()`；`beginTransaction()`；`sendOffsetsToTransaction(offsets, groupMetadata)`；`commitTransaction()`；`isolation.level=read_committed` |
| 原理和工作流程 | 生产者 acks=all 且 enable.idempotence=true，replication.factor=3、min.insync.replicas=2。消费者关闭自动提交，每批 poll 后 beginTransaction，逐条处理并发送下游消息，再 sendOffsetsToTransaction 把位移纳入事务，最后 commitTransaction；异常时 abortTransaction 并重新定位到批次起点。下游消费者 read_committed 只读已提交事务。涉及数据库时用本地消息表、唯一索引幂等或对账补偿兜底 |
| 缺点 | 事务超时需控制单批数据量；事务协调器故障影响提交；外部数据库仍需业务幂等；事务增加延迟 |

### 3. 设计一个"Kafka 集群容量规划与运维监控"方案

| 维度 | 内容 |
|------|------|
| 是什么 | 承载日均 20 亿条消息的集群，规划 Broker 数、分区数、副本数、磁盘容量并建立监控与故障处置体系 |
| 能做什么 | 分区按峰值 TPS 除以单分区承载并预留 2-3 倍；副本 3 且 min.insync.replicas=2；磁盘按日均量乘保留天数乘副本数乘 1.3 |
| 怎么用 | `replication.factor=3`；`min.insync.replicas=2`；`unclean.leader.election.enable=false`；`compression.type=lz4`；`log.segment.bytes=1073741824` |
| 原理和工作流程 | 容量规划中 Broker 至少 6 台保证容灾，单 Broker 分区总数不超过 2000-4000。监控指标含 Consumer Lag、ISR 收缩、UnderReplicatedPartitions、ActiveControllerCount 必须为 1、磁盘使用率 75%/85% 阈值、P99 延迟、网络吞吐。故障处置覆盖 Broker 宕机、副本不同步、Controller 频繁切换、分区分布不均、磁盘写满、Lag 突增。运维规范含变更窗口、扩容审批、脚本留痕与定期演练 |
| 缺点 | 容量估算依赖业务峰值假设；分区过多增加恢复时间；故障演练与工具化建设成本高 |

---

> [返回原文](./Kafka笔面试题集.md) | [返回模块目录](../../../README.md) | [返回知识导览](../../../知识导览.md)
