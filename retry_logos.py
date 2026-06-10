#!/usr/bin/env python3
import sys, urllib.request, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BRANDS_DIR = Path(r"C:\Users\user\Desktop\mengtakhong-website\assets\images\brands")

DIRECT = [
    ("lotte.png",         "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Lotte_logo.svg/320px-Lotte_logo.svg.png"),
    ("ottogi.png",        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Ottogi_logo.svg/320px-Ottogi_logo.svg.png"),
    ("hite.png",          "https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/Hite_Brewery_logo.svg/320px-Hite_Brewery_logo.svg.png"),
    ("balblair.png",      "https://images.vivino.com/thumbs/8GyfX03bHLKAlRoRRsVXpA_pb_x300.png"),
    ("king_arthur.png",   "https://www.cognac-expert.com/img/marques/king-arthur-xv-cognac.png"),
    ("hamafukutsuru.png", "https://www.hakutsuru-sake.com/wp-content/uploads/2020/09/logo.png"),
    ("kobe_winery.png",   "https://www.kobewinery.or.jp/images/logo.png"),
    ("vidigal_brutalis.png","https://vidigalwines.com/wp-content/uploads/2021/06/logo-vidigal-wines-gold.png"),
]

DDGS_QUERIES = {
    "lotte.png":          "Lotte Group logo PNG",
    "ottogi.png":         "Ottogi Korean food logo PNG",
    "hite.png":           "Hite beer Korea logo PNG",
    "balblair.png":       "Balblair whisky Highland logo PNG",
    "king_arthur.png":    "King Arthur XV XO brandy logo",
    "hamafukutsuru.png":  "Hamafukutsuru sake logo PNG Japan",
    "kobe_winery.png":    "Kobe winery Japan wine logo PNG",
    "vidigal_brutalis.png":"Vidigal wines Portugal logo PNG",
}

def dl(url, dest):
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 Chrome/120"})
        with urllib.request.urlopen(req, timeout=12) as r:
            data = r.read()
        if len(data) < 600:
            return False
        dest.write_bytes(data)
        return True
    except:
        return False

try:
    from ddgs import DDGS
    ddgs_ok = True
    print("ddgs available")
except:
    ddgs_ok = False

results = {}
for fn, url in DIRECT:
    dst = BRANDS_DIR / fn
    if dst.exists() and dst.stat().st_size > 600:
        print(f"[SKIP] {fn}")
        results[fn] = True
        continue

    if dl(url, dst):
        print(f"[OK-Direct] {fn}")
        results[fn] = True
    elif ddgs_ok:
        try:
            with DDGS() as ddgs:
                imgs = list(ddgs.images(DDGS_QUERIES.get(fn, fn), max_results=5))
            for r in imgs:
                u = r.get("image", "")
                if u and dl(u, dst):
                    print(f"[OK-DDGS] {fn} <- {u[:60]}")
                    results[fn] = True
                    break
            time.sleep(0.6)
        except Exception as e:
            print(f"[DDGS err] {fn}: {e}")

    if fn not in results:
        print(f"[FAIL] {fn}")
        results[fn] = False

ok = sum(1 for v in results.values() if v)
fails = [fn for fn, v in results.items() if not v]
print(f"\n{ok}/{len(results)} downloaded")
if fails:
    print(f"Still failed: {fails}")
