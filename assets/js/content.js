/* Karma: lädt content.json und setzt alle Texte, Preise, Öffnungszeiten, Galerie und Speisekarte ein.
   Ist content.json fehlerhaft, greift die Sicherheitskopie aus content-fallback.js. */
(function () {
  'use strict';

  var root = document.documentElement;
  var data = null;

  function $$(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }

  function get(path) {
    var parts = String(path).split('.');
    var cur = data;
    for (var i = 0; i < parts.length; i++) {
      if (cur == null) return undefined;
      cur = cur[parts[i]];
    }
    return cur;
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  /* ---------- einfache Bindungen ---------- */

  function bindText() {
    $$('[data-c]').forEach(function (n) {
      var v = get(n.getAttribute('data-c'));
      if (v != null) n.textContent = v;
    });
    $$('[data-attr]').forEach(function (n) {
      n.getAttribute('data-attr').split(';').forEach(function (pair) {
        var kv = pair.split('=');
        var v = get(kv[1]);
        if (v != null) n.setAttribute(kv[0].trim(), v);
      });
    });
    // Text mit einem kursiven Wort, z. B. "Peanut <em>Power</em>"
    $$('[data-rich]').forEach(function (n) {
      var text = get(n.getAttribute('data-rich')) || '';
      var it = get(n.getAttribute('data-rich-italic')) || '';
      n.textContent = '';
      var idx = it ? text.indexOf(it) : -1;
      if (idx < 0) { n.textContent = text; return; }
      if (idx > 0) n.appendChild(document.createTextNode(text.slice(0, idx)));
      n.appendChild(el('em', null, it));
      if (idx + it.length < text.length) n.appendChild(document.createTextNode(text.slice(idx + it.length)));
    });
    $$('[data-list]').forEach(function (n) {
      var list = get(n.getAttribute('data-list')) || [];
      n.textContent = '';
      list.forEach(function (t) { n.appendChild(el('li', null, t)); });
    });
  }

  function bindLinks() {
    $$('[data-google]').forEach(function (a) { a.href = get('cafe.google_link'); });
    $$('[data-instagram]').forEach(function (a) { a.href = get('cafe.instagram_link'); });
    $$('[data-route]').forEach(function (a) { a.href = get('cafe.route_link'); });
    var stars = parseFloat(String(get('cafe.google_sterne') || '0').replace(',', '.')) || 0;
    $$('.stars').forEach(function (s) {
      s.style.setProperty('--fill', Math.max(0, Math.min(100, stars / 5 * 100)) + '%');
      s.setAttribute('aria-label', get('cafe.google_sterne') + ' ' + (get('bedienhilfen.sterne_label') || ''));
    });
    var seo = get('seo') || {};
    if (seo.seitentitel) document.title = seo.seitentitel;
    var md = document.querySelector('meta[name="description"]');
    if (md && seo.beschreibung) md.setAttribute('content', seo.beschreibung);
    var foot = document.querySelector('[data-render-footer]');
    if (foot) {
      var k = get('bildkennzeichnung') || {};
      if (k.footer_text_anzeigen) foot.textContent = k.footer_text; else foot.remove();
    }
    // Siegel: Text wiederholen, bis der Kreis voll ist
    var seal = document.querySelector('[data-seal-text]');
    if (seal) seal.textContent = (get('hero.siegel_text') || '').repeat(2);
  }

  /* ---------- Öffnungszeiten (immer nach deutscher Zeit) ---------- */

  var DAYS = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];

  function berlinNow() {
    try {
      var f = new Intl.DateTimeFormat('de-DE', { timeZone: 'Europe/Berlin', weekday: 'long', hour: '2-digit', minute: '2-digit', hour12: false });
      var parts = {};
      f.formatToParts(new Date()).forEach(function (p) { parts[p.type] = p.value; });
      return { day: parts.weekday, minutes: parseInt(parts.hour, 10) % 24 * 60 + parseInt(parts.minute, 10) };
    } catch (e) {
      var d = new Date();
      return { day: DAYS[d.getDay()], minutes: d.getHours() * 60 + d.getMinutes() };
    }
  }

  function toMin(hhmm) {
    var p = hhmm.split(':');
    return parseInt(p[0], 10) * 60 + parseInt(p[1] || '0', 10);
  }

  function shortTime(hhmm) {
    var p = hhmm.split(':');
    var h = String(parseInt(p[0], 10));
    return p[1] && p[1] !== '00' ? h + ':' + p[1] : h;
  }

  function hours() {
    var oz = get('oeffnungszeiten') || {};
    var tage = oz.tage || [];
    var now = berlinNow();
    var dl = document.querySelector('[data-hours]');
    if (dl) {
      dl.textContent = '';
      tage.forEach(function (t) {
        var dt = el('dt', null, t.tag);
        var dd = el('dd', null, (t.zeiten && t.zeiten.length)
          ? t.zeiten.map(function (z) { return z.replace('-', '–'); }).join(', ')
          : (oz.geschlossen_text || 'geschlossen'));
        if (t.tag === now.day) { dt.className = 'is-today'; dd.className = 'is-today'; }
        dl.appendChild(dt);
        dl.appendChild(dd);
      });
    }
    var today = null;
    tage.forEach(function (t) { if (t.tag === now.day) today = t; });
    var open = false, until = '', from = '';
    if (today && today.zeiten) {
      today.zeiten.forEach(function (z) {
        var ab = z.split('-');
        if (now.minutes >= toMin(ab[0]) && now.minutes < toMin(ab[1])) { open = true; until = ab[1]; }
        else if (!from && now.minutes < toMin(ab[0])) { from = ab[0]; }
      });
    }
    var nav = get('navigation') || {};
    var text = open
      ? nav.heute_offen + ' ' + nav.bis + ' ' + shortTime(until) + ' ' + nav.uhr
      : (from ? nav.heute_zu + ', ' + nav.ab + ' ' + shortTime(from) + ' ' + nav.uhr : nav.heute_zu);
    $$('[data-status]').forEach(function (a) { a.classList.toggle('is-closed', !open); });
    $$('[data-status-text]').forEach(function (s) { s.textContent = text; });
    $$('[data-status-long]').forEach(function (p) {
      p.textContent = '';
      var d = el('i', 'dot');
      if (!open) d.style.background = 'var(--berry-ink)';
      p.appendChild(d);
      p.appendChild(document.createTextNode(text));
    });
  }

  /* ---------- Galerie ---------- */

  function gallery() {
    var grid = document.querySelector('[data-gallery-grid]');
    if (!grid) return;
    grid.textContent = '';
    (get('impressionen.bilder') || []).forEach(function (b, i) {
      var li = el('li', 'shot');
      var fig = el('figure', 'shot__fig');
      var frame = el('div', 'shot__frame');
      var img = el('img');
      img.src = b.bild;
      img.alt = b.beschreibung || '';
      img.loading = 'lazy';
      img.decoding = 'async';
      img.width = 800; img.height = 1000;
      frame.appendChild(img);
      fig.appendChild(frame);
      var cap = el('figcaption');
      cap.appendChild(el('b', null, b.bildunterschrift || ''));
      cap.appendChild(el('span', null, String(i + 1).padStart(2, '0')));
      fig.appendChild(cap);
      li.appendChild(fig);
      grid.appendChild(li);
    });
  }

  /* ---------- Speisekarte ---------- */

  function menu() {
    var wrap = document.querySelector('[data-menu]');
    var tabs = document.querySelector('[data-menu-tabs]');
    if (!wrap) return;
    wrap.textContent = '';
    if (tabs) tabs.textContent = '';
    (get('speisekarte.kategorien') || []).forEach(function (k) {
      var id = 'karte-' + (k.id || k.name.toLowerCase().replace(/[^a-z0-9]+/g, '-'));
      if (tabs) {
        var t = el('a', 'menu__tab', k.name);
        t.href = '#' + id;
        tabs.appendChild(t);
      }
      var sec = el('section', 'menu__cat');
      sec.id = id;
      var h = el('h3', null, k.name);
      h.appendChild(el('span', null, String((k.eintraege || []).length).padStart(2, '0')));
      sec.appendChild(h);
      var ul = el('ul', 'menu__list');
      (k.eintraege || []).forEach(function (e) {
        var li = el('li', 'dish');
        if (e.bild) {
          var img = el('img', 'dish__img');
          img.src = e.bild;
          img.alt = '';
          img.loading = 'lazy';
          img.decoding = 'async';
          img.width = 128; img.height = 128;
          li.appendChild(img);
        }
        li.appendChild(el('span', 'dish__name', e.name));
        li.appendChild(el('span', 'dish__price', e.preis));
        li.appendChild(el('span', 'dish__desc', e.beschreibung));
        ul.appendChild(li);
      });
      sec.appendChild(ul);
      wrap.appendChild(sec);
    });
  }

  /* ---------- Matcha-Schichten ---------- */

  function layers() {
    var ol = document.querySelector('[data-layers]');
    if (!ol) return;
    ol.textContent = '';
    (get('matcha.schichten') || []).forEach(function (s) {
      var li = el('li');
      li.appendChild(el('i', 'layers__line'));
      var box = el('span');
      var top = el('span', 'layers__num', s.nummer);
      box.appendChild(top);
      box.appendChild(el('span', 'layers__name', ' ' + s.name));
      box.appendChild(el('span', 'layers__text', s.text));
      li.appendChild(box);
      ol.appendChild(li);
    });
  }

  /* Euro-Zeichen in der Grundschrift setzen (in der Bodoni sieht es aus wie ein C) */
  function currency() {
    $$('.copy__price strong, .dish__price').forEach(function (n) {
      var t = n.textContent;
      var i = t.lastIndexOf('€');
      if (i < 0) return;
      n.textContent = t.slice(0, i).replace(/\s+$/, '');
      n.appendChild(el('span', 'cur', '€'));
    });
  }

  function apply() {
    bindText();
    bindLinks();
    hours();
    gallery();
    menu();
    layers();
    currency();
    root.classList.add('content-ready');
    window.KARMA_CONTENT = data;
    document.dispatchEvent(new CustomEvent('karma:content', { detail: data }));
    setInterval(hours, 60000);
  }

  function useFallback(reason) {
    if (reason) console.warn('content.json konnte nicht gelesen werden, die Sicherheitskopie wird angezeigt.\n' + reason);
    data = window.KARMA_FALLBACK || {};
    apply();
  }

  fetch('content.json', { cache: 'no-cache' })
    .then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.text();
    })
    .then(function (txt) {
      try { data = JSON.parse(txt); }
      catch (e) {
        var m = /position (\d+)/.exec(e.message);
        var line = m ? txt.slice(0, +m[1]).split('\n').length : '?';
        throw new Error('Fehler in content.json, ungefähr in Zeile ' + line + ': ' + e.message);
      }
      apply();
    })
    .catch(function (e) { useFallback(e.message); });
})();
