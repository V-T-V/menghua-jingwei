"""梦华经纬 · 回归入口
python run_tests.py
  1) tools/lint.py          确定性静态检查（版本/资源/哨兵/坐标/禁用模式/深链）
  2) 数据断言（python 版，与 tests/assert_data.html 同源 + P2：桥/导出/PDF）
  3) 浏览器断言页提醒（tests/assert_*.html，http 服务下打开，title=PASS 即绿）
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
fails = []


def step(name, fn):
    print(f"—— {name} ——")
    try:
        fn()
        print(f"✓ {name} 通过\n")
    except AssertionError as e:
        fails.append(name)
        print(f"✗ {name} 失败：{e}\n")


def lint():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "lint.py")],
                       capture_output=True, text=True, encoding="utf-8")
    print(r.stdout.strip())
    assert r.returncode == 0, "lint 未全绿"


def data_asserts():
    ent = json.load(open(os.path.join(ROOT, "data/intermediate/entries.json"),
                         encoding="utf-8"))
    m = ent["meta"]
    assert m["blocks"] == 88, f"阅读块 {m['blocks']} ≠ 88"
    assert m["totalChars"] == 27423, f"总字数 {m['totalChars']} ≠ 27423"
    stats = json.load(open(os.path.join(ROOT, "docs", "stats.json"), encoding="utf-8"))
    assert stats["total_chars"] == m["totalChars"], "stats 与 entries 总字数不齐"
    assert sum(stats["vol_chars"].values()) == stats["total_chars"], "卷字数与总字数不齐"
    assert stats["words"]["夜市"] >= 3, f"夜市词频 {stats['words']['夜市']} < 3"
    assert stats["words"]["金明池"] >= 5, f"金明池词频 {stats['words']['金明池']} < 5"
    assert len(stats["gate_mentions"]) >= 30, "城门提及表不足 30 门"
    assert stats["suishi_blocks"] == 43 and stats["suishi_chars"] > 14000, "节序结构异常"
    fr = json.load(open(os.path.join(ROOT, "data", "fetch_report.json"), encoding="utf-8"))
    assert len(fr["vols"]) == 11 and fr["total_chars"] > 25000, "抓取报告异常"

    # ── P2：论文 · 桥 · 导出 ──
    if os.path.exists(os.path.join(ROOT, "docs", "ANALYSIS.md")):
        assert os.path.exists(os.path.join(ROOT, "docs", "梦华经纬-数字人文.pdf")), \
            "论文 PDF 缺失（tools/build_paper_pdf.py）"
        for xf, const in [("data/xref_hy.js", "MH_XREF_HY"), ("data/xref_ly.js", "MH_XREF_LY")]:
            p = os.path.join(ROOT, xf)
            assert os.path.exists(p), f"{xf} 缺失"
            t = open(p, encoding="utf-8").read()
            head = f"window.{const} = "
            x = json.loads(t[t.find(head) + len(head):].rstrip().rstrip(";"))
            assert len(x["rows"] if "rows" in x else x["pairs"]) >= 4, f"{xf} 对照条目不足"
        kml = open(os.path.join(ROOT, "exports", "梦华经纬-城图.kml"),
                   encoding="utf-8").read()
        assert kml.count("<Placemark>") == 55, "KML 点要素 ≠ 55"

    print(f"块 88（{m['perVol']}）· 总 {stats['total_chars']:,} 字 · "
          f"夜市 {stats['words']['夜市']} 次 · 金明池 {stats['words']['金明池']} 次 · "
          f"城门提及 {len(stats['gate_mentions'])} 门 · 节序 {stats['suishi_blocks']} 节 "
          f"{stats['suishi_chars']:,} 字")
    if os.path.exists(os.path.join(ROOT, "docs", "ANALYSIS.md")):
        print("P2：论文 PDF 在账 · 双桥数据在账 · 导出五件在账")


def account_sums():
    """账目对账（SHA256SUMS）：逐行指纹与磁盘实测（行尾无关）+ 行数与生成器一致。"""
    import importlib.util
    import re as _re
    bs_path = os.path.join(ROOT, "tools", "build_sums.py")
    path = os.path.join(ROOT, "SHA256SUMS")
    if not os.path.exists(bs_path):
        assert not os.path.exists(path), "SHA256SUMS 在账但生成器缺失——异常状态"
        print("（跳过：build_sums.py 未建（P2 项））")
        return
    spec = importlib.util.spec_from_file_location("build_sums", bs_path)
    bs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bs)
    want = bs.collect()
    assert os.path.exists(path), "SHA256SUMS 缺失——先 python tools/build_sums.py"
    raw = open(path, "rb").read()
    assert b"\r" not in raw, "SHA256SUMS 行尾混入 CR——须纯 LF，重跑 tools/build_sums.py"
    lines = raw.decode("utf-8").splitlines()
    assert lines, "SHA256SUMS 为空"
    problems, seen = [], set()
    for i, line in enumerate(lines, 1):
        parts = line.split("  ", 1)
        rel = parts[1].strip().replace("\\", "/") if len(parts) == 2 else ""
        if len(parts) != 2 or not _re.fullmatch(r"[0-9a-f]{64}", parts[0]) or not rel:
            problems.append(f"第{i}行格式非法"); continue
        if rel in seen:
            problems.append(f"第{i}行重复 {rel}"); continue
        seen.add(rel)
        if not os.path.isfile(os.path.join(ROOT, rel)):
            problems.append(f"账上文件缺失 {rel}"); continue
        if bs.sha256(rel) != parts[0]:
            problems.append(f"指纹不符 {rel}")
    assert not problems, f"账目失真 {len(problems)} 处：{problems[:4]}——重跑 python tools/build_sums.py"
    assert len(lines) == len(want), \
        f"账目行数 {len(lines)} ≠ 生成器 {len(want)}（产物增删未记账）——重跑 python tools/build_sums.py"
    off = [r for r in want if r not in seen]
    assert not off, f"产物缺账 {off[:4]}——重跑 python tools/build_sums.py"
    print(f"SHA256SUMS 对账通过：{len(lines)} 行 · 指纹全符（纯 LF）")


def browser_pages():
    pages = [f for f in os.listdir(os.path.join(ROOT, "tests")) if f.startswith("assert_")]
    assert len(pages) >= 3, "断言页不足"
    print(f"浏览器断言页 {len(pages)} 枚：{', '.join(pages)}")
    print("（serve 后逐页打开，title=PASS 即绿——截图证据见 docs/img/）")


def offline_check():
    """离线三验（可选步：本地服务在跑且有浏览器才执行；CI 由 audit.yml 专步硬跑）。"""
    import shutil
    import urllib.request
    base = os.environ.get("MH_BASE", "http://127.0.0.1:9900/")
    try:
        urllib.request.urlopen(base + "index.html", timeout=3).read()
    except Exception:
        print(f"（跳过：本地服务不可达 {base}——起服务后可单跑 python tools/offline_check.py）")
        return
    cands = [os.environ.get("MH_BROWSER", ""),
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             shutil.which("google-chrome") or "", shutil.which("chromium") or ""]
    if not next((c for c in cands if c and os.path.exists(c)), None):
        print("（跳过：未找到本地浏览器——MH_BROWSER 可指定）")
        return
    oc = os.path.join(ROOT, "tools", "offline_check.py")
    if not os.path.exists(oc):
        print("（跳过：tools/offline_check.py 未建（P2 项））")
        return
    r = subprocess.run([sys.executable, oc], capture_output=True, text=True,
                       encoding="utf-8", timeout=300)
    print(r.stdout.strip())
    assert r.returncode == 0, f"离线三验未全绿（exit {r.returncode}）"


if __name__ == "__main__":
    step("lint", lint)
    step("数据断言", data_asserts)
    step("账目对账", account_sums)
    step("浏览器断言页", browser_pages)
    step("离线三验（可选）", offline_check)
    if fails:
        print(f"✗✗ 回归失败：{', '.join(fails)}")
        sys.exit(1)
    print("═══ 全绿 ═══")
