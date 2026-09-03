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


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def generate_domain_md(domain, entries, slug_index):
    lines = [f"# {domain}\n"]
    lines.append("| Titre | Variante de | ID | Repos | Site |")
    lines.append("|-------|-------------|-----|-------|------|")
    for e in sorted(entries, key=lambda x: x["title"]):
        title = e["title"]
        anchor = f"#{slugify(title)}"
        title_link = f"[{title}]({anchor})"
        slug = e.get("slug", "")
        eid = e.get("id") if e.get("id") else "—"

        # Variante de
        variant_of = e.get("variant_of")
        if variant_of and variant_of in slug_index:
            parent_title = slug_index[variant_of]
            parent_anchor = f"#{slugify(parent_title)}"
            variant_link = f"[{parent_title}]({parent_anchor})"
        elif variant_of:
            variant_link = variant_of
        else:
            variant_link = "—"

        # Repos
        repo_url = e.get("repo_url", "")
        if repo_url:
            repo_name = slug
            repo_link = f"[{repo_name}]({repo_url})"
        else:
            repo_link = "—"

        # Site
        site_url = e.get("site_url", "")
        if site_url:
            site_short = site_url.replace("https://simplonco.github.io/", "").rstrip("/")
            site_link = f"[{site_short}]({site_url})"
        else:
            site_link = "—"

        lines.append(f"| {title_link} | {variant_link} | {eid} | {repo_link} | {site_link} |")
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

    # Build slug → title index for variant resolution
    slug_index = {e["slug"]: e["title"] for e in entries if "slug" in e}

    # Group by domain
    domains_data = defaultdict(list)
    for e in entries:
        domains_data[e["domain"]].append(e)

    # Generate domain files
    for domain, domain_entries in domains_data.items():
        domain_path = os.path.join(REGISTRY_DIR, f"{domain}.md")
        content = generate_domain_md(domain, domain_entries, slug_index)
        with open(domain_path, "w", encoding="utf-8") as f:
            f.write(content)

    # Generate index
    index_content = generate_index_md(domains_data)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(index_content)

    print(f"Registre régénéré : {len(entries)} fiches, {len(domains_data)} domaines")


if __name__ == "__main__":
    main()
