/**
 * 第 7 章示例（TypeScript 版，与 07_tools.py 对应）：
 * 工具、运行时上下文注入与错误处理。
 *
 * 演示四件事：
 *   1. tool() 的 schema 从哪来
 *   2. runtime 注入：工具里怎么读到 state / context / store
 *   3. 工具返回 Command —— 直接修改图状态
 *   4. 工具抛异常时，用 wrapToolCall 把它变成模型能读懂的 ToolMessage
 *
 * 运行：pnpm run 04_tools
 */

import { createAgent, createMiddleware, tool, ToolMessage, HumanMessage, InMemoryStore } from "langchain";
import { Command } from "@langchain/langgraph";
import { z } from "zod";
import { ScriptedChatModel, reply, show, toolCall } from "./_fakeModel";

// ---------------------------------------------------------------------------
console.log("=".repeat(72));
console.log("① 工具的 schema 从哪来");
console.log("=".repeat(72));

const searchOrders = tool(
  async (args: { query: string; limit?: number }) =>
    `找到 ${args.limit ?? 5} 条与「${args.query}」相关的订单`,
  {
    name: "search_orders",
    description: "按关键词搜索订单。",
    schema: z.object({
      query: z.string().describe("搜索关键词"),
      limit: z.number().optional().describe("最多返回多少条"),
    }),
  },
);

console.log(`  工具名: ${searchOrders.name}`);
console.log(`  工具描述: ${JSON.stringify(searchOrders.description)}`);
console.log("  → 模型看到的就只有 名称 / 描述 / 参数 schema 三样东西；");
console.log("    description 写得含糊，模型就会选错工具。");
console.log();
console.log("  ⚠️ 与 Python 的差异：Python 用 @tool 装饰器 + 类型注解 + docstring；");
console.log("     JS 用 tool(fn, { name, description, schema }) —— schema 是必填的。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("② runtime 注入：工具里读取 state / context / store");
console.log("=".repeat(72));

const inspectRuntime = tool(
  async (_args: unknown, runtime: any) => {
    const history = runtime.state.messages.length;
    const tenant = runtime.context.tenantId;
    await runtime.store.put(["audit"], "last_call", { tenant });
    const hit = await runtime.store.get(["audit"], "last_call");
    return `历史 ${history} 条 | tenant=${tenant} | store 回读=${JSON.stringify(hit?.value)}`;
  },
  {
    name: "inspect_runtime",
    description: "读取运行时上下文并回报（runtime 参数对模型隐藏）。",
    schema: z.object({}),
  },
);

const rtAgent = createAgent({
  model: new ScriptedChatModel({
    script: [toolCall("inspect_runtime", {}, "c1"), reply("已读取运行时上下文。")],
  }) as any,
  tools: [inspectRuntime],
  contextSchema: z.object({ tenantId: z.string() }),
  // ⚠️ 不传 store 的话，runtime.store 是 undefined——Python 侧同理
  store: new InMemoryStore(),
});
const rtOut: any = await rtAgent.invoke(
  { messages: [new HumanMessage("看看上下文")] },
  { context: { tenantId: "t-7" } },
);
for (const m of rtOut.messages) {
  if (m.constructor.name === "ToolMessage") console.log(`  工具返回值: ${m.content}`);
}
console.log("  → runtime 参数对模型不可见：模型只看到工具名和描述。");
console.log("  → 旧写法 InjectedState / InjectedStore 在 v1 已由 runtime 统一取代。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("③ 工具返回 Command：直接修改状态");
console.log("=".repeat(72));

const setUserName = tool(
  async (args: { newName: string }, runtime: any) =>
    new Command({
      update: {
        userName: args.newName,
        // ⚠️ 返回 Command 时**必须**自己补一条 ToolMessage，
        //    否则工具节点会因为找不到对应的 tool_call_id 而报错。
        messages: [
          new ToolMessage({
            content: `名字已更新为 ${args.newName}`,
            tool_call_id: runtime.toolCallId,
          }),
        ],
      },
    }),
  {
    name: "set_user_name",
    description: "把用户名字写进会话状态。",
    schema: z.object({ newName: z.string() }),
  },
);

const cmdAgent = createAgent({
  model: new ScriptedChatModel({
    script: [toolCall("set_user_name", { newName: "小明" }, "c1"), reply("记住了。")],
  }) as any,
  tools: [setUserName],
  stateSchema: z.object({ userName: z.string().default("") }),
});
const cmdOut: any = await cmdAgent.invoke({
  messages: [new HumanMessage("我叫小明")],
});
console.log(`  最终 state.userName = ${JSON.stringify(cmdOut.userName)}`);
console.log("  → 工具不再只能返回字符串：返回 Command 就能顺手改状态，省掉一轮模型调用。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("④ 工具出错怎么办：wrapToolCall 把异常变成 ToolMessage");
console.log("=".repeat(72));

const divide = tool(
  async (args: { a: number; b: number }) => {
    if (args.b === 0) throw new Error("division by zero");
    return String(Math.trunc(args.a / args.b));
  },
  {
    name: "divide",
    description: "做整数除法。",
    schema: z.object({ a: z.number(), b: z.number() }),
  },
);

const handleToolErrors = createMiddleware({
  name: "HandleToolErrors",
  wrapToolCall: async (request: any, handler: any) => {
    try {
      return await handler(request);
    } catch (exc: any) {
      console.log(`  [中间件] 捕获到异常：${exc.constructor.name}，转成 ToolMessage`);
      return new ToolMessage({
        content: `工具执行失败：${exc.message}。请换一个参数再试。`,
        tool_call_id: request.toolCall.id,
      });
    }
  },
});

const errAgent = createAgent({
  model: new ScriptedChatModel({
    script: [
      toolCall("divide", { a: 1, b: 0 }, "c1"),
      reply("除数不能为 0，我换个数再算。"),
    ],
  }) as any,
  tools: [divide],
  middleware: [handleToolErrors] as any,
});
const errOut: any = await errAgent.invoke({ messages: [new HumanMessage("1 除以 0")] });
show(errOut.messages);
console.log();
console.log("  ⚠️ 注意：v1 已经**不再**使用 ToolException / handleToolError 这套旧 API。");
console.log("     要么像上面这样自己写 wrapToolCall，要么用内置的 toolErrorMiddleware。");
