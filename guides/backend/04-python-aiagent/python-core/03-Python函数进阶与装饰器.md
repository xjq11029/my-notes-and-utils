# Python 函数进阶与装饰器：从闭包到 Agent 中间件

> 如果你已经会写 `def`、`*args` 和 `**kwargs`，却还说不清 `@tool` 背后发生了什么，这篇文章就是为你准备的。
>
> 装饰器是 Python 里"把函数当零件组装"的机制。LangChain 的 `@tool` 把普通函数变成可被模型调用的工具，LangChain 1.x 的 `@before_model`、`@after_model` 把函数注册为 Agent 生命周期的钩子，`functools.lru_cache` 则用一行代码给昂贵的调用加上缓存。理解闭包、名字查找和 `@` 的等价展开，你才能在框架报错时知道该看哪一层。
>
> 本文面向 Python 3.10 及以上版本，示例只使用标准库；涉及版本差异的地方会单独标注。

> 参考资料：
> - [Python 教程：函数定义](https://docs.python.org/zh-cn/3/tutorial/controlflow.html#defining-functions)
> - [Python 语言参考：函数定义与装饰器](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#function-definitions)
> - [Python 标准库：functools](https://docs.python.org/zh-cn/3/library/functools.html)
> - [Python 语言参考：数据模型](https://docs.python.org/zh-cn/3/reference/datamodel.html)
> - [PEP 318：函数装饰器](https://peps.python.org/pep-0318/)
> - [PEP 443：单分派泛型函数](https://peps.python.org/pep-0443/)

---

## 目录

- [一、为什么 Agent 代码大量使用装饰器](#一为什么-agent-代码大量使用装饰器)
- [二、函数是一等对象与装饰器语法糖](#二函数是一等对象与装饰器语法糖)
- [三、闭包与 LEGB](#三闭包与-legb)
- [四、late binding 与循环变量陷阱](#四late-binding-与循环变量陷阱)
- [五、带参数的装饰器](#五带参数的装饰器)
- [六、类装饰器与可调用对象](#六类装饰器与可调用对象)
- [七、functools.wraps 与签名保留](#七functoolswraps-与签名保留)
- [八、functools.lru_cache 与缓存边界](#八functoolslru_cache-与缓存边界)
- [九、functools.partial 与 singledispatch](#九functoolspartial-与-singledispatch)
- [十、描述符与 property 的关系](#十描述符与-property-的关系)
- [十一、用装饰器写回调与注册表](#十一用装饰器写回调与注册表)
- [十二、用装饰器写中间件](#十二用装饰器写中间件)
- [十三、异步装饰器与上下文传递](#十三异步装饰器与上下文传递)
- [十四、常见坑与根因分析](#十四常见坑与根因分析)
- [十五、高频面试题（10 道）](#十五高频面试题10-道)
- [十六、避坑指南](#十六避坑指南)
- [十七、本章学习自检](#十七本章学习自检)

---

## 一、为什么 Agent 代码大量使用装饰器

Agent 框架有三个共性需求：把普通函数注册成能力、在调用前后插入横切逻辑、在生命周期节点挂载钩子。这三件事都不适合写进业务函数内部，于是一个 `@` 符号就成了框架的装配接口。

| 场景 | 常见写法 | 装饰器做了什么 |
|------|----------|----------------|
| 工具注册 | `@tool` | 读取函数签名与文档字符串，生成参数 schema，包装成框架可调用的工具对象 |
| 生命周期钩子 | `@before_model` / `@after_model` | 把函数登记到中间件列表，运行时在模型调用前后执行 |
| 包装调用 | `@wrap_model_call` / `@wrap_tool_call` | 包住真正的 handler，可改写请求、短路、重试、记录耗时 |
| 缓存与重试 | `@lru_cache` / 自定义 `@retry` | 不改业务函数，叠加横切能力 |
| Web 路由 | `@app.get("/items")` | 把路径与处理函数登记到路由表 |

具体 API 会随 LangChain 版本演进，本文关注装饰器这一层机制：只要你能把 `@` 展开成函数调用，就能读懂框架在做什么。无论形式多复杂，装饰器都可以概括为**接收一个可调用对象、返回一个可调用对象**；装饰发生在定义时，返回的可以是 wrapper、类实例或其他可调用对象，并且可以层层叠加。

学完本章你应该能：用 LEGB 和闭包解释装饰器为什么能记住外层变量；手写带参数装饰器、类装饰器；正确使用 `functools` 工具箱；用装饰器实现 Agent 的回调、中间件和异步日志，并避开顺序、绑定与缓存相关的坑。

---

## 二、函数是一等对象与装饰器语法糖

在 Python 里，`def` 不只是声明语法，它在执行时创建一个函数对象。函数对象有类型、有身份、能挂属性，也能像整数一样被赋值、传参和返回。

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

print(type(greet))        # <class 'function'>
print(greet.__name__)     # greet
greet.language = "zh"     # 函数对象可以挂自定义属性
print(greet.language)     # zh
print(greet("Ada"))       # Hello, Ada
```

| 一等对象能力 | 示例 | 在 Agent 中的用途 |
|--------------|------|-------------------|
| 赋值与传参 | `handler = greet` | 按配置选择模型或工具实现 |
| 作为返回值 | `def make(): return greet` | 工厂函数生成带配置的调用器 |
| 挂载属性 | `fn.tool_schema = schema` | 注册工具元数据 |
| 放入容器 | `TOOLS = {"weather": weather}` | 构建工具注册表 |

### 2.1 @ 只是语法糖

```python
from functools import wraps

def trace(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"call {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

@trace
def add(a: int, b: int) -> int:
    return a + b

# 完全等价于在函数定义后执行：add = trace(add)
print(add(1, 2))    # 先打印 call add，再打印 3
```

关键点：`@trace` 等价于在函数定义结束后执行 `add = trace(add)`；`wrapper` 通过闭包持有原函数 `fn`，调用时才真正执行 `fn`；这里的 `@wraps(fn)` 先照抄即可，它的作用在第七节展开。

### 2.2 装饰器的执行时机

| 阶段 | 发生的事情 |
|------|------------|
| 导入或执行到 `def` 时 | 先求值 `@` 后面的装饰器表达式，再创建原函数对象 |
| 紧接其后 | 按从下到上的顺序应用装饰器，把名字重新绑定到返回值 |
| 每次调用时 | 执行 wrapper，由 wrapper 决定是否以及何时调用原函数 |

因此，装饰器函数体内的 `print`、文件读取、网络请求都发生在**定义时**。如果希望这些动作每次调用都执行，必须把它们放进 wrapper 内部。

### 2.3 叠加顺序

```python
from functools import wraps

def tag(name):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return f"<{name}>{fn(*args, **kwargs)}</{name}>"
        return wrapper
    return decorate

@tag("outer")
@tag("inner")
def hello():
    return "hi"

print(hello())
# <outer><inner>hi</inner></outer>
```

`@a` 写在 `@b` 上面，等价于 `a(b(f))`：**下面的装饰器先包裹原函数，上面的装饰器后包裹结果**。请求从最外层进入，响应从最外层离开；最内层最接近原函数。

---

## 三、闭包与 LEGB

### 3.1 LEGB 名字查找

Python 查找一个名字时，按 Local、Enclosing、Global、Built-in 的顺序自内向外搜索，命中即停。

| 层级 | 含义 | 典型位置 | 如何修改 |
|------|------|----------|----------|
| Local | 当前函数的局部作用域 | 函数参数、函数内赋值 | 直接赋值 |
| Enclosing | 外层嵌套函数的作用域 | 闭包中的自由变量 | `nonlocal` |
| Global | 模块全局作用域 | 模块顶层变量 | `global` |
| Built-in | 内置命名空间 | `len`、`print`、`ValueError` | 不推荐覆盖 |

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        print(x)      # 找到 Enclosing 层的 x
    inner()

outer()               # enclosing
```

有一个容易忽略的规则：**只要函数体内对某个名字赋值，编译器就把这个名字视为局部变量**，除非显式声明 `global` 或 `nonlocal`。因此函数内写 `count += 1` 时，`count` 已被判定为局部变量，但第一次读取时还没有绑定值，触发 `UnboundLocalError`。

### 3.2 闭包是什么

闭包是"函数 + 它引用的外层变量"的组合。外层函数返回内层函数后，内层函数仍然能访问外层的局部变量，这些变量保存在单元格（cell）里，生命周期被延长。

```python
def make_counter(start: int = 0):
    count = start
    def counter() -> int:
        nonlocal count
        count += 1
        return count
    return counter

c = make_counter(10)
print(c(), c())       # 11 12
print(c.__code__.co_freevars)          # ('count',)
print(c.__closure__[0].cell_contents)  # 12
```

`nonlocal count` 表示"我要修改的是外层函数的 `count`，不是新建一个局部变量"。如果没有它，`count += 1` 会触发 `UnboundLocalError`。闭包在 Agent 代码里常用于预绑定配置：外层函数收前缀、超时或工具名，返回的装饰器再把配置带进 wrapper。

### 3.3 global 与 nonlocal 的差别

| 关键字 | 绑定的作用域 | 典型场景 | 不使用的后果 |
|--------|--------------|----------|--------------|
| `global` | 模块全局 | 修改模块级计数器、配置 | 赋值被当成局部变量 |
| `nonlocal` | 最近的外层函数 | 闭包状态、计数器 | 同上，或误改全局 |

两者都要求名字在外层已经存在；`nonlocal` 找不到外层变量时会直接报 `SyntaxError`。

---

## 四、late binding 与循环变量陷阱

闭包捕获的是**变量**，不是变量在创建时的**值**。函数调用时才去 cell 里取当前值，这就是 late binding（延迟绑定）。

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])   # [2, 2, 2]
```

三个 lambda 共享同一个 `i` 单元格。循环结束后 `i` 是 2，所以每个 lambda 都返回 2。列表推导式在 Python 3 中有自己的作用域，但三个 lambda 仍然捕获同一个循环变量。

在注册回调时，这个问题更隐蔽：

```python
handlers = {}
for name in ["search", "calc"]:
    handlers[name] = lambda: name

print([h() for h in handlers.values()])   # ['calc', 'calc']
```

两个回调都返回最后一个名字。常见修复有三种：

```python
# 写法一：默认参数在定义时求值，把当前值固定下来
handlers = {}
for name in ["search", "calc"]:
    handlers[name] = lambda name=name: name

# 写法二：用工厂函数为每个值创建独立作用域
def make_handler(name):
    return lambda: name

handlers = {name: make_handler(name) for name in ["search", "calc"]}

# 写法三：用 partial 绑定位置参数
from functools import partial

def handle(name: str) -> str:
    return name

handlers = {name: partial(handle, name) for name in ["search", "calc"]}
```

| 修复方式 | 原理 | 注意事项 |
|----------|------|----------|
| 默认参数 `lambda name=name` | 默认值在函数定义时求值 | 默认值不要用可变对象 |
| 工厂函数 | 每次调用创建新的外层作用域 | 代码多一层，语义最清晰 |
| `functools.partial` | 把当前值绑定为位置参数或关键字参数 | 适合已有函数，不适合复杂 lambda |

late binding 本身不是缺陷，它让闭包可以共享状态。只有在"捕获循环变量"时才会产生反直觉的结果，识别方法是问自己：**这个函数被调用时，变量还是我期望的那个值吗？**

---

## 五、带参数的装饰器

`@retry(times=3)` 比 `@retry` 多了一步：先执行 `retry(times=3)`，得到一个真正的装饰器，再用它包裹函数。即 `call_model = retry(times=3)(call_model)`。因此带参数的装饰器通常有三层：

| 层级 | 函数 | 接收什么 | 返回什么 | 执行时机 |
|------|------|----------|----------|----------|
| 最外层 | `retry(times, delay)` | 装饰器配置 | 一个装饰器 | 定义时求值一次 |
| 中间层 | `decorator(func)` | 被装饰函数 | wrapper | 定义时应用一次 |
| 最内层 | `wrapper(*args, **kwargs)` | 调用参数 | 原函数结果 | 每次调用 |

### 5.1 一个可运行的重试装饰器

```python
import time
from functools import wraps

class TransientError(Exception):
    """模拟可重试的上游错误。"""

def retry(times: int = 3, delay: float = 0.05):
    if times < 1:
        raise ValueError("times 必须大于等于 1")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except TransientError:
                    if attempt == times:
                        raise
                    time.sleep(delay * attempt)
        return wrapper

    return decorator

calls = 0

@retry(times=3, delay=0)
def flaky() -> str:
    global calls
    calls += 1
    if calls < 3:
        raise TransientError("temporary")
    return "ok"

print(flaky(), calls)   # ok 3
```

设计要点：只捕获 `TransientError`，不要把参数错误、编程错误也重试；最后一次失败用裸 `raise` 保留原始 traceback；配置校验放在最外层，让错误在导入时暴露；真实项目还应加入退避上限、抖动和总 deadline，这部分在 04 篇展开。

### 5.2 同时支持带括号和不带括号

标准库的 `lru_cache` 既能写 `@lru_cache`，也能写 `@lru_cache(maxsize=128)`。实现方式是让第一个位置参数既可能是函数，也可能是空：

```python
from functools import wraps

def logged(func=None, *, level: str = "INFO"):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            print(f"[{level}] {fn.__name__}")
            return fn(*args, **kwargs)
        return wrapper

    if func is None:          # 写成 @logged(level="DEBUG")
        return decorate
    return decorate(func)     # 写成 @logged
```

参数列表里的 `*` 让 `level` 成为仅关键字参数，避免把函数误传成 `level`。另外，装饰器配置在定义时就固定了：`@retry(delay=timeout / 10)` 之后修改模块级 `timeout` 不会影响已装饰的函数。如果希望配置可变，应把配置放进 wrapper 每次读取的对象里，例如一个 `Settings` 实例。

---

## 六、类装饰器与可调用对象

"类装饰器"有两种常见含义，面试时要先确认对方指哪一种：

| 说法 | 形态 | 典型用途 |
|------|------|----------|
| 类作为装饰器 | 类实现 `__call__`，用类实例包裹函数 | 需要保存调用次数、缓存、连接等状态 |
| 装饰类 | `@decorator` 作用在 `class` 上 | 注册类、改写类属性、生成新类 |

### 6.1 类作为装饰器

```python
from functools import update_wrapper
from types import MethodType

class CountCalls:
    def __init__(self, func):
        self.func = func
        self.calls = 0
        update_wrapper(self, func)   # 让 __name__、__doc__ 等指向原函数

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return MethodType(self, obj)

@CountCalls
def add(a: int, b: int) -> int:
    return a + b

print(add(1, 2), add.calls)   # 3 1

class Calc:
    @CountCalls
    def double(self, x: int) -> int:
        return x * 2

print(Calc().double(3))       # 6
print(Calc.double.calls)      # 1
```

这里有两个关键点：

- `@CountCalls` 让 `add` 变成一个 `CountCalls` 实例，调用 `add(1, 2)` 实际执行 `__call__`。
- 装饰实例方法时必须实现 `__get__`。普通函数是描述符，访问 `instance.method` 会自动绑定 `self`；而类实例默认不是描述符，不做处理就会出现 `missing 1 required positional argument`。

还要注意状态共享：`Calc.double` 是类属性上的同一个 `CountCalls` 实例，所有 `Calc` 对象共享 `calls`。如果需要按实例计数，应在 `__get__` 中返回绑定到实例的轻量包装，或改用函数装饰器加 `WeakKeyDictionary`。

### 6.2 装饰类

装饰类时，装饰器接收一个类，可以修改它并返回同一个类：

```python
REGISTRY: dict[str, type] = {}

def register(cls):
    REGISTRY[cls.__name__] = cls
    return cls

@register
class WeatherTool:
    pass

print(REGISTRY["WeatherTool"] is WeatherTool)   # True
```

标准库的 `@dataclass` 就是类装饰器：它读取类属性，生成 `__init__`、`__repr__` 等方法。类装饰器也可以返回一个新类，但这会改变类的身份，影响 `isinstance`、序列化和调试，除非确实需要，否则优先"原地修改并返回原类"。如果只是想在子类创建时自动注册，`__init_subclass__` 往往比类装饰器更自然。

### 6.3 闭包还是类

闭包装饰器代码少、返回函数天然支持方法绑定，适合轻量日志、计时和权限；类装饰器状态直观、可继承组合，适合需要多个状态或复杂配置的场景。代价是类装饰器必须自己处理描述符绑定。

---

## 七、functools.wraps 与签名保留

先看一个没有 `wraps` 的装饰器：

```python
import inspect

def timer(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

@timer
def fetch(url: str, timeout: float = 3.0) -> str:
    """抓取一个地址。"""
    return url

print(fetch.__name__)               # wrapper
print(fetch.__doc__)                # None
print(inspect.signature(fetch))     # (*args, **kwargs)
```

加上 `@wraps(fn)` 后，`__name__`、`__doc__`、`__module__`、`__qualname__`、`__annotations__` 等元数据会复制过来，`inspect.signature(fetch)` 也会沿着 `__wrapped__` 找到原签名。

### 7.1 wraps 做了什么，没做什么

`functools.wraps` 本质是 `functools.update_wrapper` 的语法糖，默认复制 `__module__`、`__name__`、`__qualname__`、`__annotations__`、`__doc__`，并更新 `__dict__`，最后写入 `__wrapped__`。

它**不会**改变真实的调用约定。wrapper 仍然接收 `*args, **kwargs`，只是反射工具看到的是原签名。

```python
# 假设已给 timer 的 wrapper 加上 @wraps(fn)，并重新定义 fetch
print(inspect.signature(fetch))                      # (url: str, timeout: float = 3.0) -> str
print(inspect.signature(fetch, follow_wrapped=False))  # (*args, **kwargs)
print(inspect.unwrap(fetch).__name__)                # fetch
```

### 7.2 为什么框架在意签名

- FastAPI 依赖签名做参数解析和依赖注入。
- LangChain 的 `@tool` 依赖签名与类型注解生成工具参数 schema。
- pytest 依赖签名做 fixture 注入。
- 日志和 APM 依赖 `__name__` 归类指标。

如果装饰器丢了签名，这些框架会看到 `(*args, **kwargs)`，轻则参数提示消失，重则工具 schema 为空、请求参数校验失效。因此**凡是包装函数，默认加 `@wraps`**。

### 7.3 自定义复制行为

`update_wrapper` 允许用 `assigned` 和 `updated` 指定要复制或更新的属性。如果包装的是可调用对象而不是函数，它可能没有 `__name__`；`update_wrapper` 会跳过缺失属性，但日志里可能显示 `wrapper`，此时应显式设置一个有意义的名称。

---

## 八、functools.lru_cache 与缓存边界

`lru_cache` 是最常用的"一行装饰器"：它把参数映射到结果，缓存满时按最近最少使用策略淘汰。

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(30))            # 832040
print(fib.cache_info())   # CacheInfo(hits=28, misses=31, maxsize=128, currsize=31)
```

`maxsize=None` 表示不淘汰；Python 3.9+ 可以用 `@cache`，它等价于 `lru_cache(maxsize=None)`。

### 8.1 缓存键的规则

| 规则 | 说明 | 后果 |
|------|------|------|
| 参数必须可哈希 | `list`、`dict`、`set` 不能直接作为参数 | `TypeError: unhashable type` |
| 关键字参数顺序参与键 | `f(a=1, b=2)` 与 `f(b=2, a=1)` 可能是两个条目 | 命中率下降 |
| 默认参数参与键 | 不传和显式传默认值通常键不同 | 缓存被拆成多份 |
| `typed=False` 默认 | `3` 与 `3.0` 可能视为同一个键 | 类型敏感场景要设 `typed=True` |

如果参数是列表，可以先转成元组再传入；如果调用方习惯用不同顺序传关键字参数，最好在进入缓存函数前统一成位置参数，或者再包一层规范化函数。

### 8.2 实例方法上的缓存会持有 self

用 `@lru_cache` 装饰实例方法时，缓存键包含 `self`。实例默认按身份哈希，因此每个实例都有独立缓存，但缓存会一直持有 `self` 的强引用，实例无法被回收，形成事实上的内存泄漏。替代方案包括实例级字典、`@cached_property`、`WeakKeyDictionary`，以及带 TTL 的外部缓存。

### 8.3 不要缓存协程

```python
import asyncio
from functools import lru_cache

@lru_cache(maxsize=None)
async def fetch(url: str) -> str:
    await asyncio.sleep(0)
    return url
```

第一次调用 `fetch(url)` 返回一个协程对象并被缓存；`await` 之后协程已经结束。第二次调用拿到同一个协程对象，再次 `await` 会抛出 `RuntimeError: cannot reuse already awaited coroutine`。异步场景应缓存**最终数据**，或使用支持异步的缓存库。

### 8.4 其他边界

- 函数抛异常时不会写入缓存，下一次仍会重新执行。
- CPython 的 `lru_cache` 内部有锁，多线程下不会破坏缓存结构，但并发未命中时底层函数可能被执行多次。
- 没有内置 TTL，也没有跨进程共享；需要过期策略时应在缓存函数外再包一层时间戳判断，或使用专门库。
- `cache_clear()` 用于测试或配置变更后手动失效；`cache_info()` 用于观测命中率。

---

## 九、functools.partial 与 singledispatch

### 9.1 partial：预绑定部分参数

`partial` 把一个可调用对象和一部分参数固定下来，返回新的可调用对象。它适合"同一个工具，不同默认配置"的场景。

```python
from functools import partial

def call_tool(name: str, query: str, timeout: float = 5.0) -> str:
    return f"{name}({query}) timeout={timeout}"

search = partial(call_tool, "search", timeout=2.0)
print(search("python"))          # search(python) timeout=2.0
print(search.func.__name__)      # call_tool
print(search.args)               # ('search',)
print(search.keywords)           # {'timeout': 2.0}
```

与 lambda 相比，`partial` 直接表达"绑定参数"，保留 `.func`、`.args`、`.keywords` 元数据，函数和参数可序列化时还能 pickle；lambda 更适合简单的一次性表达式。`partial` 默认没有 `__name__`，需要元数据时可以用 `functools.update_wrapper` 再包一层。类方法场景可以使用 `functools.partialmethod`，它让绑定发生在属性访问时，而不是类定义时。

### 9.2 singledispatch：按第一个参数的类型分派

Agent 拿到的工具结果可能是字符串、字典、列表或自定义对象，渲染逻辑通常按类型不同。`singledispatch` 用类型注解注册实现，避免一长串 `isinstance`。

```python
from functools import singledispatch

@singledispatch
def render(result: object) -> str:
    return repr(result)

@render.register
def _(result: str) -> str:
    return result

@render.register
def _(result: dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in result.items())

@render.register
def _(result: list) -> str:
    return "\n".join(render(item) for item in result)

print(render({"city": "Hangzhou", "temp": 24}))
# city=Hangzhou, temp=24
print(render([{"city": "Hangzhou"}, "ok"]))
# city=Hangzhou
# ok
```

规则与边界：只按**第一个参数**的类型分派；查找遵循类型的 MRO，找不到时回退到基类注册，最终回退到 `object`；可以用 `@render.register(str)` 显式指定类型，也可以省略参数让注解生效；方法版本用 `@singledispatchmethod`（Python 3.8+），并且它必须是最外层的装饰器；Python 3.11 起支持用 `int | str` 这样的联合类型注册，3.10 需要分别注册。

---

## 十、描述符与 property 的关系

描述符是"控制属性访问"的协议。一个类只要实现了 `__get__`、`__set__` 或 `__delete__`，它的实例就可以作为另一个类的类属性，接管属性读写。

| 类型 | 实现的方法 | 优先级 | 例子 |
|------|------------|--------|------|
| 数据描述符 | `__get__` + `__set__` 或 `__delete__` | 高于实例 `__dict__` | `property` |
| 非数据描述符 | 只有 `__get__` | 低于实例 `__dict__` | 普通函数、`cached_property` |

数据描述符的典型实现是 `__set_name__` 记录属性名、`__get__` 读取实例字典、`__set__` 做校验后写入。`property` 则是标准库替我们写好的数据描述符：

```python
class ModelConfig:
    def __init__(self, temperature: float):
        self.temperature = temperature

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        if not 0 <= value <= 2:
            raise ValueError("temperature 必须在 0 到 2 之间")
        self._temperature = value

cfg = ModelConfig(0.7)
print(cfg.temperature)   # 0.7
# cfg.temperature = 3    # ValueError
```

关系可以这样理解：

1. `@property` 是一个装饰器，它把方法包装成 `property` 对象。
2. `property` 对象是数据描述符，所以 `cfg.temperature` 会调用 `fget`，赋值会调用 `fset`。
3. `@temperature.setter` 并没有修改原来的 property，而是返回一个带 `fset` 的新 property 对象，再绑定回类属性。
4. 普通函数是非数据描述符，所以 `obj.method` 会自动生成绑定方法；类装饰器实例如果要装饰方法，也必须实现 `__get__`。

`functools.cached_property`（Python 3.8+）是非数据描述符：第一次访问时计算结果并写入实例 `__dict__`，之后直接从实例字典读取。它没有 setter，可以被同名实例属性覆盖，适合"计算一次、对象生命周期内复用"的派生属性。

---

## 十一、用装饰器写回调与注册表

回调注册是装饰器最朴素的用法：函数定义时把自己登记到一个字典里，运行时按事件名查找。

```python
from collections.abc import Callable

CALLBACKS: dict[str, Callable[..., str]] = {}

def on(event: str):
    def register(fn: Callable[..., str]) -> Callable[..., str]:
        if event in CALLBACKS:
            raise ValueError(f"事件重复注册: {event}")
        CALLBACKS[event] = fn
        return fn
    return register

@on("start")
def handle_start() -> str:
    return "started"

print(CALLBACKS["start"]())   # started
```

这里装饰器返回原函数，而不是 wrapper。注册表已经保存了函数引用，调用方仍可以直接调用 `handle_start()`，不需要额外包装。**只有当需要改变调用行为时才返回 wrapper**。

### 11.1 工具元数据装饰器

Agent 工具通常需要名称、描述和参数 schema。可以先用装饰器把元数据挂在函数上，再由注册中心统一读取：

```python
import inspect

def tool(description: str):
    def decorate(fn):
        sig = inspect.signature(fn)
        fn.tool_schema = {
            "name": fn.__name__,
            "description": description,
            "parameters": {
                name: getattr(param.annotation, "__name__", str(param.annotation))
                for name, param in sig.parameters.items()
                if param.annotation is not inspect.Parameter.empty
            },
        }
        return fn
    return decorate

@tool("查询指定城市的天气")
def weather(city: str, days: int = 1) -> str:
    return f"{city}: {days} 天"

print(weather.tool_schema["name"])   # weather
```

这是简化版。真实框架还要处理默认值、必填项、联合类型、嵌套模型和 JSON Schema 描述。但核心机制不变：**装饰器在定义时读取签名，把元数据附着到函数对象上**。

### 11.2 注册表的工程细节

在装饰器里检测重复注册并抛错，避免静默覆盖；把注册表放在独立模块以规避循环导入；提供清空或快照机制保证测试隔离；执行器逐个调用回调时捕获并记录异常，避免一个回调拖垮整条链。

回调注册的副作用发生在导入阶段。如果某个工具模块没有被导入，它的装饰器就不会执行，注册表里也就没有它。这是"装饰器注册"最常见的线上问题，排查时先确认模块是否被加载。

---

## 十二、用装饰器写中间件

中间件是装饰器最贴近 Agent 的用法：它包住一个 handler，在调用前后插入逻辑，形成洋葱模型。

```python
from functools import wraps

def with_logging(handler):
    @wraps(handler)
    def wrapper(request: dict) -> dict:
        print("->", request)
        response = handler(request)
        print("<-", response)
        return response
    return wrapper

def with_retry(handler):
    @wraps(handler)
    def wrapper(request: dict) -> dict:
        for attempt in range(3):
            try:
                return handler(request)
            except TimeoutError:
                if attempt == 2:
                    raise
        raise RuntimeError("unreachable")
    return wrapper

def call_model(request: dict) -> dict:
    if request.get("fail"):
        raise TimeoutError("model timeout")
    return {"text": "ok"}

pipeline = with_logging(with_retry(call_model))
print(pipeline({"prompt": "hi"}))
```

输出顺序是 `-> 请求`、`<- 响应`、最后才是返回值。`with_logging` 在最外层，所以它最先看到请求、最后看到响应；`with_retry` 在内层，只负责重试真正调用模型的那一段。用 `@` 写法时，把 `@with_logging` 放在 `@with_retry` 上方即可得到同样的结构。

### 12.1 wrap 型与 hook 型

LangChain 1.x 的中间件同时提供两类接口，理解它们的差别很重要：

| 形态 | 装饰器返回什么 | 控制流 | 适合做什么 |
|------|----------------|--------|------------|
| wrap 型 | 包装函数，包住 handler | 可以改写请求、短路、重试、捕获异常 | 日志、重试、权限、限流 |
| hook 型 | 原函数，附加阶段标记 | 运行时在固定阶段调用，不直接包住 handler | 注入系统提示、审计、状态更新 |

hook 型装饰器通常只做注册：

```python
def before_model(fn):
    fn.__hook__ = "before_model"
    return fn

@before_model
def inject_system_prompt(state: dict) -> dict:
    state["messages"].insert(0, {"role": "system", "content": "你是严谨的助手"})
    return state
```

运行时收集所有带 `__hook__` 标记的函数，在模型调用前依次执行。它不返回 wrapper，因此不能像 wrap 型那样直接控制"是否继续调用模型"；需要短路时应使用 wrap 型。

### 12.2 顺序决定语义

假设 `with_auth` 已经定义，这里只关注两个装饰器的相对位置：

```python
@with_retry
@with_auth
def call_tool():
    return "ok"
```

上面的顺序表示"认证在重试内部"：每次重试都会重新认证。如果认证失败也抛出 `TimeoutError` 之类的可重试异常，就会做无意义的重试。把两个装饰器对调，则变成"认证只做一次，重试只包住工具调用"，多数场景这才是期望行为。

| 顺序 | 请求方向 | 响应方向 | 典型语义 |
|------|----------|----------|----------|
| `@A` 在 `@B` 上 | A 先执行 | A 后执行 | A 是外层，适合总入口日志、总超时 |
| `@B` 在 `@A` 上 | B 先执行 | B 后执行 | B 是内层，适合单次调用重试 |

写中间件前先画一遍"谁包谁"，比事后排查重复认证、重复计费要省事得多。

---

## 十三、异步装饰器与上下文传递

Agent 的模型调用、工具调用、流式输出大多是异步的。给 `async def` 函数加装饰器时，wrapper 也必须是 `async def`，否则调用方拿到的是协程对象而不是结果。

```python
import asyncio
from functools import wraps

def async_timed(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        start = loop.time()
        try:
            return await fn(*args, **kwargs)
        finally:
            elapsed = loop.time() - start
            print(f"{fn.__name__}: {elapsed:.4f}s")
    return wrapper

@async_timed
async def fake_model_call() -> str:
    await asyncio.sleep(0.01)
    return "ok"

print(asyncio.run(fake_model_call()))
```

`finally` 保证即使模型调用抛异常或任务被取消，耗时也会被记录。

### 13.1 同时支持同步与异步

一个装饰器要同时兼容两种函数，必须用 `inspect.iscoroutinefunction(fn)` 在定义时判断类型：异步分支返回 `async def` wrapper 并 `await fn(*args, **kwargs)`，同步分支返回普通 wrapper。不要用同步 wrapper 包异步函数，也不要用 `async def` wrapper 包同步函数。前者的返回值是协程，后者的调用方需要额外 `await`，都会改变调用契约。

### 13.2 用 ContextVar 传递请求上下文

异步任务之间共享全局变量会串数据。`contextvars.ContextVar` 为每个任务保存独立副本，适合放 request id、用户 id、trace id。

```python
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="-")

def with_request_id(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        rid = kwargs.pop("request_id", "-")
        token = request_id.set(rid)
        try:
            return await fn(*args, **kwargs)
        finally:
            request_id.reset(token)
    return wrapper

@with_request_id
async def handle(prompt: str) -> str:
    return f"{request_id.get()}: {prompt}"

print(asyncio.run(handle("hi", request_id="req-1")))   # req-1: hi
```

`reset(token)` 必须放在 `finally` 里，否则上下文会泄漏到同一任务的后续调用。

### 13.3 异步超时

Python 3.11+ 提供 `asyncio.timeout`：

```python
async def call_with_timeout(coro, seconds: float):
    async with asyncio.timeout(seconds):
        return await coro
```

Python 3.10 可以使用 `asyncio.wait_for(coro, timeout=seconds)`。两者都会在超时时取消内部任务并抛出 `TimeoutError`（3.10 的 `asyncio.TimeoutError` 与内置 `TimeoutError` 的关系随版本变化，捕获时以实际运行版本为准）。

取消会以 `asyncio.CancelledError` 的形式进入被取消的协程。它继承自 `BaseException`，所以 `except Exception` 不会误吞它；清理逻辑应放在 `finally` 或异步上下文管理器中。

---

## 十四、常见坑与根因分析

| 坑 | 现象 | 根因 | 修复 |
|----|------|------|------|
| late binding | 循环里注册的回调都使用最后一个值 | 闭包捕获变量单元格，调用时才取值 | 默认参数、工厂函数或 `partial` 固定当前值 |
| 可变默认参数 | 多次调用共享同一个列表 | 默认值在定义时求值一次，保存在 `__defaults__` | 用 `None` 作哨兵，函数体内创建新对象 |
| wraps 丢失 | `__name__` 变成 `wrapper`，框架参数解析为空 | 新 wrapper 没有复制原函数元数据 | 统一加 `@functools.wraps(fn)` |
| 装饰器顺序 | 认证失败仍被重试三次 | 重试装饰器包住了认证 | 认证放外层，或缩小重试捕获范围 |
| 类装饰器方法绑定 | `missing 1 required positional argument: 'self'` | 类实例不是描述符，不会绑定实例 | 实现 `__get__` 返回 `MethodType`，或改用函数 |
| 同步异步混用 | 拿到协程对象或 "coroutine was never awaited" | wrapper 的同步性与原函数不一致 | 用 `inspect.iscoroutinefunction` 分支 |

其中可变默认参数最容易被面试官追问，单独看一个例子：

```python
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item(1))   # [1]
print(add_item(2))   # [1, 2]
```

默认参数陷阱和 late binding 常被混为一谈：前者是"默认值只算一次"，后者是"闭包按名字延迟取值"，两者的修复方式也不同。

---

## 十五、高频面试题（10 道）

### 1. 装饰器的本质是什么？`@decorator` 等价于什么？

**答案：** 装饰器是接收可调用对象并返回可调用对象的高阶函数。`@decorator` 写在 `def f` 上方，等价于在函数定义后执行 `f = decorator(f)`。装饰动作发生在定义时，调用时执行的是装饰器返回的 wrapper。多个装饰器从下往上应用，`@a` 在 `@b` 上方等价于 `a(b(f))`。

### 2. 什么是闭包？LEGB 的查找顺序是什么？

**答案：** 闭包是内层函数加上它引用的外层函数变量。外层函数返回后，这些变量保存在 cell 中，内层函数仍可读写。LEGB 指 Local、Enclosing、Global、Built-in，自内向外查找，命中即停。函数内只要对某个名字赋值，该名字默认就是局部变量；要修改外层函数变量用 `nonlocal`，修改模块变量用 `global`。

### 3. 为什么 `[lambda: i for i in range(3)]` 调用后都是 2？如何修复？

**答案：** 闭包捕获的是变量单元格而不是创建时的值，三个 lambda 共享同一个 `i`，循环结束后 `i` 为 2，调用时才取值，所以都返回 2。修复方式有三种：用默认参数 `lambda i=i: i` 在定义时固定值；用工厂函数为每个值创建独立作用域；用 `functools.partial` 绑定当前值。默认参数方案要注意不要用可变对象作为默认值。

### 4. 带参数的装饰器为什么要三层？`@retry(times=3)` 如何展开？

**答案：** `@retry(times=3)` 先执行 `retry(times=3)`，它必须返回一个真正的装饰器，再由这个装饰器接收函数并返回 wrapper，所以至少需要"配置层、装饰层、调用层"三层。展开式是 `call_model = retry(times=3)(call_model)`。最外层在定义时执行一次，负责校验配置；中间层在应用装饰器时执行一次；最内层每次调用执行。

### 5. `functools.wraps` 做了什么？不写会怎样？

**答案：** `wraps` 复制原函数的 `__module__`、`__name__`、`__qualname__`、`__annotations__`、`__doc__`，更新 `__dict__`，并写入 `__wrapped__`。不写时，被装饰函数的 `__name__` 变成 `wrapper`、文档丢失，`inspect.signature` 看到的是 `(*args, **kwargs)`。FastAPI、LangChain 工具 schema、pytest fixture 等依赖签名的框架会因此解析失败。`wraps` 只影响元数据和反射，不改变 wrapper 实际接收 `*args, **kwargs` 的调用方式。

### 6. 多个装饰器的执行顺序是什么？

**答案：** 应用顺序从下往上：`@a` 在 `@b` 上方等价于 `a(b(f))`，`b` 先包裹原函数，`a` 再包裹结果。调用时请求从最外层 `a` 进入，响应从 `a` 离开；最内层最接近原函数。顺序决定语义，例如把重试放在认证外层会导致认证失败也被重试。装饰器表达式本身的求值顺序是从上到下，但应用顺序是从下到上。

### 7. 类装饰器和函数装饰器有什么区别？装饰实例方法要注意什么？

**答案：** 函数装饰器用闭包保存状态，返回函数；类装饰器让类实现 `__call__`，用实例保存状态，可继承、可组合，但代码更多。类实例默认不是描述符，直接装饰实例方法后，通过对象访问不会自动绑定 `self`，会报缺少参数。解决办法是实现 `__get__`，在 `obj` 不为 `None` 时返回 `MethodType(self, obj)`；也可以改用函数装饰器。另外要注意类装饰器实例是类属性，多个实例会共享同一份状态。

### 8. `lru_cache` 的原理和限制是什么？能用在 async 函数上吗？

**答案：** `lru_cache` 用参数构建缓存键，命中直接返回，未命中调用函数并写入；缓存满时淘汰最久未使用的条目。参数必须可哈希，关键字参数顺序会影响键，实例方法的键包含 `self` 并会强引用实例，可能造成内存泄漏。它不缓存异常，也没有 TTL 和跨进程共享。不能直接用于 `async def`：它缓存的是协程对象，第二次 `await` 同一个协程会报 "cannot reuse already awaited coroutine"，应缓存最终数据或使用异步缓存库。

### 9. `property` 和描述符是什么关系？

**答案：** 描述符是实现了 `__get__`、`__set__` 或 `__delete__` 的类，用于接管属性访问。`property` 是标准库提供的数据描述符：`@property` 把方法包装成 property 对象，访问属性触发 `fget`，赋值触发 `fset`。数据描述符优先于实例 `__dict__`，所以 property 能拦截赋值；普通函数是非数据描述符，只实现 `__get__`，因此实例字典可以覆盖同名属性，而方法访问会自动绑定 `self`。`cached_property` 则是非数据描述符，把结果写进实例字典。

### 10. 如何用装饰器实现 Agent 中间件？wrap 型和 hook 型有什么区别？

**答案：** wrap 型装饰器接收 handler，返回一个包住 handler 的 wrapper，可以在调用前改写请求、调用后改写响应，也可以短路、重试、捕获异常；多个 wrap 型按 `@` 顺序形成洋葱模型。hook 型装饰器通常只给函数打阶段标记并返回原函数，运行时由框架在 `before_model`、`after_model` 等阶段统一调用，适合注入提示、审计和状态更新，但不能直接包住 handler 控制是否继续。实现时要保留 `@wraps`、区分同步与异步、只捕获明确异常，并想清楚每一层的顺序。

---

## 十六、避坑指南

### 坑1：`@decorator` 忘了括号

**错误现象：** 使用 `@retry` 而不是 `@retry(times=3)` 时，函数被替换成"装饰器工厂"本身，调用时报参数错误或返回意料之外的对象。

**产生原因：** 带参数的装饰器外层只接收配置，不接收函数。`@retry` 把函数传给了 `times`，返回的是 `decorator`，原函数从未被包裹。

**正确做法：** 统一写成 `@retry(times=3)`；如果希望两种写法都支持，使用第五节的 `func=None` 可选参数模式。

### 坑2：包装函数不写 `functools.wraps`

**错误现象：** 日志里所有函数都叫 `wrapper`；FastAPI 把参数当成未知字段；LangChain 生成的工具 schema 为空。

**产生原因：** 装饰器返回新函数后，原函数的元数据没有复制，框架通过反射看到的是 wrapper 的 `*args, **kwargs`。

**正确做法：** 每个 wrapper 都加 `@wraps(fn)`，并在测试中断言 `decorated.__name__ == original.__name__`、`inspect.signature` 与原文一致。第七节的 `timer` 加上 `@wraps(fn)` 就是最小修复。

### 坑3：在循环里创建闭包

**错误现象：** 批量注册的工具或回调全部使用最后一个配置。

**产生原因：** 闭包延迟绑定，循环变量在调用时才取值。

**正确做法：** 用工厂函数为每个值创建独立作用域，或用默认参数、`partial` 固定当前值。写完循环后加一条断言，分别调用两个回调确认返回值不同。

### 坑4：把 `lru_cache` 用在 async 函数或实例方法上

**错误现象：** 异步函数第二次调用报 "cannot reuse already awaited coroutine"；实例方法缓存后内存持续增长。

**产生原因：** `lru_cache` 缓存的是函数返回值，而 `async def` 的返回值是协程对象；实例方法的缓存键包含 `self`，缓存强引用实例。

**正确做法：** 异步函数缓存最终数据；实例方法用实例级字典、`cached_property` 或弱引用缓存；为缓存设置明确的上限和失效策略。

### 坑5：装饰器顺序随缘

**错误现象：** 认证失败被重试三次；日志里一次请求打印了两遍；限流器统计的是重试后的次数。

**产生原因：** `@` 的应用顺序是从下往上，外层装饰器包住内层，重试、认证、日志的职责边界没有画清楚。

**正确做法：** 先画调用链，再决定顺序。通常总超时、总日志在最外层，认证在重试外层，单次调用重试靠近原函数。用两个会打印的装饰器做一次最小实验，确认请求与响应的方向。

### 坑6：类装饰器装饰实例方法后 `self` 消失

**错误现象：** `TypeError: method() missing 1 required positional argument: 'self'`。

**产生原因：** 类实例不是描述符，属性访问时不会自动绑定实例，方法调用把第一个业务参数当成了 `self`。

**正确做法：** 实现 `__get__`，返回 `MethodType(self, obj)`；或者改用函数装饰器。还要确认状态是按类共享还是按实例隔离。完整写法见第六节的 `CountCalls`。

---

## 十七、本章学习自检

### 函数对象与闭包

- [ ] 能说出函数作为一等对象的四种用法，并各举一个例子
- [ ] 能解释 `@decorator` 与 `f = decorator(f)` 的等价关系
- [ ] 能画出 LEGB 的查找顺序，并说明什么情况下会触发 `UnboundLocalError`
- [ ] 能写一个带 `nonlocal` 的闭包计数器
- [ ] 能解释闭包捕获的是变量而不是值

### 装饰器语法

- [ ] 能默写一个带 `@wraps` 的计时装饰器
- [ ] 能解释多个装饰器的应用顺序和调用方向
- [ ] 能写出带参数装饰器的三层结构
- [ ] 能实现同时支持 `@decorator` 和 `@decorator(...)` 的可选参数模式
- [ ] 能用类实现一个有状态的装饰器，并知道方法绑定问题

### functools 与描述符

- [ ] 能说出 `wraps` 复制了哪些属性，以及它不改变什么
- [ ] 能解释 `lru_cache` 的缓存键规则和三个以上限制
- [ ] 会用 `partial` 预绑定参数，知道它和 lambda 的差别
- [ ] 会用 `singledispatch` 按类型分派，知道它只看第一个参数
- [ ] 能解释 `property` 为什么是数据描述符，以及 `cached_property` 的区别

### Agent 工程实践

- [ ] 能用装饰器实现工具注册表，并处理重复注册
- [ ] 能用装饰器实现日志、重试、权限三类中间件
- [ ] 能说清 wrap 型与 hook 型中间件的差别
- [ ] 能写出同步与异步通用的装饰器
- [ ] 能用 `ContextVar` 在异步调用链中传递 request id

---

> 返回 [模块目录](../../README.md) | 下一篇 [04-Python异常与上下文管理](./04-Python异常与上下文管理.md)
