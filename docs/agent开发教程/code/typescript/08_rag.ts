/**
 * 第 8 章示例（TypeScript 版，与 08_rag.py 对应）：
 * RAG 全链路 —— Load → Split → Embed → Store → Retrieve。
 *
 * 演示五件事：
 *   1. Document Loader：文件 → Document(page_content, metadata)
 *   2. Text Splitter：两种实现的差别
 *   3. Embeddings：文本 → 向量
 *   4. VectorStore：写入与相似度检索
 *   5. 检索器包成工具，交给 agent
 *
 * 全程离线、零 API Key。FakeEmbeddings 的向量没有语义——
 * 验证的是链路通不通，不是检索准不准。
 *
 * 运行：pnpm run 08_rag
 */

import { mkdtemp, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, basename } from "node:path";
import { createAgent, tool } from "langchain";
import { TextLoader } from "@langchain/classic/document_loaders/fs/text";
import { CSVLoader } from "@langchain/community/document_loaders/fs/csv";
import { JSONLoader } from "@langchain/classic/document_loaders/fs/json";
import {
  CharacterTextSplitter,
  RecursiveCharacterTextSplitter,
} from "@langchain/textsplitters";
import { MemoryVectorStore } from "@langchain/classic/vectorstores/memory";
import { FakeEmbeddings } from "@langchain/core/utils/testing";
import { z } from "zod";
import { ScriptedChatModel, reply, show, toolCall } from "./_fakeModel";

// ---------------------------------------------------------------------------
// 0. 现场造一份「私有语料」——不依赖任何外部素材
// ---------------------------------------------------------------------------
const TMP = await mkdtemp(join(tmpdir(), "rag_demo_"));

await writeFile(
  join(TMP, "notes.txt"),
  "RAG 的第一条铁律：检索质量决定生成质量。\n如果检索回来的片段本身不相关，再强的模型也只能编。\n",
  "utf-8",
);
await writeFile(
  join(TMP, "orders.csv"),
  "order_id,product,status\nA-1001,机械键盘,已发货\nA-1002,人体工学椅,待发货\n",
  "utf-8",
);
await writeFile(
  join(TMP, "faq.json"),
  JSON.stringify([
    { q: "RAG 是什么", a: "检索增强生成，提问前先把相关资料塞进上下文。" },
    { q: "为什么要切分", a: "为了控制单次进上下文的文本长度，并提高检索命中率。" },
  ]),
  "utf-8",
);

/** 多行压成一行并截断，便于终端对照 */
const flat = (t: string, w = 44) => {
  const one = t.split("\n").join(" / ");
  return one.length <= w ? one : one.slice(0, w - 3) + "...";
};

// ---------------------------------------------------------------------------
console.log("=".repeat(60));
console.log("① 文档加载器：所有 Loader 都只做一件事——文件 → Document");
console.log("=".repeat(60));

const txtDocs = await new TextLoader(join(TMP, "notes.txt")).load();
console.log(`  [TextLoader]  notes.txt → ${txtDocs.length} 个 Document`);
console.log(`      page_content = ${JSON.stringify(flat(txtDocs[0].pageContent))}`);
console.log(
  `      metadata     = ${JSON.stringify({ ...txtDocs[0].metadata, source: basename(String(txtDocs[0].metadata.source)) })}`,
);
console.log("      → 整个文件是一整条 page_content：Loader 不做任何切分。");

const csvDocs = await new CSVLoader(join(TMP, "orders.csv")).load();
console.log(`\n  [CSVLoader]   orders.csv → ${csvDocs.length} 个 Document（每行一条）`);
console.log(`      ${JSON.stringify(flat(csvDocs[0].pageContent))}`);
console.log("      → 列名被拼进了 page_content，行号落在 metadata 里。");

// ⚠️ 与 Python 的差异：TS 版 JSONLoader 收的是 JSON Pointer（RFC 6901），不是 jq 语法。
//    Python 写 jq_schema=".[].a"，这里等价写法是 ["/0/a", "/1/a"]。
const jsonDocs = await new JSONLoader(join(TMP, "faq.json"), ["/0/a", "/1/a"]).load();
console.log(`\n  [JSONLoader]  faq.json → ${jsonDocs.length} 个 Document（JSON Pointer）`);
for (const d of jsonDocs) console.log(`      ${JSON.stringify(flat(d.pageContent))}`);
console.log("      → 指针决定「取哪几条」「哪部分是正文」。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(60));
console.log("② 文档切分器：为什么切、怎么切");
console.log("=".repeat(60));

const longText =
  "LangChain 是一个用于构建大模型应用的框架。\n" +
  "它提供模型、工具、检索三块能力。\n" +
  "其中检索能力用于把外部知识接进模型。\n" +
  "向量数据库负责存储这些知识的向量表示。\n";

const charSplitter = new CharacterTextSplitter({
  separator: "\n",
  chunkSize: 40,
  chunkOverlap: 8,
});
const charChunks = await charSplitter.createDocuments([longText]);
console.log(`CharacterTextSplitter        → ${charChunks.length} 块`);
charChunks.forEach((c, i) => console.log(`  [${i + 1}] ${JSON.stringify(c.pageContent)}`));

const recSplitter = new RecursiveCharacterTextSplitter({ chunkSize: 40, chunkOverlap: 8 });
const recChunks = await recSplitter.createDocuments([longText]);
console.log(`\nRecursiveCharacterTextSplitter → ${recChunks.length} 块`);
recChunks.forEach((c, i) => console.log(`  [${i + 1}] ${JSON.stringify(c.pageContent)}`));

console.log("\n  → CharacterTextSplitter 只认一个分隔符，超长段落会硬切；");
console.log("    RecursiveCharacterTextSplitter 按「段落 → 句子 → 词」逐级回退，");
console.log("    尽量在自然边界断开，所以它是默认选择。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(60));
console.log("③ 嵌入 + 向量库：写入与检索");
console.log("=".repeat(60));

const embeddings = new FakeEmbeddings();
const vec = await embeddings.embedQuery("退换货");
const head = vec.slice(0, 4).map((x) => Number(x.toFixed(3)));
console.log(`embedQuery('退换货') → 维度 ${vec.length}，前 4 位 ${JSON.stringify(head)}`);
console.log("  → 真实嵌入模型的向量有语义（近义词距离近）；FakeEmbeddings 是随机但确定的，");
console.log("    所以下面检索到的内容不代表相关，只说明链路通了。");

const store = new MemoryVectorStore(embeddings);
await store.addDocuments([
  { pageContent: "退换货政策：签收后 7 天内可无理由退换。", metadata: { src: "faq.txt" } },
  { pageContent: "运费规则：单笔订单满 99 元免运费。", metadata: { src: "faq.txt" } },
  { pageContent: "会员等级：普通、银卡、金卡三档。", metadata: { src: "member.txt" } },
]);

const hits = await store.similaritySearch("退换货怎么处理", 2);
console.log(`\nsimilaritySearch('退换货怎么处理', 2) → ${hits.length} 条`);
hits.forEach((d, i) => console.log(`  [${i + 1}] ${d.metadata.src} | ${d.pageContent}`));

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(60));
console.log("④ 检索器包成工具，交给 agent");
console.log("=".repeat(60));

const searchDocs = tool(
  async (args: { query: string }) => {
    const found = await store.similaritySearch(args.query, 2);
    return found.map((d) => d.pageContent).join("\n");
  },
  {
    name: "search_docs",
    description: "在知识库中检索与问题相关的资料。",
    schema: z.object({ query: z.string().describe("检索关键词或自然语言问题") }),
  },
);

console.log(`工具名 = ${searchDocs.name}`);
const direct = await searchDocs.invoke({ query: "退换货" });
console.log(`直接调用 = ${JSON.stringify(String(direct).slice(0, 40))}...`);

const model = new ScriptedChatModel({
  script: [
    toolCall("search_docs", { query: "退换货" }, "call_1"),
    reply("商品签收后 7 天内可无理由退换。"),
  ],
});
const agent = createAgent({ model, tools: [searchDocs] });
const result = await agent.invoke({
  messages: [{ role: "user", content: "退换货怎么规定的？" }],
});
console.log("\nagent 的消息轨迹：");
show(result.messages);
console.log("\n  → 检索器只是普通工具的一种；agent 自己决定什么时候去查。");
console.log("    真实 RAG 的上限由检索质量决定——检索不到，模型再好也答不出。");

await rm(TMP, { recursive: true, force: true });
