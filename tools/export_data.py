# -*- coding: utf-8 -*-
"""梦华经纬 · 导出三表（CSV·BOM / KML / GeoJSON）→ exports/
三表：城门 34 · 河道 4 · 街市 21。与前端 js/export.js 同口径——
一切坐标出自 build_data.py 管线产物 data/site_data.js（MHZ），本脚本只读不另算；
示意坐标逐行注明 src:derived；经纬=示意平面锚定 WGS84（量级推算），非考古实测。
用法：python tools/export_data.py
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP = os.path.join(ROOT, "exports")
os.makedirs(EXP, exist_ok=True)

CRS_DESC = "坐标系：站内示意平面(米制)锚定WGS84·derived（量级推算）——非考古实测"


def load_const(path, const):
    t = io.open(os.path.join(ROOT, path), encoding="utf-8").read()
    head = f"const {const} = "
    i = t.find(head)
    assert i >= 0, f"{path} 缺 const {const}"
    return json.loads(t[i + len(head):].rstrip().rstrip(";"))


def csv_esc(s):
    s = str(s if s is not None else "")
    if any(c in s for c in ",\"\n"):
        return '"' + s.replace('"', '""') + '"'
    return s


def write_csv(name, head, rows):
    body = "\n".join([",".join(csv_esc(c) for c in head)] +
                     [",".join(csv_esc(c) for c in r) for r in rows])
    with io.open(os.path.join(EXP, name), "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(body + "\n")


def main():
    mhz = load_const("data/site_data.js", "MHZ")

    # ── 城门表 ──
    write_csv("梦华经纬-城门.csv",
              ["名", "类", "壁", "方位侧", "书证", "全书提及", "x_m", "y_m", "lat", "lng",
               "src", "坐标依据"],
              [[g["name"], g["wall"] + "城门" if g["wall"] != "大内" else "宫门", g["wall"],
                g["side"], g["att"].replace("·", "；"), g["mention"],
                g["pos"][0], g["pos"][1], g["wgs"][0], g["wgs"][1], "derived",
                "卷一城防谱+宋东京城考古常识方位（示意）"] for g in mhz["gates"]])

    # ── 河道表 ──
    write_csv("梦华经纬-河道.csv",
              ["名", "类", "书证", "桥数", "桥名", "走向折点数", "起点x_m", "起点y_m",
               "终点x_m", "终点y_m", "src", "坐标依据"],
              [[r["name"], "穿城河", r["att"], len(r["bridges"]), "、".join(r["bridges"]),
                len(r["pts"]), r["pts"][0][0], r["pts"][0][1],
                r["pts"][-1][0], r["pts"][-1][1], "derived",
                "卷一河道节「穿城」记载走向示意（线层，非实测）"] for r in mhz["rivers"]])

    # ── 街市表 ──
    vol_names = {1: "城防", 2: "街市·上", 3: "街市·下·寺市", 4: "人事·宴饮", 5: "民俗",
                 6: "正月·清明", 7: "三月·金明池", 8: "四时·下半", 9: "十月·冬至",
                 10: "郊祀·除夕"}
    write_csv("梦华经纬-街市.csv",
              ["名", "类", "卷", "卷部", "方位书证", "挂接块", "条目字数", "全书出场",
               "x_m", "y_m", "lat", "lng", "src", "坐标依据"],
              [[p["name"], p["cat"], p["vol"], vol_names.get(p["vol"], ""),
                p["att"].replace("·", "；"), p["jie"], p["chars"], p["mention"],
                p["pos"][0], p["pos"][1], p["wgs"][0], p["wgs"][1], "derived",
                "原文方位句+宋东京城考古常识布点；经纬为示意平面锚定换算（推）"]
               for p in mhz["places"]])

    # ── KML（点 55 + 线 4） ──
    anchor = mhz["city"]["anchor"]

    def wgs_of(pt):
        import math
        lat = anchor["lat0"] + pt[1] / 111320.0
        lng = anchor["lng0"] + pt[0] / (111320.0 * math.cos(math.radians(anchor["lat0"])))
        return round(lat, 6), round(lng, 6)

    pins = []
    for g in mhz["gates"]:
        pins.append(f"<Placemark><name>{g['name']}</name>"
                    f"<description><![CDATA[{g['wall']}城{g['side']}壁 · 提及{g['mention']}次 · "
                    f"{g['att']} · src:derived · {CRS_DESC}]]></description>"
                    f"<Point><coordinates>{g['wgs'][1]},{g['wgs'][0]},0</coordinates></Point></Placemark>")
    for p in mhz["places"]:
        pins.append(f"<Placemark><name>{p['name']}</name>"
                    f"<description><![CDATA[卷{p['vol']}·{p['cat']} · {p['att']} · "
                    f"src:derived · {CRS_DESC}]]></description>"
                    f"<Point><coordinates>{p['wgs'][1]},{p['wgs'][0]},0</coordinates></Point></Placemark>")
    lines = []
    for r in mhz["rivers"]:
        coords = " ".join(f"{wgs_of(pt)[1]},{wgs_of(pt)[0]},0" for pt in r["pts"])
        lines.append(f"<Placemark><name>{r['name']}</name>"
                     f"<description><![CDATA[穿城河 · 桥{len(r['bridges'])}座 · {r['att']} · "
                     f"src:derived（走向示意线） · {CRS_DESC}]]></description>"
                     f"<LineString><coordinates>{coords}</coordinates></LineString></Placemark>")
    kml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
           '<name>梦华经纬·北宋东京城示意点位与河道</name>'
           f'<description>{CRS_DESC} · {mhz["city"]["note"]} · {anchor["note"]}</description>'
           + "".join(pins) + "".join(lines) + "</Document></kml>")
    io.open(os.path.join(EXP, "梦华经纬-城图.kml"), "w", encoding="utf-8", newline="\n").write(kml)

    # ── GeoJSON（59 要素） ──
    feats = []
    for g in mhz["gates"]:
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [g["wgs"][1], g["wgs"][0]]},
                      "properties": {"名": g["name"], "类": g["wall"] + "城门", "壁": g["side"],
                                     "书证": g["att"], "src": "derived",
                                     "坐标系": "示意平面(米制)锚定WGS84（量级推算，非实测）"}})
    for p in mhz["places"]:
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [p["wgs"][1], p["wgs"][0]]},
                      "properties": {"名": p["name"], "类": p["cat"], "卷": p["vol"],
                                     "书证": p["att"], "src": "derived",
                                     "坐标系": "示意平面(米制)锚定WGS84（量级推算，非实测）"}})
    for r in mhz["rivers"]:
        feats.append({"type": "Feature",
                      "geometry": {"type": "LineString",
                                   "coordinates": [[wgs_of(pt)[1], wgs_of(pt)[0]] for pt in r["pts"]]},
                      "properties": {"名": r["name"], "类": "穿城河",
                                     "桥": "、".join(r["bridges"]), "书证": r["att"],
                                     "src": "derived（走向示意线）",
                                     "坐标系": "示意平面(米制)锚定WGS84（量级推算，非实测）"}})
    gj = {"type": "FeatureCollection",
          "note": "梦华经纬 · 北宋东京示意点位与河道 · js/export.js 同口径可复算",
          "anchor": anchor, "features": feats}
    io.open(os.path.join(EXP, "梦华经纬-城图.geojson"), "w", encoding="utf-8", newline="\n"
            ).write(json.dumps(gj, ensure_ascii=False, indent=1))

    n_pts = len(mhz["gates"]) + len(mhz["places"])
    print(f"✓ exports/：城门 34 · 河道 4 · 街市 21 CSV（BOM）· "
          f"KML 点 {len(pins)} 线 {len(lines)} · GeoJSON {len(feats)} 要素（全部注明 derived）")


if __name__ == "__main__":
    main()
