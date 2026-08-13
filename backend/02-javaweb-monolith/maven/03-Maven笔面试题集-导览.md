# Maven 笔面试题集 导览

> 定位：五维框架浓缩提炼 03-Maven笔面试题集.md 全部内容小节，快速查阅与复习。
> 用法：每道题目提取所考知识点生成纵向表格，需要查看原题与解析时跳转 [原文](./03-Maven笔面试题集.md)。
> 前置知识：无

---

## 一、选择题（10 题，每题附解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 覆盖 Maven 核心原理与依赖管理的 10 道单选题题型分类。 |
| 能做什么 | 考查 GAV 坐标、modelVersion、packaging、约定目录、scope、依赖冲突规则、生命周期顺序、Nexus 仓库类型、mirrorOf 陷阱、import scope 等基础与中高档知识点。 |
| 怎么用 | 单选作答后对照解析，定位薄弱点回查导览。 |
| 原理和工作流程 | 以四选一形式聚焦单一知识点辨析，解析给出正确项并解释错误项错因，覆盖基础至拔高难度梯度。 |
| 缺点 | 单选无法考查综合应用；仅考辨析不考实操；题量有限覆盖不全。 |

### 1. ★ Maven 中用于唯一定位一个构件（artifact）的三元组坐标是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 唯一定位 Maven 构件的 GAV 三元组坐标。 |
| 能做什么 | 精确定位依赖；区分组织、模块、版本；支撑仓库目录结构与解析。 |
| 怎么用 | `<groupId>..</groupId><artifactId>..</artifactId><version>..</version>` |
| 原理和工作流程 | groupId 为组织反向域名，artifactId 为模块名，version 为版本号，三者组合唯一定位构件；packaging 是打包类型、scope 是依赖范围，均非定位坐标。Maven 据此在本地仓库按 groupId/artifactId/version 目录定位 jar。 |
| 缺点 | 坐标与产物无强制校验存在顶替风险；版本命名混乱难辨稳定性。 |

### 2. ★ pom.xml 中 modelVersion 元素的固定取值是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | POM 模型版本号 modelVersion 的固定取值。 |
| 能做什么 | 标识 POM 模型版本；与 Java 版本无关；Maven 3/4 早期沿用。 |
| 怎么用 | `<modelVersion>4.0.0</modelVersion>` |
| 原理和工作流程 | modelVersion 表示 POM 模型版本，当前固定为 4.0.0，与 Java 版本无关；Maven 3 与 Maven 4 早期版本仍使用 4.0.0。 |
| 缺点 | 取值固定缺乏灵活性；新手易与 Java 版本混淆。 |

### 3. ★ Maven 默认的打包类型（packaging）是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | packaging 元素的默认取值。 |
| 能做什么 | 决定打包器选择；jar/war/pom/ear 区分；不显式声明即 jar。 |
| 怎么用 | 不声明时默认 jar，Web 应用显式 `<packaging>war</packaging>`。 |
| 原理和工作流程 | packaging 默认值为 jar；war 用于 Web 应用，pom 用于多模块父项目或 BOM，ear 用于企业级应用包。不显式声明 packaging 时打包结果为 jar，对应 maven-jar-plugin。 |
| 缺点 | 默认值隐式不透明；war/pom/ear 需显式声明易遗漏。 |

### 4. ★ 按照 Maven 约定优于配置原则，项目主源码应放在（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Maven 约定的主源码目录。 |
| 能做什么 | 主源码 src/main/java；测试 src/test/java；资源 src/main/resources；遵循约定免配置路径。 |
| 怎么用 | 源码放 `src/main/java`。 |
| 原理和工作流程 | Maven 约定主源码位于 src/main/java，编译输出到 target/classes；测试源码位于 src/test/java 编译到 target/test-classes；资源文件位于 src/main/resources。超级 POM 定义这些默认路径，遵循约定即无需在 pom.xml 显式声明源码路径。 |
| 缺点 | 约定隐式；偏离约定需额外配置；新手不知为何如此。 |

### 5. ★★ 下列依赖中，scope 应配置为 test 的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | 仅测试时使用应配 test scope 的依赖识别。 |
| 能做什么 | 区分 compile/test/provided/runtime 适用场景；JUnit 配 test 不打包。 |
| 怎么用 | JUnit `<scope>test</scope>`，Servlet API `<scope>provided</scope>`，JDBC `<scope>runtime</scope>`。 |
| 原理和工作流程 | JUnit 仅测试时使用配 test，不打包进产物；spring-boot-starter-web 是 compile；Servlet API 由容器提供配 provided；JDBC 驱动运行时才需要配 runtime。test 仅测试 classpath 不参与主编译不打包。 |
| 缺点 | scope 误配致打包膨胀或运行缺类；需理解各 scope classpath 差异。 |

### 6. ★★ 当项目中存在同一构件的多个版本时，Maven 依赖冲突的第一裁决规则是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Maven 依赖冲突的第一裁决规则。 |
| 能做什么 | 最短路径优先选定版本；直接声明必胜；路径相同时才用声明顺序。 |
| 怎么用 | 直接声明依赖（路径长度 1）强制指定版本。 |
| 原理和工作流程 | Maven 先按最短路径优先裁决，依赖树中离当前项目越近的版本胜出；当路径长度相同时才按声明顺序优先，pom.xml 中先声明的版本生效。版本号大小不影响裁决结果。 |
| 缺点 | 生效版本常非预期致 NoSuchMethodError；规则隐式难直觉判断。 |

### 7. ★★ 以下 default 生命周期阶段，执行顺序正确的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | default 生命周期关键阶段的正确执行顺序。 |
| 能做什么 | 校验→编译→测试→打包→校验→安装→发布；执行某阶段触发其前所有阶段。 |
| 怎么用 | `mvn package` 会触发 compile 与 test。 |
| 原理和工作流程 | default 生命周期关键阶段顺序为 validate → compile → test → package → verify → install → deploy。执行某阶段时其前所有阶段依次执行，因此 test 在 compile 之后、package 之前。 |
| 缺点 | 阶段顺序固定缺乏灵活性；跨生命周期组合需理解触发顺序。 |

### 8. ★★ Nexus 中用于聚合多个仓库、对外暴露统一访问地址的仓库类型是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | Nexus 中聚合多仓库对外暴露统一地址的 group 仓库类型。 |
| 能做什么 | 聚合 proxy 与 hosted；对外统一入口；按顺序查找。 |
| 怎么用 | 客户端只配 group 地址即可访问公共与内部构件。 |
| 原理和工作流程 | group 仓库把多个 proxy 和 hosted 仓库聚合为一个统一入口，客户端只需配置该地址即可同时访问公共构件与内部构件。proxy 代理远程仓库，hosted 托管内部构件，virtual 为兼容旧格式。 |
| 缺点 | group 顺序配错影响命中；聚合多仓库缓存策略复杂。 |

### 9. ★★★ settings.xml 中 mirror 的 mirrorOf 配置为 * 会带来的问题是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | mirrorOf 配 * 导致私服内部构件拉取失败的陷阱。 |
| 能做什么 | 识别 * 拦截所有仓库含私服的风险；正确限定为 central 或排除私服。 |
| 怎么用 | `<mirrorOf>central</mirrorOf>` 或 `<mirrorOf>*,!nexus-public</mirrorOf>` |
| 原理和工作流程 | mirrorOf=* 会拦截所有仓库请求并重定向到镜像地址，包括 pom.xml 中自定义的私服 repository，导致内部构件被错误重定向到镜像而拉取失败。正确做法是限定为 central，或用 `*,!nexus-public` 排除私服仓库。 |
| 缺点 | * 易误拦截私服；镜像源不同步；调试不直观。 |

### 10. ★★★ 关于 scope 取值，下列说法正确的是（ ）

| 维度 | 内容 |
|------|------|
| 是什么 | import scope 专用于 dependencyManagement 导入另一 POM 依赖管理的特性。 |
| 能做什么 | 配 type=pom 导入 BOM 整套版本清单；provided 不打包；test 不参与主编译；runtime 不参与编译。 |
| 怎么用 | `<scope>import</scope><type>pom</type>` 导入 spring-boot-dependencies。 |
| 原理和工作流程 | import 专用于 dependencyManagement，配合 type=pom 把另一 POM 的整套版本管理导入当前项目，如导入 spring-boot-dependencies。provided 不打包（由环境提供）；test 不参与主代码编译；runtime 不参与编译 classpath，只在运行时与测试时可用。 |
| 缺点 | import 仅限 dependencyManagement 易误用为普通依赖；BOM 版本可能与本地期望不一致。 |

---

## 二、简答题（5 题，每题附完整解析）

| 维度 | 内容 |
|------|------|
| 是什么 | 覆盖 Maven 核心机制与实战配置的 5 道简答题题型分类。 |
| 能做什么 | 考查依赖冲突规则、dependencyManagement 区别、三大生命周期、Nexus 仓库类型与发布流程、多环境配置等综合表述能力。 |
| 怎么用 | 简答作答后对照解析查漏补缺。 |
| 原理和工作流程 | 以开放问答形式考查对机制的完整表述与流程梳理，解析给出规则、对比、阶段、类型、实践要点，覆盖基础至拔高难度。 |
| 缺点 | 主观评分标准不一；仅考表述不考实操；题量有限。 |

### 1. ★ 简述 Maven 的依赖冲突解决规则。

| 维度 | 内容 |
|------|------|
| 是什么 | Maven 裁决同一构件多版本冲突的两条规则。 |
| 能做什么 | 最短路径优先；声明顺序优先；提供排查与修复手段。 |
| 怎么用 | `mvn dependency:tree -Dverbose`，exclusions 或 dependencyManagement 锁定。 |
| 原理和工作流程 | 第一最短路径优先，依赖树中离当前项目越近的版本胜出，直接声明（路径长度 1）必胜；第二声明顺序优先，路径长度相同时 pom.xml 先声明者生效。排查用 dependency:tree -Dverbose 看被丢弃版本（omitted for conflict with），修复用 exclusions 排除冲突版本或父 POM dependencyManagement 统一锁定。 |
| 缺点 | 生效版本常非预期致运行期错误；规则隐式难判断；大型项目排查成本高。 |

### 2. ★★ 简述 dependencyManagement 与 dependencies 的区别。

| 维度 | 内容 |
|------|------|
| 是什么 | dependencies 直接引入、dependencyManagement 只声明版本的两类配置区别。 |
| 能做什么 | dependencies 加入 classpath 并打包；dependencyManagement 统一多模块版本；子模块省略 version 沿用父版本。 |
| 怎么用 | 父 POM `<dependencyManagement>` + `scope=import type=pom` 导入 BOM，子模块只写坐标。 |
| 原理和工作流程 | dependencies 直接引入依赖会实际加入 classpath 并打包；dependencyManagement 只声明版本不引入，子模块继承父 POM 后引入同名依赖若省略 version 则采用管理版本。常见用法是父 POM 用 scope=import + type=pom 导入 spring-boot-dependencies 整套版本清单，子模块只需声明坐标即获统一版本。 |
| 缺点 | 仅声明不引入易被误解为已引入；子模块无 version 可读性下降；BOM 版本可能不符本地期望。 |

### 3. ★★ 简述 Maven 三大生命周期及其主要阶段。

| 维度 | 内容 |
|------|------|
| 是什么 | clean、default、site 三套互相独立的生命周期及主要阶段。 |
| 能做什么 | clean 清理 target；default 完成编译测试打包安装发布；site 生成站点文档。 |
| 怎么用 | `mvn clean package` / `mvn install` / `mvn deploy` |
| 原理和工作流程 | 三套生命周期互相独立。clean 阶段为 pre-clean、clean、post-clean；default 关键阶段为 validate、compile、test、package、verify、install、deploy；site 阶段为 pre-site、site、post-site、site-deploy。执行某 phase 时其前所有 phase 依次执行，真正干活的是绑定到 phase 的插件 goal。 |
| 缺点 | 三套独立易混淆；阶段绑定隐式；site 实际使用少。 |

### 4. ★★★ 简述 Nexus 的三种仓库类型及构件发布流程。

| 维度 | 内容 |
|------|------|
| 是什么 | Nexus 的 proxy、hosted、group 三类仓库及构件发布流程。 |
| 能做什么 | proxy 代理远程并缓存；hosted 托管内部构件分 releases/snapshots；group 聚合统一入口；deploy 按版本路由上传。 |
| 怎么用 | 日常配 group 地址，`mvn deploy` 发布。 |
| 原理和工作流程 | proxy 代理远程仓库并缓存构件；hosted 托管企业内部构件，releases 禁止覆盖保正式版不变，snapshots 允许覆盖并生成时间戳子版本保留历史；group 聚合多仓库统一地址。发布对应 deploy 阶段，maven-deploy-plugin 按 version 含 -SNAPSHOT 上传到 snapshotRepository 否则 repository；settings servers 需同名 id 认证且账号有写入权限。 |
| 缺点 | releases 不可覆盖需升版本；SNAPSHOT 不固定；认证 id 不匹配致 401；私服需运维。 |

### 5. ★★★ 简述如何在 Maven 中实现多环境配置隔离。

| 维度 | 内容 |
|------|------|
| 是什么 | 用 profiles + resource filtering 实现多环境配置隔离的方案。 |
| 能做什么 | 定义多环境 profile；properties 设环境标识；filtering 替换占位符；-P 激活。 |
| 怎么用 | pom 配 profiles 与 filtering，`mvn package -P prod`。 |
| 原理和工作流程 | profiles 定义 dev/test/prod，每个 profile 用 properties 设 env=prod 等；build 对资源目录 filtering=true 并用 filters 引用 application-${env}.yml；构建时 -P prod 激活，占位符替换为对应环境值。Spring Boot 结合 spring.profiles.active 与 @env@ 占位符（starter parent 默认 @..@）避免与 Spring ${} 冲突。 |
| 缺点 | profile 组合复杂；占位符冲突；filtering 性能开销；多文件维护成本高。 |

---

> [返回原文](./03-Maven笔面试题集.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
