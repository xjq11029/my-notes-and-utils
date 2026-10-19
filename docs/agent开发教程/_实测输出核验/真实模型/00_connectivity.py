"""连通性 + 可用模型探测。key 从 gitignore 的 .secrets.log 读取，不硬编码。"""
import json
import pathlib
import urllib.request

BASE = "https://open.bigmodel.cn/api/paas/v4"
KEY = (pathlib.Path(__file__).resolve().parents[2] / "code" / ".secrets.log")
API_KEY = KEY.read_text(encoding="utf-8").strip()


def call(model, messages, **extra):
    body = {"model": model, "messages": messages, **extra}
    req = urllib.request.Request(
        f"{BASE}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


print("=" * 70)
print("① 连通性探测（逐个模型发一条最小请求）")
print("=" * 70)
for m in ["glm-4.5-air", "glm-4.6v", "glm-4-plus", "glm-4.5", "glm-4.6"]:
    try:
        d = call(m, [{"role": "user", "content": "只回复两个字：收到"}], max_tokens=8)
        print(f"  {m:<14} OK   content={d['choices'][0]['message']['content']!r}")
        print(f"  {'':<14}      usage={d.get('usage')}")
    except Exception as e:  # noqa: BLE001
        detail = e.read().decode("utf-8")[:200] if hasattr(e, "read") else str(e)[:200]
        print(f"  {m:<14} FAIL {type(e).__name__}: {detail}")
