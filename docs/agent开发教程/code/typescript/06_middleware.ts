/**
 * 第 6 章示例（TypeScript 版，与 06_middleware.py 对应）：
 * 中间件的钩子体系与治理件。
 *
 * 本示例做两件事：
 *   1. 把六个钩子在一次含工具调用的完整轮次里的真实触发顺序打出来；
 *   2. 演示四类治理件：HITL 审批、PII 脱敏、调用限额、重试与回退。
 *
 * 运行：pnpm run 06_middleware
 */

import {
  createAgent,
  createMiddleware,
  humanInTheLoopMiddleware,
  modelCallLimitMiddleware,
  modelFallbackMiddleware,
  modelRetryMiddleware,
  piiMiddleware,
  tool,
  toolCallLimitMiddleware,
  toolRetryMiddleware,
  HumanMessage,
} from "langchain";
import { Command, MemorySaver } from "@langchain/langgraph";
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

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("③ humanInTheLoopMiddleware：工具调用前停下来等人");
console.log("=".repeat(72));

const REFUNDS: string[] = [];
const refund = tool(
  async (args: { order_id: string }) => {
    REFUNDS.push(args.order_id);
    return `${args.order_id} 已退款`;
  },
  {
    name: "refund",
    description: "给订单退款。",
    schema: z.object({ order_id: z.string() }),
  },
);

const makeRefundAgent = () =>
  createAgent({
    model: new ScriptedChatModel({
      script: [toolCall("refund", { order_id: "A-1" }, "c1"), reply("已处理。")],
    }) as any,
    tools: [refund],
    middleware: [humanInTheLoopMiddleware({ interruptOn: { refund: true } })],
    checkpointer: new MemorySaver(),
  });

const approveAgent = makeRefundAgent();
const approveCfg = { configurable: { thread_id: "refund-approve" } };
const first: any = await approveAgent.invoke(
  { messages: [new HumanMessage("把 A-1 退款")] },
  approveCfg,
);
const request = first.__interrupt__[0].value;
console.log(`  待审批工具 = ${request.actionRequests[0].name}`);
console.log(`  允许决策   = ${JSON.stringify(request.reviewConfigs[0].allowedDecisions)}`);
console.log(`  审批前退款次数 = ${REFUNDS.length}`);
const second: any = await approveAgent.invoke(
  new Command({ resume: { decisions: [{ type: "approve" }] } }),
  approveCfg,
);
console.log(`  approve 后退款次数 = ${REFUNDS.length}，最终回复 = ${JSON.stringify(second.messages[second.messages.length - 1].content)}`);

const rejectAgent = makeRefundAgent();
const rejectCfg = { configurable: { thread_id: "refund-reject" } };
await rejectAgent.invoke({ messages: [new HumanMessage("把 A-1 退款")] }, rejectCfg);
const rejected: any = await rejectAgent.invoke(
  new Command({ resume: { decisions: [{ type: "reject" }] } }),
  rejectCfg,
);
console.log(`  reject 后退款次数 = ${REFUNDS.length}（未增加），最终回复 = ${JSON.stringify(rejected.messages[rejected.messages.length - 1].content)}`);
console.log("  → JS 的载荷字段是 camelCase（actionRequests / reviewConfigs），且只支持 approve/edit/reject；");
console.log("    Python 多一个 respond 决策。底层同样是 interrupt + checkpointer。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("④ piiMiddleware：模型侧只看到脱敏文本");
console.log("=".repeat(72));

const piiModel = new ScriptedChatModel({ script: [reply("收到。")] });
const piiAgent = createAgent({
  model: piiModel as any,
  tools: [],
  middleware: [
    piiMiddleware("email", { strategy: "redact" }),
    piiMiddleware("credit_card", { strategy: "mask" }),
  ],
});
await piiAgent.invoke({
  messages: [new HumanMessage("联系 alice@example.com，卡号 4111 1111 1111 1111")],
});
const piiSeen = piiModel.seen[piiModel.seen.length - 1] ?? [];
console.log(`  模型实际收到：${JSON.stringify(piiSeen.map((m) => String(m.content)))}`);
console.log("  → 选项名是 camelCase：applyToInput / applyToOutput / applyToToolResults；默认值与 Python 一致。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("⑤ 限额：模型调用与工具调用的上限");
console.log("=".repeat(72));

const limitModel = new ScriptedChatModel({
  script: [toolCall("get_weather", { city: "上海" }, "c1")],
});
const limitAgent = createAgent({
  model: limitModel as any,
  tools: [getWeather],
  middleware: [modelCallLimitMiddleware({ runLimit: 1, exitBehavior: "end" })],
});
const limitOut: any = await limitAgent.invoke({
  messages: [new HumanMessage("上海天气？")],
});
console.log(`  modelCallLimit(runLimit=1) → 最后一条：${JSON.stringify(limitOut.messages[limitOut.messages.length - 1].content)}`);

const toolLimitModel = new ScriptedChatModel({
  script: [
    toolCall("get_weather", { city: "上海" }, "c1"),
    toolCall("get_weather", { city: "北京" }, "c2"),
    reply("只查了一个。"),
  ],
});
const toolLimitAgent = createAgent({
  model: toolLimitModel as any,
  tools: [getWeather],
  middleware: [
    toolCallLimitMiddleware({ toolName: "get_weather", runLimit: 1, exitBehavior: "continue" }),
  ],
});
const toolLimitOut: any = await toolLimitAgent.invoke({
  messages: [new HumanMessage("两个城市天气")],
});
for (const msg of toolLimitOut.messages) {
  if (msg.constructor.name.includes("Tool")) {
    console.log(`  ToolMessage: ${JSON.stringify(String(msg.content).slice(0, 60))}`);
  }
}

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("⑥ 重试与回退：toolRetry / modelRetry / modelFallback");
console.log("=".repeat(72));

let flakyCalls = 0;
const flakyWeather = tool(
  async (args: { city: string }) => {
    flakyCalls += 1;
    if (flakyCalls < 3) throw new Error("上游超时");
    return `${args.city}: 22°C`;
  },
  {
    name: "flaky_weather",
    description: "一个前两次会失败、第三次成功的天气工具。",
    schema: z.object({ city: z.string() }),
  },
);
const retryAgent = createAgent({
  model: new ScriptedChatModel({
    script: [toolCall("flaky_weather", { city: "上海" }, "c1"), reply("查到了。")],
  }) as any,
  tools: [flakyWeather],
  middleware: [toolRetryMiddleware({ maxRetries: 2, initialDelayMs: 10, jitter: false })],
});
const retryOut: any = await retryAgent.invoke({
  messages: [new HumanMessage("上海天气？")],
});
console.log(`  toolRetry(maxRetries=2) → 工具实际调用 ${flakyCalls} 次，最后回复 = ${JSON.stringify(retryOut.messages[retryOut.messages.length - 1].content)}`);

class FlakyModel extends ScriptedChatModel {
  fails = 1;
  async _generate(messages: any): Promise<any> {
    if (this.fails > 0) {
      this.fails -= 1;
      throw new Error("模型偶发失败");
    }
    return super._generate(messages);
  }
}
const flakyModel = new FlakyModel({ script: [reply("重试成功")] });
const modelRetryAgent = createAgent({
  model: flakyModel as any,
  tools: [],
  middleware: [modelRetryMiddleware({ maxRetries: 2, initialDelayMs: 10, jitter: false })],
});
const modelRetryOut: any = await modelRetryAgent.invoke({
  messages: [new HumanMessage("你好")],
});
console.log(`  modelRetry → ${JSON.stringify(modelRetryOut.messages[modelRetryOut.messages.length - 1].content)}（fails 余量 ${flakyModel.fails}）`);

class AlwaysFailModel extends ScriptedChatModel {
  async _generate(): Promise<any> {
    throw new Error("主模型不可用");
  }
}
const fallbackModel = new ScriptedChatModel({ script: [reply("备用模型的回答")] });
const fallbackAgent = createAgent({
  model: new AlwaysFailModel({ script: [reply("never")] }) as any,
  tools: [],
  middleware: [modelFallbackMiddleware(fallbackModel as any)],
});
const fallbackOut: any = await fallbackAgent.invoke({
  messages: [new HumanMessage("你好")],
});
console.log(`  modelFallback → ${JSON.stringify(fallbackOut.messages[fallbackOut.messages.length - 1].content)}`);
console.log("  → 重试解决「偶发失败」，回退解决「主模型整体不可用」；两者可以叠加，但顺序决定语义。");
