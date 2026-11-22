/* ═══════════ 梦华经纬 · 左列纲目（卷 → 节序/条目 · 门/河/街市组） ═══════════ */

const MHRAIL = (() => {
  const host = () => document.getElementById("raillist");

  function build() {
    const el = host();
    let html = "";
    /* 卷〇 提要·自序 */
    html += `<div class="rvol preface" data-vol="0"><span class="vlab">提要·自序</span>` +
      `<span class="vct">${MH_STATS.vol_chars["0"].toLocaleString()}字</span></div>`;
    /* 卷一 城防 */
    html += volRow(1, "城防", "門34 · 河4");
    html += `<div class="vlist citylist" data-for="1">` +
      `<div class="trow gates"><span class="tn">城门谱</span><span class="tc">34</span></div>` +
      `<div class="trow rivers"><span class="tn">穿城四河</span><span class="tc">4</span></div>` +
      `</div>`;
    /* 卷二至五 街市 */
    for (let v = 2; v <= 5; v++) {
      const ps = MHZ.places.filter(p => p.vol === v);
      html += volRow(v, VOL_NAMES[v], `${ps.length}地`);
      html += `<div class="vlist" data-for="${v}">` + ps.map(p =>
        `<div class="trow" data-id="${p.id}" data-name="${p.name}">` +
        `<span class="tn">${p.name}</span><span class="tc">${p.cat}</span></div>`).join("") + `</div>`;
    }
    /* 卷六至十 岁时 */
    for (let v = 6; v <= 10; v++) {
      const ss = MHZ.suishi.filter(s => s.vol === v);
      html += volRow(v, VOL_NAMES[v], `${ss.length}节`);
      html += `<div class="vlist" data-for="${v}">` + ss.map(s =>
        `<div class="trow" data-sui="${s.id}">` +
        `<span class="tn">${s.name}</span><span class="tc">${s.chars}字</span></div>`).join("") + `</div>`;
    }
    /* 城市骨架组 */
    html += `<div class="rvol city"><span class="vlab">城市名物</span>` +
      `<span class="vct">門${MHZ.gates.length} 河${MHZ.rivers.length} 市${MHZ.places.length}</span></div>`;
    html += `<div class="vlist citylist">` +
      `<div class="trow allgates"><span class="tn">城门谱</span><span class="tc">${MHZ.gates.length}</span></div>` +
      `<div class="trow allrivers"><span class="tn">穿城河道</span><span class="tc">${MHZ.rivers.length}</span></div>` +
      `<div class="trow allplaces"><span class="tn">街市名物</span><span class="tc">${MHZ.places.length}</span></div>` +
      `</div>`;
    el.innerHTML = html;

    el.querySelectorAll(".rvol[data-vol]").forEach(r =>
      r.addEventListener("click", () => {
        const v = +r.dataset.vol;
        el.querySelectorAll(".vlist").forEach(l =>
          l.classList.toggle("open", +l.dataset.for === v && !l.classList.contains("open")));
      }));
    el.querySelectorAll(".rvol.preface").forEach(r =>
      r.addEventListener("click", () => MHREADER.open(0)));
    el.querySelectorAll(".trow[data-id]").forEach(r =>
      r.addEventListener("click", () => MHAPP.openPlace(r.dataset.id)));
    el.querySelectorAll(".trow[data-sui]").forEach(r =>
      r.addEventListener("click", () => MHREADER.openBlock(r.dataset.sui, r.dataset.sui)));
    el.querySelectorAll(".trow.allgates").forEach(r =>
      r.addEventListener("click", () => MHAPP.openDirectory("gates")));
    el.querySelectorAll(".trow.gates").forEach(r =>
      r.addEventListener("click", () => MHAPP.openDirectory("gates")));
    el.querySelectorAll(".trow.rivers").forEach(r =>
      r.addEventListener("click", () => MHAPP.openDirectory("rivers")));
    el.querySelectorAll(".trow.allrivers").forEach(r =>
      r.addEventListener("click", () => MHAPP.openDirectory("rivers")));
    el.querySelectorAll(".trow.allplaces").forEach(r =>
      r.addEventListener("click", () => MHAPP.openDirectory("places")));
  }

  function volRow(v, name, ct) {
    return `<div class="rvol" data-vol="${v}">` +
      `<span class="vdot" style="background:${VOL_COLORS[v]}"></span>` +
      `<span class="vlab">卷${v} · ${name}</span>` +
      `<span class="vct">${ct} ${MH_STATS.vol_chars[String(v)].toLocaleString()}字</span></div>`;
  }

  function highlight(id) {
    host().querySelectorAll(".trow[data-id]").forEach(r =>
      r.classList.toggle("cur", r.dataset.id === id));
    const row = host().querySelector(`.trow[data-id="${id}"]`);
    if (row) {
      const list = row.parentElement;
      list.classList.add("open");
      row.scrollIntoView({ block: "nearest" });
    }
  }

  function highlightBlock(id) {
    host().querySelectorAll(".trow[data-sui]").forEach(r =>
      r.classList.toggle("cur", r.dataset.sui === id));
    const row = host().querySelector(`.trow[data-sui="${id}"]`);
    if (row) {
      row.parentElement.classList.add("open");
      row.scrollIntoView({ block: "nearest" });
    }
  }

  return { build, highlight, highlightBlock };
})();
window.MHRAIL = MHRAIL;
