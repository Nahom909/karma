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
     Bühne aufbauen: Ebenen aus manifest.json (Fotos: freigestellte Becherteile; Matcha: 3D-Bildfolge)
     ====================================================================== */

  var FRUIT = {};

  function buildStage(id) {
    var stage = $('[data-stage="' + id + '"]');
    var m = manifest[id];
    if (!stage || !m) return null;
    var mob = isMobile();
    var S = { id: id, el: stage, m: m, final: $('.stage__final', stage), shadow: $('.stage__shadow', stage), layers: {}, list: [], fruits: [] };
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
    if (m.ghost) {
      var g = document.createElement('img');
      g.className = 'stage__ghost';
      g.alt = '';
      g.setAttribute('aria-hidden', 'true');
      g.decoding = 'async';
      g.src = mob ? m.ghostM : m.ghost;
      stage.insertBefore(g, S.final);
      S.ghost = g;
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
        im.src = mob && L.srcM ? L.srcM : L.src;
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
    // Bühnengröße zwischenspeichern: viele Tweens fragen sie ab, jedes Auslesen würde ein Layout erzwingen
    S.W = function () { return S._w || (S._w = stage.offsetWidth); };
    S.H = function () { return S._h || (S._h = stage.offsetHeight); };
    return S;
  }

  /* Echte Fruchtfotos (Open Images, CC BY 2.0) als schwebende Ebenen vor oder hinter dem Becher */
  function fxHost(S, back) {
    var key = back ? 'fxBack' : 'fxFront';
    if (S[key]) return S[key];
    var d = document.createElement('div');
    d.className = 'stage__fx';
    d.setAttribute('aria-hidden', 'true');
    if (back) S.el.insertBefore(d, S.final); else S.el.appendChild(d);
    S[key] = d;
    return d;
  }
  function fruit(S, name, size, back, blur) {
    var f = FRUIT[name];
    if (!f) return null;
    var im = document.createElement('img');
    im.className = 'stage__fruit';
    im.alt = '';
    im.decoding = 'async';
    im.src = f.src;
    im.style.width = (size * 100) + '%';
    if (blur) im.style.filter = 'blur(' + blur + 'px)';
    im.style.opacity = 0;
    fxHost(S, back).appendChild(im);
    S.fruits.push(im);
    return im;
  }
  /* Mittelpunkt einer Frucht auf einen Punkt der Bühne setzen (Anteile 0..1) */
  function placeAt(el, cx, cy) {
    el.style.left = (cx * 100) + '%';
    el.style.top = (cy * 100) + '%';
    gsap.set(el, { xPercent: -50, yPercent: -50 });
  }
  /* Endbild gegen die deckungsgleichen Einzelteile tauschen und zurück */
  function swapIn(tl, S, at) {
    tl.set(S.list.map(function (l) { return l.el; }), { opacity: 1 }, at).set(S.final, { opacity: 0 }, at + 0.02);
  }
  function swapOut(tl, S, at, extra) {
    tl.to(S.final, { opacity: 1, duration: .2 }, at)
      .set(S.list.map(function (l) { return l.el; }).concat(extra || []), { opacity: 0 }, at + 0.22);
  }
  /* kurzes Stauchen beim Aufsetzen */
  function land(tl, el, at, H, depth) {
    tl.to(el, { scaleY: 1 - (depth || 0.05), scaleX: 1 + (depth || 0.05) * 0.4, duration: .14, ease: 'power1.out' }, at)
      .to(el, { y: 0, scaleY: 1, scaleX: 1, duration: .65, ease: 'back.out(2.6)' }, at + .14);
  }

  function teardownStages() {
    $$('.stage__seq, .stage__base, .stage__layers, .stage__fx, .stage__ghost').forEach(function (n) { n.remove(); });
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
     1 · Opener: Hero -> Classic (derselbe Becher, echtes Foto)
     Das Topping hebt ab wie in einer Explosionszeichnung, echte Früchte kreisen um den Becher.
     ====================================================================== */

  /* Früchte auf dem Höhepunkt: Name, Ziel x/y (Anteil der Bühne), Größe (Anteil der Bühnenbreite), Drehung, Unschärfe, hinter dem Becher */
  var CLASSIC_FLY = [
    ['strawberry_1', 1.07, 0.30, 0.30, 16, 0, false],
    ['blueberry_1', 0.03, 0.17, 0.12, 0, 0, false],
    ['raspberry_1', 0.22, 0.04, 0.15, -20, 0, true],
    ['strawberry_2', -0.10, 0.53, 0.25, -26, 0, true],
    ['blueberry_2', 0.95, 0.73, 0.11, 0, 0, true],
    ['raspberry_2', 0.86, 0.08, 0.12, 24, 0, false],
    ['blueberry_3', 1.24, 0.60, 0.10, 0, 2, false],
    ['strawberry_1', -0.32, 0.88, 0.46, -40, 9, false],
    ['blueberry_1', 1.32, 1.0, 0.22, 0, 7, false]
  ];
  var CLASSIC_FLY_M = [
    ['strawberry_1', 0.93, 0.15, 0.24, 16, 0, false],
    ['blueberry_1', 0.07, 0.12, 0.11, 0, 0, false],
    ['raspberry_1', 0.32, 0.02, 0.13, -20, 0, true],
    ['strawberry_2', 0.02, 0.52, 0.2, -26, 0, true],
    ['blueberry_2', 0.97, 0.66, 0.1, 0, 0, true],
    ['raspberry_2', 0.72, 0.03, 0.11, 24, 0, false],
    ['strawberry_1', -0.12, 0.94, 0.34, -40, 6, false]
  ];

  function rimCenter(S, dy) {
    var r = S.m.rim || [0.2, 0.8, 0.35];
    return [(r[0] + r[1]) / 2, r[2] + (dy || 0)];
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
    var top = S.layers.top, body = S.layers.body;
    var o = rimCenter(S, -0.05);

    gsap.set(copy, { autoAlpha: 0 });
    gsap.set([top, body], { transformOrigin: '50% 100%' });

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
      }, 0);
    swapIn(tl, S, .98);

    // Topping hebt ab, der Becher neigt sich leicht dagegen
    tl.to(top, { y: function () { return -H() * (mob ? .12 : .17); }, rotation: -5, duration: 2.0, ease: 'power2.inOut' }, 1.0)
      .to(body, { rotation: 2.2, duration: 2.0, ease: 'sine.inOut' }, 1.0)
      .to(top, { y: function () { return -H() * (mob ? .135 : .19); }, rotation: -2, duration: 2.5, ease: 'sine.inOut' }, 3.0)
      .to(body, { rotation: -1.2, duration: 2.5, ease: 'sine.inOut' }, 3.0);

    // Früchte steigen aus dem Becher auf, schweben in Tiefenebenen und fliegen aus dem Bild
    (mob ? CLASSIC_FLY_M : CLASSIC_FLY).forEach(function (d, k) {
      var el = fruit(S, d[0], d[3], d[6], d[5]);
      if (!el) return;
      placeAt(el, o[0], o[1]);
      var dx = function () { return (d[1] - o[0]) * W(); };
      var dy = function () { return (d[2] - o[1]) * H(); };
      var side = d[1] < 0.5 ? -1 : 1;
      tl.fromTo(el, { x: 0, y: 0, scale: .2, rotation: d[4] - 70, opacity: 0 },
        { x: dx, y: dy, scale: 1, rotation: d[4], opacity: 1, duration: 2.1, ease: 'power3.out' }, 1.05 + k * .06)
        .to(el, { y: function () { return dy() - (0.03 + 0.02 * (k % 3)) * H(); }, rotation: d[4] + (k % 2 ? 14 : -14), duration: 2.4, ease: 'sine.inOut' }, 3.2 + k * .03)
        .to(el, {
          // obere Früchte fliegen nach oben hinaus, untere nach unten (nicht quer über den Text)
          x: function () { return dx() * 1.4 + side * 1.1 * W(); }, y: function () { return dy() + (d[2] > 0.6 ? 0.7 : -(0.55 + 0.1 * (k % 3))) * H(); },
          rotation: d[4] + side * 80, duration: 1.6, ease: 'power2.in'
        }, 5.4 + k * .05)
        .set(el, { opacity: 0 }, 7.1);
    });

    revealCopy(tl, copy, 2.0, 2.6);

    // Topping landet wieder auf dem Becher
    tl.to(top, { y: function () { return H() * .006; }, rotation: 0, duration: 1.0, ease: 'power3.in' }, 5.7)
      .to(body, { rotation: 0, duration: 1.1, ease: 'sine.inOut' }, 5.6);
    land(tl, top, 6.7, H, .045);
    swapOut(tl, S, 7.7);
    tl.to({}, { duration: 1.4 }, 7.95);

    anchors.sorten = function () { return tl.scrollTrigger.start + (tl.scrollTrigger.end - tl.scrollTrigger.start) * 0.46; };
    return tl;
  }

  /* ======================================================================
     2 · Caramel Crunch: der Becher füllt sich von unten mit Farbe, dann landet die Haube
     ====================================================================== */

  function caramel(S, mob) {
    var sec = $('[data-scene="caramel"]');
    var copy = $('[data-copy="caramel"]');
    var big = $('[data-bigtype]', sec);
    var tl = pinTl(sec, function () { return mob ? 3.6 : 4.4; });
    var H = S.H;
    var body = S.layers.body, top = S.layers.top;
    var L = S.list.filter(function (l) { return l.name === 'body'; })[0].L;
    tintIn('caramel', sec);

    // Füll-Fenster: Rahmen fährt nach oben, der Inhalt läuft gegenläufig mit und bleibt so an seinem Platz.
    // Der Rahmen ist oben um 12 % höher, damit die weiche Kante am Ende über dem Becherrand liegt.
    var extra = 0.12;
    var fill = document.createElement('div');
    fill.className = 'stage__fill';
    fill.style.left = (L.x * 100) + '%';
    fill.style.top = ((L.y - L.h * extra) * 100) + '%';
    fill.style.width = (L.w * 100) + '%';
    fill.style.height = (L.h * (1 + extra) * 100) + '%';
    var inner = document.createElement('div');
    inner.className = 'stage__fill-in';
    body.parentNode.insertBefore(fill, body);
    fill.appendChild(inner);
    inner.appendChild(body);
    body.style.left = '0';
    body.style.top = (extra / (1 + extra) * 100) + '%';
    body.style.width = '100%';

    gsap.set(S.final, { opacity: 0 });
    gsap.set([S.ghost, body], { opacity: 1 });
    gsap.set(top, { transformOrigin: '50% 100%' });
    gsap.set(copy, { autoAlpha: 0 });

    tl.fromTo(fill, { yPercent: 100 }, { yPercent: 0, duration: 5.2, ease: 'power1.inOut' }, 0)
      .fromTo(inner, { yPercent: -100 }, { yPercent: 0, duration: 5.2, ease: 'power1.inOut' }, 0)
      .fromTo(big, { xPercent: 0 }, { xPercent: -38, duration: 10 }, 0)
      .fromTo(top, { y: function () { return -H() * (mob ? .32 : .42); }, rotation: -7 },
        { y: function () { return H() * .008; }, rotation: 0, duration: 1.2, ease: 'power3.in' }, 4.5)
      .fromTo(top, { opacity: 0 }, { opacity: 1, duration: .3 }, 4.5)
      .to(S.ghost, { opacity: 0, duration: 1.0 }, 5.6);
    land(tl, top, 5.7, H, .06);
    revealCopy(tl, copy, 0.6, 2.6);
    swapOut(tl, S, 7.6, [S.ghost]);
    tl.to({}, { duration: 1.6 }, 7.9);
    return tl;
  }

  /* ======================================================================
     3 · Peanut Power: der Becher setzt sich Schicht für Schicht zusammen, dann kippt er sanft
     ====================================================================== */

  function peanut(S, mob) {
    var sec = $('[data-scene="peanut"]');
    var copy = $('[data-copy="peanut"]');
    var a = $('[data-bigtype-a]', sec), b = $('[data-bigtype-b]', sec);
    var tl = pinTl(sec, function () { return mob ? 3.2 : 3.8; });
    var W = S.W, H = S.H, k = mob ? .55 : 1;
    tintIn('peanut', sec);
    var bands = ['band_3', 'band_2', 'band_1'].map(function (n) { return S.layers[n]; }).filter(Boolean);
    var top = S.layers.top;
    gsap.set(S.final, { opacity: 0 });
    gsap.set(bands.concat([top]), { opacity: 1 });
    gsap.set(copy, { autoAlpha: 1 });

    // Schichten gleiten abwechselnd von links und rechts herein: Açaí, Chiapudding, Erdnussbutter
    var dirs = [-1, 1, -1];
    bands.forEach(function (el, i) {
      tl.fromTo(el, { x: function () { return dirs[i] * W() * .85 * k; }, rotation: dirs[i] * 7 },
        { x: 0, rotation: 0, duration: 1.8, ease: 'power3.out' }, 0.1 + i * .75);
    });
    gsap.set(top, { transformOrigin: '50% 100%' });
    tl.fromTo(top, { y: function () { return -H() * .5 * (mob ? .7 : 1); }, rotation: 8 },
      { y: function () { return H() * .006; }, rotation: 0, duration: 1.1, ease: 'power3.in' }, 2.5)
      .fromTo(top, { opacity: 0 }, { opacity: 1, duration: .3 }, 2.5);
    land(tl, top, 3.6, H, .05);

    gsap.set(S.el, { transformOrigin: '50% 92%' });
    tl.to(S.el, { rotation: -3.5, duration: 1.4, ease: 'sine.inOut' }, 4.4)
      .to(S.el, { rotation: 2.4, duration: 1.6, ease: 'sine.inOut' }, 5.8)
      .to(S.el, { rotation: 0, duration: 1.2, ease: 'sine.inOut' }, 7.4)
      .fromTo(a, { xPercent: 4 }, { xPercent: -30, duration: 10 }, 0)
      .fromTo(b, { xPercent: -34 }, { xPercent: 2, duration: 10 }, 0);
    var colA = $('.copy__col--a', copy), colB = $('.copy__col--b', copy);
    gsap.set([colA, colB], { autoAlpha: 0 });
    revealCopy(tl, colA, 0.7, 2.4);
    revealCopy(tl, colB, 3.2, 2.4);
    swapOut(tl, S, 8.4);
    tl.to({}, { duration: 1.4 }, 8.7);
    return tl;
  }

  /* ======================================================================
     4 · Berry Blast: echte Beeren explodieren als Kranz um den Becher und kehren zurück
     ====================================================================== */

  var BERRY_POOL = ['strawberry_1', 'blueberry_1', 'raspberry_1', 'blueberry_2', 'strawberry_2', 'raspberry_2', 'blueberry_3'];
  var BERRY_SIZE = { strawberry_1: .2, strawberry_2: .19, raspberry_1: .12, raspberry_2: .11, blueberry_1: .095, blueberry_2: .09, blueberry_3: .085 };

  function berry(S, mob) {
    var sec = $('[data-scene="berry"]');
    var copy = $('[data-copy="berry"]');
    var tl = pinTl(sec, function () { return mob ? 3.4 : 4.2; });
    var W = S.W, H = S.H;
    var k = mob ? 0.8 : 1;
    var top = S.layers.top;
    tintIn('berry', sec);
    gsap.set(copy, { autoAlpha: 0 });
    gsap.set(top, { transformOrigin: '50% 100%' });
    var o = rimCenter(S, -0.07);
    var rnd = (function () { var s = 7; return function () { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; })();

    swapIn(tl, S, .98);
    // Das Topping springt kurz hoch, wenn die Beeren herausschießen
    tl.to(top, { y: function () { return -H() * .04; }, rotation: 3, duration: 1.0, ease: 'power3.out' }, 1.0)
      .to(top, { y: function () { return -H() * .05; }, rotation: -2, duration: 3.6, ease: 'sine.inOut' }, 2.0)
      .to(top, { y: function () { return H() * .005; }, rotation: 0, duration: 1.0, ease: 'power3.in' }, 6.3);
    land(tl, top, 7.3, H, .05);

    var n = mob ? 11 : 18;
    for (var i = 0; i < n; i++) {
      var name = BERRY_POOL[i % BERRY_POOL.length];
      var blur = i % 6 === 5 ? 4 + (i % 3) * 2 : 0;
      var size = BERRY_SIZE[name] * (0.8 + rnd() * 0.6) * (blur ? 1.6 : 1);
      var el = fruit(S, name, size, i % 3 === 1, blur);
      if (!el) continue;
      placeAt(el, o[0], o[1]);
      (function (el, i, blur) {
        var ang = (i / n) * Math.PI * 2 - Math.PI / 2 + (rnd() - 0.5) * 0.5;
        var rx = 0.6 + rnd() * 0.32, ry = 0.36 + rnd() * 0.17;
        if (blur) { rx *= 1.3; ry *= 1.25; }        // unscharfe Beeren liegen näher an der Kamera, also weiter außen
        if (!mob && Math.cos(ang) > 0) rx *= 0.82;  // rechts steht der Text
        var tx = 0.5 + Math.cos(ang) * rx, ty = 0.5 + Math.sin(ang) * ry;
        var dx = function () { return (tx - o[0]) * W() * k; }, dy = function () { return (ty - o[1]) * H() * k; };
        var rot = (rnd() - 0.5) * 420;
        tl.fromTo(el, { x: 0, y: 0, scale: .2, rotation: 0, opacity: 0 },
          { x: dx, y: dy, scale: 1, rotation: rot, opacity: 1, duration: 2.2, ease: 'expo.out' }, 1.0 + rnd() * .15)
          .to(el, { x: function () { return dx() + Math.cos(ang) * .05 * W() * k; }, y: function () { return dy() + (Math.sin(ang) * .04 - .02) * H() * k; }, rotation: rot * 1.2, duration: 2.2, ease: 'sine.inOut' }, 3.2)
          .to(el, { x: 0, y: 0, scale: .22, rotation: 0, duration: 1.9, ease: 'power3.in' }, 5.4 + rnd() * .3)
          .to(el, { opacity: 0, duration: .25 }, 7.2);
      })(el, i, blur);
    }

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
    swapOut(tl, S, 7.95);
    tl.to({}, { duration: 1.8 }, 8.2);
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
    var top = S.layers.top, body = S.layers.body;
    if (lenis) lenis.stop();
    // Der Becher steigt auf, das Topping fällt obendrauf und setzt federnd auf
    gsap.set(S.final, { opacity: 0 });
    gsap.set([top, body], { opacity: 1, transformOrigin: '50% 100%' });
    tl.to('.loader__mark, .loader__count', { y: -30, autoAlpha: 0, duration: .5, ease: 'power2.in', stagger: .05 }, 0)
      .to(loader, { yPercent: -100, duration: 1.0, ease: 'expo.inOut' }, .25)
      .set(loader, { display: 'none' })
      .from(S.el, { y: function () { return window.innerHeight * 0.32; }, scale: 0.88, duration: 1.6 }, .55)
      .from(w, { yPercent: 110, autoAlpha: 0, duration: 1.4, stagger: .12 }, .7)
      .fromTo(top, { y: function () { return -S.H() * 0.5; }, rotation: -9 }, { y: 0, rotation: 0, duration: .8, ease: 'power3.in' }, 1.25)
      .fromTo(top, { opacity: 0 }, { opacity: 1, duration: .25, ease: 'none' }, 1.25)
      .to(top, { scaleY: .955, scaleX: 1.02, duration: .12, ease: 'power1.out' }, 2.05)
      .to(top, { scaleY: 1, scaleX: 1, duration: .6, ease: 'back.out(3)' }, 2.17)
      .to(S.final, { opacity: 1, duration: .3, ease: 'none' }, 2.8)
      .set([top, body], { opacity: 0 }, 3.1)
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
    ['classic', 'caramel', 'peanut', 'berry', 'matcha'].forEach(function (id) { stages[id] = buildStage(id); });
    var ctx = gsap.context(function () {
      if (stages.classic && stages.classic.layers.top) opener(stages.classic, mob);
    });
    var resize = function () { Object.keys(stages).forEach(function (k) { var s = stages[k]; if (s && s.seq) s.seq.resize(); }); };
    var forget = function () { Object.keys(stages).forEach(function (k) { var s = stages[k]; if (s) s._w = s._h = 0; }); };
    ScrollTrigger.addEventListener('refresh', resize);
    ScrollTrigger.addEventListener('refreshInit', forget);
    cleanups.push(function () { ScrollTrigger.removeEventListener('refreshInit', forget); });
    resize();
    built = { ctx: ctx, stages: stages, mob: mob, resize: resize };
    var steps = [
      function () { if (stages.caramel && stages.caramel.layers.body) caramel(stages.caramel, mob); },
      function () { if (stages.peanut && stages.peanut.layers.top) peanut(stages.peanut, mob); },
      function () { if (stages.berry && stages.berry.layers.top) berry(stages.berry, mob); },
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
    ['classic', 'caramel', 'peanut', 'berry', 'matcha'].forEach(function (id) {
      var s = stages[id];
      if (!s) return;
      if (s.seq) s.seq.preload(prio);
      if (s.m.final) loadImg(s.final.currentSrc || (isMobile() ? s.m.finalM : s.m.final), prio);
      s.list.forEach(function (l) { loadImg(l.el.src, prio); });
      if (s.ghost) loadImg(s.ghost.src, prio);
      s.fruits.forEach(function (f) { loadImg(f.src, prio); });
      prio++;
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
      crit.push(loadImg(S.final.currentSrc || (isMobile() ? S.m.finalM : S.m.final), 0));
      S.list.forEach(function (l) { crit.push(loadImg(l.el.src, 0)); });
      S.fruits.forEach(function (f) { loadImg(f.src, 1); });
    }
    var countEl = $('[data-loader-count]');
    var total = crit.length || 1, done = 0;
    crit.forEach(function (p) { p.then(function () { done++; if (countEl) countEl.textContent = Math.round(done / total * 100); }); });
    var go = function () {
      if (countEl) countEl.textContent = '100';
      if (S && S.layers.top) intro(S); else { $('[data-loader]').style.display = 'none'; root.classList.add('is-loaded'); }
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
    var m = fetch('assets/render/manifest.json').then(function (r) { return r.json(); }).then(function (j) {
      manifest = j;
      (j.fruit || []).forEach(function (f) { FRUIT[f.name] = f; });
    });
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
