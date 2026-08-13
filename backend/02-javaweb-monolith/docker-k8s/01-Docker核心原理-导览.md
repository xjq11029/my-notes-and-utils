# Docker 核心原理 导览

> 定位：五维框架浓缩提炼 01-Docker核心原理.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./01-Docker核心原理.md)。
> 前置知识：无

---

## 一、核心概念

### 1.1 容器 vs 虚拟机

| 维度 | 内容 |
|------|------|
| 是什么 | 容器是共享宿主机内核的轻量级应用运行环境，虚拟机是带完整 Guest OS 的虚拟化环境 |
| 能做什么 | 容器提供进程级隔离、秒级启动、数百密度部署；虚拟机提供硬件级隔离与强安全性 |
| 怎么用 | `docker run -d nginx` 启动容器；Hypervisor 创建并引导虚拟机 |
| 原理和工作流程 | 容器基于 Linux Namespace 实现进程视图隔离，Cgroups 限制资源，共享内核省去 OS 引导开销，启动只需拉起进程；虚拟机通过 Hypervisor 虚拟硬件，每个 VM 运行完整 Guest OS，启动需引导整个操作系统，产生 5-15% 性能损耗 |
| 缺点 | 容器共享内核导致隔离性弱于虚拟机，存在容器逃逸风险；不同内核的应用无法在容器中运行，如 Windows 应用无法跑在 Linux 容器上 |

### 1.2 Docker 三大核心

| 维度 | 内容 |
|------|------|
| 是什么 | 镜像、容器、仓库是 Docker 的三大核心概念，分别对应类、实例、商店 |
| 能做什么 | 镜像提供只读模板定义应用环境；容器是镜像的运行实例附加可写层；仓库用于存储和分发镜像 |
| 怎么用 | `docker pull nginx:1.25` 拉取镜像；`docker run nginx` 创建容器；`docker push` 推送镜像 |
| 原理和工作流程 | 镜像是分层只读的文件系统模板，由 Dockerfile 指令逐层构建；容器在镜像层之上挂载可写层，通过 Copy-on-Write 修改文件；仓库（Docker Hub、Harbor）作为镜像中央存储，用标签管理版本 |
| 缺点 | 镜像层过多导致构建和拉取性能下降；容器可写层与镜像绑定，容器删除后可写层丢失；公共仓库存在镜像来源不可信的安全风险 |

### 1.3 Docker 架构

| 维度 | 内容 |
|------|------|
| 是什么 | Docker 采用 Client-Daemon-runtime 三层架构，由 CLI、守护进程、容器运行时组成 |
| 能做什么 | Client 发送命令；Daemon 管理镜像、容器、网络、存储；containerd 管理容器生命周期；runc 创建运行容器 |
| 怎么用 | `docker info` 查看 Daemon 信息；`docker version` 查看组件版本 |
| 原理和工作流程 | 用户通过 Docker CLI 发送 REST 请求到 Docker Daemon，Daemon 解析命令后调用 containerd 管理容器生命周期，containerd 进一步调用符合 OCI 标准的 runc 实际创建和运行容器，实现守护进程与运行时解耦 |
| 缺点 | Daemon 是单点，崩溃会影响所有容器；早期版本 Daemon 需 root 权限运行，存在安全风险；架构层级多增加调试复杂度 |

---

## 二、底层原理

### 2.1 镜像分层（UnionFS / Overlay2）

| 维度 | 内容 |
|------|------|
| 是什么 | 镜像分层是 Docker 基于 UnionFS（如 Overlay2）将镜像拆为多个只读层堆叠的技术 |
| 能做什么 | 共享基础层节省磁盘空间；利用缓存加速构建；只拉取差异层加快分发 |
| 怎么用 | `FROM openjdk:17` + `RUN apt-get install` + `COPY app.jar` 逐层构建 |
| 原理和工作流程 | 每个 Dockerfile 指令创建一个只读层，Overlay2 将各层堆叠为统一视图。容器运行时在镜像层之上添加可写层，采用 Copy-on-Write：读取时从上层向下查找返回首个匹配；修改时先从镜像层复制到容器层再修改；删除时在容器层创建 whiteout 标记 |
| 缺点 | 层数过多导致元数据膨胀和查找开销；跨层查找文件增加 IO 开销；写时复制带来首次修改的性能损耗 |

### 2.2 容器隔离（Namespace）

| 维度 | 内容 |
|------|------|
| 是什么 | Namespace 是 Linux 内核的进程隔离机制，Docker 用它实现容器间资源视图隔离 |
| 能做什么 | 隔离 PID、网络、挂载点、主机名、IPC、用户 ID 六类资源 |
| 怎么用 | `docker run --pid=host` 共享宿主机 PID 命名空间；默认每个容器独立隔离 |
| 原理和工作流程 | 容器启动时 dockerd 调用 runc 创建一组 Namespace，PID Namespace 给容器进程独立编号空间，Network Namespace 提供独立网络栈，Mount Namespace 隔离文件系统视图，UTS Namespace 隔离主机名，IPC Namespace 隔离信号量与消息队列，User Namespace 将容器内 root 映射为宿主机非 root 用户 |
| 缺点 | 共享内核意味着内核漏洞影响所有容器，隔离性弱于虚拟机；Namespace 无法隔离系统时间和内核模块；容器逃逸仍是安全风险 |

### 2.3 资源限制（Cgroups）

| 维度 | 内容 |
|------|------|
| 是什么 | Cgroups 是 Linux 内核的资源控制机制，Docker 用它限制容器的 CPU、内存、IO 等资源 |
| 能做什么 | 限制 CPU 核数、内存上限、磁盘 IO 权重、进程数量 |
| 怎么用 | `docker run --cpus=2 --memory=512m --pids-limit=100 nginx` |
| 原理和工作流程 | dockerd 为每个容器创建 cgroup 目录并写入限制值，CPU 子系统通过 cpu.cfs_quota_us 分配时间片，内存子系统通过 memory.limit_in_bytes 限制物理内存，超出限制的进程触发 OOM Killer 被杀掉，blkio 子系统控制磁盘读写带宽权重 |
| 缺点 | 只限制单一容器，无法防止宿主机整体资源耗尽；内存限制过严导致 OOM 频繁；IO 限制粒度粗，无法精确控制单文件读写 |

### 2.4 Dockerfile 核心指令

| 维度 | 内容 |
|------|------|
| 是什么 | Dockerfile 是描述镜像构建步骤的文本文件，由 FROM、RUN、COPY 等指令组成 |
| 能做什么 | 指定基础镜像；执行构建命令；复制文件；设置工作目录与环境变量；定义启动命令 |
| 怎么用 | `FROM openjdk:17-alpine` / `RUN apt-get install -y curl` / `CMD ["java","-jar","app.jar"]` |
| 原理和工作流程 | 每个指令对应镜像一层，构建时 dockerd 按顺序执行指令生成只读层。FROM 指定基础镜像作为底层，RUN 在容器中执行命令并提交为新层，COPY/ADD 将宿主文件复制到镜像，CMD 提供默认启动命令可被覆盖，ENTRYPOINT 定义不可覆盖的入口点，两者组合时 CMD 作为 ENTRYPOINT 的默认参数 |
| 缺点 | 指令顺序影响缓存命中率，顺序不当导致每次重建；ADD 的自动解压和 URL 下载行为不透明易出错；CMD 与 ENTRYPOINT 组合语义复杂，使用不当导致启动失败 |

---

## 三、实战应用

### 3.1 Spring Boot 应用容器化

| 维度 | 内容 |
|------|------|
| 是什么 | 将 Spring Boot 应用打包为 Docker 镜像并运行的技术，常用多阶段构建 |
| 能做什么 | 分离构建环境与运行环境；减小镜像体积；利用构建缓存 |
| 怎么用 | 第一阶段 `FROM maven:3.8-openjdk-17 AS build` 构建jar，第二阶段 `FROM openjdk:17-alpine` 复制jar运行 |
| 原理和工作流程 | 多阶段构建中第一阶段使用完整 Maven 镜像编译打包生成 jar，第二阶段基于轻量 JRE 镜像仅复制 jar，`COPY --from=build` 跨阶段拷贝产物，最终镜像不含源码和构建工具。ENTRYPOINT 通过 `sh -c` 解析 JAVA_OPTS 环境变量启动 java 进程 |
| 缺点 | 多阶段构建增加 Dockerfile 复杂度；Alpine 基于 musl libc，部分依赖库存在兼容性问题；JVM 堆内存需根据容器限制显式配置，否则可能超限被 OOM |

### 3.2 docker-compose 编排

| 维度 | 内容 |
|------|------|
| 是什么 | docker-compose 是定义和运行多容器 Docker 应用的工具，用 YAML 描述服务依赖 |
| 能做什么 | 一键启动多个服务；声明服务依赖和健康检查；管理数据卷与网络 |
| 怎么用 | `docker-compose up -d` 启动；`docker-compose down` 停止 |
| 原理和工作流程 | compose 解析 YAML 后调用 Docker API 为每个服务创建容器和网络，depends_on 控制启动顺序，`condition: service_healthy` 等待健康检查通过才启动依赖服务，volumes 声明命名卷实现数据持久化，ports 映射宿主机与容器端口 |
| 缺点 | 仅适用于单机编排，无法跨节点调度；服务发现依赖容器名 DNS，重启后可能失效；生产环境能力弱，复杂场景需 K8s |

### 3.3 镜像优化

| 维度 | 内容 |
|------|------|
| 是什么 | 通过选择轻量基础镜像、多阶段构建、减少层数等手段减小 Docker 镜像体积的方法 |
| 能做什么 | 选择 Alpine 镜像；多阶段构建；合并 RUN 命令；配置 .dockerignore；使用特定版本标签 |
| 怎么用 | `FROM openjdk:17-alpine` / `RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*` |
| 原理和工作流程 | Alpine 基于 musl 和 BusyBox，基础镜像仅 5MB；多阶段构建丢弃构建层；合并 RUN 指令减少层数并在同层清理缓存避免缓存层残留；.dockerignore 排除 target、node_modules 等目录减少构建上下文传输；特定版本标签保证镜像内容确定 |
| 缺点 | Alpine 的 musl libc 与 glibc 不兼容，部分 JNI 库可能无法运行；过度合并 RUN 降低缓存复用率；瘦身镜像缺少工具链增加排错难度 |

---

## 四、常见面试题

### 1. Docker 镜像分层的好处是什么？

| 维度 | 内容 |
|------|------|
| 是什么 | 镜像分层是 Docker 基于 UnionFS 将镜像拆分为多个只读层的机制 |
| 能做什么 | 共享基础层节省磁盘空间；缓存加速构建；差异层快速分发 |
| 怎么用 | `FROM ubuntu` 多个镜像共享该基础层 |
| 原理和工作流程 | 每个 Dockerfile 指令生成一个只读层，Overlay2 将各层联合挂载为统一文件系统。多个镜像引用相同基础层时只存储一份，构建时未变化的层命中缓存跳过执行，拉取时只下载本地缺失的层 |
| 缺点 | 层数过多导致元数据膨胀和查找开销；共享层修改会使所有引用镜像的缓存失效；跨层写时复制增加首次修改延迟 |

### 2. CMD 和 ENTRYPOINT 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | CMD 提供容器默认启动命令，ENTRYPOINT 定义不可覆盖的容器入口点 |
| 能做什么 | CMD 可被 docker run 参数覆盖；ENTRYPOINT 不可覆盖，参数追加其后；两者可组合使用 |
| 怎么用 | `ENTRYPOINT ["java"]` + `CMD ["-jar","app.jar"]` |
| 原理和工作流程 | docker run 时若提供命令参数则替换 CMD，但 ENTRYPOINT 保持不变，CMD 作为 ENTRYPOINT 的默认参数。exec 形式（JSON 数组）直接 exec 进程作为 PID 1，shell 形式通过 `/bin/sh -c` 启动导致信号传递失效 |
| 缺点 | shell 形式无法接收 SIGTERM 信号，影响容器优雅停止；CMD 被覆盖后默认参数丢失；覆盖与追加语义易混淆 |

### 3. 如何减小 Docker 镜像大小？

| 维度 | 内容 |
|------|------|
| 是什么 | 通过多种手段压缩 Docker 镜像最终体积的优化方法 |
| 能做什么 | 选 Alpine 镜像；多阶段构建；合并 RUN 清理缓存；.dockerignore；特定版本标签 |
| 怎么用 | `FROM openjdk:17-alpine` + 多阶段构建 + 合并 RUN |
| 原理和工作流程 | Alpine 基础镜像仅 5MB；多阶段构建丢弃构建工具层；合并 RUN 指令并同层 rm 清理避免缓存残留；.dockerignore 减少构建上下文；特定版本标签避免 latest 指向臃肿版本。综合优化可将 Java 镜像从 500MB 降至 100MB |
| 缺点 | Alpine 存在 musl libc 兼容性问题；过度合并降低缓存复用；瘦身镜像缺少调试工具 |

### 4. 容器和虚拟机的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 容器是共享内核的进程级隔离，虚拟机是独立 Guest OS 的硬件级隔离 |
| 能做什么 | 容器秒级启动、MB 级镜像、数百密度；虚拟机分钟级启动、GB 级镜像、数十密度 |
| 怎么用 | `docker run` 启动容器；Hypervisor 启动虚拟机 |
| 原理和工作流程 | 容器通过 Namespace 隔离进程视图，Cgroups 限制资源，共享宿主机内核避免 OS 引导开销；虚拟机通过 Hypervisor 虚拟硬件，每个 VM 运行完整 Guest OS，需引导整个操作系统产生 5-15% 性能损耗 |
| 缺点 | 容器隔离弱于虚拟机，存在逃逸风险；虚拟机资源开销大、启动慢、密度低；容器无法运行不同内核的应用 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | Docker 使用中常见错误及其现象、原因、解决方案的汇总 |
| 能做什么 | 避免容器数据丢失；防止 root 运行风险；避免 latest 标签不一致；控制层数；设置资源限制 |
| 怎么用 | 用 Volume 持久化数据；Dockerfile 中创建非 root 用户；使用 `nginx:1.25.3` 明确标签；合并 RUN；设置 `--cpus` `--memory` |
| 原理和工作流程 | 容器可写层随容器删除而丢失，需 Volume 外置存储；root 用户拥有最高权限易被逃逸利用；latest 标签动态指向导致环境漂移；每个 RUN/COPY/ADD 创建新层增加体积；未限制资源时容器可耗尽宿主机资源影响其他容器 |
| 缺点 | 避坑指南无法覆盖所有场景，新问题需结合日志和文档排查；部分解决方案如非 root 用户可能影响应用兼容性 |

---

## 本章学习自检

本节为辅助内容，无五维表格。

---

> [返回原文](./01-Docker核心原理.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
