# -*- coding: utf-8 -*-
"""梦华经纬 · 文本计量（docs/stats.json —— 全站唯一数字源）
读 data/intermediate/entries.json + data/site_data.js 前身（本脚本先于 build_data 亦可：
门/河/街市表由 build_data.py 的清单 import 而来，两脚本共用同一清单常量）。
产出：总字数/分卷字数/块数 · 门·河·街市提及计数 · 节序篇幅（月分布）· 街市民俗卷篇幅
     · 词频（酒肆市井词表）· 类别条数
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_data as BD   # 共用 GATES/RIVERS/PLACES/SUISHI_MONTH 清单（单一来源）

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def corpus_all():
    return "".join(open(os.path.join(ROOT, "data", "vol", f"{v:03d}.txt"),
                        encoding="utf-8").read() for v in range(11))


def main():
    ent = json.load(open(os.path.join(ROOT, "data", "intermediate", "entries.json"),
                         encoding="utf-8"))
    blocks = ent["blocks"]
    corpus = corpus_all()

    vol_chars = {str(v): sum(b["chars"] for b in blocks if b["vol"] == v) for v in range(11)}
    vol_blocks = {str(v): sum(1 for b in blocks if b["vol"] == v) for v in range(11)}

    # 篇幅结构（正文四层：卷一城防 / 卷二至五街市民俗 / 卷六至十岁时）
    layer_chars = {
        "chengfang": vol_chars["1"],
        "street": sum(vol_chars[str(v)] for v in (2, 3, 4, 5)),
        "suishi": sum(vol_chars[str(v)] for v in range(6, 11)),
        "front": vol_chars["0"],
    }

    # 城门/河道/街市提及计数（全书出场，含自条目句）
    gate_mentions = {g[0]: corpus.count(g[0]) for g in BD.GATES}
    river_mentions = {r["name"]: corpus.count(r["name"]) for r in BD.RIVERS}
    place_mentions = {p[0]: corpus.count(p[0]) for p in BD.PLACES}

    # 节序月分布（chars per lunar month）
    suishi_month_chars = {}
    suishi_month_n = {}
    for b in blocks:
        if b["kind"] != "suishi":
            continue
        m = BD.SUISHI_MONTH.get(b["name"])
        if m is None:
            continue
        suishi_month_chars[str(m)] = suishi_month_chars.get(str(m), 0) + b["chars"]
        suishi_month_n[str(m)] = suishi_month_n.get(str(m), 0) + 1

    # 词频（市井词表——分析预设，计数机械）
    words = {}
    for w in ["酒樓", "酒肆", "正店", "脚店", "夜市", "瓦子", "勾欄", "御街", "御路",
              "橋", "門", "車駕", "關撲", "妓", "香藥", "金銀", "綵帛", "包子", "果子",
              "宣德", "州橋", "相國寺", "金明池", "亰師", "夢"]:
        words[w] = corpus.count(w)

    suishi_blocks = [b for b in blocks if b["kind"] == "suishi"]
    out = {
        "source": BD.__doc__.split("\n")[0] if BD.__doc__ else "",
        "total_chars": ent["meta"]["totalChars"],
        "vol_chars": vol_chars,
        "vol_blocks": vol_blocks,
        "blocks": len(blocks),
        "layer_chars": layer_chars,
        "gate_mentions": gate_mentions,
        "river_mentions": river_mentions,
        "place_mentions": place_mentions,
        "suishi_blocks": len(suishi_blocks),
        "suishi_chars": layer_chars["suishi"],
        "suishi_month_chars": suishi_month_chars,
        "suishi_month_n": suishi_month_n,
        "words": words,
        "kr_entities": ent["meta"]["totalChars"] and sum(
            v.get("krEntities", 0) for v in
            json.load(open(os.path.join(ROOT, "data", "fetch_report.json"),
                           encoding="utf-8"))["vols"]),
    }
    path = os.path.join(ROOT, "docs", "stats.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"✓ docs/stats.json：总 {out['total_chars']:,} 字 · {out['blocks']} 块 · "
          f"城防 {layer_chars['chengfang']:,} / 街市 {layer_chars['street']:,} / "
          f"岁时 {layer_chars['suishi']:,} 字")
    print("  节序月分布（块数）:", {k: suishi_month_n[k] for k in sorted(suishi_month_n, key=int)})


if __name__ == "__main__":
    main()
