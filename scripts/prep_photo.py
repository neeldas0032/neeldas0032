#!/usr/bin/env python3
"""OPTIONAL — prep a headshot so it converts to clean ASCII.

Run once per photo, locally (needs the heavy libs in requirements.txt):
    python scripts/prep_photo.py my-headshot.jpg

Pipeline:
  1. remove the background (rembg) so only you remain
  2. boost local contrast (CLAHE) — a flat, evenly-lit face otherwise
     collapses to a dark blob in ASCII
  3. composite onto pure white so the background maps to blank space
Writes data/source-prepped.png (grayscale), consumed by make_ascii_svg.py.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "source-prepped.png"


def main(src):
    img = Image.open(src).convert("RGBA")
    cut = remove(img)  # transparent background

    rgba = np.array(cut)
    alpha = rgba[:, :, 3]

    gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # composite subject onto white (alpha 0 -> white -> blank glyph)
    white = np.full_like(gray, 255)
    a = alpha.astype(np.float32) / 255.0
    out = (gray.astype(np.float32) * a + white.astype(np.float32) * (1 - a)).astype(np.uint8)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out).save(OUT)
    print(f"Wrote {OUT} ({out.shape[1]}x{out.shape[0]}) — now run make_ascii_svg.py")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python scripts/prep_photo.py <photo.jpg>")
        sys.exit(1)
    main(sys.argv[1])
