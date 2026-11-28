"""Fiches publiques du catalogue : indépendantes des couleurs et des APK."""
import argparse
import html
import json
import re
from datetime import date
from pathlib import Path

FILE = Path("FICHES_APPLICATIONS.json")
ALIASES = {"la-petite-boulangerie-refonte": "la-petite-boulangerie"}


def key(name):
    name = name.strip().casefold()
    return ALIASES.get(name, name)


def load_metadata():
    if not FILE.exists():
        return {}
    raw = json.loads(FILE.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("FICHES_APPLICATIONS.json doit contenir un objet JSON.")
    return {key(k): v for k, v in raw.items() if isinstance(v, dict)}


def markdown_text(value):
    # Texte public, jamais interprété comme HTML ou lien Markdown.
    text = " ".join(str(value).split())
    return html.escape(text, quote=False).replace("|", "&#124;").replace("\\", "&#92;").replace("[", "&#91;").replace("]", "&#93;").replace("*", "&#42;").replace("_", "&#95;").replace("`", "&#96;").replace("!", "&#33;")


def validate_date(value):
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        date.fromisoformat(value)
    elif re.fullmatch(r"\d{4}-\d{2}", value):
        date.fromisoformat(value + "-01")
    elif re.fullmatch(r"\d{4}", value):
        date.fromisoformat(value + "-01-01")
    else:
        raise ValueError("Date attendue : AAAA-MM-JJ, AAAA-MM ou AAAA.")


def format_release(entry):
    value = entry.get("sortie")
    if not value:
        return "À déterminer"
    try:
        validate_date(value)
    except (ValueError, TypeError):
        return "À déterminer"
    parts = value.split("-")
    display = "/".join(reversed(parts))
    label = "Prévue" if entry.get("type_date") == "prevue" else "Estimée"
    return f"{label} : {display}"


def fields(metadata, repo_name):
    entry = metadata.get(key(repo_name), {})
    return (
        markdown_text(entry.get("description") or "Description à compléter"),
        format_release(entry),
    )


def update(app, description, release_date, kind):
    if not re.fullmatch(r"[A-Za-z0-9._-]+", app.strip()):
        raise ValueError("Indique le nom exact de l’application (sans espaces).")
    app = key(app)
    records = load_metadata()
    # Ne jamais restaurer une application volontairement supprimée.
    deleted = Path("APPLICATIONS_SUPPRIMEES.txt")
    if deleted.exists() and app in {
        key(line) for line in deleted.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }:
        raise ValueError("Application supprimée du catalogue : restauration nécessaire au préalable.")
    previous = records.get(app, {})
    entry = dict(previous)
    description = description.strip()
    release_date = release_date.strip()
    if description:
        entry["description"] = "" if description == "-" else " ".join(description.split())
        if len(entry["description"]) > 280:
            raise ValueError("La description doit faire au maximum 280 caractères.")
    if release_date == "-":
        entry.update(sortie=None, type_date="indeterminee")
    elif release_date:
        validate_date(release_date)
        entry["sortie"] = release_date
        entry["type_date"] = kind if kind != "conserver" else (
            previous.get("type_date") if previous.get("type_date") in {"estimee", "prevue"} else "estimee"
        )
    elif kind != "conserver":
        if not entry.get("sortie"):
            raise ValueError("Renseigne une date avant de choisir son type.")
        entry["type_date"] = kind
    if not description and not release_date and kind == "conserver":
        raise ValueError("Renseigne au moins une modification.")
    records[app] = {
        "description": entry.get("description", ""),
        "sortie": entry.get("sortie"),
        "type_date": entry.get("type_date", "indeterminee"),
    }
    FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import os
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", required=True)
    parser.add_argument("--kind", choices=["conserver", "estimee", "prevue"], default="conserver")
    args = parser.parse_args()
    try:
        update(args.app, os.environ.get("FICHE_DESCRIPTION", ""), os.environ.get("FICHE_DATE", ""), args.kind)
    except (ValueError, TypeError) as error:
        raise SystemExit(str(error))
