# Kubernetes 核心概念 导览

> 定位：五维框架浓缩提炼 02-Kubernetes核心概念.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./02-Kubernetes核心概念.md)。
> 前置知识：[Docker核心原理](./01-Docker核心原理-导览.md)

---

## 一、核心概念

### 1.1 K8s 架构

| 维度 | 内容 |
|------|------|
| 是什么 | K8s 集群由 Master 控制平面和 Node 工作节点组成的主从架构 |
| 能做什么 | Master 负责调度、控制、存储状态；Node 负责运行容器应用并上报状态 |
| 怎么用 | `kubectl get nodes` 查看节点；`kubectl cluster-info` 查看集群信息 |
| 原理和工作流程 | Master 的 API Server 作为集群统一入口处理所有 REST 请求并将状态存入 etcd，Scheduler 为新 Pod 选择 Node，Controller Manager 通过调谐循环维护期望状态。Node 上 kubelet 管理 Pod 生命周期并上报状态，kube-proxy 通过 iptables/IPVS 实现 Service 负载均衡，Container Runtime 实际运行容器 |
| 缺点 | Master 是单点，etcd 故障导致集群不可用；控制平面组件多，运维复杂；大规模集群下 API Server 成为性能瓶颈 |

### 1.2 核心资源对象

| 维度 | 内容 |
|------|------|
| 是什么 | Pod、Deployment、Service、Ingress 等是 K8s 管理的核心资源对象 |
| 能做什么 | Pod 承载容器；Deployment 管理副本与更新；Service 提供稳定访问；Ingress 管理外部入口；ConfigMap/Secret 存配置；StatefulSet/DaemonSet 管理特殊工作负载 |
| 怎么用 | `kubectl create deployment` / `kubectl expose` / `kubectl apply -f ingress.yaml` |
| 原理和工作流程 | Pod 是最小调度单位内容器共享网络和存储；Deployment 通过 ReplicaSet 控制 Pod 副本数；Service 通过标签选择器关联 Pod 并提供固定 IP；Ingress 根据域名和路径路由到 Service；ConfigMap 和 Secret 以环境变量或卷形式注入 Pod；StatefulSet 为每个 Pod 分配固定序号和存储 |
| 缺点 | 资源对象种类多学习曲线陡；Pod ephemeral 需要 Service 配合才能稳定访问；StatefulSet 调度和扩缩容复杂 |

### 1.3 声明式 API

| 维度 | 内容 |
|------|------|
| 是什么 | 用户描述期望状态由 K8s 自动调谐到实际状态的 API 设计模式 |
| 能做什么 | 描述副本数、资源配置、更新策略；自动修复偏差；支持滚动更新与回滚 |
| 怎么用 | `kubectl apply -f deployment.yaml` 提交期望状态 |
| 原理和工作流程 | 用户提交 YAML 描述期望状态（如 3 个副本），Controller Manager 读取期望状态并与实际状态对比，发现差异后触发调谐循环创建或删除 Pod，直到实际状态等于期望状态。该循环持续运行，任何偏差都会被自动修正 |
| 缺点 | 调谐是异步的，状态收敛需要时间；声明式语义难以表达复杂的过程式操作；调试时难以追踪调谐过程的中间状态 |

---

## 二、底层原理

### 2.1 Pod 调度流程

| 维度 | 内容 |
|------|------|
| 是什么 | Scheduler 为新创建的 Pod 选择最合适 Node 运行的过程 |
| 能做什么 | 预选过滤不满足条件的 Node；优选对剩余 Node 打分；绑定 Pod 到得分最高的 Node |
| 怎么用 | `kubectl describe pod <name>` 查看调度结果和 Events |
| 原理和工作流程 | 用户创建 Pod 后 Scheduler 监听未调度的 Pod，预选阶段过滤掉资源不足、NodeSelector 不匹配、Taints 不容忍的 Node，优选阶段根据资源均衡度、镜像本地性、Pod 亲和性对剩余 Node 打分，选择最高分 Node 绑定 Pod，目标 Node 的 kubelet 接收绑定后创建并启动容器 |
| 缺点 | 调度决策基于当前快照，集群状态变化导致后续调度不均衡；自定义调度器配置复杂；资源碎片导致大 Pod 无法调度 |

### 2.2 Service 负载均衡

| 维度 | 内容 |
|------|------|
| 是什么 | Service 为一组 Pod 提供固定 ClusterIP 和 DNS 名称的稳定网络入口 |
| 能做什么 | 解决 Pod 动态 IP 变化问题；提供集群内/外访问；通过 kube-proxy 实现负载均衡 |
| 怎么用 | `kubectl expose deployment app --port=80 --type=NodePort` |
| 原理和工作流程 | Service 通过标签选择器关联后端 Pod，分配固定 ClusterIP 和 DNS 名称。kube-proxy 监听 Service 和 Endpoint 变化，iptables 模式生成 NAT 规则将 ClusterIP 流量转发到后端 Pod，IPVS 模式使用内核 IPVS 模块支持多种调度算法性能更高。ClusterIP 仅集群内访问，NodePort 在每 Node 开放 30000-32767 端口，LoadBalancer 由云厂商提供公网 IP |
| 缺点 | iptables 模式规则多时性能下降；NodePort 端口范围有限且暴露在所有 Node；LoadBalancer 依赖云厂商产生费用 |

### 2.3 Deployment 滚动更新

| 维度 | 内容 |
|------|------|
| 是什么 | Deployment 通过 ReplicaSet 逐步替换 Pod 实现零停机更新的机制 |
| 能做什么 | 控制更新速度；保证可用性；支持自动回滚 |
| 怎么用 | `kubectl set image deployment/app app=app:v2` 触发滚动更新 |
| 原理和工作流程 | 更新时 Deployment 创建新 ReplicaSet，通过 maxSurge 控制允许超出的副本数、maxUnavailable 控制允许不可用的副本数。先创建新版本 Pod，就绪后删除旧版本 Pod，重复直到全部替换。更新失败可通过 `kubectl rollout undo` 回滚到上一版本 |
| 缺点 | 滚动更新期间新旧版本共存，需保证 API 兼容性；maxSurge 和 maxUnavailable 配置不当导致服务不可用；回滚依赖历史 ReplicaSet 保留数量 |

### 2.4 HPA 自动扩缩容

| 维度 | 内容 |
|------|------|
| 是什么 | HPA 根据 CPU/内存等指标自动调整 Deployment 副本数的机制 |
| 能做什么 | 根据负载自动扩容；低负载时缩容节省资源；设定最小最大副本数边界 |
| 怎么用 | `kubectl autoscale deployment app --min=2 --max=10 --cpu-percent=70` |
| 原理和工作流程 | HPA 控制器周期性从 Metrics Server 获取 Pod 资源指标，计算当前指标与目标利用率的比值，据此推算期望副本数=当前副本数×(当前指标/目标指标)，若超出 minReplicas 和 maxReplicas 边界则截断，然后更新 Deployment 的 replicas 字段触发扩缩容 |
| 缺点 | 依赖 Metrics Server 提供指标，未部署则 HPA 失效；扩缩容有冷却时间无法即时响应突发流量；仅基于 CPU/内存可能误判，复杂场景需自定义指标 |

---

## 三、实战应用

### 3.1 Spring Boot 微服务部署到 K8s

| 维度 | 内容 |
|------|------|
| 是什么 | 将 Spring Boot 微服务以 Deployment+Service+ConfigMap 方式部署到 K8s 的实践 |
| 能做什么 | 声明副本数和资源限制；配置健康探针；注入配置；提供稳定服务访问 |
| 怎么用 | `kubectl apply -f deployment.yaml service.yaml configmap.yaml` |
| 原理和工作流程 | Deployment 定义 3 个副本、容器镜像、resources 的 requests 和 limits（requests 影响调度，limits 限制运行时），livenessProbe 和 readinessProbe 通过 actuator 健康端点检查存活与就绪，ConfigMap 以 envFrom 注入配置，Service 通过标签选择器 app:order-service 关联 Pod 提供 ClusterIP 访问 |
| 缺点 | YAML 文件冗长易错；资源限制配置不当导致调度失败或 OOM；多服务部署需 Helm 等工具管理复杂度 |

### 3.2 Ingress 配置

| 维度 | 内容 |
|------|------|
| 是什么 | Ingress 管理集群外部 HTTP/HTTPS 访问，按域名和路径路由到 Service 的资源 |
| 能做什么 | 基于域名和路径路由；支持 TLS 终止；集中管理外部入口 |
| 怎么用 | `kubectl apply -f ingress.yaml` 创建 Ingress 规则 |
| 原理和工作流程 | Ingress Controller（如 Nginx Ingress）监听 Ingress 资源变化，将规则转换为 Nginx 配置，外部请求到达 Ingress Controller 后根据 host 和 path 匹配规则转发到对应 Service 的 Pod。TLS 通过 secretName 引用证书实现 HTTPS 终止 |
| 缺点 | 依赖 Ingress Controller 实现，不同 Controller 行为有差异；路径路由需注意 pathType 匹配语义；TLS 证书管理需额外工具如 cert-manager |

### 3.3 健康检查（livenessProbe vs readinessProbe）

| 维度 | 内容 |
|------|------|
| 是什么 | K8s 探针机制，分别检查容器存活、就绪、启动状态 |
| 能做什么 | livenessProbe 失败重启容器；readinessProbe 失败摘除流量；startupProbe 保护慢启动应用 |
| 怎么用 | `livenessProbe.httpGet.path: /actuator/health/liveness` / `readinessProbe.httpGet.path: /actuator/health/readiness` |
| 原理和工作流程 | kubelet 周期性执行探针，livenessProbe 检查容器是否存活，失败则按重启策略重启容器；readinessProbe 检查是否就绪，失败则从 Service 端点移除不接收流量；startupProbe 检查启动是否完成，完成前 liveness 和 readiness 不生效，防止慢启动应用被误杀 |
| 缺点 | livenessProbe 检查外部依赖会导致重启雪崩；未设 initialDelaySeconds 启动期被误杀；探针配置过于敏感引起频繁重启 |

---

## 四、常见面试题

### 1. Pod 和 Container 的关系？

| 维度 | 内容 |
|------|------|
| 是什么 | Pod 是 K8s 最小调度单位，可包含一个或多个 Container |
| 能做什么 | 同 Pod 容器共享网络和存储；通过 localhost 通信；作为整体被调度 |
| 怎么用 | `kubectl get pods` 查看 Pod；Pod YAML 定义 containers 数组 |
| 原理和工作流程 | Pod 内容器共享 Network Namespace（同一 IP 和端口空间）和 Volume，通过 localhost 互相通信。Pod 作为整体调度到同一 Node，共享生命周期。通常一个 Pod 运行一个主容器，必要时添加 Sidecar 容器如日志收集或代理 |
| 缺点 | 同 Pod 容器强耦合，一个崩溃影响整个 Pod；多容器 Pod 增加调试复杂度；Pod ephemeral，重启后 IP 变化需 Service 配合 |

### 2. Deployment 和 StatefulSet 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | Deployment 管理无状态应用，StatefulSet 管理有状态应用的控制器 |
| 能做什么 | Deployment 并行启停、随机 Pod 名、共享 PVC；StatefulSet 顺序启停、固定序号、独立 PVC、固定 DNS |
| 怎么用 | `kubectl create deployment` / `kubectl create statefulset` |
| 原理和工作流程 | Deployment 通过 ReplicaSet 管理 Pod，Pod 名为随机后缀，启动停止并行，存储共享。StatefulSet 为每个 Pod 分配固定序号（如 mysql-0、mysql-1），按序号顺序启动停止，每个 Pod 有独立 PVC 和固定 DNS（mysql-0.mysql-svc），适用于需要稳定标识和顺序的应用 |
| 缺点 | StatefulSet 扩缩容慢必须顺序；Deployment 不适合数据库等有状态应用；StatefulSet 删除 Pod 后 PVC 不自动回收导致存储泄漏 |

### 3. Service 的 ClusterIP、NodePort、LoadBalancer 三种类型区别？

| 维度 | 内容 |
|------|------|
| 是什么 | K8s Service 的三种暴露方式，分别面向集群内、Node 端口、云负载均衡器 |
| 能做什么 | ClusterIP 集群内访问；NodePort 通过 NodeIP:Port 外部访问；LoadBalancer 分配公网 IP |
| 怎么用 | `type: ClusterIP` / `type: NodePort` / `type: LoadBalancer` |
| 原理和工作流程 | ClusterIP 分配集群内部 IP 由 kube-proxy 转发；NodePort 在每个 Node 开放 30000-32767 端口，流量经 iptables/IPVS 转发到后端 Pod；LoadBalancer 在 NodePort 之上由云厂商创建外部负载均衡器分配公网 IP，流量先到 LB 再到 NodePort 再到 Pod |
| 缺点 | ClusterIP 无法外部访问；NodePort 端口范围有限且暴露所有 Node 有安全风险；LoadBalancer 依赖云厂商且每个 Service 一个 LB 费用高 |

### 4. 如何排查 Pod 一直处于 Pending 状态？

| 维度 | 内容 |
|------|------|
| 是什么 | Pod 被创建但无法调度到 Node 导致停留在 Pending 状态的排查方法 |
| 能做什么 | 查看 Events；识别资源不足、PVC 未绑定、NodeSelector 不匹配、Taints 不匹配、镜像拉取失败等原因 |
| 怎么用 | `kubectl describe pod <pod-name>` 查看 Events 信息 |
| 原理和工作流程 | Pending 表示 Pod 已被 API Server 接收但未被调度或无法调度。通过 `kubectl describe pod` 查看 Events，Scheduler 的调度失败事件会显示具体原因，如资源不足、NodeSelector 不匹配、Taints/Tolerations 不匹配、PVC 无法绑定、镜像拉取失败，根据原因针对性解决 |
| 缺点 | Events 有保留时限过期丢失；部分调度失败原因信息不明确需进一步排查；多原因叠加时难以定位主因 |

---

## 五、避坑指南

| 维度 | 内容 |
|------|------|
| 是什么 | K8s 使用中常见错误及其现象、原因、解决方案的汇总 |
| 能做什么 | 避免硬编码配置；防止 OOM；实现优雅关闭；避免 latest 标签；合理配置健康检查 |
| 怎么用 | ConfigMap/Secret 存配置；设置 requests 和 limits；处理 SIGTERM；使用版本号或 commit hash；liveness 不检查外部依赖 |
| 原理和工作流程 | 镜像中硬编码配置导致无法复用，应用 ConfigMap/Secret 解耦；未设 resources 导致 Pod 被 OOM Killer 杀掉或抢占资源，requests 影响调度 limits 限制运行时；Pod 删除时先 SIGTERM 超时后 SIGKILL，需应用正确处理信号完成请求后退出；latest 标签版本不确定导致回滚困难；livenessProbe 检查外部依赖会导致依赖故障引发重启雪崩，应设合理 initialDelaySeconds |
| 缺点 | 避坑指南无法穷尽所有问题；优雅关闭需应用层配合改造；resources 设置需反复调优 |

---

> [返回原文](./02-Kubernetes核心概念.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
