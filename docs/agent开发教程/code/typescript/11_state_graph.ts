/**
 * 第 11 章示例（TypeScript 版，与 11_state_graph.py 对应）：
 * LangGraph 的图与状态。
 *
 * 演示九件事：
 *   1. reducer —— 默认覆盖 vs Annotation 指定合并
 *   2. 同一线程再次 invoke：输入值按各字段自己的 reducer 合并
 *   3. 条件边
 *   4. Send：从一条边派发 N 个并行分支（map-reduce）
 *   5. Overwrite：绕过 reducer 强制覆盖
 *   6. addSequence 与静态扇入：多起点边会等所有起点完成
 *   7. 循环与 recursionLimit：GraphRecursionError
 *   8. 节点级容错：retryPolicy、async timeout、cachePolicy
 *   9. Functional API：entrypoint / task
 *
 * 运行：pnpm run 11_state_graph
 */

import {
  Annotation,
  END,
  GraphRecursionError,
  MemorySaver,
  NodeTimeoutError,
  Overwrite,
  START,
  Send,
  StateGraph,
  entrypoint,
  task,
} from "@langchain/langgraph";
import { InMemoryCache } from "@langchain/langgraph-checkpoint";

// ---------------------------------------------------------------------------
console.log("=".repeat(78));
console.log("① reducer：默认是覆盖，Annotation 才合并");
console.log("=".repeat(78));

const State = Annotation.Root({
  // 没有 reducer → 默认行为 = 用新值**覆盖**旧值
  counter: Annotation<number>({ default: () => 0 }),
  // 指定 reducer = 新值**追加**到旧值后面
  log: Annotation<string[]>({ reducer: (a, b) => a.concat(b), default: () => [] }),
  messages: Annotation<unknown[]>({
    reducer: (a: any[], b: any[]) => a.concat(b),
    default: () => [],
  }),
});

const g = new StateGraph(State)
  .addNode("a", () => ({ counter: 1, log: ["a 跑过"], messages: ["a"] }))
  .addNode("b", () => ({ counter: 2, log: ["b 跑过"], messages: ["b"] }))
  .addEdge(START, "a")
  .addEdge("a", "b")
  .addEdge("b", END)
  .compile();

const out: any = await g.invoke({ counter: 0, log: [], messages: ["起点"] });
console.log(`  counter  = ${out.counter}   ← 两个节点都写过，留下的是**最后一个**`);
console.log(`  log      = ${JSON.stringify(out.log)}   ← 两个节点的值被**合并**了`);
console.log(`  messages = ${JSON.stringify(out.messages)}`);
console.log("  → 同一个 State 里，不同字段可以有完全不同的合并规则，各管各的。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("② 同一线程再次 invoke：输入值按各字段自己的 reducer 合并");
console.log("=".repeat(78));

const Acc = Annotation.Root({
  n: Annotation<number>({ default: () => 0 }), // 默认 reducer = 覆盖
  trail: Annotation<string[]>({ reducer: (a, b) => a.concat(b), default: () => [] }),
});

const g2 = new StateGraph(Acc)
  .addNode("bump", (state: any) => {
    const n = state.n + 1;
    return { n, trail: [`→${n}`] };
  })
  .addEdge(START, "bump")
  .addEdge("bump", END)
  .compile({ checkpointer: new MemorySaver() });
const cfg = { configurable: { thread_id: "t-1" } };

const rows: Array<[string, any]> = [
  ["第 1 次", { n: 0, trail: ["起点"] }],
  ["第 2 次", null],
  ["第 3 次", {}],
  ["第 4 次", { n: 100 }],
  ["第 5 次", { trail: ["插一条"] }],
];
for (const [label, inp] of rows) {
  const r: any = await g2.invoke(inp, cfg);
  console.log(
    `  ${label}，输入 ${JSON.stringify(inp)?.padEnd(26) ?? "null".padEnd(26)} → n=${String(r.n).padEnd(4)} trail=${JSON.stringify(r.trail)}`,
  );
}

console.log();
console.log("  逐行读：");
console.log("  · 第 1 次：给了 n=0 和 trail，节点 +1 得 n=1");
console.log("  · 第 2 次：输入是 null —— **空操作**！已跑完的线程没有待执行任务，");
console.log("            直接返回当前状态（n 仍是 1）");
console.log("  · 第 3 次：输入是 {} —— 和 null **不一样**：图会从检查点状态重新执行，");
console.log("            节点读到检查点里的 n=1，+1 得 2");
console.log("  · 第 4 次：输入里给了 n=100，按默认 reducer（覆盖）冲掉检查点的 2，再 +1 得 101");
console.log("  · 第 5 次：输入里只有 trail，n 沿用检查点的 101，节点 +1 得 102；");
console.log("            trail 有 concat reducer，输入值被**追加**而不是替换");
console.log();
console.log("  结论（实测口径，Python / JS 一致）：");
console.log("  ① 输入字典里**出现**的字段 → 按该字段自己的 reducer 合并进检查点状态");
console.log("  ② 输入字典里**没出现**的字段 → 保留检查点里的值");
console.log("  ③ `invoke(null, cfg)` 是空操作；`invoke({}, cfg)` 才是「从检查点续跑」");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("③ 条件边：按状态决定下一步去哪");
console.log("=".repeat(78));

const Router = Annotation.Root({
  question: Annotation<string>({ default: () => "" }),
  route: Annotation<string>({ default: () => "" }),
  answer: Annotation<string>({ default: () => "" }),
});

const routerGraph = new StateGraph(Router)
  .addNode("classify", (s: any) => ({ route: s.question.includes("天气") ? "weather" : "math" }))
  .addNode("weather", (s: any) => ({ answer: `[天气分支] ${s.question} → 晴，22°C` }))
  .addNode("math", (s: any) => ({ answer: `[数学分支] ${s.question} → 42` }))
  .addEdge(START, "classify")
  .addConditionalEdges("classify", (s: any) => s.route, {
    weather: "weather",
    math: "math",
  })
  .addEdge("weather", END)
  .addEdge("math", END)
  .compile();

for (const q of ["今天天气怎么样", "1+1 等于几"]) {
  const r: any = await routerGraph.invoke({ question: q });
  console.log(`  输入 ${JSON.stringify(q)} → ${r.answer}`);
}

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("④ Send：map-reduce 式的并行派发");
console.log("=".repeat(78));

const FanState = Annotation.Root({
  items: Annotation<string[]>({ default: () => [] }),
  results: Annotation<string[]>({ reducer: (a, b) => a.concat(b), default: () => [] }),
});

const fan = new StateGraph(FanState)
  .addNode("worker", (s: any) => ({ results: [`${s.item} 处理完毕`] }))
  .addConditionalEdges(
    START,
    (s: any) => s.items.map((it: string) => new Send("worker", { item: it })),
    ["worker"],
  )
  .addEdge("worker", END)
  .compile();

const fanOut: any = await fan.invoke({ items: ["a", "b", "c"], results: [] });
console.log(`  items   = ${JSON.stringify(fanOut.items)}`);
console.log(`  results = ${JSON.stringify(fanOut.results)}`);
console.log("  → 三个 worker 在**同一个 super-step** 里并行执行；");
console.log("    结果靠 results 字段的 concat reducer 汇总——这就是 map-reduce。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("⑤ Overwrite：想清空合并型字段时怎么办");
console.log("=".repeat(78));

const g3 = new StateGraph(State)
  .addNode("reset", () => ({ log: new Overwrite([]) as any }))
  .addEdge(START, "reset")
  .addEdge("reset", END)
  .compile();
const resetOut: any = await g3.invoke({ counter: 0, log: ["旧值"], messages: [] });
console.log(`  log = ${JSON.stringify(resetOut.log)}`);
console.log("  → 直接返回 [] 是**没用的**（concat 会把 [] 拼上去，旧值还在）；");
console.log("    包一层 new Overwrite([]) 才是「我就是要覆盖」的显式指令。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("⑥ addSequence 与静态扇入：顺序、并行汇合");
console.log("=".repeat(78));

const Flow = Annotation.Root({
  trail: Annotation<string[]>({ reducer: (a, b) => a.concat(b), default: () => [] }),
});

const seqA = () => ({ trail: ["a"] });
const seqB = () => ({ trail: ["b"] });
const sequence = new StateGraph(Flow)
  .addSequence([["seq_a", seqA], ["seq_b", seqB]] as any)
  .addEdge(START, "seq_a")
  .addEdge("seq_b", END)
  .compile();
const seqOut: any = await sequence.invoke({ trail: [] });
console.log(`  addSequence([a, b]) → ${JSON.stringify(seqOut.trail)}`);

const left = () => ({ trail: ["left"] });
const right = () => ({ trail: ["right"] });
const join = (s: any) => ({ trail: [`join<-${[...s.trail].sort().join(",")}`] });
const fanIn = new StateGraph(Flow)
  .addNode("left", left)
  .addNode("right", right)
  .addNode("join", join)
  .addEdge(START, "left")
  .addEdge(START, "right")
  .addEdge(["left", "right"], "join")
  .addEdge("join", END)
  .compile();
const fanInOut: any = await fanIn.invoke({ trail: [] });
console.log(`  静态扇入 START→left/right→join → ${JSON.stringify(fanInOut.trail)}`);
console.log("  → addEdge(['left','right'], 'join') 的含义是「等两个起点都完成后再跑 join」。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("⑦ 循环与 recursionLimit：本机 langgraph 1.4.17 的默认值随版本变化");
console.log("=".repeat(78));

const Loop = Annotation.Root({
  n: Annotation<number>({ default: () => 0 }),
});

const loop = new StateGraph(Loop)
  .addNode("inc", (s: any) => ({ n: s.n + 1 }))
  .addEdge(START, "inc")
  .addConditionalEdges("inc", (s: any) => (s.n < 3 ? "inc" : END), { inc: "inc", [END]: END })
  .compile();
console.log(`  循环到 n>=3 自动退出 → ${JSON.stringify(await loop.invoke({ n: 0 }))}`);

try {
  await loop.invoke({ n: 0 }, { recursionLimit: 3 });
} catch (e: any) {
  console.log(`  recursionLimit=3 → ${e.constructor.name}: ${String(e.message).split("\n")[0]}`);
}
console.log("  → JS 侧配置键是 recursionLimit（驼峰），Python 侧是 recursion_limit（下划线）。");
console.log("    RemainingSteps：JS 1.4.17 未导出同名 managed 值，本节只演示 Python 侧。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("⑧ retryPolicy / async timeout / cachePolicy");
console.log("=".repeat(78));

let attempts = 0;
const retryGraph = new StateGraph(Loop)
  .addNode(
    "flaky",
    () => {
      attempts += 1;
      if (attempts < 3) throw new Error("boom");
      return { n: 1 };
    },
    { retryPolicy: { maxAttempts: 3, initialInterval: 1, jitter: false } },
  )
  .addEdge(START, "flaky")
  .addEdge("flaky", END)
  .compile();
console.log(`  retryPolicy(maxAttempts=3) → ${JSON.stringify(await retryGraph.invoke({ n: 0 }))}，实际尝试 ${attempts} 次`);
console.log("  → JS 的 initialInterval 单位是毫秒；Python 的 initial_interval 单位是秒（差异已登记）。");

const timeoutGraph = new StateGraph(Loop)
  .addNode(
    "slow",
    async () => {
      await new Promise((resolve) => setTimeout(resolve, 200));
      return { n: 1 };
    },
    { timeout: 50 },
  )
  .addEdge(START, "slow")
  .addEdge("slow", END)
  .compile();
try {
  await timeoutGraph.invoke({ n: 0 });
} catch (e: any) {
  console.log(`  async 节点 timeout=50ms → ${e.constructor.name}: ${String(e.message).split(" (elapsed")[0]}`);
}

let cacheRuns = 0;
const cacheGraph = new StateGraph(Loop)
  .addNode(
    "pure",
    (s: any) => {
      cacheRuns += 1;
      return { n: s.n + 1 };
    },
    { cachePolicy: { ttl: 60 } },
  )
  .addEdge(START, "pure")
  .addEdge("pure", END)
  .compile({ cache: new InMemoryCache() });
await cacheGraph.invoke({ n: 1 });
await cacheGraph.invoke({ n: 1 });
console.log(`  同一输入调用两次 cachePolicy(ttl=60) → 节点实际执行 ${cacheRuns} 次`);
console.log("  → JS 的内置 InMemoryCache 在 @langchain/langgraph-checkpoint 包里，不在 @langchain/langgraph 顶层。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("⑨ Functional API：entrypoint / task");
console.log("=".repeat(78));

const pipeline = entrypoint("pipeline", async (x: number) => {
  const a = await task("add_one", async (v: number) => v + 1)(x);
  const b = await task("triple", async (v: number) => v * 3)(a);
  return b;
});
console.log(`  entrypoint 串行：3 → add_one → triple = ${await pipeline.invoke(3)}`);

const fanTasks = entrypoint("fan_tasks", async (x: number) => {
  const f1 = task("add_one", async (v: number) => v + 1)(x);
  const f2 = task("triple", async (v: number) => v * 3)(x);
  return (await f1) + (await f2);
});
console.log(`  两个 task 并行后汇总：(3+1) + (3×3) = ${await fanTasks.invoke(3)}`);
console.log("  → Graph API 用节点/边描述形状；Functional API 用普通函数调用描述同一件事。");
