(function () {
  var KEY = 'gga-earned';
  var TOTAL = 7;

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; }
  }
  function save(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) { /* storage blocked: still works for this visit */ }
  }

  var earned = load();
  var cards = document.querySelectorAll('.card[data-id]');

  function render() {
    cards.forEach(function (card) {
      var id = card.getAttribute('data-id');
      var on = earned.indexOf(id) !== -1;
      card.classList.toggle('is-earned', on);
      var btn = card.querySelector('.earn');
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.querySelector('.earn-label').textContent = on ? 'Earned' : 'Mark as earned';
      var shelfItem = document.querySelector('.shelf a[href="#' + id + '"]');
      if (shelfItem) shelfItem.parentElement.classList.toggle('is-earned', on);
    });
    var n = earned.length;
    document.querySelectorAll('[data-earned-count]').forEach(function (el) { el.textContent = n; });
    var bar = document.querySelector('[data-earned-bar]');
    if (bar) {
      bar.style.width = (n / TOTAL * 100) + '%';
      bar.parentElement.setAttribute('aria-valuenow', n);
    }
  }

  cards.forEach(function (card) {
    card.querySelector('.earn').addEventListener('click', function () {
      var id = card.getAttribute('data-id');
      var i = earned.indexOf(id);
      if (i === -1) earned.push(id); else earned.splice(i, 1);
      save(earned);
      render();
    });
  });

  // Open a guide when arriving via its link (e.g. #yolo).
  function openFromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var card = document.getElementById(id);
    if (card && card.classList.contains('card')) {
      var d = card.querySelector('details');
      if (d) d.open = true;
    }
  }
  window.addEventListener('hashchange', openFromHash);

  // Keep only ids that still exist (in case cards are renamed later).
  var valid = Array.prototype.map.call(cards, function (c) { return c.getAttribute('data-id'); });
  earned = earned.filter(function (id) { return valid.indexOf(id) !== -1; });

  render();
  openFromHash();
})();
