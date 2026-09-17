# JVM 原理与调优 导览

> 定位：五维框架浓缩提炼 14-JVM原理与调优.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./14-JVM原理与调优.md)。
> 前置知识：Java 基础语法、多线程与并发编程

---

## 一、核心概念

### 1.1 JVM 运行时数据区

| 维度 | 内容 |
|------|------|
| 是什么 | JVM 运行时划分的内存区域，分线程共享与线程私有两组 |
| 能做什么 | 堆存对象；方法区存类信息；栈存栈帧；计数器存指令地址；本地方法栈服务 native |
| 怎么用 | `jstat -gc <pid>` 查看各区使用 |
| 原理和工作流程 | 线程共享：堆存对象实例与数组是 GC 主区域，方法区（JDK8 前永久代 JDK8+ 元空间）存类信息常量静态变量。线程私有：虚拟机栈存方法调用栈帧含局部变量与操作数栈，本地方法栈服务 native 方法，程序计数器存当前线程执行字节码地址。栈与计数器随线程生灭无需 GC |
| 缺点 | 堆溢出 OOM、栈溢出 StackOverflow、元空间溢出各有不同排查；永久代与元空间变迁增加认知成本 |

### 1.2 堆内存划分

| 维度 | 内容 |
|------|------|
| 是什么 | 堆按对象生命周期划分为新生代与老年代的分代结构 |
| 能做什么 | 新生代分 Eden 与两个 Survivor；老年代存长期对象；按代选 GC 算法 |
| 怎么用 | 新生代占堆 1/3，Eden:S0:S1 为 8:1:1 |
| 原理和工作流程 | 堆分新生代与老年代，新生代分 Eden 与 Survivor0、Survivor1，比例 8:1:1。新对象先分配 Eden，Minor GC 后存活对象进 Survivor，经多次 GC 仍存活进老年代。大对象直接进老年代避免复制。分代依据对象朝生夕死特性，新生代用复制算法老年代用标记整理，提升 GC 效率 |
| 缺点 | 分代比例需调优；Survivor 太小致过早晋升；大对象致老年代碎片；调参复杂 |

---

## 二、底层原理

### 2.1 GC 算法

| 维度 | 内容 |
|------|------|
| 是什么 | 垃圾回收的四种基础算法 |
| 能做什么 | 标记-复制适合新生代；标记-清除快但有碎片；标记-整理无碎片但慢；分代综合最优 |
| 怎么用 | 新生代用复制，老年代用标记-整理或清除 |
| 原理和工作流程 | 标记-复制将存活对象复制到另一块区域清理原区域无碎片速度快但浪费一半内存适合新生代。标记-清除标记存活清除未标记不浪费空间但产生碎片是 CMS 基础。标记-整理标记存活向一端移动清理边界外无碎片但移动开销大 STW 长适合老年代。分代收集不同代用不同算法综合最优 |
| 缺点 | 复制浪费空间；清除有碎片；整理 STW 长；分代实现复杂 |

### 2.2 垃圾收集器对比

| 维度 | 内容 |
|------|------|
| 是什么 | JVM 提供的多种垃圾收集器及其特性对比 |
| 能做什么 | Serial 单线程；Parallel 吞吐量优先；CMS 低延迟；G1 平衡；ZGC 超低延迟 |
| 怎么用 | JDK9+ 默认 G1，低延迟用 ZGC |
| 原理和工作流程 | Serial 单线程客户端模式。Parallel Scavenge 与 Parallel Old 多线程吞吐量优先。CMS 老年代低延迟四阶段：初始标记 STW、并发标记、重新标记 STW、并发清除，缺点有碎片与浮动垃圾。G1 全堆划分约 2048 个 Region 1 到 32MB，SATB 并发标记，RSet 记录跨 Region 引用，Mixed GC 回收新生代加部分老年代，MaxGCPauseMillis 设停顿目标，JDK9+ 默认。ZGC 染色指针 STW 小于 10ms |
| 缺点 | CMS 有碎片与浮动垃圾；G1 实现复杂；ZGC 内存开销大；选型需权衡 |

### 2.3 类加载机制

| 维度 | 内容 |
|------|------|
| 是什么 | JVM 加载类的双亲委派模型与三种类加载器 |
| 能做什么 | Bootstrap 加载核心类；Extension 加载扩展类；Application 加载应用类；双亲委派保安全 |
| 怎么用 | `ClassLoader.getSystemClassLoader()` 获取应用类加载器 |
| 原理和工作流程 | 三加载器：Bootstrap C++ 加载 lib 下 rt.jar 等核心类，Extension Java 加载 ext 目录，Application Java 加载 classpath。双亲委派：收到加载请求先委派父加载器，父失败才自行加载，保证核心类不被覆盖与类唯一性。打破场景：Tomcat WebappClassLoader 应用隔离、JDBC SPI 用线程上下文类加载器、OSGi 模块化、热部署 |
| 缺点 | 严格层级限制灵活；SPI 需打破委派；Tomcat 需自定义层级；理解成本高 |

### 2.4 JIT 编译

| 维度 | 内容 |
|------|------|
| 是什么 | 即时编译器将热点代码编译为本地机器码提升执行效率 |
| 能做什么 | C1 快速低优化；C2 慢高优化；分层编译协作；热点探测触发 |
| 怎么用 | JDK7+ 默认分层编译 |
| 原理和工作流程 | JIT 将热点代码编译为本地机器码避免解释执行开销。C1 Client 编译快优化低，C2 Server 编译慢优化高。JDK7+ 默认分层编译五级：Level 0 解释执行，Level 1 到 3 C1 编译 profiling 程度递增，Level 4 C2 深度优化。热点探测基于方法调用计数与回边计数，超阈值触发编译。逃逸分析、锁消除、内联等优化由 C2 完成 |
| 缺点 | 编译有 CPU 开销；预热阶段慢；编译优化可能退化；调试难定位编译版 |

---

## 三、实战应用

### 3.1 JVM 常用参数

| 维度 | 内容 |
|------|------|
| 是什么 | JVM 启动时配置堆、元空间、GC、调优的常用参数 |
| 能做什么 | Xms 与 Xmx 设堆大小；Xmn 设新生代；MetaspaceSize 设元空间；UseG1GC 启 G1 |
| 怎么用 | `-Xms4g -Xmx4g -XX:+UseG1GC -XX:MaxGCPauseMillis=200` |
| 原理和工作流程 | 堆参数：Xms 初始堆与 Xmx 最大堆生产建议相等避免动态扩缩，Xmn 新生代大小或用 XX:NewRatio。元空间：MetaspaceSize 与 MaxMetaspaceSize。GC：UseG1GC、UseZGC 选收集器，MaxGCPauseMillis 设停顿目标。诊断：HeapDumpOnOutOfMemoryError 致 OOM 自动 dump。生产 Xms 与 Xmx 相等避免抖动 |
| 缺点 | 参数繁多；配置不当致 OOM 或频繁 GC；版本差异；需压测验证 |

### 3.2 OOM 排查流程

| 维度 | 内容 |
|------|------|
| 是什么 | 系统发生 OutOfMemoryError 时的排查步骤 |
| 能做什么 | dump 堆快照；MAT 分析大对象；定位泄漏点；调整参数 |
| 怎么用 | `jmap -dump:format=b,file=heap.hprof <pid>` |
| 原理和工作流程 | 一确认 OOM 类型堆溢出、元空间溢出、GC overhead。二用 jmap 或 HeapDumpOnOutOfMemoryError 生成堆 dump。三用 MAT 或 JProfiler 分析支配树找大对象与泄漏链。四定位代码如静态集合不断增长、ThreadLocal 未 remove、连接未关闭。五调整参数或修复代码。常见原因大集合、内存泄漏、大对象、元空间类加载过多 |
| 缺点 | dump 大致分析慢；线上 dump 致停顿；需提前配置自动 dump；定位需经验 |

### 3.3 CPU 100% 排查流程

| 维度 | 内容 |
|------|------|
| 是什么 | 系统 CPU 占用 100% 时的排查步骤 |
| 能做什么 | top 找进程；top -Hp 找线程；jstack 找栈；定位热点代码 |
| 怎么用 | `top -Hp <pid>` 后 `printf "%x\n" <tid>` 转 16 进制 |
| 原理和工作流程 | 一 top 找 CPU 高的 Java 进程。二 top -Hp 找该进程内 CPU 高的线程 tid。三 printf 将 tid 转 16 进制。四 jstack 打印线程栈 grep 16 进制 tid 找到对应线程栈。五分析栈定位正在执行的方法，常见死循环、正则回溯、频繁 GC、锁竞争。也可用 arthas profile 定位热点方法 |
| 缺点 | 需多次采样；瞬时高 CPU 难抓；jstack 时间点需对齐；多线程复杂 |

### 3.4 GC 日志解读与线上 GC/OOM 排查

| 维度 | 内容 |
|------|------|
| 是什么 | 通过 GC 日志与配套工具定位线上 GC 频繁、停顿变长与各类 OOM 的排查方法 |
| 能做什么 | 开启并滚动 GC 日志；逐字段解读 G1 日志；区分 ZGC 与 CMS 日志差异；判定 Young GC 与 Full GC 频繁；分类排查六种 OOM；组合使用 jstat jmap jstack jinfo MAT |
| 怎么用 | `-Xlog:gc*:file=/logs/gc.log:time,uptime,level,tags:filecount=10,filesize=50m`；`jstat -gcutil <pid> 1000 30`；`jmap -dump:live,format=b,file=heap.hprof <pid>` |
| 原理和工作流程 | 日志参数上 Xlog 的标签选问题域如 gc gc+heap gc+age gc+phases，装饰器 time 与 uptime 对齐时间轴，level 与 tags 便于过滤，filecount 与 filesize 做滚动。G1 日志按字段判读：Eden 回收后清零为正常，Old regions 增加说明有晋升，Humongous 长期不降说明大对象频繁，Metaspace 持续上涨是类加载器泄漏，堆前后值评估回收效率，停顿时长与 MaxGCPauseMillis 对比，Real 远大于 User 加 Sys 说明并行度不足。判定标准为 Young GC 超每分钟 10 次或单次停顿超 50ms、Full GC 超每小时 1 次或单次超 1s、Full GC 后老年代仍超 70% 不回落、GCT 占比超 5%。Full GC 频繁按五步处置：jstat 观察趋势、判定泄漏还是容量不足、jmap dump 加 MAT 分析、检查静态集合与缓存无淘汰与元空间泄漏与 System.gc 等根因、修代码或调参后压测回归。OOM 分六类各有路径：堆溢出查大对象与引用链，元空间溢出查类加载器泄漏与动态代理，直接内存溢出查 DirectByteBuffer 与 Netty ByteBuf 是否 release，GC overhead limit exceeded 本质仍是堆不足，native thread 查线程池上限与 ulimit，StackOverflowError 查递归深度。三个反直觉点：Full GC 后占用不回落不一定是泄漏要看趋势，Real 远大于 User 加 Sys 是并行度不足，to-space exhausted 与 Evacuation Failure 应查晋升速率而非只调大 Survivor |
| 缺点 | 日志量大需配套采集与滚动策略；dump 大文件分析慢且线上 dump 有停顿；需提前配置自动 dump 否则错过现场；容器环境下 CPU 与内存视图易失真；定位高度依赖经验 |

### 3.5 Arthas 实战诊断

| 维度 | 内容 |
|------|------|
| 是什么 | 阿里开源的 Java 诊断工具，不重启不改代码即可对线上 JVM 做方法级现场取证 |
| 能做什么 | 安装与 attach；dashboard 看实时总览；thread 定位 CPU 热点与阻塞源头；jad 反编译已加载类；watch 看入参返回值异常；trace 看子调用耗时；monitor 做聚合统计；sc 查类加载器与来源；ognl 读写字段；heapdump 导堆；profiler 出火焰图 |
| 怎么用 | `java -jar arthas-boot.jar <pid>` 或 `kubectl exec -it <pod> -- java -jar arthas-boot.jar 1`；`watch com.example.OrderService create '{params, returnObj}' -x 3` |
| 原理和工作流程 | attach 通过 JVM 的 Attach API 挂载 agent 实现，失败常见于 JDK 版本不匹配、用户不一致、容器缺 /tmp 写权限或 PID 命名空间隔离。dashboard 输出分线程区与内存区，堆 usage 持续超 85% 且老年代接近占满说明内存压力大，某线程 %CPU 长期超 70% 且状态 RUNNABLE 说明存在热点。四个观察命令分工明确：watch 看单次调用的入参与返回值适合查传参与异常，trace 看方法内子调用耗时分布适合查慢在哪一行，monitor 做聚合统计适合查哪个方法整体慢，stack 看调用来源适合查谁在调。CPU 飙高案例走 dashboard 找热点线程到 thread 看栈到 profiler 出火焰图到 jad 反编译确认逻辑到 trace 验证耗时到修复后 monitor 对比 RT 六步。接口变慢案例走 monitor 定方法到 trace 定子调用到 watch 看入参返回到 thread -b 查锁竞争到定位持锁期间做网络调用到拆锁降粒度五步。注意 trace 开销较大需限次数、诊断完及时 stop、谨慎使用 redefine、与 APM 互补 |
| 缺点 | trace 与 watch 在高 QPS 接口上会加剧延迟；会输出业务数据需符合数据安全规范；redefine 热替换风险高；增强字节码未 stop 会长期驻留；容器内 attach 受权限与命名空间限制 |

---

## 四、常见面试题（附答案）

### 1. 什么是双亲委派模型？为什么需要它？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查双亲委派模型定义与作用 |
| 能做什么 | 解释委派流程；说明三加载器；说明安全与唯一作用 |
| 怎么用 | 收到请求先委派父加载器 |
| 原理和工作流程 | 双亲委派模型指类加载器收到加载请求后先委派父加载器加载，父加载失败才自行加载。层级为 Bootstrap 加载核心类、Extension 加载扩展类、Application 加载应用类。需要它因一保证核心类库安全防止自定义类覆盖如 java.lang.String，二保证类唯一性同一类不被重复加载。打破场景 Tomcat 应用隔离、JDBC SPI、OSGi |
| 缺点 | 严格层级限制灵活；SPI 需打破；理解成本高 |

### 2. CMS 和 G1 的区别？什么场景选 G1？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 CMS 与 G1 收集器的差异与选型 |
| 能做什么 | 对比堆大小；对比碎片；对比停顿；说明 G1 适用场景 |
| 怎么用 | 中小堆用 CMS，大堆用 G1 |
| 原理和工作流程 | CMS 老年代收集器用标记-清除有内存碎片，停顿不可预测，适合中小堆小于 4G 的低延迟场景 JDK8。G1 全堆收集器划分 Region 用标记-整理加复制无碎片可控，停顿可预测通过 MaxGCPauseMillis 设目标，JDK9+ 默认适合大堆大于 4G。G1 用 Mixed GC 回收新生代加部分老年代按回收价值排序。大堆、低延迟、JDK9+ 选 G1 |
| 缺点 | CMS 有碎片与浮动垃圾已废弃；G1 实现复杂内存开销大；各有适用场景 |

### 3. 什么对象会进入老年代？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查对象晋升老年代的几种条件 |
| 能做什么 | 年龄达阈值；大对象直接进；动态年龄判断；Survivor 空间不足 |
| 怎么用 | MaxTenuringThreshold 默认 15 |
| 原理和工作流程 | 对象进老年代四种情况：一对象年龄达 MaxTenuringThreshold 默认 15 晋升。二大对象超过 PretenureSizeThreshold 直接进老年代避免复制。三动态年龄判断 Survivor 中相同年龄对象大小超 Survivor 一半则该年龄及以上晋升。四 Minor GC 后 Survivor 空间不足存活对象通过担保机制进老年代 |
| 缺点 | 晋升过快致老年代膨胀频繁 Full GC；大对象致碎片；担保失败；参数需调优 |

### 4. 如何排查 Full GC 频繁？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Full GC 频繁的排查方法 |
| 能做什么 | jstat 看 GC 频率；分析老年代占满原因；定位内存泄漏或大对象；调参 |
| 怎么用 | `jstat -gcutil <pid> 1000` 观察各区变化 |
| 原理和工作流程 | 一用 jstat -gcutil 观察 GC 频率与各区占用确认 Full GC 频繁。二分析老年代是否持续涨致占满，若涨不回收疑内存泄漏。三jmap dump 堆用 MAT 找大对象与泄漏链。四常见原因：内存泄漏静态集合增长、大对象进老年代、元空间类加载过多、System.gc 调用、显式 GC。五修复代码或调大堆与新生代比例 |
| 缺点 | 排查需多工具配合；dump 致停顿；定位需经验；线上难复现 |

---

## 五、避坑指南

> 本节为辅助内容，无五维表格。汇总 Xms 与 Xmx 不等致抖动、新生代过小致频繁 GC、元空间溢出、CMS 碎片与 Concurrent Mode Failure、System.gc 触发 Full GC、大对象进老年代、ThreadLocal 泄漏致 OOM、生产用 Serial 收集器、堆 dump 致停顿、参数版本差异等错误的现象、原因与解决方案。

---

> [返回原文](./14-JVM原理与调优.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
