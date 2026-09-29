/**
 * 第 9 章示例（TypeScript 版，与 09_context.py 对应）：
 * 上下文工程的四种手段。
 *
 * 本示例要回答一个很容易搞错的问题：
 * **「装了上下文中间件之后，图状态里的消息变少了吗？」**
 *
 * 答案是——**不一定**。所以本示例同时打印两个数字：
 *   · 状态里的消息数：result.messages 有多少条
 *   · 模型收到的消息数：从假模型那一侧记录的实际输入
 *
 * 运行：pnpm run 05_context
 */

import {
  createAgent,
  tool,
  contextEditingMiddleware,
  summarizationMiddleware,
  ClearToolUsesEdit,
  HumanMessage,
  type BaseMessage,
} from "langchain";
import { z } from "zod";
import { ScriptedChatModel, reply, toolCall, approxTokens } from "./_fakeModel";

const fetchLog = tool(async (args: { service: string }) => `[${args.service}] ` + "ERROR connection reset; ".repeat(40), {
  name: "fetch_log",
  description: "拉取某个服务的日志（返回内容很长，正是上下文膨胀的元凶）。",
  schema: z.object({ service: z.string() }),
});

async function runCase(title: string, middleware: any[], rounds = 6): Promise<void> {
  console.log();
  console.log("=".repeat(78));
  console.log(title);
  console.log("=".repeat(78));
  console.log("  轮次   状态消息数   模型收到消息数   模型收到 tokens");
  console.log("  " + "-".repeat(48));

  const script = [];
  for (let i = 0; i < rounds; i += 1) {
    script.push(toolCall("fetch_log", { service: `svc-${i}` }, `c${i}`));
    script.push(reply(`第 ${i} 轮排查完毕。`));
  }

  const model = new ScriptedChatModel({ script });
  const agent = createAgent({ model: model as any, tools: [fetchLog], middleware: middleware as any });

  let messages: BaseMessage[] = [];
  for (let i = 0; i < rounds; i += 1) {
    const out: any = await agent.invoke({
      messages: [...messages, new HumanMessage(`排查 svc-${i}`)],
    });
    messages = out.messages;
    const lastSeen = model.seen[model.seen.length - 1];
    console.log(
      `  ${String(i + 1).padEnd(6)} ${String(messages.length).padEnd(12)} ${String(
        lastSeen.length,
      ).padEnd(16)} ${approxTokens(lastSeen)}`,
    );
  }
}

// ---------------------------------------------------------------------------
await runCase("① 基线：不装任何中间件 —— 两个数字一起线性上涨", []);

// ---------------------------------------------------------------------------
await runCase("② summarizationMiddleware —— 状态本身被压缩（两个数字一起变小）", [
  summarizationMiddleware({
    model: new ScriptedChatModel({
      script: [reply("【摘要】前几轮排查了 svc-0 起的服务，均无新问题。")],
    }) as any,
    // ⚠️ JS 侧的 trigger / keep 都是**对象**：{ tokens } / { messages } / { fraction }
    //    而 Python 侧是位置参数：trigger=("messages", 8)、keep=("messages", 4)
    trigger: { messages: 8 },
    keep: { messages: 4 },
  }),
]);

// ---------------------------------------------------------------------------
await runCase("③ contextEditingMiddleware —— 状态继续涨，但模型收到的不涨", [
  contextEditingMiddleware({
    edits: [
      new ClearToolUsesEdit({
        trigger: { tokens: 600 },
        keep: { messages: 2 },
        placeholder: "[已清理：旧工具输出]",
      }),
    ],
  }),
]);

console.log();
console.log("=".repeat(78));
console.log("两种手段的机制差异（这是本示例的核心结论）");
console.log("=".repeat(78));
console.log();
console.log("  summarizationMiddleware");
console.log("    实现方式：before_model 钩子，返回一条摘要消息，**写回图状态**");
console.log("    后果    ：状态与模型输入一起变小；原文从当前状态消失");
console.log("              ⚠️「永久丢失」要加前提：**不配 checkpointer** 才是；");
console.log("                 配了 checkpointer 时，摘要前那个检查点仍保有原文（第 7 章）");
console.log("    适用    ：对话很长、旧轮次的细节确实不再需要");
console.log();
console.log("  contextEditingMiddleware");
console.log("    实现方式：wrap_model_call 钩子，复制一份消息、改完只传给模型，");
console.log("              **不回写状态**");
console.log("    后果    ：状态里的历史一条不少（便于审计 / 时间旅行），");
console.log("              但模型看不到那些被清掉的工具输出");
console.log("    适用    ：工具输出又大又只用一次（日志、网页正文、检索片段）");
console.log();
console.log("  ⚠️ 两者都会造成**静默失败**：清理和压缩本身不报错，");
console.log("     只是关键信息悄悄没了，后面的回答开始变差——不报错的失败最难查。");
console.log();
console.log("  第四种手段「外部存储」不在本章演示：把长内容写进虚拟文件系统或 Store，");
console.log("  上下文里只留一句「已保存到 /xxx」——见第 10 章与第 12 章。");
