# -*- coding: utf-8 -*-
"""梦华经纬 · lint（确定性检查，失败即红）
用法: python tools/lint.py
类别（承姊妹站 lint 哲学——文字指令与 lint 冲突时 lint 是对的）：
  1  版本一致性   index.html/sw.js/js 的 ?v= 全等于 sw.js VERSION
  2  资源存在性   index.html 引用的 script/css 存在；sw SHELL_FILES 全部存在
  3  数据哨兵     城门=34(外16/舊12/大内6) · 河=4 · 街市=21 · 节序=43 · 块=88 · 总字数=stats.json
  4  坐标边界     城门/街市/河道折点全部落图界内；全部 src="derived"；书证非空
  5  挂接完整     街市 jie / 节序 id 在 MH_SECTIONS 有原文；sections 与 entries.json 同块数；ord 连续
  6  语料口径     data/text/vN.js 与 data/vol/NNN.txt 逐字一致
  7  脚本产物一致 data/stats.js 的 total_chars 与 docs/stats.json 一致（前端只读脚本产物）
  8  禁用模式     map.fire("click") / innerHTML.indexOf 验证 / window._ftw / git mv -q / || true
  9  深链一致     app.js 深链语法（#m/#juan/#jie/#men/#he/#sui）
 10  manifest     icons 三枚存在，manifest 引用一致
 11  文档同步     ANALYSIS.md 新于论文 PDF 即红（P2 起生效）
 12  导出同口径   exports/ 三 CSV+KML+GeoJSON（P2 起生效）
 13  P2 数据哨兵  xref_hy.js / xref_ly.js（P2 起生效）
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails, checks = [], []


def ok(cond, msg):
    checks.append(cond)
    if not cond:
        fails.append(msg)


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def load_const(path, const):
    t = read(path)
    head = f"const {const} = "
    i = t.find(head)
    if i < 0:
        raise AssertionError(f"{path} 缺 const {const}")
    return json.loads(t[i + len(head):].rstrip().rstrip(";"))


def load_window(path, const):
    t = read(path)
    head = f"window.{const} = "
    i = t.find(head)
    if i < 0:
        raise AssertionError(f"{path} 缺 window.{const}")
    return json.loads(t[i + len(head):].rstrip().rstrip(";"))


def main():
    # ── 1 版本一致性 ──
    sw = read("sw.js")
    mver = re.search(r'VERSION = "v(\d+)"', sw)
    ok(mver, "sw.js 缺 VERSION 常量")
    ver = mver.group(1) if mver else ""
    for f in ["index.html", "sw.js"] + ["js/" + x for x in os.listdir(os.path.join(ROOT, "js"))
                                        if x.endswith(".js")]:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8").read()
        for bad in set(re.findall(r"\?v=(\d+)", t)):
            ok(bad == ver, f"{f} 含过期版本 ?v={bad}（当前 v{ver}）——请跑 tools/bump_version.py")

    # ── 2 资源存在性 ──
    idx = read("index.html")
    for src in re.findall(r'(?:src|href)="([^"#?]+)(?:\?[^"]*)?"', idx):
        if src.startswith(("http", "data:")):
            continue
        ok(os.path.exists(os.path.join(ROOT, src)), f"index.html 引用缺失: {src}")
    for m2 in re.finditer(r'"(\./[^"]+?)(?:\?[^"]*)?"', sw):
        rel = m2.group(1)[2:]
        ok(os.path.exists(os.path.join(ROOT, rel)), f"sw SHELL_FILES 缺失: {rel}")
    ok("data/stats.js" in idx, "index.html 须引 data/stats.js（rail/stats 面板依赖 MH_STATS）")
    ok("data/site_data.js" in idx, "index.html 须引 data/site_data.js")

    # ── 3 数据哨兵 ──
    mhz = load_const("data/site_data.js", "MHZ")
    m = mhz["meta"]
    ok(m["gates"] == 34, f"城门总数 {m['gates']} ≠ 34（外16+舊12+大内6）")
    ok(m["gatesOuter"] == 16, f"外城门 {m['gatesOuter']} ≠ 16")
    ok(m["gatesInner"] == 12, f"旧城门 {m['gatesInner']} ≠ 12（卷一「三壁其門有三」×4）")
    ok(m["gatesPalace"] == 6, f"宫门 {m['gatesPalace']} ≠ 6")
    ok(m["rivers"] == 4, f"河道 {m['rivers']} ≠ 4（穿城四河）")
    ok(m["places"] == 21, f"街市 {m['places']} ≠ 21")
    ok(m["suishi"] == 43, f"节序 {m['suishi']} ≠ 43")
    ok(m["blocks"] == 88, f"阅读块 {m['blocks']} ≠ 88")
    ok(len(mhz["gates"]) == 34 and len(mhz["rivers"]) == 4 and
       len(mhz["places"]) == 21 and len(mhz["suishi"]) == 43, "四表长度与 meta 不齐")
    stats = json.load(open(os.path.join(ROOT, "docs", "stats.json"), encoding="utf-8"))
    ok(m["totalChars"] == stats["total_chars"], "site_data 与 stats.json 总字数不一致")
    ok(25000 <= stats["total_chars"] <= 32000, f"总字数 {stats['total_chars']} 越界")
    ok(stats["layer_chars"]["suishi"] > stats["layer_chars"]["street"] > 0, "三层篇幅结构异常")
    ok(stats["suishi_blocks"] == 43, f"stats 节序块 {stats['suishi_blocks']} ≠ 43")
    fr = json.load(open(os.path.join(ROOT, "data", "fetch_report.json"), encoding="utf-8"))
    ok(len(fr["vols"]) == 11 and fr["total_chars"] > 25000, "抓取报告异常（须 11 文件）")

    # ── 4 坐标边界与 src ──
    BX, BY = (-2800, 10300), (-1200, 5100)
    for g in mhz["gates"]:
        x, y = g["pos"]
        ok(BX[0] < x < BX[1] and 0 <= y <= 4800,
           f"城门「{g['name']}」坐标越界 {g['pos']}（外城内 0..8800×0..4800）")
    for p in mhz["places"]:
        x, y = p["pos"]
        ok(BX[0] < x < BX[1] and BY[0] < y < BY[1], f"街市「{p['name']}」坐标越界 {p['pos']}")
    for r in mhz["rivers"]:
        for pt in r["pts"]:
            ok(BX[0] <= pt[0] <= BX[1] and BY[0] <= pt[1] <= BY[1],
               f"河道「{r['name']}」折点越界 {pt}")
    for it in mhz["gates"] + mhz["places"] + mhz["rivers"]:
        ok(it.get("src") == "derived", f"「{it.get('name')}」缺 src:derived")
    for g in mhz["gates"]:
        ok(bool(g.get("att")), f"城门「{g['name']}」缺书证 att")
        ok(g["wall"] in ("外城", "舊城", "大内"), f"城门「{g['name']}」wall 非法")
    for p in mhz["places"]:
        ok(bool(p.get("att")), f"街市「{p['name']}」缺方位书证")
        ok(p["conf"] == "text", f"街市「{p['name']}」conf 非法")
    # 门不落城垣线外过远（外城门应在外城墙 ±400 内）
    for g in mhz["gates"]:
        x, y = g["pos"]
        if g["wall"] == "外城":
            onx = abs(x - 8800) < 400 or abs(x) < 400
            ony = y < 400 or abs(y - 4800) < 400
            ok(onx or ony, f"外城门「{g['name']}」不在城墙线上 {g['pos']}")
        if g["wall"] == "舊城":
            onx = abs(x - 5900) < 400 or abs(x - 2300) < 400
            ony = abs(y - 1400) < 400 or abs(y - 4300) < 400
            ok(onx or ony, f"旧城门「{g['name']}」不在旧城墙线上 {g['pos']}")

    # ── 5 挂接完整 ──
    secs = load_const("data/sections.js", "MH_SECTIONS")
    entries = json.load(open(os.path.join(ROOT, "data/intermediate/entries.json"),
                             encoding="utf-8"))
    ok(len(secs) == len(entries["blocks"]),
       f"sections {len(secs)} 块 ≠ entries {len(entries['blocks'])}")
    ords = sorted(b["ord"] for b in secs.values())
    ok(ords == list(range(len(secs))), "sections ord 非连续（循读排序依赖）")
    for p in mhz["places"]:
        ok(p["jie"] in secs, f"街市「{p['name']}」未挂阅读块 {p['jie']}")
        ok(secs[p["jie"]]["chars"] == p["chars"], f"街市「{p['name']}」chars 与块不齐")
    for s in mhz["suishi"]:
        ok(s["id"] in secs, f"节序「{s['name']}」未挂阅读块")
        ok(1 <= s["month"] <= 12, f"节序「{s['name']}」月序非法")
    kinds = {b["kind"] for b in entries["blocks"]}
    ok({"tiyao", "preface", "city", "street", "folk", "suishi"} <= kinds, "六类阅读块不齐")

    # ── 6 语料口径 ──
    for v in range(11):
        txt = read(f"data/vol/{v:03d}.txt")
        js = read(f"data/text/v{v}.js")
        head = f"(window.MHTEXT=window.MHTEXT||{{}})[{v}]="
        i = js.find(head)
        ok(i >= 0, f"data/text/v{v}.js 缺 MHTEXT 头")
        if i >= 0:
            body = json.loads(js[i + len(head):].rstrip().rstrip(";"))
            ok(body == txt, f"data/text/v{v}.js 与 data/vol/{v:03d}.txt 语料不一致")

    # ── 7 脚本产物一致 ──
    qstats = load_const("data/stats.js", "MH_STATS")
    ok(qstats["total_chars"] == stats["total_chars"], "data/stats.js 与 docs/stats.json 不一致")
    ok(qstats["blocks"] == 88, "data/stats.js 块数 ≠ 88")

    # ── 8 禁用模式 ──
    banned = [
        (r'map\.fire\(\s*["\']click', "map.fire(click) 委托分发不可靠——用 canvas.dispatchEvent"),
        (r'innerHTML\.indexOf\(', "innerHTML.indexOf 验证会因 & 序列化失效——用 textContent"),
        (r'window\._ftw', "闭包 let 量不在 window 上——用存取函数"),
        (r'git mv -q', "git mv 无 -q flag"),
        (r'\|\|\s*true', "|| true 兜底吞错（教训 20）"),
    ]
    for f in ["js/" + x for x in os.listdir(os.path.join(ROOT, "js")) if x.endswith(".js")]:
        t = open(p := os.path.join(ROOT, f), encoding="utf-8").read()
        for pat, why in banned:
            ok(not re.search(pat, t), f"{f} 触禁：{why}")

    # ── 9 深链一致 ──
    app = read("js/app.js")
    for frag in ["#m=", "#juan=", "#jie=", "#men=", "#he=", "#sui="]:
        ok(frag in app, f"app.js 深链语法缺 {frag}")
    reader = read("js/reader.js")
    ok("#juan=" in reader, "reader.js 深链写回缺 #juan=")

    # ── 10 manifest ──
    mani = read("manifest.json")
    for icon in re.findall(r'"src":\s*"(icons/[^"]+)"', mani):
        ok(os.path.exists(os.path.join(ROOT, icon)), f"manifest 引用图标缺失: {icon}")

    # ── 11-13 P2 哨兵（产物落地后生效；未落地时提示但不放宽 P0 门禁以外检查） ──
    if os.path.exists(os.path.join(ROOT, "docs", "ANALYSIS.md")):
        pdf = os.path.join(ROOT, "docs", "梦华经纬-数字人文.pdf")
        ok(os.path.exists(pdf), "docs/梦华经纬-数字人文.pdf 缺失——跑 tools/build_paper_pdf.py")
        if os.path.exists(pdf):
            import time
            mt, pt = os.path.getmtime(os.path.join(ROOT, "docs", "ANALYSIS.md")), os.path.getmtime(pdf)
            ok(mt <= pt + 60, "文档失同步：ANALYSIS.md 新于 PDF——重跑 tools/build_paper_pdf.py")
        exp = os.path.join(ROOT, "exports")
        for fn in ["梦华经纬-城门.csv", "梦华经纬-河道.csv", "梦华经纬-街市.csv",
                   "梦华经纬-城图.kml", "梦华经纬-城图.geojson"]:
            ok(os.path.exists(os.path.join(exp, fn)), f"exports/{fn} 缺失——跑 tools/export_data.py")
        for fn, n in [("梦华经纬-城门.csv", 34), ("梦华经纬-河道.csv", 4), ("梦华经纬-街市.csv", 21)]:
            p2 = os.path.join(exp, fn)
            if os.path.exists(p2):
                raw = open(p2, "rb").read()
                ok(raw[:3] == b"\xef\xbb\xbf", f"exports/{fn} 缺 UTF-8 BOM")
                lines = raw.decode("utf-8-sig").rstrip("\n").split("\n")
                ok(len(lines) == n + 1, f"exports/{fn} {len(lines) - 1} 行 ≠ 表 {n} 行")
                ok("derived" in lines[1], f"exports/{fn} 首数据行缺 derived 注记")
        kml_p = os.path.join(exp, "梦华经纬-城图.kml")
        if os.path.exists(kml_p):
            kml = open(kml_p, encoding="utf-8").read()
            ok(kml.count("<Point>") == 34 + 21, f"KML 点要素 {kml.count('<Point>')} ≠ 55")
            ok(kml.count("<LineString>") == 4, "KML 线要素 ≠ 4")
            ok(kml.count("<Placemark>") == 59, f"KML 总要素 {kml.count('<Placemark>')} ≠ 59")
            ok("derived" in kml, "KML 缺 derived 注记")
        gj_p = os.path.join(exp, "梦华经纬-城图.geojson")
        if os.path.exists(gj_p):
            gj = json.load(open(gj_p, encoding="utf-8"))
            ok(len(gj["features"]) == 34 + 21 + 4, f"GeoJSON 要素 {len(gj['features'])} ≠ 59")
            ok(all(f["properties"].get("src") and "derived" in f["properties"]["src"]
                   for f in gj["features"]), "GeoJSON 存在未注 derived 的要素")
    for xf in ["data/xref_hy.js", "data/xref_ly.js"]:
        if os.path.exists(os.path.join(ROOT, xf)):
            xt = read(xf)
            ok("window.MH_XREF_" in xt, f"{xf} 缺 window.MH_XREF_* 挂接")
    ok("xref_hy" in read("js/stats.js") and "xref_ly" in read("js/stats.js"),
       "计量面板缺双桥页签（xref_hy/xref_ly）")

    # ── 报告 ──
    n = len(checks)
    print(f"lint：{n} 项检查")
    if fails:
        print(f"✗ {len(fails)} 项失败：")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("✓ 全绿")


if __name__ == "__main__":
    main()
