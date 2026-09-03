#!/usr/bin/env python3
"""Génère REGISTRY.md et registry/{domaine}.md depuis registry.jsonl."""

import json
import re
import os
from collections import defaultdict

JSONL_PATH = "registry.jsonl"
REGISTRY_DIR = "registry"
INDEX_PATH = "REGISTRY.md"


def load_registry(path):
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def generate_domain_md(domain, entries):
    lines = [f"# {domain}\n"]
    lines.append("| Titre | ID | Site |")
    lines.append("|-------|----|----|")
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

    for domain in sorted(domains_data.keys()):
        count = len(domains_data[domain])
        lines.append(f"- [{domain}]({REGISTRY_DIR}/{domain}.md) ({count})")

    lines.append("")
    return "\n".join(lines)


def main():
    entries = load_registry(JSONL_PATH)

    os.makedirs(REGISTRY_DIR, exist_ok=True)

    # Group by domain
    domains_data = defaultdict(list)
    for e in entries:
        domains_data[e["domain"]].append(e)

    # Generate domain files
    for domain, domain_entries in domains_data.items():
        domain_path = os.path.join(REGISTRY_DIR, f"{domain}.md")
        content = generate_domain_md(domain, domain_entries)
        with open(domain_path, "w", encoding="utf-8") as f:
            f.write(content)

    # Generate index
    index_content = generate_index_md(domains_data)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(index_content)

    print(f"Registre régénéré : {len(entries)} fiches, {len(domains_data)} domaines")


if __name__ == "__main__":
    main()
