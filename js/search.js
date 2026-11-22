/* ═══════════ 梦华经纬 · 全文检索 ═══════════
   全书十卷+提要自序共 27KB：data/text/v0..v10.js 懒加载后主线程扫描
   （规模小，无需 Worker；结构独立成模块，语料增长可平滑升级）。
   命中定位优先级：街市名 / 城门名 / 节序节题 → 循读落卷。 */

const MHSEARCH = (() => {
  const input = document.getElementById("search");
  const box = document.getElementById("sresults");
  let loaded = false, loading = false, lastHits = [];

  function init() {
    let timer = null;
    input.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(run, 220);
    });
    input.addEventListener("keydown", e => {
      if (e.key === "Escape") { box.style.display = "none"; input.blur(); }
    });
    document.addEventListener("click", e => {
      if (!e.target.closest("#searchwrap")) box.style.display = "none";
    });
  }

  function ensureTexts() {
    if (loaded) return Promise.resolve();
    if (loading) return loading;
    loading = new Promise(ok => {
      let pending = 11;
      for (let v = 0; v <= 10; v++) {
        const s = document.createElement("script");
        s.src = `data/text/v${v}.js?v=1`;
        s.onload = s.onerror = () => { if (--pending === 0) { loaded = true; ok(); } };
        document.head.appendChild(s);
      }
    });
    return loading;
  }

  async function run() {
    const q = input.value.trim();
    if (q.length < 2) { box.style.display = "none"; return; }
    box.style.display = "block";
    box.innerHTML = `<div class="sr"><span class="where">检索</span>全书加载中……</div>`;
    await ensureTexts();
    if (input.value.trim() !== q) return;
    const T = window.MHTEXT || {};
    const hits = [];
    for (let v = 0; v <= 10; v++) {
      const t = T[v] || "";
      let i = t.indexOf(q), n = 0;
      while (i >= 0 && n < 4) {
        hits.push({ vol: v, ctx: t.slice(Math.max(0, i - 20), i + q.length + 34) });
        n++;
        i = t.indexOf(q, i + q.length);
      }
    }
    lastHits = hits.slice(0, 50);
    render(q);
  }

  function render(q) {
    if (!lastHits.length) {
      box.innerHTML = `<div class="sr"><span class="where">无得</span>全书未见「${q}」</div>`;
      return;
    }
    box.innerHTML = `<div class="sr head"><span class="where">得 ${lastHits.length} 条</span>` +
      `（提要自序 + 十卷）</div>` + lastHits.map((h, i) => {
        const ctx = h.ctx.replace(/&/g, "&amp;").replace(/</g, "&lt;")
          .replace(q, `<mark>${q}</mark>`);
        const where = h.vol === 0 ? "序" : `卷${h.vol}`;
        return `<div class="sr" data-i="${i}"><span class="where">${where}</span>${ctx}</div>`;
      }).join("");
    box.querySelectorAll(".sr[data-i]").forEach(el =>
      el.addEventListener("click", () => locate(lastHits[+el.dataset.i], q)));
  }

  /* 定位：命中街市/城门/节序名 → 循读落块；否则按卷循读 */
  function locate(hit, q) {
    box.style.display = "none";
    const p = MHZ.places.find(x => x.name === q || x.name.includes(q));
    if (p && p.vol === hit.vol) { MHREADER.open(p.vol, p.jie); return; }
    const g = MHZ.gates.find(x => x.name === q);
    if (g && hit.vol === 1) { MHREADER.open(1); return; }
    const s = MHZ.suishi.find(x => x.name.includes(q));
    if (s && s.vol === hit.vol) { MHREADER.openBlock(s.id); return; }
    MHREADER.open(hit.vol);
  }

  return { init, run };
})();
window.MHSEARCH = MHSEARCH;
