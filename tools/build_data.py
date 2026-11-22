# -*- coding: utf-8 -*-
"""梦华经纬 · Phase 2 构建（管线可重入：改本文件后重跑即得全部前端数据）
输入: data/intermediate/entries.json + data/vol/*.txt + docs/stats.json
输出: data/site_data.js  (MHZ: 城市骨架 + 城门/河道/街市 + meta)
      data/sections.js   (MH_SECTIONS: 循读阅读块)
      data/stats.js      (MH_STATS ← docs/stats.json 转抄，前端只读脚本产物)
      data/text/v0..v10.js (MHTEXT: 全文检索层，纯正文口径)
坐标: 示意城市平面 CRS（米）。原点=外城西南角，x 东 y 北。
      外城 8,800×4,800m（周回 27.2km——四库本「方圓四十餘里」量级，1宋里≈560m）；
      旧城 3,600×2,900m（「方圓約二十里許」）；大内 1,400×1,150m。
      门/街市布点=卷一城防谱 + 卷二以下方位句 + 宋东京考古常识量级，全部 src:"derived"。
书证纪律: 每个 att 引文片段（以 · 分隔）逐一在语料中验证存在，验不中即构建失败。
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INT = os.path.join(ROOT, "data", "intermediate", "entries.json")

# WGS84 锚点（导出 KML/GeoJSON/CSV 用；前后端同口径，勿单侧改动）：
#   外城西南角(0,0) → 约 34.7784N, 114.2618E（北宋东京外城遗址量级推算，
#   与寰宇经纬開封府条 c=[34.8,114.31] 同一量级）；conf:infer。
#   换算：lat = lat0 + y/111320；lng = lng0 + x/(111320·cos(lat0·π/180))
ANCHOR = {"lat0": 34.7784, "lng0": 114.2618,
          "note": "示意平面锚定WGS84：外城西南角→34.7784N,114.2618E（北宋东京外城遗址量级推算infer）；"
                  "lat=lat0+y/111320，lng=lng0+x/(111320·cos(lat0))"}


def to_wgs(x, y):
    lat = ANCHOR["lat0"] + y / 111320.0
    lng = ANCHOR["lng0"] + x / (111320.0 * math.cos(math.radians(ANCHOR["lat0"])))
    return round(lat, 6), round(lng, 6)


W, H = 8800, 4800       # 外城
IW = [(2300, 1400), (5900, 4300)]   # 旧城 rect（x0,y0,x1,y1 拆用）
DW = [(3700, 2950), (5100, 4100)]   # 大内 rect

CITY = {
    "crs": "simple-m",
    "li_m": 560,
    "note": "示意城市平面（米）：外城8,800×4,800（周回约48宋里，四库本「方圓四十餘里」量级），"
            "旧城3,600×2,900（「方圓約二十里許」），大内1,400×1,150；布点依卷一城防谱+卷二以下方位句"
            "+宋东京城考古常识量级，全部坐标 src:derived",
    "anchor": ANCHOR,
    "waicheng": [[0, 0], [8800, 0], [8800, 4800], [0, 4800], [0, 0]],
    "jiucheng": [[2300, 1400], [5900, 1400], [5900, 4300], [2300, 4300], [2300, 1400]],
    "danei": [[3700, 2950], [5100, 2950], [5100, 4100], [3700, 4100], [3700, 2950]],
    "yujie": [[4400, 2950], [4400, 0]],
    "waicheng_att": "卷一「東都外城方圓四十餘里城濠曰護龍河濶十餘丈」",
    "jiucheng_att": "卷一「舊亰城方圓約二十里許」",
    "danei_att": "卷一「大内正門宣德樓列五門」·卷二「坊巷御街自宣德樓一直南去約濶二百餘歩」",
}

# ── 城门（wall: 外城/舊城/大内；pos=示意；att=书证片段·分隔，逐段验真）──
GATES = [
    # 外城·南壁（书证皆卷一《東都外城》节）
    ("南薰門", "外城", "南", [4400, 0], "城門皆甕城三層屈曲開門唯南薰門新鄭門新宋門封邱門皆直門兩重盖此係四正門皆留御路故也·新城南壁其門有三正南門曰南薰門"),
    ("陳州門", "外城", "南", [6600, 0], "城南一邊東南則陳州門傍有蔡河水門"),
    ("戴樓門", "外城", "南", [2200, 0], "西南則戴樓門傍亦有蔡河水門"),
    # 外城·東壁
    ("東水門", "外城", "東", [8800, 2200], "東南曰東水門乃汴河下流水門也其門跨河有鐵褁牕門遇夜如閘垂下水面"),
    ("新宋門", "外城", "東", [8800, 3000], "次則曰新宋門"),
    ("新曹門", "外城", "東", [8800, 3800], "次曰新曹門又次曰東北水門乃五丈河之水門也"),
    ("東北水門", "外城", "東", [8800, 4400], "又次曰東北水門乃五丈河之水門也"),
    # 外城·西壁（從南序）
    ("新鄭門", "外城", "西", [0, 1900], "從南曰新鄭門·諸門名皆俗呼其正名如西水門曰利澤鄭門本順天門固子門本金耀門"),
    ("西水門", "外城", "西", [0, 2250], "次曰西水門汴河上水門也"),
    ("萬勝門", "外城", "西", [0, 2900], "次曰萬勝門"),
    ("固子門", "外城", "西", [0, 3500], "又次曰固子門"),
    ("西北水門", "外城", "西", [0, 4300], "又次曰西北水門乃金水河水門也"),
    # 外城·北壁
    ("陳橋門", "外城", "北", [6600, 4800], "北城一邊其門有四從東曰陳橋門"),
    ("封邱門", "外城", "北", [4400, 4800], "次曰封邱門"),
    ("新酸棗門", "外城", "北", [2800, 4800], "次曰新酸棗門"),
    ("衛州門", "外城", "北", [1400, 4800], "次曰衛州門"),
    # 旧城（书证皆卷一《舊亰城》节）
    ("朱雀門", "舊城", "南", [4400, 1400], "南壁其門有三正南曰朱雀門"),
    ("保康門", "舊城", "南", [5000, 1400], "左曰保康門"),
    ("新門", "舊城", "南", [3800, 1400], "右曰新門"),
    ("汴河南岸角門子", "舊城", "東", [5900, 2300], "東壁其門有三從南汴河南岸角門子"),
    ("舊宋門", "舊城", "東", [5900, 2650], "河北岸曰舊宋門"),
    ("舊曹門", "舊城", "東", [5900, 3250], "次曰舊曹門"),
    ("舊鄭門", "舊城", "西", [2300, 2350], "西壁其門有三從南曰舊鄭門"),
    ("汴河北岸角門子", "舊城", "西", [2300, 2500], "次汴河北岸角門子"),
    ("梁門", "舊城", "西", [2300, 3100], "次曰梁門"),
    ("舊封邱門", "舊城", "北", [5600, 4300], "北壁其門有三從東曰舊封邱門"),
    ("景龍門", "舊城", "北", [3800, 4300], "次曰景龍門(乃大内城角/實籙宫前也)"),
    ("金水門", "舊城", "北", [2900, 4300], "次曰金水門"),
    # 大内（书证皆卷一《大内》节）
    ("宣德樓", "大内", "南", [4400, 2950], "大内正門宣德樓列五門門皆金釘朱漆"),
    ("左掖門", "大内", "南", [3950, 2950], "宣德樓左曰左掖門右曰右掖門"),
    ("右掖門", "大内", "南", [4850, 2950], "宣德樓左曰左掖門右曰右掖門"),
    ("東華門", "大内", "東", [5100, 3550], "殿前東西大街東出東華門西出西華門"),
    ("西華門", "大内", "西", [3700, 3550], "殿前東西大街東出東華門西出西華門"),
    ("拱辰門", "大内", "北", [4400, 4100], "後門曰拱辰門"),
]

# ── 河道（穿城四河；pts=走向示意，att=原文书证；bridges=原文明载桥名清单）──
RIVERS = [
    {"name": "汴河", "key": "bian",
     "pts": [[-1500, 2150], [-600, 2200], [0, 2250], [900, 2300], [1800, 2360],
             [2300, 2400], [3100, 2420], [3700, 2410], [4400, 2400], [5000, 2430],
             [5900, 2450], [7000, 2350], [8800, 2200], [9600, 2150]],
     "att": "中曰汴河自西亰洛口分水入亰城東去至泗州入淮運東南之糧凡東南方物自此入亰城公私仰給焉",
     "bridges": ["虹橋", "順成倉橋", "便橋", "下土橋", "上土橋", "相國寺橋", "州橋",
                 "浚儀橋", "興國寺橋", "太師府橋", "金梁橋", "西浮橋", "西水門便橋"],
     "batt": "河上有橋十三從東水門外七里曰虹橋其橋無柱皆以巨朩虛架餙以丹艧宛如飛虹"},
    {"name": "蔡河", "key": "cai",
     "pts": [[-500, -350], [900, -150], [2200, 0], [3000, 320], [3600, 520],
             [4400, 700], [5100, 560], [5800, 300], [6600, 0], [7300, -400], [7900, -800]],
     "att": "穿城河道有四南壁曰蔡河自陳蔡由西南戴樓門入亰城遼繞自東南陳州門出",
     "bridges": ["觀橋", "宣泰橋", "雲騎橋", "横橋子", "高橋", "西保康門橋", "龍津橋",
                 "新橋", "太平橋", "糶麥橋", "宜男橋"],
     "batt": "蔡河正名惠民河為通蔡州故也·河上有橋十一"},
    {"name": "五丈河", "key": "wuzhang",
     "pts": [[9800, 4480], [8800, 4400], [7600, 4360], [6200, 4320], [4700, 4280],
             [3200, 4240], [1600, 4200], [0, 4150], [-900, 4110]],
     "att": "東北曰五丈河來自濟鄆般挽亰東路糧斛入亰城自新曹門北入亰",
     "bridges": ["小横橋", "廣備橋", "蔡市橋", "青暉橋", "染院橋"],
     "batt": "河上有橋五東去曰小横橋次曰廣備橋"},
    {"name": "金水河", "key": "jinshui",
     "pts": [[-2600, 2750], [-1800, 2400], [-1100, 2180], [-500, 2450], [-200, 3200],
             [0, 4300], [600, 4380], [1600, 4340], [2500, 4200], [3300, 4000],
             [3900, 3800], [4100, 3600]],
     "att": "西北曰金水河自亰城西南分亰索河水築堤從汴河上用朩槽架過從西北水門入亰城夾墻遮擁入大内灌後苑池浦矣",
     "bridges": ["白虎橋", "横橋", "五王宫橋"],
     "batt": "河上有橋三曰白虎橋横橋五王宫橋之類"},
]

# ── 街市地条目（cat 着色分类；vol=所在卷；att 片段验真；conf: text=有明载方位句）──
PLACES = [
    ("御街", "御路", 2, [4400, 1500], "v2-00",
     "坊巷御街自宣德樓一直南去約濶二百餘歩兩邊乃御廊"),
    ("州橋", "橋", 1, [4400, 2400], "v1-02",
     "次曰州橋(正名大漢橋)·正對於大内御街其橋與相國寺橋皆低平不通舟船"),
    ("龍津橋", "橋", 1, [4400, 700], "v1-02",
     "次曰龍津橋(正對/内前)"),
    ("虹橋", "橋", 1, [9800, 2130], "v1-02",
     "從東水門外七里曰虹橋其橋無柱皆以巨朩虛架"),
    ("州橋夜市", "夜市", 2, [4400, 1550], "v2-03",
     "出朱雀門直至龍津橋·謂之雜嚼直至三更"),
    ("東角樓街巷", "街市", 2, [5050, 2800], "v2-04",
     "自宣德東去東角樓乃皇城東南角也·最是鋪席要閙宣和間展夾城牙道矣"),
    ("潘樓街", "街市", 2, [5500, 2900], "v2-04",
     "以東街北曰潘樓酒店其下毎日自五更市合買賣衣物書畫珍玩犀玉"),
    ("界身巷", "金銀市", 2, [5480, 2755], "v2-04",
     "南通一巷謂之界身並是金銀綵帛交易之所·毎一交易動即千萬駭人聞見"),
    ("桑家瓦子", "瓦子", 2, [5700, 2620], "v2-04",
     "街南桑家瓦子近北則中瓦次𠂻瓦其中大小勾欄五十餘座"),
    ("土市子", "街市", 2, [6050, 2750], "v2-05",
     "潘樓東去十字街謂之土市子又謂之竹竿市·至曉即散謂之鬼市子"),
    ("馬行街", "街市", 2, [5800, 3350], "v2-05",
     "土市北去乃馬行街也人煙浩閙·馬行北去乃小貨行時樓大骨傅藥鋪直抵正係舊封邱門"),
    ("白礬樓", "酒樓", 2, [6250, 3450], "v2-06",
     "白礬樓後改為豐樂樓宣和間更修三層相髙五樓相向各有飛橋欄檻明暗相通"),
    ("大相國寺", "寺市", 3, [5250, 2700], "v3-03",
     "大相國寺直至十三間樓舊宋門·相國寺毎月五次開放萬姓交易"),
    ("上清宫", "宫觀", 3, [8300, 3150], "v3-05",
     "上清宫在新宋門裏街北"),
    ("開封府", "衙署", 2, [3900, 2320], "v2-01",
     "至浚儀橋之西即開封府"),
    ("景靈東宫", "宫宇", 2, [5050, 2730], "v2-01",
     "御街大内前南去左則景靈東宫右則西宫"),
    ("景靈西宫", "宫宇", 2, [3750, 2730], "v2-01",
     "御街大内前南去左則景靈東宫右則西宫"),
    ("太學國子監", "學館", 2, [4550, 550], "v2-02",
     "過龍津橋南去路心又設朱漆□子如内前·以南太學國子監"),
    ("五嶽觀", "宫觀", 2, [4250, 900], "v2-02",
     "御街至南薫門裏街西五嶽觀最為雄壯"),
    ("金明池", "池苑", 7, [-1400, 2150], "v7-00",
     "三月一日州西順天門外開金明池瓊林苑·池在順天門街北周圍約九里三十歩"),
    ("瓊林苑", "池苑", 7, [-1400, 1550], "v7-02",
     "駕方幸瓊林苑在順天門大街面北與金明池相對"),
]

# ── 岁时节序月序（卷六至十各节 → 农历月；timeline 排序用，示意口径）──
SUISHI_MONTH = {
    "正月": 1, "元旦朝㑹": 1, "立春": 1, "元宵": 1,
    "十四日車駕幸五嶽觀": 1, "十五日駕詣上清宫": 1, "十六日": 1, "收燈都人出城採春": 1,
    "清明節": 3,
    "三月一日開金明池瓊林苑": 3, "駕幸臨水殿觀爭標錫宴": 3, "駕幸瓊林苑": 3,
    "駕幸寳津樓宴殿": 3, "駕登寳津樓諸軍呈百戲": 3, "駕幸射殿射弓": 3,
    "池苑内縱人關撲遊戲": 3, "駕回儀衛": 3,
    "四月八日": 4, "端午": 5,
    "六月六日崔府君生日二十四日神保觀神生日": 6, "是月巷陌雜賣": 6,
    "七夕": 7, "中元節": 7, "立秋": 7, "秋社": 8, "中秋": 8, "重陽": 9,
    "十月一日": 10, "天寜節": 10, "宰執親王宗室百官入内上夀": 10,
    "立冬": 10, "冬至": 11,
    "大禮預教車象": 11, "車駕宿大慶殿": 11, "駕行儀衛": 11,
    "駕宿太廟奉神主出室": 11, "駕詣青城齋宫": 11, "駕詣郊壇行禮": 11,
    "郊畢駕囬": 11, "下赦": 11, "駕還詣諸宫行謝": 11,
    "十二月": 12, "除夕": 12,
}


def load_entries():
    return json.load(open(INT, encoding="utf-8"))


def corpus_all():
    return "".join(open(os.path.join(ROOT, "data", "vol", f"{v:03d}.txt"),
                        encoding="utf-8").read() for v in range(11))


def check_quotes(corpus, problems):
    """att 片段（· 分隔，可含 (夹注)）逐段验真。
    归一化：剥括号与括内换行斜杠（mandoku 夹注以 (…/…) 连写）——两侧同法，
    夹注内容保留参与比对（如「諸門名皆俗呼…」全句原在夹注内）。"""
    def norm(s):
        return s.replace("(", "").replace(")", "").replace("/", "")

    corpus_n = norm(corpus)

    def verify(att, owner):
        for frag in att.split("·"):
            frag2 = norm(frag)
            if frag2 and frag2 not in corpus_n:
                problems.append(f"{owner} 书证片段未命中语料：{frag2[:30]}…")

    for g in GATES:
        verify(g[4], f"城门「{g[0]}」")
    for r in RIVERS:
        verify(r["att"], f"河道「{r['name']}」")
        verify(r["batt"], f"河道「{r['name']}」桥证")
        for b in r["bridges"]:
            if b not in corpus:
                problems.append(f"河道「{r['name']}」桥名未命中语料：{b}")
    for p in PLACES:
        verify(p[5], f"街市「{p[0]}」")
    for name in SUISHI_MONTH:
        if f"◎{name}" not in corpus:
            problems.append(f"节序「{name}」未命中节标题")


def main():
    ent = load_entries()
    blocks = ent["blocks"]
    corpus = corpus_all()
    problems = []
    check_quotes(corpus, problems)

    by_id = {b["id"]: b for b in blocks}
    for _n, _c, _v, _p, jid, _a in PLACES:
        if jid not in by_id:
            problems.append(f"街市「{_n}」挂接块 {jid} 不存在")
        elif by_id[jid]["vol"] != _v:
            problems.append(f"街市「{_n}」vol={_v} 与块 {jid} vol={by_id[jid]['vol']} 不符")

    # 城门/街市提及计数（全书出场）
    def mention(name):
        return corpus.count(name)

    gates_out = []
    for name, wall, side, pos, att in GATES:
        lat, lng = to_wgs(*pos)
        gates_out.append({"name": name, "wall": wall, "side": side, "pos": pos,
                          "wgs": [lat, lng], "att": att, "src": "derived",
                          "mention": mention(name)})

    rivers_out = []
    for r in RIVERS:
        rivers_out.append({
            "name": r["name"], "key": r["key"], "pts": r["pts"], "att": r["att"],
            "bridges": r["bridges"], "batt": r["batt"], "src": "derived",
            "mention": mention(r["name"]),
        })

    places_out = []
    for i, (name, cat, vol, pos, jid, att) in enumerate(PLACES):
        lat, lng = to_wgs(*pos)
        places_out.append({"id": f"p{i + 1:02d}", "name": name, "cat": cat, "vol": vol,
                           "pos": pos, "wgs": [lat, lng], "att": att, "src": "derived",
                           "conf": "text", "jie": jid, "chars": by_id[jid]["chars"],
                           "mention": mention(name)})

    suishi_out = []
    for b in blocks:
        if b["kind"] == "suishi":
            if b["name"] not in SUISHI_MONTH:
                problems.append(f"节序「{b['name']}」缺月序定义")
                continue
            suishi_out.append({"id": b["id"], "name": b["name"], "vol": b["vol"],
                               "month": SUISHI_MONTH[b["name"]], "chars": b["chars"]})

    stats = json.load(open(os.path.join(ROOT, "docs", "stats.json"), encoding="utf-8"))
    meta = {
        "title": "東京夢華録", "author": "宋·孟元老",
        "vols": 10, "version": "1",
        "totalChars": ent["meta"]["totalChars"],
        "blocks": len(blocks),
        "gates": len(gates_out),
        "gatesOuter": sum(1 for g in gates_out if g["wall"] == "外城"),
        "gatesInner": sum(1 for g in gates_out if g["wall"] == "舊城"),
        "gatesPalace": sum(1 for g in gates_out if g["wall"] == "大内"),
        "rivers": len(rivers_out),
        "places": len(places_out),
        "suishi": len(suishi_out),
        "krEntities": sum(v.get("krEntities", 0) for v in
                          json.load(open(os.path.join(ROOT, "data", "fetch_report.json"),
                                         encoding="utf-8"))["vols"]),
        "source": "kanripo KR2k0111（文淵閣四庫全書本 WYG，mandoku org 格式）via GitHub raw",
    }
    mh = {"meta": meta, "city": CITY, "gates": gates_out,
          "rivers": rivers_out, "places": places_out, "suishi": suishi_out}

    def dump(path, head, obj):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"/* 梦华经纬 · {head} · tools/build_data.py 生成，勿手改 */\n")
            f.write("const " + head.split(" ")[0] + " = " +
                    json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";\n")

    dump(os.path.join(ROOT, "data", "site_data.js"), "MHZ", mh)

    # sections.js（阅读块；ord=原序）
    secs = {}
    for i, b in enumerate(blocks):
        secs[b["id"]] = {"id": b["id"], "ord": i, "name": b["name"], "vol": b["vol"],
                         "kind": b["kind"], "chars": b["chars"], "paras": b["paras"]}
    dump(os.path.join(ROOT, "data", "sections.js"), "MH_SECTIONS", secs)

    # stats.js（前端只读脚本产物）
    dump(os.path.join(ROOT, "data", "stats.js"), "MH_STATS", stats)

    # text/v0..v10.js（全文检索层，与 data/vol/NNN.txt 同口径）
    for v in range(11):
        txt = open(os.path.join(ROOT, "data", "vol", f"{v:03d}.txt"),
                   encoding="utf-8").read()
        with open(os.path.join(ROOT, "data", "text", f"v{v}.js"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(f"/* 梦华经纬 · 卷{v} · 懒加载 */\n")
            f.write(f"(window.MHTEXT=window.MHTEXT||{{}})[{v}]=" +
                    json.dumps(txt, ensure_ascii=False) + ";\n")

    if problems:
        raise SystemExit("书证/挂接验证失败：\n" + "\n".join(problems[:30]))
    print(f"✓ site_data.js：门 {len(gates_out)}（外{meta['gatesOuter']}/舊{meta['gatesInner']}"
          f"/大内{meta['gatesPalace']}）· 河 {len(rivers_out)} · 街市 {len(places_out)}"
          f" · 节序 {len(suishi_out)}")
    print(f"✓ sections.js {len(secs)} 块 · stats.js · text/v0..v10.js · 书证全部验真")


if __name__ == "__main__":
    main()
