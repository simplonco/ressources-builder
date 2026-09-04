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
| 1. Création | `Convertis quest-{id}.json` | `jekyll-create` | Dossier local + ligne `En cours` dans REGISTRY.md |
| 2. Déploiement | `Déploie {slug}` | `jekyll-deploy` | Dépôt GitHub + GitHub Pages + fiche `Terminé` dans registry.jsonl |
| 3. Archivage | `Archive quest-{id}` | `quest-files-archive` | Fichiers locaux déplacés vers archives/ |

**Important** : l'étape 1 s'arrête après la création locale. Les étapes 2 et 3 ne sont déclenchées que sur demande explicite de l'utilisateur.

## Skills associés

| Skill | Rôle | Quand l'utiliser |
|-------|------|------------------|
| `jekyll-create` | Conversion JSON → markdown Jekyll + templates | Étape 1 : création locale |
| `jekyll-deploy` | Déploiement GitHub Pages + ajout au registre | Étape 2 : déploiement (commande séparée) |
| `quest-files-archive` | Archivage fichiers locaux | Étape 3 : archivage (commande séparée) |

## Structure du projet

```
ressources-builder/
├── .agents/                      # Skills partagés
│   └── skills/                   # Skills (chargés par l'agent build via l'outil `skill`)
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
│   └── opencode.json             # Config opencode (agent build + temperature: 0)
├── quests/
│   ├── todo/                          # JSON en attente
│   └── archives/                      # JSON traités
├── repos/                             # Dépôts générés (sortie)
│   └── archives/                      # Dépôts archivés
├── registry.jsonl                     # Registre source de vérité (JSONL)
├── registry/                          # Registres par domaine (tableaux générés)
│   ├── dev-web.md
│   └── design.md
├── REGISTRY.md                        # Index du registre (liens vers domaines)
└── AGENTS.md
```

## Flux de travail

### Étape 1 : Conversion d'une quest (création locale)

Quand l'utilisateur demande de convertir une quest (ex: "Convertis quest-2114.json") :

#### 1.1 Vérification des doublons

1. Chercher le `quest_id` dans `registry.jsonl` :
   ```
   grep(pattern="\"id\":{{quest_id}}", path=".", include="registry.jsonl")
   ```
2. Si trouvé :
   - Informer l'utilisateur : "Cette quest a déjà été convertie : {URL_DU_DEPOT}"
   - Appeler l'outil `question` avec `{ "questions": [{ "question": "Cette quest est déjà convertie. Écraser ?", "header": "Doublon", "options": [{"label": "Continuer", "description": "Écraser la conversion"}, {"label": "Annuler", "description": "Ne rien faire"}] }] }` pour continuer ou annuler
3. Si non trouvé : continuer

#### 1.2 Demander le domaine

**APPELER l'outil `question`** avec le format suivant (liste cliquable à sélection unique) :

```json
{
  "questions": [{
    "question": "Quel est le domaine de cette ressource ?",
    "header": "Domaine",
    "options": [
      {"label": "dev-web", "description": "Développement web"},
      {"label": "data", "description": "Data / IA"},
      {"label": "infra", "description": "Infrastructure / DevOps"},
      {"label": "design", "description": "Design / UI-UX"}
    ]
  }]
}
```

L'option « saisir sa propre réponse » est ajoutée automatiquement par l'outil : elle couvre le cas « autre » — si choisie, demander le nom du domaine en texte libre.

**NE JAMAIS** demander de taper le domaine au clavier.

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
- Ajouter une ligne dans `REGISTRY.md` sous « En cours »

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
   - `Déploie {slug}` pour pousser sur GitHub et ajouter la fiche au registre
   - `Archive quest-{id}` une fois le déploiement terminé pour nettoyer les fichiers locaux
   - `Annule {slug}` pour annuler le brouillon et retirer la ligne de REGISTRY.md

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
4. Appeler l'outil `question` avec `{ "questions": [{ "question": "Ordre de conversion détecté : {liste}. Convertir dans cet ordre ?", "header": "Ordre", "options": [{"label": "Convertir dans cet ordre", "description": "Lancer la conversion"}, {"label": "Annuler", "description": "Ne rien faire"}] }] }` avant de continuer

#### Conversion séquentielle

Convertir les quests dans l'ordre déterminé en suivant le flux de travail standard (étapes 1.1 à 1.4) pour chaque quest.

**IMPORTANT** : après chaque conversion, s'arrêter et proposer le test local. Ne pas enchaîner automatiquement vers le déploiement.

#### Vérification des liens après conversion

Après chaque conversion, vérifier que les liens `` ```quests `` ont été correctement remplacés par les URLs des dépôts GitHub Pages (via `registry.jsonl`). Si une quest cible n'est pas encore convertie, utiliser le format `quest-{id}` et avertir l'utilisateur.

---

### Listing des quests en attente

Quand l'utilisateur veut voir les quests en attente :

1. Lire les fichiers dans `quests/todo/`
2. Lister chaque quest avec :
   - Nom du fichier
   - `quest_id` (extrait du nom)
   - Statut dans le registre (en cours dans REGISTRY.md / non convertie)
3. Afficher le résultat

---

## Commandes utiles

### Lister les quests en attente
```bash
ls quests/todo/
```

### Vérifier le registre
```bash
cat registry.jsonl
cat registry/{domaine}.md
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
