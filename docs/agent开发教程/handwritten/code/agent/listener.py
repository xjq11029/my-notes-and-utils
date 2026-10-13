"""监听器抽象：把「关心模型调用过程」的组件与模型层解耦。

Model 负责发事件，ModelListener 负责处理事件。
打印器、日志、UI、计费统计……都实现同一个接口，随时插拔。
"""
from agent.events import ALL_EVENTS


class ModelListener:
    """订阅一个 Model 的全部事件；子类实现 _handler。"""

    def listen(self, model) -> None:
        for event in ALL_EVENTS:
            model.on(event, self._handler)

    def _handler(self, event: str, **data) -> None:
        raise NotImplementedError
