/**
 * 按顺序跑完所有示例 —— `pnpm run all`
 *
 * 用途：改过任何示例或升级依赖后，一条命令确认全部仍然通过。
 */

import { spawnSync } from "node:child_process";

const FILES = [
  "02_create_agent",
  "03_middleware",
  "04_tools",
  "05_context",
  "06_state_graph",
  "07_persistence",
  "08_hitl_stream",
  "09_deep_agent",
  "10_filesystem",
  "11_delegation",
  "12_skills_memory",
  "13_observability",
  "14_multiagent",
];

let failed = 0;
for (const f of FILES) {
  // 失败时必须能看到原因：原先把 stdout/stderr 全丢掉，出问题只剩一行 FAIL，
  // 没法定位（pnpm 自身被环境拦下时 13 个会全挂，看起来像代码问题）。
  // 改成：成功静默，失败时原样透传输出与 spawn error。
  const r = spawnSync("pnpm", ["run", f], {
    stdio: ["ignore", "pipe", "pipe"],
    encoding: "utf-8",
    shell: true,
  });
  const ok = r.status === 0;
  if (!ok) {
    failed += 1;
    console.log(`FAIL  ${f}`);
    if (r.error) console.log(`  spawn error: ${r.error.message}`);
    if (r.stdout?.trim()) console.log(`  stdout:\n${r.stdout.trim()}`);
    if (r.stderr?.trim()) console.log(`  stderr:\n${r.stderr.trim()}`);
  } else {
    console.log(`OK    ${f}`);
  }
}
console.log(`\n完成：${FILES.length - failed}/${FILES.length} 通过`);
process.exit(failed > 0 ? 1 : 0);
