# -*- coding: utf-8 -*-
"""梦华经纬 · 论文插图生成：python tools/build_paper_figs.py
数据源（口径纪律）：docs/stats.json（tools/stats.py 产物）——凡数字出自脚本。
输出：docs/figs/fig1_layers.png · fig2_months.png · fig3_gates.png（200dpi 绢面汴青）
build_paper_pdf.py 于插图缺失时自动调用本脚本（管线可重入）。
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs", "figs")
os.makedirs(OUT, exist_ok=True)

STATS = json.load(open(os.path.join(ROOT, "docs", "stats.json"), encoding="utf-8"))

# ── 绢面汴青版式（沿站点 CSS 与 PDF 配色） ──
SILK, INK, MUTED = "#f1ecda", "#2a2620", "#8d8474"
BIAN, GOLD, GRIDC = "#3d6a7d", "#a8874a", "#ddd3b8"
plt.rcParams.update({
    "font.family": "Microsoft YaHei", "axes.unicode_minus": False,
    "figure.facecolor": SILK, "axes.facecolor": SILK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "text.color": INK,
})
KAI = FontProperties(fname=r"C:\Windows\Fonts\simkai.ttf", size=14)


def frame(ax, axis="x"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(True, axis=axis, color=GRIDC, lw=.7, alpha=.8)
    ax.set_axisbelow(True)


def fig1_layers():
    """正文三层结构 + 分卷字数（城防/街市/岁时）"""
    fig, ax = plt.subplots(figsize=(8.6, 3.6), dpi=200)
    lc = STATS["layer_chars"]
    vols = [f"卷{v}" for v in range(1, 11)]
    vals = [STATS["vol_chars"][str(v)] for v in range(1, 11)]
    colors = [GOLD if v == 1 else ("#9a6b3f" if v <= 5 else BIAN) for v in range(1, 11)]
    ax.bar(vols, vals, color=colors, width=.62,
           edgecolor="none")
    for i, v in enumerate(vals):
        ax.text(i, v + 60, f"{v:,}", ha="center", fontsize=8, color=MUTED)
    ax.set_ylabel("字数", fontproperties=KAI)
    ax.set_ylim(0, max(vals) * 1.18)
    frame(ax)
    ax.set_title(f"分卷字数：卷一城防 {lc['chengfang']:,} · 卷二至五街市 {lc['street']:,} · "
                 f"卷六至十岁时 {lc['suishi']:,}（岁时占全书 "
                 f"{round(lc['suishi'] / STATS['total_chars'] * 100)}%）",
                 fontproperties=KAI, fontsize=12.5, pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig1_layers.png"))
    plt.close(fig)


def fig2_months():
    """岁时月分布（篇幅条形，正月与十一月双峰）"""
    mc = STATS["suishi_month_chars"]
    mn = STATS["suishi_month_n"]
    months = list(range(1, 13))
    names = ["正月", "二月", "三月", "四月", "五月", "六月", "七月",
             "八月", "九月", "十月", "冬月", "腊月"]
    vals = [mc.get(str(m), 0) for m in months]
    ns = [mn.get(str(m), 0) for m in months]
    fig, ax = plt.subplots(figsize=(8.6, 3.4), dpi=200)
    ax.bar(names, vals, color=BIAN, width=.6)
    for i, (v, k) in enumerate(zip(vals, ns)):
        ax.text(i, v + 40, (f"{v:,}" if v else "未载"), ha="center", fontsize=8,
                color=INK if v else MUTED)
        if k:
            ax.text(i, v / 2, f"{k}节", ha="center", fontsize=8, color=SILK)
    ax.set_ylabel("节序篇幅（字）", fontproperties=KAI)
    ax.set_ylim(0, max(vals + [1]) * 1.2)
    frame(ax)
    ax.set_title("岁时月分布：正月（元宵灯山）与十一月（冬至郊祀）双峰，二月全书未载",
                 fontproperties=KAI, fontsize=12.5, pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_months.png"))
    plt.close(fig)


def fig3_gates():
    """城门提及 TOP12（空间书写锚）"""
    gm = sorted(STATS["gate_mentions"].items(), key=lambda kv: -kv[1])[:12][::-1]
    names = [k for k, _ in gm]
    vals = [v for _, v in gm]
    fig, ax = plt.subplots(figsize=(7.6, 4.2), dpi=200)
    ax.barh(names, vals, color="#5c5138", height=.6)
    for i, v in enumerate(vals):
        ax.text(v + .3, i, str(v), va="center", fontsize=8.5, color=MUTED)
    ax.set_xlabel("全书提及次数", fontproperties=KAI)
    ax.set_xlim(0, max(vals) * 1.12)
    frame(ax, axis="y")
    ax.set_title("城门提及 TOP12：卷二以下街市方位句的门锚（宣德楼/朱雀门/南薰门…）",
                 fontproperties=KAI, fontsize=12.5, pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig3_gates.png"))
    plt.close(fig)


if __name__ == "__main__":
    fig1_layers()
    fig2_months()
    fig3_gates()
    print("✓ docs/figs/fig1_layers.png · fig2_months.png · fig3_gates.png（数字出自 stats.json）")
