# Python 迭代器与生成器：从迭代器协议到 LLM 流式输出

> 迭代器是 Python 的“数据传送带”，生成器是按需生产的“工厂”。理解这两者，才能解释 `for` 为什么能遍历任何对象，才能写出不撑爆内存的大文件管道，也才能看懂 LLM 流式响应为什么一个 token 一个 token 地吐出来。

> 参考链接：
> - [Python 教程：迭代器](https://docs.python.org/zh-cn/3/tutorial/classes.html#iterators) -- 迭代器协议入门
> - [Python 语言参考：迭代器类型](https://docs.python.org/zh-cn/3/library/stdtypes.html#iterator-types) -- `__iter__` / `__next__` 规范
> - [Python 标准库：itertools](https://docs.python.org/zh-cn/3/library/itertools.html) -- 工具清单与等价实现
> - [Python 语言参考：yield 表达式](https://docs.python.org/zh-cn/3/reference/expressions.html#yieldexpr) -- 生成器语义
> - [PEP 380：yield from](https://peps.python.org/pep-0380/) -- 子生成器委托
> - [PEP 479：生成器内的 StopIteration](https://peps.python.org/pep-0479/) -- 为什么它会变成 `RuntimeError`

---

## 目录

- [一、可迭代对象与迭代器](#一可迭代对象与迭代器)
- [二、迭代器协议：iter、next 与 StopIteration](#二迭代器协议iternext-与-stopiteration)
- [三、生成器函数与 yield](#三生成器函数与-yield)
- [四、生成器表达式](#四生成器表达式)
- [五、yield from：委托与双向通道](#五yield-from委托与双向通道)
- [六、send、throw 与 close](#六sendthrow-与-close)
- [七、itertools 常用工具](#七itertools-常用工具)
- [八、工程实战：大文件与 LLM 流式处理](#八工程实战大文件与-llm-流式处理)
- [九、常见坑](#九常见坑)
- [十、避坑指南](#十避坑指南)
- [十一、高频面试题（10 道）](#十一高频面试题10-道)
- [十二、本章学习自检](#十二本章学习自检)

---

## 一、可迭代对象与迭代器

### 1.1 一个 for 循环的完整旅程

Python 的 `for` 不关心下标，它只做三件事：调用 `iter()` 拿到迭代器、反复调用 `next()`、遇到 `StopIteration` 时结束。把这段逻辑手写出来，`for` 就不再神秘：

```python
numbers = [10, 20, 30]
it = iter(numbers)
while True:
    try:
        value = next(it)
    except StopIteration:
        break
    print(value)
# 10 / 20 / 30
```

`for` 还会正确处理 `break`、`continue` 和循环 `else`，但核心协议就是这三步。也正因如此，`for` 能遍历列表、字典、文件、数据库游标、网络响应流，以及任何遵守迭代器协议的自定义对象。

在 Agent 开发中，这个模型随处可见：工具列表是可迭代对象，模型返回的 token 流是迭代器，对话历史是可以逐条读取的容器。“流式消费”本质上就是在驱动某个迭代器。

### 1.2 可迭代对象与迭代器的分界

| 维度 | 可迭代对象（Iterable） | 迭代器（Iterator） |
|------|------------------------|--------------------|
| 必须实现 | `__iter__` | `__iter__` 和 `__next__` |
| 游标状态 | 通常没有，容器不记录读到哪 | 有，内部保存当前位置 |
| 能否重复遍历 | 每次 `iter()` 通常返回新迭代器 | 一次性，耗尽后不会复位 |
| 判断方式 | `isinstance(obj, Iterable)` | `isinstance(obj, Iterator)` 或 `iter(obj) is obj` |
| 典型例子 | `list`、`dict`、`str`、`range` | `list_iterator`、生成器、文件对象 |
| 关系 | 迭代器一定是可迭代对象 | 可迭代对象不一定是迭代器 |

关键结论只有一句：**迭代器的 `__iter__` 返回自身，因此迭代器一定可迭代；列表、字典、字符串只实现 `__iter__`，它们不是迭代器。**

```python
from collections.abc import Iterable, Iterator

nums = [1, 2, 3]
print(isinstance(nums, Iterable), isinstance(nums, Iterator))  # True False
print(iter(nums) is nums)                                       # False
gen = (x for x in nums)
print(isinstance(gen, Iterator), iter(gen) is gen)              # True True
```

为什么列表不直接实现 `__next__`？因为列表要支持“反复遍历”和“嵌套遍历”。如果容器自己保存游标，外层循环读到哪里，内层循环就会接着读。把“容器”和“游标”拆开，每次 `for` 新建独立游标，才能互不干扰。

文件对象是例外：它既是可迭代对象也是迭代器，`iter(f) is f` 为真。因此两个循环同时遍历同一个文件对象时会共享读写位置。

### 1.3 手写迭代器与可重复迭代

先看一个一次性迭代器：

```python
class OneShotCountdown:
    def __init__(self, start: int) -> None:
        self.current = start
    def __iter__(self):
        return self
    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

counter = OneShotCountdown(3)
print(list(counter))   # [3, 2, 1]
print(list(counter))   # []
```

第二次得到空列表，不是 bug，而是迭代器的定义：只保证向前走一次。要支持反复遍历，应让 `__iter__` 每次返回新迭代器，最简单的方式是把它写成生成器函数：

```python
class Countdown:
    def __init__(self, start: int) -> None:
        self.start = start
    def __iter__(self):
        current = self.start
        while current > 0:
            yield current
            current -= 1

counter = Countdown(3)
print(list(counter), list(counter))   # [3, 2, 1] [3, 2, 1]
```

`__iter__` 里出现 `yield` 后，它就成了生成器函数；每次 `iter(counter)` 创建全新的生成器，各自持有独立的 `current`。这就是“可重复迭代”的正确实现。

> 生活化类比：可迭代对象像菜谱，迭代器像书签。菜谱不记录读到哪一页，书签才记录；换一枚书签就能从头再读。把书签直接印在菜谱上（让容器自己当迭代器），两个人同时读就会抢页码。

---

## 二、迭代器协议：iter、next 与 StopIteration

### 2.1 iter() 的两种形态

```python
# 形态一：从可迭代对象获取迭代器
it = iter([1, 2, 3])

# 形态二：反复调用无参函数，直到返回值等于哨兵值
import io
stream = io.BytesIO(b"abcdefgh")
for chunk in iter(lambda: stream.read(3), b""):
    print(chunk)
# b'abc' / b'def' / b'gh'
```

`iter(callable, sentinel)` 等价于“一直调用 `callable()`，直到结果 `== sentinel`，但不包括哨兵”。它适合包装没有明显结尾的读取接口，比如文件块读取、队列轮询、C 扩展缓冲区。

两个细节：`callable` 必须无参，需要参数就用 `lambda` 或 `functools.partial`；哨兵比较使用 `==`，自定义对象要保证相等语义正确。

### 2.2 StopIteration 的边界

`StopIteration` 不是错误，而是迭代协议的正常结束信号。`for`、`list()`、`sum()`、`any()` 等消费者都会捕获它并停止。

```python
it = iter([1])
print(next(it))          # 1
print(next(it, None))    # None，提供默认值就不抛异常
try:
    next(it)
except StopIteration:
    print("done")        # done
```

手动驱动时优先用 `next(it, default)`；需要区分“正常结束”和“取到 None”时，再捕获异常。

需要特别记住：**不要在生成器函数体内主动 `raise StopIteration`。** 从 Python 3.7 起（PEP 479），生成器里冒出的 `StopIteration` 会被转成 `RuntimeError`，因为它会和“生成器正常结束”的信号混淆。想提前结束，用 `return`。

```python
def bad():
    yield 1
    raise StopIteration

g = bad()
print(next(g))   # 1
try:
    next(g)
except RuntimeError as exc:
    print(type(exc).__name__, exc)   # RuntimeError generator raised StopIteration
```

同理，在生成器内部调用 `next()` 时，如果被迭代对象已经耗尽，也会触发上述转换。安全写法是 `next(it, None)`，或显式捕获后 `return`。

常见消费者的行为：

| 消费者 | 是否立即耗尽 | 说明 |
|--------|--------------|------|
| `list()` / `tuple()` / `set()` | 是 | 构建容器，内存与元素数成正比 |
| `sum()` / `min()` / `max()` | 是 | 只保留聚合结果，额外内存 O(1) |
| `any()` / `all()` | 可能提前停止 | 短路后剩余元素留在迭代器里 |
| `sorted()` | 是 | 必须读完全部元素才能排序 |
| `zip()` / `enumerate()` | 逐个消费 | 返回惰性迭代器，长度由最短输入决定 |
| `map()` / `filter()` | 逐个消费 | Python 3 返回惰性迭代器，不是列表 |

这张表解释了一个高频 bug：先用 `any()` 判断，再想遍历同一个生成器，发现数据“少了一截”。不是生成器坏了，而是 `any()` 短路后迭代器停在了中间。

---

## 三、生成器函数与 yield

### 3.1 调用生成器函数时发生了什么

普通函数调用会立刻执行函数体；生成器函数调用只创建生成器对象，函数体一行都不执行。

```python
def counter(n: int):
    print("[gen] start")
    for i in range(n):
        print(f"[gen] before yield {i}")
        yield i
        print(f"[gen] after yield {i}")
    print("[gen] done")

g = counter(2)
print("[main] created")
print(next(g))
print(next(g))
try:
    next(g)
except StopIteration:
    print("[main] exhausted")
```

输出顺序是：`[main] created` → `[gen] start` → `[gen] before yield 0` → `0` → `[gen] after yield 0` → `[gen] before yield 1` → `1` → `[gen] after yield 1` → `[gen] done` → `[main] exhausted`。

每次 `yield` 都像“暂停并交出一个值”：生成器保存栈帧、局部变量和指令位置，控制权回到调用方；下一次 `next()` 从暂停点之后继续。这个“可暂停的函数”就是生成器最本质的能力。

几个对象要分清：`counter` 是生成器函数；`counter(2)` 是生成器对象，也是迭代器；`next(g)` 驱动前进一步；函数体执行完或遇到 `return` 时抛出 `StopIteration`。用 `inspect.isgeneratorfunction(gen)` 和 `inspect.isgenerator(g)` 可以分别判断。

### 3.2 生成器的四种状态

CPython 的 `inspect` 模块把生成器状态暴露为四个常量：

| 状态 | 含义 | 如何进入 |
|------|------|----------|
| `GEN_CREATED` | 已创建，尚未开始 | 调用生成器函数后 |
| `GEN_RUNNING` | 正在执行 | 被 `next()` / `send()` 驱动期间 |
| `GEN_SUSPENDED` | 暂停在 `yield` 处 | `yield` 交出值后 |
| `GEN_CLOSED` | 已结束或已关闭 | 正常结束、异常退出、`close()` |

```python
import inspect

def gen():
    yield 1

g = gen()
print(inspect.getgeneratorstate(g))   # GEN_CREATED
next(g)
print(inspect.getgeneratorstate(g))   # GEN_SUSPENDED
try:
    next(g)
except StopIteration:
    pass
print(inspect.getgeneratorstate(g))   # GEN_CLOSED
```

对 `GEN_CLOSED` 的生成器再调用 `next()` 只会得到 `StopIteration`；在 `GEN_RUNNING` 时重入（例如生成器内部再次驱动自己）会得到 `ValueError: generator already executing`。

### 3.3 生命周期与资源释放

生成器不只是懒计算，它还是一种资源管理边界。只要用 `try/finally` 或 `with`，无论正常结束、被异常打断，还是被调用方提前关闭，清理代码都有机会执行。

```python
import io

def read_lines(stream):
    with stream:
        for line in stream:
            yield line.rstrip("\n")

source = io.StringIO("one\ntwo\n")
gen = read_lines(source)
print(next(gen))       # one
gen.close()            # 触发 GeneratorExit，with 块退出
print(source.closed)   # True
```

`close()` 会在暂停点抛出 `GeneratorExit`。生成器应让它继续传播（或直接返回），**不能在处理 `GeneratorExit` 时再 `yield`**，否则会抛 `RuntimeError: generator ignored GeneratorExit`。

如果调用方既不耗尽也不 `close()`，清理时机取决于实现：CPython 依赖引用计数，生成器失去最后一个引用时通常会立即回收并执行 `finally`；其他实现可能延迟到垃圾回收。生产代码不要依赖“GC 一定及时”，该关闭就关闭：

```python
import contextlib
import io

with contextlib.closing(read_lines(io.StringIO("one\ntwo\n"))) as lines:
    for line in lines:
        if line:
            break
# 离开 with 时一定会调用 lines.close()
```

> 生活化类比：生成器像自来水管，`yield` 是水龙头。你不开水龙头，水不会流；你关掉水龙头（`close()`），上游要负责把管子收好（`finally`）。上游接到一半就跑，下游就会漏水（资源泄漏）。

---

## 四、生成器表达式

### 4.1 语法与求值时机

生成器表达式用圆括号包住推导式，返回生成器对象：

```python
squares = (x * x for x in range(5))
print(next(squares))    # 0
print(list(squares))    # [1, 4, 9, 16]，0 已经被取走
print(sum(x * x for x in range(5)))   # 30，唯一实参可省略外层括号
```

它和列表推导式最大的区别是求值时机：列表推导式创建时就算全部元素；生成器表达式只创建“计算计划”，每次 `next()` 才算一个。额外内存 O(1)，与数据量无关。

一个容易忽略的细节：**最外层的可迭代对象在创建时求值，内层表达式和过滤条件延迟到迭代时。**

```python
data = [1, 2, 3]
gen = (x * 2 for x in data)
data = [9]
print(list(gen))        # [2, 4, 6]，绑定创建时的列表对象

factor = 10
gen = (x * factor for x in [1, 2])
factor = 100
print(list(gen))        # [100, 200]，factor 在迭代时才查找
```

第一条说明 `iter(data)` 在创建时已经取到旧列表的迭代器；第二条说明自由变量仍遵循运行时的名字查找。理解这一点，才能解释后面的“闭包延迟绑定”。

### 4.2 与列表推导式的取舍

| 维度 | 列表推导式 | 生成器表达式 |
|------|------------|--------------|
| 求值 | 立即计算全部 | 按需计算，一次一个 |
| 内存 | O(n) | O(1) 额外内存 |
| 重复遍历 | 可以 | 不可以，一次性 |
| 长度 / 下标 | 支持 `len()`、索引 | 不支持 |
| 调试 | 可直接打印整个列表 | 打印出来只是生成器对象 |
| 异常时机 | 创建时抛 | 迭代到该元素时抛 |
| 适用场景 | 数据量小、需反复使用 | 数据量大、只消费一次、流式管道 |

选择原则：需要多次遍历、随机访问、排序，或数据量可控时用列表；数据量大、只需顺序消费一次、希望尽早拿到第一个结果时用生成器表达式；传给 `sum`、`any`、`max` 等聚合函数时优先用生成器表达式，避免中间列表。

```python
with open("access.log", encoding="utf-8") as f:
    total = sum(len(line) for line in f)
```

生成器表达式不是“永远更快”：它省内存，但每次取值都要经过生成器帧切换。数据量小又要反复使用时，列表更直接。先看内存约束，再看访问模式。

---

## 五、yield from：委托与双向通道

### 5.1 委托迭代与递归展平

`yield from iterable` 最直观的作用，是把一个可迭代对象的元素原样转发给调用方：

```python
def chain_two():
    yield from [1, 2]
    yield from (3, 4)

print(list(chain_two()))   # [1, 2, 3, 4]
```

它和 `for item in sub: yield item` 在“只取值”时结果相同，但 `yield from` 不只是语法糖：`next()`、`send()`、`throw()`、`close()` 都会转发给子生成器，子生成器的 `return` 值还会成为表达式的值。手工 `for` 循环做不到这些。

递归展平是经典用法：

```python
def flatten(items):
    for item in items:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

print(list(flatten([1, [2, [3, 4]], 5])))   # [1, 2, 3, 4, 5]
```

每一层递归都把自己的产出委托给上一层，调用方看到的是一个扁平迭代器，不需要关心中间嵌套了多少层。

### 5.2 双向通道与返回值

`yield from` 的完整语义可以概括为四句：子迭代器产出的值原样传给调用方；调用方 `send()` 的值原样送进子生成器；`throw()` 的异常原样抛进子生成器；子生成器结束时，其 `StopIteration.value` 成为 `yield from` 表达式的返回值。

```python
def inner():
    received = yield 1
    print(f"[inner] received: {received}")
    yield 2
    return "inner-result"

def outer():
    result = yield from inner()
    yield f"got: {result}"

gen = outer()
print(next(gen))          # 1
print(gen.send("hello"))  # [inner] received: hello，然后输出 2
print(next(gen))          # got: inner-result
```

`send("hello")` 没有停在 `outer`，而是被转发到 `inner` 的 `yield 1` 处；`inner` 返回的字符串被 `outer` 接住，继续产出。

| 能力 | `for item in sub: yield item` | `yield from sub` |
|------|-------------------------------|------------------|
| 转发产出 | 支持 | 支持 |
| 转发 `send()` | 不支持 | 支持 |
| 转发 `throw()` | 不支持 | 支持 |
| 转发 `close()` | 部分支持 | 支持 |
| 获取子生成器返回值 | 不支持 | 支持 |
| 适用场景 | 简单拼接 | 委托、递归、协程组合 |

PEP 380 引入 `yield from`，最初就是为了让生成器像协程一样组合。Python 3.5 之后原生协程用 `await`，但委托语义一脉相承：把控制权交给另一个可暂停对象，等它完成后拿回结果。阅读老代码时看到 `yield from`，不要只当成扁平化工具，它往往意味着一种协程式控制流。

---

## 六、send、throw 与 close

### 6.1 send：向暂停点送入数据

普通 `yield` 只向外产出值；`send()` 让调用方还能把值送回去。此时 `yield` 是表达式，它的值就是 `send()` 的参数：

```python
def running_average():
    total = 0.0
    count = 0
    average = None
    while True:
        value = yield average
        if value is None:
            continue
        total += value
        count += 1
        average = total / count

avg = running_average()
print(next(avg))        # None，启动生成器，停在第一个 yield
print(avg.send(10))     # 10.0
print(avg.send(20))     # 15.0
print(avg.send(30))     # 20.0
```

第一次必须用 `next(avg)` 或 `avg.send(None)` 启动。原因很直接：生成器还没运行到第一个 `yield`，没有暂停点接收值。对刚创建的生成器调用 `send(非 None)` 会得到 `TypeError: can't send non-None value to a just-started generator`。

`next(g)` 与 `g.send(None)` 等价。`send()` 的返回值是**下一个** `yield` 产出的值，而不是本次送入的值，初学时很容易绕晕。

这种“yield 接收、send 送入”的模式就是生成器协程。在 `async/await` 出现之前，很多异步框架用它实现调度；今天业务代码很少直接这么写，但理解它有助于看懂 `contextlib.contextmanager`、旧版 `asyncio` 代码和部分流式处理库。

### 6.2 throw 与 close：异常注入和清理

`throw()` 在暂停点抛入异常，生成器可以像普通代码一样捕获：

```python
def guarded():
    try:
        while True:
            yield "waiting"
    except ValueError as exc:
        yield f"caught: {exc}"

g = guarded()
print(next(g))                       # waiting
print(g.throw(ValueError("boom")))   # caught: boom
```

如果生成器没有捕获，异常会从暂停点向外传播，生成器随之关闭。`throw()` 常用于“让上游知道下游出错了”，例如解析器发现非法输入时通知生成器清理。

`close()` 则抛出 `GeneratorExit`，用于主动结束生成器：

```python
def resource():
    try:
        yield "open"
    finally:
        print("cleanup")

g = resource()
print(next(g))    # open
g.close()         # cleanup
```

| 方法 | 作用 | 生成器可捕获 | 典型用途 |
|------|------|--------------|----------|
| `next(g)` | 驱动到下一个 `yield` | 不涉及 | 普通迭代 |
| `g.send(v)` | 送入值并驱动 | `yield` 表达式接收 | 生成器协程、状态机 |
| `g.throw(exc)` | 在暂停点抛异常 | 可以，用 `try/except` | 错误注入、取消信号 |
| `g.close()` | 抛入 `GeneratorExit` 并结束 | 可以，用 `finally` 清理 | 释放文件、连接、锁 |

几个边界：`close()` 之后生成器处于 `GEN_CLOSED`，再 `next()` 只会得到 `StopIteration`；处理 `GeneratorExit` 时不能 `yield`，否则 `RuntimeError`；`GeneratorExit` 继承自 `BaseException`，`except Exception` 捕获不到；从 Python 3.12 起，`throw(type, value, traceback)` 三参数形式已弃用，推荐直接传异常实例。

`contextlib.contextmanager` 正是利用这套机制：`yield` 之前是 `__enter__`，之后是 `__exit__`，`with` 块里的异常会通过 `throw()` 送回生成器。理解了 `send/throw/close`，再看上下文管理器就不觉得神奇。

---

## 七、itertools 常用工具

### 7.1 无限、有限与组合三类工具

`itertools` 的函数全部返回惰性迭代器，适合流式处理。可以按三类记忆：

| 类别 | 函数 | 作用 | 注意点 |
|------|------|------|--------|
| 无限 | `count(start, step)` | 等差无限序列 | 必须配合 `islice` 或 `break` |
| 无限 | `cycle(iterable)` | 循环重复序列 | 会缓存原序列，内存与长度成正比 |
| 无限 | `repeat(obj, times=None)` | 重复同一对象 | 不传 `times` 就是无限 |
| 有限 | `chain(*its)` / `chain.from_iterable` | 串联多个可迭代对象 | 不预读全部输入 |
| 有限 | `islice(it, stop)` | 切片迭代器 | 不支持负数索引 |
| 有限 | `zip_longest(*its, fillvalue=None)` | 按最长序列拉链 | 短序列用填充值补齐 |
| 有限 | `tee(it, n)` | 复制成 n 个迭代器 | 会缓冲未消费元素 |
| 有限 | `groupby(it, key)` | 按相邻 key 分组 | 必须先按 key 排序 |
| 有限 | `accumulate(it, func)` | 累积计算 | 默认累加，可传 `operator.mul` |
| 有限 | `pairwise(it)` | 相邻元素对 | Python 3.10+ |
| 有限 | `batched(it, n)` | 固定大小分批 | Python 3.12+ |
| 组合 | `product(*its, repeat=1)` | 笛卡尔积 | 结果数为长度之积 |
| 组合 | `permutations(it, r)` | 排列 | 结果数为 `n! / (n-r)!` |
| 组合 | `combinations(it, r)` | 组合，不考虑顺序 | 结果数为 `C(n, r)` |
| 组合 | `combinations_with_replacement(it, r)` | 可重复组合 | 结果数为 `C(n+r-1, r)` |

```python
import itertools

print(list(itertools.islice(itertools.count(10, 5), 4)))  # [10, 15, 20, 25]
print(list(itertools.chain([1, 2], "ab")))                # [1, 2, 'a', 'b']
print(list(itertools.accumulate([1, 2, 3, 4])))           # [1, 3, 6, 10]
print(list(itertools.pairwise([1, 2, 3, 4])))             # [(1, 2), (2, 3), (3, 4)]
```

`groupby` 是坑最多的一个。它只合并**相邻**的相同 key，不会像 SQL 的 `GROUP BY` 那样全局聚合：

```python
import itertools

rows = [("a", 1), ("a", 2), ("b", 3), ("a", 4)]
for key, group in itertools.groupby(rows, key=lambda row: row[0]):
    print(key, list(group))
# a [('a', 1), ('a', 2)] / b [('b', 3)] / a [('a', 4)]
```

希望同一个 key 只出现一次，先 `sorted(rows, key=...)`。另外，`group` 是共享底层迭代器的子迭代器，下一次外层循环会把它推进到下一组，因此要及时 `list(group)` 或消费掉，不能存起来稍后再读。

### 7.2 工程常用的四个模式

**分批处理。** 把大流切成固定大小的批次，既控制内存，也方便批量调用接口：

```python
import itertools

def chunks(iterable, size: int):
    it = iter(iterable)
    while batch := list(itertools.islice(it, size)):
        yield batch

print(list(chunks(range(7), 3)))   # [[0, 1, 2], [3, 4, 5], [6]]
```

Python 3.12+ 可直接用 `itertools.batched(iterable, size)`，返回元组批次；兼容 3.10/3.11 时用上面的 `chunks`。

**滑动窗口。** 计算相邻差值、统计最近 N 条日志都适合用窗口：

```python
import itertools
from collections import deque

def sliding_window(iterable, size: int):
    it = iter(iterable)
    window = deque(itertools.islice(it, size), maxlen=size)
    if len(window) == size:
        yield tuple(window)
    for item in it:
        window.append(item)
        yield tuple(window)

print(list(sliding_window(range(5), 3)))   # [(0, 1, 2), (1, 2, 3), (2, 3, 4)]
```

窗口大小为 2 时，Python 3.10+ 的 `pairwise` 更直接。

**展平嵌套结构。** 一层嵌套用 `chain.from_iterable`，多层用递归 `yield from`：

```python
import itertools

print(list(itertools.chain.from_iterable([[1, 2], [3], [4, 5]])))   # [1, 2, 3, 4, 5]
```

**轮询与重复。** `cycle` 可以在多个候选项之间轮转，例如多把 API Key 轮流使用：

```python
import itertools

keys = itertools.cycle(["key-a", "key-b", "key-c"])
print([next(keys) for _ in range(5)])   # ['key-a', 'key-b', 'key-c', 'key-a', 'key-b']
```

`cycle` 会缓存输入序列，输入很大时不要用；`repeat` 适合给 `zip` 补一个常量列。

---

## 八、工程实战：大文件与 LLM 流式处理

### 8.1 大文件：逐行与分块

Python 的文件对象本身就是迭代器，`for line in f` 会按行惰性读取，不会把整个文件装进内存：

```python
import os
import tempfile

with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as f:
    f.write("alpha\nbeta\ngamma\n")
    path = f.name

try:
    with open(path, encoding="utf-8") as f:
        for line in f:
            print(line.rstrip().upper())
finally:
    os.unlink(path)
# ALPHA / BETA / GAMMA
```

| 写法 | 内存 | 适用场景 |
|------|------|----------|
| `f.read()` | 整个文件 | 小文件，或确实需要完整字符串 |
| `f.readlines()` | 整个文件的所有行 | 小文件，需要按行随机访问 |
| `for line in f` | 一行（加缓冲区） | 大文本文件，逐行处理 |
| `iter(lambda: f.read(n), b"")` | 一个块 | 二进制大文件、固定块协议 |

```python
import io

stream = io.BytesIO(b"0123456789abcdef")
for chunk in iter(lambda: stream.read(6), b""):
    print(chunk)
# b'012345' / b'6789ab' / b'cdef'
```

文本模式的 `read(n)` 返回字符数而不是字节数，UTF-8 下一个字符可能占多个字节；需要精确控制字节量时用二进制模式。

### 8.2 流式管道：JSONL 与日志

生成器最适合搭管道：每层只做一件事，层间用 `yield` 传递，内存占用只与单条记录有关。

```python
import io
import json

raw = io.StringIO(
    '{"level": "INFO", "msg": "ok"}\n'
    '{"level": "ERROR", "msg": "boom"}\n'
    'not-json\n'
    '{"level": "ERROR", "msg": "again"}\n'
)

def parse_jsonl(lines):
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue

def only_errors(records):
    for record in records:
        if record.get("level") == "ERROR":
            yield record["msg"]

print(list(only_errors(parse_jsonl(raw))))   # ['boom', 'again']
```

这条管道有三个优点：`parse_jsonl` 不关心数据来自文件、网络还是内存，只要是一个行迭代器；坏行被跳过，不会中断整批处理（生产环境应记录坏行计数和样例，而不是静默吞掉）；下游不关心解析细节，职责单一，便于单独测试。

如果希望“每读一行就产生一个结果”而不是等全部读完，这种写法天然满足：调用方 `next()` 一次，管道只推进一条记录。

### 8.3 LLM token 流与 Agent 消费

大模型流式接口通常返回 SSE：一行一个 `data:` 负载，负载是 JSON，最后以 `data: [DONE]` 结束。下面用假数据模拟，不依赖网络：

```python
import json

def fake_sse():
    yield 'data: {"delta": "Hel"}\n\n'
    yield 'data: {"delta": "lo"}\n\n'
    yield 'data: {"delta": ", "}\n\n'
    yield 'data: {"delta": "world"}\n\n'
    yield "data: [DONE]\n\n"

def token_stream(lines):
    for line in lines:
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line[len("data:"):].strip()
        if payload == "[DONE]":
            return
        delta = json.loads(payload).get("delta")
        if delta:
            yield delta

print("".join(token_stream(fake_sse())))   # Hello, world
```

真实项目还要处理空行、注释行（以 `:` 开头）、多行 `data:`、网络分块把一行切成两半、`[DONE]` 之后仍有尾包，以及服务端返回错误事件。解析器的职责就是把这些细节挡在业务层之外。

Agent 场景通常要同时做两件事：一边把 token 推给前端展示，一边把完整文本攒起来供下一步决策。常见做法是把“完整文本”放在生成器外部累加，避免把控制事件和 token 混在同一个流里：

```python
def stream_answer(deltas, sink: list):
    for delta in deltas:
        sink.append(delta)
        yield delta

full = []
for chunk in stream_answer(iter(["He", "llo"]), full):
    print(chunk, end="")
print()
print("".join(full))   # Hello
```

工具调用（tool call）的流式返回要更小心：函数名通常先到，参数 JSON 是分片到达的。**不要对每个分片单独 `json.loads`**，而应把 `arguments` 片段拼成完整字符串，等流结束或收到 `finish_reason` 后再解析。否则会在第一个分片就得到“JSON 不完整”的错误。

流式处理的背压是“拉模式”自带的：生成器只在调用方 `next()` 时生产下一个值。下游处理慢，上游自然停下；不像推送式生产者，需要额外的缓冲区或信号量来限速。取消时，调用方应 `close()` 生成器，让 `finally` 关闭 HTTP 连接、释放锁和临时文件。

> 本节示例都是同步生成器。异步场景使用 `async def` + `yield` 的异步生成器，消费方式是 `async for`，细节放在《Python 并发与协程》一章。

---

## 九、常见坑

### 9.1 生成器耗尽与重复消费

生成器是一次性的，消费完后处于 `GEN_CLOSED`，再遍历只会得到空结果：

```python
gen = (x for x in range(3))
print(list(gen))   # [0, 1, 2]
print(list(gen))   # []
```

修复方式：把生成逻辑封装成函数，每次重新创建；用 `list(gen)` 物化缓存（内存换重复）；用 `itertools.tee` 复制成多个迭代器；或把对象改造成“每次 `__iter__` 返回新生成器”的可重复对象。

`tee` 不是零成本复制。多个分支共享同一个源迭代器，每个分支都要缓冲自己尚未消费的元素；如果分支消费速度差距大，缓冲区会持续增长，极端情况下接近把整个流缓存下来。数据量大时，重建生成器通常比 `tee` 更可控。

短路消费也会留下“半截”迭代器：

```python
gen = (x for x in [1, 2, 3])
print(any(x == 2 for x in gen))   # True
print(list(gen))                  # [3]
```

`any()` 在 2 处就停了，3 还没被取走。如果后续逻辑假设“生成器已经消费完”，就会得到意料之外的数据。

### 9.2 闭包延迟绑定

闭包捕获的是变量，不是变量在创建时的值。循环里创建多个函数，等循环结束后再调用，它们看到的都是循环变量的最终值：

```python
handlers = []
for name in ["search", "calc"]:
    handlers.append(lambda query: f"{name}:{query}")

print([handler("q") for handler in handlers])
# ['calc:q', 'calc:q']
```

两个 handler 都用了 `calc`，因为 lambda 执行时循环已经结束，`name` 的值是最后一个。经典修复是把当前值绑定为默认参数：

```python
handlers = []
for name in ["search", "calc"]:
    handlers.append(lambda query, name=name: f"{name}:{query}")
print([handler("q") for handler in handlers])   # ['search:q', 'calc:q']
```

在 Agent 开发中，这个坑经常出现在“批量注册工具处理器”时：所有工具都指向最后一个工具名，调用哪个都执行同一段逻辑。另一种修复是用 `functools.partial` 把当前工具名固定下来。

生成器表达式也遵循同样的名字查找规则。如果在生成器表达式里引用循环变量，真正迭代时看到的也是最终值；需要“快照”时，用默认参数或在创建前把值存进元组。

### 9.3 生成器中的异常与 return

生成器在 `yield` 处暂停，异常会在恢复执行时从暂停点抛出。`finally` 一定会执行，但它不能改变“异常继续向外传播”的事实：

```python
def boom():
    try:
        yield 1
        raise ValueError("failed")
    finally:
        print("[gen] finally")

g = boom()
print(next(g))   # 1
try:
    next(g)
except ValueError as exc:
    print(exc)   # failed
# [gen] finally 先于 failed 输出
```

如果在生成器里捕获了异常却不再抛出，调用方就永远看不到错误。流式处理里这很危险：上游解析失败被吞掉，下游会收到一条“看起来正常但缺了一段”的数据。正确做法是记录上下文后重新抛出，或把错误包装成流中的显式事件。

`return` 在生成器里的作用和普通函数不同：它不会把值返回给 `for` 循环，而是放进 `StopIteration.value`：

```python
def gen():
    yield 1
    return 42

it = iter(gen())
print(next(it))   # 1
try:
    next(it)
except StopIteration as exc:
    print(exc.value)   # 42
```

`for` 会捕获 `StopIteration` 并丢弃 `value`，所以循环里拿不到 42。想拿返回值，要么手动 `next()`，要么用 `yield from` 委托（返回值会成为表达式的值）。这就是“生成器 return 值没用”这一说法的来源——不是没用，而是普通 `for` 不暴露它。

PEP 479 的规则再强调一次：生成器体内不要 `raise StopIteration`，也不要让内部的 `next()` 把 `StopIteration` 漏出来。解释器会把它转成 `RuntimeError`，堆栈还会指向一个看似无关的位置。

### 9.4 其他高频陷阱

- **把生成器表达式当惰性列表**：它不支持 `len()`、索引、切片，也不能重复遍历；需要这些能力时先物化。
- **遍历列表时修改列表**：列表迭代器按索引推进，插入或删除会导致跳过或重复；过滤时用列表推导式生成新列表，或遍历副本。
- **无限生成器没有边界**：`count()`、`cycle()`、`repeat()` 默认无限，直接 `list()` 会耗尽内存；用 `islice`、`takewhile` 或 `break` 加上界。
- **`next()` 不带默认值**：不确定是否还有元素时可能抛 `StopIteration`；用 `next(it, None)` 或捕获异常。
- **异步生成器里用 `yield from`**：语法不允许；委托异步迭代器应写 `async for item in source: yield item`。
- **生成器没有关闭**：持有文件、连接、锁的生成器如果既不耗尽也不 `close()`，释放时机不可控；用 `contextlib.closing` 或把资源管理放进 `with`。
- **首次 `send()` 传了非 None**：生成器还没启动，没有暂停点接收值；先 `next(g)` 或 `g.send(None)`。
- **`throw()` 后继续当正常流使用**：异常没被捕获时生成器会关闭，后续 `next()` 只会得到 `StopIteration`。

---

## 十、避坑指南

### 10.1 检查清单与修复手法

| 症状 | 根因 | 修复 |
|------|------|------|
| 第二次遍历得到空结果 | 生成器已耗尽 | 重建生成器、物化列表，或改用可重复对象 |
| 只处理了一部分数据 | `any()` / `all()` / `next()` 短路 | 明确消费边界，剩余数据单独处理 |
| 所有回调都用最后一个值 | 闭包延迟绑定 | 默认参数、`functools.partial` 或工厂函数 |
| 流式解析偶发 JSON 错误 | 按分片解析了不完整 JSON | 拼接完整负载后再解析 |
| 报 `generator raised StopIteration` | PEP 479 转换 | 用 `return` 结束，不要 `raise StopIteration` |
| `for` 拿不到生成器的 `return` 值 | `for` 丢弃 `StopIteration.value` | 手动 `next()` 或 `yield from` |
| `generator ignored GeneratorExit` | 清理分支里又 `yield` | 清理时只释放，不再产出 |
| 内存没有下降 | 某处 `list(gen)` 或 `readlines()` 物化了数据 | 逐条消费，避免中间列表 |
| 文件句柄泄漏 | 生成器未耗尽也未关闭 | `contextlib.closing` 或 `with` 管理 |
| `send()` 报 TypeError | 首次传入非 None | 先 `next(g)` 启动 |
| 多分支迭代器内存上涨 | `tee` 缓冲 | 改为重建生成器或控制消费速度 |

写生成器时遵守五条纪律：一个生成器只做一件事；资源用 `try/finally` 或 `with` 包住；不要吞异常；不要 yield 之后还会被修改的可变对象；为无限流设边界。

一个可复用的安全模板：

```python
def stream_resource(source):
    resource = source.open()
    try:
        while True:
            chunk = resource.read()
            if not chunk:
                break
            yield chunk
    finally:
        resource.close()
```

正常读完会关闭，调用方 `break` 后 `close()` 会关闭，处理过程中抛异常也会关闭。把 `open()` 换成数据库游标、HTTP 响应、锁的获取，结构完全一样。

---

## 十一、高频面试题（10 道）

### 11.1 题目与参考答案

#### 题目 1：可迭代对象和迭代器有什么区别？如何判断一个对象是不是迭代器？

**参考答案：** 可迭代对象实现 `__iter__`，能被 `for` 遍历，但通常不保存游标，例如 `list`、`dict`、`str`。迭代器同时实现 `__iter__` 和 `__next__`，内部保存游标，只能向前消费一次。迭代器的 `__iter__` 返回自身，所以“迭代器一定可迭代，可迭代对象不一定是迭代器”。

判断方式：`isinstance(obj, collections.abc.Iterator)`，或更直接地看 `iter(obj) is obj`。为 `True` 说明对象本身就是迭代器；为 `False` 说明它只是可迭代容器，每次 `iter()` 会创建新游标。

#### 题目 2：`for x in obj` 的完整执行流程是什么？`StopIteration` 起什么作用？

**参考答案：** `for` 先调用 `iter(obj)` 得到迭代器，然后反复调用 `next(iterator)`，把返回值赋给 `x` 并执行循环体；当 `next()` 抛出 `StopIteration` 时，循环正常结束。`break` 会提前退出，但不会关闭迭代器；循环 `else` 只在没有 `break` 的正常结束时执行。

`StopIteration` 是迭代协议的正常结束信号，不是错误。`list()`、`sum()`、`any()` 等消费者都依赖它判断何时停止。手动驱动时可以用 `next(it, default)` 避免异常，或在确实需要区分结束时捕获它。

#### 题目 3：`yield` 和 `return` 有什么区别？调用生成器函数时发生了什么？

**参考答案：** `return` 结束函数并把值返回给调用方；`yield` 暂停函数、交出一个值，并保留栈帧和局部状态，下次 `next()` 从暂停点继续。生成器函数里可以有多个 `yield`，也可以有 `return`，但 `return` 的值会放进 `StopIteration.value`，普通 `for` 循环拿不到。

调用生成器函数时，函数体不会执行，只创建一个生成器对象。第一次 `next()` 才开始执行到第一个 `yield`；此后每次 `next()` 恢复执行到下一个 `yield`；函数结束或 `return` 时抛出 `StopIteration`。

#### 题目 4：生成器表达式和列表推导式有什么区别？分别适合什么场景？

**参考答案：** 列表推导式立即计算并返回列表，内存 O(n)，支持 `len()`、索引和重复遍历；生成器表达式返回生成器，按需计算，额外内存 O(1)，只能消费一次，不支持长度和下标。异常时机也不同：列表推导式在创建时抛，生成器表达式在迭代到出错元素时才抛。

数据量小、需要反复使用或随机访问时用列表推导式；数据量大、只需顺序消费一次、或要传给 `sum`/`any`/`max` 等聚合函数时用生成器表达式。注意生成器表达式最外层的可迭代对象在创建时就求值，内部表达式则延迟到迭代时。

#### 题目 5：`yield from` 比 `for item in sub: yield item` 多了哪些能力？

**参考答案：** 除了转发产出，`yield from` 还会把调用方的 `send()` 值转发给子生成器，把 `throw()` 的异常抛进子生成器，把 `close()` 传给子生成器；子生成器结束时，其 `StopIteration.value` 会成为 `yield from` 表达式的值。手工 `for` 循环只能转发产出，丢失了双向通信和返回值。

因此 `yield from` 适合生成器委托、递归展平，以及把多个子生成器组合成一个协程式控制流。PEP 380 引入它就是为了支持这种委托；原生协程的 `await` 在委托语义上与之相似。

#### 题目 6：`send()`、`throw()`、`close()` 分别有什么用途？为什么第一次 `send()` 必须传 `None`？

**参考答案：** `send(v)` 把值送进生成器的暂停点，作为 `yield` 表达式的值，并驱动到下一个 `yield`；`throw(exc)` 在暂停点抛入异常，生成器可以捕获并处理；`close()` 抛入 `GeneratorExit`，用于主动结束生成器并触发 `finally` 清理。

第一次必须传 `None`，因为生成器还没运行到第一个 `yield`，没有暂停点接收值。对刚创建的生成器调用 `send(非 None)` 会抛 `TypeError`。正确启动方式是 `next(g)` 或 `g.send(None)`，两者等价。

#### 题目 7：生成器如何实现协程？它和 `async/await` 是什么关系？

**参考答案：** 生成器协程利用 `yield` 暂停、`send()` 送入值、`throw()` 注入异常，把“暂停/恢复”变成双向通信机制。调用方根据生成器的产出决定下一步送什么，生成器根据收到的值继续执行。早期 `asyncio` 用 `@coroutine` 和 `yield from` 实现这种调度。

Python 3.5 之后引入原生协程 `async def` / `await`，语义更清晰，事件循环直接调度 `Task`，不再需要手动 `send()`。可以理解为生成器协程是“手动挡”，原生协程是“自动挡”；底层都基于可暂停的执行帧，但原生协程有专门的操作码、异常体系和调度协议。业务代码应优先用 `async/await`。

#### 题目 8：生成器耗尽了怎么办？`itertools.tee` 有什么代价？

**参考答案：** 生成器是一次性迭代器，耗尽后再遍历只会得到空结果。修复方式包括：把生成逻辑封装成函数，每次重新创建；用 `list(gen)` 物化缓存（内存换重复）；用 `itertools.tee` 复制成多个迭代器；或把对象改造成“每次 `__iter__` 返回新生成器”的可重复对象。

`tee` 不是零成本复制。多个分支共享同一个源迭代器，每个分支都要缓冲自己尚未消费的元素；如果分支消费速度差距大，缓冲区会持续增长，极端情况下接近把整个流缓存下来。大数据场景下，重建生成器通常比 `tee` 更可控。

#### 题目 9：生成器里 `return` 的值去哪了？PEP 479 解决了什么问题？

**参考答案：** 生成器 `return value` 会把 `value` 放进结束时的 `StopIteration.value`。普通 `for` 循环捕获 `StopIteration` 后直接结束，所以拿不到这个值；手动 `next()` 捕获异常可以读到 `exc.value`；`yield from` 会把子生成器的返回值作为表达式结果，因此能自然接住。

PEP 479 解决的是“`StopIteration` 语义冲突”：生成器内部如果意外抛出 `StopIteration`（例如直接 `raise`，或内部 `next()` 耗尽），会被误认为生成器正常结束，导致外层循环悄悄停止。从 Python 3.7 起，生成器体内冒出的 `StopIteration` 会被转成 `RuntimeError`，迫使开发者显式处理。想提前结束生成器，用 `return`。

#### 题目 10：如何用生成器处理 10GB 文件和 LLM 流式输出？背压体现在哪里？

**参考答案：** 大文件处理用 `for line in f` 或 `iter(lambda: f.read(n), b"")`，每次只保留一行/一块；解析、过滤、聚合分别写成生成器，用 `yield` 串联。不要 `read()`、`readlines()` 或 `list(gen)`，否则会把整个文件物化到内存。

LLM 流式输出把 SSE 的 `data:` 行解析成 token 生成器，下游一边 `yield` 给前端，一边把完整文本累积到列表，供下一轮 Agent 决策。工具调用的参数 JSON 分片到达，必须拼接完整后再解析。

背压体现在“拉模式”：生成器只在调用方 `next()` 时生产下一个值。下游写得慢，上游就暂停，不会无限堆积；如果中间有队列，则要用有界队列或信号量显式限制在途数据量。取消时调用 `close()`，让生成器的 `finally` 关闭 HTTP 连接和临时资源。

---

## 十二、本章学习自检

### 12.1 自检清单

**概念与协议**

- [ ] 能解释“可迭代对象”和“迭代器”的协议差异
- [ ] 能用 `iter(obj) is obj` 判断对象是否为迭代器
- [ ] 能写出 `for` 循环等价的 `iter` / `next` / `StopIteration` 代码
- [ ] 知道文件对象既是可迭代对象又是迭代器
- [ ] 能解释为什么列表不直接实现 `__next__`

**生成器语法**

- [ ] 能区分生成器函数、生成器对象和普通函数
- [ ] 能画出生成器从 `GEN_CREATED` 到 `GEN_CLOSED` 的状态迁移
- [ ] 能解释 `yield` 暂停时保存了哪些状态
- [ ] 能写出一个带 `try/finally` 清理的生成器
- [ ] 能说明生成器表达式与列表推导式的内存和一次性差异
- [ ] 知道生成器表达式最外层可迭代对象在创建时求值

**高级语义**

- [ ] 能用 `yield from` 递归展平嵌套列表
- [ ] 能说明 `yield from` 转发 `send` / `throw` / `close` 的行为
- [ ] 能写出 `send()` 驱动的累加器或状态机
- [ ] 能解释首次 `send()` 为什么必须传 `None`
- [ ] 能说明 `throw()` 和 `close()` 的区别，以及 `GeneratorExit` 的处理约束
- [ ] 知道生成器 `return` 值保存在 `StopIteration.value`
- [ ] 能解释 PEP 479 为什么把生成器内的 `StopIteration` 转成 `RuntimeError`

**工程与排错**

- [ ] 能用生成器管道处理大文件，避免 `readlines()`
- [ ] 能实现固定大小分批和滑动窗口
- [ ] 知道 `groupby` 只合并相邻 key，使用前通常要排序
- [ ] 知道 `tee` 会缓冲未消费元素，不能无脑复制大数据流
- [ ] 能识别生成器耗尽、闭包延迟绑定、无限流无边界三类 bug
- [ ] 能写出一个 SSE token 解析器，并说明工具调用参数为什么要拼接后再解析
- [ ] 能用 `close()` / `contextlib.closing` 保证生成器资源释放

**Agent 场景**

- [ ] 能解释为什么 token 流适合用生成器表达
- [ ] 能设计“边流式展示、边累积完整文本”的消费方式
- [ ] 能说明生成器拉模式天然具备背压
- [ ] 能说出同步生成器与异步生成器在消费方式上的区别

---

> 迭代器和生成器不是“高级语法糖”，而是 Python 处理流式数据的基础设施。把“容器 / 游标 / 生产者 / 消费者”四个角色分清，大部分看似诡异的 bug 都会变得可解释。
