#!/usr/bin/env python3
import json
import os
import re
import urllib.request
from datetime import datetime

OWNER = "mrgamerdu84-ctrl"
REPO = "tikowikoFamily-Downloads"
README = "README.md"
BUGFIX_FILE = "CORRECTIONS_BUGS.txt"
STATUS_FILE = "STATUTS_COULEURS.txt"

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

def load_bugfix_apps():
    selected = set()
    if not os.path.exists(BUGFIX_FILE):
        return selected
    with open(BUGFIX_FILE, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            selected.add(line.casefold())
    return selected

BUGFIX_APPS = load_bugfix_apps()

def is_bugfix_selected(repo_name, display_name):
    return (
        repo_name.casefold() in BUGFIX_APPS
        or display_name.casefold() in BUGFIX_APPS
    )

STATUS_DEFS = {
    "vert": ("🟢", "Terminé"),
    "green": ("🟢", "Terminé"),
    "orange": ("🟠", "Partiellement terminé"),
    "rouge": ("🔴", "Pas fini"),
    "red": ("🔴", "Pas fini"),
}

def load_status_colors():
    selected = {}
    if not os.path.exists(STATUS_FILE):
        return selected
    with open(STATUS_FILE, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            color, app = line.split(":", 1)
            color = color.strip().casefold()
            app = app.strip()
            if color in STATUS_DEFS and app:
                selected[app.casefold()] = color
    return selected

STATUS_COLORS = load_status_colors()

def app_color_status(repo_name, display_name):
    color = STATUS_COLORS.get(repo_name.casefold()) or STATUS_COLORS.get(display_name.casefold())
    if not color:
        return "⚪", "Non classé", None
    icon, label = STATUS_DEFS[color]
    return icon, label, color

releases = api_get(
    f"https://api.github.com/repos/{OWNER}/{REPO}/releases?per_page=100"
)

release_by_tag = {
    release.get("tag_name"): release
    for release in releases
    if not release.get("draft")
}

apps = dict(KNOWN_APPS)

# Si un nouveau dépôt est publié plus tard, sa Release "-latest" l'ajoute automatiquement.
# Les Releases versionnées (v76, v77, etc.) ne créent pas de doublons dans le catalogue.
for release in releases:
    if release.get("draft"):
        continue
    tag = release.get("tag_name") or ""
    if not tag.endswith("-latest"):
        continue
    apks = [a for a in release.get("assets", []) if a.get("name", "").lower().endswith(".apk")]
    if not apks:
        continue
    repo_name = tag[:-7]
    if repo_name not in apps:
        title = (release.get("name") or "").replace(" — Android", "").strip()
        title = re.sub(r"\s+v\d+\s*\(dernière\)$", "", title, flags=re.IGNORECASE)
        apps[repo_name] = title or repo_name.replace("-", " ").replace("_", " ").title()

rows = []
for repo_name, display_name in apps.items():
    release = release_by_tag.get(safe_tag(repo_name))
    apk = None
    if release:
        apks = [a for a in release.get("assets", []) if a.get("name", "").lower().endswith(".apk")]
        apk = apks[0] if apks else None

    bugfix = is_bugfix_selected(repo_name, display_name)
    color_icon, progress_label, color_key = app_color_status(repo_name, display_name)
    download_blocked = color_key in ("rouge", "red")

    if release and apk and not download_blocked:
        rows.append({
            "name": display_name,
            "date": formatted_date(release.get("published_at") or release.get("updated_at")),
            "size": human_size(apk.get("size", 0)),
            "download": f"[⬇️ Télécharger l'APK]({apk.get('browser_download_url', '#')})",
            "details": f"[Voir la Release]({release.get('html_url', '#')})",
            "downloads": int(apk.get("download_count", 0) or 0),
            "status": f"{color_icon} {progress_label} · 🛠️ Correction de bugs · Test public" if bugfix else f"{color_icon} {progress_label} · 🧪 Test public",
            "ready": True,
            "bugfix": bugfix,
            "progress": progress_label,
            "download_blocked": False,
        })
    elif release and apk and download_blocked:
        rows.append({
            "name": display_name,
            "date": formatted_date(release.get("published_at") or release.get("updated_at")),
            "size": "—",
            "download": "🚫 APK non disponible · développement en cours",
            "details": "—",
            "downloads": 0,
            "status": f"{color_icon} {progress_label} · 🛠️ Correction de bugs" if bugfix else f"{color_icon} {progress_label}",
            "ready": False,
            "bugfix": bugfix,
            "progress": progress_label,
            "download_blocked": True,
        })
    else:
        rows.append({
            "name": display_name,
            "date": "—",
            "size": "—",
            "download": "⏳ APK pas encore publié",
            "details": "—",
            "downloads": 0,
            "status": f"{color_icon} {progress_label} · 🛠️ Correction de bugs" if bugfix else f"{color_icon} {progress_label}",
            "ready": False,
            "bugfix": bugfix,
            "progress": progress_label,
            "download_blocked": download_blocked,
        })

rows.sort(key=lambda item: (not item["bugfix"], not item["ready"], item["name"].lower()))

ready_count = sum(1 for row in rows if row["ready"])
bugfix_count = sum(1 for row in rows if row["bugfix"])
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
    f'**{len(rows)} projets référencés · {ready_count} tests publics disponibles · {bugfix_count} en correction de bugs · {dev_count} sans APK · {download_total} téléchargements APK**',
    '',
    '> ⚠️ Certaines APK sont encore en développement et peuvent donc contenir quelques bugs.',
    '>',
    '> **Couleurs d’avancement :** 🟢 Terminé · 🟠 Partiellement terminé · 🔴 Pas fini (APK non disponible) · ⚪ Non classé.',
    '>',
    '> Les couleurs sont choisies manuellement dans **STATUTS_COULEURS.txt**.',
    '>',
    '> 🧪 Les APK disponibles sont des **versions de test en développement** : elles sont installables et testables, mais ne sont pas encore considérées comme des versions finales.',
    '>',
    '> 🛠️ Les applications marquées **Correction de bugs** ont été sélectionnées manuellement comme nécessitant des corrections. Elles peuvent rester téléchargeables pendant que les bugs sont corrigés.',
    '>',
    '> 🚧 Les applications sans APK sont encore en cours de développement.',
    '',
    '## 🛠️ Applications en correction de bugs',
    '',
    *([f"- **{row['name']}**" for row in rows if row["bugfix"]] or ["_Aucune application signalée actuellement._"]),
    '',
    'Pour modifier cette liste, édite simplement le fichier **CORRECTIONS_BUGS.txt** : une application par ligne. Tu peux écrire soit le nom du dépôt, soit le nom affiché dans le catalogue.',
    '',
    '## 🎨 Couleurs d’avancement',
    '',
    '- 🟢 **Vert** : application terminée',
    '- 🟠 **Orange** : application partiellement terminée / encore en finition',
    '- 🔴 **Rouge** : application pas encore finie — **APK non disponible dans le catalogue Download**',
    '- ⚪ **Blanc** : aucun statut choisi',
    '',
    'Pour choisir une couleur, édite **STATUTS_COULEURS.txt** avec le format `couleur: nom de l’application`.',
    '',
    '⚠️ Une application en **rouge** reste visible dans la liste, mais son bouton APK et son lien Release sont masqués du catalogue tant qu’elle reste rouge.',
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
