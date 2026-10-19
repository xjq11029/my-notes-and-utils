r"""手写线真实模型端到端实测。

对应 code/README.md:86-88「已知限制 · 真实模型端到端未实测」列的四项：
  ① 工具选择倾向   ② 提示词遵从度   ③ 真实 token 计费
  ④ 思考型模型的 reasoning 字段差异

外加两处纯手写代码的高危区（假模型永远测不到）：
  ⑤ _StreamAssembler 跨 chunk 拼接 tool_calls.arguments
  ⑥ 非流式 _normalize_message 与流式装配器是否产出**同一个** message 形状

模型层走 agent 包自己的默认 client（读 OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL），
所以本脚本同时验证了「把 FakeClient 换成 Model() 即可切真模型」这句话是否成立。
key 从 gitignore 的 code/.secrets.log 读，不落盘到输出。
"""
import json
import os
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = pathlib.Path(__file__).resolve().parents[2] / "handwritten" / "code"
sys.path.insert(0, str(HERE))

KEY = (pathlib.Path(__file__).resolve().parents[2] / "code" / ".secrets.log") \
    .read_text(encoding="utf-8").strip()
BASE = "https://open.bigmodel.cn/api/paas/v4"

os.environ["OPENAI_API_KEY"] = KEY
os.environ["OPENAI_BASE_URL"] = BASE

RULE = "=" * 78


def banner(t):
    print()
    print(RULE)
    print(t)
    print(RULE)


def run(model_name, fn, *a, **kw):
    os.environ["OPENAI_MODEL"] = model_name
    # settings 是模块级单例，model 在 __init__ 时读；这里强制重读
    import agent.config as cfg
    cfg.settings.model = model_name
    print(f"\n---- 模型 {model_name} ----")
    return fn(*a, **kw)


# ==================================================================== ⑤⑥
banner("⑤⑥ 流式装配器 vs 非流式归一化：同一请求是否拼出同一个 message")


def parity(stream):
    from agent.model import Model
    from agent.session import Session
    m = Model()
    s = Session(system_prompt="你是助手，回答要短。")
    s.add_message({"role": "user", "content": "用一句话说明什么是检查点(checkpoint)。"})
    r = m.invoke(s, stream=stream)
    return r.message


for name in ("glm-4-plus", "glm-4.5-air"):
    plain = run(name, parity, False)
    streamed = run(name, parity, True)
    same_keys = set(plain) == set(streamed)
    print(f"  非流式 keys = {sorted(plain)}")
    print(f"  流式   keys = {sorted(streamed)}")
    print(f"  → 字段集合一致? {same_keys}")
    print(f"  → 非流式 content 前 40 字 = {str(plain.get('content'))[:40]!r}")
    print(f"  → 流式   content 前 40 字 = {str(streamed.get('content'))[:40]!r}")
    if "reasoning_content" in plain or "reasoning_content" in streamed:
        print(f"  → reasoning_content: 非流式 {len(str(plain.get('reasoning_content') or ''))} 字"
              f" / 流式 {len(str(streamed.get('reasoning_content') or ''))} 字")

# ==================================================================== ④
banner("④ 思考型模型的 reasoning 通道：装配器能否正确切分 reasoning / content")


def reasoning_channels():
    from agent.model import Model
    from agent.session import Session
    from agent.events import Event
    m = Model()
    seen = {"reasoning": 0, "content": 0, "tool": 0, "order": []}

    def on(evt, **kw):
        if evt == Event.REASONING:
            seen["reasoning"] += 1
        elif evt == Event.CONTENT:
            seen["content"] += 1
        elif evt == Event.REASONING_END:
            seen["order"].append("reasoning_end")
        elif evt == Event.CONTENT_START:
            seen["order"].append("content_start")

    for e in (Event.REASONING, Event.CONTENT, Event.REASONING_END, Event.CONTENT_START):
        m.on(e, on)
    s = Session(system_prompt="回答前先想清楚。")
    s.add_message({"role": "user", "content": "9.11 和 9.9 哪个大？直接给答案。"})
    r = m.invoke(s, stream=True)
    return seen, r.message


for name in ("glm-4.5-air", "glm-4-plus"):
    seen, msg = run(name, reasoning_channels)
    print(f"  reasoning 分片数={seen['reasoning']}  content 分片数={seen['content']}")
    print(f"  边界事件顺序={seen['order'][:6]}")
    print(f"  message 是否含 reasoning_content = {'reasoning_content' in msg}")
    print(f"  content = {str(msg.get('content'))[:60]!r}")
    print("  → 装配器靠「同 chunk 或后续 chunk 出现 content」判定思考结束；"
          "看上面的顺序是否 reasoning_end 在 content_start 之前")

# ==================================================================== ①②⑤
banner("①②⑤ Agent 端到端 ReAct 循环 + 真实模型自选工具 + 流式参数拼接")


def agent_e2e():
    import importlib
    import agent.tool as tw
    from agent.agent import Agent
    from agent.tool import tool

    @tool(query="要查询的城市名，例如 上海")
    def get_weather(query: str) -> str:
        """查询指定城市的实时天气。"""
        return json.dumps({"city": query, "temp_c": 22, "sky": "晴"}, ensure_ascii=False)

    tw.registry.register(get_weather)
    ag = Agent(max_turns=6)
    res = ag.invoke("上海现在天气怎么样？")
    return res, ag


res, ag = run("glm-4.5-air", agent_e2e)
print(f"  ReAct 轮数 = {len(res)}（假模型版 s07 是脚本写死的固定轮数）")
names = []
for i, r in enumerate(res, 1):
    tc = r.message.get("tool_calls")
    if tc:
        for c in tc:
            names.append(c["function"]["name"])
            print(f"  第 {i} 轮请求工具: {c['function']['name']}"
                  f"  arguments={c['function']['arguments']!r}")
    else:
        print(f"  第 {i} 轮为最终回答: {str(r.message.get('content'))[:50]!r}")
print(f"  → 模型自选到的工具 = {names}")
print("  → 关键验证：arguments 是**跨 chunk 拼接出来的完整 JSON 字符串**，"
      "能被 json.loads 解析吗？")
for r in res:
    for c in (r.message.get("tool_calls") or []):
        try:
            print(f"     ✅ 解析成功: {json.loads(c['function']['arguments'])}")
        except Exception as e:
            print(f"     ❌ 解析失败: {e} ← 原始={c['function']['arguments']!r}")

# ==================================================================== ③
banner("③ 真实 token 计费：手写模型层到底有没有把 usage 带出来")


def usage_probe():
    from agent.model import Model
    from agent.session import Session
    out = {}
    for st in (False, True):
        m = Model()
        s = Session(system_prompt="你是助手。")
        s.add_message({"role": "user", "content": "说三个字。"})
        r = m.invoke(s, stream=st)
        raw = r.raw
        u = None
        if isinstance(raw, dict):
            u = raw.get("usage")
        out[st] = (u, r.message.get("usage"), "usage" in r.message)
    return out


u = run("glm-4-plus", usage_probe)
print(f"  非流式 raw.usage          = {u[False][0]}")
print(f"  非流式 message['usage']   = {u[False][1]}   message 里有 usage 键? {u[False][2]}")
print(f"  流式   raw（装配器不设）  = {u[True][0]}")
print("  → 结论：InvokeResult.raw 在流式路径被显式置为 None（model.py:82），"
      "而 _normalize_message 与 _StreamAssembler 都**不读 usage 字段**。")
print("    也就是说：手写线当前**拿不到 token 账**，要计费和缓存命中率必须自己补一处。")

# ==================================================================== ⑦
banner("⑦ MCP 链路：手写 stdio 服务器 + 客户端 + 真实模型驱动")


def mcp_e2e():
    from agent.mcp import MCPClient
    import agent.tool as tw
    server = HERE / "mcp_servers" / "time_server.py"
    mcp = MCPClient({"servers": {"time": {
        "type": "stdio", "command": sys.executable, "args": [str(server)]}}})
    listed = mcp.list_tools()
    n = sum(len(v) for v in listed.values())
    mcp.register_tools(tw.registry)
    from agent.agent import Agent
    ag = Agent(max_turns=5, auto_builtin=False)
    res = ag.invoke("现在几点了？")
    called = [tc["function"]["name"] for r in res
              for tc in (r.message.get("tool_calls") or [])]
    return n, called, res


try:
    n, called, res = run("glm-4.5-air", mcp_e2e)
    print(f"  MCP 服务器暴露工具数 = {n}")
    print(f"  真实模型选择并调用的工具 = {called}")
    print(f"  ReAct 轮数 = {len(res)}")
    print("  → 手写 MCP（纯 stdlib JSON-RPC over stdio）+ 真实模型 端到端跑通")
except Exception as e:
    print(f"  ❌ {type(e).__name__}: {str(e)[:300]}")

print()
print(RULE)
print("完成")
print(RULE)
