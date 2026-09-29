# -*- coding: utf-8 -*-
"""第 3 章示例：Message 与提示词模板 —— 四种消息类型与模板渲染。

演示八件事：
  1. 四种消息类型（System / Human / AI / Tool）的字段与用途
  2. 两种构造方式：JSON dict 与消息对象，模型侧看到的是同一种东西
  3. content 与 content_blocks：多模态内容块（构造可测，真实调用未实测）
  4. 多轮对话历史的管理与裁剪：只保留最近 N 轮
  5. ChatPromptTemplate 的三种调用方式：invoke / format / format_messages
  6. ChatPromptTemplate 初始化的六种参数类型
  7. MessagesPlaceholder（消息占位符）与 partial()（部分变量预填充）
  8. 用假模型的 .seen 验证：模板渲染出的消息，就是模型实际收到的消息

运行：python 03_messages_prompts.py
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from _fake_model import ScriptedChatModel, reply, show
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

# ---------------------------------------------------------------------------
# 1. 四种消息类型：角色靠类型区分，不靠字符串
# ---------------------------------------------------------------------------
print("=" * 72)
print("① 四种消息类型：字段与用途")
print("=" * 72)

system_msg = SystemMessage("你是一个严谨的技术助教。")
human_msg = HumanMessage("上海天气怎么样？", name="alice")
ai_call = AIMessage(
    content="",
    tool_calls=[{"name": "get_weather", "args": {"city": "上海"}, "id": "call_1"}],
)
tool_msg = ToolMessage(content="上海：22°C，晴", tool_call_id="call_1", name="get_weather")
ai_final = AIMessage("上海今天 22°C，晴。")

show([system_msg, human_msg, ai_call, tool_msg, ai_final])
print()
print("  → System 定规则、Human 是输入、AI 是输出、Tool 回灌工具结果——四者用途不同，")
print("    所以框架用四个类而不是一个带 role 字符串的通用对象来区分。")
print(f"  → AIMessage.tool_calls 是「模型的意图」：{ai_call.tool_calls[0]['name']}"
      f"({ai_call.tool_calls[0]['args']})")
print(f"  → ToolMessage.tool_call_id={tool_msg.tool_call_id!r} 必须与上一条 AI 消息的 id 对上，")
print("    框架靠这个 id 把「工具结果」配回「是哪次调用」。")
print(f"  → HumanMessage 的 name={human_msg.name!r} 是元数据，用于多人对话里区分发言者；")
print("    是否透传给模型由供应商决定（见「四、常见坑」第 5 条）。")

# ---------------------------------------------------------------------------
# 2. 两种构造方式：JSON dict 与消息对象
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("② 两种构造方式：JSON dict 与消息对象")
print("=" * 72)

# 写法一：JSON dict（适合从数据库、HTTP 请求体里直接拿到的数据）
as_dicts = [
    {"role": "system", "content": "你是一个严谨的技术助教。"},
    {"role": "user", "content": "上海天气怎么样？"},
    {
        "role": "assistant",
        "content": "",
        "tool_calls": [{"name": "get_weather", "args": {"city": "上海"}, "id": "call_1"}],
    },
    {"role": "tool", "content": "上海：22°C，晴", "tool_call_id": "call_1"},
]

# 写法二：消息对象（本教程其余章节统一用这种）
as_objects = [
    SystemMessage("你是一个严谨的技术助教。"),
    HumanMessage("上海天气怎么样？"),
    AIMessage(
        content="",
        tool_calls=[{"name": "get_weather", "args": {"city": "上海"}, "id": "call_1"}],
    ),
    ToolMessage(content="上海：22°C，晴", tool_call_id="call_1"),
]

model = ScriptedChatModel(script=[reply("上海 22°C，晴。")])
model.invoke(as_dicts)
dict_seen = [type(m).__name__ for m in model.seen[-1]]
model.invoke(as_objects)
object_seen = [type(m).__name__ for m in model.seen[-1]]

print(f"  传 dict     → 模型侧收到: {dict_seen}")
print(f"  传消息对象  → 模型侧收到: {object_seen}")
print(f"  两者是否一致: {dict_seen == object_seen}")
print()
print("  → dict 在进入模型之前就被框架转成了消息对象，模型侧看到的完全一样。")
print("    所以「用哪种写法」只是你这一侧的偏好：写库/收报文用 dict 省事，")
print("    在代码里拼逻辑用消息对象更直观（有类型、能挂 tool_calls）。")
print("  → 但 dict 的键名是框架约定死的：assistant 的工具调用放 tool_calls，")
print("    tool 消息必须带 tool_call_id，写错就是校验报错，而不是静默忽略。")

# ---------------------------------------------------------------------------
# 3. content 与 content_blocks：弱类型内容 vs 标准化内容块
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("③ content 与 content_blocks：多模态内容块")
print("=" * 72)

plain = HumanMessage("你好")
print(f"  纯文本 content       : {plain.content!r}")
print(f"  纯文本 content_blocks: {plain.content_blocks}")

multimodal = HumanMessage(
    content_blocks=[
        {"type": "text", "text": "这张图里有什么？"},
        {"type": "image", "base64": "iVBORw0KGgoAAAANSUhEUg...(略)", "mime_type": "image/png"},
    ]
)
print(f"  多模态 content       : {multimodal.content}")
print(f"  多模态 content_blocks: {multimodal.content_blocks}")

ai_block = AIMessage(content=[{"type": "text", "text": "图里是一瓶香水。"}])
print(f"  从 content 反读 blocks: {ai_block.content_blocks}")

print()
print("  → content 是弱类型：纯文本时是 str，多模态时是 list[dict]；")
print("    content_blocks 是统一后的 list[TypedDict]，每个块都有 type 字段")
print("    （text / image / audio / video / tool_call / reasoning）。")
print("  → 写多模态用 content_blocks，读「思维链」「引用」也优先读 content_blocks。")
print("  ⚠️ 以上只验证了「构造与解析」。真实多模态调用（把图片发给模型）需要 API Key，未实测。")

# ---------------------------------------------------------------------------
# 4. 多轮对话历史的管理与裁剪
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("④ 多轮对话历史的管理与裁剪：只保留最近 N 轮")
print("=" * 72)


def keep_recent_messages(messages, max_pairs=2):
    """保留全部 system 消息 + 最近 max_pairs 轮对话（每轮 = 一问一答）。

    为什么单独挑出 system 消息：它是「角色设定」，丢掉之后模型的语气、
    约束会整体漂移；而更早的问答只是上下文，丢掉代价小得多。
    """
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    dialogue = [m for m in messages if not isinstance(m, SystemMessage)]
    return system_msgs + dialogue[-(max_pairs * 2):]


history = [SystemMessage("你是 Python 导师。")]
for q, a in [
    ("什么是列表？用一句解释", "列表是可变的有序序列。"),
    ("列表和元组有什么区别？用一句解释", "列表可变，元组不可变。"),
    ("什么是字典？用一句解释", "字典是键值对集合。"),
]:
    history.append(HumanMessage(q))
    history.append(AIMessage(a))

print(f"  原始历史: {len(history)} 条")
trimmed = keep_recent_messages(history, max_pairs=2)
print(f"  裁剪之后: {len(trimmed)} 条（system + 最近 2 轮）")
show(trimmed)

# 关键验证：模型没有记忆，「裁剪」发生在你这一侧
model = ScriptedChatModel(script=[reply("你第二个问题问的是列表和元组的区别。")])
model.invoke(trimmed + [HumanMessage("我第二个问题问的是什么？")])
print(f"  → 模型实际收到 {len(model.seen[-1])} 条消息（裁剪后的 5 条 + 新问题 1 条）")
print("  → 模型没有记忆：你给多少，它就看多少。裁剪是客户端的事，不是模型的事。")
print("  ⚠️ 按「条数」硬切有风险：如果被切掉的正好是 AI(tool_calls) 而留下它的")
print("     ToolMessage，就会出现「找不到对应调用的工具结果」，模型会报错或胡猜。")

# ---------------------------------------------------------------------------
# 5. ChatPromptTemplate 的三种调用方式
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("⑤ ChatPromptTemplate 的三种调用方式")
print("=" * 72)

template = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个 AI 开发工程师。你的名字是 {name}。"),
        ("human", "你能开发哪些 AI 应用?"),
        ("ai", "我能开发很多 AI 应用。"),
        ("human", "{user_input}"),
    ]
)
inputs = {"name": "小谷AI", "user_input": "你能帮我做什么?"}

prompt_value = template.invoke(inputs)
as_text = template.format(**inputs)
as_messages = template.format_messages(**inputs)

print(f"  invoke()          → {type(prompt_value).__module__}.{type(prompt_value).__name__}"
      f"，含 {len(prompt_value.messages)} 条消息")
print(f"  format()          → {type(as_text).__name__}（纯字符串）")
print(f"  format_messages() → {type(as_messages).__name__}，含 {len(as_messages)} 条消息")
print()
print("  format() 的结果（角色名被拼成了 'System:' / 'Human:' / 'AI:' 三行）：")
for line in as_text.splitlines():
    print(f"    {line}")
print()
print("  → 三者同源：都先把变量填进模板，再决定输出成什么形态。")
print("    invoke() 给的是 ChatPromptValue，可以直接喂给模型；")
print("    format_messages() 给的是 list[BaseMessage]，适合再拼别的东西；")
print("    format() 给的是字符串，只适合打印、日志、或喂给「只吃字符串」的旧接口。")

# ---------------------------------------------------------------------------
# 6. ChatPromptTemplate 初始化的六种参数类型
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("⑥ ChatPromptTemplate 初始化的六种参数类型")
print("=" * 72)

cases = [
    ("类型1 str", ["Hello, {name}!"], "默认角色是 human，写死不了 system"),
    (
        "类型2 tuple",
        [("system", "你的名字是{role}。"), ("human", "很高兴认识你")],
        "最常用的写法：角色字符串 + 模板字符串",
    ),
    (
        "类型3 dict",
        [
            {"role": "system", "content": "你的名字是{role}。"},
            {"role": "human", "content": "很高兴认识你"},
        ],
        "键必须恰好是 role 和 content 两个",
    ),
    (
        "类型4 BaseMessage",
        [SystemMessage("我是一个贴心的智能助手"), HumanMessage("人工智能英文怎么说？")],
        "已实例化的消息，内部花括号不会被当变量",
    ),
    (
        "类型5 MessagePromptTemplate",
        [
            SystemMessagePromptTemplate.from_template("你是一个{role}"),
            HumanMessagePromptTemplate.from_template("给我解释{concept}"),
        ],
        "先声明角色、再挂模板，可跨文件复用",
    ),
    (
        "类型6 嵌套 ChatPromptTemplate",
        [
            ChatPromptTemplate.from_messages([("system", "你是{name}")]),
            ChatPromptTemplate.from_messages([("human", "{q}")]),
        ],
        "模板拼模板，适合把提示词拆成多个文件维护",
    ),
]

all_inputs = {"name": "小谷AI", "role": "物理学家", "concept": "相对论", "q": "你好"}
for label, msgs, why in cases:
    built = ChatPromptTemplate.from_messages(msgs)
    rendered = built.invoke(all_inputs)
    kinds = [type(m).__name__ for m in rendered.messages]
    print(f"  {label} → {kinds}")
    print(f"    {why}")

print()
print("  → 为什么会有这么多种？因为它们各自解决一个来源问题：")
print("    str / tuple / dict 面向「手写提示词」，BaseMessage 面向「已有消息对象」，")
print("    MessagePromptTemplate 面向「跨文件复用的模板」，嵌套模板面向「提示词分段维护」。")
print("  → 类型4 的坑：BaseMessage 里的花括号不会被当变量（实测 {word} 原样保留）。")

print()
print("  ⚠️ 实测纠正：官方源码里 MessageLikeRepresentation 只认六类")
print("     （BaseMessagePromptTemplate | BaseMessage | BaseChatPromptTemplate | tuple | str | dict），")
print("     把「可调用对象」（函数）放进列表会直接报错：")
try:
    ChatPromptTemplate.from_messages([lambda inputs: SystemMessage(str(inputs))])
except NotImplementedError as exc:
    print(f"     NotImplementedError: {exc}")

# ---------------------------------------------------------------------------
# 7. MessagesPlaceholder 与 partial()
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("⑦ MessagesPlaceholder（消息占位符）与 partial()（部分变量预填充）")
print("=" * 72)

template = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个{role}，目标用户是{audience}。"),
        MessagesPlaceholder("history"),
        ("human", "{task}"),
    ]
)
rendered = template.invoke(
    {
        "role": "客服专员",
        "audience": "普通用户",
        "history": [("human", "我买的东西坏了"), ("ai", "很抱歉，我帮您处理。")],
        "task": "解释退款政策",
    }
)
print("  带历史的渲染结果：")
show(rendered.messages)
print("  → MessagesPlaceholder 解决的是「不知道历史里有几条、什么角色」的问题：")
print("    它把一整个消息列表原样插到指定位置，而不是把历史拼成一段文本。")
print("    多轮对话、Agent 中间步骤回灌都靠它。")

support_template = template.partial(role="客服专员", audience="普通用户")
rendered2 = support_template.invoke({"history": [], "task": "解释退款政策"})
print()
print(f"  partial() 之后，模板还需要的变量: {support_template.input_variables}")
print(f"  role / audience 已被钉死，渲染结果 → {[str(m.content) for m in rendered2.messages]}")
print("  → partial() 把「每次都一样」的变量提前钉死，留下真正会变的。")
print("    同一套模板派生出客服版 / 销售版，靠的就是它。")

# ---------------------------------------------------------------------------
# 8. 用假模型的 .seen 验证：模板渲染的就是模型收到的
# ---------------------------------------------------------------------------
print()
print("=" * 72)
print("⑧ 验证：模板渲染出的消息，就是模型实际收到的消息")
print("=" * 72)

model = ScriptedChatModel(script=[reply("1 + 1 = 2。")])
prompt_value = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个{role}，回答要简短。"),
        ("human", "{q}"),
    ]
).invoke({"role": "数学老师", "q": "1 + 1 = ?"})

model.invoke(prompt_value)
print("  直接 model.invoke(prompt_value)，模型侧收到：")
show(model.seen[-1])
print()
print("  → ChatPromptValue 可以直接当模型的输入，不需要再 .messages 拆一层。")
print("  → 这是本教程反复用的观测手段：从模型这一侧看，才知道它究竟收到了什么。")
