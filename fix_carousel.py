#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復所有輪播 JS 語法錯誤
- 用 carouselImgError(el) 外部函數取代 inline onerror
- 修復 index.html + 所有 product/*.html
"""
import sys, re
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(r"C:\Users\user\Desktop\mengtakhong-website")

# ── 新的乾淨 inline script（無任何引號衝突）──
CLEAN_CAROUSEL_SCRIPT = '''<script>
/* ── Carousel helpers ── */
function carouselImgError(el) {
  var p = el.parentElement;
  p.innerHTML = '<div style="font-size:2.4rem;display:flex;align-items:center;justify-content:center;height:100%;background:#f5f0e8;">&#127870;</div>';
}

var _carouselState = {};
var _carouselItems = {};

function carouselCard(p, prefix) {
  prefix = prefix || '';
  var badge = (p.source === '代理正貨')
    ? '<span style="font-size:.6rem;color:#D4AF37;border:1px solid rgba(212,175,55,.3);padding:1px 6px;border-radius:20px;margin-bottom:4px;display:inline-block;">代理正貨</span><br>'
    : '';
  var imgSrc = prefix + 'assets/images/products/' + p.slug + '.jpg';
  var html = '<a href="' + prefix + 'product/' + p.slug + '.html" class="carousel-card">';
  html += '<div class="carousel-card-img">';
  html += '<img src="' + imgSrc + '" alt="" loading="lazy" onerror="carouselImgError(this)">';
  html += '</div>';
  html += '<div class="carousel-card-body">' + badge;
  html += '<div class="carousel-card-zh">' + (p.zh || '') + '</div>';
  html += '<div class="carousel-card-en">' + (p.en || '') + '</div>';
  html += '<div class="carousel-card-spec">' + (p.spec || '') + '</div>';
  html += '</div></a>';
  return html;
}

function carouselInit(cat, count, prefix, trackId, excludeSlug) {
  if (!window.MTH_PRODUCTS || !MTH_PRODUCTS[cat]) return;
  var data = MTH_PRODUCTS[cat].slice();
  if (excludeSlug) data = data.filter(function(p) { return p.slug !== excludeSlug; });
  data.sort(function() { return Math.random() - 0.5; });
  var items = data.slice(0, count);
  var tid = trackId || ('track-' + cat);
  var track = document.getElementById(tid);
  if (!track) return;
  track.innerHTML = items.map(function(p) { return carouselCard(p, prefix); }).join('');
  _carouselItems[cat] = items.length;
  _carouselState[cat] = 0;
}

function carouselMove(cat, dir) {
  var track = document.getElementById('track-' + cat);
  if (!track) return;
  var outer = track.parentElement;
  var cardEl = track.querySelector('.carousel-card');
  var cardW = cardEl ? (cardEl.offsetWidth + 18) : (outer.offsetWidth / 5 + 18);
  var total = _carouselItems[cat] || 15;
  var maxOffset = Math.max(0, total - 5);
  _carouselState[cat] = Math.max(0, Math.min(maxOffset, (_carouselState[cat] || 0) + dir));
  track.style.transform = 'translateX(-' + (_carouselState[cat] * cardW) + 'px)';
}

function ymalMove(dir) {
  var track = document.getElementById('ymal-track');
  if (!track) return;
  var outer = track.parentElement;
  var cardEl = track.querySelector('.carousel-card');
  var cardW = cardEl ? (cardEl.offsetWidth + 18) : (outer.offsetWidth / 5 + 18);
  var total = _carouselItems['__ymal__'] || 10;
  var maxOffset = Math.max(0, total - 5);
  _carouselState['__ymal__'] = Math.max(0, Math.min(maxOffset, (_carouselState['__ymal__'] || 0) + dir));
  track.style.transform = 'translateX(-' + (_carouselState['__ymal__'] * cardW) + 'px)';
}

document.addEventListener('DOMContentLoaded', function() {
  /* Homepage carousels */
  var homeCats = ["whisky", "korea", "japan", "wine", "spirits", "chinese"];
  homeCats.forEach(function(cat) {
    if (document.getElementById('track-' + cat)) {
      carouselInit(cat, 15, '', 'track-' + cat, null);
    }
  });

  /* You May Also Like (product pages) */
  var ymalSection = document.getElementById('ymal-section');
  if (ymalSection) {
    var cat = ymalSection.getAttribute('data-cat');
    var current = ymalSection.getAttribute('data-current');
    if (cat && window.MTH_PRODUCTS && MTH_PRODUCTS[cat]) {
      carouselInit('__ymal__', 10, '../', 'ymal-track', current);
      _carouselItems['__ymal__'] = Math.min(10, MTH_PRODUCTS[cat].length);
    }
  }
});
</script>'''

# ── OLD script pattern to replace ──
OLD_SCRIPT_PAT = re.compile(
    r'<script>\s*var _carouselState.*?</script>',
    re.DOTALL
)

# ── Fix index.html ──
idx_path = BASE / "index.html"
html = idx_path.read_text(encoding="utf-8")

# Remove duplicate main.js if still there
count_mainjs = html.count('<script src="assets/js/main.js"></script>')
if count_mainjs > 1:
    # keep only the last occurrence - remove all then add one
    html = html.replace('<script src="assets/js/main.js"></script>', '')
    # re-add before products-data or before inline script
    html = html.replace(
        '<script src="assets/js/products-data.js"></script>',
        '<script src="assets/js/products-data.js"></script>\n<script src="assets/js/main.js"></script>'
    )
    print(f"Removed {count_mainjs-1} duplicate main.js references")

# Replace old inline carousel script
if OLD_SCRIPT_PAT.search(html):
    html = OLD_SCRIPT_PAT.sub(CLEAN_CAROUSEL_SCRIPT, html)
    print("index.html: replaced carousel script")
else:
    # Append before </body>
    html = html.replace('</body>', CLEAN_CAROUSEL_SCRIPT + '\n</body>')
    print("index.html: appended carousel script before </body>")

idx_path.write_text(html, encoding="utf-8")

# ── Fix all product pages ──
prod_files = list((BASE / "product").glob("*.html"))
fixed = 0
for fp in prod_files:
    try:
        h = fp.read_text(encoding="utf-8")
        if OLD_SCRIPT_PAT.search(h):
            h = OLD_SCRIPT_PAT.sub(CLEAN_CAROUSEL_SCRIPT, h)
            # Also fix script includes: ensure products-data.js before main.js, no duplicates
            h = h.replace('<script src="../assets/js/main.js"></script>\n<script src="../assets/js/products-data.js"></script>\n<script src="../assets/js/main.js"></script>',
                          '<script src="../assets/js/products-data.js"></script>\n<script src="../assets/js/main.js"></script>')
            fp.write_text(h, encoding="utf-8")
            fixed += 1
    except Exception as e:
        print(f"  Error {fp.name}: {e}")

print(f"Product pages fixed: {fixed}/{len(prod_files)}")
print("\nDone! Summary:")
print(f"  index.html     — 1")
print(f"  product pages  — {fixed}")
print(f"  Total          — {fixed + 1}")
