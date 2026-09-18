# Python 通用工具（src/python）

从多个项目抽取的、与业务解耦的通用 Python 工具，**仅依赖标准库**，无第三方包依赖。

## 文件清单

- [`utils.py`](utils.py) —— `ensure_dir` / `timestamp_now` / `read_json` / `write_json` / `retry` 装饰器

## 使用约定

- 直接复制到目标工程的工具目录即可使用；无需 `pip install`。
- 与 `src/js/` 的 JS 工具（`src/js/README.md`）同源，构成跨语言通用工具集。

> 各目录的 `README.md` 必须真实反映该目录实际情况；本目录随文件增减同步更新。
