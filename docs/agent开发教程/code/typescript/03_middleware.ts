/**
 * 第 3 章示例（TypeScript 版，与 03_middleware.py 对应）：
 * 中间件的钩子体系。
 *
 * 本示例做一件文档里没有、但写代码时最需要知道的事：
 * **把六个钩子在一次含工具调用的完整轮次里的真实触发顺序打出来。**
 *
 * 运行：pnpm run 03_middleware
 */

import { createAgent, createMiddleware, tool, HumanMessage } from "langchain";
import { z } from "zod";
import { ScriptedChatModel, reply, toolCall } from "./_fakeModel";

const TRACE: string[] = [];

const getWeather = tool(
  async (args: { city: string }) => {
    TRACE.push("        └─ 工具函数体真正执行");
    return args.city + ": 22°C，晴";
  },
  {
    name: "get_weather",
    description: "查询某个城市的天气。",
    schema: z.object({ city: z.string() }),
  },
);

const traceMiddleware = createMiddleware({
  name: "TraceMiddleware",
  beforeAgent: () => {
    TRACE.push("before_agent");
  },
  beforeModel: () => {
    TRACE.push("before_model");
  },
  afterModel: () => {
    TRACE.push("after_model");
  },
  afterAgent: () => {
    TRACE.push("after_agent");
  },
  wrapModelCall: async (request: any, handler: any) => {
    TRACE.push("wrap_model_call");
    return handler(request);
  },
  wrapToolCall: async (request: any, handler: any) => {
    TRACE.push("wrap_tool_call");
    return handler(request);
  },
});

console.log("=".repeat(72));
console.log("六个钩子的真实触发顺序");
console.log("=".repeat(72));

const agent = createAgent({
  model: new ScriptedChatModel({
    script: [
      toolCall("get_weather", { city: "上海" }, "c1"),
      reply("上海 22°C，晴。"),
    ],
  }) as any,
  tools: [getWeather],
  middleware: [traceMiddleware] as any,
});
await agent.invoke({ messages: [new HumanMessage("上海天气？")] });

TRACE.forEach((line, i) => console.log(`  ${String(i + 1).padStart(2)}. ${line}`));

console.log();
console.log("  读法：");
console.log("  · before_agent / after_agent 包住**整个** agent 调用，各只触发一次；");
console.log("  · before_model → wrap_model_call → after_model 是**每一次**模型调用都走一遍；");
console.log("  · 轮次里出现了两次 before_model，因为这一轮调了两次模型");
console.log("    （第一次决定调工具，第二次拿到工具结果后给最终答案）；");
console.log("  · wrap_tool_call 只在工具执行时出现一次，且夹在两次模型调用之间。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("wrap_* 钩子能改写请求：动态切换模型");
console.log("=".repeat(72));

const SWITCH_LOG: string[] = [];

const switchModel = createMiddleware({
  name: "SwitchModelMiddleware",
  wrapModelCall: async (request: any, handler: any) => {
    const n = request.state.messages.length;
    if (n > 2) {
      SWITCH_LOG.push(`消息数 ${n} > 2 → 换用强模型`);
      // ⚠️ 与 Python 的写法不同：JS 侧没有 request.override()，
      //    约定是「展开原请求、覆盖要改的字段」再交给 handler。
      return handler({ ...request, model: strong });
    }
    SWITCH_LOG.push(`消息数 ${n} ≤ 2 → 用便宜模型`);
    return handler(request);
  },
});

const cheap = new ScriptedChatModel({ script: [reply("便宜模型的回答")] });
const strong = new ScriptedChatModel({ script: [reply("强模型的回答")] });

const swAgent = createAgent({
  model: cheap as any,
  tools: [],
  middleware: [switchModel] as any,
});
const r1: any = await swAgent.invoke({ messages: [new HumanMessage("问题一")] });
console.log(`  第一次调用：${SWITCH_LOG[SWITCH_LOG.length - 1]}`);
console.log(`  最终回复：${JSON.stringify(r1.messages[r1.messages.length - 1].content)}`);

const r2: any = await swAgent.invoke({
  messages: [
    new HumanMessage("问题一"),
    reply("答案一"),
    new HumanMessage("问题二"),
  ],
});
console.log(`  第二次调用：${SWITCH_LOG[SWITCH_LOG.length - 1]}`);
console.log(`  最终回复：${JSON.stringify(r2.messages[r2.messages.length - 1].content)}`);
console.log("  → JS 侧改写请求的约定是 `handler({ ...request, model })`；");
console.log("    Python 侧则是 `handler(request.override(model=...))`。");
console.log("    两边都保留链上其它中间件的语义，不要直接改 request 对象本身。");
