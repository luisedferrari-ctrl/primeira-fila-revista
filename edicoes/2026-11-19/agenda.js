/* ENTRESSALA — filtros da agenda, sem serviços externos. */
(function () {
  'use strict';
  var input = document.getElementById('agenda-search');
  var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-filter-city]'));
  var rows = Array.prototype.slice.call(document.querySelectorAll('.agenda-entry'));
  var months = Array.prototype.slice.call(document.querySelectorAll('.agenda-month'));
  var status = document.getElementById('agenda-status');
  var empty = document.getElementById('agenda-empty');
  if (!rows.length) return;
  var city = '*';
  function normal(s) {
    return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  }
  function apply() {
    var term = normal(input && input.value);
    var count = 0;
    rows.forEach(function (row) {
      var matchesCity = city === '*' || normal(row.getAttribute('data-city')) === normal(city);
      var matchesTerm = !term || normal(row.getAttribute('data-terms') || row.textContent).indexOf(term) >= 0;
      row.hidden = !(matchesCity && matchesTerm);
      if (!row.hidden) count += 1;
    });
    months.forEach(function (month) {
      month.hidden = !month.querySelector('.agenda-entry:not([hidden])');
    });
    if (status) status.textContent = count + ' programa' + (count === 1 ? '' : 's') + ' encontrado' + (count === 1 ? '' : 's') + '.';
    if (empty) empty.hidden = count > 0;
  }
  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      city = button.getAttribute('data-filter-city');
      buttons.forEach(function (b) {
        var active = b === button;
        b.setAttribute('aria-pressed', String(active));
        b.classList.toggle('is-active', active);
      });
      apply();
    });
  });
  if (input) input.addEventListener('input', apply);
  apply();
})();
