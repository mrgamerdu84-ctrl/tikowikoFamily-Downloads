#!/usr/bin/env python3
import json
import os
import urllib.request
from datetime import datetime

OWNER = "mrgamerdu84-ctrl"
REPO = "tikowikoFamily-Downloads"
README = "README.md"

FRIENDLY_NAMES = {
    "tikowikocosystme": "Ecosylune",
    "ilopolis": "Îlopolis",
    "jackpot-sucr-casino": "Jackpot Sucré Casino",
    "TikoWiko-Aviator": "TikoWiko Aviator",
}

def api_get(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "tikowikoFamily-catalog",
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.load(response)

def human_size(size):
    value = float(size)
    for unit in ("o", "Ko", "Mo", "Go"):
        if value < 1024 or unit == "Go":
            return f"{value:.1f} {unit}" if unit != "o" else f"{int(value)} {unit}"
        value /= 1024
    return f"{int(size)} o"

def friendly_name(release, apk):
    asset_name = apk["name"]
    base = asset_name[:-4] if asset_name.lower().endswith(".apk") else asset_name
    if base in FRIENDLY_NAMES:
        return FRIENDLY_NAMES[base]
    title = (release.get("name") or "").replace(" — Android", "").strip()
    if title in FRIENDLY_NAMES:
        return FRIENDLY_NAMES[title]
    return title or base.replace("-", " ").replace("_", " ").title()

def formatted_date(value):
    if not value:
        return "—"
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt.strftime("%d/%m/%Y")

releases = api_get(
    f"https://api.github.com/repos/{OWNER}/{REPO}/releases?per_page=100"
)

rows = []
for release in releases:
    if release.get("draft"):
        continue
    apks = [
        asset for asset in release.get("assets", [])
        if asset.get("name", "").lower().endswith(".apk")
    ]
    if not apks:
        continue
    apk = apks[0]
    rows.append({
        "name": friendly_name(release, apk),
        "date": formatted_date(release.get("published_at") or release.get("updated_at")),
        "size": human_size(apk.get("size", 0)),
        "download": apk.get("browser_download_url", "#"),
        "release": release.get("html_url", "#"),
    })

rows.sort(key=lambda item: item["name"].lower())

catalog = [
    "# 🎮 tikowikoFamily — Téléchargements Android",
    "",
    "Bienvenue sur la vitrine officielle des jeux et applications **tikowikoFamily**.",
    "",
    "> 🔒 **Le code source n'est pas public.** Ce dépôt contient uniquement les téléchargements Android publiés.",
    "",
    "## 📱 Catalogue",
    "",
]

if rows:
    catalog += [
        "| Application | Mise à jour | Taille | Télécharger | Détails |",
        "|---|---:|---:|---|---|",
    ]
    for item in rows:
        catalog.append(
            f"| 🎮 **{item['name']}** | {item['date']} | {item['size']} | "
            f"[⬇️ Télécharger l'APK]({item['download']}) | "
            f"[Voir la Release]({item['release']}) |"
        )
else:
    catalog.append("_Aucun APK public pour le moment._")

catalog += [
    "",
    "## ℹ️ Installation",
    "",
    "Télécharge l'APK de l'application souhaitée puis ouvre le fichier sur Android.",
    "Android peut demander l'autorisation d'installer une application provenant de ton navigateur ou de ton gestionnaire de fichiers.",
    "",
    "## 🔄 Mises à jour",
    "",
    "Le catalogue est régénéré automatiquement lorsqu'une nouvelle Release APK est publiée.",
    "Les projets de développement restent dans des dépôts privés séparés.",
    "",
    "---",
    "",
    "Copyright © 2026 **tikowikoFamily**",
    "",
]

with open(README, "w", encoding="utf-8") as handle:
    handle.write("\n".join(catalog))
