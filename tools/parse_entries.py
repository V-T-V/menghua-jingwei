# -*- coding: utf-8 -*-
"""梦华经纬 · Phase 1 解析（data/vol/*.txt → data/intermediate/entries.json）
块结构：每 ◎ 行起一个阅读块（提要以 JUAN 分界同式），卷内保持原序。
paras：块内长文按句群切段（每 3 个。一段——刻本连排非分段，为屏读可读性机械切分，
       不增删一字）。夹注（括号双行注）保留原文，前端以小字渲染。
验证：块数与 fetch_report.sects 对账；全书每块 chars 求和 = 总字数。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOL_DIR = os.path.join(ROOT, "data", "vol")

VOL_KINDS = {0: "preface", 1: "city", 2: "street", 3: "street", 4: "street",
             5: "folk", 6: "suishi", 7: "suishi", 8: "suishi", 9: "suishi", 10: "suishi"}
# 000 内两块特殊：◎提要 kind=tiyao，◎自序 kind=preface
SPECIAL = {("自序", 0): "preface", ("提要", 0): "tiyao"}


def split_paras(text: str, target: int = 110, slack: int = 28):
    """四库本无句读——按字长机械分段（屏读可读性），边界在 ±slack 内吸附常见
    发语/转语字（每/凡/又/自/至/其/若/常/有/於/是/中），不增删一字，纯切分。"""
    out = []
    rest = text
    while len(rest) > target + slack:
        cut = None
        for k in range(target - slack, target + slack):
            if k < len(rest) and rest[k] in "每凡又自此至其若常有於是中":
                cut = k + 1
                break
        if cut is None or cut <= 10:
            cut = target
        out.append(rest[:cut])
        rest = rest[cut:]
    if rest:
        if out and len(rest) < 30:
            out[-1] += rest
        else:
            out.append(rest)
    return out


def main():
    fr = json.load(open(os.path.join(ROOT, "data", "fetch_report.json"), encoding="utf-8"))
    blocks, problems = [], []
    for vol in range(11):
        txt = open(os.path.join(VOL_DIR, f"{vol:03d}.txt"), encoding="utf-8").read()
        parts = []
        for ln in txt.split("\n"):
            if ln.startswith("◎"):
                parts.append([ln[1:], ""])
            elif not parts:
                problems.append(f"卷{vol} 块前正文: {ln[:20]}")
            else:
                parts[-1][1] += ln
        for k, (name, body) in enumerate(parts):
            chars = len(body)
            kind = SPECIAL.get((name, vol), VOL_KINDS[vol])
            blocks.append({
                "id": f"v{vol}-{k:02d}",
                "vol": vol, "name": name, "kind": kind,
                "chars": chars, "paras": split_paras(body),
            })
        rep = next(r for r in fr["vols"] if r["num"] == f"{vol:03d}")
        if rep["sects"] != len(parts):
            problems.append(f"卷{vol} 块数 {len(parts)} ≠ 抓取报告 {rep['sects']}")
        # 报告口径含节题字；对账剥去节题（名长之和）
        vol_chars = sum(len(p[1]) for p in parts)
        rep_body = rep["chars"] - sum(len(p[0]) for p in parts)
        if vol_chars != rep_body:
            problems.append(f"卷{vol} 正文字数 {vol_chars} ≠ 报告剥节题 {rep_body}")

    out = {
        "meta": {
            "blocks": len(blocks),
            "totalChars": sum(b["chars"] for b in blocks),
            "perVol": {str(v): sum(1 for b in blocks if b["vol"] == v) for v in range(11)},
            "source": fr["source"],
        },
        "blocks": blocks,
    }
    path = os.path.join(ROOT, "data", "intermediate", "entries.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"✓ {len(blocks)} 块 · {out['meta']['totalChars']:,} 字 → data/intermediate/entries.json")
    print("  分卷块数:", " ".join(f"{v}:{out['meta']['perVol'][str(v)]}" for v in range(11)))
    if problems:
        raise SystemExit("对账失败：\n" + "\n".join(problems))
    print("  与 fetch_report 对账通过")


if __name__ == "__main__":
    main()
