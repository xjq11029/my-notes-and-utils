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
 * ⚠️ 本小节**未离线实测**，只给写法。
 *
 * 原因：JS 侧的结构化输出默认走「provider 原生 JSON schema 输出」，
 * 需要真实模型声明支持；退到工具策略时，策略工具也不经 `bindTools` 暴露，
 * 脚本化假模型无法命中。所以这里不伪造结果。
 *
 * Python 侧同一件事是实测通过的（见 02_create_agent.py 第 ④ 节）。
 */
const Weather = z.object({
  city: z.string().describe("城市名"),
  tempC: z.number().describe("摄氏度温度"),
});

const structAgent = createAgent({
  model: "openai:gpt-4o" as any, // ← 换成你有 Key 的真实模型
  tools: [],
  responseFormat: Weather,
});

// 真实模型下这样取：
//   const s = await structAgent.invoke({ messages: [new HumanMessage("上海天气？")] });
//   console.log(s.structuredResponse);   // { city: '上海', tempC: 22 }
void structAgent;

console.log("  写法：createAgent({ model, tools: [], responseFormat: Weather })");
console.log("  取结果：result.structuredResponse  ← 已校验的对象，不是字符串");
console.log();
console.log("  ⚠️ 与 Python 的两处差异（实测）：");
console.log("     ① JS 默认走 provider 原生 JSON schema 输出，需要模型支持；");
console.log("        Python 侧默认走工具策略，脚本模型也能跑通。");
console.log("     ② JS 的策略工具名默认是 \"extract\"（源码：");
console.log("        name: structuredResponseFormat.strategy.schema?.name ?? \"extract\"）。");
console.log();
console.log("  ⚠️ 本小节未实测（需 API Key）——本机无 Key，不伪造输出。");
