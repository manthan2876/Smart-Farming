r"""
download_images.py
------------------
Auto-downloads real-world "in-the-wild" leaf images from iNaturalist API.
No API key required. Downloads ~200 images per crop class.

Run from: d:\Crop Identification Dataset\notebooks\
Output:   d:\Crop Identification Dataset\new_images\<ClassName>\

Verified taxon IDs (2026-07):
  BellPepper  : 48514  (Capsicum annuum)          - 26,833 obs
  Chilli      : 122796 (Capsicum frutescens)       -  2,957 obs
  Cotton      : 77299  (Gossypium hirsutum)        -  5,639 obs
  Groundnut   : 63205  (Arachis hypogaea)          -  2,550 obs
  Potato      : 53858  (Solanum tuberosum)         - 13,168 obs
  Tomato      : 51737  (Solanum lycopersicum)      - 46,634 obs
"""

import os
import sys
import time
import urllib.request
import urllib.parse
import json

BASE_OUTPUT = r"d:\Crop Identification Dataset\new_images"

# (class_name, taxon_id, target_count)
CLASSES = [
    ("BellPepper", 48514,  200),
    ("Chilli",     122796, 150),
    ("Cotton",     77299,  150),
    ("Groundnut",  63205,  150),
    ("Potato",     53858,  200),
    ("Tomato",     51737,  200),
]

HEADERS = {"User-Agent": "Mozilla/5.0 (CropLeafResearch)"}

def fetch_observations(taxon_id, per_page=100, page=1):
    params = {
        "taxon_id":      taxon_id,
        "quality_grade": "research",
        "photos":        "true",
        "per_page":      per_page,
        "page":          page,
        "order":         "desc",
        "order_by":      "votes",
    }
    url = "https://api.inaturalist.org/v1/observations?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

def download_image(url, dest_path):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        if len(data) < 5000:   # skip tiny/corrupt images
            return False
        with open(dest_path, "wb") as f:
            f.write(data)
        return True
    except Exception:
        return False

def count_existing(directory, exts=(".jpg", ".jpeg", ".png")):
    return len([f for f in os.listdir(directory)
                if os.path.splitext(f)[1].lower() in exts])

def download_class(class_name, taxon_id, target_count):
    out_dir = os.path.join(BASE_OUTPUT, class_name)
    os.makedirs(out_dir, exist_ok=True)

    existing = count_existing(out_dir)
    if existing >= target_count:
        print(f"  [{class_name}] Already have {existing} images. Skipping.", flush=True)
        return existing

    print(f"\n[{class_name}] Fetching up to {target_count} images "
          f"(taxon_id={taxon_id})...", flush=True)

    downloaded = existing
    page = 1

    while downloaded < target_count:
        try:
            data    = fetch_observations(taxon_id, per_page=100, page=page)
            results = data.get("results", [])
        except Exception as e:
            print(f"  API error page {page}: {e}", flush=True)
            break

        if not results:
            print(f"  No more results at page {page}.", flush=True)
            break

        for obs in results:
            if downloaded >= target_count:
                break
            photos = obs.get("photos", [])
            if not photos:
                continue

            url = photos[0].get("url", "")
            if not url:
                continue
            # Replace 'square' with 'medium' for larger images
            url = url.replace("/square.", "/medium.")

            ext = url.split("?")[0].rsplit(".", 1)[-1][:4].lower()
            if ext not in ("jpg", "jpeg", "png"):
                ext = "jpg"

            fname = f"inat_{class_name.lower()}_{downloaded+1:04d}.{ext}"
            dest  = os.path.join(out_dir, fname)

            if os.path.exists(dest):
                downloaded += 1
                continue

            ok = download_image(url, dest)
            if ok:
                downloaded += 1
                if downloaded % 25 == 0:
                    print(f"  [{class_name}] {downloaded}/{target_count} downloaded...", flush=True)
            time.sleep(0.25)

        page += 1
        time.sleep(0.5)

    print(f"  [{class_name}] Done: {downloaded} images in {out_dir}", flush=True)
    return downloaded


def main():
    print("=" * 60, flush=True)
    print("iNaturalist Leaf Image Downloader (Fixed)", flush=True)
    print(f"Output: {BASE_OUTPUT}", flush=True)
    print("=" * 60, flush=True)

    total = 0
    for class_name, taxon_id, count in CLASSES:
        n = download_class(class_name, taxon_id, count)
        total += n

    print(f"\nAll done! Total downloaded: {total}", flush=True)
    print("Next: run scripts/add_new_images.py", flush=True)


if __name__ == "__main__":
    main()
