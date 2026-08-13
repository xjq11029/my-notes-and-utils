# Java 核心笔面试题集 导览

> 定位：五维框架浓缩提炼 17-Java核心笔面试题集.md 全部题目，每道题目提取所考知识点生成纵向表格。
> 用法：题目按选择题、简答题、编程题三类组织，需要查看原题与解析时跳转 [原文](./17-Java核心笔面试题集.md)。
> 前置知识：无

---

## 一、选择题（30 题）

### 选择题 1：HashMap 线程安全与默认容量

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HashMap 线程安全性、null 支持与默认容量的辨析 |
| 能做什么 | 辨析线程不安全；辨析允许一个 null 键多个 null 值；辨析默认容量 16 |
| 怎么用 | 答案选 B 允许 null 键和 null 值 |
| 原理和工作流程 | HashMap 非线程安全多线程致数据丢失，允许一个 null 键和多个 null 值，默认容量 16。key 须正确重写 hashCode 与 equals 否则查找失败。线程安全用 ConcurrentHashMap |
| 缺点 | 线程不安全易误选；null 支持易与 Hashtable 混；默认容量易误选 8 |

### 选择题 2：HashMap 树化阈值

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HashMap 链表转红黑树的阈值条件 |
| 能做什么 | 辨析树化阈值 8；辨析退化阈值 6；辨析最小树化容量 64 |
| 怎么用 | 答案选 C 链表长度 8 |
| 原理和工作流程 | TREEIFY_THRESHOLD 为 8 链表长度达 8 且数组长度达 MIN_TREEIFY_CAPACITY 64 才树化，否则优先扩容。退化阈值 UNTREEIFY_THRESHOLD 为 6 节点数降到 6 退化为链表，留缓冲避免 8 附近反复转换 |
| 缺点 | 阈值 8 与 6 易混；忽略数组长度 64 条件；退化阈值易忽略 |

### 选择题 3：ConcurrentHashMap JDK8 机制

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ConcurrentHashMap JDK8 的并发控制机制 |
| 能做什么 | 辨析 CAS 加 synchronized；辨析 JDK7 Segment；区分两版实现 |
| 怎么用 | 答案选 B CAS + synchronized |
| 原理和工作流程 | JDK7 用 Segment 分段锁继承 ReentrantLock 默认并发度 16。JDK8 废弃 Segment 改 CAS 加 synchronized 对桶头节点加锁粒度更细并发度等于桶数，空桶 CAS 插入非空桶 synchronized |
| 缺点 | 两版机制易混；CAS 与 synchronized 组合易忽略；分段锁已废弃 |

### 选择题 4：ArrayList 底层数据结构

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ArrayList 底层数据结构与扩容 |
| 能做什么 | 辨析底层 Object[]；辨析 1.5 倍扩容；区分与 LinkedList |
| 怎么用 | 答案选 B 数组 |
| 原理和工作流程 | ArrayList 底层 Object[] elementData 动态数组，随机访问 O(1)。扩容时增长至原来的 1.5 倍用 Arrays.copyOf 复制。适合随机访问与尾追加场景 |
| 缺点 | 易误选链表；1.5 倍易与 HashMap 翻倍混；中间增删 O(n) |

### 选择题 5：线程池四种拒绝策略

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ThreadPoolExecutor 四种拒绝策略 |
| 能做什么 | 列举 CallerRuns、Abort、Discard、DiscardOldest；辨析默认 Abort |
| 怎么用 | 答案选 E 以上都是 |
| 原理和工作流程 | 四种拒绝策略均为 ThreadPoolExecutor 内部类：CallerRunsPolicy 由提交线程执行；AbortPolicy 抛 RejectedExecutionException 默认；DiscardPolicy 直接丢弃；DiscardOldestPolicy 丢弃队列最老任务再提交。线程超核心数满队列满最大数后触发 |
| 缺点 | 四策略易记混；默认策略易误选；触发条件易忽略 |

### 选择题 6：synchronized 锁升级顺序

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 synchronized 锁升级的不可逆顺序 |
| 能做什么 | 辨析无锁→偏向→轻量级→重量级；辨析不可逆；辨析偏向可批量撤销 |
| 怎么用 | 答案选 A 偏向锁→轻量级锁→重量级锁 |
| 原理和工作流程 | 锁升级顺序：无锁→偏向锁单线程 CAS 设线程 ID→轻量级锁多线程交替 CAS 自旋→重量级锁激烈竞争操作系统互斥量。升级不可逆但偏向锁可被批量撤销。JDK6 引入优化提升性能 |
| 缺点 | 顺序易记反；不可逆易忽略；偏向锁撤销机制易混 |

### 选择题 7：volatile 作用

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 volatile 保证可见性与禁止重排但不保证原子性 |
| 能做什么 | 辨析可见性；辨析禁止重排；辨析不保证原子性 |
| 怎么用 | 答案选 B 保证可见性和禁止指令重排序 |
| 原理和工作流程 | volatile 保证可见性修改后刷主存其他线程可见，禁止指令重排通过内存屏障，但不保证原子性因 i++ 是读改写复合操作。不能用 volatile 代替 synchronized |
| 缺点 | 易误选保证原子性；易误选保证线程安全；与 synchronized 关系易混 |

### 选择题 8：ThreadLocal 内存泄漏

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ThreadLocal 致内存泄漏的机制 |
| 能做什么 | 辨析 key 弱引用 value 强引用；辨析线程池场景；说明 remove 解决 |
| 怎么用 | 答案选 B 内存泄漏 |
| 原理和工作流程 | ThreadLocalMap 的 Entry 中 key 是 ThreadLocal 弱引用 value 是强引用。ThreadLocal 被 GC 后 key 变 null 但 value 强引用无法回收，线程存活致 value 常驻泄漏，线程池场景严重。解决用完 finally 调 remove |
| 缺点 | 易误选死锁；key value 引用类型易混；线程池场景易忽略 |

### 选择题 9：新生代与老年代比例

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 JVM 堆新生代与老年代默认比例 |
| 能做什么 | 辨析 NewRatio=2 即老年代比新生代 2:1；辨析新生代占 1/3 |
| 怎么用 | 答案选 B 1:2 |
| 原理和工作流程 | 默认 -XX:NewRatio=2 即老年代比新生代为 2:1，新生代占堆的 1/3。新生代再分 Eden 与两个 Survivor 比例 8:1:1。比例影响 GC 频率需调优 |
| 缺点 | 比例方向易记反；NewRatio 含义易混；1/3 计算易错 |

### 选择题 10：CMS 垃圾收集器算法

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 CMS 收集器底层算法 |
| 能做什么 | 辨析标记-清除；辨析产生碎片；区分 G1 算法 |
| 怎么用 | 答案选 B 标记-清除算法 |
| 原理和工作流程 | CMS 老年代收集器基于标记-清除算法产生内存碎片，四阶段初始标记、并发标记、重新标记、并发清除。G1 基于标记-整理加复制无碎片。CMS 适合中小堆低延迟已逐步被 G1 替代 |
| 缺点 | 易误选标记-整理；碎片问题易忽略；与 G1 算法易混 |

### 选择题 11：三种类加载器

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Java 三大内置类加载器 |
| 能做什么 | 辨析 Bootstrap、Extension、Application；辨析 Network 非内置 |
| 怎么用 | 答案选 D Network ClassLoader |
| 原理和工作流程 | Java 三大类加载器：Bootstrap 启动类加载器加载 lib 核心类，Extension 扩展类加载器加载 ext 目录，Application 应用类加载器加载 classpath。Network 非内置可自定义。三者按双亲委派层级协作 |
| 缺点 | 三加载器名称易混；Bootstrap 为 C++ 易忽略；自定义加载器概念易混 |

### 选择题 12：双亲委派核心方法

| 维度 | 内容 |
|------|------|
| 是什么 | 考查双亲委派模型的实现方法 |
| 能做什么 | 辨析 loadClass 实现委派；辨析 findClass 供重写；区分两方法职责 |
| 怎么用 | 答案选 B loadClass() |
| 原理和工作流程 | ClassLoader.loadClass 实现双亲委派逻辑：先检查是否已加载再委托父加载器最后自己尝试。findClass 是子类需重写的方法负责实际加载。defineClass 将字节码转为 Class。自定义类加载器重写 findClass 即可保持委派 |
| 缺点 | loadClass 与 findClass 易混；职责易记反；defineClass 易忽略 |

### 选择题 13：G1 收集器特点

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 G1 收集器的特性辨析 |
| 能做什么 | 辨析 Region 划分；辨析可预测停顿；辨析局部仍有碎片；辨析回收价值最大 |
| 怎么用 | 答案选 C 没有碎片化问题 |
| 原理和工作流程 | G1 将堆划分为多个 Region，可预测停顿时间通过 MaxGCPauseMillis，优先回收价值最大 Region。使用标记-整理加复制整体无碎片但局部 Region 仍有碎片可控。故没有碎片化问题不是 G1 特点 |
| 缺点 | 局部碎片易误判无碎片；Region 概念易混；可预测停顿易忽略 |

### 选择题 14：String final 原因

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 String 设计为 final 的原因 |
| 能做什么 | 辨析保证线程安全不可变；辨析常量池优化；辨析 HashMap key 安全；辨析便于 GC |
| 怎么用 | 答案选 D 以上都是 |
| 原理和工作流程 | String 设计为 final 不可变带来线程安全无需同步，字符串常量池共享节省内存，作为 HashMap key 不可变保证 hashCode 缓存稳定，便于 GC。不可变性是多好处的综合体现 |
| 缺点 | 易漏选便于 GC；不可变原因多；与 StringBuilder 区别易混 |

### 选择题 15：equals 与 hashCode 关系

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 equals 与 hashCode 的契约关系 |
| 能做什么 | 辨析 equals 相等 hashCode 必相等；辨析 hashCode 相等 equals 不一定；辨析哈希碰撞 |
| 怎么用 | 答案选 A equals 相等 hashCode 一定相等 |
| 原理和工作流程 | Java 规范要求 equals 相等的对象 hashCode 必须相等。但 hashCode 相等时 equals 不一定相等即哈希碰撞。重写 equals 必须重写 hashCode 保证一致否则 HashMap、HashSet 出错 |
| 缺点 | 关系方向易记反；哈希碰撞易忽略；重写一致性易忘 |

### 选择题 16：CAS ABA 解决

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 CAS 的 ABA 问题及解决方案 |
| 能做什么 | 辨析 ABA 现象；辨析 AtomicStampedReference 版本号；区分其他方案无效 |
| 怎么用 | 答案选 B 使用版本号 AtomicStampedReference |
| 原理和工作流程 | CAS 的 ABA 问题指值从 A 变 B 再变 A，CAS 检测不到中间变化。AtomicStampedReference 通过版本号 stamp 解决，每次更新版本号递增，CAS 同时检查值与版本号。volatile 与 synchronized 不能解决 ABA |
| 缺点 | 易误选加锁；版本号机制易忽略；ABA 危害易低估 |

### 选择题 17：对象进入老年代条件

| 维度 | 内容 |
|------|------|
| 是什么 | 考查对象晋升老年代的触发条件 |
| 能做什么 | 辨析大对象直接分配；辨析年龄达阈值；辨析动态年龄判断；辨析新建对象在 Eden |
| 怎么用 | 答案选 D 对象刚被创建 |
| 原理和工作流程 | 对象进老年代条件：大对象直接分配、年龄达 MaxTenuringThreshold、Survivor 同龄对象超一半动态晋升。新创建对象首先在 Eden 区分配不在老年代。故对象刚被创建不会进老年代 |
| 缺点 | 条件多易漏；新建对象在 Eden 易误选；动态年龄判断易忽略 |

### 选择题 18：-Xms 参数含义

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 JVM 参数 -Xms 的含义 |
| 能做什么 | 辨析初始堆大小；辨析 -Xmx 最大堆；辨析生产建议相等 |
| 怎么用 | 答案选 B 初始堆内存 |
| 原理和工作流程 | -Xms 是初始堆大小 memory start，-Xmx 是最大堆大小 memory max。生产环境建议 -Xms 与 -Xmx 设为相同值避免堆动态扩缩致抖动。Xmn 设新生代，MetaspaceSize 设元空间 |
| 缺点 | -Xms 与 -Xmx 易混；memory start 含义易忘；生产相等建议易忽略 |

### 选择题 19：Full GC 频繁原因

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Full GC 频繁的可能原因辨析 |
| 能做什么 | 辨析内存泄漏；辨析大对象频繁创建；辨析 Metaspace 不足；辨析代码正常不致频繁 |
| 怎么用 | 答案选 C 代码逻辑正常 |
| 原理和工作流程 | Full GC 频繁说明 JVM 内存压力大。内存泄漏、大对象频繁创建、Metaspace 不足均可能导致。代码逻辑正常通常不会导致 Full GC 频繁，故代码逻辑正常不是原因 |
| 缺点 | 原因多易漏判；代码正常易误选为原因；Metaspace 易忽略 |

### 选择题 20：supplyAsync 与 runAsync 区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 CompletableFuture 两方法的返回值区别 |
| 能做什么 | 辨析 supplyAsync 有返回值；辨析 runAsync 无返回值；区分 Supplier 与 Runnable |
| 怎么用 | 答案选 A 一个有返回值一个没有 |
| 原理和工作流程 | supplyAsync 接收 Supplier 有返回值返回 CompletableFuture<T>。runAsync 接收 Runnable 无返回值返回 CompletableFuture<Void>。两者均异步执行默认用 ForkJoinPool |
| 缺点 | 两方法易混；Supplier 与 Runnable 易混；返回类型易忽略 |

### 选择题 21：char 类型字节数

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Java char 类型占用字节数 |
| 能做什么 | 辨析 char 占 2 字节；辨析 Unicode 编码；区分 C 语言 char 1 字节 |
| 怎么用 | 答案选 B 2 字节 |
| 原理和工作流程 | Java 的 char 使用 Unicode 编码固定占 2 字节 16 位，范围 0 到 65535。C 语言的 char 占 1 字节。Java char 可存一个中文字符 |
| 缺点 | 易误选 1 字节；与 C 语言 char 易混；Unicode 范围易忘 |

### 选择题 22：switch 不支持的数据类型

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 switch 支持与不支持的数据类型 |
| 能做什么 | 辨析支持 byte short char int String enum；辨析不支持 long float double boolean |
| 怎么用 | 答案选 C double |
| 原理和工作流程 | switch 支持 byte、short、char、int、String（JDK7+）、enum（JDK5+），JDK14+ 支持模式匹配。不支持 long、float、double、boolean。double 因浮点不精确不适合离散匹配 |
| 缺点 | 支持类型易记不全；double 易误判支持；long 不支持易忽略 |

### 选择题 23：数组特性辨析

| 维度 | 内容 |
|------|------|
| 是什么 | 考查数组长度、二维不规则、静态初始化语法的辨析 |
| 能做什么 | 辨析长度不可变；辨析二维可不规则；辨析默认值依赖类型；辨析静态初始化不能指定长度 |
| 怎么用 | 答案选 C 数组的默认值取决于元素类型 |
| 原理和工作流程 | 数组长度不可变创建后固定。二维数组每行长度可不同形成不规则数组。数组默认值取决于元素类型 int 为 0 引用为 null。静态初始化 `new int[]{1,2,3}` 不能同时指定长度与元素即不能写 `new int[3]{1,2,3}` |
| 缺点 | 长度不可变易误选可变；静态初始化语法易误；二维不规则易忽略 |

### 选择题 24：finally 与 catch return

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 catch 有 return 时 finally 的执行时机 |
| 能做什么 | 辨析 finally 必执行；辨析在 return 之前执行；辨析 finally return 覆盖 |
| 怎么用 | 答案选 C 会执行且 finally 在 return 之前执行 |
| 原理和工作流程 | finally 一定会执行除非 System.exit 或 JVM 崩溃。catch 的 return 值先暂存，执行 finally 后再返回。若 finally 中也有 return 会覆盖 catch 的 return 值并吞掉异常。故 finally 在 catch return 之前执行 |
| 缺点 | 执行时机易误判；return 覆盖易忽略；finally 不执行条件易忘 |

### 选择题 25：泛型类型擦除

| 维度 | 内容 |
|------|------|
| 是什么 | 考查泛型类型擦除的机制辨析 |
| 能做什么 | 辨析运行时无泛型信息；辨析 List<String> 与 List<Integer> 同 Class；辨析擦除为 Object 或上界 |
| 怎么用 | 答案选 C 泛型擦除后类型参数被替换为 Object 或其上界 |
| 原理和工作流程 | Java 泛型通过类型擦除实现编译后泛型信息被擦除。List<String> 与 List<Integer> 运行时是同一 Class。擦除后类型参数无界替换为 Object 有界替换为上界。方法签名中的泛型信息保留在字节码可通过反射获取 |
| 缺点 | 运行时保留易误选；同 Class 易误判不同；反射获取泛型易误选不能 |

### 选择题 26：字符流辨析

| 维度 | 内容 |
|------|------|
| 是什么 | 考查字节流与字符流的命名区分 |
| 能做什么 | 辨析 Stream 结尾为字节流；辨析 Reader/Writer 结尾为字符流；辨析 FileReader 为字符流 |
| 怎么用 | 答案选 C FileReader |
| 原理和工作流程 | 以 Stream 结尾的是字节流如 FileInputStream、BufferedInputStream。以 Reader 或 Writer 结尾的是字符流如 FileReader。FileReader 是字符输入流内部依赖 InputStreamReader 桥接字节到字符 |
| 缺点 | 命名规律易混；FileReader 易误判字节流；缓冲流归属易错 |

### 选择题 27：TCP 第三次握手作用

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 TCP 第三次握手的作用 |
| 能做什么 | 辨析防止失效连接请求到达服务端；辨析确认双方收发能力 |
| 怎么用 | 答案选 C 防止已失效的连接请求到达服务端 |
| 原理和工作流程 | 第三次握手客户端发送 ACK 主要是防止已失效的连接请求报文段突然又传到服务端，导致服务端错误建立连接浪费资源。三次握手同时确认双方收发能力，两次握手无法防止失效连接 |
| 缺点 | 作用易与确认收发能力混；两次握手缺陷易忽略；失效连接场景难理解 |

### 选择题 28：获取 Class 对象方式

| 维度 | 内容 |
|------|------|
| 是什么 | 考查获取 Class 对象的三种方式 |
| 能做什么 | 辨析 Class.forName、类名.class、对象.getClass；辨析 Class.newInstance 非获取方式 |
| 怎么用 | 答案选 D Class.newInstance 不是获取方式 |
| 原理和工作流程 | 获取 Class 对象三种方式：Class.forName(全限定名) 按名加载触发初始化、类名.class 编译期已知不初始化、对象.getClass() 运行时获取。Class.newInstance 是创建实例的方法 JDK9 已废弃推荐 getDeclaredConstructor().newInstance |
| 缺点 | newInstance 易误判为获取方式；三种方式初始化差异易混；newInstance 已废弃易忽略 |

### 选择题 29：Lambda 语法辨析

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Lambda 表达式的语法形式辨析 |
| 能做什么 | 辨析单条语句省略 return；辨析多条语句需 return；辨析表达式形式 |
| 怎么用 | 答案选 B 单条语句返回值 |
| 原理和工作流程 | Lambda 三种语法：参数->单条语句可省略 return 与花括号、参数->{多条语句;return 值;}、参数->表达式。`(a,b)->a+b` 属于第一种省略 return 与花括号的单条语句返回值形式 |
| 缺点 | 三种语法易混；省略规则易忘；与方法引用易混 |

### 选择题 30：Stream filter 操作类型

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Stream 操作的中间与终端分类 |
| 能做什么 | 辨析 filter 为中间操作；辨析惰性求值；区分终端操作 |
| 怎么用 | 答案选 B 中间操作 |
| 原理和工作流程 | Stream 操作分中间操作 filter、map、sorted、distinct 返回 Stream 惰性求值，与终端操作 forEach、collect、reduce、count 返回非 Stream 触发执行。filter 是中间操作记录谓词不立即执行 |
| 缺点 | 中间与终端易混；惰性求值易忽略；filter 易误判终端 |

---

## 二、简答题（15 题）

### 简答题 1：HashMap 的 put 流程

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 HashMap put 方法的完整执行流程 |
| 能做什么 | 描述 hash 计算与下标定位；描述空桶插入与链表尾插；描述树化与扩容触发 |
| 怎么用 | hash 扰动后 (n-1)&hash 定下标 |
| 原理和工作流程 | 一算 key 的 hash 高 16 位与低 16 位异或扰动。二 table 为 null 则 resize 初始化。三 (n-1)&hash 定下标空桶直接插入。四首节点 key 匹配则覆盖旧值。五链表则尾插红黑树则树插入。六链表长度超 8 且数组达 64 调 treeifyBin 树化。七++size 超 threshold 触发 resize 扩容 |
| 缺点 | 流程长易遗漏步骤；树化条件易忘；扰动函数易忽略 |

### 简答题 2：ConcurrentHashMap JDK7 与 JDK8 区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ConcurrentHashMap 两版线程安全实现区别 |
| 能做什么 | 描述 JDK7 Segment 分段锁；描述 JDK8 CAS 加 synchronized；说明锁粒度降低 |
| 怎么用 | JDK7 并发度 16，JDK8 并发度等于桶数 |
| 原理和工作流程 | JDK7 用 Segment 分段锁继承 ReentrantLock 默认并发度 16 锁粒度为 Segment，每 Segment 内独立 HashMap。JDK8 用 CAS 加 synchronized 锁粒度为单个 Node 节点，空桶 CAS 插入非空桶对桶头加锁。本质区别锁粒度从 Segment 降到单桶 |
| 缺点 | 两版机制易混；并发度差异易忽略；锁粒度概念难理解 |

### 简答题 3：synchronized 与 ReentrantLock 区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查内置锁与显式锁的区别 |
| 能做什么 | 区分 JVM 与 API 层面；区分自动与手动释放；区分功能特性；说明性能接近 |
| 怎么用 | 简单用 synchronized，高级特性用 ReentrantLock |
| 原理和工作流程 | synchronized 是 JVM 关键字基于 Monitor 自动释放不可中断非公平。ReentrantLock 是 API 层需手动 unlock 在 finally，支持公平锁、lockInterruptibly 可中断、tryLock 超时、多 Condition。JDK6 锁升级后 synchronized 性能接近 ReentrantLock |
| 缺点 | 两者特性多易混；释放方式易忘；选型原则易忽略 |

### 简答题 4：线程池核心参数与执行流程

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ThreadPoolExecutor 七参数与提交流程 |
| 能做什么 | 列举七参数；描述四步执行流程；说明拒绝策略触发 |
| 怎么用 | corePoolSize、maximumPoolSize、keepAliveTime、unit、workQueue、threadFactory、handler |
| 原理和工作流程 | 七参数为核心线程数、最大线程数、空闲存活时间、单位、任务队列、线程工厂、拒绝策略。执行流程：线程数小于 corePoolSize 创建核心线程；满则入队列；队列满且小于 maximumPoolSize 创建非核心线程；满则执行拒绝策略 |
| 缺点 | 七参数易遗漏；流程顺序易乱；队列与最大线程先后易混 |

### 简答题 5：AQS 原理与 ReentrantLock 实现

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 AQS 框架三要素与 ReentrantLock 基于其实现 |
| 能做什么 | 描述 state 与 CLH 队列；描述独占共享模式；描述 ReentrantLock 用 state 表示锁状态 |
| 怎么用 | state 0 未锁 1 已锁 大于 1 重入 |
| 原理和工作流程 | AQS 基于 CLH 队列的同步框架三要素：volatile int state 同步状态、CLH 双向链表存等待线程、独占与共享模式。ReentrantLock 内部 Sync 继承 AQS 用 state 表示锁状态 0 未锁 1 已锁大于 1 重入。获取锁 CAS 将 state 从 0 改 1 失败入队，释放减 1 到 0 唤醒队首 |
| 缺点 | 三要素易遗漏；state 语义易混；CLH 队列机制难理解 |

### 简答题 6：JVM 垃圾回收判定方法

| 维度 | 内容 |
|------|------|
| 是什么 | 考查垃圾回收的对象判定方法 |
| 能做什么 | 描述引用计数法缺陷；描述可达性分析；列举 GC Roots |
| 怎么用 | Java 用可达性分析 |
| 原理和工作流程 | 引用计数法每对象维护引用计数为 0 回收，无法解决循环引用。可达性分析 Java 使用从 GC Roots 出发通过引用链可达为存活不可达为垃圾。GC Roots 包括栈帧局部变量、静态变量、JNI 引用、活跃线程、synchronized 持有对象 |
| 缺点 | 引用计数缺陷易忘；GC Roots 易列举不全；循环引用易忽略 |

### 简答题 7：类加载过程

| 维度 | 内容 |
|------|------|
| 是什么 | 考查类加载的五个阶段 |
| 能做什么 | 描述加载验证准备解析初始化；说明各阶段职责；区分准备与初始化赋值 |
| 怎么用 | 准备赋零值，初始化赋实际值 |
| 原理和工作流程 | 加载获取字节流生成 Class 对象。验证检查格式与语义合法性。准备为静态变量分配内存赋零值如 static int a=1 此阶段 a=0。解析符号引用转直接引用。初始化执行 clinit 静态变量赋值与静态代码块。后接使用与卸载 |
| 缺点 | 五阶段易遗漏；准备与初始化赋值易混；解析概念难理解 |

### 简答题 8：打破双亲委派的场景

| 维度 | 内容 |
|------|------|
| 是什么 | 考查需打破双亲委派模型的场景 |
| 能做什么 | 描述 JDBC SPI；描述 Tomcat 隔离；描述热部署；描述 OSGi |
| 怎么用 | SPI 用线程上下文类加载器 |
| 原理和工作流程 | JDBC 驱动 DriverManager 在 rt.jar 由 Bootstrap 加载但驱动在 classpath 由 Application 加载，Bootstrap 无法向下委托需线程上下文类加载器。Tomcat 每 WebApp 独立 WebappClassLoader 实现应用隔离。热部署卸载旧加载器创建新加载器。OSGi 每 Bundle 独立加载器实现模块隔离 |
| 缺点 | 场景多易遗漏；SPI 机制难理解；线程上下文类加载器易忘 |

### 简答题 9：G1 与 CMS 区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 G1 与 CMS 收集器的多维区别 |
| 能做什么 | 对比算法；对比堆结构；对比停顿；对比回收范围；对比适用场景 |
| 怎么用 | CMS 适合小于 4GB，G1 适合大于 4GB |
| 原理和工作流程 | 算法 CMS 标记-清除有碎片，G1 标记-整理加复制可控。堆结构 CMS 连续分代，G1 划分 Region。停顿 CMS 不可预测，G1 可预测通过 MaxGCPauseMillis。回收范围 CMS 仅老年代，G1 全堆 Young GC 加 Mixed GC。适用 CMS 中小堆小于 4GB，G1 大堆大于 4GB |
| 缺点 | 多维区别易混；适用场景易记反；算法区别易忽略 |

### 简答题 10：ThreadLocal 原理与内存泄漏

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 ThreadLocal 原理与内存泄漏机制 |
| 能做什么 | 描述 ThreadLocalMap 结构；描述 key 弱 value 强；说明 remove 解决；列举场景 |
| 怎么用 | 用完 finally 调 remove |
| 原理和工作流程 | 每 Thread 内有 ThreadLocalMap，key 是 ThreadLocal 弱引用 value 强引用。ThreadLocal 被 GC 后 key 变 null 但 value 强引用无法回收线程存活致泄漏。解决每次用完 remove。场景数据库连接、Session、TraceId、SimpleDateFormat 线程安全 |
| 缺点 | key value 引用类型易混；泄漏机制难理解；remove 易忘 |

### 简答题 11：值传递与引用传递

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Java 只有值传递的概念 |
| 能做什么 | 说明基本类型传值副本；说明引用类型传地址副本；说明 swap 无法交换 |
| 怎么用 | Java 只有值传递没有引用传递 |
| 原理和工作流程 | Java 只有值传递。基本类型传递值的副本修改不影响原值。引用类型传递引用的副本指向同一对象，修改对象内容影响原对象但修改引用本身如设 null 不影响原引用。swap 无法交换因传入的是引用副本 |
| 缺点 | 引用类型易误判引用传递；swap 失败难理解；值传递概念易混 |

### 简答题 12：Checked 与 Unchecked Exception

| 维度 | 内容 |
|------|------|
| 是什么 | 考查受检与非受检异常的区别 |
| 能做什么 | 区分继承关系；区分编译检查；列举典型异常；说明设计原则 |
| 怎么用 | 可恢复用 Checked，编程错误用 Unchecked |
| 原理和工作流程 | Checked Exception 继承 Exception 非 RuntimeException 编译时必须 try-catch 或 throws 如 IOException。Unchecked Exception 继承 RuntimeException 编译时不强制如 NPE。Error 表示 JVM 级严重错误不应捕获如 OOM。设计原则可恢复用 Checked 编程错误用 Unchecked |
| 缺点 | 继承关系易混；编译检查差异易忘；Error 归属易错 |

### 简答题 13：serialVersionUID 作用

| 维度 | 内容 |
|------|------|
| 是什么 | 考查序列化版本号的作用 |
| 能做什么 | 说明版本校验；说明不显式声明的风险；说明最佳实践 |
| 怎么用 | `private static final long serialVersionUID = 1L;` |
| 原理和工作流程 | serialVersionUID 是序列化版本号验证序列化与反序列化版本一致性。未显式定义 JVM 按类结构自动生成，类结构变化致版本号变化。反序列化时版本不匹配抛 InvalidClassException。最佳实践显式定义兼容性修改保持不变 |
| 缺点 | 不显式声明风险易忽略；自动生成机制易忘；兼容性边界难把握 |

### 简答题 14：TCP 与 UDP 区别及场景

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 TCP 与 UDP 的区别与适用场景 |
| 能做什么 | 对比连接可靠性有序性开销；列举适用场景；说明 TCP 可靠机制 |
| 怎么用 | 可靠用 TCP，实时用 UDP |
| 原理和工作流程 | TCP 面向连接三次握手可靠有序确认重传流量拥塞控制头部 20 字节适合文件传输 HTTP 邮件。UDP 无连接不可靠无序头部 8 字节适合视频直播 DNS 游戏。TCP 通过序列号确认重传流量控制拥塞控制保证可靠性 |
| 缺点 | 多维区别易混；场景易记反；TCP 可靠机制易遗漏 |

### 简答题 15：Stream map 与 flatMap 区别

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 Stream 中 map 与 flatMap 的区别 |
| 能做什么 | 描述 map 一对一映射；描述 flatMap 一对多扁平化；列举典型场景 |
| 怎么用 | map 提取属性，flatMap 展开嵌套集合 |
| 原理和工作流程 | map 一对一映射每个元素转为另一个元素 Stream<T> 到 Stream<R>，用于提取对象属性如 map(User::getName)。flatMap 一对多映射每个元素转为 Stream 再扁平化合并 Stream<T> 到 Stream<R>，用于展开嵌套集合如 flatMap(Collection::stream)。类比 flatMap 等于 map 加 flatten |
| 缺点 | 两者易混；扁平化概念难理解；场景易记反 |

---

## 三、编程题（8 题）

### 编程题 1：LRU 缓存基于 LinkedHashMap

| 维度 | 内容 |
|------|------|
| 是什么 | 考查基于 LinkedHashMap 实现 LRU 缓存 |
| 能做什么 | 继承 LinkedHashMap 设 accessOrder；重写 removeEldestEntry；自动删除最旧 |
| 怎么用 | `super(capacity,0.75f,true)` 设访问顺序 |
| 原理和工作流程 | 继承 LinkedHashMap 构造时设 accessOrder 为 true 按访问顺序排序，最近访问移到尾部。重写 removeEldestEntry 当 size 大于 capacity 返回 true 自动删除头部最旧元素即最久未访问。get 与 put 都会更新访问顺序。利用 LinkedHashMap 双向链表维护顺序 |
| 缺点 | 非线程安全需 Collections.synchronizedMap 或 ConcurrentHashMap 改造；继承限制；容量判断时机 |

### 编程题 2：线程安全单例 DCL 加 volatile

| 维度 | 内容 |
|------|------|
| 是什么 | 考查手写双重检查锁定单例 |
| 能做什么 | volatile 修饰实例；两次 if 检查；synchronized 同步块；防指令重排 |
| 怎么用 | `private static volatile Singleton instance;` |
| 原理和工作流程 | private static volatile 修饰 instance 防指令重排。getInstance 第一次 if 检查避免不必要同步，synchronized 同步块内第二次 if 确保只创建一个实例。volatile 防 new 的分配内存、初始化、赋引用三步重排致其他线程获未初始化对象。构造器私有 |
| 缺点 | volatile 易忘；两次检查易漏；静态内部类与枚举更简洁 |

### 编程题 3：实现简单线程池

| 维度 | 内容 |
|------|------|
| 是什么 | 考查手写简易线程池 |
| 能做什么 | 维护 BlockingQueue 任务队列；Worker 线程循环取任务；核心线程数与拒绝策略 |
| 怎么用 | `BlockingQueue<Runnable>` 加 `List<Worker>` |
| 原理和工作流程 | 维护 BlockingQueue 任务队列与 List<Worker> 线程集合。构造时创建核心 Worker 线程循环从队列 poll 任务执行。execute 提交任务入队队列满抛 RejectedExecutionException。Worker 继承 Thread run 方法循环 poll 任务执行。isShutdown 控制停止 |
| 缺点 | 简化版缺最大线程与扩容；非核心线程回收；拒绝策略单一；边界处理简化 |

### 编程题 4：手写阻塞队列（基于 ReentrantLock + Condition）

| 维度 | 内容 |
|------|------|
| 是什么 | 考查基于 ReentrantLock 加双 Condition 实现阻塞队列 |
| 能做什么 | 实现线程安全的 put 入队阻塞与 take 出队阻塞；支持超时等待；区分 notFull 与 notEmpty 条件 |
| 怎么用 | `ReentrantLock lock` 加 `Condition notFull` 和 `Condition notEmpty` |
| 原理和工作流程 | 维护循环数组 items 与 count、putIndex、takeIndex。put 加锁后若满则 notFull.await 阻塞等待，入队后 notEmpty.signal 唤醒出队线程。take 加锁后若空则 notEmpty.await 阻塞等待，出队后 notFull.signal 唤醒入队线程。支持带超时的 offer 和 poll 方法。两个 Condition 实现精确唤醒，避免无效竞争 |
| 缺点 | 单锁粒度粗；无优先级；无公平模式；需注意虚假唤醒 |

### 编程题 5：手写 ConcurrentHashMap 简化版

| 维度 | 内容 |
|------|------|
| 是什么 | 考查基于分段锁思想手写并发 Map |
| 能做什么 | 定义 Segment 数组；每 Segment 继承 ReentrantLock；put 定位 Segment 加锁；get 无锁 |
| 怎么用 | `hash % segments.length` 定位段 |
| 原理和工作流程 | 定义 Segment 数组每 Segment 继承 ReentrantLock 内部维护 Node 数组小 HashMap。put 先 hash 定位 Segment 再对 Segment 加锁操作链表。get 无锁因 volatile 读。模拟 JDK7 分段锁思想降低锁粒度提升并发度。Segment 内 put 用 lock 与 unlock 配合 finally |
| 缺点 | 模拟 JDK7 已废弃思想；缺扩容与树化；get 一致性简化；无 size 统计 |

### 编程题 6：Stream 分组统计平均薪资

| 维度 | 内容 |
|------|------|
| 是什么 | 考查用 Stream 按部门统计员工平均薪资 |
| 能做什么 | groupingBy 分组；averagingDouble 求平均；返回 Map |
| 怎么用 | `collect(groupingBy(Employee::getDepartment, averagingDouble(Employee::getSalary)))` |
| 原理和工作流程 | 用 stream 流式处理，collect 触发终止操作。groupingBy 按部门分组为 Map，下游收集器 averagingDouble 计算每部门薪资平均值。相比传统 for 循环遍历加 Map 累加再除以数量更声明式简洁。collect 触发流水线一次遍历完成分组与统计 |
| 缺点 | 收集器 API 需熟悉；调试不直观；大数据量需考虑并行流；空值处理 |

### 编程题 7：反射实现依赖注入

| 维度 | 内容 |
|------|------|
| 是什么 | 考查用反射实现简单依赖注入 |
| 能做什么 | 扫描字段注解；setAccessible；反射创建依赖实例；field.set 注入 |
| 怎么用 | `field.isAnnotationPresent(Autowired.class)` |
| 原理和工作流程 | createBean 用 getDeclaredConstructor().newInstance 创建实例。遍历 declaredFields 判断 @Autowired 注解，setAccessible(true) 后用 field.getType().getDeclaredConstructor().newInstance 创建依赖实例并 field.set 注入。模拟 Spring @Autowired 字段注入的简化版 |
| 缺点 | 仅字段注入无构造器方法注入；无循环依赖处理；依赖类型无注册表；异常处理简化 |

### 编程题 8：try-with-resources 文件复制

| 维度 | 内容 |
|------|------|
| 是什么 | 考查用 try-with-resources 实现文件复制 |
| 能做什么 | 声明缓冲流资源；自动关闭；循环读写；无需 finally |
| 怎么用 | `try(BufferedInputStream bis=...; BufferedOutputStream bos=...)` |
| 原理和工作流程 | try-with-resources 声明 BufferedInputStream 与 BufferedOutputStream 资源，try 块结束自动调用 close 无需 finally 手动关闭。用 8192 字节缓冲区循环 read 与 write 提升性能。资源须实现 AutoCloseable。编译后展开为 try-catch-finally 自动正确关闭 |
| 缺点 | 资源须 AutoCloseable；JDK7 才支持；缓冲区大小需选择；异常处理 |

---

> [返回原文](./17-Java核心笔面试题集.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
