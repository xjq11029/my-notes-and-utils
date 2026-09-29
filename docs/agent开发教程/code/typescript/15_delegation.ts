/**
 * 第 15 章示例（TypeScript 版，与 15_delegation.py 对应）：
 * 规划与委派。
 *
 * 演示四件事：
 *   1. write_todos：任务列表长什么样、存在状态哪里
 *   2. subagents：怎么定义子代理
 *   3. task 工具：主代理如何把活派出去
 *   4. mode 'isolated' 与 'fork' 的区别
 *
 * 运行：pnpm run 11_delegation
 */

import { createDeepAgent } from "deepagents";
import { todoListMiddleware } from "langchain";
import { ScriptedChatModel, reply, toolCall } from "./_fakeModel";

// ---------------------------------------------------------------------------
console.log("=".repeat(78));
console.log("① write_todos：规划能力长什么样");
console.log("=".repeat(78));

const TODOS = [
  { content: "读需求文档", status: "completed" },
  { content: "设计数据模型", status: "in_progress" },
  { content: "写接口", status: "pending" },
];
const planned = createDeepAgent({
  model: new ScriptedChatModel({
    script: [toolCall("write_todos", { todos: TODOS }, "t1"), reply("计划已建。")],
  }) as any,
  middleware: [todoListMiddleware()] as any,
});
const out: any = await planned.invoke(
  { messages: [{ role: "user", content: "帮我规划一下" }] },
  { configurable: { thread_id: "todo-1" } },
);
console.log("  状态里的 todos：");
for (const item of out.todos) {
  const mark = item.status === "completed" ? "[x]" : item.status === "in_progress" ? "[~]" : "[ ]";
  console.log(`    ${mark} ${item.content}  (${item.status})`);
}
console.log();
console.log("  write_todos 是**全量覆盖**语义：模型每次都要把整张表重新写一遍，");
console.log("  而不是「追加一条」。所以状态里的 todos 永远是最新的一张完整表。");
console.log("  ⚠️ 这也意味着：模型忘掉一条，那条就真的没了——规划列表不是 append-only。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("② 定义子代理：SubAgent 的字段");
console.log("=".repeat(78));

const researcher = {
  name: "researcher",
  description: "负责查资料。当需要外部信息时派给它。", // ← 主代理靠这句话决定要不要派活
  systemPrompt: "你是调研员，只负责查资料并给出结论，不要改任何文件。",
  tools: [],
};
console.log("  SubAgent 的实测字段（Python 侧实测 11 个，JS 侧为同名 camelCase）：");
for (const f of [
  "name",
  "description",
  "systemPrompt",
  "tools",
  "model",
  "middleware",
  "interruptOn",
  "skills",
  "permissions",
  "responseFormat",
  "mode",
]) {
  console.log(`    · ${f}`);
}
console.log();
console.log(`  name        = ${JSON.stringify(researcher.name)}`);
console.log(`  description = ${JSON.stringify(researcher.description)}`);
console.log("  ⚠️ description 是子代理能不能被用上的**唯一依据**——");
console.log("     主代理看到的只有 name + description，它靠这句话判断该不该派活。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("③ task 工具：主代理把活派出去");
console.log("=".repeat(78));

const mBoss = new ScriptedChatModel({
  script: [
    toolCall("task", { description: "查一下 LangGraph 的检查点机制", subagent_type: "researcher" }, "c1"),
    reply("调研完成，结论如下……"),
  ],
});
const boss = createDeepAgent({ model: mBoss as any, subagents: [researcher] as any });
const bossOut: any = await boss.invoke(
  { messages: [{ role: "user", content: "帮我调研一下检查点机制" }] },
  { configurable: { thread_id: "delegate-1" } },
);
console.log(`  主代理暴露的工具里有 task 吗：${mBoss.lastBoundToolNames().includes("task")}`);
for (const m of bossOut.messages) {
  if (m.constructor.name === "ToolMessage") console.log(`  [task 返回] ${String(m.content).slice(0, 100)}`);
}
console.log();
console.log("  task 的返回是**一份最终报告**，不是子代理的完整对话——");
console.log("  子代理的中间过程留在它自己的上下文里，主代理只拿到结论。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("④ mode 'isolated' 与 'fork'：子代理能看见什么");
console.log("=".repeat(78));
console.log("  isolated（默认）  子代理拿到**干净的上下文**：只有你派给它的那段任务描述。");
console.log("                    适合：任务自包含、只需要一句话就能说清。");
console.log();
console.log("  fork              子代理**继承主代理当前的对话历史**，再叠加任务描述。");
console.log("                    适合：任务需要主代理已经积累的上下文才能做对。");
console.log();
console.log("  取舍：");
console.log("    isolated 上下文干净、省 token，但你要把背景写全；");
console.log("    fork     不用重复背景，但子代理的上下文一开始就很长，");
console.log("             隔离带来的收益被削掉一部分。");
console.log();
console.log("  ⚠️ 子代理的价值是**上下文隔离**，不是「多几个模型并行跑」。");
console.log("     如果任务之间需要频繁来回对齐，拆子代理反而更慢——");
console.log("     路由开销 + 交接时的上下文损失，这两项经常被低估。");
