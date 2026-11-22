/* ═══════════ 梦华经纬 · 岁时时间轴（卷六至十节序 · 农历月编年） ═══════════
   一年十二个月的东京：从正月元宵灯山到除夕大傩——
   月序=build_data.py SUISHI_MONTH 示意口径（立冬→十月、冬至/郊祀→十一月），
   点击节卡循读原文；深链 #m=suishi#sui=节名 */

const MHSUISHI = (() => {

  async function open(focusName) {
    try { await MHREADER.ensureSections(); } catch (e) {}
    MHAPP.setMode("suishi");
    document.getElementById("vname").textContent = "岁时记";
    document.getElementById("vseal").textContent = "岁时";
    document.getElementById("pmeta").innerHTML =
      `<span>卷六至十 · ${MHZ.suishi.length} 节</span>` +
      `<span>${MH_STATS.suishi_chars.toLocaleString()} 字（全书 ${Math.round(MH_STATS.suishi_chars / MH_STATS.total_chars * 100)}%）</span>` +
      `<span>农历月编年 · 点击循读</span>`;
    const host = document.getElementById("pbody");
    host.className = "";
    let html = `<div class="sect"><h3>一年之梦华</h3><p class="kv">` +
      `《梦华录》后半（卷六至十）以时间为经：孟元老把一座城拆成十二个月的节物风流——` +
      `正月灯山上元、三月金明池争标、七夕磨喝乐、中秋新酒、除夕大傩驱祟出南薰门。` +
      `月序为示意口径（「立冬」归十月、「冬至/郊祀」归十一月），节卡点击入循读。</p></div>` +
      `<div class="suiwrap">`;
    for (let m = 1; m <= 12; m++) {
      const ss = MHZ.suishi.filter(s => s.month === m);
      if (!ss.length) {
        html += `<div class="suiband"><span class="snum">${MONTH_NAMES[m]}</span>` +
          `<span class="sdesc">本卷未载</span></div>`;
        continue;
      }
      const chars = ss.reduce((a, s) => a + s.chars, 0);
      html += `<div class="suiband"><span class="snum">${MONTH_NAMES[m]}</span>` +
        `<span class="sdesc">${ss.length} 节</span>` +
        `<span class="schars">${chars.toLocaleString()} 字</span></div>`;
      html += ss.map(s => {
        const b = MH_SECTIONS[s.id];
        const frag = b && b.paras.length ? b.paras[0].slice(0, 76) : "";
        return `<div class="suicard" data-sui="${s.id}">` +
          `<div class="scname">${s.name}</div>` +
          `<div class="scmeta">卷${s.vol} · ${s.chars} 字${b ? " · " + (KIND_LABEL(b.kind)) : ""}</div>` +
          `<div class="scfrag">${frag}…</div></div>`;
      }).join("");
    }
    html += `</div>`;
    host.innerHTML = html;
    host.querySelectorAll(".suicard").forEach(c =>
      c.addEventListener("click", () => MHREADER.openBlock(c.dataset.sui)));
    document.getElementById("panel").classList.add("open");
    if (focusName) {
      const s = MHZ.suishi.find(x => x.name === decodeURIComponent(focusName));
      if (s) {
        const card = host.querySelector(`.suicard[data-sui="${s.id}"]`);
        if (card) card.scrollIntoView({ block: "center" });
      }
    }
  }

  function KIND_LABEL(k) {
    return { suishi: "节序" }[k] || k;
  }

  return { open };
})();
window.MHSUISHI = MHSUISHI;
