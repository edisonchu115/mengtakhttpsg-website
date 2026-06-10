#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明德行網站大改版 update_website.py
修改一: 首頁6個橫向滑動輪播
修改二: 分類改為高級按鈕
修改三: 產品頁加「你可能喜歡」
修改四: 品牌頁面 brands.html + Logo下載
修改五: 導航欄更新（加品牌）
"""

import sys, os, json, re, shutil, time, urllib.request, urllib.error
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE       = Path(r"C:\Users\user\Desktop\mengtakhong-website")
PROD_DIR   = BASE / "products"
BRANDS_DIR = BASE / "assets" / "images" / "brands"
BRANDS_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES_ORDER = ["whisky","cognac","japan","korea","wine","spirits","chinese","beer"]
CAT_META = {
    "whisky":  {"zh":"威士忌",        "en":"Whisky",                  "emoji":"🥃","bg":"#F5E6C8","tc":"#8B6914"},
    "cognac":  {"zh":"干邑/拔蘭地",   "en":"Cognac & Brandy",         "emoji":"🍷","bg":"#F5D5C8","tc":"#8B2500"},
    "japan":   {"zh":"日本產品",       "en":"Japanese Products",       "emoji":"🗾","bg":"#FDEAEA","tc":"#C0392B"},
    "korea":   {"zh":"韓國/亞洲飲品", "en":"Korean & Asian Beverages","emoji":"🇰🇷","bg":"#D6EAF8","tc":"#1A5276"},
    "wine":    {"zh":"葡萄酒/香檳",   "en":"Wine & Champagne",        "emoji":"🍾","bg":"#F4ECF7","tc":"#6C3483"},
    "spirits": {"zh":"烈酒/力嬌酒",   "en":"Spirits & Liqueurs",      "emoji":"🍸","bg":"#D6E4F0","tc":"#1A3A6C"},
    "chinese": {"zh":"中國白酒",       "en":"Chinese Baijiu",          "emoji":"🏮","bg":"#FADBD8","tc":"#922B21"},
    "beer":    {"zh":"啤酒/飲料",      "en":"Beer & Beverages",        "emoji":"🍺","bg":"#FEF9E7","tc":"#784212"},
}

def slugify(text):
    text = str(text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")[:80]

# ── Load products ──
def load_all_products():
    all_prods = {}
    slug_seen = {}
    for cat in CATEGORIES_ORDER:
        fp = PROD_DIR / f"{cat}.json"
        if not fp.exists():
            all_prods[cat] = []
            continue
        items = json.loads(fp.read_text(encoding="utf-8"))
        for i, p in enumerate(items):
            base = slugify(p.get("name_en","") or f"product-{i}") or f"{cat}-{i}"
            slug = f"{cat}-{base}"
            if slug in slug_seen:
                slug_seen[slug] += 1
                slug = f"{slug}-{slug_seen[slug]}"
            else:
                slug_seen[slug] = 0
            p["_cat"]  = cat
            p["_slug"] = slug
        all_prods[cat] = items
    return all_prods

print("Loading product data...")
ALL_PRODUCTS = load_all_products()
CAT_COUNTS = {cat: len(prods) for cat, prods in ALL_PRODUCTS.items()}
print(f"Loaded: { {c: CAT_COUNTS[c] for c in CATEGORIES_ORDER} }")

# ── Generate products-data.js ──
def build_products_data_js():
    lines = ["// MTH Products Data — auto-generated\nconst MTH_PRODUCTS = {"]
    for cat in CATEGORIES_ORDER:
        items = ALL_PRODUCTS[cat]
        arr = []
        for p in items:
            obj = {
                "slug":    p["_slug"],
                "zh":      p.get("name_zh") or p.get("name_en",""),
                "en":      p.get("name_en",""),
                "spec":    p.get("spec",""),
                "source":  p.get("source",""),
            }
            arr.append(json.dumps(obj, ensure_ascii=False))
        lines.append(f'  "{cat}": [{",".join(arr)}],')
    lines.append("};")
    out = BASE / "assets" / "js" / "products-data.js"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written products-data.js ({out.stat().st_size//1024}KB)")

build_products_data_js()

# ── Nav HTML ──
def make_nav(depth=0):
    p = "../" * depth
    return f'''<nav class="navbar">
  <a href="{p}index.html" class="navbar-logo">
    <img src="{p}assets/images/LOGO.jpg" alt="明德行" onerror="this.style.display='none'">
    <div>
      <div class="logo-text">明德行國際</div>
      <div class="logo-sub">Meng Tak Hong International</div>
    </div>
  </a>
  <ul class="nav-menu">
    <li><a href="{p}index.html">首頁</a></li>
    <li>
      <a href="#">產品分類 ▾</a>
      <ul class="dropdown"><li><a href="{p}category/whisky.html">威士忌</a></li><li><a href="{p}category/cognac.html">干邑/拔蘭地</a></li><li><a href="{p}category/japan.html">日本產品</a></li><li><a href="{p}category/korea.html">韓國/亞洲飲品</a></li><li><a href="{p}category/wine.html">葡萄酒/香檳</a></li><li><a href="{p}category/spirits.html">烈酒/力嬌酒</a></li><li><a href="{p}category/chinese.html">中國白酒</a></li><li><a href="{p}category/beer.html">啤酒/飲料</a></li></ul>
    </li>
    <li><a href="{p}brands.html">品牌</a></li>
    <li><a href="{p}about.html">關於我們</a></li>
    <li><a href="{p}contact.html">聯絡我們</a></li>
  </ul>
  <div class="navbar-search">
    <input id="global-search" type="text" placeholder="搜尋產品...">
    <button>🔍</button>
  </div>
</nav>'''

# ── NEW CSS to append ──
NEW_CSS = """
/* ── Carousel (橫向輪播) ── */
.carousel-section { padding: 52px 40px; background:#fff; border-bottom: 1px solid var(--border); }
.carousel-section:last-child { border-bottom: none; }
.carousel-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:22px; }
.carousel-header-left .carousel-title { font-size:1.55rem; color:var(--navy); font-weight:800; margin:0; }
.carousel-header-left .carousel-subtitle { color:var(--gold); font-size:.8rem; letter-spacing:.06em; margin-top:4px; }
.carousel-view-all { color:var(--gold); font-size:.83rem; font-weight:700; border:1px solid rgba(212,175,55,.4); padding:6px 16px; border-radius:20px; transition:background .2s, color .2s; white-space:nowrap; }
.carousel-view-all:hover { background:var(--gold); color:var(--navy); }
.carousel-wrap-outer { position:relative; display:flex; align-items:center; gap:0; }
.carousel-track-outer { overflow:hidden; flex:1; }
.carousel-track { display:flex; gap:18px; transition:transform .38s cubic-bezier(.4,0,.2,1); }
.carousel-card { flex:0 0 calc(20% - 15px); min-width:0; background:#fff; border:1px solid var(--border); border-radius:10px; overflow:hidden; cursor:pointer; transition:transform .22s, box-shadow .22s, border-color .22s; text-decoration:none; display:block; }
.carousel-card:hover { transform:translateY(-5px); box-shadow:0 12px 32px rgba(0,0,0,.1); border-color:var(--gold); }
.carousel-card-img { aspect-ratio:1/1; overflow:hidden; background:#f9f5ef; display:flex; align-items:center; justify-content:center; font-size:2.4rem; }
.carousel-card-img img { width:100%; height:100%; object-fit:contain; }
.carousel-card-body { padding:10px 12px 14px; }
.carousel-card-zh { font-size:.82rem; color:var(--navy); font-weight:700; line-height:1.35; max-height:2.7em; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; }
.carousel-card-en { font-size:.68rem; color:#aaa; margin-top:3px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.carousel-card-spec { font-size:.68rem; color:#bbb; margin-top:4px; }
.carousel-btn { flex-shrink:0; width:38px; height:38px; border-radius:50%; background:var(--navy); border:none; color:var(--gold); font-size:1.1rem; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:background .2s, color .2s; z-index:2; }
.carousel-btn:hover { background:var(--gold); color:var(--navy); }
.carousel-btn.carousel-prev { margin-right:10px; }
.carousel-btn.carousel-next { margin-left:10px; }

/* ── Category Buttons ── */
.cat-btn-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.cat-btn { background:#1C1C1C; border:1px solid rgba(212,175,55,.2); border-radius:10px; padding:22px 20px 18px; cursor:pointer; transition:border-color .25s, box-shadow .25s; text-decoration:none; display:block; }
.cat-btn:hover { border-color:var(--gold); box-shadow:0 0 18px rgba(212,175,55,.18); }
.cat-btn-zh { color:var(--gold); font-size:1.15rem; font-weight:800; display:block; }
.cat-btn-en { color:rgba(255,255,255,.7); font-size:.75rem; margin-top:5px; display:block; }
.cat-btn-count { color:rgba(255,255,255,.35); font-size:.72rem; margin-top:10px; display:block; letter-spacing:.02em; }

/* ── You May Also Like ── */
.you-may-like-section { background:var(--cream); padding:56px 40px; }
.ymal-title { font-size:1.45rem; color:var(--navy); font-weight:800; margin-bottom:28px; border-left:3px solid var(--gold); padding-left:14px; }
.ymal-title small { font-size:.58em; color:var(--gold); font-weight:400; margin-left:8px; }

/* ── Brands Page ── */
.brands-hero { background:var(--navy); padding:72px 40px; text-align:center; }
.brands-hero h1 { color:var(--gold); font-size:2.4rem; font-weight:800; margin-bottom:8px; }
.brands-hero p { color:rgba(255,255,255,.55); font-size:.9rem; }
.brands-body { max-width:1200px; margin:0 auto; padding:64px 40px; }
.brands-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:24px; }
.brand-item { border:1px solid var(--border); border-radius:10px; overflow:hidden; display:flex; align-items:center; justify-content:center; padding:16px; aspect-ratio:5/3; background:#fff; transition:border-color .22s, box-shadow .22s; cursor:default; }
.brand-item:hover { border-color:var(--gold); box-shadow:0 4px 20px rgba(212,175,55,.15); }
.brand-item img { max-width:100%; max-height:100%; object-fit:contain; }
.brand-item-text { font-size:.85rem; color:var(--navy); font-weight:700; text-align:center; line-height:1.4; }

@media (max-width:1100px) {
  .carousel-card { flex:0 0 calc(25% - 14px); }
  .cat-btn-grid { grid-template-columns:repeat(2,1fr); }
  .brands-grid { grid-template-columns:repeat(3,1fr); }
}
@media (max-width:760px) {
  .carousel-card { flex:0 0 calc(50% - 9px); }
  .cat-btn-grid { grid-template-columns:repeat(2,1fr); }
  .carousel-section { padding:40px 16px; }
  .brands-grid { grid-template-columns:repeat(3,1fr); }
  .you-may-like-section { padding:40px 16px; }
}
"""

# ── Append new CSS ──
css_path = BASE / "assets" / "css" / "style.css"
existing_css = css_path.read_text(encoding="utf-8")
marker = "/* ── GENERATED ADDITIONS ── */"
if marker not in existing_css:
    css_path.write_text(existing_css + "\n" + marker + "\n" + NEW_CSS, encoding="utf-8")
    print("Appended new CSS")
else:
    print("CSS already updated (marker found)")

# ── Homepage: category buttons HTML ──
def build_cat_buttons():
    rows = []
    for cat in CATEGORIES_ORDER:
        m = CAT_META[cat]
        cnt = CAT_COUNTS.get(cat, 0)
        rows.append(f'''<a href="category/{cat}.html" class="cat-btn">
  <span class="cat-btn-zh">{m["zh"]}</span>
  <span class="cat-btn-en">{m["en"]}</span>
  <span class="cat-btn-count">{cnt} 款產品</span>
</a>''')
    return f'<div class="cat-btn-grid">\n{"".join(rows)}\n</div>'

# ── Homepage: 6 carousel sections ──
CAROUSEL_CATS = [
    ("whisky",  "威士忌精選",    "Whisky Selection"),
    ("korea",   "韓國產品精選",  "Korean Selection"),
    ("japan",   "日本產品精選",  "Japanese Selection"),
    ("wine",    "葡萄酒精選",    "Wine Selection"),
    ("spirits", "烈酒/力嬌酒",  "Spirits & Liqueur"),
    ("chinese", "中國白酒",      "Chinese Spirits"),
]

def build_carousels_html():
    sections = []
    for idx, (cat, zh, en) in enumerate(CAROUSEL_CATS):
        sections.append(f'''<div class="carousel-section">
  <div class="carousel-header">
    <div class="carousel-header-left">
      <div class="carousel-title">{zh}</div>
      <div class="carousel-subtitle">{en}</div>
    </div>
    <a href="category/{cat}.html" class="carousel-view-all">瀏覽全部 →</a>
  </div>
  <div class="carousel-wrap-outer" id="wrap-{cat}">
    <button class="carousel-btn carousel-prev" onclick="carouselMove('{cat}', -1)">❮</button>
    <div class="carousel-track-outer">
      <div class="carousel-track" id="track-{cat}"></div>
    </div>
    <button class="carousel-btn carousel-next" onclick="carouselMove('{cat}', 1)">❯</button>
  </div>
</div>''')
    return "\n".join(sections)

# ── Homepage carousel JS ──
def build_carousel_js():
    cats_list = json.dumps([c for c, _, _ in CAROUSEL_CATS])
    return f'''<script>
var _carouselState = {{}};
var _carouselItems = {{}};

function carouselCard(p, prefix) {{
  prefix = prefix || '';
  var badge = p.source === '代理正貨' ? '<span style="font-size:.6rem;color:var(--gold);border:1px solid rgba(212,175,55,.3);padding:1px 6px;border-radius:20px;margin-bottom:4px;display:inline-block;">代理正貨</span><br>' : '';
  return '<a href="' + prefix + 'product/' + p.slug + '.html" class="carousel-card">' +
    '<div class="carousel-card-img"><img src="' + prefix + 'assets/images/products/' + p.slug + '.jpg" alt="' + (p.zh||'') + '" loading="lazy" onerror="this.parentElement.style.fontSize=\'2rem\';this.parentElement.innerHTML=\'🍾\'"></div>' +
    '<div class="carousel-card-body">' + badge +
    '<div class="carousel-card-zh">' + (p.zh||'') + '</div>' +
    '<div class="carousel-card-en">' + (p.en||'') + '</div>' +
    '<div class="carousel-card-spec">' + (p.spec||'') + '</div>' +
    '</div></a>';
}}

function carouselInit(cat, count, prefix, trackId, excludeSlug) {{
  if (!window.MTH_PRODUCTS || !MTH_PRODUCTS[cat]) return;
  var data = MTH_PRODUCTS[cat].slice();
  if (excludeSlug) data = data.filter(function(p){{return p.slug !== excludeSlug;}});
  data.sort(function(){{return Math.random()-.5;}});
  var items = data.slice(0, count);
  var tid = trackId || ('track-' + cat);
  var track = document.getElementById(tid);
  if (!track) return;
  track.innerHTML = items.map(function(p){{return carouselCard(p, prefix);}}).join('');
  _carouselItems[cat] = items.length;
  _carouselState[cat] = 0;
}}

function carouselMove(cat, dir) {{
  var track = document.getElementById('track-' + cat);
  if (!track) return;
  var cardW = track.parentElement.offsetWidth / 5 + 18;
  var total = _carouselItems[cat] || 15;
  var maxOffset = Math.max(0, total - 5);
  _carouselState[cat] = Math.max(0, Math.min(maxOffset, (_carouselState[cat]||0) + dir));
  track.style.transform = 'translateX(-' + (_carouselState[cat] * (cardW)) + 'px)';
}}

function ymalMove(dir) {{
  carouselMove('__ymal__', dir);
}}

document.addEventListener('DOMContentLoaded', function() {{
  var cats = {cats_list};
  cats.forEach(function(cat) {{
    carouselInit(cat, 15, '', 'track-' + cat, null);
  }});

  // You May Also Like (product pages)
  var ymalSection = document.getElementById('ymal-section');
  if (ymalSection) {{
    var cat = ymalSection.getAttribute('data-cat');
    var current = ymalSection.getAttribute('data-current');
    carouselInit('__ymal__', 10, '../', 'ymal-track', current);
    if (window.MTH_PRODUCTS && MTH_PRODUCTS[cat]) {{
      // override state key
      _carouselItems['__ymal__'] = Math.min(10, MTH_PRODUCTS[cat].length);
    }}
  }}
}});
</script>'''

# ── You May Also Like HTML block for product pages ──
def build_ymal_html(cat, slug):
    return f'''<div class="you-may-like-section" id="ymal-section" data-cat="{cat}" data-current="{slug}">
  <div class="related-inner" style="max-width:1300px;margin:0 auto;">
    <h2 class="ymal-title">你可能喜歡<small>You May Also Like</small></h2>
    <div class="carousel-wrap-outer">
      <button class="carousel-btn carousel-prev" onclick="ymalMove(-1)">❮</button>
      <div class="carousel-track-outer">
        <div class="carousel-track" id="ymal-track"></div>
      </div>
      <button class="carousel-btn carousel-next" onclick="ymalMove(1)">❯</button>
    </div>
  </div>
</div>'''

# ── Build new index.html ──
print("\n=== Updating index.html ===")
index_html = (BASE / "index.html").read_text(encoding="utf-8")

# Read footer (preserve it)
footer_match = re.search(r'<footer>.*?</body>', index_html, re.DOTALL)
footer_html = footer_match.group(0) if footer_match else "</body>"

new_index = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>首頁 | 明德行國際有限公司</title>
  <meta name="description" content="明德行國際有限公司 — 澳門洋酒、飲品批發代理，專業B2B服務，成立於1998年。">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

{make_nav(0)}

<section class="hero">
  <div class="hero-content">
    <div class="hero-eyebrow">Meng Tak Hong International · Est. 1998</div>
    <h1>澳門 <span>洋酒飲品</span><br>批發代理</h1>
    <p>專業B2B批發服務 · 威士忌 · 干邑 · 葡萄酒 · 日本酒 · 韓國飲品</p>
  </div>
</section>

<div class="section-dark">
  <div class="section-dark-inner">
    <div class="section-header">
      <div class="eyebrow">Our Categories</div>
      <h2 class="white">產品分類</h2>
      <p class="white">覆蓋全線洋酒、飲品及食品</p>
      <div class="divider-gold"></div>
    </div>
    {build_cat_buttons()}
  </div>
</div>

{build_carousels_html()}

<div class="section-dark" style="padding:56px 40px;">
  <div class="section-dark-inner" style="display:grid;grid-template-columns:repeat(3,1fr);gap:40px;text-align:center;">
    <div>
      <div style="font-size:2.6rem;font-weight:800;color:var(--gold);margin-bottom:6px;">1998</div>
      <div style="color:rgba(255,255,255,.6);font-size:.83rem;letter-spacing:.1em;">年成立</div>
    </div>
    <div>
      <div style="font-size:2.6rem;font-weight:800;color:var(--gold);margin-bottom:6px;">683+</div>
      <div style="color:rgba(255,255,255,.6);font-size:.83rem;letter-spacing:.1em;">款產品</div>
    </div>
    <div>
      <div style="font-size:2.6rem;font-weight:800;color:var(--gold);margin-bottom:6px;">B2B</div>
      <div style="color:rgba(255,255,255,.6);font-size:.83rem;letter-spacing:.1em;">批發服務</div>
    </div>
  </div>
</div>

{footer_html.replace("</body>","")}
<script src="assets/js/products-data.js"></script>
<script src="assets/js/main.js"></script>
{build_carousel_js()}
</body>
</html>'''

(BASE / "index.html").write_text(new_index, encoding="utf-8")
print("index.html updated")

# ── Update nav in category pages + about + contact ──
def update_nav_in_file(fpath, depth):
    try:
        html = fpath.read_text(encoding="utf-8")
        # Replace navbar block
        new_html = re.sub(r'<nav class="navbar">.*?</nav>', make_nav(depth), html, flags=re.DOTALL)
        # Add products-data.js if not present
        if "products-data.js" not in new_html:
            new_html = new_html.replace('<script src="', f'<script src="{"../"*depth}assets/js/products-data.js"></script>\n<script src="', 1)
        fpath.write_text(new_html, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error updating {fpath.name}: {e}")
        return False

print("\n=== Updating category pages nav ===")
count = 0
for cat in CATEGORIES_ORDER:
    fp = BASE / "category" / f"{cat}.html"
    if fp.exists():
        if update_nav_in_file(fp, 1):
            count += 1
print(f"Updated {count} category pages")

print("\n=== Updating about/contact ===")
for fn in ["about.html","contact.html"]:
    fp = BASE / fn
    if fp.exists():
        update_nav_in_file(fp, 0)
        print(f"  Updated {fn}")

# ── Update product pages ──
print("\n=== Updating product pages ===")

def cat_from_slug(slug):
    for cat in CATEGORIES_ORDER:
        if slug.startswith(cat + "-"):
            return cat
    return None

def update_product_page(fpath):
    slug = fpath.stem
    cat  = cat_from_slug(slug)
    if cat is None:
        return False
    try:
        html = fpath.read_text(encoding="utf-8")
        # 1. Update nav
        html = re.sub(r'<nav class="navbar">.*?</nav>', make_nav(1), html, flags=re.DOTALL)
        # 2. Replace related-section with YMAL
        ymal = build_ymal_html(cat, slug)
        html = re.sub(r'<div class="related-section"[^>]*>.*?</div>\s*</div>\s*</div>', ymal, html, flags=re.DOTALL)
        # 3. Add products-data.js before closing body
        if "products-data.js" not in html:
            html = html.replace('<script src="../assets/js/main.js"></script>',
                '<script src="../assets/js/products-data.js"></script>\n<script src="../assets/js/main.js"></script>')
        # 4. Add carousel JS if not present
        if "carouselInit" not in html:
            cjs = build_carousel_js()
            html = html.replace("</body>", cjs + "\n</body>")
        fpath.write_text(html, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error {fpath.name}: {e}")
        return False

prod_files = list((BASE / "product").glob("*.html"))
total = len(prod_files)
updated = 0
failed = 0
for i, fp in enumerate(prod_files):
    if update_product_page(fp):
        updated += 1
    else:
        failed += 1
    if (i+1) % 100 == 0:
        print(f"  Progress: {i+1}/{total}  updated={updated}  failed={failed}")

print(f"Product pages: {updated} updated, {failed} failed out of {total}")

# ── Download brand logos ──
print("\n=== Downloading brand logos ===")

BRANDS = [
    ("lotte.png",           "LOTTE 樂天",           "LOTTE korean brand logo transparent PNG"),
    ("ottogi.png",          "OTTOGI 不倒翁",         "OTTOGI korean food brand logo PNG transparent"),
    ("hite.png",            "HITE 海特啤酒",         "Hite beer Korean brand logo PNG transparent"),
    ("jinro.png",           "JINRO 真露",            "Jinro soju Korean brand logo transparent PNG"),
    ("guizhou_xijiu.png",   "貴州習酒",              "贵州习酒 Guizhou Xijiu baijiu logo PNG"),
    ("meukow.png",          "Meukow Cognac 金豹",    "Meukow cognac brand logo transparent PNG"),
    ("bardinet.png",        "BARDINET",              "Bardinet cognac brandy logo transparent PNG"),
    ("beehive.png",         "BEEHIVE 蜂巢",          "Beehive brandy French logo PNG transparent"),
    ("king_arthur.png",     "King Arthur XV XO",     "King Arthur XV XO brandy logo PNG"),
    ("cutty_sark.png",      "Cutty Sark",            "Cutty Sark whisky Scotch logo PNG transparent"),
    ("glen_moray.png",      "Glen Moray",            "Glen Moray whisky logo PNG transparent"),
    ("label5.png",          "LABEL 5",               "Label 5 whisky Scotch logo PNG transparent"),
    ("old_pulteney.png",    "Old Pulteney",          "Old Pulteney whisky logo PNG transparent"),
    ("balblair.png",        "Balblair",              "Balblair whisky Highland logo PNG transparent"),
    ("mars_whisky.png",     "Mars Whisky",           "Mars Whisky Shinshu distillery logo PNG transparent"),
    ("myers_rum.png",       "MYERS'S RUM",           "Myers's rum Planters logo PNG transparent"),
    ("hamafukutsuru.png",   "浜福鶴",                "Hamafukutsuru sake Japanese logo PNG"),
    ("kobe_winery.png",     "神戶 Kobe Winery",      "Kobe winery Japanese logo PNG transparent"),
    ("hakutsuru.png",       "Hakutsuru 白鶴",        "Hakutsuru sake logo PNG transparent"),
    ("otokoyama.png",       "男山 Otokoyama",        "Otokoyama sake Japanese logo PNG transparent"),
    ("togouchi.png",        "戶河內 Togouchi",       "Togouchi Japanese whisky logo PNG transparent"),
    ("vidigal_brutalis.png","Vidigal Brutalis",      "Vidigal Wines Brutalis Portugal wine logo PNG"),
    ("casal_branco.png",    "Casal Branco",          "Quinta do Casal Branco wine logo PNG transparent"),
    ("vina_marty.png",      "VINA MARTY",            "Vina Marty Chile wine logo PNG transparent"),
]

downloaded = []
failed_brands = []

def try_download(url, dest, timeout=12):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
        if len(data) < 800:
            return False
        dest.write_bytes(data)
        return True
    except:
        return False

try:
    from ddgs import DDGS
    ddgs_available = True
except ImportError:
    ddgs_available = False
    print("  ddgs not available, will try direct URLs only")

def search_and_download(filename, brand_name, query):
    dest = BRANDS_DIR / filename
    if dest.exists() and dest.stat().st_size > 800:
        print(f"  [SKIP] {filename} already exists")
        return True

    if ddgs_available:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.images(query, max_results=5))
            for r in results:
                url = r.get("image","")
                if url and any(url.lower().endswith(ext) for ext in [".png",".jpg",".jpeg",".webp"]):
                    if try_download(url, dest):
                        print(f"  [OK] {filename} <- {url[:60]}")
                        return True
            time.sleep(0.5)
        except Exception as e:
            print(f"  [DDGS err] {filename}: {e}")

    print(f"  [FAIL] {filename} - {brand_name}")
    return False

for filename, brand_name, query in BRANDS:
    ok = search_and_download(filename, brand_name, query)
    if ok:
        downloaded.append(filename)
    else:
        failed_brands.append(brand_name)
    time.sleep(0.3)

# ── Process logos with Pillow ──
try:
    from PIL import Image
    pillow_ok = True
except ImportError:
    pillow_ok = False
    print("Pillow not available, skipping logo processing")

if pillow_ok:
    print("\n=== Processing logos (200x120) ===")
    for filename, _, _ in BRANDS:
        src = BRANDS_DIR / filename
        if not src.exists():
            continue
        try:
            img = Image.open(src).convert("RGBA")
            # White background
            canvas = Image.new("RGBA", (200, 120), (255,255,255,255))
            img.thumbnail((180, 100), Image.LANCZOS)
            x = (200 - img.width)  // 2
            y = (120 - img.height) // 2
            canvas.paste(img, (x, y), img if img.mode == "RGBA" else None)
            final = canvas.convert("RGB")
            final.save(str(src.with_suffix(".png")), "PNG")
        except Exception as e:
            print(f"  Pillow error {filename}: {e}")
    print("Logo processing done")

# ── Build brands.html ──
print("\n=== Building brands.html ===")

def brand_item(filename, brand_name):
    src_path = BRANDS_DIR / filename
    if src_path.exists():
        return f'''<div class="brand-item">
  <img src="assets/images/brands/{filename}" alt="{brand_name}" title="{brand_name}" onerror="this.style.display='none';this.nextElementSibling.style.display='block'">
  <div class="brand-item-text" style="display:none">{brand_name}</div>
</div>'''
    else:
        return f'<div class="brand-item"><div class="brand-item-text">{brand_name}</div></div>'

brands_items = "\n".join(brand_item(fn, name) for fn, name, _ in BRANDS)

footer_block = '''<footer>
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-logo">
        <img src="assets/images/LOGO.jpg" alt="明德行" onerror="this.style.display='none'">
        <div class="company-zh">明德行國際有限公司</div>
        <div class="company-en">Meng Tak Hong International Co., Ltd.</div>
        <div class="est">Est. 1998</div>
        <address>
          澳門黑沙環慕拉士大馬路195號<br>南嶺工業大廈4樓F<br><br>
          📞 <a href="tel:+85328415128">28415128</a> / <a href="tel:+85328584838">28584838</a><br>
          ✉ <a href="mailto:info@mengtakhong.com">info@mengtakhong.com</a>
        </address>
      </div>
      <div class="footer-col">
        <h4>產品分類</h4>
        <ul><li><a href="category/whisky.html">威士忌</a></li><li><a href="category/cognac.html">干邑/拔蘭地</a></li><li><a href="category/japan.html">日本產品</a></li><li><a href="category/korea.html">韓國/亞洲飲品</a></li><li><a href="category/wine.html">葡萄酒/香檳</a></li><li><a href="category/spirits.html">烈酒/力嬌酒</a></li><li><a href="category/chinese.html">中國白酒</a></li><li><a href="category/beer.html">啤酒/飲料</a></li></ul>
      </div>
      <div class="footer-col">
        <h4>聯絡我們</h4>
        <div class="footer-social">
          <a href="https://wa.me/85366687448" class="social-btn wa" target="_blank">WhatsApp 查詢</a>
          <a href="https://www.facebook.com/profile.php?id=61555744448402" class="social-btn fb" target="_blank">Facebook</a>
          <a href="https://www.instagram.com/mengtakhong.mo/" class="social-btn ig" target="_blank">Instagram</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2025 明德行國際有限公司 Meng Tak Hong International Co., Ltd. All Rights Reserved.</span>
      <span>澳門 Macau</span>
    </div>
  </div>
</footer>'''

brands_html = f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>我們的品牌 | 明德行國際有限公司</title>
  <meta name="description" content="明德行國際有限公司代理品牌一覽 — 澳門洋酒、飲品批發代理">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

{make_nav(0)}

<div class="brands-hero">
  <div class="section-header">
    <div class="eyebrow">Our Brands</div>
    <h1>我們的品牌</h1>
    <p style="color:rgba(255,255,255,.55);">明德行代理品牌一覽</p>
    <div class="divider-gold"></div>
  </div>
</div>

<div class="brands-body">
  <div class="brands-grid">
{brands_items}
  </div>
</div>

{footer_block}
<script src="assets/js/main.js"></script>
</body>
</html>'''

(BASE / "brands.html").write_text(brands_html, encoding="utf-8")
print("brands.html created")

# ── Summary ──
print("\n" + "="*50)
print("✅ 完成！")
print(f"  修改一+二: index.html — 6個輪播 + 按鈕分類")
print(f"  修改三: product pages — {updated}/{total} 已更新")
print(f"  修改四: brands.html — 建立完成")
print(f"    Logo 成功下載: {len(downloaded)}/{len(BRANDS)}")
if failed_brands:
    print(f"    下載失敗: {', '.join(failed_brands)}")
print(f"  修改五: 全部頁面導航已加入「品牌」")
