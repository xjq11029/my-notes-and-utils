# RocketMQ 笔面试题集 导览

> 定位：五维框架浓缩提炼 RocketMQ笔面试题集.md 全部内容小节，快速查阅与复习。
> 用法：每个题型分类对应一张概要表格，每道题目提取所考知识点对应一张纵向表格，需要深入理解时跳转 [原文](./RocketMQ笔面试题集.md)。
> 前置知识：[RocketMQ核心原理](./01-RocketMQ核心原理-导览.md)、[RocketMQ高级特性](./02-RocketMQ高级特性-导览.md)

---

## 一、选择题（10 题，每题附解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 从给定选项中选择正确答案的客观题型，本题集共 10 道，覆盖 RocketMQ 核心组件、存储模型、高级特性 |
| 能做什么 | 考查 NameServer 职责、CommitLog 存储、事务消息、延迟等级、顺序消息、集群模式、长轮询等点状知识 |
| 怎么用 | 阅读题干排除干扰项，结合解析巩固易混淆概念 |
| 原理和工作流程 | 每题聚焦单一知识点，通过选项对比强化辨析。星号标注难度，一星为基础、二星为进阶、三星为深入。覆盖 RocketMQ 架构、存储、事务、延迟、顺序、过滤、集群、消费模式等核心考点 |
| 缺点 | 单题覆盖面窄；选项存在猜测成分；难以考查综合设计能力 |

### 1. ★ RocketMQ 中负责路由注册和发现的组件是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | NameServer 作为 RocketMQ 无状态路由注册中心的定位，区别于 Broker、Producer、Consumer |
| 能做什么 | 接收 Broker 注册；维护路由信息；供 Producer 和 Consumer 查询 |
| 怎么用 | 部署多台 NameServer 配置 `namesrvAddr=host1:9876;host2:9876` |
| 原理和工作流程 | NameServer 无状态各节点不通信，Broker 启动向所有 NameServer 注册心跳 30s 维持，Producer 和 Consumer 定时 30s 拉取路由信息。Broker 负责消息存储转发，Producer 生产消息，Consumer 消费消息 |
| 缺点 | 最终一致性有延迟；NameServer 单点需客户端重试其他节点；无主动推送路由变更 |

### 2. ★ RocketMQ 中所有消息统一存储的文件是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | CommitLog 作为 RocketMQ 消息主体存储文件，所有 Topic 消息顺序追加写入同一个 CommitLog |
| 能做什么 | 顺序写磁盘 600MB/s 高吞吐；统一存储简化管理；按 offset 定位消息 |
| 怎么用 | 默认 1GB 文件，`$HOME/store/commitlog/` 目录存储 |
| 原理和工作流程 | 所有 Topic 消息顺序追加写入同一个 CommitLog 文件，写满 1GB 新建。ConsumeQueue 是按 Topic+Queue 的索引文件，IndexFile 是按 Key 的哈希索引文件，两者均非消息主体存储 |
| 缺点 | 消费需随机读取依赖 Page Cache；单文件损坏影响所有 Topic；需 ConsumeQueue 索引加速 |

### 3. ★ 以下关于 RocketMQ NameServer 的描述，正确的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | NameServer 无状态、各节点不通信、不主动推送、不负责任消息存储的特性辨析 |
| 能做什么 | 识别 NameServer 的正确特性：无状态不通信、被动查询、仅路由注册 |
| 怎么用 | 部署多台独立 NameServer 无需配置节点间通信 |
| 原理和工作流程 | NameServer 各节点之间不通信互不感知，不通过 Gossip 等协议同步数据。Producer 和 Consumer 定时 30s 从 NameServer 拉取路由信息，NameServer 不主动推送。Broker 负责消息存储转发，NameServer 仅负责路由注册和发现 |
| 缺点 | 最终一致性有 30s 延迟窗口；路由变更无主动推送；无健康检查细化 |

### 4. ★ RocketMQ 中实现消息过滤的两种方式是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Tag 过滤基于 ConsumeQueue Tag HashCode 粗粒度过滤，SQL 表达式过滤基于消息属性值细粒度过滤 |
| 能做什么 | Tag 过滤简单分类；SQL 过滤复杂条件如 "amount > 500 AND region = 'east'" |
| 怎么用 | `selectorExpression="create"`；`selectorType=SelectorType.SQL92` 加 `selectorExpression="amount > 500"` |
| 原理和工作流程 | Tag 过滤在 Broker 端基于 ConsumeQueue 20 字节条目中的 Tag HashCode 比较，性能高。SQL 过滤需 Broker 开启 enablePropertyFilter 解析消息属性和计算表达式，性能较低。两种方式均为 Broker 端过滤，减少不必要消息的网络传输 |
| 缺点 | SQL 过滤性能较低需 Broker 额外配置；Tag 过滤粒度粗；Tag 和 SQL 同时使用为 AND |

### 5. ★★ 以下关于 RocketMQ 事务消息的描述，错误的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 事务消息回查最多 15 次而非 3 次的正确认知，半消息机制和最终一致性的原理 |
| 能做什么 | 半消息消费者不可见；本地事务 Commit 或 Rollback；回查最多 15 次确认最终状态 |
| 怎么用 | `sendMessageInTransaction()` 加 `@RocketMQTransactionListener` |
| 原理和工作流程 | 半消息发送后消费者不可见，Producer 执行本地事务成功返回 Commit 失败 Rollback。Broker 未收到确认定时回查，Producer 的 checkLocalTransaction 返回本地事务状态，最多回查 15 次而非 3 次。事务消息用于保证分布式事务最终一致性 |
| 缺点 | 回查次数 15 次耗时较长；Producer 宕机回查失败；回查逻辑需幂等 |

### 6. ★★ RocketMQ 延迟消息共支持多少个延迟等级？（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 18 个预设延迟等级从 1s 到 2h，不可自定义，需修改 Broker 配置来扩展 |
| 能做什么 | 订单超时取消；定时提醒；延迟通知；退避重试 |
| 怎么用 | `message.setDelayTimeLevel(16)` 30 分钟延迟 |
| 原理和工作流程 | 延迟消息写入时 Topic 替换为 SCHEDULE_TOPIC_XXXX，ScheduleMessageService 定时任务按延迟等级扫描到期消息重新投递。18 个等级为 1s、5s、10s、30s、1m、2m、3m、4m、5m、6m、7m、8m、9m、10m、20m、30m、1h、2h |
| 缺点 | 不支持自定义延迟时间；延迟非精确有 100ms 偏差；大量延迟消息扫描压力大 |

### 7. ★★ 以下关于 RocketMQ 顺序消息的描述，正确的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 分区顺序消息通过 MessageQueueSelector 按业务 Key 哈希将同一 Key 消息发往同一队列实现分区内有序 |
| 能做什么 | 订单状态流转；Binlog 同步；账户流水处理 |
| 怎么用 | `syncSendOrderly()` 加 `orderId` 哈希键；`consumeMode=ConsumeMode.ORDERLY` |
| 原理和工作流程 | 全局顺序使用单 MessageQueue 串行而非多队列并行。分区顺序同一业务 Key 消息哈希发往同一队列，消费端 ORDERLY 模式单线程消费，失败挂起不跳过。顺序消息吞吐量低于普通消息 |
| 缺点 | 全局顺序单队列吞吐极低；消费失败阻塞后续消息；Rebalance 期间有短暂中断 |

### 8. ★★ 以下哪个不是 RocketMQ 的高可用集群部署模式？（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | RocketMQ 三种集群模式为多 Master、多 Master 多 Slave、Dledger，不依赖 ZooKeeper 选主 |
| 能做什么 | 多 Master 开发测试；多 Master 多 Slave 一般生产；Dledger 金融级自动切换 |
| 怎么用 | `brokerRole=SYNC_MASTER`；`enableDLegerCommitLog=true` |
| 原理和工作流程 | RocketMQ 不像 Kafka 旧版本依赖 ZooKeeper 选主。Dledger 是 RocketMQ 自带的 Raft 实现，基于 Raft 协议自动选主和日志复制。多 Master 无 Slave 可用性低，多 Master 多 Slave 异步复制可能丢数据 |
| 缺点 | 多 Master 无 Slave 数据丢失风险高；多 Master 多 Slave 需手动切换；Dledger 需至少 3 奇数节点 |

### 9. ★★★ 以下关于 RocketMQ 存储模型的描述，错误的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | ConsumeQueue 是异步构建的由 ReputMessageService 定时从 CommitLog 转发，并非同步写入 |
| 能做什么 | 识别 ConsumeQueue 异步构建机制；CommitLog 1GB 单文件；ConsumeQueue 20 字节条目；IndexFile 按 Key 查询 |
| 怎么用 | 默认配置，ReputMessageService 自动异步构建 ConsumeQueue |
| 原理和工作流程 | CommitLog 默认单文件 1GB，ConsumeQueue 每条固定 20 字节含 8 字节 Offset 加 4 字节大小加 8 字节 Tag HashCode。ConsumeQueue 由 ReputMessageService 异步从 CommitLog 转发构建，存在延迟。IndexFile 按 Key 哈希索引支持按 Key 检索消息 |
| 缺点 | ConsumeQueue 异步构建有延迟；CommitLog 单文件损坏影响所有 Topic；IndexFile 占用额外磁盘 |

### 10. ★★★ RocketMQ 的 Push 消费模式底层实际是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Push 消费模式底层实际是长轮询 Long Polling，Consumer 发起请求 Broker 挂起等待，而非 Broker 主动推送 |
| 能做什么 | 兼顾实时性和资源消耗；避免短轮询空转和纯 Push 服务端压力 |
| 怎么用 | `longPollingEnable=true` 默认开启；Consumer 自动发起 PullRequest |
| 原理和工作流程 | Consumer 向 Broker 发起 PullRequest，Broker 有新消息立即返回，无新消息挂起请求默认 15s。挂起期间新消息到达唤醒返回，超时返回空 Consumer 立即发起下一次拉取。不是 WebSocket 或 gRPC 流式传输 |
| 缺点 | 挂起占用 Broker 连接资源；长轮询存在最多 15s 延迟；大量 Consumer 保活连接需管理 |

---

## 二、简答题（8 题，每题附完整解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 需要文字阐述原理的题型，本题集共 8 道，覆盖 RocketMQ 架构、存储、刷盘、事务、顺序、延迟、集群、消费模式 |
| 能做什么 | 考查架构组件职责、存储模型优势、刷盘策略选择、事务消息流程、顺序消息实现、延迟消息原理、集群模式对比、消费模式差异 |
| 怎么用 | 分点阐述原理，结合配置和流程说明 |
| 原理和工作流程 | 简答题要求系统阐述机制原理和流程，覆盖 RocketMQ 四大组件、CommitLog 加 ConsumeQueue 存储、同步异步刷盘对比、事务消息三阶段、顺序消息发送端和消费端保障、延迟消息 18 个等级和实现原理、三种集群模式差异、集群广播消费模式对比。每题附完整解析 |
| 缺点 | 主观评分；答案需全面否则失分；难以机器批改 |

### 1. 简述 RocketMQ 的整体架构和四大组件的职责

| 维度 | 内容 |
|------|------|
| 是什么 | NameServer 无状态路由注册、Broker 消息存储转发分 Master Slave、Producer 三种发送方式、Consumer 集群广播模式 |
| 能做什么 | NameServer 注册发现心跳 30s 剔除 120s；Broker CommitLog 存储同步异步刷盘；Producer 同步异步单向发送；Consumer 长轮询消费 |
| 怎么用 | 多 NameServer 部署，Broker 注册，Producer 和 Consumer 定时拉取路由 |
| 原理和工作流程 | NameServer 无状态不通信，Broker 向所有 NameServer 注册心跳维持。Producer 从 NameServer 拉取路由选择 MessageQueue 发送。Consumer 从 NameServer 拉取路由建立长连接拉取。Broker 消息统一存 CommitLog 通过 ConsumeQueue 索引，支持同步异步刷盘和复制 |
| 缺点 | NameServer 最终一致性有延迟；Broker 重注册依赖心跳；NameServer 单点需客户端重试 |

### 2. 解释 RocketMQ 的 CommitLog + ConsumeQueue 存储模型及其优势

| 维度 | 内容 |
|------|------|
| 是什么 | 三层存储模型：CommitLog 统一存储所有消息，ConsumeQueue 按 Topic+Queue 构建轻量索引，IndexFile 按 Key 哈希索引 |
| 能做什么 | CommitLog 顺序写 600MB/s；ConsumeQueue 20 字节条目快速定位；读写队列分离灵活缩容 |
| 怎么用 | 默认 1GB 文件，`commitlog/` 目录，`consumequeue/` 目录 |
| 原理和工作流程 | 所有 Topic 消息顺序追加写入同一个 CommitLog 避免随机 I/O。ConsumeQueue 每条 20 字节含 CommitLog Offset、消息大小、Tag HashCode，消费者按此定位。IndexFile 按 Key 哈希检索。优势为顺序写高吞吐、轻量索引加速消费、读写分离互不干扰、读写队列分离支持动态缩容 |
| 缺点 | 消费需随机读取依赖 Page Cache；ConsumeQueue 异步构建有延迟；CommitLog 单文件损坏影响所有 Topic |

### 3. 对比 RocketMQ 同步刷盘和异步刷盘的差异，以及如何选择

| 维度 | 内容 |
|------|------|
| 是什么 | 同步刷盘消息写入 Page Cache 后立即 fsync 强制刷盘 TPS 5k-10k；异步刷盘后台 500ms 刷盘 TPS 10w+ |
| 能做什么 | 同步刷盘金融支付级可靠 Broker 宕机不丢；异步刷盘日志收集高吞吐可能丢失 500ms 内消息 |
| 怎么用 | `flushDiskType=SYNC_FLUSH` 或 `ASYNC_FLUSH` |
| 原理和工作流程 | 同步刷盘消息写入 Page Cache 后立即调用 fsync 强制刷盘，返回前等待刷盘完成，延迟 ms 级。异步刷盘消息写入 Page Cache 后立即返回，后台线程每 500ms 刷盘，延迟 us 级。金融用同步刷盘，日志用异步刷盘，大多数业务推荐异步刷盘加同步复制折中 |
| 缺点 | 同步刷盘吞吐极低不适合高并发；异步刷盘 Broker 宕机可能丢消息；刷盘与复制策略需组合考虑 |

### 4. 简述 RocketMQ 事务消息的三阶段流程

| 维度 | 内容 |
|------|------|
| 是什么 | 发送半消息消费者不可见、执行本地事务返回 Commit 或 Rollback、Broker 未确认时回查最多 15 次 |
| 能做什么 | 分布式事务下单；订单创建与库存扣减一致性；跨服务数据同步 |
| 怎么用 | `sendMessageInTransaction()` 加 `@RocketMQTransactionListener` |
| 原理和工作流程 | 第一阶段发送半消息消费者不可见。第二阶段执行本地事务成功返回 Commit 失败 Rollback。第三阶段 Broker 未收到确认时定时扫描 PREPARED 状态超过 60s 的半消息发起回查，Producer 的 checkLocalTransaction 根据数据库实际状态返回结果，最多回查 15 次 |
| 缺点 | 回查增加延迟；Producer 宕机回查失败；回查逻辑需幂等；半消息占用存储 |

### 5. RocketMQ 如何实现顺序消息 消费端如何保证顺序不被破坏

| 维度 | 内容 |
|------|------|
| 是什么 | 发送端 MessageQueueSelector 按业务 Key 哈希固定队列，消费端 ORDERLY 模式分布式锁加单线程消费 |
| 能做什么 | 发送端重试不切换队列；消费端单线程前一条成功才拉取下一条；Rebalance 期间锁机制保证不并发 |
| 怎么用 | `syncSendOrderly()` 加 `orderId`；`consumeMode=ConsumeMode.ORDERLY` |
| 原理和工作流程 | 发送端按业务 Key 哈希选择固定 MessageQueue，同步发送重试不切换队列。消费端 ORDERLY 模式对每个 MessageQueue 加分布式锁，单线程消费前一条成功后才拉取下一条，失败挂起不跳过。Rebalance 期间释放锁新消费者申请锁后从上一 offset 继续 |
| 缺点 | 单线程消费限制吞吐；失败挂起阻塞后续消息；Rebalance 期间锁切换有短暂中断 |

### 6. 简述 RocketMQ 延迟消息的实现原理和 18 个延迟等级

| 维度 | 内容 |
|------|------|
| 是什么 | 延迟消息写入时 Topic 替换为 SCHEDULE_TOPIC_XXXX，ScheduleMessageService 定时扫描到期消息重新投递，18 个等级 1s 到 2h |
| 能做什么 | 订单超时取消；定时提醒；延迟通知；退避重试 |
| 怎么用 | `message.setDelayTimeLevel(16)` 30 分钟 |
| 原理和工作流程 | 延迟消息写入 CommitLog 时 Topic 替换为 SCHEDULE_TOPIC_XXXX，原始 Topic 存消息属性中。ScheduleMessageService 每 100ms 扫描各延迟等级 ConsumeQueue，到期消息读取原始 Topic 重新写入目标 CommitLog。18 个等级为 1s、5s、10s、30s、1m、2m、3m、4m、5m、6m、7m、8m、9m、10m、20m、30m、1h、2h |
| 缺点 | 不支持自定义延迟时间；延迟非精确有 100ms 偏差；大量延迟消息扫描压力大 |

### 7. 对比 RocketMQ 三种集群部署模式（多 Master、多 Master 多 Slave、Dledger）的优缺点

| 维度 | 内容 |
|------|------|
| 是什么 | 多 Master 无 Slave 可用性低；多 Master 多 Slave 异步复制可能丢数据；Dledger 基于 Raft 自动选主强一致 |
| 能做什么 | 多 Master 开发测试；多 Master 多 Slave 一般生产；Dledger 金融级自动切换 |
| 怎么用 | `brokerRole=SYNC_MASTER`；`enableDLegerCommitLog=true` |
| 原理和工作流程 | 多 Master 无 Slave 宕机不可消费。多 Master 多 Slave 每个 Master 配 1-2 个 Slave 异步复制可能丢少量数据。Dledger 基于 Raft 协议 N 个节点组成 Raft Group，Leader 故障自动选举 10s 内完成，消息写入超过半数确认才返回。选型建议为开发测试用多 Master，一般生产用多 Master 多 Slave，金融级用 Dledger |
| 缺点 | 多 Master 数据丢失风险高；多 Master 多 Slave 需手动切换；Dledger 需奇数节点 3 或 5 |

### 8. RocketMQ 的广播模式和集群模式有什么区别 各适用于什么场景

| 维度 | 内容 |
|------|------|
| 是什么 | 集群模式同组内每条消息只被一个 Consumer 消费；广播模式每条消息被所有 Consumer 消费 |
| 能做什么 | 集群模式负载均衡分布式任务调度；广播模式配置刷新缓存更新通知推送 |
| 怎么用 | `setMessageModel(MessageModel.CLUSTERING)` 或 `BROADCASTING` |
| 原理和工作流程 | 集群模式消费进度存在 Broker 端，MessageQueue 均匀分配给 Consumer 支持动态增减和 Rebalance。广播模式消费进度存在 Consumer 本地，每个 Consumer 消费全部 MessageQueue，Consumer 数量增减不影响其他 Consumer。广播模式下 Consumer 重启可能重复消费需实现幂等 |
| 缺点 | 广播模式消费进度本地存储重启可能重复；广播模式不支持负载均衡；集群模式消费者数受限于 MessageQueue 数量 |

---

## 三、场景设计题（3 题，每题附完整解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 给定业务场景设计 RocketMQ 方案的综合题型，本题集共 3 道 |
| 能做什么 | 考查保证消息不丢失方案、订单超时取消系统、顺序消费方案的设计 |
| 怎么用 | 分析场景需求，设计生产者 Broker 消费者三层保障，选择延迟消息和顺序消息等特性 |
| 原理和工作流程 | 场景设计题要求结合业务需求选择 RocketMQ 特性，设计架构、可靠性保障、幂等、分布式锁、监控告警。覆盖同步发送加本地消息表、同步刷盘加同步复制加 Dledger、手动确认加死信、延迟消息等级选择、顺序消息分区策略等典型方案。每题附完整设计方案和关键配置 |
| 缺点 | 答案开放主观评分；需综合多知识点；难以机器批改 |

### 1. 设计一个"保证消息不丢失"的 RocketMQ 方案

| 维度 | 内容 |
|------|------|
| 是什么 | 从生产者同步发送加本地消息表、Broker 同步刷盘加同步复制加 Dledger、消费者手动确认加重试加死信三环节保障消息不丢失 |
| 能做什么 | 生产者同步发送重试 3 次加本地消息表定时补偿；Broker 同步刷盘同步复制 Dledger 强一致；消费者手动确认重试 5 次死信兜底 |
| 怎么用 | `syncSend()` 加 `retryTimesWhenSendFailed=3`；`flushDiskType=SYNC_FLUSH` 加 `brokerRole=SYNC_MASTER`；`maxReconsumeTimes=5` |
| 原理和工作流程 | 生产者端同步发送加重试加本地消息表落库定时补偿。Broker 端同步刷盘 fsync 强制落盘同步复制等待 Slave 确认 Dledger Raft 超过半数确认。消费者端手动确认成功返回 CONSUME_SUCCESS 失败 RECONSUME_LATER 重试 5 次后死信队列。监控 Lag 和死信队列，定时对账补偿缺失消息 |
| 缺点 | 全链路同步吞吐极低；本地消息表增加数据库压力；死信需人工处理；监控对账增加运维成本 |

### 2. 设计一个"订单超时取消"系统

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 RocketMQ 延迟消息实现下单 30 分钟后未支付自动取消订单并释放库存的方案 |
| 能做什么 | 延迟等级 16 即 30 分钟精确触发；幂等检查防重复取消；分布式锁防并发；Redis 记录已处理 |
| 怎么用 | `setDelayTimeLevel(16)` 30 分钟延迟；`syncSend("order-cancel-topic:cancel", message, 3000, 16)` |
| 原理和工作流程 | 下单创建订单 UNPAID 状态扣减库存后发送 30 分钟延迟消息。到期后消费者收到消息查询订单状态，未支付则取消恢复库存，已支付或已取消则忽略。幂等保护使用 Redis setIfAbsent 记录已处理订单 ID，分布式锁 setIfAbsent 30s 超时防止并发取消。异常触发重试 5 次，失败进入死信队列 |
| 缺点 | 延迟等级固定不可自定义；延迟精度非精确；取消操作需幂等和分布式锁；海量订单延迟队列压力大 |

### 3. 设计一个"顺序消费"方案

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 syncSendOrderly 按账户 ID 哈希发送到固定队列，ConsumeMode.ORDERLY 分布式锁加单线程消费保证同一账户流水严格按序处理 |
| 能做什么 | 账户流水按序处理；余额计算正确；幂等防止重复；分区并行提升吞吐 |
| 怎么用 | `syncSendOrderly()` 加 `accountId` 哈希键；`consumeMode=ConsumeMode.ORDERLY`；Redis 幂等记录 |
| 原理和工作流程 | 发送端按账户 ID 哈希将同一账户流水发往同一 MessageQueue，重试不切换队列。消费端 ORDERLY 模式对每个 MessageQueue 加分布式锁单线程消费，前一条成功才处理下一条，失败挂起不跳过。分区策略为 20 个 MessageQueue 最多 20 个账户并行处理，同一账户串行。幂等使用 Redis 记录已处理 eventId 7 天过期。风险应对为设置合理重试次数 3-5 次快速进死信、监控慢消费告警、耗时逻辑异步化 |
| 缺点 | 单线程消费吞吐受限；消费失败阻塞该账户所有后续流水；Rebalance 期间锁切换有短暂中断；分区数需预评估 |

---

> [返回原文](./RocketMQ笔面试题集.md) | [返回模块目录](../../../README.md) | [返回知识导览](../../../知识导览.md)