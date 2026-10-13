"""s08 Skill：提示词按需加载——渐进式披露的完整实现。

运行：python s08_skill.py

场景：天气查询的详细指引只有用户问天气时才用得上。
- 不用 Skill：把指引塞进系统提示词 → 每一轮都在为它付费（膨胀）；
- 用 Skill：系统提示词只放「名字 + 一句话描述」（几十 token），
  模型判断需要时调 load_skill 拿全文（渐进式披露）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _fake_llm import FakeClient

from agent.agent import Agent
from agent.skill import SkillRegistry
from agent.tool import tool, registry

# ------------------------------------------------------------------
# 1) 扫描技能目录：每个 SKILL.md 只取 frontmatter
# ------------------------------------------------------------------
skill_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
skills = SkillRegistry(skill_dir)

print("== 1. 扫描到的技能（注入系统提示词的只有这些）==")
for s in skills.list_skills():
    print(f"- {s['name']}：{s['description']}")

print("\n== 2. 系统提示词中的技能清单节（截取）==")
from agent.prompt import render_prompt
prompt = render_prompt(skills=skills.list_skills())
idx = prompt.find("## 可用技能")
print(prompt[idx:idx + 200] + "…")

# ------------------------------------------------------------------
# 2) 注册天气工具 + 组装 Agent
# ------------------------------------------------------------------


@tool(city="城市名")
def get_weather(city: str) -> str:
    """查询一个城市的实时天气（教学：固定样例；真实接入需天气 API）"""
    return '{"city": "哈尔滨", "temperature": "-8", "condition": "晴", "wind": "西北风3级"}'


registry.register(get_weather)

def tool_text(msgs):
    return " ".join(m.get("content") or "" for m in msgs if m.get("role") == "tool")


client = FakeClient([
    {   # 第 1 轮：模型看到技能清单，判断需要天气技能 → 先读全文
        "match": "天气",
        "resp": {"tool_calls": [{"name": "load_skill", "arguments": {"name": "weather-report"}}]},
    },
    {   # 第 2 轮：按技能指引，调天气工具（上下文里已出现技能全文）
        "match": lambda msgs: "weather-report" in tool_text(msgs),
        "resp": {"tool_calls": [{"name": "get_weather", "arguments": {"city": "哈尔滨"}}]},
    },
    {   # 第 3 轮：按技能的播报格式回答
        "match": lambda msgs: '"temperature"' in tool_text(msgs) or "-8" in tool_text(msgs),
        "resp": {"content": "哈尔滨当前 -8°C，晴，西北风3级；建议穿羽绒服并注意防风。"},
    },
])

agent = Agent(client=client, skills=skills)
print("\n== 3. 对话：模型自己走完「读技能 → 调工具 → 按规范回答」==")
agent.invoke("今天天气怎么样？")

print("\n== 4. 完整轨迹（三次工具往返：load_skill → get_weather）==")
agent.session.print_friendly()

print("\n== 5. 对照：没有 Skill 时，模型对「怎么播报」一无所知 ==")
client2 = FakeClient([
    {"match": "天气", "resp": {"content": "我不知道天气如何，而且没有任何工具可用。"}},
])
agent2 = Agent(client=client2, skills=None)
agent2.invoke("今天天气怎么样？")
print("(无技能清单 → 模型不知道任何工作指引；本例剧本也未安排工具调用 → 只能空泛回答)")
