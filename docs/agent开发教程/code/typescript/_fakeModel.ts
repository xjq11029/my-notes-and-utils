/**
 * 离线可用的可脚本化假模型（TypeScript 版）—— 与 Python 侧的 `_fake_model.py` 同语义。
 *
 * 为什么不用 langchain 自带的 `FakeToolCallingModel`：
 * 它的回复内容是从输入消息里**回显**拼出来的，不受控；
 * 而本教程的示例需要精确控制「模型说了什么」，所以自己实现一个。
 *
 * 关键点：必须实现 `bindTools`
 * ---------------------------
 * `createAgent` 在调模型前会执行 `model.bindTools(...)`。
 * 基类默认会抛错，所以这里原样返回自身。
 *
 * 另一个用途：`seen` 记录**模型每一次实际收到的消息**。
 * 中间件可以在消息到达模型之前改写它，而图状态里看到的可能仍是未改写的样子——
 * 只有从模型这一侧看，才知道模型究竟收到了什么。
 */

import { BaseChatModel } from "@langchain/core/language_models/chat_models";
import type { BaseChatModelCallOptions } from "@langchain/core/language_models/chat_models";
import { AIMessage, type BaseMessage } from "@langchain/core/messages";
import type { ChatGeneration, ChatResult } from "@langchain/core/outputs";

export class ScriptedChatModel extends BaseChatModel {
  script: AIMessage[];
  /** 每一次 `_generate` 实际收到的消息列表 */
  seen: BaseMessage[][] = [];
  /** 每一次 `bindTools` 实际收到的工具名——「模型被给了哪些工具」只能从这里看 */
  boundToolNames: string[][] = [];
  private cursor = 0;

  constructor(fields: { script: AIMessage[] }) {
    super({});
    this.script = fields.script;
  }

  _llmType(): string {
    return "scripted-fake-chat-model";
  }

  /** 真实模型在这里把工具 schema 绑进请求；假模型只记下名字，然后原样返回。 */
  bindTools(tools: Array<{ name?: string }> = []): this {
    this.boundToolNames.push(
      tools.map((t) => t?.name ?? "?").filter((n) => n !== "?"),
    );
    return this;
  }

  /** 最近一次绑定的工具名（升序） */
  lastBoundToolNames(): string[] {
    const last = this.boundToolNames[this.boundToolNames.length - 1] ?? [];
    return [...last].sort();
  }

  async _generate(messages: BaseMessage[]): Promise<ChatResult> {
    // 记下「模型实际收到什么」——中间件的效果只能从这里看见
    this.seen.push([...messages]);
    const idx = Math.min(this.cursor, this.script.length - 1);
    this.cursor += 1;
    const message = this.script[idx];
    const generation: ChatGeneration = { text: String(message.content), message };
    return { generations: [generation] };
  }
}

/** 构造一条「请求调用工具」的 AI 消息。 */
export function toolCall(name: string, args: Record<string, unknown>, id: string): AIMessage {
  return new AIMessage({
    content: "",
    tool_calls: [{ name, args, id, type: "tool_call" }],
  });
}

/** 构造一条「给出最终答案」的 AI 消息。 */
export function reply(text: string): AIMessage {
  return new AIMessage({ content: text });
}

/** 把一条消息序列打印成人能读的形式（示例统一用这个函数输出）。 */
export function show(messages: BaseMessage[]): void {
  messages.forEach((msg, i) => {
    let content = String(msg.content);
    if (content.length > 60) content = content.slice(0, 57) + "...";
    const calls = ((msg as AIMessage).tool_calls ?? []) as Array<{
      name: string;
      args: unknown;
    }>;
    const suffix = calls.length
      ? "  tool_calls=" + JSON.stringify(calls.map((c) => [c.name, c.args]))
      : "";
    console.log(`  ${i + 1}. [${msg.constructor.name}] ${JSON.stringify(content)}${suffix}`);
  });
}

/** 复刻框架内置的近似 token 计数（每 4 字符 1 token，每条消息 +3）。 */
export function approxTokens(messages: BaseMessage[]): number {
  const chars = messages.reduce((sum, m) => sum + String(m.content).length, 0);
  return Math.floor(chars / 4) + 3 * messages.length;
}

export type { BaseChatModelCallOptions };
