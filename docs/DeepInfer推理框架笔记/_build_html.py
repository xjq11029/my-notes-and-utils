#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建《DeepInfer 推理框架笔记》单文件精读版 HTML。

用法（仓库根目录下执行）：
    python docs/DeepInfer推理框架笔记/_build_html.py

输入  docs/DeepInfer推理框架笔记/ch01..ch11*.md
输出  docs/DeepInfer推理框架笔记/deepinfer-inference-framework-deep-dive.html

约束：
    * 仅用 Python 标准库，无第三方依赖
    * 产物单文件自包含：无 CDN、无外部字体、无外部 JS/CSS
    * Mermaid 只支持本目录使用的 `graph TD` 子集，静态渲染为内联 SVG
    * 幂等：重复运行结果完全一致
"""

from __future__ import annotations

import os
import re
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "deepinfer-inference-framework-deep-dive.html")

CHAPTERS = [
    "ch01_positioning.md",
    "ch02_startup_path.md",
    "ch03_scheduler.md",
    "ch04_kv_cache.md",
    "ch05_attention.md",
    "ch06_moe_eplb.md",
    "ch07_speculative_decoding.md",
    "ch08_zos_batch_invariant.md",
    "ch09_sampling_structured_output.md",
    "ch10_multimodal_parallel.md",
    "ch11_production_eval.md",
]

LANG_LABEL = {
    "python": "Python",
    "bash": "Shell",
    "text": "文本 / 输出",
    "json": "JSON",
    "jsonc": "JSONC",
    "": "文本",
}

H1_RE = re.compile(r"^第\s*(\d+)\s*章\s*(.*)$")
H_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
IMG_RE = re.compile(r"^!\[(.*?)\]\(([^)]+)\)\s*$")
CAP_RE = re.compile(r"^\*(图\s*(?:\d+)[^*]*)\*$")


# --------------------------------------------------------------------------
# 基础工具
# --------------------------------------------------------------------------
def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def smart_join(lines: list[str]) -> str:
    out = ""
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if not out:
            out = ln
            continue
        a, b = out[-1], ln[0]
        if a.isascii() and b.isascii() and (a.isalnum() or a in ".,;:)]}\"'") and (b.isalnum() or b in "([{\"'"):
            out += " " + ln
        else:
            out += ln
    return out


_PLACEHOLDER = "\x00%d\x00"


def render_inline(text: str) -> str:
    store: list[str] = []

    def stash(html: str) -> str:
        for i, h in enumerate(store):
            html = html.replace(_PLACEHOLDER % i, h)
        store.append(html)
        return _PLACEHOLDER % (len(store) - 1)

    s = re.sub(r"`([^`]+)`", lambda m: stash("<code>" + esc(m.group(1)) + "</code>"), text)
    s = esc(s)

    def _link(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        return stash('<a href="' + esc(url) + '">' + label + "</a>")

    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)

    for i, html in enumerate(store):
        s = s.replace(_PLACEHOLDER % i, html)
    s = re.sub(r"（来源：(官方|一手|三方)([^）]*)）", r'<span class="src-tag">来源：\1\2</span>', s)
    return s


# --------------------------------------------------------------------------
# 表格
# --------------------------------------------------------------------------
def split_table_row(line: str) -> list[str]:
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


def is_sep_row(line: str) -> bool:
    s = line.strip()
    if not s.startswith("|"):
        return False
    body = s.strip("|")
    return bool(body) and re.fullmatch(r"[\s:|-]+", body) is not None and "-" in body


def render_table(rows: list[str]) -> str:
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
    out.append("</tr></thead><tbody>")
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
# 列表 / 引用 / 代码
# --------------------------------------------------------------------------
def render_list(items: list[dict]) -> str:
    idx = 0

    def rec(min_indent: int) -> str:
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


def render_quote(lines: list[str]) -> str:
    paras = []
    for ln in lines:
        t = ln[1:].strip() if ln.startswith(">") else ln.strip()
        if t:
            paras.append(t)
    if not paras:
        return ""
    joined = " ".join(paras)
    is_warn = "⚠️" in joined
    body = ["<p>" + render_inline(p) + "</p>" for p in paras]
    cls = "warn" if is_warn else "note"
    title = "注意" if is_warn else "说明"
    return '<div class="%s"><span class="t">%s</span>%s</div>' % (cls, title, "".join(body))


def render_code(lang: str, code: str) -> str:
    lab = LANG_LABEL.get(lang, lang or "文本")
    return (
        '<div class="cb"><div class="hd"><span class="fn">%s</span>'
        '<button class="copy" type="button">复制</button></div>'
        "<pre><code>%s</code></pre></div>" % (esc(lab), esc(code))
    )


# --------------------------------------------------------------------------
# Mermaid graph TD -> inline SVG（仅覆盖本目录使用的子集）
# --------------------------------------------------------------------------
NODE_RE = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*(\[|\{)\s*"(.*?)"\s*(\]|\})')
EDGE_RE = re.compile(
    r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(-\.->|-->)\s*(?:\|"?([^"|]*)"?\|\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*$'
)


def _text_width(s: str) -> int:
    return sum(14 if ord(ch) > 127 else 8 for ch in s)


def _wrap_text(s: str, max_w: int = 270) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9_./:+×=<>-]+|.", s)
    lines, cur, w = [], "", 0
    closers = "）)]}，。、；：”’"
    for tok in tokens:
        tw = _text_width(tok)
        if tok and tok[0] in closers:
            if cur:
                cur += tok
                w += tw
                continue
            if lines:
                lines[-1] += tok
                continue
        if tw > max_w:
            if cur:
                lines.append(cur)
                cur, w = "", 0
            for ch in tok:
                cw = _text_width(ch)
                if w + cw > max_w and cur:
                    lines.append(cur)
                    cur, w = "", 0
                cur += ch
                w += cw
            continue
        if w + tw > max_w and cur:
            lines.append(cur)
            cur, w = "", 0
        cur += tok
        w += tw
    if cur:
        lines.append(cur)
    return lines or [""]


def _label_lines(label: str) -> list[str]:
    parts = re.split(r"<br\s*/?>", label)
    lines: list[str] = []
    for part in parts:
        lines.extend(_wrap_text(part.strip(), 270))
    return [x for x in lines if x] or [""]


def parse_mermaid(code: str):
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def note(nid: str, label: str | None = None, shape: str = "box") -> None:
        nid = nid.strip()
        if not nid:
            return
        if nid not in nodes:
            nodes[nid] = {"label": label if label is not None else nid, "shape": shape}
        elif label is not None:
            nodes[nid]["label"] = label
            nodes[nid]["shape"] = shape

    for raw in code.splitlines():
        line = raw.strip()
        if not line or line.startswith("graph ") or line.startswith("flowchart ") or line.startswith("%%"):
            continue
        for stmt in line.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue

            def repl(m: re.Match) -> str:
                nid, open_ch, label, close_ch = m.group(1), m.group(2), m.group(3), m.group(4)
                if open_ch == "{" and close_ch != "}":
                    shape = "box"
                else:
                    shape = "decision" if open_ch == "{" else "box"
                note(nid, label, shape)
                return nid

            rest = NODE_RE.sub(repl, stmt)
            m = EDGE_RE.match(rest)
            if not m:
                # 可能是单独的节点定义行；NODE_RE 已把节点收进 nodes
                for nid in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", rest):
                    note(nid)
                continue
            src, arrow, label, dst = m.group(1), m.group(2), m.group(3), m.group(4)
            note(src)
            note(dst)
            edges.append({"src": src, "dst": dst, "label": (label or "").strip(), "dashed": arrow == "-.->"})
    return nodes, edges


def render_mermaid(code: str, fig_no: int, chapter_no: int) -> str:
    nodes, edges = parse_mermaid(code)
    if not nodes:
        return ""
    order = list(nodes.keys())
    out_map: dict[str, list[str]] = {n: [] for n in nodes}
    for e in edges:
        out_map[e["src"]].append(e["dst"])

    # DFS 找出回边；回边只用于绘制，不参与层级计算
    color: dict[str, int] = {}
    back: set[tuple[str, str]] = set()

    def dfs(u: str) -> None:
        color[u] = 1
        for v in out_map.get(u, []):
            if color.get(v) == 1:
                back.add((u, v))
            elif color.get(v) is None:
                dfs(v)
        color[u] = 2

    for n in order:
        if color.get(n) is None:
            dfs(n)

    # 在去掉回边的 DAG 上做拓扑排序 + 最长路径分层
    indeg = {n: 0 for n in nodes}
    for e in edges:
        if (e["src"], e["dst"]) not in back:
            indeg[e["dst"]] += 1
    q = deque([n for n in order if indeg[n] == 0])
    topo: list[str] = []
    while q:
        u = q.popleft()
        topo.append(u)
        for e in edges:
            if e["src"] == u and (e["src"], e["dst"]) not in back:
                indeg[e["dst"]] -= 1
                if indeg[e["dst"]] == 0:
                    q.append(e["dst"])
    for n in order:
        if n not in topo:
            topo.append(n)
    level = {n: 0 for n in nodes}
    for u in topo:
        for e in edges:
            if e["src"] == u and (e["src"], e["dst"]) not in back:
                level[e["dst"]] = max(level[e["dst"]], level[u] + 1)

    # 节点尺寸
    metrics: dict[str, dict] = {}
    for n in order:
        lines = _label_lines(nodes[n]["label"])
        w = min(340, max(120, max(_text_width(x) for x in lines) + 30))
        h = max(52, len(lines) * 20 + 24)
        metrics[n] = {"lines": lines, "w": w, "h": h}
    levels = sorted({level[n] for n in nodes})
    level_h = {lv: max(metrics[n]["h"] for n in nodes if level[n] == lv) for lv in levels}
    level_w = {
        lv: sum(metrics[n]["w"] for n in nodes if level[n] == lv)
        + 42 * (sum(1 for n in nodes if level[n] == lv) - 1)
        for lv in levels
    }
    margin = 26
    left_lane = 58
    right_lane = 58
    canvas_w = max(560, max(level_w.values()) + 2 * margin + left_lane + right_lane)
    level_gap = 62
    level_top: dict[int, int] = {}
    y = margin
    for lv in levels:
        level_top[lv] = y
        y += level_h[lv] + level_gap
    canvas_h = y - level_gap + margin

    # 节点坐标
    for lv in levels:
        row = [n for n in nodes if level[n] == lv]
        x = left_lane + (canvas_w - left_lane - right_lane - level_w[lv]) / 2
        for n in row:
            box = metrics[n]
            box["x"] = x
            box["y"] = level_top[lv] + (level_h[lv] - box["h"]) / 2
            box["cx"] = x + box["w"] / 2
            box["cy"] = box["y"] + box["h"] / 2
            x += box["w"] + 42

    defs = (
        '<defs><marker id="d%02d_arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" '
        'orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#5b7085"/></marker></defs>' % fig_no
    )
    svg_parts = [
        '<svg viewBox="0 0 %d %d" role="img" aria-label="第 %d 章机制图 %d">' % (canvas_w, canvas_h, chapter_no, fig_no),
        defs,
        '<rect x="0" y="0" width="%d" height="%d" rx="10" fill="#0f151d"/>' % (canvas_w, canvas_h),
    ]

    edge_labels = []
    side_idx = {"left": 0, "right": 0}
    for e in edges:
        s, t = metrics[e["src"]], metrics[e["dst"]]
        sx, sy = s["cx"], s["y"] + s["h"]
        tx, ty = t["cx"], t["y"]
        is_back = (e["src"], e["dst"]) in back
        s_level, t_level = level[e["src"]], level[e["dst"]]
        if (not is_back) and t_level == s_level + 1:
            mid = (sy + ty) / 2
            if abs(sx - tx) < 1:
                path = "M %.1f %.1f L %.1f %.1f" % (sx, sy, tx, ty)
                lx, ly, anchor = sx + 10, mid, "start"
            else:
                path = "M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (sx, sy, sx, mid, tx, mid, tx, ty)
                lx, ly, anchor = (sx + tx) / 2, mid, "middle"
        else:
            if is_back:
                side = "left" if s["cx"] < canvas_w / 2 else "right"
            else:
                side = "left" if tx < sx - 1 else "right"
            idx = side_idx[side]
            side_idx[side] += 1
            if side == "left":
                lane = left_lane - 20 - (idx % 3) * 8
                lx, anchor = lane + 8, "start"
            else:
                lane = canvas_w - right_lane + 20 + (idx % 3) * 8
                lx, anchor = lane - 8, "end"
            m1, m2 = sy + 16, ty - 16
            path = "M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (
                sx, sy, sx, m1, lane, m1, lane, m2, tx, m2, tx, ty
            )
            ly = m1 - 4
        dash = ' stroke-dasharray="5 4"' if e["dashed"] or is_back else ""
        svg_parts.append(
            '<path d="%s" fill="none" stroke="#5b7085" stroke-width="1.35"%s marker-end="url(#d%02d_arrow)"/>'
            % (path, dash, fig_no)
        )
        if e["label"]:
            edge_labels.append((e["label"], lx, ly, anchor))

    # 边标签（带底色，避免压线；左右车道标签贴车道放置，避免漂在中间）
    for label, lx, ly, anchor in edge_labels:
        lines = _wrap_text(label, 150)
        lw = min(220, max(_text_width(x) for x in lines) + 12)
        lh = len(lines) * 15 + 6
        if anchor == "middle":
            lx = max(left_lane + lw / 2 + 4, min(canvas_w - right_lane - lw / 2 - 4, lx))
            rect_x = lx - lw / 2
        elif anchor == "start":
            lx = min(lx, canvas_w - right_lane - lw - 4)
            rect_x = lx - 2
        else:
            lx = max(lx, left_lane + lw + 4)
            rect_x = lx - lw + 2
        svg_parts.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="#0f151d" opacity="0.92"/>'
            % (rect_x, ly - lh / 2 - 2, lw, lh)
        )
        first_y = ly - (len(lines) - 1) * 7.5 + 4
        for i, ln in enumerate(lines):
            svg_parts.append(
                '<text x="%.1f" y="%.1f" text-anchor="%s" font-size="11.5" fill="#93a1b1" font-family="sans-serif">%s</text>'
                % (lx, first_y + i * 15, anchor, esc(ln))
            )

    # 节点
    for n in order:
        box = metrics[n]
        shape = nodes[n]["shape"]
        outdeg = len(out_map.get(n, []))
        if shape == "decision":
            fill, stroke, tcolor = "#241f16", "#d09a4a", "#f0c27a"
        elif outdeg == 0:
            fill, stroke, tcolor = "#14261f", "#2f6d5a", "#bfe8d8"
        else:
            fill, stroke, tcolor = "#18222e", "#3a4c62", "#dfe6ee"
        svg_parts.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="9" fill="%s" stroke="%s" stroke-width="1.25"/>'
            % (box["x"], box["y"], box["w"], box["h"], fill, stroke)
        )
        lines = box["lines"]
        first_y = box["cy"] - (len(lines) - 1) * 10 + 4
        for i, ln in enumerate(lines):
            svg_parts.append(
                '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="13" fill="%s" font-family="sans-serif">%s</text>'
                % (box["cx"], first_y + i * 20, tcolor, esc(ln))
            )
    svg_parts.append("</svg>")
    caption = "图 %d · 第 %d 章机制图（Mermaid graph TD 静态简化渲染）" % (fig_no, chapter_no)
    return '<figure class="diagram" id="fig%d">%s<figcaption>%s</figcaption></figure>' % (
        fig_no,
        "".join(svg_parts),
        caption,
    )


# --------------------------------------------------------------------------
# Markdown -> blocks
# --------------------------------------------------------------------------
def parse_blocks(text: str) -> list[dict]:
    lines = text.split("\n")
    blocks: list[dict] = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            lang = stripped[3:].strip().lower()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            blocks.append({"t": "mermaid" if lang == "mermaid" else "code", "lang": lang, "code": "\n".join(buf).rstrip("\n")})
            continue

        if stripped == "---":
            blocks.append({"t": "hr"})
            i += 1
            continue

        m = H_RE.match(stripped)
        if m:
            blocks.append({"t": "h%d" % len(m.group(1)), "text": m.group(2).strip()})
            i += 1
            continue

        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip())
                i += 1
            blocks.append({"t": "quote", "lines": buf})
            continue

        if stripped.startswith("|"):
            buf = []
            while i < n and lines[i].strip().startswith("|"):
                buf.append(lines[i].strip())
                i += 1
            blocks.append({"t": "table", "rows": buf})
            continue

        m = IMG_RE.match(stripped)
        if m:
            blocks.append({"t": "p", "text": m.group(1) or m.group(2)})
            i += 1
            continue

        if LIST_RE.match(line):
            items = []
            base_indent = len(LIST_RE.match(line).group(1))
            while i < n:
                cur = lines[i]
                if not cur.strip():
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

        buf = []
        while i < n:
            cur = lines[i]
            if not cur.strip():
                break
            s2 = cur.strip()
            if s2.startswith(("```", ">", "|", "#")) or s2 == "---":
                break
            if LIST_RE.match(cur) or IMG_RE.match(s2):
                break
            buf.append(cur)
            i += 1
        if buf:
            blocks.append({"t": "p", "text": smart_join(buf)})
    return blocks


def render_blocks(blocks: list[dict], chapter_no: int, anchor_list: list[tuple[str, str]], fig_counter: list[int]) -> str:
    html: list[str] = []
    h2k = 0
    for b in blocks:
        t = b["t"]
        if t == "h1":
            title = b["text"]
            m = H1_RE.match(title)
            num, rest = (m.group(1), m.group(2)) if m else (str(chapter_no), title)
            html.append('<h2 class="chap" id="ch%d"><span class="num">%s</span>%s</h2>' % (chapter_no, num, render_inline(rest)))
        elif t == "h2":
            h2k += 1
            aid = "ch%d-s%d" % (chapter_no, h2k)
            anchor_list.append((aid, b["text"]))
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
        elif t == "mermaid":
            fig_counter[0] += 1
            html.append(render_mermaid(b["code"], fig_counter[0], chapter_no))
        elif t == "hr":
            html.append("<hr>")
    return "\n".join(x for x in html if x)


# --------------------------------------------------------------------------
# 页面模板
# --------------------------------------------------------------------------
CSS = """
:root{
  --bg:#0b0f14; --bg-soft:#111721; --panel:#151c26; --panel-2:#1a222e;
  --border:#232d3b; --border-soft:#1c2532;
  --text:#dfe6ee; --dim:#93a1b1; --faint:#6b7a8d;
  --blue:#4dabf7; --teal:#2dd4a7; --amber:#e8a34b; --purple:#b98ce8; --red:#f0655f;
  --code-bg:#0e141c;
  --nav-w:288px; --maxw:840px;
  --mono:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Noto Sans SC","Segoe UI",sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:24px}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);font-size:16.5px;line-height:1.85;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
::selection{background:rgba(45,212,167,.26)}
.wrap{display:flex;align-items:flex-start;max-width:1400px;margin:0 auto}
nav.toc{position:sticky;top:0;flex:0 0 var(--nav-w);width:var(--nav-w);height:100vh;overflow-y:auto;padding:28px 14px 60px 26px;border-right:1px solid var(--border-soft);font-size:13.5px;line-height:1.6}
nav.toc::-webkit-scrollbar{width:6px}
nav.toc::-webkit-scrollbar-thumb{background:#2a3644;border-radius:3px}
nav.toc .brand{font-size:12px;letter-spacing:.14em;color:var(--faint);text-transform:uppercase;margin-bottom:18px}
nav.toc a{display:block;color:var(--dim);text-decoration:none;padding:4.5px 10px;border-radius:6px;border-left:2px solid transparent;transition:.16s}
nav.toc a:hover{color:var(--text);background:var(--panel)}
nav.toc a.lv1{font-weight:600;color:#b9c6d4;margin-top:9px}
nav.toc a.lv2{padding-left:22px;font-size:12.5px;padding-top:3px;padding-bottom:3px}
nav.toc a.active{color:var(--teal);background:rgba(45,212,167,.09);border-left-color:var(--teal)}
main{flex:1 1 auto;min-width:0;padding:0 46px 120px}
article{max-width:var(--maxw);margin:0 auto}
header.hero{padding:76px 0 44px;border-bottom:1px solid var(--border-soft);margin-bottom:14px}
header.hero .eyebrow{font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--teal);font-weight:600;margin-bottom:16px}
header.hero h1{font-size:38px;line-height:1.3;margin:0 0 18px;letter-spacing:-.5px;font-weight:700}
header.hero .sub{font-size:17px;color:var(--dim);margin:0 0 26px;line-height:1.75}
header.hero .meta{display:flex;flex-wrap:wrap;gap:10px}
header.hero .meta span{font-size:12.5px;color:var(--faint);background:var(--panel);border:1px solid var(--border-soft);padding:4px 11px;border-radius:20px}
h2{font-size:27px;margin:64px 0 18px;padding-top:14px;line-height:1.4;font-weight:700;letter-spacing:-.2px}
h2.chap{border-top:1px solid var(--border-soft);margin-top:78px;padding-top:40px}
h2 .num{display:inline-block;font-size:15px;color:var(--teal);background:rgba(45,212,167,.1);border:1px solid rgba(45,212,167,.25);border-radius:6px;padding:1px 9px;margin-right:12px;vertical-align:3px;font-weight:600;font-family:var(--mono)}
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
.src-tag{display:inline-block;font-size:12px;color:var(--teal);background:rgba(45,212,167,.08);border:1px solid rgba(45,212,167,.22);border-radius:4px;padding:0 5px;margin:0 2px;white-space:nowrap}
.note,.warn{margin:24px 0;padding:15px 20px;border-radius:9px;font-size:15.5px;border:1px solid var(--border);background:var(--panel)}
.note{border-left:3px solid var(--blue)}
.warn{border-left:3px solid var(--amber);background:rgba(232,163,75,.05)}
.note .t,.warn .t{display:block;font-size:12.5px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;margin-bottom:7px}
.note .t{color:var(--blue)} .warn .t{color:var(--amber)}
.note p:last-child,.warn p:last-child{margin-bottom:0}
.tw{overflow-x:auto;margin:24px 0;border:1px solid var(--border);border-radius:10px}
table{width:100%;border-collapse:collapse;font-size:14.5px}
th,td{padding:11px 15px;text-align:left;border-bottom:1px solid var(--border-soft);vertical-align:top;line-height:1.65}
th{background:var(--panel-2);font-weight:650;color:#cbd8e6;font-size:13.5px;letter-spacing:.02em}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:rgba(255,255,255,.017)}
td code,th code{font-size:12.5px}
.cb{margin:24px 0;border:1px solid var(--border);border-radius:10px;overflow:hidden;background:var(--code-bg)}
.cb .hd{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 14px;background:var(--panel-2);border-bottom:1px solid var(--border-soft)}
.cb .hd .fn{font-family:var(--mono);font-size:12.5px;color:var(--dim)}
.cb .hd button{background:transparent;border:1px solid var(--border);color:var(--faint);font-size:11.5px;padding:3px 10px;border-radius:5px;cursor:pointer;font-family:var(--sans);transition:.15s}
.cb .hd button:hover{color:var(--teal);border-color:rgba(45,212,167,.45)}
.cb pre{margin:0;padding:16px 18px;overflow-x:auto;font-family:var(--mono);font-size:13px;line-height:1.72;color:#c9d6e2}
.cb pre code{background:none;border:0;padding:0;color:inherit;font-size:inherit}
.cb pre::-webkit-scrollbar{height:8px}
.cb pre::-webkit-scrollbar-thumb{background:#2a3644;border-radius:4px}
figure.diagram{margin:30px 0;padding:20px 14px 12px;background:var(--bg-soft);border:1px solid var(--border-soft);border-radius:12px}
figure.diagram svg{display:block;width:100%;height:auto}
figure.diagram figcaption{margin-top:12px;font-size:13px;color:var(--faint);text-align:center;line-height:1.65}
footer{margin-top:80px;padding-top:24px;border-top:1px solid var(--border-soft);font-size:13px;color:var(--faint);line-height:1.8}
footer a{color:var(--dim)}
.kicker{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);font-weight:700;margin:34px 0 -4px}
@media(max-width:1080px){nav.toc{display:none}main{padding:0 22px 90px}header.hero h1{font-size:30px}h2{font-size:23px}body{font-size:16px}}
"""

JS = """
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('nav.toc a'));
  var targets = links.map(function(a){ return document.querySelector(a.getAttribute('href')); });
  function onScroll(){
    var y = window.scrollY + 120, idx = 0;
    for (var i = 0; i < targets.length; i++){ if (targets[i] && targets[i].offsetTop <= y) idx = i; }
    links.forEach(function(a, i){ a.classList.toggle('active', i === idx); });
  }
  window.addEventListener('scroll', onScroll, {passive:true}); onScroll();
})();
document.addEventListener('click', function(e){
  var btn = e.target.closest('.cb .hd .copy'); if (!btn) return;
  var pre = btn.closest('.cb').querySelector('pre'); if (!pre) return;
  var text = pre.innerText;
  function done(){ var old = btn.textContent; btn.textContent = '已复制'; setTimeout(function(){ btn.textContent = old; }, 1400); }
  if (navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(text).then(done, done); }
  else { var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); } catch (err) {} document.body.removeChild(ta); done(); }
});
"""

HERO = """
<header class="hero">
  <div class="eyebrow">DeepSeek · DeepInfer · 源码精读</div>
  <h1>DeepInfer 推理框架：从调度、缓存<br>到注意力、MoE 与生产部署</h1>
  <p class="sub">DeepInfer 是 DeepSeek 开源的 V4.1-Flash 推理框架。这份精读版按一次请求的真实路径推进：C++ 调度器如何选批、KV 与 state cache 如何布局、MLA/压缩 KV/稀疏索引/SWA 如何拼接、MoE 专家如何跨卡搬运、DFlash 如何投机验证、ZOS 如何消除气泡，最后落到生产部署与评测。11 章正文全部由源码与官方 Q&amp;A 交叉核对，14 张 Mermaid 机制图静态渲染为内联 SVG。</p>
  <div class="meta">
    <span>11 章 · 精读版</span>
    <span>14 张静态内联 SVG</span>
    <span>源码快照 9bd9cf2</span>
    <span>全部内容内联 · 可离线打开</span>
  </div>
</header>
<div class="note"><span class="t">阅读提示</span><p>本 HTML 由同目录 <code>_build_html.py</code> 从 11 章 Markdown 生成，Mermaid 图由 <code>graph TD</code> 子集静态简化渲染为内联 SVG（布局与官方 Mermaid 不完全一致，以离线可读为目标）；不依赖 CDN、外部字体或外部 JS。笔记基于源码与官方 README / Q&amp;A，<strong>未在 SM100 / 昇腾 950 真机运行</strong>，涉及运行结果的表述均为源码推演或官方数据。</p></div>
"""

FOOTER = """
<footer>
  <p><strong>DeepInfer 推理框架源码笔记 · 精读版</strong> · 源码快照 HEAD <code>9bd9cf2</code> · 2026-10-21 核对 · 11 章 / 14 图</p>
  <p>正文路径均相对 DeepInfer 仓库根目录；行号以上述快照为准，上游更新后可能漂移。官方生产数据与开源版可复现结果已在各章区分标注。返回 <a href="#top">顶部</a>。</p>
</footer>
"""


def build() -> None:
    chapters = []
    for name in CHAPTERS:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            raise SystemExit("缺少章节文件：%s" % path)
        with open(path, "r", encoding="utf-8") as f:
            chapters.append((name, f.read()))

    nav: list[tuple[int, str, list[tuple[str, str]]]] = []
    body: list[str] = []
    fig_counter = [0]
    for idx, (name, text) in enumerate(chapters, 1):
        blocks = parse_blocks(text)
        title = ""
        for b in blocks:
            if b["t"] == "h1":
                title = b["text"]
                break
        m = H1_RE.match(title)
        nav_title = m.group(2) if m else title
        anchors: list[tuple[str, str]] = []
        html = render_blocks(blocks, idx, anchors, fig_counter)
        nav.append((idx, nav_title, anchors))
        body.append('<section class="chapter" id="chap%d">\n%s\n</section>' % (idx, html))

    toc = ['<div class="brand">DeepInfer 源码笔记</div>']
    for idx, nav_title, anchors in nav:
        toc.append('<a class="lv1" href="#ch%d">%d · %s</a>' % (idx, idx, esc(nav_title)))
        for aid, atext in anchors:
            toc.append('<a class="lv2" href="#%s">%s</a>' % (aid, esc(atext)))

    html = (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<meta name="color-scheme" content="dark">\n'
        '<meta name="description" content="DeepInfer 推理框架源码精读：调度、KV cache、注意力、MoE/EPLB、投机解码、ZOS、采样与生产部署">\n'
        "<title>DeepInfer 推理框架源码精读：从调度、缓存到注意力与生产部署</title>\n"
        "<style>" + CSS + "</style>\n</head>\n<body id=\"top\">\n"
        '<div class="wrap">\n\n<nav class="toc">\n  ' + "\n  ".join(toc) + "\n</nav>\n\n"
        "<main>\n<article>\n" + HERO + "\n" + "\n\n".join(body) + "\n" + FOOTER + "\n</article>\n</main>\n</div>\n\n"
        "<script>" + JS + "</script>\n</body>\n</html>\n"
    )
    with open(OUT_HTML, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("已生成：%s" % OUT_HTML)
    print("章节：%d  机制图：%d  行数：%d  字节：%d" % (
        len(chapters), fig_counter[0], html.count("\n") + 1, len(html.encode("utf-8"))
    ))


if __name__ == "__main__":
    build()
