#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建《Agent 开发教程》单文件精读版 HTML。

用法（仓库根目录下执行）：
    python docs/agent开发教程/_build_html.py

输入：
    docs/agent开发教程/ch01..ch14*.md   —— 14 章正文
    docs/agent开发教程/assets/NN_*.svg  —— 26 张机制图（内联，做 marker id 去重）
输出：
    docs/agent开发教程/agent-frameworks-deep-dive.html

约束：
    * 仅用 Python 标准库，无第三方依赖
    * 产物单文件自包含：无 CDN、无外部字体、无外部 JS/CSS
    * 幂等：重复运行结果完全一致
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT_HTML = os.path.join(HERE, "agent-frameworks-deep-dive.html")

# 章节顺序（与 README.md 的章节目录一致）
CHAPTERS = [
    "ch01_landscape.md",
    "ch02_create_agent.md",
    "ch03_middleware.md",
    "ch04_tools_and_rag.md",
    "ch05_context_engineering.md",
    "ch06_langgraph_state.md",
    "ch07_langgraph_persistence.md",
    "ch08_langgraph_control.md",
    "ch09_deepagents_overview.md",
    "ch10_deepagents_filesystem.md",
    "ch11_deepagents_delegation.md",
    "ch12_deepagents_context.md",
    "ch13_observability.md",
    "ch14_multiagent_and_migration.md",
]

LANG_LABEL = {
    "python": "Python",
    "typescript": "TypeScript",
    "bash": "Shell",
    "text": "文本 / 输出",
    "": "文本",
}


# --------------------------------------------------------------------------
# 基础工具
# --------------------------------------------------------------------------
def esc(s):
    """HTML 转义。& 必须最先处理。"""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def smart_join(lines):
    """把段落的多个物理行合成一段：CJK 相邻不补空格，ASCII 词相邻补一个空格。"""
    out = ""
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if not out:
            out = ln
            continue
        a, b = out[-1], ln[0]
        if a.isascii() and b.isascii() and (a.isalnum() or a in ".,;:)]}\"'") \
                and (b.isalnum() or b in "([{\"'"):
            out += " " + ln
        else:
            out += ln
    return out


# --------------------------------------------------------------------------
# 行内解析：`code`、**bold**、*em*、[text](url)
# --------------------------------------------------------------------------
_PLACEHOLDER = "\x00%d\x00"


def render_inline(text):
    store = []

    def stash(html):
        # 先展开已存在的占位符，避免「链接标签里含行内代码」这类嵌套残留
        for i, h in enumerate(store):
            html = html.replace(_PLACEHOLDER % i, h)
        store.append(html)
        return _PLACEHOLDER % (len(store) - 1)

    # 1) 行内代码先占位，避免其中的 * 与 < > 参与后续处理
    s = re.sub(r"`([^`]+)`", lambda m: stash("<code>" + esc(m.group(1)) + "</code>"), text)

    # 2) 整体转义
    s = esc(s)

    # 3) 链接
    def _link(m):
        label, url = m.group(1), m.group(2)
        return stash('<a href="' + esc(url) + '">' + label + "</a>")

    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, s)

    # 4) 粗体 -> 斜体
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)

    # 5) 还原占位
    for i, html in enumerate(store):
        s = s.replace(_PLACEHOLDER % i, html)
    return s


# --------------------------------------------------------------------------
# 表格
# --------------------------------------------------------------------------
def split_table_row(line):
    """按 | 切分，尊重 `code` 里的 | 与转义 \\|。"""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    cells, cur, in_code, i = [], "", False, 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
            cur += ch
            i += 1
            continue
        if ch == "|" and not in_code:
            cells.append(cur.strip())
            cur = ""
            i += 1
            continue
        cur += ch
        i += 1
    cells.append(cur.strip())
    return cells


def is_sep_row(line):
    s = line.strip()
    if not s.startswith("|"):
        return False
    body = s.strip("|")
    return bool(body) and re.fullmatch(r"[\s:|-]+", body) and "-" in body


def render_table(rows):
    head = split_table_row(rows[0])
    seps = split_table_row(rows[1]) if len(rows) > 1 else []
    aligns = []
    for c in seps:
        c = c.strip()
        if c.startswith(":") and c.endswith(":"):
            aligns.append("center")
        elif c.endswith(":"):
            aligns.append("right")
        else:
            aligns.append("")
    out = ['<div class="tw">', "<table>", "<thead><tr>"]
    for i, c in enumerate(head):
        style = ' style="text-align:%s"' % aligns[i] if i < len(aligns) and aligns[i] else ""
        out.append("<th%s>%s</th>" % (style, render_inline(c)))
    out.append("</tr></thead>")
    out.append("<tbody>")
    for row in rows[2:]:
        cells = split_table_row(row)
        out.append("<tr>")
        for i, c in enumerate(cells):
            style = ' style="text-align:%s"' % aligns[i] if i < len(aligns) and aligns[i] else ""
            out.append("<td%s>%s</td>" % (style, render_inline(c)))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


# --------------------------------------------------------------------------
# 列表
# --------------------------------------------------------------------------
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")


def render_list(items):
    """items: [{'indent':int,'ordered':bool,'text':str}]"""
    idx = 0

    def rec(min_indent):
        nonlocal idx
        tag = "ol" if items[idx]["ordered"] else "ul"
        out = ["<%s>" % tag]
        while idx < len(items) and items[idx]["indent"] >= min_indent:
            if items[idx]["indent"] > min_indent:
                break
            li = "<li>" + render_inline(items[idx]["text"])
            idx += 1
            if idx < len(items) and items[idx]["indent"] > min_indent:
                li += rec(items[idx]["indent"])
            li += "</li>"
            out.append(li)
        out.append("</%s>" % tag)
        return "".join(out)

    return rec(items[0]["indent"])


# --------------------------------------------------------------------------
# blockquote
# --------------------------------------------------------------------------
def render_quote(lines):
    paras = []
    for ln in lines:
        t = ln[1:].strip() if ln.startswith(">") else ln.strip()
        if t:
            paras.append(t)
    if not paras:
        return ""
    joined = " ".join(paras)
    has_zh = any(p.startswith("中译") for p in paras)
    is_warn = "⚠️" in joined

    body = []
    if has_zh:
        for p in paras:
            if p.startswith("中译"):
                body.append('<p><span class="zh">→ ' + render_inline(p[len("中译"):].lstrip("：: ")) + "</span></p>")
            else:
                body.append('<p class="en">' + render_inline(p) + "</p>")
        title = "英文原文 · 附中译"
        cls = "note zhbox"
    elif is_warn:
        for p in paras:
            body.append("<p>" + render_inline(p) + "</p>")
        title = "注意"
        cls = "warn"
    else:
        for p in paras:
            body.append("<p>" + render_inline(p) + "</p>")
        title = "版本锚点" if "版本锚点" in joined else "说明"
        cls = "note"
    return '<div class="%s"><span class="t">%s</span>%s</div>' % (cls, title, "".join(body))


# --------------------------------------------------------------------------
# 代码块
# --------------------------------------------------------------------------
def render_code(lang, code, extra_class="", label=None):
    lab = label if label is not None else LANG_LABEL.get(lang, lang or "文本")
    cls = ("cb " + extra_class).strip()
    return (
        '<div class="%s">'
        '<div class="hd"><span class="fn">%s</span>'
        '<button class="copy" type="button">复制</button></div>'
        "<pre><code>%s</code></pre>"
        "</div>" % (cls, esc(lab), esc(code))
    )


def render_code_tabs(py_code, ts_code, ts_notes):
    panes = [
        '<div class="pane active"><pre><code>%s</code></pre></div>' % esc(py_code),
        '<div class="pane">%s<pre><code>%s</code></pre></div>'
        % (
            "".join('<div class="pane-note">' + render_inline(n) + "</div>" for n in ts_notes),
            esc(ts_code),
        ),
    ]
    return (
        '<div class="cb tabs">'
        '<div class="hd"><span class="tabbar">'
        '<button class="tab active" type="button">Python</button>'
        '<button class="tab" type="button">TypeScript</button>'
        "</span>"
        '<button class="copy" type="button">复制</button></div>'
        + "".join(panes)
        + "</div>"
    )


# --------------------------------------------------------------------------
# SVG 内联 + marker id 去重
# --------------------------------------------------------------------------
def inline_svg(fig_no, path):
    with open(path, "r", encoding="utf-8") as f:
        svg = f.read().strip()
    ids = re.findall(r'\bid="([^"]+)"', svg)
    # 长 id 先替换，避免前缀重叠
    for old in sorted(set(ids), key=len, reverse=True):
        new = "f%02d_%s" % (fig_no, old)
        svg = svg.replace('id="%s"' % old, 'id="%s"' % new)
        svg = svg.replace("url(#%s)" % old, "url(#%s)" % new)
        svg = svg.replace('href="#%s"' % old, 'href="#%s"' % new)
    return svg


# --------------------------------------------------------------------------
# Markdown -> blocks
# --------------------------------------------------------------------------
IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
CAP_RE = re.compile(r"^\*(图\s*\d+[^*]*)\*$")
H_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def parse_blocks(text):
    lines = text.split("\n")
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # 围栏代码块
        if stripped.startswith("```"):
            lang = stripped[3:].strip().lower()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # 跳过结束围栏
            blocks.append({"t": "code", "lang": lang, "code": "\n".join(buf).rstrip("\n")})
            continue

        # 标题
        m = H_RE.match(stripped)
        if m:
            blocks.append({"t": "h%d" % len(m.group(1)), "text": m.group(2).strip()})
            i += 1
            continue

        # 引用
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip())
                i += 1
            blocks.append({"t": "quote", "lines": buf})
            continue

        # 表格
        if stripped.startswith("|"):
            buf = []
            while i < n and lines[i].strip().startswith("|"):
                buf.append(lines[i].strip())
                i += 1
            blocks.append({"t": "table", "rows": buf})
            continue

        # 图片（+ 紧随的图注，允许中间空行）
        m = IMG_RE.match(stripped)
        if m:
            alt, src = m.group(1), m.group(2)
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            caption = None
            if j < n:
                cm = CAP_RE.match(lines[j].strip())
                if cm:
                    caption = cm.group(1).strip()
                    i = j
            blocks.append({"t": "fig", "src": src, "alt": alt, "caption": caption or alt})
            i += 1
            continue

        # 列表
        if LIST_RE.match(line):
            items = []
            base_indent = len(LIST_RE.match(line).group(1))
            while i < n:
                cur = lines[i]
                if not cur.strip():
                    # 允许空行后继续（松散列表）
                    j = i + 1
                    while j < n and not lines[j].strip():
                        j += 1
                    if j < n and LIST_RE.match(lines[j]) and len(LIST_RE.match(lines[j]).group(1)) >= base_indent:
                        i = j
                        continue
                    break
                lm = LIST_RE.match(cur)
                if lm:
                    indent = len(lm.group(1))
                    if indent < base_indent:
                        break
                    ordered = lm.group(2)[0].isdigit()
                    items.append({"indent": indent, "ordered": ordered, "text": lm.group(3).strip()})
                    i += 1
                    continue
                if cur[:1] in (" ", "\t") and items:
                    items[-1]["text"] += " " + cur.strip()
                    i += 1
                    continue
                break
            if items:
                blocks.append({"t": "list", "items": items})
            continue

        # 普通段落
        buf = []
        while i < n:
            cur = lines[i]
            if not cur.strip():
                break
            s2 = cur.strip()
            if s2.startswith(("```", ">", "|", "#")):
                break
            if LIST_RE.match(cur):
                break
            if IMG_RE.match(s2) or CAP_RE.match(s2):
                break
            buf.append(cur)
            i += 1
        if buf:
            blocks.append({"t": "p", "text": smart_join(buf)})
    return blocks


def pair_code_blocks(blocks):
    """把 python 代码块与其后的 typescript 代码块合成 tab 组。"""
    out = []
    i, n = 0, len(blocks)
    while i < n:
        b = blocks[i]
        if b["t"] == "code" and b["lang"] == "python":
            j = i + 1
            between = []
            while j < n and blocks[j]["t"] == "p":
                between.append(blocks[j]["text"])
                j += 1
            if j < n and blocks[j]["t"] == "code" and blocks[j]["lang"] == "typescript":
                # 前导段落若是「Python 侧：」这类纯标签，去掉标签词
                if out and out[-1]["t"] == "p":
                    txt = re.sub(r"\s*(Python|TypeScript)\s*侧：\s*$", "", out[-1]["text"]).strip()
                    if txt:
                        out[-1]["text"] = txt
                    else:
                        out.pop()
                notes = []
                for t in between:
                    t = re.sub(r"\s*(Python|TypeScript)\s*侧：\s*$", "", t).strip()
                    if t:
                        notes.append(t)
                out.append({"t": "codetabs", "py": b["code"], "ts": blocks[j]["code"], "notes": notes})
                i = j + 1
                continue
        out.append(b)
        i += 1
    return out


# --------------------------------------------------------------------------
# blocks -> HTML
# --------------------------------------------------------------------------
def render_blocks(blocks, chapter_no, anchors):
    """anchors: 收集 nav 用的 (id, 文本, level)。"""
    html = []
    h2k = 0
    for b in blocks:
        t = b["t"]
        if t == "h1":
            title = b["text"]
            m = re.match(r"^第\s*(\d+)\s*章\s*(.*)$", title)
            num, rest = (m.group(1), m.group(2)) if m else (str(chapter_no), title)
            html.append('<h2 class="chap" id="ch%s"><span class="num">%s</span>%s</h2>' % (chapter_no, num, render_inline(rest)))
        elif t == "h2":
            h2k += 1
            aid = "ch%s-s%d" % (chapter_no, h2k)
            anchors.append((aid, b["text"], 2))
            html.append('<h3 id="%s">%s</h3>' % (aid, render_inline(b["text"])))
        elif t == "h3":
            html.append("<h4>%s</h4>" % render_inline(b["text"]))
        elif t == "h4":
            html.append("<h5>%s</h5>" % render_inline(b["text"]))
        elif t == "p":
            html.append("<p>%s</p>" % render_inline(b["text"]))
        elif t == "quote":
            html.append(render_quote(b["lines"]))
        elif t == "table":
            html.append(render_table(b["rows"]))
        elif t == "list":
            html.append(render_list(b["items"]))
        elif t == "code":
            html.append(render_code(b["lang"], b["code"]))
        elif t == "codetabs":
            html.append(render_code_tabs(b["py"], b["ts"], b["notes"]))
        elif t == "fig":
            m = re.match(r"assets/(\d+)_", b["src"])
            if not m:
                continue
            fig_no = int(m.group(1))
            svg_path = os.path.join(ASSETS, os.path.basename(b["src"]).rsplit(".", 1)[0] + ".svg")
            if not os.path.exists(svg_path):
                raise SystemExit("缺少 SVG：%s" % svg_path)
            svg = inline_svg(fig_no, svg_path)
            cap = b["caption"]
            cm = re.match(r"^(图\s*\d+)(.*)$", cap)
            cap_html = ("<b>%s</b>%s" % (cm.group(1), render_inline(cm.group(2)))) if cm else render_inline(cap)
            html.append('<figure id="fig%d">%s<figcaption>%s</figcaption></figure>' % (fig_no, svg, cap_html))
    return "\n".join(x for x in html if x)


# --------------------------------------------------------------------------
# 页面模板
# --------------------------------------------------------------------------
CSS = """
:root{
  --bg:#0b0f14; --bg-soft:#111721; --panel:#151c26; --panel-2:#1a222e;
  --border:#232d3b; --border-soft:#1c2532;
  --text:#dfe6ee; --dim:#93a1b1; --faint:#6b7a8d;
  --blue:#4dabf7; --teal:#2dd4a7; --amber:#e8a34b; --purple:#b98ce8; --red:#f0655f; --pink:#e879a8;
  --code-bg:#0e141c;
  --nav-w:288px; --maxw:840px;
  --mono:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Noto Sans SC","Segoe UI",sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:24px}
body{
  margin:0;background:var(--bg);color:var(--text);
  font-family:var(--sans);font-size:16.5px;line-height:1.85;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
}
::selection{background:rgba(77,171,247,.28)}

/* ---------- 布局 ---------- */
.wrap{display:flex;align-items:flex-start;max-width:1400px;margin:0 auto}
nav.toc{
  position:sticky;top:0;flex:0 0 var(--nav-w);width:var(--nav-w);
  height:100vh;overflow-y:auto;padding:28px 14px 60px 26px;
  border-right:1px solid var(--border-soft);font-size:13.5px;line-height:1.6;
}
nav.toc::-webkit-scrollbar{width:6px}
nav.toc::-webkit-scrollbar-thumb{background:#2a3644;border-radius:3px}
nav.toc .brand{font-size:12px;letter-spacing:.14em;color:var(--faint);text-transform:uppercase;margin-bottom:18px}
nav.toc a{display:block;color:var(--dim);text-decoration:none;padding:4.5px 10px;border-radius:6px;border-left:2px solid transparent;transition:.16s}
nav.toc a:hover{color:var(--text);background:var(--panel)}
nav.toc a.lv1{font-weight:600;color:#b9c6d4;margin-top:9px}
nav.toc a.lv2{padding-left:22px;font-size:12.5px;padding-top:3px;padding-bottom:3px}
nav.toc a.active{color:var(--blue);background:rgba(77,171,247,.09);border-left-color:var(--blue)}
main{flex:1 1 auto;min-width:0;padding:0 46px 120px}
article{max-width:var(--maxw);margin:0 auto}

/* ---------- 标题与文本 ---------- */
header.hero{padding:76px 0 44px;border-bottom:1px solid var(--border-soft);margin-bottom:14px}
header.hero .eyebrow{font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--blue);font-weight:600;margin-bottom:16px}
header.hero h1{font-size:38px;line-height:1.3;margin:0 0 18px;letter-spacing:-.5px;font-weight:700}
header.hero .sub{font-size:17px;color:var(--dim);margin:0 0 26px;line-height:1.75}
header.hero .meta{display:flex;flex-wrap:wrap;gap:10px}
header.hero .meta span{font-size:12.5px;color:var(--faint);background:var(--panel);border:1px solid var(--border-soft);padding:4px 11px;border-radius:20px}

h2{font-size:27px;margin:64px 0 18px;padding-top:14px;line-height:1.4;font-weight:700;letter-spacing:-.2px}
h2.chap{border-top:1px solid var(--border-soft);margin-top:78px;padding-top:40px}
h2 .num{display:inline-block;font-size:15px;color:var(--blue);background:rgba(77,171,247,.1);border:1px solid rgba(77,171,247,.25);border-radius:6px;padding:1px 9px;margin-right:12px;vertical-align:3px;font-weight:600;font-family:var(--mono)}
h3{font-size:20px;margin:44px 0 12px;font-weight:650;color:#eaf1f8;line-height:1.5}
h4{font-size:16.5px;margin:28px 0 8px;font-weight:650;color:#cfdae6}
h5{font-size:15.5px;margin:22px 0 6px;font-weight:650;color:#c3d0dd}
p{margin:0 0 17px}
a{color:var(--blue);text-decoration:none;border-bottom:1px solid rgba(77,171,247,.32)}
a:hover{border-bottom-color:var(--blue)}
strong{color:#fff;font-weight:650}
em{color:var(--amber);font-style:normal;font-weight:600}
code{font-family:var(--mono);font-size:.875em;background:var(--panel-2);border:1px solid var(--border-soft);padding:1.5px 6px;border-radius:5px;color:#9fd0f5}
ul,ol{margin:0 0 18px;padding-left:24px}
li{margin:7px 0}
li>ul,li>ol{margin:6px 0}
hr{border:0;border-top:1px solid var(--border-soft);margin:52px 0}

/* ---------- 提示块 ---------- */
.note,.warn,.key{
  margin:24px 0;padding:15px 20px;border-radius:9px;font-size:15.5px;
  border:1px solid var(--border);background:var(--panel);
}
.note{border-left:3px solid var(--blue)}
.warn{border-left:3px solid var(--amber);background:rgba(232,163,75,.05)}
.key{border-left:3px solid var(--purple);background:rgba(185,140,232,.05)}
.note .t,.warn .t,.key .t{display:block;font-size:12.5px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;margin-bottom:7px}
.note .t{color:var(--blue)} .warn .t{color:var(--amber)} .key .t{color:var(--purple)}
.note p:last-child,.warn p:last-child,.key p:last-child{margin-bottom:0}
.zhbox{border-left-color:var(--teal);background:rgba(45,212,167,.045)}
.zhbox .t{color:var(--teal)}
.zhbox p.en{color:#c9d6e2;font-family:var(--mono);font-size:14px;line-height:1.7}
.zh{color:#d8c9a6;font-family:var(--sans);font-style:normal}

/* ---------- 表格 ---------- */
.tw{overflow-x:auto;margin:24px 0;border:1px solid var(--border);border-radius:10px}
table{width:100%;border-collapse:collapse;font-size:14.5px}
th,td{padding:11px 15px;text-align:left;border-bottom:1px solid var(--border-soft);vertical-align:top;line-height:1.65}
th{background:var(--panel-2);font-weight:650;color:#cbd8e6;font-size:13.5px;letter-spacing:.02em}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:rgba(255,255,255,.017)}
td code,th code{font-size:12.5px}

/* ---------- 代码 ---------- */
.cb{margin:24px 0;border:1px solid var(--border);border-radius:10px;overflow:hidden;background:var(--code-bg)}
.cb .hd{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 14px;background:var(--panel-2);border-bottom:1px solid var(--border-soft)}
.cb .hd .fn{font-family:var(--mono);font-size:12.5px;color:var(--dim)}
.cb .hd button{background:transparent;border:1px solid var(--border);color:var(--faint);font-size:11.5px;padding:3px 10px;border-radius:5px;cursor:pointer;font-family:var(--sans);transition:.15s}
.cb .hd button:hover{color:var(--blue);border-color:rgba(77,171,247,.45)}
.cb .tabbar{display:flex;gap:6px}
.cb .tab{color:var(--faint)}
.cb .tab.active{color:var(--blue);border-color:rgba(77,171,247,.5);background:rgba(77,171,247,.08)}
.cb pre{margin:0;padding:16px 18px;overflow-x:auto;font-family:var(--mono);font-size:13px;line-height:1.72;color:#c9d6e2}
.cb pre code{background:none;border:0;padding:0;color:inherit;font-size:inherit}
.cb pre::-webkit-scrollbar{height:8px}
.cb pre::-webkit-scrollbar-thumb{background:#2a3644;border-radius:4px}
.cb .pane{display:none}
.cb .pane.active{display:block}
.cb .pane-note{padding:12px 18px 0;font-size:14px;color:var(--dim);border-bottom:1px dashed var(--border-soft);padding-bottom:10px;margin-bottom:2px}

/* ---------- SVG 图 ---------- */
figure{margin:30px 0;padding:22px 18px 14px;background:var(--bg-soft);border:1px solid var(--border-soft);border-radius:12px}
figure svg{display:block;width:100%;height:auto}
figcaption{margin-top:14px;font-size:13.5px;color:var(--faint);text-align:center;line-height:1.65}
figcaption b{color:var(--dim);font-weight:600}

/* ---------- 其它 ---------- */
.ok{color:var(--teal);font-weight:600}
.no{color:var(--red);font-weight:600}

@media(max-width:1080px){
  nav.toc{display:none}
  main{padding:0 22px 90px}
  header.hero h1{font-size:30px}
  h2{font-size:23px}
  body{font-size:16px}
}
"""

JS = """
// ---- 目录滚动高亮 ----
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('nav.toc a'));
  var targets = links.map(function(a){ return document.querySelector(a.getAttribute('href')); });
  function onScroll(){
    var y = window.scrollY + 120, idx = 0;
    for (var i = 0; i < targets.length; i++){
      if (targets[i] && targets[i].offsetTop <= y) idx = i;
    }
    links.forEach(function(a, i){ a.classList.toggle('active', i === idx); });
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();
})();

// ---- 代码复制 + 语言切换 ----
document.addEventListener('click', function(e){
  var tab = e.target.closest('.cb .tab');
  if (tab){
    var cb = tab.closest('.cb');
    var tabs = Array.prototype.slice.call(cb.querySelectorAll('.tab'));
    var panes = Array.prototype.slice.call(cb.querySelectorAll('.pane'));
    var k = tabs.indexOf(tab);
    tabs.forEach(function(b, i){ b.classList.toggle('active', i === k); });
    panes.forEach(function(p, i){ p.classList.toggle('active', i === k); });
    return;
  }
  var btn = e.target.closest('.cb .hd .copy');
  if (!btn) return;
  var box = btn.closest('.cb');
  var pane = box.querySelector('.pane.active') || box;
  var pre = pane.querySelector('pre');
  if (!pre) return;
  var text = pre.innerText;
  function done(){
    var old = btn.textContent; btn.textContent = '已复制';
    setTimeout(function(){ btn.textContent = old; }, 1400);
  }
  if (navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(done, done);
  } else {
    var ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (err) {}
    document.body.removeChild(ta); done();
  }
});
"""


def build():
    chapters = []
    for name in CHAPTERS:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            raise SystemExit("缺少章节文件：%s" % path)
        with open(path, "r", encoding="utf-8") as f:
            chapters.append((name, f.read()))

    nav = []
    body = []
    for idx, (name, text) in enumerate(chapters, 1):
        blocks = pair_code_blocks(parse_blocks(text))
        # 章标题
        title = ""
        for b in blocks:
            if b["t"] == "h1":
                title = b["text"]
                break
        m = re.match(r"^第\s*(\d+)\s*章\s*(.*)$", title)
        nav_title = m.group(2) if m else title
        anchors = []
        html = render_blocks(blocks, idx, anchors)
        nav.append((idx, nav_title, anchors))
        body.append('<section class="chapter" id="chap%d">\n%s\n</section>' % (idx, html))

    # 目录
    toc = ['<div class="brand">Agent 开发教程</div>']
    for idx, nav_title, anchors in nav:
        toc.append('<a class="lv1" href="#ch%d">%d · %s</a>' % (idx, idx, esc(nav_title)))
        for aid, atext, _lv in anchors:
            toc.append('<a class="lv2" href="#%s">%s</a>' % (aid, esc(atext)))

    hero = """
<header class="hero">
  <div class="eyebrow">LangChain · LangGraph · Deep Agents · 深度精读</div>
  <h1>Agent 开发教程：从构建块、运行时<br>到成品 harness</h1>
  <p class="sub">网上讲 LangChain / LangGraph / Deep Agents 的教程很多，但大多把三个框架混着讲，读完还是不知道「遇到一个需求该翻谁的文档」。这篇按「构建块 → 运行时 → 成品 harness」三层递进，逐章讲清边界、机制、双语言写法与实测坑点，配 26 张自绘机制图与 Python / TypeScript 双语言可切换代码。</p>
  <div class="meta">
    <span>14 章 · 精读版</span>
    <span>26 张自绘机制图</span>
    <span>Python / TypeScript 双语言代码</span>
    <span>全部内容内联 · 可离线打开</span>
  </div>
</header>
"""

    html = (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>Agent 开发教程精读版：LangChain / LangGraph / Deep Agents</title>\n"
        "<style>" + CSS + "</style>\n</head>\n<body>\n"
        '<div class="wrap">\n\n<nav class="toc">\n  ' + "\n  ".join(toc) + "\n</nav>\n\n"
        "<main>\n<article>\n" + hero + "\n" + "\n\n".join(body) + "\n</article>\n</main>\n</div>\n\n"
        "<script>" + JS + "</script>\n</body>\n</html>\n"
    )
    with open(OUT_HTML, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("已生成：%s" % OUT_HTML)
    print("行数：%d  字节：%d" % (html.count("\n") + 1, len(html.encode("utf-8"))))


if __name__ == "__main__":
    build()
