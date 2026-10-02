/* Karma: Scroll-Choreografie mit GSAP, ScrollTrigger, SplitText und Lenis (alles lokal).
   Jede Sorte ist eine gepinnte Szene mit eigener Bewegungsidee; der Scrollbalken ist der Abspielkopf.
   Bei "Bewegung reduzieren" läuft nichts davon: Die Seite zeigt alle Becher statisch (siehe style.css). */
(function () {
  'use strict';

  var root = document.documentElement;
  if (!root.classList.contains('motion-ok')) return;

  function $(sel, el) { return (el || document).querySelector(sel); }
  function $$(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

  var lenis = null;
  var manifest = null;
  var isMobile = function () { return window.innerWidth < 768; };

  /* ======================================================================
     Laden: Bilder vorladen und dekodieren, damit beim Scrollen nichts nachploppt
     ====================================================================== */

  var cache = {};
  var queue = [];
  var active = 0;

  function loadImg(src, prio) {
    if (cache[src]) return cache[src].p;
    var entry = { src: src, img: null };
    entry.p = new Promise(function (res) { entry.res = res; });
    cache[src] = entry;
    queue.push({ e: entry, prio: prio || 5 });
    queue.sort(function (a, b) { return a.prio - b.prio; });
    pump();
    return entry.p;
  }

  function pump() {
    while (active < 6 && queue.length) {
      var job = queue.shift();
      active++;
      (function (e) {
        var im = new Image();
        im.decoding = 'async';
        im.onload = function () {
          var done = function () { e.img = im; active--; e.res(im); pump(); };
          if (im.decode) im.decode().then(done, done); else done();
        };
        im.onerror = function () { active--; e.res(null); pump(); };
        im.src = e.src;
      })(job.e);
    }
  }

  function loaded(src) { return cache[src] && cache[src].img; }

  /* ======================================================================
     Bildfolge auf Canvas (mit weicher Überblendung zwischen zwei Bildern)
     ====================================================================== */

  function Seq(canvas, urls) {
    this.c = canvas;
    this.x = canvas.getContext('2d');
    this.urls = urls;
    this.n = urls.length;
    this.f = 0;
    this.key = '';
  }
  Seq.prototype.preload = function (prio, from, to) {
    var self = this;
    from = from || 0; to = to == null ? this.n - 1 : to;
    var ps = [];
    for (var i = from; i <= to; i++) ps.push(loadImg(this.urls[i], prio).then(function () { self.redraw(); }));
    return Promise.all(ps);
  };
  Seq.prototype.resize = function () {
    var r = this.c.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = Math.max(2, Math.round(r.width * dpr));
    var h = Math.max(2, Math.round(r.height * dpr));
    if (this.c.width !== w || this.c.height !== h) { this.c.width = w; this.c.height = h; }
    this.key = '';
    this.draw(this.f);
  };
  Seq.prototype.nearest = function (i) {
    for (var d = 1; d < this.n; d++) {
      var lo = i - d, hi = i + d;
      if (this.loop) { lo = (lo + this.n) % this.n; hi = hi % this.n; }
      var a = lo >= 0 ? loaded(this.urls[lo]) : null;
      if (a) return a;
      var b = hi < this.n ? loaded(this.urls[hi]) : null;
      if (b) return b;
    }
    return null;
  };
  Seq.prototype.draw = function (f) {
    this.f = f;
    var loop = this.loop;
    var n = this.n;
    var i = Math.floor(f);
    var t = f - i;
    if (loop) { i = ((i % n) + n) % n; } else { i = clamp(i, 0, n - 1); if (i === n - 1) t = 0; }
    var j = loop ? (i + 1) % n : Math.min(n - 1, i + 1);
    t = Math.round(t * 20) / 20;
    var key = i + ':' + t;
    if (key === this.key) return;
    var a = loaded(this.urls[i]) || this.nearest(i);
    if (!a) return;
    this.key = loaded(this.urls[i]) ? key : '';
    var ctx = this.x, W = this.c.width, H = this.c.height;
    ctx.clearRect(0, 0, W, H);
    ctx.globalAlpha = 1;
    ctx.drawImage(a, 0, 0, W, H);
    var b = t > 0.04 ? loaded(this.urls[j]) : null;
    if (b) { ctx.globalAlpha = t; ctx.drawImage(b, 0, 0, W, H); ctx.globalAlpha = 1; }
  };
  Seq.prototype.redraw = function () { this.key = ''; this.draw(this.f); };

  /* ======================================================================
     Bühne aufbauen: Canvas + passgenaue Ebenen aus manifest.json
     ====================================================================== */

  function buildStage(id) {
    var stage = $('[data-stage="' + id + '"]');
    var m = manifest[id];
    if (!stage || !m) return null;
    var mob = isMobile();
    var S = { el: stage, m: m, final: $('.stage__final', stage), shadow: $('.stage__shadow', stage), layers: {}, list: [] };
    if (m.seq) {
      var cv = document.createElement('canvas');
      cv.className = 'stage__seq';
      cv.setAttribute('aria-hidden', 'true');
      stage.insertBefore(cv, S.final);
      var count = mob ? m.seq.countM : m.seq.count;
      var dir = mob ? m.seq.dirM : m.seq.dir;
      var urls = [];
      for (var i = 0; i < count; i++) urls.push(dir + String(i).padStart(3, '0') + '.webp');
      S.seq = new Seq(cv, urls);
      S.canvas = cv;
    }
    if (m.base) {
      var b = document.createElement('img');
      b.className = 'stage__base';
      b.alt = '';
      b.setAttribute('aria-hidden', 'true');
      b.decoding = 'async';
      b.src = mob ? m.baseM : m.base;
      b.style.opacity = 0;
      stage.insertBefore(b, S.final);
      S.base = b;
    }
    if (m.layers) {
      var wrap = document.createElement('div');
      wrap.className = 'stage__layers';
      wrap.setAttribute('aria-hidden', 'true');
      m.layers.forEach(function (L) {
        var im = document.createElement('img');
        im.className = 'stage__layer';
        im.alt = '';
        im.decoding = 'async';
        im.src = L.src;
        im.style.left = (L.x * 100) + '%';
        im.style.top = (L.y * 100) + '%';
        im.style.width = (L.w * 100) + '%';
        im.style.opacity = 0;
        wrap.appendChild(im);
        S.layers[L.name] = im;
        S.list.push({ name: L.name, el: im, L: L });
      });
      stage.appendChild(wrap);
      S.wrap = wrap;
    }
    // Zentrierung aus dem CSS übernehmen, damit GSAP die Verschiebung sauber verwaltet
    var centerX = mob || id === 'classic' || id === 'peanut';
    var centerY = !mob || id === 'classic';
    gsap.set(stage, { xPercent: centerX ? -50 : 0, yPercent: centerY ? -50 : 0, x: 0, y: 0 });
    S.W = function () { return stage.offsetWidth; };
    S.H = function () { return stage.offsetHeight; };
    return S;
  }

  function teardownStages() {
    $$('.stage__seq, .stage__base, .stage__layers, .stage__fx').forEach(function (n) { n.remove(); });
  }

  /* ======================================================================
     Grundgerüst: Lenis + ScrollTrigger
     ====================================================================== */

  function setupScroll() {
    gsap.registerPlugin(ScrollTrigger, SplitText);
    ScrollTrigger.config({ ignoreMobileResize: true });
    if (window.Lenis) {
      lenis = new Lenis({ lerp: 0.1, wheelMultiplier: 0.9, smoothWheel: true, syncTouch: false });
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    }
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute('href').slice(1);
      var y = anchorY(id);
      if (y == null) return;
      e.preventDefault();
      if (lenis) lenis.scrollTo(y, { duration: 1.6 }); else window.scrollTo(0, y);
      history.replaceState(null, '', '#' + id);
    });
  }

  var anchors = {};
  function anchorY(id) {
    if (id === 'top') return 0;
    if (anchors[id]) return anchors[id]();
    var t = document.getElementById(id);
    if (!t) return null;
    return t.getBoundingClientRect().top + window.scrollY - (id.indexOf('karte-') === 0 ? 120 : 0);
  }

  /* ---------- kleine Helfer für Text ---------- */

  function has(t) { return t && (t.length === undefined ? true : t.length > 0); }

  function lines(el) {
    if (!el) return [];
    var s = SplitText.create(el, { type: 'lines', mask: 'lines', linesClass: 'ln', aria: 'none' });
    return s.lines;
  }
  function chars(el) {
    if (!el) return [];
    var s = SplitText.create(el, { type: 'words,chars', charsClass: 'char', mask: 'chars' });
    return s.chars;
  }

  /* Text einer Sorte zeilenweise einblenden (in eine Szenen-Timeline) */
  function revealCopy(tl, copy, at, span) {
    var kicker = $$('.copy__kicker', copy);
    var name = $$('.copy__name', copy);
    var nameChars = [];
    name.forEach(function (n) { nameChars = nameChars.concat(chars(n)); });
    var txt = [];
    $$('.copy__sub, .copy__text', copy).forEach(function (p) { txt = txt.concat(lines(p)); });
    var meta = $$('.copy__label, .copy__ingredients li, .copy__price', copy);
    var line = $$('.copy__meta', copy);
    gsap.set(copy, { autoAlpha: 1 });
    if (has(kicker)) tl.from(kicker, { yPercent: 100, autoAlpha: 0, duration: span * .3, ease: 'power2.out' }, at);
    if (has(nameChars)) tl.from(nameChars, { yPercent: 110, duration: span * .5, stagger: span * .04, ease: 'power3.out' }, at + span * .05);
    if (has(txt)) tl.from(txt, { yPercent: 105, duration: span * .45, stagger: span * .06, ease: 'power3.out' }, at + span * .3);
    if (has(line)) tl.fromTo(line, { '--rule': 0 }, { '--rule': 1, duration: span * .4, ease: 'power2.out' }, at + span * .45);
    if (has(meta)) tl.from(meta, { y: 18, autoAlpha: 0, duration: span * .35, stagger: span * .05, ease: 'power2.out' }, at + span * .55);
    return tl;
  }

  function pinTl(section, len, extra) {
    var pin = $('[data-pin]', section);
    return gsap.timeline({
      defaults: { ease: 'none' },
      scrollTrigger: Object.assign({
        trigger: section, start: 'top top', end: function () { return '+=' + Math.round(window.innerHeight * len()); },
        pin: pin, scrub: isMobile() ? 0.5 : 0.7, anticipatePin: 1, invalidateOnRefresh: true
      }, extra || {})
    });
  }

  function tintIn(name, section) {
    var t = $('[data-tint="' + name + '"]');
    if (!t || !section) return;
    gsap.fromTo(t, { opacity: 0 }, {
      opacity: 1, ease: 'none',
      scrollTrigger: { trigger: section, start: 'top 85%', end: 'top 10%', scrub: true }
    });
  }

  /* ======================================================================
     1 · Opener: Hero -> Classic (derselbe Becher)
     ====================================================================== */

  /* Zielpunkte der Toppings auf dem Höhepunkt: Mittelpunkt als Anteil der Bühne (0..1), Drehung, Größe */
  var CLASSIC_ORBIT = {
    strawberry_1: [-0.02, 0.30, -28, 1.22],
    strawberry_2: [1.12, 0.14, 34, 1.12],
    banana_1: [1.18, 0.50, 48, 1.08],
    banana_2: [-0.08, 0.64, -40, 1.1],
    granola_1: [0.56, 0.02, 18, 1.2],
    granola_2: [0.10, 0.06, -22, 1.1],
    granola_3: [0.98, -0.02, 60, 1.05]
  };
  var CLASSIC_ORBIT_M = {
    strawberry_1: [0.02, 0.10, -28, 1.1],
    strawberry_2: [0.98, 0.06, 34, 1.05],
    banana_1: [1.02, 0.42, 48, 1.0],
    banana_2: [-0.02, 0.48, -40, 1.0],
    granola_1: [0.52, -0.02, 18, 1.1],
    granola_2: [0.24, 0.0, -22, 1.0],
    granola_3: [0.78, 0.0, 60, 1.0]
  };
  function toTarget(l, o, W, H) {
    var cx = l.L.x + l.L.w / 2, cy = l.L.y + l.L.h / 2;
    return { x: function () { return (o[0] - cx) * W(); }, y: function () { return (o[1] - cy) * H(); } };
  }

  function opener(S, mob) {
    var sec = $('[data-opener]');
    var w1 = $('.hero__word--1'), w2 = $('.hero__word--2');
    var meta = $$('.hero__meta, .hero__rating, .hero__cue');
    var seal = $('[data-seal]');
    var copy = $('[data-copy="classic"]');
    var tint = $('[data-tint="acai"]');
    var tl = pinTl(sec, function () { return mob ? 4.2 : 5.4; });
    var W = S.W, H = S.H;
    var ORB = mob ? CLASSIC_ORBIT_M : CLASSIC_ORBIT;

    S.seq.loop = true;
    gsap.set(copy, { autoAlpha: 0 });

    tl.to(w1, { xPercent: -60, x: function () { return -window.innerWidth * 0.25; }, autoAlpha: 0, duration: 1.4, ease: 'power2.in' }, 0)
      .to(w2, { xPercent: 60, x: function () { return window.innerWidth * 0.25; }, autoAlpha: 0, duration: 1.4, ease: 'power2.in' }, 0)
      .to(meta, { y: -40, autoAlpha: 0, duration: .8, stagger: .05 }, 0)
      .to(seal, { rotation: 300, duration: 10 }, 0)
      .to(seal, { y: function () { return -window.innerHeight * 0.4; }, autoAlpha: 0, duration: 2, ease: 'power2.in' }, .2)
      .fromTo(tint, { opacity: 0 }, { opacity: 1, duration: 1.3 }, .1)
      .fromTo(S.el, { x: function () { return mob ? 0 : window.innerWidth * 0.19; } }, {
        x: function () { return mob ? 0 : -window.innerWidth * 0.22; },
        y: function () { return mob ? -window.innerHeight * 0.06 : 0; },
        scale: mob ? 0.86 : 0.94, duration: 1.7, ease: 'power2.inOut'
      }, 0)
      // Wechsel vom fertigen Bild auf Becher + einzelne Toppings (pixelgenau deckungsgleich)
      .set(S.canvas, { opacity: 1 }, .98)
      .set(S.list.map(function (l) { return l.el; }), { opacity: 1 }, .98)
      .set(S.final, { opacity: 0 }, 1.0);

    var proxy = { f: 0 };
    tl.to(proxy, { f: S.seq.n, duration: 6.6, ease: 'power1.inOut', onUpdate: function () { S.seq.draw(proxy.f); } }, 1.0);

    // Toppings heben ab und kreisen um den Becher
    S.list.forEach(function (l, k) {
      var o = ORB[l.name] || [0.5, 0.0, 20, 1];
      var t = toTarget(l, o, W, H);
      tl.to(l.el, { x: t.x, y: t.y, rotation: o[2], scale: o[3], duration: 2.2, ease: 'power2.inOut' }, 1.05 + k * 0.07);
      // leichtes Schweben auf dem Höhepunkt
      tl.to(l.el, { y: function () { return t.y() - (0.025 + 0.012 * (k % 3)) * H(); }, rotation: o[2] + (k % 2 ? 12 : -12), duration: 2.4, ease: 'sine.inOut' }, 3.3 + k * 0.04);
    });

    revealCopy(tl, copy, 2.0, 2.6);

    // Toppings landen nacheinander auf dem Rand
    var order = ['granola_2', 'granola_1', 'granola_3', 'banana_2', 'banana_1', 'strawberry_2', 'strawberry_1'];
    order.forEach(function (name, k) {
      var el = S.layers[name];
      if (!el) return;
      var at = 5.7 + k * 0.28;
      tl.to(el, { x: 0, y: function () { return 0.012 * H(); }, rotation: 0, scale: 1, duration: 0.9, ease: 'power3.in' }, at)
        .to(el, { y: 0, duration: 0.35, ease: 'power2.out' }, at + 0.9);
    });
    tl.to(S.final, { opacity: 1, duration: .2 }, 8.45)
      .set([S.canvas].concat(S.list.map(function (l) { return l.el; })), { opacity: 0 }, 8.66)
      .to({}, { duration: 1.3 }, 8.7);

    anchors.sorten = function () { return tl.scrollTrigger.start + (tl.scrollTrigger.end - tl.scrollTrigger.start) * 0.46; };
    return tl;
  }

  /* ======================================================================
     2 · Tropical: Becher füllt sich, Früchte schweben in Tiefenebenen und landen
     ====================================================================== */

  var TROP_FLOAT = {
    mango_1: [-1.15, 0.05, -30, 1.35], mango_2: [1.05, -0.12, 40, 1.2], mango_3: [-0.9, 0.42, 18, 1.1],
    mango_4: [0.75, 0.36, -24, 1.45], mango_5: [1.25, 0.18, 60, 0.9], pineapple_1: [-0.7, -0.28, 50, 1.3],
    pineapple_2: [0.35, -0.42, -40, 1.15], pineapple_3: [-1.25, -0.08, 20, 1.0], coconut: [0.1, -0.5, 10, 1.1]
  };

  function tropical(S, mob) {
    var sec = $('[data-scene="tropical"]');
    var copy = $('[data-copy="tropical"]');
    var big = $('[data-bigtype]', sec);
    var tl = pinTl(sec, function () { return mob ? 3.6 : 4.4; });
    var W = S.W, H = S.H;
    var k = mob ? 0.5 : 1;
    tintIn('mango', sec);
    gsap.set(S.final, { opacity: 0 });
    gsap.set(S.canvas, { opacity: 1 });
    gsap.set(copy, { autoAlpha: 0 });

    // Deko-Ebenen mit Tiefenunschärfe (Kopien einzelner Früchte)
    var fx = document.createElement('div');
    fx.className = 'stage__fx';
    fx.setAttribute('aria-hidden', 'true');
    S.el.appendChild(fx);
    var decoDef = mob ? [['mango_2', -0.9, -0.5, 1.4, 4], ['pineapple_1', 0.95, 0.62, 1.3, 4]]
      : [['mango_2', -1.5, -0.35, 2.2, 6], ['pineapple_1', 1.55, 0.5, 2.0, 7], ['mango_4', 1.45, -0.55, 0.7, 2], ['pineapple_3', -1.35, 0.7, 0.6, 2.5]];
    var decos = [];
    decoDef.forEach(function (d) {
      var src = S.layers[d[0]];
      if (!src) return;
      var c = src.cloneNode();
      c.className = 'stage__layer stage__deco';
      c.style.filter = 'blur(' + d[4] + 'px)';
      c.style.opacity = 1;
      fx.appendChild(c);
      decos.push({ el: c, d: d });
    });

    var proxy = { f: 0 };
    S.seq.draw(0);
    tl.to(proxy, { f: S.seq.n - 1, duration: 6, ease: 'power1.inOut', onUpdate: function () { S.seq.draw(proxy.f); } }, 0);
    tl.fromTo(big, { xPercent: 0 }, { xPercent: -38, duration: 10 }, 0);

    S.list.forEach(function (l, i) {
      var o = TROP_FLOAT[l.name] || [1, 0, 0, 1];
      gsap.set(l.el, { opacity: 1, x: function () { return o[0] * W() * k; }, y: function () { return o[1] * H() * k + 0.3 * H(); }, rotation: o[2], scale: o[3] });
      // Parallax: jede Frucht schwebt in eigener Geschwindigkeit
      tl.to(l.el, { y: function () { return o[1] * H() * k - (0.06 + 0.04 * (i % 3)) * H(); }, rotation: o[2] + (i % 2 ? 25 : -25), duration: 6, ease: 'none' }, 0);
      tl.to(l.el, { x: 0, y: 0, rotation: 0, scale: 1, duration: 1.6, ease: 'power3.inOut' }, 6.0 + i * 0.12);
    });
    decos.forEach(function (o, i) {
      var d = o.d;
      gsap.set(o.el, { x: function () { return d[1] * W() * k; }, y: function () { return d[2] * H() * k + 0.4 * H(); }, scale: d[3] });
      tl.to(o.el, { y: function () { return d[2] * H() * k - (0.35 + 0.15 * i) * H(); }, rotation: i % 2 ? 90 : -70, duration: 10, ease: 'none' }, 0);
      tl.to(o.el, { autoAlpha: 0, duration: 1.2 }, 7 + i * 0.2);
    });
    revealCopy(tl, copy, 0.6, 2.6);
    tl.to(S.final, { opacity: 1, duration: .2 }, 8.0)
      .set([S.canvas].concat(S.list.map(function (l) { return l.el; })), { opacity: 0 }, 8.22)
      .to({}, { duration: 1.6 }, 8.3);
    return tl;
  }

  /* ======================================================================
     3 · Peanut Power: Drip läuft herunter, Becher kippt sanft
     ====================================================================== */

  function peanut(S, mob) {
    var sec = $('[data-scene="peanut"]');
    var copy = $('[data-copy="peanut"]');
    var a = $('[data-bigtype-a]', sec), b = $('[data-bigtype-b]', sec);
    var tl = pinTl(sec, function () { return mob ? 3.2 : 3.8; });
    tintIn('peanut', sec);
    gsap.set(S.final, { opacity: 0 });
    gsap.set(S.canvas, { opacity: 1 });
    gsap.set(copy, { autoAlpha: 1 });
    S.seq.draw(0);
    var proxy = { f: 0 };
    gsap.set(S.el, { transformOrigin: '50% 92%' });
    tl.fromTo(S.el, { y: function () { return S.H() * 0.12; }, rotation: -7 }, { y: 0, rotation: 0, duration: 1.6, ease: 'power2.out' }, 0)
      .to(proxy, { f: S.seq.n - 1, duration: 6, ease: 'power1.in', onUpdate: function () { S.seq.draw(proxy.f); } }, 1.4)
      .to(S.el, { rotation: -4.5, duration: 2.2, ease: 'sine.inOut' }, 1.6)
      .to(S.el, { rotation: 3.2, duration: 2.6, ease: 'sine.inOut' }, 3.8)
      .to(S.el, { rotation: 0, duration: 1.8, ease: 'sine.inOut' }, 6.4)
      .fromTo(a, { xPercent: 4 }, { xPercent: -30, duration: 10 }, 0)
      .fromTo(b, { xPercent: -34 }, { xPercent: 2, duration: 10 }, 0);
    var colA = $('.copy__col--a', copy), colB = $('.copy__col--b', copy);
    gsap.set([colA, colB], { autoAlpha: 0 });
    revealCopy(tl, colA, 0.7, 2.4);
    revealCopy(tl, colB, 3.2, 2.4);
    tl.to(S.final, { opacity: 1, duration: .2 }, 7.6)
      .set(S.canvas, { opacity: 0 }, 7.82)
      .to({}, { duration: 2 }, 7.9);
    return tl;
  }

  /* ======================================================================
     4 · Berry Blast: Explosion nach außen, dann zurück in den Becher
     ====================================================================== */

  function berry(S, mob) {
    var sec = $('[data-scene="berry"]');
    var copy = $('[data-copy="berry"]');
    var tl = pinTl(sec, function () { return mob ? 3.4 : 4.2; });
    var W = S.W, H = S.H;
    var k = mob ? 0.8 : 1;
    tintIn('berry', sec);
    gsap.set(copy, { autoAlpha: 0 });
    var cx = 0.5, cy = 0.24;
    var rnd = (function () { var s = 7; return function () { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; })();

    // zusätzliche Funken-Beeren für eine dichtere Explosion
    var fx = document.createElement('div');
    fx.className = 'stage__fx';
    fx.setAttribute('aria-hidden', 'true');
    S.el.appendChild(fx);
    var pool = S.list.filter(function (l) { return /blueberry|raspberry/.test(l.name); });
    var sparks = [];
    for (var i = 0; i < (mob ? 8 : 14); i++) {
      var src = pool[i % pool.length];
      if (!src) break;
      var c = src.el.cloneNode();
      c.className = 'stage__layer stage__deco';
      c.style.left = (cx * 100 - src.L.w * 50) + '%';
      c.style.top = (cy * 100 - src.L.h * 50) + '%';
      c.style.opacity = 0;
      if (i % 3 === 0) c.style.filter = 'blur(' + (3 + (i % 4)) + 'px)';
      fx.appendChild(c);
      var ang = (i / 14) * Math.PI * 2 + rnd() * 0.5;
      sparks.push({ el: c, ang: ang, dist: 0.5 + rnd() * 0.65, sc: 0.6 + rnd() * 1.3, rot: (rnd() - 0.5) * 540 });
    }

    var layerEls = S.list.map(function (l) { return l.el; });
    tl.set(S.base, { opacity: 1 }, 0.98)
      .set(layerEls, { opacity: 1 }, 0.98)
      .set(S.final, { opacity: 0 }, 1.0);

    // Explosion: die Beeren verteilen sich als Kranz um den ganzen Becher
    var N = S.list.length;
    S.list.forEach(function (l, i) {
      var lx = l.L.x + l.L.w / 2, ly = l.L.y + l.L.h / 2;
      var ang = (i / N) * Math.PI * 2 - Math.PI / 2 + (rnd() - 0.5) * 0.5;
      var rx = 0.62 + rnd() * 0.3, ry = 0.36 + rnd() * 0.16;
      var tx = 0.5 + Math.cos(ang) * rx, ty = 0.5 + Math.sin(ang) * ry;
      var dx = tx - lx, dy = ty - ly;
      var sc = 1.05 + rnd() * 0.75, rot = (rnd() - 0.5) * 420;
      tl.to(l.el, { x: function () { return dx * W() * k; }, y: function () { return dy * H() * k; }, scale: sc, rotation: rot, duration: 2.2, ease: 'expo.out' }, 1.0 + rnd() * 0.15)
        .to(l.el, { x: function () { return (dx + Math.cos(ang) * 0.06) * W() * k; }, y: function () { return (dy + Math.sin(ang) * 0.04 - 0.02) * H() * k; }, rotation: rot * 1.2, duration: 2.2, ease: 'sine.inOut' }, 3.2)
        .to(l.el, { x: 0, y: function () { return 0.01 * H(); }, scale: 0.98, rotation: 0, duration: 2.0, ease: 'power3.in' }, 5.4 + rnd() * 0.3)
        .to(l.el, { y: 0, scale: 1, duration: 0.4, ease: 'power2.out' }, 7.5);
    });
    sparks.forEach(function (s) {
      var dx = Math.cos(s.ang) * s.dist, dy = Math.sin(s.ang) * s.dist * 0.62 + 0.18;
      tl.set(s.el, { opacity: 1 }, 1.0)
        .fromTo(s.el, { x: 0, y: 0, scale: 0.3, rotation: 0 }, { x: function () { return dx * W() * k; }, y: function () { return dy * H() * k; }, scale: s.sc, rotation: s.rot, duration: 2.4, ease: 'expo.out' }, 1.0)
        .to(s.el, { x: 0, y: 0, scale: 0.2, rotation: 0, duration: 1.9, ease: 'power3.in' }, 5.5)
        .to(s.el, { opacity: 0, duration: 0.2 }, 7.2);
    });

    // Titel: Buchstaben fliegen mit und setzen sich zusammen
    gsap.set(copy, { autoAlpha: 1 });
    var nameChars = chars($('.copy__name', copy));
    nameChars.forEach(function (ch) {
      tl.fromTo(ch, { x: (rnd() - 0.5) * 380 * k, y: (rnd() - 0.5) * 300 * k, rotation: (rnd() - 0.5) * 140, autoAlpha: 0 },
        { x: 0, y: 0, rotation: 0, autoAlpha: 1, duration: 2.2, ease: 'power3.out' }, 1.3 + rnd() * 0.5);
    });
    var rest = [];
    $$('.copy__sub, .copy__text', copy).forEach(function (p) { rest = rest.concat(lines(p)); });
    tl.from($$('.copy__kicker', copy), { yPercent: 100, autoAlpha: 0, duration: .8 }, 1.0)
      .from(rest, { yPercent: 105, duration: 1.2, stagger: .14, ease: 'power3.out' }, 2.6)
      .fromTo($$('.copy__meta', copy), { '--rule': 0 }, { '--rule': 1, duration: 1.2, ease: 'power2.out' }, 3.2)
      .from($$('.copy__label, .copy__ingredients li, .copy__price', copy), { y: 18, autoAlpha: 0, duration: .9, stagger: .1 }, 3.4);
    tl.to(S.final, { opacity: 1, duration: .2 }, 7.9)
      .set([S.base].concat(layerEls), { opacity: 0 }, 8.12)
      .to({}, { duration: 1.8 }, 8.2);
    return tl;
  }

  /* ======================================================================
     5 · Matcha: Schichten setzen sich ab, Hintergrund läuft von Rot zu Grün
     ====================================================================== */

  function matcha(S, mob) {
    var sec = $('[data-scene="matcha"]');
    var copy = $('[data-copy="matcha"]');
    var labels = $$('[data-layers] li', sec);
    var tl = pinTl(sec, function () { return mob ? 3.8 : 4.8; });
    tintIn('strawberry', sec);
    var green = $('[data-tint="matcha"]');
    gsap.set(S.final, { opacity: 0 });
    gsap.set(S.canvas, { opacity: 1 });
    gsap.set(copy, { autoAlpha: 0 });
    S.seq.draw(0);

    function placeLabels() {
      var p = manifest.points || {};
      var r = S.el.getBoundingClientRect();
      var pr = sec.querySelector('[data-pin]').getBoundingClientRect();
      ['puree', 'milk', 'matcha'].forEach(function (key, i) {
        var li = labels[i];
        var pt = p[key];
        if (!li || !pt) return;
        var w = S.W(), h = S.H();
        li.style.left = (r.left - pr.left + pt.x * w + 10) + 'px';
        li.style.top = (r.top - pr.top + pt.y * h) + 'px';
        li.style.transform = 'translateY(-50%)';
      });
    }
    ScrollTrigger.addEventListener('refresh', placeLabels);
    cleanups.push(function () { ScrollTrigger.removeEventListener('refresh', placeLabels); });
    placeLabels();

    var proxy = { f: 0 };
    tl.to(proxy, { f: S.seq.n - 1, duration: 9, ease: 'none', onUpdate: function () { S.seq.draw(proxy.f); } }, 0)
      .fromTo(green, { opacity: 0 }, { opacity: 1, duration: 5, ease: 'sine.inOut' }, 3.2);
    revealCopy(tl, copy, 0.1, 2.2);
    // Beschriftung erscheint, wenn die jeweilige Schicht steht
    [[0.6, 2.7], [3.0, 5.9], [6.1, 8.8]].forEach(function (span, i) {
      var li = labels[i];
      if (!li) return;
      var ln = $('.layers__line', li), box = li.children[1];
      tl.from(ln, { scaleX: 0, duration: span[1] - span[0], ease: 'power2.out' }, span[0])
        .from(box, { x: -16, autoAlpha: 0, duration: (span[1] - span[0]) * .7, ease: 'power2.out' }, span[0] + .3);
    });
    tl.to(S.final, { opacity: 1, duration: .25 }, 9.0)
      .set(S.canvas, { opacity: 0 }, 9.26)
      .to({}, { duration: 1 }, 9.3);
    anchors.matcha = function () { return tl.scrollTrigger.start + (tl.scrollTrigger.end - tl.scrollTrigger.start) * 0.04; };
    return tl;
  }

  /* ======================================================================
     Galerie, Karte, Besuch: ruhigere, scroll-gekoppelte Einblendungen
     ====================================================================== */

  function quiet() {
    tintIn('cream', $('#impressionen'));
    quietText();
  }

  function quietText() {
    $$('[data-reveal]:not(.h2)').forEach(function (el) {
      var target = el.matches('p.lead, p.note') ? lines(el) : el;
      gsap.from(target, {
        yPercent: el.matches('p.lead, p.note') ? 105 : 0, y: el.matches('p.lead, p.note') ? 0 : 36, autoAlpha: el.matches('p.lead, p.note') ? 1 : 0,
        stagger: 0.08, ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 92%', end: 'top 64%', scrub: 0.6 }
      });
    });
    $$('.h2[data-reveal], .visit__title').forEach(function (h) {
      var cs = chars(h);
      gsap.from(cs, { yPercent: 110, stagger: 0.03, ease: 'power3.out', scrollTrigger: { trigger: h, start: 'top 90%', end: 'top 55%', scrub: 0.6 } });
    });
  }

  function quietGallery() {
    $$('.shot').forEach(function (s, i) {
      var img = $('img', s), frame = $('.shot__frame', s);
      gsap.fromTo(frame, { scale: 0.9, autoAlpha: 0, y: 60 }, {
        scale: 1, autoAlpha: 1, y: 0, ease: 'power2.out',
        scrollTrigger: { trigger: s, start: 'top 98%', end: 'top 55%', scrub: 0.6 }
      });
      gsap.fromTo(img, { yPercent: -7 }, {
        yPercent: 7, ease: 'none',
        scrollTrigger: { trigger: s, start: 'top bottom', end: 'bottom top', scrub: true }
      });
      gsap.to(s, { y: -60 - 40 * (i % 3), ease: 'none', scrollTrigger: { trigger: '.gallery__grid', start: 'top bottom', end: 'bottom top', scrub: true } });
    });
  }

  function quietMenu() {
    $$('.menu__cat').forEach(function (cat) {
      gsap.from($('h3', cat), { y: 24, autoAlpha: 0, ease: 'power2.out', scrollTrigger: { trigger: cat, start: 'top 90%', end: 'top 70%', scrub: 0.6 } });
      gsap.from($$('.dish', cat), { y: 26, autoAlpha: 0, stagger: 0.12, ease: 'power2.out', scrollTrigger: { trigger: cat, start: 'top 85%', end: 'top 40%', scrub: 0.6 } });
      var tab = $('.menu__tab[href="#' + cat.id + '"]');
      if (tab) ScrollTrigger.create({ trigger: cat, start: 'top 55%', end: 'bottom 55%', toggleClass: { targets: tab, className: 'is-active' } });
    });
    var mark = $('[data-visit-mark]');
    if (mark) gsap.fromTo(mark, { yPercent: 35 }, { yPercent: 0, ease: 'none', scrollTrigger: { trigger: mark, start: 'top bottom', end: 'bottom bottom', scrub: true } });
    gsap.from($$('.visit__block'), { y: 50, autoAlpha: 0, stagger: 0.15, ease: 'power2.out', scrollTrigger: { trigger: '.visit__side', start: 'top 90%', end: 'top 50%', scrub: 0.6 } });

    var nav = $('[data-nav]');
    ScrollTrigger.create({
      trigger: '#impressionen', start: 'top top+=80',
      onEnter: function () { nav.classList.add('is-solid'); },
      onLeaveBack: function () { nav.classList.remove('is-solid'); }
    });
    gsap.to('.progress span', { scaleX: 1, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: 0.3 } });
  }

  /* ======================================================================
     Auftakt beim Laden
     ====================================================================== */

  function intro(S) {
    var loader = $('[data-loader]');
    var w = $$('.hero__word');
    var meta = $$('.hero__meta, .hero__rating, .hero__cue, .nav');
    var seal = $('[data-seal]');
    var tl = gsap.timeline({ defaults: { ease: 'expo.out' } });
    var startF = Math.round(S.seq.n * 0.84);
    var p = { f: startF };
    if (lenis) lenis.stop();
    gsap.set(S.final, { opacity: 0 });
    gsap.set(S.canvas, { opacity: 1 });
    S.seq.draw(startF);
    var lay = S.list.map(function (l) { return l.el; });
    tl.to('.loader__mark, .loader__count', { y: -30, autoAlpha: 0, duration: .5, ease: 'power2.in', stagger: .05 }, 0)
      .to(loader, { yPercent: -100, duration: 1.0, ease: 'expo.inOut' }, .25)
      .set(loader, { display: 'none' })
      .from(S.el, { y: function () { return window.innerHeight * 0.32; }, scale: 0.88, duration: 1.6 }, .55)
      .to(p, { f: S.seq.n, duration: 1.7, ease: 'power3.out', onUpdate: function () { S.seq.draw(p.f); } }, .55)
      .from(w, { yPercent: 110, autoAlpha: 0, duration: 1.4, stagger: .12 }, .7)
      .fromTo(lay, { y: function (i) { return -S.H() * (0.42 + 0.06 * (i % 3)); }, rotation: function (i) { return i % 2 ? 40 : -40; }, opacity: 0 },
        { y: 0, rotation: 0, opacity: 1, duration: 1.0, stagger: .07, ease: 'back.out(1.5)' }, 1.35)
      .to(S.final, { opacity: 1, duration: .3, ease: 'none' }, 2.45)
      .set(lay.concat([S.canvas]), { opacity: 0 }, 2.76)
      .from(meta, { y: 24, autoAlpha: 0, duration: 1, stagger: .08 }, 1.5)
      .from(seal, { scale: 0.6, rotation: -120, autoAlpha: 0, duration: 1.6 }, 1.6)
      .add(function () {
        (built && built.ready ? built.ready : Promise.resolve()).then(function () {
          if (lenis) lenis.start();
          root.classList.add('is-loaded');
        });
      }, 2.8);
    return tl;
  }

  /* ======================================================================
     Start
     ====================================================================== */

  var built = null;
  var cleanups = [];

  function tick() { return new Promise(function (r) { setTimeout(r, 0); }); }

  /* Szenen nacheinander in eigenen kleinen Aufgaben aufbauen (blockiert den Hauptthread nicht am Stück) */
  function build() {
    var mob = isMobile();
    var stages = {};
    ['classic', 'tropical', 'peanut', 'berry', 'matcha'].forEach(function (id) { stages[id] = buildStage(id); });
    var ctx = gsap.context(function () {
      if (stages.classic && stages.classic.seq) opener(stages.classic, mob);
    });
    var resize = function () { Object.keys(stages).forEach(function (k) { var s = stages[k]; if (s && s.seq) s.seq.resize(); }); };
    ScrollTrigger.addEventListener('refresh', resize);
    resize();
    built = { ctx: ctx, stages: stages, mob: mob, resize: resize };
    var steps = [
      function () { if (stages.tropical && stages.tropical.seq) tropical(stages.tropical, mob); },
      function () { if (stages.peanut && stages.peanut.seq) peanut(stages.peanut, mob); },
      function () { if (stages.berry && stages.berry.base) berry(stages.berry, mob); },
      function () { if (stages.matcha && stages.matcha.seq) matcha(stages.matcha, mob); },
      quiet, quietGallery, quietMenu
    ];
    built.ready = steps.reduce(function (p, fn) {
      return p.then(tick).then(function () { ctx.add(fn); });
    }, Promise.resolve()).then(function () {
      ScrollTrigger.refresh();
      resize();
    });
    if (started) preloadAll(stages);
    return built;
  }

  /* Bilder der späteren Szenen im Hintergrund nachladen, in Scroll-Reihenfolge */
  var started = false;
  function preloadAll(stages) {
    started = true;
    var prio = 3;
    ['classic', 'tropical', 'peanut', 'berry', 'matcha'].forEach(function (id) {
      var s = stages[id];
      if (!s) return;
      if (s.seq) s.seq.preload(prio++);
      s.list.forEach(function (l) { loadImg(l.L.src, prio); });
      if (s.m.final) loadImg(isMobile() ? s.m.finalM : s.m.final, prio);
    });
  }

  function rebuild() {
    if (!built) return;
    ScrollTrigger.removeEventListener('refresh', built.resize);
    cleanups.splice(0).forEach(function (f) { f(); });
    built.ctx.revert();
    teardownStages();
    build();
    ScrollTrigger.refresh();
  }

  function start() {
    setupScroll();
    var b = build();
    var S = b.stages.classic;
    // kritische Bilder für den Auftakt
    var crit = [];
    if (S) {
      crit.push(loadImg(isMobile() ? S.m.finalM : S.m.final, 0));
      S.list.forEach(function (l) { crit.push(loadImg(l.L.src, 0)); });
      if (S.seq) { crit.push(S.seq.preload(0, 0, 0)); S.seq.preload(1, Math.round(S.seq.n * 0.84), S.seq.n - 1); }
    }
    var countEl = $('[data-loader-count]');
    var total = crit.length || 1, done = 0;
    crit.forEach(function (p) { p.then(function () { done++; if (countEl) countEl.textContent = Math.round(done / total * 100); }); });
    var go = function () {
      if (countEl) countEl.textContent = '100';
      if (S && S.seq) intro(S); else { $('[data-loader]').style.display = 'none'; root.classList.add('is-loaded'); }
    };
    var timeout = new Promise(function (res) { setTimeout(res, 4500); });
    Promise.race([Promise.all(crit), timeout]).then(function () {
      setTimeout(go, 120);
      preloadAll(b.stages);
    });

    var lastW = window.innerWidth;
    var t;
    window.addEventListener('resize', function () {
      clearTimeout(t);
      t = setTimeout(function () {
        var w = window.innerWidth;
        if (Math.abs(w - lastW) > 80 || (w < 768) !== (lastW < 768)) { lastW = w; rebuild(); }
      }, 350);
    });
  }

  function ready() {
    var c = new Promise(function (res) {
      if (root.classList.contains('content-ready')) res(); else document.addEventListener('karma:content', res, { once: true });
    });
    var m = fetch('assets/render/manifest.json').then(function (r) { return r.json(); }).then(function (j) { manifest = j; });
    var f = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
    Promise.all([c, m, f]).then(function () {
      if (!window.gsap || !window.ScrollTrigger || !window.SplitText) throw new Error('GSAP fehlt');
      start();
    }).catch(function (e) {
      console.warn('Animationen deaktiviert:', e);
      root.classList.remove('motion-ok');
      var l = $('[data-loader]');
      if (l) l.style.display = 'none';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready); else ready();
})();
