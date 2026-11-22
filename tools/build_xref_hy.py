# -*- coding: utf-8 -*-
r"""梦华经纬 · 寰宇桥构建（《太平寰宇記》開封府 ↔ 《東京夢華録》汴京对照）
姊妹站 TPHY（D:\W_A_W\TPHY）一律只读，绝不写入。
A 夢華→寰宇：以梦华门/河/地条目为目，在寰宇記卷一「開封府一」段（4,930 字）中
  机械检索对应书证句（县名/水名/城名），两句脚本截取；
B 深链：../TPHY/#zhou=開封府 ——格式实读 TPHY js/app.js fromHash 验证（q.zhou 匹配
  HY.zhou[].n 即 openZhou），并以 site_data 校验 zhou 名存在。
消歧（如实记录）：陳留縣寰宇有传而梦华全书未及；五丈河/金水河寰宇開封府一未及——
  均入 excluded，不硬凑。
输出: data/xref_hy.js —— window.MH_XREF_HY（js/stats.js「寰宇桥」页签懒加载）
"""
import io
import json
import os
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPHY = os.path.join(os.path.dirname(ROOT), "TPHY")   # D:/W_A_W/TPHY（只读）
SITE = "../TPHY/"


def sent_of(text, term, radius=52):
    """含 term 的语境片段（term 前后各 radius 字，句读处截齐）。"""
    i = text.find(term)
    if i < 0:
        return ""
    seg = text[max(0, i - radius):i + radius + len(term)]
    j = seg.find("。")
    if 0 <= j < len(seg) - 6:
        seg = seg[:j + 1]
    return seg.strip()


def main():
    if not os.path.isdir(TPHY):
        raise SystemExit("未找到姊妹站 D:/W_A_W/TPHY（寰宇桥需要其数据，只读）")

    # ── 寰宇側：卷一「開封府一」全文（data/text/henan.js，只读） ──
    ht = io.open(os.path.join(TPHY, "data", "text", "henan.js"), encoding="utf-8").read()
    s = ht[ht.find("HYTEXT["):]
    arr = json.loads(s[s.find("=") + 1:].rstrip().rstrip(";"))
    v1 = next(b for b in arr if b["v"] == 1)
    hy_text = "".join(v1["p"])
    # 深链校验：zhou 名在 TPHY site_data 存在（实读其 fromHash 逻辑的匹配集）
    t = io.open(os.path.join(TPHY, "data", "site_data.js"), encoding="utf-8").read()
    i = t.find("const HY = ")
    hy_site = json.loads(t[i + len("const HY = "):].rstrip().rstrip(";"))
    assert any(z["n"] == "開封府" for z in hy_site["zhou"]), "TPHY zhou 表缺開封府——深链将 404"

    # 梦华侧语料
    mh = "".join(io.open(os.path.join(ROOT, "data", "vol", f"{v:03d}.txt"),
                         encoding="utf-8").read() for v in range(11))

    # ── 对照条目（name, 类, 梦华检索词, 寰宇检索词, 注） ──
    PAIRS = [
        ("開封府", "府治", ["即開封府"], ["置開封府"],
         "浚儀橋西的開封府衙——寰宇記记梁開平元年（907）升汴州为東京置開封府，汉周因之"),
        ("東京·羅城", "城垣", ["東都外城方圓四十餘里"], ["建中築羅城"],
         "唐建中年间所筑罗城即五代北宋外城前身——梦华卷一所咏「方圓四十餘里」之垣"),
        ("汴河·汴水", "水道", ["中曰汴河自西亰洛口分水"], ["城臨汴水因以為名"],
         "汴州得名于汴水；通濟渠（煬帝所開）经城中而过，至宋为漕运命脉"),
        ("蔡河·陳蔡", "水道", ["自陳蔡由西南戴樓門入"], ["陳留郡之浚儀縣"],
         "蔡河自陳蔡来——寰宇所记陳留、浚儀故地皆其流域（水名在開封府一未单立）"),
        ("開封縣", "赤县", ["即開封府"], ["復置開封縣"],
         "寰宇記成書於宋初（976–987），開封縣尚未改祥符縣（大中祥符三年，1010）——两书时差之证"),
        ("浚儀縣·浚儀橋", "县·橋", ["西去曰浚儀橋"], ["立浚儀"],
         "浚儀为大梁故城所在（魏惠王徙都大梁）；梦华汴河桥谱有浚儀橋"),
        ("封邱門·封邱縣", "門·縣", ["次曰封邱門"], ["封邱縣北六十里"],
         "外城北壁封邱門（北郊御路）——寰宇封邱縣古封国之地"),
        ("夷門", "古蹟", ["州北夷門山"], ["大梁有十二門有曰夷門"],
         "大梁夷門（侯嬴所守）——唐宋城中仍有夷門山、夷門山倉，战国记忆存于宋代地名"),
        ("亰師·東京", "都名", ["卜居於州西金梁橋"], ["升為東京"],
         "梦华自序崇寧癸未「到亰師」；寰宇記「梁開平元年升為東京」——都名之谱"),
    ]

    rows, misses = [], []
    for name, kind, mh_terms, hy_terms, note in PAIRS:
        mh_q = next((q for q in mh_terms if q in mh), "")
        hy_q = next((q for q in hy_terms if q in hy_text), "")
        if not mh_q or not hy_q:
            misses.append(f"{name}: 梦华{'√' if mh_q else '×'} 寰宇{'√' if hy_q else '×'}")
            continue
        mh_sent = sent_of(mh, mh_q, 60)
        hy_sent = sent_of(hy_text, hy_q, 60)
        rows.append({
            "name": name, "k": kind, "note": note,
            "mh": mh_sent[:120], "hy": hy_sent[:120],
            "href": SITE + "#zhou=" + urllib.parse.quote("開封府"),
        })
    if misses:
        raise SystemExit("对照条目书证未双双命中，如实失败：\n" + "\n".join(misses))

    excluded = [
        {"n": "陳留縣", "why": "寰宇開封府一有傳（陳留縣東三十五里…），梦华全书未及「陳留」二字"},
        {"n": "五丈河·金水河", "why": "梦华穿城四河之二，寰宇記開封府一（卷一）未及水道分叙"},
        {"n": "祥符縣", "why": "改县名在 1010（大中祥符三年），寰宇記成書在前——桥上仍名開封縣，注于開封縣条"},
    ]

    out = {
        "site": SITE,
        "generated": "tools/build_xref_hy.py（TPHY 只读）",
        "note": "《太平寰宇記》（樂史，成書 976–987）卷一開封府与《東京夢華録》（孟元老，"
                "記崇寧—宣和，成書 1147）同写一城而相距约百五十年：寰宇記是宋初的政区地理，"
                "梦华是北宋末的风俗记忆。深链为相对兄弟路径（父目录同根服务，README 注明）。",
        "counts": [
            {"k": "对照条目", "v": len(rows)},
            {"k": "寰宇開封府一段", "v": f"{len(hy_text):,} 字"},
            {"k": "梦华全书", "v": f"{sum(len(io.open(os.path.join(ROOT, 'data/vol', f'{v:03d}.txt'), encoding='utf-8').read().replace(chr(10), '').replace('◎', '')) for v in range(11)):,} 字"},
            {"k": "深链", "v": "../TPHY/#zhou=開封府（fromHash 实读验证）"},
        ],
        "rows": rows,
        "excluded": excluded,
    }
    path = os.path.join(ROOT, "data", "xref_hy.js")
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("/* 梦华经纬 · 寰宇桥互查数据 · tools/build_xref_hy.py 生成，勿手改 */\n")
        f.write("window.MH_XREF_HY = " +
                json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")

    print(f"✓ data/xref_hy.js")
    print(f"  对照条目 {len(rows)} 对（双双书证命中）· 寰宇段 {len(hy_text):,} 字 · "
          f"排除 {len(excluded)} 项（消歧如实）")


if __name__ == "__main__":
    main()
