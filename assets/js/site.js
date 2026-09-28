/* Shared site navigation and local service filtering. No network requests. */
(function () {
  'use strict';
  document.documentElement.classList.remove('no-site-js');
  const button = document.getElementById('siteMenuToggle');
  const menu = document.getElementById('siteMenu');
  const header = document.getElementById('siteHeader');
  function closeMenu(restoreFocus) {
    if (!menu || !button) return;
    menu.classList.remove('is-open');
    button.setAttribute('aria-expanded', 'false');
    if (restoreFocus) button.focus();
  }
  if (button && menu) {
    button.addEventListener('click', function () {
      const open = menu.classList.toggle('is-open');
      button.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menu.classList.contains('is-open')) closeMenu(true);
    });
    document.addEventListener('click', function (event) {
      if (header && !header.contains(event.target)) closeMenu(false);
    });
    menu.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMenu(false);
    });
    window.matchMedia('(min-width:1200px)').addEventListener('change', function () { closeMenu(false); });
  }
  const search = document.getElementById('serviceSearch');
  const cards = Array.from(document.querySelectorAll('[data-service]'));
  const filters = Array.from(document.querySelectorAll('[data-filter]'));
  let selected = 'all';
  function updateServices() {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach(function (card) {
      const match = (selected === 'all' || card.dataset.category === selected) && card.textContent.toLocaleLowerCase().includes(query);
      card.hidden = !match;
      if (match) visible++;
    });
    document.getElementById('serviceCount').textContent = 'Showing ' + visible + ' official service' + (visible === 1 ? '' : 's');
    document.getElementById('serviceEmpty').hidden = visible > 0;
    filters.forEach(function (filter) { filter.setAttribute('aria-pressed', String(filter.dataset.filter === selected)); });
  }
  if (search && cards.length) {
    search.addEventListener('input', updateServices);
    filters.forEach(function (filter) { filter.addEventListener('click', function () { selected = filter.dataset.filter; updateServices(); }); });
    document.getElementById('clearServices').addEventListener('click', function () { search.value = ''; selected = 'all'; updateServices(); search.focus(); });
  }
})();
