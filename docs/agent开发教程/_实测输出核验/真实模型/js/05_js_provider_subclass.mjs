/**
 * JS 侧真实模型验证：核对 code/README.md:104 与差异清单 #13/#14 的说法。
 *
 * 文档声明：
 *   「JS BaseChatModel 基类的 withStructuredOutput 只支持 function calling
 *    （源码写死：传 method: "jsonMode" 直接抛错），默认工具名 extract，
 *    jsonSchema 与 functionCalling 行为一致。
 *    provider 子类（如 ChatOpenAI）才可能覆写走原生 JSON schema——未实测。」
 *
 * 本脚本用 @langchain/openai 的 ChatOpenAI 指向智谱的 OpenAI 兼容端点，
 * 抓真正上线的 HTTP body，看 provider 子类到底走哪条路。
 *
 * 注意：这里装的 @langchain/openai / langchain 版本与教程 code/typescript 锁定的
 * 版本不同（见 05_js_output.txt 开头打印的版本），结论只能算「同生态实测补充」，
 * 不能直接替换教程正文的锚点版本。
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import http from "node:http";

const here = path.dirname(fileURLToPath(import.meta.url));
const KEY = readFileSync(path.resolve(here, "../../../code/.secrets.log"), "utf8").trim();

// ---- 用一个本地反代抓真实请求体，再转发到智谱 ------------------
const UPSTREAM = "https://open.bigmodel.cn/api/paas/v4";
const captured = [];

const proxy = http.createServer((req, res) => {
  const chunks = [];
  req.on("data", (c) => chunks.push(c));
  req.on("end", async () => {
    const body = Buffer.concat(chunks).toString("utf8");
    try {
      captured.push(JSON.parse(body));
    } catch {
      captured.push({ _unparsed: body.slice(0, 400) });
    }
    // BASE 已经带 /v4 前缀，langchain 请求的 req.url 也是 /v4/chat/completions，
    // 直接拼会变成 .../v4/v4/... → 404。剥掉重复前缀。
    const r = await fetch(UPSTREAM + req.url.replace(/^\/v4/, ""), {
      method: req.method,
      headers: { "content-type": "application/json", authorization: `Bearer ${KEY}` },
      body,
    });
    res.writeHead(r.status, { "content-type": "application/json" });
    res.end(await r.text());
  });
});
await new Promise((r) => proxy.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${proxy.address().port}/v4`;

const [{ ChatOpenAI }, { HumanMessage }] = await Promise.all([
  import("@langchain/openai"),
  import("@langchain/core/messages"),
]);
const { z } = await import("zod").catch(() => ({ z: null }));

console.log("=".repeat(78));
console.log("JS 真实模型：withStructuredOutput 的 method 在 provider 子类上改了什么");
console.log("=".repeat(78));

const mk = () =>
  new ChatOpenAI({
    model: "glm-4-plus",
    // @langchain/openai 1.6.2：apiKey 是顶层字段；baseURL 要走 configuration 且是
    // 大写 L 的 `baseURL`（写成 baseUrl 会被静默忽略、退回 api.openai.com）。
    apiKey: KEY,
    configuration: { baseURL: BASE },
    temperature: 0.1,
    maxTokens: 1024,
  });

const schema = z
  ? z.object({
      name: z.string().describe("姓名"),
      age: z.number().int().describe("年龄"),
      occupation: z.string().describe("职业"),
    })
  : null;

if (!schema) {
  console.log("  zod 未安装，跳过（pnpm add zod）");
} else {
  const PROMPT = "张三是一名 30 岁的软件工程师。请抽取人物信息。";
  for (const method of [undefined, "functionCalling", "jsonSchema", "jsonMode"]) {
    captured.length = 0;
    console.log(`\n  ── method=${method ?? "(缺省)"}`);
    try {
      const out = await mk()
        .withStructuredOutput(schema, {
          name: "Person",
          ...(method ? { method } : {}),
        })
        .invoke([new HumanMessage({ content: PROMPT })]);
      console.log(`     返回 = ${JSON.stringify(out)}`);
    } catch (e) {
      console.log(`     抛 ${e.constructor.name}: ${String(e.message).split("\n")[0].slice(0, 140)}`);
    }
    for (const b of captured) {
      const tools = b.tools;
      const rf = b.response_format;
      console.log(`     上线 tools           = ${tools ? JSON.stringify(tools.map((t) => t.function?.name ?? t.name)) : "None"}`);
      if (tools) console.log(`     上线 tool_choice     = ${JSON.stringify(b.tool_choice)}`);
      console.log(`     上线 response_format = ${rf ? JSON.stringify(rf).slice(0, 220) : "None"}`);
    }
    if (!captured.length) console.log("     （没抓到请求体）");
  }
}

proxy.close();
