#!/usr/bin/env python3
"""
Chess.com Downloader ANTI-403 Cloudflare
✅ Headers User-Agent + Email obligatoire
✅ Headers complets Chess.com
✅ Headers aléatoires anti-bot
"""
import requests
import json
import os
import time
import sys
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PLAYER = "MagnusCarlsen" 
OUTPUT_FILE = f"data/raw/{PLAYER}_all.pgn"
BASE_URL = "https://api.chess.com/pub/player"

# Headers OBLIGATOIRES Chess.com
HEADERS = {
    "User-Agent": "Mozilla/5.0 (ElectrizChessBot/1.0; +timothedurand2004@gmail.com)", 
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site"
}

# User-Agents rotation anti-Cloudflare
USER_AGENTS = [
    "Mozilla/5.0 (ElectrizChessBot/1.0; +timothedurand2004@gmail.com)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

session = requests.Session()
retry_strategy = Retry(total=5, backoff_factor=2, status_forcelist=[403, 429, 500])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

def get_headers():
    """Headers aléatoires + email"""
    headers = HEADERS.copy()
    headers["User-Agent"] = random.choice(USER_AGENTS)
    return headers

def test_player(player):
    """Test joueur + Cloudflare"""
    url = f"{BASE_URL}/{player}"
    print(f"🔍 Test {player} : {url}")
    
    for attempt in range(3):
        headers = get_headers()
        r = session.get(url, headers=headers, timeout=15)
        
        print(f"   Try {attempt+1} : {r.status_code}")
        
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"✅ {player} OK ({data.get('username')})")
                return True
            except json.JSONDecodeError:
                print("✅ 200 mais pas JSON")
                return True
        elif r.status_code == 403:
            print("⚠️  Cloudflare 403 → retry avec headers...")
            time.sleep(3 * (attempt + 1))
        elif r.status_code == 404:
            print("❌ Joueur introuvable")
            return False
        else:
            print(f"⚠️  {r.status_code}")
            time.sleep(2)
    
    return False

def get_archives(player):
    """Archives avec headers"""
    url = f"{BASE_URL}/{player}/games/archives"
    print(f"📡 Archives : {url}")
    
    for attempt in range(5):
        headers = get_headers()
        try:
            r = session.get(url, headers=headers, timeout=20)
            print(f"   Status: {r.status_code}")
            
            if r.status_code == 200:
                try:
                    data = r.json()
                    archives = data.get("archives", [])
                    print(f"✅ {len(archives)} archives")
                    return archives
                except json.JSONDecodeError:
                    print("❌ JSON invalide")
                    time.sleep(5)
            elif r.status_code == 403 or r.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"⏳ {r.status_code} → retry {wait}s")
                time.sleep(wait)
            else:
                print(f"❌ {r.status_code}: {r.text[:100]}")
                time.sleep(3)
        except Exception as e:
            print(f"❌ Exception: {e}")
            time.sleep(5)
    
    return []

def download_month(archive_url, output_file):
    """1 mois PGN"""
    month = archive_url.split("/")[-2]
    pgn_url = archive_url.replace("/archives/", "/games/") + "/pgn"
    print(f"⬇️  {month}")
    
    headers = get_headers()
    try:
        r = session.get(pgn_url, headers=headers, timeout=60)
        
        if r.status_code == 200:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(r.text.rstrip() + "\n\n")
            print(f"{len(r.text.split('[Event')) - 1} parties")
            return True
        else:
            print(f"   ❌ {r.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ {e}")
        return False

def main():
    print(f"⚡️ Chess.com Downloader ANTI-403 - {PLAYER}")
    print("📧 CHANGE User-Agent email dans code !")
    
    os.makedirs("data/raw", exist_ok=True)
    open(OUTPUT_FILE, "w").close()
    
    if not test_player(PLAYER):
        print("❌ Abandon")
        sys.exit(1)
    
    archives = get_archives(PLAYER)
    if not archives:
        print("❌ Pas d'archives")
        sys.exit(1)
    
    success = 0
    for i, archive in enumerate(archives):
        if download_month(archive, OUTPUT_FILE):
            success += 1
        
        print(f"📊 {i+1}/{len(archives)} ({success}/{i+1})")
        time.sleep(1)  # Rate limit safe
    
    size = os.path.getsize(OUTPUT_FILE) / (1024*1024)
    print(f"\n🎉 {success} mois OK")
    print(f"📁 {OUTPUT_FILE} : {size:.1f} Mo")

if __name__ == "__main__":
    main()
