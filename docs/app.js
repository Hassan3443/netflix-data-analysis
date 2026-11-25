(async function () {
  const $ = s => document.querySelector(s);
  const res = await fetch('data.json');
  const { rows } = await res.json();
  // column order is written by build_site_data.py
  const T = 0, TYPE = 1, REL = 2, ADDED = 3, RATING = 4, DUR = 5, COUNTRIES = 6, GENRES = 7, DIRS = 8;
  const state = { type: 'all', genre: '', country: '', from: 0, to: 9999, q: '' };
  let shown = 50;
  const fmt = n => n.toLocaleString('en-US');
  const years = [...new Set(rows.map(r => r[ADDED]).filter(Boolean))].sort((a, b) => a - b);
  state.from = years[0]; state.to = years[years.length - 1];

  const count = (list) => { const m = new Map(); list.forEach(v => m.set(v, (m.get(v) || 0) + 1)); return m; };
  const allGenres = [...count(rows.flatMap(r => r[GENRES]))].sort((a, b) => b[1] - a[1]);
  const allCountries = [...count(rows.flatMap(r => r[COUNTRIES]))].sort((a, b) => b[1] - a[1]);
  const fill = (sel, items) => items.forEach(([v, n]) => { const o = document.createElement('option'); o.value = v; o.textContent = `${v} (${fmt(n)})`; sel.appendChild(o); });
  fill($('#f-genre'), allGenres); fill($('#f-country'), allCountries.slice(0, 60));
  years.forEach(y => { ['#f-from', '#f-to'].forEach(s => { const o = document.createElement('option'); o.value = y; o.textContent = y; $(s).appendChild(o); }); });
  $('#f-from').value = state.from; $('#f-to').value = state.to;

  function filtered() {
    const q = state.q.toLowerCase();
    return rows.filter(r =>
      (state.type === 'all' || r[TYPE] === +state.type) &&
      (!state.genre || r[GENRES].includes(state.genre)) &&
      (!state.country || r[COUNTRIES].includes(state.country)) &&
      (r[ADDED] === null ? (state.from === years[0] && state.to === years[years.length - 1]) : (r[ADDED] >= state.from && r[ADDED] <= state.to)) &&
      (!q || r[T].toLowerCase().includes(q) || r[DIRS].some(d => d.toLowerCase().includes(q))));
  }
  const median = a => { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };

  function hbars(el, entries, key) {
    const max = Math.max(1, ...entries.map(e => e[1]));
    el.innerHTML = entries.map(([k, v]) => `<div class="hb${state[key] === k ? ' sel' : ''}" data-k="${k.replace(/"/g, '&quot;')}"><span title="${k.replace(/"/g, '&quot;')}">${k}</span><div class="tr"><div class="fl" style="width:${v / max * 100}%"></div></div><b>${fmt(v)}</b></div>`).join('') || '<p style="color:var(--mut);font-size:13px">No titles match.</p>';
    if (key) el.querySelectorAll('.hb').forEach(d => d.onclick = () => { const v = d.dataset.k; state[key] = state[key] === v ? '' : v; $(key === 'genre' ? '#f-genre' : '#f-country').value = state[key]; if (key === 'country' && ![...$('#f-country').options].some(o => o.value === v)) state[key] = ''; render(); });
  }

  function columns(el, labels, series, colors, w = 640, h = 220) {
    const max = Math.max(1, ...labels.map((_, i) => series.reduce((s, a) => s + a[i], 0)));
    const bw = (w - 40) / labels.length, tip = $('#tip');
    let out = `<svg viewBox="0 0 ${w} ${h + 24}" role="img">`;
    [0, .5, 1].forEach(f => { const y = 10 + (h - 10) * (1 - f); out += `<line x1="34" x2="${w}" y1="${y}" y2="${y}" stroke="rgba(255,255,255,.07)"/><text x="30" y="${y + 4}" text-anchor="end" fill="#a8959a" font-size="10">${fmt(Math.round(max * f))}</text>`; });
    labels.forEach((l, i) => {
      let y = h; const x = 40 + i * bw;
      series.forEach((a, si) => { const bh = (h - 10) * a[i] / max; y -= bh; out += `<rect class="bar" x="${x + bw * .12}" y="${y}" width="${bw * .76}" height="${bh}" rx="2" fill="${colors[si]}" data-t="${l}: ${fmt(a[i])}"/>`; });
      if (labels.length <= 14 || i % 2 === 0) out += `<text x="${x + bw / 2}" y="${h + 16}" text-anchor="middle" fill="#a8959a" font-size="10">${l}</text>`;
    });
    el.innerHTML = out + '</svg>';
    el.querySelectorAll('rect').forEach(r => { r.onmousemove = e => { tip.style.display = 'block'; tip.textContent = r.dataset.t; tip.style.left = e.clientX + 12 + 'px'; tip.style.top = e.clientY + 12 + 'px'; }; r.onmouseleave = () => tip.style.display = 'none'; });
  }

  function render() {
    const d = filtered();
    const movies = d.filter(r => r[TYPE] === 0), shows = d.filter(r => r[TYPE] === 1);
    const mins = movies.map(r => r[DUR]).filter(v => v !== null);
    $('#kpis').innerHTML = [
      [fmt(d.length), 'titles match'],
      [d.length ? Math.round(movies.length / d.length * 100) + '%' : '0%', `movies (${fmt(movies.length)} movies, ${fmt(shows.length)} shows)`],
      [mins.length ? Math.round(median(mins)) + ' min' : 'n/a', 'median movie length'],
      [d.length ? Math.round(median(d.map(r => r[REL]))) : 'n/a', 'median release year']
    ].map(([b, s]) => `<div class="kpi"><b>${b}</b><span>${s}</span></div>`).join('');

    const yl = years.filter(y => y >= state.from && y <= state.to);
    const per = t => yl.map(y => d.filter(r => r[ADDED] === y && r[TYPE] === t).length);
    columns($('#c-year'), yl.map(String), [per(0), per(1)], ['#ff3b4a', '#ffb4a8']);
    hbars($('#c-genre'), [...count(d.flatMap(r => r[GENRES]))].sort((a, b) => b[1] - a[1]).slice(0, 10), 'genre');
    hbars($('#c-country'), [...count(d.flatMap(r => r[COUNTRIES]))].sort((a, b) => b[1] - a[1]).slice(0, 10), 'country');
    hbars($('#c-rating'), [...count(d.map(r => r[RATING]).filter(Boolean))].sort((a, b) => b[1] - a[1]).slice(0, 8), null);

    if (state.type === '1') {
      $('#t-dur').textContent = 'TV show seasons';
      const s = [...count(shows.map(r => r[DUR]).filter(v => v !== null))].sort((a, b) => a[0] - b[0]);
      const labels = s.map(x => String(x[0]));
      columns($('#c-dur'), labels, [s.map(x => x[1])], ['#ffb4a8'], 480, 180);
    } else {
      $('#t-dur').textContent = 'Movie length (minutes)';
      const bins = [...Array(12).keys()].map(i => 30 + i * 15);
      const cnt = bins.map((b, i) => mins.filter(m => (i === 0 ? m < b + 15 : m >= b && m < b + 15) || (i === bins.length - 1 && m >= b + 15)).length);
      columns($('#c-dur'), bins.map((b, i) => i === bins.length - 1 ? b + '+' : String(b)), [cnt], ['#ff3b4a'], 480, 180);
    }

    const sorted = [...d].sort((a, b) => b[REL] - a[REL] || a[T].localeCompare(b[T]));
    $('#count').textContent = `${fmt(d.length)} total, newest releases first`;
    $('#rows').innerHTML = sorted.slice(0, shown).map(r => `<tr><td>${esc(r[T])}</td><td>${r[TYPE] ? 'TV show' : 'Movie'}</td><td>${r[REL]}</td><td>${r[ADDED] ?? ''}</td><td>${r[RATING] ?? ''}</td><td>${r[DUR] === null ? '' : r[DUR] + (r[TYPE] ? (r[DUR] > 1 ? ' seasons' : ' season') : ' min')}</td><td>${esc(r[COUNTRIES].slice(0, 2).join(', '))}</td><td>${esc(r[GENRES].join(', '))}</td></tr>`).join('');
    $('#more').style.display = sorted.length > shown ? '' : 'none';
  }
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  document.body.insertAdjacentHTML('beforeend', '<div class="tip" id="tip"></div>');

  document.querySelectorAll('#f-type button').forEach(b => b.onclick = () => { document.querySelectorAll('#f-type button').forEach(x => x.classList.remove('on')); b.classList.add('on'); state.type = b.dataset.v; shown = 50; render(); });
  $('#f-genre').onchange = e => { state.genre = e.target.value; shown = 50; render(); };
  $('#f-country').onchange = e => { state.country = e.target.value; shown = 50; render(); };
  $('#f-from').onchange = e => { state.from = +e.target.value; if (state.from > state.to) { state.to = state.from; $('#f-to').value = state.to; } shown = 50; render(); };
  $('#f-to').onchange = e => { state.to = +e.target.value; if (state.to < state.from) { state.from = state.to; $('#f-from').value = state.from; } shown = 50; render(); };
  let timer; $('#f-q').oninput = e => { clearTimeout(timer); timer = setTimeout(() => { state.q = e.target.value.trim(); shown = 50; render(); }, 150); };
  $('#more').onclick = () => { shown += 100; render(); };
  $('#reset').onclick = () => { Object.assign(state, { type: 'all', genre: '', country: '', from: years[0], to: years[years.length - 1], q: '' }); $('#f-genre').value = ''; $('#f-country').value = ''; $('#f-from').value = state.from; $('#f-to').value = state.to; $('#f-q').value = ''; document.querySelectorAll('#f-type button').forEach(x => x.classList.toggle('on', x.dataset.v === 'all')); shown = 50; render(); };
  render();
})();
