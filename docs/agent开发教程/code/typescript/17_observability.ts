/**
 * 第 17 章示例（TypeScript 版，与 17_observability.py 对应）：
 * 可观测与评测。
 *
 * 本示例用**离线回调**搭出一棵 trace 树，把「一次 agent 调用产生了哪些 span」
 * 这件事讲清楚——因为 LangSmith 上报需要账号，本机无法实测。
 *
 * 演示三件事：
 *   1. 一次 agent 调用会产生哪些嵌套的 run（这就是 trace 的结构）
 *   2. 每个 run 上能拿到什么元数据（类型、耗时）
 *   3. 离线评测的最小骨架：跑用例 → 判定 → 汇总
 *
 * 运行：pnpm run 13_observability
 */

import { createAgent, tool, HumanMessage } from "langchain";
import { BaseCallbackHandler } from "@langchain/core/callbacks/base";
import { z } from "zod";
import { ScriptedChatModel, reply, toolCall } from "./_fakeModel";

interface RunInfo {
  name: string;
  type: string;
  parent?: string;
  children: string[];
  t0: number;
  t1?: number;
}

class TraceRecorder extends BaseCallbackHandler {
  name = "TraceRecorder";
  runs = new Map<string, RunInfo>();
  roots: string[] = [];

  private start(runId: string, parentId: string | undefined, name: string, type: string) {
    this.runs.set(runId, { name, type, parent: parentId, children: [], t0: performance.now() });
    if (!parentId) this.roots.push(runId);
    else this.runs.get(parentId)?.children.push(runId);
  }

  private end(runId: string) {
    const r = this.runs.get(runId);
    if (r) r.t1 = performance.now();
  }

  handleChainStart(_c: any, _i: any, runId: string, parentRunId?: string, _t?: any, _m?: any, _rt?: any, _n?: string) {
    this.start(runId, parentRunId, "chain", "chain");
  }
  handleChainEnd(_o: any, runId: string) {
    this.end(runId);
  }
  handleChatModelStart(_l: any, _m: any, runId: string, parentRunId?: string) {
    this.start(runId, parentRunId, "ChatModel", "llm");
  }
  handleLLMEnd(_o: any, runId: string) {
    this.end(runId);
  }
  handleToolStart(_t: any, _i: string, runId: string, parentRunId?: string, _tags?: any, _m?: any, _n?: string) {
    // ⚠️ 工具名在第 7 个参数（name）里，不在 serialized 里——JS 侧踩过一次
    this.start(runId, parentRunId, _n ?? "tool", "tool");
  }
  handleToolEnd(_o: any, runId: string) {
    this.end(runId);
  }

  tree(): string {
    const lines: string[] = [];
    const walk = (id: string, depth: number) => {
      const r = this.runs.get(id)!;
      const ms = r.t1 ? r.t1 - r.t0 : 0;
      lines.push(`${"  ".repeat(depth)}├─ [${r.type.padEnd(5)}] ${r.name}  (${ms.toFixed(1)} ms)`);
      r.children.forEach((c) => walk(c, depth + 1));
    };
    this.roots.forEach((r) => walk(r, 0));
    return lines.join("\n");
  }
}

const getPrice = tool(async (args: { sku: string }) => `${args.sku}: 199 元`, {
  name: "get_price",
  description: "查商品价格。",
  schema: z.object({ sku: z.string() }),
});

// ---------------------------------------------------------------------------
console.log("=".repeat(78));
console.log("① 一次 agent 调用产生的 trace 树");
console.log("=".repeat(78));

const recorder = new TraceRecorder();
const agent = createAgent({
  model: new ScriptedChatModel({
    script: [toolCall("get_price", { sku: "A-1" }, "c1"), reply("A-1 卖 199 元。")],
  }) as any,
  tools: [getPrice],
});
await agent.invoke(
  { messages: [new HumanMessage("A-1 多少钱？")] },
  { callbacks: [recorder], runName: "price_lookup" },
);

console.log(recorder.tree());
console.log();
console.log(`  共 ${recorder.runs.size} 个 run，根节点 ${recorder.roots.length} 个`);
console.log();
console.log("  结构读法：");
console.log("    chain  ── 整次 agent 调用（对应 LangSmith 里的一个 trace）");
console.log("      └ chain ── 图里的 model 节点");
console.log("          └ llm ── 真正那次模型请求");
console.log("      └ chain ── 图里的 tools 节点");
console.log("          └ tool ── 真正那次工具执行");
console.log();
console.log("  ⚠️ 每个 run 都有自己的输入 / 输出，所以「第几次模型调用说了什么」");
console.log("     是可以逐层下钻看到的——这就是能查清「agent 为什么走了这一步」的原因。");
console.log("     没有 trace 的话，你只能看到最终答案，中间过程是个黑盒。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("② 离线评测的最小骨架");
console.log("=".repeat(78));

const CASES = [
  { input: "A-1 多少钱？", expectTool: "get_price", expectInReply: "199" },
  { input: "B-2 多少钱？", expectTool: "get_price", expectInReply: "199" },
  { input: "你好", expectTool: null, expectInReply: "你好" },
];

function buildAgent(c: (typeof CASES)[number]) {
  const script = [];
  if (c.expectTool) script.push(toolCall(c.expectTool, { sku: "X" }, "c1"));
  script.push(reply(c.expectTool ? c.expectInReply : "你好，有什么可以帮你？"));
  return createAgent({ model: new ScriptedChatModel({ script }) as any, tools: [getPrice] });
}

let passed = 0;
console.log("  #   用例             调用的工具     判定");
console.log("  " + "-".repeat(52));
for (let i = 0; i < CASES.length; i += 1) {
  const c = CASES[i];
  const rec = new TraceRecorder();
  const a = buildAgent(c);
  const r: any = await a.invoke(
    { messages: [new HumanMessage(c.input)] },
    { callbacks: [rec], configurable: { thread_id: `eval-${i}` } },
  );
  const called = [...rec.runs.values()].filter((x) => x.type === "tool").map((x) => x.name).sort();
  const actualTool = called[0] ?? null;
  const final = String(r.messages[r.messages.length - 1].content);
  const ok = actualTool === c.expectTool && final.includes(c.expectInReply);
  if (ok) passed += 1;
  console.log(
    `  ${String(i + 1).padEnd(3)} ${c.input.padEnd(14)} ${String(actualTool).padEnd(14)} ${ok ? "✅ 通过" : "❌ 失败"}`,
  );
}
console.log();
console.log(`  结果：${passed}/${CASES.length} 通过`);
console.log();
console.log("  评测的两个层次（别只做第一层）：");
console.log("    ① 结果对不对 —— 最终答案是否满足预期（本例做的就是这层）");
console.log("    ② 过程对不对 —— 工具选得对不对、调了几次、有没有绕路");
console.log("       第二层才是 agent 评测和普通 LLM 评测的分水岭：");
console.log("       答案碰对了但过程全错，换个输入就会崩。");
console.log();
console.log("  ⚠️ 本示例的「判定」是字符串匹配，只是骨架。真实项目里判定器本身也要评测——");
console.log("     用 LLM 当裁判会引入位置偏差、冗长偏差、自我偏好、风格偏差四类系统性问题。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("③ 该盯哪几个数");
console.log("=".repeat(78));
console.log("  模型调用次数   agent 的成本基本正比于它；失控循环也看这个");
console.log("  输入 token     每轮都要重发完整历史，涨得比你想的快");
console.log("  缓存命中率     命中与否，单价可能差一个数量级");
console.log("  工具调用次数   工具选错 / 反复重试，看这里最直观");
console.log("  端到端 P95     平均延迟掩盖长尾，而用户体验由长尾决定");
console.log();
console.log("  ⚠️ 本示例的 trace 是离线回调，只记了耗时；token 与成本字段需要真实模型");
console.log("     返回的 usage 元数据，本机无 API Key，未实测——以官方文档为准。");
