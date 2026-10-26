# Python 异常与上下文管理：从错误分层到 Agent 资源治理

> Agent 的日常不是"一次调用成功"，而是"模型超时、工具报错、流中断、用户取消"之后系统还能不能给出可解释的结果。异常决定错误如何传播，上下文管理器决定资源如何释放，两者共同构成 Agent 的失败处理骨架。
>
> 本文从异常模型讲到 `contextlib`、`async with` 与重试/超时模式。示例面向 Python 3.10 及以上版本，只使用标准库；涉及版本差异的地方会单独标注。

> 参考资料：
> - [Python 教程：错误和异常](https://docs.python.org/zh-cn/3/tutorial/errors.html)
> - [Python 标准库：内置异常](https://docs.python.org/zh-cn/3/library/exceptions.html)
> - [Python 标准库：contextlib](https://docs.python.org/zh-cn/3/library/contextlib.html)
> - [Python 标准库：asyncio 同步原语](https://docs.python.org/zh-cn/3/library/asyncio-sync.html)
> - [PEP 654：ExceptionGroup 与 except*](https://peps.python.org/pep-0654/)
> - [Python 标准库：traceback](https://docs.python.org/zh-cn/3/library/traceback.html)

---

## 目录

- [一、为什么 Agent 系统更需要异常与上下文管理](#一为什么-agent-系统更需要异常与上下文管理)
- [二、异常模型：BaseException 与 Exception](#二异常模型baseexception-与-exception)
- [三、EAFP 与 LBYL](#三eafp-与-lbyl)
- [四、try/except/else/finally 的执行顺序](#四tryexceptelsefinally-的执行顺序)
- [五、raise 与异常链](#五raise-与异常链)
- [六、自定义异常与业务错误分层](#六自定义异常与业务错误分层)
- [七、异常包装与转换的边界](#七异常包装与转换的边界)
- [八、上下文管理器协议](#八上下文管理器协议)
- [九、contextlib.contextmanager](#九contextlibcontextmanager)
- [十、contextlib 常用工具](#十contextlib-常用工具)
- [十一、ExitStack 与动态资源管理](#十一exitstack-与动态资源管理)
- [十二、异步上下文管理器 async with](#十二异步上下文管理器-async-with)
- [十三、重试、超时与资源清理模式](#十三重试超时与资源清理模式)
- [十四、常见坑与根因分析](#十四常见坑与根因分析)
- [十五、高频面试题（10 道）](#十五高频面试题10-道)
- [十六、避坑指南](#十六避坑指南)
- [十七、本章学习自检](#十七本章学习自检)

---

## 一、为什么 Agent 系统更需要异常与上下文管理

普通脚本的错误往往意味着"程序应该停下来"；Agent 的错误更多是"这一次工具调用失败了，但整个会话还可以继续"。把失败分类、按层转换，并保证每条退出路径都释放资源，是 Agent 可靠性的基础。

| 失败类型 | 典型例子 | 期望处理 |
|----------|----------|----------|
| 工具参数不合法 | 模型给了不存在的城市名 | 转换成工具输入错误，作为 observation 返回给模型修正 |
| 工具暂时不可用 | 上游 502、连接超时 | 识别为可重试错误，退避后重试 |
| 工具永久失败 | 权限不足、资源不存在 | 终止该工具调用，向模型或用户报告 |
| 模型超时或限流 | 推理服务响应慢 | 重试、降级模型或缩短上下文 |
| 用户主动取消 | 前端点击停止 | 传播取消信号，停止循环并清理资源 |
| 流或会话中断 | SSE 断开、文件句柄未关 | 用上下文管理器或 `finally` 释放 |

两条原则贯穿全文：

1. **异常按层转换**：底层库的异常在适配层转换成领域异常，业务层只处理自己能处理的类型。
2. **资源按作用域释放**：谁打开谁关闭，优先用 `with` 或 `async with`，不要依赖垃圾回收。

---

## 二、异常模型：BaseException 与 Exception

Python 的异常是一棵类继承树，根是 `BaseException`：

```text
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── ArithmeticError
    │   └── ZeroDivisionError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── OSError
    │   ├── FileNotFoundError
    │   └── TimeoutError
    ├── RuntimeError
    ├── ValueError
    └── StopIteration
```

| 异常 | 含义 | 是否应该捕获 |
|------|------|--------------|
| `Exception` | 常规业务和运行时错误 | 按需捕获，不要无差别吞掉 |
| `SystemExit` | 解释器退出 | 通常不捕获 |
| `KeyboardInterrupt` | 用户按下 Ctrl+C | 通常不捕获，交给进程退出 |
| `GeneratorExit` | 生成器被关闭 | 只做清理，不再 `yield` |
| `asyncio.CancelledError` | 任务被取消 | Python 3.8 起继承 `BaseException`，只在清理后重新抛出 |
| `ExceptionGroup` | 一次抛出多个异常 | Python 3.11+，用 `except*` 分组处理 |

`except Exception` 不会捕获 `KeyboardInterrupt`、`SystemExit` 和 `CancelledError`，这是好事。裸 `except:` 等价于 `except BaseException:`，会把取消和退出信号也吞掉，在 Agent 服务里尤其危险。

```python
def parse_age(text: str) -> int:
    try:
        return int(text)
    except (TypeError, ValueError) as exc:
        print(f"输入不合法: {exc}")
        return 0

print(parse_age("18"))   # 18
print(parse_age("x"))    # 输入不合法，返回 0
```

### 2.1 ExceptionGroup 与 except*

批量调用多个工具时，可能同时出现多个失败。Python 3.11 引入 `ExceptionGroup` 和 `except*`：

```python
try:
    raise ExceptionGroup("批量工具失败", [ValueError("参数错误"), TypeError("类型错误")])
except* ValueError as group:
    print("value errors:", len(group.exceptions))
except* TypeError as group:
    print("type errors:", len(group.exceptions))
```

`except*` 会把匹配的子异常从组里取出，未匹配的继续向外传播。Python 3.10 没有这个语法，只能用循环收集异常再统一处理。`BaseExceptionGroup` 可以同时容纳 `Exception` 和 `BaseException` 子类，但通常只在框架层使用。

---

## 三、EAFP 与 LBYL

EAFP 是"先做，出错再处理"（Easier to Ask Forgiveness than Permission）；LBYL 是"先检查，再执行"（Look Before You Leap）。

| 风格 | 写法 | 优点 | 风险 |
|------|------|------|------|
| EAFP | `try` 读取键 + `except KeyError` | 一次操作完成，避免检查与使用之间的竞态 | 异常路径也是控制流，滥用会降低可读性 |
| LBYL | `if "key" in data: data["key"]` | 意图直观，适合用户输入校验 | 检查和执行之间状态可能变化 |

```python
data = {"city": "Hangzhou"}

# LBYL
if "temp" in data:
    temp = data["temp"]
else:
    temp = None

# EAFP
try:
    temp = data["temp"]
except KeyError:
    temp = None

print(temp)   # None
```

LBYL 的经典问题是 TOCTOU（Time-of-check to time-of-use）：

```python
from pathlib import Path

path = Path("config.json")
if path.exists():          # 检查
    text = path.read_text()  # 文件可能在这之间被删除
```

更稳妥的写法是直接操作并捕获异常：

```python
try:
    text = path.read_text(encoding="utf-8")
except FileNotFoundError:
    text = "{}"
```

选择建议：

- 用户输入、API 参数、模型生成的工具参数：用 LBYL 或 schema 校验，尽早给出可读错误。
- 文件、网络、数据库等外部资源：用 EAFP，操作本身才是权威判断。
- 异常很少发生且操作代价低：EAFP 更简洁；异常频繁发生或属于正常分支：LBYL 更清晰。

---

## 四、try/except/else/finally 的执行顺序

| 子句 | 何时执行 | 捕获范围 |
|------|----------|----------|
| `try` | 总是先执行 | 自身抛出的异常交给后面的 `except` |
| `except` | `try` 中抛出匹配异常时 | 只捕获 `try` 块的异常，不捕获 `else` 的异常 |
| `else` | `try` 没有异常时 | 这里的异常不会被同一个 `try` 的 `except` 捕获 |
| `finally` | 无论是否异常、是否 `return` | 总在离开 `try` 语句前执行 |

```python
def demo(x: int):
    try:
        print("try")
        result = 10 // x
    except ZeroDivisionError:
        print("except")
        return "error"
    else:
        print("else")
        return result
    finally:
        print("finally")

print(demo(2))
print("---")
print(demo(0))
```

输出：

```text
try
else
finally
5
---
try
except
finally
error
```

几个容易出错的细节：

1. `else` 适合放"只有 `try` 成功后才执行、但不希望被本层 `except` 捕获"的逻辑。
2. `finally` 在 `return` 之前执行；如果 `finally` 里也 `return`，它会覆盖原来的返回值，并吞掉正在传播的异常。
3. `finally` 里的 `break`、`continue` 同样会丢弃在途异常。
4. `return` 的值在进入 `finally` 之前就已经确定，`finally` 中重新绑定局部变量不会改变返回值，但修改可变对象会影响返回内容。

```python
def mask_error():
    try:
        raise ValueError("original")
    finally:
        return "masked"

print(mask_error())   # masked，ValueError 被吞掉
```

这类写法应视为 bug，静态检查工具通常会给出警告。清理逻辑只做清理，不要在 `finally` 里改变控制流。

---

## 五、raise 与异常链

`raise` 有四种常见形态：

| 写法 | 作用 |
|------|------|
| `raise ValueError("bad")` | 抛出新的异常实例 |
| `raise` | 重新抛出当前正在处理的异常，保留原 traceback |
| `raise NewError(...) from exc` | 抛出 NewError，并把 `exc` 设为显式原因 |
| `raise NewError(...) from None` | 抛出 NewError，并抑制上下文的自动展示 |

```python
import json

class ToolError(Exception):
    pass

def parse_payload(payload: str) -> dict:
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ToolError("工具返回的不是合法 JSON") from exc

try:
    parse_payload("{bad")
except ToolError as exc:
    print(type(exc).__name__)            # ToolError
    print(type(exc.__cause__).__name__)  # JSONDecodeError
    print(exc.__suppress_context__)      # True
```

异常链有三个关键属性：

| 属性 | 含义 | 何时设置 |
|------|------|----------|
| `__cause__` | 显式原因 | 使用 `raise ... from exc` 时 |
| `__context__` | 隐式上下文 | 在处理另一个异常时又抛出异常，自动设置 |
| `__suppress_context__` | 是否隐藏上下文 | `from exc` 或 `from None` 时设为 True |

即使不写 `from exc`，在 `except` 块里 `raise NewError(...)` 也会自动把原异常放进 `__context__`。区别在于 `from exc` 表达"这是直接原因"，traceback 会显示 "The above exception was the direct cause of the following exception"；`from None` 则告诉解释器不要展示上下文。

`from None` 不是"清理异常"，只是"隐藏展示"。如果直接丢掉原因，排障时只剩一句用户友好的文案。正确做法通常是先记录原始异常，再在最终边界用 `from None` 或只返回错误码。

Python 3.11+ 可以用 `add_note` 给异常补充上下文：

```python
try:
    values = [1, 2]
    print(values[5])
except IndexError as exc:
    exc.add_note("tool=lookup; index=5")
    raise
```

`__notes__` 会出现在 traceback 中。3.10 及以下只能用日志或自定义属性达到类似效果。

---

## 六、自定义异常与业务错误分层

一个可维护的 Agent 异常体系通常包含三层：框架/传输层异常、工具领域异常、模型领域异常。业务代码只依赖领域异常，不直接依赖某个 HTTP 客户端或 SDK 的异常。

```python
class AgentError(Exception):
    """Agent 业务异常基类。"""

class ToolError(AgentError):
    def __init__(self, tool: str, message: str, *, retryable: bool = False):
        super().__init__(f"[{tool}] {message}")
        self.tool = tool
        self.retryable = retryable

class ToolInputError(ToolError):
    pass

class RetryableToolError(ToolError):
    def __init__(self, tool: str, message: str):
        super().__init__(tool, message, retryable=True)

class FatalToolError(ToolError):
    pass

class ModelError(AgentError):
    pass

class ModelTimeoutError(ModelError):
    pass

err = RetryableToolError("weather", "上游超时")
print(str(err))          # [weather] 上游超时
print(err.retryable)     # True
```

| 层级 | 代表异常 | 处理策略 | 是否展示给模型 |
|------|----------|----------|----------------|
| 工具输入错误 | `ToolInputError` | 作为 observation 返回，让模型修正参数 | 是，文案要具体 |
| 可重试工具错误 | `RetryableToolError` | 退避重试，超过次数后上报 | 可选，简短说明 |
| 致命工具错误 | `FatalToolError` | 终止该工具链，记录完整原因 | 是，但不要暴露内部细节 |
| 模型超时/限流 | `ModelTimeoutError` | 重试、降级或缩短上下文 | 视产品策略而定 |
| 用户取消 | `CancelledError` | 停止循环，清理资源，不重试 | 否 |
| 编程错误 | `TypeError`、`AttributeError` | 不转换成业务错误，暴露 bug | 否 |

设计原则：

- 继承 `Exception` 而不是 `BaseException`，避免破坏解释器的退出和取消语义。
- 自定义 `__init__` 时调用 `super().__init__(message)`，保证 `str(exc)` 和 `args` 有意义。
- 异常树保持浅，优先用 `code`、`retryable` 等属性表达差异。层级过深会让序列化和跨进程传递变复杂。
- 不要在异常里保存不可序列化的对象（连接、锁、生成器），否则日志、队列和 RPC 都会出问题。
- 用 dataclass 定义异常时要小心：多个字段会让 `str(exc)` 变成元组风格，最好显式实现 `__str__` 或手写 `__init__`。

---

## 七、异常包装与转换的边界

异常转换应该发生在系统边界，而不是每个函数里：

| 边界 | 职责 | 动作 |
|------|------|------|
| 工具适配层 | 隔离第三方 SDK 和传输细节 | 把超时、连接错误、解析错误转换成 `ToolError` 子类 |
| Agent 循环 | 决定重试、反馈还是终止 | 捕获领域异常，更新状态，不打印堆栈 |
| API/CLI 入口 | 面向用户输出 | 记录一次完整日志，返回脱敏文案和错误码 |
| 领域服务 | 表达业务规则 | 只抛领域异常，不处理 HTTP 状态码 |

```python
import logging

logger = logging.getLogger(__name__)

class ToolError(Exception):
    pass

def _call_upstream(city: str) -> str:
    if city == "timeout":
        raise TimeoutError("upstream timeout")
    return "sunny"

def weather(city: str) -> str:
    try:
        return _call_upstream(city)
    except TimeoutError as exc:
        raise ToolError("天气服务暂时不可用") from exc

try:
    weather("timeout")
except ToolError:
    logger.exception("weather tool failed")
```

几个工程原则：

- **只记录一次**：在最终处理异常的地方用 `logger.exception`，不要在每一层都"记录并重新抛出"，否则日志会重复多份。
- **保留原因**：包装时用 `raise ... from exc`；只有到了面向用户的最终边界，才考虑 `from None`。
- **不要重复包装**：捕获到 `AgentError` 时直接 `raise`，避免把领域异常再包一层。
- **脱敏**：用户看到"工具暂时不可用"即可，堆栈、URL、密钥留在日志里。
- **不要吞掉编程错误**：`TypeError`、`AttributeError` 通常意味着代码 bug，转换成"工具失败"会掩盖问题。工具边界可以统一转成致命错误，但必须记录完整堆栈。

---

## 八、上下文管理器协议

上下文管理器通过 `__enter__` 和 `__exit__` 管理资源：

```python
class ChatSession:
    def __init__(self):
        self.messages: list[tuple[str, str]] = []
        self.closed = False

    def __enter__(self):
        print("open")
        return self

    def add(self, role: str, content: str) -> None:
        self.messages.append((role, content))

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is not None:
            self.messages.clear()
        self.closed = True
        print("close")
        return False

with ChatSession() as session:
    session.add("user", "hi")
print(session.closed, session.messages)
```

`__exit__` 的三个参数：

| 参数 | 无异常时 | 有异常时 |
|------|----------|----------|
| `exc_type` | `None` | 异常类 |
| `exc` | `None` | 异常实例 |
| `tb` | `None` | traceback 对象 |

返回值决定异常是否被抑制：

- 返回 `False` 或 `None`：异常继续向外传播。
- 返回真值：异常被吞掉，`with` 之后的代码继续执行。
- `__enter__` 抛异常时，`__exit__` 不会被调用。
- `__exit__` 自身抛异常时，新异常会替换原异常，原异常进入 `__context__`。

一个健壮的上下文管理器应满足：

1. `__exit__` 可重复调用，重复 `close` 不报错。
2. 清理逻辑尽量短，避免在异常处理路径上再抛异常。
3. 只在明确知道如何恢复时才返回真值抑制异常。
4. 需要保留异常时，记录日志后返回 `False`，让上层决定。

---

## 九、contextlib.contextmanager

手写 `__enter__`/`__exit__` 类适合有多个方法和复杂状态的资源；如果只是"进入时准备、退出时清理"，生成器版本更简洁。

```python
from contextlib import contextmanager

@contextmanager
def session_scope(name: str):
    session = {"name": name, "messages": []}
    try:
        yield session
    except Exception:
        session["messages"].clear()
        raise
    finally:
        print("close", name)

with session_scope("demo") as session:
    session["messages"].append("hi")

print(session["messages"])   # ['hi']
```

执行流程：

1. 进入 `with` 时，装饰器创建上下文管理器并调用 `__enter__`，运行生成器到 `yield`。
2. `yield` 的值绑定给 `as` 后面的变量。
3. 退出 `with` 时，如果没有异常，生成器从 `yield` 之后继续执行。
4. 如果有异常，异常会在 `yield` 处抛出；生成器可以选择捕获、清理并重新抛出，或者捕获后不再抛出以抑制异常。

使用规则：

- 生成器必须恰好 `yield` 一次；`yield` 两次会报 "generator didn't stop"。
- 清理逻辑放在 `try/finally` 中，确保异常路径也会执行。
- 不要写 `except Exception: pass`，那会静默吞掉所有异常。
- 生成器上下文管理器只能使用一次，重复进入会报错；需要复用时应写类或每次新建。
- 类型注解用 `collections.abc.Iterator`，例如 `Iterator[dict[str, object]]`。

| 实现方式 | 优点 | 限制 |
|----------|------|------|
| 手写类 | 状态清晰、可复用、可继承 | 样板代码多 |
| `@contextmanager` | 代码短、逻辑直观 | 单次使用、不能直接暴露多个方法 |
| `@asynccontextmanager` | 支持异步进入和清理 | 同样是生成器单次使用 |

---

## 十、contextlib 常用工具

### 10.1 closing

`closing(obj)` 在退出时调用 `obj.close()`，适合有 `close` 方法但没有实现上下文协议的对象。

```python
from contextlib import closing

class Connection:
    def close(self):
        print("closed")

with closing(Connection()) as conn:
    print("use", type(conn).__name__)
```

### 10.2 suppress

`suppress(*exceptions)` 只抑制列出的异常：

```python
from contextlib import suppress
from pathlib import Path

with suppress(FileNotFoundError):
    Path("missing.txt").unlink()
```

不要写 `suppress(Exception)`，那和裸 `except` 的区别只剩可读性。只抑制你明确知道可以忽略的异常，并在注释里说明原因。

### 10.3 nullcontext

`nullcontext(value)` 在需要"可选地使用上下文管理器"时很有用：

```python
from contextlib import nullcontext

def maybe_lock(lock=None):
    return lock if lock is not None else nullcontext()

with maybe_lock() as value:
    print(value)   # None
```

它返回一个什么都不做的上下文管理器，避免为"没有锁"单独写一个分支。

| 工具 | 作用 | 注意 |
|------|------|------|
| `closing` | 退出时调用 `close()` | 不抑制异常 |
| `suppress` | 抑制指定异常 | 只列明确可忽略的类型 |
| `nullcontext` | 空上下文 | 适合可选资源 |
| `ExitStack` | 动态管理多个资源 | 后进先出关闭 |

---

## 十一、ExitStack 与动态资源管理

当资源数量在运行时才确定，嵌套 `with` 会变得很笨重。`ExitStack` 按后进先出顺序统一关闭：

```python
from contextlib import ExitStack

class Resource:
    def __init__(self, name: str):
        self.name = name

    def __enter__(self):
        print("open", self.name)
        return self

    def __exit__(self, exc_type, exc, tb):
        print("close", self.name)

with ExitStack() as stack:
    for name in ["a", "b"]:
        stack.enter_context(Resource(name))
    print("work")
```

输出：

```text
open a
open b
work
close b
close a
```

常用方法：

| 方法 | 作用 |
|------|------|
| `enter_context(cm)` | 进入上下文并把退出函数压栈，返回 `__enter__` 的结果 |
| `callback(func, *args, **kwargs)` | 退出时调用普通函数 |
| `push(exit_func)` | 压入自定义退出函数 |
| `pop_all()` | 把当前栈转移到一个新的 `ExitStack`，原栈清空 |
| `close()` | 立即按后进先出顺序执行所有退出函数 |

`pop_all()` 适合"工厂函数先打开一组资源，再把所有权交给调用方"的场景：

```python
def open_resources(names):
    stack = ExitStack()
    for name in names:
        stack.enter_context(Resource(name))
    return stack.pop_all()
```

即使某个 `__enter__` 抛异常，`ExitStack` 也会关闭已经成功进入的资源。需要异步资源时用 `AsyncExitStack`，方法名对应 `enter_async_context`、`push_async_callback`。

---

## 十二、异步上下文管理器 async with

异步资源实现 `__aenter__` 和 `__aexit__`，两者都是协程：

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def stream_session(name: str):
    print("open", name)
    try:
        yield {"name": name}
    finally:
        await asyncio.sleep(0)
        print("close", name)

async def main():
    async with stream_session("demo") as session:
        print("use", session["name"])

asyncio.run(main())
```

`async with` 的语义与 `with` 一致，只是进入和退出都要 `await`。清理代码运行在事件循环里，因此可以 `await` 关闭连接、刷新缓冲区。

取消与清理：

- 任务被取消时，`asyncio.CancelledError` 会在 `await` 点抛出，`finally` 仍会执行。
- 如果清理本身需要 `await`，它可能再次被取消。关键清理可以用 `asyncio.shield` 保护，但 shield 只能防止外层取消立即传播，不能保证无限期执行。
- 清理逻辑应尽量短，避免在取消路径上做重试或长时间等待。

异步生成器需要显式关闭。`async for` 中 `break` 不保证立即调用 `aclose()`，Python 3.10+ 可以用 `aclosing`：

```python
from contextlib import aclosing

async def numbers():
    try:
        for i in range(3):
            yield i
    finally:
        print("closed")

async def main():
    async with aclosing(numbers()) as gen:
        async for n in gen:
            if n == 1:
                break

asyncio.run(main())
```

Python 3.11+ 的超时可以用 `asyncio.timeout`：

```python
async def call_with_timeout(coro, seconds: float):
    async with asyncio.timeout(seconds):
        return await coro
```

Python 3.10 使用 `asyncio.wait_for(coro, timeout=seconds)`。

---

## 十三、重试、超时与资源清理模式

### 13.1 只重试可重试的错误

```python
import asyncio
import random
from dataclasses import dataclass

class RetryableError(Exception):
    pass

@dataclass
class RetryPolicy:
    attempts: int = 3
    base_delay: float = 0.1
    max_delay: float = 1.0

async def call_with_retry(fn, policy: RetryPolicy):
    if policy.attempts < 1:
        raise ValueError("attempts 必须大于等于 1")

    last: Exception | None = None
    for attempt in range(1, policy.attempts + 1):
        try:
            return await fn()
        except RetryableError as exc:
            last = exc
            if attempt == policy.attempts:
                break
            delay = min(policy.max_delay, policy.base_delay * 2 ** (attempt - 1))
            await asyncio.sleep(delay * random.uniform(0.5, 1.0))

    assert last is not None
    raise last
```

重试策略的要点：

- 只捕获明确的可重试异常，参数错误、鉴权失败、业务 4xx 不应该重试。
- 加入指数退避、上限和随机抖动，避免大量客户端同时重试。
- 考虑操作幂等性：非幂等的写操作重试可能产生重复副作用。
- 设置总 deadline，而不只是单次超时；重试次数乘以单次超时可能远超用户可接受时间。
- 不要捕获 `BaseException`，否则会吞掉取消信号和进程退出。

### 13.2 超时的边界

- `asyncio.timeout` 通过取消任务实现超时，能中断正在 `await` 的协程。
- `asyncio.wait_for` 在 3.10 可用，语义类似。
- 线程池的 `future.result(timeout=...)` 只让等待方超时，**不会杀死正在运行的线程**；线程仍会继续占用资源。
- 超时后要明确资源由谁清理：协程被取消后走 `finally`，线程则需要协作式取消或进程隔离。

### 13.3 清理模式

| 模式 | 适用场景 | 注意 |
|------|----------|------|
| `with` | 同步文件、锁、连接 | 退出时自动调用 `__exit__` |
| `async with` | 异步连接、流、会话 | 清理可以 `await` |
| `try/finally` | 没有上下文协议的临时资源 | 不要在里面 `return` 或吞异常 |
| `ExitStack` | 数量动态的多个资源 | 后进先出，单个进入失败也会清理已进入的 |
| `AsyncExitStack` | 异步动态资源 | 对应异步进入和回调 |

---

## 十四、常见坑与根因分析

| 坑 | 现象 | 根因 | 修复 |
|----|------|------|------|
| 裸 `except` | Ctrl+C 无法退出，取消信号被吞 | 裸 `except` 捕获 `BaseException` | 改为 `except Exception` 或更具体的类型 |
| 吞异常 | 任务失败但日志里什么都没有 | `except: pass` 或只记录不回传 | 至少记录一次，并决定重试/上报/返回 |
| `finally` 中 `return` | 原异常消失，返回值被覆盖 | `finally` 的控制流会丢弃在途异常 | 清理逻辑不要 `return`/`break`/`continue` |
| 异常链丢失 | 日志只有"工具失败"，没有根因 | 只记录 `str(exc)`，或包装时 `from None` | 用 `logger.exception` 和 `raise ... from exc` |
| 上下文管理器吞异常 | `with` 块出错后继续执行 | `__exit__` 返回了真值 | 只在明确恢复时返回 True |
| 重试范围过宽 | 参数错误被重试三次 | `except Exception` 包住整个调用 | 只捕获可重试异常，限制次数和总时长 |

一个典型的吞异常写法：

```python
try:
    result = call_tool()
except Exception:
    pass
```

调用方完全不知道工具失败了，后续逻辑可能基于空结果继续运行。至少应该：

```python
try:
    result = call_tool()
except ToolError:
    logger.exception("tool call failed")
    raise
```

还有一个隐蔽点：`except ... as exc` 中的 `exc` 在 `except` 块结束后会被删除，以打断异常对象与 traceback 的引用环。如果闭包或回调在块结束后还引用 `exc`，会得到 `NameError`。需要在块内把需要的信息提取到普通变量。

---

## 十五、高频面试题（10 道）

### 1. `BaseException` 和 `Exception` 有什么区别？为什么不要捕获 `BaseException`？

**答案：** `BaseException` 是所有异常的根，直接子类包括 `SystemExit`、`KeyboardInterrupt`、`GeneratorExit` 和 `Exception`。`Exception` 是常规业务和运行时错误的基类。捕获 `BaseException` 会把用户中断、解释器退出和异步任务取消一起吞掉，导致进程无法正常退出或取消无法传播。因此业务代码应捕获 `Exception` 或更具体的异常；只有在框架最外层做最后清理时才考虑 `BaseException`，并且清理后要重新抛出。

### 2. `try/except/else/finally` 的执行顺序是什么？`else` 有什么用？

**答案：** 先执行 `try`；没有异常时执行 `else`，有匹配异常时执行 `except`；无论哪条路径，离开 `try` 语句前都会执行 `finally`。`else` 用来放"只有 `try` 成功后才执行、但不希望被本层 `except` 捕获"的逻辑，可以让 `try` 块只包含真正可能出错的语句。`finally` 在 `return` 之前执行；如果 `finally` 里也 `return`，会覆盖返回值并吞掉在途异常。

### 3. `raise`、`raise ... from ...` 和 `raise ... from None` 有什么区别？

**答案：** 裸 `raise` 重新抛出当前正在处理的异常，保留原 traceback；`raise NewError(...) from exc` 抛出新的异常，并把 `exc` 设为 `__cause__`，traceback 会显示直接原因；`raise NewError(...) from None` 也会抛出新的异常，但把 `__suppress_context__` 设为 True，隐藏自动上下文。即使不写 `from`，在 `except` 块里抛出新异常也会自动设置 `__context__`，所以"异常链"不一定会丢，丢的往往是日志里只打印了 `str(exc)`。

### 4. 如何设计 Agent 的自定义异常体系？

**答案：** 先定义一个业务基类，例如 `AgentError(Exception)`，下面分 `ToolError`、`ModelError` 等分支；工具错误再用 `retryable` 属性或 `RetryableToolError`/`FatalToolError` 区分处理策略，用 `code` 表达具体原因。原则是继承 `Exception`、保持层级浅、调用 `super().__init__` 保留消息、只保存可序列化的字段。工具适配层负责把第三方异常转换成领域异常，Agent 循环只根据 `retryable` 和错误码决定重试、反馈还是终止，API 层负责脱敏和记录日志。

### 5. EAFP 和 LBYL 分别适合什么场景？

**答案：** EAFP 是"先操作，出错再捕获"，适合文件、网络、字典键等外部资源，因为操作本身才是权威判断，能避免检查与使用之间的竞态。LBYL 是"先检查再操作"，适合用户输入校验、参数 schema 校验和需要提前给出友好提示的场景。LBYL 的典型风险是 TOCTOU：检查文件存在后、读取前文件可能被删除。Agent 中模型生成的工具参数通常先做 schema 校验（LBYL），真正调用外部服务时用 EAFP。

### 6. 上下文管理器的协议是什么？`__exit__` 的返回值有什么含义？

**答案：** 上下文管理器实现 `__enter__` 和 `__exit__(exc_type, exc, tb)`。`with` 进入时调用 `__enter__`，其返回值绑定给 `as` 变量；退出时调用 `__exit__`，无异常时三个参数都是 `None`，有异常时传入异常类、实例和 traceback。`__exit__` 返回 `False` 或 `None` 时异常继续传播，返回真值时异常被抑制。`__enter__` 抛异常不会调用 `__exit__`；`__exit__` 自身抛异常会替换原异常，原异常进入 `__context__`。

### 7. `@contextmanager` 的原理是什么？有哪些限制？

**答案：** `@contextmanager` 把一个生成器函数包装成上下文管理器工厂。进入 `with` 时运行生成器到 `yield`，`yield` 的值作为 `as` 变量；退出时如果没有异常，生成器从 `yield` 后继续执行；如果有异常，异常会在 `yield` 处抛出，生成器可以捕获、清理并决定是否重新抛出。限制是生成器必须恰好 `yield` 一次、清理逻辑要放在 `try/finally` 中、同一个生成器上下文管理器只能使用一次。它适合简单的进入/退出逻辑，复杂状态和多方法资源应手写类。

### 8. `ExitStack` 解决什么问题？它的关闭顺序是什么？

**答案：** `ExitStack` 用于在运行时动态管理数量不定的资源，避免手写多层嵌套 `with`。通过 `enter_context` 进入上下文、`callback` 注册普通清理函数、`push` 压入自定义退出函数，退出时按**后进先出**顺序执行；即使某个 `__enter__` 失败，已经成功进入的资源也会被关闭。`pop_all()` 可以把当前栈转移给调用方，适合工厂函数移交资源所有权。异步场景使用 `AsyncExitStack`。

### 9. `async with` 和 `with` 有什么区别？取消时如何保证清理？

**答案：** `with` 调用同步的 `__enter__`/`__exit__`，`async with` 调用协程 `__aenter__`/`__aexit__`，进入和退出都需要 `await`，因此清理时可以等待网络或磁盘操作。任务被取消时，`asyncio.CancelledError` 会在 `await` 点抛出，`finally` 仍会执行；但清理中的 `await` 也可能再次被取消，关键清理可以用 `asyncio.shield` 保护，并尽量保持清理短小。异步生成器退出时可以用 `aclosing` 确保 `aclose()` 被调用。

### 10. 设计重试和超时机制时要注意什么？

**答案：** 只重试明确的可重试异常，例如超时、限流、临时 5xx；参数错误、鉴权失败和业务 4xx 不应重试。重试要有限次数、指数退避、随机抖动和总 deadline，并考虑操作幂等性，避免重复写入。超时方面，`asyncio.timeout` 通过取消任务生效，能中断协程；线程池的超时只让等待方返回，不会杀死正在运行的线程。超时和重试之后要明确资源由谁清理，避免留下悬挂连接或后台任务。

---

## 十六、避坑指南

### 坑1：裸 `except` 捕获一切

**错误现象：** 按下 Ctrl+C 无法退出；异步任务取消后程序还在重试；`SystemExit` 被吞掉。

**产生原因：** 裸 `except:` 等价于 `except BaseException:`，把 `KeyboardInterrupt`、`SystemExit`、`CancelledError` 都捕获了。

**正确做法：** 捕获具体异常；确实需要兜底时用 `except Exception`，并在日志中记录完整堆栈。

```python
try:
    result = call_tool()
except ToolError:
    logger.exception("tool call failed")
    raise
```

### 坑2：吞掉异常

**错误现象：** 任务失败但没有任何日志；上游收到空结果；问题无法复现。

**产生原因：** `except Exception: pass`，或者捕获后只返回默认值，没有记录也没有上报。

**正确做法：** 明确三选一：重试、转换成领域异常、记录后返回可解释的错误。不要静默吞掉。

### 坑3：在 `finally` 中 `return`

**错误现象：** 明明抛了异常，函数却正常返回；日志里没有异常；返回值被改写。

**产生原因：** `finally` 中的 `return`、`break`、`continue` 会丢弃正在传播的异常。

**正确做法：** `finally` 只做清理，不改变控制流。需要返回值时在 `try` 或 `else` 中返回。

```python
def read_config(path):
    handle = None
    try:
        handle = open(path, encoding="utf-8")
        return handle.read()
    finally:
        if handle is not None:
            handle.close()
```

### 坑4：丢失异常链

**错误现象：** 日志只有"工具调用失败"，看不到底层是超时还是解析错误。

**产生原因：** 包装时只传 `str(exc)`，或者用 `from None` 隐藏了上下文，或者在多层边界重复记录。

**正确做法：** 用 `raise NewError("工具调用失败") from exc` 保留原因，在最终边界用 `logger.exception` 记录一次完整堆栈；`from None` 只用于最终面向用户的输出。

### 坑5：`@contextmanager` 中 `yield` 没有放在 `try/finally` 里

**错误现象：** `with` 块抛异常后连接没有关闭；生成器上下文管理器被复用时行为异常。

**产生原因：** `yield` 之后的清理代码在异常路径不会执行；生成器上下文管理器本身只能使用一次。

**正确做法：** 把 `yield` 放进 `try/finally`，清理逻辑放 `finally`；不要缓存或复用同一个上下文管理器实例；需要复用时手写类。下面的 `create_session()` 代表任意返回可关闭对象的工厂：

```python
@contextmanager
def session_scope():
    session = create_session()
    try:
        yield session
    finally:
        session.close()
```

### 坑6：重试范围过宽或没有上限

**错误现象：** 参数错误被重试三次；服务过载时所有客户端同时重试；请求总耗时远超预期。

**产生原因：** 用 `except Exception` 包住整个调用；没有退避、抖动、次数上限和总 deadline；忽略操作幂等性。

**正确做法：** 只捕获可重试异常，使用指数退避加抖动，设置最大次数和总超时，非幂等操作先做去重或幂等键。

---

## 十七、本章学习自检

### 异常模型

- [ ] 能画出 `BaseException` 与 `Exception` 的主要分支
- [ ] 能解释为什么不要捕获 `BaseException`
- [ ] 知道 `CancelledError` 从 Python 3.8 起继承 `BaseException`
- [ ] 了解 `ExceptionGroup` 和 `except*` 的适用版本
- [ ] 能用自己的话解释 EAFP 与 LBYL 的取舍

### 执行顺序与异常链

- [ ] 能准确说出 `try/except/else/finally` 的执行顺序
- [ ] 知道 `else` 中的异常不会被同一个 `except` 捕获
- [ ] 能解释 `finally` 中 `return` 为什么会吞异常
- [ ] 能区分 `__cause__`、`__context__` 和 `__suppress_context__`
- [ ] 会用 `raise ... from exc` 保留根因

### 上下文管理

- [ ] 能默写一个实现 `__enter__`/`__exit__` 的资源类
- [ ] 知道 `__exit__` 返回真值会抑制异常
- [ ] 能用 `@contextmanager` 写会话作用域
- [ ] 会用 `closing`、`suppress`、`nullcontext`
- [ ] 能用 `ExitStack` 动态关闭多个资源

### Agent 工程实践

- [ ] 能设计 `AgentError`、`ToolError`、`RetryableToolError` 的浅层异常树
- [ ] 知道在哪个边界把第三方异常转换成领域异常
- [ ] 能用 `async with` 管理流式会话并处理取消清理
- [ ] 能写出只重试可重试错误、带退避和总 deadline 的重试逻辑
- [ ] 知道线程超时不会杀死正在运行的线程

---

> 返回 [模块目录](../../README.md) | 上一篇 [03-Python函数进阶与装饰器](./03-Python函数进阶与装饰器.md)
