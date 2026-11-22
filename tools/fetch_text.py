# -*- coding: utf-8 -*-
"""梦华经纬 · Phase 0 文本抓取（东京梦华录 · kanripo KR2k0111 四库本）
数据源: https://raw.githubusercontent.com/kanripo/KR2k0111/master/KR2k0111_NNN.txt
        kanripo = 汉籍リポ（Kanseki Repository）镜像仓（GitHub raw 通道——
        被墙环境下的救命通道，METHOD §一之「数据源侦察」）；
        底本 = 文淵閣四庫全書本（WYG），mandoku org 格式。
输出:   data_raw/KR2k0111_NNN.txt  原始页（mandoku 原样留档，供复查）
        data/vol/NNN.txt           每卷纯净 UTF-8 文本（节标题以 ◎ 前缀，段以 \n 分隔）
        data/fetch_report.json     字数/段落数盘点
用法:   python tools/fetch_text.py          # 断点续抓（已存在且非空则跳过）
        python tools/fetch_text.py --force # 全部重抓
纪律:   UA 自报家门 · 每页 ≥1s 限速 · 原始页留档 · 重试 3 次
"""
import json
import os
import re
import sys
import time
import urllib.request

# 本机 Windows 残留死代理（127.0.0.1:58319 拒连，承姊妹站 fetch 实录）——直连可用，
# 无代理 opener 绕过系统代理设置。
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

BASE = "https://raw.githubusercontent.com/kanripo/KR2k0111/master"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data_raw")
VOL_DIR = os.path.join(ROOT, "data", "vol")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(VOL_DIR, exist_ok=True)

HEADERS = {
    # UA 自报家门（ASCII：DongjingMenghualu = 东京梦华录数字人文站建站抓取）
    "User-Agent": "JingweiDigitalHumanities/0.1 (DongjingMenghualu-DH-site build; "
                  "academic use; resumable fetch; one-shot batch)",
}

# 000=自序 001..010=卷一..卷十
PAGES = {"000": "自序"}
for v in range(1, 11):
    PAGES[f"{v:03d}"] = f"卷{ '一二三四五六七八九十'[v - 1] }"

NOISE_RE = re.compile(
    r"^(#|<pb:|\s*$|欽定四庫全書|^　?(東京|東亰)夢華[録錄]|"
    r"　*總纂官|　*總　校　官|　*校　官)"
)
KR_ENTITY = re.compile(r"&KR\d+;")
JUAN_MARK = re.compile(r"^#\+PROPERTY:\s*JUAN\s+(.+)$")


def clean_mandoku(text: str) -> str:
    """mandoku org → 纯正文：
    · 剥 # 头 / <pb:> 页码 / 撰人衔名行 / 库页题签行
    · 去行尾 ¶（分页处的 ¶ 连排断词直接并回）
    · 节标题（全角双空格前缀）→ 「◎标题」独立行；
      000 卷内 #+PROPERTY: JUAN 提要/自序 分界 → ◎提要 / ◎自序
    · kanripo 缺字实体 &KRxxxx; → □（计数见 fetch_report）
    · 正文按原行合并为节内连续段（kanripo 行=刻本行，非句段）"""
    out = []
    n_kr = 0
    for raw in text.split("\n"):
        ln = raw.rstrip("\r")
        ln = ln.replace("¶", "")
        jm = JUAN_MARK.match(ln)
        if jm:
            juan_name = jm.group(1).strip()
            if juan_name in ("提要", "自序"):
                out.append("◎" + juan_name)
            continue
        if NOISE_RE.match(ln):
            continue
        n_kr += len(KR_ENTITY.findall(ln))
        ln = KR_ENTITY.sub("□", ln)
        ln = ln.strip("\u3000").strip()
        if not ln:
            continue
        if raw.startswith("\u3000\u3000") and len(ln) <= 30 and not raw.startswith("\u3000\u3000\u3000"):
            out.append("◎" + ln)          # 节标题
        elif re.match(r"^◎", ln):
            out.append("◎" + ln.lstrip("◎"))
        else:
            out.append(ln)
    # 合并：◎ 行独立成段；其余行按相邻同类拼接（kanripo 每刻本行一连）
    body = []
    for ln in out:
        if ln.startswith("◎"):
            if body and body[-1] == ln:   # JUAN 分界与节标题行重复（如 ◎提要×2）去重
                continue
            body.append(ln)
        elif body and not body[-1].startswith("◎"):
            body[-1] += ln
        else:
            body.append(ln)
    return "\n".join(body), n_kr


def fetch_one(num: str, force: bool) -> dict:
    txt_path = os.path.join(VOL_DIR, f"{num}.txt")
    raw_path = os.path.join(RAW_DIR, f"KR2k0111_{num}.txt")
    if not force and os.path.exists(txt_path) and os.path.getsize(txt_path) > 200:
        with open(txt_path, encoding="utf-8") as f:
            body = f.read()
        return {"num": num, "title": PAGES[num], "chars": len(body.replace("\n", "").replace("◎", "")),
                "sects": body.count("\n◎") + (1 if body.startswith("◎") else 0),
                "cached": True}
    url = f"{BASE}/KR2k0111_{num}.txt"
    if os.path.exists(raw_path) and os.path.getsize(raw_path) > 2000:
        with open(raw_path, encoding="utf-8") as f:
            raw_txt = f.read()
    else:
        raw_txt = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with OPENER.open(req, timeout=40) as r:
                    raw_txt = r.read().decode("utf-8")
                break
            except Exception as e:
                if attempt == 2:
                    raise
                print(f"  重试 {num}: {e}")
                time.sleep(4 * (attempt + 1))
        with open(raw_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(raw_txt)      # 原始 mandoku 页留档供复查
    body, n_kr = clean_mandoku(raw_txt)
    if len(body) < 300:
        raise RuntimeError(f"{num} 清洗后仅 {len(body)} 字，疑似版式变化，请人工检查 {raw_path}")
    with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    return {"num": num, "title": PAGES[num], "chars": len(body.replace("\n", "").replace("◎", "")),
            "sects": body.count("\n◎") + (1 if body.startswith("◎") else 0),
            "krEntities": n_kr, "cached": False}


def main():
    force = "--force" in sys.argv
    report = []
    for num in sorted(PAGES):
        info = fetch_one(num, force)
        tag = "缓存" if info["cached"] else "抓取"
        print(f"[{tag}] {num} {info['title']}  {info['chars']:>6} 字  {info['sects']:>3} 节")
        report.append(info)
        if not info["cached"]:
            time.sleep(1.2)   # 礼貌限速
    total = sum(r["chars"] for r in report)
    out = {"source": BASE,
           "source_note": "kanripo KR2k0111（文淵閣四庫全書本 WYG，mandoku org 格式）via GitHub raw；"
                          "GB 无转换（源即 UTF-8）；维基文库本未另行核校，版本性质见 README",
           "vols": report, "total_chars": total,
           "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(os.path.join(ROOT, "data", "fetch_report.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\n合计 {total} 字（自序 + 十卷）→ data/fetch_report.json")


if __name__ == "__main__":
    main()
