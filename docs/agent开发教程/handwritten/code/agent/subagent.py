"""子代理（Sub Agent）：给每个子任务一个全新、干净的上下文。

为什么需要子代理：把一个大任务塞进单个 ReAct 循环，会把主上下文撑爆
——几十次工具往返、中间输出、报错重试全混在一起，注意力被稀释，
上下文费用也随轮次滚雪球。

子代理的做法：主代理只做宏观规划，把每个子任务派给一个拥有**独立会话**
的子代理；子代理在自己的上下文里消化全部细节，只把最终结论带回主上下文
——一层「上下文防火墙」。

教学实现为串行执行（输出确定、便于理解）；生产实现可用线程池/异步并发。
"""
from agent.agent import Agent
from agent.tool import tool


def make_create_agent_tool(agent_factory) -> object:
    """工厂：生成 create_agent 工具（闭包持有 agent_factory）。

    agent_factory() 每次调用返回一个全新 Agent——独立会话、共享工具注册表，
    但不继承主代理的任何消息历史。
    """

    @tool(agents="子代理配置数组，每项包含 name（子代理名字）和 query（交给它的任务描述）")
    def create_agent(agents: list[dict]) -> str:
        """启动一个或多个子代理分别执行任务，返回每个子代理的最终结论"""
        reports = []
        for spec in agents:
            sub = agent_factory()
            results = sub.invoke(spec.get("query", ""))
            turns = len(results)
            final = results[-1].message.get("content") if results else ""
            reports.append(
                f"【{spec.get('name', 'sub-agent')}】（{turns} 轮调用，"
                f"{len(sub.session.messages)} 条消息，上下文独立）\n{final}"
            )
        return "\n\n".join(reports)

    return create_agent
