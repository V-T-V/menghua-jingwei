/* ═══════════ 梦华经纬 · 汴京舆图（L.CRS.Simple 示意平面） ═══════════
   外城/旧城/大内三层城垣 · 御街轴线 · 穿城四河（线层）· 城门符号（分级）
   · 街市点（按类着色，径=条目字数量级）· 分层开关（城垣/城门/河道/街市）
   坐标=build_data.py 示意米制（x 东 y 北）；传 Leaflet 用 [y, x] */

const MHMAP = (() => {
  let map, selId = null, hlId = null;
  let onPlace = null, onGate = null, onRiver = null;
  const layers = {};          /* wall/gate/river/place/focus */
  const visible = { wall: true, gate: true, river: true, place: true };

  const ll = p => [p[1], p[0]];                       /* [x,y] → latLng */
  const catColor = c => CAT_COLORS[c] || "#8e2b22";
  const radiusOf = p => Math.max(6, Math.min(16, Math.sqrt((p.chars || 300) / 22)));

  function init() {
    map = L.map("map", {
      crs: L.CRS.Simple,
      attributionControl: false, zoomControl: true,
      minZoom: MH_CONF.minZoom, maxZoom: MH_CONF.maxZoom,
      zoomSnap: 0.25, zoomDelta: 0.5,
      center: ll(MH_CONF.homeView.center), zoom: MH_CONF.homeView.zoom,
      maxBounds: L.latLngBounds(ll([-3200, -1700]), ll([10600, 5400])),
      maxBoundsViscosity: .7,
    });
    ["wall", "gate", "river", "place", "focus"].forEach(k => {
      layers[k] = L.layerGroup().addTo(map);
    });
    renderCity();
    renderGates();
    renderRivers();
    renderPlaces();
  }

  /* ── 城市骨架（城垣层） ── */
  function renderCity() {
    const c = MHZ.city;
    L.polygon(c.waicheng.map(ll), { className: "wallface", color: "#9a8f6d", weight: 3.4,
      fill: true, fillColor: "#efe9d2", fillOpacity: .28 })
      .bindTooltip(`外城（新城）· ${c.waicheng_att}`, { direction: "top", sticky: true })
      .addTo(layers.wall);
    L.polygon(c.jiucheng.map(ll), { className: "innerface", color: "#6e5a35", weight: 2.4,
      fillColor: "#efe9d2", fillOpacity: .4 })
      .bindTooltip(`旧京城 · ${c.jiucheng_att}`, { direction: "top", sticky: true })
      .addTo(layers.wall);
    L.polygon(c.danei.map(ll), { className: "daneiface", color: "#7e2b1f", weight: 2,
      fillColor: "#c8a06a", fillOpacity: .45 })
      .bindTooltip(`大内 · ${c.danei_att}`, { direction: "top", sticky: true })
      .addTo(layers.wall);
    label((0 + 8800) / 2, -320, "外城（方圓四十餘里 · 城濠曰護龍河）", "guolab", layers.wall);
    label(4100, 1900, "旧 城", "citylab small", layers.wall);
    label(4400, 3600, "大内", "citylab", layers.wall);
    /* 御街中轴 */
    L.polyline(c.yujie.map(ll), { color: "#a8874a", weight: 3, dashArray: "12 7",
      opacity: .9 }).bindTooltip("御街（宣德樓—州橋—朱雀門—南薰門）",
      { direction: "top", sticky: true }).addTo(layers.wall);
    label(4400, 1200, "御  街", "axislab", layers.wall);
  }

  function label(x, y, text, cls, layer) {
    L.marker(ll([x, y]), {
      icon: L.divIcon({ className: "", html: `<span class="${cls}">${text}</span>`, iconSize: null }),
      interactive: false,
    }).addTo(layer);
  }

  /* ── 城门（城门层；外城=常显符号，旧城/大内略小） ── */
  function renderGates() {
    layers.gate.clearLayers();
    MHZ.gates.forEach(g => {
      const minor = g.name.includes("角門子");
      const m = L.marker(ll(g.pos), {
        icon: L.divIcon({
          className: "",
          html: `<span class="gatesym w${g.wall}${minor ? " dim" : ""}">${g.name}</span>`,
          iconSize: null, iconAnchor: [0, 0],
        }),
      });
      m.bindTooltip(`<b>${g.name}</b> · ${g.wall === "大内" ? "宫门" : g.wall + "城"}${g.side ? "·" + g.side + "壁" : ""}<br>` +
        `<span class="tipatt">${g.att.replace(/·/g, "；")}</span><br>全书提及 ${g.mention} 次 · src:derived`,
        { direction: "top", opacity: .96, className: "ftip" });
      m.on("click", () => onGate && onGate(g));
      m.addTo(layers.gate);
    });
  }

  /* ── 河道（线层：四穿城河 + 桥名 tooltip） ── */
  function renderRivers() {
    MHZ.rivers.forEach(r => {
      L.polyline(r.pts.map(ll), { className: "riverline", color: "#3d6a7d", weight: r.key === "bian" ? 5 : 3.4,
        opacity: .72, smoothFactor: 1 })
        .bindTooltip(`<b>${r.name}</b> · ${r.att}<br>` +
          `<span class="tipatt">${r.batt.split("·")[0]}（桥 ${r.bridges.length} 座）</span><br>` +
          `全书提及 ${r.mention} 次 · src:derived`,
          { direction: "top", sticky: true, opacity: .96, className: "ftip" })
        .on("click", () => onRiver && onRiver(r))
        .addTo(layers.river);
      const mid = r.pts[Math.floor(r.pts.length / 2)];
      if (r.key === "bian") {
        label(6900, 2455, "汴  河", "riverlab", layers.river);
      } else {
        label(mid[0] + (r.key === "jinshui" ? 260 : 130),
              mid[1] + (r.key === "cai" ? -180 : 110), r.name, "riverlab", layers.river);
      }
    });
    /* 金明池水面（汴京西郊 · 卷七） */
    L.polygon([[-2100, 1900], [-700, 1900], [-700, 2450], [-2100, 2450]].map(ll),
              { className: "poolface", strokeDashArray: "5 5" })
      .bindTooltip("金明池 · 卷七「池在順天門街北周圍約九里三十歩」", { direction: "top" })
      .addTo(layers.river);
    label(-1400, 2175, "金明池", "pooletlab", layers.river);
  }

  /* ── 街市点（按类着色 · 径=挂接块字数） ── */
  function renderPlaces() {
    layers.place.clearLayers();
    MHZ.places.forEach(p => {
      const sel = p.id === selId;
      const dot = L.circleMarker(ll(p.pos), {
        radius: radiusOf(p) + (sel ? 3 : 0),
        color: sel ? "#b23a2e" : "#f6f3e6",
        weight: sel ? 2.6 : 1.6,
        fillColor: catColor(p.cat), fillOpacity: .92,
        className: "jiedot",
      });
      dot.bindTooltip(
        `<b style="font-family:KaiTi,serif;font-size:14px;letter-spacing:2px">${p.name}</b>` +
        ` <span style="color:#84929a">卷${p.vol}·${VOL_NAMES[p.vol]}</span><br>` +
        `<span class="tipatt">${p.att.split("·")[0]}</span><br>` +
        `条目 ${p.chars || ""}字 · 全书出场 ${p.mention} 次 · src:derived`,
        { direction: "top", opacity: .96, className: "ftip" });
      dot.on("click", () => onPlace && onPlace(p));
      dot.addTo(layers.place);
      L.marker(ll([p.pos[0], p.pos[1] + 42]), {
        icon: L.divIcon({ className: "", iconSize: null,
          html: `<span class="jielab${p.id === hlId ? " hl" : ""}" data-pid="${p.id}">${p.name}</span>` }),
        interactive: false,
      }).addTo(layers.place);
    });
  }

  /* ── 分层开关 ── */
  function toggleLayer(key, on) {
    visible[key] = on;
    if (!map || !layers[key]) return;
    if (on) map.addLayer(layers[key]);
    else map.removeLayer(layers[key]);
  }

  /* ── 选中 / 高亮 / 飞行 ── */
  function selectPlace(id, opt = {}) {
    selId = id;
    renderPlaces();
    const p = MHZ.places.find(x => x.id === id);
    if (p && opt.fly !== false && map) {
      map.flyTo(ll(p.pos), Math.max(map.getZoom(), -0.5), { duration: .9 });
    }
    focusRing(p);
  }

  function focusRing(p) {
    if (!layers.focus) return;
    layers.focus.clearLayers();
    if (!p) return;
    L.circleMarker(ll(p.pos), {
      radius: radiusOf(p) + 9, color: "#b23a2e", weight: 1.6,
      fill: false, dashArray: "4 4", className: "focusring",
    }).addTo(layers.focus);
  }

  function highlight(id, on) {
    hlId = on ? id : null;
    renderPlaces();
  }

  function flyTo(pos, zoom) {
    if (!map) return;
    map.flyTo(ll(pos), zoom != null ? zoom : Math.max(map.getZoom(), -0.5), { duration: .9 });
  }

  function fitAll() {
    if (!map) return;
    map.fitBounds(L.latLngBounds(ll([-2300, -1000]), ll([10100, 5000])), { padding: [20, 20] });
  }

  function home() {
    if (!map) return;
    map.flyTo(ll(MH_CONF.homeView.center), MH_CONF.homeView.zoom, { duration: .8 });
  }

  return {
    init, selectPlace, highlight, flyTo, fitAll, home, renderPlaces,
    toggleLayer, get visible() { return visible; },
    get map() { return map; },
    set onPlace(fn) { onPlace = fn; },
    set onGate(fn) { onGate = fn; },
    set onRiver(fn) { onRiver = fn; },
  };
})();
window.MHMAP = MHMAP;
