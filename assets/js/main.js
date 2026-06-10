
document.addEventListener('DOMContentLoaded', function() {
  var searchInput = document.getElementById('cat-search');
  if (!searchInput) return;
  var cards = document.querySelectorAll('.prod-card');
  var counter = document.getElementById('search-count');
  var noResults = document.getElementById('no-results');

  function updateCount(n) {
    if (counter) counter.textContent = '顯示 ' + n + ' 個產品';
    if (noResults) noResults.style.display = (n === 0) ? 'block' : 'none';
  }
  updateCount(cards.length);

  searchInput.addEventListener('input', function() {
    var q = this.value.toLowerCase().trim();
    var visible = 0;
    cards.forEach(function(c) {
      var text = c.getAttribute('data-search') || '';
      var show = q === '' || text.includes(q);
      c.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    updateCount(visible);
  });
});

// Global search redirect
var globalSearch = document.getElementById('global-search');
if (globalSearch) {
  globalSearch.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && this.value.trim()) {
      window.location.href = '/search.html?q=' + encodeURIComponent(this.value.trim());
    }
  });
}
