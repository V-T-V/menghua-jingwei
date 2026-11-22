/* ═══════════ 梦华经纬 · 文本计量（数字全出自 docs/stats.json） ═══════════
   页签：篇幅结构 / 词频门河 / 寰宇桥（互查） / 双京桥（伽蓝对照）
   桥页签懒加载 data/xref_hy.js · data/xref_ly.js（P2 管线产物） */

const MHSTATS = (() => {
  /* MH_STATS 为 data/stats.js 顶层 const——跨 script 可见，但不挂 window（勿 window.X 取） */
  const S = () => MH_STATS;

  function open(tab = "layer") {
    MHAPP.setMode("stats");
    document.getElementById("vname").textContent = "计量";
    document.getElementById("vseal").textContent = "计数";
    document.getElementById("pmeta").innerHTML =
      `<span>全书 ${S().total_chars.toLocaleString()} 字 · ${S().blocks} 块</span>` +
      `<span>凡数字出自脚本 stats.py</span>`;
    const host = document.getElementById("pbody");
    host.className = "";
    const tabs = `<div class="dtabs">` +
      [["layer", "篇幅结构"], ["words", "词频·门河"], ["hy", "寰宇桥"], ["ly", "双京桥"]]
        .map(([k, n]) => `<button class="dtab${k === tab ? " cur" : ""}" data-k="${k}">${n}</button>`).join("") +
      `</div>`;
    let body = "";
    if (tab === "layer") body = tabLayer();
    else if (tab === "words") body = tabWords();
    else if (tab === "hy") body = `<div id="hybox"><p class="kv">加载中……</p></div>`;
    else body = `<div id="lybox"><p class="kv">加载中……</p></div>`;
    host.innerHTML = tabs + body;
    host.querySelectorAll(".dtab[data-k]").forEach(b =>
      b.addEventListener("click", () => open(b.dataset.k)));
    document.getElementById("panel").classList.add("open");
    if (tab === "hy") loadScript("data/xref_hy.js").then(renderHY).catch(() => {
      document.getElementById("hybox").innerHTML =
        `<p class="kv">桥数据未构建（tools/build_xref_hy.py）。</p>`;
    });
    if (tab === "ly") loadScript("data/xref_ly.js").then(renderLY).catch(() => {
      document.getElementById("lybox").innerHTML =
        `<p class="kv">桥数据未构建（tools/build_xref_ly.py）。</p>`;
    });
    location.hash = "#m=stats";
  }

  function loadScript(src) {
    return new Promise((ok, bad) => {
      const s = document.createElement("script");
      s.src = src + "?v=2";
      s.onload = ok;
      s.onerror = () => bad(new Error(src + " 加载失败"));
      document.head.appendChild(s);
    });
  }

  /* ── 篇幅结构：城防/街市/岁时三层 + 分卷条形 ── */
  function tabLayer() {
    const st = S();
    const max = Math.max(...Object.values(st.vol_chars));
    const bar = (label, v, note) =>
      `<div class="strow"><span class="stl">${label}</span>` +
      `<span class="stbar"><i style="width:${Math.round(v / max * 100)}%;background:${note}"></i></span>` +
      `<span class="stv">${v.toLocaleString()} 字</span></div>`;
    let html = `<div class="sect"><h3>正文三层（结构）</h3>` +
      `<p class="kv">卷一<b>城防</b> ${st.layer_chars.chengfang.toLocaleString()} 字 · ` +
      `卷二至五<b>街市民俗</b> ${st.layer_chars.street.toLocaleString()} 字 · ` +
      `卷六至十<b>岁时</b> ${st.layer_chars.suishi.toLocaleString()} 字` +
      `（提要自序 ${st.layer_chars.front.toLocaleString()} 字）——岁时记述占全书 ` +
      `${Math.round(st.layer_chars.suishi / st.total_chars * 100)}%，梦华之「梦」在节物风流。</p></div>`;
    html += `<div class="sect"><h3>分卷字数</h3>`;
    for (let v = 0; v <= 10; v++) {
      html += bar(v === 0 ? "提要·自序" : `卷${v}`,
                  st.vol_chars[String(v)],
                  v === 0 ? "#7c7255" : VOL_COLORS[v]);
    }
    html += `</div>`;
    /* 岁时月分布 */
    const months = Object.keys(st.suishi_month_chars).map(Number).sort((a, b) => a - b);
    const mmax = Math.max(...months.map(m => st.suishi_month_chars[String(m)]));
    html += `<div class="sect"><h3>岁时月分布（篇幅）</h3>`;
    months.forEach(m => {
      html += `<div class="strow"><span class="stl">${MONTH_NAMES[m]}</span>` +
        `<span class="stbar"><i style="width:${Math.round(st.suishi_month_chars[String(m)] / mmax * 100)}%;background:#2f5d70"></i></span>` +
        `<span class="stv">${st.suishi_month_chars[String(m)].toLocaleString()} 字 · ` +
        `${st.suishi_month_n[String(m)]} 节</span></div>`;
    });
    html += `<p class="kv small">月序为示意口径（立冬→十月、冬至/郊祀→十一月）；二月全书未载。</p></div>`;
    return html;
  }

  /* ── 词频 · 门/河提及 ── */
  function tabWords() {
    const st = S();
    const wmax = Math.max(...Object.values(st.words));
    let html = `<div class="sect"><h3>市井词频（预设词表 · 机械计数）</h3>`;
    for (const [w, n] of Object.entries(st.words).sort((a, b) => b[1] - a[1])) {
      html += `<div class="strow"><span class="stl">${w}</span>` +
        `<span class="stbar"><i style="width:${Math.round(n / wmax * 100)}%;background:#a8874a"></i></span>` +
        `<span class="stv">${n} 次</span></div>`;
    }
    html += `</div><div class="sect"><h3>城门提及 TOP</h3>`;
    const gm = Object.entries(st.gate_mentions).sort((a, b) => b[1] - a[1]).slice(0, 12);
    const gmax = gm[0][1] || 1;
    gm.forEach(([g, n]) => {
      html += `<div class="strow"><span class="stl">${g}</span>` +
        `<span class="stbar"><i style="width:${Math.round(n / gmax * 100)}%;background:#5c5138"></i></span>` +
        `<span class="stv">${n} 次</span></div>`;
    });
    html += `</div><div class="sect"><h3>河道提及</h3>`;
    for (const [r, n] of Object.entries(st.river_mentions)) {
      html += `<div class="strow"><span class="stl">${r}</span>` +
        `<span class="stbar"><i style="width:${Math.round(n / (st.river_mentions["汴河"] || 1) * 100)}%;background:#3d6a7d"></i></span>` +
        `<span class="stv">${n} 次</span></div>`;
    }
    html += `<p class="kv small">提及计数含条目自述句；「門」「橋」为单字宽口径。</p></div>`;
    return html;
  }

  /* ── 寰宇桥（太平寰宇記·開封府 互查，P2） ── */
  function renderHY() {
    const X = window.MH_XREF_HY;
    const box = document.getElementById("hybox");
    if (!X || !box) return;
    box.innerHTML =
      `<div class="sect"><h3>梦华汴京 × 寰宇開封府</h3>` +
      `<p class="kv">${X.note}</p></div>` +
      `<div class="sect"><h3>互文计数</h3><p class="kv">` +
      X.counts.map(c => `${c.k}：${c.v}`).join(" · ") + `</p></div>` +
      `<div class="sect"><h3>对照条目</h3>` +
      X.rows.map(r => `<div class="xpair"><div class="xpname">${r.name}` +
        `<a class="xlink" href="${r.href}" title="↗寰宇经纬·開封府">↗ 寰宇</a></div>` +
        `<div class="xpk">${r.k}</div>` +
        `<p class="xpq"><span class="xptag">夢華</span>${r.mh}</p>` +
        `<p class="xps"><span class="xptag">寰宇</span>${r.hy}</p></div>`).join("") +
      `</div>` +
      (X.excluded.length
        ? `<div class="sect"><h3>排除（消歧）</h3><p class="kv small">` +
          X.excluded.map(e => `${e.n}：${e.why}`).join("；") + `</p></div>` : "");
  }

  /* ── 双京桥（伽蓝经纬·北魏洛阳 对照，P2） ── */
  function renderLY() {
    const X = window.MH_XREF_LY;
    const box = document.getElementById("lybox");
    if (!X || !box) return;
    box.innerHTML =
      `<div class="sect"><h3>北魏洛阳 × 北宋东京（双京对照）</h3>` +
      `<p class="kv">${X.note}</p></div>` +
      `<div class="sect"><h3>城制参数对比</h3>` +
      `<div class="strow"><span class="stl"></span><span class="stbar"></span>` +
      `<span class="stv">伽蓝·洛阳 | 梦华·东京</span></div>` +
      X.params.map(p => `<div class="strow"><span class="stl">${p.k}</span>` +
        `<span class="stbar"></span><span class="stv">${p.ly} | ${p.mh}</span></div>`).join("") +
      `</div>` +
      `<div class="sect"><h3>名物对读（两京同构）</h3>` +
      X.pairs.map(p => `<div class="xpair"><div class="xpname">${p.k}` +
        `<a class="xlink" href="${p.href}" title="↗伽蓝经纬·洛阳">↗ 伽蓝</a></div>` +
        `<p class="xpq"><span class="xptag">洛陽</span>${p.ly}</p>` +
        `<p class="xps"><span class="xptag">東京</span>${p.mh}</p></div>`).join("") +
      `</div>`;
  }

  return { open };
})();
window.MHSTATS = MHSTATS;
