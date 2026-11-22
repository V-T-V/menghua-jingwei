/* ═══════════ 梦华经纬 · 应用装配（boot / 模式 / 深链 / 夜读 / 分层开关） ═══════════
   深链语法：#m=map|read|directory|suishi|stats|about · #juan=0..10
   · #jie=街市名 · #men=门名 · #he=河名 · #sui=节序名 */

const MHAPP = (() => {
  let mode = "map";
  const MODE_NOTE = {
    map: "汴京城图 · 门/河/街市分层",
    read: "循读 · 滚动文本，舆图随行",
    directory: "名物名录 · 三表可导出",
    suishi: "岁时记 · 十二个月的东京",
    stats: "计量 · 篇幅/词频/双桥",
    about: "关于 · 数据与坐标边界",
  };

  function boot() {
    MHMAP.init();
    MHMAP.onPlace = p => openPlace(p.id);
    MHMAP.onGate = g => openGate(g);
    MHMAP.onRiver = r => openRiver(r);
    MHRAIL.build();
    MHSEARCH.init();
    bindUI();
    const dismissBoot = () => {
      const b = document.getElementById("boot");
      if (!b) return;
      b.classList.add("off");
      setTimeout(() => b.remove(), 700);
    };
    document.querySelector("#boot .go").addEventListener("click", dismissBoot);
    /* ?boot=off：跳过序幕直入（截图取证/外链分享用） */
    if (new URLSearchParams(location.search).get("boot") === "off") dismissBoot();
    const m = MHZ.meta;
    document.getElementById("bookstat").textContent =
      `十卷 ${m.totalChars.toLocaleString()} 字 · ${m.gates} 门 · ${m.places} 地`;
    applyHash();
    window.addEventListener("hashchange", applyHash);
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("sw.js").then(() => {
        const el = document.getElementById("swstate");
        el.style.display = ""; el.textContent = "离线就绪";
      }).catch(() => {});
    }
  }

  function bindUI() {
    document.querySelectorAll("#modes .mode").forEach(b =>
      b.addEventListener("click", () => act(b.dataset.mode)));
    document.getElementById("pclose").addEventListener("click", closePanel);
    document.getElementById("fitlink").addEventListener("click", () => MHMAP.fitAll());
    document.getElementById("wanderlink").addEventListener("click", () => {
      const ps = MHZ.places;
      openPlace(ps[Math.floor(Math.random() * ps.length)].id);
    });
    document.getElementById("bmlink").addEventListener("click", () => MHBM.open());
    const nightBtn = document.getElementById("nightlink");
    const nightApply = on => {
      document.body.classList.toggle("night", on);
      nightBtn.textContent = on ? "☀ 昼" : "☾ 夜读";
      try { localStorage.setItem("mhjNight", on ? "1" : ""); } catch (e) {}
    };
    nightBtn.addEventListener("click", () =>
      nightApply(!document.body.classList.contains("night")));
    try { if (localStorage.getItem("mhjNight")) nightApply(true); } catch (e) {}
    /* 分层开关（城垣/城门/河道/街市） */
    document.querySelectorAll("#layerbox .lrow").forEach(r =>
      r.addEventListener("click", () => {
        const k = r.dataset.layer;
        const on = !r.classList.contains("on");
        r.classList.toggle("on", on);
        MHMAP.toggleLayer(k, on);
      }));
    /* 循读条 */
    const sel = document.getElementById("rjvol");
    sel.innerHTML = `<option value="0">提要·自序</option>` +
      Array.from({ length: 10 }, (_, i) => i + 1).map(v =>
        `<option value="${v}">卷${v} · ${VOL_NAMES[v]}</option>`).join("");
    sel.addEventListener("change", () => MHREADER.open(+sel.value));
    document.getElementById("rprev").addEventListener("click", () => stepBlock(-1));
    document.getElementById("rnext").addEventListener("click", () => stepBlock(1));
    document.getElementById("rtts").addEventListener("click", () => MHREADER.ttsToggle());
    window.addEventListener("keydown", e => {
      if (e.key === "Escape") closePanel();
    });
  }

  function stepBlock(d) {
    if (MHREADER.current) {
      const host = document.getElementById("pbody");
      const els = [...host.querySelectorAll(".entry")];
      let i = els.findIndex(e => e.dataset.id === MHREADER.current);
      i = Math.max(0, Math.min(els.length - 1, i + d));
      if (els[i]) MHREADER.gotoBlock(els[i].dataset.id, true);
    } else {
      MHREADER.open(1);
    }
  }

  function setMode(m) {
    mode = m;
    document.querySelectorAll("#modes .mode").forEach(b =>
      b.classList.toggle("active", b.dataset.mode === m));
    const btn = document.querySelector(`#modes .mode[data-mode="${m}"]`);
    document.getElementById("modelabel").textContent =
      btn ? btn.textContent : m;
    document.getElementById("modenote").textContent = MODE_NOTE[m] || "";
    /* 非舆图模式收起分层开关 */
    const lb = document.getElementById("layerbox");
    if (lb) lb.style.display = (m === "map") ? "" : "none";
  }

  function act(m) {
    if (m === "stats") return MHSTATS.open();
    if (m === "about") return openAbout();
    if (m === "directory") return openDirectory("places");
    if (m === "suishi") return MHSUISHI.open();
    if (m === "read") return MHREADER.open(MHREADER.vol || 1);
    setMode(m);
    closePanel(false);
  }

  /* ── 街市详情 ── */
  async function openPlace(id, inReader = false) {
    const p = MHZ.places.find(x => x.id === id) ||
              MHZ.places.find(x => x.name === id);
    if (!p) return;
    if (inReader || mode === "read") { MHREADER.open(p.vol, p.jie); return; }
    setMode("map");
    try { await MHREADER.ensureSections(); } catch (e) {}
    MHMAP.selectPlace(p.id, { fly: true });
    MHMAP.highlight(p.id, true);
    MHRAIL.highlight(p.id);
    document.getElementById("vname").textContent = p.name;
    document.getElementById("vseal").textContent = p.cat.slice(0, 2);
    document.getElementById("pmeta").innerHTML =
      `<span>卷${p.vol} · ${VOL_NAMES[p.vol]}</span>` +
      `<span>${p.cat}</span>` +
      `<span>条目 ${p.chars} 字</span>` +
      `<span>全书出场 ${p.mention} 次</span>` +
      `<span>坐标 src:derived · 原文方位锚定</span>`;
    const b = (typeof MH_SECTIONS !== "undefined") && MH_SECTIONS[p.jie];
    const host = document.getElementById("pbody");
    host.className = "";
    host.innerHTML =
      `<div class="sect"><h3>方位书证</h3><p class="kv">「${p.att.replace(/·/g, "」；「")}」</p>` +
      `<p class="kv small">示意平面坐标 ${p.pos[0]}, ${p.pos[1]} m · src:${p.src} · ` +
      `依据：原文方位句 + 宋东京城考古常识布点（量级示意）</p></div>` +
      `<div class="sect"><h3>原文</h3>` +
      (b ? b.paras.map((pp, i) => paraHTML(pp, i === 0)).join("")
        : `<p class="kv">正文加载失败</p>`) + `</div>` +
      `<div class="btnrow"><button class="ftool" id="goread">▸ 循读至此（卷${p.vol}）</button>` +
      `<button class="ftool" id="gobm"></button></div>`;
    document.getElementById("panel").classList.add("open");
    const gr = document.getElementById("goread");
    if (gr) gr.addEventListener("click", () => MHREADER.open(p.vol, p.jie));
    MHBM.bindToggle(document.getElementById("gobm"), p.name, p.vol, p.jie);
    location.hash = `#jie=${encodeURIComponent(p.name)}`;
  }

  function paraHTML(p, first) {
    let html = "", rest = p, m;
    const re = /(\([^)]*\))/;
    while ((m = rest.match(re))) {
      html += escapeHtml(rest.slice(0, m.index));
      html += `<span class="note">${escapeHtml(m[1])}</span>`;
      rest = rest.slice(m.index + m[1].length);
    }
    html += escapeHtml(rest);
    return `<p class="ctxt${first ? " first" : ""}">${html}</p>`;
  }

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  /* ── 城门详情 ── */
  function openGate(g) {
    setMode("map");
    MHMAP.flyTo(g.pos, Math.max(MHMAP.map.getZoom(), 0));
    document.getElementById("vname").textContent = g.name;
    document.getElementById("vseal").textContent = "城门";
    document.getElementById("pmeta").innerHTML =
      `<span>${g.wall}城 · ${g.side}壁</span>` +
      `<span>全书提及 ${g.mention} 次</span>` +
      `<span>示意方位 · src:derived</span>`;
    document.getElementById("pbody").className = "";
    document.getElementById("pbody").innerHTML =
      `<div class="sect"><h3>城防谱书证</h3><p class="kv">「${g.att.replace(/·/g, "」；「")}」</p></div>` +
      `<div class="sect"><h3>说明</h3><p class="kv small">城门是《梦华录》空间书写的锚：` +
      `卷二以下街市条目多以「出某门」「某門裏/外」格式给出方位。门位为宋东京城` +
      `考古常识示意（外城8,800×4,800m，1里≈560m），src:derived。</p></div>` +
      `<div class="btnrow"><button class="ftool" id="govol1">▸ 循读卷一城防谱</button></div>`;
    document.getElementById("panel").classList.add("open");
    const gb = document.getElementById("govol1");
    if (gb) gb.addEventListener("click", () => MHREADER.open(1));
    location.hash = `#men=${encodeURIComponent(g.name)}`;
  }

  /* ── 河道详情 ── */
  function openRiver(r) {
    setMode("map");
    const mid = r.pts[Math.floor(r.pts.length / 2)];
    MHMAP.flyTo(mid, Math.max(MHMAP.map.getZoom(), -0.4));
    document.getElementById("vname").textContent = r.name;
    document.getElementById("vseal").textContent = "河道";
    document.getElementById("pmeta").innerHTML =
      `<span>穿城四河之一</span>` +
      `<span>桥 ${r.bridges.length} 座（原文明载）</span>` +
      `<span>全书提及 ${r.mention} 次 · src:derived</span>`;
    document.getElementById("pbody").className = "";
    document.getElementById("pbody").innerHTML =
      `<div class="sect"><h3>河道书证</h3><p class="kv">「${r.att}」</p>` +
      `<p class="kv small">「${r.batt}」（${r.bridges.join("·")}）</p></div>` +
      `<div class="sect"><h3>说明</h3><p class="kv small">线层=卷一「穿城」记载走向示意` +
      `（${r.pts.length} 折点，米制示意平面），非实测河道。</p></div>` +
      `<div class="btnrow"><button class="ftool" id="govol1h">▸ 循读卷一河道节</button></div>`;
    document.getElementById("panel").classList.add("open");
    const gb = document.getElementById("govol1h");
    if (gb) gb.addEventListener("click", () => MHREADER.open(1, "v1-02"));
    location.hash = `#he=${encodeURIComponent(r.name)}`;
  }

  /* ── 名录 ── */
  function openDirectory(kind = "places") {
    setMode("directory");
    document.getElementById("vname").textContent = "城市名物";
    document.getElementById("vseal").textContent = "名录";
    document.getElementById("pmeta").innerHTML =
      `<span>城门 ${MHZ.gates.length} · 河道 ${MHZ.rivers.length} · 街市 ${MHZ.places.length} · 节序 ${MHZ.suishi.length}</span>`;
    const host = document.getElementById("pbody");
    host.className = "";
    const tabs = `<div class="dtabs">` +
      [["places", "街市名物"], ["gates", "城门谱"], ["rivers", "穿城河道"], ["suishi", "岁时节序"]]
        .map(([k, n]) => `<button class="dtab${k === kind ? " cur" : ""}" data-k="${k}">${n}</button>`).join("") +
      `<span class="dspacer"></span>` +
      `<button class="dtab exp" id="csvdl" title="当前表 CSV（带 BOM，Excel 直开）· tools/export_data.py 同口径">⤓ CSV</button>` +
      `<button class="dtab exp" id="kmldl" title="三表合一 · Google Earth · 示意坐标已注明">⤓ KML</button>` +
      `<button class="dtab exp" id="gjdl" title="三表合一 · 通用 GIS · src:derived">⤓ GeoJSON</button>` +
      `</div>`;
    let body = "";
    if (kind === "places") {
      body = MHZ.places.map(p =>
        `<div class="drow" data-id="${p.id}"><span class="dn">${p.name}</span>` +
        `<span class="dl">${p.att.split("·")[0].slice(0, 18)}</span>` +
        `<span class="dc">卷${p.vol}·${p.cat}</span></div>`).join("");
    } else if (kind === "gates") {
      body = ["外城", "舊城", "大内"].map(w => {
        const gs = MHZ.gates.filter(g => g.wall === w);
        return `<div class="dvol">${w === "大内" ? "大内（宫门）" : w + "（" + gs[0].side + "壁序）"} · ${gs.length}</div>` +
          gs.map(g =>
            `<div class="drow" data-gate="${g.name}"><span class="dn">${g.name}</span>` +
            `<span class="dl">${g.side}壁</span>` +
            `<span class="dc">${g.mention}次</span></div>`).join("");
      }).join("");
    } else if (kind === "rivers") {
      body = MHZ.rivers.map(r =>
        `<div class="drow" data-river="${r.name}"><span class="dn">${r.name}</span>` +
        `<span class="dl">${r.bridges.length} 桥 · ${r.att.slice(0, 16)}</span>` +
        `<span class="dc">${r.mention}次</span></div>`).join("");
    } else {
      body = MHZ.suishi.map(s =>
        `<div class="drow" data-sui="${s.id}"><span class="dn">${s.name}</span>` +
        `<span class="dl">${MONTH_NAMES[s.month]} · 卷${s.vol}</span>` +
        `<span class="dc">${s.chars}字</span></div>`).join("");
    }
    host.innerHTML = tabs + `<div class="dlist">${body}</div>`;
    host.querySelectorAll(".dtab[data-k]").forEach(b =>
      b.addEventListener("click", () => openDirectory(b.dataset.k)));
    const bc = document.getElementById("csvdl");
    if (bc) bc.addEventListener("click", () =>
      MHEXPORT.csv(kind === "suishi" ? "places" : kind));
    const bk = document.getElementById("kmldl");
    if (bk) bk.addEventListener("click", () => MHEXPORT.kml());
    const bg = document.getElementById("gjdl");
    if (bg) bg.addEventListener("click", () => MHEXPORT.geojson());
    host.querySelectorAll(".drow[data-id]").forEach(r =>
      r.addEventListener("click", () => openPlace(r.dataset.id)));
    host.querySelectorAll(".drow[data-gate]").forEach(r =>
      r.addEventListener("click", () => {
        const g = MHZ.gates.find(x => x.name === r.dataset.gate);
        if (g) openGate(g);
      }));
    host.querySelectorAll(".drow[data-river]").forEach(r =>
      r.addEventListener("click", () => {
        const rv = MHZ.rivers.find(x => x.name === r.dataset.river);
        if (rv) openRiver(rv);
      }));
    host.querySelectorAll(".drow[data-sui]").forEach(r =>
      r.addEventListener("click", () => MHREADER.openBlock(r.dataset.sui)));
    document.getElementById("panel").classList.add("open");
    location.hash = "#m=directory";
  }

  function openAbout() {
    const m = MHZ.meta;
    setMode("about");
    document.getElementById("vname").textContent = "关于";
    document.getElementById("vseal").textContent = "叙";
    document.getElementById("pmeta").innerHTML = `<span>数据管线 · 方法与边界</span>`;
    document.getElementById("pbody").className = "";
    document.getElementById("pbody").innerHTML = `
<div class="sect"><h3>梦华经纬</h3>
<p class="kv">宋孟元老《东京梦华录》十卷数字人文平台。方舆（点织版图）、水道（线溯江河）、
伽蓝（点织北魏洛阳）姊妹系列第八站：此以<b>城</b>（北宋东京/汴京）为空间范式——
门谱、河道、街市、岁时四层织一座梦中的城，与伽蓝经纬构成「双京对照」。</p></div>
<div class="sect"><h3>数据与方法</h3><p class="kv">
· 文本：kanripo KR2k0111（文淵閣四庫全書本，mandoku 格式）via GitHub raw；<br>
　提要+自序+十卷共 ${m.totalChars.toLocaleString()} 字；缺字实体 ${m.krEntities} 处以 □ 代（data_raw 可复核）<br>
　版本性质：四库讳改/异文不在校勘范围（如州橋夹注「正名<b>大</b>漢橋」，通行本作天漢橋——依样保留）<br>
· 块：${m.blocks} 阅读块（◎ 节题分层）；城防 ${MH_STATS.layer_chars.chengfang.toLocaleString()} 字 · 街市民俗 ${MH_STATS.layer_chars.street.toLocaleString()} 字 · 岁时 ${MH_STATS.layer_chars.suishi.toLocaleString()} 字<br>
· 城门 ${m.gates}（外城${m.gatesOuter}·旧城${m.gatesInner}·大内${m.gatesPalace}，皆卷一书证）· 河道 ${m.rivers}（穿城四河+桥 ${MHZ.rivers.reduce((a, r) => a + r.bridges.length, 0)} 座）· 街市 ${m.places} · 节序 ${m.suishi}<br>
· 城图：自绘示意平面（Leaflet L.CRS.Simple）——外城8,800×4,800m（「方圓四十餘里」量级，1宋里≈560m），<br>
　全部坐标 <code>src:"derived"</code>；门/街市=城防谱+方位句+考古常识量级布点<br>
· 计量：数字全部出自 python tools/stats.py → docs/stats.json</p></div>
<div class="sect"><h3>体例与致谢</h3><p class="kv">
基建承伽蓝经纬/方舆经纬姊妹站：深链/夜读/TTS/书签/PWA/分层开关。文本源：kanripo。底图：自绘（无外部瓦片）。</p></div>
<div class="sect"><h3>P2 · 论文 / 导出 / 双桥</h3><p class="kv">
· 论文：docs/梦华经纬-数字人文.pdf（数字全出自脚本；改 ANALYSIS.md 必重排，lint 哨兵联动）<br>
· 导出：名录页 ⤓ CSV(BOM)/KML/GeoJSON 与 tools/export_data.py 同口径；示意坐标逐行注明 src:derived<br>
· 寰宇桥：计量页——梦华汴京 ↔ 寰宇經緯開封府（太平寰宇記卷一）对照 + ↗深链<br>
· 双京桥：计量页——与伽蓝经纬（北魏洛阳）城制参数/名物对读，「双京对照」系列命题</p></div>
<div class="sect"><h3>快速上手</h3><p class="kv">
左列纲目点条目 → 详情；「循读」按卷滚动读原文，舆图随文飞行；顶栏检全书；
「岁时记」看一年十二个月的东京；左下分层开关控门/河/街市诸层。</p></div>`;
    document.getElementById("panel").classList.add("open");
    location.hash = "#m=about";
  }

  function closePanel(clearHash = true) {
    document.getElementById("panel").classList.remove("open");
    if (MHREADER.current) MHREADER.close();
    if (clearHash) location.hash = "#m=map";
  }

  /* ── 深链：#m= #juan= #jie= #men= #he= #sui=（多段 # 并存） ── */
  async function applyHash() {
    const segs = location.hash.split("#").filter(Boolean).map(s => s.split("="));
    const get = k => { const s = segs.find(x => x[0] === k); return s ? s[1] : null; };
    const jie = get("jie"), men = get("men"), he = get("he"), sui = get("sui");
    const juan = get("juan"), m = get("m");
    if (jie) {
      const dec = decodeURIComponent(jie);
      const p = MHZ.places.find(x => x.name === dec);
      if (p) {
        if (juan !== null && juan !== "") MHREADER.open(+juan, p.jie);
        else openPlace(p.id);
        return;
      }
    }
    if (sui) {
      const dec = decodeURIComponent(sui);
      const s = MHZ.suishi.find(x => x.name === dec);
      if (s) { MHREADER.openBlock(s.id); return; }
    }
    if (juan !== null && juan !== undefined && juan !== "") {
      const v = Math.max(0, Math.min(10, +juan));
      MHREADER.open(v);
      return;
    }
    if (men) {
      const g = MHZ.gates.find(x => x.name === decodeURIComponent(men));
      if (g) { openGate(g); return; }
    }
    if (he) {
      const r = MHZ.rivers.find(x => x.name === decodeURIComponent(he));
      if (r) { openRiver(r); return; }
    }
    if (m === "stats") return MHSTATS.open();
    if (m === "suishi") return MHSUISHI.open();
    if (m === "about") return openAbout();
    if (m === "directory") return openDirectory();
    if (m === "read") return MHREADER.open(1);
    setMode("map");
  }

  document.addEventListener("DOMContentLoaded", boot);
  return { openPlace, openDirectory, setMode,
           get mode() { return mode; } };
})();
window.MHAPP = MHAPP;
