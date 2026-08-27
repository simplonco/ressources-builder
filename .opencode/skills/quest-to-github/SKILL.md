---
name: quest-to-github
description: Orchestrateur de conversion de fichiers JSON de quêtes en dépôts GitHub utilisant le thème Jekyll Simplonline. Coordonne les skills jekyll-create, jekyll-deploy et quest-files-archive.
---

# Skill: Quest to GitHub (Orchestrateur)

Convertit les fichiers JSON de quêtes en dépôts GitHub. Ce skill coordonne les skills spécialisés pour réaliser le workflow complet.

## Quand utiliser ce skill

- L'utilisateur demande de convertir une quest JSON en dépôt GitHub
- L'utilisateur veut lister les quests en attente
- Workflow complet de conversion : création → déploiement → archivage

## Skills coordonnés

| Skill | Rôle |
|-------|------|
| `jekyll-create` | Conversion du JSON en markdown Jekyll + templates |
| `jekyll-deploy` | Déploiement sur GitHub Pages + archivage registre |
| `quest-files-archive` | Archivage fichiers (JSON + repo local) |

## Structure du projet

```
ressources-builder/
├── quests/
│   ├── todo/                          # JSON en attente
│   └── archives/                      # JSON traités
├── repos/                             # Dépôts générés (sortie)
│   └── archives/                      # Dépôts archivés
├── REGISTRY.md                        # Registre des contenus
└── AGENTS.md
```

## Flux de travail

### Conversion complète d'une quest

Quand l'utilisateur demande de convertir une quest (ex: "Convertis quest-2114.json") :

#### Étape 1 : Vérification des doublons

1. Lire `REGISTRY.md`
2. Chercher le `quest_id` dans toutes les fiches
3. Si trouvé :
   - Informer l'utilisateur : "Cette quest a déjà été convertie : {URL_DU_DEPOT}"
   - Demander confirmation pour continuer (écraser) ou annuler
4. Si non trouvé : continuer

#### Étape 2 : Demander le domaine

Demander à l'utilisateur la valeur de {domain} :
- dev-web
- data
- infra
- design
- autre (préciser)

#### Étape 3 : Appeler jekyll-create (mode conversion)

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

#### Étape 4 : Déploiement et archivage

Appeler `jekyll-deploy` avec :
- `repo-name`: `{domain}-{slug}`
- `description`: la description de la quest

Le skill `jekyll-deploy` s'occupe de :
- Créer le dépôt distant sur GitHub
- Activer GitHub Pages
- Initialiser Git + commit + push
- Archiver la fiche dans le registre (`🔄 En cours` → `✅ Terminé`)

#### Étape 5 : Archivage fichiers

Pour les quests converties, l'archivage est **automatique** après le déploiement :
- Appeler `quest-files-archive` pour déplacer le JSON vers `quests/archives/` et le dépôt local vers `repos/archives/`
- Ne pas demander confirmation, c'est une étape systématique du workflow

---

### Conversion de plusieurs quests

Quand l'utilisateur demande de convertir plusieurs quests d'un coup (ex: "Convertis toutes les quests en attente" ou "Convertis les quests 1334, 1024 et 1376") :

#### Étape 1 : Vérification des liens entre quests

1. Lire chaque fichier JSON dans `quests/todo/`
2. Analyser le contenu markdown de chaque quest à la recherche de blocs `` ```quests ``
3. Construire un graphe de dépendances :
   - Si quest A référence quest B dans un bloc `` ```quests ``, alors A dépend de B
   - Une quest sans référence n'a pas de dépendances
4. Vérifier que toutes les quests référencées existent dans `quests/todo/` (sinon avertir l'utilisateur)

#### Étape 2 : Détermination de l'ordre de conversion

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

#### Étape 3 : Conversion séquentielle

Convertir les quests dans l'ordre déterminé en suivant le flux de travail standard (étapes 1 à 5) pour chaque quest.

#### Étape 4 : Vérification des liens après conversion

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
- La coordination des skills
- La vérification des doublons
- Le choix du domaine
- Le workflow utilisateur (questions, confirmations)
