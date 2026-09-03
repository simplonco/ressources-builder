#!/usr/bin/env python3
"""Migre REGISTRY.md vers registry.jsonl + registres par domaine."""

import json
import re
import os
from collections import defaultdict

REGISTRY_PATH = "REGISTRY.md"
JSONL_PATH = "registry.jsonl"
REGISTRY_DIR = "registry"


def parse_registry_md(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = {}
    current_section = None
    entries = []
    entry = {}
    title = None

    for line in content.splitlines():
        # Section header: ## 🔄 En cours (0) or ## ✅ Terminé (79)
        section_match = re.match(r"^## .+", line)
        if section_match:
            if title and entry:
                entries.append({"title": title, **entry})
            title = None
            entry = {}
            if "En cours" in line:
                current_section = "en_cours"
            elif "Terminé" in line:
                current_section = "done"
            else:
                current_section = None
            sections[current_section] = []
            continue

        # Entry title: ### Concevoir des prototypes
        title_match = re.match(r"^### (.+)$", line)
        if title_match:
            if title and entry:
                entries.append({"title": title, **entry})
            title = title_match.group(1).strip()
            entry = {}
            continue

        # Field: - **ID** : 2333
        id_match = re.match(r"^- \*\*ID\*\* : (.+)$", line)
        if id_match:
            raw = id_match.group(1).strip()
            entry["id"] = int(raw) if raw.isdigit() else raw
            continue

        # Field: - **Domaine** : dev-web
        domain_match = re.match(r"^- \*\*Domaine\*\* : (.+)$", line)
        if domain_match:
            entry["domain"] = domain_match.group(1).strip()
            continue

        # Field: - **Dépôt** : [simplonco/xxx](url)
        repo_match = re.match(r"^- \*\*Dépôt\*\* : \[([^\]]+)\]\(([^)]+)\)$", line)
        if repo_match:
            entry["repo_slug"] = repo_match.group(1).strip()
            entry["repo_url"] = repo_match.group(2).strip()
            # Derive slug from repo name
            entry["slug"] = entry["repo_slug"].replace("simplonco/", "")
            continue

        # Field: - **Site** : [simplonco.github.io/xxx](url)
        site_match = re.match(r"^- \*\*Site\*\* : \[([^\]]+)\]\(([^)]+)\)$", line)
        if site_match:
            entry["site_url"] = site_match.group(2).strip()
            continue

        # Summary line (starts with - but not a **Field** pattern)
        summary_match = re.match(r"^- (.+)$", line)
        if summary_match and "**" not in line and title:
            entry["summary"] = summary_match.group(1).strip()

    # Flush last entry
    if title and entry:
        entries.append({"title": title, **entry})

    return entries


def build_jsonl_entry(entry, status):
    result = {
        "id": entry.get("id"),
        "title": entry["title"],
        "domain": entry["domain"],
        "slug": entry["slug"],
        "status": status,
        "repo_url": entry.get("repo_url", ""),
        "site_url": entry.get("site_url", ""),
    }
    summary = entry.get("summary")
    if summary:
        result["summary"] = summary
    return result


def generate_domain_md(domain, entries):
    """Génère registry/{domain}.md avec tableau compact."""
    lines = [f"# {domain}\n"]
    lines.append(f"| Titre | ID | Site |")
    lines.append(f"|-------|----|----|")
    for e in sorted(entries, key=lambda x: x["title"]):
        title = e["title"]
        title_slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        anchor = f"#{title_slug}"
        title_with_link = f"[{title}]({anchor})"
        site = e.get("site_url", "")
        eid = e.get("id") if e.get("id") else "—"
        if site:
            site_short = site.replace("https://simplonco.github.io/", "").rstrip("/")
            site_link = f"[{site_short}]({site})"
        else:
            site_link = "—"
        lines.append(f"| {title_with_link} | {eid} | {site_link} |")
    lines.append("")
    return "\n".join(lines)


def generate_index_md(domains_data):
    """Génère REGISTRY.md (index)."""
    # Count by status
    total_en_cours = 0
    total_done = 0
    for domain, entries in domains_data.items():
        for e in entries:
            if e["status"] == "en_cours":
                total_en_cours += 1
            else:
                total_done += 1

    lines = ["# Registre des contenus\n"]
    lines.append(f"## 🔄 En cours ({total_en_cours})\n")
    lines.append(f"## ✅ Terminé ({total_done})\n")

    # Link to domain registries
    for domain in sorted(domains_data.keys()):
        count = len(domains_data[domain])
        lines.append(f"- [{domain}]({REGISTRY_DIR}/{domain}.md) ({count})")

    lines.append("")
    return "\n".join(lines)


def main():
    # Parse
    entries = parse_registry_md(REGISTRY_PATH)
    print(f"Parse : {len(entries)} fiches extraites")

    # Build JSONL
    os.makedirs(REGISTRY_DIR, exist_ok=True)
    domains_data = defaultdict(list)

    with open(JSONL_PATH, "w", encoding="utf-8") as f:
        for e in entries:
            status = e.get("status", "done")  # toutes sont "done" dans l'actuel
            # Déterminer le statut : on met "done" pour l'ancien registre
            # En cours n'existe pas dans l'actuel (0 entrées)
            jsonl_entry = build_jsonl_entry(e, status="done")
            f.write(json.dumps(jsonl_entry, ensure_ascii=False) + "\n")
            domains_data[jsonl_entry["domain"]].append(jsonl_entry)

    print(f"Écrit : {JSONL_PATH} ({len(entries)} lignes)")

    # Generate domain files
    for domain, domain_entries in domains_data.items():
        domain_path = os.path.join(REGISTRY_DIR, f"{domain}.md")
        content = generate_domain_md(domain, domain_entries)
        with open(domain_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  → {domain_path} ({len(domain_entries)} fiches)")

    # Generate index
    index_content = generate_index_md(domains_data)
    with open("REGISTRY.md", "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"Écrit : REGISTRY.md (index)")


if __name__ == "__main__":
    main()
