/**
 * 第 12 章示例（TypeScript 版，与 12_hitl_stream.py 对应）：
 * 人在回路与流式输出。
 *
 * 演示四件事：
 *   1. interrupt() / new Command({ resume }) 的完整往返
 *   2. **恢复时整个节点从头重跑** —— 这是理解一切人在回路坑的钥匙
 *   3. streamMode 各档投影分别给你什么
 *   4. agent 作为子图时，不加 subgraphs 就拿不到内部消息
 *
 * 运行：pnpm run 08_hitl_stream
 */

import { createAgent, tool, HumanMessage } from "langchain";
import {
  Annotation,
  Command,
  END,
  MemorySaver,
  START,
  StateGraph,
  interrupt,
  getWriter,
} from "@langchain/langgraph";
import { z } from "zod";
import { ScriptedChatModel, reply, toolCall } from "./_fakeModel";

// ---------------------------------------------------------------------------
console.log("=".repeat(78));
console.log("① interrupt / resume 的完整往返");
console.log("=".repeat(78));

const SIDE_EFFECTS: string[] = [];

const Order = Annotation.Root({
  amount: Annotation<number>({ default: () => 0 }),
  status: Annotation<string>({ default: () => "" }),
});

const approval = (state: any): Command => {
  // ⚠️ 注意这一行：恢复时它会被**再执行一次**
  SIDE_EFFECTS.push(`节点开始，读到 amount=${state.amount}`);
  const decision = interrupt({
    question: `确认扣款 ${state.amount} 元？`,
    amount: state.amount,
  });
  return decision
    ? new Command({ goto: "charge" })
    : new Command({ goto: "cancelled" });
};

const hitl = new StateGraph(Order)
  // ⚠️ JS 侧要求：节点返回 Command 时，必须在第三个参数里声明可能的去向（ends），
  //    否则编译期报 UnreachableNodeError。Python 侧靠类型注解 Command[Literal[...]] 表达。
  .addNode("approval", approval, { ends: ["charge", "cancelled"] })
  .addNode("charge", () => ({ status: "已扣款" }))
  .addNode("cancelled", () => ({ status: "已取消" }))
  .addEdge(START, "approval")
  .addEdge("charge", END)
  .addEdge("cancelled", END)
  .compile({ checkpointer: new MemorySaver() });
const cfg = { configurable: { thread_id: "order-1" } };

console.log("  第一次 invoke（会停在 interrupt）：");
const r1: any = await hitl.invoke({ amount: 199, status: "待审批" }, cfg);
console.log(`    __interrupt__ = ${JSON.stringify(r1.__interrupt__?.[0]?.value ?? r1.__interrupt__)}`);
const mid: any = await hitl.getState(cfg);
console.log(`    此时状态：${JSON.stringify(mid.values)}`);
console.log(`    待执行节点 next = ${JSON.stringify(mid.next)}`);

console.log();
console.log("  第二次 invoke（用 Command resume 恢复）：");
const r2: any = await hitl.invoke(new Command({ resume: true }), cfg);
console.log(`    最终状态：${JSON.stringify(r2)}`);

console.log();
console.log("  副作用日志（看清「节点从头重跑」这件事）：");
SIDE_EFFECTS.forEach((line, i) => console.log(`    ${i + 1}. ${line}`));
console.log();
console.log("  ⚠️ 看到没——「节点开始，读到 amount=199」出现了**两次**：");
console.log("     恢复不是从中断那一行继续，而是把整个节点**从头再执行一遍**。");
console.log("     所以 interrupt() 之前的代码必须是幂等的；");
console.log("     真正的副作用（扣款）要放到 interrupt() **之后**的节点里。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("② streamMode：同一张图，多种投影");
console.log("=".repeat(78));

const Talk = Annotation.Root({
  n: Annotation<number>({ default: () => 0 }),
  note: Annotation<string>({ default: () => "" }),
});

const talk = new StateGraph(Talk)
  .addNode("step", (state: any) => {
    getWriter()(`进度：正在处理第 ${state.n + 1} 步`); // 自定义事件
    return { n: state.n + 1, note: `第 ${state.n + 1} 步完成` };
  })
  .addEdge(START, "step")
  .addEdge("step", END)
  .compile({ checkpointer: new MemorySaver() });
const sCfg = { configurable: { thread_id: "stream-1" } };

for (const mode of ["values", "updates", "custom"] as const) {
  const chunks: any[] = [];
  for await (const c of await talk.stream({ n: 0, note: "" }, { ...sCfg, streamMode: mode })) {
    chunks.push(c);
  }
  console.log(`  streamMode=${JSON.stringify(mode).padEnd(11)} → ${JSON.stringify(chunks)}`);
}

console.log();
console.log("  各档给你的东西：");
console.log("    values  每步之后的**完整状态**（体积最大，但最省心）");
console.log("    updates 每步节点返回的**增量**（带节点名，适合做进度条）");
console.log("    custom  节点里用 getWriter() 主动推的事件（适合推「第 3/10 步」）");
console.log("    debug   checkpoints + tasks 的合并，信息最多");
console.log("  另有：messages（LLM 逐 token，最常用于打字机效果）、checkpoints / tasks");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("③ 坑：agent 放进父图当子图后，内部消息默认不透传");
console.log("=".repeat(78));

const lookup = tool(async (args: { q: string }) => `${args.q} 的结果`, {
  name: "lookup",
  description: "查一下。",
  schema: z.object({ q: z.string() }),
});

const subAgent = createAgent({
  model: new ScriptedChatModel({
    script: [toolCall("lookup", { q: "x" }, "c1"), reply("查完了。")],
  }) as any,
  tools: [lookup],
});

const Parent = Annotation.Root({
  messages: Annotation<any[]>({ reducer: (a, b) => a.concat(b), default: () => [] }),
});
const parent = new StateGraph(Parent)
  // ⚠️ JS 侧：createAgent 返回的是 ReactAgent 包装对象，不是 Runnable；
  //    要当节点用，得取它的 `.graph`（已编译的图）。
  //    Python 侧可以直接 add_node("agent", sub_agent)，因为它本身就是 CompiledStateGraph。
  .addNode("agent", (subAgent as any).graph)
  .addEdge(START, "agent")
  .addEdge("agent", END)
  .compile();

async function collect(stream: AsyncIterable<any>, tagged: boolean): Promise<string[]> {
  const lines: string[] = [];
  for await (const chunk of stream) {
    const [msg, meta] = tagged ? chunk[1] : chunk;
    const ns = tagged ? `ns=${String(chunk[0]?.[0] ?? "()").split(":")[0]}` : "ns=()";
    lines.push(
      `${ns} node=${meta?.langgraph_node} [${msg.constructor.name}] ${JSON.stringify(String(msg.content).slice(0, 20))}`,
    );
  }
  return lines;
}

const direct = await collect(
  await subAgent.stream({ messages: [new HumanMessage("查 x")] }, { streamMode: "messages" }),
  false,
);
const wrapped = await collect(
  await parent.stream({ messages: [new HumanMessage("查 x")] }, { streamMode: "messages" }),
  false,
);
const tagged = await collect(
  await parent.stream(
    { messages: [new HumanMessage("查 x")] },
    { streamMode: "messages", subgraphs: true },
  ),
  true,
);

console.log(`  A. 直接 stream 子 agent —— ${direct.length} 个分块，内部消息一览无余：`);
direct.forEach((l) => console.log(`       ${l}`));
console.log();
console.log(`  B. 父图 stream，**不加** subgraphs —— ${wrapped.length} 个分块：`);
wrapped.forEach((l) => console.log(`       ${l}`));
console.log("       ↑ 只剩跨边界的少数几条，模型内部的 token 全没了");
console.log("         （具体条数取决于版本与实现，Python 侧实测是 2 条、JS 侧是 1 条——");
console.log("          重点是「子图内部的消息被吞掉了」这件事，不是数字）");
console.log();
console.log(`  C. 父图 stream，**加** subgraphs —— ${tagged.length} 个分块：`);
tagged.forEach((l) => console.log(`       ${l}`));
console.log("       ↑ 分块带上了 namespace，能区分「这是哪个子图吐出来的」");
console.log();
console.log("  ⚠️ 因为 createAgent 返回的是**已编译的图**，把它当节点加进父图，它就变成了子图。");
console.log("     子图的内部输出默认不透传——这就是「图能跑、结果也对，");
console.log("     但打字机效果莫名其妙没了」的原因。要透传就显式加 subgraphs: true。");
