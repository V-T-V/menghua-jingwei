r"""梦华经纬 · 双京桥构建（伽蓝经纬·北魏洛阳 ↔ 梦华经纬·北宋东京 对照）
姊妹站 LYGL（D:\W_A_W\LYGL）一律只读，绝不写入。
内容：
  城制参数对比（params）——外郭/内城/门数/水系/中轴/叙事单元/市制，两侧数字
    分别读各自 site_data.js（脚本产物），书证句在各自语料中机械验真；
  名物对读（pairs 7 对）——御道×御街 / 门谱 / 市 / 高层 / 池苑 / 穿城水 / 坊制，
    两句脚本截取；
  深链 ../LYGL/#m=map · #gl=永宁寺 ——格式实读 LYGL js/app.js applyHash 验证。
输出: data/xref_ly.js —— window.MH_XREF_LY（js/stats.js「双京桥」页签懒加载）
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LYGL = os.path.join(os.path.dirname(ROOT), "LYGL")   # D:/W_A_W/LYGL（只读）
SITE = "../LYGL/"


def load_const(path, const, root=None):
    t = io.open(os.path.join(root or ROOT, path), encoding="utf-8").read()
    head = f"const {const} = "
    i = t.find(head)
    assert i >= 0, f"{path} 缺 const {const}"
    return json.loads(t[i + len(head):].rstrip().rstrip(";"))


def ly_corpus():
    out = ""
    for v in range(6):
        t = io.open(os.path.join(LYGL, "data", "text", f"v{v}.js"), encoding="utf-8").read()
        i = t.find(f'[{v}]="')
        s = t[i + len(f'[{v}]="'):]
        out += json.loads('"' + s[:s.rfind('";')] + '"')
    return out


def mh_corpus():
    return "".join(io.open(os.path.join(ROOT, "data", "vol", f"{v:03d}.txt"),
                           encoding="utf-8").read() for v in range(11))


def ctx(text, term, radius=55):
    i = text.find(term)
    assert i >= 0, f"书证未命中：{term}"
    return text[max(0, i - radius):i + radius + len(term)].strip()


def main():
    if not os.path.isdir(LYGL):
        raise SystemExit("未找到姊妹站 D:/W_A_W/LYGL（双京桥需要其数据，只读）")
    ly = ly_corpus()
    mh = mh_corpus()
    qlz = load_const("data/site_data.js", "QLZ", root=LYGL)
    mhz = load_const("data/site_data.js", "MHZ")

    # ── 城制参数对比（数字读各自 site_data；文字书证在各自语料验真） ──
    params = [
        {"k": "都城时代", "ly": "北魏洛阳（494 迁都—534）", "mh": "北宋东京（960—1127）"},
        {"k": "追忆成书", "ly": "《洛阳伽蓝记》547（武定重览废寺）",
         "mh": "《东京梦华录》1147（绍兴避地追忆）"},
        {"k": "外郭", "ly": ctx(ly, "京师东西二十里", 8)[:40],
         "mh": ctx(mh, "東都外城方圓四十餘里", 8)[:30]},
        {"k": "内城", "ly": f"内城示意 {qlz['city']['wall'][2][0]-qlz['city']['wall'][0][0]:,}"
                           f"×{qlz['city']['wall'][4][1]-qlz['city']['wall'][0][1]:,}m",
         "mh": ctx(mh, "舊亰城方圓約二十里許", 8)[:20]},
        {"k": "城门", "ly": f"{qlz['meta']['gatesWall']} 墙门 + {qlz['meta']['gatesPalace']} 宫门",
         "mh": f"外城 {mhz['meta']['gatesOuter']} + 旧城 {mhz['meta']['gatesInner']}"
               f" + 宫门 {mhz['meta']['gatesPalace']}"},
        {"k": "穿城水", "ly": "洛水 / 穀水 / 阳渠", "mh": "蔡河 / 汴河 / 五丈河 / 金水河"},
        {"k": "中轴", "ly": "宣阳门—阊阖门 御道", "mh": "宣德樓—南薰門 御街（濶二百餘歩）"},
        {"k": "叙事单元", "ly": f"{qlz['meta']['templeEntries']} 伽蓝（按卷五方）",
         "mh": f"{mhz['meta']['places']} 街市地条目（+ 72 正店）"},
        {"k": "市制", "ly": ctx(ly, "方三百步为一里", 12)[:46],
         "mh": "开放坊巷·夜市（「直至三更」）"},
        {"k": "城图口径", "ly": "CRS.Simple 示意平面（米制，derived）",
         "mh": "CRS.Simple 示意平面（米制，derived）"},
    ]

    # ── 名物对读（七对，两句皆脚本截取验真） ──
    PAIRS = [
        ("中轴御道", "在宫前阊阖门南一里御道西", "坊巷御街自宣德樓一直南去約濶二百餘歩",
         "../LYGL/#m=map"),
        ("城门谱", '北头第一门曰"建春门"', "新城南壁其門有三正南門曰南薰門",
         "../LYGL/#m=map"),
        ("市易", "别立市於洛水南，号曰四通市", "相國寺毎月五次開放萬姓交易",
         "../LYGL/#m=map"),
        ("高层地标", "中有九层浮图一所，架木为之", "白礬樓後改為豐樂樓宣和間更修三層相髙",
         "../LYGL/#gl=" + "永宁寺"),
        ("池苑", "华林园中有大海，即魏天渊池", "池在順天門街北周圍約九里三十歩",
         "../LYGL/#m=map"),
        ("穿城水", "穀水周围，绕城至建春门外", "穿城河道有四南壁曰蔡河",
         "../LYGL/#m=map"),
        ("坊制", "方三百步为一里，里开四门", "坊巷以食物動使菓實柴炭之類歌呌關撲",
         "../LYGL/#m=map"),
    ]
    pairs = []
    for k, lyq, mhq, href in PAIRS:
        pairs.append({"k": k, "ly": ctx(ly, lyq)[:110], "mh": ctx(mh, mhq)[:110],
                      "href": href})
    # 深链校验：#gl=目标须在 QLZ temples 存在（LYGL applyHash 以寺名匹配）
    if any("#gl=" in p["href"] for p in pairs):
        assert any(t["name"] == "永宁寺" for t in qlz["temples"]), \
            "LYGL temples 缺永宁寺——深链将不响应"

    out = {
        "site": SITE,
        "generated": "tools/build_xref_ly.py（LYGL 只读）",
        "note": "「双京对照」——北魏洛阳与北宋东京相距约六百年，是中国古代都城制度的"
                "两极：杨衒之写封闭里坊中的伽蓝浮图，孟元老写开放街市中的酒楼灯火；"
                "一城之衰（547 重览废寺），一城之梦（1147 避地追忆）。深链为相对兄弟路径"
                "（父目录同根服务，README 注明）。",
        "counts": [
            {"k": "城制参数", "v": len(params)},
            {"k": "名物对读", "v": len(pairs)},
            {"k": "两书语料", "v": f"伽蓝 {len(ly):,} 字 / 梦华 {len(mh.replace(chr(10), '').replace('◎', '')):,} 字"},
        ],
        "params": params,
        "pairs": pairs,
    }
    path = os.path.join(ROOT, "data", "xref_ly.js")
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("/* 梦华经纬 · 双京桥对照数据 · tools/build_xref_ly.py 生成，勿手改 */\n")
        f.write("window.MH_XREF_LY = " +
                json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")

    print(f"✓ data/xref_ly.js")
    print(f"  城制参数 {len(params)} 行 · 名物对读 {len(pairs)} 对（两句语料验真）· "
          f"深链 #m=map/#gl=永宁寺（applyHash 实读验证）")


if __name__ == "__main__":
    main()
