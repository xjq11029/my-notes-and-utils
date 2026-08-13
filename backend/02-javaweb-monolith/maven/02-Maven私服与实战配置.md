# Maven 私服与实战配置

> 学习路线对应：补充模块 -- Maven 构建工具（进阶）
> 前置知识：Maven 核心原理、依赖管理（见 [01-Maven核心原理与依赖管理](./01-Maven核心原理与依赖管理.md)）
> 预计学习时间：2-3 小时
> 对比 Node.js：私服约等于 Verdaccio / cnpm 私有 registry，settings.xml 约等于 .npmrc

---

## 一、核心概念

### 1.1 仓库体系

Maven 的构件（artifact）按"就近取用"原则在各级仓库间流转。仓库分为三类：

| 仓库类型 | 位置 | 作用 | 对应 Node.js |
|----------|------|------|--------------|
| 本地仓库 | 本机磁盘（默认 ~/.m2/repository） | 缓存已下载构件 | node_modules / pnpm store |
| 远程仓库 | 网络 | 提供构件下载 | registry |
| 中央仓库 | repo.maven.apache.org | Maven 官方公共仓库 | npmjs.com |

远程仓库又细分为中央仓库与私服（Nexus/Artifactory）。本地仓库找不到的构件，Maven 会依次向远程仓库请求，下载后缓存到本地。

构件查找顺序：本地仓库 → settings.xml 的 mirror → pom.xml 的 repositories → 中央仓库。理解这条链路，是排查"下载不到依赖"类问题的基础。

> **生活化类比：三级仓库就像快递物流体系** —— Maven 的三级仓库体系与快递物流非常相似：本地仓库是你家门口的快递柜（拿到货就放这，下次直接拿，免去重新配送）；私服是城市分拨中心（公司内部统一收货、二次分发，避免每个员工都向发货方下单）；中央仓库是品牌总仓（源头供货方，永不缺货但运费高、速度慢）。Maven 的"就近取用"原则对应到物流就是"先查快递柜，再问分拨中心，最后才让总仓发货"。

> 📖 **参考链接**：
> - [Maven - Introduction to Repositories](https://maven.apache.org/guides/introduction/introduction-to-repositories.html) -- 仓库简介
> - [Maven - Settings Reference](https://maven.apache.org/settings.html) -- settings.xml 配置参考

### 1.2 settings.xml 配置详解

settings.xml 是 Maven 的用户级/全局级配置文件，独立于具体项目。它存在于两个位置：

- 全局配置：`$MAVEN_HOME/conf/settings.xml`
- 用户配置：`~/.m2/settings.xml`（优先级高于全局配置）

核心元素总览：

| 元素 | 作用 | 说明 |
|------|------|------|
| localRepository | 本地仓库路径 | 默认 ~/.m2/repository，可改到 SSD 加速 |
| servers | 仓库认证信息 | id + username + password，id 与仓库 id 对应 |
| mirrors | 镜像配置 | 把对某仓库的请求重定向到镜像地址 |
| profiles | 环境配置集合 | 定义 repositories、properties 等 |
| activeProfiles | 激活的 profile | 默认激活的 profile id |
| proxies | 代理设置 | 走 HTTP 代理上网时配置 |

一个最小可用 settings.xml：

```xml
<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0">
    <localRepository>D:/maven-repo</localRepository>

    <servers>
        <server>
            <id>nexus-releases</id>
            <username>admin</username>
            <password>admin123</password>
        </server>
        <server>
            <id>nexus-snapshots</id>
            <username>admin</username>
            <password>admin123</password>
        </server>
    </servers>

    <mirrors>
        <mirror>
            <id>aliyun</id>
            <mirrorOf>central</mirrorOf>
            <name>Aliyun Public</name>
            <url>https://maven.aliyun.com/repository/public</url>
        </mirror>
    </mirrors>

    <profiles>
        <profile>
            <id>nexus</id>
            <repositories>
                <repository>
                    <id>nexus-public</id>
                    <url>http://nexus.ljit.com/repository/maven-public/</url>
                    <releases><enabled>true</enabled></releases>
                    <snapshots><enabled>true</enabled></snapshots>
                </repository>
            </repositories>
        </profile>
    </profiles>

    <activeProfiles>
        <activeProfile>nexus</activeProfile>
    </activeProfiles>
</settings>
```

注意 servers 里的 id 必须与 pom.xml 中 distributionManagement 的 repository id、mirrors 的 mirrorOf 引用的 id 一致，否则认证无法匹配。

> 📖 **参考链接**：
> - [Maven - Guide to Mirror Settings](https://maven.apache.org/guides/mini/guide-mirror-settings.html) -- 镜像配置指南
> - [Maven - Settings Descriptor](https://maven.apache.org/ref/current/maven-settings/settings.html) -- settings.xml 元素描述

---

## 二、底层原理

### 2.1 镜像机制

mirror 的作用是把对某个仓库（按 id 匹配）的请求整体重定向到镜像地址。国内最典型的用法是用阿里云镜像替换慢速的 Maven 中央仓库。

> **生活化类比：镜像机制就像高铁分流** —— 想象你原本要从北京坐绿皮火车去上海（直接访问 Maven 中央仓库），但绿皮车又慢又挤。铁路局在京沪线路上加开了一趟高铁（mirror），mirrorOf=central 就相当于"凡是原本坐绿皮车去上海的，都改乘高铁"。但如果你本来要去的是杭州（私服仓库），你不会被强制改坐高铁——除非把 mirrorOf 配成 `*`，那就是"全国所有线路都改乘高铁"，明显过头了。所以镜像要精准匹配，避免误伤。

mirrorOf 的取值决定匹配范围：

| mirrorOf 取值 | 匹配范围 |
|---------------|----------|
| * | 所有仓库 |
| external:* | 所有非本地、非 file 协议的仓库 |
| central | 仅 id 为 central 的仓库（中央仓库） |
| repo1,repo2 | 指定多个 id |
| *,!repo1 | 所有仓库，排除 repo1 |

一个常见误区：mirror 会"拦截"被镜像仓库的请求。若 mirrorOf 配成 `*`，那么 pom.xml 里自定义的所有 repository 都会被重定向到该镜像，可能导致私服上的内部构件拉取失败。正确做法是把 mirrorOf 限定为 central，或用 `*,!nexus-public` 排除私服仓库。

镜像机制进阶要点补充：

- 多镜像共存：settings.xml 中可以配置多个 mirror，但 Maven 只会选择第一个匹配的 mirror，并不是所有匹配的都生效。若 `mirrorOf=*` 的镜像先出现，后续所有镜像都会失效。
- 镜像与 repository 的关系：mirror 是"请求重定向"，并不会改变 pom.xml 中 repository 的 url 配置，只是 Maven 内部决定"实际访问哪个地址"。
- 镜像的 layout：默认 layout=default，对应 Maven 2/3 的仓库布局。如果镜像的是老 Maven 1 仓库，需要设为 legacy，但这种情况已极少见。
- HTTPS 与证书：内网 Nexus 常用自签证书，JVM 默认不信任，需要在 MAVEN_OPTS 或 truststore 中导入证书，否则会出现 `SSLPeerUnverifiedException`。
- 镜像的 blocked 属性：Maven 3.8.1+ 默认屏蔽 HTTP 镜像（非 HTTPS），需要在 mirror 节点显式加 `<blocked>false</blocked>` 才能使用 HTTP 内网镜像。

> 📖 **参考链接**：
> - [Maven - Guide to Mirror Settings](https://maven.apache.org/guides/mini/guide-mirror-settings.html) -- 镜像配置详细指南
> - [Maven - Guide to HTTP Settings](https://maven.apache.org/guides/mini/guide-http-settings.html) -- HTTP/HTTPS 设置

### 2.2 私服架构（Nexus / Artifactory）

私服是部署在企业内部的仓库代理服务器，常见实现是 Sonatype Nexus 与 JFrog Artifactory。它解决三个痛点：加速下载、统一内部构件发布、节省公网带宽。

Nexus 维护三类仓库：

| 仓库类型 | 作用 | 典型实例 |
|----------|------|----------|
| proxy | 代理远程仓库，缓存其构件 | maven-central（代理 Maven 中央仓库） |
| hosted | 托管内部构件 | maven-releases、maven-snapshots、maven-thirdparty |
| group | 聚合多个仓库，对外暴露统一入口 | maven-public（合并 central + releases + snapshots） |

group 仓库是日常使用的统一入口。客户端只需配置一个 group 地址，就能同时访问代理的公共构件和托管的内部构件，不必在 pom 里逐个声明多个 repository。

proxy 仓库的工作机制：客户端请求某构件时，Nexus 先查本地缓存；缓存未命中则向被代理的远程仓库拉取，落盘后返回给客户端。后续相同构件的请求直接命中缓存，不再访问公网。

> **生活化类比：私服架构就像企业供应链中心** —— Nexus 三种仓库类型可以用企业供应链来类比：proxy 仓库相当于"采购部"（专门去外部供应商拉货，第一次拉了就放仓库留存）；hosted 仓库相当于"自家工厂车间"（生产内部产品存放于此，分正式品仓和试作品仓）；group 仓库相当于"统一发货窗口"（员工不需要知道货是从采购部来还是工厂车间来，统一从窗口取货）。这就是为什么 group 是日常配置的入口——它隐藏了底层仓库的复杂性。

> 📖 **参考链接**：
> - [Sonatype Nexus Repository Documentation](https://help.sonatype.com/repomanager3) -- Nexus Repository 3 官方文档
> - [JFrog Artifactory Documentation](https://jfrog.com/help/r/jfrog-artifactory-documentation) -- Artifactory 官方文档
> - [Maven - Introduction to Repositories](https://maven.apache.org/guides/introduction/introduction-to-repositories.html) -- Maven 仓库体系

### 2.3 发布流程

构件发布对应 default 生命周期的 deploy 阶段。`mvn deploy` 在 install 之后执行，把打包产物上传到 distributionManagement 配置的远程仓库。

发布流程：本地构建产物 → maven-deploy-plugin → 按 SNAPSHOT 或 RELEASE 分别上传到 snapshotRepository 或 repository → Nexus hosted 仓库存储。

RELEASE 与 SNAPSHOT 在 Nexus 中的存储行为不同：

- maven-releases：不允许覆盖，同一版本号重复上传会被拒绝（保证正式版不可变）
- maven-snapshots：允许覆盖，同一 SNAPSHOT 会生成带时间戳的子版本，保留历史构建

这一差异正是私服把 releases 与 snapshots 拆成两个 hosted 仓库的原因。

#### SNAPSHOT 与 RELEASE 版本的深层差异

虽然两者都是版本号，但在 Maven 与 Nexus 的语义中存在多维度差异，理解这些差异有助于在生产环境中正确选型：

| 维度 | RELEASE（如 1.0.0） | SNAPSHOT（如 1.0.0-SNAPSHOT） |
|------|---------------------|------------------------------|
| 版本可变性 | 一旦发布即不可变 | 持续可变，每次 deploy 都更新 |
| 本地缓存策略 | 一旦下载永久缓存 | 按 updatePolicy 周期性检查更新 |
| Nexus 存储 | 同版本号只能存一份，重复上传报 400 | 同 SNAPSHOT 可保留多份，文件名带时间戳（如 order-common-1.0.0-20260720.083045-1.jar） |
| 私服仓库 | 上传到 maven-releases（hosted，Release policy） | 上传到 maven-snapshots（hosted，Snapshot policy） |
| 适用阶段 | 正式发布、生产环境依赖 | 固定版本未发布前、多模块协同开发 |
| 强制更新 | 无需 `-U` | 多人协作时常配 `-U` 拉取最新快照 |
| 稳定性风险 | 低（不可变） | 高（同一天可能多次变更） |

生产环境铁律：禁止任何形式的生产代码依赖 SNAPSHOT 版本。一旦私服上的 SNAPSHOT 被覆盖，线上行为会变得不可预测且无法回溯。正确做法是先发布 RELEASE 版本，再让生产环境引用该 RELEASE。

> 📖 **参考链接**：
> - [Maven - POM Version](https://maven.apache.org/pom.html#Maven_Coordinates) -- POM 版本号语义
> - [Maven - Dependency Management SNAPSHOT](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html#Dependency_Scope) -- SNAPSHOT 依赖机制

---

## 三、实战应用

### 3.1 Nexus 私服搭建步骤

以 Docker 方式部署 Nexus3 为例：

```bash
docker run -d \
  --name nexus \
  -p 8081:8081 \
  -v nexus-data:/nexus-data \
  sonatype/nexus3
```

部署后访问 `http://nexus.ljit.com:8081`，首次启动用容器内 `/nexus-data/admin.password` 中的初始密码登录并修改。

仓库配置步骤：

1. 创建 hosted 仓库 maven-releases（version policy=Release）
2. 创建 hosted 仓库 maven-snapshots（version policy=Snapshot）
3. 创建 proxy 仓库 maven-central（代理 https://repo1.maven.org/maven2/）
4. 创建 group 仓库 maven-public，按顺序加入 maven-central、maven-releases、maven-snapshots

group 中的仓库顺序决定查找顺序，把 hosted 放前面可优先命中内部构件。

#### Nexus 部署的进阶实践

生产环境部署 Nexus 时，单纯用 `docker run` 启动还不够，需要关注以下几个关键点：

**1. 数据持久化与备份**

`nexus-data` 卷是 Nexus 的全部数据所在（仓库、配置、用户、任务），丢失即灾难。生产环境要求：

```bash
# 使用命名卷并指定宿主机路径，便于备份
docker run -d \
  --name nexus \
  -p 8081:8081 \
  -v /data/nexus:/nexus-data \
  --restart=unless-stopped \
  sonatype/nexus3

# 每日定时备份 nexus-data 目录（含 blob store 与元数据）
0 2 * * * tar -czf /backup/nexus-$(date +\%Y\%m\%d).tar.gz /data/nexus
```

Nexus 还支持任务化备份组件（Scheduled Tasks），可定时把 blob store 同步到 S3/OSS 等对象存储，实现异地容灾。

**2. JVM 参数与内存调优**

Nexus3 默认堆内存较低（1.2G），中大型团队需要调高，通过环境变量 `INSTALL4J_ADD_VM_PARAMS` 传入：

```bash
docker run -d \
  -e INSTALL4J_ADD_VM_PARAMS="-Xms2g -Xmx4g -XX:MaxDirectMemorySize=2g" \
  ...
```

**3. 反向代理与 HTTPS**

生产环境 Nexus 必须启用 HTTPS（避免 Maven 3.8.1+ 默认屏蔽 HTTP 仓库）。推荐用 Nginx 反代：

```nginx
server {
    listen 443 ssl;
    server_name nexus.ljit.com;

    ssl_certificate     /etc/nginx/ssl/nexus.crt;
    ssl_certificate_key /etc/nginx/ssl/nexus.key;

    client_max_body_size 500M;   # 允许上传大构件

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

注意 `X-Forwarded-Proto: https` 必须显式传递，否则 Nexus 内部生成的下载链接会是 HTTP，导致 Maven 客户端报"Blocked Mirror"错误。

**4. 权限模型**

Nexus 默认用 admin 账号操作，生产环境应建立最小权限模型：

- 创建角色 `developer`：仅对 maven-snapshots 有写入权限，对 maven-releases 只读
- 创建角色 `releaser`：对 maven-releases 有写入权限
- 创建角色 `reader`：所有 hosted/proxy 只读，分配给 CI 与开发机
- 服务账号用专用账号，不使用 admin，便于审计与回收

> 📖 **参考链接**：
> - [Sonatype Nexus - Installing and Upgrading](https://help.sonatype.com/repomanager3/installation) -- Nexus 安装与升级指南
> - [Sonatype Nexus - Docker Installation](https://help.sonatype.com/repomanager3/installation/installation-methods/docker) -- Docker 部署详情
> - [Sonatype Nexus - Security](https://help.sonatype.com/repomanager3/security) -- 权限模型与安全配置

### 3.2 settings.xml 完整配置示例

兼顾公网加速与私服发布的完整配置：

```xml
<settings xmlns="http://maven.apache.org/SETTINGS/1.2.0">
    <localRepository>D:/maven-repo</localRepository>

    <!-- 私服认证：id 与 pom 中 distributionManagement 的 repository id 对应 -->
    <servers>
        <server>
            <id>nexus-releases</id>
            <username>admin</username>
            <password>${env.NEXUS_PWD}</password>
        </server>
        <server>
            <id>nexus-snapshots</id>
            <username>admin</username>
            <password>${env.NEXUS_PWD}</password>
        </server>
    </servers>

    <!-- 公网镜像加速：仅替换中央仓库，不影响私服 -->
    <mirrors>
        <mirror>
            <id>aliyun-central</id>
            <mirrorOf>central</mirrorOf>
            <url>https://maven.aliyun.com/repository/central</url>
        </mirror>
    </mirrors>

    <profiles>
        <profile>
            <id>nexus</id>
            <repositories>
                <repository>
                    <id>nexus-public</id>
                    <url>http://nexus.ljit.com/repository/maven-public/</url>
                    <releases><enabled>true</enabled></releases>
                    <snapshots>
                        <enabled>true</enabled>
                        <updatePolicy>always</updatePolicy>
                    </snapshots>
                </repository>
            </repositories>
        </profile>
    </profiles>

    <activeProfiles>
        <activeProfile>nexus</activeProfile>
    </activeProfiles>
</settings>
```

updatePolicy 取值：always（每次构建都检查更新）、daily（每天）、never（不检查）。SNAPSHOT 常配 always 或 daily，以拉取团队最新快照。

### 3.3 pom.xml 发布配置

distributionManagement 声明发布目标仓库：

```xml
<project>
    <groupId>com.ljit</groupId>
    <artifactId>order-common</artifactId>
    <version>1.0.0</version>

    <distributionManagement>
        <repository>
            <id>nexus-releases</id>
            <url>http://nexus.ljit.com/repository/maven-releases/</url>
        </repository>
        <snapshotRepository>
            <id>nexus-snapshots</id>
            <url>http://nexus.ljit.com/repository/maven-snapshots/</url>
        </snapshotRepository>
    </distributionManagement>
</project>
```

执行发布：

```bash
mvn clean deploy
```

发布前提：settings.xml 的 servers 中存在与 repository id 同名的认证条目，且账号有对应 hosted 仓库的写入权限。

### 3.4 多环境 Profile 隔离

多环境配置（dev/test/prod）在 pom.xml 用 profile + resource filtering 实现。先在 src/main/resources 放各环境配置：

```
src/main/resources/
├── application.yml
├── application-dev.yml
├── application-test.yml
└── application-prod.yml
```

pom.xml 定义 profiles 与资源过滤：

```xml
<profiles>
    <profile>
        <id>dev</id>
        <properties>
            <env>dev</env>
        </properties>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
    </profile>
    <profile>
        <id>prod</id>
        <properties>
            <env>prod</env>
        </properties>
    </profile>
</profiles>

<build>
    <resources>
        <resource>
            <directory>src/main/resources</directory>
            <filtering>true</filtering>
        </resource>
    </resources>
    <filters>
        <filter>src/main/resources/application-${env}.yml</filter>
    </filters>
</build>
```

通过 `mvn clean package -P prod` 激活 prod 环境，`${env}` 占位符被替换为对应值。若使用 Spring Boot，更推荐用 spring.profiles.active 配合 `@env@` 占位符（Maven 资源过滤），由 Spring Boot starter parent 默认用 `@..@` 而非 `${...}`，避免与 Spring 占位符冲突。

> 📖 **参考链接**：
> - [Maven - Introduction to Build Profiles](https://maven.apache.org/guides/introduction/introduction-to-profiles.html) -- Profile 介绍
> - [Maven - Profile Activation](https://maven.apache.org/guides/introduction/introduction-to-profiles.html#Profile_Activation) -- Profile 激活机制
> - [Maven - Resource Filtering](https://maven.apache.org/plugins/maven-resources-plugin/examples/filter.html) -- 资源过滤指南

---

## 四、常见面试题

### 1. Maven 的仓库体系是怎样的？本地仓库、私服、中央仓库的关系？

答案：Maven 仓库分为本地仓库、远程仓库（私服/中央仓库）。构件查找顺序是先查本地仓库（默认 ~/.m2/repository），未命中再按配置请求远程仓库，中央仓库是 Maven 官方公共仓库。引入私服后，通常把 group 仓库地址配为远程仓库，私服内部代理中央仓库并缓存构件，同时托管企业内部构件，统一对外提供下载入口。

### 2. settings.xml 中 mirror 的 mirrorOf 有哪些取值？配成 * 会有什么问题？

答案：mirrorOf 取值包括 *（所有仓库）、external:*（非本地非 file 仓库）、central（仅中央仓库）、逗号列举多个 id、`*,!repo1`（排除某仓库）。配成 * 会拦截所有仓库请求，包括 pom.xml 中自定义的私服 repository，可能导致内部构件被错误地重定向到镜像地址而拉取失败。生产环境应限定为 central，或用 `*,!nexus-public` 排除私服仓库。

### 3. Nexus 的三种仓库类型分别是什么？

答案：proxy 代理远程仓库，缓存其构件（如代理 Maven 中央仓库）；hosted 托管企业内部构件，按版本策略分为 releases（不可覆盖）与 snapshots（可覆盖，保留历史）；group 聚合多个仓库，对外暴露统一地址。日常使用只需配置一个 group 地址，即可同时访问代理的公共构件与托管的内部构件。

### 4. mvn deploy 的执行流程？RELEASE 与 SNAPSHOT 在私服中存储有何不同？

答案：deploy 对应 default 生命周期的 deploy 阶段，由 maven-deploy-plugin 执行，把构建产物上传到 distributionManagement 配置的远程仓库。Maven 根据版本号判断：含 -SNAPSHOT 的上传到 snapshotRepository，否则上传到 repository。在 Nexus 中，releases 仓库禁止覆盖同版本号，保证正式版不可变；snapshots 仓库允许覆盖，并为每次上传生成带时间戳的子版本，保留历史构建。

### 5. 多环境配置如何在 Maven 中实现？

答案：用 profiles 定义多个环境，每个 profile 通过 properties 设置环境标识变量（如 env=prod），再用 resource filtering 把变量替换进配置文件。构建时用 `mvn package -P prod` 激活目标 profile，对应配置文件被启用。Spring Boot 项目可结合 spring.profiles.active 与 `@env@` 占位符（由 spring-boot-starter-parent 配置的 resource delimiter），避免与 Spring 的 ${} 占位符冲突。

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| mirrorOf 配成 * | 私服内部构件拉取失败 | 镜像拦截了所有仓库请求，私服被重定向 | mirrorOf 限定为 central，或用 `*,!nexus-public` 排除私服 |
| servers 的 id 不匹配 | deploy 报 401 Unauthorized | distributionManagement 的 repository id 与 settings 的 server id 不一致 | 两处 id 保持完全一致，并确认账号有写入权限 |
| releases 仓库重复上传 | deploy 报 400 Repository does not allow updating assets | releases 仓库禁止覆盖同版本 | 重新发布前升级版本号，或改用 SNAPSHOT；需要覆盖时在 Nexus 开启该仓库的 Allow Redeploy |
| SNAPSHOT 不更新 | 拉取到旧快照 | 本地缓存了旧 SNAPSHOT，updatePolicy 默认 daily | 设 updatePolicy=always，或加 `-U` 强制更新（`mvn clean package -U`） |
| 离线构建失败 | Cannot access 仓库 | 本地仓库缺构件且 offline=true | settings.xml 设 offline=false，或预先在联网环境 install 好构件 |
| 密码明文泄露 | settings.xml 中明文存储私服密码 | 直接写 password | 用 `${env.NEXUS_PWD}` 从环境变量读取，或用 mvn 的 settings security 加密 |

## 本章学习自检

完成本章学习后，应该能够：
- [ ] 用自己的话解释仓库体系（本地/远程/中央/私服）、settings.xml 各核心元素、镜像机制、Nexus 三种仓库类型、deploy 发布流程
- [ ] 搭建一套 Nexus 私服，配置 settings.xml 兼顾公网加速与私服发布
- [ ] 写出 distributionManagement 发布配置并用 `mvn deploy` 上传构件
- [ ] 用 profiles + resource filtering 实现多环境配置隔离
- [ ] 回答常见面试题（仓库体系、mirrorOf 取值与陷阱、三种仓库类型、deploy 流程、多环境配置）
- [ ] 识别并避免常见错误（mirrorOf 滥用 *、id 不匹配、releases 覆盖、SNAPSHOT 不更新、密码明文）

---

> **学习导航**：
> - 返回 [学习路线总览](../../README.md)
> - 本模块其他文件：[01-Maven核心原理与依赖管理](./01-Maven核心原理与依赖管理.md) | [03-Maven笔面试题集](./03-Maven笔面试题集.md)
> - 实战应用：[电商订单实时统计分析平台](../../extensions/project/01-电商订单实时统计分析平台.md)
