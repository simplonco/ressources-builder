---
name: quest-to-github
description: Orchestrateur de création de ressources Jekyll depuis des fichiers JSON de quêtes. Gère la création locale uniquement — le déploiement et l'archivage sont des commandes séparées.
---

# Skill: Quest to GitHub (Création)

Crée des ressources Jekyll locales à partir de fichiers JSON de quêtes. Ce skill coordonne uniquement la phase de création — il ne déploie ni n'archive automatiquement.

## Quand utiliser ce skill

- L'utilisateur demande de convertir une quest JSON en ressource Jekyll
- L'utilisateur veut lister les quests en attente
- Création de ressources Jekyll (pas de déploiement)

## Workflow en 3 commandes

La conversion d'une quest se déroule en **3 étapes indépendantes**, chacune déclenchée par une commande explicite :

| Étape | Commande | Skill utilisé | Sortie |
|-------|----------|---------------|--------|
| 1. Création | `Convertis quest-{id}.json` | `jekyll-create` | Dossier local + fiche `En cours` |
| 2. Déploiement | `Déploie {slug}` | `jekyll-deploy` | Dépôt GitHub + GitHub Pages |
| 3. Validation | `Archive quest-{id}` / `Valide quest-{id}` | `quest-files-archive` | Fiche `Terminé` + fichiers archivés |

**Important** : l'étape 1 s'arrête après la création locale. Les étapes 2 et 3 ne sont déclenchées que sur demande explicite de l'utilisateur.

## Skills associés

| Skill | Rôle | Quand l'utiliser |
|-------|------|------------------|
| `jekyll-create` | Conversion JSON → markdown Jekyll + templates | Étape 1 : création locale |
| `jekyll-deploy` | Déploiement sur GitHub Pages | Étape 2 : déploiement (commande séparée) |
| `quest-files-archive` | Archivage fichiers + passage `Terminé` | Étape 3 : validation (commande séparée) |

## Structure du projet

```
ressources-builder/
├── .agents/                      # Prompts agents + skills partagés
│   ├── quest-to-github.md        # Prompt agent opencode (création)
│   ├── jekyll-deploy.md          # Prompt agent opencode (déploiement)
│   ├── quest-files-archive.md    # Prompt agent opencode (validation/archivage)
│   └── skills/                   # Skills partagés (tous assistants)
│       ├── quest-to-github/
│       │   └── SKILL.md
│       ├── jekyll-create/
│       │   ├── SKILL.md
│       │   └── templates/
│       │       ├── _config.yml
│       │       ├── Gemfile
│       │       ├── .gitignore
│       │       └── jekyll.yml
│       ├── jekyll-deploy/
│       │   └── SKILL.md
│       └── quest-files-archive/
│           └── SKILL.md
├── .opencode/
│   └── opencode.json             # Définition des agents opencode
├── quests/
│   ├── todo/                          # JSON en attente
│   └── archives/                      # JSON traités
├── repos/                             # Dépôts générés (sortie)
│   └── archives/                      # Dépôts archivés
├── REGISTRY.md                        # Registre des contenus
└── AGENTS.md
```

## Flux de travail

### Étape 1 : Conversion d'une quest (création locale)

Quand l'utilisateur demande de convertir une quest (ex: "Convertis quest-2114.json") :

#### 1.1 Vérification des doublons

1. Lire `REGISTRY.md`
2. Chercher le `quest_id` dans toutes les fiches
3. Si trouvé :
   - Informer l'utilisateur : "Cette quest a déjà été convertie : {URL_DU_DEPOT}"
   - Demander confirmation pour continuer (écraser) ou annuler
4. Si non trouvé : continuer

#### 1.2 Demander le domaine

Demander à l'utilisateur la valeur de {domain} via liste de choix cliquable dans le terminal :
- dev-web
- data
- infra
- design
- autre (préciser)

#### 1.3 Appeler jekyll-create (mode conversion)

Déléguer au skill `jekyll-create` avec les paramètres :
- `mode`: "conversion"
- `quest_id`: l'identifiant de la quest
- `source`: `quests/todo/quest-{id}.json`
- `domain`: la valeur choisie

Le skill `jekyll-create` s'occupe de :
- Parser le JSON
- Appliquer les mappings de syntaxe markdown
- Télécharger les images
- Générer les fichiers Jekyll (README.md, solution.md, templates)
- Ajouter la fiche dans `REGISTRY.md` section `🔄 En cours`

#### 1.4 Fin de la création — STOP

**Ne pas continuer vers le déploiement.** Après la création :

1. Informer l'utilisateur que la création est terminée
2. Proposer un test local :
   ```
   cd repos/{domain}-{slug}
   bundle install
   bundle exec jekyll serve --livereload
   → http://localhost:4000
   ```
3. Rappeler que le déploiement et l'archivage sont des commandes séparées :
   - `Déploie {slug}` pour pousser sur GitHub
   - `Archive quest-{id}` ou `Valide quest-{id}` une fois la relecture terminée

---

### Conversion de plusieurs quests

Quand l'utilisateur demande de convertir plusieurs quests d'un coup (ex: "Convertis toutes les quests en attente" ou "Convertis les quests 1334, 1024 et 1376") :

#### Vérification des liens entre quests

1. Lire chaque fichier JSON dans `quests/todo/`
2. Analyser le contenu markdown de chaque quest à la recherche de blocs `` ```quests ``
3. Construire un graphe de dépendances :
   - Si quest A référence quest B dans un bloc `` ```quests ``, alors A dépend de B
   - Une quest sans référence n'a pas de dépendances
4. Vérifier que toutes les quests référencées existent dans `quests/todo/` (sinon avertir l'utilisateur)

#### Détermination de l'ordre de conversion

1. Appliquer un tri topologique sur le graphe de dépendances
2. Si le graphe contient un cycle → avertir l'utilisateur et annuler
3. Présenter l'ordre de conversion à l'utilisateur :
   ```
   Ordre de conversion détecté :
   1. quest-1334 (pas de dépendances)
   2. quest-1024 (dépend de 1334)
   3. quest-1376 (dépend de 1334 et 1024)
   ```
4. Demander confirmation avant de continuer

#### Conversion séquentielle

Convertir les quests dans l'ordre déterminé en suivant le flux de travail standard (étapes 1.1 à 1.4) pour chaque quest.

**IMPORTANT** : après chaque conversion, s'arrêter et proposer le test local. Ne pas enchaîner automatiquement vers le déploiement.

#### Vérification des liens après conversion

Après chaque conversion, vérifier que les liens `` ```quests `` ont été correctement remplacés par les URLs des dépôts GitHub Pages (via `REGISTRY.md`). Si une quest cible n'est pas encore convertie, utiliser le format `quest-{id}` et avertir l'utilisateur.

---

### Listing des quests en attente

Quand l'utilisateur veut voir les quests en attente :

1. Lire les fichiers dans `quests/todo/`
2. Lister chaque quest avec :
   - Nom du fichier
   - `quest_id` (extrait du nom)
   - Statut dans le registre (en cours / non convertie)
3. Afficher le résultat

---

## Commandes utiles

### Lister les quests en attente
```bash
ls quests/todo/
```

### Vérifier le registre
```bash
cat REGISTRY.md
```

### Voir les dépôts générés
```bash
ls repos/
```

### Voir les archives
```bash
ls repos/archives/
ls quests/archives/
```

---

## Limitations de l'orchestrateur

Ce skill ne contient aucune logique de :
- Conversion markdown (délégué à `jekyll-create`)
- Déploiement GitHub (délégué à `jekyll-deploy`)
- Archivage fichiers (délégué à `quest-files-archive`)

Il est uniquement responsable de :
- La vérification des doublons
- Le choix du domaine
- La coordination de `jekyll-create`
- Le workflow utilisateur (questions, confirmations, proposition de test local)
