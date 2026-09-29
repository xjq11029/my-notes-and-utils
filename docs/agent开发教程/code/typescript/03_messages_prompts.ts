/**
 * 第 3 章示例（TypeScript 版，与 03_messages_prompts.py 对应）：
 * Message 与提示词模板 —— 四种消息类型与模板渲染。
 *
 * 演示八件事：
 *   1. 四种消息类型（System / Human / AI / Tool）的字段与用途
 *   2. 两种构造方式：JSON dict 与消息对象，模型侧看到的是同一种东西
 *   3. content 与 contentBlocks：多模态内容块（构造可测，真实调用未实测）
 *   4. 多轮对话历史的管理与裁剪：只保留最近 N 轮
 *   5. ChatPromptTemplate 的三种调用方式：invoke / format / formatMessages
 *   6. ChatPromptTemplate 初始化的六种参数类型
 *   7. MessagesPlaceholder（消息占位符）与 partial()（部分变量预填充）
 *   8. 用假模型的 .seen 验证：模板渲染出的消息，就是模型实际收到的消息
 *
 * ⚠️ 与 Python 的差异：JS 侧 invoke / format / formatMessages / partial
 *    **全部是异步的**，少一个 await 就拿到 Promise 而不是结果。
 *
 * 运行：pnpm run 03_messages_prompts
 */

import { ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate } from "@langchain/core/prompts";
import { AIMessage, HumanMessage, SystemMessage, ToolMessage } from "@langchain/core/messages";
import { ScriptedChatModel, reply, show } from "./_fakeModel";

// ---------------------------------------------------------------------------
console.log("=".repeat(72));
console.log("① 四种消息类型：字段与用途");
console.log("=".repeat(72));

const systemMsg = new SystemMessage("你是一个严谨的技术助教。");
const humanMsg = new HumanMessage({ content: "上海天气怎么样？", name: "alice" });
const aiCall = new AIMessage({
  content: "",
  tool_calls: [{ name: "get_weather", args: { city: "上海" }, id: "call_1", type: "tool_call" }] as any,
});
const toolMsg = new ToolMessage({ content: "上海：22°C，晴", tool_call_id: "call_1", name: "get_weather" });
const aiFinal = new AIMessage("上海今天 22°C，晴。");

show([systemMsg, humanMsg, aiCall, toolMsg, aiFinal]);
console.log();
console.log("  → System 定规则、Human 是输入、AI 是输出、Tool 回灌工具结果——四者用途不同，");
console.log("    所以框架用四个类而不是一个带 role 字符串的通用对象来区分。");
console.log(`  → AIMessage.tool_calls 是「模型的意图」：${aiCall.tool_calls[0].name}(${JSON.stringify(aiCall.tool_calls[0].args)})`);
console.log(`  → ToolMessage.tool_call_id=${JSON.stringify(toolMsg.tool_call_id)} 必须与上一条 AI 消息的 id 对上，`);
console.log("    框架靠这个 id 把「工具结果」配回「是哪次调用」。");
console.log(`  → HumanMessage 的 name=${JSON.stringify(humanMsg.name)} 是元数据，用于多人对话里区分发言者；`);
console.log("    是否透传给模型由供应商决定（见「四、常见坑」第 5 条）。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("② 两种构造方式：JSON dict 与消息对象");
console.log("=".repeat(72));

// 写法一：JSON dict（适合从数据库、HTTP 请求体里直接拿到的数据）
const asDicts: any[] = [
  { role: "system", content: "你是一个严谨的技术助教。" },
  { role: "user", content: "上海天气怎么样？" },
  { role: "assistant", content: "", tool_calls: [{ name: "get_weather", args: { city: "上海" }, id: "call_1", type: "tool_call" }] },
  { role: "tool", content: "上海：22°C，晴", tool_call_id: "call_1" },
];

// 写法二：消息对象（本教程其余章节统一用这种）
const asObjects: any[] = [
  new SystemMessage("你是一个严谨的技术助教。"),
  new HumanMessage("上海天气怎么样？"),
  new AIMessage({ content: "", tool_calls: [{ name: "get_weather", args: { city: "上海" }, id: "call_1", type: "tool_call" }] as any }),
  new ToolMessage({ content: "上海：22°C，晴", tool_call_id: "call_1" }),
];

const model = new ScriptedChatModel({ script: [reply("上海 22°C，晴。")] });
await model.invoke(asDicts);
const dictSeen = model.seen[model.seen.length - 1].map((m: any) => m.constructor.name);
await model.invoke(asObjects);
const objectSeen = model.seen[model.seen.length - 1].map((m: any) => m.constructor.name);

console.log(`  传 dict     → 模型侧收到: ${JSON.stringify(dictSeen)}`);
console.log(`  传消息对象  → 模型侧收到: ${JSON.stringify(objectSeen)}`);
console.log(`  两者是否一致: ${JSON.stringify(dictSeen) === JSON.stringify(objectSeen)}`);
console.log();
console.log("  → dict 在进入模型之前就被框架转成了消息对象，模型侧看到的完全一样。");
console.log("    所以「用哪种写法」只是你这一侧的偏好：写库/收报文用 dict 省事，");
console.log("    在代码里拼逻辑用消息对象更直观（有类型、能挂 tool_calls）。");
console.log("  → 但 dict 的键名是框架约定死的：assistant 的工具调用放 tool_calls，");
console.log("    tool 消息必须带 tool_call_id，写错就是校验报错，而不是静默忽略。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("③ content 与 contentBlocks：多模态内容块");
console.log("=".repeat(72));

const plain = new HumanMessage("你好");
console.log(`  纯文本 content       : ${JSON.stringify(plain.content)}`);
console.log(`  纯文本 contentBlocks : ${JSON.stringify(plain.contentBlocks)}`);

const multimodal = new HumanMessage({
  content: [
    { type: "text", text: "这张图里有什么？" },
    { type: "image", base64: "iVBORw0KGgoAAAANSUhEUg...(略)", mime_type: "image/png" },
  ] as any,
});
console.log(`  多模态 content       : ${JSON.stringify(multimodal.content)}`);
console.log(`  多模态 contentBlocks : ${JSON.stringify(multimodal.contentBlocks)}`);

const aiBlock = new AIMessage({ content: [{ type: "text", text: "图里是一瓶香水。" }] as any });
console.log(`  从 content 反读 blocks: ${JSON.stringify(aiBlock.contentBlocks)}`);

console.log();
console.log("  → content 是弱类型：纯文本时是 string，多模态时是数组；");
console.log("    contentBlocks 是统一后的内容块列表，每个块都有 type 字段");
console.log("    （text / image / audio / video / tool_call / reasoning）。");
console.log("  → 写多模态用内容块数组，读「思维链」「引用」也优先读 contentBlocks。");
console.log("  ⚠️ 以上只验证了「构造与解析」。真实多模态调用（把图片发给模型）需要 API Key，未实测。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("④ 多轮对话历史的管理与裁剪：只保留最近 N 轮");
console.log("=".repeat(72));

/**
 * 保留全部 system 消息 + 最近 maxPairs 轮对话（每轮 = 一问一答）。
 *
 * 为什么单独挑出 system 消息：它是「角色设定」，丢掉之后模型的语气、
 * 约束会整体漂移；而更早的问答只是上下文，丢掉代价小得多。
 */
function keepRecentMessages(messages: any[], maxPairs = 2): any[] {
  const systemMsgs = messages.filter((m) => m instanceof SystemMessage);
  const dialogue = messages.filter((m) => !(m instanceof SystemMessage));
  return [...systemMsgs, ...dialogue.slice(-(maxPairs * 2))];
}

const history: any[] = [new SystemMessage("你是 Python 导师。")];
for (const [q, a] of [
  ["什么是列表？用一句解释", "列表是可变的有序序列。"],
  ["列表和元组有什么区别？用一句解释", "列表可变，元组不可变。"],
  ["什么是字典？用一句解释", "字典是键值对集合。"],
] as Array<[string, string]>) {
  history.push(new HumanMessage(q), new AIMessage(a));
}

console.log(`  原始历史: ${history.length} 条`);
const trimmed = keepRecentMessages(history, 2);
console.log(`  裁剪之后: ${trimmed.length} 条（system + 最近 2 轮）`);
show(trimmed);

// 关键验证：模型没有记忆，「裁剪」发生在你这一侧
const model2 = new ScriptedChatModel({ script: [reply("你第二个问题问的是列表和元组的区别。")] });
await model2.invoke([...trimmed, new HumanMessage("我第二个问题问的是什么？")]);
console.log(`  → 模型实际收到 ${model2.seen[model2.seen.length - 1].length} 条消息（裁剪后的 5 条 + 新问题 1 条）`);
console.log("  → 模型没有记忆：你给多少，它就看多少。裁剪是客户端的事，不是模型的事。");
console.log("  ⚠️ 按「条数」硬切有风险：如果被切掉的正好是 AI(tool_calls) 而留下它的");
console.log("     ToolMessage，就会出现「找不到对应调用的工具结果」，模型会报错或胡猜。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("⑤ ChatPromptTemplate 的三种调用方式");
console.log("=".repeat(72));

const template = ChatPromptTemplate.fromMessages([
  ["system", "你是一个 AI 开发工程师。你的名字是 {name}。"],
  ["human", "你能开发哪些 AI 应用?"],
  ["ai", "我能开发很多 AI 应用。"],
  ["human", "{user_input}"],
]);
const inputs = { name: "小谷AI", user_input: "你能帮我做什么?" };

const promptValue: any = await template.invoke(inputs);
const asText = await template.format(inputs);
const asMessages = await template.formatMessages(inputs);

console.log(`  invoke()          → ${promptValue.constructor.name}，含 ${promptValue.messages.length} 条消息`);
console.log(`  format()          → ${typeof asText}（纯字符串）`);
console.log(`  formatMessages()  → ${Array.isArray(asMessages) ? "Array" : typeof asMessages}，含 ${asMessages.length} 条消息`);
console.log();
console.log("  format() 的结果（角色名被拼成了 'System:' / 'Human:' / 'AI:' 三行）：");
for (const line of String(asText).split("\n")) console.log(`    ${line}`);
console.log();
console.log("  → 三者同源：都先把变量填进模板，再决定输出成什么形态。");
console.log("    invoke() 给的是 ChatPromptValue，可以直接喂给模型；");
console.log("    formatMessages() 给的是消息数组，适合再拼别的东西；");
console.log("    format() 给的是字符串，只适合打印、日志、或喂给「只吃字符串」的旧接口。");
console.log("  ⚠️ 与 Python 的差异：JS 侧这三个都是异步的，必须 await；");
console.log("     Python 侧 format() 是同步返回 str，不用 await。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("⑥ ChatPromptTemplate 初始化的六种参数类型");
console.log("=".repeat(72));

const cases: Array<[string, any[], string]> = [
  ["类型1 str", ["Hello, {name}!"], "默认角色是 human，写死不了 system"],
  [
    "类型2 tuple",
    [["system", "你的名字是{role}。"], ["human", "很高兴认识你"]],
    "最常用的写法：角色字符串 + 模板字符串",
  ],
  [
    "类型3 dict",
    [
      { role: "system", content: "你的名字是{role}。" },
      { role: "human", content: "很高兴认识你" },
    ],
    "键必须恰好是 role 和 content 两个",
  ],
  [
    "类型4 BaseMessage",
    [new SystemMessage("我是一个贴心的智能助手"), new HumanMessage("人工智能英文怎么说？")],
    "已实例化的消息，内部花括号不会被当变量",
  ],
  [
    "类型5 MessagePromptTemplate",
    [
      SystemMessagePromptTemplate.fromTemplate("你是一个{role}"),
      HumanMessagePromptTemplate.fromTemplate("给我解释{concept}"),
    ],
    "先声明角色、再挂模板，可跨文件复用",
  ],
  [
    "类型6 嵌套 ChatPromptTemplate",
    [
      ChatPromptTemplate.fromMessages([["system", "你是{name}"]]),
      ChatPromptTemplate.fromMessages([["human", "{q}"]]),
    ],
    "模板拼模板，适合把提示词拆成多个文件维护",
  ],
];

const allInputs = { name: "小谷AI", role: "物理学家", concept: "相对论", q: "你好" };
for (const [label, msgs, why] of cases) {
  const built = ChatPromptTemplate.fromMessages(msgs as any);
  const rendered: any = await built.invoke(allInputs);
  const kinds = rendered.messages.map((m: any) => m.constructor.name);
  console.log(`  ${label} → ${JSON.stringify(kinds)}`);
  console.log(`    ${why}`);
}

console.log();
console.log("  → 为什么会有这么多种？因为它们各自解决一个来源问题：");
console.log("    str / tuple / dict 面向「手写提示词」，BaseMessage 面向「已有消息对象」，");
console.log("    MessagePromptTemplate 面向「跨文件复用的模板」，嵌套模板面向「提示词分段维护」。");
console.log("  → 类型4 的坑：BaseMessage 里的花括号不会被当变量（实测 {word} 原样保留）。");

console.log();
console.log("  ⚠️ 实测纠正：两语言的模板元素都只认这六类");
console.log("     （BaseMessagePromptTemplate | BaseMessage | BaseChatPromptTemplate | tuple | str | dict），");
console.log("     把「可调用对象」（函数）放进数组会直接报错：");
try {
  ChatPromptTemplate.fromMessages([((i: any) => new SystemMessage(String(i))) as any]);
} catch (exc: any) {
  console.log(`     ${exc.constructor.name}: ${String(exc.message).split("\n")[0]}`);
}

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("⑦ MessagesPlaceholder（消息占位符）与 partial()（部分变量预填充）");
console.log("=".repeat(72));

const template2 = ChatPromptTemplate.fromMessages([
  ["system", "你是一个{role}，目标用户是{audience}。"],
  new MessagesPlaceholder("history"),
  ["human", "{task}"],
]);
const rendered2: any = await template2.invoke({
  role: "客服专员",
  audience: "普通用户",
  history: [new HumanMessage("我买的东西坏了"), new AIMessage("很抱歉，我帮您处理。")],
  task: "解释退款政策",
});
console.log("  带历史的渲染结果：");
show(rendered2.messages);
console.log("  → MessagesPlaceholder 解决的是「不知道历史里有几条、什么角色」的问题：");
console.log("    它把一整个消息列表原样插到指定位置，而不是把历史拼成一段文本。");
console.log("    多轮对话、Agent 中间步骤回灌都靠它。");

const supportTemplate: any = await template2.partial({ role: "客服专员", audience: "普通用户" });
const rendered3: any = await supportTemplate.invoke({ history: [], task: "解释退款政策" });
console.log();
console.log(`  partial() 之后，模板还需要的变量: ${JSON.stringify(supportTemplate.inputVariables)}`);
console.log(`  role / audience 已被钉死，渲染结果 → ${JSON.stringify(rendered3.messages.map((m: any) => String(m.content)))}`);
console.log("  → partial() 把「每次都一样」的变量提前钉死，留下真正会变的。");
console.log("    同一套模板派生出客服版 / 销售版，靠的就是它。");
console.log("  ⚠️ 与 Python 的差异：JS 侧 partial() 也是异步的，必须 await。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("⑧ 验证：模板渲染出的消息，就是模型实际收到的消息");
console.log("=".repeat(72));

const model3 = new ScriptedChatModel({ script: [reply("1 + 1 = 2。")] });
const finalPrompt: any = await ChatPromptTemplate.fromMessages([
  ["system", "你是一个{role}，回答要简短。"],
  ["human", "{q}"],
]).invoke({ role: "数学老师", q: "1 + 1 = ?" });

await model3.invoke(finalPrompt);
console.log("  直接 model.invoke(promptValue)，模型侧收到：");
show(model3.seen[model3.seen.length - 1]);
console.log();
console.log("  → ChatPromptValue 可以直接当模型的输入，不需要再 .messages 拆一层。");
console.log("  → 这是本教程反复用的观测手段：从模型这一侧看，才知道它究竟收到了什么。");
