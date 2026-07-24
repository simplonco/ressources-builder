# AGENTS.md

## Setup

```bash
# Initialiser le dépôt principal (si pas encore fait)
git init
git remote add origin https://github.com/simplonco/odyssey-quests-to-github.git

# Installer les dépendances Ruby pour les tests Jekyll locaux
cd repos/{slug}
bundle install
```

## Dev commands

### Conversion d'une quest

```
Convertis quest-{id}.json en dépôt GitHub
```

### Test local

```bash
cd repos/{slug}
bundle exec jekyll serve --livereload
# → http://localhost:4000
```

### Push vers GitHub

```
Push le dépôt {slug} vers GitHub
```

### Liste des quests en attente

```
Liste les quests en attente de conversion
```

## Architecture

```
odyssey-quests-to-github/
├── .git/                          # Versionnement du projet principal
├── .gitignore                     # Ignorer repos/, .DS_Store
├── .opencode/skills/              # Skills opencode
│   └── json-to-github/            # Skill de conversion
│       ├── SKILL.md               # Instructions du skill
│       └── templates/             # Templates Jekyll
│           ├── _config.yml        # Configuration Jekyll
│           ├── Gemfile            # Dépendances Ruby
│           └── .gitignore         # Fichiers à ignorer dans les repos
├── quests/
│   ├── todo/                      # JSON en attente de conversion
│   ├── archives/                  # JSON déjà convertis
│   └── REGISTRY.md                # Registre quest → repo
├── repos/                         # [IGNORÉ] Dépôts générés localement
│   └── archives/                  # Dépôts archivés après push
└── AGENTS.md                      # Ce fichier
```

### Entrées

- `quests/todo/quest-{id}.json` : fichiers source au format JSON

### Sorties

- `repos/{slug}/` : dépôt Jekyll généré (gitignored)
- `https://github.com/simplonco/{slug}` : dépôt GitHub après push

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

- Dépôt principal : `simplonco/odyssey-quests-to-github`
- Repos générés : `simplonco/{slug}`

### Thème Jekyll

- Thème : `simplonco/simplonline-ressources-jekyll-theme`
- Docs : https://simplonco.github.io/simplonline-ressources-jekyll-theme/

### Workflow

1. Lire JSON depuis `quests/todo/`
2. Créer `repos/{slug}/` avec fichiers Jekyll
3. Tester localement avec `bundle exec jekyll serve`
4. Push vers GitHub via outils MCP
5. Archiver le JSON vers `quests/archives/`
