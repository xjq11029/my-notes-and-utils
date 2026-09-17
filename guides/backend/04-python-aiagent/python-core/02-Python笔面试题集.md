# Python核心笔面试题集

聚焦 Python 语言本身：数据类型与可变性、作用域与闭包、函数与装饰器、面向对象与元类、迭代器与生成器、GIL 与并发、异常处理、内存管理与垃圾回收、上下文管理器、常用标准库，并贯穿与 Java 的对比视角

> 📖 **参考链接**：
> - [Python 官方文档（中文）](https://docs.python.org/zh-cn/3/) -- 语法、标准库、语言参考的权威来源
> - [Python 语言参考：数据模型](https://docs.python.org/zh-cn/3/reference/datamodel.html) -- 魔术方法、MRO、描述符协议的规范定义
> - [Python 标准库：functools](https://docs.python.org/zh-cn/3/library/functools.html) -- wraps、lru_cache、partial 等装饰器工具
> - [Python 标准库：copy](https://docs.python.org/zh-cn/3/library/copy.html) -- 浅拷贝与深拷贝的官方说明
> - [Python 标准库：gc](https://docs.python.org/zh-cn/3/library/gc.html) -- 垃圾回收器接口与分代回收参数
> - [Python 标准库：weakref](https://docs.python.org/zh-cn/3/library/weakref.html) -- 弱引用与循环引用处理
> - [Python 标准库：contextlib](https://docs.python.org/zh-cn/3/library/contextlib.html) -- 上下文管理器工具
> - [Python 标准库：asyncio](https://docs.python.org/zh-cn/3/library/asyncio.html) -- 协程与事件循环
> - [Python 术语表：GIL](https://docs.python.org/zh-cn/3/glossary.html#term-GIL) -- 全局解释器锁的官方定义
> - [Python HOWTO：函数式编程](https://docs.python.org/zh-cn/3/howto/functional-programming.html) -- 迭代器、生成器、闭包与装饰器

---

## 目录

- [一、选择题（18道）](#一选择题18道)
- [二、简答题（11道）](#二简答题11道)
- [三、场景设计题（3道）](#三场景设计题3道)
- [学习导航栏](#-学习导航栏)

---

## 一、选择题（18道）

### 1. 作用域与 LEGB ★
**题目：** 关于 Python 的名字解析顺序（LEGB），以下说法正确的是：
A. Local → Global → Enclosing → Built-in  
B. Local → Enclosing → Global → Built-in  
C. Built-in → Global → Enclosing → Local  
D. Global → Local → Enclosing → Built-in

**答案：B**

**解析：** LEGB 依次为 Local（当前函数局部）→ Enclosing（外层嵌套函数）→ Global（模块全局）→ Built-in（内置命名空间），自内向外查找、命中即停。Enclosing 排在 Global 之前，正是闭包能"看到"外层函数变量的原因。

---

### 2. global 与 nonlocal ★★
**题目：** 以下代码的输出是什么？
```python
count = 0

def outer():
    count = 10
    def inner():
        nonlocal count
        count += 1
        return count
    return inner()

print(outer(), count)
```
A. `11 11`  
B. `11 0`  
C. `10 0`  
D. 抛出 `UnboundLocalError`

**答案：B**

**解析：** `nonlocal` 声明 `inner` 中的 `count` 指向**外层函数** `outer` 的局部变量，故 `outer` 内部的 `count` 变为 11 并返回；模块级全局 `count` 从未被触碰，仍是 0。若换成 `global`，则输出 `1 1`——这正是两者的核心区别：`nonlocal` 绑定外层函数作用域，`global` 绑定模块作用域。

---

### 3. *args 与 **kwargs ★
**题目：** 关于 `*args` 和 `**kwargs`，以下说法错误的是：
A. `*args` 在函数内部是一个 tuple  
B. `**kwargs` 在函数内部是一个 dict  
C. 调用时 `f(*lst, **d)` 会把序列和字典解包为独立参数  
D. `*args` 必须写在 `**kwargs` 之后

**答案：D**

**解析：** 形参顺序必须为「普通参数 → 默认参数 → `*args` → 仅关键字参数 → `**kwargs`」，即 `*args` 在前。`*args` 收集多余位置参数为 tuple，`**kwargs` 收集多余关键字参数为 dict；调用侧的 `*`/`**` 则是反向的"解包"操作。

---

### 4. 带参数的装饰器 ★★★
**题目：** 以下装饰器写法中，哪一个是正确的「带参数装饰器」结构？
A. `@decorator(arg)` 等价于 `func = decorator(func, arg)`  
B. `@decorator(arg)` 等价于 `func = decorator(arg)(func)`  
C. `@decorator(arg)` 等价于 `func = decorator(func)(arg)`  
D. 带参数装饰器无法实现

**答案：B**

**解析：** `@decorator(arg)` 先执行 `decorator(arg)`，它必须返回一个「接收函数、返回函数」的装饰器，再把原函数传进去。因此带参装饰器需要三层嵌套：最外层收参数、中间层收被装饰函数、最内层 `wrapper` 执行实际逻辑。标准库的 `functools.lru_cache(maxsize=128)` 就是这个模式。

---

### 5. functools.wraps 的作用 ★★
**题目：** 不写 `@functools.wraps(func)` 时，被装饰函数最容易丢失的是哪个属性？
A. `__name__` 与 `__doc__`  
B. `__class__`  
C. `__module__` 与 `__dict__`  
D. 所有属性都不会丢失

**答案：A**

**解析：** 装饰器返回的 `wrapper` 替换了原函数名，导致 `func.__name__` 变成 `"wrapper"`、`__doc__` 变成 wrapper 的文档串，进而影响日志、调试、文档生成和依赖函数签名的框架。`functools.wraps` 会复制原函数的 `__module__`/`__name__`/`__qualname__`/`__doc__`/`__dict__`，并写入 `__wrapped__` 指向原函数。

---

### 6. MRO 与 C3 算法 ★★★
**题目：** 对于 `class D(B, C)`、`class B(A)`、`class C(A)` 的菱形继承，`D.__mro__` 的顺序是：
A. `D, B, A, C, object`  
B. `D, B, C, A, object`  
C. `D, C, B, A, object`  
D. `D, A, B, C, object`

**答案：B**

**解析：** C3 线性化算法需满足三条约束：子类先于父类、按基类声明顺序（`B` 在 `C` 前）、保持各父类自身 MRO 的单调性。因此结果为 `D → B → C → A → object`，体现"深度优先 + 子类优先"的合并结果，保证 `super()` 在菱形继承中每个类只被调用一次。

---

### 7. __slots__ 的作用 ★★
**题目：** 关于 `__slots__`，以下说法错误的是：
A. 可以阻止动态添加未声明的实例属性  
B. 可以省去每个实例的 `__dict__`，减少内存占用  
C. 定义在父类时，子类若不定义 `__slots__` 仍会拥有 `__dict__`  
D. 使用后实例属性可以像 `__dict__` 一样被任意增删

**答案：D**

**解析：** `__slots__` 声明的属性名被编译为固定偏移量的描述符，实例不再拥有 `__dict__`，因此**无法**添加未声明的属性，同时内存显著下降（大量小对象可省 40%~50%）。子类若不声明自己的 `__slots__`，会重新获得 `__dict__`，父类优化失效。注意它与多继承、`@property` 同名字段组合时容易冲突。

---

### 8. 魔术方法 __call__ ★
**题目：** 一个类实例要能被当作函数直接调用（如 `obj()`），需要实现哪个魔术方法？
A. `__init__`  
B. `__call__`  
C. `__new__`  
D. `__invoke__`

**答案：B**

**解析：** `__call__` 使实例成为 callable，`obj()` 等价于 `type(obj).__call__(obj)`，判断可调用性用 `callable(obj)`。该机制让"带状态的函数"成为可能——装饰器类实现、依赖注入容器、偏函数包装都依赖它。`__init__` 负责初始化，`__new__` 负责创建，`__invoke__` 不存在（那是 Java 反射的 `Method.invoke`）。

---

### 9. property 与描述符 ★★
**题目：** 关于 `@property`，以下说法正确的是：
A. 只能定义只读属性，无法定义 setter  
B. 访问 `obj.age` 时触发的是 `property` 对象的 `__get__` 方法  
C. `@age.setter` 装饰的函数必须命名为 `set_age`  
D. `@property` 会真正阻止外部访问下划线私有变量

**答案：B**

**解析：** `property` 本质是实现了 `__get__`/`__set__`/`__delete__` 的**数据描述符**，属性访问触发 `__get__`，赋值触发 `__set__`（即 `@x.setter`）。`@age.setter` 要求函数名与被装饰的 property 同名（`age`），否则会创建新属性。它不提供真正的访问控制，`obj._age` 依然可直接读写。

---

### 10. 元类 metaclass ★★★
**题目：** 关于元类（metaclass），以下说法正确的是：
A. 元类是类的实例，`type` 不是元类  
B. 类本身是元类的实例，默认元类是 `type`  
C. 元类只能用于创建抽象基类  
D. 元类在类实例化时才被调用

**答案：B**

**解析：** Python 中"类"也是对象，它的类型就是元类，默认是 `type`。类定义体执行时，解释器先收集命名空间，再调用 `metaclass(name, bases, namespace)` 创建类对象，因此元类在**类定义时**就生效（而非实例化时）。典型用途：注册子类（插件系统）、自动注入属性、ORM 字段收集、强制编码规范。

---

### 11. 可迭代对象与迭代器 ★★
**题目：** 关于「可迭代对象」和「迭代器」，以下说法错误的是：
A. 实现了 `__iter__` 的对象是可迭代对象  
B. 同时实现 `__iter__` 和 `__next__` 的对象是迭代器  
C. 迭代器一定是可迭代对象，可迭代对象一定是迭代器  
D. `for` 循环先调用 `iter()` 获取迭代器，再反复调用 `next()`

**答案：C**

**解析：** 迭代器一定可迭代（其 `__iter__` 返回自身），但可迭代对象不一定是迭代器——`list`、`dict`、`str` 实现了 `__iter__` 却没有 `__next__`，是"可重复迭代"的容器。`for` 循环流程为 `it = iter(obj)` 后不断 `next(it)` 直到 `StopIteration`；用 `iter(obj) is obj` 可判断对象本身是否为迭代器。

---

### 12. yield from ★★★
**题目：** `yield from iterable` 相比 `for item in iterable: yield item`，额外的能力是：
A. 仅仅是语法糖，功能完全相同  
B. 能自动透传 `send()` 的值和 `throw()` 的异常到子生成器  
C. 能自动把生成器转为列表  
D. 能让生成器支持随机访问

**答案：B**

**解析：** `yield from` 建立了调用方与子生成器之间的**双向通道**：`send()` 的值直接传入子生成器、`throw()` 的异常直接抛入子生成器，并自动处理 `StopIteration` 的返回值（成为 `yield from` 表达式的值）。这使生成器可以像协程一样递归组合，`asyncio` 早期的 `@coroutine` 就依赖该语义。

---

### 13. 生成器表达式与内存 ★★
**题目：** 处理 10GB 日志并统计包含 "ERROR" 的行数，内存占用最低的写法是：
A. `lines = f.readlines(); len([l for l in lines if "ERROR" in l])`  
B. `sum(1 for line in f if "ERROR" in line)`  
C. `len([l for l in f if "ERROR" in l])`  
D. `len(list(filter(lambda l: "ERROR" in l, f)))`

**答案：B**

**解析：** 生成器表达式按需产生元素，配合 `sum()` 只维持 O(1) 额外内存；`readlines()` 与列表推导式（C、D）都会把 10GB 内容一次性载入内存导致 OOM。这是"惰性求值"在工程上最典型的收益场景。

---

### 14. GIL 与并发选型 ★★★
**题目：** 需要同时发起 500 个 HTTP 请求并汇总结果，最合适的并发方案是：
A. 多线程（threading）创建 500 个线程  
B. 多进程（multiprocessing）创建 500 个进程  
C. asyncio 协程 + 信号量控制并发度  
D. 单线程顺序请求

**答案：C**

**解析：** 这是典型的高并发 I/O 密集场景。asyncio 在单线程内用事件循环调度数千协程，切换开销远小于线程，配合 `asyncio.Semaphore` 可精确控制并发度；多线程虽在 IO 时释放 GIL 也有效，但 500 个线程的创建与切换成本高；多进程适合 CPU 密集；顺序请求延迟叠加不可接受。

---

### 15. try/except/else/finally ★★
**题目：** 关于 `try/except/else/finally`，以下说法正确的是：
A. `else` 子句在 `try` 块中发生异常时执行  
B. `finally` 子句只有在 `try` 块无异常时才执行  
C. `else` 子句在 `try` 块正常结束后、`finally` 之前执行  
D. `finally` 中写 `return` 不会覆盖 `try` 中的 `return`

**答案：C**

**解析：** 执行顺序为：`try` 正常结束 → `else` → `finally`；若 `try` 抛异常并被捕获，则跳过 `else` 直接执行 `finally`。`finally` **无论是否异常都会执行**（除非进程被杀）。重要陷阱：`finally` 中的 `return`/`break` 会覆盖 `try` 的返回值，也会吞掉正在传播的异常，因此 `finally` 里不应写 `return`。

---

### 16. 异常链 raise from ★★★
**题目：** `raise NewError("...") from e` 中的 `from e` 作用是什么？
A. 把 `e` 当作参数传给 `NewError` 构造函数  
B. 设置新异常的 `__cause__`，保留原始异常链路  
C. 忽略原始异常 `e`  
D. 等价于 `raise NewError(...)`，无任何区别

**答案：B**

**解析：** `raise X from e` 显式设置 `X.__cause__ = e`，Traceback 会显示"direct cause"，实现异常链的**显式链**；`except` 块中隐式抛出新异常时原异常记入 `__context__`（隐式链）；`from None` 用于主动切断上下文、隐藏底层细节。工程上用 `raise ServiceError(...) from e` 可对外统一异常类型又不丢失根因。

---

### 17. 上下文管理器 ★★
**题目：** 关于自定义上下文管理器，以下说法错误的是：
A. 需实现 `__enter__` 和 `__exit__`  
B. `__exit__` 返回 `True` 时，块内异常会被吞掉不再向外传播  
C. `__exit__` 接收 `(exc_type, exc_val, exc_tb)` 三个参数  
D. `with` 语句块内无论是否异常，`__exit__` 都不会被调用

**答案：D**

**解析：** `with` 语句保证 `__exit__` **必然被调用**，这正是它相对 `try/finally` 的核心价值。`__exit__` 的参数在无异常时为 `(None, None, None)`；返回真值表示异常已处理、不再向外抛出，返回 `None`/`False` 则继续传播。`contextlib.contextmanager` 用生成器 + 一次 `yield` 即可实现同等效果。

---

### 18. 引用计数与弱引用 ★★★
**题目：** 以下哪种情况会导致对象无法仅靠引用计数被回收？
A. 对象被全局变量引用  
B. 两个对象互相引用形成环，且无外部引用  
C. 对象被局部变量引用  
D. 对象被容器持有引用

**答案：B**

**解析：** CPython 的主回收机制是引用计数，计数归零即刻释放；但循环引用（`a.b = b; b.a = a`）让双方计数始终为 1，无法归零。为此 CPython 额外提供**标记-清除**与**分代回收**（`gc` 模块，默认阈值 `(700, 10, 10)`）周期性检测并回收循环垃圾。可用 `weakref` 弱引用打破环——弱引用不增加引用计数，对象销毁后访问其 `()` 返回 `None`（注意 `list`/`dict`/`str` 等内置类型不支持弱引用）。

---

## 二、简答题（11道）

### 1. 作用域与 LEGB ★
**题目：** 请解释 Python 的 LEGB 规则，并说明 `global` 与 `nonlocal` 的区别和适用场景。

**参考答案与解析：**

**LEGB 名字解析顺序：** L（当前函数局部）→ E（外层嵌套函数）→ G（当前模块全局）→ B（内置命名空间），自内向外、命中即停。函数内部**赋值**的变量默认视为局部变量，这正是"函数内给全局变量赋值却不加 `global` 会报 `UnboundLocalError`"的根源。

| 关键字 | 绑定目标 | 使用场景 |
|--------|---------|---------|
| `global` | 模块级全局命名空间 | 修改模块级计数器、配置、单例状态 |
| `nonlocal` | 最近的外层函数命名空间 | 闭包中修改被捕获的外层局部变量 |

**实践建议：** 优先用可变容器或类属性承载共享状态，避免大量 `global`；`nonlocal` 是实现带状态闭包（计数器、累加器）的标准手段，例如 `make_counter` 中用 `nonlocal n` 让 `inc()` 累加外层变量。

> **生活化类比：作用域=找东西的抽屉** —— 先翻自己背包（Local），再问同行同伴（Enclosing），再去家里储物间（Global），最后去小区公共仓库（Built-in），找到就停手。而 `global`/`nonlocal` 是"我不找了，我要**往那个抽屉里放东西**"的声明——Python 默认认为函数里赋值的名字都是自己背包里的新东西，不声明就当它与外面同名物品毫无关系。

---

### 2. 装饰器原理与工程用法 ★★★
**题目：** 说明 Python 装饰器的原理，写出一个带参数、能记录耗时的装饰器，并解释为什么必须用 `functools.wraps`。

**参考答案与解析：**

**原理：** 装饰器本质是"接收函数（或类）作为参数、返回新 callable 的高阶函数"。`@deco` 等价于 `func = deco(func)`，在**函数定义时**立即执行一次。因为 Python 函数是一等对象（可赋值、可传参、可返回），闭包能捕获被装饰函数，所以能在不改动原函数代码的前提下增强行为。

```python
import functools, time

def timer(repeat: int = 1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = 0.0
            for _ in range(repeat):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                elapsed += time.perf_counter() - start
            print(f"[timer] {func.__name__} 平均耗时 {elapsed / repeat:.6f}s")
            return result
        return wrapper
    return decorator

@timer(repeat=3)
def slow_task(n: int) -> int:
    return sum(i * i for i in range(n))
```

`@timer(repeat=3)` 展开为 `slow_task = timer(repeat=3)(slow_task)`：先执行 `timer(3)` 得到 `decorator`，再执行 `decorator(slow_task)` 得到 `wrapper`。

**为什么必须用 `functools.wraps`：** 不加时 `slow_task.__name__` 变成 `"wrapper"`、`__doc__` 丢失、`inspect.signature()` 拿到 `(*args, **kwargs)`，会破坏日志、调试、文档生成以及 `FastAPI`/`Flask` 等依赖函数签名与元信息的框架（路由注册、依赖注入会失效）。`wraps` 复制元信息并写入 `__wrapped__`，使 `inspect.unwrap()` 可还原原函数。

> **生活化类比：装饰器=给手机套壳** —— 手机（原函数）没变，套上壳（wrapper）后多了防摔、支架功能，操作方式仍是原来的。带参数的装饰器像"先选好壳的颜色材质（`timer(repeat=3)`），再套到手机上"——多了一层配置步骤。`functools.wraps` 是"贴一张和原手机一模一样的标签"，否则别人看到的是"保护壳牌手机"，查型号、看说明书全对不上。

---

### 3. MRO 与 C3 算法 ★★★
**题目：** 什么是 MRO？请解释 C3 线性化算法的规则，并说明 `super()` 在菱形继承中为什么能避免重复调用。

**参考答案与解析：**

**MRO（Method Resolution Order）** 是 Python 解析属性/方法时沿类继承链查找的顺序，存储于 `__mro__` 元组，Python 3 采用 **C3 线性化算法**计算，替代了 Python 2 的深度优先搜索。

**C3 的三条约束：** ①子类优先于父类；②按基类声明顺序；③保持各父类自身 MRO 的单调性。合并公式为 `L[C(B1..Bn)] = C + merge(L[B1], ..., L[Bn], [B1..Bn])`，`merge` 反复取"各列表头中不出现在其他列表尾部的元素"；无法满足时抛 `TypeError: Cannot create a consistent MRO`。

以 `class A` → `class B(A)`、`class C(A)` → `class D(B, C)` 的菱形继承为例，`D.__mro__` 为 `D → B → C → A → object`：在 `D` 实例上调用 `D().hello()`，`B.hello` 里的 `super().hello()` 会打印 B 并转到 MRO 中的下一个 `C`，`C` 再转到 `A`，因此输出顺序是 `B → C → A`，共享基类 `A` **只被调用一次**。

**`super()` 的关键点：** `super()` 不是"父类代理"，而是"MRO 中**下一个类**的代理"。它按 `__mro__` 顺序而非"直属父类"解析，因此菱形结构中共享基类不会重复初始化。这也是 Mixin 模式能正确协作的基础。

> **生活化类比：MRO=公司里的汇报链** —— 找谁签字（调用方法），公司有明确的"上报顺序表"（`__mro__`）。C3 保证这个顺序表既满足"先找直接主管再找上级"，又不会因为两位主管共用一个总监而让总监被重复打扰。`super()` 就是"交给顺序表里的下一位"，而不是"交给我的直属上司"。

---

### 4. __slots__ 的作用与限制 ★★
**题目：** `__slots__` 解决什么问题？使用它有哪些注意事项？

**参考答案与解析：**

**解决的问题：** 默认每个实例都持有 `__dict__`（字典）用于动态存放属性。创建数百万个"数据小对象"时，每个 `__dict__` 的哈希表开销（约 100+ 字节起步）会成为内存瓶颈。`__slots__` 把允许的属性名声明为类级描述符，实例用固定偏移的槽位存储，**省掉 `__dict__`**，大量小对象场景可节省 40%~50% 内存，属性访问速度也略有提升。声明 `__slots__ = ("x", "y")` 后，`p.x = 10` 正常，但 `p.z = 3` 会抛 `AttributeError`。

**注意事项：**
1. **无法动态添加属性**，丧失灵活性，不适合需要运行时挂载属性的对象（ORM 实例、动态配置对象）；
2. **子类若不定义 `__slots__`** 会重新获得 `__dict__`，父类优化失效；子类应同样声明；
3. **不支持弱引用**，除非在 `__slots__` 中显式加入 `"__weakref__"`；
4. **与多继承冲突**：多个父类若都定义了非空 `__slots__`，实例布局可能冲突导致 `TypeError`；与 `@property` 同名时属性被描述符占用，赋值可能失败；
5. **不适合依赖 `__dict__` 的框架**：`dataclasses`、`pydantic` 在特定模式下会依赖它。

> 📖 **参考链接**：
> - [Python 语言参考：__slots__](https://docs.python.org/zh-cn/3/reference/datamodel.html#slots) -- 官方对槽位机制与限制的说明

---

### 5. 元类与类创建流程 ★★★
**题目：** 请描述 Python 中类的创建流程，说明元类的作用，并举一个实际应用场景。

**参考答案与解析：**

**类创建流程（`class` 语句执行时）：** ①解释器执行类体代码，收集所有定义到命名空间字典 `namespace`；②确定元类（`metaclass` 关键字参数，否则取所有基类元类中最派生的那个，默认 `type`）；③调用 `metaclass(name, bases, namespace)`，元类的 `__new__`/`__init__` 依次执行并返回类对象；④类对象绑定到类名。`type(name, bases, dict)` 的三参数形式可动态创建类，说明"类就是元类的实例"——`type(MyClass) is type` 为 True。

**元类的作用：** 在类**创建时**拦截并修改类的定义——注入属性/方法、收集字段元数据、注册子类、校验编码规范。相比类装饰器，元类会沿继承链自动生效于所有子类。

**实际场景：轻量 ORM 的字段收集与表名注册。** 在 `ModelMeta.__new__` 中遍历 `namespace`，把所有 `Field` 实例收进 `cls._fields`，按类名推导 `cls._table = name.lower() + "s"`，再写入全局 `REGISTRY[cls._table] = cls`。这样定义 `class User(Model)` 时表名与字段就自动注册完毕（完整可运行代码见本文档场景设计题 2）。

**更轻量的替代方案：** 若只需"子类定义时钩子"，用 `__init_subclass__`（Python 3.6+）即可；若只需包装单个类，用类装饰器。元类应作为最后手段，因为它侵入性强、与多继承/`__slots__` 组合复杂、错误难调试。

> **生活化类比：元类=制造类的工厂** —— 普通类像"饼干模具"，用来生产饼干（实例）；元类则是"生产饼干模具的工厂"。你在设计模具（写 `class`）时，工厂可以顺手在模具上刻编号、登记入库（注入属性、注册子类）。一旦换了工厂（元类），所有用它造的模具都自动带上这些特征——这就是元类会沿继承链生效的原因。

---

### 6. 迭代器与生成器 ★★
**题目：** 说明迭代器协议、生成器函数与生成器表达式的区别，并解释 `yield` 的执行流程。

**参考答案与解析：**

**迭代器协议：** 对象实现 `__iter__`（返回迭代器）与 `__next__`（返回下一个值，耗尽时抛 `StopIteration`）即为迭代器。`for` 循环内部先 `iter()` 再反复 `next()`，捕获 `StopIteration` 结束循环。

**生成器函数：** 函数体内含 `yield`，调用时**不执行函数体**，而是返回一个生成器对象（本身即迭代器）。每次 `next()` 执行到下一个 `yield` 处暂停，**保留局部变量与指令指针**；`yield` 表达式的值由 `send()` 传入（默认 `None`）；函数返回时抛 `StopIteration(value)`。例如 `g = countdown(3)` 后 `next(g)` 打印"开始"并返回 3，`g.send("a")` 会打印"收到: a"并推进到下一个 `yield` 返回 2。

| 特性 | 迭代器（自定义类） | 生成器函数 | 生成器表达式 |
|------|------------------|-----------|-------------|
| 实现方式 | 手写 `__iter__`/`__next__` | 含 `yield` 的函数 | 圆括号推导式 |
| 状态管理 | 手动维护（如索引） | 解释器自动保存栈帧 | 解释器自动 |
| 适用场景 | 复杂状态机、需额外方法 | 多步逻辑、可读性优先 | 单表达式惰性变换 |
| 内存 | 惰性 | 惰性 | 惰性 |

**关键限制：** 生成器只能被消费一次，耗尽后再遍历无输出（需重复遍历时转 `list` 或用 `itertools.tee`）；不可随机访问、无 `len()`；`yield from` 可把子生成器的值、`send`、`throw` 全部透传，用于递归组合。

> 📖 **参考链接**：
> - [Python 语言参考：生成器表达式](https://docs.python.org/zh-cn/3/reference/expressions.html#generator-expressions) -- yield、yield from 的语义定义

---

### 7. GIL 与并发选型 ★★★
**题目：** 什么是 GIL？它带来什么影响？请对比多线程、多进程、asyncio 三种并发方式的适用场景。

**参考答案与解析：**

**GIL（Global Interpreter Lock，全局解释器锁）** 是 CPython 中的一把互斥锁，保证同一时刻**只有一个线程执行 Python 字节码**。它存在的原因是 CPython 的引用计数与内存管理不是线程安全的，用一把全局锁换取实现简单与单线程性能。

**影响：** CPU 密集型任务用多线程无法利用多核，反因切换开销变慢；I/O 密集型任务影响不大（执行 I/O 时主动释放 GIL）；多进程各自拥有独立解释器与 GIL，可真正并行；此外 `numpy`/`hashlib` 等 C 扩展在计算时会释放 GIL，多线程仍有加速。

| 维度 | threading | multiprocessing | asyncio |
|------|-----------|-----------------|---------|
| 并发模型 | 抢占式多线程（OS 调度） | 多进程（独立内存） | 协作式单线程事件循环 |
| 受 GIL 影响 | 是（CPU 密集无效） | 否（真并行） | 是（但本身是单线程） |
| 适用场景 | I/O 密集 + 需兼容阻塞库 | CPU 密集计算、批量数据处理 | 海量 I/O 并发（爬虫、网关） |
| 数据共享 | 共享内存（需加锁） | 需序列化（Queue/Pipe） | 单线程内共享，无需锁 |
| 开销 | 线程栈 + 切换 | 进程创建 + 序列化，较重 | 协程极轻，可数万级 |
| 典型限制 | 竞态条件、死锁 | 内存翻倍、启动慢 | 需全链路异步，阻塞调用会卡死循环 |

**选型口诀：** CPU 密集 → 多进程；I/O 密集且能改造成异步 → asyncio；I/O 密集但依赖阻塞库 → 多线程；混合型 → 多进程 + 进程内多线程/协程。

**线程安全：** 由于 GIL，单个字节码操作是原子的，但"读-改-写"这类复合操作仍会竞态（如 `counter += 1` 对应多条字节码），必须用 `threading.Lock`、`queue.Queue` 或 `concurrent.futures` 保证安全。

> **生活化类比：GIL=只有一支笔的会议室** —— 会议室（进程）里有很多人（线程），但只有一支笔（GIL），谁拿到笔谁才能写白板（执行字节码）。若大家写的是"要查资料再写"（CPU 计算），抢笔反而拖慢进度，不如开几间会议室各配一支笔（多进程）；若写的是"写一句就去打电话等回复"（I/O），拿笔时间短、等电话时主动交笔，多人协作仍高效。asyncio 则是"一个人用待办清单轮流处理"，谁都不用抢笔，但一旦有人卡住不放手（阻塞调用），整个清单就停摆。

> 📖 **参考链接**：
> - [Python 术语表：GIL](https://docs.python.org/zh-cn/3/glossary.html#term-GIL) -- 官方对全局解释器锁的定义
> - [Python 标准库：asyncio](https://docs.python.org/zh-cn/3/library/asyncio.html) -- 协程与事件循环官方指南

---

### 8. 异常处理与异常链 ★★
**题目：** 说明 `try/except/else/finally` 的执行顺序，什么是异常链？如何自定义异常？

**参考答案与解析：**

**执行顺序：** ①执行 `try` 块；②无异常 → 执行 `else` 块（放置"只有成功后才做"的逻辑，避免误捕获）；③有异常 → 按 `except` 子句自上而下匹配，命中第一个兼容类型（应"由具体到宽泛"）；④无论何种情况，**最后都执行 `finally`**。

**陷阱：** `finally` 中的 `return`/`break`/`continue` 会覆盖 `try` 的返回值并吞掉异常；`except Exception` 会连带捕获 `KeyError`/`TypeError` 等编程错误，掩盖真实 bug；裸 `except:` 连 `KeyboardInterrupt`、`SystemExit` 都吞掉，禁止使用；`except` 块只 `pass` 或只打日志不重抛，是典型的"异常吞没"。

**异常链：** 显式链 `raise NewError(...) from e` 设置 `__cause__`，Traceback 显示"direct cause"；隐式链在 `except` 块中抛新异常时原异常自动记入 `__context__`；`from None` 切断上下文，常用于对外隐藏内部实现。

**自定义异常要点：** 继承 `Exception`（业务异常）而非 `BaseException`（后者是 `KeyboardInterrupt`/`SystemExit` 的基类），并建立层次化体系便于统一捕获。例如定义 `AppError(Exception)` 作为基类、携带 `code` 字段；`ValidationError(AppError)` 覆写为 400；底层 `ValueError` 用 `raise ValidationError(...) from e` 包装，既对外统一异常类型又不丢失根因。

> 📖 **参考链接**：
> - [Python 教程：错误与异常](https://docs.python.org/zh-cn/3/tutorial/errors.html) -- try/except/else/finally 与异常链的官方说明

---

### 9. 内存管理与垃圾回收 ★★★
**题目：** 说明 CPython 的内存管理机制，包括引用计数、循环引用问题，以及 `gc` 模块和弱引用的作用。

**参考答案与解析：**

**主机制：引用计数（Reference Counting）** —— 每个 PyObject 维护 `ob_refcnt`，被引用 +1、引用消失 -1，归零则立即释放。**优点**：实时回收、无长时间停顿、确定性析构；**缺点**：维护计数有开销，且**无法处理循环引用**。

**循环引用问题：** `a.b = b; b.a = a` 且无外部引用时，双方计数都停留在 1，永不归零造成内存泄漏。常见来源：父子对象互持、观察者与被观察者互引、异常 traceback 持有栈帧、缓存持有大对象。

**补充机制：标记-清除 + 分代回收（`gc` 模块）** —— 标记-清除从根对象出发遍历可达对象，不可达的循环垃圾被回收；分代回收把对象分为 0/1/2 三代，新对象在第 0 代，存活越久越"老"、回收频率越低（默认阈值 `(700, 10, 10)`）。常用 API：`gc.collect()`、`gc.get_objects()`、`gc.garbage`、`gc.set_debug(gc.DEBUG_LEAK)`、`gc.disable()`。

**弱引用（`weakref`）：** 不增加引用计数，是打破循环的标准手段——`child.parent = weakref.ref(parent)` 后访问需写成 `child.parent().name`，`parent` 被回收后该弱引用返回 `None`。典型用途：缓存（避免缓存项阻止对象释放）、观察者模式、`WeakValueDictionary`。注意 `list`/`dict`/`str`/`int` 等内置类型不支持弱引用（除非子类化）。

**其他要点：** `__del__` 在循环引用场景下行为不确定，不应依赖它做资源清理，应使用 `with`；`pymalloc` 内存池减少系统调用；排查工具可用 `tracemalloc`、`objgraph`、`memory_profiler`。

> **生活化类比：内存管理=图书馆还书** —— 引用计数像每本书身上贴一张"借阅计数卡"，归零说明没人看，管理员立刻收走（实时回收）。但两个人互相拿着对方的书说"你先还我再还"（循环引用），卡片永远不为零，书就卡在桌上收不走，于是图书馆定期"盘点"（标记-清除 + 分代回收），从在馆读者出发检查哪些书其实没人能真正拿到，一并收走。弱引用则是"登记一个借书人姓名但不占用借阅额度"——那人走了，这条登记自然作废。

---

### 10. 上下文管理器与 contextlib ★★
**题目：** 什么是上下文管理器？说明 `with` 语句的执行流程，并给出两种自定义实现方式。

**参考答案与解析：**

**上下文管理器**是实现了 `__enter__` 和 `__exit__` 协议的对象，用于"进入/退出"时成对执行资源管理逻辑。`with` 执行流程：①调用 `__enter__()`，返回值绑定到 `as` 后的变量；②执行 `with` 块；③**无论是否异常**都调用 `__exit__(exc_type, exc_val, exc_tb)`；④无异常时收到 `(None, None, None)`，有异常时收到异常三元组；⑤`__exit__` 返回真值 → 异常被吞掉，返回假值/`None` → 异常继续向外抛。

```python
import time, contextlib

class Timer:                          # 方式一：类实现 __enter__ / __exit__
    def __init__(self, label: str):
        self.label = label
    def __enter__(self):
        self.start = time.perf_counter()
        return self                   # as 拿到的对象
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[{self.label}] 耗时 {time.perf_counter() - self.start:.6f}s")
        return False                  # 不吞异常

@contextlib.contextmanager            # 方式二：生成器写法
def open_db(dsn: str):
    conn = connect(dsn)               # yield 之前 = __enter__
    try:
        yield conn                    # 把资源交给 with 块
    finally:
        conn.close()                  # yield 之后 = __exit__（保证执行）
```

`contextmanager` 把"一次 `yield`"的生成器包装成上下文管理器：`yield` 前的代码在 `__enter__` 中运行，`yield` 的值即 `as` 变量，`yield` 之后的代码在 `__exit__` 中运行。**必须用 `try/finally` 包住 `yield`**，否则块内异常会导致清理代码被跳过；若要在块内异常时吞掉它，需在生成器内 `try/except` 并 `return True`。

**`contextlib` 其他工具：** `suppress(FileNotFoundError)` 等价于忽略指定异常的 `try/except`；`ExitStack` 动态管理数量不定的资源；`nullcontext()` 作为占位，便于条件化地决定是否使用资源管理。

> **生活化类比：with=借书登记流程** —— 借书（`__enter__`）时登记并拿到书（`as` 变量）；看书期间无论你是正常看完还是撕坏书跑掉（抛异常），离馆时都必须走还书流程（`__exit__`）。如果你跟管理员说"这页撕坏了我赔"（`__exit__` 返回 True），事情就此了结；否则损坏记录会继续往上报。

> 📖 **参考链接**：
> - [Python 语言参考：with 语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-with-statement) -- with 语句与上下文管理协议
> - [Python 标准库：contextlib](https://docs.python.org/zh-cn/3/library/contextlib.html) -- contextmanager、ExitStack、suppress

---

### 11. 装饰器 vs Java 注解、鸭子类型、生成器 vs Stream ★★★
**题目：** 有 Java 基础的同学常把 Python 装饰器类比 Java 注解。请说明二者本质区别，并对比 Python 鸭子类型 vs Java 接口、Python 生成器 vs Java Stream。

**参考答案与解析：**

**① 装饰器 vs Java 注解：本质区别是"运行时的行为增强" vs "编译期/运行期的元数据标记"。**

| 维度 | Python 装饰器 | Java 注解 |
|------|--------------|-----------|
| 本质 | 高阶函数/类，接收 callable 返回 callable | 元数据接口，本身不执行逻辑 |
| 生效时机 | **定义时**立即执行，函数对象被替换 | 需反射（`getAnnotation`）或编译期处理器（APT）读取 |
| 是否改变行为 | **直接改变**（包装、替换、拦截） | 本身不改变，行为由读取注解的框架实现 |
| 能否改签名 | 可以（wrapper 签名可不同） | 不能，注解不改变方法本身 |
| 典型用法 | `@lru_cache`、`@property`、`@dataclass`、框架路由 | `@Override`、`@Autowired`、`@Transactional` |

二者语法上都以 `@` 开头、都写在定义之上，故易混淆。Java 的 `@Transactional` 靠 Spring AOP 生成代理来改变行为，看起来像"注解带来了事务"；而 Python 的 `@decorator` 是**自己**就完成了包装，不需要额外框架参与。对应关系参考：`@property` ≈ getter/setter；`@dataclass` ≈ Lombok `@Data`；`@lru_cache` 在 Java 中通常需 Guava `Cache` 或手写。

**② 鸭子类型 vs Java 接口：** "如果它走起来像鸭子、叫起来像鸭子，那它就是鸭子"——Python 不检查对象**是什么类型**，只检查它**支持什么操作**。`sum(len(x) for x in items)` 无需关心 `x` 是 `list`、`str` 还是 `dict`，只要有 `__len__` 即可。

| 维度 | Python 鸭子类型 | Java 接口 |
|------|----------------|-----------|
| 绑定时机 | 运行时按方法存在性判断 | 编译期按 `implements` 声明检查 |
| 是否需显式声明 | 不需要 | 必须 `implements`/继承 |
| 灵活性 | 高，可适配任何满足协议的对象 | 低，受类型体系约束 |
| 安全性 | 运行时才暴露问题 | 编译期发现 |
| 补充手段 | `abc` 抽象基类、`typing.Protocol`（结构化类型）、类型注解 | 接口、泛型、抽象类 |

`typing.Protocol` 支持结构化子类型，可在 mypy 中静态校验，同时不强制运行时继承，是"给鸭子类型加保险"的折中方案。

**③ 生成器 vs Java Stream：共同点是"惰性、单次消费、函数式风格"，差异在能力边界。**

| 维度 | Python 生成器 | Java Stream |
|------|--------------|-------------|
| 惰性求值 | 是（`yield` 按需推进） | 是（中间操作惰性，终端操作触发） |
| 可复用 | **只能消费一次** | **只能消费一次** |
| 双向交互 | 支持 `send()`/`throw()`，可做协程 | 不支持 |
| 实现方式 | 语言级语法，保留栈帧 | 库级 API + 函数式接口 + Lambda |
| 并行 | 无内置（需多进程/协程） | `parallelStream()` 基于 ForkJoin |
| 典型操作 | `map`/`filter` 用生成器表达式或 `itertools` | `map`/`filter`/`reduce`/`collect` |

**关键差异：** Python 生成器是**语言级协程原语**（`yield` 可接收 `send` 的值），因此能承载状态机与异步逻辑（`asyncio` 的基础）；Java Stream 是**库级集合处理管道**，不具备双向通信能力。反过来 Java Stream 有内建并行能力，Python 生成器要靠 `multiprocessing` 或 `asyncio` 另行解决。

> 📖 **参考链接**：
> - [Python 标准库：typing.Protocol](https://docs.python.org/zh-cn/3/library/typing.html#typing.Protocol) -- 结构化子类型与静态鸭子类型

---

## 三、场景设计题（3道）

### 1. 大文件流式处理管道 ★★
**题目：** 有一个 20GB 的服务器访问日志文件，需要统计：每个 IP 的请求次数（Top 10）、5xx 响应占比、按小时分布的错误数。要求内存占用可控（不超过几百 MB），且能安全处理读取过程中的异常。请设计实现方案并写出核心代码。

**参考答案与解析：**

**设计思路：** ①**流式读取**——用生成器逐行读取，绝不 `readlines()`/`read()` 全量载入；②**管道式加工**——用生成器把"读取 → 解析 → 过滤"拆成多个环节，职责单一、可独立测试；③**单次遍历聚合**——所有统计在一次遍历中完成，用 `Counter`/`defaultdict` 承载状态；④**资源与异常管理**——用上下文管理器保证文件关闭，坏行计数跳过而不中断任务；⑤**Top-K 用 `heapq.nlargest`** 避免全量排序。

```python
import heapq, re
from collections import Counter, defaultdict
from contextlib import contextmanager

LOG_PATTERN = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+).*?"\S+ \S+ (?P<path>\S+)".*? (?P<status>\d{3}) '
)

@contextmanager
def open_log(path: str):
    """上下文管理器：保证文件关闭"""
    f = open(path, "r", encoding="utf-8", errors="replace")
    try:
        yield f
    finally:
        f.close()

def read_lines(fh):
    """生成器：逐行读取，内存 O(1)"""
    for line in fh:
        line = line.strip()
        if line:
            yield line

def parse_records(lines):
    """生成器：解析 + 过滤，坏行静默跳过"""
    for line in lines:
        m = LOG_PATTERN.search(line)
        if not m:
            continue
        yield {"ip": m.group("ip"), "status": int(m.group("status")),
               "hour": line[12:14] if len(line) > 14 else "??"}

def analyze(path: str, top_k: int = 10) -> dict:
    ip_counter, hourly_errors = Counter(), defaultdict(int)
    status_bucket = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}
    total = 0

    with open_log(path) as fh:
        for rec in parse_records(read_lines(fh)):   # 生成器链驱动，天然背压
            total += 1
            ip_counter[rec["ip"]] += 1
            bucket = f"{rec['status'] // 100}xx"
            if bucket in status_bucket:
                status_bucket[bucket] += 1
            if rec["status"] >= 500:
                hourly_errors[rec["hour"]] += 1

    error_total = status_bucket["5xx"]
    return {
        "total_requests": total,
        "top_ips": heapq.nlargest(top_k, ip_counter.items(), key=lambda x: x[1]),
        "5xx_ratio": round(error_total / total, 4) if total else 0.0,
        "status_bucket": status_bucket,
        "hourly_errors": dict(sorted(hourly_errors.items())),
    }

if __name__ == "__main__":
    stats = analyze("./access.log")
    print(f"总请求数: {stats['total_requests']:,} | 5xx 占比: {stats['5xx_ratio']:.2%}")
    print("Top10 IP:", stats["top_ips"], "| 按小时错误数:", stats["hourly_errors"])
```

**关键要点：** 整条管道只保留聚合状态，与文件大小无关，内存恒定；若需并行加速，可按文件分片后用 `multiprocessing.Pool` 分别统计再合并（各分片 `Counter` 可直接 `+`）；坏行用 `continue` 跳过并单独计数，避免一行脏数据导致 20GB 任务失败；`errors="replace"` 防止 `UnicodeDecodeError` 中断。

**涉及知识点：** 生成器与 `yield`、生成器管道组合、上下文管理器、`collections.Counter`/`defaultdict`、`heapq`、异常与编码容错。

---

### 2. 轻量 ORM 与重试框架 ★★★
**题目：** 请用装饰器与元类实现一个轻量级 ORM 雏形，要求：类定义时自动收集字段并注册表名；支持链式查询条件；查询方法带有"失败自动重试"能力，且重试次数可配置。请给出核心代码并说明各语法点的作用。

**参考答案与解析：**

**设计思路：** ①**元类 `ModelMeta`** 在类创建时收集 `Field` 实例、推导表名、注册到全局 `REGISTRY`；②**描述符 `Field`** 用 `__set_name__` 自动获取字段名，实现类型校验与默认值；③**带参装饰器 `retry`** 三层结构，`functools.wraps` 保留元信息；④**链式查询 `QuerySet`** 用 `__getattr__` 动态生成 `filter_xxx` 方法并返回自身；⑤**魔术方法** `__repr__` 便于调试、`__iter__` 让 QuerySet 可遍历。

```python
import functools, time
from typing import Any, Callable, Dict, List, Optional, Type

REGISTRY: Dict[str, Type["Model"]] = {}

class Field:
    """描述符：字段定义 + 类型校验 + 默认值"""
    def __init__(self, field_type: type = str, default: Any = None, primary_key: bool = False):
        self.field_type, self.default, self.primary_key = field_type, default, primary_key
        self.name: Optional[str] = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name                          # 类创建时自动拿到属性名

    def __get__(self, instance: Any, owner: type) -> Any:
        return self if instance is None else instance.__dict__.get(self.name, self.default)

    def __set__(self, instance: Any, value: Any) -> None:
        if value is not None and not isinstance(value, self.field_type):
            raise TypeError(f"{self.name} 期望 {self.field_type.__name__}")
        instance.__dict__[self.name] = value

def retry(times: int = 3, delay: float = 0.1, exceptions: tuple = (Exception,)) -> Callable:
    """带参数的装饰器：失败自动重试"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Optional[Exception] = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    print(f"[retry] {func.__name__} 第 {attempt}/{times} 次失败: {e}")
                    if attempt < times:
                        time.sleep(delay * attempt)          # 退避
            raise RuntimeError(f"{func.__name__} 重试 {times} 次后仍失败") from last_exc
        return wrapper
    return decorator

class QuerySet:
    """链式查询：filter_<field>=value 动态生成"""
    def __init__(self, model: Type["Model"]) -> None:
        self.model, self.conditions = model, {}

    def __getattr__(self, item: str) -> Callable:
        if item.startswith("filter_"):
            field = item[len("filter_"):]
            def _filter(value: Any) -> "QuerySet":
                self.conditions[field] = value
                return self                                # 返回自身实现链式调用
            return _filter
        raise AttributeError(item)

    def all(self) -> List["Model"]:
        rows = self.model._rows
        for k, v in self.conditions.items():
            rows = [r for r in rows if getattr(r, k) == v]
        return rows

    def __iter__(self):
        return iter(self.all())

class ModelMeta(type):
    """元类：类创建时收集字段并注册表"""
    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> type:
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "Model":
            cls._fields = {k: v for k, v in namespace.items() if isinstance(v, Field)}
            cls._table = name.lower() + "s"
            cls._rows: List[Any] = []
            REGISTRY[cls._table] = cls
        return cls

class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs: Any) -> None:
        for fname, field in self._fields.items():
            setattr(self, fname, kwargs.get(fname, field.default))

    @classmethod
    def objects(cls) -> QuerySet:
        return QuerySet(cls)

    @classmethod
    @retry(times=3, delay=0.05, exceptions=(ConnectionError,))
    def fetch_all(cls) -> List["Model"]:
        """模拟不稳定数据源：前两次抛 ConnectionError"""
        cls._attempt = getattr(cls, "_attempt", 0) + 1
        if cls._attempt < 3:
            raise ConnectionError("模拟数据库抖动")
        return cls._rows

    def __repr__(self) -> str:
        args = ", ".join(f"{k}={getattr(self, k)!r}" for k in self._fields)
        return f"{type(self).__name__}({args})"

class User(Model):
    id = Field(int, primary_key=True)
    name = Field(str, default="匿名")
    age = Field(int, default=0)

if __name__ == "__main__":
    User._rows.extend([User(id=1, name="Alice", age=30),
                       User(id=2, name="Bob", age=25),
                       User(id=3, name="Alice", age=41)])
    print("表名:", User._table, "| 字段:", list(User._fields), "| 注册表:", list(REGISTRY))
    print("链式查询:", User.objects().filter_name("Alice").filter_age(30).all())
    print("重试后取数:", len(User.fetch_all()))
```

**各语法点作用：**
- **元类**：`ModelMeta.__new__` 在 `class User(Model)` 执行时即完成字段收集与 `REGISTRY` 注册，子类自动继承该行为；
- **描述符**：`Field.__set_name__` 解决"字段不知道自己叫什么"的问题，`__set__` 提供类型校验；
- **带参装饰器**：`@retry(times=3, ...)` 展开为 `fetch_all = retry(times=3)(fetch_all)`，用 `functools.wraps` 保留元信息，用指数退避与 `raise ... from last_exc` 保留根因；
- **`__getattr__`**：只在常规属性查找失败时触发，因此可安全地动态生成 `filter_<字段>` 方法；
- **装饰器叠加顺序**：`@classmethod` 必须写在最外层，否则 `cls` 参数传递会出错——高频踩坑点。

**涉及知识点：** 元类与类创建流程、描述符协议、带参数装饰器、`functools.wraps`、`__getattr__` 动态属性、异常链、`classmethod`。

---

### 3. 异步并发限流抓取器 ★★
**题目：** 需要异步抓取 1000 个 URL，要求：并发度不超过 20、单个请求超时 5 秒、失败自动重试 2 次、整体统计成功/失败数与总耗时。请基于 `asyncio` 设计实现，并说明为什么该场景不用多线程。

**参考答案与解析：**

**设计思路：** ①`asyncio.Semaphore(20)` 控制并发度，超出则排队等待，避免打挂目标站点；②`asyncio.timeout`（或 `wait_for`）实现单请求超时；③**异步重试装饰器**——装饰的是协程函数，`wrapper` 必须是 `async def` 且 `await func(...)`；④`asyncio.gather(..., return_exceptions=True)` 汇总所有任务，异常不中断整体；⑤`dataclass` 承载统计结果，`Counter` 汇总错误类型。

```python
import asyncio, functools, time
from collections import Counter
from dataclasses import dataclass, field

@dataclass
class Stats:
    success: int = 0
    failed: int = 0
    errors: Counter = field(default_factory=Counter)

    def summary(self) -> str:
        return f"成功 {self.success} / 失败 {self.failed} | 错误分布: {dict(self.errors)}"

def async_retry(times: int = 2, delay: float = 0.2, exceptions: tuple = (Exception,)):
    """异步带参装饰器：重试协程函数"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last = None
            for attempt in range(1, times + 2):            # 首次 + times 次重试
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last = e
                    if attempt <= times:
                        await asyncio.sleep(delay * attempt)
            raise last
        return wrapper
    return decorator

@dataclass
class Fetcher:
    concurrency: int = 20
    timeout: float = 5.0

    def __post_init__(self) -> None:
        self.sem = asyncio.Semaphore(self.concurrency)
        self.stats = Stats()

    @async_retry(times=2, delay=0.2, exceptions=(TimeoutError, ConnectionError))
    async def _fetch_one(self, url: str) -> str:
        async with self.sem:                               # 限流
            async with asyncio.timeout(self.timeout):      # 单请求超时（3.11+）
                await asyncio.sleep(0.05)                  # 模拟网络 I/O
                if hash(url) % 7 == 0:
                    raise ConnectionError(f"连接失败: {url}")
                if hash(url) % 11 == 0:
                    raise TimeoutError(f"超时: {url}")
                return f"OK:{url}"

    async def run(self, urls):
        results = await asyncio.gather(
            *(self._fetch_one(u) for u in urls),
            return_exceptions=True,                        # 异常不中断 gather
        )
        for r in results:
            if isinstance(r, BaseException):
                self.stats.failed += 1
                self.stats.errors[type(r).__name__] += 1
            else:
                self.stats.success += 1
        return self.stats

async def main() -> None:
    urls = [f"https://example.com/api/{i}" for i in range(1000)]
    fetcher = Fetcher(concurrency=20, timeout=5.0)
    start = time.perf_counter()
    stats = await fetcher.run(urls)
    print(stats.summary())
    print(f"总耗时: {time.perf_counter() - start:.2f}s | 并发上限: {fetcher.concurrency}")

if __name__ == "__main__":
    asyncio.run(main())
```

**为什么不用多线程：** 该任务是**纯 I/O 密集**（网络等待为主），CPU 几乎空闲，多进程完全浪费；1000 个线程的创建、栈内存（每个约 8MB 虚拟内存）与 OS 调度切换成本远高于协程；协程在单线程事件循环内切换，开销约百纳秒级，可轻松支撑数千并发；`Semaphore` 天然表达"并发度上限"，比线程池 `max_workers` 更细粒度可控；多线程若依赖阻塞库还需处理 GIL 与锁，而 asyncio 单线程内共享状态无需加锁。

**关键要点：** `async with asyncio.timeout(...)` 是 Python 3.11+ 写法，低版本用 `asyncio.wait_for(coro, timeout)`；装饰协程函数时 `wrapper` 必须 `async def` 并 `await` 原函数，否则返回的是协程对象而非结果（高频踩坑）；`gather(return_exceptions=True)` 让单个失败不影响整体汇总；重试要配合**指数退避**与**抖动**，避免失败时对目标站点造成脉冲压力；生产环境还应加连接池复用（`aiohttp`/`httpx`）、DNS 缓存、`asyncio.Queue` 做生产者-消费者解耦。

**涉及知识点：** asyncio 事件循环与协程、`Semaphore` 限流、异步装饰器、`functools.wraps`、`dataclass`、`Counter` 统计、异常聚合、GIL 与并发选型。

---

## 学习导航栏

| 知识点 | 推荐学习路径 | 难度 |
|--------|-------------|------|
| 数据类型与可变性 | 掌握可变/不可变、深浅拷贝、可哈希与字典键约束 | ★ |
| 作用域与闭包 | 吃透 LEGB、`global`/`nonlocal`、闭包捕获与延迟绑定 | ★★ |
| 函数与装饰器 | 从高阶函数到带参装饰器、`functools.wraps`、类装饰器 | ★★★ |
| 面向对象进阶 | MRO 与 C3、`__slots__`、描述符与 `property`、元类 | ★★★ |
| 迭代器与生成器 | 迭代器协议、`yield`/`yield from`、惰性求值与管道组合 | ★★ |
| 并发与 GIL | 理解 GIL 成因与影响，按 CPU/IO 特征选择多进程/多线程/asyncio | ★★★ |
| 异常处理 | 执行顺序、异常链、自定义异常体系、避免异常吞没 | ★★ |
| 内存与垃圾回收 | 引用计数、循环引用、分代回收、弱引用与排查工具 | ★★★ |
| 上下文管理器 | `__enter__`/`__exit__`、`contextlib` 全家桶 | ★★ |
| 标准库惯用法 | `collections`、`itertools`、`typing`、`dataclasses` | ★★ |
| Java 对比视角 | 装饰器 vs 注解、GIL vs JVM 线程模型、鸭子类型 vs 接口、生成器 vs Stream | ★★ |

**推荐学习顺序：** 数据类型与作用域打底 → 函数与装饰器 → 面向对象进阶（MRO/元类） → 迭代器与生成器 → 异常与上下文管理器 → 并发与 GIL 选型 → 内存管理与性能排查 → 用 Java 视角做横向对照

> 配套资料：[Python核心语法速通](./01-Python核心语法速通.md) | [Python核心语法速通 导览](./01-Python核心语法速通-导览.md) | [概念对比速查](./概念对比速查.md)

> [返回模块目录](../../README.md) | [返回知识导览](../../知识导览.md)
