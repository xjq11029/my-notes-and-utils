# Python 并发与协程：线程、进程与 asyncio 的工程选型

> “并发”不是“同时做很多事”这么简单：线程共享内存但受 GIL 约束，进程真正并行但通信昂贵，协程轻量却要求全链路不阻塞。本文从概念、GIL、线程、进程讲到 asyncio、异步 LLM 与 FastAPI 边界，最后给出一张能落地的选型表。

> 参考链接：
> - [Python 标准库：threading](https://docs.python.org/zh-cn/3/library/threading.html) -- 线程、锁、条件变量与信号量
> - [Python 标准库：multiprocessing](https://docs.python.org/zh-cn/3/library/multiprocessing.html) -- 进程、启动方式与进程间通信
> - [Python 标准库：concurrent.futures](https://docs.python.org/zh-cn/3/library/concurrent.futures.html) -- 线程池、进程池与 Future
> - [Python 标准库：asyncio](https://docs.python.org/zh-cn/3/library/asyncio.html) -- 事件循环、协程、Task 与同步原语
> - [Python 术语表：GIL](https://docs.python.org/zh-cn/3/glossary.html#term-GIL) -- 全局解释器锁的官方定义
> - [FastAPI 文档：并发与 async/await](https://fastapi.tiangolo.com/async/) -- 同步路由与异步路由的执行差异

---

## 目录

- [一、并发、并行与异步：先把概念摆正](#一并发并行与异步先把概念摆正)
- [二、GIL：CPython 的全局解释器锁](#二gilcpython-的全局解释器锁)
- [三、threading：线程、锁与队列](#三threading线程锁与队列)
- [四、multiprocessing：绕开 GIL 的真并行](#四multiprocessing绕开-gil-的真并行)
- [五、concurrent.futures：统一的执行器抽象](#五concurrentfutures统一的执行器抽象)
- [六、asyncio：事件循环与协程](#六asyncio事件循环与协程)
- [七、异步限流、队列与背压](#七异步限流队列与背压)
- [八、异步 LLM 调用与流式输出](#八异步-llm-调用与流式输出)
- [九、FastAPI 边界：别让阻塞调用卡死事件循环](#九fastapi-边界别让阻塞调用卡死事件循环)
- [十、选型表：到底该用哪一种](#十选型表到底该用哪一种)
- [十一、常见坑](#十一常见坑)
- [十二、避坑指南](#十二避坑指南)
- [十三、高频面试题（10 道）](#十三高频面试题10-道)
- [十四、本章学习自检](#十四本章学习自检)

---

## 一、并发、并行与异步：先把概念摆正

### 1.1 三个概念的分界

很多技术讨论一上来就把“并发”“并行”“异步”混着用，结果选型全靠感觉。先把三个词拆开：

| 维度 | 并发（Concurrency） | 并行（Parallelism） | 异步（Asynchrony） |
|------|---------------------|---------------------|--------------------|
| 核心问题 | 多个任务在重叠的时间段内推进 | 多个任务在同一时刻真正同时执行 | 等待时不占住执行者，先去做别的 |
| 是否需要多核 | 不需要 | 需要 | 不需要 |
| 关注点 | 任务编排与资源共享 | 计算吞吐 | 等待管理与控制流 |
| Python 对应 | 线程、协程 | 多进程、C 扩展 | asyncio、回调、事件驱动 |
| 典型误区 | 以为并发一定更快 | 以为线程一定并行 | 以为异步一定多线程 |

一句话概括：**并发是“结构”，并行是“硬件”，异步是“等待方式”。** 单核 CPU 也能并发（时间片轮转），单线程也能异步（事件循环），但单核不可能并行。

> 生活化类比：一家餐厅里，一个服务员同时照看五桌客人，是并发；五个服务员各照看一桌，是并行；服务员点完菜不去厨房门口干等，而是先去给别的桌点单，等菜好了再端过来，是异步。异步的服务员可以只有一个，但他必须“不堵在等待上”。

### 1.2 任务画像与 Python 工具箱

选型的第一步不是挑工具，而是判断任务在等什么：

| 任务类型 | 特征 | 例子 | 瓶颈 |
|----------|------|------|------|
| CPU 密集 | 大部分时间在计算 | 图像处理、加密、批量 embedding、复杂排序 | CPU 核数 |
| IO 密集 | 大部分时间在等待 | HTTP/LLM API、数据库、磁盘、DNS | 网络/磁盘延迟 |
| 混合型 | 计算与等待交替 | 下载后解析、推理前预处理 | 两者皆有 |

Python 提供三套主流通用工具箱：

| 工具 | 调度方式 | 内存模型 | 受 GIL 影响 | 最适合 |
|------|----------|----------|-------------|--------|
| `threading` | OS 抢占式调度 | 共享进程内存 | CPU 密集时受限 | 阻塞式 IO、旧库兼容 |
| `multiprocessing` | OS 进程调度 | 独立内存，需序列化通信 | 否，每进程独立 GIL | CPU 密集、隔离性要求高 |
| `asyncio` | 单线程协作式调度 | 共享进程内存 | 单线程，无并行 | 海量网络 IO、流式处理 |

Agent 开发中三者经常同时出现：调用 LLM 和工具是 IO 密集，适合 asyncio；本地 rerank、向量计算是 CPU 密集，适合进程池或 C 扩展；一些老 SDK 只有阻塞接口，只能用线程池包一层。选型不是“选一个信仰”，而是“按边界拆开”。

---

## 二、GIL：CPython 的全局解释器锁

### 2.1 GIL 锁住了什么

GIL（Global Interpreter Lock）是 CPython 解释器中的一把互斥锁：同一时刻只有一个线程能执行 Python 字节码。注意几个限定词：

- 它是 **CPython 的实现细节**，不是 Python 语言规范；Jython、IronPython 没有 GIL。
- 它约束的是 **Python 字节码**，不是所有底层操作；线程在阻塞 IO 或某些 C 扩展中会释放 GIL。
- Python 线程是 **真正的 OS 线程**，由操作系统抢占式调度；GIL 只保证字节码互斥，不保证“线程是假的”。

GIL 存在的主要原因是 CPython 的引用计数内存管理：多线程同时修改引用计数需要细粒度锁，历史上为了单线程性能和 C 扩展的简单性，选择了全局锁。代价是 CPU 密集的多线程无法利用多核。

CPython 默认的线程切换间隔是 5 毫秒，可通过 `sys.getswitchinterval()` 查看、`sys.setswitchinterval()` 调整。这个值不是性能承诺，只是解释器的调度参数。

```python
import sys
print(sys.getswitchinterval())   # 通常为 0.005
```

### 2.2 GIL 下的 CPU 与 IO 任务

**CPU 密集任务**：线程大部分时间在执行字节码，GIL 几乎一直被占用，多线程只能轮流执行，还要付出线程切换成本。多核机器上，多线程通常不会加速，甚至更慢。

**IO 密集任务**：线程调用 `socket.recv`、文件读写、`time.sleep` 等阻塞操作时会释放 GIL，其他线程可以继续执行。因此多线程对网络、磁盘、数据库等待仍然有效。

**C 扩展**：NumPy、部分数据库驱动、加密库会在底层计算时释放 GIL，这时多线程也能获得并行收益。但这取决于扩展实现，不能一概而论。

一个可运行的对比脚手架（不预设结论，请在本机观察）：

```python
import threading
import time

def io_task():
    time.sleep(0.05)

def cpu_task():
    total = 0
    for i in range(200_000):
        total += i * i
    return total

def run_sequential(fn, n):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return time.perf_counter() - start

def run_threads(fn, n):
    threads = [threading.Thread(target=fn) for _ in range(n)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - start

if __name__ == "__main__":
    n = 4
    print(f"sleep sequential: {run_sequential(io_task, n):.3f}s")
    print(f"sleep threads:   {run_threads(io_task, n):.3f}s")
    print(f"cpu sequential:  {run_sequential(cpu_task, n):.3f}s")
    print(f"cpu threads:     {run_threads(cpu_task, n):.3f}s")
```

运行后通常会看到：`sleep` 的多线程耗时明显低于顺序执行，而 CPU 任务的多线程没有同等收益。具体数值受机器负载影响，本文不给出固定基准。

### 2.3 绕过 GIL 的路径

| 路径 | 机制 | 代价 | 适用 |
|------|------|------|------|
| `multiprocessing` | 每个进程独立解释器和 GIL | 启动、内存、序列化开销 | CPU 密集、批处理 |
| C/C++ 扩展 | 在原生代码中释放 GIL | 开发与部署复杂 | 数值计算、编解码 |
| 向量化库 | NumPy 等底层释放 GIL | 受库实现约束 | 数组运算、矩阵计算 |
| free-threaded 构建 | 3.13 起提供 free-threaded 构建（初期为实验性，PEP 703），默认安装仍带 GIL | 生态兼容性、性能取舍 | 评估与实验 |

需要澄清一个常见误解：**GIL 不等于“写 Python 就不用加锁”。** `counter += 1` 是“读、加、写”三个字节码操作，线程切换可能发生在中间，仍然会丢更新。GIL 只保证单条字节码不被并行执行，不保证复合操作原子。

---

## 三、threading：线程、锁与队列

### 3.1 创建、等待与守护线程

```python
import threading
import time

def worker(name: str, delay: float) -> None:
    print(f"{name} start")
    time.sleep(delay)
    print(f"{name} end")

t = threading.Thread(target=worker, args=("A", 0.05), name="worker-A")
t.start()
t.join()
print("main done")
```

几个要点：

- `start()` 才真正创建并启动线程；直接调用 `run()` 只是在当前线程同步执行。
- `join()` 阻塞等待线程结束，可传 `timeout`；超时后线程仍在运行。
- `daemon=True` 的线程会随主线程退出而被强制结束，不会执行 `finally`；不要用它做必须完成的清理。
- 非守护线程默认会在解释器退出前被等待；线程池的线程是非守护的。
- 线程里的异常不会自动传播到主线程，只会打印到 stderr；需要收集结果时用 `Future` 或共享队列。

### 3.2 竞态、Lock 与死锁

`counter += 1` 不是原子操作。多个线程同时执行时，可能同时读到旧值，再各自写回，导致更新丢失：

```python
import threading

counter = 0
barrier = threading.Barrier(5)

def worker():
    global counter
    barrier.wait()
    for _ in range(100_000):
        counter += 1

threads = [threading.Thread(target=worker) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(counter)   # 可能小于 500000，也可能恰好等于；竞态不保证每次复现
```

竞态的特点是不稳定复现：一次运行正确不代表代码安全。这个例子在部分解释器版本和机器上可能正好得到 500000，多跑几次或增加线程数通常更容易观察到丢失。

修复方式是让“读改写”落在同一把锁里：

```python
import threading

counter = 0
lock = threading.Lock()
barrier = threading.Barrier(5)

def worker():
    global counter
    barrier.wait()
    for _ in range(100_000):
        with lock:
            counter += 1

threads = [threading.Thread(target=worker) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(counter)   # 500000
```

`Lock` 不可重入：同一线程第二次 `acquire()` 会阻塞自己。`RLock` 允许同一线程重复获取，但必须释放相同次数。用哪个取决于临界区是否会递归调用同一个加锁函数；大多数业务代码用 `Lock` 即可。

死锁的四个必要条件：互斥、持有并等待、不可抢占、循环等待。工程上最有效的破解方式是**统一锁顺序**：

```python
# 错误示例：两个线程以相反顺序获取两把锁，可能互相等待
def transfer_a_to_b():
    with lock_a:
        with lock_b:
            pass

def transfer_b_to_a():
    with lock_b:
        with lock_a:
            pass
```

修复：所有代码按同一顺序获取锁，或使用 `lock.acquire(timeout=...)` 在超时后释放已持有的锁并重试。不要在一把锁里调用可能获取另一把锁的外部代码。

### 3.3 Condition、Event 与 Semaphore

| 原语 | 作用 | 典型场景 |
|------|------|----------|
| `Lock` / `RLock` | 保护临界区 | 计数器、共享缓存 |
| `Event` | 一个线程通知多个线程“可以继续” | 启动信号、优雅停机 |
| `Condition` | 在锁的基础上等待/通知条件成立 | 有界缓冲区、生产者-消费者 |
| `Semaphore` | 限制同时访问资源的线程数 | 限制并发连接、池化资源 |
| `Barrier` | 让固定数量的线程互相等待 | 测试并发、分阶段任务 |

`Event` 的最小用法：

```python
import threading
import time

stop = threading.Event()

def poller():
    while not stop.is_set():
        time.sleep(0.01)
    print("poller stopped")

t = threading.Thread(target=poller)
t.start()
time.sleep(0.03)
stop.set()
t.join()
```

`Condition.wait()` 必须在持有锁时调用，它会在等待期间释放锁；被 `notify()` 唤醒后重新获取锁。用 `wait_for(predicate)` 可以避免虚假唤醒带来的重复判断。

### 3.4 queue.Queue 与线程池

线程间通信优先用 `queue.Queue`，不要自己用列表加锁拼一个队列。`Queue` 自带锁、条件变量和阻塞语义：

```python
import queue
import threading

def producer(q, items):
    for item in items:
        q.put(item)
    q.put(None)          # 哨兵，通知消费者结束

def consumer(q, out):
    while True:
        item = q.get()
        try:
            if item is None:
                return
            out.append(item * 2)
        finally:
            q.task_done()

q = queue.Queue(maxsize=3)   # 有界队列，天然背压
out = []
t1 = threading.Thread(target=producer, args=(q, range(5)))
t2 = threading.Thread(target=consumer, args=(q, out))
t1.start()
t2.start()
t1.join()
t2.join()
print(out)   # [0, 2, 4, 6, 8]
```

`maxsize` 很重要：无界队列在生产者快于消费者时会无限堆积，最终耗尽内存。`task_done()` 与 `join()` 配对使用，表示“队列中的任务都已处理完”；哨兵本身也要考虑是否需要 `task_done()`。

线程池用 `concurrent.futures.ThreadPoolExecutor` 更省心：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url: str) -> str:
    return url.upper()

urls = ["a", "b", "c"]
with ThreadPoolExecutor(max_workers=2) as pool:
    futures = {pool.submit(fetch, url): url for url in urls}
    for future in as_completed(futures):
        print(futures[future], future.result())
```

线程池适合“任务数量多、单个任务阻塞等待”的场景。它不会绕过 GIL，CPU 密集任务仍然要换进程。`threading.local()` 可以为每个线程保存独立状态，但在 asyncio 中同一线程会跑很多协程，应改用 `contextvars.ContextVar`。

---

## 四、multiprocessing：绕开 GIL 的真并行

### 4.1 进程模型与启动方式

每个进程有独立的内存空间、独立的 Python 解释器和独立的 GIL，因此多进程可以真正并行执行 CPU 密集任务。代价是：

- 进程创建比线程重，启动慢；
- 数据不能直接共享，必须序列化（pickle）后传输；
- 进程间通信有延迟，频繁小消息不划算；
- 调试、日志、异常栈更分散。

Python 支持三种启动方式：

| 方式 | 平台默认 | 特点 |
|------|----------|------|
| `spawn` | Windows 始终；macOS 3.8+ | 启动新解释器，导入主模块，最安全、最慢 |
| `fork` | Linux 3.14 之前默认 | 复制父进程内存，快，但多线程下不安全 |
| `forkserver` | POSIX 3.14 起默认 | 先启动服务器进程，再从它 fork，兼顾速度与安全 |

从 Python 3.14 起，POSIX 平台的默认启动方式由 `fork` 改为 `forkserver`；Windows 始终是 `spawn`。写跨平台代码时，不要依赖默认值，用 `multiprocessing.get_context("spawn")` 显式指定更稳。

### 4.2 Windows spawn 的三条硬规则

Windows 没有 `fork`，只能用 `spawn`。这带来三条必须遵守的规则：

1. **入口必须放在 `if __name__ == "__main__":` 之下**。子进程会重新导入主模块，如果没有保护，会递归创建进程。
2. **传给子进程的函数和参数必须可 pickle**。顶层函数可以，lambda、局部函数、未加锁的生成器通常不行。
3. **不要依赖模块级共享状态**。子进程有独立内存，父进程修改的全局变量不会自动同步。

```python
import multiprocessing as mp

def square(x: int) -> int:
    return x * x

if __name__ == "__main__":
    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=2) as pool:
        print(pool.map(square, [1, 2, 3, 4]))   # [1, 4, 9, 16]
```

如果忘记 `__main__` 保护，Windows 上常见的报错是 `RuntimeError: An attempt has been made to start a new process before the current process has finished its bootstrapping phase`，或者看到进程数指数级增长。

### 4.3 进程间通信与共享状态

| 方式 | 适用 | 注意 |
|------|------|------|
| `Queue` | 多生产者/多消费者传递任务与结果 | 对象必须可 pickle；有缓冲与阻塞语义 |
| `Pipe` | 两个进程之间的双向/单向通道 | 只适合少量进程；注意两端关闭 |
| `Manager` | 共享 dict/list/Namespace | 通过代理进程访问，开销较大 |
| `Value` / `Array` | 共享简单数值/数组 | 需要自己加锁保护复合操作 |
| `shared_memory` | 大块二进制数据零拷贝共享 | 3.8+；生命周期与清理需手动管理 |

优先选择“消息传递”而不是“共享内存”：进程之间共享可变状态需要锁，锁又会带来死锁和竞态，调试成本高。确实要共享大数组时，用 `multiprocessing.shared_memory` 或把计算下沉到 NumPy 等释放 GIL 的库。

### 4.4 进程池的边界

`multiprocessing.Pool` 和 `concurrent.futures.ProcessPoolExecutor` 都能管理进程池，选择时看接口习惯：

- `Pool.map` 简单直接，适合批量同构任务；
- `ProcessPoolExecutor` 与线程池接口一致，便于切换；
- `Pool.imap` 返回惰性迭代器，适合边算边消费；
- `apply_async` 返回 `AsyncResult`，适合需要回调或超时的场景。

几个坑：

- **守护进程不能创建子进程**：`daemon=True` 的进程里再开进程会报错。
- **进程池里再开进程池**容易造成资源耗尽或死锁，尽量扁平化任务。
- **异常必须可 pickle**：自定义异常如果构造函数参数复杂，跨进程可能序列化失败。
- **Ctrl-C 处理**：主进程收到中断后，子进程不一定自动退出，需要显式终止或使用上下文管理器。
- **小任务不适合多进程**：序列化和启动成本可能超过计算本身。

---

## 五、concurrent.futures：统一的执行器抽象

### 5.1 Executor 与 Future

`ThreadPoolExecutor` 和 `ProcessPoolExecutor` 共享同一套 `Executor` 接口：`submit()` 返回 `Future`，用 `result()` 取结果，用 `exception()` 取异常，用 `done()` 判断是否完成。

```python
from concurrent.futures import ThreadPoolExecutor

def divide(a: int, b: int) -> float:
    return a / b

with ThreadPoolExecutor(max_workers=2) as pool:
    ok = pool.submit(divide, 6, 3)
    bad = pool.submit(divide, 1, 0)
    print(ok.result())          # 2.0
    print(bad.exception())      # division by zero
```

`Future` 的关键方法：

| 方法 | 作用 |
|------|------|
| `result(timeout=None)` | 等待并返回结果；任务异常会在此重新抛出 |
| `exception(timeout=None)` | 等待并返回异常对象；无异常返回 `None` |
| `done()` | 是否已完成（正常、异常或取消） |
| `cancel()` | 尝试取消；只有尚未开始执行的任务能成功 |
| `cancelled()` | 是否已取消 |
| `add_done_callback(fn)` | 完成时回调；通常在完成任务的工作线程执行，Future 已完成时立即在调用线程执行 |

`concurrent.futures.Future` 不是 `asyncio.Future`，两者不能直接 `await`。在异步代码里要用 `asyncio.wrap_future()` 或 `loop.run_in_executor()` 桥接。

### 5.2 map、as_completed 与取消

`Executor.map()` 会立即提交所有任务，返回一个按输入顺序产出结果的迭代器；某个任务抛异常时，异常会在迭代到它时重新抛出。它适合“结果顺序重要、任务数量可控”的场景。

`as_completed()` 按完成顺序产出 Future，适合“谁先完成先处理”的进度式消费：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url: str) -> str:
    return f"OK:{url}"

urls = [f"https://example.com/{i}" for i in range(5)]
with ThreadPoolExecutor(max_workers=3) as pool:
    futures = [pool.submit(fetch, url) for url in urls]
    for future in as_completed(futures):
        print(future.result())
```

`wait()` 可以等待一组 Future，并指定 `FIRST_COMPLETED`、`FIRST_EXCEPTION`、`ALL_COMPLETED` 条件，返回 `(done, not_done)` 两个集合。它不会抛异常，适合自己控制超时与退出。

取消的语义要记清楚：`cancel()` 只能取消**尚未开始**的任务；已经运行的任务无法通过 Future 取消。线程池里运行中的线程不能被强制杀死；进程池里只能通过终止整个进程或池来“硬取消”，但那会丢失该进程的清理逻辑，通常不推荐。Python 3.9+ 的 `shutdown(cancel_futures=True)` 可以取消队列中尚未开始的任务。

---

## 六、asyncio：事件循环与协程

### 6.1 事件循环与协程

asyncio 是单线程的协作式并发：事件循环维护就绪回调、定时器和 IO 事件，协程在 `await` 处主动让出控制权，循环再去执行其他就绪任务。没有抢占，也没有线程切换。

```python
import asyncio

async def work(name: str, delay: float) -> str:
    print(f"{name} start")
    await asyncio.sleep(delay)
    print(f"{name} end")
    return name

async def main() -> None:
    results = await asyncio.gather(
        work("A", 0.02),
        work("B", 0.01),
    )
    print(results)

asyncio.run(main())
# A start / B start / B end / A end / ['A', 'B']
```

关键点：

- `async def` 定义协程函数；调用它只返回协程对象，不会执行函数体。
- `await` 驱动协程运行，遇到可等待对象时挂起当前协程，把控制权交回事件循环。
- `asyncio.run()` 创建事件循环、运行入口协程、收尾并关闭循环；一个线程通常只调用一次。
- 事件循环是单线程的，任何阻塞调用都会卡住所有协程。

`await` 一个协程是“内联执行”，不会自动并发；要并发，必须把协程包装成 `Task`，或使用 `gather`、`TaskGroup` 等调度工具。

### 6.2 Task、gather 与结构化并发

`asyncio.create_task(coro)` 把协程注册到事件循环，立即返回 `Task`，让它在后台推进。`gather` 等待多个 awaitable，按输入顺序返回结果：

```python
import asyncio

async def work(name: str, fail: bool = False) -> str:
    await asyncio.sleep(0.01)
    if fail:
        raise ValueError(name)
    return name

async def main() -> None:
    results = await asyncio.gather(
        work("A"),
        work("B", fail=True),
        return_exceptions=True,
    )
    print(results)   # ['A', ValueError('B')]

asyncio.run(main())
```

`gather(return_exceptions=False)`（默认）会在第一个异常处向调用方抛出，但其他任务**不会自动取消**，仍可能在后台继续运行。`return_exceptions=True` 会把异常当作结果返回，适合“部分失败也要汇总”的场景。

`asyncio.wait()` 返回 `(done, pending)` 集合，不会抛异常，适合自己控制超时与取消；`asyncio.as_completed()` 按完成顺序产出结果。

Python 3.11+ 引入 `TaskGroup`，提供结构化并发：组内任一任务失败时，取消其余任务，并在退出时抛出 `ExceptionGroup`：

```python
import asyncio

async def work(name: str, fail: bool = False) -> str:
    await asyncio.sleep(0.01)
    if fail:
        raise ValueError(name)
    return name

async def main() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(work("ok"))
            tg.create_task(work("bad", fail=True))
    except* ValueError as group:
        print("errors:", [str(exc) for exc in group.exceptions])

asyncio.run(main())
```

`create_task` 有一个必须记住的细节：事件循环只保留任务的**弱引用**。如果任务对象没有被变量或集合引用，可能在运行途中被垃圾回收。长期后台任务要存进集合，并在完成回调里移除：

```python
background = set()

def spawn(coro):
    task = asyncio.create_task(coro)
    background.add(task)
    task.add_done_callback(background.discard)
    return task
```

### 6.3 超时、取消与清理

超时和取消是异步工程的核心。Python 3.10 及以前常用 `asyncio.wait_for(coro, timeout)`；3.11+ 可以用 `asyncio.timeout()` 上下文管理器：

```python
import asyncio

async def slow():
    await asyncio.sleep(10)

async def main() -> None:
    try:
        await asyncio.wait_for(slow(), timeout=0.05)
    except asyncio.TimeoutError:
        print("timeout")

asyncio.run(main())
```

`wait_for` 超时后会取消内部任务，并等待取消完成。`asyncio.timeout()` 在 3.11+ 可用，超时时把 `CancelledError` 转换为 `TimeoutError`：

```python
async def main() -> None:
    try:
        async with asyncio.timeout(0.05):
            await asyncio.sleep(10)
    except TimeoutError:
        print("timeout")
```

取消通过 `Task.cancel()` 发起：任务在下一次 `await` 处收到 `CancelledError`。从 Python 3.8 起，`CancelledError` 继承自 `BaseException`，所以 `except Exception` 不会误吞取消。协程应当清理资源后**重新抛出**取消信号：

```python
import asyncio

async def worker():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("cleanup")
        raise

async def main() -> None:
    task = asyncio.create_task(worker())
    await asyncio.sleep(0.01)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("cancelled")

asyncio.run(main())
```

`asyncio.shield(coro)` 可以保护内部任务不被外层取消，但外层仍会收到取消；它适合“已经提交的写操作必须完成”的场景。Python 3.11+ 的 `Task.uncancel()` 用于结构化并发中抵消取消计数，普通业务代码很少需要直接使用。

### 6.4 同步与异步的边界

在异步代码里调用同步阻塞函数，会让整个事件循环停住。处理方式有三种：

| 方式 | 用法 | 适用 |
|------|------|------|
| `asyncio.to_thread(func, *args)` | 3.9+，把同步函数丢到线程池 | 阻塞 SDK、文件 IO |
| `loop.run_in_executor(pool, func, *args)` | 指定线程池或进程池 | 需要自定义池、CPU 密集 |
| 改写为异步库 | 用 `httpx`、`aiohttp`、异步数据库驱动 | 长期高并发服务 |

```python
import asyncio
import time

def blocking_call(x: int) -> int:
    time.sleep(0.02)
    return x * 2

async def main() -> None:
    result = await asyncio.to_thread(blocking_call, 21)
    print(result)   # 42

asyncio.run(main())
```

反过来，在同步代码里调用异步函数不能直接 `asyncio.run()`（如果已有事件循环会报 `RuntimeError`）。应该用 `asyncio.run()` 作为程序入口；如果循环已经在别的线程运行，可以用 `asyncio.run_coroutine_threadsafe()` 把协程提交过去。

`asyncio.to_thread()` 会传播 `contextvars` 上下文，适合带请求 ID、用户身份的日志链路；`run_in_executor()` 不会自动传播，需要手动处理。

---

## 七、异步限流、队列与背压

### 7.1 Semaphore 与 Queue

`asyncio.Semaphore` 用来限制同时在途的任务数，是调用外部 API 时最常用的限流工具：

```python
import asyncio

async def fetch(item: int, sem: asyncio.Semaphore) -> int:
    async with sem:
        await asyncio.sleep(0.01)
        return item * 2

async def main() -> None:
    sem = asyncio.Semaphore(2)
    results = await asyncio.gather(*(fetch(i, sem) for i in range(6)))
    print(results)   # [0, 2, 4, 6, 8, 10]

asyncio.run(main())
```

`async with sem` 在进入时获取许可，离开时释放；即使任务抛异常也会释放。不要把 `Semaphore` 用在多线程之间，它不是线程安全的；线程场景用 `threading.Semaphore`。

`asyncio.Queue` 是协程间的生产者-消费者通道，`maxsize` 提供背压：

```python
import asyncio

async def producer(q: asyncio.Queue, n: int) -> None:
    for i in range(n):
        await q.put(i)
    await q.put(None)

async def consumer(q: asyncio.Queue, out: list) -> None:
    while True:
        item = await q.get()
        if item is None:
            return
        out.append(item)
        q.task_done()

async def main() -> None:
    q = asyncio.Queue(maxsize=2)
    out = []
    await asyncio.gather(producer(q, 5), consumer(q, out))
    print(out)   # [0, 1, 2, 3, 4]

asyncio.run(main())
```

多个消费者时，每个消费者都需要一个哨兵，或者使用 `TaskGroup` 统一取消。`task_done()` 与 `join()` 的配对规则和线程队列一致。

### 7.2 背压与生产者-消费者

背压的本质是：**让生产速度受消费速度约束。** 常见实现有三种：

| 方式 | 机制 | 适用 |
|------|------|------|
| 有界队列 | `put()` 在队列满时等待 | 生产者-消费者解耦 |
| 信号量 | 在途任务数达到上限时等待 | 限制并发请求 |
| 拉式生成器 | 消费者 `next()`/`async for` 才生产 | 流式读取、天然背压 |

没有背压的系统，在流量突增时会把内存或下游打爆。一个无界队列 + 快速生产者，是最常见的 OOM 来源之一。

取消时要同时处理三件事：取消生产者、取消消费者、清空或标记队列。`TaskGroup` 在异常时会取消同组任务，但队列里的残留数据仍需业务决定是丢弃还是补偿。

---

## 八、异步 LLM 调用与流式输出

### 8.1 并发调用与限流

LLM API 的延迟主要在网络和模型生成，CPU 几乎空闲，天然适合 asyncio。下面的假客户端不依赖网络，可以直接运行：

```python
import asyncio

class FakeLLM:
    def __init__(self, delay: float = 0.02) -> None:
        self.delay = delay

    async def complete(self, prompt: str) -> str:
        await asyncio.sleep(self.delay)
        return f"answer:{prompt}"

    async def stream(self, prompt: str):
        for token in ["Hel", "lo", " ", prompt]:
            await asyncio.sleep(self.delay)
            yield token

async def main() -> None:
    llm = FakeLLM()
    sem = asyncio.Semaphore(3)

    async def ask(prompt: str) -> str:
        async with sem:
            return await llm.complete(prompt)

    answers = await asyncio.gather(*(ask(f"q{i}") for i in range(6)))
    print(answers)

    parts = []
    async for delta in llm.stream("world"):
        parts.append(delta)
    print("".join(parts))   # Hello world

asyncio.run(main())
```

工程上还要加：

- **超时**：单次调用、单轮流式、整个任务分别设超时；
- **重试**：只对幂等请求重试，采用指数退避加随机抖动，避免失败时形成脉冲；
- **限流**：`Semaphore` 限制在途请求数，必要时再加令牌桶限制 QPS；
- **熔断**：连续失败时快速失败，避免拖垮上游；
- **可观测性**：记录请求 ID、模型名、token 用量、首 token 延迟和总延迟。

### 8.2 流式输出与工具调用

异步生成器是流式输出的自然表达：

```python
import asyncio

async def fake_stream():
    for token in ["Hel", "lo", ", ", "world"]:
        await asyncio.sleep(0.01)
        yield token

async def collect(stream) -> str:
    parts = []
    async for token in stream:
        parts.append(token)
    return "".join(parts)

async def main() -> None:
    print(await collect(fake_stream()))   # Hello, world

asyncio.run(main())
```

Agent 场景要同时做两件事：把 token 推给前端，把完整文本留给下一轮决策。可以在消费端累加：

```python
async def relay(stream):
    parts = []
    async for token in stream:
        parts.append(token)
        yield token
    print(f"[agent] full answer: {''.join(parts)}")
```

工具调用（tool call）的流式返回更复杂：函数名通常先到，参数 JSON 是分片到达的。**不要对每个分片 `json.loads`**，而应把 `arguments` 片段拼接完整，等流结束或收到 `finish_reason` 后再解析。结构化输出也是同理：流式过程中的 JSON 不完整，不能边流边解析。

工具之间如果有依赖，必须串行；相互独立时用 `gather` 并发，并为每个工具设置独立超时。某个工具失败时，要决定是整体失败还是把错误作为观察结果交回模型。

---

## 九、FastAPI 边界：别让阻塞调用卡死事件循环

### 9.1 async def 与 def 的执行位置

FastAPI 的路由函数写法直接决定它在哪里执行：

| 路由写法 | 执行位置 | 阻塞后果 |
|----------|----------|----------|
| `async def` | 事件循环线程 | 一旦阻塞，整个 worker 的所有请求都停住 |
| `def` | 外部线程池 | 阻塞只占一个线程，但仍受线程池大小限制 |
| `async def` + `await async_client` | 事件循环 | 正确让出控制权，可高并发 |

```python
# 需要安装 fastapi，非本章离线示例
from fastapi import FastAPI

app = FastAPI()

@app.get("/bad")
async def bad():
    import time
    time.sleep(1)          # 阻塞事件循环，所有请求一起卡住
    return {"ok": True}

@app.get("/good")
def good():
    import time
    time.sleep(1)          # 在线程池中执行，不阻塞事件循环
    return {"ok": True}
```

依赖项也遵循同样规则：`async def` 依赖在事件循环执行，`def` 依赖在线程池执行。不要在一个 `async def` 依赖里调用阻塞数据库驱动。

### 9.2 阻塞调用的正确下沉

如果只有同步 SDK，用 `asyncio.to_thread()` 把它丢到线程池：

```python
# 需要安装 fastapi，非本章离线示例
import asyncio
from fastapi import FastAPI

app = FastAPI()

def blocking_llm_call(prompt: str) -> str:
    import time
    time.sleep(0.5)
    return f"answer:{prompt}"

@app.get("/chat")
async def chat(prompt: str):
    answer = await asyncio.to_thread(blocking_llm_call, prompt)
    return {"answer": answer}
```

如果是 CPU 密集计算，应该用进程池，而不是线程池：

```python
from concurrent.futures import ProcessPoolExecutor
import asyncio

def heavy_transform(data: bytes) -> bytes:
    return data[::-1]

# Windows 下应在 __main__ 保护内创建，避免子进程重复创建
pool = ProcessPoolExecutor(max_workers=2)

async def run_cpu_bound(data: bytes) -> bytes:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(pool, heavy_transform, data)
```

`ProcessPoolExecutor` 在 Windows 上同样需要 `__main__` 保护和可 pickle 的函数。FastAPI 的多 worker 模式（如 `uvicorn --workers 4`）本身是多个进程，每个进程有自己的事件循环；不要再在每个请求里随意创建进程池。

### 9.3 流式响应与生命周期

流式接口用 `StreamingResponse` 包一个异步生成器：

```python
# 需要安装 fastapi / uvicorn，非本章离线示例
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def fake_llm_stream(prompt: str):
    for token in ["Hel", "lo", " ", prompt]:
        yield token

async def event_stream(prompt: str):
    async for token in fake_llm_stream(prompt):
        yield f"data: {token}\n\n"
    yield "data: [DONE]\n\n"

@app.get("/stream")
async def stream(prompt: str):
    return StreamingResponse(
        event_stream(prompt),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

客户端断开时，Starlette 会取消流式任务；生成器应在 `finally` 中关闭上游 HTTP 连接、释放信号量。`BackgroundTasks` 只适合“响应返回后很快完成”的小任务，长时间任务应交给独立队列或 worker 进程。需要复用的 HTTP 客户端、数据库连接池，放在 `lifespan` 中初始化与关闭。

---

## 十、选型表：到底该用哪一种

### 10.1 按任务与约束选型

| 场景 | 首选 | 备选 | 关键理由 |
|------|------|------|----------|
| 大量 HTTP / LLM 调用 | asyncio | 线程池 | 等待为主，协程切换轻 |
| 阻塞 SDK、旧代码 | 线程池 | 多进程 | 不改库，隔离阻塞 |
| CPU 密集批处理 | 多进程 | C 扩展 | 绕过 GIL，真并行 |
| 简单批量任务 | `concurrent.futures` | 手动线程 | 统一接口，易收集结果 |
| 共享大量状态 | 线程 + 锁 | 单线程重构 | 避免序列化与同步成本 |
| 需要强隔离 | 多进程 | 容器/沙箱 | 崩溃与内存隔离 |
| 实时流式输出 | asyncio 异步生成器 | 线程 + 队列 | 天然拉式背压 |
| Windows 桌面/服务 | 线程或 asyncio | 多进程（注意 spawn） | 避免 fork 与 guard 问题 |

### 10.2 混合架构与反模式

真实系统通常是混合的：

```text
FastAPI (asyncio)
  ├── async HTTP 客户端 → LLM / 工具 API
  ├── asyncio.to_thread → 阻塞 SDK、文件 IO
  └── run_in_executor(ProcessPool) → 本地 CPU 计算
```

常见反模式：

- **每个请求开一个线程**：高并发下线程创建与栈内存压垮系统，应使用有界线程池或协程。
- **每个小任务开一个进程**：启动与序列化成本远大于计算，应批量提交。
- **在 async def 里调用 requests / time.sleep**：卡死事件循环，必须下沉到线程或改异步库。
- **用无界队列做缓冲**：流量突增时 OOM，必须有 `maxsize` 或信号量。
- **多进程共享可变全局状态**：子进程各有一份，改了不同步；应消息传递或显式共享内存。
- **在协程里用 threading.Lock**：锁等待会阻塞事件循环，应使用 `asyncio.Lock`。
- **混用多个事件循环**：一个线程一个循环，跨线程通信用 `run_coroutine_threadsafe`。

---

## 十一、常见坑

### 11.1 死锁与竞态

**死锁**最常见的原因是锁顺序不一致。两个线程分别持有 A、B 两把锁，再互相请求对方持有的锁，就会永久等待。修复方式是全局统一锁顺序，或使用带超时的 `acquire`。

```python
# 错误示例：不要直接运行
def transfer_a_to_b():
    with lock_a:
        with lock_b:
            pass

def transfer_b_to_a():
    with lock_b:
        with lock_a:
            pass
```

**竞态**最常见的是 check-then-act：

```python
cache = {}
key = "k"

def compute():
    return 42

if key not in cache:
    cache[key] = compute()   # 两个线程可能同时进入，重复计算
```

修复方式是用锁保护整个判断与写入，或使用 `setdefault`、`threading.Lock`、`asyncio.Lock` 等原子化手段。注意 GIL 不会让 `if` 加赋值的组合变成原子操作。

### 11.2 事件循环阻塞与任务丢失

在 `async def` 里调用 `time.sleep()`、`requests.get()`、同步数据库驱动、超大循环，都会阻塞事件循环。表现是“所有协程一起变慢”，而不是单个请求慢。

`asyncio.create_task()` 只保留弱引用，如果不保存返回值，任务可能被垃圾回收：

```python
background = set()

def spawn(coro):
    task = asyncio.create_task(coro)
    background.add(task)
    task.add_done_callback(background.discard)
```

“发射后不管”的任务如果抛异常，异常可能只出现在日志里，甚至被静默丢弃。至少加 `add_done_callback` 记录异常，或使用 `TaskGroup` 管理生命周期。

`gather(return_exceptions=False)` 在第一个异常处退出，但其余任务不会自动取消；如果调用方直接离开，后台任务可能继续运行。需要“一个失败全停”时用 `TaskGroup`。

### 11.3 取消、进程与线程池陷阱

- **吞掉 `CancelledError`**：清理后必须重新抛出，否则取消信号丢失，上层会一直等。
- **取消时做阻塞清理**：`finally` 里的同步网络请求会卡住事件循环；清理也应是异步的。
- **Windows 多进程忘记 `__main__` 保护**：子进程重新导入主模块，递归创建进程。
- **进程池嵌套**：父进程占满池后等待子进程，子进程又向同一个池提交任务，可能死锁。
- **Future 异常没人取**：`submit()` 后不调用 `result()`/`exception()`，异常会被静默吞掉；用 `add_done_callback` 记录。
- **线程池里做 CPU 密集任务**：受 GIL 限制，应该换进程池。
- **在异步代码里用 `threading.Lock`**：等待锁会阻塞整个事件循环，应使用 `asyncio.Lock`。
- **用 `asyncio.run()` 嵌套调用**：已有运行中的事件循环时会抛 `RuntimeError`，应 `await` 或使用 Runner。

---

## 十二、避坑指南

### 12.1 规则清单

| 症状 | 根因 | 修复 |
|------|------|------|
| CPU 密集多线程不提速 | GIL 串行化字节码 | 改用多进程或 C 扩展 |
| 所有请求一起变慢 | 事件循环被阻塞 | 用 `to_thread` 下沉阻塞调用 |
| Windows 进程数爆炸 | 缺少 `__main__` 保护 | 入口放到 guard 内 |
| 线程计数小于预期 | `+=` 非原子 | 用 `Lock` 保护读改写 |
| 任务偶尔不执行完 | `create_task` 无强引用 | 存入集合并清理 |
| 取消后程序挂起 | 吞掉 `CancelledError` | 清理后重新抛出 |
| 内存持续上涨 | 无界队列或无界并发 | 有界队列 + `Semaphore` |
| 进程池卡死 | 池嵌套或任务互相等待 | 扁平化任务、分离池 |
| 线程池任务异常丢失 | 未读取 `Future` | `result()` 或完成回调记录 |
| 多进程共享变量不同步 | 进程内存独立 | 消息传递或共享内存 |
| 异步里锁死 | 用了 `threading.Lock` | 改用 `asyncio.Lock` |
| 流式接口断开后资源泄漏 | 未处理取消 | `finally` 关闭上游、释放许可 |

八条工程纪律：

1. **先判断 CPU/IO，再选工具**，不要先选线程或协程。
2. **共享可变状态必须有锁或所有权边界**，跨进程优先消息传递。
3. **所有队列有界**，所有外部调用有超时。
4. **异步链路全链路异步**，一处阻塞会拖垮整个循环。
5. **后台任务必须有强引用和异常处理**。
6. **取消是正常控制流**，清理后重新抛出。
7. **多进程入口必须可导入、可 pickle、有 guard**。
8. **并发度是配置，不是常量**，按下游容量和机器规格调整。

---

## 十三、高频面试题（10 道）

### 13.1 题目与参考答案

#### 题目 1：并发、并行、异步有什么区别？

**参考答案：** 并发是多个任务在重叠时间段内推进，强调任务编排；并行是多个任务在同一时刻真正同时执行，需要多核；异步是等待时不占住执行者，先去做别的事。单核可以并发但不能并行，单线程可以异步但不是并行。

Python 中线程和协程提供并发，多进程提供并行，asyncio 提供异步编程模型。三者不是互斥关系：一个异步服务可以同时使用线程池处理阻塞 SDK、进程池处理 CPU 计算。

#### 题目 2：GIL 是什么？为什么存在？对 CPU 和 IO 任务分别有什么影响？

**参考答案：** GIL 是 CPython 的全局解释器锁，保证同一时刻只有一个线程执行 Python 字节码。它主要为了简化引用计数内存管理和 C 扩展实现，并保持单线程性能。GIL 是 CPython 实现细节，不是语言规范。

CPU 密集任务中，线程大部分时间占着 GIL，多线程无法利用多核，还可能因切换变慢；IO 密集任务在阻塞调用时会释放 GIL，其他线程可以继续，因此多线程仍有效。C 扩展在底层计算时也可能释放 GIL，具体取决于实现。

#### 题目 3：多线程、多进程、协程如何选型？Windows 下多进程要注意什么？

**参考答案：** IO 密集且使用阻塞库时选线程池；海量网络 IO、希望全链路异步时选 asyncio；CPU 密集、需要绕过 GIL 时选多进程；需要强隔离时也选多进程。简单批量任务可以用 `concurrent.futures` 统一接口。

Windows 只支持 `spawn`，子进程会重新导入主模块，因此入口必须放在 `if __name__ == "__main__":` 下；传给子进程的函数与参数必须可 pickle，最好是顶层函数；不要依赖模块级共享状态。忘记 guard 会导致递归创建进程或 bootstrapping 错误。

#### 题目 4：`Lock` 和 `RLock` 有什么区别？死锁的四个条件是什么，如何避免？

**参考答案：** `Lock` 不可重入，同一线程重复获取会阻塞自己；`RLock` 允许同一线程重复获取，但需要释放相同次数。临界区可能递归调用同一加锁函数时用 `RLock`，否则优先 `Lock`。

死锁四个条件：互斥、持有并等待、不可抢占、循环等待。工程上最有效的避免方式是统一锁顺序、缩小临界区、避免嵌套锁、使用 `acquire(timeout=...)` 超时回退，以及不在持锁时调用外部代码。

#### 题目 5：`Future` 是什么？`cancel()` 能取消正在运行的任务吗？

**参考答案：** `Future` 是异步结果的占位对象，代表一个尚未完成的操作，提供 `result()`、`exception()`、`done()`、`cancel()` 等方法。线程池和进程池的 `submit()` 都返回 `Future`。

`cancel()` 只能取消尚未开始执行的任务；已经运行的任务无法通过 Future 取消。线程无法被安全强杀；进程可以被终止，但会丢失清理逻辑。Python 3.9+ 的 `shutdown(cancel_futures=True)` 可以取消队列中未开始的任务。

#### 题目 6：asyncio 事件循环的原理是什么？协程、Task、Future 有什么区别？

**参考答案：** 事件循环在单线程中维护就绪回调、定时器和 IO 事件，协程在 `await` 处让出控制权，循环再调度其他就绪任务。它是协作式调度，没有抢占，因此任何阻塞调用都会卡住整个循环。

协程是 `async def` 调用后返回的可等待对象，本身不会自动执行；Task 是协程的调度包装，注册到事件循环并保存状态；Future 是一个更底层的结果占位对象，Task 是 Future 的子类。`await` 协程是内联执行，`create_task` 才会并发调度。

#### 题目 7：`gather` 和 `wait` 有什么区别？`return_exceptions` 有什么作用？

**参考答案：** `gather` 等待多个 awaitable，按输入顺序返回结果；默认在第一个异常处向调用方抛出，其他任务不会自动取消。`return_exceptions=True` 会把异常作为结果返回，适合部分失败也要汇总的场景。

`wait` 返回 `(done, pending)` 两个集合，不会抛异常，可以指定 `FIRST_COMPLETED`、`FIRST_EXCEPTION`、`ALL_COMPLETED` 条件，适合自己控制超时、取消和退出。`as_completed` 则按完成顺序逐个产出结果。

#### 题目 8：如何取消协程任务？取消时如何清理资源？为什么 `CancelledError` 继承 `BaseException`？

**参考答案：** 调用 `Task.cancel()` 发起取消，任务在下一次 `await` 处收到 `CancelledError`。协程应在 `try/finally` 或 `except CancelledError` 中关闭连接、释放锁、清理临时文件，然后重新抛出取消信号，不能吞掉。

`CancelledError` 继承 `BaseException`，是为了避免被常见的 `except Exception` 误捕获，从而保证取消信号能可靠传播。清理代码应当是异步且快速的，不能在取消路径里做阻塞 IO。

#### 题目 9：在 `async def` 里调用 `time.sleep` 或 `requests` 会怎样？FastAPI 中如何处理？

**参考答案：** 会阻塞事件循环线程，导致同一 worker 内的所有协程和请求都停住，表现为整体延迟上升甚至超时。`time.sleep`、同步 HTTP 库、同步数据库驱动都属于阻塞调用。

处理方式：优先改用异步库；无法改写时用 `await asyncio.to_thread(...)` 或 `loop.run_in_executor(...)` 把阻塞调用下沉到线程池；CPU 密集计算用进程池。FastAPI 中 `def` 路由会自动在线程池执行，`async def` 路由则直接在事件循环执行，必须自己保证不阻塞。

#### 题目 10：如何设计一个高并发 LLM 调用服务？请说明限流、超时、重试和背压。

**参考答案：** 用 asyncio + 异步 HTTP 客户端做并发；用 `Semaphore` 限制在途请求数，必要时叠加令牌桶限制 QPS；为单次请求、单轮流式、整个任务分别设置超时；只对幂等请求重试，采用指数退避加随机抖动；用有界队列或拉式异步生成器实现背压，防止生产者压垮内存和下游。

还要考虑：连接池复用、DNS 缓存、失败熔断、请求 ID 与 token 用量观测、客户端断开时取消上游请求并释放信号量。多进程部署时每个 worker 有自己的事件循环和限流器，总并发是各 worker 之和，需要按实例统一规划。

---

## 十四、本章学习自检

### 14.1 自检清单

**概念与 GIL**

- [ ] 能区分并发、并行、异步，并各举一个 Python 例子
- [ ] 能解释 GIL 约束的是什么、不约束什么
- [ ] 能说明 CPU 密集与 IO 密集任务在多线程下的不同表现
- [ ] 知道 `counter += 1` 为什么不是原子操作
- [ ] 能说出至少三种绕过 GIL 的路径及其代价

**线程与进程**

- [ ] 能正确创建、`join` 线程，并说明守护线程的风险
- [ ] 会用 `Lock` / `RLock` 保护临界区
- [ ] 能说出死锁四个条件与至少两种避免方式
- [ ] 会用 `queue.Queue` 实现有界生产者-消费者
- [ ] 会用 `ThreadPoolExecutor` 提交任务并收集结果
- [ ] 能说明 Windows `spawn` 的三条硬规则
- [ ] 知道 `Queue`、`Pipe`、`Manager`、`shared_memory` 的适用差异
- [ ] 能解释进程池嵌套与小任务多进程的风险

**asyncio**

- [ ] 能解释事件循环如何调度协程
- [ ] 能区分协程、Task、Future
- [ ] 会用 `gather`、`wait`、`as_completed` 并说明差异
- [ ] 知道 `gather` 默认不会取消其余任务
- [ ] 会用 `wait_for` / `asyncio.timeout` 设置超时
- [ ] 能正确取消任务并在 `finally` 中清理
- [ ] 知道 `create_task` 需要保存强引用
- [ ] 会用 `Semaphore` 限流、用有界 `Queue` 做背压
- [ ] 会用 `asyncio.to_thread` 下沉阻塞调用
- [ ] 知道 `CancelledError` 为什么继承 `BaseException`

**框架与工程**

- [ ] 能说明 FastAPI 中 `async def` 与 `def` 路由的执行位置
- [ ] 能识别并修复 `async def` 里的阻塞调用
- [ ] 会用 `StreamingResponse` + 异步生成器实现流式输出
- [ ] 知道客户端断开时如何清理上游资源
- [ ] 能设计 LLM 调用的超时、重试、限流与背压
- [ ] 能根据任务画像选择合适的并发模型
- [ ] 能说出至少五个本章的常见坑及其修复方式

---

> 并发选型没有银弹：线程解决“阻塞等待”，进程解决“多核计算”，协程解决“海量等待下的调度开销”。把任务画像、共享状态和失败边界想清楚，工具自然就选对了。
