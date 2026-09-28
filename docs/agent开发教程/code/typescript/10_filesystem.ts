/**
 * 第 10 章示例（TypeScript 版，与 10_filesystem.py 对应）：
 * 虚拟文件系统与执行环境。
 *
 * 演示四件事：
 *   1. 默认后端 StateBackend：文件存在图状态里，随线程走
 *   2. 文件工具的实际行为（write_file / read_file / edit_file / ls）
 *   3. FilesystemPermission 的声明式权限
 *   4. 后端谱系：StoreBackend / FilesystemBackend / CompositeBackend
 *
 * 运行：pnpm run 10_filesystem
 */

import {
  createDeepAgent,
  CompositeBackend,
  FilesystemBackend,
  LocalShellBackend,
  StateBackend,
  StoreBackend,
} from "deepagents";
import { InMemoryStore } from "@langchain/langgraph";
import { ScriptedChatModel, reply, toolCall } from "./_fakeModel";

// ---------------------------------------------------------------------------
console.log("=".repeat(78));
console.log("① 文件工具跑起来是什么样（StateBackend，文件存在图状态里）");
console.log("=".repeat(78));

const script = [
  toolCall("write_file", { file_path: "/notes/todo.md", content: "# 待办\n- 写文档\n- 跑测试" }, "c1"),
  toolCall("read_file", { file_path: "/notes/todo.md" }, "c2"),
  toolCall("edit_file", { file_path: "/notes/todo.md", old_string: "- 跑测试", new_string: "- 跑测试 ✅" }, "c3"),
  toolCall("ls", { path: "/notes" }, "c4"),
  reply("做完了。"),
];
const model = new ScriptedChatModel({ script });
const agent = createDeepAgent({ model: model as any });

const out: any = await agent.invoke(
  { messages: [{ role: "user", content: "先写个待办，再读出来改一改" }] },
  { configurable: { thread_id: "fs-1" } },
);
console.log(`  默认暴露给模型的工具（invoke 之后才取得到）：`);
console.log(`    ${JSON.stringify(model.lastBoundToolNames())}`);
console.log();
console.log("  逐条工具调用的返回值：");
for (const m of out.messages) {
  if (m.constructor.name === "ToolMessage") {
    const text = String(m.content).replace(/\n/g, "\\n");
    console.log(`    [${(m as any).name}] ${text.slice(0, 88)}`);
  }
}

console.log();
console.log(`  状态里的键：${JSON.stringify(Object.keys(out).sort())}`);
console.log(`  state.files = ${JSON.stringify(out.files)?.slice(0, 160)}`);
console.log();
console.log("  ⚠️ 关键点：StateBackend 把「文件」存在**图状态**里。");
console.log("     好处：跟着线程走，天然享受检查点（可回放、可时间旅行）；");
console.log("     代价：跨线程就没了——新 thread_id 打开是一张白纸。");
console.log("     要跨线程，得换 StoreBackend（见 ③）。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("② FilesystemPermission：声明式权限");
console.log("=".repeat(78));

console.log("  权限规则形如：");
console.log("    { operations: ['read', 'write'], paths: ['/workspace/**'], mode: 'allow' }");
console.log();
console.log("  三个字段：");
console.log("    operations  ['read', 'write'] 的数组");
console.log("    paths       路径 glob，如 '/workspace/**'");
console.log("    mode        'allow' | 'deny' | 'interrupt'");
console.log();
console.log("  ⚠️ mode='interrupt' 这一档容易被忽略：它不是「拒绝」，");
console.log("     而是**暂停下来问人**——权限系统与人在回路是打通的。");
console.log();
console.log("  规则按**声明顺序首次匹配即生效**（first match wins）：");
console.log("    1. 先声明「/secrets/** 禁止读写」");
console.log("    2. 再声明「/workspace/** 允许读写」");
console.log("    3. 没被任何规则命中的路径 → **默认 allow（放行）**");
console.log();
console.log("  ⚠️ 顺序写反了（先 allow /workspace/**，再 deny /workspace/secrets/**）");
console.log("     后一条永远不会生效——因为第一条已经命中了。");
console.log("     这条规则和防火墙的 ACL 是同一个思路：**具体规则放前面，宽泛规则放后面**。");
console.log("     ⚠️ 两个例外：① 未命中任何规则时**默认放行**（只写一条 deny 得不到白名单）；");
console.log("                 ② 递归 delete 的 deny **不受顺序约束**，更靠后的 deny 照样拦得住。");

// ---------------------------------------------------------------------------
console.log();
console.log("=".repeat(78));
console.log("③ 后端谱系：文件到底存在哪");
console.log("=".repeat(78));

const rows: Array<[string, string, string]> = [
  ["StateBackend", "图状态（默认）", "跟线程走、可回放；跨线程丢失"],
  ["StoreBackend", "LangGraph Store", "跨线程持久；适合 /memories/ 这类长期记忆"],
  ["FilesystemBackend", "真实磁盘", "直接读写本机文件；要小心权限"],
  ["LocalShellBackend", "本机 shell", "提供 execute 能力；生产环境慎用"],
  ["LangSmithSandbox", "托管沙箱", "隔离执行；适合不信任的代码"],
  ["CompositeBackend", "按路径分流", "如 /memories/** 走 Store，其余走 State"],
];
console.log(`  ${"后端".padEnd(20)} ${"落点".padEnd(16)} 特点`);
console.log("  " + "-".repeat(70));
for (const [name, where, note] of rows) {
  console.log(`  ${name.padEnd(20)} ${where.padEnd(16)} ${note}`);
}

console.log();
console.log("  实测确认：这几个类都能从 deepagents 顶层导入——");
console.log(`    ${JSON.stringify([StateBackend, StoreBackend, FilesystemBackend, LocalShellBackend, CompositeBackend].map((c) => c.name))}`);

console.log();
console.log("  CompositeBackend 的典型用法（把长期记忆单独分流）：");
console.log("    backend: (config) => new CompositeBackend(new StateBackend(config), {");
console.log("      '/memories/': new StoreBackend(config),");
console.log("    })");
console.log("  → agent 写 /memories/xxx 就跨线程持久，写别处仍走状态，各取所需。");
console.log();
console.log("  ⚠️ 默认后端是 StateBackend。");
console.log("     官方文档提到「默认写入图状态中的本地文件系统」，与实测一致。");
void new InMemoryStore();
