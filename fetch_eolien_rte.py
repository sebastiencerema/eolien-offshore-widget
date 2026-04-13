#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_eolien_rte.py
Récupère la production éolienne offshore par parc via l'API RTE
et écrit data_eolien.json dans le répertoire courant.

Credentials lus depuis les variables d'environnement :
  RTE_CLIENT_ID      (GitHub Secret)
  RTE_CLIENT_SECRET  (GitHub Secret)
"""
import requests, json, base64, os, sys
from datetime import datetime, timedelta

CLIENT_ID     = os.environ.get("RTE_CLIENT_ID",     "66c46445-121c-4e9a-98c3-89488f393a19")
CLIENT_SECRET = os.environ.get("RTE_CLIENT_SECRET",  "1293d144-c33c-42b7-b66f-2fe43d0c55fa")
OUTPUT_FILE   = "data_eolien.json"
HEURES        = 30

TOKEN_URL = "https://digital.iservices.rte-france.com/token/oauth/"
API_BASE  = "https://digital.iservices.rte-france.com/open_api/actual_generation/v1"


def fmt_rte(dt):
    if dt.tzinfo is None:
        dt = dt.astimezone()
    s   = dt.strftime("%Y-%m-%dT%H:%M:%S")
    tz  = dt.strftime("%z")
    return s + tz[:3] + ":" + tz[3:]


def get_token():
    b64  = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {b64}",
                 "Content-Type":  "application/x-www-form-urlencoded"},
        data="grant_type=client_credentials",
        timeout=15,
    )
    resp.raise_for_status()
    data  = resp.json()
    token = data.get("access_token")
    if not token:
        raise ValueError(f"Pas de token : {data}")
    print(f"[token] OK — expire dans {data.get('expires_in','?')}s")
    return token


def fetch_per_unit(token, start, end):
    url = (f"{API_BASE}/actual_generations_per_unit"
           f"?start_date={fmt_rte(start)}&end_date={fmt_rte(end)}")
    print(f"[API] GET {url}")
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    if not resp.ok:
        print(f"[API] Erreur {resp.status_code} : {resp.text[:300]}", file=sys.stderr)
        resp.raise_for_status()
    return resp.json().get("actual_generations_per_unit", [])


def build_json(units):
    parcs = []
    for unit in units:
        offshore = [v for v in unit.get("values", [])
                    if v.get("production_type") == "WIND_OFFSHORE" and v.get("value") is not None]
        if not offshore:
            continue
        serie = [{"t": v["start_date"], "mw": v["value"]} for v in offshore]
        parcs.append({"nom": unit["unit"]["name"],
                      "eic_code": unit["unit"]["eic_code"],
                      "serie": serie})
        print(f"[parc] {unit['unit']['name']} — {len(serie)} points")

    return {"generated_at": datetime.now().astimezone().isoformat(),
            "source": "RTE Actual Generation API v1.1",
            "parcs": parcs}


def main():
    now   = datetime.now().astimezone()
    start = now - timedelta(hours=HEURES)
    print(f"[fetch] {now:%Y-%m-%d %H:%M:%S} — fenêtre {HEURES}h")
    token = get_token()
    units = fetch_per_unit(token, start, now)
    print(f"[API] {len(units)} unités reçues")
    data  = build_json(units)
    if not data["parcs"]:
        print("[warn] Aucun parc WIND_OFFSHORE — vérifier la période")
    else:
        print(f"[OK] {len(data['parcs'])} parc(s) : {[p['nom'] for p in data['parcs']]}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[fichier] Écrit : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
