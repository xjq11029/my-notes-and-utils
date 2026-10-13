"""Agent：把模型、会话、工具、监听器编排成一个 ReAct 循环。

Agent 不是新协议，而是一个 while 循环::

    调模型 → 模型请求工具？ → 执行工具、结果回灌 → 再调模型 → … → 最终回答

终止条件只有一个：模型不再请求工具（registry.invoke 返回 None）。
max_turns 是安全阀：防止模型陷入工具调用死循环——这是 Loop Engineering
最基本的一条实践。
"""
import sys

from agent.model import InvokeResult, Model
from agent.session import Session
from agent.skill import make_load_skill_tool
from agent.tool import registry
from agent.tool import builtin as builtin_tools


class Agent:
    """一个可直接对话的智能体。

    参数：
        client:        模型客户端（默认按环境变量创建；离线注入 FakeClient）
        model_listener: 模型事件监听器（如 ModelPrinterListener）
        system_prompt: 系统提示词；缺省时用 render_prompt 渲染内置模板
        skills:        SkillRegistry；提供后自动注册 load_skill 工具，
                       并把技能清单注入默认系统提示词
        max_turns:     ReAct 循环的最大轮次（安全阀）
        auto_builtin:  是否自动注册三个内置工具（读文件/写文件/执行命令）
    """

    def __init__(
        self,
        client=None,
        model_listener=None,
        system_prompt: str | None = None,
        skills=None,
        max_turns: int = 10,
        auto_builtin: bool = True,
    ) -> None:
        self.max_turns = max_turns
        self.model = Model(client)
        if model_listener is not None:
            model_listener.listen(self.model)

        if auto_builtin:
            for t in (builtin_tools.read_file, builtin_tools.write_file,
                      builtin_tools.bash_command):
                registry.register(t)
        if skills is not None:
            registry.register(make_load_skill_tool(skills))

        tools = list(registry.schemas())
        if system_prompt is None:
            from agent.prompt import render_prompt
            system_prompt = render_prompt(skills=skills.list_skills() if skills else [])
        self.session = Session(system_prompt=system_prompt, tools=tools)

    def invoke(self, query: str) -> list[InvokeResult]:
        """处理一条用户输入：跑完整个 ReAct 循环，返回每轮的调用结果。"""
        self.session.add_message({"role": "user", "content": query})
        results: list[InvokeResult] = []
        for _ in range(self.max_turns):
            resp = self.model.invoke(self.session, stream=True)
            results.append(resp)
            tool_results = registry.invoke(self.session.messages[-1])
            if tool_results is None:
                return results  # 模型不再请求工具：任务完成
            self.session.messages.extend(tool_results)
        print(f"[Agent] 已达最大轮次 {self.max_turns}，强制停止。",
              file=sys.stderr)
        return results
