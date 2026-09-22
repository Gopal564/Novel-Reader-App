"""
github_chapter_fetcher.py
-------------------------
Automated chapter batch fetcher for GitHub Actions and local execution.
Fetches chapters in bundles of 50 from NovelPing (or any source), cleans the text,
tokenizes into TTS sentences, and updates index.json manifest.
"""

import os
import re
import json
import time
import argparse
import urllib.request
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from novel_scraper import NovelScraper

NOVEL_ID = "infinite-mana-in-the-apocalypse"
ARCHIVE_AJAX_URL = f"https://novelping.com/ajax/chapter-archive?novelId={NOVEL_ID}"

def fetch_all_chapter_links():
    """Fetches the complete archive of all 5,700+ chapters from NovelPing."""
    print(f"Fetching complete chapter archive for novel '{NOVEL_ID}'...")
    req = urllib.request.Request(
        ARCHIVE_AJAX_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "X-Requested-With": "XMLHttpRequest"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        html = res.read().decode("utf-8", errors="ignore")

    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    
    chapter_map = {}
    for a in links:
        href = a.get("href")
        text = a.get_text(strip=True)
        if not href:
            continue
        
        # Match chapter number from title or URL (e.g., "Chapter 1780 - ...")
        m = re.search(r'chapter[- ](\d+)', text, re.I)
        if not m:
            m = re.search(r'chapter-(\d+)', href, re.I)
            
        if m:
            ch_num = int(m.group(1))
            if ch_num not in chapter_map:
                chapter_map[ch_num] = {
                    "chapter_number": ch_num,
                    "title": text or f"Chapter {ch_num}",
                    "url": href if href.startswith("http") else f"https://novelping.com{href}"
                }

    print(f"Discovered {len(chapter_map)} unique chapters in archive.")
    return chapter_map

def download_bundle(start_ch: int, end_ch: int, output_dir: str = "data"):
    """Downloads a bundle of chapters from start_ch to end_ch."""
    os.makedirs(output_dir, exist_ok=True)
    chapter_map = fetch_all_chapter_links()
    scraper = NovelScraper()

    bundled_chapters = []
    print(f"\n--- Downloading Bundle: Chapter {start_ch} to {end_ch} ---")
    
    for ch_num in range(start_ch, end_ch + 1):
        if ch_num not in chapter_map:
            print(f"Warning: Chapter {ch_num} not found in archive index. Skipping.")
            continue
            
        ch_meta = chapter_map[ch_num]
        print(f"Fetching Chapter {ch_num}: {ch_meta['title']} ({ch_meta['url']})...")
        
        try:
            ch_data = scraper.fetch_chapter(ch_meta['url'])
            bundled_chapters.append({
                "chapter_index": ch_num,
                "title": ch_meta['title'],
                "url": ch_meta['url'],
                "paragraphs": ch_data.get('paragraphs', []),
                "sentences": ch_data.get('sentences', []),
                "word_count": ch_data.get('word_count', 0)
            })
            time.sleep(0.3)  # Friendly delay
        except Exception as e:
            print(f"Error fetching Chapter {ch_num}: {e}")

    bundle_filename = f"chapters_{start_ch}_{end_ch}.json"
    bundle_path = os.path.join(output_dir, bundle_filename)
    
    bundle_payload = {
        "novel_id": NOVEL_ID,
        "start_chapter": start_ch,
        "end_chapter": end_ch,
        "total_chapters": len(bundled_chapters),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "chapters": bundled_chapters
    }

    with open(bundle_path, "w", encoding="utf-8") as f:
        json.dump(bundle_payload, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully saved {len(bundled_chapters)} chapters to {bundle_path}!")

    # Update index.json manifest
    update_manifest(output_dir, bundle_filename, start_ch, end_ch, len(bundled_chapters))

def update_manifest(output_dir: str, bundle_filename: str, start_ch: int, end_ch: int, count: int):
    manifest_path = os.path.join(output_dir, "index.json")
    manifest = {"novel_id": NOVEL_ID, "bundles": []}

    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            pass

    # Filter out existing entry for this range if present
    manifest["bundles"] = [b for b in manifest.get("bundles", []) if b.get("bundle_file") != bundle_filename]
    manifest["bundles"].append({
        "bundle_file": bundle_filename,
        "start_chapter": start_ch,
        "end_chapter": end_ch,
        "chapter_count": count,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })
    # Sort bundles by start_chapter
    manifest["bundles"].sort(key=lambda b: b.get("start_chapter", 0))

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Updated manifest at {manifest_path}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch chapter bundles for Novel Reader")
    parser.add_argument("--start", type=int, default=1780, help="Start chapter number (e.g. 1780)")
    parser.add_argument("--end", type=int, default=1784, help="End chapter number (e.g. 1830)")
    parser.add_argument("--output-dir", type=str, default="data", help="Output directory for JSON bundles")
    args = parser.parse_args()

    download_bundle(args.start, args.end, args.output_dir)
