# -*- coding: utf-8 -*-
"""第 4 章示例：结构化输出 —— 四种 schema 模式与两种策略。

演示六件事：
  1. 手动「要求 JSON + 解析 + 校验」的脆弱链路 vs with_structured_output 一步到位
  2. 四种 schema 模式：Pydantic / TypedDict / JSON Schema dict / @dataclass
  3. 两种策略：method="function_calling" 与 method="json_schema"
  4. 类型校验：非法参数抛什么错；include_raw 把错误收进 parsing_error
  5. 输出解析器（PydanticOutputParser 等）：不推荐，但 API 仍在
  6. 与 agent 侧 response_format 的关系（第 5 章的主题）

运行：python 04_structured_output.py
"""

import json
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Optional, TypedDict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, show, tool_call
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import BaseModel, Field, ValidationError

ARGS = {"name": "张三", "age": 30, "occupation": "软件工程师"}
TEXT = "张三是一名 30 岁的软件工程师"


# ---------------------------------------------------------------------------
# 1. 为什么需要结构化输出：手动链路的四个环节，每个都能静默出错
# ---------------------------------------------------------------------------
print("=" * 72)
print("① 手动链路 vs with_structured_output")
print("=" * 72)

# 传统做法：提示词里求模型吐 JSON，然后自己解析、自己校验、自己建对象
raw = '{"name": "张三", "age": "三十", "occupation": "软件工程师"}'  # 模型把年龄写成了中文
data = json.loads(raw)
print(f"  json.loads 成功，拿到 dict：{data}")
print(f"  手动校验 isinstance(data['age'], int) → {isinstance(data['age'], int)}")
print("  → 少写一个 if，这个「三十」就会一路流到下游数据库里。")

# 结构化输出：schema 声明一次，绑定、约束、解析、校验都由框架完成
class Person(BaseModel):
    """人物信息"""
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")


model = ScriptedChatModel(script=[tool_call("Person", ARGS, "c1")])
person = model.with_structured_output(Person).invoke(TEXT)
print(f"  with_structured_output(Person) → {type(person).__name__} 实例：{person!r}")
print(f"  直接点属性：person.name={person.name!r} person.age={person.age!r}")
print("  → 字段的 description 会被转成 JSON Schema 交给模型，模型侧的约束 + 客户端的校验一次配好。")

print()
print("  schema 交给模型时长这样（convert_to_openai_tool 的产物）：")
print("   ", json.dumps(convert_to_openai_tool(Person), ensure_ascii=False)[:150], "...")


# ---------------------------------------------------------------------------
# 2. 四种 schema 模式：只有 Pydantic 返回实例、只有 Pydantic 做校验
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("② 四种 schema 模式：各自的返回类型")
print("=" * 72)


class PersonDict(TypedDict):
    """人物信息（TypedDict）"""
    name: Annotated[str, "姓名"]
    age: Annotated[int, "年龄"]
    occupation: Annotated[str, "职业"]


PERSON_JSON_SCHEMA = {
    "title": "PersonJson",
    "description": "人物信息（JSON Schema）",
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "姓名"},
        "age": {"type": "integer", "description": "年龄"},
        "occupation": {"type": "string", "description": "职业"},
    },
    "required": ["name", "age", "occupation"],
}


@dataclass
class PersonDC:
    """人物信息（dataclass）"""
    name: str
    age: int
    occupation: str


# 为什么这么分：四种模式的能力差别只在「能不能表达约束」和「返回什么」，
# 不在「能不能用」——四种都能绑到模型上，只有 Pydantic 多一层运行时校验。
# 关键点：模型要回吐的工具名，就是 convert_to_openai_tool 生成的这个名字。
for label, schema in [
    ("Pydantic", Person),
    ("TypedDict", PersonDict),
    ("JSON Schema", PERSON_JSON_SCHEMA),
    ("@dataclass", PersonDC),
]:
    tool_name = convert_to_openai_tool(schema)["function"]["name"]
    m = ScriptedChatModel(script=[tool_call(tool_name, ARGS, "c1")])
    out = m.with_structured_output(schema).invoke(TEXT)
    print(f"  {label:12s} 工具名={tool_name:12s} 返回 {type(out).__name__:8s} {out!r}")

print("  → 工具名不是随便取的：Pydantic/TypedDict/dataclass 取类名，JSON Schema 取 title；")
print("     名字对不上，解析器找不到这条 tool_call，结果就是 None（见第 4 节）。")


# ---------------------------------------------------------------------------
# 3. 两种策略：function_calling 与 json_schema
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("③ 两种策略：method 参数")
print("=" * 72)


class SpyModel(ScriptedChatModel):
    """把 bind_tools 收到的东西打出来，看清两种策略的差别。"""

    def bind_tools(self, tools, **kwargs):
        names = [getattr(t, "__name__", None) or getattr(t, "name", None) for t in tools]
        print(f"    bind_tools 收到：{names}  额外参数：{sorted(kwargs)}")
        return super().bind_tools(tools, **kwargs)


for method in [None, "function_calling", "json_schema"]:
    label = "默认（不传 method）" if method is None else f'method="{method}"'
    m = SpyModel(script=[tool_call("Person", ARGS, "c1")])
    sllm = m.with_structured_output(Person) if method is None else m.with_structured_output(Person, method=method)
    out = sllm.invoke(TEXT)
    print(f"  {label:22s} → {out!r}")

print("  → 实测（langchain 1.4.2）：在**基类**实现里 method 被直接丢掉，")
print("     三条路径都走 bind_tools + tool_choice；假模型上三者输出完全一致。")
print("     method=\"json_schema\" 的真实差别由 provider 子类实现（如 ChatOpenAI 会改用")
print("     response_format 的 json_schema 模式）——**需真实模型，本教程未实测**。")


# ---------------------------------------------------------------------------
# 4. 类型校验：只有 Pydantic 会抛错；include_raw 把错误降级成返回值
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("④ 类型校验：什么时候抛错、抛什么")
print("=" * 72)

# 4.1 非法参数
m = ScriptedChatModel(script=[tool_call("Person", {"name": "张三", "age": "三十", "occupation": "工程师"}, "c1")])
try:
    m.with_structured_output(Person).invoke(TEXT)
except ValidationError as exc:
    err = exc.errors()[0]
    print(f"  age 传中文 → {type(exc).__name__}：loc={err['loc']} type={err['type']}")
    print(f"             msg={err['msg']}")

# 4.2 缺字段
m = ScriptedChatModel(script=[tool_call("Person", {"name": "张三", "occupation": "工程师"}, "c1")])
try:
    m.with_structured_output(Person).invoke(TEXT)
except ValidationError as exc:
    err = exc.errors()[0]
    print(f"  漏填 age  → ValidationError：loc={err['loc']} type={err['type']}")

# 4.3 能强转就强转：Pydantic 默认是宽松模式，'30' 会被转成 30
m = ScriptedChatModel(script=[tool_call("Person", {"name": "张三", "age": "30", "occupation": "工程师"}, "c1")])
print(f"  age 传 '30' → {m.with_structured_output(Person).invoke(TEXT)!r}  （宽松模式，强转成功）")

# 4.4 其余三种模式：原样透传，字段名错了也不报错
m = ScriptedChatModel(script=[tool_call("PersonDict", {"title1": "盗梦空间", "year2": 2010}, "c1")])
print(f"  TypedDict 字段名全错 → {m.with_structured_output(PersonDict).invoke(TEXT)!r}  （不校验）")

# 4.5 include_raw=True：把 raw / parsed / parsing_error 一起给你
m = ScriptedChatModel(script=[tool_call("Person", {"name": "张三", "age": "三十", "occupation": "工程师"}, "c1")])
out = m.with_structured_output(Person, include_raw=True).invoke(TEXT)
print(f"  include_raw=True → keys={sorted(out)}")
print(f"    parsed={out['parsed']!r}")
print(f"    parsing_error={type(out['parsing_error']).__name__}")
print("  → include_raw 把「抛错」变成「返回值」：批量跑抽取任务时不会一条坏数据打断整批。")

# 4.6 工具名对不上：静默返回 None，这是最容易踩的一个
m = ScriptedChatModel(script=[tool_call("Person", ARGS, "c1")])
print(f"  脚本回吐 Person，但 schema 是 PersonDict → {m.with_structured_output(PersonDict).invoke(TEXT)!r}")
print("  → 不报错、不告警，只是 None。换 schema 时先确认工具名。")


# ---------------------------------------------------------------------------
# 5. 输出解析器：不推荐，但 API 仍在
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("⑤ 输出解析器（PydanticOutputParser）：不推荐，但 API 仍在")
print("=" * 72)


class Movie(BaseModel):
    """电影信息"""
    title: str = Field(description="电影标题")
    year: int = Field(description="上映年份")


parser = PydanticOutputParser(pydantic_object=Movie)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "回答用户问题，必须始终输出 JSON。{format_instructions}"),
        ("human", "问题：{question}"),
    ]
)
chain = prompt.partial(format_instructions=parser.get_format_instructions()) | ScriptedChatModel(
    script=[reply('{"title": "盗梦空间", "year": 2010}')]
) | parser
print(f"  正常 JSON → {chain.invoke({'question': '介绍《盗梦空间》'})!r}")

chain_bad = prompt.partial(format_instructions=parser.get_format_instructions()) | ScriptedChatModel(
    script=[reply("《盗梦空间》2010 年上映")]
) | parser
try:
    chain_bad.invoke({"question": "介绍《盗梦空间》"})
except Exception as exc:
    print(f"  非 JSON 文本 → {type(exc).__name__}: {str(exc).splitlines()[0][:70]}")
print("  → 老链路把 schema 拼成一段提示词塞进 system（format_instructions），再靠文本解析回来；")
print("     模型不听话就整条链断掉。v1 的路线是 with_structured_output，解析器只保留兼容。")


# ---------------------------------------------------------------------------
# 6. 与 agent 侧 response_format 的关系（第 5 章主题）
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("⑥ 与 agent 侧 response_format 的关系")
print("=" * 72)

# 模型先回一个非法参数，看 agent 怎么自救
m = ScriptedChatModel(
    script=[
        tool_call("Person", {"name": "张三", "age": "三十", "occupation": "工程师"}, "c1"),
        tool_call("Person", ARGS, "c2"),
    ]
)
agent = create_agent(model=m, tools=[], response_format=ToolStrategy(Person))
out = agent.invoke({"messages": [{"role": "user", "content": TEXT}]})
print(f"  result['structured_response'] = {out['structured_response']!r}")
show(out["messages"])
print(f"  模型被调用 {len(m.seen)} 次：第一次参数非法，框架把错误写回 ToolMessage，模型自己改对了。")

# 关掉重试就是直接抛
m2 = ScriptedChatModel(script=[tool_call("Person", {"name": "张三", "age": "三十", "occupation": "工程师"}, "c1")])
agent2 = create_agent(model=m2, tools=[], response_format=ToolStrategy(Person, handle_errors=False))
try:
    agent2.invoke({"messages": [{"role": "user", "content": TEXT}]})
except Exception as exc:
    print(f"  handle_errors=False → {type(exc).__name__}")
print("  → 这就是与 with_structured_output 的分工：模型侧用哪个方法绑定，agent 侧由")
print("     ToolStrategy / ProviderStrategy 决定，还多了「校验失败自动重试」这一步。")


# ---------------------------------------------------------------------------
# 附：枚举与可选字段（schema 表达能力的两个高频需求）
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("附：枚举与 Optional —— 约束字段的取值范围")
print("=" * 72)


class Priority(str, Enum):
    """紧急程度"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"


class Ticket(BaseModel):
    """工单信息"""
    title: str = Field(description="工单标题")
    urgency: Priority = Field(description="紧急程度")
    assignee: Optional[str] = Field(default=None, description="处理人，未知就留空")


m = ScriptedChatModel(
    script=[tool_call("Ticket", {"title": "订单未发货", "urgency": "高"}, "c1")]
)
ticket = m.with_structured_output(Ticket).invoke("订单一直没发货，很着急")
print(f"  {ticket!r}")
print(f"  ticket.urgency={ticket.urgency!r}（枚举成员） ticket.urgency.value={ticket.urgency.value!r}")
print(f"  ticket.assignee={ticket.assignee!r}（模型没给 → 落到默认值 None）")
