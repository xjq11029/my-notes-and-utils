/**
 * 第 5 章示例（TypeScript 版，与 05_create_agent.py 对应）：
 * createAgent 与 Agent Loop。
 *
 * 演示四件事：
 *   1. 一次工具调用的完整往返
 *   2. messages 只追加
 *   3. thread_id（对话作用域）与 context（单次运行作用域）的区别
 *   4. 结构化输出 responseFormat
 *
 * 运行：pnpm run 02_create_agent
 */

import { createAgent, tool, HumanMessage } from "langchain";
import { MemorySaver } from "@langchain/langgraph";
import { z } from "zod";
import { ScriptedChatModel, reply, show, toolCall } from "./_fakeModel";

const getWeather = tool(async (args: { city: string }) => args.city + ": 22C sunny", {
  name: "get_weather",
  description: "查询某个城市的天气。",
  schema: z.object({ city: z.string().describe("城市名") }),
});

console.log("=".repeat(72));
console.log("① 一次工具调用的完整往返");
console.log("=".repeat(72));

const agent = createAgent({
  model: new ScriptedChatModel({
    script: [
      toolCall("get_weather", { city: "上海" }, "call_1"),
      reply("上海 22°C，晴。"),
    ],
  }) as any,
  tools: [getWeather],
});
const result: any = await agent.invoke({
  messages: [new HumanMessage("上海天气怎么样？")],
});
show(result.messages);
console.log("\n  模型从没执行过工具——它只输出「请调用 get_weather」；");
console.log("  真正执行并把结果写回上下文的是框架的 tools 节点。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("② messages 只追加（append-only）");
console.log("=".repeat(72));

const chat = createAgent({
  model: new ScriptedChatModel({
    script: [reply("你好，我是脚本模型。"), reply("你刚才说你叫小明。")],
  }) as any,
  tools: [],
  checkpointer: new MemorySaver(),
});
const cfg = { configurable: { thread_id: "chat-1" } };

const first: any = await chat.invoke(
  { messages: [new HumanMessage("你好，我叫小明。")] },
  cfg,
);
console.log(`  第 1 轮后，历史里有 ${first.messages.length} 条消息`);

const second: any = await chat.invoke({ messages: [new HumanMessage("我叫什么？")] }, cfg);
console.log(`  第 2 轮后，历史里有 ${second.messages.length} 条消息（不是 2 条）`);
show(second.messages);
console.log("\n  第二次 invoke 传进去的那条消息是被**追加**进去的，而不是替换掉旧历史——");
console.log("  这就是 messages 字段的 addMessages reducer 在起作用。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("③ thread_id（对话作用域）与 context（单次运行作用域）");
console.log("=".repeat(72));

const whoami = tool(async (_args: unknown, runtime: any) => "user_id=" + runtime.context.userId, {
  name: "whoami",
  description: "返回当前调用的用户 ID（参数对模型隐藏）。",
  schema: z.object({}),
});

const ctxAgent = createAgent({
  model: new ScriptedChatModel({
    script: [toolCall("whoami", {}, "c1"), reply("已确认身份。")],
  }) as any,
  tools: [whoami],
  contextSchema: z.object({ userId: z.string() }),
  checkpointer: new MemorySaver(),
});
const out: any = await ctxAgent.invoke(
  { messages: [new HumanMessage("我是谁？")] },
  { configurable: { thread_id: "ctx-1" }, context: { userId: "u-42" } },
);
for (const m of out.messages) {
  if (m.constructor.name === "ToolMessage") console.log(`  工具看到的 context：${m.content}`);
}
console.log("  → thread_id 决定「这段历史属于哪次对话」，会被写进检查点；");
console.log("  → context 是「这一次运行」的随身数据，不写进检查点，也不进消息历史。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("④ 结构化输出：responseFormat");
console.log("=".repeat(72));

/**
 * 本节**离线实测通过**（2026-10 探针补测）。
 *
 * 常见误读：「JS 结构化输出默认走 provider 原生 JSON schema」——那只说对了
 * provider 子类（如 ChatOpenAI 覆写了 withStructuredOutput）。源码
 * （langchain 1.5.11 的 agents/responses.js）里裸 schema 一律包成 ToolStrategy：
 * 策略工具名取 schema 的 title，没有 title 时退化为 extract-N。
 * 所以脚本化假模型能跑通——脚本按该工具名回一条 tool_call 即可。
 */
const Weather = z.object({
  city: z.string().describe("城市名"),
  tempC: z.number().describe("摄氏度温度"),
}).meta({ title: "Weather", description: "天气查询结果" });

// 策略工具名 = schema 的 title（这里即 "Weather"），与 Python 侧取类名对应
const structModel = new ScriptedChatModel({
  script: [toolCall("Weather", { city: "上海", tempC: 22 }, "s1")],
});
const structAgent = createAgent({
  model: structModel as any,
  tools: [],
  responseFormat: Weather,
});
const structOut: any = await structAgent.invoke({
  messages: [new HumanMessage("上海天气？")],
});
console.log(`  result.structuredResponse = ${JSON.stringify(structOut.structuredResponse)}`);
console.log("  → 与 Python 一样拿到按 schema 解析的对象，不用自己 JSON.parse。");
console.log("  → 参数不合法时框架走「校验失败写回 ToolMessage → 模型重试」（见 04 示例第 ⑥ 节）。");
console.log();
console.log("  ⚠️ 假模型回普通文本而不回工具调用时，structuredResponse 是 undefined——");
console.log("     策略没被命中，框架不报错；真实模型下由模型自己决定调不调这个工具。");
console.log("  ⚠️ 「JS 默认走 provider 原生 JSON schema」只对 provider 子类成立（未实测）；");
console.log("     裸 schema 与纯 BaseChatModel 子类的默认策略都是工具调用（源码可证）。");
