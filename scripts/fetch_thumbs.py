#!/usr/bin/env python3
"""
fetch_thumbs.py — fetch an OpenGraph preview image from a page URL.

Given a page URL, this script downloads the page, parses out the
`og:image` (or `twitter:image`) meta tag, fetches that image, normalises
it to 800x450 (16:9 centre-crop), and saves it as a JPEG.

Usage:

    python scripts/fetch_thumbs.py <url> <name>

    # examples:
    python scripts/fetch_thumbs.py https://pubmed.ncbi.nlm.nih.gov/39626222/ cure-19-trial
    python scripts/fetch_thumbs.py https://www.jacc.org/doi/10.1016/X cure-19-trial --out-dir /tmp

By default the image is saved as <name>.jpg under assets/images/thumbs/
relative to the website root. After running, add the resulting path to
the relevant biblio entry's frontmatter, e.g.:

    thumbnail: /assets/images/thumbs/<name>.jpg

Dependencies: requests, beautifulsoup4, pillow
    pip install requests beautifulsoup4 pillow
"""

import argparse
import io
import sys
import urllib.parse
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    from PIL import Image
except ImportError as e:
    sys.exit(
        f"Missing dependency: {e.name}.\n"
        "Install with: pip install requests beautifulsoup4 pillow"
    )


HERE = Path(__file__).resolve().parent
DEFAULT_OUT_DIR = HERE.parent / "assets" / "images" / "thumbs"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 20  # seconds
TARGET_W, TARGET_H = 800, 450  # 16:9


def fetch_html(url):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
    }
    r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
    r.raise_for_status()
    return r.text, r.url


def find_og_image(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    for prop in ("og:image", "og:image:url", "og:image:secure_url",
                 "twitter:image", "twitter:image:src"):
        tag = (
            soup.find("meta", attrs={"property": prop})
            or soup.find("meta", attrs={"name": prop})
        )
        if tag and tag.get("content"):
            return urllib.parse.urljoin(base_url, tag["content"].strip())
    return None


def fetch_image(url):
    headers = {"User-Agent": USER_AGENT, "Accept": "image/*,*/*;q=0.8"}
    r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
    r.raise_for_status()
    return r.content


def normalise_image(raw, target_w, target_h):
    """Centre-crop to target aspect ratio, then resize. Returns (bytes, src_size)."""
    img = Image.open(io.BytesIO(raw))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(round(src_h * target_ratio))
        offset = (src_w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, src_h))
    elif src_ratio < target_ratio:
        new_h = int(round(src_w / target_ratio))
        offset = (src_h - new_h) // 2
        img = img.crop((0, offset, src_w, offset + new_h))
    img = img.resize((target_w, target_h), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=82, optimize=True)
    return out.getvalue(), (src_w, src_h)


def main():
    ap = argparse.ArgumentParser(
        description="Fetch an og:image preview from a page URL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("url", help="Page URL to fetch og:image from")
    ap.add_argument("name", help="Output filename (without extension)")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR),
                    help=f"Output directory (default: {DEFAULT_OUT_DIR})")
    ap.add_argument("--width", type=int, default=TARGET_W,
                    help=f"Target width in pixels (default: {TARGET_W})")
    ap.add_argument("--height", type=int, default=TARGET_H,
                    help=f"Target height in pixels (default: {TARGET_H})")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.name}.jpg"

    try:
        html, final = fetch_html(args.url)
    except Exception as e:
        sys.exit(f"Failed to fetch page: {type(e).__name__}: {e}")

    og_url = find_og_image(html, final)
    if not og_url:
        sys.exit("No og:image / twitter:image meta tag found on the page.")
    print(f"og:image: {og_url}")

    try:
        raw = fetch_image(og_url)
    except Exception as e:
        sys.exit(f"Failed to fetch image: {type(e).__name__}: {e}")

    try:
        normalised, src_size = normalise_image(raw, args.width, args.height)
    except Exception as e:
        sys.exit(f"Failed to process image: {type(e).__name__}: {e}")

    out_path.write_bytes(normalised)
    print(
        f"wrote {out_path} "
        f"({src_size[0]}x{src_size[1]} -> {args.width}x{args.height}, "
        f"{len(normalised)//1024}KB)"
    )


if __name__ == "__main__":
    main()
