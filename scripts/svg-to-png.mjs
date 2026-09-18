#!/usr/bin/env node
/**
 * svg-to-png.mjs —— 把 SVG 矢量源批量渲染为 2× PNG（供 Markdown 引用）
 *
 * 用途：本仓库的课程笔记配图约定为「SVG 矢量源 + 2× PNG 导出」，
 *       PNG 供 Markdown 引用（`![](assets/xx.png)`），SVG 供二次编辑。
 *       改完 SVG 后跑一次本脚本，即可重新生成全部 PNG。
 *
 * 用法：
 *   node scripts/svg-to-png.mjs <目录或 SVG 文件…> [--scale 2] [--force]
 *
 * 示例：
 *   node scripts/svg-to-png.mjs "docs/大模型与神经网络原理笔记/coding-agent/assets"
 *   node scripts/svg-to-png.mjs assets/06_mcp_flow.svg --scale 2
 *
 * 行为：
 *   - 递归查找目录下的 *.svg，在**同目录**生成同名 .png
 *   - 默认跳过已存在且比源文件新的 PNG；加 --force 强制全部重渲染
 *   - 文件名以 `_` 开头的 SVG 一律跳过（元文件 / 内部素材）
 *
 * 依赖：@resvg/resvg-js（见 scripts/package.json）
 *       首次使用先在 scripts/ 目录执行 `npm install`
 */

import { readdirSync, statSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname, basename, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

let Resvg;
try {
  ({ Resvg } = await import('@resvg/resvg-js'));
} catch {
  console.error('找不到依赖 @resvg/resvg-js。请先在 scripts/ 目录执行：');
  console.error('  npm install --registry=https://registry.npmmirror.com');
  process.exit(1);
}

/* ---------- 参数解析 ---------- */

const argv = process.argv.slice(2);

const scaleIdx = argv.indexOf('--scale');
const SCALE = scaleIdx >= 0 ? Number(argv[scaleIdx + 1]) : 2;
if (!Number.isFinite(SCALE) || SCALE <= 0) {
  console.error('--scale 必须为正数');
  process.exit(1);
}
const FORCE = argv.includes('--force');

// 位置参数 = 排除所有 --flag 及其取值（--scale 后面的那个数字）
const flagsWithValue = new Set(['--scale']);
const targets = [];
for (let i = 0; i < argv.length; i += 1) {
  const a = argv[i];
  if (a.startsWith('--')) {
    if (flagsWithValue.has(a)) i += 1; // 跳过取值
    continue;
  }
  targets.push(a);
}

if (targets.length === 0) {
  console.error('用法：node scripts/svg-to-png.mjs <目录或 SVG 文件…> [--scale 2] [--force]');
  process.exit(1);
}

/* ---------- 字体 ---------- */

// 中文字体必须显式指定，否则 resvg 可能回退到无中文字形的字体，导致方块 / 乱码。
const CANDIDATE_FONTS = [
  'C:/Windows/Fonts/msyh.ttc', // 微软雅黑
  'C:/Windows/Fonts/msyhbd.ttc',
  'C:/Windows/Fonts/simhei.ttf', // 黑体
  'C:/Windows/Fonts/simsun.ttc', // 宋体
  '/System/Library/Fonts/PingFang.ttc',
  '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
];
const fontFiles = CANDIDATE_FONTS.filter((p) => existsSync(p));

if (fontFiles.length === 0) {
  console.warn('⚠️  未找到任何已知中文字体文件，中文可能渲染为空白或方块。');
}

const FONT_OPTIONS = {
  loadSystemFonts: true,
  fontFiles,
  defaultFontFamily: 'Microsoft YaHei',
  sansSerifFamily: 'Microsoft YaHei',
};

/* ---------- 收集 SVG ---------- */

function collect(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    if (name.startsWith('_') || name.startsWith('.')) continue;
    const full = join(dir, name);
    const st = statSync(full);
    if (st.isDirectory()) out.push(...collect(full));
    else if (extname(name).toLowerCase() === '.svg') out.push(full);
  }
  return out;
}

const svgFiles = [];
for (const t of targets) {
  const abs = resolve(process.cwd(), t);
  if (!existsSync(abs)) {
    console.error(`跳过（不存在）：${t}`);
    continue;
  }
  const st = statSync(abs);
  if (st.isDirectory()) svgFiles.push(...collect(abs));
  else if (extname(abs).toLowerCase() === '.svg') svgFiles.push(abs);
}

if (svgFiles.length === 0) {
  console.error('没有找到任何 .svg 文件');
  process.exit(1);
}

/* ---------- 渲染 ---------- */

let rendered = 0;
let skipped = 0;
let failed = 0;

for (const svgPath of svgFiles.sort()) {
  const pngPath = svgPath.replace(/\.svg$/i, '.png');

  if (!FORCE && existsSync(pngPath) && statSync(pngPath).mtimeMs >= statSync(svgPath).mtimeMs) {
    console.log(`跳过（已是最新）：${basename(pngPath)}`);
    skipped += 1;
    continue;
  }

  try {
    const svg = readFileSync(svgPath, 'utf8');
    const resvg = new Resvg(svg, {
      fitTo: { mode: 'zoom', value: SCALE },
      font: FONT_OPTIONS,
      background: '#FFFFFF',
    });
    const image = resvg.render();
    const png = image.asPng();
    writeFileSync(pngPath, png);
    const { width, height } = image;
    console.log(
      `渲染：${basename(svgPath)} → ${basename(pngPath)}  ${width}×${height}  ${(png.length / 1024).toFixed(1)} KB`,
    );
    rendered += 1;
  } catch (err) {
    console.error(`失败：${basename(svgPath)} —— ${err.message}`);
    failed += 1;
  }
}

console.log(`\n完成：渲染 ${rendered} 张，跳过 ${skipped} 张，失败 ${failed} 张。`);
if (failed > 0) process.exit(1);
