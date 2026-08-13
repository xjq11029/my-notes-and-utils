# Spring Boot 部署与运维

> 学习路线对应：第2周 -- Spring Boot 框架
> 前置知识：Spring Boot 基础、Maven、Docker 基础
> 预计学习时间：1-2 天

## 一、核心概念

### 1.1 部署方式演进

| 阶段 | 部署方式 | 特点 | 局限 |
|------|---------|------|------|
| **传统阶段** | WAR 部署到 Tomcat | 需单独安装 Tomcat，打包为 WAR | 环境耦合重，多应用共享容器 |
| **内嵌阶段** | JAR 部署（Spring Boot） | 内嵌 Tomcat，`java -jar` 直接运行 | 单机部署，水平扩展需手动管理 |
| **容器化阶段** | Docker 部署 | 环境隔离，一次构建到处运行 | 单节点编排，需配合 K8s |
| **云原生阶段** | Kubernetes 部署 | 自动伸缩、滚动更新、自愈 | 学习曲线陡，运维复杂度高 |

```
WAR（外部 Tomcat） -> JAR（内嵌 Tomcat） -> Docker（容器化） -> K8s（编排调度）
```

> **生活化类比：部署方式演进就像交通方式演进** —— ① **WAR 部署（火车）**：你需要先修铁路（安装 Tomcat），再买火车票（打 WAR 包），然后按铁路时刻表运行（依赖外部容器），基础设施重、灵活性差；② **JAR 部署（汽车）**：汽车自带发动机（内嵌 Tomcat），加油就能跑（java -jar），不依赖外部铁路（无需独立容器），但一辆车只能跑一条路（单机部署，扩展需手动管理）；③ **Docker 部署（集装箱运输）**：标准化集装箱（Docker 镜像）可以装上轮船、火车、卡车（任何支持 Docker 的环境），一次打包到处运输（一次构建到处运行），但单辆卡车需要自己调度；④ **K8s 部署（物流调度系统）**：像顺丰物流网络，自动调度集装箱（Pod 调度），根据包裹量增减车辆（自动伸缩），车辆坏了自动换新车（自愈），还能滚动更新换代（滚动更新）。

> 📖 **参考链接**：
> - [Spring Boot Reference Documentation](https://docs.spring.io/spring-boot/docs/) -- Spring Boot 官方文档（部署方式、内嵌容器、fat jar 打包）
> - [Spring Framework Reference](https://docs.spring.io/spring-framework/reference/) -- Spring 框架参考文档（外部化配置、Profile 环境隔离）

### 1.2 Spring Boot 内嵌容器

| 容器 | 特点 | 并发性能 | 适用场景 |
|------|------|---------|---------|
| **Tomcat** | Spring Boot 默认，生态成熟 | 中 | 通用 Web 应用 |
| **Jetty** | 轻量级，启动快 | 中 | 对启动速度有要求、嵌入式场景 |
| **Undertow** | 基于 NIO，内存占用低 | 高 | 高并发、资源受限环境 |

```xml
<!-- 切换为 Undertow -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-undertow</artifactId>
</dependency>
```

---

## 二、底层原理

### 2.1 JAR 打包原理

Spring Boot 通过 `spring-boot-maven-plugin` 的 `repackage` goal 将普通 JAR 重新打包为可执行的 fat jar。

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <executions>
                <execution>
                    <goals>
                        <goal>repackage</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

**repackage 过程：**

```
原始 JAR（项目编译后的 class + 依赖）
    ↓ spring-boot-maven-plugin repackage
fat JAR 结构：
    app.jar
    ├── META-INF/
    │     └── MANIFEST.MF          (Main-Class: org.springframework.boot.loader.JarLauncher)
    ├── BOOT-INF/
    │     ├── classes/              (项目自身的 class 文件)
    │     └── lib/                  (所有第三方依赖 JAR)
    └── org/springframework/boot/loader/  (启动器代码)
```

**启动流程：**

```
1. java -jar app.jar
2. JVM 读取 MANIFEST.MF，找到 Main-Class: JarLauncher
3. JarLauncher 执行 main() 方法
4. 创建 LaunchedURLClassLoader（专门加载 BOOT-INF/lib 下的 JAR）
5. 通过反射调用项目主类的 main() 方法
6. SpringApplication.run() 启动应用
```

**关键点：** fat jar 使用自定义类加载器 `LaunchedURLClassLoader`，可读取嵌套 JAR 内部的 class 文件（标准 URLClassLoader 无法读取 JAR 中的 JAR）。

> **生活化类比：fat jar 就像压缩行李箱** —— 普通的 Java JAR 像一个只装了自己衣服的小行李箱（只含项目 class），出门还得额外带几个大箱子（第三方依赖 JAR 分别放置）。而 Spring Boot 的 fat jar 就像一个"压缩行李箱"：启动器代码（JarLauncher）是行李箱的拉杆和轮子（箱子的自身结构），`BOOT-INF/classes/` 是你的私人衣物（项目 class），`BOOT-INF/lib/` 是装好的日用品包（所有第三方依赖 JAR）。一个箱子搞定所有东西，拉着就能出门（java -jar 一键启动）。关键在于这个箱子用了特殊的"压缩技术"（LaunchedURLClassLoader），能直接从箱中取出日用品包里的东西（读取嵌套 JAR 中的 class），普通行李箱（标准 URLClassLoader）做不到这点——它只能打开箱子最外层，看不到里面的小包。

> 📖 **参考链接**：
> - [Spring Boot Reference Documentation](https://docs.spring.io/spring-boot/docs/) -- Spring Boot 官方文档（可执行 JAR 打包、LaunchedURLClassLoader 类加载机制）

### 2.2 外部化配置

Spring Boot 支持多种配置来源，按优先级从高到低排列：

| 优先级 | 配置来源 | 示例 |
|--------|---------|------|
| 1 | 命令行参数 | `java -jar app.jar --server.port=9090` |
| 2 | 环境变量 | `SERVER_PORT=9090 java -jar app.jar` |
| 3 | application-{profile}.yml（jar 包外） | `./config/application-prod.yml` |
| 4 | application-{profile}.yml（jar 包内） | `classpath:/application-prod.yml` |
| 5 | application.yml（jar 包外） | `./config/application.yml` |
| 6 | application.yml（jar 包内） | `classpath:/application.yml` |

**重要原则：** 高优先级覆盖低优先级，jar 包外配置覆盖 jar 包内配置，profile 配置覆盖默认配置。

```bash
# 命令行参数覆盖
java -jar app.jar --server.port=9090 --spring.profiles.active=prod

# 外部配置文件（放在 jar 同级 config 目录，自动加载）
mkdir config
echo "server.port: 9090" > config/application.yml
java -jar app.jar
```

### 2.3 Profile 环境隔离

```java
// 方式一：@Profile 注解
@Configuration
@Profile("prod")
public class ProdDataSourceConfig {
    @Bean
    public DataSource dataSource() { /* 生产数据源 */ }
}

// 方式二：配置文件分组
```

```yaml
# application.yml（公共配置）
spring:
  profiles:
    active: dev  # 默认激活 dev 环境
server:
  port: 8080

---
# application-dev.yml（开发环境）
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/dev_db

---
# application-prod.yml（生产环境）
spring:
  datasource:
    url: jdbc:mysql://prod-host:3306/prod_db
```

**激活 Profile 的方式：**

```bash
# 命令行
java -jar app.jar --spring.profiles.active=prod

# 环境变量
SPRING_PROFILES_ACTIVE=prod java -jar app.jar

# 配置文件
spring.profiles.active=prod
```

### 2.4 热部署（spring-boot-devtools）

devtools 通过双类加载器机制实现快速重启，比完整重启快 5-10 倍。

```
类加载器层级：
  BaseClassLoader（第三方依赖 JAR，很少变化）
    └── RestartClassLoader（项目自身 class，修改后重新加载）

工作原理：
1. 应用启动时，第三方依赖由 BaseClassLoader 加载（不变）
2. 项目代码由 RestartClassLoader 加载
3. 代码修改后，devtools 监听到文件变化
4. 丢弃旧 RestartClassLoader，创建新 RestartClassLoader 重新加载项目代码
5. BaseClassLoader 保持不变，避免重新加载大量第三方依赖
```

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <scope>runtime</scope>
    <optional>true</optional>
</dependency>
```

**注意：** devtools 仅用于开发环境，生产部署时不会自动启用（optional=true 不传递依赖）。

---

## 三、实战应用

### 3.1 JAR 打包部署完整流程

```bash
# 1. 打包（跳过测试加速）
mvn clean package -DskipTests

# 2. 运行（基础方式）
java -jar target/app.jar

# 3. 指定外部配置
java -jar target/app.jar --spring.config.location=./config/application.yml

# 4. 后台运行（Linux）
nohup java -jar app.jar --spring.profiles.active=prod > /dev/null 2>&1 &

# 5. 外部配置文件覆盖（推荐方式）
# 将 application.yml 放到 jar 同级的 config/ 目录，自动加载
java -jar app.jar --spring.profiles.active=prod
```

### 3.2 Docker 部署

**基础 Dockerfile：**

```dockerfile
FROM eclipse-temurin:17-jre-jammy
VOLUME /tmp
COPY target/app.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar", "--spring.profiles.active=prod"]
```

**多阶段构建（减小镜像体积）：**

```dockerfile
# 阶段一：构建
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline              # 先下载依赖（利用缓存层）
COPY src ./src
RUN mvn clean package -DskipTests

# 阶段二：运行
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app
COPY --from=builder /build/target/app.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

```bash
# 构建镜像
docker build -t myapp:latest .

# 运行容器
docker run -d --name myapp -p 8080:8080 myapp:latest

# 查看日志
docker logs -f myapp
```

**Spring Boot 应用从开发到生产的完整部署流程 Mermaid 图：**

```mermaid
%%{init: {'themeVariables': {'fontSize': '16px'}}}%%
flowchart TD
    A["开发环境<br/>编写代码 + application-dev.yml"] --> B["mvn clean package -DskipTests<br/>spring-boot-maven-plugin repackage"]
    B --> C["生成 fat JAR<br/>BOOT-INF/classes + BOOT-INF/lib"]
    C --> D{"部署方式选择"}

    D -->|"传统部署"| E["java -jar app.jar<br/>--spring.profiles.active=prod"]
    E --> F["nohup 后台运行<br/>外部 config/ 目录覆盖配置"]

    D -->|"Docker 部署"| G["编写 Dockerfile<br/>多阶段构建减小镜像"]
    G --> H["docker build -t myapp:latest ."]
    H --> I["docker run -d -p 8080:8080<br/>-e SPRING_PROFILES_ACTIVE=prod"]
    I --> J["容器启动，应用就绪"]

    D -->|"K8s 部署"| K["推送镜像到 Registry"]
    K --> L["编写 Deployment + Service YAML"]
    L --> M["kubectl apply -f deployment.yaml"]
    M --> N["K8s 调度 Pod，自动拉取镜像"]
    N --> O["健康检查通过，服务上线"]

    F --> P["生产环境运行"]
    J --> P
    O --> P

    P --> Q{"需要停机？"}
    Q -->|"收到 SIGTERM"| R["优雅停机：拒绝新请求"]
    R --> S["等待正在处理的请求完成<br/>（最长 30s）"]
    S --> T["@PreDestroy 释放资源"]
    T --> U["关闭内嵌容器，进程退出"]

    style D["部署方式决策点"]
    style R["优雅停机流程"]
```

> 📖 **参考链接**：
> - [Spring Boot Reference Documentation](https://docs.spring.io/spring-boot/docs/) -- Spring Boot 官方文档（Docker 部署、K8s 集成、优雅停机配置）

### 3.3 多环境配置管理

```
项目结构：
  src/main/resources/
    ├── application.yml          (公共配置)
    ├── application-dev.yml      (开发环境)
    ├── application-test.yml     (测试环境)
    └── application-prod.yml     (生产环境)
```

```yaml
# application.yml（公共配置）
spring:
  application:
    name: order-service
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}  # 通过环境变量切换，默认 dev

# application-dev.yml
server:
  port: 8080
logging:
  level:
    com.example: DEBUG

# application-prod.yml
server:
  port: 8080
  shutdown: graceful            # 优雅停机
logging:
  level:
    com.example: INFO
    root: WARN
```

### 3.4 优雅停机

```yaml
server:
  shutdown: graceful           # 开启优雅停机（默认为 immediate）
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s  # 等待最长 30 秒处理完请求
```

```java
// 配合 @PreDestroy 释放资源
@Component
public class ResourceHolder {

    @PreDestroy
    public void cleanup() {
        // 关闭连接池、刷新缓存、保存状态
        System.out.println("应用关闭，释放资源...");
    }
}
```

**优雅停机流程：**

```
1. 收到 SIGTERM 信号（kill 命令或容器停止）
2. Spring Boot 停止接收新请求
3. 等待正在处理的请求完成（最长等待 timeout-per-shutdown-phase）
4. 触发 @PreDestroy 销毁回调
5. 关闭内嵌容器
6. 进程退出
```

---

## 四、常见面试题（附答案）

### 1. Spring Boot 的 fat jar 是如何工作的？

fat jar 通过 `spring-boot-maven-plugin` 的 repackage goal 重新打包，将项目 class 放入 `BOOT-INF/classes`，第三方依赖放入 `BOOT-INF/lib`。启动时由 `JarLauncher` 加载，使用自定义的 `LaunchedURLClassLoader` 读取嵌套 JAR 中的 class 文件。标准 URLClassLoader 无法读取 JAR 中的 JAR，因此需要自定义类加载器。

### 2. Spring Boot 配置文件的优先级是怎样的？

从高到低：命令行参数 > 环境变量 > jar 包外 application-{profile}.yml > jar 包内 application-{profile}.yml > jar 包外 application.yml > jar 包内 application.yml。高优先级覆盖低优先级，同名属性后者覆盖前者。

### 3. spring-boot-devtools 的热部署原理是什么？

devtools 使用双类加载器机制：BaseClassLoader 加载第三方依赖（不变），RestartClassLoader 加载项目代码。代码修改后只需重新加载 RestartClassLoader，避免重新加载大量第三方依赖，重启速度比完整重启快 5-10 倍。

### 4. 如何实现 Spring Boot 优雅停机？

配置 `server.shutdown=graceful` 和 `spring.lifecycle.timeout-per-shutdown-phase=30s`。收到停机信号后，Spring Boot 拒绝新请求，等待正在处理的请求完成（最长 30 秒），触发 `@PreDestroy` 回调释放资源，最后关闭容器。在 Docker/K8s 环境中需配合 `SIGTERM` 信号和合理的 `terminationGracePeriodSeconds`。

### 5. Spring Boot 如何切换内嵌容器？

在 `spring-boot-starter-web` 中排除 `spring-boot-starter-tomcat`，然后引入 `spring-boot-starter-jetty` 或 `spring-boot-starter-undertow`。切换后无需修改业务代码，Spring Boot 自动适配新容器。

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| 外部配置不生效 | 配置文件被忽略 | 配置文件位置不对 | 放到 jar 同级 `config/` 目录（优先级最高）；或用 `--spring.config.location` 指定 |
| 环境变量不生效 | 配置未覆盖 | 环境变量命名格式不对 | 将属性名转为大写下划线：`server.port` -> `SERVER_PORT` |
| Docker 镜像过大 | 镜像超过 1GB | 使用 JDK 而非 JRE 基础镜像 | 使用多阶段构建 + JRE 基础镜像；或使用 jib 插件 |
| 优雅停机被强杀 | 请求处理到一半被中断 | K8s `terminationGracePeriodSeconds` 小于应用等待时间 | 调大 K8s 宽限期（需大于 `timeout-per-shutdown-phase`） |
| devtools 生产环境生效 | 应用频繁重启 | 未排除 devtools 依赖 | 设 `optional=true`；或 Maven 中设 `excludeDevtools` |
| 时区问题 | 日志时间与实际差 8 小时 | JVM 默认时区非东八区 | 启动参数加 `-Duser.timezone=Asia/Shanghai`；Docker 中设 `TZ=Asia/Shanghai` |

---

## 本章学习自检

完成本章学习后，应该能够：
- [ ] 用自己的话解释部署方式演进、fat jar 打包原理、LaunchedURLClassLoader、外部化配置优先级
- [ ] 完成 JAR 打包部署、Docker 多阶段构建、多环境配置管理、优雅停机配置
- [ ] 回答常见面试题（fat jar 原理、配置优先级、devtools 热部署、优雅停机、容器切换）
- [ ] 识别并避免常见错误（外部配置位置、环境变量命名、镜像体积、停机被强杀、时区问题）

---

> **学习导航**：
> - 返回 [学习路线总览](../../README.md)
> - 本模块其他文件：[06-Web核心与Servlet基础](./06-Web核心与Servlet基础.md) | [07-日志整合与监控](./07-日志整合与监控.md) | [05-Spring-Boot笔面试题集](./05-Spring-Boot笔面试题集.md)
> - 实战应用：[电商订单实时统计分析平台](../../extensions/project/01-电商订单实时统计分析平台.md)
