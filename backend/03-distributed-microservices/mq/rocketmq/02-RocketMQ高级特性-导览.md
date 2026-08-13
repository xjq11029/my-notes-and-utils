# RocketMQ 高级特性 导览

> 定位：五维框架浓缩提炼 02-RocketMQ高级特性.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-RocketMQ高级特性.md)。
> 前置知识：[RocketMQ核心原理](./01-RocketMQ核心原理-导览.md)

---

## 一、核心概念

### 1.1 消费模式（集群 vs 广播）

| 维度 | 内容 |
|------|------|
| 是什么 | 集群模式同一 ConsumerGroup 内每条消息只被一个 Consumer 消费；广播模式每条消息被所有 Consumer 消费 |
| 能做什么 | 集群模式负载均衡分布式任务调度；广播模式配置刷新缓存更新通知推送 |
| 怎么用 | `setMessageModel(MessageModel.CLUSTERING)` 或 `BROADCASTING` |
| 原理和工作流程 | 集群模式消费进度存在 Broker 端，MessageQueue 均匀分配给 Consumer 支持动态增减和 Rebalance。广播模式消费进度存在 Consumer 本地，每个 Consumer 消费全部 MessageQueue。广播模式下 Consumer 重启可能重复消费，需实现幂等逻辑 |
| 缺点 | 广播模式消费进度本地存储重启可能重复；广播模式不支持负载均衡；集群模式消费者数量受限于 MessageQueue 数量 |

### 1.2 长轮询机制

| 维度 | 内容 |
|------|------|
| 是什么 | Push 消费模式底层实际是长轮询，消费者发起拉取请求，Broker 挂起请求等待消息到达默认 15s |
| 能做什么 | 兼顾实时性和资源消耗；避免短轮询空转和纯 Push 服务端压力 |
| 怎么用 | `longPollingEnable=true` 默认开启；`longPollingInterval` 配置挂起时间 |
| 原理和工作流程 | Consumer 向 Broker 发起 PullRequest，Broker 有新消息立即返回，无新消息挂起请求默认 15s。挂起期间新消息到达则唤醒挂起请求返回消息，超时则返回空 Consumer 立即发起下一次拉取 |
| 缺点 | 挂起期间占用 Broker 连接资源；长轮询存在延迟（最多 15s）；大量 Consumer 时长轮询保活连接需管理 |

### 1.3 消费重试（进阶）

| 维度 | 内容 |
|------|------|
| 是什么 | 消费重试的配置调优和死信处理，默认 16 次重试，超过后进入 %DLQ%{ConsumerGroup} 死信队列 |
| 能做什么 | 调整 maxReconsumeTimes 为 3-5 次；死信队列监听处理；消费线程池调优 |
| 怎么用 | `maxReconsumeTimes=5`；`@RocketMQMessageListener(topic="%DLQ%order-consumer-group")` |
| 原理和工作流程 | 普通业务重试 3-5 次，金融业务 5-10 次。消费线程 min 20 max 64 按 CPU 核数调整。死信队列消费者记录消息 ID、重试次数、消息体到数据库，触发告警通知人工处理 |
| 缺点 | 重试次数过多阻塞消费队列；死信需人工处理增加运维成本；重试消息与正常消息共用线程资源 |

### 1.4 顺序消息（全局顺序 vs 分区顺序）

| 维度 | 内容 |
|------|------|
| 是什么 | 全局顺序单队列串行读写吞吐极低；分区顺序同一业务 Key 消息发往同一队列分区内有序吞吐较高 |
| 能做什么 | 全局顺序极少数全局有序场景；分区顺序订单状态流转、Binlog 同步 |
| 怎么用 | `syncSendOrderly()` 加 MessageQueueSelector；`consumeMode=ConsumeMode.ORDERLY` |
| 原理和工作流程 | 发送端 syncSendOrderly 按业务 Key 哈希选择队列，重试不切换队列。消费端 ORDERLY 模式对每个 MessageQueue 加分布式锁单线程消费，前一条成功后才拉取下一条。Rebalance 期间通过锁机制保证同一队列仅一个消费者处理 |
| 缺点 | 全局顺序单队列串行吞吐极低；分区顺序消费失败挂起队列阻塞后续消息；顺序消费单线程处理限制吞吐 |

### 1.5 事务消息（半消息 / 两阶段确认 / 消息回查）

| 维度 | 内容 |
|------|------|
| 是什么 | RocketMQ 核心特性，通过半消息机制实现分布式事务最终一致性：发送半消息、执行本地事务、提交或回滚、异常兜底回查 |
| 能做什么 | 分布式事务下单；订单创建与库存扣减一致性；跨服务数据同步 |
| 怎么用 | `sendMessageInTransaction()` 加 `@RocketMQTransactionListener` 实现 executeLocalTransaction 和 checkLocalTransaction |
| 原理和工作流程 | 第一阶段发送半消息消费者不可见。第二阶段执行本地事务成功 Commit 失败 Rollback。第三阶段 Broker 未收到确认时定时回查，Producer 根据本地事务状态返回 Commit 或 Rollback 最多 15 次。半消息存在 CommitLog 标记为事务状态，Commit 前不构建 ConsumeQueue |
| 缺点 | 实现复杂度高需实现回查逻辑；回查增加延迟；半消息占用存储；Producer 需高可用否则回查失败 |

### 1.6 延迟消息（18 个等级）

| 维度 | 内容 |
|------|------|
| 是什么 | 18 个预设延迟等级从 1s 到 2h，使用 delayTimeLevel 参数指定，消息到期后自动投递到目标 Topic |
| 能做什么 | 订单超时取消；定时提醒；延迟通知；退避重试 |
| 怎么用 | `message.setDelayTimeLevel(16)` 30 分钟延迟 |
| 原理和工作流程 | 延迟消息写入时 Topic 替换为 SCHEDULE_TOPIC_XXXX，原始 Topic 存在消息属性中。ScheduleMessageService 定时任务按延迟等级扫描到期消息，重新写入目标 Topic。延迟精度约 100ms 偏差，非精确延迟 |
| 缺点 | 不支持自定义延迟时间仅 18 个预设等级；延迟精度非精确有秒级偏差；大量延迟消息扫描压力大；占用 CommitLog 存储 |

### 1.7 消息过滤（Tag 过滤 / SQL 表达式过滤）

| 维度 | 内容 |
|------|------|
| 是什么 | Tag 过滤基于 ConsumeQueue 的 Tag HashCode 粗粒度过滤；SQL 表达式过滤基于消息属性值细粒度过滤 |
| 能做什么 | Tag 过滤简单分类 "create"、"pay"；SQL 过滤复杂条件 "amount > 500 AND region = 'east'" |
| 怎么用 | `selectorExpression="create"`；`selectorType=SelectorType.SQL92` 加 `selectorExpression="amount > 500"` |
| 原理和工作流程 | Tag 过滤在 Broker 端基于 ConsumeQueue 20 字节条目中的 Tag HashCode 比较，性能高。SQL 过滤需 Broker 开启 enablePropertyFilter 解析消息属性和计算表达式，性能较低。Tag 和 SQL 同时设置时为 AND 关系 |
| 缺点 | SQL 过滤性能较低需 Broker 额外配置；Tag 过滤粒度粗仅支持简单匹配；Tag 和 SQL 同时使用可能导致意外过滤 |

### 1.8 高可用集群（多 Master / 多 Master 多 Slave / Dledger 选主）

| 维度 | 内容 |
|------|------|
| 是什么 | 三种集群模式：多 Master 无 Slave 可用性低；多 Master 多 Slave 异步复制；Dledger 基于 Raft 自动选主强一致 |
| 能做什么 | 多 Master 开发测试；多 Master 多 Slave 生产一般可靠；Dledger 金融级可靠自动切换 |
| 怎么用 | `brokerRole=SYNC_MASTER` 或 `ASYNC_MASTER`；`enableDLegerCommitLog=true` |
| 原理和工作流程 | 多 Master 模式无 Slave 宕机不可消费。多 Master 多 Slave 模式每个 Master 配 1-2 个 Slave，异步复制可能丢少量数据。Dledger 基于 Raft 协议，N 个节点组成 Raft Group，Leader 故障自动选举 10s 内完成，消息写入超过半数确认才返回，强一致不丢消息 |
| 缺点 | 多 Master 无 Slave 数据丢失风险高；多 Master 多 Slave 需手动切换；Dledger 节点数推荐奇数 3 或 5 偶数可能平票；Dledger 增加网络开销 |

---

## 二、底层原理

### 2.1 顺序消息实现原理

| 维度 | 内容 |
|------|------|
| 是什么 | 发送端通过 MessageQueueSelector 按业务 Key 哈希固定队列，消费端通过分布式锁加单线程保证分区内有序 |
| 能做什么 | 发送端重试不切换队列；消费端单线程消费前一条成功才拉取下一条；Rebalance 期间锁机制保证不并发 |
| 怎么用 | `syncSendOrderly()` 加 `orderId` 哈希键；`consumeMode=ConsumeMode.ORDERLY` |
| 原理和工作流程 | 发送端按业务 Key 哈希选择固定 MessageQueue，同步发送重试不切换队列。消费端 ORDERLY 模式对每个 MessageQueue 使用独立锁，向 Broker 申请分布式锁，单线程消费前一条成功后才拉取下一条，失败挂起不跳过。Rebalance 期间释放锁新消费者申请锁后从上一 offset 继续 |
| 缺点 | 单线程消费限制吞吐；失败挂起阻塞后续消息；Rebalance 期间锁切换有短暂中断 |

### 2.2 事务消息底层实现

| 维度 | 内容 |
|------|------|
| 是什么 | 半消息存储在 CommitLog 标记为事务状态，Commit 前不构建 ConsumeQueue 消费者不可见，通过回查保证最终一致性 |
| 能做什么 | 半消息事务状态管理；Broker 端事务状态表记录 PREPARED COMMIT ROLLBACK UNKNOWN；定时扫描回查 |
| 怎么用 | `sendMessageInTransaction()` 加 `@RocketMQTransactionListener` |
| 原理和工作流程 | 半消息存在 CommitLog 标记为事务状态，Commit 前不构建 ConsumeQueue。Broker 维护事务状态表，定时扫描 PREPARED 状态超过 60s 的消息发起回查。Producer 的 checkLocalTransaction 根据本地事务状态返回 Commit 或 Rollback。最多回查 15 次 |
| 缺点 | 回查增加延迟；Producer 宕机回查失败；半消息占用存储；事务状态表需维护 |

### 2.3 延迟消息实现原理

| 维度 | 内容 |
|------|------|
| 是什么 | 延迟消息写入时 Topic 替换为 SCHEDULE_TOPIC_XXXX，ScheduleMessageService 定时按延迟等级扫描到期消息重新投递 |
| 能做什么 | 18 个预设延迟等级；定时扫描到期投递；原始 Topic 保存在消息属性中 |
| 怎么用 | `message.setDelayTimeLevel(16)` 30 分钟 |
| 原理和工作流程 | 延迟消息写入 CommitLog 时 Topic 被替换为 SCHEDULE_TOPIC_XXXX，原始 Topic 和 QueueId 存储在消息属性中。ScheduleMessageService 定时任务每 100ms 扫描各延迟等级的 ConsumeQueue，到期消息读取原始 Topic 重新写入目标 CommitLog，未到期继续等待 |
| 缺点 | 仅 18 个预设等级不可自定义；非精确延迟有 100ms 偏差；大量延迟消息扫描压力大 |

### 2.4 Dledger 选主原理

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 Raft 协议实现自动选主和日志复制，N 个节点组成 Raft Group，Leader 故障自动选举 10s 内完成 |
| 能做什么 | Leader 选举随机定时器 150ms-300ms；日志复制超过半数确认；故障自动切换不丢消息 |
| 怎么用 | `enableDLegerCommitLog=true`；`dLegerPeers=n0-host:port;n1-host:port;n2-host:port` |
| 原理和工作流程 | 每个节点启动为 Follower，定时器到期未收到心跳转为 Candidate 加 Term 发起投票。收到超过半数投票成为 Leader 定期发送心跳。生产者消息发到 Leader，Leader 写本地后向 Follower 发送 AppendEntries，超过半数确认后提交。Leader 故障 10s 内完成重新选举 |
| 缺点 | 节点数偶数可能平票选举失败；同步复制增加延迟；Raft 日志需额外存储；需至少 3 节点 |

---

## 三、实战应用

### 3.1 订单状态流转（顺序消息实战）

| 维度 | 内容 |
|------|------|
| 是什么 | 使用 syncSendOrderly 按订单 ID 发送顺序消息，消费端 ConsumeMode.ORDERLY 保证同一订单状态变更按序处理 |
| 能做什么 | 订单创建、支付、发货、完成状态按序流转；库存扣减和恢复按序处理 |
| 怎么用 | `syncSendOrderly("order-status-topic:change", payload, orderId)`；`consumeMode=ConsumeMode.ORDERLY` |
| 原理和工作流程 | 同一订单 ID 的消息通过哈希发往同一 MessageQueue，消费端 ORDERLY 模式单线程消费，前一条处理成功后才处理下一条，保证状态不混乱 |
| 缺点 | 单线程顺序消费吞吐受限；消费失败阻塞后续消息；需保证发送端和消费端都使用顺序模式 |

### 3.2 分布式事务下单（事务消息实战）

| 维度 | 内容 |
|------|------|
| 是什么 | 通过事务消息保证订单创建和库存扣减的分布式事务一致性，executeLocalTransaction 执行本地事务，checkLocalTransaction 回查兜底 |
| 能做什么 | 订单创建与库存扣减原子性；支付成功与积分发放一致性；跨服务数据同步 |
| 怎么用 | `sendMessageInTransaction()` 加 `@RocketMQTransactionListener` |
| 原理和工作流程 | 发送半消息后执行本地事务扣减库存和创建订单，成功返回 COMMIT 半消息变为可消费，失败返回 ROLLBACK 半消息删除。Broker 未收到确认时回查 checkLocalTransaction 根据订单是否存在判断 COMMIT 或 ROLLBACK |
| 缺点 | 回查逻辑需幂等；Producer 宕机回查失败；事务消息增加延迟；本地事务失败需正确回滚 |

### 3.3 延迟消息实现订单超时取消

| 维度 | 内容 |
|------|------|
| 是什么 | 下单时发送延迟等级 16 即 30 分钟延迟消息，消费者收到后检查订单状态，未支付则取消并恢复库存 |
| 能做什么 | 订单超时自动取消；定时提醒；延迟通知 |
| 怎么用 | `syncSend("order-cancel-topic:cancel", message, 3000, 16)` 30 分钟延迟 |
| 原理和工作流程 | 下单后发送 30 分钟延迟消息，延迟到期后消费者收到消息查询订单状态，若为 UNPAID 则取消订单并恢复库存，若已支付则忽略。需保证取消操作幂等防止重复取消 |
| 缺点 | 延迟等级固定不可自定义；延迟精度非精确；大量延迟消息积压扫描压力大；取消操作需幂等设计 |

---

## 四、常见面试题

### 1. RocketMQ 如何实现顺序消息 全局顺序和分区顺序有什么区别

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 MessageQueueSelector 按业务 Key 哈希和 ConsumeMode.ORDERLY 分布式锁加单线程消费实现顺序消息 |
| 能做什么 | 全局顺序单队列串行；分区顺序多队列并行分区内有序 |
| 怎么用 | `syncSendOrderly()` 加 `orderId`；`consumeMode=ConsumeMode.ORDERLY` |
| 原理和工作流程 | 全局顺序 writeQueueNums=1 所有消息串行吞吐极低。分区顺序同一业务 Key 消息哈希发往同一队列，消费端 ORDERLY 模式对每个 MessageQueue 加分布式锁单线程消费，Rebalance 期间锁机制保证不并发。前一条成功后才处理下一条，失败挂起不跳过 |
| 缺点 | 全局顺序单队列吞吐极低；分区顺序单线程消费吞吐受限；消费失败阻塞后续消息 |

### 2. 事务消息的三阶段流程是怎样的 回查机制如何保证最终一致性

| 维度 | 内容 |
|------|------|
| 是什么 | 发送半消息消费者不可见、执行本地事务返回 Commit 或 Rollback、Broker 未确认时回查本地事务状态 |
| 能做什么 | 半消息 Commit 前不构建 ConsumeQueue；事务状态表记录 PREPARED COMMIT ROLLBACK UNKNOWN；回查最多 15 次 |
| 怎么用 | `sendMessageInTransaction()` 加 `@RocketMQTransactionListener` |
| 原理和工作流程 | 第一阶段发送半消息消费者不可见。第二阶段执行本地事务成功返回 COMMIT 失败 ROLLBACK。第三阶段 Broker 定时扫描 PREPARED 状态超过 60s 的半消息发起回查，Producer 的 checkLocalTransaction 根据数据库实际状态返回结果，最多回查 15 次 |
| 缺点 | 回查增加延迟；Producer 宕机回查失败；回查逻辑需幂等；半消息占用存储 |

### 3. RocketMQ 的延迟消息是如何实现的 有什么局限性

| 维度 | 内容 |
|------|------|
| 是什么 | 延迟消息写入时 Topic 替换为 SCHEDULE_TOPIC_XXXX，ScheduleMessageService 定时按延迟等级扫描到期消息重新投递 |
| 能做什么 | 18 个延迟等级 1s 到 2h；订单超时取消；定时提醒 |
| 怎么用 | `message.setDelayTimeLevel(16)` 30 分钟 |
| 原理和工作流程 | 延迟消息写入 CommitLog 时 Topic 替换为 SCHEDULE_TOPIC_XXXX，原始 Topic 存消息属性中。ScheduleMessageService 每 100ms 扫描各延迟等级 ConsumeQueue，到期消息读取原始 Topic 重新写入目标 CommitLog。局限性为仅 18 个预设等级不支持自定义、延迟非精确有 100ms 偏差、大量延迟消息扫描压力大、占用 CommitLog 存储 |
| 缺点 | 不支持自定义延迟时间；延迟精度非精确；大量延迟消息扫描压力大；占用 CommitLog 存储 |

### 4. Dledger 模式和传统主从模式有什么区别 什么场景下推荐使用 Dledger

| 维度 | 内容 |
|------|------|
| 是什么 | 传统主从手动切换异步复制可能丢数据；Dledger 基于 Raft 自动选主 10s 内完成强一致不丢消息 |
| 能做什么 | 传统主从开发测试；Dledger 金融支付订单交易自动故障切换 |
| 怎么用 | `brokerRole=SYNC_MASTER` 传统；`enableDLegerCommitLog=true` Dledger |
| 原理和工作流程 | 传统主从 Master 宕机需人工将 Slave 提升为 Master，异步复制可能丢少量数据。Dledger 基于 Raft 协议，N 个节点组成 Raft Group，Leader 自动选举 10s 内完成，消息写入超过半数确认才返回。推荐金融支付、订单交易等对数据一致性和可用性要求极高的场景使用 Dledger |
| 缺点 | Dledger 节点数需奇数 3 或 5；同步复制增加延迟；需额外存储 Raft 日志；需至少 3 节点 |

---

## 五、避坑指南

本节以表格形式列举常见错误、现象、原因与解决方案，属辅助清单内容，不单独生成五维表格。

## 本章学习自检

本节为自检清单，列出本章应掌握的能力点，不生成五维表格。

---

> [返回原文](./02-RocketMQ高级特性.md) | [返回模块目录](../../../README.md) | [返回知识导览](../../../知识导览.md)