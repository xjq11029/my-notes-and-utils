# RabbitMQ 笔面试题集

> 模块：04-message-queue（第4周 消息队列）
> 覆盖：RabbitMQ 核心原理、可靠性投递、死信与延迟队列、高可用与运维治理
> 题量：12 道选择题 + 8 道简答题 + 3 道场景设计题

> 📖 **参考链接**：
> - [RabbitMQ Documentation](https://www.rabbitmq.com/docs/) -- RabbitMQ 官方文档总入口
> - [AMQP 0-9-1 协议模型](https://www.rabbitmq.com/tutorials/amqp-concepts) -- AMQP 协议与核心概念官方教程

---

## 一、选择题（12 题，每题附解析）

### 1. ★ RabbitMQ 中 Exchange 与 Queue 之间的路由规则由什么定义？（ ）

A. Routing Key
B. Binding
C. Virtual Host
D. Consumer Tag

**答案：B**

**解析：** Binding（绑定）定义 Exchange 与 Queue 之间的路由规则，包括 Binding Key 以及可选的绑定参数。生产者发送消息时携带 Routing Key，Exchange 根据自身类型和所有 Binding 的匹配结果决定把消息投递到哪些 Queue。Routing Key 是消息属性，Virtual Host 是逻辑隔离单元，Consumer Tag 标识消费者。

---

### 2. ★★ Topic Exchange 中，Binding Key 为 `order.#` 时，以下哪个 Routing Key 不能被匹配？（ ）

A. `order.create`
B. `order.cn.pay`
C. `order`
D. `order.ship`

**答案：C**

**解析：** Topic Exchange 中 `*` 匹配一个词，`#` 匹配零个或多个词。`order.#` 要求以 `order` 开头并紧跟一个 `.`，可匹配 `order.create`、`order.cn.pay`、`order.ship` 等；但 `order` 本身没有后续的词和分隔符，因此不匹配。若希望匹配 `order` 本身，Binding Key 应写成 `order.#` 之外的 `order` 或 `#.order`（视语义而定）。

---

### 3. ★★ 生产者发送消息后，消息无法路由到任何队列，此时设置 mandatory=true 的效果是（ ）

A. 消息被自动重试
B. 触发 Basic.Return 回调，生产者可感知并处理
C. Broker 自动创建队列
D. 消息被写入死信队列

**答案：B**

**解析：** mandatory=true 时，若消息无法路由到任何队列，Broker 会通过 Basic.Return 把消息退回生产者，Spring AMQP 中对应 setReturnsCallback 回调。若 mandatory=false（默认），无法路由的消息会被静默丢弃且生产者无感知。死信队列处理的是"已入队但无法正常消费"的消息，与路由失败是两回事。

> 📖 **参考链接**：[RabbitMQ 消息可靠性](https://www.rabbitmq.com/docs/confirms) -- Publisher Confirm 与 Return 回调官方说明

---

### 4. ★★ 关于 Quorum Queue 与镜像队列（Mirrored Queue），描述正确的是（ ）

A. Quorum Queue 基于 Raft 协议，副本间强一致，写入需多数派确认
B. Quorum Queue 使用内存存储，性能高于镜像队列
C. 镜像队列支持负载均衡，读写可分散到各 Mirror 节点
D. 镜像队列基于 Raft 协议，不会出现脑裂

**答案：A**

**解析：** Quorum Queue 基于 Raft 一致性协议，队列数据在多个节点间强一致复制，写入需多数派确认，避免了镜像队列的脑裂风险，但吞吐低于经典队列。镜像队列中所有读写都经过 Master 节点，不提供负载均衡；且镜像队列使用旧同步算法，网络分区时可能出现脑裂与消息丢失。

---

### 5. ★★ 在 RabbitMQ 中，保证单个队列内消息顺序性的正确做法是（ ）

A. 使用多个消费者并行消费同一队列
B. 单队列 + 单消费者 + prefetch=1 + 手动 ack
C. 使用 Fanout Exchange 广播
D. 设置消息优先级

**答案：B**

**解析：** RabbitMQ 只保证单队列内 FIFO，但多个消费者竞争同一队列会因处理速度不同导致乱序。要保证顺序，需单队列 + 单消费者 + prefetch=1（一次只投递一条）+ 手动 ack（处理成功再确认下一条）。C、D 与顺序性无关，A 反而会破坏顺序。

---

### 6. ★★★ 队列配置了 `x-max-length` 且 `x-overflow=reject-publish-dlx`，当队列已满时新消息会（ ）

A. 覆盖最旧的消息
B. 被拒绝并进入死信队列
C. 在 Broker 内存中排队等待
D. 被静默丢弃

**答案：B**

**解析：** x-overflow 支持三种取值：`drop-head`（默认，丢弃队头最旧消息）、`reject-publish`（拒收新消息并给生产者返回 nack）、`reject-publish-dlx`（拒收新消息并投递到死信交换机）。A 是 drop-head 的行为，D 是未配置 overflow 且无死信交换机时的表现。

---

### 7. ★★ Spring AMQP 中 `publisher-confirm-type=correlated` 相比 `simple` 的优势是（ ）

A. 性能更高
B. 可通过 CorrelationData 精确定位哪条消息确认失败，便于重发
C. 无需配置回调
D. 支持自动创建队列

**答案：B**

**解析：** correlated 模式下生产者发送时携带 CorrelationData（通常含消息唯一 ID），Confirm 回调中可以取出该数据定位具体失败的消息，便于落库重试。simple 模式只提供全局确认开关，无法精确关联到具体消息。correlated 并不会带来更高性能，也不会免除回调配置。

---

### 8. ★★★ `channel.basicQos(prefetchCount)` 的作用是（ ）

A. 限制 Broker 同时推送给该消费者的未确认消息数量
B. 限制队列最大长度
C. 设置消息 TTL
D. 限制生产者发送速率

**答案：A**

**解析：** basicQos（prefetch）限制消费者端未确认消息的最大数量，Broker 只有在未确认数低于 prefetch 时才继续推送，从而实现公平分发，避免某个消费者被压垮。prefetch=1 表示处理完一条并 ack 后才投递下一条。它与队列长度、TTL、生产者限流无关。

---

### 9. ★★ 消息进入死信队列后，`x-death` 头信息中不包含（ ）

A. 死信原因（如 expired、rejected、maxlen）
B. 原队列名称
C. 消息的原始内容
D. 消息被死信的次数（count）

**答案：C**

**解析：** x-death 是 Broker 自动附加的数组型头信息，记录死信原因（reason）、原队列（queue）、原交换机（exchange）、路由键、时间戳和次数（count）。消息原始内容保存在消息体中，不在 x-death 里。x-death 是排查"消息为什么进死信"的关键线索。

---

### 10. ★★ Headers Exchange 中 `x-match=all` 的含义是（ ）

A. 只要有一个 Header 匹配就投递
B. 消息的所有指定 Header 都必须匹配才投递
C. 忽略 Header，广播到所有队列
D. 按 Routing Key 精确匹配

**答案：B**

**解析：** Headers Exchange 忽略 Routing Key，根据消息 Header 属性匹配。`x-match=all` 要求 Binding 中声明的所有 Header 都匹配才投递，`x-match=any` 只需其中一个匹配。C 是 Fanout 的行为，D 是 Direct 的行为。

---

### 11. ★★★ 消费者收到消息后尚未 ack 就宕机，RabbitMQ 会（ ）

A. 消息直接丢失
B. 消息重新入队，可能被其他消费者消费，且 redelivered 标记为 true
C. 消息立即进入死信队列
D. Broker 等待该消费者恢复后原样投递

**答案：B**

**解析：** 未确认的消息在消费者连接断开后会被重新入队（requeue），投递给其他消费者或原消费者重连后消费，消息的 redelivered 标记置为 true。这体现了"至少一次"投递语义，也意味着消费端必须实现幂等。只有在消费者显式 basic.nack/reject 且 requeue=false，或 TTL 过期、队列超限时才会进入死信队列。

---

### 12. ★★ RabbitMQ 3.12 起，经典队列的默认消息存储模式是（ ）

A. 内存优先，磁盘仅作备份
B. 磁盘优先（惰性队列行为），消息直接写入磁盘文件
C. 仅内存，不落盘
D. 由客户端逐条指定

**答案：B**

**解析：** RabbitMQ 3.10 引入惰性队列（Lazy Queue），3.12 起成为默认模式，经典队列默认采用磁盘优先存储，消息到达即写入磁盘文件，内存仅作缓存。这样在百万级消息堆积时内存占用稳定，避免 OOM，代价是消费吞吐降低约 30%-50%。

---

## 二、简答题（8 题，每题附完整解析）

### 1. 简述 RabbitMQ 四种 Exchange 类型的路由机制与适用场景。

**答案：**

| 类型 | 路由逻辑 | 匹配示例 | 适用场景 |
|------|----------|----------|----------|
| **Direct** | Routing Key 与 Binding Key 精确相等 | `error` → `error` | 单播、按日志级别分发 |
| **Topic** | Binding Key 支持通配符：`*` 匹配一个词，`#` 匹配零个或多个词 | `order.*.pay` 匹配 `order.cn.pay` | 多条件路由，按地域+业务分类 |
| **Fanout** | 忽略 Routing Key，广播到所有绑定队列 | 所有绑定队列都收到 | 配置变更通知、缓存刷新广播 |
| **Headers** | 按消息 Header 属性匹配，忽略 Routing Key；`x-match=all/any` | `type=log AND level=error` | 复杂属性路由，Routing Key 不便表达时 |

**Topic 通配符要点：**

```
Binding Key: order.#   → 匹配 order.create、order.cn.pay、order.ship
Binding Key: order.*.pay → 匹配 order.cn.pay、order.us.pay
                        不匹配 order.pay、order.cn.ship
```

**选型建议：** 能用 Direct 就不用 Topic（性能更好、更易维护）；需要广播用 Fanout；Headers 因性能较差且可读性低，实际使用较少。

---

### 2. RabbitMQ 如何保证消息不丢失？请从生产者、Broker、消费者三个环节说明全链路方案。

**答案：**

**1. 生产者端（确保消息到达 Broker）：**

- 开启 Publisher Confirm：`publisher-confirm-type=correlated`，Broker 返回 ack/nack，未确认的消息落库重试
- 开启 Publisher Return：`publisher-returns=true` + `mandatory=true`，处理无法路由的消息
- 使用本地消息表：业务落库与消息记录同一事务，定时任务扫描未确认消息重发

**2. Broker 端（确保消息落盘与高可用）：**

- 队列持久化：`QueueBuilder.durable()`
- 消息持久化：`deliveryMode=2`
- Exchange 持久化：`ExchangeBuilder.durable()`
- 三者缺一不可，只设消息持久化而队列非持久化，Broker 重启后队列消失消息仍会丢
- 高可用：使用 Quorum Queue（Raft 多数派确认）或镜像队列

**3. 消费者端（确保消息被正确处理）：**

- 使用手动确认：`acknowledge-mode=manual`，处理成功调用 `basicAck`
- 处理失败调用 `basicNack` 且根据场景决定是否 requeue；重试达上限后进死信队列
- 消费端实现幂等，应对"至少一次"语义下的重复投递
- 合理设置 prefetch（10-50），避免一次拉取过多消息，宕机后大量重投

**完整链路对照：**

| 环节 | 风险 | 保障手段 |
|------|------|----------|
| 生产者 → Broker | 网络中断、路由失败 | Confirm + Return + 本地消息表 |
| Broker 存储 | 宕机、磁盘故障 | 三重持久化 + Quorum Queue |
| Broker → 消费者 | 消费失败、消费者宕机 | 手动 ack + 重试 + 死信队列 + 幂等 |

> **生活化类比：可靠性投递 = 寄挂号信** —— 生产者 Confirm 像寄挂号信后收到邮局回执，确认信已收寄；Return 像地址写错被退回，你能收到退件；Broker 持久化像邮局把信件入库上架；消费者手动 ack 像收件人签收后才算送达。任何一环没回执，都说明这封信可能丢了，需要补寄。

---

### 3. 简述 RabbitMQ 死信队列的实现原理与常见使用场景。

**答案：**

**消息成为死信的三种情况：**

1. **消息 TTL 过期**：消息在队列中存活时间超过 x-message-ttl
2. **队列达到最大长度**：超过 x-max-length 且 x-overflow=reject-publish 或 reject-publish-dlx
3. **消费拒绝**：消费者调用 basic.nack / basic.reject 且 requeue=false

**实现原理：**

```
业务队列声明时指定：
  x-dead-letter-exchange    → 死信转发到的交换机
  x-dead-letter-routing-key → 死信转发时使用的路由键（不指定则沿用原路由键）
消息成为死信 → Broker 自动转发到死信交换机 → 路由到死信队列
死信消息头自动附加 x-death，记录 reason/queue/exchange/count
```

**配置示例：**

```java
@Bean
public Queue businessQueue() {
    return QueueBuilder.durable("business.order.queue")
        .deadLetterExchange("dead.letter.exchange")
        .deadLetterRoutingKey("dead.order")
        .ttl(30000)              // 消息 TTL 30 秒
        .maxLength(10000)        // 队列最大长度
        .build();
}
```

**常见使用场景：**

| 场景 | 说明 |
|------|------|
| 消息重试 | 消费失败的消息进死信队列，定时任务按退避策略重新投递 |
| 延迟队列 | TTL + DLX 组合实现延迟消息（订单超时取消） |
| 异常消息分析 | 收集无法消费的消息，记录 x-death 原因，人工排查修复 |
| 流量削峰 | 队列满时多余消息进死信队列，后台异步处理 |

**注意事项：** 死信队列必须配置消费者并监控堆积量，否则死信会无限堆积直至磁盘写满；死信消费者处理失败时也应确认消息避免死循环。

---

### 4. RabbitMQ 延迟队列有哪两种实现方式？各自有什么坑？

**答案：**

**方案一：TTL + DLX 组合**

```
消息发送到普通队列（设置 TTL）
  → TTL 到期消息过期
  → 自动转发到死信交换机 / 死信队列
  → 消费者监听死信队列，实现延迟消费
```

**坑点：**

1. **队头阻塞**：RabbitMQ 只检查队头消息是否过期。若队列级 TTL 统一，问题不大；若使用消息级 TTL 且先入队的消息 TTL 长、后入队的 TTL 短，则后入队的短 TTL 消息必须等队头消息过期后才能被处理，实际延迟时间被拉长
2. **只能近似延迟**：延迟精度受 Broker 扫描和消费速度影响
3. **拓扑复杂**：每个延迟时长可能需要独立队列，维护成本高

**方案二：rabbitmq-delayed-message-exchange 插件**

```java
Map<String, Object> args = new HashMap<>();
args.put("x-delayed-type", "direct");
new CustomExchange("delayed.exchange", "x-delayed-message", true, false, args);

// 发送时指定延迟毫秒数
msg.getMessageProperties().setDelay(30 * 60 * 1000);
```

**优点：** 支持任意延迟时间，无队头阻塞；**缺点：** 需额外安装维护插件，延迟消息存储在 Erlang Mnesia 中，大量延迟消息占用内存，节点故障时可能丢失，且延迟精度仍有限。

**两种方案对比：**

| 维度 | TTL + DLX | 延迟插件 |
|------|-----------|----------|
| 延迟时间 | 受队列/消息 TTL 限制，有队头阻塞 | 任意延迟，无队头阻塞 |
| 运维成本 | 低，无需插件 | 需安装维护插件 |
| 可靠性 | 消息在普通队列中，可持久化 | 依赖插件存储，节点故障风险较高 |
| 适用场景 | 固定几档延迟、延迟时间较短 | 延迟时间灵活多变 |

**替代思路：** 若延迟场景要求精确且量级较大，建议改用 RocketMQ 延迟消息（18 个固定等级）或"定时任务扫描 + 数据库"方案，避免在 RabbitMQ 上过度设计。

> 📖 **参考链接**：
> - [RabbitMQ 死信队列](https://www.rabbitmq.com/docs/dlx) -- 死信交换机（DLX）官方说明
> - [RabbitMQ 延迟消息插件](https://www.rabbitmq.com/docs/deferred-message-exchange) -- delayed-message-exchange 插件官方文档

---

### 5. RabbitMQ 如何保证消息顺序性？为什么说顺序和吞吐难以兼得？

**答案：**

**保证顺序的三个条件：**

1. **单队列**：同一业务 Key 的消息必须路由到同一队列（用 Direct/Topic Exchange 按业务 Key 绑定，而不是 Fanout 广播或多队列轮询）
2. **单消费者**：一个队列只由一个消费者消费。多个消费者并行消费同一队列时，处理速度不同会导致后到的消息先处理完
3. **prefetch=1 + 手动 ack**：一次只投递一条，处理成功 ack 后才投递下一条

```java
// 保证顺序的消费者配置
channel.basicQos(1);   // 一次只投递一条
// autoAck=false，处理成功后 basicAck
```

**为什么顺序与吞吐难以兼得：**

| 维度 | 顺序优先 | 吞吐优先 |
|------|----------|----------|
| 队列数 | 单队列 | 多队列分片 |
| 消费者数 | 1 | 多消费者竞争消费 |
| prefetch | 1 | 10-50 或更大 |
| 消费失败 | 阻塞该队列后续消息 | 仅影响当前消息 |
| 吞吐量 | 低 | 高 |

**实践建议：**

1. 优先设计为幂等消费，不依赖消息顺序，从根上规避问题
2. 确实需要顺序时，按业务 Key 分片到多个队列，每个队列单消费者，实现"局部有序 + 全局并行"
3. 消费失败时不要无限 requeue（会阻塞队列），设置重试上限后转死信队列，避免顺序消息被单条异常消息拖死

---

### 6. 什么是幂等消费？RabbitMQ 场景下有哪些常见的幂等实现方案？

**答案：**

**为什么需要幂等：** RabbitMQ 提供"至少一次"（at-least-once）投递语义——消费者未 ack 就宕机、网络抖动导致 ack 丢失、手动重试等情况都会造成消息重复投递。因此消费端必须保证同一消息被处理多次与处理一次的结果一致。

**常见实现方案：**

| 方案 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| 业务唯一 ID + 数据库唯一索引 | 以消息业务 ID 建唯一索引，重复插入触发约束冲突 | 简单可靠，数据库层兜底 | 仅适用于插入场景 |
| Redis 去重表 | 处理前 `setIfAbsent(msgId, 1, TTL)`，返回 false 则跳过 | 性能高，适合高并发 | 需考虑 Redis 不可用与过期时间 |
| 状态机 + 版本号 | 业务状态只能单向流转，判断当前状态是否允许本次操作 | 语义清晰，可防止乱序覆盖 | 需业务设计状态机 |
| 数据库乐观锁 | `UPDATE ... WHERE version = ?`，影响行数为 0 则跳过 | 无额外组件 | 需为每张表加版本字段 |

**关键实践：**

1. **幂等键的选择**：优先使用业务唯一 ID（订单号、支付流水号），而非消息 ID，因为重发时消息 ID 会变化
2. **幂等窗口**：Redis 去重的 TTL 需大于消息可能重投的最大时间窗口
3. **ack 时机**：幂等校验通过并处理成功后再 ack，避免处理失败但已 ack 导致消息丢失
4. **与死信配合**：幂等命中（说明已处理）时直接 ack，不要抛异常触发重试

> **生活化类比：幂等消费 = 快递签收登记** —— 同一个包裹（消息）可能因为快递员没收到签收回执（ack 丢失）而被重复派送。收件人（消费者）只要在登记本上按运单号（业务唯一 ID）查一下，已签收过的就不再重复入库，这样就避免了"一份包裹记两笔账"。

---

### 7. 镜像队列（Mirrored Queue）与 Quorum Queue 有什么区别？如何选择？

**答案：**

| 维度 | 镜像队列（Mirrored Queue） | Quorum Queue |
|------|---------------------------|--------------|
| 一致性协议 | 自研主从同步（无一致性协议保证） | Raft 协议，多数派确认 |
| 数据安全 | 网络分区时可能脑裂，切换时可能丢消息 | 强一致，多数派写入成功才确认 |
| 读写路径 | 所有读写都经 Master，Mirror 仅同步 | Leader 处理读写，Follower 同步 |
| 负载均衡 | 不支持 | 不支持 |
| 性能 | 同步开销较大，但仍高于 Quorum Queue | 吞吐较低（需多数派落盘） |
| 节点要求 | 任意节点数 | 至少 3 个节点（建议奇数） |
| 队列特性 | 支持全部特性（优先级、TTL 等） | 不支持部分特性（如优先级队列、消息 TTL 有限制） |
| 官方定位 | 已被 Quorum Queue 取代，不再推荐 | 官方推荐的持久化队列高可用方案 |

**选型建议：**

- **新项目、要求数据不丢**：优先选 Quorum Queue，配置 `default_queue_type = quorum`
- **需要优先级队列、消息级 TTL 等经典特性**：使用经典队列，必要时配镜像队列
- **临时队列、自动删除队列、低延迟场景**：使用经典队列（非持久化）
- 集群节点数需 ≥ 3，且跨机架/可用区分布，否则 Quorum Queue 无法发挥多数派优势

**迁移注意：** 经典队列不能原地转换为 Quorum Queue，需新建队列并迁移消费，迁移期间注意双写或灰度切换。

---

### 8. RabbitMQ 出现消息积压应如何处理？与 Kafka 的积压处理有何不同？

**答案：**

**RabbitMQ 积压的排查与处理：**

1. **定位**：通过管理台或 `rabbitmqctl list_queues name messages consumers` 查看队列深度、消费者数量、消息入队/出队速率
2. **扩容消费者**：RabbitMQ 队列没有分区概念，增加消费者即可提升并行度（同一队列多消费者竞争消费），但会破坏顺序性
3. **调大 prefetch**：适度提高 prefetch 让消费者一次拿更多消息，提升吞吐（但宕机后重投量增加）
4. **优化消费逻辑**：耗时操作异步化、批量处理、减少外部调用
5. **转存到新队列**：积压极严重时，启动临时消费者把消息快速转存到新队列，再并行消费，避免影响原队列
6. **清理或丢弃**：确认业务可容忍时，通过管理台 purge 队列或设置 TTL 让消息过期
7. **启用惰性队列**：大量积压时切到磁盘优先模式，避免内存 OOM

**与 Kafka 的差异：**

| 维度 | RabbitMQ | Kafka |
|------|----------|-------|
| 并行度上限 | 无硬性分区限制，加消费者即可（但破坏顺序） | 消费者数 ≤ Partition 数 |
| 扩容手段 | 增加消费者、提高 prefetch、转存新队列 | 增加消费者、增加 Partition、转存新 Topic |
| 消息保留 | 消费后删除，积压消息只能消费一次 | 按 offset 保留，可重置位移重放 |
| 丢弃方式 | purge 队列、TTL 过期 | 重置 offset 到 latest、删除重建 Topic |
| 积压代价 | 消息占内存/磁盘，易 OOM（惰性队列缓解） | 受磁盘限制，几乎无内存压力 |
| 顺序影响 | 加消费者会破坏顺序 | 加消费者不影响分区内顺序 |

**共性原则：** 先止血（扩容并行度）→ 再治本（优化消费逻辑）→ 最后兜底（转存或丢弃），并配套队列深度告警。

> 📖 **参考链接**：[RabbitMQ 运维与监控](https://www.rabbitmq.com/docs/monitoring) -- 队列深度、消费者数量等监控指标官方说明

---

## 三、场景设计题（3 题，每题附完整解析）

### 1. 设计一个"RabbitMQ 可靠性投递"全链路方案

**场景描述：** 某支付系统使用 RabbitMQ 传递支付结果通知，要求消息在生产者宕机、Broker 重启、消费者宕机等任何情况下都不丢失、不重复处理。

**设计方案：**

**1. 生产者端：Confirm + Return + 本地消息表**

```yaml
spring:
  rabbitmq:
    publisher-confirm-type: correlated   # 异步确认，可关联 CorrelationData
    publisher-returns: true              # 开启 Return 回调
    template:
      mandatory: true                    # 无法路由时退回
```

```java
rabbitTemplate.setConfirmCallback((correlationData, ack, cause) -> {
    if (!ack) {
        // 落库待重发，correlationData 中携带业务唯一 ID
        messageRetryRepository.save(correlationData.getId(), cause);
    }
});
rabbitTemplate.setReturnsCallback(returned -> {
    // 路由失败：记录 exchange、routingKey、消息体，人工介入
    log.error("消息无法路由: {} / {}", returned.getExchange(), returned.getRoutingKey());
});
```

```
本地消息表流程：
1. 支付结果落库 + 写入消息表（同一数据库事务，状态 PENDING）
2. 事务提交后发送消息到 RabbitMQ
3. 收到 Confirm ack 后更新消息表状态为 SENT
4. 定时任务扫描超时仍为 PENDING 的记录重新发送（重发需业务幂等）
```

**2. Broker 端：三重持久化 + 高可用**

```
- Exchange 持久化：durable=true
- Queue 持久化：durable=true
- 消息持久化：deliveryMode=2
- 高可用：关键队列使用 Quorum Queue（default_queue_type=quorum）
- 磁盘水位告警：disk_free_limit 触发时 Broker 会阻塞生产者，需提前扩容
```

**3. 消费者端：手动 ack + 重试 + 死信兜底 + 幂等**

```java
@RabbitListener(queues = "payment.result.queue")
public void onMessage(PaymentResult result, Message message, Channel channel) throws IOException {
    long tag = message.getMessageProperties().getDeliveryTag();
    String idempotentKey = "pay:result:" + result.getPayNo();
    try {
        // 1. 幂等校验
        if (!redisTemplate.opsForValue().setIfAbsent(idempotentKey, "1", Duration.ofDays(7))) {
            channel.basicAck(tag, false);   // 已处理过，直接确认
            return;
        }
        // 2. 业务处理
        paymentService.handleResult(result);
        // 3. 处理成功再确认
        channel.basicAck(tag, false);
    } catch (Exception e) {
        // 4. 重试达上限则进死信队列，未达上限则重新入队
        int retry = getRetryCount(message);
        if (retry >= 3) {
            channel.basicNack(tag, false, false);  // requeue=false → 死信队列
        } else {
            channel.basicNack(tag, false, true);   // 重新入队
        }
    }
}
```

**关键技术点：**

| 环节 | 技术方案 | 说明 |
|------|----------|------|
| 发送可靠 | Confirm + Return + 本地消息表 | 三重保障，未确认消息可重发 |
| 存储可靠 | 三重持久化 + Quorum Queue | 消息落盘且多数派确认 |
| 消费可靠 | 手动 ack + 重试 + 死信兜底 | 处理成功才确认，失败有重试与死信 |
| 幂等消费 | Redis 业务唯一 ID 去重 | 防止重复投递导致重复处理 |
| 监控告警 | 队列深度 + 死信队列 + 未确认消息数 | 及时发现积压与死信堆积 |

**风险与应对：**

| 风险 | 应对措施 |
|------|----------|
| 重发导致消息重复 | 消费端幂等；重发时保持业务唯一 ID 不变 |
| requeue 导致死循环 | 记录重试次数，达上限后 requeue=false 进死信 |
| 死信队列无人消费 | 死信队列必须有消费者 + 堆积告警 |
| Broker 磁盘写满阻塞生产者 | 配置磁盘水位告警；启用惰性队列降低内存压力 |

---

### 2. 设计一个"基于 RabbitMQ 的订单超时取消"系统

**场景描述：** 电商平台用户下单后，若 30 分钟内未支付，系统需自动取消订单并释放库存，要求触发精确、不重复取消。

**设计方案：**

**方案一：TTL + DLX 组合（无插件，推荐用于固定延迟档位）**

```
拓扑设计：
1. 延迟交换机 delay.exchange (Direct)
2. 延迟等待队列 delay.wait.queue（30 分钟档）
   - x-message-ttl = 1800000
   - x-dead-letter-exchange = delay.process.exchange
   - x-dead-letter-routing-key = order.cancel
3. 处理交换机 delay.process.exchange (Direct)
4. 处理队列 order.cancel.queue，绑定路由键 order.cancel
5. 消费者监听 order.cancel.queue

流程：
下单 → 创建订单(UNPAID) → 扣减库存
     → 发送消息到 delay.exchange，路由键 order.wait
     → 消息在 delay.wait.queue 中等待 30 分钟
     → TTL 到期 → 转发到 order.cancel.queue
     → 消费者查询订单状态：
         UNPAID  → 取消订单 + 恢复库存 + 发通知
         PAID    → 忽略
         CANCELLED → 忽略（幂等）
```

**关键：不同延迟档位使用独立队列**（如 15 分钟、30 分钟、1 小时各一个队列），避免消息级 TTL 导致的队头阻塞。

**方案二：延迟插件（需要任意延迟时间时）**

```java
Map<String, Object> args = new HashMap<>();
args.put("x-delayed-type", "direct");
new CustomExchange("order.delayed.exchange", "x-delayed-message", true, false, args);

rabbitTemplate.convertAndSend("order.delayed.exchange", "order.cancel",
    orderId, msg -> {
        msg.getMessageProperties().setDelay(30 * 60 * 1000);
        return msg;
    });
```

**消费者幂等与并发控制：**

```java
@RabbitListener(queues = "order.cancel.queue")
public void checkOrder(Long orderId, Message message, Channel channel) throws IOException {
    long tag = message.getMessageProperties().getDeliveryTag();
    try {
        // 幂等：同一订单只处理一次
        if (!redisTemplate.opsForValue().setIfAbsent("order:cancel:" + orderId, "1",
                Duration.ofHours(1))) {
            channel.basicAck(tag, false);
            return;
        }
        Order order = orderService.findById(orderId);
        if (order != null && order.getStatus() == OrderStatus.UNPAID) {
            orderService.cancelOrder(orderId);       // 内部用状态机/乐观锁保证幂等
            inventoryService.restore(order.getSkuId(), order.getQuantity());
        }
        channel.basicAck(tag, false);
    } catch (Exception e) {
        channel.basicNack(tag, false, true);   // 重试，达上限后转死信
    }
}
```

**方案对比：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| TTL + DLX | 无需插件、消息可持久化、运维简单 | 档位固定；消息级 TTL 有队头阻塞 |
| 延迟插件 | 支持任意延迟、无队头阻塞 | 需安装维护；依赖 Mnesia 存储，节点故障风险较高 |
| 定时任务扫描 | 实现最简单、可自定义 | 数据库压力大、有扫描延迟（最多 1 分钟） |
| 改用 RocketMQ 延迟消息 | 原生支持、精确、资源消耗低 | 需引入新中间件，等级固定 |

**关键技术点：**

| 保障点 | 技术方案 | 说明 |
|--------|----------|------|
| 精确触发 | 独立队列对应独立延迟档位 | 避免队头阻塞，30 分钟整触发 |
| 幂等取消 | Redis 去重 + 订单状态机 + 乐观锁 | 防止重复取消与并发取消 |
| 可靠性 | 消息持久化 + 手动 ack + 死信兜底 | 消费失败可重试，最终进死信人工处理 |
| 监控 | 延迟队列深度 + 死信堆积告警 | 及时发现延迟消息积压 |

---

### 3. 设计一个"RabbitMQ 高可用与积压治理"方案

**场景描述：** 某业务系统使用 RabbitMQ 承载订单、通知、日志三类消息，单集群 3 节点。近期出现通知队列积压 200 万条、镜像队列切换后少量消息丢失的问题，需要给出高可用与积压治理方案。

**设计方案：**

**1. 高可用架构改造：**

```
集群规划：3 节点起步（推荐 3 或 5 奇数节点），跨机架/可用区分布
- 关键业务队列（订单、支付）→ Quorum Queue，Raft 多数派确认，数据不丢
- 非关键队列（通知、日志）→ 经典队列 + 惰性模式，优先吞吐与内存安全
- 临时/自动删除队列 → 经典队列（非持久化）
- 设置 default_queue_type = quorum（RabbitMQ 3.12+ 需评估兼容性）
```

**2. 积压治理三级策略：**

```
第一级：扩容消费能力（止血）
- 增加消费者实例（RabbitMQ 无分区限制，可横向加）
- 适度提高 prefetch（如 10 → 50），提升单消费者吞吐
- 注意：多消费者竞争同一队列会破坏顺序性，仅适用于无需顺序的队列

第二级：转存到新队列再消费（消费逻辑本身慢时）
- 创建新队列 notice.queue.retry，绑定新交换机
- 部署临时消费者，只做"拉取-转发"不做业务逻辑，把积压消息快速转存
- 启动大批量业务消费者消费新队列，并行处理
- 转存完成后下线临时消费者，业务切回原队列

第三级：丢弃（业务可容忍时）
- 管理台 purge 队列，或对队列设置消息 TTL 让其自然过期
- 前需确认业务影响并做好数据备份，操作不可逆
```

**3. 惰性队列缓解内存压力：**

```bash
# 对通知、日志类队列批量启用惰性模式
rabbitmqctl set_policy lazy-queue "^(notice|log)\." '{"queue-mode":"lazy"}' --apply-to queues
```

百万级消息堆积时，默认队列内存占用可达数 GB 且面临 OOM，惰性队列内存占用稳定在数百 MB，代价是消费吞吐降低约 30%-50%。

**4. 监控指标与告警阈值：**

| 指标 | 含义 | 建议阈值 |
|------|------|----------|
| 队列深度（messages） | 待消费消息数 | > 10 万告警，> 100 万严重 |
| 消费者数量（consumers） | 队列消费者数 | = 0 立即告警（无人消费） |
| 未确认消息数（messages_unacknowledged） | 已投递未 ack | 持续接近 prefetch × 消费者数时告警 |
| 消息入队/出队速率 | 生产与消费速率 | 入队速率持续大于出队速率告警 |
| 磁盘剩余空间 | Broker 磁盘 | 低于 disk_free_limit 1.5 倍告警 |
| 内存使用率 | Erlang 虚拟机内存 | > 80% 告警 |
| 死信队列深度 | 死信堆积 | > 1000 告警 |
| 节点存活与分区 | 集群状态 | 任一节点不可用或出现网络分区告警 |

**5. 运维规范：**

```
- 队列必须有消费者：上线前检查 consumers > 0，避免"只发不消费"
- 死信队列必须有消费者 + 告警：否则死信无限堆积直至磁盘写满
- 队列长度与 TTL 必须设置：x-max-length + x-message-ttl 双保险
- 定期巡检：队列深度、消费者数、连接数、磁盘水位
- 变更演练：节点故障切换、镜像/Quorum 切换演练，验证不丢消息
```

**关键技术点：**

| 问题 | 根因 | 方案 |
|------|------|------|
| 镜像队列切换丢消息 | 镜像队列无一致性协议保证，脑裂时可能丢数据 | 关键队列改用 Quorum Queue（Raft 多数派确认） |
| 通知队列积压 200 万 | 消费能力不足 + 内存优先存储 | 扩容消费者 + 惰性队列 + 转存新队列 |
| 磁盘写满风险 | 死信与积压消息持续增长 | 设置队列长度上限 + TTL + 死信告警 |
| 无负载均衡 | 镜像/Quorum 队列读写都经 Leader | 通过多队列分片 + 多消费者实现水平扩展 |

> 📖 **参考链接**：
> - [RabbitMQ 高可用](https://www.rabbitmq.com/docs/ha) -- 镜像队列与 Quorum Queue 官方说明
> - [RabbitMQ 运维与监控](https://www.rabbitmq.com/docs/monitoring) -- 队列深度、消费者数与告警官方指南

---

> **学习导航**：
> - 返回 [学习路线总览](../../../README.md)
> - 本模块其他文件：[02-RabbitMQ核心原理](./02-RabbitMQ核心原理.md) | [02-RabbitMQ核心原理导览](./02-RabbitMQ核心原理-导览.md) | [03-消息队列笔面试题集](../03-消息队列笔面试题集.md)
