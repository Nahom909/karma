/* Karma: ruhige Bewegung mit GSAP, ScrollTrigger, SplitText und Lenis (alles lokal).
   Hero: Schrift und Becher blenden beim Laden einmal ein (CSS). Highlights, Karte, Galerie: Einblendungen beim Scrollen.
   Bewegt werden nur transform und opacity. Bei "Bewegung reduzieren" läuft nichts davon (siehe index.html). */
(function () {
  'use strict';

  var root = document.documentElement;
  if (!root.classList.contains('motion-ok')) return;

  function $(sel, el) { return (el || document).querySelector(sel); }
  function $$(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }
  function has(t) { return t && (t.length === undefined ? true : t.length > 0); }

  var lenis = null;
  var isMobile = function () { return window.innerWidth < 768; };

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
      if (lenis) lenis.scrollTo(y, { duration: 1.4 }); else window.scrollTo(0, y);
      history.replaceState(null, '', '#' + id);
    });
  }

  function anchorY(id) {
    if (id === 'top') return 0;
    var t = document.getElementById(id);
    if (!t) return null;
    var off = id.indexOf('karte-') === 0 ? 120 : (id === 'acai' || id === 'matcha') ? 0 : 40;
    return t.getBoundingClientRect().top + window.scrollY - off;
  }

  /* ---------- kleine Helfer für Text ---------- */

  function lines(el) {
    if (!el) return [];
    return SplitText.create(el, { type: 'lines', mask: 'lines', linesClass: 'ln', aria: 'none' }).lines;
  }
  function chars(el) {
    if (!el) return [];
    return SplitText.create(el, { type: 'words,chars', charsClass: 'char', mask: 'chars' }).chars;
  }

  /* ======================================================================
     1 · Hero (der Auftakt beim Laden ist reines CSS, siehe style.css)
     ====================================================================== */

  /* Beim Wegscrollen hebt sich der Titel leicht ab, die Becher bleiben ruhig stehen */
  function heroScroll() {
    gsap.to('.hero__title', {
      yPercent: -18, autoAlpha: 0.2, ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
    });
  }

  /* ======================================================================
     2/3 · Highlights: Becher und Text kommen herein, das große Wort gleitet
     ====================================================================== */

  function spots() {
    $$('[data-spot]').forEach(function (sec) {
      var media = $('[data-spot-media]', sec);
      var copy = $('[data-spot-copy]', sec);
      var word = $('[data-spot-word]', sec);
      var fromLeft = sec.classList.contains('spot--acai');

      if (word) gsap.fromTo(word, { xPercent: fromLeft ? -42 : -58 }, {
        xPercent: fromLeft ? -58 : -42, ease: 'none',
        scrollTrigger: { trigger: sec, start: 'top bottom', end: 'bottom top', scrub: true }
      });

      gsap.fromTo(media, { y: 90, autoAlpha: 0, rotation: fromLeft ? -4 : 4 }, {
        y: 0, autoAlpha: 1, rotation: 0, ease: 'power2.out',
        scrollTrigger: { trigger: sec, start: 'top 85%', end: 'top 25%', scrub: 0.6 }
      });
      // leichtes Schweben beim Weiterscrollen
      gsap.fromTo($('.spot__cup', media), { y: 0 }, {
        y: function () { return -window.innerHeight * 0.06; }, ease: 'none',
        scrollTrigger: { trigger: sec, start: 'top top', end: 'bottom top', scrub: true }
      });

      var tl = gsap.timeline({ scrollTrigger: { trigger: copy, start: 'top 82%', end: 'top 34%', scrub: 0.6 } });
      var name = chars($('.spot__name', copy));
      var txt = lines($('.spot__sub', copy)).concat(lines($('.spot__text', copy)));
      tl.from($('.spot__kicker', copy), { y: 18, autoAlpha: 0, duration: 0.3 }, 0);
      if (has(name)) tl.from(name, { yPercent: 110, duration: 0.5, stagger: 0.025, ease: 'power3.out' }, 0.05);
      if (has(txt)) tl.from(txt, { yPercent: 105, duration: 0.45, stagger: 0.06, ease: 'power3.out' }, 0.3);
      tl.from($$('.spot__label, .spot__ingredients li', copy), { y: 16, autoAlpha: 0, duration: 0.3, stagger: 0.035 }, 0.5)
        .from($('.spot__price', copy), { y: 24, autoAlpha: 0, duration: 0.4 }, 0.75);
    });
  }

  /* ======================================================================
     Karte, Galerie, Besuch: ruhige, scroll-gekoppelte Einblendungen
     ====================================================================== */

  function quietText() {
    $$('[data-reveal]:not(.h2)').forEach(function (el) {
      var isText = el.matches('p.lead, p.note');
      gsap.from(isText ? lines(el) : el, {
        yPercent: isText ? 105 : 0, y: isText ? 0 : 36, autoAlpha: isText ? 1 : 0,
        stagger: 0.08, ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 92%', end: 'top 64%', scrub: 0.6 }
      });
    });
    $$('.h2[data-reveal], .visit__title').forEach(function (h) {
      gsap.from(chars(h), { yPercent: 110, stagger: 0.03, ease: 'power3.out', scrollTrigger: { trigger: h, start: 'top 90%', end: 'top 55%', scrub: 0.6 } });
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
  }

  /* Navigation bekommt einen Hintergrund, sobald gescrollt wird; Fortschrittsbalken oben */
  function chrome() {
    var nav = $('[data-nav]');
    ScrollTrigger.create({
      start: 40,
      onEnter: function () { nav.classList.add('is-solid'); },
      onLeaveBack: function () { nav.classList.remove('is-solid'); }
    });
    gsap.to('.progress span', { scaleX: 1, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: 0.3 } });
  }

  /* ======================================================================
     Start
     ====================================================================== */

  function start() {
    setupScroll();
    heroScroll();
    spots();
    quietMenu();
    quietGallery();
    quietText();
    chrome();
    // Spätere Bilder laden lazy nach: danach Positionen neu berechnen
    if (document.readyState === 'complete') ScrollTrigger.refresh();
    else window.addEventListener('load', function () { ScrollTrigger.refresh(); });
  }

  function ready() {
    var c = new Promise(function (res) {
      if (root.classList.contains('content-ready')) res(); else document.addEventListener('karma:content', res, { once: true });
    });
    var f = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
    // Schriften höchstens 1,5 Sekunden abwarten, damit der Hero nicht hängt
    var fonts = Promise.race([f, new Promise(function (r) { setTimeout(r, 1500); })]);
    Promise.all([c, fonts]).then(function () {
      if (!window.gsap || !window.ScrollTrigger || !window.SplitText) throw new Error('GSAP fehlt');
      start();
    }).catch(function (e) {
      console.warn('Animationen deaktiviert:', e);
      root.classList.remove('motion-ok');
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready); else ready();
})();
