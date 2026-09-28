/**
 * 第 14 章示例（TypeScript 版，与 14_multiagent.py 对应）：
 * 多智能体协作与从旧版迁移。
 *
 * 演示三件事：
 *   1. supervisor 拓扑：把 createAgent 建好的 agent 当节点塞进父图
 *   2. handoff 拓扑：用 Command 把控制权交给另一个 agent
 *   3. 从 LCEL / 旧版迁移到 v1 的写法对照
 *
 * 运行：pnpm run 14_multiagent
 */

import { createAgent, tool, HumanMessage } from "langchain";
import { Annotation, Command, END, START, StateGraph } from "@langchain/langgraph";
import { z } from "zod";
import { ScriptedChatModel, reply, toolCall } from "./_fakeModel";

// ---------------------------------------------------------------------------
console.log("=".repeat(78));
console.log("① supervisor 拓扑：agent 当节点");
console.log("=".repeat(78));

const queryDb = tool(async (args: { sql: string }) => `[${args.sql}] → 3 行结果`, {
  name: "query_db",
  description: "查数据库。",
  schema: z.object({ sql: z.string() }),
});
const sendEmail = tool(async (args: { to: string }) => `已发送给 ${args.to}`, {
  name: "send_email",
  description: "发邮件。",
  schema: z.object({ to: z.string() }),
});

const dbAgent = createAgent({
  model: new ScriptedChatModel({
    script: [toolCall("query_db", { sql: "select 1" }, "c1"), reply("查到 3 行。")],
  }) as any,
  tools: [queryDb],
  name: "db_agent",
});
const mailAgent = createAgent({
  model: new ScriptedChatModel({ script: [reply("邮件已发。")] }) as any,
  tools: [sendEmail],
  name: "mail_agent",
});

const TopState = Annotation.Root({
  messages: Annotation<any[]>({ reducer: (a, b) => a.concat(b), default: () => [] }),
  route: Annotation<string>({ default: () => "" }),
});

const top = new StateGraph(TopState)
  .addNode("supervisor", (s: any) => ({
    route: String(s.messages[s.messages.length - 1].content).includes("邮件") ? "mail" : "db",
  }))
  // ⚠️ JS 侧要把 agent 的 `.graph` 拿出来当节点（Python 侧可直接传 agent）
  .addNode("db", (dbAgent as any).graph)
  .addNode("mail", (mailAgent as any).graph)
  .addEdge(START, "supervisor")
  .addConditionalEdges("supervisor", (s: any) => s.route, { db: "db", mail: "mail" })
  .addEdge("db", END)
  .addEdge("mail", END)
  .compile();

for (const text of ["帮我查一下数据库", "帮我发个邮件"]) {
  const out: any = await top.invoke({ messages: [new HumanMessage(text)] });
  const last = out.messages[out.messages.length - 1];
  console.log(`  输入 ${JSON.stringify(text).padEnd(18)} → route=${out.route.padEnd(5)} 最终回复=${JSON.stringify(String(last.content))}`);
}
console.log();
console.log("  ⚠️ createAgent 返回的就是**已编译的图**，所以可以直接当节点用。");
console.log("     副作用：它变成了子图，流式输出需要 subgraphs: true（见第 8 章示例）。");
console.log("     记得给每个 agent 起 name，否则 trace 里分不清是谁在跑。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("② handoff 拓扑：用 Command 交棒");
console.log("=".repeat(78));

const HandState = Annotation.Root({
  messages: Annotation<any[]>({ reducer: (a, b) => a.concat(b), default: () => [] }),
  owner: Annotation<string>({ default: () => "" }),
});

const triage = (s: any): Command => {
  const text = String(s.messages[s.messages.length - 1].content);
  const target = text.includes("账单") ? "billing" : "tech";
  return new Command({ goto: target, update: { owner: target } });
};

const hand = new StateGraph(HandState)
  // 返回 Command 的节点必须声明 ends
  .addNode("triage", triage, { ends: ["billing", "tech"] })
  .addNode("billing", () => ({ messages: [{ role: "assistant", content: "[账单组] 已处理" }] }))
  .addNode("tech", () => ({ messages: [{ role: "assistant", content: "[技术组] 已处理" }] }))
  .addEdge(START, "triage")
  .addEdge("billing", END)
  .addEdge("tech", END)
  .compile();

for (const text of ["我要问账单", "系统报错了"]) {
  const out: any = await hand.invoke({ messages: [{ role: "user", content: text }] });
  console.log(
    `  输入 ${JSON.stringify(text).padEnd(16)} → owner=${out.owner.padEnd(8)} 回复=${JSON.stringify(out.messages[out.messages.length - 1].content)}`,
  );
}

console.log();
console.log("  supervisor vs handoff 的区别：");
console.log("    supervisor  有一个「调度者」节点反复决定下一步交给谁，交完还能收回来；");
console.log("    handoff     交棒后**不回来**，接手的 agent 负责到底——更像「转人工」。");
console.log("    前者适合需要多轮协调的任务，后者适合一次分流就结束的场景。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("③ 从旧版迁移到 v1");
console.log("=".repeat(78));

const rows: Array<[string, string, string]> = [
  ["建 agent", "AgentExecutor(agent, tools)", "createAgent({ model, tools })"],
  ["调用", "executor.invoke({ input })", "agent.invoke({ messages })"],
  ["输入形态", "字符串 input", "消息列表 messages"],
  ["输出形态", "{ output: '...' }", "{ messages: [...] }，取 messages.at(-1)"],
  ["提示词", "prompt 模板字符串", "prompt / systemPrompt + middleware"],
  ["记忆", "new BufferMemory()", "checkpointer + thread_id"],
  ["工具错误", "handleToolError", "wrapToolCall 或 toolErrorMiddleware"],
  ["运行时注入", "InjectedState / InjectedStore", "runtime 参数"],
  ["链式拼装", "LCEL 的 .pipe()", "StateGraph 的 addNode / addEdge"],
  ["扩展点", "自定义 Agent / 继承", "middleware 的六个钩子"],
];
console.log("  能力         旧版写法                           v1 写法");
console.log("  " + "-".repeat(88));
for (const [cap, old, now] of rows) {
  console.log(`  ${cap.padEnd(12)} ${old.padEnd(34)} ${now}`);
}

console.log();
console.log("  迁移的心智转变（比记 API 更重要）：");
console.log("    · 旧版：agent 是一个**组件**，你用 LCEL 把它串进链里；");
console.log("    · v1 ：agent 是一张**图**，你用节点和边定义控制流，用中间件扩展行为。");
console.log("    所以「迁移」不是换函数名，而是把控制流从链式表达改成图表达。");
console.log();
console.log("  建议顺序：① 先把 AgentExecutor 换成 createAgent（接口迁移，非行为等价）；");
console.log("            ② 再把 LCEL 的编排改成 StateGraph（这一步才真正动结构）；");
console.log("            ③ 最后把自定义逻辑收进 middleware。");
console.log("            一次全改，出了问题分不清是哪一步引入的。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("④ 部署形态");
console.log("=".repeat(78));
console.log("  托管（Agent Server）");
console.log("    · 持久化（checkpointer / store）由服务端自动提供，不用自己配");
console.log("    · 自带 trace、评测、人工审批的 UI");
console.log("    · 代价：绑定平台，本地调试与线上环境的差异要自己盯");
console.log();
console.log("  自托管");
console.log("    · 自己接 Postgres 做检查点与 Store，自己接观测后端");
console.log("    · 自由度最高，但「持久化」这件事必须一开始就做对——");
console.log("      中途从 MemorySaver 换到 PostgresSaver，历史数据是搬不过去的");
console.log();
console.log("  ⚠️ 无论哪种形态，上线前都该确认三件事：");
console.log("     ① 检查点有没有持久化（进程重启会不会丢会话）");
console.log("     ② 有没有调用次数上限（模型调用 / 工具调用都要限）");
console.log("     ③ 高风险操作有没有人在回路（扣款、发邮件、删文件）");
