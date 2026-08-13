# Spring Boot 部署与运维 导览

> 定位：五维框架浓缩提炼 08-SpringBoot部署与运维.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./08-SpringBoot部署与运维.md)。
> 前置知识：[Spring-Boot自动配置原理](./02-Spring-Boot自动配置原理-导览.md)、[Maven核心原理与依赖管理](../maven/01-Maven核心原理与依赖管理-导览.md)、[Docker核心原理](../docker-k8s/01-Docker核心原理-导览.md)

---

## 一、核心概念

### 1.1 部署方式演进

| 维度 | 内容 |
|------|------|
| 是什么 | Java Web 应用从 WAR 到 JAR 到 Docker 再到 Kubernetes 的四个部署阶段演进 |
| 能做什么 | WAR 部署外部 Tomcat；JAR 内嵌容器直接运行；Docker 环境隔离；K8s 自动伸缩滚动更新 |
| 怎么用 | 演进路线：`WAR（外部 Tomcat） -> JAR（内嵌 Tomcat） -> Docker（容器化） -> K8s（编排调度）` |
| 原理和工作流程 | 传统阶段打包为 WAR 部署到独立 Tomcat，需单独安装容器环境耦合重多应用共享容器。内嵌阶段 Spring Boot 内嵌 Tomcat 打包为 JAR，java -jar 直接运行，单机部署水平扩展需手动管理。容器化阶段用 Docker 部署实现环境隔离一次构建到处运行，单节点编排需配合 K8s。云原生阶段用 Kubernetes 部署实现自动伸缩、滚动更新、自愈，学习曲线陡运维复杂度高。每个阶段都在前阶段基础上提升环境一致性和运维自动化 |
| 缺点 | WAR 环境耦合重；JAR 单机部署扩展需手动；Docker 单节点编排能力弱；K8s 学习曲线陡运维复杂 |

### 1.2 Spring Boot 内嵌容器

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 支持的三种内嵌 Servlet 容器 Tomcat、Jetty、Undertow 及其切换方式 |
| 能做什么 | Tomcat 默认生态成熟；Jetty 轻量启动快；Undertow 基于 NIO 高并发内存占用低；按需切换 |
| 怎么用 | 排除 `spring-boot-starter-tomcat` 后引入 `spring-boot-starter-undertow` |
| 原理和工作流程 | Spring Boot 支持三种内嵌容器。Tomcat 是默认容器生态成熟，并发性能中等适用于通用 Web 应用。Jetty 轻量级启动快，适用于对启动速度有要求和嵌入式场景。Undertow 基于 NIO 内存占用低并发性能高，适用于高并发和资源受限环境。切换容器时在 spring-boot-starter-web 中通过 exclusions 排除 spring-boot-starter-tomcat，然后引入 spring-boot-starter-undertow 或 spring-boot-starter-jetty。Spring Boot 通过 ServletWebServerFactory 抽象自动适配新容器，业务代码无需修改 |
| 缺点 | Tomcat 默认配置不一定最优需调优；Jetty 生态不如 Tomcat 完善；Undertow 社区文档较少；切换后部分容器特有配置失效 |

---

## 二、底层原理

### 2.1 JAR 打包原理

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 通过 spring-boot-maven-plugin 的 repackage goal 将普通 JAR 重新打包为可执行 fat jar 的机制 |
| 能做什么 | 将项目 class 放入 BOOT-INF/classes；第三方依赖放入 BOOT-INF/lib；生成 JarLauncher 启动器；自定义类加载器加载嵌套 JAR |
| 怎么用 | `<plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId><executions><execution><goals><goal>repackage</goal></goals></execution></executions></plugin>` |
| 原理和工作流程 | repackage 过程将原始 JAR 重新打包为 fat JAR 结构：app.jar 含 META-INF/MANIFEST.MF（Main-Class 为 org.springframework.boot.loader.JarLauncher）、BOOT-INF/classes（项目自身 class）、BOOT-INF/lib（所有第三方依赖 JAR）、org/springframework/boot/loader（启动器代码）。启动流程：1. java -jar app.jar。2. JVM 读取 MANIFEST.MF 找到 Main-Class JarLauncher。3. JarLauncher 执行 main 方法。4. 创建 LaunchedURLClassLoader 专门加载 BOOT-INF/lib 下的 JAR。5. 通过反射调用项目主类的 main 方法。6. SpringApplication.run 启动应用。关键点是 fat jar 使用自定义类加载器 LaunchedURLClassLoader，可读取嵌套 JAR 内部的 class 文件，标准 URLClassLoader 无法读取 JAR 中的 JAR |
| 缺点 | fat jar 体积大包含全部依赖；嵌套 JAR 类加载机制对调试不友好；依赖冲突排查困难；无法像 WAR 那样共享容器依赖 |

### 2.2 外部化配置

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 支持多种配置来源并按固定优先级覆盖的外部化配置机制 |
| 能做什么 | 命令行参数覆盖；环境变量覆盖；jar 包外配置覆盖包内；profile 配置覆盖默认；多来源灵活组合 |
| 怎么用 | `java -jar app.jar --server.port=9090`；或 `config/application.yml` 放 jar 同级目录 |
| 原理和工作流程 | Spring Boot 支持多种配置来源按优先级从高到低排列：1 命令行参数、2 环境变量、3 jar 包外 application-{profile}.yml、4 jar 包内 application-{profile}.yml、5 jar 包外 application.yml、6 jar 包内 application.yml。重要原则是高优先级覆盖低优先级，jar 包外配置覆盖 jar 包内配置，profile 配置覆盖默认配置。命令行参数通过 --key=value 传入。环境变量将属性名转为大写下划线（server.port -> SERVER_PORT）。外部配置文件放在 jar 同级 config 目录自动加载优先级最高。也可用 --spring.config.location 显式指定配置文件位置 |
| 缺点 | 优先级层级多容易混淆；同名属性跨来源覆盖排查困难；环境变量命名需转换；外部配置文件位置不当不生效 |

### 2.3 Profile 环境隔离

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 通过 Profile 机制实现开发、测试、生产等多环境配置隔离的方案 |
| 能做什么 | @Profile 注解按环境装配 Bean；application-{profile}.yml 分组配置；多种方式激活 Profile；环境隔离 |
| 怎么用 | `java -jar app.jar --spring.profiles.active=prod`；或 `SPRING_PROFILES_ACTIVE=prod` |
| 原理和工作流程 | Profile 环境隔离有两种方式。方式一 @Profile 注解，标注在 @Configuration 类上，仅当指定 Profile 激活时该配置类才生效装配对应 Bean。方式二配置文件分组，application.yml 为公共配置，application-dev.yml 为开发环境配置，application-prod.yml 为生产环境配置，通过 spring.profiles.active 激活对应环境。激活 Profile 的方式有三种：命令行参数 --spring.profiles.active=prod、环境变量 SPRING_PROFILES_ACTIVE=prod、配置文件 spring.profiles.active=prod。激活后对应 profile 的配置覆盖默认配置，实现多环境隔离 |
| 缺点 | 多环境配置文件分散管理成本高；激活方式多样易混淆；Profile 切换需重启；公共与 profile 配置覆盖关系复杂 |

### 2.4 热部署（spring-boot-devtools）

| 维度 | 内容 |
|------|------|
| 是什么 | spring-boot-devtools 通过双类加载器机制实现快速重启的热部署工具，比完整重启快 5-10 倍 |
| 能做什么 | 监听文件变化自动重启；双类加载器只重载项目代码；保留第三方依赖不重载；仅用于开发环境 |
| 怎么用 | 引入 `spring-boot-devtools` 依赖 scope 为 runtime optional 为 true |
| 原理和工作流程 | devtools 通过双类加载器机制实现快速重启。类加载器层级：BaseClassLoader 加载第三方依赖 JAR（很少变化），RestartClassLoader 加载项目自身 class（修改后重新加载）。工作原理：1. 应用启动时第三方依赖由 BaseClassLoader 加载不变。2. 项目代码由 RestartClassLoader 加载。3. 代码修改后 devtools 监听到文件变化。4. 丢弃旧 RestartClassLoader 创建新 RestartClassLoader 重新加载项目代码。5. BaseClassLoader 保持不变避免重新加载大量第三方依赖。因只需重载项目代码而非全部依赖，重启速度比完整重启快 5-10 倍。devtools 仅用于开发环境，生产部署时不会自动启用（optional=true 不传递依赖） |
| 缺点 | 仅适用开发环境；双类加载器可能导致类加载相关问题；文件监听有延迟；与某些框架集成有兼容性问题 |

---

## 三、实战应用

### 3.1 JAR 打包部署完整流程

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 应用从打包到运行的完整 JAR 部署流程，含基础运行、外部配置、后台运行等方式 |
| 能做什么 | Maven 打包跳过测试；java -jar 运行；指定外部配置文件；nohup 后台运行；config 目录自动加载 |
| 怎么用 | `mvn clean package -DskipTests`；`java -jar target/app.jar --spring.profiles.active=prod` |
| 原理和工作流程 | 完整部署流程：1. 打包 mvn clean package -DskipTests 跳过测试加速生成 fat jar。2. 基础运行 java -jar target/app.jar。3. 指定外部配置 java -jar target/app.jar --spring.config.location=./config/application.yml。4. 后台运行（Linux）nohup java -jar app.jar --spring.profiles.active=prod > /dev/null 2>&1 & 将输出重定向到空设备并后台运行。5. 外部配置文件覆盖（推荐方式）将 application.yml 放到 jar 同级 config 目录自动加载，配合 --spring.profiles.active=prod 激活生产环境。config 目录的配置优先级高于 jar 包内配置 |
| 缺点 | 单机部署无高可用；nohup 进程管理需额外脚本；端口冲突需手动处理；日志输出需单独配置文件 |

### 3.2 Docker 部署

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 应用的 Docker 部署方案，含基础 Dockerfile 和多阶段构建两种方式 |
| 能做什么 | 基础 Dockerfile 打包 fat jar；多阶段构建减小镜像体积；构建镜像运行容器；查看容器日志 |
| 怎么用 | `docker build -t myapp:latest .`；`docker run -d --name myapp -p 8080:8080 myapp:latest` |
| 原理和工作流程 | 基础 Dockerfile 基于 eclipse-temurin JRE 基础镜像，COPY fat jar，EXPOSE 端口，ENTRYPOINT 执行 java -jar。多阶段构建减小镜像体积：阶段一构建用 maven 基础镜像，先 COPY pom.xml 并 mvn dependency:go-offline 下载依赖利用缓存层，再 COPY src 并 mvn clean package -DskipTests 编译打包。阶段二运行用 eclipse-temurin JRE 基础镜像（比 JDK 镜像小），COPY --from=builder 构建产物，EXPOSE 端口 ENTRYPOINT 运行。多阶段构建最终镜像只含 JRE 和 fat jar 不含 Maven 和源码体积大幅减小。构建后 docker run -d 后台运行 -p 端口映射，docker logs -f 查看日志 |
| 缺点 | 基础 Dockerfile 镜像仍较大未分离构建环境；多阶段构建配置复杂；容器时区默认非东八区需设置；镜像层缓存失效导致重建慢 |

### 3.3 多环境配置管理

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 application.yml 公共配置加 application-{profile}.yml 环境配置实现多环境管理的方案 |
| 能做什么 | 公共配置放 application.yml；环境差异配置放 application-{profile}.yml；环境变量切换 Profile；默认 dev |
| 怎么用 | `spring.profiles.active: ${SPRING_PROFILES_ACTIVE:dev}` 通过环境变量切换默认 dev |
| 原理和工作流程 | 项目结构在 src/main/resources 下放 application.yml（公共配置如应用名）、application-dev.yml（开发环境端口 8080 DEBUG 日志）、application-test.yml（测试环境）、application-prod.yml（生产环境端口 8080 优雅停机 INFO/WARN 日志）。公共配置 application.yml 中 spring.profiles.active 设为 ${SPRING_PROFILES_ACTIVE:dev}，通过环境变量 SPRING_PROFILES_ACTIVE 切换环境，未设置时默认 dev。生产配置开启 server.shutdown=graceful 优雅停机，日志级别 com.example=INFO root=WARN 减少日志量。各环境配置只写差异部分公共配置共享 |
| 缺点 | 配置文件分散管理成本高；环境变量未设置导致默认 dev 上生产风险；配置覆盖关系复杂；敏感配置不应入库需加密 |

### 3.4 优雅停机

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 通过 server.shutdown=graceful 配合 @PreDestroy 实现的优雅停机机制 |
| 能做什么 | 拒绝新请求；等待正在处理的请求完成；触发 @PreDestroy 释放资源；关闭内嵌容器；支持超时配置 |
| 怎么用 | `server.shutdown: graceful` + `spring.lifecycle.timeout-per-shutdown-phase: 30s` |
| 原理和工作流程 | 配置 server.shutdown=graceful 开启优雅停机（默认 immediate 立即停机），spring.lifecycle.timeout-per-shutdown-phase=30s 设置等待最长 30 秒处理完请求。优雅停机流程：1. 收到 SIGTERM 信号（kill 命令或容器停止）。2. Spring Boot 停止接收新请求。3. 等待正在处理的请求完成最长等待 timeout-per-shutdown-phase。4. 触发 @PreDestroy 销毁回调释放资源（关闭连接池、刷新缓存、保存状态）。5. 关闭内嵌容器。6. 进程退出。配合 @PreDestroy 注解在 Bean 销毁时执行清理逻辑。在 Docker/K8s 环境中需配合 SIGTERM 信号和合理的 terminationGracePeriodSeconds（需大于应用等待时间）避免被强杀 |
| 缺点 | 等待超时后仍会强杀未完成请求；K8s 宽限期设置不当导致强杀；@PreDestroy 执行慢拖长停机；长连接请求难以优雅关闭 |

---

## 四、常见面试题

### 1. Spring Boot 的 fat jar 是如何工作的？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 通过 repackage 打包的 fat jar 结构及自定义类加载器启动机制 |
| 能做什么 | 项目 class 放 BOOT-INF/classes；依赖 JAR 放 BOOT-INF/lib；JarLauncher 启动；LaunchedURLClassLoader 加载嵌套 JAR |
| 怎么用 | `java -jar app.jar` 启动 fat jar |
| 原理和工作流程 | fat jar 通过 spring-boot-maven-plugin 的 repackage goal 重新打包，将项目 class 放入 BOOT-INF/classes，第三方依赖放入 BOOT-INF/lib。启动时由 JarLauncher 加载，MANIFEST.MF 的 Main-Class 指向 JarLauncher。JarLauncher 创建自定义的 LaunchedURLClassLoader 读取嵌套 JAR 中的 class 文件。标准 URLClassLoader 无法读取 JAR 中的 JAR，因此需要自定义类加载器。LaunchedURLClassLoader 加载 BOOT-INF/lib 下的依赖后，通过反射调用项目主类的 main 方法，SpringApplication.run 启动应用 |
| 缺点 | fat jar 体积大含全部依赖；嵌套 JAR 类加载对调试不友好；依赖冲突排查困难；无法共享容器依赖 |

### 2. Spring Boot 配置文件的优先级是怎样的？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 多来源配置属性按固定优先级覆盖的规则 |
| 能做什么 | 命令行参数最高；环境变量次之；jar 包外高于包内；profile 配置高于默认；高优先级覆盖低优先级 |
| 怎么用 | `java -jar app.jar --server.port=9090` 命令行参数最高优先级 |
| 原理和工作流程 | 从高到低：命令行参数 > 环境变量 > jar 包外 application-{profile}.yml > jar 包内 application-{profile}.yml > jar 包外 application.yml > jar 包内 application.yml。高优先级覆盖低优先级，同名属性后者覆盖前者。Spring Boot 通过 Environment 抽象管理配置属性，按优先级构造 PropertySource 链，获取属性时从高到低遍历首个命中即返回。jar 包外配置覆盖 jar 包内配置便于不改包修改配置，profile 配置覆盖默认配置实现环境隔离。命令行参数优先级最高便于临时覆盖 |
| 缺点 | 优先级层级多容易混淆；同名属性跨来源覆盖排查困难；环境变量命名需转换；外部配置位置不当不生效 |

### 3. spring-boot-devtools 的热部署原理是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | spring-boot-devtools 基于双类加载器机制实现快速重启的热部署原理 |
| 能做什么 | BaseClassLoader 加载第三方依赖不变；RestartClassLoader 加载项目代码；修改后只重载项目代码；比完整重启快 5-10 倍 |
| 怎么用 | 引入 `spring-boot-devtools` 依赖 scope runtime optional true |
| 原理和工作流程 | devtools 使用双类加载器机制：BaseClassLoader 加载第三方依赖（很少变化不重载），RestartClassLoader 加载项目代码（修改后重新加载）。代码修改后 devtools 监听到文件变化，丢弃旧 RestartClassLoader 创建新 RestartClassLoader 重新加载项目代码，BaseClassLoader 保持不变避免重新加载大量第三方依赖。因只需重载项目代码而非全部依赖，重启速度比完整重启快 5-10 倍。devtools 仅用于开发环境，optional=true 使依赖不传递生产部署不生效 |
| 缺点 | 仅适用开发环境；双类加载器可能导致类加载问题；文件监听有延迟；与某些框架集成有兼容性问题 |

### 4. 如何实现 Spring Boot 优雅停机？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 通过 graceful 配置和 @PreDestroy 实现的优雅停机方案 |
| 能做什么 | 配置 graceful 停机；设置等待超时；拒绝新请求等待处理中请求；触发销毁回调释放资源 |
| 怎么用 | `server.shutdown=graceful` + `spring.lifecycle.timeout-per-shutdown-phase=30s` |
| 原理和工作流程 | 配置 server.shutdown=graceful 和 spring.lifecycle.timeout-per-shutdown-phase=30s。收到停机信号（SIGTERM）后 Spring Boot 拒绝新请求，等待正在处理的请求完成最长 30 秒，触发 @PreDestroy 回调释放资源（关闭连接池、刷新缓存），最后关闭容器。在 Docker/K8s 环境中需配合 SIGTERM 信号和合理的 terminationGracePeriodSeconds（需大于应用 timeout-per-shutdown-phase）避免容器在等待期被强杀。@PreDestroy 注解标注的方法在 Bean 销毁时执行清理逻辑 |
| 缺点 | 等待超时后仍强杀未完成请求；K8s 宽限期设置不当导致强杀；@PreDestroy 执行慢拖长停机；长连接难优雅关闭 |

### 5. Spring Boot 如何切换内嵌容器？

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 在 Tomcat、Jetty、Undertow 三种内嵌容器间切换的方法 |
| 能做什么 | 排除默认 Tomcat starter；引入目标容器 starter；Spring Boot 自动适配；业务代码无需修改 |
| 怎么用 | 排除 `spring-boot-starter-tomcat` 引入 `spring-boot-starter-undertow` |
| 原理和工作流程 | 在 spring-boot-starter-web 中通过 exclusions 排除 spring-boot-starter-tomcat（默认容器），然后引入 spring-boot-starter-jetty 或 spring-boot-starter-undertow。Spring Boot 通过 ServletWebServerFactory 抽象自动适配新容器，检测到类路径下的容器工厂类（如 UndertowServletWebServerFactory）创建对应容器实例，业务代码无需修改。切换场景通常是为获得更高并发性能（Undertow 基于 NIO）或更快启动速度（Jetty 轻量） |
| 缺点 | 切换后部分 Tomcat 特有配置失效；新容器生态文档不如 Tomcat；依赖冲突需彻底排除；非必要切换增加复杂度 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | Spring Boot 部署运维中外部配置不生效、环境变量命名、镜像过大、停机被强杀等高频问题汇总 |
| 能做什么 | 修正配置文件位置；规范环境变量命名；多阶段构建减小镜像；调大 K8s 宽限期；排除 devtools；设置时区 |
| 怎么用 | 配置放 `config/` 目录；`SERVER_PORT` 大写下划线；JRE 基础镜像多阶段构建；`-Duser.timezone=Asia/Shanghai` |
| 原理和工作流程 | 外部配置不生效因配置文件位置不对，需放到 jar 同级 config 目录（优先级最高）或用 --spring.config.location 指定。环境变量不生效因命名格式不对，需将属性名转为大写下划线 server.port -> SERVER_PORT。Docker 镜像过大因使用 JDK 而非 JRE 基础镜像，需用多阶段构建加 JRE 基础镜像或使用 jib 插件。优雅停机被强杀因 K8s terminationGracePeriodSeconds 小于应用等待时间，需调大 K8s 宽限期（大于 timeout-per-shutdown-phase）。devtools 生产环境生效因未排除依赖，需设 optional=true 或 Maven 中设 excludeDevtools。时区问题因 JVM 默认时区非东八区，需启动参数加 -Duser.timezone=Asia/Shanghai，Docker 中设 TZ=Asia/Shanghai |
| 缺点 | 配置位置规则多易混淆；环境变量命名转换易遗漏；多阶段构建增加构建时间；K8s 宽限期过长影响滚动更新；时区设置需多处一致 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./08-SpringBoot部署与运维.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
