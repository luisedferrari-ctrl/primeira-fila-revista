(function () {
  'use strict';
  var input = document.getElementById('agenda-search');
  var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-filter-city]'));
  var rows = Array.prototype.slice.call(document.querySelectorAll('.agenda-item'));
  var months = Array.prototype.slice.call(document.querySelectorAll('.agenda-month'));
  var status = document.getElementById('agenda-status');
  var empty = document.getElementById('agenda-empty');
  if (!input || !status || !rows.length) return;
  var city = '*';
  function normal(s) {
    return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  }
  function apply() {
    var query = normal(input.value);
    var visible = 0;
    rows.forEach(function (row) {
      var matchedCity = city === '*' || normal(row.dataset.city) === normal(city);
      var matchedText = !query || normal(row.dataset.terms).indexOf(query) > -1;
      var show = matchedCity && matchedText;
      row.hidden = !show;
      if (show) visible++;
    });
    months.forEach(function (month) {
      month.hidden = !month.querySelector('.agenda-item:not([hidden])');
    });
    status.textContent = visible + ' programa' + (visible === 1 ? '' : 's') + ' encontrado' + (visible === 1 ? '' : 's') + '.';
    empty.hidden = visible !== 0;
  }
  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      city = button.dataset.filterCity;
      buttons.forEach(function (other) {
        var active = other === button;
        other.setAttribute('aria-pressed', String(active));
        other.classList.toggle('is-active', active);
      });
      apply();
    });
  });
  input.addEventListener('input', apply);
  apply();
})();
