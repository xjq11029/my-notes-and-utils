# ZooKeeper 笔面试题集

> 学习路线对应：分布式微服务模块 — ZooKeeper 专题
> 题目来源：大厂面试真题 + 高频考点
> 难度标注：★基础  ★★中档  ★★★拔高

---

## 一、选择题（10 题，每题 4 分，共 40 分）

### 1. ZooKeeper 的数据模型类似于？（★）

A. 关系型数据库表
B. 键值对存储
C. Unix 文件系统
D. 图数据库

**答案：C**

**解析**：ZooKeeper 的数据模型类似于 Unix 文件系统，是一个层级命名空间树。每个节点称为 ZNode，以 `/` 分隔路径，可存储数据并拥有子节点。A 错误（ZK 不是关系型），B 描述的是 Redis 等 KV 存储，D 描述的是 Neo4j 等图数据库。

> 📖 **参考链接**：[ZooKeeper 官方文档 - Data Model](https://zookeeper.apache.org/doc/current/zookeeperDataStructure.html) -- ZNode 树形层级命名空间说明

---

### 2. 以下哪种 ZNode 类型在客户端会话结束后会自动删除？（★）

A. 持久节点（PERSISTENT）
B. 持久有序节点（PERSISTENT_SEQUENTIAL）
C. 临时节点（EPHEMERAL）
D. 容器节点（CONTAINER）

**答案：C**

**解析**：临时节点（EPHEMERAL）与客户端会话绑定，会话结束（超时或主动关闭）后自动删除。持久节点（A/B）在显式删除前一直存在，容器节点（D）在最后一个子节点被删除后自动删除，与会话无关。

> 📖 **参考链接**：[ZooKeeper 官方文档 - Ephemeral Nodes](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#Ephemeral+Nodes) -- 临时节点生命周期与会话绑定机制

---

### 3. ZooKeeper 在 CAP 理论中选择了？（★★）

A. AP（可用性 + 分区容错性）
B. CP（一致性 + 分区容错性）
C. CA（一致性 + 可用性）
D. 三者兼顾

**答案：B**

**解析**：ZooKeeper 选择 CP 架构，基于 Zab 协议保证强一致性，通过过半机制保证分区容错性。代价是选举期间（约 200ms）集群不可用，过半节点故障时集群拒绝服务。Nacos 支持 AP/CP 模式切换，Ca 在分布式系统中不可能实现。

> 📖 **参考链接**：[ZooKeeper 官方文档 - Guarantees & Consistency](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#ch_zkGuarantees) -- ZooKeeper 一致性保证与 CAP 选择说明

---

### 4. ZooKeeper 的 Watcher 机制中，以下哪项描述是**正确**的？（★★）

A. Watcher 触发后会持续监听，不需要重新注册
B. Watcher 通知中包含变更后的节点数据
C. 同一客户端的 Watcher 事件按顺序串行处理
D. Watcher 可以在服务端持久化，客户端重启后仍有效

**答案：C**

**解析**：ZooKeeper 的 Watcher 特性：一次性触发（A 错误，需重新注册）；轻量级通知只含事件类型和路径不含数据（B 错误）；串行执行保证客户端事件处理顺序（C 正确）；Watcher 存储在服务端内存中，客户端重启后需要重新注册（D 错误）。

> 📖 **参考链接**：[ZooKeeper 官方文档 - Watches](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#ch_zkWatches) -- Watcher 一次性触发、串行执行、轻量级通知特性

---

### 5. ZAB 协议中，zxid 的高 32 位表示什么？（★★）

A. 事务计数器（counter）
B. 服务器 ID（myid）
C. 纪元号（epoch）
D. 客户端会话 ID

**答案：C**

**解析**：zxid 是 64 位整数，高 32 位为 epoch（纪元号），每次 Leader 选举递增，用于区分不同 Leader 任期；低 32 位为 counter（事务计数器），同一 epoch 内每个事务递增。myid 是服务器配置 ID，与 zxid 无关。

> 📖 **参考链接**：[ZooKeeper 官方文档 - zxid & Leader Election](https://zookeeper.apache.org/doc/current/zookeeperInternals.html#sc_leaderElection) -- zxid 结构（epoch + counter）与选举优先级

---

### 6. 关于 ZooKeeper 集群的过半机制，以下说法**错误**的是？（★★）

A. 5 节点集群可容忍 2 个节点故障
B. 事务提交需要过半 Follower 返回 ACK
C. 集群节点数建议为偶数，容错能力更强
D. Leader 选举需要获得超过半数投票

**答案：C**

**解析**：过半机制下，奇数节点更经济。4 节点（过半 3）容忍 1 个故障，与 3 节点（过半 2）容忍度相同，浪费 1 个节点。5 节点（过半 3）容忍 2 个故障。A、B、D 均为正确说法。

> 📖 **参考链接**：[ZooKeeper 官方文档 - Quorum Mechanism](https://zookeeper.apache.org/doc/current/zookeeperInternals.html#sc_leaderElection) -- 过半机制与奇数节点选型分析

---

### 7. 以下哪种场景**不适合**使用 ZooKeeper 实现？（★★）

A. 分布式配置管理
B. 分布式锁
C. 海量数据存储（TB 级）
D. Leader 选举

**答案：C**

**解析**：ZooKeeper 设计用于存储协调元数据，单个 ZNode 数据上限 1MB，所有数据存储在内存中，不适合海量数据存储。A（配置管理）、B（分布式锁）、D（Leader 选举）都是 ZooKeeper 的典型应用场景。

> 📖 **参考链接**：[ZooKeeper 官方文档 - Data Model & 1MB Limit](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#sc_zkDataModel_znodes) -- ZNode 数据存储限制与适用场景边界

---

### 8. ZooKeeper 集群中 Observer 角色的特点是？（★★）

A. 参与 Leader 选举和事务过半确认
B. 同步 Leader 数据，处理读请求，不参与投票
C. 处理所有写请求
D. 不存储任何数据

**答案：B**

**解析**：Observer 与 Follower 类似，同步 Leader 数据并响应读请求，但不参与 Leader 选举和事务过半确认。引入 Observer 可在不影响写性能的前提下扩展读能力。A 描述的是 Follower，C 描述的是 Leader，D 错误（Observer 存储完整数据）。

> 📖 **参考链接**：[ZooKeeper 官方文档 - Observers](https://zookeeper.apache.org/doc/current/zookeeperObservers.html) -- Observer 角色特点与扩展读能力

---

### 9. 关于 ZooKeeper 分布式锁，以下说法**正确**的是？（★★★）

A. 排他锁基于持久有序节点实现
B. 基于临时有序节点的锁是公平锁
C. ZooKeeper 锁的性能高于 Redis 锁
D. 客户端断开连接后，锁节点不会自动删除

**答案：B**

**解析**：基于临时有序节点实现的锁，序号最小的客户端获得锁，其他客户端监听前一个节点，保证了先到先得（公平锁）。A 错误（排他锁基于同名临时节点），C 错误（Redis 锁性能更高），D 错误（临时节点在会话超时后自动删除，自动释放锁）。

> 📖 **参考链接**：[ZooKeeper 官方文档 - Recipes: Locks](https://zookeeper.apache.org/doc/current/recipes.html#sc_recipes_Locks) -- 分布式锁与公平锁实现方案

---

### 10. ZooKeeper 崩溃恢复时，以下哪种数据同步策略用于全量同步？（★★★）

A. TRUNC
B. DIFF
C. SNAP
D. COMMIT

**答案：C**

**解析**：崩溃恢复时新 Leader 与 Follower 进行数据同步，三种策略：TRUNC（Follower zxid 更大，回退截断多余事务）、DIFF（Follower zxid 略小，逐条同步差异事务日志）、SNAP（Follower zxid 远小于 Leader，发送完整快照全量同步）。COMMIT 不是同步策略，是消息广播阶段的提交操作。

> 📖 **参考链接**：[ZooKeeper 官方文档 - Crash Recovery & Sync](https://zookeeper.apache.org/doc/current/zookeeperInternals.html#sc_recovery) -- 崩溃恢复 TRUNC/DIFF/SNAP 同步策略

---

## 二、简答题（8 题，每题 5 分，共 40 分）

### 1. 简述 ZooKeeper 的 Watcher 机制及其一次性特性。

**答**：Watcher 是 ZooKeeper 的事件监听机制，客户端在 ZNode 上注册 Watcher 后，当节点发生对应变化时服务端主动发送事件通知。

**一次性特性**：每个 Watcher 只触发一次，收到通知后自动失效。客户端需要在回调中重新注册 Watcher 才能继续监听。这种设计简化了服务端状态管理，但增加了客户端复杂度。

**Curator 的改进**：提供 NodeCache（监听单个节点）、PathChildrenCache（监听子节点）、TreeCache（监听节点及其子树）三种缓存，自动处理反复注册。

> **生活化类比：Watcher = 快递签收短信** —— 你网购后订阅了物流提醒（注册 Watcher），快递状态一变（节点数据变更），快递公司给你发一条短信（WatcherEvent 通知），告诉你"你的包裹状态更新了"，但短信里不会写包裹里装了啥（轻量级通知只含事件类型和路径，不含变更后数据），你得自己打开 App 查（客户端主动调 getData 拉取）。最关键的是，这条短信是一次性的——看一次就失效了（一次性触发），下次状态再变，想再收短信必须重新订阅物流（在回调里重新注册 Watcher）。Curator 的 NodeCache/TreeCache 就相当于"自动续订"，你订一次它就帮你一直盯着，不用每次手动重新订阅。

> 📖 **参考链接**：
> - [ZooKeeper 官方文档 - Watcher Mechanism](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#ch_zkWatches) -- Watcher 一次性触发、串行执行等特性
> - [ZooKeeper 官方文档 - Watcher Notification](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#sc_WatcherTypes) -- NodeCreated/NodeDeleted 等事件类型说明

---

### 2. 简述 ZooKeeper 中临时节点和持久节点的区别及各自适用场景。

**答**：

| 对比维度 | 临时节点 | 持久节点 |
|---------|---------|---------|
| 生命周期 | 与会话绑定，会话结束自动删除 | 显式删除前一直存在 |
| 创建命令 | `create -e /path data` | `create /path data` |
| 可拥有子节点 | 否 | 是 |
| 典型场景 | 服务注册、分布式锁、存活检测 | 配置信息、服务元数据 |

**应用场景**：临时节点适合与客户端生命周期绑定的场景（如服务注册发现），客户端下线后自动清理注册信息；持久节点适合存储不随客户端变化的元数据（如数据库连接配置）。

> **生活化类比：临时节点 vs 持久节点 = 酒店租客房 vs 自有业主房** —— 临时节点就像酒店的租客房：你办了入住（客户端建立会话），前台给你一间房（创建临时节点），你退房走人（会话结束），房间自动收回给酒店（节点自动删除），不用你操心打扫。这种房不能挂子房间（临时节点不能有子节点）。持久节点就像自有业主房：你买了房（创建持久节点），只要你不去卖掉（显式 delete），房子永远在你名下，哪怕你长期出差不在家（客户端断开），房子还在，还能装修出子房间（可以有子节点）。服务注册用租客房（服务下线自动注销），配置管理用业主房（配置持久保留）。

> 📖 **参考链接**：
> - [ZooKeeper 官方文档 - ZNode Types](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#sc_zkDataModel_znodes) -- 临时节点（EPHEMERAL）与持久节点（PERSISTENT）类型说明
> - [ZooKeeper 官方文档 - Ephemeral Nodes](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#Ephemeral+Nodes) -- 临时节点生命周期与会话绑定机制

---

### 3. 简述 ZooKeeper 的 ZAB 协议中消息广播的两阶段提交流程。

**答**：

**阶段一（Proposal + ACK）**：
1. Leader 收到客户端写请求，生成 Proposal（包含 zxid 和操作数据）。
2. Leader 将 Proposal 广播给所有 Follower。
3. Follower 收到 Proposal 后写入本地事务日志，返回 ACK 给 Leader。

**阶段二（Commit）**：
1. Leader 收到过半 Follower 的 ACK 后，发送 Commit 消息给所有 Follower。
2. Leader 和所有 Follower 将事务应用到内存数据树。
3. Leader 返回操作结果给客户端。

**与经典 2PC 的区别**：ZAB 协议支持流水线化（可连续发送多个 Proposal），自动选举新 Leader 避免阻塞，过半机制容忍少数节点故障。

> 📖 **参考链接**：
> - [ZooKeeper 官方文档 - Atomic Broadcast](https://zookeeper.apache.org/doc/current/zookeeperInternals.html#sc_atomicBroadcast) -- ZAB 消息广播两阶段提交（Proposal-ACK-Commit）流程
> - [ZooKeeper 官方文档 - Quorum & 2PC](https://zookeeper.apache.org/doc/current/zookeeperInternals.html#sc_leaderElection) -- 过半 ACK 提交与经典 2PC 的差异

---

### 4. 简述 ZooKeeper 集群的三种角色及其职责。

**答**：

| 角色 | 职责 | 参与选举 | 参与过半确认 |
|------|------|---------|------------|
| Leader | 唯一写处理器，广播 Proposal，协调事务提交 | 被选举 | 无需 |
| Follower | 参与选举，参与过半确认，同步数据，处理读请求 | 是 | 是 |
| Observer | 同步数据，处理读请求，不参与投票 | 否 | 否 |

**Observer 的引入原因**：随着集群规模增大，参与投票的节点增多会导致事务提交延迟增大。Observer 不参与投票，可在不影响写性能的前提下扩展读能力，也适合跨数据中心部署。

> 📖 **参考链接**：
> - [ZooKeeper 官方文档 - Observer Role](https://zookeeper.apache.org/doc/current/zookeeperObservers.html) -- Observer 角色职责与 peerType=observer 配置
> - [ZooKeeper 官方文档 - Cluster Roles](https://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_zkMulitserver) -- Leader/Follower/Observer 三种角色对比

---

### 5. 简述 ZooKeeper 如何避免脑裂问题。

**答**：

1. **过半机制**：任何决策需要超过半数节点同意。网络分区后，少数派无法凑够过半票数，自动退化为 LOOKING 状态并拒绝服务，不会出现两个 Leader 同时服务。

2. **epoch 机制**：每个 Leader 任期有唯一的递增 epoch 号（zxid 高 32 位）。网络恢复后，旧 Leader 发现 epoch 已落后，自动降级为 Follower 并同步新 Leader 的数据。

3. **Quorum 检查**：Follower 定期检查与 Leader 的连接，若心跳超时则发起重新选举，确保集群中只有一个有效 Leader。

> 📖 **参考链接**：
> - [ZooKeeper 官方文档 - Quorum & Split-Brain](https://zookeeper.apache.org/doc/current/zookeeperInternals.html#sc_leaderElection) -- 过半机制如何避免脑裂与网络分区
> - [ZooKeeper 官方文档 - Epoch Mechanism](https://zookeeper.apache.org/doc/current/zookeeperInternals.html#sc_atomicBroadcast) -- epoch 纪元号防止旧 Leader 脑裂

---

### 6. 简述 ZooKeeper 的本地文件存储架构及重启恢复流程。

**答**：

**存储架构**：
- **内存数据树（DataTree）**：存储所有 ZNode 的完整数据、Stat 元数据、Watcher 注册表和 ACL 列表，提供快速读写。
- **事务日志（TxnLog）**：预写日志（WAL），每次写操作先写入日志文件（`log.<zxid>`）并 fsync 落盘，再修改内存。
- **快照（Snapshot）**：事务日志累积超过 `snapCount`（默认 100000）条时异步生成完整序列化副本（`snapshot.<zxid>`）。

**重启恢复流程**：
1. 加载最新的快照文件，恢复基础数据状态。
2. 按序回放快照之后的所有事务日志，恢复完整状态。
3. 这种设计既保证数据不丢失（WAL），又避免每次启动从头回放海量日志（快照加速）。

> 📖 **参考链接**：
> - [ZooKeeper 官方文档 - Data Storage](https://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_storage) -- 事务日志与快照存储配置说明
> - [ZooKeeper 官方文档 - Autopurge](https://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_maintenance) -- autopurge.snapRetainCount / purgeInterval 自动清理

---

### 7. 简述 ZooKeeper 分布式锁与 Redis 分布式锁的优缺点对比。

**答**：

| 维度 | ZooKeeper 锁 | Redis 锁（Redisson） |
|------|-------------|---------------------|
| 一致性 | 强一致（CP 架构） | 弱一致（AP 架构，主从切换可能丢锁） |
| 性能 | 中等 | 高 |
| 公平锁 | 原生支持（临时有序节点） | 支持 |
| 自动释放 | 会话超时自动删除临时节点 | 看门狗续期 + TTL 过期 |
| 惊群效应 | 公平锁无惊群，非公平锁有 | 均有 |
| 适用场景 | 要求强一致性的锁场景 | 高并发、可容忍短暂不一致 |

**选型建议**：对一致性要求极高（如金融交易）选 ZooKeeper；对性能要求极高（如秒杀限流）选 Redis。

> 📖 **参考链接**：
> - [ZooKeeper 官方文档 - Recipes: Locks](https://zookeeper.apache.org/doc/current/recipes.html#sc_recipes_Locks) -- ZooKeeper 分布式锁官方实现方案
> - [ZooKeeper 官方文档 - Curator InterProcessMutex](https://curator.apache.org/curator-recipes/shared-reentrant-lock.html) -- Curator 可重入锁实现与 Redisson 对比

---

### 8. 简述 ZooKeeper 中 Stat 结构体的版本号机制及其乐观锁实现。

**答**：

**三个版本号**：
- `version`：数据版本号，每次 `setData` 成功后递增。
- `cversion`：子节点版本号，子节点增删时递增。
- `aversion`：ACL 版本号，ACL 修改时递增。

**乐观锁实现**：
1. 读取节点数据时同时获取当前 `version` 值。
2. 更新数据时传入期望的 `version` 值。
3. 服务端比较期望版本号与当前版本号：
   - 匹配则更新成功，版本号递增。
   - 不匹配则抛出 `BadVersionException`，客户端重新读取版本号并重试。

**作用**：保证并发更新时的数据一致性，避免丢失更新（Lost Update），类似于数据库乐观锁机制。

> 📖 **参考链接**：
> - [ZooKeeper 官方文档 - Stat Structure](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#sc_zkStatStructure) -- Stat 结构体 version/cversion/aversion 字段说明
> - [ZooKeeper 官方文档 - Version & CAS](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#zk) -- 基于 version 的乐观锁与 BadVersionException 处理

---

## 三、场景设计题（2 题，每题 10 分，共 20 分）

### 1. 分布式锁系统设计

**场景**：某电商系统需要在分布式环境下实现库存扣减的互斥访问。要求支持公平锁（先到先得）、锁超时自动释放、高可用（集群故障时锁不丢失）。请设计基于 ZooKeeper 的分布式锁方案。

**参考答案**：

**方案设计**：

采用基于临时有序节点的公平锁方案，利用 Curator 框架的 `InterProcessSemaphoreMutex` 实现。

**锁路径设计**：
```
/locks/inventory/{productId}/
    ├── _c_0000000001  （客户端 A 创建，序号最小，获得锁）
    ├── _c_0000000002  （客户端 B 创建，监听 _c_0000000001）
    └── _c_0000000003  （客户端 C 创建，监听 _c_0000000002）
```

**核心代码**：

```java
@Service
public class InventoryLockService {
    @Autowired
    private CuratorFramework client;

    private final Map<String, InterProcessSemaphoreMutex> lockCache = new ConcurrentHashMap<>();

    public boolean executeWithLock(String productId, Runnable task) {
        String lockPath = "/locks/inventory/" + productId;
        InterProcessSemaphoreMutex lock = lockCache.computeIfAbsent(
            lockPath,
            k -> new InterProcessSemaphoreMutex(client, lockPath)
        );

        try {
            // 尝试获取锁，最多等待 5 秒
            if (lock.acquire(5, TimeUnit.SECONDS)) {
                try {
                    task.run();
                    return true;
                } finally {
                    lock.release();
                }
            }
            return false;
        } catch (Exception e) {
            log.error("获取分布式锁失败: {}", lockPath, e);
            return false;
        }
    }
}
```

**公平性保证**：所有客户端在 `/locks/inventory/{productId}/` 下创建临时有序节点，序号最小的客户端获得锁。其他客户端监听前一个节点的删除事件，释放锁时只有下一个客户端被唤醒，保证先到先得。

**超时自动释放**：客户端宕机或网络中断，会话超时后临时节点自动删除，锁自动释放，避免死锁。

**高可用保证**：ZooKeeper 集群 5 节点部署，基于过半机制，容忍 2 个节点故障。临时节点与会话绑定，即使 Leader 切换也不影响已有锁。

---

### 2. 配置中心系统设计

**场景**：某微服务系统有 20+ 个服务实例，需要实现配置集中管理。要求：配置变更实时推送、支持配置回滚、配置变更审计、对业务代码侵入小。请设计基于 ZooKeeper 的配置中心方案。

**参考答案**：

**整体架构**：

```
配置管理后台（Web 界面）
    |
    v
ZooKeeper 集群（5 节点，存储配置）
    |
    +-- /config/common/          （公共配置）
    |   +-- timeout              = "3000"
    |   +-- log.level            = "INFO"
    |
    +-- /config/order-service/   （订单服务配置）
    |   +-- db.url               = "jdbc:mysql://..."
    |   +-- db.pool.size         = "20"
    |
    +-- /config/user-service/    （用户服务配置）
        +-- db.url               = "jdbc:mysql://..."
        +-- redis.host            = "127.0.0.1"
```

**配置存储方案**：

```
/config
├── /common/{key}              -- 公共配置，所有服务共享
├── /{serviceName}/{key}       -- 服务专属配置，覆盖公共配置
├── /history/{serviceName}/{key}/{version} -- 配置历史版本（持久节点）
└── /audit/{timestamp}         -- 变更审计日志
```

**核心代码**：

```java
// 配置变更监听器接口
@FunctionalInterface
public interface ConfigChangeListener {
    void onChange(String path, String value);
}
```

```java
@Component
public class ConfigCenter {
    @Autowired
    private CuratorFramework client;

    private final Map<String, String> configCache = new ConcurrentHashMap<>();
    private final Map<String, List<ConfigChangeListener>> listeners = new ConcurrentHashMap<>();

    @PostConstruct
    public void init() throws Exception {
        // 确保根节点存在
        if (client.checkExists().forPath("/config") == null) {
            client.create().creatingParentsIfNeeded().forPath("/config");
        }

        // 监听所有配置变更
        TreeCache treeCache = new TreeCache(client, "/config");
        treeCache.getListenable().addListener((curatorClient, event) -> {
            if (event.getData() != null && event.getType() == TreeCacheEvent.Type.NODE_UPDATED) {
                String path = event.getData().getPath();
                String value = new String(event.getData().getData(), StandardCharsets.UTF_8);

                // 更新本地缓存
                configCache.put(path, value);

                // 记录历史版本
                saveHistory(path, value);

                // 通知监听器
                notifyListeners(path, value);
            }
        });
        treeCache.start();
    }

    // 发布配置
    public void publishConfig(String path, String value, String operator) throws Exception {
        String fullPath = "/config" + path;
        // 检查路径是否存在，不存在则创建，避免 setData 在节点不存在时抛异常
        if (client.checkExists().forPath(fullPath) == null) {
            client.create().creatingParentsIfNeeded().forPath(fullPath, value.getBytes(StandardCharsets.UTF_8));
        } else {
            client.setData().forPath(fullPath, value.getBytes(StandardCharsets.UTF_8));
        }

        // 记录审计日志
        String auditPath = "/config/audit/" + System.currentTimeMillis();
        String auditData = String.format("{\"path\":\"%s\",\"operator\":\"%s\",\"time\":%d}",
                path, operator, System.currentTimeMillis());
        client.create().creatingParentsIfNeeded().forPath(auditPath, auditData.getBytes());
    }

    // 回滚配置到指定版本
    public void rollback(String path, int targetVersion) throws Exception {
        String historyPath = "/config/history" + path + "/" + targetVersion;
        byte[] data = client.getData().forPath(historyPath);
        String value = new String(data, StandardCharsets.UTF_8);
        publishConfig(path, value, "ROLLBACK");
    }

    // 注册配置变更监听器
    public void addListener(String path, ConfigChangeListener listener) {
        listeners.computeIfAbsent(path, k -> new CopyOnWriteArrayList<>()).add(listener);
    }

    // 保存历史版本
    private void saveHistory(String path, String value) throws Exception {
        String historyPath = "/config/history" + path;
        if (client.checkExists().forPath(historyPath) == null) {
            client.create().creatingParentsIfNeeded().forPath(historyPath);
        }
        // 创建持久有序节点保存历史版本
        client.create()
            .withMode(CreateMode.PERSISTENT_SEQUENTIAL)
            .forPath(historyPath + "/", value.getBytes(StandardCharsets.UTF_8));
    }

    private void notifyListeners(String path, String value) {
        List<ConfigChangeListener> list = listeners.get(path);
        if (list != null) {
            list.forEach(l -> l.onChange(path, value));
        }
    }
}
```

**配置优先级**：服务专属配置覆盖公共配置。读取时先查 `/config/{serviceName}/{key}`，若不存在则查 `/config/common/{key}`。

**实时推送**：基于 TreeCache 监听整个 `/config` 子树，配置变更时自动通知所有监听的服务实例，实现准实时推送。

**配置回滚**：每次配置变更时在 `/config/history/` 下创建持久有序节点保存历史版本，回滚时读取指定版本数据并重新发布。

**审计日志**：每次配置变更在 `/config/audit/` 下创建带时间戳的节点，记录操作路径、操作人和时间，便于审计追溯。

**低侵入性**：业务代码只需注入 ConfigCenter 并通过 `getConfig()` 读取配置，或通过 `addListener()` 注册变更回调，不需要修改业务逻辑。

---

> **学习导航**：
> - 返回 [学习路线总览](../../README.md)
> - 本模块其他文件：[01-ZooKeeper核心原理](./01-Zookeeper核心原理.md) | [02-ZooKeeper集群与应用场景](./02-Zookeeper集群与应用场景.md)