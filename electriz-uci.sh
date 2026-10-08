#!/usr/bin/env bash
# Lanceur UCI pour Cute Chess / Arena : utilise le venv du projet, d'où qu'on l'appelle.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR" && exec "$DIR/.venv/bin/python" -m electriz.uci
