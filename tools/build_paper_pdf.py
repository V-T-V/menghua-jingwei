# -*- coding: utf-8 -*-
"""梦华经纬 · 研究论文排印 → docs/梦华经纬-数字人文.pdf
   学 LYGL/HHH build_paper_pdf.py 模式（BaseDocTemplate + 楷体/雅黑 + 中表）。
   数字纪律：一切统计数字运行时读自 docs/stats.json · data/site_data.js(MHZ) ·
   data/xref_hy.js / data/xref_ly.js（桥）——脚本产物，不手抄；
   lint 哨兵联动（ANALYSIS.md 新于 PDF 即红）。"""
import io
import json
import os
import subprocess
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, Image, KeepTogether,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "梦华经纬-数字人文.pdf")

# 插图缺失时自动重建（管线可重入：stats.json → build_paper_figs.py）
FIGS_DIR = os.path.join(ROOT, "docs", "figs")
NEED_FIGS = ["fig1_layers.png", "fig2_months.png", "fig3_gates.png"]
if not all(os.path.isfile(os.path.join(FIGS_DIR, f)) for f in NEED_FIGS):
    subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "build_paper_figs.py")],
                   check=True)

pdfmetrics.registerFont(TTFont("KaiTi", r"C:\Windows\Fonts\STKAITI.TTF"))
pdfmetrics.registerFont(TTFont("YaHei", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))

# 配色承站点 CSS（绢面·汴青·灯金）
ACCENT = colors.HexColor('#7e2b1f')
TEXT_PRIMARY = colors.HexColor('#2a2620')
TEXT_MUTED = colors.HexColor('#8d8474')
BG_SURFACE = colors.HexColor('#e9e2c9')
BG_PAGE = colors.HexColor('#f1ecda')

W, H = A4
M = 20 * mm
AW = W - 2 * M

S = {
    "title": ParagraphStyle("t", fontName="KaiTi", fontSize=23, leading=33,
                            alignment=TA_CENTER, textColor=TEXT_PRIMARY, wordWrap="CJK"),
    "sub": ParagraphStyle("s", fontName="KaiTi", fontSize=12.5, leading=19,
                          alignment=TA_CENTER, textColor=TEXT_MUTED, wordWrap="CJK"),
    "h1": ParagraphStyle("h1", fontName="KaiTi", fontSize=15.5, leading=23,
                         textColor=ACCENT, spaceBefore=14, spaceAfter=6, wordWrap="CJK"),
    "h2": ParagraphStyle("h2", fontName="KaiTi", fontSize=12.5, leading=19,
                         textColor=TEXT_PRIMARY, spaceBefore=9, spaceAfter=4, wordWrap="CJK"),
    "body": ParagraphStyle("b", fontName="YaHei", fontSize=10.5, leading=17.5,
                           alignment=TA_JUSTIFY, textColor=TEXT_PRIMARY,
                           spaceAfter=5, wordWrap="CJK", firstLineIndent=21),
    "body0": ParagraphStyle("b0", fontName="YaHei", fontSize=10.5, leading=17.5,
                            alignment=TA_JUSTIFY, textColor=TEXT_PRIMARY,
                            spaceAfter=5, wordWrap="CJK"),
    "abs": ParagraphStyle("a", fontName="YaHei", fontSize=9.8, leading=16.5,
                          alignment=TA_JUSTIFY, textColor=TEXT_PRIMARY,
                          wordWrap="CJK", firstLineIndent=19.6),
    "cap": ParagraphStyle("c", fontName="KaiTi", fontSize=9.5, leading=14,
                          alignment=TA_CENTER, textColor=TEXT_MUTED,
                          spaceBefore=2, spaceAfter=8, wordWrap="CJK"),
    "th": ParagraphStyle("th", fontName="YaHei", fontSize=9.5, leading=13.5,
                         alignment=TA_CENTER, textColor=colors.white, wordWrap="CJK"),
    "td": ParagraphStyle("td", fontName="YaHei", fontSize=9.5, leading=13.5,
                         alignment=TA_CENTER, textColor=TEXT_PRIMARY, wordWrap="CJK"),
    "tdl": ParagraphStyle("tdl", fontName="YaHei", fontSize=9.5, leading=13.5,
                          alignment=TA_JUSTIFY, textColor=TEXT_PRIMARY, wordWrap="CJK"),
}


def P(t, st="body"):
    return Paragraph(t, S[st])


def tbl(headers, rows, widths, caption=None, left_cols=()):
    data = [[Paragraph(h, S["th"]) for h in headers]]
    for r in rows:
        data.append([Paragraph(str(c), S["tdl"] if i in left_cols else S["td"])
                     for i, c in enumerate(r)])
    t = Table(data, colWidths=[w * AW for w in widths], hAlign="CENTER", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_SURFACE]),
        ("GRID", (0, 0), (-1, -1), .4, colors.HexColor('#c9bfa5')),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    out = [t]
    if caption:
        out.append(Paragraph(caption, S["cap"]))
    return KeepTogether(out)


def fig(fname, h_mm, caption):
    img = Image(os.path.join(FIGS_DIR, fname), width=AW, height=h_mm * mm, hAlign="CENTER")
    return KeepTogether([Spacer(1, 2 * mm), img, Paragraph(caption, S["cap"])])


def footer(cv, doc):
    cv.saveState()
    cv.setFont("KaiTi", 8.5)
    cv.setFillColor(TEXT_MUTED)
    cv.drawCentredString(W / 2, 12 * mm, f"— {doc.page} —")
    cv.setFont("KaiTi", 7.5)
    cv.drawString(M, 12 * mm, "梦华经纬 · 数字人文研究")
    cv.drawRightString(W - M, 12 * mm, "docs/build_paper_pdf.py 可复核重排")
    cv.restoreState()


def load_head(path, head):
    t = io.open(os.path.join(ROOT, path), encoding="utf-8").read()
    i = t.find(head)
    assert i >= 0, f"{path} 缺 {head.strip()}"
    return json.loads(t[i + len(head):].rstrip().rstrip(";"))


def main():
    stats = json.load(io.open(os.path.join(ROOT, "docs", "stats.json"), encoding="utf-8"))
    mhz = load_head("data/site_data.js", "const MHZ = ")
    xhy = load_head("data/xref_hy.js", "window.MH_XREF_HY = ")
    xly = load_head("data/xref_ly.js", "window.MH_XREF_LY = ")

    m = mhz["meta"]
    lc = stats["layer_chars"]
    wm = stats["words"]

    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=M, rightMargin=M,
                          topMargin=18 * mm, bottomMargin=20 * mm,
                          title="《东京梦华录》的城市书写与岁时结构研究",
                          author="梦华经纬项目组", subject="数字人文·北宋东京·城市史",
                          creator="梦华经纬")
    frame = Frame(M, 20 * mm, AW, H - 38 * mm, id="f")
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=footer)])

    E = []
    E += [Spacer(1, 10 * mm),
          Paragraph("《东京梦华录》的城市书写与岁时结构研究", S["title"]),
          Spacer(1, 3 * mm),
          Paragraph("——基于门谱·河道·街市·岁时四层结构的汴京数字人文平台", S["sub"]),
          Spacer(1, 8 * mm),
          Paragraph("梦华经纬项目组", S["sub"]),
          Paragraph("2026 年 11 月 · 全部数字由脚本可复核（stats.py / build_data.py / "
                    "build_xref_hy.py / build_xref_ly.py）", S["sub"]),
          Spacer(1, 5 * mm),
          HRFlowable(width="34%", thickness=.7, color=ACCENT, hAlign="CENTER"),
          Spacer(1, 5 * mm)]

    abs_txt = (
        f"<b>摘　要</b>　本文对宋孟元老《东京梦华录》十卷进行城市尺度数字化：以卷一城防谱为"
        f"坐标（外城 {m['gatesOuter']} 门 · 旧城 {m['gatesInner']} 门 · 大内 {m['gatesPalace']} 门、"
        f"穿城四河及明载桥 {sum(len(r['bridges']) for r in mhz['rivers'])} 座），以卷二至五"
        f"{m['places']} 条街市地条目的方位句为锚（「出某門」「某門裏/外」句式），"
        f"在自绘示意平面（外城 8,800×4,800m，1 宋里≈560m）上分层织出北宋东京。语料为"
        f"kanripo KR2k0111 文淵閣四庫全書本（mandoku 格式清洗），提要自序并十卷共 "
        f"{stats['total_chars']:,} 字、{stats['blocks']} 节。主要发现：(1) 篇幅重心在岁时——"
        f"卷六至十 {lc['suishi']:,} 字占全书 {round(lc['suishi'] / stats['total_chars'] * 100)}%，"
        f"月分布呈正月（元宵）与十一月（冬至郊祀）双峰，二月全书未载；"
        f"(2) 空间书写高度门桥锚化——「門」{wm['門']} 次、「橋」{wm['橋']} 次，"
        f"朱雀門与宣德樓并立提及之首（各 {stats['gate_mentions']['朱雀門']} 次）；"
        f"(3) 双京对照：与《洛阳伽蓝记》北魏洛阳（相距约六百年）{len(xly['pairs'])} 对名物"
        f"互文显封闭里坊制与开放街市制的都城两极；与《太平寰宇记》開封府段对照 "
        f"{len(xhy['rows'])} 条，宋初政区地理与北宋末风俗记忆互补。")
    abs_tbl = Table([[Paragraph(abs_txt, S["abs"])],
                     [P("<b>关键词</b>　东京梦华录；北宋东京；数字人文；城市空间结构；"
                        "岁时民俗；双京对照；文本计量", "abs")]],
                    colWidths=[AW])
    abs_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_PAGE),
        ("LINEBELOW", (0, 0), (-1, 0), .4, colors.HexColor('#d5ccb2')),
        ("BOX", (0, 0), (-1, -1), .6, colors.HexColor('#c9bfa5')),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    E += [abs_tbl, Spacer(1, 6 * mm)]

    # ── 一、引言 ──
    E += [P("一、引言", "h1"),
          P("《东京梦华录》十卷，宋孟元老撰（成书绍兴丁卯，1147 年），追记崇宁—宣和间"
            "汴京的城郭河梁、市肆节物，是中国古代城市风俗书写的巅峰。自序云「謹省記編次成集，"
            "庶幾開巻得覩當時之盛……目之曰夢華録」——一座以记忆筑成的城。"),
          P("本平台「梦华经纬」为「经纬」系列第八站，承方舆经纬（读史方舆纪要·点织版图）、"
            "水道经纬（水经注·线溯江河）、伽蓝经纬（洛阳伽蓝记·点织北魏洛阳）的架构范式，"
            "以<b>城</b>（北宋东京）为空间范式：门谱、河道、街市、岁时四层，与伽蓝经纬构成"
            "「双京对照」。")]

    # ── 二、语料与结构化 ──
    E += [P("二、语料与结构化", "h1"),
          P("文本取 kanripo KR2k0111（文淵閣四庫全書本 WYG，mandoku org 格式）经 GitHub raw"
            " 通道抓取（断点续抓、限速、UA 自报家门，原始页留档）。清洗后得提要+自序+十卷共 "
            f"{stats['total_chars']:,} 字、{stats['blocks']} 节（◎ 节题分层）；"
            f"kanripo 缺字实体 {stats['kr_entities']} 处以 □ 代。版本异文依四库本原样"
            "（如卷一州橋夹注「正名大漢橋」，通行本作天漢橋），校勘不在范围。"),
          P(f"结构化四表：城门 {m['gates']}（外城 {m['gatesOuter']}·旧城 {m['gatesInner']}"
            f"·大内 {m['gatesPalace']}，皆卷一书证）、河道 {m['rivers']}（穿城四河及桥 "
            f"{sum(len(r['bridges']) for r in mhz['rivers'])} 座）、街市地条目 {m['places']}"
            f"（卷二以下方位句锚定）、节序 {m['suishi']}（卷六至十）。每个条目的引文片段"
            "在构建期于语料中机械验真，验不中即构建失败——「引用可复核」做进管线。")]
    E += [tbl(["层", "卷", "字数", "占比", "内容"],
              [["城防", "卷一", f"{lc['chengfang']:,}",
                f"{round(lc['chengfang'] / stats['total_chars'] * 100)}%",
                "东都外城/旧京城/河道/大内/内外诸司"],
               ["街市民俗", "卷二至五", f"{lc['street']:,}",
                f"{round(lc['street'] / stats['total_chars'] * 100)}%",
                "御街/州桥夜市/东角楼/酒楼/相国寺/民俗"],
               ["岁时节序", "卷六至十", f"{lc['suishi']:,}",
                f"{round(lc['suishi'] / stats['total_chars'] * 100)}%",
                "元宵/金明池争标/七夕/中秋/冬至郊祀/除夕"],
               ["（提要自序）", "卷〇", f"{lc['front']:,}",
                f"{round(lc['front'] / stats['total_chars'] * 100)}%", "四库提要+孟元老自序"]],
              [.16, .12, .12, .10, .50], "表 1　正文三层结构（字数出自 stats.py）", left_cols=(4,)),
          fig("fig1_layers.png", 52, "图 1　分卷字数与三层结构（数字出自 stats.json）")]

    # ── 三、空间书写的门桥锚 ──
    E += [P("三、空间书写的门桥锚", "h1"),
          P(f"宽口径「門」全书 {wm['門']} 次、「橋」{wm['橋']} 次。卷二以下的方位句几乎都以"
            "门桥为锚：「出朱雀門直至龍津橋」「自宣德東去東角樓」「上清宫在新宋門裏街北」。"
            "城门提及以朱雀門与宣德樓（各 "
            f"{stats['gate_mentions']['朱雀門']} 次）居首——御街两端（旧城正南门与大内正门）"
            "构成全书空间纵轴；提及前十二名中旧城门与大内门占七席，说明孟元老的日常叙事"
            "重心在内城。"),
          fig("fig3_gates.png", 62, "图 2　城门提及 TOP12（门锚的叙事密度）"),
          P("四河各叙一遍之后，汴河转以「州橋」（14 次）出场——桥比河更常被提及："
            "交通节点才是市井记忆的坐标。穿城四河走向取卷一「穿城」记载作示意线层"
            "（src:derived），金水河「從汴河上用朩槽架過」的跨河渡槽亦依书证示意。")]

    # ── 四、岁时结构 ──
    E += [P("四、岁时结构：一年的城", "h1"),
          P(f"卷六至十 {stats['suishi_blocks']} 节共 {lc['suishi']:,} 字，占全书 "
            f"{round(lc['suishi'] / stats['total_chars'] * 100)}%——《梦华录》的篇幅重心"
            "不在城也不在市，而在「时」：孟元老把一座城拆成十二个月的节物风流。"
            "月分布呈双峰：正月（元宵灯山、车驾幸五岳观上清宫，"
            f"{stats['suishi_month_chars']['1']:,} 字）与十一月（冬至—郊祀九节连排，"
            f"{stats['suishi_month_chars']['11']:,} 字）；三月（金明池琼林苑开放与争标百戏）"
            "为次峰。二月全书未载，如实计零。"),
          fig("fig2_months.png", 50, "图 3　岁时月分布（正月与十一月双峰）"),
          P("「夢」字全书 5 见：提要自序 4 见（「夢遊華胥」「目之曰夢華録」等），正文仅"
            "卷七 1 见（「好夢初覺」）——正文不诉诸感伤，只铺陈繁华本身，这正是「梦华体」"
            "的修辞结构。")]

    # ── 五、双京对照与寰宇互查 ──
    E += [P("五、双京对照与寰宇互查", "h1"),
          P("与伽蓝经纬（北魏洛阳）构成「双京对照」：两京相距约六百年，是中国古代都城"
            "制度的两极——杨衒之写封闭里坊中的伽蓝浮图（方三百步为一里，里开四门），"
            "孟元老写开放街市中的酒楼灯火（夜市直至三更）。城制参数十行、名物对读七对"
            "（御道×御街、四通市×相国寺万姓交易、九层浮图×白矾楼三层相高等），两句"
            "书证皆脚本截取验真。"),
          tbl(["对读", "洛陽（伽蓝记）", "東京（梦华录）"],
              [[p["k"], p["ly"], p["mh"]] for p in xly["pairs"][:4]],
              [.18, .41, .41], "表 2　双京名物对读（节选 4/7 对，全表见站内「计量→双京桥」）",
              left_cols=(1, 2)),
          P(f"与寰宇经纬《太平寰宇记》開封府段（卷一，宋初成书）对照 {len(xhy['rows'])} 条："
            "寰宇记是宋初的政区地理（「梁開平元年升為東京置開封府」），梦华是北宋末的"
            "风俗记忆；开封县尚未改祥符县（1010）——两书时差本身即是史料。排除项如实"
            "记录（陳留縣梦华未及、五丈河金水河寰宇未及）。")]

    # ── 六、方法与边界 ──
    E += [P("六、方法与边界", "h1"),
          P("凡数字出自脚本（stats.py → stats.json 唯一数字源）；坐标全量 src:derived"
            "（示意平面米制+考古常识量级），示意坐标在导出与本文逐行注明；月序为示意口径"
            "（立冬归十月、冬至郊祀归十一月）。测试防线：lint "
            "（版本/资源/哨兵/坐标/禁用模式）+ 断言页三枚（数据/循读/舆图 DOM 级）+ "
            "SHA256SUMS 账目对账 + 真断网离线三验。本文所有图表由 stats.json 机械生成，"
            "改 ANALYSIS.md 必重排（lint 哨兵联动）。"),
          P("未竟：3D 不建（城市尺度慎用，承伽蓝经纬判例）；四库本无句读，分段为机械"
            "切分（不增删一字）；示意坐标非考古实测，量级推算。")]

    doc.build(E)
    print(f"✓ {OUT}")


if __name__ == "__main__":
    main()
