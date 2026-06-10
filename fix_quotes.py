#!/usr/bin/env python3
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(r"C:\Users\user\Desktop\mengtakhong-website")

# Single quotes inside JS string break it - need to escape them as \'
BAD  = """onerror="this.parentElement.style.fontSize='2rem';this.parentElement.innerHTML='&#127870;'">"""
GOOD = r"""onerror="this.parentElement.style.fontSize=\'2rem\';this.parentElement.innerHTML=\'&#127870;\'">"""

fixed = 0
files = list((BASE / "product").glob("*.html")) + [BASE / "index.html"]
for fp in files:
    try:
        txt = fp.read_text(encoding="utf-8")
        if BAD in txt:
            fp.write_text(txt.replace(BAD, GOOD), encoding="utf-8")
            fixed += 1
    except Exception as e:
        print(f"Error {fp.name}: {e}")

print(f"Fixed {fixed}/{len(files)} files")

# Verify
sample = (BASE / "product" / "whisky-glen-moray-classic-single-malt.html").read_text(encoding="utf-8")
idx = sample.find("carousel-card-img")
print("Sample:", sample[idx:idx+200])
