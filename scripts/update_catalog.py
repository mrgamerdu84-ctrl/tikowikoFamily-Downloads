#!/usr/bin/env python3
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

OWNER = "mrgamerdu84-ctrl"
REPO = "tikowikoFamily-Downloads"
README = "README.md"
BUGFIX_FILE = "CORRECTIONS_BUGS.txt"
STATUS_FILE = "STATUTS_COULEURS.txt"
DELETED_FILE = "APPLICATIONS_SUPPRIMEES.txt"
STABLE_FILE = "APPLICATIONS_STABLES.txt"
MANUAL_STATUS_FILE = "STATUTS_MANUELS.txt"

# Applications déjà disponibles sur Google Play en version de test.
# Une application en correction de bugs reste prioritairement orange.
STORE_APPS = {
    "la-jungle-de-l-arcade": {
        "label": "Google Play — version test",
        "url": "https://play.google.com/store/apps/details?id=com.planete.sharky.game",
    },
}

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

def api_patch(url, payload):
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return None
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "tikowikoFamily-catalog",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    with urllib.request.urlopen(req) as response:
        return json.load(response)

def api_delete(url):
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return False
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "tikowikoFamily-catalog",
        "Authorization": f"Bearer {token}",
    }
    req = urllib.request.Request(url, headers=headers, method="DELETE")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status in (200, 202, 204)
    except Exception:
        return False

def forced_download_url(asset):
    """Force le navigateur mobile à traiter l'asset GitHub comme un téléchargement."""
    url = (asset or {}).get("browser_download_url", "#")
    if not url or url == "#":
        return "#"
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}download=1"

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

def load_deleted_apps():
    selected = set()
    if not os.path.exists(DELETED_FILE):
        return selected
    with open(DELETED_FILE, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            selected.add(line.casefold())
    return selected

DELETED_APPS = load_deleted_apps()

def load_stable_apps():
    selected = set()
    if not os.path.exists(STABLE_FILE):
        return selected
    with open(STABLE_FILE, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            selected.add(line.casefold())
    return selected

STABLE_APPS = load_stable_apps()

def load_manual_statuses():
    selected = {}
    if not os.path.exists(MANUAL_STATUS_FILE):
        return selected
    with open(MANUAL_STATUS_FILE, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            app, color = line.split("|", 1)
            app = app.strip().casefold()
            color = color.strip().lower()
            if app and color in {"purple", "yellow", "orange", "blue", "green", "gray", "red"}:
                selected[app] = color
    return selected

MANUAL_STATUSES = load_manual_statuses()

MANUAL_STATUS_META = {
    "purple": ("🟣", "En réflexion", "Projet en suspens : décision en cours sur la poursuite ou non du développement.", "purple"),
    "yellow": ("🟡", "Test développeur", "Le développeur teste actuellement cette application avant une éventuelle mise à disposition publique.", "yellow"),
    "orange": ("🟠", "Correction active", "Des corrections de bugs ou correctifs sont en cours.", "orange"),
    "blue": ("🔵", "Développement actif", "Développement maintenu actif manuellement par le créateur.", "blue"),
    "green": ("🟢", "Disponible / test", "Application déclarée disponible en version de test par le créateur.", "green"),
    "gray": ("⚪", "Stable pour le moment", "Application déclarée stable pour le moment par le créateur.", "gray"),
    "red": ("🔴", "Pas disponible", "Application déclarée indisponible par le créateur.", "red"),
}

def manual_status_for(repo_name, display_name):
    return MANUAL_STATUSES.get(repo_name.casefold()) or MANUAL_STATUSES.get(display_name.casefold())

def is_stable_selected(repo_name, display_name):
    return (
        repo_name.casefold() in STABLE_APPS
        or display_name.casefold() in STABLE_APPS
    )

def is_deleted_app(repo_name, display_name=""):
    return (
        repo_name.casefold() in DELETED_APPS
        or (display_name and display_name.casefold() in DELETED_APPS)
    )

def is_bugfix_selected(repo_name, display_name):
    return (
        repo_name.casefold() in BUGFIX_APPS
        or display_name.casefold() in BUGFIX_APPS
    )

FIX_KEYWORDS = (
    "corrig", "fix", "bug", "répar", "repar", "patch",
    "crash", "erreur", "bloqu", "rame", "problème", "probleme"
)

def release_age_days(release):
    value = release.get("published_at") or release.get("updated_at")
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return max(0, (datetime.now(timezone.utc) - dt).days)

def automatic_status(repo_name, display_name, release, apk, bugfix, stable, store_info=None, manual=None):
    body = (release.get("body") or "").casefold() if release else ""
    age = release_age_days(release) if release else None

    # Un statut manuel choisi dans GitHub Actions est prioritaire.
    if manual in MANUAL_STATUS_META:
        icon, label, reason, key = MANUAL_STATUS_META[manual]
        if age is not None and key not in ("purple", "yellow", "red"):
            reason += f" Dernière mise à jour il y a {age} jour(s)."
        return icon, label, reason, key

    # Une correction déclarée manuellement reste prioritaire.
    if bugfix:
        reason = "Des corrections de bugs ou correctifs sont en cours."
        if age is not None:
            reason += f" Dernière mise à jour il y a {age} jour(s)."
        return "🟠", "Correction active", reason, "orange"

    # Le statut stable explicite neutralise les anciens mots fix/bug des notes de Release.
    if stable:
        reason = "Application déclarée stable pour le moment."
        if age is not None:
            reason += f" Dernière mise à jour il y a {age} jour(s)."
        return "⚪", "Stable pour le moment", reason, "gray"

    if any(keyword in body for keyword in FIX_KEYWORDS):
        reason = "Des corrections de bugs ou correctifs sont indiqués dans la dernière version."
        if age is not None:
            reason += f" Dernière mise à jour il y a {age} jour(s)."
        return "🟠", "Correction active", reason, "orange"

    if store_info:
        return (
            "🟢",
            "Google Play Test",
            "Cette application est disponible sur Google Play en version de test.",
            "green",
        )

    if not release or not apk:
        return "🔴", "Pas disponible", "Aucune APK publique disponible dans Download.", "red"

    if age is not None and age <= 14:
        return (
            "🔵",
            "Développement actif",
            f"APK mise à jour récemment ({age} jour(s)) : développement actuel détecté.",
            "blue",
        )

    if age is None:
        return "⚪", "Stable pour le moment", "APK disponible, mais date de mise à jour non déterminée.", "gray"

    return (
        "⚪",
        "Stable pour le moment",
        f"APK disponible ; aucune activité récente détectée depuis {age} jour(s).",
        "gray",
    )

def release_timestamp(release):
    if not release:
        return 0
    value = release.get("published_at") or release.get("updated_at") or release.get("created_at")
    if not value:
        return 0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0

def release_belongs_to_app(repo_name, release):
    prefix = safe_tag(repo_name)[:-7]
    tag = release.get("tag_name") or ""
    return tag == prefix + "-latest" or re.fullmatch(re.escape(prefix) + r"-v\d+", tag) is not None

def sync_app_release_visibility(repo_name, should_hide):
    """Orange = toutes les Releases APK de l'app passent en brouillon privé."""
    changed = 0
    for release in releases:
        if not release_belongs_to_app(repo_name, release):
            continue
        has_apk = any(
            asset.get("name", "").lower().endswith(".apk")
            for asset in release.get("assets", [])
        )
        if not has_apk:
            continue
        if bool(release.get("draft")) == bool(should_hide):
            continue
        updated = api_patch(
            f"https://api.github.com/repos/{OWNER}/{REPO}/releases/{release['id']}",
            {"draft": bool(should_hide)},
        )
        if updated:
            release.update(updated)
            changed += 1
    return changed

releases = api_get(
    f"https://api.github.com/repos/{OWNER}/{REPO}/releases?per_page=100"
)

release_by_tag = {
    release.get("tag_name"): release
    for release in releases
}

# Départs connus, en ignorant définitivement les applications supprimées.
apps = {
    repo_name: display_name
    for repo_name, display_name in KNOWN_APPS.items()
    if not is_deleted_app(repo_name, display_name)
}

# Index insensible à la casse : TikowikoMusicV2 et tikowikomusicv2
# représentent la même application et ne doivent jamais créer deux lignes.
app_keys_folded = {repo_name.casefold(): repo_name for repo_name in apps}

def release_repo_guess(release):
    tag = release.get("tag_name") or ""
    if tag.endswith("-latest"):
        return tag[:-7]
    match = re.fullmatch(r"(.+)-v\d+", tag)
    return match.group(1) if match else ""

# Supprimer du dépôt Download les anciennes Releases des applications placées
# dans APPLICATIONS_SUPPRIMEES.txt pour qu'elles ne puissent plus réapparaître.
for release in list(releases):
    repo_guess = release_repo_guess(release)
    if not repo_guess:
        continue
    known_key = next((k for k in KNOWN_APPS if k.casefold() == repo_guess.casefold()), repo_guess)
    known_display = KNOWN_APPS.get(known_key, "")
    title = (release.get("name") or "").replace(" — Android", "").strip()
    title = re.sub(r"\s+v\d+\s*\(dernière\)$", "", title, flags=re.IGNORECASE)
    if is_deleted_app(repo_guess, known_display or title):
        api_delete(f"https://api.github.com/repos/{OWNER}/{REPO}/releases/{release['id']}")

# Une nouvelle Release "-latest" peut ajouter un futur projet, sauf s'il est
# supprimé ou s'il correspond déjà à une application connue avec une casse différente.
for release in releases:
    tag = release.get("tag_name") or ""
    if not tag.endswith("-latest"):
        continue
    apks = [a for a in release.get("assets", []) if a.get("name", "").lower().endswith(".apk")]
    if not apks:
        continue
    repo_name = tag[:-7]
    title = (release.get("name") or "").replace(" — Android", "").strip()
    title = re.sub(r"\s+v\d+\s*\(dernière\)$", "", title, flags=re.IGNORECASE)
    display_guess = title or repo_name.replace("-", " ").replace("_", " ").title()

    if is_deleted_app(repo_name, display_guess):
        continue

    folded = repo_name.casefold()
    if folded in app_keys_folded:
        continue

    apps[repo_name] = display_guess
    app_keys_folded[folded] = repo_name

rows = []
for repo_name, display_name in apps.items():
    release = release_by_tag.get(safe_tag(repo_name))
    apk = None
    if release:
        apks = [a for a in release.get("assets", []) if a.get("name", "").lower().endswith(".apk")]
        apk = apks[0] if apks else None

    bugfix = is_bugfix_selected(repo_name, display_name)
    stable = is_stable_selected(repo_name, display_name)
    manual = manual_status_for(repo_name, display_name)
    store_info = STORE_APPS.get(repo_name)
    color_icon, progress_label, reason, color_key = automatic_status(
        repo_name, display_name, release, apk, bugfix, stable, store_info, manual
    )

    # Orange, violet et rouge : aucune APK publique pendant ce statut.
    sync_app_release_visibility(repo_name, color_key in ("orange", "purple", "yellow", "red"))

    ts = release_timestamp(release)
    base = {
        "name": display_name,
        "status": f"{color_icon} {progress_label}",
        "reason": reason,
        "bugfix": color_key == "orange",
        "manual": manual,
        "progress": progress_label,
        "color_key": color_key,
        "updated_ts": ts,
        "store": bool(store_info),
    }

    if color_key == "green" and store_info:
        rows.append({
            **base,
            "date": formatted_date(release.get("published_at") or release.get("updated_at")) if release else "—",
            "size": human_size(apk.get("size", 0)) if apk else "Google Play",
            "download": f"[▶️ Ouvrir sur Google Play]({store_info['url']})",
            "details": f"[Voir la Release GitHub]({release.get('html_url', '#')})" if release and not release.get("draft") else "Version test sur le Store",
            "downloads": int(apk.get("download_count", 0) or 0) if apk else 0,
            "ready": True,
            "download_blocked": False,
        })
    elif color_key == "orange":
        rows.append({
            **base,
            "date": formatted_date(release.get("published_at") or release.get("updated_at")) if release else "—",
            "size": "—",
            "download": "🟠 Indisponible · correction de bugs en cours",
            "details": "🛠️ Correction en cours",
            "downloads": 0,
            "ready": False,
            "download_blocked": True,
        })
    elif color_key == "purple":
        rows.append({
            **base,
            "date": formatted_date(release.get("published_at") or release.get("updated_at")) if release else "—",
            "size": "—",
            "download": "🟣 Indisponible · projet en réflexion",
            "details": "🤔 Projet en suspens",
            "downloads": 0,
            "ready": False,
            "download_blocked": True,
        })
    elif color_key == "yellow":
        rows.append({
            **base,
            "date": formatted_date(release.get("published_at") or release.get("updated_at")) if release else "—",
            "size": "—",
            "download": "🟡 Indisponible · test développeur en cours",
            "details": "🧪 Test développeur",
            "downloads": 0,
            "ready": False,
            "download_blocked": True,
        })
    elif color_key == "red":
        rows.append({
            **base,
            "date": formatted_date(release.get("published_at") or release.get("updated_at")) if release else "—",
            "size": "—",
            "download": "🔴 APK indisponible",
            "details": "⛔ Indisponible",
            "downloads": 0,
            "ready": False,
            "download_blocked": True,
        })
    elif release and apk:
        rows.append({
            **base,
            "date": formatted_date(release.get("published_at") or release.get("updated_at")),
            "size": human_size(apk.get("size", 0)),
            "download": f"[⬇️ Télécharger l'APK]({forced_download_url(apk)})",
            "details": f"[Voir la Release]({release.get('html_url', '#')})",
            "downloads": int(apk.get("download_count", 0) or 0),
            "ready": True,
            "download_blocked": False,
        })
    else:
        rows.append({
            **base,
            "date": "—",
            "size": "—",
            "download": "⏳ APK pas encore publié",
            "details": "—",
            "downloads": 0,
            "ready": False,
            "download_blocked": True,
        })

# Mettre en avant : corrections, développement récent, Store, puis stable et indisponible.
priority = {"purple": 0, "yellow": 1, "orange": 2, "blue": 3, "green": 4, "gray": 5, "red": 6}
rows.sort(key=lambda item: (
    priority.get(item["color_key"], 9),
    -item["updated_ts"],
    item["name"].lower(),
))

ready_count = sum(1 for row in rows if row["ready"])
reflection_count = sum(1 for row in rows if row["color_key"] == "purple")
developer_test_count = sum(1 for row in rows if row["color_key"] == "yellow")
bugfix_count = sum(1 for row in rows if row["color_key"] == "orange")
active_count = sum(1 for row in rows if row["color_key"] in ("orange", "blue"))
store_count = sum(1 for row in rows if row["color_key"] == "green")
unavailable_count = sum(1 for row in rows if row["color_key"] == "red")
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
    f'**{len(rows)} projets référencés · {reflection_count} en réflexion · {developer_test_count} en test développeur · {active_count} en développement actuel · {bugfix_count} en correction · {store_count} sur Google Play Test · {unavailable_count} indisponibles · {download_total} téléchargements APK**',
    '',
    '> ⚠️ Certaines APK sont encore en développement et peuvent donc contenir quelques bugs.',
    '>',
    '> **Couleurs :** 🟣 En réflexion · 🟡 Test développeur · 🟠 Correction active · 🔵 Développement actif · 🟢 Disponible / test · ⚪ Stable · 🔴 Indisponible.',
    '>',
    '> La couleur est recalculée automatiquement à chaque mise à jour du catalogue selon la dernière APK et les changements indiqués dans la Release.',
    '>',
    '> 🧪 Les APK disponibles sont des **versions de test en développement** : elles sont installables et testables, mais ne sont pas encore considérées comme des versions finales.',
    '>',
    '> 🛠️ Les applications en **🟠 Correction active** restent visibles dans le catalogue, mais toutes leurs Releases APK sont temporairement masquées du public jusqu’à la fin de la correction.',
    '>',
    '> 🚧 Les applications sans APK sont encore en cours de développement.',
    '',
    '## 🟣 Projets en réflexion',
    '',
    *([f"- **{row['name']}** — projet en suspens, décision en cours sur la suite du développement." for row in rows if row["color_key"] == "purple"] or ["_Aucun projet en réflexion actuellement._"]),
    '',
    '## 🟡 Tests développeur',
    '',
    *([f"- **{row['name']}** — test en cours par le développeur ; téléchargement public temporairement bloqué." for row in rows if row["color_key"] == "yellow"] or ["_Aucune application en test développeur actuellement._"]),
    '',
    '## 🔥 Développement actuel',
    '',
    *([f"- {row['status']} **{row['name']}** · mise à jour {row['date']}" for row in rows if row["color_key"] in ("orange", "blue")] or ["_Aucun développement récent détecté._"]),
    '',
    'Les applications les plus récemment mises à jour apparaissent en premier dans le catalogue.',
    '',
    '## 🟢 Applications sur Google Play',
    '',
    *([f"- **{row['name']}** — [▶️ Ouvrir la version test sur Google Play]({STORE_APPS[next(k for k,v in KNOWN_APPS.items() if v == row['name'])]['url']})" for row in rows if row["color_key"] == "green" and row["name"] in KNOWN_APPS.values()] or ["_Aucune application Store signalée actuellement._"]),
    '',
    '## 🛠️ Applications en correction de bugs',
    '',
    *([f"- **{row['name']}**" for row in rows if row["color_key"] == "orange"] or ["_Aucune application signalée actuellement._"]),
    '',
    'Pour modifier cette liste, édite simplement le fichier **CORRECTIONS_BUGS.txt** : une application par ligne. Tu peux écrire soit le nom du dépôt, soit le nom affiché dans le catalogue.',
    '',
    '## 🎨 Couleurs automatiques',
    '',
    '- 🟣 **Violet — En réflexion** : projet en suspens ; on décide s’il sera poursuivi, revu ou arrêté. Les APK sont masquées du public.',
    '- 🟡 **Jaune — Test développeur** : l’APK est testée par le développeur avant publication. Les joueurs ne peuvent pas encore la télécharger.',
    '- 🟠 **Orange — Correction active** : une correction est déclarée ou détectée. Toutes les Releases APK de l’application sont temporairement masquées du public.',
    '- 🔵 **Bleu — Développement actif** : une APK a été publiée ou mise à jour dans les 14 derniers jours, sans correction active. Les plus récentes sont affichées en premier.',
    '- 🟢 **Vert — Disponible / test** : l’application est disponible en version de test ; si elle est sur Google Play, le bouton Store est affiché.',
    '- ⚪ **Gris — Stable pour le moment** : une APK existe mais aucune activité récente n’est détectée.',
    '- 🔴 **Rouge — Pas disponible** : aucune APK publique n’est disponible dans Download.',
    '',
    'Chaque ligne du catalogue explique automatiquement pourquoi la couleur a été choisie.',
    '',
    '## 📱 Catalogue complet',
    '',
    '| Application | Statut | Pourquoi cette couleur ? | Mise à jour | Taille | Téléchargements | Télécharger | Détails |',
    '|---|---|---|---:|---:|---:|---|---|',
]
for item in rows:
    catalog.append(
        f"| 🎮 **{item['name']}** | {item['status']} | {item['reason']} | {item['date']} | {item['size']} | "
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
    'Pour une application disponible, appuie sur **Télécharger l’APK** : le lien force maintenant le téléchargement du fichier .apk sur Android.',
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
