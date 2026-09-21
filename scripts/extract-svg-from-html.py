#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract-svg-from-html.py —— 把 HTML 里的内联 <svg> 抽成独立 .svg 文件

用途：
  长文 HTML（如 docs/harness/agent-harness-deep-dive.html）里的图示是内联 SVG，
  内嵌在单文件里、不依赖外部图片。但要往 Markdown 平台（掘金 / CSDN）发文章时，
  必须先把它们变成独立图片文件。本脚本负责第一步：抽成 .svg；
  第二步交给 scripts/svg-to-png.mjs 渲染成 2× PNG。

  ⚠️ 为什么要 --bg：svg-to-png.mjs 硬编码 `background: '#FFFFFF'`，
     而深色主题文档里的图示文字全是浅色。不注入底色，渲染出来就是
     「浅字白底」= 不可读。注入与文档 --bg-soft 同色的满幅底矩形，
     等于把原文的深色图面板原样搬到浅色平台上。

用法：
  python scripts/extract-svg-from-html.py <html 文件> <输出目录> [选项]

选项：
  --from-anchor ID   起始锚点（该 <h2 id="ID"> 之后的内容纳入；默认从文件开头）
  --to-anchor   ID   结束锚点（该 <h2 id="ID"> 之前的内容纳入；默认到文件末尾）
  --bg COLOR         注入满幅底矩形的颜色（如 #111721）；不给则保持透明
  --label            在每张图底部注入一行居中的「图 N」（viewBox 高度 +34）
  --replace OLD=NEW  对抽出的 SVG 做字面替换，可重复。用于修正「在长文里正确、
                     但重编号后在发布稿里失效」的图内文字（改不了文字只能改源）
  --prefix STR       文件名前缀（默认 fig）
  --names A,B,C      逐张短名，生成 fig01-A.svg；数量须与图数一致
  --expect N         断言抽到的图数（不符则报错退出，防区间写错）
  --dry-run          只打印清单，不写文件

行为：
  - 只在 [from-anchor, to-anchor) 区间内找 <figure>…</figure>，逐张抽其中的 <svg>
  - 底矩形宽高取自该图自己的 viewBox（不要用 viewBox 当唯一标识去定位图，
    同尺寸的图会抽错——区间切分本身才是定位手段）
  - 处理顺序固定：抽 SVG → --replace → --bg 注入底矩形 → --label 注入图号
  - 已存在同名文件直接覆盖；输出统一 LF 行尾

示例：
  python scripts/extract-svg-from-html.py \
      docs/harness/agent-harness-deep-dive.html \
      docs/harness/articles/images \
      --from-anchor s0 --to-anchor s4 --bg '#111721' --expect 13 --label \
      --replace '方块里的数字与 3.1 的组件表一致=方块里的数字与组件表的编号一致'
"""

import argparse
import re
import sys
from pathlib import Path

SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>")
VIEWBOX_RE = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')
FIGURE_RE = re.compile(r"<figure>.*?</figure>", re.S)

# --label：底部图号栏的高度，以及图号基线相对「原 viewBox 底边」的偏移
LABEL_PAD = 34
LABEL_BASELINE = 23
LABEL_FILL = "#93a1b1"   # 文档 --dim：长文 figcaption 里 <b>图 N</b> 用的就是这个色
LABEL_SIZE = 12.5


def inject_label(svg: str, w: str, h: str, n: int) -> str:
    """把 viewBox 加高 LABEL_PAD，在底部居中写入「图 N」。

    ⚠️ 图号栏必须放在**原 viewBox 之外**，不能复用现有底部留白——各图留白从 6px
    到 38px 不等，塞进留白会让留白小的图（如图 5，仅 6px）压到内容。
    """
    W, H = float(w), float(h)
    new_h = H + LABEL_PAD
    vb = f'viewBox="0 0 {w} {h}"'
    assert vb in svg, "找不到 viewBox，无法注入图号"
    svg = svg.replace(vb, f'viewBox="0 0 {w} {new_h:g}"', 1)
    # 满幅底矩形（--bg 注入的那一条）跟着长高
    svg = svg.replace(f'x="0" y="0" width="{w}" height="{h}"',
                      f'x="0" y="0" width="{w}" height="{new_h:g}"', 1)
    text = (f'  <text x="{W / 2:g}" y="{H + LABEL_BASELINE:g}" fill="{LABEL_FILL}"'
            f' font-size="{LABEL_SIZE}" font-weight="600" text-anchor="middle"'
            f' font-family="sans-serif">图 {n}</text>\n')
    assert svg.count("</svg>") == 1, "</svg> 不唯一，无法注入图号"
    return svg.replace("</svg>", text + "</svg>", 1)


def slice_by_anchors(html: str, from_anchor: str | None, to_anchor: str | None) -> tuple[str, int]:
    """按 <h2 id="..."> 锚点切出区间，返回 (区间文本, 起始行号)。"""
    start = 0
    if from_anchor:
        m = re.search(rf'<h2 id="{re.escape(from_anchor)}"', html)
        if not m:
            sys.exit(f'找不到起始锚点 id="{from_anchor}"')
        start = m.start()
    end = len(html)
    if to_anchor:
        m = re.search(rf'<h2 id="{re.escape(to_anchor)}"', html)
        if not m:
            sys.exit(f'找不到结束锚点 id="{to_anchor}"')
        end = m.start()
    if end <= start:
        sys.exit("结束锚点位于起始锚点之前，区间为空")
    return html[start:end], html[:start].count("\n") + 1


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("html")
    ap.add_argument("outdir")
    ap.add_argument("--from-anchor")
    ap.add_argument("--to-anchor")
    ap.add_argument("--bg")
    ap.add_argument("--label", action="store_true",
                    help="在每张图底部注入一行居中的「图 N」（viewBox 高度 +%d）" % LABEL_PAD)
    ap.add_argument("--replace", action="append", default=[], metavar="OLD=NEW",
                    help="对抽出的 SVG 做字面替换，可重复")
    ap.add_argument("--prefix", default="fig")
    ap.add_argument("--names")
    ap.add_argument("--expect", type=int)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    html_path = Path(args.html)
    if not html_path.is_file():
        sys.exit(f"文件不存在：{html_path}")
    html = html_path.read_text(encoding="utf-8")

    region, base_line = slice_by_anchors(html, args.from_anchor, args.to_anchor)
    figures = FIGURE_RE.findall(region)

    print(f"区间：{args.from_anchor or '文件开头'} → {args.to_anchor or '文件末尾'}"
          f"（约第 {base_line} 行起），命中 <figure> {len(figures)} 张")

    if args.expect is not None and len(figures) != args.expect:
        sys.exit(f"图数不符：预期 {args.expect}，实际 {len(figures)} —— 区间可能写错，已中止")

    names = args.names.split(",") if args.names else []
    if names and len(names) != len(figures):
        sys.exit(f"--names 给了 {len(names)} 个，但图有 {len(figures)} 张")

    outdir = Path(args.outdir)
    if not args.dry_run:
        outdir.mkdir(parents=True, exist_ok=True)

    problems: list[str] = []
    written: list[str] = []
    replace_hits: dict[str, int] = {r: 0 for r in args.replace}

    for i, fig in enumerate(figures, start=1):
        m = SVG_OPEN_RE.search(fig)
        if not m:
            problems.append(f"图 {i}：<figure> 内找不到 <svg> 开标签")
            continue

        open_tag = m.group(0)
        vb = VIEWBOX_RE.search(open_tag)
        if not vb:
            problems.append(f"图 {i}：viewBox 解析失败")
            continue
        w, h = vb.group(1), vb.group(2)

        end = fig.find("</svg>")
        if end < 0:
            problems.append(f"图 {i}：找不到 </svg>")
            continue
        svg = fig[m.start(): end + len("</svg>")]

        if "xmlns=" not in svg:
            svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)

        if args.bg:
            # 紧跟 <svg …> 开标签之后插入满幅底矩形
            rect = f'\n  <rect x="0" y="0" width="{w}" height="{h}" fill="{args.bg}"/>'
            svg = svg[: len(open_tag)] + rect + svg[len(open_tag):]

        # 字面替换：修正「在长文里正确、重编号后在发布稿里失效」的图内文字。
        # 规则是**全局**的（一条规则可能只命中其中一张图），所以命中数按规则累计，
        # 循环结束后再判断——某条规则全程 0 命中才说明它失效了。
        for rule in args.replace:
            if "=" not in rule:
                sys.exit(f"--replace 需要 OLD=NEW 形式，收到：{rule}")
            old, new = rule.split("=", 1)
            n = svg.count(old)
            if n:
                svg = svg.replace(old, new)
                replace_hits[rule] += n
                print(f"    图 {i}：替换 ×{n}　{old[:22]}… → {new[:22]}…")

        if args.label:
            svg = inject_label(svg, w, h, i)

        suffix = f"-{names[i - 1]}" if names else ""
        fname = f"{args.prefix}{i:02d}{suffix}.svg"
        target = outdir / fname
        # 最终尺寸要算上 --label 加高的那一段，否则打印出来的尺寸是误导
        out_h = float(h) + (LABEL_PAD if args.label else 0)

        if args.dry_run:
            print(f"  [dry-run] {fname}  {w}×{out_h:g}")
        else:
            target.write_text(svg + "\n", encoding="utf-8", newline="\n")
            print(f"  写出 {fname}  {w}×{out_h:g}  {len(svg)} 字符")
        written.append(fname)

    for rule, hits in replace_hits.items():
        if hits == 0:
            problems.append(f"--replace 全程 0 命中（规则已失效，检查原文是否变过）：{rule}")

    if problems:
        print("\n问题：")
        for p in problems:
            print("  - " + p)
        return 1

    print(f"\n完成：共 {len(written)} 张。"
          + ("（dry-run，未写盘）" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
