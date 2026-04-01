/* DTT Ireland — Main JS
   Minimal vanilla JS: nav toggle, scroll effects, FAQ accordion
   No frameworks, no dependencies */

(function () {
  'use strict';

  // ── NAV TOGGLE (mobile) ──────────────────────────────────────
  const navToggle = document.getElementById('navToggle');
  const navLinks  = document.getElementById('navLinks');
  const mainNav   = document.getElementById('mainNav');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      const isOpen = navLinks.classList.toggle('open');
      navToggle.classList.toggle('active', isOpen);
      navToggle.setAttribute('aria-expanded', isOpen);
    });

    // Close nav when a link is clicked
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('open');
        navToggle.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });

    // Close nav on outside click
    document.addEventListener('click', function (e) {
      if (!mainNav.contains(e.target)) {
        navLinks.classList.remove('open');
        navToggle.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // ── NAV SCROLL EFFECT ────────────────────────────────────────
  if (mainNav) {
    var lastScroll = 0;
    window.addEventListener('scroll', function () {
      var y = window.scrollY;
      mainNav.classList.toggle('scrolled', y > 20);
      lastScroll = y;
    }, { passive: true });
  }

  // ── FAQ ACCORDION ────────────────────────────────────────────
  var faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(function (item) {
    var btn = item.querySelector('.faq-question');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var isOpen = item.classList.contains('open');
      // Close all
      faqItems.forEach(function (fi) { fi.classList.remove('open'); });
      // Toggle current
      if (!isOpen) item.classList.add('open');
    });
  });

  // ── SMOOTH SCROLL for anchor links ──────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        var navH = mainNav ? mainNav.offsetHeight : 68;
        var top  = target.getBoundingClientRect().top + window.scrollY - navH - 16;
        window.scrollTo({ top: top, behavior: 'smooth' });
      }
    });
  });

  // ── INTERSECTION OBSERVER (fade-up animation) ───────────────
  if ('IntersectionObserver' in window) {
    var animEls = document.querySelectorAll('.feature-card, .step, .proof-stat, .lang-card');
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    animEls.forEach(function (el, i) {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.45s ease ' + (i * 0.06) + 's, transform 0.45s ease ' + (i * 0.06) + 's';
      obs.observe(el);
    });
  }

})();
