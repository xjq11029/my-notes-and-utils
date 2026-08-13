# RocketMQ 笔面试题集

> 模块：04-message-queue（第4周 消息队列）
> 覆盖：RocketMQ 核心原理、高级特性
> 题量：10 道选择题 + 8 道简答题 + 3 道场景设计题

> 📖 **参考链接**：
> - [RocketMQ Documentation](https://rocketmq.apache.org/docs/) -- RocketMQ 官方文档总入口
> - [RocketMQ 架构设计](https://rocketmq.apache.org/docs/rmq-arc/) -- 四大组件与整体架构官方说明

---

## 一、选择题（10 题，每题附解析）

### 1. ★ RocketMQ 中负责路由注册和发现的组件是（ ）

A. Broker
B. NameServer
C. Producer
D. Consumer

**答案：B**

**解析：** NameServer 是 RocketMQ 的无状态路由注册中心，负责接收 Broker 注册、维护路由信息，供 Producer 和 Consumer 查询。Broker 是消息存储转发节点，Producer 是消息生产者，Consumer 是消息消费者。

---

### 2. ★ RocketMQ 中所有消息统一存储的文件是（ ）

A. ConsumeQueue
B. IndexFile
C. CommitLog
D. MessageStore

**答案：C**

**解析：** CommitLog 是 RocketMQ 的消息主体存储文件，所有 Topic 的消息顺序追加写入同一个 CommitLog。ConsumeQueue 是按 Topic+Queue 构建的索引文件，IndexFile 是按 Key 构建的哈希索引文件。

---

### 3. ★ 以下关于 RocketMQ NameServer 的描述，正确的是（ ）

A. NameServer 之间通过 Gossip 协议同步数据
B. NameServer 主动向 Producer 推送路由变更
C. NameServer 是无状态的，各节点之间不通信
D. NameServer 负责消息的存储和转发

**答案：C**

**解析：** NameServer 是无状态的，各节点之间不通信、互不感知。Producer 和 Consumer 定时从 NameServer 拉取路由信息（默认 30s），NameServer 不会主动推送。Broker 负责消息存储和转发，而非 NameServer。

---

### 4. ★ RocketMQ 中实现消息过滤的两种方式是（ ）

A. Key 过滤和 Value 过滤
B. Tag 过滤和 SQL 表达式过滤
C. 前缀过滤和正则过滤
D. Header 过滤和 Body 过滤

**答案：B**

**解析：** RocketMQ 提供 Tag 过滤（基于 ConsumeQueue 的 Tag HashCode）和 SQL 表达式过滤（基于消息属性值，需 Broker 开启 `enablePropertyFilter=true`）两种方式。

---

### 5. ★★ 以下关于 RocketMQ 事务消息的描述，错误的是（ ）

A. 事务消息通过半消息机制实现
B. 半消息在 Commit 前消费者不可见
C. 事务消息回查最多执行 3 次
D. 事务消息用于保证分布式事务的最终一致性

**答案：C**

**解析：** 事务消息回查最多执行 15 次，而非 3 次。当 Broker 未收到 Commit 或 Rollback 时，会定时向 Producer 回查本地事务状态，最多回查 15 次。A、B、D 均为正确描述。

> 📖 **参考链接**：[RocketMQ 事务消息](https://rocketmq.apache.org/docs/feature/transaction-message/) -- 事务消息半消息与回查机制官方说明

---

### 6. ★★ RocketMQ 延迟消息共支持多少个延迟等级？（ ）

A. 8 个
B. 12 个
C. 18 个
D. 24 个

**答案：C**

**解析：** RocketMQ 原生支持 18 个预设延迟等级，从 1s（等级 1）到 2h（等级 18）。延迟等级不可自定义，如需自定义延迟时间需修改 Broker 的 `messageDelayLevel` 配置。

---

### 7. ★★ 以下关于 RocketMQ 顺序消息的描述，正确的是（ ）

A. 全局顺序消息通过多 MessageQueue 并行实现
B. 分区顺序消息中，同一业务 Key 的消息通过哈希发送到同一 MessageQueue
C. 顺序消费模式下，消费失败会自动跳过该消息
D. 顺序消息的吞吐量与普通消息一致

**答案：B**

**解析：** 分区顺序消息通过 MessageQueueSelector 按业务 Key 哈希，将同一 Key 的消息发送到同一 MessageQueue 实现分区内有序。A 错误，全局顺序使用单 MessageQueue 串行；C 错误，消费失败会挂起该队列不跳过；D 错误，顺序消息吞吐量低于普通消息。

---

### 8. ★★ 以下哪个不是 RocketMQ 的高可用集群部署模式？（ ）

A. 多 Master 模式
B. 多 Master 多 Slave 模式
C. Dledger 模式
D. ZooKeeper 选主模式

**答案：D**

**解析：** RocketMQ 支持三种高可用集群模式：多 Master 模式、多 Master 多 Slave 模式、Dledger 模式（基于 Raft 协议自动选主）。RocketMQ 不像 Kafka 旧版本那样依赖 ZooKeeper 选主，Dledger 是 RocketMQ 自带的 Raft 实现。

---

### 9. ★★★ 以下关于 RocketMQ 存储模型的描述，错误的是（ ）

A. CommitLog 默认单文件大小为 1GB
B. ConsumeQueue 每条条目固定为 20 字节
C. ConsumeQueue 与 CommitLog 同步写入
D. IndexFile 支持按消息 Key 查询消息

**答案：C**

**解析：** ConsumeQueue 是异步构建的，由 ReputMessageService 定时从 CommitLog 转发构建，并非同步写入。A 正确，CommitLog 默认 1GB；B 正确，ConsumeQueue 条目 20 字节（8 字节 Offset + 4 字节大小 + 8 字节 Tag HashCode）；D 正确，IndexFile 按 Key 哈希索引。

---

### 10. ★★★ RocketMQ 的 Push 消费模式底层实际是（ ）

A. Broker 主动推送消息到 Consumer
B. 长轮询（Long Polling），Consumer 发起请求，Broker 挂起等待
C. WebSocket 双向通信
D. gRPC 流式传输

**答案：B**

**解析：** RocketMQ 的 Push 消费模式底层实际是长轮询。Consumer 向 Broker 发起拉取请求，Broker 有消息立即返回，无消息则挂起请求（默认 15s），期间新消息到达时唤醒返回。这种方式兼顾了实时性和资源消耗。

---

## 二、简答题（8 题，每题附完整解析）

### 1. 简述 RocketMQ 的整体架构和四大组件的职责。

**答案：**

RocketMQ 由四大组件构成：

1. **NameServer（路由注册中心）**：无状态，各节点之间不通信。接收 Broker 注册并维护路由信息，供 Producer 和 Consumer 查询。Broker 每 30s 发送心跳，120s 无心跳则剔除路由。

2. **Broker（消息存储转发）**：分为 Master 和 Slave，Master 负责读写，Slave 负责备份。消息统一存储在 CommitLog 中，通过 ConsumeQueue 索引加速消费。支持同步刷盘/异步刷盘和同步复制/异步复制。

3. **Producer（消息生产者）**：从 NameServer 获取路由信息，按负载均衡策略选择 MessageQueue 发送消息。支持同步、异步、单向三种发送方式。

4. **Consumer（消息消费者）**：从 NameServer 获取路由信息，建立长连接拉取消息。支持集群模式（负载均衡）和广播模式（全量消费）。

---

### 2. 解释 RocketMQ 的 CommitLog + ConsumeQueue 存储模型及其优势。

**答案：**

RocketMQ 采用三层存储模型：

1. **CommitLog**：所有 Topic 的消息顺序追加写入同一个 CommitLog 文件，默认单文件 1GB。顺序写磁盘速度可达 600MB/s，极大提升写入吞吐量。

2. **ConsumeQueue**：按 Topic+Queue 维度构建的轻量索引，每条条目固定 20 字节（8 字节 CommitLog Offset + 4 字节消息大小 + 8 字节 Tag HashCode）。消费者通过 ConsumeQueue 快速定位 CommitLog 中的消息位置。

3. **IndexFile**：按消息 Key 构建的哈希索引，支持按 Key 快速检索消息。

**优势：** 顺序写 CommitLog 避免随机 I/O；ConsumeQueue 轻量索引加速消费；读写分离互不干扰；通过读写队列分离支持动态缩容。

---

### 3. 对比 RocketMQ 同步刷盘和异步刷盘的差异，以及如何选择。

**答案：**

| 维度 | 同步刷盘 | 异步刷盘 |
|------|----------|----------|
| 原理 | 消息写入 Page Cache 后立即调用 fsync 强制刷盘 | 消息写入 Page Cache 后立即返回，后台线程定期刷盘（默认 500ms） |
| 可靠性 | 极高，Broker 宕机不丢消息 | 可能丢失最近 500ms 内的消息 |
| 吞吐量 | 较低（TPS 约 5k-10k） | 高（TPS 可达 10w+） |
| 延迟 | ms 级 | us 级 |

**选择建议：** 金融支付等不可丢消息的场景选择同步刷盘；日志收集等允许少量丢失的场景选择异步刷盘。大多数业务场景推荐"异步刷盘 + 同步复制"的折中方案，兼顾可靠性和性能。

---

### 4. 简述 RocketMQ 事务消息的三阶段流程。

**答案：**

事务消息通过三阶段保证分布式事务的最终一致性：

**第一阶段（发送半消息）**：Producer 向 Broker 发送半消息（Half Message），Broker 存储后返回确认，但半消息尚未被构建到 ConsumeQueue，消费者不可见。

**第二阶段（执行本地事务）**：Producer 执行本地事务（如创建订单、扣减库存），执行成功返回 Commit，失败返回 Rollback。Commit 后 Broker 将半消息构建到 ConsumeQueue 变为可消费，Rollback 后 Broker 删除半消息。

**第三阶段（消息回查）**：当 Broker 未收到 Commit 或 Rollback 时（如 Producer 宕机），Broker 定时向 Producer 发起回查（Check）。Producer 的 checkLocalTransaction 方法根据本地事务状态返回最终结果。最多回查 15 次。

> **生活化类比：事务消息 = 签收付款** —— 事务消息就像快递的"货到付款"模式。先发半消息（包裹到站但标记"待确认"），再执行本地事务（寄件人办事），成功则 Commit（通知发货），失败则 Rollback（退回销毁）。若快递站迟迟等不到通知，就主动回查（打电话确认），最多问 15 次。

> 📖 **参考链接**：[RocketMQ 事务消息](https://rocketmq.apache.org/docs/feature/transaction-message/) -- 事务消息三阶段流程官方说明

---

### 5. RocketMQ 如何实现顺序消息？消费端如何保证顺序不被破坏？

**答案：**

**发送端保证**：通过 `syncSendOrderly` 和 MessageQueueSelector 按业务 Key（如订单 ID）哈希，将同一业务 Key 的消息发送到固定的 MessageQueue。重试时不会切换队列，保证消息在同一队列内有序。

**消费端保证**：
1. 使用 `ConsumeMode.ORDERLY` 模式，对每个 MessageQueue 加分布式锁
2. 获取锁后，单线程顺序消费该队列的消息
3. 前一条消息返回 CONSUME_SUCCESS 后，才拉取并消费下一条
4. 消费失败时挂起该队列，不跳过失败消息，按延迟等级重试

**Rebalance 期间保证**：当前 Consumer 释放锁，新分配的 Consumer 向 Broker 申请锁，获取锁后从上一个 Consumer 提交的 offset 继续顺序消费。

---

### 6. 简述 RocketMQ 延迟消息的实现原理和 18 个延迟等级。

**答案：**

**实现原理：**
1. 延迟消息写入 CommitLog 时，Topic 被替换为内部 Topic `SCHEDULE_TOPIC_XXXX`，原始 Topic 和 QueueId 存储在消息属性中
2. `ScheduleMessageService` 定时任务按照延迟等级定时扫描到期的延迟消息
3. 到期消息读取原始 Topic 和 QueueId，重新写入目标 Topic 的 CommitLog
4. 消费者随后从目标 Topic 拉取并消费

**18 个延迟等级：** 1s、5s、10s、30s、1m、2m、3m、4m、5m、6m、7m、8m、9m、10m、20m、30m、1h、2h。延迟等级不可自定义，如需自定义需修改 Broker 的 `messageDelayLevel` 配置。延迟精度约 100ms 偏差。

> **生活化类比：延迟消息 = 定时快递** —— 延迟消息就像快递公司的"定时派送"服务，包裹先放在定时区（SCHEDULE_TOPIC_XXXX），按固定档期排列，到点后调度员扫描转入正常派送。快递公司只提供 18 个固定时间档，不能选任意时间。

> 📖 **参考链接**：[RocketMQ 延迟消息](https://rocketmq.apache.org/docs/feature/delay-message/) -- 延迟消息与 18 个延迟等级官方说明

---

### 7. 对比 RocketMQ 三种集群部署模式（多 Master、多 Master 多 Slave、Dledger）的优缺点。

**答案：**

| 维度 | 多 Master | 多 Master 多 Slave | Dledger |
|------|----------|-------------------|---------|
| 可用性 | 低（Master 宕机不可消费） | 高（Slave 可读） | 极高（自动选主） |
| 数据可靠性 | 低（Master 宕机磁盘数据丢失） | 中（异步复制可能丢数据） | 高（Raft 强一致） |
| 故障恢复 | 人工介入 | 人工介入 | 自动（10s 内） |
| 运维复杂度 | 低 | 中 | 中 |
| 适用场景 | 开发测试 | 一般生产环境 | 金融级生产环境 |

**选型建议：** 开发测试用多 Master；一般生产用多 Master 多 Slave；金融支付等对数据一致性要求极高的场景用 Dledger。

---

### 8. RocketMQ 的广播模式和集群模式有什么区别？各适用于什么场景？

**答案：**

| 维度 | 集群模式 | 广播模式 |
|------|----------|----------|
| 消费行为 | 同一 ConsumerGroup 内每条消息只被一个 Consumer 消费 | 同一 ConsumerGroup 内每条消息被所有 Consumer 消费 |
| 消费进度 | 存储在 Broker 端 | 存储在 Consumer 本地 |
| 负载均衡 | 支持 | 不支持 |
| 适用场景 | 订单处理、分布式任务调度 | 配置刷新、缓存更新、通知推送 |

**注意事项：** 广播模式下消费进度存储在 Consumer 本地，重启后可能重复消费，需实现幂等逻辑。广播模式下 Consumer 数量增减不影响其他 Consumer。

---

## 三、场景设计题（3 题，每题附完整解析）

### 1. 设计一个"保证消息不丢失"的 RocketMQ 方案

**场景描述：** 某电商平台订单系统使用 RocketMQ 进行异步解耦，要求订单消息在任何情况下（Broker 宕机、网络抖动、Consumer 宕机）都不能丢失。

**设计方案：**

**1. 生产者端保障：**

```
- 使用同步发送（syncSend）+ 重试机制（retryTimesWhenSendFailed=3）
- 采用本地消息表方案：订单落库和消息发送在同一事务中
  - 消息表字段：messageId、topic、tag、body、status（PENDING/SENT）、retryCount
  - 定时任务扫描 PENDING 状态消息，重新发送
  - 发送成功更新为 SENT，失败递增 retryCount
```

**2. Broker 端保障：**

```
- 刷盘策略：同步刷盘（flushDiskType=SYNC_FLUSH）
- 主从复制：同步复制（brokerRole=SYNC_MASTER）
- 集群模式：Dledger 模式（Raft 强一致，自动故障切换）
- 磁盘保护：配置磁盘使用率告警（diskMaxUsedSpaceRatio=75）
```

**3. 消费者端保障：**

```
- 手动确认模式：消费成功返回 CONSUME_SUCCESS，失败返回 RECONSUME_LATER
- 重试次数：maxReconsumeTimes=5，失败后快速进入死信队列
- 死信处理：监听 %DLQ%{ConsumerGroup}，记录死信消息到数据库，触发告警
- 幂等消费：使用业务唯一 ID（如订单号）去重，Redis 记录已消费的 messageId
```

**4. 监控告警：**

```
- 监控消费 Lag（积压量），设置告警阈值
- 监控死信队列消息数量
- 监控消息发送成功率
- 定时对账：对比订单表和消息表，发现缺失消息补偿
```

**关键技术点：**

| 保障点 | 技术方案 | 说明 |
|--------|----------|------|
| 发送可靠 | 同步发送 + 本地消息表 + 定时补偿 | 三重保障，确保消息一定发送到 Broker |
| 存储可靠 | 同步刷盘 + 同步复制 + Dledger | 消息落盘到多节点后才返回成功 |
| 消费可靠 | 手动确认 + 重试 + 死信兜底 | 消费成功才确认，失败有重试和死信兜底 |
| 幂等消费 | 业务唯一 ID + Redis 去重 | 防止重复消费导致数据异常 |

---

### 2. 设计一个"订单超时取消"系统

**场景描述：** 电商平台用户下单后，如果在 30 分钟内未支付，系统需要自动取消订单并释放库存。要求方案精确可靠，支持高并发。

**设计方案：**

**方案：基于 RocketMQ 延迟消息**

```
1. 用户下单 -> 创建订单（状态：UNPAID）-> 扣减库存
2. 发送延迟消息到 RocketMQ：
   - Topic: order-cancel-topic
   - Tag: cancel
   - delayTimeLevel: 16（30 分钟）
   - Key: orderId（用于幂等和查询）
3. 30 分钟后，延迟消息到期，消费者收到消息
4. 查询订单状态：
   - 仍为 UNPAID -> 取消订单 -> 恢复库存 -> 发送取消通知
   - 已支付（PAID） -> 忽略
   - 已取消（CANCELLED） -> 忽略（幂等保护）
```

**消费者实现：**

```java
@Component
@RocketMQMessageListener(
    topic = "order-cancel-topic",
    consumerGroup = "order-cancel-group",
    selectorExpression = "cancel"
)
public class OrderTimeoutCancelConsumer implements RocketMQListener<MessageExt> {

    @Autowired
    private OrderService orderService;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @Override
    public void onMessage(MessageExt message) {
        String orderId = message.getKeys();
        // 幂等检查：订单是否已处理
        String cacheKey = "order:cancel:processed:" + orderId;
        Boolean processed = redisTemplate.opsForValue()
            .setIfAbsent(cacheKey, "1", Duration.ofHours(1));
        if (Boolean.FALSE.equals(processed)) {
            return; // 已处理，跳过
        }

        try {
            Order order = orderService.findById(orderId);
            if (order != null && order.getStatus() == OrderStatus.UNPAID) {
                // 分布式锁防止并发取消
                String lockKey = "order:cancel:lock:" + orderId;
                Boolean locked = redisTemplate.opsForValue()
                    .setIfAbsent(lockKey, "1", Duration.ofSeconds(30));
                if (Boolean.TRUE.equals(locked)) {
                    try {
                        orderService.cancelOrder(orderId);
                        inventoryService.restore(order.getSkuId(), order.getQuantity());
                    } finally {
                        redisTemplate.delete(lockKey);
                    }
                }
            }
        } catch (Exception e) {
            // 异常触发重试
            throw new RuntimeException("订单取消失败: " + orderId, e);
        }
    }
}
```

**关键技术点：**

| 保障点 | 技术方案 | 说明 |
|--------|----------|------|
| 幂等性 | Redis 记录已处理订单 ID + 订单状态判断 | 防止重复消费和重复取消 |
| 并发控制 | Redis 分布式锁 | 多消费者同时处理同一订单时加锁 |
| 精确性 | 延迟等级 16（30 分钟） | 下单 30 分钟后精确触发取消检查 |
| 可靠性 | 消费失败触发重试 | 重试 5 次，失败进入死信队列 |

**方案对比：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| RocketMQ 延迟消息 | 精确触发，资源消耗低，原生支持 | 延迟等级固定，不可自定义 |
| 定时任务扫描 | 实现简单，可自定义扫描间隔 | 数据库压力大，有扫描延迟 |
| Redis 过期回调 | 精确触发 | Redis 回调不可靠，可能丢失 |

---

### 3. 设计一个"顺序消费"方案

**场景描述：** 某金融系统需要处理账户的转账流水，要求同一账户的流水严格按时间顺序处理（先转入后转出不能颠倒），防止出现账户余额计算错误。

**设计方案：**

**1. 整体架构：**

```
转账服务 -> RocketMQ（顺序消息） -> 流水处理服务 -> 账户余额计算
```

**2. 发送端设计：**

```java
@Service
public class TransferProducer {

    @Autowired
    private RocketMQTemplate rocketMQTemplate;

    public void sendTransferMessage(TransferEvent event) {
        // 按账户 ID 哈希，同一账户的流水发往同一 MessageQueue
        SendResult result = rocketMQTemplate.syncSendOrderly(
            "transfer-topic:event",
            MessageBuilder.withPayload(event)
                .setHeader("accountId", event.getAccountId())
                .setHeader("eventId", event.getEventId())
                .setHeader("timestamp", event.getTimestamp())
                .build(),
            event.getAccountId()  // 哈希键：同一账户到同一队列
        );
        if (result.getSendStatus() != SendStatus.SEND_OK) {
            // 发送失败，记录到本地消息表，由定时任务重试
            saveToMessageLog(event);
        }
    }
}
```

**3. 消费端设计：**

```java
@Slf4j
@Component
@RocketMQMessageListener(
    topic = "transfer-topic",
    consumerGroup = "transfer-process-group",
    consumeMode = ConsumeMode.ORDERLY,  // 顺序消费
    consumeThreadMax = 20  // 每个队列一个线程，20 个队列对应 20 个线程
)
public class TransferConsumer implements RocketMQListener<TransferEvent> {

    @Autowired
    private AccountBalanceService balanceService;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @Override
    public void onMessage(TransferEvent event) {
        // 幂等检查
        String eventKey = "transfer:processed:" + event.getEventId();
        if (redisTemplate.hasKey(eventKey)) {
            return; // 已处理
        }

        try {
            // 处理流水：更新账户余额
            balanceService.processTransfer(event);
            // 标记已处理
            redisTemplate.opsForValue()
                .set(eventKey, "1", Duration.ofDays(7));
        } catch (Exception e) {
            // 失败触发重试，挂起当前队列，不跳过
            log.error("流水处理失败: {}", event.getEventId(), e);
            throw new RuntimeException(e);
        }
    }
}
```

**4. 关键设计点：**

| 设计点 | 方案 | 说明 |
|--------|------|------|
| 分区策略 | 按账户 ID 哈希 | 同一账户的所有流水进入同一 MessageQueue |
| 发送方式 | syncSendOrderly | 同步顺序发送，失败重试不切换队列 |
| 消费模式 | ConsumeMode.ORDERLY | 单线程顺序消费，前一条成功才处理下一条 |
| 幂等保证 | Redis 记录已处理 eventId | 防止重试或重复消费导致余额重复计算 |
| 失败处理 | 挂起重试不跳过 | 某条流水失败，阻塞后续同一账户流水，保证顺序 |
| 监控告警 | 消费 Lag 告警 + 死信告警 | 及时发现积压和异常 |

**5. 并发度与顺序的权衡：**

```
MessageQueue 数量 = 20
-> 最多 20 个账户的流水可以同时被处理
-> 同一账户的流水在同一个 MessageQueue 内串行处理
-> 不同账户的流水在不同 MessageQueue 间并行处理
-> 吞吐量 = 单队列吞吐 * 20
```

**6. 风险与应对：**

| 风险 | 应对措施 |
|------|----------|
| 某账户流水处理慢导致积压 | 设置单条消息处理超时，监控慢消费告警；将耗时逻辑异步化 |
| 消费失败导致该账户所有流水阻塞 | 设置合理的重试次数（3-5 次），快速进入死信队列；死信消息人工处理 |
| Rebalance 期间短暂不可用 | 使用锁机制，Rebalance 完成后新消费者获取锁继续消费 |

> 📖 **参考链接**：
> - [RocketMQ 顺序消息](https://rocketmq.apache.org/docs/feature/order-message/) -- 顺序消息实现原理官方说明
> - [RocketMQ 最佳实践](https://rocketmq.apache.org/docs/best-practice/) -- 生产环境配置与运维最佳实践

---

> **学习导航**：
> - 返回 [学习路线总览](../../../README.md)
> - 本模块其他文件：[01-RocketMQ核心原理](./01-RocketMQ核心原理.md) | [02-RocketMQ高级特性](./02-RocketMQ高级特性.md)