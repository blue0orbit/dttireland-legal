/*
 * Cookie consent for Google Analytics (through Firebase).
 *
 * Analytics is loaded only after the visitor accepts; until then this file makes no network requests
 * and sets no cookies. The choice is kept for 12 months in this browser and can be changed at any
 * time from "Cookie settings" in the footer. Rejecting after accepting turns analytics off and deletes
 * the cookies it set.
 */
(function () {
  'use strict';

  var KEY = 'dtt_analytics_consent';
  var MAX_AGE_MS = 365 * 24 * 60 * 60 * 1000;
  var MEASUREMENT_ID = 'G-3HWHMZQ4HQ';
  var FIREBASE = 'https://www.gstatic.com/firebasejs/12.11.0/';
  var CONFIG = {
    apiKey: 'AIzaSyDhFNrCKwU0vcO5RgtLHlM78j1C1dZXyps',
    authDomain: 'dtt-ireland-web.firebaseapp.com',
    projectId: 'dtt-ireland-web',
    storageBucket: 'dtt-ireland-web.firebasestorage.app',
    messagingSenderId: '997190540940',
    appId: '1:997190540940:web:8ff2d0010e852536f3e5a9',
    measurementId: MEASUREMENT_ID
  };
  // The privacy policy sits next to the site root; this file is in assets/js/.
  var script = document.currentScript;
  var privacyUrl = script ? new URL('../../privacy-policy.html', script.src).href : '/privacy-policy.html';

  var analytics = null; // { module, instance } once loaded
  var loading = false;
  var banner = null;

  function readChoice() {
    try {
      var saved = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (saved && (saved.v === 'granted' || saved.v === 'denied') && Date.now() - saved.t < MAX_AGE_MS) return saved.v;
    } catch (e) { /* storage blocked: ask again next time */ }
    return null;
  }

  function saveChoice(value) {
    try { localStorage.setItem(KEY, JSON.stringify({ v: value, t: Date.now() })); } catch (e) { /* not remembered */ }
  }

  function startAnalytics() {
    window['ga-disable-' + MEASUREMENT_ID] = false;
    if (analytics) { analytics.module.setAnalyticsCollectionEnabled(analytics.instance, true); return; }
    if (loading) return;
    loading = true;
    Promise.all([import(FIREBASE + 'firebase-app.js'), import(FIREBASE + 'firebase-analytics.js')])
      .then(function (m) {
        analytics = { module: m[1], instance: m[1].getAnalytics(m[0].initializeApp(CONFIG)) };
      })
      .catch(function () { /* blocked or offline: nothing is collected */ })
      .then(function () { loading = false; });
  }

  function stopAnalytics() {
    window['ga-disable-' + MEASUREMENT_ID] = true;
    if (analytics) analytics.module.setAnalyticsCollectionEnabled(analytics.instance, false);
    // Delete the Google Analytics cookies, on this host and on the parent domain.
    var host = location.hostname;
    var domains = ['', host, '.' + host.replace(/^www\./, '')];
    document.cookie.split(';').forEach(function (cookie) {
      var name = cookie.split('=')[0].trim();
      if (name === '_ga' || name === '_gid' || name.indexOf('_ga_') === 0) {
        domains.forEach(function (domain) {
          document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + (domain ? '; domain=' + domain : '');
        });
      }
    });
  }

  function choose(value) {
    saveChoice(value);
    if (value === 'granted') startAnalytics(); else stopAnalytics();
    hideBanner();
  }

  function addStyles() {
    if (document.getElementById('dttConsentStyles')) return;
    var style = document.createElement('style');
    style.id = 'dttConsentStyles';
    style.textContent =
      '.dtt-consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:1000;max-width:560px;margin:0 auto;' +
      'background:#fff;color:var(--ink,#17372c);border:1px solid var(--line,#dbe3dc);border-radius:14px;' +
      'box-shadow:0 10px 30px rgba(18,61,47,.18);padding:16px 18px;font-size:15px;line-height:1.5}' +
      '.dtt-consent p{margin:0 0 12px}' +
      '.dtt-consent a{color:var(--forest,#123d2f);text-decoration:underline}' +
      '.dtt-consent__actions{display:flex;gap:10px;flex-wrap:wrap}' +
      '.dtt-consent button{flex:1 1 140px;min-height:44px;border-radius:10px;border:1px solid var(--forest,#123d2f);' +
      'background:var(--forest,#123d2f);color:#fff;font:inherit;font-weight:600;cursor:pointer}' +
      '.dtt-consent button:focus-visible{outline:3px solid var(--accent,#cf7444);outline-offset:2px}';
    document.head.appendChild(style);
  }

  function showBanner() {
    if (banner) { banner.querySelector('button').focus(); return; }
    addStyles();
    banner = document.createElement('div');
    banner.className = 'dtt-consent';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', 'Cookie consent');
    banner.innerHTML =
      '<p>We would like to use Google Analytics cookies to see how this website is used. They are only set ' +
      'if you accept, and you can change your mind at any time with Cookie settings at the bottom of the page. ' +
      '<a href="' + privacyUrl + '">Privacy policy</a></p>' +
      '<div class="dtt-consent__actions">' +
      '<button type="button" data-choice="denied">Reject</button>' +
      '<button type="button" data-choice="granted">Accept</button>' +
      '</div>';
    banner.addEventListener('click', function (event) {
      var button = event.target.closest('button[data-choice]');
      if (button) choose(button.getAttribute('data-choice'));
    });
    document.body.appendChild(banner);
  }

  function hideBanner() {
    if (banner) { banner.remove(); banner = null; }
  }

  function addSettingsLink() {
    var deletion = document.querySelector('.site-footer a[href$="data-deletion.html"]');
    if (!deletion || document.getElementById('dttCookieSettings')) return;
    var link = document.createElement('a');
    link.id = 'dttCookieSettings';
    link.href = '#cookie-settings';
    link.setAttribute('role', 'button');
    link.textContent = 'Cookie settings';
    link.addEventListener('click', function (event) { event.preventDefault(); showBanner(); });
    deletion.insertAdjacentElement('afterend', link);
  }

  function init() {
    addSettingsLink();
    var choice = readChoice();
    if (choice === 'granted') startAnalytics();
    else if (choice === null) showBanner();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
