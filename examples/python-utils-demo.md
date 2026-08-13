# Python 工具函数用法示例

演示如何使用 `src/python/utils.py` 中的常用工具函数。

## 引入方式

将 `src/python/utils.py` 复制到你的项目，或把 `src/python` 加入 `PYTHONPATH` 后导入：

```python
import sys
sys.path.insert(0, "/path/to/src/python")
from utils import ensure_dir, timestamp_now, read_json, write_json, retry
```

> 说明：以下示例假设 `utils.py` 已处于可导入路径中。

## 示例 1：确保目录存在并打印时间戳

```python
from utils import ensure_dir, timestamp_now

path = ensure_dir("./output/logs")
print("已确保目录存在：", path)
print("当前时间：", timestamp_now())
```

## 示例 2：写入并读取 JSON

```python
from utils import write_json, read_json

data = {"name": "demo", "items": [1, 2, 3]}
write_json("./output/demo.json", data)
loaded = read_json("./output/demo.json")
print("读取结果：", loaded)
```

## 示例 3：用 retry 装饰器提升健壮性

```python
from utils import retry
import random

@retry(times=3)
def unstable_call():
    if random.random() < 0.5:
        raise RuntimeError("瞬时失败")
    return "ok"

print(unstable_call())
```
