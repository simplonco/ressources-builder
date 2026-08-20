# Odyssey Quests to GitHub

Outil de conversion automatique des quêtes Odyssey (format JSON) en dépôts GitHub utilisant le thème Jekyll Simplonline.

## Fonctionnement

1. Les fichiers JSON des quêtes sont placés dans `quests/todo/`
2. Un agent IA convertit le contenu en dépôt Jekyll structuré
3. Le dépôt est poussé sur GitHub et le site est déployé via GitHub Pages

## Structure

```
odyssey-quests-to-github/
├── quests/
│   ├── todo/          # JSON en attente de conversion
│   ├── archives/      # JSON déjà convertis
│   └── REGISTRY.md    # Registre des correspondances
├── repos/             # Dépôts générés (gitignored)
│   └── archives/      # Dépôts archivés après push
└── .opencode/skills/  # Skill de conversion IA
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

## Registre des quests

[Voir le registre des quests](quests/REGISTRY.md)

## Thème

[simplonline-ressources-jekyll-theme](https://simplonco.github.io/simplonline-ressources-jekyll-theme/)
