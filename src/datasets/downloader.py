#!/usr/bin/env python3
"""Télécharge toutes les parties d'un joueur via l'API publique de Chess.com.

Doc : https://support.chess.com/en/articles/9650547-published-data-api
- les requêtes en série ne sont pas limitées, les requêtes parallèles peuvent
  recevoir un 429 « Too Many Requests » ;
- Chess.com demande un User-Agent qui identifie l'outil avec un contact.

Usage :
    python -m electriz.datasets.downloader MagnusCarlsen --contact moi@example.com
    (ou variable d'environnement ELECTRIZ_CONTACT)
"""

import argparse
import os
import sys
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.chess.com/pub/player"


def creer_session(contact):
    session = requests.Session()
    ua = "electriz/0.1 (https://github.com/Timodur/electriz"
    ua += f"; contact: {contact})" if contact else ")"
    session.headers.update({"User-Agent": ua, "Accept": "application/json"})
    # Réessaie sur 429 / erreurs serveur, en respectant l'en-tête Retry-After.
    retry = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def get_archives(session, player):
    """Liste des URL d'archives mensuelles du joueur (404 si joueur inconnu)."""
    r = session.get(f"{BASE_URL}/{player}/games/archives", timeout=20)
    r.raise_for_status()
    return r.json().get("archives", [])


def download_month(session, archive_url):
    """PGN d'un mois (endpoint .../games/YYYY/MM/pgn)."""
    r = session.get(archive_url + "/pgn", timeout=60)
    r.raise_for_status()
    return r.text


def main():
    parser = argparse.ArgumentParser(description="Téléchargement des parties Chess.com")
    parser.add_argument("player", help="pseudo Chess.com, ex. MagnusCarlsen")
    parser.add_argument("--contact", default=os.environ.get("ELECTRIZ_CONTACT"),
                        help="e-mail de contact mis dans le User-Agent")
    parser.add_argument("--output", help="défaut : data/raw/<player>_all.pgn")
    args = parser.parse_args()

    if not args.contact:
        print("Conseil : ajoute --contact (Chess.com le recommande pour éviter les blocages).")

    output = args.output or f"data/raw/{args.player}_all.pgn"
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    session = creer_session(args.contact)

    try:
        archives = get_archives(session, args.player)
    except requests.HTTPError as e:
        sys.exit(f"Impossible de lire les archives de {args.player} : {e}")
    print(f"{len(archives)} mois d'archives")

    ok = 0
    with open(output, "w", encoding="utf-8") as f:
        for i, archive in enumerate(archives, start=1):
            mois = "/".join(archive.split("/")[-2:])
            try:
                pgn = download_month(session, archive)
            except requests.RequestException as e:
                print(f"[{i}/{len(archives)}] {mois} : échec ({e})")
                continue
            f.write(pgn.rstrip() + "\n\n")
            ok += 1
            print(f"[{i}/{len(archives)}] {mois} : {pgn.count('[Event ')} parties")
            time.sleep(0.5)  # requêtes en série, sans marteler l'API

    taille = os.path.getsize(output) / (1024 * 1024)
    print(f"\n{ok}/{len(archives)} mois téléchargés -> {output} ({taille:.1f} Mo)")


if __name__ == "__main__":
    main()
