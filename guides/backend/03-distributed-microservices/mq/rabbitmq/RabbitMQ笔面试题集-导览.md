# RabbitMQ 笔面试题集 导览

> 定位：五维框架浓缩提炼 RabbitMQ笔面试题集.md 全部内容小节，快速查阅与复习。
> 用法：每个题型分类对应一张概要表格，每道题目提取所考知识点对应一张纵向表格，需要深入理解时跳转 [原文](./RabbitMQ笔面试题集.md)。
> 前置知识：[RabbitMQ核心原理](./02-RabbitMQ核心原理-导览.md)

---

## 一、选择题（12 题，每题附解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 从给定选项中选择正确答案的客观题型，本题集共 12 道，覆盖 Exchange 路由、消息确认、死信与延迟、顺序性、高可用与存储模式 |
| 能做什么 | 考查 Binding 定义、Topic 通配符、mandatory 与 Return、Quorum Queue、顺序性三条件、x-overflow、publisher-confirm-type、basicQos、x-death、Headers x-match、未 ack 重入队、3.12 默认存储模式等点状知识 |
| 怎么用 | 阅读题干排除干扰项，结合解析巩固易混淆概念 |
| 原理和工作流程 | 每题聚焦单一知识点，通过选项对比强化辨析。星号标注难度，一星为基础、二星为进阶、三星为深入。覆盖 Exchange 四种类型、Binding、Confirm/Return、prefetch、死信与 x-death、顺序性、Quorum Queue、惰性队列等核心考点 |
| 缺点 | 单题覆盖面窄；选项存在猜测成分；难以考查综合设计与运维能力 |

### 1. ★ RabbitMQ 中 Exchange 与 Queue 之间的路由规则由什么定义？（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Binding 定义 Exchange 与 Queue 之间的路由规则，含 Binding Key 与绑定参数 |
| 能做什么 | 建立交换机和队列的关联；决定 Routing Key 匹配方式；支持多队列绑定同一交换机 |
| 怎么用 | `BindingBuilder.bind(queue).to(exchange).with("order.create")` |
| 原理和工作流程 | 生产者发送消息携带 Routing Key，Exchange 根据自身类型与所有 Binding 的匹配结果决定投递到哪些 Queue。Routing Key 是消息属性，Virtual Host 是逻辑隔离单元，Consumer Tag 标识消费者，均不定义路由规则 |
| 缺点 | Binding 配置分散易遗漏；绑定关系复杂后排查困难；变更需重启或热更新策略 |

### 2. ★★ Topic Exchange 中，Binding Key 为 `order.#` 时，以下哪个 Routing Key 不能被匹配？（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Topic Exchange 的 `*` 匹配一个词、`#` 匹配零个或多个词的通配符规则 |
| 能做什么 | 按多级 Routing Key 灵活路由；实现按地域+业务的多条件分发；通配符组合表达复杂规则 |
| 怎么用 | Binding Key `order.#`；发送时 Routing Key 形如 `order.cn.pay` |
| 原理和工作流程 | `order.#` 要求以 order 开头并紧跟分隔符，可匹配 order.create、order.cn.pay、order.ship；但 order 本身没有后续的词和分隔符，故不匹配。若需匹配 order 本身，应使用 order 或调整通配符写法 |
| 缺点 | 通配符语义易混淆；过度通配导致消息误投；匹配规则比 Direct 更难排查 |

### 3. ★★ 生产者发送消息后，消息无法路由到任何队列，此时设置 mandatory=true 的效果是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | mandatory=true 时无法路由的消息通过 Basic.Return 退回生产者，可被感知处理 |
| 能做什么 | 感知路由失败；把失败消息落库重发；避免消息被静默丢弃 |
| 怎么用 | `mandatory=true` + `setReturnsCallback(...)` |
| 原理和工作流程 | mandatory=true 时 Broker 将无法路由的消息通过 Basic.Return 退回，Spring AMQP 对应 setReturnsCallback。mandatory=false 默认时消息被静默丢弃且生产者无感知。死信队列处理的是已入队但无法正常消费的消息，与路由失败是两回事 |
| 缺点 | 需额外配置回调；退回消息仍需业务兜底重发；增加生产者处理逻辑复杂度 |

### 4. ★★ 关于 Quorum Queue 与镜像队列（Mirrored Queue），描述正确的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Quorum Queue 基于 Raft 协议强一致复制，写入需多数派确认；镜像队列无一致性协议保证 |
| 能做什么 | Quorum Queue 保证数据不丢与自动选主；镜像队列提供主从冗余但存在脑裂风险 |
| 怎么用 | `default_queue_type = quorum`；镜像队列用 `ha-mode=all` 策略 |
| 原理和工作流程 | Quorum Queue 基于 Raft，Leader 处理读写，写入需多数派落盘确认，节点数需至少 3 个（建议奇数），避免脑裂。镜像队列所有读写经 Master，Mirror 仅同步，不提供负载均衡，网络分区时可能出现脑裂与消息丢失。Quorum Queue 使用磁盘存储，吞吐低于经典队列 |
| 缺点 | Quorum Queue 吞吐较低且不支持部分经典特性；镜像队列已不推荐用于新项目 |

### 5. ★★ 在 RabbitMQ 中，保证单个队列内消息顺序性的正确做法是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 单队列 + 单消费者 + prefetch=1 + 手动 ack 保证单队列内 FIFO 顺序 |
| 能做什么 | 保证同一队列消息按序处理；避免多消费者竞争导致乱序；失败阻塞而非跳过 |
| 怎么用 | `channel.basicQos(1)`；autoAck=false；处理成功 basicAck |
| 原理和工作流程 | RabbitMQ 只保证单队列内 FIFO，多消费者竞争同一队列会因处理速度不同导致乱序。保证顺序需单队列 + 单消费者 + prefetch=1（一次只投递一条）+ 手动 ack（处理成功再确认下一条）。Fanout 广播与消息优先级与顺序性无关，多消费者反而破坏顺序 |
| 缺点 | 单消费者吞吐低；消费失败阻塞后续消息；与并行扩展天然冲突 |

### 6. ★★★ 队列配置了 `x-max-length` 且 `x-overflow=reject-publish-dlx`，当队列已满时新消息会（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | x-overflow=reject-publish-dlx 时拒收新消息并投递到死信交换机 |
| 能做什么 | 队列满时保护 Broker；把溢出消息转入死信队列异步处理；避免丢弃队头旧消息 |
| 怎么用 | `x-max-length` + `x-overflow=reject-publish-dlx` + 死信交换机 |
| 原理和工作流程 | x-overflow 支持 drop-head（默认丢弃队头最旧消息）、reject-publish（拒收并返回 nack）、reject-publish-dlx（拒收并投递死信交换机）三种取值。选 reject-publish-dlx 时新消息进死信队列，不覆盖旧消息 |
| 缺点 | 队列满时生产者需处理 nack；死信堆积需监控；三种取值语义易混淆 |

### 7. ★★ Spring AMQP 中 `publisher-confirm-type=correlated` 相比 `simple` 的优势是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | correlated 模式携带 CorrelationData，可在 Confirm 回调中精确定位失败消息 |
| 能做什么 | 定位具体失败消息；把失败消息落库重发；实现可靠的发送确认链路 |
| 怎么用 | `publisher-confirm-type=correlated` + `setConfirmCallback(...)` 取 correlationData.getId() |
| 原理和工作流程 | correlated 模式下发送时携带 CorrelationData（通常含业务唯一 ID），Confirm 回调可取出定位失败消息并落库重试。simple 模式只提供全局确认开关，无法关联到具体消息。correlated 不提升性能，也不免除回调配置 |
| 缺点 | 需业务维护 CorrelationData；回调中重发需幂等；增加代码复杂度 |

### 8. ★★★ `channel.basicQos(prefetchCount)` 的作用是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | basicQos 限制消费者端未确认消息的最大数量，实现公平分发 |
| 能做什么 | 防止单个消费者被压垮；控制未确认消息上限；配合手动 ack 实现可靠消费 |
| 怎么用 | `channel.basicQos(1)` 或 `spring.rabbitmq.listener.simple.prefetch=10` |
| 原理和工作流程 | Broker 仅在消费者未确认消息数低于 prefetch 时继续推送，prefetch=1 表示处理完一条并 ack 后才投递下一条。它与队列最大长度、消息 TTL、生产者发送速率限制无关，是消费者级别的流控机制 |
| 缺点 | prefetch 过小限制吞吐；过大则宕机后大量消息重新入队；需按业务处理耗时调优 |

### 9. ★★ 消息进入死信队列后，`x-death` 头信息中不包含（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | x-death 记录死信原因、原队列、原交换机、路由键、时间戳与次数，不含消息原始内容 |
| 能做什么 | 排查消息为何进入死信；统计死信次数；区分 expired/rejected/maxlen 等原因 |
| 怎么用 | 死信消费者读取 `headers.get("x-death")` 数组解析 |
| 原理和工作流程 | Broker 在消息成为死信时自动附加 x-death 数组型头信息，字段含 reason、queue、exchange、routing-keys、time、count。消息原始内容保存在消息体中，不在 x-death 里。x-death 是定位死信根因的关键线索 |
| 缺点 | 结构为数组，解析稍繁琐；多次死信会累积多个条目；不包含业务上下文需自行补充 |

### 10. ★★ Headers Exchange 中 `x-match=all` 的含义是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Headers Exchange 按消息 Header 属性匹配，x-match=all 要求所有声明 Header 都匹配 |
| 能做什么 | 按属性组合路由；表达 Routing Key 难以承载的复杂条件；支持 all/any 两种匹配模式 |
| 怎么用 | `BindingBuilder.bind(queue).to(headersExchange).whereAll("type","log").match()` |
| 原理和工作流程 | Headers Exchange 忽略 Routing Key，根据消息 Header 属性匹配。x-match=all 要求 Binding 中声明的所有 Header 都匹配才投递，x-match=any 只需其中一个匹配。Fanout 忽略 Routing Key 全广播，Direct 按 Routing Key 精确匹配，均与 Headers 语义不同 |
| 缺点 | 性能低于 Direct/Topic；可读性差排查困难；实际使用较少生态工具支持弱 |

### 11. ★★★ 消费者收到消息后尚未 ack 就宕机，RabbitMQ 会（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 未确认消息在消费者连接断开后重新入队，redelivered 标记为 true |
| 能做什么 | 保证消息不因消费者宕机而丢失；投递给其他消费者或原消费者重连后消费；触发消费端幂等需求 |
| 怎么用 | 手动 ack 模式；消费端按业务唯一 ID 幂等 |
| 原理和工作流程 | 未确认消息在消费者连接断开后会被重新入队，投递给其他消费者或原消费者，redelivered 置为 true，体现"至少一次"语义。只有显式 basic.nack/reject 且 requeue=false、TTL 过期、队列超限时才进入死信队列，不会直接丢失 |
| 缺点 | 重复投递需幂等；大量未确认消息重投造成瞬时压力；redelivered 需业务感知 |

### 12. ★★ RabbitMQ 3.12 起，经典队列的默认消息存储模式是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 3.12 起经典队列默认磁盘优先（惰性队列行为），消息直接写入磁盘文件 |
| 能做什么 | 大幅降低内存占用；支撑百万级消息堆积；避免 OOM |
| 怎么用 | 默认行为；也可显式 `x-queue-mode=lazy` 或策略 `queue-mode=lazy` |
| 原理和工作流程 | RabbitMQ 3.10 引入惰性队列，3.12 起成为默认模式，经典队列默认磁盘优先，消息到达即写入磁盘文件，内存仅作缓存，百万级堆积时内存占用稳定在数百 MB，代价是消费吞吐降低约 30%-50% |
| 缺点 | 消费吞吐下降；磁盘 I/O 成为瓶颈；低延迟场景不如内存优先模式 |

---

## 二、简答题（8 题，每题附完整解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 需要文字阐述原理的题型，本题集共 8 道，覆盖 Exchange 路由、可靠性投递、死信与延迟、顺序性、幂等、高可用、积压治理 |
| 能做什么 | 考查四种 Exchange 路由机制、三环节防丢消息、死信原理与 x-death、延迟队列两方案对比、顺序性三条件、幂等四方案、镜像队列与 Quorum Queue 选型、RabbitMQ 与 Kafka 积压差异 |
| 怎么用 | 分点阐述原理，结合配置项和拓扑图说明 |
| 原理和工作流程 | 简答题要求系统阐述机制原理与流程，覆盖 Exchange 通配符匹配、Confirm+Return+三重持久化+手动 ack 全链路、死信三种触发与转发机制、TTL+DLX 与延迟插件的优劣、顺序性三条件与吞吐权衡、幂等键选择与幂等窗口、Raft 与镜像队列差异、队列深度与消费者数排查。每题附完整解析 |
| 缺点 | 主观评分；答案需全面否则失分；难以机器批改 |

### 1. 简述 RabbitMQ 四种 Exchange 类型的路由机制与适用场景

| 维度 | 内容 |
|------|------|
| 是什么 | Direct 精确匹配、Topic 通配符匹配、Fanout 广播、Headers 按属性匹配四种路由机制 |
| 能做什么 | Direct 单播分发；Topic 多条件路由；Fanout 全局广播；Headers 复杂属性路由 |
| 怎么用 | `ExchangeBuilder.direct/topic/fanout/headers(...)`；绑定 `with("order.*.pay")` |
| 原理和工作流程 | Direct 要求 Routing Key 与 Binding Key 完全相等。Topic 中 `*` 匹配一个词、`#` 匹配零个或多个词，如 order.*.pay 匹配 order.cn.pay 不匹配 order.pay。Fanout 忽略 Routing Key 广播到所有绑定队列。Headers 按消息 Header 匹配，x-match=all 要求全部匹配、any 只需其一。选型建议：能用 Direct 就不用 Topic，广播用 Fanout，Headers 少用 |
| 缺点 | Topic 通配符易误投；Fanout 无差别分发浪费带宽；Headers 性能差可读性低 |

### 2. RabbitMQ 如何保证消息不丢失 请从生产者 Broker 消费者三个环节说明全链路方案

| 维度 | 内容 |
|------|------|
| 是什么 | 生产者 Confirm 与 Return、Broker 三重持久化与高可用、消费者手动 ack 与死信兜底的全链路方案 |
| 能做什么 | 生产者感知发送结果并重发；Broker 落盘且多副本；消费者处理成功才确认 |
| 怎么用 | `publisher-confirm-type=correlated`；`publisher-returns=true`；durable + deliveryMode=2；`acknowledge-mode=manual` |
| 原理和工作流程 | 生产者端开启 Confirm 与 Return，配合本地消息表把未确认消息落库重发。Broker 端 Exchange、Queue、消息三重持久化缺一不可，关键队列用 Quorum Queue 多数派确认，配置磁盘水位告警。消费者端手动 ack，处理失败 basicNack，达上限进死信，并用业务唯一 ID 实现幂等 |
| 缺点 | 全链路同步降低吞吐；本地消息表增加数据库压力；死信需人工处理；运维成本上升 |

### 3. 简述 RabbitMQ 死信队列的实现原理与常见使用场景

| 维度 | 内容 |
|------|------|
| 是什么 | 消息因 TTL 过期、队列超限、消费拒绝 requeue=false 成为死信，经死信交换机转发到死信队列 |
| 能做什么 | 消息重试；延迟队列；异常消息分析；流量削峰 |
| 怎么用 | `x-dead-letter-exchange` + `x-dead-letter-routing-key`；消费端 `basicNack(tag,false,false)` |
| 原理和工作流程 | 业务队列声明时指定死信交换机与死信路由键，消息成为死信后 Broker 自动转发，并在消息头附加 x-death 记录 reason、queue、exchange、count 等。三种触发条件为 TTL 过期、队列达最大长度被拒、消费者 basic.nack/reject 且 requeue=false。死信队列必须有消费者并监控堆积，否则会无限堆积直至磁盘写满 |
| 缺点 | 死信堆积需监控与人工介入；TTL 队头阻塞；增加拓扑复杂度与运维成本 |

### 4. RabbitMQ 延迟队列有哪两种实现方式 各自有什么坑

| 维度 | 内容 |
|------|------|
| 是什么 | TTL + DLX 组合与 rabbitmq-delayed-message-exchange 插件两种延迟消息实现 |
| 能做什么 | 订单超时取消；定时提醒；失败消息退避重试 |
| 怎么用 | `.ttl(1800000).deadLetterExchange("dlx")`；`CustomExchange("x-delayed-message")` + `setDelay(ms)` |
| 原理和工作流程 | TTL + DLX 让消息在普通队列等待 TTL 过期后自动转发死信队列，消费者监听死信队列实现延迟。坑在于 RabbitMQ 只检查队头消息是否过期，消息级 TTL 下短 TTL 消息会被长 TTL 消息阻塞（队头阻塞），故不同延迟档位应用独立队列。插件支持任意延迟且无队头阻塞，但需安装维护、延迟消息存于 Mnesia 节点故障风险较高 |
| 缺点 | TTL+DLX 档位固定且有队头阻塞；插件需额外维护且可靠性受限；延迟精度有限 |

### 5. RabbitMQ 如何保证消息顺序性 为什么说顺序和吞吐难以兼得

| 维度 | 内容 |
|------|------|
| 是什么 | 单队列 + 单消费者 + prefetch=1 + 手动 ack 是保证顺序的三个条件 |
| 能做什么 | 保证单队列内严格 FIFO；失败阻塞不跳过；按业务 Key 分片实现局部有序 |
| 怎么用 | `channel.basicQos(1)`；autoAck=false；处理成功 basicAck |
| 原理和工作流程 | RabbitMQ 只保证单队列内 FIFO，多消费者竞争同一队列会因处理速度差异乱序，故需单队列单消费者加 prefetch=1 加手动 ack。顺序优先意味着单队列单消费者大 prefetch 小，吞吐优先则多队列多消费者，两者直接冲突。实践建议优先设计幂等消费，确需顺序时按业务 Key 分片到多队列，每个队列单消费者，实现局部有序加全局并行，并对失败消息设置重试上限转死信 |
| 缺点 | 单消费者吞吐低；消费失败阻塞队列；分片方案增加拓扑复杂度；与扩容天然矛盾 |

### 6. 什么是幂等消费 RabbitMQ 场景下有哪些常见的幂等实现方案

| 维度 | 内容 |
|------|------|
| 是什么 | 幂等消费指同一消息被处理多次与处理一次结果一致，应对至少一次投递语义 |
| 能做什么 | 业务唯一 ID 加唯一索引；Redis 去重表；状态机加版本号；数据库乐观锁 |
| 怎么用 | `redisTemplate.opsForValue().setIfAbsent(idempotentKey, "1", Duration.ofDays(7))` |
| 原理和工作流程 | 消息重复来源包括未 ack 就宕机、ack 丢失、手动重试等。幂等键优先选业务唯一 ID（订单号、流水号）而非消息 ID，因为重发时消息 ID 会变化。Redis 去重的 TTL 需大于最大重投时间窗口。幂等校验通过并处理成功后再 ack，幂等命中时直接 ack 不要抛异常触发重试。数据库唯一索引可作最后兜底 |
| 缺点 | 需额外存储与组件；幂等窗口难精确估计；状态机方案需业务改造；乐观锁增加写冲突 |

### 7. 镜像队列（Mirrored Queue）与 Quorum Queue 有什么区别 如何选择

| 维度 | 内容 |
|------|------|
| 是什么 | 镜像队列为主从同步无一致性协议，Quorum Queue 基于 Raft 多数派确认强一致 |
| 能做什么 | Quorum Queue 保证数据不丢与自动选主；镜像队列提供主从冗余但存在脑裂风险 |
| 怎么用 | `default_queue_type = quorum`；镜像队列 `ha-mode=all` 策略 |
| 原理和工作流程 | 镜像队列所有读写经 Master，Mirror 仅同步不提供负载均衡，网络分区时可能脑裂丢消息，官方已不再推荐。Quorum Queue 基于 Raft，Leader 处理读写，写入需多数派落盘确认，节点数至少 3 且建议奇数，自动选主避免脑裂，但吞吐较低且不支持优先级队列等部分经典特性。新项目要求不丢数据优先选 Quorum Queue，需经典特性时用经典队列 |
| 缺点 | Quorum Queue 吞吐低且特性受限；经典队列不能原地转 Quorum 需迁移；节点数要求高 |

### 8. RabbitMQ 出现消息积压应如何处理 与 Kafka 的积压处理有何不同

| 维度 | 内容 |
|------|------|
| 是什么 | RabbitMQ 通过扩容消费者、调大 prefetch、转存新队列、惰性队列、清理丢弃处理积压 |
| 能做什么 | 定位队列深度与消费者数；扩容并行度；转存新队列再消费；启用惰性队列防 OOM |
| 怎么用 | `rabbitmqctl list_queues name messages consumers`；`set_policy ... '{"queue-mode":"lazy"}'`；管理台 purge |
| 原理和工作流程 | 先通过管理台或 rabbitmqctl 查看队列深度、消费者数量、入出队速率定位瓶颈。处理手段包括增加消费者（无分区硬限制但会破坏顺序）、调大 prefetch、优化消费逻辑、转存新队列并行消费、启用惰性队列避免 OOM、确认可容忍时 purge 或设 TTL 丢弃。与 Kafka 差异：Kafka 消费者数受 Partition 数限制、消息按 offset 保留可重放、积压主要受磁盘限制；RabbitMQ 加消费者无硬限制但破坏顺序、消费后删除不可重放、积压易占内存需惰性队列缓解 |
| 缺点 | 加消费者破坏顺序；转存需额外运维且可能重复；purge 不可逆；惰性队列降低吞吐 |

---

## 三、场景设计题（3 题，每题附完整解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 给定业务场景设计 RabbitMQ 方案的综合题型，本题集共 3 道 |
| 能做什么 | 考查可靠性投递全链路、订单超时取消、高可用与积压治理的设计 |
| 怎么用 | 分析场景需求，设计生产者 Broker 消费者三层保障，选择延迟队列方案，规划 Quorum Queue 与监控阈值 |
| 原理和工作流程 | 场景设计题要求结合业务需求选择 RabbitMQ 特性，设计拓扑、可靠性保障、幂等、死信兜底、监控告警与运维规范。覆盖 Confirm 加 Return 加本地消息表、三重持久化加 Quorum Queue、手动 ack 加重试加死信、TTL+DLX 独立档位队列与延迟插件对比、惰性队列与三级积压处置。每题附完整设计方案和关键配置 |
| 缺点 | 答案开放主观评分；需综合多知识点；难以机器批改 |

### 1. 设计一个"RabbitMQ 可靠性投递"全链路方案

| 维度 | 内容 |
|------|------|
| 是什么 | 支付结果通知场景下，从生产者 Confirm+Return+本地消息表、Broker 三重持久化+Quorum Queue、消费者手动 ack+重试+死信+幂等的全链路不丢不重方案 |
| 能做什么 | 未确认消息落库重发；路由失败可感知；消息落盘且多数派确认；消费成功才确认；重复投递幂等 |
| 怎么用 | `publisher-confirm-type=correlated`；`publisher-returns=true`；`mandatory=true`；durable + `deliveryMode=2`；`acknowledge-mode=manual` |
| 原理和工作流程 | 生产者端 Confirm 回调中未 ack 则落库重发，Return 回调记录路由失败，本地消息表与业务落库同一事务，状态 PENDING 到 SENT 由定时任务补偿。Broker 端 Exchange、Queue、消息三重持久化缺一不可，关键队列用 Quorum Queue 多数派确认并配置磁盘水位告警。消费者端 Redis 幂等校验通过后处理，处理成功 basicAck，失败按重试次数决定 requeue 或进死信，监控队列深度与死信堆积 |
| 缺点 | 全链路可靠性带来吞吐下降；本地消息表增加数据库压力；死信需人工介入；运维复杂度上升 |

### 2. 设计一个"基于 RabbitMQ 的订单超时取消"系统

| 维度 | 内容 |
|------|------|
| 是什么 | 下单 30 分钟未支付自动取消并释放库存，基于 TTL+DLX 独立档位队列或延迟插件实现 |
| 能做什么 | 30 分钟整触发；幂等防重复取消；分布式并发控制；失败重试与死信兜底 |
| 怎么用 | `.ttl(1800000).deadLetterExchange(...)`；`CustomExchange("x-delayed-message")` + `setDelay(30*60*1000)` |
| 原理和工作流程 | 拓扑为延迟交换机到延迟等待队列（TTL 30 分钟，绑定死信交换机）到处理交换机到处理队列到消费者。不同延迟档位用独立队列避免消息级 TTL 队头阻塞。消费者先做 Redis 幂等校验，再查订单状态，UNPAID 则取消并恢复库存，PAID 或 CANCELLED 忽略，处理成功 basicAck，异常 basicNack 重试，达上限进死信。方案对比：TTL+DLX 无需插件但档位固定，延迟插件支持任意延迟但需维护，定时任务扫描最简单但有延迟，RocketMQ 延迟消息最精确但需引入新中间件 |
| 缺点 | TTL+DLX 有队头阻塞风险；插件节点故障风险较高；海量订单下延迟队列压力大；取消需幂等与并发控制 |

### 3. 设计一个"RabbitMQ 高可用与积压治理"方案

| 维度 | 内容 |
|------|------|
| 是什么 | 3 节点集群出现通知队列积压 200 万、镜像队列切换丢消息问题的高可用改造与三级积压治理方案 |
| 能做什么 | 关键队列改 Quorum Queue；非关键队列启用惰性模式；扩容消费能力；转存新队列；监控告警与运维规范 |
| 怎么用 | `default_queue_type = quorum`；`set_policy lazy-queue "^(notice|log)\." '{"queue-mode":"lazy"}'`；`rabbitmqctl list_queues name messages consumers` |
| 原理和工作流程 | 高可用改造：集群 3 或 5 奇数节点跨机架分布，关键队列用 Quorum Queue 基于 Raft 多数派确认避免脑裂丢消息，非关键队列用经典队列加惰性模式优先吞吐与内存安全。积压治理三级：先扩容消费者并适度调大 prefetch 止血，消费逻辑慢时建新队列用临时消费者快速转存再并行消费，可容忍时 purge 或设 TTL 丢弃。监控指标含队列深度、消费者数量为 0 告警、未确认消息数、入出队速率、磁盘剩余空间、内存使用率、死信深度、节点存活与网络分区 |
| 缺点 | Quorum Queue 吞吐较低；惰性队列降低消费吞吐约 30%-50%；转存方案需额外运维且可能重复；purge 不可逆 |

---

> [返回原文](./RabbitMQ笔面试题集.md) | [返回模块目录](../../../README.md) | [返回知识导览](../../../知识导览.md)
