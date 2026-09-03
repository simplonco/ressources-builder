# AGENTS.md

## Setup

```bash
# Initialiser le dépôt principal (si pas encore fait)
git init
git remote add origin git@github.com:simplonco/ressources-builder.git

# Installer les dépendances Ruby pour les tests Jekyll locaux
cd repos/{slug}
bundle install
```

## Politiques de commit
- Ne jamais commit sans l'autorisation de l'utilisateur

## Dev commands

### Conversion d'une quest

```
Convertis quest-{id}.json
```

### Créer une ressource Jekyll

```
Créer une ressource Jekyll
```

### Déployer sur GitHub Pages

```
Déploie le dépôt {slug} sur GitHub Pages
```

### Valider et archiver une quest

```
Valider et archiver quest-{id}
```

### Test local

```bash
cd repos/{slug}
bundle exec jekyll serve --livereload
# → http://localhost:4000
```

### Liste des quests en attente

```
Liste les quests en attente de conversion
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
│       ├── quest-files-archive/  # Validation et archivage
│       │   └── SKILL.md
│       └── create-variant/       # Création de variante
│           └── SKILL.md
├── .opencode/
│   └── opencode.json             # Config opencode (agent build + temperature: 0)
├── quests/
│   ├── todo/                     # JSON en attente de conversion
│   └── archives/                 # JSON déjà convertis
├── repos/                        # [IGNORÉ] Dépôts générés localement
│   └── archives/                 # Dépôts archivés après push
├── REGISTRY.md                   # Index du registre (liens vers domaines)
├── registry.jsonl                # Registre source de vérité (JSONL)
├── registry/                     # Registres par domaine (tableaux générés)
├── scripts/                      # Scripts de migration/génération
├── AGENTS.md                     # Instructions Codex / universel
└── CLAUDE.md                     # Instructions Claude Code
```

### Skills

| Skill | Rôle | Quand l'utiliser |
|-------|------|------------------|
| `quest-to-github` | Orchestrateur de création | Conversion d'une quest JSON en ressource Jekyll (création locale uniquement) |
| `jekyll-create` | Création de ressources Jekyll | Créer/modifier une ressource Jekyll (depuis JSON ou from scratch) |
| `jekyll-deploy` | Déploiement GitHub Pages | Pousser un site Jekyll sur GitHub (sans archivage) |
| `quest-files-archive` | Validation et archivage | Mettre la fiche en Terminé + archiver fichiers après relecture |
| `create-variant` | Création de variante | Créer une variante d'une ressource existante (clone + fiche JSONL) |

### Entrées

- `quests/todo/quest-{id}.json` : fichiers source au format JSON

### Sorties

- `repos/{slug}/` : dépôt Jekyll généré (gitignored)
- `https://github.com/simplonco/{slug}` : dépôt GitHub après push
- `https://simplonco.github.io/{slug}` : site Jekyll après push

### Conversions markdown

| Source | Jekyll |
|--------|--------|
| ` ```alert-info ` | `{:.alert-info}` |
| ` ```alert-warning ` | `{:.alert-warning}` |
| ` ```xtext story ` | Blockquote `> ` |
| ` ```js live ` | Playground interactif |
| ` ```quests ` | Lien vers autre quest |
| ` ```ressource ` | Bloc stylisé avec lien |

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

### Workflow

1. Lire JSON depuis `quests/todo/`
2. Créer `repos/{slug}/` avec fichiers Jekyll (via `jekyll-create`)
3. Tester localement avec `bundle exec jekyll serve`
4. Déploiement sur demande explicite (via `jekyll-deploy`)
5. Validation + archivage sur demande explicite (via `quest-files-archive`)

### Support multi-assistants

| Assistant | Fichier de config | Skills |
|-----------|-------------------|--------|
| opencode | `.opencode/opencode.json` (agent build) | `.agents/skills/` |
| Claude Code | `CLAUDE.md` (racine) | `.agents/skills/` |
| Codex | `AGENTS.md` (ce fichier) | `.agents/skills/` |

Les skills sont centralisés dans `.agents/skills/` et discoverés automatiquement par chaque assistant. Dans opencode, l'agent `build` (natif) charge les skills via l'outil `skill`.
