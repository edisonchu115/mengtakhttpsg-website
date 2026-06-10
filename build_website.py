#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明德行國際有限公司 網站生成器
Meng Tak Hong International Co., Ltd. Website Builder
"""

import json, os, shutil, re
from pathlib import Path

BASE_DIR   = Path(r"C:\Users\user\Desktop\mengtakhong-website")
PROD_DIR   = BASE_DIR / "products"
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
CSS_DIR    = ASSETS_DIR / "css"
JS_DIR     = ASSETS_DIR / "js"
CAT_DIR    = BASE_DIR / "category"
PROD_PAGE_DIR = BASE_DIR / "product"

CATEGORIES = {
    "whisky":  {"zh":"威士忌",       "en":"Whisky",                  "color":"#8B6914","bg":"#F5E6C8","desc":"蘇格蘭、愛爾蘭、美國、日本等世界各地頂級威士忌"},
    "cognac":  {"zh":"干邑/拔蘭地",  "en":"Cognac & Brandy",         "color":"#8B2500","bg":"#F5D5C8","desc":"法國頂級干邑及優質拔蘭地系列"},
    "japan":   {"zh":"日本產品",      "en":"Japanese Products",       "color":"#C0392B","bg":"#FDEAEA","desc":"日本威士忌、清酒、燒酎及特色飲品"},
    "korea":   {"zh":"韓國/亞洲飲品","en":"Korean & Asian Beverages","color":"#1A5276","bg":"#D6EAF8","desc":"韓國燒酒、啤酒、飲料及亞洲特色食品"},
    "wine":    {"zh":"葡萄酒/香檳",  "en":"Wine & Champagne",        "color":"#6C3483","bg":"#F4ECF7","desc":"法國、澳洲、葡萄牙、智利等產區優質葡萄酒及香檳"},
    "spirits": {"zh":"烈酒/力嬌酒",  "en":"Spirits & Liqueurs",      "color":"#1A3A6C","bg":"#D6E4F0","desc":"琴酒、伏特加、冧酒、龍舌蘭及各式力嬌酒"},
    "chinese": {"zh":"中國白酒",      "en":"Chinese Baijiu",          "color":"#922B21","bg":"#FADBD8","desc":"貴州茅台、習酒等頂級中國醬香白酒"},
    "beer":    {"zh":"啤酒/飲料",     "en":"Beer & Beverages",        "color":"#784212","bg":"#FEF9E7","desc":"各式啤酒、汽水、果汁及非酒精飲料"},
}

WA_LINK = "https://wa.me/85366687448"
FB_LINK = "https://www.facebook.com/profile.php?id=61555744448402"
IG_LINK = "https://www.instagram.com/mengtakhong.mo/"

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def slugify(text):
    text = str(text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")[:80]

def load_products():
    all_products = {}
    slug_seen = {}
    for cat, meta in CATEGORIES.items():
        fp = PROD_DIR / f"{cat}.json"
        if not fp.exists():
            all_products[cat] = []
            continue
        with open(fp, "r", encoding="utf-8") as f:
            items = json.load(f)
        for i, p in enumerate(items):
            base = slugify(p.get("name_en", f"product-{i}")) or f"{cat}-{i}"
            slug = f"{cat}-{base}"
            # ensure unique
            if slug in slug_seen:
                slug_seen[slug] += 1
                slug = f"{slug}-{slug_seen[slug]}"
            else:
                slug_seen[slug] = 0
            p["_cat"]  = cat
            p["_slug"] = slug
        all_products[cat] = items
    return all_products

def abv_str(p):
    v = p.get("abv")
    if v is None: return "—"
    return f"{v}%"

def source_badge(p, small=False):
    if p.get("source") == "代理正貨":
        cls = "badge-agency-sm" if small else "badge-agency"
        return f'<span class="{cls}">代理正貨</span>'
    return ""

# ──────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────
CSS = """
/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { font-family: 'Noto Serif TC', 'Georgia', serif; color: #4A4A4A; background: #fff; line-height: 1.7; }
a { text-decoration: none; color: inherit; }
img { max-width: 100%; display: block; }
ul { list-style: none; }

/* ── Variables ── */
:root {
  --gold: #D4AF37;
  --gold-dark: #B8960C;
  --navy: #1C1C1C;
  --cream: #F5F0E8;
  --border: #E5DDD0;
  --text: #4A4A4A;
}

/* ── Navbar ── */
.navbar {
  background: var(--navy);
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 12px rgba(0,0,0,.4);
}
.navbar-logo img { height: 48px; width: auto; object-fit: contain; }
.navbar-logo .logo-text { color: #fff; font-size: 1.15rem; font-weight: 700; letter-spacing: .05em; }
.navbar-logo .logo-sub  { color: var(--gold); font-size: .65rem; letter-spacing: .15em; text-transform: uppercase; }
.navbar-logo { display: flex; align-items: center; gap: 12px; }

.nav-menu { display: flex; align-items: center; gap: 6px; }
.nav-menu > li { position: relative; }
.nav-menu > li > a {
  color: #fff;
  font-size: .88rem;
  letter-spacing: .04em;
  padding: 8px 14px;
  border-radius: 4px;
  transition: color .2s, background .2s;
  display: block;
}
.nav-menu > li > a:hover,
.nav-menu > li > a.active { color: var(--gold); background: rgba(212,175,55,.08); }

.dropdown { display: none; position: absolute; top: 100%; left: 0; background: var(--navy);
  border: 1px solid rgba(212,175,55,.2); border-top: 2px solid var(--gold);
  min-width: 200px; border-radius: 0 0 6px 6px; box-shadow: 0 8px 24px rgba(0,0,0,.4); z-index: 999; }
.nav-menu > li:hover .dropdown { display: block; }
.dropdown li a { display: block; padding: 10px 18px; font-size: .83rem; color: #ccc; border-bottom: 1px solid rgba(255,255,255,.05); transition: color .2s, background .2s; }
.dropdown li:last-child a { border-bottom: none; }
.dropdown li a:hover { color: var(--gold); background: rgba(212,175,55,.06); }

.navbar-search { display: flex; align-items: center; gap: 0; }
.navbar-search input {
  background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.2);
  color: #fff;
  padding: 7px 14px;
  font-size: .83rem;
  border-radius: 20px 0 0 20px;
  outline: none;
  width: 190px;
  transition: width .3s, background .2s;
}
.navbar-search input:focus { width: 230px; background: rgba(255,255,255,.12); }
.navbar-search input::placeholder { color: rgba(255,255,255,.45); }
.navbar-search button {
  background: var(--gold);
  border: none;
  color: var(--navy);
  padding: 7px 14px;
  border-radius: 0 20px 20px 0;
  cursor: pointer;
  font-size: .9rem;
  font-weight: 700;
  transition: background .2s;
}
.navbar-search button:hover { background: var(--gold-dark); }

/* ── Hero ── */
.hero {
  position: relative;
  height: 540px;
  overflow: hidden;
  background: linear-gradient(135deg, #1C1C1C 0%, #2C2416 60%, #1C1C1C 100%);
  display: flex; align-items: center; justify-content: center; text-align: center;
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23D4AF37' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.hero-content { position: relative; z-index: 1; max-width: 760px; padding: 0 24px; }
.hero-eyebrow { color: var(--gold); font-size: .8rem; letter-spacing: .35em; text-transform: uppercase; margin-bottom: 18px; }
.hero h1 { color: #fff; font-size: 3rem; font-weight: 800; line-height: 1.15; margin-bottom: 16px; text-shadow: 0 2px 12px rgba(0,0,0,.5); }
.hero h1 span { color: var(--gold); }
.hero p { color: rgba(255,255,255,.75); font-size: 1.05rem; margin-bottom: 32px; }
.hero-cta { display: inline-flex; align-items: center; gap: 10px; background: var(--gold); color: var(--navy); padding: 13px 30px; border-radius: 40px; font-weight: 700; font-size: .93rem; letter-spacing: .06em; transition: transform .2s, box-shadow .2s; box-shadow: 0 4px 20px rgba(212,175,55,.35); }
.hero-cta:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(212,175,55,.45); }

/* ── Section ── */
.section { padding: 72px 40px; max-width: 1300px; margin: 0 auto; }
.section-dark { background: var(--navy); padding: 72px 40px; }
.section-dark-inner { max-width: 1300px; margin: 0 auto; }
.section-cream { background: var(--cream); padding: 72px 40px; }
.section-cream-inner { max-width: 1300px; margin: 0 auto; }

.section-header { text-align: center; margin-bottom: 52px; }
.section-header .eyebrow { font-size: .72rem; letter-spacing: .35em; text-transform: uppercase; color: var(--gold); margin-bottom: 10px; }
.section-header h2 { font-size: 2.1rem; color: var(--navy); font-weight: 800; margin-bottom: 12px; }
.section-header h2.white { color: #fff; }
.section-header p { color: #888; max-width: 520px; margin: 0 auto; font-size: .9rem; }
.section-header p.white { color: rgba(255,255,255,.6); }
.divider-gold { width: 56px; height: 2px; background: var(--gold); margin: 14px auto 0; }

/* ── Category Grid ── */
.cat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.cat-card {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform .25s, box-shadow .25s;
  text-decoration: none;
  background: #fff;
  border: 1px solid var(--border);
}
.cat-card:hover { transform: translateY(-6px); box-shadow: 0 16px 40px rgba(0,0,0,.13); }
.cat-card-img {
  height: 140px;
  display: flex; align-items: center; justify-content: center;
  font-size: 3.5rem;
}
.cat-card-body { padding: 18px 20px 22px; }
.cat-card-body h3 { font-size: 1.1rem; color: var(--navy); font-weight: 700; margin-bottom: 5px; }
.cat-card-body p  { font-size: .78rem; color: #888; line-height: 1.5; }
.cat-card-body .cat-count { margin-top: 12px; font-size: .75rem; color: var(--gold); font-weight: 600; letter-spacing: .05em; }

/* ── Product Card ── */
.product-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.prod-card {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform .22s, box-shadow .22s;
  text-decoration: none;
  display: block;
}
.prod-card:hover { transform: translateY(-5px); box-shadow: 0 14px 36px rgba(0,0,0,.11); }
.prod-card-img {
  height: 180px;
  display: flex; align-items: center; justify-content: center;
  font-size: 2.8rem;
  position: relative;
}
.prod-card-body { padding: 14px 16px 18px; }
.prod-card-body h4 { font-size: .93rem; color: var(--navy); font-weight: 700; margin-bottom: 4px; line-height: 1.35; }
.prod-card-body .en-name { font-size: .75rem; color: #aaa; margin-bottom: 8px; }
.prod-card-meta { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; font-size: .72rem; color: #888; }
.prod-card-meta .spec { background: var(--cream); padding: 2px 8px; border-radius: 20px; border: 1px solid var(--border); }
.prod-card-meta .abv  { color: var(--gold); font-weight: 600; }

/* ── Badges ── */
.badge-agency    { display: inline-block; font-size: .7rem; color: var(--gold); border: 1px solid rgba(212,175,55,.45); padding: 2px 9px; border-radius: 20px; letter-spacing: .04em; margin-bottom: 6px; }
.badge-agency-sm { display: inline-block; font-size: .65rem; color: var(--gold); border: 1px solid rgba(212,175,55,.35); padding: 1px 7px; border-radius: 20px; letter-spacing: .03em; }
.badge-cat { display: inline-block; font-size: .7rem; background: var(--cream); color: var(--navy); border: 1px solid var(--border); padding: 2px 10px; border-radius: 20px; letter-spacing: .03em; }

/* ── Breadcrumb ── */
.breadcrumb { background: var(--cream); padding: 14px 40px; font-size: .8rem; color: #888; border-bottom: 1px solid var(--border); }
.breadcrumb-inner { max-width: 1300px; margin: 0 auto; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.breadcrumb a { color: var(--gold); transition: color .2s; }
.breadcrumb a:hover { color: var(--gold-dark); }
.breadcrumb .sep { color: #ccc; }

/* ── Category Page Header ── */
.cat-page-header {
  background: var(--navy);
  padding: 60px 40px;
  text-align: center;
}
.cat-page-header .eyebrow { color: var(--gold); font-size: .75rem; letter-spacing: .35em; text-transform: uppercase; margin-bottom: 10px; }
.cat-page-header h1 { color: #fff; font-size: 2.4rem; font-weight: 800; margin-bottom: 10px; }
.cat-page-header p { color: rgba(255,255,255,.6); font-size: .9rem; max-width: 500px; margin: 0 auto; }
.cat-count-badge { display: inline-block; margin-top: 14px; background: rgba(212,175,55,.15); color: var(--gold); border: 1px solid rgba(212,175,55,.3); padding: 4px 16px; border-radius: 20px; font-size: .8rem; }

/* ── Search Bar ── */
.search-bar-wrap { max-width: 520px; margin: 0 auto 48px; }
.search-bar-wrap input {
  width: 100%;
  padding: 12px 20px;
  border: 2px solid var(--border);
  border-radius: 40px;
  font-size: .9rem;
  font-family: inherit;
  color: var(--navy);
  outline: none;
  transition: border .2s, box-shadow .2s;
}
.search-bar-wrap input:focus { border-color: var(--gold); box-shadow: 0 0 0 3px rgba(212,175,55,.12); }
.search-count { text-align: center; font-size: .8rem; color: #aaa; margin-bottom: 28px; }
.no-results { text-align: center; padding: 60px 20px; color: #aaa; font-size: .95rem; display: none; }

/* ── Product Detail ── */
.product-detail { max-width: 1100px; margin: 0 auto; padding: 56px 40px; display: grid; grid-template-columns: 380px 1fr; gap: 60px; align-items: start; }
.product-detail-img {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border);
  aspect-ratio: 3/4;
  display: flex; align-items: center; justify-content: center;
  font-size: 7rem;
  position: sticky;
  top: 90px;
}
.product-info { }
.product-info .cat-breadcrumb { font-size: .78rem; color: #aaa; margin-bottom: 12px; }
.product-info h1 { font-size: 2.1rem; color: var(--navy); font-weight: 800; line-height: 1.25; margin-bottom: 6px; }
.product-info .en-name { font-size: .95rem; color: #aaa; margin-bottom: 18px; }
.product-info .divider { height: 1px; background: var(--border); margin: 22px 0; }
.spec-table { width: 100%; border-collapse: collapse; }
.spec-table tr td { padding: 10px 0; border-bottom: 1px solid var(--border); font-size: .9rem; }
.spec-table tr:last-child td { border-bottom: none; }
.spec-table td:first-child { color: #999; width: 110px; font-size: .82rem; }
.spec-table td:last-child { color: var(--navy); font-weight: 500; }
.wa-btn {
  display: inline-flex; align-items: center; gap: 10px;
  background: #25D366; color: #fff;
  padding: 14px 28px; border-radius: 40px;
  font-weight: 700; font-size: .92rem;
  transition: background .2s, transform .2s;
  margin-top: 28px;
  text-decoration: none;
}
.wa-btn:hover { background: #1ebe5d; transform: translateY(-2px); }
.wa-btn svg { width: 20px; height: 20px; flex-shrink: 0; }

/* ── Related Products ── */
.related-section { background: var(--cream); padding: 64px 40px; }
.related-inner { max-width: 1300px; margin: 0 auto; }
.related-section h2 { font-size: 1.5rem; color: var(--navy); font-weight: 800; margin-bottom: 32px; border-left: 3px solid var(--gold); padding-left: 14px; }

/* ── About ── */
.about-hero { background: var(--navy); padding: 80px 40px; text-align: center; }
.about-hero h1 { color: #fff; font-size: 2.6rem; font-weight: 800; margin-bottom: 12px; }
.about-hero h1 span { color: var(--gold); }
.about-hero p { color: rgba(255,255,255,.65); max-width: 560px; margin: 0 auto; }
.about-body { max-width: 900px; margin: 0 auto; padding: 72px 40px; }
.about-body h2 { font-size: 1.45rem; color: var(--navy); font-weight: 800; margin: 40px 0 14px; padding-bottom: 8px; border-bottom: 2px solid var(--gold); display: inline-block; }
.about-body p { color: var(--text); line-height: 1.9; margin-bottom: 14px; font-size: .93rem; }
.about-body ul { margin: 12px 0 20px 20px; }
.about-body ul li { color: var(--text); line-height: 1.9; font-size: .93rem; list-style: disc; }
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin: 40px 0; }
.stat-box { background: var(--cream); border: 1px solid var(--border); border-radius: 10px; padding: 28px 20px; text-align: center; }
.stat-box .num { font-size: 2.4rem; font-weight: 800; color: var(--gold); line-height: 1; margin-bottom: 6px; }
.stat-box .label { font-size: .8rem; color: #888; letter-spacing: .06em; }

/* ── Contact ── */
.contact-grid { max-width: 1100px; margin: 0 auto; padding: 72px 40px; display: grid; grid-template-columns: 1fr 1fr; gap: 60px; }
.contact-info h2 { font-size: 1.7rem; color: var(--navy); font-weight: 800; margin-bottom: 8px; }
.contact-info .sub { color: #aaa; font-size: .85rem; margin-bottom: 32px; }
.contact-row { display: flex; gap: 14px; margin-bottom: 20px; align-items: flex-start; }
.contact-row .icon { width: 38px; height: 38px; background: var(--cream); border: 1px solid var(--border); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.contact-row .detail .label { font-size: .72rem; color: #aaa; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 3px; }
.contact-row .detail .val { font-size: .9rem; color: var(--navy); font-weight: 500; }
.social-row { display: flex; gap: 12px; margin-top: 28px; flex-wrap: wrap; }
.social-btn { display: inline-flex; align-items: center; gap: 8px; padding: 9px 18px; border-radius: 8px; font-size: .82rem; font-weight: 600; transition: transform .2s, box-shadow .2s; text-decoration: none; }
.social-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,.15); }
.social-btn.wa  { background: #25D366; color: #fff; }
.social-btn.fb  { background: #1877F2; color: #fff; }
.social-btn.ig  { background: linear-gradient(135deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888); color: #fff; }
.map-wrap iframe { width: 100%; height: 360px; border: none; border-radius: 12px; border: 1px solid var(--border); }

/* ── Footer ── */
footer {
  background: var(--navy);
  padding: 64px 40px 32px;
  color: #fff;
}
.footer-inner { max-width: 1300px; margin: 0 auto; }
.footer-grid { display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 48px; margin-bottom: 48px; }
.footer-logo img { height: 44px; width: auto; object-fit: contain; margin-bottom: 14px; }
.footer-logo .company-zh { font-size: 1rem; font-weight: 700; color: #fff; }
.footer-logo .company-en { font-size: .72rem; color: rgba(255,255,255,.5); letter-spacing: .06em; margin-bottom: 4px; }
.footer-logo .est { font-size: .7rem; color: var(--gold); letter-spacing: .1em; margin-bottom: 18px; }
.footer-logo address { font-style: normal; font-size: .78rem; color: rgba(255,255,255,.55); line-height: 1.8; }
.footer-logo address a { color: rgba(255,255,255,.55); transition: color .2s; }
.footer-logo address a:hover { color: var(--gold); }
.footer-col h4 { font-size: .78rem; letter-spacing: .18em; text-transform: uppercase; color: var(--gold); margin-bottom: 18px; font-weight: 600; }
.footer-col ul li { margin-bottom: 9px; }
.footer-col ul li a { font-size: .83rem; color: rgba(255,255,255,.55); transition: color .2s; }
.footer-col ul li a:hover { color: var(--gold); }
.footer-social { display: flex; flex-direction: column; gap: 10px; }
.footer-social .social-btn { justify-content: flex-start; padding: 8px 16px; border-radius: 6px; font-size: .82rem; }
.footer-bottom { border-top: 1px solid rgba(255,255,255,.1); padding-top: 24px; display: flex; justify-content: space-between; align-items: center; font-size: .75rem; color: rgba(255,255,255,.35); }
.footer-bottom a { color: rgba(255,255,255,.35); }

/* ── Utilities ── */
.text-gold { color: var(--gold); }
.mt-12 { margin-top: 12px; }
.mt-24 { margin-top: 24px; }
.mt-48 { margin-top: 48px; }
.text-center { text-align: center; }

/* ── Responsive ── */
@media (max-width: 1100px) {
  .cat-grid { grid-template-columns: repeat(2, 1fr); }
  .product-grid { grid-template-columns: repeat(3, 1fr); }
  .product-detail { grid-template-columns: 1fr; }
  .product-detail-img { position: static; aspect-ratio: auto; height: 280px; }
  .footer-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 760px) {
  .navbar { padding: 0 16px; height: 60px; }
  .navbar-search, .nav-menu { display: none; }
  .hero h1 { font-size: 2rem; }
  .hero { height: 420px; }
  .section { padding: 48px 16px; }
  .product-grid { grid-template-columns: repeat(2, 1fr); }
  .cat-grid { grid-template-columns: repeat(2, 1fr); }
  .contact-grid { grid-template-columns: 1fr; }
  .footer-grid { grid-template-columns: 1fr; }
  .stat-grid { grid-template-columns: 1fr; }
  .breadcrumb { padding: 12px 16px; }
}
"""

# ──────────────────────────────────────────────
# JS
# ──────────────────────────────────────────────
JS_SEARCH = """
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
"""

# ──────────────────────────────────────────────
# HTML Templates
# ──────────────────────────────────────────────
def nav_html(depth=0):
    prefix = "../" * depth
    cats_html = "".join([
        f'<li><a href="{prefix}category/{k}.html">{v["zh"]}</a></li>'
        for k, v in CATEGORIES.items()
    ])
    return f"""
<nav class="navbar">
  <a href="{prefix}index.html" class="navbar-logo">
    <img src="{prefix}assets/images/LOGO.jpg" alt="明德行" onerror="this.style.display='none'">
    <div>
      <div class="logo-text">明德行國際</div>
      <div class="logo-sub">Meng Tak Hong International</div>
    </div>
  </a>
  <ul class="nav-menu">
    <li><a href="{prefix}index.html">首頁</a></li>
    <li>
      <a href="#">產品分類 ▾</a>
      <ul class="dropdown">{cats_html}</ul>
    </li>
    <li><a href="{prefix}about.html">關於我們</a></li>
    <li><a href="{prefix}contact.html">聯絡我們</a></li>
  </ul>
  <div class="navbar-search">
    <input id="global-search" type="text" placeholder="搜尋產品...">
    <button>🔍</button>
  </div>
</nav>"""

def footer_html(depth=0):
    prefix = "../" * depth
    cat_links = "".join([
        f'<li><a href="{prefix}category/{k}.html">{v["zh"]}</a></li>'
        for k, v in CATEGORIES.items()
    ])
    return f"""
<footer>
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-logo">
        <img src="{prefix}assets/images/LOGO.jpg" alt="明德行" onerror="this.style.display='none'">
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
        <ul>{cat_links}</ul>
      </div>
      <div class="footer-col">
        <h4>聯絡我們</h4>
        <div class="footer-social">
          <a href="{WA_LINK}" class="social-btn wa" target="_blank">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
            WhatsApp 查詢
          </a>
          <a href="{FB_LINK}" class="social-btn fb" target="_blank">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
            Facebook
          </a>
          <a href="{IG_LINK}" class="social-btn ig" target="_blank">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
            Instagram
          </a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2025 明德行國際有限公司 Meng Tak Hong International Co., Ltd. All Rights Reserved.</span>
      <span>澳門 Macau</span>
    </div>
  </div>
</footer>
<script src="{prefix}assets/js/main.js"></script>"""

def page_wrap(title, body, depth=0, extra_head=""):
    prefix = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | 明德行國際有限公司</title>
  <meta name="description" content="明德行國際有限公司 — 澳門洋酒、飲品批發代理，專業B2B服務，成立於1998年。">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}assets/css/style.css">
  {extra_head}
</head>
<body>
{nav_html(depth)}
{body}
{footer_html(depth)}
</body>
</html>"""

# ──────────────────────────────────────────────
# Emoji icons per category
# ──────────────────────────────────────────────
CAT_EMOJI = {"whisky":"🥃","cognac":"🍷","japan":"🗾","korea":"🇰🇷","wine":"🍾","spirits":"🍸","chinese":"🏮","beer":"🍺"}

def get_cat_bg(cat):
    return CATEGORIES[cat]["bg"]

def product_img_html(cat, size="card"):
    bg = CATEGORIES[cat]["bg"]
    color = CATEGORIES[cat]["color"]
    emoji = CAT_EMOJI.get(cat, "🍶")
    if size == "detail":
        return f'<div class="product-detail-img" style="background:{bg};color:{color};">{emoji}</div>'
    return f'<div class="prod-card-img" style="background:{bg};color:{color};">{emoji}</div>'

# ──────────────────────────────────────────────
# Homepage
# ──────────────────────────────────────────────
def build_homepage(all_products):
    cat_cards = ""
    for k, v in CATEGORIES.items():
        count = len(all_products.get(k, []))
        cat_cards += f"""
<a href="category/{k}.html" class="cat-card">
  <div class="cat-card-img" style="background:{v['bg']};color:{v['color']};">{CAT_EMOJI[k]}</div>
  <div class="cat-card-body">
    <h3>{v['zh']}</h3>
    <p>{v['en']}</p>
    <div class="cat-count">{count} 款產品</div>
  </div>
</a>"""

    # Featured products: first 8 from whisky + cognac
    featured = []
    for cat in ["whisky","cognac","wine","spirits"]:
        featured.extend(all_products.get(cat,[])[:2])
    featured = featured[:8]
    feat_cards = ""
    for p in featured:
        cat = p["_cat"]
        feat_cards += f"""
<a href="product/{p['_slug']}.html" class="prod-card">
  {product_img_html(cat)}
  <div class="prod-card-body">
    {source_badge(p, small=True)}
    <h4>{p.get('name_zh','')}</h4>
    <div class="en-name">{p.get('name_en','')}</div>
    <div class="prod-card-meta">
      <span class="spec">{p.get('spec','')}</span>
      <span class="abv">{abv_str(p)}</span>
    </div>
  </div>
</a>"""

    body = f"""
<section class="hero">
  <div class="hero-content">
    <div class="hero-eyebrow">Meng Tak Hong International · Est. 1998</div>
    <h1>澳門 <span>洋酒飲品</span><br>批發代理</h1>
    <p>專業B2B批發服務 · 威士忌 · 干邑 · 葡萄酒 · 日本酒 · 韓國飲品</p>
    <a href="{WA_LINK}" class="hero-cta" target="_blank">
      <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
      WhatsApp 即時查詢
    </a>
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
    <div class="cat-grid">{cat_cards}</div>
  </div>
</div>

<div class="section-cream">
  <div class="section-cream-inner">
    <div class="section-header">
      <div class="eyebrow">Featured Products</div>
      <h2>精選產品</h2>
      <p>部分精選代理及進口產品</p>
      <div class="divider-gold"></div>
    </div>
    <div class="product-grid">{feat_cards}</div>
    <div class="text-center mt-48">
      <a href="category/whisky.html" style="display:inline-block;background:var(--gold);color:var(--navy);padding:12px 32px;border-radius:40px;font-weight:700;font-size:.88rem;transition:transform .2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform=''">瀏覽所有產品</a>
    </div>
  </div>
</div>

<div class="section-dark" style="padding:56px 40px;">
  <div class="section-dark-inner" style="display:grid;grid-template-columns:repeat(3,1fr);gap:40px;text-align:center;">
    <div>
      <div style="font-size:2.6rem;font-weight:800;color:var(--gold);margin-bottom:6px;">1998</div>
      <div style="color:rgba(255,255,255,.6);font-size:.83rem;letter-spacing:.1em;">年成立</div>
    </div>
    <div>
      <div style="font-size:2.6rem;font-weight:800;color:var(--gold);margin-bottom:6px;">500+</div>
      <div style="color:rgba(255,255,255,.6);font-size:.83rem;letter-spacing:.1em;">款產品</div>
    </div>
    <div>
      <div style="font-size:2.6rem;font-weight:800;color:var(--gold);margin-bottom:6px;">B2B</div>
      <div style="color:rgba(255,255,255,.6);font-size:.83rem;letter-spacing:.1em;">批發服務</div>
    </div>
  </div>
</div>
"""
    return page_wrap("首頁", body, depth=0)

# ──────────────────────────────────────────────
# Category Page
# ──────────────────────────────────────────────
def build_category_page(cat_key, products):
    meta = CATEGORIES[cat_key]
    cards = ""
    for p in products:
        search_data = f"{p.get('name_zh','')} {p.get('name_en','')} {p.get('spec','')}".lower()
        cards += f"""
<a href="../product/{p['_slug']}.html" class="prod-card" data-search="{search_data}">
  {product_img_html(cat_key)}
  <div class="prod-card-body">
    {source_badge(p, small=True)}
    <h4>{p.get('name_zh','')}</h4>
    <div class="en-name">{p.get('name_en','')}</div>
    <div class="prod-card-meta">
      <span class="spec">{p.get('spec','')}</span>
      <span class="abv">{abv_str(p)}</span>
    </div>
  </div>
</a>"""

    body = f"""
<div class="breadcrumb">
  <div class="breadcrumb-inner">
    <a href="../index.html">首頁</a>
    <span class="sep">›</span>
    <span>{meta['zh']}</span>
  </div>
</div>

<div class="cat-page-header">
  <div class="eyebrow">Product Category</div>
  <h1>{CAT_EMOJI[cat_key]} {meta['zh']}</h1>
  <p>{meta['desc']}</p>
  <div class="cat-count-badge">{len(products)} 款產品</div>
</div>

<div style="padding:48px 40px;max-width:1300px;margin:0 auto;">
  <div class="search-bar-wrap">
    <input id="cat-search" type="text" placeholder="搜尋 {meta['zh']} 產品名稱...">
  </div>
  <div class="search-count" id="search-count">顯示 {len(products)} 個產品</div>
  <div class="no-results" id="no-results">找不到相關產品，請嘗試其他關鍵字。</div>
  <div class="product-grid" id="product-grid">{cards}</div>
</div>
"""
    return page_wrap(meta["zh"], body, depth=1)

# ──────────────────────────────────────────────
# Product Detail Page
# ──────────────────────────────────────────────
def build_product_page(p, related):
    cat_key = p["_cat"]
    meta = CATEGORIES[cat_key]
    abv_display = abv_str(p)
    cat_type = p.get("category", "").replace("_"," ").title()

    spec_rows = f"""
<tr><td>規格</td><td>{p.get('spec','—')}</td></tr>
<tr><td>酒精度</td><td>{abv_display}</td></tr>
<tr><td>產品類別</td><td><span class="badge-cat">{cat_type or meta['zh']}</span></td></tr>
<tr><td>來源</td><td>{p.get('source','—')}</td></tr>
"""

    rel_cards = ""
    for rp in related[:3]:
        rel_cards += f"""
<a href="../product/{rp['_slug']}.html" class="prod-card">
  {product_img_html(rp['_cat'])}
  <div class="prod-card-body">
    {source_badge(rp, small=True)}
    <h4>{rp.get('name_zh','')}</h4>
    <div class="en-name">{rp.get('name_en','')}</div>
    <div class="prod-card-meta">
      <span class="spec">{rp.get('spec','')}</span>
      <span class="abv">{abv_str(rp)}</span>
    </div>
  </div>
</a>"""

    wa_msg = f"您好，我想查詢 {p.get('name_zh','')} ({p.get('spec','')}) 的箱價及庫存，謝謝。"
    import urllib.parse
    wa_url = f"{WA_LINK}?text={urllib.parse.quote(wa_msg)}"

    body = f"""
<div class="breadcrumb">
  <div class="breadcrumb-inner">
    <a href="../index.html">首頁</a>
    <span class="sep">›</span>
    <a href="../category/{cat_key}.html">{meta['zh']}</a>
    <span class="sep">›</span>
    <span>{p.get('name_zh','')}</span>
  </div>
</div>

<div class="product-detail">
  {product_img_html(cat_key, size='detail')}
  <div class="product-info">
    {source_badge(p)}
    <span class="badge-cat">{meta['zh']}</span>
    <div class="divider"></div>
    <h1>{p.get('name_zh','')}</h1>
    <div class="en-name">{p.get('name_en','')}</div>
    <div class="divider"></div>
    <table class="spec-table">
      {spec_rows}
    </table>
    <a href="{wa_url}" class="wa-btn" target="_blank">
      <svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
      WhatsApp 查詢箱價
    </a>
    <div style="margin-top:14px;font-size:.75rem;color:#bbb;">歡迎餐廳、酒吧、超市、便利店等 B2B 客戶查詢批發報價</div>
  </div>
</div>

<div class="related-section" {'style="display:none;"' if not rel_cards else ''}>
  <div class="related-inner">
    <h2>相關產品</h2>
    <div class="product-grid">{rel_cards}</div>
  </div>
</div>
"""
    return page_wrap(p.get('name_zh','產品'), body, depth=1)

# ──────────────────────────────────────────────
# About Page
# ──────────────────────────────────────────────
def build_about():
    body = f"""
<div class="about-hero">
  <div class="eyebrow">About Us</div>
  <h1>關於<span>明德行</span></h1>
  <p>澳門本地專業洋酒飲品批發代理，深耕市場逾廿年</p>
</div>
<div class="about-body">
  <div class="stat-grid">
    <div class="stat-box"><div class="num">1998</div><div class="label">年成立</div></div>
    <div class="stat-box"><div class="num">25+</div><div class="label">年行業經驗</div></div>
    <div class="stat-box"><div class="num">500+</div><div class="label">款產品</div></div>
  </div>

  <h2>公司簡介</h2>
  <p>明德行國際有限公司（Meng Tak Hong International Co., Ltd.）於1998年在澳門成立，是澳門本地歷史最悠久的洋酒及飲品批發代理商之一。</p>
  <p>多年來，我們致力為澳門各類餐飲及零售業客戶提供穩定、優質的產品供應，建立了廣泛的合作網絡及良好的市場口碑。</p>

  <h2>主要業務</h2>
  <ul>
    <li>蘇格蘭、愛爾蘭、美國、日本單一麥芽及調和威士忌代理</li>
    <li>法國干邑（軒尼斯、馬爹利、人頭馬等）及拔蘭地進口</li>
    <li>優質葡萄酒及香檳（法國、澳洲、葡萄牙、智利等）</li>
    <li>日本清酒、燒酎、日本威士忌</li>
    <li>韓國燒酒（真露、舞鶴等）及亞洲飲品食品</li>
    <li>琴酒、伏特加、冧酒、龍舌蘭及各式力嬌酒</li>
    <li>中國白酒（茅台、習酒等）</li>
    <li>各式啤酒及非酒精飲料</li>
  </ul>

  <h2>客戶群體</h2>
  <p>我們主要服務 B2B 批發客戶，包括：</p>
  <ul>
    <li>酒店、度假村及高級餐廳</li>
    <li>酒吧、夜店及娛樂場所</li>
    <li>超市、便利店及士多</li>
    <li>企業及活動採購</li>
    <li>私人買酒用家</li>
  </ul>

  <h2>聯絡我們</h2>
  <p>如需查詢箱價、最新優惠或有任何採購需要，歡迎致電或透過 WhatsApp 聯絡我們的銷售團隊。</p>
  <div style="margin-top:24px;display:flex;gap:12px;flex-wrap:wrap;">
    <a href="{WA_LINK}" class="social-btn wa" target="_blank" style="padding:10px 22px;border-radius:8px;">WhatsApp 查詢</a>
    <a href="contact.html" style="display:inline-block;padding:10px 22px;border-radius:8px;background:var(--gold);color:var(--navy);font-weight:700;font-size:.85rem;">聯絡頁面</a>
  </div>
</div>
"""
    return page_wrap("關於我們", body, depth=0)

# ──────────────────────────────────────────────
# Contact Page
# ──────────────────────────────────────────────
def build_contact():
    body = f"""
<div class="about-hero">
  <div class="eyebrow">Contact Us</div>
  <h1 style="font-size:2.3rem;">聯絡<span>我們</span></h1>
  <p>歡迎 B2B 客戶查詢批發報價及補貨事宜</p>
</div>

<div class="contact-grid">
  <div class="contact-info">
    <h2>聯絡資料</h2>
    <div class="sub">Meng Tak Hong International Co., Ltd.</div>

    <div class="contact-row">
      <div class="icon">📍</div>
      <div class="detail">
        <div class="label">地址</div>
        <div class="val">澳門黑沙環慕拉士大馬路195號<br>南嶺工業大廈4樓F座</div>
      </div>
    </div>
    <div class="contact-row">
      <div class="icon">📞</div>
      <div class="detail">
        <div class="label">電話</div>
        <div class="val"><a href="tel:+85328415128">+853 2841 5128</a> / <a href="tel:+85328584838">+853 2858 4838</a></div>
      </div>
    </div>
    <div class="contact-row">
      <div class="icon">✉️</div>
      <div class="detail">
        <div class="label">電郵</div>
        <div class="val"><a href="mailto:info@mengtakhong.com">info@mengtakhong.com</a></div>
      </div>
    </div>
    <div class="contact-row">
      <div class="icon">🕐</div>
      <div class="detail">
        <div class="label">辦公時間</div>
        <div class="val">週一至週六 9:00 – 18:00</div>
      </div>
    </div>

    <div class="social-row" style="margin-top:32px;">
      <a href="{WA_LINK}" class="social-btn wa" target="_blank">
        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        WhatsApp
      </a>
      <a href="{FB_LINK}" class="social-btn fb" target="_blank">Facebook</a>
      <a href="{IG_LINK}" class="social-btn ig" target="_blank">Instagram</a>
    </div>
  </div>

  <div>
    <div class="map-wrap">
      <iframe
        src="https://maps.google.com/maps?q=%E6%BE%B3%E9%96%80%E9%BB%91%E6%B2%99%E7%92%B0%E6%85%95%E6%8B%89%E5%A3%AB%E5%A4%A7%E9%A6%AC%E8%B7%AF195%E8%99%9F%E5%8D%97%E5%B6%BA%E5%B7%A5%E6%A5%AD%E5%A4%A7%E5%BB%88&output=embed&z=16"
        allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade"
        title="明德行地址">
      </iframe>
    </div>
    <div style="margin-top:20px;background:var(--cream);border:1px solid var(--border);border-radius:10px;padding:20px 22px;font-size:.82rem;color:var(--text);line-height:1.8;">
      <strong style="color:var(--navy);">B2B 批發查詢</strong><br>
      餐廳、酒吧、超市、便利店、酒店等業務客戶歡迎致電或 WhatsApp 查詢最新箱價及優惠。<br><br>
      <strong style="color:var(--navy);">訂單及補貨</strong><br>
      如需定期補貨安排或大批量採購，請直接聯絡我們的銷售團隊商討。
    </div>
  </div>
</div>
"""
    return page_wrap("聯絡我們", body, depth=0)

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    print("🚀 明德行網站生成器啟動...")

    # Create directories
    for d in [ASSETS_DIR, IMAGES_DIR, CSS_DIR, JS_DIR, CAT_DIR, PROD_PAGE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    print("✅ 資料夾建立完成")

    # Copy logo
    src_logo = BASE_DIR / "LOGO.jpg"
    dst_logo = IMAGES_DIR / "LOGO.jpg"
    if src_logo.exists():
        shutil.copy2(src_logo, dst_logo)
        print(f"✅ Logo 複製完成: {dst_logo}")
    else:
        print(f"⚠️  Logo 不存在: {src_logo}，網站會顯示文字代替")

    # Write CSS
    with open(CSS_DIR / "style.css", "w", encoding="utf-8") as f:
        f.write(CSS)
    print("✅ CSS 生成完成")

    # Write JS
    with open(JS_DIR / "main.js", "w", encoding="utf-8") as f:
        f.write(JS_SEARCH)
    print("✅ JS 生成完成")

    # Load products
    all_products = load_products()
    total_products = sum(len(v) for v in all_products.values())
    print(f"✅ 產品資料載入完成，共 {total_products} 款產品")

    page_count = 0

    # Homepage
    with open(BASE_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(build_homepage(all_products))
    page_count += 1
    print("✅ 首頁生成完成")

    # About
    with open(BASE_DIR / "about.html", "w", encoding="utf-8") as f:
        f.write(build_about())
    page_count += 1

    # Contact
    with open(BASE_DIR / "contact.html", "w", encoding="utf-8") as f:
        f.write(build_contact())
    page_count += 1
    print("✅ 關於/聯絡頁面生成完成")

    # Category pages
    for cat_key, products in all_products.items():
        fp = CAT_DIR / f"{cat_key}.html"
        with open(fp, "w", encoding="utf-8") as f:
            f.write(build_category_page(cat_key, products))
        page_count += 1
    print(f"✅ 8 個分類頁面生成完成")

    # Product pages
    prod_page_count = 0
    for cat_key, products in all_products.items():
        for i, p in enumerate(products):
            # Related: same category, exclude self, take up to 3
            related = [rp for rp in products if rp is not p][:3]
            fp = PROD_PAGE_DIR / f"{p['_slug']}.html"
            with open(fp, "w", encoding="utf-8") as f:
                f.write(build_product_page(p, related))
            prod_page_count += 1
        print(f"  ↳ {CATEGORIES[cat_key]['zh']}: {len(products)} 個產品頁面")

    page_count += prod_page_count
    print(f"✅ {prod_page_count} 個產品獨立頁面生成完成")

    # Summary
    print("\n" + "="*55)
    print("🎉 網站生成完成！")
    print("="*55)
    print(f"📄 總頁面數：{page_count}")
    print(f"   - 首頁：1")
    print(f"   - 關於我們：1")
    print(f"   - 聯絡我們：1")
    print(f"   - 分類頁面：8")
    print(f"   - 產品獨立頁面：{prod_page_count}")
    print(f"\n📁 資料夾結構：")
    print(f"   {BASE_DIR}/")
    print(f"   ├── index.html")
    print(f"   ├── about.html")
    print(f"   ├── contact.html")
    print(f"   ├── assets/")
    print(f"   │   ├── css/style.css")
    print(f"   │   ├── js/main.js")
    print(f"   │   └── images/LOGO.jpg")
    print(f"   ├── category/  ({len(all_products)} 個檔案)")
    print(f"   └── product/   ({prod_page_count} 個檔案)")
    print(f"\n🌐 用瀏覽器開啟：file:///{BASE_DIR}/index.html")

if __name__ == "__main__":
    main()
