"""s07 Agent：把模型 / 会话 / 工具 / 监听器组装成一个可对话的智能体。

运行：python s07_agent.py

本脚本演示三件事：
1. Agent 的组装与对话（含内置工具自动注册）；
2. print_friendly 作为「行车记录仪」查看完整轨迹；
3. max_turns 安全阀：模型陷入死循环时的强制终止。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _fake_llm import FakeClient

from agent.agent import Agent
from agent.printer import ModelPrinterListener
from agent.tool import tool

# ------------------------------------------------------------------
# 1) 组装并对话
# ------------------------------------------------------------------
print("== 1. Agent 组装与一次多步任务 ==")


@tool(query="搜索关键字")
def web_search(query: str) -> str:
    """根据关键字搜索网络，返回结构化搜索结果（教学：固定样例）"""
    return ('{"results": ['
            '{"title": "WorkBuddy 发布 5.0", "snippet": "支持多智能体协作"},'
            '{"title": "Buddy 加油站上新", "snippet": "签到积分可兑权益"}]}')


# 真实接入只需把函数体换成 Tavily / Firecrawl 等 API 调用（需 API Key，未实测）：
#   from tavily import TavilyClient
#   resp = TavilyClient(api_key=...).search(query=query)
#   return json.dumps(resp, ensure_ascii=False)

from agent.tool import registry
registry.register(web_search)  # 内置工具由 Agent 自动注册，自定义工具要显式注册

client = FakeClient([
    {"match": "AI 领域最近有什么新闻",
     "resp": {"tool_calls": [{"name": "web_search", "arguments": {"query": "AI 最近新闻"}}]}},
    {"match": lambda msgs: any(m.get("role") == "tool" for m in msgs),  # 字符串匹配只看最后一条 user 消息，工具往返后要改用函数匹配
     "resp": {"content": "搜到两条：WorkBuddy 发布 5.0（多智能体协作）；Buddy 加油站上新（签到积分兑权益）。"}},
])

listener = ModelPrinterListener()
agent = Agent(client=client, model_listener=listener)

print("--- 终端输出开始 ---")
agent.invoke("AI 领域最近有什么新闻？")
print("--- 终端输出结束 ---")

print("\n== 2. 行车记录仪：完整消息序列 ==")
agent.session.print_friendly()

# ------------------------------------------------------------------
# 2) max_turns 安全阀
# ------------------------------------------------------------------
print("\n== 3. max_turns 安全阀：模型疯起来时兜底 ==")
client2 = FakeClient([
    {"match": "死循环", "resp": {"tool_calls": [{"name": "web_search", "arguments": {"query": "x"}}]},
     "once": False},
], default_content="(final)")
agent2 = Agent(client=client2, max_turns=3)
import contextlib
import io
buf = io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
    agent2.invoke("死循环测试")
print(f"模型每次都请求工具 → 第 {agent2.max_turns} 轮被强制停止（消息数 {len(agent2.session.messages)}）")
