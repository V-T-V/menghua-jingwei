/* ═══════════ 梦华经纬 · 城图导出（CSV·BOM / KML / GeoJSON） ═══════════
   三表：城门 34 · 河道 4 · 街市 21。
   坐标口径与 tools/export_data.py 同源——一切 wgs 出自 build_data.py 管线
   （MHZ.*.wgs），前端只读不另算；示意坐标在每一行/每个要素注明 src:derived。
   经纬=示意平面锚定 WGS84（MHZ.city.anchor，量级推算），非考古实测。 */

const MHEXPORT = (() => {
  const CRSDesc = "坐标系：站内示意平面(米制)锚定WGS84·derived（量级推算）——非考古实测";

  function csvEsc(s) {
    s = String(s == null ? "" : s);
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }

  function dl(content, mime, filename) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([content], { type: mime }));
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 3000);
  }

  /* ── 表结构（列名 + 行函数）；wgs/pos/书证全出自 MHZ ── */
  const TABLES = {
    gates: {
      label: "城门", file: "梦华经纬-城门",
      head: ["名", "类", "壁", "方位侧", "书证", "全书提及", "x_m", "y_m", "lat", "lng",
             "src", "坐标依据"],
      rows: () => MHZ.gates.map(g => [
        g.name, g.wall === "大内" ? "宫门" : g.wall + "城门", g.wall, g.side,
        g.att.replace(/·/g, "；"), g.mention, g.pos[0], g.pos[1], g.wgs[0], g.wgs[1],
        "derived", "卷一城防谱+宋东京城考古常识方位（示意）"]),
    },
    rivers: {
      label: "河道", file: "梦华经纬-河道",
      head: ["名", "类", "书证", "桥数", "桥名", "走向折点数", "起点x_m", "起点y_m",
             "终点x_m", "终点y_m", "src", "坐标依据"],
      rows: () => MHZ.rivers.map(r => [
        r.name, "穿城河", r.att, r.bridges.length, r.bridges.join("、"),
        r.pts.length, r.pts[0][0], r.pts[0][1],
        r.pts[r.pts.length - 1][0], r.pts[r.pts.length - 1][1],
        "derived", "卷一河道节「穿城」记载走向示意（线层，非实测）"]),
    },
    places: {
      label: "街市", file: "梦华经纬-街市",
      head: ["名", "类", "卷", "卷部", "方位书证", "挂接块", "条目字数", "全书出场",
             "x_m", "y_m", "lat", "lng", "src", "坐标依据"],
      rows: () => MHZ.places.map(p => [
        p.name, p.cat, p.vol, VOL_NAMES[p.vol], p.att.replace(/·/g, "；"), p.jie,
        p.chars, p.mention, p.pos[0], p.pos[1], p.wgs[0], p.wgs[1], "derived",
        "原文方位句+宋东京城考古常识布点；经纬为示意平面锚定换算（推）"]),
    },
  };

  function csv(kind) {
    const t = TABLES[kind];
    const NL = String.fromCharCode(10);
    const BOM = String.fromCharCode(0xFEFF);
    const body = [t.head.join(",")].concat(
      t.rows().map(r => r.map(csvEsc).join(","))).join(NL);
    dl(BOM + body, "text/csv;charset=utf-8", t.file + ".csv");
  }

  /* ── KML / GeoJSON：三表合一（点要素 + 河道线要素） ── */
  function kml() {
    let pins = "";
    const CRS = CRSDesc;
    MHZ.gates.forEach(g => {
      pins += `<Placemark><name>${g.name}</name>` +
        `<description><![CDATA[${g.wall}城${g.side}壁 · 提及${g.mention}次 · ${g.att} · src:derived · ${CRS}]]></description>` +
        `<Point><coordinates>${g.wgs[1]},${g.wgs[0]},0</coordinates></Point></Placemark>`;
    });
    MHZ.places.forEach(p => {
      pins += `<Placemark><name>${p.name}</name>` +
        `<description><![CDATA[卷${p.vol}·${p.cat} · ${p.att} · src:derived · ${CRS}]]></description>` +
        `<Point><coordinates>${p.wgs[1]},${p.wgs[0]},0</coordinates></Point></Placemark>`;
    });
    MHZ.rivers.forEach(r => {
      const coords = r.pts.map(pt => {
        const [lat, lng] = wgsOf(pt);
        return `${lng},${lat},0`;
      }).join(" ");
      pins += `<Placemark><name>${r.name}</name>` +
        `<description><![CDATA[穿城河 · 桥${r.bridges.length}座 · ${r.att} · src:derived（走向示意线） · ${CRS}]]></description>` +
        `<LineString><coordinates>${coords}</coordinates></LineString></Placemark>`;
    });
    const k = `<?xml version="1.0" encoding="UTF-8"?>` +
      `<kml xmlns="http://www.opengis.net/kml/2.2"><Document>` +
      `<name>梦华经纬·北宋东京城示意点位与河道</name>` +
      `<description>${CRS} · ${MHZ.city.note} · ${MHZ.city.anchor.note}</description>` +
      pins + `</Document></kml>`;
    dl(k, "application/vnd.google-earth.kml+xml", "梦华经纬-城图.kml");
  }

  function wgsOf(pt) {
    const a = MHZ.city.anchor;
    const lat = a.lat0 + pt[1] / 111320;
    const lng = a.lng0 + pt[0] / (111320 * Math.cos(a.lat0 * Math.PI / 180));
    return [Math.round(lat * 1e6) / 1e6, Math.round(lng * 1e6) / 1e6];
  }

  function geojson() {
    const feats = [];
    MHZ.gates.forEach(g => feats.push({
      type: "Feature",
      geometry: { type: "Point", coordinates: [g.wgs[1], g.wgs[0]] },
      properties: { 名: g.name, 类: g.wall + "城门", 壁: g.side, 书证: g.att,
                    src: "derived", 坐标系: "示意平面(米制)锚定WGS84（量级推算，非实测）" },
    }));
    MHZ.places.forEach(p => feats.push({
      type: "Feature",
      geometry: { type: "Point", coordinates: [p.wgs[1], p.wgs[0]] },
      properties: { 名: p.name, 类: p.cat, 卷: p.vol, 书证: p.att,
                    src: "derived", 坐标系: "示意平面(米制)锚定WGS84（量级推算，非实测）" },
    }));
    MHZ.rivers.forEach(r => feats.push({
      type: "Feature",
      geometry: { type: "LineString",
                  coordinates: r.pts.map(pt => { const [la, ln] = wgsOf(pt); return [ln, la]; }) },
      properties: { 名: r.name, 类: "穿城河", 桥: r.bridges.join("、"), 书证: r.att,
                    src: "derived（走向示意线）",
                    坐标系: "示意平面(米制)锚定WGS84（量级推算，非实测）" },
    }));
    dl(JSON.stringify({ type: "FeatureCollection",
      note: "梦华经纬 · 北宋东京示意点位与河道 · tools/export_data.py 同口径可复算",
      anchor: MHZ.city.anchor, features: feats }, null, 1),
      "application/geo+json", "梦华经纬-城图.geojson");
  }

  return { csv, kml, geojson, tables: TABLES };
})();
window.MHEXPORT = MHEXPORT;
