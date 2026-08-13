# RocketMQ 核心原理 导览

> 定位：五维框架浓缩提炼 01-RocketMQ核心原理.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./01-RocketMQ核心原理.md)。
> 前置知识：了解分布式系统基本概念，了解消息队列的三大作用（削峰、解耦、异步）

---

## 一、核心概念

### 1.1 RocketMQ 概述与发展历史

| 维度 | 内容 |
|------|------|
| 是什么 | 阿里巴巴开源的分布式消息中间件，2011 年 MetaQ 起源，2017 年成为 Apache 顶级项目，服务于双十一万亿级消息流转 |
| 能做什么 | 金融级业务消息传递；分布式事务支持；万亿级消息吞吐；生产环境大规模验证 |
| 怎么用 | 引入 rocketmq-spring-boot-starter 依赖，配置 NameServer 地址，通过 RocketMQTemplate 发送消息 |
| 原理和工作流程 | 起源于阿里内部 MetaQ 服务淘宝交易核心链路，2012 年抽象出四大组件，2016 年捐赠 Apache，2017 年成为 TLP。历经 4.x 到 5.x 版本迭代，引入事务消息、ACL、Proxy 模式、Pop 消费等能力，持续向云原生演进 |
| 缺点 | 社区生态较 Kafka 小；早期版本文档不完善；5.x 版本架构变动较大，迁移成本较高；强依赖 Java 生态 |

### 1.2 与 Kafka/RabbitMQ 对比

| 维度 | 内容 |
|------|------|
| 是什么 | RocketMQ 与 Kafka、RabbitMQ 在定位、吞吐量、延迟、功能特性、运维复杂度等维度的差异矩阵 |
| 能做什么 | RocketMQ 10w+ TPS 原生事务消息 18 级延迟；Kafka 100w+ TPS 流处理；RabbitMQ 复杂路由微秒延迟 |
| 怎么用 | 金融电商事务消息选 RocketMQ；大数据管道选 Kafka；复杂路由低延迟选 RabbitMQ |
| 原理和工作流程 | RocketMQ 基于 Topic + Queue 模型，类似 Kafka 但原生支持事务消息和延迟消息，消费后保留可回溯。Kafka 基于日志分区模型，百万 TPS 适合流处理。RabbitMQ 基于 AMQP 队列模型，四种 Exchange 灵活路由，消费后删除。RocketMQ 在事务消息、延迟消息、Tag 过滤方面有独特优势 |
| 缺点 | 吞吐量低于 Kafka（10w vs 100w+）；延迟高于 RabbitMQ（ms vs us）；路由能力弱于 RabbitMQ；运维复杂度高于 RabbitMQ |

### 1.3 整体架构

| 维度 | 内容 |
|------|------|
| 是什么 | 由 NameServer、Broker、Producer、Consumer 四大组件构成的分布式消息中间件架构 |
| 能做什么 | NameServer 无状态路由注册；Broker 消息存储转发；Producer 消息生产；Consumer 消息消费 |
| 怎么用 | 多 NameServer 部署，Broker 注册 Topic 路由，Producer 和 Consumer 从 NameServer 拉取路由信息 |
| 原理和工作流程 | Broker 启动向所有 NameServer 注册 Topic 路由信息心跳 30s。Producer 启动从 NameServer 拉取路由信息选择 MessageQueue 发送消息。Consumer 启动从 NameServer 拉取路由信息建立长连接拉取消息。NameServer 之间不通信，客户端定时拉取感知路由变更 |
| 缺点 | NameServer 最终一致性有延迟（最多 30s）；Broker 重注册依赖心跳；NameServer 单点故障客户端需重试其他节点；没有中心化配置管理 |

### 1.4 核心概念

| 维度 | 内容 |
|------|------|
| 是什么 | Topic、Tag、MessageQueue、ProducerGroup、ConsumerGroup 五个核心概念的定位与关系 |
| 能做什么 | Topic 逻辑分类；Tag 子分类过滤；MessageQueue 物理分片并行；ProducerGroup 事务回查标识；ConsumerGroup 集群消费负载均衡 |
| 怎么用 | `topic:tag` 发送消息；`writeQueueNums` 和 `readQueueNums` 控制读写并行度 |
| 原理和工作流程 | Topic 是一类消息的集合，Tag 进一步细分。MessageQueue 是物理分片，每个 Broker 上可配置多个读写队列。读写队列分离允许缩容时先缩小写队列，待消费完再缩小读队列。ProducerGroup 用于事务消息回查，ConsumerGroup 用于集群消费时负载均衡 |
| 缺点 | Tag 过滤仅支持单个 Tag 或全部；MessageQueue 读写分离增加配置复杂度；缩容需手动操作且依赖消费进度 |

---

## 二、底层原理

### 2.1 NameServer 路由发现

| 维度 | 内容 |
|------|------|
| 是什么 | 无状态轻量级路由注册中心，各 NameServer 之间不通信，通过 Broker 心跳注册和客户端定时拉取实现路由发现 |
| 能做什么 | 接收 Broker 注册；维护路由信息；供 Producer 和 Consumer 查询；心跳超时剔除；主动下线处理 |
| 怎么用 | 部署多台 NameServer，Producer 和 Consumer 配置 `namesrvAddr=host1:9876;host2:9876` |
| 原理和工作流程 | Broker 启动向所有 NameServer 发送注册请求携带 Topic 配置，每 30s 心跳维持。Producer 和 Consumer 启动定时 30s 从 NameServer 拉取路由信息。Broker 120s 未心跳时 NameServer 移除路由。Broker 正常关闭发送 UNREGISTER_BROKER。磁盘满时 Broker 标记自身不可写 |
| 缺点 | 最终一致性有 30s 窗口延迟；NameServer 数量增加客户端连接开销；无健康检查细化机制；路由变更无主动推送 |

### 2.2 消息存储（CommitLog + ConsumeQueue + IndexFile）

| 维度 | 内容 |
|------|------|
| 是什么 | 三层存储模型：CommitLog 统一存储所有消息，ConsumeQueue 按 Topic+Queue 构建轻量索引，IndexFile 按 Key 构建哈希索引 |
| 能做什么 | CommitLog 顺序写 600MB/s 高吞吐；ConsumeQueue 20 字节条目快速定位；IndexFile 按 Key 检索消息 |
| 怎么用 | 默认每文件 1GB，`$HOME/store/commitlog/` 存储，`$HOME/store/consumequeue/` 索引 |
| 原理和工作流程 | 所有 Topic 消息顺序追加写入同一个 CommitLog 文件，写满 1GB 新建。ReputMessageService 异步从 CommitLog 构建 ConsumeQueue 条目，每条 20 字节含 CommitLog Offset、消息大小、Tag HashCode。消费者按 ConsumeQueue 定位后从 CommitLog 读取。IndexFile 按 Key 哈希定位哈希槽，链表遍历匹配消息 |
| 缺点 | 消费时需随机读取 CommitLog 依赖 Page Cache 命中率；ConsumeQueue 异步构建有延迟；IndexFile 占用额外磁盘；CommitLog 单文件损坏影响所有 Topic |

### 2.3 零拷贝（mmap vs sendfile）

| 维度 | 内容 |
|------|------|
| 是什么 | RocketMQ 同时使用 mmap 内存映射和 sendfile 系统调用两种零拷贝技术，分别用于写文件和发网卡操作 |
| 能做什么 | mmap 减少写入拷贝次数提升写入吞吐；sendfile 跳过用户态直接将 Page Cache 数据发网卡 |
| 怎么用 | RocketMQ 内部自动选择，mmap 用于 CommitLog 写入和 ConsumeQueue 读取，sendfile 用于消息拉取 |
| 原理和工作流程 | mmap 将文件映射到进程虚拟地址空间，用户态直接操作 Page Cache，1 次 DMA 拷贝加 2 次上下文切换。sendfile 使数据从 Page Cache 直接 DMA 拷贝到网卡，不经过用户态，2 次 DMA 拷贝加 2 次上下文切换。生产者发送时 mmap 写入 CommitLog，消费者拉取时 sendfile 将 CommitLog 数据从 Page Cache 直发网卡 |
| 缺点 | mmap 受虚拟地址空间限制（32 位系统）；sendfile 无法在用户态加工数据；两者均依赖 Page Cache 命中率；sendfile 仅适用于文件到网络传输 |

### 2.4 同步刷盘 vs 异步刷盘

| 维度 | 内容 |
|------|------|
| 是什么 | 消息写入磁盘的两种策略：同步刷盘等待 fsync 完成，异步刷盘后台线程定期刷盘默认 500ms |
| 能做什么 | 同步刷盘保证 Broker 宕机不丢消息；异步刷盘提升吞吐 10 倍以上 |
| 怎么用 | `flushDiskType=SYNC_FLUSH` 或 `ASYNC_FLUSH`；复制模式 `SYNC_MASTER` 或 `ASYNC_MASTER` |
| 原理和工作流程 | 同步刷盘消息写入 Page Cache 后立即调用 fsync 强制刷盘，返回成功前等待刷盘完成，TPS 约 5k-10k。异步刷盘消息写入 Page Cache 后立即返回成功，后台线程每 500ms 刷盘，TPS 可达 10w+。主从复制中同步复制 Master 等待 Slave 复制完成，异步复制 Master 写入成功即返回。金融用同步刷盘加同步复制，日志用异步刷盘加异步复制，电商用异步刷盘加同步复制折中 |
| 缺点 | 同步刷盘吞吐极低；异步刷盘可能丢失 500ms 内消息；同步复制增加延迟；多副本同步增加网络开销 |

### 2.5 消息发送（同步/异步/单向）

| 维度 | 内容 |
|------|------|
| 是什么 | 三种发送方式：同步阻塞等待结果、异步回调通知结果、单向不等待不感知 |
| 能做什么 | 同步高可靠感知结果；异步高吞吐低延迟；单向最高性能 |
| 怎么用 | `syncSend()` 同步；`asyncSend()` 加 `SendCallback` 异步；`sendOneWay()` 单向 |
| 原理和工作流程 | 同步发送后阻塞等待 Broker 返回 SendResult 含 msgId 和 sendStatus，失败自动重试 2 次。异步发送后立即返回，通过 SendCallback 的 onSuccess 和 onException 通知结果，失败自动重试 2 次。单向发送后不等待任何返回，不重试。发送流程为从 NameServer 获取路由、选择 MessageQueue、构建消息、序列化发送、Broker 写入 CommitLog 返回 |
| 缺点 | 同步发送阻塞线程增加延迟；异步发送回调增加代码复杂度；单向发送不感知结果消息可能丢失；三种方式混用增加维护成本 |

### 2.6 消费重试机制

| 维度 | 内容 |
|------|------|
| 是什么 | 消费者消费失败后按延迟等级递增重试的机制，默认 16 次后进入死信队列 |
| 能做什么 | 自动重试失败消息；延迟等级实现退避策略；死信队列兜底防止消息丢失 |
| 怎么用 | 消费失败返回 `RECONSUME_LATER` 或抛出异常；配置 `maxReconsumeTimes` 调整最大重试次数 |
| 原理和工作流程 | 消费失败时消息发送到 `%RETRY%{ConsumerGroup}` 重试 Topic，按延迟等级递进。每次重试延迟递增从 10s 到 2h，共 18 个等级。超过最大重试次数 16 次后消息进入 `%DLQ%{ConsumerGroup}` 死信队列。重试队列和死信队列的 Topic 由 RocketMQ 自动创建和管理 |
| 缺点 | 16 次重试总计约 2-3 小时阻塞消费队列；重试消息与正常消息共用消费线程；死信队列需人工处理；重试次数过多影响消费吞吐 |

---

## 三、实战应用

### 3.1 Spring Boot 集成 RocketMQ

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 rocketmq-spring-boot-starter 依赖在 Spring Boot 项目中接入 RocketMQ 的集成方案 |
| 能做什么 | RocketMQTemplate 同步异步单向发送消息；@RocketMQMessageListener 注解声明消费者；Tag 过滤消费 |
| 怎么用 | `rocketMQTemplate.syncSend("order-topic:create", payload)`；`@RocketMQMessageListener(topic="order-topic", selectorExpression="create")` |
| 原理和工作流程 | 引入 starter 后 Spring Boot 自动配置 RocketMQTemplate 和 DefaultRocketMQListenerContainer。生产者通过 RocketMQTemplate 调用底层 DefaultMQProducer 发送消息。消费者通过 @RocketMQMessageListener 注解注册到容器，容器管理消费线程和确认。配置项映射到 ProducerConfig 和 ConsumerConfig |
| 缺点 | 自动配置隐藏底层细节问题排查需了解原生 API；消费者异常处理需手动配置；注解配置不够灵活不适合复杂消费场景 |

### 3.2 消息发送可靠性保障

| 维度 | 内容 |
|------|------|
| 是什么 | 通过本地消息表先落库再发送的方案，保证消息发送与业务操作的事务一致性 |
| 能做什么 | 消息先持久化到数据库；发送成功更新状态；发送失败由定时任务补偿重试 |
| 怎么用 | 事务中先插入消息日志 PENDING 状态，同步发送消息，成功更新为 SENT，失败由定时任务扫描重试 |
| 原理和工作流程 | 业务操作和消息日志插入在同一事务中保证原子性。发送消息到 RocketMQ 成功后更新消息状态为 SENT。发送失败时消息状态保持 PENDING，定时任务扫描 PENDING 状态消息重新发送。需要保证消息幂等，避免重复发送导致重复消费 |
| 缺点 | 消息表增加数据库写入压力；定时任务扫描有延迟；消息体过大时数据库存储成本高；需处理消息表数据清理 |

### 3.3 消费积压排查

| 维度 | 内容 |
|------|------|
| 是什么 | 消费者处理速度落后于生产速度导致消息堆积的排查与处理方法 |
| 能做什么 | 查看消费组积压量；定位积压队列；扩容消费者或优化处理逻辑 |
| 怎么用 | `mqadmin consumerProgress -g order-consumer-group`；`mqadmin statsAll -t order-topic` |
| 原理和工作流程 | 通过 mqadmin 命令查看消费组各队列的 Diff Total 即积压量。处理策略为增加消费者实例不超过 readQueueNums、提升消费线程数、优化消费逻辑异步处理耗时操作、临时扩容 readQueueNums、创建临时 ConsumerGroup 消费积压数据转发新 Topic |
| 缺点 | 消费者扩容受限于 readQueueNums；扩容 readQueueNums 需重启 Broker；积压严重时清理消息会造成数据丢失；临时 ConsumerGroup 方案需额外运维 |

---

## 四、常见面试题

### 1. RocketMQ 的整体架构是怎样的 各组件分别承担什么职责

| 维度 | 内容 |
|------|------|
| 是什么 | 由 NameServer、Broker、Producer、Consumer 四大组件构成的分布式消息中间件架构 |
| 能做什么 | NameServer 无状态路由注册中心；Broker 消息存储转发分 Master Slave；Producer 三种发送方式；Consumer 集群广播模式 |
| 怎么用 | 多 NameServer 部署，Broker 注册心跳 30s 剔除 120s，Producer 和 Consumer 定时拉取路由 |
| 原理和工作流程 | NameServer 无状态不通信，Broker 启动向所有 NameServer 注册心跳维持。Producer 从 NameServer 拉取路由选择 MessageQueue 发送。Consumer 从 NameServer 拉取路由建立长连接拉取。Broker 分 Master 负责读写和 Slave 负责备份，消息统一存 CommitLog 通过 ConsumeQueue 索引消费 |
| 缺点 | NameServer 最终一致性有延迟；Broker 重注册依赖心跳；NameServer 单点需客户端重试；无中心化配置管理 |

### 2. RocketMQ 的 CommitLog + ConsumeQueue 存储模型有什么优势

| 维度 | 内容 |
|------|------|
| 是什么 | 所有 Topic 消息顺序追加写入 CommitLog，按 Topic+Queue 构建 ConsumeQueue 轻量索引的三层存储模型 |
| 能做什么 | CommitLog 顺序写 600MB/s 高吞吐；ConsumeQueue 20 字节条目快速定位；读写队列分离灵活扩缩容 |
| 怎么用 | 默认 1GB 文件，`commitlog/` 目录存储，`consumequeue/` 目录索引 |
| 原理和工作流程 | 所有 Topic 消息顺序追加写入同一个 CommitLog 避免随机 I/O。ConsumeQueue 每条 20 字节含 CommitLog Offset、消息大小、Tag HashCode，消费者按此定位后从 CommitLog 读取。读写队列分离支持动态缩容先缩小写队列消费完再缩小读队列 |
| 缺点 | 消费需随机读取 CommitLog 依赖 Page Cache；ConsumeQueue 异步构建有延迟；CommitLog 单文件损坏影响所有 Topic |

### 3. RocketMQ 如何保证消息不丢失

| 维度 | 内容 |
|------|------|
| 是什么 | 从生产者同步发送加重试、Broker 同步刷盘加同步复制、消费者消费确认加重试死信兜底三环节保障 |
| 能做什么 | 生产者同步发送失败自动重试加本地消息表；Broker 同步刷盘加同步复制；消费者失败重试 16 次后死信队列 |
| 怎么用 | `syncSend()` 加 `retryTimesWhenSendFailed=2`；`flushDiskType=SYNC_FLUSH` 加 `brokerRole=SYNC_MASTER`；`maxReconsumeTimes=16` |
| 原理和工作流程 | 生产者端同步发送阻塞等待 Broker 确认，失败自动重试 2 次，配合本地消息表保证发送可靠性。Broker 端同步刷盘消息写入 Page Cache 后立即 fsync 强制落盘，同步复制等待 Slave 复制完成。消费者端消费成功返回 CONSUME_SUCCESS，失败返回 RECONSUME_LATER 触发重试，超最大次数进入死信队列 |
| 缺点 | 全链路同步导致吞吐量极低；同步刷盘和同步复制叠加 TPS 不到 1000；本地消息表增加数据库写入压力 |

### 4. 同步刷盘和异步刷盘有什么区别 如何选择

| 维度 | 内容 |
|------|------|
| 是什么 | 同步刷盘等待 fsync 完成 Broker 宕机不丢消息 TPS 5k-10k；异步刷盘后台 500ms 刷盘 TPS 10w+ 可能丢失 500ms 内消息 |
| 能做什么 | 同步刷盘金融支付级可靠；异步刷盘日志收集高吞吐 |
| 怎么用 | `flushDiskType=SYNC_FLUSH` 或 `ASYNC_FLUSH` |
| 原理和工作流程 | 同步刷盘消息写入 Page Cache 后立即调用 fsync 强制刷盘，返回成功前等待刷盘完成，延迟 ms 级。异步刷盘消息写入 Page Cache 后立即返回成功，后台线程每 500ms 刷盘，延迟 us 级。金融支付用同步刷盘，日志收集用异步刷盘，大多数业务推荐异步刷盘加同步复制折中方案 |
| 缺点 | 同步刷盘吞吐极低不适合高并发；异步刷盘 Broker 宕机可能丢消息不满足金融级要求；刷盘策略与复制策略需组合考虑 |

---

## 五、避坑指南

本节以表格形式列举常见错误、现象、原因与解决方案，属辅助清单内容，不单独生成五维表格。

## 本章学习自检

本节为自检清单，列出本章应掌握的能力点，不生成五维表格。

---

> [返回原文](./01-RocketMQ核心原理.md) | [返回模块目录](../../../README.md) | [返回知识导览](../../../知识导览.md)