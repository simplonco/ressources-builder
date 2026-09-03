# Ressources Builder

Outil de conversion automatique des quêtes (format JSON) en ressources Jekyll déployées sur GitHub Pages.

## Fonctionnement

1. Les fichiers JSON des quêtes sont placés dans `quests/todo/`
2. Un agent IA convertit le contenu en dépôt Jekyll structuré
3. Le dépôt est poussé sur GitHub et le site est déployé via GitHub Pages

## Structure

```
ressources-builder/
├── quests/
│   ├── todo/          # JSON en attente de conversion
│   └── archives/      # JSON déjà convertis
├── repos/             # Dépôts générés (gitignored)
│   └── archives/      # Dépôts archivés après push
├── REGISTRY.md        # Index du registre (liens vers domaines)
├── registry.jsonl     # Registre source de vérité (JSONL)
├── registry/          # Registres par domaine (tableaux générés)
├── scripts/           # Scripts de migration/génération
└── .opencode/skills/  # Skills IA
```

## Utilisation

### Convertir une quest

```
Convertis quest-{id}.json en dépôt GitHub
```

### Tester localement

```bash
cd repos/{slug}
bundle install
bundle exec jekyll serve --livereload
```

### Lister les quests en attente

```
Liste les quests en attente de conversion
```

## Registre des contenus

[Voir le registre des contenus](REGISTRY.md) — [registry.jsonl](registry.jsonl)

## Thème

[simplonline-ressources-jekyll-theme](https://simplonco.github.io/simplonline-ressources-jekyll-theme/)
