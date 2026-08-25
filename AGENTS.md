# AGENTS.md

## Setup

```bash
# Initialiser le dépôt principal (si pas encore fait)
git init
git remote add origin git@github.com:simplonco/odyssey-quests-to-github.git

# Installer les dépendances Ruby pour les tests Jekyll locaux
cd repos/{slug}
bundle install
```

## Politiques de commit
- Ne jamais commit sans l'autorisation de l'utilisateur

## Dev commands

### Conversion d'une quest

```
Convertis quest-{id}.json en dépôt GitHub
```

### Créer une ressource Jekyll

```
Créer une ressource Jekyll
```

### Déployer sur GitHub Pages

```
Déploie le dépôt {slug} sur GitHub Pages
```

### Archiver une quest

```
Archiver quest-{id}
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
odyssey-quests-to-github/
├── .git/                          # Versionnement du projet principal
├── .gitignore                     # Ignorer repos/, .DS_Store
├── .opencode/skills/              # Skills opencode
│   ├── json-to-github/            # Orchestrateur (workflow complet)
│   │   └── SKILL.md
│   ├── jekyll-create/             # Création de ressources Jekyll
│   │   ├── SKILL.md
│   │   └── templates/             # Templates Jekyll
│   │       ├── _config.yml
│   │       ├── Gemfile
│   │       ├── .gitignore
│   │       └── jekyll.yml
│   ├── jekyll-deploy/             # Déploiement GitHub Pages
│   │   └── SKILL.md
│   └── quest-archive/             # Archivage + maintenance registre
│       └── SKILL.md
├── quests/
│   ├── todo/                      # JSON en attente de conversion
│   ├── archives/                  # JSON déjà convertis
│   └── REGISTRY.md                # Registre des contenus
├── repos/                         # [IGNORÉ] Dépôts générés localement
│   └── archives/                  # Dépôts archivés après push
└── AGENTS.md                      # Ce fichier
```

### Skills

| Skill | Rôle | Quand l'utiliser |
|-------|------|------------------|
| `json-to-github` | Orchestrateur du workflow complet | Conversion d'une quest JSON en dépôt GitHub |
| `jekyll-create` | Création de ressources Jekyll | Créer/modifier une ressource Jekyll (depuis JSON ou from scratch) |
| `jekyll-deploy` | Déploiement GitHub Pages | Pousser un site Jekyll sur GitHub |
| `quest-archive` | Archivage + registre | Finaliser et archiver une conversion |

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

- Dépôt principal : `simplonco/odyssey-quests-to-github`
- Repos générés : `simplonco/{slug}`

### Thème Jekyll

- Thème : `simplonco/simplonline-ressources-jekyll-theme`
- Docs : https://simplonco.github.io/simplonline-ressources-jekyll-theme/

### Workflow

1. Lire JSON depuis `quests/todo/`
2. Créer `repos/{slug}/` avec fichiers Jekyll (via `jekyll-create`)
3. Tester localement avec `bundle exec jekyll serve`
4. Push vers GitHub (via `jekyll-deploy`)
5. Archiver (via `quest-archive`)
