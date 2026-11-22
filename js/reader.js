/* ═══════════ 梦华经纬 · 循读（核心体验：卷 → 节块滚动，舆图随行） ═══════════
   右幅 = 一卷全部阅读块（提要/自序/城防/街市/民俗/节序）
   滚动文本 → 当前块若有挂接街市点则地图飞行+高亮；块卡点击 → 地图跟随
   深链写回 #m=read#juan=N[#jie=名]（节序块写 #sui=名） */

const MHREADER = (() => {
  let curVol = 1, curId = null;
  const pbody = () => document.getElementById("pbody");

  /* 全书 27KB：sections.js 懒加载一次（检索/循读共用） */
  function ensureSections() {
    if (typeof MH_SECTIONS !== "undefined") return Promise.resolve();
    if (ensureSections._p) return ensureSections._p;
    ensureSections._p = new Promise((ok, bad) => {
      const s = document.createElement("script");
      s.src = "data/sections.js?v=2";
      s.onload = ok;
      s.onerror = () => bad(new Error("sections.js 加载失败"));
      document.head.appendChild(s);
    });
    return ensureSections._p;
  }

  function blocksOf(v) {
    return Object.values(MH_SECTIONS)
      .filter(b => b.vol === v)
      .sort((a, b2) => a.ord - b2.ord);
  }

  async function open(vol, focusId = null) {
    try { await ensureSections(); } catch (e) { /* 骨架仍可展示 */ }
    curVol = vol;
    MHAPP.setMode("read");
    document.getElementById("vname").textContent =
      (vol === 0 ? "提要 · 自序" : `卷${vol} · ${VOL_NAMES[vol]}`);
    document.getElementById("vseal").textContent = "循读";
    document.getElementById("pmeta").innerHTML = metaHTML(vol);
    renderBody(vol);
    document.getElementById("panel").classList.add("open");
    document.getElementById("readerbar").classList.remove("hidden");
    const sel = document.getElementById("rjvol");
    if (sel) sel.value = String(vol);
    gotoBlock(focusId || firstBlockId(vol), true);
    writeHash(focusId || firstBlockId(vol));
  }

  async function openBlock(id) {
    const b = (typeof MH_SECTIONS !== "undefined") ? MH_SECTIONS[id] : null;
    if (!b) return open(1);
    return open(b.vol, id);
  }

  function firstBlockId(v) {
    return blocksOf(v)[0].id;
  }

  function nameOf(id) {
    return MH_SECTIONS[id] ? MH_SECTIONS[id].name : "";
  }

  function metaHTML(vol) {
    const bs = blocksOf(vol);
    const sp = MHZ.places.filter(p => p.vol === vol).length;
    return `<span>${MH_STATS.vol_chars[String(vol)].toLocaleString()} 字</span>` +
      `<span>${bs.length} 节块</span>` +
      (sp ? `<span>挂图地条目 ${sp}</span>` : "") +
      `<span>滚动文本 · 舆图随行</span>`;
  }

  const KIND_TAG = {
    tiyao: "提要", preface: "自序", city: "城防", street: "街市",
    folk: "民俗", suishi: "节序",
  };

  /* 夹注渲染：（……）双行夹注以小字缀排（四库本体例） */
  function renderPara(p, first) {
    let html = "";
    let rest = p;
    let m;
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

  function blockCard(b) {
    const p = MHZ.places.find(x => x.jie === b.id);
    const tag = KIND_TAG[b.kind] || b.kind;
    const meta = p
      ? `<div class="bmeta">${p.cat} · ${p.att.split("·")[0]}</div>`
      : `<div class="bmeta">${b.chars} 字</div>`;
    return `<div class="entry${p ? "" : " narr"}" data-id="${b.id}">` +
      `<div class="ehead"><span class="etag">${tag}</span>` +
      `<span class="ename">${b.name}</span></div>` +
      meta +
      b.paras.map((p2, i) => renderPara(p2, i === 0)).join("") +
      `</div>`;
  }

  function renderBody(vol) {
    const host = pbody();
    host.className = "reading";
    const bs = blocksOf(vol);
    host.innerHTML = bs.map(blockCard).join("");
    host.querySelectorAll(".entry").forEach(el =>
      el.addEventListener("click", () => {
        gotoBlock(el.dataset.id, true);
        writeHash(el.dataset.id);
      }));
    host.onscroll = onScroll;
  }

  /* ── 锚导航 + 地图跟随 ── */
  function gotoBlock(id, scroll = true) {
    const host = pbody();
    const el = host.querySelector(`.entry[data-id="${id}"]`);
    if (!el) return;
    curId = id;
    host.querySelectorAll(".entry").forEach(x => x.classList.toggle("cur", x.dataset.id === id));
    if (scroll) el.scrollIntoView({ block: "start", behavior: "smooth" });
    const p = MHZ.places.find(x => x.jie === id);
    MHRAIL.highlightBlock(id);
    if (p) {
      MHMAP.selectPlace(p.id, { fly: true });
      MHMAP.highlight(p.id, true);
      MHRAIL.highlight(p.id);
    } else if (MH_SECTIONS[id] && MH_SECTIONS[id].kind === "city") {
      /* 城防块：回到全城视野 */
      if (MHMAP.map && MHMAP.map.getZoom() < -1.6) MHMAP.fitAll();
    }
    updateProg();
  }

  function writeHash(id) {
    const b = MH_SECTIONS[id];
    if (!b) return;
    const p = MHZ.places.find(x => x.jie === id);
    let h = `#m=read#juan=${curVol}`;
    if (p) h += `#jie=${encodeURIComponent(p.name)}`;
    else if (b.kind === "suishi") h += `#sui=${encodeURIComponent(b.name)}`;
    location.hash = h;
  }

  function updateProg() {
    const host = pbody();
    const els = [...host.querySelectorAll(".entry")];
    const i = els.findIndex(e => e.dataset.id === curId);
    document.getElementById("rprog").textContent =
      `${nameOf(curId)} · 卷${curVol} ${i + 1}/${els.length}`;
  }

  /* 滚动跟随：可视区顶部最近的 entry 即当前块（节流） */
  let timer = null;
  function onScroll() {
    if (timer) return;
    timer = setTimeout(() => {
      timer = null;
      const host = pbody();
      const top = host.scrollTop + 80;
      const els = [...host.querySelectorAll(".entry")];
      let best = 0;
      els.forEach((e, k) => { if (e.offsetTop <= top) best = k; });
      const id = els[best] && els[best].dataset.id;
      if (id && id !== curId) {
        curId = id;
        els.forEach(e => e.classList.toggle("cur", e.dataset.id === id));
        const p = MHZ.places.find(x => x.jie === id);
        if (p) {
          MHMAP.flyTo(p.pos);
          MHMAP.highlight(p.id, true);
          MHRAIL.highlight(p.id);
        }
        MHRAIL.highlightBlock(id);
        updateProg();
        history.replaceState(null, "", `#m=read#juan=${curVol}` +
          (p ? `#jie=${encodeURIComponent(p.name)}`
             : (MH_SECTIONS[id].kind === "suishi"
                ? `#sui=${encodeURIComponent(MH_SECTIONS[id].name)}` : "")));
      }
    }, 260);
  }

  /* ── TTS 听书 ── */
  const tts = { queue: [], idx: 0, on: false };
  function collectFrom(id) {
    const b = MH_SECTIONS[id];
    return b ? b.paras.slice(0, 6) : [];
  }
  function ttsNext() {
    if (!tts.on || tts.idx >= tts.queue.length) { ttsStop(); return; }
    const u = new SpeechSynthesisUtterance(tts.queue[tts.idx++]);
    u.lang = "zh-CN";
    u.rate = 0.95;
    const v = speechSynthesis.getVoices().find(x => x.lang && x.lang.startsWith("zh"));
    if (v) u.voice = v;
    u.onend = () => setTimeout(ttsNext, 240);
    speechSynthesis.speak(u);
  }
  function ttsToggle() {
    if (tts.on) { ttsStop(); return; }
    if (typeof speechSynthesis === "undefined") return;
    tts.queue = collectFrom(curId);
    if (!tts.queue.length) return;
    tts.on = true; tts.idx = 0;
    const b = document.getElementById("rtts");
    if (b) b.textContent = "■ 停读";
    ttsNext();
  }
  function ttsStop() {
    tts.on = false;
    try { speechSynthesis.cancel(); } catch (e) {}
    const b = document.getElementById("rtts");
    if (b) b.textContent = "▷ 朗读";
  }

  function close() {
    ttsStop();
    curId = null;
    document.getElementById("readerbar").classList.add("hidden");
  }

  return { open, openBlock, close, gotoBlock, ensureSections, ttsToggle,
           get current() { return curId; },
           get vol() { return curVol; } };
})();
window.MHREADER = MHREADER;
