# Kubernetes 核心概念

> 学习路线对应：第6周 -- 容器化与 K8s
> 前置知识：Docker 基础
> 对比 Node.js：K8s 管理容器 约等于 PM2 管理 Node 进程，但更强大

> 📖 **参考链接**：
> - [Kubernetes 官方文档（中文）](https://kubernetes.io/zh-cn/docs/) -- Kubernetes 官方中文文档总站，涵盖概念、任务、教程、参考手册
> - [Kubernetes 概念](https://kubernetes.io/zh-cn/docs/concepts/) -- 官方概念详解：Pod、Deployment、Service、ConfigMap、Volume 等核心对象
> - [Kubernetes 调度器](https://kubernetes.io/zh-cn/docs/concepts/scheduling-eviction/) -- 调度与驱逐：kube-scheduler 预选优选、节点亲和性、污点容忍
> - [Kubernetes 服务网络](https://kubernetes.io/zh-cn/docs/concepts/services-networking/) -- Service、Ingress、网络策略、DNS
> - [Kubernetes 存储卷](https://kubernetes.io/zh-cn/docs/concepts/storage/) -- Volume、PersistentVolume、StorageClass、CSI

---

## 一、核心概念

### 1.1 K8s 架构

Kubernetes 集群由 Master 节点（控制平面）和 Node 节点（工作节点）组成：

**Master 节点组件：**

| 组件 | 职责 |
|------|------|
| **API Server** | 集群统一入口，处理所有 REST 请求，将资源状态存入 etcd |
| **Scheduler** | 调度器，为新创建的 Pod 选择最合适的 Node 运行 |
| **Controller Manager** | 控制器管理器，维护集群期望状态（Deployment、ReplicaSet 等） |
| **etcd** | 分布式键值存储，保存集群所有配置和状态数据 |

**Node 节点组件：**

| 组件 | 职责 |
|------|------|
| **kubelet** | Node 上的代理，管理 Pod 生命周期，上报 Node 状态 |
| **kube-proxy** | 网络代理，实现 Service 的负载均衡（iptables/IPVS） |
| **Container Runtime** | 容器运行时（containerd、CRI-O 等），运行容器 |

> **生活化类比：** Kubernetes 编排就像施工现场的项目经理。工地上有几十个工人（容器），项目经理（K8s）不需要亲自搬砖，但需要统筹全局：哪个工人闲着就给他派活（Scheduler 调度 Pod），工人受伤了马上换人顶上（Deployment 自愈），物料不够了就叫供应商补货（HPA 自动扩缩容），工地入口统一设一个前台接待处（Service 提供统一入口），外部来访客要登记才能进（Ingress 管理外部访问）。每个 Node 上还有 kubelet 作为"现场监工"，负责接收项目经理的指令并在本地执行。工人不需要知道项目经理在哪儿，只要按分配的任务干活就行。项目经理的核心工作就是"看着图纸（声明式 YAML），确保工地实际状态和图纸一致"。

### 1.2 核心资源对象

| 资源 | 说明 | 类比 |
|------|------|------|
| **Pod** | K8s 最小调度单位，包含一个或多个容器 | 豌豆荚（Pod = 豆荚，容器 = 豆子） |
| **Deployment** | 管理 Pod 副本数量、滚动更新、回滚 | 部署管理器 |
| **Service** | 为一组 Pod 提供稳定的网络访问入口 | 负载均衡器 |
| **Ingress** | 管理外部 HTTP/HTTPS 访问 | 反向代理 / Nginx |
| **ConfigMap** | 存储非敏感配置 | 配置文件 |
| **Secret** | 存储敏感信息（密码、Token、证书） | base64 编码的配置（需配合 RBAC 和 etcd 加密才能真正安全） |
| **StatefulSet** | 管理有状态应用（数据库等） | 类似 Deployment 但有状态：每个 Pod 有固定身份标识、有序部署（0→1→2）、独立持久存储 |
| **DaemonSet** | 确保每个 Node 运行一个 Pod 副本 | 守护进程 |

> **生活化类比：Pod = "豌豆荚（最小调度单元）"** —— K8s 不直接调度容器，而是调度 Pod，这就像农业上不按"粒"卖豆子而是按"荚"卖。一个豌豆荚（Pod）里可以有一颗豆子（单容器，最常见）或几颗豆子（多容器，如主应用 + sidecar 日志代理）。同一荚里的豆子共享同一份"营养供给"——Pod 内所有容器共享网络命名空间（相同 IP、端口空间，互相 localhost 通信）和存储卷，就像荚内豆子共生根茎。但不同荚之间相互隔离，各自有独立 IP。为什么 K8s 不直接管容器而要套一层 Pod？因为有些应用天生需要"紧耦合"——比如业务容器和日志收集容器必须同生共死、共享存储，把它们放在一个 Pod 里调度最自然。Pod 是 K8s 调度的最小粒度：要么整个荚一起调度到某台 Node，要么一起走，不会出现"豆子分家"的情况。记住：**Pod 是临时的、可丢弃的**（豆荚摘了还能再长），Pod 的 IP 会随重建而变化，所以才需要 Service 给它一个"固定门牌号"。

### 1.3 声明式 API

K8s 采用声明式 API：用户描述期望状态（如"运行 3 个副本"），K8s 自动调谐（Reconciliation Loop），确保实际状态与期望状态一致。

```
用户提交 YAML（期望状态: 3 个副本）
  -> Controller Manager 读取期望状态
  -> 对比实际状态（当前只有 2 个副本）
  -> 调谐：创建 1 个新 Pod
  -> 实际状态 = 期望状态
```

---

## 二、底层原理

### 2.1 Pod 调度流程

```
1. 用户创建 Pod（或 Deployment 创建 Pod）
2. Scheduler 监听未调度的 Pod
3. 预选（Filtering）：过滤掉不满足条件的 Node
   - 资源不足（CPU/内存不够）
   - NodeSelector/NodeAffinity 不匹配
   - Taints/Tolerations 不匹配
4. 优选（Scoring）：对剩余 Node 打分
   - 资源均衡度（LeastRequestedPriority）
   - 镜像本地性（ImageLocalityPriority）
   - Pod 亲和性/反亲和性
5. 选择得分最高的 Node，绑定 Pod
6. kubelet 创建并启动容器
```

**Pod 调度全流程（预选 -> 优选 -> 绑定）Mermaid 图：**

```mermaid
%%{init: {'themeVariables': {'fontSize': '16px'}}}%%
graph TD
    A["用户创建 Pod<br/>（或 Deployment 创建 Pod）"] --> B["Scheduler 监听<br/>未调度的 Pod"]
    B --> C["预选阶段（Filtering）<br/>过滤不满足条件的 Node"]
    C --> C1{"资源是否充足?<br/>（CPU / 内存）"}
    C1 -->|"否"| C1a["过滤：资源不足"]
    C1 -->|"是"| C2{"NodeSelector<br/>/ Affinity<br/>是否匹配?"}
    C2 -->|"否"| C2a["过滤：标签不匹配"]
    C2 -->|"是"| C3{"Taints<br/>/ Tolerations<br/>是否匹配?"}
    C3 -->|"否"| C3a["过滤：污点不匹配"]
    C3 -->|"是"| D["优选阶段（Scoring）<br/>对剩余 Node 打分"]
    D --> D1["资源均衡度打分<br/>LeastRequestedPriority"]
    D --> D2["镜像本地性打分<br/>ImageLocalityPriority"]
    D --> D3["Pod 亲和性 / 反亲和性<br/>打分"]
    D1 --> E["综合所有评分<br/>排序"]
    D2 --> E
    D3 --> E
    E --> F["选择得分最高的 Node"]
    F --> G["绑定 Pod 到该 Node"]
    G --> H["kubelet 创建并启动容器"]
    H --> I["Pod 进入 Running 状态"]
```

**Pod 生命周期状态流转（Mermaid 图）：**

```mermaid
%%{init: {'themeVariables': {'fontSize': '15px'}}}%%
graph LR
    P["⏳ Pending<br/>已创建未调度<br/>或正在拉取镜像"] -->|"调度成功 + 镜像就绪"| R["🟢 Running<br/>容器正常运行"]
    R -->|"容器正常退出"| S["✅ Succeeded<br/>任务完成（Job 类型）"]
    R -->|"容器异常退出"| F["❌ Failed<br/>容器崩溃/被 OOM Kill"]
    P -->|"镜像拉取失败<br/>或资源不足"| F
    R -->|"容器崩溃重启"| CR["🔁 CrashLoopBackOff<br/>反复崩溃，指数退避重启"]
    CR -->|"重启成功"| R
    CR -->|"超过 backOff 上限"| F
    F -.->|"Deployment 自愈<br/>重新创建新 Pod"| P
```

> 上图展示 Pod 的生命周期状态流转：**Pending**（已提交但未就绪，可能在等调度或拉镜像）→ **Running**（容器启动并运行）→ **Succeeded**（正常完成，如 Job/CronJob）或 **Failed**（异常退出，如崩溃、OOM）。若容器反复崩溃，进入 **CrashLoopBackOff** 状态，kubelet 按指数退避（10s→20s→40s…最大 5 分钟）重试启动。Deployment 控制器监测到 Pod Failed 后会自动创建新 Pod 替代（自愈）。排查 CrashLoopBackOff 的常用命令：`kubectl describe pod <pod>` 看 Events、`kubectl logs <pod> --previous` 看上次崩溃时的日志。

### 2.2 Service 负载均衡

Service 为一组 Pod 提供稳定的网络访问入口（固定 ClusterIP 和 DNS 名称），解决 Pod 动态创建/销毁导致 IP 变化的问题。

> **生活化类比：Service = "公司的固定门牌号"** —— Pod 像公司里搬来搬去的工位（每次重建 IP 都变），员工（客户端）想找"技术部"办事，总不能每次都去查工位号（Pod IP）——太麻烦了。于是公司在大厅设了一个固定门牌号"技术部前台"（Service 的 ClusterIP + DNS 名 `tech-svc.default.svc.cluster.local`），这个门牌号永远不变。不管技术部搬到几楼、换了几拨人（Pod 扩缩容、滚动更新重建），前台（Service）始终在原地，通过背后的一张"员工座位表"（Endpoints，记录当前 Pod IP 列表）把来访者路由到具体工位。kube-proxy 就是"前台路由员"，它在每个 Node 上维护 iptables/IPVS 规则，把发往 Service IP 的流量按轮询/会话保持转发到后端 Pod。Pod 一旦重建 IP 变了，Endpoints 控制器自动更新座位表，前台无感知——这就是 Service 解耦"访问入口"与"后端实例"的精髓。NodePort 是"在公司大门外也挂个同样的牌子"，LoadBalancer 是"直接向电信局申请个公网号码"。

**三种 Service 类型：**

| 类型 | 访问范围 | 说明 |
|------|----------|------|
| **ClusterIP**（默认） | 集群内部 | 分配集群内部 IP，只能在集群内访问 |
| **NodePort** | 集群外部 | 在每个 Node 上开放端口（30000-32767），通过 NodeIP:Port 访问 |
| **LoadBalancer** | 集群外部 | 云厂商提供的负载均衡器，分配公网 IP |

**kube-proxy 工作模式：**

| 模式 | 原理 | 性能 |
|------|------|------|
| **iptables** | 通过 iptables 规则实现流量转发 | 规则数量多时性能下降 |
| **IPVS** | 使用 Linux 内核 IPVS 模块，支持多种调度算法 | 高性能，推荐 |

### 2.3 Deployment 滚动更新

Deployment 通过 ReplicaSet 控制 Pod 副本数量，支持滚动更新和回滚。

> **生活化类比：Deployment = "牧场管理员"** —— 你是牧场主，在羊圈里养着一群羊（Pod 副本）。你告诉牧场管理员（Deployment）"我要 5 只澳洲白绵羊"（期望状态 replicas=5），管理员就照办：数一数圈里，只有 3 只就再买 2 只补齐，有 7 只就卖掉 2 只。某天一只羊病死了（Pod 崩溃），管理员发现圈里只剩 4 只，立刻补买 1 只——这就是**自愈**。后来你想把品种从"澳洲白"换成"杜泊"（镜像版本升级），管理员不会一次性把 5 只全杀了再买新的（那样牧场就空了），而是**滚动更新**：先买 1 只杜泊羊放进去（+1），等它适应环境后再卖掉 1 只澳洲白（-1），逐步替换直到 5 只全是杜泊——业务零中断。如果新买的杜泊羊水土不服集体生病，管理员还能**回滚**——把之前的澳洲白羊买回来。maxSurge 是"换种期间圈里最多多养几只"（临时超额），maxUnavailable 是"换种期间最多少养几只"（临时缺额）。管理员手里还留着历次品种变更记录（revision history），随时能回退到任意历史版本。

**滚动更新参数：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| **maxSurge** | 滚动更新期间允许超出期望副本数的最大数量 | 25% |
| **maxUnavailable** | 滚动更新期间允许不可用的最大 Pod 数量 | 25% |

```
滚动更新示例（期望 4 个副本，maxSurge=25%, maxUnavailable=25%）：
  Step 1: 创建 1 个新版本 Pod（总数 5，maxSurge 允许 1 个超出）
  Step 2: 新 Pod 就绪后，删除 1 个旧版本 Pod（总数 4）
  Step 3: 重复直到所有 Pod 都是新版本
```

### 2.4 HPA 自动扩缩容

HPA（Horizontal Pod Autoscaler）根据 CPU/内存等指标自动调整 Pod 副本数：

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 三、实战应用

### 3.1 Spring Boot 微服务部署到 K8s

**Deployment YAML：**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
        - name: order-service
          image: registry.example.com/order-service:1.0.0
          ports:
            - containerPort: 8080
          envFrom:
            - configMapRef:
                name: order-service-config
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
```

**Service YAML：**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  type: ClusterIP
  selector:
    app: order-service
  ports:
    - port: 8080
      targetPort: 8080
```

**ConfigMap YAML：**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-service-config
data:
  application.yml: |
    server:
      port: 8080
    spring:
      datasource:
        url: jdbc:mysql://mysql-service:3306/order_db
```

### 3.2 Ingress 配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  tls:
    - hosts:
        - api.example.com
      secretName: tls-secret
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /order
            pathType: Prefix
            backend:
              service:
                name: order-service
                port:
                  number: 8080
          - path: /user
            pathType: Prefix
            backend:
              service:
                name: user-service
                port:
                  number: 8080
```

### 3.3 健康检查（livenessProbe vs readinessProbe）

| 探针类型 | 作用 | 失败后果 |
|----------|------|----------|
| **livenessProbe** | 检查容器是否存活 | 重启容器 |
| **readinessProbe** | 检查容器是否就绪 | 从 Service 端点移除，不接收流量 |
| **startupProbe** | 检查容器是否启动完成 | 启动完成前，livenessProbe 和 readinessProbe 不生效 |

**配置建议：**
- livenessProbe 检查简单的存活状态（如 HTTP 200）
- readinessProbe 检查依赖服务是否可用（如数据库连接）
- 给 livenessProbe 设置较长的 initialDelaySeconds，避免启动过程中被误杀

---

## 四、常见面试题

### 1. Pod 和 Container 的关系？

**答案：** Pod 是 K8s 最小调度单位，可以包含一个或多个容器。同一 Pod 内的容器共享网络命名空间（同一 IP 和端口空间）和存储卷，可以通过 localhost 通信。Pod 内的容器作为一个整体被调度到同一 Node 上。

### 2. Deployment 和 StatefulSet 的区别？

| 维度 | Deployment | StatefulSet |
|------|-----------|-------------|
| Pod 标识 | 随机名称（如 order-7d5f8b9c-abc） | 固定序号（如 mysql-0, mysql-1） |
| 网络标识 | 无固定 DNS | 固定 DNS（如 mysql-0.mysql-svc） |
| 启动/停止顺序 | 并行 | 顺序（0->1->2） |
| 持久化存储 | 共享 PVC | 每个 Pod 独立 PVC |
| 适用场景 | 无状态应用 | 有状态应用（数据库、消息队列） |

### 3. Service 的 ClusterIP、NodePort、LoadBalancer 三种类型区别？

**答案：** ClusterIP：默认类型，分配集群内部 IP，只能集群内访问。NodePort：在每个 Node 上开放端口（30000-32767），通过 NodeIP:Port 可从外部访问。LoadBalancer：云厂商提供的外部负载均衡器，分配公网 IP，自动转发流量到 NodePort。

### 4. 如何排查 Pod 一直处于 Pending 状态？

**答案：** 排查步骤：1）`kubectl describe pod <pod-name>` 查看 Events 信息；2）常见原因：资源不足（CPU/内存不够）、PVC 无法绑定、NodeSelector 不匹配、Taints/Tolerations 不匹配、镜像拉取失败；3）根据 Events 信息针对性解决。

---

## 五、避坑指南

| 常见错误 | 现象 | 原因 | 解决方案 |
|---------|------|------|---------|
| Pod 中硬编码配置 | 镜像和环境绑定，无法复用 | 配置写在镜像中 | 使用 ConfigMap 存储非敏感配置，Secret 存储敏感信息 |
| 未设置 resources 资源限制 | Pod 被 OOM Killer 杀死，或抢占其他 Pod 资源 | 未设置 requests 和 limits | 设置 resources.requests（调度决策）和 resources.limits（运行时限制） |
| Pod 未优雅关闭 | 请求被中断，数据不一致 | Pod 删除时先 SIGTERM，超时后 SIGKILL 强制终止 | 应用正确处理 SIGTERM 信号，完成正在处理的请求后再退出 |
| 使用 latest 标签 | 镜像版本不确定，回滚困难 | latest 标签版本不确定 | 使用明确的版本号或 Git commit hash |
| 健康检查配置不当 | Pod 频繁重启或被错误摘除 | livenessProbe 检查外部依赖导致重启雪崩；未设置 initialDelaySeconds | livenessProbe 不检查外部依赖；readinessProbe 可检查依赖；设置合理的 initialDelaySeconds |

---

> **学习导航**：
> - 返回 [学习路线总览](../../README.md)
> - 本模块其他文件：[03-容器与K8s笔面试题集](./03-容器与K8s笔面试题集.md)
> - 实战应用：[电商订单实时统计分析平台](../../extensions/project/01-电商订单实时统计分析平台.md)

