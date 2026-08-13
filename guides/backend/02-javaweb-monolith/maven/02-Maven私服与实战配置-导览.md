# Maven 私服与实战配置 导览

> 定位：五维框架浓缩提炼 02-Maven私服与实战配置.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-Maven私服与实战配置.md)。
> 前置知识：无

---

## 一、核心概念

### 1.1 仓库体系

| 维度 | 内容 |
|------|------|
| 是什么 | Maven 构件按"就近取用"在本地仓库、远程仓库、中央仓库间流转的三级仓库体系。 |
| 能做什么 | 本地缓存加速；远程提供下载；中央仓库为官方公共源；私服代理并托管内部构件。 |
| 怎么用 | 默认本地 `~/.m2/repository`，中央 `repo.maven.apache.org`。 |
| 原理和工作流程 | 构件查找顺序为本地仓库 → settings.xml 的 mirror → pom.xml 的 repositories → 中央仓库；本地未命中即向远程请求，下载后缓存到本地；引入私服后通常将 group 地址配为远程仓库，私服内部代理中央仓库并缓存，同时托管内部构件。 |
| 缺点 | 本地缓存可能过期致版本不一致；纯离线时缺构件即失败；远程链路故障导致构建中断；多级仓库查找链路复杂。 |

### 1.2 settings.xml 配置详解

| 维度 | 内容 |
|------|------|
| 是什么 | Maven 用户级/全局级配置文件，独立于项目，配置本地仓库、认证、镜像、profile 等。 |
| 能做什么 | 设本地仓库路径；配仓库认证 servers；重定向镜像 mirrors；定义环境 profile 与激活项；配 HTTP 代理。 |
| 怎么用 | 全局 `$MAVEN_HOME/conf/settings.xml`，用户 `~/.m2/settings.xml`（优先级更高）。 |
| 原理和工作流程 | settings.xml 元素 localRepository 指定本地缓存路径；servers 以 id 关联仓库认证；mirrors 按 mirrorOf 匹配仓库并重定向请求；profiles 定义 repositories 与 properties，activeProfiles 默认激活；用户配置覆盖全局配置。servers 的 id 必须与 pom distributionManagement 的 repository id、mirrors 引用 id 一致方能匹配认证。 |
| 缺点 | 两处配置优先级易混淆；id 不匹配导致 401；明文密码泄露风险；XML 冗长。 |

---

## 二、底层原理

### 2.1 镜像机制

| 维度 | 内容 |
|------|------|
| 是什么 | mirror 把对某仓库（按 id 匹配）的请求整体重定向到镜像地址的机制。 |
| 能做什么 | 用国内镜像加速中央仓库；按 mirrorOf 控制匹配范围；支持 *、external:*、central、列举、排除等取值。 |
| 怎么用 | `<mirror><mirrorOf>central</mirrorOf><url>https://maven.aliyun.com/repository/public</url></mirror>` |
| 原理和工作流程 | Maven 解析 mirrorOf 决定拦截范围：* 拦截所有仓库，central 仅中央仓库，external:* 排除本地与 file 协议，`*,!repo1` 排除指定仓库；匹配的仓库请求被重定向到 mirror url，被镜像仓库不再被直接访问。 |
| 缺点 | mirrorOf=* 会拦截私服导致内部构件拉取失败；镜像源不同步致版本缺失；多镜像冲突；调试困难。 |

### 2.2 私服架构（Nexus / Artifactory）

| 维度 | 内容 |
|------|------|
| 是什么 | 部署在企业内部的仓库代理服务器，常见实现为 Sonatype Nexus 与 JFrog Artifactory。 |
| 能做什么 | 加速下载；统一内部构件发布；节省公网带宽；聚合多仓库对外暴露统一入口。 |
| 怎么用 | Nexus 维护 proxy、hosted、group 三类仓库，日常配 group 地址。 |
| 原理和工作流程 | proxy 代理远程仓库并缓存构件，请求先查本地缓存未命中再向远端拉取落盘；hosted 托管内部构件按 releases（不可覆盖）与 snapshots（可覆盖留历史）分开；group 聚合多个 proxy 与 hosted 对外暴露统一地址，按顺序查找。客户端只配 group 即可同时访问公共与内部构件。 |
| 缺点 | 私服自身需运维与备份；缓存策略不当致版本滞后；group 顺序配错影响查找；单点故障影响全局构建。 |

### 2.3 发布流程

| 维度 | 内容 |
|------|------|
| 是什么 | 构件发布对应 default 生命周期 deploy 阶段，把打包产物上传到远程仓库的流程。 |
| 能做什么 | 按 SNAPSHOT/RELEASE 分别上传；RELEASE 不可覆盖保证正式版不变；SNAPSHOT 保留历史构建。 |
| 怎么用 | pom 配 distributionManagement，`mvn clean deploy`。 |
| 原理和工作流程 | deploy 在 install 之后执行，由 maven-deploy-plugin 按 version 判断：含 -SNAPSHOT 上传到 snapshotRepository，否则上传到 repository；Nexus 中 releases 仓库拒绝同版本号覆盖以保正式版不可变，snapshots 仓库允许覆盖并为每次上传生成带时间戳子版本保留历史。settings servers 需有同名 id 认证且账号有写入权限。 |
| 缺点 | releases 重复上传被拒需升版本；SNAPSHOT 不固定致生产不确定；认证 id 不匹配致 401；网络故障致 deploy 失败需重试。 |

---

## 三、实战应用

### 3.1 Nexus 私服搭建步骤

| 维度 | 内容 |
|------|------|
| 是什么 | 以 Docker 部署 Nexus3 并配置 proxy/hosted/group 仓库的搭建步骤。 |
| 能做什么 | 容器化部署 Nexus；创建 releases/snapshots hosted 与 central proxy；聚合为 group 统一入口。 |
| 怎么用 | `docker run -d --name nexus -p 8081:8081 -v nexus-data:/nexus-data sonatype/nexus3` |
| 原理和工作流程 | 容器启动后用 /nexus-data/admin.password 初始密码登录修改；按 version policy 创建 hosted（Release/Snapshot）分别存正式版与快照；创建 proxy 代理 https://repo1.maven.org/maven2/；创建 group 按顺序加入 central、releases、snapshots，顺序决定查找顺序，hosted 放前优先命中内部构件。 |
| 缺点 | 首次启动慢；初始密码位于容器内需进入读取；仓库顺序配错影响命中率；数据卷需备份。 |

### 3.2 settings.xml 完整配置示例

| 维度 | 内容 |
|------|------|
| 是什么 | 兼顾公网加速与私服发布的完整 settings.xml 配置实践。 |
| 能做什么 | 本地仓库指向 SSD；servers 配私服认证（密码走环境变量）；mirrors 仅镜像 central 不影响私服；profile 配 group 仓库与 updatePolicy。 |
| 怎么用 | servers id 与 distributionManagement id 对应；mirrorOf=central；activeProfiles 激活 nexus。 |
| 原理和工作流程 | localRepository 指定缓存路径；servers 用 ${env.NEXUS_PWD} 从环境变量读取密码避免明文；mirrors 仅 mirrorOf=central 替换中央仓库，私服 repository 不受影响；profile 的 repositories 配 group 地址，snapshots 配 updatePolicy=always 每次构建检查更新以拉取最新快照；activeProfiles 默认激活。 |
| 缺点 | 配置项繁多易错；环境变量未注入致认证失败；updatePolicy=always 增加网络开销；多环境需多 profile。 |

### 3.3 pom.xml 发布配置

| 维度 | 内容 |
|------|------|
| 是什么 | distributionManagement 声明发布目标仓库的 pom 配置与发布命令。 |
| 能做什么 | 声明 repository 与 snapshotRepository；按版本自动路由上传；执行 mvn deploy 发布。 |
| 怎么用 | `<distributionManagement><repository>..</repository><snapshotRepository>..</snapshotRepository></distributionManagement>` + `mvn clean deploy` |
| 原理和工作流程 | distributionManagement 的 repository 与 snapshotRepository 分别指定 RELEASE 与 SNAPSHOT 上传目标；maven-deploy-plugin 按 version 含 -SNAPSHOT 与否选择目标；settings servers 中需有与 repository id 同名认证条目，账号需有对应 hosted 仓库写入权限，否则 401。 |
| 缺点 | id 不匹配致认证失败；账号权限不足致 403；RELEASE 重复上传被拒；网络不稳致上传中断。 |

### 3.4 多环境 Profile 隔离

| 维度 | 内容 |
|------|------|
| 是什么 | 用 profiles + resource filtering 实现 dev/test/prod 多环境配置隔离的实践。 |
| 能做什么 | 定义多环境 profile；用 properties 设环境标识；resource filtering 替换占位符；命令行 -P 激活。 |
| 怎么用 | pom 定义 profiles 与 filtering，`mvn clean package -P prod`。 |
| 原理和工作流程 | 各 profile 通过 properties 设 env=dev/prod 等；build 对资源目录开启 filtering=true，并用 filters 引用 application-${env}.yml；构建时 -P prod 激活对应 profile，占位符被替换为该环境值。Spring Boot 项目用 spring.profiles.active 配合 @env@ 占位符（starter parent 默认用 @..@ 而非 ${}），避免与 Spring 占位符冲突。 |
| 缺点 | profile 组合复杂；占位符冲突（${} 与 Spring）；filtering 性能开销；环境配置散落多文件维护成本高。 |

---

## 四、常见面试题

### 1. Maven 的仓库体系是怎样的？本地仓库、私服、中央仓库的关系？

| 维度 | 内容 |
|------|------|
| 是什么 | 本地、远程（私服/中央）三级仓库及查找关系。 |
| 能做什么 | 本地缓存加速；私服代理中央并托管内部构件；统一对外入口。 |
| 怎么用 | 本地 `~/.m2/repository`，group 地址配为远程仓库。 |
| 原理和工作流程 | 查找顺序为本地仓库 → settings mirror → pom repositories → 中央仓库；本地未命中向远程请求并缓存。引入私服后通常将 group 地址配为远程仓库，私服内部 proxy 代理中央并缓存构件，hosted 托管企业内部构件，group 聚合统一入口。 |
| 缺点 | 本地缓存过期；离线缺构件失败；多级链路复杂；私服单点故障。 |

### 2. settings.xml 中 mirror 的 mirrorOf 有哪些取值？配成 * 会有什么问题？

| 维度 | 内容 |
|------|------|
| 是什么 | mirrorOf 控制镜像匹配范围的取值集合及配 * 的陷阱。 |
| 能做什么 | 取值含 *、external:*、central、列举、`*,!repo1`；限定镜像范围避免误拦截私服。 |
| 怎么用 | `<mirrorOf>central</mirrorOf>` 或 `<mirrorOf>*,!nexus-public</mirrorOf>` |
| 原理和工作流程 | mirrorOf 决定拦截范围：* 拦截所有仓库含私服，central 仅中央，external:* 排除本地与 file，`*,!repo1` 排除指定。配 * 会拦截 pom 中自定义私服 repository 请求并重定向到镜像，致内部构件拉取失败。正确做法限定 central 或排除私服。 |
| 缺点 | * 易误拦截私服；镜像源不同步；多镜像冲突；调试不直观。 |

### 3. Nexus 的三种仓库类型分别是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | Nexus 维护的 proxy、hosted、group 三类仓库。 |
| 能做什么 | proxy 代理远程并缓存；hosted 托管内部构件分 releases/snapshots；group 聚合统一入口。 |
| 怎么用 | 日常只配 group 地址即可访问公共与内部构件。 |
| 原理和工作流程 | proxy 代理远程仓库（如 Maven 中央），请求先查缓存未命中再拉取落盘；hosted 托管企业内部构件，releases 禁止覆盖保正式版不变，snapshots 允许覆盖并生成时间戳子版本保留历史；group 聚合多个 proxy 与 hosted 对外暴露统一地址，按顺序查找。 |
| 缺点 | 缓存策略致版本滞后；group 顺序影响命中；hosted releases 不可覆盖需升版本；私服需运维。 |

### 4. mvn deploy 的执行流程？RELEASE 与 SNAPSHOT 在私服中存储有何不同？

| 维度 | 内容 |
|------|------|
| 是什么 | deploy 阶段执行流程及 RELEASE/SNAPSHOT 在 Nexus 中的存储差异。 |
| 能做什么 | 把产物上传到 distributionManagement 配置的远程仓库；按版本路由；RELEASE 不可覆盖、SNAPSHOT 留历史。 |
| 怎么用 | `mvn clean deploy` |
| 原理和工作流程 | deploy 对应 default 生命周期 deploy 阶段，由 maven-deploy-plugin 在 install 之后执行，按 version 含 -SNAPSHOT 上传到 snapshotRepository 否则 repository。Nexus 中 releases 仓库禁止同版本号覆盖保证正式版不可变；snapshots 仓库允许覆盖并为每次上传生成带时间戳子版本保留历史。settings servers 需同名 id 认证。 |
| 缺点 | releases 重复上传被拒；SNAPSHOT 不固定致生产不确定；认证 id 不匹配致 401；上传中断需重试。 |

### 5. 多环境配置如何在 Maven 中实现？

| 维度 | 内容 |
|------|------|
| 是什么 | 用 profiles + resource filtering 实现多环境配置隔离的方案。 |
| 能做什么 | 定义多环境 profile；properties 设环境标识；filtering 替换占位符；-P 激活。 |
| 怎么用 | pom 配 profiles 与 filtering，`mvn package -P prod`。 |
| 原理和工作流程 | profiles 定义 dev/test/prod，每个 profile 用 properties 设 env=prod 等；build 对资源目录 filtering=true 并用 filters 引用 application-${env}.yml；构建时 -P prod 激活，占位符替换为对应环境值。Spring Boot 结合 spring.profiles.active 与 @env@ 占位符（starter parent 默认 @..@）避免与 Spring ${} 冲突。 |
| 缺点 | profile 组合复杂；占位符冲突；filtering 性能开销；多文件维护成本高。 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | Maven 私服与配置常见错误现象、根因与修复方案汇总。 |
| 能做什么 | 识别 mirrorOf=* 误配、servers id 不匹配、releases 重复上传、SNAPSHOT 不更新、离线构建失败、密码明文等陷阱并给出修复。 |
| 怎么用 | mirrorOf 限 central 或排除私服；id 保持一致；releases 升版本或开 Allow Redeploy；updatePolicy=always 或 -U；offline=false；密码走环境变量或加密。 |
| 原理和工作流程 | 各陷阱根因分别源于 mirror 拦截范围、servers id 关联认证、releases 不可覆盖策略、SNAPSHOT 缓存与 updatePolicy、offline 标志、明文存储。修复对应为限定 mirrorOf、统一 id、升版本或开启覆盖、强制更新、关闭 offline、环境变量或 settings security 加密。 |
| 缺点 | 清单覆盖有限；部分修复影响全局需回归；Allow Redeploy 破坏不可变语义；加密配置复杂。 |

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./02-Maven私服与实战配置.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
