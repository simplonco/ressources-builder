# CLAUDE.md

## Règles du projet

- Ne jamais commit ou push sans l'autorisation explicite de l'utilisateur
- Ne jamais supprimer de fichiers ou dossiers sans validation
- Toujours lire le filesystem avant d'agir — jamais d'invention de chemins

## Skills

Les skills du projet sont dans `.agents/skills/`. Consulte chaque `SKILL.md` avant d'agir.

| Skill | Rôle | Quand l'utiliser |
|-------|------|------------------|
| `quest-to-github` | Orchestrateur de création | Conversion d'une quest JSON en ressource Jekyll (création locale uniquement) |
| `jekyll-create` | Création de ressources Jekyll | Créer/modifier une ressource Jekyll (depuis JSON ou from scratch) |
| `jekyll-deploy` | Déploiement GitHub Pages | Pousser un site Jekyll sur GitHub (sans archivage) |
| `quest-files-archive` | Validation et archivage | Mettre la fiche en Terminé + archiver fichiers après relecture |

## Commandes principales

```
Convertis quest-{id}.json
Créer une ressource Jekyll
Déploie le dépôt {slug} sur GitHub Pages
Valider et archiver quest-{id}
Liste les quests en attente de conversion
```

## Test local

```bash
cd repos/{slug}
bundle exec jekyll serve --livereload
# → http://localhost:4000
```

## Architecture

```
ressources-builder/
├── .agents/                      # Skills partagés
│   └── skills/                   # Skills (chargés par l'agent build via l'outil `skill`)
│       ├── quest-to-github/      # Orchestrateur de création
│       │   └── SKILL.md
│       ├── jekyll-create/        # Création de ressources Jekyll
│       │   ├── SKILL.md
│       │   └── templates/        # Templates Jekyll
│       │       ├── _config.yml
│       │       ├── Gemfile
│       │       ├── .gitignore
│       │       └── jekyll.yml
│       ├── jekyll-deploy/        # Déploiement GitHub Pages
│       │   └── SKILL.md
│       └── quest-files-archive/  # Validation et archivage
│           └── SKILL.md
├── .opencode/
│   └── opencode.json             # Config opencode (agent build + temperature: 0)
├── quests/
│   ├── todo/                     # JSON en attente de conversion
│   └── archives/                 # JSON déjà convertis
├── repos/                        # Dépôts générés (gitignored)
│   └── archives/                 # Dépôts archivés après push
├── REGISTRY.md                   # Index du registre (liens vers domaines)
├── registry.jsonl                # Registre source de vérité (JSONL)
├── registry/                     # Registres par domaine (tableaux générés)
├── scripts/                      # Scripts de migration/génération
├── AGENTS.md                     # Instructions Codex / universel
└── CLAUDE.md                     # Ce fichier (instructions Claude Code)
```

## Conventions

### Slug des dépôts

- Minuscules, tirets, sans emojis ni caractères spéciaux
- Ex: `installer-et-utiliser-visual-studio-code`
- Si collision : ajouter le `quest_id` (`{slug}-{id}`)

### Organisation GitHub

- Dépôt principal : `simplonco/ressources-builder`
- Repos générés : `simplonco/{slug}`

### Thème Jekyll

- Thème : `simplonco/simplonline-ressources-jekyll-theme`
- Docs : https://simplonco.github.io/simplonline-ressources-jekyll-theme/

### Conversions markdown

| Source | Jekyll |
|--------|--------|
| ` ```alert-info ` | `{:.alert-info}` |
| ` ```alert-warning ` | `{:.alert-warning}` |
| ` ```xtext story ` | Blockquote `> ` |
| ` ```js live ` | Playground interactif |
| ` ```quests ` | Lien vers autre quest |
| ` ```ressource ` | Bloc stylisé avec lien |
