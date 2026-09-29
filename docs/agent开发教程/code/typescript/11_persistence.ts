/**
 * 第 11 章示例（TypeScript 版，与 11_persistence.py 对应）：
 * 持久化与持久执行。
 *
 * 演示五件事：
 *   1. checkpointer 让「同一线程」的第二次调用接着上次的状态跑
 *   2. getState / getStateHistory —— 看清检查点长什么样
 *   3. updateState —— 时间旅行：改历史再重放
 *   4. Store —— 跨线程的长期记忆（与 checkpointer 的分工）
 *   5. Store 的命名空间与前缀搜索语义
 *
 * 运行：pnpm run 07_persistence
 */

import {
  Annotation,
  END,
  MemorySaver,
  START,
  StateGraph,
  InMemoryStore,
} from "@langchain/langgraph";

const Counter = Annotation.Root({
  n: Annotation<number>({ default: () => 0 }),
  trail: Annotation<string[]>({ default: () => [] }),
});

const step = (state: any) => {
  const n = state.n + 1;
  return { n, trail: [...(state.trail ?? []), `step→${n}`] };
};

// ---------------------------------------------------------------------------
console.log("=".repeat(78));
console.log("① checkpointer：同一线程接着上次跑");
console.log("=".repeat(78));

const graph = new StateGraph(Counter)
  .addNode("step", step)
  .addEdge(START, "step")
  .addEdge("step", END)
  .compile({ checkpointer: new MemorySaver() });
const cfg = { configurable: { thread_id: "order-2026" } };

const r1: any = await graph.invoke({ n: 0, trail: [] }, cfg);
console.log(`  第 1 次，输入 {n:0, trail:[]}      → n=${r1.n}, trail=${JSON.stringify(r1.trail)}`);
const r2: any = await graph.invoke({}, cfg);
console.log(`  第 2 次，输入 {}（从检查点续跑）  → n=${r2.n}, trail=${JSON.stringify(r2.trail)}`);
const r3: any = await graph.invoke(null, cfg);
console.log(`  第 3 次，输入 null（空操作）      → n=${r3.n}, trail=${JSON.stringify(r3.trail)}`);
const r4: any = await graph.invoke({ n: 100 }, cfg);
console.log(`  第 4 次，输入 {n:100}（覆盖 n）    → n=${r4.n}, trail=${JSON.stringify(r4.trail)}`);

console.log();
console.log("  读法（与 Python 侧实测一致）：");
console.log("  · `invoke({}, cfg)` —— 空对象：图从检查点状态**重新执行**，n 从 1 变 2；");
console.log("  · `invoke(null, cfg)` —— null：**空操作**。已跑完的线程没有待执行任务，");
console.log("    直接返回当前状态，图一步都没跑；");
console.log("  · 第 4 次输入里给了 n=100，按默认 reducer 覆盖掉检查点里的 2，再 +1 得 101；");
console.log("  · trail 一直在长，因为输入里从没给过 trail，它一直沿用检查点里的值。");

// ---------------------------------------------------------------------------
console.log();
console.log("  状态快照（getState）：");
const snap: any = await graph.getState(cfg);
console.log(`    values = ${JSON.stringify(snap.values)}`);
console.log(`    next   = ${JSON.stringify(snap.next)}    ← 空数组表示已跑完`);
console.log(`    config = ${JSON.stringify(snap.config.configurable)}`);

console.log();
console.log("  检查点历史（getStateHistory）：");
const history: any[] = [];
for await (const s of await graph.getStateHistory(cfg)) history.push(s);
console.log(`    共 ${history.length} 个检查点：`);
history.slice().reverse().forEach((s: any, i: number) => {
  console.log(
    `      [${i}] step=${String(s.metadata?.step).padStart(2)}  n=${s.values?.n}  next=${JSON.stringify(s.next)}`,
  );
});

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("③ updateState：改写历史再重放（时间旅行）");
console.log("=".repeat(78));

const target = history[history.length - 2];
console.log(`  选中的历史检查点：step=${target.metadata?.step}, n=${target.values?.n}`);
const forked: any = await graph.updateState(target.config, {
  n: 100,
  trail: ["人工改写：从 100 开始"],
});
const replayed: any = await graph.invoke(null, forked);
console.log(`  重放结果：n = ${replayed.n}, trail = ${JSON.stringify(replayed.trail)}`);
console.log("  → updateState 会**新建一个分支**，原线程的历史不受影响。");
console.log("    这是调试 agent 的利器：把某一步的状态改一改，看后面会怎么走。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("④ Store：跨线程的长期记忆（与 checkpointer 的分工）");
console.log("=".repeat(78));

const store = new InMemoryStore();
const USER = ["alice", "memories"];

await store.put(USER, "pref-food", { text: "喜欢川菜" });
await store.put(USER, "pref-city", { text: "住在杭州" });
await store.put(["alice", "notes"], "note-1", { text: "上周开会提到 Q3 目标" });

const food: any = await store.get(USER, "pref-food");
console.log(`  store.get(['alice','memories'], 'pref-food') → ${JSON.stringify(food?.value)}`);

console.log();
console.log("  前缀搜索的坑（namespacePrefix 是**前缀**匹配，不是精确匹配）：");
const hits: any[] = await store.search(["alice"]);
console.log(`    store.search(['alice']) 命中 ${hits.length} 条：`);
for (const item of hits) {
  console.log(`      namespace=${JSON.stringify(item.namespace)}  key=${item.key}  value=${JSON.stringify(item.value)}`);
}

console.log();
const memOnly: any[] = await store.search(USER);
console.log(`  只想要 memories 这一层：store.search(['alice','memories']) → ${JSON.stringify(memOnly.map((i: any) => i.key))}`);
const nsList: any[] = await store.listNamespaces({ prefix: ["alice"] });
console.log(`  列出命名空间：store.listNamespaces({ prefix: ['alice'] }) → ${JSON.stringify(nsList)}`);
console.log("  → 一旦数据多了，把命名空间写细（['alice','memories'] 而不是 ['alice']）能省掉不少误命中。");

console.log();
console.log("=".repeat(78));
console.log("checkpointer 与 store 的分工");
console.log("=".repeat(78));
console.log("  作用范围   checkpointer = 单个线程（thread） / store = 跨线程");
console.log("  存什么     checkpointer = 图状态的完整快照 / store = 应用自定义键值数据");
console.log("  怎么取     checkpointer = 传 thread_id      / store = 节点里用 runtime.store");
console.log("  典型用途   对话延续 / 人在回路 / 时间旅行 / 故障恢复");
console.log("             用户偏好 / 长期事实 / 共享知识");
console.log();
console.log("  ⚠️ 生产环境别用 MemorySaver / InMemoryStore —— 进程一重启就全没了。");
console.log("     持久化检查点要用 @langchain/langgraph-checkpoint-* 系列包。");
