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

  // The notice speaks the page's language (<html lang>); English is the fallback.
  var COPY = {
    en: { text: 'We would like to use Google Analytics cookies to see how this website is used. They are only set ' +
            'if you accept, and you can change your mind at any time with Cookie settings at the bottom of the page.',
          privacy: 'Privacy policy', reject: 'Reject', accept: 'Accept', settings: 'Cookie settings', region: 'Cookie consent' },
    ga: { text: 'Ba mhaith linn fianáin Google Analytics a úsáid chun a fheiceáil conas a úsáidtear an suíomh gréasáin seo. ' +
            'Ní shocraítear iad ach amháin má ghlacann tú leo, agus is féidir leat d’intinn a athrú am ar bith le Socruithe fianán ' +
            'ag bun an leathanaigh.',
          privacy: 'Polasaí príobháideachais', reject: 'Diúltaigh', accept: 'Glac leis', settings: 'Socruithe fianán',
          region: 'Toiliú le fianáin' },
    pl: { text: 'Chcielibyśmy używać plików cookie Google Analytics, aby sprawdzać, jak korzysta się z tej strony internetowej. ' +
            'Są one zapisywane tylko wtedy, gdy je zaakceptujesz, a zdanie możesz zmienić w dowolnym momencie w Ustawieniach ' +
            'plików cookie na dole strony.',
          privacy: 'Polityka prywatności', reject: 'Odrzuć', accept: 'Akceptuj', settings: 'Ustawienia plików cookie',
          region: 'Zgoda na pliki cookie' },
    pt: { text: 'Gostaríamos de usar cookies do Google Analytics para ver como este site é utilizado. Eles só são definidos ' +
            'se você aceitar, e você pode mudar de ideia a qualquer momento em Configurações de cookies, na parte inferior da página.',
          privacy: 'Política de privacidade', reject: 'Rejeitar', accept: 'Aceitar', settings: 'Configurações de cookies',
          region: 'Consentimento de cookies' },
    ro: { text: 'Am dori să folosim cookie-uri Google Analytics pentru a vedea cum este utilizat acest site. Acestea sunt plasate ' +
            'numai dacă accepți, iar oricând te poți răzgândi din Setări cookie-uri, în partea de jos a paginii.',
          privacy: 'Politica de confidențialitate', reject: 'Respinge', accept: 'Acceptă', settings: 'Setări cookie-uri',
          region: 'Consimțământ pentru cookie-uri' },
    uk: { text: 'Ми хотіли б використовувати файли cookie Google Analytics, щоб бачити, як користуються цим сайтом. ' +
            'Вони встановлюються, лише якщо ви їх приймете, і ви будь-коли можете передумати через «Налаштування файлів cookie» ' +
            'внизу сторінки.',
          privacy: 'Політика конфіденційності', reject: 'Відхилити', accept: 'Прийняти', settings: 'Налаштування файлів cookie',
          region: 'Згода на файли cookie' },
    zh: { text: '我们希望使用 Google Analytics Cookie 来了解本网站的使用情况。只有在您接受的情况下才会设置这些 Cookie，' +
            '而且您可以随时通过页面底部的“Cookie 设置”改变主意。',
          privacy: '隐私政策', reject: '拒绝', accept: '接受', settings: 'Cookie 设置', region: 'Cookie 使用同意' },
    ar: { text: 'نودّ استخدام ملفات تعريف الارتباط الخاصة بـ Google Analytics لمعرفة كيف يُستخدم هذا الموقع. ' +
            'ولا تُوضع هذه الملفات إلا إذا قبلتها، ويمكنك تغيير رأيك في أي وقت من خلال «إعدادات ملفات تعريف الارتباط» في أسفل الصفحة.',
          privacy: 'سياسة الخصوصية', reject: 'رفض', accept: 'قبول', settings: 'إعدادات ملفات تعريف الارتباط',
          region: 'الموافقة على ملفات تعريف الارتباط' },
    ur: { text: 'ہم Google Analytics کی کوکیز استعمال کرنا چاہیں گے تاکہ دیکھ سکیں کہ اس ویب سائٹ کو کس طرح استعمال کیا جاتا ہے۔ ' +
            'یہ کوکیز صرف اسی صورت میں محفوظ کی جاتی ہیں جب آپ انہیں قبول کریں، اور آپ کسی بھی وقت صفحے کے نیچے موجود ' +
            'کوکیز کی ترتیبات کے ذریعے اپنا فیصلہ تبدیل کر سکتے ہیں۔',
          privacy: 'پرائیویسی پالیسی', reject: 'مسترد کریں', accept: 'قبول کریں', settings: 'کوکیز کی ترتیبات',
          region: 'کوکیز کے لیے رضامندی' }
  };
  var lang = (document.documentElement.lang || 'en').toLowerCase().split('-')[0];
  var copy = COPY[lang] || COPY.en;

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
    banner.setAttribute('aria-label', copy.region);
    var paragraph = document.createElement('p');
    paragraph.textContent = copy.text + ' ';
    var policy = document.createElement('a');
    policy.href = privacyUrl;
    policy.textContent = copy.privacy;
    paragraph.appendChild(policy);
    var actions = document.createElement('div');
    actions.className = 'dtt-consent__actions';
    [['denied', copy.reject], ['granted', copy.accept]].forEach(function (choice) {
      var button = document.createElement('button');
      button.type = 'button';
      button.setAttribute('data-choice', choice[0]);
      button.textContent = choice[1];
      actions.appendChild(button);
    });
    banner.appendChild(paragraph);
    banner.appendChild(actions);
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
    link.textContent = copy.settings;
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
