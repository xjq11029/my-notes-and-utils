/**
 * 第 2 章示例（TypeScript 版，与 02_models.py 对应）：
 * 模型的创建与调用 —— 三个初始化角度与四种调用形态。
 *
 * 演示五件事：
 *   1. 模型初始化的三个角度：提供商库 / initChatModel / 本地 Ollama
 *   2. invoke 的三种入参形态，以及它们被归一化成什么（用假模型的 seen 观测）
 *   3. 返回值 AIMessage 的字段结构
 *   4. 三种调用形态：invoke / stream / batch（JS 没有 ainvoke，见 ④）
 *   5. profile 属性与 config 参数（tags / metadata / callbacks）
 *
 * ⚠️ 与 Python 的两处差异（本文件实测）：
 *   - initChatModel() 是**异步**的，必须 await；Python 的 init_chat_model() 是同步的。
 *   - JS 侧 invoke / stream / batch **本来就在 Promise 上**，没有 ainvoke 这套孪生方法。
 *
 * ⚠️ 未实测范围（本机没有模型 API Key，也没有本地 Ollama）：
 *   - 本机未装 @langchain/openai，所以「provider 前缀」这一节只能看到**报错**，
 *     构造不出真实的 ChatOpenAI（Python 侧装了包，能构造出来）；
 *   - 真实 provider 的 invoke、stream 的真实分块、token 计费**未实测**，逐处标注；
 *   - 本示例真正跑通的调用链路全部走假模型 ScriptedChatModel（见 _fakeModel.ts）。
 *
 * 运行：pnpm run 02_models
 */

import { initChatModel } from "langchain";
import { BaseCallbackHandler } from "@langchain/core/callbacks/base";
import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import { ScriptedChatModel, reply, toolCall } from "./_fakeModel";

/** 报错信息常常是多行的，这里只取第一行，方便对齐输出。 */
const firstLine = (e: unknown): string => String((e as Error).message).split("\n")[0];

/** 模块解析失败时 Node 会在错误里带上本机绝对路径——剪掉，保证输出可复现。 */
const shortErr = (e: unknown): string => firstLine(e).split(" imported from ")[0];

// ---------------------------------------------------------------------------
console.log("=".repeat(72));
console.log("① 模型初始化的三个角度：提供商库 / initChatModel / 本地 Ollama");
console.log("=".repeat(72));
console.log("  ⚠️ 本节只走到「构造出对象」，不发请求——真实调用需 API Key，未实测。");
console.log();

// 角度 1：模型提供商库 —— 直接 new 一个 ChatXxx 类
// 写法：import { ChatOpenAI } from "@langchain/openai";
//       const direct = new ChatOpenAI({ model: "gpt-4o", apiKey: "..." });
// 这里用动态 import 探测，包没装时打印原因而不是崩掉。
console.log("  角度 1｜提供商库：直接 new 一个 ChatXxx 类");
try {
  const spec = "@langchain/openai"; // 用变量包一层，避免 TS 在编译期就找不到模块
  const mod: any = await import(spec);
  const direct = new mod.ChatOpenAI({ model: "gpt-4o", apiKey: "sk-placeholder" });
  console.log(`    new ChatOpenAI({ model: "gpt-4o" }) → ${direct.constructor.name}`);
} catch (e: unknown) {
  console.log(`    （未安装 @langchain/openai，跳过：${shortErr(e)}）`);
}
console.log("    → 一个提供商一个包、一套参数名；换一家就得改 import 和参数名。");
console.log();

// 角度 2：统一入口 initChatModel()（注意：异步）
console.log('  角度 2｜统一入口：await initChatModel("provider:model")');
try {
  const unified: any = await initChatModel("openai:gpt-4o", { apiKey: "sk-placeholder" });
  console.log(`    initChatModel("openai:gpt-4o") → ${unified.constructor.name}`
    + "（前缀 openai 自动选中了 ChatOpenAI）");
} catch (e: unknown) {
  console.log(`    initChatModel("openai:gpt-4o") → ${(e as Error).constructor.name}: ${firstLine(e)}`);
}
console.log("    实测：initChatModel 返回的是 Promise —— 少一个 await，拿到的是 Promise 而不是模型。");
console.log();

console.log("    「provider 前缀 → 需要装哪个包」从报错里就能读出来（实测）：");
for (const modelId of ["deepseek:deepseek-chat", "ollama:llama3", "anthropic:claude-sonnet-4-5"]) {
  try {
    const m: any = await initChatModel(modelId, { apiKey: "sk-placeholder" });
    console.log(`      initChatModel(${JSON.stringify(modelId)}) → 构造成功：${m.constructor.name}`);
  } catch (e: unknown) {
    console.log(`      initChatModel(${JSON.stringify(modelId)}) → ${firstLine(e)}`);
  }
}
console.log("      ↑ 前缀名和包名不是一一对应的字符串（deepseek 的包是 @langchain/deepseek，");
console.log("        anthropic 的是 @langchain/anthropic），拼错时看到的就是这类报错。");
console.log();

console.log("    不写前缀时，框架得自己猜出提供商：");
try {
  const m: any = await initChatModel("qwen-plus");
  console.log(`      initChatModel("qwen-plus") → 构造成功：${m.constructor.name}`);
} catch (e: unknown) {
  console.log(`      initChatModel("qwen-plus") → ${(e as Error).constructor.name}: ${firstLine(e)}`);
}
console.log();

// 角度 3：本地模型
console.log("  角度 3｜本地模型：ChatOllama（需本机先起 Ollama 服务）");
try {
  const spec = "@langchain/ollama";
  const mod: any = await import(spec);
  const local = new mod.ChatOllama({ model: "deepseek-r1:1.5b", baseUrl: "http://localhost:11434" });
  console.log(`    new ChatOllama({ model: "deepseek-r1:1.5b" }) → ${local.constructor.name}`);
} catch (e: unknown) {
  console.log(`    （未安装 @langchain/ollama，跳过：${shortErr(e)}）`);
}
console.log('    → 也可以走统一入口：await initChatModel("deepseek-r1:1.5b", { modelProvider: "ollama" })。');
console.log("    ⚠️ Ollama 必须先在本机跑起来（默认 http://localhost:11434）。");
console.log("       服务没起、模型没 pull，构造能过，一 invoke 就连接失败——本机无 Ollama，未实测。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("② invoke 的三种入参形态，与模型实际收到的消息（seen 观测）");
console.log("=".repeat(72));

const probe = new ScriptedChatModel({
  script: [reply("收到。"), reply("收到。"), reply("收到。")],
});
const cases: Array<[string, any]> = [
  ["字符串", "翻译成英文：你好世界"],
  [
    "dict 列表",
    [
      { role: "system", content: "你是翻译助手。" },
      { role: "user", content: "翻译成英文：你好世界" },
    ],
  ],
  ["消息对象列表", [new SystemMessage("你是翻译助手。"), new HumanMessage("翻译成英文：你好世界")]],
];
for (const [label, payload] of cases) {
  await probe.invoke(payload);
  const received = probe.seen[probe.seen.length - 1];
  const kinds = received.map((m) => m.constructor.name);
  console.log(`  [${label}] 模型收到 ${received.length} 条：${JSON.stringify(kinds)}`);
  console.log(`      ${JSON.stringify(received.map((m) => [m.constructor.name, m.content]))}`);
}

console.log();
console.log("  → 三种写法归一化成同一件事：一条 system + 一条 human。");
console.log("    模型侧永远只认消息对象：字符串被包成一条 HumanMessage，dict 被逐条转换。");
console.log();

// 反例：单独一条 dict 不合法
try {
  await probe.invoke({ role: "user", content: "hi" } as any);
  console.log("  单条 dict → 竟然通过了");
} catch (e: unknown) {
  console.log(`  单条 dict → ${(e as Error).constructor.name}: ${firstLine(e)}`);
}
console.log("  → 「dict 形态」指的是 dict 的**列表**；传单条 dict 会被当成非法输入直接拒绝。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("③ 返回值 AIMessage 的字段结构");
console.log("=".repeat(72));

const textReply: any = await new ScriptedChatModel({ script: [reply("2 + 3 * 2 = 8")] }).invoke(
  "2 + 3 * 2 = ？",
);
console.log("  一条「正常回答」的 AIMessage：");
console.log(`    content            = ${JSON.stringify(textReply.content)}   ← 最终文本，最常读的就是它`);
console.log(`    tool_calls         = ${JSON.stringify(textReply.tool_calls)}   ← 模型请求调用的工具（这里没有）`);
console.log(`    invalid_tool_calls = ${JSON.stringify(textReply.invalid_tool_calls)}   ← 格式错误的调用尝试`);
console.log(`    response_metadata  = ${JSON.stringify(textReply.response_metadata)}   ← 假模型是空对象`);
console.log(`    usage_metadata     = ${JSON.stringify(textReply.usage_metadata)}   ← 假模型是 undefined`);
console.log(`    additional_kwargs  = ${JSON.stringify(textReply.additional_kwargs)}`);
console.log("    id                 = undefined   ← 假模型不填；真实 provider 会给一个运行 ID");

console.log();
console.log("  一条「请求调用工具」的 AIMessage：");
const withCall: any = await new ScriptedChatModel({
  script: [toolCall("get_weather", { city: "上海" }, "call_1")],
}).invoke("上海天气");
console.log(`    content    = ${JSON.stringify(withCall.content)}   ← 要调工具时，文本通常为空`);
console.log(`    tool_calls = ${JSON.stringify(withCall.tool_calls)}`);
console.log();
console.log("  → content / tool_calls 说的是「模型说了什么」；");
console.log("    response_metadata / usage_metadata 说的是「这次调用花了什么代价」——");
console.log("    模型版本、结束原因、token 数，都由真实 provider 填。");
console.log("    假模型不产生这两项，所以这里是空的，不是 bug。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("④ 三种调用形态：invoke / stream / batch（JS 没有 ainvoke）");
console.log("=".repeat(72));

const one: any = await new ScriptedChatModel({ script: [reply("一次性返回。")] }).invoke("你好");
console.log(`  invoke  → ${JSON.stringify(one.content)}`);
console.log("            阻塞：等模型全部生成完，再一次性返回一个 AIMessage。");

const chunks: any[] = [];
for await (const c of await new ScriptedChatModel({ script: [reply("流式输出。")] }).stream("你好")) {
  chunks.push(c);
}
console.log(`  stream  → ${chunks.length} 个 chunk：${JSON.stringify(chunks.map((c) => c.content))}`);
console.log("            ⚠️ 假模型只吐 1 个 chunk（一次给整条消息）；");
console.log("               真实模型逐 token 分多个 chunk，靠 for await 边收边显示。");

const outs: any = await new ScriptedChatModel({
  script: [reply("第一"), reply("第二"), reply("第三")],
}).batch(["q1", "q2", "q3"]);
console.log(`  batch   → ${JSON.stringify(outs.map((o: any) => o.content))}`);
console.log("            一批输入，按原顺序返回数组；真实场景下框架会并发发请求。");
console.log();
console.log("  → 与 Python 的差异：JS 侧没有 ainvoke / astream / abatch——");
console.log("    invoke / stream / batch 本来就返回 Promise，await 一下就是「异步版」。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(72));
console.log("⑤ profile 属性与 config 参数（tags / metadata / callbacks）");
console.log("=".repeat(72));

console.log("  profile：LangChain 给模型做的「能力画像」，声明过才有——");
const fakeProfile = new ScriptedChatModel({ script: [reply("x")] }).profile;
console.log(`    假模型 profile = ${JSON.stringify(fakeProfile)}（空对象；Python 侧同一位置是 None）`);
console.log("    真实模型下这样读（⚠️ 需 API Key，未实测）：");
console.log('      const m = await initChatModel("openai:gpt-4o", { apiKey: "..." });');
console.log("      m.profile.maxInputTokens / m.profile.toolCalling");
console.log("    → 用途：运行时判断这个模型支不支持工具调用、上下文窗口有多大。");
console.log();

class TagProbe extends BaseCallbackHandler {
  name = "TagProbe";

  /** config 里的 tags / metadata 不进消息，只能从回调这一侧看见。 */
  async handleChatModelStart(
    _llm: any,
    _messages: any,
    _runId: string,
    _parentRunId?: string,
    _extra?: any,
    tags?: string[],
    metadata?: Record<string, unknown>,
    runName?: string,
  ): Promise<void> {
    console.log(`    [回调] tags     = ${JSON.stringify(tags)}`);
    console.log(`    [回调] metadata = ${JSON.stringify(metadata)}`);
    console.log(`    [回调] runName  = ${JSON.stringify(runName)}`);
  }
}

console.log("  config：不改模型，只改「这一次调用」的记账方式");
const model = new ScriptedChatModel({ script: [reply("收到。")] });
await model.invoke("你好", {
  tags: ["ch02", "demo"],
  metadata: { user_id: "u-42" },
  callbacks: [new TagProbe()],
  runName: "my_run",
});
console.log("    → tags / metadata / runName 都不进消息、不改模型行为，");
console.log("      它们是给追踪系统（如 LangSmith）用的记账信息。");
console.log("      metadata 里多出的 ls_provider / ls_model_type / versions 是框架自动补的。");
console.log();

const pinned: any = new ScriptedChatModel({ script: [reply("收到。")] }).withConfig({
  tags: ["pinned"],
  metadata: { src: "withConfig" },
});
console.log("  withConfig：把 tags / metadata 钉在模型对象上");
console.log(`    返回对象类型 = ${pinned.constructor.name}（不再是 ScriptedChatModel，这是个容易踩的点）`);
await pinned.invoke("你好", { callbacks: [new TagProbe()] });
console.log("    → 返回的是包装后的 Runnable，照样能 invoke，但 instanceof 判断会失败；");
console.log("      要取回原对象用 .bound。");
