#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
明德行 產品圖片搜尋、下載、處理及HTML更新腳本
支援斷點續傳 — 進度儲存於 progress.json
"""

import sys, os, json, re, time, shutil, io, hashlib, urllib.parse, subprocess
from pathlib import Path

# ── 安裝缺少的依賴 ──
def ensure_pkg(pkg, import_name=None):
    import_name = import_name or pkg
    try:
        __import__(import_name)
    except ImportError:
        print(f"[SETUP] 安裝 {pkg} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

ensure_pkg("Pillow", "PIL")
ensure_pkg("requests")
ensure_pkg("ddgs", "ddgs")
ensure_pkg("pymupdf", "fitz")

import warnings
warnings.filterwarnings("ignore")

# Fix Windows console encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import requests
from PIL import Image
import fitz  # PyMuPDF
DDG_OK = False
try:
    from ddgs import DDGS
    DDG_OK = True
except Exception:
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from duckduckgo_search import DDGS
        DDG_OK = True
    except Exception:
        pass

# ── Paths ──
BASE_DIR     = Path(r"C:\Users\user\Desktop\mengtakhong-website")
PROD_DIR     = BASE_DIR / "products"
IMG_OUT_DIR  = BASE_DIR / "assets" / "images" / "products"
PROGRESS_FILE = BASE_DIR / "progress.json"
MISSING_FILE  = BASE_DIR / "missing_images.txt"
HTML_CAT_DIR  = BASE_DIR / "category"
HTML_PROD_DIR = BASE_DIR / "product"

IMG_OUT_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = ["whisky","cognac","japan","korea","wine","spirits","chinese","beer"]

PDF_MAP = {
    "whisky":  ["【代理正貨】威士忌報價.pdf",      "【進口】威士忌.pdf"],
    "cognac":  ["【代理正貨】拔蘭地干邑.pdf",       "【進口】拔蘭地干邑.pdf"],
    "japan":   ["【代理正貨】日本產品.pdf",          "【進口】日本產品.pdf"],
    "korea":   ["【代理正貨】韓國_台灣_泰國_澳洲_越南.pdf"],
    "wine":    ["【代理正貨】葡萄酒_香檳.pdf",       "【進口】葡萄酒_香檳.pdf"],
    "spirits": ["【代理正貨】烈酒力嬌.pdf",          "【進口】烈酒力嬌_酒辦.pdf"],
    "chinese": ["中國酒報價_Chinese_Spirits.pdf"],
    "beer":    ["【進口】汽水啤酒.pdf"],
}

CAT_ZH = {"whisky":"威士忌","cognac":"干邑/拔蘭地","japan":"日本產品",
           "korea":"韓國/亞洲飲品","wine":"葡萄酒/香檳","spirits":"烈酒/力嬌酒",
           "chinese":"中國白酒","beer":"啤酒/飲料"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
}

# ── Progress ──
def load_progress():
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "found": {},       # slug -> image_path (relative)
        "missing": [],     # slugs we gave up on
        "pdf_extracted": {},  # cat -> list of extracted image paths
        "html_updated_cat": [],   # category page slugs updated
        "html_updated_prod": [],  # product page slugs updated
        "step": "search",  # "search" | "process" | "html_update" | "done"
        "last_processed": None,
        "stats": {"searched": 0, "downloaded": 0, "failed": 0, "html_cat": 0, "html_prod": 0}
    }

def save_progress(prog):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)

# ── Load all products ──
def load_all_products():
    products = []
    slug_seen = {}
    for cat in CATEGORIES:
        fp = PROD_DIR / f"{cat}.json"
        if not fp.exists():
            continue
        with open(fp, "r", encoding="utf-8") as f:
            items = json.load(f)
        for i, p in enumerate(items):
            p["_cat"] = cat
            # Generate slug exactly as build_website.py does
            base = slugify(p.get("name_en", f"product-{i}")) or f"{cat}-{i}"
            slug = f"{cat}-{base}"
            if slug in slug_seen:
                slug_seen[slug] += 1
                slug = f"{slug}-{slug_seen[slug]}"
            else:
                slug_seen[slug] = 0
            p["_slug"] = slug
        products.extend(items)
    return products

def slugify(text):
    text = str(text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")[:80]

def get_slug(p):
    return p.get("_slug") or p.get("slug") or ""

# ── Image download ──
def download_image(url, dest_path, timeout=15):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type",""):
            data = r.content
            if len(data) < 3000:  # too small = likely placeholder
                return False
            # validate it's actually an image
            try:
                img = Image.open(io.BytesIO(data))
                img.verify()
            except Exception:
                return False
            with open(dest_path, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        pass
    return False

# ── DuckDuckGo image search ──
def ddg_search_image(query, dest_path, max_tries=5):
    if not DDG_OK:
        return False
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=max_tries, safesearch="off"))
        for r in results:
            url = r.get("image","")
            if not url:
                continue
            if download_image(url, dest_path):
                return True
            time.sleep(0.3)
    except Exception as e:
        pass
    return False

# ── Search with multiple queries ──
def find_image_online(p, dest_path):
    name_en = p.get("name_en","")
    name_zh = p.get("name_zh","")
    cat = p.get("_cat","")

    queries = []
    if name_en:
        queries.append(f"{name_en} bottle product image transparent")
        queries.append(f"{name_en} bottle whisky spirits")
    if name_zh:
        queries.append(f"{name_zh} 產品圖片")
        queries.append(f"{name_zh} 瓶裝")

    for q in queries:
        print(f"  [DDG] {q[:55]}...")
        if ddg_search_image(q, dest_path):
            return True
        time.sleep(1.2)
    return False

# ── PDF image extraction ──
_pdf_images_cache = {}  # cat -> list of (image_bytes, page_num, img_idx)

def extract_pdf_images(cat):
    if cat in _pdf_images_cache:
        return _pdf_images_cache[cat]
    imgs = []
    for pdf_name in PDF_MAP.get(cat, []):
        pdf_path = PROD_DIR / pdf_name
        if not pdf_path.exists():
            continue
        try:
            doc = fitz.open(str(pdf_path))
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                for img_idx, img_info in enumerate(image_list):
                    xref = img_info[0]
                    try:
                        base_image = doc.extract_image(xref)
                        img_bytes = base_image["image"]
                        w = base_image.get("width", 0)
                        h = base_image.get("height", 0)
                        # Skip tiny images (icons, borders)
                        if w >= 80 and h >= 80:
                            imgs.append({
                                "bytes": img_bytes,
                                "ext":   base_image.get("ext","png"),
                                "w": w, "h": h,
                                "page": page_num,
                            })
                    except Exception:
                        pass
            doc.close()
        except Exception as e:
            print(f"  [PDF] 讀取失敗 {pdf_name}: {e}")
    _pdf_images_cache[cat] = imgs
    return imgs

def save_pdf_image(img_info, dest_path):
    try:
        data = img_info["bytes"]
        img = Image.open(io.BytesIO(data))
        img.verify()
        with open(dest_path, "wb") as f:
            f.write(data)
        return True
    except Exception:
        return False

# ── Process image (600x600 white bg) ──
def process_image(src_path, out_path=None):
    if out_path is None:
        out_path = src_path
    try:
        img = Image.open(str(src_path)).convert("RGBA")
        # Remove white/near-white background if PNG with alpha
        canvas = Image.new("RGB", (600, 600), (255, 255, 255))
        # Resize to fit 500x500
        img_rgb = Image.new("RGB", img.size, (255,255,255))
        if img.mode == "RGBA":
            img_rgb.paste(img, mask=img.split()[3])
        else:
            img_rgb = img.convert("RGB")
        img_rgb.thumbnail((500, 500), Image.LANCZOS)
        # Center on canvas
        x = (600 - img_rgb.width) // 2
        y = (600 - img_rgb.height) // 2
        canvas.paste(img_rgb, (x, y))
        canvas.save(str(out_path), "JPEG", quality=90)
        return True
    except Exception as e:
        print(f"  [PIL] 處理失敗 {src_path.name}: {e}")
        return False

# ── HTML update helpers ──
CAT_EMOJI = {"whisky":"🥃","cognac":"🍷","japan":"🗾","korea":"🇰🇷",
             "wine":"🍾","spirits":"🍸","chinese":"🏮","beer":"🍺"}
CAT_BG    = {"whisky":"#F5E6C8","cognac":"#F5D5C8","japan":"#FDEAEA","korea":"#D6EAF8",
             "wine":"#F4ECF7","spirits":"#D6E4F0","chinese":"#FADBD8","beer":"#FEF9E7"}

def update_product_page(slug, cat):
    fp = HTML_PROD_DIR / f"{slug}.html"
    if not fp.exists():
        return False
    try:
        html = fp.read_text(encoding="utf-8")
        emoji = CAT_EMOJI.get(cat,"🍶")
        bg    = CAT_BG.get(cat,"#F5F0E8")
        # Replace the detail img div
        old_pat = re.compile(
            r'<div class="product-detail-img"[^>]*>.*?</div>',
            re.DOTALL
        )
        new_div = (
            f'<div class="product-detail-img" style="background:#fff;padding:0;overflow:hidden;">'
            f'<img src="../assets/images/products/{slug}.jpg" '
            f'alt="" style="width:100%;height:100%;object-fit:contain;" '
            f'onerror="this.parentElement.style.background=\'{bg}\';'
            f'this.parentElement.style.fontSize=\'7rem\';'
            f'this.parentElement.innerHTML=\'{emoji}\'">'
            f'</div>'
        )
        new_html, n = old_pat.subn(new_div, html, count=1)
        if n > 0:
            fp.write_text(new_html, encoding="utf-8")
            return True
    except Exception as e:
        print(f"  [HTML] product/{slug}.html 更新失敗: {e}")
    return False

def update_category_page(cat, found_slugs):
    fp = HTML_CAT_DIR / f"{cat}.html"
    if not fp.exists():
        return 0
    try:
        html = fp.read_text(encoding="utf-8")
        count = 0
        emoji = CAT_EMOJI.get(cat,"🍶")
        bg    = CAT_BG.get(cat,"#F5F0E8")

        # Pattern: find each card anchor + its img div
        # <a href="../product/SLUG.html" class="prod-card" ...>
        #   <div class="prod-card-img" ...>EMOJI</div>
        card_pat = re.compile(
            r'(<a href="\.\./product/([^"]+)\.html" class="prod-card"[^>]*>)\s*'
            r'(<div class="prod-card-img"[^>]*>.*?</div>)',
            re.DOTALL
        )
        def replace_card(m):
            nonlocal count
            anchor_open = m.group(1)
            slug        = m.group(2)
            if slug in found_slugs:
                new_img_div = (
                    f'<div class="prod-card-img" style="background:#fff;padding:8px;overflow:hidden;">'
                    f'<img src="../assets/images/products/{slug}.jpg" '
                    f'alt="" style="width:100%;height:100%;object-fit:contain;" '
                    f'onerror="this.parentElement.style.background=\'{bg}\';'
                    f'this.parentElement.style.fontSize=\'2.8rem\';'
                    f'this.parentElement.style.padding=\'0\';'
                    f'this.parentElement.innerHTML=\'{emoji}\'">'
                    f'</div>'
                )
                count += 1
                return anchor_open + "\n" + new_img_div
            return m.group(0)

        new_html = card_pat.sub(replace_card, html)
        fp.write_text(new_html, encoding="utf-8")
        return count
    except Exception as e:
        print(f"  [HTML] category/{cat}.html 更新失敗: {e}")
    return 0

# ── STEP 1: Search & Download ──
def step_search(products, prog):
    print("\n" + "="*60)
    print("STEP 1: 搜尋及下載產品圖片")
    print("="*60)

    found   = prog["found"]
    missing = set(prog["missing"])
    stats   = prog["stats"]

    todo = [p for p in products
            if get_slug(p) not in found and get_slug(p) not in missing]

    print(f"待搜尋: {len(todo)} | 已完成: {len(found)} | 跳過: {len(missing)}")

    batch_size = 10
    for i, p in enumerate(todo):
        slug = get_slug(p)
        if not slug:
            continue
        dest = IMG_OUT_DIR / f"{slug}.jpg"
        cat  = p.get("_cat","")

        print(f"\n[{stats['searched']+1}/{len(todo)+stats['searched']}] {p.get('name_zh','')} | {p.get('name_en','')[:40]}")

        # Try online search
        found_online = find_image_online(p, dest)

        if not found_online:
            # Try PDF extraction: use first suitable image from category PDF
            print(f"  [PDF] 嘗試從 PDF 提取...")
            pdf_imgs = extract_pdf_images(cat)
            if pdf_imgs:
                # Pick the most "portrait" image (like a bottle)
                best = sorted(pdf_imgs, key=lambda x: abs(x["h"]/max(x["w"],1) - 2.0))
                # Use index based on product position within category
                cat_products_in_todo = [pp for pp in products if pp.get("_cat") == cat]
                idx = cat_products_in_todo.index(p) % len(best) if len(best) > 0 else 0
                chosen = best[idx % len(best)]
                tmp = IMG_OUT_DIR / f"_tmp_{slug}.{chosen['ext']}"
                if save_pdf_image(chosen, tmp):
                    shutil.move(str(tmp), str(dest))
                    found_online = True
                    print(f"  [PDF] OK — 從PDF提取 {chosen['w']}x{chosen['h']}")
                else:
                    tmp.unlink(missing_ok=True)

        if found_online and dest.exists():
            found[slug] = str(dest.relative_to(BASE_DIR))
            stats["downloaded"] += 1
            print(f"  --> 已儲存: {dest.name}")
        else:
            missing.add(slug)
            stats["failed"] += 1
            print(f"  --> 未找到圖片")

        stats["searched"] += 1
        prog["missing"] = list(missing)
        prog["last_processed"] = slug

        # Save progress every batch_size
        if (i + 1) % batch_size == 0:
            save_progress(prog)
            pct = round((len(found) + len(missing)) / len(products) * 100, 1)
            prog["total_pct"] = pct
            print(f"\n--- 進度: {pct}% | 已搜尋: {stats['searched']} | 找到: {stats['downloaded']} | 失敗: {stats['failed']} ---\n")

        time.sleep(0.8)  # polite delay

    prog["missing"] = list(missing)
    save_progress(prog)
    print(f"\n搜尋完成: 找到 {stats['downloaded']} / {len(products)} 張圖片")
    return prog

# ── STEP 2: Process images ──
def step_process(prog):
    print("\n" + "="*60)
    print("STEP 2: 統一圖片大小 (600x600 白底)")
    print("="*60)

    found = prog["found"]
    processed = prog.get("processed", [])
    processed_set = set(processed)

    to_process = [(slug, path) for slug, path in found.items()
                  if slug not in processed_set]
    print(f"待處理: {len(to_process)} 張 | 已處理: {len(processed_set)} 張")

    ok = 0
    for i, (slug, rel_path) in enumerate(to_process):
        src = BASE_DIR / rel_path
        if not src.exists():
            continue
        if process_image(src):
            processed_set.add(slug)
            ok += 1
            if (i + 1) % 20 == 0:
                prog["processed"] = list(processed_set)
                save_progress(prog)
                print(f"  進度: {i+1}/{len(to_process)} 已處理")
        else:
            print(f"  跳過: {slug}")

    prog["processed"] = list(processed_set)
    save_progress(prog)
    print(f"圖片處理完成: {ok}/{len(to_process)} 張成功")
    return prog

# ── STEP 3: Update HTML ──
def step_html_update(products, prog):
    print("\n" + "="*60)
    print("STEP 3: 更新 HTML 檔案")
    print("="*60)

    found  = prog["found"]
    found_slugs = set(found.keys())

    updated_prod = prog.get("html_updated_prod", [])
    updated_prod_set = set(updated_prod)

    # Update product detail pages
    print("更新產品獨立頁面...")
    prod_count = 0
    for p in products:
        slug = get_slug(p)
        if not slug or slug in updated_prod_set:
            continue
        if slug not in found_slugs:
            continue
        cat = p.get("_cat","")
        if update_product_page(slug, cat):
            updated_prod_set.add(slug)
            prod_count += 1
        if prod_count % 50 == 0 and prod_count > 0:
            prog["html_updated_prod"] = list(updated_prod_set)
            save_progress(prog)
            print(f"  產品頁: {prod_count} 已更新")

    prog["html_updated_prod"] = list(updated_prod_set)
    save_progress(prog)
    print(f"產品頁更新完成: {prod_count} 個")

    # Update category pages
    print("更新分類頁面...")
    cat_total = 0
    for cat in CATEGORIES:
        n = update_category_page(cat, found_slugs)
        cat_total += n
        print(f"  {CAT_ZH[cat]}: {n} 個卡片更新")
        prog["stats"]["html_cat"] += n

    prog["stats"]["html_prod"] = prod_count
    save_progress(prog)
    print(f"分類頁更新完成: {cat_total} 個卡片")
    return prog

# ── Write missing report ──
def write_missing_report(products, prog):
    missing_set = set(prog["missing"])
    found_set   = set(prog["found"].keys())
    lines = ["# 未能找到圖片的產品\n",
             f"# 共 {len(missing_set)} 款\n",
             f"# 生成時間: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"]
    for p in products:
        slug = get_slug(p)
        if slug in missing_set and slug not in found_set:
            lines.append(f"{slug}\n")
            lines.append(f"  名稱: {p.get('name_zh','')} / {p.get('name_en','')}\n")
            lines.append(f"  分類: {p.get('_cat','')}\n\n")
    with open(MISSING_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"\n未找到圖片清單: {MISSING_FILE}")

# ── Final report ──
def print_report(products, prog):
    s = prog["stats"]
    found   = len(prog["found"])
    missing = len(prog["missing"])
    total   = len(products)
    print("\n" + "="*60)
    print("完成報告")
    print("="*60)
    print(f"  總產品數:       {total}")
    print(f"  找到圖片:       {found} ({round(found/total*100,1)}%)")
    print(f"  未找到圖片:     {missing}")
    print(f"  處理圖片數:     {len(prog.get('processed',[]))}")
    print(f"  更新產品頁面:   {s.get('html_prod',0)}")
    print(f"  更新分類卡片:   {s.get('html_cat',0)}")
    print(f"\n  進度檔案: {PROGRESS_FILE}")
    print(f"  缺圖清單: {MISSING_FILE}")

# ── MAIN ──
def main():
    print("=" * 60)
    print("明德行 產品圖片搜尋及網站更新工具")
    print("=" * 60)

    if not DDG_OK:
        print("[警告] duckduckgo_search 未能載入，將只從PDF提取圖片")

    products = load_all_products()
    print(f"載入產品: {len(products)} 款")

    prog = load_progress()

    step = prog.get("step","search")
    if prog.get("last_processed"):
        print(f"[續傳] 從上次位置繼續 | 已完成: {len(prog['found'])} 張 | 步驟: {step}")

    # STEP 1
    if step in ("search",):
        prog = step_search(products, prog)
        prog["step"] = "process"
        save_progress(prog)

    # STEP 2
    if step in ("search","process"):
        prog = step_process(prog)
        prog["step"] = "html_update"
        save_progress(prog)

    # STEP 3
    if step in ("search","process","html_update"):
        prog = step_html_update(products, prog)
        prog["step"] = "done"
        save_progress(prog)

    # Report
    write_missing_report(products, prog)
    print_report(products, prog)
    print("\n全部完成！用瀏覽器重新整理頁面即可看到產品圖片。")

if __name__ == "__main__":
    main()
