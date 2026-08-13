# 常用类与基础 API 导览

> 定位：五维框架浓缩提炼 07-常用类与基础API.md 全部内容小节，快速查阅与复习。
> 用法：每个内容小节对应一张纵向表格，需要深入理解时跳转 [原文](./07-常用类与基础API.md).
> 前置知识：[04-数组-导览](./04-数组-导览.md)

---

## 一、核心概念

### 1.1 String 类与不可变性

| 维度 | 内容 |
|------|------|
| 是什么 | 用 final 修饰、底层用 final 数组存储的不可变字符串类 |
| 能做什么 | 字面量与 new 两种创建方式；常量池复用；提供 length、substring、replace 等方法；与基本类型互转 |
| 怎么用 | `String s = "hello";` 或 `Integer.parseInt("123")` |
| 原理和工作流程 | String 被 final 修饰不可继承，底层 value 为 final 数组内容不可改，任何修改操作返回新对象。不可变性使字符串常量池共享同一对象节省内存，保证线程安全，并缓存 hashCode。创建方式：字面量进常量池，new 在堆建对象。JDK9 改为 byte[] 加 coder 实现 Compact Strings，Latin-1 单字节省内存 |
| 缺点 | 不可变致拼接产生大量临时对象；循环拼接性能差；占用常量池内存 |

### 1.2 StringBuilder 与 StringBuffer

| 维度 | 内容 |
|------|------|
| 是什么 | 继承 AbstractStringBuilder 的可变字符序列类，StringBuffer 加 synchronized 线程安全 |
| 能做什么 | append 追加；insert 插入；delete 删除；replace 替换；reverse 反转 |
| 怎么用 | `StringBuilder sb = new StringBuilder(); sb.append("a").append(1);` |
| 原理和工作流程 | 二者均提供可变字符序列避免 String 拼接产生临时对象。StringBuilder 非线程安全性能最高，StringBuffer 方法加 synchronized 线程安全有同步开销。单线程大量拼接用 StringBuilder，多线程用 StringBuffer。拼接超 3 次即应使用 StringBuilder 而非 String + |
| 缺点 | StringBuilder 非线程安全；StringBuffer 同步开销大；容量预估不当多次扩容 |

### 1.3 JDK 8 前后日期时间 API 对比

| 维度 | 内容 |
|------|------|
| 是什么 | 旧 Date 与 Calendar API 与 JDK8 引入的 java.time 新 API 的对比 |
| 能做什么 | 旧 API 表示时间戳与日历；新 API 提供不可变线程安全的 LocalDate、LocalTime、LocalDateTime、ZonedDateTime、Instant、Duration、Period |
| 怎么用 | 新 API `LocalDate.now()`、`LocalDateTime.of(2024,1,1,10,0)` |
| 原理和工作流程 | 旧 Date 表示时间戳月份从 0 开始且可变线程不安全，Calendar 配套使用繁琐。JDK8 引入 java.time 包：LocalDate 仅日期、LocalTime 仅时间、LocalDateTime 日期时间、ZonedDateTime 带时区、Instant 时间戳、Duration 时间差、Period 日期差。新 API 不可变线程安全，用 of、plus、minus、with 链式操作，DateTimeFormatter 线程安全格式化 |
| 缺点 | 旧 API 仍大量存在遗留代码；新 API 类多需熟悉；新旧互转需 Instant 桥接 |

### 1.4 System 类与常用工具方法

| 维度 | 内容 |
|------|------|
| 是什么 | java.lang.System 提供的系统级工具类，含标准流、时间、属性、环境变量、退出方法 |
| 能做什么 | 标准输入输出流；获取毫秒与纳秒时间戳；获取系统属性与环境变量；复制数组；强制 GC |
| 怎么用 | `System.out.println()`、`System.currentTimeMillis()`、`System.arraycopy(src,0,dst,0,len)` |
| 原理和工作流程 | System 是 final 类私有构造全静态方法。out、in、err 是标准流静态字段。currentTimeMillis 返回毫秒时间戳，nanoTime 返回纳秒用于测量时间差非时间点。arraycopy 是 native 方法高性能复制数组。getProperty 获取系统属性，getenv 获取环境变量。exit 终止 JVM，gc 建议 GC |
| 缺点 | exit 强制终止风险大；gc 不保证立即回收；System.in 读取需包装；nanoTime 非时间点不可用于时间戳 |

### 1.5 Math 类与 Random

| 维度 | 内容 |
|------|------|
| 是什么 | Math 提供数学函数，Random 提供伪随机数生成器 |
| 能做什么 | Math 求绝对值、最大最小、四舍五入、幂指对三角函数；Random 生成随机数 |
| 怎么用 | `Math.max(a,b)`、`new Random().nextInt(100)` |
| 原理和工作流程 | Math 是 final 类全静态方法，包含 abs、max、min、round、pow、sqrt、random 等。Math.random 返回 [0,1) double。Random 基于种子线性同余算法生成伪随机数，相同种子产生相同序列。ThreadLocalRandom 是多线程下更高效的选择，SecureRandom 提供密码学安全随机数 |
| 缺点 | Math.random 需手动缩放；Random 非线程安全；伪随机不适用安全场景；Math.round 对负数半数进位方向易误 |

### 1.6 BigDecimal 与 BigInteger

| 维度 | 内容 |
|------|------|
| 是什么 | BigDecimal 提供任意精度十进制运算，BigInteger 提供任意精度整数运算 |
| 能做什么 | 精确金额计算；指定舍入模式；大整数运算；超 long 范围数值 |
| 怎么用 | `new BigDecimal("0.1").add(new BigDecimal("0.2"))` |
| 原理和工作流程 | BigDecimal 用 BigInteger 存储 unscaledValue 加 scale 表示任意精度小数。**new BigDecimal(double) 有精度陷阱**因 double 已是近似值，应使用 String 构造器或 valueOf。除法须指定舍入模式否则除不尽抛 ArithmeticException，常用 RoundingMode.HALF_UP 四舍五入。BigInteger 用 int 数组存大整数支持任意精度运算 |
| 缺点 | 性能低于基本类型；new(double) 精度陷阱；除法不指定舍入抛异常；对象创建开销 |

### 1.7 Arrays 工具类

| 维度 | 内容 |
|------|------|
| 是什么 | java.util.Arrays 提供数组操作的工具类 |
| 能做什么 | sort 排序；binarySearch 查找；fill 填充；copyOf 复制；equals 比较；toString 转串；asList 转流 |
| 怎么用 | `Arrays.sort(arr)`、`Arrays.binarySearch(arr,5)` |
| 原理和工作流程 | sort 对基本类型用双轴快排对对象用 TimSort。binarySearch 要求数组已排序返回索引未找到返回负的插入点。asList 返回 Arrays 内部固定长度 List 是数组视图不支持 add/remove。stream 生成顺序流支持并行。equals 逐元素比较 |
| 缺点 | asList 返回 List 不可变是高频坑；基本类型数组 asList 整体当元素；binarySearch 前未排序结果错误 |

### 1.8 Objects 工具类（JDK 7+）

| 维度 | 内容 |
|------|------|
| 是什么 | JDK7 引入的对对象操作的静态工具类，提供 null 安全方法 |
| 能做什么 | equals 空安全比较；requireNonNull 校验非空；hashCode 计算哈希；toString 空安全转串；isNull 非Null 判断 |
| 怎么用 | `Objects.equals(a,b)`、`Objects.requireNonNull(obj,"不能为空")` |
| 原理和工作流程 | Objects 全静态方法。equals 内部先判空再调用 a.equals(b) 避免 NPE。requireNonNull 校验参数非空为空抛 NullPointerException 带消息，用于方法参数校验。hashCode 支持多字段生成。toString 提供默认值参数防 null。isNull 与 nonNull 替代 == null 提升可读性 |
| 缺点 | requireNonNull 抛 NPE 仍需调用方处理；过度依赖掩盖设计问题；与 Object 方法易混 |

---

## 二、底层原理

### 2.1 字符串常量池

| 维度 | 内容 |
|------|------|
| 是什么 | JVM 存储字符串字面量实现共享的常量池机制 |
| 能做什么 | 字面量复用同一对象；intern 返回常量池引用；节省内存 |
| 怎么用 | `String s = "hello";` 进常量池，`s.intern()` 查找或入池 |
| 原理和工作流程 | 常量池位置随版本变迁：JDK6 在方法区永久代大小固定易 OOM，JDK7+ 移到堆受 GC 管理可动态调整。字面量创建时查常量池存在则复用不存在则入池。new String("hello") 创建常量池对象加堆对象两个。intern 方法 JDK7+ 若常量池无则存堆对象引用而非复制，故 `new String("a")+new String("b")` intern 后与字面量 == 为 true |
| 缺点 | intern 滥用致常量池膨胀；JDK6 常量池固定易 OOM；new String 双对象浪费内存 |

### 2.2 StringBuilder 扩容机制

| 维度 | 内容 |
|------|------|
| 是什么 | StringBuilder 容量不足时按 2 倍旧容量加 2 扩容的机制 |
| 能做什么 | 初始容量 16；扩容公式 2 倍加 2；预估容量避免多次扩容 |
| 怎么用 | `new StringBuilder(1024)` 预估容量一次分配 |
| 原理和工作流程 | 默认构造初始容量 **16**。append 时若所需长度超当前容量触发扩容，公式为 新容量 = 旧容量 × 2 + 2，若仍不足则取所需最小值。扩容用 Arrays.copyOf 复制旧数组到新数组。每次扩容涉及数组复制有开销，预知长度应在构造时指定容量 |
| 缺点 | 默认容量小易多次扩容；扩容复制有开销；预估过大浪费内存 |

### 2.3 BigDecimal 的精度陷阱原理

| 维度 | 内容 |
|------|------|
| 是什么 | double 无法精确表示十进制小数致 new BigDecimal(double) 产生精度误差的原理 |
| 能做什么 | 解释二进制无法精确表示某些十进制小数；用 String 构造避免误差；理解 IEEE754 截断 |
| 怎么用 | 用 `new BigDecimal("0.1")` 而非 `new BigDecimal(0.1)` |
| 原理和工作流程 | 十进制 0.1 在二进制是无限循环小数，double 仅存 53 位有效位后面被截断故 0.1 是近似值。new BigDecimal(0.1) 会精确捕获这个近似值得 0.1000000000000000055...。正确做法用 String 构造器 `new BigDecimal("0.1")` 得精确 0.1，或用 valueOf 内部先转 String。除法须指定舍入模式 |
| 缺点 | new(double) 陷阱易踩；除法不指定舍入抛异常；性能低于基本类型；运算繁琐 |

---

## 三、实战应用

### 3.1 字符串处理工具箱

| 维度 | 内容 |
|------|------|
| 是什么 | 封装常见字符串判断与处理操作的工具方法集合 |
| 能做什么 | 判空与空白；首字母大小写转换；驼峰下划线互转；重复填充 |
| 怎么用 | `isEmpty(str)`、`capitalize(str)`、`camelToUnderline(str)` |
| 原理和工作流程 | 封装判空（null 与空串与空白）、首字母大小写转换（substring 加 toUpperCase 拼接）、驼峰下划线互转（遍历遇大写转下划线加小写）、重复填充（循环 append）。实际项目优先用 Apache Commons Lang 的 StringUtils 或 Guava 的 Strings 避免重复造轮子 |
| 缺点 | 重复造轮子不如第三方库；边界处理易遗漏；性能敏感场景需手写 |

### 3.2 日期时间处理工具箱

| 维度 | 内容 |
|------|------|
| 是什么 | 基于 java.time 封装的日期时间格式化与计算工具方法 |
| 能做什么 | 格式化与解析；日期加减；计算间隔；判断区间 |
| 怎么用 | `format(LocalDateTime.now(),"yyyy-MM-dd HH:mm:ss")` |
| 原理和工作流程 | 用 DateTimeFormatter 定义格式线程安全替代旧 SimpleDateFormat。format 用 formatter.format 日期，parse 用 formatter.parse 字符串。日期加减用 plusDays、minusMonths。计算间隔用 Duration（时间差）与 Period（日期差）。判断区间用 isBefore、isAfter、isEqual |
| 缺点 | 格式符号需记忆；时区处理复杂；旧代码遗留 SimpleDateFormat 线程不安全 |

### 3.3 资金计算与精度控制

| 维度 | 内容 |
|------|------|
| 是什么 | 用 BigDecimal 实现金额精确计算与舍入控制的实战方案 |
| 能做什么 | 加减乘除精确运算；指定小数位与舍入模式；金额格式化；分元互转 |
| 怎么用 | `amount.divide(BigDecimal.valueOf(3),2,RoundingMode.HALF_UP)` |
| 原理和工作流程 | 金额用 BigDecimal(String) 构造避免 double 误差。加减乘直接调用，除法必须指定 scale 与 RoundingMode 否则除不尽抛异常。常用 HALF_UP 四舍五入保留 2 位小数。金额内部建议用分（long）存储避免精度，展示时转元。数据库用 DECIMAL 类型存储 |
| 缺点 | BigDecimal 运算繁琐性能低；舍入模式选择需谨慎；分元互转易错 |

### 3.4 完整代码示例

> 本节为辅助内容，无五维表格。以综合程序演示 String 不可变验证、StringBuilder 拼接、日期时间 API、BigDecimal 金额计算、Arrays 排序查找、Objects 校验，并附编译运行输出。

---

## 四、常见面试题（附答案）

### 1. String、StringBuilder、StringBuffer 的区别？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查三者可变性、线程安全与性能的差异 |
| 能做什么 | 对比可变性；对比线程安全；对比性能与适用场景 |
| 怎么用 | 少量常量用 String，单线程拼接用 StringBuilder，多线程用 StringBuffer |
| 原理和工作流程 | String 不可变 final 修饰底层 final 数组线程安全但拼接产生新对象。StringBuilder 可变非线程安全性能最高。StringBuffer 可变方法加 synchronized 线程安全有同步开销。性能 StringBuilder > StringBuffer >> String 拼接 |
| 缺点 | String 循环拼接性能灾难；StringBuffer 同步开销；选型不当影响性能 |

### 2. String s = new String("abc") 创建了几个对象？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查 new String 与常量池的创建对象数量 |
| 能做什么 | 区分常量池对象与堆对象；说明常量池复用；解释 intern 行为 |
| 怎么用 | 常量池无则 2 个，有则 1 个 |
| 原理和工作流程 | 若常量池中无 "abc"，先在常量池创建 "abc" 一个对象，再 new 在堆创建一个 String 对象共 2 个。若常量池已有 "abc" 则只 new 创建堆对象 1 个。s 指向堆对象，堆对象 value 指向常量池数据 |
| 缺点 | 对象数量随常量池状态变化易误判；常量池位置变迁增加复杂度 |

### 3. 字符串常量池是什么？intern() 方法的作用？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查常量池机制与 intern 方法行为 |
| 能做什么 | 解释常量池位置变迁；解释字面量复用；解释 intern JDK7+ 行为 |
| 怎么用 | `s.intern()` 返回常量池引用 |
| 原理和工作流程 | 常量池存储字符串字面量实现共享，JDK6 在永久代 JDK7+ 移到堆受 GC 管理。字面量创建查常量池存在复用。intern 方法先查常量池有则返回引用，JDK7+ 若无则存堆对象引用而非复制，故 intern 后可与字面量 == 为 true。intern 可减少内存但需谨慎 |
| 缺点 | intern 滥用致常量池膨胀；JDK6 与 7+ 行为不同易混；== 比较不可依赖 |

### 4. 为什么不能用 double 做金额计算？怎么解决？

| 维度 | 内容 |
|------|------|
| 是什么 | 考查浮点精度问题及 BigDecimal 解决方案 |
| 能做什么 | 解释二进制无法精确表示十进制小数；用 BigDecimal(String)；指定舍入模式 |
| 怎么用 | `new BigDecimal("0.1").add(new BigDecimal("0.2"))` |
| 原理和工作流程 | double 采用 IEEE754 二进制浮点，0.1 等十进制小数是无限循环二进制被截断为近似值，故 0.1+0.2 不等于 0.3。解决用 BigDecimal 的 String 构造器避免 double 误差，除法指定 scale 与 RoundingMode.HALF_UP。生产建议金额用 long 分存储数据库用 DECIMAL |
| 缺点 | BigDecimal 性能低运算繁琐；舍入模式选择影响结果；分元互转易错 |

### 5. String、equals、== 的区别（字符串比较）

| 维度 | 内容 |
|------|------|
| 是什么 | 考查字符串 == 与 equals 的比较差异 |
| 能做什么 | 区分地址比较与内容比较；说明 String 重写 equals；解释常量池干扰 |
| 怎么用 | 字符串内容比较用 equals 不用 == |
| 原理和工作流程 | == 比较引用地址，字面量因常量池复用 == 为 true，new 出来的为 false。equals 是 String 重写的方法逐字符比较内容，无论字面量还是 new 内容相同即 true。字符串比较须用 equals，常量池复用与 intern 会让 == 偶然成立不可依赖 |
| 缺点 | == 误用于内容比较是高频 bug；常量池复用干扰判断；intern 后 == 行为变化 |

---

## 五、避坑指南

> 本节为辅助内容，无五维表格。汇总 String 循环拼接、new BigDecimal(double) 精度、BigDecimal 除法不指定舍入、SimpleDateFormat 线程不安全、asList 后 add/remove、== 比较字符串、Random 多线程、Math.round 负数、intern 滥用等错误的现象、原因与解决方案。

## 本章学习自检

> 本节为辅助内容，无五维表格。以复选清单形式罗列本章应掌握的能力点。

---

> [返回原文](./07-常用类与基础API.md) | [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
