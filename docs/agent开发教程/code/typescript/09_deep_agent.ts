/**
 * 第 9 章示例（TypeScript 版，与 09_deep_agent.py 对应）：
 * Deep Agents 全景。
 *
 * 演示四件事：
 *   1. createDeepAgent 默认给你哪些工具（与官方文档的差异在这里显式指出）
 *   2. 规划能力默认**不开**，要显式加 todoListMiddleware
 *   3. 预装中间件栈 —— 打印真实的图节点名
 *   4. HarnessProfile：声明式地裁掉不要的能力
 *
 * 运行：pnpm run 09_deep_agent
 */

import { createDeepAgent, createHarnessProfile, registerHarnessProfile, getHarnessProfile } from "deepagents";
import { todoListMiddleware } from "langchain";
import { ScriptedChatModel, reply, toolCall } from "./_fakeModel";

function runOnce(agent: any, thread = "probe") {
  return agent.invoke(
    { messages: [{ role: "user", content: "你好" }] },
    { configurable: { thread_id: thread } },
  );
}

// ---------------------------------------------------------------------------
console.log("=".repeat(78));
console.log("① createDeepAgent 默认给你哪些工具");
console.log("=".repeat(78));

const m0 = new ScriptedChatModel({ script: [reply("好的")] });
const agent0 = createDeepAgent({ model: m0 as any });
console.log(`  构造完还没 invoke 时：${JSON.stringify(m0.lastBoundToolNames())}   ← bindTools 还没触发`);
await runOnce(agent0);
const names = m0.lastBoundToolNames();
console.log(`  invoke 一次之后：共 ${names.length} 个`);
console.log(`  ${JSON.stringify(names)}`);
console.log();
console.log("  模型实际看到的这些，按用途分：");
console.log("    文件读写  ls / read_file / write_file / edit_file / delete");
console.log("    文件检索  glob / grep");
console.log("    委派      task（创建子代理）");
console.log();
console.log("  ⚠️ 这里有个容易搞错的点：**「注册了工具」不等于「模型看得见」**。");
console.log("     Python 侧实测：工具节点里注册了 9 个（多一个 execute），");
console.log("     但默认后端 StateBackend 不提供执行能力，所以 execute **没有被绑定给模型**。");
console.log("     想看 agent 到底能干什么，要看模型被绑定了什么。");
console.log();
console.log("  ⚠️ 与官方文档的差异：文档把 write_todos 列为「v0.7 起需主动开启」——");
console.log("     实测确认默认绑定给模型的工具里确实没有 write_todos。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("② 显式加 todoListMiddleware，write_todos 才出现");
console.log("=".repeat(78));

const m1 = new ScriptedChatModel({
  script: [
    toolCall(
      "write_todos",
      { todos: [{ content: "调研", status: "in_progress" }, { content: "写稿", status: "pending" }] },
      "t1",
    ),
    reply("计划已建立。"),
  ],
});
const planned = createDeepAgent({ model: m1 as any, middleware: [todoListMiddleware()] as any });
const out1: any = await planned.invoke(
  { messages: [{ role: "user", content: "帮我做个计划" }] },
  { configurable: { thread_id: "todo-1" } },
);
const names2 = m1.lastBoundToolNames();
console.log(`  加中间件后共 ${names2.length} 个：${JSON.stringify(names2)}`);
console.log(`  write_todos 出现了：${names2.includes("write_todos")}`);
console.log(`  运行后状态里多出的键：${JSON.stringify(Object.keys(out1).filter((k) => k !== "messages"))}`);
console.log(`  todos = ${JSON.stringify(out1.todos)}`);

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("③ 预装中间件栈 —— 图里到底挂了哪些节点");
console.log("=".repeat(78));

const configs: Array<[string, Record<string, unknown>]> = [
  ["裸的（只给 model）", {}],
  ["+ 记忆 + 技能", { memory: ["/memories/AGENTS.md"], skills: ["/skills/"] }],
  ["+ 子代理", { subagents: [{ name: "researcher", description: "做调研", systemPrompt: "你负责调研" }] }],
  ["+ 人工审批", { interruptOn: { execute: true } }],
];
for (const [label, kw] of configs) {
  const a: any = createDeepAgent({ model: new ScriptedChatModel({ script: [reply("ok")] }) as any, ...kw });
  const nodes = Object.keys(a.graph.nodes).filter((n) => !n.startsWith("__"));
  console.log(`  ${label.padEnd(20)} → 节点 ${JSON.stringify(nodes)}`);
}

console.log();
console.log("  读法：");
console.log("    · 固定节点 model / tools 是所有 agent 共有的骨架；");
console.log("    · 形如 `XxxMiddleware.before_agent` 的节点，是**中间件自己插进来的钩子节点**；");
console.log("    · 挂了 memory 才有 MemoryMiddleware 节点，挂了 skills 才有 SkillsMiddleware 节点——");
console.log("      所以「看节点名」是反查「这个 agent 到底装了哪些能力」最快的方式。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("④ HarnessProfile：声明式裁剪内置能力");
console.log("=".repeat(78));

const profile = createHarnessProfile({
  systemPromptSuffix: "回答一律用中文。",
  excludedTools: ["execute"], // 不要执行能力
  toolDescriptionOverrides: { grep: "在本项目源码里搜索。" },
});
// ⚠️ excludedTools 是 **Set**，不是数组——直接 JSON.stringify 会得到 {}
console.log(`  profile.excludedTools = ${JSON.stringify(Array.from(profile.excludedTools))}`);
console.log(`  profile.systemPromptSuffix = ${JSON.stringify(profile.systemPromptSuffix)}`);

registerHarnessProfile("my-profile", profile);
const back: any = getHarnessProfile("my-profile");
console.log(`  已注册并回读 profile：excludedTools = ${JSON.stringify(Array.from(back?.excludedTools ?? []))}`);

console.log();
console.log("  ⚠️ 与 Python 的三处差异（实测）：");
console.log("     ① JS 的工厂函数叫 createHarnessProfile，Python 直接 new HarnessProfile(...)；");
console.log("     ② JS 的字段是 camelCase（systemPromptSuffix / excludedTools），");
console.log("        Python 是 snake_case（system_prompt_suffix / excluded_tools）；");
console.log("     ③ JS 的 excludedTools 是 Set，Python 是 frozenset。");
console.log();
console.log("  ⚠️ 图节点名两边也不同（实测，别照抄）：");
console.log("     JS     → model_request / tools / FilesystemMiddleware.before_agent /");
console.log("              patchToolCallsMiddleware.before_agent（P 小写）");
console.log("     Python → model / tools / PatchToolCallsMiddleware.before_agent（P 大写）");
console.log("     结论：**节点名是内部实现细节**，跨语言、跨版本都可能变；");
console.log("           要判断「装了哪些能力」，用工具列表或中间件清单，别硬编码节点名。");
console.log();
console.log("  用 profile 而不是「自己拼中间件」的好处：内置能力升级时你不用跟着改。");
