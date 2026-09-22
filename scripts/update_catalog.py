#!/usr/bin/env python3
import json
import os
import re
import urllib.request
from datetime import datetime

OWNER = "mrgamerdu84-ctrl"
REPO = "tikowikoFamily-Downloads"
README = "README.md"

# Tous les dépôts privés existants au 21/09/2026.
# Les futurs projets apparaissent automatiquement dès leur première Release APK publique.
KNOWN_APPS = {
    "batterie-super-intelligente": "Batterie Super Intelligente",
    "chicken-coop-charm": "Chicken Coop Charm",
    "clandestin-arcade-manager": "Clandestin Arcade Manager",
    "divertissement-zen-": "Divertissement Zen +",
    "Game-Booster4K": "Game Booster 4K",
    "gang-de-serpent": "Gang de Serpent",
    "gleam-mine-adventure": "Gleam Mine Adventure",
    "Grimoix-petit-dragon": "Grimoix Petit Dragon",
    "histoire-pour-enfants": "Histoire pour Enfants",
    "ilopolis": "Îlopolis",
    "jackpot-sucr-casino": "Jackpot Sucré Casino",
    "l-attaque-des-dieux": "L'Attaque des Dieux",
    "la-jungle-de-l-arcade": "La Jungle de l'Arcade",
    "my-taxi-world-les-rue-sont-nous-bc60a008": "My Taxi World",
    "N-on-Jetons-": "N-on Jetons",
    "planete-sharky-game": "Planète Sharky",
    "SmoothinCreams": "SmoothinCreams",
    "snack-attack-": "Snack Attack",
    "super-winner-de-la-fortune": "Super Winner de la Fortune",
    "tapas-fiesta": "Tapas Fiesta",
    "tikowiko-agenda-budg-taire": "Tikowiko Agenda Budgétaire",
    "tikoWiko-Anti-virus-": "TikoWiko Anti-virus",
    "TikoWiko-Aviator": "TikoWiko Aviator",
    "tikowiko-security": "Tikowiko Security",
    "tikowikocity": "Tikowiko City",
    "tikowikocosystme": "Ecosylune",
    "tikowikointelligent-": "Tikowiko Intelligent",
    "tikoWiko-taxi-": "tikoWikoTaxi",
    "TikowikoMusic": "Tikowiko Music",
    "TikowikoMusicV2": "Tikowiko Music V2",
}

def safe_tag(name):
    return re.sub(r"[^a-z0-9._-]", "-", name.lower()) + "-latest"

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

def formatted_date(value):
    if not value:
        return "—"
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt.strftime("%d/%m/%Y")

releases = api_get(
    f"https://api.github.com/repos/{OWNER}/{REPO}/releases?per_page=100"
)

release_by_tag = {
    release.get("tag_name"): release
    for release in releases
    if not release.get("draft")
}

apps = dict(KNOWN_APPS)

# Si un nouveau dépôt est publié plus tard, sa Release l'ajoute automatiquement au catalogue.
for release in releases:
    if release.get("draft"):
        continue
    apks = [a for a in release.get("assets", []) if a.get("name", "").lower().endswith(".apk")]
    if not apks:
        continue
    apk_name = apks[0]["name"]
    repo_name = apk_name[:-4] if apk_name.lower().endswith(".apk") else apk_name
    if repo_name not in apps:
        title = (release.get("name") or "").replace(" — Android", "").strip()
        apps[repo_name] = title or repo_name.replace("-", " ").replace("_", " ").title()

rows = []
for repo_name, display_name in apps.items():
    release = release_by_tag.get(safe_tag(repo_name))
    apk = None
    if release:
        apks = [a for a in release.get("assets", []) if a.get("name", "").lower().endswith(".apk")]
        apk = apks[0] if apks else None

    if release and apk:
        rows.append({
            "name": display_name,
            "date": formatted_date(release.get("published_at") or release.get("updated_at")),
            "size": human_size(apk.get("size", 0)),
            "download": f"[⬇️ Télécharger l'APK]({apk.get('browser_download_url', '#')})",
            "details": f"[Voir la Release]({release.get('html_url', '#')})",
            "downloads": int(apk.get("download_count", 0) or 0),
            "status": "🧪 Test public · En développement",
            "ready": True,
        })
    else:
        rows.append({
            "name": display_name,
            "date": "—",
            "size": "—",
            "download": "⏳ APK pas encore publié",
            "details": "—",
            "downloads": 0,
            "status": "🚧 En développement",
            "ready": False,
        })

rows.sort(key=lambda item: (not item["ready"], item["name"].lower()))

ready_count = sum(1 for row in rows if row["ready"])
dev_count = len(rows) - ready_count
download_total = sum(row["downloads"] for row in rows)

catalog = [
    '<div align="center">',
    '',
    f'<img src="https://github.com/{OWNER}.png" width="130" alt="tikowikoFamily">',
    '',
    '# 🎮 tikowikoFamily',
    '',
    '### Jeux & applications Android',
    '',
    '![Android](https://img.shields.io/badge/Android-APK-3DDC84?logo=android&logoColor=white) ![Tests](https://img.shields.io/badge/Versions-Tests%20publics-orange) ![Développement](https://img.shields.io/badge/Statut-En%20développement-blue)',
    '',
    '**Créateur : tikowikoFamily**  ',
    '**Contact : mrgamerdu84@gmail.com**',
    '',
    '</div>',
    '',
    '---',
    '',
    '> 🔒 **Le code source n’est pas public.** Les projets restent dans des dépôts privés. Ce dépôt public sert de vitrine et de page officielle de téléchargement des APK de test.',
    '',
    f'**{len(rows)} projets référencés · {ready_count} tests publics disponibles · {dev_count} sans APK · {download_total} téléchargements APK**',
    '',
    '> 🧪 Les APK disponibles sont des **versions de test en développement** : elles sont installables et testables, mais ne sont pas encore considérées comme des versions finales.',
    '>',
    '> 🚧 Les applications sans APK sont encore en cours de développement.',
    '',
    '## 📱 Catalogue complet',
    '',
    '| Application | Statut | Mise à jour | Taille | Téléchargements | Télécharger | Détails |',
    '|---|---|---:|---:|---:|---|---|',
]
for item in rows:
    catalog.append(
        f"| 🎮 **{item['name']}** | {item['status']} | {item['date']} | {item['size']} | "
        f"{item['downloads']} | {item['download']} | {item['details']} |"
    )

catalog += [
    '',
    '## 📊 Statistiques',
    '',
    f'- **Téléchargements APK comptabilisés par GitHub : {download_total}**',
    '- Les compteurs sont actualisés automatiquement plusieurs fois par jour.',
    '- Les statistiques par pays ne sont pas encore affichées : GitHub ne fournit pas directement le pays des téléchargements de Releases.',
    '',
    '## 👨‍💻 Développeur',
    '',
    f'<img src="https://github.com/{OWNER}.png" width="90" alt="Développeur tikowikoFamily">',
    '',
    '**tikowikoFamily**  ',
    'Contact : **mrgamerdu84@gmail.com**',
    '',
    '## ℹ️ Installation',
    '',
    'Pour une application disponible, appuie sur **Télécharger l’APK**, puis ouvre le fichier sur Android.',
    'Android peut demander l’autorisation d’installer une application provenant de ton navigateur ou de ton gestionnaire de fichiers.',
    '',
    '## 🔄 Mises à jour automatiques',
    '',
    'Quand le Builder publie un nouvel APK, sa Release publique met automatiquement ce catalogue à jour.',
    'Un futur projet non encore référencé sera ajouté automatiquement lors de sa première Release APK.',
    '',
    '---',
    '',
    'Copyright © 2026 **tikowikoFamily**',
    '',
]
with open(README, "w", encoding="utf-8") as handle:
    handle.write("\n".join(catalog))
