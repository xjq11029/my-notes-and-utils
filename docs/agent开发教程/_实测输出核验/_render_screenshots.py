"""把 截图页面/*.html 逐张渲染成 PNG（无头 Edge）。"""
import pathlib
import subprocess
import sys
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent
FRAG = ROOT / "截图页面"
SHOTS = ROOT / "截图"
SHOTS.mkdir(exist_ok=True)

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
TITLES = {
    "00": "00-示例运行清单",
    "01": "01-智谱key连通性与可用模型",
    "02": "02-真实模型验证未实测声明",
    "03": "03-Python上线请求体",
    "04": "04-JS上线请求体",
    "05": "05-ch09快照数复现",
}

for html in sorted(FRAG.glob("*.html")):
    key = html.stem
    url = pathlib.Path(html).absolute().as_uri()
    out = SHOTS / f"{TITLES.get(key, key)}.png"
    # 高度按内容估：每行 ~21px，留足余量；宽 1240 与 CSS 的 1180 容器匹配
    lines = len(html.read_text(encoding="utf-8").splitlines())
    h = max(1000, min(6000, 260 + lines * 22))
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           f"--user-data-dir={pathlib.Path.home() / 'AppData' / 'Local' / 'Temp' / 'edge-shot'}",
           "--force-device-scale-factor=2", f"--window-size=1240,{h}",
           "--virtual-time-budget=6000", f"--screenshot={out}", url]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = out.exists()
    print(f"  {out.name:<34} {'OK ' if ok else 'FAIL'} "
          f"{out.stat().st_size if ok else 0:>9,} B   (窗口高 {h})")
