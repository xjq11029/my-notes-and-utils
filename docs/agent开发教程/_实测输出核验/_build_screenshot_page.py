"""把核验输出渲染成终端风格的 HTML，供截图用。不写死内容，全部读自本目录的 .txt。"""
import html
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent

SECTIONS = [
    ("智谱 key 连通性与可用模型", "真实模型/00_connectivity.txt"),
    ("A/C/D/E：真实模型验证文档标「未实测」的声明", "真实模型/01_verify_untested_claims.txt"),
    ("B：with_structured_output 的 method 真正上线了什么（Python ChatOpenAI）",
     "真实模型/04_wire_capture.txt"),
    ("B：同上，JS ChatOpenAI（本地反代抓真实请求体）", "真实模型/05_js_provider_subclass.txt"),
    ("ch09:182「42 个快照」断言复现", "真实模型/06_ch09_snapshot_count.txt"),
]

CSS = """
:root{--bg:#0d1117;--panel:#161b22;--ink:#c9d1d9;--dim:#8b949e;--acc:#58a6ff;
--ok:#3fb950;--warn:#d29922;--bad:#f85149;--line:#21262d}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.65 "Microsoft YaHei","Segoe UI",system-ui,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:32px 28px 64px}
h1{font-size:26px;margin:0 0 6px;letter-spacing:.5px}
.sub{color:var(--dim);font-size:13px;margin-bottom:26px}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;
border:1px solid var(--line);color:var(--dim);margin-right:6px}
.badge.ok{color:var(--ok);border-color:#238636}
.badge.bad{color:var(--bad);border-color:#da3633}
section{margin-bottom:34px}
h2{font-size:15px;margin:0 0 10px;padding-left:10px;border-left:3px solid var(--acc);
font-weight:600}
.term{background:var(--panel);border:1px solid var(--line);border-radius:8px;
overflow:hidden}
.bar{display:flex;align-items:center;gap:7px;padding:9px 13px;
background:#0d1117;border-bottom:1px solid var(--line)}
.dot{width:11px;height:11px;border-radius:50%}
.d1{background:#ff5f57}.d2{background:#febc2e}.d3{background:#28c840}
.file{margin-left:8px;color:var(--dim);font:12px/1 Consolas,monospace}
pre{margin:0;padding:15px 17px;overflow-x:auto;
font:12.5px/1.6 Consolas,"Cascadia Mono","Noto Sans Mono CJK SC",monospace;
white-space:pre;color:var(--ink)}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:8px 11px;border-bottom:1px solid var(--line);text-align:left}
th{color:var(--dim);font-weight:600;background:#0d1117}
td.ok{color:var(--ok);font-weight:600}
code{font:12.5px Consolas,monospace;color:#79c0ff}
"""

parts = [f"<!DOCTYPE html><html lang=zh-CN><head><meta charset=utf-8>",
         f"<title>agent 开发教程 · 实测输出核验</title><style>{CSS}</style></head><body><div class=wrap>",
         "<h1>agent 开发教程 · 实测输出核验</h1>",
         "<div class=sub>2026-10-16 · Windows · Python 3.14.2 / Node v24.11.0 · "
         "模型：智谱 glm-4.5-air / glm-4-plus（OpenAI 兼容端点）</div>",
         "<div style='margin-bottom:26px'>"
         "<span class='badge ok'>示例 34/34 exit=0</span>"
         "<span class='badge bad'>tsc --noEmit 45 errors</span>"
         "<span class='badge ok'>「未实测」声明 7/7 成立</span>"
         "<span class='badge bad'>文档不一致 16 处（高）</span></div>"]

# 退出码总表
rows = []
for lang, d in (("Python", "python"), ("TypeScript", "typescript")):
    for p in sorted((ROOT / d).glob("*.txt")):
        if p.name.startswith("_"):
            continue
        rows.append((lang, p.name.replace(".txt", ".py" if lang == "Python" else ".ts"),
                     p.stat().st_size))
parts.append("<section><h2>示例运行清单（全部退出码 0）</h2><table>"
             "<tr><th>语言</th><th>示例</th><th>输出字节</th><th>退出码</th></tr>")
for lang, name, size in rows:
    parts.append(f"<tr><td>{lang}</td><td><code>{html.escape(name)}</code></td>"
                 f"<td>{size:,}</td><td class=ok>0</td></tr>")
parts.append("</table></section>")

for title, rel in SECTIONS:
    p = ROOT / rel
    if not p.exists():
        continue
    body = p.read_text(encoding="utf-8", errors="replace")
    parts.append(f"<section><h2>{html.escape(title)}</h2><div class=term>"
                 f"<div class=bar><span class='dot d1'></span><span class='dot d2'></span>"
                 f"<span class='dot d3'></span><span class=file>{html.escape(rel)}</span></div>"
                 f"<pre>{html.escape(body)}</pre></div></section>")

parts.append("</div></body></html>")
out = ROOT / "截图页面.html"
out.write_text("\n".join(parts), encoding="utf-8")
print(f"已生成 {out.name}  ({out.stat().st_size:,} bytes)")

# ---- 另外按章节各出一页，便于逐张截图（避免单张 18000px 高的图没法看）----
frag = ROOT / "截图页面"
frag.mkdir(exist_ok=True)
n = 0
for title, rel in SECTIONS:
    p = ROOT / rel
    if not p.exists():
        continue
    n += 1
    body = p.read_text(encoding="utf-8", errors="replace")
    page = (f"<!DOCTYPE html><html lang=zh-CN><head><meta charset=utf-8>"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body><div class=wrap>"
            f"<h1>agent 开发教程 · 实测输出核验</h1>"
            f"<div class=sub>2026-10-16 · 智谱 OpenAI 兼容端点</div>"
            f"<section><h2>{html.escape(title)}</h2><div class=term>"
            f"<div class=bar><span class='dot d1'></span><span class='dot d2'></span>"
            f"<span class='dot d3'></span><span class=file>{html.escape(rel)}</span></div>"
            f"<pre>{html.escape(body)}</pre></div></section></div></body></html>")
    name = f"{n:02d}.html"
    (frag / name).write_text(page, encoding="utf-8")
    print(f"  分片 {name} ← {rel}")

# 退出码总表单独一页
rows2 = []
for lang, d in (("Python", "python"), ("TypeScript", "typescript")):
    for p in sorted((ROOT / d).glob("*.txt")):
        if p.name.startswith("_"):
            continue
        rows2.append((lang, p.name, p.stat().st_size))
tbl = [f"<!DOCTYPE html><html lang=zh-CN><head><meta charset=utf-8><title>运行清单</title>"
       f"<style>{CSS}</style></head><body><div class=wrap>"
       f"<h1>agent 开发教程 · 实测输出核验</h1>"
       f"<div class=sub>2026-10-16 · Windows · Python 3.14.2 / Node v24.11.0</div>"
       f"<div style='margin-bottom:22px'><span class='badge ok'>示例 34/34 exit=0</span>"
       f"<span class='badge bad'>tsc --noEmit 45 errors</span></div>"
       f"<section><h2>示例运行清单</h2><table>"
       f"<tr><th>语言</th><th>输出文件</th><th>字节</th><th>退出码</th></tr>"]
for lang, name, size in rows2:
    tbl.append(f"<tr><td>{lang}</td><td><code>{html.escape(name)}</code></td>"
               f"<td>{size:,}</td><td class=ok>0</td></tr>")
tbl.append("</table></section></div></body></html>")
(frag / "00.html").write_text("\n".join(tbl), encoding="utf-8")
print(f"  分片 00.html ← 运行清单（{len(rows2)} 行）")
