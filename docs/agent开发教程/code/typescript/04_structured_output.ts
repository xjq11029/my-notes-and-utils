/**
 * 第 4 章示例（TypeScript 版，与 04_structured_output.py 对应）：
 * 结构化输出 —— schema 形态与两种策略。
 *
 * 演示六件事：
 *   1. 手动「要求 JSON + 解析 + 校验」的脆弱链路 vs withStructuredOutput 一步到位
 *   2. schema 形态：zod / JSON Schema dict（以及 TS 没有的 TypedDict、@dataclass）
 *   3. 两种策略：默认（function calling）与 method 参数
 *   4. 类型校验：JS 基类**不校验**——与 Python 最大的差异
 *   5. includeRaw：返回 { raw, parsed }，没有 parsing_error
 *   6. 与 agent 侧 responseFormat 的关系（第 5 章的主题）
 *
 * 运行：pnpm run 04_structured_output
 */

import { z } from "zod";
import { createAgent, HumanMessage, providerStrategy, toolStrategy } from "langchain";
import { AIMessageChunk } from "@langchain/core/messages";
import type { BaseMessage } from "@langchain/core/messages";
import type { ChatResult } from "@langchain/core/outputs";
import { ScriptedChatModel, reply, show, toolCall } from "./_fakeModel";

/**
 * 本地派生一个假模型，只改一处：把脚本里的 AIMessage 包成 AIMessageChunk。
 *
 * 为什么必须这么做：`withStructuredOutput` 的解析器第一步就是
 * `if (!AIMessageChunk.isInstance(input)) throw new Error("Input is not an AIMessageChunk.")`，
 * 而 `_fakeModel.ts` 返回的是 AIMessage（两者是父子类，不是同一个类）。
 * 不改公共假模型，就在这里派生——这也是「框架只认 chunk」这条实现细节的实证。
 */
class ChunkScriptedChatModel extends ScriptedChatModel {
  async _generate(messages: BaseMessage[]): Promise<ChatResult> {
    (this as any).seen.push([...messages]);
    const idx = Math.min((this as any).cursor, this.script.length - 1);
    (this as any).cursor += 1;
    const msg = this.script[idx];
    const calls: any[] = (msg as any).tool_calls ?? [];
    const chunk = new AIMessageChunk({
      content: msg.content,
      tool_calls: calls,
      tool_call_chunks: calls.map((c) => ({
        name: c.name,
        args: JSON.stringify(c.args),
        id: c.id,
        index: 0,
        type: "tool_call_chunk",
      })),
    });
    return { generations: [{ text: String(chunk.content), message: chunk }] };
  }

  /** 记下被绑定的工具名；JS 侧绑定的是 { type, function: { name } } 形态的字典。 */
  bindTools(tools: Array<any> = []): this {
    this.boundToolNames.push(
      tools.map((t) => t?.function?.name ?? t?.name).filter((n): n is string => Boolean(n)),
    );
    return this;
  }
}

const Person = z
  .object({
    name: z.string().describe("姓名"),
    age: z.number().describe("年龄"),
    occupation: z.string().describe("职业"),
  })
  .meta({ title: "Person", description: "人物信息" });

const ARGS = { name: "张三", age: 30, occupation: "软件工程师" };
const TEXT = "张三是一名 30 岁的软件工程师";

// ---------------------------------------------------------------------------
console.log("=".repeat(72));
console.log("① 手动链路 vs withStructuredOutput");
console.log("=".repeat(72));

// 传统做法：提示词里求模型吐 JSON，然后自己解析、自己校验、自己建对象
const raw = '{"name": "张三", "age": "三十", "occupation": "软件工程师"}';
const data = JSON.parse(raw);
console.log(`  JSON.parse 成功，拿到对象：${JSON.stringify(data)}`);
console.log(`  手动校验 typeof data.age === "number" → ${typeof data.age === "number"}`);
console.log("  → 少写一个 if，这个「三十」就会一路流到下游数据库里。");

// 结构化输出：schema 声明一次，绑定、约束、解析都由框架完成
const m1 = new ChunkScriptedChatModel({ script: [toolCall("extract", ARGS, "c1")] }) as any;
const person = await m1.withStructuredOutput(Person).invoke(TEXT);
console.log(`  withStructuredOutput(Person) → ${JSON.stringify(person)}`);
console.log(`  直接点属性：person.name=${JSON.stringify(person.name)} person.age=${person.age}`);
console.log("  → zod 的 .describe() 会被转成 JSON Schema 交给模型，字段约束与解析一次配好。");
console.log(`  默认策略把 schema 绑成的工具名 = ${JSON.stringify(m1.boundToolNames)}`);

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("② schema 形态：zod 与 JSON Schema dict");
console.log("=".repeat(72));

const jsonSchema = {
  title: "PersonJson",
  description: "人物信息（JSON Schema）",
  type: "object",
  properties: {
    name: { type: "string", description: "姓名" },
    age: { type: "integer", description: "年龄" },
    occupation: { type: "string", description: "职业" },
  },
  required: ["name", "age", "occupation"],
} as const;

for (const [label, schema] of [
  ["zod", Person],
  ["JSON Schema", jsonSchema],
] as Array<[string, any]>) {
  const m = new ChunkScriptedChatModel({ script: [toolCall("extract", ARGS, "c1")] }) as any;
  const out = await m.withStructuredOutput(schema).invoke(TEXT);
  console.log(`  ${label.padEnd(12)} → ${JSON.stringify(out)}   绑定工具名=${JSON.stringify(m.boundToolNames)}`);
}
console.log("  → 两种形态在基类实现里都落到「工具名 extract」这一个工具上，只能用 name 选项改名。");
console.log("     与 Python 不同：Python 那边工具名取类名（Person / PersonDict / PersonDC / title）。");

console.log();
console.log("  ⚠️ JS 只有两种可运行时使用的形态。Python 的 TypedDict 与 @dataclass 在 JS 侧**没有等价物**：");
console.log("     TS 的 interface / type 编译后就被擦除，运行时拿不到字段信息，传进去只会报错。");
try {
  const m = new ChunkScriptedChatModel({ script: [toolCall("extract", ARGS, "c1")] }) as any;
  await m.withStructuredOutput(undefined as any).invoke(TEXT);
} catch (e: any) {
  console.log(`     实测：withStructuredOutput(undefined) → ${e.constructor.name}: ${String(e.message).slice(0, 60)}`);
}

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("③ 两种策略：method 参数");
console.log("=".repeat(72));

for (const [label, config] of [
  ["不传 config（默认）", undefined],
  ["method=functionCalling", { method: "functionCalling" }],
  ["method=jsonSchema", { method: "jsonSchema" }],
  ["method=jsonMode", { method: "jsonMode" }],
  ["name=Person", { name: "Person" }],
] as Array<[string, any]>) {
  const m = new ChunkScriptedChatModel({ script: [toolCall(label === "name=Person" ? "Person" : "extract", ARGS, "c1")] }) as any;
  try {
    const out = await m.withStructuredOutput(Person, config).invoke(TEXT);
    console.log(`  ${label} → ${JSON.stringify(out)}`);
  } catch (e: any) {
    console.log(`  ${label} → ${e.constructor.name}: ${String(e.message).slice(0, 80)}`);
  }
}
console.log("  → 实测（@langchain/core 1.2.12）：基类只认 function calling——`jsonMode` 直接抛错，");
console.log("     其余 method 值被忽略；默认工具名是 `extract`（可用 name 覆盖）。");
console.log("     「JS 默认走 json_schema」说的是 **provider 子类**（如 ChatOpenAI）；");
console.log("     在纯 BaseChatModel 子类上，默认就是工具调用。**真实 provider 未实测。**");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("④ 类型校验：JS 基类不校验");
console.log("=".repeat(72));

const m2 = new ChunkScriptedChatModel({
  script: [toolCall("extract", { name: "张三", age: "三十", occupation: "工程师" }, "c1")],
}) as any;
console.log(`  age 传中文 → ${JSON.stringify(await m2.withStructuredOutput(Person).invoke(TEXT))}`);

const m3 = new ChunkScriptedChatModel({ script: [toolCall("extract", { name: "张三" }, "c1")] }) as any;
console.log(`  漏填 age/occupation → ${JSON.stringify(await m3.withStructuredOutput(Person).invoke(TEXT))}`);
console.log("  → 基类实现里解析器只做「找到这条 tool_call 就返回它的 args」，**没有一步校验**。");
console.log("     同一个 schema 在 Python 侧会抛 ValidationError——这是双语言最容易踩空的一处。");
console.log("     想要校验，走 agent 侧的工具策略（第 ⑥ 节），那条路径会用 zod 校验。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("⑤ includeRaw：拿到原始响应");
console.log("=".repeat(72));

const m4 = new ChunkScriptedChatModel({ script: [toolCall("extract", ARGS, "c1")] }) as any;
const withRaw: any = await m4.withStructuredOutput(Person, { includeRaw: true }).invoke(TEXT);
console.log(`  keys = ${JSON.stringify(Object.keys(withRaw))}`);
console.log(`  parsed = ${JSON.stringify(withRaw.parsed)}`);
console.log(`  raw 类型 = ${withRaw.raw.constructor.name}`);
console.log("  → JS 只有 { raw, parsed }；Python 多一个 parsing_error，且解析失败时 parsed 为 null。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("⑥ 与 agent 侧 responseFormat 的关系");
console.log("=".repeat(72));

// 工具策略：schema 变成一个真正的工具绑给模型；校验失败会写回 ToolMessage 让模型重试
const strategies: any = toolStrategy(Person);
const toolName: string = strategies[0].name;
console.log(`  toolStrategy(Person) 的策略工具名 = ${JSON.stringify(toolName)}`);

const m5 = new ChunkScriptedChatModel({
  script: [
    toolCall(toolName, { name: "张三", age: "三十", occupation: "工程师" }, "c1"),
    toolCall(toolName, ARGS, "c2"),
  ],
}) as any;
const agent = createAgent({ model: m5, tools: [], responseFormat: strategies });
const out: any = await agent.invoke({ messages: [new HumanMessage(TEXT)] });
console.log(`  state.structuredResponse = ${JSON.stringify(out.structuredResponse)}`);
show(out.messages);
console.log(`  模型被调用 ${m5.seen.length} 次：第一次参数非法，框架把错误写回 ToolMessage，模型自己改对了。`);

// provider 原生策略：模型直接吐 JSON 文本，客户端按 schema 解析
const m6 = new ChunkScriptedChatModel({ script: [reply(JSON.stringify(ARGS))] }) as any;
const agent2 = createAgent({ model: m6, tools: [], responseFormat: providerStrategy(Person) });
const out2: any = await agent2.invoke({ messages: [new HumanMessage(TEXT)] });
console.log(`  providerStrategy(Person) → ${JSON.stringify(out2.structuredResponse)}`);
console.log("  → 分工：模型侧由 withStructuredOutput 决定怎么绑，agent 侧由 responseFormat 决定用哪种策略，");
console.log("     且工具策略多一步「校验失败自动重试」。这是第 5 章的主题。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("附：枚举与可选字段 —— 约束字段的取值范围");
console.log("=".repeat(72));

const Ticket = z
  .object({
    title: z.string().describe("工单标题"),
    urgency: z.enum(["低", "中", "高"]).describe("紧急程度"),
    assignee: z.string().optional().describe("处理人，未知就留空"),
  })
  .meta({ title: "Ticket", description: "工单信息" });

const m7 = new ChunkScriptedChatModel({
  script: [toolCall("extract", { title: "订单未发货", urgency: "高" }, "c1")],
}) as any;
const ticket = await m7.withStructuredOutput(Ticket).invoke("订单一直没发货，很着急");
console.log(`  ${JSON.stringify(ticket)}`);
console.log(`  ticket.assignee = ${JSON.stringify(ticket.assignee)}（模型没给 → undefined）`);
console.log("  ⚠️ JS 侧 zod 的 .optional() 只是 schema 约束；基类不校验，所以字段缺了也不会报错。");
