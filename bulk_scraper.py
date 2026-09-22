"""
bulk_scraper.py
Fetches metadata and chapters 1 through 30 for Infinite Mana In The Apocalypse
Saves to android-app/app/src/main/assets/novel_data.json
"""

import os
import json
import time
from novel_scraper import NovelScraper

def main():
    scraper = NovelScraper()
    novel_url = "https://novelping.com/book/infinite-mana-in-the-apocalypse"
    
    print("Fetching novel metadata...")
    meta = scraper.extract_novel_metadata(novel_url)
    print(f"Novel: {meta['title']} | Chapters detected: {len(meta['chapters'])}")
    
    # We will fetch the first 25 chapters to bundle directly into the APK
    # (Each chapter is ~1.5k words, 25 chapters is ~37,000 words!)
    chapters_to_fetch = meta['chapters'][:25]
    bundled_chapters = []
    
    for i, ch in enumerate(chapters_to_fetch):
        print(f"[{i+1}/{len(chapters_to_fetch)}] Fetching: {ch['title']} ({ch['url']})...")
        try:
            ch_data = scraper.fetch_chapter(ch['url'])
            bundled_chapters.append({
                "chapter_index": ch['chapter_index'],
                "title": ch['title'],
                "url": ch['url'],
                "paragraphs": ch_data['paragraphs'],
                "sentences": ch_data['sentences'],
                "word_count": ch_data.get('word_count', 0)
            })
            time.sleep(0.3) # Friendly rate limiting
        except Exception as e:
            print(f"Error fetching {ch['title']}: {e}")
            
    payload = {
        "novel": {
            "title": meta["title"],
            "author": meta["author"],
            "status": meta["status"],
            "genres": meta["genres"],
            "cover_url": meta["cover_url"],
            "description": meta["description"],
            "source_url": meta["source_url"]
        },
        "all_chapters_nav": meta["chapters"], # List of all chapter titles & URLs
        "bundled_chapters": bundled_chapters
    }
    
    assets_dir = os.path.join("android-app", "app", "src", "main", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    out_path = os.path.join(assets_dir, "novel_data.json")
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccessfully bundled {len(bundled_chapters)} full chapters to {out_path}!")

if __name__ == "__main__":
    main()
