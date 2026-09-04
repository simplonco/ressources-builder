# Ressources Builder

Outil de création de ressources pédagogiques Jekyll déployées sur GitHub Pages. Il embarque également un convertisseur pour migrer d'anciennes ressources (appelées « quêtes » / « quests ») vers le nouveau format.

80 ressources déjà en ligne — [Voir le registre](REGISTRY.md).

## Sommaire

- [Ressources Builder](#ressources-builder)
  - [Sommaire](#sommaire)
  - [Prérequis](#prérequis)
  - [Démarrage rapide](#démarrage-rapide)
  - [Commandes principales](#commandes-principales)
    - [Création de ressources](#création-de-ressources)
    - [Conversion de quêtes (legacy)](#conversion-de-quêtes-legacy)
  - [Fonctionnement](#fonctionnement)
    - [Création d'une ressource](#création-dune-ressource)
    - [Conversion d'une quest](#conversion-dune-quest)
    - [Test local](#test-local)
    - [Régénérer le registre](#régénérer-le-registre)
  - [Architecture](#architecture)
  - [Agents IA](#agents-ia)
  - [Thème](#thème)



## Prérequis

| Outil | Utilité | Installation |
|-------|---------|--------------|
| [Python 3](https://www.python.org/) | Scripts de génération du registre | [python.org/downloads](https://www.python.org/downloads/) |
| [Ruby](https://www.ruby-lang.org/) + [Bundler](https://bundler.io/) | Build Jekyll en local | [ruby-lang.org/downloads](https://www.ruby-lang.org/en/downloads/) puis `gem install bundler` |
| [GitHub CLI (`gh`)](https://cli.github.com/) | Déploiement sur GitHub Pages | [cli.github.com](https://cli.github.com/) puis `gh auth login` |
| [Git](https://git-scm.com/) | Versionnement | [git-scm.com/downloads](https://git-scm.com/downloads) |

> **`gh` doit être authentifié** : exécutez `gh auth status` pour vérifier. Sans cette authentification, le déploiement sur GitHub Pages ne fonctionnera pas.

> Le projet utilise [opencode](https://opencode.ai) comme agent IA, mais fonctionne aussi avec [Claude Code](https://claude.ai/code), [Codex](https://openai.com/index/codex/) ou autre. Voir la section [Agents IA](#agents-ia-supportés).

## Démarrage rapide

```bash
# 1. Cloner le dépôt
git clone git@github.com:simplonco/ressources-builder.git
cd ressources-builder

# 2. Lancer opencode (ou l'agent de votre choix)
opencode

# 3. Créer une ressource Jekyll
Créer une ressource 
```

## Commandes principales

### Création de ressources

| Commande | Description |
|----------|-------------|
| `Créer une ressource` | Créer une ressource markdown depuis zéro via un questionnaire interactif |
| `Créer une variante de {titre} ou {slug}` | Cloner une ressource existante pour en faire une variante |
| `Déploie {slug}` | Pousser un dépôt local sur GitHub Pages |
| `Archive {slug}` | Archiver une ressource après relecture |

### Conversion de quêtes (legacy)

| Commande | Description |
|----------|-------------|
| `Convertis quest {id}` | Convertir une ancienne quest Odyssey JSON en ressource Jekyll |
| `Liste les quests en attente` | Voir les fichiers JSON en attente de conversion (dossier `quests/todo/`) |

## Fonctionnement

### Création d'une ressource

1. `Créer une ressource` lance un questionnaire interactif (domaine, titre, contenus interactifs…)
2. Le squelette est généré en local dans `repos/{slug}/`
3. `Déploie {slug}` crée le dépôt GitHub et active GitHub Pages
4. `Archive {slug}` archive la fiche dans le registre

### Conversion d'une quest

| Étape | Commande | Description |
|-------|----------|-------------|
| 1. Création | `Convertis quest {id}` | Parse le JSON, applique les mappings markdown, génère les fichiers Jekyll |
| 2. Déploiement | `Déploie {slug}` | Crée le dépôt GitHub, active GitHub Pages, pousse le premier commit |
| 3. Archivage | `Archive {slug}` | Passe la fiche à `Terminé` dans le registre, archive les fichiers |

> Les étapes 2 et 3 ne sont déclenchées que **sur demande explicite** — la création locale s'arrête après l'étape 1.

### Test local

```bash
cd repos/{slug}
bundle install
bundle exec jekyll serve --livereload
# → http://localhost:4000
```

### Régénérer le registre

```bash
python3 scripts/generate-registry.py
```

## Architecture

```
ressources-builder/
├── .agents/skills/            # Skills IA (workflow de création)
│   ├── jekyll-create/         # Création de ressources Jekyll
│   │   └── templates/         # Templates Jekyll (Gemfile, _config.yml…)
│   ├── jekyll-deploy/         # Déploiement GitHub Pages
│   ├── quest-files-archive/   # Validation et archivage
│   ├── quest-to-github/       # Orchestrateur de conversion (legacy)
│   └── create-variant/        # Création de variante
├── quests/
│   ├── todo/                  # JSON en attente de conversion
│   └── archives/              # JSON déjà convertis
├── repos/                     # Dépôts générés (gitignored)
│   └── archives/              # Dépôts archivés après push
├── scripts/
│   └── generate-registry.py   # Régénère REGISTRY.md et registry/*.md
├── registry.jsonl             # Registre source de vérité (JSONL)
├── registry/                  # Registres par domaine (tableaux générés)
└── REGISTRY.md                # Index du registre
```

## Agents IA

Le projet est conçu pour fonctionner avec **opencode** (agent recommandé), mais les skills dans `.agents/skills/` sont compatibles avec tout assistant respectant le format `SKILL.md` :

| Agent | Fichier de config |
|-------|-------------------|
| opencode | `.opencode/opencode.json` |
| Claude Code | `CLAUDE.md` |
| Codex | `AGENTS.md` |

## Thème

Les ressources générées utilisent le thème [simplonline-ressources-jekyll-theme](https://simplonco.github.io/simplonline-ressources-jekyll-theme/).
