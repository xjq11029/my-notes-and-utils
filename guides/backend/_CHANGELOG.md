# Java 后端资料库变更日志

> 记录 `guides/backend/` 笔面试资料库的版本演进（内容补充、结构变更、索引修正），便于在同一处追溯整个体系的变更。
> 下表按**日期 + 版本**升序排列（最旧在上）。版本规则：新增模块 / 新增原理文件或题集 / 新增章节 → 次版本号 +1；扩充条目、修订措辞、修正错误 → 修订号 +1。
> 变更类别（新增 / 扩充 / 修复 / 修订）以摘要正文的动词内联表达，不单设分类列；「来源项目」列为该次变更的触发来源。

| 版本 | 日期 | 变更摘要 | 来源项目 |
|---|---|---|---|
| v1.0.0 | 2026-09-17 | 新增本变更日志机制，并完成首轮内容补齐与一致性修复。**新增文件（8 个）**：`01-java-basics/jvm-juc/19-JMM与happens-before.md`（1365 行，JMM 抽象模型与 8 种原子操作、三类重排序与 as-if-serial、happens-before 八条规则及与「时间先后」的辨析、四种内存屏障、volatile/synchronized/final 内存语义、DCL 重排序推导）及配套导览；`mq/kafka/Kafka笔面试题集.md`（592 行，23 题）与 `mq/rabbitmq/RabbitMQ笔面试题集.md`（723 行，23 题）及各自导览——此前 Kafka、RabbitMQ 均无独立题集；`python-core/02-Python笔面试题集.md`（884 行，32 题）及配套导览——此前 python-core 无独立题集。**新增章节（并入既有文件）**：`jvm-juc/14-JVM原理与调优.md` 新增 3.4「GC 日志解读与线上 GC/OOM 排查」与 3.5「Arthas 实战诊断」（496→855 行）；`mq/03-消息队列笔面试题集.md` 新增「消息积压治理专题」（扩容分区 / 转存新 Topic / 丢弃 三级处置 + 三款 MQ 差异）；`docker-k8s/02-Kubernetes核心概念.md` 新增 3.4「CI/CD 流水线集成」；`mysql-advanced/06-MySQL深度优化.md` 新增 2.5「间隙锁与 Next-Key Lock」；以上四处均同步更新对应 `-导览.md`。**扩充**：`python-core/综合场景.md` 场景数 1→3（462→950 行）、`git/综合场景.md` 场景数 2→3（216→530 行）；17 个模块的 `常见错误汇总.md` 扩充条目（如 jvm-juc 21→43 条、docker-k8s 10→32 条、mysql-jdbc 16→29 条、clickhouse 9→22 条、git 10→27 条）；8 个模块的 `概念对比速查.md` 扩充主题（如 jvm-juc 3→6、clickhouse 2→5、elasticsearch 3→7、nginx 3→7、langchain-rag 3→7）。**一致性修复**：修复 `langchain-rag/04-Python与AI智能体笔面试题集.md` 指向不存在 `./README.md` 的死链、`mysql-jdbc/综合场景.md` 因小节重编号而失效的数据类型锚点；`guides/backend/README.md` 补「跨目录连续编号」说明；同步 `README.md`、`知识导览.md`、`docs/TOC.md` 与根 `AGENTS.md` 的文件数与结构登记。修订后全库共 258 个文件，2084 条本地相对链接零失效、锚点零失效。 | 需求创建（内容缺口排查与补齐） |
